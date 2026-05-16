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
```

実行は基本的に「翻訳マップ JSON」を作ってからスクリプトを叩く:

```bash
/tmp/imgtools/bin/python3 scripts/translate_image.py \
    src/images/ch11/maet_1102.png --map maps/maet_1102.json
```

## Prerequisites

Python venv にライブラリが必要。なければ自動セットアップ:
```bash
python3 -m venv /tmp/imgtools
/tmp/imgtools/bin/python3 -m pip install Pillow opencv-python-headless easyocr
```

### 日本語フォント

スクリプトは次の優先順位でフォントを解決する:

1. 環境変数 `IMG_FONT_BOLD` / `IMG_FONT_REGULAR`（TTF/OTF/TTC への絶対パス）
2. OS 別デフォルト
   - macOS: ヒラギノ角ゴシック W6 / W3 (`/System/Library/Fonts/...`)
   - Linux: Noto Sans CJK JP Bold / Regular (`/usr/share/fonts/...`)
3. `fc-match` (fontconfig) によるファミリー名解決（`Noto Sans CJK JP`）

Linux / CI で実行する場合は Noto を導入する:
```bash
sudo apt-get install -y fonts-noto-cjk fontconfig  # Debian/Ubuntu
```

別フォントを使う場合は env で上書き:
```bash
IMG_FONT_REGULAR=/path/to/regular.otf \
IMG_FONT_BOLD=/path/to/bold.otf \
/tmp/imgtools/bin/python3 scripts/translate_image.py ...
```

## Approach: OCR + Inpainting

1. **OCR**: EasyOCR が全テキストの位置・内容を自動検出
2. **Mask (連結成分フィルター)**: 各 OCR bbox 内の「文字形状の連結成分」だけマスクし、横長/縦長/極端なアスペクト比の連結成分（= 矢印・枠線・直線）はマスクから除外して保護する
3. **Inpainting**: OpenCV TELEA でテキスト部分の背景を復元
4. **Border Restoration**: 原本の枠線・矢印ピクセル（gray < 100）を inpainting 後の画像に上書き復元する。OCR テキスト bbox（+8px padding）内は除外して英文残骸の混入を防ぐ
5. **Overlay**: 復元された背景の上に日本語テキストを描画

### 旧版（v1）の問題と v2 の対応

| 旧版 v1 の問題 | v2 の対応 |
|---|---|
| `gray < 180` を bbox 全体に適用していたため bbox 内に侵入した枠線・矢印まで削除されていた | 連結成分の幅/高さ/アスペクト比で線形オブジェクトを検出して除外 |
| `pad=6` + `dilate iterations=2` で広範囲を侵食 | `pad=2` + `dilate iterations=1` に縮小 |
| OCR bbox 高さ依存でフォントサイズを個別計算 → 隣接ラベル間でサイズがバラバラ | 翻訳マップで `font_size` 明示指定 or `size_group` で同グループを統一 |

## 翻訳マップ JSON の仕様

```json
{
  "Original Text": {
    "ja": "翻訳テキスト",
    "bold": true,
    "font_size": 22,
    "size_group": "steps",
    "group": "step1",
    "text_offset_x": 10,
    "text_offset_y": -5
  },
  "Web3": {"ja": null},
  "__extra_mask_boxes__": [[x1, y1, x2, y2]],
  "__extra_mask_boxes_soft__": [[x1, y1, x2, y2]],
  "__extra_preserve_boxes__": [[x1, y1, x2, y2]]
}
```

### テキストフィールド

| フィールド | 用途 |
|---|---|
| `ja` | 翻訳テキスト。`null` を指定すると preserve（マスクから除外、原文を残す） |
| `bold` | true で Bold ウェイト、それ以外は Regular。実フォントは Prerequisites の解決順序で決まる |
| `font_size` | フォントサイズの明示指定。指定すると自動縮小も無効化される |
| `size_group` | 同 group 名の region は bbox 高さの中央値でフォントサイズを統一 |
| `group` | OCR が分割検出した断片を 1 つの翻訳としてマージ（`ja` を持つ要素が代表） |
| `text_offset_x` | 描画位置の水平オフセット（px）。正で右、負で左にずらす |
| `text_offset_y` | 描画位置の垂直オフセット（px）。正で下、負で上にずらす |

### 特殊キー（マスク制御）

| キー | 用途 |
|---|---|
| `__extra_mask_boxes__` | 指定領域を無条件で全マスク + inpaint 後に周辺中央値で塗装。テキスト残骸やタイトルバンドの除去に使う |
| `__extra_mask_boxes_soft__` | 指定領域を連結成分フィルター付きでマスク。枠線を保護しつつテキストだけ消したい場合に使う |
| `__extra_preserve_boxes__` | 指定領域をマスクから強制除外。OCR bbox と重なる枠線・矢印を保護する |

### マッチング順序

1. **完全一致**（大文字小文字無視）が最優先
2. 次に `*` を含むキーで `fnmatch` グロブマッチ
3. それ以外は skip（ログ出力のみ）

## Workflow

### Step 1: OCR でテキスト検出を確認

```bash
/tmp/imgtools/bin/python3 -c "
import easyocr
r = easyocr.Reader(['en'], gpu=False, verbose=False)
for bbox, text, conf in r.readtext('src/images/ch11/maet_1102.png'):
    print(repr(text), round(conf, 2))
