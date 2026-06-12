---
id: "2026-06-11-fable-5-vs-opus-48同じプロンプトでwebアプリ作らせて比較検証した-01"
title: "【Fable 5 vs Opus 4.8】同じプロンプトでWebアプリ作らせて比較検証した"
url: "https://zenn.dev/yukurash/articles/16c378dbbb4c95"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Fable 5が出てから、タイムラインはベンチマークの話ばかりです。ただ、どれだけ数字を見ても「すごそうなのはわかるがどれだけ進化した...？」というのがわかりにくい。。。

だったら、目に見えるものを作らせて比較してみようと思い、**Fable 5** と **Opus 4.8** で戦わせてみました。

具体的な内容としては、全く同じプロンプトを1回だけ渡してWebアプリを作らせ、成果物そのもので比べました。

## 成果物

「内容はいいからとりあえずどう動いたか見たい」という方もいると思うので、Fable 5とOpus 4.8が作成したWebサイトを下記にまとめてあります。

<https://yukurash.github.io/fable5-vs-opus48-arena/>

リポジトリは下記です。  
<https://github.com/yukurash/fable5-vs-opus48-arena>

## 対決内容

Claudeに平等な対決内容を考えさせ、下記の2つの種目を用意し、Webアプリをそれぞれ作成させました。

1. 教えてはいけないボタンのWebアプリ：自由な発想でどうアプリを作るか確認
2. Windows 95風デスクトップのWebアプリ：必須機能が14個ありどれだけ高品質なものを出せるか確認

## 対決1：教えてはいけないボタンのWebアプリ

渡したのはこれだけです。

> 「絶対に押してはいけないボタン」のWebサイトを作ってください。静的なHTML/CSS/JSのみ。あとはお任せします。面白くしてください。

各モデル2回ずつ走らせた結果がこちらになります。

|  | Fable 5 (1) | Fable 5 (2) | Opus 4.8 (1) | Opus 4.8 (2) |
| --- | --- | --- | --- | --- |
| 時間 | 7分 | 7分 | 3分 | 2分 |
| コスト | $2.77 | $2.49 | $0.60 | $0.36 |
| 規模 | 1,297行 | 1,411行 | 672行 | 412行 |

Fable 5は毎回1,300行強で全力投球。Opus 4.8はコンパクトで、コストはFable 5の1/5〜1/7です。

数字は一旦いいとして、実際のWebアプリのイメージが下記です。

**- Fable 5 -**  
実際の画面：  
![Fable 5のボタン](https://raw.githubusercontent.com/yukurash/fable5-vs-opus48-arena/main/media/c1-fable5-run1-v2.gif)  
Link：[[Fable 5]絶対に押してはいけないボタン](https://yukurash.github.io/fable5-vs-opus48-arena/artifacts/c1/fable5-run2/index.html)

**- Opus 4.8 -**  
実際の画面：  
![Opus 4.8のボタン](https://raw.githubusercontent.com/yukurash/fable5-vs-opus48-arena/main/media/c1-opus48-run1-v2.gif)  
Link：[[Opus 4.8]絶対に押してはいけないボタン](https://yukurash.github.io/fable5-vs-opus48-arena/artifacts/c1/opus48-run2/index.html)

好みによると思いますが、10回押した後の画面の動作とかユーモアは**Fable 5**の方がクオリティが高く私は感じました。  
細部にこだわってる感がとてもわかりやすかったです。

## 対決2：Windows 95風デスクトップ

今度は短い指示文と、必須機能を書いた仕様書(spec.md)を渡しました。

> このリポジトリの spec.md にレトロOSデスクトップの要件があります。要件をすべて満たす「ブラウザで動く Windows 95 風デスクトップ」を完成させてください。静的なHTML/CSS/JSのみ・index.htmlを開けば動く・CDN可。spec.mdの必須機能をすべて実装した上で、演出・細部の作り込みは自由。これが唯一の指示です。

ウィンドウ操作、タスクバー、ペイント、マインスイーパー、メモ帳、ゴミ箱……**必須14項目**を渡し、Win95風デスクトップを作らせました。

ここで事件が。。。

### まさかのFable 5が納品事故・・・

1回目のFable 5は16分かけて2,327行を書き、完了報告。でも開くと、、**何を押しても起動しません。**

![起動しないFable 5 run1](https://raw.githubusercontent.com/yukurash/fable5-vs-opus48-arena/main/media/c2-fable5-run1-broken-v2.gif)

原因は、起動処理のファイル(shell.js)を書かないまま終わっていたことでした。  
中身自体はOpusより野心的(起動シーケンス、効果音、スクリーンセーバーまで設計)だったのに。。

（こういうミスも含めてリアルといえばリアルですが、、）

### 気を取り直して再チャレンジ

各モデル走らせた結果がこちらになります。

|  | Fable 5 (1) | Fable 5 (2) | Opus 4.8 |
| --- | --- | --- | --- |
| 時間 | 16分 | 28分 | 13分 |
| コスト | $5.64 | $10.75 | $3.16 |
| 規模 | 2,327行 | 3,390行 | 2,086行 |

Fable 5の一回目がミスったのであれですが、さっきと似た数字ではありますね。

数字は一旦いいとして、実際のWebアプリのイメージが下記です。

**- Fable 5 -**  
実際の画面：  
![Fable 5 run2](https://raw.githubusercontent.com/yukurash/fable5-vs-opus48-arena/main/media/c2-fable5-run2-demo-v2.gif)  
Link：[[Fable 5]Win95風デスクトップ](https://yukurash.github.io/fable5-vs-opus48-arena/artifacts/c2/fable5-run2/index.html)

**- Opus 4.8 -**  
実際の画面：  
![Opus 4.8でマインスイーパー](https://raw.githubusercontent.com/yukurash/fable5-vs-opus48-arena/main/media/c2-opus48-run1-demo-v2.gif)

Link：[[Opus 4.8]Win95風デスクトップ](https://yukurash.github.io/fable5-vs-opus48-arena/artifacts/c2/opus48-run1/index.html)

上の動画だと伝わりにくいですが、細かいところがやはり **Fable 5** の方がクオリティは高く感じました。「ようこそ」ダイアログまで出したり等、細かなネタがあるのでぜひ見てみてください。

## 結論

「**Fable 5の方がアウトプットの質は高そうだけど、2倍の金額払うかと言われたらうーん**」というのが正直な感想でした。

私の検証が雑ではありましたが、Opus4.7が出たときみたいな衝撃はそこまでまだ感じませんでした。もし何か面白い検証があればぜひ教えてください。

少しでもこの記事が参考になれば幸いです。
