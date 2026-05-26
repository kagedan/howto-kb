---
id: "2026-05-25-aiエージェント検証用pcを作るメモ⑥codex-cliでreadmeを編集してみる-01"
title: "AIエージェント検証用PCを作るメモ⑥：Codex CLIでREADMEを編集してみる"
url: "https://zenn.dev/imaginarygate/articles/64b61226a2c46d"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-05-25"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回は、Ubuntu側に `nvm` を入れ、Node.js LTS と npm を使える状態にした。

今回は、いよいよ Codex CLI を入れて、`~/agent-sandbox` 内の `README.md` を編集させてみる。

今回のゴールは以下。

* Ubuntu側に Codex CLI をインストールする
* Codex CLIにサインインする
* `~/agent-sandbox` の中だけでCodexを起動する
* `README.md` に `Hello AI Agent` を追記させる
* `git status` / `git diff` で差分を確認する
* 変更内容をコミットする

今回は、大きな自動化はしない。

最初の実験は、`README.md` に1行だけ追記させる。  
AIエージェントに触らせる場所も、`~/agent-sandbox` の中だけに限定する。

---

## 前提

環境は以下。

* OS: Windows 11
* WSL環境: Ubuntu
* 作業場所: `~/agent-sandbox`
* Node.js / npm: nvm経由でUbuntu側に導入済み
* Git: 導入済み
* `agent-sandbox`: Git管理済み

基本方針はこれまでと同じ。

今回は、この「檻」として作った `~/agent-sandbox` の中で、Codex CLIを試す。

---

## 作業場所に移動する

まず、Ubuntuを開いて `agent-sandbox` に移動する。

以下のように表示されればOK。

```
/home/ユーザー名/agent-sandbox
```

ここから先は、必ずこの `agent-sandbox` の中で作業する。

---

## Gitの状態を確認する

Codex CLIを動かす前に、Gitの状態を確認する。

ここでは、現在の作業状態を確認する。  
表示内容は、コミット履歴の有無やブランチ名によって異なる。

大事なのは、Codexに作業させる前の状態を一度見ておくこと。  
あとで `git status` や `git diff` を見たときに、Codexが何を変更したのか分かりやすくなる。

---

## Codex CLIをインストールする

Codex CLIは、前回導入した Node.js / npm を使ってインストールする。

Ubuntu側で、以下を実行する。

```
npm install -g @openai/codex
```

今回は、すでにUbuntu側に Node.js / npm を入れているため、npm経由でCodex CLIをインストールする。

インストール後、バージョンを確認する。

バージョン番号が表示されればOK。

---

## Codex CLIにサインインする

Codex CLIを使うには、認証が必要になる。

ブラウザでChatGPTにログインしていても、Ubuntu側のCodex CLIが自動でログイン済みになるわけではない。  
CLI側でも、別途サインインを行う。

今回は、ChatGPTアカウントでサインインした。

実行すると、ブラウザでサインインする流れになる。

環境によっては、追加の認証が求められる場合がある。  
このときは、表示されているURLが公式のものか確認してから進める。

サインインが完了すると、CLI側でもログイン済みのような表示が出る。

---

## Codexを起動する

`agent-sandbox` の中で、Codexを起動する。

Codexが起動すると、対話型のプロンプトが表示される。  
ここで自然文で指示を出せる。

初回起動時に、以下のような確認が出た。

```
Do you trust the contents of this directory?
Working with untrusted contents comes with higher risk of prompt injection.
Trusting the directory allows project-local config, hooks, and exec policies to load.
```

これは、「このディレクトリの中身を信頼してよいか」という確認。

今回の `~/agent-sandbox` は自分で作った検証用ディレクトリで、中身も `README.md` だけの小さな作業場。

そのため、今回は信頼して進めた。

---

## CodexにREADME.mdを編集させる

Codexが起動したら、最初の指示は小さくする。

今回は、以下のように依頼した。

```
README.md に Hello AI Agent という1行を追記してください。
```

いきなり複雑な作業はさせない。

最初は、Gitで差分を確認しやすいように、`README.md` に1行だけ追記させる。

---

## Ubuntuに戻る

Codexの対話画面からUbuntuの通常入力に戻るには、Codex内で以下を入力する。

または、

戻ると、以下のような通常のプロンプトに戻る。

```
ユーザー名@PC名:~/agent-sandbox$
```

もし戻り方が分からなくなった場合は、`/quit` または `/exit` を試す。

---

## git statusで変更を確認する

