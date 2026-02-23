#!/usr/bin/env python3
"""Translation consistency tests across chapters.

Checks glossary term usage, note format, paragraph formatting,
katakana spacing, and code fence balance in translated chapters.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHAPTER_GLOB = "chapter_*.md"

# {canonical: [variant spellings to flag]}
VARIANT_MAP: dict[str, list[str]] = {
    "マークルツリー": ["マークル木", "マークル ツリー"],
    "コンテクスト": ["コンテキスト"],
}

# Accepted blockquote note labels -> what they should be
NOTE_CORRECTIONS: dict[str, str] = {
    "> **注**": "> **注記**",
    "> **Note**": "> **注記**",
    "> **Tip**": "> **ヒント**",
    "> **Warning**": "> **警告**",
}

JAPANESE_RE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]")
KATAKANA_SPACE_RE = re.compile(r"[\u30A0-\u30FF][\s][\u30A0-\u30FF]")
HEADING_PUNCT_RE = re.compile(r"^#+\s.*[。、]$")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def extract_prose_lines(content: str) -> list[tuple[int, str]]:
    """Return (1-based line number, text) for lines outside code fences."""
    result: list[tuple[int, str]] = []
    in_code = False
    for i, line in enumerate(content.splitlines(), 1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            result.append((i, line))
    return result


def is_translated(content: str) -> bool:
    """True if >= 20% of non-whitespace characters are Japanese."""
    prose = [line for _, line in extract_prose_lines(content)]
    text = "".join(prose)
    chars = re.sub(r"\s", "", text)
    if not chars:
        return False
    jp_count = len(JAPANESE_RE.findall(chars))
    return jp_count / len(chars) >= 0.20


def get_translated_chapters() -> list[Path]:
    """Return paths of translated chapter files."""
    src = REPO_ROOT / "src"
    chapters: list[Path] = []
    for p in sorted(src.glob(CHAPTER_GLOB)):
        content = p.read_text(encoding="utf-8")
        if is_translated(content):
            chapters.append(p)
    return chapters


def _strip_inline_code(line: str) -> str:
    """Remove inline code spans from a line."""
    return re.sub(r"`[^`]+`", "", line)


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

class TestGlossaryConsistency(unittest.TestCase):
    """Check that known term variants are not used in translated chapters."""

    @classmethod
    def setUpClass(cls):
        cls.chapters = get_translated_chapters()
        if not cls.chapters:
            raise unittest.SkipTest("No translated chapters found")

    def test_no_variant_terms(self):
        errors: list[str] = []
        for path in self.chapters:
            content = path.read_text(encoding="utf-8")
            for lineno, line in extract_prose_lines(content):
                clean = _strip_inline_code(line)
                for canonical, variants in VARIANT_MAP.items():
                    for variant in variants:
                        if variant in clean:
                            errors.append(
                                f"{path.name}:{lineno}: "
                                f"expected \"{canonical}\" but found \"{variant}\""
                            )
        if errors:
            self.fail(
                f"Found {len(errors)} glossary variant(s):\n"
                + "\n".join(errors)
            )


class TestNoteFormatConsistency(unittest.TestCase):
    """Check that blockquote note labels use the canonical format."""

    @classmethod
    def setUpClass(cls):
        cls.chapters = get_translated_chapters()
        if not cls.chapters:
            raise unittest.SkipTest("No translated chapters found")

    def test_note_labels(self):
        errors: list[str] = []
        for path in self.chapters:
            content = path.read_text(encoding="utf-8")
            for lineno, line in extract_prose_lines(content):
                stripped = line.rstrip()
                for bad, good in NOTE_CORRECTIONS.items():
                    if stripped == bad:
                        errors.append(
                            f"{path.name}:{lineno}: "
                            f"\"{bad}\" should be \"{good}\""
                        )
        if errors:
            self.fail(
                f"Found {len(errors)} non-standard note label(s):\n"
                + "\n".join(errors)
            )


class TestParagraphFormatting(unittest.TestCase):
    """Check full-width space at paragraph start and no heading punctuation."""

    @classmethod
    def setUpClass(cls):
        cls.chapters = get_translated_chapters()
        if not cls.chapters:
            raise unittest.SkipTest("No translated chapters found")

    def test_heading_no_trailing_punctuation(self):
        errors: list[str] = []
        for path in self.chapters:
            content = path.read_text(encoding="utf-8")
            for lineno, line in extract_prose_lines(content):
                if HEADING_PUNCT_RE.match(line):
                    errors.append(f"{path.name}:{lineno}: {line.rstrip()}")
        if errors:
            self.fail(
                f"Found {len(errors)} heading(s) ending with punctuation:\n"
                + "\n".join(errors)
            )

    def test_paragraph_fullwidth_space(self):
        skip_prefixes = ("#", ">", "|", "!", "[", "```", "\u3000")
        errors: list[str] = []
        for path in self.chapters:
            content = path.read_text(encoding="utf-8")
            lines = extract_prose_lines(content)
            prev_was_bold_def = False
            for lineno, line in lines:
                stripped = line.strip()
                if not stripped:
                    # Blank lines preserve bold-def context
                    continue
                if any(line.startswith(p) for p in skip_prefixes):
                    prev_was_bold_def = False
                    continue
                # Track definition term lines: **bold** or `code`
                if re.match(r"^\*\*[^*]+\*\*\s*$", line):
                    prev_was_bold_def = True
                    continue
                if re.match(r"^`[^`]+`\s*$", line):
                    prev_was_bold_def = True
                    continue
                # Skip list items (unordered and numbered)
                if re.match(r"^[-*]\s", line) or re.match(r"^\d+\.\s", line):
                    prev_was_bold_def = False
                    continue
                # Skip lines that are entirely non-Japanese
                if not JAPANESE_RE.search(line):
                    prev_was_bold_def = False
                    continue
                # Skip figure captions (図X-Y ...)
                if re.match(r"^図\d+", line):
                    prev_was_bold_def = False
                    continue
                # Skip label lines ending with ： or :
                if stripped.endswith("：") or stripped.endswith(":"):
                    prev_was_bold_def = False
                    continue
                # Skip definition list descriptions (line after bold term)
                if prev_was_bold_def:
                    prev_was_bold_def = False
                    continue
                prev_was_bold_def = False
                # Line starts with Japanese but no full-width space
                if JAPANESE_RE.match(line):
                    errors.append(f"{path.name}:{lineno}: {line[:40]}...")
        if errors:
            self.fail(
                f"Found {len(errors)} paragraph(s) missing full-width space:\n"
                + "\n".join(errors)
            )


class TestKatakanaSpacing(unittest.TestCase):
    """Check no half-width spaces between katakana words."""

    @classmethod
    def setUpClass(cls):
        cls.chapters = get_translated_chapters()
        if not cls.chapters:
            raise unittest.SkipTest("No translated chapters found")

    def test_no_katakana_spaces(self):
        errors: list[str] = []
        for path in self.chapters:
            content = path.read_text(encoding="utf-8")
            for lineno, line in extract_prose_lines(content):
                clean = _strip_inline_code(line)
                if KATAKANA_SPACE_RE.search(clean):
                    errors.append(f"{path.name}:{lineno}: {line.rstrip()}")
        if errors:
            self.fail(
                f"Found {len(errors)} katakana spacing issue(s):\n"
                + "\n".join(errors)
            )


class TestCodeFenceBalance(unittest.TestCase):
    """Check that code fences are balanced (even count) in each file."""

    @classmethod
    def setUpClass(cls):
        cls.chapters = get_translated_chapters()
        if not cls.chapters:
            raise unittest.SkipTest("No translated chapters found")

    def test_balanced_fences(self):
        errors: list[str] = []
        for path in self.chapters:
            content = path.read_text(encoding="utf-8")
            count = sum(
                1 for line in content.splitlines() if line.startswith("```")
            )
            if count % 2 != 0:
                errors.append(
                    f"{path.name}: {count} code fence markers (odd)"
                )
        if errors:
            self.fail(
                "Unbalanced code fences:\n" + "\n".join(errors)
            )


if __name__ == "__main__":
    unittest.main()
