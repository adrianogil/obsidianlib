"""Parse YAML frontmatter from Markdown documents."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import yaml
from yaml.composer import ComposerError
from yaml.events import AliasEvent


class FrontmatterError(ValueError):
    """Raised when a document contains invalid YAML frontmatter."""


class _NoAliasSafeLoader(yaml.SafeLoader):
    """Load safe YAML while rejecting aliases and their expansion risks."""

    def compose_node(self, parent: Any, index: Any) -> Any:
        if self.check_event(AliasEvent):
            event = self.peek_event()
            raise ComposerError(
                None,
                None,
                "YAML aliases are not allowed in frontmatter",
                event.start_mark,
            )
        return super().compose_node(parent, index)


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return a document's frontmatter metadata and unchanged Markdown body.

    A document without an opening ``---`` delimiter has no frontmatter, so its
    full text is returned as the body. Once an opening delimiter is present,
    both a closing delimiter and a YAML mapping are required. YAML is loaded
    safely, and aliases are rejected to avoid reference-expansion complexity.
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
        metadata = yaml.load(yaml_text, Loader=_NoAliasSafeLoader)
    except yaml.YAMLError as error:
        raise FrontmatterError(f"invalid YAML frontmatter: {error}") from error

    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise FrontmatterError("frontmatter must contain a YAML mapping")

    body = "".join(lines[closing_index + 1 :])
    return metadata, body
