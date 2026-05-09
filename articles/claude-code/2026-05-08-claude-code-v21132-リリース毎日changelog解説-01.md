---
id: "2026-05-08-claude-code-v21132-リリース毎日changelog解説-01"
title: "Claude Code v2.1.132 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/9dbf420099a35a044f82"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "AI-agent", "qiita"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.132 は新規 env var が3つ、修正が25件超のメンテナンスリリース。スクロール周りの不具合や MCP のメモリリーク修正が並びます。

### 今回の注目ポイント

1. **`CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` でフルスクリーンを切れる**。ネイティブ scrollback に会話を残せる opt-out が追加
2. **stdio MCP 起点の 10GB+ メモリリークが修正**。非プロトコル出力を stdout に書く MCP サーバで RSS が無限に膨らむ問題
3. **IDE の Stop ボタンや `kill -INT` で `--resume` できなかったのを修正**。graceful shutdown が走り、ターミナルモード復元と再開ヒントが出るように
4. **`/` 始まりのテキストをペーストすると消える/未知コマンド扱いになる問題を修正**
5. **`--resume` が絵文字破損で `no low surrogate in string` を吐く問題を修正**。既存の壊れたセッションも load 時にサニタイズ
6. **Bedrock/Vertex で `ENABLE_PROMPT_CACHING_1H` を立てると 400 が返る問題を修正**

---

## フルスクリーンレンダラーの opt-out が追加

:::note info
対象: 2.1 系で fullscreen renderer に切り替えられて困っていた人
:::

`CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` を立てると、起動時に alternate screen バッファに切り替えず、ターミナルの通常スクロールバックの上で動きます。Claude を抜けた後も会話履歴がスクロール可能。

```bash
export CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1
claude
```

何が変わるか:

- 終了後に画面がクリアされず、これまでのやり取りがそのまま端末に残る
- tmux の copy-mode や iTerm2 の検索でセッション内容を遡れる
- マウスサポート・自動コピー・低メモリといった fullscreen 側の利点は失われる

`/tui fullscreen` のスタートアップバナーも更新され、低メモリ・マウスサポート・選択時の自動コピーといった追加メリットが説明に入りました。fullscreen が好きな人はそのまま、戻したい人は env var で戻す、という棲み分けです。

導入: v2.1.132

---

## stdio MCP サーバ起因のメモリリーク (10GB+ RSS) を修正

:::note alert
対象: MCP サーバを長時間つなぎっぱなしにしている人
:::

stdio 接続の MCP サーバが JSON-RPC プロトコル外のテキスト(ログ・デバッグ出力など)を stdout に書き出すと、Claude 側の受信バッファが解放されず、RSS が 10GB を超えるところまで膨らんでいました。

仕様上 stdio MCP は stdout が完全にプロトコルチャネルなので、サーバ側がうっかり `print()` や `console.log()` を書いただけで顕在化するパターンです。長時間セッションでマシンが重くなる原因に心当たりがあれば、v2.1.132 に上げてください。

MCP 周りでは他にも変更が入っています:

- `tools/list` がサイレントに失敗していた MCP サーバが、リトライ1回 + `/mcp` での `connected · tools fetch failed` 表示に
- 未認可の claude.ai MCP コネクタが `failed` ではなく `needs auth` と表示されるように。`-p` モードの非 transient 4xx 失敗での無限リトライも止まる

導入: v2.1.132

---

## IDE Stop / `kill -INT` で graceful shutdown が走る

:::note info
対象: VS Code / Cursor / JetBrains の Stop ボタンを押した後、`claude --resume` できずに困っていた人
:::

外部 SIGINT(IDE の停止ボタン、`kill -INT $PID`)で Claude Code が中断されると、ターミナルモード(raw mode、alternate screen)の復元が走らず、`--resume` のヒントも出ずに切れていました。v2.1.132 でここが直り、Ctrl+C と同じ graceful shutdown を経由するようになります。

セッションが復元可能になるだけでなく、シェルが raw mode に取り残されて入力が壊れる副作用も解消。

導入: v2.1.132

---

## その他の主な変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.132 | 追加 | `CLAUDE_CODE_SESSION_ID` 環境変数 | Bash tool のサブプロセスで hooks と同じ session_id を参照可能 |
| v2.1.132 | 追加 | "Pasting…" フッタヒント | Ctrl+V で画像をペースト中に表示 |
| v2.1.132 | 修正 | ネイティブビルドのクラッシュ | ターミナルクローズ・SSH 切断時の uncaught exception |
| v2.1.132 | 修正 | `--permission-mode` フラグ無視 | plan-mode セッション復元時に効くように。`ExitPlanMode` 後の plan 再適用も |
| v2.1.132 | 修正 | スリープ復帰後のフルスクリーン空白 | 次のキー入力かストリーム出力まで描画されない |
| v2.1.132 | 修正 | カーソルが grapheme の途中に着地 | Indic conjunct や ZWJ 絵文字の行折返し時に Ctrl+E/A/K/U/矢印で発生 |
| v2.1.132 | 修正 | vim operators が NFD 文字を破壊 | 分解形のアクセント付き文字 |
| v2.1.132 | 修正 | マウスホイールが速すぎる | Cursor / VS Code 1.92–1.104 の xterm.js バグ起因 |
| v2.1.132 | 修正 | JetBrains 2025.2 のスクロール | 偽の矢印キー、逆方向、加速暴走 |
| v2.1.132 | 修正 | `/usage` Ctrl+S が Linux/X11 でハング | スクショのクリップボードコピー処理 |
| v2.1.132 | 修正 | `/effort` picker が env var を無視 | `CLAUDE_CODE_EFFORT_LEVEL` の override が反映 |
| v2.1.132 | 修正 | statusline `context_window` 表示 | 累計ではなく現在のコンテキスト使用量に |
| v2.1.132 | 修正 | Alt+T (thinking toggle) | iTerm2/Terminal.app の "Option as Meta" 未設定環境で効くように |
| v2.1.132 | 改善 | `/login`, `/upgrade`, `/extra-usage` の余白 | ダイアログのビジュアル整理 |

<details><summary>細かいバグ修正(クリックで展開)</summary>

- ペーストにフォーカスイベントやマウストラッキングが混ざり、エスケープ列が垂れ流される問題を修正
- `/terminal-setup` が Windows Terminal で誤ったエラーを表示していた問題を修正(ネイティブで Shift+Enter サポート済み)
- `/status` が一部ユーザで間違ったデフォルトモデルを表示していた問題を修正
- スラッシュコマンドのオートコンプリートが3〜5件で頭打ちだったのを、ターミナル高さに応じて拡張
- Windows で `claude agents` からバックグラウンドセッションを再開した後、キーボード入力が死ぬ問題を修正

</details>

## まとめ

修正25件超に対し、追加機能は env var 3つだけ。安定化に振った週です。fullscreen を理由に 2.1 系を避けていたなら、`CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` で 1.x 系の挙動に戻せます。MCP を常用していて Claude のメモリ消費が気になっていたなら、このバージョンに上げる価値があります。
