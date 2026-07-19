---
id: "2026-07-19-claude-code-v21214permission-チェックの穴が一斉に塞がる毎日change-01"
title: "Claude Code v2.1.214｜permission チェックの穴が一斉に塞がる｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/6c6646ec2759b63216c5"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "qiita"]
date_published: "2026-07-19"
date_collected: "2026-07-20"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.214 は permission チェックの取りこぼしを一斉に塞ぐリリース。`Edit(src/**)` のような allow ルールが、ツリー内のどこにある `src/` への書き込みも自動承認していたバグが直りました。allow を細かく書いている設定ほど、承認プロンプトの出方が変わります。

## 今回の注目ポイント

1. **`Edit(src/**)` の効きすぎを修正** - 単一セグメント `dir/**` の allow ルールが `<cwd>/dir` 以外の `dir/` まで自動承認していた (v2.1.214)
2. **EndConversation ツールを追加** - 悪質な利用や脱獄試行に対し、Claude 側からセッションを終了できる (v2.1.214)
3. **Bash の permission チェックが軒並み fail-closed に** - 10,000 文字超のコマンド、FD リダイレクト、zsh の `[[ ]]` 添字などが自動承認されなくなった (v2.1.214)
4. **docker のデーモンリダイレクトフラグに確認を追加** - `--url` / `--connection` / `--identity` や Podman のリモートモードが無確認で走っていた (v2.1.214)
5. **バックグラウンドセッションの居座り・削除不能を修正** - `claude rm` で消せない、アイドルでもデーモンが生き残るなど複数 (v2.1.214)
6. **`--settings` 経由の plugins 未ロード回帰を修正** - v2.1.181 以来、CLI フラグで有効化した plugins が読まれていなかった (v2.1.214)

## allow ルールと Bash チェックの締め直し

:::note alert
`.claude/settings.json` の allow ルールや hook の `if:` 条件で単一セグメントの `dir/**` を書いている場合、このアップデートで挙動が変わります。承認プロンプトが増えたり hook が発火しなくなったら、まずここを疑ってください。
:::

対象読者: `Edit(src/**)` や `Read(config/**)` のような allow ルール、あるいは hook の `if:` 条件を `.claude/settings.json` に書いている人。

これまで `Edit(src/**)` は、`<cwd>/src` だけでなくツリー内のどこにある `src/` への書き込みも自動承認していました。モノレポで `packages/foo/src/` や `vendor/lib/src/` を触ると、意図せず素通り。v2.1.214 でこれが `<cwd>/src` のみに限定されました。

hook の `if:` 条件も同じ方向へ。単一セグメントの `dir/**` は `<cwd>/dir` にしかマッチしなくなり、任意の深さでマッチさせたいなら `**/dir/**` と書きます。ただし `deny` / `ask` の permission ルールは従来どおり任意深さでマッチするので、安全側の挙動は据え置き。

Bash の permission チェック側もまとめて厳しくなりました。

- 10,000 文字を超えるコマンドは常にプロンプトを出す(以前は誤判定で自動実行されることがあった)
- bash が解釈を変える FD リダイレクト形式は fail-closed。自動承認しない
- `[[ ]]` 内の zsh 変数の添字・修飾子を「ただの文字列」とみなしていたのを修正し、確認を出すように
- 一部の `help` / `man` コマンドが危険なオプションやコマンド置換を実行し得たため、自動承認を撤回

いずれも、解析器が構造を読み切れないコマンドは自動承認しない、という一点に揃っています。

`docker` にデーモンリダイレクト系のフラグが付いているときも、確認プロンプトを出すようになりました。対象は `--url` / `--connection` / `--identity`、それに Podman の `docker` シムのリモートモード。これらは接続先を別のデーモンへ向け替えるため、read-only だと思って許可していると想定外のホストにコマンドが飛びます。`file` コマンドも同様に、`-m` / `--magic-file` と `-f` / `--files-from` を使う形は read-only 自動許可の対象外に。

## EndConversation ツール

Claude が、悪質なユーザーや脱獄試行に対してセッション自体を終了できる EndConversation ツールが入りました。claude.ai では 2025 年から動いていた挙動が、Claude Code にも来た形。

> Claude can end sessions with highly abusive users or jailbreak attempts

背景は[公式リサーチ](https://www.anthropic.com/research/end-subset-conversations)に説明があります。

## バックグラウンドセッションのデーモン周りが一段落

バックグラウンドセッションの「消せない・居座る」系のバグをまとめて修正。

- `←` や `/background` で退避してアイドル放置すると、デーモンとワーカーが無期限に生き残っていた
- 完了済みセッションが、バックグラウンドサービスのアイドル後は `claude rm` でもエージェントビューでも削除できなかった
- git 管理外のフォルダから起動したセッションがエージェントビューから消せなかった
- 交代したデーモンが後継の制御ソケットを削除し、次のクライアントが健全な後継デーモンを kill してしまう問題

退避セッションを放置してデーモンが残っていた環境なら、v2.1.214 で一掃されます。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.214 | 新機能 | 進捗ハートビート | 無音だった長時間ツール実行に定期的な進捗表示を追加 |
| v2.1.214 | 新機能 | OTel 属性追加 | `message.uuid` / `client_request_id` / `tool_source` をログイベントに付与、メッセージ相関とツール由来の追跡が可能に |
| v2.1.214 | 新機能 | `CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH` | OTel content 属性の 60 KB 切り詰め上限を設定可能に |
| v2.1.214 | 新機能 | memory frontmatter の `modified` | ISO タイムスタンプを自動付与 |
| v2.1.214 | 新機能 | subagentStatusLine に reasoning effort | カスタムエージェント行でモデルと effort を描画できるように |
| v2.1.214 | 破壊的変更 | SessionStart hook の source | fork で開始したセッションを `"resume"` でなく `"fork"` と報告 |
| v2.1.214 | 修正 | Windows/PowerShell ツール群 | UTF-16LE 書き込み、Unicode エラー、stdin ハング、`where.exe` の誤エラーなど複数を修正 |
| v2.1.214 | 修正 | プロキシ下の "Socket is closed" | Windows の企業プロキシ経由でストリーミングが失敗していた |
| v2.1.214 | 修正 | scheduled タスクの prompt 拒否 | 設定した prompt を untrusted 入力として拒否していた |
| v2.1.214 | 修正 | telemetry の二重計上 | cumulative な `message_delta` を複数フレーム出す際にコスト/トークンが二重計上 |
| v2.1.214 | 修正 | `/ultrareview` が merge base なしで拒否 | tracked ファイル全体のレビューを提案するように |
| v2.1.214 | 修正 | 巨大 `--settings` でメモリ肥大 | device file や数 GB のファイルで無制限に消費、2 MiB 超は起動時にエラー |

## まとめ

v2.1.214 は新機能より、permission チェックの取りこぼしを塞ぐ修正が主役。特に `Edit(src/**)` 型の allow ルールと hook の `if:` 条件は挙動が変わるので、`.claude/settings.json` を細かく書いているなら一度見直す価値があります。EndConversation は悪質な入力への防御、バックグラウンドセッションの整理はデーモンの後始末に効きます。
