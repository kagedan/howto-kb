---
id: "2026-04-06-anthropic公式skills完全ガイドを読んだらskillmdのトークン消費を40削減できた-01"
title: "Anthropic公式「Skills完全ガイド」を読んだら、自分のSKILL.mdのトークン消費を40%減らせた"
url: "https://qiita.com/yurukusa/items/f69920b4a02cf7e2988c"
source: "notebooklm"
category: "claude-code"
tags: ["claude-code", "skills", "token-optimization", "qiita"]
date_published: "2026-03-13"
date_collected: "2026-04-06"
summary_by: "cowork"
---

Anthropic公式ガイド「The Complete Guide to Building Skills for Claude」の知見を自分のSkillに適用し、SKILL.mdのトークン消費を約40%削減した実践報告。

## Progressive Disclosure（段階的開示）の3層構造

Skillのトークン効率を高める鍵は「3層分離」にある。

- **第1層: YAMLフロントマター** — 常に読み込まれる部分。name（kebab-case必須）とdescription（トリガーフレーズを具体的に記載）を置く。
- **第2層: SKILL.md本文** — スキル発火時にのみ読み込まれる。実際の手順やルールを記述。
- **第3層: references/フォルダ** — 必要時のみ読み込まれる。API仕様・エラーパターン・詳細情報を分離。

## 具体的な改善例

15,885バイトのスキルを6,000バイトに削減。6プラットフォーム対応の投稿手順をreferences/に分離し、プラットフォーム固有の部分は参照ファイル化した。

## Troubleshootingセクション

「エラー → 原因 → 対処」の3点セット構造をSKILL.mdに含めることで、エージェントの自律解決率が向上する。

## まとめ

「3層分離」というシンプルな構造変更だけで40%のトークン削減が実現可能。スキルが肥大化してきたら、まずreferences/への分離を検討すべき。
