---
id: "2026-05-24-aiエージェント検証用pcを作るメモ⑤ubuntu側にnodejsとnpmを入れる-01"
title: "AIエージェント検証用PCを作るメモ⑤：Ubuntu側にNode.jsとnpmを入れる"
url: "https://zenn.dev/imaginarygate/articles/3dd4ccb4982763"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "GPT", "zenn"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回は、Ubuntu側の `~/agent-sandbox` をGit管理下に置き、`README.md` を初回コミットした。

今回は、Ubuntu側に Node.js と npm を入れる。

この記事では、Windows本体には Node.js を入れず、Ubuntu / WSL側にだけ導入する。  
AIエージェントやCLIツールを動かすための土台として、Node.js / npm を使える状態にする。

今回のゴールは以下。

* Ubuntu側で `nvm` を使えるようにする
* Node.js LTS をインストールする
* `node -v` でNode.jsのバージョンを確認する
* `npm -v` でnpmのバージョンを確認する
* Windows本体ではなく、WSL側にNode.js環境を作る

Codex CLIは、この記事ではまだ入れない。  
まずは Node.js / npm の土台を整える。

---

## 前提

環境は以下。

* OS: Windows 11
* WSL環境: Ubuntu
* 作業場所: `~/agent-sandbox`
* 方針: Windows本体には開発ツールをなるべく入れず、WSL / Docker側に寄せる

基本方針はこれまでと同じ。

前回までに、以下は完了している。

* 作業用Ubuntuのインストール
* `~/agent-sandbox` の作成
* Gitのインストール
* `README.md` の初回コミット

今回は、Ubuntu側にNode.jsとnpmを用意する。

---

## なぜ nvm を使うのか

Node.jsの入れ方はいくつかある。

たとえば、Ubuntuの `apt` で入れる方法もある。

```
sudo apt install nodejs npm
```

ただし、今回はこの方法ではなく、`nvm` を使うことにした。

`nvm` は、Node.jsのバージョンを管理するためのツール。  
Node.jsのバージョンを切り替えたり、LTS版を選んで入れたりしやすい。

今回の方針では、Windows本体にNode.jsを入れない。  
Ubuntu側に閉じて、必要な範囲だけでNode.jsを使えるようにする。

```
Windows本体
→ Node.jsは入れない

Ubuntu / WSL
→ nvmでNode.jsを入れる
```

---

## agent-sandbox に移動する

Ubuntuを開き、作業場所に移動する。

以下のように表示されればOK。

```
/home/ユーザー名/agent-sandbox
```

今回のNode.js / npm導入自体は、`agent-sandbox` の中だけに入るわけではない。  
`nvm` はユーザーのホームディレクトリ配下に導入される。

ただし、作業の流れを分かりやすくするため、今回も `agent-sandbox` にいる状態で進める。

---

## nvmをインストールする

Ubuntu側で、以下を実行する。

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
```

このコマンドで、`nvm` のインストールスクリプトを取得して実行する。

もし `curl` が入っていないと言われた場合は、先に以下を実行する。

```
sudo apt update
sudo apt install curl -y
```

---

## nvmを読み込む

インストール直後は、現在開いているシェルで `nvm` がまだ使えない場合がある。

そのため、以下を実行して `nvm` を読み込む。

その後、バージョンを確認する。

バージョン番号が表示されればOK。

例：

環境によって表示されるバージョンは異なる場合がある。  
`nvm --version` で数字が表示されれば、`nvm` は使える状態になっている。

---

## nvmコマンドが見つからない場合

もし以下のような表示が出た場合。

まずは、もう一度読み込みを実行する。

それでもだめな場合は、Ubuntuを一度閉じて開き直す。

または、以下を実行する。

その後、もう一度確認する。

---

## Node.js LTSをインストールする

`nvm` が使えるようになったら、Node.jsのLTS版をインストールする。

LTSは Long Term Support の略。  
長期サポート版として扱われるNode.jsを入れる。

インストールが終わるまで待つ。

---

## Node.jsとnpmのバージョンを確認する

Node.jsのインストール後、以下を実行する。

それぞれバージョン番号が表示されれば成功。

例：

表示されるバージョンは環境やタイミングによって異なる。  
大事なのは、`node -v` と `npm -v` の両方でバージョン番号が出ること。

これで、Ubuntu側でNode.jsとnpmが使える状態になった。

---

## どこにNode.jsが入ったのか確認する

念のため、`node` と `npm` の場所を確認する。

`nvm` 経由で入っている場合、だいたい以下のように `.nvm` 配下のパスが表示される。

```
/home/ユーザー名/.nvm/versions/node/...
```

これは、Windows本体ではなく、Ubuntu側のユーザー環境にNode.jsが入っているということ。

今回の方針に合っている。

---

## Windows本体に入れたわけではない

今回入れたNode.js / npmは、Ubuntu側の環境で使うもの。

Windows本体にNode.jsをインストールしたわけではない。

整理すると、以下。

```
Windows本体
→ Node.js / npm は入れない

