---
id: "2026-04-22-備忘録salesforce-hosted-mcp-server-を使い始める-claude-desk-01"
title: "【備忘録】Salesforce Hosted MCP Server を使い始める ― Claude Desktop から sobject-reads まで繋ぐまでの流れ"
url: "https://qiita.com/Tadataka_Takahashi/items/5fc44899426563c03966"
source: "qiita"
category: "claude-code"
tags: ["MCP", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

## はじめに

[![fig_intro.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F62bc5fda-176b-4778-be34-f6524a147b3b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2ebff9f1463640eae9b2e39afa1feda5)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F62bc5fda-176b-4778-be34-f6524a147b3b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2ebff9f1463640eae9b2e39afa1feda5)

Salesforce が提供する **Hosted MCP Server** の初期セットアップ方法について、公式ブログを読みながら自分なりに整理した備忘録です。

MCP（Model Context Protocol）対応のクライアント（Claude / ChatGPT / Cursor など）から、Salesforce のデータや自動化機能に接続できるようになるという機能で、一度 Salesforce 側で設定すれば、複数の AI クライアントから同じサーバーを使い回せる点が特徴だと理解しました。

本記事では、次の順で整理します。

* Hosted MCP Server がどういう位置付けの機能か
* 設定の全体フロー
* 外部クライアントアプリケーションの作り方（OAuth 周りのハマりどころ）
* MCP Server の有効化と動作確認
* カスタム MCP サーバーで Flow / Apex を公開する話
* 実際に接続を試すときに踏みそうな、GitHub 報告の既知の事象（Claude 連携）

**機能のステータスについて（2026年4月時点）**

本機能は **TDX 2026（2026年4月15日）で Enterprise Edition 以上向けに GA（正式リリース）** されました。あわせて、Developer Edition でも無料で利用できるようになっています（公式 GitHub [`forcedotcom/mcp-hosted`](https://github.com/forcedotcom/mcp-hosted) でも「Hosted MCP servers are now generally available (GA)」と明記）。

ただし、Salesforce Help や Spring '26 Release Notes など **一部のドキュメントでは依然として「Beta」表記が残っている** のが現状で、画面や仕様の細部が今後変わる可能性はあります。実際に設定を行う際は、必ず公式ドキュメントで最新仕様をご確認ください。本記事は個人の整理メモです。

---

## Salesforce Hosted MCP Server とは何か

MCP（Model Context Protocol）は、AI アプリケーションと外部システムを繋ぐためのオープン規格です。各 AI アプリ・エージェントごとに独自のコネクタを作らなくても、MCP 経由で標準的に繋げる、というのが狙いです。

Hosted MCP Server は、この MCP サーバーを Salesforce 自身が提供・ホストする形態で、Claude Desktop、ChatGPT、Cursor、あるいは独自エージェントなど、MCP に対応したクライアントから Salesforce の各種機能（レコード参照、レコード作成・更新、Flow、Apex、Data 360、Prompt Template など）に接続できるようになります。

[![fig0_overview.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F945d69c5-b1ee-4df3-b077-69c3e5d14367.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1a0ccd933437a6d60499725be76bbebe)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F945d69c5-b1ee-4df3-b077-69c3e5d14367.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1a0ccd933437a6d60499725be76bbebe)

ポイントだと感じた点を挙げると、

* **接続の一本化**: AIアプリごとに API ラッパーを作り込む必要がなく、一度サーバーを設定すれば複数クライアントで再利用できる
* **共有ルール・FLS を尊重**: 連携時に使うユーザーの権限の範囲内でしか動作しない（フィールドレベルセキュリティや共有ルールが効く）
* **OAuth 2.0 / PKCE ベース**: ユーザーごとの認証で、エージェントはそのユーザーの権限で動く

従来のように「生成 AI から Salesforce を触るため専用の API ラッパー」を作る必要がなく、MCP という共通プロトコルに寄せることで設定・運用が共通化される、と捉えると理解しやすそうです。

---

## 設定の全体フロー

設定は大きく分けて 3 ステップです。

[![fig1_setup_flow.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F9cd5a8eb-1f11-4692-9286-3d77be2f26be.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0a4db68277583003841e18cc6dd162aa)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F9cd5a8eb-1f11-4692-9286-3d77be2f26be.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0a4db68277583003841e18cc6dd162aa)

1. **Salesforce 側**: 外部クライアントアプリケーションを作成（OAuth の器を作る）
2. **Salesforce 側**: 使いたい MCP Server（例: `sobject-reads`）を有効化
3. **クライアント側**: コネクタとして接続を追加

Salesforce 側の 1, 2 は組織で一度きりの設定、3 は利用するクライアントを追加するたびに行う、という構造です。

以降のセクションで、それぞれの手順を見ていきます（今回は Developer Edition ＆システム管理者前提）。

---

## ステップ1: 外部クライアントアプリケーションの作成

MCP クライアントからのアクセスを Salesforce で認証・認可できるように、まず **外部クライアントアプリケーション** を作成します。

### 設定場所

```
設定 -> アプリケーション -> 外部クライアントアプリケーション -> 外部クライアントアプリケーションマネージャー
-> 「新規外部クライアントアプリケーション」
```

### 押さえておきたい設定項目

ここがこの機能で一番つまずきやすいところだと思うので、4 つのポイントを図にまとめました。

[![fig2_oauth_scope.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Fe6465ac4-ad84-4ec5-8632-3758e6795d7e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b3f1eb8808b9cb56a830b0efc9318ccd)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Fe6465ac4-ad84-4ec5-8632-3758e6795d7e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b3f1eb8808b9cb56a830b0efc9318ccd)

👉 **コールバック URL**

クライアントごとに指定が異なります。Claude Desktop で使う場合は以下を設定します。

```
https://claude.ai/api/mcp/auth_callback
```

使う側のクライアントの公式ドキュメントで最新値を確認するのが安全です。

👉 **OAuth 範囲（Scope）**

以下の 2 つを選択します。

* `refresh_token, offline_access`（いつでも要求を実行）
* `mcp_api`（Salesforce でホストされている MCP サーバーにアクセス）

`mcp_api` スコープが入っていないと、OAuth のトークン発行自体は通っても、その後の MCP 呼び出しで弾かれる原因になります。選択漏れに注意です。

👉 **セキュリティ**

以下の 2 つのみを有効にする構成が公式ブログで紹介されている構成です。

* サポートされる認証フローに PKCE 拡張を要求
* 指名ユーザーの JWT ベースのアクセストークンを発行

👉 **コンシューマー鍵（Client ID）**

作成後、「設定」タブ → OAuth 設定のアコーディオン → 「コンシューマー鍵と秘密」ボタンから取得します。メールで送られる確認コードの入力が必要なので、管理者メールを受け取れる状態で作業するとスムーズです。

この **コンシューマー鍵** は、後のクライアント側設定で使います。

---

## ステップ2: MCP Server の有効化

外部クライアントアプリを作ったら、次に使いたい MCP サーバーを有効化します。

### 設定場所

```
設定 -> インテグレーション -> API カタログ -> MCP サーバー
```

提供機能ごとにサーバーが分かれています。今回は公式ブログでも例になっている `sobject-reads`（レコード参照系）を有効化します。

* 一覧から `sobject-reads` のリンクを押す
* 画面右上の「有効化」ボタンを押す
* サーバー状態が「稼働中」になれば OK

「ツール」タブから、この MCP サーバーが提供しているツール（機能）の一覧を確認できます。このタブで出てくる一覧が、AI クライアントから呼べる関数群のイメージだと捉えておくとよさそうです。

---

## ステップ3: クライアント側（Claude Desktop）での接続設定

ここからは Claude Desktop 側の操作です。

ここからは他社プロダクト側の設定になります。画面表示や操作パスは予告なく変更になる場合があるので、実際に試す際は Claude 側の最新ドキュメントもあわせてご確認ください。

大まかな流れは、

1. カスタマイズ → コネクタ → 「＋（追加）」 → 「カスタムコネクタを追加」
2. 必要事項を入力
   * コネクタ名: 任意
   * URL: Salesforce 設定画面にある MCP サーバーの **Server URL**
   * 詳細設定を開き、OAuth の **クライアント ID** にステップ1で取得したコンシューマー鍵を設定
3. 「連携」ボタンを押す
4. ブラウザが開くので連携に使う Salesforce ユーザーを選び、許可
5. デスクトップアプリに戻って、ツール一覧が見えていれば接続成功

`sobject-reads` を有効化してある場合、接続後に取引先参照などのツールがクライアント側から見えるようになります。

### 動作確認

Claude Desktop で次のように話しかけます。

> こんにちは！Salesforce にアクセスして、取引先の一覧を見せて

MCP 経由でツール呼び出しが走り、取引先の一覧が返ってくれば成功です。取引先名の部分一致検索など、多少聞き方を変えても意図を汲んで対応してくれることが、公式ブログの例でも示されています。

---

## カスタム MCP サーバーという面白ポイント

ここが個人的にこの機能の面白いところだと感じた部分です。

Salesforce の Hosted MCP Server は、事前提供のサーバー（`sobject-reads` など）だけでなく、**カスタムの MCP サーバー** を作成し、**Flow や Apex をツールとして登録** することができます。登録後は、ノーコードで AI クライアントから自然言語で呼び出せます。

[![fig3_custom_mcp.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F47624bd1-529f-471d-8041-7cb0cb4b4560.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=62d420c94085c5345b41fad2831b6f5a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F47624bd1-529f-471d-8041-7cb0cb4b4560.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=62d420c94085c5345b41fad2831b6f5a)

つまり、

* 既存の承認 Flow
* Invocable Apex や `@AuraEnabled` メソッド
* Apex REST メソッド
* Named Query（SOQL テンプレート）
* Prompt Builder の Prompt Template

といった「すでに業務で使っている資産」を、追加のコネクタ実装なしで MCP ツールとして公開できる、という位置付けです。

エージェント基盤を自前で作ってきた人にとっては、「毎回ツールアダプタを書かずに済む」という観点で、運用上のメリットが大きそうだと感じました。

---

## GitHub で報告されている既知の事象（備忘）

今回自分で全パターンを踏んだわけではないのですが、導入前の下調べとして GitHub Issue を眺めていて見つけた事象を、今後接続トラブルに遭遇したときの手がかりとしてメモしておきます。

2026年4月時点で、Anthropic 側リポジトリ [`anthropics/claude-ai-mcp`](https://github.com/anthropics/claude-ai-mcp) の Issue に以下のような報告が上がっていました。

* Claude の Custom MCP Connector から Salesforce Hosted MCP Server（`sobject-reads`）に接続しようとすると、
* OAuth のトークン発行自体は成功し、Salesforce 側でも接続済みとして記録されるが、
* その後の MCP エンドポイント呼び出しで「Authorization with the MCP server failed」と返ってくる

というパターンです（Issue #171 が Sandbox org での報告、Issue #184 が Production Enterprise org での報告）。Anthropic 側で追跡中である旨のコメントもついていました。

もしこの症状に遭遇した場合の切り分けとしては、

* まず Salesforce 側の `OAuth 使用状況` で接続ユーザーにトークンが発行されているかを確認
* その上で、スコープに `mcp_api` が入っているかを再確認
* 発行されているのに呼び出しが失敗する場合、クライアント側の既知バグの可能性もあるので、Anthropic / Salesforce それぞれの Issue トラッカーを見て状況を確認

という順で見ていくと整理しやすそうです。

👉 本番組織でいきなり試すよりも、まずは **Developer Edition や Sandbox で挙動を確認してから組織展開** するのが安全そうだと感じました。

---

## まとめ

[![fig_summary.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Fa4be803b-f1f7-47c5-b63d-491979d3c947.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7a4ff57d93888ffbcc02d324a436e365)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Fa4be803b-f1f7-47c5-b63d-491979d3c947.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7a4ff57d93888ffbcc02d324a436e365)

今回の整理で手元に残したいのは以下の点です。

* Salesforce Hosted MCP Server は、AI クライアントと Salesforce を繋ぐ共通プロトコル（MCP）の Salesforce 公式実装
* **2026年4月の TDX 2026 で Enterprise Edition 以上向けに GA**、Developer Edition でも無料で利用可能に（ただし Help / Release Notes 側には Beta 表記が残るドキュメントもある）
* セットアップは「外部クライアントアプリ作成 → MCP Server 有効化 → クライアント側設定」の 3 ステップ
* OAuth スコープには `mcp_api` が必須、PKCE と JWT を有効化しておく
* `sobject-reads` などの既製サーバーに加え、Flow / Apex をツール公開できる **カスタム MCP サーバー** が強み
* Claude 連携の接続エラーが GitHub Issue で報告されているので、まずは Developer Edition / Sandbox で検証すると安心

一言でまとめると、**「AI クライアントごとに API ラッパーを作ってきた世界から、MCP に寄せて運用を共通化していく世界への橋渡し」** として捉えると、この機能の位置付けが腹落ちしやすそうです。

---

## 参考（公式情報）

※最新仕様は必ず公式ドキュメントを基準にご確認ください。

※Web上の情報は変更・削除されることがあるため、将来的にリンク切れとなる可能性があります。
