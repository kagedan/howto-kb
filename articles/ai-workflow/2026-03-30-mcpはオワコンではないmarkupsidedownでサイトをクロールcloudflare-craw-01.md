---
id: "2026-03-30-mcpはオワコンではないmarkupsidedownでサイトをクロールcloudflare-craw-01"
title: "MCPはオワコンではない。MarkUpsideDownでサイトをクロール（Cloudflare /crawl endpoint）した話。"
url: "https://zenn.dev/jphfa/articles/markupsidedown-mcp-crawl-events"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

```
Before: curl → ポーリング → JSON取得 → 手動変換 → 保存 → バリデーション（8ステップ）
After:  /crawl-events gewoelbe.ticket.io（1コマンド）
```

[ケルンのクラブのイベントカレンダー](https://cologne.ravers.workers.dev)を更新するのに8ステップの手作業を踏んでいました。環境変数の管理、curlコマンドの組み立て、ポーリング、JSONの手動変換。やりたいことは「URLを渡してイベントデータを得る」だけなのにインフラの都合に付き合わされていました。

これを1コマンドに変えた話です。使ったのは自作のMarkdownエディタ[MarkUpsideDown](https://github.com/M-Igashi/MarkUpsideDown)のMCP機能と、Claude Codeのカスタムコマンド。

## MarkUpsideDownとは

MarkUpsideDownはあらゆるMarkupをMarkdownに変換するデスクトップエディタです。Tauri v2 + Cloudflare Workers AIで動いています。

<https://github.com/M-Igashi/MarkUpsideDown>

Webページ、PDF、Office文書、画像 — 何でもMarkdownにします。詳しくは[開発マニフェスト記事](https://zenn.dev/jphfa/articles/markupsidedown-development-manifesto)に書きましたが、今回注目するのは **MCPサーバー機能** です。

MarkUpsideDownはRust製のMCPサーバーを内蔵しており、41のツールを公開しています。Claude Code、Claude Desktop、Coworkなど **どのMCPクライアントからでも同じツール群にアクセスできます**。エディタの全機能がAIエージェントの「手」になる設計です。

その中にクロール関連のツールがあります。前回curlで叩いていたBrowser Rendering APIを、MCPツールとしてラップしたものです。

| ツール | 役割 |
| --- | --- |
| `crawl_website` | Browser Renderingでサイトをクロール（JSON Schema付き構造化抽出対応） |
| `crawl_status` | クロールジョブの進捗確認・結果取得 |
| `crawl_save` | クロール結果をローカルMarkdownファイルとして保存 |
| `extract_json` | 単一ページからAIで構造化JSONを抽出 |
| `get_markdown` | URLをMarkdownとして取得（静的/動的ページ自動判定） |

このうち`get_markdown`や`crawl_save`はUI上のクロール機能と同じMarkdown変換パイプラインを使いますが、`extract_json`や`crawl_website`のJSON出力は **MCPからのみアクセスできる機能** です。UIはMarkdownエディタとしてのマニフェストに従いJSONを扱いません。この設計上の意図については後述します。今回はClaude Codeから使います。

## Before: curlで8ステップ

Cloudflare Browser Rendering `/crawl` APIは強力です。[前回の記事](https://zenn.dev/jphfa/articles/cloudflare-browser-rendering-crawl-api)ではcurlで直接叩いてイベント情報を抽出しました。URLとJSON Schemaを投げるだけで構造化データが返ってくる体験は衝撃的でした。

しかし実際の運用はこうなります：

1. 環境変数を設定（アカウントID + APIトークン）
2. curlでクロールジョブを投入
3. ジョブIDをコピー
4. ポーリング（10秒待って再実行を繰り返す）
5. 完了後に結果を取得
6. JSONをプロジェクトフォーマットに手動で変換
7. `data/`ディレクトリに保存
8. バリデーション実行

動きます。動きますが **8ステップの手作業** です。新しいヴェニューを追加するたびにこれを回すのはなかなか面倒でした。

## After: 1コマンドで完了

同じことをMarkUpsideDownのMCPツール経由でClaude Codeに任せます。以下はケルンのクラブ [Gewölbe](https://gewoelbe.ticket.io) のイベントカレンダーを実際に更新したときの **本物のワークフロー** をお見せします。[cologne-raves](https://github.com/M-Igashi/cologne-raves)プロジェクトで運用しています。

### Step 1: カスタムコマンドで構造化抽出

Claude Codeに対して：

```
/crawl-events gewoelbe.ticket.io
```

これはClaude Codeのカスタムコマンドです。ツール選択・フォールバック・フォーマット変換・重複チェック・保存・バリデーションまでの全ワークフローが定義されています。Claude Codeが MarkUpsideDown の`extract_json`ツールを呼び出します。

```
extract_json(
  url: "https://gewoelbe.ticket.io",
  prompt: "Extract all upcoming events. For each event, extract: title,
           date (ISO 8601 format YYYY-MM-DD), start time (HH:MM format),
           artists/DJs performing, and the ticket URL.",
  response_format: '{"type":"object","properties":{"events":{"type":"array",
    "items":{"type":"object","properties":{"title":{"type":"string"},
    "date":{"type":"string"},"start_time":{"type":"string"},
    "artists":{"type":"array","items":{"type":"string"}},
    "ticket_url":{"type":"string"}},"required":["title","date"]}}}}'
)
```

APIトークンの設定もポーリングも不要です。`extract_json`はBrowser RenderingでJSをレンダリングし、Workers AIのLLM推論でJSON Schemaに従った構造化データを生成して、結果を一発で返します。なぜ認証が不要なのかは後述するアーキテクチャのセクションで説明します。

### Step 2: 結果 — 実データ

実際に返ってきたJSONがこれです（15件中抜粋）：

```
{
  "events": [
    {
      "title": "IPSO w/ Kölsch, Jonathan Kaspar",
      "date": "2026-05-08",
      "start_time": "23:00",
      "artists": ["Kölsch", "Jonathan Kaspar"],
      "ticket_url": "https://gewoelbe.ticket.io/NmKjL6Eh/"
    },
    {
      "title": "The Third Room w/ .VRIL, Ahmet Sisman, Elisen",
      "date": "2026-05-09",
      "start_time": "23:00",
      "artists": [".VRIL", "Ahmet Sisman", "Elisen"],
      "ticket_url": "https://gewoelbe.ticket.io/9G48bcwt/"
    },
    {
      "title": "Klubnacht w/ Âme live, Marcus Worgull",
      "date": "2026-05-15",
      "start_time": "23:00",
      "artists": ["Âme live", "Marcus Worgull"],
      "ticket_url": "https://gewoelbe.ticket.io/MYAqljHM/"
    }
  ]
}
```

Kölschのウムラウト、Âmeのアクセント記号、`.VRIL`のドット — 特殊文字も正確に抽出されています。これはBrowser RenderingがヘッドレスブラウザでJSを実行した後に、Workers AIがDOMを解析して構造化しているからです。正規表現のスクレイピングでは一生到達できない精度です。

### Step 3: 差分検出と保存

Claude Codeが抽出結果を既存データ（19件）と照合し、**5件の新規イベント** を検出しました。

| 日付 | イベント | アーティスト |
| --- | --- | --- |
| 05/02 | Remember the Future | Luke Alessi, Shumi |
| 05/08 | IPSO | Kölsch, Jonathan Kaspar |
| 05/09 | The Third Room | .VRIL, Ahmet Sisman, Elisen |
| 05/15 | Klubnacht | Âme live, Marcus Worgull |
| 05/29 | Schleuse Eins | evolpeeD, Victor |

プロジェクトのフォーマットに変換し、`data/`ディレクトリに追加。`npm run build`でバリデーション。すべて自動です。

**人間がやったことは`/crawl-events gewoelbe.ticket.io`と打っただけです。** 1コマンド。裏では同じBrowser Rendering APIが動いています。変わったのはMarkUpsideDownがAPIとの対話をMCPツールとして抽象化しClaude Codeがオーケストレーションを担当するようになったことです。

## 技術的な仕組み — なぜ認証不要なのか

MarkUpsideDownのMCPサーバーはRustで書かれたスタンドアロンバイナリです。Tauriサイドカーとしてバンドルされ、stdio経由でMCPクライアントと通信します。

ポイントは、MCPサーバーが直接Cloudflare APIを叩くのではなく、**MarkUpsideDownのWorker経由でリクエストする** ところです。これにより：

* **認証の一元管理** — APIトークンはWorkerのシークレットに格納されます。MCPサーバーもユーザーもトークンを意識しません
* **レート制限のサーバーサイド管理** — Workerがリクエスト間隔を制御します
* **レスポンスの正規化** — Worker側でMarkdownの正規化（見出し階層の修正、空リンクの除去、テーブル整形など）を適用してから返します

curlで直接APIを叩く場合認証・レート制限・レスポンス処理のすべてがクライアント側の責任です。MarkUpsideDownはこれをWorkerに吸収し、MCPツールのインターフェースをシンプルに保っています。

## ツール設計 — 使い分けとフォールバック

今回は`extract_json`を使いましたがMarkUpsideDownのMCPツール群は複数の変換パスを持っておりサイトの特性に応じて使い分けられます。

| ツール | 出力 | 動作 | 適するケース |
| --- | --- | --- | --- |
| `extract_json` | JSON | 1ページ → 即結果 | 一覧ページに全情報がある場合（今回） |
| `crawl_website` | JSON or MD | 複数ページ → ジョブ管理 | 個別ページまで辿る必要がある場合 |
| `get_markdown` | Markdown | 1ページ → 即結果 | Schema不要、意味的なフィルタが必要な場合 |

`get_markdown`でMarkdownを取得してClaude Codeに解析させるアプローチは一見回りくどいですが、「4月以降のイベントだけ」「テクノ系のイベントだけ」といった **意味的なフィルタリング** はJSON Schemaでは表現できません。Claude Codeなら自然言語で指示できます。

サイトによってはクロールが失敗することもあるためこれらのツールはフォールバックチェーンとしても機能します。

```
1. extract_json   — 一覧ページから構造化JSON（最速）
       ↓ 失敗
2. crawl_website  — 複数ページのフルクロール
       ↓ 失敗
3. get_markdown   — Markdownとして取得 → Claude Codeが解析
       ↓ 失敗
4. ユーザーに手動入力を依頼
```

`get_markdown`は静的ページにはCloudflare Markdown for Agentsのヘッダー、動的ページにはBrowser Renderingの`/content`エンドポイントを自動判定して使います。[マニフェスト記事](https://zenn.dev/jphfa/articles/markupsidedown-development-manifesto)で書いた3段階の変換パイプライン — Markdown for Agents → Workers AI → Browser Rendering — がMCPツールとしてもそのまま機能しています。

今回の`/crawl-events`コマンドはこのワークフロー全体 — ツール選択 → フォールバック → フォーマット変換 → 重複チェック → 保存 → バリデーション — をClaude Codeのカスタムコマンドとして定義したものです。

## UIが扱わないJSON — MCPの本質

ここで重要な事実を明かします。**MarkUpsideDownのUI上にJSON出力機能はありません。**

[開発マニフェスト](https://zenn.dev/jphfa/articles/markupsidedown-development-manifesto)で宣言した通りMarkUpsideDownは「あらゆるMarkupをMarkdownに変換するエディタ」です。UIが扱うのはMarkdown。JSONではありません。

しかしMCPツールの`extract_json`はJSON Schemaに従った構造化データを返します。**UIのマニフェストが「やらない」と宣言した機能をMCPは提供しています。**

矛盾ではありません。MCPが公開しているのはUIではなく **機能（capability)** だからです。

```
Cloudflare Browser Rendering API
├── /content (Markdown)  ← UI ✓  MCP ✓
├── /crawl (Markdown)    ← UI ✓  MCP ✓
├── /crawl (JSON)        ← UI ✗  MCP ✓ ← crawl_website
└── /json (JSON)         ← UI ✗  MCP ✓ ← extract_json
```

UIは「Markdownエディタ」というマニフェストに忠実であるべきです。JSONの構造化抽出をUIに入れれば便利かもしれませんがそれはエディタの責務ではありません。しかしCloudflareが提供するJSON抽出の力を使えないのはもったいない。MCPがこの問題を解決します。UIの設計思想を一切侵食せずにCloudflareの機能をフルカバーする。MCPサーバーはUIの「リモコン」ではなく **アプリケーションが持つ全機能のプログラマブルなインターフェース** です。

### 「MCPはオワコン」なのか

「MCPはオワコン」「ただのJSON-RPCの再発明」「関数呼び出しで十分」といった論争があります。この議論が見落としているのはMCPがUIの代替ではなく **UIでは提供できない（あるいは提供すべきでない）機能を公開するレイヤー** だということです。

* UIは「Markdownエディタ」というマニフェストを守る。JSONは扱わない
* MCPは **Cloudflare Browser Renderingの全機能** をAIエージェントに公開する。JSONも扱う
* この2つは矛盾せず **補完関係にある**

MCPなしでJSON抽出機能をどこに置くか。UIに入れればマニフェストに反する。CLIを作ればメンテナンスが増える。REST APIを立てればサーバー運用が必要。MCPなら **既存のWorkerとMCPサーバーバイナリだけで追加のインフラなしに機能を公開できます。**

MCPの価値は「チャットUIからツールを呼べること」ではありません。**アプリケーションの設計思想を守りながらその全機能をプログラマブルに公開できること**。これは関数呼び出しの話ではなくソフトウェアアーキテクチャの話です。

## まとめ

ケルンのクラブGewölbeのイベントカレンダーを`/crawl-events gewoelbe.ticket.io`の1コマンドで更新しました。15件を構造化抽出し5件の新規イベントを追加。ビルド確認まで完了。

この実践を通じてわかったのはMCPの価値が「チャットUIからツールを呼べること」にあるのではないということです。**アプリケーションの設計哲学を守りながらその全機能をプログラマブルに公開できること** — これがMCPの本質でありオワコンどころかまだ本領を発揮し始めたばかりです。

MarkUpsideDownはmacOS（Apple Silicon）対応。`brew install`ですぐ試せます。

```
brew install M-Igashi/tap/markupsidedown
```

<https://github.com/M-Igashi/MarkUpsideDown>
