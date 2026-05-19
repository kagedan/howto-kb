---
id: "2026-05-18-activejobcontinuable-で-durable-agent-を作る-01"
title: "ActiveJob::Continuable で Durable Agent を作る"
url: "https://zenn.dev/takeyuwebinc/articles/47cedf5634186d"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

RubyLLMでは「エージェント」や「ツール」を提供しますが、それらをどのように繋げるかとワークフローの実装についてフレームワークを提供せず、アプリ実装者に委ねられています。

<https://x.com/takeyuweb/status/2050868032906621319>

[https://zenn.dev/takeyuwebinc/articles/ea2be00723b53d#構成要素4-—-マルチエージェントワークフロー](https://zenn.dev/takeyuwebinc/articles/ea2be00723b53d#%E6%A7%8B%E6%88%90%E8%A6%81%E7%B4%A04-%E2%80%94-%E3%83%9E%E3%83%AB%E3%83%81%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E3%83%95%E3%83%AD%E3%83%BC)

このようなAIエージェントによるワークフローをはじめとした長時間・多段階の実行では、ネットワークアクセス失敗やタイムアウト、プロセス終了による中断など、正常に完了できないリスクが高まります。素直な実装では都度はじめからやりなおしになりますが、LLM呼び出しはコストがかかりますし、例えばメールの送信など2度実行してはならない処理もあります。

このような場合に備えて、 **Rails 8.1** では、 `ActiveJob::Continuable` によって、実行中のエラーや、プロセスの中断などがあったとき、完了済みステップをスキップする仕組みを提供しています。

[https://railsguides.jp/active\_job\_basics.html#ジョブの継続](https://railsguides.jp/active_job_basics.html#%E3%82%B8%E3%83%A7%E3%83%96%E3%81%AE%E7%B6%99%E7%B6%9A)

ただしこのフレームワークを利用するだけでは、**中断や障害から復帰できるエージェント（Durable Agent）** は完成しません。  
`ActiveJob::Continuable` というフレームワークが提供するのは **「ステップ分割と進捗チェックポイント」という一部品で、中断したジョブを再実行するトリガー、ステップ間で状態を渡す中間状態の永続化、再実行で副作用を二重に起こさない冪等設計、再実行を判断するエラー設計は、アプリ側で別途用意する必要があります。**

この記事では、その範囲を前提に「フレームワークが提供する部分」と「自分で実装する部分」を切り分け、後者の実装ポイントをコードで示します。

## TL;DR

* **中断したジョブを再実行するトリガー**: 永続化バックエンドのジョブ基盤（Solid Queue 等）を用意する。
* **ステップ間で状態を渡す中間状態の永続化**: ステップ間の状態を DB に置く
* **再実行で副作用を二重に起こさない冪等設計**:
  + `ActiveJob::Continuable` は完了済みステップが再実行されないことを保証しない
  + 各ステップを完了チェックや `find_or_create` で再実行安全にする
  + 外部副作用（API 呼び出しなど）は冪等キーで二重実行を防ぐ
* **再実行を判断するエラー設計**:
  + `ActiveJob::Continuable` はエラークラスを問わず完了まで繰り返し再実行するものでは**ない**
  + 再実行したいエラーは通常のジョブと同様 `retry_on` で指定する
  + 一時的なエラーと恒久的なエラーを切り分けた設計が必要

たとえば、LLM でドキュメントを要約するパイプライン（抽出 → 要約 → 整形 → 配信）を題材にします。Durable Agent として成立させるには次のようにします。

app/jobs/summarize\_pipeline\_job.rb

```
class SummarizePipelineJob < ApplicationJob
  # 自動再開の設定ここから
  include ActiveJob::Continuable

  # 経路に依らずジョブがもう実行されない状態になる前に呼ばれる
  # エラートラッキングするなど
  #after_discard do |job, exception|
  #  ExceptionNotifier.report(exception)
  #end

  # 一時的なエラーは再試行する
  # 自動再開によりエラーが発生した step までに完了済みの step はスキップされる。
  # 再試行回数を超過したジョブは失敗ジョブとしてバックエンドに残る。
  # retry_on 指定のないエラー発生時も失敗ジョブとしてバックエンドに残る。
  # ただし retry_on を指定しなくても、その実行中に進捗（完了したstepがある or カーソルが進んだ）がある場合は1度再開（resume）される。
  # これは、進捗ロスを防ぎ、進捗状況をジョブに記録するために再エンキューが必要なための措置で、ここで定義する再試行とは別。
  # 再開後、進捗がないまま再びエラーが発生した場合は、retry_onがなければそのまま失敗ジョブとなる（進捗状況は再開時に記録されているので、進捗状況付きの失敗ジョブとなる）
  retry_on Net::OpenTimeout, Timeout::Error

  def perform(document_id)
    # step の外側は毎回実行される
    @document = Document.find(document_id)
    @llm = LlmClient.new

    # 実際の処理はそれぞれのstepの中で行う
    # それぞれのstepは
    # - 状態をインスタンス変数でやり取りしない
    # - 繰り返し実行しても安全
    step :extract
    # 最初のstepが完了して以降は「自動再開」対象となる
    step :summarize
    step :format
    step :deliver
  end

  private

  def extract
    return if @document.sections.exists?  # 完了チェックで再実行を吸収する
    @document.create_sections!(@llm.extract(@document.body))
  end

  def summarize
    return if @document.summary.present?
    @document.update!(summary: @llm.summarize(@document.sections))
  end

  def format
    return if @document.formatted_report.present?
    @document.update!(formatted_report: @llm.format(@document.summary))
  end

  def deliver
    # deliver は外部 API を呼ぶ。再実行で二重に呼ばれないよう、
    # ポイント5 で冪等キーと結果確認により冪等化する。
    DeliverReport.new(@document).call
  end
end
```

以下で、「フレームワークが埋める部分」と「自分で書く部分」を切り分けながら、背景と実装の詳細を解説します。

## 背景: なぜ Durable Agent が必要か

参考に示したパイプラインは、デプロイ・worker 再起動・例外で中断すると、素朴な実装では最初からやり直しになります。抽出 → 要約 → 整形 → 配信の 4 ステップのうち要約まで終わっていても、整形でプロセスが落ちれば、再実行は抽出からです。

この痛みを解消するのが Durable Agent です。

### Durable Agent とは何か

Durable Agent は、クラッシュ・中断・再起動を生き延び、進捗を失わず最新のチェックポイントから再開できる AI エージェントを指し、次の 4 要件が揃った状態として説明されています（[Inngest: Building Durable AI Agents](https://www.inngest.com/blog/building-durable-agents)、[Diagrid: Checkpoints Are Not Durable Execution](https://www.diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows)）。

| 要件 | 内容 |
| --- | --- |
| 状態チェックポイント | 各ステップ完了時に出力と進捗を永続化する |
| 再開可能性 | 中断後、最初の未完了ステップから再開し、完了済みステップを再実行しない |
| リトライ | ステップ内の失敗に対して再試行する。再試行時も再開可能性を維持する |
| 冪等性 | 各ステップ・各副作用が複数回実行されても結果を破壊しない |

ここで重要なのは、「Durable Agent」が達成すべき**性質**を指す語であって、特定のランタイムや機構を指す語ではないという点です。4 要件を満たしさえすれば、それがどう実装されていても Durable Agent と呼べるそうです。

### `ActiveJob::Continuable` に足りないもの

`ActiveJob::Continuable` は、4 要件のうち「状態チェックポイント（の進捗管理部分）」と「再開可能性（の再開ロジック部分）」にあたります。`perform` 内で `step` メソッドによりステップを定義すると、Continuable はステップの完了を進捗として追跡し、中断したジョブの再開時には、完了済みステップをスキップして最初の未完了ステップから実行します（[Rails 8.1 リリースノート](https://rubyonrails.org/2025/10/22/rails-8-1)、[ActiveJob::Continuation API ドキュメント](https://api.rubyonrails.org/v8.1/classes/ActiveJob/Continuation.html)）。

補足: 復元方法による checkpoint型と 決定論的リプレイ型 の違い

`ActiveJob::Continuable` の復元方式は **checkpoint 型** と呼ばれます。これはLangGraphなどのフレームワークでも採用されている方式で、フレームワークが状態のスナップショット（save point）を保存し、その先の障害検知やリカバリの起動は開発者に委ねる、という分類です（[Diagrid: Checkpoints Are Not Durable Execution](https://www.diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows)）。`ActiveJob::Continuable` の場合は、ステップの完了を進捗として記録し、再開時は完了済みステップをスキップして未完了ステップを再実行します。

Temporal などが採用する **決定論的リプレイ型** は、ここまで述べた checkpoint 型と、復元の仕組み、とりわけ実行状態を記録する粒度が異なります。リプレイ型は外部呼び出し 1 回ごとに、その呼び出しと結果を実行履歴に記録します。再開時はコードを最初から再実行しますが、記録済みの呼び出しは実行せず、記録された結果を差し替えます（[Temporal: Durable Execution Meets AI](https://temporal.io/blog/durable-execution-meets-ai-why-temporal-is-the-perfect-foundation-for-ai)）。記録の粒度が呼び出し単位なので、1 つの処理のなかで外部呼び出しを 2 回行い、1 回目の直後にクラッシュした場合でも、再開時は 1 回目の結果が記録から差し替えられ、2 回目だけが実行されます。

checkpoint 型が記録するのは「どのステップまで完了したか」だけで、ステップの内部までは記録しません。あるステップが外部呼び出しを 2 回行い、1 回目の直後（そのステップ完了の永続化前）にクラッシュすると、そのステップは「未完了」のままなので、再開時にステップごと丸ごと再実行されます。済んでいた 1 回目の呼び出しもやり直しになります。両者とも「完了したものは再実行しない」点は同じですが、その"完了"の単位が、リプレイ型は呼び出し 1 回、checkpoint 型はステップ 1 つ、という違いです。リプレイ型は基盤が呼び出し単位の exactly-once を保証しますが、checkpoint 型では、再実行されても壊れないことの担保はアプリ側に残ります。

`ActiveJob::Continuable` が checkpoint 型であることは、次の設計上の限界を伴います。いずれも後続の実装ポイントの動機であり、構成を揃えても完全には消えません（詳細は「この構成で埋まらないこと」で扱います）。

* 進捗の永続化前にクラッシュしたステップは、最初から再実行される。ステップ内のコードは複数回実行されても安全に書く必要がある
* exactly-once を基盤が保証しない。副作用の重複防止は冪等キーなどでアプリ側が実装する
* 能動的な障害検知（watchdog）を持たない。中断したジョブの再開はジョブ基盤による再配信に依存する
* 進行中ジョブがある状態でのステップ構成変更に弱い。再開時に進捗とステップ構成が食い違うと失敗しうる

しかしながら、Durable Agentの文脈において、開発者が最も保護したいのは「エージェントの記憶（Context）と現在」であり、これはCheckpoint型で十分に実現可能であるので、決定論的リプレイ型は必須ではないと考えます。

ただし、`ActiveJob::Continuable` だけでは不足する部分があります。これがこの記事の本題です。

* **不足①: 再開のトリガーを持たない**：中断時にジョブの再エンキューを試みますが、クラッシュしたジョブを実際に再実行する主体は持たず、これはジョブ基盤の責務です
* **不足②: ステップ間で状態を渡さない**：再開時にジョブを `perform` から再構築するためプロセスメモリは引き継がれず、中間状態の永続化はアプリ設計の責務です（[active\_job/continuation.rb（rails v8.1.2）](https://github.com/rails/rails/blob/v8.1.2/activejob/lib/active_job/continuation.rb)）
* **不足③: 冪等性を担保しない**：ステップの再実行は行いますが、再実行で副作用が二重に起きないことは保証せず、これはアプリ設計の責務です
* **不足④: 失敗を再試行する方針を持たない**:`ActiveJob::Continuable` はエラークラスを問わず完了まで繰り返し再実行するものでは**ない**ので、どのエラーを再試行するべきかは、アプリ設計の責務です

つまり `ActiveJob::Continuable` は、Durable Agent を構成する一部に過ぎず、残りをジョブ基盤の選定とアプリ設計で補う必要があります。次のセクションから、その実装ポイントを順に見ていきます。

## 実装ポイント

先ほど挙げた 3 つの不足と、それを埋める実装の対応は次のとおりです。

| 不足 | 担当 | 実装 |
| --- | --- | --- |
| ① 再開のトリガー | ジョブ基盤 | 前提: DB バックエンドのジョブ基盤を用意する |
| ② ステップ間の状態 | アプリ設計 | ポイント1: `step` で分割する／ポイント2: 状態を DB に置く |
| ③ 冪等性 | アプリ設計 | ポイント3: ステップを再実行安全にする／ポイント4: `cursor` で刻む／ポイント5: 外部副作用を冪等化する |
| ④ 再試行方針 | アプリ設計 | ポイント6: `retry_on` で再試行する例外を宣言する |

### 不足①: 再開のトリガー（ジョブ基盤の責務）

中断したジョブを再実行するトリガーを、`ActiveJob::Continuable` は持ちません。これは DB バックエンドのジョブ基盤が埋めます。

#### 前提: DB バックエンドのジョブ基盤を用意する

**フレームワークの責務**: なし。  
**開発者の責務**: ジョブ基盤の選定と設定。

たとえば Rails 8.1 標準の Solid Queue は DB をバックエンドとし、ジョブを永続キューで管理します。

config/environments/production.rb

```
config.active_job.queue_adapter = :solid_queue
```

Solid Queue でなくても、アダプタが対応していれば使用できます。

### 不足②: ステップ間の状態（中間状態の永続化）

ステップ間で中間状態を渡す仕組みを、`ActiveJob::Continuable` は持ちません。処理をステップに分割し（ポイント1）、ステップ間で受け渡す状態を DB に永続化する（ポイント2）ことで、アプリ側で埋めます。

#### ポイント1: `step` で処理をステップに分割する

**フレームワークの責務**: ステップ完了の進捗追跡、中断時の進捗の永続化、再開時の完了済みステップのスキップ。  
**開発者の責務**: どこをステップ境界にするかの設計。

`include ActiveJob::Continuable` したジョブの `perform` 内で `step` メソッドを呼ぶと、Continuable は各ステップの完了を進捗として追跡します。そして次のステップへ進む境界で、ジョブ基盤が停止要求を出していれば（デプロイや worker のシャットダウン時）、そこまでの進捗をジョブデータに書き出してジョブを再エンキューします。再開したジョブは、完了済みステップをスキップして最初の未完了ステップから実行します。

app/jobs/summarize\_pipeline\_job.rb

```
class SummarizePipelineJob < ApplicationJob
  include ActiveJob::Continuable

  def perform(document_id)
    @document = Document.find(document_id)
    @llm = LlmClient.new

    step :extract
    step :summarize
    step :format
    step :deliver
  end

  private

  def extract
    @document.create_sections!(@llm.extract(@document.body))
  end

  def summarize
    @document.update!(summary: @llm.summarize(@document.sections))
  end

  # format, deliver も同様
end
```

`step :extract` は、`extract` メソッドを 1 つのステップとして実行し、完了を進捗に記録します。要約ステップの手前まで進んだジョブがデプロイなどで中断・再開した場合、`extract` はスキップされ、`summarize` から再開されます。

ステップ境界の設計は開発者の判断です。原則は「やり直したくない高コストな処理（LLM 呼び出しなど）と、副作用を持つ処理を、それぞれ独立したステップに切り出す」ことです。複数の LLM 呼び出しを 1 ステップにまとめると、そのステップ内の後半でクラッシュしたとき前半の呼び出しもやり直しになります。

#### ポイント2: 状態はプロセスメモリではなく DB に置く

**フレームワークの責務**: なし  
**開発者の責務**: ステップ間で受け渡す状態の DB 永続化。

`ActiveJob::Continuable` は再開時にジョブを `perform` から再構築します。このとき、`step` の外に書いたコードは再開のたびに毎回実行されます。前のステップがインスタンス変数に保存した中間結果は引き継がれません（[active\_job/continuation.rb（rails v8.1.2）](https://github.com/rails/rails/blob/v8.1.2/activejob/lib/active_job/continuation.rb)）。

たとえば、次の実装は中断耐性を持ちません。

```
# 中断に耐えられない例: 抽出結果をメモリで持ち回る
def perform(document_id)
  @document = Document.find(document_id)
  step :extract
  step :summarize
end

def extract
  @sections = LlmClient.new.extract(@document.body)  # メモリにしか残らない
end

def summarize
  # 一度の実行で到達するとうまくいくが、
  # 再開して summarize から始まると @sections は nil
  @document.update!(summary: LlmClient.new.summarize(@sections))
end
```

このようにします。なお、後述しますが、各ステップはスキップされず複数回呼ばれる可能性や、同時に2つ以上のプロセスから実行される可能性があるので、冪等性も必要です。

app/jobs/summarize\_pipeline\_job.rb

```
def perform(document_id)
  @document = Document.find(document_id)
  step :extract
  step :summarize
end

def extract
  # 抽出結果を Document に紐づくレコードとして永続化する
  @document.create_sections!(LlmClient.new.extract(@document.body))
end

def summarize
  # 後続ステップは DB から読み直す。再開後でも欠落しない
  sections = @document.sections
  @document.update!(summary: LlmClient.new.summarize(sections))
end
```

### 不足③を埋める: 冪等性（再実行で壊れない設計）

再実行で副作用が二重に起きないこと（冪等性）を、`ActiveJob::Continuable` は保証しません。ステップが複数回実行されうることを前提に、ステップ単位の再実行安全性（ポイント3）、巨大なステップの再開点（ポイント4）、外部副作用の冪等化（ポイント5）をアプリ側で設計します。

#### ポイント3: 各ステップを再実行安全にする

**フレームワークの責務**: 完了済みステップのスキップ。  
**開発者の責務**: ステップ内コードを複数回実行しても壊れないようにする設計。

**ステップは複数回実行されうることを前提に書く必要があります。**`ActiveJob::Continuable` がステップ完了をスキップ対象と判断できるのは、その進捗がジョブデータに永続化されたあとだけです。進捗が永続化されるのは、中断（停止要求）や再試行でジョブが再エンキューされる時です。それを挟まずにプロセスがクラッシュすると、完了していたステップでも進捗が残っておらず、再開時に最初から再実行されます。各ステップ内のコードは複数回実行されても安全でなければなりません。  
また、バックエンドアダプターによっては、「At-least-once（少なくとも1回は実行する）」によって多重実行される可能性もあります。そのようなときに安全な設計でないと、多重課金など致命的な障害につながる恐れがあります。

再実行安全にする手段は、ステップが何をするかで変わります。

**早期 return**: 「そのステップが既に完了しているか」を出力の存在で判定できる場合に使えます。

app/jobs/summarize\_pipeline\_job.rb

```
def extract
  return if @document.sections.exists?  # 既に抽出済みなら何もしない
  @document.create_sections!(@llm.extract(@document.body))
end
```

**`find_or_create_by` を使う**: レコード単位で「あれば取得、なければ作成」を保証したい場合に使えます。

app/jobs/summarize\_pipeline\_job.rb

```
def summarize
  # 同じ document_id では既存の summary を取得し、なければ生成する
  summary = Summary.find_or_create_by(document: @document) do |s|
    s.body = @llm.summarize(@document.sections)
  end
  @document.update!(summary_id: summary.id)
end
```

**DBの一意制約**: 競合時に `RecordNotUnique` を発生させます。発生時はリトライで既存レコードを拾い直す設計にしておくとよいでしょう。

db/migrate/20260517000000\_add\_unique\_index\_to\_summaries.rb

```
class AddUniqueIndexToSummaries < ActiveRecord::Migration[8.1]
  def change
    add_index :summaries, :document_id, unique: true
  end
end
```

どの手段を使うかはステップの性質次第ですが、**「ステップは 1 回しか動かない」という前提でコードを書かないことが共通の原則**です。

#### ポイント4: 巨大なステップは `cursor` で刻む

**フレームワークの責任**: `cursor` の値の永続化と、再開時の復元。  
**開発者の責任**: ループ処理と進捗の前進。

1 つのステップが大量のデータを 1 件ずつ処理する場合、ステップ全体を 1 つのチェックポイント境界にすると、途中でクラッシュしたときにそのステップが丸ごとやり直しになります。

`ActiveJob::Continuable` の `cursor` は、単一ステップ内にサブステップ単位の再開点を設ける機能です（[ActiveJob::Continuation API ドキュメント](https://api.rubyonrails.org/v8.1/classes/ActiveJob/Continuation.html)）。`step` メソッドにブロック引数を取り、`start:` で初期値を指定すると、ステップ内で `cursor` を読み書きできます。

app/jobs/summarize\_pipeline\_job.rb

```
def perform(document_id)
  @document = Document.find(document_id)
  @llm = LlmClient.new

  step :extract, start: 0  # cursor の初期値を 0 にする
  step :summarize
end

def extract(step)
  sections = @document.sections.order(:position).to_a
  while step.cursor < sections.size
    section = sections[step.cursor]
    section.update!(extracted: @llm.extract(section.raw))
    step.advance!  # cursor を 1 進め、進捗を永続化する
  end
end
```

`step.advance!` を呼ぶと、`cursor` が 1 進み、その位置が永続化されます。再開時には `cursor` が復元された値から始まるので、途中から継続できる仕組みです。

ただし、以下に注意して設計してください。

**`cursor` で処理する 1 件ごとの処理も、再実行安全である**:  
`advance!` の前にクラッシュすれば、その 1 件は再実行されます。上のコードで `section.update!` が冪等（同じ section に同じ値を書くだけ）なのはそのためです。

**再開をまたいで処理対象の集合と順序が不変である**:  
`cursor` はインデックス位置を記録するだけなので、再開後に `sections` の件数や並びが変わると、`cursor` が指す位置が別の対象を指してしまい、処理の取りこぼしや重複が起きます。途中で対象が増減する場合は、インデックスではなく処理済み ID を記録する進捗管理に切り替えます。

#### ポイント5: 外部副作用は冪等キーと結果確認で冪等化する

**フレームワークの責務**: なし。  
**開発者の責務**: 副作用の冪等化のすべて。

ジョブ基盤も `ActiveJob::Continuable` も冪等化を一切代行しません。要件 4（冪等性）のうち副作用の冪等性は、完全にアプリ設計の責任です。

問題は、配信ステップが再実行されうることです。外部 API の呼び出しに成功しても、その完了が永続化される（中断・再試行でジョブが再エンキューされる）前にクラッシュすれば、再開時に配信ステップは丸ごと再実行され、外部 API が 2 回呼ばれます。

これは、アプリ側で冪等キーを作成して外部APIに渡すことで対策できます[^外部APIがべき当キーをサポートしている場合]。冪等キーは、リトライ・再開・デプロイをまたいで同じ値が再現される必要があるため、再実行で変化しない要素だけから生成します。タイムスタンプ・乱数・リトライ回数・LLM 出力など、再実行で変わる値は含めてはいけません。

```
# 副作用の重複実行を防ぐ冪等キー
# 再実行で変化しない要素（ここではドキュメント ID・ステップ名・操作種別）のみから
# 決定論的に生成する。
class IdempotencyKey
  def self.for(document:, step:, action:)
    [ "document", document.id, step, action ].join(":")
  end
end
```

このキーを外部 API に渡すと、外部側が重複排除します。課金 API や通知 API は冪等キー（idempotency key）を受け取るものが多く、たとえば Stripe は `Idempotency-Key` ヘッダで同じキーの再呼び出しを 1 回分として扱います（[Stripe API: Idempotent requests](https://docs.stripe.com/api/idempotent_requests)）。ただしこれは外部 API 側の機能であり、利用する外部 API が冪等キーを受け付けない場合、外部側での重複排除はできません。

外部 API 側の機能で冪等キーが使用できない場合は、事前に「すでに処理がリクエストされていないか」確認する API が提供されていればそれによって実現できます。他にも、外部 API の呼び出し成功時に、冪等キーを一意制約としたレコードをDBに記録していれば、それによって外部 API 呼び出しが実行済みであることがわかります。

このように、アプリ側の工夫で外部 API 呼び出しステップを冪等にするよう設計する必要があります。

### 不足④を埋める: 再試行方針（`retry_on`）

失敗を乗り越えてジョブを完走させる再試行方針を、`ActiveJob::Continuable` は持ちません。**進捗後のエラーの自動再開は進捗保全であって完走の保証ではなく**、どの例外を再試行するかは、通常の ActiveJob と同じく `retry_on` でアプリ側が宣言します（要件 3 に対応）。

#### ポイント6: `retry_on` でリトライ方針を決める

**フレームワークの責務**: リトライ時のステップスキップ（再試行でも完了済みステップは再実行されない）。  
**開発者の責務**: どの例外を再試行するかの方針。

**リトライ方針の決め方は、通常の ActiveJob と変わりません。** 再試行で解決する一時的な失敗のエラークラスを `retry_on` に宣言します。Continuable を使っていても、一時的な失敗を克服してジョブを完走するには必要です。後述するとおり、Continuable の自動再開はこの宣言の代わりにはならないからです。

app/jobs/summarize\_pipeline\_job.rb

```
class SummarizePipelineJob < ApplicationJob
  include ActiveJob::Continuable

  # 再試行で解決する一時的な失敗を再試行する。
  retry_on ApiTemporaryError, attempts: 10, wait: :polynomially_longer
```

`retry_on` による再試行はジョブの再エンキューですが、再エンキュー時にも `ActiveJob::Continuable` の進捗は保持されます。そのため再試行時も完了済みステップはスキップされ、未完了ステップだけが再実行されます。

ここで紛らわしいのが、`ActiveJob::Continuable` の自動再開機構です。ジョブが現在の実行で進捗（ステップ完了・カーソル前進）したあとに例外が起きると、Continuable は `retry_on` の宣言がなくてもジョブを再エンキューします。**リトライのように見えますが、これは進捗をジョブ基盤に書き戻して進捗ロスを防ぐための再エンキューであり、ジョブが再実行されるのはその副作用です。** 公式APIドキュメント（[ActiveJob::Continuation API](https://api.rubyonrails.org/v8.1/classes/ActiveJob/Continuation.html)）も、自動再開を「エラー時に進捗が失われる問題」への緩和策として説明しています。リトライ方針として数えるものではありません。

したがって、リトライ方針は `retry_on` に一元化します。克服したい一時的エラーは、進捗の前に起きるか後に起きるかに関わらず、すべて `retry_on` に宣言します。自動再開を当てにして省くと、自動再開は 1 ステップにつき 1 回しか行わないので、それだけでは完走のあてにできません。

自動再開の制御

自動再開は class attribute `resume_errors_after_advancing`（デフォルト `true`）で制御され、再開回数の上限は `max_resumptions`（デフォルトは無制限）で設定できます。ただしこれはリトライ方針の調整ではなく、進捗保全の機構です。`false` にして `retry_on` だけで制御しようとすると、`retry_on` に宣言していないエラークラスで失敗したとき、その実行の進捗が失われます。

`Continuation::Error` 系の例外は、進捗の有無にかかわらず自動再開の対象になりません。たとえば `InvalidStepError` は、ステップ構成と永続化済み進捗の不整合（ステップの改名・削除・並び替えなど）を主な原因として `ActiveJob::Continuable` が送出する例外で、アプリの更新時に起こりがちな障害（後述）に関わります。再試行してもステップ構成は変わらないため、`retry_on` の対象にもしません。

InvalidStepError が送出される条件の詳細

`InvalidStepError` の送出条件は、再開時の不整合検知だけではありません。`ActiveJob::Continuable` の検証ロジックでは、再開した進捗と現在のステップ構成が食い違うケース（expected to resume from）や実行順序の食い違いに加えて、ステップ名が `Symbol` でない場合・同名ステップが重複している場合・ステップが別のステップの中にネストしている場合にも同じ例外が送出されます。

実装は [`activejob/lib/active_job/continuation/validation.rb`（v8.1.2）](https://github.com/rails/rails/blob/v8.1.2/activejob/lib/active_job/continuation/validation.rb) を参照してください。本記事が扱うのは、このうち「進行中ジョブがある状態でのステップ構成変更」に起因するケースです。

## この構成で埋まらないこと

ここまでの実装ポイントにより Durable Agent の 4 要件を満たします。ただし、課題もあります。

**exactly-once はジョブ基盤が保証しない**。`ActiveJob::Continuable` も Solid Queue も、操作がちょうど 1 回だけ実行されることを基盤レベルでは保証しません。配信は at-least-once（少なくとも 1 回）です。ポイント5 の冪等設計は、この「複数回起きうる」を「複数回起きても 1 回分の結果に収まる」に変換して実質的に代替するものであって、呼び出し回数そのものを 1 回に固定するものではありません。

**サイレント障害は検知できない**。`ActiveJob::Continuable` は、障害検知を持ちません。ジョブ基盤が中断したジョブを再配信しない構成では、ワークフローが誰にも気づかれず停止し続けることがあります（[Diagrid: Checkpoints Are Not Durable Execution](https://www.diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows)）。ジョブの滞留や失敗を検知する監視は別途必要です。

**バージョンアップ時に再開が壊れることがある**。進行中のジョブがある状態でステップ構成を変更してデプロイすると、再開時に永続化済みの進捗と新しいステップ構成が食い違い、`InvalidStepError` で失敗する可能性があります 。ステップ名を不変の識別子として扱う、新ステップは末尾に追加するだけにする、破壊的な構成変更の前は進行中ジョブを drain する、といった運用規律で回避します。これはコードではなく運用で埋める領域です。

これらが要件になる本番ユースケース — 厳格な exactly-once 保証、自動的な障害検知と透過的なリカバリが必須 — では、Temporal のような専用の Durable Execution 基盤を検討する余地があります（[Temporal: Durable Execution Meets AI](https://temporal.io/blog/durable-execution-meets-ai-why-temporal-is-the-perfect-foundation-for-ai)）。`ActiveJob::Continuable` で組む構成が示せるのは「中断 → 未完了ステップからの再開と、高コスト処理の重複回避」であり、Temporal 級の保証とは保証の強度が異なります。

## まとめ

`ActiveJob::Continuable` で中断に強い AI エージェントを組むとき、フレームワークが提供してくれるのは「ステップ分割と進捗チェックポイント」「再開ロジック」の部分です。残りはジョブ基盤の選定とアプリ設計と実装で解決します。

* 不足①（再開のトリガー）: 永続化バックエンドのジョブ基盤を用意する。再開のトリガーと並行実行防止はここが担う
* 不足②（ステップ間の状態）: `step` で処理をステップに分割し、ステップ間の状態は永続化する。後続ステップは読み直す
* 不足③（冪等性）: 各ステップを完了チェック・`find_or_create`・一意制約で再実行安全にし、巨大なステップは `cursor` で刻む。外部副作用は冪等キーと結果確認で冪等化する
* 不足④（再試行方針）: 一時的な失敗のエラークラスを `retry_on` に宣言する。自動再開は進捗保全であって完走保証ではない

冪等性レイヤーと中間状態の永続化はアプリ設計に残り続けるコストで、特に冪等レイヤーは後付けしにくく、この負担はなかなか大きいです。

その負担を引き受ける見返りとして、専用クラスタのような追加インフラなしに、Rails のみで Durable Agent が成立します。厳格な exactly-once や自動的な障害検知が要件でない範囲であれば、Rails 標準機能の延長で中断に強い AI エージェントを組めます。

## 参考資料
