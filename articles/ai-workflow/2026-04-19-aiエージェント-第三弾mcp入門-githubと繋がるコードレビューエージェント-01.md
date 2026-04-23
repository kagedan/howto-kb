---
id: "2026-04-19-aiエージェント-第三弾mcp入門-githubと繋がるコードレビューエージェント-01"
title: "【AIエージェント 第三弾】MCP入門 ── GitHubと繋がるコードレビューエージェント"
url: "https://qiita.com/bit-tanghao/items/90e31851a97beee36fbe"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "qiita"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

第2弾までのエージェントはローカルファイルしか読めなかった。実際の開発現場でレビューが必要なのはGitHubのPull Requestだ。

第3弾では自前のMCPサーバーを実装してGitHub APIをラップし、PRのdiffを自動取得してインラインコメント付きのレビューを投稿するパイプラインを作る。

---

## Tool UseとMCPの違い

第2弾ではAnthropicのTool Useを使ってツールを呼んでいた。Tool UseはAgentのコードの中に書いた関数をClaudeが呼ぶ仕組みだ。

MCPはそこから一歩進んで、ツールを**独立したサーバープロセス**として切り出す。サーバーとクライアントはJSON-RPC 2.0でstdio通信する。

```
Tool Use:  Claude → Agent内の関数（同一プロセス）
MCP:       Claude → AgentプロセスがMCPサーバープロセスを呼ぶ（プロセス間通信）
```

なぜMCPが生まれたのか。Tool Useでは同じツールを別のLLMやアプリケーションから使い回せない。MCPはツールをサーバーとして独立させることで、どのLLMからでも同じツールを呼べる標準化されたプロトコルを実現している。

---

## アーキテクチャ

```
react_agent.py
    │
    │ subprocess起動（stdin/stdout）
    ▼
github_mcp_server.py  ← MCPサーバー（自前実装）
    │
    │ HTTPS
    ▼
GitHub API
```

`react_agent.py` を実行すると、MCPサーバーが自動的にサブプロセスとして起動する。別ターミナルを開く必要はない。

---

## MCPプロトコルの実装

MCPはJSON-RPC 2.0を使う。クライアントとサーバーの通信フローをシーケンス図で示す。

[![mcp_protocol_sequence.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2604123%2F7a260d3d-85a7-47d9-8bda-203481c172c2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b4e0551875a796e45dacb577a4f8cb93)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2604123%2F7a260d3d-85a7-47d9-8bda-203481c172c2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b4e0551875a796e45dacb577a4f8cb93)

サーバー側の基盤（`mcp_protocol.py`）はstdinを1行ずつ読んでJSONパースし、レスポンスをstdoutに1行で書き出す。WindowsでコンソールのエンコーディングがデフォルトでGBKになっているため、stdoutはバイナリモードで開いてUTF-8で明示的にエンコードする必要がある。

```
stdin  = open(sys.stdin.fileno(),  "rb", closefd=False, buffering=0)
stdout = open(sys.stdout.fileno(), "wb", closefd=False, buffering=0)

def write_response(obj: dict):
    data = json.dumps(obj, ensure_ascii=False) + "\n"
    stdout.write(data.encode("utf-8"))
    stdout.flush()
```

---

## GitHubMCPServerの実装

サーバーが公開するツールは5つだ。

| ツール | 役割 |
| --- | --- |
| `get_pull_request` | PRの基本情報を取得 |
| `get_pr_diff` | unified diff形式でdiffを取得 |
| `get_pr_files` | 変更ファイル一覧を取得 |
| `add_pr_review` | インラインコメント付きレビューを投稿 |
| `list_pr_comments` | 既存コメント一覧を取得 |

`add_pr_review` が今回の核心だ。GitHub の Pull Reviews API（`POST /repos/.../pulls/{pr}/reviews`）を使い、`inline_comments` でファイルパス・行番号・コメント本文を指定するとdiffの該当行の直下にコメントが表示される。

実装で注意が必要な点が3つあった。

**1. 行番号はdiffに存在する行のみ指定できる**

diffに含まれない行番号を指定するとGitHub APIが422を返す。そのため `add_pr_review` を呼ぶ前にMCPサーバー側でdiffを解析して有効な行番号セットを構築し、Agentから来た行番号を事前にフィルタする。

```
def _get_valid_lines(self, owner, repo, pr_number) -> dict:
    diff_text = self._github_raw(f"/repos/{owner}/{repo}/pulls/{pr_number}")
    valid = {}
    current_file = None
    current_line = 0

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:]
            valid[current_file] = set()
            current_line = 0
        elif raw_line.startswith("@@"):
            # @@ -X,Y +A,B @@ の +A が変更後の開始行番号
            current_line = int(raw_line.split("+")[1].split(",")[0].split()[0]) - 1
        elif raw_line.startswith("+"):
            current_line += 1
            valid[current_file].add(current_line)   # 追加行
        elif raw_line.startswith(" "):
            current_line += 1                        # コンテキスト行

    return valid  # {filename: {行番号, ...}}
```

**2. 同じ行番号への重複コメントは1件に結合する**

LLMは同じ行の複数の問題を別々のコメントとして生成することがある。GitHub APIは同一ファイルの同一行への複数コメントの一括投稿を許可しないため、MCPサーバー側で重複を検出して本文を結合する。

**3. 自分のPRにはREQUEST\_CHANGESを使えない**

