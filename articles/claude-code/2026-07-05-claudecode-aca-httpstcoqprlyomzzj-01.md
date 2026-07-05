---
id: "2026-07-05-claudecode-aca-httpstcoqprlyomzzj-01"
title: "@ClaudeCode_aca: https://t.co/QPrlYomZzj"
url: "https://x.com/ClaudeCode_aca/status/2073698812535967776"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "x"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/QPrlYomZzj


--- Article ---
Claude Code アカデミアです。

AIエージェント開発に2,000時間以上を費やしたガチ勢のみで運営しています。

![](https://pbs.twimg.com/media/HMdAUH_a8AAnKAl.jpg)

**Claude Codeを極めたい方は、フォロー (**[@ClaudeCode_aca](https://x.com/@ClaudeCode_aca) **)しておいてください。**

**無料公式LINEは[こち**ら](https://utage-system.com/line/open/wcoIZQB0rwv3?mtid=1U5McDifKcjO)

では本題です。

**Fable 5には「裏仕様」が8つあります。** 公式ドキュメントにしか書いてない。ほとんどの人は知らないまま使っています。

たとえば——

- **「思考過程を見せて」と書くだけで、回答がOpusにすり替わる**
- **Effort設定でOpusの最高設定を超える性能がmediumで出る**
- **API課金を90%カットするプロンプトキャッシュがある**
結論から言います。**Fable 5は「知ってる人」と「知らない人」で別のAIになります**。

僕らが使い込んだ結論です。この8つを知ってから活用レベルが次元ごと変わった。今回はその全部を解説します。

> **👉 Claude Codeを極めたい方は、**[@ClaudeCode_aca](https://x.com/@ClaudeCode_aca) **をフォロー！

👉 無料公式LINEは[こち**ら](https://utage-system.com/line/open/wcoIZQB0rwv3?mtid=1U5McDifKcjO)

# 裏仕様① Fable 5を使ってるつもりで「Opusの回答を読んでいる」

![](https://pbs.twimg.com/media/HMdA7UkbcAAs60V.jpg)

これ、知らない人マジで多い。Fable 5には**裏で動いてるフォールバック機構**があります。

## 4つの安全分類器がリアルタイムで監視している

Fable 5には**4つの安全分類器**が搭載されています。全リクエストをリアルタイムで監視しています。

分類器が「リスクあり」と判定した瞬間——**Opus 4.8が自動で回答を引き継ぎます**。通知はありません。あなたはFable 5を使ってるつもりで、Opusの回答を読んでいるんですよ。

4つの分類器はこれです。

- **サイバーセキュリティ**: 攻撃手法やマルウェア関連の指示
- **バイオ・化学**: 危険物質や生物兵器に関連する内容
- **競合AI開発**: Fable 5の能力を別モデルにコピーする試み
- **推論抽出**: 内部の思考過程を出力させる指示
**95%以上のリクエストでは発生しません。** でも残りの数%で、あなたは気づかないままOpusの回答を受け取っています。

## 最もハマりやすい罠:「思考過程を見せて」

4つの中で**一番厄介なのが「推論抽出」**です。Anthropic公式がこう明記しています。

> **「内部の推論をテキストとして出力させる指示は、Opus 4.8へのフォールバックが増加する」**

つまりこういうプロンプトが全部アウトなんですよ——

- ❌「ステップバイステップで考えて」
- ❌「chain of thoughtを出力して」
- ❌「思考過程を書き出して」
**旧モデル用プロンプトにこの一文が残ってるだけでアウトです。** Opusの回答を読むことになります。僕らも全削除しました。

## 回避するための正解

僕らが実際にやっている対策です。

- ✅「結論の根拠を説明して」→ 推論抽出に引っかかりません
- ✅ APIなら thinking.display: "summarized" を使う
- ✅ 既存プロンプトから「思考」「考えて」系の指示を全部消す
**今使ってるプロンプトで「考えて」「思考」を検索してみてください。** これだけでFable 5が本来の性能を発揮します。

> **👉 Claude Codeを極めたい方は、**[@ClaudeCode_aca](https://x.com/@ClaudeCode_aca) **をフォロー

👉 無料公式LINEは[こち**ら](https://utage-system.com/line/open/wcoIZQB0rwv3?mtid=1U5McDifKcjO)
