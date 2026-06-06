#!/usr/bin/env python3
"""Model/runtime profiles for tail-only KV capsule harnesses.

This module is deliberately non-inference: it resolves paths, runtime library
names, raw/cache locations, and scoring calibration notes for ignored raw
benchmark runners. It is safe to run locally or remotely before model-bearing
gates.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path, PureWindowsPath
from typing import Any


PROFILE_ENV_PREFIX = "KV_CAPSULE_PROFILE_"


@dataclass(frozen=True)
class CapsuleProfile:
    profile_id: str
    model_family: str
    model_name: str
    model_path: str
    model_size_bytes: int | None
    bundle: str
    backend: str
    llama_dll: str
    ctx_size: int
    predict: int
    n_gpu_layers: int
    state_route: str
    raw_dir: str
    cache_dir: str
    completion_bin: str | None = None
    server_bin: str | None = None
    manifest_path: str | None = None
    completion_smoke_args: list[str] | None = None
    tokenizer_or_template_notes: str | None = None
    output_calibration: str | None = None
    mmproj_layer_note: str | None = None

    @property
    def llama_dll_name(self) -> str:
        return PureWindowsPath(self.llama_dll).name

    def to_jsonable(self) -> dict[str, Any]:
        data = asdict(self)
        data["llama_dll_name"] = self.llama_dll_name
        data["runner_args"] = self.runner_args()
        return data

    def runner_args(self) -> list[str]:
        return [
            "--bundle",
            self.bundle,
            "--backend",
            self.backend,
            "--llama-dll",
            self.llama_dll,
            "--model",
            self.model_path,
            "--out-dir",
            self.raw_dir,
            "--cache-dir",
            self.cache_dir,
            "--state-route",
            self.state_route,
            "--ctx-size",
            str(self.ctx_size),
            "--predict",
            str(self.predict),
            "--n-gpu-layers",
            str(self.n_gpu_layers),
        ]


def windows_join(*parts: str) -> str:
    path = PureWindowsPath(parts[0])
    for part in parts[1:]:
        path /= part
    return str(path)


GPT_OSS_BUNDLE = r"C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss"
GEMMA_BUNDLE = r"C:\Users\Dushyant\Tools\llama-b9512-cuda13"
PROJECT_ROOT_WIN = r"C:\Users\Dushyant\Projects\ai-research-lab"


PROFILES: dict[str, CapsuleProfile] = {
    "gpt-oss-20b": CapsuleProfile(
        profile_id="gpt-oss-20b",
        model_family="gpt-oss",
        model_name="GPT-OSS 20B",
        model_path=r"C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb",
        model_size_bytes=None,
        bundle=GPT_OSS_BUNDLE,
        backend="cuda_v13",
        llama_dll=windows_join(GPT_OSS_BUNDLE, "libllama.dll"),
        completion_bin=None,
        server_bin=windows_join(GPT_OSS_BUNDLE, "llama-server.exe"),
        completion_smoke_args=None,
        ctx_size=32768,
        predict=48,
        n_gpu_layers=-1,
        state_route="auto",
        raw_dir=windows_join(
            PROJECT_ROOT_WIN,
            "research",
            "01-ssd-native-inference-current",
            "benchmarks",
            "tail-only-kv-capsule-continuation-repair-2026-06-04",
            "raw",
        ),
        cache_dir=windows_join(
            PROJECT_ROOT_WIN,
            "research",
            "01-ssd-native-inference-current",
            "benchmarks",
            "tail-only-kv-capsule-continuation-repair-2026-06-04",
            "cache",
        ),
        tokenizer_or_template_notes="Existing GPT-OSS tail-only sequence-state baseline; preserve prior defaults.",
        output_calibration="No known channel-token calibration gate beyond existing Family 1/2 scorer.",
    ),
    "gemma4-12b": CapsuleProfile(
        profile_id="gemma4-12b",
        model_family="gemma",
        model_name="Gemma 4 12B",
        manifest_path=r"C:\Users\Dushyant\.ollama\models\manifests\registry.ollama.ai\library\gemma4\12b",
        model_path=r"C:\Users\Dushyant\.ollama\models\blobs\sha256-5cf8a1f2fc4268b3fd628743675910cf1d8137c4742d0be401c3e885f605023a",
        model_size_bytes=7_381_382_048,
        bundle=GEMMA_BUNDLE,
        backend="cuda_v13",
        llama_dll=windows_join(GEMMA_BUNDLE, "llama.dll"),
        completion_bin=windows_join(GEMMA_BUNDLE, "llama-completion.exe"),
        server_bin=windows_join(GEMMA_BUNDLE, "llama-server.exe"),
        completion_smoke_args=[
            "-p",
            "Return exactly OK.",
            "-n",
            "8",
            "-c",
            "4096",
            "-ngl",
            "99",
            "--temp",
            "0",
            "--reasoning",
            "off",
            "-no-cnv",
            "--no-warmup",
        ],
        ctx_size=32768,
        predict=48,
        n_gpu_layers=99,
        state_route="auto",
        raw_dir=windows_join(
            PROJECT_ROOT_WIN,
            "research",
            "01-ssd-native-inference-current",
            "benchmarks",
            "tail-only-kv-capsule-gemma4-12b-replication-2026-06-04",
            "raw",
        ),
        cache_dir=windows_join(
            PROJECT_ROOT_WIN,
            "research",
            "01-ssd-native-inference-current",
            "benchmarks",
            "tail-only-kv-capsule-gemma4-12b-replication-2026-06-04",
            "cache",
        ),
        tokenizer_or_template_notes=(
            "Gemma smoke emitted thinking/channel markers; calibrate scorer or disable "
            "thinking through a supported route before Family 1/2 evidence."
        ),
        output_calibration="case_insensitive_contains_preserves_exact_fields; channel markers observed in raw C API output",
        mmproj_layer_note="Ollama manifest has an mmproj layer beginning sha256:a18399bf; text-only smoke did not require it.",
    ),
}


def available_profiles() -> list[str]:
    return sorted(PROFILES)


def get_profile(profile_id: str) -> CapsuleProfile:
    try:
        return PROFILES[profile_id]
    except KeyError as exc:
        raise ValueError(f"unknown KV capsule profile: {profile_id}") from exc


def env_value(name: str) -> str | None:
    value = os.environ.get(PROFILE_ENV_PREFIX + name.upper().replace("-", "_"))
    return value if value not in (None, "") else None


def resolve_profile(
    profile_id: str,
    *,
    model: str | None = None,
    bundle: str | None = None,
    backend: str | None = None,
    llama_dll: str | None = None,
    out_dir: str | None = None,
    cache_dir: str | None = None,
    ctx_size: int | None = None,
    predict: int | None = None,
    n_gpu_layers: int | None = None,
    state_route: str | None = None,
) -> CapsuleProfile:
    profile = get_profile(profile_id)
    override_bundle = bundle or env_value("bundle")
    override_llama_dll = llama_dll or env_value("llama_dll")
    if override_bundle and not override_llama_dll:
        override_llama_dll = windows_join(override_bundle, profile.llama_dll_name)
    return replace(
        profile,
        model_path=model or env_value("model") or profile.model_path,
        bundle=override_bundle or profile.bundle,
        backend=backend or env_value("backend") or profile.backend,
        llama_dll=override_llama_dll or profile.llama_dll,
        raw_dir=out_dir or env_value("out_dir") or profile.raw_dir,
        cache_dir=cache_dir or env_value("cache_dir") or profile.cache_dir,
        ctx_size=ctx_size if ctx_size is not None else int(env_value("ctx_size") or profile.ctx_size),
        predict=predict if predict is not None else int(env_value("predict") or profile.predict),
        n_gpu_layers=n_gpu_layers if n_gpu_layers is not None else int(env_value("n_gpu_layers") or profile.n_gpu_layers),
        state_route=state_route or env_value("state_route") or profile.state_route,
    )


def path_status(profile: CapsuleProfile) -> dict[str, dict[str, Any]]:
    paths = {
        "model_path": profile.model_path,
        "bundle": profile.bundle,
        "llama_dll": profile.llama_dll,
        "raw_dir": profile.raw_dir,
        "cache_dir": profile.cache_dir,
    }
    if profile.manifest_path:
        paths["manifest_path"] = profile.manifest_path
    if profile.completion_bin:
        paths["completion_bin"] = profile.completion_bin
    if profile.server_bin:
        paths["server_bin"] = profile.server_bin
    status = {}
    for key, value in paths.items():
        path = Path(value)
        status[key] = {
            "path": value,
            "exists_on_this_host": path.exists(),
            "is_dir_on_this_host": path.is_dir(),
            "is_file_on_this_host": path.is_file(),
        }
    return status


def build_report(profile: CapsuleProfile, *, include_path_status: bool = False) -> dict[str, Any]:
    report = {
        "profile": profile.to_jsonable(),
        "profile_contract": {
            "non_inference": True,
            "whole_context_success_allowed": False,
            "requires_output_calibration_before_evidence": profile.output_calibration is not None
            and profile.output_calibration != "No known channel-token calibration gate beyond existing Family 1/2 scorer.",
            "reasoning_off_cli_smoke_only": profile.profile_id == "gemma4-12b",
        },
    }
    if include_path_status:
        report["path_status"] = path_status(profile)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve tail-only KV capsule model/runtime profiles without inference.")
    parser.add_argument("--profile", choices=available_profiles(), default="gpt-oss-20b")
    parser.add_argument("--model")
    parser.add_argument("--bundle")
    parser.add_argument("--backend")
    parser.add_argument("--llama-dll")
    parser.add_argument("--out-dir")
    parser.add_argument("--cache-dir")
    parser.add_argument("--ctx-size", type=int)
    parser.add_argument("--predict", type=int)
    parser.add_argument("--n-gpu-layers", type=int)
    parser.add_argument("--state-route", choices=["auto", "seq-file", "seq-memory", "whole-context"])
    parser.add_argument("--check-paths", action="store_true", help="Report whether resolved paths exist on this host; does not load a model.")
    parser.add_argument("--runner-args", action="store_true", help="Print a shell-escaped runner argument string instead of JSON.")
    parser.add_argument("--completion-smoke-command", action="store_true", help="Print a one-shot llama-completion load-smoke command when the profile defines one.")
    return parser.parse_args(argv)


def quote_arg(value: str) -> str:
    if not value:
        return '""'
    if any(ch.isspace() for ch in value) or "\\" in value or ":" in value:
        return '"' + value.replace('"', '\\"') + '"'
    return value


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    profile = resolve_profile(
        args.profile,
        model=args.model,
        bundle=args.bundle,
        backend=args.backend,
        llama_dll=args.llama_dll,
        out_dir=args.out_dir,
        cache_dir=args.cache_dir,
        ctx_size=args.ctx_size,
        predict=args.predict,
        n_gpu_layers=args.n_gpu_layers,
        state_route=args.state_route,
    )
    if args.completion_smoke_command:
        if not profile.completion_bin or not profile.completion_smoke_args:
            raise SystemExit(f"profile {profile.profile_id} does not define a completion smoke command")
        command = [profile.completion_bin, "-m", profile.model_path] + profile.completion_smoke_args
        print(" ".join(quote_arg(arg) for arg in command))
    elif args.runner_args:
        print(" ".join(quote_arg(arg) for arg in profile.runner_args()))
    else:
        print(json.dumps(build_report(profile, include_path_status=args.check_paths), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
