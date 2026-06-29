---
id: "2026-06-29-notionで良くないと思ってた私がobsidianにハマってついにclaudeと連携させた話-01"
title: "「Notionで良くない？」と思ってた私がObsidianにハマって、ついにClaudeと連携させた話"
url: "https://zenn.dev/ryunotezenn/articles/3da3403bb2c30f"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "VSCode", "zenn"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

# 「Notionで良くない？」と思ってた私がObsidianにハマって、ついにClaudeと連携させた話

## 最初は正直、懐疑的でした

Obsidianって名前、エンジニアなら一度は聞いたことあると思います。でも最初に触ったとき、私の感想はこうでした。

「……あれ、これただのMarkdownエディタじゃないの？」

Notionならデータベース機能もあるし、チームで共有もできるし、UIも洗練されてる。それに比べてObsidianはローカルで動くだけの地味なアプリに見えて、「わざわざ乗り換える理由なくない？」と思ってたんですよね。

でも実際に使い込んでいくうちに、**Obsidianの本質はメモアプリじゃなくて「自分専用の知識グラフエンジン」だ**ということに気づいてから、評価が完全に変わりました。

この記事では、懐疑派だった私がObsidianの何に惹かれたのか、そして最終的にClaude（AI）とMCPで連携させるところまでやったので、その全部をまとめます！

---

## Obsidianって結局何がいいの？

### データが自分のものである、という安心感

Notionを使っていて、ちょっと怖いなと思ったことないですか？

「もしNotionがサービス終了したら？」「APIの仕様が変わったら？」「オフラインで使えない…」

Obsidianはこの不安をゼロにしてくれます。なぜかというと、**すべてのノートがローカルのMarkdownファイルとして保存される**からです。

```
~/Documents/ObsidianVault/
├── Projects/
│   ├── my-app.md
│   └── インフラ移行計画.md
├── Areas/
│   ├── Career/
│   └── 学習ログ/
└── Daily/
    └── 2025-06-29.md
```

このフォルダ、そのままGitで管理できます。VSCodeで開いても読めます。Obsidianが仮に明日なくなっても、データは手元に残ります。「データの主権が自分にある」って、思ってる以上に重要なことだと気づきました。

### リンクで知識がつながっていく感覚がクセになる

Obsidianの一番の特徴は `[[WikiLink]]` 構文で、ノート同士をリンクできることです。

```
# Kubernetesの勉強メモ

Podの概念を理解するには[[Dockerコンテナ]]の知識が前提。
本番運用では[[EKS]]か[[GKE]]の選定が必要になる。
コスト感については[[クラウドコスト最適化]]も参照。
```

リンクを貼ると、リンク先のノートには自動的に「このノートからリンクされてますよ」というバックリンクが記録されます。これが積み重なると、グラフビューでノート同士のつながりが可視化されて、自分の知識の構造が一目でわかるようになります。

「ただメモが増えるだけ」から「知識が育っていく」感覚になるのが、Obsidianの一番の面白さだと思います。

### プラグインが豊富すぎて沼

コミュニティプラグインが1,000個以上あります。沼です。特に使えるやつを紹介すると：

| プラグイン | 何ができる？ |
| --- | --- |
| **Dataview** | ノートをSQLっぽいクエリで集計・一覧表示できる |
| **Tasks** | `- [ ]` タスクをVault全体から横断検索できる |
| **Templater** | 動的テンプレートでノート作成を自動化できる |
| **Calendar** | デイリーノートをカレンダーUIで管理できる |
| **Local REST API** | HTTPでObsidianをプログラマブルに操作できる |

Dataviewが特に強力で、こんなクエリが書けます：

```
```dataview
TABLE file.mtime AS "更新日", status AS "ステータス"
FROM "Projects"
WHERE status != "完了"
SORT file.mtime DESC
```
```

Notionのデータベースビューみたいなことが、Markdownファイルの上に実現できるんです。しかもファイル本体は汚染されないので、後でエディタを変えてもデータはクリーンなまま。

---

## 情報の整理、どうしてる？

