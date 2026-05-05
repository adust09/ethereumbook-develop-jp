#!/usr/bin/env python3
"""
章単位で画像翻訳を実行するバッチドライバ。

各画像 stem (例: maet_0406) に対し、--maps-dir 配下の同名 JSON
(scripts/maps/maet_0406.json) を翻訳マップとして探索する。マップが無い
画像はスキップする。

Usage:
    /tmp/imgtools/bin/python3 scripts/translate_chapter_images.py ch4
    /tmp/imgtools/bin/python3 scripts/translate_chapter_images.py ch4 \
        --only maet_0406,maet_0407 --preview \
        --font-bold /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc \
        --font-regular /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
"""
import argparse
import json
import sys
from pathlib import Path

from translate_image import translate_image


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-translate every image in a chapter")
    parser.add_argument("chapter", help="Chapter directory under src/images, e.g. ch4")
    parser.add_argument("--maps-dir", default="scripts/maps",
                        help="Directory containing per-image JSON maps (default: scripts/maps)")
    parser.add_argument("--preview", action="store_true",
                        help="Save as _jp.png alongside originals")
    parser.add_argument("--only",
                        help="Comma-separated image stems to limit to (e.g. maet_0406,maet_0407)")
    parser.add_argument("--font-bold", dest="font_bold", default=None)
    parser.add_argument("--font-regular", dest="font_regular", default=None)
    args = parser.parse_args()

    img_dir = Path("src/images") / args.chapter
    maps_dir = Path(args.maps_dir)

    if not img_dir.is_dir():
        print(f"Image dir not found: {img_dir}", file=sys.stderr)
        return 2
    if not maps_dir.is_dir():
        print(f"Maps dir not found: {maps_dir}", file=sys.stderr)
        return 2

    only = set(args.only.split(",")) if args.only else None

    images = sorted(img_dir.glob("maet_*.png"))
    if not images:
        print(f"No maet_*.png images under {img_dir}", file=sys.stderr)
        return 2

    failures: list[tuple[str, str]] = []
    processed = 0
    skipped = 0
    for img_path in images:
        stem = img_path.stem
        if only and stem not in only:
            continue
        map_path = maps_dir / f"{stem}.json"
        if not map_path.exists():
            print(f"INFO: no map for {stem}, skip ({map_path})")
            skipped += 1
            continue
        print(f"\n=== {stem} ===")
        try:
            tmap = json.loads(map_path.read_text())
            translate_image(
                str(img_path),
                tmap,
                preview=args.preview,
                font_bold=args.font_bold,
                font_regular=args.font_regular,
            )
            processed += 1
        except Exception as exc:
            failures.append((stem, repr(exc)))

    print(f"\nDone: {processed} ok, {skipped} skipped (no map), {len(failures)} failed")
    if failures:
        for k, msg in failures:
            print(f"  FAIL {k}: {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
