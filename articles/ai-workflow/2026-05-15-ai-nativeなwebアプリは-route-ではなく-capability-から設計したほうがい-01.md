---
id: "2026-05-15-ai-nativeなwebアプリは-route-ではなく-capability-から設計したほうがい-01"
title: "AI-nativeなWebアプリは route ではなく capability から設計したほうがいい"
url: "https://zenn.dev/53able/articles/5e32c6e5a4b511"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

# Piの思想でWebフレームワークを作る: capability-firstな AI-native application layer 構想

Web アプリに AI を組み込む話は増えました。ですが、実装に入ると次の壁がすぐに出ます。

* チャット UI を足せば AI-native と呼べるのか
* LLM にどこまで権限を渡してよいのか
* DB 更新やメール送信をどう安全に扱うのか
* Next.js や Rails の上に、どんな形で AI を載せるのか

私はこの問いに対して、Pi の設計思想を Web フレームワークへ持ち込む形が有力だと考えています。

この記事の主張は一つです。

**Web アプリを「画面と API の集合」としてではなく、LLM が安全に呼べる capability の集合として設計する。**

この考え方を取ると、AI を後付けの便利機能として足すのではなく、AI が操作することを前提にした application layer を設計できます。

!

この記事は次の読者を想定しています。

* AI agent を業務システムに入れたい方
* LLM に backend を触らせたい方
* 既存の Web フレームワークの上に AI 層を足したい方

## まず Pi とは何か

Pi は AI agent を動かすための harness です。

harness という言葉が分かりにくければ、「AI が仕事を進めるための土台」と考えてください。モデルそのものではなく、モデルに何をさせ、どんな道具を持たせ、状態をどう管理し、UI とどうつなぐかを扱う実行基盤です。

Pi の公式サイトは Pi を `minimal terminal coding harness` と説明しています。つまり Pi は、最初から全部入りの巨大製品を目指すより、小さい中核を持ち、必要な機能を拡張で足す方針を取っています。

Pi には公式に次の4モードがあります。

* **interactive**: 対話しながら使うモード
* **print / JSON**: スクリプトや機械処理向けのモード
* **RPC**: 他のシステムからプロトコル経由で呼ぶモード
* **SDK**: 自分のアプリケーションへ埋め込むモード

GitHub の monorepo を見ると、責務も分かれています。

* `pi-agent-core`: agent runtime、tool calling、state management
* `pi-ai`: 複数 LLM provider の抽象化
* `pi-coding-agent`: coding agent 本体
* `pi-web-ui`: AI chat interface 用の Web UI 部品

この構成を見ると、Pi は単なる1個のアプリではありません。agent を組み立てるための部品群として設計されています。

Pi の全体像は、公式リポジトリを見るとつかみやすいです。

## この記事で言う AI-native とは何か

私はこの記事で、AI-native を次の意味で使います。

**AI-native とは、AI を後から足すのではなく、最初から AI が操作主体の一つになる前提でシステムを設計することです。**

たとえば、既存の業務システムにチャット欄を追加するだけでは足りません。AI-native にしたいなら、最初から次を決める必要があります。

* AI が何を見られるか
* AI が何を実行できるか
* AI の判断とコードの判断をどう分けるか
* 危険な副作用をどこで止めるか
* 実行履歴をどう監査するか

この記事で扱うのはこの部分です。

## 従来の Web アプリ設計では何が中心だったか

通常の Web アプリは、人間が使うことを中心に設計します。流れは大まかにこうなります。

先に要点だけ読みたい方へ

従来の Web アプリは、画面と API を中心に設計します。  
この記事の構想では、中心を capability に置き換えます。

もう少し一般化すると、次の形です。

```
Route → Controller → Service → DB
```

この設計では、画面や HTTP endpoint が中心です。たとえば請求書作成機能なら、多くのチームは次の順で考えます。

1. 請求書作成ページを作る
2. ページから叩く API を作る
3. API の裏に business logic を置く
4. DB に保存する

人間がフォームを埋めて送信するなら、この流れで問題ありません。

## AI が主体になると、見たい単位が変わる

AI agent は人間のように「まず請求管理画面を開こう」とは考えません。ユーザーがこう頼んだとします。

> 未払い請求を確認して、必要ならリマインドメールの下書きを作ってください。

この依頼を処理するとき、AI が欲しいのは画面 URL ではありません。AI は次のような業務操作を必要とします。

* 未払い請求を検索する
* 顧客情報を取得する
* リマインドメールを下書きする
* 送信前に承認を求める
* 承認後に送信する
* 結果を監査ログへ記録する

ここで AI が扱う単位は、画面でも REST endpoint でもありません。意味のある業務操作です。

この違いを踏まえると、システムの中心は次の形に置き換わります。

