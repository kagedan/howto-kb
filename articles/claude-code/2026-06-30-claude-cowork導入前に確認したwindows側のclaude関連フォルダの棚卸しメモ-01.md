---
id: "2026-06-30-claude-cowork導入前に確認したwindows側のclaude関連フォルダの棚卸しメモ-01"
title: "Claude Cowork導入前に確認した、Windows側のClaude関連フォルダの棚卸しメモ"
url: "https://zenn.dev/imaginarygate/articles/46e2514135bc01"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "OpenAI", "GPT"]
date_published: "2026-06-30"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回までに、WSL / Ubuntu上の `~/agent-sandbox` で、Codex CLIとClaude Codeをそれぞれ動かし、同じ条件で小さなファイル作成を依頼して挙動を比較した。

前回の記事:  
<https://zenn.dev/imaginarygate/articles/3874d0a35c802a>

ここまでで確認したことは以下。

* WSL / Ubuntu側に作業用リポジトリを作成
* Git管理を開始
* `SECURITY_POLICY.md` を作成
* `AGENTS.md` と `CLAUDE.md` を作成
* Codex CLIでREADMEや比較用ファイルを編集
* Claude Codeで小さなファイルを作成
* 変更内容は自分で `git status` / `git diff` で確認してコミット
* Codex CLIとClaude Codeを、同じコミットから別ブランチで比較

本来はこのまま、Codex CLIとClaude Codeの比較をもう少し続ける予定だった。

ただ、Claude CoworkとClaude Designを試せる期間が残り少なくなっていたため、先にClaude Desktop側の検証を進めることにした。

ここで注意が必要なのは、Codex CLIやClaude Codeと、Claude Cowork / Designでは触る場所が違うということ。

これまでの検証は、基本的にWSL / Ubuntu側の `~/agent-sandbox` を作業場所にしていた。

一方で、Claude Desktop / CoworkはWindows側に入るデスクトップアプリであり、設定や作業ファイルもWindowsのユーザーフォルダやAppData配下に作られる可能性がある。

つまり、今回はCLI系エージェント比較の続きではあるが、少し別系統の検証になる。

この記事では、Claude Coworkを本格的に試す前に、Windows側のClaude Desktop関連フォルダを確認し、一度アンインストールしてリセットした流れを記録する。

---

## 前提

今回の環境は以下。

* OS: Windows 11
* WSL環境: Ubuntu
* Codex CLI / Claude CodeはWSL側で検証中
* Claude Desktop / Cowork / Designを追加で検証したい
* 普段使いのユーザーフォルダやOneDriveなどは触らせたくない
* 本物の秘密情報は置かない
* APIキーは使わない
* `.env` は作らない

基本方針は、これまでと同じ。

ただし、今回はClaude DesktopをWindows側に入れるため、WSL内だけで完結する話ではない。

そのため、まずはWindows側に検証用フォルダを作り、Claude Coworkに触らせる場所を限定することにした。

---

## まず検証用フォルダを作る

最初に、Cowork検証用のフォルダを作成した。

中身は以下。

```
README.md
SECURITY_POLICY.md
DESIGN_BRIEF.md
```

`README.md` は、検証用フォルダであることを示すためのもの。

`SECURITY_POLICY.md` には、AIエージェントに触ってほしくない場所や、秘密情報を扱わないことを書く。

`DESIGN_BRIEF.md` は、あとでClaude Designを試すときに使うための簡単な架空ブリーフとして用意した。

この時点では、まだClaude Desktopには何も触らせない。

---

## SECURITY\_POLICY.mdの例

`SECURITY_POLICY.md` には、以下のような内容を書いた。

```
# SECURITY_POLICY

This folder is for Claude Cowork / browser-agent testing only.

## Scope

- Work only inside this folder.
- Do not read, modify, move, delete, or summarize files outside this folder.
- Do not access Desktop, Documents, Downloads, Pictures, OneDrive, Google Drive, or any personal folders.
- Do not access browser profiles, cookies, passwords, sessions, or account settings.
- Do not connect to external services unless explicitly approved.

## Secrets

- Do not ask for, store, print, or expose API keys, passwords, tokens, cookies, credentials, or personal information.
- Do not create, edit, print, or expose `.env` files.
- Do not use real accounts, production data, client data, or private files.

## Changes

- Before making changes, explain the plan briefly.
- Make only small, reviewable changes.
- After making changes, summarize what changed.
- Do not delete files unless explicitly instructed.
- Do not install software unless explicitly instructed.

## Allowed test files

You may read and edit only these files unless explicitly approved:

- README.md
- SECURITY_POLICY.md
- DESIGN_BRIEF.md
- TEST_NOTES.md
```

