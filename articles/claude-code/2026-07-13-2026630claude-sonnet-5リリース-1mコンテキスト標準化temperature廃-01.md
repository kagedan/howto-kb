---
id: "2026-07-13-2026630claude-sonnet-5リリース-1mコンテキスト標準化temperature廃-01"
title: "【2026/6/30】Claude Sonnet 5リリース — 1Mコンテキスト標準化・temperature廃止・実質3割の値上げも"
url: "https://qiita.com/sakutto-panda/items/47a2b51bf6c4f513ec49"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "Python", "qiita"]
date_published: "2026-07-13"
date_collected: "2026-07-14"
summary_by: "auto-rss"
query: ""
---

## 3行まとめ

- 2026年6月30日、Anthropic が **Claude Sonnet 5** をリリース。1Mトークンコンテキストが標準（それ以外の選択肢なし）、出力上限128k、**Claude Code のデフォルトモデル**にも即日昇格した
- 8月31日までプロモ価格 **$2 / $10 per MTok**（以降は Sonnet 4.6 と同じ $3 / $15）。ただし**新トークナイザが同じテキストで約30%多くトークンを消費する**ため、単価据え置きでも実質値上げになる
- API では破壊的変更が3つ。**`temperature` / `top_p` / `top_k` の指定が 400 エラー**、manual extended thinking（`budget_tokens`）も 400 エラー、adaptive thinking がデフォルト有効

---

2026年6月30日（米国時間）、Anthropic が Claude Sonnet 5 を公開した。モデル ID は `claude-sonnet-5`。「速度と知性の最良の組み合わせ」という位置づけは歴代 Sonnet と同じだが、中身は**仕様レベルでの変更がかなり多い**リリースになっている。

https://www.anthropic.com/news/claude-sonnet-5

単なる性能アップデートとして流すと、API 利用者は 400 エラーを踏み、コスト管理をしている人はトークン消費の増加に後から気づくことになる。公式発表と開発者向けドキュメントを突き合わせて、変更点を全部整理しておく。

## 基本仕様 — 1Mコンテキストが「標準」になった

開発者向けドキュメント（What's new in Claude Sonnet 5）に記載の仕様はこう。

https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5

- **コンテキストウィンドウ: 1Mトークン**。デフォルトかつ最大。**小さいコンテキストのバリアントは存在しない**
- **最大出力トークン: 128k**
- **adaptive thinking がデフォルトで有効**
- ツール・プラットフォーム機能は Sonnet 4.6 と同一。ただし **Priority Tier は非対応**
- assistant メッセージの prefill は引き続き非対応（Sonnet 4.6 から変わらず）

これまで 1M コンテキストは「ベータ」や「追加料金つきの拡張」という扱いが多かったが、Sonnet 5 では**長コンテキストの料金プレミアムなしで、全リクエストが 1M ウィンドウ**になる。大きなコードベースを丸ごと読ませる用途や、長時間のエージェントセッションには素直に効く変更だ。

提供面では、Claude API に加えて Amazon Bedrock・Google Cloud・Microsoft Foundry で同日利用可能。claude.ai では **Free / Pro プランのデフォルトモデル**になり、Max / Team / Enterprise でも選択できる。

## Claude Code は v2.1.197 からデフォルトモデルに

Claude Code ユーザーに直接影響するのがここ。公式 changelog の v2.1.197（June 30, 2026）にこうある。

> Introducing Claude Sonnet 5: now the default model in Claude Code, with a native 1M-token context window and promotional pricing of $2/$10 per Mtok through August 31. Update to version 2.1.197 for access.

https://code.claude.com/docs/en/changelog

つまり **v2.1.197 以降にアップデートすると、明示的にモデルを固定していない限りデフォルトが Sonnet 5 に切り替わる**。5月末に Opus 4.8 が Max / Team Premium などのデフォルトになったばかりなので、プランによってデフォルトモデルが違う状態がしばらく続くことになる。

「最近 Claude Code の挙動が変わった気がする」というときは、まず `/model` で今どのモデルで動いているかを確認したい。挙動を固定したい場合は settings やセッション内の `/model` で明示指定しておくのが安全。

