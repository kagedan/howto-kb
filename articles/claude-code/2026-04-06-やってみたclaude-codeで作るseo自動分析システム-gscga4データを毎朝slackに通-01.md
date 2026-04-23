---
id: "2026-04-06-やってみたclaude-codeで作るseo自動分析システム-gscga4データを毎朝slackに通-01"
title: "【やってみた】Claude Codeで作るSEO自動分析システム - GSC×GA4データを毎朝Slackに通知"
url: "https://qiita.com/kenji_harada/items/ce01ef8185b48da92013"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-06"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/claude-code-gsc-ga4-ai-seo-autonomous-analysis-406853))の要約版です

## はじめに

毎朝GSCを開いてパフォーマンスをチェックし、GA4で記事の直帰率を確認する...この作業、自分も毎週やっていましたが、100記事を超えるとさすがに限界でした。

そこでClaude Codeを使って、GSCとGA4のデータを自動取得し、全記事をAIがスコアリングして改善すべき記事をSlackに通知してくれるシステムを作ってみました。

結果：**月間4,000表示でCTR 0.02%の記事**をAIが発見し、手動では見落としていた致命的なボトルネックを検出できました。

## システム構成

**技術スタック：**

* データ取得：`googleapis`（GSC）、`@google-analytics/data`（GA4）
* ストレージ：Supabase
* 実行環境：GitHub Actions
* 通知：Slack Bot API

## 実装手順

### 1. Google Cloud Console設定

GSC API用のOAuth2認証とGA4 API用のサービスアカウントを設定します。

```
// GSC API設定
const auth = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  'urn:ietf:wg:oauth:2.0:oob'
);

auth.setCredentials({
  refresh_token: process.env.GOOGLE_REFRESH_TOKEN
});

const searchconsole = google.searchconsole({ version: 'v1', auth });
```

```
// GA4 API設定
import { BetaAnalyticsDataClient } from '@google-analytics/data';

const analyticsDataClient = new BetaAnalyticsDataClient({
  keyFilename: 'service-account.json'
});
```

### 2. GSCデータ取得

```
async function fetchGSCData() {
  const response = await searchconsole.searchanalytics.query({
    siteUrl: 'https://nands.tech/',
    requestBody: {
      startDate: '2024-01-01',
      endDate: '2024-01-31',
      dimensions: ['page', 'query'],
      searchType: 'web',
      aggregationType: 'byPage'
    }
  });
  
  return response.data.rows;
}
```

### 3. GA4データ取得

```
async function fetchGA4Data() {
  const [response] = await analyticsDataClient.runReport({
    property: `properties/${GA4_PROPERTY_ID}`,
    dateRanges: [{ startDate: '30daysAgo', endDate: 'today' }],
    dimensions: [{ name: 'pagePath' }],
    metrics: [
      { name: 'sessions' },
      { name: 'bounceRate' },
      { name: 'averageSessionDuration' },
      { name: 'scrolledUsers' }
    ]
  });
  
  return response.rows;
}
```

## スコアリングアルゴリズム

Claude Codeで実装したスコアリングロジックです。3つの軸で評価します。

```
function calculateArticleScore(gscData, ga4Data) {
  // SEOスコア（40%）
  const seoScore = calculateSEOScore({
    ctr: gscData.ctr,
    position: gscData.avgPosition,
    impressions: gscData.impressions,
    queryCount: gscData.queries.length
  });
  
  // エンゲージメントスコア（40%）
  const engagementScore = calculateEngagementScore({
    bounceRate: ga4Data.bounceRate,
    avgDuration: ga4Data.avgSessionDuration,
    scrollDepth: ga4Data.scrolledUsers / ga4Data.sessions
  });
  
  // コンバージョンスコア（20%）
  const conversionScore = calculateConversionScore({
    conversionRate: ga4Data.conversionRate,
    eventDensity: ga4Data.events / ga4Data.sessions
  });
  
  return {
    overall: seoScore * 0.4 + engagementScore * 0.4 + conversionScore * 0.2,
    seo: seoScore,
    engagement: engagementScore,
    conversion: conversionScore
  };
}
```

### SEOスコアの計算

