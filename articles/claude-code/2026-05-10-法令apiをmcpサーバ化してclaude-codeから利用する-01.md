---
id: "2026-05-10-法令apiをmcpサーバ化してclaude-codeから利用する-01"
title: "法令APIをMCPサーバ化してClaude Codeから利用する"
url: "https://qiita.com/wonderrrrrr/items/8b03479a9575af93aa7c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

## はじめに

デジタル庁が運営する[e-Gov法令検索](https://laws.e-gov.go.jp/)は、日本の法令を検索・閲覧できるシステムで、法令データの検索や法令文の一括ダウンロードに対応しています。そのデータ取得用に[法令API（Version 2）](https://laws.e-gov.go.jp/api/2/swagger-ui#/)も提供されています。
本記事では、この法令APIをリモートMCPサーバに変換し、ローカルPCのClaude Codeから呼び出してみます。

## 法令API（Version 2）の実行例

法令API Version 2では、下記のAPIが公開されています。
各APIの必須・任意パラメータなどの仕様は、https://laws.e-gov.go.jp/api/2/swagger-ui#/ に記載があります。

| メソッド | API | 説明 | 
| --- | --- | --- | 
| GET | /laws | 法令一覧取得 |
| GET | /law_revisions/{law_id_or_num} | 法令履歴一覧取得 |
| GET | /law_data/{law_id_or_num_or_revision_id} | 法令本文取得 |
| GET | /attachment/{law_revision_id} | 添付ファイル取得 | 
| GET | /keyword | キーワード検索 |
| GET | /law_file/{file_type}/{law_id_or_num_or_revision_id} | 法令本文ファイル取得 |  

例えば、キーワード検索APIをCURLで実行すると、下記のようなレスポンスが返ってきます。

- キーワード検索APIの実行例

```bash
$ curl -X 'GET' \
  'https://laws.e-gov.go.jp/api/2/keyword?keyword=人工知能' \
  -H 'accept: application/json'
```

<details><summary>Response body</summary>

```bash
{
  "total_count": 160,
  "sentence_count": 100,
  "next_offset": 100,
  "items": [
    {
      "law_info": {
        "law_type": "Act",
        "law_id": "332AC0000000026",
        "law_num": "昭和三十二年法律第二十六号",
        "law_num_era": "Showa",
        "law_num_year": 32,
        "law_num_type": "Act",
        "law_num_num": "026",
        "promulgation_date": "1957-03-31"
      },
      "revision_info": {
        "law_revision_id": "332AC0000000026_20260501_508AC0000000012",
        "law_type": "Act",
        "law_title": "租税特別措置法",
        "law_title_kana": "そぜいとくべつそちほう",
        "abbrev": "租特法",
        "category": "国税",
        "updated": "2026-05-01T00:41:35+09:00",
        "amendment_promulgate_date": "2026-03-31",
        "amendment_enforcement_date": "2026-05-01",
        "amendment_enforcement_comment": null,
        "amendment_scheduled_enforcement_date": null,
        "amendment_law_id": "508AC0000000012",
        "amendment_law_title": "所得税法等の一部を改正する法律",
        "amendment_law_title_kana": null,
        "amendment_law_num": "令和八年法律第十二号",
        "amendment_type": "3",
        "repeal_status": "None",
        "repeal_date": null,
        "remain_in_force": false,
        "mission": "New",
        "current_revision_status": "CurrentEnforced"
      },
      "sentences": [
        {
          "position": "mainprovision",
          "text": "」という。）であつて、前項の法人が令和六年四月一日以後に取得又は製作をしたものをいう。特許権官民データ活用推進基本法（平成二十八年法律第百三号）第二条第二項に規定する<span>人工知能</span>"
        }
      ]
    },
    {
      "law_info": {
        "law_type": "Act",
        "law_id": "345AC0000000090",
        "law_num": "昭和四十五年法律第九十号",
        "law_num_era": "Showa",
        "law_num_year": 45,
        "law_num_type": "Act",
        "law_num_num": "090",
        "promulgation_date": "1970-05-22"
      },
      "revision_info": {
        "law_revision_id": "345AC0000000090_20250804_507AC0000000030",
        "law_type": "Act",
        "law_title": "情報処理の促進に関する法律",
        "law_title_kana": "じょうほうしょりのそくしんにかんするほうりつ",
        "abbrev": "情報処理促進法",
        "category": "産業通則",
        "updated": "2026-03-02T17:45:51+09:00",
        "amendment_promulgate_date": "2025-05-14",
        "amendment_enforcement_date": "2025-08-04",
        "amendment_enforcement_comment": null,
        "amendment_scheduled_enforcement_date": null,
        "amendment_law_id": "507AC0000000030",
        "amendment_law_title": "情報処理の促進に関する法律及び特別会計に関する法律の一部を改正する法律",
        "amendment_law_title_kana": null,
        "amendment_law_num": "令和七年法律第三十号",
        "amendment_type": "3",
        "repeal_status": "None",
        "repeal_date": null,
        "remain_in_force": false,
        "mission": "New",
        "current_revision_status": "CurrentEnforced"
      },
      "sentences": [
        {
          "position": "toc",
          "text": "第六章　先端半導体・<span>人工知能</span>関連技術債（第六十九条―第七十三条）"
        },
        {
          "position": "mainprovisiontoc",
          "text": "第六章　先端半導体・<span>人工知能</span>関連技術債"
        },
        {
          "position": "caption",
          "text": "（先端半導体・<span>人工知能</span>関連技術債の発行）"
        },
        {
          "position": "mainprovision",
          "text": "境に応じた安定的かつ適切なエネルギーの需給構造の構築に資するものとして講ずる先端的な半導体の性能の向上及びその安定的な生産の確保並びに先端的な電子計算機の導入その他の<span>人工知能</span>"
        },
        {
          "position": "mainprovision",
          "text": "先端的な電子計算機の導入、<span>人工知能</span>関連技術を活用して官民データ活用推進基本法第二条第二項の機能を実現するために必要な基礎的なプログラムの開発又は先端的な電子計算機に係る技術の"
        },
        {
          "position": "mainprovision",
          "text": "第一項の規定による公債（以下この章において「先端半導体・<span>人工知能</span>関連技術債」という。）の発行は、各年度の翌年度の六月三十日までの間、行うことができる。この場合において、翌年度"
        },
        {
          "position": "caption",
          "text": "（先端半導体・<span>人工知能</span>関連技術債等の償還）"
        },
        {
          "position": "mainprovision",
          "text": "先端半導体・<span>人工知能</span>関連技術債等（先端半導体・<span>人工知能</span>関連技術債及び先端半導体・<span>人工知能</span>関連技術債に係る借換国債（特別会計"
        },
        {
          "position": "caption",
          "text": "（先端半導体・<span>人工知能</span>関連技術措置に係る歳入歳出の経理）"
        },
        {
          "position": "mainprovision",
          "text": "先端半導体・<span>人工知能</span>関連技術措置並びに先端半導体・<span>人工知能</span>関連技術債の発行及び償還に係る歳入歳出は、先端半導体・<span>人工知能</span>関"
        },
        {
          "position": "caption",
          "text": "（財政投融資特別会計の投資勘定からエネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定への繰入れ）"
        },
        {
          "position": "mainprovision",
          "text": "次の各号に掲げる費用の財源に充てるため、当該各号に定める期間においては、予算で定めるところにより、財政投融資特別会計の投資勘定からエネルギー対策特別会計の先端半導体・<span>人工知能</span>"
        },
        {
          "position": "mainprovision",
          "text": "先端半導体・<span>人工知能</span>関連技術措置に要する費用令和七年度から令和十二年度までの間"
        },
        {
          "position": "mainprovision",
          "text": "先端半導体・<span>人工知能</span>関連技術債等の償還金（借換国債を発行した場合においては、当該借換国債の収入をもつて充てられる部分を除く。）、利子並びに先端半導体・<span>人工知能</"
        },
        {
          "position": "mainprovision",
          "text": "第六十九条第一項の規定により先端半導体・<span>人工知能</span>関連技術債を発行する場合におけるエネルギー対策特別会計についての特別会計に関する法律第十六条の規定の適用については、同条中「融"
        },
        {
          "position": "caption",
          "text": "（エネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定の廃止等）"
        },
        {
          "position": "amendsupplprovision",
          "text": "エネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定は、別に法律で定めるところにより、令和十五年三月三十一日までに廃止するものとする。"
        },
        {
          "position": "amendsupplprovision",
          "text": "政府は、前項の規定によりエネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定が廃止されるときは、同項の法律で定めるところにより、第一条の規定による改正後の情報処理の促進に"
        }
      ]
    },
    {
      "law_info": {
        "law_type": "Act",
        "law_id": "411AC0000000089",
        "law_num": "平成十一年法律第八十九号",
        "law_num_era": "Heisei",
        "law_num_year": 11,
        "law_num_type": "Act",
        "law_num_num": "089",
        "promulgation_date": "1999-07-16"
      },
      "revision_info": {
        "law_revision_id": "411AC0000000089_20260401_507AC0000000043",
        "law_type": "Act",
        "law_title": "内閣府設置法",
        "law_title_kana": "ないかくふせっちほう",
        "abbrev": "中央省庁等改革関連法",
        "category": "行政組織",
        "updated": "2026-04-02T00:22:45+09:00",
        "amendment_promulgate_date": "2025-05-23",
        "amendment_enforcement_date": "2026-04-01",
        "amendment_enforcement_comment": null,
        "amendment_scheduled_enforcement_date": null,
        "amendment_law_id": "507AC0000000043",
        "amendment_law_title": "重要電子計算機に対する不正な行為による被害の防止に関する法律の施行に伴う関係法律の整備等に関する法律",
        "amendment_law_title_kana": null,
        "amendment_law_num": "令和七年法律第四十三号",
        "amendment_type": "3",
        "repeal_status": "None",
        "repeal_date": null,
        "remain_in_force": false,
        "mission": "New",
        "current_revision_status": "CurrentEnforced"
      },
      "sentences": [
        {
          "position": "mainprovision",
          "text": "<span>人工知能</span>関連技術（<span>人工知能</span>関連技術の研究開発及び活用の推進に関する法律（令和七年法律第五十三号）第二条に規定するものをいう。第三項第七号の九において"
        },
        {
          "position": "mainprovision",
          "text": "<span>人工知能</span>関連技術の研究開発及び活用に関する施策の推進に関すること。"
        }
      ]
    },
    {
      "law_info": {
        "law_type": "Act",
        "law_id": "419AC0000000023",
        "law_num": "平成十九年法律第二十三号",
        "law_num_era": "Heisei",
        "law_num_year": 19,
        "law_num_type": "Act",
        "law_num_num": "023",
        "promulgation_date": "2007-03-31"
      },
      "revision_info": {
        "law_revision_id": "419AC0000000023_20260401_507AC0000000052",
        "law_type": "Act",
        "law_title": "特別会計に関する法律",
        "law_title_kana": "とくべつかいけいにかんするほうりつ",
        "abbrev": "特別会計法,特会法",
        "category": "財務通則",
        "updated": "2026-01-06T10:01:15+09:00",
        "amendment_promulgate_date": "2025-06-04",
        "amendment_enforcement_date": "2026-04-01",
        "amendment_enforcement_comment": null,
        "amendment_scheduled_enforcement_date": null,
        "amendment_law_id": "507AC0000000052",
        "amendment_law_title": "脱炭素成長型経済構造への円滑な移行の推進に関する法律及び資源の有効な利用の促進に関する法律の一部を改正する法律",
        "amendment_law_title_kana": null,
        "amendment_law_num": "令和七年法律第五十二号",
        "amendment_type": "3",
        "repeal_status": "None",
        "repeal_date": null,
        "remain_in_force": false,
        "mission": "New",
        "current_revision_status": "PreviousEnforced"
      },
      "sentences": [
        {
          "position": "mainprovision",
          "text": "金及び利子この勘定に帰属する納付金投資財源資金からの受入金投資財源資金から生ずる収入一般会計からの繰入金第九十一条の七の規定によるエネルギー対策特別会計の先端半導体・<span>人工知能</span>"
        },
        {
          "position": "mainprovision",
          "text": "歳出出資の払込金貸付金投資財源資金への繰入金一般会計への繰入金第六十八条の二の規定によるエネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定への繰入金借入金の償還金及び利"
        },
        {
          "position": "caption",
          "text": "（投資勘定からエネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定への繰入れ）"
        },
        {
          "position": "mainprovision",
          "text": "要する費用並びに第八十八条第四項第二号ヘの償還金及び利子並びに同号トの諸費の財源に充てるため、予算で定める金額を限り、投資勘定からエネルギー対策特別会計の先端半導体・<span>人工知能</span>"
        },
        {
          "position": "mainprovision",
          "text": "エネルギー対策特別会計は、燃料安定供給対策、エネルギー需給構造高度化対策、電源立地対策、電源利用対策、原子力安全規制対策、原子力損害賠償支援対策及び先端半導体・<span>人工知能</span>関連技"
        },
        {
          "position": "mainprovision",
          "text": "この節において「先端半導体・<span>人工知能</span>関連技術対策」とは、次に掲げる財政上の措置をいう。"
        },
        {
          "position": "mainprovision",
          "text": "情報処理の促進に関する法律第六十九条第一項第四号に掲げる措置で政令で定めるもの（第八十八条第四項において「先端半導体・<span>人工知能</span>関連技術対策に係る附帯事務等に関する措置」という"
        },
        {
          "position": "mainprovision",
          "text": "ろにより、同会計全体の計算整理に関するものについては経済産業大臣が、その他のものについてはエネルギー需給勘定、電源開発促進勘定、原子力損害賠償支援勘定又は先端半導体・<span>人工知能</span>"
        },
        {
          "position": "mainprovision",
          "text": "エネルギー対策特別会計は、エネルギー需給勘定、電源開発促進勘定、原子力損害賠償支援勘定及び先端半導体・<span>人工知能</span>関連技術勘定に区分する。"
        },
        {
          "position": "mainprovision",
          "text": "号ハの出資金及び交付金第八十五条第三項第一号ニからトまでの補助金第九十一条の四第一項の規定による電源開発促進勘定への繰入金第九十一条の五第一項の規定による先端半導体・<span>人工知能</span>"
        },
        {
          "position": "mainprovision",
          "text": "先端半導体・<span>人工知能</span>関連技術勘定における歳入及び歳出は、次のとおりとする。"
        },
        {
          "position": "mainprovision",
          "text": "資勘定からの繰入金第九十一条の五第一項の規定によるエネルギー需給勘定からの繰入金情報処理の促進に関する法律第六十九条第一項の規定により発行する公債（以下「先端半導体・<span>人工知能</span>"
        },
        {
          "position": "mainprovision",
          "text": "金、委託費その他の給付金を含む。ハにおいて同じ。）第八十五条第八項第三号の補助金及び出資金第九十一条の七の規定による財政投融資特別会計の投資勘定への繰入金先端半導体・<span>人工知能</span>"
        },
        {
          "position": "caption",
          "text": "（一般会計から先端半導体・<span>人工知能</span>関連技術勘定への繰入れの特例）"
        },
        {
          "position": "mainprovision",
          "text": "かつ効率的な実施に必要であると認められるものの財源として設置する基金に充てるために経済産業大臣が交付した補助金について、国に返納された金額がある場合には、先端半導体・<span>人工知能</span>"
        },
        {
          "position": "caption",
          "text": "（エネルギー需給勘定から先端半導体・<span>人工知能</span>関連技術勘定への繰入れ）"
        },
        {
          "position": "mainprovision",
          "text": "先端半導体・<span>人工知能</span>関連技術対策に要する費用の財源に充てるため、予算で定める金額を限り、エネルギー需給勘定から先端半導体・<span>人工知能</span>関連技術勘定に繰り"
        },
        {
          "position": "mainprovision",
          "text": "繰入れが行われる年度における第九十条ただし書の規定の適用については、同条ただし書中「費用の額」とあるのは、「費用の額並びに第九十一条の五第一項の規定による先端半導体・<span>人工知能</span>"
        },
        {
          "position": "caption",
          "text": "（先端半導体・<span>人工知能</span>関連技術勘定から財政投融資特別会計の投資勘定への繰入れ）"
        },
        {
          "position": "mainprovision",
          "text": "第六十八条の二の規定により財政投融資特別会計の投資勘定から繰り入れられた繰入金については、後日、先端半導体・<span>人工知能</span>関連技術勘定からその繰入金に相当する金額に達するまでの金額"
        },
        {
          "position": "caption",
          "text": "（先端半導体・<span>人工知能</span>関連技術債の発行）"
        },
        {
          "position": "mainprovision",
          "text": "情報処理の促進に関する法律第六十九条第一項の規定によりエネルギー対策特別会計の負担において行われる先端半導体・<span>人工知能</span>関連技術債の発行は、先端半導体・<span>人工知能</"
        },
        {
          "position": "caption",
          "text": "（先端半導体・<span>人工知能</span>関連技術勘定から国債整理基金特別会計等への繰入れ）"
        },
        {
          "position": "mainprovision",
          "text": "先端半導体・<span>人工知能</span>関連技術債及び当該先端半導体・<span>人工知能</span>関連技術債に係る借換国債の償還金（借換国債を発行した場合においては、当該借換国債の収入をも"
        },
        {
          "position": "mainprovision",
          "text": "前項に規定する事務取扱費の額に相当する金額は、毎会計年度、先端半導体・<span>人工知能</span>関連技術勘定から一般会計に繰り入れなければならない。"
        },
        {
          "position": "mainprovision",
          "text": "第十五条第四項の規定にかかわらず、エネルギー需給勘定、電源開発促進勘定及び先端半導体・<span>人工知能</span>関連技術勘定において、歳入不足のために一時借入金を償還することができない場合には"
        },
        {
          "position": "supplprovision",
          "text": "令和十六年度以前の各年度の第九十一条の五第一項の規定によるエネルギー需給勘定から先端半導体・<span>人工知能</span>関連技術勘定への繰入金の決算額を合算した額から令和十六年度以前の各年度の同"
        },
        {
          "position": "supplprovision",
          "text": "令和十七年度以降の年度に先端半導体・<span>人工知能</span>関連技術勘定における第九十一条の五第一項の規定に基づくエネルギー需給勘定からの繰入金を財源とする財政上の措置に要する費用について国"
        },
        {
          "position": "supplprovision",
          "text": "第八十八条第一項の規定によるほか、前二項の規定による先端半導体・<span>人工知能</span>関連技術勘定からエネルギー需給勘定への繰入金は、同勘定の歳入とする。"
        },
        {
          "position": "supplprovision",
          "text": "第八十八条第四項の規定によるほか、第一項及び第二項の規定による先端半導体・<span>人工知能</span>関連技術勘定からエネルギー需給勘定への繰入金は、先端半導体・<span>人工知能</span"
        },
        {
          "position": "caption",
          "text": "（エネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定の廃止等）"
        },
        {
          "position": "amendsupplprovision",
          "text": "エネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定は、別に法律で定めるところにより、令和十五年三月三十一日までに廃止するものとする。"
        },
        {
          "position": "amendsupplprovision",
          "text": "政府は、前項の規定によりエネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定が廃止されるときは、同項の法律で定めるところにより、第一条の規定による改正後の情報処理の促進に"
        },
        {
          "position": "amendsupplprovision",
          "text": "「令和六年度第一次補正予算」という。）に計上された費用のうち新特会法第八十五条第八項の財政上の措置に該当する措置に要する費用（次項及び次条第一項において「先端半導体・<span>人工知能</span>"
        },
        {
          "position": "amendsupplprovision",
          "text": "令和六年度第一次補正予算に計上された先端半導体・<span>人工知能</span>関連技術費用に関する経費であって、財政法第十四条の三第一項又は第四十二条ただし書の規定により繰越しをしたものについて、"
        },
        {
          "position": "amendsupplprovision",
          "text": "この法律の施行の際エネルギー対策特別会計のエネルギー需給勘定に所属する権利義務であって、令和六年度の特別会計補正予算（特第１号）に計上された費用のうち先端半導体・<span>人工知能</span>関連"
        },
        {
          "position": "amendsupplprovision",
          "text": "前項の規定によりエネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定に帰属する権利義務に係る収入は、予算で定めるところにより、同勘定からエネルギー需給勘定に繰り入れるもの"
        },
        {
          "position": "amendsupplprovision",
          "text": "新特会法第八十八条第一項の規定によるほか、前項の規定によるエネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定からエネルギー需給勘定への繰入金は、同勘定の歳入とする。"
        },
        {
          "position": "amendsupplprovision",
          "text": "新特会法第八十八条第四項の規定によるほか、第二項の規定によるエネルギー対策特別会計の先端半導体・<span>人工知能</span>関連技術勘定からエネルギー需給勘定への繰入金は、先端半導体・<span"
        }
      ]
    },
    {
      "law_info": {
        "law_type": "Act",
        "law_id": "419AC0000000059",
        "law_num": "平成十九年法律第五十九号",
        "law_num_era": "Heisei",
        "law_num_year": 19,
        "law_num_type": "Act",
        "law_num_num": "059",
        "promulgation_date": "2007-05-25"
      },
      "revision_info": {
        "law_revision_id": "419AC0000000059_20250601_504AC0000000068",
        "law_type": "Act",
        "law_title": "地域公共交通の活性化及び再生に関する法律",
        "law_title_kana": "ちいきこうきょうこうつうのかっせいかおよびさいせいにかんするほうりつ",
        "abbrev": "地域公共交通活性化・再生法,地域公共交通活性化法",
        "category": "陸運",
        "updated": "2025-06-01T23:25:17+09:00",
        "amendment_promulgate_date": "2022-06-17",
        "amendment_enforcement_date": "2025-06-01",
        "amendment_enforcement_comment": null,
        "amendment_scheduled_enforcement_date": null,
        "amendment_law_id": "504AC0000000068",
        "amendment_law_title": "刑法等の一部を改正する法律の施行に伴う関係法律の整理等に関する法律　抄",
        "amendment_law_title_kana": null,
        "amendment_law_num": "令和四年法律第六十八号",
        "amendment_type": "3",
        "repeal_status": "None",
        "repeal_date": null,
        "remain_in_force": false,
        "mission": "New",
        "current_revision_status": "CurrentEnforced"
      },
      "sentences": [
        {
          "position": "mainprovision",
          "text": "客自動車運送事業者が円滑な運送の実施を確保するために行う事業であって、運行経路指示システム（官民データ活用推進基本法（平成二十八年法律第百三号）第二条第二項に規定する<span>人工知能</span>"
        }
      ]
    },
    {
      "law_info": {
        "law_type": "Act",
        "law_id": "425AC0000000107",
        "law_num": "平成二十五年法律第百七号",
        "law_num_era": "Heisei",
        "law_num_year": 25,
        "law_num_type": "Act",
        "law_num_num": "107",
        "promulgation_date": "2013-12-13"
      },
      "revision_info": {
        "law_revision_id": "425AC0000000107_20260501_507AC0000000037",
        "law_type": "Act",
        "law_title": "国家戦略特別区域法",
        "law_title_kana": "こっかせんりゃくとくべつくいきほう",
        "abbrev": "国家戦略特区法",
        "category": "国土開発",
        "updated": "2026-05-01T02:23:56+09:00",
        "amendment_promulgate_date": "2025-05-21",
        "amendment_enforcement_date": "2026-05-01",
        "amendment_enforcement_comment": null,
        "amendment_scheduled_enforcement_date": null,
        "amendment_law_id": "507AC0000000037",
        "amendment_law_title": "医薬品、医療機器等の品質、有効性及び安全性の確保等に関する法律等の一部を改正する法律",
        "amendment_law_title_kana": null,
        "amendment_law_num": "令和七年法律第三十七号",
        "amendment_type": "3",
        "repeal_status": "None",
        "repeal_date": null,
        "remain_in_force": false,
        "mission": "New",
        "current_revision_status": "CurrentEnforced"
      },
      "sentences": [
        {
          "position": "mainprovision",
          "text": "この法律において「先端的区域データ活用事業活動」とは、官民データ活用推進基本法（平成二十八年法律第百三号）第二条第二項に規定する<span>人工知能</span>関連技術、同条第三項に規定するインター"
        }
      ]
    },
    {
      "law_info": {
        "law_type": "Act",
        "law_id": "428AC1000000103",
        "law_num": "平成二十八年法律第百三号",
        "law_num_era": "Heisei",
        "law_num_year": 28,
        "law_num_type": "Act",
        "law_num_num": "103",
        "promulgation_date": "2016-12-14"
      },
      "revision_info": {
        "law_revision_id": "428AC1000000103_20210901_503AC0000000035",
        "law_type": "Act",
        "law_title": "官民データ活用推進基本法",
        "law_title_kana": "かんみんでーたかつようすいしんきほんほう",
        "abbrev": "",
        "category": "電気通信",
        "updated": "2021-10-16T00:00:02+09:00",
        "amendment_promulgate_date": "2021-05-19",
        "amendment_enforcement_date": "2021-09-01",
        "amendment_enforcement_comment": null,
        "amendment_scheduled_enforcement_date": null,
        "amendment_law_id": "503AC0000000035",
        "amendment_law_title": "デジタル社会形成基本法",
        "amendment_law_title_kana": "",
        "amendment_law_num": "令和三年法律第三十五号",
        "amendment_type": "3",
        "repeal_status": "None",
        "repeal_date": null,
        "remain_in_force": false,
        "mission": "New",
        "current_revision_status": "
