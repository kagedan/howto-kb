---
id: "2026-07-23-using-llms-to-secure-source-codeを継続的に実行するanthropic-01"
title: "「Using LLMs to secure source code」を継続的に実行する——Anthropicの手法を実装した記録"
url: "https://zenn.dev/ryokkon/articles/8b62e221fc9ac3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-07-23"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

2026年5月にAnthropicが [「Using LLMs to secure source code」](https://claude.com/blog/using-llms-to-secure-source-code) を公開しました。「LLMでソースコードの脆弱性を見つける」記事かと思いきや、読んでみると大事なのは“見つけたその先”にありました。

私は個人開発で、Claude Codeのエージェント（SM・DEV・PO・各レビュアー）にスクラムを回させる仕組みを運用しています。本記事は、Anthropicのこの手法をその既存チームに「セキュリティのロール」として組み込み、継続的に実行できるようにした記録です。

## 1. 元ネタ：Anthropic「Using LLMs to secure source code」

### 1.1 主張は「発見は容易。ボトルネックは“その先”」

記事のいちばんの主張はこちらです。

> 原文: Our primary takeaway: discovery is now straightforward to parallelize, and the bottleneck has shifted to verification, triage, and patching.  
> 訳: 私たちの一番の結論: 発見（discovery）はいまや並列化が容易になり、ボトルネックは検証・トリアージ・修正へと移った。

*（以降、引用ブロックは原文（英語）＋筆者による訳です。）*

つまり「AIに脆弱性をたくさん見つけさせる」こと自体は、もう難しくない。難しいのは、その大量の候補を裏取りし、優先順位をつけ、実際に直しきること。だから記事は、発見して終わりにせず「見つける → 裏取り → 優先度づけ → 直す」を回しきる6段階のループ（Find-and-Fix Loop）を提案しています。

### 1.2 Find-and-Fix Loop（6段階）

| # | 段階 | 概要 |
| --- | --- | --- |
| ① | Threat Modeling（脅威モデリング） | スキャン前に「何を脆弱性とみなすか」を決める |
| ② | Sandboxing（サンドボックス） | exploitを安全に試せる隔離環境を作る |
| ③ | Discovery（発見） | 脆弱性候補を洗い出す（網羅重視） |
| ④ | Verification（検証） | 本当に悪用できるかを確かめる（精度重視） |
| ⑤ | Triage（トリアージ） | 重複排除・重大度づけ・優先順位づけ |
| ⑥ | Patching（修正） | 直して、亜種を探す |

このうち、記事が特に紙幅を割くのが ③Discoveryと ④Verificationです。両者の役割は、原文の次の一文で説明されています。

> 原文: Discovery optimizes for recall; verification optimizes for precision.  
> 訳: Discoveryはrecall（網羅性）を、Verificationはprecision（精度）を最適化する。

* Discoveryは網羅性を最適化する：「あり得なさそうな候補まで含めて、とにかく広く挙げる」のが仕事。
* Verificationは精度を最適化する：「実際には悪用できない候補を、確実に落とす」のが仕事。

役割が正反対、という点が次の原則につながります。

### 1.3 大事な原則：発見と検証を分離する

記事が繰り返し強調するのがこちらです。

> 原文: When an agent tries to do both in the same step, it can self censor and exclude exploitable true positives.  
> 訳: ひとつのエージェントに（発見と検証の）両方を同じステップでやらせると、自己検閲が起き、悪用可能なtrue positiveまで除外してしまう。

理由は、Discovery（網羅）とVerification（精度）が相反する最適化目標だから。ひとつのエージェントに両方を実行させると、「これは悪用できないかも…」と自分で候補を除外してしまい（自己検閲）、本来抽出しなければいけないものまで落としてしまう。

だから**検証者は、発見者から独立**させる。

* 発見者の推論を見せない（見せると “検証” せず “同意” するだけになる）。
* 渡すのは「findings（検知された脆弱性の候補）」と「コード」だけ。あとは自力で反証（＝このfindingは間違いだと言える理由を探す）させる。
* 1回で不安なら、複数の検証者 × 多数決。可能ならサンドボックスでPoCを実際に動かす（**動くexploitは多数決より優先**）。

※exploit＝脆弱性を実際に突く攻撃コード・手順

記事は、パートナー各社の実測をこう伝えています。

> 原文: Across the teams we've worked with, adding an adversarial verifier roughly halved the rate of non-exploitable findings from the discovery phase. Requiring that verifier to also build a proof of concept confirming the exploit brought the false positive rate to near zero.  
> 訳: 私たちが協働してきたチーム全体で見ると、敵対的な検証者を足すだけで、発見フェーズの悪用不能なfindingsの割合はおよそ半減した。さらにその検証者に、exploitを確認するPoCの構築まで課すと、誤検知率はほぼゼロになった。

### 1.4 なぜ “下流” が主役になるのか

昔は発見に手間がかかったので、バグを見つけた本人がそのまま優先度づけ（トリアージ）もしていた。ところが今は、モデルが昼までに100件の候補を出す時代になってきた。

ここで「100件全部どうぞ」と開発者に渡す。そうすると、重複や重大度の水増しの山に埋もれて、開発者は報告を読まなくなる（alert fatigue＝アラート疲れ）。そして即修正が必要なcriticalまで、無視されてしまう。

だから重心は「たくさん見つける」から、重複を排除し、正しい重大度をつけ、直せる量に絞り込む、つまり検証・トリアージ・修正へ移る。これが元記事の、中心的な主張と捉えています。そのため、記事は、こう言い切っているのだと思います。

> 原文: Budget for the pipeline after the scan before you budget for more scanning.  
> 訳: スキャンを増やす予算を組む前に、スキャン“後”のパイプライン（検証・トリアージ・修正）の予算を確保せよ。

## 2. プロダクトと開発手法

私の環境の紹介です。この章は次章以降のための前提の紹介であるため関連する箇所のみ説明します。気になる点があれば過去記事をご参照ください（ [過去記事](https://zenn.dev/ryokkon/articles/a7f943f87da11a#%E5%85%A8%E4%BD%93%E5%83%8F)）。

### 2.1 プロダクトと構成

題材はHwHubという、家庭の家事を可視化する個人開発サービスです。構成は複数リポジトリに分かれています。

ここで関わってくるのは「リポジトリごとに攻撃面が違う」ことです。フロントはXSSやトークンの扱い、バックは認可やIDOR、バッチは外部入力を含むAI連携、インフラはIAMや公開設定など、見るべき観点がリポジトリで変わります。

### 2.2 スクラムを回すAIエージェントチーム

このプロダクトを、Claude CodeのAIエージェントチームに開発させています。`.claude/agents/` に各ロールを定義し、スクラムのイベントを回す構成です。

| ロール | 担当 |
| --- | --- |
| SM（Scrum Master） | イベント進行、エージェント間の調整（チームリード） |
| DEV（Developer） | バックログの実装、AC（受入基準）を満たす |
| PO（Product Owner） | バックログ管理、ACの詳細化 |
| 各Reviewer | 規約 / パフォーマンス / セキュリティ観点のレビュー |

運用していていちばん大きいのが、一気通貫であること。私がSMエージェントに「Sprint XXのPlanningを開始して」と言うだけで、Planning → 実装（DEV）→ レビュー（Reviewer群）→ PR →レトロスペクティブまで、エージェントが自走します。私は要所の判断だけをしています。

### 2.3 この既存チームに「SEC」を新設する

既存のAIエージェントチームは"作る"ためのチームでした。本記事では、この構成に"守る"ためのロールとしてSEC（security-lead）を新設して組み込みます。

次章から、このSECをどう別フロー化し、Find-and-Fix Loopをどう組み込んだかを紹介します。

## 3. プロダクトにどう組み込んだか（実装・設計思想）

### 3.1 全体設計 — Find-and-Fix Loopをどう組み込むか

記事に記載があるとおり、Find-and-Fix Loopの6ステップは「setupとloop」の2つに分かれます。

> 原文: The first two steps—building a threat model and a sandbox—are the setup for the rest of the loop. These are typically done once per codebase and revisited when the underlying system changes. The next four steps are the loop you'll run against the source: discover, verify, triage, and patch.  
> 訳: 最初の2ステップ——脅威モデルとサンドボックスの構築——は、残りのループのための"下準備"。これらは通常、コードベースごとに一度だけ行い、土台となるシステムが変わったときに見直す。続く4ステップが、ソースに対して回す"ループ"——発見・検証・トリアージ・修正——。

| Anthropicのステップ | 自環境での実装内容 | どこに組み込むか |
| --- | --- | --- |
| ① Threat Modeling | `THREAT_MODEL.md`を用意（信頼境界・スコープ外＝最終強制点） | 各リポジトリで一度対応 |
| ② Sandboxing | PoC環境を段階で決める（ローカル→IAM→Ephemeral STG） | 各リポジトリで一度対応 |
| ③ Discovery | Scan（定期ツール／PRレビュー）＋AI深掘り（攻撃面ごとに並列） | 新規フロー（一部既存のSprint） |
| ④ Verification | 3ペルソナ多数決＋ライブPoC | 新規フロー |
| ⑤ Triage | 重大度づけ・既存Issue突合・起票前の人間承認 | 新規フロー |
| ⑥ Patching | Issue → PO Refinement → DEVがTDD＋回帰テスト | 既存のSprint |

記事はloopの4ステップ（③Discovery → ④Verification → ⑤Triage → ⑥Patching）をひとつのループとしていますが、私は③Discovery → ④Verification → ⑤Triageまでを新規フロー（Discovery&Verificationフロー）に、⑥Patchingだけを既存のフロー（POのRefinement → DEVのTDD＋回帰テスト）で対応することにしました。これは、既存チームの品質保証（テスト・レビュー・PR）がそのまま活かせるためです。  
![](https://static.zenn.studio/user-upload/135a285c54e1-20260723.png)

### 3.2 setup — 各リポジトリで一度対応

③以降を対応する前に、①② をリポジトリごとに整えます。改修が入る度に毎回作り直すものではなく、土台となるシステムが変わったときだけ見直すものになります。

#### ① Threat Modeling＝ `THREAT_MODEL.md`

各リポジトリのルートに`THREAT_MODEL.md`を置き、「何を脆弱性とみなすか」を文章化します。以下のようなことをまとめていきます。

* 信頼境界：どの入力を信頼し、どこからを信頼しないか（外部ユーザー入力／内部サービス間／管理者操作）。
* スコープ外＝最終強制点：認可はサーバー側で最終的に強制される、DB権限で守られている、といった "最後に強制される防御"がどこか。
* 前提・非目標：コードから見ない範囲（例：物理セキュリティ、サードパーティSaaSの内部）。

THREAT\_MODELがあると、「この指摘は、どれくらい深刻か」を判断するときの基準になります。AIに任せきると何でも"Critical"に寄りがちです。でも「このリポジトリでは、何がどこまで守られているのか」をAIに渡すことで、その基準に照らして、重大度を決めるようになります。

THREAT\_MODELは、重大度設定の両方向に効果があります。

* 上げすぎを防ぐ：認可がサーバー側やDB権限で最終的に守られているなら、フロント側の抜けだけを見て「最重要」に格上げしない。
* 下げすぎも防ぐ：WAFのような"コードからは見えない防御"を「たぶん止めてくれるはず」と当てにして、重大度を下げない。見えない防御を前提にしない。

つまりTHREAT\_MODELは、脆弱性をむやみに増やすのも、見落としも防ぎ、重大度を適切に設定するために利用されます。

（Threat Modelingは、セキュリティに触れていないと、なかなかとっつきにくいと思います。私の場合はClaude Codeに「このリポジトリのThreat Modelingをしたい」と相談しながら`THREAT_MODEL.md`を作りました。）

#### ② Sandboxing＝PoC環境を段階で用意する

④Verificationでは「実際に悪用できるか」をライブPoCで確かめます。そのための隔離環境（以降PoC環境と記載）をリポジトリごとに用意しておきます。PoC環境としては3段階に分けて選べるようにしました。

| 段階 | 環境・手段 | 適したfindings |
| --- | --- | --- |
| 軽量 | ローカルDocker＋localstack（フロントはPlaywrightで観測） | アプリ層（認可/IDOR・認証・入力・アプリ内S3）。ほとんどはここで足りる |
| 実API | `aws iam simulate-principal-policy` / Access Analyzer（フル環境を建てずに権限を評価） | IAM権限まわり |
| 中〜重 | Ephemeral STG（Terraform apply/destroy）／一時Fargate（egress-lock） | ネットワーク到達性・ALB/WAF・S3公開・破壊的／横展開 |

運用ルールは、

* 軽量から選択する
* 終わったら必ず後始末する
* クラウドやSTGが要るfindingsの場合は、コストに影響があるため事前に人間へ相談する  
  としています。

（これまでの実績ではPoCはすべて軽量な段階（ローカル）で足りており、実API、中〜重の段階は選択されていません。必要になったら上げられるよう、設計だけ先にしています。）

### 3.3 ③Discovery — 2つに分割

Discoveryは「候補を広く出す」ステップです。私はこれを2つに分けました。

| 名称 | 実行手段 | 性質 | いつ |
| --- | --- | --- | --- |
| Scan | ルールベースのツール＋PR時の軽量AIレビュー | 広く浅く / 安い / 機械的 | 常時／週次定期 |
| AI深掘り | `security-scanner`（AI）を攻撃面ごとに並列起動 | 狭く深く / 高い / 意味を含む | オンデマンド |

理由は、検知できるものが違うからです。

* ルールベース（Semgrep等）は"既知"止まりで、パターンに一致するものは検知可能、一方で、認可ロジックの穴やトークン設計の誤りのような、コードの意味・文脈に依存する脆弱性は検知不可。
* そこはAI深掘りでないと検知できない。しかし、AI深掘りだけを常時回すのはコストが高い。

そのため「常時ルールベースのScanで広く、ときどきAI深掘りで深く」の2つにしました。

#### Scan — 常時・自動で「既知の脆弱性」を検知

Scanは、既存のSprintフローに組み込み自動化しています。ワークフローは2つあります（frontendの例： [同期ワークフロー](https://github.com/ryokkon624/hw-hub-frontend/blob/main/.github/workflows/security-frontend.yml) 、 [週次ワークフロー](https://github.com/ryokkon624/hw-hub-frontend/blob/main/.github/workflows/security-scheduled-frontend.yml)）。

* 同期（PRごと）：PRのたびに走るスキャン。依存パッケージの監査（npm audit）＋差分のAIレビュー（`claude-code-security-review`）。コミット時点で差分を見て、その場で指摘する。
* 非同期（週次）：毎週月曜に自動実行するツールスキャン。使うツールはリポジトリの性質で変わり、結果の集約先で2つに分かれます。
  + SARIFでGitHub code scanningに集約
    - Semgrep：SAST（コードの静的解析）
    - Trivy：IaC設定、コンテナスキャン ※コンテナ／IaCのあるinfra・backend
  + Actionsの実行ログ／ジョブサマリに出力
    - gitleaks：秘密情報の混入・git履歴含む。検知でジョブfail
    - npm audit：依存の棚卸し。依存の脆弱性はDependabot alertsでも継続追跡

同期のAIレビューに使っている `claude-code-security-review` は、元記事に記載されているGitHub Actionです。

> 原文: [`claude-code-security-review action`](https://github.com/anthropics/claude-code-security-review): Github action with Claude as a security reviewer on every pull request.  
> 訳: claude-code-security-review action：すべてのプルリクエストで、Claudeをセキュリティレビュアーとして走らせるGitHub Action。

このScanが検知できるのは、既知の危険なパターン、古い依存、ハードコードされたキー、などのルールに一致するものです。新設したフローのDiscoveryは、このScanの結果をTriageするところから始まります。

#### AI深掘り — オンデマンドで「コードの意味・文脈に依存する」脆弱性を検知

もう一方が、新設したフロー実行時に走らせるAIの深掘りです。実行は`security-scanner`というサブエージェントを、攻撃面ごとに並列起動して行います。

設計のポイントは3つ：

1. 攻撃面ごとに並列化する。ひとつのエージェントに全部行わせるのではなく、分担させる。概ねこのように並列化：
   * 認可 / IDOR / 権限昇格
   * 認証 / トークン / OAuth / セッション
   * 入力 / インジェクション / アップロード / SSRF / デシリアライズ
   * ＋リポジトリ別の狙い目
     + frontend：XSS・CSP・オープンリダイレクト・localStorageトークン
     + mobile：セキュアストレージ・証明書ピンニング・ディープリンク
     + batch：プロンプトインジェクション・S3ナレッジ連鎖
     + infra：IAM・SG・公開設定
2. THREAT\_MODELをコンテキストとして渡す。3.2で作成した `THREAT_MODEL.md` を読ませ、「何を脆弱性とみなすか・どこが最終強制点か」を踏まえて探索させる。
3. 発見に専念させる。`security-scanner`には検証もPoCもさせない（これは別エージェントの仕事）。1.の原則「**発見と検証を分離する**」を、ここでは役割を分離するように実装しています。

そして、この「発見に専念」させるプロンプトは、簡素にしています。元記事ではこう釘を刺しています。

> 原文: Counterintuitively, more prescriptive prompts make discovery worse—long checklists tend to reduce the model's creativity and generate fewer novel bugs.  
> 訳: 直感に反して、規定的すぎるプロンプトは発見をむしろ悪くする——長いチェックリストはモデルの創造性を下げ、新規のバグを生みにくくする。

そのため`security-scanner`には「目的（この攻撃面で脆弱性を探せ）と文脈（THREAT\_MODEL）」だけを渡し、どう探索するかはモデルに委ねています。

（これはskillを作るときの勘所と同じだと思います。手順をガチガチに固めるほど、そのときのモデルには最適でも、将来モデルが賢くなったときの恩恵を受けられなくなる。"やり方"ではなく"狙い"を書くほど、モデルの成長の恩恵を受けられる、という考えです。）

### 3.4 ④Verification — 3ペルソナの多数決とライブPoC

③Discoveryが広く挙げた候補を、④Verificationで "本物だけ"に絞り込みます。1.の原則「**発見と検証を分離する**」に則り、検証者は独立したエージェントとして実装しました。

④Verificationで行うのは3ペルソナの多数決と、ライブPoCです。

#### 多数決 — 3つのペルソナに独立して「反証」させる

`security-verifier`というサブエージェントを3体、それぞれ違うペルソナで起動します。

* 懐疑的な監査者：「これは本当に悪用できるのか？」を疑う。
* コードを守る保守者：「いや、ここはこう守られている」と反論する立場。
* レッドチーム：「自分が攻撃者なら、こう攻める」と悪用経路を組み立てる。

3体それぞれが③Discoveryで検知したfindingsを独立して確定 / 反証し、多数決で判定します。設計のポイントは、各エージェントに"反証"をさせる点です。「正しいか確認して」ではなく「間違っていると言える理由を探して」と指示します。「検証者は同意マシンになりがち」という点を、役割を反転させることで回避しています。

さらに、発見者（`security-scanner`）の推論は検証者に見せません。渡すのは「findings」と「現行コード」のみです。発見時の"それらしい説明"がアンカリング効果となり検証者が同意してしまうのを防ぐためです。

#### ライブPoC — 「動くexploit」で確かめる

動的に安価に試せるfindingは、`security-poc-runner`を起動してPoC環境で実際にexploitを流します（環境は3.2で用意した段階から選びます。例えばfrontendはブラウザ越しにPlaywrightで観測）。

1.のとおり、**動くexploitは多数決より優先**ですので、ライブPoCが成功したらそのfindingは多数決を省略してよいことにしています。

### 3.5 ⑤Triage — 重複を防ぎ、人間が確認し、Sprintへ渡す

④Verificationを通過したfindingsを、どうSprintに渡すかがこのステップです。ポイントは3つ：

* A. 重複起票を防ぐ
* B. 起票前の人の承認
* C. SECは修正せずSprintに渡す

#### A. 重複を防ぐ — 既存Issue突合（NEW / KNOWN / REGRESSION）

同じリポジトリでDiscoveryを再実行すると、前回すでにIssueにした（けどまだ直していない）findingsが検知されます。重大度が低くて塩漬けしているものは特にそうです。放っておくと同じIssueを何度も起票してしまうため、起票の前に既存のIssue（open＋直近closed）と突合し、findingsを3つに分類します。

| 分類 | 状況 | アクション |
| --- | --- | --- |
| NEW | 一致する既存Issueなし | 起票候補にする |
| KNOWN | 一致するopen Issueあり（未対応） | 新規起票しない。該当Issueに「再検出」コメントだけ付ける |
| REGRESSION | 一致するIssueがclosed（修正済み） | 再オープンor新規起票し「再発」と明記 |

照合はタイトル / `file:line` / 攻撃面の意味照合で「同じ根本原因を指しているか」をSECが判断します。

ひとつ大事なのは、③Discoveryと④Verificationでは既存Issueを見せないことです。「前回こう書いた」を見せると、発見も検証もそれに引っ張られます（アンカリング効果）。そのため突合（既存Issuesの参照含む）はこのステップだけで行い、③Discovery、④Verificationは毎回まっさらな状態で走らせます。

#### B. 起票の前に、人間が確認する

SECは起票候補を一覧で提示します。タイトル / 重大度 / 判定根拠 / NEW・KNOWN・REGRESSION / 束ね方、など。  
その後、人間がGoを出してからIssue起票するようにしています。  
AIが見つけたものを素通しでIssueにすればalert fatigueが発生する可能性があるため、念のため確認するようにしています。

Issueを起票する際は、検証の証跡（多数決の内訳 / PoCのHTTP応答・DB証跡）をコメントに残しています。

#### C. SECは直さない — Patchingは通常Sprintへ

SECの仕事は、「見つけて・裏取りして・起票する」までです。修正（Patching）はしません。

起票されたIssueは、通常の開発フローに合流します。POがRefinementでAC / ストーリーポイントを付け → DEVがTDDで修正＋回帰テスト。こうすれば、既存チームの品質保証（テスト・レビュー・PR）がそのまま活かせます。

最後に、SECはDiscovery&Verificationフローの実行ごとに `summary.html` を出力し、その回の結果（Scan取込 → Discovery件数 → Verificationの結果 → 突合のNEW / KNOWN / REGRESSION内訳 → 起票）をまとめます。

### 3.6 フォルダ構成とエージェント一覧

#### ステップ × エージェント（どのステップで誰が動くか）

`CLAUDE.md` に「SECモードで動いて」と指示するとSEC（security-lead）が起動し、Discovery&Verificationフローを開始するように設定しています。  
起動したSEC（security-lead）は、その後オーケストレータとして動き、③Discovery、④Verificationではサブエージェントを並列起動します。⑤Triageでは人間が読む用に今回フローの結果（summary.html）を出力します。

![](https://static.zenn.studio/user-upload/d515cd2fb3ce-20260723.png)

#### フォルダ構成（`.claude/agents/`）

エージェント定義は、既存のスクラムチームと同じ[`.claude/agents/`](https://github.com/ryokkon624/scrum-agent-base/tree/main/.claude/agents)に、定義しています。★ が今回追加したものです。今回追加したものは[PR](https://github.com/ryokkon624/scrum-agent-base/pull/29)にまとまっています。

```
.claude/agents/
├── scrum-master.md          … SM（既存：イベント進行）
├── product-owner.md         … PO（既存：Refinement）
├── developer.md             … DEV（既存：実装・TDD）
├── convention-reviewer.md   ┐
├── performance-reviewer.md  │ 既存：DEV実装後のレビュアー群
├── security-reviewer.md     ┘
├── security-lead.md       ★ SEC：Find-and-Fix Loopのオーケストレータ
├── security-scanner.md    ★ Discoveryワーカー（攻撃面で並列起動）
├── security-verifier.md   ★ Verificationワーカー（多数決の1票）
└── security-poc-runner.md ★ ライブPoCワーカー
```

新設した4つの役割です。

| ファイル | 役割 | フロー上の登場箇所 | ポイント |
| --- | --- | --- | --- |
| `security-lead.md` | SEC（オーケストレータ） | 全ステップを指揮 | 「作る」ではなく「見つけて裏取り」。修正はしない |
| `security-scanner.md` | Discoveryワーカー | ③Discovery | 攻撃面ごとに並列起動、THREAT\_MODELを文脈に発見に専念（検証しない） |
| `security-verifier.md` | Verificationワーカー | ④Verification | 3ペルソナの1票、反証して過半数で判定 |
| `security-poc-runner.md` | PoCワーカー | ④Verification | PoC環境で実証、後始末 |

（既存のSM / DEV / PO / レビュアー群は前回記事で解説済みなので、ここでは割愛します。）

## 4. 学び

追加したDiscovery&Verificationフローを数回実行して得た学びです。

* 知見①：ルールベースのScanとAI深掘りは二層構造がGood
* 知見②：独立検証は両方向に働く——過大主張を落とし、見落としを格上げする
* 知見③：無変更コードでも二周目は異なる結果に——"一発"でなく回を重ねるのが吉

### 4.1 Scanの結果 — ルールベースが拾えるもの／拾えないもの

定期Scan（ルールベース）を、infraとアプリコードの両方に当てました。

#### infra（Trivy／IaCスキャン）

15件上がりました。そこに、THREAT\_MODELで校正・重複排除・重大度を再評価すると、このようになりました。

| Trivy重大度 | ルール | 件数 | 校正後の判定 |
| --- | --- | --- | --- |
| critical | AWS-0067 Lambda権限にsource ARN無し | 1 | 中・要対応（IAM過剰） |
| critical | AWS-0104 egress 0.0.0.0/0 | 3 | 低（一般に許容）→ 任意ハードニング |
| high | AWS-0052 ALB不正ヘッダ未破棄 | 1 | 中・要対応（簡単な改善） |
| high | AWS-0053 ALBがインターネット公開 | 1 | 棄却（公開API＝設計どおり） |
| low | AWS-0017/0124/0034/0066暗号化・説明・可観測性 | 9 | 低・任意 |

Trivyがcriticalとしたegress(0.0.0.0/0) は「一般に許容」で低へ、ALBのインターネット公開は「公開APIなのだから設計どおり」で棄却へ。criticalのIAM過剰だけは影響範囲を見て「中・要対応」に残す。結果、15件のうち"本当に手を動かすべき"は「中・要対応」の2件。ルールベースのcriticalを、そのままcriticalとして受け取らず、過大評価を抑えられたケースとなりました。

#### アプリコード（Semgrep／SAST）

backendでは0件でした。つまり、ルールに一致する"既知"の脆弱性はないという結果です。  
しかし、次の4.2で見るとおり、Scanで0件だったbackendから、AI深掘りはCriticalを検出します。

### 4.2 Discovery → 反証&多数決 — 独立検証は「両方向」に働く

Semgrepが0件だったbackendで、AI深掘りが7件検知しました——Critical 1・High 2・Mid 4。

下表は、Discoveryが挙げた主張が、Verification（ライブPoC／3ペルソナ多数決）でどうなったかを表しています。最終判定列の ↑↓ が、初期重大度から動いた向き（↓＝過大主張の棄却／↑＝見落としの格上げ）を示しています。

| No. | リポジトリ | Discoveryの主張 | 初期重大度 | ライブPoC | 3ペルソナ多数決 | 最終判定 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | backend | Google OAuthのidToken aud未検証 → 乗っ取り | Critical | 実証成功 | - PoCで実証済み | Critical |
| 2 | backend | bodyのhouseholdIdを信頼 → 世帯越境write（IDOR） | High | 実証成功 | CONFIRMED 3/3 | High |
| 3 | backend | fileKey未検証 → クロステナントS3読取 | High | 実証成功 | CONFIRMED 3/3 | High |
| 4 | backend | 招待トークンの認可漏れ | Mid | - | CONFIRMED 3/3 | Mid |
| 5 | backend | 招待トークンが“推測できる” | Mid | - | REFUTED 3/3 | ↓棄却 |
| 6 | backend | 認証ハードニング：refresh失効不能・レート制限なし・admin粒度 | Mid | 実証成功 | CONFIRMED 3/3 | Mid |
| 7 | backend | 認証：nonce=Math.random・ユーザー列挙（認証系） | Mid | - | REFUTED 3/3 | ↓棄却 |
| 8 | batch | AI返信バッチ：呼び出しにタイムアウト・入力上限なし＋全件を1トランザクション直列 | Low | - | CONFIRMED 3/3 レッドチーム視点で見落としを発見 | ↑Mid |

※No.2,3,6は多数決で確定させた後に「PoC環境のテスト」を兼ねてPoCを実施しました。本来はPoCで実証済みであれば多数決は省略しています。

この表から、独立検証が両方向に働くことが分かります。

#### 方向1：過大主張の棄却。

* No.5：招待トークンを「推測できる」というものは、多数決でREFUTED。実装は `SecureRandom` 由来の122bitで、推測は現実的でない。
* No.7：認証まわりの「`nonce = Math.random()`」は 事実だが悪用不可（完全性はHMACが担保し、nonceの一意性は使っていない）。「ユーザー列挙」は未知メールも誤パスワードも同じ401で、区別できないと反証。

もし発見と検証を同じエージェントにやらせていたら、これらは"それらしい指摘"のままIssueになっていた可能性があります。検証者に発見者の推論を見せず、反証を仕事として与え、多数決を取ることで過大主張を削ぎ落としました。

#### 方向2：見落としを格上げする。

batchのNo.8で、Discoveryは外部API呼び出しにタイムアウトや入力上限が無く全件を1トランザクションで直列処理する点を「Low」と付けていました。遅延や大きな入力でリソースを長く握る、というコスト寄りの見立てです。ところが独立検証（特に攻撃者視点のレッドチーム）が現行コードを追うと、より重いfindingを見つけました。このバッチはエラーが出た時点でその実行を打ち切り、次回も古い順に同じ問い合わせから処理し直します。つまり確実にエラーになる問い合わせを1件仕込むだけで、その実行の後続が止まり、しかもその1件が毎回先頭で実行されて継続的に封じられてしまいます。1実行あたりのコストの話が、全ユーザーの可用性の話に変わりMidへ格上げしています。（補助機能でデータ喪失は無いためMidどまり）

### 4.3 二周目はどうなるか

元記事は、初回は一発で終わらせず、複数回まわせと勧めています。

> 原文: On your first iteration with a codebase, you should run the loop multiple times, deciding when to stop based on the number of net-new findings and your risk tolerance for that system.  
> 訳: コードベースに対する初回は、ループを複数回まわし、"新規に増えたfindings（net-new）"の数と、そのシステムに対する許容リスクを見て、いつ止めるかを決めるべきだ。

そして、コードを変更していなくても、検知されると言っています。

> 原文: However, don't expect the *nth* run to have zero new findings. Models are stochastic, and a large codebase can have a long tail of vulnerabilities that continue to trickle in even when the code is unchanged.  
> 訳: ただし、n回目の実行で新規のfindingsがゼロになると期待してはいけない。モデルは確率的であり、大きなコードベースには、コードが変わっていなくても断続的に検出され続けるような"脆弱性のロングテール"がある。

frontendでコードを変更していない状態で2周目を実行してみました。

#### 結果：差分は加算的、そして拾い物もあり

今回のケースでは、記事の内容と一致しました。

* 一周目で確定した主要なfindingsは、二周目でもほぼそのまま再現。全部がランダムに入れ替わるわけではなかった。
* 前回出なかった新規findingsが検知された。ただし記事の言う *diminishing returns*（逓減）どおり、新しく出るものほど重大度は低めという結果になった。
* 新規の中に、アプリのバグが1件混じっていた。（拾い物）

つまり、二周目は、カバレッジの上積みとなる結果になりました。

#### だから「継続的に実行する」仕組みが要る

二周目に価値があるなら、三周目にもあるはずです。コードは変わり続け、モデルも更新されます。Discoveryは"一度対応して終わり"にはできず、回し続けるほど、カバレッジは積み上がります。

しかし、毎回この一連（Scan → AI深掘り → 3ペルソナ検証 → PoC → 突合 → 承認 → 起票）を人間がプロンプトを書いて回すのは、現実的ではありません。だからこそ、本記事で作ってきた、継続的に実行できる"仕組み"が必要だと考えます。

## 5. まとめ

### 「継続的に実行する」とは何だったか

この記事のタイトルは「Using LLMs to secure source codeを継続的に実行する」でした。この"継続的に"とは、一発の完璧なスキャンを狙わないことにあります。

* 発見は確率的で、二周目でも新しいfindingsが検知される
* ルールベースの外側は、AI深掘りでしか埋まらない
* AIが検知したfindings候補は、独立検証で選別しないと"alert fatigue"が発生する

だから、AnthropicのFind-and-Fix Loopを回し続けられる仕組みが要る。既存のスクラムAIエージェントチームにSECというロールを追加し、Discovery → Verification → Triageを別フローで回し、確定した本物だけを通常SprintでPatchする——これが今回やったことです。

## 6. おまけ：Fable5で実行すると

記事に合わせてモデルはOpusで実行していたのですが、異なるモデルを使うと異なる観点で探索し、結果も異なるのではないかと予測しました。ちょうどFable5が利用できる期間であったため実行してみました。

結果は、Fableのセーフガードが発動し、Opusに切り替わりました。おそらく脆弱性探索という文脈がひっかかったのでしょう。「別モデルで別観点」というのは試せませんでしたが、Opusによる2周目（§4.3）を実験することができました。

実験できませんでしたが、「別モデルで別観点」ができるのであれば、`security-scanner`にモデルの多様性（攻撃面 \* モデル）を組み込むのも面白そうではあります。
