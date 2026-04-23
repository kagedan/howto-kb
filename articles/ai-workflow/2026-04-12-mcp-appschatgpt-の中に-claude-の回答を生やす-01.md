---
id: "2026-04-12-mcp-appschatgpt-の中に-claude-の回答を生やす-01"
title: "【MCP Apps】ChatGPT の中に Claude の回答を生やす"
url: "https://zenn.dev/peintangos/articles/85d704b3c3ecd9"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "LLM", "GPT", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

どうも！peitangosです。

「MCP Apps」で少し遊んでみたら意外と面白かったので、記事にしてみました。  
今回やったことを一言で言うと、「ChatGPT の会話の中に Claude の回答をカードとして生やしてみた」です。

ChatGPT に何かを質問すると、ChatGPT 自身の回答に加えて「Claude の答え」というオレンジのカードが同じ会話内にもう 1 枚ぽこっと出てきます。ライバルベンダー同士の LLM を 1 つの UI で同居させる構造です。

![ChatGPT の中で Claude の回答カードが描画されている様子](https://static.zenn.studio/user-upload/deployed-images/fde5b126b9d795f70d25a2e7.gif?sha=3824d06dd6a8487cf5a200353f5f24ade3369485)

## はじめに

まず出発点の理解を合わせておきます。

2026 年 1 月 26 日、MCP Apps（SEP-1865, `io.modelcontextprotocol/ui`）は MCP の最初の公式拡張として公開されました。提案そのものは 2025 年 11 月に出ていて、そこから仕様と実装が整ってきた、という流れです。

MCP 自体をざっくりおさらいしておくと、LLM ホスト（Claude Desktop、ChatGPT など）と外部ツールをつなぐ共通プロトコルです。いわば「AI 版の LSP」みたいな立ち位置で、サーバー側が tool を 1 つ登録すれば、対応ホストからそのツールを呼べる、というやつですね。

で、MCP Apps というのはその上に乗る UI 拡張で、一言で言うと、

> MCP サーバーが HTML ベースの UI リソースを返せるようにして、ホスト側はそれを sandboxed iframe で描画する

という仕組みです。ツール呼び出しの結果がテキストや JSON だけじゃなくて、リッチな UI コンポーネントになります。公式ドキュメントでも、UI リソースは `text/html;profile=mcp-app` として扱われ、ホストが iframe で安全にレンダリングする前提になっています。

しかも設計思想としては「一度宣言した UI を、対応ホストで再利用できる」方向がはっきり打ち出されています。  
今回はこの「ホストをまたいで UI を持ち運べる」という特性を活かして、ChatGPT の中で Claude の回答カードを描画させてみます。

## その機能が解こうとしている課題

そもそもなんでこんな拡張が入ったのかという話です。

MCP は登場してしばらくの間、ツール呼び出しの結果として主にテキストや structured data を返す形が中心でした。  
これだとたとえば「GitHub のリポジトリ一覧をリッチな表で出したい」とか「地図を埋めたい」とか「グラフを出したい」とかをやろうとしたとき、ホスト側が独自に UI を解釈・描画する必要がありました。MCP Apps の公式 overview でも、以前はホストごとに UI サポートがバラバラで、サーバー開発者が別々の実装を抱えがちだったことが課題として説明されています。

* ホスト A: Markdown テーブルとして描画
* ホスト B: 独自 UI でカードとして描画
* ホスト C: 何もしない（生 JSON が見える）

これ、ツール開発者から見ると「どのホストでどう見えるか」がかなり運に左右されます。  
MCP Apps はこの問題をシンプルに解決していて、ツール側が UI リソースを宣言すれば、対応ホストはそれを共通ルールで描画する、という形に寄せています。

つまり、レンダリングの責任がある程度ホストからツール側へ移った、というのが本質です。  
ツール開発者は自分が期待する見た目を自分で持てるようになり、代わりにホストは「安全に iframe を表示し、ホストと UI の間を仲介する」ことに集中できます。

この「ホストを越境して同じ UI を使いやすくする」という性質があるからこそ、今回のネタである「ChatGPT の会話の中で Claude の回答カードを描画する」という仕組みを成立させています。

## なにをしたか

ここからが本題です。

### できあがったもの

完成したのはこういう感じの MCP App です。

1. ChatGPT で「〇〇について教えて、**あと Claude にも聞いて**」と聞く
2. ChatGPT は普通に自分の回答をテキストで返す
3. 同時に `ask_claude` ツールを呼ぶ
4. MCP サーバー（自前 Node.js）が Anthropic API で Claude を叩く
5. Claude の回答を structuredContent として返す
6. ChatGPT の会話内にオレンジのカードとして Claude の回答が生える

冷静に考えると、ChatGPT からバックエンド越しに Claude に問い合わせること自体は以前から構成次第でできました。  
ただ、「UI として会話内に Claude の回答カードを描画する」という体験は、MCP Apps のおかげでかなりやりやすくなった、という感覚です。

### 全体のアーキテクチャ

最終的にクラウドにホストした後の全体像はこんな感じです。

![簡単なアーキテクチャ](https://static.zenn.studio/user-upload/deployed-images/39f2dd2be7ead33438ad289a.png?sha=eb06005ecccec0e3d47f13ca0029c668addea408)

登場人物は 4 つだけです。

1. ChatGPT — ユーザーが質問を打つ場所。MCP クライアントとしてサーバーを叩く
2. MCP サーバー（自前 Node.js, Fly.io にデプロイ）— `ask_claude` ツール / `mcp-app.html` リソース / 認証まわりをまとめて持つ
3. Anthropic API — Claude 本体。MCP サーバーから HTTPS で叩く
4. Anthropic 側の spend limit — 万一に備えるための上限設定

同じ Node.js プロセスがツール実行・UI 配信・認証関連の処理をまとめて受け持つ構成は、MCP の認可仕様とも相性が悪くありません。MCP の authorization spec でも、authorization server は resource server と同居していても、別でもよいとされています。

UI（HTML）の配信まで MCP サーバー側が持つので、普通のフロントエンド + バックエンドの分離とは少し感覚が違います。  
その代わり、対応ホストに対して同じ UI リソースを見せやすい、というのが面白いところです。

### 実装は 4 パーツだけ

中身もシンプルで、大きく分けて以下の 4 ファイルしかありません。

* `server.ts` — MCP サーバー本体。`ask_claude` ツール、`mcp-app.html` リソース、認証ルートの mount を行う
* `src/claude.ts` — Anthropic SDK の薄いラッパー。質問文字列を受け取って Claude の回答を返すだけ
* `src/main.tsx` — React 製 UI。ツール呼び出し結果を受け取ってオレンジのカードを描画するだけ
* `src/oauth.ts` — 最小限の OAuth 対応をまとめた部分

## MCP サーバーをホストする時の注意点

MCP サーバーを公開する際に、いくつか注意したいことがあります。

### 本当に怖いのは「API 課金焼き」

まず、API 課金の爆死リスクです。

想像してください。Fly.io に MCP サーバーを置いて安定 URL を手に入れた → 嬉しい → ついその URL を記事に書く → 悪意ある人がスクリプトで `ask_claude` を秒間 100 発叩く → 自分の `ANTHROPIC_API_KEY` で Claude Opus が無限に呼ばれる → 1 晩で数百ドル。

### まず Anthropic Console の spend limit を入れる

この地雷を踏まないための最後の砦としてかなり効くのが、Anthropic Console の spend limit です。Anthropic の公式ドキュメントでも、API 利用には月次の spend limit があり、Limits ページで確認でき、上限に達すると次の月まで API を利用できなくなると説明されています。

実装コスト 0、画面でポチるだけ、強制的な上限。  
公開するなら真っ先に入れておくべきです。

なお、429 は Anthropic の公式には rate limit 超過時の代表的なエラーとして説明されています。  
spend limit 到達時の HTTP ステータスコードまでここでは断言せず、「上限に達するとその月の API 利用が止まる」と理解しておくのが安全です。

## 認証まわりのちょっとした話

あともう 1 つ、ChatGPT に繋ぐときに地味に面倒だったのが認証です。

ChatGPT の developer mode で remote MCP を app として追加する場合、現行ドキュメントでは認証方式として **OAuth / No Authentication / Mixed Authentication** が案内されています。

![ChatGPT の Authentication ドロップダウン](https://static.zenn.studio/user-upload/deployed-images/4dbabffdb2f1061a75d50d74.png?sha=530e22cda39ffd12a621f8172ec5f91a32ecef41)

というわけで、MCP サーバー側にも認証まわりを用意する必要がありました。  
MCP の authorization spec は OAuth 2.1 ベースで、MCP サーバー側には Protected Resource Metadata（RFC 9728）が必須です。認可サーバー側は Authorization Server Metadata か OpenID Connect Discovery のどちらかを提供する必要があり、Dynamic Client Registration（RFC 7591）は SHOULD とされています。

本気の OAuth プロバイダを作ろうとすると大仕事ですが、自分 1 人が使う前提でかなり割り切ると、思ったよりは小さく収まりました。

触ってみて得た観点をポイントベースで残しておきます。

* ChatGPT 側で remote MCP をつなぐなら、少なくとも現状は OAuth を前提に考えるのが無難
* 個人用途なら Authorization Server と Resource Server を 1 プロセスに同居させる構成も取りやすい
* 同意画面は普通の HTML を 1 枚返すだけでも十分成立する
* トークン保存をどこまで本格化するかは用途次第。個人利用ならかなり割り切れる
* Anthropic 側の spend limit と併用しておくと、万一の被害を絶対額で抑えやすい
* MCP Appsを追加するには「DEVLOPER MODE」にする必要がある。
* Memory は OFFになる。

自作 OAuth サーバーが返す同意画面はこんな感じ。  
`/authorize` に飛んできたときにサーバーが返すだけのシンプルな HTML です。

![自前 OAuth サーバーが描画する同意画面](https://static.zenn.studio/user-upload/deployed-images/3f83619a9ce2ad80b2f663a1.png?sha=47e86b28692e354f4bc76ad6a45d4bcc2c40b132)

## 最後に

いかがでしたでしょうか。  
割と遊び半分でやってみましたが、ライバルベンダーの LLM が 1 枚の UI で握手する体験は意外と未来感があって面白かったです。  
一方で、認可付きの remote MCP サーバーとして公開するなら、OAuth 2.1 ベースの仕様に沿う必要があり、これが思ったより大変でした。

今回やったことを改めて整理すると、

* MCP Apps のおかげで、ツールの結果を iframe でリッチに描画しやすくなった
* 同じ UI リソースを対応ホストで再利用しやすい、という設計になっている
* 公開するなら Anthropic 側の spend limit を真っ先に入れるのが安全
* 開発中は quick tunnel、公開は Fly.io などのちゃんとしたホスティング、という使い分けが落ち着きどころ
* ChatGPT 側で remote MCP をつなぐなら、認証方式は先にちゃんと考えておく必要がある

次は何を書くかまだ決めていないですが、MCP Apps 越しに複数 LLM を束ねる方向はまだまだ掘れそうなので、「LLM 合議制」みたいなネタも面白いかもな〜とぼんやり考えています。

ソースコードはこちら。結構甘々ですがご勘弁ください。  
<https://github.com/peintangos/mcp-apps-sample>

## 参考文献
