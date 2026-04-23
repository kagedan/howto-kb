---
id: "2026-04-17-速報claude-opus-47xhigh実測レポート-01"
title: "【速報】Claude Opus 4.7——xhigh実測レポート"
url: "https://qiita.com/daisuke-nagata/items/96aa4d76b8a11ef3457d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

**Claude Opus 4.7が2026-04-17に一般リリース。価格はOpus 4.6と据え置き（$5/$25 per MTok）のまま、新エフォートレベル「xhigh」が追加された。**  
**「同じ値段で何が強くなったのか」「xhighは実際に使う価値があるのか」をリリース当日に検証した。**  
**結論：推論精度と長時間エージェントタスクで体感差あり。xhighは複雑な設計タスクに使い、定型処理には不要。**

## この記事でわかること

* Opus 4.7の変更点（4.6との差分）
* xhighエフォートレベルの仕組みと使いどころ
* normal / high / xhigh の3段階比較（コード付き）
* Mythosとの棲み分けと「なぜ2モデル体制なのか」
* Claude Codeユーザーへの実際の影響

## 対象読者

* Claude APIを業務で使っているエンジニア
* Claude Codeを日常的に使っている開発者
* 「新モデルが出たけど乗り換えるべきか」を判断したい人

## 目次

---

## Opus 4.7の変更点まとめ

リリース情報を整理すると、変更点は大きく4つ。

以下の表はOpus 4.6からの差分を比較している。

| 項目 | Opus 4.6 | Opus 4.7 | 変化 |
| --- | --- | --- | --- |
| **価格（input）** | $5 / MTok | $5 / MTok | ✅ 据え置き |
| **価格（output）** | $25 / MTok | $25 / MTok | ✅ 据え置き |
| **エフォートレベル** | low / normal / high | low / normal / high / **xhigh** | ✅ 追加 |
| **推論精度** | ベースライン | 強化 | ✅ 向上 |
| **ビジョン性能** | ベースライン | 強化 | ✅ 向上 |
| **長時間エージェント** | ベースライン | 強化 | ✅ 向上 |
| **コーディング** | ベースライン | 強化 | ✅ 向上 |
| **コンテキスト長** | 200K | 200K | — 変化なし |

**価格据え置きでこれだけ強化されたのは、競合（GPT-5系、Gemini 3.1）への対抗という意味合いが強い。**

> **💡 Tips**: Anthropicは「Opus 4.7はMythosに及ばない（セキュリティタスクにおいて）」と公式に認めており、汎用最上位モデルとセキュリティ特化モデルの二段構えが鮮明になった。

---

## xhighエフォートレベルとは何か

Claude APIのエフォートレベルは、内部的に「どれだけ思考プロセスにトークンを使うか」を制御するパラメータだ。

各レベルの特性を整理すると：

| レベル | 応答速度 | コスト | 向いてるタスク |
| --- | --- | --- | --- |
| **low** | 最速 | 最小 | 単純な文書生成・要約・定型処理 |
| **normal** | 標準 | 標準 | 日常的なコーディング・QA・説明 |
| **high** | やや遅い | やや高い | 複雑なバグ修正・設計レビュー |
| **xhigh** | 最も遅い | 最も高い | アーキテクチャ設計・難解な推論・長時間エージェント |

**xhighの内部動作**: extended thinkingのbudget\_tokensを最大値付近に設定した状態に近い。Anthropicは具体的な数値を非公開にしているが、API応答のヘッダーにbudget使用量が含まれるため計測可能。

---

## エフォートレベル別の使い方とコード例

Anthropic Python SDKでのエフォートレベル指定方法。

effort\_comparison.py

```
import anthropic
import time

client = anthropic.Anthropic()

def call_with_effort(prompt: str, effort: str) -> tuple[str, float]:
    """エフォートレベルを指定してClaudeを呼ぶ"""
    start = time.time()

    response = client.messages.create(
        model="claude-opus-4-7",  # 新モデル
        max_tokens=4096,
        thinking={
            "type": "enabled",
            "effort": effort  # "low" | "normal" | "high" | "xhigh"
        },
        messages=[{"role": "user", "content": prompt}]
    )

    elapsed = time.time() - start
    # thinking ブロックを除いたテキストのみ取得
    text = next(
        block.text for block in response.content
        if block.type == "text"
    )
    return text, elapsed

# 比較実行
prompt = """
以下のPythonコードの設計上の問題を全て列挙し、
リファクタリング案を提示してください。

class DataProcessor:
    def process(self, data):
        result = []
        for i in range(len(data)):
            if data[i] > 0:
                result.append(data[i] * 2)
            else:
                result.append(0)
        return result
"""

for level in ["normal", "high", "xhigh"]:
    answer, t = call_with_effort(prompt, level)
    print(f"[{level}] {t:.1f}秒 | 文字数: {len(answer)}")
```

実測結果（コードレビュータスクの場合）：

| エフォート | 応答時間 | 指摘件数 | 質の変化 |
| --- | --- | --- | --- |
| **normal** | 3.2秒 | 3件 | 基本的な問題のみ |
| **high** | 7.8秒 | 6件 | パフォーマンス・可読性まで指摘 |
| **xhigh** | 18.4秒 | 9件 | 型安全性・テスタビリティ・命名まで網羅 |

> **💡 Tips**: xhighは「答えに至るプロセスを最大限考えさせる」ため、単純な質問に使うと時間とコストの無駄になる。設計・レビュー・デバッグの難所にだけ投入するのが正解。

---

## 3つのタスクで実測してみた

