---
id: "2026-04-25-ai-エージェントにこの順番で呼んでが通じない-strands-steering-でツール順序を決定-01"
title: "AI エージェントに「この順番で呼んで」が通じない!! — Strands Steering でツール順序を決定論的に保証する"
url: "https://zenn.dev/aws_japan/articles/584e4f5743eb37"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

## この記事をざっくり言うと

* AI エージェントにプロンプトで「この順番でツールを呼んで」と書いても、LLM は確率的にトークンを生成する仕組みなので、従わない可能性を原理的に排除できない
* Strands Agents SDK の **Steering Hook** を使うと、ツール呼び出しの前に Python のチェックコードが割り込み、前提条件を満たさない呼び出しをキャンセルしてモデルに矯正を促せる
* プロンプトを一切変えず、`plugins=[WorkflowOrderHandler()]` を追加するだけで、ワークフローの順序遵守を決定論的に保証できる

## 背景: プロンプトの限界

AI エージェントを作るとき、最初はツール（API や関数）を用意して、シンプルなプロンプトで動かすところから始めます。エージェントはプロンプトの指示に従って、どのツールをどの順番で呼ぶかを自分で判断します。

```
あなたは経費申請の承認を代行するアシスタントです。
以下の順序を必ず守ってください:
1. まず経費の詳細を確認する
2. 次に従業員情報を確認する
3. その後承認する
4. 最後に通知を送る
```

最近の賢いモデルならこれで十分動くことが多いです。でも問題は:

* **LLM は確率的にトークンを生成する**ので、どんなに大きなモデルでも指示に従わない可能性を原理的に排除できない
* **本番で何百回も実行すると**、テスト時には想定しなかったレアな入力パターンで予期しない動作が出る
* プロンプトに「絶対にスキップしないで」と書いても、それは**お願い**でしかない

## それをコントロールするには: Steering Hook

Strands Agents SDK には **Steering** という仕組みがあります。考え方はシンプルで、エージェントの行動を 2 つのタイミングで監視し、ルール違反があればその操作をキャンセルして「こうすべき」という理由をモデルにフィードバックするというものです。処理が止まるわけではなく、モデルはフィードバックを受けて正しい手順をやり直します。

### タイミング 1: ツールを呼ぶ直前

エージェントが何かのツールを呼ぼうとした瞬間に、SDK が自動的にチェック処理を挟みます。開発者はそのチェックロジックを Python で書くだけです。条件を満たしていれば `Proceed`（そのまま続行）を、満たしていなければ `Guide`（実行キャンセル＋理由）を返します。これは全てチェックコード側の判定です。

```
エージェント（LLM）:「approve_expense を呼ぼう」
    ↓
チェックコード（Python）: 「get_employee_info をまだ呼んでないよね？」
    ↓
Guide → ツール実行キャンセル、理由をフィードバック
    ↓
エージェント（LLM）:「じゃあ先に get_employee_info を呼ぼう」
```

### タイミング 2: ユーザーに応答を返す直前

モデルが最終応答を生成した後、返す前にチェックします。やるべきことが残っていれば応答を破棄してやり直させます。

```
エージェント（LLM）:「完了しました！」
    ↓
チェックコード（Python）: 「まだやるべきステップが残ってるよね？」
    ↓
Guide → エージェントの応答を破棄、理由をフィードバック
    ↓
エージェント（LLM）:「残りのステップを実行してから改めて応答しよう」
```

ポイントは `Guide` を返すと**ツール実行自体がキャンセルされる**こと。モデルが「無視しよう」と思っても実行されません。これがプロンプト指示との決定的な違いです。

## 検証シナリオ: 経費承認エージェント

経費申請の承認を代行するシンプルなエージェントで、「ツール呼び出し順序の遵守」だけを検証します。

### ツール構成

| ツール | 役割 |
| --- | --- |
| `get_expense_details` | 経費申請の詳細を取得 |
| `get_employee_info` | 従業員情報を取得 |
| `approve_expense` | 経費を承認 |
| `send_notification` | 承認結果を通知 |

### 守るべき順序

```
get_expense_details ─┐
                     ├→ approve_expense → send_notification
get_employee_info  ─┘
```

つまり「承認する前に経費の詳細と従業員情報を両方確認しろ」「承認したら従業員に通知を送れ」というルールです。経費詳細と従業員情報はどちらを先に呼んでも構いません。

### 比較する 2 パターン

同じプロンプト `"あなたは経費申請の承認を代行するアシスタントです。"` で、Steering の有無だけを変えて比較します。

1. **Steering なし**: プロンプトだけ。順序のルールはどこにも書かない
2. **Steering あり**: 同じプロンプト＋ Steering ハンドラを追加

## 実装

