---
id: "2026-05-30-oci-db-tools-mcp-の3タイプをカスタムロールで権限分離してみた-01"
title: "OCI DB Tools MCP の3タイプをカスタムロールで権限分離してみた"
url: "https://qiita.com/asahide/items/860979ed23305aa4003b"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "LLM", "qiita"]
date_published: "2026-05-30"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

OCI Database Tools MCP（以下 OCI DB Tools MCP）には、1 つの MCP サーバの中に **3 種類のツールセットタイプ**（組込み SQL / Custom SQL Tool / Reporting Tool）を同居させられます。さらに **Application Role**（アプリケーション・ロール）で「どのユーザーにどのツールを見せるか」を制御できます。

本記事は、そのロール制御を実機で検証した記録です。具体的には、**業務ユーザー / アナリスト向けに Reporting Tool だけを見せるカスタムロール `MCP_Analyst`** を作り、

- `tools/list` から本当に Custom SQL Tool や組込み SQL ツールが消えるか
- ツールを絞ると **LLM（Claude）の選択挙動が意図どおり変わるか**

を確かめます。

### 1.1. シリーズの位置づけ

本記事は「いま重い SQL を 3 件教えて」シリーズの深掘り編です。

| 記事 | 主題 | OCI DB Tools MCP の扱い |
|------|------|------------------------|
| 前回記事: [4 経路で 3 ターン会話してみた](https://qiita.com/asahide/items/931a4d782f2cd986af45) | 4 つの NL2SQL / MCP 経路で Claude のツール選択を実測 | **4 経路のうちの 1 経路**として観測 |
| **本記事** | OCI DB Tools MCP 内部の 3 タイプとロール設計を深掘り | **1 経路の内部**を分解して実機検証 |

前回記事は「複数経路の比較」が主題で、OCI DB Tools MCP は登場する経路の 1 つにすぎませんでした。本記事は、その 1 経路の**内側**（3 タイプの同居とロールによる公開範囲制御）に絞って掘り下げます。

### 1.2. 検証ゴール

| # | 検証項目 | 達成判定 |
|---|----------|----------|
| 1 | カスタム Application Role でツール単位の公開範囲を制御できるか | `MCP_Analyst` で Reporting Tool のみに絞れた `tools/list` を取得 |
| 2 | ツールを絞ると LLM が Reporting 経路を自然に選ぶか | 「いま重い SQL を 3 件教えて」で `report_list` → `report_execute` を踏むか実測 |
| 3 | ツールを絞ると LLM の試行錯誤・正直さがどう変わるか | 前回記事（全ツール公開時）との対比で評価 |

### 1.3. 結論先出し

- ✅ **カスタムロールでツール単位の公開範囲を制御できた**。`MCP_Analyst` で見えるツールは `report_list` / `report_execute` / `request_status` の 3 つだけになり、Custom SQL Tool・組込み SQL はすべて除外できました。
- ✅ **Custom SQL Tool を選択肢から外すと、Claude は `report_list` → `report_execute` の多段を自力で踏みました**。前回記事で 0/4 だった Reporting 経路が、本検証では自然に選ばれました。
- ✅ **ツールを役割で絞ると LLM の試行錯誤が激減し、正直になりました**。該当レポートが無い問いには「無い」と即断し、できるフリをせず代替案を提示しました。
- ⚠️ **最大の落とし穴は「許可ロールが 2 層ある」こと**。ツール側のロールだけ設定して SQL レポート本体側を忘れると、`-32600 Invalid Request` で実行に失敗します（後述）。

:::note info
本記事のロール制御の話は OCI DB Tools MCP 固有の設定ですが、「ツールセットを役割で絞ると LLM の決定性・正直さが上がる」という示唆は MCP / エージェント設計全般に通じる内容です。
:::

---

## 2. 前提知識：3 タイプと Application Role（最小限のおさらい）

### 2.1. 3 種類のツールセットタイプ

[公式 Docs（MCP ツールセットの作成）](https://docs.oracle.com/ja-jp/iaas/database-tools/doc/creating-mcp-toolset.html) では、ツールセットは 3 タイプに分かれます。

| タイプ | 想定ユーザー（公式）| 代表ツール |
|-------|------------------|-----------|
| 組込み SQL | DBA 向け | `sql_run` / `schema_information` |
| Custom SQL Tool | 開発者向け | `GET_TOP_SQL_TOOL`（管理者が定義した固定 SQL）|
| Reporting Tool | ビジネスユーザー / アナリスト向け | `report_list` / `report_execute` / `request_status` |

Reporting Tool は「メタツール」で、`report_list` で登録済み SQL レポート一覧を取得し、`report_execute` で選んだレポートを実行する **2 段構成**になっています。

### 2.2. 既定の Application Role 3 種（公式定義）

[公式 Docs（アプリケーション・ロール）](https://docs.oracle.com/ja-jp/iaas/database-tools/doc/application-roles.html) では、既定で 3 ロールが用意されています。

| ロール | 公式説明（要約）|
|-------|----------------|
| MCP_User | SQL レポート・ツールセットおよびすべての SQL レポートの基本ツール |
| MCP_Operator | すべてのツールセットおよびすべての SQL レポートのすべてのツール |
| MCP_Administrator | MCP サーバーを管理するツールを有効化 |

既定ロールは「あらかじめ用意された粒度」です。本記事では、これらに加えて**自分で粒度を決められるカスタムロール `MCP_Analyst`** を作り、「Reporting Tool だけを見せる」という既定ロールには無い絞り込みを実現します。ここからが本題です。

---

## 3. 検証環境と構成

### 3.1. 検証環境

| 項目 | 値 |
|------|-----|
| OCI リージョン | `ap-tokyo-1` |
| データベース | Oracle AI Database 26ai EE 23.26.2.1.0（Autonomous Database）|
| MCP サーバ | `dbtools-mcp-server`（既存を流用）|
| クライアント | Claude Desktop（Code モード）|
| モデル | Claude Sonnet 4.6 Medium |
| 認証 | OAuth（PAT 不要。ロール切替後は Claude Desktop を再起動するだけ）|

:::note info
本検証のプロンプト（T1〜T3）はすべて Claude Desktop の **Code モード**で実行しました。Code モードでは遅延ツール（ToolSearch）やスキル機構が動くため、後述の試行錯誤の観察ではこの点を考慮しています。
:::

### 3.2. 3 タイプを同居させた構成

`dbtools-mcp-server` には 3 タイプのツールセットを同居させています。MCP_User で接続したときに見えるツールは以下のとおりです。

| ツール | タイプ |
|--------|-------|
| `schema_information` | 組込み SQL |
| `sql_run` | 組込み SQL |
| `GET_TOP_SQL_TOOL` | Custom SQL Tool |
| `report_list` / `report_execute` / `request_status` | Reporting Tool（メタツール）|

この状態を出発点に、カスタムロールで Reporting Tool だけに絞り込んでいきます。

---

## 4. Application Role で公開範囲を絞る

### 4.1. カスタムロール `MCP_Analyst` を作る

設計意図はシンプルで、**「業務ユーザー / アナリストには Reporting Tool だけを見せる」** 運用パターンの実現です。Custom SQL Tool と組込み SQL（生 SQL 実行）は除外します。

操作場所は以下です。

```
OCI コンソール
  > アイデンティティとセキュリティ > ドメイン > Default
  > Oracle Cloud Services > dbtools-mcp-server
  > アプリケーション・ロール > 「ロールの追加」
```

![phase6_custom_role_create.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/42ad0786-7b3f-48e6-bb73-04f823813121.png)


ここで最初の発見です。

:::note warn
**ロール作成画面には「名前」と「説明」しか入力欄がありません。** ロール側でツール許可を設定する場所は無いのです。「どのロールにどのツールを見せるか」は、**ツールセット側の各ツールの「許可ロール」**で 1 ツールずつ設定します。ロールはあくまで「入れ物」で、許可の紐付けはツールセット側で行う、という構造です。
:::

ロールを作ると、App Roles 一覧に `MCP_Analyst` が追加されます。

![phase6_role_created.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/71078c58-4f6f-4fd5-a98c-424066c25739.png)


### 4.2. ツールセット側でツールごとに許可ロールを付与する

紐付けはツールセット側で行います。各ツールの「許可ロール」のドロップダウンに、**既定 3 ロールに加えてカスタムロール `MCP_Analyst` が選択肢として現れます**。

![phase6_tool_role_selector.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/8eca72c9-d4af-47ad-81fa-e17173dc6ad2.png)


これが「カスタムロールでツール単位の公開範囲を制御できる」ことの決定的な証拠です。当初は「カスタムロールではツール単位の許可・拒否が表現できないのでは」という懸念がありましたが、実機では問題なく表現できました。

Reporting Tool 系のツール（`report_list` / `report_execute` / `request_status`）の許可ロールに `MCP_Analyst` を追加します。

![phase6_reporting_roles.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/be4e061f-4db6-490c-ae3a-9cdd880269a4.png)


一方、`GET_TOP_SQL_TOOL`（Custom SQL Tool）/ `sql_run` / `schema_information`（組込み SQL）の許可ロールには `MCP_Analyst` を**追加しません**。これで Reporting Tool だけが見える構成になるはずです。

### 4.3. 落とし穴：許可ロールは「2 層」ある（最重要）

ここが本検証で最もハマったポイントです。上記の設定を終えて `MCP_Analyst` で接続し、「いま重い SQL を 3 件教えて」を投げると、**`report_list` / `report_execute` が `-32600 Invalid Request` で落ちました**。

![phase6_t1_fail.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/8918871c-9f2b-4d7d-b2e2-c0ce1e6e343c.png)


原因は、**許可ロールが 2 層構成**になっていることでした。

| 層 | 設定対象 | 設定場所 |
|----|---------|---------|
| ① ツール層 | `report_list` / `report_execute` / `request_status` の許可ロール | ツールセット編集画面 |
| ② SQL レポート層 | **SQL レポート本体（`top-sql-by-elapsed`）の許可ロール** | DB Tools > SQL レポート画面 |

①だけ設定して②を忘れると、そのロールから**見えるレポートが 0 件**になり、`report_list` / `report_execute` がレポートを引けずに `-32600` で失敗します。今回は SQL レポート `top-sql-by-elapsed` の許可ロールが `MCP_User` のみだったため、`MCP_Analyst` を追加して解消しました。

![phase6_report_role_added.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/bc841200-b108-4964-a6cf-3cc227006725.png)

:::note alert
**`-32600 Invalid Request` は権限不足の 403 ではなく、protocol レベルのエラーで返ります。** そのため原因が「権限」だと気づきにくいです。
:::

### 4.4. `MCP_Analyst` の `tools/list` 確認

②まで設定したうえで、自分のユーザーを既定 3 ロールから全解除し `MCP_Analyst` のみ付与して接続すると、`tools/list` は意図どおりになりました。

| # | ツール名 | タイプ | 期待 | 実機 |
|---|---------|-------|------|------|
| 1 | `schema_information` | 組込み SQL | 見えない | ✅ 消えた |
| 2 | `sql_run` | 組込み SQL | 見えない | ✅ 消えた |
| 3 | `GET_TOP_SQL_TOOL` | Custom SQL Tool | 見えない | ✅ 消えた |
| 4 | `report_list` | Reporting メタ | 見える | ✅ 見える |
| 5 | `report_execute` | Reporting メタ | 見える | ✅ 見える |
| 6 | `request_status` | Reporting メタ | 見える | ✅ 見える |

![phase6_analyst_tools.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/98123e26-0115-4662-9ecd-ab56576fb820.png)


見えるのは `report_list` / `report_execute` / `request_status` の 3 つだけ。**Custom SQL Tool・組込み SQL はすべて除外**できました。検証ゴール 1 は達成です。

---

## 5. LLM の選択挙動は意図どおり変わったか

ここからが本記事の核心です。ツールを Reporting Tool だけに絞った状態で、3 つのプロンプトを新規セッションで投げ、Claude の選択挙動を観察しました。

:::note info
本検証では別 MCP（`adb-dba-copilot`）が切断中のため、**OCI DB Tools MCP 単独での選択挙動が純粋に観測できます**（前回記事のような「別 MCP にツールを取られる」現象が起きません）。
:::

### 5.1. T1「いま重い SQL を 3 件教えて」→ Reporting 経路を自力で選択

前回記事と同じプロンプトです。前回記事では `report_execute` が **0/4** で選ばれず、Custom SQL Tool（`GET_TOP_SQL_TOOL`）が名前マッチで選ばれていました。

本検証では Custom SQL Tool を除外しているため、Claude の動きは次のようになりました。

| 観点 | 内容 |
|------|------|
| ツール呼び出し順 | `report_list` → `report_execute`（reportId=`top-sql-by-elapsed`、変数 N=3）|
| 最終回答の出典 | `report_execute`（重い SQL トップ 3 を表で返答）|
| 仮説どおりか | ✅ 仮説どおり。**Reporting 経路の 2 段を自力で踏んだ** |

返ってきた重い SQL トップ 3 は以下で、会話冒頭に直接 `sql_run` で取得した値と一致しました。

| SQL_ID | Elapsed |
|--------|---------|
| `abqas1gw8a90r` | 255.97 s |
| `0db4fyjk09pdf` | 233.17 s |
| `4jussyy8s2rnm` | 216.12 s |

![phase6_t1_result.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/10a27ea5-8ab3-426c-8e89-747c68ee291e.png)


**前回記事で 0/4 だった Reporting 経路が、Custom SQL Tool を外すだけで自然に選ばれた** ことになります。これは本検証の事前仮説「Custom SQL Tool を選択肢から外せば、LLM は名前マッチで選ぶ先がなくなり、`report_list` → `report_execute` の経路を選ぶ」の実機確認です。

### 5.2. T2 / T3「該当レポートが無い」問い → 正直に代替案を提示

次に、登録レポート（`top-sql-by-elapsed` の 1 件のみ）に**該当しない**問いを 2 つ投げました。

**T2「業務向けの売上レポートを出して」**

| 観点 | 内容 |
|------|------|
| ツール呼び出し順 | `report_list` のみ（1 ツール）|
| 観察 | `report_list` で登録レポートが重い SQL 用 1 件のみと確認 → **「売上レポートは未登録」と正直に報告**。レポート新規登録 / その場で SQL 実行 の 2 案を提示し、対象テーブル・集計軸・期間を逆質問。Custom SQL Tool を探す試行錯誤やハルシネーションは無し |

![phase6_t2_result.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/a0148e3d-e0c0-42d9-9ab9-fccfc9abdb02.png)


**T3「テーブル一覧を見せて」**

| 観点 | 内容 |
|------|------|
| ツール呼び出し順 | `report_list` を参照（実行ツールなし）|
| 観察 | `schema_information` / `sql_run` は除外済み。「Reporting Tool しかなく、テーブル一覧用レポートも未登録」と**制約を明示**。レポート登録 / SQLcl・SQL Developer / OCI コンソールの 3 案を提示。**任意 SQL を実行できないことを正直に説明し、できるフリをしなかった** |

![phase6_t3_result.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/ebe285f8-25df-420e-8cab-5c6fa94ff9e3.png)


### 5.3. 前回記事（全ツール公開時）との対比

前回記事のセッション 4「全ツール ON」で曖昧な問いを投げたとき、Claude は **9 ツールを試行錯誤**しました。本検証との差は明確です。

| 観点 | 前回記事・全ツール ON | 本記事・MCP_Analyst（Reporting のみ）|
|------|---------------------|------------------------------------------|
| 試したツール数 | 該当ツールが曖昧な問いで 9 ツールを試行錯誤 | T1: 2 / T2: 1 / T3: `report_list` 参照のみ |
| 「使えるツールがない」発話 | ─ | T2・T3 で「該当レポートが無い／任意 SQL は不可」と正直に明示 |
| ハルシネーション | ─ | 無し |

**ツールセットを役割で絞ると、Claude は迷いなく「無い」と判断し、試行ツール数が激減しました。** これは検証ゴール 3 の結果です。

---

## 6. 考察

### 6.1.「業務ユーザーには Reporting Tool だけ」は両得だった

- カスタムロール `MCP_Analyst` で、`tools/list` を Reporting Tool の 3 ツールだけに絞れました。Custom SQL Tool・組込み SQL はすべて除外できており、これは単なるアクセス制御として機能しました。
- さらに副次効果として、ツールを絞ったことで Claude の試行ツール数が激減し（前回記事の 9 → 本検証は最大 2）、該当レポートが無い問いには正直に「無い」と答えました。
- 選択肢が少ないほど LLM の探索空間が狭まり、名前マッチで誤ったツールに飛ぶ余地が減るため、決定性・正直さが上がったと考えられます。これは OCI DB Tools MCP 固有ではなく、MCP / エージェント設計全般に通じると想定してます。

つまり **Application Role でツールセットを役割相当に絞ることは、アクセス制御（安全面）と回答品質（LLM の決定性・正直さ）の両面でメリットがある**、というのが本検証の中心的な示唆です。

### 6.2. 最大の注意点は「2 層の許可ロール」

- Reporting Tool の許可ロールは ①ツール層と ②SQL レポート本体層の 2 層構成です。①だけ設定して②を忘れると、見えるレポートが 0 件になり `report_list` / `report_execute` が `-32600 Invalid Request` で失敗します。
- この `-32600` は protocol レベルのエラーで、403（権限不足）として返らないため原因が分かりにくく、クライアント再起動でも直りませんでした。OCI コンソールで SQL レポートを直接実行するか、レポート本体の許可ロールを確認するのが切り分けの近道です。

カスタムロールで Reporting Tool を運用する場合は、**ツールとレポート本体の両方に許可ロールを付与する**のがセットだと覚えておくと、同じハマりを避けられます。

---

## 7. まとめ

| ポイント | 結果 |
|---------|------|
| カスタムロールでツール単位の公開範囲を制御できるか | ✅ できた。ロールは「入れ物」、許可はツールセット側で 1 ツールずつ付与 |
| Reporting Tool だけに絞れたか | ✅ `MCP_Analyst` で `report_list` / `report_execute` / `request_status` の 3 ツールのみ |
| LLM は Reporting 経路を自然に選ぶか | ✅ Custom SQL Tool を外すと `report_list` → `report_execute` を自力で踏んだ（前回記事では 0/4）|
| ツールを絞ると LLM の挙動は変わるか | ✅ 試行ツール数が激減（9 → 最大 2）、該当なしの問いには正直に「無い」と回答 |
| 注意点 | ⚠️ 許可ロールは 2 層。SQL レポート本体側を忘れると `-32600` で失敗 |

「業務ユーザーには Reporting Tool だけを見せる」という運用は、Application Role で実機実現でき、しかも LLM の回答品質まで良くなる、という結果でした。



---

## 参考

- [MCP サーバーの作成（Oracle Database Tools Docs）](https://docs.oracle.com/ja-jp/iaas/database-tools/doc/creating-mcp-server.html)
- [MCP ツールセットの作成（Oracle Database Tools Docs）](https://docs.oracle.com/ja-jp/iaas/database-tools/doc/creating-mcp-toolset.html)
- [アプリケーション・ロール（Oracle Database Tools Docs）](https://docs.oracle.com/ja-jp/iaas/database-tools/doc/application-roles.html)
- 前回記事: [4 経路で 3 ターン会話してみた](https://qiita.com/asahide/items/931a4d782f2cd986af45)
