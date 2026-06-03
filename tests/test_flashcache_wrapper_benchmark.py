from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import flashcache_wrapper_benchmark as benchmark  # noqa: E402


class FlashcacheWrapperBenchmarkTests(unittest.TestCase):
    def test_session_cache_mode_requires_persistent_server_mode(self) -> None:
        args = SimpleNamespace(cache_mode="session", server_mode="per-request")

        with self.assertRaises(SystemExit):
            benchmark.validate_args(args)

    def test_session_hit_counts_as_cache_hit(self) -> None:
        runs = [{"cache_state": "hit"}, {"cache_state": "session-hit"}, {"cache_state": "miss"}]

        self.assertEqual(benchmark.cache_hit_count(runs), 2)


if __name__ == "__main__":
    unittest.main()
