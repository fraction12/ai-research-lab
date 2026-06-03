from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from flashcache.wrapper import FlashcacheConfig, FlashcacheWrapper


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "benchmarks" / "models" / "gemma-3-270m-it-Q8_0.gguf"


@unittest.skipUnless(os.environ.get("FLASHCACHE_RUN_INTEGRATION") == "1", "set FLASHCACHE_RUN_INTEGRATION=1 to run")
class FlashcacheIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(MODEL.exists(), "small GGUF model is not available")
    def test_cache_miss_then_hit_with_local_llama_cpp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wrapper = FlashcacheWrapper(
                FlashcacheConfig(
                    model_path=MODEL,
                    cache_dir=Path(tmp),
                    prime_n_predict=1,
                    timeout=120,
                )
            )
            payload = {
                "model": "local",
                "messages": [{"role": "user", "content": "What changed in this turn?"}],
                "max_tokens": 4,
                "temperature": 0,
                "ssd_cache": {
                    "namespace": "integration",
                    "stable_prefix_text": "You are a local test assistant.",
                    "debug": True,
                },
            }

            first, _ = wrapper.complete(payload)
            second, _ = wrapper.complete(payload)

            self.assertEqual(first["flashcache"]["cache_state"], "miss")
            self.assertEqual(second["flashcache"]["cache_state"], "hit")
            self.assertIsNotNone(second["flashcache"].get("restored_tokens"))


if __name__ == "__main__":
    unittest.main()
