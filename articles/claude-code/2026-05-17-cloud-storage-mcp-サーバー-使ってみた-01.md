---
id: "2026-05-17-cloud-storage-mcp-サーバー-使ってみた-01"
title: "Cloud Storage MCP サーバー 使ってみた"
url: "https://zenn.dev/choshosu/articles/70798aebd6edaa"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "zenn"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

AIが作成した画像を一瞬で共有したい、画像の差し替えをAIと対話ベースで行いたい。そのようなユースケースにおいてCloud Storage MCPサーバーが便利そうだったので実際に使用してみました。

試した手順と実際に使用しての所感をまとめます。

## Cloud Storage MCP サーバーとは

Cloud Storage MCP サーバーは、MCPの仕様に沿って Google Cloud Storage のバケットに対する読み書きをAI クライアント側のツールとして公開してくれるサーバーです。  
普段は `gcloud storage cp` や `gsutil` で叩いていた操作を、Claude / Cursor / Claude Desktop などの MCP 対応クライアントから対話形式で呼び出せるようになります。

公式ドキュメントは下記です。

## セットアップ

Cloud Storage MCP は HTTP リモート版 (`https://storage.googleapis.com/storage/mcp`) と、`npx` で起動する **ローカル stdio 版** (`@google-cloud/storage-mcp`) の 2 系統があります。  
HTTP リモート版は Claude Code 側 SDK が OAuth Dynamic Client Registration を要求する一方、Cloud Storage 側が DCR 非対応のため `SDK auth failed: Incompatible auth server: does not support dynamic client registration` で弾かれます。  
そこで今回は **ローカル stdio 版** を使います。ADC (`gcloud auth application-default login`) でそのまま認証が通り、コマンド 1 つで済みます。

参考:

### 1. 事前準備

1. 書き込み先の Cloud Storage バケットを用意
2. 実行ユーザーに `roles/storage.objectViewer` / `roles/storage.objectCreator` を付与 (バケット新規作成も使うなら `roles/storage.admin`)
3. gcloud 認証 + プロジェクト指定（以下コマンド）

```
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=[GCP プロジェクト ID]
```

### 2. MCP サーバーの登録

Claude Code に Cloud Storage MCP (stdio 版) を登録します。

```
claude mcp add cloud-storage --scope user -- npx -y @google-cloud/storage-mcp
```

### 3. 動作確認

Claude Code 内で `/mcp` を叩き、`cloud-storage` が `connected` になり、`list_buckets` / `list_objects` / `read_object_content` / `upload_object_new` などのツールが見えれば OK。  
そのうえでバケット一覧を聞いてみます。

```
> バケット [バケット名] にあるオブジェクト一覧を教えて
```

## 実際にやってみた

### 1. AIが作成したdraw.ioのアーキテクチャ図をCloud Storageにアップロードする

普段は draw.io をAIに描いてもらった後、ローカルに保存して `gcloud storage cp` でアップロードしていたところを、対話だけで完結させます。

手順は次のとおりです。

1. AIにアーキテクチャ図を依頼する

   ```
   プロンプト例:
   > クリーンアーキテクチャの概要図を draw.io で描いて
   ```
2. AIが `architecture.drawio` を生成する

   * 作成された図  
     ![](https://static.zenn.studio/user-upload/5841d5acc334-20260517.png)
3. そのまま「これを Cloud Storage にアップロードして」と伝える

   ```
   プロンプト例:
   > いまの図を、バケット [バケット名] の architecture/ 配下にアップロードして
   ```
4. MCP 経由で `upload_object_new` ツールが呼ばれ、バケットに保存される  
   ![](https://static.zenn.studio/user-upload/b94038551ad6-20260517.png)

ここまでで「描いてもらう → 保存する」が終わります。

### 2. Webアプリの画像を差し替える

Web アプリで使っている画像を、AI と対話しながら差し替えます。

手順は次のとおりです。

1. 現在の画像をバケットから取得して状況を把握する

   ```
   プロンプト例:
   > バケット [バケット名] の [ファイルパス] を読み込んで内容を教えて
   ```
2. 新しい画像を生成してもらう

   ```
   プロンプト例:
   > いまの画像を、[変更内容（例: こっちの画像にして、○○をマスクして）]
   ```
3. 生成された画像で既存ファイルを上書きする

   ```
   プロンプト例:
   > いまの画像を、同じパスにアップロードして上書きして
   ```
4. Web アプリ側で再読み込みして表示確認する

## 所感

以上、Cloud Storage MCPサーバーの使用方法をまとめました。  
ここからは使ってみての所感をまとめます。

* 画像を `作る` から `アップロードする` までがシームレス
  + これまで作成した画像を手動やgcloudでアップロードしていたため、その手間が省けると結構快適だなと思いました。
  + 画像生成を使用する機会は多いですが、それを編集してアップロードするまでがシームレスなのは体験としてかなりよかったです。
* プログラムやコマンドが不要
  + 1つ目の感想と重なる部分ですが、いちいちコマンドを調べてアップロードするという手間が無いのは便利です。
  + また、アップロードするファイルが大量にある場合には一層便利だと感じています。
* Cloud Storageをハブとして使える
  + 今回の使用例では大きく取り上げませんでしたが、Cloud Storage MCPサーバーでは画像をアップロードするだけでなく、もちろん読み取りも可能です。
  + 一度アップロードしたファイルは使い捨てではなく、それを知識ベースとして使用することができます。

## まとめ

以上、Cloud Storage MCPサーバーについてまとめてみました。  
Cloud Storageは使う機会が多いものの、MCPサーバーを使用する必然性を感じたことはあまりありませんでしたが、場面によっては結構使えるなと思いました。本記事がどなたかの参考になれば幸いです！
