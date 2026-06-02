---
id: "2026-06-01-多様なdbからアサイン提案-人事エージェントtarentscopeの紹介-01"
title: "多様なDBからアサイン提案-人事エージェントTarentScopeの紹介"
url: "https://zenn.dev/joesaber/articles/18ca9616d99888"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

## デモ動画

<https://www.youtube.com/watch?v=k65vZEHs_0U>

---

## なぜ人事判断は「AI の出番」なのか

人事異動・プロジェクトのアサイン決定は、**組織全体のパフォーマンスを左右する経営判断**です。

しかし現実はどうでしょうか。100人の異動案を作るだけで、その組み合わせは膨大。人間が「勘と経験」で比較できるのはせいぜい数十通りです。残りの選択肢は、**最適解ではなく「ましな解」、もしくは人事部がてきとうに選んでいるに過ぎません。**

さらに深刻なのは、**必要な情報がすべての企業に存在するのに、それを統合する仕組みがない** ということです。

* 職歴・希望 → HR システム
* スキル → スキルシート
* 実績・貢献度 → プロジェクト管理ツール / GitHub
* 発言傾向・問題解決能力 → Slack / 会議録
* 本当の適性 → マネージャーの頭の中

**これらを「同時に」読んでいる人間は存在しません。** 100人超の情報を一元管理し、制約条件下で最適なチーム構成を導き出すことは、人間には物理的に不可能です。このDBを統合し、最適な人事戦略を提案するのが、今回つくったTarentScopeというわけです。

余談ですが、最近、富士通が企業の人事異動案を AI で自動提案するシステムを開発してました。大企業もやっぱりそこに業務課題を感じていたということを知り、ちょっと元気づけられました。  
<https://www.youtube.com/watch?v=IyhUpBkjAAo>

---

## 現場で起きていると思われる3つの根本問題

### 問題1：「データの分散」が判断を妨げる

ソフトウェア企業ほど深刻です。

* 「誰がLLMの最新トレンドに詳しいか」を実は誰も把握していない
* プロジェクト間で技術スタックが異なるため、スキル比較が困難
* Slack の技術チャネルに議論は溜まるが、「あの話題は誰が主導してたっけ？」と属人的になる

**結果**：正確な評価ではなく「見える範囲での推測」で判断が進みます。

### 問題2：「複雑さ」が最適化を阻む

100人の異動には 10^158 通りの組み合わせがあります。

人間が直感的に比較できるのは数十通りです。チーム間のシナジー、技術スタックのバランス、個人の成長機会、通勤時間などの制約を **同時に最適化** することは、人間にはできません。

**結果**：「なんとなく良さそう」という判断の集積になり、事後的に「あの異動、失敗だったね」と評価されます。

### 問題3：「根拠」がないまま決定される

> 「小林さんはバックエンド得意だから、このプロジェクトに」

その根拠は何でしょうか。

* GitHub のコミット数？ 2年前のスキルシート？ 管理職の直感？

根拠がないと：

* 本人が納得できず、モチベーション低下
* 人事異動の説得力がない
* 判断が組織に蓄積されず、次も同じ試行錯誤が繰り返される

---

## TalentScope — 「データ × AI」で証拠ベースの人事へ

上記の 3 つの問題は、実は **1 つのプラットフォーム** で解決できます。

Slack / Notion / GitHub を横断して読み込み、各メンバーの **スキル・貢献度・適性・成長傾向を自動分析** し、**制約条件下で最適なチーム構成を提案する AI エージェント**。それが TalentScope です。

## 

## 実装上の工夫と機能

TalentScope は、Slack / Notion / GitHub を横断して読み込み、**証拠ベースで人材を評価・分析するAIエージェント**です。

チャット形式で操作し、現在デフォルトで3つのモードを備えています。

| モード | できること |
| --- | --- |
| 💬 チャット | 「誰が○○に詳しい？」「このプロジェクトの状況は？」など自由質問 |
| 👤 個人スキル分析 | 特定メンバーのスキル・貢献度・議事録での発言傾向をレポート出力 |
| 📋 アサイン提案 | プロジェクトに誰を・どの役割で・いくらのコストでアサインすべきかをチーム単位で提案 |
| ✏️ レポート修正 | 出力済みのレポートをチャットで指示して再編集 |

因みにこのモードは後から追加可能です。現在はシステムプロンプトしかいじれませんが、いずれもっと細かい設定を加えられるようにしていきたいとおもっています。

---

## 工夫点２つ

### 1. 制約違反を自分で検知し、再提案する

TalentScope の評価エージェントは **2種類** あります。

**① ステップ確認エージェント**

アサイン提案のような複雑なタスクでは、メインエージェントへの指示（計画）が長くなりがちです。LLM は途中で「もう十分な情報が揃った」と判断し、未実行のステップをスキップして先に進んでしまうことがあります。

