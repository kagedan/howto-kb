---
id: "2026-06-08-claude-codeを部品として使うclaude-p-コマンドの使い方とユースケース5選-01"
title: "Claude Codeを「部品」として使う｜claude -p コマンドの使い方とユースケース5選"
url: "https://qiita.com/satoshi_061/items/f30a6c2067a066b14d04"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "qiita"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

## はじめに

`claude -p` は Claude Code の**非対話型ワンショット実行モード**です。

通常の `claude` コマンドと何が違うのか、一言で言うと「**Claudeをツールチェーンの部品として使える**」ところです。

この記事では、`claude -p` の基本からCI/CDへの組み込みまで、実際のユースケースを交えて解説します。`git diff | claude -p "レビューして"` から試せます。

---

## TL;DR

- `claude -p` はプロンプトを渡して結果を返すだけの1回完結モード
- `git diff | claude -p "レビューして"` が最もシンプルな使い方
- CI/CDやシェルスクリプトへの組み込みに最適
- `--allowedTools` で権限を絞るのが安全な使い方
- インタラクティブなレビューには `/code-review` の方が便利
- **2026/6/15〜 `claude -p` はサブスク枠とは別のクレジット制に移行**

---

## 基本構文

```bash
claude -p "質問やタスク"
```

`-p` は `--print` の略で、プロンプトを渡してレスポンスを出力し、すぐに終了します。

### 通常モードとの違い

| | 通常モード | `-p` モード |
|---|---|---|
| 対話性 | 複数ターンの会話 | 1回実行して終了 |
| 用途 | 開発中の探索・修正 | スクリプト・自動化 |
| 向いている場面 | 試行錯誤・深掘り | 繰り返し・他ツール連携 |

---

## なぜ使うのか？

**「Claudeを部品として使える」**ところに尽きます。

```bash
# 他のコマンドとパイプで繋げる
git diff | claude -p "このdiffをレビューして"
tail -f app.log | claude -p "エラーの原因を教えて"

# 出力をJSONで受け取って次の処理に流す
claude -p "依存関係の問題を分析して" --output-format json | jq '.issues[]'
```

通常の `claude` はインタラクティブに使うもの。`claude -p` は**自動化のための道具**です。

---

## ユースケース5選

### 1. Git との連携

```bash
# 差分をレビューさせる
git diff | claude -p "このdiffのセキュリティ問題を指摘して"

# ステージした変更からコミットメッセージを生成
git diff --cached | claude -p "コミットメッセージを作って。メッセージだけ返して"

# PRの説明文を自動生成
gh pr diff | claude -p "PRの説明文を書いて"
```

`git diff | claude -p` は最もシンプルで効果的なパターンです。まずここから試してみてください。

---

### 2. ログ・ファイル解析

```bash
# エラーログの診断
tail -100 app.log | claude -p "エラーの原因を教えて" > analysis.txt

# コードの説明
cat auth.ts | claude -p "この関数が何をしているか説明して"

# Dockerfile のセキュリティチェック
claude -p "セキュリティ問題がないか確認して" < Dockerfile
```

ファイルを丸ごと渡してClaudeに解析させることができます。

---

### 3. CI/CD への組み込み（GitHub Actions）

```yaml
- name: コードレビュー
  run: |
    gh pr diff ${{ github.event.pull_request.number }} | \
      claude -p "セキュリティと品質の観点でレビューして" \
      --output-format json | jq -r '.result' > review.txt

- name: PRにコメント投稿
  run: gh pr comment $PR_NUMBER --body "$(cat review.txt)"
```

PRが作成されるたびに自動でレビューコメントを投稿する、という仕組みが作れます。

---

### 4. シェルスクリプトでの自動化

```bash
# テスト失敗時に修正案を出す
TEST_OUTPUT=$(npm test 2>&1 || true)
echo "$TEST_OUTPUT" | claude -p "テスト失敗の原因と修正案を教えて"

# リリースノートを自動生成
LAST_TAG=$(git describe --tags --abbrev=0)
git log ${LAST_TAG}..HEAD --oneline | \
  claude -p "Features・Bug Fixes・Improvementsに分類して" \
  >> RELEASE_NOTES.md
```

定型的な作業の自動化に向いています。

---

### 5. JSON出力で後続処理に流す

```bash
cat report.txt | \
  claude -p "問題点を抽出して" --output-format json | \
  jq -r '.result'
```

### 出力フォーマットの選択肢

| オプション | 説明 |
|---|---|
| `--output-format text` | テキスト（デフォルト） |
| `--output-format json` | 構造化出力、後続処理に最適 |
| `--output-format stream-json` | リアルタイムストリーミング（`--verbose` と併用） |

