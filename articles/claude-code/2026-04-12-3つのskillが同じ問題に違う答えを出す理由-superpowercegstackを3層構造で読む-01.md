---
id: "2026-04-12-3つのskillが同じ問題に違う答えを出す理由-superpowercegstackを3層構造で読む-01"
title: "3つのSkillが同じ問題に違う答えを出す理由 ── Superpower・CE・gstackを3層構造で読む"
url: "https://zenn.dev/analysis/articles/thought-analyzer-harness-skills"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

最近、AI Agentの「実行品質問題」を解こうとするSkillが立て続けに登場している。

[Superpower](https://github.com/obra/superpowers)、[Compound Engineering（CE）](https://github.com/EveryInc/compound-engineering-plugin)、[gstack](https://github.com/garrytan/gstack)。3つとも解こうとしている問題は共通だ。

> AIがコードを書くとき、計画をスキップしやすく、品質が不安定で、固定されたワークフローがないためにそれを制限できない

──Jing Wang（[@jingwangtalk](https://x.com/jingwangtalk)）が3つを使い比べた感想を投稿し、注目を集めた。

しかし3つを試した結論は「それぞれ違う体験」だった。同じ問題を解こうとしているはずなのに、なぜそうなるのか。

これは「どのSkillが優れているか」の問いではない。**3つが、問題の異なる層に作用しているから**だ。

---

## 3つのSkillが解こうとしていること

まず、各Skillの設計思想を整理する。

**Superpower**：プロセス規律を強調する。`spec → plan → タスク分解 → 実行 → テスト・レビュー → 提出` という一連のフローを各ラウンドで踏む。利点は実行の制御性が高いこと。欠点は小さなタスクでもフローを踏むため、承認回数とトークン消費が増える。

**Compound Engineering（CE）**：知識の複利を強調する。`/ce:compound` が過去のエラーを蓄積し、次回同じミスを繰り返さないようにする。`/ce:ideate` が具体的な改善提案を生成し、優先順位をつける。ただし「改善提案がそれほど痛快でない」という声もある（Jing Wang）。

**gstack**：YCの知識と評価基準を埋め込み、製品・アイデアの品質を問い返す。AIが「魂の拷問をするように」製品コンセプトの弱点を突いてくる。知識の蓄積機能も持ち始めている。

---

## なぜ体験が違うのか：3層構造で読む

AIを使った作業には3つの層がある。

| 層 | 問い | 例 |
| --- | --- | --- |
| 発想層 | 何をつくるか、何を解くか | プロダクトの構想、問いの設定 |
| 構想層 | どう設計するか、何が制約か | 要件定義、フレーミング |
| 指示層 | AIにどう伝えるか | プロンプト、仕様書、フィードバック |

3つのSkillは、それぞれ異なる層で主に働いている。

**Superpowerは指示層に作用する。** `spec → plan → 実行` というフローは、指示の構造を標準化する設計だ。AIに渡る指示の精度と一貫性を上げることで、実行品質を安定させる。Jing Wangが「プロセスの制御がとても良い」と評したのは、この層での制御が強いからだ。

**CEも指示層に作用するが、別の方向から。** エラーの蓄積と学習は、フィードバックサイクルの質を上げる設計だ。「前回のミスを次回繰り返さない」は、指示の精度より**修正サイクルの精度**を高める。指示を上手くするより、ズレを早く正確に見つける力を鍛える。

**gstackは構想層・発想層に作用する。** YCの評価基準でアイデアを問い返すのは、「何をつくるか」「なぜつくるか」の層に入り込む設計だ。Superpowerが「どう実行するか」を問うなら、gstackは「それを実行すべきか、本当に正しい問いを立てているか」を問う。

---

## Jing Wangの結論は、3層構造の実証だった

Jing Wangは3つを使い比べた末にこう結論を出した。

> 大規模プロジェクトではgstackで製品とアイデアを磨き、superpowerで実行するのが良いと思います。

この推奨を図に落とすと、こうなる。

```
発想・構想の品質 → gstack（YC基準でフレーミングを問い返す）
          ↓
指示・実行の品質 → Superpower（プロセス規律で実行を制御する）
```

これはそのまま、3層構造の「構想層 → 指示層」の流れだ。

Jing Wangは3つのSkillを実際に使って試行錯誤した結果、**道具を使い分けることで構想と実行を分離する**という設計に自然に辿り着いた。理論から導いたわけではなく、体験から到達した。

---

## CEが「痒くも痛くもない」と感じられた理由

Jing Wangの感想の中で興味深いのは、CEへの評価だ。

> これらの改善提案はそれほど痛快ではなく、痒くも痛くもない感じです。

CEのエラー蓄積・改善提案機能は、確かに「指示層の改善」に効く。しかし「何をつくるか」というフレーミングが定まっていない状態でエラーを積み上げても、**方向ごとズレた実行の精度が上がるだけ**になる。

これは思考パターン分析でも同様の問題が起きる。フレーミングが弱いまま精緻な分析を回しても、フレーミングの偏りが99%の解釈に影響する（詳細は後述）。

CEが活きるのは、gstackで構想が固まった後の「同じ方向で精度を上げる」フェーズかもしれない。単独では威力が半減する。

補足しておくと、CEの本質的な価値は**セッションをまたいだエラーの蓄積記憶**にある。「前回のミスを今回引き継ぐ」という設計だ。これはTAの6軸（`error_recognition`・`iteration_style`）では単回セッション内のパターンしか捕捉できず、現状では直接測れない部分だ。将来の軸拡張の候補として認識している。

---

## あなたの思考パターンが、Skill選択に影響する

3層構造のどこに問題があるかは、人によって違う。

thought-analyzerの分析では、ユーザーによって詰まる層が異なることが繰り返し観察される。

| 詰まりやすい層 | 特徴（thought-analyzerの軸） | 相性の良いSkill |
| --- | --- | --- |
| 指示層 | `specification_precision` が低い、`iteration_style: batch_vague` | Superpower（実行フローを標準化） |
| 指示層のフィードバック | `error_recognition: result_only` | CE（エラーの構造認識を補完） |
| 構想層 | `need_for_cognition` は高いが `evaluation_framing: loss_first` で詰まる | gstack（問いの品質を外部から問い返す） |

「どのSkillを使うか」の前に、「自分がどの層で詰まっているか」を知ることが、選択の精度を上げる。

---

## 補足：自己進化記憶AgentとSkillの違い

最近、[hermes-agent](https://github.com/NousResearch/hermes-agent)のような「使うほどあなたの好みを学習する」AIも登場している。

こういったAgentはあなたのパターンをAI側が暗黙的に学習する。Skillはあなたのワークフローを構造化する。アプローチは正反対だ。

前者は「AIがあなたに合わせる」、後者は「あなたの思考プロセスを整える」。どちらが長期的に指示力を上げるかは、また別の問いになる。

---

## まとめ

3つのSkillの体験が違う理由は、「優劣」ではなく「作用する層」の違いだ。

* **gstack**：構想・発想の質を問い返す（構想層）
* **Superpower**：実行プロセスを規律化する（指示層・構造）
* **CE**：フィードバックサイクルの精度を上げる（指示層・改善）

Jing Wangが「gstackで磨き、superpowerで実行」に行き着いたのは、使い比べを通じて3層構造を実証的に発見した結果だ。

どの層で自分が詰まっているかを知ることが、Skill選択の出発点になる。

---

**← 関連記事**

[AIで理想を実現する3層フレームワーク ── 発想力×構想力×指示力](https://zenn.dev/thought_analyzer/articles/thought-analyzer-framework)

[コーディング指示力6軸の設計根拠 ── AI協働時代の技術指示能力](https://zenn.dev/thought_analyzer/articles/thought-analyzer-coding-6axes)

**本記事で取り上げたSkill**

[Superpower（GitHub）](https://github.com/obra/superpowers)

[Compound Engineering（GitHub）](https://github.com/EveryInc/compound-engineering-plugin)

[gstack（GitHub）](https://github.com/garrytan/gstack)

[thought-analyzer（skill本体）](https://github.com/thought-analyzer/thought-analyzer/blob/main/skills/skill.md?plain=1)：Claude Codeで実際に分析を実行する
