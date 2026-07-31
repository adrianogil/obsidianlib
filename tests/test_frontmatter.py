"""Tests for YAML frontmatter parsing."""

from __future__ import annotations

import unittest

import yaml

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

    def test_empty_document_has_no_frontmatter(self) -> None:
        self.assertEqual(parse_frontmatter(""), ({}, ""))

    def test_empty_frontmatter_returns_empty_metadata(self) -> None:
        metadata, body = parse_frontmatter("---\n---\nBody\n")

        self.assertEqual(metadata, {})
        self.assertEqual(body, "Body\n")

    def test_opening_boundary_must_be_the_first_line(self) -> None:
        text = "\n---\ntitle: Not frontmatter\n---\nBody\n"

        metadata, body = parse_frontmatter(text)

        self.assertEqual(metadata, {})
        self.assertEqual(body, text)

    def test_opening_boundary_must_be_exact(self) -> None:
        for boundary in ("--- ", "--- comment"):
            with self.subTest(boundary=boundary):
                text = f"{boundary}\ntitle: Not frontmatter\n---\nBody\n"

                metadata, body = parse_frontmatter(text)

                self.assertEqual(metadata, {})
                self.assertEqual(body, text)

    def test_closing_boundary_must_be_exact(self) -> None:
        for boundary in ("--- ", "--- comment"):
            with self.subTest(boundary=boundary):
                text = f"---\ntitle: Unterminated\n{boundary}\nBody\n"

                with self.assertRaisesRegex(FrontmatterError, "closing"):
                    parse_frontmatter(text)

    def test_rejects_malformed_yaml(self) -> None:
        text = "---\ntags: [obsidian, testing\n---\nBody\n"

        with self.assertRaisesRegex(FrontmatterError, "invalid YAML"):
            parse_frontmatter(text)

    def test_preserves_yaml_error_as_exception_cause(self) -> None:
        text = "---\ntags: [obsidian, testing\n---\nBody\n"

        with self.assertRaises(FrontmatterError) as raised:
            parse_frontmatter(text)

        self.assertIsInstance(raised.exception.__cause__, yaml.YAMLError)

    def test_rejects_missing_closing_boundary(self) -> None:
        text = "---\ntitle: Unterminated\n\nBody\n"

        with self.assertRaisesRegex(FrontmatterError, "closing"):
            parse_frontmatter(text)

    def test_rejects_yaml_that_is_not_a_mapping(self) -> None:
        text = "---\n- first\n- second\n---\nBody\n"

        with self.assertRaisesRegex(FrontmatterError, "mapping"):
            parse_frontmatter(text)

    def test_preserves_indented_boundary_inside_block_scalar(self) -> None:
        metadata, body = parse_frontmatter(
            "---\n"
            "description: |\n"
            "  first line\n"
            "  ---\n"
            "  last line\n"
            "---\n"
            "Body\n"
        )

        self.assertEqual(
            metadata,
            {"description": "first line\n---\nlast line\n"},
        )
        self.assertEqual(body, "Body\n")

    def test_rejects_yaml_aliases(self) -> None:
        text = (
            "---\n"
            "defaults: &defaults\n"
            "  draft: true\n"
            "copy: *defaults\n"
            "---\n"
        )

        with self.assertRaisesRegex(FrontmatterError, "aliases are not allowed"):
            parse_frontmatter(text)

    def test_allows_standard_safe_yaml_tags(self) -> None:
        metadata, body = parse_frontmatter("---\ncount: !!str 123\n---\nBody\n")

        self.assertEqual(metadata, {"count": "123"})
        self.assertEqual(body, "Body\n")

    def test_rejects_custom_yaml_tags(self) -> None:
        text = "---\nvalue: !custom tagged\n---\nBody\n"

        with self.assertRaisesRegex(FrontmatterError, "invalid YAML") as raised:
            parse_frontmatter(text)

        self.assertIsInstance(raised.exception.__cause__, yaml.YAMLError)

    def test_preserves_body_exactly(self) -> None:
        expected_body = "\nFirst line  \r\n--- not a boundary\r\nLast line"
        text = "---\r\ntitle: Exact body\r\n---\r\n" + expected_body

        metadata, body = parse_frontmatter(text)

        self.assertEqual(metadata, {"title": "Exact body"})
        self.assertEqual(body, expected_body)


if __name__ == "__main__":
    unittest.main()
