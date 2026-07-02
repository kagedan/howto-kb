---
id: "2026-07-02-oikon48-ちなみにclaude-fable-5をまとめ役にする手法はいくつかあります-clau-01"
title: "@oikon48: ちなみにClaude Fable 5をまとめ役にする手法はいくつかあります ・CLAUDE.mdに指示を書く（Suba"
url: "https://x.com/oikon48/status/2072608553685414020"
source: "x"
category: "claude-code"
tags: ["CLAUDE-md", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

ちなみにClaude Fable 5をまとめ役にする手法はいくつかあります

・CLAUDE.mdに指示を書く（Subagentのモデルなど）
・--append-system-prompt を使う
・カスタム output-style を作る
・/advisor にFable 5を指定する
・OpusPlanでFable 5をPlan modelに指定する

それぞれ使用感とPros/Consが違うので、色々試してみると良いと思います。

/advisor でFable 5指定いけると思ったけど、実はFable 5使えなかったりしますか？バグですか？ https://t.co/Gvk6Nj9EjP


--- 引用元 @oikon48 ---
Claude Fable 5 にプランさせて、Opus 4.8 や Sonnet 5で実行する手法で、個人的には以下が今のところしっくりきた

・サブエージェントをFable以外に固定（CLAUDE_CODE_SUBAGENT_MODEL）
・システムプロンプトにFable運用用の指示を追記（--append-system-prompt）

例)
CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5 claude --append-system-prompt "基本的にタスクや作業の実行は、適切な粒度でsubagentsに実行手順が明確な指示を与えて委譲すること。あなたは全体進行の俯瞰と立案を行う。自己判断による例外は認める"

CLAUDE/.md やルールファイルと違って、簡単で設定をクリーンに保てるので、Fable 5が期間限定である限りしばらくはこれを試してみる
