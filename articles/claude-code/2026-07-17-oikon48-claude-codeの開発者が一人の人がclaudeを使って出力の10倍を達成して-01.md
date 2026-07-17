---
id: "2026-07-17-oikon48-claude-codeの開発者が一人の人がclaudeを使って出力の10倍を達成して-01"
title: "@oikon48: Claude Codeの開発者が「一人の人がClaudeを使って出力の10倍を達成しているのに、組織の他の人たちはまだ追"
url: "https://x.com/oikon48/status/2077932711411679404"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "cowork", "x"]
date_published: "2026-07-17"
date_collected: "2026-07-18"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Codeの開発者が「一人の人がClaudeを使って出力の10倍を達成しているのに、組織の他の人たちはまだ追いついていない」という課題に対して回答

AI採用のステップ：

Step 0: Gated

・生産性目安：0〜1倍（ほぼ使えていない）
・状態: AIツールの利用が厳しく制限されている段階。
古いモデルしか使えず、遅延がひどく、セキュリティ承認やガバナンスが追いついていない。
・主なボトルネック: レガシーなセキュリティ承認プロセス、技術者以外の声が意思決定を支配している。
・必要なガードレール: SSO/SCIM + 役割ベースのアクセス制御、組織レベルの予算上限、既存の承認フローの中にデプロイするなど。

→ この段階から抜け出すには：経営層と合意形成し、安全にClaudeを導入するための枠組みを作る。

Step 1: Assisted（あなた＋エージェントのペア）

・生産性目安：〜1倍（まだ個人レベル）
・状態: 1人のエンジニアが1つのエージェントとペアを組んで作業。基本的に「あなたが全部確認」する同期作業。
・主なボトルネック: モデルの出力が信用できず、毎回全部読まないと不安。作業が同期型で時間がかかる。
・役立つ機能: Claude Code（Desktop/CLI/IDE）、Claude Cowork / Design、Analyticsダッシュボード、Compliance API など。
・必要なガードレール: 1人あたりの利用上限、中央管理のモデル設定、OpenTelemetryで既存の監視スタックに連携。

→ 次のステップへ移行するには: 1人で複数エージェントを動かせるようになり、自己検証ループを信頼できる状態にする。

Step 2: Parallel Orchestrator（並列オーケストレーター）

・生産性目安：〜10倍
・状態: 1人のエンジニアが5〜10個のエージェントを同時に動かしている。
・各エージェントが自分のワークツリーでテスト・ビルド・セキュリティスキャンまで自動でやってくれる。
・主なボトルネック: 出力のレビューに時間がかかりすぎる（手動レビューがボトルネック）。
・役立つ機能: Auto mode、Agent view、Claude Code Review、Claude Security Review、Worktree isolation、Remote control（スマホから監視）など。
・必要なガードレール: 自動コードレビュー・セキュリティレビュー、Claudeの品質を保証するためのエンドツーエンド検証、事前承認された安全なコマンドなど。

→ ここが多くのチームが最初に到達する「本当の10x」段階

Step 3: Supervised autonomy（監督付き自律）

・生産性目安：〜100倍
・状態: Claudeがコードのほとんどを書く。
「このコード読んだ？」という質問が「次に何をすればいいか？」に変わる。メンテナンス作業がバックグラウンドで回り始める。
・主なボトルネック: ループ（作業の流れ）への信頼と、トークン使用量の効率的な管理。
・役立つ機能: Subagents + Worktree isolation、Dynamic workflows、Routines /loop /batch、Claude Tagで使用状況監視。
・必要なガードレール: 自動コードレビュー・セキュリティレビュー、Agent sandbox、CLAUDE.mdの整備、トークン使用量のモデル選択による制御。

Step 4: AI-native（AIネイティブ）

・生産性目安：〜1,000倍以上
・状態: ループが完全に閉じていて、ほとんどのエージェントがClaudeによって管理・起動・停止される。人間は「意図（intent）」で指示を出し、例外的な部分だけ監視する。
・主なボトルネック: 大規模なドメイン特化の自動化（コード移行、ファジング、機能開発など）をどう安全にスケールさせるか。
・役立つ機能: Claude Agent SDK、Claude Tag（Slackなどで自動応答）。
・必要なガードレール: 自動化向けのコスト制御、自動化向けのモデル選択。

Claude Artifacts によって表が公開されています：
https://t.co/AHcCFGYx96


--- 引用元 @bcherny ---
I talk to engineers at other companies every day and hear the same thing: one person is 10x'ing their output with
