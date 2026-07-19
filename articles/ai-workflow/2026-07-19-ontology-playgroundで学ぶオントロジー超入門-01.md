---
id: "2026-07-19-ontology-playgroundで学ぶオントロジー超入門-01"
title: "Ontology Playgroundで学ぶオントロジー超入門"
url: "https://zenn.dev/mm_ai/articles/ontology-playground-ai-agent-intro"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "LLM", "Python", "zenn"]
date_published: "2026-07-19"
date_collected: "2026-07-20"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIエージェントは一般的な知識は豊富でも、社内固有の情報に関する知識がありません。例えば、「備品を購入するので購買申請を起票して、部門長の承認後に発注して」と頼んだとした場合、購買申請とはどのシステムのどの申請なのか、部門長とは誰なのか、金額によって決裁者が変わるのか、といったことは会社ごとに異なります。これらはLLMが一般知識として持っていない情報です。

AIエージェントに情報を渡す技術はいくつかありますが、今回扱う「オントロジー」は用語の意味や用語同士の関係を整理する技術です。

オントロジーは少々理解が難しいのですが、Microsoftが最近公開した[Ontology Playground](https://github.com/microsoft/Ontology-Playground)を使うと、GUIでグラフが表示され理解しやすいので、さっそく試してみました。

自分はオントロジーについて、G検定の勉強で少し見たことがある程度なので、本記事は初学者の学習体験記としてみていただければと思います。

## この記事の内容

* AIエージェントと社内知識の問題
* オントロジーの超基本
* RDF、OWL、Fabric IQとの関係
* Ontology Playgroundの学習コンテンツを試した結果

確認日は2026年7月19日です。Ontology PlaygroundはPreview段階のため、今後、画面や機能、用語が変わる可能性があります。

## Ontology Playgroundとは？

Microsoft公式のGitHub組織で公開されている、オントロジーで使われる概念や設計パターンとMicrosoft Fabric IQを学ぶための無料・オープンソースのWebアプリです。

[公式README](https://github.com/microsoft/Ontology-Playground#readme)によると、主な機能は次のとおりです。

* オントロジーをノードとエッジのグラフとして探索する
* Catalogueから、業種別のサンプルを読み込む
* Visual Ontology Designerで、EntityやRelationshipを視覚的に設計する
* RDF/XMLをインポート／エクスポートする
* Ontology Schoolの記事やクイズで段階的に学ぶ
* 自然言語の質問がEntityやRelationshipへどう対応するかを試す
* 作成したオントロジーをGitHubのPull RequestとしてCatalogueへ投稿する

今回は体験が目的なので、GitHubリポジトリのcloneやNode.jsを使ったローカルインストールはせずに、公開Web版をブラウザーで利用します。

![Ontology Playgroundのデフォルト画面](https://static.zenn.studio/user-upload/deployed-images/bc5729da8388927d3a7f4bb9.png?sha=5c84109585a08ac0f5118a4667ca5c26f11b6125)  
*Ontology Playgroundのデフォルト画面（2026年7月19日確認）*

デフォルトでは、コーヒーショップチェーンを題材にした「Fourth Coffee」のオントロジーが表示されます。画面中央にはCustomer、Order、Product、Store、Supplier、Shipmentといった概念と関係のグラフがあります。左側には学習用のQuest、右側にはEntityやRelationshipの検索欄と詳細パネルが並んでいます。

画面右下にある「Inspector」は、グラフ上で選択したEntityやRelationshipについて、Propertyの型、Identifier、説明、Cardinalityなどを見るための詳細パネルです。（定義の不備を検査するValidationとは別の役割です）

## AIエージェントは社内の「当たり前」を知らない

AIエージェントが社内の作業でつまずく理由を、次の依頼で考えてみます。

> A案件の見積額が50万円を超えたので、購買申請を起票して決裁ルートに回してください。

この一文だけでもAIエージェントには分からないことがいくつもあります。

* 「A案件」は、どの顧客、部門、予算と結び付いているのか
* 「購買申請」は、どのシステムのどの申請種別なのか
* 「50万円を超える」と、承認者や必要書類がどう変わるのか
* 「決裁ルート」には、誰がどの順番で含まれるのか
* 見積書、申請、発注、検収は、どのような順序と関係なのか

プロンプトへ毎回すべてを書くこともできますが、用語や手続きが増えるほど管理が難しくなります。また、同じ「案件」という言葉でも、営業部門と開発部門で指すものが違うかもしれません。では、どうすればAIエージェントが迷わずに済むのでしょうか。

### 対策1：RAG～必要な文書を見つける技術

RAG（Retrieval-Augmented Generation）は、質問に関係する社内規程、マニュアル、過去事例などを検索し、その内容をLLMへ渡すために使えます。RAGはよく使われる技術ですが、もし複数の文書で表記が揺れていたり、用語同士の関係が明示されていなかったりすると、検索結果だけから一貫した解釈を作るのが難しいかもしれません。

### 対策2：MCP～社内システムをAIから利用する技術

MCP（Model Context Protocol）は、AIエージェントが外部のデータやツールを利用するための接続方法です。申請システムから申請種別を取得する、現在の承認状況を確認する、権限の範囲内で申請を登録する、といった操作を行いたいときに役立ちます。

MCPを使うことでAIエージェントが外部のデータやツールの利用で迷う場面は減ると思われますが、業務上の意味を理解して正しく使えることとは別です。「購買申請」と「発注」の違いや、どの条件でどの操作を選ぶかは、別途エージェントへ伝える必要があります。

### 対策3：用語の意味と関係を共有する―オントロジー

オントロジーは、ある分野に登場する概念、その性質、概念同士の関係を、コンピューターでも扱える形で定義します。社内用語の辞書へ関係図を加えた「意味の地図」に近いものといえます。

```
Employee -- submits --> PurchaseRequest
PurchaseRequest -- belongsTo --> Project
PurchaseRequest -- requiresApprovalFrom --> Approver
PurchaseRequest -- resultsIn --> PurchaseOrder
```

「申請」「案件」「承認者」「発注」という言葉を個別に説明するだけでなく、それらがどうつながるのかも明示します。これにより、たとえば申請をあげた人の承認者は誰になるのか（〇〇さんの上長は誰？）といった情報をAIエージェントに明確に伝えることができるようになります。

これはRAGやMCPだけで実現するのが難しい内容で、オントロジーがAIエージェントにとって有用であることがわかります。ただオントロジーだけで全部解決できるわけではなく、データベースなどとの組み合わせが必要になります。

## そもそもオントロジーとは

[Ontology Fundamentalsの最初の記事](https://github.com/microsoft/Ontology-Playground/blob/main/content/learn/ontology-fundamentals/01-what-is-an-ontology.md)では、オントロジーを、ある領域に存在するものの種類と、それらが互いにどう関係するかを形式的に記述する方法と説明しています。個々のデータそのものというより、データの形と意味を表す設計図です。

初学者向けのザックリ理解：

> オントロジーは、ある分野で使う「もの」「性質」「つながり」を、機械にも読めるように整理した意味の地図。

### 架空の社内申請を例に考える

購買申請を題材にすると、例えば次のような地図を作れます。

ここでは、社員、購買申請、部門、承認者が「ものの種類」です。社員が申請する、社員が部門に所属する、申請が承認を必要とする、といった線が「関係」です。

### オントロジーの構成要素～Entity、Property、Relationship

Ontology Playgroundで最低限押さえる要素を整理すると、次のようになります。

| 要素 | 意味 | 購買申請の例 |
| --- | --- | --- |
| Entity type | ものの種類、業務上の概念 | `Employee`、`PurchaseRequest` |
| Property | Entityが持つ値や性質 | `employeeId`、`amount`、`submittedAt` |
| Relationship | Entity同士の意味のある関係 | `submits`、`belongsTo` |
| Identifier | 個々のEntityを一意に見分けるProperty | `employeeId`、`requestId` |
| Cardinality | Relationshipが何対何で成り立つか | 社員1人が複数の申請を出す |

Relationshipの名前には、`owns`、`places`、`belongsTo`のような動詞を使います。すると、グラフを文章として読めます。

```
Customer -- places --> Order
顧客が注文を行う
```

Cardinality（カーディナリティ、基数、多重度）は、その関係が1対1、1対多、多対1、多対多のどれなのかを表します。

```
Customer -- places [one-to-many] --> Order
1人の顧客は複数の注文を行う
```

Relationshipの向きを逆にすれば、自然な動詞とCardinalityも変わります。例えば`Employee -- belongsTo [many-to-one] --> Department`を逆から表すなら、`Department -- employs [one-to-many] --> Employee`のようになります。

## オントロジーを作るための道具～RDFとOWL

ここまで見てきたように、オントロジーは「意味の地図」ではあるのですが、これは概念的なもので、地図をどう描いてコンピュータが理解できるようにするか？という実際の手段が欠けています。

この「意味の地図」を現実の形にする手段がRDFとOWLです。[2番目の記事](https://github.com/microsoft/Ontology-Playground/blob/main/content/learn/ontology-fundamentals/02-understanding-rdf-and-owl.md)で解説されています。

### RDF(Resource Description Framework)

設計図を現実の形にするための一番ベースになる材料です。「主語・述語・目的語」というパーツを使って、実際にデータを繋ぎ合わせるために使います。

```
Customer -- places --> Order
Order -- contains --> Product
```

これは英語の語順と同じですね。日本語の「主語・目的語・述語」とは順番が異なります。

### OWL(Web Ontology Language)

RDFを基数制約、クラス階層、論理公理など、より豊かなモデリングで拡張します。本来なら略称は「WOL」になるはずですが、「知性の象徴であるフクロウ（Owl）」にあやかって、あえて文字を入れ替えて OWL と名付けられたそうです。

#### 実際のOWLを見てみる

教材にはOWLの最小サンプルが入っています。本体の一部を抜き出すと次のようになります。

```
<owl:Class rdf:about="Product">
  <rdfs:label>Product</rdfs:label>
</owl:Class>

<owl:DatatypeProperty rdf:about="productName">
  <rdfs:domain rdf:resource="Product"/>
  <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
  <rdfs:label>productName</rdfs:label>
</owl:DatatypeProperty>
```

ここでは、`Product`をOWLのクラスとして宣言し、`productName`を文字列値を持つDatatype Propertyとして宣言しています。`rdfs:domain`は`productName`を`Product`へ、`rdfs:range`は値を文字列型へ結び付けています。

## Fabric IQでオントロジーを使う

Fabric IQはRDF/OWLなどの考え方をベースに、Microsoftのクラウド上で誰もがクリック操作やAIで簡単に使えるようにパッケージングした「製品」です。

[3番目の記事](https://github.com/microsoft/Ontology-Playground/blob/main/content/learn/ontology-fundamentals/03-fabric-iq-ontology-concepts.md)では、ここまでに出てきた要素が、自然言語の質問を業務データへ結び付けるためにどのようにFabric IQで使われるかが分かります。

教材では、Fabric IQがオントロジーを読み、自然言語の質問をSQLへ変換すると説明しています。例えば「先月の地域別売上合計は？」という質問へ答えるには、少なくとも次のことを知る必要があります。

```
Order.totalAmount
Order.date
Order -- placedAt --> Store
Store -- locatedIn --> Region
```

オントロジーを使うことで、`Order`、`Store`、`Region`が何を意味し、どのPropertyを持ち、どのRelationshipでつながるかが分かるので、利用者が実際のテーブル名や列名を知らなくても、質問から必要なデータをたどりやすくなります。

| 項目 | Fabric IQが知りたいこと |
| --- | --- |
| Entity type | `Customer`、`Order`、`Store`とは何か |
| Property | 日付、金額、地域などをどこから得るか |
| Relationship | Entity同士をどの経路でたどるか |
| Cardinality | 1対1、1対多など、何件ずつ対応するか |
| Identifier | 各Entityを何で一意に見分けるか |

CardinalityとIdentifierは、正しい`JOIN`、`COUNT`、`GROUP BY`を考える手掛かりになります。例えば`Customer -- places [one-to-many] --> Order`と分かれば、「顧客ごとの注文数」は複数になり得る一方、1件の注文に対応する顧客は通常1人だと判断できます。

## Ontology Fundamentalsの概念編まとめ

ここまでの理解を一言ずつまとめると、次のようになります。

```
オントロジー = 業務用語の共通辞書に、関係図を加えた意味の地図
RDF           = その関係をトリプルのグラフとして表すモデル
OWL           = クラス、プロパティ、制約などを定義する言語
Fabric IQ     = その意味をデータ、質問、AIエージェントへつなぐFabricの仕組み
```

## 学習コンテンツを体験してみた

ここからは、ブラウザー版のOntology Playgroundで実際にグラフを操作し、学習コンテンツを進めていきます。

### Library Systemをゼロから作る

[Building Your First Ontology](https://github.com/microsoft/Ontology-Playground/blob/main/content/learn/ontology-fundamentals/04-building-your-first-ontology.md)に従い、最初のオントロジーを作ります。題材は図書館です。`Book`、`Author`、`Member`という3種類のEntity typeを作り、2種類のRelationshipでつなぎます。

#### Designerを開く

Playground上部のペン先のようなアイコンがDesignerです。ここをクリックすると、オントロジーを視覚的に作る画面が開きます。

![上部メニューにあるDesignerボタン](https://static.zenn.studio/user-upload/deployed-images/f056b010daf4aec10d073249.png?sha=f7bad961ac95bed0a907d64a24be987d72975cd5)  
*上部メニューのDesignerボタン*

Designerは、左側の入力フォームと右側のグラフプレビューに分かれています。EntityやRelationshipを追加すると、グラフがその場で更新されます。

続いて上部の`New`をクリックして白紙のキャンバスを開きます。

![Designer上部のツールバー](https://static.zenn.studio/user-upload/deployed-images/aea26c30560aa7b6e2afc586.png?sha=b866425f9fa81152806ab753b4ba3338c07fd03f)  
*Designer上部のツールバー*

#### Book、Author、Memberを作る

最初に`Book`を作ります。Propertyは教材の指定どおり、次の3つです。

| Property | 型 | Identifier |
| --- | --- | --- |
| `isbn` | string | Yes |
| `title` | string | No |
| `publishedYear` | integer | No |

Identifierに指定したPropertyには、黄色い鍵のアイコンが付きます。`Book`そのものを表すアイコンは見当たらなかったため、近そうな本棚のアイコンを選びました。こうした表示上の選択も、GUIなら結果を見ながら決められます。

![BookのEntity typeとProperty設定](https://static.zenn.studio/user-upload/deployed-images/12d5bdd90b348d7e1f1bd4ca.png?sha=e9ec325469b91f0fffcb1fae2e63dd3a70315951)  
*Bookを作成。isbnをIdentifierに設定した*

同様に`Author`も作ります。

| Property | 型 | Identifier |
| --- | --- | --- |
| `authorId` | string | Yes |
| `name` | string | No |
| `nationality` | string | No |

![AuthorのEntity typeとProperty設定](https://static.zenn.studio/user-upload/deployed-images/59d8a7d22d0aae919c295248.png?sha=61bd6f75b1b905b6d019630a7e856a5894d93a99)  
*Authorを作成。authorIdをIdentifierに設定した*

3つ目は`Member`です。

| Property | 型 | Identifier |
| --- | --- | --- |
| `memberId` | string | Yes |
| `name` | string | No |
| `joinDate` | date | No |

![MemberのEntity typeとProperty設定](https://static.zenn.studio/user-upload/deployed-images/3e103a8b23ae76591692a58e.png?sha=c5412fff424b1cc12c4d3dc13ca657604793db26)  
*Memberを作成。joinDateにはdate型を選んだ*

3つのEntity typeを作ると、右側のキャンバスに青、緑、紫の丸が表示されました。ただし、この段階ではまだ3つの丸が重なっているだけです。Entity同士の関係を定義していないため、線は1本もありません。

![Relationshipを定義する前の3つのEntity](https://static.zenn.studio/user-upload/deployed-images/d7b5ffec53b49ed2f97f09cc.png?sha=28957ebc895263c24a7d1529ecc58fb2f56a7082)  
*Book、Author、Memberを作成した直後。まだRelationshipがない*

#### Relationshipを定義する

次に、Entity同士をRelationshipでつなぎます。

1つ目は「本は著者によって書かれる」という関係です。名前を`writtenBy`、向きを`Book → Author`としました。複数の本が同じ著者に対応し、教材では各Bookに1人の主著者がいるものとしているため、Cardinalityは`N:1`です。

![BookからAuthorへのwrittenBy関係](https://static.zenn.studio/user-upload/deployed-images/faa1ca1045062cd04a4857bf.png?sha=2c623e08afc6538191adcc5c01e01f2b5e092f1c)  
*writtenByはBookからAuthorへのN:1*

2つ目は「本は会員によって借りられる」という`borrowedBy`です。1冊の本は時間をまたいで複数の会員に借りられ、1人の会員も複数の本を借りられるため、教材どおり`Book → Member`の`N:N`にしました。

![BookからMemberへのborrowedBy関係](https://static.zenn.studio/user-upload/deployed-images/b03164ea323b14e4f0d9ec9c.png?sha=b51493b761f0066ebc24db6453d495115cbe4438)  
*borrowedByはBookからMemberへのN:N*

Relationshipを追加すると、重なっていた3つの丸が並び、矢印と`writtenBy`、`borrowedBy`のラベルが表示されました。フォームで選んだ内容がすぐ図になるため、向きや名前の間違いにも気付きやすそうです。

![完成したLibrary ontologyのDesigner画面](https://static.zenn.studio/user-upload/deployed-images/7ea4c83d5a5a6c0bf62cd1cd.png?sha=01065168e19b8ace34af7c4a8901039c5e72bc0c)  
*Bookを中心に、MemberとAuthorがRelationshipでつながった*

#### Validateで定義を確認する

EntityとRelationshipを作り終えたら、上部の`Validate`をクリックします。

![DesignerのValidateボタン](https://static.zenn.studio/user-upload/deployed-images/850095a21038f05dc58b7589.png?sha=e3b154bd21f4e0e7d650e5e8925f87c82b2620a7)  
*Validateをクリックして定義を検査する*

今回は緑色の`No issues found`が表示されました。

![Validationに成功してNo issues foundと表示された画面](https://static.zenn.studio/user-upload/deployed-images/e7f6fac0c36762f4a4033254.png?sha=eb446bb86b0b7ba3dddf2643250e4870513d2b65)  
*問題がなければ緑色のチェックマークで知らせてくれる*

教材によると、Validationでは少なくとも、各EntityにIdentifierがあるか、Relationshipの参照先が存在するか、IDが重複していないかを確認します。Inspectorが定義内容を見る詳細パネルだったのに対し、Validationは定義の問題を検査する機能です。

#### RDFを確認してExportする

右側のプレビューを`Graph`タブから`RDF`タブへ切り替えると、作成したオントロジーのRDF/OWLが構文ハイライト付きで表示されます。正直なところ、ここまで学んだ後でも、生成されたRDF/XMLを眺めただけでは内容をすぐ理解するのは難しいです。

完成した内容は`Export RDF`から`.rdf`ファイルとしてダウンロードできます。教材には、RDFのダウンロード、Catalogueへの投稿、JSONのコピーという3つの出力方法が書かれていますが、2026年7月19日に公開Web版で確認したDesignerには、`Copy JSON`に相当するメニューは見当たりませんでした。Preview中の教材と実装の差かもしれません。

#### 最初のオントロジーを作ってみた感想

これで最初のハンズオンは完了です。

RDF/XMLを最初から直接書くように言われていたら、途中で挫折していたと思います。Designerでは、Entity名、Propertyの型、Identifier、Relationshipの向き、Cardinalityをフォームで選ぶと、結果がリアルタイムにグラフへ反映されます。RDF/OWLを意識しなくても、まず「何があり、何を持ち、どうつながるか」というモデリングに集中でき、Validationを通してRDFとして出力するところまで、迷子にならず進められました。Ontology Playgroundの一番分かりやすい価値は、この「RDFを直接書かずに、意味の地図を作って確認できること」かもしれません。

今回作ったLibrary ontologyは非常に単純ですが、社内用語へ置き換えれば、`Employee`、`Department`、`PurchaseRequest`などを同じ手順で定義できそうだ、という感覚はつかめます。

### Ontology Design Patterns―コンピューターを迷わせない設計

[Ontology Design Patterns](https://github.com/microsoft/Ontology-Playground/blob/main/content/learn/ontology-fundamentals/05-ontology-design-patterns.md)にはオントロジーを作るうえでの注意点がまとめられています。

AIエージェントに理解してもらうための指南書のようなものです。Pythonなどでプログラミングをしている人なら、変数名や関数名を分かりやすくする、1つのクラスへ役割を詰め込みすぎない、といった設計と似ているため理解しやすいと思います。

#### 1. 名前は人間が読んで分かるようにする

Entity type、Property、Relationshipは、人間が読んで意味を推測できる名前にします。意味を省略した`qty`、`amt`、`dt`、何を指すか分からない`Item`、`Record`、`Thing`などは避けるようにします。

これは、Pythonで`x`や`data2`よりも`total_amount`や`approved_requests`と書くほうが理解しやすいのと同じです。特にオントロジーでは、名前が自然言語の質問を解釈する手掛かりにもなります。

#### 2. 1つのEntityには1つの概念を持たせる

1つのEntity typeへ関係のないPropertyを詰め込まないようにします。

教材では、次のような`Person`をアンチパターンとして挙げています。

```
Person
├─ salary
├─ patientId
├─ courseGrade
└─ accountBalance
```

給与を持つ従業員、患者番号を持つ患者、成績を持つ学生、口座残高を持つ顧客という、異なる4つの概念が`Person`へ押し込まれています。この場合は`Employee`、`Patient`、`Student`、`Customer`へ分け、必要なら共通の`Person`とRelationshipでつなぎます。

プログラミングでいえば、あらゆる処理を1つの巨大クラスへ詰め込む「God Object」を避け、クラスの責務を分ける考え方に近いです。

#### 3. Identifierは一意で、安定したものを選ぶ

Identifierは、Entityの各インスタンスを数え、グループ化し、結合するときの基準です。教材では、よいIdentifierの条件を次のように説明しています。

* すべてのインスタンスの中で一意である
* 時間がたっても変わらない
* できれば業務上意味のあるキーである
* 複数項目を組み合わせた複合Identifierを避ける

例として、Bookの`isbn`、Userの`email`、Orderの`orderId`が挙げられています。

Identifierは、例をそのまま使うのではなく、対象範囲に合わせて考える必要があります。メールアドレスは変更や再利用の可能性があります。またISBNが識別するのは書籍の版であり、図書館が所有する物理的な1冊ごとの蔵書ではありません。個々の蔵書を管理するなら、`BookCopy`と`copyId`や管理用バーコードが必要になるかもしれません。

「業務上意味があること」と「絶対に変わらないこと」が両立しない場合もあります。実際の設計では、どの範囲で一意なのか、将来変更されないか、別システムとも共有できるかを確認する必要があります。

#### 4. 外部キーではなく、関係の意味をモデル化する

リレーショナルデータベースでは、外部キーを使ってテーブルを結びます。オントロジーでは、その接続が業務上何を意味するのかを、名前付きのRelationshipとして表します。

| リレーショナルDBの表現 | オントロジーの表現 |
| --- | --- |
| `orders.customer_id → customers.id` | `Order → placedBy → Customer` |
| `order_items.product_id → products.id` | `OrderItem → contains → Product` |

`fk_cust_id`では「つながっている」ことしか分かりません。`placedBy`なら、「注文は顧客によって行われる」と読めます。Relationshipは単なる線ではなく、2つの概念を結ぶ動詞であることに留意しましょう。

#### 5. Cardinalityは脳内シミュレーションして確認する

Cardinalityを間違えると、件数や集計結果も間違う可能性があります。教材では、次の問いを使うよう勧めています。

> Aのインスタンスが1つあるとき、対応するBはいくつ存在できるか？

例えば、次のように考えます。

* 1人の顧客は複数の注文を行える：one-to-many
* 複数の注文が1つの店舗で行われる：many-to-one
* 学生は複数の科目を履修し、科目にも複数の学生がいる：many-to-many

Relationshipの向きに合わせて、「1人のCustomerが複数のOrderをplacesする」のように脳内でシミュレーションすると、動詞とCardinalityの不整合に気付きやすくなります。実際に紙に書いてみるのも有効かもしれません。

#### 6. 名前だけで足りないときはDescriptionを書く

Entity type、Property、RelationshipにはDescriptionを付けられます。例えば`approvalStatus`だけでなく、「購買申請の現在状態。draft、submitted、approved、rejectedのいずれか」と説明すれば、人間にもAIにも解釈しやすくなります。

## AIエージェントにどう役立ちそうか

最初に触れた社内の購買申請へ置き換えると、オントロジーには次のような役割を期待できます。

* `Employee`、`Department`、`PurchaseRequest`、`Approver`といった社内概念を定義する
* `submits`、`belongsTo`、`requiresApprovalFrom`など、概念同士の関係を明示する
* `requestId`、`amount`、`approvalStatus`などのPropertyと型を定義する
* 1人の社員が複数の申請を出せる、といったCardinalityを定義する
* 略語や社内固有語へDescriptionを付ける

こうした意味の地図があれば、AIエージェントは、単に似た単語を探すだけでなく、「申請者が所属する部門をたどり、その部門の承認者を調べる」といった関係に沿って情報を探しやすくなります。また、同じ用語を人、データ基盤、複数のAIエージェントで共有できるため、システムごとに解釈がずれる問題も減らせそうです。

### RAG、オントロジー、MCPを組み合わせる

冒頭で挙げた購買申請をAIエージェントに任せるなら、3つの技術は次のように分担できると思います。

| 技術 | 主な役割 | 購買申請の例 |
| --- | --- | --- |
| RAG | 文書から根拠や手順を探す | 購買規程から、金額別の承認条件や必要書類を取得する |
| オントロジー | 用語の意味と関係を共有する | 申請者、部門、承認者、案件、申請の関係をたどる |
| MCP | データやツールへ接続する | 申請システムを検索し、権限の範囲内で申請を登録する |

例えば「50万円を超える備品購入を申請して」と頼まれた場合、AIエージェントは次のように動くイメージです。

1. RAGで購買規程を検索し、50万円を超える場合の条件を確認する
2. オントロジーに基づいて、申請者の所属部門、案件、必要な承認者の関係を解釈する
3. データベースから、実際の部門や承認者を取得する
4. MCP経由で申請システムを操作する
5. 実行前に権限と入力内容を確認し、必要なら人へ承認を求める

この役割分担なら、RAGへすべてを詰め込むことも、MCPで接続したツールの説明だけに業務判断を任せることもありません。オントロジーが、文書に書かれたルールと、システムに保存されたデータの間をつなぐ共通語彙になります。

### オントロジーもメンテが必要

もしRelationshipの向きやCardinalityを間違えれば、AIエージェントも誤った関係を前提に判断する可能性があります。組織変更で部門や承認ルートが変われば、定義や実データも更新しなければなりません。また、権限管理、処理の実行、例外への対応、最新規程の確認などは、オントロジーだけでは解決できません。特に社内手続きでは、AIエージェントが実行できる範囲と、人の承認が必要な範囲を別途設計する必要があります。

## まとめ

オントロジーは、ある分野の「もの」「性質」「つながり」を機械にも読めるように整理した、意味の地図です。

RDFやOWLのコードは初見では難しいのですが、Ontology PlaygroundではGUIで捜査した結果がリアルタイムにグラフへ反映されるので、初心者でも白紙の状態からオントロジーを実際に作るところまで進められました。オントロジーをゼロから学ぶためのよい入口だと思います。

## 参考資料
