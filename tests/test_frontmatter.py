"""Tests for YAML frontmatter parsing."""

from __future__ import annotations

import unittest

from obsidianlib import FrontmatterError, parse_frontmatter


class ParseFrontmatterTests(unittest.TestCase):
    def test_parses_valid_yaml_frontmatter(self) -> None:
        metadata, body = parse_frontmatter(
            "---\n"
            "title: Parser tests\n"
            "draft: false\n"
            "tags:\n"
            "  - obsidian\n"
            "  - testing\n"
            "---\n"
            "# Parser tests\n"
        )

        self.assertEqual(
            metadata,
            {
                "title": "Parser tests",
                "draft": False,
                "tags": ["obsidian", "testing"],
            },
        )
        self.assertEqual(body, "# Parser tests\n")

    def test_returns_original_text_when_frontmatter_is_missing(self) -> None:
        text = "# Plain note\n\nNo metadata here.\n"

        metadata, body = parse_frontmatter(text)

        self.assertEqual(metadata, {})
        self.assertEqual(body, text)

    def test_rejects_malformed_yaml(self) -> None:
        text = "---\ntags: [obsidian, testing\n---\nBody\n"

        with self.assertRaisesRegex(FrontmatterError, "invalid YAML"):
            parse_frontmatter(text)

    def test_rejects_missing_closing_boundary(self) -> None:
        text = "---\ntitle: Unterminated\n\nBody\n"

        with self.assertRaisesRegex(FrontmatterError, "closing"):
            parse_frontmatter(text)

    def test_rejects_yaml_that_is_not_a_mapping(self) -> None:
        text = "---\n- first\n- second\n---\nBody\n"

        with self.assertRaisesRegex(FrontmatterError, "mapping"):
            parse_frontmatter(text)

    def test_preserves_body_exactly(self) -> None:
        expected_body = "\nFirst line  \r\n--- not a boundary\r\nLast line"
        text = "---\r\ntitle: Exact body\r\n---\r\n" + expected_body

        metadata, body = parse_frontmatter(text)

        self.assertEqual(metadata, {"title": "Exact body"})
        self.assertEqual(body, expected_body)


if __name__ == "__main__":
    unittest.main()
