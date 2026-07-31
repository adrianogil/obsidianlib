"""Library for parsing and analyzing Obsidian markdown notes."""

from obsidianlib.frontmatter import FrontmatterError, parse_frontmatter
from obsidianlib.titles import (
    filename_to_title,
    normalize_note_title,
    note_title_keys,
    note_title_keys_from_markdown,
)
from obsidianlib.version import __version__
from obsidianlib.wikilinks import (
    Wikilink,
    extract_backlinks,
    extract_backlinks_from_file,
    extract_wikilinks,
    extract_wikilinks_from_file,
)

__all__ = [
    "FrontmatterError",
    "Wikilink",
    "__version__",
    "extract_backlinks",
    "extract_backlinks_from_file",
    "extract_wikilinks",
    "extract_wikilinks_from_file",
    "filename_to_title",
    "normalize_note_title",
    "note_title_keys",
    "note_title_keys_from_markdown",
    "parse_frontmatter",
]
