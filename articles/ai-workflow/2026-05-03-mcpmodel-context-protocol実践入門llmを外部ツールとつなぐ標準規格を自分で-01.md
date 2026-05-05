---
id: "2026-05-03-mcpmodel-context-protocol実践入門llmを外部ツールとつなぐ標準規格を自分で-01"
title: "MCP（Model Context Protocol）実践入門──LLMを外部ツールとつなぐ標準規格を自分で実装する【2026】"
url: "https://zenn.dev/karaagedesu/articles/4eefd40f81817d"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "zenn"]
date_published: "2026-05-03"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

「LLMに自分のデータを読ませたい」「LLMからAPIを呼び出したい」──そう思ったとき、これまでは用途ごとに個別実装が必要でした。

**MCP（Model Context Protocol）** はその問題を解決するオープンプロトコルです。Anthropicが2024年11月に公開し、2026年現在はOpenAI・Google・Microsoftも採用。LLMとあらゆる外部ツール・データソースをつなぐ**事実上の業界標準**になっています。

「AIのためのUSB-C」と例えられることが多く、一度MCPサーバーを作れば、Claude Desktop・Cursor・Zedなど対応クライアントからそのまま呼び出せます。

本記事では、MCPの仕組みから始まり、自分でサーバーを実装して実際にClaudeから使うところまでを解説します。

---

## MCPとは何か

### 従来の問題

LLMにツールを接続する方法は、これまでプラットフォームごとにバラバラでした。

* Claude向けのツール統合
* ChatGPT向けのFunction Calling
* Cursor向けのコンテキスト注入

それぞれに別々の実装が必要で、「一度作ったら使い回せない」状態でした。

### MCPが解決すること

MCPは**LLMクライアントとツール（サーバー）の間の標準通信規格**を定めます。

```
MCPクライアント（Claude Desktop / Cursor / Zed）
        ↕ MCP標準プロトコル
MCPサーバー（あなたが作るツール）
        ↕ 任意のAPI・DB・ファイル
外部リソース（Notion / GitHub / ローカルDB / 独自API）
```

MCPサーバーを一度作れば、すべての対応クライアントからそのまま使えます。

### MCPの3つの機能

MCPサーバーが提供できる機能は3種類あります。

**Tools（ツール）**  
LLMが呼び出せる関数。検索・書き込み・計算など能動的な処理。

**Resources（リソース）**  
LLMが読み取れるデータ。ファイル・DB・APIレスポンスなど。

**Prompts（プロンプト）**  
再利用可能なプロンプトテンプレート。ユーザーが選択して使う。

個人開発では**Toolsだけ実装すれば十分**なケースがほとんどです。

---

## セットアップ

FastMCPはFlaskのような感覚でMCPサーバーを書けるライブラリです。公式SDKより大幅にボイラープレートが減ります。

---

## 最小実装：ノートを検索するMCPサーバー

まず最もシンプルな例として、ローカルのMarkdownノートを検索するサーバーを作ります。

```
# note_search_server.py
from mcp.server.fastmcp import FastMCP
from pathlib import Path

mcp = FastMCP("note-search")

NOTES_DIR = Path.home() / "notes"  # ノートのディレクトリ

@mcp.tool()
def search_notes(query: str) -> str:
    """
    ローカルのMarkdownノートを全文検索する。
    
    Args:
        query: 検索キーワード
    
    Returns:
        マッチしたノートのファイル名と該当箇所
    """
    results = []
    
    if not NOTES_DIR.exists():
        return "ノートディレクトリが見つかりません"
    
    for md_file in NOTES_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        if query.lower() in content.lower():
            # マッチした行を抽出
            lines = [
                line for line in content.split("\n")
                if query.lower() in line.lower()
            ]
            results.append(f"## {md_file.name}\n" + "\n".join(lines[:3]))
    
    if not results:
        return f"「{query}」に関するノートは見つかりませんでした"
    
    return "\n\n".join(results)

@mcp.tool()
def list_notes() -> str:
    """ノートの一覧を取得する"""
    if not NOTES_DIR.exists():
        return "ノートディレクトリが見つかりません"
    
    files = list(NOTES_DIR.rglob("*.md"))
    return "\n".join([f.name for f in files[:50]])

if __name__ == "__main__":
    mcp.run()
```

---

## Claude Desktopに接続する

作ったサーバーをClaude Desktopから使えるようにします。

