"""High-level cache wrapper around llama.cpp slot persistence."""

from __future__ import annotations

import dataclasses
import datetime as dt
import time
import uuid
from pathlib import Path
from typing import Any

from .cache import (
    CacheError,
    CacheManifest,
    CacheStore,
    ParsedChatRequest,
    build_cache_key,
    new_manifest,
    parse_chat_request,
    sha256_text,
)
from .llama_cpp import LlamaCppError, LlamaServerConfig, ManagedLlamaServer, llama_server_version


ROOT = Path(__file__).resolve().parents[1]


class UnsupportedRequestError(Exception):
    """Raised when the wrapper subset explicitly does not support a request."""


@dataclasses.dataclass
class FlashcacheConfig:
    model_path: Path = ROOT / "benchmarks" / "models" / "gemma-3-270m-it-Q8_0.gguf"
    hf_repo: str | None = None
    server_bin: str = "llama-server"
    host: str = "127.0.0.1"
    port: int = 0
    ctx_size: int = 4096
    timeout: float = 120.0
    slot_id: int = 0
    cache_dir: Path = ROOT / "benchmarks" / "flashcache"
    max_cache_bytes: int = 2_000_000_000
    existing_base_url: str | None = None
    prime_n_predict: int = 1

    @property
    def manifest_dir(self) -> Path:
        return self.cache_dir / "manifests"

    @property
    def slot_cache_dir(self) -> Path:
        return self.cache_dir / "slot-cache"

    @property
    def log_dir(self) -> Path:
        return self.cache_dir / "logs"

    @property
    def prompt_debug_dir(self) -> Path:
        return self.cache_dir / "prompts"

    def llama_settings(self) -> dict[str, Any]:
        return {
            "ctx_size": self.ctx_size,
            "slot_id": self.slot_id,
            "prime_n_predict": self.prime_n_predict,
        }

    def model_identity(self) -> str:
        return self.hf_repo or str(self.model_path)

    def server_config(self) -> LlamaServerConfig:
        return LlamaServerConfig(
            server_bin=self.server_bin,
            model_path=self.model_path,
            slot_cache_dir=self.slot_cache_dir,
            log_dir=self.log_dir,
            hf_repo=self.hf_repo,
            host=self.host,
            port=self.port,
            ctx_size=self.ctx_size,
            timeout=self.timeout,
            existing_base_url=self.existing_base_url,
            slot_id=self.slot_id,
        )


def timing_record(response: dict[str, Any]) -> dict[str, Any]:
    timings = response.get("timings", {})
    return {
        "wall_ms": response.get("_wall_ms"),
        "prompt_ms": timings.get("prompt_ms"),
        "prompt_n": timings.get("prompt_n"),
        "prompt_per_token_ms": timings.get("prompt_per_token_ms"),
        "predicted_ms": timings.get("predicted_ms"),
        "predicted_n": timings.get("predicted_n"),
        "predicted_per_token_ms": timings.get("predicted_per_token_ms"),
    }


def completion_text(response: dict[str, Any]) -> str:
    return str(response.get("content", ""))


def telemetry_headers(telemetry: dict[str, Any]) -> dict[str, str]:
    headers = {
        "X-Flashcache-Cache": str(telemetry.get("cache_state", "unknown")),
    }
    if telemetry.get("cache_key"):
        headers["X-Flashcache-Key"] = str(telemetry["cache_key"])
    if telemetry.get("fallback_reason"):
        headers["X-Flashcache-Fallback"] = str(telemetry["fallback_reason"])
    if telemetry.get("prompt_ms") is not None:
        headers["X-Flashcache-Prompt-Ms"] = str(telemetry["prompt_ms"])
    return headers


def chat_response(parsed: ParsedChatRequest, llama_response: dict[str, Any], telemetry: dict[str, Any]) -> dict[str, Any]:
    timings = timing_record(llama_response)
    usage = {
        "prompt_tokens": timings.get("prompt_n"),
        "completion_tokens": timings.get("predicted_n"),
        "total_tokens": None,
    }
    if usage["prompt_tokens"] is not None and usage["completion_tokens"] is not None:
        usage["total_tokens"] = int(usage["prompt_tokens"]) + int(usage["completion_tokens"])
    response: dict[str, Any] = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": parsed.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": completion_text(llama_response)},
                "finish_reason": "stop",
            }
        ],
        "usage": usage,
    }
    if parsed.debug:
        response["flashcache"] = telemetry
    return response


