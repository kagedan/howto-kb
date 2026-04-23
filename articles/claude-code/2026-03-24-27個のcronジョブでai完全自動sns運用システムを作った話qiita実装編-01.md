---
id: "2026-03-24-27個のcronジョブでai完全自動sns運用システムを作った話qiita実装編-01"
title: "27個のcronジョブでAI完全自動SNS運用システムを作った話【Qiita実装編】"
url: "https://qiita.com/kenji_harada/items/f846eab18f9cafa63d8d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "TypeScript", "qiita"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/ai-autonomous-sns-platform-full-architecture))の要約版です

## はじめに

「SNS更新、忘れがちなんですよね...」

そんな悩みを抱えるエンジニアは多いはず。自分も例外ではなく、技術的な知見はあるのに情報発信が継続できない日々が続いていました。

そこで思い切って**AIに全部任せる**システムを作ってみました。

1ヶ月間Claude Codeと向き合い、27個のcronジョブが24時間稼働する完全自動SNS運用基盤が完成。結果、**人間の作業時間は1日0分**になりました。

今回は実装のポイントとコード例を中心に紹介します。

## システム構成と技術スタック

まず全体像から。6層のアーキテクチャで構成されています：

```
// メインの処理フロー
export async function executeAutoPostFlow() {
  // 1. ソース収集
  const sources = await collectContentSources();
  
  // 2. コンテンツ生成
  const content = await generateContent(sources);
  
  // 3. AI Judge による品質チェック
  const judgment = await aiJudge.evaluate(content);
  
  // 4. 承認された場合のマルチプラットフォーム配信
  if (judgment.decision === 'approve') {
    await distributeToAllPlatforms(content);
  }
  
  // 5. 結果の学習・最適化
  await updateLearningModel(content, judgment);
}
```

技術スタック：

* **TypeScript + Next.js** (API Routes)
* **Supabase** (PostgreSQL + Storage)
* **GitHub Actions** (スケジュール実行)
* **Vercel** (ホスティング)
* **各種SNS API** (X, LinkedIn, Threads)

## 実装①: 自動ソース収集システム

### トレンド記事の収集

```
// Brave Search APIでAI関連記事を収集
export async function collectTrendingSources() {
  const searchQueries = [
    'AI breakthrough 2024',
    'machine learning news',
    'ChatGPT update',
    // 動的に拡張される
  ];
  
  const articles = [];
  
  for (const query of searchQueries) {
    const response = await braveSearch.search({
      q: query,
      count: 10,
      freshness: 'pd', // past day
    });
    
    // 記事の品質スコアリング
    const scored = response.web.results.map(article => ({
      ...article,
      relevanceScore: calculateRelevance(article),
      engagementPrediction: predictEngagement(article.title),
    }));
    
    articles.push(...scored);
  }
  
  // Supabaseに保存
  await supabase.from('trend_articles').upsert(articles);
  
  return articles.sort((a, b) => b.relevanceScore - a.relevanceScore);
}
```

### 関連度スコアリング

```
function calculateRelevance(article: Article): number {
  const keywords = ['AI', 'machine learning', 'LLM', 'automation'];
  const titleMatch = keywords.filter(k => 
    article.title.toLowerCase().includes(k.toLowerCase())
  ).length;
  
  const recencyBoost = getRecencyBoost(article.age);
  const sourceCredibility = getSourceCredibility(article.profile.name);
  
  return (titleMatch * 0.4 + recencyBoost * 0.3 + sourceCredibility * 0.3);
}
```

## 実装②: コンテンツ生成エンジン

### 6つの投稿モードの実装

```
enum ContentMode {
  ORIGINAL = 'original',
  THREAD = 'thread', 
  ARTICLE = 'article',
  QUOTE = 'quote',
  REPOST = 'repost',
  VIRAL_ARTICLE = 'viral_article'
}

export async function generateContent(sources: Article[]): Promise<GeneratedContent> {
  // パフォーマンス履歴に基づいてモード選択
  const selectedMode = await selectOptimalMode();
  
  switch (selectedMode) {
    case ContentMode.ORIGINAL:
      return await generateOriginalPost(sources[0]);
    case ContentMode.THREAD:
      return await generateThreadPost(sources[0]);
    case ContentMode.QUOTE:
      return await generateQuotePost(sources[0]);
    // 他のモードも同様
  }
}

async function generateOriginalPost(source: Article): Promise<GeneratedContent> {
  const prompt = `
技術系CEOの原田賢治として、以下の記事について投稿を作成してください：

記事: ${source.title}
要約: ${source.snippet}

