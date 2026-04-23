---
id: "2026-04-22-革命aiが6時間自律コーディングanthropicの3エージェントharnessが放置開発を実現した-01"
title: "【革命】AIが6時間自律コーディング！Anthropicの3エージェントHarnessが「放置開発」を実現した"
url: "https://qiita.com/emi_ndk/items/facb4cecfd145f6d6c1a"
source: "qiita"
category: "ai-workflow"
tags: ["AI-agent", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

「AIに丸投げしたら、6時間後にゲームが完成していた」

これ、冗談じゃない。2026年4月にAnthropicが公開した**3-Agent Harness**アーキテクチャの実際の成果だ。

## 結論から言うと

Anthropicが公開した3エージェント構成（Planner・Generator・Evaluator）を使えば、**数時間の自律開発が可能**になる。従来の単一エージェントでは20分で$9、でも「動かないゲーム」しか作れなかった。3エージェント構成なら6時間で$200、**完全に遊べるゲーム**が完成する。

## なぜ単一エージェントは長時間作業で崩壊するのか

AIエージェントを長時間動かした経験がある人なら分かるだろう。

* **コンテキストが膨張**して、最初の指示を忘れる
* **自己評価が甘くなる**（「できました！」→動かない）
* **手戻りが爆発**して、同じバグを何度も直す

Anthropicの研究チームも同じ壁にぶつかった。そして彼らが出した答えが「**エージェントを分割する**」というシンプルな発想だった。

## 3エージェントの役割分担

```
┌─────────────┐
│   Planner   │ ← ユーザーの1-4文の指示を詳細仕様書に展開
└──────┬──────┘
       ▼
┌─────────────┐
│  Generator  │ ← スプリント単位で実装、各スプリント後に自己評価
└──────┬──────┘
       ▼
┌─────────────┐
│  Evaluator  │ ← Playwright MCPで実際にUIを操作してテスト
└─────────────┘
```

### Planner（企画エージェント）

ユーザーの曖昧な指示（「音楽制作アプリ作って」）を受け取り、**野心的なスコープ**を含む詳細な製品仕様書を生成する。

ポイントは「技術的な詳細を書きすぎない」こと。過度な技術指定は、後続エージェントのカスケードエラーを引き起こす。

### Generator（実装エージェント）

React + Vite + FastAPI + SQLite（後にPostgreSQL）のスタックで、**スプリント単位**で機能を実装する。

各スプリントの終わりに自己評価を行い、QA（Evaluator）に引き継ぐ。Gitでバージョン管理しながら進める。

### Evaluator（評価エージェント）

ここが革命的。**Playwright MCPを使って実際にアプリを操作**し、UIの動作・APIエンドポイント・データベース状態をチェックする。

スプリント開始前にGeneratorと「スプリント契約」を締結し、明確な成功基準を定義。主観的な「いい感じ」ではなく、**具体的な評価軸**で採点する：

* 製品の深さ
* 機能の完成度
* ビジュアルデザイン
* コード品質

## 実際のパフォーマンス

### ゲーム制作の例（Opus 4.5）

| 構成 | 所要時間 | コスト | 結果 |
| --- | --- | --- | --- |
| 単一エージェント | 20分 | $9 | コアゲームプレイが動作せず |
| 3エージェント | 6時間 | $200 | 完全にプレイ可能 |

### DAW（音楽制作ソフト）の例（Opus 4.6）

* **総所要時間**: 3時間50分
* **総コスト**: $124.70
* **内訳**: Planner（4.7分、$0.46）、Build（3+イテレーション）、QA（3イテレーション）

## なぜ「分離」が効くのか

**自己評価バイアス問題**  
AIは自分の出力を過大評価しがち。特にデザインなど主観的なタスクで顕著。Evaluatorを別エージェントにすることで、「お手盛り採点」を防げる。

実験では、**5〜15回のイテレーション**を回すことで品質が向上した。ただし面白いのは、必ずしも最終版が最良ではなく、中間バージョンが最高点を出すケースもあったということ。

## 今日から試せる実装パターン

```
# 簡略化した3エージェントハーネスの概念実装
from anthropic import Claude

class ThreeAgentHarness:
    def __init__(self):
        self.planner = Claude(model="claude-opus-4-7")
        self.generator = Claude(model="claude-opus-4-7")
        self.evaluator = Claude(model="claude-opus-4-7")

    def run(self, user_prompt: str):
        # Phase 1: Planner expands spec
        spec = self.planner.generate_spec(user_prompt)

        # Phase 2: Sprint loop
        for sprint in spec.sprints:
            # Generator and Evaluator negotiate contract
            contract = self.negotiate_contract(sprint)

            # Generator implements
            code = self.generator.implement(sprint, contract)

            # Evaluator tests with Playwright
            result = self.evaluator.test(code, contract)

            if not result.passed:
                # Iterate until contract is met
                code = self.iterate(code, result.feedback)

        return code
```

## 注意点：コストと時間のトレードオフ

3エージェント構成は明らかに高コスト（$9 → $200）。しかし「動かないゴミ」に$9払うのと、「完全に動くプロダクト」に$200払うのと、どちらが価値があるか？

答えは明らかだろう。

## Managed Agentsとの組み合わせ

2026年4月8日にリリースされた**Claude Managed Agents**を使えば、このアーキテクチャをAnthropicのインフラ上で動かせる。ローカルでラップトップを開きっぱなしにする必要がなくなった。

```
# managed_agent.yaml
name: "full-stack-builder"
agents:
  - role: planner
    prompt: "Expand user requirements into detailed product spec"
  - role: generator
    prompt: "Implement features sprint by sprint"
  - role: evaluator
    prompt: "Test with Playwright, grade against contract"
schedule:
  trigger: "on_push"
  repository: "your-repo"
```

## まとめ

* **単一エージェントの限界**を突破するには「分割」が鍵
* **Planner・Generator・Evaluator**の3分割で長時間自律開発が可能に
* **自己評価バイアス**を別エージェントで解消
* コストは上がるが、**品質は比較にならない**
* **Managed Agents**と組み合わせれば完全放置運用も可能

「寝てる間にアプリが完成している」時代は、もう始まっている。

---

この記事が参考になったら、いいねと保存をお願いします！

**質問**: あなたは長時間の自律開発、試したことありますか？うまくいった例・失敗した例をコメントで教えてください。

## 参考リンク

Harness design for long-running application development

Anthropic Designs Three-Agent Harness Supports Long-Running Full-Stack AI Development - InfoQ

Claude Managed Agents
