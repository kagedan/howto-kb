---
id: "2026-07-10-oikon48-anthropicのメンバーがclaude-fable-5のコストを大幅に抑えつつ性-01"
title: "@oikon48: Anthropicのメンバーが、Claude Fable 5のコストを大幅に抑えつつ性能を維持する方法の記事を公開 多"
url: "https://x.com/oikon48/status/2075645044930023708"
source: "x"
category: "ai-workflow"
tags: ["x"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

Anthropicのメンバーが、Claude Fable 5のコストを大幅に抑えつつ性能を維持する方法の記事を公開

多くのタスクでは「必要な知能」がトークンごとに大きく偏っている。全部をFable 5でやるのは高コストなので、ハーネス（エージェントの制御枠組み）がこの偏りを見極めて、Fable 5を戦略的に使うべき

Lance氏が挙げている主な使い方パターンは以下の3つ：

1. Fable 5をオーケストレーター（指揮者）として使い、安いモデルに実行を委譲

2. Fable 5をアドバイザーとして使い、安い実行モデルが「相談」する

3. Fable 5をベリファイア（検証者）**として使い、結果をチェックさせる

Lance氏がClaude自身にharnessを書かせる際に与えている指針：

1. タスクをまず分析
 ・判断がタスク全体に散らばる → 安いexecutor＋Fable 5 advisor
・判断が最初or最後に集中 → Fable 5をorchestrator/verifierに

2. 委譲の判断ルール

・判断と実行が切り離せない作業 → Fable 5単独でやる
・検証作業 → 強いモデル（Fable 5）を使う
・「このタスクは難しいから強いモデルに…」という自己判断はほぼランダム並みに当たらない → 構造的に固定チェックポイントなどでescalationする

3. 十分な作業量を移す
 初回実行後に「workerが実際に何%タスクをやっていたか」を確認（audit）する。

4. Plumbing（基盤実装）が全てを決める

・キャッシュの活用（読み込みは安い）
・Workerをpersistent（永続的）に保つ
・役割は「ツール」で明確に明示（プロンプトの文章だけでは曖昧）
・サイレントなモデルフォールバックやキャッシュ無効化に注意

「Fable 5は強いけど全部に使うのはもったいない。タスクの特性を見て、賢くSonnet 5と分担すれば、性能をほぼ維持したままコストを半分近くにできる」


--- 引用元 @RLanceMartin ---
https://t.co/5TDlA7reYa
