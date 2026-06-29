---
id: "2026-06-29-ragは記憶ではない-hermes-agentのための記銘想起忘却設計-01"
title: "RAGは記憶ではない — Hermes-agentのための記銘・想起・忘却設計"
url: "https://zenn.dev/zapabob/articles/rag-is-not-memory-hermes-agent"
source: "zenn"
category: "claude-code"
tags: ["AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

## はじめに：RAGで検索できても、記憶したことにはならない

RAGは便利です。

ドキュメントをchunkに分け、embeddingを作り、質問に近いchunkを検索し、LLMのcontextに渡す。  
この仕組みによって、LLMはモデル内部に持っていない知識や、あとから追加された情報を使って答えられるようになります。

しかし、AIエージェントを長く動かしていると、すぐに分かることがあります。

**RAGで検索できることと、エージェントが記憶していることは違います。**

RAGは、外部知識を引くための技術です。  
一方で、記憶はライフサイクルです。

* 何を残すか
* どの形式で残すか
* どのくらい信頼するか
* いつ取り出すか
* いつ弱めるか
* いつ忘れるか
* 矛盾したとき、どちらを優先するか

Hermes-agentのような長期稼働するAIエージェントには、単なる検索ではなく、**記銘・想起・忘却を含む記憶設計**が必要になります。

この記事では、まずRAGの数的基盤を軽く整理し、その限界を見ます。  
そのうえで、エビングハウス型の忘却曲線を参考にしながら、LLM WikiとObsidian Vaultを使ったエージェント記憶の外部化について考えます。

> RAGの元論文（Lewis et al., 2020）は、事前学習モデルのパラメトリックメモリと、dense vector indexとして持つ非パラメトリックメモリを組み合わせる生成モデルとしてRAGを定義しています。つまりRAGは最初から「モデルの中の知識」と「外部検索可能な知識」を組み合わせる発想でした。ただし、それは「人生経験を蓄積するエージェント記憶」と同じものではありません。

---

## RAGの数的基盤

RAGの基本は、かなり素直です。

文書集合を次のように置きます。

D = \{d\_1, d\_2, ..., d\_n\}

実際には文書をそのまま扱うのではなく、chunkに分けます。

C = \{c\_1, c\_2, ..., c\_m\}

質問を q とします。embedding関数を f とすると、質問とchunkはベクトルになります。

v\_q = f(q), \quad v\_i = f(c\_i)

検索では、質問ベクトルとchunkベクトルの近さを測ります。典型的にはcosine similarityを使います。

s(q, c\_i) = \frac{v\_q \cdot v\_i}{\|v\_q\| \|v\_i\|}

そして、スコアが高いものから上位k件を取り出します。

R\_k(q) = \operatorname{TopK}\_{c\_i \in C}\ s(q, c\_i)

最後に、LLMは質問 q と検索結果 R\_k(q) をcontextとして受け取り、回答 y を生成します。

この仕組みは強力です。  
ただし、この数式を見ると、RAGの限界も見えてきます。

RAGが直接見ているのは、多くの場合「**質問とchunkの近さ**」です。  
けれども、質問に答えるために必要なのは、近いchunkではなく、十分な文脈です。

---

## RAGの限界

RAGの限界は、単に検索精度が低いという話ではありません。  
より本質的には、RAGは「**記憶の全工程**」を持っていないことにあります。

### 類似度は十分性ではない

cosine similarityが高いchunkは、質問に似ているchunkです。  
しかし、似ていることと、答えるのに十分であることは違います。

Google Researchの研究では、contextがrelevantかどうかだけでは足りず、LLMが答えるために必要な情報を含んでいるか（**sufficient context**）かどうかを見るべきだと述べています。

これは実装上かなり重要です。

RAGで上位に来たchunkが、質問に関連していることはあります。  
けれども、答えの決定に必要な条件、例外、日付、比較対象、反証が抜けていることがあります。  
この場合、LLMは「それっぽい文脈」を受け取っているのに、答えに必要な材料は持っていません。  
これは幻覚の温床になります。

### chunkは文脈を切断する

RAGでは、長い文書を扱うためにchunkingをします。

ただし、chunkは便利な一方で、文脈を切ります。  
設計判断、議論の経緯、反対意見、後日の修正、古い仕様の破棄などは、単一chunkにきれいに収まらないことが多いです。

そのため、検索では関連chunkが取れていても、判断に必要な背景が落ちることがあります。

### top-kは落ちた記憶を存在しないことにする

RAGはtop-kで文脈を選びます。

これは効率のために必要ですが、上位k件に入らなかった情報は、そのターンのLLMから見れば**存在しないのと同じ**です。

* 重要な反証が11位にある
* 古いが必要な設計判断が20位にある
* 関連語が違うために検索にかからない

こうした状況では、RAGは「保存されているのに想起できない」状態を作ります。

### context windowは無限ではない

retrievalで取ってきた情報は、最終的にcontext windowへ入ります。

そのため、検索結果が多すぎると、圧縮・再ランキング・切り捨てが必要になります。  
近年のRAG研究でも、context windowの制約やノイズのある検索結果に対して、context compressionやutility filteringのような後処理が扱われています。

検索できることと、生成時に使えることは違います。

### RAGには記銘判断がない

RAGは、多くの場合、すでにある文書から検索します。

しかし、エージェントには「**いま起きた出来事を記憶として残すか**」という判断が必要です。

* ユーザーが好む設計方針
* 過去に失敗したコマンド
* 採用しなかった実装案
* 一度だけ起きたが重要な障害
* 会話中に決まった命名規則
* 次回以降も守るべき制約

これらは、ただ検索対象を増やせばよいという話ではありません。  
記憶として記銘するか、ログに留めるか、AGENTS.mdに昇格するか、破棄するかを決める必要があります。

### RAGには忘却がない

RAGのvector storeは、基本的には足していく仕組みです。

もちろん削除や再indexはできます。  
けれども、記憶の強さ・古さ・使用頻度・信頼度・矛盾・重要度をもとに自然に弱める仕組みは、RAGそのものには含まれていません。

その結果、**古い仕様・破棄された方針・修正前の調査メモ**が、いつまでも同じ顔で検索に出てくることがあります。

これは、長期稼働するAIエージェントではかなり危険です。

> 古い記憶は、ないより悪いことがあります。  
> 自信ありげに古い記憶を想起するエージェントは、単に忘れっぽいエージェントより扱いにくいです。

---

## AIエージェントに必要な記憶

エージェント記憶の研究でも、単純な短期記憶・長期記憶だけでは分類が粗いという見方が出ています。2025年のサーベイでは、agent memoryをRAGやcontext engineeringと区別し、forms・functions・dynamicsの観点から整理されています。機能面では、factual memory・experiential memory・working memoryのような分け方が提示されています。

Hermes-agentに引き寄せるなら、最低限ほしい記憶は次の4種類です。

| 種類 | 役割 | 置き場所 |
| --- | --- | --- |
| working memory | 現在のタスク、直近の会話、実行中の方針 | context / session note |
| episodic memory | いつ何が起きたか、どんな判断をしたか | `_memory/episodes/` |
| semantic memory | 概念、設計、仕様、関係性 | `wiki/` |
| procedural memory | 作業手順、禁止事項、SOP | `AGENTS.md` / `_sop/` |

RAGは、このうちsemantic memoryやepisodic memoryを想起するための部品として使えます。  
けれども、記憶全体の設計としては足りません。

必要なのは、次の流れです。

```
出来事
  ↓
記銘するか判断する
  ↓
記憶ノートとして保存する
  ↓
index / link / embedding / graph を更新する
  ↓
必要なときに想起する
  ↓
使われた記憶を強化する
  ↓
使われない記憶を弱める
  ↓
古い記憶を圧縮・昇格・忘却する
```

ここまで含めて、ようやくエージェントの記憶になります。

> Generative Agentsの研究（Park et al., 2023）では、エージェントの経験を自然言語で完全に記録し、それを高次のreflectionへ統合し、必要に応じて動的に取り出して計画に使うアーキテクチャが示されています。観察・計画・reflectionが行動のもっともらしさに重要だった、という点もHermes-agentの記憶設計と相性がよいです。

---

## Hermes-agentに必要なエビングハウス型記憶

エビングハウスの忘却曲線は、人間の記憶が時間とともに弱まることを示す古典的なモデルです。2015年の再現研究では、20分から31日までの間隔で忘却曲線の再現実験が行われ、古典的な結果に近い傾向が報告されています。

もちろん、AIエージェントに人間の記憶をそのまま移植するわけではありません。  
ここで使いたいのは、人間の脳の完全な模倣ではなく、**記憶を時間で減衰させ、想起によって強化するという運用モデル**です。

たとえば、各記憶 m\_i に次の値を持たせます。

* `created_at`
* `last_recalled_at`
* `recall_count`
* `importance`
* `confidence`
* `stability`
* `source`
* `status`

記憶の残りやすさを、単純化して次のように置きます。

R\_i(t) = \exp\!\left(-\frac{t - last\\_recalled\_i}{S\_i}\right)

ここで、R\_i(t) は時刻 t における想起しやすさ、S\_i は記憶の安定度です。

記憶が使われたら、安定度を上げます。

S\_i \leftarrow S\_i \cdot (1 + \alpha \cdot quality\_i) + \beta \cdot importance\_i

逆に、長いあいだ使われず、重要度も低く、信頼度も低い記憶は、検索順位を下げるか、archiveへ移します。

このとき重要なのは、**忘却を削除と同一視しないこと**です。

AIエージェントにおける忘却は、多くの場合、物理削除ではなく次の操作です。

* 検索順位を下げる
* 要約へ圧縮する
* 古い記憶として印をつける
* 新しい記憶にsupersededさせる
* archiveへ移す
* 標準の想起対象から外す

Hermes-agentに必要なのは、何でも覚えることではありません。  
必要なときに思い出し、不要になった記憶を弱め、矛盾した記憶を整理することです。

---

## LLM WikiとObsidian Vault

ここで使いやすいのが、**LLM Wiki**という考え方です。

Andrej Karpathy氏のLLM Wikiメモでは、通常のRAGが「質問のたびにraw documentから関連chunkを探して答える」のに対し、LLMが継続的にMarkdownのwikiを構築・更新していく発想が述べられています。raw sources・wiki・schemaの3層に分け、sourceは不変、wikiはLLMが維持し、schemaがLLMの作業規約になる、という構成です。

この発想は、Hermes-agentの記憶外部化にとても合います。

**Obsidian Vaultを使うと、記憶は単なるvector storeではなく、Markdownとして読める形で残ります。**

* 人間が読める
* LLMも読める
* gitで差分を追える
* リンクで関係を張れる
* frontmatterで機械処理できる
* graph viewで構造を見られる

この性質が、エージェント記憶にはかなり重要です。

Hermes-agentでは、Obsidian Vaultを次のように分けます。

```
HermesVault/
├── AGENTS.md
├── _schema/
│   ├── memory-note.md
│   ├── episode-note.md
│   ├── concept-note.md
│   └── forgetting-policy.md
├── raw/
│   ├── papers/
│   ├── chats/
│   ├── logs/
│   └── sources/
├── wiki/
│   ├── concepts/
│   ├── agents/
│   ├── projects/
│   └── decisions/
├── _memory/
│   ├── episodes/
│   ├── learned/
│   ├── recalls/
│   └── archive/
├── _indexes/
│   ├── index.md
│   ├── graph.json
│   ├── embeddings.parquet
│   └── stale_report.md
└── _logs/
    ├── ingest.log.md
    ├── recall.log.md
    └── maintenance.log.md
```

ポイントは、**Markdownを正本にすること**です。

embedding・graph・SQLite・FTS indexは便利ですが、それらは派生物にします。  
正本は、人間が読めるMarkdownに置きます。  
そうしておくと、記憶の編集・レビュー・差分確認・巻き戻しがしやすくなります。

---

## 記銘：Memory Noteの形式

Hermes-agentが何かを記憶するときは、ただログを残すだけではなく、記憶ノートとして保存します。

たとえば、次のようなfrontmatterを持たせます。

```
---
id: mem-2026-06-29-001
type: episode
title: "Codex本ではAGENTS.mdとSandboxを厚くする"
created_at: 2026-06-29T10:30:00+09:00
last_recalled_at: 2026-06-29T10:30:00+09:00
recall_count: 0
importance: 0.82
confidence: 0.74
stability: 1.0
status: active
source: chat
links:
  - "[[AGENTS.md設計]]"
  - "[[Codex実践設計入門]]"
supersedes: []
superseded_by: []
tags:
  - hermes-memory
  - codex-book
  - agents-md
---
```

本文には、次の3つを書きます。

```
## What happened

Codex本の中心章として、AGENTS.mdとSandboxを厚くする方針を確認した。

## Why it matters

Codexを単なるCLI操作本ではなく、AI開発エージェント基盤の設計本として立てるため。

## Recall cues

- Codex本の章構成を考えるとき
- AGENTS.mdテンプレートを作るとき
- Sandbox / Approval章を書くとき
```

ここで大事なのは、記憶を「あとで検索できる文」にすることです。  
エージェントにとって良い記憶は、長文ログそのものではありません。  
**あとで想起しやすいcueを持ち、出典があり、関係先があり、必要なら古くできる単位**です。

---

## 想起：検索スコアを記憶スコアへ拡張する

通常のRAGでは、質問とchunkの類似度を中心に検索します。

Hermes-agentでは、これを記憶用に拡張します。

Score(m\_i, q, t) =
\alpha \cdot Rel(m\_i, q)
+ \beta \cdot Importance(m\_i)
+ \gamma \cdot Freshness(m\_i, t)
+ \delta \cdot Confidence(m\_i)
+ \epsilon \cdot LinkScore(m\_i)
- \lambda \cdot ConflictRisk(m\_i)

それぞれの意味は次の通りです。

| 項 | 意味 |
| --- | --- |
| `Rel` | queryとの意味的関連度 |
| `Importance` | 記憶自体の重要度 |
| `Freshness` | 古さ、または最終想起からの近さ |
| `Confidence` | 出典や検証状態にもとづく信頼度 |
| `LinkScore` | Obsidian上の被リンク、関連ノート数 |
| `ConflictRisk` | 矛盾、古い仕様、supersededの可能性 |

通常のRAGが `Rel` に強く依存するのに対して、エージェント記憶では、重要度・信頼度・鮮度・関係性・矛盾リスクを加えます。

**この差が、RAGと記憶の違いです。**

RAGは近いものを探します。  
記憶システムは、いま思い出すべきものを選びます。

---

## 忘却：消すのではなく、弱める

Hermes-agentでは、定期的に忘却ジョブを走らせます。

目的は、記憶を消すことではありません。  
古い記憶・弱い記憶・矛盾した記憶を、そのまま権威ある文脈として出さないことです。

```
from dataclasses import dataclass, field
from datetime import datetime
from math import exp
from pathlib import Path

@dataclass
class MemoryMeta:
    path: Path
    created_at: datetime
    last_recalled_at: datetime
    recall_count: int
    importance: float
    confidence: float
    stability: float
    status: str
    superseded_by: list[str] = field(default_factory=list)

def retention(meta: MemoryMeta, now: datetime) -> float:
    """Ebbinghaus型の想起しやすさを返す"""
    elapsed_days = (now - meta.last_recalled_at).total_seconds() / 86400.0
    stability = max(meta.stability, 0.1)
    return exp(-elapsed_days / stability)

def should_archive(meta: MemoryMeta, now: datetime) -> bool:
    if meta.status != "active":
        return False
    if meta.superseded_by:
        return True
    r = retention(meta, now)
    return (
        r < 0.15
        and meta.importance < 0.40
        and meta.confidence < 0.60
        and meta.recall_count <= 1
    )

def next_action(meta: MemoryMeta, now: datetime) -> str:
    if meta.superseded_by:
        return "mark_superseded"
    r = retention(meta, now)
    if should_archive(meta, now):
        return "archive"
    if r < 0.30 and meta.importance >= 0.70:
        return "summarize_and_link"
    if r < 0.30:
        return "deprioritize"
    return "keep"
```

この処理では、重要な記憶を雑に消しません。

* 重要だが古い記憶は、要約してリンクを残す
* 矛盾した記憶は、`superseded`として明示する
* 低重要度で使われていない記憶は、標準検索から外す

**忘却とは、記憶の破棄ではなく、想起順位の制御です。**

---

## おわりに：RAGの次は、記憶アーキテクチャである

RAGは重要です。

外部知識を検索し、LLMに渡し、根拠のある回答を作るために、RAGは今後も使われ続けます。

しかし、Hermes-agentのような長期稼働するAIエージェントでは、RAGだけでは足りません。

**RAGは、記憶のうち「想起」の一部です。**

エージェントには、

* 何を記憶するかを決める**記銘**が必要です
* 記憶をどの形式で保つかという**保持**が必要です
* 必要な記憶を取り出す**想起**が必要です
* 古い記憶を弱め、矛盾を整理する**忘却**が必要です

Obsidian Vaultは、この外部記憶を作るうえで扱いやすい基盤です。

* Markdownとして読める
* gitで履歴を追える
* リンクで関係を張れる
* frontmatterで機械処理できる
* 人間もLLMも同じ記憶を見られる

LLM Wikiの考え方を応用すれば、Hermes-agentは毎回ゼロからRAG検索するだけのエージェントではなく、**記憶を育て、整理し、必要なときに思い出すエージェント**になります。

RAGは、知識を探す技術です。

これから必要になるのは、AIエージェントが何を覚え、何を忘れ、何を次の行動に使うかを設計することです。

---

## 次の記事候補

この記事はシリーズの柱として機能します。続編候補：

* Obsidian VaultでHermes-agentのMemory Noteを実装する
* RAGとLLM Wikiの違いを実装で比較する
* エージェント記憶の忘却ジョブをPythonで書く
* AGENTS.mdとObsidian Vaultを接続して、記憶のSOPを作る
