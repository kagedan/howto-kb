---
id: "2026-06-07-claude-code-v21166v21167-リリース毎日changelog解説-01"
title: "Claude Code v2.1.166〜v2.1.167 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/dab2d73fbb0ce6eea33d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-06-07"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.166〜v2.1.167 の計 2 本を 1 本にまとめてお届けします。v2.1.167 はバグ修正のみ。中身はほぼ v2.1.166 に詰まっていますよね。モデル過負荷で止まる問題への対策がまとめて入りました。

## 今回の注目ポイント

1. **フォールバックモデルを最大3つ指定** - 主モデルが過負荷でも順番に切り替えて止まらない (v2.1.166)
2. **deny ルールに glob 対応** - `"*"` でツールを全拒否、ホワイトリスト運用が楽に (v2.1.166)
3. **クロスセッションメッセージの権限剥奪** - 他セッションから中継された指示が勝手に承認されない (v2.1.166)
4. **think 既定モデルの thinking を明示オフ** - `MAX_THINKING_TOKENS=0` が Claude API モデルにも効く (v2.1.166)
5. **想定外エラーで1回だけ自動リトライ** - フォールバックモデルに切り替えて再試行 (v2.1.166)
6. **`claude update` がDL前に対象バージョンを表示** - 無言でフリーズしたように見えなくなった (v2.1.166)

## フォールバックモデルを最大3つまで連鎖指定できる

:::note info
対象読者: ピーク時間帯に `overloaded` でセッションが止まって困っている人
:::

`fallbackModel` 設定で、主モデルが過負荷・利用不可のときに試すモデルを**最大3つまで順番に**並べられるようになりました (v2.1.166)。

```json
// settings.json
{
  "model": "claude-opus-4-8",
  "fallbackModel": [
    "claude-sonnet-4-6",
    "claude-haiku-4-5"
  ]
}
```

Opus が詰まったら Sonnet、それもダメなら Haiku、と上から順に試す。1つでも空いていれば応答が返る。

もう1つ大きいのが、`--fallback-model` フラグの適用範囲。これまで非対話(`-p`)実行だけだったのが、対話セッションにも効くようになりました。

```bash
claude --fallback-model claude-sonnet-4-6
```

対話中に `overloaded` で固まっても、自動で次のモデルに切り替わって応答が返ります。

---

## deny ルールのツール名に glob が書ける

権限設定の deny ルールで、ツール名の位置に glob パターンを書けるようになりました (v2.1.166)。`"*"` 単体は全ツール拒否。

```json
{
  "permissions": {
    "deny": ["*"],
    "allow": ["Read", "Grep", "Glob"]
  }
}
```

全部閉じてから必要なものだけ開ける、ホワイトリスト運用がそのまま書けます。ただし allow 側は MCP 以外の glob を弾きます。`allow: ["*"]` のような雑な全許可は通らない、という非対称な設計。deny で不明なツール名を書くと起動時に警告が出ます。

## 他セッションから中継されたメッセージはユーザー権限を持たない

`SendMessage` で別の Claude セッションから中継されたメッセージが、ユーザー本人の権限を引き継がなくなりました (v2.1.166)。受信側は中継された permission request を拒否し、auto モードでもブロックします。

マルチエージェント構成で、片方のセッションを乗っ取れればもう片方に好き放題コマンドを通せる、という権限昇格の穴を塞いだ変更。複数セッションを連携させている人は、この回以降を前提にしておくと安全です。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| 2.1.166 | モデル | thinking 無効化の徹底 | `MAX_THINKING_TOKENS=0`・`--thinking disabled`・モデル別トグルが、既定で think する Claude API モデルにも効くように(3Pプロバイダは変更なし) |
| 2.1.166 | 信頼性 | 想定外エラーのリトライ | API が想定外の non-retryable エラーを返したとき、フォールバックモデルで1回だけ再試行。認証・レート制限・リクエストサイズ・transport エラーは即時表面化 |
| 2.1.166 | UX | `claude update` の進捗表示 | DL開始前に対象バージョンを告知。無言で固まったように見えなくなった |
| 2.1.166 | UX | `claude agents` のURLフィルタ | 一覧にURLを入力すると、最初のプロンプトにそのURLを含むセッションへ絞り込み |

<details><summary>バグ修正(v2.1.166、クリックで展開)</summary>

- 処理不能な画像送信時の `image could not be processed` エラーと、それに伴う余分なトークン消費を修正
- 起動時の worker 登録中にバックエンドが瞬断すると、リモートセッションが永久にスタックする問題を修正
- JetBrains IDE(IntelliJ・PyCharm・WebStorm 等)2026.1+ のターミナルのちらつきを synchronized output 有効化で修正
- Kitty keyboard protocol 使用ターミナル(WezTerm・Ghostty・kitty)で Shift+非ASCII文字(例: Shift+ä → Ä)が落ちる問題を修正
- Windows で、kill されたプロセスの子が出力パイプを握ったまま PowerShell コマンド検証が時間予算を大幅超過してハングする問題を修正
- macOS で daemon 死亡後に孤立した `claude --bg-pty-host` プロセスが100% CPUで回り続ける問題を修正
- `/voice` トグル後、stale な認証チェックの解消に `/login` が必要だった voice mode の問題を修正
- managed settings に1つでも無効なエントリがあると、残りの有効なポリシーの enforcement まで黙って無効化される問題を修正
- managed-settings の `allowedMcpServers`/`deniedMcpServers` 述語が `${VAR}` 参照を使うとマッチしない問題を修正
- git worktree に入ったバックグラウンドエージェントセッションを `claude agents` から再開すると `No conversation found` でクラッシュループする問題を修正
- Ctrl+O のトランスクリプト表示で、ストリーミング中に thinking テキストが重複する問題を修正
- リモートセッション内で `/doctor` を実行すると `Not inside a remote session` チェックが矛盾した失敗を表示する問題を修正
- `claude agents` の dispatch/reply 入力で、複数行プロンプト入力時にカーソルが1行目末尾に張り付く問題を修正
- Unicode 非対応ターミナルで、タスク一覧のバックグラウンドエージェント行間に空行が入る問題を修正

</details>

## まとめ

v2.1.166 はモデルの可用性まわりを固めた回。`fallbackModel` の連鎖指定と対話セッションへの `--fallback-model` 適用で、ピーク時の `overloaded` 停止がかなり減ります。権限まわりも deny の glob 対応とクロスセッションメッセージの権限剥奪で一段堅くなりました。v2.1.167 はバグ修正のみなので、アップデートするなら v2.1.166 の中身を押さえておけば十分です。
