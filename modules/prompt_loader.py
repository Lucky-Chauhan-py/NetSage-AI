"""
prompt_loader.py – Load and compose prompts for the AI engine.

Reads Markdown prompt files from the /prompts directory and assembles
the final prompt string to be sent to Gemini.
"""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

# Prompts directory (sibling to /modules)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = _PROJECT_ROOT / "prompts"

DIAGNOSE_PROMPT_FILE = PROMPTS_DIR / "diagnose_prompt.md"
FEW_SHOT_FILE = PROMPTS_DIR / "few_shot_examples.md"


# ---------------------------------------------------------------------------
# File readers (cached for performance)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=4)
def _read_file(path: Path) -> str:
    """Read and cache a prompt file. Raises FileNotFoundError if missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}. "
            "Ensure the /prompts directory is present."
        )
    return path.read_text(encoding="utf-8").strip()


def get_system_prompt() -> str:
    """Return the system prompt from diagnose_prompt.md."""
    return _read_file(DIAGNOSE_PROMPT_FILE)


def get_few_shot_examples() -> str:
    """Return the few-shot examples from few_shot_examples.md."""
    return _read_file(FEW_SHOT_FILE)


# ---------------------------------------------------------------------------
# Prompt composer
# ---------------------------------------------------------------------------

def build_diagnosis_prompt(
    symptom: str,
    topology: str,
    show_output: str,
    include_few_shot: bool = True,
) -> str:
    """
    Compose the full user prompt to send to Gemini.

    The system prompt is returned separately (for use as the system role).
    This function builds the *user message* containing the incident data.

    Parameters
    ----------
    symptom:           What the user observed / reported.
    topology:          Network topology description.
    show_output:       Paste of Cisco 'show' command outputs.
    include_few_shot:  Whether to prepend few-shot examples.

    Returns
    -------
    Composed user prompt string.
    """
    sections: list[str] = []

    if include_few_shot:
        try:
            examples = get_few_shot_examples()
            sections.append(f"## Reference Examples\n\n{examples}")
        except FileNotFoundError:
            pass  # Gracefully skip if file missing

    sections.append(
        "## Incident to Diagnose\n\n"
        f"**Symptom:**\n{symptom.strip()}\n\n"
        f"**Topology Notes:**\n{topology.strip() if topology.strip() else 'Not provided'}\n\n"
        f"**Cisco Show Outputs:**\n```\n{show_output.strip() if show_output.strip() else 'Not provided'}\n```"
    )

    sections.append(
        "## Instructions\n\n"
        "Analyse the incident above using OSI layer methodology. "
        "Return ONLY the JSON diagnosis object. "
        "Do not include markdown code fences, backticks, or any text outside the JSON object."
    )

    return "\n\n---\n\n".join(sections)


def reload_prompts() -> None:
    """Clear the prompt cache to force re-reading from disk."""
    _read_file.cache_clear()