このエージェントは「計画に含まれるすべてのステップが実行されたか」をチェックし、不足があればメインエージェントに次のアクションをフィードバックします。ユーザーの関与なしに、自動でループが走ります。

**② レポート評価エージェント**

生成された提案レポートを **2軸** で検証します。

提案 → 評価 → フィードバック → 再提案という ReAct パターンのループが、2段階の評価を通過するまで自動で走ります。ユーザーは何も言っていません。

### 2. 使うほど、判断基準が蓄積される

> 「シニアと若手を必ず1名ずつ含めてほしい。コストよりスキルマッチを優先してください。」

このような定性条件をチャットで伝えると、AI設定タブで「会話から学習」ボタンを押すことで次回以降の提案に引き継がれます。毎回同じことを言わなくてもいい状態になっていきます。

---

## アーキテクチャ

![](https://static.zenn.studio/user-upload/de20a2e3df7f-20260601.png)

全体の構成はシンプルです。

```
[Notion / Slack / GitHub]
        ↓（Ingest層が取り込み）
[Azure Cosmos DB]  ← 4コンテナ（members / projects / meetings / slack_channels）
        ↓
[Semantic Kernel エージェント群]
        ↓
[FastAPI + Next.js チャットUI]
```

エージェントは**Main Agent（Orchestrator）+ 5つのサブエージェント**で構成されます。

```
[Main Agent]
  ├──► [ConversationAnalysisAgent]  Slack + 会議録の発言傾向を横断分析
  ├──► [TaskAnalysisAgent]          タスク実績から貢献度・スキル深度を分析
  ├──► [MemberProfilerAgent]        1名を横断して ~300トークンのプロファイルを生成
  ├──► [TeamEvaluatorAgent]         提案チームをシナジー・バランス・コストで評価
  └──► [GitHubAnalyzerAgent]        GitHub の実装履歴・PRをスキル証拠として分析
```

### 処理フロー（Step 1〜5）

**Step 1 — モード判定**

受け取ったプロンプトを「モード判定 LLM」が分析し、処理モードを決定します。モードごとにシステムプロンプトが切り替わります。現在 **4 モード** を実装しています。

| モード | 役割 |
| --- | --- |
| アサイン提案 | Step 2〜5 のフルフローを実行し、チーム構成を提案 |
| 個人スキル分析 | 特定メンバーの横断分析レポートを生成 |
| 通常応答 | DB 検索を含む自由質問に回答 |
| レポート修正 | 生成済みレポートを指示に従って再編集 |

---

**Step 2 — 計画立案**

計画LLMが、ゴールに対する実行計画を作成します。この計画はStep4のステップ確認にもそのまま渡されます。

---

**Step 3 — 情報収集**

5種のサブエージェントとツール群が協調して情報を収集します。GitHub SA 以外は Notion / Slack のコンテンツを取り込んだ **Azure Cosmos DB** を検索します。GitHub SA のみ **GitHub MCP** 経由で外部 API にアクセスします。

すべてのエージェントは `ChatCompletionAgent + FunctionChoiceBehavior.Auto()` による **ReAct パターン**で動きます。コードで処理フローを強制するのではなく、LLM が自律的にツールを選び、必要な情報を集める設計です。

**エージェント別ツール一覧**

以下は各サブエージェントおよびオーケストレータが外部から呼べる主要なツール（`@kernel_function`）の要約です。

ConversationAnalysisAgent（SlackPlugin / MeetingPlugin）

* `get_slack_speaker_counts(project_id, date_from?, date_to?)` — 発言量集計
* `get_project_slack_messages(project_id, date_from?, date_to?, speaker_id?)` — PJチャット本文取得
* `get_member_slack_messages(member_id, project_id?, date_from?, date_to?)` — メンバー発言取得
* `get_project_meetings(project_id, date_from?, date_to?, limit?)` — 議事録 full\_text 取得

TaskAnalysisAgent（ContributionPlugin）

* `get_member_task_stats(member_id, project_id?)` — タスク貢献度・SP集計
* `get_project_tasks(project_id)` — プロジェクトタスク一覧
* `calc_project_cost(member_ids_json, project_id)` — チームコスト試算

MemberProfilerAgent（MemberPlugin / MeetingPlugin / ContributionPlugin / SlackPlugin）

* `list_all_members()` — 全メンバー概要
* `get_member_detail(member_id)` — メンバー詳細（スキル・Slack vlog 等）
* `find_members_by_skill(skill_name)` — スキル検索
* `get_member_schedule(member_id)` — 全プロジェクト在籍期間取得

TeamEvaluatorAgent（ContributionPlugin / SynergyPlugin / TeamBalancePlugin）

* `get_collaboration_matrix(member_ids_json)` — 協働実績マトリクス
* `evaluate_team_balance(proposed_team_json, project_requirements_json)` — LLMによる総合評価
* `find_skill_gaps(project_id, proposed_member_ids_json?)` — 必要スキルの不足検出
* `compare_members(member_ids_json, aspect?)` — メンバー比較

GitHubAnalyzerAgent（GitHubMCPPlugin）

* MCP経由ツール: `search_repositories`, `get_file_contents(owner,repo,path,branch?)`, `list_commits`, `list_pull_requests`, `get_pull_request`, `get_pull_request_files`, `search_code` 等

Orchestrator（Main Agent が公開するラッパー）

* メンバー/プロジェクト参照: `list_all_members()`, `get_member_schedule(member_id)`, `list_all_projects()`, `get_project_detail(project_id)`, `find_available_members(date_from, date_to?)`
* コスト/評価: `calc_project_cost(...)`, `evaluate_team_balance(...)`, `find_skill_gaps(...)`
* サブエージェント呼び出し（invoke\_\*）: `invoke_conversation_agent(...)`, `invoke_task_agent(...)`, `invoke_member_profiler(...)`, `invoke_team_evaluator(...)`, `invoke_github_analyzer(...)`
* 逆質問ツール: `ask_user_clarification(question, options_json?)`

---

**Step 4 — ステップ確認**

「ステップ確認 LLM」が、Step 2 で立てた計画のすべてのステップが実行されたかを照合します。未実行のステップがあればメインエージェントにフィードバックし、Step 3 に戻って続きを実行させます。完了するまでこのループが自動で走ります。

---

**Step 5 — レポート生成 → 評価ループ**

ステップ確認を通過すると、レポートを生成します。「レポート評価 LLM」が **2 軸** で検証し、問題があれば再提案を要求します。

* **絶対条件**：事前設定のルールをチェックリスト形式で検証。違反があれば即却下。
* **定性評価**：会社の方針・育成思想との整合性を自然言語で評価。

提案 → 評価 → フィードバック → 再提案のループが 2 軸を通過するまで自動で続きます。

> 通常応答モードでは Step 5 のレポート評価ループは走らず、情報収集後に直接回答を生成します。

## 

## 使用技術

| 項目 | 技術 |
| --- | --- |
| エージェントFW | **Semantic Kernel** |
| LLM | **Azure OpenAI** (gpt-4o) |
| DB | **Azure Cosmos DB** |
| バックエンド | FastAPI (Python) |
| フロントエンド | Next.js (TypeScript) |
| 実行基盤 | **Azure Container Apps** |
| データソース | Notion / Slack / GitHub |

Microsoft の技術を中核に据えた構成になっています。Semantic Kernel は ReAct パターンのエージェントを自然に実装できる点が採用の決め手です。

---

## 今後の展望

### 1. カレンダーや他PJのアサイン状況を同時に見ながら、もっと人間が使いやすくいじれるUIにする

現状のアサイン提案は、スキル・貢献度・適性・コストを見られる一方で、最終判断をする人が「どこをどう調整すればいいか」を直感的に操作しにくい部分があります。今後は、メンバーのアサインカレンダー、進行中プロジェクト、空き期間、兼務状況を1画面で見られるUIを追加し、候補の比較と調整をその場で行えるようにしたいです。

### 2. 評価エージェントを設けてもなお起こるハルシネーションを減らす

提案内容を評価エージェントでレビューしても、LLM 由来のハルシネーションを完全には消し切れませんでした。  
今後は、出力の各主張に対して必ず証拠リンクを付ける設計に寄せていきたいです。

### 3. Notion や Slack へ、アドバイスや提案まで書き込む

今はチャット上で提案を返すだけですが、実運用では「提案を見たあと、次の行動に移す」までが重要です。そのため、将来的には TalentScope が Notion や Slack に対して、分析結果をそのまま書き込めるようにしたいです。

たとえば、Notion のメンバーページに「最近は会議でのファシリテーションが増えている」「技術選定の相談役として存在感が高い」といったフィードバックを追記したり、Slack のプロジェクトチャンネルに「このPJはバックエンド強め、ただしデータ基盤担当が不足しているので補強候補を検討してください」といった提案を自動投稿したりする形です。

---

## おわりに

TalentScope が目指したのは、「AI が答えてくれるツール」ではなく、\*\*「AI が自律的に動いて、人事判断を支える仕組み」\*\*です。

Slack・Notion・GitHub・議事録——バラバラに存在していたデータが、エージェントを通じて初めて繋がります。「勘と経験」に閉じていた判断を、データと証拠の世界に引き出せるかもしれません。

富士通のケーススタディが示すように、この問題は「やれば成果が出る」ことが既に実証されています。あとは、それを **より汎用的に、より小さなコストで、より多くの企業で** 実現できるかどうかです。

まだ荒削りな部分もかなりありますが、「検索ではなく推論、回答ではなく行動」というエージェントの本質は、実際に動く形で示せたと思っています。
