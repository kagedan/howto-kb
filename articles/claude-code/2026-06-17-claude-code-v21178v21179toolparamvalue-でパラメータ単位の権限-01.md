---
id: "2026-06-17-claude-code-v21178v21179toolparamvalue-でパラメータ単位の権限-01"
title: "Claude Code v2.1.178〜v2.1.179｜Tool(param:value) でパラメータ単位の権限制御｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/aa08e8d2c5cf5aa0e731"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "qiita"]
date_published: "2026-06-17"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.178 で permission ルールが `Tool(param:value)` 形式に対応した。これまでツール単位でしか許可・拒否できなかったが、ツールに渡る入力パラメータの値まで見て弾けるようになった。`settings.json` の `permissions` を細かく書いているほど挙動が変わる。

## 今回の注目ポイント

1. **`Tool(param:value)` でパラメータ単位の権限制御** — `Agent(model:opus)` のように入力値を見て許可・拒否できる。`*` ワイルドカードも可 (v2.1.178)
2. **auto モードがサブエージェント起動前に分類** — 起動前に分類器が評価し、ブロック対象のアクションを素通りさせない (v2.1.178)
3. **ネストした `.claude` は近い定義が優先** — 作業ディレクトリに最も近い agent / workflow / output-style が衝突時に勝つ (v2.1.178)
4. **接続切れで部分応答を保持** — 途中で切れても生エラーにせず応答を残す。スピナーの running tool 固着も解消 (v2.1.179)
5. **compaction が `--fallback-model` を尊重** — overload やモデル不可時にフォールバックモデル連鎖へ落ちる (v2.1.178)
6. **Linux サンドボックスの glob 肥大化を修正** — 巨大ディレクトリへの `denyRead`/`allowRead` で Bash ツール記述が膨張しセッション不能だった問題 (v2.1.179)

## パラメータ単位の権限ルール `Tool(param:value)`

:::note info
対象読者: `settings.json` の `permissions` で allow / deny を細かく書いている人。
:::

**ツール名だけでなく、ツールに渡る入力パラメータの値で許可・拒否できるようになった。** v2.1.178 で追加された `Tool(param:value)` 構文がそれ。

公式が挙げる例は `Agent(model:opus)`。Opus を使うサブエージェントの起動だけをブロックする書き方。値には `*` ワイルドカードが使える。

```json
{
  "permissions": {
    "deny": ["Agent(model:opus)"]
  }
}
```

ただし changelog が触れているのは構文の追加まで。対応パラメータの一覧やマッチ仕様は原文に無い。`*` を絡めた指定は挙動を確認してから本番ルールに入れてください。

## 接続が切れても応答が消えなくなった

ストリーミング中に接続が切れると、それまでの部分応答が生エラーに置き換わって消えていた。長い生成の途中で落ちると、出力を丸ごと失う。v2.1.179 でここが直り、部分応答はそのまま残るようになった。

あわせて、スピナーが running tool のまま固まる問題も解消。ツール実行の途中で切れても進行表示が止まらなくなった。

## auto モードがサブエージェントを起動前に止める

auto モードで、サブエージェントの起動を分類器が起動前に評価するようになった (v2.1.178)。これまではサブエージェント経由ならブロック対象のアクションをレビューなしで要求できる隙があり、その経路が塞がれた。

:::note warn
permission を厳しく運用しているなら、サブエージェント発の操作も auto モードの判定対象に入る。意図せず止まるケースが出たらルールを見直してください。
:::

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.178 | スキル | ネスト `.claude/skills` の読み込み | 作業中ディレクトリ配下のスキルも読み込み、名前衝突時は `<dir>:<name>` で両方残る |
| v2.1.178 | 設定解決 | ネスト `.claude` の優先順位 | 作業ディレクトリに最も近い agent / workflow / output-style が衝突時に勝つ |
| v2.1.178 | workflow | キーワード起動を厳格化 | run a workflow や workflow: など明示句のみで起動。紫シマーで強調 |
| v2.1.178 | /bug | 説明を必須化 | 説明なしでは送信不可。モデル拒否テキストを issue タイトルに使わない |
| v2.1.178 | MCP | サブエージェント `disallowedTools` を修正 | `mcp__server` / `mcp__*` 等のサーバ単位指定が無視されていた問題 |
| v2.1.178 | 認証 | リフレッシュ後の auth エラーを修正 | セッション外で資格情報を更新しても古いキャッシュ設定で失敗が続いていた問題 |
| v2.1.179 | UI | WSL2 マウスホイールスクロール修正 | Windows Terminal / VS Code 上で効かなかった問題 (2.1.172 のリグレッション) |
| v2.1.179 | サブエージェント | Ctrl+O でトランスクリプト表示 | サブエージェント閲覧中に Ctrl+O が効かなかった問題 |

## まとめ

v2.1.178 の中心は `Tool(param:value)` によるパラメータ単位の権限制御。サブエージェントのモデル指定まで踏み込んでルールを書ける。v2.1.178 は権限まわりの締め直し、v2.1.179 は接続切れ時の応答保持を含むバグ修正が中心。
