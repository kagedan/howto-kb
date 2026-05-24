---
id: "2026-05-23-aiエージェント検証用pcを作るメモubuntu側でgit管理を始める-01"
title: "AIエージェント検証用PCを作るメモ：Ubuntu側でGit管理を始める"
url: "https://zenn.dev/imaginarygate/articles/20b3ef2d7e233e"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "GPT", "zenn"]
date_published: "2026-05-23"
date_collected: "2026-05-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回は、作業用Ubuntuをインストールし、AIエージェント用の最小作業場所として `~/agent-sandbox` を作成した。

この記事では、その `agent-sandbox` をGit管理下に置き、`README.md` を初回コミットするところまで進める。

この記事は、実際に構築しながら整理した作業メモです。  
環境によって表示やエラー内容が異なる可能性があるため、必要に応じて追記・修正します。

今回のゴールは以下。

* Ubuntu側にGitをインストールする
* `git --version` でGitの導入を確認する
* `README.md` を作成する
* `agent-sandbox` をGit管理下に置く
* Gitのユーザー名とメールアドレスをローカル設定する
* `README.md` を初回コミットする
* `git log --oneline` でコミット履歴を確認する

Node.js / npm や Codex CLI は、この記事ではまだ入れない。  
まずは「変更を記録して戻せる作業場」を作る。

---

## 前提

環境は以下。

* OS: Windows 11
* WSL環境: Ubuntu
* 作業場所: `~/agent-sandbox`
* 方針: Windows本体には開発ツールをなるべく入れず、WSL / Docker側に寄せる

基本方針はこれまでと同じ。

前回までに、Ubuntu上に以下の作業場所を作成した。

今回は、このフォルダをGitで管理する。

---

## なぜGit管理を先に始めるのか

AIエージェントにファイルを触らせる前に、Git管理を始めておく。

理由は単純で、変更内容を確認し、必要なら戻せるようにするため。

AIエージェント系ツールは、ファイルの編集やコマンド実行ができる。  
便利な反面、何が変わったのか分からないまま進めると危ない。

そのため、最初にGitで管理しておく。

```
変更前の状態をコミットする
↓
AIエージェントに作業させる
↓
差分を見る
↓
問題があれば戻す
```

まずは、`README.md` だけを管理する小さなGitリポジトリから始める。

---

## agent-sandbox に移動する

Ubuntuを開き、作業場所に移動する。

以下のように表示されればOK。

```
/home/ユーザー名/agent-sandbox
```

ここから先は、この `agent-sandbox` の中で作業する。

---

## Gitをインストールする

まず、パッケージ情報を更新する。

次にGitをインストールする。

インストール後、バージョンを確認する。

今回は以下のように表示された。

バージョン番号は環境によって異なる。  
`git version ...` と表示されれば、Gitは使える状態になっている。

---

## Not Upgrading が出た場合

`apt` 実行後に、以下のような表示が出ることがある。

```
Summary:
Upgrading: 0, Installing: 0, Removing: 0, Not Upgrading: 4
```

これは、更新されていないパッケージがあるという表示。

今回のGitインストール自体には影響しなかったため、そのまま進めた。

この記事では、Gitの導入と初回コミットを優先する。  
保留パッケージの詳細確認は、必要になったタイミングで別途扱う。

---

## README.md を確認する

`agent-sandbox` の中身を確認する。

`README.md` が表示されればOK。

もし `README.md` がない場合は、ここで作成する。

```
echo "# agent-sandbox" > README.md
cat README.md
```

以下のように表示されれば成功。

もう一度確認する。

これで、Git管理する最初のファイルができた。

---

## git init でGit管理を始める

`agent-sandbox` の中で、Git管理を開始する。

次に状態を確認する。

`README.md` が `Untracked files` に表示されればOK。

例：

```
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md
```

`Untracked files` は、Gitがまだ追跡していないファイルという意味。

この段階では、`README.md` は存在しているが、まだGitには登録されていない。

