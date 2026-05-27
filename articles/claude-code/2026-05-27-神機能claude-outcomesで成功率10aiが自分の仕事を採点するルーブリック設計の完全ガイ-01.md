---
id: "2026-05-27-神機能claude-outcomesで成功率10aiが自分の仕事を採点するルーブリック設計の完全ガイ-01"
title: "【神機能】Claude Outcomesで成功率+10%！「AIが自分の仕事を採点する」ルーブリック設計の完全ガイド"
url: "https://qiita.com/emi_ndk/items/9ab097906780047f845c"
source: "qiita"
category: "claude-code"
tags: ["API", "AI-agent", "Python", "JavaScript", "qiita"]
date_published: "2026-05-27"
date_collected: "2026-05-27"
summary_by: "auto-rss"
query: ""
---

**「AIの出力が微妙...でも何度も手直しさせるの面倒...」**

この悩み、持っていませんか？

2026年5月6日、AnthropicがCode with Claudeカンファレンスで発表した**Outcomes機能**が、この問題を根本から解決します。

## 結論から言うと

Claude Outcomesは「**別のAIがあなたの代わりに出力を採点し、ダメなら自動で修正させる**」機能です。

社内ベンチマークで：
- **タスク成功率+10ポイント**
- **Word文書品質+8.4%**
- **PowerPoint品質+10.1%**

という衝撃的な結果が出ています。

## なぜ「セルフレビュー」は失敗するのか

「出力をチェックして」とClaude自身に頼んだことありますよね？

**これ、ほぼ意味ないです。**

理由は単純。**自分の推論過程を見ながら採点するから、甘くなる**んです。

```
❌ 従来のセルフレビュー
┌─────────────────────────────────────┐
│ Writer Claude                        │
│ ├─ タスク実行                        │
│ ├─ 自分の推論を記憶している          │
│ └─ 「まあ、いいんじゃない？」        │ ← 甘い
└─────────────────────────────────────┘

✅ Outcomes方式
┌─────────────────────────────────────┐
│ Writer Claude                        │
│ └─ タスク実行 → 成果物出力           │
└─────────────────────────────────────┘
          ↓ 成果物のみ渡す
┌─────────────────────────────────────┐
│ Grader Claude（別インスタンス）       │
│ ├─ ルーブリックのみ参照              │
│ ├─ Writerの推論は見えない            │
│ └─ 「ここがダメ。直して」            │ ← 厳しい
└─────────────────────────────────────┘
```

**Graderは別のコンテキストウィンドウで動く**ので、Writerがどう考えてその結論に至ったかを知りません。

これが「お手盛り採点」を防ぐ仕組みです。

## 実装方法：5ステップで始める

### Step 1: 環境セットアップ

```python
import anthropic
from dotenv import load_dotenv

BETAS = ["managed-agents-2026-04-01"]
MODEL = "claude-sonnet-4-6"
client = anthropic.Anthropic()

# 環境作成
env = client.beta.environments.create(
    name="research-brief",
    config={
        "type": "anthropic_cloud",
        "networking": {"type": "unrestricted"}
    },
)
```

### Step 2: Writerエージェント作成

```python
writer = client.beta.agents.create(
    name="Research Analyst",
    model=MODEL,
    system="""あなたはリサーチアナリストです。

    事実の主張には必ず脚注[n]を付けてください。
    文末にSourcesセクションを設けてください：
    [n] "引用元の原文、25語以内" - タイトル - URL

    成果物は /mnt/session/outputs/brief.md に保存してください。""",
    tools=[
        {
            "type": "agent_toolset_20260401",
            "configs": [
                {"name": "web_search"},
                {"name": "web_fetch"},
                {"name": "read"},
                {"name": "write"},
            ],
        }
    ],
    betas=BETAS,
)
```

### Step 3: セッション作成

