---
id: "2026-06-11-claude-code-をrag的に使えるチャットボットwebui-を作りましたopen-ccui-01"
title: "Claude Code をRAG的に使えるチャットボットWebUI を作りました（Open CCUI）"
url: "https://zenn.dev/bondicha/articles/4941e7750c0b4d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "TypeScript"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

## このツールは何？

**Open CCUI (Open Claude Code UI)** — ブラウザから Claude Code を操作できる AI ChatbotのWeb インターフェースです。

チャットボットの裏側で**本物の Claude Code** が動いており、ユーザーの質問に対して、必要に応じて Knowledge Baseから情報を探し出しながら回答します。PCやVPSにインストールするだけで、どこからでも、スマホからでも、Claude Codeベースの強力なチャットボットにアクセスできるようになります。

**主な特徴**

* Knowledge Baseを作成可能。システム全体で共有する共有Knowledge Baseと、ユーザーごとに隔離された個人Knowledge Baseの両方をサポート
* Claude Codeの強力なエージェント機能を活用した、Web SearchやRAGなどをベースにしたチャット

![ダッシュボード](https://static.zenn.studio/user-upload/a51d76409c22-20260611.png)  
*ログイン後のダッシュボード*

GitHub リポジトリ  
[https://github.com/bondICha/claude-code-kb-for-all](https://github.com/bondICha/Open-CCUI)

## 背景

皆さん、RAG（Retrieval-Augmented Generation）は何を使っていますか？  
私はRAGを諦めました。

いろいろなRAGツールはありますが、いまいちうまくいかないんですよね。そもそも、RAGで「ベクタライズしてコサイン類似度が高いものを抽出して……」と言われても、「**本当に必要なデータが取れているのか？**」「**重要なデータを取りこぼしていないか？**」と、**不安になりませんか？**

一方で、コーディング時に使う **Claude Code** は、人間の感覚に近い形でデータを見つけ出してくれるため、なんとなく安心感があります。何をやっているか（どんなコマンドを実行して、どのファイルを読んだか）が透明なので、もし意図と違うファイルや情報を読んでいた場合は、**「そうじゃないよ！」と AI に対してフィードバックしやすい**のも便利です。

そこで、**Knowledge Baseに基づく AI Chatbot も、Claude Code にやらせれば良いじゃん**!と思い至りました。  
さらに、MCP（Model Context Protocol）を使って社内ツールと連携すれば、面倒な Vector DB などを自前で用意しなくても、社内ナレッジと連携した強力な AI Chatbot が作れてしまいます。

## 目的

* ユーザーが指定したファイル・フォルダ（Knowledge Base）をもとに、Claude Code がチャットで応答するツールを作る。
* 社内外のナレッジを取り込むため、Web 検索や MCP も組み込める設計にする。
* CLIの文字だらけの画面に抵抗がある人でも、簡単に Claude Code に触れられる機会を作る。

### Claude Code on the Web との違い

似たアプローチのものとして [Claude Code on the Web] がありますが、チャットというよりはコーディング用という感じです。また、ClaudeのSubscriptionでしか使えません。  
一方の本ツール「Open CCUI」は、**「Knowledge Base と連携可能なチャットツールのバックエンドとして Claude Code を活用する」** ことを主眼に置いています。特に、社内ドキュメントを読んで答えたり、資料や HTML を作ったり、Web を調べたりするのを主目的としています。  
**生のClaude Code**が使えるので、OpenRouterやClaude Code Routerなど、Claude互換のEndpointなら何でも使えます。

## 全体構成

Frontend - Backend - Claude Code Executor の 3 コンテナ構成です。

| レイヤー | 技術スタック |
| --- | --- |
| フロントエンド | React + TypeScript + Tailwind CSS + Vite |
| バックエンド | Express + TypeScript + Socket.IO |
| 実行環境 | Ubuntu コンテナ内で `claude -p`（stream-json）をサブプロセス実行 |
| 認証 | Google OAuth 2.0 |
| デプロイ | Docker + Docker Compose + Nginx |

ポイントは、**API サーバー（Backend）と Claude 実行環境（Executor）のコンテナを分離している点**です。

* Claude やブラウザ（Playwright）がクラッシュしても API サーバーは巻き込まれません。
* セッションシークレットや OAuth のクレデンシャルは Backend 側にのみ保持し、Executor には `ANTHROPIC_API_KEY` などの必要最小限の環境変数しか渡しません。Claude Code はサーバー上で任意のコマンドを実行できるため、**万が一悪意のある操作をされても認証情報にはアクセスできない**安全な構成にしています。
* Backend と Executor 間は WebSocket の独自プロトコルで通信し、`run` → `status` / `token` / `tool_use` / `complete` のイベントを逐次ストリーミングします。生成のAbortや、切断時の残存プロセスのクリーンアップもここで一元管理しています。

## 主な機能

### 機能 1. チャットインターフェース＋ツール実行ログ

普通のチャット AI と同じ感覚で会話できます。回答中は「考え中」「Bash 実行中」のようなライブステータスが表示されます。

![チャット画面](https://static.zenn.studio/user-upload/1757ab159fc2-20260611.png)  
*チャット画面。裏では本物の Claude Code が動いています*

Claude がコマンド実行や検索などのツールを使うと、回答の上に「🛠 ツール N 件」というパネルが表示され、クリックで展開すると各ツールの入力と結果を確認できます。AIが何をやってるか透明、というToolのCore機能なので、ここはこだわりました。

![ツール実行ログ（展開時）](https://static.zenn.studio/user-upload/68bb60a529ab-20260611.png)  
*ツール実行ログを展開したところ。各ツールをクリックするとさらに展開して、Input / Result の詳細が見られます*

### 機能 2. ナレッジベース（KB）—— Claude Code を agentic RAG として使う

ドキュメントを置いておくと、Claude が会話の中で参照してくれます。チャット画面から明示的に指定することもできます。

| スコープ | 内容 |
| --- | --- |
| **個人KB** | 自分だけが使えるドキュメント置き場 |
| **共有KB** | 全ユーザー共通の知識ベース |

ベクトル DB を使う一般的な RAG と違い、**Claude Code 自身が grep や Read でドキュメントを探索**します。埋め込みのインデックス作成は不要で、フォルダにファイルを置くだけ。  
何をどう検索してどのファイルを読んだかはツール実行ログに全部出るので、「ほんまにちゃんとデータ取ってんの？」という不安が解消されます。

### 機能 3. ユーザー隔離

複数ユーザーで使うための機能です。  
各ユーザーには専用の作業フォルダ（ /workspace/users/<uid>/ ）が割り当てられ、複数ユーザーで使うための機能です。各ユーザーには専用の作業フォルダ（ /workspace/users/<uid>/ ）が割り当てられ、ファイル・会話履歴・個人 KB は論理的に分離されます。  
ClaudeはUserごとの作業フォルダ内で実行されます。Claude Code に対してはシステムプロンプトで「自分のフォルダ外には絶対にアクセスしないこと」を指示しています。そのため、通常は他人のデータが見えることはありません。  
(※ただし、現時点では**すべての Claude プロセスが同一のコンテナ内・同一の OS ユーザー権限で動いているため、悪意のあるプロンプトインジェクション等によって制限を突破された場合、物理的に他人のフォルダを読み取られてしまうリスク**は残っています。完全なコンテナ単位での隔離は今後の課題です。)

### 機能 4. HTML ライブプレビュー

「ダッシュボードを作って」のような依頼をすると、生成された HTML が**右側のプレビューパネルにリアルタイムで描画**されます。Claude が書き直すたびにプレビューも更新されます。

![HTMLライブプレビュー](https://static.zenn.studio/user-upload/a8a3933387f6-20260611.png)  
*生成中の HTML が右側のパネルにリアルタイムで描画されます*

### 機能 5. Web 検索

「〜について最新情報を調べて」と頼むと、websearch スキルで 2 系統の検索を並列実行します。

1. **検索エンジン scrape**（web-search MCP）— [mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp)　を使い、Bing / Brave / DuckDuckGo を高速に検索
2. **実ブラウザ検索**（Playwright MCP）— Playwrightでページを開き、JS レンダリング後の内容を取得

両方の結果を突き合わせて、出典リンク付きで回答するようSystem promptを記述しています。

### 機能 6. その他

## セキュリティ上の注意

## 今後のロードマップ

* Claude Code Router とより密接に連携させ、消費したトークン数やコストを UI 上で可視化したい。
* Claude Code Executor を Kubernetes の Job のような**使い捨てコンテナ**として実行し、セキュリティとリソース管理を強化したい。
* より柔軟なMCPの組み込み。

## 作者の実行環境

個人用途として、NetCup というドイツのプロバイダが提供する 「**VPS 2000 ARM G11**」のManassasロケーションで運用しています。

スペック：

* 10 vCore (ARM64)
* 16 GB RAM
* 512 GB NVMe

月額 11.27 ユーロです（2026 年 6 月 11 日時点）。

当初は 8GB RAM のプランを使っていましたが、Claude を並列で動かしたり、Playwright MCP をブラウザ上で複数起動したりするとメモリ不足になることがあったため、16GB にアップグレードしました。

※Claude Code Routerなど他のツールも動かしているというのもあります。Open CCUIのみであれば、最安の「VPS 1000 ARM G11」（6 vCore, 8GB RAM, 256GB NVMeで　€ 6.53）でも足りると思います。

## 公開先

GitHub で MIT License で公開しています。Docker Compose で起動できます。

<https://github.com/bondICha/Open-CCUI>

## 謝辞

UI は Claude Code 用デスクトップアプリの [Glyphic](https://github.com/caioricciuti/glyphic) を参考にしています。生成停止（Stop）機構は [sugyan/claude-code-webui](https://github.com/sugyan/claude-code-webui)（MIT）のアボート処理を参考に独自再実装しました。Web 検索には [mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp)（MIT）を同梱しています。素晴らしい OSS を公開してくださった皆様に感謝いたします。

*※なお、本プロジェクトの公開にあたり、所属する会社・組織は一切関係しておらず、これにより発生した問題はすべて私個人に帰属します。*
