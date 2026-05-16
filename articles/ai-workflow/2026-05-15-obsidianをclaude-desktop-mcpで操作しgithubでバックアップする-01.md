---
id: "2026-05-15-obsidianをclaude-desktop-mcpで操作しgithubでバックアップする-01"
title: "ObsidianをClaude Desktop MCPで操作し、GitHubでバックアップする"
url: "https://qiita.com/zygm/items/4077e2a70e78f77ebe85"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

## 概要

ObsidianのVaultをClaude Desktop（MCP経由）から読み書きし、GitHubのprivate repositoryでバックアップする環境を構築する。

この構成を取ると何ができるかというと：

- ClaudeとのチャットからObsidianのノートを直接作成・更新できる
- 記事のドラフト、ナレッジメモ、プロジェクト管理をClaude経由で自動化できる
- VaultをGitで管理することでバージョン履歴が残り、誤削除や破損から守れる

筆者はこれをコンテンツ制作フロー（Note.com落語記事・Qiita技術記事）と営業管理の両方に使っている。

---

## 前提条件

| ツール | バージョン |
|---|---|
| Obsidian | 最新版 |
| Claude Desktop | 最新版（MCP対応版） |
| Git | 2.x以上 |
| GitHubアカウント | 作成済み |

---

## 全体構成

```
Claude Desktop（チャット）
    │
    │ MCP（obsidian-vault）
    ▼
Obsidian Vault（ローカル）
    │
    │ Git
    ▼
GitHub Private Repository
```

Claude → Obsidian の読み書きはMCPが担い、Obsidian → GitHubのバックアップはGitが担う。

---

## Step 1：Obsidian MCP サーバーのセットアップ

### 1-1. MCPサーバーのインストール

Obsidian用のMCPサーバーをインストールする。

```bash
npm install -g obsidian-mcp
```

または、[obsidian-mcp](https://github.com/MarkusPfundstein/mcp-obsidian) をクローンしてローカルで動かす方法もある。

### 1-2. Claude Desktopの設定ファイルを編集

Claude Desktopの設定ファイルを開く。

**Windowsの場合：**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOSの場合：**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

以下の内容を追記する：

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "npx",
      "args": [
        "obsidian-mcp",
        "/path/to/your/obsidian/vault"
      ]
    }
  }
}
```

`/path/to/your/obsidian/vault` は実際のVaultのパスに置き換える。

Windowsの場合のパス例：
```json
"args": [
  "obsidian-mcp",
  "C:\\Users\\xxxx\\OneDrive\\ITIL\\Documents\\Obsidian Vault"
]
```

### 1-3. Claude Desktopを再起動

設定ファイルを保存してClaude Desktopを再起動すると、MCPサーバーが起動する。

チャット画面で「Vaultの一覧を見せて」と聞いてみて、ファイルが返ってきたら接続成功だ。

---

## Step 2：できること確認

MCPが接続されると、Claudeから以下の操作ができるようになる。

### ノートの読み書き

```
「Articles/Note/rakugo/drafts/ に新しい記事ドラフトを作って」
「Legal/著作権/ブログ著作権保護_運用ガイド.md を読んで」
「Projects/SES/XX_進捗.md を更新して」
```

### フォルダ構造の参照

```
「Vaultのフォルダ構造を見せて」
「Articlesフォルダ以下を一覧表示して」
```

### タグ管理

```
「このノートにタグ #draft を追加して」
「Vault全体のタグ一覧を出して」
```

---

## Step 3：GitHub Private Repositoryの作成

### 3-1. リポジトリを作成

[https://github.com/new](https://github.com/new) にアクセスして以下の設定で作成する。

| 設定項目 | 値 |
|---|---|
| Repository name | `obsidian-vault`（任意） |
| Visibility | **Private** ← 重要 |
| Add README | **Off** |
| Add .gitignore | Off（後で手動作成） |

### 3-2. VaultでGitを初期化

PowerShell（またはターミナル）を開く。

```powershell
cd "C:\Users\xxxx\OneDrive\ITIL\Documents\Obsidian Vault"
git init
git remote add origin https://github.com/<your-username>/obsidian-vault.git
git branch -M main
```

### 3-3. `.gitignore` を作成

Vault直下に `.gitignore` を作成する。

個人情報・営業情報など、GitHubに上げたくないフォルダを除外しておく。

```gitignore
# 個人情報・取引先情報
実績/
HiNet/
Diary/
Calendar/

# Obsidian内部ファイル（環境依存）
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# 画像ファイル（容量節約・必要なら外す）
Pasted image *.png

