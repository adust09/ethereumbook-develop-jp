---
name: translate-image
description: 画像内の英語テキストを日本語に翻訳する。OCR + Inpainting で元画像のレイアウトを完全に維持し、テキスト部分のみを差し替える
user_invocable: true
---

# Image Translation Skill

ダイアグラム画像内の英語テキストを日本語に翻訳して差し替えるスキル。
OCR（EasyOCR）でテキスト領域を自動検出し、OpenCV の Inpainting で背景を自然に復元してから、日本語テキストを描画する。

## Usage

```
/translate-image <image_path>
/translate-image src/images/ch11/maet_1101.png
/translate-image ch11          # ch11の全画像を処理
```

## Prerequisites

Python venv にライブラリが必要。なければ自動セットアップ:
```bash
python3 -m venv /tmp/imgtools
/tmp/imgtools/bin/pip install Pillow opencv-python-headless easyocr
```

## Approach: OCR + Inpainting

### Why this approach?

元画像は Adobe Photoshop で作成された PNG（ソースファイル非公開）。
テキスト部分だけを差し替えるために以下の3ステップで処理する:

1. **OCR**: EasyOCR が全テキストの位置・内容を自動検出（手動座標不要）
2. **Inpainting**: テキストピクセルのみをマスクし、OpenCV が背景を自然に復元（矢印・枠線を壊さない）
3. **Overlay**: 復元された背景の上に日本語テキストを描画

### Key advantage

矢印、点線、ボックス枠、アイコンなどの構造要素が自動的に保存される。
従来の矩形塗りつぶし方式では構造要素が消えてしまう問題を根本的に解決。

## Workflow

### Step 1: OCR でテキスト検出

```python
import easyocr
reader = easyocr.Reader(['en'], gpu=False)
results = reader.readtext(image_path)
# results: [(bbox, text, confidence), ...]
```

### Step 2: 翻訳マッピングを作成

1. OCR 結果を Claude のビジョンで確認（Read ツール）
2. 各テキストの日本語訳を決定
3. `src/glosary.md` を参照して用語を統一

ルール:
- 技術用語のカタカナ: "Oracle" → "オラクル", "Smart contract" → "スマートコントラクト"
- 固有名詞: そのまま（"AWS", "IPFS", "ENS", "Vercel", "TradFi", "DeFi"）
- 矢印ラベル: 自然な日本語（"Read" → "読み取り", "Loan application" → "融資の申請"）
- OCR が複数行を別テキストとして検出した場合: マージして1つの翻訳にする

### Step 3: ピクセルレベルマスク + Inpainting

```python
import cv2, numpy as np

img_cv = cv2.imread(src_path)
gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
mask = np.zeros(gray.shape, dtype=np.uint8)

for region in regions_to_translate:
    x1, y1, x2, y2 = region["box"]
    # テキストピクセルのみマスク（暗いピクセル = テキスト）
    region_gray = gray[y1:y2, x1:x2]
    text_mask = (region_gray < 180).astype(np.uint8) * 255
    # アンチエイリアス端をカバーするために膨張
    kernel = np.ones((3, 3), np.uint8)
    text_mask = cv2.dilate(text_mask, kernel, iterations=2)
    mask[y1:y2, x1:x2] = np.maximum(mask[y1:y2, x1:x2], text_mask)

# Inpainting（TELEA法、半径3）
inpainted = cv2.inpaint(img_cv, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
```

### Step 4: 日本語テキスト描画

```python
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

img_pil = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
draw = ImageDraw.Draw(img_pil)

for region in regions_to_translate:
    box = region["box"]
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    box_h = box[3] - box[1]
    font_size = max(14, int(box_h * 0.55))
    font = ImageFont.truetype(font_path, font_size)
    draw.text((cx, cy), region["translation"], font=font, fill=(0,0,0), anchor="mm")
```

### Step 5: レビュー

1. 翻訳画像を Read ツールで表示
2. 元画像と比較して確認:
   - 全テキストが正しく翻訳されている
   - 矢印・枠線・アイコンが保存されている
   - テキストが適切にセンタリングされている
   - Inpainting のアーティファクトがない
3. 問題があれば翻訳マッピングやフォントサイズを調整して再実行

### Step 6: 保存

元ファイルを上書き保存:
```python
img_pil.save(original_path)
```

## サンプルスクリプト

`scripts/translate_image.py` に実用的なサンプルスクリプトを用意。
使い方: `/translate-image` スキル実行時にこのスクリプトをベースにする。

## 翻訳不要な画像

以下はスクリーンショットのため翻訳不要:
- ch2: 全26枚（MetaMask, Etherscan, Remix, Faucet の UI キャプチャ）
- ch12: maet_1204〜1212（Scaffold-ETH, Vercel 等の UI キャプチャ）

## 翻訳対象の画像（18枚）

| 章 | ファイル | 内容 |
|---|---|---|
| ch1 | maet_0101 | Execution client / Consensus client 構成図 |
| ch3 | maet_0301 | Ethereum node + Web3 library 構成図 |
| ch11 | maet_1101〜1105 | Oracle / クロスチェーン図（5枚） |
| ch12 | maet_1201〜1203, 1213 | DApp アーキテクチャ図（4枚） |
| ch13 | maet_1301〜1307 | DeFi フロー図（7枚） |
