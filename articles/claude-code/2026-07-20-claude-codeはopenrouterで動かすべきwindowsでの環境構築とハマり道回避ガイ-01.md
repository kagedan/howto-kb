---
id: "2026-07-20-claude-codeはopenrouterで動かすべきwindowsでの環境構築とハマり道回避ガイ-01"
title: "Claude CodeはOpenRouterで動かすべき？Windowsでの環境構築とハマり道回避ガイド"
url: "https://zenn.dev/lluminai_tech/articles/538f1281268587"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "OpenAI", "zenn"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-rss"
query: ""
---

## はじめに

ルミナイR&Dチームの宮脇彰梧です。  
現在はマルチモーダルAIの研究を行う大学院生として、生成AIやAIエージェントの技術を実践的に探求しています。

AnthropicがリリースしたCLIエージェント「Claude Code」、ターミナルから直接コードを生成・編集してくれて最高ですよね。ただ、「Anthropic APIの課金設定が面倒」「OpenRouterのクレジットが余ってるからそっちを使いたい」という方も多いはず。

今回は、**Windows環境でClaude Codeの接続先をOpenRouterに切り替える方法と、その成功例**を実際のターミナル画面を交えて解説します。

### 💡 この記事で学べること

* Claude CodeをOpenRouter経由で動かすメリットとデメリット
* Windows特有の「環境変数の罠」とその回避策
* 既存のOllama設定と競合した際のトラブルシューティング
* 設定成功時の実際のステータス画面（答え合わせ）

### 📝 記事の構成

1. なぜこのテーマを選んだのか？
2. この技術は採用すべき？
3. 技術の仕組みと設計思想
4. 実装・検証
5. 筆者の考察
6. まとめ

### 🎯 結論

結論から言うと、「たまにしかClaude Codeを使わない」「OpenRouterに課金を一元化したい」なら、OpenRouter経由のセットアップは圧倒的にアリ（採用すべき）です。ただし、Windowsの環境変数特有の仕様（空文字が登録できない等）に引っかかると丸一日溶かすので、本記事の手順でサクッと回避してください。

## 1. なぜこのテーマを選んだのか？

Claude CodeはデフォルトでAnthropicの公式APIを見に行きます。しかし、我々開発者は**色々なLLM APIの課金をOpenRouterで一元管理している**ことが多いですよね。

「よし、環境変数の `ANTHROPIC_BASE_URL` をOpenRouterに向けよう！」と意気込んで設定したものの、なぜかClaude Codeが起動しない。ステータスを見ると謎のエラーを吐く。過去にローカルLLM（Ollama）で遊んだ時の残骸が邪魔をしている……。そんな**現場の泥臭いWindows環境構築あるある**を解決し、快適なAI駆動開発ライフを取り戻すために筆を執りました。

## 2. この技術は採用すべき？

実装に入る前に、そもそも\*\*公式APIではなく、あえてOpenRouterをプロキシとして使うべきか？\*\*を判断しましょう。

### 📊 公式API vs OpenRouter 比較表

| 比較項目 | Anthropic 公式API | OpenRouter経由 |
| --- | --- | --- |
| **セットアップの手間** | 🟢 楽（`claude login` のみ） | 🟡 やや面倒（環境変数の手動設定が必要） |
| **課金の管理** | 🟡 Anthropic専用のクレカ登録が必要 | 🟢 OpenRouterのプリペイド残高が使える |
| **モデルの柔軟性** | 🟡 Claudeシリーズのみ | 🟢（※理論上）APIキー次第で他モデルへのフォールバックも可能 |
| **環境競合のリスク** | 🟢 ほぼなし | 🔴 Ollama等の既存設定と衝突しやすい（後述） |

### 🤔 向いているケース・不向きなケース

* **⭕ クリティカルに効くケース：**
  + すでにOpenRouterに多額のクレジットをチャージしてある人。
  + AnthropicのConsoleにわざわざクレジットカードを登録したくない人。
  + 「使った分だけ」の完全従量課金で、細かくコストをコントロールしたい人。
* **❌ ぶっちゃけ微妙なケース：**
  + すでにClaude Proに課金していて、公式の連携でサクッと使いたい人。
  + 環境変数（システム変数／ユーザー変数）の違いを意識したくない、CLI初心者。

**【導入判断フローチャート】**

1. OpenRouterのアカウントと残高がある？ ➡️ **[No]** 公式APIを使おう。 **[Yes]** 次へ。
2. Windowsの「環境変数」をGUIで編集することに抵抗はない？ ➡️ **[No]** 公式APIが無難。 **[Yes]** **採用決定！本記事の手順へ進んでください。**

## 3. 技術の仕組みと設計思想（⚙️ Dev）

Claude Code（および多くのAnthropic SDK依存ツール）は、認証と通信先を**環境変数**から読み取る仕様になっています。

本来は `ANTHROPIC_API_KEY` を読んで `https://api.anthropic.com` にリクエストを送りますが、以下の変数を上書きすることで、通信先をOpenRouterのAPIエンドポイントに「騙くらかす」ことができます。

* `ANTHROPIC_BASE_URL`: 通信先を `https://openrouter.ai/api` に向ける。
* `ANTHROPIC_AUTH_TOKEN`: ここにOpenRouterのAPIキー（`sk-or-...`）を食わせる。

OpenRouterはOpenAI互換のAPIを提供しつつ、内部でAnthropicモデルへのルーティングを良しなにやってくれるため、ツール側からは「AnthropicのAPIと通信している」ように見えます。

## 4. 実装・検証（判断の裏付けとして）

