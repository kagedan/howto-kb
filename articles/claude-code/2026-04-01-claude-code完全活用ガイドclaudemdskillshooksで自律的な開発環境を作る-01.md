---
id: "2026-04-01-claude-code完全活用ガイドclaudemdskillshooksで自律的な開発環境を作る-01"
title: "Claude Code完全活用ガイド：CLAUDE.md・Skills・Hooksで自律的な開発環境を作る"
url: "https://zenn.dev/devken/articles/claude-code-skills-and-claudemd"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

## はじめに

この記事はClaude Codeを使い始めた方を対象にしています。

「毎回同じ指示をしている」「どこまで自律的に動いてくれるの？」と感じていませんか。

この記事では、Claude Codeを**自分のプロジェクトに最適化し、繰り返し作業を自動化する**ための3つの仕組みを解説します。

* **CLAUDE.md** — Claudeに毎回読ませる指示書
* **Skills** — 再利用可能なカスタムコマンド
* **Hooks** — ツール実行に連動する自動処理

---

## 1. CLAUDE.md：Claudeへの永続的な指示書

### CLAUDE.mdとは

Claude Codeはセッションのたびにコンテキストがリセットされます。その問題を解決するのが `CLAUDE.md` です。

セッション開始時に自動で読み込まれる markdown ファイルで、ここに書いたことが毎回 Claude に伝わります。

### 置き場所と優先度

| 場所 | 適用範囲 |
| --- | --- |
| `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) | 組織全体（管理者が設定） |
| `~/.claude/CLAUDE.md` | 自分のすべてのプロジェクト |
| `./CLAUDE.md` または `./.claude/CLAUDE.md` | そのプロジェクトのみ（チーム共有可） |

優先度：**プロジェクト > 個人 > 組織**（より具体的な場所が優先）

### 効果的な書き方

```
# プロジェクト名

## 開発コマンド
- テスト実行：`npm test`
- ビルド：`npm run build`

## コーディングルール
- インデント：2スペース
- コミット前に必ず `npm test` を実行する
- APIハンドラは `src/api/handlers/` に配置する

## Git運用
- コミットメッセージは日本語で書く
- 機能単位で細かくコミットする
```

**ポイント（[公式ドキュメント](https://code.claude.com/docs/en/memory#write-effective-instructions)より）：**

* 200行以内を目安にする（長すぎると遵守率が下がる）
* 「ちゃんとやる」より「`npm test` を実行する」と具体的に書く
* 矛盾するルールを書かない（2つのルールが競合すると、Claudeがどちらかを任意に選んでしまう）

### ファイルのインポート

`@` 構文で他のファイルを読み込めます。

```
# CLAUDE.md

詳細なAPI設計規約は @docs/api-conventions.md を参照。
個人設定は @~/.claude/my-preferences.md を参照。
```

### ルールの分割管理（`.claude/rules/`）

大規模プロジェクトでは、ルールをファイル別に管理できます。

```
.claude/
├── CLAUDE.md           # メインの指示
└── rules/
    ├── testing.md      # テストのルール
    ├── api-design.md   # API設計のルール
    └── security.md     # セキュリティルール
```

さらに、**特定のファイルを操作するときだけ読み込む**ルールも作れます。

```
---
paths:
  - "src/api/**/*.ts"
---

# APIルール（TypeScriptファイル操作時のみ適用）

- すべてのエンドポイントにバリデーションを追加する
- 標準エラーフォーマットを使用する
```

### Auto Memory

`CLAUDE.md` はあなたが書くものですが、**Auto Memory** はClaudeが自動で書いてくれる学習ノートです。

* ビルドコマンド、デバッグの知見、コードスタイルなど
* `~/.claude/projects/` 以下のプロジェクト別ディレクトリに保存される
* `/memory` コマンドで確認・編集できる

> セッションをまたいで「この前気づいたこと」を覚えていてくれるイメージ

---

## 2. Skills：再利用可能なカスタムコマンド

### Skillsとは

`/コマンド名` で呼び出せる、カスタムのワークフローです。

例えば `/commit` や `/review-pr` のような、**チームで共有できる繰り返し作業の自動化**ができます。

### 基本的な作り方

```
.claude/skills/
└── commit/
    └── SKILL.md   ← これが1つのSkill
