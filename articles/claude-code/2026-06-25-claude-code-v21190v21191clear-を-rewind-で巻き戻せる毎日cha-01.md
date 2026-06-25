---
id: "2026-06-25-claude-code-v21190v21191clear-を-rewind-で巻き戻せる毎日cha-01"
title: "Claude Code v2.1.190〜v2.1.191｜/clear を /rewind で巻き戻せる｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/f64cef66531e691d05c4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-06-25"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

`/clear` で消したはずの会話に、`/rewind` で戻れるようになった。これまで `/clear` は取り消し不能で、誤って実行したら直前までのやり取りは戻らなかった。v2.1.190 は信頼性修正のみなので、本体は v2.1.191。

## 今回の注目ポイント

1. **`/clear` の前まで `/rewind` で戻れる** クリアした会話を巻き戻して再開できる (v2.1.191)
2. **停止したエージェントが復活しなくなった** tasks パネルからの停止が恒久化 (v2.1.191)
3. **カンマ区切り matcher の hooks 不具合を修正** `"Bash,PowerShell"` が黙って素通りしていた (v2.1.191)
4. **ストリーミング中の CPU を約37%削減** テキスト更新を100msでまとめる (v2.1.191)
5. **`/permissions` の拒否取り消しが保存される** Recently-denied タブで承認しても破棄されていた (v2.1.191)
6. **MCP の capability discovery と OAuth がリトライ対応** 一過性のネットワークエラーを再試行 (v2.1.191)

## `/clear` の前まで戻れる `/rewind`

**`/clear` で消した会話が、`/rewind` で復元できるようになった。** (v2.1.191)

`/clear` は会話履歴をまるごと捨てるコマンド。コンテキストをリセットしたいときに使うが、押した瞬間に直前までのやり取りは戻らなかった。タスクの途中で誤爆すると、組み立てた文脈を一から作り直すことになる。

v2.1.191 の `/rewind` は、`/clear` を実行する前の地点まで会話を巻き戻せる。クリア直後でも、`/rewind` で `/clear` 前の状態に復帰できる。

:::note info
対象読者: `/clear` でコンテキストを区切りながら長いセッションを回している人。誤爆のリスクが一つ減る。
:::

## カンマ区切り matcher の hooks が発火しない不具合

`"Bash,PowerShell"` のように複数ツールをカンマでまとめた matcher が、これまで一度も発火していなかった。

:::note warn
カンマ区切り matcher で hooks を組んでいるなら要確認。v2.1.191 から実際に発火するようになるので、これまで素通りしていた hook が動き出す。想定どおりの挙動か見ておいてください。
:::

## ストリーミング中の CPU が約37%軽くなった

**応答のストリーミング表示中の CPU 使用率を、約37%削減した。** (v2.1.191) テキスト更新を100msごとにまとめることで実現している。

あわせて、長時間セッションでターミナル出力キャッシュによるメモリ増加も抑えた。スクロール位置が応答中に勝手に最下部へ飛ぶ不具合も直っている。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.191 | sandbox | ネットワーク許可の記憶 | 「Yes」で許可したホストをセッション中は再プロンプトしない |
| v2.1.191 | MCP | HTTP 404 エラーの改善 | URL と MCP 設定箇所を表示するように |
| v2.1.191 | 設定管理 | forceRemoteSettingsRefresh の修正 | MDM / file policy 経由でも有効化。`Cache-Control: no-cache` でプロキシの stale 応答を防止 |
| v2.1.191 | UI | welcome splash の表示崩れ修正 | 80×24 の macOS Terminal で枠からはみ出ていた |
| v2.1.190 | 全般 | 信頼性改善 | バグ修正と安定性向上のみ |

## まとめ

目玉は `/clear` を取り消せる `/rewind`。誤爆からの復帰手段が一つ増えた。カンマ区切り matcher の hooks はこれまで無言で死んでいたので、組んでいるなら発火を確認しておく。
