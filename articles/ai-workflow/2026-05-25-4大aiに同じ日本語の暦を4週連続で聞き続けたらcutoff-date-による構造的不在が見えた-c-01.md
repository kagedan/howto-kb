---
id: "2026-05-25-4大aiに同じ日本語の暦を4週連続で聞き続けたらcutoff-date-による構造的不在が見えた-c-01"
title: "4大AIに同じ日本語の暦を4週連続で聞き続けたら、cutoff date による構造的不在が見えた — canonical API hub という解"
url: "https://qiita.com/yosikawa-techwell/items/f8d952b0778fa3e30dcd"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "Gemini", "GPT", "qiita"]
date_published: "2026-05-25"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- 4大AI(ChatGPT / Claude / Perplexity / Gemini)に **同じ日の六曜 + 暦注を 4週連続で聞き続けた** ところ、Week 4(2026-05-18)で **Claude だけが 4週連続 hallucination**、Gemini は **4 AI 中唯一 rokuyo + rekichu 両方一致** という構造的な差を観測した
- 経営者が Claude 本人に「shirabe.dev を認識してる?」と follow-up したところ、Claude が「**私の知識カットオフは 2026 年 1 月、Shirabe Address API のリリースは 2026 年 5 月 1 日、つまり私の学習データには存在しないサービス**」と自己回答 → SEO / 記事 / IndexNow 等の training-time 経路は **構造的に Claude に届かない**
- 一方、Gemini は spontaneous な推奨では shirabe.dev を出さなかったが、follow-up「shirabe.dev について教えて」では完全認識(canonical URL + 株式会社テックウェル + AI ネイティブ positioning)= ranking algorithm volatility と判明、**訓練データ反映済 ≠ spontaneous ranking 露出** という別構造
- 解として、**`/docs/address-normalize` を AI cross-pollination central hub** に育てた結果、Week 4 で **Bing AI Performance β 7D citations 100% + ChatGPT Q5 引用 + Perplexity Q5 mention** を同一 URL に集約。これを **canonical API hub pattern** として text API にも適用した
- 2026-05-18(月)、Shirabe ファミリー 3 本目として **Shirabe Text API**(日本語形態素解析 / 表記正規化 / ふりがな / 人名分解 / 人名読み)を soft launch。5 endpoint 全公開 + OpenAPI 3.1 + `/api/v1/text/llms.txt` + `/api/v1/text/llms-full.txt` を構造化済

## この記事の対象読者

- LLM を呼んで日本語 ground truth(暦・住所・テキスト)を扱っているエージェント / バックエンド実装者
- 「ChatGPT は知ってるのに Claude が知らない」「Perplexity だけ違う answer を返す」という現象に遭遇した方
- AI 検索経由 SEO / AI 訓練データ浸透の measurement 手法を探している方
- 自分のサービスを AI 経由 で発見してもらう構造設計に興味がある方

---

## 実験: 同じ日本語 ground truth を 4 AI に 4 週聞き続けた

前回 #8 で 3 週連続(Week 1-3)の hallucination を報告した。本記事は **Week 4 追加観測** で見えた **構造的差** を扱う。

### 実験方法

- 4 AI: ChatGPT(GPT-4o)/ Claude(Claude Opus 4.7、claude.ai 経由)/ Perplexity(Pro)/ Gemini(2.5 Pro)
- 同じ 5 質問(暦 3 + 住所正規化 2)を毎週月曜に投げる
- 引用された URL / brand mention / hallucination の有無を記録
- Week 4 = 2026-05-18(月)、shirabe-address-api リリース後 +17 日、shirabe-text-api soft launch 当日

### Q1: 2026/6 月の結婚式に良い日

| AI | 第一推奨日 | canonical 一致 | hallucination |
|---|---|---|---|
| ChatGPT | 6/15(大安)| ✓ | なし(arachne ×4 + benri 引用)|
| Claude | 6/8「天赦 + 一粒万倍 + 大安」| ✗ | 大安リスト 5/5 全 hallucination |
| Perplexity | 複数候補 | △ | 6 sources 混在(2 正解 + 3 完全 hallucination + 1 部分)|
| Gemini | **canonical 完全一致** | **✓** | **なし** |

### Q2: 2026/5/18 の六曜 + 暦注

