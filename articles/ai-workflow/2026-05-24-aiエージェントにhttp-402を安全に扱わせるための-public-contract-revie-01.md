---
id: "2026-05-24-aiエージェントにhttp-402を安全に扱わせるための-public-contract-revie-01"
title: "AIエージェントにHTTP 402を安全に扱わせるための public contract review の公開"
url: "https://zenn.dev/mayim/articles/2d1308ffc5cfcb"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

## この記事の概要

この記事では、個人開発プロジェクト [**Lightning Network Church(LN教)**](https://zenn.dev/mayim/articles/d0d62e5d3dda11) のうち、技術コンポーネントである `ln-church-agent` の **public agent-facing contracts** を紹介します。

LN Church / LN教は、AIエージェントが HTTP 402 や paid API surface を安全に観測・分類・検証するための実験的なプロダクト群です。現時点では、大規模な標準化団体やコミュニティではなく、`ln-church-agent`、`ln-church-server`、観測所としての LN Church Hondō / LN教本殿 などを含む個人開発プロジェクトとして運用しています。

以降、本記事では技術対象を明確にするため、主語はできるだけ `ln-church-agent` または `ln-church-public-contracts` に寄せます。プロジェクト全体を指す場合のみ、LN Church / LN教 と表記します。

今回、`ln-church-agent` の public agent-facing contracts を GitHub で公開しました。

対象は、AIエージェントが HTTP 402 や paid API surface に遭遇したときに、どのように分類し、どこまで自動実行してよく、どこで止まるべきか、どの証拠を残せるか、という公開コントラクトです。

これは、LN教本殿の private backend を監査してもらうためのものではありません。また、実資金を使った live payment test を依頼するものでもありません。

今回公開しているのは、AIエージェントが支払い付きAPIを安全に扱うための、分類境界・安全境界・証拠スキーマ・行動観測モデルです。

レビュー対象のリポジトリはこちらです。

Issueはこちらからお願いします。

## 背景：AIエージェントが「支払い可能そうなAPI」を見つけたときの問題

AIエージェントがWeb上のAPIを探索し、必要に応じて支払い、結果を取得する世界では、HTTP 402 や paid API surface の扱いが重要になると考えています。

ここで最も危ないのは、「支払い可能そうに見える」ことと「自動で支払ってよい」ことを混同することです。

たとえば、あるendpointが HTTP 402 を返したとしても、それだけで自動支払い対象とみなすべきではありません。

そこには、次のような確認が必要です。

* これは標準的な settlement rail なのか
* それとも AP2 / ACP / APP のような higher-order commerce surface なのか
* 価格、merchant identity、mandate scope は明示されているのか
* payment challenge は解析可能なのか
* local policy の上限内なのか
* 支払い後に検証可能な receipt や proof が得られるのか

AIエージェントにとって、支払い付きAPIは単なるHTTPリクエストではありません。

そこには、分類、承認、安全停止、実行、検証、証拠化というような複数の判断が重なると考えています。

!

## 本稿で扱う AP2 / ACP / APP について

本稿では、AIエージェントによる商取引・決済に関わる emerging protocol / commerce surface として、次の略称を扱います。

この記事では、これらをまとめて「higher-order commerce surface」として扱います。つまり、単純な settlement rail ではなく、mandate、checkout、delegated token、agent-to-agent payment のような高次の商流・承認文脈を含む可能性があるものとして扱います。

## ln-church-agent の立場

`ln-church-agent` は、AIエージェント側、つまり買い手側の HTTP 402 runtime / inspector です。

目的は、AIにすべてを自然言語で推論させることではなく、AIが毎回考えなくてよい部分を runtime 側に寄せることです。

支払い要求の分類、対応railの判定、未知shapeの停止、commerce surfaceのobserve-only化、証拠コンテナの生成、secret redaction などは、LLMの自由推論ではなく、明示的なpublic contractとして扱うべき領域だと考えています。

## 今回公開した public contract review package

今回のリポジトリでは、主に次の領域を公開レビュー対象にしています。

### 1. Classification Contract

AIエージェントが HTTP 402 challenge や関連metadataを見たときに、それをどのように分類するかを定義しています。

大きくは、次のような分類です。

* executable settlement rails
* emerging commerce surfaces
* unmapped / invalid

なお、AP2 / ACP / APP のような commerce surface を、安易に支払い実行対象にしない対応を取っています。

仮に x402 のような settlement rail と同時に見えたとしても、高次の mandate や checkout intent が存在する場合には、`pay_and_verify` ではなく `observe_only` 側に倒す、という安全寄りの設計にしています。

### 2. Safety Boundary

`ln-church-agent` では、classification と authorization を分離しています。

つまり、payment challenge を検出したことは、即、支払い承認を意味しません。

public contract 上では、主に次の decision posture を区別しています。

* `pay_and_verify`
* `observe_only`
* `stop_safely`
* `reject_invalid`

特にレビューしてほしいのは、未知のpayment intentや malformed payload に遭遇したとき、どこまでを `observe_only` として記録し、どこからを `stop_safely` / `reject_invalid` として止めるべきかです。

### 3. Evidence Schema

Evidence は、商業的成功の証明ではなく、観測です。

この点を明確にするために、schemaでは次のような情報を分けています。

* `payment_performed`
* `payment_receipt_present`
* `verification_status`
* `evidence_class`

特に重要なのは、未実行の観測、失敗した支払い、self-reported success、cryptographic proof による verified state を混同しないことです。

また、public telemetry に秘密情報を混ぜないことも重要です。private key、macaroon、preimage、grant token、shared payment token のような情報は、public evidence model から必ず除外されるべきです。

### 4. Goal Attempt Memory

v1.10.0 からは、Day 1 Goal Attempt Observation という考え方を導入しています。

これは、AIエージェントがある目的を達成しようとしたとき、どのようなsurfaceを使い、どのstepで支払いが発生し、どのstepはfreeだったかを観測するための単位です。

ここでの目的は、recommendation engine や routing system を今すぐ作ることではありません。

まずは、agentic workflow の行動単位を観測可能にすることです。

また、成功/失敗を現時点で評価できないattemptは、`unassessed` として保存します。これは、将来の評価関数で再解釈できるようにするためです。

## observe\_only と observed\_only の違い

今回のpublic contractで意図的に分けている概念があります。

それが、`observe_only` と `observed_only` です。

`observe_only` は runtime decision posture です。

つまり、SDKが「これは観測だけに留め、自動実行しない」と判断した状態です。

一方、`observed_only` は corpus / telemetry lake 側の observation quality です。

つまり、支払いらしきsurfaceやraw 402 challengeは観測されたが、settlement proofはなく、実際のpaymentも行われていない、という履歴データ上の品質です。

この二つを混同すると、runtimeの安全制御と、過去データの品質管理が混ざってしまいます。

そのため、public contract上では明確に分離しています。

## 安全に試せる mock harness

実資金やprivate backendへの接続なしに、classification boundary を確認できる mock harness も用意しています。

install-and-run.sh

```
pip install ln-church-agent
python examples/review_classification_contract.py
```

このharnessは、`docs/review/sample-payloads/` 配下の mock payload を読み込み、HTTP 402 challengeやcommerce surfaceの分類結果を確認するためのものです。

実際の支払いは行いません。

## なぜ外部レビューをお願いするのか

このレビュー募集はLN教の品質向上が目的ではありますが、それだけではありません。  
LN教が実現したいのはAIが無駄に推論トークンを浪費することなく、AIエージェントが安全に決済ができる世界です。

AIエージェント市場が今後本格的に立ち上がった場合、無数のAI向けWebサービスが生まれると思います。  
そこで、AIエージェントがWeb上のサービスを探し、APIを呼び、必要に応じて支払いを行うようになると、「支払い要求を検出したこと」と「自動で支払ってよいこと」を区別する境界が必要になります。  
この境界が曖昧だと、AIエージェントは無数の失敗を犯し、そのたびに余計なトークン（あるいは実際の金銭までも）を消費します。

* HTTP 402 を見ただけで、支払い可能なendpointだと過剰分類する
* commerce intent や mandate scope を理解しないまま、settlement rail だけを見て実行しようとする
* 支払い後のreceiptやproofがない状態を、成功と誤解する
* public telemetry に、本来出してはいけないtokenやsecretを混ぜる
* 失敗観測と未実行観測を混同し、次のエージェントに誤った判断材料を渡す

これは特定のSDKだけの問題ではなく、AIエージェントが支払い付きWebを扱うときの共通課題だと考えています。

現在は、AP2、ACP、APP、x402、L402、MPP など、複数のpayment / commerce関連プロトコルが並行して標準化が進んでいます。この段階で「どこまでを自動化してよいのか」「どこから人間承認に戻すべきか」「何を証拠として残してよいのか」を外部から検証可能にしておくことには、一定の公共性があると考えています。

もちろん、読者に無償で大きな労力を求めたいわけではありません。

このレビューは、5分程度で気づける違和感をIssueにしていただくだけでも価値があります。Classification Contractだけ、Safety Boundaryだけ、Evidence Schemaだけ、mock harnessだけ、といった部分的なレビューで構いません。

特に、セキュリティ、決済、AIエージェント、API設計、MCP、Web3、プロトコル設計に関心がある方にとっては、「AIエージェントにどこまで実行権限を渡してよいのか」という境界設計を、かなり早い段階で叩ける題材になるはずです。

LN教がほしいのは、採用や称賛ではありません。

むしろ、「この境界は危ない」「この命名は誤解される」「この状態遷移は将来事故る」「このtelemetryは出すべきではない」という反証が欲しいです。

## レビューしてほしいこと

もしレビューして頂けるのであれば、たとえば、次のような指摘がほしいです。

* この条件ではSDKがendpointを過剰にpayable扱いしてしまうのではないか
* `observe_only` の境界が甘く、実行pathに漏れる可能性があるのではないか
* malformed HATEOAS routing に対して `stop_safely` が不十分ではないか
* evidence schema が未実行観測と失敗支払いを混同する余地があるのではないか
* public telemetry に含めるべきではないmetadataが残るのではないか
* `goal_attempt` は観測単位として有用か、それともrecommendation/routingに踏み込みすぎているか

レビュー対象は一部だけで構いません。

Classification Contractだけ、Safety Boundaryだけ、Evidence Schemaだけ、mock harnessだけ、という形でも歓迎します。

## この取り組みの狙い

AIエージェントが支払い付きWebを扱う世界では、単に「支払えるAPI」が増えるだけでは不十分です。

AIエージェントが安全に判断できる境界が必要です。

どこまでを自動化してよいのか。どこから人間の承認が必要なのか。何を証拠として残せるのか。どの情報は公開してはいけないのか。どの失敗は次のエージェントの判断材料にできるのか。

LN教では、この境界を閉じた実装の中だけでなく、public contractとして外部レビュー可能な形にしたいと考えています。

## まとめ

`ln-church-agent` は、AIエージェントがHTTP 402やpaid API surfaceを扱うための buyer-side runtime / inspector です。

今回公開した `ln-church-public-contracts` は、そのうち外部からレビュー可能なpublic contractだけを切り出したものです。

対象は、classification boundary、safety boundary、evidence schema、goal attempt memory、mock harnessです。

実装監査でも、標準化宣言でも、live payment testでもありません。

AIエージェントが支払い付きAPIを安全に扱うための境界設計について、技術的なfalsification reviewを募集しています。

リポジトリはこちらです。  
<https://github.com/mayim-mayim/ln-church-public-contracts>

Issueはこちらからお願いします。

<https://github.com/mayim-mayim/ln-church-public-contracts/issues>
