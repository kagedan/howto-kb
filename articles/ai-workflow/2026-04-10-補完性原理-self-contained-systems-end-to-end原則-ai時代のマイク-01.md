---
id: "2026-04-10-補完性原理-self-contained-systems-end-to-end原則-ai時代のマイク-01"
title: "補完性原理 × Self-contained Systems × End-to-End原則 — AI時代のマイクロサービス設計"
url: "https://zenn.dev/fixu/articles/subsidiarity-scs-end-to-end-ai-native"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

はじめに — 「共通基盤 + DRY + 共通モジュール」は本当に正解か
マイクロサービス化したはずなのに、なぜか「共通基盤」の更新が全サービスのボトルネックになっていく。モジュールを DRY にした途端、ちょっとした改修にも全サービスの影響調査が必要になる。ベストプラクティスを中央で一元管理しようとしたら、誰もそれを更新したがらなくなる。
こうした「中央集権の疲弊」は、マイクロサービス時代のあるあるとして多くの組織で観測されています。
本記事の主張を先に3行で示します。


中央集権的な共通基盤は、更新サイクルのミスマッチでいずれ詰まる。低頻度・高影響と高頻度・低影響が同じ場所に同...
