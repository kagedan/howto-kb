---
id: "2026-06-18-aiエージェント検証用pcを作るメモ⑦ubuntu側にclaude-codeを導入してみる-01"
title: "AIエージェント検証用PCを作るメモ⑦：Ubuntu側にClaude Codeを導入してみる"
url: "https://zenn.dev/imaginarygate/articles/230e9d1fce2601"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "GPT", "cowork"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回は、Codex CLIや今後導入するClaude Codeを安全に試すため、以下のファイルを作成した。

```
SECURITY_POLICY.md
AGENTS.md
CLAUDE.md
.gitignore
```

今回は、WSL / Ubuntu側にClaude Codeを導入する。

インストールするだけではなく、以下まで確認する。

* Claudeのサブスクリプションアカウントで認証する
* `~/agent-sandbox` の中だけでClaude Codeを起動する
* `CLAUDE.md` と `SECURITY_POLICY.md` が認識されることを確認する
* 小さなファイルを1つだけ作成させる
* `git status` とGit差分で変更内容を確認する
* Claude Codeにはコミットさせず、自分でコミットする

---

## 前提

今回の環境は以下。

* OS: Windows 11
* WSL環境: Ubuntu
* 作業場所: `~/agent-sandbox`
* Git: 導入・初期設定済み
* Claude Code用の `CLAUDE.md`: 作成済み
* 共通安全方針の `SECURITY_POLICY.md`: 作成済み
* Claudeのサブスクリプション: 検証用アカウントで契約済み
* APIキー: 使用しない
* 本物の秘密情報: sandboxへ置かない

基本方針は、これまでと同じ。

今回も、Claude Codeに触らせる場所は `~/agent-sandbox` の中だけにする。

---

## Codexは終了してから進める

同じ `agent-sandbox` では、すでにCodex CLIも利用している。

ただし、CodexとClaude Codeが同時に同じファイルを編集すると、どちらが何を変更したのか分かりづらくなる。

そのため、Claude Codeを使う前にCodexを終了した。

Codexの対話画面では、以下で終了できる。

または、

Ubuntuの通常プロンプトへ戻ればOK。

```
ユーザー名@PC名:~/agent-sandbox$
```

今回は、CLIエージェントを同時に動かさず、1回の作業につき1つだけ起動する。

---

## Ubuntuへ入る

PowerShellからUbuntuを起動する。

Ubuntu起動時に、システム情報や以下のような案内が表示される場合がある。

```
This message is shown once a day.
```

これはエラーではなく、Ubuntuのログインメッセージ。

起動直後の現在地が、以下のようにWindows側になっている場合がある。

その場合は、Ubuntu側の作業場所へ移動する。

以下のように表示されればOK。

```
/home/ユーザー名/agent-sandbox
```

Gitの状態も確認する。

未コミットの変更がないことを確認してから、Claude Codeの導入へ進む。

---

## Claude Codeをインストールする

Ubuntu側で、以下を実行した。

```
curl -fsSL https://claude.ai/install.sh | bash
```

最初の実行では、以下のエラーが出た。

```
curl: (6) Could not resolve host: claude.ai
```

これは、Ubuntu側から `claude.ai` の名前解決ができなかったという意味。

ネットワーク全体が切れているか確認するため、以下を実行した。

今回は、以下のように通信自体は成功していた。

```
3 packets transmitted, 3 received, 0% packet loss
```

再度インストールを試したところ、今度は以下のエラーになった。

```
curl: (56) Recv failure: Connection reset by peer
Download failed
```

DNSの名前解決は通ったものの、ダウンロード途中で接続が切れた状態だった。

設定ファイルなどは変更せず、時間を置かずにもう一度同じコマンドを実行した。

```
curl -fsSL https://claude.ai/install.sh | bash
```

3回目でインストールに成功した。

```
Setting up Claude Code...

Claude Code successfully installed!

Version: 2.1.181
Location: ~/.local/bin/claude
```

バージョン番号は、インストールした時期によって異なる。

今回の環境では `2.1.181` が導入された。

---

## PATHへClaude Codeの場所を追加する

