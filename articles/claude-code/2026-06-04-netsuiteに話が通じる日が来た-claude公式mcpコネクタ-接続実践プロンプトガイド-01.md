---
id: "2026-06-04-netsuiteに話が通じる日が来た-claude公式mcpコネクタ-接続実践プロンプトガイド-01"
title: "NetSuiteに話が通じる日が来た。 ── Claude公式MCPコネクタ 接続〜実践プロンプトガイド"
url: "https://qiita.com/itan_63/items/fe525e384809ac35aa78"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "GPT", "qiita"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

## 先に結論

- NetSuite が公式提供する **AI Connector Service(＝MCPサーバー)** を使うと、**Claude から自然言語で NetSuite を照会・操作**できます。
- たとえば「**うちの顧客って何件いる？**」と聞くだけで、Claude が裏で SuiteQL を組み立てて実行し、「**約18,000件です**」と返します。
- 本記事は **接続(NetSuite側の準備 → Claude側の設定)→ 入門プロンプト → 応用(保存済み検索 / レポート / レコード操作 / SuiteQL)→ 効くプロンプトの書き方 → ガバナンス** まで通しで解説します。
- **対象読者**:NetSuite 管理者・業務担当(コードを書かない人)〜 開発者。前半は自然言語だけ、後半は SuiteQL まで踏み込みます。
- **検証環境**:claude.ai / Claude Desktop の公式 NetSuite コネクタ。

:::note info
本記事は **2026年6月時点** の情報です。NetSuite のメニュー名や Claude の UI はバージョンで変わります。最終的な手順は末尾の **Oracle 公式ドキュメント** で必ず確認してください。
:::

---

## 1. これは何？ 何ができる？

「NetSuite AI Connector Service」は、AI ツール(Claude / ChatGPT など)を **Model Context Protocol(MCP)** で NetSuite に直接つなぐ、NetSuite 公式のサービスです。接続すると、Claude から次のような「ツール」が呼べるようになります。

| 分類 | 代表的なツール | できること |
|---|---|---|
| 照会(SuiteQL) | `runCustomSuiteQL` / `getSuiteQLMetadata` | SuiteQL でデータ抽出(実行前にスキーマ確認) |
| 照会(保存済み検索) | `runSavedSearch` / `listSavedSearches` | 既存の保存済み検索を一覧・実行 |
| 照会(レポート) | `runReport` / `listAllReports` | 標準/カスタムレポートを実行 |
| レコード操作 | `getRecord` / `createRecord` / `updateRecord` | レコードの取得・作成・更新 |
| メタデータ | `getRecordTypeMetadata` | レコード型のフィールド定義を取得 |
| 会計基盤 | `getSubsidiaries` / `getAccountingBooks` / `getNexusIds` | 子会社・会計帳簿・税管轄の取得 |
| 補助UI | `selector_app` / `prompt_library_app` / `report_filters_app` | レコード選択・プロンプト集・レポート絞り込み |

:::note info
これらのツールを **どれをいつ呼ぶか** は Claude が自動で判断します。利用者は日本語でお願いするだけです。
:::

---

## 2. 仕組み(アーキテクチャ)

```mermaid
flowchart LR
    U[ユーザー] -->|日本語で依頼| C[Claude＝MCPクライアント]
    C <-->|MCP / OAuth 2.0| S[NetSuite AI Connector Service＝MCPサーバー]
    S <-->|SuiteScript / REST| N[(NetSuite アカウント)]
```

ポイントは3つです。

1. **MCPサーバーの実体は、あなたの NetSuite アカウント内にインストールする SuiteApp**(`MCP Standard Tools`)です。外部にデータの保管庫を建てるわけではありません。
2. **認証は OAuth 2.0**。Claude は「あなたが許可した専用ロールの権限の範囲」でしか動けません。
3. Claude は依頼を受けて **「メタデータ取得 → クエリ/REST生成 → 実行」** を自動で行います。だから利用者はスキーマを覚えていなくても大丈夫。

---

## 3. 事前準備(NetSuite 側)

接続の前に、NetSuite 管理者が3つの準備をします。

### 3-1. 機能(Features)を有効化

`設定 > 会社 > 機能を有効化`(Setup > Company > Enable Features)の **SuiteCloud** タブで、次を ON にします。

- **クライアント SuiteScript**(Client SuiteScript)
- **サーバー SuiteScript**(Server SuiteScript)
- **REST Web サービス**(REST Web Services)
- **OAuth 2.0**

