---
id: "2026-03-21-claude-codeを手懐ける-claudemdhooksskillsmcpによるカスタマイズ戦略-01"
title: "Claude Codeを手懐ける — CLAUDE.md・Hooks・Skills・MCPによるカスタマイズ戦略"
url: "https://zenn.dev/76hata/articles/claude-code-customization-ecosystem"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "zenn"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## はじめに

Claude Codeはターミナルで動くAIコーディングエージェントだ。インストールして `claude` と打てばすぐに使える。しかし、素の状態で使い続けるのはもったいない。

Claude Codeには4つのカスタマイズレイヤーがある。**CLAUDE.md**、**Hooks**、**Skills**、**MCP** だ。これらを組み合わせることで、「チームの規約を守らせる」「危険な操作をブロックする」「定型作業をワンコマンドで実行する」「外部サービスと連携する」といったことが実現できる。

この記事では、各レイヤーの役割と使いどころを整理し、実際のプロジェクトでどう組み合わせるかを解説する。

## 全体像：4つのカスタマイズレイヤー

まず全体像を押さえよう。

| レイヤー | 役割 | 設定場所 | 共有範囲 |
| --- | --- | --- | --- |
| CLAUDE.md | プロジェクトの規約・ルール・コンテキストを伝える | リポジトリルート | チーム全体（git管理） |
| Hooks | ツール実行前後にシェルコマンドを自動実行 | `.claude/settings.json` | チームまたは個人 |
| Skills | スラッシュコマンドで呼び出せる定型ワークフロー | `.claude/skills/` | チーム全体（git管理） |
| MCP | 外部サービス（Slack, Notion, DB等）との接続 | `.mcp.json` 等 | プロジェクト単位 |

それぞれ見ていく。

## レイヤー1：CLAUDE.md — AIへの指示書

CLAUDE.mdはClaude Codeがセッション開始時に最初に読むファイルだ。プロジェクトのルール、コーディング規約、アーキテクチャの方針をここに書く。

### 設定のスコープ

Claude Codeの設定にはスコープがある。CLAUDE.mdも同様だ。

| スコープ | 場所 | 影響範囲 |
| --- | --- | --- |
| User | `~/.claude/CLAUDE.md` | 全プロジェクト共通の個人設定 |
| Project | リポジトリルートの `CLAUDE.md` | チーム共有（gitにコミット） |
| Local | `.claude/CLAUDE.local.md` | 自分だけ（gitignored） |

### 効果的なCLAUDE.mdの書き方

CLAUDE.mdで重要なのは **具体的な指示** を書くことだ。「きれいなコードを書いてください」のような曖昧な指示は意味がない。

```
# CLAUDE.md

## 技術スタック
- 言語: TypeScript (strict mode)
- ランタイム: Bun
- フレームワーク: Hono
- DB: PostgreSQL + Drizzle ORM

## コーディング規約
- パッケージ追加は `bun add` を使う（npm/yarn禁止）
- テストは Vitest で書く
- エラーハンドリングは Result 型パターンを使う

## 開発フロー
1. 実装前に tasks/todo.md を確認する
2. 実装完了後、/code-review を実行する
3. テストが全て通ることを確認してからコミットする
```

### CLAUDE.md + ドキュメント駆動

CLAUDE.md単体ではなく、補助ドキュメントと組み合わせるパターンが実践では有効だ。

| ファイル | 役割 |
| --- | --- |
| `CLAUDE.md` | 何を読むか、どう振る舞うかの指示 |
| `tasks/todo.md` | 残タスクの管理（セッション間の引き継ぎ） |
| `tasks/lessons.md` | 過去の失敗と学び（同じバグを踏まない） |

CLAUDE.mdに「セッション開始時は `tasks/todo.md` を読んで状況を把握せよ」と書いておけば、コンテキストウィンドウをリセットしても作業を継続できる。

## レイヤー2：Hooks — イベント駆動の自動処理

Hooksは、Claude Codeの特定のイベントに応じてシェルコマンドを自動実行する仕組みだ。CLAUDE.mdが「お願い」なら、Hooksは「強制」に近い。

### 主要なHookイベント

| イベント | タイミング | 用途 |
| --- | --- | --- |
| `PreToolUse` | ツール実行前 | 危険な操作のブロック |
| `PostToolUse` | ツール実行後 | Lint・Format の自動実行 |
| `Stop` | 応答完了時 | 通知の送信 |
| `SessionStart` | セッション開始時 | 環境チェック |

`.claude/settings.json` に以下のように設定する。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "bash -c 'if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE \"npm |npx \"; then echo \"BLOCK: bun を使ってください\" >&2; exit 1; fi'"
      },
      {
        "matcher": "Edit",
        "command": "bash -c 'if echo \"$CLAUDE_TOOL_INPUT\" | grep -q \"package.json\"; then echo \"BLOCK: bun add/remove を使ってください\" >&2; exit 1; fi'"
      }
    ]
  }
}
```

この設定により、Claude Codeが `npm install` を実行しようとすると自動的にブロックされ、`bun add` を使うよう促される。CLAUDE.mdに「npmは使わないで」と書くだけでは無視されることがあるが、Hooksなら確実に止められる。

### PostToolUseでフィードバックサイクルを短くする

ファイル編集後に自動で Lint と型チェックを走らせるパターンも有効だ。

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "bash -c 'bun run lint --fix && bun run typecheck'"
      }
    ]
  }
}
```

これにより、Claude Codeが編集するたびに即座にフィードバックが返り、問題を小さいうちに修正できる。

