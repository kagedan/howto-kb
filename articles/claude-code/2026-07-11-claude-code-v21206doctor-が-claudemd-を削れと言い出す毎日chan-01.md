---
id: "2026-07-11-claude-code-v21206doctor-が-claudemd-を削れと言い出す毎日chan-01"
title: "Claude Code v2.1.206｜/doctor が CLAUDE.md を削れと言い出す｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/719ee336cd64f9e78423"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "qiita"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

`/doctor` に、CLAUDE.md を痩せさせる診断が v2.1.206 で入りました。中身のうち Claude がコードベースから読み取れる記述を洗い出し、削る候補として提示。手で膨らみがちな指示ファイルを、コマンド一発で棚卸しできます。

## 今回の注目ポイント

1. **`/doctor` が CLAUDE.md の削減を提案** - コードから導ける記述を削除候補として指摘する (v2.1.206)
2. **MCP の per-server `request_timeout_ms` が効くように** - 60 秒デフォルトで切れていた長い MCP tool 呼び出しが直った (v2.1.206)
3. **`/commit-push-pr` が `pushDefault` リモートも自動許可** - origin 以外の push 先も確認なしで通る (v2.1.206)
4. **バックグラウンド agent が更新後すぐ裏で自己更新** - アタッチ時の遅いアップグレード待ちが消える (v2.1.206)
5. **`EnterWorktree` が管理外 worktree で確認を挟む** - `.claude/worktrees/` の外へ入る前に確認プロンプトが出る (v2.1.206)
6. **`/model` ピッカーが別モデルの価格を表示していたバグ修正** - 行名と違うモデルの料金が出ていた (v2.1.206)

## MCP tool が 60 秒で切れる問題が直った

`--mcp-config` や `.mcp.json` でサーバーごとに `request_timeout_ms` を指定しても、v2.1.205 以前は読まれていませんでした。時間のかかる MCP tool 呼び出しは、60 秒のデフォルトで一律に打ち切り。長い検索やビルド処理を MCP 経由で回していると、ここで詰まります。

v2.1.206 で per-server の `request_timeout_ms` が反映されるようになりました。指定した値までタイムアウトが伸びます。

:::note warn
この不具合は新規セッションで顕在化していました。`request_timeout_ms` を書いているのに 60 秒で切れる症状に心当たりがあれば、v2.1.206 で解消します。
:::

## `/doctor` が CLAUDE.md の「コードで分かる記述」を削らせる

:::note info
対象読者: CLAUDE.md が育ちすぎて、何が効いているか分からなくなってきた人。
:::

v2.1.206 の `/doctor` に、チェックインされた CLAUDE.md を対象にした診断が加わりました。中身のうち Claude がコードベースから直接読み取れる記述（ディレクトリ構成、使っているフレームワーク、命名規則など）を洗い出し、削る候補として提案してきます。

> proposes trimming checked-in `CLAUDE.md` files by cutting content Claude could derive from the codebase

CLAUDE.md は放っておくと膨らみます。コードを見れば分かることまで書き込むと、コンテキストを圧迫するだけで効き目は薄い。この診断は、コードと重複する記述だけを抜き出し、削除候補として並べます。全文を読み返して要否を判断していた手間が、`/doctor` の提案から始められます。

## push と worktree で確認の入り方が変わった

`/commit-push-pr` はこれまで `origin` への `git push` だけを自動許可していました。v2.1.206 からは `remote.pushDefault` に設定したリモート、あるいは唯一のリモートも対象に加わります。fork 運用や origin 以外を push 先にしている環境で、確認が一つ減る。

逆に `EnterWorktree` は確認が増えました。プロジェクトの `.claude/worktrees/` の外にある worktree へ入るときだけ、確認プロンプトを挟みます。管理下のディレクトリはそのまま、範囲外だけ一拍置く形。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.206 | 新機能 | `/cd` にパス補完 | `/add-dir` と同じディレクトリ候補を表示 |
| v2.1.206 | 認証 | 期限切れログインのエラー改善 | 全モデルが「選択モデルに問題」と誤表示していたのを `/login` 案内に変更 |
| v2.1.206 | MCP | OAuth MCP の再認証不要に | トークン更新が 1 回失敗しただけで手動再認証を求められていた |
| v2.1.206 | 起動 | `claude --resume` / `--continue` のキー入力修正 | 起動直後にキーボードを受け付けない不具合を解消 |
| v2.1.206 | agent | `CLAUDE_CODE_EXTRA_BODY` が効くように | `claude agents` / `--bg` のワーカーで無視されていた |
| v2.1.206 | 改善 | `/code-review` の指摘品質向上 | claude-opus-4-8 で全 effort レベルの精度を改善 |
| v2.1.206 | Bedrock | 起動ハング修正 | `awsCredentialExport` 使用時の数分のハングを解消 |
| v2.1.206 | agents view | 表示改善 | ステータス列が端末幅いっぱいに、Ctrl+X で完了セッションを完全削除 |

## まとめ

v2.1.206 は追加より修正が主体のリリースです。バグ修正 18 件のなかで体感を変えるのは、MCP の `request_timeout_ms` が効くようになった点。新機能で目立つのは `/doctor` の CLAUDE.md 診断で、コードから導ける行を削除候補として出してくれます。
