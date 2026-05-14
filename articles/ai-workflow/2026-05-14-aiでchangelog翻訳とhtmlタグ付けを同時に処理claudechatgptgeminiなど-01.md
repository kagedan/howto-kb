---
id: "2026-05-14-aiでchangelog翻訳とhtmlタグ付けを同時に処理claudechatgptgeminiなど-01"
title: "AIでChangeLog翻訳とHTMLタグ付けを同時に処理：Claude・ChatGPT・Geminiなど7サービス精度比較"
url: "https://qiita.com/Reng/items/cbf8d8632f86242c6b6e"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "Gemini", "GPT", "qiita"]
date_published: "2026-05-14"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

# AIでChangeLog翻訳とHTMLタグ付けを同時に処理：Claude・ChatGPT・Geminiなど7サービス精度比較

__前文__
「そうだ、AIを使ったらHTMLタグ付けも和訳もいっぺんに出来るんじゃ…？！」と今更ながら気づいた。**Claude・ChatGPT・Gemini・Copilot・Grok・DeepSeek・Perplexity**の7サービスを使ってみた検証結果の記録。

✅ 実際に使ったプロンプトも公開 
✅ それぞれのAIサービスのアイコン画像付き ↔︎ 親切・分かりやすさ

📅 検証日：2026/05/07

