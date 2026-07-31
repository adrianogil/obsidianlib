"""Tests for Obsidian note-title normalization."""

from __future__ import annotations

from pathlib import Path
import unittest

from obsidianlib import (
    filename_to_title,
    normalize_note_title,
    note_title_keys,
    note_title_keys_from_markdown,
)


class FilenameToTitleTests(unittest.TestCase):
    def test_converts_markdown_filename_to_display_title(self) -> None:
        self.assertEqual(
            filename_to_title(Path("/vault/Project   notes.MD")),
            "Project notes",
        )

    def test_preserves_punctuation_case_and_unicode(self) -> None:
        self.assertEqual(
            filename_to_title("recipes/Crème brûlée — chef's choice!.md"),
            "Crème brûlée — chef's choice!",
        )

    def test_normalizes_decomposed_unicode(self) -> None:
        self.assertEqual(filename_to_title("Cafe\u0301.md"), "Café")


class NormalizeNoteTitleTests(unittest.TestCase):
    def test_normalizes_case_whitespace_and_compatibility_characters(self) -> None:
        self.assertEqual(
            normalize_note_title("  Ｃａｆé\u00a0  NOTES  "),
            "café notes",
        )

    def test_canonicalizes_typographic_dashes_and_quotes(self) -> None:
        self.assertEqual(
            normalize_note_title("Author’s Notes—2026"),
            normalize_note_title("AUTHOR'S NOTES-2026"),
        )

    def test_retains_meaningful_punctuation(self) -> None:
        self.assertNotEqual(
            normalize_note_title("C++"),
            normalize_note_title("C#"),
        )

    def test_is_idempotent(self) -> None:
        title = "  Résumé’s\tDraft—２  "
        once = normalize_note_title(title)

        self.assertEqual(normalize_note_title(once), once)

    def test_rejects_non_string_values(self) -> None:
        with self.assertRaisesRegex(TypeError, "must be a string"):
            normalize_note_title(123)  # type: ignore[arg-type]


class NoteTitleKeysTests(unittest.TestCase):
    def test_combines_filename_title_and_existing_aliases(self) -> None:
        keys = note_title_keys(
            "Project Notes.md",
            {
                "title": "Project notes",
                "alias": "PN",
                "aliases": ["Notes—Project", "Projeto Notas", "PN"],
            },
        )

        self.assertEqual(
            keys,
            ("project notes", "pn", "notes-project", "projeto notas"),
        )

    def test_accepts_scalar_aliases_and_numeric_titles(self) -> None:
        self.assertEqual(
            note_title_keys("Nineteen Eighty-Four.md", {"aliases": 1984}),
            ("nineteen eighty-four", "1984"),
        )

    def test_ignores_empty_and_structured_alias_values(self) -> None:
        self.assertEqual(
            note_title_keys(
                "Title.md",
                {"aliases": [None, "  ", {"name": "not a title"}]},
            ),
            ("title",),
        )

    def test_missing_frontmatter_falls_back_to_filename(self) -> None:
        markdown = "# Plain note\n\nNo metadata here.\n"

        self.assertEqual(
            note_title_keys_from_markdown("Plain Note.md", markdown),
            ("plain note",),
        )

    def test_parses_aliases_from_frontmatter(self) -> None:
        markdown = (
            "---\n"
            "aliases:\n"
            "  - Résumé\n"
            "  - CV\n"
            "---\n"
            "# Curriculum vitae\n"
        )

        self.assertEqual(
            note_title_keys_from_markdown("Curriculum Vitae.md", markdown),
            ("curriculum vitae", "résumé", "cv"),
        )

    def test_note_keys_are_idempotent(self) -> None:
        keys = note_title_keys("Résumé—2026.md", {"aliases": ["CV", "cv"]})

        self.assertEqual(
            tuple(normalize_note_title(key) for key in keys),
            keys,
        )


if __name__ == "__main__":
    unittest.main()
