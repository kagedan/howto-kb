---
id: "2026-06-10-claude-code-v21169v21170-リリース毎日changelog解説-01"
title: "Claude Code v2.1.169〜v2.1.170 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/72904f7295eb568f9d4e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-06-10"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.169〜v2.1.170 の計 2 本を 1 本にまとめます。v2.1.170 で新モデル Claude Fable 5 が一般公開、v2.1.169 は機能追加と修正の大型リリースです。

### 今回の注目ポイント

1. **Claude Fable 5 が一般公開** - Mythos クラスの新モデル。v2.1.170 へ上げるとアクセスできる (v2.1.170)
2. **`--safe-mode` で全カスタマイズ無効起動** - CLAUDE.md・plugins・skills・hooks・MCP を一括で切って原因を切り分け (v2.1.169)
3. **`/cd` でセッション中に作業ディレクトリ変更** - プロンプトキャッシュを壊さず移動 (v2.1.169)
4. **`disableBundledSkills` でバンドル skill を隠す** - 標準 skill・workflow・組み込みコマンドをモデルから隠せる (v2.1.169)
5. **VS Code 統合ターミナルで transcript が保存されない不具合を修正** - `--resume` に出てこなかったセッションが戻る (v2.1.170)
6. **エンタープライズ MCP ポリシーの適用漏れを修正** - 再接続時の未適用と OTEL 証明書パスの trust 回避を塞ぐ (v2.1.169)

## 新モデル Claude Fable 5 が一般公開

:::note info
対象読者: 最新モデルをすぐ試したい全ユーザー
:::

v2.1.170 の中身はほぼこれ一点。Anthropic が新モデル Claude Fable 5 を一般公開しました。公式は「Mythos クラス」と位置づけ、これまで一般提供したどのモデルより能力が高いとしています。

使うには v2.1.170 へ上げるだけ。

```bash
claude update                  # v2.1.170 以降へ更新
claude --model claude-fable-5  # 起動時にモデル指定
```

セッション中の切り替えは `/model` から。ベンチマークや詳しい位置づけは[公式アナウンス](https://www.anthropic.com/news/claude-fable-5-mythos-5)を。

ただ、能力が高い=自分のワークフローで速く正確、とは限りません。コストと応答速度、既存プロンプトとの相性は手元で測ってから常用を決めます。

---

## `--safe-mode` でカスタマイズを全部切って起動

:::note info
対象読者: プラグインや hook の不調を切り分けたい人
:::

CLAUDE.md、plugins、skills、hooks、MCP サーバー。これを全部無効にして起動するフラグが v2.1.169 で入りました。

```bash
claude --safe-mode
# 環境変数でも指定できる
CLAUDE_CODE_SAFE_MODE=1 claude
```

plugin や hook を増やすほど、落ちたとき容疑者が増えます。`--safe-mode` なら素の状態から起動し、設定を1つずつ戻して切り分けられる。MCP が悪いのか hook が悪いのか、当たりをつける前の最初の一手。

---

## `/cd` でセッションを止めずに作業ディレクトリを変更

:::note info
対象読者: 1 セッションで複数リポジトリを行き来する人
:::

```
/cd ../another-project
```

v2.1.169 で追加された `/cd` は、セッションの作業ディレクトリを移動するコマンド。効くのはプロンプトキャッシュを壊さないこと。途中でディレクトリを変えてもキャッシュは効いたまま、次のターンに入れます。

## その他の変更

機能追加と改善の残りは表で。

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.169 | 機能 | `disableBundledSkills` | 標準 skill・workflow・組み込みコマンドをモデルから隠す設定と環境変数 |
| v2.1.169 | 機能 | `/workflows` 即時起動 | ターン実行中でも待たずに開く |
| v2.1.169 | 改善 | CPU 使用率 | 応答ストリーミング中とスピナー描画中の CPU 使用を削減 |
| v2.1.169 | 改善 | `claude agents --json` | blocked・dispatch 直後も出力し、`--all`・`id`・`state` を追加 |
| v2.1.169 | 改善 | Vertex/Foundry | 5 分のアイドルタイムアウトを復活、`API_FORCE_IDLE_TIMEOUT=0` で無効化 |
| v2.1.169 | 改善 | CLAUDE.md 警告 | 「長すぎ」警告のしきい値がモデルのコンテキスト窓に応じて変動 |
| v2.1.169 | セキュリティ | MCP ポリシー | `allowedMcpServers`/`deniedMcpServers` の再接続時などの適用漏れを修正 |
| v2.1.169 | セキュリティ | OTEL 証明書 | untrusted な project settings が trust 確認なしに証明書パスを設定できた問題を修正 |
| v2.1.170 | 修正 | VS Code transcript | 統合ターミナル起動時に transcript が保存されず `--resume` に出ない問題を修正 |

### バグ修正(v2.1.169)

<details><summary>Windows・リモート・background セッション・UI まわりの修正(クリックで展開)</summary>

- background セッションが retire→wake をまたいで `--ide`・`--chrome`・`--bare`・`--remote-control` などのフラグを保持するように
- `TaskCreate` の信頼性を改善。壊れた入力を自動修復し、未ロードツールの検証エラーにスキーマを含める
- background セッションに、worktree へ入るまで共有チェックアウトの編集がブロックされる旨を事前通知し、無駄な編集拒否を回避
- リモート管理設定に無効なエントリがあっても、残りの有効なポリシーを適用したうえでエラーを表示(payload 全体を破棄しない)
- Up/Down 矢印が長い入力のラップ行を飛ばして履歴へ移る問題を修正。各表示行を1行ずつ移動するように
- macOS の claude.ai ログイン時、ターン開始時の約 30-50ms の UI 停止を修正
- `claude -p` が Windows でスラッシュコマンド/skill スキャン待ちにより遅延・ハングする問題を修正(v2.1.161 のリグレッション)
- Remote Control がセッション再開時の OAuth トークン更新と重なり「reconnecting」で固まる問題を修正
- Windows 起動時に Git Credential Manager の「Connect to GitHub」ポップアップが出る問題を修正
- カスタム statusline 利用時にフッターのヒント(「esc to interrupt」等)が出ない問題を修正
- worker が落ちたリモートセッションへ再接続するたび、古い権限・ダイアログのプロンプトが復活する問題を修正
- WSL の Windows Terminal で agents 画面から戻ると古い・崩れたフレームが残る問題を修正
- background agent が pre-warmed worker 上でプロジェクトの `env`(`ANTHROPIC_MODEL` 等)を無視する問題を修正
- Windows で MCPB プラグインキャッシュが不当に無効化され再展開される問題を修正
- plugin の `.in_use` PID ロックファイルが無制限に溜まる問題を修正(1 日 1 回掃除)
- Windows の自動アップデータが `claude.exe` を他プロセスが掴んでいるとき、セッション内でのリトライを止めるように
- スラッシュコマンドメニューの skill タグの色コントラストを改善

</details>

## まとめ

v2.1.170 の主役は Claude Fable 5。気になるならまず `claude update` で v2.1.170 へ。v2.1.169 は `--safe-mode` と `/cd` という日常使いの 2 コマンドが効きます。