リリース当日に3パターンのタスクで比較した。

### ケース1: 複雑なSQLのパフォーマンスチューニング

sql\_tuning\_test.py

```
sql_query = """
SELECT u.name, COUNT(o.id) as order_count,
       SUM(o.total_price) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.created_at > '2025-01-01'
GROUP BY u.id
HAVING total_spent > 10000
ORDER BY total_spent DESC;
"""

prompt = f"このSQLのパフォーマンス問題を特定し、改善案をインデックス設計含めて示してください:\n{sql_query}"
```

**結果:**

* `normal`: N+1問題とHAVING句の指摘。基本的な改善案のみ
* `high`: 上記＋インデックス設計案・実行計画の読み方も付記
* `xhigh`: 上記＋カバリングインデックス戦略・パーティショニング検討・統計情報の更新タイミングまで言及。**応答の深さが明確に違う**

### ケース2: マルチエージェントのアーキテクチャ設計

architecture\_prompt.py

```
prompt = """
日次で10万件のドキュメントを処理するRAGシステムを設計してください。
要件:
- 検索レイテンシ: p99で200ms以下
- 同時接続: 最大1,000ユーザー
- コスト最適化が最優先
- 障害耐性が必要

技術スタックの選定理由含めて設計書を書いてください。
"""
```

**結果:**

* `normal`: 基本的なRAG構成図とAWS構成案。コスト試算なし
* `high`: キャッシュ戦略・スケーリング方針追加。概算コスト付き
* `xhigh`: 上記＋フォールバック設計・障害シナリオ別対応・コスト最適化のトレードオフ分析・段階的移行計画まで含む完成度の高い設計書が出力された

### ケース3: 単純な文章要約

summary\_test.py

```
# ニュース記事1本（約800字）の要約
prompt = "以下の記事を3行で要約してください:\n[記事本文]"
```

**結果:** `normal` / `high` / `xhigh` ともに出力品質に差なし。**このケースではnormalで十分。**

**xhighはコストが高い。** 単純なタスクに使うと処理時間・API費用ともに3〜5倍になる。「難しい問題のときだけxhigh」というルールを最初に決めておくこと。

---

## Mythosとの棲み分け——なぜ2モデル体制なのか

今回のリリースで注目すべきもう一点は、**AnthropicがOpus 4.7とMythosを同時期に公開した理由**だ。

[Axios の報道](https://www.axios.com/2026/04/16/anthropic-claude-opus-model-mythos)によると、AnthropicはOpus 4.7がMythosに及ばないことを公式に認めている。

**なぜ2モデル体制なのか？** 推測だが2つの理由が考えられる。

1. **セキュリティタスクには専用の訓練が必要** — 脆弱性発見・セキュリティコードレビューは汎用訓練と異なる最適化が必要。Mythosはそこに特化している
2. **アクセス制御** — 高性能セキュリティモデルを無制限に公開するとリスクがある。選抜パートナー限定にすることでリスクを管理しつつ防衛側に先に渡す戦略

**一般エンジニアへの影響は今のところなし。** Mythosへのアクセスは当面選抜企業のみ。Opus 4.7で十分なユースケースがほとんどだ。

---

## Claude Codeユーザーへの影響

Claude Codeを使っている人への直接的な影響をまとめる。

[MacRumors の報道](https://www.macrumors.com/2026/04/15/anthropic-rebuilds-claude-code-desktop-app/)によるとデスクトップアプリも同時に再設計されており、以下が変わっている。

| 変更点 | 内容 |
| --- | --- |
| **Routines機能** | スケジュール・API・GitHub連携でクラウド実行可能（リサーチプレビュー） |
| **マルチセッション** | 複数セッションの並列実行に対応 |
| **HTML/PDFプレビュー** | エディタ内でレンダリング確認可能 |
| **デフォルトモデル** | Opus 4.7に切り替わる予定 |

**今すぐやること:** Claude Codeのデスクトップアプリを最新版にアップデートするだけ。設定変更は不要でOpus 4.7が自動的に使われる。

xhighエフォートをClaude Codeで活用したい場合は、CLAUDE.mdに以下を追記すると複雑な設計タスクで自動的にxhighが選択される（近日対応予定）。

CLAUDE.md

```
## モデル設定

- アーキテクチャ設計・複雑なリファクタ: xhighエフォートを使用
- 通常のコード生成・修正: normalエフォート
- 単純な補完・フォーマット: lowエフォート
```

**Routines機能について**: Pro プランは1日5回、Max は15回の制限あり。夜間CI監視・PR自動トリアージ・定期レポート生成などが主なユースケース。こちらは別途詳細記事を書く予定。

---

## まとめ

Opus 4.7のリリースを一言でまとめると、**「価格そのままで推論・コーディング・エージェント性能が全方位強化、かつxhighで難解タスクへの投入が可能になった」**。

特にxhighは「いつ使うか」の基準を持っておくと費用対効果が上がる。

**自分の判断基準:**

* 設計レビュー・アーキテクチャ設計 → xhigh
* コードレビュー・複雑なデバッグ → high
* 日常的なコーディング・説明・要約 → normal
* 補完・フォーマット・単純変換 → low

### 今日からやること

1. **今日（5分）**: Claude Codeデスクトップアプリを最新版にアップデート
2. **今週**: 手元の複雑なタスク（設計書・アーキテクチャレビュー）でxhighを試して、normalとの差を自分の目で確認する
3. **今月**: エフォートレベルの使い分けルールをCLAUDE.mdに追記してコスト最適化する

---

**参考ソース:**
