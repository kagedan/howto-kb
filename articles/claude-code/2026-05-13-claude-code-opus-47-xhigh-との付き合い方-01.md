---
id: "2026-05-13-claude-code-opus-47-xhigh-との付き合い方-01"
title: "Claude Code | Opus 4.7 xhigh との付き合い方"
url: "https://zenn.dev/gudezou/articles/ce6ff755b2861f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "zenn"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

長いので先に結論:

* Claude Code を最新版に上げてから Opus の応答が妙に長く感じるなら、それは Opus 4.7で新設された `xhigh` という思考レベルが、しれっと既定値に引き上げられたのが要因かも。
* `xhigh` は `high` と `max` の中間に置かれた新しい層で、長時間のエージェント作業や繰り返しのツール呼び出しに向けて「深く考え続ける」ための設定です。
* ただし「深いほどよい」は公式自身が否定しており、`max` は overthinking で逆効果になり得ます。

本記事は `xhigh` / `high` / `max` の使い分け基準を整理します。

## 「いつもより長く考える」の正体

Claude Code v2.1.111以降は Opus 4.7に対応し、v2.1.117以降では既定 effort が `xhigh` に切り替わりました。

つまり Opus 4.7を選んだだけで、ユーザーに無断で思考の深さが「いつもより一段上」に引き上げられている状態です。

これは公式が意図した設計で、Opus 4.7を初めて起動したとき、Claude Code は過去に Opus 4.6や Sonnet 4.6で別の effort を設定していても、強制的に `xhigh` を当てます。  
`/effort` を改めて叩いて再選択する前提です。

既定値が引き上げられた背景には、Opus 4.7自体の性能改善があります。  
Anthropic はリリース時に、SWE-bench Verified の解決率が13%向上、CursorBench が58%から70%、XBOW 視覚認識が54.5%から98.5%へ伸びたと報告しています。  
深く考えるほど結果が良くなる前提条件が強化されたから、既定もそちらへ寄せた、と読み取れます。