class FlashcacheWrapper:
    def __init__(self, config: FlashcacheConfig) -> None:
        self.config = config
        self.store = CacheStore(config.manifest_dir, config.slot_cache_dir, config.max_cache_bytes)

    def complete(self, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
        parsed = parse_chat_request(payload)
        if parsed.stream:
            raise UnsupportedRequestError("streaming chat completions are not supported by this wrapper yet")
        server_version = llama_server_version(self.config.server_bin)
        if not parsed.has_cache_metadata or not parsed.stable_prefix_prompt:
            response, telemetry = self._direct_completion(parsed, server_version, "bypass")
            return response, telemetry_headers(telemetry)
        response, telemetry = self._cache_aware_completion(parsed, server_version)
        return response, telemetry_headers(telemetry)

    def _direct_completion(
        self,
        parsed: ParsedChatRequest,
        server_version: str,
        cache_state: str,
        fallback_reason: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        with ManagedLlamaServer(self.config.server_config(), label="direct") as client:
            llama_response = client.completion(
                parsed.full_prompt,
                n_predict=parsed.max_tokens,
                temperature=parsed.temperature,
            )
        timings = timing_record(llama_response)
        telemetry = {
            "cache_state": cache_state,
            "cache_key": None,
            "fallback_reason": fallback_reason,
            "server_version": server_version,
            "prompt_ms": timings.get("prompt_ms"),
            "prompt_n": timings.get("prompt_n"),
            "timings": timings,
        }
        return chat_response(parsed, llama_response, telemetry), telemetry

    def _cache_aware_completion(
        self,
        parsed: ParsedChatRequest,
        server_version: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        cache_key, key_material = build_cache_key(
            namespace=parsed.namespace,
            model_identity=self.config.model_identity(),
            server_version=server_version,
            ctx_size=self.config.ctx_size,
            llama_settings=self.config.llama_settings(),
            stable_prefix_prompt=parsed.stable_prefix_prompt,
            block_hashes=parsed.block_hashes,
        )
        manifest = self.store.load(cache_key)
        slot_filename = f"{cache_key[:16]}-slot.bin"
        if manifest and self.store.slot_path(manifest.slot_filename).exists():
            try:
                response, telemetry = self._cache_hit(parsed, cache_key, manifest, server_version)
                return response, telemetry
            except (LlamaCppError, CacheError) as exc:
                response, telemetry = self._direct_completion(parsed, server_version, "fallback", str(exc))
                return response, telemetry

        manifest = new_manifest(
            cache_key=cache_key,
            cache_key_material=key_material,
            namespace=parsed.namespace,
            slot_filename=slot_filename,
            model_identity=self.config.model_identity(),
            server_version=server_version,
            stable_prefix_prompt=parsed.stable_prefix_prompt,
            block_hashes=parsed.block_hashes,
            tail_prompt=parsed.tail_prompt,
            persist_volatile_text=parsed.persist_volatile_text,
        )
        response, telemetry = self._cache_miss(parsed, cache_key, manifest, server_version)
        return response, telemetry

    def _cache_miss(
        self,
        parsed: ParsedChatRequest,
        cache_key: str,
        manifest: CacheManifest,
        server_version: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        with ManagedLlamaServer(self.config.server_config(), label=f"miss-{cache_key[:8]}") as client:
            prime_response = client.completion(
                parsed.stable_prefix_prompt,
                n_predict=self.config.prime_n_predict,
                temperature=0.0,
            )
            save_response = client.save_slot(manifest.slot_filename)
            slot_path = self.store.slot_path(manifest.slot_filename)
            manifest.saved_tokens = save_response.get("n_saved")
            manifest.slot_file_bytes = slot_path.stat().st_size if slot_path.exists() else save_response.get("n_written")
            manifest.save_ms = save_response.get("timings", {}).get("save_ms")
            self.store.save(manifest)
            llama_response = client.completion(
                parsed.full_prompt,
                n_predict=parsed.max_tokens,
                temperature=parsed.temperature,
            )

        timings = timing_record(llama_response)
        telemetry = {
            "cache_state": "miss",
            "cache_key": cache_key,
            "fallback_reason": None,
            "server_version": server_version,
            "slot_file_bytes": manifest.slot_file_bytes,
            "saved_tokens": manifest.saved_tokens,
            "save_ms": manifest.save_ms,
            "prime": timing_record(prime_response),
            "prompt_ms": timings.get("prompt_ms"),
            "prompt_n": timings.get("prompt_n"),
            "timings": timings,
        }
        manifest.prompt_ms = timings.get("prompt_ms")
        self.store.save(manifest)
        self.store.cleanup_lru()
        return chat_response(parsed, llama_response, telemetry), telemetry

    def _cache_hit(
        self,
        parsed: ParsedChatRequest,
        cache_key: str,
        manifest: CacheManifest,
        server_version: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        with ManagedLlamaServer(self.config.server_config(), label=f"hit-{cache_key[:8]}") as client:
            restore_response = client.restore_slot(manifest.slot_filename)
            llama_response = client.completion(
                parsed.full_prompt,
                n_predict=parsed.max_tokens,
                temperature=parsed.temperature,
            )
        timings = timing_record(llama_response)
        manifest.restored_tokens = restore_response.get("n_restored")
        manifest.restore_ms = restore_response.get("timings", {}).get("restore_ms")
        manifest.prompt_ms = timings.get("prompt_ms")
        self.store.save(manifest)
        telemetry = {
            "cache_state": "hit",
            "cache_key": cache_key,
            "fallback_reason": None,
            "server_version": server_version,
            "slot_file_bytes": manifest.slot_file_bytes,
            "restored_tokens": manifest.restored_tokens,
            "restore_ms": manifest.restore_ms,
            "prompt_ms": timings.get("prompt_ms"),
            "prompt_n": timings.get("prompt_n"),
            "timings": timings,
        }
        return chat_response(parsed, llama_response, telemetry), telemetry
