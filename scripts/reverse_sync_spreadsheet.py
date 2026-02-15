#!/usr/bin/env python3
"""Reverse sync: push markdown changes back to Google Spreadsheet."""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SHEET_ID = "19Dh5V0LsO23DPH6uwqIRPz7koQwNfN_TuJjUvPVSZDo"

REPO_ROOT = Path(__file__).resolve().parent.parent

SHEETS = {
    "people": "人名一覧",
    "glossary": "用語集 のコピー",
    "rules": "翻訳ルール のコピー",
    "memo": "翻訳中メモ のコピー",
}


# ---------------------------------------------------------------------------
# Markdown Parsers
# ---------------------------------------------------------------------------

def parse_table_row(line: str) -> list[str]:
    """Parse a markdown table row, handling escaped pipes."""
    placeholder = "\x00PIPE\x00"
    line = line.replace("\\|", placeholder)
    cells = line.split("|")
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    cells = [c.replace(placeholder, "|").strip() for c in cells]
    return cells


def parse_table(
    text: str, header_keywords: list[str], num_cols: int
) -> list[list[str]]:
    """Parse a markdown table into a list of data rows."""
    lines = text.split("\n")
    found_header = False
    skip_separator = False
    results: list[list[str]] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if not found_header:
            if all(kw in line for kw in header_keywords):
                found_header = True
                skip_separator = True
            continue

        if skip_separator:
            if "---" in stripped:
                skip_separator = False
                continue
            skip_separator = False

        if not stripped.startswith("|"):
            continue

        cells = parse_table_row(stripped)
        while len(cells) < num_cols:
            cells.append("")
        results.append(cells)

    return results


def parse_glossary(text: str) -> list[dict]:
    """Parse glosary.md into a list of glossary entries."""
    rows = parse_table(text, ["English Term", "日本語訳"], 2)
    entries: list[dict] = []
    seen: set[str] = set()
    for cells in rows:
        key = cells[0]
        if not key:
            continue
        if key in seen:
            print(
                f"Warning: duplicate key '{key}' in glosary.md, "
                "using first occurrence",
                file=sys.stderr,
            )
            continue
        seen.add(key)
        entries.append({"english": key, "japanese": cells[1]})
    return entries


def parse_people(text: str) -> list[dict]:
    """Parse people.md into a list of people entries."""
    rows = parse_table(text, ["Name", "カタカナ表記"], 5)
    entries: list[dict] = []
    seen: set[str] = set()
    for cells in rows:
        key = cells[0]
        if not key or key.startswith("※"):
            continue
        if key in seen:
            print(
                f"Warning: duplicate key '{key}' in people.md, "
                "using first occurrence",
                file=sys.stderr,
            )
            continue
        seen.add(key)
        entries.append(
            {
                "name": key,
                "katakana": cells[1],
                "method": cells[2],
                "url1": cells[3],
                "url2": cells[4],
            }
        )
    return entries


def parse_rules(text: str) -> list[dict]:
    """Parse translation-rule.md rules section."""
    lines = text.split("\n")
    in_rules = False
    rules: list[dict] = []
    current_rule: dict | None = None
    rule_re = re.compile(r"^(\d+)\.\s+(.+)$")

    for line in lines:
        stripped = line.rstrip()

        if "## JTF" in stripped:
            in_rules = True
            continue

        if in_rules and "## 翻訳中メモ" in stripped:
            if current_rule:
                rules.append(current_rule)
            break

        if not in_rules:
            continue

        if not stripped or stripped.startswith("参照:"):
            continue

        m = rule_re.match(stripped)
        if m:
            if current_rule:
                rules.append(current_rule)
            current_rule = {
                "number": m.group(1),
                "text": m.group(2),
                "continuations": [],
            }
            continue

        if stripped.startswith("   ") and current_rule:
            current_rule["continuations"].append(stripped.strip())

    if current_rule and current_rule not in rules:
        rules.append(current_rule)

    return rules


def parse_memo(text: str) -> list[str]:
    """Parse translation-rule.md memo section."""
    lines = text.split("\n")
    in_memo = False
    memos: list[str] = []
    memo_re = re.compile(r"^-\s+(.+)$")

    for line in lines:
        stripped = line.strip()
        if "## 翻訳中メモ" in stripped:
            in_memo = True
            continue
        if not in_memo or not stripped:
            continue
        m = memo_re.match(stripped)
        if m:
            memos.append(m.group(1))

    return memos


# ---------------------------------------------------------------------------
# Sheet key-dict builders
# ---------------------------------------------------------------------------

