---
id: "2026-04-04-claude-code解析anthropic-conway完全実装ガイド-常時稼働aiエージェントを-01"
title: "【Claude Code解析】Anthropic Conway完全実装ガイド - 常時稼働AIエージェントを作ってみた"
url: "https://qiita.com/kenji_harada/items/76e1ccd0a1cd14ea1a7f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "TypeScript", "qiita"]
date_published: "2026-04-04"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/anthropic-conway-persistent-agent-guide))の要約版です

## はじめに🚀 リーク情報から判明したConwayの全貌

2026年3月31日、Claude Codeのnpmパッケージから59.8MBのソースマップがリークし、Anthropicの隠しプロジェクト「**Conway**」が発覚しました。

従来のAIは「呼び出し待ち」でしたが、Conwayは**24時間365日稼働し続ける自律エージェント**です。メール受信、GitHub更新、Slack通知など外部イベントに自動反応し、人間が寝ている間も作業を継続します。

僕自身、同様のシステムを手作りで構築・運用しているので、実装者の視点からConwayの仕組みを解説し、実際に動かせる常時稼働エージェントを作ってみます。

## Conway の3つのコアエリア

リーク情報から判明したConwayの構成：

### 1. Search エリア

```
// 実験的なホットキー機能
interface ConwaySearch {
  hotkeys: boolean;
  webAccess: boolean;
  autonomousGathering: boolean;
}
```

### 2. Chat エリア

```
// Conway専用チャット（通常のClaudeとは別インスタンス）
interface ConwayChat {
  persistentContext: boolean;
  webhookIntegration: boolean;
  extensionSupport: boolean;
}
```

### 3. System エリア

```
interface ConwaySystem {
  extensions: ExtensionManager;
  connectors: ConnectorManager;
  webhooks: WebhookManager;
}
```

## 最重要機能：Webhook駆動エージェント

Conwayの革新的な点は、外部イベントでエージェントが自動起動することです：

```
// Webhook URL設定例
const conwayWebhook = {
  url: "https://conway.anthropic.com/webhook/{userId}",
  services: {
    github: true,     // PR作成時に自動レビュー
    slack: true,      // @メンション時に自動応答
    email: true,      // 重要メール受信時に自動分析
    calendar: false   // スケジュール変更通知（オフ）
  }
}
```

## 実際にConway風システムを作ってみた

### 1. 基本構成

```
# プロジェクト構成
mkdir conway-clone
cd conway-clone

# 必要パッケージ
npm init -y
npm install @anthropic-ai/sdk express webhook-signature-verification
npm install @modelcontextprotocol/server cron
```

### 2. 常時稼働デーモン（KAIROS相当）

```
// daemon.js - 常時稼働エンジン
const Anthropic = require('@anthropic-ai/sdk');
const cron = require('cron');

class ConwayDaemon {
  constructor(apiKey) {
    this.anthropic = new Anthropic({ apiKey });
    this.memory = new Map(); // セッション間永続メモリ
    this.isActive = false;
  }

  // 15秒間隔のハートビート（リーク情報通り）
  startHeartbeat() {
    this.heartbeatJob = new cron.CronJob('*/15 * * * * *', async () => {
      if (this.isActive) return; // ブロッキングバジェット
      
      this.isActive = true;
      await this.checkTasks();
      this.isActive = false;
    });
    
    this.heartbeatJob.start();
    console.log('💓 Conway daemon started - heartbeat every 15s');
  }

  async checkTasks() {
    const prompt = `
現在時刻: ${new Date().toISOString()}
メモリ: ${JSON.stringify(Object.fromEntries(this.memory))}

今やるべきタスクはありますか？実行する場合は具体的なアクションを返してください。
何もない場合は "IDLE" と返してください。
`;

    try {
      const response = await this.anthropic.messages.create({
        model: "claude-3-sonnet-20240229",
        max_tokens: 1000,
        messages: [{ role: "user", content: prompt }]
      });

      const action = response.content[0].text;
      if (action !== "IDLE") {
        console.log('🔥 Auto-action:', action);
        await this.executeAction(action);
      }
    } catch (error) {
      console.error('❌ Heartbeat error:', error.message);
    }
  }

  async executeAction(action) {
    // ここで実際のタスク実行
    // GitHub API操作、メール送信、ファイル生成など
    this.memory.set('lastAction', {
      action,
      timestamp: new Date().toISOString()
    });
  }
}

// 起動
const daemon = new ConwayDaemon(process.env.ANTHROPIC_API_KEY);
daemon.startHeartbeat();
```

