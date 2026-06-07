# Mechanism Decision

Decision: `same_server_restore_reuse_only`

## What Passed

All scored controls returned the exact JSON answer.

`same-server-exact-repeat` showed strong reuse:

```text
cold/full first prompt_n: 7784
exact-repeat second prompt_n: 1
cold/full first prompt_ms: 5971.621
exact-repeat second prompt_ms: 46.572
```

`same-server-restore-full` also showed strong reuse:

```text
cold-full prompt_n: 7784
same-server restore/full prompt_n: 46
cold-full prompt_ms: 5971.621
same-server restore/full prompt_ms: 305.354
```

## What Failed

`fresh-server-restore-full` did not show reuse:

```text
cold-full prompt_n: 7784
fresh-server restore/full prompt_n: 7784
cold-full prompt_ms: 5971.621
fresh-server restore/full prompt_ms: 5943.286
```

This is despite successful slot telemetry:

```text
n_saved: 7743
n_restored: 7743
n_written: 193563740
n_read: 193563740
```

## Interpretation

The backend and `cache_prompt` path can reuse prefix work. The restored-prefix full-resend failure from the prior experiment is therefore not because llama.cpp cannot reuse prompts at all.

The problem is specifically at the persistent/fresh-server boundary. The slot file restores, but the fresh server does not treat the resent full prompt as already backed by reusable prefix state in the same way the live server does.

## Stop Rule

Do not run GraphWalks yet.

The useful mechanism is currently same-server/session-local. Track 02 should either:

- build around persistent server sessions and quality gates, or
- inspect llama.cpp slot restore internals, prompt-cache matching, and token accounting until fresh-server restore/full-resend reduces prompt work.

GraphWalks should wait until the mechanism being tested matches the desired deployment shape.
