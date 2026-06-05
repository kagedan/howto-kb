---
id: "2026-06-04-claude-managed-agentsでまずエンジニアに聞こうをまずbotに聞こうに変えた-01"
title: "Claude Managed Agentsで「まずエンジニアに聞こう」を「まずbotに聞こう」に変えた"
url: "https://zenn.dev/dinii/articles/d7be3acc43d868"
source: "zenn"
category: "claude-code"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "TypeScript"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

## はじめに

ダイニーでは、開発チーム宛ての質問（社内では dev-help と呼んでいます）が日に8件ほど来ます。1件 10 分でも、積み上がれば月に数十時間が消えていきます。[前回の記事](https://zenn.dev/dinii/articles/18128bd1685e2a)では、過去の dev-help チケットを RAG（過去の文書を意味検索で引っ張ってくる仕組み）で引いて関連事例をスレッドに貼る bot を作り、リードタイム中央値を 10 日から 5 時間まで縮めました。

ただし、構造上どうしても拾えない層が残っていました。**「いまのデータ・ログ・コードを、人が読みに行かないと答えが出ない」** タイプの問い合わせです。

今回作った @ask-anything は、この層を拾うために設計した Slack bot です。実際のスレッドを 1 つだけ先に示します。これまでなら「まずエンジニアに聞こう」と dev-help 起票されていた、店舗運用担当からの操作ログ確認依頼です。

![](https://static.zenn.studio/user-upload/96a0bc41d8d1-20260604.png)

`@ask-anything 昨日の◯◯店の客数を教えて`

と投げると、bot が BigQuery を組み立てて結果を返します。エラー調査なら Cloud Logging を読み、コード調査ならダイニーの monorepo を grep して根本原因の仮説まで返します。実装は [Anthropic Claude Managed Agents](https://docs.claude.com/en/docs/build-with-claude/managed-agents) が中心です。

本記事は **「何ができるようになり、開発組織にどんな効果が出たか」** を扱い、技術詳細は別記事（近日公開予定）に分けてあります。

## 1. ask-anything ができるようになったこと

ask-anything が拾うのは、過去事例の検索ではなく **「いまのシステムを read-only で調査するタスク」** です。具体的には次の 3 種類に分けられます。

### 1.1 データ調査

例: 「◯◯店の昨日の客数を教えてほしい」「直近 7 日のリピート率は？」「ある店舗の shopId を教えて」

これまで → エンジニアが BigQuery を開き、テーブル定義を確認し、SQL を書き、実行するまでに、1 件 10〜15 分がかかっていました。

導入後 → スレッドで質問を投げると、bot が SQL を組み立て、dry-run でコストをチェックし、本実行し、結果を Slack に整形して返します。1 件 1〜2 分で完結できるようになりました。

### 1.2 ログ・履歴の調査

例: 「◯◯店のレジ開閉記録を CSV でほしい」「店舗から『△△の操作ができない』と問い合わせが来た、何が起きた？」「決済が時々失敗するという報告が入った、原因は？」

これまで → 店舗運用 / カスタマーサクセス担当からエンジニアに依頼が回り、エンジニアが Cloud Logging を開いて filter を組む、または BigQuery で操作ログを SQL で抽出して CSV にする作業が必要で、1 件 15〜30 分 + 待ち時間がかかっていました。

導入後 → bot が Cloud Logging / BigQuery を自分で叩き、時系列で読み、必要であれば CSV にして Slack に upload してくれるため、1 件 1〜3 分で完結できるようになりました。

### 1.3 仕様・バグの確認

例: 「この機能、今の仕様はどうなってる？」「店舗から『◯◯すると△△が起きる』と言われたが、これはバグ？それとも仕様通り？」「このボタンを押したときの挙動を教えて」

これまで → PdM / CS / 店舗運用担当からエンジニアに質問が回り、エンジニアが IDE で関連コードを grep し、依存関係を辿って仕様と実装を照合する。回答までに数十分〜数時間（エンジニア側の手が空くまでの待ち時間込み）がかかっていました。

導入後 → bot が Anthropic 側の作業環境にダイニーの monorepo を read-only で配置し、内部から rg で grep する。スレッドに関連ファイル・該当処理の要約 +「仕様通り / バグの可能性あり」の判断材料が返ってくる。

いずれも「過去事例の検索」ではなく、**ツールを複数回叩きながら調査をやり切るタイプの仕事** です。RAG ベースの bot がカバーできない、人手の代行が長く残っていた領域でした。

## 2. Claude Managed Agents の概要

### 2.1 なぜ自前オーケストレーションを捨てたか

前回の RAG bot は Mastra（TypeScript の AI orchestration framework）で組んでいました。Anthropic SDK を直接叩いて、「LLM の出力 → ツール呼び出し → 実行結果を LLM に投げ返す」というループを自前で 100 行ほど書く構成です。

ただし、ask-anything で必要なツールの種類と数は、これまでの比ではありません。

* BigQuery（クエリ実行・dry-run・CSV エクスポート）
* Cloud Logging（filter 組み立て・時系列読取）
* ダイニーの monorepo（session ごとに clone して grep）
* Notion（議事録・運用ドキュメント・dev-help 過去事例 DB）
* GitHub / Sentry / Slack / channel-talk（外部 SaaS のデータ参照）

これらすべてに対して「自前でアダプタを書く」「自前で credential を rotate する」「自前で retry / ストリーム切断ハンドリングを書く」という方針もありえます。ただ、そうすると本来 prompt 設計に充てたい時間が、定型的な「つなぎ」のコードに吸い取られていきます。

### 2.2 Claude Managed Agents とは

[Claude Managed Agents](https://docs.claude.com/en/docs/build-with-claude/managed-agents) は、Anthropic が提供する Claude API の上位機能です。

ざっくり言うと、**「ツールをいくつか登録した Claude」を Anthropic 側でホストしてくれる仕組み** です。こちらは Slack 等のイベントを Anthropic に中継するだけで、agent が自律的にツールを叩いて回答を組み立ててくれます。

大事なポイントは 3 つあります。

| 機能 | 何が嬉しいか |
| --- | --- |
| Anthropic 側に sandbox（agent が自分でコード・コマンドを実行できる作業環境）が用意されている | 「自分でコードを書いて実行する」「ファイルを保存しておく」が agent 単独でできるので、自前で実行環境を用意する必要がない |
| MCP server の URL を登録するだけで、agent が外部 SaaS（GitHub / Sentry / Notion 等）を直接読める | 各 SaaS の credential 管理（取得・rotate・漏洩対策）を Anthropic 側に寄せられる |
| Skill（agent に持たせる手順書）を agent 本体とは別ファイルで管理できる | system prompt が太らず、運用知識を後から差し替えやすい（publish した瞬間に本番反映される運用も組める） |

### 2.3 自前で書くコードは 3 種類に減った

ask-anything を Claude Managed Agents で組み直した結果、ダイニー側で書き続けているコードは 3 種類に収束しました。

1. Slack からイベントを受ける薄い HTTP handler
2. Claude Managed Agents の session を作り、events を中継する relay
3. agent から呼ばれる custom tool の実装本体（BigQuery 実行、Cloud Logging 実行、CSV upload など）

「ダイニーならではの business logic」と呼べるのは 3 番目だけで、1 と 2 はほぼ dispatcher です。前回 Mastra で書いた orchestration コードのうち、**体感で 7 割ほどが不要になりました**。

実装の細部や落とし穴（GCP credential を sandbox に渡せない問題、MCP server URL の trailing slash 一つで credential が見つからなくなる罠など）は、別記事（近日公開予定）に書いています。

## 3. 実際どう変わったか（KPI で見る）

ask-anything は 2026 年 4 月末から本格稼働を開始しました。社内 KPI ダッシュボードで週次トレンドを観察しています。

### 3.1 ask-anything が回答するスレッド数

bot が回答したスレッド数の週次推移です。

| 週 | bot 参加スレッド数 |
| --- | --- |
| 4/27 週（本格稼働開始） | 24 |
| 5/4 週 | 46 |
| 5/11 週 | 96 |
| 5/18 週 | 109 |

導入直後の週 24 件から、4 週で約 4.5 倍まで伸びました。skill / prompt の試行錯誤を重ねながら、対応できるユースケースの裾野を広げてきた結果です。

### 3.2 dev-help チケット起票数

dev-help は「開発チームへの正式な問い合わせ」を管理する Notion DB です。ここに起票される件数（= 開発チームメンバーが見て対応すべき問い合わせ件数）の推移を見ると、変化が分かりやすいです。

| 期間 | dev-help 起票数 / 週 |
| --- | --- |
| 導入前 4 週（3/30〜4/20） | 36〜49 件（平均 約 45 件） |
| 5/4 週 | 20 件 |
| 5/11 週 | 35 件 |
| 5/18 週 | 24 件 |

ask-anything 本格稼働後は週 20〜30 件台に下がっています。導入前の週 40〜50 件と比べると、**ほぼ半減** という結果です。

質問の絶対数が減ったわけではなく（Slack の質問総数はむしろ増えています）、「開発チームに正式チケット化される前に bot が答えを返している」量が増えた、という意味合いです。

### 3.3 エスカレーション率

「ask-anything が回答したスレッドのうち、結局 dev-help チケット化された割合」をエスカレーション率として観察しています。bot の回答品質（人手不要で完結したかどうか）を測る指標です。

| 週 | エスカレーション率 |
| --- | --- |
| 4/27 週（導入直後） | 100%（ほぼ全件チケット化） |
| 5/4 週 | 約 45% |
| 5/11 週 | 約 35% |
| 5/18 週 | 22.0% |

導入直後はまだ bot の回答精度が低く、人がフォローして dev-help 起票することがほぼ毎回必要でした。skill の整備や custom tool の精度向上を進めた結果、5/18 週には **「ask-anything が回答したスレッドのうち約 8 割は追加のチケット化が不要」** な状態まで到達しています。

## 4. まとめと次の記事

ask-anything の運用 4 週で見えた成果を整理すると次の通りです。

* bot が拾うスレッド数: 0 → 週 109 件まで急速に立ち上がった
* dev-help チケット起票数: 週 40〜50 件 → 週 20〜30 件（ほぼ半減）
* エスカレーション率: 100% → 22%（bot 単独完結率の改善）

開発チームへの問い合わせが半減すれば、エンジニアが本来の実装業務に集中できる時間が増えます。Claude Managed Agents の具体的な実装パターンに興味がある方は、ぜひ続編もお待ちいただければと思います。
