"""
utils.py – Shared utility functions for NetSage AI.

Provides common helpers for formatting, validation, OSI layer mapping,
severity colour coding, and other cross-module utilities.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any


# ---------------------------------------------------------------------------
# OSI Layer helpers
# ---------------------------------------------------------------------------

OSI_LAYERS: dict[str, str] = {
    "Layer 1": "Physical",
    "Layer 2": "Data Link",
    "Layer 3": "Network",
    "Layer 4": "Transport",
    "Layer 5": "Session",
    "Layer 6": "Presentation",
    "Layer 7": "Application",
}

OSI_COLORS: dict[str, str] = {
    "Layer 1 – Physical":       "#EF4444",
    "Layer 2 – Data Link":      "#F97316",
    "Layer 3 – Network":        "#EAB308",
    "Layer 4 – Transport":      "#22C55E",
    "Layer 5 – Session":        "#06B6D4",
    "Layer 6 – Presentation":   "#8B5CF6",
    "Layer 7 – Application":    "#EC4899",
}

SEVERITY_COLORS: dict[str, str] = {
    "Critical": "#DC2626",
    "High":     "#EA580C",
    "Medium":   "#CA8A04",
    "Low":      "#16A34A",
    "Info":     "#2563EB",
}

SEVERITY_EMOJI: dict[str, str] = {
    "Critical": "🔴",
    "High":     "🟠",
    "Medium":   "🟡",
    "Low":      "🟢",
    "Info":     "🔵",
}


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def get_timestamp() -> str:
    """Return ISO-8601 UTC timestamp string."""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def generate_case_id() -> str:
    """Generate a unique case ID based on current timestamp."""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"CASE-{ts}"


def generate_review_id() -> str:
    """Generate a unique review ID based on current timestamp."""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"REV-{ts}"


def truncate_text(text: str, max_len: int = 120) -> str:
    """Truncate text to *max_len* characters, appending ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def confidence_to_label(confidence: int | str) -> tuple[str, str]:
    """Convert a 0-100 confidence value to a (label, colour) pair."""
    val = int(confidence)
    if val >= 90:
        return "Very High", "#22C55E"
    elif val >= 75:
        return "High", "#84CC16"
    elif val >= 55:
        return "Medium", "#EAB308"
    elif val >= 35:
        return "Low", "#F97316"
    else:
        return "Very Low", "#EF4444"


def severity_color(severity: str) -> str:
    """Return hex colour for a severity label."""
    return SEVERITY_COLORS.get(severity, "#6B7280")


def osi_color(osi_layer: str) -> str:
    """Return hex colour for an OSI layer string."""
    # Try exact match first
    if osi_layer in OSI_COLORS:
        return OSI_COLORS[osi_layer]
    # Fuzzy: try to match on layer number prefix
    for key, color in OSI_COLORS.items():
        if osi_layer.startswith(key.split(" –")[0]):
            return color
    return "#6B7280"


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

IP_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)

SUBNET_PATTERN = re.compile(
    r"\b(255\.(?:255\.(?:255\.(?:0|128|192|224|240|248|252|254|255)|0)|0)|0)\.0\.0\b"
)


def extract_ips(text: str) -> list[str]:
    """Extract all IP addresses from a text string."""
    return IP_PATTERN.findall(text)


def is_valid_ip(ip: str) -> bool:
    """Validate an IPv4 address string."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    return all(0 <= int(p) <= 255 for p in parts if p.isdigit())


def sanitise_input(text: str) -> str:
    """Basic sanitisation – strip leading/trailing whitespace."""
    return text.strip() if text else ""


# ---------------------------------------------------------------------------
# OSI layer normalisation
# ---------------------------------------------------------------------------

def normalise_osi_layer(raw: str) -> str:
    """
    Normalise an OSI layer string to the canonical format used in the app.

    Examples
    --------
    "layer 3"           → "Layer 3 – Network"
    "Layer 2 – Data Link" → "Layer 2 – Data Link"   (pass-through)
    "physical"          → "Layer 1 – Physical"
    """
    raw_lower = raw.lower().strip()

    # Full keyword match
    keyword_map = {
        "physical": "Layer 1 – Physical",
        "data link": "Layer 2 – Data Link",
        "network": "Layer 3 – Network",
        "transport": "Layer 4 – Transport",
        "session": "Layer 5 – Session",
        "presentation": "Layer 6 – Presentation",
        "application": "Layer 7 – Application",
    }
    for keyword, canonical in keyword_map.items():
        if keyword in raw_lower:
            return canonical

    # Numeric match
    num_map = {
        "layer 1": "Layer 1 – Physical",
        "layer 2": "Layer 2 – Data Link",
        "layer 3": "Layer 3 – Network",
        "layer 4": "Layer 4 – Transport",
        "layer 5": "Layer 5 – Session",
        "layer 6": "Layer 6 – Presentation",
        "layer 7": "Layer 7 – Application",
    }
    for prefix, canonical in num_map.items():
        if raw_lower.startswith(prefix):
            return canonical

    # Return original if no match
    return raw


def format_fix_steps(fix_steps_raw: str) -> list[str]:
    """
    Parse a fix_steps string into a list of individual steps.
    Handles newline-separated and already-split lists.
    """
    if not fix_steps_raw:
        return []
    lines = fix_steps_raw.splitlines()
    steps: list[str] = []
    for line in lines:
        line = line.strip()
        if line:
            # Strip leading "Step N:" prefix if present
            line = re.sub(r"^Step\s+\d+[:.]\s*", "", line)
            steps.append(line)
    return steps


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------

def safe_int(value: Any, default: int = 0) -> int:
    """Convert a value to int safely, returning *default* on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def badge_html(label: str, color: str) -> str:
    """Return an HTML span badge string (used in Streamlit markdown)."""
    return (
        f'<span style="background:{color};color:#fff;padding:3px 10px;'
        f'border-radius:12px;font-size:0.78rem;font-weight:600;">{label}</span>'
    )
