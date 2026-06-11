---
id: "2026-06-10-claude-code-obsidian-で記憶の二層構造を作る-01"
title: "Claude Code × Obsidian で『記憶の二層構造』を作る"
url: "https://zenn.dev/0rv3/articles/b6a7172bfda1ed"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "VSCode", "zenn"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude(Claude Code / claude.ai)を日常的に使っていると、「前にこの話したよね」「あのアイデア、どこかに書いた気がする」という場面が増えてくる。

これを解消するために、以下の二層構造を構築した。

* **長期ナレッジ層**: Obsidian + MCP連携で、claude.aiからアイデアや内省を直接読み書き
* **作業文脈層**: Claude CodeのセッションログをローカルDBに自動保存し、次回セッションで参照

本記事では前者、Obsidian × Claude連携の構築過程で踏んだ落とし穴を中心にまとめる。後半でClaude Code側の記憶機構にも軽く触れる。

## 全体構成

```
GitHub private repo (SSoT)
    ↕ git pull / push
ローカルvault (PC, Git管理)
    ↑ MCP経由で読み書き (claude.ai)
    ↓ rsync (定期実行)
クラウドストレージ上のvault
    ↕ 同期
モバイル端末のObsidian
```

* claude.aiからはMCPサーバー経由でGitHub上のvaultを直接読み書きする
* ローカルPCはGit管理のvaultを持ち、定期的にpull
* pull後、クラウドストレージ配下の別vaultにrsyncで一方向反映
* モバイル端末はクラウドストレージの同期機能でそのvaultを参照

「どこから書いても、最終的にモバイルまで届く」状態を作るのが目的。

## MCPサーバーについて

NotionやGoogle DriveのようなホストされたMCPコネクタもあるが、今回はObsidian vaultをGitHub repo経由で操作する自作の軽量MCPサーバー(Cloudflare Workers上)を使った。`create_note` / `read_note` / `list_notes` / `update_note` の4ツールがあれば十分動く。

claude.aiのCustom Connectorとして登録するには、OAuth 2.1のフロー(動的クライアント登録・authorize・tokenエンドポイント＋ `.well-known/oauth-authorization-server`)を最低限満たす必要がある。本格的な認可サーバーは不要で、パススルー実装で十分だった。

## ハマったポイント集

### 1. クラウドストレージの「同じ名前のフォルダが複数ある」問題

iCloud Driveを例にすると、Windows側から見えるパスには罠がある。

* `iCloudDrive/Obsidian/` ← 新規に作ったフォルダ(空)
* `iCloudDrive/iCloud~md~obsidian/Obsidian/` ← モバイルアプリが実際に使っているvault

モバイル側のObsidianがすでにiCloud上にvaultを持っている場合、そのパスは `iCloud~<bundle-id風の文字列>/<vault名>/` のような形式になっている。新規にフォルダを作ってもモバイル側とは繋がらない。

**教訓**: モバイル側で先にvaultを作っている場合、PC側はそのパスを探して合わせにいく方が早い。

### 2. rsyncで`.git`ごと同期してしまう

Git管理下のvaultをそのままrsyncすると、`.git/`や`.obsidian/`(ローカル設定)も一緒に飛んでいく。`.git`が数百MB単位になっていると、同期先のストレージ容量を圧迫するし、競合の原因にもなる。

```
rsync -av --delete \
  --exclude='.git/' \
  --exclude='.obsidian/' \
  /path/to/git-vault/ \
  /path/to/cloud-vault/
```

一度汚染してしまった場合は、同期先で該当フォルダを手動削除してから再実行するのが早い。

### 3. WSLでのSSH鍵設定忘れ

GUI(VSCode等)でGit操作をしていると、WSLのターミナルからは別のSSH鍵設定が必要なことを忘れがちになる。

```
ssh -T git@github.com
# Permission denied (publickey).
```

が出たら、`~/.ssh/id_rsa.pub` の中身をGitHubの該当アカウントに登録すれば解決する。

### 4. リポジトリのremoteが古いブランチ/リポジトリを向いていた

過去にリポジトリ名を変更していたケースで、ローカルの `origin` が旧リポジトリを向いたままになっていた。

```
git remote -v
# origin  git@github.com:xxx/old-repo-name.git
```

`git remote set-url origin git@github.com:xxx/new-repo-name.git` で修正。地味だが、自動化スクリプトが「成功はするが何も更新しない」状態になっていたため発覚に時間がかかった。

### 5. cronはWSL再起動で止まる

WSL上のcronデーモンは、Windows再起動後に自動では立ち上がらない。Windowsのタスクスケジューラから、ログオン時に `wsl.exe -u root service cron start` を実行するタスクを登録しておくと解決する。

```
$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-u root service cron start"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "WSL-cron-autostart" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
```

### 6. MCP経由の変更とローカルGitの不整合

claude.aiのMCPはGitHub repoを直接(API経由で)読み書きする。一方ローカルのGit vaultはpullしない限り変更を受け取らない。

「MCPで作ったファイルがローカルに見当たらない」という事象が発生した場合、まず `git pull` を試すとよい。定期同期スクリプトには **pull → rsync** の順序を組み込んでおくと、この問題が定常的に解消される。

```
#!/bin/bash
cd /path/to/git-vault && git pull origin main
rsync -av --delete \
  --exclude='.git/' \
  --exclude='.obsidian/' \
  /path/to/git-vault/ \
  /path/to/cloud-vault/
```

## 最終的な運用フロー

```
外出先・PC問わずClaudeにメモを投げる
  ↓
Claudeがフォルダ構造を見て適切な場所に書き込む(MCP経由)
  ↓
定期実行スクリプトが pull → rsync
  ↓
モバイル端末に反映
```

ルールは「キャプチャはどこでもいい、整理はClaudeに任せる」の一言に集約した。複雑な運用ルールは続かないので、迷ったら一箇所に投げる設計にしている。

## おまけ: Claude Codeセッションのローカル記憶化

Obsidian側が「内省・アイデアの長期保存」だとすると、Claude Codeのセッション内容(技術的な議論やデバッグの経緯)は別の性質を持つ。こちらはSQLite + FTS5 + ベクトル検索のローカルツールを自作し、`SessionEnd`フックで自動保存するようにしている。

実装中に踏んだ小さなバグも一つ書いておく。SQLiteのFTS5はデフォルトのトークナイザーだと、検索クエリに含まれる`-`(ハイフン)を列指定の構文として解釈してしまう。`"my-project"`のようなクエリを投げると `no such column: project` のようなエラーになる。

対策はクエリをダブルクォートで囲んでフレーズ検索として渡すこと。

```
# Before
"WHERE memories_fts MATCH ?"

# After
"WHERE memories_fts MATCH '\"' || ? || '\"'"
```

ハイフンを含む単語(プロジェクト名など)を検索対象にする場合は、最初からこの対策をしておくと無難。

## まとめ

* claude.aiからはMCP経由でナレッジベース(Obsidian vault)を直接操作
* ローカルとモバイルの同期は「pull → rsync」の一方向で割り切る
* 自動化(cron)はOS再起動を考慮して設定する
* FTS5でハイフン入りの検索語を扱う場合はクォートで囲む

どれも個別には小さな話だが、組み合わせて「壊れずに回る」状態にするまでが地味に時間がかかる部分だった。同じ構成を作る人の参考になれば幸いだ。
