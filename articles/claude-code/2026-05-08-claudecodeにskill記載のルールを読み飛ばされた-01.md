---
id: "2026-05-08-claudecodeにskill記載のルールを読み飛ばされた-01"
title: "ClaudeCodeにSKILL記載のルールを読み飛ばされた。"
url: "https://qiita.com/Y-Misaki/items/411cae322300c3e893e8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

## 要約

* SKILLSの内容を読み飛ばされました。
* 原因はユーザとClaudeCodeとの会話が長くなり、ClaudeCodeの精度が落ちてしまいました。
* 適度に「/clear」や「/compact」で会話のリセットや要約を行うことが重要です。

---

## 状況

　ClaudeCodeのSKILLSを用いて作業を行っていた際、SKILLSに記載されたルールをClaudeCodeが読み飛ばし、outputを出力するという事象が発生しました。

---

## 原因

　Claude Codeはコンテキストウィンドウ（一度に保持できる情報量）に上限があり、会話が長くなると古い内容が自動圧縮されます。  
SKILLの内容は毎回読み込まれますが、作業途中の詳細な文脈（「さっきこのルールを確認した」「このファイルを読んだ」等）が薄まります。  
結果、ClaudeCodeの精度が弱まり、SKILLやCLAUDE.mdに記載したルールが読み飛ばされるという事象が発生します。

---

## 解決策：こまめな会話リセット

　「/clear（会話履歴を完全リセット）」や「/compact（会話を要約）」を行います。

| コマンド | 効果 | 使いどころ |
| --- | --- | --- |
| /clear | 会話履歴を完全リセット | 別のタスクに切り替える時 |
| /compact | 会話を要約して圧縮（履歴は残る） | 同じタスクを続けながら軽くしたい時 |
