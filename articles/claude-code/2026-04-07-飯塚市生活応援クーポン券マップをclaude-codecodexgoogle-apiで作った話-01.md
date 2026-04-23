---
id: "2026-04-07-飯塚市生活応援クーポン券マップをclaude-codecodexgoogle-apiで作った話-01"
title: "飯塚市生活応援クーポン券マップをClaude Code×Codex×Google APIで作った話"
url: "https://qiita.com/Kawashima_RPA/items/d13a1aa23ed813f0e6f5"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

# 飯塚市生活応援クーポン券マップをClaude Code×Codex×Google APIで作った話

**作ったサイト: <https://www.afr-iizuka-seikatsu-coupon-2026.jp>**

## なぜ作ったのか

### PDFの一覧表、本当に使いにくい

飯塚市では2026年度、「生活応援クーポン券」が配布されました。でも配布されるのはPDFの一覧表。店舗名がびっしり並んでいるだけで、「この近くに使えるお店あるかな？」と思っても全然わかりません。

[![元のPDF一覧表](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FAutoFor%2Flife-public%2Fmain%2Fqiita%2F20260406-iizuka-coupon%2F2026-04-07_14h13_26.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=406649e39f403803d461575e3fbcfae8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FAutoFor%2Flife-public%2Fmain%2Fqiita%2F20260406-iizuka-coupon%2F2026-04-07_14h13_26.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=406649e39f403803d461575e3fbcfae8)

毎回クーポンを使う気満々で一覧を開いても、気づいたら「もういいや…」となってしまう体験、心当たりがある方も多いのではないでしょうか。

### 有名店・大型店ばかりにクーポンが集中する問題

もう一つ気になっていたのが、クーポンの偏りです。知名度の高いチェーン店や有名どころは自然と使われやすく、一方で地元の小さな個人店はPDF一覧の中に埋もれてしまって気づかれません。

「試しに使ってみようか」というお試し層の流入も、目につきやすいかどうかで大きく差が出てしまいます。地図で視覚的に表示すれば、近くの知らなかったお店に気づいてもらえるきっかけになるはずです。

### 事務員さんの更新作業も大変なはず

クーポン券は配布のたびに店舗リストが変わります。市職員の方や担当事務員さんが毎回ExcelやPDFを手作業で更新している光景は想像に難くありません。

「こういうWebサービスあったらいいよね」という声は、市の職員からも市民からも出ていると思います。でも実現までには「誰がどうやって更新するの？」という壁があります。AIを使えばその更新作業を自動化・省力化できるはずという仮説を証明したいと思いました。

### Claude CodeやCodexで何かできないか試してみたかった

正直なところ、もう一つの動機はこれです。Claude CodeとCodexが手元にある、何か実用的なものを作ってみたい。PDFをデータ化して地図に表示するというのは、ちょうどよい実験台でした。

---

## どうやって作ったか

### 構成の全体像

```
PDF（市配布）
   ↓ Perplexityで店舗名・住所を抽出
CSV（stores.csv）
   ↓ Python × Google Places API で緯度経度・カテゴリを付与
stores_enriched.csv
   ↓ Claude Code でフロントエンド開発
Leaflet.js マップ（index.html + app.js）
   ↓ Azure Functions
お問い合わせAPI（contact.js）
```

### 使ったツール

| ツール | 用途 |
| --- | --- |
| **Perplexity** | PDFから店舗名・住所の一覧を抽出 |
| **Claude Code** | フロントエンド実装・スクリプト生成 |
| **Codex** | Pythonスクリプトのロジック補完 |
| **Google Places API** | 店舗名から緯度経度・カテゴリを自動取得 |
| **Azure Functions** | お問い合わせフォームのバックエンドAPI |

### Step 1: PDFから店舗データを作る

まず元データはPDFしかありません。Perplexityに投げて店舗名と住所の一覧をCSV形式で吐き出してもらいました。完璧ではないので目視確認は必要ですが、手作業でタイピングするよりはるかに速いです。

### Step 2: Google Places APIで緯度経度とカテゴリを補完

`stores.csv`には店舗名と住所だけしかありません。地図表示するには緯度経度が必要です。

Python スクリプト（`scripts/enrich_stores.py`）を Claude Code + Codex で書き、Google Places API の Text Search を使って店舗名から自動で緯度経度・カテゴリを取得しました。

```
# 概念的な処理フロー
for store in stores:
    result = google_places_text_search(store["店舗名"] + " 飯塚市")
    store["lat"] = result["lat"]
    store["lng"] = result["lng"]
    store["category"] = map_type_to_japanese(result["types"])
```

Google Places APIはリクエスト数に応じた従量課金ですが、今回の規模（数百件程度）では無料枠内に収まりました。

### Step 3: フロントエンドをClaude Codeで実装

地図ライブラリは**Leaflet.js**（無料・OSS）を採用しました。Claude Codeに「こういうフィルタが欲しい」「カテゴリ別に色分けしたい」と会話しながら `app.js` と `style.css` を作り上げました。

機能：

* **カテゴリフィルタ**（飲食・美容・医療など）
* **券種フィルタ**（紙クーポン・デジタルクーポン・両方）
* **店舗名検索**
* **地図上にピンを表示** → クリックで詳細表示
* **スマホ対応**（サイドパネルの開閉、モバイルUI）

### Step 4: お問い合わせAPIをAzure Functionsで

「掲載内容に誤りがある」という連絡を受け取れるよう、Azure Functions（Node.js）でお問い合わせフォームのAPIを実装。Azure Communication Services経由でメール通知する構成です。

---

[![完成したクーポンマップ](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FAutoFor%2Flife-public%2Fmain%2Fqiita%2F20260406-iizuka-coupon%2F2026-04-07_14h17_43.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=02444806353b5f65c339150b073d41f9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FAutoFor%2Flife-public%2Fmain%2Fqiita%2F20260406-iizuka-coupon%2F2026-04-07_14h17_43.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=02444806353b5f65c339150b073d41f9)

---

## コスト感

| サービス | 費用 |
| --- | --- |
| Google Places API（データ取得時のみ） | 無料枠内（$200/月クレジット） |
| Azure Functions | 無料枠内（月100万リクエストまで無料） |
| Azure Communication Services | 送信メール数に応じた従量課金（小規模なら月数円〜） |
| Leaflet.js | 無料・OSS |
| **Claude Code・Codex** | **月額約3,000円**（サブスクリプション） |
| ホスティング | Azure Static Web Apps 無料枠 or GitHub Pages |

**トータルの実費はAPI利用料1,000円未満＋Claude Code/Codexの月額約3,000円**です。API系（Google Places・Azure・Perplexity等）はすべて無料枠内か数百円程度に収まりました。Google Places APIのデータ取得は一回走らせるだけなので$200の無料枠を超えることはなく、ランニングコストも問い合わせが殺到しない限り無料枠内で収まる想定です。

---

## やってみてわかったこと

### AIは「雑用」を引き受けてくれる

PDFからのデータ抽出、APIリクエストのスクリプト生成、フロントのUI実装。どれも「わかっていれば時間さえかければできる」作業です。でも全部一人でやろうとするとかなりの工数がかかる。Claude CodeとCodexがいれば、自分はディレクション（何を作りたいか）に集中できて、実装の大部分はAIに任せられました。

### 更新作業の自動化が現実的

来年クーポン対象店舗が変わっても、やることは「新しいPDFをPerplexityに投げてCSV更新 → Pythonスクリプト再実行」だけです。フロントエンドは触らなくてよいです。市の担当者でなくても、ボランティアの市民開発者でも継続的に運用できる形になっています。

### 「できそう」の証明が大事

市役所や行政機関には「こういうサービスがあればいい」という声は届いていると思います。でも「誰がどう作って、誰がどう維持するのか」がわからないと動けない。今回のプロジェクトは、**AIツールを組み合わせれば市民がゼロコストに近い形で作れて、維持できる**という一つのProof of Conceptになりました。

### デザインに「Claude Codeっぽさ」が残る

正直な反省点として、デザインがいかにもAI生成という雰囲気を脱しきれませんでした。Claude Codeに指示を出して実装してもらうと、どうしても似たようなレイアウト・配色になりがち。「もう少し洗練させたい」と思っても、デザインの細かいニュアンスを言語で伝えるのは難しく、何度かやりとりしても大きくは変わりませんでした。

デザインに強いこだわりがある場合は、FigmaなどでモックアップをAIに渡す、あるいはデザイナーとの協働が必要だと感じます。機能を作るのはAIが得意でも、「らしさ」や「好み」の部分はまだ人間が手を入れる余地が大きいです。

### スマホ・PCのレイアウト調整が指示だけでは進まない

レスポンシブ対応も苦労しました。「スマホでサイドパネルが崩れる」「PCでは横並びにしたい」といった指示を出しても、修正が部分的だったり別の箇所が崩れたりと、なかなか一発で決まらない。

ここは**Playwrightでスマホ・PCそれぞれのビューポートをスクリーンショット撮影するテストを書いて、Claude Codeに渡すサイクルを回す**べきでした。テスト結果（画像）を根拠に修正指示を出せば、「どこがどう崩れているか」が明確になり、手戻りを大幅に減らせたはずです。

### 店舗データの収集・整備こそ一番の手間

実は今回いちばん地味に大変だったのが、店舗データの整備です。全レコードに対して「緯度経度を取得する」「カテゴリを決める」「説明文を作る」「公式サイトのURLを調べる」を繰り返すのは、数が多いと本当に骨が折れます。

ただ、見方を変えると**この作業こそAIが最も得意な領域**です。店舗名と住所さえあれば、AIに「緯度経度・カテゴリ・説明文・公式リンクをまとめて出力して」と一括指示できます。今回はPythonスクリプト＋Google Places APIで緯度経度は自動化しましたが、説明文や公式リンクはまだ手作業が残りました。

この部分を丸ごとAIに任せるフローを組めば、**担当者の作業時間を大幅に削減できる**という確信がより強まりました。市の事務員さんがPDFを更新するたびに手作業でExcelを直している光景と比べると、改善余地は非常に大きいと思います。

### 意外な発見：地元にこんなにお店があったのか

作ってみて一番の驚きは、飯塚市にこれだけ多くの個人店舗があることを自分自身が知らなかった、ということです。

正直なところ、クーポンを使うなら大手スーパーで生活費に充てようかな、くらいの気持ちでいました。でも地図にピンを打っていくうちに、「こんなところにこんなお店が？」という発見が次々と出てきました。

**マップを作ること自体が、今まで行ったことのないお店への導線になりました。** 情報が整理されて初めて気づける価値というのは、想像以上に大きかったです。クーポン施策の本来の目的である「地域経済の循環」という観点でも、可視化には意味があると改めて感じました。

---

## おわりに

飯塚市生活応援クーポン券マップは、「PDFがわかりにくい」という些細な不満から始まりました。でもその背景には、地元商店への流入を増やしたいという思いと、事務員さんの更新負担を減らしたいという課題意識がありました。

Claude Code・Codex・Perplexity・Google APIを組み合わせれば、こういった**行政サービスの可視化や利便性向上を市民が自分で作れる時代**になっています。

同じような「あったらいいのに」を持っている人のヒントになれば幸いです。

---

*サイト: <https://www.afr-iizuka-seikatsu-coupon-2026.jp>*  
*ソースコード: [AutoFor/iizuka-coupon-map](https://github.com/AutoFor/iizuka-coupon-map)*