```

`SKILL.md` はYAMLフロントマター + Markdownの2部構成：

```
---
name: commit
description: コミットメッセージを自動生成してコミットする
disable-model-invocation: true
---

以下の手順でコミットしてください：

1. `git diff --staged` で変更内容を確認する
2. 変更内容に基づいて日本語のコミットメッセージを作成する
3. `git commit -m "..."` でコミットする
```

### Skillの置き場所

| 場所 | 適用範囲 |
| --- | --- |
| `~/.claude/skills/<name>/SKILL.md` | 自分の全プロジェクト |
| `.claude/skills/<name>/SKILL.md` | そのプロジェクトのみ |

### フロントマターの重要フィールド

| フィールド | 意味 |
| --- | --- |
| `description` | Claudeが自動判断するためのヒント（推奨） |
| `disable-model-invocation: true` | Claudeが自動で呼び出さないようにする（手動専用） |
| `user-invocable: false` | `/メニュー` に表示しない（Claudeだけが呼び出せる） |
| `allowed-tools` | このSkill実行中に許可するツールを制限 |
| `context: fork` | サブエージェントとして独立実行 |
| `agent` | `context: fork` 時に使うエージェント種別（`Explore`、`Plan` など） |
| `model` | このSkill実行中に使うモデルを指定 |
| `effort` | このSkill実行中の思考量（`low`/`medium`/`high`/`max`） |
| `paths` | 特定のファイルパスに一致するときだけ自動適用するグロブパターン |

### 自動トリガーと手動トリガーの使い分け

**自動トリガー（Claudeが判断して使う）**

```
---
name: explain-code
description: コードの仕組みを図解つきで説明する。「これどう動く？」と聞かれたときに使う
---
```

`description` に「どんな場面で使うか」を書いておくと、Claude が文脈に合わせて自動で読み込む。

**手動トリガーのみ（`/deploy` など副作用があるもの）**

```
---
name: deploy
description: 本番環境にデプロイする
disable-model-invocation: true
---
```

`disable-model-invocation: true` をつけると、Claudeが勝手に実行しなくなる。

### 引数を渡す

```
---
name: fix-issue
description: GitHubのIssueを修正する
disable-model-invocation: true
---

Issue #$ARGUMENTS を修正してください。

1. Issueの内容を確認する
2. 修正を実装する
3. テストを書く
4. コミットする
```

`/fix-issue 123` と実行すると `$ARGUMENTS` が `123` に置換される。

### 動的なコンテキスト注入

`` !`コマンド` `` はSKILL.md専用の構文で、Skill実行前にシェルコマンドを実行してその出力を埋め込めます：

```
---
name: pr-summary
description: PRの変更内容をサマリーする
context: fork
---

## PR情報
- 差分: !`gh pr diff`
- コメント: !`gh pr view --comments`

このPRの変更内容をサマリーしてください。
```

---

## 3. Hooks：ツール実行に連動する自動処理

### Hooksとは

Claude Codeの動作の「前後」に任意のシェルコマンドを実行できる仕組みです。

```
ユーザーの入力
  → [UserPromptSubmit Hook]  ← 入力受付直後
  → Claude の処理
    → [PreToolUse Hook]      ← ツール実行前
    → ツール実行
    → [PostToolUse Hook]     ← ツール実行後
    （ツール実行を繰り返す）
  → [Stop Hook]              ← Claude が回答を完了した後
  → レスポンス完了
```

### 設定場所

`.claude/settings.json` または `~/.claude/settings.json` に書きます。基本構造は以下の通りで、キーにはHookイベント名、`matcher` には対象ツール名（正規表現）を指定します：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/format.sh"
          }
        ]
      }
    ]
  }
}
```

