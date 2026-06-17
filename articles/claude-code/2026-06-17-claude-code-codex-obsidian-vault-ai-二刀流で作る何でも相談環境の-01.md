---
id: "2026-06-17-claude-code-codex-obsidian-vault-ai-二刀流で作る何でも相談環境の-01"
title: "Claude Code × Codex × Obsidian Vault ― AI 二刀流で作る「何でも相談」環境の全設定公開"
url: "https://qiita.com/htani0817/items/5c5bffcbb53241ed5b54"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-06-17"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

# Claude Code × Codex × Obsidian Vault ― AI 二刀流で作る「何でも相談」環境の全設定公開

> **2026-04-29 追記**: 初稿から約2週間運用した結果、スキル体制・MCP構成・CLAUDE.md の中身がかなり変わりました。各セクションに取消線＋追記で差分を残しています。
>
> **2026-05-18 追記**: モデルを Sonnet 4.6 に変更・`effortLevel` 削除・フック2本追加（機密ファイル保護 / frontmatter チェック）・`claude-code-setup` プラグイン追加。各セクションに取消線＋追記で差分を残しています。
>
> **2026-06-16 追記**: プロジェクトが Claude Code 専用から **Claude Code + Codex 共有運用**へ大型アップデートされました。`AGENTS.md` の追加、Codex 向け実行機構（`.agents/` / `.codex/`）の整備、Claude–Codex 間レビューフローの導入、hooks の拡張、Google Drive 同期への移行など。各セクションに取消線＋追記で差分を残しています。

## はじめに

Claude Code を使い始めて少し経つと、多くの人が同じ問題にぶつかります。

- Claude が生成した `.md` がプロジェクトルート直下に散乱する
- 「あの調査メモどこ行った？」が週1で起きる
- Mac と Windows を行き来するたびにパス問題でつまずく

この記事では、私が実際に運用している「何でも相談-pj」という~~Claude Code 専用~~プロジェクトの中身を、**フォルダ構成・`CLAUDE.md`・`.claude/settings.json`・`.mcp.json` まで全部公開**します。（**2026-06-16**: Claude Code + Codex の共有運用プロジェクトへ進化しています）Obsidian の Vault をプロジェクトに内包することで、Claude Code の成果物を自動で整理し、さらに後から Obsidian のグラフビューで知識を俯瞰できる、という構成です。

対象読者：Claude Code を使い始めた〜中級者。Obsidian は未経験でも OK。

## プロジェクト全体像

まず設計の軸になっている3つの原則を先に書きます。この3つが全ての構成判断を支えています。

1. **成果物は全部 Obsidian Vault に入れる**（プロジェクトルートには散らかさない）
2. ~~**置き場ルールは `CLAUDE.md` に書いて Claude 自身に守らせる**（人間が毎回指示しない）~~ → **2026-06-16 更新**: `AGENTS.md` が正本になり、Claude Code と Codex の両方がこのファイルを読む
3. ~~**Mac と Windows を USB/ZIP で行き来できるポータブル設計**（Git 同期は使わない）~~ → **2026-06-16 更新**: Google Drive 同期に移行。ポータブル設計の原則（絶対パス禁止・UTF-8・LF）は引き続き有効

フォルダの全体像はこうなっています。

~~**2026-04-29 更新**: スキルが7つに増え、`coding/` 配下にも実際のプロジェクトが育ってきました。~~

