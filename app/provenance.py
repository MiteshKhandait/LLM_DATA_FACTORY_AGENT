import re
from typing import Any

from app.models import Document


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.

    This removes differences caused by:
    - capitalization
    - repeated whitespace
    - line breaks
    """

    text = text.casefold()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def compact_text(text: str) -> str:
    """
    Create a more tolerant representation for matching.

    This removes whitespace and punctuation so that small formatting
    differences such as '150 crore' vs '150crore' do not prevent
    a source match.
    """

    return re.sub(
        r"[^a-z0-9]+",
        "",
        text.casefold(),
    )


def find_evidence(
    document: Document,
    evidence: str | None,
) -> dict[str, Any]:
    """
    Search the document's source segments for the supplied evidence.

    Returns the exact source segment and its location when a match
    is found.
    """

    if not evidence:
        return {
            "verified": False,
            "reason": "No evidence was provided.",
        }

    evidence_normalized = normalize_text(evidence)
    evidence_compact = compact_text(evidence)

    for segment in document.segments:

        segment_normalized = normalize_text(
            segment.text
        )

        # First try a normal normalized-text match.
        if evidence_normalized in segment_normalized:
            return {
                "verified": True,
                "evidence": segment.text,
                "source": document.source,
                "segment_id": segment.segment_id,
                "location": segment.location,
                "match_type": "normalized_text",
            }

        # Then try the more tolerant compact representation.
        segment_compact = compact_text(
            segment.text
        )

        if evidence_compact in segment_compact:
            return {
                "verified": True,
                "evidence": segment.text,
                "source": document.source,
                "segment_id": segment.segment_id,
                "location": segment.location,
                "match_type": "compact_text",
            }

    return {
        "verified": False,
        "reason": "Evidence could not be located in the document.",
        "requested_evidence": evidence,
    }