---
id: "2026-06-02-figma-の有料席なしでai-にデザインファイルを無料で読ませるtempad-dev-mcp-入門-01"
title: "Figma の有料席なしで、AI にデザインファイルを無料で読ませる：TemPad Dev + MCP 入門"
url: "https://zenn.dev/itsuki_y/articles/71c8c6b34ed4e0"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "zenn"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/3b7e223703be-20260508.png)

## 背景

AI を使って Figma のデザインファイルをコードへ「翻訳」することは、いまのフロントエンド開発で最もよく出てくるニーズの一つです。一般的な方法は次の二つです。

* Figma 公式 REST API を使う：PAT が必要で、Dev Mode の有料席も必要になり、さらにレート制限もあります。
* Figma 公式 MCP（Dev Mode MCP server）を使う：Dev Mode の席が必須です。無料アカウントでは使えず、取得回数にも制限があります。たとえば次のようなメッセージが表示されます。

```
ProfessionalプランのViewシートで利用できる Figma MCP ツールの呼び出し上限に達しました。
```

個人開発者で、しかも無料の Figma アカウントを使っている場合、この二つの方法は高すぎるか、そもそも使えません。そこで第三の選択肢になるのが **TemPad Dev** です。Figma プラグインからローカルの MCP に直接つなぐことで、Codex / Claude Code などのツールがノードのスタイルを直接読めるようになります。**REST API のクォータを消費せず、Dev Mode も不要です**。

## TemPad Dev とは

