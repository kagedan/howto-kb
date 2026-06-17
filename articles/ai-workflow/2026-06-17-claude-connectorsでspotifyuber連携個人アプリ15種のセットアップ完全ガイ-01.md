---
id: "2026-06-17-claude-connectorsでspotifyuber連携個人アプリ15種のセットアップ完全ガイ-01"
title: "Claude ConnectorsでSpotify・Uber連携：個人アプリ15種のセットアップ完全ガイド"
url: "https://qiita.com/kai_kou/items/202b244a34a46b998eb9"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "GPT", "qiita"]
date_published: "2026-06-17"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月23日（米国時間）、AnthropicはClaudeの「Connectors」機能を大幅に拡張し、Spotify・Uber・Instacartなど **15種の個人向けアプリ** との連携を発表しました。

これまでClaude ConnectorsはMicrosoft 365やSlackなどのビジネスツールが中心でしたが、今回の更新により日常生活のアプリに直接つながる「パーソナルAIアシスタント」としての性格が大きく強まりました。

### この記事で解説すること
- Claude Connectorsの概要と今回の発表内容
- 新たに追加された15種のアプリ一覧と用途
- セットアップ手順（接続〜利用まで）
- 具体的なユースケースと会話例
- プライバシー・セキュリティの設計
- 開発者向けの技術アーキテクチャ（PKCE・APIエンドポイント）

### 対象読者
- Claude活用を深掘りしたいエンジニア・個人ユーザー
- AIアシスタントとサードパーティアプリ連携の仕組みを理解したい方
- OAuth/PKCEなどの認証フローに興味がある方

## TL;DR

- AnthropicがClaude Connectorsに15種のパーソナルアプリを追加（2026年4月23日、米国時間）
- 全Claudeプランで利用可能。モバイルはベータ提供中
- PKCE フローによる ephemeral トークン採用で、静的APIキー方式より安全
- 購入・予約前には必ずユーザー確認。データはモデル学習に未使用

## Claude Connectorsとは

Claude Connectorsは、Claudeの会話中にサードパーティサービスのデータや機能を直接呼び出せる仕組みです。ユーザーが一度アプリを連携しておくと、Claude は会話の文脈から「今はこのアプリが役立つ」と判断してサジェストしたり、ユーザーが指定したサービスに対してアクションを実行したりできます。

### 従来の対応アプリ（ビジネス中心）
- Google Drive / Google Docs
- Microsoft 365（Word・Excel・Outlook）
- Slack
- GitHub
- Notion
- Jira / Confluence

### 今回の追加（パーソナル向け15種）
2026年4月23日（米国時間）の発表で追加されたのは以下のアプリです。

| カテゴリ | アプリ名 | 主な用途 |
|---------|---------|---------|
| 音楽・エンタメ | Spotify | プレイリスト作成・楽曲再生 |
| 音楽・エンタメ | StubHub | コンサート・スポーツチケット検索 |
| 音楽・エンタメ | Audible | オーディオブック検索・再生 |
| 旅行・外食 | Booking.com | ホテル検索・予約 |
| 旅行・外食 | Tripadvisor | レストラン・観光スポットのレビュー |
| 旅行・外食 | Viator | 観光体験・ツアー予約 |
| 旅行・外食 | Resy | レストラン予約 |
| 移動・デリバリー | Uber | 配車サービス |
| 移動・デリバリー | Uber Eats | フードデリバリー |
| 食料品 | Instacart | 食料品オンライン注文 |
| アウトドア | AllTrails | ハイキングコース検索 |
| 家事・地域サービス | Taskrabbit | 家事代行・修繕業者手配 |
| 家事・地域サービス | Thumbtack | 地域サービス業者検索 |
| 財務 | Intuit TurboTax | 税務申告サポート |
| 財務 | Intuit Credit Karma | クレジットスコア管理 |