要件：
- 280文字以内
- 専門的だが親しみやすいトーン
- エンゲージメントを促すフック
- 一人称は「自分」「僕」を使用
  `;
  
  const response = await claude.messages.create({
    model: "claude-3-5-sonnet-20241022",
    max_tokens: 1000,
    messages: [{ role: "user", content: prompt }]
  });
  
  return {
    mode: ContentMode.ORIGINAL,
    content: response.content[0].text,
    source: source,
    metadata: {
      generatedAt: new Date(),
      prompt: prompt
    }
  };
}
```

### Thompson Samplingによるパターン最適化

```
interface PatternStats {
  successes: number;
  failures: number;
  lastUsed: Date;
}

class ThompsonSampling {
  private patterns: Map<string, PatternStats> = new Map();
  
  async selectBestPattern(): Promise<string> {
    const samples = new Map<string, number>();
    
    // 各パターンでBeta分布からサンプリング
    for (const [pattern, stats] of this.patterns) {
      const decayedStats = this.applyDecay(stats);
      const sample = this.betaSample(
        decayedStats.successes + 1, 
        decayedStats.failures + 1
      );
      samples.set(pattern, sample);
    }
    
    // 最高スコアのパターンを選択
    return Array.from(samples.entries())
      .sort((a, b) => b[1] - a[1])[0][0];
  }
  
  private betaSample(alpha: number, beta: number): number {
    // Beta分布からのサンプリング実装
    const gamma1 = this.gammaSample(alpha);
    const gamma2 = this.gammaSample(beta);
    return gamma1 / (gamma1 + gamma2);
  }
  
  private applyDecay(stats: PatternStats): PatternStats {
    const daysSince = (Date.now() - stats.lastUsed.getTime()) / (1000 * 60 * 60 * 24);
    const decay = Math.pow(0.97, daysSince); // 半減期23日
    
    return {
      ...stats,
      successes: stats.successes * decay,
      failures: stats.failures * decay
    };
  }
}
```

## 実装③: AI Judge システム

### 4層品質チェック

```
export class AIJudge {
  async evaluate(content: GeneratedContent): Promise<JudgmentResult> {
    // L1: 事前安全チェック
    const safetyCheck = await this.preGenerationGuard();
    if (!safetyCheck.passed) {
      return { decision: 'reject', reason: safetyCheck.reason };
    }
    
    // L2: コンテンツ検証
    const validation = await this.validateContent(content);
    if (!validation.passed) {
      return { decision: 'reject', reason: validation.reason };
    }
    
    // L3: Claude判定
    const claudeJudgment = await this.claudeEvaluation(content);
    
    // L4: 動的しきい値調整
    const threshold = await this.calculateDynamicThreshold();
    
    const decision = claudeJudgment.totalScore >= threshold ? 'approve' : 'reject';
    
    return {
      decision,
      scores: claudeJudgment.scores,
      totalScore: claudeJudgment.totalScore,
      threshold,
      reason: claudeJudgment.reasoning
    };
  }
  
  private async claudeEvaluation(content: GeneratedContent) {
    const prompt = `
以下の投稿を5つの次元で0-10点で評価してください：

投稿内容: ${content.content}

評価次元：
1. hookStrength: フック文の魅力度
2. voiceAuthenticity: CEOらしい声か
3. engagementTrigger: エンゲージメント喚起力
4. platformFit: プラットフォーム適合性
5. factualGrounding: 事実的根拠

JSON形式で回答：
{
  "hookStrength": number,
  "voiceAuthenticity": number,
  "engagementTrigger": number,
  "platformFit": number,
  "factualGrounding": number,
  "reasoning": "判定理由"
}
    `;
    
    const response = await claude.messages.create({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 500,
      messages: [{ role: "user", content: prompt }]
    });
    
    const scores = JSON.parse(response.content[0].text);
    const totalScore = Object.values(scores)
      .filter(v => typeof v === 'number')
      .reduce((sum: number, score: number) => sum + score, 0) / 5;
    
    return { scores, totalScore, reasoning: scores.reasoning };
  }
  
  private async calculateDynamicThreshold(): Promise<number> {
    const hour = new Date().getHours();
    const todayPosts = await this.getTodayPostCount();
    
    let baseThreshold = 6.0;
    
    // 時間帯調整
    if (hour >= 6 && hour <= 9) baseThreshold -= 0.2; // 朝は少し緩く
    if (hour >= 18 && hour <= 22) baseThreshold += 0.3; // 夜は厳しく
    
    // 投稿数調整
    if (todayPosts >= 3) baseThreshold += 0.5; // 既に多く投稿済みなら厳しく
    
    return baseThreshold;
  }
}
```

