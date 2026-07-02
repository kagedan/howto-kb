---
id: "2026-07-02-openchat-graph-開発環境が更新されました以下のprがマージされましたオプチャグラフ-5-01"
title: "@openchat_graph: 🚀 開発環境が更新されました。以下のPRがマージされました。#オプチャグラフ #583: [STG] skip-ci:"
url: "https://x.com/openchat_graph/status/2072723406295044289"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "x"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

🚀 開発環境が更新されました。以下のPRがマージされました。#オプチャグラフ
#583: [STG] skip-ci: 開発ドキュメント(CLAUDE.md)を必須ルールだけに整理し、手順の詳細をスキルへ分離
---
## 概要
CLAUDE.md が517行まで肥大化し、必須ルールと手順の詳細が混ざって読みにくくなっていたため、必須ルール（憲法）だけに薄くして約110行にしました。手順・コマンド・書き方の詳細は、リポジトリにコミットするプロジェクトスキル3本へ分離しています。

- `.claude/skills/dev-env` — 環境の起動・Mock・Shared mode・Codespaces・CI・ポート
- `.claude/skills/coding-guide` — ページ追加MVC・DBアクセス・スキーマ変更・DI・フロントビルド・キャッシュ生成/genetop
- `.claude/skills/pr-guide` — PRの書き方・スクショ・skip-ci/skip-post・デプロイ確認・署名

.gitignore は `.claude/` 丸ごと除外から `.claude/skills/` だけコミット対象になるよう変更（settings.local.json 等は引き続き除外）。

## 分離時に実態と突き合わせて直した記述
旧 CLAUDE.md には実態とずれた記述が複数残っていたため、コード・Makefile・CI設定と照合して修正しました。

- `make up-mock-slow` / `up-mock-cron` / `down-mock` / `restart-mock` / `rebuild-mock` / `ssh-mock` は存在しない（down/restart/rebuild/ssh は起動中の環境を自動判定、cron は `make cron`/`cron-stop`、Mock の遅延・件数は `.env` の MOCK_* 変数で制御）
- Mock 環境の HTTPS 8543 はどの設定にも存在しない（実際は基本環境と同じ 8443）
- Codespaces の post-create は `make init-y` を自動実行しない（Claude CLI / GitHub CLI 導入のみ）
- frontend/ のサブディレクトリは ranking / oc-app / all-room-stats の3つのみ（stats-graph・comments は無い）。フロント側翻訳TSの実際の場所も明記
- Controllers 配下は Api/ と Pages/（旧記述は Page/）。psr-4 に `App\Views` → `app/Views/Classes` を追記
- deploy run の `[PROD]` は pr-title-prefix.yml がPRタイトルに自動付与したもの、と出所を明記。skip-ci のタイトル判定が `[STG]`/`[PROD]` 自動付与で壊れる注意も追記
- PR スクショのホスティング用ブランチ運用は廃止（2026-06-27 指示）。添付は GitHub web UI へのドラッグ&ドロップ

あわせて CLAUDE.md に「実態を変えたら CLAUDE.md・スキルも同じ PR で更新する」ルールを追加しました。

---
🤖 Generated with Claude Code (claude-fable-5)
Posted from: `user-B550M-Pro4:~/repos/Open-Chat-Graph`
