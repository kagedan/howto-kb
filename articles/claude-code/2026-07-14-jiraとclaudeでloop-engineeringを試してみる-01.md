---
id: "2026-07-14-jiraとclaudeでloop-engineeringを試してみる-01"
title: "JiraとClaudeでLoop Engineeringを試してみる"
url: "https://zenn.dev/hittskapi/articles/4dbb0e4eb9b7b3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "LLM"]
date_published: "2026-07-14"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

## はじめに

Loop Engineeringが言われるようになって約１か月です。色々記事は読みましたが、理解を深めるために実践してみることにしました。**Jira好きなのでJiraとの組み合わせです。**

## Loop Engineeringについて

2026年6月頃に急に話題になった手法です。解説記事も多いので詳細な説明は省きますが、ざっくり説明すると、人がAI Agentにプロンプトを入力する代わりに、AIがプロンプトを作るループを人が設計する考え方で、Addy Osmani氏のブログで[Loop Engineering](https://addyosmani.com/blog/loop-engineering/)として体系化されています。

Claude Codeでは`/goal`を使いゴール達成までループを続ける機能がすでにありますが、証跡が残る形でLoop Engineeringの基本環境をアジャイル開発の管理でよく使われるJiraを使って作ってみました。

## なぜJiraを使うのか

Jiraは課題管理やプロジェクト管理ツールで特にスクラム開発でよく使われるサービスです。私もアジャイルのプロジェクト管理で使うことが多いです。  
今回Jiraを使うのは単に私が慣れているというのもありますが、Atlassian Rovoを使ってClaudeとMCPで連携ができ、小さなプロジェクトなら無料枠でもLoop Engineeringが証跡が残る形で実現可能です。

実際のところ、Loop Engineeringとアジャイルは無関係ですし、Jiraである必要はないと思います。私は試していませんが、他のサービスやツールに置き換え可能と思います。  
ですが、Loop Engineeringのループの停止条件と同じように受け入れ条件(Acceptance Criteria)や完了条件(Definition of Done)を管理するアジャイル系のツールは相性が良いように思います。

## ループ設計

ループの流れは以下の通りです。Agentが何を計画して、何を実装したのかを全てJiraとConfluenceに残す設計にしています。

1. 人が要件と受け入れ条件（ループ停止条件）を書いたEPICを用意する
2. EPICの状態を進行中にする。Jira Automation機能でClaude Codeを起動する
3. Claude CodeがEPICの内容を分解し、必要なSTORYのチケットを作りJiraに登録する。
4. STORYチケットをClaude Codeが実装する。
5. Sub Agentの検証Agent(Verifier)が簡易テストを行う。テストNGの時はJiraにBUGチケットを登録する。テスト報告書をConfluenceに登録。
6. 全てのチケットの実装が完了したら、検証Agent(Verifier)がループ停止条件（受け入れ条件）を満たしているか確認する。NGの場合はBUGチケットをJiraに登録。テスト報告書をConfluenceに登録。
7. 検証AgentがPASSと判定したら、Pull Requestを作成する

運用ルールとポイントは以下の通りです。

1. 人が作るのは**EPICだけ**。受け入れ基準は機械的に判定可能な形で書く
2. EPICの実現に必要なストーリーやバグのチケットは基本的に**エージェントが起票**する。人がバグを見つけた場合は、チケットを起票し、ループを起動するが動作中のループに割り込まない
3. 完了を宣言できるのは実装者ではなく\*\*検証Agent(Verifier)\*\*だけ。検証Agentは実装とは別のサブエージェント。
4. エージェント同士が**JIRA＝状態、Confluence＝検証記録、Git＝コード**という共有ストレージ越しに繋がる（ブラックボード型）

特に**重要なのが3です**。コードを書いたAgentは自分の宿題を甘く採点しがちです。もちろんテスト強化のためにルールを明確にし、ハーネスで縛るのも効果的ですが、停止条件が明確であるほど、条件を「満たす」最短経路（テストのskip、閾値の緩和）を選びがちになるように思います。そのため、Verifierには別コンテキスト・読み取り専用の権限・独立したE2E実行ができるように分離しています。

## 実際の動作

実際に動かすとこんな感じになります。

### ループ開始前にEPICを分解

![私ここまで要件書いたっけ？というぐらい分解されます](https://static.zenn.studio/user-upload/896b9cc3a35c-20260714.png)  
Claude CodeがEPICの内容を実装しやすいようにチケットに分解してEPICの子要素にし実装を始めます。

### ループ検証のレポート

![Verifierが直接Confluenceにレポートできていないのは見逃して](https://static.zenn.studio/user-upload/e7f6165a3a87-20260714.png)  
全てのチケットの実装が終われば、検証Agent(Verifier)がテストをしてPASS/NGの判定をしてくれます。  
実測が必要な項目もDEFERRED（先送り）にならずに検証してくれました。APIコールの多い処理で60秒以内の処理完了と30コール/60秒の非機能要件の条件を入れてますが以下の報告してくれていました。

```
実API実測 elapsed=10.71s < 60s。実測レート 19.2 req/min ≤ 実効上限30（=ライト60×0.5）。ユニバース: listed_info=4439件・statements=93件。summary.elapsed_seconds ログ記録あり
```

## 環境構築

実際の環境構築の手順です。

### 1. Jira / Confluenceにスペース作成

Jira / Confluenceにプロジェクトやスペースを準備します。私はSCRUMテンプレートでプロジェクトを作りましたが、別の形式でも大丈夫だと思います。

### 2. ClaudeにAtlassian Rovo接続

[Claude.ai](https://claude.ai/)のコネクターでAtlassian Rovoを有効にします。JiraやConfluenceにアクセス可能か確認しておきます。![Claude.aiに設定すると、Claude Codeでも使えるのはわかりにくいけど便利だよね](https://static.zenn.studio/user-upload/9eb62b358783-20260714.png)

### 3. Claude Code Routinesの設定

ループの起動は[Routines](https://claude.ai/code/routines)で監視しています。[Claude Code Routines](https://claude.ai/code/routines)でルーチンを新規作成します。

* Gitリポジトリの設定
* 利用するLLM Modelの設定
* 環境の設定。検証にネットワークを使う場合はドメインを許可。環境変数もここで設定する。
* トリガーは`API経由で呼び出す`
* コネクターは基本的に`Atlassian Rovo`のみ。最低限のみ有効にする。

設定例です。  
![設定例](https://static.zenn.studio/user-upload/57017b41243b-20260714.png)  
指示の例です。

```
 あなたは <project name> の実装エージェントです。この実行はRoutine(cron / fire API)による無人のクラウド実行です。あなたの行動規範はすべてリポジトリ内のルールに書かれており、このプロンプトは**セッションの立ち上げ方だけ**を定めます。このプロンプトとルールが矛盾する場合は、**リポジトリのルールを正**とします。
  ## 1. 行動規範の読み込み(最初に必ず)
  CLAUDE.md、.claude/rules/ の全ファイル、スキルを読む。以降の進め方・禁止事項・停止条件・エスカレーションはすべてそこに従う。
  ## 2. 対象EPICの特定
  実行コンテキスト(text)にEPICキーが含まれる場合はそれに従う。無ければ JQL `project = NS AND issuetype = エピック AND status = "進行中"` で特定する。対象が特定できない(0件・複数で判断不能)、またはJIRAに接続できない場合は、**何も変更せず**理由を報告して終了する。
  ## 3. 二重起動ガード
  対象EPIC配下の「進行中」チケットに直近30分以内の着手・進捗コメントがある場合は、別セッションが作業中とみなし、何も変更せず終了する。
  ## 4. 状態復元と実行
  ルールの再開プロトコルに従って状態を復元する。この環境はフレッシュなクローンなので、未マージPRの続きを行う場合は新規ブランチを作らず**そのPRのブランチをチェックアウト**して再開する。以降はルールの「ループの1周」を停止条件に達するまで繰り返し、停止時の記録・ラベル運用もルールに従う。
  ## 5. 無人実行の自覚
  このセッションに確認を求める相手はいない。判断に迷ったら推測で進めず、ルールのエスカレーション手順に従って保留・停止する。
```

設定後にFire URLとAPI KEYが分かるのでメモを取っておきます。

### 4. Jira Automationの設定

Jiraの`スペース設定`の`自動化`でEPICの状態変化をトリガーにClaude Code Routinesで設定したFire URLを呼ぶよう設定します。  
![Jiraのスペース一覧で・・・のメニューからスペース設定を開くと自動化の設定ができます](https://static.zenn.studio/user-upload/3701c3cd640f-20260714.png)  
Webリクエストには以下を設定します。

* HTTP メソッド: **POST**
* Webリクエスト本文: **カスタムデータ**
* カスタムデータ

```
{"text": "JIRA Automationからの起動: EPIC {{issue.key}}（{{issue.summary}}）が「進行中」に遷移しました。このEPICを対象にループを実行してください。"}
```

ヘッダーも設定が必要です

* Authorization: **Bearer <API-KEY文字列>**
* Content-Type: **application/json**
* anthropic-beta: **experimental-cc-routine-2026-04-01**
* anthropic-version: **2023-06-01**

### 5. Agent / rules / skill の整備

Loop Engineeringに必要なClaude.mdやagent定義、ルール、スキルを作成し、Gitにpushしておきます。私はLoop Engineering用に以下のルールを設定しました。

## 実際にループ設計をしてみてわかったこと

実際ループを書いてみると色々トラブルが発生しました。その中で印象に残ったものです。

### 検証していないのにPASS判定になる

* 環境変数の誤りで検証できない項目があったが、人による確認後に再度検証を行うことにして暫定でPASS判定をしていた。  
  → 未検証項目が残っているときはPASS判定できないと明記し、３回ループで解決しないときはDEFERRED（先送り）としてレポートするように変更

### ループが多重に起動する

* ループの起動トリガをEPICチケットを「進行中」に変更したときにしていたが、Claude Codeが気を利かせてループに合わせてEPICの状態を変更していた。「進行中」に変更してしまい、FireURLが呼ばれてしまった。  
  → EPICの状態は変更不可と明記（人だけが変更可能）

### ループに時間がかかる

* ループ起動のたびに検証を行うため、結構時間がかかってしまいます。今回はループ停止条件の判定はフルでテスト、それ以外は簡易テストで時間を節約しましたが、それでも時間がかかるので試行錯誤がしづらいです。  
  → Loop EngineeringはUXや機能が固まってから移行したほうが良い。

## 感想

検証がしっかりと動くのは魅力的です。ですが、検証は確かにOKだけど何か違う...みたいなことが多かったです。特にUXなどの作りこみが必要な場合は仕様駆動開発や、Vibe Codingで試行錯誤しながら作ったほうが効率的に思いました。  
非機能要件だったり、脆弱性対応など定期的な改善処理には変更後の検証が重要なので、こういったところでLoop Engineeringを活用していきたいです。

今回検証に利用したソースコードです。

## 参考リンク