### 3. Webhook受信サーバー

```
// webhook-server.js
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

// Conway風Webhook受信
app.post('/webhook/:service', async (req, res) => {
  const service = req.params.service;
  const payload = req.body;
  
  console.log(`📨 Webhook from ${service}:`, payload);
  
  // サービス別処理
  switch(service) {
    case 'github':
      await handleGitHubEvent(payload);
      break;
    case 'slack':
      await handleSlackEvent(payload);
      break;
    default:
      console.log('❓ Unknown service:', service);
  }
  
  res.json({ status: 'processed' });
});

async function handleGitHubEvent(payload) {
  if (payload.action === 'opened' && payload.pull_request) {
    // PR作成時の自動レビュー
    const prUrl = payload.pull_request.html_url;
    const prTitle = payload.pull_request.title;
    
    console.log(`🔍 Auto-reviewing PR: ${prTitle}`);
    
    // Claude にレビュー依頼
    // 実装省略...
  }
}

async function handleSlackEvent(payload) {
  if (payload.event && payload.event.text && payload.event.text.includes('<@CONWAY>')) {
    // @Conway メンション時の自動応答
    console.log('💬 Slack mention detected');
    
    // 自動応答処理
    // 実装省略...
  }
}

app.listen(3000, () => {
  console.log('🎯 Conway webhook server running on port 3000');
});
```

### 4. メモリ統合システム（autoDream相当）

```
// memory-integration.js - 深夜の記憶統合
const cron = require('cron');

class MemoryIntegrator {
  constructor(daemon) {
    this.daemon = daemon;
    this.setupNightlyIntegration();
  }

  setupNightlyIntegration() {
    // 毎晩3時にメモリ統合（autoDream相当）
    const nightlyJob = new cron.CronJob('0 3 * * *', async () => {
      console.log('🌙 Starting nightly memory integration...');
      await this.integrateMemories();
    });

    nightlyJob.start();
  }

  async integrateMemories() {
    const memories = Array.from(this.daemon.memory.entries());
    
    const integrationPrompt = `
過去24時間のメモリ:
${memories.map(([key, value]) => `${key}: ${JSON.stringify(value)}`).join('\n')}

重要な学習事項や改善点を統合してください。新しいメモリ構造を提案してください。
`;

    try {
      const response = await this.daemon.anthropic.messages.create({
        model: "claude-3-sonnet-20240229",
        max_tokens: 2000,
        messages: [{ role: "user", content: integrationPrompt }]
      });

      // 統合結果をメモリに反映
      const integration = response.content[0].text;
      this.daemon.memory.set('integrated_memory', {
        content: integration,
        timestamp: new Date().toISOString()
      });

      console.log('✨ Memory integration complete');
    } catch (error) {
      console.error('❌ Memory integration failed:', error.message);
    }
  }
}

module.exports = MemoryIntegrator;
```

## Conway式Extensions（.cnw.zip相当）の実装

```
// extension-manager.js
class ExtensionManager {
  constructor() {
    this.extensions = new Map();
    this.tools = new Map();
  }

  // Conway風拡張機能ローダー
  async loadExtension(extensionPath) {
    try {
      const extension = require(extensionPath);
      
      // .cnw.zip相当の構造
      if (extension.tools) {
        extension.tools.forEach(tool => {
          this.tools.set(tool.name, tool);
        });
      }

      if (extension.uiTabs) {
        // UI拡張の処理
      }

      if (extension.contextHandlers) {
        // コンテキストハンドラーの登録
      }

      this.extensions.set(extension.name, extension);
      console.log(`📦 Extension loaded: ${extension.name}`);
    } catch (error) {
      console.error('❌ Extension load failed:', error.message);
    }
  }

  // ツール実行
  async executeTool(toolName, params) {
    const tool = this.tools.get(toolName);
    if (!tool) {
      throw new Error(`Tool not found: ${toolName}`);
    }

    return await tool.execute(params);
  }
}

// サンプル拡張
const sampleExtension = {
  name: "github-integration",
  version: "1.0.0",
  tools: [
    {
      name: "create_pr",
      description: "Create GitHub pull request",
      execute: async (params) => {
        // GitHub API実装
        console.log('Creating PR:', params);
        return { status: 'success', pr_url: 'https://github.com/...' };
      }
    }
  ],
  contextHandlers: [
    {
      type: "git_commit",
      handler: async (context) => {
        // Git コミット情報の処理
        return { processed: true };
      }
    }
  ]
};

module.exports = { ExtensionManager, sampleExtension };
```

