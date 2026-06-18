---
id: "2026-06-17-k-koga555-openclaw-hermes-openclawのbotをhermesに変換でき-01"
title: "@k_koga555: #OpenClaw #Hermes # OpenClawのbotをHermesに変換できるか こういうテーマで、Chat"
url: "https://x.com/k_koga555/status/2067218545650651348"
source: "x"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "LLM", "GPT", "x"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

#OpenClaw #Hermes
# OpenClawのbotをHermesに変換できるか
こういうテーマで、ChatGPTに相談してみた
最近、Hermesの話題やスキル実装の話など多くて、今まで育てたOpenClawを１体だけ変換してみようかというのが発端です
DEL, ADDなんて嫌じゃない

以下、結果はmdフォーマット
---------
# OpenClawのbotをHermesに変換できるか

## 結論

**OpenClawのbot 1体をHermesに「完全コピー」することは難しい**です。  
ただし、**会話履歴・人格設定・長期メモリ・スキル・運用ルールのかなりの部分は移植できます**。

OpenClawは、人格や記憶をMarkdownファイル中心に構成する設計が多く、`MEMORY.md` や日次メモリ、`SOUL.md` / `IDENTITY.md` 的な人格ファイルで振る舞いを作る構成が確認できます。  
一方、Hermesは「自己改善するエージェント」として、永続メモリ、スキル生成、セッション検索、ユーザーモデリングを重視する設計です。

---

## できる箇所

### 1. キャラクター設定・人格・口調

これはかなり移植しやすいです。

OpenClaw側に以下のようなファイルや設定がある場合、Hermes側の人格設定・初期プロンプト・エージェント説明・スキル説明に変換できます。

```text
SOUL.md
IDENTITY.md
PERSONA.md
AGENTS.md
system prompt
custom instructions
```

移せる内容は、例えば以下です。

| OpenClaw側 | Hermes側での移植先 |
|---|---|
| bot名 | agent name / persona |
| 口調 | system prompt / behavior rule |
| 一人称・キャラ性 | persona prompt |
| 禁止事項 | safety / instruction section |
| 得意分野 | skill description |
| ユーザーとの関係性 | user model / memory |
| 反応スタイル | communication skill |

つまり、**「このbotはどう話すか」「何を重視するか」「どんな性格か」は移せる**と考えてよいです。

---

### 2. 長期メモリ

OpenClawの `MEMORY.md` や `memory/YYYY-MM-DD.md` のような記録は、Hermesの永続メモリに変換できます。

移せるものは以下です。

| 内容 | 移植可否 |
|---|---|
| ユーザーの好み | 可能 |
| 過去のプロジェクト情報 | 可能 |
| よく使う手順 | 可能 |
| 継続中のタスク | 可能 |
| 注意点・禁止事項 | 可能 |
| 過去の失敗と改善策 | 可能 |
| 会話から得た事実 | 可能 |

ただし、**そのまま全部突っ込むのは非推奨**です。  
OpenClawの長期メモリをHermes向けに使うなら、次のように分類した方が安全です。

```text
1. 永続的なユーザー情報
2. botの人格・口調
3. プロジェクト別の記憶
4. よく使う作業手順
5. 注意すべき制約
6. 古い会話ログ・参照用アーカイブ
```

Hermesは「学習ループ」「スキル改善」を持つ設計なので、OpenClawの雑多なメモリをそのまま入れるより、**要約・構造化して渡す方が再現性が高い**です。

---

### 3. 会話履歴

会話履歴そのものも移せますが、扱いは2種類に分けるべきです。

| 形式 | Hermesでの使い方 |
|---|---|
| 全文ログ | 検索用アーカイブ |
| 要約ログ | 実用メモリ |
| 重要な発言 | 永続メモリ |
| 決定事項 | プロジェクトメモリ |
| キャラ形成に関わるやり取り | persona補助情報 |

「それまでの会話履歴をそのまま引き継ぐ」という意味が、**過去ログを参照できる状態にする**なら可能です。

しかし、**過去の全会話を常に人格や判断に反映させる**のは難しいです。  
LLMにはコンテキスト長の制限があり、Hermes側でも必要に応じて検索・要約・注入する形になるためです。

現実的には、以下の変換が最も安定します。

```text
過去ログ全文 → archive
重要事項 → MEMORY
人格に関わる発言 → PERSONA
作業手順