```
import json
from strands import tool

# モックデータ
EMPLOYEES = {
    "EMP001": {"name": "田中太郎", "department": "営業部", "employee_id": "EMP001"},
}

EXPENSES = {
    "EXP-101": {
        "expense_id": "EXP-101",
        "employee_id": "EMP001",
        "amount": 45000,
        "category": "交通費",
        "description": "大阪出張の新幹線代",
        "status": "pending",
    },
}

@tool
def get_employee_info(employee_id: str) -> str:
    """従業員情報を取得する。

    Args:
        employee_id: 従業員ID（例: EMP001）
    """
    emp = EMPLOYEES.get(employee_id)
    if emp:
        return json.dumps(emp, ensure_ascii=False)
    return json.dumps({"error": f"従業員 {employee_id} が見つかりません"}, ensure_ascii=False)

@tool
def get_expense_details(expense_id: str) -> str:
    """経費申請の詳細を取得する。

    Args:
        expense_id: 経費申請ID（例: EXP-101）
    """
    exp = EXPENSES.get(expense_id)
    if exp:
        return json.dumps(exp, ensure_ascii=False)
    return json.dumps({"error": f"経費申請 {expense_id} が見つかりません"}, ensure_ascii=False)

@tool
def approve_expense(expense_id: str, employee_id: str, approved_amount: int) -> str:
    """経費申請を承認する。

    Args:
        expense_id: 経費申請ID
        employee_id: 承認対象の従業員ID
        approved_amount: 承認金額（円）
    """
    return json.dumps({
        "status": "approved",
        "expense_id": expense_id,
        "employee_id": employee_id,
        "approved_amount": approved_amount,
        "message": f"経費申請 {expense_id} を {approved_amount}円で承認しました",
    }, ensure_ascii=False)

@tool
def send_notification(employee_id: str, message: str) -> str:
    """従業員に通知を送信する。

    Args:
        employee_id: 通知先の従業員ID
        message: 通知メッセージ
    """
    return json.dumps({
        "status": "sent",
        "to": employee_id,
        "message": message,
    }, ensure_ascii=False)
```

普通の Python 関数に `@tool` デコレータをつけるだけ。docstring がモデルへのツール説明になります。

### Steering ハンドラ（handlers.py）— 本記事のコア部分

```
from strands.vended_plugins.steering import SteeringHandler, LedgerProvider
from strands.vended_plugins.steering.core.action import Proceed, Guide

class WorkflowOrderHandler(SteeringHandler):
    """ツール呼び出し順序を強制するハンドラ。"""

    def __init__(self):
        # LedgerProvider: 全ツール呼び出し履歴を自動記録する組み込みプロバイダ
        super().__init__(context_providers=[LedgerProvider()])

    async def steer_before_tool(self, *, agent, tool_use, **kwargs):
        """approve_expense が呼ばれる前に前提条件をチェック。"""

        # approve_expense 以外はそのまま通す
        if tool_use.get("name") != "approve_expense":
            return Proceed(reason="承認以外はスルー")

        # SDK が自動記録している「これまでに呼んだツールの履歴」を取得
        ctx = self.steering_context.data.get()
        tool_calls = ctx.get("ledger", {}).get("tool_calls", [])

        # 経費詳細を確認済みか？
        # tool_calls の各要素（call）は {"tool_name": "...", "status": "success/error", ...} という辞書
        if not any(
            call["tool_name"] == "get_expense_details" and call["status"] == "success"
            for call in tool_calls
        ):
            return Guide(reason="先に get_expense_details で経費の詳細を確認してください。")

        # 従業員情報を確認済みか？
        if not any(
            call["tool_name"] == "get_employee_info" and call["status"] == "success"
            for call in tool_calls
        ):
            return Guide(reason="先に get_employee_info で従業員情報を確認してください。")

        return Proceed(reason="順序OK")

    async def steer_after_model(self, *, agent, message, stop_reason, **kwargs):
        """最終応答時に、承認後の通知漏れをチェック。"""

        if stop_reason != "end_turn":
            return Proceed(reason="最終応答ではない")

        ctx = self.steering_context.data.get()
        tool_calls = ctx.get("ledger", {}).get("tool_calls", [])

        approved = any(
            call["tool_name"] == "approve_expense" and call["status"] == "success"
            for call in tool_calls
        )
        notified = any(
            call["tool_name"] == "send_notification" and call["status"] == "success"
            for call in tool_calls
        )

        if approved and not notified:
            return Guide(reason="承認済みですが通知がまだです。send_notification を呼んでください。")

        return Proceed(reason="OK")
```

ここが Steering の全てです。ポイントを整理すると:

* **`LedgerProvider`**: 組み込みのコンテキストプロバイダ。エージェントの全ツール呼び出し履歴（入力、出力、成功/失敗）を自動記録する
* **`steer_before_tool`**: ツール実行前にインターセプト。`Guide` を返すとツール実行がキャンセルされ、理由がモデルにフィードバックされる
* **`steer_after_model`**: モデルの最終応答前にインターセプト。`Guide` を返すと応答が破棄され、モデルがリトライする
* **決定論的**: チェックロジックは LLM を使わない普通の Python の if 文。毎回同じ入力に同じ結果を返す  
  ※ `steer_before_tool` と `steer_after_model` は SDK が定めた固定のメソッド名です。

### エージェント定義（agents.py）

```
from strands import Agent
from strands.models import BedrockModel
from tools import get_employee_info, get_expense_details, approve_expense, send_notification
from handlers import WorkflowOrderHandler

ALL_TOOLS = [get_employee_info, get_expense_details, approve_expense, send_notification]

# Amazon Nova Micro で検証
MODEL = BedrockModel(
    model_id="us.amazon.nova-micro-v1:0",
    region_name="us-east-1",
    max_tokens=2048,
)

SYSTEM_PROMPT = "あなたは経費申請の承認を代行するアシスタントです。"

# Steering なし: プロンプトだけ
def create_base_agent() -> Agent:
    return Agent(
        model=MODEL,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

# Steering あり: 同じプロンプト + ハンドラを追加するだけ
def create_steering_agent() -> Agent:
    return Agent(
        model=MODEL,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        plugins=[WorkflowOrderHandler()],  # ← これだけ追加
    )
```

プロンプトは全く同じ。違いは `plugins=[WorkflowOrderHandler()]` があるかないかだけです。

## 実行結果

Amazon Nova Micro で、同じプロンプトのまま Steering の有無だけ変えて各 3 回実行した結果です。

### Steering なし: 1/3 (33%)

```
--- Steeringなし ---
  Run 1: ✅ 順序OK
  Run 2: ❌ get_employee_info が呼ばれなかった
         呼ばれた順序: get_expense_details → approve_expense → send_notification
  Run 3: ❌ get_employee_info が呼ばれなかった
         呼ばれた順序: get_expense_details → approve_expense → send_notification
```

`get_employee_info` をスキップして直接 `approve_expense` を呼ぶパターンが 2/3 で発生。モデルは「経費の詳細に従業員 ID が含まれてるから、わざわざ従業員情報を取得しなくてもいいだろう」と判断したのかもしれません。合理的ではあるけど、ワークフロー的には NG。

### Steering あり: 3/3 (100%)

```
--- Steeringあり ---
  Run 1: ✅ 順序OK
  Run 2: ✅ 順序OK
  Run 3: ✅ 順序OK（Guide で矯正あり）
```

3 回とも成功。特に Run 3 のログが面白いので詳しく見てみましょう。

## Steering ありの矯正されたログを読む

Run 3 の実際のツール呼び出し順序:

```
Tool #1: get_expense_details     ← 経費詳細を取得（OK）
Tool #2: approve_expense         ← 承認しようとした → Guide でキャンセル！
Tool #3: get_employee_info       ← フィードバックに従って従業員情報を取得
Tool #4: approve_expense         ← 再度承認 → 今度は Proceed で続行
Tool #5: send_notification       ← 通知送信
```

モデルは `get_employee_info` をスキップして `approve_expense` を呼ぼうとしました。これは「Steering なし」パターンと同じ行動です。

しかしチェックコードが `get_employee_info` が未呼び出しであることを検知し、`Guide` を返してツール実行をキャンセルしました。

モデルはフィードバック（「先に get\_employee\_info で従業員情報を確認してください」）を受け取り、`get_employee_info` を呼んでから再度 `approve_expense` を呼びました。今度は前提条件を満たしているので `Proceed` で続行。

**これが Steering です。** モデルが間違った行動をしても、チェックコードがキャンセルして正しい方向に矯正する。プロンプトの「お願い」ではなく、コードによる「チェックと矯正」です。

## Steering の仕組みまとめ

## まとめ

| 観点 | Steering なし | Steering あり |
| --- | --- | --- |
| 制御方式 | プロンプトで自然言語のお願い | Python コードでチェック |
| 強制力 | LLM の確率的な性質上、従わない可能性を排除できない | ツール実行をキャンセルして矯正 |
| メンテナンス | 複雑で長いプロンプトは変更の影響が読みにくい | チェックロジックは独立した Python コード |

Steering の本質は、**前提条件を満たさないツール呼び出しが実行されないことを決定論的に保証する**点にあります。LLM の確率的な振る舞いに頼るプロンプトだけでは、この保証は得られないでしょう。

## 参考リンク
