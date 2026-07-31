"""Command-line interface for extracting Obsidian backlink destinations."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import List, Optional, Sequence

from obsidianlib.wikilinks import (
    Wikilink,
    extract_wikilinks,
    extract_wikilinks_from_file,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="obsidian-backlinks",
        description="Extract Obsidian wikilinks from Markdown files or standard input.",
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        type=Path,
        help="Markdown file to parse; reads standard input when omitted",
    )
    parser.add_argument(
        "--keep-duplicates",
        action="store_true",
        help="retain every wikilink occurrence instead of unique destinations",
    )
    parser.add_argument(
        "--exclude-embeds",
        action="store_true",
        help="ignore embedded wikilinks such as ![[image.png]]",
    )
    return parser


def _records(source: str, links: List[Wikilink]) -> List[dict]:
    return [
        {"source": source, **asdict(link), "destination": link.destination}
        for link in links
    ]


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the ``obsidian-backlinks`` command."""

    args = _build_parser().parse_args(argv)
    options = {
        "include_embeds": not args.exclude_embeds,
        "deduplicate": not args.keep_duplicates,
    }

    records: List[dict] = []
    try:
        if args.files:
            for path in args.files:
                records.extend(
                    _records(
                        str(path),
                        extract_wikilinks_from_file(path, **options),
                    )
                )
        else:
            records.extend(
                _records("-", extract_wikilinks(sys.stdin.read(), **options))
            )
    except (OSError, UnicodeError) as exc:
        print(f"obsidian-backlinks: {exc}", file=sys.stderr)
        return 1

    json.dump(records, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
