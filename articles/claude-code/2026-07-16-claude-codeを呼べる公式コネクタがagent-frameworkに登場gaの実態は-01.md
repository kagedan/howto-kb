---
id: "2026-07-16-claude-codeを呼べる公式コネクタがagent-frameworkに登場gaの実態は-01"
title: "Claude Codeを呼べる公式コネクタがAgent Frameworkに登場、GAの実態は？"
url: "https://zenn.dev/kazu_aiengineer/articles/agent-framework-claude-code-connector"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-07-16"
date_collected: "2026-07-18"
summary_by: "auto-rss"
query: ""
---

## 先に結論

* Microsoft Agent Framework に **Claude Code と GitHub Copilot をエージェントの「部下」として呼び出す公式コネクタ**が来た。7/15（米国時間）に [Azure Updates で発表](https://azure.microsoft.com/updates?id=563701)されている
* Claude Code コネクタの実体は **Claude Agent SDK のラッパー**。Claude Code の permission mode・hooks・sandbox・skills までオプションでほぼそのまま扱える
* 発表文には "generally available" とあるが、**PyPI のパッケージは beta / rc、.NET 版の Claude Code コネクタは存在せず、Learn のプロバイダ一覧にも未掲載**（2026-07-17時点）。導入判断はこの差分を踏まえたい

## 何が発表されたか

7/15 の Azure Updates に、Microsoft Agent Framework 関連のアナウンスが1日で9件まとめて流れた。Magentic を含むオーケストレーションパターン、Agent Harness、トレーシング、CodeAct と Hyperlight コンテナ……と盛りだくさんだが、私が真っ先に目を止めたのはこれだ。

> Microsoft Agent Framework now ships generally available connectors for GitHub Copilot and Claude Code, so developers can build .NET and Python agents that delegate coding tasks to either system without writing custom adapter code.
>
> — [Announcing: GitHub Copilot and Claude Code connectors in Microsoft Agent Framework（Azure Updates, 2026-07-15）](https://azure.microsoft.com/updates?id=563701)

要するに、Agent Framework で組んだエージェントから、**コーディングタスクを GitHub Copilot や Claude Code に委譲できる**公式アダプタが出た、という話だ。発表文はさらに「既存の session・middleware・テレメトリ設定を変えずに追加でき、コーディングエージェントのトラフィックも他のエージェントと同じトレースやダッシュボードに乗る」と続く。

面白いことに、この発表に対応する記事は [Agent Framework の公式ブログ](https://devblogs.microsoft.com/agent-framework/)にはまだない（2026-07-17時点。直近の記事は 7/15 の Agent Skills for Python）。Azure Updates 単発の静かなアナウンスだ。

構成としてはこうなる。

## Claude Code コネクタの中身を読む

パッケージは [`agent-framework-claude`](https://pypi.org/project/agent-framework-claude/)。[実装](https://github.com/microsoft/agent-framework/tree/main/python/packages/claude)を読むと、`ClaudeAgent` クラスが Claude Agent SDK の `ClaudeSDKClient` をラップして、Agent Framework 標準の `BaseAgent` インターフェイスに変換している。つまり**裏で動くのはローカルにインストールされた Claude Code CLI そのもの**で、[サンプルコード](https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/providers/anthropic/anthropic_claude_basic.py)の前提条件にも「Claude Code CLI must be installed and configured」と明記されている。

使い方は他のプロバイダと変わらない。

```
from agent_framework import tool
from agent_framework.anthropic import ClaudeAgent

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"The weather in {location} is sunny."

agent = ClaudeAgent(
    name="BasicAgent",
    instructions="You are a helpful assistant.",
    tools=[get_weather],
)

async with agent:
    result = await agent.run("What's the weather in Seattle?")
    print(result.text)
```

読んでいて唸ったのはオプションの網羅ぶりだ。`ClaudeAgentOptions` には Claude Code ユーザーにはおなじみの概念がほぼ全部並んでいる。

| オプション | 内容 |
| --- | --- |
| `permission_mode` | `default` / `acceptEdits` / `plan` / `bypassPermissions` |
| `allowed_tools` / `disallowed_tools` | ツールの許可・拒否リスト（`"Read"`, `"Bash"` 等の組み込みツール名を文字列で渡す） |
| `hooks` | pre/post ツールフック |
| `sandbox` | Bash 実行のサンドボックス設定 |
| `skills` | 有効化する Agent Skills（`"all"` / 名前リスト / `[]`） |
| `plugins` / `setting_sources` | プラグインと settings ファイル（user / project / local）の読み込み制御 |
| `max_budget_usd` / `max_turns` | 予算・ターン数の上限 |
| `enable_file_checkpointing` | ファイル変更の巻き戻し用チェックポイント |
| `session_id` / `fork_session` / `continue_conversation` | セッションの継続・フォーク |

`~/.claude` に育てた設定・skills・hooks の資産を、業務エージェントのワークフローからそのまま使える設計になっている。昨日書いた [Agent Skills の standalone 対応](https://zenn.dev/kazu_aiengineer/articles/agent-framework-skills-stable)と合わせると、Microsoft が「Claude Code エコシステムとの相互運用」に本気で寄せてきているのがわかる。

実装面で押さえておきたい挙動が2つある。

**1. カスタムツールは in-process MCP サーバー経由で渡る**

Claude Code CLI は外部ツールを MCP 経由でしか受け付けないため、コネクタは `@tool` で渡した Python 関数を SDK の MCP ツールに変換し、`_agent_framework_tools` という名前のインプロセス MCP サーバーとして Claude 側に見せる。[ソースコードのコメント](https://github.com/microsoft/agent-framework/blob/main/python/packages/claude/agent_framework_claude/_agent.py)に理由まで書かれていて読みやすい。

**2. 承認必須ツールはデフォルト拒否**

`approval_mode="always_require"` を付けたツールは、承認コールバック（`on_function_approval`）を設定しない限り**デフォルトで実行拒否**される。Claude Agent SDK が自前のツール実行ループを持つため、Agent Framework 標準の承認ラウンドトリップが使えず、代わりにエージェントレベルの強制ポイントを置いた——という設計判断だ。コールバックが例外を投げた場合も拒否に倒れる。secure-by-default が徹底している。

## GitHub Copilot コネクタも同じ構図

[`agent-framework-github-copilot`](https://pypi.org/project/agent-framework-github-copilot/) は `github-copilot-sdk`（1.0.2 固定）のラッパーで、`GitHubCopilotAgent` として使う。こちらは依存パッケージの都合で **Python 3.11 以上が必要**（コネクタ自体の `requires-python` は 3.10+ だが、SDK 依存が `python_version >= '3.11'` 条件付き）。

承認モデルは Claude 版と思想は同じで実装が異なる。Copilot SDK ネイティブの `on_pre_tool_use` フックが承認必須ツールに `"ask"` を返し、`on_permission_request` ハンドラに委ねる二段構え。[README](https://github.com/microsoft/agent-framework/tree/main/python/packages/github_copilot) には「自前の `on_pre_tool_use` を渡した場合は承認の全責任がユーザー側に移る」という警告と、旧 `on_function_approval` の非推奨化まで書かれている。この辺りのドキュメント密度は、リリースに向けた整備が進んでいる印象を受けた。

## "generally available" の実態を確かめる

さて本題。発表文の "generally available connectors" を額面通り受け取ってよいか、パッケージレジストリと公式ドキュメントを一つずつ確認した。

| 確認対象 | 2026-07-17 時点の状態 |
| --- | --- |
| PyPI `agent-framework-claude` | **1.0.0b260709（beta）**。classifier も `Development Status :: 4 - Beta`、[README](https://github.com/microsoft/agent-framework/tree/main/python/packages/claude) のインストール手順は `pip install agent-framework-claude --pre` |
| PyPI `agent-framework-github-copilot` | **1.0.0rc3（release candidate）**。classifier は同じく Beta |
| NuGet `Microsoft.Agents.AI.GitHub.Copilot` | **1.13.0-rc1**（安定版なし） |
| .NET の Claude Code コネクタ | **リポジトリの main ブランチに存在しない**。あるのは Claude *モデル* を API で呼ぶ `Microsoft.Agents.AI.Anthropic`（1.13.0-preview）のみ |
| Learn の [Providers Overview](https://learn.microsoft.com/en-us/agent-framework/agents/providers/)（7/10更新） | GitHub Copilot は掲載あり、**Claude Code コネクタは未掲載**。`/agents/providers/claude` は 404 |

発表は「.NET と Python のエージェントからどちらにも委譲できる」と読めるが、Claude Code への委譲を今日できるのは Python だけ、それも `--pre` 付きインストールのプレリリース版だ。GitHub Copilot 側は rc まで来ているので、正式リリースは近そうではある。

## 既存の Anthropic プロバイダと混同しやすい

紛らわしいことに、Agent Framework には Claude 関連のパッケージが2系統ある。インポートパスがどちらも `agent_framework.anthropic` 配下なので、名前だけ見ると区別がつかない。

|  | `agent-framework-anthropic` | `agent-framework-claude`（今回の主役） |
| --- | --- | --- |
| 何を呼ぶか | Claude **モデル**（Messages API） | **Claude Code**（Claude Agent SDK → CLI） |
| クラス | `AnthropicClient` | `ClaudeAgent` |
| 認証 | `ANTHROPIC_API_KEY`（Foundry 経由も可） | ローカルの Claude Code CLI の認証に従う |
| ツール実行 | フレームワーク側のループで実行 | Claude Code 側のループで実行（ファイル編集・Bash 等の組み込みツール込み） |
| 向いている用途 | チャット・推論・hosted tools | コーディングタスクの委譲、`~/.claude` 資産の再利用 |
| Learn ドキュメント | [あり](https://learn.microsoft.com/en-us/agent-framework/agents/providers/anthropic) | 専用ページなし（2026-07-17時点） |

「Claude をエージェントの頭脳にする」のが anthropic パッケージ、「Claude Code をエージェントの手足にする」のが claude パッケージ、と覚えるのがわかりやすいと思う。

## どう受け止めたか

マルチエージェント構成の中に「コーディング担当」として Claude Code を置く、というのは私自身欲しかったピースだ。オーケストレーターは Foundry の安いモデルで回し、コード生成・リファクタだけ Claude Code に投げる——という役割分担が、自前アダプタなしで組めるようになる。発表文の「テレメトリに乗る」も地味に重要で、コーディングエージェントの挙動が他のエージェントと同じ観測基盤で追えるのは運用側には効く。

一方で、beta パッケージである以上 API はまだ動く可能性があるし、Claude Code CLI をホストに置く前提なので、サーバーサイドで使うにはインストールと認証の設計が別途必要になる。まずはローカルのオーケストレーション実験から試すのが現実的だろう。私も次は実際に動かして、委譲まわりの挙動とハマりどころを確かめたい。

## 参考リンク（一次ソース）