~~```
何でも相談-pj/
├── README.md                  # 初回セットアップ手順
├── CLAUDE.md                  # プロジェクト指針（大幅拡充済み）
├── .mcp.json                  # MCP設定（AWS Docs + NotebookLM）
├── .claude/
│   ├── settings.json          # model / effortLevel など
│   ├── settings.local.json    # 許可リスト（個人用）
│   └── skills/                # カスタムスキル ×7
│       ├── obsidian-markdown/ # 必須: Obsidian記法の自動適用
│       ├── humanizer/         # 必須: AI臭さ除去（29パターン）
│       ├── note-article-writing/ # note.com 記事執筆
│       ├── obsidian-bases/    # .base データベースビュー
│       ├── json-canvas/       # .canvas ビジュアルキャンバス
│       ├── obsidian-cli/      # Obsidian CLI 操作
│       └── defuddle/          # Webページ→Markdown抽出
└── obsidian-vault/            # Obsidian Vault ルート
    ├── .obsidian/             # Obsidian 設定ごと持ち運び可能
    ├── daily/                 # デイリーノート YYYY-MM-DD.md
    ├── coding/                    # コーディング相談・実プロジェクト
    │   ├── project-a/             # クラウドリソース管理ツール
    │   ├── project-b/             # データベース移行調査
    │   │   └── reports/           # スクリプト実行結果
    │   ├── project-c/             # コンテンツ生成ツール
    │   ├── project-d/             # サーバ構築スクリプト
    │   └── project-e/             # Webサイト
    ├── research/              # 技術調査・学習メモ
    ├── docs/                  # ドキュメント下書き・成果物
    ├── references/            # 参考資料・URL・PDF等
    └── archive/               # 終了した相談のアーカイブ
```~~

**2026-06-16 更新**: Claude Code 専用から Claude Code + Codex 共有運用への移行に伴い、フォルダ構成が大幅に変わりました。`AGENTS.md` が共通指示の正本として追加され、Codex 向けの実行機構フォルダ（`.agents/` / `.codex/`）と共有層フォルダ（`guidelines/` / `scripts/` / `hooks/`）が追加されています。`coding/reviews/` もレビュー記録の専用置き場として明示されました。

```
何でも相談-pj/
├── README.md                  # 初回セットアップ手順
├── AGENTS.md                  # Claude Code と Codex の共通指示（正本）← 新規
├── CLAUDE.md                  # Claude Code 用入口（@AGENTS.md を読む薄いファイルに変更）
├── .mcp.json                  # MCP設定（AWS Docs + NotebookLM）
├── .claude/
│   ├── settings.json          # model / hooks など
│   ├── settings.local.json    # 許可リスト（個人用）
│   └── skills/                # Claude Code 側のスキル ×7
│       ├── obsidian-markdown/
│       ├── humanizer/
│       ├── note-article-writing/
│       ├── obsidian-bases/
│       ├── json-canvas/
│       ├── obsidian-cli/
│       └── defuddle/
├── .agents/                   # Codex 側の実行機構 ← 新規
│   └── skills/                # Codex 側スキル入口（.claude/skills/ を参照）
├── .codex/                    # Codex のプロジェクト設定 ← 新規
│   ├── config.toml
│   ├── hooks.json
│   ├── hooks/
│   └── agents/
├── guidelines/                # 文体・方針・ブランドなど共有ドキュメント ← 新規
├── scripts/                   # Claude Code と Codex の共有補助スクリプト ← 新規
├── hooks/                     # hook 実処理スクリプト（共有層） ← 新規
└── obsidian-vault/            # Obsidian Vault ルート
    ├── .obsidian/
    ├── daily/                 # デイリーノート YYYY-MM-DD.md
    ├── coding/                # コーディング相談・実プロジェクト
    │   ├── reviews/           # Claude–Codex レビュー記録 ← 新規
    │   └── <各プロジェクト>/
    ├── research/
    ├── docs/
    ├── references/
    └── archive/
```

<details>
<summary>初稿時点のフォルダ構成（参考）</summary>

```
何でも相談-pj/
├── README.md                  # 初回セットアップ手順
├── CLAUDE.md                  # プロジェクト指針（Claude Code が自動読込）
├── .mcp.json                  # プロジェクト固有のMCPサーバ設定
├── .claude/
│   ├── settings.json          # model / effortLevel など
│   ├── settings.local.json    # 許可リスト（個人用）
│   └── skills/
│       └── note-article-writing/   # プロジェクト固有のカスタムスキル
└── obsidian-vault/            # Obsidian Vault ルート
    ├── .obsidian/             # Obsidian 設定ごと持ち運び可能
    ├── daily/                 # デイリーノート YYYY-MM-DD.md
    ├── coding/                # コーディング相談・サンプル
    ├── research/              # 技術調査・学習メモ
    ├── docs/                  # ドキュメント下書き・成果物
    ├── references/            # 参考資料・URL・PDF等
    └── archive/               # 終了した相談のアーカイブ
```

