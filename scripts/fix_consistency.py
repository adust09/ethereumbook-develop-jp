#!/usr/bin/env python3
"""Auto-fix translation consistency issues detected by test_consistency.py.

Usage:
    python3 scripts/fix_consistency.py src/chapter_6.md [src/chapter_8.md ...]
    python3 scripts/fix_consistency.py --all    # fix all translated chapters
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"

# Must match test_consistency.py
VARIANT_MAP: dict[str, list[str]] = {
    "マークルツリー": ["マークル木", "マークル ツリー"],
    "コンテクスト": ["コンテキスト"],
    "暗号通貨": ["仮想通貨"],
    "スマートコントラクト": ["スマート コントラクト"],
    "ライブラリ": ["ライブラリー"],
    "ブラウザ": ["ブラウザー"],
    "コンピュータ": ["コンピューター"],
    "バリデータ": ["バリデーター"],
    "ギャヴィン・ウッド": ["ギャビン・ウッド"],
    "ピーター・ヴェスネス": ["ピーター・ヴェッセネス"],
    "フィリップ・ダイアン": ["フィル・ダイアン"],
    "ナスターシア・サックス": ["ナスターシャ・サックス"],
    "ジェイコブ・エヴァンス": ["ジェイコブ・エバンス"],
}

JAPANESE_RE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]")
SKIP_PREFIXES = ("#", ">", "|", "!", "[", "```", "\u3000")


def fix_variant_terms(content: str) -> str:
    """Replace variant terms with canonical forms."""
    for canonical, variants in VARIANT_MAP.items():
        for variant in variants:
            content = content.replace(variant, canonical)
    return content


def fix_fullwidth_spaces(content: str) -> str:
    """Add full-width space to paragraph-starting Japanese lines."""
    lines = content.splitlines(keepends=True)

    # Find prose lines (outside code fences)
    in_code = False
    prose_linenos = set()
    for i, line in enumerate(lines):
        if line.rstrip("\n").startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            prose_linenos.add(i)

    prev_was_bold_def = False
    for i in range(len(lines)):
        if i not in prose_linenos:
            prev_was_bold_def = False
            continue
        line = lines[i].rstrip("\n")
        stripped = line.strip()
        if not stripped:
            continue
        if any(line.startswith(p) for p in SKIP_PREFIXES):
            prev_was_bold_def = False
            continue
        if re.match(r"^\*\*[^*]+\*\*\s*$", line):
            prev_was_bold_def = True
            continue
        if re.match(r"^`[^`]+`\s*$", line):
            prev_was_bold_def = True
            continue
        if re.match(r"^[-*]\s", line) or re.match(r"^\d+\.\s", line):
            prev_was_bold_def = False
            continue
        if not JAPANESE_RE.search(line):
            prev_was_bold_def = False
            continue
        if re.match(r"^図\d+", line):
            prev_was_bold_def = False
            continue
        if stripped.endswith("：") or stripped.endswith(":"):
            prev_was_bold_def = False
            continue
        if prev_was_bold_def:
            prev_was_bold_def = False
            continue
        prev_was_bold_def = False
        if JAPANESE_RE.match(line):
            lines[i] = "\u3000" + lines[i]

    return "".join(lines)


def fix_file(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    original = content

    content = fix_variant_terms(content)
    content = fix_fullwidth_spaces(content)

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"  Fixed: {path.name}")
    else:
        print(f"  OK:    {path.name}")


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    if sys.argv[1] == "--all":
        files = sorted(SRC_DIR.glob("chapter_*.md")) + \
                sorted(SRC_DIR.glob("intro.md")) + \
                sorted(SRC_DIR.glob("preface.md"))
    else:
        files = [Path(f) for f in sys.argv[1:]]

    for path in files:
        if not path.exists():
            print(f"  Skip:  {path} (not found)")
            continue
        fix_file(path)


if __name__ == "__main__":
    main()
