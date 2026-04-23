---
id: "2026-04-11-stripe-webhook-claude-cli-で法律文書を自動生成した話nodejs-sqli-01"
title: "Stripe Webhook × Claude CLI で法律文書を自動生成した話（Node.js + SQLite）"
url: "https://qiita.com/Mildsolt2914491/items/e705e8da8eaf7808d3e6"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## 1. はじめに

契約書や利用規約などの法律文書って、テンプレートから何度も同じことを書き直したり、細かい表現を調整したりと、かなりの手作業がかかります。

数ヶ月前、「このプロセスを自動化できたら、もっと効率的に運用できるのでは？」と考え始めました。そこで目をつけたのが **Stripe Webhook** と **Claude CLI** の組み合わせです。

* **Stripe Webhook**: 支払い成功時などのイベントをリアルタイムに検知
* **Claude CLI**: AIに法律文書の生成タスクを委譲

この2つを組み合わせることで、顧客の支払い完了→自動的に法律文書生成という、**完全自動化のパイプライン**を実現できました。

## 2. システム概要（アーキテクチャ）

全体の流れは以下の通りです：

```
Stripe Payment Event
        ↓
    Webhook受信 (Express)
        ↓
   署名検証 (重要!)
        ↓
   Claude CLIに処理を委譲
        ↓
   生成ログをSQLiteに保存
        ↓
   (200 OK をすぐ返す)
        ↓
   並列で文書生成処理が進む
```

ポイントは、Webhookレスポンスをなるべく**早く返す**こと。生成処理が時間がかかるので、同期的に待つと タイムアウトしてしまいます。

## 3. Stripe Webhookの設定と express.raw() の重要性

Stripe Webhookの署名検証には、**生のリクエストボディ（バイナリ形式）** が必要です。これが重要なポイント。

```
const express = require('express');
const app = express();

// ⚠️ 重要: express.json() よりも前に express.raw() を置く
app.post('/webhook', 
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const sig = req.headers['stripe-signature'];
    const body = req.body; // Buffer形式

    try {
      // Stripe署名検証
      const event = stripe.webhooks.constructEvent(
        body,           // バイナリデータが必須
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );

      // イベント処理
      if (event.type === 'payment_intent.succeeded') {
        await handlePaymentSuccess(event.data.object);
      }

      res.json({ received: true });
    } catch (err) {
      res.status(400).send(`Webhook Error: ${err.message}`);
    }
  }
);
```

**なぜ express.json() を後に置くのか？**

* `express.json()` はリクエストボディを **JSON文字列として解析** してしまう
* その過程で元のバイナリデータが失われる
* Stripe署名検証には、改変されていない元のバイナリが必要

順序を逆にすると、署名検証が失敗してしまい、セキュリティホールになります。

## 4. tmpfileでstdinにプロンプトを渡す方法

Claude CLIを呼び出すときに、長めのプロンプトを渡す必要があります。シェルのコマンドライン引数だと制限があるため、**一時ファイル経由で stdin** に渡すのが確実です。

```
const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

async function generateLegalDocument(customerData) {
  // プロンプトを組み立てる
  const prompt = `
顧客情報に基づいて、契約書を生成してください。

【顧客情報】
- 企業名: ${customerData.company}
- 業種: ${customerData.industry}
- 契約期間: ${customerData.term}

【要件】
- 日本の法律に準拠した形式
- 専門用語は分かりやすく説明
- A4サイズで印刷可能な長さ

契約書本文を Markdown 形式で出力してください。
  `.trim();

  // 一時ファイルを作成
  const tmpDir = os.tmpdir();
  const tmpFile = path.join(tmpDir, `prompt_${Date.now()}.txt`);
  
  try {
    // プロンプトを一時ファイルに書き込み
    fs.writeFileSync(tmpFile, prompt, 'utf-8');

    // stdin経由でClaudeに渡す
    const command = `cat "${tmpFile}" | claude conversation`;
    const result = execSync(command, { 
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024 // 10MBバッファ
    });

    return result;
  } finally {
    // 一時ファイルを削除
    fs.unlinkSync(tmpFile);
  }
}
```

**tmpfile経由のメリット：**

* 長いプロンプトを制限なく渡せる
* 改行や特殊文字の扱いが簡単
* ClaudeのCLIが標準入力を読むので自然

## 5. setImmediate()でWebhookレスポンスを先に返す

Webhook処理を素早く完了させるため、生成処理を非同期で実行します。

```
app.post('/webhook', 
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const sig = req.headers['stripe-signature'];
    
    try {
      const event = stripe.webhooks.constructEvent(
        req.body,
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );

      // ✅ ここで即座に200を返す
      res.json({ received: true });

      // ✅ 以降の処理は非同期で実行（レスポンス送信後）
      setImmediate(async () => {
        try {
          if (event.type === 'payment_intent.succeeded') {
            const payment = event.data.object;
            const document = await generateLegalDocument({
              customerId: payment.customer,
              amount: payment.amount,
            });
            
            // ログを記録（次項参照）
            await logGeneration(payment.customer, document);
          }
        } catch (err) {
          console.error('Background task error:', err);
          // アラート送信など
        }
      });

    } catch (err) {
      res.status(400).send(`Webhook Error: ${err.message}`);
    }
  }
);
```

