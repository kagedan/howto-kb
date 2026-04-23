---
id: "2026-03-28-llm-apiコスト比較2026openai-vs-claude-vs-gemini試験対策アプリの-01"
title: "LLM APIコスト比較2026：OpenAI vs Claude vs Gemini（試験対策アプリの視点から）"
url: "https://qiita.com/takkenai/items/a367ea202f2e036c9517"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "Gemini", "GPT", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

# LLM APIコスト比較2026：OpenAI vs Claude vs Gemini（試験対策アプリの視点から）

個人開発で宅建（宅地建物取引士）試験対策アプリ [takkenai.jp](https://takkenai.jp) を運営しています。1250問以上の過去問にAI解説を付けており、毎日かなりの量のLLM API呼び出しが発生します。

そこで2026年時点での実運用データをもとに、主要3社のLLM APIを比較してみました。

## はじめに：なぜこの比較が必要だったか

宅建アプリのAI解説機能では「結論→根拠→覚え方」の3段階で解説を生成しています。1問あたり約700トークンの出力が発生し、月間リクエスト数が増えるにつれてAPIコストが無視できなくなりました。

## トークン単価比較（2026年3月時点）

| モデル | 入力 (USD/1M) | 出力 (USD/1M) |
| --- | --- | --- |
| GPT-4o | $2.50 | $10.00 |
| GPT-4o mini | $0.15 | $0.60 |
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| Claude 3 Haiku | $0.25 | $1.25 |
| Gemini 2.0 Flash | $0.10 | $0.40 |

## 品質比較：日本語の自然さと解説の丁寧さ

同じ宅建過去問を各モデルに投げて比較しました。

**Claude 3.5 Sonnetの解説例：**

```
【結論】正しい記述です。

【根拠】宅建業法第39条第1項により、宅建業者が自ら売主となる場合、
手付金は代金の20%が上限。業者間取引には適用されない点も重要です。

【覚え方】「手付は2割まで」＋5%超・1000万超は保全措置必要もセットで覚える。
```

**Gemini 2.0 Flashの解説例：**

```
【結論】正しいです。

【根拠】宅建業法39条により手付金は代金の20%が上限です。

【覚え方】20%＝10分の2、これを超えると違反になります。
```

ClaudeはGeminiに比べ関連知識（業者間取引の例外、保全措置）まで言及しており、学習効果が高いです。

## 日本語品質スコア（主観評価）

| モデル | 自然さ | 正確性 | 学習効果 | 総合 |
| --- | --- | --- | --- | --- |
| Claude 3.5 Sonnet | 9 | 10 | 10 | **9.7** |
| Claude 3 Haiku | 8 | 9 | 8 | **8.3** |
| GPT-4o | 8 | 9 | 7 | **8.0** |
| Gemini 2.0 Flash | 7 | 8 | 6 | **7.0** |

## コスト最適化：キャッシュ戦略

同じ問題への解説は頻繁に発生します。Redisによるキャッシュで大幅なコスト削減を実現しました。

```
export async function getCachedExplanation(questionId: string): Promise<string | null> {
  const key = `explanation:${questionId}`;
  return redis.get<string>(key);
}

export async function setCachedExplanation(
  questionId: string,
  explanation: string,
  ttl = 60 * 60 * 24 * 30 // 30日
): Promise<void> {
  await redis.setex(`explanation:${questionId}`, ttl, explanation);
}
```

キャッシュ導入後、APIコストが約60%削減されました。

## まとめ：コスパ最強はどれ？

| 用途 | おすすめ | 理由 |
| --- | --- | --- |
| 本番の日本語解説 | Claude 3.5 Sonnet | 品質とコストのバランス最良 |
| 大量バッチ処理 | Claude 3 Haiku | 品質十分でコスト大幅削減 |
| コスト最優先 | Gemini 2.0 Flash | 圧倒的な安さ |

日本語の試験解説という用途では、Claudeシリーズが頭一つ抜けています。

## おわりに

この比較・最適化の知見を活用して開発した宅建試験対策アプリ **[takkenai.jp](https://takkenai.jp)** をぜひ試してみてください。1250問以上の過去問、AI解説付き、基本無料です。