## 実装④: マルチプラットフォーム配信

### X (Twitter) 投稿

```
export async function postToX(content: GeneratedContent): Promise<PostResult> {
  try {
    // 画像が必要な場合はGeminiで生成
    let mediaIds: string[] = [];
    if (content.requiresImage) {
      const imageBuffer = await generateThumbnail(content);
      const mediaUpload = await xClient.v1.uploadMedia(imageBuffer);
      mediaIds = [mediaUpload];
    }
    
    // 長文記事の場合は分割投稿
    if (content.mode === ContentMode.ARTICLE && content.content.length > 280) {
      return await this.postLongArticle(content);
    }
    
    // 通常投稿
    const tweet = await xClient.v2.tweet({
      text: content.content,
      media: mediaIds.length > 0 ? { media_ids: mediaIds } : undefined,
    });
    
    return { success: true, postId: tweet.data.id, platform: 'x' };
  } catch (error) {
    console.error('X投稿エラー:', error);
    return { success: false, error: error.message };
  }
}

private async postLongArticle(content: GeneratedContent) {
  // X記事機能を使用した長文投稿
  const articleData = {
    title: content.title,
    text: content.content,
    media: content.media ? [content.media] : undefined
  };
  
  const article = await xClient.v2.createArticle(articleData);
  
  // 記事へのリンクツイート
  const tweet = await xClient.v2.tweet({
    text: `新しい記事を書きました：${content.title}\n\n記事を読む ↓`,
    // 記事URLは自動で展開される
  });
  
  return { success: true, postId: tweet.data.id, articleId: article.data.id };
}
```

### LinkedIn自動投稿

```
export async function postToLinkedIn(content: GeneratedContent): Promise<PostResult> {
  // LinkedInはビジネスライクなトーンに自動調整
  const optimizedContent = await optimizeForLinkedIn(content.content);
  
  const postData = {
    author: process.env.LINKEDIN_PERSON_URN,
    lifecycleState: 'PUBLISHED',
    specificContent: {
      'com.linkedin.ugc.ShareContent': {
        shareCommentary: {
          text: optimizedContent
        },
        shareMediaCategory: 'NONE'
      }
    },
    visibility: {
      'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
    }
  };
  
  const response = await fetch('https://api.linkedin.com/v2/ugcPosts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.LINKEDIN_ACCESS_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(postData)
  });
  
  const result = await response.json();
  return { success: true, postId: result.id, platform: 'linkedin' };
}

async function optimizeForLinkedIn(content: string): Promise<string> {
  const prompt = `
以下のX投稿をLinkedIn向けに最適化してください：

元投稿: ${content}

要件：
- よりビジネスライクなトーン
- 専門性を強調
- ネットワーキング要素を追加
- 280文字制限なし（適度な長さに）
  `;
  
  const response = await claude.messages.create({
    model: "claude-3-5-sonnet-20241022",
    max_tokens: 800,
    messages: [{ role: "user", content: prompt }]
  });
  
  return response.content[0].text;
}
```

## 実装⑤: GitHub Actions設定

### メインの自動投稿ワークフロー

```
# .github/workflows/auto-post.yml
name: Auto SNS Post

on:
  schedule:
    # 平日: 7:00, 12:00, 18:00, 23:00 JST
    - cron: '0 22 * * 0-4'  # 7:00 JST
    - cron: '0 3 * * 1-5'   # 12:00 JST 
    - cron: '0 9 * * 1-5'   # 18:00 JST
    - cron: '0 14 * * 1-5'  # 23:00 JST
    
    # 週末: 10:00, 20:00 JST
    - cron: '0 1 * * 6,0'   # 10:00 JST
    - cron: '0 11 * * 6,0'  # 20:00 JST

jobs:
  auto-post:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - run: npm ci
    
    - name: Execute Auto Post
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        X_API_KEY: ${{ secrets.X_API_KEY }}
        LINKEDIN_TOKEN: ${{ secrets.LINKEDIN_TOKEN }}
        SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
      run: |
        node -e "
        const { executeAutoPost } = require('./dist/lib/auto-post');
        executeAutoPost().catch(console.error);
        "
```

### エラーハンドリングとアラート