</details>

~~`CLAUDE.md` と `README.md` だけプロジェクトルートに残しています。これは Claude Code が起動時にこの2ファイルを自動で読むため、Vault の中に入れてしまうと参照されない、という理由です。~~

~~**2026-04-29 更新**: プロジェクトルートに残すファイルは `CLAUDE.md`、`README.md`、`.mcp.json` の3つです。`.mcp.json` は Claude Code がプロジェクトルートから読み込む MCP サーバ設定ファイルなので、Vault 内に移動すると接続が壊れます。ファイル整理をした際にこの例外を `CLAUDE.md` にも明記しました。~~

**2026-06-16 更新**: Codex との共有運用への移行に伴い、プロジェクトルートに残すファイル・フォルダが増えました。`AGENTS.md`（共通指示の正本）、`.agents/`（Codex 実行機構）、`.codex/`（Codex 設定）、`guidelines/`・`scripts/`・`hooks/`（両エージェント共有層）はすべてプロジェクトルートに置く必要があります。これらを Vault 内に移動すると各エージェントの参照が壊れます。

## フォルダ構成とサブフォルダの役割

`obsidian-vault/` をプロジェクトに内包しているのがこの構成の肝です。Claude Code の作業ディレクトリはプロジェクトルート（`何でも相談-pj/`）のままなので、`.claude/` や `.mcp.json` はちゃんと認識される。一方で、ノート・成果物はすべて Vault 配下に入る。

サブフォルダ6つの役割を表にまとめました。

| フォルダ | 用途 | 命名規則 |
|---|---|---|
| `daily/` | デイリーノート・作業ログ | `YYYY-MM-DD.md` |
| `coding/` | コーディング相談・サンプル・実プロジェクト | `<トピック>/...` |
| `coding/reviews/` | Claude–Codex レビュー依頼と結果の記録（2026-06-16 追加） | `YYYY-MM-DD-<トピック>.md` |
| `research/` | 技術調査・学習メモ | `YYYY-MM-DD-トピック.md` |
| `docs/` | ドキュメント下書き・成果物 | `<ドキュメント名>.md` |
| `references/` | 参考資料・URL集・PDF | `links.md` / `<資料名>.pdf` |
| `archive/` | 終了した相談のアーカイブ | `YYYY-MM/<元のパス>` |

ポイントは `archive/` の運用で、月単位フォルダ（`archive/2026-04/` など）に**元のフォルダ構造ごと**移動します。こうすると Vault ルートが常に最小化されつつ、過去の文脈を辿りたい時に元の階層のまま見つけられる。

## CLAUDE.md に置き場ルールを書く

> **2026-06-16 更新**: `CLAUDE.md` は `AGENTS.md` への薄い入口に変更されました。共通指示の正本は `AGENTS.md` です。`CLAUDE.md` には Claude Code 固有の補足だけを書き、冒頭で `@AGENTS.md` を参照させます。以下の説明は初稿〜2026-05-18 時点のものですが、「CLAUDE.md（または AGENTS.md）に置き場ルールを書く」という考え方は現在も変わりません。

ここがこの記事で一番伝えたいところです。

~~`CLAUDE.md` はプロジェクトごとの指示書として機能します。多くの人は「コーディング規約を書く場所」として使っていると思いますが、私は**ファイル配置の自動化装置**として使っています。~~

**2026-06-16 補足**: 現在は `AGENTS.md` がプロジェクト共通指示の正本で、Claude Code も Codex も `AGENTS.md` を読みます。`CLAUDE.md` は Claude Code 専用の入口ファイルとして薄く保ちます。フォルダ置き場ルールや Obsidian 運用ルールはすべて `AGENTS.md` に記載しています。

