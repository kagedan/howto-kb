---
id: "2026-04-20-claude-code-の記憶を育てる-osskiokuを作った-01"
title: "Claude Code の記憶を育てる OSS「KIOKU」を作った"
url: "https://qiita.com/megaphone-tokyo/items/fdd8d91e1134e15fc5d7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

[![Generated Image April 16, 2026 - 10_20PM.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4412014%2F6e9ada1a-a55d-4a23-af43-45cbe7e22037.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a9d323bc5c32420e35cbb404b60a3097)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4412014%2F6e9ada1a-a55d-4a23-af43-45cbe7e22037.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a9d323bc5c32420e35cbb404b60a3097)

> ※この記事は [Zenn での投稿](https://zenn.dev/megaphone/articles/af2b2a05531912) の転載です。

## はじめに

Claude Code を毎日使っていて、一つ大きな不満がありました。

**「前のセッションで話した内容、次のセッションでは全部忘れられている」**

プロジェクトの前提、使っている技術スタック、設計判断の理由。毎回一から説明し直す日々。「これ昨日も言ったんだけどな...」を何度繰り返したか分かりません。

この問題を解決するために、Claude Code のセッション記憶を自動で蓄積するツールを作りました。

**KIOKU — Memory for Claude Code**

「KIOKU」は日本語の「記憶」。使うほどに育つ「second brain（第二の脳）」を Claude に持たせる、というコンセプトです。

## インスピレーション

発想の元は Andrej Karpathy が公開した [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) です。

「LLM との対話ログから構造化された Wiki を育てる」というコンセプト。これを読んだ時、「まさにこれが欲しかった」と思いました。

ただ、gist はあくまでコンセプトの提示で、実装は各自に委ねられています。そこで Claude Code に特化した形で、自動化まで含めて作り込んだのが KIOKU です。

## 何が起きるのか

KIOKU を入れると、こういう流れが自動で回ります。

```
🗣️  いつも通り Claude Code と会話する
         ↓  （自動で記録される — あなたは何もしなくていい）
📝  セッションログがローカルに保存される
         ↓  （定期ジョブが AI にログを読ませ、知識を抽出する）
📚  Wiki がセッションごとに育つ — 概念、設計判断、パターン
         ↓  （Git で同期）
☁️  GitHub が Wiki をバックアップし、複数マシン間で共有する
```

ポイントは **「あなたは何もしなくていい」** という部分です。ノートを取る必要も、ログを整理する必要もありません。ただ Claude Code と会話するだけで、裏側で Wiki が育っていきます。

## アーキテクチャ

KIOKU は 4 層構造になっています。

### L0: 自動収集

Claude Code の Hook システムを使って、セッションの入出力を捕捉します。

使っている Hook イベントは 4 つです。

* `UserPromptSubmit` — あなたが入力したプロンプト
* `Stop` — Claude の応答
* `PostToolUse` — ツール実行の結果
* `SessionEnd` — セッション終了時のファイナライズ

これらを Obsidian Vault の `session-logs/` に Markdown として書き出します。外部依存ゼロの `.mjs` スクリプトで、ネットワークアクセスも一切しません。

### L1: 構造化

macOS の LaunchAgent（Linux では cron）で定期実行するジョブがあります。

このジョブが `session-logs/` の未処理ログを `claude -p` に読ませ、`wiki/` 配下に構造化されたページを生成します。

生成されるのは以下の種類のページです。

* **概念ページ** — 技術的な概念やパターンの説明
* **プロジェクトページ** — プロジェクト固有の文脈、技術スタック、設計方針
* **設計判断ページ** — なぜその判断をしたかの記録（コンテキストと理由付き）
* **セッション分析** — 各セッションから抽出された知見

### L2: 整合性チェック

月次で Wiki 全体の健全性をチェックします。壊れた wikilink、欠落した frontmatter、孤立したページを検出して `wiki/lint-report.md` にレポートします。秘密情報の漏れ検知もここで自動実行します。

### L3: 同期

Vault 自体を Git リポジトリにしています。`SessionStart` で `git pull`、`SessionEnd` で `git commit && git push` することで、複数マシン間で Wiki を共有します。

重要なのは、**session-logs/ は Git に入らない**ということです。`.gitignore` で除外し、マシンごとにローカル保持します。Git で共有するのは蒸留された `wiki/` だけです。

### Wiki コンテキスト注入

ここが KIOKU の核心部分です。

`SessionStart` 時に `wiki/index.md` をシステムプロンプトに注入します。これによって、Claude は過去のセッションで蓄積された知識を持った状態で新しいセッションを開始します。

つまり「前のセッションで決めた設計判断」が、次のセッションでは最初から Claude の頭に入っている状態になります。

## 技術的に工夫した点

### セッションログのマスキング

これが一番神経を使った部分です。

Claude Code のセッションには、プロンプトや tool 出力として API キーやトークンが含まれることがあります。これをそのままログに残すのは危険です。

`session-logger.mjs` では正規表現ベースのマスキングを実装しています。対象は以下のプロバイダーのトークンです。

* Anthropic / OpenAI / GitHub / AWS
* Slack / Vercel / npm / Stripe
* Supabase / Firebase / Azure
* Bearer / Basic 認証トークン
* URL 埋込クレデンシャル
* PEM 秘密鍵

検出したトークンは `***` に置換してからログに書き出します。

ただし、正規表現マスキングは完全ではありません。新しいサービスのトークンフォーマットには対応できないこともあります。そのため、月次の `scan-secrets.sh` でマスキング漏れを検知する二重チェックも入れています。

### .gitignore ガード

session-logs/ を `.gitignore` で除外しているだけでは不十分だと考えました。

SessionEnd の `git commit` を実行する前に、`.gitignore` に `session-logs/` が含まれていることを**毎回検証する**ガードを入れています。誰かが誤って `.gitignore` を編集してしまった場合でも、セッションログが GitHub に push されるのを防ぎます。

### Hook の再帰防止

これはハマりました。

auto-ingest ジョブは `claude -p` を呼んでログを処理します。しかし、`claude -p` の実行自体も Claude Code のセッションなので、Hook が発火します。つまり「ログを処理するためのセッション」のログが生成され、さらにそれを処理しようとして... という再帰ループが発生します。

解決策として、二重ガードを実装しました。

1. **環境変数ガード**: `KIOKU_NO_LOG=1` を設定して `claude -p` を呼ぶ。Hook スクリプトはこの変数を見て早期 return
2. **cwd チェック**: カレントディレクトリが Vault 内かどうかを確認。Vault 内からの実行はログ対象外

どちらか一方が壊れても、もう一方が再帰を止めます。

### LLM の権限制限

auto-ingest / auto-lint で呼ぶ `claude -p` は、`--allowedTools Write,Read,Edit` で実行しています。

**Bash は許可していません。**

Wiki の生成・編集に必要なのはファイルの読み書きだけです。Bash を許可してしまうと、万が一プロンプトインジェクション的なことがあった場合のリスクが大きすぎます。

## 実際の運用

私は MacBook（メイン開発機）と Mac mini の 2 台構成で運用しています。

* session-logs/ はマシンごとにローカル保持
* wiki/ は Git 同期で共有
* Ingest(Wiki生成ジョブ)の実行時刻を 30 分ずらして Git の競合を回避（MacBook: 7:00/13:00/19:00、Mac mini: 7:30/13:30/19:30）

数週間使ってみて、**想像以上に快適でした**。

特に効果を感じたのは以下の場面です。

* **設計判断の継続性**: 「昨日、パフォーマンスの理由で X ではなく Y を選んだ」という文脈が次のセッションで自動的に引き継がれる
* **技術スタックの説明不要**: プロジェクトで使っている技術の組み合わせを毎回説明しなくていい
* **過去の失敗の記憶**: 「前に Z のアプローチを試して、こういう理由でうまくいかなかった」が記録されている

## セットアップ

KIOKU には対話式セットアップがあります。Claude Code で以下を入力するだけです。

```
skills/setup-guide/SKILL.md を参照して、KIOKU のインストール作業をしてください。
```

Claude Code 自身がステップごとに説明しながら、環境に合わせてセットアップを進めてくれます。

手動でやりたい場合は README に詳しい手順があります。必須ステップは 5 つだけで、それ以降はオプションです。

## やるべきだったこと・やり直したいこと

振り返ると、いくつか「最初からこうすればよかった」と思うことがあります。

**Wiki スキーマをシンプルに始めるべきだった**

最初からノートテンプレートを作り込みすぎました。概念ページ、プロジェクトページ、設計判断ページ... と分類を細かくしたのですが、初期は「とりあえず全部メモ」くらいの粒度で始めて、蓄積されてから分類した方が自然だったかもしれません。

**Ingest プロンプトのチューニングが重要**

Wiki ページの品質は、Ingest 時のプロンプトにほぼ完全に依存します。最初のプロンプトでは「あらゆる知見を抽出して」と指示していましたが、ノイズが多すぎました。「本当に次のセッションで必要になる情報だけ」に絞る選別基準の調整は、今も継続中です。

## 今後の計画

* **マルチ LLM 対応**: 現在は Claude Code（Max プラン）専用ですが、`claude -p` の部分をプラガブルにして OpenAI API や Ollama 経由のローカルモデルでも動くようにする予定です
* **Morning Briefing**: 毎朝の日次サマリーを自動生成。昨日のセッション要約、未完了の設計判断、新しい知見のハイライトを `wiki/daily/` に出力
* **プロジェクト別コンテキスト注入**: cwd からプロジェクトを推定し、注入する Wiki の内容をフィルタリング
* **チーム共有 Wiki**: 複数人での Wiki 共有（各メンバーの session-logs はローカル保持、wiki/ のみ Git で共有）

## まとめ

Claude Code は強力なツールですが、セッション間の記憶がないのが大きな弱点でした。KIOKU はその弱点を補い、「使えば使うほど Claude があなたの文脈を理解していく」状態を作ります。

Karpathy の LLM Wiki gist のコンセプトを、Claude Code に特化した形で実装し、自動化しました。MIT License で公開しています。

フィードバック、Issue、PR、大歓迎です。

特に以下の点について意見をもらえると嬉しいです。

* Wiki のディレクトリ構成はこれで使いやすいか
* Ingest の選別基準をどう調整すべきか
* マルチ LLM 対応で優先すべきバックエンドは何か

## 他のプロダクト

趣味で撮影した季節の写真を集めたギャラリーサイトです。  
作者が撮影した四季折々の写真を眺められるだけでなく、**自分の画像と季節の写真を AI で合成する**機能もあります。

写真が好きで、AI で遊ぶのも好き、という個人的な興味から作りました。

---

**作者**: [@megaphone\_tokyo](https://x.com/megaphone_tokyo)  
コードと AI で何かつくる人 / フリーランスエンジニア 10 年目
