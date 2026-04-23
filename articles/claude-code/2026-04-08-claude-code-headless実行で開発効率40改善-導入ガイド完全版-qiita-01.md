---
id: "2026-04-08-claude-code-headless実行で開発効率40改善-導入ガイド完全版-qiita-01"
title: "Claude Code Headless実行で開発効率40%改善 - 導入ガイド完全版 - Qiita"
url: "https://qiita.com/moha0918_/items/998f0ca62960492a13d4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

Claude Codeを使い始めたチームでよく見られるパターンがあります。最初は対話的に使っていて便利さを実感するものの、「毎回同じレビューを頼むのが手間」「CIに組み込めないか」という壁にぶつかる段階です。

その突破口が **`-p` フラグ（旧headlessモード）** です。Claude Codeをプログラムから呼び出せるようにする機能で、CI/CDパイプラインへの組み込みや定型作業の自動化が実現します。

この記事では、チーム導入の観点から設定テンプレートつきで解説します。

対象読者: Claude Codeをすでに個人利用しており、チームやCI/CDへの展開を検討している方  
前提: `claude` CLIがインストール済みで、`ANTHROPIC_API_KEY` が取得済みであること

## -p フラグとは何か

`claude -p` は、Claude Codeを非対話的に実行するためのフラグです。以前は "headless mode" と呼ばれていました。

```
claude -p "auth.pyのバグを見つけて修正してください" --allowedTools "Read,Edit,Bash"
```

これだけで、Claude Codeが自律的にコードを読んで修正します。対話なし、承認プロンプトなしで完結します。

チームで活用する場面は主に3つです。

* **CI/CDパイプライン**: PRのたびに自動コードレビューやテスト修正
* **定型バッチ処理**: 毎朝のコード品質チェック、ドキュメント生成
* **シェルスクリプト連携**: 既存のgitフックやMakefileへの組み込み

## まずここから：--bare モードを理解する

チームで使うときに最初に覚えておきたいのが `--bare` フラグです。

```
claude --bare -p "このファイルを要約してください" --allowedTools "Read"
```

`--bare` を付けると、**実行環境のローカル設定を一切読み込まない**モードになります。具体的には以下がスキップされます。

* `~/.claude` 以下のフック・スキル設定
* プロジェクトの `.mcp.json`
* 自動メモリ、`CLAUDE.md` の自動探索

なぜこれがチーム運用で重要かというと、**再現性** の問題があるためです。Aさんのローカルには特定のMCPサーバーが設定されていて、Bさんにはない、CIサーバーはまた別の状態、という状況では動作が一致しません。

`--bare` を使えば、どのマシンでも同じ結果が得られます。公式ドキュメントも、スクリプト実行では `--bare` を推奨しており、将来的に `-p` のデフォルトになる予定とされています。

`--bare` モードでは OAuth 認証がスキップされます。`ANTHROPIC_API_KEY` 環境変数か、`--settings` に渡す JSON 内の `apiKeyHelper` で認証する必要があります。

## CI/CD 組み込みテンプレート

### GitHub Actions でのコードレビュー自動化

PRが出るたびに自動でセキュリティレビューを走らせる設定です。

```
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Run Security Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          DIFF=$(gh pr diff ${{ github.event.pull_request.number }})
          REVIEW=$(echo "$DIFF" | claude --bare -p \
            --append-system-prompt "あなたはセキュリティエンジニアです。脆弱性を中心にレビューしてください。日本語で回答してください。" \
            --output-format json \
            --allowedTools "Read" | jq -r '.result')
          
          gh pr comment ${{ github.event.pull_request.number }} --body "## Claude Code レビュー結果
          
          $REVIEW"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`gh pr diff` の出力をパイプで渡して、`--append-system-prompt` でレビュー観点を指示しています。

### テスト自動修正パイプライン

テストが壊れたときに自動修正を試みるジョブです。

```
# .github/workflows/auto-fix-tests.yml
name: Auto Fix Tests

on:
  push:
    branches: [main, develop]

jobs:
  fix-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Check tests
        id: test
        run: npm test || echo "TESTS_FAILED=true" >> $GITHUB_OUTPUT
      
      - name: Auto-fix with Claude Code
        if: steps.test.outputs.TESTS_FAILED == 'true'
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --bare -p "テストスイートを実行して失敗しているテストを修正してください。テストの期待値を変えずに実装側を修正すること。" \
            --allowedTools "Bash,Read,Edit" \
            --output-format json
      
      - name: Commit fixes
        if: steps.test.outputs.TESTS_FAILED == 'true'
        run: |
          git config user.name "Claude Code Bot"
          git config user.email "claude-bot@example.com"
          git add -A
          claude --bare -p "ステージされた変更を確認して適切なコミットメッセージでコミットしてください" \
            --allowedTools "Bash(git diff *),Bash(git log *),Bash(git status *),Bash(git commit *)"
```

ポイントは `--allowedTools` で **git コマンドをホワイトリスト形式で制限**している部分です。

```
--allowedTools "Bash(git diff *),Bash(git log *),Bash(git commit *)"
```

`Bash(git commit *)` は `git commit` で始まるコマンドのみを許可します。`*` の前にスペースが必要な点に注意してください。`Bash(git commit*)` だと `git commit-index` のような予期しないコマンドにもマッチしてしまいます。

## 構造化出力でスクリプト連携を簡単に

`--output-format json` を使うと、レスポンスをJSONで受け取れます。

```
claude --bare -p "このプロジェクトを要約してください" \
  --output-format json | jq -r '.result'
