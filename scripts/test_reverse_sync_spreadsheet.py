#!/usr/bin/env python3
"""Unit tests for reverse_sync_spreadsheet.py."""

import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, call, patch

# Ensure scripts directory is importable
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from reverse_sync_spreadsheet import (
    build_key_dict,
    build_memo_set,
    build_rule_dicts,
    parse_glossary,
    parse_memo,
    parse_people,
    parse_rules,
    parse_table,
    parse_table_row,
    sync_glossary,
    sync_memo,
    sync_people,
    sync_rules,
)


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------


class TestParseTableRow(unittest.TestCase):
    def test_basic_row(self):
        result = parse_table_row("| Ethereum | イーサリアム |")
        self.assertEqual(result, ["Ethereum", "イーサリアム"])

    def test_escaped_pipe(self):
        result = parse_table_row("| A \\| B | C |")
        self.assertEqual(result, ["A | B", "C"])

    def test_empty_cells(self):
        result = parse_table_row("| Infura |  |")
        self.assertEqual(result, ["Infura", ""])


class TestParseGlossary(unittest.TestCase):
    def test_parse_glossary_table(self):
        text = (
            "# 用語集\n\n"
            "> notice\n\n"
            "| English Term | 日本語訳 |\n"
            "|-------------|--------|\n"
            "| Ethereum | イーサリアム |\n"
            "| Ether | Ether |\n"
        )
        entries = parse_glossary(text)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0], {"english": "Ethereum", "japanese": "イーサリアム"})
        self.assertEqual(entries[1], {"english": "Ether", "japanese": "Ether"})

    def test_parse_glossary_escaped_pipes(self):
        text = (
            "| English Term | 日本語訳 |\n"
            "|---|---|\n"
            "| A \\| B | テスト |\n"
        )
        entries = parse_glossary(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["english"], "A | B")

    def test_parse_glossary_empty_japanese(self):
        text = (
            "| English Term | 日本語訳 |\n"
            "|---|---|\n"
            "| Infura |  |\n"
        )
        entries = parse_glossary(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], {"english": "Infura", "japanese": ""})

    def test_parse_glossary_skip_empty_key(self):
        text = (
            "| English Term | 日本語訳 |\n"
            "|---|---|\n"
            "| Ethereum | イーサリアム |\n"
            "|  |  |\n"
        )
        entries = parse_glossary(text)
        self.assertEqual(len(entries), 1)

    def test_parse_glossary_duplicate_key_warning(self):
        text = (
            "| English Term | 日本語訳 |\n"
            "|---|---|\n"
            "| Ethereum | イーサリアム |\n"
            "| Ethereum | 別の訳 |\n"
        )
        stderr = StringIO()
        with patch("sys.stderr", stderr):
            entries = parse_glossary(text)
        self.assertEqual(len(entries), 1)
        self.assertIn("duplicate", stderr.getvalue())


class TestParsePeople(unittest.TestCase):
    def test_parse_people_table(self):
        text = (
            "| Name | カタカナ表記 | カナふり方法 | 参考URL1 | 参考URL2 |\n"
            "|------|-------------|-------------|----------|----------|\n"
            "| Gavin Wood | ギャヴィン・ウッド | 1 | https://example.com |  |\n"
        )
        entries = parse_people(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "Gavin Wood")
        self.assertEqual(entries[0]["katakana"], "ギャヴィン・ウッド")
        self.assertEqual(entries[0]["method"], "1")
        self.assertEqual(entries[0]["url1"], "https://example.com")
        self.assertEqual(entries[0]["url2"], "")

    def test_parse_people_skip_note_rows(self):
        text = (
            "| Name | カタカナ表記 | カナふり方法 | 参考URL1 | 参考URL2 |\n"
            "|---|---|---|---|---|\n"
            "| ※注意事項 | | | | |\n"
            "| Alan Turing | アラン・チューリング | | | |\n"
        )
        entries = parse_people(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "Alan Turing")

    def test_parse_people_short_row(self):
        text = (
            "| Name | カタカナ表記 | カナふり方法 | 参考URL1 | 参考URL2 |\n"
            "|---|---|---|---|---|\n"
            "| Alan Turing | アラン・チューリング |\n"
        )
        entries = parse_people(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["method"], "")
        self.assertEqual(entries[0]["url1"], "")
        self.assertEqual(entries[0]["url2"], "")


