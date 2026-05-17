---
id: "2026-05-16-claude-codeとmysqlを連携する方法をまとめてみた-01"
title: "Claude CodeとMySQLを連携する方法をまとめてみた"
url: "https://qiita.com/kamome_susume/items/a342e0dd02f0668c86e8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Python", "qiita"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

「Claude Codeは使っているけど、毎回スキーマをコピペして渡すのが面倒くさい」「自然言語でSQLを書いてほしいのに、テーブル構造を説明するところから始まる」——そんな経験、ありませんか？

この記事では、MCP（Model Context Protocol）を使ってClaude CodeとMySQLを直接つなぐ方法を、設定手順から実践的な使い方まで丁寧にまとめました。一度設定してしまえば、Claudeが自分でスキーマを読んでくれるので、毎回説明する手間がゼロになります。

---

## 結論：MCP経由でつなぐだけで、Claudeがスキーマを自律的に理解してくれる

「Claude CodeとMySQLを連携したいけど、何から始めればいいかわからない」と悩んでいませんか？

結論はシンプルです。**MySQL用のMCPサーバーを`claude mcp add`コマンドで登録するだけ**で、Claude Codeが直接MySQLに接続できるようになります。一度つながれば「先月の売上をカテゴリ別に集計して」と自然言語で頼むだけでSQLが走ります。設定ファイルを書いて、接続確認して、それだけです。

---

## そもそもMCPって何？という方へ

MCPは、Anthropicが2024年11月に公開したオープンスタンダードのプロトコルで、AIと外部ツール・データベース・APIを安全につなぐための仕組みです。よく「USB-Cの革命」と例えられます。

スマートフォンの充電がUSB-Cに統一されたように、**AIと外部サービスの接続がMCPという一つのプロトコルに統一される**イメージです。MySQLだけでなく、PostgreSQL、GitHub、Slack、Notionなど数百のサービスと同じインターフェースで連携できます。

| 比較項目 | MCP連携あり | MCP連携なし |
|----------|-------------|-------------|
| スキーマ情報の渡し方 | Claudeが自動で取得 | 毎回コピペして渡す |
| SQLの実行 | Claude Codeから直接実行 | 手動でMySQLクライアントで実行 |
| テーブル名の認識 | リアルタイムで把握 | 都度説明が必要 |
| 開発体験 | ◎ 会話の流れで完結 | ❌ 文脈が途切れやすい |

---

