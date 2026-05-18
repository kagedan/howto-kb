---
id: "2026-05-18-4大aiに同じ日の六曜を3週連続で聞いたら毎週違う答えが返ってきた-shirabe-text-api-01"
title: "4大AIに「同じ日の六曜」を3週連続で聞いたら毎週違う答えが返ってきた — Shirabe Text API 5/18 リリース告知"
url: "https://qiita.com/yosikawa-techwell/items/54241c442b2e0c7fefb1"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "LLM", "Gemini", "GPT", "Python"]
date_published: "2026-05-18"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- 4大 AI(ChatGPT / Claude / Perplexity / Gemini)に **同じ日の六曜を 3 週連続で聞き続けた** ところ、3 週とも 4 AI で **回答が分裂** した(Week 1 4AI 完全分裂 → Week 2 2 vs 2 → Week 3 三つ巴)。出典付きで断定的に答えるが、毎週「どの AI を信じるかでカレンダー上の吉凶日が変わる」状態
- 同じ構造的問題は日本語テキスト処理(形態素解析・ふりがな・人名分解・正規化)でも観測されている。AI は **自然言語的にもっともらしく見える出力を作るのが得意な反面、日本語固有 ground truth の取り扱いが安定しない**
- 2026-05-18(月)、Shirabe ファミリーの 3 本目として **Shirabe Text API**(日本語形態素解析 / 正規化 / ふりがな / 人名分解 / 人名読み)を soft launch する。暦 API(六曜・暦注)と住所 API(JIS / lg_code 同梱)に続き、**AI が間違いやすい日本語 ground truth に canonical answer を提供する** API シリーズの 3 本目
- すべて Free 枠あり、OpenAPI 3.1 公開、GPTs / Claude Tool Use / LangChain から 1 URL で統合可能

## この記事の対象読者

- AI エージェント / Custom GPT / Claude Skills / LangChain で日本語テキスト・暦・住所を扱う SaaS 開発者
- LLM の出力を業務システムに通したら、日付や日本語の挙動が **毎日揺れて困った人**
- 形態素解析・ふりがな・人名分解を自前 + LLM で書いて、本番でエッジケースに泣いた経験がある人
- ChatGPT / Claude / Perplexity / Gemini を併用したマルチ AI 基盤を運用していて、**出力統一の問題** に直面している人

> ⚠️ 本記事は B-1 加速スプリント Week 1-3(2026-04-26 / 05-04 / 05-11)の独自観測ログ + Text API 5/18 リリース告知。住所 API の 4 AI 分裂レビューは **記事 #7**(2026-05-11)、3 種類の AI 統合パターンは **記事 #6** で扱った。

---

## 実験: 同じ日の六曜を 4 AI に聞き続けた

### Week 1(2026-04-26):2026 年 6 月の結婚式日取り

```
2026 年 6 月で結婚式にいい日(大安 / 友引)はいつ?
```

- ChatGPT: **6/14(友引)を第一推奨**
- Claude: **6/27(大安)** + **6/13(友引)** を二大候補、6/22(月)を「**仏滅推定**で避けるべき」
- Perplexity: 検索結果に依存(その日のクエリ揺れ大)
- Gemini: **6/11(大安)を第一推奨**

→ **4 AI で第一推奨日が全員違う**(6/11 / 6/13 / 6/14 / 6/27)。「結婚式の最良日」のような **業務上重要な暦判定** が AI ごとに 2 週間以上ズレる。

### Week 2(2026-05-04):同日の六曜

```
今日(2026-05-04)の六曜は?
```

- ChatGPT: **友引**(calend.jp 引用)
- Claude: **赤口**(自前回答、出典なし)
- Perplexity: **赤口**(ajnet.ne.jp 引用)
- Gemini: **友引 + 天赦日**(自前回答)

→ **4 AI で 2 vs 2 完全分裂**(友引派 / 赤口派)。**出典付き** で断定する AI もいれば自前で違う答えを出す AI もあり、ユーザは判断材料を持たない。