Ubuntu / WSL
→ nvm経由でNode.js / npm を使う
```

第1回で決めた「Windows本体はなるべく薄くする」という方針に沿っている。

---

## Git管理への影響

今回の作業では、`agent-sandbox` 内の `README.md` などを変更していない。

`nvm` やNode.jsは、主にホームディレクトリ配下に導入される。

そのため、`agent-sandbox` のGit管理には基本的に変化はない。

確認するなら、`agent-sandbox` 内で以下を実行する。

```
cd ~/agent-sandbox
git status
```

前回の初回コミット後からファイルを変更していなければ、以下のような表示になる。

```
nothing to commit, working tree clean
```

もし何か変更が出ている場合は、内容を確認してから進める。

---

## 今回ハマりやすい点

### nvmはインストール直後に読み込みが必要な場合がある

`nvm` をインストールした直後に、すぐ `nvm --version` を実行すると、コマンドが見つからない場合がある。

その場合は、以下を実行する。

または、Ubuntuを開き直す。

### nodeとnpmはセットで確認する

Node.jsだけでなく、npmも使えるか確認する。

両方のバージョンが出ることを確認する。

### Windows側に入ったわけではない

今回のNode.js / npmはUbuntu側に入っている。

WindowsのPowerShellで `node -v` を実行しても、同じように使えるとは限らない。

このシリーズでは、開発ツールは原則としてUbuntu側に寄せる。

### Codex CLIはまだ入れない

この記事では、Node.js / npmの導入まで。

Codex CLIはまだ入れない。

次の段階で、インストール方式や認証、触らせるディレクトリを確認しながら進める。

---

## 今回できたこと

今回できたことは以下。

* Ubuntu側に `nvm` をインストールした
* `nvm --version` でnvmの導入を確認した
* `nvm install --lts` でNode.js LTSをインストールした
* `node -v` でNode.jsのバージョンを確認した
* `npm -v` でnpmのバージョンを確認した
* Windows本体ではなく、Ubuntu側にNode.js / npm環境を作った

これで、Codex CLIなどのNode.js系ツールを試すための土台ができた。

---

## 次回やること

次回は、いよいよCodex CLIの導入に進む。

ただし、いきなり動かすのではなく、まず以下を確認する。

* Codex CLIのインストール方式
* 認証方法
* どのディレクトリで実行するか
* `agent-sandbox` の中だけを触らせる運用
* Gitで差分を確認する流れ

最初の実験は、小さく始める。

```
agent-sandbox の README.md に
Hello AI Agent
と1行追記させる
```

AIエージェントに触らせるのは、まず `~/agent-sandbox` の中だけにする。

---

## まとめ

この記事では、Ubuntu側に `nvm` を入れ、Node.js LTSとnpmを使える状態にした。

今回のポイントは以下。

これで、AIエージェント系CLIを試すための土台がまた一段整った。

次回は、Codex CLIの導入と、`agent-sandbox` 内での最小実験に進む。

---

## 補足

この記事は、筆者が実際にAIエージェント検証用端末を構築する中で得た作業ログや試行錯誤をもとに、ChatGPTとの対話を通じて整理・執筆したものです。

手順や設計方針は、実際に試した内容と、その中で得られた学びをベースにまとめています。
