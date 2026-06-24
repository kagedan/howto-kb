---
id: "2026-06-23-prompt-cachingで-apiコストを90削減する初心者向け実装ガイド-01"
title: "Prompt Cachingで APIコストを90%削減する——初心者向け実装ガイド"
url: "https://zenn.dev/shun_producer/articles/claude-prompt-caching-beginner-guide"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

> シリーズ: 教科書バックログ B2（B1モデル選択ガイドの姉妹編）  
> あわせて読みたい：[Claudeモデル×エフォート選択ガイド](./claude-model-selection-guide.md)——本記事のキャッシュ知識を踏まえた上で、モデル選択とエフォート設定の最適化を扱っています。

## はじめに——「API呼び出しのたびに、同じ話を何度も聞かせている問題」

Claude API を使っていると、こんな経験はないだろうか。

毎日、同じシステムプロンプトを送り込んで、毎日、同じ背景情報を読ませて、毎回数百円のトークン代を払っている——。

もし、今日の買い物リストが昨日と同じなら、わざわざ全部読み上げ直さず「昨日のリストでいいよ」と言えたら。その部分の料金が 9割削減されたら。それが **Prompt Caching** です。

2026年6月現在、Claude API に組み込まれたこの機能は、ほぼ何も設定しなくても、自動で「変わらない部分」をキャッシュして再利用します。特に、チャットボット、ドキュメント処理、定期的な分析タスクを回す人には、**ほぼノーコストの値下げ** になります。

## Prompt Caching って何？——システムプロンプト × キャッシュ

ふつう、API を呼ぶたびに：

1. システムプロンプト（「あなたは優秀なアシスタントです」みたいなやつ）
2. 過去の会話履歴
3. 背景資料（マニュアル、コンテキスト）
4. 今回の質問

すべてを送り直します。すべてが **トークンカウント** されます。

Prompt Caching は、その中で「変わらない部分」を識別して、2回目以降は **キャッシュ済み部分は 1/10 の料金** で済ませます。

!

**料金の仕組み（Sonnet 4.6 基準）**

* 通常：システムプロンプト 30,000 トークン = $0.09
* キャッシュ有効時：同じプリフィックス = $0.009（90%削減！）

## 実装——「最小コード」で自動キャッシングを有効にする

では、実際に使ってみましょう。

### Step 1: SDK をインストール

```
pip install anthropic --break-system-packages
```

### Step 2: 最小実装コード

```
from anthropic import Anthropic

client = Anthropic()

# ここからが重要：システムプロンプトを「キャッシュ対象」に指定
system_prompt = """あなたはテクニカルライターです。
受け取ったコードを分析して、1行ずつ日本語で説明してください。
難しい用語が出たら、例えで置き換えます。"""

def analyze_code(code_snippet: str) -> str:
    """コードを分析する（キャッシング有効）"""

    # 重要：cache_control フィールドを追加
    response = client.messages.create(
        model="claude-sonnet-4-6",  # 2026年6月時点の本番デフォルト
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}  # ←ここ！
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"このコードを説明して：\n{code_snippet}"
            }
        ]
    )

    return response.content[0].text

# 使用例
code1 = "x = [i for i in range(10) if i % 2 == 0]"
code2 = "def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)"

print("1回目:", analyze_code(code1))
print("2回目:", analyze_code(code2))  # ← この呼び出しで、システムプロンプト部分がキャッシュから復帰
```

### Step 3: キャッシュが有効だったか確認

```
# レスポンス内に詳細が含まれている
print(f"入力トークン数: {response.usage.input_tokens}")
print(f"キャッシュ読み込み: {response.usage.cache_read_input_tokens}")
print(f"キャッシュ書き込み: {response.usage.cache_creation_input_tokens}")
```

**読み込みが 0 でない** = キャッシュが効いている証拠です。

## 動かないときの調べ方——キャッシュが効かないパターンを切り分ける

「何度も呼んでるのに、キャッシュが利いていない」という時の診断フロー：

### ① キャッシュ統計を確認

```
if response.usage.cache_read_input_tokens > 0:
    print("✅ キャッシュ有効")
else:
    print("❌ キャッシュ未使用")
    print(f"なぜ？ 新規書き込み: {response.usage.cache_creation_input_tokens}")
```

### ② システムプロンプトが本当に同じか確認

キャッシュは「プリフィックスが完全一致」でないと効きません。

```
# 悪い例：毎回違うシステムプロンプト
system1 = "あなたはテクニカルライターです"
system2 = "あなたはテクニカルライター です"  # スペース追加で完全NG

# 良い例：定数として固定
SYSTEM_PROMPT = "あなたはテクニカルライターです"
```

