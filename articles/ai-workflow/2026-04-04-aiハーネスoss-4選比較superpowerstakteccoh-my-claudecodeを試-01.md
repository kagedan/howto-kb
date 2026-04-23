---
id: "2026-04-04-aiハーネスoss-4選比較superpowerstakteccoh-my-claudecodeを試-01"
title: "AIハーネスOSS 4選比較：superpowers・TAKT・ECC・oh-my-claudecodeを試してTAKTを選んだ理由"
url: "https://zenn.dev/purple_matsu1/articles/20260402-takt-adoption"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

## はじめに

前回の記事では、AIエージェントを活用した開発ワークフローを「ハーネス」として設計する考え方（ハーネスエンジニアリング）を紹介し、6フェーズの要件定義を行いました。

要件のポイントは4つ。**厳格なワークフロー**（フェーズスキップ不可）、**サブエージェント活用**、**LLM非依存**、**人手なしの自動ループ**です。

この要件を持って4つのOSSを調査しました。この記事では、その比較とTAKT採用の経緯、実装したpieceを整理します。

---

## 比較した4つのOSS

### superpowers

スキル駆動の「プロセス強制型」ハーネスです。brainstorming → planning → subagent-driven-development の流れが明確で、`No production code without a failing test first` のような強い行動規範を前面に出しているのが特徴でした。

* **ワークフロー強制**: プロンプト内のテキストで「飛ばすな」と強く指示するソフトな強制
* **サブエージェント**: 実装をサブエージェントに委譲し、spec compliance と code quality の2段階レビューを組み込める
* **LLM対応**: Claude Code を中心に、Codex / OpenCode / Gemini / Cursor など各環境向けの導入手順が用意されている
* **良い点**: シンプルで導入コストが低い。brainstormingスキルの「1問ずつ質問→spec.md生成」は実用的
* **懸念**: ワークフロー強制がプロンプトやスキル規律への依存が大きい。強い誘導はあるが、制御の中心はあくまで指示文

### TAKT

YAML定義の状態マシン（PieceEngine）でワークフローを制御するマルチエージェントオーケストレーションです。音楽メタファーが設計に一貫して使われており、ワークフロー（Piece）をステップ（Movement）で構成します。

* **ワークフロー強制**: PieceEngineがルール評価で next を決定する。プロンプト依存より強く、YAMLの状態遷移でフェーズを制御できる
* **サブエージェント**: built-in piece でも parallel review や multi-stage review を表現できる
* **ループ制御**: review → fix のループを piece 側で宣言的に定義しやすい
* **LLM対応**: README上は Claude Code / Codex / OpenCode を主対象にしつつ、provider 抽象化で切り替えられる
* **良い点**: declarative な強制力、review/fix loop の書きやすさ、`takt eject` によるカスタマイズ
* **懸念**: TypeScriptで本格実装されている分、内部まで深くいじると保守コストはそれなりにある

プロンプト設計には**Faceted Prompting**を採用しており、Persona / Policy / Instruction / Knowledge / Output Contract の5つの関心事を分離して扱います。ここは他の3つと比べても、かなり設計思想が明文化されていると感じました。

### everything-claude-code（ECC）

多数の agents / skills / commands を備えた包括的ハーネスです。Anthropicハッカソン優勝を前面に出しており、マニフェスト駆動の選択的インストールや、ツール使用パターンを観察して instinct 化していく **continuous learning** 系の仕組みが特徴的でした。

* **ワークフロー強制**: ルール＋フック＋エージェント委譲（ミドルレベル）
* **LLM対応**: マニフェスト＋アダプタで5種対応
* **良い点**: 非常に包括的で、フック制御が柔軟
* **懸念**: 複雑度が非常に高く、導入コストが高い

### oh-my-claudecode（OMC）

イベント駆動のマルチエージェントオーケストレーションです。現行ドキュメントでは Team が canonical orchestration surface とされていて、`ralph` のような persistent mode や `UltraQA` のような QA loop と並んで、かなり多機能な構成です。

* **ワークフロー強制**: Team / persistent mode / hooks を組み合わせて、完了まで進める方向にかなり強く寄せている
* **特筆機能**: UltraQA（build→lint→test→fixを最大5サイクル）、deep-interview（ソクラテス式対話）
* **良い点**: 「完了まで止めない」思想がはっきりしている、Team や tmux workers で並列化の選択肢が多い
* **懸念**: 複雑度が高く、Claude Code依存度が高い

---

## 比較表

