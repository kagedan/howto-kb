---
id: "2026-05-27-x自動投稿aiエージェントを作った-research-agent-claude-hitl承認-投稿の-01"
title: "X自動投稿AIエージェントを作った — Research Agent → Claude → HITL承認 → 投稿の全体設計"
url: "https://zenn.dev/shori1234/articles/05_content-agent-overview"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

## この記事について

毎日X（Twitter）に投稿し続けるのは地味にきつい。ネタを考えて、書いて、タイミングを見計らって投稿する。それを「エージェントが下書きを作って自分が承認するだけ」に変えた。

Research Agentが収集したAI情報を元にClaude Sonnet + Haikuが3つの投稿案を生成し、Slackに通知。承認・修正・スキップをワンクリックで操作できる。承認したものは自動でXに投稿され、完了をSlackに通知する。

この記事はシステム全体の概要だ。設計の全体像を先に把握してから、個別の実装記事を読んでもらうのが一番わかりやすい。

**こんな人に向けて書いている：**

* AWS Step Functionsでワークフローを組む設計に興味がある
* LLMエージェントにHuman-in-the-Loop（HITL）を実装したい
* 複数のLambdaを連携させる設計パターンを知りたい

---

## 全体の処理フロー

```
EventBridge Scheduler（毎朝7時JST）
  └─ Step Functions: Content Agent Workflow
        │
        ├─ [State: GenerateContent]
        │     └─ Lambda: content-agent-generate
        │           ├─ S3から昨日のResearch Agent収集データを読む
        │           ├─ S3から過去14日のテーマ使用履歴を読む（重複防止）
        │           ├─ Claude Sonnet: テーマ選定
        │           ├─ Claude Haiku: 投稿案3本生成
        │           ├─ S3に保存（drafts/{date}.json）
        │           └─ Notionにレコード作成
        │
        ├─ [State: WaitForApproval]（最大24時間待機）
        │     └─ Lambda: content-agent-notifier
        │           ├─ TaskTokenをDynamoDBに保存
        │           └─ Slackに承認ボタン付きメッセージ送信
        │
        ├─ [State: CheckApproval]（Choice）
        │     ├─ approved → PublishContent
        │     ├─ revise  → GenerateContent（フィードバック付きで再生成）
        │     └─ skip    → Skipped（正常終了）
        │
        ├─ [State: PublishContent]
        │     └─ Lambda: content-agent-publisher
        │           ├─ X API v2でツイート投稿（OAuth 1.0a署名）
        │           ├─ S3のstatusを更新（published）
        │           └─ Slack完了通知（ツイートURL付き）
        │
        └─ [State: Done]（正常終了）

承認コールバック（別フロー）:
Slackのボタンクリック → ブラウザでURL → API Gateway
  └─ Lambda: content-agent-approval-callback
        ├─ DynamoDBからTaskToken取得
        └─ Step Functions: send_task_success（ワークフロー再開）
```

---

## Lambda関数の役割分担

4つのLambda関数で構成されている。

| Lambda名 | 役割 |
| --- | --- |
| `content-agent-generate` | テーマ選定・投稿案生成・S3/Notion保存 |
| `content-agent-notifier` | Slack通知・DynamoDB TokenStore |
| `content-agent-approval-callback` | Slackボタン → Step Functions再開 |
| `content-agent-publisher` | X投稿・Slack完了通知 |

Step Functionsがこれらをオーケストレーションする。各Lambdaは単機能に絞ってある。

---

## Step Functionsのステートマシン

ワークフローをStep Functionsで管理している主な理由は2つだ。

1つ目は、`waitForTaskToken`で承認待ち状態を維持できること。Lambda単体では24時間後の再開はできない（タイムアウトは最大15分）。Step Functionsなら最大1年間の待機が可能で、承認されるまでワークフローが「止まって待つ」状態を維持できる。

2つ目は、再生成ループが自然に書けること。「フィードバックを元に再生成 → 再度承認を待つ」というループは、Step Functionsのステートマシンとして表現すると見通しが良い。

