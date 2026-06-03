from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import flashcache_wrapper_benchmark as benchmark  # noqa: E402


class FlashcacheWrapperBenchmarkTests(unittest.TestCase):
    def test_session_cache_modes_require_persistent_server_mode(self) -> None:
        for cache_mode in ["session", "session-tail"]:
            with self.subTest(cache_mode=cache_mode):
                args = SimpleNamespace(cache_mode=cache_mode, server_mode="per-request")

                with self.assertRaises(SystemExit):
                    benchmark.validate_args(args)

    def test_session_hit_counts_as_cache_hit(self) -> None:
        runs = [
            {"cache_state": "hit"},
            {"cache_state": "session-hit"},
            {"cache_state": "session-tail-hit"},
            {"cache_state": "miss"},
        ]

        self.assertEqual(benchmark.cache_hit_count(runs), 3)

    def test_session_tail_uses_tail_only_completion_prompt(self) -> None:
        parsed = SimpleNamespace(full_prompt="stable prefix\n\nchanged tail", tail_prompt="changed tail")

        self.assertEqual(
            benchmark.session_completion_prompt(parsed, "session"),
            ("stable prefix\n\nchanged tail", "full-prompt"),
        )
        self.assertEqual(
            benchmark.session_completion_prompt(parsed, "session-tail"),
            ("changed tail", "tail-only"),
        )


if __name__ == "__main__":
    unittest.main()
