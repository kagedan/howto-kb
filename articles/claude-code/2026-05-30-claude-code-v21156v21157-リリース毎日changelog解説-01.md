---
id: "2026-05-30-claude-code-v21156v21157-リリース毎日changelog解説-01"
title: "Claude Code v2.1.156〜v2.1.157 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/c3ffb7ef1058e2403bf1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "VSCode", "qiita"]
date_published: "2026-05-30"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

2.1.156〜2.1.157 の計 2 本を 1 本にまとめて解説します。目玉は `.claude/skills` 配下のプラグインが marketplace 登録なしで自動ロードされるようになったこと。Opus 4.8 を使っているなら thinking ブロック由来の API エラー修正(2.1.156)も効きます。

### 今回の注目ポイント

1. **`.claude/skills` のプラグイン自動ロード** - marketplace 登録が不要に。`claude plugin init` で雛形も生成できる(2.1.157)
2. **`/plugin` の引数補完** - サブコマンド・導入済みプラグイン名・既知マーケットプレイスのプラグインを Tab で補完(2.1.157)
3. **`claude agents` の `--agent` 指定** - `settings.json` の `agent` がディスパッチ時も効くようになり、`--agent <name>` で上書きできる(2.1.157)
4. **Workflow キーワードトリガーの無効化** - プロンプト中の「workflow」で勝手に起動するのを `/config` で止められる(2.1.157)
5. **Opus 4.8 の API エラー修正** - thinking ブロックが改変されてエラーになる問題を解消(2.1.156)

## `.claude/skills` のプラグインが marketplace なしで動く

:::note info
対象読者: スキルやプラグインを自作している人、チーム配布したい人
:::

これまで `.claude/skills` にプラグインを置いても、marketplace に登録しないとロードされませんでした。2.1.157 からは `.claude/skills` 配下を Claude Code が自動で拾います。ローカルで書いたスキルを置くだけで使える。

雛形の生成コマンドも追加されました。

```bash
# .claude/skills/my-tools/ に雛形を作る
claude plugin init my-tools
```

生成された雛形に手を入れて、そのまま自動ロードに乗せられる流れ。marketplace への公開は配布したくなった段階で考えればよくなりました。

合わせて `/plugin` の引数補完も入っています。サブコマンド、導入済みプラグイン名、既知のマーケットプレイス上のプラグイン名を Tab で補完できる。プラグイン名をうろ覚えでも手が止まりません。

---

## `claude agents` で使うエージェントを固定・上書きできる

:::note info
対象読者: サブエージェントを切り替えながら作業する人
:::

`settings.json` の `agent` フィールドが、ディスパッチされたセッションでも有効になりました(2.1.157)。普段使うエージェントを設定に書いておけば、毎回指定する手間が消えます。

その場で変えたいときは `--agent` で上書き。

```bash
# 設定の agent を無視して、この実行だけ別エージェントで起動
claude agents --agent code-reviewer
```

設定でデフォルトを固定し、必要なときだけコマンドで切り替える。両方できます。

---

## Opus 4.8 の thinking ブロック由来 API エラー修正(2.1.156)

Opus 4.8 利用時に thinking ブロックが改変され、API エラーになる不具合が 2.1.156 で修正されました。