[TemPad Dev](https://github.com/ecomfe/tempad-dev) は、Figma プラグインとローカル MCP サービスを組み合わせたツールです。

* **Figma プラグイン側**：Figma のサンドボックス内で動き、`figma.*` Plugin API を呼び出して、現在開いているファイルのノードを読み取ります。
* **ローカル hub**：`hub.mjs` という Node プロセスです。WebSocket / Unix socket を起動してプラグインからのデータを受け取り、標準的な MCP ツールとして外部に公開します。
* **MCP ツール**：`get_code`、`get_structure` などです。AI コーディングアシスタントはこれらのツールを通じて、ノードのスタイル、コンポーネント構造、SVG アセットを取得します。

要するに、**「AI が Figma のノードを読みたい」という処理を、「Figma のクラウド API を呼ぶ」方式から、「ブラウザですでに開いているファイルをローカル経由で読む」方式に変える**ということです。

## 仕組み

TemPad Dev は単体のプログラムではありません。**三つのプログラムが連携して動きます**。

### 三つの役割と配置

![](https://static.zenn.studio/user-upload/df169ce6518c-20260508.png)

### 全体構成図

![](https://static.zenn.studio/user-upload/7ce5f312dbad-20260508.png)

### 一回の呼び出しの流れ：Codex で「この Figma リンクを読んで」と言った場合

各ノードは、それぞれ一つの役割だけを担当します。

1. Codex に「この Figma リンクを読んで」と依頼すると、Codex は `get_code` を呼び出すと判断し、MCP プロトコル経由で hub にリクエストを送ります。
2. hub は自分では Figma を読みません。受け取ったリクエストを、WebSocket の向こう側にいるプラグインへ渡します。
3. プラグインは Figma のサンドボックス内で動いているため、`figma.getNodeById(...)` のような API を呼び出してノードを直接読みます。
4. サイズ、色、フォントなどのスタイル属性が Figma のメモリから取り出され、プラグインへ戻ります。
5. プラグインはそのデータを WebSocket 経由で hub に返します。
6. hub は MCP 経由で結果を Codex に返します。Codex は受け取ったスタイル情報をもとにコードを書き始めます。

### 重要なポイントは三つ

1. **データの入口はブラウザ**：ユーザーはすでに Figma にログインし、対象ファイルを開いています。ノードツリーはブラウザ上にあり、プラグインがそこを直接読みます。
2. **データの出口はローカル**：hub がローカルの WebSocket を起動し、AI アシスタントは MCP プロトコルで接続します。基本的な経路はローカル内で完結します。
3. **Figma のサーバー API を呼ばない**：そのため REST API のクォータを消費せず、Dev Mode の有料機能にも依存しません。

## インストールと設定

前提環境は Node 18+、Chrome、そして Figma Web 版が問題なく使えることです。

### Step 1：Figma プラグインをインストールする

Figma Community で TemPad Dev を検索し、Save を押します。その後、読み取りたいファイル内でプラグインを Run します。プラグインのパネルには、ローカル hub への接続状態と MCP server のスイッチが表示されます。

![](https://static.zenn.studio/user-upload/9bafc3aa0d17-20260508.png)

### Step 2：AI コーディングアシスタントで MCP を設定する

Codex の場合は、`~/.codex/config.toml` を編集します。

```
[mcp_servers.tempad-dev]
command = 'npx'
args = ['-y', '@tempad-dev/mcp']
```

Claude Code の場合は、`~/.claude.json` に `mcpServers` を追加します。

```
{
  "mcpServers": {
    "tempad-dev": {
      "command": "npx",
      "args": ["-y", "@tempad-dev/mcp"]
    }
  }
}
```

初回起動時には、npx が自動的にパッケージを取得して `hub.mjs` を起動します。hub は 6220（WebSocket）と、アセット用 HTTP server のランダムなポート（例：58946）を listen します。

### Step 3：接続を確立する

次の順序で操作します。

1. Chrome で読み取りたい Figma ファイルを開きます。
2. そのファイル内で TemPad Dev プラグインを一度 Run し、パネル内の MCP server スイッチをオンにします。これにより、Figma サンドボックス内のプラグインがローカル hub に WebSocket で接続します。

![](https://static.zenn.studio/user-upload/6ba00501327c-20260508.png)

3. Codex / Claude Code を起動します。これらは MCP client として同じ hub に接続します。

hub のログに `Extension connected` と `Auto-activated sole extension` が表示されれば、三者のハンドシェイクは完了です。ここからツールを呼び出せます。

## 実際に呼び出してみる

TemPad Dev が公開している中心的なツールは二つです。

`get_structure`：選択中ノードの階層構造を返します。ノードタイプ、命名、ネスト関係などを取得できるため、AI にまずコンポーネント構造を理解させる用途に向いています。

`get_code`：選択中ノードの具体的なスタイルデータを返します。サイズ、座標、padding、gap、角丸、背景色、フォント、行高、ウェイト、token 解決後の変数値、エクスポートされた SVG アセットのリンクなどが含まれます。

Codex での典型的な対話フローは次のようになります。

![](https://static.zenn.studio/user-upload/c641968918bf-20260508.png)

AI により正確に使わせるためのコツもあります。

* **先にノードを選択してから質問する**：プラグインが読むのは Figma の現在の selection です。何も選択していないと取得できません。
* **複雑なコンポーネントは分割して読む**：十数階層にネストしたページ全体を一度に変換させると context が膨らみます。区画ごとに `get_code` するほうが安定します。
* **SVG はアセット URL 経由で扱う**：アイコンノードは `http://127.0.0.1:58946/...` のようなリンクとして返されます。AI に「ダウンロードして `src/icons` に保存して」と依頼すれば十分です。

## 注意点と制約

1. **すでに開いているファイルだけを読める**：プラグインはブラウザ内の Figma セッションに依存します。ファイルを開いていない、ログインしていない、アクセス権がない、といった場合は失敗します。権限のない非公開ファイルを読むための抜け道ではありません。
2. **大きなノードでは重くなる**：Plugin API で数千ノードを走査すると、Figma UI が数秒固まることがあります。複雑なページでは frame ごとに分けて呼び出すのがおすすめです。
3. **公式ソリューションではない**：他のサードパーティ製プラグインと同じく、更新頻度、安定性、今後の Figma 側のポリシー変更には不確実性があります。重要なプロジェクトでは、公式 API を使う退路も残しておくと安心です。

## まとめ

TemPad Dev の価値は、「AI が Figma を読む」ための入口を、有料のサーバー API から、無料で使えるブラウザ上の Plugin API に置き換えられることです。個人開発者や小規模チームにとっては、次のメリットがあります。

* 無料アカウントでも、AI がスタイル、token、変数、SVG を正確に読める。
* REST API のレート制限に引っかからない。
* Dev Mode の有料席がなくても、AI コーディングアシスタントと Figma の距離をかなり近づけられる。

無料枠で試せる構成としてはかなり実用的です。Figma からコード化する作業を AI に任せたい場合、まず試す価値があります。
