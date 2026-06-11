---
id: "2026-06-11-claude-code-v21172-リリース毎日changelog解説-01"
title: "Claude Code v2.1.172 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/90ccc7a4c0595a51c1cf"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "VSCode", "qiita"]
date_published: "2026-06-11"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.172 が公開。サブエージェントが自分のサブエージェントを呼べるようになった回ですよね。残りはほぼバグ修正だが、permission ルールと 1M コンテキスト周りに実害のある修正が混ざっている。

## 今回の注目ポイント

1. **サブエージェントの多階層ネスト** - サブエージェントが自身のサブエージェントを最大 5 階層まで起動できるように
2. **1M コンテキストのスタック自動回避** - クレジット無しで 1M を使ったセッションが固まる不具合を修正。標準上限まで自動圧縮して復帰
3. **WebFetch のワイルドカードドメイン許可が機能するように** - `*.example.com` がサブドメインに一切マッチしなかったバグを修正
4. **`/plugin` にプラグイン検索バー** - マーケットプレイスのプラグイン一覧を絞り込み可能に
5. **Bedrock が `~/.aws` からリージョンを読む** - `AWS_REGION` 未設定時に AWS SDK と同じ優先順で解決
6. **長い会話とアイドル時の負荷を軽減** - 冗長なメッセージ正規化を削除、アイドル時の再描画を抑制

以降で触れる変更はすべて v2.1.172。

## サブエージェントが、サブエージェントを呼ぶ

:::note info
対象読者: サブエージェントで調査や実装を並列化している人
:::

これまでサブエージェントは末端だった。親が分割したタスクを受け取り、自分で処理して返すだけ。今回からそのサブエージェント自身が、さらに別のサブエージェントを起動できる。深さは最大 5 階層。

大きめのリファクタや横断調査を、再帰的に分解できるようになる。

```
親エージェント
├─ 子: 認証まわりを調査
│   ├─ 孫: login.ts を精査
│   └─ 孫: session.ts を精査
└─ 子: 課金まわりを調査
    └─ 孫: webhook 受信処理を精査
```

親が領域で割り、子が領域内をファイル単位で割り、孫が個別ファイルを読む。これまで親 1 段で抱えていた分割を、各層に押し下げられる。

ただし 5 階層という上限がある。無限に増殖して並列度が破綻するのを防ぐためのキャップ。深いネストを組むときは、各層が何を返すかを明示しておかないと、孫の出力が親まで素通りして文脈が薄まる。

---

## WebFetch の `*.example.com` 許可が、ずっと効いていなかった

permission でワイルドカードドメインを許可・拒否している設定向けの修正。

`WebFetch(domain:*.example.com)` を allow に書いても、`docs.example.com` のようなサブドメインに一切マッチしていなかった。allow だけでなく deny、ask でも同じ。さらに `Read(secrets-*/config.json)` のようなパターン途中にワイルドカードを置いたルールは、起動時に弾かれてエラーになっていた。

```json
// settings.json: これまで素通り、または起動エラーになっていたルール
{
  "permissions": {
    "allow": ["WebFetch(domain:*.anthropic.com)"],
    "deny": ["Read(secrets-*/config.json)"]
  }
}
```

deny で塞いだつもりが素通りだったケースも含まれる。ワイルドカードで許可・拒否を細かく書いている設定ほど、意図とのズレが大きかった修正。一度 `settings.json` を読み直す価値がある。

## 1M コンテキストのスタックが自動で解ける

usage クレジット無しで 1M コンテキストを使うと、セッションが永久に固まることがあった。今回からは標準コンテキスト上限まで自動でコンパクト(圧縮)し、固まらずに処理を続ける。

## その他の変更

| カテゴリ | 変更点 | 概要 |
|---|---|---|
| 機能追加 | `/plugin` 検索バー | マーケットプレイスのプラグイン一覧を検索 |
| 機能追加 | Bedrock リージョン解決 | `~/.aws` から読み、`/status` に取得元を表示 |
| 計測 | OTEL `lines_of_code.count` | `model` 属性を追加 |
| パフォーマンス | 長い会話 | 冗長な正規化とフル変換を削減 |
| パフォーマンス | アイドル CPU | `/goal` チップの 5Hz 再描画を停止 |
| パフォーマンス | Claude in Chrome | ブラウザツールを 1 回のバッチでロード |
| UX | `/code-review ultra` | claude.ai 未サインインでも選択肢を表示 |
| UX | Remote Control | フッター表示を "/rc active" に短縮 |

<details><summary>その他のバグ修正(v2.1.172)</summary>

- 複数画像を含む会話で「an image ... could not be processed」エラーが繰り返す不具合
- agents view でワーカー応答後も最大 30 秒スピナーが回り続ける不具合
- バックグラウンドエージェントが別ディレクトリのプロジェクト設定(`.mcp.json` 承認、trust)を読む可能性
- 旧バージョンで開始したバックグラウンドセッションへの attach が daemon 自動更新後に EAUTH で失敗
- ネストした子エージェント停止後もバックグラウンドサブエージェントが "active" のまま固まる
- `claude agents` の `/model` 候補が誤ったスラッシュ接頭辞で表示、組織で無効化済みモデルも表示
- `availableModels` 制限がサブエージェントのモデル上書き、dispatch ピッカー、advisor モデルに未適用
- `availableModels` 許可リストが `claude-opus-4-8` のような version-specific ID 使用時に Opus / Sonnet 1M 行を隠す
- Bedrock の `/model` ピッカーが提供外モデルを表示、選択でサイレントにセッションモデルを切替
- `ANTHROPIC_DEFAULT_OPUS_MODEL` に既にサフィックスがある場合の `[1M][1m]` 二重表示
- `opusplan` がプランモードで 1M コンテキストを伴わない不具合、`opusplan[1m]` 回避策も修正
- 上矢印のプロンプト履歴が、サブエージェントのチャットタブ表示中にメイン側のプロンプトを表示
- リモートセッションでマウントされた team memory stores(`CLAUDE_MEMORY_STORES`)をメモリリコールが見つけられない
- workflow 検証が `Date.now()` / `Math.random()` に言及しただけのコメント・文字列を誤って拒否
- マウストラッキングを未対応の Windows コンソールで無効化
- `/plugin` マーケットプレイス一覧が長いリストから戻るとカーソルを失う、Esc で誤ったタブに戻る
- 非インタラクティブの Usage Policy 拒否メッセージを改善し、新規セッション開始やモデル変更を案内
- リモートで `/loop` の宣伝を停止(pending loop がコンテナを保持しないため)
- [VSCode] PowerShell ツールコールが生 JSON で表示される不具合を修正、表示シェル出力から ANSI エスケープを除去

</details>

## まとめ

目玉はサブエージェントの再帰ネスト。ただ実務でいま効くのは WebFetch のワイルドカード許可と 1M スタックの修正のほう。とくに前者は allow と deny がこれまで意図通り動いていなかったので、permission を細かく書いているなら挙動が変わる。
