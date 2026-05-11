---
id: "2026-05-10-aiエージェント検証用pcを作るwsl2とdocker-desktop導入編-01"
title: "AIエージェント検証用PCを作る：WSL2とDocker Desktop導入編"
url: "https://zenn.dev/imaginarygate/articles/f8282f8e953f1e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "GPT", "Python", "zenn"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回は、AIエージェント検証用PCを作る前に、設計方針を決めた。

合言葉は以下。

この記事では、その方針に沿って、Windows 11環境にWSL2とDocker Desktopをインストールし、検証用workspaceをDockerコンテナにマウントするところまで進める。

この記事のゴールは、以下。

* WSL2が使える状態になっている
* Docker Desktopが動く
* `docker run hello-world` が成功する
* `C:\AI-LAB\workspace` をDockerコンテナに渡せる
* PythonをWindows本体ではなく、Dockerコンテナ内で動かせる

Codex CLIやClaude Codeは、この記事ではまだ入れない。  
まずはAIエージェント検証用PCの土台だけを作る。

---

## 前提

環境は以下。

* OS: Windows 11
* 用途: AIエージェント検証専用機
* 方針: Windows本体には開発ツールをなるべく入れず、WSL / Docker側に寄せる

前回の記事で決めた通り、Windows本体はなるべく薄く保つ。

Windows本体に置いてよいものは、以下。

* ブラウザ
* VS Code
* Docker Desktop
* WSL2
* AIクライアントアプリ
* 必要最低限の認証系アプリ

AIクライアントアプリの例としては、ChatGPT Desktop、Claude Desktopなどを想定している。

一方で、以下は原則としてWindows本体には入れない。

* Python
* Node.js
* npm
* Git
* Codex CLI
* Claude Code
* その他の開発用CLIツール

この記事ではPythonを使う場面があるが、Windows本体にPythonを入れるのではなく、Dockerコンテナ内のPythonを使う。

---

## やること

作業内容は以下。

1. `C:\AI-LAB` を作る
2. `C:\AI-LAB\workspace` を作る
3. `DESIGN_POLICY.md` を置く
4. WSL2の状態を確認する
5. Docker Desktopをインストールする
6. `docker run hello-world` を実行する
7. Pythonコンテナで `workspace` をマウントする

最終的に、以下の構成を目指す。

```
Windows本体
  ├─ Docker Desktop
  ├─ WSL2
  └─ C:\AI-LAB\
       ├─ workspace\
       └─ DESIGN_POLICY.md

Dockerコンテナ
  └─ /workspace
       ↑
       C:\AI-LAB\workspace をマウント
```

---

## AI-LABフォルダを作る

まず、Windows側に検証専用フォルダを作る。

```
C:\AI-LAB
C:\AI-LAB\workspace
```

この `workspace` が、DockerコンテナやAIエージェントに渡してよい作業場所になる。

普段使いの `Documents` や `Downloads` は直接使わない。  
検証用の場所を明確に分ける。

最小構成は以下。

```
C:\AI-LAB\
  workspace\
  DESIGN_POLICY.md
```

必要に応じて、あとから以下を追加してもよい。

```
C:\AI-LAB\
  downloads\
  logs\
  docker\
```

最初は最小構成でよい。

---

## DESIGN\_POLICY.mdを置く

次に、`C:\AI-LAB\DESIGN_POLICY.md` を作る。

これは、この端末の設計方針をまとめたファイル。

中身は以下のようにした。

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

このファイルは、別のAIに相談するときにも使う。

別アカウントのChatGPTやClaudeに作業を相談する場合は、最初にこの方針を渡しておく。

---

## WSL2の状態を確認する

PowerShellを開いて、WSLの状態を確認する。

Ubuntuが表示され、VERSIONが `2` になっていればOK。

例：

```
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

もしWSLが未導入の場合は、管理者PowerShellで以下を実行する。

必要に応じて、PCを再起動する。

Docker DesktopはWSL2と連携して使うため、ここが整っていることを先に確認しておく。

---

## Docker Desktopをインストールする

Docker Desktop for Windowsをインストールする。

インストール後、Docker Desktopを起動し、WSL2ベースのエンジンを使う設定になっていることを確認する。

確認場所は以下。

```
Docker Desktop
→ Settings
→ General
→ Use the WSL 2 based engine
```

ここにチェックが入っていればOK。

その後、PowerShellで以下を実行する。

バージョンが表示されれば、Dockerコマンドが使える状態になっている。

例：

```
Docker version xx.x.x, build xxxxxxx
```

---

## Dockerの動作確認をする

次に、Dockerの基本動作を確認する。

PowerShellで以下を実行する。

成功すると、以下のようなメッセージが表示される。

これが表示されれば、Docker Desktopの基本動作は成功。

この時点で、Windows本体にPythonやNode.jsを入れなくても、Dockerコンテナを使って検証環境を動かせる土台ができた。

---

## workspaceをPythonコンテナにマウントする

次に、Windows側の `C:\AI-LAB\workspace` をDockerコンテナに渡す。

PowerShellで、まず変数にパスを入れる。

次に、Python 3.12のコンテナを起動し、`C:\AI-LAB\workspace` をコンテナ内の `/workspace` にマウントする。

```
docker run --rm -it `
  --mount type=bind,source=$p,target=/workspace `
  python:3.12 bash
