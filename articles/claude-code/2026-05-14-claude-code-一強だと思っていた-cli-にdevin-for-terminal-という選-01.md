---
id: "2026-05-14-claude-code-一強だと思っていた-cli-にdevin-for-terminal-という選-01"
title: "Claude Code 一強だと思っていた CLI に、Devin for Terminal という選択肢"
url: "https://zenn.dev/asix/articles/47c28121f0918a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "AI-agent", "GPT", "zenn"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

> **この記事が参考になったら、画面の「いいね」やストックを押してもらえると、次を書く励みになります。**（読み飛ばして本文から読んでも大丈夫です）

「ターミナルで動くコーディングCLI = Claude Code」、私は半年くらいそう決め打ちしていました。

そこに2026年4月27日、Cognitionが `devin` コマンドを出してきました。**Devin for Terminal**。公式ブログではターミナルUI向けに **Rust で書いたカスタム描画ライブラリ** を使っている旨が述べられているローカルCLIで、`curl` 一発でインストールできて、ノートPCを閉じてもクラウド側で続きをやってくれる、と書かれています。

「ローカルCLIならClaude Codeでいいだろう」と最初は流していたのですが、1週間並べて使ってみたら、想像以上に機能が揃っていて、しかも **Claude Code の Subagent 設定がそのまま動く** と分かったときに考えが変わりました。

この記事は、Devin for Terminal の機能を公式ドキュメント準拠でちゃんと紹介しつつ、Claude Code と並べて使ってみた所感を書きます。

## 1分で Devin for Terminal

公式アナウンス（2026/4/27）と公式ドキュメント `cli.devin.ai` を読むと、ざっくり次のような立ち位置です。

| 項目 | 内容 |
| --- | --- |
| **インストール** | `curl -fsSL <https://cli.devin.ai/install.sh> |
| **起動** | プロジェクトディレクトリで `devin` |
| **実装** | ターミナル描画は Rust のライブラリ（公式ブログ）。「VT-100 でも動く」とデモで紹介 |
| **対応モデル** | Opus 4.7 / GPT-5.5 / Cognition自社の SWE-1.6 を切替可 |
| **設計思想** | "Start Local, Hand Off to the Cloud" |
| **Windsurf** | Windsurf Enterprise v1.9577.24以降にバンドル提供 |

`curl` 1行でインストールして `devin` で起動、というシンプルさは Claude Code と同じ感覚で触れます。

## Devin for Terminal の機能、思ったより充実してた

ここがこの記事の主題です。「ローカル版のおまけ機能なんでしょ？」と思って公式ドキュメントを開いたら、想像していた3倍くらい機能がありました。

### 機能1: Skills — Claude Code 互換の指示書システム

`.devin/skills/<スキル名>/SKILL.md` のように **スキル名のディレクトリ配下** に `SKILL.md` を置いてカスタムスキルを定義します。YAMLフロントマター付きMarkdownで、Claude Code の Skills とほぼ同じ書き方です。`allowed-tools` に使えるのは公式で列挙されている小文字のツール名（`read`, `edit`, `grep`, `glob`, `exec` など）です。

```
---
name: deploy-staging
description: ステージング環境へデプロイ
allowed-tools:
  - read
  - exec
triggers:
  - user
  - model
---