ここからが本番です。Windows環境で、確実にOpenRouterへ接続するための設定を行います。  
**ここで私は、過去のOllama設定の残骸に気づかず1時間ほど虚無の時間を過ごしました（笑）。** 皆さんは同じ轍を踏まないでください。

### STEP 1: Windowsの「環境変数」GUIを開く

1. Windowsキーを押し、「検索」に `環境変数` と入力します。
2. **「環境変数を編集する」**（または「システム環境変数の編集」）をクリックします。
3. 画面上部の「ユーザー環境変数」の枠に注目してください。

### STEP 2: 【落とし穴】過去の残骸を削除する

もし過去にOllama等で遊んでいた場合、`ANTHROPIC_AUTH_TOKEN` の値が `ollama` になっていることがあります。これがあるとClaude CodeがOllamaに繋ぎに行って死にます。

* **対処:** 一覧に `ANTHROPIC_AUTH_TOKEN = ollama` があれば、選択して「削除(D)...」をクリック。

### STEP 3: OpenRouter用の変数を新規追加

「ユーザー環境変数」の枠で、「新規(N)...」をクリックし、以下の **3つ** を順番に追加します。

1. **APIキーの設定**
   * 変数名：`OPENROUTER_API_KEY`
   * 変数の値：`sk-or-あなたのOpenRouterキー`
2. **接続先URLの変更**
   * 変数名：`ANTHROPIC_BASE_URL`
   * 変数の値：`https://openrouter.ai/api`
3. **Claude Codeへのキー受け渡し**
   * 変数名：`ANTHROPIC_AUTH_TOKEN`
   * 変数の値：`sk-or-あなたのOpenRouterキー` （※1と同じ値を入れる）

### 🚨 【超重要】Windows GUI特有の罠：ANTHROPIC\_API\_KEYは「触らない」

公式ドキュメントなどでは `export ANTHROPIC_API_KEY=""`（空にする）と書かれていますが、**WindowsのGUI設定では「空文字」を登録できません。**  
無理に設定しようとするとエラーになるか無視されます。

* **正解：** `ANTHROPIC_API_KEY` は**最初から追加しない**のがベストです。もし既に変な値が入っているなら「削除」してください。

### STEP 4: ターミナルの再起動と感動の瞬間（成功例）

**現在開いているPowerShellやコマンドプロンプトをすべて閉じます。**（閉じないと環境変数が再読み込みされません）。  
新しくターミナルを開き、Claude Codeを起動してステータスを確認しましょう。

**▼ 成功時の実際のステータス画面**  
無事に設定が完了すると、以下のように `Anthropic base URL` が OpenRouter を向き、モデルが正しく認識されます！

```
──────────────────────────────────────────────────────────────────────────────────
   Status   Config   Usage                                                                                                                                                                                                                                                            
                                                                                                                                                              
 Version: 2.1.89                                                                                                                                              
 Session name: /rename to add a name                                                                                                                          
 Session ID: ~~~~                                                                                                         
 cwd: C:\env\note                                                                                                                                             
 Auth token: ANTHROPIC_AUTH_TOKEN                                                                                                                             
 Anthropic base URL: [https://openrouter.ai/api](https://openrouter.ai/api)                                                                                                                
                                                                                                                                                              
 Model: sonnet[1m] (claude-sonnet-4-6[1m])                                                                                                                    
 Setting sources: User settings                                                                                                                               
 Esc to cancel  
──────────────────────────────────────────────────────────────────────────────────
```

`Anthropic base URL: https://openrouter.ai/api` と `Model: sonnet[1m]` などのモデル名が確認できれば完全勝利です！これであなたのCLIはOpenRouterの恩恵をフルに受けられます。

## 5. 筆者の考察

今回の検証で面白かったのは、**CLIツールがいかに素直に環境変数に従うか**という点です。

モダンなAIツールはブラックボックスに見えがちですが、内部的には昔ながらのUNIX的な「環境変数でエンドポイントを切り替える」というシンプルな設計思想を踏襲しています。だからこそ、OpenRouterのようなプロキシサービスが輝くわけです。

ただ、WindowsのGUI環境変数設定が「空文字を許容しない」という仕様は、マルチプラットフォーム前提のモダン開発において地味なペインポイント（痛手）になりがちです。Mac/Linux向けの `export FOO=""` というシェルスクリプトのノリをそのままWindowsに持ち込むと痛い目を見ます。  
今回のように「設定を空にするのではなく、変数そのものを存在させない（消す）」というアプローチが、Windows環境におけるAPIオーバーライドの最適解だと言えるでしょう。

## 6. まとめ

1. **コスト一元化に最適：** Claude CodeはOpenRouter経由にすることで、課金をスマートにまとめられます。
2. **既存設定の競合に注意：** `ANTHROPIC_AUTH_TOKEN = ollama` などの過去の残骸は必ず削除すること。
3. **Windowsの罠を回避：** `ANTHROPIC_API_KEY` は空文字設定ではなく「設定自体をしない（削除する）」のが正解。
4. **成功の証：** `/status` で `Anthropic base URL: https://openrouter.ai/api` が出れば勝利。

今後は、このOpenRouter経由のClaude Codeに、さらにMCP（Model Context Protocol）を組み合わせて、社内ドキュメントを読み込ませた自律型エージェントの構築なんかも検証していきたいですね。

ぜひ皆さんのターミナルにも、安くて賢いClaudeを住まわせてみてください！

---

## *執筆：宮脇 彰梧（ルミナイ株式会社 / Lluminai）*

【現在採用強化中です！】

* AIエンジニア
* PM/PdM
* 戦略投資コンサルタント

▼代表とのカジュアル面談URL

<https://pitta.me/matches/VCmKMuMvfBEk>
