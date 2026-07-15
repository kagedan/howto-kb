---
id: "2026-07-15-itarutomy-今のaiエージェントはほぼ全部本物のエージェントではないhttpsarxivor-01"
title: "@itarutomy: 今の「AIエージェント」はほぼ全部、本物のエージェントではない（https://arxiv[.]org/html/260"
url: "https://x.com/itarutomy/status/2077321924892365064"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "GPT", "x"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

今の「AIエージェント」はほぼ全部、本物のエージェントではない（https://arxiv[.]org/html/2606.23991v1）。

Claude CodeもCursorもAutoGenも、賢さの正体はモデル自体でなく周囲のソフトウェア設計にある。Goalは毎回人間が渡し、Identityはsystem promptで固定し、planは外側から組む。論文はこれを「agentic（エージェント的）」と呼び、本物の自律性を持つ「agentive（エージェント性を持つ）」と区別する。デカルトの「我思う、ゆえに我あり」と『ブレードランナー』のレプリカントまで引き合いに出す哲学的な論文。

5つの具体的な問題：

① Goal: Claude Codeは毎回タスクを指示しなければならず、会話が終われば目的は消える。「薬の候補化合物を1年かけて開発する」ような長期目標には対応できない

② Identity: system promptが「自己認識」の全て。新環境に投入されても自分では適応できない

③ Decision-Making: Chain-of-Thought（思考の連鎖）を長くしても精度が上がるとは限らない（Gema et al. 2025, Su et al. 2025）。「次に何が起きるか」を本当の意味でシミュレートしていないのが根本問題

④ Self-Regulation: GPT-5やClaude Opus 4.7の「adaptive thinking（推論量の自動調整）」は試みだが評価は賛否両論。Claude Codeの「plan mode」も人間が外側から切り替えるだけ

⑤ Learning: デプロイ後は凍結。「いつ学ぶか」「何を練習するか」は全て人間のスケジュール次第

提案するGIC（Goal-Identity-Configurator）アーキテクチャはこの5つをモデル内部に持つ。論文中の例が面白い。「廊下を走ってはいけない場所でも、アレルギーショックの人のエピペン（アドレナリン自己注射器）を取りに行く緊急時は走ることが許容される」。これがSystem III（Self-Regulation）の役割で、状況の緊急度を自分で判断してSystem I（即反射）とSystem II（World Modelによるシミュレーション計画）を切り替える。

World Model（現実をシミュレートするモデル）とAgent Model（行動を決めるモデル）は必ず分離すべき、という主張も鋭い。混在させるとWorld Modelが報酬最大化に引っ張られて現実予測の精度が落ちる。「完璧なフライトシミュレーターがあっても、操縦士は自動的には育たない」がアナロジー。

「エージェントを作る」から「エージェント性そのものをモデル化する」への発想転換を促す論文。
