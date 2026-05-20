---
id: "2026-05-19-vercel-が作った-ai-のための言語-zero-ってなんなの-01"
title: "Vercel が作った AI のための言語 Zero ってなんなの？"
url: "https://zenn.dev/ymtdir/articles/215fdc89851791"
source: "zenn"
category: "ai-workflow"
tags: ["API", "JavaScript", "TypeScript", "zenn"]
date_published: "2026-05-19"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Vercel が「AIエージェントのための言語」Zero を OSS リリースした
* エラー出力を `--json` で叩くと、エージェントがそのまま修正に使える構造化データが返ってくる
* まだ実用できるものではないが、コンセプトは知っておいて損はない

---

Vercel が新しいプログラミング言語を出した、という話を見かけて気になって調べてみた。

「AIのための言語」というキャッチコピーがあったので最初は「また大げさな…」と思ったんだけど、設計の意図を読んだらけっこう面白かったので記事にしておく。

ちなみに自分は TypeScript / JavaScript メインで、Rust はほとんど書いたことがない。Zero は「Rust に近い」と言われているので、その辺も調べながら書いた。

## Zero ってなに？

Vercel Labs が 2026 年 5 月にリリースした実験的なシステム言語。拡張子は `.0`（ゼロ）。Rust や Zig に近い構文で、ネイティブバイナリにコンパイルされる。バイナリサイズが 10KB 以下になるのが売りらしい。

## 何が違うのか

### コンパイラの JSON 出力が「設計の中心」になっている

これが一番の特徴だと思う。

普通の言語のコンパイルエラーって、こういう英文テキストで出てくる：

```
error[E0425]: cannot find value `wrold` in this scope
 --> src/main.rs:3:5
```

AI エージェントがこれを修正しようとすると、英語をパースして「たぶんこういう意味だろう」と推測するしかない。

Zero の場合、`--json` フラグを付けると、エラー位置・期待値・実際の値・修正案がすべて構造化された JSON で返ってくる。エージェントはそのまま受け取って自動修正に使える。

特に面白いのが **`fixSafety`（修正の安全度ラベル）** で、5 段階のラベルが付いてくる：

* `format-only` — フォーマット変更のみ
* `behavior-preserving` — 挙動は変わらない
* `local-edit` — そのスコープ内で完結する
* `api-changing` — 公開 API が変わる
* `requires-human-review` — 人間の確認が必要

エージェントが「この修正は勝手にやって OK か、人間に確認すべきか」を判断できる仕組みになっている。これは普通の言語にはない発想で、ちょっと感心した。

「今の AI でも普通の言語のエラーくらい読めるんじゃ？」という気持ちもわかる。自分もそう思った。ただ「英文をパースして推測する」のと「最初から構造化データとして取り出す」のは、安定性も速度も違う。

### 副作用が関数の型に強制される

hello world がこう：

```
pub fun main(world: World) -> Void raises {
    check world.out.write("hello from zero\n")
}
```

最初これを見て「`World` って何？」となった。

`World` は「外の世界にアクセスするための権限」みたいなもの。これを受け取っていない関数は外部に何も触れない。print すら書けない。

つまり関数シグネチャを見れば、「この関数が副作用を持つかどうか」が一目で分かる。コードレビューがめちゃくちゃ楽になりそう。

Rust をちゃんと知っている人から見るとどうなんだろうと思って調べたら、Rust よりだいぶシンプルらしい（その分、安全性の保証は Rust より弱い）。ただ「読んで分かりやすい」という点では Zero のほうが上かもしれない。

## 基本的な書き方

Rust を知らない自分がドキュメントを読んで把握した範囲：

```
// 変数（let はイミュータブル、let mut がミュータブル）
let message = "hello"
let mut counter = 0

// 関数
fun answer() -> i32 {
    return 40 + 2
}

// if / else（条件は Bool 必須、整数の truthy 判定は不可）
if value == 42 {
    check world.out.write("math works\n")
} else {
    check world.out.write("math broke\n")
}

// for ループ
for index in 0..4 {
    check world.out.write("tick\n")
}

// 構造体は shape
shape Point {
    x: i32,
    y: i32,
}
let point = Point { x: 40, y: 2 }

// ペイロード付き列挙は choice（Rust の enum に近い）
choice Result {
    ok: i32,
    err: String,
}

match result {
    .ok => value { /* 成功 */ }
    .err => message { /* 失敗 */ }
}
```

`class` はない。TypeScript 出身としては少し戸惑うけど、`shape` と `choice` の組み合わせで大体のことは表現できそう。

`check` は「失敗するかもしれない処理」に付けるキーワードで、失敗したら呼び出し元に伝搬する。TypeScript の感覚だと「`try/catch` を 1 単語に圧縮した糖衣構文」、Rust の `?` 演算子に近いらしい。

## インストールは npm じゃない

「Vercel の言語なら npm で入るだろう」と思ったら違った。シェルスクリプトでインストールするグローバル CLI ツール。

```
curl -fsSL https://zerolang.ai/install.sh | bash
export PATH="$HOME/.zero/bin:$PATH"
zero --version
```

pnpm も npm も不要。`devDependencies` に書けないのは、チーム導入のハードルとしてはちょっと高い。

## まだ実用は厳しい

* パッケージレジストリなし
* 言語仕様は非安定（随時変わる）
* **公式が「本番環境では使うな」と明言**している

実用目的で触るのはまだ早い。ただ「AIエージェントがコードを書く前提でツールチェーンを設計し直す」という発想自体は面白くて、今後こういう考え方が他の言語やツールにも影響を与えていきそう。

とりあえず `zero check --json` の出力を一回見てみる、くらいの温度感でいいと思う。

## まとめ

1. Zero のキモは構造化された診断出力。エラーコードに加えて **「修正の安全度ラベル」** まで付いてくるので、エージェントがそのまま修正ループを回せる
2. `World` 型で副作用を強制するので、コードを読んだだけで何をする関数か分かる
3. 今すぐ使えるものではないが、「AIファーストな設計」のリファレンスとして見る価値はある

## 参考
