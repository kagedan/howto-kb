---
id: "2026-05-01-claude-max-で毎月-8833-分使っていたpromaxapi-の境目を実データで割り出した-01"
title: "Claude Max で毎月 $8,833 分使っていた。Pro/Max/API の境目を実データで割り出した"
url: "https://zenn.dev/kojihq/articles/42addb8f5acd4b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code を毎日使っていて、「自分は本当にこのプランで合ってるのか」が気になり始めました。

私は Claude Max（5x プラン、Pro の 5 倍利用枠）に入っています。定額なので「いくら使っても OK」のはずなのに、本当にプランに見合うほど使えているのか、Pro $20 に下げても良いのか、逆に Max 20x に上げるべきなのか、API 従量課金にした方が安いのか — その答えがどこにも出てきません。

Anthropic Console で見えるのは「今月の使用状況」と「サブスクのプラン」だけ。「もし API だったらいくらだったか」の答えはどこにも出ません。

でもローカルには答えがあります。Claude Code はセッションログを `~/.claude/projects/<project>/<session>.jsonl` に書き出していて、`usage`（input/output/cache\_read/cache\_create トークン数）と `model` が全イベントに付いている。これを集計すれば、API 換算コストは正確に出せます。

実際に集計してみたら、自分の使い方が想像と違っていて驚きました。本記事では、その観察結果と、Pro / Max 5x / Max 20x / API のどれを選ぶべきかの境目について書きます。

## Anthropic が見せてくれない 3 つの数字

公式ツール（Claude Code の `/usage`、Anthropic Console、Claude Pro/Max ダッシュボード）で見えるもの・見えないものを整理します。

| 知りたいこと | 公式で見える？ |
| --- | --- |
| 今月の合計トークン数 | ✓（Console） |
| サブスクの残量 / リセット日 | ✓（Pro/Max） |
| **API 換算でいくら相当か** | **✗** |
| **モデル別（Opus / Sonnet / Haiku）の内訳** | **✗** |
| **プロジェクト別 / セッション別** | **✗** |

特にサブスクユーザーには「API 換算でいくら相当か」がブラックボックスです。「自分は元を取っているのか」「プランを下げるべきか上げるべきか」を判断する材料がない。

ところが JSONL ログには `usage` と `model` が全イベントに付いているので、集計するだけで答えが出ます。

## 観察結果: ケース A（実データ、Max 5x 加入者）

直近 30 日のログを集計したスクリプトの出力です。これは実際に私が `koji-lens summary --since 30d` を打った結果です。

```
$ koji-lens summary --since 30d
TOTAL
  sessions:       338
  duration (sum): 274h 31m
  cost:           $8,833.42 (API-equivalent)
  tokens:         output=25.8M, cache_read=4.85B
  models:         sonnet×13,996, opus×13,403, haiku×2,437
  note: Cost is API-rate equivalent.
        Subscribers pay a flat fee regardless.
```

**$8,833.42**。

これが API 従量課金だった場合の月額です。私が払っているのは Max 5x（Pro の 5 倍利用枠、約 $100/月）。**つまり 88× の価値を受け取っている**計算になります。逆に言えば、もし Max 5x が無くて API で同じ使い方をしていたら、月末の請求が $8,800 で来ます。

> 念のための前置き: これは私が AI コーディングに専念している濃い使い方の結果です。直近 30 日で 274 時間 = 1 日平均 9 時間以上 Claude Code に触れている計算で、一般的な副業エンジニアの数倍は使っています。あなたの数字はもっと現実的なはずですが、「自分はいくらか」を測ってみる価値はあります（後述）。

ここで興味深い発見がありました: 私の使用量だと **Pro $20 では完全に枠超え**で、**Max 5x ($100) が論理的な選択**、それでも API 換算 88× で十分元が取れている、ということです。「もしかして Max 20x ($200) に上げた方が...」という不安も、Max 5x で十分という事実が数字で確認できました（Anthropic 側の利用枠制限に当たっていない前提）。

つまり Max 5x はサブスクとして極めて強力です。月 $100 で API $8,000+ 相当の使い方ができている人は、Anthropic に感謝するレベルです。

## 観察結果: ケース B（仮定の試算、API ユーザー）

次は別のパターンとして、API キーで Claude Code を使っているケースを試算してみます。**ここからは仮定の数字です**。

仮に「Opus 中心の使い方で、Sonnet にあまり切り替えていない」ユーザーがいたとします。