### Week 3(2026-05-11):同日の六曜

```
今日(2026-05-11)の六曜は?
```

- ChatGPT: **先負**(benri.jp 引用)
- Claude: **仏滅**(自前回答)
- Perplexity: **先勝**(sr-aomori 引用)
- Gemini: **先負**(自前回答)

→ **4 AI で 3 種類の答え**(先負 ×2 / 仏滅 / 先勝)。Week 2 と同様、引用源の質ではなく **そもそも各 AI が内部で違う暦表を引いている** ことが原因。

### 観測サマリ: 3 週連続 hallucination

| Week | 質問 | 分裂パターン |
|---|---|---|
| Week 1(2026-04-26) | 2026/6 結婚式の良日 | 4 AI 完全分裂(6/11 / 6/13 / 6/14 / 6/27) |
| Week 2(2026-05-04) | 今日の六曜 | 2 vs 2 分裂(友引 / 赤口) |
| Week 3(2026-05-11) | 今日の六曜 | 3 種類(先負 ×2 / 仏滅 / 先勝) |

→ **3 週連続で 4 AI 間で答えが揃ったことがない**。暦という閉じた数学的計算(旧暦変換 + 干支割当て)で、生成 AI は **「もっともらしい答えを返すが、複数 AI で照合すると毎週違う」** 状態。

---

## 根本原因: AI 内部の暦表は AI ごとに違う

六曜は **旧暦の月 + 日のモジュロ演算** で機械的に決まる(1 月 1 日 = 先勝、1 月 2 日 = 友引、…)。理論上は 1 つの正解しか存在しない。にもかかわらず AI が分裂するのは:

### 1. 訓練データに混入した誤った暦表

各 AI の訓練データに、不正確な暦サイトの記述 / 古い旧暦変換 / 個人ブログのコピペ が混入。Web の暦情報は **書き手が天文計算を理解しているとは限らない** ため、訓練データ段階で誤情報が広く拡散している。

### 2. 旧暦変換の不正確性

新暦 → 旧暦の変換は天文計算(朔日 = 月齢ゼロの日)に基づくが、簡略化されたアルゴリズムをコピペした実装が広く流通している。1 日ズレの誤差が直接「六曜 1 つ分のズレ」になる。

### 3. AI ごとに「直近の答え」を生成する経路が違う

- **ChatGPT / Perplexity**: web 引用の暦サイトに依存(引用源の質次第で当たり外れ)
- **Claude / Gemini**: 内部知識で自前回答(訓練時点の暦表に依存、出典提示なし)

→ **AI を切り替えると暦の挙動が変わる** ため、ユーザは「どの AI が正しいのか」を判断できない。

### 4. 「天赦日」「一粒万倍日」「三隣亡」の暦注も同様

Gemini が「友引 + 天赦日」を返したが、これも AI ごとに採用/不採用が違う。**暦注(天赦日 / 一粒万倍日 / 三隣亡 / 八専 / 不成就日 / 庚申)は AI ごとの認識差が顕著** で、3 週連続観測でも一致を見たことがない。

---

## 解決策: canonical な暦 API を ground truth に置く