```
Intent → Agent Harness → Capability → Deterministic Runtime → State
```

順に説明します。

* **Intent**: ユーザーが本当にやりたいことです
* **Agent Harness**: LLM が計画し、道具を選び、作業を進める土台です
* **Capability**: システムが提供する安全な業務操作単位です
* **Deterministic Runtime**: DB 更新や認可を確実に実行するコードです
* **State**: DB、ジョブ状態、監査ログのような永続状態です

要点は明確です。AI は DB を直接触りません。AI は capability を通して操作します。

## capability とは何か

capability は単なる関数ではありません。私は capability を、次をまとめた安全な業務操作の定義として扱います。

* 何をする操作か
* どんな入力を受け取るか
* どんな出力を返すか
* どんな権限が必要か
* どんな副作用を持つか
* 承認や監査が必要か

イメージはこうです。

```
capability("invoice.create", {
  input: InvoiceCreateInput,
  policy: requireRole("accounting"),
  effect: "write",
  handler: async (ctx, input) => { ... }
})
```

この定義があると、AI は「この操作を呼んでよいか」を判断しやすくなります。人間も「この操作は何をして、どこが危険か」を追いやすくなります。

つまり capability は、AI に見せるインターフェースであり、人間が安全性を設計する境界でもあります。

## Pi から借りるべき3つの思想

この章では、Pi の公開情報から確認できる性質のうち、Web フレームワークへ移しやすいものを3つに絞って整理します。

### 1. コアを小さく保つ

Pi の公式サイトと CONTRIBUTING.md から、Pi がコアを小さく保つ姿勢を取っていることが分かります。

この方針は Web 側でも重要です。AI 系フレームワークは、planning、memory、workflow、approval、RAG、UI を全部 core に入れがちです。ですが、そのやり方だと差し替えが難しくなります。

そのため、この構想でも core は小さく保つべきです。

### 2. feature ではなく primitive を作る

Pi は `Primitives, not features` を掲げています。私はこの考え方を Web にも持ち込みたいです。

巨大な billing module を一つ作るより、意味がはっきりした小さい capability を並べる方が扱いやすくなります。たとえば次のような形です。

* `invoice.searchOverdue`
* `customer.getContact`
* `email.composeReminder`
* `email.send`

この粒度なら、AI は計画を立てやすく、人間は権限や承認条件を付けやすくなります。

### 3. Pi を harness として埋め込む

Pi は interactive 専用ツールではありません。RPC と SDK があり、他のアプリに組み込む前提があります。

この点が大きいです。私は Pi を完成済みのチャット製品としてではなく、agent control plane を組み立てる部品として見るべきだと思います。そう考えると、Web フレームワーク側で deterministic runtime を持ちつつ、Pi 側に planning や tool orchestration を担わせる構成が見えてきます。

## LLM は何を担当し、コードは何を担当するか

役割分担を曖昧にすると事故が起きます。私は、LLM に判断を任せ、コードに実行を任せる切り分けが必要だと考えています。

AI-native な設計で失敗しやすい点は、LLM に何でも任せることです。業務システムでは、LLM とコードの得意分野を分けた方が安全です。

### LLM が得意なこと

* ユーザーの意図を読む
* 曖昧な依頼を具体化する
* 必要な capability を選ぶ
* 実行順序を組み立てる
* エラー時の回復方針を考える
* 人間への確認文を書く

### 決定論コードが得意なこと

* validation
* 認可
* DB 更新
* transaction
* idempotency
* external API call
* audit log

ここで言う決定論コードとは、同じ入力に対して同じルールで動くコードです。業務システムでは、この部分が再現可能で説明可能であることが重要です。

私は役割分担をこう置くのがよいと考えます。

**LLM は判断し、コードは実行します。**

## deterministic runtime とは何か

deterministic runtime という言葉も補足します。難しい概念ではありません。本当に副作用を起こす部分は、堅いアプリケーションコードで持つという意味です。

対象はたとえば次です。

* DB への insert / update / delete
* 認証と認可
* 決済 API 呼び出し
* メール送信
* キュー投入
* 監査ログ保存

こうした処理をモデルの自由な振る舞いに任せるわけにはいきません。AI は「何をしたいか」を決めます。実行は deterministic runtime が担当します。

## Pi は本番 runtime ではなく harness として置く

この構想では、Pi を本番リクエストの唯一の中核には置きません。私は次の役割分担が妥当だと考えます。

```
Pi = agent harness / control plane / developer-facing runtime
Web Framework = deterministic app runtime
```

Pi 側が担うのは次です。

* planning
* tool calling
* session tree 管理
* skills の適用
* provider abstraction

Web アプリ側が担うのは次です。

* 認可
* transaction 管理
* 副作用実行
* durability
* audit と approval