:::note
__ページ内リンクas 目次__
- [用語・略語や前提](#用語略語や前提)
- [まず結果を言うと](#まず結果を言うと)
- [背景と動機・作業フロー比較](#背景と動機作業フロー比較)
- [検証内容・プロンプト](#検証内容プロンプト)
  - [プロンプト①：txt → HTMLタグ付き整形（En版・Ja版）](#プロンプトtxt--htmlタグ付き整形en版ja版)
  - [プロンプト②：PDF → HTMLタグ付き整形＋翻訳（En版・Ja版）](#プロンプトPDF--HTMLタグ付き整形翻訳En版Ja版)
- [検証結果（表）](#検証結果表)
  - [AIサービス別 評価（txtから）](#aiサービス別-評価txtから)
  - [AIサービス別 評価（PDFから）](#aiサービス別-評価pdfから)
- [各AIの傾向と実感](#各AIの傾向と実感)
- [参考データ](#参考データ)
- [スクリーンショット・画像素材](#スクリーンショット・画像素材)
  - [Release Notes 原本スクショ](#release-notes-原本スクショ)
  - [合成済み ReleaseNotes 画像](#合成済み-releasenotes-画像)
  - [pdf化前の調整済み画像](#pdf化前の調整済み画像)
- [総括](#総括)
:::

---

## 用語・略語や前提
この記事における用語や略語や前提をはじめに記しておきます。

__用語・略語について__
- **ChangeLog**：アプリやソフトウェアのアップデート内容をまとめたリリースノート。今回の検証で使ったのは英文しかない・文章としてコピペ出来ない仕様（ずばり「**Guitar Pro 8**」のリリースノートです）
- **ScnSht**：スクリーンショットの略
- **cap**：キャプチャーの略、スクリーンショットとほぼ同じ意味
- **Fire Alpaca**：無料の画像編集ソフト( Win / Mac / Linux )。レイヤー機能でスクロールが必要なScnSht画を1枚の縦長画像に合成するために使用
- **プレビュー.app**：MacOS標準画像編集ソフト/アプリ。トリミング（Crop,上下左右の余白=辺を削ること）やPDF書き出しに使用
- **En版 / Ja版**：英語版 / 日本語版の略

::: note
前提
- **パーソナライズ設定**：各AIサービスは事前に同じパーソナライズ設定済みの状態　※ただしCopilot、DeepSeekは除く 
  - AIサービスによって名称や（パーソナライズ、カスタム指示etc）設定する場所までの行き方などは異なるが、本記事では同じことを指しているものとする
- **AIモデル**：各AIサービスはどれも無料プランで初期表示のAIモデル。すなわち2026年5月上旬現在で
  - Gemini〈Gemini 3 Flash〉`高速モード`
  - Claude〈Sonnet 4.6〉
  - ChatGPT〈GPT-5.5〉...の多分Instant
    - ※GPT-5.5 Instant(2026年5月)、 GPT-5.3 Instant(2026年3月)
  - Copilot〈総合的*〉`Smart`モード
  - Grock〈Grock*〉`速い`モード
  - DeepSeeek〈DeepSeek-V3〉
  - Perplexity〈初期値*〉
  ※書式「各AIサービス〈AIモデル名〉」、モデルが特にない総合的なやつや初期値のやつは｢*｣付き
- **AIボット**：今回は検証の対象外。色々なAI系サービス/オールインワン系のAIサービスで作成できたりする機能。
  - <font color=darkgray>限定的な「できる事」をカスタムして作ることができる。これを使えば毎回プロンプト入力せず、そのAIボットで作業させることができる。特定のタスクに先鋭化・最適化された専用ツールを自作するようなもの</font>
  - <font color=darkgray>オールインワン系のAIサービスでは機能を使うと**クレジット消費しがち**。上記に挙げたAIサービスではクレジット消費とかないから（無料プランでできる処理のうち）</font>

- **Webサイト版**：パソコンで使用、スマホでのアプリ版ではない
- **プロンプト文の文章違いver**：同じ指示文の意味になる（はずの）違う文章、は試してない
:::

:::note
前提 補足
パーソナライズ設定する場所についてのQiita記事を別途作った
→ ref) [パーソナライズ設定の場所と項目名：Gemini・Claude・ChatGPT・Copilot・Grok・DeepSeek・Perplexity 7つのAIサービス](https://qiita.com/Reng/items/54bc250db36ed3e80921)

※__パーソナライズ設定以外にも__ 回答スタイルをselectから選んでカスタムできる場合はしてる(ChatGPT, Claudeなど）

※__メモリの記憶__：ON （トグルでON/OFF設定できる)

※__Perplexity は__ “検索”を中心にした ｢AI搭載検索エンジン｣ 寄りで(中略)「検索＋情報整理＋引用の設計」と言うのが最も実態に近い。らしい。
→ ref) [ChatGPT ｢Perplexityと他AIの違い｣](https://chatgpt.com/share/6a031d4a-1ae0-8321-9bb9-2324d2794aff)より
:::

　
## まず結果を言うと

- 望んだ通りの整形結果が出たのは**ClaudeとCopilotのみ**
- 他の5サービスはtxtからにしろPDFからにしろ、整形結果は同じようにNG
- 英単語の綴りミスを自動修正したのは**ClaudeとDeepSeekのみ**

:::note warn
結果からの気づき

✔︎ 今回のお題＆検証では __Claude__ が最良の結果という事に

✔︎ __Copilot__ はAIモデルにChatGPTも活用した独自チューニングのAIモデル(AIエンジン)とのことだが、その通り __ChatGPT とは違う結果__ になったとことが伺える
:::

　
## 背景と動機・作業フロー比較

使っているソフト/アプリのChangeLogを、英語のまま＆日本語訳の両方をブログ記事に載せている。この作業がそれなりに手間だった。AI使うと工程と作業量を減らせる。

| | 今まで | これから |
|---|---|---|
| ステップ数 | 6ステップ | 5ステップ |
| txtファイルの手動編集 | En版・Ja版それぞれ必要 | 不要 |
| HTMLタグ付け | 手動 | AIが一括 |
| 翻訳 | DeepLデスクトップ版 → 手動整形 | AIが一括 |

ただし希望通りの整形結果を出せたのは先に言及した通りClaudeのみ。

__🌀 今まで（6ステップ）__

1. **Fire Alpaca** で合成：ScnShtを撮ってレイヤーにして1枚の縦長画像に合成する編集
2. **DeepLデスクトップ版**：英文を *範囲選択のキャプチャで取り込み ＆和訳* まで一気（文字列の範囲選択ではなく画像をScnShtする要領）
   - <font color=seagreen>ただし **改行がまったくされてない状態** のため（読みずらっ）、改行・空白行を手動で整える必要あり ※1</font>
3. DeepL：英文をtxtで保存、和訳をtxtで保存
4. text系Editor：En版にHTMLタグ付け、タグ付きtxtとして保存
   - <font color=seagreen>手作業で体裁を整える ※2 ※3</font>
5. text系Editor：Ja版にHTMLタグ付け、タグ付きtxtとして保存
   - <font color=seagreen>手作業で体裁を整える ※2 ※3</font>
6. 記事化：ブログ本文の該当箇所にEn版とJa版をそれぞれコピペ

:::note
✔︎ これだって実は、手順2 のDeepLデスクトップ版の恩恵により、以前やってたやり方より断然作業量が減ってはいる（入力欄に貼り付け＆和訳まではショートカット使って1アクション）。以前は **英文をタイピングして書き起こすという作業**をしてからDeepLに突っ込んでいた。
:::

　
__🌀これから（5ステップ）__

1. **Fire Alpaca** で合成：ScnShtを撮ってレイヤーにして1枚の縦長画像に合成する編集
2. **プレビュー.app** でトリミングなど調整してPDF化（En版）<font color=seagreen>※4</font>
3. PDFをAIに読み込ませてEn版とJa版それぞれHTMLタグ付けを一気に
4. 結果をDLかコピペしてEn版・Ja版をtxtとして保存
5. 記事化：ブログ本文の該当箇所にEn版とJa版をそれぞれコピペ

...お分かりいただけただろうか...？

単に6ステップ→5ステップと、1ステップ減ったのではなく、手順3〜5で**txtファイルを自分で編集・用意する工程がまるごとなくなる** わけだ。 

➡︎ 作業量も時間も大幅に減る。

---
<font color=darkgray>註
※1）**DeepLデスクトップ版**での取り込み＆和訳は一息に済むが、改行が一切されない状態になる。改行・空白行を手動で入れる編集が必要。</font>

<font color=darkgray>※2）ブログ記事の改行設定との兼ね合いで、txt的改行とHTML的改行が混在した状態が必要になる。</font>

<font color=darkgray>※3）対象のタグは `<h4>`・`<h5>`・`<ul>`・`<li>` のみ。改行や空白の位置も含めて手動で整える必要がある。</font>

<font color=darkgray>※4）**プレビュー.app**でPDF化する方法は2通りある：
　`ファイル › プリントする...` `⌘+P`
　`ファイル › PDFとして書き出す...` `⌘+P`
PDF化後の文字の大きさ（見え方）が両者で異なる、上下左右の余白の多さが違うため。両方試して字が大きい方（＝余白が少ない方）を使った。</font>


:::note warn 
**Fire Alpaca**での画像編集は自動化できていない
ScnShtを撮ってレイヤーにして×必要枚数分、ずらして全文が見える縦長画像に合成、不要部分の削除と位置微調整……という手間は今も変わらず残っている。ここも自動化できれば理想的なのだが、今回の “AI活用による作業量激減しようぜ” 検証の範囲外。
:::

　
## 検証内容・プロンプト

最初は単に **txt → HTMLタグ付き化** をしてもらえばいいじゃーん、と思いついたので、txtからHTMLタグ付き化を実践した。

『！ …英文PDF状態から読み取ってもらえばいいんじゃん？？！！』と気づいたのは そのあとのこと。

__プロンプト①、プロンプト② について共通__
※ 実際は各AIのプロンプト内では &lt;/h4&gt;や&lt;li&gt; はそのまま書いたが、このQiita記事 引用ブロック上でそれをやるとhtmlタグとして効いてしまうので`</h4>`や`<li>`のインラインコードで書いている

※ 'Release Note' は正確には 'Release Notes' なのだが、検証結果に影響はなかった模様

　
### プロンプト①：txt → HTMLタグ付き整形（En版・Ja版）

txtファイルを渡して英語版・日本語版それぞれHTMLタグ付きで整形させる。タグの構造・改行ルール・冒頭3行の扱いまで細かく指定することで、コピペしてすぐ使える状態を目指している。

__プロンプト①：txt → HTMLタグ付き整形（En版・Ja版）__
>添付したtextベースの英語または日本語のChangeLogに html の h4見出しと ul と li のタグをつけてください。その際`</h4>`の次に改行なしで`<ul>`、`<li>`と`</li>`を1行とし`</ul>`後は1行空白をあけて`<h4>`とする事。
h4、(必要に応じて h5)、 ul、li（行頭の「-」や「• 」を削除して li タグに整形）のタグを付けhtml整形してください。
>
>添付したtextベースの冒頭3行ほどの扱いについて。原則プレーンな状態のままこの変換に加える。もし、"【"〜"】"で囲われた箇所があればその分は削除する。もし、"Release Note"後に改行でバージョン番号（例 8.1.x などの書式）がある場合は"Release Note"後に半角スペースでバージョン番号を配置。バージョン番号の後に1行空白をあけて、上記で指示したhtmlタグを付けてください。
>


### プロンプト②：PDF → HTMLタグ付き整形＋翻訳（En版・Ja版）

PDFを直接渡してタグ付き整形と和訳を一発でこなさせる。内容としてはプロンプト①の指示に加え、<font color=darkseagreen>英語版・日本語版の両方を同時に出力</font>するよう言ってる。

__プロンプト②：PDF → HTMLタグ付き整形＋翻訳（En版・Ja版）__
> <font color="darkseagreen">添付したpdfのChangelog文書を html の h4見出しと ul と li のタグをつけたtxtに整形するお仕事です。英語のままと日本語版が必要です。</font>pdfの冒頭3行ほどの本文（リスト）が始まる前の部分の扱いについて：原則プレーンな状態のまま変換し、"Release Notes" 後のバージョン番号（例 8.1.x などの書式）は "Release Notes" 後に半角スペースでVer番号を配置。Ver番号の後に1行空白をあけ、h4見出しとulを付けていってください。 その際`</h4>`の次に改行なしで`<ul>`、`<li>`と`</li>`を1行とし`</ul>`後は1行空白をあけて`<h4>`とする事。全体として、h4、(必要に応じて h5)、 ul、li（行頭の「-」または「• 」を削除して li タグに整形）のタグを付けhtml整形したtxtにしてください。
> では、上記で指示の通りタグ付け・整形したtxtを英語版と日本語版で用意してください。

　
## 検証結果（表）
txtからにしてもpdfからにしても違いはなかった。記事冒頭でも書いた通り
- 望んだ通りの整形結果が出たのは**ClaudeとCopilotのみ**

ということ。つまり各AIサービスの結果は
**txt → HTMLタグ付き整形（En版・Ja版）** にしろ、
**PDF → HTMLタグ付き整形＋翻訳（En版・Ja版）** にしろ、
総合して4段階評価｢★｣マークではこう：

|　　<!-- 全角sapace x2 -->| AIサービス | 評価 |
|---|---|---|
| ![gemini_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/b6c96acd-9257-406f-a76c-e5b70a06856e.png)| Gemini | ☆☆☆☆ | 
|![Claude_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/a1ed3b12-185e-4e0c-815d-8a5c11f334a3.png) | Claude | ★★★★ | 
|![gpt_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/19be4f1c-2cb1-4a51-837f-3ae7218ba718.png)| ChatGPT | ★☆☆☆ | 
|![copilot_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/83390f38-6d13-4a8a-9939-4d5b5331fd1b.png)| Copilot | ★★★☆ |
|![Grock_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/c74faf35-6947-4613-a0a7-9eb4e2c755dc.png)| Grok | ★☆☆☆ | 
|![DeepSeeek_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/ce1a1c93-b6f0-4247-aca1-cb1ee0eca026.png)| DeepSeek | ★☆☆☆ | 
|![Perplexity_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/cc3cff57-6f48-4d20-990a-e54385650ad5.png)| Perplexity | ★☆☆☆ |

これがすべてなのだけど、txtからのときとpdfからのときのそれぞれの評価をもう少し分かりやすく備考付きにしたものが「AIサービス別 評価（txtから）」と「AIサービス別 評価（PDFから）」の下記セクション。

### AIサービス別 評価（txtから）
4段階評価で｢★｣マークと、備考。
|　　<!-- 全角sapace x2 -->| AIサービス | 評価 | 備考 |
|---|---|---|---|
| ![gemini_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/b6c96acd-9257-406f-a76c-e5b70a06856e.png)| Gemini | ☆☆☆☆ | 残念な結果、甚だ遺憾。txtやコードブロックじゃなくて大NG |
|![Claude_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/a1ed3b12-185e-4e0c-815d-8a5c11f334a3.png) | Claude | ★★★★ | 速い、望み通り。綴りミス修正まで《誤 "redudant" → 正 "redundant"》 |
|![gpt_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/19be4f1c-2cb1-4a51-837f-3ae7218ba718.png)| ChatGPT | ★☆☆☆ | 惜しい、改行位置がNG |
|![copilot_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/83390f38-6d13-4a8a-9939-4d5b5331fd1b.png)| Copilot | ★★★☆ | 望み通り、ただし整形結果を出す前の冒頭文が不要、綴りミス修正まで《誤 "redudant" → 正 "redundant"》 |
|![Grock_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/c74faf35-6947-4613-a0a7-9eb4e2c755dc.png)| Grok | ★☆☆☆ | 冒頭3行の扱いがNG：不要なタグ付け＆指示通りじゃない |
|![DeepSeeek_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/ce1a1c93-b6f0-4247-aca1-cb1ee0eca026.png)| DeepSeek | ★☆☆☆ | 整形がEn+Ja統合になっててNG。冒頭3行の扱いがNG。タグ付け・改行が指示通りじゃない |
|![Perplexity_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/cc3cff57-6f48-4d20-990a-e54385650ad5.png)| Perplexity | ★☆☆☆ | 遅い、整形結果が本文にない（展開しないと見えない）。タグ付け・改行が指示通りじゃない |


　
### AIサービス別 評価（PDFから）
4段階評価で｢★｣マークと、備考。

|　　<!-- 全角sapace x2 -->| AIサービス| 評価 | PDFからの結果 |
|---|---|---|---|
|![gemini_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/b6c96acd-9257-406f-a76c-e5b70a06856e.png)| Gemini | ☆☆☆☆| txtからと同等（NG） |
|![Claude_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/a1ed3b12-185e-4e0c-815d-8a5c11f334a3.png)| Claude | ★★★★| txtよりは時間かかった。本文中ではなく**アーティファクトとして**出力された。綴りミス修正まで《誤 "redudant" → 正 "redundant"》 |
|![gpt_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/19be4f1c-2cb1-4a51-837f-3ae7218ba718.png)| ChatGPT | ★☆☆☆ | 速め、txtからと同等の結果（NG） |
|![copilot_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/83390f38-6d13-4a8a-9939-4d5b5331fd1b.png)| Copilot | ★★★☆ | 速め、txtからと同等の結果（OK）、綴りミス修正まで《誤 "redudant" → 正 "redundant"》 |
|![Grock_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/c74faf35-6947-4613-a0a7-9eb4e2c755dc.png)| Grok | ー| =未検証= <font color=darkgray>⚠️</font>|
|![DeepSeeek_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/ce1a1c93-b6f0-4247-aca1-cb1ee0eca026.png)| DeepSeek | ★☆☆☆ | PDFアップロードにやや時間がかかった。処理は速い。En・Ja別にはなったが他はtxtからと同等（NG） |
|![Perplexity_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/cc3cff57-6f48-4d20-990a-e54385650ad5.png)| Perplexity | ★☆☆☆ | txtからと同等の結果（NG） |


<font color=darkgray> *※⚠️：Grockの未検証については、まぁまぁ真夜中にやってたのにも関わらず｢アクセスが集中しています｣と、応答してもらえなかったため*</font>

:::note 
**Claude**のPDFから版での**アーティファクトの件**

Claudeはtxtからの場合と違い、pdfからでは結果をアーティファクトとして出してきた。

もし、Promptで「本文中にtxtで表示」と指示していたら、（txtからの場合と同じように）本文中に記述したのかも。その場合、アーティファクト用意のレンダリング時間がかからず、速度も体感上もっと短く応答を終えたのかも。

比較検証として共通プロンプトを使うという趣旨のため、今回はPrompt内に「本文中にtxtで表示」と書いた場合までは検証していない。
:::

　
## 各AIの傾向と実感

7サービスを同じプロンプトで試して分かったのは、**指示の忠実度にかなり差がある**ということ。

::: note
全く同じプロンプト使ってるのにこの差！
:::

「タグ付けして」という大まかな指示はどのサービスもこなせる。ただ今回のように **AIが間違わないよう・分かりやすいよう、順を追って指示**、具体的には「`</h4>` の直後に改行なしで `<ul>`」「`</ul>` の後に1行空白」という **細部まで指示通りか** となると、望み通りのものを提出してきたのは **ClaudeとCopilot**の2つだけだった。

::: note
コードに強いという評がよくつきがちな**ChatGPT**も指示通り整形出来てない
:::

:::note warn
また、**Claude** と **DeepSeek** は英単語の綴りミス（"redudant" → "redundant"）を自動で修正していた。指示外である英単語の誤りにも気づいて直してくれるのは実用上ありがたい。
:::

PDFからの読み取り精度はtxtからの場合と大差ない結果で、PDFを経由することによる精度の劣化はほぼ感じないと言っていいと思われる（ファイルアップロードに多少時間かかったとこはある）。

和訳については、DeepLが「〜を修正しました」「〜ようになりました」句調なのに対し、今回どのAIサービスも「〜を修正」「〜ようになった」という語尾で、この点は個人的にはGood。語尾の句調に関してはDeepLで和訳してた時はわざわざこの語尾に修正してた位なので。

総じて、**細かい指定を含むタスクほど、AIサービスによる結果の差がある**という事に。汎用的な文章生成では差が見えにくくても、「これこれこのように」という指示（要件）が細かいほどその指示を守れるかどうかがハッキリする結果となった。

:::note
“読み取り能力”？ “Codeの出力能力”？
- プロンプト文の意向を正確に汲み取れるかの “読み取り能力”？
- 正確に出力を施せるかの　“Codeの出力能力”？
- またはその両方？
:::

　
## 参考データ

### チャットの自動命名比較

各AIサービスがどういう名前をつけるかも比べてみた。結構違う。<!--プロンプトの意図をどう解釈しているかが見える。-->個人的にはサイドバーの幅内に収まる文字数が好ましいんだが。
AIサービス名は共有リンクになっているので確かめたい方はどうぞ。

| | AIサービス | 自動命名されたチャット名 |
|---|---|---|
|![gemini_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/b6c96acd-9257-406f-a76c-e5b70a06856e.png) ☆☆☆☆|[Gemini](https://gemini.google.com/share/115444031d4a) | Changelog HTML Formatting Request|
| ![Claude_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/a1ed3b12-185e-4e0c-815d-8a5c11f334a3.png)★★★★ |[Claude](https://claude.ai/share/6d51d373-3225-4318-8d2a-ef05ee21202a) | テキストベースのChangeLogをHTML形式に変換|
| ![gpt_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/19be4f1c-2cb1-4a51-837f-3ae7218ba718.png)★☆☆☆|[ChatGPT](https://chatgpt.com/share/69fbdf97-cd00-8320-99c4-8fed7fdcd45f) | HTML整形の指示 |
|![copilot_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/83390f38-6d13-4a8a-9939-4d5b5331fd1b.png) ★★★☆|[Copilot](https://copilot.microsoft.com/shares/YHqoqHaK6swkr1PLb2xku) | ChangeLogのHTML整形依頼|
| ![Grock_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/c74faf35-6947-4613-a0a7-9eb4e2c755dc.png) ★☆☆☆|[Grok](https://grok.com/share/c2hhcmQtNA_f5754d24-1eda-490f-ac37-ef5a00192bc0) | ChangeLog HTML整形（日本語・英語版） |
| ![DeepSeeek_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/ce1a1c93-b6f0-4247-aca1-cb1ee0eca026.png) ★☆☆☆|[DeepSeek](https://chat.deepseek.com/share/qwqr3ep2jfob2bwivv) | HTMLタグ付け変更履歴 |
| ![Perplexity_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/cc3cff57-6f48-4d20-990a-e54385650ad5.png) ★☆☆☆|[Perplexity](https://www.perplexity.ai/search/3c1bc5f4-6063-4e86-a11c-af5e3258d86f) | =自動で短いタイトルはつかない= |





### プロンプト欄の表示挙動比較

プロンプトをコピペしたときの見え方と、送信後の（プロンプト欄の）表示の違いも各AIサービスによって異なる。
AIサービス名は共有リンクになっているので確かめたい方はどうぞ。

| 　 | AIサービス | コピペ後の表示 | 送信後のプロンプト文 |
|---|---|---|---|
| ![gemini_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/b6c96acd-9257-406f-a76c-e5b70a06856e.png)|[Gemini](https://gemini.google.com/share/115444031d4a)  | 改行・空白行：反映 | 全表示（☆：5行ほど＋グラデなし） |
| ![Claude_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/a1ed3b12-185e-4e0c-815d-8a5c11f334a3.png)|[Claude](https://claude.ai/share/6d51d373-3225-4318-8d2a-ef05ee21202a)  | 改行：反映 / 空白行：未反映 | 全表示（☆：8行ほど＋グラデ） |
| ![gpt_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/19be4f1c-2cb1-4a51-837f-3ae7218ba718.png)|[ChatGPT](https://chatgpt.com/share/69fbdf97-cd00-8320-99c4-8fed7fdcd45f) | 改行・空白行：反映 → 詰まった文章 | 全表示 |
| ![copilot_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/83390f38-6d13-4a8a-9939-4d5b5331fd1b.png)|[Copilot](https://copilot.microsoft.com/shares/YHqoqHaK6swkr1PLb2xku) | 改行・空白行：未反映 | 全表示 |
| ![Grock_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/c74faf35-6947-4613-a0a7-9eb4e2c755dc.png)|[Grok](https://grok.com/share/c2hhcmQtNA_f5754d24-1eda-490f-ac37-ef5a00192bc0)  | 改行・空白行：反映 → <font color=tomato>※⚠️</font> | 全表示 |
| ![Perplexity_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/cc3cff57-6f48-4d20-990a-e54385650ad5.png)|[Perplexity](https://www.perplexity.ai/search/3c1bc5f4-6063-4e86-a11c-af5e3258d86f)| 改行・空白行：未反映 → 詰まった文章 | 5行ほど表示＋グラデ |
|![DeepSeeek_icon_32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/ce1a1c93-b6f0-4247-aca1-cb1ee0eca026.png) |[DeepSeek](https://chat.deepseek.com/share/qwqr3ep2jfob2bwivv) | 改行・空白行：未反映 → 詰まった文章 | 全表示 |

※「☆」マーク：プロンプトの量が多ければ省スペース表示になる
<font color=tomato>※⚠️</font>：Grokはプロンプト内の `<h4>` や `<ul>` などのHTMLタグが“ブラウザとしての画面表示”に反映されてしまったらしく、意図しない空白が生じた<!---HTMLタグが表示に反映されて意図せぬ空白が発生-->



## スクリーンショット・画像素材

### Release Notes 原本スクショ

以前からアップデートのお知らせはあった。キャプチャと翻訳作業をしたのがこの時期というだけ。

![8-1-5_31_1.png ReleaseNotes原本スクショ](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/baeb53ed-593a-4811-852a-644d26a7d926.png)
*Release Notes 8.1.5-31*


### 合成済み ReleaseNotes 画像

スクロールしないと全文が見えないため、画像ソフトで1枚に合成したもの。

![①8-1-5_31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/e9a401bf-4654-47be-b9ae-3303893c98d8.png)
*ReleaseNotes 8.1.5-31 全文（画像ソフトで合成）*

:::note
今回はたまたまこの長さ＝文章量だっただけで、過去にはこの2倍以上だったり、もっと長かったこともある。
:::


### PDF化前の調整済み画像

プレビュー.appの「マークアップ」でトリミングした状態。これを元にPDF化。<font color=darkgray>
※綴りミス箇所は「Engraving」の最初の項目、「Fix a redudant 」部：
正）redu<font color=tomato>n</font>dant、誤)redudant</font>
![_pdf化_0_書き出し用.jpg PDF化前のトリミング済み画像](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/9fea2631-f056-4b53-904d-e43106bd0c53.jpeg)
*欄内のChangelog本文部のみにした状態*

　
__PDF化したもの__...、は無理、PDFはQiitaでファイルアップロードできない、対象外。
┌：：：：：：：：：：：：：：：：┐
：：：：：：：：：：：：：：：：：：
：：：：：：：：：：：：：：：：：：
：：：「PDF化前の調整済み画像」：：：
：：：：：：：：：：：：：：：：：：
：：：：：：：：の：：：：：：：：：
：：：：：：：：：：：：：：：：：：
：：：：：：上下左右に：：：：：：：
：：：：：：：：：：：：：：：：：：
：：：余白がついた状態のもの：：：：
：：：：：：：：：：：：：：：：：：
：：：：：：：：：：：：：：：：：：
：：：：：：：：：：：：：：：：：：
：：：：：：：：：：：：：：：：：：
└：：：：：：：：：：：：：：：：┘



:::note
※**プレビュー.app**でPDF化する方法は2通りある：
　`ファイル › プリントする...` `⌘+P`
　`ファイル › PDFとして書き出す...` `⌘+P`
PDF化後の文字の大きさ（見え方）が両者で異なる。両方試して字が大きい方（＝余白が少ない方）を使った。
:::

今回は使ったのは`PDFとして書き出す...`で作成したものの方、余白が少なく文字が大きかったから。
![_pdf余白比較_.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1024463/97f4d048-f0f6-42a8-ad44-9488a48cc43f.png)
<font color=darkgray>*pdf化: 余白比較 プレビュー.app 作成方法別*</font>



## 総括

作業の中核だった「**DeepL**で和訳 → 手動でタグ付け・整形 → txtで保存」の流れが、**PDFをAIに渡すだけ**で出来る。自分で用意・編集するtxtファイルがなくなるのが一番大きい。

**Fire Alpaca**での画像合成作業は引き続き残るわけだが、それ以外の工程は大幅に短縮！できることが分かった。

今回のこの件に限らずだが 個人的には、**世間的に生成AIの代名詞みたいに言われてるChatGPT**より**Claude**の方が良い結果になるという体感があり、今回ももれなくClaudeが優秀だったという話。

::: note
その他、**使い心地に関係する**あれやこれやとして

プロンプト文の文字数がある程度 多かったりしたときに
- 省スペース表示になるのかならないのか
- 送信済みプロンプト文の編集ができるのかできないか（枝分かれ、ブランチ）

や、
- **Copilot**はコピペでプロンプト埋めるならいいけどキーボード入力してたら変換や確定のつもりのリターン↩︎でまだ文章書き終わってないのに送信されてしまいがちで使いずらいナ！ 
- **Grok**や**DeepSeek**のページ右端にNotionで作ったWEBページのように目次を表す「ー」横線が並んでるの便利だな
- Grokは｢アクセスが集中しています｣と応答してもらえなえないことがままある感じだな
- **Perplexity**の背景色と文字色のコントラストちょっと見ずらいな（視認性が悪いな）

など、あと、行間や見出し文字の大きさ由来の、ぱっと見での把握のしやすさや読みやすさもあるので、そういったことも、どのAIサービスのページ・機能が満足いくか・使いやすいかに関わってくると思う。
:::

個人的には**Copilot**の 送信するつもりのないリターンで送信されてしまいがちな事や、「OK、〇〇」とか馴れ馴れしく呼び掛けられるのが本当にイヤなんだけど、
でも一方でCopilotの**実務面が強い**っぽいところやどこ開いてるかがスグ分かるページ色が**濃い紺色**（ダークモード時）なとこはアドバンテージなんだよなぁ。

---
以上です。