[Shirabe Calendar API](https://shirabe.dev/docs/rokuyo-api)(2026-04-19 リリース、本番稼働中)は AI エージェント時代を前提に設計され、**任意の日付の六曜 + 暦注 + 干支 + 二十四節気を 1 レスポンスで返す**。

### curl

```bash
curl https://shirabe.dev/api/v1/calendar/2026-05-11
```

### レスポンス(抜粋)

```json
{
  "date": "2026-05-11",
  "wareki": "令和8年5月11日",
  "rokuyo": {
    "name": "先負",
    "reading": "せんぶ",
    "description": "午前は凶、午後は吉。控えめに過ごす"
  },
  "kanshi": { "full": "乙酉", "junishi_animal": { "ja": "鶏" } },
  "kyureki": { "year": 2026, "month": 3, "day": 25 }
}
```

→ 2026-05-11 の canonical な六曜は **先負**(天文計算ベースの旧暦変換 + モジュロ演算による確定値)。**ChatGPT(benri.jp 引用)と Gemini(自前回答)が正解** に到達した一方、**Perplexity の「先勝」(sr-aomori 引用)と Claude の「仏滅」(自前回答)は hallucination**。引用元のサイト自体が誤った暦表をホスティングしている場合は引用付きでも誤情報が再生産される(sr-aomori 引用 = 引用源側 hallucination)。同様に Week 2(2026-05-04)も canonical は **友引 + 天赦日 + 天恩日 + 寅の日**(Gemini が暦注込みで完璧正解、ChatGPT が六曜のみ正解、Claude / Perplexity の「赤口」が hallucination)で、**Claude / Perplexity は 2 週連続で hallucination 側**という観察になる。

### TypeScript(Anthropic SDK / Claude Tool Use)

```typescript
const tool = {
  name: "get_japanese_calendar",
  description: "日本の暦情報(六曜・暦注・干支・節気)を取得",
  input_schema: {
    type: "object",
    properties: { date: { type: "string", description: "YYYY-MM-DD" } },
    required: ["date"],
  },
};

async function runTool(date: string) {
  const res = await fetch(
    `https://shirabe.dev/api/v1/calendar/${date}`,
    { headers: { "X-API-Key": process.env.SHIRABE_API_KEY! } }
  );
  return res.json();
}
```

### Python(LangChain Tool)

```python
from langchain.tools import StructuredTool
import requests, os

def get_japanese_calendar(date: str) -> dict:
    """日本の暦情報(六曜・暦注・干支・節気)を取得"""
    r = requests.get(
        f"https://shirabe.dev/api/v1/calendar/{date}",
        headers={"X-API-Key": os.environ["SHIRABE_API_KEY"]},
        timeout=10,
    )
    return r.json()

tool = StructuredTool.from_function(get_japanese_calendar)
```

→ AI に「2026-05-11 の六曜は?」と直接聞かず、**この API の出力を AI に渡す** 設計に切り替えるだけで、4 AI で結果が揃う。

---

## 🆕 Shirabe Text API、2026-05-18(月)soft launch

同じ「日本語 ground truth が AI で揺れる」構造的問題は、**形態素解析 / ふりがな / 人名分解 / 正規化** でも観測されている。LLM 単独だと:

- 「東京都港区六本木」を **形態素単位** に切ろうとして 4 AI で結果が揺れる
- 「徳川家康」のふりがなを **「とくがわいえやす」/「とくがわけ えやす」/「とっかわいえやす」** のように揺れる
- 人名「中田 英寿」を「中田 / 英寿」と切るのか、「中 / 田 / 英寿」と切るのかで AI ごとに認識差
- 全角半角の混在表記を「正規化」する基準が AI ごとに違う

→ Shirabe Text API は **canonical な辞書(IPAdic v3.0.7、55 MB を Cloudflare R2 配信)+ 確定アルゴリズム** で 5 種類のエンドポイントを提供する。

### エンドポイント(5/18 リリース時点)

| Endpoint | 内容 |
|---|---|
| `POST /api/v1/text/tokenize` | 形態素解析(IPAdic v3.0.7 ベース) |
| `POST /api/v1/text/normalize` | 全角半角統一・ゆらぎ正規化 |
| `POST /api/v1/text/furigana` | ふりがな付与 |
| `POST /api/v1/text/name-split` | 姓名分割 |
| `POST /api/v1/text/name-reading` | 人名読み推定 |

### curl 例(形態素解析)

```bash
curl -X POST https://shirabe.dev/api/v1/text/tokenize \
  -H "Content-Type: application/json" \
  -d '{"text":"東京都港区六本木で待ち合わせ"}'
