---
id: "2026-05-12-claude-code-v21137v21139-リリース毎日changelog解説-01"
title: "Claude Code v2.1.137〜v2.1.139 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/9a85125fe731e2fc306a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-12"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.137〜v2.1.139 の計 3 本を 1 本にまとめて解説します。新機能ラッシュは v2.1.139 に集中、残り 2 本は VSCode 拡張周りと内部修正のみ。

## 今回の注目ポイント

1. **agent view (Research Preview)**: `claude agents` で全 Claude Code セッションを 1 リストに集約 (v2.1.139)
2. **`/goal` コマンド**: 完了条件を渡すと Claude がターンを跨いで作業を継続 (v2.1.139)
3. **hook の `args: string[]` (exec form)**: シェル経由なしで spawn、パスのクオート問題が消える (v2.1.139)
4. **`continueOnBlock` 設定**: `PostToolUse` の rejection 理由を Claude に戻してターンを継続させる (v2.1.139)
5. **MCP stdio に `CLAUDE_PROJECT_DIR`**: hooks と同じ環境変数が stdio MCP サーバーにも渡る (v2.1.139)
6. **API key 設定時の機能無効化**: Remote Control・`/schedule`・claude.ai MCP connectors・通知設定が無効化 (v2.1.139)

## `claude agents` で並走セッションを 1 画面に集約 (v2.1.139)

:::note info
対象: Claude Code を複数並走させて、どれが自分待ちか分からなくなる人。
:::

`claude agents` を叩くと、走行中・自分の入力で止まっている・完了済み、の Claude Code セッションが 1 つのリストに並ぶ。

```bash
claude agents
```

