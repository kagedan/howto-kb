---
id: "2026-07-10-oss-zukan-これclaude-codeを入れて終わりにしてる人に刺さる話-インストールは一番-01"
title: "@oss_zukan: これ、Claude Codeを「入れて終わり」にしてる人に刺さる話。 インストールは一番小さい仕事。本命はCLIの“周"
url: "https://x.com/oss_zukan/status/2075692374798610630"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "x"]
date_published: "2026-07-10"
date_collected: "2026-07-12"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

これ、Claude Codeを「入れて終わり」にしてる人に刺さる話。

インストールは一番小さい仕事。本命はCLIの“周り”に積む設定の面。

skills / hooks / subagents / MCPサーバー / ワークフローYAML / カナリア——この面(surface)が、素のチャット窓を「毎回同じ手順で動く開発環境」に変える。しかも一式をGitHubで管理。

何をどう積むか、順番に噛み砕きます👇

まず“ワークスペース”って何？

Claude Code本体(CLI)は、賢いけど記憶を持たない新人みたいなもの。毎回ゼロから指示すると疲れます。

そこで .claude/ フォルダに「この現場のやり方」を置く。CLAUDE.md(常時読む共通ルール)、skills(反復手順のレシピ)、subagents(専任の分身)を用意すると、新人が毎回“研修済み”で動き出す。

この置き場ごとGitHubに載せる＝チームで同じ環境を共有・再現できる、が肝です。

次に、なぜ“チャット窓”が“開発環境”に化けるのか。

鍵はhooksとMCP、そしてカナリア。
・hooks＝モデルの気分に関係なく必ず走るシェル。編集後に自動整形、コミット前にlint、と手順を強制できる。
・MCPサーバー＝Jira/Slack/社内DBなど外部ツールへの差込口。
・カナリア＝異常を先に鳴らす見張り番。

skills(何をやるか)にhooks(必ずやる保証)が噛み合うと、“賢いけど気まぐれ”が“手順どおり”に変わります。

効くのは、例えばこんな時。

・新メンバーがcloneした瞬間、同じskills/hooksが効いて即戦力になる
・PRレビューやデプロイ手順が“口伝”じゃなくコードとして残る
・モデルを差し替えても、周りの設定はそのまま資産になる

落とし穴も一つ。hooksは任意のコマンドを実行する＝「設定」ではなく「コード」。他人の.claudeを丸ごと信用せず中身を読む、が鉄則です。

まとめると——“入れる”は入口、“周りを組む”が本番。設定はGitHubで資産になる。