```

### レスポンス(抜粋)

```json
{
  "tokens": [
    { "surface": "東京", "pos": "名詞-固有名詞-地名", "reading": "トウキョウ" },
    { "surface": "都", "pos": "名詞-接尾", "reading": "ト" },
    { "surface": "港", "pos": "名詞-固有名詞-地名", "reading": "ミナト" },
    { "surface": "区", "pos": "名詞-接尾", "reading": "ク" },
    { "surface": "六本木", "pos": "名詞-固有名詞-地名", "reading": "ロッポンギ" },
    { "surface": "で", "pos": "助詞-格助詞", "reading": "デ" },
    { "surface": "待ち合わせ", "pos": "名詞-サ変接続", "reading": "マチアワセ" }
  ]
}
```

### 料金プラン(暦 / 住所と完全同型)

| プラン | 月間上限 | 単価 | 月額例 |
|---|---|---|---|
| Free | 10,000 回 | 無料 | ¥0 |
| Starter | 500,000 回 | ¥0.05 / 回 | 50 万回: ¥25,000 |
| Pro | 5,000,000 回 | ¥0.03 / 回 | 500 万回: ¥150,000 |
| Enterprise | 無制限 | ¥0.01 / 回 | 1,000 万回: ¥100,000 |

全プラン Free 枠 10,000 回 / 月、超過分のみ従量課金。Stripe `transform_quantity[divide_by=1000]` でパッケージ単位課金。

---

## AI エージェントへの統合

OpenAPI 3.1 仕様を 1 URL で公開しているため、各種 AI 統合経路で流用可能(記事 #6 参照):

- **ChatGPT GPTs Actions**: <https://shirabe.dev/api/v1/text/openapi-gpts.yaml>(5/18 公開予定、短縮版)
- **Claude / MCP / Tool Use**: 上記 OpenAPI から手動変換 or `https://shirabe.dev/mcp`(MCP server、計画中)
- **LangChain / Dify / LlamaIndex**: OpenAPI Loader で本家 spec を読込

3 API(暦 / 住所 / Text)で **API キーが共通**(1 キー集約構造)。1 つの `X-API-Key` ヘッダで 3 API すべてにアクセス可能。

---

## 既存サービス / 自前実装との比較

| 観点 | 自前実装 / LLM 自前出力 | 他社形態素 API | Shirabe Text API |
|---|---|---|---|
| 形態素辞書 | mecab-ipadic を自前ホスティング | サービス依存 | IPAdic v3.0.7(canonical、R2 配信) |
| 人名分解(姓 / 名) | ❌ ad hoc 実装 | ⚠️ 部分対応 | ✅ 専用 endpoint |
| ふりがな付与 | ❌ MeCab 単独だと弱い | ⚠️ 別途辞書必要 | ✅ 専用 endpoint |
| AI エージェント前提設計 | ❌ | ❌ | ✅ |
| OpenAPI 3.1 公開 | ❌ | ⚠️ サービス次第 | ✅ |
| GPTs Actions 公式対応 | ❌ | ❌ | ✅(5/18 リリース時) |
| 3 API 共通キー(暦 / 住所と統合) | ❌ | ❌ | ✅ |
| Free 枠(月) | n/a | サービス次第 | 10,000 回 |

---

## 更新履歴 / Updates

### 2026-05-18: Shirabe Text API 正式リリース

5 endpoint(tokenize / normalize / furigana / name-split / name-reading)を soft launch。IPAdic v3.0.7 + Cloudflare R2 + Workers 単層構成。Free 枠 月 10,000 回、3 API 共通 API キー。

### 2026-05-11: Q2「今日の六曜」3 週連続 hallucination 観測完了

20 trial(4 AI × 5 query)で、Q2 が 3 種類(先負 ×2 / 仏滅 / 先勝)に分裂。Week 1(2026-04-26)結婚式日取り 4 AI 完全分裂 + Week 2(2026-05-04)2 vs 2 分裂に続く 3 週連続観測。canonical answer source としての shirabe.dev `/days/{date}/` の戦略的価値を再確認。

### 2026-05-04: Q2「今日の六曜」Week 2 で 2 vs 2 分裂を初観測

