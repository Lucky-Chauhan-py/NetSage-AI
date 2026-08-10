"""
logger.py – JSON-based logging for NetSage AI.

Maintains a rotating set of JSON log files (one per session) inside the
/logs directory.  Logs every AI request, AI response, human review action,
and rule checker result.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# Root project directory (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = _PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _log_file() -> Path:
    """Return today's log file path, creating it if necessary."""
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    return LOGS_DIR / f"netsage_{date_str}.json"


def _append_entry(entry: dict[str, Any]) -> None:
    """Append a single JSON entry to the daily log file (JSON Lines format)."""
    try:
        log_path = _log_file()
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception as exc:  # pragma: no cover
        # Never let logging crash the application
        print(f"[NetSage Logger] Failed to write log: {exc}")


def _make_entry(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Build a standard log entry dictionary."""
    return {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "event_type": event_type,
        **payload,
    }


# ---------------------------------------------------------------------------
# Public logging functions
# ---------------------------------------------------------------------------

def log_ai_request(
    case_id: str,
    symptom: str,
    topology: str,
    show_output: str,
) -> None:
    """Log an outgoing AI diagnosis request."""
    entry = _make_entry(
        "AI_REQUEST",
        {
            "case_id": case_id,
            "symptom_length": len(symptom),
            "topology_length": len(topology),
            "show_output_length": len(show_output),
            "symptom_preview": symptom[:200],
        },
    )
    _append_entry(entry)


def log_ai_response(
    case_id: str,
    response: dict[str, Any],
    attempt: int = 1,
    model: str = "gemini-1.5-flash",
) -> None:
    """Log an incoming AI diagnosis response."""
    entry = _make_entry(
        "AI_RESPONSE",
        {
            "case_id": case_id,
            "model": model,
            "attempt": attempt,
            "root_cause_preview": str(response.get("root_cause", ""))[:200],
            "confidence": response.get("confidence"),
            "osi_layer": response.get("osi_layer"),
            "has_fix_steps": bool(response.get("fix_steps")),
        },
    )
    _append_entry(entry)


def log_ai_error(case_id: str, error: str, attempt: int = 1) -> None:
    """Log an AI API or JSON parsing error."""
    entry = _make_entry(
        "AI_ERROR",
        {"case_id": case_id, "attempt": attempt, "error": str(error)[:500]},
    )
    _append_entry(entry)


def log_rule_checker(
    case_id: str,
    findings: list[dict[str, Any]],
) -> None:
    """Log rule checker findings."""
    entry = _make_entry(
        "RULE_CHECKER",
        {
            "case_id": case_id,
            "finding_count": len(findings),
            "findings": findings[:20],  # cap to avoid huge log entries
        },
    )
    _append_entry(entry)


def log_human_review(
    review_id: str,
    case_id: str,
    status: str,
    reviewer_name: str,
    comments: str,
) -> None:
    """Log a human review action (Accept / Edit / Reject)."""
    entry = _make_entry(
        "HUMAN_REVIEW",
        {
            "review_id": review_id,
            "case_id": case_id,
            "status": status,
            "reviewer_name": reviewer_name,
            "comment_length": len(comments),
        },
    )
    _append_entry(entry)


def log_csv_operation(operation: str, file_path: str, rows_affected: int = 0) -> None:
    """Log a CSV file operation (upload, download, edit, delete)."""
    entry = _make_entry(
        "CSV_OPERATION",
        {
            "operation": operation,
            "file": Path(file_path).name,
            "rows_affected": rows_affected,
        },
    )
    _append_entry(entry)


# ---------------------------------------------------------------------------
# Log reader
# ---------------------------------------------------------------------------

def read_recent_logs(n: int = 100) -> list[dict[str, Any]]:
    """
    Read the most recent *n* log entries from all log files, newest first.
    """
    all_entries: list[dict[str, Any]] = []
    try:
        for log_file in sorted(LOGS_DIR.glob("netsage_*.json"), reverse=True):
            with log_file.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            all_entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            if len(all_entries) >= n:
                break
    except Exception:  # pragma: no cover
        pass
    return all_entries[:n]


def get_log_files() -> list[Path]:
    """Return list of existing log file paths, newest first."""
    return sorted(LOGS_DIR.glob("netsage_*.json"), reverse=True)
