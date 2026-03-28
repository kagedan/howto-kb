---
id: "2026-03-27-claude-code-agent-teams-でllmのデータ品質を自動検証してみた-01"
title: "Claude Code Agent Teams でLLMのデータ品質を自動検証してみた"
url: "https://qiita.com/kei-concierge/items/600994783a474dce4811"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

---

## はじめに

AIが出力する情報を、あなたはどこまで信頼していますか？

社内でClaude APIを使った自動レポート生成システムを構築したとき、最初は「これで工数が半分になる！」と喜んでいました。でもしばらく運用してみると、じわじわと問題が積み上がってきました。

**実際に起きた品質問題 3例**

1. **ハルシネーション（幻覚）の混入**: 存在しない数値・出典が本文に紛れ込み、気づかずに承認されたケースが2件発生
2. **フォーマット崩れ**: プロンプトを少し変えただけで Markdown の表が壊れてパースエラーになる
3. **トーン・文量のばらつき**: 同じプロンプトでも、日によって文体や分量が大きく違う

「LLMの出力は非決定的だから仕方ない」——そう思っていたとき、**Claude Code Agent Teams** を使ったデータ品質自動検証の構成を試してみました。今回はその仕組みと、実際に動かして気づいたことを紹介します。

---

## Agent Teams とは？

Claude Code の Agent Teams は、**