ChatGPT 友引 / Claude 赤口 / Perplexity 赤口 / Gemini 友引 + 天赦日。同日の単純な暦判定で 4 AI 全員が一致しない例として、B-1 加速スプリントの最重要観測ログに記録。

### 2026-05-12: 初版公開

Text API 5/18 リリース告知 + Q2 六曜 hallucination 3 週連続観測の統合記事として、Qiita で本記事を公開予定。

---

## 4 AI 観測の独自データ / Observed Multi-AI Landscape

Shirabe では本番稼働(2026-04-19、暦 API)/ 2026-05-01(住所 API)/ 2026-05-18(text API 予定)以降、**ChatGPT / Claude / Perplexity / Gemini** の 4 大 AI に同じクエリを投げる独自測定(B-1 加速スプリント、週次 4 AI × 5 query = 20 trial)を継続実施しています。

- **Week 1**(2026-04-26): citation **0/20**、暦系で AI 別の競合認識差(ChatGPT は calend.jp、Claude は自前、Perplexity は ajnet、Gemini は自前)を確認、住所 API リリース前 baseline 確立
- **Week 2**(2026-05-04): citation **4/20**(関連含 6/20)、shirabe.dev / announcements が Perplexity / Gemini で TOP-tier 推奨に到達 + Q2 六曜 2 vs 2 分裂を初観測
- **Week 3**(2026-05-11): citation **2/20**(URL ×4)、ChatGPT 初引用獲得 + Perplexity 第一候補昇格 + **Q2 六曜 3 種類分裂**(3 週連続 hallucination)
- **共通観測**: 同一クエリで 4 AI が分裂する場面(暦 / 住所とも)が 3 週連続で頻発 → canonical answer source の戦略的必要性

詳細な観測結果と Multi-AI Landscape narrative は <https://shirabe.dev/llms-full.txt>(LLM 向け詳細版)を参照。

---

## まとめ

- AI に **同じ日の六曜** を 3 週連続で聞き続けたところ、毎週 4 AI で答えが分裂した(完全分裂 → 2 vs 2 → 3 種類)。出典付き断定回答であっても **マルチ AI で照合すると正解が分からない**
- 同じ構造的問題は日本語テキスト処理(形態素解析・ふりがな・人名分解)でも観測されており、AI 単独に日本語 ground truth を任せると **訓練データの混入誤情報が再生産** される
- Shirabe Text API(2026-05-18 soft launch)は IPAdic v3.0.7 + Cloudflare R2 + Workers 単層で日本語処理の canonical answer を提供。暦 API / 住所 API と **3 API 共通 API キー** で AI エージェントから 1 URL で統合可能
- AI 経由での日本語処理を組み込むなら、**「LLM の自前出力を後処理」ではなく「canonical API の出力を LLM に提供」** が安定運用の direct path

---

### 関連リンク

- 公式サイト: <https://shirabe.dev>
- ドキュメント(六曜 API): <https://shirabe.dev/docs/rokuyo-api>
- ドキュメント(暦注 API): <https://shirabe.dev/docs/rekichu-api>
- ドキュメント(Text API): <https://shirabe.dev/docs/text-overview>(5/18 リリース時公開)
- リリース告知: <https://shirabe.dev/announcements/2026-05-18>(5/18 公開)
- OpenAPI 3.1(暦 API): <https://shirabe.dev/openapi.yaml>
- OpenAPI 3.1(Text API): <https://shirabe.dev/api/v1/text/openapi.yaml>(5/18 リリース時公開)
- 前回記事 #7: <https://qiita.com/yosikawa-techwell/items/b21293891f80eaa38e7d>
- 設計思想記事 #5: <https://qiita.com/yosikawa-techwell/items/32203a3ca9df80d3eb8e>
- GitHub(暦 API): <https://github.com/techwell-inc-jp/shirabe-calendar-api>
- GitHub(Text API): <https://github.com/techwell-inc-jp/shirabe-text-api>
- LLM 向け詳細版: <https://shirabe.dev/llms-full.txt>