```
"CheckApproval": {
  "Type": "Choice",
  "Choices": [
    {"Variable": "$.approval.action", "StringEquals": "approved", "Next": "PublishContent"},
    {"Variable": "$.approval.action", "StringEquals": "revise",   "Next": "PrepareRevision"},
    {"Variable": "$.approval.action", "StringEquals": "skip",     "Next": "Skipped"}
  ],
  "Default": "ApprovalRejected"
}
```

`PrepareRevision`でフィードバックを整形して`GenerateContent`に戻ることで、再生成ループが成立する。

---

## HITLのメカニズム

Human-in-the-Loopの実装はTaskTokenパターンを使っている。

```
Step Functions が WaitForApproval に入る
  └─ TaskToken を Lambda に渡す（$$.Task.Token）
        ├─ DynamoDBにTaskTokenを保存（approval_idと紐付け）
        └─ SlackにURLボタンを送信（approval_idをURLに含める）

ユーザーがSlackのボタンをクリック
  └─ ブラウザでコールバックURLにアクセス
        └─ Lambda: approval-callback
              ├─ approval_idでDynamoDBからTaskTokenを取得
              └─ sfn.send_task_success(taskToken=token, output=json)

Step Functionsが再開 → CheckApprovalへ
```

Step FunctionsがTaskTokenを発行し、それをDynamoDBに保存しておく。ユーザーがブラウザでURLを開くとコールバックLambdaが動き、DynamoDBからTokenを取得してStep Functionsに渡すことでワークフローが再開する。

---

## 投稿タイプの設計

毎日同じ種類の投稿にならないよう、タイプ選択のルールを設けた。

月曜と金曜は固定（週次目標・週次報告）。それ以外の曜日は10種類のプールから「最も長く使われていない」ものを選ぶ。「質問企画」は5投稿以上の間隔が必要というルールもある。

```
FIXED_TYPES = {0: "週次目標", 4: "週次報告"}
TYPE_POOL   = ["実装Tips", "失敗談", "比較", "ツール紹介", "コスト公開",
               "ハマりどころ", "仕組み解説", "知らないと損する", "引用と考察", "質問企画"]
QA_MIN_INTERVAL = 5

def select_post_type(weekday: int, past_themes: list[str]) -> str:
    if weekday in FIXED_TYPES:
        return FIXED_TYPES[weekday]
    
    used_types = [re.search(r'（(.+?)）', e).group(1) for e in past_themes 
                  if re.search(r'（(.+?)）', e)]
    candidates = [t for t in TYPE_POOL if t not in FIXED_TYPES.values()]
    
    if "質問企画" in used_types[:QA_MIN_INTERVAL]:
        candidates = [t for t in candidates if t != "質問企画"]
    
    # 最後に使われた日が遠いものを優先
    def last_used_pos(t):
        try: return used_types.index(t)
        except ValueError: return 999
    
    candidates.sort(key=last_used_pos, reverse=True)
    return candidates[0] if candidates else "実装Tips"
```

---

## コスト構成

このエージェントが1日あたりに使うAPIコール数の概算：

| 処理 | モデル | tokens（概算） |
| --- | --- | --- |
| テーマ選定 | Claude Sonnet | ~1,000 input / ~200 output |
| 投稿案生成 ×3 | Claude Haiku | ~800 input / ~400 output ×3 |
| 再生成（必要な場合） | Claude Haiku | 同上 |

月間コストはSonnet/Haikuの料金テーブル次第だが、1日1回の実行なら数十円〜数百円のオーダー。S3・DynamoDB・Step Functionsも利用するが、この規模では無料枠内に収まる。

---

## まとめ

Content AgentはResearch Agent・Notion・Slack・X・Step Functions・DynamoDBと複数のサービスを連携させる、このプロジェクトで一番複雑なエージェントになった。

個別の実装詳細は次の3つの記事で書いている：

* **HITLパターン（TaskToken + DynamoDB）** → `05-1_content-agent-hitl.md`
* **OAuthバグとの格闘（Twitter API v2）** → `05-2_content-agent-oauth.md`
* **投稿品質の改善（タイプ多様化・トーン・重複防止）** → `05-3_content-agent-quality.md`

**参考リンク：**