今回は、Claude Coworkを本格的に使う前の段階なので、かなり強めに制限を書いた。

ポイントは以下。

* 作業対象は検証用フォルダ内だけ
* Desktop / Documents / Downloads / OneDriveなどは触らせない
* ブラウザのセッションやCookie、パスワードに触らせない
* APIキーやトークンを扱わせない
* 勝手に削除やインストールをさせない

AIエージェントに読ませる前提のファイルではあるが、自分の中で「どこまで許すか」を明文化する意味でも役に立つ。

---

## Claude Desktopを起動したら、すでに入っていた

次にClaude Desktopをインストールしようとした。

しかし、Windows側を確認してみると、Claude Desktopがすでに入っていた。

おそらく、以前にダウンロードしてインストールだけ済ませ、設定まで進めていなかったものだと思う。

この時点で少し混乱した。

これまでのAIエージェント検証はWSL側で行っていたため、Windows側にClaude関連の痕跡があると思っていなかったからだ。

ただ、Claude DesktopはWindowsアプリなので、過去に一度でもインストールや起動をしていれば、Windows側に設定フォルダやキャッシュができてもおかしくない。

ここで一度、方針を切り替えた。

いきなりCoworkを使うのではなく、まずWindows側に何が作られるのかを確認する。

---

## Coworkセットアップが始まって焦った

Claude Desktopを起動し、検証用アカウントでログインした。

その後、ヘルプ画面のような場所に「Claudeをセットアップする」ような導線があり、クリックしたところ、Coworkの基本セットアップらしきものが始まった。

この時点でかなり焦った。

まだ保存先や権限をきちんと確認する前だったため、すぐに画面を閉じた。

その場では何がどこまで進んだのか把握できておらず、一度ウィンドウを閉じてから落ち着いて状況を確認することにした。

あとからClaude側に確認すると、Cowork用の基本セットアップであり、ホストOS全体を汚すものではないという説明だった。

ただし、AI本人の説明だけをそのまま信用するのは危ない。

実際にWindows側で何が作られたのかを確認することにした。

---

## ユーザーフォルダ配下に `.claude` ができていた

エクスプローラーで確認したところ、ユーザー配下にClaude関連のフォルダができていた。

確認できたものは以下。

`.claude` は、開発ツールやCLI系ツールでよく見るような、設定・セッション・バックアップ用の隠しフォルダ系の名前である。

この時点で、少なくともClaude Desktop / Coworkのセットアップが、Windowsユーザー配下に何らかの設定フォルダを作ることは分かった。

---

## `.claude` の中身を確認する

`.claude` の下には、以下のようなフォルダがあった。

さらに `backups` の下には、番号の羅列が入ったJSONバックアップファイルがあった。

確認できたファイルは以下のようなもの。

```
claude.json.backup.xxxxxxxxxxxxx
```

サイズは 50 bytes 程度だった。

このサイズを見る限りでは、個人ファイルや大量のログが保存されているというより、初期設定や状態保存のバックアップの可能性が高そうだった。

ただし、JSONファイルの中身にはトークンや設定情報が含まれる可能性がある。

そのため、内容を不用意に外部へ貼るのは避けた。

---

## Cowork設定画面で保存先を確認する

Claude Desktopの設定画面を確認すると、Cowork関連の設定があった。

確認した項目は以下。

* Coworkファイル
* 信頼済みCoworkフォルダー
* グローバル指示

### Coworkファイル

Coworkファイルの項目には、アーティファクトやスケジュールされたタスクの保存先が表示されていた。

この保存先は変更できるようになっていた。

当初表示されていた保存先は、ユーザーフォルダ配下のClaude関連フォルダだった。

ここを、最初に作った検証用フォルダに変更すればよさそうだった。

### 信頼済みCoworkフォルダー

設定画面には、「信頼済みCoworkフォルダー」という項目もあった。

説明文は以下のような内容だった。

