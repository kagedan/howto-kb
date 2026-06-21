---
id: "2026-06-20-aiに実用ツールを作って本番に出してと丸投げしてみたclaude-code-kamuidash-01"
title: "AIに「実用ツールを作って本番に出して」と丸投げしてみた（Claude Code × KamuiDash）"
url: "https://zenn.dev/kamuidash/articles/8010bae646cabc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Python", "zenn"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

この記事は[前回](https://zenn.dev/kamuidash/articles/6a673850634039)の続きです。前回簡単なレスポンスを返すバックエンドのホストでしたが、今回はそのアプリをリッチにしてみました。

## 要約

* Claude Code に**1本のプロンプトで丸投げ**したら、「公開エンドポイントの稼働モニター」が本番公開まで進みました。実装、デプロイ、独自ドメイン設定、までAIが自走。
* 中身は FastAPI + マネージド PostgreSQL。監視先 URL を登録すると 5 分おきに死活と応答時間を記録し、ダッシュボードにグラフ表示します。今 [monitor.kamui.online](https://monitor.kamui.online) で動いています。
* KamuiDash は MCP 対応なので、`create_app`（DB 接続込み）やデプロイ確認まで Claude Code から呼べます。`git push` で自動再デプロイ。

## やったこと：開発を Claude Code に丸投げ

最近は実装を AI に任せる人が増えましたが、「じゃあデプロイや運用設定まで丸ごと任せたらどこまで行ける？」を試したくなりました。そこで、前に作った Hello アプリの延長で、**ちゃんと使える小さなツール**を 1 つ、Claude Code に丸投げで作ってもらうことにしました。

題材は「公開エンドポイントの稼働モニター」。登録した URL を定期的に叩いて、応答時間と死活（UP/DOWN）を記録し、グラフで見せるツールです。地味だけど開発者なら一度は欲しくなるやつですね。

## 投げたのは、これ1本

Claude Code に渡したのは、ざっくり次のような 1 プロンプトだけです（要点を抜粋）。

> 公開エンドポイントの「稼働モニター」を新規で作って、KamuiDash に本番デプロイするところまで丸ごとやって。
>
> * URL を登録・一覧・削除できる Web ページ
> * サーバが 5 分おきに HTTP GET して、ステータス・応答時間・時刻を記録
> * ダッシュボードに UP/DOWN・直近の応答時間・折れ線グラフ（Chart.js）
> * データはマネージド PostgreSQL
> * 起動は `python main.py`、`/health` あり
> * GitHub（kamuiplatform 配下）に push して、KamuiDash MCP で DB 作成＋`create_app`＋デプロイ＋動作確認まで

## AI が自走した範囲

ここからはほぼ見ているだけでした。Claude Code は、

1. 作業ディレクトリを用意し、`gh` のログインアカウントを確認
2. KamuiDash のマネージド DB が注入する接続用環境変数を調べてコードを合わせる
3. FastAPI + Chart.js でアプリを実装し、ローカルでテスト
4. `kamuiplatform/endpoint-monitor` を作って push
5. （人間ステップを挟んで）`create_app` で DB に接続してデプロイ
6. 独自ドメインを設定し、SSL を発行、TXT 伝播まで確認
7. `/health` 200・SSL 発行済み・ダッシュボード表示を検証して報告

までを通しでやってくれました。

**cron の判断も任せた**ところ、「アプリ内スケジューラ（asyncio、5 分間隔）を主にしつつ、`/cron/check` も用意して外部スケジューラからも叩けるように。replicas は 1 なので二重実行しない」と、こちらが指定しなくても理由つきで構成してくれました。

![](https://static.zenn.studio/user-upload/6b35959efe3f-20260620.png)

## 結果：ちゃんと動く実用ツールが本番に

今 [monitor.kamui.online](https://monitor.kamui.online) で動いています。試しに 2 つの公開サイト（実際に我々が運用中のサイト）を登録してみたところ、どちらも UP・HTTP 200 で、応答時間の推移がグラフで見えています（東京リージョンの KamuiDash Dashboard は ~220ms 台、別サイトは ~600ms 台）。  
![](https://static.zenn.studio/user-upload/e62ac744325a-20260620.png)

SSL も自動発行され（発行元 Google Trust Services）、`git push` すれば以後は自動で再デプロイ。無料プランでもスリープしないので、定期チェックを動かし続ける用途とも相性が良いです。

## まとめ

「実用ツールを作って本番に出して」と 1 プロンプト投げただけで、FastAPI + Postgres の稼働モニターが独自ドメイン＋SSL付きで公開できました。実装からデプロイ、運用設定までを AI がほぼ自走し、人間は権限・認証の 3 ステップだけ。

"丸投げでも、認証と権限まわりだけは人間"という線引きが見えたのが個人的な収穫です。逆に言えば、そこさえ通せば、AI コーディングの勢いを止めずに本番運用まで持っていけます。

KamuiDash は無料で試せます。手元のアイデアを AI ごと本番に出してみたい人はぜひ。

KamuiDash  
<https://kamui-platform.com/ja/>

MCP セットアップ  
<https://docs.kamui-platform.com/ja/mcp.html>
