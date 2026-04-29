---
id: "2026-04-29-claude-code-v21121-リリース毎日changelog解説-01"
title: "Claude Code v2.1.121 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/fbf4e1c6ed0629c2c248"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "qiita"]
date_published: "2026-04-29"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.121 は MCP 周りの強化と、長時間セッションを破綻させていたメモリリーク修正が中心ですよね。tool-search の遅延読み込みをサーバ単位でオフにできる `alwaysLoad` も地味な効き目。フックの `updatedToolOutput` もついに全ツール対応へ。

## 今回の注目ポイント

1. **MCPサーバ全ツールを常時ロード** - `alwaysLoad: true` で tool-search 経由の遅延読み込みをスキップ
2. **PostToolUse フックで全ツール出力を書き換え可能に** - `hookSpecificOutput.updatedToolOutput` が MCP 限定から解放
3. **メモリリーク3件まとめて修正** - 画像処理で数GB に膨らむ RSS、`/usage` の約2GB リーク、長時間ツールの解放漏れ
4. **`claude plugin prune` 追加** - 孤立した自動インストール済みプラグイン依存を一掃
5. **フルスクリーンモードのスクロール挙動改善** - 入力中に末尾へ戻されない、長いダイアログも矢印キー対応
6. **`/skills` に検索ボックス** - 多数のスキルから目的の1つを即座に絞り込める

## 1. MCPサーバごとに「全ツール常時ロード」を選べる `alwaysLoad`

:::note info
**対象**: MCPサーバを複数登録していて、特定サーバのツールを必ず使うケース
:::

`alwaysLoad: true` を MCP server config に書くと、そのサーバの全ツールが tool-search 経由の遅延読み込みをスキップして即時利用可能になります。

これまで tool-search は「使う直前にサーチで呼び出す」ワンクッションが入る前提でした。コンテキスト節約には効きますが、社内検索や定常監視のように毎回必ず使う MCP は最初から常駐させたい。`alwaysLoad` はそこを直接指定する逃げ道です。

```json
{
  "mcpServers": {
    "internal-search": {
      "command": "node",
      "args": ["./internal-search-mcp.js"],
      "alwaysLoad": true
    }
  }
}
```

全 MCP に `true` を入れるとコンテキストを食うので、本当に常駐させたいサーバだけに限定するのが現実的です。

入ったバージョン: v2.1.121

---

## 2. PostToolUse フックで「全ツール」の出力を差し替え可能に

:::note info
**対象**: ツール出力にフィルタを噛ませたい、リダクションや整形を自動化したいフック開発者
:::

これまで MCP ツール限定だった `hookSpecificOutput.updatedToolOutput`。v2.1.121 から Bash, Read, Edit, Grep など全ツールに対象が広がりました。

書き換えるのはあくまで「Claude が見る結果」のみ。ツール実行そのものは通常通り走るので、副作用を変えずにコンテキストへ流す内容だけを整えられます。

擬似レスポンス:

```json
{
  "hookSpecificOutput": {
    "updatedToolOutput": "REDACTED: 17 secrets removed"
  }
}
```

ハマる用途:

- `Bash` のログから API キー・トークン・社外秘を伏せる
- `Read` 結果の特定パス(機密リポジトリ等)を除外
- `Grep` の生出力を「3件マッチ、上位2件: ...」のように圧縮してトークン消費を抑える
- `Edit` の diff から自動生成ノイズ(.lock や .min.js)を消す

実装で1つ落とし穴。空の `updatedToolOutput` を返すと出力がそのまま空文字に置き換わって Claude が状況を読めなくなります。書き換え条件に当てはまらなければ、`updatedToolOutput` キーごと省くのが無難。

入ったバージョン: v2.1.121

---

## 3. 数GB級だったメモリリーク3件をまとめて潰す

長時間セッション派には地味に効きます。

| 現象 | 修正内容 |
|---|---|
| 画像を多数扱うと RSS が数GB単位で増え続ける | 解放漏れを修正 |
| `/usage` 実行で約2GB リーク(履歴の大きいマシン) | トランスクリプト走査の参照保持を解消 |
| 長時間ツールが進捗イベントを出し損ねるとリーク | progress 監視のタイマー漏れを修正 |

「半日使っているとMacのファンが回り続ける」「`/usage` を叩いた瞬間に重くなる」覚えがあるなら、v2.1.121 にあげるだけで体感が変わります。

