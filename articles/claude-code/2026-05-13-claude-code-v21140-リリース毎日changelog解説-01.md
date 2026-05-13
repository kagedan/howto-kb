---
id: "2026-05-13-claude-code-v21140-リリース毎日changelog解説-01"
title: "Claude Code v2.1.140 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/71ae2b61978505b1560d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "qiita"]
date_published: "2026-05-13"
date_collected: "2026-05-13"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.140 はバグ修正中心のリリース。改善 3 件と修正 10 件が入っています。

## 今回の注目ポイント

1. **Agent ツールの `subagent_type` が大文字小文字・区切り文字を問わなくなった** - `"Code Reviewer"` でも `code-reviewer` に解決される
2. **`/goal` のサイレントハング修正** - hooks を全部止めた環境で進捗インジケーターが永久に回り続ける問題が解消
3. **Plugin の silent ignore に警告表示** - `commands/` 等のデフォルトフォルダが `plugin.json` 側の指定で無視されている時に `/doctor` で気づける
4. **`claude --bg` の "connection dropped mid-request" 解消** - バックグラウンドサービスが idle-exit する直前にだけ起きていた接続エラーを修正
5. **`/loop` の無駄な wakeup 削減** - 完了通知を持つタスクへの冗長なポーリングを停止
6. **Windows での event-loop stall 修正** - 存在しない `gh` 等の探索で `where.exe` が毎回同期再起動していた

---

## Agent ツールの subagent_type が緩やかになった

:::note info
対象読者: カスタムサブエージェントを `Agent` ツールから呼び出している人
:::

`"Code Reviewer"` のような大文字混じり・スペース区切りの表記でも、v2.1.140 からは `code-reviewer` に解決されるようになりました。

```json
{
  "subagent_type": "Code Reviewer"
}
```

LLM がカスタムエージェント名を表記揺れで指定して失敗するケースが、これで消えます。

---

## `/goal` のサイレントハングが直った

:::note info
対象読者: `disableAllHooks` か `allowManagedHooksOnly` を設定している人(エンタープライズ環境に多い)
:::

`/goal` は内部で hook を経由して状態を回しているため、hooks を全部止めると進捗インジケーターが永遠に回り続ける挙動でした。タイムアウトもエラーも出ないので、ユーザーは「動いているかも」と待ち続けるしかなかった。

v2.1.140 ではこの状況を検出し、`/goal` 起動時にメッセージを出して停止します。

`settings.json` 例:

```json
{
  "disableAllHooks": true
}
```

これまでは無言でハングしていたものが、`/goal` を叩いた瞬間に「hooks が無効化されているので使えない」と返すようになります。エンタープライズ環境で `disableAllHooks` を設定したユーザーが「壊れている」と誤認するパターンも回避できる。

---

## Plugin の silent ignore が `/doctor` で見えるようになった

:::note info
対象読者: 自作プラグインを書いている人
:::

プラグインは `commands/`, `agents/` 等のデフォルトフォルダを自動的に拾います。ただし `plugin.json` で `commands` キーを明示すると、フォルダ側は無視される(指定が優先される)。エラーも警告も出ない silent な挙動だったので、「`commands/` に置いたのに認識されない」というハマりが発生していました。

v2.1.140 からは以下の 3 箇所で警告が出ます。

- `/doctor`
- `claude plugin list`
- `/plugin`

`/doctor` の出力に「`commands/` が無視されている」旨が含まれるため、`plugin.json` の指定漏れに気づける。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.140 | 改善 | agent color palette 更新 | サブエージェント表示色を刷新 |

<details>
<summary>バグ修正一覧(v2.1.140)</summary>

- `claude --bg` が idle-exit 直前に "connection dropped mid-request" で失敗していた問題
- エンタープライズ endpoint security 環境でバックグラウンドサービス起動が失敗していた問題(起動猶予を延長)
- remote managed settings が 401 でリトライしない問題(force-refreshed token で 1 回だけリトライ)
- managed `extraKnownMarketplaces` の auto-update policy が `known_marketplaces.json` に永続化されない問題
- `/loop` が完了通知を持つバックグラウンドタスクに redundant な wakeup をスケジュールしていた問題
- Windows で `gh` 等の missing executable が `where.exe` の同期再起動を毎チェック誘発し、event-loop が stall する問題
- `Read` tool の `offset` が whitespace-padded / `+`-prefixed 文字列で validation 失敗する問題
- 設定ファイル hot-reload で symlinked settings が誤った変更検出と spurious `ConfigChange` hook を発生させていた regression
- native terminal cursor がフォーカス喪失時に入力 caret に留まらない問題

</details>

## まとめ

v2.1.140 は新機能ゼロ、修正のみのリリース。`/goal` のサイレントハングや Plugin の silent ignore など、「動いているか分からない」状態が表に出るようになったのが今回の主軸。エンタープライズ環境(`disableAllHooks` や endpoint security)向けの修正もまとまって入っています。
