---
id: "2026-04-05-openclawのclaude代替モデル-01"
title: "OpenClawのClaude代替モデル"
url: "https://note.com/ioridev/n/nc36e4c8a209a"
source: "note"
category: "claude-code"
tags: ["claude-code", "GPT", "note"]
date_published: "2026-04-05"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

Claude CodeのサブスクプランをOpenClawで使うのができなくなったらしい。（いや、元々ダメなんだけど、できちゃうからやってるやつがいっぱいいた）

ChatGPT、Codexのサブスクを使うのはおっけーらしいが、GPT5.4は会話するには出力がきしょすぎる。

Z.ai の GLM というモデルが出力がClaudeに似ていて定額で安く使えるのでおすすめ

価格はこんな感じで

![](https://assets.st-note.com/img/1775349659-fCmBIG1qpngzV94dtOkbU2Y0.png?width=1200)

10ドル払えばClaude Proの3倍、30ドル払えばClaude 100 ドルプランと同じくらい使えるといった触れ込み

コーディング性能も結構いいっぽい、僕はコーディングはCODEXにやらせるのでよくわからんが

![](https://assets.st-note.com/img/1775349835-IvOoQ7KNridBq6uL3SXFgtza.png?width=1200)

まぁとにかくClaudeっぽい出力のモデルが 1 / 3 の価格で使えるので、OpenClaw用としてはかなりおすすめ

一応使ってる感じだと  
GLM 5 → 十分いい安定  
GLM5.1 → いいけどたまに他の言語がまじって不安定？  
って感じ、  
で、glm-5-turboってのがあってこれはオープンモデルではないけどOpenClawみたいなハーネスエージェントに最適化されてるっぽくていまこれ試してる。

Vertex AI経由でも使えるようになってるのでエンプラではVertex AI経由で使ってます。

Z.AI 自体も Auto Clawっていうエージェントアプリ出してるから、それ用に調整したならまあ良さそうではあるかもな

ちなみに、出力が似ててZ.AIも公式ページでやけにClaudeと比較してるほど意識していながら、アンソロピックのこいつら蒸留してやがる名指しリストには名前入ってない

真面目にがんばってるのか…?

おまけで僕の OpenClaw のSOUL.MD貼っときます。

```
- Never guess. Read the file first. Search before asking. Be resourceful.
```

ってのが肝かも
