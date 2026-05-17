#!/usr/bin/env python3
"""
画像内の英語テキストを日本語に翻訳するスクリプト。

OCR (EasyOCR) + Inpainting (OpenCV) により、元画像のレイアウト（矢印、枠線、アイコン等）
を維持しながらテキスト部分のみを差し替える。

Usage:
    # venv setup (初回のみ)
    python3 -m venv /tmp/imgtools
    /tmp/imgtools/bin/pip install Pillow opencv-python-headless easyocr

    # 実行（翻訳マップ JSON 指定）
    /tmp/imgtools/bin/python3 scripts/translate_image.py \\
        src/images/ch11/maet_1102.png --map maps/maet_1102.json

    # プレビューのみ（上書きしない、_jp.png に保存）
    /tmp/imgtools/bin/python3 scripts/translate_image.py \\
        src/images/ch11/maet_1102.png --map maps/maet_1102.json --preview

翻訳マップ JSON の仕様:
    {
      "Original Text": {
        "ja": "翻訳テキスト",
        "bold": true,           // (省略可) ヒラギノ W6 を使う
        "font_size": 22,        // (省略可) フォントサイズを明示指定（自動縮小無効）
        "size_group": "steps",  // (省略可) 同グループは bbox 高さ中央値でサイズ統一
        "group": "step1"        // (省略可) 複数 OCR 領域を 1 つの翻訳にマージ
      },
      // ja=null は「テキストを残す」preserve（マスクから除外）
      "Web3": {"ja": null},
      // __skip_match_boxes__: 指定 bbox 内に収まる OCR 検出はマッチング処理を
      // スキップし、強制的にマスク対象（soft）に回す。同じ英単語が異なる場所で
      // 異なるサイズになる場合に、片方の領域を __extra_text_regions__ で
      // 上書き描画するために使う。
      "__skip_match_boxes__": [[x1, y1, x2, y2], ...]
    }
"""
import argparse
import fnmatch
import json
from collections import defaultdict
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import easyocr

import os

_FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]
_FONT_CANDIDATES_REGULAR = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def _pick_font(paths: list[str]) -> str:
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0]


FONT_BOLD = _pick_font(_FONT_CANDIDATES_BOLD)
FONT_REGULAR = _pick_font(_FONT_CANDIDATES_REGULAR)


def detect_text(image_path: str) -> list[dict]:
    reader = easyocr.Reader(["en"], gpu=False)
    results = reader.readtext(image_path)
    out = []
    for bbox, text, conf in results:
        pts = np.array(bbox, dtype=np.int32)
        x_min, y_min = pts.min(axis=0).tolist()
        x_max, y_max = pts.max(axis=0).tolist()
        out.append({
            "text": text,
            "confidence": round(conf, 2),
            "box": [x_min, y_min, x_max, y_max],
        })
    return out


def build_mask(image_path: str, regions: list[dict], pad: int = 2) -> np.ndarray:
    """
    bbox 内の「文字形状の連結成分」だけをマスクする。
    枠線・矢印などの線（横長/縦長/極端なアスペクト比/巨大塗りつぶし）は除外して保護する。

    旧実装は `gray < 180` を bbox 全体に適用していたため、bbox 内に侵入した
    枠線や矢印まで削除していた。連結成分フィルターでこれを防ぐ。
    """
    img_cv = cv2.imread(image_path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    for region in regions:
        x1, y1, x2, y2 = region["box"]
        x1 = max(0, x1 - pad); y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad); y2 = min(h, y2 + pad)
        rh, rw = y2 - y1, x2 - x1
        if rh <= 0 or rw <= 0:
            continue

        roi = gray[y1:y2, x1:x2]
        bin_dark = (roi < 180).astype(np.uint8)

        n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bin_dark, 4)
        char_mask = np.zeros_like(bin_dark)

        for i in range(1, n_labels):
            _, _, cw, ch_, area = stats[i]
            if area < 3:
                continue
            aspect = max(cw, ch_) / max(1, min(cw, ch_))
            if cw >= rw * 0.85 and ch_ <= rh * 0.35:
                continue  # 横線
            if ch_ >= rh * 0.85 and cw <= rw * 0.35:
                continue  # 縦線
            if aspect > 12:
                continue  # 細長い線
            if area > rh * rw * 0.5:
                continue  # 巨大な塗りつぶし
            char_mask[labels == i] = 1

        # アンチエイリアス端カバーの軽い膨張のみ（旧 iterations=2 → 1）
        kernel = np.ones((3, 3), np.uint8)
        char_mask = cv2.dilate(char_mask, kernel, iterations=1)
        mask[y1:y2, x1:x2] = np.maximum(mask[y1:y2, x1:x2], char_mask * 255)

    return mask


