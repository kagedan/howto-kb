---
id: "2026-03-30-ブラウザなしpc-で-claude-code-を-oauth-認証する手順-01"
title: "ブラウザなしPC で Claude Code を OAuth 認証する手順"
url: "https://zenn.dev/akinobukato/articles/5bd6db5d657f20"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "VSCode", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

ブラウザなしPC で Claude Code を OAuth 認証する手順
ブラウザが使えない PC でも、スマホや別 PC を使って Claude Code の OAuth 認証を通す方法。

 前提

認証したい PC にはブラウザがない（または使えない）
スマホ or 別 PC でブラウザ操作ができる
API キーは使えず、OAuth 認証が必要



 手順

 1. 認証を開始する
ブラウザなし PC のターミナルで以下を実行：
claude
ログイン URL がターミナルに表示される。c キーを押すと URL をクリップボードにコピーできる。
もしくはvscodeでcla...
