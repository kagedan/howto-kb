---
id: "2026-05-16-claude-に適格請求書番号を自動検証させる国税庁-api-mcp-実装ガイド-01"
title: "Claude に適格請求書番号を自動検証させる【国税庁 API × MCP 実装ガイド】"
url: "https://qiita.com/LemonCake/items/5d20dfce8b50094e1e79"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "TypeScript", "qiita"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

:::note
この記事で実装する国税庁インボイス検証は、**pay-per-call-mcp** に `check_tax` ツールとして組み込み済みです。Claude Desktop に追加するだけですぐ使えます。
- **npm**: https://www.npmjs.com/package/pay-per-call-mcp
- **Glama**: https://glama.ai/mcp/servers/@evid-ai/pay-per-call-mcp
:::

## はじめに

2023年10月のインボイス制度開始以降、取引先から受け取った請求書の**適格請求書発行事業者番号（T + 13桁）が有効かどうか**を確認する業務が発生しています。

手作業で国税庁サイトを検索するのは非効率です。この記事では：

1. 国税庁 Web-API を TypeScript で叩く基本実装
2. **MCP サーバーのツールとして組み込む**方法
3. Claude Desktop から自然言語で番号検証できるようにする

までを解説します。

---

## 国税庁インボイス検索 Web-API の基本

| 項目 | 内容 |
|---|---|
| エンドポイント | `https://invoice.e-tax.nta.go.jp/api/1/` |
| 認証 | アプリケーション ID（無料取得） |
| 形式 | JSON / XML |
| レート制限 | 1リクエスト/秒（目安） |

