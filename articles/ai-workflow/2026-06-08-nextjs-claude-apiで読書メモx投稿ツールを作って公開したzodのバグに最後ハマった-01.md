---
id: "2026-06-08-nextjs-claude-apiで読書メモx投稿ツールを作って公開したzodのバグに最後ハマった-01"
title: "Next.js × Claude APIで「読書メモ→X投稿」ツールを作って公開した（zodのバグに最後ハマった）"
url: "https://zenn.dev/nora_saito/articles/46e2d3fdefdf54"
source: "zenn"
category: "ai-workflow"
tags: ["API", "TypeScript", "zenn"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

## 何を作ったか

読書メモを貼ると、AIがX(Twitter)投稿を3案つくってくれるツールを作って公開した。実際に公開したものがこれ。

<https://ai-playground-reading-to-sns.vercel.app/>

きっかけは完全に自分の悩みで、「本は読むのに、それを発信に活かせてない」をどうにかしたかった。読んだメモを貼るだけで、切り口の違う投稿が3つ出てくるなら自分が一番欲しい、と思って作った。

使ったものはこのへん。

* Next.js 15 (App Router) + React 19 + TypeScript
* Tailwind CSS v4
* Claude API（`@anthropic-ai/sdk`、モデルは Haiku 4.5）
* Zod（構造化出力 + バリデーション）
* pnpm + Turborepo のモノレポ / ホスティングは Vercel

で、作ること自体よりも「公開してから詰まったところ」のほうが学びが多かったので、そこを正直に書く。同じ穴に落ちる人が減れば嬉しい。

---

## まず設計：出力はZodでガチガチに固定した

「3案を、それぞれ違う切り口で、Xに貼れる形で」返してほしかった。ここでAIの自由テキストを正規表現でパースするとか、絶対に事故る。なので最初から**Zodスキーマで出力の形を固定**する構造化出力でいった。

```
// lib/schema.ts
export const PostSchema = z.object({
  text: z.string().describe("X投稿の本文。140字以内が望ましい"),
  hook_type: z.string().describe("切り口を一言で（結論先出し/問いかけ/逆説 など）"),
  hashtags: z.array(z.string()).max(5).describe("関連性の高いタグ。#は付けない"),
});

export const PostsResponseSchema = z.object({
  posts: z.array(PostSchema).length(3),
});
```

`.describe()` をちゃんと書くと、AIがそれを読んで出力を整えてくれる。ここは手を抜かない方がいい。

---

## 詰まり①：ビルド通ってるのに、本番で `reading 'def'` で落ちた

これが一番ヒヤッとした。

ローカルで `typecheck` も `build` も通る。Vercelへのデプロイも成功。「完成じゃん」と思って本番で生成ボタンを押したら——

```
Cannot read properties of undefined (reading 'def')
```

**ビルドは緑なのに、実際に動かすと落ちる**やつ。一番タチが悪い。

### 原因

スタックトレースを追ったら、犯人は `zod` のバージョンだった。

* 入ってた zod は **3.25系**
* `@anthropic-ai/sdk` の `zodOutputFormat` は、内部で **zod v4 の `toJSONSchema`** を呼ぶ
* でも自分のコードは旧来の `import { z } from "zod"`（= **v3** スキーマ）
* v4向けの変換が v3 スキーマの内部（`def`）を読もうとして `undefined` → クラッシュ

zod 3.25 は v3 と v4 が同梱されてて、`import { z } from "zod"` は後方互換で **v3**、`import { z } from "zod/v4"` が **v4**、という分かれ方をしてた。SDKはv4を要求してたのに、自分はv3を渡してた、というすれ違い。

### 直し方

importをv4に変えるだけ。

```
- import { z } from "zod";
+ import { z } from "zod/v4";
```

ただこれだと今度は**型エラー**が出る。SDK 0.93 の `zodOutputFormat` は「実体はv4を要求するのに、型定義はv3を指してる」っていう不整合があるせい。なので呼び出し側で型を逃がした。

```
output_config: {
  // SDK 0.93 の型は zod v3 を指すが、実体は v4 を要求するため回避
  format: zodOutputFormat(PostsResponseSchema as never),
},
```

### 学び

* **`typecheck` も `build` も通る ＝ 動く、ではない。** 型と実行時は別物。痛感した。
* ライブラリのメジャー境界（今回はzod v3/v4同梱期）は、「型は合ってるのに実体が違う」事故が起きやすい。
* **公開したら、絶対に本番で一回手で叩く。** 自動チェックは万能じゃない。

ちなみに同じ書き方をしてた別アプリにも同じ地雷が埋まってたので、ついでに直した。1個見つけたら横展開で探すの大事。

---

## 詰まり②：モデル選定でコストが5倍変わる

最初はテンプレのまま上位モデル（Opus）を使ってたけど、このタスクは「読書メモ→短い投稿3案」っていう軽い処理。Opusは完全にオーバースペックだった。

公開＝知らない人に無料で使われる前提なので、**1回あたりのコストはちゃんと効いてくる。**

| モデル | 1回あたり目安 |
| --- | --- |
| Opus | 約 ¥3〜4 |
| Haiku 4.5 | **約 ¥0.5〜1** |

品質が十分な範囲で **Haiku 4.5 に変えてコスト約1/5**。「とりあえず一番賢いやつ」じゃなくて、タスクに合わせて選ぶ、を体で覚えた。

---

## 詰まり③：「クレジット残高不足」、でも買ったんだけど…？

公開後、`Your credit balance is too low to access the Anthropic API` が出た。買ったのに、である。

原因は、**Claude（アプリ版）の利用クレジットと、API（開発者プラットフォーム）のクレジットが完全に別**だったこと。`sk-ant-api03-...` のAPIキーが引くのは後者。前者にいくら入れても届かない。どっちも名前が「利用クレジット」で、これは普通に紛らわしいと思う。

→ **console.anthropic.com 側でAPIクレジットを買って解決**。APIを使うなら入金先はこっち、と覚えておけば迷わない。

---

## 公開する前に入れた「守り」

宣伝して人を呼ぶ前に、最低限の防御だけ入れた。

* **無料の上限**：クッキーで「1ブラウザ1日5回まで」。コスト垂れ流し防止 ＋ 将来「もっと使うなら登録」への導線にもなる。
* **Anthropic側のSpend limit**：万一の天井。どれだけ使われても上限額で必ず止まる。
* **Vercel Analytics**：訪問数・流入元・生成回数を計測。改善の判断材料に。

クッキー消して無限に使う、までは防げない（それやるならDBが要る）。けど**最悪はSpend limitで止まる**ので、規模に対して過剰にせず、今回はここで十分とした。

---

## まとめ

1日で「作る→公開→課金→守り」まで通すと、教科書に載らない地味な詰まりが一通り出てきて、むしろそれが一番勉強になった。

* **構造化出力はZodで形を固定**すると事故が減る（`.describe()`を効かせる）
* **ビルドが通る ≠ 動く**。zod v3/v4みたいな境界は要注意。公開後に必ず手で確認
* **モデルはタスクに合わせて選ぶ**（コストは現実の制約）
* **APIとアプリの課金は別の財布**
* 宣伝の前に**利用上限**と**Spend limit**で守りを固める

動くものはこれ。「発信のネタ出しが面倒」な人に刺さると嬉しい。

<https://ai-playground-reading-to-sns.vercel.app/>
