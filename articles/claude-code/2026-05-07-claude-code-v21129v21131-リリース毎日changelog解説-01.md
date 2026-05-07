---
id: "2026-05-07-claude-code-v21129v21131-リリース毎日changelog解説-01"
title: "Claude Code v2.1.129〜v2.1.131 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/ca528c5eaee11b779dbf"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "qiita"]
date_published: "2026-05-07"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.129〜v2.1.131 の計 2 本を 1 本にまとめてお届けします。新機能と地味に効くバグ修正が両方詰まっていますよね。

## 今回の注目ポイント

1. **URL からプラグインを直接ロードする `--plugin-url` 追加** - `.zip` を fetch して現在のセッションに適用 (v2.1.129)
2. **1時間 prompt cache TTL がサイレントに5分へ縮んでいたバグ修正** - `/effort` や `/model` 切り替え後の cache miss も同根 (v2.1.129)
3. **Homebrew/WinGet 用の自動アップデート** - `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` でバックグラウンド更新+再起動プロンプト (v2.1.129)
4. **Ctrl+R 履歴検索が全プロジェクト横断に復帰** - Ctrl+S で現プロジェクト/セッションに絞る (v2.1.129)
5. **`/context` の ASCII ビジュアル出力削除** - 1呼び出しあたり約1.6kトークン節約 (v2.1.129)
6. **VS Code 拡張の Windows 起動失敗修正** - createRequire ポリフィルのバンドルバグを解消 (v2.1.131)

---

## URL から直接プラグインを取ってくる `--plugin-url`

:::note info
Claude Code のプラグインを社内配布したい / GitHub Releases の `.zip` をそのまま試したい人向け。
:::

```bash
claude --plugin-url https://example.com/my-plugin.zip
```

これだけで指定 URL の `.zip` をフェッチし、現在のセッションでプラグインとして読み込みます。マーケットプレイスや `~/.claude/plugins/` に置く前のお試し導入、社内 CDN からの配布、PR ブランチの成果物検証あたりが一発で通るようになる形。

ただし対象は当該セッション限定。永続化したい場合は従来通り通常のインストール経路を踏む必要があります。 (v2.1.129 で追加)

---

## 1時間の prompt cache TTL が裏で5分に縮められていたバグ修正

:::note info
長尺の context を保持しつつ `/effort` や `/model` を切り替えるワークフローの人向け。
:::

1時間 TTL を指定した prompt cache が、実際は5分で揮発していました。同じ根として、`/clear` や compaction の後に `/effort` や `/model` を切り替えた直後に「cache miss」警告がスプリアスに出る挙動も観測されていたところ。今回これらが揃って直り、宣言通り1時間効きます。

5分と60分ではヒット率の桁が変わるので、トークンコスト面の影響は素直に大きいバグ。長尺の system プロンプトや MCP サーバ定義を抱えたまま `/effort high` ↔ `/effort medium` を行き来する人ほど、月のトークン消費が変わる規模の修正です。 (v2.1.129 で修正)

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.129 | 機能追加 | `CLAUDE_CODE_FORCE_SYNC_OUTPUT=1` | Emacs `eat` など自動検出漏れの端末で synchronized output を強制 ON |
| v2.1.129 | 機能追加 | `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` | Homebrew / WinGet 環境でバックグラウンド upgrade + 再起動プロンプト |
| v2.1.129 | 仕様変更 | プラグインマニフェスト | `themes` / `monitors` を `"experimental": { ... }` 配下へ移動。トップレベル宣言は `claude plugin validate` で警告 |
| v2.1.129 | 仕様変更 | Gateway `/model` 自動探索 | `/v1/models` の discovery は `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` でオプトイン化 (v2.1.126〜v2.1.128 は自動だった) |
| v2.1.129 | 操作感 | Ctrl+R 履歴検索 | デフォルトで全プロジェクト横断に戻る。Ctrl+S で現プロジェクト/セッションに絞る |
| v2.1.129 | 体験改善 | サードパーティ deployment | Bedrock / Vertex / Foundry / `ANTHROPIC_BASE_URL` で Anthropic 一次面のスピナーチップを非表示 |
| v2.1.129 | 設定 | `skillOverrides` | `off` / `user-invocable-only` / `name-only` がきちんと効くように |
| v2.1.129 | 観測 | OTel `claude_code.pull_request.count` | MCP 経由で作成された PR / MR もカウント対象に |
| v2.1.129 | 観測 | ポリシー拒否エラー | エラーメッセージに API Request ID を併記 |

### バグ修正(全件)

<details><summary>v2.1.129 / v2.1.131 のバグ修正一覧</summary>

- 400 status の不明エラーで raw JSON が出ていたのを内側のメッセージ表示に変更 (v2.1.129)
- `/clear` 後にターミナルタブのタイトルがリセットされない (v2.1.129)
- パーミッションダイアログ表示中に `/rename` 由来のセッションタイトルチップが消える (v2.1.129)
- サブエージェント実行中にプロンプト下のエージェントパネルが隠れる (v2.1.122 のリグレッション、v2.1.129 で修正)
- Ctrl+G の外部エディタ往復で会話履歴が空になる (v2.1.129)
- `/context` のレンダリング ASCII グリッドが会話に出力され約1.6kトークン消費していた (v2.1.129)
- `/agents` Library のリストでハイライト位置がビューポート外に出る (v2.1.129)
- `/branch` の成功メッセージに `/resume` 用の session id が含まれていない (v2.1.129)
- フルスクリーンモードで keycap / ZWJ / 肌色絵文字を含む太字見出しの末尾文字が欠ける (v2.1.129)
- `user:inference` スコープを欠いた OAuth 認証情報で server-managed settings ポリシーが適用されない (v2.1.129)
- スリープ復帰後の OAuth refresh レースで全セッションがログアウトする (v2.1.129)
- 1時間 prompt cache TTL がサイレントに5分へダウングレードされる (v2.1.129)
- `/clear` や compaction 後の `/effort` / `/model` 変更で cache-miss 警告がスプリアス発生 (v2.1.129)
- `Bash(mkdir *)` / `Bash(touch *)` などの allow ルールがプロジェクト内パスで効かない (v2.1.129)
- `deniedMcpServers` の `*://` スキームワイルドカードが大文字小文字混在ホストにマッチしない (v2.1.129)
- `--debug` の voice mode で無害な WebSocket 警告が error として記録される (v2.1.129)
- VS Code: `/clear` で会話 context と表示中のトランスクリプトが消えない (v2.1.129)
- VS Code 拡張が Windows でハードコードされたビルドパス起因の createRequire ポリフィルバグで activate 失敗 (v2.1.131)
- Mantle エンドポイントの認証で `x-api-key` ヘッダが欠落していたのを修正 (v2.1.131)

</details>

## まとめ

v2.1.129 は機能追加よりもバグ修正の手数で押した感触のリリース。特に1時間 prompt cache TTL 周りの修正は、長時間セッションを回している人ほど効いてくる地味だが効果の大きい改善です。v2.1.131 は VS Code (Windows) と Mantle 認証のホットフィックス2件で、該当環境の人は即更新推奨。
