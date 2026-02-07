#!/usr/bin/env python3
"""Sync translation reference files from Google Spreadsheet to markdown."""

import csv
import io
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SHEET_ID = "19Dh5V0LsO23DPH6uwqIRPz7koQwNfN_TuJjUvPVSZDo"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq"

REPO_ROOT = Path(__file__).resolve().parent.parent

SHEETS = {
    "people": "人名一覧",
    "glossary": "用語集 のコピー",
    "rules": "翻訳ルール のコピー",
    "memo": "翻訳中メモ のコピー",
}

AUTO_GENERATED_NOTICE = (
    "> このファイルは Google Spreadsheet から自動生成されています。\n"
    "> 手動で編集した内容は次回の同期時に上書きされます。\n"
    f"> ソース: https://docs.google.com/spreadsheets/d/{SHEET_ID}/\n"
)


def fetch_csv(sheet_name: str) -> str:
    encoded = urllib.parse.quote(sheet_name)
    url = f"{BASE_URL}?tqx=out:csv&sheet={encoded}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"Error fetching sheet '{sheet_name}': {e}", file=sys.stderr)
        sys.exit(1)

    if data.strip().startswith("<"):
        print(
            f"Error: received HTML instead of CSV for sheet '{sheet_name}'. "
            "The sheet name may have changed.",
            file=sys.stderr,
        )
        sys.exit(1)

    return data


def escape_pipe(text: str) -> str:
    return text.replace("|", "\\|")


def generate_people_md(csv_text: str) -> str:
    reader = csv.reader(io.StringIO(csv_text))
    next(reader)  # skip header row

    rows = []
    for row in reader:
        if not row or not row[0].strip():
            continue
        if row[0].strip().startswith("※"):
            continue
        name = escape_pipe(row[0].strip()) if len(row) > 0 else ""
        katakana = escape_pipe(row[1].strip()) if len(row) > 1 else ""
        method = escape_pipe(row[2].strip()) if len(row) > 2 else ""
        url1 = escape_pipe(row[3].strip()) if len(row) > 3 else ""
        url2 = escape_pipe(row[4].strip()) if len(row) > 4 else ""
        rows.append(f"| {name} | {katakana} | {method} | {url1} | {url2} |")

    if not rows:
        print("Error: people sheet has no data rows", file=sys.stderr)
        sys.exit(1)

    lines = [
        "# 人名一覧\n",
        "\n",
        AUTO_GENERATED_NOTICE,
        "\n",
        "| Name | カタカナ表記 | カナふり方法 | 参考URL1 | 参考URL2 |\n",
        "|------|-------------|-------------|----------|----------|\n",
    ]
    for r in rows:
        lines.append(r + "\n")

    return "".join(lines)


def generate_glossary_md(csv_text: str) -> str:
    reader = csv.reader(io.StringIO(csv_text))
    next(reader)  # skip header row

    rows = []
    for row in reader:
        if not row or not row[0].strip():
            continue
        en = escape_pipe(row[0].strip())
        ja = escape_pipe(row[1].strip()) if len(row) > 1 else ""
        rows.append(f"| {en} | {ja} |")

    if not rows:
        print("Error: glossary sheet has no data rows", file=sys.stderr)
        sys.exit(1)

    lines = [
        "# 用語集\n",
        "\n",
        AUTO_GENERATED_NOTICE,
        "\n",
        "| English Term | 日本語訳 |\n",
        "|-------------|--------|\n",
    ]
    for r in rows:
        lines.append(r + "\n")

    return "".join(lines)


def generate_rules_md(rules_csv: str, memo_csv: str) -> str:
    lines = [
        "# 翻訳ルール\n",
        "\n",
        AUTO_GENERATED_NOTICE,
        "\n",
        "## JTF日本語標準ガイドに基づくルール\n",
        "\n",
    ]

    # Parse rules sheet
    reader = csv.reader(io.StringIO(rules_csv))
    all_rows = list(reader)

    # Extract JTF URL from the title row (first row containing a URL)
    data_start = 0
    for i, row in enumerate(all_rows):
        if row and row[0] and "https://" in row[0]:
            title_text = row[0].strip()
            url_start = title_text.index("https://")
            url = title_text[url_start:].strip()
            lines.append(f"参照: {url}\n")
            lines.append("\n")
            data_start = i + 1
            break

    for row in all_rows[data_start:]:
        if not row:
            continue
        col0 = row[0].strip() if len(row) > 0 else ""
        col1 = row[1].strip() if len(row) > 1 else ""

        if not col0 and not col1:
            continue

        if col0 and col0.isdigit():
            lines.append(f"{col0}. {col1}\n")
        elif not col0 and col1:
            lines.append(f"   {col1}\n")

    # Add memo section
    lines.append("\n")
    lines.append("## 翻訳中メモ\n")
    lines.append("\n")

    reader = csv.reader(io.StringIO(memo_csv))
    for row in reader:
        if not row:
            continue
        text = row[0].strip() if row[0] else ""
        if text:
            lines.append(f"- {text}\n")

    return "".join(lines)


def write_if_changed(filepath: Path, content: str) -> bool:
    if filepath.exists() and filepath.read_text(encoding="utf-8") == content:
        return False
    filepath.write_text(content, encoding="utf-8")
    return True


def main():
    print("Fetching spreadsheet data...")

    people_csv = fetch_csv(SHEETS["people"])
    glossary_csv = fetch_csv(SHEETS["glossary"])
    rules_csv = fetch_csv(SHEETS["rules"])
    memo_csv = fetch_csv(SHEETS["memo"])

    people_md = generate_people_md(people_csv)
    glossary_md = generate_glossary_md(glossary_csv)
    rules_md = generate_rules_md(rules_csv, memo_csv)

    updated = 0

    if write_if_changed(REPO_ROOT / "people.md", people_md):
        print("Updated: people.md")
        updated += 1

    if write_if_changed(REPO_ROOT / "glosary.md", glossary_md):
        print("Updated: glosary.md")
        updated += 1

    if write_if_changed(REPO_ROOT / "translation-rule.md", rules_md):
        print("Updated: translation-rule.md")
        updated += 1

    if updated == 0:
        print("No changes detected")
    else:
        print(f"Sync complete: {updated} file(s) updated")


if __name__ == "__main__":
    main()
