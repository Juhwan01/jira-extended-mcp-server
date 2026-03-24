"""Atlassian Document Format (ADF) helpers."""

from __future__ import annotations

from typing import Any


def text_to_adf(text: str) -> dict[str, Any]:
    """Convert plain text to ADF document format.

    Splits on newlines to create separate paragraphs.
    """
    paragraphs = []
    for line in text.split("\n"):
        if line.strip():
            paragraphs.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}],
            })
        else:
            paragraphs.append({"type": "paragraph", "content": []})

    if not paragraphs:
        paragraphs = [{"type": "paragraph", "content": []}]

    return {"type": "doc", "version": 1, "content": paragraphs}


def adf_to_text(adf: dict[str, Any] | None) -> str:
    """Convert ADF document to plain text."""
    if not adf or not isinstance(adf, dict):
        return ""

    parts: list[str] = []
    _extract_text(adf, parts)
    return "\n".join(parts)


def _extract_text(node: dict[str, Any], parts: list[str]) -> None:
    """Recursively extract text from ADF nodes."""
    if node.get("type") == "text":
        parts.append(node.get("text", ""))
        return

    for child in node.get("content", []):
        if isinstance(child, dict):
            _extract_text(child, parts)
