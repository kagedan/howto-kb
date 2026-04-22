---
id: "2026-04-22-770mパラメータでtransformer-13bに匹敵すると主張openmythosアーキテクチャ-01"
title: "770MパラメータでTransformer 1.3Bに匹敵すると主張——OpenMythosアーキテクチャをPyTorchで読み解く"
url: "https://qiita.com/shioccii/items/7572f472e2a7acd01c71"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

## 概要

LLMの世界では「パラメータ数が多いほど賢い」という直感が長く通用してきました。ところが最近は、アーキテクチャの工夫次第でパラメータ効率を大幅に改善できる事例が相次いでいます。

その流れに沿った注目プロジェクトが **OpenMythos** です。Kye GomezがGitHub上で公開したこのPyTorchプロジェクトは、Anthropicが公式技術論文を出していない「Claude Mythos」アーキテクチャを理論的に再構成し、770Mパラメータで1.3BクラスのTransformerと同等の性能を実現すると主張しています。

本記事ではOpenMythosが何を目指しているのか、どのような設計思想に基づいているのか、そしてAI開発や業務効率化に取り組む実務者にとって何が参考になるかを整理します。

---

## Claude Mythosとは何か

Anthropicは自社モデルのアーキテクチャ詳細を積極的に公開していません。Claude 3系やClaude 4系についても、学術論文ベースの詳細な技術報告は限られており、推論効率化やスケーリングの手法は「社内知