> 情報ソース: [New connectors in Claude for everyday life | Claude](https://claude.com/blog/connectors-for-everyday-life)（2026-04-23、米国時間）

## セットアップ手順

### 1. Connectors設定画面を開く

1. Claude.ai（https://claude.ai）にログイン
2. 左サイドバーの「**Customize**」タブをクリック
3. 「**Connectors**」セクションを選択
4. 接続したいアプリを探して「**Connect**」ボタンをクリック

### 2. OAuth認証で連携を許可

「Connect」ボタンを押すと、対象アプリのOAuth認証画面に遷移します。アプリへのログインとClaude側へのアクセス許可を行うことで連携が完了します。

### 3. 会話で利用する

連携後は、会話の中でアプリ名を指定するか、Claudeが文脈に応じて該当アプリをサジェストします。

```
ユーザー: 今週末のドライブ用に、最近聴いている音楽からプレイリストを作ってほしい
Claude: Spotifyの再生履歴をもとに2時間のプレイリストを作成しました。確認してからSpotifyに保存しますか？
```


> **モバイルアプリはベータ提供中**
> 2026年4月時点でモバイル版のConnectors機能はベータです。Web版（Claude.ai）では全プランで利用可能です。


## 具体的なユースケース

### 週末の旅行プランをまとめて手配

```
ユーザー: 来週末に大阪旅行を考えています。ホテルとレストラン、観光スポットをまとめて提案して

Claude: Booking.comで梅田・難波エリアのホテルを3件提案します。
        [ホテルA - ¥12,000/泊]
        [ホテルB - ¥18,000/泊]
        …
        また、Resyで金曜夜の人気レストランに空席があります。予約しますか？
        Tripadvisorの評価が高い観光スポットもリストアップしました。
```

### 食材注文をAIに任せる

```
ユーザー: 今週のメニューは親子丼、ハンバーグ、サラダ。必要な食材をInstacartで注文して

Claude: 3メニュー分の材料をリストにしました。
        鶏もも肉 300g、卵 6個、玉ねぎ 2個…（合計12品）
        注文金額は￥3,280の見込みです。注文を確定しますか？
```

### 気分に合うコンサートを探す

```
ユーザー: 来月、インディーズロックかジャズのライブに行きたい。おすすめは？

Claude: StubHubで来月の東京公演を調べました。
        - [アーティストA]: 5月15日 渋谷 ¥6,500〜
        - [アーティストB]: 5月22日 下北沢 ¥4,000〜
        ジャンルや価格帯で絞り込みますか？
```

### ハイキング計画を立てる

```
ユーザー: 今週末、初心者向けで2時間程度のハイキングコースを提案して

Claude: AllTrailsで東京近郊の初心者向けコースを3件見つけました。
        - 高尾山（陣馬山コース）: 距離8km、累積標高450m
        - 鎌倉天園: 距離6km、累積標高200m
        - 御岳山: 距離5km、累積標高180m
```

## プライバシーとセキュリティ

Anthropicは今回の発表と合わせて、Connectorsのプライバシーに関するポリシーを[公式ブログ](https://claude.com/blog/connectors-for-everyday-life)で公開しています。

### データ保護の設計方針

| 項目 | 内容 |
|------|------|
| モデル学習 | 連携アプリのデータはモデル学習に **使用しない** |
| クロスアプリアクセス | 連携アプリAは会話のうちアプリA関連の部分のみにアクセス可能 |
| 購入・予約 | 実行前に **必ずユーザー確認** を取るステップがある |
| 切断 | いつでも任意のアプリ連携を解除可能 |
| 有料配置なし | Anthropicはパートナーアプリから紹介料を受け取らない |

> **「有料配置なし」について**: Anthropicは、Claudeがあるアプリをサジェストするかどうかについて、パートナーから費用を受け取らないと明言しています。サジェストはあくまでユーザーの会話の文脈に基づきます。

## 技術アーキテクチャ（開発者向け）

### ChatGPT方式との違い

ChatGPTの初期プラグイン実装では、ユーザーが静的なAPIキーをクライアント側で保存・管理する方式でした。Claude Connectorsは、会話単位で発行・破棄される **ephemeral（一時的）アクセストークン** を採用しています。

### PKCE フロー

Claude ConnectorsはPKCE（Proof Key for Code Exchange）フローを用いてOAuth認証を行います。PKCE は認可コードが傍受されても悪用されにくい設計で、パブリッククライアント（ブラウザアプリやモバイルアプリ）向けの標準的なセキュリティ強化手法です。

```
1. Claude → code_verifier を生成
2. Claude → code_challenge = BASE64URL(SHA256(code_verifier)) を算出し認可リクエストに含める
3. ユーザー → サードパーティアプリのOAuth画面で許可
4. 認可サーバー → code_challenge を記録し、認可コード（authorization code）を返却
5. Claude → 認可コードと code_verifier をトークンエンドポイントへ送信
6. 認可サーバー → code_verifier を変換して保存済み code_challenge と照合し、一致すればアクセストークンを返却
7. Claude → 会話スコープ限定の ephemeral トークンとして使用（OAuthベストプラクティスに基づく設計）
8. 会話終了 → トークン自動破棄
```

### 開発者向けConnectors連携

Anthropicの公式プラットフォームドキュメント（[Claude API Docs](https://platform.claude.com/docs/en/home)）では、MCPサーバーやサードパーティサービスとの連携方法が説明されています。ConnectorsはLLMとサードパーティサービス間のスコープ付きトークンをブローカーする設計で、Claude API を利用するサードパーティ開発者も独自のConnectorをディレクトリに登録できる仕組みになっています。

開発者向けの詳細は [Claude Help Center](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities) を参照してください。

## 現時点の制限・注意点

- **日本語版アプリ対応**: 上記15アプリは主に北米向けサービス中心。日本国内でのサービス提供状況はアプリにより異なる
- **モバイル**: ベータ版のため機能制限の可能性がある
- **実行前確認**: Claudeは自律的に購入・予約を完了させない。ユーザーの最終承認が必要
- **ビジネス向けコネクタとの並用**: 個人向けと仕事向けの両コネクタを同じClaudeアカウントで利用可能

## まとめ

Claude Connectorsの個人向けアプリ対応拡張は、AIアシスタントの「日常生活への浸透」を加速する大きなアップデートです。

**今回の発表のポイント:**
- Spotify・Uber・Instacartなど15種のパーソナルアプリと連携
- PKCE + ephemeralトークンによる安全な認証設計
- 購入・予約前の必須ユーザー確認でAIの自律暴走を防止
- 連携データはモデル学習に不使用

AIが単なる「チャットbot」から「実際にタスクを完遂するアシスタント」へと進化する流れの中で、Connectorsは重要なインターフェースレイヤーになると考えられます。

## 参考リンク

- [New connectors in Claude for everyday life | Claude Blog](https://claude.com/blog/connectors-for-everyday-life) — 公式発表（2026-04-23、米国時間）
- [Use connectors to extend Claude's capabilities | Claude Help Center](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities) — コネクター利用ガイド
- [Claude API Documentation | Anthropic](https://platform.claude.com/docs/en/home) — 開発者向けドキュメント
- [Claude can now connect to lifestyle apps like Spotify, Instacart and AllTrails | Engadget](https://www.engadget.com/ai/claude-can-now-connect-to-lifestyle-apps-like-spotify-instacart-and-alltrails-225510552.html)
- [Anthropic Launches New App Connectors For Claude Users | Dataconomy](https://dataconomy.com/2026/04/24/anthropic-launches-new-app-connectors-for-claude-users/)