```

さらに `--json-schema` を組み合わせると、スキーマ定義に沿った構造化データを取り出せます。

```
# auth.py から関数名を抽出して JSON 配列で受け取る
claude --bare -p "auth.py にある関数名をすべて抽出してください" \
  --output-format json \
  --json-schema '{
    "type": "object",
    "properties": {
      "functions": {
        "type": "array",
        "items": {"type": "string"}
      }
    },
    "required": ["functions"]
  }' \
  --allowedTools "Read" | jq '.structured_output.functions'
```

これを使えば、「コードの複雑度スコアを数値で返す」「変更が必要なファイルをリスト形式で返す」といった、下流のスクリプトが処理しやすいデータを取り出せます。

## セッション継続で複数ステップの処理を組む

`--continue` と `--resume` を使うと、1つの会話を複数のコマンドにまたがって継続できます。

```
# ステップ1: コードベース全体をレビュー
claude --bare -p "このコードベースのパフォーマンス問題を洗い出してください" \
  --allowedTools "Read,Bash" \
  --output-format json > step1.json

SESSION_ID=$(cat step1.json | jq -r '.session_id')

# ステップ2: 同じセッションでDBクエリに絞る
claude --bare -p "そのなかでデータベースクエリに関連する問題だけに絞ってください" \
  --resume "$SESSION_ID" \
  --output-format json

# ステップ3: サマリーを生成
claude --bare -p "見つかった問題を優先度順にまとめてください" \
  --resume "$SESSION_ID" \
  --output-format json | jq -r '.result'
```

`session_id` を変数に保存しておいて `--resume` に渡すのがポイントです。複数の処理が並行して走っていても、特定のセッションだけを続けられます。

## チーム設定テンプレート集

実際にチームで使い始めるときに役立つ設定ファイルをまとめます。

### settings.json テンプレート（CI用）

```
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Bash(git *)",
      "Bash(npm test)",
      "Bash(npm run lint)"
    ],
    "deny": [
      "Bash(rm *)",
      "Bash(curl *)",
      "Bash(wget *)"
    ]
  }
}
```

`--settings` フラグでこのファイルを渡します。

```
claude --bare -p "テストを修正してください" \
  --settings ./ci/claude-settings.json
```

### Makefile への組み込み例

```
# Makefile
CLAUDE_OPTS = --bare --allowedTools "Read,Bash" --output-format json

.PHONY: review lint-fix summarize

## PR レビュー（BRANCH 変数を指定）
review:
	gh pr diff $(BRANCH) | claude $(CLAUDE_OPTS) \
		--append-system-prompt "コードレビューをしてください。問題点と改善提案を日本語で返してください。" \
		| jq -r '.result'

## lint エラーを自動修正
lint-fix:
	claude --bare -p "lintエラーを修正してください" \
		--allowedTools "Read,Edit,Bash(npm run lint)" \
		--output-format json | jq -r '.result'

## プロジェクトサマリー生成
summarize:
	claude $(CLAUDE_OPTS) -p "このプロジェクトの概要を3段落で説明してください" \
		| jq -r '.result' > SUMMARY.md
```

### ツール許可範囲の早見表

| ユースケース | 推奨 allowedTools | 備考 |
| --- | --- | --- |
| コードレビュー（読み取りのみ） | `Read` | 変更なし。安全に使える |
| テスト修正 | `Read,Edit,Bash` | Bashは無制限。信頼できる環境のみ |
| テスト修正（制限あり） | `Read,Edit,Bash(npm test)` | npm test のみ実行許可 |
| コミット作成 | `Bash(git diff *),Bash(git status *),Bash(git commit *)` | git 操作だけに限定 |
| lint 自動修正 | `Read,Edit,Bash(npm run lint)` | lint コマンドのみ |
| ドキュメント生成 | `Read,Edit` | Bash 不要なことが多い |

## ハマりやすいポイント3つ

**1. 認証エラー**

`--bare` モードでは `~/.claude` の認証情報を読まないため、`ANTHROPIC_API_KEY` が未設定だとエラーになります。CI環境ではシークレットとして必ず登録してください。

**2. ツール未許可による中断**

`--allowedTools` に含まれないツールをClaudeが使おうとすると、処理が止まります。事前に想定されるツールを洗い出しておくか、`--permission-mode acceptEdits` で書き込み系を一括許可する選択肢もあります。ただし `acceptEdits` はシェルコマンドの実行は許可しないため、Bashが必要な場合は別途 `--allowedTools` で指定が必要です。

**3. ストリーム出力の扱い**

`--output-format stream-json` を使う場合、1行ずつJSONオブジェクトが流れてきます。パイプ先で `jq` を使う場合は `-r` と `-j` を組み合わせてトークンを連続表示できます。

```
claude --bare -p "長い説明をしてください" \
  --output-format stream-json \
  --verbose \
  --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

リトライ発生時には `system/api_retry` イベントが流れてくるので、進捗表示やエラーハンドリングに使えます。

## まとめ

`claude -p` は「対話的なAIアシスタント」ではなく「**コードを読んで変更するCLIツール**」として扱うのが正しい視点です。

既存のCI/CDやMakefileと同じように組み込めます。`--bare` で環境依存をなくし、`--allowedTools` で操作範囲を絞り、`--output-format json` でスクリプトと連携する。この3つを押さえるだけで、チーム全員が同じ品質の自動化を使える状態になります。

まず試してみるなら、今あるCIのテストステップの後ろに「失敗時だけClaudeに修正を依頼する」ステップを1つ追加するのが取っ掛かりとしておすすめです。