たとえば私の `CLAUDE.md` にはこんな表が書いてあります。

```markdown
## フォルダ構成とデフォルト置き場ルール

新規ファイルを作る際は、内容に応じて以下のフォルダに配置してください
（絶対にプロジェクトルートや Vault ルートに散らさない）：

| フォルダ | 用途 | ファイル命名例 |
|----------|------|----------------|
| `obsidian-vault/daily/` | デイリーノート | `obsidian-vault/daily/YYYY-MM-DD.md` |
| `obsidian-vault/coding/` | コーディング相談 | `obsidian-vault/coding/<トピック>/...` |
| `obsidian-vault/research/` | 技術調査・学習メモ | `obsidian-vault/research/YYYY-MM-DD-トピック.md` |
| `obsidian-vault/docs/` | ドキュメント成果物 | `obsidian-vault/docs/<ドキュメント名>.md` |
| `obsidian-vault/references/` | 参考資料・URL集 | `obsidian-vault/references/links.md` |
| `obsidian-vault/archive/` | 終了した相談 | `obsidian-vault/archive/YYYY-MM/<元のパス>` |

会話の冒頭で `obsidian-vault/daily/<今日の日付>.md` が存在する場合、
Claude はそれを一度読んで当日の文脈を把握してから作業に入ってください。
```

この1枚の表を書いておくだけで、挙動が劇的に変わります。

**Before（`CLAUDE.md` なし）**：
> 私「API 設計のメモを書いて」
> Claude「`api-design.md` を作りました」（プロジェクトルートに生える）

**After（`CLAUDE.md` に置き場ルールあり）**：
> 私「API 設計のメモを書いて」
> Claude「`obsidian-vault/research/2026-04-18-API設計.md` を作りました」

毎回「Vault の research 配下に作ってね」と言わなくて良い。`CLAUDE.md` の最後の一文「会話の冒頭でデイリーノートを読む」も効いていて、セッション開始時に Claude が勝手に当日のデイリーノートを読み、前後の文脈を把握した上で返答してくれます。

### 2026-04-29 追記：CLAUDE.md はフォルダルールだけじゃ足りなかった

2週間運用して分かったのは、フォルダの置き場ルールだけでは Claude の出力品質を安定させられない、ということでした。現在の `CLAUDE.md` は初稿の3倍近い分量になっていて、主に以下のセクションを追加しています。

**スキル利用ポリシー** — 7つのカスタムスキルのうち、どれが「常時適用」でどれが「必要時のみ」かを明記しています。特に `obsidian-markdown`（Obsidian記法の自動適用）と `humanizer`（AI臭さ29パターン除去）は必須スキルとして、Claude がノートを書くたびに自動で適用するよう指示しています。

```markdown
### 必須スキル（常時適用）

| スキル | 適用場面 |
|--------|----------|
| `obsidian-markdown` | Vault 内の .md 作成・編集時。frontmatter、wikilinks、callouts を必ず使う |
| `humanizer` | 文章生成時に自動適用。AI臭さ29パターンを除去 |
```

**humanizer の適用ルール** — 「いつ適用して、いつ適用しないか」の線引きを明確にしています。コードブロック内や YAML frontmatter には適用しない、引用ブロックは原文ママ、など。これを書いておかないと、Claude がコードのコメントまで humanize しようとして壊れます。

**スクリプト文字コードルール** — Windows と Linux を行き来するプロジェクトなので、`.sh` は BOM 無し UTF-8 + LF、`.ps1` は BOM 付き UTF-8 + CRLF、`.py` は BOM 無し UTF-8 + LF、という具体的なルールを書いています。これを書く前は、Claude が作った `.sh` を Linux に持っていくと改行コードで動かない、ということが起きていました。

