---
id: "2026-03-31-mcpで異なるaiモデルを連携させる実践ガイド-claude-code-codex-cli-gpt-01"
title: "MCPで異なるAIモデルを連携させる実践ガイド — Claude Code × Codex CLI (GPT-5.4)"
url: "https://qiita.com/tsunamayo7/items/545a21a13f3b758a7d70"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "GPT"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

## はじめに

Claude Code（Opus 4.6）とOpenAI Codex CLI（GPT-5.4）を**MCPプロトコル**で連携させると、単一モデルでは得られない実用的なワークフローが実現できます。

本記事では、**claude-code-codex-agents**というMCPサーバーを使って、Claude CodeからGPT-5.4にタスクを委譲し、構造化された実行レポートを受け取る方法をハンズオンで解説します。

## アーキテクチャ

```
Claude Code (Opus 4.6)
    | MCP Protocol
        v
        claude-code-codex-agents (MCPサーバー)
            | subprocess + stdin
                v
                Codex CLI -> OpenAI API (GPT-5.4)
                    | JSONL event stream
                        v
