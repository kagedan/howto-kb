---
id: "2026-05-17-claude-maxサブスクanthropicのmessages-apiは叩けない別途apiキー必須-01"
title: "Claude MaxサブスクAnthropicのMessages APIは叩けない：別途APIキー必須、5分で解決"
url: "https://qiita.com/DevMasatoman/items/02dcfb75eb29fca6bbad"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "Python", "TypeScript", "qiita"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

## 結論：Max サブスクと API は別課金体系

```typescript
import Anthropic from "@anthropic-ai/sdk";

// ❌ ANTHROPIC_API_KEY がないと AuthenticationError
// Max/Pro サブスクのクオータは使えない
const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// ✅ platform.anthropic.com で別途 API キーを発行してチャージ後に動く
```

Claude Max/Pro のサブスクリプションが使えるのは以下だけです：

| サービス | Max/Pro で使えるか |
|---|---|
| claude.ai のチャット | ✅ |
| Claude Code（CLI・VS Code拡張） | ✅ |
| Messages API | ❌ |
| Agent SDK | ❌ |
| 自作アプリの API 呼び出し | ❌ |

## なぜ混同するのか

Claude Code（CLI）は Max プランで動くので、「API も同じ枠で使えるはず」と思い込みがちです。実際は Claude Code が内部で OAuth トークンを使っているだけで、自分でコードを書いて `anthropic.messages.create()` を呼ぶ場合は `ANTHROPIC_API_KEY` が別途必要です。

**2026年4月4日以降**は、OAuth 経由でサブスク枠を使う第三者ツール（CLIProxy 系）も Anthropic が公式にブロックしました。

## 解決手順（5分）

1. [platform.anthropic.com](https://platform.anthropic.com) にアクセス
2. 「API Keys」→「Create Key」でキー発行
3. 「Billing」→「Add credit」で **$5** チャージ
4. `.env.local` に `ANTHROPIC_API_KEY=sk-ant-...` を追記

```bash
# 確認
echo $ANTHROPIC_API_KEY
```

## 注意：Claude Code への影響

`ANTHROPIC_API_KEY` を設定すると **Claude Code もこのキーに切り替わります**（Max クオータが消費されなくなる）。Claude Code は Max プランのまま使いたい場合は、環境変数を実行環境ごとに分けてください。

## Python の場合

```python
import anthropic

# API キーが必須
client = anthropic.Anthropic(api_key="sk-ant-...")
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

## コスト感（業界ベンチマーク試算）

Sonnet 4.6 で入力 1,000 + 出力 500 トークンの往復 1 回 ≈ $0.0105（約¥1.6）。$5 チャージで数百回の呼び出しが可能です（業界ベンチマーク試算）。

| モデル | 入力 $/MTok | 出力 $/MTok |
|---|---|---|
| Claude Opus 4.7 | $5.00 | $25.00 |
| Claude Sonnet 4.6 | $3.00 | $15.00 |
| Claude Haiku 4.5 | $0.80 | $4.00 |

---

より詳しいコスト試算と「で、どう稼ぐ？」の視点は masatoman.net の記事で公開しています。

👉 [Claude Max契約者の盲点：外部アプリのAPI利用はサブスク枠外、従量課金キー別途必須](https://masatoman.net/articles/claude-max-api-key-required-2026)
