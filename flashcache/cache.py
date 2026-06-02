"""Cache request parsing, keying, manifests, and artifact cleanup."""

from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import json
import time
from pathlib import Path
from typing import Any


POLICY_VERSION = "flashcache-v1"


class CacheError(Exception):
    """Raised for cache parsing or manifest errors."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(part for part in parts if part)
    return "" if content is None else str(content)


def format_messages(messages: list[dict[str, Any]]) -> str:
    parts = []
    for message in messages:
        role = str(message.get("role", "user"))
        name = message.get("name")
        header = f"{role}:{name}" if name else role
        parts.append(f"<|{header}|>\n{message_text(message.get('content'))}")
    return "\n".join(parts).strip()


def stable_prefix_from_metadata(metadata: dict[str, Any]) -> str:
    if "stable_prefix_text" in metadata:
        return str(metadata.get("stable_prefix_text") or "").strip()
    stable_prefix = metadata.get("stable_prefix")
    if isinstance(stable_prefix, str):
        return stable_prefix.strip()
    if isinstance(stable_prefix, list):
        if all(isinstance(item, dict) for item in stable_prefix):
            return format_messages(stable_prefix)
        return "\n".join(str(item) for item in stable_prefix).strip()
    return ""


def normalize_block_hashes(metadata: dict[str, Any]) -> list[str]:
    block_hashes = metadata.get("block_hashes", [])
    if block_hashes is None:
        return []
    if not isinstance(block_hashes, list):
        raise CacheError("ssd_cache.block_hashes must be a list when provided")
    normalized = []
    for item in block_hashes:
        if isinstance(item, dict):
            value = item.get("sha256") or item.get("hash") or item.get("id")
        else:
            value = item
        if value:
            normalized.append(str(value))
    return normalized


@dataclasses.dataclass(frozen=True)
class ParsedChatRequest:
    model: str
    messages: list[dict[str, Any]]
    full_prompt: str
    tail_prompt: str
    stable_prefix_prompt: str
    namespace: str
    has_cache_metadata: bool
    debug: bool
    persist_volatile_text: bool
    block_hashes: list[str]
    temperature: float
    max_tokens: int
    stream: bool
    raw_cache_metadata: dict[str, Any]


def parse_chat_request(payload: dict[str, Any]) -> ParsedChatRequest:
    if not isinstance(payload, dict):
        raise CacheError("Request body must be a JSON object")
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise CacheError("Request body must include a messages array")
    normalized_messages: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            raise CacheError("Each message must be an object")
        normalized_messages.append(dict(message))

    metadata = payload.get("ssd_cache")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise CacheError("ssd_cache must be an object when provided")

    stable_prefix = stable_prefix_from_metadata(metadata)
    tail_prompt = format_messages(normalized_messages)
    if stable_prefix:
        full_prompt = f"{stable_prefix}\n{tail_prompt}".strip() if tail_prompt else stable_prefix
    else:
        full_prompt = tail_prompt

    return ParsedChatRequest(
        model=str(payload.get("model", "local-model")),
        messages=normalized_messages,
        full_prompt=full_prompt,
        tail_prompt=tail_prompt,
        stable_prefix_prompt=stable_prefix,
        namespace=str(metadata.get("namespace") or payload.get("model") or "default"),
        has_cache_metadata=bool(payload.get("ssd_cache")),
        debug=bool(metadata.get("debug") or payload.get("flashcache_debug")),
        persist_volatile_text=bool(metadata.get("persist_volatile_text")),
        block_hashes=normalize_block_hashes(metadata),
        temperature=float(payload.get("temperature", 0.0)),
        max_tokens=int(payload.get("max_tokens", payload.get("max_completion_tokens", 16))),
        stream=bool(payload.get("stream", False)),
        raw_cache_metadata=dict(metadata),
    )


def build_cache_key(
    *,
    namespace: str,
    model_identity: str,
    server_version: str,
    ctx_size: int,
    llama_settings: dict[str, Any],
    stable_prefix_prompt: str,
    block_hashes: list[str],
    policy_version: str = POLICY_VERSION,
) -> tuple[str, dict[str, Any]]:
    material = {
        "policy_version": policy_version,
        "namespace": namespace,
        "model_identity": model_identity,
        "server_version": server_version,
        "ctx_size": ctx_size,
        "llama_settings": llama_settings,
        "stable_prefix_sha256": sha256_text(stable_prefix_prompt),
        "stable_prefix_bytes": len(stable_prefix_prompt.encode("utf-8")),
        "block_hashes": block_hashes,
    }
    return sha256_json(material), material


@dataclasses.dataclass
class CacheManifest:
    cache_key: str
    cache_key_material: dict[str, Any]
    namespace: str
    created_at: str
    updated_at: str
    slot_filename: str
    slot_file_bytes: int | None
    model_identity: str
    server_version: str
    stable_prefix_sha256: str
    stable_prefix_bytes: int
    block_hashes: list[str]
    volatile_tail_sha256: str | None = None
    volatile_tail_bytes: int | None = None
    volatile_tail_text: str | None = None
    saved_tokens: int | None = None
    restored_tokens: int | None = None
    save_ms: float | None = None
    restore_ms: float | None = None
    prompt_ms: float | None = None
    fallback_reason: str | None = None
    access_count: int = 0
    last_accessed_at: str | None = None

    def to_json(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "CacheManifest":
        return cls(**payload)


class CacheStore:
    def __init__(self, manifest_dir: Path, slot_dir: Path, max_cache_bytes: int = 2_000_000_000) -> None:
        self.manifest_dir = manifest_dir
        self.slot_dir = slot_dir
        self.max_cache_bytes = max_cache_bytes
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        self.slot_dir.mkdir(parents=True, exist_ok=True)

    def manifest_path(self, cache_key: str) -> Path:
        return self.manifest_dir / f"{cache_key}.json"

    def slot_path(self, slot_filename: str) -> Path:
        return self.slot_dir / slot_filename

    def load(self, cache_key: str) -> CacheManifest | None:
        path = self.manifest_path(cache_key)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            manifest = CacheManifest.from_json(json.load(handle))
        manifest.access_count += 1
        manifest.last_accessed_at = dt.datetime.now(dt.timezone.utc).isoformat()
        self.save(manifest)
        return manifest

    def save(self, manifest: CacheManifest) -> Path:
        manifest.updated_at = dt.datetime.now(dt.timezone.utc).isoformat()
        path = self.manifest_path(manifest.cache_key)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(manifest.to_json(), handle, indent=2, sort_keys=True)
            handle.write("\n")
        return path

    def total_bytes(self) -> int:
        total = 0
        for directory in [self.manifest_dir, self.slot_dir]:
            if not directory.exists():
                continue
            for path in directory.rglob("*"):
                if path.is_file():
                    total += path.stat().st_size
        return total

    def cleanup_lru(self) -> list[Path]:
        removed: list[Path] = []
        if self.total_bytes() <= self.max_cache_bytes:
            return removed

        manifests = []
        for path in self.manifest_dir.glob("*.json"):
            try:
                with path.open("r", encoding="utf-8") as handle:
                    manifest = CacheManifest.from_json(json.load(handle))
                access_time = manifest.last_accessed_at or manifest.updated_at or manifest.created_at
            except Exception:
                access_time = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).isoformat()
                manifest = None
            manifests.append((access_time, path, manifest))

        for _, manifest_path, manifest in sorted(manifests, key=lambda item: item[0]):
            if self.total_bytes() <= self.max_cache_bytes:
                break
            if manifest is not None:
                slot_path = self.slot_path(manifest.slot_filename)
                if slot_path.exists():
                    slot_path.unlink()
                    removed.append(slot_path)
            if manifest_path.exists():
                manifest_path.unlink()
                removed.append(manifest_path)
            time.sleep(0)
        return removed


def new_manifest(
    *,
    cache_key: str,
    cache_key_material: dict[str, Any],
    namespace: str,
    slot_filename: str,
    model_identity: str,
    server_version: str,
    stable_prefix_prompt: str,
    block_hashes: list[str],
    tail_prompt: str,
    persist_volatile_text: bool,
) -> CacheManifest:
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    return CacheManifest(
        cache_key=cache_key,
        cache_key_material=cache_key_material,
        namespace=namespace,
        created_at=now,
        updated_at=now,
        slot_filename=slot_filename,
        slot_file_bytes=None,
        model_identity=model_identity,
        server_version=server_version,
        stable_prefix_sha256=sha256_text(stable_prefix_prompt),
        stable_prefix_bytes=len(stable_prefix_prompt.encode("utf-8")),
        block_hashes=block_hashes,
        volatile_tail_sha256=sha256_text(tail_prompt) if tail_prompt else None,
        volatile_tail_bytes=len(tail_prompt.encode("utf-8")) if tail_prompt else 0,
        volatile_tail_text=tail_prompt if persist_volatile_text else None,
    )
