---
id: "2026-06-13-claude-obsidianで忘れないai環境を1日で作った話-01"
title: "Claude × Obsidianで「忘れないAI環境」を1日で作った話"
url: "https://zenn.dev/n2naoya/articles/21382102b24395"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "GPT", "Python", "TypeScript"]
date_published: "2026-06-13"
date_collected: "2026-06-14"
summary_by: "auto-rss"
query: ""
---

AIはなぜ毎回忘れるのか。その問題をObsidianで解決した記録です。

![](https://static.zenn.studio/user-upload/d08c6e5ff094-20260613.jpeg)

この記事の対象読者

Obsidianをすでに使っている方

GitHubアカウントを持っている方

Claude Pro（$20/月）またはMax（$100/月）に契約済みの方

Macのターミナルに抵抗がない方

上記に当てはまらない方は、記事末尾の「事前準備」（有料）セクションを先にご確認ください。

この記事を読んでできるようになること

ObsidianのVaultをAIの「外部脳」として設計できる

ClaudeがセッションをまたいでVaultの内容を引き継いで動くようになる

Claudianを使ってObsidian内でClaude Codeが動く環境を構築できる

CLAUDE.mdで自分専用のAI行動ルールを設定できる

VaultをGitHubにバックアップして自動同期できる

Claude CodeからもVaultに接続できる

はじめに：AIは賢いけど忘れる

ChatGPTでもClaudeでも、毎回「自己紹介」から始めたことはないだろうか。

「私は福岡でAIコンサルをやっています」 「進行中のプロジェクトはこれです」 「このスタックで開発しています」

毎回同じことを説明するのは時間の無駄だし、AIも毎回ゼロから考えるから精度が上がらない。

この問題を解決するために、ObsidianをAIの「外部脳」として使う環境を1日で構築した。その記録を残しておく。

作ったものの全体像

今日1日で構築したのはこれだ。

Obsidian Vault（N-Brain）  
├── Daily/ 日次メモ・作業ログ  
├── Knowledge/ 技術知見・バグ解決  
├── Decisions/ 設計・方針決定の記録  
├── Projects/ 進行中プロジェクトの状態  
├── Preferences/ 自分の作業スタイル・好み  
└── Archive/ 完了プロジェクト

* CLAUDE.md（Claude専用の行動ルール）
* GitHub連携（自動バックアップ）
* Claudian（ObsidianでClaude Codeが動くプラグイン）

構築後の画面

Claude（AI）がこのVaultを毎回読んでから回答するので、自己紹介不要・文脈引き継ぎ済みの状態でやり取りできる。

ステップ1：Vaultのフォルダ構成を設計する

まずObsidianのVaultにどんなフォルダを作るかを決める。

決めた構成の理由

Daily/ → その日の気づきをとにかく放り込む場所

Knowledge/ → バグ解決・ツール発見など「次回知っておきたかった」ことを貯める

Decisions/ → 「なぜこれを選んだか」の記録。AとBで迷った理由を残す

Projects/ → 進行中プロジェクトの現在地。ClaudeはここをまずRead

Preferences/ → 自分の作業スタイル・使用スタック・好みを書いておく

Archive/ → 完了したものを移動する場所

1. 下のコードをコピーしてテキストエディタに貼り付ける

#!/bin/bash

# Obsidian × Claude 外部脳 初期セットアップ

# 使い方: bash setup-vault.sh /path/to/your/vault

# 例: bash setup-vault.sh /Users/yourname/MyVault

VAULT="{1:-HOME/MyVault}"

echo "Vault を作成します: $VAULT"

mkdir -p "$VAULT/Daily"  
mkdir -p "$VAULT/Knowledge"  
mkdir -p "$VAULT/Decisions"  
mkdir -p "$VAULT/Projects"  
mkdir -p "$VAULT/Preferences"  
mkdir -p "$VAULT/Archive"

# mistakes.md

## cat > "$VAULT/Knowledge/mistakes.md" << 'EOF'

# Claude ミス記録

Claudeへの行動矯正ルール。セッション開始時に必ず読む。

<!-- 形式:  
YYYY-MM-DD: [一言で何を間違えたか]  
**NG Action**: 実際にやってしまった間違い  
**Correct Action**: 次回からの正しい対応  
**Trigger**: このルールが適用される状況  
-->  
EOF

# profile.md

## cat > "$VAULT/Preferences/profile.md" << 'EOF'

# プロファイル

## 基本情報

* 名前: （あなたの名前）
* 拠点: （例: 東京・大阪・福岡）
* 仕事: （例: フリーランスエンジニア / 会社名・役職）
* 副業: （例: なし / ○○）

## 技術スタック

* 言語: （例: Python, TypeScript）
* フロントエンド: （例: Next.js, React）
* バックエンド: （例: Supabase, Firebase）
* 自動化: （例: n8n, GAS）
* 開発環境: （例: Cursor, VS Code）

## 進行中プロジェクト

* （プロジェクト名） → [[Projects/project-name]]

## 作業スタイル

* （例: シンプル・実用重視）
* （例: UIにemojiを使わない）

## 趣味

# Projects サンプルファイル

## cat > "$VAULT/Projects/my-project.md" << 'EOF'

# プロジェクト名

## 概要

## 現在の状態

## 直近のアクション

## メモ

EOF

echo ""  
echo "セットアップ完了: $VAULT"  
echo ""  
echo "作成したファイル:"  
find "$VAULT" -name "\*.md" | sort  
echo ""  
echo "次のステップ:"  
echo "1. Preferences/profile.md を自分の情報に書き換える"  
echo "2. CLAUDE.md を Vault のルートに配置する（有料付録）"  
echo "3. Obsidian で Vault を開いて確認する"

2. setup-vault.sh という名前で保存する
3. ターミナルで実行する

bash ~/Desktop/setup-vault.sh /Users/yourname/YourVault

ステップ2：CLAUDE.mdを設計する

これが核心部分だ。

CLAUDE.md はClaude（AI）への指示書。Vaultのルートに置いておくと、ClaudeがVaultを開くたびに自動で読み込む。

書いた内容はこの5つ

自分のプロフィール — 事業・スタック・家族・注意事項

セッション開始時の手順 — 毎回何を読むか

書き込みトリガー — どんなときに何のフォルダに書くか

フォーマット — YAMLフロントマターの形式

mistakes.md — Claudeが間違えたことを記録するファイル

特に重要なのが「書き込みトリガー」だ。

フォルダ書くタイミングKnowledge/バグ解決・API発見・次回知っておきたかったことDecisions/A vs B の選択・設計方針の決定Projects/プロジェクトの状態が変わったPreferences/自分の好み・スタイルを発見した

「後で書く」はしない。会話の流れの中で都度書き込む。これを徹底することでVaultが育っていく。

付録（有料）：CLAUDE.mdテンプレート 個人情報を抜いた汎用テンプレートを有料記事の付録として配布しています。  
0. プロファイルの欄を自分の情報に書き換えるだけで使えます。

ステップ3：Claudianを導入する

ObsidianでClaude Codeを動かすプラグイン「Claudian」を入れる。

インストール手順

ObsidianのコミュニティプラグインでBRATを検索しインストール

BRATの設定 → Add beta plugin → YishenTu/claudian を入力

コミュニティプラグインの一覧でClaudianが表示されたら有効化

前提条件

Claude Pro（$20/月）またはMax（$100/月）

Node.js v18以上

ハマったポイント

最初にこんなエラーが出た。

Error: API Error: 400 - cache\_control ttl error

原因はモデルの設定だった。Claudianのチャット欄下部に表示されているモデルが「Haiku」になっていたのを「Sonnet」に変えたら解決した。

ステップ4：動作確認する

Claudianのチャットに入力した。

CLAUDE.mdを読んで内容を教えて

返ってきた応答：

Obsidian: Knowledge/mistakes.md を読みました — 現在ミス記録なし  
Obsidian: Preferences/profile.md を読みました — プロファイル確認済み  
進行中プロジェクトが5件あることも確認しました。  
何かお手伝いできることはありますか？

CLAUDE.mdを読んでルールを認識し、mistakes.mdとprofile.mdも自動で読み込んでいる。設計通りに動いた。

ステップ5：GitHubと連携する

VaultをGitHubでバックアップ・バージョン管理する。

GitHubでPrivateリポジトリを作成

個人情報（家族の名前・生年月日・事業情報）が入っているのでPrivate必須。

ターミナルで初期設定

cd /Users/n2/N-Brain  
git init  
git add .  
git commit -m "initial commit"  
git branch -M main  
git remote add origin <https://github.com/USERNAME/N-Brain.git>  
git push -u origin main

GitHubの認証はPersonal Access Token（PAT）を使う。パスワードではなくトークンが必要になっているので注意。

Obsidian Gitプラグインで自動バックアップ

コミュニティプラグインで「Git」を検索してインストール。設定でAuto backup every X minutesを30に設定すれば30分ごとに自動でGitHubに同期される。

ステップ6：Claude Codeからも使えるようにする

ターミナルからVaultに移動してClaude Codeを起動するだけでいい。

cd /Users/n2/N-Brain  
claude

CLAUDE.mdをClaude Codeが自動で読み込むので、同じルールで動く。

さらにスキルファイルをVaultに置いた。

mkdir -p /Users/n2/N-Brain/.claude/skills/obsidian-vault  
cp SKILL.md /Users/n2/N-Brain/.claude/skills/obsidian-vault/SKILL.md

Claude Codeに確認すると：

obsidian-n-brainスキルが正常にロードされました。

完成した環境

要素内容Vault構成6フォルダ + CLAUDE.md + profile.md + mistakes.mdClaudianObsidian内でClaude Codeが動くClaude CodeターミナルからVaultに接続GitHubPrivateリポジトリで自動バックアップスキルobsidian-n-brainスキル登録済み

使い始めて感じたこと

よかった点

毎回自己紹介が不要になった。ClaudeがVaultを読んでから回答するので、プロジェクトの文脈を共有済みの状態でやり取りできる。

スマホはまだ使えない

ClaudianはObsidianのデスクトップ専用プラグインなので、iPhoneでは動かない。スマホでは普通のObsidianアプリでメモを書いて、Mac作業時にClaudianが読む、という使い方が現実的。

Vaultは育てるもの

セットアップしただけでは意味がない。作業のたびにProjectsを更新して、バグを解決したらKnowledgeに書いて、設計を決めたらDecisionsに残す。この習慣をつけることでVaultが育ち、Claudeの精度が上がっていく。

まとめ

AIに毎回自己紹介するのをやめたければ、外部脳を作るのが一番の近道だ。

ObsidianはMarkdownファイルをローカルに持てるので、GitHubでバックアップしながらClaudeと一緒に育てていける。Claudianがあればターミナルを開かなくてもObsidian内でClaude Codeが動く。

環境構築に1日かかったが、これで毎回の文脈共有コストがほぼゼロになった。

補足：事前準備

本編を始める前に以下が揃っていない方はここから準備してください。

1. Obsidianのインストール

<https://obsidian.md> からダウンロードしてインストール。 起動後「新しいVaultを作成」でフォルダを指定するだけで使えます。

2. GitHubアカウントの作成

<https://github.com> にアクセスしてSign upからアカウント作成。 メールアドレスがあれば無料で作れます。

3. Claude Proの契約

<https://claude.ai> にアクセスしてUpgrade to Pro。 月額$20（約3,000円）。Claudianを動かすために必要です。

4. Node.jsのインストール

<https://nodejs.org> から「LTS版」をダウンロードしてインストール。 インストール後、ターミナルで以下を実行して確認してください。

node -v

v18.0.0 以上が表示されればOKです。

5. Claude Code CLIのインストール

ターミナルで以下を実行してください。

npm install -g @anthropic-ai/claude-code

完了後：

claude /login

ブラウザが開くのでAnthropicアカウントでログインしてください。

以上が揃ったら本編のステップ1から進めてください。
