---
id: "2026-06-18-power-biをmcpサーバーなしでclaudeに操作させる-01"
title: "Power BIをMCPサーバーなしでClaudeに操作させる"
url: "https://qiita.com/ktdatascience/items/5456cbc1e91b305d6449"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "qiita"]
date_published: "2026-06-18"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

## はじめに
 
Power BIをAIに作らせる、というと「専用のMCPサーバーを立てて、Power BIをツール越しに操作する」イメージを持っていませんか。私もそう思い込んでいました。でも実際にやってみたら、自分の用途ではMCPサーバーは要りませんでした。理由はシンプルで、`.pbip` というファイル形式の中身がただのテキストだからです。
 
公式の「Power BI Modeling MCP」も調べました。こちらはコミットがREADMEくらいしか更新されておらず、個人的にはMicrosoftも開発に力を入れていないし、出来ることも限定的で私の用途では使えませんでした。
 
https://github.com/microsoft/powerbi-modeling-mcp
 
この記事は、`.pbix` と `.pbip` の違いを腹落ちさせたうえで、Claudeに `.pbip` を直接書かせてPower BIを組んだときの記録です。Power BIは触るけれどGitやコードはちょっと苦手、という人を想定して書いています。
 
:::note info
読了の目安は7〜8分。先に結論だけ言うと「`.pbip` はテキスト（設計図）なので、Claudeに書かせれば追加のサーバーなしでPower BIが作れる。ただしデータ本体は別途refreshで読み込む」です。
:::
 
## そもそも何がうれしいのか
 
Power BIをAIで生成しようとすると、たいてい「Power BI Desktopをツールから操作する」発想になります。そのためにMCPサーバーやREST APIの口を用意して……と考えると、もう腰が重い。
 
ところが `.pbip` 形式で保存されたPower BIは、レポートもモデルも全部テキストファイルで表現されています。テキストということは、Claudeがそのまま読めて、そのまま書けるということです。つまり余計なサーバーを挟まず、「このフォルダにこういうTMDLとPBIRを置いて」と頼むだけで成立する。ここに気づいたとき、正直「なんだ、それでよかったのか」と拍子抜けしました。
 
## PBIX と PBIP の違い ─ ポイントは「データ本体を持つかどうか」
 
まず土台になる違いを整理します。
 
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3937496/9cc477cc-687a-4e17-a2a9-5989ec5a26ac.png)
 
[^import]: 正確にはインポートモードの話です。DirectQueryやライブ接続のテーブルは、pbixでもデータ実体は埋め込まず接続情報だけを持ちます。この記事はCSVを取り込むインポートモード前提で書いています。
 
表をひとことに圧縮すると、違いは「データ本体を持つかどうか」に尽きます。
 
`.pbip` は設計図だけです。どのCSVをどう読むか（Mクエリ）、DataFolderパラメーター、リレーション、メジャーの定義しか入っていません。たとえば2万件の売上行そのものは入っておらず、更新（refresh）したとき初めて `data/*.csv` から読み込まれます。だからリポジトリには「答え」であるDAXやMはテキストで入っているのに、データ値そのものは入っていない、という状態になります。
 
一方の `.pbix` は、設計図に加えて「いま読み込み済みのデータのスナップショット」まで丸ごと1ファイルに固めたものです。
 
## .pbip の中身を覗く
 
`.pbip` を保存すると、こんな構成のフォルダができます。
 
```text
MyReport/
├─ MyReport.pbip            ← ただのポインタ（どこを見るかの入口）
├─ MyReport.Report/         ← レポート定義（ページ・ビジュアル）
│   └─ definition/ ...       (PBIR: JSON)
└─ MyReport.SemanticModel/  ← モデル定義
    └─ definition/
        ├─ tables/ ...        (TMDL)
        ├─ relationships.tmdl
        └─ ...
```
 
セマンティックモデルはTMDL（Tabular Model Definition Language）というテキスト形式で書かれます。たとえばメジャーひとつはこんな見た目です。
 
```text:Sales.tmdl
table Sales
	column Amount
		dataType: int64
		sourceColumn: Amount
 
	measure 'Total Sales' = SUM(Sales[Amount])
		formatString: #,0
```
 
そしてデータの読み込み方はMクエリで定義されます。
 
```text:expressions.tmdl
expression DataFolder = "C:\data" meta [IsParameterQuery=true]
 
let
    Source = Csv.Document(File.Contents(DataFolder & "\sales.csv"), [Delimiter=","]),
    Promoted = Table.PromoteHeaders(Source)
in
    Promoted
```
 