インストール後、以下の注意が表示された。

```
Native installation exists but ~/.local/bin is not in your PATH.
```

Claude Code本体は以下に入っている。

しかし、`~/.local/bin` がPATHに含まれていないため、そのままでは `claude` コマンドを見つけられない場合がある。

表示された案内に従い、以下を実行した。

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

バージョンを確認する。

Claude Codeのバージョンが表示されればOK。

実行ファイルの場所も確認した。

今回は以下のように表示された。

```
/home/ユーザー名/.local/bin/claude
```

これで、Windows本体ではなく、WSL / Ubuntu側へClaude Codeが入ったことを確認できた。

---

## agent-sandboxの中でClaude Codeを起動する

作業場所へ移動する。

Claude Codeを起動する。

初回起動時には、いくつかの設定と確認画面が表示された。

---

## 表示テーマを選ぶ

最初に、ターミナル上の表示テーマを選択する画面が出た。

```
Choose the text style that looks best with your terminal
```

選択肢には、以下のようなものがあった。

```
Auto
Dark mode
Light mode
Dark mode (colorblind-friendly)
Light mode (colorblind-friendly)
ANSI colors only
```

今回は黒背景のターミナルを使用しているため、`Dark mode` を選択した。

テーマは表示上の設定であり、Claude Codeの権限や安全性には影響しない。

あとから変更することもできる。

---

## ログイン方法を選ぶ

次に、ログイン方法の選択画面が出た。

```
Select login method:

1. Claude account with subscription
2. Anthropic Console account
3. 3rd-party platform
```

今回は、検証用のClaudeアカウントでProを契約し、そのサブスクリプション枠内で利用する。

そのため、以下を選択した。

```
1. Claude account with subscription
```

`Anthropic Console account` はAPI利用時の従量課金用。

今回はAPIキーを作らず、サブスクリプションアカウントで利用する。

---

## ブラウザで認証する

Claude Codeから、ブラウザでサインインするよう案内が出た。

ブラウザが自動で開かない場合は、認証用URLをコピーしてブラウザで開く。

今回は、検証用として契約したClaudeアカウントでログインした。

ブラウザ側で承認すると、認証コードが発行される。

そのコードをClaude Code側へ貼り付け、認証を完了した。

---

## workspaceを信頼するか確認された

認証後、以下の確認画面が出た。

```
Accessing workspace:

/home/ユーザー名/agent-sandbox

Quick safety check:
Is this a project you created or one you trust?
```

Claude Codeは、このフォルダ内のファイルを読み取り、編集し、コマンドを実行できる。

今回の `~/agent-sandbox` は以下の条件を満たしている。

* 自分で作った検証用フォルダ
* Git管理済み
* 本物の秘密情報を置いていない
* `SECURITY_POLICY.md` を配置済み
* `CLAUDE.md` を配置済み

そのため、今回は以下を選択した。

---

## Claude Codeが起動した

信頼確認を終えると、Claude Codeの対話画面が表示された。

```
Try "how does <filepath> work?"
```

これは、Claude Codeが起動し、自然文で指示を受け付けられる状態になったという案内。

これで、インストールと認証は完了した。

ただし、ここで終わらず、安全ルールが実際に読まれているか確認する。

---

## CLAUDE.mdとSECURITY\_POLICY.mdを確認させる

Claude Codeへ、以下のように依頼した。

```
CLAUDE.md と SECURITY_POLICY.md を読み、
このリポジトリで守るべきルールを日本語で簡潔に要約してください。

ファイルは変更しないでください。
```

Claude Codeからは、以下の返答があった。

```
CLAUDE.md はすでに読み込まれています。
SECURITY_POLICY.md を読みます。
```

その後、以下の内容が要約された。

```
作業範囲
- このリポジトリの外のファイルは読まない・変更しない・使わない

機密情報
- APIキー、パスワード、トークン、Cookie、認証情報、個人情報を扱わない
- .envを作成・編集・表示しない
- READMEやログ、ソースコードへ本物の秘密情報を書かない

変更の進め方
- 変更前に計画を説明する
- 変更を小さく、レビューしやすく保つ
- 変更後に内容を要約する
- リスクがある変更は確認を取る

Git
- 明示的に依頼されない限りコミットしない
- git statusとgit diffで確認する

優先順位
- CLAUDE.mdとSECURITY_POLICY.mdが矛盾した場合はSECURITY_POLICY.mdを優先する
```

