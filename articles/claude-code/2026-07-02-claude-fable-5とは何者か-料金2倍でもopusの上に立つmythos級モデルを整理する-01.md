---
id: "2026-07-02-claude-fable-5とは何者か-料金2倍でもopusの上に立つmythos級モデルを整理する-01"
title: "Claude Fable 5とは何者か — 料金2倍でもOpusの上に立つ「Mythos級」モデルを整理する"
url: "https://zenn.dev/ojyo/articles/0209116ab6a3fd"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

2026年6月9日、AnthropicがClaude Fable 5を一般公開した（[PC Watch](https://pc.watch.impress.co.jp/docs/news/2121713.html)）。「Opusの上」に新設されたティアのモデルで、話題性のわりに情報が散らばっているので、公式ドキュメントと各種報道をもとに要点を整理する。

なお、この記事を書くにあたって使っているClaude Code自体もFable 5で動かしている。使用感も最後に少しだけ書く。

## 位置づけ:「Opusの後継」ではなく「Opusの上」

Claude Fable 5は、これまで最上位だったOpusのさらに上に新設された、Anthropicの**一般公開モデルとしては最上位**のティアだ。もともと「高性能すぎる」として招待制限定だったMythos級モデルの能力を、安全機構付きで一般公開したものとされる（[ギズモード・ジャパン / Yahoo!ニュース](https://news.yahoo.co.jp/articles/e0ce5fb9f0d3ee49dc1f1b26c7974e394295b4d2)）。

なお、招待制プログラム（Project Glasswing）参加組織向けには同等モデル「Claude Mythos 5」が提供されており、能力・価格・API仕様は同一とされている（[Anthropic公式ドキュメント](https://platform.claude.com/docs/en/about-claude/models/overview)）。

## 料金: Opus 4.8のちょうど2倍

| モデル | 入力/1M tok | 出力/1M tok | コンテキスト |
| --- | --- | --- | --- |
| Claude Fable 5 | $10 | $50 | 1M |
| Claude Opus 4.8 | $5 | $25 | 1M |
| Claude Sonnet 5 | $3 | $15 | 1M |

（出典: [Anthropic公式 Pricing](https://platform.claude.com/docs/en/pricing)）

コンテキストウィンドウは100万トークン（これが最大かつデフォルト）、最大出力は128Kトークン。

## 何がすごいのか（報道ベース）

## 開発者視点で重要なAPI仕様の変化

公式ドキュメント（[Introducing Claude Fable 5](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5)）から、既存コードを移行する人が知るべき点を抜粋する。

1. **思考(thinking)が常時オン。** `thinking`パラメータの明示的な設定は不要どころか、`{type: "disabled"}`や`budget_tokens`指定は400エラーになる。思考の深さは`output_config.effort`（low〜max）で制御する。
2. **生の思考過程は返ってこない。** `display: "summarized"`を指定すると要約された思考は読めるが、生のchain of thoughtは一切返らない設計。
3. **安全分類器によるrefusal。** サイバーセキュリティ・生物系などの高リスク領域でリクエストが拒否されることがある（HTTP 200で`stop_reason: "refusal"`）。APIではOpus 4.8への**サーバーサイド・フォールバック**をオプトインでき、拒否時に同一リクエスト内でOpus 4.8が応答を引き継ぐ。
4. **30日間のデータ保持が必須。** ゼロデータリテンション設定の組織では全リクエストが400になる。
5. **温度(temperature)等のサンプリングパラメータは廃止。** Opus 4.7以降と同じ。

## 使ってみた感想（Claude Code経由）

このセッション自体をFable 5で動かしてみて感じたのは、「1ターンが長い」こと。難しいタスクでは1リクエストが数分続くことも普通で、対話的というより「任せて待つ」使い方が合う。公式も、タスクの全体像を最初に伝えて長時間走らせる使い方を推奨している。

逆に、料金がOpus 4.8の2倍である以上、日常的な短いタスクにFable 5を使うのはコスパが悪い。実際、Claude Codeでもモデルを切り替えながら「普段はSonnet/Opus、重いタスクだけFable」という使い分けがしっくりくる。

## まとめ

* Fable 5は「Opusの次」ではなく「Opusの上」。料金も2倍
* 本命用途は長時間の自律エージェント。短いチャットに使うモデルではない
* API移行時はthinking常時オン・refusalフォールバック・データ保持要件の3点に注意

## 参考文献