```
function calculateSEOScore(data) {
  // 期待CTRを順位から計算
  const expectedCTR = getExpectedCTR(data.position);
  const ctrRatio = (data.ctr / expectedCTR) * 100;
  
  // 順位スコア（1位=100pt, 10位=50pt）
  const positionScore = Math.max(0, 110 - data.position * 10);
  
  // 表示回数スコア（対数スケール）
  const impressionScore = Math.min(100, Math.log10(data.impressions + 1) * 25);
  
  return (ctrRatio * 0.3 + positionScore * 0.3 + 
          impressionScore * 0.2 + data.queryCount * 2 * 0.2);
}

function getExpectedCTR(position) {
  const ctrCurve = {
    1: 0.30, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05,
    6: 0.04, 7: 0.03, 8: 0.025, 9: 0.02, 10: 0.015
  };
  return ctrCurve[Math.ceil(position)] || 0.01;
}
```

## Quick Wins検出

```
function detectQuickWins(articles) {
  return articles
    .filter(article => 
      article.avgPosition >= 4 && 
      article.avgPosition <= 15 && 
      article.impressions >= 100
    )
    .sort((a, b) => b.impressions - a.impressions)
    .slice(0, 20);
}

function detectLowCTR(articles) {
  return articles
    .filter(article => {
      const expectedCTR = getExpectedCTR(article.avgPosition);
      return article.ctr < expectedCTR * 0.3; // 期待値の30%未満
    })
    .sort((a, b) => b.impressions - a.impressions);
}
```

## Slack通知

```
async function sendSlackNotification(analysisResults) {
  const blocks = [
    {
      type: "header",
      text: { type: "plain_text", text: "📊 Daily SEO Report" }
    },
    {
      type: "section",
      text: { 
        type: "mrkdwn", 
        text: `*Quick Wins detected:* ${analysisResults.quickWins.length}`
      }
    }
  ];
  
  // Quick Winsの詳細を追加
  analysisResults.quickWins.forEach(article => {
    blocks.push({
      type: "section",
      text: {
        type: "mrkdwn",
        text: `🎯 *${article.title}*\n順位: ${article.avgPosition} | 表示: ${article.impressions}`
      }
    });
  });
  
  await fetch('https://slack.com/api/chat.postMessage', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${SLACK_BOT_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      channel: '#seo-alerts',
      blocks: blocks
    })
  });
}
```

## 実際の結果

111記事をスコアリングした結果：

| グレード | 記事数 | 改善ポイント |
| --- | --- | --- |
| A | 1記事 | 現状維持 |
| B | 10記事 | 微調整でS狙い |
| C | 28記事 | タイトル改善 |
| D | 72記事 | 抜本的リライト |

**最も衝撃的だった発見：**

* 「AIエージェントとは」記事：月間4,241表示、CTR 0.02%
* 期待CTR 1.5%に対して実際は0.02%
* タイトル改善だけで月間60-80クリック増加の可能性

## カスタマイズポイント

### 期待CTRカーブの調整

```
// サイトのジャンルに応じて調整
const techBlogCTRCurve = {
  1: 0.25,  // テック系は少し低め
  2: 0.12,
  3: 0.08,
  // ...
};

const ecommerceCTRCurve = {
  1: 0.35,  // ECは高め
  2: 0.18,
  3: 0.12,
  // ...
};
```

### スコア重み配分のカスタマイズ

```
// コンテンツ重視サイト
const contentSiteWeights = {
  seo: 0.3,
  engagement: 0.5,  // エンゲージメント重視
  conversion: 0.2
};

// EC/リード獲得サイト
const businessSiteWeights = {
  seo: 0.4,
  engagement: 0.2,
  conversion: 0.4   // コンバージョン重視
};
```

## 運用コストと効果

| 項目 | 従来（手動） | 自動化後 |
| --- | --- | --- |
| 週次分析時間 | 30分 | 0分 |
| 見落としリスク | 高 | ほぼゼロ |
| API使用料 | - | 無料枠内 |
| インフラ費用 | - | 無料（Supabase） |

## まとめ

Claude Codeを使ってGSC×GA4の自動分析システムを構築した結果、手動では見落としていた改善機会を21件検出できました。

特に月間4,000表示でCTR 0.02%という「見た目は悪くないが実は致命的」なボトルネックの発見は、手動分析では不可能だったでしょう。

毎朝Slackに届く分析レポートを見て「この記事のタイトルを直そう」と判断するだけで、SEO改善が継続的に進んでいきます。

詳細な実装手順はこちら → <https://nands.tech/posts/claude-code-gsc-ga4-ai-seo-autonomous-analysis-406853>