::: note info
エンジニアなら読むべき本を30冊以上紹介しています。
正直、私の仕事のやり方をガラッと変えた神本やSQLのチューニングに悩んだ時にめちゃくちゃ役に立ったもあります👇
[→記事を読む
](https://www.kamome-susume.com/recommended-books-for-engineers/)
:::

---

## 主なMySQL MCPサーバーの選択肢

設定前に、どのMCPサーバーを使うかを決めましょう。代表的なものを比較します。

| パッケージ名 | 言語 | 特徴 | 向いている用途 |
|---|---|---|---|
| `@benborla29/mcp-server-mysql` | Node.js | Claude Code最適化・SSH対応 | 開発・本番DB連携 |
| `mysql-mcp-server`（PyPI） | Python | `uvx`で手軽に動く | ローカル開発 |
| `@lakshya-mcp/mysql-mcp-server-claude` | Node.js | 書き込み権限を細かく制御可 | セキュリティ重視の現場 |
| `mysql-mcp-server`（Go製） | Go | 高速・読み取り専用・監査ログ | 本番参照・分析用途 |

私は`@benborla29/mcp-server-mysql`をよく使っています。Claude Code向けに最適化されており、SSHトンネル対応もあるので、リモートDBにも使いやすいと感じています。

---

## セットアップ手順（Node.js版）

### ① 事前準備

Node.js（v18以上）がインストールされていればすぐ使えます。

```bash
node -v  # v18以上であることを確認
```

### ② `claude mcp add`で登録する（コマンド1行）

ターミナルで以下を実行します。

```bash
claude mcp add mcp_server_mysql \
  -e MYSQL_HOST=localhost \
  -e MYSQL_PORT=3306 \
  -e MYSQL_USER=your_username \
  -e MYSQL_PASS=your_password \
  -e MYSQL_DB=your_database \
  -e ALLOW_INSERT_OPERATION=false \
  -e ALLOW_UPDATE_OPERATION=false \
  -e ALLOW_DELETE_OPERATION=false \
  -- npx @benborla29/mcp-server-mysql
```

✅ パスワードなどの認証情報は**環境変数で渡すのが基本**です。`.mcp.json`にパスワードを直書きすると、Gitにコミットしてしまうリスクがあります。

### ③ `.mcp.json`で管理する場合（チーム共有向け）

プロジェクトルートに`.mcp.json`を置くと、チームメンバー全員が同じ設定を使えます。ただし認証情報は環境変数参照にしましょう。

```json
{
  "servers": {
    "mysql": {
      "type": "stdio",
      "command": "npx",
      "args": ["@benborla29/mcp-server-mysql"],
      "env": {
        "MYSQL_HOST": "${MYSQL_HOST}",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "${MYSQL_USER}",
        "MYSQL_PASS": "${MYSQL_PASS}",
        "MYSQL_DB": "${MYSQL_DB}",
        "ALLOW_INSERT_OPERATION": "false",
        "ALLOW_UPDATE_OPERATION": "false",
        "ALLOW_DELETE_OPERATION": "false"
      }
    }
  }
}
```

❌ パスワードを`.mcp.json`に直書きしてGitにコミットしない  
✅ `${ENV_VAR}`形式で環境変数を参照する

### ④ 接続確認

Claude Codeを起動して`/mcp`と入力すると、登録されたサーバーの一覧が表示されます。

```
❯ 1. mcp_server_mysql ✔ connected
```

◎ `connected`と出ていれば成功です。

---

## セキュリティを考えるなら「読み取り専用ユーザー」を作ろう

本番DBに接続する場合は特に、専用の読み取り専用ユーザーを用意するのがベストプラクティスです。

```sql
-- 読み取り専用ユーザーを作成
CREATE USER 'claude_readonly'@'localhost' IDENTIFIED BY 'secure_password';

-- SELECT権限のみを付与
GRANT SELECT ON your_database.* TO 'claude_readonly'@'localhost';

-- 権限を反映
FLUSH PRIVILEGES;
```

| 設定項目 | 推奨値 | 理由 |
|----------|--------|------|
| `ALLOW_INSERT_OPERATION` | `false` | 誤ってINSERTが走るのを防ぐ |
| `ALLOW_UPDATE_OPERATION` | `false` | 予期しないデータ変更を防ぐ |
| `ALLOW_DELETE_OPERATION` | `false` | 削除事故を防ぐ |
| MySQLユーザー権限 | SELECTのみ | 二重の安全網として機能する |

---

## Claude CodeとMySQLを連携すると何ができるか

設定が完了すると、こんなことが自然言語でできるようになります。

### スキーマの確認

```
> usersテーブルの構造を教えて
```
→ Claudeが自動でDESCRIBEを実行して返してくれます。

### SQLの自動生成・実行

```
> 先月登録したユーザーのうち、購入履歴のある人を一覧で出して
```
→ JOINを含むSQLを生成して、そのまま実行してくれます。

### データ分析

```
> 商品カテゴリ別の売上を月次で集計してグラフ用のCSVを出力して
```
→ 集計クエリの作成からCSV出力まで一気に進めてくれます。

私がいちばん便利だと感じるのは、**スキーマを覚えていてくれる**点です。「ordersテーブルのuser_idって外部キーどこに張ってたっけ」という確認作業が、会話の中でサクッと終わります。

---

## スコープの使い分け：ローカル・ユーザー・プロジェクト

Claude CodeのMCP設定には3つのスコープがあります。

| スコープ | 用途 | 認証情報の扱い |
|----------|------|----------------|
| `local`（デフォルト） | 現在のプロジェクトのみ | ✅ 個人のローカルに留まる |
| `user`（`-s user`） | 全プロジェクトで使いたい共通DB | ✅ `~/.claude.json`に保存 |
| `project`（`-s project`） | チームで共有する設定 | ❌ 認証情報は環境変数で参照 |

本番DBの接続情報は`local`か`user`スコープに留めておくのが安心です。

---

## よくあるトラブルと対処法

| 症状 | 原因 | 対処 |
|------|------|------|
| `Connection closed.` | `npx`がPATHに見つからない | 絶対パスを使うか、PATHを確認 |
| `/mcp`で`disconnected` | 認証情報の誤り or MySQLが起動していない | `mysql -u user -p`で手動確認 |
| JSONパースエラー | `.mcp.json`に末尾カンマが入っている | JSONリンターで検証する |
| nvm環境で動かない | シェルのPATH設定が異なる | nodeの絶対パスを`command`に指定する |

---

## まとめ

- `claude mcp add`コマンド一行でMySQL連携は完結する
- 認証情報は必ず環境変数参照にして、`.mcp.json`への直書きを避ける
- 本番DBには読み取り専用ユーザーを作って二重に安全を確保する
- スキーマ確認・SQL生成・データ分析が自然言語だけで完結するようになる

「まず試してみよう」という方は、ローカルのMySQLに読み取り専用ユーザーを作るところからスタートするのがおすすめです。

---

::: note info
エンジニアなら読むべき本を30冊以上紹介しています。
正直、私の仕事のやり方をガラッと変えた神本やSQLのチューニングに悩んだ時にめちゃくちゃ役に立ったもあります👇
[→記事を読む
](https://www.kamome-susume.com/recommended-books-for-engineers/)
:::