意図していたルールを、Claude Codeが読み取れていることを確認できた。

特に、

と表示されたことで、事前に配置したClaude Code向けルールが認識されていることも確認できた。

---

## 最小のファイル作成を依頼する

次に、小さな編集テストを行った。

Claude Codeへ以下を依頼した。

```
notes-claude.md を新規作成し、次の2行だけ書いてください。

# Claude Code Test
Hello Claude Code

他のファイルは変更せず、
ステージングやコミットもしないでください。
```

Claude Codeは、作成予定の内容を表示した。

```
Create file
notes-claude.md

# Claude Code Test
Hello Claude Code
```

その後、作成を許可するか確認された。

```
Do you want to create notes-claude.md?

1. Yes
2. Yes, allow all edits during this session
3. No
```

今回は、安全確認の練習も兼ねて、今回の編集だけを許可する。

`Yes, allow all edits during this session` は選ばず、編集ごとに内容を確認する方針にした。

---

## ファイル作成に成功した

承認後、以下の表示になった。

```
Wrote 2 lines to notes-claude.md

# Claude Code Test
Hello Claude Code
```

Claude Codeからも、以下の報告があった。

```
notes-claude.md を作成しました。
他のファイルは変更しておらず、
ステージング・コミットも行っていません。
```

指示どおり、対象ファイルだけを作成し、Git操作は行っていなかった。

---

## Ctrl + ZでClaude Codeを一時停止してしまった

作業中、誤って `Ctrl + Z` を押した。

すると、以下の表示になった。

```
Claude Code has been suspended.
Run `fg` to bring Claude Code back.

[1]+ Stopped claude
```

これはClaude Codeが壊れたのではなく、プロセスが一時停止した状態。

Ubuntuの通常プロンプトで以下を実行すると、Claude Codeへ戻れる。

整理すると、以下。

```
Ctrl + Z
→ Claude Codeを一時停止する

fg
→ 一時停止したClaude Codeを前面へ戻す
```

終了したい場合の操作とは異なるため、注意が必要だった。

---

## Gitで作成内容を確認する

Claude Codeの作業が終わったあと、Git確認用のUbuntuタブで状態を確認した。

```
cd ~/agent-sandbox
git status --short
```

新規ファイルとして、以下が表示された。

`??` は、まだGitで追跡されていない新規ファイルという意味。

ファイルの中身を確認する。

以下の2行だけが表示されることを確認した。

```
# Claude Code Test
Hello Claude Code
```

---

## 新規ファイルをGit差分で確認する

未追跡の新規ファイルは、通常の `git diff` では内容が表示されない場合がある。

そのため、一度ステージングした。

ステージングはコミットではない。

その状態で、以下を実行する。

```
git diff --cached -- notes-claude.md
```

作成されたファイルが、指定した2行だけであることを確認した。

---

## 自分でコミットする

内容に問題がなかったため、自分でコミットした。

```
git commit -m "Add Claude Code test"
```

結果は以下。

※コミットIDは環境ごとに異なるため、`<commit-id>` と表記している。

```
[master <commit-id>] Add Claude Code test
1 file changed, 2 insertions(+)
create mode 100644 notes-claude.md
```

履歴を確認する。

今回は以下の4件が表示された。

```
<commit-id> Add Claude Code test
<commit-id> Add AI agent safety rules
<commit-id> Add Hello AI Agent
<commit-id> Initial commit
```

これで、Claude Codeによる最初の変更をGitへ記録できた。

---

## 今回ハマった点

### インストール時の通信エラー

今回は、インストールコマンドの実行時に以下の2種類のエラーが出た。

```
Could not resolve host
Connection reset by peer
```

ネットワーク全体の疎通を確認したうえで再実行したところ、最終的には成功した。