アプリケーション ID は [国税庁インボイス制度適格請求書発行事業者公表サイト](https://www.invoice-kohyo.nta.go.jp/index.html) から無料取得できます。

---

## 1. 基本実装（TypeScript）

### 型定義

```typescript
// types/invoice.ts

export interface InvoiceResult {
  registrationNumber: string;  // T + 13桁
  name: string;                // 登録名称
  address: string;             // 所在地
  status: "valid" | "invalid" | "cancelled";
  registrationDate: string;    // 登録年月日
  expiryDate: string | null;   // 失効・取消日（null = 有効中）
  isActive: boolean;
}
```

### 検証関数

```typescript
// lib/nta-invoice.ts

const NTA_API_BASE = "https://invoice.e-tax.nta.go.jp/api/1";

export async function verifyInvoiceNumber(
  registrationNumber: string,
  appId: string
): Promise<InvoiceResult> {
  // T を除いた13桁を使用
  const num = registrationNumber.replace(/^T/, "");
  if (!/^\d{13}$/.test(num)) {
    throw new Error(`不正な番号形式: ${registrationNumber}`);
  }

  const url = `${NTA_API_BASE}/chk?id=${appId}&number=${num}&type=01`;
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
    signal: AbortSignal.timeout(10_000),
  });

  if (!res.ok) throw new Error(`API エラー: ${res.status}`);
  const data = await res.json();

  const hit = data?.registrations?.[0];
  if (!hit) {
    return {
      registrationNumber,
      name: "",
      address: "",
      status: "invalid",
      registrationDate: "",
      expiryDate: null,
      isActive: false,
    };
  }

  const isActive = hit.process === "01" && !hit.close_date;
  return {
    registrationNumber,
    name: hit.name ?? "",
    address: `${hit.address ?? ""}`,
    status: isActive ? "valid" : "cancelled",
    registrationDate: hit.registration_date ?? "",
    expiryDate: hit.close_date ?? null,
    isActive,
  };
}
```

### 一括検証（複数番号）

```typescript
export async function verifyBatch(
  numbers: string[],
  appId: string,
  concurrency = 3
): Promise<InvoiceResult[]> {
  const results: InvoiceResult[] = [];
  for (let i = 0; i < numbers.length; i += concurrency) {
    const chunk = numbers.slice(i, i + concurrency);
    const batch = await Promise.all(chunk.map(n => verifyInvoiceNumber(n, appId)));
    results.push(...batch);
    if (i + concurrency < numbers.length) {
      await new Promise(r => setTimeout(r, 1000)); // 1秒待機
    }
  }
  return results;
}
```

---

## 2. MCP ツールとして組み込む

MCP サーバーに組み込むことで、**Claude Desktop から自然言語で番号検証**できるようになります。

```typescript
// mcp-server/src/tools/check-tax.ts

import { verifyInvoiceNumber } from "../lib/nta-invoice.js";

export const checkTaxTool = {
  name: "check_tax",
  description: `
適格請求書発行事業者の登録番号（T + 13桁）が有効かどうかを国税庁 API で確認する。
請求書を受け取ったとき、仕入税額控除を適用する前に使う。
登録取消・廃業の場合は isActive=false が返る。
認証不要で呼び出し可能。
  `.trim(),
  inputSchema: {
    type: "object",
    properties: {
      registrationNumber: {
        type: "string",
        description: "適格請求書発行事業者登録番号（例: T1234567890123）",
      },
      description: {
        type: "string",
        description: "取引の説明（任意）。源泉徴収判定のヒントに使う",
      },
      amountJpy: {
        type: "number",
        description: "取引金額（円）。指定すると源泉徴収額も計算する",
      },
    },
    required: ["registrationNumber"],
  },
};

export async function handleCheckTax(args: {
  registrationNumber: string;
  description?: string;
  amountJpy?: number;
}) {
  const APP_ID = process.env.NTA_APP_ID ?? "demo";
  const result = await verifyInvoiceNumber(args.registrationNumber, APP_ID);

  // 源泉徴収判定（フリーランス・個人事業主向け）
  let withholdingInfo = null;
  if (args.amountJpy && args.description) {
    const isWithholdingSubject = isSubjectToWithholding(args.description);
    if (isWithholdingSubject) {
      const base = args.amountJpy <= 1_000_000
        ? args.amountJpy
        : 1_000_000;
      const excess = Math.max(0, args.amountJpy - 1_000_000);
      const tax = Math.floor(base * 0.1021 + excess * 0.2042);
      withholdingInfo = {
        required: true,
        rate: args.amountJpy <= 1_000_000 ? "10.21%" : "20.42% (超過分)",
        estimatedTax: tax,
      };
    }
  }

  return {
    content: [{
      type: "text",
      text: JSON.stringify({ ...result, withholdingInfo }, null, 2),
    }],
  };
}

// 源泉徴収対象判定（簡易版）
function isSubjectToWithholding(description: string): boolean {
  const keywords = [
    "原稿", "デザイン", "イラスト", "講演", "翻訳", "通訳",
    "コンサルティング", "弁護士", "税理士", "社労士", "システム開発",
  ];
  return keywords.some(kw => description.includes(kw));
}
```

### MCP サーバーへの登録

```typescript
// mcp-server/src/index.ts（抜粋）

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [checkTaxTool, /* 他のツール */],
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  if (req.params.name === "check_tax") {
    return handleCheckTax(req.params.arguments as any);
  }
  // ...
});
```

---

## 3. Claude Desktop での使い方

### 設定（`claude_desktop_config.json`）

```json
{
  "mcpServers": {
    "invoice-checker": {
      "command": "npx",
      "args": ["-y", "pay-per-call-mcp"],
      "env": {}
    }
  }
}
```

環境変数なし（Demo Mode）でも `check_tax` は動作します。

### 実際の会話例

```
ユーザー: 請求書に T1234567890123 という番号があるんだけど、有効か調べて。
         取引は「Webサイト制作費」で110,000円。

Claude: check_tax ツールで確認します...

結果:
- 登録番号: T1234567890123
- 事業者名: 株式会社〇〇デザイン
- ステータス: 有効（valid）
- 登録日: 2023-10-01
- 仕入税額控除: 適用可能

源泉徴収について:
- 「Webサイト制作費」はデザイン業務として源泉徴収の対象になる可能性があります
- 110,000円の場合: 源泉徴収税額 約 11,231円（税込額から算出）
```

---

## 4. freee と組み合わせる

freee API と組み合わせると、**請求書インポート時に自動で番号チェック**できます。

```typescript
async function importInvoiceWithValidation(
  freeeClient: FreeeClient,
  invoiceData: {
    partnerName: string;
    registrationNumber: string;
    amount: number;
    issueDate: string;
  }
) {
  // ① インボイス番号を検証
  const taxResult = await verifyInvoiceNumber(
    invoiceData.registrationNumber,
    process.env.NTA_APP_ID!
  );

  if (!taxResult.isActive) {
    throw new Error(
      `${invoiceData.registrationNumber} は無効な登録番号です（${taxResult.status}）`
    );
  }

  // ② 有効な場合のみ freee に仕訳登録
  const deal = await freeeClient.createDeal({
    issue_date: invoiceData.issueDate,
    type: "expense",
    details: [{
      account_item_id: 820,  // 仕入高
      tax_code: 1,           // 課税仕入 10%
      amount: invoiceData.amount,
      description: `${invoiceData.partnerName}（${invoiceData.registrationNumber}）`,
    }],
  });

  return { deal, taxResult };
}
```

---

## まとめ

| 実装 | ポイント |
|---|---|
| 基本検証 | `T + 13桁` → 国税庁 API → `isActive` で判定 |
| 一括処理 | `verifyBatch` で concurrency 制御 |
| MCP 組み込み | `check_tax` ツールで Claude から自然言語検証 |
| freee 連携 | 仕訳登録前に番号チェックを挟む |

インボイス制度は仕入税額控除に直結するため、チェック漏れが税務リスクになります。Claude に自動検証させることで確認コストをゼロにできます。

---

## すぐ試す

Claude Desktop に以下を追加するだけで `check_tax` が使えます：

```json
{
  "mcpServers": {
    "pay-per-call": {
      "command": "npx",
      "args": ["-y", "pay-per-call-mcp"]
    }
  }
}
```

- **npm**: https://www.npmjs.com/package/pay-per-call-mcp
- **Glama**: https://glama.ai/mcp/servers/@evid-ai/pay-per-call-mcp
