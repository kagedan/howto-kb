---
id: "2026-06-20-claude-code-v21181v21183auto-modeが破壊的コマンドを止める毎日cha-01"
title: "Claude Code v2.1.181〜v2.1.183｜auto modeが破壊的コマンドを止める｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/74e97e0f8be8174d312e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-06-20"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

auto mode が、頼んでいない破棄系コマンドを実行前に止めるようになりました。v2.1.183 で `git reset --hard` や `git clean -fd` の暴発がブロックされます。設定を変えなくても効くので、auto mode を回している人ほど挙動が変わります。

## 今回の注目ポイント

1. **破棄系コマンドの自動ブロック** — `git reset --hard` や `terraform destroy` を、明示的に頼んでいなければ auto mode が止める (v2.1.183)
2. **`/config key=value` 構文** — プロンプトから `/config thinking=false` のように任意の設定を変えられる (v2.1.181)
3. **非推奨モデルの警告** — 要求したモデルが廃止・自動更新されたら stderr へ警告。エージェント frontmatter のモデル指定も対象 (v2.1.183)
4. **`CLAUDE_CLIENT_PRESENCE_FILE`** — マシンの前にいる間はモバイルのプッシュ通知を抑制する (v2.1.181)
5. **prompt caching の取りこぼし修正** — カスタム `ANTHROPIC_BASE_URL` と Foundry でキャッシュが読まれていなかった (v2.1.181)
6. **`/config` のトグル挙動変更** — Esc が破棄ではなく保存して閉じるように。Enter / Space どちらでも設定が変わる (v2.1.183)

## auto mode が破棄系コマンドを止める

:::note info
対象読者: auto mode で Claude Code に手を離して作業させている人。
:::

v2.1.183 で、auto mode が破棄系コマンドを実行する条件が厳しくなりました。ブロック対象はこうなっています。

- 破棄系 git: `git reset --hard` / `git checkout -- .` / `git clean -fd` / `git stash drop` は、ローカルの変更を捨ててと頼んでいない限りブロック
- `git commit --amend`: そのセッションでエージェント自身が作ったコミットでなければ拒否
- インフラ破棄: `terraform destroy` / `pulumi destroy` / `cdk destroy` は、対象スタックを指定して頼んだときだけ通す

どれも「うっかり全消し」の典型パターン。auto mode は許可を求めずに進むぶん、この手のコマンドが一度走ると戻せません。実行前に弾くぶん、取り返しのつかない操作の事故が減ります。

:::note alert
自動化スクリプトで auto mode に `git reset --hard` を打たせていた場合、v2.1.183 以降はブロックされます。「ローカルの変更を破棄して」と意図を明示して渡す運用に切り替えてください。
:::

## /config がプロンプトから直接叩ける

```
/config thinking=false
/config --help
```

v2.1.181 で `/config key=value` 構文が入りました。interactive / `-p` / Remote Control のどこでも効きます。設定画面を開かずに、その場で 1 つだけ値を変えられる。

v2.1.183 で補助も追加。`/config --help` が `key=value` に使える shorthand キーの一覧を出します。トグル操作の挙動も変わって、Esc が「破棄して戻る」から「保存して閉じる」に。Enter と Space はどちらも選択中の設定を切り替えます。

## カスタム BASE_URL で prompt caching が効いていなかった

`ANTHROPIC_BASE_URL` を独自に差し替えている環境と Foundry で、prompt caching が読み込まれていませんでした。原因は、リクエストごとに毎ターン変わる attestation トークン。v2.1.181 で修正済みです。

:::note warn
社内プロキシなどで `ANTHROPIC_BASE_URL` を差し替えている場合、v2.1.181 より前はキャッシュが毎ターン素通りで、入力トークンを余計に消費していました。心当たりがあれば更新してください。
:::

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.183 | 新機能 | `attribution.sessionUrl` | commit / PR から claude.ai のセッションリンクを省略できる |
| v2.1.183 | 修正 | WebSearch | サブエージェント内で空の結果を返していたのを修正 |
| v2.1.183 | 修正 | `thinking.disabled.display` | サブエージェント生成時の 400 エラーを修正 |
| v2.1.183 | 変更 | 起動ログ | ロゴ下の "setup issues" 行を削除。`/doctor` で確認する形に |
| v2.1.181 | 改善 | Bun ランタイム | バンドルする Bun を 1.4 に更新 |
| v2.1.181 | 改善 | ストリーミング | 長い段落が改行待ちせず行単位で表示される |
| v2.1.181 | 修正 | Write / Edit | ネットワークドライブで 0 バイト・切り詰めファイルが生成される問題を修正 |
| v2.1.181 | 修正 | macOS error -600 | `open` / `osascript` / ブラウザ認証の失敗を Apple Events entitlement 追加で解消 |
| v2.1.181 | 修正 | 起動 | 約 120ms の起動 regression (v2.1.169 で混入) を修正 |

## まとめ

今回の核は auto mode の破棄系ブロック。頼んでいない破壊的操作が走らなくなったぶん、auto mode をもう一歩任せやすくなりました。設定変更をプロンプトから直接打てる範囲も、`/config key=value` を含めてこの2バージョンで広がっています。