def build_key_dict(
    values: list[list[str]],
    key_col: int,
    sheet_name: str,
    skip_header: bool = True,
    skip_note_rows: bool = False,
) -> dict[str, tuple[int, list[str]]]:
    """Build {key: (sheet_row_number, row_data)} from sheet values."""
    key_dict: dict[str, tuple[int, list[str]]] = {}
    start = 1 if skip_header else 0
    offset = 2 if skip_header else 1

    for i, row in enumerate(values[start:], start=offset):
        key = row[key_col].strip() if len(row) > key_col and row[key_col] else ""
        if not key:
            continue
        if skip_note_rows and key.startswith("※"):
            continue
        if key in key_dict:
            print(
                f"Warning: duplicate key '{key}' in {sheet_name}, "
                f"using first occurrence (row {key_dict[key][0]})",
                file=sys.stderr,
            )
            continue
        key_dict[key] = (i, row)
    return key_dict


def build_rule_dicts(
    values: list[list[str]],
) -> tuple[dict[str, tuple[int, str]], dict[str, list[tuple[int, str]]]]:
    """Build rule_dict and continuation_dict from rules sheet values."""
    rule_dict: dict[str, tuple[int, str]] = {}
    continuation_dict: dict[str, list[tuple[int, str]]] = {}
    last_rule: str | None = None

    for i, row in enumerate(values, start=1):
        col_a = row[0].strip() if len(row) > 0 and row[0] else ""
        col_b = row[1].strip() if len(row) > 1 and row[1] else ""
        if col_a.isdigit():
            rule_dict[col_a] = (i, col_b)
            last_rule = col_a
        elif col_a == "" and col_b != "" and last_rule is not None:
            continuation_dict.setdefault(last_rule, []).append((i, col_b))

    return rule_dict, continuation_dict


def build_memo_set(values: list[list[str]]) -> set[str]:
    """Build a set of memo texts from memo sheet values."""
    memo_set: set[str] = set()
    for row in values:
        text = row[0].strip() if len(row) > 0 and row[0] else ""
        if text:
            memo_set.add(text)
    return memo_set


# ---------------------------------------------------------------------------
# Diff & Sync logic
# ---------------------------------------------------------------------------

def _safe_get(row: list[str], idx: int) -> str:
    """Get a cell value safely, returning empty string for missing indices."""
    return row[idx].strip() if len(row) > idx and row[idx] else ""


def sync_glossary(
    service, md_entries: list[dict], sheet_values: list[list[str]], dry_run: bool
) -> tuple[int, int]:
    """Sync glossary entries. Returns (new_count, updated_count)."""
    sheet_name = SHEETS["glossary"]
    key_dict = build_key_dict(sheet_values, 0, sheet_name)
    new_count = 0
    updated_count = 0

    for entry in md_entries:
        key = entry["english"]
        ja = entry["japanese"]

        if key in key_dict:
            sheet_row, row_data = key_dict[key]
            sheet_ja = _safe_get(row_data, 1)
            if ja != sheet_ja:
                if dry_run:
                    print(
                        f"[DRY RUN] Would update {sheet_name} row {sheet_row}: "
                        f"{key} | {ja}"
                    )
                else:
                    service.spreadsheets().values().update(
                        spreadsheetId=SHEET_ID,
                        range=f"'{sheet_name}'!A{sheet_row}:B{sheet_row}",
                        valueInputOption="RAW",
                        body={"values": [[key, ja]]},
                    ).execute()
                updated_count += 1
        else:
            if dry_run:
                print(
                    f"[DRY RUN] Would append to {sheet_name}: {key} | {ja}"
                )
            else:
                service.spreadsheets().values().append(
                    spreadsheetId=SHEET_ID,
                    range=f"'{sheet_name}'!A:B",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [[key, ja]]},
                ).execute()
            new_count += 1

    return new_count, updated_count


