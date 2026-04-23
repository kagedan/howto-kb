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
                        構造化レポート -> Claude Code に返却
                        ```

                        ポイントは**Codex CLIが出力するJSONLイベントストリームを全解析**し、ツール呼び出し・ファイル操作・エラーを構造化レポートに変換する点です。

                        ## 前提条件

                        | 要件 | バージョン |
                        |------|-----------|
                        | Python | 3.12以上 |
                        | Node.js | 18以上 |
                        | uv | 最新版推奨 |
                        | OpenAIアカウント | Codex CLI認証用 |

                        ## Step 1: Codex CLIのインストールと認証

                        ```bash
                        npm install -g @openai/codex
                        codex login
                        ```

                        ## Step 2: claude-code-codex-agentsのインストール

                        ```bash
                        git clone https://github.com/tsunamayo7/claude-code-codex-agents.git
                        cd claude-code-codex-agents
                        uv sync
                        ```

                        ## Step 3: MCPクライアントへの登録

                        `~/.claude/settings.json` に以下を追加:

                        ```json
                        {
                          "mcpServers": {
                              "claude-code-codex-agents": {
                                    "type": "stdio",
                                          "command": "uv",
                                                "args": ["run", "--directory", "/path/to/claude-code-codex-agents", "python", "server.py"],
                                                      "env": { "PYTHONUTF8": "1" }
                                                          }
                                                            }
                                                            }
                                                            ```

                                                            ## Step 4: 利用可能なツール一覧

                                                            | ツール | 用途 | サンドボックス |
                                                            |--------|------|---------------|
                                                            | execute | タスクをCodexに委譲し構造化レポートを取得 | workspace-write |
                                                            | trace_execute | execute+全イベントタイムライン付き | workspace-write |
                                                            | parallel_execute | 最大6タスクを同時並列実行 | read-only |
                                                            | review | GPT-5.4によるコードレビュー | read-only |
                                                            | explain | コード解説（brief/medium/detailed） | read-only |
                                                            | generate | コード生成 | workspace-write |
                                                            | discuss | GPT-5.4の見解を取得 | read-only |
                                                            | session_continue | 前回スレッドを引き継いで継続 | workspace-write |
                                                            | session_list | セッション履歴の一覧表示 | - |
                                                            | status | Codex CLIの状態と認証確認 | - |

                                                            ## Step 5: 実際に使ってみる

                                                            ### 基本的なタスク委譲（execute）

                                                            ```
                                                            [Codex gpt-5.4] Completed
                                                            Execution time: 8.3s
                                                            Thread: 019d436e-4c39-7093-b7ed-f8a26aca7938

                                                            Tools used (3):
                                                              read_file -- src/auth.py
                                                                edit_file -- src/auth.py
                                                                  shell -- python -m pytest tests```
                                                                  Files touched (1):
                                                                    src/auth.py
                                                                    ```

                                                                    ### Adversarial Review（review）

                                                                    ```
                                                                    [Codex Review] GPT-5.4 Review Result
                                                                    Execution time: 15.7s

                                                                    - [CRITICAL] os.system(cmd) -- command injection
                                                                    - - [WARNING] ZeroDivisionError when b == 0
                                                                    - - [INFO] No type hints on function signatures
                                                                    - ```

異なるモデルが異なる視点でレビューするため、**単一モデルの盲点を補完**できます。

## セキュリティモデル

| モード | ファイル書き込み | シェル実行 | 用途 |
|--------|-----------------|-----------|------|
| read-only | ブロック | ブロック | review, explain |
| workspace-write | CWDのみ | 許可 | execute, generate |
| danger-full-access | どこでも | 許可 | フルアクセス |

ANSI/OSCエスケープシーケンスのサニタイズ（ターミナルインジェクション防止）も実装済みです。

## まとめ

- **インストール**: git clone + uv sync で完結
- - **単一ファイル構成**: server.py（約820行）のみ
- - **56テスト**: パース、セキュリティ、セッション管理をカバー

リポジトリ: https://github.com/tsunamayo7/claude-code-codex-agents
ライセンス: MIT
```