```
（仮定の試算例）
TOTAL
  period:   last 7 days
  cost:     $187.45
  cost by model:
    claude-opus-4-7    $173.21 (92%)
    claude-sonnet-4-6  $14.24  ( 8%)
  models: opus×238, sonnet×12
```

直近 1 週間で **$187**、月換算 **$750-800**。そして 92% が Opus。

Opus を使うべき難しいタスクは確かにありますが、9 割を超える比率は明らかに過剰です。簡単な編集や再生成は Sonnet で十分。`/model claude-sonnet-4-6` で切り替えるだけで、品質ほぼ同じで料金が大幅に下がります。

仮に「複雑な設計タスクは Opus、それ以外は Sonnet」のルールで運用したら、Opus 比率は 30-40% まで下がる可能性が高い。月 $480 → $250 くらいの試算です。

このユーザーの場合、月 $750-800 を払い続けるなら、**Max 20x（$200/月）に切り替えれば 4× 安くなる**判断もあります。

> 注: ケース B は仮定の試算です。実際の API ユーザーの数字は環境によって大きく変動します。

## 使い分けの境目

集計結果から、Pro / Max 5x / Max 20x / API のどれを選ぶべきかの判断基準が見えてきました。

| 月の API 換算（30 日） | 推奨プラン |
| --- | --- |
| $20 未満 | API 従量課金（Pro より安い） |
| $20-100 | **Pro $20** が圧倒的にコスパ良い |
| $100-500 | **Max 5x ≈ $100**（私のケース） |
| $500-2000 | **Max 20x ≈ $200** |
| $2000+ | API + 厳格なコスト管理（プラン上限超え） |

> 価格は 2026-05 時点（Anthropic 公式 [claude.com/pricing](https://claude.com/pricing) で最新確認推奨）。Max 5x / 20x の利用枠倍率は Pro 比。

副業 / 個人開発で Claude Code を毎日使っているなら、Pro か Max 5x のどちらかにほぼ収まります。私のように 88× の価値が出ている Max 5x ユーザーは AI 開発専念ケースで例外的ですが、それでも Max 5x が妥当 = Max 20x ($200) まで上げる必要はないという判断でした。**自分が表のどのレンジに入るかを数字で確認すること**が、本記事で言いたいことです。

ただし、**自分の API 換算がいくらか分からなければ判断のしようがありません**。測る方法は次のセクションで。

## 自分で測る方法

私が開発している [`@kojihq/lens`](https://www.npmjs.com/package/@kojihq/lens) という OSS の CLI ツールで測れます（β、MIT ライセンス）。

```
$ npm install -g @kojihq/lens@beta
$ koji-lens summary --since 30d
```

これだけで、上記ケース A と同じ形式の出力が手元で出ます。クラウド送信なし、サインアップなし、ローカルの JSONL を読むだけです。

GitHub: [etoryoki/koji-lens](https://github.com/etoryoki/koji-lens)  
LP: [lens.kojihq.com](https://lens.kojihq.com)

詳細なコマンド（`sessions` / `session <id>` / `serve` で Web ダッシュボード起動など）は GitHub README を参照してください。

## まとめ

* Claude Code の `~/.claude/projects/**/*.jsonl` には API 換算コストを正確に出すための情報が全て入っている
* Pro / Max ユーザーは「API 換算でいくら使っているか」を測ることで、**自分のプランが妥当か / 下げるべきか / 上げるべきか**を数字で判断できる
* API ユーザーは「モデル別内訳」を見ることで、Opus → Sonnet 移行で月のコストを大幅に下げられる
* 自分で測りたい人は `@kojihq/lens` をどうぞ（私が開発しています）

「使ってみたら自分の使い方が想像と違ってた」が、私の一番の発見でした。あなたの API 換算が何ドルか、ぜひ一度測ってみてください。

---

**この記事について**

* ケース A は私自身の Claude Code 使用ログから取得した実データ（直近 30 日、koji-lens で集計、Max 5x プラン加入者）
* ケース B は API ユーザーの一例として仮定の試算（実際の数字は環境によって変動）
* API 換算コストは Anthropic 公式の API 価格表（2026-05 時点）に基づく
* Anthropic Pro / Max のサブスク価格は claude.com/pricing を参照（時期により変動）
* koji-lens は β 版、issue / PR 歓迎: <https://github.com/etoryoki/koji-lens>

---