def inpaint_image(image_path: str, mask: np.ndarray, radius: int = 3) -> np.ndarray:
    img_cv = cv2.imread(image_path)
    return cv2.inpaint(img_cv, mask, radius, cv2.INPAINT_TELEA)


def restore_borders(
    original_path: str,
    inpainted: np.ndarray,
    detections: list[dict],
    dark_thresh: int = 100,
    text_pad: int = 8,
    protect_boxes: list = None,
) -> np.ndarray:
    """Inpainting でぼけた枠線・矢印を原本から復元する。

    原本の暗いピクセル (gray < dark_thresh) のうち、OCR テキスト bbox の
    外側にあるものだけを inpainted 画像に上書きコピーする。

    protect_boxes: __extra_mask_boxes__ など、復元を抑止したい領域（OCR が
    検出できなかった文字（italic I、em ダッシュ等）を再描画しないため）。
    """
    orig = cv2.imread(original_path)
    gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # テキスト除外ゾーン（OCR bbox + padding）
    text_zone = np.zeros((h, w), dtype=np.uint8)
    for det in detections:
        x1, y1, x2, y2 = det["box"]
        x1 = max(0, x1 - text_pad)
        y1 = max(0, y1 - text_pad)
        x2 = min(w, x2 + text_pad)
        y2 = min(h, y2 + text_pad)
        text_zone[y1:y2, x1:x2] = 1
    for box in (protect_boxes or []):
        x1, y1, x2, y2 = box
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(w, x2); y2 = min(h, y2)
        text_zone[y1:y2, x1:x2] = 1

    # 枠線マスク: 暗いピクセル & テキスト外
    border = ((gray < dark_thresh).astype(np.uint8)) & (1 - text_zone)
    kernel = np.ones((2, 2), np.uint8)
    border = cv2.dilate(border, kernel, iterations=1)

    result = inpainted.copy()
    result[border == 1] = orig[border == 1]
    return result


def compute_size_groups(regions: list[dict]) -> dict:
    """同一 size_group の region は bbox 高さの中央値でフォントサイズを揃える。"""
    grouped = defaultdict(list)
    for r in regions:
        g = r.get("size_group")
        if g:
            grouped[g].append(r["box"][3] - r["box"][1])
    return {g: int(np.median(hs) * 0.55) for g, hs in grouped.items()}


