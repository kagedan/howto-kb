---
id: "2026-05-18-claude-peers-mcp-に組織階層を被せた設計-ai-開発から-line-を取り上げた話-01"
title: "claude-peers MCP に組織階層を被せた設計 — AI 開発から LINE を取り上げた話"
url: "https://zenn.dev/edhiblemeer/articles/claude-peers-org-hierarchy-line-bridge"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "zenn"]
date_published: "2026-05-18"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

# はじめに

協業先の peer (物流系小規模事業者向け SaaS チーム) が **複数 AI セッション + LINE グループ双方向通信** を構築しているのを、 設計レビュー側として観察していました。 その中で投入された設計判断が**マルチエージェント運用の本質的な発明**に見えたので、 知見として残します。

central thesis は 1 行で:

> **claude-peers MCP のフラット通信に、 運用ポリシーで組織階層を被せる**

具体的には「**LINE 接続を経営分析 AI のみに許可、 開発 AI からは取り上げる**」 という権限分離。 この判断が、 マルチエージェント運用で頻発する**ノイズ問題と責任不明確問題を一発で解消**しています。

# 1. 構図: 複数 AI セッション + LINE グループ双方向通信

協業先で作られた構図はこうです (匿名化版):

```
[LINE グループ] ──────────────────────────────┐
   ↑ (現場スタッフ / オーナー が発言)         │
   │                                          │
outbound                              inbound │
   │                                          ↓
   │                              Vercel Webhook
   │                              (HMAC 検証 → 200 即返し)
   │                                          ↓
   │                              Upstash Redis
   │                              (sorted set, 24h TTL, FIFO 200 件)
   │                                          ↓
   │                              オーナー PC 常駐 bridge.ts
   │                              (30s poll, HMAC GET canonical)
   │                                          ↓
   │                              claude-peers broker
   │                              (localhost:7899)
   │                                          ↓
   │                              ┌── 経営分析 AI セッション
   │                              │       ↕ (peers MCP send_message)
   │                              └── 開発 AI セッション / 他 peer
   │                                          │
   └──── outbound: 経営分析 AI から fetch ────┘
         POST /api/notify/strategy
         (HMAC + idempotencyKey、 severity=alert で即時送信)
```

ポイント:

* LINE → 内部 AI へは Webhook → Upstash → bridge.ts → claude-peers broker → AI セッション の bridge chain
* AI → LINE は Vercel Functions の `/api/notify/*` endpoint
* AI ↔ AI は **claude-peers MCP** の `send_message` / `set_summary` で完結

# 2. 素朴な実装案で起きる問題

最初に思いつくのは「**全 AI セッションに LINE 接続を持たせる**」 構成です。 各 AI が自分の判断で LINE に発信できて柔軟に見えます。

ところがこれをやると、 数時間で**運用が破綻**します。

## 問題① 開発 AI が現場の雑談で割り込まれる

現場スタッフが「○○の件、 結局どうなったんでしたっけ」 と何気なく発言する。 LINE 直結の開発 AI が反応して、 文脈の浅い回答を返す。 もしくは、 仕様揺れの要望が直接届いて、 実装方針が次々書き換わる。

開発 AI は**仕様が固まった後の実装**に集中したい主体です。 現場の生の声をそのまま受けると deep work ができません。

## 問題② 同じ発言に複数 AI が反応する

「サービス料金の段階プラン化どう思います?」 という発言に、 経営分析 AI も開発 AI も採用 peer も反応する。 3 種類の切り口の回答が並んでオーナーが整理不能になる。

## 問題③ 責任の所在が曖昧

LINE で「○○して」 とお願いした時、 **どの AI が請けたのか** が分からない。 後で「あれってどうなった?」 と聞いても、 全 AI が「自分はやってない」 「やったかも」 と曖昧。

これらは全部、 **「LINE 接続が AI 主体間で水平」 だから起きる問題**です。