この分離があると、AI 側は柔軟に変えやすくなり、業務システム側は堅く保てます。

## 提案アーキテクチャ

図にすると、全体はこうなります。

*上から下へ、意図の解釈、capability の選択、決定論コードでの実行、監査の記録、という順で流れます。*

この図で重要なのは、UI と AI の両方が capability registry を共有する点です。従来の設計では、画面と API が主役でした。ここでは capability が主役です。画面も API もチャット UI も、その capability を使う入口になります。

## capability registry を中心に置くと何が変わるか

capability-first の利点は、capability 定義を source of truth にしやすいことです。1つの capability 定義から、次のものを派生できます。

* agent tool schema
* API endpoint
* admin form
* ドキュメント
* テスト fixture
* audit schema

このとき UI は本体ではありません。capability の投影です。

従来はフォームを作り、その裏に API を作りました。ここでは逆です。capability を作り、その投影として UI や API を作ります。

## 最小 API 案

具体例はこうです。

```
import { app, capability, policy } from "@piweb/core"

const createInvoice = capability("invoice.create", {
  description: "Create a draft invoice for a customer",
  input: InvoiceCreateSchema,
  output: InvoiceSchema,
  effect: "write",
  policies: [
    policy.authenticated(),
    policy.role("accounting"),
    policy.requiresApprovalWhen(input => input.amount > 100000),
  ],
  handler: async ({ db, actor }, input) => {
    return db.transaction(async tx => {
      return tx.invoice.create({ data: input })
    })
  },
})

export default app({
  capabilities: [createInvoice],
})
```

この API で大事なのは、`handler` の前に実行条件が見えることです。

* 入力と出力
* 副作用の種類
* 必要な認可
* どの条件で承認が要るか

AI に backend を触らせるなら、実装本体より先に危険境界を書ける設計が必要です。

## 設計原則 1: primitive は小さくする

primitive は、AI と人間が組み合わせて使う最小単位です。大きすぎる関数は扱いにくくなります。

たとえば、これは粗すぎます。

この1つに検索、更新、送信、支払い確認、承認判定が全部入っていたら、中で何が起きるか見えません。

一方で、次のように分けると意味がはっきりします。

```
customer.find()
invoice.createDraft()
invoice.validate()
invoice.send()
payment.status()
```

もちろん細かくしすぎても困ります。ですが、少なくとも意味が見えない巨大関数より、意味がはっきりした小さい操作の方が AI と相性がよいです。

## 設計原則 2: すべての副作用に policy を付ける

AI にシステムを触らせるとき、role-based auth だけでは足りません。副作用の種類ごとにルールが必要です。

```
read     → 自動実行可
write    → policy 次第
money    → 必ず approval
delete   → reversible または approval
external → rate limit + audit
```

理由は単純です。同じ権限を持つユーザーでも、読み取りは自動でよく、顧客送信は承認が欲しく、高額請求は必ず止めたい、という運用差があるからです。

私は AI-native backend では、この運用ルールを code と同じくらい明示的に置くべきだと考えています。

## 設計原則 3: agent 実行は必ず trace 可能にする

AI が関わると、何が起きたかを追いにくくなります。そのため、最低でも次は残したいです。

```
intent
plan
tool calls
inputs
outputs
approval
final result
```

trace は単なるデバッグログではありません。誰が、何をしようとし、なぜその capability を選び、どこで人間が承認し、最終的に何を実行したかを説明するための記録です。

業務システムでは、動くだけでは足りません。説明できる必要があります。

## 設計原則 4: Human-in-the-loop を最初から入れる

AI の話では自動化率に注目が集まりがちです。ですが、実運用では止める場所の方が重要です。

たとえば次のように書きます。

```
policy.requiresApproval({
  reason: "This operation sends email to a customer",
})
```

これは「何かまずければ人が見る」という発想ではありません。最初から、この種類の操作は人が最終確認すると決めておく設計です。

メール送信、課金、削除、外部公開は、この対象になりやすいです。

## 設計原則 5: UI も capability から生成する

従来は UI が先で API が後ろにありました。capability-first では逆です。capability を中心に置き、そこから UI と API を派生させます。

この形にすると、次の一貫性を保ちやすくなります。

* チャットから呼ぶ能力
* 管理画面から呼ぶ能力
* API から呼ぶ能力
* 監査対象になる能力

入口が違っても、同じ capability を見ていれば安全境界をそろえやすくなります。

## Pi とどう接続するか

Pi の4モードのうち、この構想と相性がよいのは RPC と SDK です。

### 開発時

`pi-coding-agent` は、次の作業を支援できます。

* capability 雛形の生成
* migration 作成
* テスト作成
* 運用スクリプト作成

### 運用時

