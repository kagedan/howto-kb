---
id: "2026-07-03-claude-codeが書くiacの根拠のない値をsubagentで炙り出す-01"
title: "Claude Codeが書くIaCの「根拠のない値」をSubAgentで炙り出す"
url: "https://zenn.dev/acntechjp/articles/8ef2f6734561f6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

執筆者：Shota Tsutsui

## TL;DR

* Claude CodeにCloudFormationを書かせると「動くけど根拠のない値」が静かに紛れ込む。cfn-lintでは弾けない。
* プロンプトで根拠を求めてもClaudeはアプリ固有の事情を知らないので「一般論」止まりになってしまう。
* レビュー専用のSubAgentに「値の正しさ」ではなく「仕様書(requirements.md)との対応関係」をチェックさせると、根拠が書かれていない値だけを炙り出せる。SubAgentの出力は「この値で合ってる？」ではなく「requirements.mdにこの根拠を追記して」になる。

💡 使用モデル：claude-sonnet-4.6（2026年6月時点）／個人検証。検証範囲はパラメータ設計まわりに限定。

## はじめに

Claude CodeにCloudFormationを書かせていたとき、TargetValue: 70.0（CPU70%でスケールアウト）という値が出てきた。  
一見それっぽいし、動く。  
でも「なぜ70%なのか」と聞いても、はっきりした根拠は返ってこなかった。

AIにIaCを書かせると、こういう 「動くけど根拠のない値」 が静かに紛れ込む。  
構文エラーと違って自動では検出されず、人間のレビューで初めて気づく——あるいは気づかないまま本番に乗る。

しかもインフラはアプリと違い、後から直しづらい設定値が多い。

* 事実上変更不可：VPC / サブネットの CIDR は、変えるなら既存リソースごと作り直し
* 変更コストが高い：DBInstanceClass は再起動かフェイルオーバーが必要。CPU/Memory は「正しい値」を出すのに負荷試験が要る
* 失った分は戻らない：バックアップ保持期間を後から延ばしても、過去分は存在しない
* 気づくのが遅れる：登録解除遅延などは、障害やデプロイ遅延で痛い目を見るまで見直されない

だからインフラこそ最初から根拠を持って決めたい。  
この記事では、その問題を検証し、レビュー専用のSubAgentで「人間がレビューすべき箇所を絞り込む」仕組みを試した内容をまとめる。

### 登場するファイル

| ファイル | 役割 |
| --- | --- |
| docs/requirements.md | 仕様書。構成・実測値・制約など、設計判断の根拠を人間が書き溜めるドキュメント |
| templates/main.yaml | Claudeが生成するCloudFormationテンプレート（インフラ定義の本体） |
| .claude/agents/param-reviewer.md | レビュー専用SubAgentの定義。main.yaml の各値が requirements.md に根拠を持つか照合する |

要件をまとめたファイルをインプットとしてClaude Codeに渡し、CFnのyamlをアウトプットさせるフローの中で、実際にSubAgentを作り、使ってみた。

## Claude Codeに任せてみた

要件ファイルには、手元の実測値や制約を一通り書いた。  
**docs/requirements.md**