ターミナルタブを行き来して「どれが入力待ち」を探す手間が減る。Research Preview 扱いなので今後挙動は変わりうる。詳細は [公式ドキュメント](https://code.claude.com/docs/en/agent-view) に集約されている。

---

## `/goal` で完了条件を渡して放置する (v2.1.139)

:::note info
対象: 「テストが通るまで」「lint が消えるまで」のような達成条件を伝えて放置したい人。
:::

`/goal` で完了条件を 1 つ宣言すると、Claude が満たすまでターンを跨いで作業を続ける。interactive モード・`-p` (非対話) モード・Remote Control いずれでも動く。

```
/goal すべての pytest が通るまで修正を続ける
```

実行中はオーバーレイパネルに elapsed / turns / tokens が出る。トークンの伸びを横目で見ながら止め時を判断できる。

「失敗テストを直して」のような単発依頼だと、Claude が「直しました」と返してもテストが赤いまま、ということが起きる。`/goal` は「何が満たされたら終わるか」を Claude 側に持たせるので、止まる条件がコマンド側で固定される。

---

## hook の `args` 配列でクオート地獄から抜ける (v2.1.139)

シェル経由でコマンドを組み立てると、空白や `$` を含むパスは引用符で囲む必要がある。`args: string[]` はシェルを介さずプロセスを直接 spawn するので、`${path}` に空白が混ざっても引用符は不要。

```json
{
  "type": "command",
  "command": "/usr/local/bin/myhook",
  "args": ["${path}", "--mode", "check"]
}
```

同じく v2.1.139 で `PostToolUse` hook の `continueOnBlock: true` も入った。立てておくと hook がツール実行を拒否したとき、rejection 理由を Claude に戻してターンを継続させられる。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.139 | UX | `/scroll-speed` | マウスホイール速度をライブプレビューで調整 |
| v2.1.139 | Plugin | `claude plugin details <name>` | コンポーネント一覧とセッションあたり推定トークンコストを表示 |
| v2.1.139 | UX | transcript ナビゲーション | `?` でショートカット、`{`/`}` で user prompt 間ジャンプ、`v` でショートカットパネル切替 |
| v2.1.139 | MCP | `/mcp` Reconnect ホットリロード | `.mcp.json` の編集を再起動なしで反映、失敗時は HTTP status と URL を表示 |
| v2.1.139 | MCP | stdio に `CLAUDE_PROJECT_DIR` | hooks と同じ環境変数を stdio サーバーが受け取れる。plugin config からも `${CLAUDE_PROJECT_DIR}` 参照可 |
| v2.1.139 | Plugin | `claude plugin install` 自動再フェッチ | マーケットプレイスを自動更新してリトライしてから「not found」を返す |
| v2.1.139 | Telemetry | subagent ヘッダ | `x-claude-code-agent-id` / `x-claude-code-parent-agent-id` 付与、OTEL `claude_code.llm_request` span に `agent_id` / `parent_agent_id` 属性追加 |
| v2.1.139 | 認証 | API key 設定時の機能無効化 | `ANTHROPIC_API_KEY` / `apiKeyHelper` / `ANTHROPIC_AUTH_TOKEN` が立っていると Remote Control・`/schedule`・claude.ai MCP connectors・通知設定が無効化される (Claude.ai login が併存していても同じ) |
| v2.1.139 | コンパクション | sensitive な user instructions を保全 | コンパクションプロンプトがモデルに保持を指示 |
| v2.1.139 | コンテキスト | `/context all` の skill 推定 | モデル側 tokenizer を反映した丸め値で表示 |
| v2.1.139 | コンテキスト | プラグイン出所表示 | `/context` でプラグイン由来 skill の plugin 名を表示 |
| v2.1.139 | MCP | Remote MCP 再接続リトライ | 一時的失敗時の自動リトライが全ユーザーで有効化 |
| v2.1.139 | VSCode | 直近セッション再オープン | `Cmd/Ctrl+Shift+T` で直前タブ復活。`claudeCode.enableReopenClosedSessionShortcut` で切り替え |
| v2.1.138 | 内部 | 内部修正のみ | 公開向け変更なし |
| v2.1.137 | VSCode | Windows 起動失敗を修正 | 拡張機能が Windows でアクティベートできない不具合を解消 |

<details>
<summary>バグ修正 (v2.1.139)</summary>

- `forceRemoteSettingsRefresh` ポリシーと expired credentials が組み合わさり、`claude auth login` / `logout` / `status` がデッドロックして復旧不能だった問題
- `autoAllowBashIfSandboxed` がシェル展開 (`$VAR`, `$(cmd)`) を含むコマンドを自動承認しなかった問題
- 端末に書き込む hook が対話プロンプトの表示を壊す問題 (hook は端末アクセスなしで実行されるようになった)
- HTTP/SSE MCP サーバーが non-protocol データを流すとメモリが無制限に伸びる問題 (1 SSE フレームあたり 16 MB cap)
- `Skill(name *)` のワイルドカードが `Bash(ls *)` と同じ prefix match で動かない問題
- シンボリックリンク経由の `~/.claude/settings.json` 編集を hot-reload が拾わない問題
- marketplace キーと manifest 名が違うとき plugin details がロードできない問題
- `/model` ピッカーの「Default」行が `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` の上書きを反映しない問題
- レスポンス完了 5 分後に「stream idle timeout」が誤発火する問題 (watchdog がストリームキャンセル時にクリアされていなかった)
- MCP サーバーが 10 個以上で cache directory が書き込み不可のとき、原因不明のまま `exit 1` で落ちていた問題
- ダイアログのタブ名・リスト矢印・select 行でタイピングカーソルが点滅する問題
- transcript view でマウスクリック後にレターショートカットが効かなくなる問題
- Bash モードの上矢印が最初の履歴を繰り返し、編集途中のドラフトを上書きする問題
- 画像を複数まとめてペースト / ドロップしたとき最後の 1 枚しか挿入されない問題
- ハイパーリンクが dark テーマで読めない dark navy で表示される問題 (active テーマに合わせるように)
- 3P プロバイダーで model が `opus` alias のとき model picker に重複した「Current model」行が出る問題
- PAYG 3P プロバイダーの legacy Opus picker エントリがデフォルトと同じモデルに解決される問題
- Cursor / VS Code 1.92〜1.104 でマウスホイールスクロールが暴れる問題 (トラックパッドは一定速度、マウスホイールは 1 ノッチ約 3 行)
- Windows Terminal / VS Code でバックグラウンドセッションに attach したときのスクロール挙動の崩れ
- 切断済みサーバー由来の MCP リソースが `@server:` 補完に残り続ける問題
- 2 ファイル diff の snippet で truncated 行数を 1 行多く報告していた問題
- Grep の Windows ドライブレターパスが相対化されない問題と、count モードが単一ファイル paths の合計を誤って出す問題
- 罫線埋め込みテキストが CJK / 絵文字の visual cell width 計算ミスでオーバーフローする問題
- ファジー一致のハイライトが絵文字や astral plane 文字をペアの途中で割る問題
- skill 引数名に regex メタ文字が含まれていると引数置換が壊れる問題
- ProgressBar がほぼ満杯の fractional cell でフルブロックを描画していた問題
- 最後の subscriber が抜けたあともフェッチ中だと task polling と `fs.watch` が復活する問題
- manifest 名と source identifier が違うとき、plugin の依存解決でカウントが古いまま残る問題
- Insights の Time-of-Day チャートで unparseable timestamp が混ざるとセッション分布が歪む問題
- cmd / super / win 修飾キー単独の keybinding が unparseable 扱いになる問題
- `--print` モードで `claude_code.active_time.total` OTEL メトリクスが出ない問題
- `claude plugin update` が marketplace 内のクロスプラグイン symlink を壊す問題

</details>

## まとめ

v2.1.139 の目玉は agent view と `/goal`。複数並走しているセッションの待ち状態を 1 リストで確認でき、完了条件付きの長時間タスクを `/goal` 経由で渡せるようになった。hooks 側も `args: string[]` と `continueOnBlock` の追加で、シェルクオートと PostToolUse rejection 周りが整理された。v2.1.137 / v2.1.138 は VSCode 拡張と内部修正のみで大きな変更なし。