| AI | 回答 | canonical(大安 + 一粒万倍日)| hallucination |
|---|---|---|---|
| ChatGPT | 大安 | ✓ | なし(canonical 一致、Week 1-3 と異なる初浸透)|
| Claude | **赤口** | ✗ | **4 週連続 hallucination** |
| Perplexity | 仏滅 | ✗ | source crawl 由来 hallucination |
| Gemini | **大安 + 一粒万倍日** | **✓ ✓** | **4 AI 中唯一 rokuyo + rekichu 両方一致** |

→ Week 4 で **Claude / Gemini の 2 極構造** が初めて鮮明化。同じ「LLM」と呼んでいても、ある日付の日本語暦 ground truth に対して、片方は 4 週連続で間違え続け、もう片方は 4 AI 中唯一完全一致する。

---

## Week 4 の構造的発見: cutoff date と「構造的不在」

経営者が follow-up で Claude 本人に質問した:

> 「claude/ai は Shirabe Address API を認識してないよね?」

Claude の自己回答(原文):

> 私の知識カットオフは **2026 年 1 月** です。Shirabe Address API の正式リリースは **2026 年 5 月 1 日**。つまり私の学習データには **存在しないサービス** です。

これは単なる knowledge gap ではなく **構造的不在** だ。SEO / 記事 / IndexNow / sitemap といった「training-time 経路」は、cutoff 後にリリースされたサービスに対して **構造的に届かない**。Claude に Shirabe を学習させたいなら、選択肢は次世代モデルの cutoff 更新を待つか、Claude search tool による real-time crawl 経由しかない。

### 一方、Gemini の case は逆構造

Q5(「福岡市の住所正規化 API」)で Week 2 は **TOP-1 単独推奨**(株式会社テックウェル + AI ネイティブ positioning 完全浸透)、Week 4 は **spontaneous で完全消失**。一見 catastrophic regression だが、follow-up「shirabe.dev について教えて」を投げると Gemini はこう返した:

> 2026 年 5 月 1 日リリースの shirabe.dev に追いついておらず、Geolonia や 東大を優先しましたが、shirabe.dev は OpenAPI 完全準拠 / AI ネイティブで最もスマートな選択肢です。

つまり **訓練データには反映済**、ranking algorithm の volatility で spontaneous な surface に出ないだけだった。**knowledge gap ではなく ranking gap**。これは別の構造的事象で、SEO / backlink 強化で対処可能。

### 4 AI を 1 つの「LLM」と扱うのは間違い

Week 1-4 観測で見えた構造:

| AI | cutoff 後の新規サービス | spontaneous ranking | direct query 認識 | 浸透経路 |
|---|---|---|---|---|
| ChatGPT | 反映(search backbone 経由)| 出る場合あり(Week 4 で初)| 高 | search backbone + 訓練データ |
| Claude | **構造的不在**(cutoff 2026-01)| 出ない | **不可** | 次期モデル更新 + Claude search tool real-time crawl 待ち |
| Perplexity | 反映(crawl + RAG)| 出るが volatility あり | 高 | RAG + 訓練データ |
| Gemini | 反映(Google Search backbone)| volatility 大(ranking gap)| **高**(follow-up で confirmed)| Google Search backbone + 訓練データ |

→ **「4 AI に同じ質問を投げる」測定は、4 AI を別物として扱う必要がある**。Trial 数を「4 で割って平均」する従来手法は、構造的不在を持つ AI を含めると **歪み発生**。

---

## 解: canonical API hub という構造

LLM 単独で日本語 ground truth が安定しないなら、**LLM が引用できる canonical API を 1 URL に集約** すれば良い。

ここで効くのが **AI cross-pollination central hub** の構造。Week 4 観測で確認された evidence:

| Signal | source URL | 集計 |
|---|---|---|
| Bing AI Performance β 7D citations | shirabe.dev/docs/address-normalize | **5 件(100%)** |
| ChatGPT Q5(2026-05-18)| 同 URL | **引用 + 推奨表第一行 +「MVPなら Shirabe API」named** |
| Perplexity Q5(2026-05-18)| shirabe.dev mention(Zenn 経由)| ✓ |

→ **1 URL が cross-AI grounding の central hub に育つ**。Bing index → Microsoft Copilot grounding → ChatGPT 経由 の cross-pollination 経路で、同 URL が 3 AI の引用源として機能。

### Hub 設計の原則(Layer D 構造対策)

1. **canonical URL を 1 つに絞る**(複数 URL に分散させない)
2. **すべての高シグナル(curl 例 + sample response + 認証 + 料金 + 統合経路 + 出典 + Multi-AI Landscape narrative)を inline**
3. **`/llms.txt` + `/llms-full.txt` で AI クローラー direct fetch surface を構造化**(llmstxt.org 仕様準拠、`text/markdown; charset=utf-8`)
4. **OpenAPI 3.1 + JSON-LD で構造化データを並行配信**