| 観点 | superpowers | TAKT | ECC | OMC |
| --- | --- | --- | --- | --- |
| ワークフロー強制 | テキスト（ソフト） | 状態マシン（ハード） | ルール+フック（ミドル） | 状態ファイル+Stopフック（ハード） |
| LLM非依存 | 複数環境向け導入あり | Provider抽象化 | マニフェスト+アダプタ | Claude主体+CLI連携 |
| サブエージェント | レビュー重視 | movement設計で表現 | 非常に多い | Team/tmux並列 |
| ループ制御 | なし（手動寄り） | review/fix loopを宣言しやすい | フックや運用で補う | UltraQA（5サイクル） |
| brainstorm | スキルあり | assistantモード | Researchフェーズ | deep-interview |
| 複雑度 | ★★☆ | ★★★ | ★★★★ | ★★★★ |
| 導入コスト | 低 | 中 | 高 | 高 |

---

## TAKTを選んだ5つの理由

### 1. コードレベルのワークフロー強制

superpowersのようなプロンプトテキストによる強制は、どうしてもLLMの従順さに依存する面があります。TAKTのPieceEngineはYAMLで状態遷移を定義し、ルール評価で next を決めるので、少なくとも「指示文だけで縛る」よりは強く制御できます。

### 2. LLM非依存が最も成熟している

Provider抽象化がはっきりしていて、piece の定義と provider の切り替えを分離しやすいのがよかったです。README上でも Claude / Codex / OpenCode を明確に対象にしていて、persona ごとの provider override まで用意されています。

### 3. cycle detectorが要件に直結

review↔fix のループを「テスト通過まで自動継続する」という要件に寄せやすいのが大きかったです。loop そのものを piece で宣言しやすく、閾値や監視を組み合わせることで無限ループも抑えやすい設計でした。

### 4. Faceted Prompting

Persona / Policy / Instruction / Knowledge / Output Contract を分離する設計は、他の3つと比べてもかなり明示的です。特に policy を独立させられるので、レビュー基準や禁止事項を workflow から切り離して再利用しやすいのがよかったです。

### 5. ejectによるカスタマイズ

`takt eject`でビルトインpieceをローカルにコピーし、最小限の変更で独自pieceを作れます。ゼロから書く必要がなく、保守コストを抑えつつカスタマイズできます。

ちなみに、TAKTにないbrainstormフェーズや2段階レビューも、他リポの設計を参照して補完できました。

* brainstormフェーズ: `interactive_mode: assistant`で対話的に要件を掘り下げ
* 2段階レビュー: faceted promptingで review 観点を分離して近い構成にできる
* 「完了まで止めない」: loop 定義と movement 制御を組み合わせて近い挙動を作れる

---

## 実際に作ったpiece

### my-frontend-design（デザイン実装）

デザインリファレンスからの実装に特化したpieceで、ビジュアル差分がゼロになるまで自動ループします。

```
assistant対話（要件ヒアリング）
  → plan（デザイン解析・コード調査・スタイルマッピング）
  → implement（Next.js + Tailwind + shadcn/ui 実装）
  → visual_verify ↔ visual_fix ループ（閾値5、judge介入）
  → reviewers（AI antipattern + supervisor 並列）
  → fix → visual_verify に戻る
  → COMPLETE
```

`visual_verify`でagent-browserのスクリーンショットとデザインリファレンスを比較し、差異がゼロになるまで自動ループするのがポイントです。

---

## 当初の要件定義はTAKTでどう実現されたか

| 当初の構想 | TAKTでの実現 |
| --- | --- |
| Brainstorm: 1問ずつ質問→spec.md生成 | `interactive_mode: assistant`（`/go`前の対話フェーズ） |
| Plan: 推論モデルでplan.md + todo.md生成 | `plan` movement（plannerペルソナ）→ plan.md出力 |
| Execute: サブエージェントで実装 | `implement` movement（coderペルソナ）+ parallel review / multi-stage review |
| Test: ビジュアルテスト含む | `visual_verify` ↔ `visual_fix` ループ |
| Review: 2段階コードレビュー | `reviewers` parallel movement（AI antipattern + supervisor） |
| Loop: テスト完了まで自動ループ | review/fix loop + monitors をYAMLで宣言 |

定義した要件がTAKTの既存機能とほぼ1対1で対応できました。正直、ここまでぴったりはまるとは思っていませんでした。

ハーネスを選ぶとき、「要件との合致度」を先に言語化しておくと、こういう比較がかなりしやすくなると思います。少なくとも自分にとっては、TAKTを選ぶ理由がかなり明確になりました。

---

## 参考
