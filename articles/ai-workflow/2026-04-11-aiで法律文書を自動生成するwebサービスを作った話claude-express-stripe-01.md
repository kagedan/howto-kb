---
id: "2026-04-11-aiで法律文書を自動生成するwebサービスを作った話claude-express-stripe-01"
title: "AIで法律文書を自動生成するWebサービスを作った話（Claude + Express + Stripe）"
url: "https://qiita.com/Mildsolt2914491/items/fb1aa7ddbcfd4a098a67"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

# AIで法律文書を自動生成するWebサービスを作った話（Claude + Express + Stripe）

スタートアップや個人開発者が事業を始めるとき、必ずぶつかる問題があります。

**「契約書どうする？」**

弁護士に頼むと最低でも5〜20万円、時間もかかる。テンプレートをそのまま使うと抜けがある。かといって自分で0から書くのは無理。

この問題をAIで解決するWebサービスを作りました。

## 作ったもの

**AI法律文書作成サービス** → <https://legal.mildsolt.jp>

* NDA（秘密保持契約書）：¥30,000 即日
* SaaS利用規約：¥50,000 即日
* 業務委託契約書：¥40,000 即日
* プライバシーポリシー：¥30,000 即日

必要情報を入力 → Stripe決済 → Claude MAXが文書生成 → メールで即納品

## 技術スタック

```
バックエンド: Node.js / Express
DB: SQLite (better-sqlite3)
AI生成: Claude MAX (claude-haiku-4-5-20251001)
決済: Stripe Checkout
メール: Postfix + Nodemailer
インフラ: VPS + Caddy (HTTPS自動)
```

## アーキテクチャ

```
ユーザー
  ↓ (HTTPS)
legal.mildsolt.jp (Caddy reverse proxy)
  ↓
Express server (port 3458)
  ↓
Stripe Checkout Session作成
  ↓ (ユーザーがStripeで決済)
Stripe Webhook → /api/webhook/stripe
  ↓
setImmediate（非同期）
  ├─ Claude CLI で文書生成
  └─ Nodemailer でメール送信
```

## Claude CLIでの文書生成

Claude MAX PLANを使うことでAPI課金なし（月定額）で生成できます。

```
function generateDocument(docType, params) {
  const type = DOC_TYPES[docType];
  const prompt = `以下の情報を使って、${type.name}を日本語で作成してください...`;

  // stdin経由でプロンプトを渡す（シェルエスケープ問題を回避）
  const fs = require("fs");
  const tmpFile = `/tmp/legal_prompt_${Date.now()}.txt`;
  fs.writeFileSync(tmpFile, prompt);

  const result = execSync(
    `claude --print --model claude-haiku-4-5-20251001 < "${tmpFile}"`,
    { timeout: 120000 }
  );

  fs.unlinkSync(tmpFile);
  return result.toString().trim();
}
```

## Stripe Webhookの実装（重要ポイント）

```
// express.raw()をjsonミドルウェアより前に置く！
app.post("/api/webhook/stripe",
  express.raw({ type: "application/json" }),
  async (req, res) => {
    const sig = req.headers["stripe-signature"];
    const event = stripe.webhooks.constructEvent(
      req.body, sig, process.env.STRIPE_WEBHOOK_SECRET
    );

    if (event.type === "checkout.session.completed") {
      const orderId = event.data.object.metadata.order_id;
      // 非同期で文書生成・メール送信（レスポンスをブロックしない）
      setImmediate(async () => {
        const doc = generateDocument(order.doc_type, params);
        await sendDocument(order, doc);
        db.prepare("UPDATE orders SET status = 'delivered' WHERE id = ?").run(orderId);
      });
    }

    res.json({ received: true });
  }
);
```

`express.raw()`をjsonミドルウェアより前に置かないとWebhook署名検証が失敗します。ここは必ずハマるポイント。

## SQLiteで軽量な注文管理

```
db.exec(`
  CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    doc_type TEXT NOT NULL,
    client_email TEXT NOT NULL,
    params TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);
```

ステータス遷移: `pending` → `paid` → `delivered`

## 工夫した点

### 1. プロンプトに法的条件を明示する

```
要件:
1. 法的に有効な形式で作成
2. 東京地方裁判所を管轄とする
3. 日本法準拠
4. 全条項を網羅
5. 署名欄を含む
```

この条件を入れるだけで生成品質が大幅に向上します。

### 2. 非同期生成でUXを損なわない

Stripeの成功URLにリダイレクト後、バックグラウンドで生成・送信。  
ユーザーは即座に完了画面を見られます。

### 3. Caddy で SSL を自動化

```
legal.mildsolt.jp {
    reverse_proxy localhost:3458 {
        header_up X-Real-IP {remote_host}
    }
}
```

Let's Encrypt の証明書取得・更新が完全自動。

## 現在の課題

* 弁護士監修の明示（現在は「AI生成」と注記）
* 英語版対応（外国人起業家向け）
* 契約書レビュー機能（既存文書のチェック）

---

スタートアップや個人開発者の皆さん、法律文書でつまずかないよう使っていただければ嬉しいです。