### 3-2. SuiteApp をインストール

`SuiteApps` タブで **「MCP」** を検索し、**`MCP Standard Tools`** をインストールします。これがコネクタ(MCPサーバー)の本体です。

### 3-3. 専用ロールを作成

MCP 接続用の **専用カスタムロール** を作り、接続するユーザーに割り当てます。最小権限から始めるのがおすすめです(例:まずは REST Web サービス＋必要なレコードの「表示」権限のみ＝読み取り専用)。

:::note alert
**管理者(Administrator)ロールでは MCP 接続できません。** NetSuite がセキュリティ上ブロックしています。必ず専用ロールを作成してください。
:::

---

## 4. 接続手順(Claude 側)

### 4-1. コネクタを追加

Claude(claude.ai または Claude Desktop)で:

1. **設定 → コネクタ(Connectors)→ カスタムコネクタを追加**
2. 名前(例:`NetSuite`)と、**リモート URL** を入力:

```text
https://<accountid>.suitetalk.api.netsuite.com/services/mcp/v1/suiteapp/com.netsuite.mcpstandardtools
```

- `<accountid>` は自社のアカウントID。**Sandbox は `1234567-sb1` の形式**(アンダースコアはハイフン)になります。

3. **追加** を押すと OAuth の同意画面が出ます。**Associated Risks(関連リスク)を確認**のうえ許可し、接続に使う**専用ロール**を選びます。

:::note info
カスタムコネクタの利用可否は Claude のプランによって異なります(Pro / Max / Team / Enterprise など)。組織で使う場合は管理者にご確認を。
:::

### 4-2. NetSuite 側で連携レコードを「有効」にする

初回接続時、NetSuite に **Integration(統合)レコード**が自動生成されますが、**初期状態は Inactive(無効)** です。

➡ 該当レコードを開き、**State(状態)= Enabled(有効)** に変更して保存してください。

:::note warn
「接続したのにツールが使えない / 認証が通らない」の最頻出原因がこれです。**Integration レコードの State を必ず確認**。
:::

### 4-3. 動作確認

Claude にこう聞いてみましょう。

> NetSuite に接続できてる？ 使えるツールを一覧で教えて。

ツール一覧が返れば成功です。

### 4-4. つまずき早見表

| 症状 | 主な原因 / 対処 |
|---|---|
| ツールが出てこない | Integration レコードが **Enabled** か確認 |
| 認証がループ／弾かれる | 接続ロールが**管理者ではない**か、専用ロールに権限があるか |
| `Claude Code` から繋がらない | **既知の OAuth バグ**あり。現状は **Desktop / claude.ai** を使う |
| `Permission Violation` 等 | そのレコード/検索/レポートの権限がロールに無い |

---

## 5. まず触ってみる(入門プロンプト)

最初は **読み取り(照会)系** から。事故が起きません。

### 例1:件数を聞く

> うちの顧客レコードは何件登録されている？

Claude は裏でこう動きます(`getSuiteQLMetadata` でスキーマ確認 → `runCustomSuiteQL` 実行)。

```sql
SELECT COUNT(*) AS customer_count FROM customer
```

返ってきた実データ(マスキング済み):

```json
{ "data": [ { "customer_count": 18000 } ] }
```

> 現在 **約18,000件** の顧客レコードがあります。

### 例2:項目を日本語で把握する(コネクタの“目玉”)

> 顧客レコードにはどんな項目がある？ 日本語ラベルで主要なものを教えて。

`getRecordTypeMetadata("customer")` の実レスポンス抜粋(標準項目はラベルが日本語で返る／カスタム項目は汎用化):

```jsonc
{
  "companyName": { "title": "会社名",     "type": "string" },
  "email":       { "title": "電子メール", "type": "string" },
  "balance":     { "title": "残高",       "type": "number" },
  "creditLimit": { "title": "信用限度",   "type": "number" },
  "taxable":     { "title": "課税対象",   "type": "boolean" },
  "custentity_xxx": { "title": "(御社のカスタム項目ラベル)",
                      "type": "string", "x-ns-custom-field": true }
}
```

:::note info
**ここがすごいところ**:Claude は標準項目だけでなく、御社で追加した **`custentity_*` のカスタム項目もラベル付きで認識**します。つまり「自社用語」で会話できます。
:::

### 例3:条件付きで一覧

> アクティブな顧客を10件、会社名とメールアドレスで。

