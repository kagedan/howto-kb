---
id: "2026-06-04-claude-code-v21162-リリース毎日changelog解説-01"
title: "Claude Code v2.1.162 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/c31d5e74c50848db7859"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "qiita"]
date_published: "2026-06-04"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

2.1.162 は新機能控えめの磨き込み回で、中身は `claude agents` の表示崩れ修正と権限・MCP まわりのバグ潰しが大半。ただスラッシュコマンドのクリック挙動が変わったので、マウス派は操作感が変わりますよね。

## 今回の注目ポイント

1. **スラッシュコマンドのクリックで即実行されなくなった** オートコンプリートをクリックすると prompt に挿入されるだけ。実行は Enter。
2. **WebFetch の権限ルールがプリアプルーブドドメインに優先** 明示した `WebFetch(domain:...)` の deny / ask / allow が自動許可より先に効く。
3. **`--tools` で Grep/Glob 明示が有効に** ネイティブビルドで専用検索ツールを提供。以前は名前が無視されていた。
4. **設定ディレクトリが書き込み不可でも起動する** ブランク画面でハングせず、in-memory config で起動してエラーを表示。
5. **MCP の timeout が 1000ms 未満でも全ツールが死なない** 1秒 watchdog が全ツールコールを abort していたバグを修正。
6. **`/effort` がデフォルト保存を確認** 選んだレベルが新セッションの既定になると明示するように。

## クリックでコマンドが暴発しなくなった

:::note info
対象読者: スラッシュコマンドをマウスで選んでいる人
:::

オートコンプリートメニューのスラッシュコマンドをクリックすると、これまでは即実行。`/clear` を選ぼうとして誤爆、という事故があった。2.1.162 からはクリックで prompt 欄に挿入されるだけ。実行には Enter のワンステップが要る。

キーボードで Tab 補完していた人には影響なし。マウスで選ぶ人だけ、確認のひと押しが増える。

---

## WebFetch の権限ルールがプリアプルーブドに勝つ

:::note info
対象読者: settings.json で WebFetch の許可ドメインを絞っている人
:::

Claude Code には WebFetch で自動許可されるドメイン(プリアプルーブドホスト)がある。2.1.161 までは、ここに対して自前の deny ルールを書いても適用されず素通りしていた。社内ドメインを塞いだつもりが塞げていない、という権限の穴。

2.1.162 で、明示した `WebFetch(domain:...)` ルールがプリアプルーブドの自動許可より優先されるようになった。

```json
// .claude/settings.json
{
  "permissions": {
    "deny": ["WebFetch(domain:internal.example.com)"]
  }
}
```

これで内部ドメインへの WebFetch を確実に止められる。ask / allow も同様に優先。deny で社内ドメインを塞いでいたなら、2.1.161 以前は素通りしていたことになる。

合わせて Windows の権限ルールも直っている。`~\` や `\\server\share` のようなバックスラッシュ表記、大文字小文字違いのパスがマッチしなかった問題と、Read の deny ルールが Glob/Grep の結果からファイルを隠せていなかった問題。Windows で権限ルールを書いているなら要確認。

---

## MCP の timeout が 1秒未満でも全ツールが死ななくなった

:::note info
対象読者: MCP サーバーを複数繋いでいる人
:::

MCP はサーバーごとに `timeout` を設定できる。ただ 1000ms 未満の値を入れると 1秒の watchdog に切り下げられ、その watchdog が全ツールコールを abort していた。短いタイムアウトを設定したつもりが、逆に全ツールが即死する罠。

2.1.162 では 1000ms 未満の値は無視され、`MCP_TOOL_TIMEOUT` か既定値にフォールバックする。

```json
// .mcp.json
{
  "mcpServers": {
    "fast-api": { "command": "...", "timeout": 500 }
  }
}
```

`claude mcp get` でも、その値が無視された旨を注記する。1000ms 未満を設定していたなら、これまで全ツールコールが abort されていたことになる。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| 2.1.162 | CLI | `claude agents --json` に `waitingFor` 追加 | 待機中セッションが何でブロックされているか(権限プロンプト等)を表示 |
| 2.1.162 | CLI | `--tools` で Grep/Glob 明示が有効に | ネイティブビルドで専用検索ツールを提供。以前は無視されていた |
| 2.1.162 | UI | `/effort` がデフォルト保存を確認 | 選んだレベルが新セッションの既定になると明示 |
| 2.1.162 | UI | Remote Control がフッターピル化 | 起動メッセージでなく常設フッター。セッションへのリンク付き |
| 2.1.162 | UI | Launch-prompt 警告を入力欄下にピン留め | ディープリンク / 事前入力プロンプトの警告が、操作するまで流れず残る |
| 2.1.162 | 名称 | Windsurf を Devin Desktop に改名 | `/ide` `/terminal-setup` `/scroll-speed` をエディタのリブランドに追従 |
| 2.1.162 | 起動 | 設定ディレクトリ書き込み不可時のハング修正 | in-memory config で起動してエラーを表示。ブランク画面を解消 |
| 2.1.162 | 起動 | 起動表示を整理 | 通知を重大度でグループ化、警告を短文化、失敗ターンを1行警告に、Chrome / marketplace 等の起動メッセージを quiet notices 化 |
| 2.1.162 | 起動 | バイナリ検証の待機を改善 | EDR スキャン中に 5秒で失敗せず待つように |

バグ修正:

<details><summary>2.1.162 のバグ修正(クリックで展開)</summary>

- Esc をターン開始直後に送ると stream-json/SDK セッションで握り潰され、ターンが無反応のまま走り続けていた問題を修正
- 絵文字が切り詰め境界付近にある分類器サイドクエリ / MCP サーバー説明で API 400 `no low surrogate in string` が出ていた問題を修正
- LSP ツールの `workspaceSymbol` が結果を返さなかった問題を修正(`query` パラメータを受け取り言語サーバーに渡すように)
- `claude agents` のライブステータス(ツール引数 / 返信 / プロンプト / 実行出力)が 60〜120 列で切れていた問題を修正。ターミナル幅いっぱいを使うように
- `claude agents` が長いセッション名を 40 列で切っていた問題を修正
- `claude agents` の attach がバックグラウンドサービス再起動直後の初回にセッション一覧へ跳ね返る問題を修正
- `claude agents` の Ctrl+V 画像ペーストが効かなかった問題を修正。画像なしの貼り付けはヒントを表示
- ← でセッションをバックグラウンド化した際、バックグラウンドサービスが起動できないと会話が消えていた問題を修正。失敗行として一覧に残り Enter で復帰可能に
- agents ビューからの返信が送信失敗時に失われていた問題を修正。次回セッション起動時の配信用にキューイング
- `CLAUDE_CODE_TMPDIR` や `$TMPDIR` が深い階層を指すとクロスセッションメッセージング(`SendMessage`)が無言で壊れる問題を修正
- `claude agents` から実行中のバックグラウンドセッションを開くと attach 前に 5秒ストールする問題を修正
- バックグラウンド dispatch の spawn 失敗時、errno が無い場合にエラークラス名を報告するように

</details>

## まとめ

2.1.162 は派手な新機能こそ無いが、権限と MCP の穴を塞ぐ実用的な修正が詰まっている。特に WebFetch の deny ルールが効いていなかった件は、権限設定の前提が崩れる。settings.json で WebFetch を絞っているなら、2.1.162 で挙動を確認しておく価値がある。