# OS生成ファイル
.DS_Store
Thumbs.db
```

> **補足：** OneDrive上にVaultを置いている場合、OneDrive同期とGitの両方が動く。競合はほぼ起きないが、`.git/` フォルダはOneDriveの同期対象から除外しておくと安心だ。

### 3-4. 初回コミット & push

```powershell
git add .
git commit -m "initial commit: Obsidian Vault"
git push -u origin main
```

---

## Step 4：Claude側スキルのバックアップ

ここが見落としがちなポイントだ。

Claude Desktopのスキルファイル（`/mnt/skills/user/`）は**ローカルではなくClaude側のサーバーに保存されている**。

つまり、Windowsのエクスプローラーからは見えないし、直接編集もできない。編集はClaude経由でのみ可能だ。

対策として、Vault内に `Skills/` フォルダを作り、Claudeにスキルの内容を書き出してもらう運用をおすすめする。

```
Obsidian Vault/
└── Skills/
    ├── README.md                              ← 運用ルール
    ├── zygm-note-rakugo-style.md
    ├── zygm-note-yuraiki-style.md
    ├── zygm-qiita-style.md
    ├── zygm-note-rakugo-header.md
    ├── zygm-note-yuraiki-header.md
    ├── zygm-note-rakugo-header/
    │   ├── assets/template_sea_sun.md         ← SVGをコードブロックで保存
    │   └── references/design-tokens.md
    └── zygm-note-yuraiki-header/
        ├── assets/template_scroll.md
        └── references/yuraiki-design-tokens.md
```

スキルを更新したときは「スキルのバックアップを更新して」とClaudeに依頼するだけでVaultに反映される。

---

## Step 5：日常のバックアップ運用

記事を書いたとき・スキルを更新したときに以下を実行する。

```powershell
cd "C:\Users\xxxx\OneDrive\ITIL\Documents\Obsidian Vault"
git add .
git commit -m "update: 記事タイトルや変更内容を一言で"
git push
```

頻度の目安：記事1本書くごと、もしくは週1回。

---

## 補足：Obsidian Sync は必要か？

Obsidianには公式の同期サービス「Obsidian Sync」($4〜$8/月)がある。バックアップを検討する中で「これでいいのでは？」と思う人もいるだろう。結論から言うと、**用途次第で判断が分かれる**。

### GitHub vs Obsidian Sync の比較

| | GitHub Private Repo | Obsidian Sync |
|---|---|---|
| **料金** | **無料** | 有料（$4〜$8/月） |
| **バージョン管理** | ✅ commit単位で無制限 | △ 最大1年 |
| **PC→スマホ同期** | ❌ 手動操作が必要 | ✅ 自動・得意 |
| **E2E暗号化** | ❌ Private設定のみ | ✅ あり |
| **Claude MCP連携** | ✅ Git MCPで自動化できる | ❌ 不可 |
| **OneDriveとの共存** | ✅ 問題なし | ⚠️ 公式非推奨 |

### 判断の目安

**Obsidian Syncが向いているケース：**
- iPhoneやiPadでもObsidianを使いたい
- PCとスマホのリアルタイム同期が必要
- E2E暗号化でVaultを保護したい

**GitHubで十分なケース：**
- PCのみで使っている
- コストをかけたくない
- Claude MCP + Git自動化の連携を活かしたい
- バージョン履歴をcommitメッセージ付きで管理したい

### OneDrive + GitHub で十分な理由

すでにOneDrive上にVaultを置いている場合、**OneDriveが自動同期・Gitがバージョン管理**という役割分担で必要十分だ。

ここにObsidian Syncを追加すると三重管理になるうえ、OneDriveとObsidian Syncの競合リスクも生じる。スマホ同期が不要なら追加するメリットはほぼない。

---

## まとめ

```
構成まとめ

① Claude Desktop + Obsidian MCP
   └─ claude_desktop_config.json にMCPサーバーを登録
   └─ VaultのパスをMCPに渡す

② Vault の Git 管理
   └─ .gitignore で個人情報フォルダを除外
   └─ GitHub Private Repositoryにpush

③ スキルファイルのバックアップ
   └─ /mnt/skills/user/ はサーバー側にある（ローカルではない）
   └─ Vault/Skills/ にClaudeが書き出す運用で保護

④ Obsidian Syncは？
   └─ スマホ同期が不要なら GitHub + OneDrive で十分
   └─ 追加するとOneDriveと競合リスクあり・費用対効果も低い
```

この構成を取ると、Claudeとのチャットで積み上げてきた設定・スキル・記事ドラフトがすべてGitHubに残る。アカウントの問題や仕様変更があっても資産を失わない体制になる。

MCPの設定は一度やってしまえば後は意識しなくてよいので、ぜひ試してみてほしい。