設定ファイルを編集します。

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```
{
  "mcpServers": {
    "note-search": {
      "command": "python",
      "args": ["/path/to/note_search_server.py"]
    }
  }
}
```

Claude Desktopを再起動すると、チャット画面にツールが表示されます。あとは「LangGraphについてメモしたことある？」と話しかけるだけで、Claudeが自動でツールを呼び出してノートを検索してくれます。

---

## 実用例：GitHub Issues連携サーバー

より実用的な例として、GitHub Issuesを参照できるサーバーを作ります。

```
# github_issues_server.py
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("github-issues")

GITHUB_TOKEN = "your-github-token"
REPO = "owner/repo-name"

@mcp.tool()
def get_open_issues(label: str = "") -> str:
    """
    GitHubのオープンIssueを取得する。
    
    Args:
        label: フィルタするラベル名（省略可）
    
    Returns:
        Issue一覧（番号・タイトル・本文の先頭）
    """
    url = f"https://api.github.com/repos/{REPO}/issues"
    params = {"state": "open", "per_page": 20}
    if label:
        params["labels"] = label
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = httpx.get(url, params=params, headers=headers)
    issues = response.json()
    
    results = []
    for issue in issues:
        body_preview = (issue.get("body") or "")[:200]
        results.append(
            f"#{issue['number']} {issue['title']}\n{body_preview}"
        )
    
    return "\n\n---\n\n".join(results) if results else "オープンIssueはありません"

@mcp.tool()
def create_issue_comment(issue_number: int, comment: str) -> str:
    """
    GitHubのIssueにコメントを投稿する。
    
    Args:
        issue_number: IssueのID番号
        comment: 投稿するコメント本文
    
    Returns:
        投稿結果
    """
    url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = httpx.post(url, json={"body": comment}, headers=headers)
    
    if response.status_code == 201:
        return f"Issue #{issue_number} にコメントを投稿しました"
    return f"エラー: {response.status_code}"

if __name__ == "__main__":
    mcp.run()
```

これをClaude Desktopに接続すると、「バグ系のIssueを全部確認して優先度をつけて」といった自然言語での操作が可能になります。

---

## Resourcesの実装

ファイルやDBをLLMが直接参照できる「リソース」も実装できます。

```
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-resources")

@mcp.resource("file://config")
def get_config() -> str:
    """設定ファイルの内容を提供する"""
    return Path("config.yaml").read_text()

@mcp.resource("db://users/{user_id}")
def get_user(user_id: str) -> str:
    """ユーザー情報をDBから取得する"""
    # DBから取得する処理
    return f"User {user_id} の情報..."
```

リソースはToolsと違い、LLMが能動的に呼び出すのではなく、クライアントがコンテキストとして注入する用途に使います。

---

## よくあるつまずきポイント

**① サーバーが認識されない**  
設定ファイルのパスが間違っているケースが多いです。`command` に `python` ではなく仮想環境のフルパスを指定すると解決することがあります。

```
{
  "mcpServers": {
    "note-search": {
      "command": "/Users/yourname/.venv/bin/python",
      "args": ["/path/to/note_search_server.py"]
    }
  }
}
```

**② ツールの説明が重要**  
LLMはdocstringを読んでツールを選択します。説明が曖昧だと正しいツールが呼ばれません。「いつ使うか」「何を返すか」を明示的に書くのがポイントです。

**③ エラーハンドリングを必ず入れる**  
ツールが例外を投げるとLLMが止まります。try-exceptで必ずエラーメッセージを文字列で返すようにしてください。

```
@mcp.tool()
def safe_tool(query: str) -> str:
    try:
        return do_something(query)
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"
```

---

## まとめ

| 項目 | 内容 |
| --- | --- |
| MCPとは | LLMと外部ツールをつなぐ業界標準プロトコル |
| 使えるクライアント | Claude Desktop / Cursor / Zed など |
| 実装の最小単位 | `@mcp.tool()` デコレータを付けた関数 |
| 推奨ライブラリ | FastMCP（公式SDKより簡潔） |
| 向いているユースケース | 自分のデータへのアクセス・社内ツール連携・API統合 |

一度MCPサーバーを作る感覚をつかめば、あとは `@mcp.tool()` を増やすだけでLLMの能力をどんどん拡張できます。まずはノート検索など身近なものから始めてみてください。

**参考リンク**
