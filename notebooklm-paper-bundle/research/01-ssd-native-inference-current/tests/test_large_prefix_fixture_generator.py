from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import generate_large_prefix_fixtures as gen  # noqa: E402
import ollama_workflow_benchmark as owb  # noqa: E402


class LargePrefixFixtureGeneratorTests(unittest.TestCase):
    def test_generates_target_prefix_and_preserves_volatile_turns(self) -> None:
        source = gen.read_fixture(gen.DEFAULT_SOURCE)
        with tempfile.TemporaryDirectory() as tmp:
            target = 12 * 1024
            generated = gen.generate(
                source_path=gen.DEFAULT_SOURCE,
                output_dir=Path(tmp),
                targets=[target],
                max_ctx_size=32768,
                dry_run=False,
            )

            item = generated[0]
            loaded = owb.read_fixture(item.path)
            source_volatile = [block["name"] for block in source["blocks"] if block.get("tier") == "volatile"]
            loaded_volatile = [block["name"] for block in loaded["blocks"] if block.get("tier") == "volatile"]

            self.assertGreaterEqual(item.metrics.prefix_prompt_bytes, target)
            self.assertLess(item.metrics.prefix_prompt_bytes - target, 1024)
            self.assertEqual(source_volatile, loaded_volatile)
            self.assertIn(gen.block_name_for_target(target), loaded["scenarios"][0]["blocks"])
            self.assertEqual(loaded["metadata"]["generated_large_prefix"]["safety_status"], "passed")

    def test_secret_pattern_detection_blocks_non_dry_run(self) -> None:
        fixture = gen.read_fixture(gen.DEFAULT_SOURCE)
        fixture = copy.deepcopy(fixture)
        fixture["blocks"][0]["lines"].append("leaked token gho_abcdefghijklmnopqrstuvwxyz123456")

        matches = gen.scan_for_secrets(fixture)

        self.assertTrue(matches)

    def test_context_sanitizer_removes_private_connection_handoff_lines(self) -> None:
        sanitized = gen.sanitize_context_text(
            "\n".join(
                [
                    "Safe benchmark note",
                    "Continuation handoff: docs/private-benchmark-handoff.md",
                    "ssh user@example",
                    f"ssh-ed25519 {'A' * 80} label",
                    "HostName 100.64.0.1",
                    "IdentityFile REDACTED",
                ]
            )
        )

        self.assertEqual(sanitized, "Safe benchmark note")

    def test_context_budget_failure_is_actionable(self) -> None:
        source = gen.read_fixture(gen.DEFAULT_SOURCE)
        context_entries = gen.collect_context()

        with self.assertRaises(gen.FixtureGenerationError) as caught:
            gen.build_generated_fixture(
                source_fixture=source,
                source_path=gen.DEFAULT_SOURCE,
                target_prefix_bytes=64 * 1024,
                context_entries=context_entries,
                max_ctx_size=4096,
            )

        self.assertIn("recommended ctx", str(caught.exception))

    def test_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            generated = gen.generate(
                source_path=gen.DEFAULT_SOURCE,
                output_dir=output_dir,
                targets=[16 * 1024],
                max_ctx_size=32768,
                dry_run=True,
            )

            self.assertFalse(generated[0].path.exists())


if __name__ == "__main__":
    unittest.main()
