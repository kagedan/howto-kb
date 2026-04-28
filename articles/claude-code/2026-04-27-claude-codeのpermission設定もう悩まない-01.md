---
id: "2026-04-27-claude-codeのpermission設定もう悩まない-01"
title: "claude codeのpermission設定もう悩まない"
url: "https://qiita.com/suisuisan/items/7d2c1346660aa7f0e3ee"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

タイムリーでした。
パーミッションのわずらわしさ、放置時間の無駄について対策をしていました。（今日）

【今日やったこと】
1. --dangerously-skip-permissions（なんでも通す）：これはやめとく。
2. allowlist充実：read系はもとよりパーミションされている。追加するものは特にないと判明。
3. 公式のfewer-permission-promptsスキルで過去のパーミションからリスト作成して追加。下記👇

| # | Pattern | 用途 | 追加理由 |
| --- | --- | --- | --- |
| 1 | `Bash(docker compose -f * logs:*)` | docker compose ログ閲覧 | スキャンで 28回観測、read-only |
| 2 | `Bash(mkdir:*)` | フォルダ作成 | 取り返し可で安全 |
| 3 | `Bash(cp:*)` | ファイルコピー | コピー元無傷で安全 |
| 4 | `Bash(npm pack:*)` | tarball 生成 | publish はしない、副作用なし |
| 5 | `Bash(npx prisma generate)` | Prisma 型生成 | DB に触れない、exact match |

しかし。

ここで「fewer-permission-prompts skill」でちょっとWEB検索。
こちらの記事が見つかりました。

https://note.com/0x__tom/n/n3e67c74ef254

auto mode
auto mode
auto mode
・
・
・

ん？auto mode？

結論。auto modeというものが登場していました。
Claudeの調査では以下。

| 時期 | イベント |
| --- | --- |
| **2026-03-24** | リサーチプレビュー開始 |
| **2026-03-24 ~ 04-16** | Team → Enterprise → Max plan へ段階的ロールアウト |
| **2026-04-16頃** | Max plan ユーザーへ展開完了 |
| **2026-04-27（今日）** | **約10日前に Max plan で利用可能になった** |

そうだったのか。

:::note info
10日ほど前からMAXプラン（現在MAX x5です）展開されてましたかね？気が付いてませんでしたが。日本では遅いとかあり？いや4/16頃からあったのかもしれませんね^-^)
:::

先ほどの記事ではauto modeで作業を平行で走らせることが可能になったことの意義が強調されてました。

## 早速、私の見解をclaudeに投げて確認

| 認識 | 評価 |
| --- | --- |
| auto mode にすると既存の allowlist は関係なくなる | ⚠️ **正確には「補完関係」** — 後述 |
| `--dangerously-skip-permissions` は危険 | ✅ 同意 |
| allowlist 整理は大変、`/fewer-permission-prompts` でも大変 | ✅ そのとおり |
| `/fewer-permission-prompts` の結果は「めくら判リスト」になりがち | ✅ **鋭い指摘**。実績ベースだが、未来のコマンドを判定できない |
| auto mode は Claude Code が**自律的にコマンドを判定**するモード | ✅ そのとおり。Stage 1（即判定）+ Stage 2（思考審査） |
| → permissions 数を減らしながら安全性も担保 | ✅ そういう設計思想 |

— 後述
> auto mode にすると既存のリストは関係なくなる
> 
> → 厳密には「allowlist が先に効いて、漏れたものを auto modeの自動判定が拾う**」という補完関係です。
> 
> つまり:
> 
> allowlist にマッチ → 即 OK（一番速い）
> auto Stage 1 → 「即・安全」判定 → 通す
> auto Stage 2 → 思考で審査 → OK/NG
> それでも危険なら従来通り prompt
> なので allowlist は無駄にはなりません。

とのことですが、作ったものは無駄にはならないかもですが、こだわりがなければallowlistは、まあなくてもいいよねという感じ。

## 結論。

パーミッション問題はいったん決着。
今後はauto mode一択で進めればよい感じでしょうかね。

![annotate_20260427_134607.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3805817/3e6f7f4e-6481-4bfe-ad6c-f87f9d3225db.png)

上記の文字図形入れは自前の無料ツールで加工しました^-^)
使い切り画像ならキャプチャした後はペースト、コピー、ペーストで済むので早いです。

https://microapps.one/tool-forest/image/annotate/