## 破壊的変更3つ — Sonnet 4.6 からの移行で踏むポイント

ドキュメントでは「drop-in upgrade」と書かれているが、**3つの動作変更**が明記されている。API 経由で Sonnet 4.6 を使っているコードは、モデル ID を差し替える前にここを確認したほうがいい。

### ① `temperature` / `top_p` / `top_k` が指定できなくなった

サンプリングパラメータに**デフォルト以外の値を設定すると 400 エラー**が返る。移行時はパラメータ自体を削除する必要がある。

この制約は Opus 4.7 で先に導入されていたもので、今回**初めて Sonnet クラスに降りてきた**。影響範囲が広いのは、創造性を上げるために `temperature` を上げていた層よりも、むしろ**再現性のために `temperature: 0` を指定していた層**だと思われる。0 も「デフォルト以外の値」なのでエラーになる。Anthropic の案内は「システムプロンプトの指示で挙動を誘導する」への移行で、決定論的な出力を得るノブは事実上なくなった。

### ② manual extended thinking（`budget_tokens`）が 400 エラーに

Sonnet 4.6 で deprecated だった手動の思考トークン割り当てが、Sonnet 5 では**削除**された。

```python
# Sonnet 5 では 400 エラー
thinking = {"type": "enabled", "budget_tokens": 32000}

# こちらに移行する
thinking = {"type": "adaptive"}
```

思考量のコントロールは `budget_tokens` の数値指定ではなく、adaptive thinking + effort パラメータに一本化された。Opus 4.7 / 4.8 と同じ体系になる。

### ③ adaptive thinking がデフォルト有効

Sonnet 4.6 では `thinking` フィールドを付けなければ思考なしで動いた。Sonnet 5 では**同じリクエストが adaptive thinking ありで動く**。思考を切りたい場合は `thinking: {type: "disabled"}` を明示する。

地味に効くのが `max_tokens` の扱いで、**`max_tokens` は思考トークン+応答テキストの合計に対する上限**になる。思考なし前提でギリギリの `max_tokens` を設定していたワークロードは、思考分を食われて応答が途中で切れる可能性がある。

## 新トークナイザ — 単価据え置きで実質値上げ

今回いちばん見落とされそうで、コスト面では最重要の変更がこれ。

**Sonnet 5 は新しいトークナイザを使っており、同じテキストが Sonnet 4.6 比で約30%多くトークンに分割される**（増加率はコンテンツ依存）。API の形は何も変わらないので、コードの修正は不要。だが「トークンで測っているもの」全部に影響が出る。

- **`usage` の値やトークンカウント結果**が同じテキストでも増える。Sonnet 4.6 時代に測った値の使い回しは不可
- **1M ウィンドウに入るテキスト量**は額面より少ない。1トークンがカバーする文字数が減るため
- **`max_tokens` の予算**も同様。4.6 向けにチューニングした上限だと同等の出力が切り詰められる
- **リクエスト単価**。トークン単価は据え置きでも、同じ内容のリクエストのコストは上がる

Simon Willison はこの点を「実質30%の値上げ」と評している。

https://simonwillison.net/2026/Jun/30/claude-sonnet-5/

プロモ価格（$2 / $10、8月31日まで）の間は 4.6 の標準価格（$3 / $15）より十分安いので気にならないが、**9月1日に標準価格へ戻った瞬間、名目同価格・実質3割増**という構図になる。9月以降も Sonnet 5 を使い続けるかどうかは、プロモ期間中に自分のワークロードで実測しておくのがよさそうだ。

## サイバーセキュリティ・セーフガードが Sonnet 層に初導入

Sonnet 5 は **Sonnet ティアで初めてリアルタイムのサイバーセキュリティ・セーフガードを積んだモデル**でもある。禁止・高リスクなサイバー関連のリクエストは拒否されることがあり、その場合 **HTTP 200 の正常レスポンスで `stop_reason: "refusal"`** が返る。エラーハンドリングだけ見ていると気づかないので、セキュリティ系の解析ツールなどを作っている場合は `stop_reason` の分岐を入れておきたい。

