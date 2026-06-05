---
id: "2026-06-04-laravel-13-ai-sdkを試して一問一答形式のテストアプリを作成してみたclaude-ap-01"
title: "Laravel 13 AI SDKを試して一問一答形式のテストアプリを作成してみた（Claude APIを使用）"
url: "https://qiita.com/MASEE/items/d9666f9ee54aa27d87b1"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "GPT", "qiita"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

## はじめに

Laravel 公式の AI SDK（`laravel/ai`）を使って、質問を入力すると AI が回答を生成して一覧表示する Q&A アプリを作りました。
Laravel13でAI SDKが正式安定版となったのでテスト感覚で作成してみました。

APIはClaudeのAPIを使用しました。
（今回の使用モデルはHaiku 4.5）

この記事では実装の流れ、アプリケーションの動作について順番に解説します。


---

## 主な技術スタック

- Laravel 13.x
- laravel/ai（Laravel 公式 AI SDK）
- Anthropic Claude（AI プロバイダー）：Claude Haiku 4.5（課金額：5ドル）


---

## Laravel AI SDKのインストール
まずはcomposer経由でインストールします。
（※今回Docker上で作成していますので、docker compose exec app bashでコンテナ内に入って作業）

```bash
composer require laravel/ai
```

インストールが完了したら、設定ファイルを作成します。
```bash
php artisan vendor:publish --provider="Laravel\Ai\AiServiceProvider"
```

このとき/database/migrations/yyyy_dd_mm_xxxxx_create_agent_conversations_table.phpのmigrationファイルが作成されるので、以下を実行します。
```bash
php artisan migrate
```

実行すると、

- agent_conversations
- agent_conversation_messages

こちらは、例えばChatGPTのように、チャット形式のように以前の質問を引用して回答を生成するようなアプリを作成する場合に使用します。
今回は、一問一答形式のテストアプリを作成するので使いません。


---

## Claude API Keyの作成
① アカウント作成
https://console.anthropic.com に飛んで、サインインします。

② クレジットカード登録・チャージ
クレジットカードを登録して購入フローを完了させます。いくつか選択肢がありますが、今回は5ドルで課金しました。

③ API キーを作成
Claude Consoleというダッシュボードに遷移します。
メニューから「Get API keys（APIキーを取得）」を選択 → APIキーの名前を入力し、「Create Key（APIキーを作成）」ボタンを押して作成します。

④ キーをコピーして保存
キーが生成されると sk-ant-api03-から始まる長い文字列が表示されます。
この画面は一度しか表示されないので、必ずコピーして保管しておきます。

⑤ Laravel の .env に設定
```.env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxx
```


これで仕込みは完了です。
くれぐれも、.envをGitHubなどにpushしないよう気をつけてください。


---

## View、Controller、Modelの作成について
今回はLaravel 13 AI SDKの解説なので、画面や処理のロジックは解説を省きます。
以下のGitHubのリポジトリを参考にしてください。

https://github.com/MASANORI-M/test-laravel/tree/master/src

---

Viewファイルについては以下です。

src/resources/views/ai_index.blade.php
![スクリーンショット 2026-05-31 17.34.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2661712/db2d624c-1110-49ba-9c5d-2a15d6e3670c.png)
Top画面


src/resources/views/question.blade.php
![スクリーンショット 2026-05-31 17.34.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2661712/d23d582c-4b42-4d2e-9803-7d697a576247.png)
質問画面


src/resources/views/ansers.blade.php
![スクリーンショット 2026-05-31 17.34.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2661712/84cca89f-fcde-40c7-9560-5b6aa2411c8f.png)
回答一覧画面

---

各画面のビジネスロジックは以下のControllerファイルに記載
- src/app/Http/Controllers/QuestionController.php
- src/app/Http/Controllers/AnsersController.php

レイヤードアーキテクチャ（3層構造）で構成
```
  Controller          ← リクエストの受け取り・レスポンスの返却のみ
      ↓ 呼び出す
  Service             ← ビジネスロジック（今回ならClaude API呼び出し、回答一覧の取得など）
      ↓ 呼び出す
  Repository          ← DBとのやり取り
      ↓ 呼び出す
  Model / DB
  ```