---

## Gitのユーザー名とメールアドレスを設定する

コミットする前に、Gitのユーザー名とメールアドレスを設定する。

今回は、まず `agent-sandbox` の中だけで使うローカル設定にした。

```
git config user.name "sandbox"
git config user.email "sandbox@example.local"
```

確認する。

```
git config user.name
git config user.email
```

以下のように表示されればOK。

```
sandbox
sandbox@example.local
```

今回は `--global` を付けていない。  
そのため、この設定は現在のリポジトリ内だけに適用される。

---

## README.md をステージングする

次に、`README.md` をGitに登録する準備をする。

状態を確認する。

`README.md` が `Changes to be committed` に表示されればOK。

例：

```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   README.md
```

これで、`README.md` は次のコミット対象になった。

---

## 初回コミットする

初回コミットを作成する。

```
git commit -m "Initial commit"
```

成功すると、コミットが作成される。

この時点で、`README.md` の最初の状態がGitに記録された。

---

## コミット履歴を確認する

コミット履歴を1行で確認する。

以下のように表示されれば成功。

先頭の英数字はコミットIDの一部。  
環境によって表示される文字列は異なる。

---

## --oneline と --online の打ち間違いに注意

今回、コミット履歴を確認する時に、以下のように打ち間違えた。

すると、以下のようなエラーが出た。

```
fatal: unrecognized argument: --online
```

これは、Gitが `--online` というオプションを知らないという意味。

正しいコマンドは以下。

`oneline` は「1行表示」という意味。  
`online` ではない。

---

## 今回ハマりやすい点

### README.md がない場合は作ればいい

`ls` で確認した時に `README.md` が表示されなくても、失敗ではない。

その場で作ればいい。

```
echo "# agent-sandbox" > README.md
```

そのあと `cat README.md` や `ls` で確認する。

### Gitのメールアドレスは慎重に扱う

Gitのコミットには、ユーザー名とメールアドレスが記録される。

公開リポジトリに上げる場合、個人メールが見える可能性がある。

そのため、今回はローカル実験用として以下を使った。

```
sandbox
sandbox@example.local
```

GitHubに上げる段階では、GitHubの noreply メールなどを検討する。

### --oneline は online ではない

`git log --oneline` は、かなり見間違えやすい。

```
正しい：--oneline
間違い：--online
```

エラーが出ても、コミットが壊れたわけではない。  
オプション名を打ち間違えただけ。

---

## 今回できたこと

今回できたことは以下。

* Gitをインストールした
* `git --version` でGitの導入を確認した
* `README.md` を作成した
* `git init` で `agent-sandbox` をGit管理下に置いた
* Gitのユーザー名とメールアドレスをローカル設定した
* `README.md` を初回コミットした
* `git log --oneline` でコミット履歴を確認した

これで、`agent-sandbox` に変更履歴を残せるようになった。

---

## 次回やること

次回は、Ubuntu側に Node.js / npm を入れる。

予定は以下。

* Node.js の導入方法を決める
* Node.js をインストールする
* npm を確認する
* `node -v` / `npm -v` でバージョン確認を行う

Codex CLIは、Node.js / npm の土台が整ってから扱う。

焦って一気に進めず、まずはAIエージェントを動かすための開発環境を一つずつ整えていく。

---

## まとめ

この記事では、Ubuntu側の `~/agent-sandbox` をGit管理下に置き、`README.md` を初回コミットした。

今回のポイントは以下。

これで、今後AIエージェントがファイルを編集した時に、差分を確認しやすくなる。

次回は、Ubuntu側に Node.js / npm を入れて、Codex CLI導入の前段階を整える。

---

## 補足

この記事は、筆者が実際にAIエージェント検証用端末を構築する中で得た作業ログや試行錯誤をもとに、ChatGPTとの対話を通じて整理・執筆したものです。

手順や設計方針は、実際に試した内容と、その中で得られた学びをベースにまとめています。
