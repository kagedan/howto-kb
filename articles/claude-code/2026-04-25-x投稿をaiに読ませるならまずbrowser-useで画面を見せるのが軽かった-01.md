---
id: "2026-04-25-x投稿をaiに読ませるならまずbrowser-useで画面を見せるのが軽かった-01"
title: "X投稿をAIに読ませるなら、まずBrowser Useで画面を見せるのが軽かった"
url: "https://zenn.dev/yamk/articles/xmcp-vs-computer-use-x-research"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

X Developer Platform が [XMCP](https://github.com/xdevplatform/xmcp) を公開しています。

XMCP は、X API の OpenAPI spec を読み込んで、投稿検索、ユーザー取得、投稿作成などを MCP tool として公開できるローカル MCP サーバーです。AI エージェントから X API を直接呼べるようになるので、かなり面白いです。

ただ、調べていて最初に引っかかったのがこれでした。

> 特定の X 投稿を読ませたいだけなら、X API まで使わなくてもよくない？

ここでいう「読ませたい」は、X の投稿 URL をチャットに貼るだけ、という意味ではありません。X は動的ページなので、URL を貼っただけで LLM が安定して本文を読めるとは限りません。

今回の話は、**Browser Use / Computer Use で実際にブラウザを開き、画面に表示された投稿を AI に読ませる**という意味です。

この記事では、XMCP と Computer Use / Browser Use の使い分けを整理します。

## XMCP でできること

XMCP は X API 用の MCP サーバーです。

ローカルで起動すると、デフォルトで次の endpoint が立ちます。

```
http://127.0.0.1:8000/mcp
```

MCP クライアント側にこの URL を登録すると、AI エージェントから X API を tool call として呼べます。

たとえば、以下のような操作ができます。

* ユーザー情報を取得する
* 投稿を検索する
* 投稿 ID から投稿を取得する
* 自分のタイムラインを取得する
* 投稿する
* いいねする
* リポストする
* follow / unfollow する

公式 docs でも、XMCP は X API endpoint を callable tools として公開する official MCP server と説明されています。

## ただし X API は pay-per-use

XMCP 自体は GitHub で公開されているコードですが、実際に X API を呼ぶには X Developer Console で app を作り、credentials を用意する必要があります。

X 公式 docs では、現在の X API は pay-per-use pricing と説明されています。

大まかな流れはこうです。

1. X Developer Console に入る
2. Developer account を作る
3. Project / App を作る
4. API Key、API Secret、Bearer Token を取得する
5. 必要に応じて API credits を購入する
6. XMCP の `.env` に credentials を入れる
7. `python server.py` でローカル MCP サーバーを起動する

つまり、特定投稿を1つ画面で確認して要約したいだけの用途に対しては、少し重いです。

誤解しない方がよいのは、**XMCP が有料というより、裏側で使う X API が pay-per-use** という点です。

## URLを貼るだけでは読めないことがある

以前、ターミナルで起動した Claude Code に X の投稿 URL を渡して読ませようとしたことがあります。

そのときはうまく読めませんでした。

これは自然な挙動です。X の投稿ページは JavaScript で描画され、ログイン状態、表示制限、bot 判定、rate limit などにも影響されます。単純に URL を渡しただけでは、投稿本文や画像、スレッド文脈まで安定して取れるとは限りません。

つまり、次の2つは別物です。

| 方法 | 期待できること |
| --- | --- |
| チャットに X の URL を貼るだけ | 読めないことがある |
| Browser Use / Computer Use で実際にページを開く | 画面に表示された範囲なら読めることがある |

今回うまくいったのは、URL を貼ったからではなく、Codex の in-app browser で X の投稿ページを実際に開き、DOM とスクリーンショットで表示内容を確認できたからです。

## 特定投稿を画面で確認するだけなら Browser Use で十分

今回試したかったのは、X の特定投稿をブラウザで開き、画面に表示された内容を AI に読ませることでした。

対象は Google Cloud Tech の投稿です。

```
https://x.com/GoogleCloudTech/status/2047377692488601949
```

Codex の in-app browser で投稿 URL を開くと、ログインしていない状態でも投稿本文、画像、投稿日時、表示数、いいね数などが見えました。

この程度の確認なら、X API は不要です。

Browser Use / Computer Use でできたこと:

* 投稿 URL を開く
* 投稿本文を読む
* 画像の内容を確認する
* 投稿日時を見る
* 返信数、リポスト数、いいね数、ブックマーク数、表示数を見る
* その場で要約する

実際の投稿は、Google Cloud Tech が Agent Skills の公式 GitHub repository を公開した、という内容でした。添付画像には `github.com/google/skills.git` 由来の skills 一覧らしき CLI 画面が表示されていました。

## この用途で XMCP を使うと何が重いか

XMCP を使う場合、次の準備が必要です。

* X Developer Console への登録
* Developer app の作成
* callback URL の設定
* OAuth / Bearer Token などの credentials 管理
* API credits / billing の確認
* ローカル MCP サーバーの起動
* MCP クライアント設定
* tool allowlist の設定

もちろん、これは API 連携としては正しい手順です。

しかし「ブラウザで表示できる1投稿を要約したい」だけなら、準備の方が大きくなります。

## Browser Use / Computer Use が向いているケース

以下の用途なら、まず Browser Use / Computer Use でよいと思います。

* 特定の投稿 URL を開いて画面上の内容を読む
* スレッドをざっと追う
* 投稿画像を確認する
* 引用や返信を数件見る
* アカウントの直近投稿を見る
* X 検索で雰囲気を見る
* 話題の反応を少量だけ拾う

この場合、AI は人間と同じようにブラウザ上の表示を見て判断します。

API credentials も不要です。X API credits も消費しません。

## XMCP が向いているケース

一方で、次のような用途では XMCP / X API の方が向いています。

* キーワード検索を構造化して繰り返したい
* 一定件数の投稿を集めたい
* 投稿 ID、ユーザー ID、metrics を正確に扱いたい
* pagination しながらデータ収集したい
* 投稿を分類・集計したい
* 定期実行や監視に組み込みたい
* 自動投稿など write 操作をしたい

ブラウザ操作は、画面に見える範囲を読むには便利です。しかし、大量取得や定量分析には向いていません。

そこは API の領域です。

## 使い分け

自分の中では、こう整理しました。

| やりたいこと | 向いている手段 |
| --- | --- |
| 特定投稿を画面で読む | Browser Use / Computer Use |
| 投稿画像を見る | Browser Use / Computer Use |
| スレッドをざっと確認する | Browser Use / Computer Use |
| X 上の雰囲気を見る | Browser Use / Computer Use |
| 大量の投稿を集める | XMCP / X API |
| 検索結果を構造化して保存する | XMCP / X API |
| metrics を正確に集計する | XMCP / X API |
| 投稿・いいね・follow などを自動化する | XMCP / X API |

軽い調査は Browser Use / Computer Use。

構造化取得や継続運用は XMCP / X API。

この分け方が現実的だと思います。

## 注意点

Browser Use / Computer Use には限界もあります。

* ログイン状態に依存する
* X の UI 変更に弱い
* 表示されない metadata は取れない
* 大量取得には向かない
* 検索結果の網羅性は保証できない
* URL を貼るだけで読めるわけではない
* 画面に表示できない投稿は読めない
* 投稿、いいね、フォローなどの操作は誤操作リスクがある

特に、AI にブラウザ操作をさせる場合は、書き込み操作を勝手に実行させない方がよいです。

読むだけなら軽いですが、投稿する、いいねする、フォローする、DM する、フォーム送信する、といった操作は別物です。

## まとめ

XMCP は X API を MCP tool として扱えるので、かなり強力です。

ただし、X API の準備や pay-per-use の前提を考えると、すべての X 調査に XMCP を使う必要はありません。

特定投稿を画面で読む、画像を見る、スレッドを少し追う、数件の反応を確認する。そういう用途なら Browser Use / Computer Use の方が速くて軽いです。

一方で、大量収集、定量分析、継続監視、自動投稿のような用途になったら XMCP / X API を使う価値が出ます。

MCP を使うかどうかよりも、まずは調査の粒度に合った道具を選ぶのが大事です。

## 参考リンク
