---
id: "2026-04-08-claude-notebooklmclaude-codeのskillで2つのaiを連携させる方法セッ-01"
title: "【Claude × NotebookLM】Claude CodeのSkillで2つのAIを連携させる方法【セットアップ手順付き】"
url: "https://note.com/miyabi5432/n/nba9cc05e3f76"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-04-08"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## はじめに

こんにちは！エンジニアのたまごのKAIです。

普段からAIを開発業務でバリバリ活用しているのですが、最近「**Claude CodeのSkillを使ってNotebookLMと連携させる**」という使い方にハマっています。

「ClaudeとNotebookLM、それぞれ使ってるけど別々に使っている」という方も多いと思います。でもこの2つを連携させると、**Claudeの頭の良さ + NotebookLMのドキュメント特化の精度**という最強の組み合わせが実現します。

この記事ではGitHubで公開されているSkillを使ったセットアップ手順から、実際の使い方まで丸ごとまとめます！

---

## そもそもClaude Codeとは？

**Claude Code** はAnthropicが提供するCLI（コマンドライン）ツールです。ターミナルからClaudeに指示を出してコードの編集・検索・実行などを自動でやってくれます。

さらに「**Skill（スキル）**」という拡張機能があり、GitHubで公開されているSkillをクローンするだけで外部サービスとの連携が可能になります。今回使う**notebooklm-skill**もその一つです。

---

## NotebookLMとは？

**NotebookLM** はGoogleが提供するAIノートツールです。最大の特徴は「**自分がアップロードしたドキュメントだけを参照して回答する**」という点です。

ChatGPTやClaudeに直接ドキュメントを貼って聞く方法と比べて、何がいいかというとこんな感じです。

方法トークン消費ハルシネーション回答品質ドキュメントをClaudeに直接貼る高いあり不安定Web検索中高いバラつきあり**NotebookLM Skill**最小限**ほぼなし**ソース根拠あり

---

## 2つを連携させるとどうなるの？

Claude Codeのnotebooklm-skillを使うと、**Claudeのターミナルから直接NotebookLMのノートブックに質問**できます。

あなた（Claude Codeに指示） ↓ Claude Code（ブラウザを自動操作） ↓ NotebookLM（自分のノートブックをもとにGeminiが回答） ↓ Claude Code（回答を整理・分析して返答） ↓ あなた

コピペ不要で、**Claudeが勝手にNotebookLMに聞きに行って答えを持ってきてくれます。**

---

## セットアップ手順

### Step 1：skillsディレクトリにクローン

bash mkdir -p ~/.claude/skills cd ~/.claude/skills git clone https://github.com/PleasePrompto/notebooklm-skill notebooklm

これだけです。クローン後はClaude Codeを開くと自動的にSkillが認識されます。

初回使用時には以下が**自動でセットアップ**されます：  
- Python仮想環境（.venv）の作成  
- 必要なライブラリのインストール  
- ブラウザ自動化のセットアップ

手動でのインストール作業は不要です。

### Step 2：Google認証（初回のみ）

Claude Codeで以下のように話しかけます：

"Set up NotebookLM authentication"

またはターミナルから直接：

bash python scripts/run.py auth\_manager.py setup

Chromeブラウザが起動するので、Googleアカウントでログインします。一度認証すれば以降は自動的にセッションを引き継いでくれます。

### Step 3：NotebookLMでノートブックを作成・共有

1. notebooklm.google.com にアクセス
2. ノートブックを作成してドキュメントをアップロード
3. PDF・Google Docs・Markdownファイル
4. Webサイト・GitHubリポジトリ・YouTubeも可
5. **⚙️ 共有 → リンクを知っている全員 → URLをコピー**

### Step 4：ノートブックをライブラリに登録

Claude Codeでこう伝えるだけです：

"このノートブックを追加して：[コピーしたURL]"

ClaudeがノートブックのURLにアクセスして内容を自動判定し、メタデータを付けて登録してくれます。

### Step 5：質問する

あとは普通にClaudeに話しかけるだけです：

"技術仕様書を参照して、認証フローについて教えて" "このシステムのAPIエンドポイント一覧をまとめて"

---

## 具体的な活用シーン

### 社内ドキュメントのQ&A

設計書や仕様書をNotebookLMにアップロードしておけば、「この機能の仕様は？」と聞くだけで**引用付きの正確な回答**が得られます。ドキュメントに書いてあることだけ答えてくれるので、でたらめな回答が来ません。

### 技術記事・ブログ執筆

参考にしたい資料をまとめてノートブックに入れておき、記事執筆時にClaudeから質問→回答を参考にして執筆、という流れが作れます。

### 資格・試験の勉強

テキストや過去問解説をNotebookLMにアップロードして「この概念を説明して」と聞くと、アップロードしたテキストの内容をもとに説明してくれます。

---

## 使ってみてわかった注意点

注意点内容ローカルのClaude Codeのみ対応Claude.ai（Web版）では動作しない質問の上限無料Googleアカウントで1日50回まで毎回ブラウザが起動質問ごとに新セッションが開くため数秒かかるドキュメントは手動アップロードNotebookLMへのファイル追加は自分で行う

「毎回ブラウザが立ち上がる」のは最初少し気になりましたが、すぐ慣れます。回答の精度を考えると十分すぎるトレードオフです。

---

## おわりに

GitHubからクローンするだけで使えるのがこのSkillの素晴らしいところです。インフラ不要・設定最小限で「ClaudeがNotebookLMを使いこなしてくれる」環境が5分で整います。

「ドキュメントが多くて探すのが大変」「AIに聞いても的外れな回答が来る」という場面でぜひ試してみてください！

この記事が参考になったら**スキ！をポチっとしていただけると励みになります**！質問・感想はコメントで教えてください！
