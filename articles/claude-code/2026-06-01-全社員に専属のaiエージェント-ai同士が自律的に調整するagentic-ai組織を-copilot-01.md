---
id: "2026-06-01-全社員に専属のaiエージェント-ai同士が自律的に調整するagentic-ai組織を-copilot-01"
title: "全社員に専属のAIエージェント ― AI同士が自律的に調整するAgentic AI組織を Copilot Studio で実装"
url: "https://zenn.dev/katohiro_fi/articles/43d20e4b292634"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "zenn"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

# はじめに

IBM JapanのIBM Microsoft Teamです。  
AIがこんなに進化を遂げているのに、未だに人が調整業務をやっているよね…そろそろ調整から解放されたいよね…ということで、調整業務をAIエージェントにお任せする構想を描いてCopilot Studioで実装してみました。

【プレゼン動画 + デモ動画】  
<https://youtu.be/fcaB0xWOixA>

# 1. 背景・課題：Copilot は準備時間を減らした。でも、調整・行動は誰がやる？

Microsoft 365 Copilot の登場により、私たちの日常業務は確実に変わりました。会議の議事録は自動で生成され、メールの下書きも一瞬で出てくる。PowerPointのスライドも自然言語で説明すれば書いてくれる。これらは「行動するための準備」を劇的に効率化してくれました。

