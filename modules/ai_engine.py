"""
ai_engine.py – Gemini API integration for NetSage AI.

Responsibilities:
  - Load API key from environment/.env
  - Load system prompt
  - Build and send the diagnosis prompt to Gemini
  - Validate and parse JSON response (with Pydantic)
  - Retry up to MAX_RETRIES on invalid JSON
  - Handle API errors gracefully
  - Return a typed DiagnosisResponse
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

# Load .env if present (optional; works with or without python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)
except ImportError:
    pass  # dotenv is optional; key can be set manually

try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

from modules.prompt_loader import get_system_prompt, build_diagnosis_prompt
from modules import logger as app_logger

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2.0

# ---------------------------------------------------------------------------
# Pydantic response model
# ---------------------------------------------------------------------------


class DiagnosisResponse(BaseModel):
    """Validated AI diagnosis output."""

    root_cause: str = Field(..., min_length=5)
    confidence: str = Field(default="50")
    osi_layer: str = Field(default="Layer 3 – Network")
    evidence: str = Field(default="")
    next_command: str = Field(default="show ip interface brief")
    fix_steps: str = Field(default="")

    @field_validator("confidence", mode="before")
    @classmethod
    def coerce_confidence(cls, v: Any) -> str:
        """Ensure confidence is a string integer 0-100."""
        try:
            val = int(float(str(v)))
            val = max(0, min(100, val))
            return str(val)
        except (TypeError, ValueError):
            return "50"

    @field_validator("osi_layer", mode="before")
    @classmethod
    def normalise_osi(cls, v: Any) -> str:
        from modules.utils import normalise_osi_layer
        return normalise_osi_layer(str(v))

    def confidence_int(self) -> int:
        """Return confidence as integer."""
        return int(self.confidence)


# ---------------------------------------------------------------------------
# API key management
# ---------------------------------------------------------------------------

def get_api_key() -> str | None:
    """Return the Gemini API key from environment, or None if not set."""
    return os.getenv("GEMINI_API_KEY") or None


def is_api_key_configured() -> bool:
    """Return True if a non-empty API key is available."""
    key = get_api_key()
    return bool(key and key.strip() and key != "your_gemini_api_key_here")


# ---------------------------------------------------------------------------
# JSON extraction helpers
# ---------------------------------------------------------------------------

def _extract_json_from_text(text: str) -> dict[str, Any]:
    """
    Extract the first JSON object from a text string.

    Handles:
    - Pure JSON response
    - JSON wrapped in markdown code fences
    - JSON embedded in explanation text
    """
    # Strip markdown fences
    text = re.sub(r"```(?:json)?", "", text).strip("`").strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find first { ... } block
    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in response: {text[:300]}")


# ---------------------------------------------------------------------------
# Core diagnosis function
# ---------------------------------------------------------------------------

def diagnose(
    symptom: str,
    topology: str,
    show_output: str,
    case_id: str = "ADHOC",
    model_name: str | None = None,
) -> DiagnosisResponse:
    """
    Send a diagnosis request to Gemini and return a validated DiagnosisResponse.

    Parameters
    ----------
    symptom:     Observed network problem description.
    topology:    Network topology notes.
    show_output: Cisco 'show' command outputs.
    case_id:     Identifier for logging purposes.
    model_name:  Optional Gemini model override.

    Returns
    -------
    DiagnosisResponse (Pydantic model)

    Raises
    ------
    RuntimeError: If API key is missing or not configured.
    Exception:    After MAX_RETRIES attempts on persistent failures.
    """
    if not _GENAI_AVAILABLE:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install google-genai"
        )

    api_key = get_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Create a .env file with your API key. "
            "Get one at: https://aistudio.google.com/app/apikey"
        )

    model_id = model_name or DEFAULT_MODEL

    # Log the request
    app_logger.log_ai_request(case_id, symptom, topology, show_output)

    system_prompt = get_system_prompt()
    user_prompt = build_diagnosis_prompt(symptom, topology, show_output)

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_id,
                contents=[
                    genai_types.Content(
                        role="user",
                        parts=[genai_types.Part(text=user_prompt)],
                    )
                ],
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                    max_output_tokens=1024,
                ),
            )
            raw_text = response.text.strip()
            parsed = _extract_json_from_text(raw_text)
            validated = DiagnosisResponse(**parsed)
            app_logger.log_ai_response(case_id, validated.model_dump(), attempt, model_id)
            return validated

        except Exception as exc:
            last_error = exc
            app_logger.log_ai_error(case_id, str(exc), attempt)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            continue

    raise RuntimeError(
        f"AI diagnosis failed after {MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    ) from last_error


# ---------------------------------------------------------------------------
# Demo / offline fallback
# ---------------------------------------------------------------------------

def diagnose_demo(symptom: str) -> DiagnosisResponse:
    """
    Return a realistic demo DiagnosisResponse without calling the API.
    Used when no API key is configured, for UI demonstration.
    """
    return DiagnosisResponse(
        root_cause=(
            "DEMO MODE – API key not configured. "
            "Based on the symptom pattern, the most likely cause is an interface "
            "shutdown or missing route configuration. Please set GEMINI_API_KEY "
            "to enable real AI diagnosis."
        ),
        confidence="72",
        osi_layer="Layer 3 – Network",
        evidence=(
            "Symptom keyword analysis suggests a Layer 3 routing issue. "
            "Common causes include: missing static route, shutdown interface, or "
            "incorrect subnet mask."
        ),
        next_command="show ip route",
        fix_steps=(
            "Step 1: Check interface status: show ip interface brief\n"
            "Step 2: Verify routing table: show ip route\n"
            "Step 3: If interface is down: no shutdown\n"
            "Step 4: If route missing: ip route <dest> <mask> <next-hop>\n"
            "Step 5: Re-test connectivity: ping <destination>"
        ),
    )
