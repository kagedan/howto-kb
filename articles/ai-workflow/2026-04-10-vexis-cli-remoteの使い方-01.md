---
id: "2026-04-10-vexis-cli-remoteの使い方-01"
title: "VEXIS-CLI-REMOTEの使い方"
url: "https://zenn.dev/ainohogosya/articles/7cff4517639b8b"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

この記事では、AIエージェント「VEXIS-CLI-REMOTE」のセットアップ方法と基本的な使い方を解説します。

本ツールは「VEXIS」「VEXIS-CLI」の派生プロジェクトとして開発されました。前身となる2つのツールは非常にシンプルで使い勝手が良い設計ですが、今回の「VEXIS-CLI-REMOTE」は少しだけ設定手順が複雑です。  
とはいえ、Windows環境へのLinux導入や他の複雑なエージェントツールのセットアップと比較すると、はるかに簡単に導入できます。本記事の手順に沿って、ぜひ環境を構築してみてください。

## VEXIS-CLI-REMOTEとは

VEXIS-CLI-REMOTEは、スマートフォンなどの外部デバイスからWebUI（VEXIS-Chat）を経由して、PC上で稼働する「VEXIS-CLI-2」に指示を出せるリモートAIエージェントです。

これにより、離れた場所からでもPC上でプログラムの作成・テスト実行、各種設定の変更、環境構築などのタスクを、AIに自動で実行させることが可能になります。

## 具体的な使い方

### 1. リポジトリのクローンと起動

まず、GitHubからVEXIS-CLI-REMOTEのソースコードをクローンします。

```
gh repo clone AInohogosya/VEXIS-CLI-REMOTE
```

ディレクトリに移動し、サーバーを起動します。

```
cd VEXIS-CLI-REMOTE
npm run server
```

このコマンドを実行すると、通常であればVEXIS-CLI-REMOTEに必要な環境構築がすべて自動で完了します。  
※もしエラーが発生した場合は、[GitHubのIssue](https://github.com/AInohogosya/VEXIS-CLI-REMOTE/issues)などで報告をお願いします。

起動が完了すると、ターミナルに以下のようなメッセージが表示されます。

```
========================================
   VEXIS Message Forwarder Service
========================================

This service forwards messages from
VEXIS-mail-CLI to VEXIS-CLI-2

Type /login to authenticate or /help for commands.

[Forwarder] Not logged in. Please login first.
```

**このターミナル（コマンドプロンプト）の画面は閉じずに、そのまま起動した状態にしておいてください。**

### 2. VEXIS-Chatでのアカウント登録

次に、PCまたはスマートフォンのブラウザで [VEXIS-Chat](https://ainohogosya.github.io/VEXIS-Chat/) にアクセスします。  
以下のような画面が表示されます。

![](https://static.zenn.studio/user-upload/baa641af380e-20260410.png)

任意のメールアドレスとパスワードを入力し、**「新規登録」**（白いボタン）をタップまたはクリックしてください。

登録が完了すると、以下のようなチャット画面に遷移します。

![](https://static.zenn.studio/user-upload/07377a1f03a9-20260410.png)

ここでメッセージを入力したくなりますが、**一旦ブラウザの操作を止めて、先ほど起動したままにしていたターミナル（コマンドプロンプト）に戻ります。**

### 3. ターミナルでのログインとAI設定

ターミナル上で `/login` コマンドを実行してください。  
先ほどWebサイト（VEXIS-Chat）で登録した「メールアドレス」と「パスワード」を求められるので、入力してEnterを押します。

ログイン成功後、続けて `/setting` コマンドを実行し、AIモデルの設定を行います。  
プロンプトに従って、以下の情報を順番に入力してください。

1. **Provider**: `OpenRouter`, `OpenAI`, `Ollama` を推奨しています。
2. **Model**: 使用するモデル名を入力します。
3. **API Key**: 選択したプロバイダーのAPIキーを入力します。

### 4. リモートからの指示出し

ターミナルでの設定が完了したら、再びブラウザの VEXIS-Chat 画面に戻ります。  
「メッセージを入力」の欄に、VEXIS-CLI-REMOTEへのプロンプトを入力し、送信してください。これでPC側のエージェントがタスクを開始します。

## 最後に

今回は、VEXIS-CLI-REMOTEの基本的なセットアップ方法と使い方を解説しました。  
「ターミナルを実行しているPC」と「ブラウザを開くデバイス（スマホなど）」が別々であっても、インターネット接続さえあれば同様に利用可能です。

必要な環境が揃っていれば、セットアップにかかる所要時間は15分〜30分程度だと思います。ぜひ気軽に使ってみてください！
