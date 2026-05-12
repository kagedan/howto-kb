---
id: "2026-05-11-claude-agent-sdk-入門python-30行で自分だけのaiエージェントを作る-01"
title: "Claude Agent SDK 入門：Python 30行で自分だけのAIエージェントを作る"
url: "https://zenn.dev/yokotaro/articles/af304f93110b90"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "GPT", "Python"]
date_published: "2026-05-11"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

「AIエージェントを作りたいけど、LangChainは複雑すぎる」「ChatGPT APIは使えるけど、ファイル操作や検索を自分で全部実装するのが面倒」——そう感じたことはないだろうか。

Claude Agent SDK は、そのボトルネックを根本から解決する。`pip install claude-agent-sdk` の1行で、ファイル読み書き・コマンド実行・Web検索といったツール群が使えるエージェントループを手に入れられる。Anthropic 社が 2026年に Claude Code SDK から改名してリリースした本 SDK は、2026年5月時点で GitHub Stars が 22,000 を超え、週間 npm ダウンロードが 110,000 を超えるほど急成長している。

この記事では、**ローカル環境で最初のエージェントを動かすところまで**を Python コードで段階的に解説する。所要時間は環境構築込みで30分程度だ。

---

## Claude Agent SDK とは何か

### Claude Code との関係

Claude Agent SDK は、AI コーディング支援ツール「Claude Code」の実行エンジンを Python / TypeScript ライブラリとして切り出したものだ。つまり、日頃 Claude Code を使っているなら、**その裏側で動いているのと同じツール群とエージェントループ**をそのまま自分のアプリに組み込める。

