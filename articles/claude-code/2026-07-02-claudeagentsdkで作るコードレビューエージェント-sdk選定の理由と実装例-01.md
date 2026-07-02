---
id: "2026-07-02-claudeagentsdkで作るコードレビューエージェント-sdk選定の理由と実装例-01"
title: "ClaudeAgentSDKで作るコードレビューエージェント — SDK選定の理由と実装例"
url: "https://qiita.com/renly/items/d82fb9913db58e5199e1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

ClaudeAgentSDKは、Anthropicが提供するエージェント実行SDK（Python: `claude-agent-sdk` / TypeScript: `@anthropic-ai/claude-agent-sdk`）です。Claude Codeのエンジンを切り出したものであり、`query()` 関数1つでエージェントループを実行できます。

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="リポジトリの依存関係を最新化して",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"])
):
    print(message)
```

このSDKには「Claudeモデルでしか得られない利点」がいくつかあります。本記事ではAnthropic Client SDKとの比較を軸に整理します。

---

## ClaudeAgentSDK vs Anthropic Client SDK

同じAnthropicから提供されていますが、設計思想が大きく異なります。

| | ClaudeAgentSDK | Anthropic Client SDK |
|---|---|---|
| パッケージ | `claude-agent-sdk` | `anthropic` |
| 抽象レベル | 高（エージェントループ込み） | 低（HTTPクライアント） |
| ツールループ | **自動**（組み込みエージェントループ） | **自前実装**が必要 |
| ビルトインツール | bash, Read, Write, Edit, Glob, Grep | なし |
| Extended Thinking | `effort="high"` 1パラメータ | `thinking: { budget_tokens: N }` で細かく制御 |
| システムプロンプト | `claude_code` プリセットあり（デフォルト） | 完全自由記述 |
| MCP | `mcp_servers` + Tool Search | `mcp_servers`（Tool Searchなし） |
| サブエージェント | AgentDefinition / `.claude/agents/*.md` | なし（自前実装） |

ClaudeAgentSDKは「エージェントループをすぐに使いたい」場合、Anthropic Client SDKは「APIを細かく制御したい」場合に向きます。

---

## 利点① ツール訓練の一致

ClaudeAgentSDKが提供するビルトインツール（`bash`・`Read`・`Write`・`Edit`・`Glob`・`Grep`）は、Claude Codeのツールセットそのものです。

Claudeモデルはこれらのツールを使って大量にトレーニングされており、**ツール定義とモデルの学習データが一致**しています。

```
Anthropic Client SDKの場合:
  カスタムfunction_call → Claudeはこのツールの使い方を学習していない
  → 推論で補う必要がある

ClaudeAgentSDKの場合:
  bash / Read / Edit → Claudeが最も多く訓練されたツール定義
  → 最短パスで正しいツール呼び出しが出る
```

---

## 利点② Extended Thinking の直接制御

Claude 3.7以降が持つExtended Thinking（拡張思考）を、`effort`パラメータで簡潔に制御できます。

```python
ClaudeAgentOptions(
    effort="high"  # "low" | "normal" | "high"
)
```

| effort | 内容 |
|---|---|
| `low` | 標準的な思考（高速・低コスト） |
| `normal` | バランス型 |
| `high` | 最大思考予算（複雑な推論・設計タスクに） |

Anthropic Client SDKでは `thinking: { type: "enabled", budget_tokens: N }` としてトークン数まで細かく制御できますが、ツールループは自前実装が必要です。ClaudeAgentSDKでは「難所タスクだけ `effort="high"` に上げる」という設計が1行で実現できます。

---

## 利点③ `claude_code` システムプロンプトプリセット

ClaudeAgentSDKには `system_prompt` プリセットとして `claude_code` が用意されています。

```python
ClaudeAgentOptions(
    system_prompt="claude_code"  # デフォルト値
)
```

このプリセットはClaudeの訓練時のシステムプロンプトと一致しており、モデルが最も自然にツールを活用するよう設計されています。

- カスタムSPに変更すると既存の訓練プロファイルから外れる
- 拡張する場合は `append_system_prompt` で追記する形が推奨

Anthropic Client SDKにはこの概念はなく、システムプロンプトは完全に自由記述です。

---

## 利点④ MCP策定元による深いネイティブ統合

MCPはAnthropicが設計したオープン標準プロトコルです。ClaudeAgentSDKはその策定元のSDKであり、MCPサポートが最も深い実装です。

```python
ClaudeAgentOptions(
    mcp_servers=[
        {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
        }
    ]
)
```

### Tool Search（ClaudeAgentSDKのみの機能）

MCPサーバーが多数のツールを提供する場合、**各ターンにタスク関連ツールだけを動的ロード**するTool Search機能がデフォルトで有効です。

```
通常:
  全MCPツール定義 → コンテキスト圧迫

Tool Search有効時:
  タスクに必要なツールだけ → トークン節約 + 精度向上
```

Anthropic Client SDKも `mcp_servers` パラメータを持ちますが、Tool Searchに相当する機能はありません。

---

## 利点⑤ auto パーミッションモード

ClaudeAgentSDKのパーミッションモードはリスクレベルに応じた5段階です。

| モード | 動作 |
|---|---|
| `default` | 標準的な確認動作 |
| `acceptEdits` | ファイル編集は自動承認 |
| `autoEdit` | 編集+作成を自動承認 |
| `auto` | **Claudeの分類器が承認判断** |
| `dontAsk` | 全操作を自動承認 |

`auto` モードが特徴的で、Claudeモデル自身がリスク分類器として機能します。単純な「全許可」ではなく、タスクの性質に応じた動的判断です。

---

## サブエージェント定義の柔軟性

ClaudeAgentSDKはサブエージェントを3つの方法で定義できます。

### ① プログラム定義（推奨）

```python
ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Agent"],
    agents={
        "code-reviewer": AgentDefinition(
            description="セキュリティ・品質観点でコードレビューする専門家",
            prompt="You are a strict code reviewer...",
            tools=["Read", "Grep"],
            model="claude-opus-4-5",  # 子エージェントだけ高性能モデルに
            effort="high",
            permissionMode="dontAsk",
        )
    }
)
```

- 各サブエージェントに異なる `model`・`effort`・`permissionMode` を割り当て可能
- ランタイムで動的生成も可能

### ② ファイルシステム定義（`.claude/agents/*.md`）

Claude Codeと同形式のMarkdownファイルで定義します。

```markdown
# code-reviewer
description: セキュリティ・品質観点でコードレビューする専門家
tools: Read, Grep
model: claude-opus-4-5
effort: high

You are a strict code reviewer...
```

Windowsではプロンプトが長い場合にCLI長制限（8191文字）に当たるため、こちらが推奨されることもあります。

### ③ ビルトイン general-purpose

定義不要で、Claudeが必要と判断した場合に自律起動するサブエージェントです。

サブエージェントは**最大5階層**までネスト可能（v2.1.172以降）で、数十〜数百エージェントを扱う場合は `Workflow` ツール（TypeScript v0.3.149以降）が利用できます。

---

## AutoGen との比較：動的 vs 静的オーケストレーション

| | ClaudeAgentSDK | AutoGen |
|---|---|---|
| オーケストレーション主体 | **Claude（モデルが判断）** | **開発者（コードで設計）** |
| トポロジー | 階層型（最大5段ネスト） | フラット協調型（Graph, Swarm, Selector） |
| エージェント起動 | descriptionを見てClaudeが自律判断 | SelectorChat・GraphFlowで明示指定 |
| コード実行 | 組み込みbash（Docker不要） | Docker必須 |
| LLM依存 | Claude専用 | LLM非依存 |

フローが「事前にわかる」タスクにはAutoGenが向き、「何手かかるか実行前に不明」なタスクにはClaudeAgentSDKが向きます。

---

## 用途例：コードレビューエージェント

コードレビューはGitHub Copilotのようなツールでも実行できます。しかし**自前でコードを組む**ことで、ツールでは届かないカスタマイズが可能になります。

- チーム固有のコーディング規約をプロンプトに組み込む
- セキュリティ・パフォーマンス・可読性など観点ごとにサブエージェントを分ける
- レビュー結果を社内システム（Jira・Slack・独自DB）へ直接連携する
- `effort` をファイルの重要度に応じて動的に変える

### MCP でJVNデータベースをツールとして追加

セキュリティレビューでは、コードに含まれるライブラリの既知脆弱性を [JVN iPedia](https://jvndb.jvn.jp/)（Japan Vulnerability Notes）で照合したいケースがあります。MCPサーバーとして `mcp-server-fetch` を追加することで、ClaudeがJVN APIを自律的に呼び出せるようになります。

```python
mcp_servers=[
    {
        "type": "stdio",
        "command": "uvx",           # 公式推奨の起動方法
        "args": ["mcp-server-fetch"],
        "name": "jvn",
    }
]
```

:::message alert
`mcp-server-fetch` は汎用HTTPフェッチツールであり、アクセス先ドメインの制限機能は現時点の公式オプションでは提供されていません（`--ignore-robots-txt`・`--user-agent`・`--proxy-url` が主なオプション）。本番運用では、プロキシでアクセス先を限定するか、JVN専用MCPサーバーを自作することを推奨します。
:::

### Skill でJVN照合の手順を定義

MCPツールの使い方をエージェントに教えるSkillを `.claude/skills/jvn-lookup/SKILL.md` に定義します。

```markdown
---
name: jvn-lookup
description: JVN iPediaで既知の脆弱性情報を検索する手順
---

# JVN脆弱性照合スキル

コードで使用しているライブラリとバージョンを特定したら、
JVN iPedia APIで既知脆弱性を照合してください。

## APIエンドポイント

GET https://jvndb.jvn.jp/apis/myjvn/?method=getVulnOverviewList&keyword={ライブラリ名}

## 照合手順

1. Grep で requirements.txt / package.json / pom.xml を確認してライブラリ一覧を取得
2. 使用バージョンを特定
3. JVN API にキーワード検索（ライブラリ名）
4. CVSSスコアと影響バージョン範囲を確認
5. 影響がある場合は修正推奨バージョンとともに報告
```

### 全体の実装例

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob", "Agent"],
    effort="normal",
    system_prompt="claude_code",
    append_system_prompt="""
    レビュー時は以下の社内規約を必ず確認してください:
    - 全ての公開関数にdocstringが必要
    - SQLクエリは必ずパラメータバインディングを使用
    - ログに個人情報を含めない
    """,
    mcp_servers=[
        {
            "type": "stdio",
            "command": "uvx",
            "args": ["mcp-server-fetch"],
            "name": "jvn",
        }
    ],
    agents={
        "security-reviewer": AgentDefinition(
            description="セキュリティ脆弱性（インジェクション・認証・情報露出）を専門にレビューする。必要に応じてJVNで既知脆弱性を照合する",
            tools=["Read", "Grep"],
            # MCPツールはサーバー接続後に自動公開される
            # 実際のツール名は起動ログまたはMCP Inspectorで確認する
            effort="high",       # セキュリティ観点だけ拡張思考を使う
            skills=["jvn-lookup"],
        ),
        "performance-reviewer": AgentDefinition(
            description="N+1クエリ・不要なループ・メモリリークなどパフォーマンス問題を検出する",
            tools=["Read", "Grep"],
        ),
    }
)

async def main():
    async for msg in query(
        prompt="PR #142 の変更ファイルをレビューしてください。",
        options=options
    ):
        print(msg)

asyncio.run(main())
```

:::message
MCPツール名（例: `fetch`）は接続するサーバーの実装によって変わります。利用可能なツール一覧は `npx @modelcontextprotocol/inspector uvx mcp-server-fetch` で確認できます。
:::

`security-reviewer` は `jvn-lookup` Skillを持っているため、依存ライブラリを発見した際に自律的にJVN APIを照合し、CVSSスコア付きで報告します。

---

## まとめ

ClaudeAgentSDKとAnthropic Client SDKはどちらを選ぶべきか、判断軸を整理します。

| 条件 | 推奨 |
|---|---|
| エージェントループをすぐ使いたい | **ClaudeAgentSDK** |
| Extended Thinkingを使いたい | **ClaudeAgentSDK** |
| MCPをTool Search付きで活用したい | **ClaudeAgentSDK** |
| サブエージェントで役割分担したい | **ClaudeAgentSDK** |
| APIレベルで細かく制御したい | Anthropic Client SDK |
| トークン予算をバイト単位で管理したい | Anthropic Client SDK |

ClaudeAgentSDKはClaude専用という制約があります。しかしその制約によって「訓練データとの一致」「Extended Thinkingの直接制御」「MCP策定元としての深い統合」という固有の利点が生まれています。**Claudeで複雑なタスクを自律実行させたい場合のファーストチョイス**として位置づけることができます。