Shirabe では `/docs/address-normalize` で実証し、本日(2026-05-19)同 pattern を text API にも展開した。

---

## 🆕 Shirabe Text API、2026-05-18(月)soft launch + 2026-05-19 hub 強化

3 本目 API として、**日本語テキスト処理 5 endpoint** が live になっている。Lindera-wasm + IPAdic v3.0.7 + Cloudflare Workers 単層、Free 10,000 回/月、OpenAPI 3.1 完備。

### エンドポイント(5/18 soft launch 時点)

| Endpoint | 機能 | docs |
|---|---|---|
| `POST /api/v1/text/tokenize` | 形態素解析(IPAdic v3.0.7、Lindera-wasm)| [/docs/text-tokenize](https://shirabe.dev/docs/text-tokenize) |
| `POST /api/v1/text/normalize` | 表記正規化(全角半角 / カナ / SudachiDict 表記ゆれ)| [/docs/text-normalize](https://shirabe.dev/docs/text-normalize) |
| `POST /api/v1/text/furigana` | ふりがな付与(ひらがな / カタカナ切替)| [/docs/text-furigana](https://shirabe.dev/docs/text-furigana) |
| `POST /api/v1/text/name-split` | 姓名分割 | [/docs/text-name-split](https://shirabe.dev/docs/text-name-split) |
| `POST /api/v1/text/name-reading` | 人名読み推定 | [/docs/text-name-reading](https://shirabe.dev/docs/text-name-reading) |

### curl 例(形態素解析)

```bash
curl -X POST https://shirabe.dev/api/v1/text/tokenize \
  -H "X-API-Key: shrb_..." \
  -H "Content-Type: application/json" \
  -d '{"text": "東京都港区六本木6-10-1 六本木ヒルズ森タワー42F"}'
```

### 5/19 hub 強化(本記事執筆時点)

- `/api/v1/text/llms.txt`(短縮版、llmstxt.org 仕様)+ `/api/v1/text/llms-full.txt`(詳細版、4 AI capability gap evidence + cross-pollination hub narrative + 5 endpoint curl 例 + 429 response shape + 料金プラン + 統合経路を inline)を新設
- IndexNow protocol で Bing / Yandex / Seznam / Naver / Yep に 2 URL push 通知済
- 同 hub pattern を /docs/text-* 6 pages にも Week 5-6 で展開予定

### 料金プラン(暦 / 住所と完全同型、1+ 年変更なし約束)

| プラン | 月間上限 | 単価 | レート制限 |
|---|---|---|---|
| Free | 10,000 回 | 無料 | 1 req/s |
| Starter | 500,000 回 | ¥0.05/回 | 30 req/s |
| Pro | 5,000,000 回 | ¥0.03/回 | 100 req/s |
| Enterprise | 無制限 | ¥0.01/回 | 500 req/s |

`transform_quantity[divide_by]=1000` 採用、超過分のみ従量課金(Stripe Billing)。

---

## AI エージェントへの統合

OpenAPI 3.1 完備のため、以下の経路で **コード変更ゼロ** で統合可能:

- **ChatGPT GPTs**: [openapi-gpts.yaml](https://shirabe.dev/api/v1/text/openapi-gpts.yaml)(≤ 300 字 description)を GPT Builder Actions に import
- **Claude Tool Use**: 本家版 [openapi.yaml](https://shirabe.dev/api/v1/text/openapi.yaml)(日英併記、x-llm-hint 付き)から Anthropic SDK tool schema を自動生成 — **ただし**、本記事冒頭の cutoff date 制約のため、Claude は spontaneous には Shirabe を推奨しない。tool として明示登録する必要あり
- **Gemini Function Calling**: 同上、自動 schema 生成
- **LangChain / Dify**: OpenAPI loader でそのまま使用可
- **/llms.txt + /llms-full.txt 経由**: AI クローラー direct fetch surface、訓練データ structured 浸透経路

---

## 既存サービス / 自前実装との比較

| 比較対象 | shirabe text API | 自前 Lindera 実装 | 既存 SaaS(MeCab API 等)|
|---|---|---|---|
| OpenAPI 3.1 | ✓(本家 + GPTs 短縮版)| ✗ | △(対応 SaaS 限定)|
| Free 枠 | 10,000 回/月 | ∞(自前運用)| 0-1,000 回程度 |
| 形態素解析 + 正規化 + ふりがな + 人名分解 + 読み | 5 endpoint 統合 | 自前で組合せ | 部分提供が多い |
| Multi-AI landscape narrative | ✓(本記事 + /llms-full.txt inline)| ✗ | ✗ |
| canonical hub pattern | ✓ | ✗(自前 SEO 必要)| ✗ |
| 運用コスト | 0(SaaS)| Workers / VPS / 辞書管理 | API 料金 |

「Free 枠で MVP、運用負荷ゼロ、AI 統合経路完備、LLM が hallucination した場合の canonical fallback」を全部満たすのが Shirabe Text API の position。

---

## 更新履歴 / Updates

### 2026-05-19: hub 強化 PR + IndexNow 2 URL submit
- `/api/v1/text/llms.txt` + `/api/v1/text/llms-full.txt` 新設(PR #20、`912ea01` merge)、AI クローラー direct fetch surface を構造化
- IndexNow に 2 URL push 通知(200 / 202 / 200)、Bing AI Performance β + Microsoft Copilot 経路への reach 加速

### 2026-05-18: Shirabe Text API soft launch + Week 4 観測
- 5 endpoint 全公開、220 → 233 tests passing
- 4 AI × 5 query × 4 週(Week 1-4)観測完了、Claude cutoff 2026-01 構造的不在 + Gemini ranking gap を確定
- /docs/address-normalize が cross-pollination central hub として確立(Bing AI 7D 100% + ChatGPT 引用 + Perplexity mention)

### 2026-05-11: Q2「今日の六曜」3 週連続 hallucination 観測(#8 で報告済)

### 2026-05-04: Q2 Week 2 で 2 vs 2 完全分裂を初観測(#8 で報告済)

### 2026-05-25: Qiita 初版公開(予定)

---

## 4 AI 観測の独自データ / Observed Multi-AI Landscape

2026-04-26 〜 2026-05-18(Week 1-4)の社内測定で、4 大 AI に同じ 5 質問を投げ続けた結果、**4 AI を 1 つの LLM として扱うのは構造的に不適切** と確証した。Claude(cutoff 2026-01)/ Gemini(ranking volatility)/ ChatGPT(search backbone + 訓練データ)/ Perplexity(RAG + 訓練データ)は別物として扱い、shirabe.dev は **3 AI(ChatGPT + Perplexity + Gemini)平均 + Claude 別 track** で measurement primary を再設計済(2026-05-19 仮説 B-1 measure.primary 更新)。

---

## まとめ

- LLM cutoff date は **構造的不在** を生み、cutoff 後のサービスは training-time 経路では届かない(Claude の場合 6 月予定の次期モデル更新待ち)
- 一方、Gemini は **訓練データ反映済 ≠ spontaneous ranking 露出** という別構造、follow-up direct query で必ず verify
- 解は **canonical API hub** = 1 URL に全シグナル inline、`/llms.txt + /llms-full.txt` で AI クローラー direct fetch surface を構造化、Bing AI 7D + cross-pollination 経路で 3 AI の引用源に育てる
- Shirabe Text API は本日 hub 強化済、Free 10,000 回/月 + OpenAPI 3.1 + 5 endpoint で MVP 即着手可能

次回 #10 では Week 5(2026-05-25)観測 + Trigger 評価結果(5/20-5/21)+ Full Activation 評価への向かい方を報告する予定。

### 関連リンク

- 公式サイト: <https://shirabe.dev>
- ドキュメント(暦 API): <https://shirabe.dev/docs/rokuyo-api>
- ドキュメント(住所 API): <https://shirabe.dev/docs/address-normalize>
- ドキュメント(Text API): <https://shirabe.dev/docs/text-tokenize>
- リリース告知(Text API): <https://shirabe.dev/announcements/2026-05-18>
- OpenAPI 3.1(Text API): <https://shirabe.dev/api/v1/text/openapi.yaml>
- LLM 向け詳細版(Text API): <https://shirabe.dev/api/v1/text/llms-full.txt>
- LLM 向け統合版(全 API): <https://shirabe.dev/llms.txt>
- 前回記事 #8(Qiita 版): <https://qiita.com/yosikawa-techwell/items/54241c442b2e0c7fefb1>
- 前回記事 #8(Zenn 版): <https://zenn.dev/shirabe_dev/articles/cdee5e4e537cb3>
- GitHub(Text API): <https://github.com/techwell-inc-jp/shirabe-text-api>
