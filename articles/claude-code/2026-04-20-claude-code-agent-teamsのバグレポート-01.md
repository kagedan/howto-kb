---
id: "2026-04-20-claude-code-agent-teamsのバグレポート-01"
title: "Claude Code Agent Teamsのバグレポート"
url: "https://zenn.dev/znet/articles/20260420_claude-code-agent-teams-bug-report"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

# Claude Code v2.1.114 Agent Teams クラッシュ事故レポート

**発生日**: 2026-04-20  
**影響バージョン**: Claude Code **v2.1.114**（および v2.1.50〜v2.1.111 系にも類似症状）  
**安定バージョン**: **v2.1.98**（本報告時点で動作確認済み）  
**対象ユーザー**: Claude Code の Agent Teams（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`）機能を利用して tmux ベースでマルチエージェント運用している方・アップデート後に Agent Teams が動かなくなった方

## 症状（観測された現象）

Claude Code v2.1.114 を team-lead として tmux 上で起動し、teammate（Dev / Reviewer 等）を `TeamCreate` + `Agent` tool で起動すると、以下が単発または複合で発生します。

| 現象 | 体感 |
| --- | --- |
| team-lead のクラッシュ | `q.toolUseContext.getAppState is not a function` 等のエラーで team-lead プロセスが落ちる |
| スタックオーバーフロー（無限再帰） | teammate が permission request を発行したタイミングで team-lead が再帰ループに陥り落ちる |
| teammate の孤立 | teammate 側だけ `Waiting for team lead approval` のまま停止し、tmux 画面では生きて見える |
| `teammateMode: "tmux"` が無視される | 設定上は tmux モードのはずが、実際には in-process モードで起動してしまう |
| `Agent` tool の `team_name` パラメータが失敗 | `getTeammateModeFromSnapshot called before capture` エラーで teammate 生成が失敗 |

筆者の環境（WSL2 Ubuntu + tmux 3.4 + Claude Code v2.1.114 + Opus 4.7）では、実戦投入中（Webhook 拡張タスク）にスタックオーバーフローで team-lead がクラッシュし、`scribe` のみ稼働・他の teammate は待機状態のまま取り残される事象が発生しました。

**2026-04-20 完走テスト結果（v2.1.98）**: v2.1.98 ダウングレード後、5エージェント構成（Chief + dev-1 / dev-2 / reviewer / scribe）で調査系タスクを実行。Chief クラッシュなし・全エージェントが gh コマンドを Deny なしで完走・60分以内に完了。**v2.1.98 での安定稼働を再確認。**

---

## 原因（GitHub Issue 3件の複合）

Anthropic 公式リポジトリ `anthropics/claude-code` に以下3件の Issue が既報告・クローズ済みです。**クローズされていても、対応バージョンが特定リリースに限定されるため v2.1.114 では症状が再発する可能性があります**。

### 1. `teammateMode "tmux"` がサイレントに in-process へフォールバック（#29207）

* v2.1.50+ 以降、`process.stdin.isTTY === false` の条件下で `teammateMode: "tmux"` 設定が無視され、警告も出さず in-process モードに落ちる gatekeeper バグ
* 利用者は tmux 運用しているつもりでも、実態は in-process 単独プロセスで動作

### 2. team-lead スタックオーバーフロー（#49303）

* v2.1.111 + Opus 4.7 環境下で、teammate が permission request を発行した後に team-lead が `aLH ↔ rV` 間の無限再帰（`rQ7` / `permission-explainer` 周辺）でスタックオーバーフロー
* team-lead が落ちる一方 teammate は `Waiting for team lead approval` のまま停止するため、見た目は「動いているが応答がない」状態

### 3. `getTeammateModeFromSnapshot` race condition（#40270）

* v2.1.86 系で `Agent` tool に `team_name` パラメータを渡すと `getTeammateModeFromSnapshot called before capture` エラーで teammate 生成が失敗する初期化レース

v2.1.114 は上記の直接フィックス対象外のリリース帯であり、筆者環境では Issue #49303 と同様の症状が再発しました。

---

## 回避策（検証済み）

### 即応: Claude Code を v2.1.98 に固定

v2.1.98 は Agent Teams 機能の動作確認が取れている最後のマイナーとして扱い、以下でインストールします。

```
# WSL2 Ubuntu 想定
npm install -g @anthropic-ai/claude-code@2.1.98

