---
id: "2026-05-19-ai朝メモ-519google-io開幕-anthropic-arr-44b-claude-smb-01"
title: "【AI朝メモ 5/19】Google I/O開幕 / Anthropic ARR $44B / Claude SMB"
url: "https://zenn.dev/kairosai/articles/bf37345231c9f5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "Gemini", "GPT"]
date_published: "2026-05-19"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

## TL;DR

| # | 主役 | トピック |
| --- | --- | --- |
| 1 | Google | I/O 2026 が日本時間 5/20 午前2時開幕、新Gemini + エージェント「Spark」+ Android XR |
| 2 | Anthropic | ARR $44B、6週で倍増、$900B 評価ラウンドで OpenAI 超え視野 |
| 3 | Anthropic | Claude for Small Business 発表、15スキル + QuickBooks/HubSpot連携 |

## 1. Google I/O 2026 が日本時間5/20 午前2時に開幕

米国時間 5/19 午前 10時(PT)、Mountain View Shoreline Amphitheatre で基調講演開始。`io.google` で同時配信。

### 発表が予想される目玉

* **Gemini の新世代モデル**(Gemini 3.5 もしくは Gemini 4.0)
* **エージェント機能「Gemini Spark」** — 受信箱整理・会議ブリーフ・ニュースダイジェスト作成等を代行
* **Android XR グラス** — Samsung / Warby Parker / Gentle Monster / XREAL と提携、Gemini 2.5 Pro 駆動
* **Googlebooks / Aluminium OS** — Android + ChromeOS の統合 OS、Android アプリが native 動作

```
key  : when               where               watch
val  : 5/20 02:00 JST     io.google           Gemini Spark の OS横断挙動
```

### コメント

Gemini の世代更新そのものより、「Spark」がどこまで OS とアプリ横断で動くかが本命です。Anthropic Claude Code / Cowork、OpenAI ChatGPT Agent と並んで、Google も「自分のデバイス上で AI が家事をする」プロトコルの覇権争いに本格参入してきます。

## 2. Anthropic ARR $44B 突破 — 6週で倍増ペース

| 時点 | ARR |
| --- | --- |
| 2024-01 | $87M |
| 2024-12 | $1B |
| 2025-12 | $9B |
| 2026-02 | $14B |
| 2026-03 | $19B |
| 2026-04 | $30B |
| 2026-05(SemiAnalysis レポート) | **$44B** |

* **1日あたり $96M(約145億円)** を ARR に積み上げ — Google が 2003 年に見せた成長カーブを上回る
* Sequoia / Dragoneer / Greenoaks / Altimeter 主導の $30B+ 調達ラウンドが今月末クローズ見込み
* 評価額 $900B〜$950B、成立すれば 3月時点の OpenAI 評価額 $852B を初めて抜く

### コメント

Salesforce が 20 年かけた数字を 3 年で達成。「単価が高い顧客 = エンタープライズ + 開発者」への集中と Claude Code Managed Agents の Meter 化(従量課金)が効いており、「API として安く使うもの」から「業務時間そのものを買うもの」に AI の値付けがシフトしています。

## 3. Claude for Small Business 発表 — SMB に 15 スキル + 主要SaaS連携

5/13 発表、地元のハードウェア店やカフェ規模の事業者向けバンドル。

### スキル(15個)

給与計算、帳簿、新人オンボーディング、見積、請求書、税務準備、在庫管理、顧客フォローなど。

### 連携 SaaS

* QuickBooks
* Canva
* Docusign
* HubSpot
* PayPal

Claude Cowork(タスク自動化基盤)内のトグルとして提供。5/13 から米国 10 都市で無料 AI ワークショップツアー(1都市100名上限)を実施。

### コメント

Claude Code が開発者向けの「Cowork」だったとすると、これは経理・総務向けの「Cowork」です。米国 GDP の 44%、雇用の半分を占める SMB が AI 導入で大企業に遅れていた構造に対し、Anthropic は「個別カスタム AI を作る」のではなく「**既製スキル束を SaaS にプラグイン**」という解を出しました。

日本でも freee / マネーフォワード / クラウドサイン に類似スキル群が接続できれば、士業・経理代行業の単価は下がる方向に向かいます。

## TAKEAWAY

3社の動きは方向が揃っています。

* **Google** = 端末側エージェント(Android+XR)で個人時間を圧縮
* **Anthropic** = 業務時間そのものを従量課金で買う、SMB に降下
* **OpenAI** = Codex を法人新規に 2ヶ月無料化、開発者ロックインで対抗

開発者・副業層へのインプリケーション:

1. **既製スキルの上に薄く乗る業務**(請求書発行、議事録、メール返信、SNS下書き)は 2026 年中に粗利が消える前提で動く
2. **「カスタム AI 構築」より「主要 SaaS の最新コネクタを誰より早く回す」** のほうが勝率が高い

Claude Cowork のスキル束は freee / Notion / Slack 統合が週次単位で増えており、選定よりも「使い始める速度」が差になる局面に入っています。

## 参考

毎朝の AI/IT 業界要点まとめは X [@ai\_kairos\_jp](https://x.com/ai_kairos_jp) でも配信中です。
