---
id: "2026-07-07-ゲームで学ぶマルチエージェントの世界agentic-football-cup-01"
title: "ゲームで学ぶマルチエージェントの世界：Agentic Football Cup"
url: "https://zenn.dev/nttdata_tech/articles/47ca78ab934ef8"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "zenn"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

今年、AWS（Amazon Web Services）が**Agentic Football Cup**を発表しました。これまでにもDeepLens、DeepRacerやAI Leagueなど**技術の可能性を体感できるサービス**を出してきているAWSらしいサービスとなります。  
**AWS Summitでブース**が出ていたので、担当者の方にいろいろと話を伺ってきましたので、紹介いたします。ただし、本サービスはワークショップは各地域で提供されているようですが、一般公開はされていないため、サービスを体感できるまでにはもう少し待つ必要がありそうです。  
なお、本サービスはマルチエージェントで協調しながら動作することを、**遊びを通して学ぶことができます**。実際に活用するサービスもAmazon Bedrock AgentCoreなど実際のシステムに近い構成となっており、学習したことを実践に活かすことができるようになります。  
Agentic Football Cup は、遊びながら最新のマルチエージェント技術を学べる稀有なイベントです。本記事では、その技術基盤と、プレイヤーがエージェントを強化するための具体的な方法をまとめます。