Codexに作業させたあと、すぐにGitの状態を確認する。

今回は、以下のような表示になった。

```
On branch master
Changes not staged for commit:
  modified: README.md

no changes added to commit
```

これは、`README.md` が変更されたという意味。

まだ `git add` されていないため、コミット対象には入っていない。

整理すると、以下。

```
modified: README.md
→ README.md が変更された

Changes not staged for commit
→ まだコミット対象には入っていない
```

この時点で、Codexが `README.md` を触ったことが分かる。

---

## git diffで差分を確認する

次に、実際に何が変わったのか確認する。

`README.md` に `Hello AI Agent` が追加されていればOK。

差分では、追加された行に `+` が付いて表示される。

例：

ここで、Codexが意図した変更だけを行っているか確認する。

問題なければコミットする。  
意図しない変更があれば、その時点で戻す。

---

## 変更をコミットする

差分に問題がなければ、`README.md` をステージングする。

状態を確認する。

`README.md` がコミット対象になっていればOK。

次に、コミットする。

```
git commit -m "Add Hello AI Agent"
```

これで、Codex CLIによる最初の変更をGitに記録できた。

---

## コミット履歴を確認する

コミット履歴を1行で確認する。

以下のように2行表示されれば成功。

```
英数字 Add Hello AI Agent
英数字 Initial commit
```

これで、最初のコミットと、Codexによる変更コミットの2つが記録された。

---

## --oneline と --online をまた間違えた

今回も、履歴確認で以下のように打ち間違えた。

すると、以下のようなエラーが出た。

```
fatal: unrecognized argument: --online
```

これは、Gitが `--online` というオプションを知らないという意味。

正しいコマンドは以下。

`oneline` は「1行表示」という意味。  
`online` ではない。

このエラーは、コミットが失敗したという意味ではない。  
履歴確認コマンドのオプション名を間違えただけ。

---

## 今回ハマりやすい点

### ブラウザでChatGPTにログインしただけでは終わりではない

Codex CLIを使うには、CLI側でも認証が必要になる。

ブラウザでChatGPTにログインしていても、Ubuntu側のCodex CLIが自動でログイン済みになるわけではない。

今回は `codex login` からサインインした。

### Trustの確認で慌てない

Codex起動時に、ディレクトリを信頼するか確認されることがある。

自分で作った `~/agent-sandbox` のような検証用ディレクトリなら、内容を確認したうえで進められる。

一方で、知らないリポジトリや外部から取得したコードでは、すぐにTrustしない。

### 最初の指示は小さくする

Codex CLIはファイルを編集できる。

そのため、最初から大きな作業を頼まない。

今回は、`README.md` に1行だけ追記させた。

小さな変更にすることで、`git diff` で確認しやすくなる。

### 変更後は必ずgit statusとgit diffを見る

AIエージェントにファイルを触らせたら、すぐに以下を確認する。

何が変わったのかを確認してから、コミットする。

---

## 今回できたこと

今回できたことは以下。

* Codex CLIをインストールした
* Codex CLIにサインインした
* `~/agent-sandbox` の中でCodexを起動した
* ディレクトリのTrust確認に対応した
* Codexに `README.md` を編集させた
* `git status` で変更を確認した
* `git diff` で差分を確認した
* `README.md` の変更をコミットした
* `git log --oneline` でコミット履歴を確認した

これで、Codex CLIを使った最小のAIエージェント実験ができた。

---

## 次回やること

次回は、Codex CLIをもう少し安全に使うための運用を整理する。

予定は以下。

* Codexに触らせる範囲を確認する
* Git差分確認の流れを固定する
* `.gitignore` を作る
* `.env` をGitに入れない準備をする
* APIキーや秘密情報を扱う前の最低限ルールを整理する

まだ大きな自動化には進まない。

まずは、Codexが触れる場所と、変更を戻せる仕組みを固める。

---

## まとめ

この記事では、Codex CLIをUbuntu側にインストールし、`~/agent-sandbox` 内の `README.md` を編集させた。

今回のポイントは以下。

これで、AIエージェントが実際にファイルを編集するところまで進めた。

次は、Codex CLIを安全に使い続けるための運用ルールを整える。

---

## 補足

この記事は、筆者が実際にAIエージェント検証用端末を構築する中で得た作業ログや試行錯誤をもとに、ChatGPTとの対話を通じて整理・執筆したものです。

手順や設計方針は、実際に試した内容と、その中で得られた学びをベースにまとめています。
