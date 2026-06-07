from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import kv_capsule_profiles as profiles  # noqa: E402


class KvCapsuleProfilesTests(unittest.TestCase):
    def test_gpt_oss_default_preserves_libllama_runtime(self) -> None:
        profile = profiles.resolve_profile("gpt-oss-20b")

        self.assertEqual(profile.profile_id, "gpt-oss-20b")
        self.assertEqual(profile.backend, "cuda_v13")
        self.assertTrue(profile.model_path.endswith("sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb"))
        self.assertTrue(profile.bundle.endswith(r"llama-ollama-a731805ce-gptoss"))
        self.assertTrue(profile.llama_dll.endswith(r"libllama.dll"))
        self.assertEqual(profile.llama_dll_name, "libllama.dll")
        self.assertIn("tail-only-kv-capsule-continuation-repair", profile.raw_dir)

    def test_gemma_profile_uses_ollama_blob_and_b9512_llama_dll(self) -> None:
        profile = profiles.resolve_profile("gemma4-12b")

        self.assertEqual(profile.profile_id, "gemma4-12b")
        self.assertEqual(profile.model_family, "gemma")
        self.assertTrue(profile.model_path.endswith("sha256-5cf8a1f2fc4268b3fd628743675910cf1d8137c4742d0be401c3e885f605023a"))
        self.assertEqual(profile.model_size_bytes, 7_381_382_048)
        self.assertTrue(profile.bundle.endswith(r"llama-b9512-cuda13"))
        self.assertTrue(profile.llama_dll.endswith(r"llama.dll"))
        self.assertEqual(profile.llama_dll_name, "llama.dll")
        self.assertIn("thinking/channel", profile.tokenizer_or_template_notes or "")
        self.assertIn("tail-only-kv-capsule-gemma4-12b-replication", profile.raw_dir)
        self.assertNotEqual(profiles.resolve_profile("gpt-oss-20b").raw_dir, profile.raw_dir)

    def test_explicit_bundle_override_preserves_profile_dll_name(self) -> None:
        gpt = profiles.resolve_profile("gpt-oss-20b", bundle=r"D:\runtime\gpt")
        gemma = profiles.resolve_profile("gemma4-12b", bundle=r"D:\runtime\gemma")

        self.assertEqual(gpt.llama_dll, r"D:\runtime\gpt\libllama.dll")
        self.assertEqual(gemma.llama_dll, r"D:\runtime\gemma\llama.dll")

    def test_explicit_llama_dll_override_wins(self) -> None:
        profile = profiles.resolve_profile("gemma4-12b", bundle=r"D:\runtime\gemma", llama_dll=r"E:\custom\llama.dll")

        self.assertEqual(profile.bundle, r"D:\runtime\gemma")
        self.assertEqual(profile.llama_dll, r"E:\custom\llama.dll")

    def test_env_overrides_are_profile_scoped_by_prefix(self) -> None:
        env = {
            "KV_CAPSULE_PROFILE_MODEL": r"D:\models\gemma.gguf",
            "KV_CAPSULE_PROFILE_LLAMA_DLL": r"D:\runtime\llama.dll",
            "KV_CAPSULE_PROFILE_CTX_SIZE": "8192",
        }
        with patch.dict(os.environ, env, clear=False):
            profile = profiles.resolve_profile("gemma4-12b")

        self.assertEqual(profile.model_path, r"D:\models\gemma.gguf")
        self.assertEqual(profile.llama_dll, r"D:\runtime\llama.dll")
        self.assertEqual(profile.ctx_size, 8192)

    def test_report_is_non_inference_and_flags_gemma_calibration(self) -> None:
        report = profiles.build_report(profiles.resolve_profile("gemma4-12b"))

        self.assertTrue(report["profile_contract"]["non_inference"])
        self.assertTrue(report["profile_contract"]["requires_output_calibration_before_evidence"])
        self.assertFalse(report["profile_contract"]["whole_context_success_allowed"])

    def test_main_outputs_json_without_model_load(self) -> None:
        with patch("builtins.print") as fake_print:
            exit_code = profiles.main(["--profile", "gemma4-12b"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(fake_print.call_args.args[0])
        self.assertEqual(payload["profile"]["profile_id"], "gemma4-12b")
        self.assertEqual(payload["profile"]["llama_dll_name"], "llama.dll")

    def test_runner_args_include_profile_values(self) -> None:
        profile = profiles.resolve_profile("gemma4-12b")
        args = profile.runner_args()

        self.assertIn("--model", args)
        self.assertIn(profile.model_path, args)
        self.assertIn("--llama-dll", args)
        self.assertIn(profile.llama_dll, args)
        self.assertIn("--bundle", args)
        self.assertIn(profile.bundle, args)
        self.assertIn("--state-route", args)
        self.assertIn("auto", args)

    def test_gemma_completion_smoke_command_uses_reasoning_off(self) -> None:
        with patch("builtins.print") as fake_print:
            exit_code = profiles.main(["--profile", "gemma4-12b", "--completion-smoke-command"])

        self.assertEqual(exit_code, 0)
        command = fake_print.call_args.args[0]
        self.assertIn("llama-completion.exe", command)
        self.assertIn("--reasoning off", command)
        self.assertIn("-no-cnv", command)


if __name__ == "__main__":
    unittest.main()
