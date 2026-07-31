"""Extract Obsidian wikilinks from Markdown text and files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Optional, Set, Tuple, Union


_WIKILINK_PATTERN = re.compile(
    r"(?<![\\!])(?P<embedded>!)?\[\[(?P<body>[^\]\r\n]+)\]\]"
)


@dataclass(frozen=True)
class Wikilink:
    """A parsed Obsidian wikilink."""

    target: str
    heading: Optional[str] = None
    alias: Optional[str] = None
    embedded: bool = False
    raw: str = ""

    @property
    def destination(self) -> str:
        """Return the target and optional heading without the display alias."""

        if self.heading is None:
            return self.target
        return f"{self.target}#{self.heading}"


def _parse_match(match: re.Match[str]) -> Optional[Wikilink]:
    body = match.group("body")
    destination, alias_separator, alias_text = body.partition("|")
    destination = destination.strip()

    target, heading_separator, heading_text = destination.partition("#")
    target = target.strip()
    heading = heading_text.strip() if heading_separator else None
    if heading == "":
        heading = None

    if not target and heading is None:
        return None

    alias = alias_text.strip() if alias_separator else None
    if alias == "":
        alias = None

    return Wikilink(
        target=target,
        heading=heading,
        alias=alias,
        embedded=match.group("embedded") is not None,
        raw=match.group(0),
    )


def extract_wikilinks(
    markdown: str,
    *,
    include_embeds: bool = True,
    deduplicate: bool = True,
) -> List[Wikilink]:
    """Extract wikilinks in order of appearance.

    Deduplication uses the destination (target plus heading), so aliases and
    embed markers do not create duplicate backlink destinations. Escaped links
    such as ``\\[[Page]]`` are ignored.
    """

    links: List[Wikilink] = []
    seen: Set[Tuple[str, Optional[str]]] = set()

    for match in _WIKILINK_PATTERN.finditer(markdown):
        link = _parse_match(match)
        if link is None or (link.embedded and not include_embeds):
            continue

        key = (link.target, link.heading)
        if deduplicate and key in seen:
            continue

        links.append(link)
        seen.add(key)

    return links


def extract_wikilinks_from_file(
    path: Union[str, Path],
    *,
    encoding: str = "utf-8",
    include_embeds: bool = True,
    deduplicate: bool = True,
) -> List[Wikilink]:
    """Read a Markdown file and extract its wikilinks."""

    markdown = Path(path).read_text(encoding=encoding)
    return extract_wikilinks(
        markdown,
        include_embeds=include_embeds,
        deduplicate=deduplicate,
    )


def extract_backlinks(
    markdown: str,
    *,
    include_embeds: bool = True,
    deduplicate: bool = True,
) -> List[Wikilink]:
    """Alias for :func:`extract_wikilinks` in backlink-indexing workflows."""

    return extract_wikilinks(
        markdown,
        include_embeds=include_embeds,
        deduplicate=deduplicate,
    )


def extract_backlinks_from_file(
    path: Union[str, Path],
    *,
    encoding: str = "utf-8",
    include_embeds: bool = True,
    deduplicate: bool = True,
) -> List[Wikilink]:
    """Alias for :func:`extract_wikilinks_from_file`."""

    return extract_wikilinks_from_file(
        path,
        encoding=encoding,
        include_embeds=include_embeds,
        deduplicate=deduplicate,
    )


__all__ = [
    "Wikilink",
    "extract_backlinks",
    "extract_backlinks_from_file",
    "extract_wikilinks",
    "extract_wikilinks_from_file",
]
