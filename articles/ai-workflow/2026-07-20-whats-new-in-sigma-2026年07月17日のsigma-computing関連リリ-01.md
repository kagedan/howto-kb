---
id: "2026-07-20-whats-new-in-sigma-2026年07月17日のsigma-computing関連リリ-01"
title: "What's New in Sigma - 2026年07月17日のSigma Computing関連リリース情報まとめ"
url: "https://zenn.dev/truestar/articles/7aa44cdb6b8302"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "OpenAI", "zenn"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/e6f5050f33c8-20260720.png)

Sigma(Sigma Computing)の最新リリースノート情報を集約・要約して紹介しているコミュニティスレッド『**[Release Notes](https://community.sigmacomputing.com/c/welcome-center/release-notes/31)**』。米国時間毎週金曜日中(日本時間土曜日早朝)に定期的に公開されているこちらのスレッドの内容について、個人的情報観測も兼ねて公開されたタイミングで目を通すようにしています。

当エントリではこのコミュニティスレッドにおける**2026年07月17日**付けの投稿について、内容を要約・咀嚼理解したものを紹介します。

## TL;DR

2026年07月17日のSigmaリリースにおける主なトピック、目玉は以下の通り。

* **Sigma agentのデータソースにdata modelのテーブルを追加できるように(Beta)**：
  + これまでワークブック内の要素に限られていたagentのデータソースが、data modelのテーブルにも対応。長らく待たれていたagentとData Modelの組み合わせがようやく実現した。
* **AI usage dashboardが本格運用フェーズへ**：
  + agentやAssistantのtoken消費量を横断的に可視化できるダッシュボード。旧来の[Assistant usage dashboard](https://help.sigmacomputing.com/docs/assistant-usage)は**2026年6月2日より前にセットアップ済みの組織のみ**利用可能な状態になっており、**2026年9月15日以降は完全に廃止**される予定。まだ移行していない場合は早めの対応が必要。
* **Claude / OpenAI / Snowflake Cortex AIそれぞれのAI費用可視化テンプレートが登場**：
  + 各AIベンダーの利用コストをウェアハウス上のデータから可視化できるテンプレート一式。Claude Enterpriseを使っている組織には特に嬉しいアップデート。
* **アプリテンプレートがBetaで10種類追加**：
  + プロジェクト管理や需要予測、チケット管理など業務ユースケース別のテンプレートがまとめて登場。
* その他：
  + Assistantのビルドモードでの数式結合キー対応やバランスシート作成支援(いずれもBeta)、Sigma Tenantsへのフォルダ / レポートのデプロイ拡充とデプロイ依存関係の可視化(Beta)、ボタン・ナビゲーション要素のアイコン対応(GA)、カスタムメールブランディングの設定場所変更や送信者情報の非表示設定などが含まれる。

## リリース内容詳細

今回のリリースに含まれるトピックの一覧と、各トピックのステータスは以下の通り。

| No. | カテゴリ | トピック | ステータス |
| --- | --- | --- | --- |
| 1. | AI | Sigma agentのデータソースにdata modelのテーブルを追加(Beta) | Beta |
| 2. | AI | Assistantのビルドモード: 数式による結合キー対応(Beta) | Beta |
| 3. | AI | Assistantのビルドモード: バランスシート作成支援(Beta) | Beta |
| 4. | Admin | AI usage dashboard(AI利用状況ダッシュボード) | - |
| 5. | Admin | 利用状況データに関する自然言語での質問 | - |
| 6. | Admin | テナント組織へのコンテンツデプロイの拡充(3件: フォルダのデプロイ / レポートのデプロイ / ドキュメントの手動再デプロイ)(Beta) | Beta |
| 7. | Admin | デプロイメントポリシーでの依存関係の可視化 | - |
| 8. | Templates | AI費用可視化テンプレート(Claude / OpenAI / Snowflake Cortex AI) | - |
| 9. | Templates | アプリテンプレート(Beta) | Beta |
| 10. | Workbook elements | ボタンとナビゲーション要素のアイコン対応(GA) | GA |
| 11. | Workbook features | カスタムメールブランディングとSMTPサーバー設定の移動 | - |
| 12. | Workbook features | エクスポートメールでの送信者情報の非表示 | - |

### 1. Sigma agentのデータソースにdata modelのテーブルを追加(Beta)

#### この機能は何？どういう機能？

Sigmaのagent機能は、ワークブック内にAIエージェントを組み込み、データソースやツール(action、warehouse agent、warehouse search service、MCPツールなど)をもとに自然言語で対話できるようにする仕組みです。これまでagentのデータソースにできるのは、ワークブックに追加済みのテーブルやピボットテーブル、チャート、input tableといった「要素」に限られていましたが、今回のアップデートでdata model(複数テーブルの結合やmetricsの定義をまとめて管理する仕組み)のテーブルも直接データソースとして追加できるようになりました。詳細は公式の[Build Sigma agents](https://help.sigmacomputing.com/docs/build-agents)にまとまっています。

#### 具体的に何が出来るの？

* agentの設定画面でデータソースを追加する際、data model由来のテーブルを選択できるようになります。
* data model側でmetricsを定義していても、そのmetricで使われている列がagentから見える状態であれば、agentはmetricsを利用できます。
* data model由来のデータソースの場合、relationship(リレーションシップ)経由のrelated columnやmetricsにはagentからアクセスできない点は現時点の制約として明記されています。
* agentはRBAC(ロールベースアクセス制御)を尊重するため、ユーザーがアクセス権を持つデータ・ツールしか使えません。Beta機能なので、本番のガバナンス要件に組み込む前にはGA化のタイミングを確認しておくと安心です。

#### 誰が/何が嬉しい？

* **data modelを中心にガバナンスを組んでいるSigma管理者**：
  + dataset単位ではなくdata model単位でagentのコンテキストを統一管理でき、二重管理を避けられる。
* **AI apps・ダッシュボードを作るワークブック開発者**：
  + data modelの内容をわざわざワークブック側に複製しなくても、そのままagentの文脈として使える。

### 2. Assistantのビルドモード: 数式による結合キー対応(Beta)

#### この機能は何？どういう機能？

Sigma Assistantには、ワークブックの作成や編集を対話的に進められる「ビルドモード」があります。これまでテーブル同士のjoin(結合)をAssistantに任せる場合、生の列同士の一致でしか結合キーを指定できませんでしたが、今回のアップデートで数式や式(formula)を使った結合キーにも対応しました。

#### 具体的に何が出来るの？

日付を丸めた値や、テキストを正規化した値、その他任意の数式から導出した値を結合キーとして使えます。「日付を月単位に丸めた値」同士や「大文字小文字を統一したテキスト」同士でのjoinを、Assistantに自然言語で依頼できるようになります。Beta機能のため、複雑な結合ロジックを伴う本番ワークブックに組み込む際はGA化を待つか、挙動を検証してから採用するのが安全です。

#### 誰が/何が嬉しい？

* **表記ゆれのあるデータを結合したいアナリスト**：
  + 生の列だけでは結合できなかったデータ同士も、Assistantに任せて素早く結合できる。

### 3. Assistantのビルドモード: バランスシート作成支援(Beta)

#### この機能は何？どういう機能？

Sigma Assistantのビルドモードには、これまでP&L(損益計算書)や売上予測を組み立てるガイド付きワークフローが用意されていましたが、今回新たに貸借対照表(バランスシート)作成のガイド付きワークフローが追加されました。

#### 具体的に何が出来るの？

手元のデータ構造に合わせて、スナップショット形式(ある時点の残高)と比較形式(期間比較)の両方のレイアウトに対応します。財務系のワークブックをゼロから組むよりも、一貫した構造で素早くセットアップできます。

#### 誰が/何が嬉しい？

* **FP&A・経理部門でSigmaを使う担当者**：
  + フォーマットが決まった資料を、毎回同じ構造でスピーディに作成できる。
* **すでにP&Lや売上予測のワークフローを使っているチーム**：
  + 財務レポート一式をSigma Assistant経由で統一的に組み立てられるようになる。

### 4. AI usage dashboard(AI利用状況ダッシュボード)

* カテゴリ：Admin
* ステータス：明記なし(GA相当)

#### この機能は何？どういう機能？

組織全体で、Sigma agentやSigma Assistantといったtokenを消費するAI機能の利用状況を横断的に可視化するダッシュボードです。詳細は[AI usage dashboard](https://help.sigmacomputing.com/docs/ai-usage)にまとまっています。Overview / Agents / Assistant: Viewer / Assistant: Builderの4タブで構成され、ユーザーやAIプロバイダー、会話のsentiment、日付でフィルタできます。

#### 具体的に何が出来るの？

ダッシュボードは**Add to workspace**でワークブックとして自分のDocumentsフォルダに複製し、カスタマイズできます。token消費量に対してconditional alert(条件付きアラート)を設定でき、たとえば「1日あたりのtoken消費が10,000を超えたらメール通知」といった運用ができます。権限があれば、`AI_USAGE_<ORGANIZATION_NAME>`という名前のテーブルとして、connection browser経由でも生データを参照できます。

**重要な移行事項**: 旧来の[Assistant usage dashboard](https://help.sigmacomputing.com/docs/assistant-usage)は既にDeprecated(非推奨)扱いとなっており、**2026年6月2日より前にセットアップ済みの組織でのみ**利用可能です。まだ設定していない場合はAI usage dashboardを新規に使う必要があり、既存のAssistant usageデータは[Migrate Assistant usage data to AI usage](https://help.sigmacomputing.com/docs/configure-a-usage-dashboard-for-assistant#migrate-assistant-usage-data-to-ai-usage)の手順で移行できます。Assistant usage dashboard自体は**2026年9月15日以降に完全に削除**される予定です。

#### 誰が/何が嬉しい？

* **AIコストをガバナンスしたいSigma管理者**：
  + agentとAssistantの利用状況をひとつのダッシュボードで横断的に把握でき、予算超過の兆候を早期に検知できる。
* **旧Assistant usage dashboardを使ってきた組織の管理者**：
  + 2026年9月15日の廃止に向けて、早めにAI usage dashboardへの移行を計画する必要がある。

### 5. 利用状況データに関する自然言語での質問

#### この機能は何？どういう機能？

Users・Document Activityという既存の利用状況ダッシュボードに、ダッシュボード内のデータについてAIエージェントへ自然言語で質問できるオプションが追加されました。

#### 具体的に何が出来るの？

利用するにはSigma組織にAIプロバイダーが設定されている必要があります。エージェントと対話しない限りtokenは消費されません。

#### 誰が/何が嬉しい？

* **利用状況レポートを毎回自分でフィルタして読み解いていた管理者**：
  + グラフを読み込む代わりに「先月一番アクティブだったチームは？」のように聞くだけで済むようになる。

### 6. テナント組織へのコンテンツデプロイの拡充(3件: フォルダのデプロイ / レポートのデプロイ / ドキュメントの手動再デプロイ)(Beta)

#### この機能は何？どういう機能？

Sigma Tenants(Beta)は、親組織から複数のテナント組織へワークブックやdata modelなどのコンテンツを配布できる仕組みです。今回のリリースでは、配布できる対象と操作の幅が広がりました。詳細は[Deploy content to tenant organizations](https://help.sigmacomputing.com/docs/deploy-content-to-tenant-organizations)にまとまっています。

#### 具体的に何が出来るの？

1. **📂 フォルダのデプロイ**: フォルダごと、その中のワークブック・レポート・data modelをまとめてテナント組織へデプロイできるようになりました。ただしexploration(探索用の一時ビュー)やshortcut(ショートカット)など未対応のファイルはデプロイされません。
2. **📊 レポートのデプロイ**: これまでワークブックやdata modelが対象だったデプロイに、レポートも加わりました。
3. **🔄 手動での再デプロイ**: デプロイメントポリシーの**Deploy to**タブでテナントを選び、**Redeploy to tenant**を選択することで、任意のタイミングでドキュメントを手動再デプロイできます。

デプロイされたドキュメントは、ソース側で公開(またはバージョンタグ付け)されるたびに自動更新され、テナント組織側では編集できない仕組みは従来通りです。なおSigma Tenantsはpremium機能のため、利用にはSigmaのアカウントエグゼクティブへの問い合わせが必要な点は留意してください。

#### 誰が/何が嬉しい？

* **マルチテナントでSigmaを展開しているプラットフォームチーム**：
  + フォルダ単位・レポート単位でも配布対象を選べるようになり、テナントごとの手動セットアップの手間が減る。
* **配布内容を細かく更新したい管理者**：
  + 公開を待たずに任意のタイミングで再デプロイでき、緊急の修正配布がしやすくなる。

### 7. デプロイメントポリシーでの依存関係の可視化

#### この機能は何？どういう機能？

テナント組織へドキュメントをデプロイする際、そのワークブックがデータソースとして使っているdata modelや、actionの遷移先になっている別のワークブックなど、依存関係にあるドキュメントも自動的に一緒にデプロイされます。今回、その依存関係をデプロイメントポリシー画面上で確認できるようになりました。

#### 具体的に何が出来るの？

デプロイメントポリシーの画面から、どのドキュメントがどんな依存関係を伴ってテナント組織にデプロイされているかをレビューできます。

#### 誰が/何が嬉しい？

* **複数ワークブックが絡み合った構成をテナントに展開している管理者**：
  + 「このワークブックをデプロイすると何が一緒に配布されるか」を事前に把握でき、想定外の依存関係を見落とすリスクを減らせる。

### 8. AI費用可視化テンプレート(Claude / OpenAI / Snowflake Cortex AI)

* カテゴリ：Templates
* ステータス：明記なし

#### この機能は何？どういう機能？

組織のAIツール利用コストを可視化するための、すぐ使えるテンプレートが3種類追加されました。データプラットフォームにコストデータが取り込まれていれば、対応するテンプレートで可視化できます。

#### 具体的に何が出来るの？

Claude spend templateを例にすると、以下のような構成になっています。

* サンプルデータ付きで提供されるため、[Anthropic Console](https://console.anthropic.com/)からエクスポートした実データを接続しなくても中身を確認できます。
* 想定するテーブル構成は、組織全体のコストを持つ`ANTHROPIC_ANALYTICS_ORG_COST_REPORT`、組織全体の利用量の`ANTHROPIC_ANALYTICS_ORG_USAGE_REPORT`、ユーザー単位のコストの`ANTHROPIC_ANALYTICS_USER_COST_REPORT`、日次アクティブユーザーの`ANTHROPIC_ANALYTICS_USERS_DAILY`、skill・connectorの利用状況を持つ`ANTHROPIC_ANALYTICS_SKILLS_DAILY` / `ANTHROPIC_ANALYTICS_CONNECTORS_DAILY`などです。
* テンプレートは大きく3ページ構成です。
  + **Executive overview**: 月次spend / token / requestのKPIや部門別スペンドの積み上げ棒グラフ、モデル別スペンドTop 5、input / output / cache関連のtoken内訳を確認できます。
  + **Adoption & engagement**: seat utilization(付与シートのうち実際に使われている割合)、日次・週次・月次アクティブユーザーの推移、部門別・職種別のスペンドを確認できます。
  + **Skills & connectors**: どのskillやconnectorがよく使われているか、その利用トレンドと詳細内訳を確認できます。
* 部門別・職種別ビューを使うには、`USER_ID_HASH`をキーに自組織のユーザーテーブルと結合する必要があります(Anthropic側はユーザー個人や部門の情報を提供しないため)。

#### 誰が/何が嬉しい？

* **Claude Enterpriseを全社導入している組織の管理者**：
  + どの部門・職種がどれだけAIコストを使っているかを、自前でダッシュボードを組まずに可視化できる。
* **複数のAIベンダーを併用している組織のFinOps担当**：
  + Claude・OpenAI・Snowflake Cortex AIそれぞれの専用テンプレートがあるため、ベンダーごとに比較しながらコスト管理できる。

#### その他観点

Claudeの活用度合いを定量的に説明する材料が欲しい人にとっては、社内向けのAI活用レポートを作る際の下敷きとしても使えそうです。

### 9. アプリテンプレート(Beta)

* カテゴリ：Templates
* ステータス：Beta

#### この機能は何？どういう機能？

Sigmaでアプリ(データ入力や業務フローを伴うワークブック)を作り始める際の出発点として使えるテンプレート群です。各テンプレートにはサンプルデータ、input table、agentがあらかじめ組み込まれています。詳細は[Get started with templates](https://help.sigmacomputing.com/docs/get-started-with-templates)にまとまっています。

#### 具体的に何が出来るの？

以下の10種類のアプリテンプレートが提供されます。

* Project Management(プロジェクト管理)
* Revenue Forecasting(売上予測)
* Demand Planning(需要予測)
* Pipeline Forecasting(パイプライン予測)
* Budget Variance Analysis(予算差異分析)
* Territory Management(テリトリー管理)
* Shift Management(シフト管理)
* Marketing Analytics(マーケティング分析)
* Headcount Planning(人員計画)
* Ticket Management(チケット管理)

Sigma **Home**の左側ナビゲーションから**Templates**を選ぶとテンプレートギャラリーを閲覧できます(閲覧には**Create, edit, and publish workbooks**権限が必要です)。

#### 誰が/何が嬉しい？

* **業務アプリをSigmaで内製したいチーム**：
  + ゼロから設計せずに、業務ユースケースに近いテンプレートを土台にできる。
* **Sigmaでのアプリ構築を学びたい人**：
  + テンプレートの構造を読み解くことで、自分でアプリを組む際の設計パターンを学べる。

### 10. ボタンとナビゲーション要素のアイコン対応(GA)

* カテゴリ：Workbook elements
* ステータス：GA

#### この機能は何？どういう機能？

ワークブック内のボタン要素や、ナビゲーション要素の選択肢にアイコンを設定できるようになりました。Sigmaが用意する検索可能なアイコンライブラリからすぐ使えるアイコンを選べます。

#### 具体的に何が出来るの？

[Button elements](https://help.sigmacomputing.com/docs/button-elements#customize-button-properties)のプロパティからアイコンを設定できます。[ナビゲーション要素](https://help.sigmacomputing.com/docs/use-the-navigation-element-to-guide-user-exploration#set-icons-for-navigation-options)の各選択肢にもアイコンを付けられます。GA機能なので、本番のアプリにもすぐ組み込んで問題ありません。

#### 誰が/何が嬉しい？

* **業務アプリのUIを整えたいワークブック開発者**：
  + テキストラベルだけよりも視覚的にわかりやすいナビゲーションを組める。

### 11. カスタムメールブランディングとSMTPサーバー設定の移動

* カテゴリ：Workbook features
* ステータス：明記なし(設定場所の変更)

#### この機能は何？どういう機能？

カスタムメールブランディングとSMTPサーバー設定のオプションが、**Administration** > **Scheduled exports & actions**内の**Email customization**タブに移動しました。従来は**Settings**タブにあった設定です。

#### 具体的に何が出来るの？

設定できる項目自体は従来と同じで、[Customize email branding](https://help.sigmacomputing.com/docs/custom-email-branding)にまとまっています。

* ロゴ画像のアップロード(推奨サイズは幅135px以上、アスペクト比3:1〜1:2)
* **Sender name**(送信者名。受信者には\*[Sender name] via Sigma Computing\*と表示されます)
* **Global Bcc email addresses**(すべての送信メールに既定でBccするアドレス)
* **Reply-to email**(返信先アドレス)
* **Signature name** / **Email footer**(署名・フッター)

カスタムブランディングの設定を1つでも入れると、Sigma標準のブランディングはすべて解除される点、およびunsubscribe(配信停止)オプションが無効になる点には注意が必要です。

#### 誰が/何が嬉しい？

* **メールブランディングを設定・運用してきたSigma管理者**：
  + 操作手順自体は変わらないが、設定場所を探すときに迷わないよう覚えておく必要がある。

#### その他観点

管理画面のナビゲーション変更は地味に見えますが、社内ドキュメントや手順書を書いている担当者には影響が大きいものです。手順書のスクリーンショットを更新しておくとよさそうです。

### 12. エクスポートメールでの送信者情報の非表示

* カテゴリ：Workbook features
* ステータス：明記なし

#### この機能は何？どういう機能？

スケジュールエクスポートやアクション経由で送信されるメールの本文には、誰がそのエクスポートをスケジュール・送信したかを示す一文が入ります。今回、その一文を非表示にできる**Hide sender information**設定が追加されました。

#### 具体的に何が出来るの？

メール本文中の送信者情報の行だけを非表示にする設定で、メールの「From」欄自体には影響しません。[Customize email branding](https://help.sigmacomputing.com/docs/custom-email-branding)のオプションの一つとして設定できます。

#### 誰が/何が嬉しい？

* **顧客向けにエクスポートメールを送っている組織**：
  + 社内の担当者名を外部の受信者に見せたくない場合に使える。
* **メールテンプレートを自社ブランドで統一したい管理者**：

## Next Action

今回のリリース内容を踏まえて、すぐ動けるアクションを読者・ユーザー層別に整理します。期限が決まっているものを優先度高めに並べています。

### Sigma管理者

* 旧Assistant usage dashboardを使っている場合は**2026年9月15日までに**AI usage dashboardへの移行を完了させる。[Migrate Assistant usage data to AI usage](https://help.sigmacomputing.com/docs/configure-a-usage-dashboard-for-assistant#migrate-assistant-usage-data-to-ai-usage)の手順を確認しておく。
* Claude / OpenAI / Snowflake Cortexのいずれかをすでに使っている場合は、該当するspend templateをサンプルデータでまず触ってみる。
* Sigma Tenantsを使っている場合は、フォルダ・レポートのデプロイ拡充と依存関係の可視化を確認する。

### ワークブックを作るビルダー

* Sigma agentにdata modelのテーブルを追加できるようになったので、既存agentのデータソースをdata model側に寄せられないか検討する。
* ボタン・ナビゲーション要素のアイコン対応(GA)はすぐ試せるので、業務アプリのUI改善に使ってみる。

### 触ってみる枠

* アプリテンプレート10種類をSigma **Home** > **Templates**から一通り眺めて、自組織で使えそうなものがないか確認する。
* Assistantのビルドモードで、数式を使った結合キー指定を試してみる。

## 参考文献(全体)

## この記事を読んだ方へ

感想・フィードバックは X（[@shinyaa31](https://x.com/shinyaa31)）までお気軽にどうぞ。
