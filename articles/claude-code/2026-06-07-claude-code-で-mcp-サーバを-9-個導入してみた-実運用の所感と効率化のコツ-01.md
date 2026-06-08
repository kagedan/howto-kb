---
id: "2026-06-07-claude-code-で-mcp-サーバを-9-個導入してみた-実運用の所感と効率化のコツ-01"
title: "Claude Code で MCP サーバを 9 個導入してみた: 実運用の所感と効率化のコツ"
url: "https://qiita.com/iigtn/items/e0e066bf8ddb54784bf9"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

## はじめに

この記事では、Claude Code を用いて 9 つの MCP サーバを導入した構成について紹介します。具体的には、filesystem, GitHub, PostgreSQL, brave-search, fetch, playwright, JetBrains, Slack, sequential-thinking などの MCP サーバを実運用で活用した所感をお伝えします。特に、実際によく使うサーバと、設定したまま忘れてしまいがちなサーバについて触れます。また、MCP の認証やコンフリクト解消のコツも共有します。

### 想定読者
- MCP サーバを使ったシステム構築に興味があるエンジニア
- Claude Code の導入を検討している方
- サーバ運用の効率化を図りたいフリーランス

### この記事を読むとできるようになること
- MCP サーバの効果的な運用方法を理解する
- よく使うサーバとそうでないサーバの見極め方
- MCP の認証とコンフリクト解消の実践的なコツを学ぶ

## 環境

- OS: Ubuntu 20.04
- Claude Code バージョン: 1.2.3
- MCP サーバ: filesystem, GitHub, PostgreSQL, brave-search, fetch, playwright, JetBrains, Slack, sequential-thinking
- 必要な前提: Docker, Git

## MCP サーバの構成と運用

Claude Code を利用して MCP サーバを 9 つ導入しましたが、実際の運用では毎日頻繁に使用するのは 3 つ程度です。このセクションでは、それぞれのサーバについて簡単に紹介し、どのように運用しているかを説明します。

### よく使うサーバ

- **filesystem**: データのバックアップや共有に頻繁に使用。Claude Code のファイルシステムとの連携がスムーズです。
- **GitHub**: プロジェクトのバージョン管理に不可欠。特にプルリクエストの自動化に役立っています。
- **PostgreSQL**: データベース管理としての利用が中心。特に大規模データのクエリ処理に重宝しています。

### 設定して忘れがちなサーバ

- **brave-search**: 特定の検索クエリの自動化を目指して導入しましたが、実際には利用頻度が低くなっています。
- **fetch**: API のデータ取得に使いますが、プロジェクトによってはあまり活用しないことも。
- **playwright**: テスト自動化のために設定しましたが、他のツールで十分なことも多く、使わないことが増えました。

## MCP 認証とコンフリクト解消のコツ

MCP の認証設定やサーバ間でのコンフリクトは運用上の課題となることがあります。ここでは、私が実際に試して効果的だった方法を紹介します。

### 認証の設定

認証情報の管理はセキュアに行う必要があります。Claude Code では、以下のように環境変数を活用しています。

```bash
# .env
GITHUB_TOKEN=<YOUR_TOKEN>
POSTGRES_PASSWORD=<YOUR_PASSWORD>
```

環境変数を使用することで、コードに直接認証情報を埋め込むことを避け、セキュリティを強化しています。

### コンフリクト解消のコツ

複数の MCP サーバが同時に動作する環境では、リソースの競合が発生することがあります。以下のテクニックを用いて解消しています。

- サーバの優先順位を明確にし、競合が発生しそうなタスクはシーケンシャルに実行する。
- ログを詳細に記録し、問題が発生した際の原因追求を容易にする。

## ハマったポイント / トラブルシュート

### Brave-search の設定ミス

最初に brave-search サーバを導入した際、API キーの設定を忘れてしまい、データ取得ができませんでした。公式ドキュメントには API キーの設定に関する記述が見当たらなかったため、設定手順を細かく確認する必要がありました。

### PostgreSQL の接続エラー

初期の段階で PostgreSQL サーバへの接続が不安定でした。原因はポート設定のミスで、`pg_hba.conf` ファイルを適切に編集することで解決しました。

```bash
# pg_hba.conf
host all all <PRIVATE_IP>/32 md5
```

## まとめ

Claude Code を用いて 9 つの MCP サーバを導入し、運用してみると、実際に日常的に使用するのは 3 つ程度であることがわかりました。認証やコンフリクトの解消には注意が必要ですが、効率的な運用が可能です。今後は、使っていないサーバの整理や、さらなる自動化の検討を進める予定です。

## 参考リンク

@[card](https://docs.claude.ai/mcp)
@[card](https://www.postgresql.org/docs/)
@[card](https://docs.github.com/en)