```python
session = client.beta.sessions.create(
    agent={"type": "agent", "id": writer.id, "version": writer.version},
    environment_id=env.id,
    title="EV急速充電の経済性分析",
    betas=BETAS,
)
```

### Step 4: タスクとルーブリックを定義

```python
TASK = """
EV急速充電の経済性についてブリーフを作成してください。
以下を含めること：
  1. 設備投資額の範囲
  2. デマンドチャージの影響
  3. 損益分岐点の稼働率
  4. 補助金プログラム
  5. 主要事業者の財務状況
  6. 批判的な見解
  7. ハードウェアvs設置コストの内訳
"""

RUBRIC = """
/mnt/session/outputs/brief.md のブリーフをチェックリストに照らして評価してください。

【カバレッジチェック】各項目を確認：
  1. 設備投資: DC急速充電スタンドあたりのドル建てコスト範囲
  2. デマンドチャージ: 運営コストへの影響（$/kWまたは運営費の%）
  3. 損益分岐稼働率: 閾値（%またはkWh/日）
  4. 補助金: NEVIなど公的プログラム名を明記
  5. 事業者財務: SEC提出書類（10-K/10-Q）からの純損益
  6. 批判的見解: 経済性に否定的な情報源
  7. コスト内訳: ハードウェアvsソフトコスト（設置・許可・系統接続）の比率

【引用チェック】Sourcesセクションの各[n]について：
  a. URLをweb_fetchで取得。ページが読めればLIVE、404/ログイン壁等はDEAD
  b. 引用文字列がページ内に存在するか確認
  c. 引用が主張を裏付けているか確認

【出力フォーマット】
1行目: Coverage N/7. Citations M/K verified.

失敗項目ごとに：
- Item [N] [Topic] - [理由]. [不足点]

失敗引用ごとに：
- [n] domain - 理由. [修正方法]
"""

# Outcome定義を送信
client.beta.sessions.events.send(
    session.id,
    betas=BETAS,
    events=[
        {
            "type": "user.define_outcome",
            "description": TASK,       # Writerが読む
            "rubric": {"type": "text", "content": RUBRIC},  # Graderが読む
            "max_iterations": 5,
        },
    ],
)
```

### Step 5: イベントストリーミング

```python
TERMINAL = {"satisfied", "max_iterations_reached", "failed", "interrupted"}

with client.beta.sessions.events.stream(session.id, betas=BETAS) as stream:
    for ev in stream:
        if ev.type == "span.outcome_evaluation_start":
            print("📝 Writer完了。Grader評価中...")

        elif ev.type == "span.outcome_evaluation_end":
            result = ev.result
            feedback = ev.explanation
            print(f"結果: {result}")
            print(f"フィードバック:\n{feedback}")

            if result in TERMINAL:
                break
```

## 【最重要】ルーブリック設計の6原則

Outcomesの威力は**ルーブリックの質で決まります**。

### 原則1: 各基準を「チェック可能」にする

```
❌ ダメな例
「デマンドチャージについて書かれているか確認」

✅ 良い例
「デマンドチャージ: 運営コストへの定量的影響（$/kWまたは運営費の%）が記載されている」
```

### 原則2: 具体的な証拠を要求する

```python
# ダメ：曖昧
"信頼できる情報源から引用すること"

# 良い：具体的
"SEC提出書類（sec.gov）からの引用が必須。プレスリリースやニュース記事は不可。10-Kと8-K EX-99.1を明確に区別すること"
```

:::note info
**実例**: Graderが「EVgo FY2024の純損失」の引用を却下
- Writer: `sec.gov/Archives/edgar/.../R4.htm`（8-K Exhibit 99.1）を引用
- Grader: 「これは8-K添付のプレスリリース。10-Kまたは10-Qを引用してください」
- Writer: EDGARで10-Kを発見 → Pass 3で合格

**この区別がルーブリックに明記されていたから機能した！**
:::

### 原則3: 「手順」ではなく「目標」を書く