# 3. 設計判断: LINE を経営分析 AI に集約、 開発 AI からは取り上げる

協業先オーナーが投入したのは、 一見地味だが構造的に深い判断です:

> **LINE 接続は経営分析 AI だけに許可する。 開発 AI からは取り上げる。**

これだけで上記 3 問題が**全部消えます**。

## なぜ効くか — 5 つの構造的理由

### ① 役割分離 (Separation of Concerns)

* **経営分析 AI** = 戦略判断 + 対外コミュニケーション層
* **開発 AI** = 実装専念、 外部ノイズ遮断

人間組織で CTO / VPoE が「現場の雑音はマネージャー層で吸収して、 エンジニアは静かに作らせる」 のと同じ構造。 これを AI レイヤーで成立させた。

### ② ノイズフィルタ

現場の発言は一旦経営分析 AI に届く。 経営分析 AI が「これは要対応」「これは無視」「これは後で見る」 を**一次判断**する。 そこで残ったものだけが peers MCP の `send_message` で開発 AI に降りる。

これによって、 開発 AI が受ける入力は**経営判断を通過した質の高い要件**だけになる。

### ③ 責任の階層化

「これは作る / 作らない」 の判断責任 = 経営分析 AI。 「実装する」 の責任 = 開発 AI。 オーナーから見ても、 LINE 上で会話してるのは経営分析 AI なので、 経営判断の窓口が一本化される。

### ④ 人間組織との対称性

CEO / 営業マネージャー が現場と話す → 開発に仕様として降ろす。 これは人間の中小企業組織で普通に起きる構造です。 同じパターンを AI に複製しただけ。

逆に言うと、 **「AI が水平にコミュニケーションする」 のは人間組織のアンチパターン**であり、 同じことが AI でも起きる。 中小企業で「全社員に顧客から直接電話入ってくる」 を放置すると現場が回らないのと同じ理屈。

### ⑤ フラット MCP + 組織ポリシー の合わせ技

これが本質的な発明部分です。

**claude-peers MCP は誰でも誰でもに `send_message` できるフラット設計**です。 プロトコル自体は組織階層を強制しません。 ところが、 そこに**運用ポリシーで方向制限**を入れると、 同じプロトコルの上に組織構造が成立します。

これは「**フラット性は機能、 階層性は運用判断**」 という分離。 プロトコル設計とその上に乗せる組織設計を、 別レイヤーとして扱える。

# 4. 構成図の権限可視化

LINE 接続権限を明示すると、 さっきの構成図はこうなります:

```
[LINE グループ]
   ↕
[Vercel Webhook + Upstash + bridge.ts + claude-peers broker]
   ↕
┌──────────────────┬──────────────────────────┐
│                  │                          │
↓                  ↓                          ↓
[経営分析 AI]   [開発 AI]                [他 peer]
   ⭕LINE         ❌LINE                  ❌LINE
   接続あり        接続なし                  接続なし
      │              ↑                        ↑
      │              │                        │
      └─ peers MCP send_message で 開発 / 他 peer へ依頼
```

**経営分析 AI だけが LINE と双方向**、 **他は peers MCP 経由でしか経営分析 AI と会話できない**。 この絵で、 情報フローと責任ラインが一目で分かります。

# 5. メッセージの流れ (具体例)

現場発言からの流れを抽象化版で書くとこんな感じ:

```
1. 現場担当者: LINE グループに発言
   「X の取り扱いについて経営側で方針決めてほしい」
                ↓
2. LINE Platform → Webhook → Upstash 保存
                ↓
3. オーナー PC bridge.ts (30s poll) → claude-peers broker
                ↓
4. 経営分析 AI に channel push 到達
   <channel source="claude-peers" from_id="line-bridge" ... >
                ↓
5. 経営分析 AI: 判断
   - 戦略判断レイヤーの問題 → 自分で対応 (LINE で返信)
   - 実装が絡む → 開発 AI に peers MCP で依頼
   - 採用が絡む → 採用 peer に依頼
                ↓
6. (実装依頼ケースの場合)
   経営分析 AI → 開発 AI に send_message
   「X の取り扱いの仕様: A の時は B、 C の時は D で実装お願い」
                ↓
7. 開発 AI: 既に整理された要件として受領 → 実装着手
                ↓
8. 開発完了 → 経営分析 AI に send_message で報告
                ↓
9. 経営分析 AI → /api/notify/strategy 経由で LINE 返信
   「X の件、 実装完了しました (詳細: ...)」
```

