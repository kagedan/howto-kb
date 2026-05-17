---
id: "2026-05-17-claude完全活用ガイド上級編api自動化エージェントでclaudeを仕組みに変える-01"
title: "Claude完全活用ガイド【上級編】API・自動化・エージェントで、Claudeを「仕組み」に変える"
url: "https://note.com/ai_fukugyou_navi/n/n17cad25fe40c"
source: "note"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "cowork", "Python", "note"]
date_published: "2026-05-17"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

## 

---

> **この記事はこんな人に向けて書きました**

中級編を読んで、プロンプト設計をマスターした方 Claudeを手動で使うだけでなく、自動で動かしたい方 ノーコード〜軽量コードで業務を自動化したい方 アプリやサービスにAIを組み込みたい方

---

## はじめに ─ 「使う」から「仕組みを作る」へ

初級・中級編では、ClaudeをUI（画面）から手動で操作してきました。

上級編のテーマは **「Claudeを仕組みの中に組み込む」** こと。

APIやMCPサーバー、エージェント設計を使いこなせば、Claudeは「毎回自分が操作するツール」から「勝手に動く自動化システム」に変わります。

プログラミングの知識がなくても使える部分から解説しますので、ぜひ最後まで読んでください。

---

## 第1章：Claude APIとは何か？

### 1-1. APIの基本概念

**API（Application Programming Interface）** とは、プログラムからClaudeを呼び出すための「接続口」です。

通常はブラウザでclaud.aiを開いて手動で操作しますが、APIを使うと：

### 1-2. APIキーの取得

```
① console.anthropic.com にアクセス
② アカウントを作成（claude.aiとは別）
③ 「API Keys」→「Create Key」
④ 生成されたキーをメモ（再表示されないので注意）
```

**料金：** APIは従量課金制（使った分だけ）。月数百円〜使えます。

### 1-3. 最もシンプルなAPI呼び出し

ターミナル（コマンドライン）で以下を実行するだけでClaudeと会話できます：

```
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: あなたのAPIキー" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "こんにちは！"}
    ]
  }'
```

### 1-4. Pythonから呼び出す（最もよく使われる方法）

```
import anthropic

client = anthropic.Anthropic(api_key="あなたのAPIキー")

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "このメールを要約してください：（本文）"}
    ]
)

print(message.content[0].text)
```

**たったこれだけ**で、Claudeの回答がプログラムから取得できます。

---

## 第2章：APIの実践活用パターン