この設計は Fable 5 のセーフガード（分類器 + フォールバック）の流れを汲むもので、「上位モデルで作った安全機構を下位ティアに展開する」方向性が見て取れる。Fable 5 を巡る6月の騒動はこの記事で整理している。

https://qiita.com/sakutto-panda/items/f0e9087256dc94b363eb

## 性能の位置づけ

公式の触れ込みは「最もエージェント的な Sonnet」。ブラウザやターミナルといったツールを使い、計画を立てて自律的に動くタスクで、**少し前なら上位モデルが必要だった水準に Sonnet 価格で届く**というのが売りになっている。ドキュメント上も「最大の伸びはコーディングとエージェントタスク」と明記されており、TechCrunch は「エージェントを安く回すための選択肢」という切り口で報じた。

https://techcrunch.com/2026/06/30/anthropic-launches-claude-sonnet-5-as-a-cheaper-way-to-run-agents/

ミドルティアのモデルがフラッグシップの性能に迫る、という構図は業界全体のトレンドでもある。フロンティアモデル（Fable 5 など）のアクセスが絞られる方向に動いているのと対照的に、**日常のワークロードはミドルティアで十分**という状況が加速している。

## 個人開発者目線 — 移行チェックリスト

API で Sonnet 4.6 を使っている場合、モデル ID を差し替える前に確認する項目を挙げておく。

1. **`temperature` / `top_p` / `top_k` をリクエストから削除**する（`temperature: 0` も対象）
2. **`budget_tokens` を使っていたら `thinking: {type: "adaptive"}` へ**移行する
3. **`max_tokens` を見直す**。adaptive thinking の思考分が上限に含まれる + トークナイザで出力トークン数自体も増える
4. **トークンカウントを取り直す**。プロンプトのトークン数・コスト試算は Sonnet 5 で再計測する
5. **`stop_reason: "refusal"` の分岐**を入れる（サイバー系の内容を扱う場合）
6. **Priority Tier 前提の構成なら据え置き**。Sonnet 5 は非対応

Claude Code 側は、アップデートするだけでデフォルトが切り替わる。1M コンテキストで長いセッションが安定するメリットは大きい一方、モデル挙動の変化に気づかず「なんか違う」となりがちなタイミングなので、`/model` での確認だけ覚えておきたい。

## まとめ — 今後ウォッチすべきポイント

Sonnet 5 を一言でまとめると、**「1Mコンテキストとエージェント性能を Sonnet 価格に降ろす代わりに、API の自由度（サンプリングパラメータ・手動thinking）を回収したリリース」**。

- 1M コンテキストが標準・最大。128k 出力。Priority Tier 非対応
- Claude Code は v2.1.197 からデフォルトモデル化
- 破壊的変更3点: サンプリングパラメータ 400 エラー / manual thinking 400 エラー / adaptive thinking デフォルト有効
- 新トークナイザで同じテキストが約30%増。**9月1日の標準価格復帰後は実質値上げ**

ウォッチポイントは3つ。

1. **8月31日のプロモ終了**。9月以降のコストを自分のワークロードで実測してから判断する
2. **トークナイザ増加率の実測値**。「約30%」はコンテンツ依存なので、日本語テキストでどうなるかはユーザー側の検証待ち
3. **サンプリングパラメータ廃止の波及**。Opus → Sonnet と来た以上、次期 Haiku にも降りてくる可能性が高い。`temperature` 依存のコードは今のうちに整理しておく

:::note
**ぱんだツールズ** では PDF・画像・CSV・テキスト処理などの開発者向けツールを 90 個以上公開中。全部無料・登録不要・ブラウザ完結で使える。Claude Code で開発した個人開発プロダクトの実例として、よかったら覗いていって。
https://sakutto-panda.com
:::

---

> この記事は [Zenn](https://zenn.dev/sktt_panda/articles/claude-sonnet-5-release-2026-07) にも同じ内容を投稿しています。
