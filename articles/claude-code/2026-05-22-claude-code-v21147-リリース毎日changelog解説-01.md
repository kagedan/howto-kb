---
id: "2026-05-22-claude-code-v21147-リリース毎日changelog解説-01"
title: "Claude Code v2.1.147 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/9b8a0e25b3daaae074c3"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-22"
date_collected: "2026-05-22"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

2026-05-21 リリースの v2.1.147 を読みます。目玉は新しい `Workflow` ツールと、`/simplify` を置き換えた `/code-review` の挙動変更。裏で PowerShell と Windows の細かい修正もまとめて入っています。

### 今回の注目ポイント

1. **`Workflow` ツールが新登場** - 決定的なマルチエージェント編成。`CLAUDE_CODE_WORKFLOWS=1` でオプトイン
2. **`/simplify` が `/code-review` にリネーム** - effort レベル指定と PR への直接コメント投稿ができる
3. **ピン留め背景セッションが落ちにくくなった** - `Ctrl+T` でピン留めすればアップデートもその場で反映
4. **REPL と Workflow のサンドボックス強化** - prototype-pollution と thenable 経由の脱出を同時に塞いだ
5. **自動アップデータの失敗時診断が具体化** - OS エラーコード・現バージョン表示・通信失敗のリトライ
6. **プロンプト履歴の連続重複が排除** - `↑` で呼び出して再送しても履歴が膨らまない

---

## `Workflow` ツールで多エージェントを決定的に動かす

:::note info
対象: 複数のエージェントを毎回同じ手順で走らせたいレビューアー・自動化担当
:::

`Workflow` ツールは、エージェントの組み合わせ・分岐・順序をスクリプトとして固定するための仕組みです。LLM の判断に任せず、フローを固定したいケースで使います。

デフォルト無効。使うには環境変数を入れてから Claude Code を起動します。

```bash
CLAUDE_CODE_WORKFLOWS=1 claude
```

セキュリティ面で同時に固められたのが、Workflow ツールと REPL のサンドボックス。`Object.prototype` を汚染する経路と、Promise の `then` を握って実行コンテキストを抜ける経路をどちらも今回のリリースで塞いでいます。

---

## `/simplify` から `/code-review` へ

旧 `/simplify` のクリーンアップ＆修正動作は廃止。新しい `/code-review` はバグ指摘専任のコマンドになりました。

| 操作 | 効果 |
|---|---|
| `/code-review` | 既定の effort で正しさのバグを指摘 |
| `/code-review high` | 高 effort で深く検査 |
| `/code-review --comment` | 検出結果を GitHub PR のインラインコメントとして投稿 |

`--comment` をつけると、レビュー結果がそのまま PR 上のコメントになります。ローカルにログを抱えなくても、PR 上で議論を続けられる構成です。ただし `/simplify` のクリーンアップ機能は `/code-review` に引き継がれていないので、使い続けていた人は気をつけてください。

---

## ピン留め背景セッションが粘る

`claude agents` 画面でセッションを選び `Ctrl+T` でピン留めしておくと、これまでアイドル時に切られていたセッションがそのまま生き残ります。挙動は次のとおり。

- アイドルでも終了しない
- Claude Code 本体のアップデートはピン留めセッションをその場で再起動して反映
- メモリ不足時の解放は非ピン留めセッションを先に対象とし、ピン留めは最後

監視系・ポーリング系のエージェントを `Ctrl+T` で固定しておけば、再起動のたびに状態を組み立て直す手間が減ります。

---

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.147 | パフォーマンス | 大ファイル編集の diff 描画 | 大規模 edit の diff 表示を高速化 |
| v2.1.147 | 体験 | プロンプト履歴の連続重複排除 | `↑` 連打で同じプロンプトを再送しても履歴に積まれない |
| v2.1.147 | アップデータ | 自動更新の失敗時メッセージ強化 | エラーカテゴリ・OS エラーコード・現バージョンを表示。一時的な通信失敗はリトライ |
| v2.1.147 | エンタープライズ | `forceLoginOrgUUID` / `forceLoginMethod` | サードパーティプロバイダや API キーセッションにも管理設定が効くように修正 |
| v2.1.147 | ヘッドレス | 未知のスラッシュコマンド | SDK / headless で無反応だったのをエラー表示に修正 |
| v2.1.147 | クリップボード | ペースト内容の保持 | `[Pasted text #N]` プレースホルダではなく実テキストが届くように |
| v2.1.147 | バックグラウンド | 権限プロンプトの再表示 | 「Don't ask again」した権限がバックグラウンドセッションで再度聞かれていた挙動を修正 |

<details>

<summary>バグ修正(v2.1.147)</summary>

- `!` コマンド出力の `&` が `&amp;` で表示され、`gcloud auth login` 等の URL がコピペできない
- `/help` のタブヘッダーが崩れ、小さなターミナルで 1 ページに 1 コマンドしか表示されない
- シェルスナップショットがアンダースコア始まり(`_func`)のユーザー関数を落とし、関連エイリアスが壊れる
- プラグインの agent frontmatter の `tools:` に複数 `Agent(...)` を書くと最後の 1 つ以外が消える
- フック条件 `PowerShell(git push*)` が一切マッチせず、`PowerShell(*)` しか効かなかった
- PowerShell ツールがデフォルトフォーマッタ依存のコマンドで出力を落とす
- Windows の「Yes, and don't ask again」がスクリプト呼び出しに対して後続実行へマッチしないルールを書いていた
- winget / Microsoft Store 経由で入れた `pwsh` で PowerShell ツールが終了コード 1 で落ちる
- `/effort` がスライダーを現在値ではなく違うレベルで開く
- MCP サーバーのページング 2 ページ目以降で resources / templates / prompts が抜け落ちる
- アタッチ中のバックグラウンドセッションが Windows Terminal でストリーミング中に全画面ストロボする
- Windows でバックグラウンドジョブの worktree 削除が NTFS ジャンクションを辿ってメインリポを巻き込む
- 入力がスキルやカスタムスラッシュコマンドだけのセッションを `/background` が拒否する
- ユーザーやスキルが `AskUserQuestion` を必要とする場面で auto モードがそれを抑制する
- `/theme` の「新規カスタムテーマ」とカラーエディタの Esc が効かない
- Agent SDK のストリーミングセッション終了時の uncaught exception
- Windows でスクロール終端検知がまれにハングする
- Windows のエージェント一覧で背景セッション結果に CJK 等の wide 文字が含まれると行が古いまま・重複する
- `claude plugin details` と `/plugin` のプラグイン構成要素カウントが、マニフェストでデフォルトディレクトリと重複するパスを宣言したときに倍化する
- GNOME Terminal の右クリック・中クリックペーストが本文に入らない
- `CLAUDE_CODE_SUBAGENT_MODEL` がエージェントチームの子プロセスに伝わらない
- スラッシュコマンド直後のタブ・改行が未知コマンド扱いされる
- `/plugin` / `/status` / `/mobile` / `/sandbox` / `/permissions` メニューのスペーシング・レイアウトの細かいズレ
- 削除済み画像をモデルが繰り返し再読み込みしようとする

</details>

## まとめ

Workflow ツールが入って、Claude Code は対話エージェントだけでなく決まった手順を流す実行基盤としても動かせます。`/code-review --comment` と組み合わせれば、PR レビューの一次切り分けまで Claude Code 内で完結。あわせて Windows と PowerShell 周りの細かい修正もまとめて入っています。