### 主要なHookイベント

| イベント | タイミング | 主な用途 |
| --- | --- | --- |
| `UserPromptSubmit` | ユーザー入力の直後 | プロンプトの検証・補足情報の追加 |
| `PreToolUse` | ツール実行前 | 危険なコマンドのブロック |
| `PostToolUse` | ツール実行後 | フォーマット、Lint の自動実行 |
| `Stop` | Claudeが回答を終えた後 | 完了条件の検証 |

### 実用例①：ファイル保存後に自動フォーマット

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_FILE_PATHS\""
          }
        ]
      }
    ]
  }
}
```

`$CLAUDE_FILE_PATHS` はClaude Codeが操作したファイルパスが自動でセットされる環境変数です。

### 実用例②：危険なコマンドをブロック

2つのファイルを用意します。

**① `.claude/hooks/block-dangerous.sh`（実際の判定ロジック）：**

```
#!/bin/bash
# Claude Code は Hook スクリプトに JSON をstdinで渡す
# jq でコマンド文字列だけ取り出す
COMMAND=$(cat | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -qE 'rm -rf|DROP TABLE'; then
  echo "危険なコマンドはブロックされました" >&2
  exit 2  # exit 2 = Claudeにエラーとして伝える
fi

exit 0  # 許可
```

**② `.claude/settings.json`（どのツールにHookを適用するか）：**

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/block-dangerous.sh"
          }
        ]
      }
    ]
  }
}
```

### 終了コードの意味

| 終了コード | 動作 |
| --- | --- |
| `0` | 成功・処理を続行 |
| `2` | Claudeにエラーとして伝え、処理をブロックする |
| `1`など（それ以外） | Hookの実行エラーとして記録されるが、処理は続行される |

### Skillの中でHooksを定義する

Skill専用のHookをフロントマターに書ける。これにより、そのSkillが実行されているときだけ有効になるHookを定義できる：

```
---
name: secure-deploy
description: セキュリティチェック付きでデプロイする
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

---

## 4. 組み合わせで「自律的な環境」を作る

CLAUDE.md、Skills、Hooksを組み合わせると、Claude Codeが「自分で判断して動く」環境になります。

### 構成例：自律的なコードレビュー環境

```
.claude/
├── CLAUDE.md              # 常時：コーディング規約、チームルール
├── rules/
│   └── api.md             # APIファイル操作時のみ：API規約
├── skills/
│   ├── review-pr/
│   │   └── SKILL.md       # /review-pr：PRレビューを自動化
│   └── commit/
│       └── SKILL.md       # /commit：コミットを自動化（手動のみ）
└── settings.json          # Hooks：保存後に自動フォーマット
```

**流れ：**

1. Claudeが `CLAUDE.md` を読んでプロジェクトルールを把握
2. APIファイルを編集するとき `rules/api.md` が自動で読み込まれる
3. ファイル保存のたびに Hook が走り自動フォーマット
4. `/commit` で手動トリガーのSkillが起動、日本語コミットを作成
5. 「この記事レビューして」と言うと `review-article` Skillが自動で起動

---

## まとめ

| 機能 | 何をするか | いつ使うか |
| --- | --- | --- |
| **CLAUDE.md** | Claudeへの常時指示 | プロジェクトルール、コーディング規約 |
| **Skills** | 再利用可能なコマンド | 繰り返す作業、チームで共有したいワークフロー |
| **Hooks** | 自動処理のトリガー | フォーマット、検証、危険コマンドのブロック |

この3つを使いこなすと、「毎回同じことを指示する」から卒業できます。

なお、CLAUDE.mdと似た仕組みとして複数のAIツール共通の **AGENTS.md** という標準もあります。Gemini CLIやCursorなど複数ツールを使う場合は「[AGENTS.md完全ガイド：Claude Code・Gemini CLI・Cursorを1ファイルで統一管理する](https://zenn.dev/kentaro_and_dev/articles/agents-md-ai-cli-guide)」も参照してください。

---

## 参考
