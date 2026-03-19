---
id: "2026-03-18-aiに色を聞いてはいけない-vision-modelの色認識の限界と正確に取得する方法-01"
title: "AIに色を聞いてはいけない — Vision Modelの色認識の限界と、正確に取得する方法"
url: "https://zenn.dev/kenimo49/articles/ai-color-recognition-limit"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

AIにスクリーンショットの色を聞いてみた
Figmaのデザインカンプを見ながら、Claude CodeやCodexにスクリーンショットを渡してフロント実装を進めていたときのことです。出来上がったUIを見て「なんか色が違う」と感じました。
Figma上では落ち着いたダークネイビーだったはずが、AIが実装したCSSでは微妙に青みが強い。ボタンの赤も、どこか彩度が高すぎる。AIはスクリーンショットを「見て」実装しているはずなのに、なぜカラーコードがズレるのか。
気になったので、検証してみました。12色のカラーパレット画像を作成し、Claude Visionに各ブロックのhexカラーコードを...
