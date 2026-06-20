---
id: "2026-06-19-claude-codeのremote-controlでどこからでも作業-01"
title: "Claude Codeの「Remote Control」でどこからでも作業！"
url: "https://qiita.com/hiroakikka/items/0dcab0cb1016fe16e0a7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

# Claude Codeの「Remote Control」でどこからでも作業ができる
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/dcb86dcf-f2b2-4880-b2af-2a1e2d7480a4.png)


Claude Codeに「Remote Control（リモートコントロール）」という機能があります。PCのターミナルで動かしているClaude Codeのセッションを、スマホやブラウザから覗いて操作できるようにする機能です。今回は図を使ってざっくり仕組みとセットアップの流れをまとめます。

## Remote Controlでできること

ポイントは「処理は常にPC上で実行され続ける」ことです。セッションをクラウドに丸ごと引っ越すわけではなく、スマホやブラウザは会話を読んだり指示を送ったりするための「窓」として繋がるだけ、というイメージです。

![diagram1_overview.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/0bb5f7a7-131e-44d5-974f-8a75c7433c53.png)


できることを大きく3つに絞ると、こんな感じです。

1. **ローカル環境をそのまま使える**: ファイル、MCPサーバー、ツール設定などはPCに置かれたまま。クラウドには移動しません。
2. **会話はリアルタイムで同期**: ターミナル・ブラウザ・スマホのどれからでも同じ会話に入って指示を送れます。
3. **切れても自動で復帰**: PCがスリープしたりネットが一瞬切れても、PCが復帰すれば自動で再接続されます。

なお、Remote ControlはPro/Max/Team/Enterpriseプランで利用可能で、APIキー利用時は使えません。Team/Enterpriseプランでは管理者が管理画面で有効化する必要があります（詳細は記事末尾の参考リンクへ）。

## セットアップの流れ

実際の手順は次の5ステップです。
![diagram2_flow.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/252a720c-97a8-4a7a-939b-e8754b14e487.png)


### 1. ターミナルでClaude Codeをインストール

```powershell
Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

```cmd
Windows コマンドプロンプト
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```
![2026-06-19_claude_install.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/1ba2610c-9727-4f85-b8c9-623327861bcd.png)


> 参照: [Quickstart - Claude Code Docs](https://code.claude.com/docs/en/quickstart)

Windowsの場合、インストール直後に `claude` コマンドが見つからないことがあります。これはPATHの設定が原因なので、対処法は後述の「環境変数の設定で気をつけたいポイント」にまとめました。

### 2. Remoteセッションをしたいフォルダで claude と入力

```bash
cd /path/to/your/project
claude
```
![2026-06-19_claude_login.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/9f3775c7-4dc2-443d-917b-f6f13bd7dfdf.png)



好きなテーマを選択。今回はダークモードを選択。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/fcb21755-cac4-4579-90b4-7389268e1228.png)



初回起動時はブラウザでログインを求められます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/10caaa73-91fc-4528-9fee-3a34d93bf4d5.png)


この画面が出ればOK！
![2026-06-19_claude_login_finish.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/1355a17b-2faf-4398-aec9-831deb383444.png)

### 3. remoteのコマンドを打てば完了

セッション内、またはターミナルから次のいずれかを実行するとRemote Controlが有効になります。

```bash
claude remote-control
```


```text
# 既存のセッション内から続きを遠隔操作したい場合（/rc でも同じ）
/remote-control
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/5e9004ed-73dd-4b63-aaba-c3f7eb70b177.png)




実行するとターミナルにセッションURLが表示されます。これで完了です。あとはスマホのClaudeアプリか、ブラウザで claudeを開いてセッション一覧から選ぶだけで接続できます。

![2026-06-19_claude_remote.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/61eb403f-ded2-41e9-9d91-7023f9faf15f.png)


## 環境変数の設定で気をつけたいポイント

Remote Controlが起動しない・有効にならない時は、環境変数を見直すと解決することが多いです。それぞれ「確認方法」と「直し方」をまとめました。

### PATHに 「claude」 の場所が入っているか

Windowsのネイティブインストーラーは `claude.exe` を `C:\Users\<ユーザー名>\.local\bin` に置きますが、ここがPATHに入っていないとインストール直後に警告が出て、ターミナルを開き直しても `claude` コマンドが見つかりません。

以下の方法で環境変数を追加します。

- 「システムの詳細設定」→「環境変数」→ユーザー環境変数の `Path` を選択して「編集」→「新規」で `C:\Users\<ユーザー名>\.local\bin` を追加→OK→ターミナルを開き直す

ユーザー環境変数のPATHを選択する。

![2026-06-19_環境変数.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/5374e8b1-bd2c-4b72-80c8-f3f485ddb2ea.png)


新規で`C:\Users\<ユーザー名>\.local\bin` を追加

![2026-06-19_環境変数_2.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3760884/2cb2a35e-59a1-4218-a87e-8ffa12334d79.png)


## 接続の仕組みについて少し

ローカルのClaude Codeプロセスは外向きのHTTPS通信のみを行い、PC側で受信用のポートを開くことはありません。Remote Controlを開始するとAnthropicのAPIにセッションを登録して待機し、スマホやブラウザから接続するとAPIを経由してメッセージが中継される仕組みです。通信はすべてTLSで保護されています。

## まとめ

Remote Controlを使うと、PCで始めた作業を外出先のスマホや別のブラウザからそのまま続けられます。クラウドにコードを上げる必要がなく、ローカルの環境（ファイルやMCPサーバーなど）をそのまま使えるのが大きな利点です。インストール→対象フォルダで`claude`→`remote-control`系コマンド、という3ステップだけなので、一度試してみる価値はあります。

## 参考

- [Continue local sessions from any device with Remote Control - Claude Code Docs](https://code.claude.com/docs/en/remote-control)
- [Quickstart - Claude Code Docs](https://code.claude.com/docs/en/quickstart)
- [Environment variables - Claude Code Docs](https://code.claude.com/docs/en/env-vars)
- [Claude - iOS App Store](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684)
- [Claude - Android Google Play](https://play.google.com/store/apps/details?id=com.anthropic.claude)
