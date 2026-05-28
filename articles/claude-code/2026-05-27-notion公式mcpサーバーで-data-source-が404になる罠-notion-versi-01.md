---
id: "2026-05-27-notion公式mcpサーバーで-data-source-が404になる罠-notion-versi-01"
title: "Notion公式MCPサーバーで data_source が404になる罠 — Notion-Version の更新で解決"
url: "https://zenn.dev/hideakitamai/articles/962877887450a2"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "Python"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

自前の業務自動化基盤で動かしている議事録生成の Claude Code Skill が突然 timeout 連発で止まりました。Claude Code が headless で起動して Notion を操作するパイプラインです。

12時間かけて H1〜H10 の仮説検証を回した結果、真因は意外なところにありました。 **`.mcp.json` の `Notion-Version` が古いまま、 Notion 公式 MCP server ([@notionhq/notion-mcp-server](https://github.com/makenotion/notion-mcp-server)) のデフォルト設定と組み合わさって、新規 DB に対して 404 を返し続けていた** というものです。

同じ問題で詰まる人が他にもいるはずなので、真因の解説と、そこに至るまでの仮説検証ログを整理します。

**この記事が役に立つ人**

* Notion 公式 MCP server を使っていて、ある日突然「DB が見つからない」エラーが出始めた人
* Notion API 2025-09-03 リリースの `data_sources` 独立概念がよくわかっていない人
* Claude Code × MCP のパイプラインで真因切り分けに苦しんでいるエンジニア
* LLM ベースの自動化システムが詰まったときの仮説検証アプローチを参考にしたい人

# 結論：1行修正で解消する

先に結論。 `.mcp.json` の Notion-Version を更新するだけで解消します。

```
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{
-         \"Notion-Version\": \"2022-06-28\",
+         \"Notion-Version\": \"2025-09-03\",
          \"Authorization\": \"Bearer <NOTION_TOKEN>\"
        }"
      }
    }
  }
}
```

ただし、この1行修正に到達するまでに12時間かかりました。なぜなら:

1. 404 のエラーメッセージが `"Make sure the relevant pages and databases are shared with your integration"` という **共有設定問題を示唆する誤誘導** をしてくる
2. LLM の自己診断がそのメッセージを信じて「権限の問題」と報告してくる
3. 同時期に発生していた別の問題（バイナリアップグレード・PATH 不足・typo 顕在化）と症状が絡んで切り分けが難しい

以下、何が起きていたかを順に書きます。

# 何が起きていたか

## Notion API 2025-09-03 リリースで何が変わったか

2025-09-03 リリースの Notion API で、 `data_sources` が独立した概念として導入されました。それ以前は「database」が1つの概念でしたが、新しいモデルでは database が複数の data\_source を持てる構造に変わりました。

実用上の影響は以下です:

* 新規作成された DB は **`data_source_id` のみを持ち、従来の `database_id` を持たない**
* 旧エンドポイント `/v1/databases/{id}` と `/v1/databases/{id}/query` は、新しい DB の `data_source_id` を渡しても 404 を返す
* 新エンドポイント `/v1/data_sources/{id}` と `/v1/data_sources/{id}/query` は、`Notion-Version: 2025-09-03` 以降でないと「Invalid request URL」を返す

つまり、 **新規 DB は新しい Notion-Version でしかアクセスできない** 状態になっています。

## Notion 公式 MCP server のデフォルト設定が古いまま

Notion 公式の `@notionhq/notion-mcp-server`（npm 上の最新 v2.2.1）は、デフォルトの `Notion-Version` が `2022-06-28` のままです。 `OPENAPI_MCP_HEADERS` で上書きしない限り、この古いバージョンで Notion API を叩き続けます。

公式が出している MCP server を、 npm install するだけで普通に使う設定だと、新規 DB に対しては全クエリが 404 になります。

## エラーメッセージの誤誘導

旧 API endpoint で新規 DB を叩くと、Notion API は以下のレスポンスを返します:

```
{
  "object": "error",
  "status": 404,
  "code": "object_not_found",
  "message": "Could not find database with ID: xxx. Make sure the relevant pages and databases are shared with your integration."
}
```

この **"Make sure shared with your integration"** という文言が罠でした。私の Skill は LLM ベースで自己診断する作りになっていて、このエラーメッセージを読んで「integration の共有設定の問題」と報告してきました。

実際には共有設定は正しくできていて、 ID が `data_source_id` で旧 endpoint には存在しないだけだったのですが、 LLM が「もっともらしい説明」を構築する力が高い分、誤誘導されたメッセージから誤った診断を出してしまう構造です。

# curl 直叩きで真因を確認する

LLM の自己診断を信用せず、 curl で直接 HTTP コードと生レスポンスを確認したのが切り分けの決定打でした。

```
NOTION_TOKEN="<NOTION_TOKEN>"
DATA_SOURCE_ID="<DATA_SOURCE_ID>"

# 旧 API（落ちる）
curl -s -w "\nHTTP %{http_code}\n" \
  -X POST \
  -H "Authorization: Bearer ${NOTION_TOKEN}" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  "https://api.notion.com/v1/databases/${DATA_SOURCE_ID}/query" \
  -d '{"page_size": 1}'

# 新 API（成功）
curl -s -w "\nHTTP %{http_code}\n" \
  -X POST \
  -H "Authorization: Bearer ${NOTION_TOKEN}" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  "https://api.notion.com/v1/data_sources/${DATA_SOURCE_ID}/query" \
  -d '{"page_size": 1}'
```

結果:

| Endpoint | Notion-Version | HTTP | レスポンス |
| --- | --- | --- | --- |
| `/v1/databases/{id}` | 2022-06-28 | 404 | "Make sure shared..." |
| `/v1/databases/{id}/query` | 2022-06-28 | 404 | "Make sure shared..." |
| `/v1/data_sources/{id}` | 2025-09-03 | 200 | 正常 |
| `/v1/data_sources/{id}/query` | 2025-09-03 | 200 | 正常 |

これで完全に確定しました。 `.mcp.json` の Notion-Version を `2025-09-03` に上げて完了。

# 同じ罠を踏みうるパターン

このトラブルが特に厄介なのは、 **ある日突然詰まり始める** ことです。私のケースでは以下のような順序で症状が顕在化しました:

1. `.mcp.json` の Notion-Version は `2022-06-28` のまま、数ヶ月運用していた
2. 旧 DB（database\_id を持つ）に対しては旧 API で問題なく動いていた
3. 新しく作った DB（data\_source\_id のみ）を Skill が参照するようになった
4. 新規 DB が増えるにつれて 404 が増え始めた
5. ある日のクエリで失敗の比率が閾値を超えて、 timeout 連発で全停止

つまり、 `.mcp.json` の設定自体は何も変えていないのに、 **Notion 側で新規作成される DB の構造が変わったことで、後追いで壊れる** タイプの障害です。

同じ構造を持つ環境:

* Notion 公式 MCP server のデフォルト設定をそのまま使っている
* 自前で `Notion-Version` を指定していても、 `2025-09-03` より前のバージョンを使っている
* 自分のライブラリ層（直接 HTTP 叩き）と MCP 層で API バージョンを別管理している

特に最後の **「ライブラリ層と MCP 層で API バージョンが二重管理されている構造」** が見えにくくて怖いです。私のケースでも、自前の `notion_client.py` は `2025-09-03` で動いていたので、 MCP 経由じゃない観測パイプラインは無影響でした。 MCP 経由の議事録 Skill だけが壊れていて、 `.mcp.json` の方を見るまで気付けませんでした。

# 真因に至るまでの仮説検証ログ

H9（Notion-Version の問題）に到達するまでに、 H1〜H8 の仮説を順に検証して却下しました。 LLM ベースの自動化システムが詰まったときに、安易に思いつきの対策に走らず、データで仮説を一つずつ落としていくのは、結果的に最短の解法だったと思います。

参考までに、各仮説と却下理由を整理します。

| # | 仮説 | 結果 | 却下理由 |
| --- | --- | --- | --- |
| H1 | transcript が長すぎて重い | ❌ | 失敗 7,412 chars vs 成功 37,432 chars、文字数では説明できない |
| H2 | Claude Code バイナリ更新が原因（時系列ほぼ一致） | ❌ | 旧バイナリにダウングレードしても症状再現 |
| H3 | subprocess stdout blocking timeout | ❌ | Python 3.3+ では内部スレッドで read するため deadlock しない |
| H4 | timeout 値を延長すれば解決する | △ | 対症療法。真因が「無限に重くなった」なら被害を遅らせるだけ |
| H5 | MCP server 起動失敗 | △ | 観測されたが、 SSH non-interactive shell の PATH 不足が原因。本番 LaunchAgent は無影響 |
| H6 | `allowedTools` の typo（`API-post-data-source-query` → 正しくは `API-query-data-source`） | △ | 確かに typo はあったが、これは元から存在しており、 2025-09-03 まで偶然動いていただけ |
| H7 | API-query-data-source が "Invalid request URL" を返す | → | これが H9 への入口になった |
| H8 | Meeting Notes DB が 404、「integration 共有問題」と LLM が誤診断 | → | curl 直叩きで確認したら共有設定は正常、 ID が data\_source\_id だった |
| **H9** | **`.mcp.json` の Notion-Version が古い** | **✅ 主犯** | **curl で確定** |
| H10 | Skill 自体の固定オーバーヘッドが timeout ギリギリ | ✅ 共犯 | H9 修正後も 1200s timeout する場合あり。 timeout を 2400s に延長して暫定対応 |

H2（バイナリ更新が原因）と H6（typo）は特に紛らわしかったです。

**H2** はバイナリ更新の時系列（5/22 10:44）と症状発生（5/22 16:32〜）がほぼ完全に一致していました。これだけ見たら誰でも「バイナリのバグ」と思う。 2.1.96 にダウングレードして再計測したら症状再現したので H2 を落とせましたが、ダウングレード検証をやらなければここで時間を溶かしていました。

**H6** は確かに `watcher.py` の `allowedTools` に `API-post-data-source-query` という間違った名前が登録されていました（正しくは `API-query-data-source`）。これは **5/22 以前から既に存在していた typo** で、当時は無害でした（旧 API でも `databases/{id}/query` に data\_source\_id を投げると 200 が返ってきていたため）。新 DB が増えて 404 が増えてきたタイミングで、この typo も一緒に致命的になっていた、というオチでした。

正しいツール名は、 MCP server が公開しているツール一覧から確認できます。 MCP クライアントから `tools/list` を呼び出すと、 server 側が定義している正式名と引数スキーマが返ってきます。 Claude Code で MCP server を接続している環境なら、 `claude mcp list` で接続中の MCP server を確認し、 各 server の `tools/list` レスポンスを参照すれば公式の名前が分かります。 `allowedTools` に書く名前はこのレスポンスの `name` フィールドに合わせる必要があります。

**「過去 OK だった typo が突然顕在化する」** というパターンは他にも応用が効くと思います。 API バージョンが変わったタイミングで、長年無害だった既存コードが突然牙を剥く。

# LLM の自己診断の限界

今回の調査で痛感したのは、 **LLM ベースの自動化システムが詰まったとき、 LLM 自身に「何が悪い？」と聞いてもダメ** だということです。

Skill は 404 のエラーメッセージ `"Make sure shared with your integration"` を読んで、「integration の共有設定の問題」と報告してきました。これは LLM が「もっともらしい説明」を構築する能力の副作用です。

一次情報（HTTP レスポンス・システムログ・生データ）を **LLM を介さずに人間が確認する** 必要があります。今回も curl 直叩きで HTTP コードと生レスポンスを確認したのが、真因到達の決定打でした。

LLM ベースの自動化を本番運用するなら、 **LLM の自己診断レポートと、 LLM を経由しない一次情報の両方を出力する** 設計にしておくべきです。私の Skill は今のところ前者だけだったので、ここは次のメンテナンスで対応予定です。

# 公式パッケージのデフォルト設定を信用しない

もう一つの教訓は、 **「公式パッケージ = 最新の正しい設定」とは限らない** ということです。

Notion 公式 MCP server `@notionhq/notion-mcp-server` v2.2.1 のデフォルト Notion-Version が `2022-06-28` のままなのは、おそらく後方互換性のために残しているのだと思います。古いコードベースで動かしていたユーザーが、 npm update したら突然新 API に切り替わって壊れる、という事故を避けるための判断としては理解できます。

ただし、利用者側からすると、 **npm install で「最新の公式パッケージ」を入れた安心感の裏で、内部に古い設定が固定されている** のは罠です。設定ファイルの全項目を一度は目視で確認しておく習慣が必要です。

特に SaaS の API バージョンを扱うパッケージは要注意です。 Notion / Stripe / Slack / Google API など、バージョン管理を強制するすべての SaaS で同じ罠が起こりえます。

# クライアントが MCP server や SDK 経由のとき、 API バージョンが二重管理になる

これも今回の事故から見えた構造的な学びです。

普段、自前のコード（例: `lib/notion_client.py`）を持っていれば、 API バージョンの更新は1箇所だけで済みます。しかし、 **MCP server や SDK が間に挟まる構造** だと、そちらが古いヘッダーを使い続けていることに気付かないまま運用が進んでしまいます。

今回の私のケースでは:

* 自前の `notion_client.py` → `2025-09-03` で正しく更新済み（観測パイプライン群は無影響）
* Notion 公式 MCP server 経由の Skill → `.mcp.json` で `2022-06-28` 固定（致命的に壊れていた）

**「クライアント = 自分のライブラリ」だけ更新すればいい時代は終わった** という感覚があります。 MCP server を導入するなら、その内部で叩いている API のバージョン管理を自分で把握しておく必要があります。

# まとめ

Notion 公式 MCP server で `data_source` が 404 になる罠は、 `.mcp.json` の `Notion-Version` を `2025-09-03` 以降に更新する1行で解消します。

ただし、 そこに至るまでに以下の要素が絡んで時間がかかります:

* 404 エラーメッセージが「共有設定問題」を示唆する誤誘導をする
* LLM ベースの自動化システムだと、 LLM が誤誘導されたメッセージから誤診断する
* 自前ライブラリ層と MCP 層で API バージョンが二重管理されている構造に気付きにくい
* 既存の typo や設定ミスが、 API バージョン変更のタイミングで一斉に顕在化する場合がある

教訓を3つ:

1. **LLM の自己診断を信用せず、 curl で一次情報を取る**: HTTP コードと生レスポンスを LLM を介さずに確認する
2. **公式パッケージのデフォルト設定を一度は目視確認する**: 「公式 = 最新」とは限らない
3. **MCP server や SDK が間に挟まる構造では API バージョンが二重管理になる**: 自前コードだけ更新では不十分

LLM ベースの自動化システムを本番運用しているエンジニアにとって、似たような罠は他の SaaS（Stripe / Slack / Google API）でも起こりえます。同じ問題で詰まった人の役に立てば幸いです。

# 参考リンク

---

筆者：玉井秀明（Hide Tamai）

BAIOX取締役CMO / Goaico共同代表。医療AIと中小企業向けAI導入支援の両面でAI事業に関わっています。