**setImmediate() のメリット：**

* Webhookの応答が即座に返される（Stripeは通常2秒でタイムアウト）
* イベントループの次のターンで処理が実行される
* メインのリクエスト処理をブロックしない

## 6. SQLiteで生成ログを管理

生成された文書の履歴を管理するため、SQLiteを使用します。

```
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./documents.db');

// テーブル初期化
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS document_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      customer_id TEXT NOT NULL,
      generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      document_content TEXT,
      status TEXT DEFAULT 'success',
      error_message TEXT
    )
  `);
});

async function logGeneration(customerId, documentContent) {
  return new Promise((resolve, reject) => {
    db.run(
      `INSERT INTO document_logs (customer_id, document_content, status) 
       VALUES (?, ?, 'success')`,
      [customerId, documentContent],
      function(err) {
        if (err) reject(err);
        else resolve(this.lastID);
      }
    );
  });
}

async function getCustomerDocuments(customerId) {
  return new Promise((resolve, reject) => {
    db.all(
      `SELECT * FROM document_logs WHERE customer_id = ? ORDER BY generated_at DESC`,
      [customerId],
      (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      }
    );
  });
}
```

SQLiteの利点：

* セットアップが簡単（外部DBサーバー不要）
* Node.jsアプリケーションと同じプロセスで動作
* クエリが高速

## 7. 実際のコードスニペット（完全版）

ここまでを統合した、実用的な完全コードです：

```
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const sqlite3 = require('sqlite3').verbose();
const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const app = express();
const db = new sqlite3.Database('./documents.db');

// DB初期化
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS document_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      customer_id TEXT NOT NULL,
      document_type TEXT,
      generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      document_content TEXT,
      status TEXT DEFAULT 'success',
      error_message TEXT
    )
  `);
});

// Webhook エンドポイント
app.post('/webhook',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const sig = req.headers['stripe-signature'];
    
    try {
      const event = stripe.webhooks.constructEvent(
        req.body,
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );

      // 即座にレスポンスを返す
      res.json({ received: true });

      // バックグラウンド処理
      setImmediate(async () => {
        try {
          if (event.type === 'payment_intent.succeeded') {
            const payment = event.data.object;
            const customerId = payment.customer;

            // 顧客情報を取得（実装省略）
            const customerData = await getCustomerData(customerId);

            // 法律文書を生成
            const document = await generateDocumentWithClaude(customerData);

            // ログに保存
            await logGeneration(customerId, 'contract', document);
          }
        } catch (err) {
          console.error('Background processing error:', err);
        }
      });

    } catch (err) {
      res.status(400).send(`Webhook Error: ${err.message}`);
    }
  }
);

// Claude CLIで文書生成
async function generateDocumentWithClaude(customerData) {
  const prompt = `
以下の顧客情報に基づいて、日本の法律に準拠した契約書を生成してください。

【顧客情報】
企業名: ${customerData.company}
業種: ${customerData.industry}
契約期間: ${customerData.term}月

【出力形式】
- Markdown形式
- A4で印刷可能な長さ
- 法的に有効な表現

契約書本文を出力してください。
  `.trim();

  const tmpFile = path.join(os.tmpdir(), `prompt_${Date.now()}.txt`);
  
  try {
    fs.writeFileSync(tmpFile, prompt, 'utf-8');
    const command = `cat "${tmpFile}" | claude conversation`;
    const result = execSync(command, { 
      encoding: 'utf-8',
      maxBuffer: 20 * 1024 * 1024
    });
    return result;
  } finally {
    fs.unlinkSync(tmpFile);
  }
}

// DB操作
function logGeneration(customerId, docType, content) {
  return new Promise((resolve, reject) => {
    db.run(
      `INSERT INTO document_logs (customer_id, document_type, document_content) 
       VALUES (?, ?, ?)`,
      [customerId, docType, content],
      function(err) {
        if (err) reject(err);
        else resolve(this.lastID);
      }
    );
  });
}

async function getCustomerData(customerId) {
  // Stripe APIから顧客情報を取得
  const customer = await stripe.customers.retrieve(customerId);
  return {
    company: customer.description,
    industry: 'SaaS',  // 実装では動的に取得
    term: 12,
  };
}

// サーバー起動
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Webhook server running on port ${PORT}`);
});
```

## 8. まとめ

Stripe Webhook + Claude CLI + SQLite という組み合わせにより、以下を実現できました：

| 項目 | 効果 |
| --- | --- |
| **自動化度** | 支払い完了→文書生成が完全自動 |
| **応答性** | Webhookが2秒以内に完了 |
| **スケーラビリティ** | SQLiteで小〜中規模のログ管理が可能 |
| **実装の簡潔さ** | Express + Node.js標準APIで実装可能 |

特に重要なポイント：

* ✅ `express.raw()` を `express.json()` より前に配置すること
* ✅ `setImmediate()` で非同期化すること
* ✅ tmpfile経由でプロンプトを渡すこと

これらを押さえることで、安定した自動文書生成パイプラインが構築できます。

## 9. 最後に

このシステムを実装したサービスを **<https://legal.mildsolt.jp>** で公開中です。

実際に契約書や利用規約の生成をお試しいただけます。フィードバックやご質問があれば、ぜひお気軽にお寄せください！

---

**参考リンク：**
