---
id: "2026-06-21-akira-papa-it-claude-codeを自分仕様に育てる7つの指示方法をメモシェアcla-01"
title: "@akira_papa_IT: 【Claude Codeを自分仕様に育てる7つの指示方法をメモシェア〜🎵CLAUDE.mdに何でも書くのはもう卒業👀"
url: "https://x.com/akira_papa_IT/status/2068837895524507930"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "x"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

【Claude Codeを"自分仕様"に育てる7つの指示方法をメモシェア〜🎵CLAUDE.mdに何でも書くのはもう卒業👀】

⚙️ Claude Code「指示の置き場所」完全整理

各手法は ①いつ読まれるか ②圧縮(compaction)後も残るか ③強さ・コスト で使い分け。

■ 常駐＝強いがコスト高 🔴
 ▸ CLAUDE.md(root):起動時から常駐。ビルドコマンド・構成・規約用。※200行以内＆オーナー必須
 ▸ Rules(無スコープ):常時ロード＋圧縮後も再注入
 ▸ Output Styles:システムプロンプトに注入＝遵守度が最強。役割ごと変える時だけ

■ 必要時だけ＝軽い 🟢
 ▸ CLAUDE.md(サブ階層)/Pathスコープ Rules:該当ディレクトリを触った時だけ発火
 ▸ Skills:名前と説明だけ常駐→呼ばれて本体ロード。デプロイ等の"手順"はここ
 ▸ Subagents:別ウィンドウで隔離実行→結果サマリーだけ返す。並列調査・監査向き

■ 確実な強制力 🔒
 ▸ Hooks:イベント発火で確定実行。lint自動化・コマンドブロック等。圧縮を完全回避

💡 置き場所の鉄則
 - 「毎回必ずYして」→ Hook(自動実行≠AIの判断)
 - 「絶対するな」→ Hook/権限で物理ブロック(指示は破られ得る)
 - 30行の手順 → Skill へ
 - API限定ルール → paths: でスコープ
 - 個人設定→user階層／チーム設定→project階層

→揃えたら plugin にまとめてチーム共有も◎

Steering Claude Code: CLAUDE.md files, skills, hooks, rules, subagents and more
　URL: https://t.co/HRTAzng1mA