1 行の修正ですが、Opus 4.8 を常用しているなら効きます。リクエストが落ちる頻度に直結する修正なので、4.8 を使っているなら 2.1.156 以降に上げておく価値があります。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| 2.1.157 | Workflow | キーワードトリガー設定 | プロンプト内の「workflow」で動的ワークフローが起動するのを `/config` で無効化。トリガー直後の backspace で取り消し(alt+w と同じ)も可能に |
| 2.1.157 | Worktree | セッション中の切り替え | `EnterWorktree` で Claude 管理の worktree 間を実行中に行き来できる |
| 2.1.157 | Worktree | 終了時にアンロック | エージェント完了後は worktree がアンロックされ、`git worktree remove`/`prune` で掃除できる |
| 2.1.157 | Telemetry | パラメータ記録 | `OTEL_LOG_TOOL_DETAILS=1` のとき `tool_decision` イベントに `tool_parameters`(bash コマンド、MCP/スキル名)が入る |
| 2.1.157 | Terminal | 描画安定化 | `/terminal-setup` が VS Code/Cursor/Windsurf 統合ターミナルで GPU アクセラレーションを無効化し、文字化けを防止 |
| 2.1.157 | Performance | 会話再描画の高速化 | 長い会話・再開した会話で冗長なメッセージ再描画計算を排除 |
| 2.1.157 | UI | 起動バナー削減 | 「bash commands will be sandboxed」「/ide for …」の起動時表示を削除。sandbox 状態は `/status` で確認 |

<details><summary>バグ修正(クリックで展開)</summary>

**2.1.157**

- paste / MCP / ダイアログ経由の壊れた画像(0 バイト・破損)がリクエストをクラッシュさせず、テキストプレースホルダになるよう修正
- desktop アプリ・IDE 拡張・SDK で auto / bypass-permissions モード時に sandbox のネットワーク許可プロンプトが出る問題を修正
- `claude agents` で、アイドルのサブエージェントが残留したりバックグラウンドシェルがリークしていると完了セッションが retire されない問題を修正
- `claude agents` で「opening…」が遅いときに Esc でキャンセルできずリストが固まる問題を修正
- 30 日のジョブ保持スイープ後に `.claude/worktrees/` 配下のバックグラウンドエージェント worktree が孤立する問題を修正
- スリープ/復帰後に再アタッチしたバックグラウンドセッションが、モデルに正しい日付を伝えない問題を修正
- tmux で `set-clipboard on` のとき `claude agents` の copy-on-select がシステムクリップボードに届かない問題を修正(2.1.153 のリグレッション)
- `--resume` が、前回プロセス終了時に動いていたバックグラウンドサブエージェントを報告しない問題を修正
- `--resume` のセッションピッカーが、フルスクリーンモードで終了後に内容を端末に残す問題を修正
- `--worktree` および `--worktree --tmux` が、現在のリンク済み worktree ではなくリポジトリルートに戻る問題を修正
- `/model` ピッカーが、選択中モデルが同系統で最新でも「新しいバージョンあり」と誤表示する問題を修正。ピン留め行は raw ID ではなく説明を表示
- フルスクリーンモードで進行中メッセージにマークダウン記号(バッククォート・アスタリスク)がそのまま出る問題を修正
- 起動時の managed-settings セキュリティダイアログ承認後に端末が固まる問題を修正
- 端末 UI 再描画後にスクロールバックへ重複行がまれに出る問題を修正
- VS Code / Cursor / Windsurf 統合ターミナルで右クリックペーストがクリップボードを重複させる問題を修正
- WSL: 画像ペースト(`alt+v`)、Windows 11 でのスクリーンショットペーストを修正。Windows Explorer からの画像ドラッグに対応
- `claude agents` のディスパッチ入力でスラッシュコマンド補完が部分一致するように
- [IDE] バックグラウンドサブエージェント実行中に Stop を押しても止まらない問題を修正
- [VSCode] Opus 4.8 で fast モードインジケータが出ない問題を修正
- Feature of the Week のクレジット請求ステータスを、プロンプト上部の行ではなくステータス領域の通知として表示

**2.1.156**

- Opus 4.8 で thinking ブロックが改変され API エラーになる問題を修正

</details>

## まとめ

2.1.157 の主役はプラグイン周り。`.claude/skills` に置くだけで動き、`claude plugin init` で雛形まで用意できる。ローカルの `.claude/skills` に置いて試すまでが一手で済みます。Opus 4.8 を使っているなら、API エラー修正の入った 2.1.156 以降への更新を優先してください。
