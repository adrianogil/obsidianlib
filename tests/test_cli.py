"""Tests for the backlink extraction CLI."""

from __future__ import annotations

import io
import json
from unittest import mock
import unittest

from obsidianlib.cli import main


class CliTests(unittest.TestCase):
    def test_reads_stdin_and_outputs_json(self) -> None:
        stdout = io.StringIO()
        with (
            mock.patch("sys.stdin", io.StringIO("[[Page|Alias]] ![[image.png]]")),
            mock.patch("sys.stdout", stdout),
        ):
            result = main([])

        self.assertEqual(result, 0)
        records = json.loads(stdout.getvalue())
        self.assertEqual(
            [(record["destination"], record["embedded"]) for record in records],
            [("Page", False), ("image.png", True)],
        )
        self.assertTrue(all(record["source"] == "-" for record in records))


if __name__ == "__main__":
    unittest.main()
