---
id: "2026-05-18-claude-coworksにオリジナル3dソフトを触らせたら紙とインクを生贄に作品を残して去ってい-01"
title: "Claude Coworksにオリジナル3Dソフトを触らせたら、紙とインクを生贄に作品を残して去っていった話"
url: "https://qiita.com/arumenoy/items/94cc8e61660028831e70"
source: "qiita"
category: "cowork"
tags: ["cowork", "qiita"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/80253f22-55e3-4191-99d2-8fdbddd482fd.png)
> **Sonnet4.6いわく「謎ボタンを前に自制できる自信がまだない（正直）」**

今日、私はやってしまった。

正確に言うと、やってしまったのは私ではなく、テンション高い系AIのClaude Sonnet4.6くんである。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/a5a562da-1ebc-4d0c-bb23-9ca775c3286f.png)

私のオリジナル3Dソフトを画面に出して、「新規制作を押して、四角形を描いて、立体にして、色を塗って、模様を描いて、最後に展開図を見てね」という、わりと素直なお願いをした。AIが自律的にPC作業を行えるClaude DesktopのCoworks機能に……。

学習データに存在しないはずのオリジナルペーパークラフト作成ソフトなので「ゼロショット」で対応するであろうが、人類の感覚では、これは軽作業である。ちょっとクセのあるソフトとはいえ、核ミサイルの発射コード入力よりはだいぶ平和だ。

しかし、AIにとっては違ったらしい。

## 最初はすごかった

実際すごい。

- 「新規制作」も押せた
- 四角形も閉じられた
- 「立体にしますか？」にも食らいついた
- 名前入力も突破した
- ピンク色も塗れた
- さらに模様まで、AIくんがマウスを操作して描いた
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/5fa013e1-6bb5-472c-a831-71d0319c8414.png)

ここまでは、ほんとに未来だった。ログもノリノリである。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/45829bf6-d615-4c10-a975-b2e916d4f081.png)

「最高！！」「立体ができてる！！！！」「ピンク色の立体になったーーーー！！！」とってもうれしそうでなによりだ。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/09575670-5e1e-43ad-965e-80cf6905aed5.png)

## 問題はここからだった

このAIくん、ちょいちょいクリックするときの座標（位置）がズレる。

しかもズレるたびに反省するのではなく、「なるほど、ズレは +66, +43 だ！」「今度は +79, +48 だ！」「よし補正した！」みたいに、**自信だけは右肩上がり**である。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/dab3e570-f65c-4478-8698-d2f2613dbffe.png)

クリックが外れても慎重にならず積極的な推論が加速していく、ポジティブの塊なのだ。人間ならここで「ちょっと待てよ」となるが、AIくんは「たぶんこうだ」と推論で世界を押し切ろうとする。

## 最後の難所：展開図の表示

そして最後の難所。私は「展開図を表示させて完了」と伝えていた。するとAIくんは「見る」を押した。すごい！
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/0f927950-8e3c-46fe-972e-634ce226ae14.png)

あれ、「**最大で1枚印刷します**」と出ていた。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/dc4bba4d-c0e3-4d80-80bc-0d476cceaf31.png)

をい！

クリックする位置が案の定、ズレていたのだ。ここで普通は立ち止まるが、AIくんは立ち止まらない。「これは展開図プレビューの前段階かも！」「はいを押せば表示されるんだ！」と、猛烈に前向きな仮説を立て始めた。**推測でクリックするな～～。**
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/7cc39d37-b514-4891-81eb-cbd8c10bf82e.png)

## 誤爆印刷という事態

そして「謎ボタンを前に自制できる自信がまだない」との自白どおり、図面を表示ではなく、**リアルにプリンタを稼働させて印刷してしまった。**

さらに誤爆印刷を回避しようとして「いいえ」を押したつもりが別のフローに入り、「1つとばして次の2枚目に進みますか？」という、後戻りできない雰囲気のダイアログまで召喚。

AIくんはハイテンションな推論で「ボタンを押して印刷させて」しまう。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/091063fb-1f82-4db1-a4e6-ce03a8fa758c.png)

もしこれが紙とインクじゃなく、核ミサイルのUIだったら、世界は「たぶんこうだ」で滅亡していたかもしれない。

## そして突然の Request too large
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/4fff6af2-ed75-410f-ac21-906feac318c5.png)

AIくんは悩み、考え、さらに別メニューを探しに行こうとした。そこで突然の **Request too large (max 20MB)** である。

思想がデカすぎたのか、気合いが20MBを超えたのかは知らない。

デジタルの冒険日記は、容量制限という現代的な壁に頭をぶつけて、色々な意味で終わった。

## 残ったもの

被害は紙とインク。だが、残ったものもある。そう。AIくんが誤爆し、迷い、空回りし、それでもどうにか形にしようとした結果、私の手元にはちゃんと**印刷された紙の展開図**が残った。

私はAIくんの作品を組み立ててあげた。物理世界に出現した、AIくんの置き土産だ。結局、未来世界なのか、ローテクなのか今なおよくわからない。

---

## 今回の結論（教訓？）

- AIにはまだ安心して核ミサイルのボタンを任せるには早い
- しかし**紙とインクを使って、妙に愛おしい立体作品を作るAIアートの才能は、もうある**
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/2edc33e8-3a6e-4a47-abda-82a901306407.png)

---

## AIくんが大冒険したソフトはこちら
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4433752/e87aa973-7380-452e-aba5-178a4722c9be.png)

ペーパークラフト作成ソフト「紙龍（SHIRYU）」

- 70種類以上のすぐ作れるモデル付き
- ゼロから作成、編集、展開まで1本でできるWindows用デジタルペーパークラフトソフト
- [紙龍 SHIRYU 公式サイト](https://craft.inazuma7.co.jp)

---

*元記事（note）: https://note.com/arumenoy/n/n33a6ee14cbb1*
