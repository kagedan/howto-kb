---
id: "2026-07-05-つまずかない順番で-claude-code-を-windows-に入れる完全手順2026年7月版-01"
title: "つまずかない順番で —— Claude Code を Windows に入れる完全手順（2026年7月版）"
url: "https://note.com/zoobenia_0855/n/nc07931bbdafa"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-07-05"
date_collected: "2026-07-05"
summary_by: "auto-rss"
query: ""
---

Macの手順記事に、いちばん多く届いた声が「Windows版はないんですか？」でした。

お待たせしました。**コピペ1行で終わる、Windowsの完全手順**です。

この記事で分かること：Claude CodeをWindowsに入れて、最初の一言を打つまでの全手順（約10分）。

## 始める前に確認する2つだけ

**①Windowsのバージョン**。Windows 10（1809以降）か Windows 11 なら大丈夫です。ここ数年のPCならまず問題ありません。

**②アカウント**。Claude Codeは**有料プラン（Pro以上）が必要**です。無料のClaude.aiプランでは使えません。

先週、無料ユーザーの標準モデルがSonnet 5になって話題でしたが、あれはブラウザ版の話。Claude Codeは「AIに手を動かしてもらう」ための別の道具です。

まだ有料プランにしていない人は、この記事をブックマークして、月初のタイミングで始めるのがおすすめです。

## 手順は3つだけ（コピペ1行）

![](https://assets.st-note.com/img/1783193673-cVCy8xOE21fPSNJupA6asZnr.png?width=1200)

**手順1：PowerShellを開く**

スタートボタンを押して「powershell」と入力し、出てきた「Windows PowerShell」をクリック。

青い（または黒い）画面が開けばOKです。管理者として実行する必要はありません。

**手順2：この1行を貼り付けてEnter**

```
irm https://claude.ai/install.ps1 | iex
```

これだけでインストールが走ります。1〜2分待つと完了します。

**手順3：動作確認してログイン**

いったんPowerShellを**閉じて、開き直して**から、こう打ちます。

```
claude --version
```

数字が出たらインストール成功。続けて claude と打つと、ブラウザが自動で開いてログイン画面になります。

いつものClaudeアカウントでログインすれば、準備完了です。

## つまずくのは、だいたいこの2箇所

![](https://assets.st-note.com/img/1783193715-eB2rDX8MK3y7H0un6zji5mLZ.png?width=1200)

**つまずき①「irm が認識されません」と出る**

それはPowerShellではなく、CMD（コマンドプロンプト）に打っています。

見分け方は簡単で、行の先頭が「PS C:\」で始まっていればPowerShell、「PS」が無ければCMDです。PowerShellを開き直してください。

**つまずき②「claude が見つかりません」と出る**

インストール直後にそのまま打つと、こうなることがあります。

原因はウィンドウが古い状態のままだから。**PowerShellを一度閉じて開き直す**だけで直ります。

**補足：Git for Windowsは入れなくても動きます**。入れるとClaude Codeがより多くの操作をこなせるようになるので、慣れてきたら公式サイト（git-scm.com）から追加すればOKです。

## ターミナルが怖い人には、近道もあります

黒い画面はどうしても無理——という人のために、**デスクトップアプリ版**が出ています。

claude.com/download からダウンロードすれば、ターミナルを一切触らずにClaude Codeが使えます。

ただ、今日の1行コピペができた人なら、ターミナル版のほうが応用が利きます。まずは上の3手順を試してみてください。

## 動いたら、最初にこれを貼ってください

初日に何を頼むかで、Claude Codeの印象は決まります。**何も壊さず、実力だけ分かる1行**を置いておきます。

デスクトップの適当なフォルダで claude を起動して、これをコピペ：

```
このフォルダの中身を一覧して、あなたに任せられそうな作業を3つ提案してください。ファイルの変更はまだしないでください。
```

「変更はまだしないで」の一言がポイントです。安全に様子見しながら、自分の仕事のどこに効くかをAI自身に言わせる。

事業部長時代から変わらない鉄則ですが、新しい道具は「何ができるか」を道具自身に説明させるのが一番早いです。

## 今日やること（3つだけ）

![](https://assets.st-note.com/img/1783193741-cu2P7wmbTBsZlvGI38gtCWdj.png?width=1200)

☐ PowerShellを開く（スタート→「powershell」）

☐ インストールの1行を貼ってEnter

☐ claude でログインして、様子見プロンプトを貼る

**次の一歩**：導入が済んだら、何を打てばいいかは『[最初の「3つ」だけ覚えればOK](https://note.com/zoobenia_0855/n/n3134af3ac0b9)』へ。

仕事で本格的に使う「型」は、¥500の[売れる商品企画プロンプト集](https://note.com/zoobenia_0855/n/nad0dca2ee6f6)と、月¥500の[メンバーシップ「売れる型の研究室」](https://note.com/zoobenia_0855/membership)にまとめています。

私は年商30.8億の事業を作ってきた元事業部長です。現場で使えるAIの型だけを、POP FRIENDSの仲間と一緒に配っています。

**出典**（2026-07-05確認）：[Claude Code 公式ドキュメント「高度なセットアップ」](https://code.claude.com/docs/ja/setup)（システム要件・インストールコマンド・認証）／[Claude Desktop アプリ](https://claude.com/download)／[Git for Windows](https://git-scm.com/downloads/win)
