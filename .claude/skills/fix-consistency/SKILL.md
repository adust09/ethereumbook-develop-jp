# Fix Consistency

翻訳チャプターの一貫性テスト（`scripts/test_consistency.py`）を実行し、失敗箇所を自動修正する。

## Triggers

- `/fix-consistency`

## Instructions

以下の手順を実行してください。

### 1. テスト実行

```bash
python3 scripts/test_consistency.py
```

### 2. 失敗があれば修正スクリプトを実行

引数が指定されている場合はそのファイルのみ、なければ失敗したファイルを対象にする。

```bash
python3 scripts/fix_consistency.py src/chapter_N.md
```

修正内容:
- **用語の統一**: `test_consistency.py` の `VARIANT_MAP` に定義された表記ゆれを正規形に置換（例: バリデーター→バリデータ、仮想通貨→暗号通貨）
- **段落先頭の全角スペース**: 日本語で始まる段落行の先頭に全角スペース（U+3000）を追加

### 3. テスト再実行で確認

```bash
python3 scripts/test_consistency.py
```

全テストがパスすることを確認して結果を報告する。

### Notes

- `VARIANT_MAP` が `test_consistency.py` と `fix_consistency.py` の両方に定義されている。新しい用語を追加する場合は両方を更新すること。
- `--all` オプションで全チャプターを一括修正できるが、意図しない変更を避けるため対象ファイルを明示するのが望ましい。
