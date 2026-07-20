---
id: "2026-07-20-ai-エージェントはあなたの-db-の意味を知らない-postgresql-に書いた意味を渡す-ko-01"
title: "AI エージェントは、あなたの DB の「意味」を知らない — PostgreSQL に書いた意味を渡す Kozou の紹介"
url: "https://zenn.dev/takashi_m_jp/articles/5223da58abc329"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "TypeScript", "zenn"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-rss"
query: ""
---

> 🔗 この記事は <https://blog.tak3.jp/ja/blog/introducing-kozou/> からの転載です（一次情報源）。

[basou](https://basou.dev) の紹介記事の結びに、こう書いた。「エージェントに『DB が何を意味するか』を渡す側の Kozou という別プロジェクトも公開している。こちらも稿を改めて紹介する」。本稿がその稿だ。

紹介するのは [Kozou](https://kozou.org)。ひとことで言えば、**PostgreSQL データベースの「意味」を AI エージェントに渡すためのオープンソースのツール**だ。README の冒頭にはこうある — "Give your AI agent the *meaning* of your PostgreSQL database, not just its columns."（列だけではなく、データベースの*意味*を AI エージェントに）。スキーマに書かれた `COMMENT ON` のテキスト、ビュー定義、型情報 — そこに埋まっている意味を読み取り、[MCP](https://modelcontextprotocol.io)（AI エージェントに外部ツールをつなぐ標準プロトコル）経由でエージェントに渡す。

## 列は読めるが、意味を知らない

AI エージェントに DB を触らせると、すぐに気づくことがある。エージェントはスキーマを読むのがうまい。テーブルを列挙し、列と型を並べ、それらしい JOIN を組み立てる。それでも間違う。**もっともらしく、間違う。**

Kozou の quickstart に同梱されているデモスキーマ（小さなオンラインストア）が、この間違い方をよく再現している。`orders` テーブルには `amount_total numeric(12,2)` という列がある。合計金額。売上を聞かれたエージェントがこの列を `SUM` したくなるのは自然だ。だがこの列は、**アプリケーションが更新をやめた古い非正規化キャッシュ**で、明細と食い違い得るし、テスト注文も混ざっている。`status` 列には `'paid'` も `'refunded'` も `'chargeback'` も入るが、売上として数えてよいのは `'paid'` だけ — 後の2つは、売上の取り消しだ。

こうした知識は、列名・型・制約 — 構造そのもの — のどこにも現れない。普段それがどこにあるかといえば、データディクショナリか、社内 wiki か、誰かの頭の中だ。エージェントは目の前の構造から「もっともらしい」クエリを書く。もっともらしさと正しさの差分を埋めるものが、この「意味」である。

## 意味の置き場は、最初から DB にある

ここで新しい仕組みを持ち出す前に、確認しておきたいことがある。PostgreSQL には、意味を書く場所が最初からネイティブに用意されている。

`COMMENT ON` だ。Kozou はここに書き方の規約を足している。意味づけの中心は `@ai` / `@policy` / `@example` の3つ — ほかに Admin UI 向けの `@widget` などもある。デモスキーマの実物はこう書いてある（読みやすさのため折り返しのみ調整）。

```
COMMENT ON TABLE orders IS 'Customer orders.
@ai: An order is recognized revenue only when status = ''paid''
  AND is_test = false AND deleted_at IS NULL and its customer is not
  soft-deleted; value each line at order_items.unit_price
  (the captured price), not products.list_price.
@ai: The vw_recognized_revenue view already applies every one of these
  rules — start there for any revenue question.
@policy: ''refunded'' and ''chargeback'' reverse a sale;
  never count them as revenue.';
```

そしてビュー。「正しい売上の出し方」を知っているのが人間の頭の中なら、それをビューとして定義してしまえば、**名前の付いた、実行可能な概念**になる。デモスキーマの `vw_recognized_revenue` は「認識済み売上の正本」であり、テスト注文の除外も、論理削除の考慮も、明細単価での評価も、定義に織り込んである。

意味を DB 自身に書く — この習慣は Kozou 以前の話で、単体で価値がある。書いた瞬間から、意味はスキーマと同じ場所に住み、スキーマと一緒にマイグレーションされる一次情報になる。

だが、書いただけではエージェントに届かない。生の接続でも、エージェントがカタログを掘れば `COMMENT` は読める。しかし、掘るかどうかはエージェント任せだ。どこに何が書いてあるか、どのビューが「正」か、どのルールが助言でどれが強制か — それを教えてくれるものは、素の接続にはない。

## その意味を、そのまま渡す — ここが Kozou

先に、Kozou が DB に対して何を*しない*かを言っておく。新しいメタデータストアを立てるものではない。DB に元からある `COMMENT` とビュー定義を**読むだけ**で、独自のテーブルは作らず、DDL も実行しない（Kozou はマイグレーションツール非依存で、マイグレーションが作ったスキーマをコンパイルするだけだ）。外せば、ただの PostgreSQL に戻る。

その上で、Kozou は PostgreSQL スキーマを読み、`COMMENT ON` テキスト・ビュー定義・型情報を、**要約も言い換えもせず**（README の言葉では *verbatim*）、タグ別に構造化して MCP からエージェントに渡す。エージェント側から見えるのは、こういうツール群だ。

* `list_tables` / `describe_table` — テーブルの一覧と、1テーブルずつのスキーマ全体 + COMMENT
* `list_views` / `describe_view` — ビューの列・目的・基底テーブル、そして**定義 SQL そのもの**
* `list_concepts` / `get_concept_context` — ビューを「ドメイン概念」として扱い、関連テーブルと推奨クエリ経路を返す
* `describe_functions` — 公開された RPC アクションの列挙
* `search_schema` — 名前・ラベル・COMMENT 本文・`@ai`/`@policy` ノート・enum メンバーを横断するメタデータ検索

たとえば `search_schema` に "revenue" と投げると、`vw_recognized_revenue` というビュー名と、`amount_total` に付いた「レポートに使うな」の COMMENT が、名前と本文の両方からヒットして返る。スキーマ全体を `describe` して回らずに、その語に関わる意味の在り処が分かる。

既定は describe 系のみ、つまり読むだけだ。実行系の `call` が現れるのは、設定ファイル（`kozou.config.yaml`）で `server.mcp.execution` を明示的に有効化し、実行に使う role を指定したときだけ。CLI のフラグで切り替わるものではなく、素の `kozou mcp` はつねに describe-only のままだ — 実行できる状態は、運用者が設定として選び取ったときにだけ成立する。

`describe_table("public.orders")` が実際に返すものの断片（デモスキーマの実物・抜粋。読みやすさのため文字列を折り返している）:

```
{
  "name": "amount_total",
  "dataType": "numeric(12,2)",
  "aiDescription": "Do NOT use this for reporting — it is a stale cache
    the application stopped maintaining, can disagree with the line items,
    and includes test orders. Compute revenue from vw_recognized_revenue
    instead."
},
{
  "name": "status",
  "enumValues": ["cart", "pending", "paid", "refunded", "chargeback"],
  "aiDescription": "Only 'paid' is a captured sale; 'cart' and 'pending'
    are not sales yet; 'refunded' and 'chargeback' reverse a prior sale."
}
```

さっきの罠が、列のすぐ隣に、エージェントへの注意書きとして届いている。`COMMENT ON` の中の `@ai:` 行が `aiDescription` に、`@policy:` 行が `policy` に。書いた意味が、書いたとおりの言葉で、構造化されて手元に来る。この注意書きを受け取ったエージェントは、`amount_total` の意味を推測でつなぐ代わりに、正本と宣言されたビュー — `vw_recognized_revenue` — へ向かえる。

リレーションも同じだ。`get_concept_context` は、ビューの基底テーブル間に**実在する外部キー**から JOIN 候補を導出し、FK 制約に付けた COMMENT を、その JOIN の「目的」として添える。FK 制約に COMMENT を書いていれば、こういう提案が返る（この断片は例示だ — デモスキーマは FK 制約に COMMENT を付けていないため、そのまま叩くと `purpose` は空で返ってくる）。

```
"joinSuggestions": [
  {
    "table": "public.customers",
    "on": "orders.customer_id = customers.id",
    "purpose": "the customer who placed the order"
  }
]
```

`ON` 条件は機械が導ける。だが「この JOIN は何のためにあるのか」は、FK 制約の COMMENT に人間が書いた意味のほうだ。両方を1つの提案として渡す。

ひとつ、設計上の一線がある。**Kozou は意味を渡すが、強制はしない。** `@policy` はエージェントへの助言（advisory）であり、実際のアクセス制御は PostgreSQL 側 — 権限と行レベルセキュリティ（RLS） — に残る。Kozou は RLS が有効かどうかは伝えるが、ポリシー式そのものはエージェントに出さない。意味の供給と権限の施行を混ぜない、という線引きだ。

## 1つの定義から、多くの忠実な形へ

MCP はいちばんの差別化点だが、出口のひとつでもある。Kozou は同じスキーマの読み取りから、管理用の Admin UI、REST + OpenAPI、Markdown ドキュメント、TypeScript 型も生成する。スキーマとコメントという**1つのソース**から、人間と AI が必要とする形をすべて導出する — 定義の重複がなければ、ドリフトもない。この「ワンソースマルチユース」という構えの話は、それだけで1本書けるので稿を改める。

## 10分で始める

```
git clone https://github.com/kozou-dev/kozou
cd kozou/examples/quickstart
cp .env.example .env
docker compose up
```

これで、さっきの罠を仕込んだデモスキーマ入りの PostgreSQL と `kozou dev` が立ち上がる。Admin UI が `http://localhost:3333`、MCP サーバーが `http://localhost:3334/mcp` だ。

Docker スタックなしで、手元の DB に対して stdio で試すなら:

```
DATABASE_URL=postgres://user:pass@localhost:5432/mydb npx -y kozou mcp --stdio
```

自分のプロジェクトとして始めるなら:

```
npx -p kozou create-kozou my-project
```

クライアント別の MCP 設定・remote MCP（OAuth）のガイド・リファレンスは [kozou.org](https://kozou.org) にまとまっている。手順の再掲はしない — *どうやるか* はドキュメントが source of truth だ。

## まとめ

* AI エージェントは列と型を読めるが、その「意味」— どの列が罠で、どのビューが正か — は列名と型に現れない。もっともらしくて間違ったクエリは、ここから生まれる
* 意味の置き場は PostgreSQL に最初からある。`COMMENT ON` とビュー定義。**まず意味を DB に書く** — これは Kozou 以前の、単体で効く習慣だ
* Kozou はその意味を、要約も言い換えもせず MCP からエージェントに渡す。列の隣に注意書きが、JOIN に目的が、概念に推奨クエリ経路が付いてくる。そして意味は渡すが、強制は PostgreSQL に残す

リポジトリは [github.com/kozou-dev/kozou](https://github.com/kozou-dev/kozou)（Apache-2.0）、ドキュメントは [kozou.org](https://kozou.org)。執筆時点の最新は v1.15.1 だ。使ってみて引っかかった点は、Issue で教えてもらえるとありがたい。

英語版（この記事の「対」になる記事）も近く公開する。
