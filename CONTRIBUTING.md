# 貢献ガイド

Mastering Ethereum 日本語翻訳プロジェクトへの貢献を歓迎します。

## 貢献の種類

- **誤訳の修正** — 翻訳内容の誤りを発見した場合
- **用語の提案** — 用語集（`glosary.md`）への追加・修正提案
- **未翻訳章の翻訳** — まだ日本語化されていない章の翻訳
- **画像の日本語化** — 図中のテキストを日本語に置き換え
- **スタイルの改善** — より自然な日本語への改善

## 翻訳ワークフロー

### 1. Issue を確認・作成する

作業前に同じ内容の Issue や PR がないか確認してください。
なければ [Issue テンプレート](.github/ISSUE_TEMPLATE/) を使って Issue を作成してください。

### 2. ブランチを切る

```bash
git checkout main
git pull origin main
git checkout -b fix/chapter-X-mistranslation
```

### 3. 翻訳・修正を行う

翻訳スタイルは [translation-rule.md](translation-rule.md) に従ってください。

**主なルール:**
- 本文: です/ます調
- リスト・引用: である調
- 段落の先頭: 全角スペース（　）
- 用語: [glosary.md](glosary.md) の訳語を使用

### 4. 用語集を更新する

新しい技術用語を翻訳した場合は `glosary.md` に追加してください。
`glosary.md` は Google Sheets と自動同期されます。

### 5. 一貫性チェックを実行する

```bash
python3 scripts/test_consistency.py
```

すべてのテストが通ることを確認してください。

### 6. PR を作成する

[PR テンプレート](.github/pull_request_template.md) に従って PR を作成してください。
CI の consistency-check が green になることを確認してください。

## 翻訳スキル（Claude Code ユーザー向け）

Claude Code を使っている場合、以下のスキルが利用できます：

```
/translate [path]       # 英語章を日本語に翻訳
/natural-japanese [path] # 翻訳後の日本語スタイルを改善
/katakana-fix           # カタカナ複合語のスペースを修正
```

## 運用スクリプト（管理者のみ）

`scripts/sync_spreadsheet.py` と `scripts/reverse_sync_spreadsheet.py` は
Google Sheets との同期スクリプトです。実行には Google サービスアカウントキーが必要で、
**管理者のみが実行できます**。これらは GitHub Actions でも自動実行されます。
