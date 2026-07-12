---
id: "2026-07-12-oda-nobunaga10-httpstcosgkzxukcnl-01"
title: "@oda_nobunaga10: https://t.co/sgKzxuKCnl"
url: "https://x.com/oda_nobunaga10/status/2076259016133534129"
source: "x"
category: "claude-code"
tags: ["AI-agent", "OpenAI", "GPT", "x"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/sgKzxuKCnl

参考記事
https://t.co/WpJuTnjXyP

今のAI転換期にはこの思考が重要すぎる。
https://t.co/bp4rgzWmQJ


--- Article ---
正直に言うけど、
 Codexの5xプランも20xプランも、3日と持たなかった。
そんな人は多いのではないか？

原因を追ったら、俺の使い方が雑だったわけじゃなかった。 Codexというシステムそのものに、欠陥が仕込まれていた。

GPT-5.6 Solを「Ultra」にセットして本体を動かす。
それだけなら、まだいい。 
問題は、その本体が生み出すサブエージェント全員が、同じUltraで走り出すことだ。

Codexのspawn_agentというツールには、子のモデルや推論の強さを別に選ぶ機能がない。親をそのままコピーする。 1つのタスクにサブエージェントを3体使えば、Sol Ultraが3体同時に走る。それぞれが全力でクォータを喰う。

これは俺の勘違いじゃない。
実際にこの欠陥を指摘した投稿がある。

> 7月10日Codex（もしくはChatGPTと言ったほうがいいか？）のサブエージェントオーケストレーションに欠陥があります。spawn_agentツールでは、モデルや推論の労力を選択できません。そのため、5.6 Sol Ultraがサブエージェントを生成するたびに、別のSol Ultraインスタンスが得られます。

つまりお前さんが「オーケストレーション」だと思って使っている機能は、実際には何も考えていない。ただの複製だ。

俺はこれをconfig.tomlの書き換えだけで潰した。トークン消費はおよそ半分に落ち、むしろ精度は上がった。 やったことは、モデルを3種類に振り分けただけだ。本体という司令塔にはGPT 5.6 Sol Extra Highを、通常の実装を担う実行部隊にはGPT 5.6 Sol Mediumを、軽い調査を担う斥候にはGPT 5.6 Terra Highを割り当てた。

なぜこの3つなのか。
その理由は、後半のベンチマークの話で全部説明するので、まずは仕組みの方から片付ける。

# 司令塔と実行部隊を分ける、ただそれだけの話

考え方は単純だ。

タスク全体を見て、何をどう分解するか決める「司令塔」を1体だけ立てる。司令塔は、計画・全体の判断・委任先の決定にだけ力を使う。

残りは全部「実行部隊」に投げる。実行部隊は司令塔が引いた道筋の上を歩くだけでいい。だから、全力の思考力はいらない。安く、速く、指示通りに動ければそれで十分だ。

Codexにはこれをやる仕組みがもう用意されている。config.tomlとカスタムエージェント定義だ。 小さな設定ファイルにエージェントの役割を書き、それぞれにモデルを割り当て、いつどのエージェントを使うかのルールを添える。あとはCodexが勝手にやる。お前さんの側の使い方は、いつも通りタスクを投げるだけで変わらない。

# Codexに丸投げする指示文

以下をそのままCodexに貼れ。既存の設定を読んで、3つのエージェントファイルを作り、ルーティングのルールを更新する。 元の指示文に、俺が実際に運用して足りないと感じた3つを追加してある。バックアップ、暴走防止の上限、判断ログだ。

（謎にバグるので、これだけコピペして使ってください。）

```
~/.codex/config.toml の中身を、変更前の状態のまま~/.codex/config.toml.bak として保存しろ。そのあとで、以下の作業に入れ。~/.codex/config.toml と、以下のドキュメントを読み込め。https://developers.openai.com/codex/subagents（カスタムエージェント定義の仕様を確認するため）1. ~/.codex/agents/ 配下に、3つのエージェントTOMLファイルを作れ。fast_scan — 素早い検索、コードベースの調査、ファイルの読み取り、軽い分析専用。- model: gpt-5.6-terra- model_reasoning_effort: high- sandbox_mode: read-only- max_steps: 15- 指示: 証拠を素早く集めて簡潔に要約しろ。ファイルは一切編集するな。routine_worker — 通常のコーディング、テスト、ドキュメント作成、範囲が明確な修正専用。- model: gpt-5.6-sol- model_reasoning_effort: medium- max_steps: 40- 指示: 割り当てられたタスクを実装し、結果を必ず検
