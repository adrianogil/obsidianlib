"""Parse YAML frontmatter from Markdown documents."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import yaml


class FrontmatterError(ValueError):
    """Raised when a document contains invalid YAML frontmatter."""


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return a document's frontmatter metadata and unchanged Markdown body.

    A document without an opening ``---`` delimiter has no frontmatter, so its
    full text is returned as the body. Once an opening delimiter is present,
    both a closing delimiter and a YAML mapping are required.
    """

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return {}, text

    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.rstrip("\r\n") == "---"
        ),
        None,
    )
    if closing_index is None:
        raise FrontmatterError("frontmatter is missing a closing '---' delimiter")

    yaml_text = "".join(lines[1:closing_index])
    try:
        metadata = yaml.safe_load(yaml_text)
    except yaml.YAMLError as error:
        raise FrontmatterError(f"invalid YAML frontmatter: {error}") from error

    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise FrontmatterError("frontmatter must contain a YAML mapping")

    body = "".join(lines[closing_index + 1 :])
    return metadata, body
