#!/usr/bin/env python3
"""Maintain a passive local ledger for the AI research lab Workspace Manager."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

REPO_NAME = "ai-research-lab"
MANAGER_TITLE = "Workspace Manager"
MANAGER_THREAD_IDS = {
    "019e8c24-54ac-7c90-9df6-233396abc5fb",
}
EVENT_LIMIT = 50
MESSAGE_LIMIT = 4000


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    try:
        payload = _read_payload()
        thread_id = _extract_thread_id(payload)
        title = _lookup_thread_title(thread_id)

        if not _is_workspace_manager(thread_id, title):
            return _emit_success()

        now = _utc_now()
        last_message = str(payload.get("last_assistant_message") or "").strip()
        entry = _build_entry(payload, thread_id, title or MANAGER_TITLE, last_message, now)
        _update_ledger(repo_root, entry, payload, now)
        return _emit_success()
    except Exception as exc:  # Hooks must stay passive; log and let Codex continue.
        _write_error(repo_root, exc)
        return _emit_success()


def _read_payload() -> Dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def _extract_thread_id(payload: Mapping[str, Any]) -> str:
    for key in ("session_id", "thread_id", "conversation_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value

    transcript_path = payload.get("transcript_path")
    if isinstance(transcript_path, str):
        match = re.search(
            r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
            transcript_path,
            re.IGNORECASE,
        )
        if match:
            return match.group(1)

    return "unknown"


def _lookup_thread_title(thread_id: str) -> Optional[str]:
    if not thread_id or thread_id == "unknown":
        return None

    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    index_path = codex_home / "session_index.jsonl"
    if not index_path.exists():
        return None

    title: Optional[str] = None
    try:
        with index_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("id") == thread_id and isinstance(row.get("thread_name"), str):
                    title = row["thread_name"]
    except OSError:
        return None
    return title


def _is_workspace_manager(thread_id: str, title: Optional[str]) -> bool:
    if thread_id in MANAGER_THREAD_IDS:
        return True
    return title == MANAGER_TITLE


def _build_entry(
    payload: Mapping[str, Any],
    thread_id: str,
    title: str,
    last_message: str,
    now: str,
) -> Dict[str, Any]:
    summary = _first_nonempty_line(last_message)
    return {
        "thread_id": thread_id,
        "title": title,
        "role": "orchestration",
        "repo": REPO_NAME,
        "status": _infer_status(last_message),
        "current_assignment": _extract_current_assignment(last_message, summary),
        "last_update": summary,
        "next_action": _extract_next_action(last_message),
        "cwd": _optional_str(payload.get("cwd")),
        "turn_id": _optional_str(payload.get("turn_id")),
        "transcript_path": _optional_str(payload.get("transcript_path")),
        "updated_at": now,
        "last_assistant_message_excerpt": last_message[:MESSAGE_LIMIT],
    }


def _infer_status(message: str) -> str:
    text = message.lower()
    blocked_terms = ("blocked", "failed", "failure", "error", "cannot", "can't")
    waiting_terms = ("waiting", "stand by", "standing by", "wait for")
    done_terms = (
        "completed",
        "complete",
        "done",
        "sent",
        "validated",
        "passed",
        "landed",
        "imported",
    )

    if any(term in text for term in blocked_terms):
        return "blocked"
    if any(term in text for term in waiting_terms):
        return "waiting"
    if any(term in text for term in done_terms):
        return "done"
    return "active"


def _extract_current_assignment(message: str, fallback: str) -> str:
    for line in _meaningful_lines(message):
        lower = line.lower()
        if any(term in lower for term in ("coordinate", "sent track", "track 2", "track two", "review", "design", "run")):
            return line
    return fallback


def _extract_next_action(message: str) -> str:
    candidates = []
    for line in _meaningful_lines(message):
        lower = line.lower()
        if any(
            term in lower
            for term in (
                "next",
                "wait",
                "review",
                "send",
                "land",
                "import",
                "validate",
                "ready",
                "blocked",
            )
        ):
            candidates.append(line)
    return candidates[-1] if candidates else "Review current thread state and decide the next manager action."


def _meaningful_lines(message: str) -> Iterable[str]:
    for raw_line in message.splitlines():
        line = raw_line.strip(" -\t")
        if line:
            yield line[:500]


def _first_nonempty_line(message: str) -> str:
    return next(iter(_meaningful_lines(message)), "No assistant message captured.")


def _optional_str(value: Any) -> Optional[str]:
    return value if isinstance(value, str) and value else None


def _update_ledger(
    repo_root: Path,
    entry: Mapping[str, Any],
    payload: Mapping[str, Any],
    now: str,
) -> None:
    ledger_path = repo_root / ".codex" / "manager-ledger.json"
    ledger = _load_ledger(ledger_path)

    threads = ledger.setdefault("threads", {})
    if not isinstance(threads, dict):
        threads = {}
        ledger["threads"] = threads
    threads[str(entry["thread_id"])] = dict(entry)

    events = ledger.setdefault("events", [])
    if not isinstance(events, list):
        events = []
        ledger["events"] = events
    events.append(
        {
            "thread_id": entry["thread_id"],
            "title": entry["title"],
            "status": entry["status"],
            "last_update": entry["last_update"],
            "next_action": entry["next_action"],
            "turn_id": entry.get("turn_id"),
            "updated_at": now,
        }
    )
    del events[:-EVENT_LIMIT]

    ledger["schema_version"] = 1
    ledger["repo"] = REPO_NAME
    ledger["updated_at"] = now

    tmp_path = ledger_path.with_suffix(ledger_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(ledger_path)


def _load_ledger(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "repo": REPO_NAME, "threads": {}, "events": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": 1, "repo": REPO_NAME, "threads": {}, "events": []}
    return data if isinstance(data, dict) else {"schema_version": 1, "repo": REPO_NAME, "threads": {}, "events": []}


def _write_error(repo_root: Path, exc: Exception) -> None:
    path = repo_root / ".codex" / "manager-ledger.errors.log"
    line = f"{_utc_now()} {type(exc).__name__}: {exc}\n"
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
    except OSError:
        pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _emit_success() -> int:
    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
