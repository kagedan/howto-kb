---
id: "2026-04-25-aiエージェントシリーズ-第7弾マルチagent基礎anthropic-harness論文に学ぶ専門-01"
title: "【AIエージェントシリーズ 第7弾】マルチAgent基礎：Anthropic Harness論文に学ぶ専門家チームレビューの作り方"
url: "https://qiita.com/bit-tanghao/items/29708ac044a58e8e0844"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "Python", "qiita"]
date_published: "2026-04-25"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

前回（第6弾）では、コードレビューAgentに4つの専門Skill（Security / Performance / Style / Documentation）を持たせた。ファイルを読んだあと、どのSkillを使うかをLLMが判断し、結果を統合して出力する構成だ。

しかし、このAgentには根本的な問題がある。

**「評価者と実行者が同一人物」** という問題だ。

自分が書いたコードを自分でレビューするとどうなるか。ベテランエンジニアでも、盲点は生まれやすい。AIも同じだ。

2026年3月、AnthropicはこのAIの「自己評価バイアス」を正面から解決した論文をエンジニアリングブログに公開した。この記事ではその知見をコードレビューAgentに応用し、**専門家チームによる並列レビュー**を実装する。

---

## Anthropic Harness論文が明かした2つの失敗パターン

Anthropic Labs の Prithvi Rajasekaran が執筆した [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（2026/3/24）は、長時間自律コーディングを実現するために Anthropic が内部で設計したマルチAgent基盤の解説だ。

論文が指摘する**単一Agentの2大失敗パターン**がこちら。

### 失敗① Context Anxiety（コンテキスト不安）

コンテキストウィンドウが埋まってくると、Agentは「早く終わらせなければ」という焦りのような動作をし始める。未完成のまま出力を切り上げたり、後半の指摘が粗くなったりする現象だ。

```
# context anxietyのイメージ
コンテキスト使用率  0%  ──────────────── 100%
Agentの動作品質   高い ────────────── 低下→打ち切り
```

### 失敗② Self-evaluation Bias（自己評価バイアス）

自分が生成した出力を自分で評価すると、Agentは一貫して過大評価する。論文には「たとえ人間の目には明らかに品質が低くても、自信満々に褒める」と書かれている。

> "When asked to evaluate work they've produced, agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre."

この2つの問題に対して Anthropic が出した答えが **Generator / Evaluator の分離**、そして **Planner → Generator → Evaluator の3層アーキテクチャ** だ。

---

## コードレビューAgentへの応用

Anthropicの3層を、コードレビューの文脈に置き換えると次のようになる。

| Anthropic Harness | 今回の実装 | 役割 |
|---|---|---|
| Planner | Orchestrator | タスクを分解してサブAgentに割り当て |
| Generator × 3 | Security / Performance / Style Agent | 専門観点だけに集中してレビュー |
| Evaluator | （第8弾で実装） | 出力品質を独立した視点で評価 |

今回は Evaluator の接続口だけ設計しておき、実装は第8弾に回す。まず「分割して並列実行」という土台を固める。

### trust_level という概念

マルチAgent設計では、各Agentがどの立場で動いているかを明示することが重要になる。今回はsystem promptに `trust_level` タグを埋め込む設計を採用した。

```python
# Orchestratorのsystem prompt（概念）
trust_level: orchestrator  # タスク割り当て・結果統合の権限を持つ

# サブAgentのsystem prompt
trust_level: worker        # 与えられた観点だけを実行する権限
```

これはAnthropicの[Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)で言及されている「エージェント間の役割明示」の実践だ。第11弾のHuman-in-the-Loopでは `trust_level: human` をここに加える。

---

## 実装

### ディレクトリ構成

```
ep07_multi_agent/
├── orchestrator.py      # メインAgent（タスク割り当て・統合）
├── sub_agents.py        # Security / Performance / Style の3専門Agent
├── aggregator.py        # 結果統合・重複排除
├── requirements.txt
└── review_targets/
    └── sample_01.py     # SQLインジェクション（第6弾と同じ）
```

### sub_agents.py（抜粋）

各Agentはsystem promptで担当観点を明示し、結果をJSONで返す。

```python
SECURITY_SYSTEM = """
あなたはセキュリティ専門のコードレビューAgentです。
trust_level: worker
担当: セキュリティ観点のみ

以下の脆弱性カテゴリに絞ってレビューしてください：
- SQLインジェクション
- 平文パスワード / 認証の欠陥
- ハードコードされた秘密情報
...

結果は必ずJSON形式で返してください：
{
  "issues": [...],
  "summary": "..."
}
"""
```

ポイントは2点。

1. **「担当: ○○観点のみ」と明示する**。他の観点を指摘しないよう制約することで、専門性が上がり出力が安定する。
2. **JSON強制**。Orchestratorがパースしやすくするため、自然言語の混入を防ぐ。

### aggregator.py（抜粋）

3つのAgentから集まった指摘を重複排除してseverity順にソートする。

```python
def _is_duplicate(a: ReviewIssue, b: ReviewIssue) -> bool:
    """カテゴリが一致し、メッセージの先頭30文字が重複する場合は重複とみなす。"""
    if a.category == b.category:
        overlap = len(set(a.message[:30]) & set(b.message[:30]))
        if overlap > 15:
            return True
    return False
```

SecurityAgentとStyleAgentが「ハードコードされた認証情報」を別々に指摘するケースが実際に発生する。このロジックで1件にまとめる。

### orchestrator.py（抜粋）

```python
def orchestrate(filepath: Path) -> None:
    code = filepath.read_text(encoding="utf-8")
    filename = filepath.name

    print(f"🚀 オーケストレーター起動: {filename}")

    sec_result   = run_security_agent(code, filename)
    perf_result  = run_performance_agent(code, filename)
    style_result = run_style_agent(code, filename)

    report = aggregate([sec_result, perf_result, style_result])
    print(format_report(filename, report))
```

現在は逐次実行だが、`concurrent.futures.ThreadPoolExecutor` に差し替えると3 Agent を並列実行できる。今回はシンプルさを優先して逐次にした。

![ep07_sequence_diagram.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2604123/ad43a6f1-f836-43b6-a987-f49f6940b6f7.png)

---

## 実行ログ

`sample_01.py`（SQLインジェクション + 平文パスワード）に対して実行した結果。

```
============================================================
AIエージェントシリーズ 第7弾: マルチAgent コードレビュー
構成: Orchestrator → [Security / Performance / Style] → Aggregator
============================================================
🚀 オーケストレーター起動: sample_01.py
  → SecurityAgent    に割り当て中...
     完了: 2件の指摘
  → PerformanceAgent に割り当て中...
     完了: 3件の指摘
  → StyleAgent       に割り当て中...
     完了: 4件の指摘
  → Aggregator で統合中...

============================================================
📋 Multi-Agent コードレビュー結果: sample_01.py
============================================================
【各Agentのサマリー】
  [SecurityAgent] SQLインジェクションと平文パスワード比較の2つの重大なセキュリティ脆弱性が検出されました。パラメータ化クエリとパスワードハッシング化が必須です。
  [PerformanceAgent] パフォーマンス観点では、DB接続のリソース解放漏れが最大の問題です。接続プーリングまたはコンテキストマネージャ(with文)の導入を推奨します。
  [StyleAgent] スタイル面ではdocstring不足とマジックナンバーの使用が主な指摘です。コードの可読性向上のため、関数説明とインデックスの意味を明確にしてください。

【統合指摘リスト】（重複排除後: 8件）

  🔴 CRITICAL (3件)
    [SecurityAgent] [SQLインジェクション] ユーザー入力をf文字列で直接クエリに埋め込んでいます。攻撃者は username に ' OR '1'='1 などを入力してクエリを改変できます。パラメータ化されたクエリ（プレースホルダ）を使用してください。
      → query = f"SELECT * FROM users WHERE username = '{username}'"
    [SecurityAgent] [平文パスワード / 認証の欠陥] パスワードが平文で保存・比較されています。bcrypt、Argon2などのハッシング関数を使用し、ハッシュ化されたパスワードと比較してください。
      → if user and user[2] == password:
    [PerformanceAgent] [リソース解放漏れ] get_user()関数内でDB接続がクローズされていません。接続オブジェクト(conn)とカーソル(cursor)が開きっぱなしになり、リソースリークの原因となります。
      → conn = sqlite3.connect("users.db") ～ return cursor.fetchone() の間にconn.close()がない

  🟡 WARNING (2件)
    [PerformanceAgent] [DB接続の管理] login()関数が呼ばれるたびにget_user()でDB接続が生成されます。接続プーリングやコンテキストマネージャの使用を検討してください。
      → def login(username, password):
    [StyleAgent] [マジックナンバー] ハードコードされたインデックス `user[2]` は何を指すのか不明瞭です。定数として定義するか、タプルアンパックを使用してください。
      → if user and user[2] == password:

  🔵 INFO (3件)
    [PerformanceAgent] [メモリ効率] cursor.fetchone()の戻り値がタプルで、user[2]でアクセスしています。列名ベースのアクセス(row_factory)を使用すると可読性とメンテナンス性が向上します。
      → if user and user[2] == password:
    [StyleAgent] [docstring] 関数 `get_user` にdocstringがありません。関数の目的、引数、戻り値を説明するdocstringを追加してください。
      → def get_user(username):
    [StyleAgent] [PEP8] コメント '# SQLインジェクション脆弱性' と '# 平文パスワード比較' は実装上の問題を指摘しているように見えます。本来は実装時に修正すべき内容で、コメント化するべきではありません。
      → # SQLインジェクション脆弱性
```

注目したいのはStyleAgentの最後の指摘だ。「脆弱性を示すコメントは修正すべき問題であり、コメントとして残すべきではない」という観点は、SecurityAgentもPerformanceAgentも出さなかった。**専門Agentが1つの視点に集中したことで、他のAgentが見逃す角度の指摘が生まれた。** これがマルチAgent分割の実質的なメリットだ。

第6弾（単一Agent）と比べて何が変わったか。

| 項目 | 第6弾（Skills Agent） | 第7弾（Multi-Agent） |
|---|---|---|
| 指摘の視点 | 1つのAgentが全観点を担当 | 専門Agentが1観点に集中 |
| 重複指摘 | 発生しにくい（一元処理） | 発生する→Aggregatorで除去 |
| 拡張方法 | Skillを1ファイルに追記 | Agentファイルを1本追加 |
| Evaluator接続 | 構造上難しい | Aggregator後に自然に挿入できる |

---

## 設計上の気づき：Aggregatorの必要性

実行してみると、SecurityAgentとStyleAgentが同じ「ハードコード認証情報」を別の角度から指摘するケースが頻発した。これは **分割したことで生まれる代償** だ。

Anthropic論文でも「Generator と Evaluator の分離は直ちに問題を消すわけではない。Evaluatorを懐疑的に調教するほうが、Generatorを自己批判的にするよりはるかにやりやすい」と述べている。

つまり分割は「問題を解決する」のではなく「問題を制御可能な形に変換する」。

重複指摘という新しい問題は、Aggregatorというシンプルな仕組みで制御できた。Evaluatorという新しい役割は、第8弾のDebate Patternで制御する。

---

## 第8弾への予告

今回の構成には、まだ重大な欠陥がある。

**誰も出力品質を保証していない。**

Aggregatorは指摘を統合するが、指摘の「質」は評価しない。SecurityAgentが見逃したバグがあっても、誰も気づかない。Anthropic論文が最も強調したのはまさにこの点だ。

```
現在の構成:
Orchestrator → [Security / Performance / Style] → Aggregator → 出力

第8弾で追加:
Orchestrator → [Security / Performance / Style] → Aggregator → Evaluator → 出力
                                                                    ↑
                                                       Debate Pattern / OutputValidator
```

第8弾では、独立したEvaluatorを接続し、出力品質を定量スコアで測る **Debate Pattern** を実装する。

---

## まとめ

- 単一Agentの「自己評価バイアス」と「context anxiety」はAnthropicの論文が実証した失敗パターン
- **Generator / Evaluator の分離**がAnthropicの解答。今回はGeneratorを3専門Agentに分割した
- **trust_level タグ**で各Agentの権限・役割を明示する設計は、第11弾のHuman-in-the-Loopまで使い回す
- Aggregatorは「分割によって生まれる新問題（重複）」を制御する役割
- 次の課題は「出力品質を誰が保証するか」→第8弾のEvaluator実装へ

---

## コード

```
ep07_multi_agent/
├── orchestrator.py
├── sub_agents.py
├── aggregator.py
├── requirements.txt
└── review_targets/sample_01.py
```

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your_key"
python orchestrator.py
```