class TestParseRules(unittest.TestCase):
    def test_parse_rules_numbered(self):
        text = (
            "## JTF日本語標準ガイドに基づくルール\n\n"
            "参照: https://example.com\n\n"
            "1. ルール1テキスト\n"
            "2. ルール2テキスト\n\n"
            "## 翻訳中メモ\n"
        )
        rules = parse_rules(text)
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0], {"number": "1", "text": "ルール1テキスト", "continuations": []})
        self.assertEqual(rules[1], {"number": "2", "text": "ルール2テキスト", "continuations": []})

    def test_parse_rules_continuation(self):
        text = (
            "## JTF日本語標準ガイドに基づくルール\n\n"
            "1. ルール1テキスト\n"
            "   継続行テキスト\n"
            "2. ルール2テキスト\n\n"
            "## 翻訳中メモ\n"
        )
        rules = parse_rules(text)
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0]["continuations"], ["継続行テキスト"])

    def test_parse_rules_no_memo_section(self):
        text = (
            "## JTF日本語標準ガイドに基づくルール\n\n"
            "1. ルール1テキスト\n"
        )
        rules = parse_rules(text)
        self.assertEqual(len(rules), 1)


class TestParseMemo(unittest.TestCase):
    def test_parse_memo_section(self):
        text = (
            "## JTF rules\n\n"
            "1. Rule\n\n"
            "## 翻訳中メモ\n\n"
            "- メモ1\n"
            "- メモ2\n"
        )
        memos = parse_memo(text)
        self.assertEqual(memos, ["メモ1", "メモ2"])

    def test_parse_memo_empty(self):
        text = "## 翻訳中メモ\n\n"
        memos = parse_memo(text)
        self.assertEqual(memos, [])


# ---------------------------------------------------------------------------
# Diff tests
# ---------------------------------------------------------------------------


class TestDiffGlossary(unittest.TestCase):
    def test_diff_new_entries(self):
        md = [
            {"english": "A", "japanese": "ア"},
            {"english": "B", "japanese": "ビー"},
            {"english": "C", "japanese": "シー"},
        ]
        sheet = [["en", "ja"], ["A", "ア"], ["B", "ビー"]]
        service = MagicMock()
        new, updated = sync_glossary(service, md, sheet, dry_run=True)
        self.assertEqual(new, 1)
        self.assertEqual(updated, 0)

    def test_diff_changed_entries(self):
        md = [{"english": "A", "japanese": "新しい訳"}]
        sheet = [["en", "ja"], ["A", "古い訳"]]
        service = MagicMock()
        new, updated = sync_glossary(service, md, sheet, dry_run=True)
        self.assertEqual(new, 0)
        self.assertEqual(updated, 1)

    def test_diff_unchanged(self):
        md = [{"english": "A", "japanese": "ア"}]
        sheet = [["en", "ja"], ["A", "ア"]]
        service = MagicMock()
        new, updated = sync_glossary(service, md, sheet, dry_run=True)
        self.assertEqual(new, 0)
        self.assertEqual(updated, 0)

    def test_diff_spreadsheet_only(self):
        md = [{"english": "A", "japanese": "ア"}]
        sheet = [["en", "ja"], ["A", "ア"], ["B", "ビー"], ["C", "シー"]]
        service = MagicMock()
        new, updated = sync_glossary(service, md, sheet, dry_run=True)
        self.assertEqual(new, 0)
        self.assertEqual(updated, 0)

    def test_diff_duplicate_key_warning(self):
        sheet = [["en", "ja"], ["A", "ア"], ["A", "別"]]
        key_dict = build_key_dict(sheet, 0, "test")
        self.assertEqual(len(key_dict), 1)
        self.assertEqual(key_dict["A"][0], 2)