![](https://static.zenn.studio/user-upload/8d565001be9d-20260703.png)

※ 一方で、DBスペック・CIDR設計・スケーリング目標値などは**意図的に書いていない**。

このファイルを渡し、docs/requirements.md を読んで templates/main.yaml を作成してください と指示した。

![](https://static.zenn.studio/user-upload/4226c0fc3ffa-20260703.png)

約450行のテンプレートが生成された。

おもしろいのは、**requirements.mdに書いた要件は、Claudeがコメント付きで正しく値に翻訳していた**ことだ。

問題は、**書かなかった値**のほうだ。  
これらはコメントもなく、それっぽいリテラルとして、しれっと埋まっていた（以下の「なぜ？」は生成物のコメントではなく、筆者の疑問）。

> CidrBlock: "10.0.0.0/24" # ← なぜ /24？  
> HealthCheckIntervalSeconds: 10 # ← なぜ10秒間隔？  
> TargetValue: 70.0 # ← なぜCPU70%でスケール？  
> EngineVersion: "8.0.mysql\_aurora.3.04.0" # ← なぜこのバージョン固定？  
> DBInstanceClass: db.r6g.large # ← なぜこのインスタンスクラス？

ぱっと見、完成度は高い。  
要件由来の値にはコメントまで付いていて、なおさら「全部考え抜かれている」ように見える。  
これを見せられたら、レビューでうっかり「OK」と言ってしまいそうだ。  
構文エラーはCIで弾けるが、**「根拠のない値」を弾く仕組みは標準には存在しない**。

## プロンプトで根拠を求めても「一般論」止まり

生成済みのテンプレートに対し、Claude自身に根拠を問い詰めてみた。  
「各値の根拠を、アプリ固有か一般的な慣習かに分けて教えて」

返ってきた回答は見事に二つに分かれた。

* **requirements.mdに書いた値**（応答100ms→HealthCheckTimeoutSeconds:2、RPO24h→DBBackupRetentionDays:1 など）→ 具体的な根拠を提示
* **書かなかった値**（TaskCpu:512、TargetValue:70.0、RetentionInDays:30 など）  
  →「軽量Webアプリの慣習値」「AWS公式が例示する値」といった一般論。  
  さらに AutoScaleMaxCapacity・DBInstanceClass・EngineVersion の3つは、**Claude自身が「根拠なし（要確認）」と認めた**

![](https://static.zenn.studio/user-upload/627b3deb1e62-20260703.png)  
![](https://static.zenn.studio/user-upload/0cf1f8aa875d-20260703.png)

根拠を問い詰めたときのClaudeの回答。要件由来か慣習由来かで明確に二分された。

ここに、プロンプトだけで解決しきれない限界がある。  
**Claudeはアプリ固有の事情（実測レスポンスタイム、ピーク負荷、CIDR制約など）を知らない。** どれだけプロンプトを工夫しても一般論の域を出ない。

問題は「Claudeがサボっている」ことではなく「**根拠となる情報が与えられていない**」ことだ。  
であれば打ち手は明確で——**どの値に根拠情報が欠けているかを機械的に検出すればいい**。

## 対策：レビュー専用のSubAgentに「requirements.mdとの乖離」を検出させる

Claude Codeには、役割と判断基準を限定した別のエージェント（SubAgent）を定義しておき、必要なときに呼び出す機能がある。これを使う。

狙いを絞る。SubAgentにやらせるのは 「**requirements.mdに根拠が記述されていない値を炙り出し、追記を促す**」 ことだけ。  
値の正しさは判断しない。

チェックの軸も「YAMLにコメントがあるか」ではなく「**requirements.mdとの対応関係があるか**」にする。  
これで # 一般的な初期値 とコメントを付けるだけではすり抜けられない。

なぜ専用のSubAgentか。  
生成したのと同じ会話でレビューさせると「さっき自分で書いた値」を肯定しに行きやすい。  
役割を絞った別エージェントにクリーンな状態で照合させるほうが、抜け漏れが減る。

### SubAgentの定義

.claude/agents/param-reviewer.md を作る。

> ---  
> name: param-reviewer  
> description: CloudFormationの設定値とrequirements.mdの対応関係をチェックし、根拠が記述されていない値を炙り出す  
> ---  
> あなたはCloudFormationパラメータのトレーサビリティレビュー担当です。
>
> 1. `docs/requirements.md` を読む
> 2. `templates/` のテンプレートを読む（Parametersだけでなく、Resources内のリテラルもすべて対象）
> 3. 各設定値について、その根拠となる記述が requirements.md に存在するか確認する
> 4. 根拠の記述がない値を一覧化し、追記を促す
>
> **値の正しさは判断しません。**「requirements.mdに対応する記述がない値を漏れなく特定し、追記を促す」ことだけが役割です。  
> **requirements.md に実際に書かれている記述だけを根拠としてください。ファイルにない内容を「記載あり」と報告してはいけません。**
>
> 出力フォーマット：  
> ## requirements.mdへの追記依頼  
> - パラメータ名(現在値): requirements.mdに追記すべき情報の例

### 実際のレビュー出力

テンプレート生成後、param-reviewer を使って templates/main.yaml と docs/requirements.md を照合して と頼むと、こう返ってきた。

![](https://static.zenn.studio/user-upload/8d5b8fe0ab6d-20260703.png)

重要なのは、requirements.mdに書いた分はちゃんとフラグの対象外になっていることだ。  
「それなりに要件を書いた」つもりでも12項目が根拠なしで残る。  
この「書いた分はクリアされ、書かなかった分だけが残る」挙動が、このSubAgentの実用価値だ。

人間のアクションも「このパラメータは問題ないか？」という曖昧な確認から「TaskCpuの選定根拠をrequirements.mdに追記してください」という具体的な指示に変わる。

### requirements.mdが育っていく

あとはフラグが立った項目について、requirements.mdに根拠を書き足していくだけだ。

例えばスケーリングについて、「最大タスク数20（月次コスト試算より）」「スケールアウト開始CPU60%」を追記する。

![](https://static.zenn.studio/user-upload/df3b820216d4-20260703.png)

そのうえでテンプレートを再生成し、再度 param-reviewer を回す。

すると AutoScaleMaxCapacity: 20・TargetValue: 60.0 は「根拠あり」に移り、フラグ一覧から消えた。  
根拠を書くたびに、フラグは1つずつ減っていく。

![](https://static.zenn.studio/user-upload/c80b15219f08-20260703.png)

人間のレビューが「全パラメータをゼロから精査する」から「フラグが立った項目の根拠をrequirements.mdに書く」に変わる。  
そして書いた根拠は requirements.md に蓄積され、次に誰がテンプレートを触っても参照できる資産になる。

## まとめ

* インフラの設定値には、後から変えづらいものが多い。だからこそ、最初から根拠を持って決める必要がある。
* Claude CodeにCloudFormationを任せると「動くが根拠のない値」が紛れ込む。cfn-lintでは弾けない。
* プロンプトで根拠を求めてもアプリ固有の事情を知らないため「一般論」止まりになってしまう。
* SubAgentの役割を「requirements.mdとの対応関係チェック」に絞ると、一般論コメントではすり抜けられない。  
  出力は「この値を確認して」ではなく「requirements.mdに根拠を追記して」になり、ドキュメントが設計根拠の蓄積場所として育っていく。
* レビューエージェントは万能の判定者ではなく、人間が見るべき場所を絞り込む道具。  
  最後に正しさを確かめるのは、やはり人間になる。

AIにIaCを書かせる流れは止まらない。  
「出力をどう疑うか」「人間のレビューをどこに集中させるか」という設計が、これからじわじわ効いてくると思っている。

## 参考