Obsidianを使いこなすには、フォルダ構造の設計が地味に大事です。私はPARA法をベースにしています。

```
vault/
├── 🚀 Projects/    # 期限のある進行中プロジェクト
├── 🏛️ Areas/       # 継続的に管理する領域（キャリア、健康など）
├── 📚 Resources/   # 参考情報・技術メモ
├── 📦 Archive/     # 完了・不要になったもの
└── 📅 Daily/       # デイリーノート
```

「これどこに置くんだっけ？」ってNotionで悩んでたやつが、PARAの基準（期限あり＝Projects、継続管理＝Areas、参考情報＝Resources、完了済み＝Archive）で迷わなくなりました。

毎日デイリーノートを起点にして、ProjectsやAreasにリンクを張っていくだけで、自然と知識が蓄積されていきます。

---

## ここからが本題！Claude MCP連携でObsidianがAIに動かされる

Obsidianのデータがローカルのファイルであること、これが **Claude Desktop + MCP** と組み合わせると最強になります。

### どういう仕組み？

```
Obsidian Vault (ローカルの.mdファイル群)
        ↕ ファイルを直接読み書き
   obsidian-mcp-server (Node.jsプロセス)
        ↕ MCP（Model Context Protocol）
   Claude Desktop
        ↕ 自然言語で会話
       あなた
```

MCP（Model Context Protocol）はAnthropicが策定した、AIが外部ツールを操作するための標準プロトコルです。`obsidian-mcp-server` はこのプロトコルに対応したサーバーで、ClaudeがVaultのファイルを読み書きできるようにしてくれます。

### セットアップ手順

**ステップ1：Claude Desktopをインストール**

```
brew install --cask claude
```

:::message claude.ai（ブラウザ版）ではローカルファイルにアクセスできません。必ずデスクトップアプリが必要です！ :::

**ステップ2：設定ファイルを編集**

```
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

```
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": [
        "-y",
        "obsidian-mcp-server",
        "/Users/yourname/Documents/ObsidianVault"
      ]
    }
  }
}
```

パスは自分のVaultの場所に変えてください。

**ステップ3：フルディスクアクセスを許可（macOSのみ）**

システム設定 → プライバシーとセキュリティ → フルディスクアクセス → Claude を追加

**ステップ4：Claude Desktopを完全に再起動**

:::message alert `Cmd + Q` でプロセスごと終了してから再起動してください。メニューバーにアイコンが残った状態では設定が読み込まれません（私はここで10分くらいハマりました）。 :::

### 実際に何ができるの？

設定完了後は、こんな感じで自然言語でVaultを操作できます。

**ノートを参照して質問に答えてもらう：**

```
「Projectsフォルダのノートを一覧して」
「Kubernetesについて書いたメモを全部読んで、共通する課題をまとめて」
```

**ToDoを書き込んでもらう：**

```
「明日の朝イチでオンボーディング資料を確認する、
というタスクをTasks/ToDo.mdに追記して」
```

するとClaudeが自動でこういうMarkdownを追記してくれます：

```
- [ ] オンボーディング資料を確認する 📅 2025-06-30
```

**複数ノートを横断して分析：**

```
「先週のデイリーノートを読んで、
今週フォローすべきことをまとめて」
```

これ、Notionの「ページ内AI」とは全然違います。Claude Desktop + MCPはVault全体をコンテキストとして扱えるので、複数ノートをまたいだ分析・統合ができるんです。

---

## まとめ

最初は「Notionで良くない？」と思ってたObsidianでしたが、使い込んでみると全然違う価値がありました。

* **データが手元にある安心感** → ローカルMarkdownだからどこでも使えるし消えない
* **知識がつながっていく体験** → バックリンクとグラフビューが思考を可視化してくれる
* **拡張性の高さ** → Claude MCP連携みたいな面白いこともできる

「ただのメモアプリ」から「AI連携できる自分専用の知識OS」まで育てられる、というのがObsidianの一番の魅力だと思います。

ぜひ試してみてください！

---

*この記事はObsidian + Claude Desktop MCP連携の実運用から生まれたメモをもとに書きました。*
