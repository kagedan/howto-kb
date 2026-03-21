---
id: "2026-03-21-claude-code-スキルで-readme-を渡すだけで要件定義からランニングコスト見積もりまで-01"
title: "Claude Code スキルで README を渡すだけで要件定義からランニングコスト見積もりまでを自動化する"
url: "https://zenn.dev/kazusa_nakagawa/articles/article14_claude_code_skill_estimate"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

はじめに
時間が限られた状況で、要件から実現可否・見積もりを出す必要がある場合に叩き台として使える Skills を作成してみました。
精度はブラッシュアップしながら上げていければと考えています。工数設定が大きい気がする。。。
すでに有用な情報はあるかと思いますが、私なりに Claude Skills 機能の理解を深めたく作成しました。


README → 要件分析 → 顧客向けサマリー + 設計書（req-estimate）

設計書 → DB設計書（db-design）

設計書 + DB設計書 → 詳細設計書（detail-design）

設計書 → 月額ランニングコスト ...
