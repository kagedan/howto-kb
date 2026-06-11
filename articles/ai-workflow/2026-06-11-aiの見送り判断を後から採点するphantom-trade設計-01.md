---
id: "2026-06-11-aiの見送り判断を後から採点するphantom-trade設計-01"
title: "AIの「見送り判断」を後から採点するPhantom Trade設計"
url: "https://qiita.com/inowa/items/0c7c9fbbd6d24a178fdd"
source: "qiita"
category: "ai-workflow"
tags: ["AI-agent", "Python", "TypeScript", "qiita"]
date_published: "2026-06-11"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

Hermes Agent には **Phantom Trade（ファントムトレード）** という仕組みがあります。Claude が「WAIT（見送り）」を選んだとき、「もしエントリーしていたら？」を仮想トレードとして記録し、後から正解・不正解を採点する機能です。

---

## なぜ WAIT の記録が必要か

自動売買システムの評価は普通「実際のトレードの勝率」で行います。しかしこれだと **「慎重すぎて勝てるトレードを全部見逃している」** 状態を検知できません。

```
実際のトレード：0勝0敗 WR = N/A（判断できない）

でも実は…
WAIT したトレード：8勝2敗 → 見逃しコスト大！
```

Phantom Trade は「見送り判断の質」を定量化するためのものです。

---

## 実装の仕組み

### 1. WAIT 時に phantom を記録

Stage 2（Claude）が WAIT を返したとき、通常の市場時間内であれば phantom として記録します。

```typescript
// hermes.ts（抜粋）
} else {
  // WAIT — 市場が開いている時間帯のみ phantom 記録
  if (isMarketTradeable(symbol)) {
    const phantomId = this.memory.phantomRecord({
      symbol,
      direction:  preliminary.action === "BUY" ? "LONG" : "SHORT",
      entryPrice: indicators.price,
      stopLoss:   decision.stop_loss  ?? preliminary.stopLoss,
      takeProfit: decision.take_profit ?? preliminary.takeProfit,
      rsi14:      indicators.rsi,
      atrPct:     (indicators.atr / indicators.price) * 100,
      engineType: params.engineType,
      reasoning:  decision.reasoning_brief,  // なぜ見送ったか
    });
  }
}
```

### 2. 通常の SL/TP チェックで自動決着

```typescript
// memory.ts（抜粋）
checkPendingOutcomes(latestPrices: Map<string, number>): TradeMemoryEntry[] {
  const resolved: TradeMemoryEntry[] = [];
  for (const e of this.entries) {
    if (e.outcome) continue; // 決着済みはスキップ

    const price = latestPrices.get(e.symbol);
    const hitTP = e.direction === "LONG" ? price >= e.takeProfit : price <= e.takeProfit;
    const hitSL = e.direction === "LONG" ? price <= e.stopLoss  : price >= e.stopLoss;

    if (hitSL) {
      e.outcome = "LOSS"; // → WAIT は正解だった
      resolved.push(e);
    } else if (hitTP) {
      e.outcome = "WIN";  // → WAIT は間違いだった
      resolved.push(e);
    }
  }
  return resolved;
}
```

real トレードも phantom トレードも**同じロジック**で SL/TP を判定します。型フィールド（`e.type`）で区別するだけです。

---

## キャリブレーションへの活用

phantom の勝率は **Claude が「慎重すぎるか」「適切か」** の指標になります。

```typescript
// memory.ts（getSummaryForClaude内）
const phantomNote = phantomWins.length > phantomLosses.length
  ? "You have been too conservative — your WAITs are missing more wins than losses."
  : phantomWins.length < phantomLosses.length
    ? "Your WAITs are mostly correct — those skipped setups would have lost."
    : "Your WAITs are mixed — roughly equal wins and losses skipped.";
```

このメッセージが Claude へのコンテキストに含まれ、次の判断に影響します。

```
Memory (META SHORT, RSI 52-76):
  [WAIT decisions retrospective] 8 resolved: 6 would-be WIN, 2 would-be LOSS
  Calibration note: You have been too conservative — your WAITs are
  missing more wins than losses.
```

---

## Discord 通知

phantom の記録・決着はリアルタイムで Discord に通知されます。

```
👻 Phantom recorded — META SHORT
Entry: 608.51 | SL: 609.375 | TP: 606.78 | R:R 1:2.0
"Structural engine fired SELL on RSI 64 overbought, but the last bar
is a strong bullish marubozu..."

5分後 →

✅ Phantom WIN — META SHORT
Entry: 608.51 → Exit: 606.78 | P&L: +0.28%
```

実際のトレードと見た目が似ているので、「WAIT したはずなのに TP 到達した」というフィードバックが直感的にわかります。

---

## ダッシュボードでの可視化

Streamlit ダッシュボードの Overview タブに **Phantom Calibration** グラフがあります。

```python
# python/dashboard/app.py（概略）
phantom_closed = df[(df["type"] == "phantom") & df["outcome"].notna()]
wins   = len(phantom_closed[phantom_closed["outcome"] == "WIN"])
losses = len(phantom_closed[phantom_closed["outcome"] == "LOSS"])

# バーチャート：WAITが正解(LOSS)か間違い(WIN)か
st.bar_chart({"Would-be WIN (miss)": wins, "Would-be LOSS (correct)": losses})
```

---

## 設計上の注意点

### 市場時間外の WAIT は記録しない

株式で 22:00 JST（after-hours）に WAIT した場合、翌朝には価格が大きく動いている可能性があります。このギャップは「signal が正しかったか」の判定に使えないため、`isMarketTradeable()` が false の間は phantom を記録しません。

### win rate gate は phantom を見ない

`getOverallWinRate()` は real トレードのみを対象にします。phantom は「見送り精度の検証」用であり、システムの実力評価に混ぜるべきではないためです。

```typescript
getOverallWinRate(minTrades = 5): { winRate: number | null; closedCount: number } {
  const closed = this.entries.filter(
    e => (e.type ?? "real") === "real" &&  // real のみ
         (e.outcome === "WIN" || e.outcome === "LOSS"),
  );
  // ...
}
```

---

## まとめ

Phantom Trade は「AIが見送った判断を後から採点する」という、従来の自動売買システムにはない仕組みです。

| 目的 | 内容 |
|------|------|
| 見逃しコスト可視化 | WAIT した場合に何を失ったか定量化 |
| Claude の自動キャリブレーション | 過剰に慎重な判断を次サイクルで補正 |
| 戦略の検証 | 「エンジンは正しいが Claude が見送った」パターンを発見 |

実際の運用で最も役立っているのは「Claude が連続して WAIT した銘柄を後から見ると全部 WIN だった」というパターンの発見です。こうなるとキャリブレーション警告が出て、Claude が次サイクルで EXECUTE しやすくなります。