実際に生成されるTMDLのパラメーターには `Type` などの注釈が付きますが、ここでは見やすさ優先で簡略化しています。見てのとおり、全部テキストです。`git diff` で差分が見えるし、GitHub上でもそのまま読めます。バイナリの `.pbix` ではこうはいきません。
 
## なぜ「テキストだからClaudeで書ける」のか
 
ここがこの記事の肝です。Claudeのようなテキスト生成AIが得意なのは、まさにこういう構造化テキストの読み書きです。
 
`.pbix` はバイナリなので、Claudeにそのまま渡しても中身を直接は編集できません。じゃあAIでモデルをいじるにはどうするのか——という文脈で出てくるのが、さっきの公式「Power BI Modeling MCP」です。ただ、ここは私も最初に誤解していたのですが、このMCPは「pbixがバイナリだから」必要になるわけではありません。役割は、稼働中のセマンティックモデルに（TOM/XMLA経由で）接続して、テーブルやメジャー、DAXを操作・検証することです。接続先はDesktopでもFabricでも、そして実は `.pbip` ファイルでも構いません。つまりMCPと「pbipをテキストで書く」は、どちらか一方を選ぶものではなく、併用できる関係なんです。
 
その上で、私の用途——モデルやメジャーの定義をまとめて作る・直す——に絞ると、`.pbip` のTMDLもPBIRもMも全部テキストなので、Claudeは普通のソースコードと同じ感覚で生成・編集できます。エンジンに接続してPower BIを"操作"するのではなく、設計図そのものを"執筆"してもらうイメージ。サーバーを用意する前に、まずこっちで十分だった——これが実際に手を動かしてみた率直な感想です。
 
:::note info
用語を整理しておきます。よく混同されますが、TMDL（フォーマットそのもの）がGA（一般提供）になったのは2024年8月です。一方、Power BI Desktop内でTMDLをコードとして編集できる「TMDL view」がGAになったのが2025年9月。"TMDLのGA"と一括りに語られがちですが、対象が別物です。さらに、TMDLとPBIP・Fabric Git連携の統合や、PBIP全体のGAは2026年6月時点でまだ移行の途中です（末尾の注意も参照）。
:::
 
## 実際にClaudeでpbipを書いて動かしてみた
 
私がやった流れはこんな感じです。
 
1. 雛形として、Power BI Desktopで空のレポートを「Power BI プロジェクト（.pbip）」として一度保存する
2. できたフォルダ構成をClaudeに渡して、「このCSVスキーマに対して、TMDLでテーブル・メジャー・リレーションを書いて」と依頼する
3. Claudeが生成したTMDL / Mをフォルダの該当箇所に配置する
4. Power BI Desktopで `.pbip` を開き、データを更新（refresh）する
4番目のrefreshで初めて、`data/sales.csv` の中身（私の場合は売上データ約2万件）がモデルに読み込まれて、ビジュアルに数字が出ます。設計図に血が通う瞬間で、ここはちょっと気持ちよかったです。
 
ポイントは、DataFolderパラメーターを使ってCSVの置き場所を1か所にまとめておくこと。こうしておくと、Claudeが書くMクエリ側はパスをベタ書きせずに済み、環境が変わってもパラメーターだけ直せば動きます。
 
## ハマったポイント
 
正直に書きます。最初の数回は普通に失敗しました。
 
ひとつ目は、データ未読み込みのまま保存してしまった件です。`.pbip` 自体はデータを持たないので困らないのですが、後述する `.pbix` 化のときにこれをやると、空のテーブルがそのまま固定されてしまいます（実際に踏みました）。
 
 
:::note warn
Claudeが生成したTMDL / Mは、必ずPower BI Desktopで開いてrefreshが通るところまで確認してください。テキストとして文法が正しくても、列名やパスがずれていると更新で落ちます。私はここを横着して時間を溶かしました。
:::
 
:::note info
もうひとつ、やってみて分かった肌感です。同じテキストでも、モデル定義（TMDL）に比べてレポート定義（PBIR、中身はJSON）はClaudeに一発で書かせるハードルが上がります。ビジュアルの細かい設定まで含めると記述が長く繊細になるためです。手応えがあったのは主にモデル・メジャー側で、レポートは雛形をDesktopで用意して細部はDesktop側で詰めるのが結局ラクでした。
:::
 
## pbip → pbix の「実体化」とは何か
 
