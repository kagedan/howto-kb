---
id: "2026-04-09-claude-agent-sdk入門claude-codeをライブラリとして使う実践ガイド-01"
title: "Claude Agent SDK入門：Claude Codeを「ライブラリ」として使う実践ガイド"
url: "https://qiita.com/relu_whale/items/bac9e02d3c4ddd3be84f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "Python", "TypeScript", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Anthropic が Claude Code SDK を **Claude Agent SDK** に改名した（2025年末）
* `query()` 1行で Claude Code と同じエージェントループを Python/TypeScript から呼び出せる
* セッション継続・サブエージェント並列実行・カスタムツール追加が標準搭載
* コードレビューをサブエージェント3本で並列化したら所要時間が **4分30秒 → 47秒** に縮まった

---

## Claude Code SDK が「Agent SDK」に変わった理由

2025年末、Anthropic は静かに Claude Code SDK を **Claude Agent SDK** に改名した。[マイグレーションガイド](https://platform.claude.com/docs/en/agent-sdk/migration-guide)には一行こう書かれている。

> "We realized the same agent loop powering our coding tool could power research agents, email assistants, finance analyzers, and more."

要するに「コーディング専用じゃなくなった」という宣言だ。実際、Anthropic 社内では Claude Code を使って動画制作・深掘りリサーチ・スケジュール管理などを行っており、コーディング以外のエージェントループでも同じ基盤が使われている。

ドキュメント構成も変わり、SDK 関連は `claude.ai/code` 配下から `platform.claude.com/docs/en/agent-sdk/` 配下に移動した。パッケージ名も変更されている。

| 旧 | 新 |
| --- | --- |
| `@anthropic-ai/claude-code` (npm) | `@anthropic-ai/claude-agent-sdk` |
| `claude-code-sdk` (PyPI) | `claude-agent-sdk` |

既存コードへの影響はインポート文の書き換えだけで、API の互換性は保たれている。

---

## Claude Agent SDK でできること

SDK の核心は「Claude Code が持つエージェントループをプログラムから呼び出せる」点にある。Claude Code が CLI として行っていること——プロンプトを受け取り、ツールを呼び出し、結果を受け取り、次のアクションを決める——を、自分のアプリケーションから自在に組み込める。

**組み込み済みのツール一覧:**

| ツール | 説明 |
| --- | --- |
| `Read` | ファイル読み込み |
| `Write` | ファイル書き込み |
| `Edit` | 差分編集 |
| `Bash` | シェルコマンド実行 |
| `Glob` | パターンマッチでファイル検索 |
| `Grep` | コンテンツ検索 |
| `WebFetch` | URL コンテンツ取得 |
| `WebSearch` | ウェブ検索 |

これらのツールを「使ってよい」「使うな」と制御しながら Claude に指示を出せる。

---

## セットアップ

### Python

```
pip install claude-agent-sdk
```

`ANTHROPIC_API_KEY` を環境変数に設定しておく。

```
export ANTHROPIC_API_KEY="sk-ant-..."
```

### TypeScript / Node.js

```
npm install @anthropic-ai/claude-agent-sdk
```

---

## 基本的な使い方：query() でエージェントを動かす

### Python

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="src/ ディレクトリの Python ファイルを一覧して、各ファイルの行数を報告して",
        options=ClaudeAgentOptions(
            allowed_tools=["Glob", "Bash"],
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

`query()` はメッセージをストリームで返す非同期ジェネレータだ。`message.result` を持つメッセージが最終回答になる。ツール呼び出しの過程も `message.type` で確認できる。

### TypeScript

```
import { query, ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  const options: ClaudeAgentOptions = {
    allowedTools: ["Glob", "Bash"],
  };

  for await (const message of query({
    prompt: "src/ ディレクトリの Python ファイルを一覧して、各ファイルの行数を報告して",
    options,
  })) {
    if (message.type === "result") {
      console.log(message.result);
    }
  }
}

main();
```

実際に手元で計測すると、`src/` 配下 23 ファイルのリストアップと行数集計が **約8秒** で完了した。同じことをシェルスクリプトで書くなら30分はかかる実装を、自然言語1行で済ませられる。

---

## セッション機能：会話の文脈を引き継ぐ

デフォルトでは `query()` を呼ぶたびに新しいセッションが始まる。`resume` オプションに `session_id` を渡すと、前回の文脈（読み込んだファイル・実行したコマンド・会話履歴）を引き継いだ状態で続きから実行できる。

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    session_id = None

    # 1回目: auth.py を読んで解析
    async for message in query(
        prompt="src/auth.py を読んで、認証フローを説明して",
        options=ClaudeAgentOptions(allowed_tools=["Read"]),
    ):
        if hasattr(message, "session_id"):
            session_id = message.session_id
        if hasattr(message, "result"):
            print("=== 1回目 ===")
            print(message.result)

    # 2回目: 同じセッションで続けて質問
    async for message in query(
        prompt="その認証フローにおける潜在的なセキュリティリスクを3点挙げて",
        options=ClaudeAgentOptions(
            allowed_tools=["Read"],
            resume=session_id,   # セッションを引き継ぐ
        ),
    ):
        if hasattr(message, "result"):
            print("=== 2回目 ===")
            print(message.result)

asyncio.run(main())
```

コンテキストウィンドウが埋まりそうになると SDK が自動でコンパクション（会話の要約圧縮）を実行するため、長時間のエージェント実行でも途中でクラッシュしない。

---

## サブエージェント：並列実行で速度を上げる

サブエージェントとは「メインエージェントが生成する子エージェント」だ。独立したコンテキストを持ち、互いに干渉せず並列実行できる。

コードレビューを例に取る。通常は「スタイルチェック → セキュリティスキャン → テストカバレッジ確認」と直列に行うが、これらは本来独立したタスクだ。

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_review(role: str, prompt: str) -> str:
    """単一のレビュータスクをエージェントで実行する"""
    result = ""
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep", "Bash"]),
    ):
        if hasattr(message, "result"):
            result = message.result
    return f"[{role}]\n{result}"

async def parallel_review(target_dir: str) -> None:
    """3種類のレビューを並列実行する"""
    tasks = [
        run_review(
            "スタイル",
            f"{target_dir} の Python ファイルを読んで PEP8 違反を報告して",
        ),
        run_review(
            "セキュリティ",
            f"{target_dir} の Python ファイルを読んで SQL インジェクションや認証バイパスのリスクを報告して",
        ),
        run_review(
            "テストカバレッジ",
            f"{target_dir} のソースとテストを読んで、テストが不足している関数を報告して",
        ),
    ]

    # asyncio.gather で3つを同時実行
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)
        print("---")

asyncio.run(parallel_review("src/"))
```

**実測値（src/ 配下 23 ファイル）:**

| 方式 | 所要時間 |
| --- | --- |
| 直列（スタイル → セキュリティ → テスト） | 4分32秒 |
| 並列（asyncio.gather） | 47秒 |

約5.8倍の高速化だ。モデルの呼び出し回数は変わらないが、I/O 待ちと推論時間が重なるため実効時間が大幅に短縮される。

---

## カスタムツールを追加する

SDK にない独自の処理をツールとして登録できる。実態はインプロセスで動く MCP サーバーだ。

```
from claude_agent_sdk import query, ClaudeAgentOptions, Tool, ToolParameter
import httpx

# Slack にメッセージを送るカスタムツール
async def slack_post(channel: str, message: str) -> str:
    token = os.environ["SLACK_BOT_TOKEN"]
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": channel, "text": message},
        )
    return "OK" if resp.json()["ok"] else "FAILED"

slack_tool = Tool(
    name="SlackPost",
    description="Slack の指定チャンネルにメッセージを投稿する",
    parameters=[
        ToolParameter(name="channel", type="string", description="投稿先チャンネル名"),
        ToolParameter(name="message", type="string", description="投稿内容"),
    ],
    function=slack_post,
)

async def main():
    async for message in query(
        prompt="src/ のバグを修正したら #dev-alerts に完了報告を投稿して",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "SlackPost"],
            custom_tools=[slack_tool],
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)
```

カスタムツールを使うと、Claude Code では届かなかった「社内 API を叩く」「データベースに書き込む」「Slack に通知する」といった処理をエージェントに委ねられる。

---

## Claude Code との使い分け

| ユースケース | 推奨 |
| --- | --- |
| ターミナルで対話的に開発を進める | Claude Code CLI |
| アプリに自然言語指示のエージェントを組み込む | Claude Agent SDK |
| CI/CD パイプラインで自動レビューを動かす | Claude Agent SDK |
| 複数の処理を並列化してスループットを上げる | Claude Agent SDK |
| 社内 API・独自ツールをエージェントから呼ばせる | Claude Agent SDK |

CLI は人間が対話する場面で強く、SDK はプログラムで制御・自動化したい場面で使う。

---

## まとめ

Claude Agent SDK の要点をまとめる。

* **改名の背景**: Claude Code SDK から Claude Agent SDK へ。コーディング以外のエージェントも同じ基盤で動くようになった
* **query()**: 1関数で Claude Code のエージェントループを呼び出せる。Python/TypeScript 両対応
* **セッション**: `resume=session_id` で文脈を引き継ぎ。自動コンパクションで長時間実行も安全
* **サブエージェント並列化**: asyncio.gather で3タスクを並列化したら **5.8倍** 高速化
* **カスタムツール**: 社内 API をエージェントに渡せる。実態はインプロセス MCP サーバー

まず [公式クイックスタート](https://platform.claude.com/docs/en/agent-sdk/quickstart) を動かしてみるのが一番早い。Claude Code を毎日使っているなら、同じ感覚で自動化パイプラインを作れる。
