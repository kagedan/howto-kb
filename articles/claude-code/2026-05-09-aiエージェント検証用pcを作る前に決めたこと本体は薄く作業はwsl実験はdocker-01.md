---
id: "2026-05-09-aiエージェント検証用pcを作る前に決めたこと本体は薄く作業はwsl実験はdocker-01"
title: "AIエージェント検証用PCを作る前に決めたこと：本体は薄く、作業はWSL、実験はDocker"
url: "https://zenn.dev/imaginarygate/articles/ee2ad30e1e5e52"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "GPT", "Python", "zenn"]
date_published: "2026-05-09"
date_collected: "2026-05-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

古いSurfaceを、AIエージェント検証専用機として再構築することにした。

目的は、Codex CLI、Claude Code、Docker、ブラウザAIエージェントなどを、安全に検証できる環境を作ること。

最初は「古いPCを初期化して、必要なツールを順番に入れていけばよい」と考えていた。

しかし実際には、Python、Node.js、Git、Codex CLI などを Windows本体に入れるべきなのか、WSL側に寄せるべきなのかで迷う場面が多かった。

さらに、AIエージェント系ツールはローカル環境へアクセスできる範囲が広いため、「どこで動かすか」を先に整理しておく必要があると感じた。

結果として、単に「AIエージェントを動かす」だけでなく、先に設計思想を決めておく必要があると分かった。

この記事では、AIエージェント検証用PCを作る前に決めた方針を整理する。

---

## この記事の前提

今回使う端末は、古いSurface。

想定している環境は以下。

* OS: Windows 11
* 用途: AIエージェント検証専用機
* 目的: メインPCや本番データから切り離した安全な検証環境を作る

この端末では、以下のようなものを試す予定。

* Codex CLI
* Claude Code
* Docker
* WSL2 / Ubuntu
* ブラウザAIエージェント
* AIによる作業ログ整理

ただし、最初から本物のデータや本番アカウントを扱うのではなく、まずはダミーデータと検証用アカウントだけで試す。

---

## 最初に決めた合言葉

今回の設計方針は、以下の一文にまとめた。

この合言葉を、今後の判断基準にする。

何かをインストールする前に、以下を確認する。

* これはWindows本体に入れるべきか？
* WSL側でよいのではないか？
* Dockerコンテナ内で済むのではないか？
* AIエージェントに触らせる必要があるのか？

---

## なぜ設計思想が必要だったのか

AIエージェント系のツールは、便利な反面、ファイルを読んだり、編集したり、コマンドを実行したりできる。

つまり、普通のチャットAIよりも、ローカル環境への影響が大きい。

何も考えずに普段使いのPCへ入れてしまうと、以下のような不安が出る。

* 普段使いのファイルを読まれるかもしれない
* 本物のAPIキーや認証情報に触れるかもしれない
* メインアカウントのデータと混ざるかもしれない
* どのツールがどこに入ったか分からなくなる
* Windows本体のPATHや環境変数が汚れる
* 後から再現できない環境になる

そこで今回は、「とりあえず動かす」よりも、安全に検証できる構成を作ることを優先する。

---

## Windows本体はなるべく薄くする

今回の基本方針は、Windows本体に開発用ツールをなるべく入れないこと。

Windows本体は、あくまで母艦として扱い、環境汚染を防ぐために極力手を加えないこと。

Windows本体に置いてよいものは、以下に限定する。

* ブラウザ
* VS Code
* Docker Desktop
* WSL2
* Claude / ChatGPT などのAIクライアントアプリ
* 必要最低限の認証系アプリ

一方で、以下は原則としてWindows本体には入れない。

* Python
* Node.js
* npm
* Git
* Codex CLI
* Claude Code
* その他の開発用CLIツール

これらは、基本的にWSL / Ubuntu側に入れる。

---

## 開発ツールはWSL側に寄せる

Windows本体に直接いろいろ入れると、PATH、npm、pip、Git設定などが混ざりやすい。

そのため、開発作業やCLIツールはWSL側に寄せる。

想定は以下。

