---
id: "2026-03-21-2026321最新claude-code-on-the-webのスケジュールタスクで毎朝aiニュース-01"
title: "【2026/3/21最新】Claude Code on the webのスケジュールタスクで毎朝AIニュースを自動収集してみた"
url: "https://qiita.com/rf_p/items/23303cde99deddd24689"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "cowork", "qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## はじめに

2026/3/21、Claude Code PMのNoah Zweben氏から、Claude Code on the webに**スケジュールタスク機能**が追加されたことが発表されました。

Claude Code DesktopやClaude Coworkには少し前に追加された機能ですが、今回クラウド実行に対応したことで、PCの電源を気にせず定期実行できるようになっています。

せっかくなので、元々ローカルで定期実行していた仕組みをクラウド化しました。  
AIエージェント・開発ツール系のニュースを毎朝自動収集してGitHub Pagesで読めるようにする仕組みです。実際に稼働しているリポジトリとビューアはこちらです。

[![スクリーンショット 2026-03-21 18.01.16.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F199678%2F9fe18e22-2ae2-4df4-b6ba-14ff7346907d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=82f39aa32092111228cd5bf522712e89)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F199678%2F9fe18e22-2ae2-4df4-b6ba-14ff7346907d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=82f39aa32092111228cd5bf522712e89)

## Desktop版との違い

Desktop版のスケジュールタスクはローカルで実行されるため、PCが起動していないと動きません。朝のニュース収集をセットしておいても、PCがスリープ状態だから実行されないことがほぼ毎日でした。on the web版はクラウド実行なので、この問題がなくなります。

もう一つの大きな違いは、on the web版はGitリポジトリが前提になる点です。そのためブランチへのpush権限を制御する設定があります。

| 項目 | Desktop | on the web |
| --- | --- | --- |
| 実行環境 | ローカルマシン | クラウド |
| PC & Claudeアプリ起動が必要 | はい | いいえ |
| Gitリポジトリ | 任意 | 必須 |
| ブランチpush制御 | 設定に準じる | あり（`claude/*` のみ or 全ブランチ） |

デフォルトでは `claude/*` ブランチにしかpushできず、「ブランチプッシュの制限を解除」をオンにすると `main` を含む全ブランチにpushできるようになります。（もちろんリスクも増えます）

## 設定画面

スケジュールタスクの作成画面では、以下の項目を設定します。

