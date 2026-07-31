"""Normalize Obsidian note titles from filenames and frontmatter."""

from __future__ import annotations

from os import PathLike, fspath
from pathlib import Path
import re
import unicodedata
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from obsidianlib.frontmatter import parse_frontmatter


Filename = Union[str, PathLike[str]]

_DASHES = str.maketrans(
    {
        "\u058a": "-",
        "\u05be": "-",
        "\u1400": "-",
        "\u1806": "-",
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2015": "-",
        "\u2e17": "-",
        "\u2e1a": "-",
        "\u2e3a": "-",
        "\u2e3b": "-",
        "\u2e40": "-",
        "\u2e5d": "-",
        "\u301c": "-",
        "\u3030": "-",
        "\u30a0": "-",
        "\ufe31": "-",
        "\ufe32": "-",
        "\ufe58": "-",
        "\ufe63": "-",
        "\uff0d": "-",
    }
)
_QUOTES = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u2032": "'",
        "\u2035": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
        "\u2033": '"',
        "\u2036": '"',
    }
)


def _collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def filename_to_title(filename: Filename) -> str:
    """Return a display title from the basename of a Markdown filename.

    Only a final, case-insensitive ``.md`` suffix is removed. Meaningful case
    and punctuation are preserved, Unicode is normalized to NFC, and runs of
    whitespace are collapsed.
    """

    basename = Path(fspath(filename)).name
    if basename.lower().endswith(".md") and len(basename) > 3:
        basename = basename[:-3]
    return _collapse_whitespace(unicodedata.normalize("NFC", basename))


def normalize_note_title(title: str) -> str:
    """Return a stable comparison key for a note title or alias.

    The key uses Unicode compatibility normalization and case folding, maps
    typographic dash and quote variants to their ASCII equivalents, and
    collapses whitespace. Other punctuation is deliberately retained so that
    distinct titles such as ``C++`` and ``C#`` do not collide.
    """

    if not isinstance(title, str):
        raise TypeError("note title must be a string")

    normalized = unicodedata.normalize("NFKC", title)
    normalized = normalized.translate(_DASHES).translate(_QUOTES)
    return _collapse_whitespace(normalized).casefold()


def _frontmatter_values(metadata: Dict[str, Any]) -> Iterable[Any]:
    title = metadata.get("title")
    if title is not None:
        yield title

    for key in ("alias", "aliases"):
        value = metadata.get(key)
        if isinstance(value, (list, tuple)):
            yield from value
        elif value is not None:
            yield value


def note_title_keys(
    filename: Filename,
    metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[str, ...]:
    """Return deduplicated comparison keys for a note and its aliases.

    The filename-derived title is always first. A frontmatter ``title`` and
    either the singular ``alias`` or plural ``aliases`` form follow in source
    order. Empty values and structured alias values are ignored.
    """

    candidates = [filename_to_title(filename)]
    if metadata:
        candidates.extend(_frontmatter_values(metadata))

    keys = []
    seen = set()
    for candidate in candidates:
        if not isinstance(candidate, (str, int, float)):
            continue
        key = normalize_note_title(str(candidate))
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return tuple(keys)


def note_title_keys_from_markdown(
    filename: Filename,
    markdown: str,
) -> Tuple[str, ...]:
    """Parse Markdown frontmatter and return all normalized note-title keys."""

    metadata, _ = parse_frontmatter(markdown)
    return note_title_keys(filename, metadata)
