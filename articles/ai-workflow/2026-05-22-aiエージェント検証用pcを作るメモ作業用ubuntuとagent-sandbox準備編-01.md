---
id: "2026-05-22-aiエージェント検証用pcを作るメモ作業用ubuntuとagent-sandbox準備編-01"
title: "AIエージェント検証用PCを作るメモ：作業用Ubuntuとagent-sandbox準備編"
url: "https://zenn.dev/imaginarygate/articles/7db04b8bd98d5f"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "GPT", "zenn"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回は、Windows 11環境でDocker Desktopを使い、検証用workspaceをDockerコンテナにマウントするところまで進めた。

この記事では、WSL側に「作業用Ubuntu」を用意し、AIエージェントが触れる最小の作業場所として `~/agent-sandbox` を作るところまで進める。

この記事は、実際に構築しながら整理した作業メモです。  
環境によって表示やエラー内容が異なる可能性があるため、必要に応じて追記・修正します。

前回の記事で分かった重要な点は、以下。

Docker Desktopを使うだけなら、`docker-desktop` があれば進められる。  
しかし、Git / Node.js / Codex CLI などをWSL側に入れて作業するには、別途「作業用Ubuntu」が必要になる。

この記事のゴールは以下。

* 作業用Ubuntuをインストールする
* Ubuntuの初回セットアップを行う
* `sudo apt update` / `sudo apt upgrade -y` を実行する
* aptの取得先エラーに対応する
* `~/agent-sandbox` を作る
* `README.md` を作る

Codex CLIは、この記事ではまだ入れない。  
まずは、AIエージェントに触らせるための小さな作業場所を作る。

---

## 前提

環境は以下。

* OS: Windows 11
* 用途: AIエージェント検証専用機
* 方針: Windows本体には開発ツールをなるべく入れず、WSL / Docker側に寄せる

基本方針は、第1回から変わらない。

前回までに、Docker DesktopとDockerコンテナの動作確認は済んでいる。

今回は、WSL側の作業場を作る。

---

## docker-desktop と Ubuntu は別物

PowerShellで以下を実行する。

最初に確認した時点では、以下のように `docker-desktop` だけが表示されていた。

```
  NAME              STATE           VERSION
* docker-desktop    Stopped         2
```

この表示を見て、WSL側の作業環境もできていると思ってしまった。

しかし、`docker-desktop` はDocker Desktopが内部で使うWSL環境であり、普段の作業に使うUbuntuではない。

整理すると、以下。

```
WSL2
├─ docker-desktop   # Docker Desktop用
└─ Ubuntu           # 作業用
```

つまり、この時点では以下の状態だった。

```
WSL2：有効
Docker Desktop用のWSL環境：あり
作業用Ubuntu：まだない
```

そのため、この記事では作業用Ubuntuを追加する。

---

## 作業用Ubuntuをインストールする

PowerShellを管理者として開き、まずインストール可能なディストリビューションを確認する。

一覧に `Ubuntu` が表示されることを確認する。

次に、Ubuntuをインストールする。

インストール後、再起動を求められた場合はPCを再起動する。

再起動後、スタートメニューから `Ubuntu` を起動する。  
または、PowerShellから以下でも起動できる。

---

## Ubuntuの初回セットアップを行う

Ubuntuを初回起動すると、ユーザー名とパスワードの設定を求められる。

```
Enter new UNIX username:
New password:
Retype new password:
```

ここで作成するのは、Ubuntu内で使うユーザー名とパスワード。  
Windowsのアカウントとは別のものとして考えてよい。

また、途中でメトリクス（活動記録や統計データ）収集について聞かれた。

```
Would you like to opt-in to platform metrics collection (Y/n)?
```

今回は、外部へのデータ送信をさせたくないため、`n` を選んだ。

---

## Ubuntuが追加されたことを確認する

PowerShellで、もう一度WSLの一覧を確認する。

Ubuntuが表示され、VERSIONが `2` になっていればOK。

例：

```
  NAME              STATE           VERSION
* Ubuntu            Running         2
  docker-desktop    Stopped         2
```

`Ubuntu` が `Stopped` になっていても、VERSIONが `2` であれば問題ない。  
起動していないだけで、必要な時に起動できる。

---

## Ubuntu側で現在地を確認する

Ubuntuを開いたら、まず現在地を確認する。

以下のように表示されれば、Ubuntu内のホームディレクトリにいる。

ここから先は、PowerShellではなくUbuntu側で作業する。

---

## apt update を実行する

Ubuntuのパッケージ情報を更新する。

パスワードを聞かれたら、Ubuntu初回セットアップで作ったパスワードを入力する。

入力中は何も表示されない。  
そのまま入力してEnterを押せばよい。

---

## apt update で Warning が出た

結論から言うと、`apt update` のWarningは致命的なエラー（Fatal Error）ではなく警告（Warning）であった  
今回の環境では、取得先を日本ミラーとHTTPSに変更することで解消できた。

最初に `sudo apt update` を実行したところ、以下のようなWarningが大量に表示された。

```
Warning: Failed to fetch http://archive.ubuntu.com/ubuntu/...
Some index files failed to download. They have been ignored, or old ones used instead.
```

