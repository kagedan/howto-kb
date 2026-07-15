---
id: "2026-07-15-llm-api-gateway設計入門1つのapiキーで複数モデルを扱う-01"
title: "LLM API Gateway設計入門：1つのAPIキーで複数モデルを扱う"
url: "https://zenn.dev/flatkey_ai_jp/articles/1b826e61ec9ec6"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "Gemini", "GPT", "zenn"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-rss"
query: ""
---

## 背景

AI コーディングツールやエージェントを使い始めると、最初は 1 つの API key で足ります。ところが実運用に近づくほど、次のような問題が出てきます。

* Claude / GPT / Gemini / DeepSeek など、用途ごとに使いたいモデルが変わる
* API key がツールごとに増えて管理しづらい
* モデルごとに料金、制限、レスポンス速度が違う
* 障害や rate limit のときに手動で切り替える必要がある
* チーム利用だと、誰がどのモデルをどれだけ使ったか分からない

この問題を解くための薄いレイヤーが LLM API Gateway です。

## 最小構成

まずは次の 4 つがあれば成立します。

```
Client / Tool
  ↓
OpenAI-compatible endpoint
  ↓
Routing layer
  ↓
Model providers
```

クライアント側は OpenAI SDK や Cline / Dify / OpenWebUI のようなツールです。Gateway 側が OpenAI 互換の endpoint を持っていれば、多くの場合は `base_url` と `api_key` を差し替えるだけで接続できます。

## Gateway が持つべき責務

### 1. 認証と key 管理

ユーザーには 1 つの API key を渡し、裏側で各 provider の key を管理します。チーム利用では、個人 key の乱立を防ぎやすくなります。

### 2. モデル選択

モデル名をそのまま provider に渡すだけではなく、用途ごとの推奨や alias を用意すると運用しやすくなります。

```
coding-fast      → 低遅延のコード向けモデル
coding-quality   → 高品質のコード向けモデル
cheap-test       → 検証用の低価格モデル
long-context     → 長文向けモデル
```

### 3. fallback

本番利用では、特定モデルの rate limit や一時障害が起きます。fallback を設計しておくと、ユーザー側のコードを書き換えずに継続できます。

```
primary: claude-like-model
fallback:
  - gpt-like-model
  - gemini-like-model
  - low-cost-model
```

### 4. コストの可視化

日本語は英語より token 数が増えやすく、為替の影響もあります。1 リクエストごとの概算コスト、日次/月次の上限、残高の見通しを出すと、利用者の不安が減ります。

## OpenAI 互換にする理由

独自 API を作ることもできますが、最初の導入ハードルは上がります。開発者がすでに使っている SDK やツールに合わせるなら、OpenAI 互換 endpoint を持つ方が簡単です。

```
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.API_KEY,
  baseURL: process.env.BASE_URL,
});

const res = await client.chat.completions.create({
  model: "coding-fast",
  messages: [{ role: "user", content: "この関数をリファクタしてください" }],
});

console.log(res.choices[0].message.content);
```

## まとめ

LLM API Gateway は「モデルをたくさん並べるサービス」ではありません。実際には、認証、モデル選択、fallback、コスト可視化、チーム管理をまとめる運用レイヤーです。

個人利用では `base_url` 差し替えの簡単さが重要で、チーム利用では予算上限や監査ログが重要になります。どちらも、最初の設計段階で分けて考えると後から拡張しやすくなります。

---

Flatkey でも OpenAI 互換 endpoint と複数モデルの routing を検証しています。設定例だけ見たい場合は、公式ドキュメントにまとめています。