```
❌ ダメな例
「web_fetchでURLを実行してください」

✅ 良い例
「URLを取得してください。web_fetchが読めるページを直接返した場合のみLIVE。
404、パーク済み、ログイン壁、ペイウォール、bot-block/403、
JavaScript専用レンダリングの場合はDEAD」
```

### 原則4: ショートカットを予測して防ぐ

```python
RUBRIC += """
ミラーサイト、転載、検索スニペットでの検証は禁止。
引用URLそのものがfetch可能でなければならない。
"""
```

### 原則5: フィードバック形式を指定する

```python
RUBRIC += """
【出力フォーマット】
1行目: Coverage N/7. Citations M/K verified.

失敗項目ごとに新しい箇条書き：
- Item [N] [Topic] - [理由]. [不足点]

失敗引用ごとに新しい箇条書き：
- [n] domain - 理由. [修正方法]
"""
```

### 原則6: 範囲外を明示する

```python
RUBRIC += """
【採点対象外】
- 文体の好み
- 既存のフォーマット問題
- スコープ外の追加情報
"""
```

## ユースケース：Outcomesが輝く場面

| シナリオ | なぜOutcomesが有効か |
|---------|---------------------|
| **リサーチレポート** | 引用検証、網羅性チェック |
| **法務文書** | 条項の抜け漏れ防止 |
| **APIドキュメント** | エンドポイント網羅、サンプルコード検証 |
| **プレゼン資料** | ブランドガイドライン準拠、データ正確性 |
| **コードレビュー** | テストカバレッジ、セキュリティチェック |

:::note warn
**Outcomesが向かないケース**
- 主観的なトーン・スタイルの判断
- 人間の最終判断が必要な場面
- 単発の検証タスク
:::

## イテレーション回数のチューニング

```python
# 推奨設定
"max_iterations": 3  # デフォルト。ほとんどのタスクに適切

# 複雑なリサーチタスク
"max_iterations": 5  # 引用検証が多い場合

# シンプルな品質チェック
"max_iterations": 2  # 修正が軽微な場合
```

**チューニングの目安：**
- 同じ問題で上限に達する → ルーブリックを明確化
- 不要な修正が続く → 基準をより具体的に

## Webhooksとの連携

Outcomesは**Webhooks**と組み合わせると真価を発揮します。

```python
# Console設定
# Event types: session.status_idled, span.outcome_evaluation_end

# Webhook受信サーバー
@app.post("/webhook")
async def handle_webhook(payload: dict):
    if payload["type"] == "span.outcome_evaluation_end":
        if payload["result"] == "satisfied":
            # Slack通知
            notify_slack(f"✅ タスク完了: {payload['session_id']}")
        elif payload["result"] == "max_iterations_reached":
            # 人間のレビューをトリガー
            create_review_task(payload)
```

## まとめ

**Claude Outcomesの核心：**

1. **分離されたコンテキスト** → お手盛り採点を防止
2. **ルーブリック駆動** → 曖昧さを排除
3. **自動修正ループ** → 人間の介入を最小化
4. **最大+10%の成功率向上** → 実証済み

**今日から試せる3ステップ：**

1. `managed-agents-2026-04-01` ベータに参加
2. 既存タスクをルーブリック形式に書き換え
3. `max_iterations: 3`で実験開始

---

**この記事が役に立ったら「いいね」お願いします！**

Outcomesを試してみた感想、うまくいったルーブリック設計のコツがあればコメントで教えてください 👇

## 参考リンク

Outcomes: agents that verify their own work | Claude Cookbook

https://platform.claude.com/cookbook/managed-agents-cma-verify-with-outcome-grader

New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration | Claude

https://claude.com/blog/new-in-claude-managed-agents

Code w/ Claude SF 2026: Building on the AI exponential | Claude

https://claude.com/blog/code-w-claude-sf-2026-sf
