---
name: translation-accuracy
description: 翻訳済みチャプターを原文と照合し、誤訳・意味欠落・未翻訳語・用語不整合を検出する。修正はせずレポートのみ出力
argument-hint: "[chapter-file-path] (例: src/chapter_11.md)"
allowed-tools: Read, Grep, Glob, Bash
---

# 翻訳精度レビュースキル

翻訳済みチャプターを原文（`tmp/chapter_*_orig.md`）と照合し、翻訳精度の問題を検出してレポートする。**修正は行わない。**

## 役割

あなたは英日翻訳のQAレビュアーです。原文の意味が正確に日本語に反映されているかを検証します。文体や読みやすさは対象外（それは `natural-japanese` スキルの担当）。

## 処理手順

### Step 1: 原文の準備

`tmp/` に原文があるか確認する。なければ git history から取得:

```bash
git log --all --oneline -- src/chapter_N.md | tail -3
git show <initial-commit>:src/chapter_N.md > tmp/chapter_N_orig.md
```

### Step 2: Codex原文照合

以下のプロンプトで `codex exec` に委譲する:

```bash
codex exec -s read-only -o /tmp/codex-chN-output.txt "$(cat /tmp/codex-chN-prompt.txt)"
```

プロンプトには以下の検出カテゴリを指定:

1. **mistranslation**: 誤訳（意味が原文と異なる）
2. **missing-content**: 原文の一部が訳出されていない
3. **untranslated-term**: カタカナ化すべき英語がそのまま残っている
4. **glossary-mismatch**: `glosary.md` の用語集と矛盾する訳語

### Step 3: レポート出力

Codexの結果を精査し、以下の形式で報告する:

```
## Ch[N] 翻訳精度レビュー

### HIGH
| 行 | 問題 | 原文 | 修正案 |

### MEDIUM
| 行 | 問題 | 原文 | 修正案 |

### LOW（参考）
| 行 | 問題 | 原文 | 修正案 |
```

## 今日のPRから抽出した頻出パターン

以下は実際の翻訳で発見された問題パターン。レビュー時に重点的にチェックする。

### パターン1: 意味欠落（原文の一部が消える）

原文に含まれる情報が翻訳で落ちるケース。特に関係詞節・副詞句・補足情報。

| 原文 | 誤訳 | 正訳 |
|------|------|------|
| `and trying to find workarounds` | （訳出なし） | `その回避策を模索する` |
| `the last stage: Serenity` | `セレニティの段階` | `最後の段階であるセレニティ` |
| `which is the most likely outcome` | （訳出なし） | `これが最も可能性の高い帰結です` |
| `and the Ethereum protocol` | （訳出なし） | `イーサリアムプロトコルとどう関わるか` |
| `respectively` | （訳出なし） | `それぞれ` |

### パターン2: 構造の曖昧化（英語の修飾関係が崩れる）

`A and B of C` の構造が `A and B` + `of C` に誤解されるケース。

| 原文 | 誤訳 | 正訳 |
|------|------|------|
| `transactions and blocks of verified transactions` | `トランザクションと検証済みトランザクションのブロック` | `トランザクションと、検証済みトランザクションから成るブロック` |
| `a dishonest whitelist creator` | `不正なホワイトリスト作成` | `悪意あるホワイトリスト作成者による不正` |
| `distributed single-state (singleton)` | `分散シングルトン` | `分散された単一状態（シングルトン）` |

### パターン3: カタカナ英語の不統一

同一チャプター内で同じ用語が英語とカタカナで混在。

| 問題 | 修正 |
|------|------|
| `Oracle` と `オラクル` の混在 | 章内で統一（カタカナ優先） |
| `Relayer` と `リレイヤー` の混在 | 同上 |
| `Client` が英語のまま | `クライアント` |
| `Web` が半角英語 | `ウェブ`（カタカナルール） |

### パターン4: 造語・誤訳

日本語として存在しない語や、原文の意味と異なる訳語。

| 原文 | 誤訳 | 正訳 |
|------|------|------|
| `end-of-day pricing` | `日末の価格情報`（造語） | `1日の終わりの価格情報` |
| `Merkle trees with salts` | `マークルパトリシアツリー` | `マークルツリー`（Patriciaは原文にない） |
| `economically bonded` | `経済的に結合` | `経済的担保によって拘束` |
| `powerful aggregation` | `強力な集合体` | `強力な組み合わせ` |
| `near-production environment` | `本番環境` | `準本番環境` |
| `commitment` | `コミットメント` | `取り組み` |

### パターン5: 主語の曖昧化

原文で明示されている主語や行為者が翻訳で消えるケース。

| 原文 | 誤訳 | 正訳 |
|------|------|------|
| `new exploits will be discovered and [TEEs will be] compromised` | `発見され侵害される` | `発見されTEEが侵害される` |
| `(De)centralized Finance` | `分散型（？）金融` | `（非）中央集権型金融` |

## 制約

- **修正しない**: レポートのみ。修正はユーザーの判断を仰いでから
- **文体は対象外**: 読点・接続詞・長文分割は `natural-japanese` スキルの担当
- **用語全体統一は慎重に**: ether/Ether、バリデータ/バリデーター等は書籍全体の方針が必要。1章だけ変えない