def draw_translations(inpainted_bgr: np.ndarray, regions: list[dict]) -> Image.Image:
    img_pil = Image.fromarray(cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    group_sizes = compute_size_groups(regions)

    for region in regions:
        box = region["box"]
        cx = (box[0] + box[2]) / 2 + region.get("text_offset_x", 0)
        cy = (box[1] + box[3]) / 2 + region.get("text_offset_y", 0)
        box_w = box[2] - box[0]
        box_h = box[3] - box[1]

        # 優先順位: 明示 font_size > size_group の中央値 > box_h ベース
        if region.get("font_size"):
            font_size = int(region["font_size"])
            allow_shrink = False
        elif region.get("size_group") in group_sizes:
            font_size = max(14, group_sizes[region["size_group"]])
            allow_shrink = False
        else:
            font_size = max(14, int(box_h * 0.55))
            allow_shrink = True
        if "\n" in region["translation"] and allow_shrink:
            font_size = max(14, int(font_size * 0.7))

        font_path = FONT_BOLD if region.get("bold") else FONT_REGULAR
        font = ImageFont.truetype(font_path, font_size)

        if allow_shrink:
            max_w = box_w * 0.95
            longest_line = max(region["translation"].split("\n"), key=len)
            while font_size > 8:
                tb = font.getbbox(longest_line)
                if (tb[2] - tb[0]) <= max_w:
                    break
                font_size -= 1
                font = ImageFont.truetype(font_path, font_size)

        color = region.get("color")
        if color is None:
            fill = (0, 0, 0)
        elif isinstance(color, str):
            c = color.lstrip("#")
            fill = (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
        else:
            fill = tuple(color)
        draw.text((cx, cy), region["translation"], font=font, fill=fill, anchor="mm")

    return img_pil


def translate_image(image_path: str, translation_map: dict, preview: bool = False, output_path: str = None):
    print(f"[1/4] OCR: detecting text in {image_path}")
    detections = detect_text(image_path)
    print(f"       Found {len(detections)} text regions")

    # __extra_mask_boxes__: 全領域マスク（タイトルバンドなど大きく消したい場合）
    extra_mask_boxes = translation_map.pop("__extra_mask_boxes__", [])
    # __extra_mask_boxes_soft__: 連結成分フィルター適用マスク（はみ出し文字の追加マスクに）
    extra_mask_boxes_soft = translation_map.pop("__extra_mask_boxes_soft__", [])
    # __extra_preserve_boxes__: マスクから強制的に除外する領域（矢印などを保護）
    extra_preserve_boxes = translation_map.pop("__extra_preserve_boxes__", [])
    # __extra_text_regions__ は OCR を経由せず座標指定で翻訳テキストを描画
    # 形式: [{"box": [x1,y1,x2,y2], "ja": "テキスト", "bold": true, "font_size": 24}, ...]
    extra_text_regions = translation_map.pop("__extra_text_regions__", [])
    # __skip_match_boxes__: 指定 bbox に収まる OCR 検出はマッチング対象から外し、
    # soft マスクに強制追加する（英語は消えるが日本語は描画されない）。
    # 同じ英単語が場所ごとに異なるサイズ/色で描画されるケースを切り分けるために、
    # 片方の領域を __extra_text_regions__ で上書きする用途で使う。
    skip_match_boxes = translation_map.pop("__skip_match_boxes__", [])

    regions = []
    preserve_boxes = []
    groups = defaultdict(list)
    for det in detections:
        if any(
            det["box"][0] >= sb[0] and det["box"][1] >= sb[1]
            and det["box"][2] <= sb[2] and det["box"][3] <= sb[3]
            for sb in skip_match_boxes
        ):
            extra_mask_boxes_soft.append(det["box"])
            print(f"       '{det['text']}' → (skip-match, masked)")
            continue
        text_lower = det["text"].lower().strip()
        matched, matched_key = None, None
        for key, value in translation_map.items():
            if text_lower == key.lower():
                matched, matched_key = value, key
                break
        if matched_key is None:
            for key, value in translation_map.items():
                if "*" in key and fnmatch.fnmatchcase(text_lower, key.lower()):
                    matched, matched_key = value, key
                    break

        if matched_key is None:
            print(f"       '{det['text']}' → (skip)")
            continue
        # group は preserve より優先（group メンバーは ja=null でも OK）
        if matched.get("group"):
            groups[matched["group"]].append((det, matched))
            print(f"       '{det['text']}' → (merge:{matched['group']})")
            continue
        # ja=null は preserve（マスクから除外して原文を残す）
        if matched.get("ja") is None:
            preserve_boxes.append(det["box"])
            print(f"       '{det['text']}' → (preserve)")
            continue

        regions.append({
            "box": det["box"],
            "original": det["text"],
            "translation": matched["ja"],
            "bold": matched.get("bold", False),
            "size_group": matched.get("size_group"),
            "font_size": matched.get("font_size"),
            "text_offset_x": matched.get("text_offset_x", 0),
            "text_offset_y": matched.get("text_offset_y", 0),
            "color": matched.get("color"),
        })
        print(f"       '{det['text']}' → '{matched['ja']}'")

    for gname, items in groups.items():
        boxes = [det["box"] for det, _ in items]
        merged_box = [
            min(b[0] for b in boxes),
            min(b[1] for b in boxes),
            max(b[2] for b in boxes),
            max(b[3] for b in boxes),
        ]
        ja = next((v["ja"] for _, v in items if v.get("ja")), None)
        bold = next((v.get("bold", False) for _, v in items if v.get("ja")), False)
        size_group = next((v.get("size_group") for _, v in items if v.get("ja")), None)
        font_size = next((v.get("font_size") for _, v in items if v.get("ja")), None)
        text_offset_x = next((v.get("text_offset_x") for _, v in items if v.get("ja")), 0) or 0
        text_offset_y = next((v.get("text_offset_y") for _, v in items if v.get("ja")), 0) or 0
        color = next((v.get("color") for _, v in items if v.get("ja")), None)
        if ja:
            regions.append({
                "box": merged_box,
                "original": f"<group:{gname}>",
                "translation": ja,
                "bold": bold,
                "size_group": size_group,
                "font_size": font_size,
                "text_offset_x": text_offset_x,
                "text_offset_y": text_offset_y,
                "color": color,
            })
            print(f"       (merged '{gname}') → '{ja}'")

    # __extra_text_regions__ をそのまま region に追加（OCR 経由しない描画）
    for er in extra_text_regions:
        regions.append({
            "box": er["box"],
            "original": "<extra>",
            "translation": er["ja"],
            "bold": er.get("bold", False),
            "size_group": er.get("size_group"),
            "font_size": er.get("font_size"),
            "color": er.get("color"),
        })
        print(f"       (extra) → '{er['ja']}'")

    if not regions and not preserve_boxes:
        print("No regions to translate.")
        return

    print(f"[2/4] Mask (connected-component filter) for {len(regions)} regions")
    mask_regions = list(regions)
    if extra_mask_boxes_soft:
        for box in extra_mask_boxes_soft:
            mask_regions.append({"box": box})
        print(f"       + {len(extra_mask_boxes_soft)} soft extra mask box(es)")
    mask = build_mask(image_path, mask_regions)
    if extra_mask_boxes:
        for box in extra_mask_boxes:
            x1, y1, x2, y2 = box
            mask[y1:y2, x1:x2] = 255  # 連結成分フィルター無視で全領域マスク
        print(f"       + {len(extra_mask_boxes)} extra mask box(es) [unconditional]")
    for box in preserve_boxes:
        x1, y1, x2, y2 = box
        mask[y1:y2, x1:x2] = 0
    for box in extra_preserve_boxes:
        x1, y1, x2, y2 = box
        mask[y1:y2, x1:x2] = 0

    print("[3/4] Inpainting (TELEA)")
    inpainted = inpaint_image(image_path, mask)
    # extra_mask_boxes (hard) は inpaint 後に各 box の周辺中央値で再塗装
    # （inpaint が複雑な領域で失敗した残骸を確実に消す）
    if extra_mask_boxes:
        for box in extra_mask_boxes:
            x1, y1, x2, y2 = box
            h_img, w_img = inpainted.shape[:2]
            sx1, sy1 = max(0, x1 - 5), max(0, y1 - 5)
            sx2, sy2 = min(w_img, x2 + 5), min(h_img, y2 + 5)
            sample = inpainted[sy1:sy2, sx1:sx2].copy()
            sample[max(0, y1-sy1):y2-sy1, max(0, x1-sx1):x2-sx1] = 0
            sample_pixels = sample[sample.sum(axis=2) > 0]
            if len(sample_pixels) > 0:
                fill_color = np.median(sample_pixels, axis=0).astype(np.uint8)
                inpainted[y1:y2, x1:x2] = fill_color

    # 枠線・矢印の復元（inpainting で発生したボケを原本から上書き修復）
    inpainted = restore_borders(image_path, inpainted, detections, protect_boxes=extra_mask_boxes)

    print("[4/4] Drawing Japanese text")
    result = draw_translations(inpainted, regions)

    if preview:
        out = output_path or image_path.replace(".png", "_jp.png")
    else:
        out = output_path or image_path
    result.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate image text EN→JP")
    parser.add_argument("image", help="Path to PNG image")
    parser.add_argument("--map", required=True, help="JSON file with translation map")
    parser.add_argument("--preview", action="store_true", help="Save as _jp.png instead of overwriting")
    parser.add_argument("--out", default=None, help="Explicit output path")
    args = parser.parse_args()

    with open(args.map) as f:
        tmap = json.load(f)
    translate_image(args.image, tmap, preview=args.preview, output_path=args.out)
