"""Library for parsing and analyzing Obsidian markdown notes."""

from obsidianlib.frontmatter import FrontmatterError, parse_frontmatter
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
    "parse_frontmatter",
]
