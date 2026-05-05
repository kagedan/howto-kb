---
id: "2026-05-05-claude-code-v21128-リリース毎日changelog解説-01"
title: "Claude Code v2.1.128 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/594b6094fad9a479dd9e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-05-05"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

Claude Code v2.1.128 が 2026-05-04 にリリースされました。git worktree 利用時の未 push コミットが落ちる重大バグの修正と、並列 shell ツール呼び出しの挙動改善が中心の更新です。

## 今回の注目ポイント

1. **`EnterWorktree` がローカル HEAD から分岐するよう修正** - 未 push コミットが消える事故を回避
2. **並列 shell ツール呼び出しのキャンセル挙動改善** - 1 つの失敗が他のコマンドを巻き込まなくなる
3. **subagent progress summary でプロンプトキャッシュが効くように** - `cache_creation` がおよそ 3 分の 1 に
4. **subprocess が `OTEL_*` 環境変数を継承しなくなった** - bash 経由の OTEL アプリが CLI のエンドポイントに二重送信しなくなる
5. **`/mcp` がツール数を表示、0 ツールのサーバーを警告** - 設定ミスを画面上で発見できる
6. **`claude -p` への 10 MB 超 stdin でのクラッシュ修正** - 巨大ログをパイプで流しても落ちない

---

## `EnterWorktree` のローカル HEAD 起点修正

:::note info
対象: Agent SDK で `EnterWorktree` を使うユーザー、git worktree 経由の長時間タスクを Claude に任せる人。
:::

今回のリリースで一番効くのはここです。

これまで `EnterWorktree` ツールは、ドキュメントに「ローカル HEAD から新ブランチを切る」と書かれていながら、実際には `origin/<default-branch>` を起点にブランチを作っていました。結果、**ローカルにある未 push のコミットが新しい worktree に乗らない**という挙動になっていて、Agent に worktree を切らせて作業させた直後に「あれ、さっきのコミットがない」となる事故が起きていました。

v2.1.128 では起点が修正され、現在のローカル HEAD からブランチが切られます。手元の作業を踏まえた上で並行ブランチが立つので、未 push のコミットは保持される動きに揃いました。

```bash
# 修正前 (v2.1.126 以前)
# ローカル HEAD: 5 コミット先行 (未 push)
# EnterWorktree → origin/main から分岐
# → 5 コミット分が新ブランチに含まれず消える

# 修正後 (v2.1.128)
# ローカル HEAD: 5 コミット先行 (未 push)
# EnterWorktree → ローカル HEAD から分岐
# → 5 コミットがそのまま新ブランチに乗る
```

挙動はドキュメントに書かれていた仕様に揃った形ですが、ドキュメントを信じて Agent に worktree タスクを委譲していた人ほど被害が大きい類のバグです。v2.1.128 への更新は早めに済ませておきたいところ。

---

## 並列 shell ツール呼び出しの巻き添えキャンセル修正

Claude Code は複数の読み取り系 Bash コマンド (grep, git diff, ls など) を 1 ターンで並列実行できます。これまでは並列に投げた 1 本が失敗すると、**同じバッチに乗っている他のコマンドまでまとめてキャンセルされる**挙動でした。

例えば以下のように 3 本を同時に走らせていて、`grep` の対象ファイルが存在しないようなケース。`git diff` と `ls` の結果も丸ごと取れない、ということが起きていました。

```bash
# 1 ターンで 3 並列実行
grep -n "foo" missing.txt   # 失敗
git diff --stat              # 巻き添えでキャンセルされていた
ls -la src/                  # 巻き添えでキャンセルされていた
```

v2.1.128 では失敗したコマンド以外は通常通り結果が返ります。Claude が一度のターンで広く調査するときの取りこぼしが減るので、調査系のタスクで体感が変わるはずです。

---

## subagent progress summary のキャッシュ最適化

地味に効くのが subagent 周りのキャッシュ改善。

これまで sub-agent の進捗サマリ (親エージェントが子エージェントの状態を確認するときに走るやつ) はプロンプトキャッシュをスキップしていて、子エージェントを多用する構成だと `cache_creation` トークンが嵩む原因になっていました。v2.1.128 ではここでもキャッシュが効くようになり、`cache_creation` がおよそ **3 倍削減**されます。

