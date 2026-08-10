"""
csv_manager.py – CSV read/write/CRUD operations for NetSage AI.

Handles cases.csv and human_review_log.csv with schema validation,
safe row operations, and data integrity checks.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd

# Project paths
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = _PROJECT_ROOT / "data"
CASES_CSV = DATA_DIR / "cases.csv"
REVIEWS_CSV = DATA_DIR / "human_review_log.csv"

# ---------------------------------------------------------------------------
# Schema definitions
# ---------------------------------------------------------------------------

CASES_COLUMNS = [
    "case_id", "symptom", "topology_note", "show_output",
    "expected_fault", "osi_layer", "concept_tag", "severity", "correct_answer",
]

REVIEWS_COLUMNS = [
    "review_id", "case_id", "original_symptom",
    "ai_root_cause", "ai_osi_layer", "ai_confidence", "ai_fix_steps",
    "human_root_cause", "human_osi_layer", "human_fix_steps", "human_evidence",
    "status", "reviewer_comments", "reviewer_name", "timestamp",
]

VALID_SEVERITIES = {"Critical", "High", "Medium", "Low", "Info"}
VALID_STATUSES = {"Accepted", "Edited", "Rejected"}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_file(path: Path, columns: list[str]) -> None:
    """Create a CSV file with headers if it does not exist."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=columns).to_csv(path, index=False)


def _load(path: Path, columns: list[str]) -> pd.DataFrame:
    """Load a CSV into a DataFrame, creating with headers if missing."""
    _ensure_file(path, columns)
    try:
        df = pd.read_csv(path, dtype=str)
        # Add any missing columns
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df[columns].fillna("")
    except Exception as exc:
        raise IOError(f"Failed to read {path.name}: {exc}") from exc


def _save(df: pd.DataFrame, path: Path) -> None:
    """Save a DataFrame to CSV."""
    try:
        df.to_csv(path, index=False)
    except Exception as exc:
        raise IOError(f"Failed to write {path.name}: {exc}") from exc


# ---------------------------------------------------------------------------
# Cases CSV
# ---------------------------------------------------------------------------

def load_cases() -> pd.DataFrame:
    """Load cases.csv into a DataFrame."""
    return _load(CASES_CSV, CASES_COLUMNS)


def save_cases(df: pd.DataFrame) -> None:
    """Persist the cases DataFrame to cases.csv."""
    _save(df[CASES_COLUMNS], CASES_CSV)


def get_case_by_id(case_id: str) -> dict[str, Any] | None:
    """Return a single case dict by case_id, or None if not found."""
    df = load_cases()
    match = df[df["case_id"] == case_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def add_case(row: dict[str, Any]) -> None:
    """Append a new case row to cases.csv."""
    df = load_cases()
    new_row = pd.DataFrame([{col: row.get(col, "") for col in CASES_COLUMNS}])
    df = pd.concat([df, new_row], ignore_index=True)
    save_cases(df)


def update_case(case_id: str, updates: dict[str, Any]) -> bool:
    """Update an existing case by case_id. Returns True if found and updated."""
    df = load_cases()
    mask = df["case_id"] == case_id
    if not mask.any():
        return False
    for col, val in updates.items():
        if col in df.columns:
            df.loc[mask, col] = str(val)
    save_cases(df)
    return True


def delete_case(case_id: str) -> bool:
    """Delete a case by case_id. Returns True if deleted."""
    df = load_cases()
    before = len(df)
    df = df[df["case_id"] != case_id]
    if len(df) == before:
        return False
    save_cases(df)
    return True


def import_cases_from_upload(uploaded_file: Any) -> tuple[bool, str, int]:
    """
    Import cases from an uploaded CSV file.

    Returns (success, message, rows_imported).
    """
    try:
        content = uploaded_file.read()
        new_df = pd.read_csv(io.BytesIO(content), dtype=str).fillna("")
        # Validate columns
        missing = [c for c in CASES_COLUMNS if c not in new_df.columns]
        if missing:
            return False, f"Missing columns: {missing}", 0
        existing = load_cases()
        combined = pd.concat([existing, new_df[CASES_COLUMNS]], ignore_index=True)
        combined.drop_duplicates(subset=["case_id"], keep="last", inplace=True)
        save_cases(combined)
        return True, "Import successful.", len(new_df)
    except Exception as exc:
        return False, f"Import failed: {exc}", 0


# ---------------------------------------------------------------------------
# Human Review CSV
# ---------------------------------------------------------------------------

def load_reviews() -> pd.DataFrame:
    """Load human_review_log.csv into a DataFrame."""
    return _load(REVIEWS_CSV, REVIEWS_COLUMNS)


def save_reviews(df: pd.DataFrame) -> None:
    """Persist the reviews DataFrame."""
    _save(df[REVIEWS_COLUMNS], REVIEWS_CSV)


def add_review(row: dict[str, Any]) -> None:
    """Append a new review row to human_review_log.csv."""
    df = load_reviews()
    new_row = pd.DataFrame([{col: row.get(col, "") for col in REVIEWS_COLUMNS}])
    df = pd.concat([df, new_row], ignore_index=True)
    save_reviews(df)


def get_review_stats() -> dict[str, Any]:
    """Compute review statistics for the dashboard."""
    df = load_reviews()
    if df.empty:
        return {
            "total": 0,
            "accepted": 0,
            "edited": 0,
            "rejected": 0,
            "ai_agreement_pct": 0.0,
        }
    total = len(df)
    accepted = len(df[df["status"] == "Accepted"])
    edited = len(df[df["status"] == "Edited"])
    rejected = len(df[df["status"] == "Rejected"])
    ai_agreement_pct = round((accepted / total) * 100, 1) if total else 0.0
    return {
        "total": total,
        "accepted": accepted,
        "edited": edited,
        "rejected": rejected,
        "ai_agreement_pct": ai_agreement_pct,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_cases_df(df: pd.DataFrame) -> list[str]:
    """
    Validate a cases DataFrame and return a list of error strings.
    Empty list means the dataset is valid.
    """
    errors: list[str] = []
    # Check required columns
    for col in CASES_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")
    if errors:
        return errors  # Stop early if columns missing

    # Check for duplicate case_ids
    dupes = df[df.duplicated(subset=["case_id"])]["case_id"].tolist()
    if dupes:
        errors.append(f"Duplicate case_ids found: {dupes}")

    # Check severity values
    invalid_sev = df[~df["severity"].isin(VALID_SEVERITIES | {""})]
    if not invalid_sev.empty:
        errors.append(
            f"Invalid severity values in rows: {invalid_sev.index.tolist()}"
        )

    # Check empty required fields
    for col in ["case_id", "symptom", "expected_fault"]:
        empties = df[df[col].str.strip() == ""]
        if not empties.empty:
            errors.append(f"Empty '{col}' in rows: {empties.index.tolist()}")

    return errors


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def cases_to_csv_bytes() -> bytes:
    """Return the cases CSV as bytes for download."""
    df = load_cases()
    return df.to_csv(index=False).encode("utf-8")


def reviews_to_csv_bytes() -> bytes:
    """Return the reviews CSV as bytes for download."""
    df = load_reviews()
    return df.to_csv(index=False).encode("utf-8")
