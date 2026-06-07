---
id: "2026-06-07-claude-codeで-aurora-postgresqlのバージョン間の変更点を一覧化してみた-01"
title: "Claude Codeで Aurora PostgreSQLのバージョン間の変更点を一覧化してみた"
url: "https://qiita.com/daitak/items/0381ac57406ad810d486"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-07"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

# はじめに

こんにちはタカサオです!

Aurora PostgreSQL のメジャーバージョンアップを行う際には、事前に影響調査を行います。
具体的には、以下の情報を網羅的に把握する必要があります。

- OSS PostgreSQLのバージョン間の全変更点（特に Migration セクション）
- AWS Aurora PostgreSQL 固有の変更・制限事項
- アップグレード時に必ず確認すべき Breaking Changes

手作業でリリースノートを読み込むのは結構な時間が掛るため、今回はClaude Codeに調査・整理を依頼してみました。


# 想定バージョン

* 現在のAurora PostgreSQLバージョン： 13.9
* バージョンアップ後のバージョン： 17.9


# 使用したプロンプト

今回作成したプロンプトは以下です。

```
Aurora PostgreSQL のメジャーバージョンアップ（13.9 → 17.9）を実施予定です。
以下の2つの情報源から、バージョン間のすべての変更点を取得し、Markdown 形式の表として一覧化してください。

【情報源】
1. OSS PostgreSQL 公式リリースノート
   - PostgreSQL 14: https://www.postgresql.org/docs/14/release-14.html
   - PostgreSQL 15: https://www.postgresql.org/docs/15/release-15.html
   - PostgreSQL 16: https://www.postgresql.org/docs/16/release-16.html
   - PostgreSQL 17: https://www.postgresql.org/docs/17/release-17.html

2. AWS Aurora PostgreSQL リリースノート
   - https://docs.aws.amazon.com/AmazonRDS/latest/AuroraPostgreSQLReleaseNotes/AuroraPostgreSQL.Updates.html
   （対象バージョン: Aurora PG 14.x, 15.x, 16.x, 17.x の初回リリースノート）

【出力形式】
各テーブルは以下の列構成にしてください：
| バージョン | セクション | タイトル | 解説 | 出典URL |

【出力内容】
以下のセクション別に分けて出力してください：
1. OSS PostgreSQL 14 変更一覧（Migration セクションを含むすべての変更）
2. OSS PostgreSQL 15 変更一覧（同上）
3. OSS PostgreSQL 16 変更一覧（同上）
4. OSS PostgreSQL 17 変更一覧（同上）
5. Aurora PostgreSQL 固有変更一覧（AWS Aurora 独自の機能追加・変更・制限事項）
6. 重要な互換性変更事項（アップグレード時に確認必須な breaking changes）

【注意事項】
- "Migration" セクションの変更は特に重要なので必ず含めること
- 主要な変更だけでなく、すべての変更項目を網羅すること
- Aurora 固有の変更はOSSの変更と分けて記載すること
- 互換性を破壊する変更（破壊的変更）は最後にまとめて再掲すること
- 出力内容は極力日本語で出力すること
```


# 出力結果

出力結果は行数が多いため、GitHub リポジトリに掲載しています。

👉 **[aurora-postgresql-upgrade - GitHub](https://github.com/daitak/aurora-postgresql-upgrade)**

`pg13-to-17-migration-changelog.md` に以下の6セクション構成で出力されています。

| セクション | 内容 | 項目数 |
|-----------|------|-------|
| 1. PG 14 変更一覧 | Migration 21件含む全変更 | 約70項目 |
| 2. PG 15 変更一覧 | Migration 23件含む全変更 | 約60項目 |
| 3. PG 16 変更一覧 | Migration 11件含む全変更 | 約60項目 |
| 4. PG 17 変更一覧 | Migration 17件含む全変更 | 約60項目 |
| 5. Aurora PG 固有変更一覧 | Aurora 独自の機能・制限事項 | 約25項目 |
| 6. Breaking Changes まとめ | 対処方法付きで再掲 | 約35項目 |

---

# 特に注意が必要な変更（抜粋）

出力結果の中から、アップグレード時に特に影響が大きい変更をいくつか紹介します。

## ① Aurora PG 17：`rds.force_ssl` がデフォルトで有効化

Aurora PostgreSQL 17 以降、`rds.force_ssl` パラメータのデフォルト値が `1`（有効）に変更されます。

**影響：** SSL/TLS に対応していないクライアントからの接続がすべて拒否されます。

```sql
-- 接続確認（SSL が使われているかチェック）
SELECT ssl, version FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

## ② PG 15：`public` スキーマの CREATE 権限が削除

新規 DB クラスタでは `public` スキーマへの CREATE 権限がデフォルトで削除されます。

**影響：** スーパーユーザー以外のロールが `public` スキーマにオブジェクトを作成できなくなります。

```sql
-- 対処：必要なロールに権限を付与する
GRANT CREATE ON SCHEMA public TO your_role;
```

## ③ PG 17：`pg_stat_statements` のカラム名変更

| 旧カラム名 | 新カラム名 |
|-----------|-----------|
| `blk_read_time` | `shared_blk_read_time` |
| `blk_write_time` | `shared_blk_write_time` |

**影響：** `pg_stat_statements` を参照するモニタリングツールやクエリは修正が必要です。

## ④ PG 17：メンテナンス操作時の `search_path` 安全化

`VACUUM` / `ANALYZE` / `CREATE INDEX` などのメンテナンス操作で安全な `search_path` が使用されるようになります。

**影響：** カスタムスキーマを参照するインデックス関数やデフォルト値関数は `search_path` を明示的に指定する必要があります。

## ⑤ PG 14：`password_encryption` のデフォルトが `scram-sha-256` に変更

デフォルトのパスワード暗号化方式が `md5` から `scram-sha-256` に変更されます。

**影響：** 古いドライバや MD5 認証のみに対応したクライアントは認証に失敗する可能性があります。


# まとめ

Claude Codeに依頼することで、バージョン間の変更点を日本語で整理された一覧を出力することができました。

手作業では数時間かかる作業が、プロンプト一つで完了できました。Claude Codeすごいですね!
これ以外にも、実機のパラメータと比較してパラメータ変更が必要かどうかを調査する事もClaude Codeにお願いできないか考えていますので、次回実施したいと思います。

それでまた!


# 参考リンク

- [出力結果（GitHub）](https://github.com/daitak/aurora-postgresql-upgrade)
- [OSS PostgreSQL 14 リリースノート](https://www.postgresql.org/docs/14/release-14.html)
- [OSS PostgreSQL 15 リリースノート](https://www.postgresql.org/docs/15/release-15.html)
- [OSS PostgreSQL 16 リリースノート](https://www.postgresql.org/docs/16/release-16.html)
- [OSS PostgreSQL 17 リリースノート](https://www.postgresql.org/docs/17/release-17.html)
- [Aurora PostgreSQL リリースノート](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraPostgreSQLReleaseNotes/AuroraPostgreSQL.Updates.html)