def sync_people(
    service, md_entries: list[dict], sheet_values: list[list[str]], dry_run: bool
) -> tuple[int, int]:
    """Sync people entries. Returns (new_count, updated_count)."""
    sheet_name = SHEETS["people"]
    key_dict = build_key_dict(
        sheet_values, 0, sheet_name, skip_note_rows=True
    )
    new_count = 0
    updated_count = 0

    for entry in md_entries:
        key = entry["name"]
        md_row = [
            entry["name"],
            entry["katakana"],
            entry["method"],
            entry["url1"],
            entry["url2"],
        ]

        if key in key_dict:
            sheet_row, row_data = key_dict[key]
            # Build merged row: preserve sheet values when markdown is empty
            merged = []
            for col_idx in range(5):
                md_val = md_row[col_idx]
                sheet_val = _safe_get(row_data, col_idx)
                if md_val == "" and sheet_val != "":
                    merged.append(sheet_val)
                else:
                    merged.append(md_val)

            # Check if anything changed
            sheet_vals = [_safe_get(row_data, i) for i in range(5)]
            if merged != sheet_vals:
                if dry_run:
                    print(
                        f"[DRY RUN] Would update {sheet_name} row {sheet_row}: "
                        f"{' | '.join(merged)}"
                    )
                else:
                    service.spreadsheets().values().update(
                        spreadsheetId=SHEET_ID,
                        range=f"'{sheet_name}'!A{sheet_row}:E{sheet_row}",
                        valueInputOption="RAW",
                        body={"values": [merged]},
                    ).execute()
                updated_count += 1
        else:
            if dry_run:
                print(
                    f"[DRY RUN] Would append to {sheet_name}: "
                    f"{' | '.join(md_row)}"
                )
            else:
                service.spreadsheets().values().append(
                    spreadsheetId=SHEET_ID,
                    range=f"'{sheet_name}'!A:E",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [md_row]},
                ).execute()
            new_count += 1

    return new_count, updated_count


def sync_rules(
    service,
    md_rules: list[dict],
    sheet_values: list[list[str]],
    dry_run: bool,
) -> tuple[int, int]:
    """Sync rules entries. Returns (new_count, updated_count)."""
    sheet_name = SHEETS["rules"]
    rule_dict, continuation_dict = build_rule_dicts(sheet_values)
    new_count = 0
    updated_count = 0

    for rule in md_rules:
        num = rule["number"]
        md_text = rule["text"]
        md_conts = rule["continuations"]

        if num in rule_dict:
            sheet_row, sheet_text = rule_dict[num]
            # Update main rule text if changed
            if md_text != sheet_text:
                if dry_run:
                    print(
                        f"[DRY RUN] Would update {sheet_name} row {sheet_row}: "
                        f"{num} | {md_text}"
                    )
                else:
                    service.spreadsheets().values().update(
                        spreadsheetId=SHEET_ID,
                        range=f"'{sheet_name}'!A{sheet_row}:B{sheet_row}",
                        valueInputOption="RAW",
                        body={"values": [[num, md_text]]},
                    ).execute()
                updated_count += 1

            # Handle continuation lines
            sheet_conts = continuation_dict.get(num, [])
            for j, md_cont_text in enumerate(md_conts):
                if j < len(sheet_conts):
                    s_row, s_text = sheet_conts[j]
                    if md_cont_text != s_text:
                        if dry_run:
                            print(
                                f"[DRY RUN] Would update {sheet_name} "
                                f"row {s_row}: | {md_cont_text}"
                            )
                        else:
                            service.spreadsheets().values().update(
                                spreadsheetId=SHEET_ID,
                                range=f"'{sheet_name}'!A{s_row}:B{s_row}",
                                valueInputOption="RAW",
                                body={"values": [["", md_cont_text]]},
                            ).execute()
                        updated_count += 1
                else:
                    # New continuation line
                    if dry_run:
                        print(
                            f"[DRY RUN] Would append to {sheet_name}: "
                            f"| {md_cont_text}"
                        )
                    else:
                        service.spreadsheets().values().append(
                            spreadsheetId=SHEET_ID,
                            range=f"'{sheet_name}'!A:B",
                            valueInputOption="RAW",
                            insertDataOption="INSERT_ROWS",
                            body={"values": [["", md_cont_text]]},
                        ).execute()
                    new_count += 1
        else:
            # New rule
            if dry_run:
                print(
                    f"[DRY RUN] Would append to {sheet_name}: "
                    f"{num} | {md_text}"
                )
            else:
                service.spreadsheets().values().append(
                    spreadsheetId=SHEET_ID,
                    range=f"'{sheet_name}'!A:B",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [[num, md_text]]},
                ).execute()
            new_count += 1

            # Append continuation lines for new rule
            for md_cont_text in md_conts:
                if dry_run:
                    print(
                        f"[DRY RUN] Would append to {sheet_name}: "
                        f"| {md_cont_text}"
                    )
                else:
                    service.spreadsheets().values().append(
                        spreadsheetId=SHEET_ID,
                        range=f"'{sheet_name}'!A:B",
                        valueInputOption="RAW",
                        insertDataOption="INSERT_ROWS",
                        body={"values": [["", md_cont_text]]},
                    ).execute()
                new_count += 1

    return new_count, updated_count