GitHubの仕様として、PRの作成者本人は `REQUEST_CHANGES` でレビューを投稿できない。`/user` APIでトークンのユーザーとPR作成者を比較し、一致する場合は自動的に `COMMENT` に変換する。

---

## 実行結果

実際にGitHub PR に対して実行した。

```
--- イテレーション 1 ---
MCP呼び出し: get_pull_request
MCP呼び出し: get_pr_files
MCP呼び出し: get_pr_diff

--- イテレーション 2 ---
MCP呼び出し: add_pr_review
結果: {
  "review_id": 4134606491,
  "inline_count": 28,
  "skipped_count": 0,
  "fallback_used": false
}

✅ GitHubにレビュー投稿完了
   インラインコメント: 28件
```

28件のインラインコメントが全件投稿され、フォールバックはゼロだった。

インラインコメントの内訳は以下の通りだ。

| ファイル | 件数 | 内容 |
| --- | --- | --- |
| sample\_01.py | 3件 | SQLインジェクション（文字列結合・f-string・%演算子） |
| sample\_02.py | 5件 | 未使用変数 |
| sample\_03.py | 7件 | 例外処理なし（ZeroDivisionError・ValueError等） |
| sample\_04.py | 9件 | 平文パスワード・ハードコードAPIキー・機密情報ログ出力 |
| sample\_05.py | 4件 | N+1クエリ・Python側フィルタリング・Python側SUM |

GitHubのPRページで「Files changed」タブを開くと、各ファイルの該当行の直下にコメントが表示される。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2604123%2F84526617-5d53-4ac7-9ea5-5b16007d82b0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6afa6a39024140ac7fa451eb6261e56c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2604123%2F84526617-5d53-4ac7-9ea5-5b16007d82b0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6afa6a39024140ac7fa451eb6261e56c)

---

## シーケンス図で見る動作

[![episode03_sequence_inkscape.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2604123%2F7c5da083-3f6e-4c56-9799-b85d16163f29.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=774b8be348b36842f9e6e972e82b8baa)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2604123%2F7c5da083-3f6e-4c56-9799-b85d16163f29.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=774b8be348b36842f9e6e972e82b8baa)

第1・2弾との大きな違いは、Toolsが独立したプロセスになっていることだ。第2弾ではAgentが直接ローカル関数を呼んでいたが、第3弾ではAgentがMCPクライアントとしてサブプロセスにJSON-RPCメッセージを送り、そのサブプロセスがGitHub APIに問い合わせる。

シーケンス図でもう一点重要なのは、`get_pull_request`・`get_pr_files`・`get_pr_diff` の3ツールがイテレーション1で同時に呼ばれていることだ。Anthropic APIのTool UseはレスポンスにToolUseブロックを複数含められるので、Claudeが「3つ同時に呼ぶ」と判断すれば1イテレーションで全部完了する。

---

## 第2弾のツールはなぜ使わないのか

第2弾で実装した `lint_check`・`complexity_check`・`search_best_practice` は第3弾には含めていない。

理由はシンプルで、これらのツールはローカルファイルのパスを受け取ってASTを直接解析する設計だからだ。

```
# 第2弾: ファイルパスを渡してAST解析できる
result = run_lint_check("review_targets/sample_01.py")
```

第3弾ではGitHub APIから取得するのはdiff（テキスト差分）であり、ソースコード全体ではない。既存ファイルへの部分変更であれば差分だけではAST解析できない。組み合わせるには `get_file_content` のようなツールでファイルの全文を別途取得する必要があり、第3弾の本題であるMCPの仕組みから外れるため省いた。

第6弾（Skills設計）でこれらを統合する予定だ。

---

## 第2弾との比較

| 観点 | 第2弾 | 第3弾 |
| --- | --- | --- |
| 入力 | ローカルファイル | GitHub PR |
| ツール実行 | 同一プロセス内の関数 | MCPサーバープロセス |
| 出力 | コンソール表示 | GitHubにインラインコメント投稿 |
| イテレーション | 3〜5回/ファイル | 3回/PR全体 |
| 実行時間 | 87.5秒（5ファイル） | 38.1秒（5ファイル） |

実行時間が大幅に短くなったのは、全ファイルのdiffをまとめて1回取得して1回のレビューで全コメントを投稿しているからだ。第2弾はファイルを1本ずつ処理していた。

---

## 今回の限界と次回

今回のエージェントはレビューのたびにゼロから始める。「このプロジェクトは先週も同じ指摘をした」「社内の命名規則はPEP8より優先する」という文脈を持っていない。

次回（#4：メモリを持つAgent）ではその問題を解決する。短期記憶（会話内）と長期記憶（ファイル）の2層を実装して、プロジェクト固有の文脈を持ち続けるエージェントにする。

---

## コード

```
episode03/
├── react_agent.py
├── mcp_client.py              # MCPクライアント（subprocess通信）
└── mcp_server/
    ├── mcp_protocol.py        # MCPプロトコル基盤（JSON-RPC 2.0）
    └── github_mcp_server.py   # GitHub APIをMCPツールとして公開
```

```
pip install anthropic
set ANTHROPIC_API_KEY=sk-ant-xxxxx
set GITHUB_TOKEN=ghp_xxxxx
set PYTHONIOENCODING=utf-8

python react_agent.py --owner your-name --repo your-repo --pr 1
```

GITHUBのPersonal Access Tokenは `repo` スコープが必要だ。
