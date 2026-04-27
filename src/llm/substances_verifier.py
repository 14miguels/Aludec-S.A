"""LLM-based verifier for substances extracted from SDS Section 3.

This module is intentionally generic. It does not contain supplier-specific
hardcoded substance lists. Its purpose is to ask the LLM to verify and clean the
substances already extracted from Section 3 using the original Section 3 text as
source of truth.
"""

import json
import logging
from typing import Any
from src.llm.prompts import SUBSTANCES_VERIFICATION_PROMPT
from src.llm.client import call_llm
from src.schema.schema import Substance

logger = logging.getLogger(__name__)



def _substance_to_dict(substance: Substance | dict[str, Any]) -> dict[str, Any]:
    """Convert a Substance object or dictionary into a plain dictionary."""
    if isinstance(substance, dict):
        return {
            "name": substance.get("name"),
            "cas_number": substance.get("cas_number"),
            "ce_number": substance.get("ce_number"),
            "percentage": substance.get("percentage"),
        }

    return {
        "name": getattr(substance, "name", None),
        "cas_number": getattr(substance, "cas_number", None),
        "ce_number": getattr(substance, "ce_number", None),
        "percentage": getattr(substance, "percentage", None),
    }


def _dict_to_substance(data: dict[str, Any]) -> Substance:
    """Convert a plain dictionary into a Substance object."""
    return Substance(
        name=data.get("name"),
        cas_number=data.get("cas_number"),
        ce_number=data.get("ce_number"),
        percentage=data.get("percentage"),
    )


def _parse_json_array(response: str) -> list[dict[str, Any]]:
    """Parse a JSON array returned by the LLM."""
    if not response:
        return []

    cleaned = response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    parsed = json.loads(cleaned)

    if not isinstance(parsed, list):
        raise ValueError("Substance verifier response is not a JSON array")

    normalized = []
    for item in parsed:
        if not isinstance(item, dict):
            continue

        normalized.append({
            "name": item.get("name"),
            "cas_number": item.get("cas_number"),
            "ce_number": item.get("ce_number"),
            "percentage": item.get("percentage"),
        })

    return normalized


def verify_substances_with_llm(
    section_text: str,
    substances: list[Substance] | list[dict[str, Any]],
) -> tuple[list[Substance], list[str]]:
    """Verify and clean Section 3 substances using an additional LLM call.

    Args:
        section_text: Original text from SDS Section 3.
        substances: Substances extracted by the primary Section 3 extractor.

    Returns:
        A tuple with:
        - verified substances;
        - warnings generated during verification.
    """
    warnings = []

    if not section_text:
        warnings.append("Substance verifier skipped: missing Section 3 text")
        return list(substances or []), warnings

    extracted_substances = [_substance_to_dict(substance) for substance in substances or []]

    prompt = SUBSTANCES_VERIFICATION_PROMPT.format(
        section_text=section_text,
        extracted_substances_json=json.dumps(
            extracted_substances,
            ensure_ascii=False,
            indent=2,
        ),
    )

    try:
        logger.info("LLM substance verifier triggered")
        response = call_llm(prompt)
        verified_dicts = _parse_json_array(response)
    except Exception as exc:
        warnings.append(f"Substance verifier failed: {exc}")
        logger.warning("Substance verifier failed: %s", exc)
        return list(substances or []), warnings

    if not verified_dicts:
        warnings.append("Substance verifier returned no substances; keeping original extraction")
        return list(substances or []), warnings

    verified_substances = [_dict_to_substance(item) for item in verified_dicts]

    if len(verified_substances) != len(extracted_substances):
        warnings.append(
            "Substance verifier changed substance count "
            f"from {len(extracted_substances)} to {len(verified_substances)}"
        )

    return verified_substances, warnings