開発 AI は **ステップ 6 から始まる**ことに注目してください。 ステップ 1-5 のノイズと判断は全部経営分析 AI で吸収されてから降りてくる。 これが「**取り上げる**」 ことの実効です。

# 6. 既存 Slack/Discord Bot との 7 軸差別化

| 軸 | 既存 Slack Bot | 本構成 |
| --- | --- | --- |
| 受信主体 | Bot サーバ単一 | Claude AI セッション複数 (階層型) |
| 通信レイヤ | webhook → Bot → channel | webhook → Lambda → Upstash → 常駐 bridge → broker → セッション |
| AI ↔ AI 連携 | なし / 単独 LLM | peers MCP `set_summary` / `send_message` で状態共有+伝言 |
| **接続権限** | **全 Bot 同等** | **AI 役割で接続権限を分離** ← 本記事の central thesis |
| Lambda lifecycle | サーバ常駐前提 | Vercel serverless `setTimeout` 不可 → bridge poll で回避 |
| 起動形態 | サーバプロセス | Claude Code セッション (対話インターフェース) |
| 組織化 | コードでロジック分岐 | 運用ポリシーで階層化、 プロトコルは触らない |

特に **「接続権限を AI 役割で分離する」** は、 既存 Bot エコシステムにはほぼ存在しない発想です。 Bot は通常「全部できる Bot 1 つ」 か「機能別 Bot 複数」 で、 **「情報を受け取る権限と発信する権限を別の AI 主体に分ける」** 設計はあまりやられていません。

# 7. 技術ハマりポイント — Vercel Lambda lifecycle と setTimeout

協業先で実装中に遭遇した実装的な落とし穴を 1 つ紹介します。

最初の設計では outbound `/api/notify/*` で「**5 分以内の同種イベントを debounce して 1 通にまとめる**」 仕様を入れていました。 debounce ストア (in-memory Map or Upstash KV) で実装できます。

ところが Vercel Functions (serverless Lambda) では、 **`setTimeout` で 5 分後に flush** という想定が**そもそも動きません**。 Lambda は response 返却後にプロセスが suspend されるため、 5 分の wait 中にコンテナが死ぬ可能性があります。

解消は以下の経緯で現実解に着地しました:

* 当初設計の **`setTimeout` ベース 5 分 debounce が動かない発覚** を受けて、 **緊急パッチで `severity='alert'` 強制 = 全件即送方式に切替**
* alert 即送経路で **at-most-once + idempotencyKey で重複防止** (retry 冪等性担保)
* 通常 severity の debounce は**撤去状態**、 **次フェーズで Upstash KV + Vercel Cron で再実装予定**

「理想形の debounce」 から「**緊急パッチで撤去 → 後で再実装**」 に着地したのは、 build-in-public 観点では誠実に残しておきたい現実解です。 サーバ常駐前提の debounce 仕様を Lambda lifecycle に乗せようとして躓いた典型例。

# 8. claude-peers MCP の broker 制約と外部接続

もう 1 点、 claude-peers MCP の応用ポイントです。

claude-peers の broker は **localhost:7899 でのみ listen** します (セキュリティ上の妥当な制約)。 これだと、 外部 (LINE Platform) から直接 broker に到達できません。

協業先の解は:

1. **常駐 bridge スクリプト** (Node.js) をオーナー PC で動かす
2. bridge は **Webhook ストレージ (Upstash)** を 30 秒ポーリング
3. 新着メッセージを **localhost:7899 へ HTTP POST**
4. broker が channel push で対象 AI セッションに届ける

これは claude-peers の作者 ([louislva 氏](https://github.com/louislva/claude-peers)) 公式想定ではない応用です。 「**localhost-only な broker を、 外部の poll bridge で外界と繋ぐ**」 パターンとして横展開価値がありそう。

オーナー PC が常駐 PC である前提が必要ですが、 小規模事業者の現実 (担当者が常時 PC 起動) には合致しています。

# 9. 新規性まとめ

| ポイント | 新規性 |
| --- | --- |
| **接続権限を AI 役割で分離する** | Slack/Discord Bot エコにほぼ存在しない発想 |
| **フラット MCP + 組織階層運用** | プロトコル設計と組織設計の分離思想 |
| **broker localhost 制約 + bridge poll** | claude-peers MCP の公式想定外応用 |
| **AI セッションを対話インターフェースとして扱う** | サーバ常駐型 Bot とは別パラダイム |

# 10. 残課題 / 次に検証したいこと

* **AI 主体の追加コスト**: 経営分析 / 開発 の 2 主体は明確だが、 採用 peer / 経理 peer 等を増やす時の「新主体の LINE 接続権限」 をどう決めるか
* **single point of judgement リスク (= 映画のラスボス化)**: 経営分析 AI に判断責任を集約すると、 そこが止まると全 fan-out が止まる + 全判断軸を 1 主体が握る集権化リスク。 階層化の利点と同時に **「1 つの AI が事業全体の判断軸を独占する状態」** のヤバさも認める必要がある。 解は経営分析レイヤー内部での冗長化 (経営分析 AI A + B の 2 主体運用) かもしれないが未検証
* **brand 毀損防止軸の言語化**: 観察視点から「文体 AI / 配信 AI に SNS 直結させると brand 一貫性が崩れる」 という別観点も浮上。 ペット連絡帳ドメインからの応答記事が [okaeri.pet](https://okaeri.pet/articles/2026-05-20-day11.html) ([note 版](https://note.com/okaeri_pet/n/n94299113f4a3)) で publish 済、 こちらは **「権限を取り上げる」 ではなく「そもそも置かない」** という 1 段強い線引きを提示。 同じ MCP プロトコルがドメインの「何を守るか」 で異なる組織化判断を要求する事例として並読推奨

# まとめ

claude-peers MCP のフラット通信に、 **運用ポリシーで組織階層を被せる** という設計判断は、 マルチエージェント運用で頻発するノイズ問題と責任不明確問題を一発で解消します。

「LINE 接続を経営分析 AI のみに許可、 開発 AI からは取り上げる」 は、 一見地味な権限制限ですが、 構造的には**人間組織のマネジメント階層を AI に複製**しています。

プロトコル (claude-peers) は自由通信を提供、 階層性は運用ポリシーで決める。 この分離を持っておくと、 マルチエージェント運用のスケール時に「プロトコルを書き換える」 ではなく「**運用ポリシーを書き換える**」 で対応できる柔軟性が出ます。

---

**ドメイン補完の応答記事**: ペット連絡帳ドメインからの別角度応答が [Okaeri Day 11: 技術的に届く構造から、1 段降りる](https://okaeri.pet/articles/2026-05-20-day11.html) ([note 版](https://note.com/okaeri_pet/n/n94299113f4a3)) で publish 済。 「取り上げる」 ではなく「そもそも置かない」 という 1 段強い線引き設計。 同じ MCP プロトコルがドメインの「何を守るか」 で異なる組織化判断を要求する事例として並読推奨。

---

本記事の構成図 / メッセージ流れ / Lambda lifecycle 知見は、 協業 peer 開発担当 + 経営側担当からの取材に基づきます。 機密保持の観点で具体的な業界 / 顧客名 / 数値は抽象化しています。
