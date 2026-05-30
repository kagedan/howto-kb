---
id: "2026-05-29-autonomyとcontrolのあいだ-graflowで記述するaiエージェント協調-01"
title: "AutonomyとControlのあいだ — Graflowで記述するAIエージェント協調"
url: "https://zenn.dev/myui/articles/c195b671ca9202"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "OpenAI", "cowork", "Python"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年5月15日に開催された[第5回 AIエージェントソフトウェア開発勉強会](https://aiagentsoftware.connpass.com/event/388586/)にて、私が開発しているOSSのAgentic Workflow Orchestration Engine **[Graflow](https://github.com/GraflowAI/graflow)** について登壇させていただきました。

本記事では登壇内容のうち、**特に共有したい2つの論点** — 「Autonomy と Control のあいだ」という設計空間と、「Harness Engineering の潮流の中での Graflow の立ち位置」 — に絞って紹介します。設計詳細・本番運用機能・コード例はスライド側に譲ります。

登壇スライドはこちらです:

## Autonomy と Control のあいだ

### 自律エージェントの急速な進化と、それでも残る課題

ここ最近、AIエージェントの世界は明らかに**自律性を高める方向**に急速に動いています。Claude Code、Cursor Agent、Devin、Claude Cowork……いずれも「人間が一手ずつ指示する」段階を脱して、長時間・複数ステップの作業を自律的にこなすところまで来ています。フロンティアモデルの性能向上と相まって、「自律エージェントで十分」という領域は今後も拡大し続けるでしょう。

その流れ自体に異論はありません。一方で、本番システムに載せる際には依然として以下のような課題が残ります:

1. **信頼性**: 何が起きたか・なぜ失敗したかを追える設計が必要
2. **再現性**: 検証・段階的改善のために挙動の安定性が欲しい場面がある
3. **レイテンシ・コスト・安全性**: 自律ループは予測困難で、適用領域には濃淡がある

例えば「東証上場企業で過去2年連続赤字の企業を漏れなくリストせよ」という同じプロンプトを2回投げると、参照ソースも結果件数も変わってきます。自律性を活かしたい場面と、決定的な挙動が欲しい場面は、ユースケース次第で使い分けが必要です。

### Autonomy Slider — 自律性は連続的なダイヤル

Andrej Karpathy 氏が示すように、自律性は二者択一ではなく**信頼とリスクに応じて調整するスライダー**として捉えるのが現実的です。

```
[Deterministic]──────[Agentic Workflow]──────[Fully Autonomous]
Airflow/Dagster      Controlled Autonomy       Claude Code / Cowork
従来ETL · RPA       (Graflowが狙う領域)       Devin / Cursor Agent
```

右側(Fully Autonomous)は今まさにモデル進化とエージェント基盤の充実で急速に拡大している領域です。左側(Deterministic)は伝統的に成熟しています。**その中間にも、自律性を部分的に取り込みながら全体は人間がデザインしたい、というニーズが一定数ある** — というのが私の見方です。

### Production Gap — 中間領域は流動的

中間領域をカバーする選択肢は、現時点ではまだ流動的です。

* **Workflow Engines (Airflow/Dagster/Prefect)**: 本番運用機能は充実しているが、エージェント推論ループの表現や動的なタスク生成は得意ではない
* **Agent Frameworks (LangGraph/AutoGen/CrewAI/Google ADK/PydanticAI/Mastra)**: ReActループの記述やLLM呼び出しの抽象化は得意。HITL や分散実行は各フレームワークごとに進化中

LangGraph も Google ADK も急速に進化しており、境界は流動的です。その上で、 **「人間が設計したワークフローの中に、自律性を限定的に組み込む」** というスタイルを Python ネイティブの書き心地で実現できる選択肢を、私自身が欲しかった。それが Graflow を作り始めた動機です。

## Graflow の設計上の核心

詳細はスライドに譲って、設計上の3つのコア判断だけ紹介します。

### ① Pythonic DSL — コードがそのままワークフロー図に見える

`>>` で逐次、`|` で並列。Diamond パターンも1行です。

```
fetch >> (transform_a | transform_b) >> store
```

同じことを LangGraph の `add_edge` で書くと5行必要になります。ノード数 × 依存数でエッジを書くため、グラフが大きくなるほど冗長化します。

### ② Define-by-run — 実行時に組み替え可能

LangGraph が **Define-and-compile**(TF1.x流)であるのに対し、Graflow は **Define-by-run**(PyTorch流)です。タスク数も依存関係も実行時に決まり、分岐は普通の `if` 文で書けます。

```
if r.score < 0.8:
    ctx.next_iteration()
elif r.has_error:
    ctx.next_task(handler, goto=True)
else:
    ctx.next_task(finalize)
```

routing DSL も END sentinel も conditional-edge registry も不要。`pdb` で普通にデバッグできるのが地味に効きます。

### ③ SuperAgent as Fat Node

「**ReActループはAgentの中、ワークフローはタスク依存だけを表現する**」という関心の分離。Agent 部分は ADK / PydanticAI / OpenAI Agents SDK など Best-of-Breed のフレームワークに委譲し、Graflow はワークフロー編成に集中します。

## Harness Engineering の潮流の中での Graflow

ここからが今回の登壇でもう一つ共有したかった論点です。

### Harness Engineering とは

最近、AIエージェント開発界隈で **Harness Engineering** という考え方が広まりつつあります。Harness とは「馬具・装具」の意味で、つまり **「モデルを取り囲む環境・記憶・道具・反復ループ」を工学的に整える**という発想です。

背景にあるのは、モデル単体の性能差が縮小傾向にあるという観測です。トップティアモデル間の差は確実に縮まっており、**差別化要因がモデル単体から、その周辺の設計品質にシフトしつつある**。

代表的な構成要素は次の4つ:

* **Skills**: ドメイン特化の手順書・知識をエージェントに動的装着
* **Context Engineering**: 関連情報の自動注入・トリミング・要約
* **Agent Memory**: 短期・長期・エピソード記憶
* **Ralph-loop**: 自己反復改善ループ(Critique → Revise の発展形)

Anthropic の Claude Skills 公開が大きな注目を集めましたが、これは単一プロダクトの話ではなく**業界全体のトレンド**として広がっています。

### ADK / PydanticAI も Skills / Memory をサポートしつつある

注目すべきは、**Agent Framework 側もこの流れに追従し始めている**ことです。

**Google ADK** は `google.adk.skills.load_skill_from_dir` でスキルディレクトリを動的ロードし、`SkillToolset` 経由でツールとして装着できるようになっています。Multi-agent や context-compression もネイティブサポートしています。

**PydanticAI** も `pydantic_ai_skills` パッケージの `SkillsCapability` でディレクトリベースのスキル読み込みに対応。type-safe な構造化出力と組み合わせて使えます。

Agent Memory についても、両フレームワークとも短期・セッションメモリのサポートを進めています。

つまり、**Skills や Memory は今後どの Agent Framework でも「あって当たり前」の機能になる**ということです。

### Graflow の立ち位置 — Best-of-Breed を束ねるレイヤーとして

Harness の構成要素がフレームワーク標準になっていく流れの中で、Graflow が提供したい価値はシンプルです: **個々の Agent Framework が進化させている機能を尊重しつつ、それらを横断的に組み合わせるためのワークフロー層を提供する**。

具体的なロードマップ:

1. **Skills Support**: ADK / PydanticAI のどちらの Agent からも同一の skill ディレクトリを参照可能に。`inject_llm_agent` 経由でワークフローからは透過的にアクセス
2. **Context Engineering**: 既存のチャネル機構を発展させ、関連情報の注入・トリミング・要約をサポート
3. **Agent Memory**: 短期/長期/エピソード記憶をチャネルと統合
4. **Ralph-loop**: 既に実装している Critique → Revise パターンの発展形を first-class にサポート

これは「Agent Framework 内蔵の機能では足りない」という主張ではありません。むしろ各フレームワークが個別に進化しているからこそ、**複数を組み合わせたいときの統合点**として Graflow を位置づけたい、ということです。ADK の multi-agent と PydanticAI の type-safe 出力を一つのワークフローで併用する、といった場面で役立つはずです。

加えて、Skill のバージョン管理・A/Bテスト・HITL を絡めた段階的ロールアウトなど、**ワークフロー全体としてのライフサイクル管理**が必要な領域では、ワークフロー層を持つメリットが出やすいと考えています。

> モデルではなく「モデルを取り囲む環境・記憶・道具・反復ループ」の品質で差がつく時代へ。

## まとめ

* 自律エージェントの急速な進化は確かなトレンドですが、自律性を**スライダー**として捉え、用途に応じてどの位置を選ぶかが現実的なアプローチだと考えています
* スライダーの中間領域 — 全体は人間が設計しつつ、個々のタスクで Agent が自律する「Controlled Autonomy」 — は、まだ選択肢が流動的な領域です
* Graflow はその中間領域を Python で素直に書ける選択肢の一つとして開発しています
* Harness Engineering の構成要素(Skills / Memory / Context / Ralph-loop)が各 Agent Framework の標準機能になっていく中で、Graflow は**複数を束ねるワークフロー層**として価値を出していきたいと考えています

設計詳細・コード例・本番運用機能・マルチエージェント構築事例については、ぜひスライドをご覧ください。

## おわりに

Graflow は Apache-2.0 の OSS として GitHub で開発しています。Issue / PR / Feedback をお待ちしています。

勉強会の主催者・参加者の皆様、貴重な議論の場をありがとうございました。