def sync_memo(
    service, md_memos: list[str], sheet_values: list[list[str]], dry_run: bool
) -> int:
    """Sync memo entries (append-only). Returns new_count."""
    sheet_name = SHEETS["memo"]
    memo_set = build_memo_set(sheet_values)
    new_count = 0

    for memo_text in md_memos:
        if memo_text not in memo_set:
            if dry_run:
                print(
                    f"[DRY RUN] Would append to {sheet_name}: {memo_text}"
                )
            else:
                service.spreadsheets().values().append(
                    spreadsheetId=SHEET_ID,
                    range=f"'{sheet_name}'!A:A",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [[memo_text]]},
                ).execute()
            new_count += 1

    return new_count


# ---------------------------------------------------------------------------
# Authentication & Service
# ---------------------------------------------------------------------------

def build_service():
    """Build Google Sheets API service from environment variable."""
    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
    if not key_json:
        print(
            "Error: GOOGLE_SERVICE_ACCOUNT_KEY environment variable is not set",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        key_info = json.loads(key_json)
    except json.JSONDecodeError as e:
        print(f"Error: failed to parse service account key JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        from google.oauth2.service_account import Credentials

        creds = Credentials.from_service_account_info(
            key_info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
    except Exception as e:
        print(f"Error: authentication failed: {e}", file=sys.stderr)
        sys.exit(1)

    from googleapiclient.discovery import build

    return build("sheets", "v4", credentials=creds)


def fetch_sheet(service, sheet_name: str, range_suffix: str) -> list[list[str]]:
    """Fetch sheet values via Sheets API."""
    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=SHEET_ID,
            range=f"'{sheet_name}'!{range_suffix}",
            valueRenderOption="FORMATTED_VALUE",
        )
        .execute()
    )
    return result.get("values", [])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Reverse sync markdown files to Google Spreadsheet"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without writing to spreadsheet",
    )
    args = parser.parse_args()
    dry_run = args.dry_run

    service = build_service()
    total_changes = 0

    # --- Glossary ---
    glossary_path = REPO_ROOT / "glosary.md"
    if glossary_path.exists():
        glossary_text = glossary_path.read_text(encoding="utf-8")
        md_glossary = parse_glossary(glossary_text)
        sheet_glossary = fetch_sheet(service, SHEETS["glossary"], "A:B")
        new, updated = sync_glossary(service, md_glossary, sheet_glossary, dry_run)
        total_changes += new + updated
        print(
            f"Reverse sync: glosary.md -> {SHEETS['glossary']}: "
            f"{new} new, {updated} updated"
        )
    else:
        print("Warning: glosary.md not found, skipping", file=sys.stderr)

    # --- People ---
    people_path = REPO_ROOT / "people.md"
    if people_path.exists():
        people_text = people_path.read_text(encoding="utf-8")
        md_people = parse_people(people_text)
        sheet_people = fetch_sheet(service, SHEETS["people"], "A:E")
        new, updated = sync_people(service, md_people, sheet_people, dry_run)
        total_changes += new + updated
        print(
            f"Reverse sync: people.md -> {SHEETS['people']}: "
            f"{new} new, {updated} updated"
        )
    else:
        print("Warning: people.md not found, skipping", file=sys.stderr)

    # --- Rules ---
    rules_path = REPO_ROOT / "translation-rule.md"
    if rules_path.exists():
        rules_text = rules_path.read_text(encoding="utf-8")

        # Rules section
        md_rules = parse_rules(rules_text)
        sheet_rules = fetch_sheet(service, SHEETS["rules"], "A:B")
        new, updated = sync_rules(service, md_rules, sheet_rules, dry_run)
        total_changes += new + updated
        print(
            f"Reverse sync: translation-rule.md (rules) -> {SHEETS['rules']}: "
            f"{new} new, {updated} updated"
        )

        # Memo section
        md_memos = parse_memo(rules_text)
        sheet_memos = fetch_sheet(service, SHEETS["memo"], "A:A")
        new = sync_memo(service, md_memos, sheet_memos, dry_run)
        total_changes += new
        print(
            f"Reverse sync: translation-rule.md (memo) -> {SHEETS['memo']}: "
            f"{new} new"
        )
    else:
        print("Warning: translation-rule.md not found, skipping", file=sys.stderr)

    if total_changes == 0:
        print("Reverse sync: no changes detected")
    else:
        print(f"Reverse sync complete: {total_changes} change(s) applied")


if __name__ == "__main__":
    main()