"
```

### Step 2: 翻訳マップを作成

1. OCR 結果と画像を見比べて全テキストの翻訳を決める
2. `src/glosary.md` を参照して用語を統一
3. ステップ番号付きラベル（1., 2., 3., ...）には同じ `font_size` を指定して統一
4. OCR が複数行を別テキストとして検出した場合は `group` でマージ
5. 残したい英語（"Web3", "P2P", "AWS" 等）は `"ja": null` で preserve

### Step 3: 実行 → レビュー → 調整

```bash
/tmp/imgtools/bin/python3 scripts/translate_image.py \
    src/images/ch11/maet_1102.png --map maps/maet_1102.json --preview
```

レビュー観点:
- 全テキストが正しく翻訳されている
- 矢印・枠線・アイコンが保存されている（特に bbox 内に侵入していた線）
- 番号付きラベル群でフォントサイズが揃っている
- Inpainting のかすれ跡がない（残っていれば連結成分フィルターの閾値を緩和）

問題があれば翻訳マップ（`font_size`、`group`、`preserve` 指定）を調整して再実行。

### Step 4: 上書き保存

`--preview` を外して再実行すると元ファイルを上書き。

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

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| 矢印・枠線が灰色化 / 消失 | bbox 内の線が連結成分フィルターで除外されない | `aspect > 8` を `> 5` に厳しくする、または `pad` を 0 に |
| 枠線がボケている / 太さが変わる | inpainting がテキスト近傍の枠線まで平滑化した | `restore_borders()` が自動復元するが、OCR bbox と枠線が重なる場合は `__extra_preserve_boxes__` で枠線座標を明示保護する |
| テキスト残骸の黒いドットが残る | 連結成分フィルターの最小面積閾値 (area < 3) で除外された微小ピクセル | `__extra_mask_boxes__`（unconditional）で該当領域を強制マスクする。`__extra_mask_boxes_soft__` では消えない |
| 翻訳テキストが矢印や枠線に被る | 日本語テキストが英語より長く、描画位置が重なる | `text_offset_x` / `text_offset_y` で位置調整、または `font_size` を縮小する |
| 番号 (1. 2. 3.) のサイズがバラバラ | OCR 検出ごとに個別計算されている | 翻訳マップで `font_size` 明示 or `size_group` で統一 |
| 一部の OCR が拾えない (例: 数字 "4") | EasyOCR の検出漏れ | 該当領域に `preserve` boxを与えるか、隣接テキストとまとめて bbox 拡張 |
| 翻訳が反映されない | OCR テキストとマップキーが一致していない | OCR 結果の repr を確認（半角/全角、ハイフン、コンマの違い） |
