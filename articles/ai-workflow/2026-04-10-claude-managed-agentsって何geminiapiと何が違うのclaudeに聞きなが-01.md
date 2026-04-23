---
id: "2026-04-10-claude-managed-agentsって何geminiapiと何が違うのclaudeに聞きなが-01"
title: "Claude Managed Agentsって何？GeminiAPIと何が違うの？Claudeに聞きながら理解した"
url: "https://qiita.com/t_mando_/items/933ed7fa7b2d52b641f9"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

## はじめに

Anthropicが2026年4月に「Claude Managed Agents」をパブリックベータとしてリリースしました。  
名前だけ聞いても「APIとして使えるClaudeってこと？GeminiAPIみたいな感じ？」となったので、Claudeに直接質問しながら理解を深めました。

## Claude Managed Agentsとは？

一言で言うと、**「エージェントをそのままクラウドで動かせる実行環境込みのAPI」** です。

GeminiAPIが「モデルを呼ぶAPI」なのに対し、Managed Agentsは以下をAnthropicのクラウドが全部肩代わりしてくれます。

* サンドボックス付きコード実行
* セッション（会話状態）の永続管理
* Web検索・ファイル操作などのツール実行
* チェックポイント・クレデンシャル管理・権限管理
* エラー時のリトライ

## 3層構造で整理する

```
【ユーザー向けUI層】
  Claude.ai / ChatGPT / Gemini chat
  └── ブラウザで使う完成品アプリ
 
【エージェント実行基盤層】
  Claude Managed Agents   ← 今回の新サービス
  └── 自律実行・状態管理・ツール実行をまるごと提供
 
【モデル呼び出し層】
  Claude API（/v1/messages）/ OpenAI API / Gemini API
  └── モデルを呼ぶだけのAPI（従来からある）
```

> **補足：** Claude.aiはClaude APIの上にUIを乗せたもの。Managed AgentsはAPIに「エージェント実行インフラ」を丸ごと被せた新サービス。Claude APIは今後も普通に使い続けられます。

## GeminiAPIとClaude Managed Agentsの違い

### お題：「競合他社の最新情報を調べて、Slackにレポートを投稿するボット」

#### GeminiAPIで作る場合

Geminiは「質問に答えるだけ」なので、周辺の全部が自分の仕事になります。

* Web検索機能（Google Search APIを別途実装）
* Slack連携（Slack APIを自前で実装）
* 会話履歴の保存（DBに保存・読み込みの仕組みを作る）
* エラー処理・リトライ（タイムアウト対策も自前）
* 実行環境（自前のサーバーやLambdaで動かす）

#### Claude Managed Agentsで作る場合

開発者が用意するのはこれだけ：

* エージェントの定義（「競合調査してSlackに投稿して」という指示）
* Slack MCPサーバーの接続設定

あとはAnthropicのクラウドがWeb検索・レポート作成・Slack投稿・状態管理・リトライを全部やってくれます。

#### 開発者の負担量イメージ

```
Gemini API：
  自分         ████████████████████ 80%
  Gemini       ████ 20%
 
Managed Agents：
  自分         ████ 20%
  Anthropic    ████████████████████ 80%
```

## Laravelで実装すると？

普段業務でLaravelをメインで使用するので、イメージを深めるために例示してもらいました。

### Gemini API × Laravel

```
app/
├── Services/
│   ├── GeminiService.php         # API呼び出しラッパー
│   ├── GoogleSearchService.php   # 検索機能（別途実装）
│   └── SlackService.php          # Slack投稿（別途実装）
├── Jobs/
│   └── RunCompetitorResearch.php # キューで非同期処理
├── Models/
│   └── ConversationHistory.php   # 会話履歴をDBに保存
└── Http/Controllers/
    └── BotController.php         # エンドポイント
```

LaravelのQueue・Eloquent・HTTP Clientをフル活用しても、つなぎ合わせる作業は全部自分です。

### Claude Managed Agents × Laravel

```
app/
├── Services/
│   └── ManagedAgentService.php  # セッション作成・イベント送信だけ
└── Http/Controllers/
    └── BotController.php        # エンドポイント
```

Laravelを**薄いゲートウェイとして使うだけ**で済みます。

### 工数比較

| 作業 | Gemini API | Managed Agents |
| --- | --- | --- |
| マイグレーション（会話履歴DB） | 必要 | 不要 |
| Queue / Job実装 | 必要 | 不要 |
| 外部API（Search・Slack）連携 | 自前実装 | MCP設定のみ |
| リトライ・エラーハンドリング | 自前実装 | Anthropic側 |
| Serviceクラス数 | 4〜5個 | 1個 |

## Claude.aiとManaged Agentsは同じ仕組み？

「ChatGPTやGemini（チャット版）と同じような仕組み？」という疑問が浮かびますが、目的が根本的に違います。

|  | Claude.ai | Managed Agents |
| --- | --- | --- |
| 対象 | エンドユーザー | 開発者・企業 |
| 使い方 | ブラウザで会話 | APIで自分のサービスに組み込む |
| カスタマイズ | できない | エージェントの挙動を自由に定義 |
| 自律実行 | 基本的に1ターンずつ | 長時間・複数ステップを自律実行 |

Claude.aiは「Anthropicが作った完成品アプリ」、Managed Agentsは「自分のサービスにエージェント機能を埋め込むための部品」です。

## まとめ

* **Claude API** → GeminiAPIと同じ。モデルを呼ぶだけ。以前から存在する
* **Claude Managed Agents** → エージェント実行インフラごと提供する新サービス（2026年4月パブリックベータ）
* **Claude.ai** → Anthropicが作ったエンドユーザー向け完成品アプリ

シンプルなFAQボットならClaude APIで十分ですが、「調べる→考える→行動する→報告する」という複数ステップをまたぐタスクになった瞬間に、Managed Agentsのメリットが一気に出てきます。

料金は通常のAPIトークン料金に加え、アクティブ実行時間として **$0.08/セッション時間** が追加される仕組みです。

現在パブリックベータ中なので、気になる方はAnthropicのドキュメントをチェックしてみてください。

---

*この記事はClaudeとの対話を通じてまとめました。*
