---
id: "2026-05-28-claude-code-v21152-リリース毎日changelog解説-01"
title: "Claude Code v2.1.152 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/408f349397dd1dda3cc3"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-05-28"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.152 は `/code-review --fix` の追加と、スキル・フック拡張が中心の更新。中でも刺さるのは、レビュー結果をそのままコードへ書き戻す `--fix` ですよね。

今回の注目ポイント:

1. **`/code-review --fix` が指摘を作業ツリーに適用** レビュー後に reuse・simplification・efficiency の提案をコードへ直接反映。`/simplify` も同じ経路に統合
2. **スキルが `disallowed-tools` でツールを封印** frontmatter 指定で、スキル実行中だけ特定ツールをモデルから外せる
3. **`/reload-skills` で再起動なしのスキル再読込** セッションを保ったままスキルディレクトリを再スキャン
4. **モデル未検出時に `--fallback-model` へ自動切替** primary model が無くても毎リクエスト失敗せず、セッションを継続
5. **Vim NORMAL モードの `/` が逆方向履歴検索に** bash/zsh の vi-mode と同じ Ctrl+R 相当の挙動
6. **Auto モードが opt-in 同意不要に** 初回の同意ステップを削除

## `/code-review --fix`: 指摘を読んで直す往復を消す

:::note info
対象読者: PR 前のセルフレビューを回している人、レビュー指摘の手直しが面倒な人
:::

`/code-review` はこれまで指摘を一覧で出すだけだった。出た指摘を読み、該当箇所を探し、手で書き換える。指摘の数だけ、この往復が続く。

v2.1.152 の `--fix` は、レビュー後に提案を作業ツリーへ直接書き戻す。対象は次の通り。

- reuse: 重複コードの集約
- simplification: 冗長なロジックの簡素化
- efficiency: 効率化の余地

```bash
# レビューだけ(従来通り、指摘を出して終わり)
/code-review

# レビュー結果を作業ツリーに適用
/code-review --fix
```

書き戻した後は `git diff` で確認し、要らない変更を捨てればいい。指摘テキストとコードを目で突き合わせる作業がまるごと消える。

`/simplify` も内部で `/code-review --fix` を呼ぶようになった。簡素化だけ手早くかけたいときは `/simplify`、レビュー全体を回したいときは `/code-review --fix`。用途で選べる。

---

## スキル実行中だけツールを取り上げる

:::note info
対象読者: スキル・スラッシュコマンドを自作している人
:::

スキルとスラッシュコマンドの frontmatter に `disallowed-tools` を書けるようになった(v2.1.152)。スキルがアクティブな間だけ、指定したツールをモデルの手から外す。読み取り専用で調査させたいスキルから `Write`・`Edit` を封じる、といった制御ができる。

開発ループも軽くなった。`/reload-skills` でセッションを保ったままスキルディレクトリを再スキャンできる。SessionStart フックが `reloadSkills: true` を返せば、フックがインストールしたスキルを同じセッションで即使える。書いて、読み込んで、試す。これが再起動なしで回る。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.152 | Hooks | `MessageDisplay` イベント追加 | アシスタントのメッセージ表示時に、テキストを変換・非表示にできる |
| v2.1.152 | Hooks | `SessionStart` で `sessionTitle` 指定 | 起動・再開時にセッションタイトルを設定できる |
| v2.1.152 | Plugins | `pluginSuggestionMarketplaces` 管理設定 | 提案を許可する組織マーケットプレイスを管理者が allowlist 化 |
| v2.1.152 | Plugins | `marketplace remove --scope` | `user` / `project` / `local` を指定可能に。`add`/`install` と対称化 |
| v2.1.152 | UI | Thinking サマリーの表示改善 | 折りたたみ時に最低3秒表示、markdown レンダリング、10行で打ち切り |
| v2.1.152 | UI | フルスクリーンの思考時間表示 | "Thinking for Ns" が思考中もライブ加算、中断しても値を保持 |
| v2.1.152 | UI | Workflow ツールの進捗表示を簡素化 | ライブのエージェント数をプロンプト下の常設行だけに集約 |
| v2.1.152 | UI | バックグラウンド完了待ちの表示 | "Waiting for N background agents/workflows to finish" を表示 |
| v2.1.152 | 計測 | `/usage` が大きいセッションファイルを集計 | ストリーミング読み込みでメモリ使用量を平坦に保つ |
| v2.1.152 | 計測 | OpenTelemetry に `app.entrypoint` | セッションの起点を属性として記録(`OTEL_METRICS_INCLUDE_ENTRYPOINT=true` で opt-in) |

## バグ修正

表示・プラグイン・MCP 接続まわりが中心。

<details><summary>バグ修正(v2.1.152、16件)</summary>

- 長時間セッションでターミナル装飾が劣化する問題を修正(レンダラのスタイルプールを再利用)
- condensed 起動表示で sandbox 有効の警告が出ない問題を修正。全レイアウトで表示されるように
- ツール実行中にローディングが "still thinking" / "almost done thinking" と出続ける問題を修正。ツールごとに "thinking" へリセット
- 非表示アクティビティが無いターンで focus モードが "N messages hidden" を誤表示する問題を修正
- 展開したツール結果内のリンクをクリックすると、リンクを開かずセクションが折りたたまれる問題を修正
- markdown テーブルのセル罫線がインラインコードの色を継ぐ問題、折り返し行がスタイルを失う問題、空ヘッダーセルにラベルが出る問題を修正
- コマンドが同じで環境変数だけ異なるプラグイン MCP サーバーが誤って重複排除される問題を修正
- 削除済みマーケットプレイスやドロップされたプラグインを参照する `enabledPlugins` で、`/doctor` が "marketplace not found" / "plugin not found" を出す問題を修正
- git ブランチを追従するプラグインが、レジストリ再構築後に更新を受け取らなくなる問題を修正
- egress プロキシ有効時に、Claude Code Remote セッションでリモート MCP サーバーが接続できない問題を修正
- メッセージが無い、または同じ値に解決される effort レベル間の切替で、確認ダイアログが出る問題を修正
- `--bare` や添付無効時に配信されないエージェント一覧を、Agent ツールの説明が参照する問題を修正
- subagent キャンセル後に古い権限プロンプトを承認した際の、`claude agents` バックグラウンドワーカークラッシュを修正
- API が `cache_creation` のネスト内訳でのみキャッシュ書き込みを報告する際、`cache_creation_input_tokens` が 0 になる問題を修正
- Remote Control 有効の SDK ホストセッションで、PushNotification ツールが "Mobile push not sent (Remote Control inactive)" を誤報告する問題を修正
- モデルやログイン切替後、古い thinking ブロック署名が履歴に残りセッションが固まる問題を修正(先回りで除去し、リトライのセーフティネットを追加)

</details>

## まとめ

v2.1.152 の中心は `/code-review --fix`。レビューと修正の間にあった手作業を、`git diff` の確認だけに圧縮する。スキルを書く人なら `disallowed-tools` と `/reload-skills` で、権限を絞ったスキルをセッションを切らずに書き直せる。