---

## 権限確認の扱い方

`claude -p` はデフォルトでも権限確認があります。ただし非対話モードなので、確認が出ると**処理がブロック**されます。

### 推奨: `--allowedTools` で必要なツールだけ指定

```bash
# 使うツールを明示的に指定 → そのツールは確認なしで実行
claude -p "差分をレビューして" \
  --allowedTools "Bash(git *),Read"
```

### その他の権限モード

```bash
# 編集系は自動許可
claude -p "タスク" --permission-mode acceptEdits

# すべて自動許可
claude -p "タスク" --permission-mode dontAsk

# 全権限確認をスキップ（本番環境では非推奨）
claude -p "タスク" --dangerously-skip-permissions
```

`--dangerously-skip-permissions` は名前の通り危険なので、信頼できるスクリプトの中だけで使ってください。

---

## CI/CD 向け推奨の組み合わせ

```bash
claude --bare \
  -p "タスク内容" \
  --output-format json \
  --max-turns 5 \
  --allowedTools "Bash(git *),Read,Edit" \
  --max-budget-usd 10.00
```

| フラグ | 目的 |
|---|---|
| `--bare` | 高速起動（コンテキスト読み込みスキップ） |
| `--output-format json` | 後続処理で解析しやすい |
| `--max-turns` | 暴走防止 |
| `--allowedTools` | 権限を最小限に絞る |
| `--max-budget-usd` | コスト上限設定 |

---

## 【2026年6月15日〜】料金体系の変更に注意

`claude -p` を使う前に知っておきたい重要な変更があります。

**2026年6月15日から、`claude -p` などの自動化・エージェント系利用がサブスク枠とは別のクレジット制に切り分けられます。**

> [Use the Claude Agent SDK with your Claude plan | Claude Help Center](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)

### 何が変わるのか

| 利用方法 | 6/15以降の扱い |
|---|---|
| claude.ai チャット | 従来通りサブスク枠 |
| ターミナル・IDEの通常 Claude Code | 従来通りサブスク枠 |
| **`claude -p`（非対話モード）** | **別クレジット枠** |
| Agent SDK / GitHub Actions | 別クレジット枠 |

### プラン別のクレジット付与量（月次）

| プラン | 月額 | 月次クレジット |
|---|---|---|
| Pro | $20 | $20相当 |
| Max 5x | $100 | $100相当 |
| Max 20x | $200 | $200相当 |

### 注意点

- クレジットは**月末リセット**（ロールオーバーなし）
- チームメンバーとの**共有・プール不可**（個人単位）
- クレジットを使い切ると、次の課金サイクルまで自動化機能が停止

### 実際の影響は？

Proプランで `claude -p` を使う場合、月$20分のトークン消費が上限になります。単純なgit diffレビューやログ解析程度なら十分ですが、大規模ファイルの解析やCI/CDで頻繁に実行するケースでは注意が必要です。

---

## `/code-review` との使い分け

「`claude -p` でコードレビューできるなら、`/code-review` コマンドはいらなくない？」と思うかもしれません。**用途が違います。**

| シーン | 使うもの |
|---|---|
| 手動でコードレビューしたい | `/code-review` |
| PRに自動でコメントしたい | `/code-review --comment` |
| 深掘りレビューしたい | `/code-review ultra` |
| CI/CDやgit hookで自動実行したい | `claude -p` |
| 独自の観点でレビューしたい | `claude -p "〇〇の観点で..."` |

**インタラクティブなレビューなら `/code-review` の方が断然便利**です。`claude -p` はあくまで「自動化のための道具」として使い分けましょう。

---

## まとめ

- `claude -p` は「Claudeをコマンドラインツールとして使う」ためのフラグ
- `git diff | claude -p` から始めるのが一番シンプル
- CI/CDに組み込む場合は `--allowedTools` で権限を絞るのが安全
- インタラクティブなレビューには `/code-review` の方が向いている
- `--output-format json` と `jq` の組み合わせで柔軟な後続処理が可能
- **2026/6/15〜 自動化利用は別クレジット枠に移行（Pro=$20/月が上限）**

Claude Codeを「対話相手」としてだけでなく「自動化の部品」として使えると、日常の反復作業が一気に楽になります。

---

## 参考

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/ja/docs/claude-code/overview)
- [Claude Code CLI リファレンス](https://docs.anthropic.com/ja/docs/claude-code/cli-reference)
- [Use the Claude Agent SDK with your Claude plan | Claude Help Center](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