あわせて、sub-agent のトランスクリプトが更新されていないのに進捗サマリが繰り返し発火してトークンを浪費する挙動も修正されました。アイドル状態の sub-agent が裏で走り続けるような構成では、最悪ケースのトークンコストに上限が付きます。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.128 | MCP | `/mcp` ツール数表示 | 接続済みサーバーのツール数を表示し、0 ツールのサーバーを警告 |
| v2.1.128 | MCP | `workspace` 名予約 | `workspace` という名前の MCP サーバーは警告とともにスキップ |
| v2.1.128 | MCP | 再接続時のツール再告知抑制 | サーバープレフィックス単位の要約に変更、会話が埋め尽くされない |
| v2.1.128 | MCP | tool_results の画像復活 | structured content と content blocks 両方返したときに画像が落ちないよう修正 |
| v2.1.128 | OTEL | `OTEL_*` の継承停止 | Bash, hooks, MCP, LSP の subprocess に CLI の OTLP 設定が漏れない |
| v2.1.128 | Plugin | `--plugin-dir` の `.zip` 対応 | ディレクトリだけでなく zip アーカイブもそのまま指定できる |
| v2.1.128 | Plugin | npm 由来 plugin の更新検知 | `/plugin update` が npm ソースの新バージョンを検知するよう修正 |
| v2.1.128 | 認証 | `--channels` が API キー認証で動作 | console 組織は managed settings で `channelsEnabled: true` を立てる |
| v2.1.128 | SDK | `localSettings` 永続化提案 | Bash の "Always allow" が `.claude/settings.local.json` に書かれる |
| v2.1.128 | UI | `/color` 引数なしでランダム | bare `/color` がセッションカラーをランダム選択 |
| v2.1.128 | UI | 1M context モデルの誤判定修正 | autocompact ウィンドウが小さい設定でも "Prompt is too long" にならない |
| v2.1.128 | UI | OSC 8 非対応端末のリンク表示 | markdown リンクのラベルが消えず `label (url)` 形式で出る |
| v2.1.128 | Auto mode | 分類エラーのヒント追加 | 失敗時に retry / `/compact` / `--debug` の案内が出る |

<details>
<summary>v2.1.128 のバグ修正一覧</summary>

- focus mode で新しいプロンプト送信時に直前の応答が一瞬暗くなる問題
- Kitty などで `/exit` 時に "4;0;" の通知が出る問題 (OSC 9 を desktop notification と解釈する端末)
- Remote Control がレート制限時に "Opening your options…" の空メッセージで止まる問題
- ドラッグ&ドロップ画像アップロードが画像読み込み失敗時に "Pasting text…" でハングする問題
- `claude -p` に 10 MB 超の入力をパイプするとクラッシュループする問題
- フルスクリーンモードで折り返された長い URL が一部の行でしかクリックできない問題
- `/plugin` Components パネルが `--plugin-dir` 由来 plugin で "Marketplace 'inline' not found" を出す問題
- list 内のフェンスドコードブロックがコピー時に先頭の空白を引きずる問題
- `/config` のタブナビゲーションでフォーカスが迷子になる問題
- 並列 shell tool calls で読み取り系コマンドが失敗すると兄弟コマンドまでキャンセルされる問題
- effort 非対応モデルで banner に "with X effort" が出る問題
- 3P プロバイダで `/fast` が無関係な skill にあいまいマッチする問題
- Bedrock のデフォルトモデルが `global.*` に解決されてリージョンプレフィックスが効かない問題
- vim mode の NORMAL モードで `Space` がカーソル右移動にならない問題
- ターミナルプログレスインジケータ (OSC 9;4) がツール呼び出し間で消える問題
- `/rename` が引数なしで、最後のエントリが compact 境界の resumed セッションに対し失敗する問題
- `--resume` / `--continue` 後に過去の "remote-control is active" ステータスが残る問題
- 削除済みキャッシュディレクトリを指す `installed_plugins.json` エントリが PATH を汚す問題
- `CLAUDE_CODE_SHELL_PREFIX` 設定時、空白やシェルメタ文字を含む引数が MCP stdio サーバーに壊れて渡される問題
- `/plugin update` が npm 由来 plugin の新バージョンを検知しない問題
- Headless `--output-format stream-json` の `init.plugin_errors` に `--plugin-dir` のロード失敗が含まれない問題

</details>

## まとめ

v2.1.128 は派手な新機能はないものの、`EnterWorktree` の起点バグや並列 shell の巻き添えキャンセルなど、Agent に長時間作業を任せている人ほど刺さる修正が並んでいます。subagent のキャッシュ削減も累計コストで効いてくるので、子エージェントを多用する構成なら更新する価値があります。
