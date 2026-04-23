---
id: "2026-04-04-claude-haiku-apiで中古車を5段階スコアリングする仕組み-01"
title: "Claude Haiku APIで中古車を5段階スコアリングする仕組み"
url: "https://qiita.com/bit-sap/items/cc5b41aacb3d0f11ab98"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-04"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

## はじめに

[中古車ウォッチ](https://car-watch.jp/)という、中古車サイト15社を自動巡回してLINEに新着通知するサービスを個人開発しています。

新着が見つかるたびに、**Claude Haiku APIで車両を分析し、5段階スコアをつけてLINEに通知**します。スコア5の「要チェック」物件だけ見れば、毎日何十件もの新着を全部チェックする必要がなくなります。

この記事では、スコアリングの仕組みとClaude APIの使い方、月$2-3で運用するコスト設計を紹介します。

## 通知の実例

LINEに届く通知はこんな感じです：

```
🎯 トヨタ プリウス 1.8 S
  ★★★★★ 🔥 要チェック
  💰 185万円
  📏 走行2.3万km / 2021年式
  🔧 車検2026年8月
  📊 価格は下位25%の割安ゾーン
  💡 ✓低走行、高年式、車検長い
  💡 △修復歴あり
  💡 中央値220万円比-16%
  💡 🤖 修復歴ありだが走行2.3万kmで車検も長く、
     同条件比-16%は割安。内容次第で買い
  🔗 https://carsensor.net/...
```

1通の通知で以下がわかります：

* **★5段階スコア**（ルールベース）
* **相場比較**（蓄積データから算出）
* **メリット・デメリット**（キーワード検出）
* **AIコメント**（Claude Haikuの一言分析）

## 処理パイプライン

```
新着検知 → DB保存 → フィルタ適用 → AI分析(Top3) → スコアリング → LINE通知
```

全件にClaude APIを呼ぶとコストがかさむので、**上位3件だけAI分析、残りはルールベースのみ**という設計です。

## ステップ1：ルールベースのスコアリング

まずは全物件にルールベースで1-5のスコアをつけます。ベース3点から加減算する方式です。

```
function calculateScore(
  listing: Listing,
  stats: MarketStats
): number {
  let points = 0;

  // --- 価格（相場比較） ---
  if (stats.medianPrice && listing.price) {
    const ratio = listing.price / stats.medianPrice;
    if (ratio <= 0.70) points += 3;      // 30%以上安い
    else if (ratio <= 0.85) points += 2;  // 15%以上安い
    else if (ratio <= 1.00) points += 1;  // 相場以下
    else if (ratio >= 1.30) points -= 1;  // 30%以上高い
  }

  // --- 走行距離 ---
  if (listing.mileage_km !== null) {
    const man = listing.mileage_km / 10000; // 万km換算
    if (man <= 1) points += 2;        // 極低走行
    else if (man <= 3) points += 1;    // 低走行
    else if (man >= 10) points -= 1;   // 多走行
  }

  // --- 年式 ---
  const age = new Date().getFullYear() - listing.year;
  if (age <= 3) points += 2;          // 高年式
  else if (age <= 5) points += 1;
  else if (age >= 10) points -= 1;    // 低年式

  // --- 車検 ---
  if (listing.inspection === "なし") points -= 1;
  if (listing.inspection === "整備付") points += 1;

  // --- リスク（重いペナルティ） ---
  if (listing.repair_history === "あり") points -= 2;
  if (/水没|冠水/.test(listing.raw_text)) points -= 3;

  // --- ボーナス ---
  if (/ワンオーナー/.test(listing.raw_text)) points += 1;
  if (/禁煙/.test(listing.raw_text)) points += 1;

  return Math.max(1, Math.min(5, Math.round(points + 3)));
}
```

ポイントは**相場データを使っている**こと。蓄積した物件データから中央値・四分位数を計算し、「この車種の中でこの価格はどうか」を判定します。

## ステップ2：相場データの算出

各監視URL（＝車種×サイト）ごとに、直近の物件データから統計値を計算します。

```
async function getMarketStats(monitoringUrlId: string): Promise<MarketStats> {
  const { data } = await supabase
    .from("properties")
    .select("price, mileage_km, year, first_seen_at, delisted_at")
    .eq("monitoring_url_id", monitoringUrlId)
    .order("first_seen_at", { ascending: false })
    .limit(500);

  const prices = data.map(d => d.price).filter(Boolean).sort((a, b) => a - b);

  return {
    medianPrice: median(prices),
    priceQ1: percentile(prices, 25),  // 下位25%
    priceQ3: percentile(prices, 75),  // 上位25%
    medianMileage: median(mileages),
    medianYear: median(years),
    weeklyNewCount: countNewThisWeek(data),
    avgDaysOnMarket: medianDaysOnMarket(data),
    priceTrendPct: monthOverMonthChange(data),
  };
}
```

これにより通知に含まれる「中央値220万円比-16%」「価格は下位25%の割安ゾーン」といった情報が生成されます。

## ステップ3：メリット・デメリット抽出

キーワードマッチで車両のメリット・デメリットを抽出します。

```
function deepAnalysis(listing: Listing): string {
  const merits: string[] = [];
  const demerits: string[] = [];

  // メリット
  if (listing.mileage_km < 30000) merits.push("低走行");
  if (age <= 5) merits.push("高年式");
  if (/ワンオーナー/.test(text)) merits.push("ワンオーナー");
  if (/禁煙/.test(text)) merits.push("禁煙車");
  if (/車検整備付/.test(text)) merits.push("車検整備付");
  if (/サンルーフ/.test(text)) merits.push("サンルーフ");

  // デメリット
  if (listing.mileage_km >= 100000) demerits.push("過走行");
  if (age >= 10) demerits.push("年式古い");
  if (/修復歴あり/.test(text)) demerits.push("修復歴あり");
  if (/車検なし|車検切れ/.test(text)) demerits.push("車検なし");
  if (/水没/.test(text)) demerits.push("水没歴");

  let result = "";
  if (merits.length) result += `✓${merits.join("、")}`;
  if (demerits.length) result += `。△${demerits.join("、")}`;
  return result;
}
```

出力例：`✓低走行、高年式、車検整備付。△修復歴あり`

ルールベースなので全物件に適用してもコストゼロです。

## ステップ4：Claude Haiku APIで一言分析

ここがこの記事の本題です。**上位3件だけ**、Claude Haikuに詳細ページの内容を渡して一言コメントを生成します。

### プロンプト設計

```
const prompt = `あなたは中古車の目利きです。以下の車両情報を見て、購入検討者が最も気にすべきポイントを1〜2点、1文で指摘してください。

## 車両データ
車名: ${title}
価格: ${price}万円
走行距離: ${mileage}万km
年式: ${year}年
車検: ${inspection}
修復歴: ${repair}
色: ${color}
ミッション: ${transmission}

## 市場データ
中央値: ${stats.medianPrice}万円
走行距離中央値: ${stats.medianMileage}万km
週間新着数: ${stats.weeklyNewCount}件

## 詳細ページ抜粋
${detailContent.slice(0, 1000)}

50文字以内、装飾なしのプレーンテキストで回答してください。`;
```

ポイントは：

1. **構造化データ＋詳細ページテキスト**の両方を渡す
2. \*\*市場データ（中央値・新着数）\*\*をコンテキストとして含める
3. **50文字以内**と制限して簡潔なコメントを強制する
4. max\_tokens=200で出力トークンも制限

### API呼び出し

```
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic();

async function getCarAIAnalysis(
  listing: Listing,
  detailContent: string,
  stats: MarketStats
): Promise<string> {
  // キャッシュチェック: 同じ物件の分析結果があれば再利用
  const cached = await getCachedComment(listing.external_id);
  if (cached) return cached;

  const message = await anthropic.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 200,
    messages: [{
      role: "user",
      content: buildPrompt(listing, detailContent, stats),
    }],
  });

  const comment = message.content[0].type === "text"
    ? message.content[0].text.trim()
    : "";

  // キャッシュ保存
  await saveComment(listing.external_id, comment);

  // レート制限: 1-2秒のランダム遅延
  await sleep(1000 + Math.random() * 1000);

  return comment;
}
```

### キャッシュ戦略

同じ車両が複数回通知に含まれる場合（価格変動で再検知など）、`properties`テーブルの`ai_comment`カラムにキャッシュします。

```
async function getCachedComment(externalId: string): Promise<string | null> {
  const { data } = await supabase
    .from("properties")
    .select("ai_comment")
    .eq("external_id", externalId)
    .not("ai_comment", "is", null)
    .limit(1)
    .single();

  return data?.ai_comment || null;
}
```

これにより**70-80%のAPI呼び出しをスキップ**できます。

## ステップ5：類似車両比較

直近のDBデータから似た条件の車両を探し、価格差を表示します。

```
function findSimilarCars(listing: Listing, recentCars: Property[]): string | null {
  const candidates = recentCars.filter(car => {
    if (car.maker !== listing.maker) return false;
    if (Math.abs(car.year - listing.year) > 5) return false;
    const mileageRatio = car.mileage_km / listing.mileage_km;
    if (mileageRatio < 0.5 || mileageRatio > 2.0) return false;
    return true;
  });

  // 類似度スコアで並び替え
  const scored = candidates.map(car => ({
    car,
    score: makerMatch(30) + yearSimilarity(20) + mileageProximity(20) + priceProximity(15),
  }));

  const best = scored.sort((a, b) => b.score - a.score)[0];
  if (!best) return null;

  const pctDiff = ((listing.price - best.car.price) / best.car.price * 100).toFixed(0);
  const direction = pctDiff > 0 ? "高い" : "安い";
  return `📊 類似車両が${daysAgo}日前に${best.car.price}万円で掲載（本車両は${Math.abs(pctDiff)}%${direction}）`;
}
```

AIを使わずDBだけで完結するので、コストゼロで相場感を提供できます。

## コスト実績

### なぜClaude Haikuか

| モデル | 入力単価 (1M tokens) | 出力単価 (1M tokens) | 品質 |
| --- | --- | --- | --- |
| Claude Haiku | $0.80 | $4.00 | 中古車分析には十分 |
| Claude Sonnet | $3.00 | $15.00 | オーバースペック |
| Claude Opus | $15.00 | $75.00 | 完全にオーバースペック |

中古車の一言コメント生成は、価格・走行距離・年式という**数値比較が中心**。高度な推論は不要で、Haikuで十分な品質が出ます。

### 月額コスト

```
1通知あたりの入力: ~500トークン
Top3のみAI分析: 3件/通知 × 500 = 1,500トークン
月間通知数: ~100通知
月間トークン: 150,000トークン

入力コスト: 0.15M × $0.80 = $0.12
出力コスト: 0.01M × $4.00 = $0.04
キャッシュヒット率70%を考慮: ($0.12 + $0.04) × 30% = $0.05

実質月額: 約$0.05（キャッシュ効果大）
```

上記はユーザー数が少ない現段階の数字です。ユーザーが増えても、URLが重複する（同じ車種を複数人が監視する）場合はキャッシュが効くので、コストは線形には増えません。

### コスト削減のポイント

1. **Top 3だけAI分析**: 全件ではなく上位3件のみClaude APIを呼ぶ
2. **キャッシュ**: 同じ`external_id`の分析結果をDB保存
3. **出力制限**: max\_tokens=200、「50文字以内」のプロンプト指示
4. **詳細テキスト制限**: 詳細ページの内容を1000文字に切り詰め
5. **構造化データ優先**: 自然言語の長文より、数値データを中心に渡す

## AIコメントの品質

実際に生成されたコメント例：

| 車両 | コメント |
| --- | --- |
| プリウス 185万円 修復歴あり 2.3万km | 修復歴ありだが走行2.3万kmで車検も長く、同条件比-16%は割安。内容次第で買い |
| RX-7 480万円 走行8.5万km | 走行8.5万kmはRX-7としては標準的。エンジン圧縮測定の確認を推奨 |
| ジムニー 198万円 2019年式 | 人気車種で値落ちしにくい。走行5万km以下なら相場通り |

車種の特性を踏まえたコメント（RX-7のロータリーエンジンの圧縮測定、ジムニーのリセールバリュー）が出るのは、Claudeの知識ベースが効いています。

## まとめ

| 処理 | 手法 | コスト |
| --- | --- | --- |
| 5段階スコア | ルールベース（相場比較） | $0 |
| メリット・デメリット | キーワードマッチ | $0 |
| 相場比較・類似車両 | DB集計 | $0 |
| AIコメント | Claude Haiku（Top3のみ） | ~$0.05/月 |

**9割をルールベースで処理し、AIは「一言の付加価値」に絞る**。これがコストを抑えつつ品質を保つ設計です。

全件AI分析すれば確かに品質は上がりますが、ユーザーが実際に見るのは上位数件です。「スコア5の物件だけAIコメント付き」というのは、コストと体験のバランスとして合理的な落とし所だと考えています。