![](https://assets.st-note.com/img/1778893687-CsuP7oGNFVBHyInwpJEUrSqh.png?width=1200)

### 2-1. パターン①：バッチ処理（大量データの一括処理）

100件のお客様レビューを一括で感情分析する例：

```
import anthropic

client = anthropic.Anthropic(api_key="あなたのAPIキー")

reviews = [
    "商品の品質は良かったですが、配送が遅かった。",
    "期待通りの商品でした。また購入します！",
    "サイズが合わなかった。返品したい。",
    # ... 残りのレビュー
]

results = []
for review in reviews:
    response = client.messages.create(
        model="claude-haiku-4-5",  # 速くて安いモデルを使用
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": f"以下のレビューの感情を「ポジティブ/ネガティブ/中立」で分類し、理由を一言で：{review}"
        }]
    )
    results.append(response.content[0].text)

# 結果をCSVに保存
with open("results.csv", "w") as f:
    for r in results:
        f.write(r + "\n")
```

### 2-2. パターン②：定期実行（スケジュール自動化）

毎朝9時に競合他社のサイトを調査してレポートをSlackに送る、といった自動化が可能です。

```
import anthropic
import schedule
import time

def daily_report():
    client = anthropic.Anthropic(api_key="あなたのAPIキー")
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": "今日の業務優先タスクリストを作成してください。（社内データ参照）"
        }]
    )
    
    # Slack等に送信する処理
    send_to_slack(response.content[0].text)

schedule.every().day.at("09:00").do(daily_report)
```

### 2-3. パターン③：システムプロンプトで役割を固定

APIでは**システムプロンプト**を設定することで、Claudeの役割を固定できます。

```
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="""
    あなたは株式会社〇〇のカスタマーサポートAIです。
    以下のルールを必ず守ってください：
    - 返答は必ず敬語で、200文字以内
    - 返金・キャンセルの質問は「担当者に確認します」と答える
    - 商品の在庫情報は答えない
    """,
    messages=[
        {"role": "user", "content": "注文した商品がまだ届きません"}
    ]
)
```

---

## 第3章：ノーコードで自動化する（Zapier・Make）

プログラムを書かなくても、ノーコードツールでClaudeを自動化できます。

### 3-1. Zapier × Claude

**Zapierとは：** アプリ同士を「トリガー→アクション」でつなぐノーコードツール

**活用例：**

トリガー アクション（Claude） 結果 Gmailに新着メール 内容を要約してSlackに送信 メール確認の時間を削減 Googleフォームに回答 回答を分析してスプレッドシートに記録 アンケート集計を自動化 カレンダーに予定追加 事前準備リストを自動作成 会議準備の手間を削減 ECサイトに注文 お礼メールを自動生成・送信 フォローメールを自動化

**設定手順：**

```
① Zapierにログイン
② 「Create Zap」をクリック
③ トリガーアプリを選択（例：Gmail）
④ アクションに「Anthropic Claude」を選択
⑤ プロンプトを設定
⑥ テスト実行して確認
```

### 3-2. Make（旧Integromat）× Claude

Makeは視覚的なフロー設計ができるため、複雑な処理の自動化に向いています。

**活用例：週次レポート自動生成**

```
Googleアナリティクス → データ取得
        ↓
    Claude → データを分析してレポート文を生成
        ↓
Google Docs → レポートを自動作成
        ↓
    Slack → チームに自動通知
```

---

## 第4章：MCP（Model Context Protocol）サーバー

![](https://assets.st-note.com/img/1778893711-3TabldjJkRSz7CopVIi6qQBX.png?width=1200)

### 4-1. MCPとは何か？

**MCP（Model Context Protocol）** は、Claudeと外部ツール・サービスを接続するための標準的な仕組みです。

2024年末にAnthropicが発表し、急速に普及しています。

**MCPが革命的な理由：** プラグインのようにインストールするだけで、ClaudeがGitHub・Notion・Slack・データベースなど外部サービスを**直接操作**できるようになります。

### 4-2. 代表的なMCPサーバー

MCPサーバー できること GitHub MCP リポジトリの読み書き・PR作成・Issue管理 Notion MCP ページ作成・データベース操作 Slack MCP メッセージ送受信・チャンネル管理 Google Drive MCP ファイル読み書き・共有 PostgreSQL MCP データベースの読み書き・SQL実行 Puppeteer MCP ブラウザの自動操作（スクレイピング等） Filesystem MCP ローカルファイルの読み書き

### 4-3. MCPの設定方法（Claude Desktopの場合）

```
// claude_desktop_config.json に追記
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token"
      }
    },
    "notion": {
      "command": "npx",
      "args": ["-y", "@suekou/mcp-notion-server"],
      "env": {
        "NOTION_API_TOKEN": "your_token"
      }
    }
  }
}
```

設定後、Claudeに「GitHubの〇〇リポジトリにあるREADMEを確認して」と話しかけるだけで、自動でGitHubにアクセスして内容を取得します。

---

## 第5章：エージェント設計

![](https://assets.st-note.com/img/1778893777-QSMixTKvskFJUE2Xna4whLl0.png?width=1200)

### 5-1. エージェントとは何か？

**エージェント** とは、複数のステップを自律的に実行するAIシステムです。

通常のClaudeの使い方：

```
人間が質問 → Claudeが回答 → 終わり
```

エージェントの動き方：

```
人間が「〇〇をやっておいて」と指示
    ↓
Claude が自分でステップを考える
    ↓
ツールを使ってデータを収集
    ↓
収集した情報をもとに処理
    ↓
結果をレポートにまとめて報告
    ↓
必要なら追加ステップを実行
```

### 5-2. Claude Codeによるエージェント活用

Claude Code（CLIツール）は、エージェントとして特に強力です。

```
# インストール
npm install -g @anthropic-ai/claude-code

# 起動
claude

# 指示の例
「このプロジェクトのコードを読んで、バグを見つけて修正してください」
「テストを実行して、失敗しているテストを直してください」
「README.mdを現在のコードの状態に合わせて更新してください」
```

Claude Codeは指示に従って自律的にファイルを読み、コードを修正し、テストを実行し、問題を解決します。

### 5-3. エージェント設計の3原則

```
① 明確なゴール設定
   「何を達成したら完了か」を明確に伝える

② ツールの適切な提供
   必要なMCPサーバーや権限を事前に設定しておく

③ 人間のチェックポイント
   重要な処理の前には人間の確認を挟む設計にする
```

---

## 第6章：上級者の実践ワークフロー集

### 6-1. コンテンツ生産パイプライン

```
① キーワードリスト（CSV） → Claude API で記事構成を自動生成
② 構成 → Claude API で本文を自動執筆
③ 本文 → Claude API でSEOチェック・改善提案
④ 完成記事 → Notion MCP でDBに自動保存
⑤ Slack通知 → 担当者に確認依頼
```

### 6-2. 顧客対応自動化

```
① 問い合わせメール受信（Gmail）
② Claude API で内容を分類（クレーム/質問/注文）
③ 分類に応じた返信テンプレートを生成
④ 人間が確認・承認
⑤ 承認された返信を自動送信
```

### 6-3. 社内ナレッジBot

```
① 社内マニュアル・議事録をVector DBに保存
② Slack で社員が質問
③ Claude API が関連ドキュメントを検索
④ ドキュメントを参照して回答を生成
⑤ Slack に自動返信
```

---

## まとめ ─ 上級編で学んだこと

```
✅ APIを使えばプログラムからClaudeを自由に操作できる
✅ システムプロンプトでカスタムAIアシスタントを作れる
✅ Zapier・Makeでプログラム不要の自動化が可能
✅ MCPサーバーで外部ツールと直接連携できる
✅ エージェントは複数ステップを自律実行する仕組み
✅ 組み合わせることで強力な業務自動化パイプラインが作れる
```

---

## 次のステップ ─ 専門編へ

上級編をマスターしたら、いよいよ専門編へ。

専門編では：

* **Cowork編：** チームでClaudeを活用する仕組みの作り方
* **Code編：** Claude Codeで開発生産性を10倍にする方法
* **Design編：** UIデザイン・画像分析・クリエイティブ制作への活用

…を具体的にお伝えします。

---

Claude完全活用ガイド【上級編】 著：note AI活用シリーズ