# 確認
claude --version
# → 2.1.98 が表示されれば OK
```

Windows 側の Claude Code は Agent Teams を使わない用途（通常対話・IDE 拡張等）であれば最新版のままで差し支えありません。**Agent Teams を利用する環境のみ v2.1.98 固定**が現実解です。

### アップグレード判断フロー（今後）

新しいリリースを Agent Teams 用途で適用する前に、以下をすべて満たしてから本適用してください。

1. **GitHub Issue 3件の状態確認**:
   * #29207 / #49303 / #40270 が該当バージョンで修正済みである旨、リリースノート or 関連コミットで確認できる
2. **dev 検証**: 本番投入前に捨てて良いサンドボックス環境で、軽量タスク（5-10分で終わるもの）を完走させる
3. **段階適用**: dev 検証を通った後に Agent Teams 本番環境へ適用

「安定バージョン」は常に「動作確認が取れているバージョン」を指します。最新が必ずしも安定ではないことが Experimental 機能の性質です。

---

## ハマらないためのチェックポイント

| チェック | 確認方法 |
| --- | --- |
| Claude Code バージョン | `claude --version` |
| Agent Teams 機能の ON | 環境変数 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` が設定されているか |
| tmux バージョン | `tmux -V`（3.x 推奨） |
| Node.js バージョン | `node --version`（v20+ 推奨） |
| `teammateMode` が実際に tmux で起動しているか | team-lead 起動後、`tmux list-panes -a` で teammate 用のペインが生成されているか |
| permission 設定 | `~/.claude/settings.json` の deny リストが team-lead ↔ teammate の通信を阻害していないか |
| gh CLI インストール済み | `gh --version`（WSL 側で確認） |
| GH\_TOKEN 設定済み | `gh auth status` で `Logged in` が表示されるか。未設定の場合 gh コマンドが全エージェントで失敗する |
| tmux セッション内での GH\_TOKEN 読み込み | tmux セッション起動前に `~/.bashrc` に `export GH_TOKEN="..."` を追記し `source ~/.bashrc` を実行済みか。セッション内で環境変数が引き継がれない場合、エージェントに `source ~/.bashrc` を明示的に指示する必要がある |

`teammateMode: "tmux"` を設定したのにペインが増えていない場合は #29207 のフォールバックに当たっている可能性が高いです。

---

## 成果物を失わないための運用

team-lead がクラッシュしても、各 teammate が git commit 済みの成果物はリポジトリに残ります。筆者のケースでは以下の救出ルートで実害を回避しました。

1. teammate がそれぞれ作業ブランチに commit 済みであることを前提に設計する
2. team-lead クラッシュ時は tmux セッションを強制終了 → ブランチから PR を手動作成
3. 1セッション=1作業指示書（スコープ単位）で運用し、長時間稼働を避ける

Agent Teams のような Experimental 機能を実戦で使う場合、**「クラッシュ前提」の救出ルートを事前に運用設計しておく**ことが最大の保険です。

---

## まとめ

* Claude Code v2.1.114 は Agent Teams の3つの既知バグ（#29207 / #49303 / #40270）の複合で team-lead がクラッシュし得る
* **v2.1.98 へのダウングレードで安定稼働**（2026-04-20 時点で筆者確認）
* Experimental 機能のアップデートは「修正確認 → dev 検証 → 本適用」の3段階で対応推奨
* 成果物救出ルート（teammate の git commit 前提設計）を運用に組み込むこと

同じ症状で困っている方の参考になれば幸いです。

---

## 情報ソース