入ったバージョン: v2.1.121

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.121 | プラグイン | `claude plugin prune` | 孤立した自動インストール済みプラグイン依存を削除。`plugin uninstall --prune` で連鎖削除 |
| v2.1.121 | UI | `/skills` 検索ボックス | 入力でフィルタ。長いリストでもスクロール不要 |
| v2.1.121 | UI | フルスクリーンのダイアログをスクロール可 | 矢印キー、PgUp/PgDn、home/end、マウスホイール対応 |
| v2.1.121 | UI | 折り返した URL の全行クリックで開ける | 行をまたぐ長い URL でも全体が起点に |
| v2.1.121 | UI | フルスクリーン入力中のスクロールジャンプ抑制 | 上方向に読みに行ってもツール完了で末尾に戻されない |
| v2.1.121 | SDK | `CLAUDE_CODE_FORK_SUBAGENT=1` 非対話セッション対応 | `claude -p` でも有効に |
| v2.1.121 | 権限 | `--dangerously-skip-permissions` の挙動修正 | `.claude/skills/`, `.claude/agents/`, `.claude/commands/` への書き込みで確認しない |
| v2.1.121 | 連携 | iTerm2 クリップボード許可を自動設定 | `/terminal-setup` がチェックを入れ、tmux 経由の `/copy` も動作 |
| v2.1.121 | MCP | 起動時エラーの自動リトライ | 最大3回、以前は1回失敗で切断のまま |
| v2.1.121 | UI | ターミナルタブのセッションタイトルを言語設定で生成 | `language` 設定に従う |
| v2.1.121 | 接続 | claude.ai コネクタを URL で重複排除 | 同一 URL を複数登録しても1つにまとまる |
| v2.1.121 | 認証 | Vertex AI で X.509 mTLS ADC 対応 | Workload Identity Federation を証明書ベースで利用可 |
| v2.1.121 | UI | 起動高速化 | リリースノートの "Recent Activity" パネル削除 |
| v2.1.121 | UI | LSP 診断サマリの展開 | クリックまたは Ctrl+O で展開、ヒント表示 |
| v2.1.121 | SDK | `mcp_authenticate` の `redirectUri` 対応 | カスタムスキームと claude.ai コネクタ向け |
| v2.1.121 | OTel | LLM スパンに `stop_reason` 等追加 | `gen_ai.response.finish_reasons`、`user_system_prompt`(`OTEL_LOG_USER_PROMPTS` ゲート) |
| v2.1.121 | VSCode | 音声入力が `accessibility.voice.speechLanguage` 尊重 | Claude Code 側に言語設定がない場合 |
| v2.1.121 | VSCode | `/context` がトークン使用ダイアログで開く | プレーンテキスト返却ではなくネイティブ UI |

<details><summary>v2.1.121 のバグ修正一覧</summary>

- メモリリーク3件(本文セクション3で詳述)
- `Bash` ツールが、起動ディレクトリ削除/移動でセッション中ずっと使えなくなる問題
- `--resume` が外部ビルドで起動時クラッシュ
- `--resume` が大規模セッションでトランスクリプト破損行に当たると失敗。破損行をスキップして継続するように
- Bedrock の application inference profile ARN で `thinking.type.enabled is not supported` エラー
- Microsoft 365 MCP の OAuth が重複/未対応の `prompt` パラメータで失敗
- 非フルスクリーン下で Ctrl+L や再描画時にスクロールバック重複(tmux / GNOME Terminal / Windows Terminal / Konsole)
- claude.ai MCP コネクタが起動時のコネクタ一覧取得で一時認証エラーに遭うと無言で消える問題
- リモートセッションのビルトインツール「Always allow」ルールがワーカ再起動後に消える
- `managed-settings.json` 配下のネイティブビルドで `NO_PROXY` が一部 HTTP クライアントに反映されない
- 管理設定承認プロンプトを Accept してもセッション終了。適用して継続するように
- 古い OAuth トークンで `/usage` が「rate limited」表示。自動リフレッシュで解消
- `settings.json` の不正な旧 enum 値で設定全体が無効化される問題
- `/usage` ダイアログが no-flicker オフ時にクリッピング
- フルスクリーンレンダラがオフのとき `/focus` が "Unknown command" 表示。有効化方法を案内
- 組み込み grep/find/rg のシェルラッパが、実行中バイナリが削除されると失敗。インストール済みツールにフォールバック
- 大規模ディレクトリツリーでの `find` のピーク fd 使用量を削減

</details>

## まとめ

v2.1.121 は派手な目玉機能こそ少ないものの、`alwaysLoad` とフック `updatedToolOutput` の全ツール解放という MCP/フック開発者目線で確実に効く変更が入りました。長時間セッションでメモリが膨らんでいた人は、メモリリーク修正だけでも上げる価値があります。
