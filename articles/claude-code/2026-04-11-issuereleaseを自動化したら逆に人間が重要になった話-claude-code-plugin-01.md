---
id: "2026-04-11-issuereleaseを自動化したら逆に人間が重要になった話-claude-code-plugin-01"
title: "Issue→Releaseを自動化したら、逆に人間が重要になった話 ― Claude Code Plugin gh-issue-driven を作って学んだ HITL Gate 設計"
url: "https://qiita.com/kiyotaman/items/302c8b7dc2cbcec555ff"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに
> **AI の出力そのものではなく、AI の出力を見た人間の中に起きる反応こそが価値である。**

この記事は「**AIで開発しているけど、なんか質が上がらない**」と感じている方向けです。

https://docs.google.com/presentation/d/1eVUJLepOofN5bJUC7GBK7grPgTqRdfge5Ft9izaK8k4/edit?usp=sharing

## TL;DR

- AI は品質を上げます。でも、価値は生みません
- 価値は「**立ち止まった時**」にだけ生まれます
- **Gate** はそのための装置です ― 承認ではなく、気づきを引き出す構造
- **gh-issue-driven** はその Gate を **3フェーズの横矢印** に仕込んだ Claude Code Plugin です

---

## 1. はじめに ― Issue を AI にレビューさせたら、Issue が間違っていた

ある日、Claude Code に Issue の設計レビューを頼みました。返ってきたのは「この実装方針は妥当です