```sql
SELECT companyname, email
FROM customer
WHERE isinactive = 'F'
FETCH FIRST 10 ROWS ONLY
```

---

## 6. 一歩進んだ使い方(応用)

### 6-1. 保存済み検索を実行する

既存の保存済み検索(Saved Search)をそのまま走らせられます。

> 「未消込の請求書」っぽい保存済み検索を探して、上位20件を実行して。

Claude の動き:`listSavedSearches` で候補を探す → `runSavedSearch(searchId)`。一覧の各要素はこんな形です。

```json
{ "id": "customsearch1234", "title": "(検索名)", "recordtype": "transaction", "public": true }
```

### 6-2. レポートを実行する

> 2026年5月の損益計算書(P&L)を出して。

Claude の動き:

1. `listAllReports` で対象レポートと**必須パラメータ**を確認
   - `as_of_format=false` なら `dateFrom` と `dateTo` が**必須**
   - `has_subsidiary_filter=true` なら `subsidiaryId` が**必須**
2. 必要なら `getSubsidiaries` で子会社IDを取得(本検証環境は子会社1件＝シングル構成)
3. `runReport` を実行

:::note info
レポート系は「必須パラメータ」を外すとエラーになります。`listAllReports` を**先に**呼ぶのが定石(Claude は自動でやってくれます)。
:::

### 6-3. レコードの作成・更新(メタデータ駆動)

> 新規顧客「サンプル商事」を作りたい。必要項目を教えて、内容を確認してから作成して。

Claude の動き:

1. `getRecordTypeMetadata("customer")` で**必須項目と参照項目**を把握
2. 参照項目(子会社・税コード等)は **SuiteQL で内部IDを引く** か `selector_app` で選ばせる
3. 内容を提示 → あなたの「OK」後に `createRecord`

実際に生成されるデータ(イメージ):

```json
{
  "recordType": "customer",
  "data": "{ \"companyname\": \"サンプル商事\", \"subsidiary\": \"1\", \"email\": \"info@example.com\" }"
}
```

:::note alert
`createRecord` / `updateRecord` は **本番に即反映** されます。**まず Sandbox で試す**、そして Claude に必ず **「実行前に投入内容を表で見せて」** と指示してください。
:::

### 6-4. SuiteQL は“ふつうの SQL”と違う(ハマりどころ)

Claude が生成する SuiteQL を読む・直すときの注意点。

- **文字列連結は `||`**(`+` や `CONCAT` ではない)
- **`WITH`(CTE)は不可** → サブクエリで書く
- **日付は `TO_DATE('2026-05-01','YYYY-MM-DD')`**(Oracle 形式)
- **大量レコードはページネーション必須**(`customer` / `transaction` / `item` 等)。`pageSize=1000` で `pageIndex` をループ。**1クエリ最大5000行**
- **表示名が欲しいときは `BUILTIN.DF(フィールド)`**(例:`BUILTIN.DF(entity)` で得意先名)

```sql
-- 2026年5月の請求書を得意先別に集計(上位10件)
SELECT BUILTIN.DF(t.entity) AS customer,
       SUM(t.foreigntotal)  AS total
FROM transaction t
WHERE t.type = 'CustInvc'
  AND t.trandate >= TO_DATE('2026-05-01','YYYY-MM-DD')
  AND t.trandate <  TO_DATE('2026-06-01','YYYY-MM-DD')
GROUP BY t.entity
ORDER BY total DESC
FETCH FIRST 10 ROWS ONLY
```

:::note info
集計に使うフィールド名(`total` / `foreigntotal` 等)や符号(請求書はマイナス計上のことも)は環境差があります。**`getSuiteQLMetadata` で確認**してから使うのが安全です。
:::

---

## 7. 効くプロンプトの書き方

「なんとなく」より「具体的に」。指示の精度がそのまま結果の精度になります。

### 7-1. 良い例 / 悪い例

| ❌ 悪い例 | ✅ 良い例 |
|---|---|
| 売上を見せて | **2026年5月**の **請求書(invoice)** 合計を **得意先別・降順・上位10件** で。SuiteQLで。 |
| この顧客を更新して | 得意先「○○」の**内部IDを先に確認**してから、電話番号だけを更新して。**更新前に内容を提示**して。 |
| 全部出して | **全件対象**。多ければ**ページネーションして全件集計**して。 |
| 在庫を教えて | **アイテム別の在庫数**を、**ロケーション「東京」**だけ、**残数の少ない順**で20件。 |

