---
id: "2026-04-25-claude-design-claude-code-で東海オンエアの企画用ツールを作ってみた-01"
title: "Claude Design × Claude Code で東海オンエアの企画用ツールを作ってみた"
url: "https://zenn.dev/citron24ah/articles/claude-design-x-claude-code-yubin-gacha-visual"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

**Claude Design** でプロダクトの見た目をまるごと組んで、できあがったものを **Claude Code** に URL 1 本で渡して実装まで走らせた。エージェント同士を URL で手渡しするような体験が、想像以上に地続きだった、という話。

題材は東海オンエアの企画用ツール『郵便ガチャ』。Claude Design のキャンバス・絵コンテ・実装後のバグ画面・修正後の画面まで、手元にあったスクショを並べながら振り返ってみる。

## 作ったもの：東海オンエアの企画ツール『郵便ガチャ』

実物 → **<https://yubin-gacha.citron24ah.workers.dev/>**（Cloudflare Workers で公開中、完全無料）

[東海オンエア](https://www.youtube.com/channel/UCutJqz56653xV2wwSvut_hQ)の人気企画:【まさかの東北】第１回！日本０円帰宅！！（[シリーズ第一回はこちら](https://www.youtube.com/watch?v=b7iWY4-5KoQ)）。日本全国どこかに置き去りにされたメンバーが、ヒッチハイクなり徒歩なりで岡崎に帰ってくるやつ。

行き先の決定は「ランダム7桁の数字を発番 → 郵便番号検索で実在するか確認 → ハズレなら再抽選」という手順でやっている。が、7桁の数字から実在する郵便番号を引き当てる確率はかなり低い。実在する郵便番号は全国で約 12 万件、7 桁の数字の組み合わせは 1,000 万通りなので、ざっくり **12% くらいしか当たらない**。動画収録中にガチャが外れ続けると、ただの待ち時間が発生する。

そこを短縮するために作ったのが『**郵便ガチャ**』。実在する郵便番号だけから 1 件をランダムに引いて、都道府県・市区町村・町域と、出発地からの直線距離まで表示する Web アプリ。ハズレがない。

特徴をまとめるとこう:

* 実在する郵便番号から 1 件だけ抽選（124,508 件、ハズレなし）
* 7 桁をルーレット演出で順に引いていくチャンキーな POP UI
* 出発地を都道府県＋市区町村で指定（localStorage に永続化）
* 結果画面で出発地からの直線距離を表示（岡崎→札幌で約 971km）
* Google マップへの外部リンクで地図もすぐ確認
* Cloudflare Workers + Static Assets にデプロイ（完全無料運用）

素材データは日本郵便が公開している `KEN_ALL.zip` が元で、市区町村単位の緯度経度は Geolonia が公開している `japanese-addresses-v2` から取ってきている。

で、いきなりだけどこれが完成形 — ただしまだ動いていない。

![Claude Design のキャンバス上にできあがった POP デザイン案（まだ動くアプリではない）](https://static.zenn.studio/user-upload/deployed-images/5edf88beca7e9f615f1925a2.jpg?sha=c782ae5130a34cf49ff47057e507446465a8afb2)

上のスクショは実は動いているアプリではなく、**Claude Design のキャンバス上にできあがったデザイン案**。実装する前のこの段階でほぼビジュアルは決まっていて、Claude Code には「この絵のとおりに組んで」と渡した形になる。

ここまでの実装（バックエンドと暫定 UI）は、普段どおり Claude Code と一緒に進めた。テストは 55 ケース、バンドルは gzip 後 54KB まで絞って、そこそこ真面目に作ったつもり。

でも今回の主役は、**そのアプリの見た目を Claude Design に全部任せた**という話。

## Claude Design って何？

自分も最初は Claude Design の名前すら知らなくて、作業途中に「そういえばそんな新機能なかったっけ？」と気づいた。調べてみる。

公式発表は [Claude Design アナウンス（Anthropic Labs）](https://www.anthropic.com/news/claude-design-anthropic-labs)。リリース直後でちょうど話題になっていたタイミングだった。要点はこんな感じ:

* **Claude Opus 4.7** を搭載した experimental プロダクト（research preview 段階）
* Claude Pro / Max / Team / Enterprise プランで利用可能
* プロトタイプ、スライド、1 枚ページ、モックアップを生成できる
* **コードベースやデザインファイルを読んで、自動でデザインシステムを組んでくれる**（既存の色・タイポ・コンポーネントをそのまま活かす）
* 要素ごとにインラインコメント・テキスト編集・スペーシング / 色 / レイアウトのノブ調整
* PDF / URL / PPTX / Canva 連携でエクスポート
* 裏側では [Canva の Design Engine が使われている](https://www.canva.com/newsroom/news/canva-claude-design/)（これは Canva の公式ニュースルームでアナウンスされている提携）

アナウンス当日には Figma の株価が動いた、という報道もちらほらあって（[TechCrunch](https://techcrunch.com/2026/04/17/anthropic-launches-claude-design-a-new-product-for-creating-quick-visuals/)）、ちょっとザワついていた印象がある。

で、とりあえず開いてみた（Claude Pro 以上のログインが必要）。

![Claude Design の初期画面。プロジェクトを作るとこの Start with context 画面が出てくる](https://static.zenn.studio/user-upload/deployed-images/5d80877c5c055478213d7a4f.jpg?sha=bd526f836ca446a9ed5b8685201ff5db2b14b6a0)

新しいプロジェクトを作るとこの画面が出てきた。Start with context の選択肢が 4 つ（Design System / Add screenshot / Attach codebase / Drag in a Figma file）と、右側に Design Files のツリー。正直、最初に見たときは「使い方マジでわからん…」となった。ボタンを押しても何も起きない感じがして、入口が掴めなかった。

Claude Code に「これの使い方どうするん」と投げたら、**Attach codebase** で GitHub リポを渡して、下の入力欄に要件を書けばいい、という流れを教えてもらった。コードベースを食わせる発想が無かったので、ここは自分では気づけなかった。

## バックエンドを先に作っておく

Claude Design を使う前提で、今回のワークフローは意図的に **バックエンド先行**で組んだ。デザインを後から差し込めるよう、UI 構造・データの形・状態遷移だけ先に固める方針。

データの持ち方だけは少し悩んだ。郵便ガチャは「`12` で始まる郵便番号には何がある？」→「`123` で始まるなら？」と **接頭辞で範囲を絞る** 操作を 1 桁ずつ走らせたいけど、一般的な郵便番号 API は「7 桁完全一致 → 住所」の単方向で、こういう用途には向かない。最終的には **ビルド時に KEN\_ALL.zip を取得して JSON 化、CDN 経由で配る** に着地した。約 12 万件で gzip 後 1.1MB、月次更新は GitHub Actions に任せて完全自動化。

実装の成果物はざっくりこんなところ:

* データ生成スクリプト（KEN\_ALL.zip → 約 12 万件の JSON）
* 抽選ロジック（ソート済み配列 + 二分探索）
* 距離計算（Haversine 式）
* 暫定 UI（ダーク背景に白い数字タイル、赤い STOP ボタン）
* 緯度経度のマージ（Geolonia の `japanese-addresses-v2` から市区町村単位で）
* 単体テスト 55 ケース、月次データ更新用の GitHub Actions

ポイントは、この段階で**デザインは意図的に雑**にしたこと。フレーム（UI 構造、データ表示、状態遷移、レスポンシブ）だけは真面目に組んでおいて、色や装飾やタイポは Claude Design が仕上げる前提で最小限に済ませた。

たとえば抽選ロジックのコア部分はこういう関数で、ここは最後まで変わらない:

```
function candidateDigits(zips: string[], prefix: string): number[] {
  const lo = lowerBound(zips, prefix);
  const hi = lowerBound(zips, nextPrefixBound(prefix));
  const pos = prefix.length;
  const set = new Set<number>();
  for (let i = lo; i < hi; i++) {
    const zip = zips[i];
    if (zip.length > pos) {
      set.add(Number(zip[pos]));
    }
  }
  return [...set].sort((a, b) => a - b);
}
```

二分探索で「ある接頭辞に一致する郵便番号の範囲」を取り、その位置にくる数字を集めてくるだけ。

こういう「動くけど見た目が地味」な状態を**完成品の一歩手前**にしておいたうえで、Claude Design に渡した。

## Claude Design にデザインだけお願いする

[claude.ai/design](https://claude.ai/design) に戻って、先ほどの Start with context 画面から **Attach codebase** を選び、GitHub リポを渡す。

下の入力欄に依頼内容を書く。こんなプロンプトを渡した:

> 東海オンエアの「所持金0円で岡崎に帰る」企画専用、実在郵便番号ルーレット Web アプリの UI デザインをお願いします。
>
> 要件：
>
> * 一発勝負の緊張感と「ガチャ」感
> * モバイルファースト
> * ダークテーマ基調（現状 bg-neutral-950 / 赤アクセント）
> * 3画面：ガチャ中 / 目的地をみるボタン表示時 / 結果画面
> * 東海オンエアっぽい遊び心（ただし無許可ロゴ等は避ける）
> * 7桁のルーレット数字が主役
>
> 既存実装は SPEC.md と src/ に入ってます。現行の暫定デザインを下敷きに、ロゴ・配色・タイポ・装飾の改善案を3パターンほど提示してください。

Claude Design は**パターンを並べて比較できる**のが強い。今回は 3 バリアントで提案が返ってきた:

* **TICKET** — 昭和の券売機レシート風、琥珀 × ドットマトリクス、ミシン目装飾
* **NEON PACHINKO** — パチンコ屋ネオン風、深紅 × シアンのグロー、スキャンライン
* **ZINE** — リソグラフ／zine パンク風、墨 × 紙 × 赤、ハンコ「済」、ハーフトーン

ここから「こういうイメージがいい」と参考画像を渡して方向転換。最終的に**POP 路線**に着地した。空色の背景に太い黒アウトライン、原色ベタ、ポスト・はがき・雲・太陽といった郵便モチーフで世界観を作る、という方針。

そのあと「Web 表示も欲しい」と追加注文したら、モバイルだけじゃなく**1200×820 のデスクトップ絵コンテ**まで描き足してくれた。結果画面はデスクトップでは 2 カラムで「行き先 | 距離＋Google マップボタン」になる、という形まで決まった。

まずはモバイル絵コンテから。

![Claude Design が出力した郵便ガチャのモバイル絵コンテ。ガチャ中・全桁確定・結果の 3 画面が並ぶ](https://static.zenn.studio/user-upload/deployed-images/21c195fa2a22bb1146e196f0.png?sha=f3d116fd267a398c7982de4e1147d58be485b98d)

続いてデスクトップ絵コンテ。

![Claude Design が出力したデスクトップ版の絵コンテ。結果画面は 2 カラムグリッドになる](https://static.zenn.studio/user-upload/deployed-images/fafefa99ea128bff9279047e.png?sha=3c05fef940560c1fea556575788901f3147967ff)

左から順に「ガチャ中」「全桁確定（目的地をみるボタン表示）」「結果画面」の 3 画面。**モバイルとデスクトップで別の絵コンテが用意されている**のがポイント。これは後でハマる伏線になる。

Claude Design の絵コンテは、ただの画像じゃなくて**HTML + CSS + JSX のコード**として出てくる。`Yubin Gacha.html` という単一ファイルが成果物になる。

## URL 1 本で Claude Code に手渡す — ハンドオフの地続き感

ここが今回いちばん驚いたところ。

Claude Design の右上に **Export** ボタンがあって、それを押すと、プロジェクト全体を `.zip`（もしくは `.tar.gz`）で落とせる。が、もう 1 つ別の動作があって、**プロジェクトを識別する URL が発行される**。

その URL を Claude Code のチャットにそのまま貼ると、こういう指示文が自動で付加される形になる:

```
Fetch this design file, read its readme, and implement the relevant aspects of the design. https://api.anthropic.com/v1/design/h/XXX?open_file=Yubin+Gacha.html
Implement: Yubin Gacha.html
```

URL を 1 本貼っただけで、Claude Code が勝手にバンドルを取りに行って、中のドキュメントを読み、実装まで走り始めた。「手渡しする」の感覚がほぼゼロ距離で、エージェント同士が直接話している場に立ち会っているような体験だった。

中身は `.tar.gz` のハンドオフバンドルで、解凍するとこんな構成:

```
yubin-gacha/
├── README.md          # 実装者（コーディングエージェント）向けの指示
├── chats/             # Claude Design 上での会話ログ
│   └── chat1.md
└── project/
    ├── Yubin Gacha.html    # メインの絵コンテ
    ├── variants/
    │   ├── pop.jsx         # モバイル版 POP
    │   ├── pop-desktop.jsx # デスクトップ版 POP
    │   └── ...
    ├── components/         # 既存コンポーネント（参考用）
    └── og-image.png, favicon.svg
```

そして `README.md` の頭にこう書いてある:

> # CODING AGENTS: READ THIS FIRST
>
> This is a **handoff bundle** from Claude Design.
>
> **Read the chat transcripts first.**  
> **Read `yubin-gacha/project/Yubin Gacha.html` in full.** Then **follow its imports**: open every file it pulls in so you understand how the pieces fit together before you start implementing.

**実装エージェント向けに指示が書いてある**。Claude Code はこの指示通りに chat ログ → メイン HTML → imports の順で読み込み、POP 配色の定数（`#8ed0f0`, `#e8443c`, `#ffd23f` など）、Yusei Magic / Kosugi Maru フォント、太い黒ストロークの積層テキストタイトル、「OK!」バッジ付き数字タイル、空 + 雲 + 太陽 + ポスト + 飛ぶはがきの背景構成、を React + Tailwind のコンポーネントに落とし込んでいく。

この「URL を渡すだけ → Claude Code が自分でバンドルを取りに行く → README の指示通りに読み解く → 実装する」というフローは、地続き感がすごい。Claude Design 側から「実装者向け指示」が書いてあって、Claude Code 側がそれを素直に受け取る、という**エージェント同士がやり取りする前提で設計されている**感じが伝わってきた。

そのあと、OG 画像と favicon もまとめてお願いした。「同じ POP のトンマナで」と一言添えただけで、こんなのが出てきた。

![Claude Design が生成した OG 画像（1200×630 PNG）。POP トンマナで「ハズレなしの郵便番号ガチャ」のキービジュアル](https://static.zenn.studio/user-upload/deployed-images/d6ad739f65eef36921aca889.png?sha=4d7afa314769d47cb0f1c4765461eedd6784fa0d)

![Claude Design が生成した favicon（780B の SVG）。黄色の角丸カードに赤い 〒 マーク](https://res.cloudinary.com/zenn/image/fetch/s--mM8p2ck4--/v1/claude-design-x-claude-code-yubin-gacha-visual/08-favicon.svg?_a=BACAGSGT)

OG 画像は X / Slack / Discord でリンクが踏まれたときのカードに使うやつで、favicon はブラウザのタブにそのまま乗る。本体アプリ・OG カード・favicon が全部同じ世界観で揃って、ここも同じ URL ハンドオフで Claude Code が実装まで通してくれた。

できあがったものは [Cloudflare Workers + Static Assets](https://developers.cloudflare.com/workers/static-assets/) に乗せて公開している。Workers は静的アセットを 1 オリジンから配れる仕組みなので、追加の CDN 設定なしで OG 画像も `/zipcodes.json` も同じドメインから配れる。独自ドメインを取らず、`https://yubin-gacha.citron24ah.workers.dev/` のままで月額 0 円運用中。

# 失敗談

## 【事件1】Claude Code、絵コンテを読み違えてくる

URL を渡して Claude Code が実装してくれたものを、ブラウザで動作確認したらなんかイメージと違う。広い画面では数字タイルも STOP ボタンも真ん中に小さく並んでいて、スカスカで貧相な感じになっていた。

![絵コンテ読み違え後 / before：実装直後のデスクトップ画面。数字タイルも STOP ボタンも真ん中に小さく、周りはスカスカ](https://static.zenn.studio/user-upload/deployed-images/1d267e04a42f0b8c08dc9928.jpg?sha=2fe90d173278cb4be5947ab4e0e77259639ca7ef)

絵コンテを見返してみると、**モバイル 390×844 とデスクトップ 1200×820 の 2 通りが明確に描かれている**。数字タイルも 38px と 90px でサイズが違うし、結果画面もデスクトップは 2 カラムグリッドになっていた。

どうやら Claude Code は、絵コンテの 2 段構成を「モバイル絵コンテ + デスクトップは参考画像」みたいな解釈をしてしまっていたらしい。モバイル寸法のコンポーネントをそのまま desktop でも使い回してきた、という感じ。**ハンドオフされた絵コンテの情報量を全部は読み取り切れなかった**、というやつ。

そこで Claude Code に絵コンテをもう一度見直してもらって、「mobile と desktop は別レイアウトで、それぞれの寸法に合わせて実装し直して」と伝え直したら、ビューポート幅で分岐して別サイズを渡すレスポンシブ実装にしてくれた。

![レスポンシブ対応後 / after（デスクトップ幅 1200px）：数字タイルが大きく、ポストやはがきの装飾も画面全体に広がっている](https://static.zenn.studio/user-upload/deployed-images/829bb04f3838f0166515d571.png?sha=d0d41e91a1bd15514bf42293d87fca20da1862be)

修正後がこれ。数字タイルが 90px に拡大され、左右のポスト・雲・飛ぶはがきが画面全体に広がって、絵コンテ通りの「POP な空」の世界観になった。

## 【事件2】緯度経度の突合キーで join 率 81% から動かない

距離計算用に Geolonia の `japanese-addresses-v2` から市区町村単位の lat/lng を取ってきて、KEN\_ALL の住所と join する処理を書いた。最初は **「都道府県 + 市区町村」 のキーで突き合わせたら 81% しかヒットしなかった**。

データソース側のスキーマを見直してみると、市区町村が単一フィールドではなく **「郡」と「区」が別フィールド** に分かれていた。例えば北海道の郡部は `county` が別フィールドに入っているし、政令指定都市の区も `ward` という別フィールドになっていたりする。最初のキーは郡や区の情報を捨ててしまっていたので、住所の表記揺れと衝突して取りこぼしていた、というやつ。

連結したキーで突き合わせ直したら、**join 率が 99.98%** にまで上がった（124,508 件中、未マッチは離島等の 20 件）。データソースのスキーマを最初にちゃんと読み切れていなかったというシンプルな話やった。

# まとめ：デザイン力に圧倒された — バックエンド先行 × Claude Design × Claude Code が強い

Claude Design の一番強かったところは、**トンマナの一貫性**。

今回のハンドオフバンドルには少なくとも以下が一気に揃ってきた:

* モバイル版の絵コンテ 3 画面（ガチャ中 / 全桁確定 / 結果）
* デスクトップ版の絵コンテ 3 画面（同上、2 カラム結果）
* `variants/pop.jsx` / `pop-desktop.jsx` として実装可能な React コード
* 色パレット 7 色（sky / red / yellow / green / blue / pink / cream）
* フォント指定（Yusei Magic / Kosugi Maru）
* OG 画像（1200×630 PNG）
* favicon（64×64 SVG）

全部同じ世界観でまとまっている。デザインシステムを事前に作らず、参考画像を 1 枚渡してブランドの方向を伝えただけで、ここまで揃うのは素直にすごい。個人開発でブランドやりきるのって結構手が回らないので、**1 日で世界観が立つ**のは革命的だった。

一方で今回効いたワークフローはこれ:

1. **仕様書先行** — SPEC.md を Single Source of Truth にして、機能要件・データ仕様・画面遷移を先に固める
2. **バックエンド完成 → 暫定 UI** — 雑でいいので「動く」状態まで作る。デザインが後から差し込めるように、コンポーネント分割だけは意識しておく
3. **Claude Design にビジュアルだけ依頼** — コードベースごと渡すと既存のコンポーネント構成を踏襲してくれる
4. **URL 1 本で Claude Code に手渡し** — 実装は Claude Code に全面委任。ハンドオフ README が指示を書いてくれる
5. **絵コンテの情報量を全部読む** — モバイルとデスクトップで異なる絵コンテが描かれていることを見落とさない（今回の反省）

次に何か作るなら、逆に**フロントエンドから先に作る**流れでも試してみたい。Claude Design で先に世界観を立てて、それに合う API / データ仕様を SPEC.md に落として、Claude Code でバックエンドを組む、というルート。ビジュアルから逆算する発想は、個人開発だと特に効きそう。

**URL を渡すだけで Claude Design → Claude Code に情報が流れる**。エージェント同士が URL ひとつで手渡しされる時代が、もう普通の個人開発ワークフローに入ってきている。