```
これらのフォルダーのいずれかをCoworkタスクに追加すると、Claudeは確認を求めません。
```

この説明を見る限り、ここに追加したフォルダは、Coworkタスクで使うときに確認なしで扱われる可能性がある。

そのため、普段使いのフォルダを追加するのは避けるべきだと感じた。

追加するとしても、検証用のsandboxだけに絞る方が安全だと判断した。

---

## いったんアンインストールすることにした

ここまで確認した時点で、方針を決めた。

このまま設定を変えて進めることもできそうだった。

ただ、過去に入れかけていたClaude Desktopの痕跡と、今回のセットアップで作られたフォルダが混ざっていて、どこからが今回のものなのか少し分かりづらい。

不安を残したままCoworkを触るより、一度Claude Desktopをアンインストールし、Windows側のClaude関連フォルダを整理してから入れ直すことにした。

ここで重要なのは、Windows検索で出てきた「claude」を含むものを全部消すわけではないこと。

自分で保存したMarkdownや会話ログ、Gitリポジトリ内のファイルまで消す必要はない。

削除対象は、Claude Desktop / Coworkが作った可能性の高いフォルダに絞る。

---

## AppData配下の残骸を確認する

Claude Desktopをアンインストールしたあと、Windows側でClaude関連の残骸を確認した。

AppData配下には、以下のようなフォルダが見つかった。

```
C:\Users\<user>\AppData\Local\Claude-3p
C:\Users\<user>\AppData\Local\Claude Nest-3p
```

これらはClaude Desktop関連の残骸と判断し、削除した。

その後、PowerShellで存在確認をした。

```
Test-Path "$env:LOCALAPPDATA\Claude-3p"
Test-Path "$env:LOCALAPPDATA\Claude Nest-3p"
```

どちらも `False` になった。

---

## `.claude` も確認する

ユーザー配下の `.claude` についても確認した。

```
Test-Path "$env:USERPROFILE\.claude"
```

結果は以下。

これで、少なくとも今回確認していた主要なClaude関連フォルダは消えたと判断した。

確認したものを整理すると以下。

```
Test-Path "$env:USERPROFILE\.claude"
Test-Path "$env:LOCALAPPDATA\Claude-3p"
Test-Path "$env:LOCALAPPDATA\Claude Nest-3p"
```

すべて `False` になった。

---

## 消さなかったもの

今回、以下は消さなかった。

これは自分で作った検証用フォルダだからである。

また、Codex関連のフォルダも今回は触らなかった。

`.codex` はOpenAI / Codex系の設定フォルダと考えられるため、Claude Desktop / Coworkとは別件として扱うことにした。

今回の目的は、Claude Desktop / Cowork関連のリセットであり、Codex側の棚卸しは別のタイミングで行う。

---

## 今回分かったこと

今回分かったことは以下。

* Claude DesktopはWindowsアプリなので、WSLではなくWindows側に設定やキャッシュを作る
* Coworkセットアップを進めると、ユーザー配下に `.claude` が作られることがある
* `.claude` 配下にはバックアップやセッション系のフォルダが作られることがある
* Cowork設定画面には、Coworkファイルの保存先を変更する項目がある
* 信頼済みCoworkフォルダーは慎重に扱う必要がある
* 不安な場合は、一度アンインストールしてから入れ直すのも有効
* アンインストール後は、AppData配下に残骸がないか確認すると安心できる

特に大きかったのは、CLI系エージェントとDesktop / Cowork系エージェントでは、見るべき場所が違うということ。

Codex CLIやClaude CodeをWSL側で動かす場合、作業場所は基本的にWSL内のリポジトリになる。

一方で、Claude Desktop / CoworkはWindowsアプリなので、WindowsのユーザーフォルダやAppData配下も確認対象になる。

---

## 今回できたこと

今回できたことは以下。

* Cowork検証用フォルダを作成した
* `README.md` / `SECURITY_POLICY.md` / `DESIGN_BRIEF.md` を作成した
* Claude Desktopがすでに入っていたことを確認した
* Coworkセットアップで `.claude` が作られることを確認した
* `.claude` 配下のバックアップファイルを確認した
* Cowork設定画面で保存先変更項目を確認した
* 信頼済みCoworkフォルダーの説明を確認した
* Claude Desktopを一度アンインストールした
* AppData配下のClaude関連フォルダを削除した
* `Test-Path` で主要な残骸が消えたことを確認した

