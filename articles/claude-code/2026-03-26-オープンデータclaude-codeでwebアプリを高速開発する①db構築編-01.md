---
id: "2026-03-26-オープンデータclaude-codeでwebアプリを高速開発する①db構築編-01"
title: "オープンデータ×Claude Codeでwebアプリを高速開発する【①DB構築編】"
url: "https://zenn.dev/truestar/articles/8cc14b92f8c5d5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

# はじめに

お疲れ様です。本田です。  
先日は久しぶりにバスケットボールをやっていたのですが、楽しすぎて両脚を攣って退場しました。二日経ちましたがまだ違和感があります。

しかしそれでもシステム開発はできる！  
ということで今回はAIエージェントとオープンデータを使った、効率的なアプリ開発について実践していきます。

今回はDB構築編です。

# 統計データを活用するための課題

例えばWebアプリやダッシュボードで「公的な統計データ」を組み込もうとすると避けて通れないのが、e-Statなどからの CSV 取得やクレンジングといった準備作業です。  
これにより、本来注力すべき開発・実装の前に多くの時間が奪われてしまいます。

![統計データを利用するための障害](https://static.zenn.studio/user-upload/85b5bfd01f3b-20260225.png)  
*オープンデータといっても、すぐに使えるものは少ない*  
そこで今回は「データの準備」をスキップするため、snowflakeで提供されているオープンデータ「**Prepper Open Data Bank(PODB)**」を活用します。

## PODBを活用するメリット

<https://podb.truestar.co.jp/>

PODBは、e-Statで公開されている国勢調査をはじめとした商用・二次利用可能なオープンデータを、分析・開発にすぐ活用できる状態で提供するサービスです。

* **加工済み**: オープンデータを整形・クレンジング済みで提供。すぐに分析へ着手できます。
* **自動更新**: ソース元の更新に自動で追従するため、鮮度管理が不要です。
* **多分野を網羅**: 人流・気象・統計など、多様なデータを一か所に集約。
* **無料:** 商用利用も可能です。

# 今回の試み

今回はPODBのラインナップから「JAPANESE CITY DATA（市区町村単位統計）」を選択し、Claude CodeとStreamlitを組み合わせたWebアプリを構築します。

![PODBには多種多様なデータが存在する](https://static.zenn.studio/user-upload/d1a0c0847ca5-20260225.png)  
*PODBには多種多様なデータが存在する*

## 今回作りたいもの

かなりシンプルですが、下記のようなアプリ開発を想定します。

* 機能①: 都道府県を選択すると、属する市区町村の各種指標と値を可視化
* 機能②: 複数の市区町村を選び、各種指標と値を比較
* 表示にはテーブルと棒グラフ・円グラフを使用

**今回はそのアプリ開発に必要な、データベースの構築に焦点を当てて実践していきます。**

# **データベースの構築**

## PODBの取得

Snowflakeのマーケットプレイスより、PODBの「Japanese City Data」を取得します。  
![Japanese City Dataを取得する](https://static.zenn.studio/user-upload/81730dd52463-20260225.png)  
*無料！*

## **データの確認と結合**

### データを取得してみる

早速PODBのデータを活用していきましょう。  
公式でER図が提供されているので、これをもとにテーブルを結合してみましょう。  
<https://podb.truestar.co.jp/archives/city-data/er>  
例えばSQLはこんな感じですね

```
-- 主要なテーブルを結合する(10件のみ)
select * from ci_tb_mst tb_mst
inner join ci_st_mst st_mst on st_mst.estatdb_research_table_id = tb_mst.estatdb_research_table_id
inner join ci_st st on st.estatdb_stats_full_id = st_mst.estatdb_stats_full_id
inner join ci_mst mst on mst.city_code = st.city_code
inner join ci_geo_pt geo_pt on geo_pt.city_code = mst.city_code
inner join ci_geo_pg geo_pg on geo_pg.city_code = mst.city_code
limit 10;
```

実行結果です。問題なさそうですね。  
![CITY_DATAを取得](https://static.zenn.studio/user-upload/a7d207c2f983-20260226.png)

なお、今回利用しているCITY\_DATAには結合済みのビュー（日本語版・英語版）も用意されているので、素早く使いたい場合はそちらも便利です。  
![日本語版結合済みビュー](https://static.zenn.studio/user-upload/b164e7ec7acb-20260226.png)

### Claude Codeを使ってみる

さてここから、CITY DATAにはどういったテーブルなのか、どういったカラムがあるのか、そしてどういったレコードがあるのかを理解する必要があります。

PODBのサイトにはテーブルやカラムについての説明があるので、通常はこれらをSELECTしデータを読み解いていく作業があるのですが、ここでもClaude Codeを活用してみましょう。

サイトのURLを渡して、**Claude Codeにデータ分析を手伝ってもらいます。**

![claude codeに依頼する](https://static.zenn.studio/user-upload/afcd8a4fc05e-20260227.png)  
*手伝うっていうか丸投げしてる*

結果がこちらです。  
![PODBスキーマ 総合分析](https://static.zenn.studio/user-upload/92287b3afd2f-20260227.png)  
*この下には統計カテゴリ内訳や、実データのポイントについても言及しています*

おお、かなり分かりやすくまとめてくれています。  
開発者による確認は必要ですが、**ゼロから確認するよりも、格段に早く情報収集ができそうです。**

![ビューについても言及](https://static.zenn.studio/user-upload/8f07568ec499-20260227.png)  
結合済のビューについても言及してくれていますね。  
このように、データ理解やデータ探索のアシスタントとしても、Claude Codeは活用できると考えています。

## データベースの設計

### どのようなデータベースを構築するべきか

次はデータベースの設計について考えてみましょう。これらについて検討するのも開発の醍醐味ですが、**Claude Codeに一回聞いてみましょう。**  
アイデアを募ったり、仕様の是非を相談するのも、生成AIの有効な活用方法だと考えております。

![DB設計を相談してみる](https://static.zenn.studio/user-upload/978aa60d098b-20260227.png)

雑な依頼にClaude Codeも心なしか考え込んでいるようでしたが、提案を頂きました。

![DB設計の提案](https://static.zenn.studio/user-upload/b1ef74b29b00-20260227.png)  
*この下に設計内容が続きます*

いいですね。具体的に、課題と詳細について整理してくれました。  
省略していますが具体的なテーブル名やカラム名についても提示してくれています。

今回はゼロから設計を依頼しましたが、  
方向性としてはそんなに違和感がないものを提案してくれました。

仕様を固めてから設計を依頼するもよし、  
いったん仮の設計を組んでもらってイメージを膨らませるもよし、  
そういった使い方ができるのも、Claude Codeの利点だと感じます。

### 指標、基本情報、補足情報の構造とする

Claude Codeとしばらくやり取りを続け、最終的には下記の仕様に落ち着きました。

1. CITY\_DATAの様々な指標から、取り扱う指標を「指標マスタ」に登録する
2. 指標マスタのデータを元に、「基本情報データ」を作成する
3. 別途、独自で追加したいデータを「補足情報データ」に登録する

![データとアプリの関連性](https://static.zenn.studio/user-upload/b46e2a2f0dcb-20260324.png)  
*「基本情報データ」と「補足情報テーブル」を連結したデータを取り扱う*

PODBのデータをそのまま表示するだけでも良かったのですが、  
「アプリ内で取り扱う指標マスタは別のテーブルで管理する」「PODBの値だけでなく、独自に算出した割合なども表示できる」などの機能があった方が実用的・リアリティがあるかと思ったので、このような仕様にしてみました。

### 設計の意思決定

補足情報データの仕様については多少の検討時間がありました。  
最もスマートな解決策はカスタム指標とその計算式をテーブルで持ち、動的に補足情報を形成することでしょう。しかしsnowflakeの実行コストや更新頻度を考えたとき、そこまで高度なものは不要になるだろうと判断しました。

なので次点のアイデアとして、補足情報を保持するテーブルを作成し、pythonのスクリプトで定期的にデータを更新する方式を採用しました。

![補足情報テーブルはスクリプトによって定期的に更新される](https://static.zenn.studio/user-upload/b3bbac46415f-20260324.png)  
*補足情報テーブルはスクリプトによって定期的に更新される*

補足情報を生成するスクリプトを走らせて、PODBのデータなどから独自の統計を補足情報テーブルに取り込むことを想定しています。

デモであっても、こうした仕様や設計を決定するのは人間の役割だなと感じます。

## 開発

### 指標マスタ

さて仕様と設計が決まったので開発に進んでいきましょう。  
Claude Codeをフル活用し、指標マスタを作成します。

```
create or replace TABLE CITYDASHBOARD.PUBLIC.CITY_BASIC_INDICATOR (
	ESTATDB_STATS_FULL_ID VARCHAR(200) NOT NULL,
	DESCRIPTION VARCHAR(500),
	primary key (ESTATDB_STATS_FULL_ID)
)COMMENT='基本指標マスタ: 表示する指標のIDと説明'
;
```

指標IDと概要を登録するシンプルなテーブルです。

従来であればひとつずつ指標を選定していくところですが、せっかくなのでClaudeに依頼してみました。  
![claudeに指標を選定して貰う](https://static.zenn.studio/user-upload/d01d9f176208-20260325.png)  
*やれんのか！？*  
![Claudeが指標を選定した](https://static.zenn.studio/user-upload/52cfe14b15e7-20260325.png)  
*心なしか誇らしげ*

さすがです。使えそうな指標をまとめてくれました。分析・開発の足がかりとしては十分なレベルです。  
ここからカテゴリや指標を壁打ちする地味な時間もありましたが、「このカテゴリで使えそうな指標はある？」「このカテゴリの指標一覧を見せて」といった、Claudeとのやり取りを経て指標を精査しました。

### 基本情報データ

では、CITY\_DATA(PODB)と指標マスタを使って、webアプリのための基本情報をビューでまとめてみましょう。  
こちらもClaudeに相談しながら作成しました。

```
CREATE OR REPLACE VIEW CITY_BASIC_DATA (PREF_CODE, PREF_NAME, CITY_CODE, CITY_NAME, STATS_CATEGORY, STATS_SUBCATEGORY, ESTATDB_STATS_FULL_ID, ESTATDB_STATS_FULL_NAME, STATS_VALUE, STATS_UNIT, STATS_YEAR) AS
SELECT MST.pref_code, MST.pref_name, ST.city_code, MST.city_name, TB_MST.stats_category, TB_MST.stats_subcategory, ST.estatdb_stats_full_id,
       COALESCE(IND.DESCRIPTION, ST_MST.estatdb_stats_full_name) AS ESTATDB_STATS_FULL_NAME, ST.stats_value, ST.STATS_UNIT, ST.STATS_YEAR
FROM PREPPER_OPEN_DATA_BANK__JAPANESE_CITY_DATA.PODB.CI_ST ST
JOIN PREPPER_OPEN_DATA_BANK__JAPANESE_CITY_DATA.PODB.CI_MST MST ON MST.city_code = ST.city_code
JOIN PREPPER_OPEN_DATA_BANK__JAPANESE_CITY_DATA.PODB.CI_ST_MST ST_MST ON ST.estatdb_stats_full_id = ST_MST.estatdb_stats_full_id
JOIN PREPPER_OPEN_DATA_BANK__JAPANESE_CITY_DATA.PODB.CI_TB_MST TB_MST ON ST_MST.estatdb_research_table_id = TB_MST.estatdb_research_table_id
LEFT JOIN CITYDASHBOARD.PUBLIC.CITY_BASIC_INDICATOR IND ON ST.estatdb_stats_full_id = IND.ESTATDB_STATS_FULL_ID
WHERE ST.estatdb_stats_full_id IN (SELECT ESTATDB_STATS_FULL_ID FROM CITYDASHBOARD.PUBLIC.CITY_BASIC_INDICATOR)
ORDER BY ST.city_code, ST.estatdb_stats_full_id;
```

SELECTした結果は下記です。  
CITY\_DATAの様々なデータから、特定の指標、特定のカラムのみを取り出すことができました。  
データを使いやすい形に加工したことで、webアプリ側の開発も効率的になることでしょう。  
![基本情報データ](https://static.zenn.studio/user-upload/ee43a88e1381-20260325.png)

### 補足情報データ

補足情報データは、基本情報データと同じ構造にして連結する形を考えました。  
Claude Codeを使い、PODBビューと同じ構造のテーブルを生成します。

```
CREATE OR REPLACE TABLE CITY_CUSTOM_DATA (
    PREF_CODE VARCHAR(255),
    PREF_NAME VARCHAR(255),
    CITY_CODE VARCHAR(254),
    CITY_NAME VARCHAR(255),
    STATS_CATEGORY VARCHAR(255),
    STATS_SUBCATEGORY VARCHAR(255),
    ESTATDB_STATS_FULL_ID VARCHAR(254),
    ESTATDB_STATS_FULL_NAME VARCHAR(10000),
    STATS_VALUE FLOAT,
    STATS_UNIT VARCHAR(254),
    STATS_YEAR VARCHAR(254)
)
COMMENT = 'カスタムデータ: ユーザー定義の統計データ';
```

CITY\_DATAには総人口・男性人口・女性人口はありますが男性割合・女性割合がないため、新たな指標として計算、追加しました。  
こういったシンプルな計算とデータ追加もclaudeに依頼すればまとめてやってくれますね。

![男性割合・女性割合の登録](https://static.zenn.studio/user-upload/fba468bac9e1-20260325.png)  
*男性割合・女性割合の登録*

Claude Codeはコーディング力に目が行きがちですが、こういった作業に利用することができます。AIということで誘導や品質チェックやはもちろん必要ですが、PODBのデータがクレンジング済みだったこともあり、シンプルな作業でデータを準備できました。

## できあがったデータを確認する

今回構築したデータは以下の2つで構成しています。

* **基本情報データ**: webアプリ用にPODBのデータを「指標マスタ」で抽出・整理したもの
* **補足情報データ**: PODBに存在しないデータを独自に追加したもの

この2つを連結してダッシュボード用データとします。  
市区町村で絞り込むとこんな感じ。

![東京都渋谷区の結果](https://static.zenn.studio/user-upload/905fd30c3551-20260326.png)  
*東京都渋谷区の各指標*

![市区町村の男性割合](https://static.zenn.studio/user-upload/73394c5d9815-20260326.png)  
*市区町村の男性割合（補足情報データ）*

いいですね。この連結データがあればアプリ化できそうです。

# おわりに

DB構築はこれで完了です。Claude Codeを活用することで、データの内容を素早く把握し、ビューやテーブルを手軽に作成できました。

一方で**意外とスピード感がないな**と思った方もいるかもしれません。例えば「PODBのデータを使って、都道府県別人口のTOP10を表示するwebアプリを作って」といえばそれだけで完成させることもできるでしょう。

しかし個人的な意見としては、そのように生成されるシステムには哲学がなく、哲学がないシステムは「なんか違うんだよなあ…」みたいなものになりがちです。これはAIエージェントを使っても使わなくても同様です。  
**どのようなシステムを求めているのか、そのためには何が必要なのか、それらの意思決定はまだ人間の手が必要になっています。**

とはいえClaude Codeなしで同じことをやろうとすれば、5倍・10倍以上の時間がかかっていたでしょう。従来は地道な作業が必要だったデータ基盤の構築が、格段に速く実装できたのは間違いありません。

今後も振り回されることなく、距離を置くのでもなく、AIと二人三脚でエンジニアリングしていきたいと思います。

以上です。  
次回はstreamlitアプリ実装編に進みます。

ここまでお読みいただき、ありがとうございました。