**Obsidian 運用ルール** — frontmatter の必須フィールド（title, date, tags, aliases）、wikilink の書式、callout の使い方、埋め込み記法などを網羅しています。`obsidian-markdown` スキルの `SKILL.md` に詳細は委ねつつ、`CLAUDE.md` にもサマリを書いておくことで、スキルを読み込む前の段階でも最低限の記法が守られるようにしています。

## .claude/settings.json の工夫

プロジェクトの挙動を固めるために `.claude/settings.json` でいくつかのキーを明示しています。

~~**2026-04-29 更新**: モデルを Opus 4.6 に変更しています。~~

~~**2026-05-18 更新**: モデルを **Sonnet 4.6** に変更。`effortLevel` を削除し、機密ファイル保護と frontmatter チェックの2フックを追加しています。~~

~~```json
{
  "model": "claude-sonnet-4-6",
  "enabledPlugins": {
    "everything-claude-code@everything-claude-code": true
  },
  "env": {
    "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "shell": "bash", "statusMessage": "機密ファイルチェック中...", "command": "# .env / credentials / secret を含むパスへの編集を自動ブロック" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "shell": "bash", "command": "# obsidian-vault/*.md に frontmatter がない場合に systemMessage で警告" }]
      }
    ]
  }
}
```~~

**2026-06-16 更新**: Codex との連携に伴い `Stop` フックを追加。既存の `PreToolUse` / `PostToolUse` と合わせて hooks は3種類になりました。

> **注**: 以下は構造を示す概略版です。`PreToolUse` / `PostToolUse` の `command` には実際には `node -e "..."` の Node.js スクリプトが入りますが、記事では可読性のため説明文で示しています。そのままコピーしても機密ファイル保護と frontmatter チェックは動作しません。

```json
{
  "model": "claude-sonnet-4-6",
  "enabledPlugins": {
    "everything-claude-code@everything-claude-code": true
  },
  "env": {
    "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1"
  },
  "hooks": {
    "Stop": [
      {
        "hooks": [{ "type": "command", "shell": "powershell", "statusMessage": "Codex レビュー依頼を確認中...", "command": "pwsh -File scripts/notify-codex-review.ps1" }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "shell": "bash", "statusMessage": "機密ファイルチェック中...", "command": "# .env / credentials / secret を含むパスへの編集を自動ブロック（実際は node -e スクリプト）" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "shell": "bash", "command": "# obsidian-vault/*.md に frontmatter がない場合に systemMessage で警告（実際は node -e スクリプト）" }]
      }
    ]
  }
}
```

<details>
<summary>2026-04-29時点の settings.json（参考）</summary>

```json
{
  "model": "claude-opus-4-6",
  "enabledPlugins": {
    "everything-claude-code@everything-claude-code": true
  },
  "effortLevel": "xhigh",
  "env": {
    "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1"
  }
}
```

</details>

<details>
<summary>初稿時点の settings.json（参考）</summary>

```json
{
  "model": "claude-opus-4-7",
  "enabledPlugins": {
    "everything-claude-code@everything-claude-code": true
  },
  "effortLevel": "xhigh",
  "env": {
    "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1"
  }
}
```

</details>

それぞれの狙いは次の通り。

- ~~`model`: Opus 4.7 に固定。モデルが勝手に変わらないように。~~ → ~~**2026-04-29 更新** Opus 4.6 に変更。Claude Code では Opus 4.6 が「Fast mode」として高速出力に対応しており、`/fast` トグルで切り替えられます。コーディング相談や調査タスクでは出力速度が体感に直結するため、こちらに乗り換えました。~~ → **2026-05-18 更新** Sonnet 4.6 に変更。日常的な相談・開発では Sonnet で十分であり、コスト削減のため変更。重い推論が必要なときは `/model` コマンドでその場だけ Opus に切り替えられます。
- `enabledPlugins`: 後述の `everything-claude-code` をプロジェクトで明示的に有効化。
- ~~`effortLevel: "xhigh"`: 推論の深さを最大寄り（`max` の一段下）に固定。コーディングや調査で妥協されないように。~~ → **2026-05-18 更新** `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING: "1"` で adaptive thinking を無効化している状態では effortLevel が機能しないため削除。
- `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING`: 思考量の自動調整を止める。毎回同じ深さで考えてもらう方が実運用で安定するため。
- ~~**`hooks`（2026-05-18 追加）**: 2種類のフックを追加。~~
  - ~~**PreToolUse（機密ファイル保護）**: Edit/Write の直前に実行。`.env` `credentials` `secret` を含むパスへの編集を自動ブロック。誤って APIキーファイルを書き換えるミスを防ぐ。~~
  - ~~**PostToolUse（frontmatter チェック）**: Write の直後に実行。`obsidian-vault/` 内の `.md` ファイルに frontmatter がない場合、systemMessage で警告を表示。~~