## レイヤー3：Skills — 再利用可能なワークフロー

Skillsは、`.claude/skills/{スキル名}/SKILL.md` にMarkdownファイルを配置するだけで使えるカスタムスラッシュコマンドだ。

### SKILL.mdの構造

```
---
name: code-review
description: コードレビューを実行し、問題点をレポートする
---

# コードレビュースキル

## 手順
1. `git diff main...HEAD` で変更差分を取得する
2. 以下の観点でレビューする:
   - セキュリティ（OWASP Top 10）
   - パフォーマンス（N+1クエリ、不要な再レンダリング）
   - 保守性（関数の責務分離、命名）
3. 問題があればファイル名と行番号付きで指摘する
4. 重要度（Critical / Warning / Info）を付与する
```

`/code-review` と入力するだけで、上記の手順が自動実行される。

### マルチエージェントでスキルを並列実行

複数のレビュースキルを用意しておき、CLAUDE.mdの開発フローに組み込むパターンもある。

各レビュアーは独立したサブエージェントとして並列実行されるため、単一のレビュアーに全観点を任せるより高速かつ精度が高い。

## レイヤー4：MCP — 外部サービス連携

MCP（Model Context Protocol）は、AIツールを外部データソースに接続するオープン標準だ。MCPサーバーを追加することで、Claude CodeからSlack、Notion、データベースなどに直接アクセスできるようになる。

### MCPサーバーの追加

```
# HTTP経由のMCPサーバー追加（推奨）
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# stdio経由のMCPサーバー追加
claude mcp add --transport stdio my-db-server -- node ./mcp-server.js
```

追加後、Claude Code内で `/mcp` を実行すると接続状態を確認できる。

### 活用パターン

MCPの真価は「ツールの集約」にある。従来は目的ごとに別のツールを開いていた作業を、Claude Code一箇所に集約できる。

| 従来 | MCP連携後 |
| --- | --- |
| Slackを開いてメッセージ確認 | Claude Code内でSlack MCPから取得 |
| Notionを開いてドキュメント参照 | Claude Code内でNotion MCPから取得 |
| psqlでDB確認 | Claude Code内でDB MCPから取得 |
| Sentryでエラー確認 | Claude Code内でSentry MCPから取得 |

コンテキストスイッチのコストが減り、「調べて → 考えて → 実装する」のサイクルがClaude Code内で完結する。

## 設定のスコープを使い分ける

Claude Codeの設定には明確なスコープ階層がある。これを理解しておかないと、個人設定がチームに影響したり、逆にチーム設定が効かなかったりする。

| スコープ | 場所 | 共有 | 用途 |
| --- | --- | --- | --- |
| Managed | サーバー管理設定 | 組織全体 | セキュリティポリシーの強制 |
| User | `~/.claude/` | 個人のみ | 個人の好みやAPIキー |
| Project | `.claude/settings.json` | チーム（git管理） | プロジェクト共通のルール |
| Local | `.claude/settings.local.json` | 個人のみ（gitignored） | 個人の実験的設定 |

実運用では、**Hooksによる制約はProject**に、**MCPのAPIキーはLocalまたはUser**に置くのが基本だ。

## 組み合わせの実践例

4つのレイヤーを組み合わせた実践的な構成例を示す。

```
project-root/
├── CLAUDE.md                          # 規約・フロー定義
├── .claude/
│   ├── settings.json                  # Hooks（チーム共有）
│   ├── settings.local.json            # 個人設定（gitignored）
│   └── skills/
│       ├── code-review/SKILL.md       # コードレビュー
│       ├── db-migration/SKILL.md      # DBマイグレーションレビュー
│       └── deploy-check/SKILL.md      # デプロイ前チェック
├── .mcp.json                          # MCP設定
└── tasks/
    ├── todo.md                        # タスク管理
    └── lessons.md                     # 学びのログ
```

この構成で実現できること：

1. **CLAUDE.md** → 「実装前にtodo.mdを確認」「コミット前にレビュースキルを実行」というフローを定義
2. **Hooks** → npm使用のブロック、ファイル編集後の自動Lint
3. **Skills** → `/code-review` でレビュー、`/db-migration` でマイグレーションチェック
4. **MCP** → Sentry連携でエラーを確認しながらバグ修正

## カスタマイズの指針

最後に、カスタマイズを進める上での指針をまとめる。

**段階的に導入する。** 最初からすべてを設定しようとしない。まずCLAUDE.mdから始めて、守られない規約があればHooksで強制し、繰り返す作業があればSkillsにし、外部サービスとの往復が多ければMCPで繋ぐ。

**CLAUDE.mdは「お願い」、Hooksは「強制」と使い分ける。** CLAUDE.mdに書いた指示は無視される可能性がある。絶対に守らせたいルール（パッケージマネージャーの統一、本番DB接続の禁止など）はHooksでブロックする。

**フィードバックサイクルを短くする。** PostToolUseでLint・型チェックを自動実行し、問題を早期に検出する。大量の修正が最後にまとめて必要になる事態を防ぐ。

**設定はgitで管理する。** `.claude/settings.json` と `.claude/skills/` はリポジトリにコミットし、チームで共有する。個人の実験的設定は `.local` ファイルに分離する。

Claude Codeは素の状態でも有用だが、プロジェクトに合わせてカスタマイズすることで、単なるコード補完を超えた開発パートナーになる。まずはCLAUDE.mdを1つ書くところから始めてみてほしい。

---

### こちらもよく読まれています
