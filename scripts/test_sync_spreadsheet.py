#!/usr/bin/env python3
"""Verify structure of generated translation reference files."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestGlosary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = REPO_ROOT / "glosary.md"
        if not path.exists():
            raise unittest.SkipTest("glosary.md does not exist. Run sync_spreadsheet.py first.")
        cls.content = path.read_text(encoding="utf-8")
        cls.lines = cls.content.splitlines()

    def test_glosary_header(self):
        header_found = any("| English Term | 日本語訳 |" in line for line in self.lines)
        self.assertTrue(header_found, "glosary.md must contain '| English Term | 日本語訳 |' header")

    def test_glosary_has_data(self):
        data_lines = [
            line
            for line in self.lines
            if line.startswith("|") and "English Term" not in line and "---" not in line
        ]
        self.assertGreater(len(data_lines), 0, "glosary.md must have at least 1 data row")

    def test_glosary_sample(self):
        self.assertIn("Ethereum", self.content, "glosary.md must contain 'Ethereum'")
        self.assertIn("イーサリアム", self.content, "glosary.md must contain 'イーサリアム'")


class TestPeople(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = REPO_ROOT / "people.md"
        if not path.exists():
            raise unittest.SkipTest("people.md does not exist. Run sync_spreadsheet.py first.")
        cls.content = path.read_text(encoding="utf-8")
        cls.lines = cls.content.splitlines()

    def test_people_header(self):
        header_found = any("| Name |" in line and "カタカナ表記" in line for line in self.lines)
        self.assertTrue(header_found, "people.md must contain header with '| Name |' and 'カタカナ表記'")

    def test_people_has_data(self):
        data_lines = [
            line
            for line in self.lines
            if line.startswith("|") and "Name" not in line and "---" not in line
        ]
        self.assertGreater(len(data_lines), 0, "people.md must have at least 1 data row")

    def test_people_sample(self):
        self.assertIn("Vitalik Buterin", self.content, "people.md must contain 'Vitalik Buterin'")
        self.assertIn("ヴィタリック・ブテリン", self.content, "people.md must contain 'ヴィタリック・ブテリン'")


class TestTranslationRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = REPO_ROOT / "translation-rule.md"
        if not path.exists():
            raise unittest.SkipTest("translation-rule.md does not exist. Run sync_spreadsheet.py first.")
        cls.content = path.read_text(encoding="utf-8")
        cls.lines = cls.content.splitlines()

    def test_rules_sections(self):
        self.assertIn(
            "## JTF日本語標準ガイドに基づくルール",
            self.content,
            "Must contain JTF rules section heading",
        )
        self.assertIn("## 翻訳中メモ", self.content, "Must contain memo section heading")

    def test_rules_numbered(self):
        numbered = any(re.match(r"^1\.\s", line) for line in self.lines)
        self.assertTrue(numbered, "Must contain a rule starting with '1.'")


class TestTableIntegrity(unittest.TestCase):
    def _check_unescaped_pipes(self, filepath: Path):
        if not filepath.exists():
            self.skipTest(f"{filepath.name} does not exist")
        content = filepath.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            if not line.startswith("|"):
                continue
            if line.startswith("|---"):
                continue
            # Remove leading/trailing pipe, then check inner content
            inner = line.strip("|")
            cells = inner.split("|")
            for cell in cells:
                # Check for pipe that is not escaped (not preceded by \)
                unescaped = re.findall(r"(?<!\\)\|", cell)
                self.assertEqual(
                    len(unescaped),
                    0,
                    f"Unescaped '|' found in {filepath.name} line {i}: {line}",
                )

    def test_no_pipe_in_glosary(self):
        self._check_unescaped_pipes(REPO_ROOT / "glosary.md")

    def test_no_pipe_in_people(self):
        self._check_unescaped_pipes(REPO_ROOT / "people.md")


if __name__ == "__main__":
    unittest.main()