これは、Ubuntuが更新リストを取りに行ったものの、一部の取得に失敗したという意味。

この時点で、PCやUbuntuが壊れたわけではない。

まずはネットワークが通っているか確認した。

通信自体は通っていたため、ネット接続そのものではなく、aptの取得先まわりの問題と判断した。

---

## aptの取得先を日本ミラーとHTTPSに変更する

今回の環境では、`archive.ubuntu.com` への接続で失敗していたため、取得先を日本ミラーに変更した。

まず、現在の設定ファイルを確認する。

```
ls /etc/apt/sources.list.d/
```

今回の環境では、`/etc/apt/sources.list.d/ubuntu.sources` が使われていた。  
これはUbuntu 24.04系などで使われるDEB822形式の `.sources` ファイル。

`ubuntu.sources` がある場合は、以下を実行する。

```
sudo sed -i 's|http://archive.ubuntu.com/ubuntu|https://jp.archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources
sudo sed -i 's|http://security.ubuntu.com/ubuntu|https://jp.archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources
```

その後、再度更新する。

`sudo apt update` の結果、以下のような表示になった。

```
23 packages can be upgraded.
Run 'apt list --upgradable' to see them.
```

これは、更新リストの取得に成功し、更新できるパッケージがあるという意味。

---

## パッケージをアップグレードする

更新可能なパッケージがあったため、以下を実行する。

途中で文字が大量に流れるが、そのまま待つ。

以下のような表示が出ることがある。

```
Processing triggers for ...
```

これは、アップグレード後の関連処理を実行している表示。

入力待ちに戻り、以下のようなプロンプトが表示されれば完了。

または、末尾に `$` が出て入力できる状態になっていればOK。

---

## agent-sandbox を作る

次に、AIエージェント用の最小作業場所を作る。

Ubuntu側で以下を実行する。

```
mkdir -p ~/agent-sandbox
cd ~/agent-sandbox
pwd
```

以下のように表示されれば成功。

```
/home/ユーザー名/agent-sandbox
```

この `agent-sandbox` は、今後Codex CLIなどに触らせるための最小作業場所として使う。

いきなり大事なファイルや普段使いのフォルダを触らせない。  
まずは、この小さな檻の中だけで試す。

---

## README.md を作る

最後に、テスト用の `README.md` を作る。

```
echo "# agent-sandbox" > README.md
cat README.md
```

以下のように表示されれば成功。

これで、Ubuntu上にAIエージェント用の最小作業場所ができた。

---

## 今回ハマりやすい点

### docker-desktopだけでは作業用Ubuntuではない

`wsl -l -v` で `docker-desktop` が表示されていると、WSLの作業環境も整っているように見える。

しかし、`docker-desktop` はDocker Desktop用の環境。  
GitやNode.jsなどを入れて作業するには、別途Ubuntuを入れる必要がある。

```
docker-desktop がある
→ Docker Desktop用のWSL環境はある

Ubuntu がある
→ 作業用のWSL環境がある
```

この違いは、最初かなり分かりづらかった。

### Ubuntuのパスワード入力は表示されない

`sudo apt update` などでパスワードを求められた時、入力しても何も表示されない。

これは正常な挙動。

何も出ないからといって、入力できていないわけではない。

### apt update の Warning は即致命傷ではない

`Some index files failed to download` のようなWarningが出ても、Ubuntuが壊れたわけではない。

今回のように、取得先を日本ミラーやHTTPSに変更すると解消する場合がある。

ただし、エラーの内容は環境によって異なるため、表示されたメッセージを確認しながら対応する。

### Codex CLIはまだ入れない

この記事では、作業用Ubuntuと `agent-sandbox` の準備まで。

Codex CLIはまだ入れない。

まずは、AIエージェントに触らせる場所を作るところで止める。

---

## 今回できたこと

今回できたことは以下。

* 作業用Ubuntuをインストールした
* Ubuntuの初回セットアップを行った
* `docker-desktop` と `Ubuntu` の違いを確認した
* `sudo apt update` を実行した
* aptの取得先エラーに対応した
* `sudo apt upgrade -y` を実行した
* `~/agent-sandbox` を作成した
* `README.md` を作成した

これで、WSL側にAIエージェント用の最小作業場所ができた。

---

## 次回やること

次回は、WSL側に開発用ツールを入れる。

予定は以下。

* Gitをインストールする
* Node.js / npmをインストールする
* バージョン確認を行う
* `agent-sandbox` 内でGit管理を始める

Codex CLIは、その次の段階で扱う予定。

焦って一気に進めず、まずはGitとNode.jsの土台を整える。

---

## まとめ

この記事では、作業用Ubuntuをインストールし、AIエージェント用の最小作業場所として `~/agent-sandbox` を作成した。

今回のポイントは以下。

前回まででDockerコンテナの土台を確認し、今回はWSL側の作業場を作った。

次回は、Ubuntu側にGitやNode.jsを入れて、AIエージェントを動かす準備を進める。

---

## 補足

この記事は、筆者が実際にAIエージェント検証用端末を構築する中で得た作業ログや試行錯誤をもとに、ChatGPTとの対話を通じて整理・執筆したものです。

手順や設計方針は、実際に試した内容と、その中で得られた学びをベースにまとめています。
