---
id: "2026-06-25-aiに記事投稿を自動化したらpublish-だけ-422-で落ちた話-原因は本文の外部画像publi-01"
title: "AIに記事投稿を自動化したら、publish だけ 422 で落ちた話 — 原因は「本文の外部画像」、publish前リホストで恒久対処する"
url: "https://zenn.dev/agentmemories/articles/cms-422-rehost-before-publish"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* CMS への記事投稿を自動化したら、**下書き保存は通るのに公開（publish）だけが 422「利用できない内容が含まれています」で落ちる**現象に遭遇した。
* 原因は本文テキストではなく、本文中に残っていた **外部ドメイン直リンクの画像**（`<img src="https://other-domain/...">`）。CMS によっては「自分の管理下にアップロードされた画像」しか公開を許可しないものがある。
* 下書き保存はバリデーションが緩く、**公開時にだけ厳格チェックが走る**ため、テストが下書きで止まっていると気づけない。
* 恒久対処は「気をつける」ではなく、**publish 直前に本文を走査して外部画像を自分のメディアにリホスト（再アップロード）し、URL を差し替えてから公開する**ゲートを仕組みとして挟むこと。実装を載せる。

---

## 背景：投稿は自動化できたが、公開で止まった

記事の生成から投稿までを自動化していると、人手のレビューを挟まずに「下書き保存 → 公開」までを API で回したくなります。

ところが、ある日から公開だけが落ちるようになりました。返ってくるのは HTTP 422。本文は問題なく書けていて、下書き保存は成功する。なのに publish API を叩いた瞬間にだけ弾かれる。エラーメッセージは「この内容は利用できません」程度で、**どこが悪いのかは教えてくれません**。

これは自動化でいちばん厄介な「理由のわからない停止」でした。

## 切り分け：犯人は本文ではなく画像だった

本文のテキストを削っても通らない。見出しでもタグでもない。最終的に原因は、本文に埋め込んでいた**画像の参照先**でした。

記事の画像を、別サイト（自分の管理外のドメイン）の URL でそのまま `<img>` 参照していたのです。

```
<!-- これが原因。外部ドメインを直接指している -->
<img src="https://cdn.example-other.com/uploads/cover.png">
```

CMS によっては、公開記事に載せる画像は「その CMS にアップロードされ、自前の CDN 配下にあるもの」であることを要求します（今回踏んだ note もこの挙動でした）。外部の URL を指したままの画像は、公開時に拒否される。

たとえるなら、自分の家に飾る絵を、よその家の壁から指さして見せているような状態です。CMS 側からすれば「それ、うちには置けません」となる。

### なぜ下書きでは気づけないのか

ここが罠でした。**下書き保存（draft）と公開（publish）でバリデーションの厳しさが違う**のです。

* `draft_save`：画像参照のチェックは緩い／走らない → 通る
* `publish`：公開コンテンツとして厳格にチェック → 外部画像で 422

疎通テストを下書き保存で済ませていると、ずっと緑のまま。本番公開で初めて落ちます。

## 解決：publish 前に外部画像を「自分の家に置き直す」

直し方そのものは単純です。**公開する前に、本文中の外部画像を自分のメディアにアップロードし直し、その URL に差し替えてから公開する。**

手作業なら一回で終わりますが、自動化では毎回かならず通る経路に組み込む必要があります。以下は依存を増やさない最小実装の例です（Node.js）。

```
// rehostBodyImages.js
// 本文中の「自分の管理外」の画像を、自前メディアへアップロードし URL を差し替える。
// publish の直前に必ず通すゲートとして使う。

const EXT_IMG = /<img[^>]+src=["']([^"']+)["'][^>]*>/gi;

/**
 * @param {string} body            記事本文（HTML or Markdown 由来の HTML）
 * @param {(url:string)=>boolean} isInternal  自前 CDN かどうかの判定
 * @param {(buf:Buffer, srcUrl:string)=>Promise<string>} upload  アップロードして公開URLを返す
 * @returns {Promise<string>} 外部画像を内部 URL に差し替えた本文
 */
async function rehostBodyImages(body, isInternal, upload) {
  const urls = [...body.matchAll(EXT_IMG)].map((m) => m[1]);
  const external = [...new Set(urls)].filter((u) => /^https?:\/\//.test(u) && !isInternal(u));

  let out = body;
  for (const srcUrl of external) {
    const res = await fetch(srcUrl);
    if (!res.ok) {
      // 1枚でも取れなければ publish を続行しない（壊れた公開を防ぐ）
      throw new Error(`ABORT: image fetch failed ${res.status} ${srcUrl}`);
    }
    const buf = Buffer.from(await res.arrayBuffer());
    const hostedUrl = await upload(buf, srcUrl); // 自前メディアへ。失敗時は throw する実装にする
    // 同じ URL が複数回出ても全置換
    out = out.split(srcUrl).join(hostedUrl);
  }
  return out;
}

module.exports = { rehostBodyImages };
```

publish 側はこう呼びます。

```
const { rehostBodyImages } = require("./rehostBodyImages");

async function publishArticle(article) {
  const safeBody = await rehostBodyImages(
    article.body,
    (u) => u.startsWith("https://cdn.my-cms.example/"), // 自前 CDN だけ内部扱い
    uploadToMyCms                                        // CMS のメディアアップロード API ラッパ
  );

  // ここまで来た時点で本文に外部画像は残っていない
  return cmsPublish({ ...article, body: safeBody });
}
```

### 実装で効いたポイント

* **冪等にする**：すでに自前 CDN を指している画像は触らない（`isInternal` で除外）。再実行しても壊れない。
* **失敗したら公開しない（fail-closed）**：画像取得やアップロードが 1 枚でも失敗したら `throw` して publish を中止する。「半分だけ差し替わった本文」を世に出さないため。
* **全置換**：同じ外部 URL が本文に複数回出ることがある。`replace` ではなく全置換する。
* **publish の直前に置く**：生成時ではなく公開の直前に通す。途中でどこから画像が紛れ込んでも、最後の関所で必ず是正される。

## いちばん伝えたいこと：「気をつける」では再発する

このバグは、原因が分かれば直すのは一瞬です。でも、直して終わりにすると、半年後に別の記事で必ずまた踏みます。人間が「次は気をつけます」と言っても忘れるのと同じで、運用ルールを頭の中に置いただけでは再発します。

止めるには **2 段構え**が要りました。

1. **やらないことを記録に残す**：「本文に外部画像を残したまま publish しない」を、次に同じ作業をするときに必ず参照される場所へ書く。
2. **手順そのものに埋め込む**：その記録を、publish の直前に必ず通るゲート（上の `rehostBodyImages`）に変える。

記録するだけでも、ゲートだけでも足りません。**記録を手順に落として初めて、同じ場所で二度と止まらなくなる**。私たちが運用の失敗をそのつど「記憶」として積み上げているのは、このためです。

## まとめ

* CMS の publish だけが 422 で落ちるときは、本文の外部画像を疑う。draft では通っても publish で弾かれる。
* 恒久対処は publish 直前のリホストゲート。冪等・fail-closed・全置換で組む。
* そして「気をつける」で終わらせず、失敗を記録して手順に埋め込む。これが再発を止める唯一の方法。

---

私たちは、AIエージェントの運用で踏んだこうした失敗を「記憶」として積み上げ、同じ失敗を繰り返さない仕組みづくりを [Agent Memories](https://agentmemories.jp/) として進めています。記憶をモデルの外側に置くことで、どのAIに挿しても同じ前提と失敗回避が戻るようにする——そんなレイヤーを目指して、実録とともに育てている最中です。
