---
id: "2026-06-22-minicoohei-httpstcowir8p6fqih-01"
title: "@minicoohei: https://t.co/WiR8P6FqIh"
url: "https://x.com/minicoohei/status/2069062337877668022"
source: "x"
category: "claude-code"
tags: ["claude-code", "LLM", "x"]
date_published: "2026-06-22"
date_collected: "2026-06-24"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/WiR8P6FqIh


--- Article ---
> 「AI Readyなデータ基盤」を作るとき、議事録・Slack・メールのような非構造データをAIにどう探させるか。素朴には Databricksに索引化してGenieに聞かせるのが王道に見える。でも Claude Codeに元フォルダを直接探させる方が速くて正確かもしれない。

前回の投稿でとりあえずどうなんだろうって思ってやってみた。（基本的な事業の数値とかそういうものはDataBricksから呼ぶ前提で）

——自社データ約1万件で、実際に両方やって殴り合わせた。

連載第2回。前回（#1）はコストの話。今回は** 「索引をDatabricksに渡す」vs「Claude Codeに直接探させる」** の実測対決。

![](https://pbs.twimg.com/media/HLbGgGkbgAA4gCr.jpg)

## 背景：AIの「目・耳・手」

社内データをAIから使えるようにする、を分解すると：

- **目（Eyes）** = アナリティクス（売上・KPI・件数）。構造化データ。SQL の世界 → ここは文句なし **Databricks+Genie **
- **耳（Ears）** = 議事録・Slack・メール・チケット。非構造データ。**今回の主題**
- **手（Hands）** = ツールで実行する（メール送信・チケット更新）
耳をどう実装するか。選択肢は2つ：

**A. Databricks + Genie（索引を渡す）**全文書を documents テーブルに索引化し、Genieに自然言語で聞く（中身はキーワード検索＋LLM要約）

**B. Claude Code（フォルダ直読み）**Claude Code に元フォルダを grep させ、ヒットした文書を読んで理解させる

検証対象：自社の非構造データ **約9,980件** を Databricks の1テーブルに統一索引化したもの。（まー正直大した量じゃないけど個人で扱うデータ量っていう範囲で）

![](https://pbs.twimg.com/media/HLbHJD_a8AAIp3k.png)

## 結果：固有名詞・日付・金額で差がついた

**Q「認証まわり（Clerk）の対応期日は？」**

CopyA Databricks+Genie : [AIB-408] #sales Clerkの環境手配… を候補提示
                     → 関連チケットは出るが「期日」までは要追い読み
B Claude Code      : 「6月26日」← 該当議事録を読んで日付を特定

**Q「OCR処理のコストを抑える方針は？」**

A Databricks+Genie : OCRを含む案件を列挙(候補は出る)
B Claude Code      : 「12.5万件で約8万円」← コスト試算の記述を読み当てた

## 10問通した全体像

Claude Code側だけが、固有名詞・日付・金額をピンポイントで当てた。候補の会議を特定して、Notionのボードを当て、具体的な数値をすべて抽出できた。B2Bリストとか無関係の記事とか議事録の位置だけでなく、具体的な数値まで抽出できた。

## なぜ差がついたのか

Databricks+Genie が苦手だった理由

Genieの中身は **キーワード検索（SQL LIKE）＋ LLM要約** の2段。

これ自体は強力で、「定例で何が決まった？」のような **要約系**には答えられる。だが今回のような **固有名詞のピンポイント抽出** では弱点が出た：

1. **字面でしか引けない** — 「資金調達」は「増資」「ファイナンス」にヒットしない
1. **ノイズに弱い** — 受信トレイの宣伝メールやB2Bリストが候補に混ざり、本命が埋もれる
1. **要約が候補に引きずられる** — 検索で拾えた範囲しか要約できない。本命の文書が候補に入らなければ、LLMがどんなに賢くても答えは出ない
Claude Code が強かった理由

Claude Code は **grep でヒット → 該当文書を実際に読む → 文脈を理解して答える**。検索と理解が一体なので、「どの文書のどの行に答えがあるか」まで辿り着く。固有名詞・日付・金額に圧倒的に強い。

※ ちなみに「ベクトル検索（意味検索）」も一応試したが、Databricks標準の埋め込みが英語モデル（gte-large-en）で、日本語を入れると「認証Clerk」に「クラウドサイン」を返すレベルで惨敗した。多言語モデル＋チャンク
