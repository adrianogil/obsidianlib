"""Library for parsing and analyzing Obsidian markdown notes."""

from obsidianlib.frontmatter import FrontmatterError, parse_frontmatter
from obsidianlib.version import __version__

__all__ = ["FrontmatterError", "__version__", "parse_frontmatter"]
