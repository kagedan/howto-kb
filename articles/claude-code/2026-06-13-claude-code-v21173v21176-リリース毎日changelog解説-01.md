---
id: "2026-06-13-claude-code-v21173v21176-リリース毎日changelog解説-01"
title: "Claude Code v2.1.173〜v2.1.176 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/397036a48b61dd257ef9"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "VSCode", "qiita"]
date_published: "2026-06-13"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.173〜v2.1.176 の計4本を1本にまとめます。今回は新機能より、モデルの統制とバックグラウンド / Remote Control まわりの修正が中心です。

## 今回の注目ポイント

1. **会話の言語でセッションタイトル生成** - タイトルが会話と同じ言語で作られる (v2.1.176)
2. **availableModels の統制が Default にも効く** - 環境変数や /fast での抜け道を塞ぐ (v2.1.175 / v2.1.176)
3. **/usage に利用内訳が出る** - cache miss・subagent・skill 別を 24h / 7d で表示 (v2.1.175, VSCode)
4. **/model ピッカーが Default の実体を表示** - 解決先のモデル家系を独立した行で見せる (v2.1.174)
5. **footerLinksRegexes でフッターにリンクバッジ** - 正規表現にマッチしたリンクをバッジ表示 (v2.1.176)

## 会話の言語でセッションタイトルが付く

:::note info
対象読者: 日本語など、英語以外でClaude Codeを使っている人
:::

これまでセッションタイトルは英語で生成されていました。v2.1.176 からは会話の言語に合わせて生成されます。日本語でやり取りしていれば、タイトルも日本語。

言語を固定したいときは `language` 設定で指定します。

```json
// ~/.claude/settings.json
{
  "language": "ja"
}
```

設定を入れなければ、その時々の会話言語に追従します。固定したい場合だけ書けば十分。

---

## availableModels がモデル選択の抜け道を塞いだ

:::note info
対象読者: チームや組織でモデルを制限している管理者、managed settings を運用している人
:::

`availableModels` で使えるモデルを絞っていても、これまでは抜け道があった。環境変数 `ANTHROPIC_DEFAULT_*_MODEL` に別名を渡すと、ブロックしたはずのモデルへ redirect できてしまう。Default モデルが allowlist 外に解決されるケースも素通りだった。

v2.1.175 で `enforceAvailableModels` という managed 設定が入りました。有効にすると挙動が変わります。

- Default が許可外モデルに解決される場合、allowlist の先頭モデルに fallback する
- user / project 設定で、managed の `availableModels` リストを広げられなくなる

```json
// managed-settings.json
{
  "enforceAvailableModels": true,
  "availableModels": ["claude-opus-4-8", "claude-sonnet-4-6"]
}
```

v2.1.176 ではさらに穴がふさがれました。

- alias でのモデル選択を `ANTHROPIC_DEFAULT_*_MODEL` 経由でブロック対象に redirect できない
- `/fast` が allowlist 外のモデルへ切り替わる場合、トグル自体を拒否する

要は、組織で「このモデルしか使わせない」を環境変数や `/fast` で迂回できなくなった、ということ。managed settings でモデルを統制しているなら、`enforceAvailableModels` を有効化して設定を見直す価値があります。

---

## /usage で使用量の内訳が見える (VSCode)

:::note info
対象読者: トークン消費を把握したい人、サブエージェントや skill を多用する人
:::

VSCode 拡張の Account & usage ダイアログ (`/usage`) に、使用量の attribution が追加されました (v2.1.175)。直近 24h または 7d で、次の内訳が出ます。

- cache miss
- long context
- subagents
- skill / agent / plugin / MCP 別の breakdown

何がトークンを食っているのかが分解して見えるように。Workflow でサブエージェントを大量に回す使い方だと、コストがどこに乗っているか追えます。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.176 | 認証 | Bedrock 認証情報キャッシュ | `awsCredentialExport` の認証情報を固定1時間でなく `Expiration` まで保持 |
| v2.1.176 | モデル | auto モードの fallback | Opus 4.8 未開放の組織で Fable 5 が落ちず、最善の Opus に fallback |
| v2.1.175 | 内部 | skill ホットリロード | 1つ変更時に全 skill 一覧を再送せず、変更分だけ再通知 |
| v2.1.174 | UI | `wheelScrollAccelerationEnabled` | フルスクリーンのマウスホイール加速を無効化する設定 |
| v2.1.173 | モデル | Fable 5 `[1m]` 接尾辞 | 1M context が標準のため `[1m]` を自動で除去 |

<details>
<summary>バグ修正 (v2.1.173〜v2.1.176)</summary>

**Remote Control / バックグラウンド (v2.1.176)**

- Remote Control 接続でセッションのモデルが勝手に切り替わる
- 切断通知が人間可読の理由でなく数値コードだけを表示、接続失敗時に会話ログへ重複行が出る
- 別アカウントにサインインしても Remote Control が切断されない
- `/bg` をターン途中で実行し継続対象が無いと "Working" が消えない
- `claude agents` で別ウィンドウの back が同一セッションの他ウィンドウを detach する
- cloud session が長時間 idle 後に "Could not resolve authentication method" で失敗
- (Windows) agents ビューの入力にカーソルが出ない / daemon が ReadOnly 属性で起動しない

**モデル・課金 (v2.1.174 / v2.1.175)**

- `/model` ピッカーが `ANTHROPIC_DEFAULT_SONNET_MODEL` 指定時もハードコードの Sonnet ラベルを表示
- "Fable 5 is now consuming usage credits" バナーが従量課金のエンタープライズに誤表示
- Bedrock GovCloud (`us-gov-*`) が `global` prefix を導出して 400 エラー
- `/advisor` ダイアログが allowlist でブロック済みのモデルを事前選択
- git commit の co-author に一部モデルで誤ったモデル名

**その他**

- hook の `if` 条件で `Edit(src/**)` `Read(.env)` などのパスが正しくマッチ (v2.1.176)
- Linux sandbox が `settings.json` の絶対パス symlink で起動失敗 (v2.1.176)
- `/copy`・マウス選択コピーが tmux over SSH でシステムクリップボードに届かない (v2.1.176)
- `/cd`・worktree 移動後も前ディレクトリの git ブランチを報告 (v2.1.176)
- background session が別 session の `ANTHROPIC_*` env を継承 (v2.1.175)
- macOS / Linux でシェルコマンド中断直後の終了が1-2秒遅延 (v2.1.175)
- (Windows) 偽の "sandbox dependencies missing" 起動警告 (v2.1.173)

</details>

## まとめ

v2.1.173〜v2.1.176 は機能追加より足回りの強化。組織で `availableModels` を運用しているなら、`enforceAvailableModels` で環境変数経由の抜け道が塞がった点は要チェック。Remote Control とバックグラウンドセッションの修正も多く、リモートからセッションを操作している人は今回の更新で挙動が安定します。
