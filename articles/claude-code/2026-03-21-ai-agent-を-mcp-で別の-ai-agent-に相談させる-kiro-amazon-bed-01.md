---
id: "2026-03-21-ai-agent-を-mcp-で別の-ai-agent-に相談させる-kiro-amazon-bed-01"
title: "AI Agent を MCP で別の AI Agent に相談させる (Kiro / Amazon Bedrock)"
url: "https://zenn.dev/kumagaias/articles/9f70ea31a66cd4"
source: "zenn"
category: "claude-code"
tags: ["MCP", "AI-agent", "Gemini", "zenn"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## 背景

AI エージェントがアドホックな対応でループし続けることがあります。

そんなとき、別の AI（Claude や Gemini）に会話のログを渡して相談すると、同じモデルを使っていても的確な答えが返ってくることがあります。

コンテキストが多すぎるとループしてしまうのかもしれません。

そこで、MCP (Model Context Protocol) を使って、AI エージェントが別の AI に自動で相談できる仕組みを試してみました。

## 実装：Bedrock Advisor MCP Server

私の場合は Kiro (IDE) を使っていて、AWS アカウントもあり、AWS にコストをまとめたかったので、以下の流れにしました。

Kiro => MCP => Amazon Bedrock の Claude

MCP はいったんローカルで Node.js で動かす感じです。

実装の全コードはこちらです。  
<https://github.com/kumagaias/kiro-best-practices/blob/main/mcp/bedrock-advisor/src/index.ts>

AWS アカウントでなくても、Anthropic や OpenAI の API キーを使う構成に変えれば同様の仕組みが作れます。

### 主な機能

1. **ask\_advisor**: 問題を相談する
2. **record\_attempt**: 修正試行を記録し、同じエラーが2回以上発生したら自動的に Advisor に相談

### コード例

```
// record_attempt の使い方
// エラー修正を試みる前に必ず呼び出す
await record_attempt({
  error_key: "FFmpeg timeout",
  what_i_tried: "Increase timeout from 180s to 300s",
  code_context: "VideoCompositor.ts:145-160"
});

// 同じエラーが2回目なら、自動的に Advisor に相談される

// ask_advisor の使い方
const advice = await ask_advisor({
  question: "FFmpeg zoompan filter is too slow on Cloud Run. How to optimize?",
  context: `
    - Cloud Run: 4GB RAM, 2 CPU, no GPU
    - Current: zoompan filter for Ken Burns effect
    - Problem: Takes 10+ minutes, hits Cloud Run timeout
  `
});
```

## 実際の例

**問題**: FFmpeg の `zoompan` フィルタが遅すぎて Cloud Run の 10 分タイムアウトに引っかかっていた

**Advisor の提案と結果**:

* `-hwaccel auto` でハードウェアアクセラレーション（Cloud Run では GPU 非対応のため不採用）
* `-preset faster` と `-crf 28` で品質とスピードのバランス調整（効果あり）
* **`zoompan` を `scale+crop` に置き換え → 決定打**

**結果**: `zoompan` → `scale+crop` に変更したところ、処理時間が 10 分超から約 1 分に短縮（約 10 倍高速化）。タイムアウト問題が解決しました。処理時間は FFmpeg のログ出力から計測しています。

## MCP 設定例

./kiro/settings/mcp.json

```
{
  "mcpServers": {
    "bedrock-advisor": {
      "command": "sh",
      "args": [
        "-c",
        "node ~/.kiro/kiro-best-practices/mcp/bedrock-advisor/dist/index.js"
      ],
      "env": {
        "AWS_REGION": "us-west-2"
      },
      "disabled": false,
      "autoApprove": [
        "ask_advisor"
      ]
    }
  }
}
```

## まとめ

AI エージェントが行き詰まったとき、別の AI に相談させることで次の効果が得られました。

* 新鮮な視点で問題を見直せる
* コンテキストをリセットして本質的な問題に集中できる
* 同じエラーを繰り返すループから抜け出せる

MCP を使ってこの「相談」を自動化できました。

お読みいただきありがとうございました！！

---