![Opus 4.6→4.7のベンチマーク改善](https://static.zenn.studio/user-upload/aa89622a0202-20260514.png)

この先で次の3点について深堀ります。

* effort とは何か
* `xhigh` はどこから来たのか
* `high` と `xhigh` をどう使い分けるか

## effort の5段階

effort は Claude API と Claude Code の両方で使える「思考の深さ」を制御する設定です。

値を上げれば思考が深くなり、下げればトークン消費とレイテンシが減ります。  
Opus 4.7では段階が5つあります。

| Level | 用途 | トークン消費 |
| --- | --- | --- |
| `low` | 短い処理、速度優先 | 最小 |
| `medium` | 平均的なワークフロー、コスト寄り | 控えめ |
| `high` | 知性とコスト効率のスイートスポット、API 既定値 | 標準 |
| **`xhigh`** | **コーディングとエージェント作業の推奨スタート、Claude Code 既定値** | **`high` より明確に多い** |
| `max` | 真にフロンティアな問題のみ | 最大 |

![effort 5段階の位置関係](https://static.zenn.studio/user-upload/11ca34258aa7-20260514.png)

Opus 4.6と Sonnet 4.6は `xhigh` を持ちません。  
`low / medium / high / max` の4段階のみです。

`/effort xhigh` を指定した状態でモデルを Opus 4.6に切り替えると、`xhigh` は警告なしで `high` に落ちます。  
Claude Code の仕様で、サポートしないレベルが指定されたときは「それ以下で最も高いレベル」へ自動でフォールバックするためです。

公式のガイドは、Opus 4.7では `xhigh` を「コーディングとエージェント作業のスタート地点」、`high` を「知性が必要なほとんどのワークロードの最低ライン」と位置づけています。

## extended thinking 廃止と adaptive thinking 一本化

Opus 4.7では effort の話と並んで、もう一つ大きな仕様変更が静かに入っています。

**手動の extended thinking が廃止されました。**

旧来の Opus 4.6と Sonnet 4.6では、`thinking: {type: "enabled", budget_tokens: N}` で「N トークン分まで考えていい」と直接指定できました。  
Opus 4.7ではこの API が受け付けられなくなり、`adaptive thinking` のみになっています。

`adaptive thinking` は、モデル自身が「この問題は深く考えるべきか、すぐ返事すべきか」をプロンプトごとに判断するモードです。  
`high` 以上では「ほぼ常に深く考える」、`low` と `medium` では「簡単な問題は思考をスキップ」という挙動になります。

つまり Opus 4.7では、**思考の深さは effort でだけ制御する設計に統一**されました。

Claude Code 側でも `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` は Opus 4.7に効きません。`MAX_THINKING_TOKENS` は thinking 完全停止 (`=0`) は引き続き有効ですが、正の値での予算指定は Opus 4.7では無視されます (旧来の固定 thinking budget モードに紐づく設定のため)。  
Opus 4.6と Sonnet 4.6では従来通り使えます。

この変更が意味するのは「ユーザーが直接 budget を制御する時代から、effort で間接制御する時代に移った」ということです。  
段数が決め打ちになり、自由に微調整できるダイヤルではなくスイッチに近くなりました。

![Opus 4.7で変わった思考制御 API](https://static.zenn.studio/user-upload/4701d0c06c81-20260514.png)

## 使い分けの判断表

実用上いちばん気になるのは「自分のセッションで何を選ぶか」で、Anthropic 公式の推奨を要約すると次の通りです。

| 状況 | 推奨 effort |
| --- | --- |
| 短い質問、分類、ログ参照 | `low` |
| 平均的なコーディング、コストを抑えたい | `medium` |
| 知性は欲しいがトークンも抑えたい | `high` |
| **コーディング全般、エージェント作業、繰り返しのツール呼び出し** | **`xhigh` (Claude Code の既定)** |
| 評価で `xhigh` に余白が残ると確認できた挑戦的な問題 | `max` |

公式は `max` を「効果が頭打ちになる領域」と明言しています。  
`max` で増えるトークン消費に対して品質改善が見合わないことが多く、構造化出力や知性依存度の低いタスクでは overthinking で逆効果にすらなり得ます。

もうひとつ覚えておくと得なのが、Opus 4.7は `low` と `medium` で「頼まれたこと以上のことをしない」という挙動です。  
Opus 4.6は気を利かせて scope を広げる傾向がありましたが、4.7は素直になりました。

その結果、低 effort で複雑な問題に対応すると、4.6時代よりも浅い応答が返ってきやすくなっています。  
公式の対処方針は明快で、

> If you observe shallow reasoning on complex problems with Claude Opus 4.7, raise effort rather than prompting around it.

つまり「プロンプト工夫で深く考えさせる」ではなく「`/effort` を一段上げる」が公式推奨です。

## 実運用での5つの注意点

### モデル切り替えで `xhigh` が黙って消える

`/effort xhigh` の状態でモデルを Opus 4.6に切り替えると、`xhigh` は警告なしで `high` に落ちます。  
ステータスラインの effort 表示で現在値を確認するのが安全です。

### `max` はセッション限定 (env var を除く)

`/effort max` で持ち上げても、セッションを閉じれば次回は元の effort に戻ります。  
永続化したい場合だけ env var に `CLAUDE_CODE_EFFORT_LEVEL=max` を立てます。  
`max` を全プロジェクトで常用する必然性はほぼないので、特定セッションでの一時投入が前提です。

### `xhigh` と `max` では `max_tokens` を大きく取る

公式は `xhigh` や `max` で動かすときの `max_tokens` を64,000トークンから始めて調整するよう推奨しています。  
サブエージェントやツール呼び出しが連鎖する余地を残すためです。

### プロンプトの互換性は崩れている

Opus 4.6用にチューニングしたプロンプトを Opus 4.7と `xhigh` の組み合わせで動かすと、過剰応答や応答不足が起きる可能性があります。  
プロンプトを「4.6向け」から動かしていないなら、`xhigh` での挙動を一度評価し直す価値があります。

### Opus 使用量が閾値超過で Sonnet にフォールバックする

Opus 4.7を使い続けても、プラン上限に当たると自動的に Sonnet にフォールバックします。  
`xhigh` 前提で組んだプロンプトが Sonnet 4.6の `high` で走るとどうなるか、頭の隅に置いておく必要があります。

## effort 選択の指針

公式の推奨と挙動を踏まえると、Claude Code ユーザーが取るべき戦略は次の通り。

* **既定値 (`xhigh`) でとりあえず動かす**: コーディングとエージェント作業はこれで十分
* **コスト重視のサイドタスクは `/effort medium`**: ドキュメント生成、軽い refactor、定型作業など
* **詰まったら `/effort` を一段上げる**: プロンプト工夫の前に effort を上げる
* **本当に難しい一発勝負だけ `ultrathink`**: セッション全体の effort は変えずに「このターンだけ深く考えて」と指示できる

`ultrathink` というキーワードは、プロンプトのどこにでも書けるワンショットフラグです。  
`/effort max` のセッション波及を避けたいときに使えます。  
プロンプト文字列に含まれているとモデル側がそのターンだけ思考を深めます。

まとめると、

* 深く考えるほどよい結果が出るとは限らない
* コストとレイテンシが線形に増える
* `max` では overthinking が起きるかもしれない

です。

**自分のセッションで何を最適化したいのか**を先に決めてから effort を選ぶのが、Opus 4.7時代の付き合い方になりそうです。

## 参考