```

コンテナに入ったら、以下を実行する。

```
cd /workspace
pwd
python --version
```

`pwd` の結果が以下になればOK。

また、`python --version` でPython 3.12系が表示されれば成功。

ここで重要なのは、PythonがWindows本体に入っているわけではないということ。

このPythonは、Dockerコンテナ内で動いている。

つまり、Windows本体を汚さずに、Python環境を一時的に使えている。

---

## Windowsパス指定では --mount を使った

最初は短い `-v` オプションでマウントしようとしたが、Windowsのパス指定まわりでうまくいかなかった。

Windowsパスには `C:\...` のようにコロンが含まれるため、Dockerのボリューム指定と混ざって分かりづらくなりやすい。

そのため、今回は `--mount` を使って、`type=bind`、`source`、`target` を明示する形にした。

```
$p="C:\AI-LAB\workspace"

docker run --rm -it `
  --mount type=bind,source=$p,target=/workspace `
  python:3.12 bash
```

`--mount` の各指定は、以下の意味になる。

* `type=bind`: ホスト側のフォルダをコンテナに渡す
* `source=$p`: Windows側のフォルダ
* `target=/workspace`: コンテナ内のマウント先

`-v` でも同じことはできるが、今回はトラブルを避けるため、指定内容が分かりやすい `--mount` を使った。

---

## 今回ハマりやすい点

### PythonをWindows本体に入れたわけではない

以下のコマンドは、Windows本体にPythonをインストールするものではない。

```
docker run --rm -it `
  --mount type=bind,source=$p,target=/workspace `
  python:3.12 bash
```

これは、Python入りのDockerイメージを使って、コンテナ内でPythonを動かしているだけ。

つまり、以下のように分けて考える必要がある。

```
Pythonインストーラーを実行する
→ Windows本体にPythonが入る可能性がある

docker run python:3.12 bash
→ Dockerコンテナ内でPythonが動く
→ Windows本体にPythonを入れているわけではない
```

### PowerShellでは複数行コマンドにバッククォートを使う

PowerShellでコマンドを複数行に分ける場合は、行末にバッククォートを使う。

```
docker run --rm -it `
  --mount type=bind,source=$p,target=/workspace `
  python:3.12 bash
```

1行で書くなら、以下でもよい。

```
docker run --rm -it --mount type=bind,source=$p,target=/workspace python:3.12 bash
```

スマホを見ながら手入力する場合は、1行版の方が分かりやすい場合もある。

### python:3.12ではbashを使える

この記事では、`python:3.12` イメージを使っているため、`bash` で起動している。

```
docker run --rm -it python:3.12 bash
```

ただし、すべてのDockerイメージで `bash` が使えるとは限らない。

たとえば、Alpine系の軽量イメージでは `bash` が入っていない場合がある。  
その場合は `sh` を使うことがある。

```
docker run --rm -it イメージ名 sh
```

### AIエージェントにはまだ触らせない

この記事ではDockerとWSL2の土台確認まで。

Codex CLIやClaude CodeなどのAIエージェント系ツールは、まだ入れない。

まずは、AIエージェントに触らせてもよい場所を決める。  
そのうえで、最小のsandboxを作ってから試す。

---

## 今回できたこと

できたことは以下。

* `C:\AI-LAB` を作成した
* `C:\AI-LAB\workspace` を作成した
* `DESIGN_POLICY.md` を置いた
* WSL2の状態を確認した
* Docker Desktopを使える状態にした
* `docker run hello-world` が成功した
* `C:\AI-LAB\workspace` をPythonコンテナ内の `/workspace` としてマウントできた
* Windows本体にPythonを入れず、Dockerコンテナ内のPythonを使えた

これで、AIエージェント検証用PCの土台ができた。

---

## 次回やること

次回は、WSL側に開発用ツールを入れる。

予定は以下。

* WSL側にGitを入れる
* WSL側にNode.js / npmを入れる
* WSL側にCodex CLIを入れる
* `agent-sandbox` を作る
* Codex CLIに `README.md` を1行だけ編集させる
* 差分を確認する
* 変更を戻せることを確認する

最初のAIエージェント実験は、小さく始める。

```
agent-sandbox の README.md に
Hello AI Agent
と1行追記させる
```

いきなり大きな自動化はしない。

まずは、AIエージェントに檻の中の1ファイルだけ触らせる。

---

## まとめ

この記事では、Windows 11環境にWSL2とDocker Desktopを用意し、AIエージェント検証用のworkspaceをDockerコンテナにマウントした。

ポイントは以下。

第1回で決めた通り、方針は変えない。

この土台の上に、次回はCodex CLIをWSL側に入れて、最小のAIエージェント実験を行う。

---

## 補足

この記事は、筆者が実際にAIエージェント検証用端末を構築する中で得た作業ログや試行錯誤をもとに、ChatGPTとの対話を通じて整理・執筆したものです。

手順や設計方針は、実際に試した内容と、その中で得られた学びをベースにまとめています。