```
Windows本体
  ├─ ブラウザ
  ├─ VS Code
  ├─ Docker Desktop
  └─ WSL2

WSL / Ubuntu
  ├─ Git
  ├─ Node.js
  ├─ npm
  ├─ Codex CLI
  ├─ Claude Code
  └─ 開発用sandbox
```

Windows本体はなるべく汚さず、作業はWSL側で行う。

---

## 実験はDockerで隔離する

Dockerは、単なる便利ツールとしてではなく、検証環境を閉じ込めるために使う。

たとえばPythonを使いたい場合でも、Windows本体にPythonを入れるのではなく、まずはDockerコンテナで動かす。

```
docker run --rm -it python:3.12 bash
```

あるいは、Windows側の検証用フォルダだけをコンテナに渡す。

```
$p="C:\AI-LAB\workspace"
docker run --rm -it `
  --mount type=bind,source=$p,target=/workspace `
  python:3.12 bash
```

この場合、PythonはWindows本体にインストールされるのではなく、Dockerコンテナ内で動く。

これにより、Windows本体をできるだけ清潔に保てる。

---

## AIエージェントに触らせる場所を限定する

AIエージェントに触らせる場所は、明確に限定する。

今回の基本作業場所は以下。

または、WSL側の専用sandbox。

AIエージェントに触らせてよいものは、以下に限定する。

* `C:\AI-LAB\workspace`
* WSL内の専用sandbox
* Dockerコンテナ内の作業ディレクトリ
* 検証用GitHubリポジトリ
* ダミーデータ

逆に、触らせないものは以下。

!

* ユーザー日常データ領域
* クラウド同期フォルダ
* 本番データ置き場
* 個人ファイル領域
* メインPC由来のファイル
* 本物のAPIキー
* パスワード
* 個人情報
* 仕事の実データ

AIエージェントに渡すのは、必ず検証用の檻の中だけにする。

---

## AI-LABフォルダを作る

Windows側には、検証専用フォルダとして `C:\AI-LAB` を作る。

想定する構成は以下。

```
C:\AI-LAB\
  workspace\
  downloads\
  logs\
  docker\
  DESIGN_POLICY.md
```

最低限必要なのは、以下。

```
C:\AI-LAB\
  workspace\
  DESIGN_POLICY.md
```

`workspace` は、DockerやAIエージェントに渡してよい作業場所。

`DESIGN_POLICY.md` は、この端末の設計方針をまとめるファイル。

---

## DESIGN\_POLICY.md を作る

今後、別のAIや別アカウントのChatGPTに相談する時にも方針がブレないように、設計方針をファイルにしておく。

`C:\AI-LAB\DESIGN_POLICY.md` に、以下のような内容を書く。

```
# AI-LAB Design Policy

この端末はAIエージェント検証専用機として使う。

## 合言葉

本体は薄く。  
作業はWSL。  
実験はDocker。  
触らせるのは檻の中だけ。

## Windows本体に置いてよいもの

- ブラウザ
- VS Code
- Docker Desktop
- WSL2
- AIクライアントアプリ
- 必要最低限の認証系

## Windows本体に原則入れないもの

- Python
- Node.js
- npm
- Git
- Codex CLI
- Claude Code
- 開発用CLIツール

## 開発・CLIツールを置く場所

- WSL / Ubuntu
- Dockerコンテナ
- 専用sandbox

## AIエージェントに触らせてよい場所

- 検証用workspace
- WSL内の専用sandbox
- Dockerコンテナ内の作業ディレクトリ
- 検証用GitHubリポジトリ
- ダミーデータのみ

## AIエージェントに触らせない場所

- ユーザー日常データ領域
- クラウド同期フォルダ
- 本番データ置き場
- 個人ファイル領域
- 本物のAPIキー
- パスワード
- 個人情報
- 実運用データ
```

このファイルを、今後の憲法として扱う。

---

## 一度つまずいた点

今回、途中でCodex CLIやPythonをどこに入れるべきか分からなくなった。

WindowsのcmdやPowerShellでCodex CLIを試した際、実行環境による挙動差があり、構成整理の必要性を感じた。

