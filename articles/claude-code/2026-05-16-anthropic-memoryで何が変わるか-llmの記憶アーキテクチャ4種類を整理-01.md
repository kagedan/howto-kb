---
id: "2026-05-16-anthropic-memoryで何が変わるか-llmの記憶アーキテクチャ4種類を整理-01"
title: "Anthropic Memoryで何が変わるか LLMの記憶アーキテクチャ4種類を整理"
url: "https://zenn.dev/kenimo49/articles/llm-memory-context-engineering-4-architectures"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "LLM"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

## 「前回の会話を覚えていない」を6ヶ月放置していた

Claude Codeを使い始めて、私が一番ストレスだったのは「前回の会話を覚えていない」ことでした。

毎朝、同じプロジェクトを再開するたびに、コンテキストを最初から積み直す必要があります。「私はエンジニア兼投資家で、合同会社を経営していて、〇〇プロジェクトを進めていて……」と。

CLAUDE.mdに書けば一部は解決しますが、 **動的に変わる情報** (「先週の決定事項」「今扱っている課題」)は、CLAUDE.mdに書くのが面倒です。

6ヶ月放置していました。

その間に、Anthropicが2026年3月2日に **Memory機能を全Claudeユーザーに公開** しました([Anthropic Memory Feature](https://www.macrumors.com/2026/03/02/anthropic-memory-import-tool/))。さらに3月3日には、ChatGPT、Gemini、Perplexity、Grok等から **Memoryをインポートする機能** もリリース。

「もう自分で記憶設計する必要ないのでは？」と一瞬思いましたが、調べていくと **そうではない** ことに気づきました。

Anthropic Memoryは「ChatGPT並みの基本機能」を提供しますが、 **エージェント設計者が踏み込むべき記憶アーキテクチャ** はその上にあります。本記事では、 **LLMの記憶アーキテクチャ4種類** と、Anthropic Memoryをどう使い分けるかを整理します。

## Anthropic Memoryが2026年3月にデフォルト機能になった

結論: **Anthropic Memoryは、Claudeが約24時間ごとに会話履歴をスキャンし、長期保存に値する事実を要約した記憶を作る機能** です。

具体的には、以下を自動で抽出します。

* 職業(ソフトウェアエンジニア、PMなど)
* よく使うツール(Python、Claude Code、Notion等)
* 繰り返し出るトピック(LLMO、context engineering等)
* 言語の好み(英語/日本語)

スマートな点は、 **元の会話ログを保持せず、要約だけを記憶する** こと。プライバシー保護とトークン節約の両方を達成しています。

無料ユーザーから利用可能で、ChatGPTからの乗り換えを促進する戦略的機能として位置づけられています。Memory Importでは ChatGPT/Gemini/Perplexity/Grok から長期コンテキスト、ライティングスタイル、プロジェクト知識、個人嗜好、口調ガイドラインを移行できます。

### Anthropic Memoryでカバーされること、されないこと

| カバーされる | カバーされない |
| --- | --- |
| 個人の職業・嗜好の長期記憶 | プロジェクト固有の最新状況 |
| 言語・トーンの好み | チーム内で共有する記憶 |
| 繰り返し出るトピック | 動的に変わる作業フォーカス |
| Importで他LLMから移行 | エージェント間の記憶共有 |

つまり、Anthropic Memoryは **「ユーザー個人の長期記憶」のレイヤー** を埋めるものです。

エージェント設計者が踏み込むべき **アプリケーション層の記憶** は、別途設計が必要です。

ここから、その「アプリケーション層の記憶」を4種類のアーキテクチャに分類します。

## メモリアーキテクチャ4種類: どれを選ぶか

### 4種類の比較表

| アーキテクチャ | 仕組み | 長所 | 短所 | 適用場面 |
| --- | --- | --- | --- | --- |
| **バッファ** | 直近N回の会話をそのまま保持 | シンプル、実装容易 | 古い情報が消失 | 短い対話セッション |
| **サマリー** | 古い会話をLLMで要約して保持 | 長期文脈を圧縮保持 | 要約時の情報損失 | 長時間の対話 |
| **エンティティ** | 人物・概念をプロファイルとして記録 | 構造化された知識 | 抽出精度に依存 | 顧客対応・CRM連携 |
| **知識グラフ** | エンティティ間の関係性も記録 | 最も豊富な記憶 | 実装・運用が複雑 | 複雑なドメイン知識管理 |

4種類は **複雑性とコストが上に行くほど高い** という階層関係にあります。

### 私の判断: サマリーメモリが最もコスパが高い

4種類の中で **最もコストパフォーマンスが高い** のはサマリーメモリだと考えています。

バッファメモリの「古い情報が消える」問題を解決しつつ、エンティティ/知識グラフメモリほどの実装複雑性がありません。

Pythonで書くと、こんな構造になります。

```
from collections import deque

class SummaryMemory:
    def __init__(self, llm, summary_interval=10):
        self.llm = llm
        self.summary_interval = summary_interval
        self.current_summary = ""
        self.recent_buffer = deque(maxlen=5)
        self.interaction_count = 0

    def add_interaction(self, user_input, assistant_response):
        self.recent_buffer.append({"user": user_input, "assistant": assistant_response})
        self.interaction_count += 1
        if self.interaction_count % self.summary_interval == 0:
            self._update_summary()

    def _update_summary(self):
        prompt = f"""
以下を簡潔に要約してください。重要な決定事項、継続中のタスク、
ユーザーの嗜好や背景情報を中心にまとめてください。

既存のサマリー: {self.current_summary}
最近の会話: {format_recent(self.recent_buffer)}
"""
        self.current_summary = self.llm.generate(prompt)
        keep = list(self.recent_buffer)[-2:]
        self.recent_buffer.clear()
        self.recent_buffer.extend(keep)

    def get_context_for_llm(self):
        parts = []
        if self.current_summary:
            parts.append(f"=== 会話サマリー ===\n{self.current_summary}")
        if self.recent_buffer:
            parts.append("=== 最近の会話 ===")
            parts.extend(format_interaction(i) for i in self.recent_buffer)
        return "\n".join(parts)
```

要約の更新間隔(`summary_interval`)を10回程度に設定すれば、トークン消費を抑えつつ長期文脈を保持できます。

### Anthropic Memory(個人) + サマリー(プロジェクト)の組合せが最強

ここで設計判断のヒントを共有します。

![Anthropic Memory + サマリー + バッファの3層メモリアーキテクチャ](https://static.zenn.studio/user-upload/deployed-images/b3a1f4f2e438e7c7bc2d2fb1.png?sha=c70e87dc01fb1d7a3758c934e3ea91a91fde526a)  
*個人記憶はAnthropic Memoryに任せ、プロジェクト記憶はサマリーで自前管理する3層構造*

**Anthropic Memoryは個人の長期記憶を、サマリーメモリはプロジェクト固有の動的記憶を担当する** 、という分業が私の中での最適解です。

具体的には以下です。

| レイヤー | 担当 | 例 |
| --- | --- | --- |
| User Layer | Anthropic Memory | 「私はソフトウェアエンジニア」「Pythonを使う」 |
| Project Layer | サマリーメモリ(自前) | 「現在Context Engineering本第9章執筆中」 |
| Session Layer | バッファメモリ | 直近5往復の会話 |

3層構造にすると、 **Claude Codeを開いた瞬間から、過去のコンテキストが復元される** 環境ができます。

## 7ファイル・アーキテクチャ: メイン/サブの記憶共有設計

実プロダクションのエージェントでは、もう一段踏み込んだ記憶設計が使われています。OpenClawという実装が **7つのファイルで人格と記憶を構成する** モデルを提示しています。

| ファイル | 役割 | メイン | サブエージェント |
| --- | --- | --- | --- |
| AGENTS.md | 全員共通の作業ルール | ✅ | ✅ |
| TOOLS.md | ツール一覧とローカル設定 | ✅ | ✅ |
| SOUL.md | 人格・性格・関係性 | ✅ | ❌ |
| IDENTITY.md | 対外的プロフィール | ✅ | ❌ |
| USER.md | ユーザーの情報 | ✅ | ❌ |
| HEARTBEAT.md | 定期チェック項目 | ✅ | ❌ |
| MEMORY.md | 過去の記憶(日次+長期) | ✅ | ❌ |

ポイントは、 **サブエージェントには記憶を渡さない** こと。

サブエージェントは「派遣社員」と考えると分かりやすいです。必要最小限の情報で特定タスクに集中させる。 **不要なコンテキストの削減(トークン節約)とプライバシー保護の両方を実現** します。

私は信長の野望で「兵糧を配分しすぎないこと」を学びました。すべての城に十分な兵糧を送ると、本城が枯渇します。記憶も同じで、配り方を間違えると本体が機能しなくなるのです。

## Context Window汚染の4つの障害モード

長期対話では、記憶の蓄積に伴って4種類の障害が発生します。

| 障害モード | 症状 | 対策 |
| --- | --- | --- |
| **Context Poisoning(汚染)** | 誤情報がコンテキストに混入し、以降の回答が歪む | 情報の交差検証 + 信頼度スコアリング + 未検証情報の隔離バッファ |
| **Context Distraction(散漫)** | 無関係な情報が多すぎて焦点がぼける | 関連性スコアリング(関連度0.5 + 新しさ0.3 + 重要度0.2)でフィルタ |
| **Context Confusion(混乱)** | 複数トピックが混在し、文脈を取り違える | トピック別クラスタリング + セクション分け + 一貫性チェック |
| **Context Clash(衝突)** | 矛盾する情報が共存し、回答が不安定になる | 矛盾検出 + 信頼性・新しさ・ソース権威性に基づく解決 |

これらの障害は長期対話ほど蓄積します。 **定期的なコンテキスト「棚卸し」** (古い情報の要約・矛盾の解消)が重要です。

私は週次でMEMORY.mdを手動で棚卸ししています。月曜の朝、Claude Codeを開いて「先週のMEMORY.mdを要約・整理して」と頼むだけです。これでContext Poisoningの発生率が顕著に減りました。

## トークン予算の動的配分

4種類のメモリシステムを統合するときの最後の論点が、 **トークン予算の動的配分** です。

```
# デフォルトの予算配分
budget_ratios = {
    "recent_buffer":         0.4,  # 40% - 最新の対話(常に最重要)
    "conversation_summary":  0.3,  # 30% - 過去の要約
    "relevant_entities":     0.2,  # 20% - 関連エンティティ
    "knowledge_graph":       0.1,  # 10% - 詳細な関係性(必要時のみ)
}

# 実際の配分は「関連性スコア × 優先度」で動的に調整
# 例: エンティティの関連性が高い質問では、エンティティ枠を拡大
```

設計のポイントは以下です。

* **最新の対話(バッファ)は関連性に関わらず常に高い予算を確保**
* **知識グラフは最もコストが高いため、明確に必要な場合のみ活用**
* **予算超過時はスケールファクターで全枠を均等に縮小**

Claudeの200K (1Mベータ)のコンテキストウィンドウは、現状でも十分大きいですが、 **動的配分の設計がないとすぐ埋まります** 。

## 「前回の会話を覚えていない」問題への即効薬

理論はここまで。実践的な即効薬を共有します。

長期タスクで「前の会話を覚えていない」問題が起きたら、 **System Promptに以下を追記するだけ** で目に見えて改善します。

```
## 継続中の会話コンテキスト
[前回までの重要な決定事項・進行状況を2-3行で要約]

## ユーザーの嗜好・背景
[ユーザーの特徴・好みを1-2行で記載]

## 現在の作業フォーカス
[今取り組んでいる主要タスクを1行で記載]
```

これを **MEMORY.md** という形でリポジトリのルートに置くと、Claude Code起動時に自動的に読み込まれます。

```
# MEMORY.md - AIエージェントの長期記憶

## ユーザープロファイル
- 職業: ソフトウェアエンジニア兼投資家
- 専門領域: Python, JavaScript, Context Engineering
- 作業スタイル: 段階的実装を好む、詳細な説明を求める傾向

## 継続中のプロジェクト
### Context Engineering本執筆
- 状況: 第2部(第5-9章)を執筆中
- 締切: 2026年3月末
- 前回の決定事項: 実験データを各章の背骨として使用

## 重要な決定事項(2026年2月)
- Context Engineering定義: 「モデルが話すときに何を見るか」の制御
- 実験メトリクス: Factual、Hallucination、Specificity、Honestyの4項目
- 執筆方針: ですます調、一人称「私」で統一

## メモリ更新ルール
- 重要な決定 → 即座に記録
- 嗜好の変化 → 3回以上同じパターンで更新
- プロジェクト状況 → 週1回以上更新
- 6ヶ月以上前の詳細 → 要約・削除
```

MEMORY.mdは、要するに **「自分の取扱説明書」** です。日次ログ(`memory/YYYY-MM-DD.md`)が「日記」なら、MEMORY.mdは「自己分析の総まとめ」。

## まとめ

* **Anthropic Memory** が2026年3月にデフォルト機能化。約24時間ごとに会話を要約して記憶
* Memory Importで ChatGPT/Gemini/Perplexity/Grokから記憶を移行可能
* アプリケーション層の記憶は **4種類(バッファ/サマリー/エンティティ/知識グラフ)** に分類できる
* **サマリーメモリ** がコスパ最強。Pythonで20-30行で書ける
* 推奨3層構造: User(Anthropic Memory) + Project(サマリー) + Session(バッファ)
* **7ファイル・アーキテクチャ** でメイン/サブエージェントの記憶を分離
* 4つのContext障害モード(Poisoning/Distraction/Confusion/Clash)を理解する
* トークン予算は **動的配分** で最適化
* 即効薬: **MEMORY.md** をリポジトリに置く

記憶設計は、 **AIエージェントを「賢いツール」から「信頼できるパートナー」に変える鍵** だと思っています。

「面白くいきましょう」と思える領域です。

!

本記事は、私が執筆した **Context Engineering** 第9章「State & Memory」の内容をベースにしています。Few-shot ExamplesからRAG、Full Context Engineering、MCP、Memory、Agentic RAGまでをカバーしたBookです。Zenn Book、Kindle JP/EN、kenimoto.dev LPで公開中です。

[Context Engineeringを読む(LP経由)](https://kenimoto.dev/ja/books/context-engineering?utm_source=zenn&utm_medium=article&utm_campaign=ce-memory)

## 関連記事