- **`hooks`（2026-06-16 更新）**: 3種類に拡張。
  - **PreToolUse（機密ファイル保護）**: 変わらず。`.env` `credentials` `secret` を含むパスへの編集を自動ブロック。
  - **PostToolUse（frontmatter チェック）**: 変わらず。`obsidian-vault/` 内の `.md` に frontmatter がない場合に警告。
  - ~~**PostToolUse（Codex agent 自動起動）**: `obsidian-vault/coding/reviews/*.md` への Write を検知して Codex agent を自動起動。~~ → Codex が agent フック形式に未対応のため削除。
  - **Stop（レビュー自動送信）**: Claude の作業完了時に `scripts/notify-codex-review.ps1` を実行。reviews/ に当日のノートがあれば `codex exec` で Codex にレビュー依頼を直接送信する。

加えて `.claude/settings.local.json` には**個人の許可リスト**を置いています。

```json
{
  "permissions": {
    "allow": [
      "mcp__awslabs_aws-documentation-mcp-server__search_documentation",
      "mcp__awslabs_aws-documentation-mcp-server__read_documentation",
      "WebFetch(domain:qiita.com)",
      "WebFetch(domain:www.anthropic.com)",
      "WebFetch(domain:aws.amazon.com)",
      "WebSearch"
    ]
  }
}
```

`settings.json` は「プロジェクトとして共有したい設定」、`settings.local.json` は「自分の端末だけの許可」と使い分けるのがコツ。このファイルのおかげで、よく使う AWS 公式ドキュメント・Qiita・Anthropic 公式へのフェッチで**権限確認プロンプトが出なくなり**、作業のリズムが崩れません。

## .mcp.json と everything-claude-code プラグイン

~~MCP サーバはプロジェクト固有の `.mcp.json` で1つだけ有効化しています。~~ → **2026-04-29 更新**: 2つに増やしました。AWS Docs に加え、NotebookLM MCP を追加しています。

```json
{
  "mcpServers": {
    "awslabs.aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_DOCUMENTATION_PARTITION": "aws"
      }
    },
    "notebooklm": {
      "command": "npx",
      "args": ["-y", "notebooklm-mcp@latest"]
    }
  }
}
```

<details>
<summary>初稿時点の .mcp.json（参考）</summary>

```json
{
  "mcpServers": {
    "awslabs.aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_DOCUMENTATION_PARTITION": "aws"
      }
    }
  }
}
```

</details>

起動は `uvx` 経由。uv/uvx を先に入れておけば、初回起動時に自動でパッケージをダウンロードしてくれます。なぜ AWS Docs を入れたかというと、Claude に AWS の話を聞くと**古い情報**で答えられがちなので、一次情報を直接引けるようにするためです。

**NotebookLM MCP** は、自分が Google NotebookLM に登録したソース群（PDF・URL・テキスト）に対して、Claude Code の会話の中から直接質問できるサーバです。`npx` で起動し、初回だけ Chrome で Google ログインすれば以降は Cookie が永続化されます。自分専用の知識ベースを Claude に横断検索させたい、という用途にぴったりで、「あの PDF に書いてあった気がするけど何ページだっけ」みたいな質問を引用付きで返してくれます。