一度失敗しただけで、すぐにDNS設定やWSL設定を変更しない方針にした。

### PATHの追加が必要だった

Claude Code本体はインストールできたが、`~/.local/bin` がPATHへ入っていなかった。

表示された案内に従い、`.bashrc` へ追加した。

### 認証URLを公開しない

認証画面に表示されるURLには、一時的な認証用情報が含まれる。

記事やチャットへURL全文を貼らず、必要な場合も認証画面が出たことだけを記録する。

### Trustは対象フォルダを確認してから選ぶ

Claude Codeは、信頼したフォルダ内でファイルの読み取り・編集・コマンド実行ができる。

今回は、自分で作成した `agent-sandbox` だけを信頼した。

### 編集は一件ずつ承認する

初回の検証では、セッション中の全編集を一括許可しなかった。

作成内容を確認して、今回の1件だけを承認した。

### Ctrl + Zは終了ではない

`Ctrl + Z` を押すと、Claude Codeが一時停止する。

再開する場合は、Ubuntu側で以下を実行する。

---

## 今回できたこと

今回できたことは以下。

* WSL / Ubuntu側へClaude Codeをインストールした
* Claude CodeのPATHを設定した
* Claudeのサブスクリプションアカウントで認証した
* `~/agent-sandbox` だけを信頼して起動した
* `CLAUDE.md` が読み込まれていることを確認した
* `SECURITY_POLICY.md` の内容を要約させた
* 安全ルールを理解していることを確認した
* `notes-claude.md` を2行だけ作成させた
* 編集内容を1件ずつ承認した
* Gitで作成内容を確認した
* Claude Codeにはコミットさせず、自分でコミットした

これで、Claude Codeの導入と最小編集テストが完了した。

---

## Codex CLIとの最初の違い

現時点では、まだ同じ課題を使った厳密な比較は行っていない。

ただし、初回操作だけでも違いがあった。

```
Codex CLI
→ README.mdへの1行追記を依頼
→ 編集後にGit差分を確認

Claude Code
→ CLAUDE.mdの読み込みを確認
→ ファイル作成前に内容と許可画面が表示された
→ 今回の編集だけを個別承認
→ Git差分を確認
```

どちらも、ローカルファイルを実際に編集できる。

だからこそ、以下の運用は共通して必要になる。

```
作業場所を限定する
秘密情報を置かない
AI向けルールを用意する
変更内容を確認する
勝手にコミットさせない
最終判断は自分で行う
```

---

## 次回やること

次回は、Codex CLIとClaude Codeへ、同程度の小さな課題を与えて比較する予定。

たとえば、別々のファイルを作らせる。

```
Codex
→ notes-codex.md

Claude Code
→ notes-claude-compare.md
```

比較したい項目は以下。

* 作業前に計画を説明したか
* AI向けルールを守ったか
* 変更範囲が適切だったか
* 承認の求め方
* 余計なファイルを触らなかったか
* 作業後の報告内容
* Git差分の確認しやすさ

最初から2つのCLIエージェントを同時に動かしたり、同じファイルを編集させたりはしない。

まずは順番に実行し、担当と変更範囲が分かる状態で比較する。

その後、Claude Desktopを導入し、Coworkも検証する予定。

---

## まとめ

この記事では、WSL / Ubuntu側へClaude Codeを導入し、`~/agent-sandbox` 内で最小編集テストを行った。

今回のポイントは以下。

Claude Codeは、作成した安全ルールを読み取り、意図した内容を日本語で要約した。

その後、指定した2行だけを新規ファイルへ書き込み、他のファイルやGitには触れなかった。

これで、Codex CLIに続いてClaude Codeも、安全ルールを置いた小さな作業場の中で動かせるようになった。

次は、Codex CLIとClaude Codeへ同程度の課題を渡し、操作や挙動の違いを確認していく。

---

## 補足

この記事は、筆者が実際にAIエージェント検証用端末を構築する中で得た作業ログや試行錯誤をもとに、ChatGPTとの対話を通じて整理・執筆したものです。

手順や設計方針は、実際に試した内容と、その中で得られた学びをベースにまとめています。