```
export async function executeAutoPost() {
  try {
    const result = await executeAutoPostFlow();
    
    // 成功をSlackに通知
    await notifySlack({
      type: 'success',
      message: `✅ 自動投稿完了: ${result.platform} (${result.mode})`,
      details: {
        content: result.content.substring(0, 100) + '...',
        aiJudgeScore: result.judgment.totalScore,
        engagementPrediction: result.prediction
      }
    });
    
  } catch (error) {
    // エラーをSlackに通知
    await notifySlack({
      type: 'error',
      message: `❌ 自動投稿エラー: ${error.message}`,
      error: error.stack
    });
    
    // 連続エラーの場合は自動停止
    const errorCount = await incrementErrorCount();
    if (errorCount >= 5) {
      await emergencyStop('連続エラー検知による自動停止');
    }
  }
}
```

## データベース設計

### 投稿管理テーブル

```
-- 投稿履歴
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  content TEXT NOT NULL,
  mode VARCHAR(20) NOT NULL,
  platform VARCHAR(20) NOT NULL,
  post_id VARCHAR(100),
  ai_judge_score DECIMAL(3,2),
  engagement_prediction DECIMAL(3,2),
  actual_engagement DECIMAL(3,2),
  created_at TIMESTAMP DEFAULT NOW(),
  posted_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'pending'
);

-- AI Judge判定履歴
CREATE TABLE ai_judgments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID REFERENCES posts(id),
  hook_strength INTEGER,
  voice_authenticity INTEGER,
  engagement_trigger INTEGER,
  platform_fit INTEGER,
  factual_grounding INTEGER,
  total_score DECIMAL(3,2),
  threshold DECIMAL(3,2),
  decision VARCHAR(10),
  reasoning TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- パターン学習データ
CREATE TABLE pattern_performance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pattern_name VARCHAR(50) NOT NULL,
  successes INTEGER DEFAULT 0,
  failures INTEGER DEFAULT 0,
  last_used TIMESTAMP DEFAULT NOW(),
  avg_engagement DECIMAL(4,3),
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 監視とアラート

### Slack統合

```
export async function notifySlack(notification: SlackNotification) {
  const webhook = process.env.SLACK_WEBHOOK_URL;
  
  const payload = {
    text: notification.message,
    attachments: [{
      color: notification.type === 'error' ? 'danger' : 'good',
      fields: [
        {
          title: '詳細',
          value: JSON.stringify(notification.details, null, 2),
          short: false
        }
      ],
      footer: 'AI SNS System',
      ts: Math.floor(Date.now() / 1000)
    }]
  };
  
  await fetch(webhook, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

// 緊急停止機能
export async function emergencyStop(reason: string) {
  // 全自動投稿を停止
  await supabase
    .from('system_settings')
    .update({ auto_post_enabled: false, stop_reason: reason })
    .eq('id', 1);
  
  // 緊急アラート
  await notifySlack({
    type: 'critical',
    message: `🚨 緊急停止: ${reason}`,
    details: { timestamp: new Date().toISOString() }
  });
}
```

## パフォーマンス実績

1ヶ月運用した結果の数字：

```
// 統計データ取得
const stats = await supabase.rpc('get_performance_stats');

/* 結果:
{
  total_posts: 106,
  ai_judge_executions: 146,
  approval_rate: 0.73,
  avg_engagement_improvement: 0.24,
  automation_rate: 1.0,  // 100%自動
  platforms: ['x', 'linkedin', 'threads', 'zenn', 'qiita'],
  cron_jobs: 27,
  uptime: 0.998  // 99.8%稼働
}
*/
```

## 学んだこと・改善点

### Claude Codeの威力

正直、全部一人で書くのは無理でした。Claude Codeがあったからこそ実現できたプロジェクト。

特に複雑な状態管理やエラーハンドリング周りは、人間が書くより確実で堅牢なコードを生成してくれました。

### AIシステムのデバッグは独特

従来のバグと違い、「なぜこの判定になったのか」が見えにくい。

そのため全ての判定に`reasoning`フィールドを設け、AIの思考プロセスを記録するようにしました。

### 学習データの質が全て

パターン最適化は、エンゲージメントデータの質に完全依存。

初期は人力で「良い投稿」「悪い投稿」をラベリングし、最低限の教師データを作ることが重要でした。

## まとめ

27個のcronジョブで回る完全自動SNS運用システム、想像以上に複雑でしたが想像以上に効果的でした。

特に面白いのは、**AIがAIを判定する**部分。AI Judgeが生成コンテンツの27%を却下し、品質を保っています。

人間は「方針を決める」だけ。あとは全部システムが考えて実行する。

これが2024年のSNS運用の形かもしれません。

---

詳細な実装手順はこちら → <https://nands.tech/posts/ai-autonomous-sns-platform-full-architecture>