2026年3月に「Claude Code SDK」から現在の「Claude Agent SDK」へ名称が変更された。移行ガイドも公式に提供されているため、旧バージョンのユーザーは[移行ガイド](https://code.claude.com/docs/ja/agent-sdk/migration-guide)を参照してほしい。

### 他のフレームワークとの違い

| 比較対象 | Claude Agent SDK | LangChain / LlamaIndex |
| --- | --- | --- |
| ツール実装 | 組み込み済み（Read・Edit・Bash・WebSearch など10種以上） | 自前でツールを定義・実装 |
| エージェントループ | SDK が自動管理 | 自分でループ・リトライを実装 |
| 学習コスト | 低（関数1つで動く） | 中〜高（抽象レイヤーが多い） |
| モデル選択 | Claude 専用 | マルチモデル対応 |

LangChain はマルチモデル対応の汎用性が強みだが、ツール実行ループをすべて自分で実装する必要がある。Claude Agent SDK は Claude 専用の代わりに、**ツール実行を SDK が自律的に処理する**点が最大の差別化要素だ。

### Anthropic Client SDK との違い

同じく Anthropic が提供する Client SDK（`anthropic` パッケージ）は直接の API アクセスを提供する。比べると違いが明確だ。

```
# Client SDK: ツールループを自分で実装する必要がある
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# Agent SDK: Claude がツールを自律的に処理する
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

「Claude にツールを使って自律的に仕事をさせたい」なら Agent SDK、「APIレスポンスをきめ細かく制御したい」なら Client SDK が適している。

---

## 環境構築（5分）

### 前提条件

* Python 3.10 以上
* Anthropic アカウント（[無料登録](https://platform.claude.com/)）
* API キー

### インストール

```
# 仮想環境を作成（推奨）
python3 -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows コマンドプロンプト
.venv\Scripts\activate.bat

# SDK をインストール
pip install claude-agent-sdk
```

`uv` を使っている場合は `uv add claude-agent-sdk` でも可。Claude Code バイナリは SDK に同梱されているため、別途インストール不要だ。

### API キーの設定

[Claude Console](https://platform.claude.com/) でキーを発行し、環境変数に設定する。

```
# Linux / macOS
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxx"
```

プロジェクトフォルダに `.env` ファイルを作って書いておく方法も使いやすい。

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

---

## Hello Agent：30行で動く最小エージェント

まず「現在のディレクトリにあるファイルを列挙する」だけの最小エージェントを動かしてみよう。

```
# agent_hello.py
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="このディレクトリにあるファイルを一覧表示して、各ファイルの役割を簡単に説明してください。",
        options=ClaudeAgentOptions(
            allowed_tools=["Bash", "Glob", "Read"],
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

`python3 agent_hello.py` で実行すると、Claude がディレクトリを探索し、ファイルの役割まで説明した結果が返ってくる。

### コードの3つのポイント

**1. `query` 関数がエージェントループのエントリーポイント**

`query()` は非同期ジェネレータを返す。`async for` でメッセージをストリーミング受信しながら、Claude が思考・ツール呼び出し・結果観察を繰り返す。ループが終了するのは Claude がタスクを完了したか、エラーが発生したときだ。

**2. `ClaudeAgentOptions` でエージェントを設定する**

`allowed_tools` に渡したツールだけを Claude が使用できる。主要な組み込みツールは以下の通り。

| ツール | できること |
| --- | --- |
| `Read` | ファイルの読み取り |
| `Write` | 新規ファイルの作成 |
| `Edit` | 既存ファイルの編集 |
| `Bash` | ターミナルコマンド実行 |
| `Glob` | パターンでファイル検索 |
| `Grep` | 正規表現でファイル内容検索 |
| `WebSearch` | Web 検索 |
| `WebFetch` | Web ページ取得・解析 |

**3. メッセージのフィルタリング**

`hasattr(message, "result")` で最終結果だけを拾っている。フィルタリングしないと、Claude の思考過程やツール呼び出しの中間メッセージも流れてくる（デバッグには便利）。

---

## バグ修正エージェント：ファイルの読み書きを自動化

次に、**ファイルを読んでバグを修正する**エージェントを作る。これが公式クイックスタートでも紹介されている基本パターンだ。

まず、バグを仕込んだテスト用ファイルを用意する。

```
# utils.py（バグ入り）
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)  # Bug: リストが空のとき ZeroDivisionError

def get_user_name(user):
    return user["name"].upper()  # Bug: user が None のとき TypeError
```

次に、このファイルを自動修正するエージェントを書く。

```
# agent_bugfix.py
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    print("バグ修正エージェントを起動...")

    async for message in query(
        prompt=(
            "utils.py を読んでクラッシュの原因になるバグを全て見つけ、"
            "防御的なエラーハンドリングを追加して修正してください。"
        ),
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",  # ファイル編集を自動承認
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text") and block.text:
                    print(block.text)        # Claude の思考・説明
                elif hasattr(block, "name"):
                    print(f"[Tool] {block.name}")  # 呼び出したツール名
        elif isinstance(message, ResultMessage):
            print(f"\n完了: {message.subtype}")

asyncio.run(main())
```

実行すると、Claude は `utils.py` を読み、2つのバグを発見し、ゼロ除算と None チェックを自動で追加する。**自分でコードを書かずに、自然言語の指示だけでファイルが修正される。**

### `permission_mode` の選択

| モード | 挙動 | 用途 |
| --- | --- | --- |
| `acceptEdits` | ファイル編集・一般的なコマンドを自動承認 | 開発ワークフロー |
| `dontAsk` | `allowed_tools` 外はすべて拒否 | ヘッドレスエージェント |
| `bypassPermissions` | すべてのツールを無条件実行 | サンドボックス CI |

---

## サブエージェントでマルチエージェント構成にする

Claude Agent SDK のもっとも強力な機能の一つが、**サブエージェントの定義と呼び出し**だ。専門特化したエージェントを組み合わせることで、より複雑なタスクを分業処理できる。

```
# agent_multi.py
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ResultMessage

async def main():
    async for message in query(
        prompt="code-reviewer エージェントを使って、このコードベースの品質とセキュリティを確認してください。",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep", "Agent"],  # Agent ツールが必須
            agents={
                "code-reviewer": AgentDefinition(
                    description="コード品質とセキュリティの専門レビュアー。",
                    prompt="コードの品質、セキュリティ上の問題、改善提案を分析して報告してください。",
                    tools=["Read", "Glob", "Grep"],
                )
            },
        ),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

asyncio.run(main())
```

ポイントは2つ。

1. `allowed_tools` に `"Agent"` を追加する（これがないとサブエージェントを呼べない）
2. `agents` 辞書に `AgentDefinition` でサブエージェントを定義する

メインエージェントが判断してサブエージェントに処理を委譲し、結果を受け取るという構成を、数十行のコードで実現できる。

---

## ケーススタディ：毎朝ニュースを要約してファイルに保存するエージェント

これまでの知識を組み合わせて、実用的なエージェントを作ろう。AIに関するニュースを検索し、日本語で要約して Markdown ファイルに保存するエージェントだ。

```
# agent_news_summary.py
import asyncio
from datetime import date
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    today = date.today().isoformat()
    output_file = f"news_summary_{today}.md"

    print(f"ニュース要約エージェントを起動 → {output_file} に保存します")

    async for message in query(
        prompt=(
            f"今日（{today}）の Claude / Anthropic / AI エージェント関連の最新ニュースを"
            "Web で3件検索し、各記事を200字以内の日本語で要約してください。"
            f"要約結果を Markdown 形式で {output_file} に保存してください。"
            "ファイルには「# 今日のAIニュース要約」という見出しと、各記事のタイトル・URL・要約を含めてください。"
        ),
        options=ClaudeAgentOptions(
            allowed_tools=["WebSearch", "WebFetch", "Write"],
            permission_mode="acceptEdits",
            system_prompt="あなたは技術ニュースの要約専門家です。正確で簡潔な日本語で情報を伝えてください。",
        ),
    ):
        if isinstance(message, ResultMessage):
            if message.subtype == "success":
                print(f"完了: {output_file} を確認してください")
            else:
                print(f"エラー: {message.subtype}")

asyncio.run(main())
```

このスクリプトを cron や Windows タスクスケジューラに登録すれば、毎朝自動でニュース要約ファイルが生成される。**APIコール料金は1回あたり $0.05〜$0.50 程度（2026年5月時点、モデルやコンテキスト量による）。**

---

## まとめ

* Claude Agent SDK は `pip install claude-agent-sdk` で使える。ファイル操作・コマンド実行・Web 検索などのツールが組み込み済みで、エージェントループは SDK が自動管理する
* エントリーポイントは `query()` 関数1つ。`ClaudeAgentOptions` でツールと権限を設定し、`async for` でメッセージをストリーミング受信する
* `AgentDefinition` でサブエージェントを定義すれば、マルチエージェント構成も数十行で実現できる
* 実用レベルでは「毎朝ニュース要約」「コードベースの自動レビュー」「バグ修正パイプライン」などにすぐ応用できる

---

## 参考
