---
id: "2026-07-13-makeai-ceo-httpstcolzfnrqh821-01"
title: "@MakeAI_CEO: https://t.co/LzfNrQh821"
url: "https://x.com/MakeAI_CEO/status/2076548451790434766"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "OpenAI"]
date_published: "2026-07-13"
date_collected: "2026-07-14"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/LzfNrQh821


--- Article ---
Claude Fable 5の追加料金なしで使える期間は、当初2026年7月7日までと案内され、その後7月12日、さらに7月19日まで延長された。Claude Codeの週間利用上限が50％増える施策も、同じく7月19日まで継続される。

つまり、Fable 5が今すぐ消えるわけではない。

しかし、Fable 5を月額プランの範囲内で当然のように使い続けられる状況が、恒久的に保証されたわけでもない。元の案内では期間終了後にusage creditsへ移行するとされており、API価格も入力100万トークン当たり10ドル、出力100万トークン当たり50ドルだ。

終わろうとしているのはFable 5そのものではなく、**最高性能モデルを月額料金だけで無制限に近い感覚で使える時代**なのだ。

では、Claude Codeを捨てて、OpenAIのCodexへ全面移行するべきなのか。

結論から言えば、その必要はない。

Claude Codeのターミナル体験、既存のCLAUDE.md、Hooks、MCP、Skills、権限設定を残したまま、難しい作業だけをGPT-5.6 Solへ渡せばいい。

しかも、怪しいプロキシサービスや非公式なAPI互換レイヤーを使う必要はない。

OpenAI自身が、Claude Codeの中からCodexを呼び出すための公式プラグインを公開している。

ここで作るのは、「ClaudeをGPT-5.6に変身させる仕組み」ではない。

Claude Codeを司令塔として残し、GPT-5.6 Solを第二の思考エンジンとして接続する**二脳構成**だ。

Claudeはユーザーとの会話、リポジトリ探索、小さな編集、既存パターンへの追従を担当する。

GPT-5.6 Solは、複雑な設計判断、解決しない不具合、敵対的レビュー、複数コンポーネントにまたがる変更、出荷前のセカンドオピニオンを担当する。

さらに、日本語の運用プロンプトをAgent Skillとして置き、どちらのモデルにも同じ完了条件、検証基準、変更範囲を守らせる。

これが、Claude Codeに「ChatGPT 5.6の頭脳」を与える、最も現実的な方法である。

なお、セットアップやガチの活用術はPDFにまとめてます。

欲しい人は、この👇から受け取れるようにしてます！

[https://x.com/MakeAI_CEO/status/2027682940847898770?s=20](https://x.com/MakeAI_CEO/status/2027682940847898770?s=20)

## Claude CodeにGPT-5.6の頭脳を与える3つのレイヤー

最初に区別したいのは、プロンプトをコピーすることと、実際のモデルへ接続することは別だという点だ。

CLAUDE.mdにGPT-5.6向けの指示を書いても、ClaudeのモデルそのものがGPT-5.6へ変わるわけではない。

変わるのは仕事の進め方である。

これを**行動レイヤー**と呼ぶ。

次に、OpenAI公式の「Codex plugin for Claude Code」を導入する。

このプラグインを使うと、Claude Codeの中から、ローカル環境にインストールされたCodex CLIとCodex app serverを通じて、Codexへコードレビューや実装作業を委譲できる。

これが**推論・実行レイヤー**だ。

最後に「OpenAI Developers plugin」を導入する。

こちらにはOpenAIの公式ドキュメントを参照するDocs MCPと、OpenAI API、Agents SDK、ChatGPT Apps、APIキー設定、トラブルシューティングなどに対応するSkillsが含まれている。

これが**知識レイヤー**である。

この3つを重ねる。

行動レイヤー
日本語の運用プロンプトとAgent Skill

推論・実行レイヤー
Codex plugin for Claude Code

知識レイヤー
OpenAI Developers pluginと公式Docs MCP

こうすると、普段の操作はClaude Codeのまま、必要なときだけGPT-5.6 SolとOpenAIの最新ドキュメントを呼び出せる。

## まずはOpenAI公式のCodexプラグインを入れる

導入に必要なのは、ChatGPTアカウントまたはOpenAI APIキー、Node.js 18.18以降、そしてCodex CLIだ。

このプラグインは、どこかの非公式サービス
