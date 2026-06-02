"""HTTP server for the Flashcache local wrapper."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .cache import CacheError
from .wrapper import FlashcacheConfig, FlashcacheWrapper, UnsupportedRequestError


def error_body(message: str, code: str) -> dict[str, Any]:
    return {"error": {"message": message, "type": "invalid_request_error", "code": code}}


class FlashcacheHandler(BaseHTTPRequestHandler):
    wrapper: FlashcacheWrapper

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self._write_json(404, error_body("Unknown endpoint", "not_found"))
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}
            response, headers = self.wrapper.complete(payload)
        except json.JSONDecodeError:
            self._write_json(400, error_body("Request body must be valid JSON", "invalid_json"))
            return
        except UnsupportedRequestError as exc:
            self._write_json(400, error_body(str(exc), "unsupported_request"))
            return
        except CacheError as exc:
            self._write_json(400, error_body(str(exc), "invalid_cache_request"))
            return
        except Exception as exc:
            self._write_json(500, error_body(str(exc), "internal_error"))
            return
        self._write_json(200, response, headers)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _write_json(self, status: int, body: dict[str, Any], headers: dict[str, str] | None = None) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(encoded)


def build_handler(wrapper: FlashcacheWrapper) -> type[FlashcacheHandler]:
    class BoundFlashcacheHandler(FlashcacheHandler):
        pass

    BoundFlashcacheHandler.wrapper = wrapper
    return BoundFlashcacheHandler


def serve(config: FlashcacheConfig, host: str, port: int) -> None:
    wrapper = FlashcacheWrapper(config)
    server = ThreadingHTTPServer((host, port), build_handler(wrapper))
    print(f"flashcache listening on http://{host}:{port}")
    try:
        server.serve_forever()
    finally:
        server.server_close()