ステージング環境への手順は次のとおり...
```

配置場所の例（公式の Skills Overview に沿った代表例）です。

| 場所 | スコープ |
| --- | --- |
| `.devin/skills/` または `.agents/skills/` など | プロジェクト固有（git管理に乗せる） |
| `~/.config/devin/skills/` | グローバル（全プロジェクトで使用） |
| `~/.codeium/<channel>/skills/` | チャネル依存のグローバル（`windsurf` / `windsurf-next` / `windsurf-insiders` 等） |

`/skill-name` でユーザーから呼ぶこともできるし、agent が文脈から自動呼び出しすることもできます。

### 機能2: Subagents — Claude Code の agent ファイルを自動インポート

ここが個人的に一番驚いたところです。

Devin for Terminal のカスタムサブエージェントは **`.devin/agents/<プロフィール名>/AGENT.md`**（例: `reviewer/AGENT.md`）で定義できます。加えて **`.claude/agents/*.md` も自動でインポートして使える** と公式ドキュメントに明記されています。

違いは「`tools` フィールド」 vs 「`allowed-tools` フィールド」程度で、両者は自動マッピングされます。これは乗り換えコストを露骨に下げに来ています。

### 機能3: MCP — OAuth対応で GitHub / Notion / Linear / Jira

MCPサーバーの追加は次の通り。

```
# stdio サーバー（公式例では npx に -y を付けることが多い）
devin mcp add github -- npx -y @modelcontextprotocol/server-github

# HTTP サーバー（OAuth対応）
devin mcp add notion https://mcp.notion.com/mcp
```

設定スコープも3段階。

| ファイル | 用途 |
| --- | --- |
| `.devin/config.local.json` | 個人用（git除外） |
| `.devin/config.json` | プロジェクト共有 |
| `~/.config/devin/config.json` | グローバル |

注意点としては「Streamable HTTPのみ対応、SSEトランスポートは非サポート」と公式に書かれています。新規サーバーを選ぶときはここに気を付けたいところ。

### 機能4: Hooks — Claude Code と互換のライフサイクルフック

[Hooks の公式ドキュメント](https://cli.devin.ai/docs/extensibility/hooks/overview) では、`PreToolUse` / `PostToolUse` / `PermissionRequest` など Claude Code と同じイベントモデルでコマンドやプロンプトを差し込めると説明されています。`.devin/hooks.v1.json` や各種 config の `hooks` キーに加え、デフォルトでは **`read_config_from.claude` が有効なとき `.claude/settings.json` の hooks も読み込まれる** 旨が書かれています。セッション中は **`/hooks`** で読み込み一覧を確認できます。

### 機能5: Permission Mode — Autonomous は OS レベルサンドボックス

Claude Code の permission mode に相当するものが4段階あります。

| Mode | 自動承認の範囲 | 推奨用途 |
| --- | --- | --- |
| **Normal**（デフォルト） | **カレントディレクトリ内**の読み取りなど読み取り系は自動承認し、書き込みやシェルは確認 | 通常作業 |
| **Accept Edits** | ワークスペース内のファイル編集は自動、シェルは確認 | 編集中心のタスク |
| **Bypass** | 全ツールコールを自動承認 | 信頼できる場面 |
| **Autonomous** | `--sandbox` 時のみ。OS-level sandbox でシェルは隔離のうえ自動承認 | 放置で回したい場面 |

ポイントは **Autonomous モード**。Bypass のようにマシン全体への野放しではなく、**OSレベルのサンドボックス**でシェル実行を隔離します。公式の Bypass との対比表では、**`edit` / `write` 系は Autonomous でも引き続きプロンプト**（スコープ拡大で許可）、ネットワークはサンドボックスの allow/deny でフィルタ、といった整理になっています。「完全放置で回したいが、本当に何でも触られるのは怖い」というジレンマへの、公式の一方の答えになっています。

### 機能6: Agent Mode — Normal / Plan / Ask

permission mode とは別軸で、エージェントの振る舞いを変えるモードもあります。

| Mode | 起動 | 振る舞い |
| --- | --- | --- |
| **Normal** | デフォルト | コード変更含む通常モード |
| **Plan** | `/plan` | 計画立案に集中、コード変更しない |
| **Ask** | `/ask <質問>` | 質問応答のみ、コードを書かない |

Claude Code の Plan mode と同じ発想です。

### 機能7: クラウドハンドオフ — `/handoff` でPCを閉じて続行

ここが Claude Code と最大の差分です。ローカルで動かしていたセッションを `/handoff` 1コマンドで Devin Cloud に渡せます。

`/handoff` には次の特徴があります。

* 引数なしで叩くと、現在の会話を自動要約してクラウド側に渡す
* ローカルのgit diffも一緒に送られる（未コミット変更が見える状態でクラウドが受け取る）
* `&` を空のプロンプトで打つだけでhandoffモードに入れるショートカットあり（`!` でbashモードに入るのと同じ感覚）

クラウド側は自前のVMで動くので、ローカルマシンを閉じても作業は続きます。これは Claude Code には対応する機能がありません。

### 機能8: スラッシュコマンドとショートカット

普段使いの便利機能もちゃんと揃っています。

| 操作 | 内容 |
| --- | --- |
| `/mode <name>` | permission mode の切替 |
| `/loop <prompt>` | 自動diff レビュー付きでプロンプト実行 |
| `/workspace` | ワークスペースディレクトリ一覧 |
| `/help` | 全コマンド表示 |
| `/hooks` | 読み込まれた Hooks の一覧 |
| `Shift+Tab` | mode を順に切り替え |
| `@` | ファイル名補完してコンテキストに追加 |
| `Ctrl+V` | クリップボードから画像貼り付け |
| `Ctrl+G` | 外部エディタで編集 |
| `devin -c` | 直近セッションをresume |
| `devin -r` | resumeしたいセッションを一覧から選ぶ |

`Shift+Tab` で mode を切り替える感覚は Claude Code そっくりです。

## Claude Code と並べた機能対応表

ここまで紹介してきた機能を、Claude Code 側と並べてみるとこうなります。

| 機能 | Claude Code | Devin for Terminal |
| --- | --- | --- |
| 起動 | `claude` | `devin` |
| 対応モデル | Anthropic製モデル中心 | **Opus 4.7 / GPT-5.5 / SWE-1.6 切替可** |
| Skills | ✅ `.claude/skills/<名前>/SKILL.md` | ✅ `.devin/skills/<名前>/SKILL.md` など（`.agents/skills/` も可） |
| Subagents | ✅ `.claude/agents/*.md` | ✅ `.devin/agents/<名前>/AGENT.md` ＋ **Claude形式を自動インポート** |
| MCP | ✅ | ✅（OAuth対応、Streamable HTTPのみ） |
| Permission mode | `default` / `acceptEdits` / `plan` / `bypassPermissions` 等（`--dangerously-skip-permissions` はバイパス系） | Normal / Accept-Edits / Bypass/**Autonomous（`--sandbox` 時）** |
| Plan mode | ✅ | ✅ `/plan` |
| クラウド連携 | なし | ✅ **`/handoff` で Devin Cloud に引き継ぎ** |
| マルチエージェント並列 | Subagents | worktreeなしで同一リポジトリに複数 |
| Hooks | ✅ `PreToolUse` 等 | ✅ **Claude Code と同形式**（`.devin/hooks.v1.json` や `.claude` から読込可） |

## 「遜色なし」と感じた4つのポイント

1週間使った中で、特にこの4点で「Claude Code じゃなくてもいい」と感じました。

### 1. Claude Code の Subagent がそのまま動く

`.claude/agents/` を作り込んでいるプロジェクトで `devin` を起動すると、既存の agent がそのまま選択肢に出てきました。乗り換えではなく **並走** ができる、というのは大きい。私の場合「Explore的なagent」と「PR Reviewer的なagent」を Claude Code 側で書き溜めていたので、これがそのまま使えたのは正直驚きでした。

### 2. Autonomous モードの設計が一段先

「放置で回したいが本当に何でも実行されるのは怖い」というのは Claude Code でも長年のジレンマでした。`--dangerously-skip-permissions` は強力ですが、ネットワークや外部書き込みまで自由になります。

Devin for Terminal の Autonomous は `--sandbox` で OS レベルの隔離をかけたうえでシェル実行などを自動承認する設計です。公式の整理では **`edit` / `write` 系はプロンプトが残り**、ネットワークはサンドボックスのドメイン制御のもとで扱われます。Bypass ほど「端末上のすべてが暗黙承認」ではない、という意味で夜回しの安心感が違います。

### 3. マルチモデルを1つのCLIで切り替えられる

Claude Code は Anthropic 製モデル中心の世界観です。一方 Devin for Terminal は Opus 4.7 と GPT-5.5、そして Cognition 自社の SWE-1.6 を1つのCLI内で切り替えられます。

「このリファクタリングは Opus、こっちの大量生成は GPT-5.5」みたいな使い分けが、ツールを切り替えずにできるのは効率がいい。

### 4. クラウドへの逃し先がある

これは Claude Code にはない、Devin for Terminal の最大の独自機能です。重い処理だけ `/handoff` でクラウドに逃して、ローカルは身軽にしておけます。

「夜中に大量のテスト書き換えを回したい、でも自分のMacBookは閉じて寝たい」という場面で、`/handoff` を打ってからMacを閉じると、**タスク次第では**朝までに Devin Cloud 側で PR まで進んでいることもあります（保証ではなく所感です）。

## Claude Code が依然として強い領域

正直に書くと、Claude Code 側が依然有利な部分もあります。

| 観点 | Claude Code が有利な理由 |
| --- | --- |
| エコシステム・文献の厚み | Skills / Subagents / Hooks / Auto Mode を組み合わせた記事・事例・チーム運用の蓄積は、現時点では Claude Code に先行しがち（Devin 側も Hooks は Claude 互換で読み込めるが、検索でヒットする手順書の量は差が出やすい） |
| クラウド版Devinの独自機能を CLI から使えない | Knowledge / Playbooks / Secrets は **Devin for Terminal では現状未対応**。公式 Quickstart では順次サポートに向けて開発中とされている |

特に最後の点は重要で、「Devin の旨味は Knowledge と Playbook」という従来の評価軸からすると、CLIだけで Devin を評価するのはまだ早い、とも言えます。

## どう使い分けるか

| シナリオ | 推奨 | 理由 |
| --- | --- | --- |
| Anthropic モデル中心の対話開発 | Claude Code | エコシステムが厚い |
| 既に `.claude/agents/` を作り込んでいる | Devin for Terminal | そのまま使えて、加えてクラウド連携も得られる |
| GPT-5.5 や SWE-1.6 を試したい | Devin for Terminal | マルチモデル切替が公式機能 |
| 夜中に放置で回したい | Devin for Terminal | Autonomous（`--sandbox`）＋ OS sandbox ＋ クラウドハンドオフ |
| 検索ヒットする手順書・社内標準が Claude 中心 | Claude Code | ドキュメントとコミュニティの量 |
| Knowledge / Playbook を使いたい | クラウドDevin | CLIにはまだ未対応 |

## おわりに

正直、最初は「Claude Code でいいでしょ」と思って `devin` コマンドを試しました。

1週間後、自分の `.claude/agents/` がそのまま動き、`--sandbox` で安全に夜回しできるようになり、`/handoff` で重い処理だけクラウドに逃せるようになっていました。Claude Code を捨てたわけではなく、ターミナルCLIに **選択肢が増えた** という感覚です。

「ターミナルで動くコーディングCLI = Claude Code」と思い込んでいた半年前の自分に、「devin というのが2026/4/27に出るから試してみろ」と言いたい。それくらい遜色なく、そして部分的には先を行っている機能もあります。

両方インストールして、タスクごとに使い分けるのが2026年5月時点の最適解だと思っています。

---

## 参考リンク

### Devin for Terminal 公式

### Claude Code 公式
