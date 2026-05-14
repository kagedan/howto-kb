---
id: "2026-05-14-claude-agent-sdk-の課金が-615-に変わる個人開発者向けに-as-isto-be-01"
title: "Claude Agent SDK の課金が 6/15 に変わる！個人開発者向けに As-Is/To-Be を整理してみた"
url: "https://qiita.com/sakamoto66/items/abe1f1106104a9bd1b34"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "Python", "qiita"]
date_published: "2026-05-14"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

Claude Pro / Max を使って個人開発してる人、ちょっと待って。

2026年6月15日から **Claude Agent SDK と `claude -p`(headless mode)の課金ルールが変わります**。
「え、何がどう変わるの？自分には関係ある？」ってなったので調べてまとめました。

公式ドキュメント: [Use the Claude Agent SDK with your Claude plan](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)

---

## 一言でいうと

> **6/15 から、Agent SDK / `claude -p` / GitHub Actions の利用がサブスクの枠から切り離されて、別建ての「月次クレジット(USD)」に移る。**

対話でふつうに Claude Code を使っている分には何も変わりません。
変わるのは「自動化・非対話系」の呼び出しだけです。

---

## ユースケースごとの As-Is / To-Be

| ユースケース | 〜6/14 | 6/15〜 | 課金モデル |
|---|---|---|---|
| ブラウザ / アプリで Claude チャット | サブスク枠 | **変わらず** | 定額(プラン内) |
| Claude Code(ターミナル / IDE・対話) | サブスク枠 | **変わらず** | 定額(プラン内) |
| `claude -p`(headless・非対話) | サブスク枠 | **専用月次クレジットへ移動** | 定額(クレジット内)+ 超過は従量 |
| Claude Agent SDK(Python / TS) | サブスク枠 | **専用月次クレジットへ移動** | 定額(クレジット内)+ 超過は従量 |
| GitHub Actions 連携 | サブスク枠 | **専用月次クレジットへ移動** | 定額(クレジット内)+ 超過は従量 |
| サブスク認証で連携する 3rd party ツール | サブスク枠 | **専用月次クレジットへ移動** | 定額(クレジット内)+ 超過は従量 |
| API キー直呼び出し | API 従量課金 | **変わらず** | 純粋な従量 |

### もらえるクレジット額(ユーザーあたり / 月・繰り越し不可)

| プラン | 月次クレジット |
|---|---|
| Pro | $20 |
| Max 5x | $100 |
| Max 20x | $200 |
| Team Standard seat | $20 |
| Team Premium seat | $100 |

:::note info
クレジットは **ユーザーごとの個別割り当て**。チーム内でプールしたり、月をまたいで繰り越したりはできません。
:::

---

## 良くなったこと

### 1. 対話用と自動化用の枠が分離される
今まで CI や夜間バッチが走るたびに「あ、また枠食われてる…」ってなってた人、これで解消されます。  
人間が日中に Claude Code を使う枠は守られます。

### 2. 暴走時の安全弁ができる
Extra usage(超過従量課金)を **OFF** にしておけば、自動化が暴走しても請求が爆発しません。  
クレジット枯渇で止まるだけなので、予算管理がしやすくなります。

### 3. GitHub Actions が定額の範囲に収まる
$20〜$200/月の予算で CI/CD 連携が運用できるようになります。

---

## 悪くなったこと / 注意点

### 1. 天井が明確になる
「サブスク枠の中でなんとかなってた」ものが、$20/$100/$200 という明確な上限に変わります。  
重い SDK ワークロードを回している人は実質的に枠が減る可能性があります。

### 2. 繰り越し不可・プール不可
使わなかった分は消えます。チームメンバー間で融通もできません。

### 3. 自分でメールから opt-in する必要がある
自動でもらえるわけじゃなく、Anthropic からのメールで claim 操作が必要です。  
**見逃すとクレジットがもらえないので注意！**

### 4. クレジットが USD 建て・トークン換算が不透明
実際に何回 SDK を呼べるかはモデル選択(Opus / Sonnet / Haiku)とトークン量次第。  
[API 価格表](https://www.anthropic.com/pricing)で事前に見積もっておくのが吉です。

### 5. Extra usage を OFF にしていると本番が止まる
「予算厳守なので OFF にしよう」→「本番の自動化が突然止まった」になりかねないので、設計が必要です。

---

## `/loop` などのスキルは定額？従量？

> 「slash command のスキルって定額ですか？従量ですか？」

という疑問が出たので補足します。  
結論：**「定額か従量か」はスキル自体ではなく、実行モードで決まります。**

| 実行モード | 〜6/14 | 6/15〜 |
|---|---|---|
| 対話 Claude Code(ターミナル / IDE) | サブスク枠(定額) | **サブスク枠(定額)** ← 変わらず |
| `claude -p`(headless) | サブスク枠(定額) | **月次クレジット + 枯渇後は従量** |
| Agent SDK / autopilot 経由 | サブスク枠(定額) | **月次クレジット + 枯渇後は従量** |

`/loop` を対話 Claude Code のターミナルで回してるなら 6/15 以降も定額のまま。  
`claude -p` や autopilot 経由で走らせているなら、月次クレジット枠での消化になります。

---

## 6/15 までにやること

- [ ] Anthropic からの案内メールを受け取れる状態にしておく
- [ ] メールが届いたら **one-time opt-in** でクレジットを claim する(これ重要)
- [ ] 現在使っている Agent SDK / `claude -p` / GitHub Actions を棚卸しする
- [ ] 月間使用量を USD で概算して、クレジット枠($20/$100/$200)に収まるか確認
- [ ] **Extra usage を ON にするか OFF にするかを決める**
  - 本番が止まると困る → ON にして請求監視も設定する
  - 実験用・予算厳守 → OFF でクレジット枯渇で止まる設計にする

---

## 6/15 以降にやること

- [ ] 月次クレジット消費の monitoring を入れる(残額 0 で止まるので)
- [ ] 自動化で使うモデルを見直す(Opus ばっかりだとすぐ消える。Haiku / Sonnet で賄えないか検討)
- [ ] 対話 Claude Code と `claude -p` を混在させないよう運用を分ける
- [ ] 月末に未使用クレジットが消えないよう、ワークロードを平準化する
- [ ] 6/15 以降の Usage ダッシュボードでクレジット消費 / 超過分を確認

---

## これだけやっとけば OK

> **6/15 までに「届いた案内メールから一回だけ opt-in」+「Extra usage の ON/OFF を決める」だけ。**  
> 残りは Anthropic 側で自動的に月次クレジット制に移行してくれます。

---

## 参考

- [Use the Claude Agent SDK with your Claude plan — Anthropic Help Center](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
- [Use Claude Code with your Pro or Max plan — Anthropic Help Center](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan)
