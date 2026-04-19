#!/usr/bin/env python3
"""
画像内の英語テキストを日本語に翻訳するスクリプト。

OCR (EasyOCR) + Inpainting (OpenCV) により、元画像のレイアウト（矢印、枠線、アイコン等）
を完全に維持しながらテキスト部分のみを差し替える。

Usage:
    # venv setup (初回のみ)
    python3 -m venv /tmp/imgtools
    /tmp/imgtools/bin/pip install Pillow opencv-python-headless easyocr

    # 実行
    /tmp/imgtools/bin/python3 scripts/translate_image.py src/images/ch13/maet_1301.png

    # プレビューのみ（上書きしない）
    /tmp/imgtools/bin/python3 scripts/translate_image.py src/images/ch13/maet_1301.png --preview
"""
import argparse
import sys
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import easyocr

FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"


def detect_text(image_path: str) -> list[dict]:
    reader = easyocr.Reader(["en"], gpu=False)
    results = reader.readtext(image_path)
    detections = []
    for bbox, text, conf in results:
        pts = np.array(bbox, dtype=np.int32)
        x_min, y_min = pts.min(axis=0).tolist()
        x_max, y_max = pts.max(axis=0).tolist()
        detections.append({
            "text": text,
            "confidence": round(conf, 2),
            "box": [x_min, y_min, x_max, y_max],
        })
    return detections


def build_mask(image_path: str, regions: list[dict], pad: int = 6) -> np.ndarray:
    img_cv = cv2.imread(image_path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    for region in regions:
        x1, y1, x2, y2 = region["box"]
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)

        region_gray = gray[y1:y2, x1:x2]
        text_mask = (region_gray < 180).astype(np.uint8) * 255
        kernel = np.ones((3, 3), np.uint8)
        text_mask = cv2.dilate(text_mask, kernel, iterations=2)
        mask[y1:y2, x1:x2] = np.maximum(mask[y1:y2, x1:x2], text_mask)

    return mask


def inpaint_image(image_path: str, mask: np.ndarray, radius: int = 3) -> np.ndarray:
    img_cv = cv2.imread(image_path)
    return cv2.inpaint(img_cv, mask, radius, cv2.INPAINT_TELEA)


def draw_translations(inpainted_bgr: np.ndarray, regions: list[dict]) -> Image.Image:
    img_pil = Image.fromarray(cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    for region in regions:
        box = region["box"]
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        box_h = box[3] - box[1]

        font_size = max(14, int(box_h * 0.55))
        if "\n" in region["translation"]:
            font_size = max(14, int(box_h * 0.35))

        font_path = FONT_BOLD if region.get("bold") else FONT_REGULAR
        font = ImageFont.truetype(font_path, font_size)
        draw.text((cx, cy), region["translation"], font=font, fill=(0, 0, 0), anchor="mm")

    return img_pil


def translate_image(image_path: str, translation_map: dict, preview: bool = False):
    print(f"[1/4] OCR: detecting text in {image_path}")
    detections = detect_text(image_path)
    print(f"       Found {len(detections)} text regions")

    regions = []
    for det in detections:
        text_lower = det["text"].lower().strip()
        matched = None
        for key, value in translation_map.items():
            if key.lower() in text_lower or text_lower in key.lower():
                matched = value
                break
        if matched:
            regions.append({
                "box": det["box"],
                "original": det["text"],
                "translation": matched["ja"],
                "bold": matched.get("bold", False),
            })
            print(f"       '{det['text']}' → '{matched['ja']}'")
        else:
            print(f"       '{det['text']}' → (skip)")

    if not regions:
        print("No regions to translate.")
        return

    print(f"[2/4] Creating pixel-level mask for {len(regions)} regions")
    mask = build_mask(image_path, regions)

    print("[3/4] Inpainting (removing text, preserving structure)")
    inpainted = inpaint_image(image_path, mask)

    print("[4/4] Drawing Japanese text")
    result = draw_translations(inpainted, regions)

    if preview:
        out_path = image_path.replace(".png", "_jp.png")
        result.save(out_path)
        print(f"Preview saved: {out_path}")
    else:
        result.save(image_path)
        print(f"Overwritten: {image_path}")


# ============================================================
# サンプル: ch13/maet_1301.png (TradFi vs DeFi) の翻訳マッピング
# ============================================================
SAMPLE_MAP = {
    "Prerequisites": {"ja": "前提条件", "bold": True},
    "User": {"ja": "ユーザー", "bold": True},
    "Loan application": {"ja": "融資の申請"},
    "Approvalof theloan": {"ja": "融資の承認"},
    "Approval of the loan": {"ja": "融資の承認"},
    "Overcollateralization": {"ja": "融資の\n過剰担保"},
    "of the loan": {"ja": "過剰担保"},
    "Loan received": {"ja": "融資の受領"},
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate image text EN→JP")
    parser.add_argument("image", help="Path to PNG image")
    parser.add_argument("--preview", action="store_true", help="Save as _jp.png instead of overwriting")
    parser.add_argument("--map", help="JSON file with translation map (default: built-in sample)")
    args = parser.parse_args()

    if args.map:
        with open(args.map) as f:
            tmap = json.load(f)
    else:
        tmap = SAMPLE_MAP
        print("Using built-in sample translation map")

    translate_image(args.image, tmap, preview=args.preview)