大事なのは「**MCP を増やしすぎない**」こと。everything-claude-code の README にも「すべての MCP を有効にすると 200k のコンテキストが 70k まで縮む可能性」と書いてあります。私は AWS Docs と NotebookLM をプロジェクトスコープで有効化し、他の MCP（`context7` `exa` `github` `memory` `playwright` `sequential-thinking`）は everything-claude-code プラグイン経由で必要時だけ使う、という運用です。NotebookLM は Google ログインが必要で常時接続するわけではないため、不要な会話では起動しないよう注意が必要です。

そのプラグイン側でよく使っているスラッシュコマンドを表にしておきます。

| コマンド | 使いどころ |
|---|---|
| `/plan` | 実装計画を立てるとき |
| `/tdd` | TDD でコードを書き始めるとき |
| `/code-review` | 書いたコードの品質レビュー |
| `/security` | セキュリティ観点のレビュー |
| `/build-fix` | ビルドエラーの原因特定・修正 |
| `/refactor-clean` | デッドコード削除・整理 |
| `/verify` | 実装後の検証ループ |
| `/checkpoint` | 検証通過時の状態保存 |

**2026-05-18 追加**: `claude-code-setup@claude-plugins-official` プラグインも導入しました。コードベースを分析して、フック・スキル・MCP サーバの最適な設定を提案してくれます。`/claude-automation-recommender` で呼び出せます。

~~さらに `.claude/skills/note-article-writing/` に**プロジェクト固有のカスタムスキル**を置いています。note.com 向け記事を書くためのチェックリストやテンプレを `SKILL.md` に記述し、Claude が自動トリガーで呼び出してくれる。プロジェクトスコープで独自スキルを配置できるのが `.claude/skills/` の強みで、ワークフローに合わせたミニエージェントを自作できます。~~

**2026-04-29 更新**: スキルは7つまで増えました。「常時適用」と「必要時のみ」に分けて運用しています。

| スキル | 分類 | やること |
|---|---|---|
| `obsidian-markdown` | 常時適用 | Vault 内の `.md` を書くとき、frontmatter・wikilinks・callouts・embeds・tags を自動で正しい記法にする |
| `humanizer` | 常時適用 | 文章生成時にAI臭さ29パターン（「～と言えるでしょう」「～することが重要です」等）を自動除去。コードやYAMLには適用しない |
| `note-article-writing` | 必要時 | note.com 向け記事の執筆・チェック。スタイルルールとテンプレートを内蔵 |
| `obsidian-bases` | 必要時 | `.base` ファイル（Obsidian のデータベースビュー）を作成するとき |
| `json-canvas` | 必要時 | `.canvas` ファイル（ビジュアルキャンバス）を作成するとき |
| `obsidian-cli` | 必要時 | Obsidian 起動中に CLI からノート操作・検索するとき |
| `defuddle` | 必要時 | Web ページからクリーンな Markdown を抽出するとき |

特に `humanizer` の導入は大きかった。Claude が書く文章にはどうしても「構成としては〜」「〜と言えるでしょう」「〜において」みたいな定型句が混ざるので、29パターンをリスト化して `SKILL.md` に入れておくと、出力段階で自動的に言い換えてくれます。note.com の記事を書くときは `note-article-writing` のスタイルルールと `humanizer` の両方が効く形になっていて、わざわざ「自然な文体にして」と毎回言わなくてよくなりました。

## Codex との共有運用（2026-06-16 追加）

プロジェクトを Claude Code と Codex の両方から使えるように実行機構を分離・共有化しました。

### 指示書の二階建て構造

| ファイル | 役割 |
|---------|------|
| `AGENTS.md` | Claude Code と Codex の共通指示の正本 |
| `CLAUDE.md` | `@AGENTS.md` を読ませる薄い入口。Claude Code 固有の補足のみ記載 |