ここで「実体化」という言葉を整理しておきます。`.pbip` を開いてデータを読み込んだ状態で「名前を付けて保存 → `.pbix`」とした瞬間、その時点でメモリに乗っているデータの実体＋レポート＋モデル定義が、すべて1つの `.pbix` に埋め込まれて固定されます。スナップショット化、と言うとしっくりきます。
 
だから順序が大事なんです。保存前にデータを更新して読み込んでおけば、その2万件が `.pbix` の中に入る。逆にデータ未読み込みのまま `.pbix` 保存すると、空のテーブルが実体化してしまう。私が最初にやらかしたのはまさにこれでした。
 
`.pbix` にしてしまえば、CSVが無い別PCに持っていっても、保存時点のデータは表示できます。ただし最新化（refresh）するには元のCSVパスが必要になります。
 
## pbix → pbip に戻せるか
 
戻せます。Power BI Desktopの「名前を付けて保存」で `.pbix` → `.pbip` も可能です。
 
ただし注意があって、`.pbix` に埋め込まれていたデータ本体は `.pbip` 側には保存されません。`.pbip` はあくまで定義だけなので、開いたあとにrefreshが必要になります。ここは「データは戻らない、設計図だけ戻る」と覚えておくと混乱しません。
 
## MCPサーバー方式との比較 ─ どっちを使う？
 
整理するとこうなります。
 
| | .pbip をテキスト生成（今回） | Power BI Modeling MCP |
|---|---|---|
| 追加セットアップ | 不要（Claude＋Desktopだけ） | VS Code拡張 or `npx` で導入（公式・Public Preview） |
| 接続先 | ファイル（PBIP）を直接編集 | 稼働中モデル（Desktop / Fabric / PBIP） |
| 得意なこと | モデル・レポート定義の生成、まとめ書き | 稼働中モデルへの操作・DAX検証・大規模な一括操作 |
| レポート層（ビジュアル等） | PBIRテキストで編集できる | 対象外（モデル操作の口なのでビジュアルは触れない） |
| バージョン管理 | Gitと相性が良い | PBIP経由なら可 |
| 学習コスト | TMDL / PBIRの構造理解が要る | ツールの仕様理解が要る |
 
ここで一点だけ補足を。MCPの基盤になっているモデル操作の口（TOM）は、テーブルやメジャーは変えられてもレポートのビジュアルは変えられません。これはMicrosoft自身のツールも直面している制約で、だからこそレポートまで含めて触りたいときは結局PBIRのテキストを編集する、という流れになります。「モデルはMCP、レポートはPBIRテキスト」と棲み分けるのが現実的です。
 
私の結論は、「モデルやメジャーをまとめて作る・直す」用途なら、`.pbip` をClaudeに書かせる方式が圧倒的に手軽だということです。MCPは稼働中モデルへの一括操作やDAX検証で強いので、用途が分かれます。まずは手元のフォルダで `.pbip` を試してみて、対話的にゴリゴリ直したくなったらMCPを足す——くらいの順番がちょうどいいと思います。
 
## まとめ
 
`.pbix` と `.pbip` の違いは「データ本体を持つかどうか」、これに尽きます。`.pbip` はテキストの設計図だからClaudeがそのまま書けて、自分の用途ならMCPサーバー無しでPower BIが組める。`.pbix` 化はその設計図にデータを焼き込む「実体化」で、戻すときはデータが落ちる ─ この3点が腹落ちすれば、もう怖くないはずです。
 
次は、生成したTMDLをGitに乗せてPRレビューする運用まで試したら、また追記しようと思います。もし同じやり方を試した人がいたら、どこでハマったか教えてください。
 
:::note warn
2026年6月時点の状況です。TMDL（フォーマット）はGA、TMDL viewもGAですが、PBIPやFabric Git連携との統合、PBIP全体のGAは移行途中です。PBIR（新レポート形式）もデフォルト化が進行中で、Power BI Desktopでは順次デフォルトになりつつあります。最新の対応状況は必ず公式ドキュメントとブログで確認してください。
:::
 
## 参考リンク
 
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
 
https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-tmdl-view
 
https://powerbi.microsoft.com/en-us/blog/announcing-general-availability-of-tabular-model-definition-language-tmdl/
 
https://powerbi.microsoft.com/en-us/blog/tmdl-view-generally-available/
 
https://powerbi.microsoft.com/en-us/blog/pbir-will-become-the-default-power-bi-report-format-get-ready-for-the-transition/
