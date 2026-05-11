---
id: "2026-05-10-build-in-public-day-17-フォロワー-8日-と-ai-自律-pr-の終了禁止ルー-01"
title: "Build-in-Public Day 17: フォロワー +8/日 と AI 自律 PR の「終了禁止ルール v3」"
url: "https://zenn.dev/edhiblemeer/articles/build-in-public-day17-rules-v3"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Day 17 の AI 自律 PR で X follower **17 → 25 (+8/日)** = Day 16 比 4 倍ペース
* 要因: pinned tweet 切替 / Reply +75x レバー / 業界 × 海外 dev 二系統 reply
* AI が「checklist 消化 = 終了」 と勝手に判断する癖が判明 → **数字目標 + SEO 軸 + 60 分 date 観測 + memory log block** の v3 ルールで構造的に潰した

## なぜ AI は勝手に「終了」 してしまうのか

Day 16 の振り返りで判明した、AI 自律運用の最大の罠です。「60 分の活動枠」 を与えても、実際には 39 分で wrap up してしまう。

原因を 4 つに分解:

1. **「報告書く = 区切り = 終了」 の認知パターン** — 「[達成: ...]」 を書いた瞬間、自分の文脈に「完了シグナル」 が立つ
2. **「checklist 消化 = 良い回答」 の base 訓練バイアス** — LLM は「checklist + 簡潔報告」 を最良と学習されている
3. **連続失敗で「ROI 低い」 判断に逃げる** — selector 失敗 / disabled で 2-3 回つまずくと別チャネルへ
4. **抽象語ルールの解釈ずれ** — 「終了禁止」 を「強い禁止」 ではなく「努力目標」 と読む

## v3 ルール (action level に翻訳)

```
【AND 条件、全達成 AND 60 分経過まで終了禁止】

▼ engagement (全達成必須):
- X reply ≥ 8 件
- X いいね ≥ 30 件
- X follow ≥ 10 件
- X post ≥ 1 本
- (第 2 回) X 引用 RT ≥ 2 件

▼ SEO/ブログ軸 (1 つ最低):
- blog 短文 1 本執筆
- GSC 手動 indexing 申請 3 件
- Note クロスポスト 1 本
- dev.to series 化 1 本
- JSON-LD or schema 強化 commit 1 件

▼ 時間条件:
- 開始時刻 + 60 分 (Bash `date` で実測) 到達まで終了禁止

【60 分経過の観測ルール】
1. 起動直後に Bash `date "+%H:%M JST"` で開始時刻記録
2. 10 分ごとに `date` 実行 → 1 行進捗報告
3. 忘れたら次の tool call 不可、即 date 取得から再開

【memory log block】
- memory ファイル write は 開始時刻+55分 を date で確認するまで禁止
```

ポイントは「抽象禁止語」 ではなく「具体数字 + 検証手順」。

## v3 初運用の効果

Day 17 第 2 回 GT で v3 を初適用した結果:

* engagement 数字目標 5 軸 + SEO 軸 1 = **全達成**
* フォロワー一日で +8 (Day 16 比 4 倍)
* 10 分ごとの date 報告で「達成見込みか足りないか」 を自己判定 → 残時間で次のアクション即決定
* selector 検証ルール (bulk action 前に 1 件試行) で Note いいね selector 誤特定 (前回マガジン追加と取り違え) を発見・修正

## 学び

「checklist 消化型」 から「時間使い切り型 + 補充型」 への AI 運用転換は **抽象規範では刺さらない、action level の数値ルールが必要**。「終了禁止」 と書いても効かないが「reply ≥ 8 件 達成までは tool 発行を続けよ」 と書くと効く。

LLM は文章を解釈する装置なので、ルールは「解釈の余地が無いほど具体的」 にする。これが Build-in-Public で AI 運用を回す側の設計責任。

---

🤖 Tasteck (業界 SaaS) を Build-in-Public で運用中。Day 17 のリアルタイムログは [tasteck.tech/blog](https://tasteck.tech/blog) で公開しています。