### ③ モデルが対応しているか確認

キャッシング対応モデル（2026年6月時点）：

* ✅ Claude Sonnet 4.6（本番デフォルト推奨）
* ✅ Claude Opus 4.8
* ✅ Claude Haiku 4.5
* ✅ 旧世代の Sonnet 4.5 / Opus 4.5 など、4.x系全般
* ❌ Claude 3.x 以前の旧モデル（推奨されない）

### ④ 最小限に絞ってテスト

```
# 複雑なコードをシンプルにして再テスト
system=[{"type": "text", "text": "You are helpful.", "cache_control": {"type": "ephemeral"}}]
messages=[{"role": "user", "content": "Hello"}]
# これでキャッシュが効くなら、複雑さが原因
```

## よくある間違い・無駄・禁止事項

### ❌ 間違い 1：毎回 `cache_control` を付け直す

```
# 悪い例：毎回指定
for i in range(10):
    response = client.messages.create(
        system=[{"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}}],
        # ...
    )
```

**何が起きるか**：毎回「新規キャッシュ作成」になり、キャッシュ読み込みが発生しない。

**対策**：システムプロンプトを定数化する。

### ❌ 間違い 2：ユーザー入力をシステムプロンプトに含める

```
# 悪い例：毎回違うプロンプト
system = f"あなたは {user_name} の担当者です"  # ← ユーザーごとに違う！

# 良い例：ユーザー情報は messages に
system = "You are a helpful assistant"
messages = [
    {"role": "user", "content": f"I'm {user_name}. Please help me."}
]
```

### ❌ 間違い 3：キャッシュの有効期限を過信する

Ephemeral キャッシュ（`cache_control: ephemeral`）は、5分程度で自動削除されます。長時間のセッションでは、**1時間キャッシュ**（extended duration）の利用を検討してください。

長期キャッシュが必要なら、別途データベースに保存するか、アプリ側で履歴管理が必要。

### ❌ 間違い 4：extended thinking のbudget\_tokensを動的に変更する

姉妹編の[Claudeモデル×エフォート選択ガイド](./claude-model-selection-guide.md)でも触れていますが、`budget_tokens`（エフォートの強さ）を動的に変えると **message history のキャッシュが無効化**されます。エフォートは用途ごとに固定運用が鉄則です。

### 🔍 こんなときは「キャッシュを使うな」

* **1回限りの呼び出し** → 書き込み遅延のせいで遅くなる
* **1,024トークン未満のシステムプロンプト** → 仕様上キャッシュ対象外
* **セッションごとにシステムプロンプトが変わる** → 毎回新規キャッシュ

## 実践例：チャットボットで毎日 9割コスト削減

```
from anthropic import Anthropic

client = Anthropic()

# 固定のシステムプロンプト（キャッシング対象）
SYSTEM = """あなたはカスタマーサポート担当者です。
以下のナレッジベースに基づいて、顧客の質問に回答してください。

【ナレッジベース】
- 商品 A の返品期限：30日
- 送料：3000円以上で無料
- 問い合わせ時間：月〜金 10:00-18:00

（※実用上は、最低 1,024 トークン分のナレッジベース・指示文を入れてください。
ここでは説明のため省略しています。）
"""

def support_chat(user_question: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": SYSTEM,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[{"role": "user", "content": user_question}]
    )

    # 統計表示
    cache_hit = response.usage.cache_read_input_tokens
    if cache_hit > 0:
        savings = cache_hit * 0.9  # 90% 削減
        print(f"💰 キャッシュ利用：{cache_hit} トークン、約 {savings:.0f} 円節約！")

    return response.content[0].text

# 1日 100件の問い合わせがあると...
# システムプロンプト（仮に3,000トークン）が100回再利用
# → 月 9,000,000 トークン分、Sonnet 4.6 の単価で約 $24/月 → 年 $290 程度の削減
```

## まとめ——「最小コード、最大削減」

Prompt Caching は決して難しくありません。

* **3行追加**：`system` に `cache_control: {"type": "ephemeral"}` を付けるだけ
* **自動動作**：以降のリクエストで、同じシステムプロンプトなら勝手にキャッシュから復帰
* **効果**：90% のコスト削減（適用範囲内で）
* **最低条件**：プリフィックスが **1,024トークン以上** あること

繰り返すタスク（チャットボット、定期分析、ドキュメント処理）を回してるなら、今すぐ試す価値があります。

「キャッシュが効くかどうか」は、`cache_read_input_tokens` を見れば一目瞭然。試行錯誤も簡単です。

---

## あわせて読みたい
