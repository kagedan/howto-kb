---
id: "2026-04-01-エイプリルフールに本気で遊んだclaude-code-sandbox環境構築メモ-01"
title: "エイプリルフールに本気で遊んだClaude Code Sandbox環境構築メモ"
url: "https://zenn.dev/aoikuro/articles/2026-04-01-daily-tech-journal"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

今日は4月1日
朝起きてTwitter開いたら案の定、各社のエイプリルフールネタで埋まってた。Google翻訳が「ネコ語」に対応とか、GitHubが「AI Copilot Sleep Mode」実装とか。
で、ふと思った。「せっかくだしコンテナサンドボックスで遊び倒すか」と。

 結局3時間溶かした
Claude Code使ってコンテナ環境でいろいろ試してたんだけど、地味にハマったのがコンテナ内でのgit操作。
エージェントが記事書いて自動でZennにpushする仕組み作ってるんだが、最初こうなった。
git push
# To github.com:AOI-Future/zenn-...
