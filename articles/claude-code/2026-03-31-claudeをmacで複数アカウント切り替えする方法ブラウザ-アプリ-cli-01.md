---
id: "2026-03-31-claudeをmacで複数アカウント切り替えする方法ブラウザ-アプリ-cli-01"
title: "ClaudeをMacで複数アカウント切り替えする方法（ブラウザ / アプリ / CLI）"
url: "https://zenn.dev/5alt_nacl/articles/claude-account-switching-guide-mac"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## この記事でできること

* Claudeを「個人用」と「仕事用」で完全に分離して使える
* デスクトップアプリを複数起動できる
* CLI（Claude Code）もアカウントごとに切り替え可能

## こんな人におすすめ

* Claudeを仕事と個人で分けたい
* 課金アカウントを複数使っている
* セキュリティ的に環境を分離したい

## 背景

以前まで個人的にClaudeを課金して利用してきましたが、複数アカウントを利用する状況が発生してきました。  
ブラウザ版では、Chromeプロファイルを切り替えることで対応してきましたが、Claudeデスクトップアプリや、Claude Code（CLI）でも同様に複数アカウントを切り替えて利用できるようにしたいと考え、その方法を試し実現できたので備忘録も兼ねてまとめます。

## 概要

本記事では、例として個人用と仕事用の2つのアカウントを切り替える方法を紹介します。対象は以下の3つです。

* **ブラウザ版 (claude.ai)**
* **Claude デスクトップアプリ**
* **Claude Code (CLI)**

## 1. ブラウザ版の切り替え

### Chromeプロファイル機能

Chromeの「プロファイル」機能を使えば、プロファイルごとに別アカウントでログインできます。

1. Chrome右上のアイコン → 「プロファイルを追加」
2. 個人用・仕事用のプロファイルを作成し、それぞれでclaude.aiにログイン
3. Dockに各プロファイルのショートカットを登録

## 2. Claude デスクトップアプリの切り替え

### デフォルトのデータ保存先

```
~/Library/Application Support/Claude/
```

### --user-data-dir フラグで別インスタンスを起動

ClaudeデスクトップアプリはElectron製のため、`--user-data-dir` フラグを使ってデータディレクトリを分離できます。

```
/Applications/Claude.app/Contents/MacOS/Claude \
  --user-data-dir="$HOME/Library/Application Support/Claude-Work"
```

### 初回セットアップ手順

1. 既存のClaudeアプリを完全終了（`Cmd+Q`）
2. ターミナルで以下を実行

```
open -n -a "Claude" --args \
  --user-data-dir="$HOME/Library/Application Support/Claude-Work"
```

3. 起動したアプリでログインを実施（Chromeプロファイルの仕事用アカウントで認証）
4. 通常のClaudeアプリ（個人用）と仕事用アプリを並行起動可能になる

### DockにランチャーをAutomatorで登録

Automatorでアプリ化しておくと、通常のアプリと同じようにDockからワンクリックで起動できるため便利です。

1. Spotlightで「Automator」を起動 → 「新規書類」→「アプリケーション」
2. 「シェルスクリプトを実行」アクションを追加して以下を入力

```
/Applications/Claude.app/Contents/MacOS/Claude \
  --user-data-dir="$HOME/Library/Application Support/Claude-Work"
```

3. `/Applications/Claude Work.app` などの名前で保存
4. LaunchpadからDockにドラッグしてDock登録完了

### アイコン変更方法

1. `/Applications/Claude.app` を右クリック →「情報を見る」（`Cmd+I`）
2. 情報ウィンドウ左上の小さいアイコンをクリックして選択 → `Cmd+C` でコピー
3. `Claude Work.app` を右クリック →「情報を見る」（`Cmd+I`）
4. 情報ウィンドウ左上の小さいアイコンをクリックして選択 → `Cmd+V` で貼り付け
5. Dockへの反映は `killall Dock` で即時反映

元に戻す場合

「情報を見る」の左上アイコンを選択 → `Delete` キーで元のアイコンに戻ります。

## 3. Claude Code（CLI）の切り替え

### デフォルトのデータ保存先

### 初回セットアップ手順

```
# Step 1: 現在のログイン済み状態（個人用）をコピー保存
cp -r ~/.claude ~/.claude_personal

# Step 2: 仕事用ディレクトリでログイン
CLAUDE_CONFIG_DIR=~/.claude_work claude login

# Step 3: エイリアスを登録
echo 'alias claude-personal="CLAUDE_CONFIG_DIR=~/.claude_personal claude"' >> ~/.zshrc
echo 'alias claude-work="CLAUDE_CONFIG_DIR=~/.claude_work claude"' >> ~/.zshrc

# Step 4: 反映
source ~/.zshrc
```

## まとめ

Claudeの複数アカウント運用は、

* ブラウザ → Chromeプロファイル
* デスクトップ → `--user-data-dir`
* CLI → `CLAUDE_CONFIG_DIR`

で「データディレクトリを分離する」ことで実現できます。

一度設定すれば、ほぼストレスなく使い分け可能になります。

Claudeをより活用するうえで、少しでも参考になれば嬉しいです。

## 参考
