---
id: "2026-04-14-専門知識不要でbim情報要件を生成-経産省とnedoのgeniacで開発したaiモデル公開-01"
title: "専門知識不要でBIM情報要件を生成 経産省とNEDOのGENIACで開発したAIモデル公開"
url: "https://built.itmedia.co.jp/bt/articles/2604/14/news122.html"
source: "rss"
category: "construction"
tags: ["rss"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

ONESTRUCTION（ワンストラクション）は、経済産業省とNEDO（新エネルギー・産業技術総合開発機構）が推進する国内生成AIの開発力強化プロジェクト「GENIAC（Generative AI Accelerator Challenge）」の一環として開発した研究開発成果となるAIモデル「Ishigaki-IDS」と評価ベンチマーク「IDS-Bench」を公開した。

### 属性情報の照査に用いるIDSを自動生成、openBIM管理を効率化

![](https://image.itmedia.co.jp/bt/articles/2604/14/is20260414ONESTRUCTION01_w490.jpg)
出典：ONESTRUCTIONプレスリリース

　ONESTRUCTIONは、BIMデータを建設プロセスの各段階でソフトウェアが異なっても問題なく受け渡せる「openBIM」の概念をテーマに、BIMで建設課題の解決に取り組む建設テック企業。2025年からは、建設ドメイン特化型の汎用生成AI基盤モデルシリーズ「Ishigaki」の開発に着手している。

　Ishigakiは、BIMのベンダーに依存しないオープンな国際標準規格「IFC（Industry Foundation Classes）」で扱う、属性情報の照査に用いられる規格「IDS（Information Delivery Specifications）」を生成する基盤モデル。IDSを自動生成することで、BIMの専門家でなくても、BIMに付与された属性情報の確認や管理が効率化され、BIM活用の裾野が広がる。

　IDSは、BIMモデル（＝IFCモデル）にどのような情報を付与するかを定義するXML形式の規格。IDSを作成するには、独自の文法に加え、IFCに関する知識やルールの理解が必要となる。そのため、ONESTRUCTIONでは基盤モデルで知識の障壁を下げ、IDSの自動生成と作成支援の実現を目的としている。

　開発した基盤モデルは、IFCデータの照査内容を整理したCSV、または自然言語による指示を入力として受け取り、それに対応するIDSを生成する。

```
User:
Please create an IDS in IFC4 to check whether the property "Fire Resistance" is set for the Door entity.
Assistant:
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ids:ids xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://standards.buildingsmart.org/IDS http://standards.buildingsmart.org/IDS/1.0/ids.xsd" xmlns:ids="http://standards.buildingsmart.org/IDS">
  <!--edit with ONESTRUCTION Inc.-->
  <ids:info>
    <ids:title>Door Fire Resistance Check</ids:title>
  </ids:info>
  <ids:specifications>
    <ids:specification ifcVersion="IFC4" name="Door Fire Resistance Check">
      <ids:applicability minOccurs="1" maxOccurs="unbounded">
        <ids:entity>
          <ids:name>
            <ids:simpleValue>IFCDOOR</ids:simpleValue>
          </ids:name>
        </ids:entity>
      </ids:applicability>
      <ids:requirements>
        <ids:property dataType="IFCLABEL" cardinality="required">
          <ids:propertySet>
            <ids:simpleValue>Pset_DoorCommon</ids:simpleValue>
          </ids:propertySet>
          <ids:baseName>
            <ids:simpleValue>FireRating</ids:simpleValue>
          </ids:baseName>
        </ids:property>
      </ids:requirements>
    </ids:specification>
  </ids:specifications>
</ids:ids>
```

**モデルの使用例。IFCのドアに、防火耐性があるかどうかを確認するIDSを生成**

　今回は、GENIACの取り組みとして、IDS生成に特化した基盤モデル「Ishigaki-IDS（8B/14B/32B）」の3種類のモデルと評価ベンチマーク「IDS-Bench」を構築した。そのうち、[「Ishigaki-IDS-8B」](https://onestruction.com/news/ishigaki-ids-ids-bench-202603)と評価ベンチマーク[「IDS-Bench」](https://huggingface.co/datasets/ONESTRUCTION/IDS-Bench)は、AIモデルやデータセットを共有できるプラットフォーム「Hugging Face」上に公開している。

　Ishigaki-IDSは、Qwen3の8B／14B／32Bをベースに、IDS生成タスクに特化させるための追加学習を実施して開発。ベースモデルの選定は[Nejumi Leaderboard4](https://nejumi.ai/)を参考にし、汎用的な言語性能と安全性が一定程度確保されていること、複数のモデルサイズがそろっていること、国内外で広く利用されているベースモデルで情報収集や検証がしやすいことから、「Qwen3」を採用している。今回の使用方法は、モデルをダウンロードし、追加学習や推論を全て管理環境で完結させる構成を取っている。そのため、学習データや入力データが外部に送信されることはないことを確認した上で開発を進めている。

![](https://image.itmedia.co.jp/bt/articles/2604/14/is20260414ONESTRUCTION02_w490.jpg)
出典：ONESTRUCTIONプレスリリース

　IDS-Benchについては、IDS自体が比較的新しい規格で、非常にニッチな領域のため、既存の評価ベンチマークが存在せず、建設／BIM領域の専門人材と協働し、生成精度を測定する独自のベンチマークを構築した。実務の現場では、組織ごとにCSVの形式や列名が異なるだけでなく、独自の用語や言い回しが用いられることも少なくない。そのため、IFCのバージョン、言語、建設分類（意匠、構造、設備など）の観点からカバレッジを確保し、IDS生成性能を多面的に評価できるように設計した。

　評価の結果、Ishigaki-IDSはIDSを適切に生成できている一方で、汎用的なフロンティアモデルでは十分に対応できないケースが多いと分かった。IDSが建設／BIM領域の中でも専門性の高い領域で、2024年に公開された比較的新しい規格なことが要因だと考えられる。ただ、ONESTRUCTIONでは、今回取り組んだタスクは、フロンティアモデルにとっては難易度が高く、ドメインに特化して開発したモデルであれば解決可能としている。

[![Ishigaki-IDSのIDS生成性能の評価結果](https://image.itmedia.co.jp/bt/articles/2604/14/is20260414ONESTRUCTION03.jpg)](https://image.itmedia.co.jp/l/im/bt/articles/2604/14/l_is20260414ONESTRUCTION03.jpg)
**Ishigaki-IDSのIDS生成性能の評価結果**　出典：ONESTRUCTIONプレスリリース

　ベンチマークによる定量評価以外にも、buildingSMARTともユーザーテストを実施。「日々の業務の中で効率化に活用できそうだ」「曖昧な表現でも意図通りのIDSを生成してくれるので驚いた」といった好意的な反応が得られたという。
