---
id: "2026-05-29-claude-code-v21153v21154-リリース毎日changelog解説-01"
title: "Claude Code v2.1.153〜v2.1.154 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/d42ad8905e76c9b7a0c1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "qiita"]
date_published: "2026-05-29"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.153〜v2.1.154 の計 2 本を 1 本にまとめて解説します。同じ日に新モデル Opus 4.8 と、裏で数百エージェントを束ねる dynamic workflows が同時に着弾した回ですよね。エージェント基盤まわりの修正も濃いめ。

今回の注目ポイント:

1. **Opus 4.8 が登場** — 既定で high effort、最難関タスク向けに `/effort xhigh` を新設（v2.1.154）
2. **dynamic workflows** — 数十〜数百のエージェントをバックグラウンドで束ねて 1 タスクを処理（v2.1.154）
3. **Opus 4.8 の Fast mode** — 標準の 2 倍料金で 2.5 倍速。以前より大幅に安く（v2.1.154）
4. **lean system prompt が既定に** — Haiku / Sonnet / Opus 4.7 以前を除く全モデルで適用（v2.1.154）
5. **多肢選択の質問を自制** — 文脈で判断できる場面では聞かずに進む（v2.1.154）
6. **`/model` の選択がデフォルト保存に** — 今回だけ切り替えるなら picker で `s`（v2.1.153）

## Opus 4.8 が既定モデルに

:::note info
対象読者: 普段から Opus を回していて、effort の使い分けを詰めたい人
:::

v2.1.154 で Opus 4.8 が入りました。既定の effort は high。さらに最難関タスク向けの最上位として `/effort xhigh` が増えています。

```
/effort xhigh   # 最難関タスク向けの最上位
/effort high    # Opus 4.8 の既定
```

スライダーのラベルも変わりました。「Speed」「Intelligence」から「Faster」「Smarter」へ。速度優先か品質優先かを、ラベルから直接読めます。

Fast mode も同じ v2.1.154 で Opus 4.8 に対応。標準の 2 倍の料金で 2.5 倍速という設定で、以前の Fast mode より大幅に安くなっています。なお旧 `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE` は非推奨化され、06/01 に削除予定。Opus 4.6 で Fast mode を使うなら `/model claude-opus-4-6[1m]` で切り替えてから `/fast on` という手順に変わります。

---

## dynamic workflows でエージェントを束ねる

:::note info
対象読者: 大規模リファクタや横断調査を 1 セッションで回したい人
:::

Claude にワークフローの作成を頼むと、数十〜数百のエージェントへ作業をオーケストレーションし、バックグラウンドで進めます。1 つのコンテキストに収まらない規模のタスクを、丸ごと投げられるようになったということ。

```
> このリポジトリ全体の未使用エクスポートを洗い出して削除するワークフローを作って

（Claude がワークフローを組み、エージェント群が裏で並走）

/workflows   # 実行中・完了したランの一覧を表示
```

手元のセッションを占有せずに進むので、重い一括処理を投げたまま別の作業へ戻れます。進捗とログは `/workflows` から追えます。

---

## `/model` の保存挙動が変わった

v2.1.153 で `/model` の挙動が IDE 版に揃いました。選んだモデルが新規セッションの既定として保存されます。今回のセッションだけ変えたいときは、picker で `s` を押す。

```
/model   # 選んだモデルが新規セッションの既定になる
         # 今回のセッションだけなら picker で s
```