---

Model / DBは以下のansersテーブルのみ作成しています。

| カラム名 | データ型 | コメント |
|-----|-----|-----|
|id|bigint||
|question|text|質問内容|
|answer|longtext|回答|
|status|tinyint|AIによる生成の、0: 待ち, 1: 完了, 2: 失敗|
|created_at|timestamp|作成日時|
|updated_at|timestamp|更新日時|


---

## Agent
Agentは、AIの役割をまとめるクラスになります。

### ① ai.phpの編集
``` src/config/ai.php
# 今回はClaude APIを利用するので以下のように変更
'default' => 'anthropic',
```


### ② Agentの作成
```
php artisan make:agent AnserAgent
```

### ③ src/app/Ai/Agents/AnserAgent.phpの編集
instructions()には、claudeやChatGPTに普段書いているようなプロンプトを記載します。
今回は質問に対して回答を生成して返す記述にしました。

``` src/app/Ai/Agents/AnserAgent.php
<?php

namespace App\Ai\Agents;

use Laravel\Ai\Contracts\Agent;
use Laravel\Ai\Promptable;
use Stringable;

class AnserAgent implements Agent
{
    use Promptable;

    public function instructions(): Stringable|string {
        return <<<'PROMPT'
        あなたは知識豊富なAIアシスタントです。
        ユーザーから送られてくる質問に対して、正確でわかりやすい回答を提供してください。

        厳守事項:
        - 出力は必ず日本語にすること。
        - 回答は簡潔かつ丁寧にまとめること。
        - 不明な点や判断できない内容については、推測せずその旨を正直に伝えること。
        - 質問の意図を正しく汲み取り、的外れな回答をしないこと。
        PROMPT;
    }
}
```


こちらで編集したクラスは、Controller側（Service）で呼び出します。
今回はQuestionService.phpで呼び出します。
```src/app/Services/QuestionService.php
<?php

namespace App\Services;

use App\Ai\Agents\AnserAgent;
use App\Repositories\QuestionRepository;
use Throwable;

class QuestionService
{
    public function __construct(
        private QuestionRepository $repository,
    ) {}

    public function store(string $question): void {
        $anser = $this->repository->create($question);

        try {
            # ansersテーブルに保存された質問事項を渡す
            $response = AnserAgent::make()->prompt($anser->question);
            $this->repository->save($anser, $response->text);
        } catch (Throwable $e) {
            logger()->error('AnserAgent failed', [
                'message' => $e->getMessage(),
                'trace'   => $e->getTraceAsString(),
            ]);
            $this->repository->failedSave($anser);
        }
    }
}
```


これで完成です。
テスト実行していきます。


## 実行してみる
質問画面に、事項を記入して「回答を生成」ボタンを押します。
![スクリーンショット 2026-05-31 17.02.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2661712/7dbf4ec0-c867-4c33-abfb-e0ab7214325c.png)


しばらくすると、回答一覧画面に回答が表示されました。
回答内容が少し簡素かなと思いましたが、プロンプトやモデルによって調整可能だと考えます。
![スクリーンショット 2026-05-31 18.05.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2661712/b3cd36bc-69d1-441d-a1c0-edbeaafa16fa.png)
![スクリーンショット 2026-05-31 18.05.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2661712/f945ab00-11c4-4dde-bcfb-cd48d14e7c4c.png)



---
従量課金なので、Claude Consoleのダッシュボードに使用量が表示されます。
0.01ドル消費とのことなので、今回のようなテストなら約500回くらい試せそうです。
![スクリーンショット 2026-05-31 17.36.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2661712/54570094-e758-4c06-aee6-f8c90a89fe35.png)



## まとめ
　Laravel AI SDKの正式安定版がリリースされたことにより、アプリケーションにAIが組み込みやす機能実装が容易になったと思いました。
　今後もいろいろ試していこうと思います。
