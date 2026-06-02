"""Small llama.cpp HTTP client and managed server process helpers."""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class LlamaCppError(Exception):
    """Raised for llama.cpp client and process failures."""


def free_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 60.0) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = str(exc)
        raise LlamaCppError(f"HTTP {exc.code} from {url}: {body[:500]}") from exc
    except urllib.error.URLError as exc:
        raise LlamaCppError(f"Could not reach {url}: {exc}") from exc
    try:
        return json.loads(body) if body else {}
    except json.JSONDecodeError as exc:
        raise LlamaCppError(f"Non-JSON response from {url}: {body[:500]}") from exc


@dataclasses.dataclass
class LlamaServerConfig:
    server_bin: str
    model_path: Path
    slot_cache_dir: Path
    log_dir: Path
    host: str = "127.0.0.1"
    port: int = 0
    ctx_size: int = 4096
    timeout: float = 120.0
    existing_base_url: str | None = None
    slot_id: int = 0

    @property
    def base_url(self) -> str:
        if self.existing_base_url:
            return self.existing_base_url.rstrip("/")
        return f"http://{self.host}:{self.port}"


class LlamaClient:
    def __init__(self, base_url: str, timeout: float = 120.0, slot_id: int = 0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.slot_id = slot_id

    def health(self) -> dict[str, Any]:
        return http_json("GET", self.base_url + "/health", timeout=min(self.timeout, 5))

    def wait_for_health(self) -> None:
        deadline = time.time() + self.timeout
        last_error = ""
        while time.time() < deadline:
            try:
                response = self.health()
                if response.get("status") == "ok":
                    return
                last_error = json.dumps(response)
            except LlamaCppError as exc:
                last_error = str(exc)
            time.sleep(0.25)
        raise LlamaCppError(f"llama.cpp server did not become healthy: {last_error}")

    def completion(
        self,
        prompt: str,
        *,
        n_predict: int,
        temperature: float,
        cache_prompt: bool = True,
    ) -> dict[str, Any]:
        payload = {
            "prompt": prompt,
            "id_slot": self.slot_id,
            "n_predict": n_predict,
            "temperature": temperature,
            "cache_prompt": cache_prompt,
            "timings_per_token": True,
            "stream": False,
        }
        started = time.perf_counter()
        response = http_json("POST", self.base_url + "/completion", payload, timeout=self.timeout)
        response["_wall_ms"] = (time.perf_counter() - started) * 1000
        return response

    def save_slot(self, filename: str) -> dict[str, Any]:
        started = time.perf_counter()
        response = http_json(
            "POST",
            f"{self.base_url}/slots/{self.slot_id}?action=save",
            {"filename": filename},
            timeout=self.timeout,
        )
        response["_wall_ms"] = (time.perf_counter() - started) * 1000
        return response

    def restore_slot(self, filename: str) -> dict[str, Any]:
        started = time.perf_counter()
        response = http_json(
            "POST",
            f"{self.base_url}/slots/{self.slot_id}?action=restore",
            {"filename": filename},
            timeout=self.timeout,
        )
        response["_wall_ms"] = (time.perf_counter() - started) * 1000
        return response


def llama_server_version(server_bin: str) -> str:
    try:
        version = subprocess.run([server_bin, "--version"], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise LlamaCppError(f"llama.cpp server binary not found: {server_bin}") from exc
    return "\n".join(part for part in [version.stdout.strip(), version.stderr.strip()] if part)


def server_command(config: LlamaServerConfig) -> list[str]:
    return [
        config.server_bin,
        "--model",
        str(config.model_path),
        "--host",
        config.host,
        "--port",
        str(config.port),
        "--ctx-size",
        str(config.ctx_size),
        "--parallel",
        "1",
        "--slot-save-path",
        str(config.slot_cache_dir),
        "--cache-prompt",
        "--slots",
        "--no-ui",
        "--no-warmup",
        "--log-disable",
    ]


class ManagedLlamaServer:
    def __init__(self, config: LlamaServerConfig, label: str = "flashcache") -> None:
        self.config = config
        self.label = label
        self.process: subprocess.Popen[bytes] | None = None
        self.log_path: Path | None = None
        self.client: LlamaClient | None = None

    def __enter__(self) -> LlamaClient:
        self.config.slot_cache_dir.mkdir(parents=True, exist_ok=True)
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        if self.config.existing_base_url:
            self.client = LlamaClient(self.config.existing_base_url, self.config.timeout, self.config.slot_id)
            self.client.wait_for_health()
            return self.client
        if self.config.port == 0:
            self.config.port = free_port(self.config.host)
        if not self.config.model_path.exists():
            raise LlamaCppError(f"Model file not found: {self.config.model_path}")
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.log_path = self.config.log_dir / f"{timestamp}-{self.label}.log"
        log_handle = self.log_path.open("wb")
        self.process = subprocess.Popen(server_command(self.config), stdout=log_handle, stderr=subprocess.STDOUT)
        log_handle.close()
        self.client = LlamaClient(self.config.base_url, self.config.timeout, self.config.slot_id)
        try:
            self.client.wait_for_health()
        except Exception:
            self.stop()
            raise
        return self.client

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.stop()

    def stop(self) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=15)