また、Pythonについても、「Windows本体へ導入した」のか、「Dockerコンテナ内で一時的に動かしているだけ」なのかを途中で混同しやすかった。

整理すると、以下の違いが重要だった。

```
Pythonインストーラーを実行する
→ Windows本体にPythonが入る可能性がある

docker run python:3.12 bash
→ Dockerコンテナ内でPythonが動くだけ
→ Windows本体にPythonを入れているわけではない
```

また、GitHubについても同様。

```
GitHubアカウントを作る
→ Windows本体には何も入らない

ブラウザでGitHubにログインする
→ ブラウザにログイン情報が残るだけ

GitHub Desktopを入れる
→ Windows本体にアプリが入る

Gitを入れる
→ Windows本体にCLIツールが入る
```

「アカウントを作った」「ログインした」「アプリを入れた」「CLIツールを入れた」「Dockerで一時的に動かした」は、分けて考える必要がある。

---

## PowerShellでコマンドの場所を調べる

Windowsでツールが入っているか確認する時、PowerShellでは `where` ではなく `where.exe` を使う。

```
where.exe python
where.exe py
where.exe node
where.exe npm
where.exe git
where.exe codex
```

PowerShellでは `where` が別の意味で扱われることがあるため、Windowsの検索コマンドとして使う場合は `where.exe` と書く。

PowerShell流に確認するなら、以下でもよい。

```
Get-Command python
Get-Command node
Get-Command npm
Get-Command git
Get-Command codex
```

---

## 現在の状態

一度セットアップ途中で設計方針が曖昧になったため、不要なアプリや残骸を整理してやり直すことにした。

今後は、以下の順番で再構築する。

1. `C:\AI-LAB` を作成する
2. `DESIGN_POLICY.md` を置く
3. WSL2 を導入する
4. Docker Desktop を導入する
5. Docker の `hello-world` を確認する
6. Pythonコンテナで `workspace` のマウントを確認する
7. WSL側に Git / Node.js / Codex CLI を入れる
8. `agent-sandbox` で最小実験を行う

最初のAIエージェント実験は、小さく始める。

```
agent-sandbox の README.md に
Hello AI Agent
と1行追記させる
```

最初から複雑な自動化を目指さない。

まずは、AIエージェントに檻の中の1ファイルだけ触らせる。

その差分を確認し、戻せることを確認する。

それが最初のゴール。

---

## 今後やること

今後は、以下を順番に進める。

### 第1段階

* WSL2の導入
* Docker Desktopの導入
* `C:\AI-LAB\workspace` の作成
* Dockerコンテナでworkspaceをマウント確認

### 第2段階

* WSL側にGitを入れる
* WSL側にNode.js / npmを入れる
* WSL側にCodex CLIを入れる
* `agent-sandbox` を作る

### 第3段階

* Codex CLIにREADMEを編集させる
* 差分を確認する
* Gitで変更を管理する

### 第4段階

* Claude Codeを試す
* ブラウザAIエージェントを試す
* Zenn記事や作業ログの整理を半自動化する

---

## まとめ

AIエージェント検証用PCを作る時は、いきなりツールを入れる前に、設計思想を決めることが大事だと分かった。

今回の方針は以下。

Windows本体には、ブラウザ、VS Code、Docker Desktop、WSL2、AIクライアントアプリ程度にとどめる。

Python、Node.js、Git、Codex CLI、Claude Codeなどの開発ツールは、原則としてWSL側に置く。

AIエージェントに触らせるのは、検証用フォルダ、専用sandbox、Dockerコンテナ内だけにする。

最初の目標は、大きな自動化ではなく、`README.md` を1行変更させること。

そこから少しずつ、安全に検証範囲を広げていく。

---

## 補足

この記事は、筆者が実際にAIエージェント検証用端末を構築する中で得た作業ログや試行錯誤をもとに、ChatGPTとの対話を通じて整理・執筆したものです。

手順や設計方針は、実際に試した内容と、その中で得られた学びをベースにまとめています。