Codex は `AGENTS.md` を直接読みます。Claude Code は `CLAUDE.md` を起動時に読み、その中で `@AGENTS.md` を参照します。どちらのエージェントも同じルールで動くため、「Claude Code で作ったルール設定を Codex に再説明する」手間がなくなります。

### 役割分担

| エージェント | 役割 |
|------------|------|
| Claude（Claude Code） | 実行役。実装・ファイル編集・デバッグ・調査などの主作業を担う |
| Codex | レビュー役。Claude が作成・変更したコードの品質・セキュリティ・設計を検査する |
| Obsidian Vault | 共有データベース。Claude と Codex のやり取り・作業ログ・レビュー結果を蓄積する |

### Claude–Codex レビューフロー

`obsidian-vault/coding/reviews/` がレビュー記録の専用置き場です。

1. Claude が実装・変更を行う
2. Claude が `obsidian-vault/coding/reviews/YYYY-MM-DD-<トピック>.md` にレビュー依頼ノートを作成
3. Claude の作業完了時に Stop フック（`scripts/notify-codex-review.ps1`）が起動し、当日のレビューノートを検出して `codex exec` でレビュー依頼を直接 Codex に送信
4. Codex がノートを読み、「レビュー結果」セクションに結果を書き込む
5. Claude がノートを読み、必要な修正を行い「対応メモ」を残す
6. 完了後「完了記録」セクションに最終状態を記録

Obsidian Vault が Claude と Codex の共有データベースとして機能します。

### 追加されたフォルダ

| フォルダ | 役割 |
|---------|------|
| `.agents/skills/` | Codex 側の skill 入口（`.claude/skills/` を参照元として読む） |
| `.codex/` | Codex のプロジェクト設定・hooks・custom agent |
| `guidelines/` | 文体・方針・ブランドなど参照ドキュメント（両エージェント共有） |
| `scripts/` | 共有補助スクリプト（通知・dry-run 処理など） |
| `hooks/` | hook 実処理スクリプト（Claude Code と Codex の共有層） |

## ~~Mac/Windows 手動コピー移行のルール~~

~~このプロジェクトは Git もクラウド同期も使わず、USB/ZIP で手動コピーする前提です。Git を使わない理由は、Obsidian のグラフ・設定ファイル・PDF などバイナリ類まで含めた「丸ごと」を雑に持ち運びたいから。その代わり、**ファイル作成時のルール6つ**を守る必要があります。~~

**2026-06-16 更新**: 現在は **Google Drive で同期**しており、Mac/Windows 間の移行は自動化されています。手動コピーは不要になりました。ただしポータブル設計の原則（絶対パス禁止・BOM なし UTF-8・LF 統一）は Google Drive 同期でも有効なため、以下のルールは引き続き守ります。

| # | ルール | 理由 |
|---|---|---|
| 1 | 絶対パスを書かない | OS をまたぐと即死 |
| 2 | ホームディレクトリ直接参照（`C:\Users\...` や `/Users/...`）を埋め込まない | 同上 |
| 3 | パス区切りは `/` で統一 | Windows でも `/` は動く |
| 4 | BOM 無し UTF-8 で保存 | 文字化け対策 |
| 5 | 改行は LF（CRLF 混在は避ける） | Git を使わないのでエディタ側で揃える |
| 6 | `obsidian-vault/.obsidian/` も一緒にコピー | Obsidian の設定・プラグイン有効化状態を引き継ぐため |

別 PC に移した後は、プラグインだけ再導入します。これは `~/.claude/plugins/` が OS ごとにバイナリダウンロードされるため、フォルダごと持ち運べないからです。

/plugin marketplace add https://github.com/affaan-m/everything-claude-code
/plugin install everything-claude-code

**2026-05-18 更新**: `claude-code-setup` プラグインも追加しました。

/plugin marketplace add https://github.com/affaan-m/everything-claude-code
/plugin install everything-claude-code
/plugin install claude-code-setup@claude-plugins-official

この3行を叩けば、2回目以降の同じ PC では `~/.claude/settings.json` に記録されるので不要。Obsidi