![](https://static.zenn.studio/user-upload/1534ae5fdd1f-20260529.png)

ただ、日常業務は「準備 + 調整・行動」で構成されている思っていて、Copilot が圧縮してくれたのは準備パートです。Work IQ や日々の機能追加により、準備パートはさらに短くなっていますが、**調整・行動のパートは、今も人間がやっています**。

エグゼクティブ層はこの「調整・行動」を秘書に任せています。つまり、自分でやらなくても回る業務です。であれば、これを AIエージェントに任せられない理由はないはず…  
そろそろAIが「調整・行動」にも手を出す頃なのでは？と思い、今回のMicrosoft Agent Hackathonではこの領域に踏み込んでいきます。

## 日本企業でよくある調整祭り

### 日程調整系

* 他の社員の Outlook 予定表を見ても「予定あり」のブロックがびっしり並んでいて、どこが本当に空いているのかわからない。社員によって予定表の使い方が違うため、判別もつかない。Copilot やスケジュールアシスタントもこの予定表をベースに判断するため、結局「いつに入れていいか」が見えてこない。
* 空いていそうな時間に予定を入れたら、実は Planner や Asana など別ツールで管理されていた別件があり、再調整の依頼が来る。
* 招待送信時には問題なかったのに、後日、重要なステークホルダーに急用が入ってリスケが必要になる。  
  ![](https://static.zenn.studio/user-upload/460fd9f38f03-20260531.png)

### タスク調整系

タスクの依頼ひとつとっても、3 つの視点で気遣いが発生します。

* **依頼者の視点**：「A さんにタスクを依頼したいけど、今、依頼していいのかわからない。どれくらいの負荷なのかもわからない」
* **A さん（受け手）の視点**：「周りが困っているなら、今自分が忙しくても依頼を断りにくい。特に役職者からなら尚更…そもそも、そのタスクを管理するのが面倒（入力することすら）」
* **マネージャーの視点**：「勝手に依頼されるのは困る。メンバーの負荷はしっかり管理したいし、スコープ外のことは受けたくないし、依頼状況はキャッチアップしておきたい。依頼は必ずマネージャーを経由してほしい」

### そして「板挟み」と「集中の喪失」

複数の上司や部署から同時に依頼が来ると、板挟みが発生します。優先度を自分で判断するのが難しい。判断するためにも調整が必要。

さらに、こうした調整が入るたびに作業の手が止まり、「あれ？どこまでやっていたっけ」と完全に再開するまでに時間がかかる。これが 1 日に何度も繰り返されると、その人の調整工数が肥大化していく。

## もし、調整も AI に任せられる仕組みがあれば…

これらは実務時間ではなく「**調整時間**」です。価値を創出する時間ではなく、価値を創出するための仕事を回すための時間。

ここを解消する手段は、M365 Copilot 単体では見えてきません。なぜなら、調整・行動は自分から見える情報だけでは完結しないからです。**相手の予定、相手の負荷、相手の個人的な事情や行動特性、相手のマネージャーの意向、組織のルール** ―― これらすべてを統合して初めて、調整は完了します。

もし、これらを「相手のプライバシーを侵害せず」「組織のガバナンスを保ったまま」自動でやってくれる仕組みがあれば…私たちの働き方は、もう一段先に進めるかもしれません。

# 2. 構想：従業員専属のAIエージェントが互いに調整する組織へ

私たちが描いた構想はシンプルです。

**全従業員に専属の AI エージェントを展開する。**

その AI エージェントは、本人専属の秘書のような存在として、本人の予定やタスク、個人的な事情や行動特性、チャット等のコミュニケーション状況を理解しています（もちろん本人の権限境界の内側で行動する）

そして、調整が必要なとき、例えば「来週、A さんと打ち合わせをしたい」「B さんにタスクを依頼したい」と本人が頼むと、本人の AI エージェントは、相手の AI エージェントと直接やりとりして調整を完了させます。

![](https://static.zenn.studio/user-upload/3e76558c75d9-20260601.png)

## Copilot と 専属AIエージェント ― 担う仕事が違う

これまで Copilot が担ってきた領域と、専属AIエージェントが担う領域は、こう違います。

|  | M365 Copilot（AsIs） | 専属AIエージェント（ToBe） |
| --- | --- | --- |
| 主な担当 | 行動するための準備 | 調整・行動そのもの |
| 動き方 | 人が指示し、人が動く | 人が指示した後はAIエージェント同士が動く |
| 情報の範囲 | 本人の参照権限の範囲 | 本人の参照権限 + 調整先の参照権限の範囲 |
| 完了する仕事 | 議事録、メール下書き、パワポ資料作成など | 日程調整、タスク調整、関係者承認、結果反映まで |

### シーン：専属の AI エージェント同士が、裏で交渉する

朝、Teams で「来週、A さんと 30 分の打ち合わせがしたい」と、あなたの専属AIエージェントに伝えたとします。

この間、あなたは A さんの予定の中身を一切見ていません。A さん・B さんのエージェントも、あなたに「タスク詳細」「個人的事情」「内部推論」「他の予定の詳細」を返していません。それでも、調整は完了しています。

人が裏で気を遣いながらやってきた小さな調整を、専属の AI エージェント同士が最小限のやりとりで完結するAgentic AIな組織 ― これを目指していきます。

# 3. アーキテクチャ全体像 ―― Enterprise Agentic AI Organization

全従業員に専属のAIエージェントが展開され、そのAIエージェントたちが現実の組織構造と同じように動く世界 ―― **Enterprise Agentic AI Organization** とでも呼ぶべき、新しい組織のかたちです。本章では、その実装の中核となるアーキテクチャをご紹介します。

![](https://static.zenn.studio/user-upload/397eff7cbad1-20260601.png)

## 使用した Microsoft 技術スタック

| カテゴリ | サービス / コネクタ名 | 本実装での役割 |
| --- | --- | --- |
| Power Platform | Copilot Studio | AI Agent（Main / Responder）の構築・実行基盤 |
| Power Platform | Copilot Studio（Direct Line API） | Gateway から Responder Agent を呼び出すための API チャネル |
| Power Platform | Power Automate | Gateway 本体。A2A 通信のルーティング・宛先解決・Responder 呼び出し |
| Power Platform | Power Apps | 調整状況のダッシュボード |
| Power Platform | Dataverse | Agent Directory（宛先解決テーブル）・A2A 監査ログの保存 |
| Power Platform | Dataverse Web API / Custom API | UI・Gateway からの状態参照／状態更新API |
| Power Platform | Dataverse Plug-in | Custom API 実行時またはテーブル更新時のサーバーサイド処理 |
| Work IQ MCP Server | Work IQ Copilot | 複数ソース横断の要約・統合的な文脈把握 |
| Work IQ MCP Server | Work IQ Calendar, Mail | 本人の予定・メール上の依頼背景の参照 |
| Work IQ MCP Server | Work IQ Teams | Teams の直近論点・会話文脈の参照 |
| Work IQ MCP Server | Work IQ SharePointOnline | 共有ドキュメントの参照 |
| Work IQ MCP Server | Work IQ OneDrive | 個人領域の作業中ファイル、議事録の参照 |
| Work IQ MCP Server | Work IQ User | 組織情報の取得 |

※ Work IQ MCP ServerのCopilot Studio Toolは2026/6/1時点でPreview機能

## 1 人 2 エージェント構成

本実装では、1 人の従業員に Main Agent と Responder Agent の 2 つのエージェントを展開します。

* **Main Agent**：人間が話しかける入口、つまりフロントエンドエージェントのようなものです。本人の予定、タスク、Teams 文脈を確認でき、従業員と対話します。
* **Responder Agent**：他のMain Agentから Gateway 経由で呼ばれる内部応答口、バックエンドエージェントのようなものです。人間向けの自然文ではなく、A2A 調整用の JSON だけを返します。

## Gateway と二段階照会のフロー

A2A 通信は、すべて Power Automate で構成した Gateway を経由します。

例として、user03 が user14 と日程調整したいケースを見てみましょう。

1. user03 の Main Agent から Gateway にリクエストが飛びます
2. Gateway は EntraID MCP Server の組織情報を参照して、user14 の上司である user12 を解決します
3. user12 の Responder Agent に「user14 に調整を依頼してよいか」を確認します
4. accept なら、Gateway はもう一度同じルートで、今度は user14 本人の Responder Agent に調整内容をリクエストします
5. user14 の Responder Agent が本人領域だけ確認し、候補日時を JSON で返します

## Work IQ 前提の設計（理想形）

この設計の中心に置きたいのは、Work IQ MCP Server です。

扱いたいのは、予定表の空きだけではありません。メール上の依頼背景、Teams の直近論点、SharePoint の議事録、OneDrive の作業中資料、Manager 情報など、Microsoft 365 に散らばるコンテキストです。

| 必要な業務文脈 | Work IQ MCP Server |
| --- | --- |
| 組織情報 | Work IQ User |
| 空き時間、会議密度 | Work IQ Calendar |
| メール上の依頼背景 | Work IQ Mail |
| Teams の直近論点 | Work IQ Teams |
| 作業中資料、議事録 | Work IQ OneDrive / SharePoint |
| 行動特性、個人的な事情 | Work IQ Copilot |

全従業員の専属AIエージェントが Work IQ を通じて本人領域を理解し、現実の組織構造と同じように承認・相談・調整を行う ―― これが Enterprise Agentic AI Organization の理想形です。

## 現行実装はナレッジ/コネクタベース、でも置き換え可能

提出時点では Work IQ MCP Server は Preview です。全てを Work IQ 前提で安定動作させるには時間が足りませんでした。

そこで現行では、Copilot Studio の knowledge と Microsoft 365 コネクタでMVP開発しています。組織情報や本人の個人的な事情/行動特性は knowledge、予定は Outlook コネクタ、Teams 文脈は Teams コネクタ、として登録しています。

これは Work IQ を諦めた設計ではなく、Work IQ を見越して構築した前提です。Main Agent、Responder Agent、Gateway、Directory という枠組みはそのままに、情報取得の部分を Work IQ MCP Server に置き換えられる構成にしています。

※Work IQ SharePointOnlineやOneDriveはコンテキスト量が急増するため、今回のHackathon環境のスコープ外としました。

# 4. なぜ、AIエージェントにCopilot Studioを採用したのか？

本構想は全社員への展開が前提です。そのスケールで動かす基盤として、3 つの理由で Copilot Studio を選びました。

## ① 統一性のあるUX：Microsoft 365エコシステムから自然にAIエージェントを呼び出せる

今回、私たちが扱いたいのは、高度な独自計算でも、巨大モデルの推論基盤でもなく、従業員が常日頃から利用している業務環境の中で、いかに自然にAIエージェントを呼び出せるか？これが全社員展開に向けた利用定着の鍵だと考えています。

ユーザーが「新しい UI を覚える」「別アプリを起動する」、その必要がない統合的なフロントエンドは、定着率を左右する要素の１つになります。

## ② 全社員展開に効果的なローコード性

私たちが目指しているのは、**全従業員に専属のAIエージェントを展開する** 構想のため、IT部門が全てのAIエージェントを訓練し続けるのは現実的ではありません。

Copilot Studio で作られたエージェントは、業務担当者が画面上で instructions や knowledge、Tools を改善できます。  
**業務部門が現場の言葉でエージェントを育てられる**。IT 部門の作業を待つことなく、現場が AIエージェント を進化させていけるローコード性です。

## ③ Microsoft 365 エコシステムによる統制とコスト効率

実業務で AI エージェントを使うとき、最も怖いリスクは「便利だが統制できない」「セキュリティ上の懸念があって全社規模に展開できない」です。

GartnerやIBMの調査レポートでは、AIエージェント導入における理解と実装の間に大きなギャップがあり、ガバナンスの不備は、もはや技術論ではなく経営リスクの領域であることが語られています。

| 観点 | 業界の現実 | 出典 |
| --- | --- | --- |
| ガバナンス成熟度ギャップ | 経営層の **74%** が AI ガバナンスを重要視、自組織が成熟していると考えるのは **21%** のみ | IBM IBV (2025 年 1 月) |
| AI 起因の法的リスク | 2026 年末までに「AI に起因する」法的請求が **2,000 件超** と予測 | Gartner Strategic Predictions for 2026 |
| ガバナンス基盤不足による失敗 | AI エージェントデプロイ失敗の **50%** が、ガバナンス基盤のランタイム制御不足とマルチシステム相互運用性の欠如に起因 | Gartner Newsroom (2025 年 6 月) |

この観点で Copilot Studio が強いのは、エージェントを Microsoft 365 のセキュリティ・ガバナンス基盤にまとめて乗せられることです。

| 領域 | Microsoft Solution |
| --- | --- |
| 脅威検知・異常動作のリアルタイム検出 | Microsoft Defender |
| 監査・DLP・データ保持ポリシー | Microsoft Purview |
| エージェント ID 管理 | Microsoft Entra Agent ID |
| エージェント全体の統制・可視化 | Microsoft Agent 365 |
| コンプライアンス認証 | ISO 27001 / SOC 2 / FedRAMP / ISMAP / GDPR / HIPAA 等、90+ の第三者機関認証 |

Microsoft 365 のプラットフォームに乗せることで、これらを丸ごと享受できます。

更には Microsoft 365 Copilot を既に契約している企業にとっては、Copilot Studio のクレジット消費が Free になるなど、追加投資の説明が比較的容易になります。

全社員への展開という全社規模でのガバナンスとコスト効率を考えると、Copilot Studio は非常に優れていると考えています。

# 5. 設計の工夫点 ― Microsoft の仕様意図を尊重

今回のアーキテクチャは最初から決まっていたわけではありません。全社員への展開を前提にすると、接続数、Agent chaining、プライバシー漏洩を考慮する必要があります。  
本章では、3 つの工夫と、それらが収束した理由を共有します。

核にあるのは、**Microsoft の仕様制限を抜け道で回避するのではなく、その意図を尊重して設計を進化させる** という考え方です。

## 工夫① 接続方式、3 案を試行錯誤

先程のアーキテクチャ全体像でも疑問に思った部分は多々あるかもしれません（なぜ Gatewayを経由する設計にしたのか）

![](https://static.zenn.studio/user-upload/199e4dc31d03-20260531.png)

### Case1: Connected Agent フルメッシュ

最初に思いついたのは、全員の専属AIエージェントを Connected Agent で相互接続する構成です。

具体的にはCopilot Studioの以下の画面で全台分を追加するイメージです。  
![](https://static.zenn.studio/user-upload/e9c5217035c3-20260531.png)

ただし、全社展開を考えた瞬間に破綻します。接続数は `N × (N - 1)` で、もし1万人の従業員がいれば 10000 × 9999、約 1 億本の接続になります。1 つあたりのエージェントが持つコンテキストの量が爆発的に増え、運用は現実的に不可能です。

新人 1 名を追加するだけでも、既存 N 名全員に接続設定が必要です。異動、退職、組織変更、権限変更まで考えると、なおさら無理があります。

### Case2: 組織構造ベースの Connected Agent

では、我々が組織体制を組んで、その組織構造の基に行動するのと同じように、エージェントも組織構造の中で動いたら良いのでは？という発想で、組織構造をそのまま Connected Agent に写す案を考えました。

たとえば、user02 が Manager、user03 / user04 がメンバーなら、user02 からメンバーへ、メンバーから user02 へ接続します。

ところが、今度は Copilot Studio の仕様によってエラーで止まりました。  
`ConnectedAgentChainingNotSupported` ― エージェントのチェーンが検出されました、と返されます。

![](https://static.zenn.studio/user-upload/6eff51a111e9-20260601.png)

参考: [ConnectedAgentChainingNotSupported - Copilot Studio error codes](https://learn.microsoft.com/ja-jp/troubleshoot/power-platform/copilot-studio/authoring/error-codes?tabs=webApp#connectedagentchainingnotsupported)

### Case3: Direct Line API + Gateway 方式

試行錯誤の末、Gateway 方式に辿り着きました。何か通信する際は全て Gateway を経由して、その Gateway が接続先の宛先を解決することで、A2A 接続を実現します。

Copilot Studioエージェント は Gateway 1 本にだけつながります。Gatewayに依頼先の情報を渡し、Gateway がDataverseの組織情報を参照して対象のCopilot Studioエージェントの宛先を解決します。

この方式なら、新人 1 名を追加するときも、全員の Main Agent に接続を足す必要はありません。Dataverseの組織情報に 1 行を追加し、その人のCopilot Studioエージェント と本人領域への接続を用意すればよい。**接続管理は社員数に対して線形にスケール** します。

また、工夫②にもつながりますが、接続チェーンが発生しない構成にしているので、Copilot Studio の設計思想を尊重した設計になっています。

## 工夫② 1 従業員 2 エージェント構成 ― 一方向通信で抜け道を作らない

ただし、Gateway を介せば、技術的には双方向通信や循環的な A2A を作れてしまいます。Microsoft が Connected Agent で制限している agent chaining を、Direct Line API と Gateway で迂回するのは設計意図を裏切ることになると考えました。

エージェントチェーンの仕様制限している理由は見当たりませんでしたが、恐らく Microsoft がこの仕様にしているのは、何かしら理由・設計思想があるはずです。たとえば、リクエストが可能なエージェント同士で A2A 接続すると循環要求が発生してしまう、ということではないでしょうか。

![](https://static.zenn.studio/user-upload/e722c1d069df-20260601.png)

そこで採用したのが、1 従業員 2 エージェント構成です。リクエストを出す側を木構造のツリーで言うところの根、Manager を節点、Member を葉とする構造を組み、リクエストは根から葉への一方向のみとしました。

![](https://static.zenn.studio/user-upload/9faf3bae956a-20260531.png)

| 木構造の位置 | エージェント | 役割 |
| --- | --- | --- |
| 根 (root) | Main Agent | 依頼者の入口、Gateway を呼ぶ |
| 節点 (node) | Responder Agent (Manager) | 承認・優先度判断 |
| 葉 (leaf) | Responder Agent (Member) | 可否・候補・capacity 回答 |

（厳密には木構造ではないですが、設計の整理として、根/節点/葉の表現を使用しています。）

ルールは 3 つです：

* リクエストは Main → Responder の一方向のみ
* Member → Manager、Manager → Main の経路は作らない
* Responder は再委任しない（Gateway tool を持たせない）

Responder Agent には Gateway tool を持たせません。他のエージェントを呼び返す経路を構造的に消し、A2A の向きを Main → Gateway → Responder に限定しました。

Microsoft社の **仕様の制限には意味があるはず**…そう尊重した結果、この構造に辿り着きました。

### 補足：M365 Copilot Portal/Teams と Copilot Studio Direct Line APIの認証方式

なお、Main / Responder を分けた理由は、上記の設計だけではありません

Gatewayを構成する際に、今回、Copilot StudioのDirect Line API を使用しています。このAPIを使用するには、Copilot Studio の Web チャネルを有効化し、シークレットキーで通信する必要があります。  
となると、構成上、Microsoft 認証を外す必要があります。一方で、Teams や M365 Copilot ポータルに公開するには Microsoft 認証が必要です。この制約も、1 人 2 エージェント構成を後押ししました。

## 工夫③ 最小開示の JSON 生成 ― プライバシーを構造で守る

AI エージェントには、Microsoft 365 Graph への強い読み取り権限を持たせています。M365 Copilot Work IQやTeams,OulookなどのWork IQに全てにアクセスできる、かなり広い権限です。

何もしなければ、これら全てが他のエージェントに開示されてしまいます。その社員の予定やタスク情報、お客様情報、行動特性、個人的な事情など…全部です。

そこで、Responder Agent は本人領域の生データではなく、構造化された JSON だけを返す設計にしました。

![](https://static.zenn.studio/user-upload/3e2956d11350-20260531.png)

返してよい情報は次の通りです：

| 返してよい情報 | 意味 |
| --- | --- |
| `status` | accept / counter / decline / need\_approval |
| `candidateSlots` | 候補日時 |
| `capacityBand` | high / medium / low / unknown |
| `abstractReason` | 抽象化された理由 |
| `redactionApplied` | 情報を最小化したことの明示 |

予定名、Planner タスク名、Teams 本文、メール本文、個人的事情、内部推論は返しません。Main Agent は、相手の詳細ではなく、**調整に必要な判断材料だけを受け取ります**。

**強い権限を持つエージェントだからこそ、構造でデータを守り、開示は最小限にしていく**。これが 3 つ目の工夫です。プライバシーは「気をつけて扱う」ではなく、「構造で守る」設計に落とし込みました。

# 6. デモ動画

※デモ：4:30～6:21  
<https://youtu.be/fcaB0xWOixA>

ユーザーは M365 Copilotポータル や Teams 上で、自分の Main Agent に一言依頼を投げるだけ。Main Agent が受付し、Gateway 経由で対象の Responder Agent に問い合わせ、結果を返してくる…ユーザーから見える挙動は、本当にそれだけで非常にシンプルです。

なので、裏では何が起きているのか、エージェント間の調整の様子をダッシュボードで可視化しています。動画では、画面左が調整ダッシュボード、右半分がM365 Copilotポータルのチャット画面になります。

例えば、  
「業務部のマネージャー以外のメンバー全員と再来週に30分枠で来期のIT部門への要望についてヒアリングしたい」  
とプロンプトを送信します。

![](https://static.zenn.studio/user-upload/936f06e809aa-20260601.png)

まず自分の予定やタスク、Teamsチャット等の状況から自分の候補日時を選定します。  
その後、業務部のマネージャーに「メンバーと打ち合わせしても良いか？」確認しに行きます。  
（中村さんエージェントが調整先のマネージャーの阿部さんエージェントに交渉している様子）

![](https://static.zenn.studio/user-upload/daeb72c95680-20260601.png)

マネージャーの阿部さんから承認を得られたら、次にメンバーと調整します。まずは石川さんから。  
（中村さんエージェントが調整先の石川さんエージェントに交渉している様子）

![](https://static.zenn.studio/user-upload/25a5e165e2df-20260601.png)

もう1名のメンバーの佐藤さんにも調整します。  
（中村さんエージェントが調整先の佐藤さんエージェントに交渉している様子）

![](https://static.zenn.studio/user-upload/19e67fe43063-20260601.png)

メンバー2名との調整が完了し、それぞれのメンバーとのTeams会議が作成されました。

![](https://static.zenn.studio/user-upload/01269003daec-20260601.png)  
![](https://static.zenn.studio/user-upload/7ac2c96e2f51-20260601.png)  
![](https://static.zenn.studio/user-upload/38f639a6e99b-20260601.png)

# 7. さいごに：専属の AI エージェントが武器を増やす未来

第 2 章で「ToBe」として提示した構想は、全従業員に専属のAIエージェントが展開され、AIエージェント同士が調整を引き受ける組織「Enterprise Agentic AI Organization」を今回のMicrosoft Agent Hackathonで環境を構築しました。ここまで紹介してきた実装は、その一つの例です。

なので、今日の視点から見ると、これはCanBeです。そしてその先に、もう一段先の ToBe があると思っています。

ToBe を語る前に、少し M365 Copilot の歴史を振り返らせてください。

## M365 Copilot リリース当初の評価を覚えていますか？

2023 年 5 月にアーリーアクセスプログラムが始まり、同年 11 月 1 日に Microsoft 365 Copilot が一般提供を開始しました。多くの企業がここで PoC を始めましたが、当時の Copilot は今とは比べものにならないものでした。

* Office の Copilot は全般的に自然言語が通じない
* Excel は表計算とグラフ作成しかできず、WBS や QA 表のような資料は作れない
* PowerPoint はスライドの新規作成や編集が困難で、翻訳すら十分にできない
* Copilot チャットの回答精度は悪く、ハルシネーション多発。出力ファイルも軒並み微妙

「もう少し成熟してから本格導入しよう」と PoC を縮小・撤退した企業も少なくありませんでした。当時の状況からすれば、合理的な判断に見えました。実際、メディアでも辛口な評価が並んでいた時期です。

<https://www.itmedia.co.jp/aiplus/article/2605/15/1260515013/>

しかし、現在の M365 Copilot は実用度が大きく向上しています。特に PowerPoint の精度が大きく改善され、実用的になりました。Copilot チャットの回答品質も大きく向上し、当時とは別物と言えるレベルに到達しています。

## 成果を出しているのは、ずっと使い続けた企業

このM365 Copilot が大きく進化したとき、すでに成果を出し始めていたのは、**諦めずに使い続けてきた企業** だと思っています。

これらの企業はM365 Copilot を日常業務に組み込む文化を社員の中に作り終えています。Copilot に何を頼めばいいか、どんな業務フローに組み込むか ― これらの体得には、Copilot の進化とは別の時間がかかります。Copilot が完成してから飛び乗った企業は、ここから始めなければなりません。

## ToBe：専属AIエージェントが「武器」を増やしていく未来

![](https://static.zenn.studio/user-upload/17db17d1f34c-20260529.png)

今回の専属AIエージェントは Work IQ MCP Server とコネクタで本人文脈を理解します。これが「CanBe」です。

新しい更なる ToBe は、Copilot Studio が機能を増やすたびに、専属のAIエージェントが新しい武器を手にしていく世界です。新しい MCP Server、新しいコネクタ、新しい自律性 ― これらが追加されるたびに、専属AIエージェントは「秘書」を超えて、業務全体を引き受ける存在に進化していくと想定しています。

そして、これがローコード（Copilot Studio）で組まれているため、現場のユーザー自身が画面上のポチポチ操作で新しい機能を組み込めます。AI の進化を、IT 部門の作業待ちなしで、現場が直接享受できる構造です。

もちろん、現場が自由に機能を追加できるとガバナンスが論点になりますが、Microsoft 365 の堅牢なセキュリティと法規制準拠、そして Agent 365 によるエージェント制御によって、現場の柔軟性と組織のガバナンスを両立できる設計になっています。

## 将来を想定すると…

M365 Copilotの歴史も踏まえて、Copilot Studio で全社員のリテラシーを今のうちに作り上げた組織と、そうではない組織との間に、数年後、想像以上に生産性の差が生まれると見ています。利活用の浸透には、Copilot Studio の進化とは別の長い時間が必要だからです。Copilot Studio が完成してから動いても、その時には既に大きな差ができています。

本記事で紹介した実装は、あくまで一つの例です。しかし、根本にあるメッセージは、  
**今、Copilot Studio で何かを動かしましょう。完璧でなくてもOKです。組織がそれに慣れた頃、Copilot Studio が本気を出してきます。**  
そして、その時に「使える組織」と「これから使う組織」の差は、もう簡単には埋まりません。

そのためにも、今、このタイミングで Copilot Studio が自律的に行動する環境を作り出すことで、未来に備えていく ― そういう構想を、今回お示しできていれば嬉しいです。

---

私たちが今回のMicrosoft Agent Hackathonで描いた構想は、全従業員に専属の AI エージェントが付き、その AI エージェントたちが現実の組織構造と同じように動く世界 ― **Enterprise Agentic AI Organization** とでも呼ぶべき、新しい組織のかたちです。

ボリュームが大きい記事にはなりましたが、最後までお読みいただき、ありがとうございました。
