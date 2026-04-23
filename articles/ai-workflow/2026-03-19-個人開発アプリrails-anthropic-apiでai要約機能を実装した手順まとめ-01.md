---
id: "2026-03-19-個人開発アプリrails-anthropic-apiでai要約機能を実装した手順まとめ-01"
title: "【個人開発アプリ】Rails × Anthropic APIでAI要約機能を実装した手順まとめ"
url: "https://qiita.com/masa_tech_0326/items/9506e0ca3c975f308e9d"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

## はじめに

個人開発をしているRailsアプリ「[MabaTalk](https://mabatalk.com/)」では、利用者のメッセージ履歴をログとして蓄積しています。

しかし、ログが増えるにつれて「どのような傾向があるのか」を人手で振り返ることが難しくなるという課題がありました。

そこで、Anthropic APIを利用し、ログの内容を**AIで要約する機能**を実装しました。

本記事では、AI要約機能の実装手順に加えて、外部APIとの連携処理をService Objectとして切り出し、Controllerの責務を肥大化させない設計についても解説します。

RailsでAI機能を組み込んでみたい方の参考になれば幸いです。

MabaTalkを開発した背景は下記note記事で紹介しています。

["伝えたいのに伝えられない"を減らしたい。未完成のまま「MabaTalk」を公開しました。](https://note.com/prime_snail5740/n/n02d9f797d46a?from=notice)

## 想定読者

* Railsで外部API連携を実装してみたい方
* AI（LLM）を既存のRailsアプリに組み込みたい方

## 実装の全体像

### 構成ファイル

| ファイル | 役割 |
| --- | --- |
| `config/routes.rb` | エンドポイントの定義 |
| `app/controllers/ai_summaries_controller.rb` | リクエスト制御 |
| `app/services/ai_summary_service.rb` | ログ取得・集計・プロンプト生成・API呼び出し |
| `app/models/ai_summary.rb` | 再生成制限ロジック |
| `app/views/analytics/show.html.erb` | 要約の表示・ボタン |

### 処理の流れ

実際の処理の流れは下記となっています。

```
ユーザーが「AI で振り返る」ボタンを押す
  ↓
① 二重送信防止・ログ存在チェック
  ↓
② AiSummaryService
   ログ取得 → 集計 → テキスト変換 → Anthropic APIに送信
  ↓
③ Serviceで生成された要約テキストをDBに保存
  ↓
④ 振り返りページに表示
```

### なぜこの設計にしたか

API呼び出し・集計ロジックをControllerに直接書くと、Controllerが肥大化して保守しにくくなります。  
`AiSummaryService`として切り出すことで：

* Controllerは「リクエストの受け取りとレスポンス」だけに集中できる
* 将来バッチ処理などから同じServiceを再利用できる
* ロジック単体でテストしやすくなる

という意図があります。

## 前提環境

今回私が実行した環境です。

```
- Ruby: 3.3.6
- Rails: 7.2.3
- DB: PostgreSQL 17
- 認証: Devise
- 実行環境: Docker
```

## APIキーの取得・設定

### ① Anthropicのアカウント作成・APIキー取得

1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウント作成・ログイン
3. 「API Keys」からキーを発行

### ② gemのインストール

```
# Gemfile
gem "anthropic", "~> 1.23"
```

### ③ APIキーをcredentialsに保存

```
bin/rails credentials:edit
```

以下を追記：

```
anthropic:
  api_key: sk-ant-xxxx
```

### ④ 使い方

```
# コード内でこう呼び出す
api_key = Rails.application.credentials.dig(:anthropic, :api_key)
client = Anthropic::Client.new(api_key: api_key)

response = client.messages.create(...)
```

上記のコードでは、まず credentials に保存したAPIキーを取得し、  
そのキーを使ってAnthropicのクライアントを生成しています。

client はAnthropic APIとの通信を行うためのオブジェクトで、  
messages.create を呼び出すことで、実際にAIへリクエストを送信できます。

(実装コードでは1行でまとめていますが、記事では処理の流れを分かりやすくするために分けて記載しています。)

> **なぜ `.env` ではなく `credentials` を使うか**  
> Railsの `credentials.yml.enc` は暗号化された状態で管理でき、Gitで安全に共有できます。`.env` はローカル環境ごとに管理する必要があり、チーム開発や本番環境での運用が煩雑になりがちです。

※APIキーは絶対にコードに直書きしないように要注意です。

## DB・Modelの設計

AIによって生成された要約結果をユーザーごとに保存し、再生成や表示を効率的に行うためのデータ構造を設計しました。

### マイグレーション

```
class CreateAiSummaries < ActiveRecord::Migration[7.2]
  def change
    create_table :ai_summaries do |t|
      t.references :user, null: false, foreign_key: true, index: { unique: true }
      t.text :content, null: false
      t.datetime :generated_at, null: false
      t.timestamps
    end
  end
end
```

### カラム設計の意図

今回の設計では、AI要約結果をユーザーごとに一意に管理し、常に最新の要約をシンプルに参照できる構成にしています。

また、AI生成日時は再生成制限などのビジネスロジックで使用するため、`updated_at` とは分離して専用のカラムとして管理しています。

履歴として複数保持する設計も考えられますが、  
今回は「直近30日の傾向を素早く確認する」という用途を優先し、  
上書き型のシンプルな設計を採用しています。

| カラム | 型 | 理由 |
| --- | --- | --- |
| `user_id`（unique） | references | 1ユーザー1要約を強制 |
| `content` | text | AI要約は256文字を超えるためstring型では不足 |
| `generated_at` | datetime | `updated_at` はレコード更新のたびに変わるため、AI生成日時専用カラムとして分離 |

### Modelの実装

AI要約の再生成可否の判定など、データに紐づくビジネスロジックをModelに定義しています。

```
class AiSummary < ApplicationRecord
  belongs_to :user

  validates :content, :generated_at, presence: true

  REGENERATE_INTERVAL = 1.day

  def regeneratable?
    generated_at < REGENERATE_INTERVAL.ago
  end

  def next_regeneratable_at
    generated_at + REGENERATE_INTERVAL
  end
end
```

`generated_at` に基づいた再生成可否の判定は、AI要約におけるビジネスルールのため、Modelに集約することでロジックの分散を防いでいます。

## Service Objectの実装

このServiceは、ユーザーのメッセージログを集計・整形し、Anthropic APIを利用して要約テキストを生成する責務を持ちます。

処理の流れは以下の通りです：

1. ログを取得
2. 集計して構造化
3. プロンプトを生成
4. APIに送信して要約を取得

### なぜControllerに直接書かなかったか

* **Controllerの肥大化を防ぐ**：Controllerの責務を「リクエストの受け取りとレスポンス」だけに絞る
* **再利用できる**：将来バッチ処理などから同じServiceを呼び出せる
* **保守性が上がる**：API処理の修正はService Objectだけ触れば済む
* **外部APIとの通信は副作用を伴うため**：Controllerから分離し責務を明確にする

### 実装

```
class AiSummaryService
  LOOKBACK_DAYS = 30
  MAX_TOKENS = 600
  MODEL = "claude-haiku-4-5-20251001"
  SYSTEM_PROMPT = <<~PROMPT.freeze
    あなたは、重度障害のある方のコミュニケーション支援アプリの
    ログを振り返るためのアシスタントです。
    ...
  PROMPT

  # クラスメソッドで呼び出せるようにする（呼び出し側がnewを意識しなくて済む）
  def self.call(user:)
    new(user:).call
  end

  def initialize(user:)
    @user = user
  end

  def call
    logs   = @user.message_logs.where(created_at: LOOKBACK_DAYS.days.ago..)
    stats  = build_stats(logs)              # ① 集計
    prompt = build_prompt(stats, logs.size) # ② テキスト変換
    generate_summary(prompt)                # ③ API送信・要約取得
  end

  private

  # ログをカテゴリ・項目ごとに件数集計する
  # 例: { "飲みもの" => { "水" => 2, "お茶" => 1 } }
  def build_stats(logs)
    logs.group_by(&:message_category_name)
        .transform_values { |cat_logs|
          cat_logs.group_by(&:flow_item_name).transform_values(&:count)
        }
  end

  # 集計データをAPIに渡すテキスト形式に変換する
  # 件数の多い順に並べることでAIが重要な傾向を把握しやすくなる
  def build_prompt(stats, total)
    lines = ["直近30日のコミュニケーション記録（合計 #{total} 件）\n"]
    stats.each do |cat, items|
      lines << "[#{cat}]"
      items.sort_by { |_, count| -count }
           .each { |item, count| lines << "  - #{item}: #{count}件" }
    end
    lines.join("\n")
  end

  # Anthropic APIを呼び出して要約テキストを取得する
  def generate_summary(prompt)
    client = Anthropic::Client.new(
      api_key: Rails.application.credentials.dig(:anthropic, :api_key)
    )
    response = client.messages.create(
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: SYSTEM_PROMPT,  # AIへの指示（医療的診断をしない等）
      messages: [{ role: "user", content: prompt }]  # 集計テキストを渡す
    )
    response.content.first.text  # レスポンスから要約テキストだけ取り出す
  end
end
```

AIへの指示(プロンプト)はService内で管理しています。  
医療的な断定を避ける・推測を制限するなど、実際の利用シーンで誤解を生まないよう制約を設けています。

### 設計のポイント：1メソッド1責務

| メソッド | 責務 |
| --- | --- |
| `build_stats` | ログをカテゴリ・項目ごとに件数集計 |
| `build_prompt` | 集計データをAPIに渡すテキストに変換 |
| `generate_summary` | Anthropic APIを呼び出して要約テキストを取得 |

メソッドごとに責務を分離することで、処理の意図が明確になり、変更の影響範囲を限定できます。

例えばAPIのモデルを変更する場合は `generate_summary` のみ、集計のロジック変更は`build_stats`のみを修正すれば済みます。

## Controllerの実装

AI要約の生成リクエストを受け取り、事前チェック・Service呼び出し・保存・リダイレクトといった一連の制御を行います。

### ルーティング

AI要約はユーザーごとに1件のみ保持する設計のため、複数レコードを前提とする`resources`ではなく、単一リソースを扱う`resource`を使用しています。

```
# config/routes.rb
resource :ai_summary, only: [:create]
```

### 実装

```
class AiSummariesController < ApplicationController
  before_action :authenticate_user!

  def create
    # ① 二重送信防止・事前チェック
    current_user.with_lock do
      summary = current_user.ai_summary

      # 要約が存在していて再生成できない場合は弾く
      if summary&.persisted? && !summary.regeneratable?
        return redirect_to analytics_path,
                            alert: t("ai_summary.create.too_soon", ...)
      end

      # 直近30日のログが存在しない場合は弾く
      unless current_user.message_logs.where(created_at: 30.days.ago..).exists?
        return redirect_to analytics_path, alert: t("ai_summary.create.no_logs")
      end
    end

    # ② API呼び出しはService Objectに委譲（Controllerには書かない）
    content = AiSummaryService.call(user: current_user)

    # ③ 結果をDBに保存
    current_user.with_lock do
      summary = current_user.ai_summary || current_user.build_ai_summary
      summary.update!(content: content, generated_at: Time.current)
    end

    redirect_to analytics_path, notice: t("ai_summary.create.success")

  rescue Anthropic::Errors::APITimeoutError
    redirect_to analytics_path, alert: t("ai_summary.create.timeout")
  rescue Anthropic::Errors::APIError => e
    redirect_to analytics_path, alert: t("ai_summary.create.error")
  rescue StandardError => e
    redirect_to analytics_path, alert: t("ai_summary.create.error")
  end
end
```

### 工夫した点

**① 二重送信防止（`with_lock`）**

ユーザーが素早く2回ボタンを押した場合でも、DBレベルで排他ロックをかけることで二重にAPIが呼ばれないようにしています。

※ API呼び出しは時間がかかるため、ロックの範囲は最小限に留めています。

**② 早期リターン**

要約生成できない条件（再生成制限中・ログなし）を先にチェックして即座にリダイレクトします。条件をクリアしたリクエストだけAPI呼び出しに進みます。

**③ Service Objectへの委譲**

API呼び出し・集計ロジックは `AiSummaryService` に委譲し、Controllerは「チェック・保存・リダイレクト」だけを担います。

## Viewの実装

AI要約の状態(未生成・生成済み・再生成制限中)に応じて表示内容を切り替え、ユーザーが迷わず操作できるようにUIを構築しています。

### 表示の場合分け

要約の有無・ログの有無・再生成可否の3つの状態をもとに表示を分岐しています。

```
① 要約が存在する → 要約テキストを表示

② ログが1件以上ある？
   ├── Yes → 再生成制限中？
   │          ├── Yes → 次回可能日を表示
   │          └── No  → 生成／再生成ボタンを表示
   └── No  → 要約もない → ログなしメッセージを表示
```

### 実装

```
<%# ① 要約が存在すれば表示 %>
<% if @ai_summary %>
  <p class="whitespace-pre-line">
    <%= @ai_summary.content %>
  </p>
  <p class="text-xs text-stone-400 mt-3">
    <%= t("ai_summary.generated_at", date: l(@ai_summary.generated_at.to_date)) %>
  </p>
<% end %>

<%# ② ログが1件以上あるか %>
<% if @recent_log_count > 0 %>

  <%# 再生成制限中か %>
  <% if @ai_summary&.persisted? && !@ai_summary.regeneratable? %>
    <p><%= t("ai_summary.next_regeneratable", date: ...) %></p>

  <% else %>
    <%# 生成・再生成ボタン %>
    <%= button_to ai_summary_path, method: :post,
                  data: { turbo_submits_with: t("ai_summary.generating") } do %>
      <%= t("ai_summary.#{@ai_summary ? 'regenerate' : 'generate'}") %>
    <% end %>
  <% end %>

<% else %>
  <%# ログなしメッセージ %>
  <% unless @ai_summary %>
    <p><%= t("ai_summary.create.no_logs") %></p>
  <% end %>
<% end %>
```

### 実装のポイント

**状態に応じたUIの出し分け**

要約の有無・ログの有無・再生成制限の状態に応じて、表示内容やボタンの有無を切り替えています。

これにより、ユーザーが現在の状態を理解しやすく、次に取るべきアクションが明確になります。

**ボタン文言の切り替え**

初回生成と再生成でボタンの文言を自動で切り替えています：

```
<%= t("ai_summary.#{@ai_summary ? 'regenerate' : 'generate'}") %>
```

**処理中のUX改善**

ボタンを押した後、処理中は「振り返り中...」に文言が変わります。ユーザーへの視覚的フィードバックと二重押し防止を兼ねています：

```
data: { turbo_submits_with: t("ai_summary.generating") }
```

## 詰まったポイント・改善余地

### 改善余地①：依存性注入ができていない

現状は `generate_summary` の中で `Anthropic::Client.new` を直接生成しています。

```
# 現状
def generate_summary(prompt)
  client = Anthropic::Client.new(...)  # 内部で直接生成している
end
```

この実装だと、外部APIクライアントの生成と利用の責務が分離されておらず、外部依存を切り離せない状態になっています。

その結果：

* テスト時に本物のAPIが呼ばれてしまう
* モック（偽物）に差し替えられない
* テスト時にAPI費用がかかってしまう
* ネットワークやレスポンスに依存した不安定なテストになる

これは、「依存性注入(DI)ができていない状態」で、  
簡単にいうと「中で勝手に作っているので、外から差し替えられない設計」です。

### 改善案

```
def initialize(user:, client: default_client)
  @user = user
  @client = client
end

def default_client
  Anthropic::Client.new(
    api_key: Rails.application.credentials.dig(:anthropic, :api_key)
  )
end
```

これにより：

* テスト時にモックへ差し替え可能になる
* API費用をかけずにテストできる
* ネットワーク不要で高速・安定したテストになる

将来的にAPIを変更する場合（例：Claude → OpenAI）でも、呼び出し側のコードを大きく変更せずに対応できるようになります。

### 改善余地②：同期処理による待ち時間の発生

現状はAPI呼び出しを同期処理で行っているため、要約が生成されるまで（3〜10秒）ユーザーは結果が返るまで待つ必要があります。

この間、Railsのサーバーはその処理につきっきりになるため、他のリクエストを同時に処理しづらくなります。  
（これをスレッドがブロックされるといいます）

ユーザー数が少ない現状は問題ありませんが、アクセスが増えて同時に多くのリクエストが来るようになると、

といった影響が出る可能性があります。  
（このように、ユーザーが増えても安定して動作するかを「スケール」といいます）

### 改善案

ActiveJobを使って非同期処理に切り出すことで、API呼び出しをバックグラウンドで実行できます。

```
AiSummaryJob.perform_later(user: current_user)
```

これにより、ユーザーは待たずに画面遷移できるようになります。

ただし非同期にすると

* いつ生成が完了したか
* ユーザーにどのように通知するか

という別の設計が必要になるため、

今回は

* ユーザー数がまだ少ないこと
* 要約結果をその場で確認できるUXを優先したいこと

から、まずは同期処理でシンプルに実装しました。

特に介護現場では即時性が重要なケースもあるため、UXとのバランスを考慮した設計が必要だと感じています。

今後ユーザー数が増加した場合は、ActiveJobによる非同期処理への移行を検討しています。

## まとめ

今回の実装では、AI要約機能を通じて以下の点を意識して設計しました。

* **責務分離**：Service Objectを用いて、Controllerの肥大化を防ぎつつ、外部API連携ロジックを明確に分離
* **安全性とUXの両立**：`with_lock` による二重送信防止や再生成制限により、無駄なAPI呼び出しを抑制
* **データの意味の明確化**：`generated_at` を専用カラムとして持たせることで、生成日時の意図を明確に管理
* **用途に応じた技術選定**：医療・福祉領域での利用を考慮し、安全性の高いAnthropic APIを採用

また、同期処理による待ち時間や依存性注入ができていない点など、改善余地もあるため、今後は非同期処理やテスト容易性の向上にも取り組んでいきたいと考えています。

本記事が、RailsでAI機能を実装する際の設計の参考になれば幸いです。