[![スクリーンショット 2026-03-21 17.43.57.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F199678%2F37d356f7-a042-4211-bc7b-96343cc1ca12.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4042f149d3fad3457af4e4e53d77fbc9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F199678%2F37d356f7-a042-4211-bc7b-96343cc1ca12.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4042f149d3fad3457af4e4e53d77fbc9)

* **名前**: タスクの識別名
* **プロンプト**: 各セッションでClaudeが行うことを自然言語で記述
* **モデル**: 実行に使うモデル（Opus 4.6等）
* **リポジトリ**: 対象リポジトリ（複数指定可）
* **環境**: 設定済みの環境選択
* **頻度**: 時間ごと / 毎日 / 平日 / 週次
* **時間**: 実行時刻（JST表示）
* **コネクタ**: 接続済みのNotion, Slack等がデフォルトで含まれる（不要なら削除可）
* **ブランチプッシュの制限を解除**: リポジトリごとにpush先を制御

## RSSリーダーやキュレーションメディアとの違い

やっていることは簡易的な自作RSSリーダーに近いですが、LLMが間に入ることでいくつかの違いがあります。

**メリット:**

* **RSS非対応サイトでもいける**。WebFetchでHTMLを直接取得してLLMが解釈するので、RSSフィードがないサイト（Cursor ChangelogやDevin Release Notes等）も監視対象にできます
* **自分の興味でフィルタリングできる**。`.claude/rules/interests/` に関心領域を書いておけば、LLMがそれに基づいて取捨選択します。「学術論文のみは除外、実装を伴うものだけ拾う」といったニュアンスのあるフィルタリングが自然言語で書けます
* **監視先の改善もLLMに任せられる**。ダイジェスト末尾に「改善メモ」セクションを設けていて、新しい監視対象の提案やURL変更の検知を毎回出力させています。別のスケジュールタスクでHuman-in-the-loopを取り入れれば、サジェストの承認から実装まで自動化することもできます
* **ビューアのカスタマイズが自由**。HTML1ファイルなので、見た目を変えたければCSSを書き換えるだけです。RSSリーダーのUIに不満があっても変えられませんが、これは自分のリポジトリなので好きにできます

**デメリット:**

* **リポジトリが肥大化していく**。毎日Markdownファイルが増えるので、長期運用するとdigests/以下が膨らみます。アーカイブの仕組みは自分で考える必要があります
* **簡易的なので壊れやすい**。バックエンドもDBもないHTML+JSON構成なので、`files.json` の整合性が崩れるとビューアが壊れます
* **LLMなので確率的に動く**。WebFetchの取得失敗、差分判定のミス、フォーマットのブレなど、毎回同じ品質で実行される保証はありません。実際、サイトの構造が変わると取得内容が変わることがあります
* **利用枠を消費する**。毎日のスケジュールタスク実行はClaude Codeの利用枠を使います
* **セキュリティリスクがある**。監視対象サイトをユーザーが自由に追加できる構造なので、悪意のあるサイトをソースに含めてしまうと、WebFetch時にプロンプトインジェクション等の攻撃を受ける可能性があります。信頼できるサイトのみを監視対象にしてください

バックエンドやDBを使わない分セットアップは楽ですが、堅牢性はトレードオフになります。壊れても直せばいい、くらいの温度感で運用するのが合っています。

## 作ったものの概要

毎朝のスケジュールタスクで以下のソースを巡回し、Markdownダイジェストを生成してGitHub Pagesに自動反映する仕組みです。

**監視対象サイト:**

* Claude Code Changelog / Anthropic Blog / Claude Release Notes
* Cursor Changelog / Devin Release Notes  
  など

**処理の流れ:**

```
スケジュールタスク（毎朝実行）
  ↓
対象サイトをWebFetch / WebSearchで巡回
  ↓
前回チェック状態との差分を抽出
  ↓
Markdownダイジェストを生成
  ↓
git commit + push → GitHub Pages に自動反映
```

ビューアはHTML1ファイルで、marked.jsでMarkdownをレンダリングしているだけです。バックエンドは不要で、GitHub Pagesの静的ホスティングだけで完結します。

## リポジトリ構成

```
ai-news/
├── .claude/
│   └── rules/              # フィルタリング基準・対象サイト・出力スタイル
│       ├── interests/
│       │   └── ai-tools.md
│       ├── preferences/
│       │   └── output-style.md
│       └── sites/
│       │   └── daily-sources.md
├── digests/                 # 生成されたダイジェスト（YYYY/MM/配下）
├── .last-check-state.md     # 前回チェック状態（差分判定用）
├── files.json               # ビューア用ファイル一覧
├── index.html               # GitHub Pagesビューア
└── CLAUDE.md                # プロジェクト方針・生成手順
```

監視対象やフィルタリング基準を `.claude/rules/` に分離しています。CLAUDE.mdに全部書くと肥大化するので、関心事ごとにファイルを分けました。サイトを追加したければ `sites/daily-sources.md` を編集するだけで済みます。

mainにpushする必要があるため、ブランチプッシュの制限は解除しておきます。

## Forkして試す手順

このリポジトリをForkすれば、自分専用のニュースレターとして使えます。

### 1. ForkしてGitHub Pagesを有効化

```
Settings > Pages > Source: main, / (root)
```

### 2. ルールをカスタマイズ

`.claude/rules/` 配下のファイルを自分の関心に合わせて編集します。

* `sites/daily-sources.md` — 監視対象サイトの追加・削除
* `interests/ai-tools.md` — 関心領域のカスタマイズ
* `preferences/output-style.md` — 出力フォーマットの調整

たとえばフロントエンド技術に特化させたければ、`daily-sources.md` にReact BlogやNext.js Release Notesを追加して、`ai-tools.md` の関心領域を書き換えるだけです。

### 3. 状態をリセット

```
echo -e "# 前回チェック状態\n\n初回実行前。状態なし。" > .last-check-state.md
echo "[]" > files.json
```

### 4. スケジュールタスクを設定

Claude Code on the webでスケジュールタスクを作成します。プロンプトには以下のような手順を記述します。

```
以下の手順でAIニュースダイジェストを生成してください。

1. CLAUDE.md を読み、プロジェクト構成を確認
2. .claude/rules/ 配下の全ファイルを読み込み
3. .last-check-state.md を読み、前回チェック状態を確認
4. daily-sources.md に定義されたソースから情報を収集（WebFetch / WebSearch）
5. 前回状態との差分を判定し、新規情報のみを抽出
6. output-style.md に従い、ダイジェストを生成
7. digests/YYYY/MM/ai-news-YYYY-MM-DD.md として保存
8. .last-check-state.md を今日の状態で更新
9. files.json の配列先頭に新ファイルのパスを追加
10. git add → commit → push (main)
```

## 注意点

* **GitHub PagesはPrivateリポジトリでも公開されます**。ダイジェスト内容に機密情報や個人情報を含める場合はPrivateリポジトリにするとともに、Pagesを無効化してください
* PrivateリポジトリでGitHub Pagesを使うにはGitHub Pro以上が必要です
* スケジュールタスクの実行にはClaude Codeの利用枠を消費します

## その他利用方法

放置されているPull RequestやチェックすべきissueをSlackに通知させる、等の使い方が可能です。  
むしろ、一般的にはそういったGitHubを用いたワークフローの自動化に利用するツールだと思います。

## まとめ

on the web版のスケジュールタスクは、PCの状態を気にせずクラウドで定期実行できるのが一番の利点です。Gitリポジトリ前提なのでGitHub Pagesとの組み合わせが自然で、バックエンドなしで自動更新されるサイトが作れます。

クラウド上でリポジトリ内の定期実行ができるということは、ありとあらゆる作業の自動化が可能です。ご自身の業務に合わせてカスタマイズしてみてください。
