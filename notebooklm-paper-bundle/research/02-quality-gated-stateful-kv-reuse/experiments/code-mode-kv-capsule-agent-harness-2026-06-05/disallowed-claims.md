# Disallowed Claims

- Do not claim KV capsules make Gemma 4 generally smarter.
- Do not claim this proves broad benchmark superiority; this was a controlled 30-case fixture suite.
- Do not claim real OpenClaw integration was tested; the route is an OpenClaw-shaped local Code-mode emulator.
- Do not claim restored capsules are faster end to end yet; prompt eval fell sharply, but total restored wall time still includes save/restore overhead.
- Do not claim compact visible evidence is enough; it passed only 11/30 cases.
- Do not hide direct-tool failures; direct full-visible tools passed 19/30 gates and are an important secondary baseline gap.
- Do not claim paper-ready novelty from this result alone; the next benchmark must use non-handmade datasets with the same control ladder.

Allowed narrow claim:

> In a controlled 30-case local-agent fixture suite, Gemma 4 12B achieved 30/30 Code-mode full-visible, native live-append, and restored KV-capsule gates, with 0/30 fresh-tail and wrong-capsule answer leakage, while using about 43 visible prompt tokens for restored tail-only requests versus about 337 for Code-mode full-visible requests.
