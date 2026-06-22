---
id: "2026-06-21-claude-desktop-on-amazon-bedrock-からm365に接続してみた組み込み-01"
title: "Claude Desktop on Amazon Bedrock からM365に接続してみた（組み込みサーバー/ローカルコネクター）"
url: "https://zenn.dev/aws_japan/articles/claude-desktop-bedrock-m365-local-connector"
source: "zenn"
category: "cowork"
tags: ["MCP", "API", "cowork", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは！AWS でソリューションアーキテクトをしている町田です。

今回は、Claude Desktop (Cowork) から Microsoft 365 のデータ（Outlook メール・カレンダー、OneDrive、SharePoint、Teams）にアクセスするための **ローカルコネクタ** を Windows 環境でセットアップしてみました。

ローカルコネクタを設定することで、Claude Desktop の会話内から「先週のメールを検索して」「来週のカレンダーを確認して」「OneDrive にあるファイルの内容を教えて」といった指示が可能になります。

## ローカルコネクタとは

Claude Desktop には Microsoft 365 サーバーのビルトインコピーが含まれています。ローカルコネクタを選択すると、各ユーザーのデバイス上でローカルプロセスとしてサーバーが動作し、**デバイスから直接 Microsoft Graph を呼び出します**。

M365 コネクタにはリモートコネクタとローカルコネクタの 2 種類がありますが、以下の理由から今回はローカルコネクタを採用しました。

| 項目 | リモートコネクタ | ローカルコネクタ（今回） |
| --- | --- | --- |
| **データ経路** | Anthropic インフラを経由（保存なし） | **デバイスから直接 Microsoft Graph** |
| **Anthropic へのアローリスト申請** | 必要（2〜3 営業日待ち） | **不要** ✅ |
| **アプリ登録** | 2 つ必要（自アプリ + Anthropic コネクタアプリ同意） | **1 つのみ** |
| **ネットワーク要件** | login.microsoftonline.com + microsoft365.mcp.claude.com | login.microsoftonline.com + graph.microsoft.com |
| **Claude Desktop での選択** | リモートテンプレート → Microsoft 365 | **組み込みサーバー → Microsoft 365** |

!

**ローカルコネクタの利点**

* ✅ アローリスト申請不要で**すぐに使い始められる**
* ✅ M365 データが **Anthropic のインフラを経由しない**
* ✅ セットアップが**シンプル**（アプリ登録 1 つだけ）

## 前提条件

* Claude Desktop がインストール済みで、Amazon Bedrock 経由のサードパーティ推論が設定済み
* Microsoft Entra テナントの **グローバル管理者** または **クラウドアプリケーション管理者** の権限

## セットアップの全体像

セットアップは以下の 3 ステップで完了します。

今回のセットアップは Entra テナント管理者と Claude Desktop 利用者で役割が分かれます。

**Entra テナント管理者が行うこと：**

* パブリッククライアントアプリの登録
* Microsoft Graph の委任アクセス許可の追加と管理者同意
* Client ID / Tenant ID を利用者に共有

**Claude Desktop 利用者が行うこと：**

* Claude Desktop でのコネクタ設定
* M365のサインイン

## ステップ 1: Entra でパブリッククライアントアプリを登録する

### 1.1 新規アプリ登録

1. [Entra 管理センター](https://entra.microsoft.com) を開きます
2. **アプリの登録** → **新規登録** を選択します
3. 以下のように設定します：
   * **名前**: `Claude Desktop M365 Local`（任意の名前で OK）
   * **サポートされるアカウントの種類**: 「**シングルテナントのみ**」
   * **リダイレクト URL** :
     + **パブリック クライアント/ネイティブ（モバイルとデスクトップ）** を選択します
     + `http://localhost` を入力します
4. **「登録」** を選択します

![](https://static.zenn.studio/user-upload/deployed-images/f4913cc0f77af60aa0f967a5.png?sha=b1a1bebdf0f87d27c8c51383c355155f9fbf94a2)

5. 概要ページに表示される以下をメモします：

* **アプリケーション (クライアント) ID**
* **ディレクトリ (テナント) ID**  
  ![](https://static.zenn.studio/user-upload/deployed-images/cf44be10366d200075277f6e.png?sha=b7bf9cdb7ff8e0508e3cd954470a4ed9976dfa85)

### 1.2 Microsoft Graph の委任アクセス許可を追加

1. **API のアクセス許可** → **アクセス許可の追加** を選択します

![](https://static.zenn.studio/user-upload/deployed-images/8e49fa467de42d2d9be39fa5.png?sha=d90c849f2a455732b42a838b1cceeb4866b82dff)

2. **Microsoft Graph** → **委任されたアクセス許可** を選択します

![](https://static.zenn.studio/user-upload/deployed-images/8f3b9482db1194538b15c47b.png?sha=cc39327e5b825098dab2ffaa0c2957810a37c4d9)  
![](https://static.zenn.studio/user-upload/deployed-images/74c3fd825347270c44598fb0.png?sha=b1443b12f8cf7ab3555cc4b977fb6856b524461f)

3. 以下のスコープをすべて追加します：

| スコープ | 目的 |
| --- | --- |
| User.Read | サインイン済みユーザーのプロフィール読み取り |
| Mail.Read | メール読み取り |
| Mail.Read.Shared | 共有メールボックスのメール読み取り |
| Calendars.Read | カレンダーイベント読み取り |
| Calendars.Read.Shared | 共有カレンダーのイベント読み取り |
| Files.Read.All | OneDrive・SharePoint のファイル読み取り |
| Sites.Read.All | SharePoint サイトコンテンツ読み取り |
| Chat.Read | Teams チャットメッセージ読み取り |
| OnlineMeetings.Read | オンライン会議の読み取り |
| offline\_access | トークンの自動更新（再サインイン不要） |

4. 上記のスコープを検索してチェックボックスをクリックした後に、**「アクセス許可の追加」** を選択します。

![](https://static.zenn.studio/user-upload/deployed-images/b6d97de6d9bd2b5d35eccbe8.png?sha=f316fc740ee3e4dbb12ae8c2d79ef6f40fcff29d)

5. アクセス許可が追加されましたので、次に進みます。

![](https://static.zenn.studio/user-upload/deployed-images/29a4c6723c70b333c26be08b.png?sha=30942311b33899dd65f1028594ba592523d7f4d6)

### 1.3 管理者の同意を付与

1. **「{組織名} に管理者の同意を与えます」** をクリックします

![](https://static.zenn.studio/user-upload/deployed-images/5a9e5fe9a5e23e76713a6797.png?sha=aef0c9e63309964bc0c9a8738a989b7c47e194f2)

2. 「はい」をクリックします

![](https://static.zenn.studio/user-upload/deployed-images/225b9a6f5e44cef80838a00b.png?sha=a707b6c6764e5e5ed7252116d3dd630f462e0f09)

3. 各スコープの状態が **「{組織名} に付与」** ✅ になっていることを確認します

![](https://static.zenn.studio/user-upload/deployed-images/81be00ddcb0a8262e6f23cd1.png?sha=d6645582b20a843b205b057fd2ce52120f0638d8)

## ステップ 2: Claude Desktop を設定する

ここからは Claude Desktop 利用者の作業です。

1. Claude Desktop を開き、**開発** → **サードパーティ推論の設定** → **コネクタと拡張機能** を選択します。
2. **「+ サーバーを追加」** を選択し、ドロップダウンから **組み込みサーバーグループの 「Microsoft 365」** を選択します。

![](https://static.zenn.studio/user-upload/deployed-images/151644f88b72bd0f0bc7411b.png?sha=378b2362e1f8fd81572e47e839f3455b90cc42c4)

3. 以下の値を入力します：

| フィールド | 値 |
| --- | --- |
| テナントID | 管理者から共有されたディレクトリ (テナント) ID |
| クライアントID | 管理者から共有されたアプリケーション (クライアント) ID |
|  |  |

4. **「この接続をテスト」** をクリックして、サーバーが起動しツール一覧が表示されることを確認します。
5. テスト結果が接続完了となっていることを確認します。

![](https://static.zenn.studio/user-upload/deployed-images/8eec5fa9c970a97f35698737.png?sha=5f0a4a8bee0549aa73df18b1cbafcd903042405d)  
![](https://static.zenn.studio/user-upload/deployed-images/aee05bda896355789a14e92a.png?sha=9352afd30717e82b15a7d5b2de4184c4f1625abb)

6. **「変更を適用」** をクリックします。  
   ![](https://static.zenn.studio/user-upload/deployed-images/5a6f2dfaebf43fe81a8a8542.png?sha=5082d6afed0bfc171a4d5bf3f3695531a3c6547d)
7. **「今すぐ再起動」** をクリックします。  
   ![](https://static.zenn.studio/user-upload/deployed-images/0c4e637dd6beda89afee440d.png?sha=585b753e8516cb9f4b0dffc9d363baa7da6e1ea2)

## ステップ 3: 動作確認

### カレンダーの予定確認

1. 以下を Claude Desktop cowork に入力します。

2. 「一度だけ許可」をクリックします。

![](https://static.zenn.studio/user-upload/deployed-images/06296d104c29fbb69d24659a.png?sha=03629301a7675ffb12a4ae4b767101b105db9c9a)

3. M365 の認証アカウントを選択します。

![](https://static.zenn.studio/user-upload/deployed-images/3ce8484ce86aa500e8ff5aee.png?sha=9600b347fa012016f303ccb2bf7be087d56a7042)

4. Auth code was successfully acquired." と表示されることを確認する。

![](https://static.zenn.studio/user-upload/deployed-images/189be4a4e2870de34bcf0aec.png?sha=6941e2b877107ef68d4dc68b4b48f892069383e2)

5. Claude Desktop の画面ではM365からカレンダー情報を取得できていることが分かる。

![](https://static.zenn.studio/user-upload/deployed-images/af340e3b498a88a4319d5f3c.png?sha=3b73ef68e8fc6059dc5a775b00cc72a16472c314)

6. Outlook に予定を追加して確認してみる

![](https://static.zenn.studio/user-upload/deployed-images/ec4e8aadcbe5faee7e9cef89.png?sha=0a71eff75de7e43184768497c35a7306d20e9edf)

7. 再度カレンダー情報を取得してみる

![](https://static.zenn.studio/user-upload/deployed-images/65b852695451b59f4e911ccf.png?sha=894e09f93abe27050e8127d7077137ed134b90eb)

8. カレンダー情報を取得できたがタイムゾーンがずれている

![](https://static.zenn.studio/user-upload/deployed-images/82d37312ad7e752945d7a08b.png?sha=8e79a65f84a9e67d0218ec6d4e10da2a6c0693c8)

9. プロンプトで指摘したら直った

![](https://static.zenn.studio/user-upload/deployed-images/f966dcb6f6ab5f5a0ea22722.png?sha=41a68265c4398d1991412e447a39ca9be8151f01)

### 複数のリソースから情報を取得する

sharepoint, onedrive, outlook, teams には以下のリソースがある状態で、以下のプロンプトを実行してみます。

1. 以下のプロンプトを実行します。

```
来週月曜にテストカンパニー社との定例ミーティングがあります。
準備のため、以下を横断的に調べてブリーフィングメモを作成してください：

1. テストカンパニーに関する直近のメール（商談の進捗、先方からの質問）
2. Teamsチャットでの社内議論（チーム内の方針・懸念点）
3. SharePoint/OneDriveにある関連ドキュメント一覧

これらを統合して、以下の構成でまとめてください：
- 案件サマリー（現在のフェーズ・主要論点）
- 先方からの未回答事項
- 社内で合意済みの方針
- 次回MTGで準備すべき資料リスト
```

![](https://static.zenn.studio/user-upload/deployed-images/84f6ecdc3eaabae5aa3f65fb.png?sha=e5cd48a048bfe72ba4c60eac4e0c539abcc3d331)

2. 何度か許可を求められるので、**「一度だけ許可」** をクリックします。  
   ![](https://static.zenn.studio/user-upload/deployed-images/5efcadaadcdcb30a7ccc8319.png?sha=acfdc1ac23878e2571ee1387a93bd7cb0688d367)
3. M365上の複数リソースにアクセスできて、回答を得られました。  
   ![](https://static.zenn.studio/user-upload/deployed-images/c8785524a9883f411f8b6f7a.png?sha=ae478154e526bd84c487969014684ffae3bba9d3)
4. Sources: のリンクをクリックすると M365 のデータを確認することができます。  
   ![](https://static.zenn.studio/user-upload/deployed-images/bee2d70a1b3144d36c97e88d.png?sha=eceebd1b6c3e8593269b86c5b24a79861196ee3b)  
   ![](https://static.zenn.studio/user-upload/deployed-images/410d43c9a76a7b50b03a21a7.png?sha=4a3376f6398b760a31f6856a0c7e27ee9a2bc4bb)

また、ブリーフィングメモまで作ってくれています。  
![](https://static.zenn.studio/user-upload/deployed-images/aab34d0cf69b5c9cd0d6f04b.png?sha=67885911ce1a90d2e24d6f09a2caafa5ce2e3b12)

以上のようにM365からデータを取得して業務効率化を図ることができました！

## 利用可能なツール

M365 コネクタを接続すると、以下のツールが Claude Desktop から利用可能になります：

| ツール | 機能 |
| --- | --- |
| outlook\_email\_search | Outlook メールの検索 |
| outlook\_calendar\_search | カレンダーイベントの検索 |
| find\_meeting\_availability | 空き時間の検索 |
| chat\_message\_search | Teams チャットの検索（1:1 およびグループ） |
| sharepoint\_search / sharepoint\_folder\_search | SharePoint・OneDrive の検索 |
| read\_resource | 特定のアイテム（メール、イベント、ファイル等）の取得 |

![](https://static.zenn.studio/user-upload/deployed-images/4a3b65e9fd82f5508dd23eaa.png?sha=509559201b3351be92623f9ac4f0d58bc411588e)

## ネットワーク要件 (Anthropic 公式ドキュメントから抜粋)

ローカルコネクタはデバイスから直接 Microsoft に呼び出しを行うため、以下のホストへの HTTPS アウトバウンドアクセスが必要です：

| ホスト | 目的 |
| --- | --- |
| login.microsoftonline.com | Microsoft Entra サインイン |
| graph.microsoft.com | Microsoft Graph データ API |

## トラブルシューティング (Anthropic 公式ドキュメントから抜粋)

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| 「サーバーを追加」に「組み込みサーバー」の Microsoft 365 がない | Claude Desktop のバージョンが古い | Claude Desktop を最新版にアップグレード |
| コネクタが設定画面に表示されない | 設定パース時にエントリが拒否された | アプリのメインログで原因を確認 |
| AADSTS50011 リダイレクトミスマッチ | `http://localhost` が未登録、または「Web」の下に登録されている | ステップ 1.2 で「モバイルおよびデスクトップ」として追加されているか確認 |
| AADSTS65001 管理者同意が必要 | Graph 委任アクセス許可に管理者同意が付与されていない | ステップ 1.4 を再確認 |
| ツールがアクセス許可エラー / Graph 403 を返す | 必要なスコープがアプリ登録で同意されていない | 必要な Graph スコープを追加し管理者同意を付与 |
| サーバーへの接続に失敗しました | ネットワーク的に graph.microsoft.com に到達できない | プロキシ・ファイアウォール設定を確認 |

**ログファイルの場所（Windows）:**

```
%LOCALAPPDATA%\Claude-3p\logs\mcp-server-office365-builtin.log
```

設定パースや接続ライフサイクルのメッセージは同じディレクトリの `main.log` に出力されます。

## まとめ

Claude Desktop (Cowork) の M365 ローカルコネクタを設定することで、会話の中から Outlook メール・カレンダー、OneDrive、SharePoint、Teams のデータにシームレスにアクセスできるようになりました。  
リモートコネクタと違い、**Anthropic へのアローリスト申請が不要** なので、アプリ登録さえ完了すればすぐに利用開始できます。

## 参考リンク
