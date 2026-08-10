"""
diagnosis.py – Orchestrates the full diagnosis pipeline for NetSage AI.

Combines:
  1. Rule checker (fast, deterministic)
  2. AI engine (Gemini LLM)
  3. Result packaging

This is the primary entry point called by the Streamlit pages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from modules.rule_checker import FindingDict, run_all_rules, get_rule_summary
from modules.ai_engine import DiagnosisResponse, diagnose, diagnose_demo, is_api_key_configured
from modules.utils import generate_case_id, get_timestamp, normalise_osi_layer
from modules import logger as app_logger


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class DiagnosisResult:
    """
    Full result of one diagnosis run including rule findings and AI output.
    """
    case_id: str
    symptom: str
    topology: str
    show_output: str
    timestamp: str

    # Rule checker results
    rule_findings: list[FindingDict] = field(default_factory=list)
    rule_summary: dict[str, int] = field(default_factory=dict)

    # AI diagnosis
    ai_response: DiagnosisResponse | None = None
    ai_error: str | None = None
    is_demo: bool = False

    # Computed
    overall_severity: str = "Unknown"

    def has_ai_response(self) -> bool:
        return self.ai_response is not None

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict for storage/display."""
        ai_data: dict[str, Any] = {}
        if self.ai_response:
            ai_data = self.ai_response.model_dump()
        return {
            "case_id": self.case_id,
            "timestamp": self.timestamp,
            "symptom": self.symptom,
            "topology": self.topology,
            "show_output": self.show_output,
            "rule_findings": self.rule_findings,
            "rule_summary": self.rule_summary,
            "ai_error": self.ai_error,
            "is_demo": self.is_demo,
            "overall_severity": self.overall_severity,
            **ai_data,
        }


# ---------------------------------------------------------------------------
# Severity calculator
# ---------------------------------------------------------------------------

def _calculate_severity(
    rule_findings: list[FindingDict],
    ai_confidence: int = 50,
) -> str:
    """Determine overall severity from rule findings and AI confidence."""
    if not rule_findings:
        return "Low" if ai_confidence < 60 else "Medium"
    severities = [f.get("severity", "Low") for f in rule_findings]
    if "Critical" in severities:
        return "Critical"
    if "High" in severities:
        return "High"
    if "Medium" in severities:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_diagnosis(
    symptom: str,
    topology: str,
    show_output: str,
    case_id: str | None = None,
    use_demo_if_no_key: bool = True,
) -> DiagnosisResult:
    """
    Run the complete diagnosis pipeline.

    Step 1: Rule checker (always runs, no API needed).
    Step 2: AI engine (Gemini) or demo fallback.

    Parameters
    ----------
    symptom:              Observed network problem.
    topology:             Topology description.
    show_output:          Cisco show command outputs.
    case_id:              Optional case ID (auto-generated if None).
    use_demo_if_no_key:   If True, use demo mode when no API key is set.

    Returns
    -------
    DiagnosisResult dataclass.
    """
    cid = case_id or generate_case_id()
    ts = get_timestamp()

    result = DiagnosisResult(
        case_id=cid,
        symptom=symptom,
        topology=topology,
        show_output=show_output,
        timestamp=ts,
    )

    # -----------------------------------------------------------------------
    # Step 1: Rule checker
    # -----------------------------------------------------------------------
    try:
        findings = run_all_rules(symptom, show_output)
        result.rule_findings = findings
        result.rule_summary = get_rule_summary(findings)
        app_logger.log_rule_checker(cid, findings)
    except Exception as exc:
        result.rule_findings = []
        result.rule_summary = {}
        app_logger.log_ai_error(cid, f"Rule checker error: {exc}")

    # -----------------------------------------------------------------------
    # Step 2: AI diagnosis
    # -----------------------------------------------------------------------
    api_configured = is_api_key_configured()

    if not api_configured and use_demo_if_no_key:
        # Demo mode
        result.ai_response = diagnose_demo(symptom)
        result.is_demo = True
    else:
        try:
            result.ai_response = diagnose(
                symptom=symptom,
                topology=topology,
                show_output=show_output,
                case_id=cid,
            )
            result.is_demo = False
        except Exception as exc:
            result.ai_error = str(exc)
            result.ai_response = None

    # -----------------------------------------------------------------------
    # Calculate overall severity
    # -----------------------------------------------------------------------
    ai_conf = result.ai_response.confidence_int() if result.ai_response else 50
    result.overall_severity = _calculate_severity(result.rule_findings, ai_conf)

    return result


# ---------------------------------------------------------------------------
# Convenience: format diagnosis for display
# ---------------------------------------------------------------------------

def format_fix_steps_for_display(fix_steps_raw: str) -> list[str]:
    """Split fix steps string into a clean numbered list."""
    if not fix_steps_raw:
        return []
    import re
    steps: list[str] = []
    for line in fix_steps_raw.splitlines():
        line = line.strip()
        if line:
            # Remove leading "Step N:" if present
            line = re.sub(r"^Step\s*\d+[:.]\s*", "", line)
            steps.append(line)
    return steps