`pi-agent-core` は capability registry を tool 群として見て、どの capability をどの順で呼ぶかを計画できます。

### 管理時

`pi-web-ui` のような UI 部品を使うと、次の画面を作れます。

* chat interface
* approval console
* trace viewer
* replay UI

ここで大事なのは、Pi をチャット画面と見なさないことです。Pi は、agent control plane を組み立てる部品群として使う方が自然です。

## パッケージ構成のイメージ

framework として切り出すなら、私は次の構成を考えます。

```
packages/
  core/
    capability registry
    policy engine
    execution context
    audit log

  agent/
    Pi adapter
    planner
    tool router
    session manager

  web/
    HTTP routes
    React components
    server actions
    chat UI

  runtime/
    job queue
    transaction boundary
    durable execution adapter

  devtools/
    trace viewer
    capability explorer
    replay UI
    approval console
```

ここでも `core/` を膨らませすぎないことが重要です。Pi の思想を借りるなら、中心は小さく保ち、周辺を拡張可能にしておく方がよいです。

## まず作るべき MVP

MVP で最初に絞る範囲

最初から全部作る必要はありません。私は次の7点で十分だと思います。

```
1. capability() DSL
2. Pi tool adapter
3. policy engine
4. audit log
5. approval gate
6. simple chat UI
7. dev CLI
```

ユースケースも1つで足ります。

> 未払い請求を確認して、必要ならリマインドメールの下書きを作ってください。

この依頼を次の流れで処理できれば、MVP として筋が通っています。

```
user intent
→ agent plans
→ invoice.searchOverdue
→ customer.getContact
→ email.composeReminder
→ approval required
→ email.send
→ audit saved
```

この1本が安全に動けば、次の論点が見えます。

* capability の粒度は適切か
* approval UX は実用的か
* trace は監査に耐えるか
* retry と idempotency は足りるか
* 危険 capability を agent が誤選択しないか

## これは Next.js や Rails の代替ではない

ここは誤解しやすいので、はっきり書きます。この構想は Next.js や Rails を置き換えるものではありません。

```
Next.js / Hono / Fastify / Rails
        +
Pi-based Capability Framework
```

立ち位置としては、フロントエンドフレームワークでも ORM でもなく、その上に載る AI-native application layer です。私は、Web アプリを作る基盤を総入れ替えするのではなく、AI が安全に業務操作できる標準層を足す形が現実的だと考えています。

## この構想の難所

筋はよいと思いますが、難しい点もあります。ここを曖昧にしたまま進めると、MVP は動いても運用で崩れます。

### 1. capability の粒度設計

細かすぎると plan が長くなります。粗すぎると危険になります。どこで切るかはドメイン次第です。

### 2. policy は auth より広い

role check だけでは足りません。金額、宛先、顧客状態、時間帯、可逆性、レート制限が効いてきます。

### 3. trace は保存するだけでは弱い

記録を残すだけでは不十分です。人間が replay、diff、approval rationale を読める UI まで必要です。

### 4. AI の失敗は UI の失敗より重い

画面の表示ミスは直せます。誤送信、誤課金、誤削除は簡単に戻せません。だから重要なのは、AI を便利にすること以上に、危険境界を明示することです。

## まとめ

Pi の面白さは、完成済みの agent 製品であることより、最小 harness を中心に置き、必要な機能を primitive と extension で増やしていける設計思想にあります。

この思想を Web アプリケーションへ移すと、中心概念は route や controller ではなく capability になります。

* LLM は意図理解と計画を担う
* capability は安全な業務操作単位になる
* deterministic runtime が副作用を実行する
* policy、approval、audit、trace が全体を支える

私が狙うべきだと思うものは明確です。

**LLM が安全に操作できる Web backend の標準形です。**

この構想を本当に作るなら、それは「AI 付き Web フレームワーク」ではありません。Web アプリケーションを、agent が操作可能なシステムとして再定義する application layer になります。

## 実装メモ

実際に作り始めるなら、順番はこのくらいが現実的です。

実装開始時の最小チェックリスト

* capability ごとに副作用分類を書く
* approval が必要な条件を書く
* audit log に残す項目を先に決める
* 1つの実ユースケースで最後まで通す

1. `capability()` DSL を作る
2. schema から tool schema を自動生成する
3. `read / write / money / delete / external` の policy 分類を作る
4. approval gate を capability 実行前に差し込む
5. audit log に `intent / plan / tool calls / output / approval` を残す
6. chat UI から capability 実行までを 1 ユースケースで通す

最初から汎用 platform を全部作ろうとする必要はありません。まずは、危険な副作用を伴う現実の1業務を、traceable に、安全に、自動化できるかを確かめるべきです。

## 参考リンク

本文中で触れたものをまとめます。