class TestDiffPeople(unittest.TestCase):
    def test_diff_people_empty_cols_preserved(self):
        md = [
            {
                "name": "Test Person",
                "katakana": "テスト",
                "method": "",
                "url1": "",
                "url2": "",
            }
        ]
        sheet = [
            ["Name", "カタカナ", "method", "url1", "url2"],
            ["Test Person", "テスト", "2", "https://example.com", ""],
        ]
        service = MagicMock()
        new, updated = sync_people(service, md, sheet, dry_run=True)
        # method and url1 should be preserved from sheet, so no change
        self.assertEqual(new, 0)
        self.assertEqual(updated, 0)


# ---------------------------------------------------------------------------
# API call tests (mocked)
# ---------------------------------------------------------------------------


class TestAPICallsGlossary(unittest.TestCase):
    def test_append_new_glossary_entries(self):
        md = [{"english": "NewTerm", "japanese": "新用語"}]
        sheet = [["en", "ja"]]
        service = MagicMock()
        sync_glossary(service, md, sheet, dry_run=False)
        service.spreadsheets().values().append.assert_called_once()
        append_call = service.spreadsheets().values().append.call_args
        self.assertIn("用語集 のコピー", append_call.kwargs["range"])
        self.assertEqual(
            append_call.kwargs["body"]["values"], [["NewTerm", "新用語"]]
        )

    def test_update_changed_glossary_entries(self):
        md = [{"english": "A", "japanese": "新訳"}]
        sheet = [["en", "ja"], ["A", "旧訳"]]
        service = MagicMock()
        sync_glossary(service, md, sheet, dry_run=False)
        service.spreadsheets().values().update.assert_called_once()
        update_call = service.spreadsheets().values().update.call_args
        self.assertIn("A2", update_call.kwargs["range"])


class TestAPICallsPeople(unittest.TestCase):
    def test_update_changed_people_entries(self):
        md = [
            {
                "name": "Gavin Wood",
                "katakana": "ギャヴィン・ウッド",
                "method": "1",
                "url1": "https://new.com",
                "url2": "",
            }
        ]
        sheet = [
            ["Name", "カタカナ", "method", "url1", "url2"],
            ["Gavin Wood", "ギャビン・ウッド", "1", "https://old.com", ""],
        ]
        service = MagicMock()
        sync_people(service, md, sheet, dry_run=False)
        service.spreadsheets().values().update.assert_called_once()
        update_call = service.spreadsheets().values().update.call_args
        self.assertIn("A2", update_call.kwargs["range"])


class TestAPICallsRules(unittest.TestCase):
    def test_update_rule_text(self):
        md_rules = [
            {"number": "1", "text": "新しいルール文", "continuations": []}
        ]
        sheet = [["1", "古いルール文"]]
        service = MagicMock()
        sync_rules(service, md_rules, sheet, dry_run=False)
        service.spreadsheets().values().update.assert_called_once()
        update_call = service.spreadsheets().values().update.call_args
        self.assertIn("翻訳ルール のコピー", update_call.kwargs["range"])
        self.assertEqual(
            update_call.kwargs["body"]["values"], [["1", "新しいルール文"]]
        )


class TestDryRun(unittest.TestCase):
    def test_dry_run_no_writes(self):
        md = [{"english": "NewTerm", "japanese": "新用語"}]
        sheet = [["en", "ja"]]
        service = MagicMock()
        sync_glossary(service, md, sheet, dry_run=True)
        service.spreadsheets().values().append.assert_not_called()
        service.spreadsheets().values().update.assert_not_called()


class TestMissingEnvVar(unittest.TestCase):
    def test_missing_env_var(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                from reverse_sync_spreadsheet import build_service

                build_service()
            self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
