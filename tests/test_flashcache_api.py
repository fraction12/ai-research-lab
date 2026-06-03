from __future__ import annotations

import unittest

from flashcache.cache import CacheError
from flashcache.wrapper import (
    BoundaryTimings,
    FlashcacheConfig,
    FlashcacheWrapper,
    UnsupportedRequestError,
    chat_response,
    telemetry_headers,
)
from flashcache.cache import parse_chat_request


class FlashcacheApiTests(unittest.TestCase):
    def test_streaming_request_is_rejected_before_llama_server_lookup(self) -> None:
        wrapper = FlashcacheWrapper(FlashcacheConfig(server_bin="definitely-missing-llama-server"))

        with self.assertRaises(UnsupportedRequestError):
            wrapper.complete(
                {
                    "model": "local",
                    "stream": True,
                    "messages": [{"role": "user", "content": "hello"}],
                }
            )

    def test_invalid_messages_raise_cache_error(self) -> None:
        with self.assertRaises(CacheError):
            parse_chat_request({"model": "local", "messages": "not-a-list"})

    def test_telemetry_headers_include_cache_state_key_and_prompt_ms(self) -> None:
        headers = telemetry_headers(
            {
                "cache_state": "hit",
                "cache_key": "abc123",
                "prompt_ms": 12.5,
            }
        )

        self.assertEqual(headers["X-Flashcache-Cache"], "hit")
        self.assertEqual(headers["X-Flashcache-Key"], "abc123")
        self.assertEqual(headers["X-Flashcache-Prompt-Ms"], "12.5")

    def test_chat_response_includes_debug_object_only_when_requested(self) -> None:
        parsed = parse_chat_request(
            {
                "model": "local",
                "messages": [{"role": "user", "content": "hello"}],
                "ssd_cache": {"stable_prefix_text": "stable", "debug": True},
            }
        )
        response = chat_response(
            parsed,
            {
                "content": "world",
                "timings": {"prompt_n": 3, "predicted_n": 1},
            },
            {"cache_state": "hit", "boundary_timings": {"cache_lookup_ms": 1.25}},
        )

        self.assertEqual(response["choices"][0]["message"]["content"], "world")
        self.assertEqual(response["usage"]["total_tokens"], 4)
        self.assertEqual(response["flashcache"]["cache_state"], "hit")
        self.assertEqual(response["flashcache"]["boundary_timings"]["cache_lookup_ms"], 1.25)

    def test_boundary_timings_accumulate_phase_durations(self) -> None:
        timings = BoundaryTimings()

        timings.record("cache_lookup_ms", 1.25)
        timings.record("cache_lookup_ms", 0.75)
        result = timings.finish()

        self.assertEqual(result["cache_lookup_ms"], 2.0)
        self.assertGreaterEqual(result["total_wrapper_ms"], 0)


if __name__ == "__main__":
    unittest.main()
