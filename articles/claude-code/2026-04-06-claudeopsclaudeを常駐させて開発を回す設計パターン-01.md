---
id: "2026-04-06-claudeopsclaudeを常駐させて開発を回す設計パターン-01"
title: "ClaudeOps：Claudeを常駐させて開発を回す設計パターン"
url: "https://zenn.dev/okojoai_tech/articles/05d90e3c472fe2"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "zenn"]
date_published: "2026-04-06"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## はじめに

筆者はもともとソフトウェアエンジニア出身で、その後Deep Learning研究に移り、ここ1年ほどはLLMを使ったSaaSプロダクト開発に時間を費やし、零細法人の経営と子育てと研究をしています。

本当はDeep Learningの研究だけをやっていたい。でも現実的には、Claude Codeのようなツールなしには競争できないし、パラレルにやることが多く時短もしたい。

この葛藤から生まれたのが **ClaudeOps** という考え方です。

---

## ClaudeOpsとは何か

> **ClaudeOps**とは、Claudeをバックグラウンドで継続的に動かし、定常的な検知・トリアージ・アクション生成を自動化する実践のことです。判断はClaudeと人間が共有しますが、最終承認は常に人間が持ちます。

既存のOps概念との比較：

| Ops名 | 自動化の対象 |
| --- | --- |
| DevOps | ビルド・テスト・デプロイ |
| MLOps | モデルの学習・評価・サービング |
| LLMOps | プロンプト管理・モデル評価・推論コスト |
| **ClaudeOps** | **判断と情報処理のパイプライン** |

LLMOpsとの違いを補足すると、LLMOpsは「LLM自体をどう運用するか」の話です。ClaudeOpsは「LLMを使ってビジネス運用をどう自動化するか」の話。Claudeはインフラであり、ClaudeOpsはその上に構築される運用設計です。

---

## 3つのフェーズ

ClaudeOpsは以下の3フェーズで構成されます。

### 1. Scan（検知）

コード・データ・外部サービスを定期的にスキャンし、問題や変化を検出する。

### 2. Surface（整理・通知）

検出した内容を整理・分類し、人間が行動できる形で届ける。IssueのファイリングやSlackへのサマリー投稿、レポート生成など。

### 3. Act（実行）

Claudeの判断と人間の入力を組み合わせてアクションを実行する。PRの作成、レビューコメントの投稿、通知の送信など。

**Scan → Surface → Act** がコアループです。

---

## 設計の核心：Intentional Delegation（意図的な委譲）

ClaudeOpsで最も重要な概念が **Intentional Delegation** です。

「何をClaudeに任せ、何を人間が持つか」を設計の段階で明示的に決める。曖昧な自動化ではなく、Claudeの権限と人間の権限の境界線をはっきりさせる。

### 実際の分担例

**Claudeが決めること**

* 定期スキャンによるバグ検出
* Issueのファイリングと分類
* 修正が明確な場合のauto-fixラベル付け
* レビューコメントの生成

**人間が決めること**

* Claudeが確信を持てなかったIssueへのauto-fixラベル付け
* PRのマージ
* パイプライン自体の設計・調整

**ハイブリッド**

* 何を修正するかの判断：Claudeが確信のあるものにラベルを付け、残りは人間が補う

---

## 実装例：開発パイプラインの自動化

OkojoAIでは、**Claude CodeのScheduled Tasks**を使って以下のパイプラインを構築しています。

```
05:00  バグ検出        コードベース全体をスキャン → Linear Issueを起票
確信があればauto-fixラベルを自動付与
06:00  PR作成          auto-fixラベルのついたIssueのみ → PRを自動作成
07:00  コードレビュー  未レビューのPR全件 → レビューコメントを投稿
```

人間がやることは、**Claudeが確信を持てなかったIssueへのラベル付けだけ**。PRのマージは常に人間の判断です。

また、Sentryをポーリングトリガーとして使い、本番エラーを検知して自動でIssueを起票する仕組みも試験中です。

カスタムインフラもAPI開発も不要。Claude Codeのサブスクリプションだけで動いています。

---

## エンジニアリング以外への応用

Scan → Surface → Act のループはSaaS運用全般に使えます。

* **プロダクト分析**：PostHogのデータを定期取得してSlackにサマリーを投稿
* **カスタマーサクセス**：利用パターンからチャーンリスクを検出してCSチームに通知
* **サポート**：問い合わせを自動分類してルーティングを提案

構造は汎用的です。スタックに合わせて具体的な実装を変えるだけ。

---

## まとめ

ClaudeOpsはまだ生まれたばかりの概念で、現時点では最初の実装を試みた段階です。

「とりあえず自動化」ではなく、**人間とClaudeの境界線を設計の中心に置く**こと。それがClaudeOpsの本質です。

似たような取り組みをしている方、あるいは興味を持った方はぜひコメントやフィードバックをください。

---

英語版原典について

本記事のオリジナルは英語で書かれています。概念の詳細や英語コミュニティでのディスカッションはそちらもあわせてご参照ください。

**原典記事**：[ClaudeOps — A New Practice for Embedding Claude into Your Operations](https://dev.to/okojoalg/claudeops-a-new-practice-for-embedding-claude-into-your-operations-iak)