キーバインドをカスタムしている人は注意が要ります。`d` のアクションが `s` に置き換わったため、`keybindings.json` の `modelPicker:setAsDefault` は `modelPicker:thisSessionOnly` にリネームしてください。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.154 | レビュー | `/simplify` がクリーンアップ専用に | バグ探索を伴わず、再利用・簡素化・効率・粒度の整理だけ実行して適用 |
| v2.1.154 | agents | `! <command>` でシェルをバックグラウンド実行 | `claude --bg --exec '<command>'` でも起動でき、後からアタッチ/デタッチ可能 |
| v2.1.154 | MCP | stdio サーバへ環境変数を注入 | サブプロセスに `CLAUDE_CODE_SESSION_ID` と `CLAUDECODE=1` を渡す |
| v2.1.154 | MCP | 未承認 `.mcp.json` を自動接続しない | パイプ出力時も `⏸ Pending approval` と表示するだけに |
| v2.1.154 | プラグイン | `defaultEnabled: false` を宣言可能 | 既定で無効にし `/plugin` や `claude plugin enable` で有効化。依存は自動で有効 |
| v2.1.154 | 安全性 | auto-mode の流出検知を強化 | リポジトリ内容の一括転送を重点的に検出 |
| v2.1.154 | ツール実行 | ストリーミング実行が常時有効に | Bedrock / Vertex / Foundry やテレメトリ無効時も対象（旧フラグを撤廃） |
| v2.1.153 | プラグイン | `skipLfs` オプション追加 | git / github マーケットプレースの clone・update で Git LFS の取得を省略 |
| v2.1.153 | status line | `COLUMNS` / `LINES` を渡す | スクリプトが端末幅に合わせて出力サイズを調整できる |
| v2.1.153 | doctor | 直近の更新結果を表示 | `claude doctor` で前回の `claude update` の成否が分かる |
| v2.1.153 | macOS | バックグラウンドエージェントが「Claude Code」表示に | プライバシーとセキュリティ上の権限がアップグレード後も維持される |

<details><summary>バグ修正（v2.1.153〜v2.1.154）</summary>

**v2.1.154**
- `HOME` が末尾スラッシュ付きのとき `rm -rf $HOME` が危険パスとしてブロックされない問題を修正
- `$TMPDIR` が同一セッション内でサンドボックス有無により別ディレクトリに解決される問題を修正
- バックグラウンドエージェントの完了通知が、一部 1M コンテキストモデルで早すぎる「out of context」挙動を誘発する問題を修正
- バックグラウンドセッションのサブエージェントが worktree 隔離ガードを迂回し、共有チェックアウトへ書き込む問題を修正
- macOS でデーモン終了後に `claude --bg-pty-host` プロセスが 100% CPU で残る問題を修正
- 1 件の不正な `allowedMcpServers` / `deniedMcpServers` エントリが managed-settings ポリシー全体を破棄する問題を修正（該当エントリのみ破棄し `claude doctor` で警告）
- `CLAUDE_CODE_ALWAYS_ENABLE_EFFORT` 設定時に、effort 非対応モデルで API 400 が出る問題を修正
- 安全性分類器が出力トークンを使い切った際、auto mode が誤って操作をブロックする問題を修正

**v2.1.153**
- カスタム API ゲートウェイに、ゲートウェイ自身のトークンではなくユーザーの Anthropic OAuth 認証情報が渡る回帰を修正
- サブエージェント（Agent ツール）frontmatter の MCP サーバが `--strict-mcp-config` や managed-settings の許可/拒否ポリシーを無視する問題を修正
- ステートフル MCP サーバ（GET SSE ストリーム未提供）が `tools/list` で再接続ループする問題を修正（v2.1.147 の回帰）
- 多数のセッションを保存したマシンで、transcript ファイルパス指定の再開時に数 GB のメモリを消費する問題を修正
- Windows PowerShell インストーラがインストール失敗時にも「Installation complete!」と表示する問題を修正
- npm 版で `claude update` が、設定したリリースチャンネルの版ではなく最新版をインストールする問題を修正
- `subagent_type: 'claude'` の Agent ツールが未文書の一時 worktree で走り、gitignore 対象への出力を黙って捨てる問題を修正

</details>

## まとめ

v2.1.154 は Opus 4.8 と dynamic workflows という大物が同時に来た回。Opus 4.8 で 1 エージェントの精度が上がり、workflows で同時に動かせる数が数十〜数百規模に増えました。v2.1.153 は `/model` のデフォルト保存とキーバインド変更が手元に効くので、カスタム勢は `keybindings.json` の確認を。
