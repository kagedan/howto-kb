---
id: "2026-05-10-claudecode-lab-httpstcod2q8t4yxtt-01"
title: "@claudecode_lab: https://t.co/D2q8t4Yxtt"
url: "https://x.com/claudecode_lab/status/2053290657788391819"
source: "x"
category: "claude-code"
tags: ["claude-code", "JavaScript", "x"]
date_published: "2026-05-10"
date_collected: "2026-05-12"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/D2q8t4Yxtt


--- Article ---
Claude Codeの出力フォーマットをめぐって、興味深い議論が起きています。きっかけはClaude Code創設者のThariq（@trq212）の「[The Unreasonable Effectiveness of HTML](https://x.com/trq212/status/2052809885763747935)」という投稿。

「Markdownは100行を超えると読まれなくなる」「HTMLなら色・表・インタラクションをすべて1ファイルに収められる」という主張で、5.1Mビューを記録しました。Claude Codeチーム内でもHTMLへの移行が進んでいると言います。この記事では、その主張を詳しく紹介しながら、**実際にHTMLとMarkdownの両フォーマットでドキュメントを作成し、生成時間・トークン数・読みやすさを数値で比較しました。**単純な「どちらが良いか」ではなく、それぞれが向いている場面を見極めることを目指します。

# Claude Codeチームが「HTMLに切り替えた」理由

Markdownはこれまで、AIとのやり取りで生成されるドキュメントの主役でした。シンプルで、どこでも開けて、編集もしやすい。Claude自身もMarkdownファイルの中でテキストだけで図を描けるほど上達しています。

ただ、問題もあります。100行を超えたMarkdownファイルは、正直なところあまり読まれません。仕様書も計画書もPRの説明文も、ざっと流し読みされるか、最悪そもそも開かれないまま終わることが多いです。

HTMLに切り替えることで変わるのは、この「読まれない問題」です。Thariqは「私はこれらのファイルを自分で編集することが減り、仕様書・参照ファイル・ブレインストーミングの出力として使うようになっている。編集するときもClaudeに任せることが多く、それによってMarkdownの最大のメリットの一つが失われている」と述べています。

# HTMLが持つ6つの優位性

## 1.情報密度（Information Density）

![](https://pbs.twimg.com/media/HH66xLDbcAAow5z.jpg)

HTMLが1ファイルで扱える情報の種類は、Markdownの比ではありません。

- テーブルを使った表形式データ
- CSSを使ったデザイン
- SVGで描いた図解・イラスト
- scriptタグを使ったコード例
- JavaScriptとCSSによるインタラクション
- SVGとHTMLを使ったワークフロー図
- 絶対位置指定とcanvasを使った空間データ
- imageタグを使った画像
Claudeが扱える情報であれば、ほぼすべてをHTMLで表現できます。しかし、Markdownで色を表現するのはほぼ不可能です。

![](https://pbs.twimg.com/media/HH67b0AbIAAhWhq.jpg)

視覚的な差は一目瞭然です。同じ情報が、片方は「読まなければわからない」状態で、もう片方は「見ればわかる」状態で出てきます。

## 2.視覚的な明瞭さ

Claudeがより複雑な作業をこなせるようになるにつれ、より大きな仕様書や計画書を書くようになっています。しかし、100行を超えるMarkdownファイルは読まれない傾向があり、組織内の他の人に読んでもらうことも難しいです。

HTMLドキュメントはタブ、イラスト、リンクを使って視覚的に最適な構造を組み立てられます。モバイルレスポンシブにすることもでき、フォームファクターに応じた読み方が可能です。

## 3.共有のしやすさ

Markdownファイルはほとんどのブラウザがネイティブにレンダリングしないため、共有が難しいです。メールに添付したり、GitHubに上げたりしてようやく読んでもらえる状態になります。

HTMLならS3にアップロードするだけでURLが生まれ、誰でもどこからでも開けます。仕様書、レポート、PRの説明書を実際に読んでもらえる可能性が格段に上がります。

## 4.双方向インタラクション

![](https://pbs.twimg.com/media/HH67nQIbwAAZ2QS.jpg)

HTMLはドキュメントとのインタラクションを可能にします。スライダーを動かしてアニメーションパラメータを調整したり、異なるアルゴリズムのオプションをビジュアルで試したりできます。「調整した内容をClaude Codeに貼り戻す」ボタンも追加できます。これにより、人間とAIが1つのHTMLファイル