### 7-2. 5つのコツ

1. **レコード型を英語名で**:`invoice` / `salesorder` / `customer` など。あいまいさが消えます。
2. **期間は `YYYY-MM-DD` で明示**:相対表現(先月)より誤解が減ります。
3. **段階で指示する**:`まず読み取りだけ → 内容確認 → 私のOKで書き込み`。
4. **参照は内部ID経由で**:「得意先名」より「内部IDを引いてから」と頼むと安定します。
5. **出力フォーマットを指定**:「Markdownの表で」「CSVでも」など。

### 7-3. コピペで使える“お作法”プロンプト

セッション冒頭にこれを貼っておくと、以降の挙動が安定します。

```text
あなたはNetSuiteオペレーターです。次のルールを守ってください:
- 取得はSuiteQLを基本に。高ボリューム(customer/transaction/item等)はページネーションして全件集計。
- 期間は YYYY-MM-DD で明示。レコード型は英語名(invoice, salesorder, customer ...)で扱う。
- 参照項目(得意先・アイテム・子会社等)は内部IDを先に確認してから使う。
- 作成・更新の前に、投入内容を必ず表で提示し、私の「OK」を待ってから実行。
- 結果はMarkdownの表で。件数も併記。
- エラー時は、実行したSuiteQL / パラメータも一緒に見せて。
```

---

## 8. 注意点・ガバナンス

- **最小権限ロールで縛る**:まず読み取り専用ロールで開始し、必要に応じて権限を足す。
- **書き込みは確認フロー＋Sandbox先行**:`createRecord`/`updateRecord` は本番即反映。
- **データの外部送信ポリシー**:照会結果は AI 側へ渡ります。社内のデータ取扱い規程・契約を確認。
- **監査**:誰が何をしたかは NetSuite の **システムノート / ログイン監査証跡**、接続自体は **Integration レコード**で管理。
- **コスト/レート**:大量クエリは API ガバナンスとトークンを消費。ページネーションと件数上限を意識。
- **公開時マスキング**:ブログ等に貼るときは **アカウントID・固有名・カスタム項目名**を伏せる。

---

## 9. まとめ

- NetSuite 公式の **AI Connector Service(MCP)** で、Claude から **自然言語 → SuiteQL/REST** の操作ができる。
- 接続の肝は **専用ロール(管理者不可)** と **Integration レコードを Enabled** にすること。
- 使い始めは **読み取り系から**。慣れてきたら **保存済み検索 → レポート → レコード作成/更新** へ。
- 効果を出す近道は **具体的な指示**(レコード型・期間・ID・段階・出力形式)。
- **書き込みは Sandbox と確認フロー** を徹底すれば、業務の強力な相棒になります。

---

## 付録A:よく使う SuiteQL スニペット

> ※フィールド名・ステータスコードは環境差があります。`getSuiteQLMetadata` で確認のうえご利用ください。

```sql
-- 顧客の総件数
SELECT COUNT(*) AS cnt FROM customer;

-- アクティブな顧客(会社名・メール)
SELECT companyname, email
FROM customer
WHERE isinactive = 'F'
FETCH FIRST 50 ROWS ONLY;

-- アイテムを種別ごとに件数集計
SELECT BUILTIN.DF(itemtype) AS item_type, COUNT(*) AS cnt
FROM item
GROUP BY itemtype
ORDER BY cnt DESC;

-- 当月の受注(salesorder)金額トップ10 得意先
SELECT BUILTIN.DF(t.entity) AS customer, SUM(t.foreigntotal) AS total
FROM transaction t
WHERE t.type = 'SalesOrd'
  AND t.trandate >= TO_DATE('2026-06-01','YYYY-MM-DD')
  AND t.trandate <  TO_DATE('2026-07-01','YYYY-MM-DD')
GROUP BY t.entity
ORDER BY total DESC
FETCH FIRST 10 ROWS ONLY;
```

## 付録B:参考リンク(一次情報)

- Oracle 公式:Connect to the NetSuite AI Connector Service
  https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_0714082142.html
- Oracle 公式:NetSuite AI Connector Service FAQ
  https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_4160616848.html
- NetSuite 製品ページ:What is the NetSuite AI Connector Service?
  https://www.netsuite.com/portal/products/artificial-intelligence-ai/mcp-server.shtml

## 付録C:推奨タグ

`NetSuite` `Claude` `MCP` `AI` `ERP` `SuiteQL`
