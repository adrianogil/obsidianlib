"""Tests for Obsidian wikilink extraction."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from obsidianlib import (
    Wikilink,
    extract_backlinks,
    extract_wikilinks,
    extract_wikilinks_from_file,
)


class ExtractWikilinksTests(unittest.TestCase):
    def test_parses_common_wikilink_forms(self) -> None:
        markdown = (
            "See [[Page]], [[Page#Heading]], [[Page|Alias]], "
            "![[File.png]], and [[#Local heading]]."
        )

        links = extract_wikilinks(markdown, deduplicate=False)

        self.assertEqual(
            links,
            [
                Wikilink(target="Page", raw="[[Page]]"),
                Wikilink(
                    target="Page",
                    heading="Heading",
                    raw="[[Page#Heading]]",
                ),
                Wikilink(target="Page", alias="Alias", raw="[[Page|Alias]]"),
                Wikilink(
                    target="File.png",
                    embedded=True,
                    raw="![[File.png]]",
                ),
                Wikilink(
                    target="",
                    heading="Local heading",
                    raw="[[#Local heading]]",
                ),
            ],
        )
        self.assertEqual(
            [link.destination for link in links],
            ["Page", "Page#Heading", "Page", "File.png", "#Local heading"],
        )

    def test_deduplicates_by_destination_and_keeps_first_occurrence(self) -> None:
        markdown = (
            "[[Page|First alias]] [[Page]] ![[Page]] "
            "[[Page#Heading]] [[Page#Heading|Second alias]]"
        )

        links = extract_wikilinks(markdown)

        self.assertEqual(
            links,
            [
                Wikilink(
                    target="Page",
                    alias="First alias",
                    raw="[[Page|First alias]]",
                ),
                Wikilink(
                    target="Page",
                    heading="Heading",
                    raw="[[Page#Heading]]",
                ),
            ],
        )

    def test_can_retain_duplicates_and_exclude_embeds(self) -> None:
        markdown = "[[Page]] [[Page|Alias]] ![[image.png]]"

        links = extract_wikilinks(
            markdown,
            deduplicate=False,
            include_embeds=False,
        )

        self.assertEqual([link.raw for link in links], ["[[Page]]", "[[Page|Alias]]"])

    def test_ignores_escaped_and_empty_wikilinks(self) -> None:
        links = extract_wikilinks(r"\[[Escaped]] [[ ]] \![[Also escaped]] [[Valid]]")

        self.assertEqual(links, [Wikilink(target="Valid", raw="[[Valid]]")])

    def test_extracts_from_utf8_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            note = Path(directory) / "note.md"
            note.write_text("[[Página|apelido]]", encoding="utf-8")

            links = extract_wikilinks_from_file(note)

        self.assertEqual(
            links,
            [Wikilink(target="Página", alias="apelido", raw="[[Página|apelido]]")],
        )

    def test_backlink_api_is_equivalent(self) -> None:
        markdown = "[[One]] [[One|alias]] [[Two]]"

        self.assertEqual(extract_backlinks(markdown), extract_wikilinks(markdown))


if __name__ == "__main__":
    unittest.main()
