"""Command-line entry points for the Flashcache wrapper."""

from __future__ import annotations

import argparse
from pathlib import Path

from .server import serve
from .wrapper import FlashcacheConfig


def config_from_args(args: argparse.Namespace) -> FlashcacheConfig:
    return FlashcacheConfig(
        model_path=args.model,
        server_bin=args.server_bin,
        host=args.llama_host,
        port=args.llama_port,
        ctx_size=args.ctx_size,
        timeout=args.timeout,
        slot_id=args.slot_id,
        cache_dir=args.cache_dir,
        max_cache_bytes=args.max_cache_bytes,
        existing_base_url=args.llama_base_url,
        prime_n_predict=args.prime_n_predict,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Flashcache local llama.cpp cache wrapper.")
    parser.add_argument("--model", type=Path, default=FlashcacheConfig.model_path, help="Path to a GGUF model.")
    parser.add_argument("--server-bin", default="llama-server", help="llama.cpp server binary.")
    parser.add_argument("--llama-host", default="127.0.0.1", help="Managed llama.cpp host.")
    parser.add_argument("--llama-port", type=int, default=0, help="Managed llama.cpp port. 0 chooses a free port per request.")
    parser.add_argument("--llama-base-url", help="Use an already-running llama.cpp server instead of managing one.")
    parser.add_argument("--ctx-size", type=int, default=4096, help="llama.cpp context size.")
    parser.add_argument("--timeout", type=float, default=120.0, help="Server/client timeout seconds.")
    parser.add_argument("--slot-id", type=int, default=0, help="llama.cpp slot id.")
    parser.add_argument("--cache-dir", type=Path, default=FlashcacheConfig.cache_dir, help="Local wrapper cache directory.")
    parser.add_argument("--max-cache-bytes", type=int, default=2_000_000_000, help="Cache artifact size cap.")
    parser.add_argument("--prime-n-predict", type=int, default=1, help="Tokens to generate while priming prefix slot.")

    subparsers = parser.add_subparsers(dest="command", required=True)
    serve_parser = subparsers.add_parser("serve", help="Run the wrapper HTTP service.")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Wrapper HTTP host.")
    serve_parser.add_argument("--port", type=int, default=8099, help="Wrapper HTTP port.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "serve":
        serve(config_from_args(args), args.host, args.port)
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
