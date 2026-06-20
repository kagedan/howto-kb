---
id: "2026-06-19-kkk-cun-httpstcoiu97lbggl6-01"
title: "@kkk_cun: https://t.co/iU97lbGGl6"
url: "https://x.com/kkk_cun/status/2067826155420520624"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "x"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

https://t.co/iU97lbGGl6


--- Article ---
今回は有料noteをたった5分で3万文字の有料noteを作成する

というテーマで記事書いてみました。

こちらClaude codeを活用すれば大量の長文noteをたくさん作れます。

![](https://pbs.twimg.com/media/HLJkC5ZaUAEbJxH.jpg)

今回はその作り方を公開します。

==

## この記事で作るもの

Claude Codeに1つのコマンドを打つだけで、以下が自動で生成される仕組み。

・1000本分のnoteタイトル ・本文（3000〜8000字） ・冒頭のフック文 ・CTA  ・SEOメタデータ

しかも**ジャンル別に品質を最適化**できる。

副業系、マインド系、恋愛系、ビジネス系、自己啓発系… ジャンルごとに「売れる型」が違うから、それをテンプレートとして定義する。

## 前提条件

・Claude Codeがインストール済み  ・AnthropicのAPIキーを持っている

まだの人は以下の手順でセットアップ。

**Mac**

| bashcurl -fsSL

[https://claude.ai/install.sh](https://claude.ai/install.sh)

**Windows（PowerShell）：**

| iexirm

[https://claude.ai/install.ps1](https://claude.ai/install.ps1)

インストールしたら、APIキーを環境変数にセット。

**Mac/Linux**

export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxx

**Windows（PowerShell）：**

:ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxx"

[$env](https://x.com/search?q=%24env&src=cashtag_click)

これでClaude Codeが使える状態になる。

## STEP 1：プロジェクトを作って Claude Codeを起動する

やることはたった2つ。

**① ターミナルを開く **Mac → 「command + スペース」で「ターミナル」と入力してEnter   Windows → スタートメニューから「PowerShell」を開く

**② 以下の3行をコピペしてEnterを押す**

mkdir note-generator-1000 cd note-generator-1000 claude

これだけ。   1行目で作業フォルダを作って、2行目でそこに移動して、3行目でClaude Codeが起動する。

## STEP 2：CLAUDE.md＋フォルダ構成を一発で作る（これが最重要）

**CLAUDE.mdって何？ **Claude Codeがプロジェクトに入った瞬間に自動で読み込む「指示書」のこと。 人間でいうと「マニュアル」みたいなもの。

これがあると、**毎回プロンプトを打たなくても、 Claude Codeが勝手に「売れるnoteの書き方」を理解した状態で動いてくれる。**

Claude Codeの > に以下のプロンプトをそのまま貼り付けてEnterを押す。 CLAUDE.mdの作成も、フォルダの作成も、全部Claude Codeが自動でやってくれる。

**プロンプト⓪プロジェクト初期設定（CLAUDE.md＋フォルダ構成**）

以下の作業をすべて実行してください。

  【1】プロジェクトのフォルダ構成を作成 mkdir -p .claude/skills templates output data scripts  

【2】CLAUDE.md をプロジェクトルートに作成（以下の内容で）

  # NOTE自動生成プロジェクト

  ## プロジェクト概要 noteプラットフォームで販売する有料noteを自動生成するツール。 ターゲット：18〜35歳の副業・自己投資に関心がある日本人。 目標：1000本の「売れるnote」を生成する。

  ## 文章スタイルルール - 一文は60文字以内。短く切る。 - 漢字率は30%以下。ひらがな多めで読みやすく。 - 「〜です。〜ます。」の連続禁止。断定調と混ぜる。

 - 具体的な数字を必ず入れる（「たくさん」→「月収30万」）。 - 冒頭3行で読者の痛みに触れる（フック）。 - 箇条書きは5個以内。多すぎると読まれない。 - CTAは「今すぐ」「限定」「残りわずか」を自然に使
