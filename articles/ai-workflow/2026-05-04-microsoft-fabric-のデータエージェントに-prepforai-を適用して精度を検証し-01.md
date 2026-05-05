---
id: "2026-05-04-microsoft-fabric-のデータエージェントに-prepforai-を適用して精度を検証し-01"
title: "Microsoft Fabric のデータエージェントに PrepForAI を適用して精度を検証してみた"
url: "https://zenn.dev/headwaters/articles/47f92204ba5baa"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## Fabricデータエージェントの精度を上げたい

Microsoft Fabricのデータエージェントは、セマンティックモデルをデータソースとして接続することで、自然言語による質問に対してDAXクエリを自動生成し、回答を返してくれます。

![](https://static.zenn.studio/user-upload/6a1cbbc01194-20260429.png)  
*Fabric上のデータエージェントの応答*

![](https://static.zenn.studio/user-upload/1f4742643479-20260429.png)  
*データエージェントの仕組み*

ただし、公式ドキュメントにも記載されている通り、データエージェントの応答品質は **データソースの準備状況に大きく依存** します。

今回は、データエージェント構築のベストプラクティスにある1つ、「**PrepForAI（AIデータスキーマ＋AIインストラクション）** 」を検証しました。  
適用する前後で、データエージェントの回答がどのように変化するか確認します。

<https://learn.microsoft.com/ja-jp/fabric/data-science/semantic-model-best-practices>

以下、主な検証環境です。

* サンプルデータ：[Fabricオントロジーチュートリアル](https://learn.microsoft.com/ja-jp/fabric/iq/ontology/tutorial-0-introduction?pivots=semantic-model)のアイスクリーム小売販売データ
* **セマンティックモデル**：`sm_ontology_sales`（4テーブル、7メジャー）
* **データエージェント**：`da_retail_sm`（`sm_ontology_sales`をデータソースとして設定済み）

セマンティックモデルのテーブル構成は以下の通り。

| テーブル | 内容 |
| --- | --- |
| dimproducts | 商品マスタ（Category、Subcategory、Brand、ProductName） |
| dimstore | 店舗マスタ（StoreName、City、Region） |
| factsales | 売上トランザクション（SaleDate、RevenueUSD、Units） |
| freezer | フリーザー機器マスタ（今回のスコープ外） |

![](https://static.zenn.studio/user-upload/088f501ba701-20260429.png)

## Before：PrepForAI適用前の回答

まず、PrepForAIを何も設定していない状態でデータエージェントに質問を投げました。

**Q.1店舗あたりの平均売上はいくらですか？**

> 1店舗あたりの平均売上は$285.00です。

生成されたDAXは以下の通りです。

```
EVALUATE
  ROW(
    "Total Revenue (USD)", [Revenue (USD)],
    "Store Count", [Store Count],
    "Revenue per Store (USD)", [Revenue per Store (USD)]
  )
```

「1店舗あたりの平均売上」だけを聞いているにもかかわらず、合計売上・店舗数・1店舗あたり売上の**3列を返しています**。  
AIがどのメジャーを使うべきか迷った結果、関連しそうなメジャーをまとめて返したと考えられます。

## PrepForAI設定内容

ここからPrepForAIを適用するため、PowerBIの画面から2つの設定を行いました。

![](https://static.zenn.studio/user-upload/08ee71476a98-20260429.png)

### 1. AIデータスキーマ

まず、AIデータスキーマです。  
AIデータ スキーマを使用すると、AI の優先順位付けに焦点を当てたモデルのサブセットを定義できます。設定にするにあたっての方針は以下の通りです。

1. **あいまいさが制限されたクリーンな列に優先順位を付ける**
2. **Copilotの混乱を招く可能性のあるフィールドを削除する**
3. **リレーションシップは、AIデータスキーマの設定に関係なく引き続き尊重される（不要）**

つまり、JoinキーをOFFにしてもテーブル間の結合はAIが利用できるため、積極的に除外してOKです。今回の設定方針は以下の通りです。

| テーブル/列 | 設定 | 理由 |
| --- | --- | --- |
| dimproducts / ProductId | ❌ OFF | Joinキーは不要 |
| dimstore / Latitude・Longitude | ❌ OFF | 座標値はAIが誤用しやすい可能性がある |
| dimstore / StoreId | ❌ OFF | Joinキーは不要 |
| factsales / ProductId・StoreId | ❌ OFF | Joinキーは不要 |
| freezer（テーブルごと） | ❌ OFF | スコープ外 |
| 上記以外 | ✅ ON | 分析に必要な列・メジャー |

![](https://static.zenn.studio/user-upload/e9b9cf44e833-20260429.png)

<https://learn.microsoft.com/ja-jp/fabric/data-science/semantic-model-best-practices#ai-data-schemas>

### 2. AIインストラクション

次にAIへの指示（AIインストラクション）です。  
AIインストラクションを設定することで、セマンティックモデルに関するコンテキスト、ビジネスロジック、ガイダンスを直接提供できます。  
設定にするにあたっての方針は以下の通りです。

1. ビジネス用語を明確にする
2. 分析アプローチをガイドする
3. 同じモデルを使うレポート全体で、より意味のある分析情報を提供できるようにする

今回はメジャーの使い分けとスコープを以下のように明示しました。

```
このセマンティックモデルは、アイスクリームの小売販売データを管理するモデルです。

## テーブル構成
- dimproducts: 商品マスタ。Category（大分類）、Subcategory（小分類）、Brand、ProductNameで商品を識別する
- dimstore: 店舗マスタ。StoreName、City、Regionで店舗を識別する
- factsales: 売上トランザクション。SaleDateごとの販売数量（Units）と売上金額（RevenueUSD）を記録する

## メジャーの使い分け
- 売上金額を聞かれた場合は Revenue (USD) を使用する
- 店舗数を聞かれた場合は Store Count を使用する
- 商品数を聞かれた場合は Product Count を使用する
- 1店舗あたりの売上を聞かれた場合は Revenue per Store (USD) を使用する

## 注意事項
- 地理情報（緯度・経度）は分析に使用しない
- freezerテーブルは本モデルのスコープ外のため使用しない
```

![](https://static.zenn.studio/user-upload/b84cfcf55deb-20260429.png)

<https://learn.microsoft.com/ja-jp/fabric/data-science/semantic-model-best-practices#ai-instructions>

### 3. 補足

#### 「DAX式をCopilotと共有する」

上記2点の設定に加え、PrepForAIの「設定」タブにある「DAX式をCopilotと共有する」を有効化しています。  
これにより、モデル内のメジャーのDAX式をCopilotが読み取れるようになります。各メジャーの計算ロジックをAIが把握した上でDAXを生成できるため、より正確な回答が期待できると思われます。  
（読み取りアクセスを持つユーザーにはDAX式が表示される点には注意が必要です）

![](https://static.zenn.studio/user-upload/7454aabe35ee-20260429.png)

#### 「検証済みの回答（Verified Answers）」

PrepForAIにはAIデータスキーマ・AIインストラクションのほかに、「検証済みの回答（Verified Answers）」 という機能もあります。  
検証済みの回答とは、特定のフレーズがトリガーとなる、モデル作成者が承認した視覚的な回答です。一般的または複雑な質問に対して一貫性のある信頼性の高い回答を提供できます。  
今回は即効性を重視したかったので、スコープを絞り省略しています。

![](https://static.zenn.studio/user-upload/f6abe65d5075-20260429.png)

## After：PrepForAI適用後の回答

ここまでを設定し、更新・反映した上で、先ほどと同じ質問を投げてみます。

**Q. 1店舗あたりの平均売上はいくらですか？**

> 1店舗あたりの平均売上は$285.00です。

```
EVALUATE
  ROW(
    "Average Revenue per Store (USD)",
    [Revenue per Store (USD)]
  )
```

Beforeと比較すると、**`Revenue per Store (USD)` の1メジャーのみを使った回答に変化しました**。  
数値の精度はBeforeから正確でしたが、**DAXの構造がよりシンプルかつ意図に忠実になりました**。

## まとめ

今回の検証結果まとめです。

* PrepForAIは**PowerBIのセマンティックモデル編集ページから設定可能**
* 小規模モデルでも**DAX構造がシンプルになる**など効果は確認できた
* **おそらく本領発揮は複雑なモデル・あいまいな質問**のケース
* 設定はセマンティックモデルに保存されるため、**同じモデルを使うすべてのデータエージェント・Copilotに自動で反映**される

PrepForAIはCopilotとデータエージェントの両方に効くため、データエージェントで使わないとしても、設定しておく価値は高いと思いました。

今回のサンプルは小規模モデル（4テーブル・7メジャー）だったため、Beforeの時点でも数値精度は高い状態でした。PrepForAIの効果がより顕著に現れるのは以下のようなケースと考えられます。

**1. メジャーが多い大規模モデル**  
**2. 似た名前のメジャーが複数ある場合**  
**3. あいまいな質問への対応**  
**4. 複数データソースをまたぐエージェント**

実務のモデルほど複雑になりやすく、PrepForAIの効果が出やすい条件が揃いやすいと思われます。セマンティックモデルを本番運用する際には、どちらにせよ早めに設定しておくほうがいいかもしれません。

#### 参考リンク

<https://learn.microsoft.com/ja-jp/fabric/data-science/semantic-model-best-practices>

<https://learn.microsoft.com/ja-jp/power-bi/create-reports/copilot-prepare-data-ai>

<https://learn.microsoft.com/ja-jp/power-bi/create-reports/copilot-prepare-data-ai-data-schema>

<https://learn.microsoft.com/ja-jp/power-bi/create-reports/copilot-prepare-data-ai-instructions>
