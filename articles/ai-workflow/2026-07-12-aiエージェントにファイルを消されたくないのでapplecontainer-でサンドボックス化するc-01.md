---
id: "2026-07-12-aiエージェントにファイルを消されたくないのでapplecontainer-でサンドボックス化するc-01"
title: "AIエージェントにファイルを消されたくないので、apple/container でサンドボックス化するCLI「pall8t」を作った"
url: "https://zenn.dev/takitake/articles/c347d6f061a22f"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

## GitHubリポジトリ

<https://github.com/TakiTake/pall8t>

## 背景

AIエージェントを自律的に動かしたい。でもホストで直接動かすと、間違えてファイルを消される事故が怖い。かといって権限確認に毎回答えるのは本末転倒です。

コンテナに閉じ込めるのが定番の対策ですが、macOSを使っているならせっかくなので[apple/container](https://github.com/apple/container)を使いたい。Docker Desktop不要で、コンテナごとに軽量VMが立つmacOSネイティブのランタイムです。ただCLIがdocker非互換で、エージェント用途に必要なマウントや再ビルドを毎回手で組み立てるのは面倒でした。

そこで、その面倒を全部引き受けるCLIとしてpall8tを作りました。発音は「パレット」です。

## ゴール

`pall8t run` の一発で、カレントディレクトリをworkspaceにしたサンドボックス内でエージェントが起動する、というお手軽さを目標にしています。

サンドボックスといってもworkspaceは読み書き可能でマウントするので、そこのファイルは消され得ます（gitがあるのでだいたい戻せます）。pall8tがやるのは被害範囲の限定です。エージェントはVM内で動き、ホストの `~/.claude` や他のディレクトリには一切触れません。作られるファイルの所有者は常に自分のUIDになります。

## 前提条件

## インストール

```
brew install TakiTake/tap/pall8t
```

ソースからビルドする場合はリポジトリをcloneして `cargo install --path .` でも入ります。

## 使い方

```
cd ~/src/my-project
pall8t init   # 初回のみ: 設定ファイルとデフォルトContainerfileを生成
pall8t run    # サンドボックス内でエージェント（デフォルト: claude）が起動
```

初回の `pall8t run` ではコンテナ内で一度エージェントにログインします。ログイン情報は `~/.pall8t/home`（コンテナ用のホーム）に永続化されるので、次回以降は不要です。

### 設定

設定はTOML二層で、グローバル `~/.pall8t/config.toml` とプロジェクトの `.pall8t/config.toml` を項目ごとにマージします（プロジェクト側が優先）。

```
[container]
cpus = 4
memory = "8g"

[run]
command = ["claude"]         # 起動するエージェント。--dangerously-skip-permissions を
                             # 付けたい人はここに明示的に書く

[[repos]]                    # 参照用リポジトリ。git clone --local で複製した
source = "~/src/other-lib"   # コピーが同じパスにマウントされる
```

### Containerfileのカスタマイズ

サンドボックスのイメージはContainerfileで決まり、探す順番は「設定の `containerfile` → プロジェクトの `.pall8t/Containerfile` → ユーザーレベルのデフォルト」です。

**ユーザーレベル（デフォルト）を変える場合**は `~/.pall8t/Containerfile` を直接編集します。`pall8t init` が最初に一度だけ生成するファイル（中身はnode + claude CLI + gh）で、以後pall8tが上書きすることはありません。編集すれば全プロジェクト共通のデフォルトになり、削除すれば同梱のものに戻ります。

**プロジェクト専用にする場合**は、そのプロジェクトに `.pall8t/Containerfile` を置きます。存在すれば常にデフォルトより優先されます。ゼロから書くより `~/.pall8t/Containerfile` をコピーして手を入れるのが手っ取り早いです。

```
# プロジェクト用Containerfileをデフォルトから作る
cp ~/.pall8t/Containerfile ~/src/my-project/.pall8t/Containerfile
```

別の場所を指したい場合は設定に `containerfile = "path/to/Containerfile"`（プロジェクトディレクトリ相対）を書きます。なおプロジェクトルートの `./Containerfile` を暗黙に拾うことはしません。

どのContainerfileでも、編集すれば内容ハッシュが変わるので次の `pall8t run` で自動的に再ビルドされます。一つ注意点として、追加のツールチェーンは `/home/dev` 以外に入れてください。`~/.pall8t/home`（コンテナ用のホーム）のマウントが `/home/dev` を上書きするためです。

### 何をしてくれるか

カレントディレクトリはコンテナ内の**同じ絶対パス**にマウントされます。エージェントが作ったファイルをホストのIDEがそのまま同じパスで開けます。

Containerfileは内容のハッシュでイメージタグが決まるので、編集すると次の `run` で自動的に再ビルドされます。デーモンも状態ファイルもありません。

cwdがgit worktreeの場合は本体リポジトリの `.git` も一緒にマウントするので、コンテナ内の `git status` や `commit` がホストと同じに動きます。

設定に書いた参照リポジトリは複製したコピーをマウントするので、エージェントが何をしても原本は無傷です（apple/containerにread-onlyマウントがないことへの回避策です）。

## ハマった話：herdrにAgentとして認識されない

私は複数のエージェントを[herdr](https://herdr.dev/)で並べて管理しているのですが、素直にコンテナ上でclaudeを動かすと、herdrがペインをAgentとして認識してくれませんでした。

原因はherdrの検出方法です。herdrはホスト側のプロセスツリーを見て、argv[0]のベース名（`claude` など）からエージェントを識別します。サンドボックス構成ではVMの中のclaudeはホストから見えず、見えるのは `container` というクライアントプロセスだけ。herdrにとっては「何かが動いているペイン」でしかなく、idle/workingの状態追跡も効きません。

そこでpall8tは、containerクライアントをexecする際にargv[0]をエージェント名に差し替えるようにしました。herdrがペインを認識しさえすれば、エージェントの画面はPTYをそのまま流れてくるので、状態検出もネイティブ実行と同じに動きます。一筋縄でいかなかったのはHomebrew版の `container` で、実体がbashのexecラッパーになっており内側でargv[0]を書き戻してしまうため、ラッパーかどうかを判定して中のバイナリを直接execする対応も必要でした。

この辺りは全部Fable 5をぶん回して対応してもらいました。開発環境自体がpall8tのサンドボックスなので、pall8tの中で動くClaudeがpall8t自身を直すというドッグフーディングです。argv[0]が壊れる問題も、実際にこの構成で踏んで直しています。

## おわりに

エージェントには自由にやらせたい、でもホストは壊されたくない、という人にはちょうどいいはずです。フィードバックは[Issue](https://github.com/TakiTake/pall8t/issues)までどうぞ。

過去の記事を参考にこの記事をFable 5に書いてもらいましたが、所々に小癪な表現があったので微妙に添削しました笑
