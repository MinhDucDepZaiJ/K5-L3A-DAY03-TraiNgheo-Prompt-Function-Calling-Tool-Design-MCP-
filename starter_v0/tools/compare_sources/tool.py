
from __future__ import annotations

import re
from difflib import SequenceMatcher


def _sentences(text: str) -> list[str]:
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+|\n+", text)
        if s.strip()
    ]


def compare_sources(
    source_a: str,
    source_b: str,
    title_a: str = "Source A",
    title_b: str = "Source B",
) -> dict:
    """
    Compare two supplied source texts.
    Uses lexical similarity, not factual verification.
    """
    if not isinstance(source_a, str) or not source_a.strip():
        return {"error": "source_a must not be empty"}

    if not isinstance(source_b, str) or not source_b.strip():
        return {"error": "source_b must not be empty"}

    a = _sentences(source_a)
    b = _sentences(source_b)

    def normalize(s: str) -> str:
        return " ".join(s.casefold().split())

    def similar(x: str, y: str) -> bool:
        return SequenceMatcher(
            None, normalize(x), normalize(y)
        ).ratio() >= 0.85

    matched_b = set()
    common = []
    unique_a = []

    for sentence_a in a:
        match_index = next(
            (
                i for i, sentence_b in enumerate(b)
                if i not in matched_b
                and similar(sentence_a, sentence_b)
            ),
            None,
        )

        if match_index is not None:
            matched_b.add(match_index)
            common.append({
                "source_a": sentence_a,
                "source_b": b[match_index],
            })
        else:
            unique_a.append(sentence_a)

    unique_b = [
        sentence
        for i, sentence in enumerate(b)
        if i not in matched_b
    ]

    similarity = SequenceMatcher(
        None, normalize(source_a), normalize(source_b)
    ).ratio()

    return {
        "tool": "compare_sources",
        "title_a": title_a,
        "title_b": title_b,
        "similarity_score": round(similarity, 4),
        "common_statements": common,
        "unique_to_a": unique_a,
        "unique_to_b": unique_b,
        "note": (
            "Lexical comparison only. Unique statements "
            "are not necessarily contradictions. "
            "Facts have not been verified."
        ),
    }