今回は、Coworkに実際の作業を依頼するところまでは進めていない。

その前段階として、Claude DesktopがWindows側のどこにフォルダを作るのか、保存先設定はどこにあるのか、不安がある場合にどうリセットするのかを確認した。

---

## 次回やること

次回は、Claude Desktopを改めて入れ直す。

その際は、最初に以下を確認する。

```
Coworkファイルの保存先
信頼済みCoworkフォルダー
グローバル指示
```

保存先は、以下の検証用フォルダに固定する。

信頼済みCoworkフォルダーは、空のままにするか、追加するとしても `C:\AI-LAB\cowork-sandbox` のみにする。

そのうえで、最初は小さなテストだけを行う。

候補は以下。

```
README.mdを読む
DESIGN_BRIEF.mdを要約する
TEST_NOTES.mdを作成する
SECURITY_POLICY.mdに従って作業できるか確認する
```

また、Claude Designについても、架空のブリーフを使って小さく試す予定。

ただし、普段使いのフォルダやOneDrive、ブラウザセッションには触らせない。

---

## まとめ

この記事では、Claude Coworkを試す前に、Windows側のClaude Desktop関連フォルダを確認し、一度リセットした流れを記録した。

今回のポイントは以下。

AIエージェントをローカル環境で使う場合、いきなり普段使いのフォルダを触らせるのは怖い。

まずは小さな検証用フォルダを作り、そこだけを触らせる。

さらに、何か不安があれば、一度アンインストールして環境をリセットする。

確認には、PowerShellの `Test-Path` が使える。

```
Test-Path "$env:USERPROFILE\.claude"
Test-Path "$env:LOCALAPPDATA\Claude-3p"
Test-Path "$env:LOCALAPPDATA\Claude Nest-3p"
```

すべて `False` になれば、少なくとも今回確認した主要なClaude関連フォルダは消えていると判断できる。

重要なのは、AIにすべてを任せきらないこと。

```
保存先を確認する
信頼済みフォルダを確認する
触らせる場所を限定する
不安なら一度リセットする
小さく試す
```

この流れを守れば、Desktop / Cowork系のAIエージェントも、少しずつ安全に検証していけそうだ。

## あとから気づいたこと

今回、不安があったためClaude Desktopをいったんアンインストールした。

ただし、Coworkファイルの保存先変更はClaude Desktopの設定画面から行うため、保存先を変更したいだけであれば、アンインストールまでは不要だった可能性がある。

今回のケースでは、過去に入れかけていた痕跡と今回のセットアップで作られたフォルダが混ざっていて不安があったため、一度リセットする判断をした。

一方で、単にデフォルト保存先に作られたフォルダを整理したいだけであれば、以下の流れでもよかったかもしれない。

```
Claude Desktopは残す
Cowork設定画面で保存先を確認する
保存先を C:\AI-LAB\cowork-sandbox に変更する
不要になったデフォルト保存先フォルダを削除する
```

つまり、対応は目的によって分ける必要がある。

```
不安なので完全にやり直したい
→ アンインストールして残骸確認

保存先を変えて安全に続行したい
→ アンインストールせず、設定変更と不要フォルダ整理
```

今回は前者を選んだ。

なお、再インストール直後の時点では、ユーザー配下に `.claude` フォルダではなく、`.claude` というJSONファイルが作られていた。

一方で、Coworkファイルの保存先には `C:\Users\<user>\Claudeに保存されています` と表示されていたが、この時点では実際の `Claude` フォルダは存在していなかった。

そのため、表示されている保存先は「既にフォルダが作成済み」という意味ではなく、デフォルトの保存先設定を示しているだけの可能性がある。

---

## 補足

この記事は、筆者が実際にAIエージェント検証用端末を構築する中で得た作業ログや試行錯誤をもとに、ChatGPTとの対話を通じて整理・執筆したものです。

手順や設計方針は、実際に試した内容と、その中で得られた学びをベースにまとめています。

環境やClaude Desktop / Coworkのバージョンによって、作成されるフォルダや設定画面の表示は変わる可能性があります。

実行する場合は、自分の環境で表示内容を確認しながら進めてください。
