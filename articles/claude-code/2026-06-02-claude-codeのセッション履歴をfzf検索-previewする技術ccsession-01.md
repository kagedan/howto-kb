---
id: "2026-06-02-claude-codeのセッション履歴をfzf検索-previewする技術ccsession-01"
title: "Claude Codeのセッション履歴をfzf検索 & previewする技術（ccsession）"
url: "https://zenn.dev/soramarjr/articles/4eb891ab20498e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

W杯の優勝予想はポルトガルです。  
[fujitani sora](https://x.com/sorafujitani)です。

![](https://static.zenn.studio/user-upload/440bb458cd58-20260601.png)  
ということで、  
`claude --resume`の使い勝手を改善するために「ccsession」というOSSを開発しています。  
これが何を解決するのか、どう使うのかの紹介記事です。

GitHub Star お願いします 😏

---

## ccsession が解決すること

Ctrl+Cなどによって終了したClaude Codeセッションを開き直す手段として、  
公式からは`claude --resume`オプションが提供されています。

一方、`claude --resume`に対して下記の課題感がありました。

* 別プロジェクトの session を resume したいときは、まずそのプロジェクトに `cd` してから起動する必要がある
* 検索時にPreviewができないので開かないと詳細がわからない
* セッションのbyte sizeなど、見えなくてもいい情報が載っている

![](https://static.zenn.studio/user-upload/bde0d79b9a2c-20260602.png)

`claude --resume`の利便性はそのままに、柔軟な検索やPreview、ディレクトリに依存せずに全セッションを検索対象とする機能を実装したCLIを開発しています。  
ccsession（シーシーセッション）と言います。

ざっくり下記の機能を提供します。

* PC内のClaude Code セッションを統一的に検索できる
* Previewによる、直近のやり取り・開始時刻・メッセージ数を確認してから選択できる
* 検索・プレビュー・再開をひと画面で完結できる

![](https://static.zenn.studio/user-upload/1541d72dcbdf-20260601.gif)

## Usage

`ccsession` を起動すると fzf が立ち上がり、PC内全てのセッションが一覧表示されます。

![](https://static.zenn.studio/user-upload/7a4ec29b93a7-20260602.png)

```
時刻      ディレクトリ      ラベル
2h ago    ccsession        list が ANSI を leak する問題
1d ago    toridori-inc     application監視の達成状態をまとめる
1d ago    blog             ccsession 紹介記事を書く
```

左から「Agent最終実行時刻, ディレクトリ, ラベル」を表示します。  
対象セッションにカーソルを当ててEnterを押すと、`claude --resume ${ID}`が内部的に実行され、過去の履歴を保持したままセッションを開きます。

ポイントとして、`ccsession`はPC内の全てのClaude Codeセッションを対象に検索することができます。  
`claude --resume`ではカレントディレクトリのClaude Codeセッションしか対象になりません。  
PC内の`.claude/project/`を横断的にロードし、まとめて検索する仕組みを実装しています。

本記事では実装詳細には踏み込みませんが、goroutineを活用した並列トラバーサルによってそれなりに高速です。

### 検索パターン

状況に応じて検索対象を切り替えられるようにしています。

| キー | やること |
| --- | --- |
| `Ctrl-F` | 通常の検索(デフォルト)。時刻・ディレクトリ・ラベルをまたぐ |
| `Ctrl-O` | ディレクトリ名だけで検索 |
| `Ctrl-G` | **セッションの会話の中身**で絞り込み。「あの会話で `xxx` って言ってたセッション」を探せる |
| `Enter` | 選択したセッションを開く |
| `Esc` | キャンセル |

### キーバインド設定(config.toml)

`Ctrl-F` / `Ctrl-O` / `Ctrl-G` をデフォルトのキーバインドとし、  
`.config/ccsession/config.toml`でのユーザー設定に対応しています。  
恒久的にキーバインドを設定したいときはこれを利用してください。

ex:

config.toml

```
[keybindings]
grep  = "ctrl-r"
dir   = "ctrl-o"
fuzzy = "alt-f"
```

コマンドのオプション, 環境変数によるキーバインド設定にも対応しています。  
一時的にキーバインドを変更したい場合はこれを利用してください。

```
# 1つのccsessionプロセスのみ
ccsession --bind-grep ctrl-r --bind-fuzzy alt-f

# shell単位での設定
export CCSESSION_BIND_GREP=ctrl-r
export CCSESSION_BIND_DIR=ctrl-o
export CCSESSION_BIND_FUZZY=alt-f
```

### その他オプション

セッション一覧に表示されて欲しくないディレクトリは`--exclude-dir` で隠せます。

```
ccsession --exclude-dir worktrees
```

fzf を介さず、ID を直接渡す単発のサブコマンドもあります。スクリプトに組み込みたいとき向け。

```
ccsession list                      # 全セッションを一覧で出力
ccsession list --grep "needle"      # 会話の中身で絞り込み
ccsession preview <sessionId>       # プレビューの内容を表示
ccsession resume <sessionId>        # そのセッションに戻る
```

## install

必要なのは [fzf](https://github.com/junegunn/fzf) と Claude Code 本体だけです。  
外部ライブラリ依存は現状ありません。

```
# Homebrew(おすすめ。fzf も一緒に入る)
brew install sorafujitani/tap/ccsession

# Nix flake
nix run github:sorafujitani/ccsession

# go install
go install github.com/sorafujitani/ccsession/cmd/ccsession@latest

# GitHub Releases から prebuilt binary
curl -L
https://github.com/sorafujitani/ccsession/releases/latest/download/ccsession_0.1.3_darwin_arm64.tar.gz | tar xz
install -m 0755 ccsession ~/.local/bin/
```

## contribution

ccsessionは、ユーザーの要望に応じて継続的に開発していく意思があります。  
自分もユーザーですしね。

IssueやPullRequest、フィードバックなどなど大歓迎です。  
good first issueもラベル付けしてあります。  
Templateも用意しているので、参考にしてみてください。

<https://github.com/sorafujitani/ccsession/issues>

<https://x.com/sorafujitani/status/2059985513810145282?s=20>

気に入ったら GitHub Star をもらえると励みになります！

<https://github.com/sorafujitani/ccsession>