## 全体起動スクリプト

```
// main.js - Conway Clone起動
const ConwayDaemon = require('./daemon');
const MemoryIntegrator = require('./memory-integration');
const { ExtensionManager, sampleExtension } = require('./extension-manager');

async function startConwayClone() {
  console.log('🚀 Starting Conway Clone...');

  // 1. デーモン起動
  const daemon = new ConwayDaemon(process.env.ANTHROPIC_API_KEY);
  daemon.startHeartbeat();

  // 2. メモリ統合システム
  new MemoryIntegrator(daemon);

  // 3. 拡張管理
  const extensionManager = new ExtensionManager();
  await extensionManager.loadExtension('./sample-extension');

  // 4. Webhookサーバー（別プロセスで起動）
  require('./webhook-server');

  console.log('✅ Conway Clone fully operational!');
}

startConwayClone().catch(console.error);
```

## 実用的な活用例

### 1. 自動コードレビューBot

```
# GitHub Webhookの設定
curl -X POST https://api.github.com/repos/{owner}/{repo}/hooks \
  -H "Authorization: token {github_token}" \
  -d '{
    "name": "web",
    "active": true,
    "events": ["pull_request"],
    "config": {
      "url": "http://your-server.com/webhook/github",
      "content_type": "json"
    }
  }'
```

### 2. Slack統合

```
// Slack app設定でWebhook URLを指定
// Events API: http://your-server.com/webhook/slack
// Bot Token Scopesに chat:write を追加
```

## デバッグとモニタリング

```
// monitoring.js
class ConwayMonitor {
  constructor(daemon) {
    this.daemon = daemon;
    this.setupHealthCheck();
  }

  setupHealthCheck() {
    setInterval(() => {
      const memorySize = this.daemon.memory.size;
      const lastAction = this.daemon.memory.get('lastAction');
      
      console.log(`📊 Health Check:
        - Memory entries: ${memorySize}
        - Last action: ${lastAction ? lastAction.timestamp : 'None'}
        - Daemon active: ${this.daemon.isActive}
      `);
    }, 60000); // 1分間隔
  }
}
```

## 実装時の注意点

### 1. レート制限対策

```
// リクエスト制限管理
class RateLimiter {
  constructor(requestsPerMinute = 10) {
    this.requests = [];
    this.limit = requestsPerMinute;
  }

  async checkRate() {
    const now = Date.now();
    this.requests = this.requests.filter(time => now - time < 60000);
    
    if (this.requests.length >= this.limit) {
      const waitTime = 60000 - (now - this.requests[0]);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    this.requests.push(now);
  }
}
```

### 2. エラーハンドリング

```
// 堅牢なエラー処理
process.on('uncaughtException', (error) => {
  console.error('💥 Uncaught Exception:', error);
  // ログ出力、アラート送信など
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
});
```

## まとめ：Conway時代への準備

本記事では、リーク情報を基にConway風の常時稼働AIエージェントを実装しました。重要なポイント：

1. **ハートビートベースの自律動作**
2. **Webhook駆動のイベント処理**
3. **永続メモリと夜間統合**
4. **拡張可能なツールシステム**

Conwayの正式リリースを待つ必要はありません。今すぐ同等のシステムを構築し、AI Agent時代の先行者利益を獲得しましょう。

詳細な実装手順はこちら → <https://nands.tech/posts/anthropic-conway-persistent-agent-guide>
