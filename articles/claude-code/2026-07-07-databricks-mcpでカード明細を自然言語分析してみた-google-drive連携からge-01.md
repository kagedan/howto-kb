---
id: "2026-07-07-databricks-mcpでカード明細を自然言語分析してみた-google-drive連携からge-01"
title: "Databricks MCPでカード明細を自然言語分析してみた ― Google Drive連携からGenie接続まで"
url: "https://zenn.dev/shiroqujira/articles/fc049e10836c8b"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "LLM", "cowork", "zenn"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

## 最初に

やること：Google Drive上に貯めているカード明細CSVを、Databricksで自動的に取り込み・分析し、Genie経由で「先月一番使った店は？」のように自然言語で聞けるようにする。

全体像はこう。

```
Google Drive（カード明細CSV）
  → Auto Loader（差分取り込み）
  → Bronze / Silver / Gold（Delta Table）
  → Genie Space（AI/BI）
  → Databricks MCP
  → Claude Desktop（自然言語で質問）
```

![](https://static.zenn.studio/user-upload/44a66af06d0f-20260708.png)

Databricksでの自分専用データ基盤づくりと、Genie SpaceをMCP経由で外部のAIアシスタントに繋ぐところまで、実際にやってみた記録。想定読者は、Databricksで個人利用の分析基盤を作りたい人、Genie・MCPに興味がある人。

## Bronze：Auto LoaderでGoogle Driveを監視する

### やること

Google Drive上の特定フォルダを監視し、新しいCSVファイルが置かれたら自動でDelta Tableに取り込む。

### 事前準備

* Catalog Explorerを開く
* **Create a connection**からGoogle Drive用のUnity Catalog接続を作成する
* OAuth認可の画面が出るので、対象のGoogleアカウントで許可する
* 手順の詳細は公式ドキュメントを参照（[Google Driveからの取り込み](https://docs.databricks.com/aws/ja/ingestion/google-drive)）

### 取り込みコード

カード会社ごとにフォルダが分かれているケースを想定し、フォルダごとに個別のAuto Loaderストリーム（チェックポイントも別々）を立てて、同じBronzeテーブルに集約する構成にした。

```
GDRIVE_SOURCES = {
    "card_a": "https://drive.google.com/drive/folders/xxxx",
    "card_b": "https://drive.google.com/drive/folders/yyyy",
}

def start_bronze_stream(source_name, folder_url):
    raw_stream = (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "binaryFile")
        .option("databricks.connection", "google-drive-connection")
        .option("pathGlobFilter", "*.csv")
        .load(folder_url)
    )
    checkpoint = f"/Volumes/{CATALOG}/{SCHEMA}/_checkpoint/card_bronze_{source_name}"
    return (
        raw_stream.writeStream
        .option("checkpointLocation", checkpoint)
        .trigger(availableNow=True)
        .outputMode("append")
        .toTable(BRONZE)
    )
```

### ハマったポイント：`path`列はファイル名ではない

Google DriveをAuto Loaderで読むと、`path`列の中身はファイル名ではなくGoogle DriveのファイルID（`1h4YcvCxHclvW...`のような文字列）になる。ファイル名の末尾を`split`で取り出しても、出てくるのはファイルIDだけ。

```
# ❌ これだとファイルIDがそのままfilenameになる
df.withColumn("filename", element_at(split(col("path"), "/"), -1))
```

正しくは、標準の隠しメタデータ列`_metadata`から取る。

```
# ✅ 標準の隠しメタデータ列から実際のファイル名を取る
df.select("*", "_metadata") \
  .withColumn("filename", col("_metadata.file_name"))
```

Google Drive固有のメタデータ列`_gdrive_metadata`もあるが、こちらには`id`・`web_url`などは入っているものの、肝心のファイル名は含まれていない。紛らわしいので注意。

確認ポイント：

* `SELECT filename FROM bronze_table`を実行する
* → 実際のファイル名（`card_a_202606.csv`など）が出てくればOK
* ファイルID風の文字列が並んでいたら、上記の修正が反映されていない

## Silver：複数フォーマットへの対応

カード会社ごとにCSVの列構成やメタデータのキー名が違う（本記事ではカードA・カードBと呼ぶ）。そこで、メタデータのキー名でフォーマットを自動判定し、共通スキーマにマッピングする設計にした。

```
CARD_FORMATS = {
    "カード名": {"brand": "card_a", "column_map": {...}},
    "カード名称": {"brand": "card_b", "column_map": {...}},
}
```

型変換も一緒にやっている。`use_date`は文字列→日付、`amount`などの金額列は文字列→数値にキャストする。

```
df_all["use_date"] = pd.to_datetime(df_all["use_date"], format="%Y/%m/%d", errors="coerce")
df_all["amount"] = pd.to_numeric(df_all["amount"], errors="coerce")
```

#### コラム：ルールベースの代わりにAI関数という手もある

今回はメタデータのキー名を見て力技でフォーマット判定したが、Databricksには`ai_query`・`ai_extract`といったAI関数がある。スキーマを渡すだけで、LLMがテキストから該当項目を抽出してくれる。

```
SELECT ai_extract(raw_content, 'card_name STRING, use_date STRING, amount STRING')
FROM bronze_card_statement
```

今回は対象フォーマットが2種類だけで規模も小さかったため採用しなかったが、フォーマットの種類がもっと増える場合はこちらの方が簡潔かもしれません。

## Databricks MCPでGenie Spaceに接続する

### Genie SpaceをMCPサーバーとして公開する

**手順**

* GoldテーブルからGenie Spaceを作成する
* Genie Spaceの管理画面から、MCPサーバーとして公開する操作を行う
* 公開すると、次のようなMCPサーバーURLが発行される

```
https://<workspace-hostname>/api/2.0/mcp/genie/{genie_space_id}
```

* あわせて2つのツールが使えるようになる
  + `query_space`：質問を投げる
  + `poll_response`：投げた質問の結果を取得する（非同期のため2段階になっている）

### 認証：PAT（アクセストークン）を発行する

* Databricksのユーザー設定を開く
* **開発者** タブ → **アクセストークン** の管理画面に進む
* **新しいトークンを生成** をクリック
* コメント（用途メモ）と有効期限を設定する
* スコープは「すべてのAPI」ではなく、Genieに関連するスコープ（`genie`）だけに絞る
* 表示されたトークンをコピーする（この画面を閉じると二度と表示されないので注意）
* MCPクライアント接続の認証方式については公式ドキュメントも参照（[MCPをAIアシスタントおよびコーディングエージェントに接続する（個人アクセストークン認証）](https://docs.databricks.com/gcp/ja/agents/mcp/connect-clients)）

### Claude DesktopアプリにGenie MCP serverを追加する

**Claude Desktopアプリ**の`claude_desktop_config.json`に、`mcp-remote`というプロキシ経由でPATをヘッダーとして注入する設定を追加する。

* Claude Desktopを開く
* **Settings** → **Developer** タブ → **Edit Config** をクリック
* 開いた`claude_desktop_config.json`に、次の設定を追記する（既存の中身は消さない）

```
{
  "mcpServers": {
    "genie-store-sales": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://<workspace-hostname>/api/2.0/mcp/genie/{genie_space_id}",
        "--header",
        "Authorization: Bearer <PAT>"
      ]
    }
  }
}
```

* 保存後、Claude Desktopを完全終了する（macOSなら⌘+Q）
* 再起動する

### ハマったポイント：設定ファイルは他の環境設定と同居している

最新のClaude Desktopでは、この設定ファイルにMCPサーバー設定だけでなく、アプリの他の環境設定（Coworkの設定など）も同居している。既存の中身を消さず、同じ階層に`mcpServers`キーを追記する必要がある。

保存後はClaude Desktopを完全終了（macOSなら⌘+Q）して再起動する。

確認ポイント：

* チャット入力欄の下にツールアイコンが表示されていれば接続成功
* 「先月一番使った店は？」のように普通に質問する
* → Genie経由でSQLが自動生成され、ツール呼び出しの許可を求められる

## 動作確認

実際に「6月のカード利用を分析して」と聞いてみると、Genie Space経由でSQLが自動生成され、月合計・最高利用日・利用店舗数のスコアカードと、日別推移・店舗別ランキングのダッシュボードがその場で組み上がった。

![](https://static.zenn.studio/user-upload/c88eb97237f6-20260708.png)

Google Driveにファイルを置くだけで、翌日には自動でBronze/Silver/Goldが更新され、Claudeに話しかけるだけで分析結果が返ってくる状態になった。

## まとめ

| できたこと | 内容 |
| --- | --- |
| 自動取り込み | Google DriveのCSVをAuto Loaderで差分検知 |
| 複数フォーマット対応 | メタデータのキー名でカード会社を自動判定 |
| 自然言語分析 | Genie Space × Databricks MCP × Claude |

次にやりたいことは、以下の3つ：

* 同じ仕組みを給与明細にも横展開
* 固定費と変動費を分けて集計
* Claude Desktopで家計収支レポートを作成

この記事が同じようなことを試したい方の参考になれば嬉しいです！

最後までお読みくださりありがとうございました🙌

## 参考リンク
