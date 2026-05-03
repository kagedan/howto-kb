---
id: "2026-05-02-smartnewsクローンを作るはずがapple-intelligenceで動く月額0の広告ゼロトレ-01"
title: "SmartNewsクローンを作るはずが、Apple Intelligenceで動く月額$0の広告ゼロ・トレンドリーダーになった"
url: "https://zenn.dev/sawasige/articles/seekthea-development-story"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Python", "JavaScript", "zenn"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

**[Seekthea](https://apps.apple.com/app/id6762122200)** は、ニュース・ソーシャル・テックのトレンドを広告やポップアップなしでクリーンに読める iPhone / iPad / Mac / Vision Pro 対応のリーダーアプリです。アプリ自体の詳しい紹介は **[Apple Intelligenceで動く無料ニュースアプリを作った話（note）](https://note.com/sawasige/n/nac022819e97b)** をどうぞ。

この記事は、その Seekthea が「SmartNewsみたいなアプリを自分で作りたい」という最初の構想から、Claude（AI）との壁打ちを通じて二転三転し、まったく別のコンセプトに辿り着くまでの **設計プロセスの記録** です。失敗や方向転換も含めてリアルなままに。

## こんな人に刺さるかも

* **個人開発で iOS アプリを作っている／作りたい人** — サーバーレスでどこまで出来るかの一例として
* **Apple Intelligence（Foundation Models）に興味がある人** — 要約・カテゴリ分類で実際に使ってみての所感を交えて
* **AI と壁打ちしながら設計を進める人** — 壁打ちが設計をどう動かすか、AI の出力を信じすぎる落とし穴の話も
* **サーバー運用や月額課金を避けたい人** — $7〜10 想定が $0 に着地するまで
* **ニュース / RSS まわりのアプリを作りたい人** — FeedKit、Google News RSS、Readability.js の組み合わせ

---

## 1. 最初の構想：「SmartNewsクローンを作ろう」

最初に考えたのはシンプルな **ニュースアグリゲーター**。

* **プラットフォーム**: iOS（SwiftUI）
* **ニュース取得**: Webスクレイピング
* **機能**: カテゴリ分類 + AI要約

Claudeに相談したところ、提案されたのは **Python Backend（FastAPI）+ iOS Frontend** の2層構成。BeautifulSoupでスクレイピング、Claude APIで要約、PostgreSQLにデータ保存、REST APIでiOSアプリに配信。

**見積もりコスト: 月額 $7〜10**（Railway $5 + Claude API $2〜5 = $7〜10）

「ちゃんとしたサービス」を作る構成としては王道。サーバーがあること自体に不満はないけど、なくて済むならその方がいいな、くらいの感覚はあった。

---

## 2. 転換点①：「サーバーなしでできない？」

ここで最初の方向転換。

> 「サーバーをほとんど使わないで、iOSアプリだけで実現できないかな？」

この発想が全体の設計を大きく変えた。答えは **RSSフィード** だった。

Webスクレイピングはオンデバイスでもできなくはないけど、JavaScriptレンダリング・アンチボット対策・セレクタ保守を考えるとサーバーでやる方が現実的。一方 RSS なら iOS アプリ内で直接パースして終わり。FeedKit という Swift ライブラリを使えばいい。

**構成の変化:**

```
Before: [Sites] → Python Scraper → DB → REST API → iOS
After:  [RSS]  → FeedKit (iOS内) → SwiftData → SwiftUI
```

Backend丸ごと削除。これは大きい。

---

## 3. 転換点②：AIのAPIは従量課金が嫌 → Apple Intelligence

サーバーを消したのはいいけど、AI要約のために結局 Claude API を呼ぶ必要がある。

引っかかったのは料金体系。AI の API は従量課金で、ユーザーが増えるほど月額が読めなくなる。個人開発だと、これがそこそこのストレス。

ただ、このアプリで AI に頼みたいのは **要約とカテゴリ分類** くらい。重い推論をさせるわけじゃないなら、Apple Intelligence でも行けそうな予感がした。

> 「要約とカテゴリ分類くらいなら Apple Intelligence 使える？」

**使えた。しかも完全無料で。**

iOS 26 の Foundation Models フレームワークを使えば、要約もカテゴリ分類もオンデバイスで完結する。ネットワーク不要、コストゼロ、ついでに「API キーをアプリに持たせるセキュリティリスク」からも解放される。

**月額コスト: $7〜10 → $0**

---

プリセットのRSSを手動で管理するのは面倒。新しいサイトを自動で見つけられないか？

> 「たとえばGoogleで検索してトレンドのRSSサイトを抽出できない？」

Google検索を直接叩くのはTOS違反。でも **Google News自体がRSSフィードを公開していた**（2026年時点。Google News の URL 仕様は変わることがあります）。

* `https://news.google.com/rss?hl=ja&gl=JP` — 日本のトップニュース
* カテゴリ別、キーワード別のフィードもある

Google News RSSの各記事は **異なるソースサイトの記事** なので、パースするだけで日本中のニュースサイトが自動的に見つかる。登録済みのソースはスキップ、出現頻度が高い未知のサイトにはRSS自動検出をかけて、ユーザーに「追加しますか？」と提案。

**Googleが勝手にトレンドのソースを集めてくれるエンジン** になった。

---

ニュースの発見が自動化できたところで、ふと考えた。

> 「ニュースしか見れないのかな？Twitterとかのトレンドを追えるとさらに良いけど。」

調べてみると、RSSの守備範囲は想像以上に広かった。

| ソース | RSS | コスト |
| --- | --- | --- |
| Reddit | ◎ `/r/subreddit/.rss` | 無料 |
| はてなブックマーク | ◎ `hotentry.rss` | 無料 |
| Hacker News | ◎ `hnrss.org` | 無料 |
| Zenn, Qiita | ◎ `/feed` | 無料 |
| Bluesky | △ 非公式エンドポイント / AT Protocol 経由 | 無料 |
| X (Twitter) | ✗ Basic 以上の API（$200+/mo） | 高すぎ |

X以外は全部RSSで取れる。FeedKitの仕組みをそのまま使える。

**「ニュースアグリゲーター」から「トレンドアグリゲーター」** に進化。

---

RSSベースの設計が固まったところで、現実に気づいた。

> 「RSSだと内容が薄すぎるね。」

RSSのdescriptionはタイトルと1〜2行の要約だけ。画像もないことが多い。OGP（LPMetadataProvider）で画像は補完できる、Readability.jsで本文も抽出できる——でも根本的な問題はそこじゃなかった。

> 「要約が見たいんじゃないんだよ。記事が見たいの。」

**ここでアプリの本質が変わった。**

求めていたのは「AIが要約してくれるアプリ」ではなく、**「いろんなサイトの記事を、ゴミを全部取り除いて、きれいに読める場所」** だった。

Cookie同意バナー、利用規約ポップアップ、広告オーバーレイ——実際のWebは記事に辿り着くまでの障壁が多すぎる。

**解決策: WKWebView + Readability.js**

Safariのリーダーモードと同じ原理で、HTMLから記事本文だけをクリーンに抽出する。

```
記事発見（RSS / Google News）
    ↓
WKWebView + Readability.js で本文抽出
    ↓
クリーンな記事ビュー  ← ここがメインの体験
    ↓
AI要約はカード一覧でのサポート役
```

こうして「ニュース・アグリゲーター」→「トレンド・アグリゲーター」→ **「トレンド・リーダー」** と着地した。

---

プリセットRSSの品質をチェックする段階で、予想外のトラブル。

Claudeに「RSSフィードの中身（画像有無、description充実度）を確認して」と頼んだら、一覧表を作ってくれた。GIGAZINEは「◎ enclosure + img in desc」——画像フィールドが充実しているらしい。

実際にフィードを取得して確認したら、**画像フィールドは一切なかった**。

> 「GIGAZINEは『enclosureあり』と書いていましたが嘘でした。」

AIが「確認しました」と言っても、実際にはデータを取得できていない（あるいは取得結果を見ずに答えている）ケースがある。当時の AI セッションが Web 取得ツールを持っていなかったのか、持っていたが使わなかったのか、原因は外からはわからない。

**教訓: AIの「確認結果」を鵜呑みにしない。** 特にデータ検証は自分の手で。

---

## 最終形：Seektheaの全体像

紆余曲折を経て辿り着いた設計：

```
[RSS + Google News] → 記事URL発見
        ↓
[WKWebView + Readability.js] → クリーンな本文抽出
        ↓
[LPMetadataProvider] → OGP画像・favicon補完
        ↓
[Apple Intelligence] → 要約・カテゴリ分類（サポート役）
        ↓
[SwiftData + CloudKit] → ローカル保存＆全デバイス同期
        ↓
[SwiftUI] → iPhone / iPad でクリーンに読む
```

### 初期構想との比較

| 項目 | 最初の構想 | 最終形 |
| --- | --- | --- |
| 名前 | NewsAgg | **Seekthea** |
| コンセプト | ニュースアグリゲーター | **トレンドリーダー** |
| ソース | ニュースサイトのみ | ニュース + ソーシャル + テック |
| 取得方法 | Webスクレイピング | **RSS + WKWebView/Readability.js** |
| AI | Claude API（サーバー側） | **Apple Intelligence（オンデバイス）** |
| Backend | Python + FastAPI + PostgreSQL | **不要** |
| ホスティング | Railway | **不要** |
| DB | PostgreSQL | **SwiftData + CloudKit** |
| 対応デバイス | iPhoneのみ | **iPhone + iPad** |
| 月額コスト | $7〜10 | **$0** |
| APIキー | 必要 | **不要** |
| メイン体験 | AI要約を読む | **記事をクリーンに読む** |

### 採用した技術スタック

| 役割 | 技術 |
| --- | --- |
| 記事ソース | RSS / Google News RSS |
| RSS パース | FeedKit |
| 本文抽出 | WKWebView + Readability.js |
| 画像・メタデータ補完 | LPMetadataProvider |
| AI（要約・カテゴリ分類） | Apple Intelligence (Foundation Models) |
| 永続化・同期 | SwiftData + CloudKit |
| UI | SwiftUI |
| Backend | なし |

---

## まとめ：設計は会話で進化する

最初の「SmartNewsクローン」から最終形まで、5つの大きな転換があった。

1. **サーバーあり → サーバーレス**（RSSの発見）
2. **Claude API → Apple Intelligence**（コストゼロ＆APIキー不要）
3. **手動ソース管理 → Google News自動発見**
4. **ニュース専用 → マルチソース・トレンド**（スコープ拡大）
5. **AI要約がメイン → 記事を読むのがメイン**（コンセプト転換）

どれも「こうしたい」ではなく「これじゃダメだ」から生まれた方向転換。特に最後の「要約が見たいんじゃない、記事が見たいんだ」は、自分でも言語化するまで気づいていなかった本質的な欲求だった。

AIとの壁打ちで設計を進める利点は、こういう「自分でも気づいていないこと」が対話の中で浮かび上がってくること。ただし、AIの出力を検証なしに信じると痛い目を見る（RSSの画像フィールド詐称事件）。

気が向いたら、次は Apple Intelligence について書こうかなと思っています。

---

## Seekthea について

Seek（探し求める）+ Thea（θέα：ギリシャ神話の視覚の女神）。

📱 **[App Store からダウンロード](https://apps.apple.com/app/id6762122200)**  
🌐 **[ランディングページ](https://sawasige.github.io/seekthea/)**  
📝 **[Apple Intelligenceで動く無料ニュースアプリを作った話（note）](https://note.com/sawasige/n/nac022819e97b)**