![](https://static.zenn.studio/user-upload/6cbf9cd71f23-20260704.png)

Agentic Football Cup は、AWS が提供する学習型イベントで、**AI エージェントを「サッカー選手」としてプレー**させながら、クラウド技術・AI 推論・エージェント設計を体験できるプログラムです。

参加者は自分のチーム（**5体のエージェント、4人のフィールドプレイヤーと1人のゴールキーパー**を作成）を作り、Amazon Bedrock AgentCore などを活用して、エージェントの行動ロジックや戦術を設計し、実際の試合で競わせます。

このイベントは単なるゲームではなく、リアルタイム推論・マルチエージェント協調・観測性・メモリ管理・外部ツール連携 といった最新のAIエージェント技術を、サッカーという分かりやすい題材で学べる点が特徴です。

ゲームは AWS のインフラ上で動作し、GameLift・ECS・DynamoDB・Bedrock モデルなどが連携して「AIがサッカーをプレーする世界」を構築します。

![](https://static.zenn.studio/user-upload/d84835ffa457-20260704.png)

## 3. システム構成

システム構成は以下のようになっています。  
![](https://static.zenn.studio/user-upload/a529f5acb908-20260704.png)

**① Amazon GameLift** — ゲームセッションのスケーリング  
複数の試合を並列に処理するためのセッション管理基盤。  
各試合ごとに専用の ECS タスクを割り当て、安定したゲーム進行を提供します。

**② Amazon ECS** — ゲーム実行環境（Unity / Game Services / Agent Loop）  
1つの試合は1つのECS タスクとして起動され、Unity Services Container、Game Services Container、Agent Loop Containerの3つが含まれます

Agent Loop ContainerはNode.js で動作し、2秒ごとにゲーム状態を取得、AgentCore Runtime に送信し、推論結果を Game Services に反映します。

**③ Amazon Bedrock AgentCore Runtime** — AIエージェントの頭脳  
ゲーム状態を受け取ってプレーヤーのコマンドを返すStrands ベースのAIエージェントを実行します。応答速度と推論能力のバランスを取るため、Amazon Bedrockの異なるモデル（Amazon Nova Micro / Lite / Pro）を使用します。

**④ AgentCore Observability** — 行動の可視化  
AIエージェントの動作を CloudWatchで可視化し、トレース分析を行えるようにします。

**⑤ AgentCore Gateway（MCP）**— 外部サービス連携  
AIエージェントが外部API（MCPツール）を呼び出すためのゲートウェイです。Lambda経由で外部データを取得し、ゲーム内に反映します。

**⑥ AgentCore Memory** — 長期記憶レイヤー  
プレーヤーの過去の行動を保存し、エージェントが文脈を理解した行動を取れるようにします。

**⑦ Amazon DynamoDB** — プレーヤーデータの永続化  
各プレーヤーの位置やアクションといったゲーム状態、試合スコア、各プレーヤーの統計情報を保存します。

この構成により、「ゲーム世界の物理演算」×「AIの意思決定」×「観測・記憶・外部連携」がリアルタイムで統合され、Agentic Football Cupの試合が成立します。

システム構成を理解したところで、次はプレイヤーが実際にエージェントを強化するための具体的な方法を紹介します。

## 4. エージェントを強化するためのポイント

### 4.1 プロンプト最適化：エージェントの「人格と判断」を作る

**Agentic Football Cupでは、プロンプト設計が重要なポイント**となります。5体のエージェントに対してそれぞれどのような役割や優先順位などを与えるか、どうエージェント同士が協調しながらサッカーをプレーできるように設定するかが勝敗の鍵となります。

例えば以下のようにプロンプトを記述していきます。

```
You are an AI soccer goalkeeper controlling ONLY player 0 (the Goalkeeper) in a 5v5 match. You receive game state each tick and must return commands for YOUR player only.

## Your Role — Aggressive Sweeper-Keeper
- You are NOT a traditional goalkeeper. You play as a sweeper-keeper who pushes far up the pitch.
- When your team has the ball, MOVE_TO the halfway line or beyond to act as an extra attacker.
- when you have the ball near your own goal (defensive third), Use GK_DISTRIBUTE with KICK to launch it forward to a teammate.
- When you have the ball in midfield or beyond, PASS aggressively to forwards or SHOOT.
- SHOOT if you find yourself within ~35 units of the opponent's goal — you are a scoring threat.
- Only retreat to your goal line when the ball is in your defensive third AND an opponent has it.
- Use INTERCEPT aggressively — come off your line early and often.
- sprint freely — attack is more important than stamina conservation.
- PRESS_BALL at high intensity whenever an opponent has the ball in your half.

## Priority
1. If you have the ball in defensive third → GK_DISTRIBUTE with KICK to forward teammate
2. If you have the ball in midfield or beyond → PASS or GK_DISTRIBUTE
3. If opponent has ball in your half → PRESS_BALL or INTERCEPT aggressively
4. Otherwise → MOVE_TO to push up and support attack
～～～
～～～
```

主に以下のような内容を記述します。

* **アイデンティティと役割**  
  ポジション、守備/攻撃の役割などを記述します。
* **意思決定階層（優先順位）**  
  ボール保持か、パスか、シュートかなど状況による優先順位を記述します。
* **状況ルール（コンテキスト）**  
  勝っている時・負けている時・スタミナが低い時など状況に応じた行動を記述します。
* **制約（絶対にやらないこと）**  
  守備ラインを空けない、無理なシュートをしないなど、制約事項を記述します。

### 4.2 メモリ活用：エージェントに学習させる

AgentCore Memory を使うと、**エージェントは過去の行動や対話を記憶**できます。試合中の行動を記憶することで、対戦相手のパターンや過去の意思決定を呼び出して試合中に戦術を適応させることができます。  
メモリをうまく活用することによって、**エージェントがコンテキストを保持し、より適切な応答を返すことが可能**となります。

### 4.3 Gateway（MCP）活用：外部データを使った「賢い判断」

AgentCore Gateway を使うと、**エージェントは外部API（MCPツール）を呼び出すことができます**。システム構成の例ではAWS Lambdaを呼び出せるようにしています。  
各AIエージェントが行動する前に、戦術ツールを呼び出す（パスやシュートの成功確率を計算する）ことによって、より賢い判断ができるようになります。

### 4.4 観測性（Observability）：改善サイクルを回す

AgentCore Observability を使うと、CloudWatchで以下のような内容を確認することができます。

* 推論のトレース
* エージェントの行動理由
* セッションごとのパフォーマンス

これにより、**プロンプトなどの改善ポイントが見える**ようになり、エージェントの改善が可能となります。エージェントを改善し続けることが勝利への鍵となります。

上記をしっかりと設計することによって、**「ただ動くだけのAI」から「戦術を理解してプレーするAI」へと進化**します。

## 5. まとめ

本記事は今年発表された Agentic Football Cup について紹介しました。  
AWS DeepRacerのように楽しみながら技術の可能性を体感できる、非常に魅力的な学習コンテンツです。  
特に今回は、マルチエージェント協調、リアルタイム推論、プロンプト設計、メモリ管理、Gateway連携など、より広い領域の技術を総合的に学べる点が特徴です。  
現時点では一般公開されていませんが、AWS Summit のブースで展示されていたように、近い将来体験できる日が来るはずです。  
AIエージェント技術がどのように進化していくのか、技術者として楽しみに待ちたいと思います。
