---
id: "2026-05-27-claude-codeはいま-flibbertigibbeting-している-01"
title: "Claude Codeはいま Flibbertigibbeting している"
url: "https://qiita.com/insei_99/items/ac90d5e3ce42217a07ff"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

## はじめに
Claude Codeを使っていると、処理中にこんな表示がくるくる切り替わる。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2510592/55e7e14d-f159-438a-b1d3-1fb729ad39ac.png)


```
✻ Newspapering… (3s)
✻ Pondering… (5s)
✻ Flibbertigibbeting… (7s)
```

Pondering（熟考中）はわかる。Newspapering は新聞配達でもしているのか。Flibbertigibbeting に至っては辞書を引かないと意味が取れない。**処理中に表示されるing形の動詞は、固定でもなく数個の使い回しでもなく、200個近いセットからランダムに引かれている。**

実装はネイティブバイナリ内に文字列定数として並んでいる。なお Claude Code は内部実装の詳細を公式に公開していないため、本記事では**観察できる範囲**に絞り、特徴的な動詞だけを引用する。

## 雑多に見えて、強い偏りがある

200近い動詞は無作為ではない。いくつかのクラスタに明確に偏っており、開発作業の待ち時間に対する設計者の態度がそこに出ている。**いちばん独自性が高いのが、辞書を引きたくなるレベルの古風・ナンセンス英語の塊だ。**

### ナンセンス英語の重厚な層

```
Flibbertigibbeting    おしゃべりに興じる
Lollygagging          ぐずぐずする
Discombobulating      混乱させる
Hullaballooing        大騒ぎする
Razzle-dazzling       派手にやる
Whatchamacalliting    あれをする（あれ、なんだっけ）
Tomfoolering          ばかげたまねをする
Boondoggling          無駄仕事をする
Wibbling              ぐずぐず動く
Befuddling            煙に巻く
```

待ち時間にAIが返してくる文言が `Lollygagging…`（ぐずぐずしている）や `Boondoggling…`（無駄仕事をしている）だと、表示として完全に正解だ。AIが「いま何してるの」に対して「いや、ちょっと、その、あれ……」と返してくるのを意図的に演出している。

### 自己言及と小ネタ

```
Clauding              Claudeしている
Gitifying             gitっぽくしている
Newspapering          新聞している（？）
```

`Clauding` は固有名詞の動詞化、`Gitifying` はコードを書く文脈をそのままメタ動詞にしたもの。どちらも意図が読める。

### 料理が一大勢力

開発の待ち時間を**コンパイルではなく仕込み時間**として演出する語が並ぶ。

```
Marinating   Sautéing       Caramelizing  Whisking
Kneading     Flambéing      Julienning    Proofing
Tempering    Simmering      Drizzling
```

`Marinating…`（漬け込み中）や `Tempering…`（テンパリング中）が出ると、4秒の待ちでも腹を立てづらくなる。これが本記事の主張の核で、スピナー文言は単なる装飾ではなく、**待ち時間の体感を変えるためのUIコンポーネント**として機能している。

### その他の小さなクラスタ

| クラスタ | 例 |
|---|---|
| 思考系のバリエーション | Pondering, Cogitating, Ruminating, Cerebrating, Pontificating |
| ダンス・音楽 | Moonwalking, Jitterbugging, Sock-hopping, Beboppin' |
| 魔法・SF | Prestidigitating, Hyperspacing, Quantumizing, Photosynthesizing, Levitating |
| 動物のしぐさ | Slithering, Waddling, Scampering |
| オノマトペ寄り | Booping, Smooshing |

`Pontificating…`（偉そうに講釈している）はAIに対するセルフ皮肉として面白いが、こうした語は数だけ見ればナンセンス英語層より少ない。

## 自分の動詞を仕込める

`settings.json` に `spinnerVerbs` を書くと、ランダム選択の母集団を拡張・置換できる。

```json
{
  "spinnerVerbs": {
    "mode": "append",
    "verbs": ["Love-machine-ing", "Koikoi-ing", "Yoroshiku-ing"]
  }
}
```
サマーウォーズごっこも可能
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2510592/2b7edb80-8a84-46d4-8bca-27637e52d7aa.png)


## 何が言えるか

スピナー文言は、AIエージェントの待ち時間UXに対するひとつの解答だ。プログレスバーを精密にするのではなく、**「いま何が起きているか」を真面目に見せることを諦め、語彙の幅で時間の質を変える**という設計判断である。Claude Codeは Pondering（熟考）と Lollygagging（ぐずぐず）を同列に並べることで、AIに対するユーザーの期待値を意識的にコントロールしている。

待ち時間が `Flibbertigibbeting…` だと、ちょっと許せる。それは UI の勝利だ。
