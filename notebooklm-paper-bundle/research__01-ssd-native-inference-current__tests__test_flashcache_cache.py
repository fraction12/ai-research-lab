from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from flashcache.cache import (
    CacheStore,
    build_cache_key,
    new_manifest,
    parse_chat_request,
    sha256_text,
)


class FlashcacheCacheTests(unittest.TestCase):
    def test_parse_chat_request_without_cache_metadata_bypasses_cache(self) -> None:
        parsed = parse_chat_request(
            {
                "model": "local-model",
                "messages": [{"role": "user", "content": "hello"}],
                "max_tokens": 4,
            }
        )

        self.assertFalse(parsed.has_cache_metadata)
        self.assertEqual(parsed.stable_prefix_prompt, "")
        self.assertIn("<|user|>", parsed.full_prompt)
        self.assertEqual(parsed.max_tokens, 4)

    def test_parse_chat_request_with_stable_prefix_keeps_tail_separate(self) -> None:
        parsed = parse_chat_request(
            {
                "model": "local-model",
                "messages": [{"role": "user", "content": "tail"}],
                "ssd_cache": {
                    "namespace": "workflow",
                    "stable_prefix_text": "stable instructions",
                    "block_hashes": [{"sha256": "abc"}, "def"],
                    "debug": True,
                },
            }
        )

        self.assertTrue(parsed.has_cache_metadata)
        self.assertEqual(parsed.namespace, "workflow")
        self.assertEqual(parsed.stable_prefix_prompt, "stable instructions")
        self.assertTrue(parsed.full_prompt.startswith("stable instructions"))
        self.assertEqual(parsed.block_hashes, ["abc", "def"])
        self.assertTrue(parsed.debug)

    def test_cache_key_is_deterministic_and_changes_on_compatibility_inputs(self) -> None:
        common = {
            "namespace": "workflow",
            "model_identity": "model.gguf",
            "server_version": "llama 1",
            "ctx_size": 4096,
            "llama_settings": {"slot_id": 0},
            "stable_prefix_prompt": "stable",
            "block_hashes": ["a", "b"],
        }
        first, first_material = build_cache_key(**common)
        second, second_material = build_cache_key(**common)
        changed, _ = build_cache_key(**{**common, "ctx_size": 8192})

        self.assertEqual(first, second)
        self.assertEqual(first_material, second_material)
        self.assertNotEqual(first, changed)

    def test_manifest_round_trip_does_not_persist_volatile_text_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = CacheStore(root / "manifests", root / "slots", max_cache_bytes=1_000_000)
            cache_key, material = build_cache_key(
                namespace="workflow",
                model_identity="model.gguf",
                server_version="llama 1",
                ctx_size=4096,
                llama_settings={"slot_id": 0},
                stable_prefix_prompt="stable",
                block_hashes=[],
            )
            manifest = new_manifest(
                cache_key=cache_key,
                cache_key_material=material,
                namespace="workflow",
                slot_filename="slot.bin",
                model_identity="model.gguf",
                server_version="llama 1",
                stable_prefix_prompt="stable",
                block_hashes=[],
                tail_prompt="secret tail",
                persist_volatile_text=False,
            )

            store.save(manifest)
            loaded = store.load(cache_key)

            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.volatile_tail_sha256, sha256_text("secret tail"))
            self.assertIsNone(loaded.volatile_tail_text)

    def test_cleanup_lru_removes_slot_and_manifest_when_over_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = CacheStore(root / "manifests", root / "slots", max_cache_bytes=10)
            cache_key, material = build_cache_key(
                namespace="workflow",
                model_identity="model.gguf",
                server_version="llama 1",
                ctx_size=4096,
                llama_settings={"slot_id": 0},
                stable_prefix_prompt="stable",
                block_hashes=[],
            )
            manifest = new_manifest(
                cache_key=cache_key,
                cache_key_material=material,
                namespace="workflow",
                slot_filename="slot.bin",
                model_identity="model.gguf",
                server_version="llama 1",
                stable_prefix_prompt="stable",
                block_hashes=[],
                tail_prompt="tail",
                persist_volatile_text=False,
            )
            store.save(manifest)
            store.slot_path("slot.bin").write_bytes(b"x" * 100)

            removed = store.cleanup_lru()

            self.assertTrue(removed)
            self.assertFalse(store.manifest_path(cache_key).exists())
            self.assertFalse(store.slot_path("slot.bin").exists())


if __name__ == "__main__":
    unittest.main()
