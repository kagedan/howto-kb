---
id: "2026-03-25-スマホからmacを操作claude-dispatchを使ってみた-01"
title: "スマホからMacを操作！Claude Dispatchを使ってみた"
url: "https://qiita.com/wozisagi/items/dce4fbe55bcb1fa3b850"
source: "qiita"
category: "cowork"
tags: ["cowork", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## はじめに

2026年3月23日、Anthropicが **Claude Dispatch** をリリースしました。  
「スマートフォンからClaudeに指示を出すと、自宅のMacが勝手に作業してくれる」という機能です。Claudeのリリースを確認したときに、OpenClawみたいでセットアップも簡単そうと思ったので実際にやってみました。

## 環境

| 項目 | バージョン・内容 |
| --- | --- |
| OS（デスクトップ） | macOS |
| OS（モバイル） | iOS |
| 利用サービス | Claude Cowork（Claude Pro プラン） |
| 確認時点 | 2026年3月23日 |

Claude Dispatch は **Claude Pro（$20/月）以上のプランが必要**です。無料プランでは利用できません。

## Claude Dispatch とは

まず軽く概要を整理します。

Claude Dispatch は、Anthropicの **Claude Cowork**（永続的なAIワークスペース）に追加された機能で、「スマートフォンから自分のMacにタスクを遠隔で割り当てられる」仕組みです。

### 通常のClaudeチャットとの違い

| 項目 | 通常のClaudeチャット | Claude Dispatch |
| --- | --- | --- |
| セッションモデル | 会話ごとにリセット | **永続的な1本のスレッド** |
| 実行場所 | Anthropicのクラウド | **自分のMac上（ローカル）** |
| 操作スタイル | リアルタイム・同期 | **非同期（投げて離脱OK）** |
| デバイス要件 | なし | **Mac + スマートフォンのペアリングが必要** |
| ファイルアクセス | なし | **ローカルファイルの読み書き可能** |
| PC操作 | なし | **クリック・入力・アプリ操作まで可能** |

「ファイルはクラウドに送らず、自分のMacがそのまま動く」という点がセキュリティ面でも興味深いです。

---

## やってみた

### 1. セットアップ（QRコードでペアリング）

セットアップは驚くほど簡単です。

**必要なもの**

* Claude Desktop アプリ（最新版）
* Claude モバイルアプリ（iOS / Android、最新版）

**手順**

1. Claude Desktop を最新版にアップデート
2. Claude Desktop を開き、左メニューの **「Cowork」** タブへ移動
3. 左パネルの **「Dispatch」** をクリック
4. **「Get started」** をクリック
5. ファイルアクセス許可と「Macをスリープさせない」の設定を確認
6. 表示された **QRコードをスマートフォンのClaudeアプリでスキャン**

これだけでペアリング完了です。拍子抜けするくらいシンプルでした。

**Macの電源とClaudeアプリは起動し続ける必要があります。**  
外出先から使いたい場合は、Mac をスリープさせない設定にしておきましょう。

---

### 2. スマホからタスクを投げてみる

スマホの Claude アプリを開くとサイドバーに **「Dispatch」** が追加されています。  
ここから自然言語でタスクを送るだけです。  
[![IMG_9231.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2752598%2F037c1e08-dee1-41aa-a86d-d5b965abcc74.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e92bcf7017b06b4b5477d05171c7de09)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2752598%2F037c1e08-dee1-41aa-a86d-d5b965abcc74.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e92bcf7017b06b4b5477d05171c7de09)

接続できたかを確認します。  
**こんにちは**と入力します。返信が返ってきました。  
次に**Testフォルダ**を閲覧できるかを確認します。私がフォルダを作るときにスペルをミスったのでスムーズに検索できませんでしたが、Claudeさんは見つけてくれました。  
[![20260325_ディスパッチ_テストフォルダ内容の確認.PNG](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2752598%2Fd21fa7f9-a67c-4509-90f8-9f2af36ff981.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7a2454795298c727cf07df91a1b4ae24)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2752598%2Fd21fa7f9-a67c-4509-90f8-9f2af36ff981.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7a2454795298c727cf07df91a1b4ae24)

フォルダにあるファイルを確認してもらいます。  
優秀ですね。ちゃんと確認することができました。  
[![20260325_ディスパッチ_テストフォルダのファイル一覧.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2752598%2F5d032dab-4162-4e05-8d17-b1858f91d788.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ff481d68abf4b06b17423dc491bd2a47)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2752598%2F5d032dab-4162-4e05-8d17-b1858f91d788.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ff481d68abf4b06b17423dc491bd2a47)

自分のPCはGoogleDriveと共有するフォルダがあるのでそこにファイルを配置してもらい、自分のiPhoneからファイルを閲覧できるようにしてもらいます。  
**mvコマンド**は許可されず、どうしてもできませんでした。代わりに**cpコマンド**でGoogleDrive経由で共有してもらいました。  
[![20260325_ディスパッチ_レポートログのコピー完了.PNG](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2752598%2Fc5934915-5b1a-4b26-8102-4774816a2590.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=230eb9db74432a02904b087e38cc7c18)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2752598%2Fc5934915-5b1a-4b26-8102-4774816a2590.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=230eb9db74432a02904b087e38cc7c18)

---

### 3. タスクの流れを確認する

実際の動きとしては、以下のような流れになっています。

```
[スマホ] タスク送信
    ↓（暗号化通信）
[Mac] Claude Desktop がタスクを受信
    ↓
[Mac] Claude がローカルで実行（アプリ操作・ファイルアクセス等）
    ↓
[スマホ] 結果が通知で届く
```

## Claude Dispatch vs OpenClaw：類似ツールとの比較

Claude Dispatch と同様に「スマホ・チャットから自PCにタスクを割り当てる」用途で話題になっているOSSツールに **OpenClaw** があります。  
どちらを使うべきか迷う人も多いと思うので、主要な観点で比較します。

| 項目 | Claude Dispatch | OpenClaw |
| --- | --- | --- |
| **費用** | $20+/月（Pro以上必須） | 無料（API実費のみ） |
| **セットアップ** | 数分・アプリベース | ターミナル操作が必要 |
| **対応プラットフォーム** | macOS・Windows x64のみ | macOS・Windows・Linux |
| **チャット連携** | Claude モバイルアプリのみ | WhatsApp・Telegram・Slackなど |
| **プライバシー** | データがAnthropicを経由 | 完全にローカルで動作 |
| **セキュリティ** | サンドボックスVM・エンタープライズ管理 | サンドボックスなし・ユーザー責任 |
| **AIモデル** | Claudeのみ | Claude・GPT・Gemini・ローカルモデルなど |

### 選び方の目安

**Claude Dispatch が向いている人**

* すでにClaude Proを契約している
* セキュリティ・サンドボックス管理を公式に任せたい
* セットアップの手間を最小化したい

**OpenClaw が向いている人**

* コストを抑えたい（API従量課金のみで済む）
* LinuxやARM Windowsなど幅広いOSで動かしたい
* WhatsApp・TelegramなどのチャットアプリからAIを操作したい
* データをAnthropicサーバーに送りたくない（完全ローカル志向）

OpenClaw はOSSのためカスタマイズ性が高い反面、サンドボックス保護がないため、実行するコマンドの責任はユーザー自身が負います。

---

## おわりに

Claude Dispatch を使うことで「スマホから指示を投げて、ローカルPCを操作する」ということが実現できました。シンプルなタスクは十分実用的で、通勤時間の使い方が変わりそうです。いつでも仕事ができる状態になってしまいますが・・・

ただし、まだリサーチプレビュー段階であり複雑なタスクの成功率は高くありません。**ファイルの削除・変更など取り返しのつかない操作は慎重に**使うことが推奨されています。

Coworkは容量を食いますので気をつけてください。私は途中で制限に引っかかってしまったので土曜日のリセットを待ちます。

## 参考
