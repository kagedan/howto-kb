---
id: "2026-07-06-mastra-announce-エージェント定義がファイルベースに規約による構造化でコードを書かずに-01"
title: "[Mastra Announce] エージェント定義がファイルベースに——規約による構造化でコードを書かずに AI エージェントを組み立てる"
url: "https://zenn.dev/shiromizuj/articles/945e1e9d275c7d"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "OpenAI", "GPT", "TypeScript", "zenn"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

---

2026年7月4日、Mastra は **ファイルベースエージェント（File-based Agents）** を発表しました。エージェントの構成要素——モデル設定・インストラクション・ツール・スキル・メモリ・ワークスペース・サブエージェント——をフォルダー内のファイルとして分割して管理できる新機能です。既存のコード登録型エージェントとの完全な後方互換性を保ちつつ、初めて Mastra を触る人でも迷わずエージェントを作れる「規約（Convention）」を提供します。

---

## これまで何が課題だったのか

### コードにすべてが混在していた

従来の Mastra では、エージェントは `new Agent({...})` でインスタンスを生成してコードに登録するスタイルでした。

```
// 従来のコード登録型エージェント
import { Agent } from '@mastra/core/agent'

export const weatherAgent = new Agent({
  id: 'weather',
  name: 'weather',
  // インストラクションが長くなると可読性が落ちる
  instructions: `
    あなたは天気アシスタントです。
    現在の気象状況を正確に伝え、
    天気予報に合わせたアクティビティを提案してください。
    ...（数百行になることもある）
  `,
  model: 'openai/gpt-5.5',
  tools: { getWeather, getForecast, getAlerts },
  memory: new Memory(),
  // ツールが増えるほどこのオブジェクトが肥大化する
})
```

この手法には以下の問題がありました。

**1. 関心の混在（Mixing Concerns）**  
インストラクション（何をするか）とモデル設定（どう動くか）とツール定義（どんな手段を持つか）が 1 つのオブジェクトに詰め込まれていました。  
インストラクションが数百行になると、コードとしての可読性が著しく低下します。

**2. エントリーポイントの肥大化**  
ツールやサブエージェントが増えるほど、`index.ts` や `agents/index.ts` が膨れ上がり、どのエージェントが何を持っているかを把握するのが難しくなっていました。

**3. 新規参入コストの高さ**  
「とりあえず動く最小構成」を作るためにも、TypeScript の書き方・`Agent` クラスの API・ツールの登録方法などを一通り覚える必要がありました。  
`instructions.md` をただ置けば動く、という手軽さはありませんでした。

---

## ファイルベースエージェントで何が変わるか

### 「規約（Convention）」がファイル構造になる

ファイルベースエージェントは **「1 エージェント = 1 フォルダー」** という規約を導入します。  
Mastra の CLI（`mastra dev` / `mastra build`）がフォルダー構造を自動スキャンして、エージェントを自動登録します。

```
src/mastra/agents/
└── weather/                    # エージェント名 = フォルダー名
    ├── config.ts               # モデル設定
    ├── instructions.md         # インストラクション（Markdown で書ける）
    ├── memory.ts               # メモリ設定
    ├── workspace.ts            # ワークスペース設定
    ├── tools/
    │   ├── get-weather.ts      # ツール（ファイル名がツールキーになる）
    │   └── get-forecast.ts
    ├── skills/
    │   ├── forecasting.md      # シンプルなスキル（Markdown）
    │   ├── temperature-units.ts  # コードで定義するスキル
    │   └── severe-weather/     # 参照ファイル付きのパッケージスキル
    │       ├── SKILL.md
    │       └── references/
    │           └── thresholds.md
    └── subagents/
        └── activity-planner/   # サブエージェント（同じ構造を再帰的に持てる）
            ├── config.ts
            └── instructions.md
```

### インストラクションが Markdown になる

最も実感しやすい変化は、**インストラクションを `.md` ファイルに分離できること** です。

```
<!-- instructions.md: Markdown で自由に書けるため、長文でも読みやすい -->

# 天気アシスタント

あなたは天気情報を提供する専門家です。

## 基本方針
- 現在の気象状況を正確かつ簡潔に伝えます
- 気温は摂氏と華氏の両方で報告します
- 危険な気象条件（嵐・洪水など）は最優先で警告します

## アクティビティ提案
天気予報に基づいて、ユーザーに適したアクティビティを提案します。
雨天時は室内活動、晴天時は屋外活動を優先してください。
```

TypeScript のテンプレートリテラルに長文を書き続ける必要はなくなりました。

### `config.ts` はシンプルなモデル設定だけ

```
// config.ts: モデル設定に集中できる
import { agentConfig } from '@mastra/core/agent'

export default agentConfig({
  model: 'openai/gpt-5.5',
  // instructions は instructions.md から自動で読み込まれる
  // tools は tools/*.ts から自動で収集される
})
```

`agentConfig()` ヘルパーは、ファイルから補完される残りの設定を考慮した型付けを提供します。

### 最小構成は 2 ファイルだけ

```
// src/mastra/index.ts: 空の Mastra インスタンスだけ置けばよい
import { Mastra } from '@mastra/core/mastra'
export const mastra = new Mastra({})
```

```
// src/mastra/agents/weather/config.ts
import { agentConfig } from '@mastra/core/agent'
export default agentConfig({ model: 'openai/gpt-5.5' })
```

```
<!-- src/mastra/agents/weather/instructions.md -->
あなたは天気アシスタントです。
```

`mastra dev` を起動するだけで、`weather` エージェントが自動登録されます。

---

## スキル（Skills）の仕組みを理解する

スキルは [Agent Skills 仕様](https://agentskills.io) に準拠した、**エージェントに特定のタスクのやり方を教える再利用可能なインストラクション**です。  
ファイルベースエージェントでは、`skills/` フォルダーに置くだけで自動的にエージェントへ付与されます。

#### 3 つのスキル定義スタイル

**① シンプルな Markdown ファイル**

```
<!-- skills/forecasting.md: ファイル名がスキル名になる -->
複数日の天気予報をまとめるときは、1 日ごとに整理して降水確率を強調してください。
```

**② コードで定義（`createSkill()`）**

```
// skills/temperature-units.ts
import { createSkill } from '@mastra/core/skills'

export default createSkill({
  name: 'temperature-units',
  description: '気温の単位変換に関するルールを適用する',
  instructions: '気温は常に摂氏（°C）と華氏（°F）の両方で報告してください。',
})
```

**③ 参照ファイル付きパッケージスキル**

```
<!-- skills/severe-weather/SKILL.md -->
---
name: severe-weather
description: 嵐・洪水などの危険な気象状況に対応するときに使用する
---

アクティブな警報から先に伝え、安全のためのアドバイスを続けます。
詳細な閾値については references/thresholds.md を参照してください。
```

参照ファイルはビルド時にバンドルに組み込まれるため、デプロイ後にファイルシステムを読みに行く必要はありません。

---

## サブエージェントと委任

ファイルベースエージェントは **サブエージェント** の宣言もフォルダー構造で表現できます。  
親エージェントの `subagents/` 以下に子エージェントのフォルダーを置くと、Mastra がそれをデリゲーションツールとして自動配線します。

```
src/mastra/agents/
└── supervisor/
    ├── config.ts
    ├── instructions.md
    └── subagents/
        └── researcher/
            ├── config.ts          # description が必須（モデルが委任判断に使う）
            └── instructions.md
            └── tools/
                └── search.ts
```

```
// subagents/researcher/config.ts
// description がないとビルドエラーになる（モデルが委任判断に使うため）
import { agentConfig } from '@mastra/core/agent'

export default agentConfig({
  model: 'openai/gpt-5.5',
  description: 'トピックを調査して引用付きの結果を返す。',
})
```

サブエージェントは親から完全に独立しており、自前のツール・スキル・ワークスペースを持ちます。  
最大 3 レベルのネストが可能です。

---

## コード登録型との共存と優先順位

ファイルベースエージェントは既存のコード登録型エージェントを**置き換えるものではなく、補完するもの**です。  
両者を同じプロジェクトで混在させることができます。

```
// src/mastra/index.ts
// コード登録型とファイルベースの共存例
import { Mastra } from '@mastra/core'
import { Agent } from '@mastra/core/agent'

// コードで登録されたエージェント（動的設定が必要なケースに向いている）
const supportAgent = new Agent({
  id: 'support',
  name: 'support',
  instructions: 'あなたはサポートエージェントです。',
  model: 'openai/gpt-5.5',
})

// ファイルベースの weather エージェントは CLI が自動登録する
export const mastra = new Mastra({
  agents: { support: supportAgent },
})
```

名前が衝突した場合は**コード登録が優先**され、警告がログに出力されます。

| 設定項目 | 優先順位 |
| --- | --- |
| `instructions` | 動的関数 > `instructions.md` > 静的文字列 |
| `model` | 未指定はビルドエラー |
| `tools` | `config.tools` > `tools/*.ts`（衝突時は config が優先） |
| `skills` | `config.skills` > `skills/`（衝突時は config が優先） |
| `memory` | `config.memory` > `memory.ts` |
| `workspace` | `config.workspace` > `workspace.ts` > デフォルト |
| `subagents` | `config.agents` > `subagents/`（衝突時は config が優先） |

---

## 既存手法・関連規格との位置づけ

### Convention over Configuration（設定より規約）の再発見

「規約より設定」という思想は Ruby on Rails が広めたものですが、ファイルベースエージェントもこの哲学を採用しています。  
Next.js がページを `pages/` や `app/` ディレクトリのファイル構造から自動生成するように、Mastra はエージェントを `agents/` ディレクトリから自動組み立てします。

### Agent Skills 仕様（agentskills.io）

Mastra のスキルシステムは [Agent Skills 仕様](https://agentskills.io) に準拠しています。  
これはエージェントがスキルを発見・読み込み・参照するための標準的なフォーマットを定義したものです。  
`SKILL.md` のフロントマター形式やスキルのディレクトリ構造は、この仕様に基づいています。

### Mastra CLI との統合

ファイルベースエージェントは `mastra dev` / `mastra build` の**バンドラー**フェーズで発見されます。  
Mastra インスタンスを直接インポートして使う場合（ライブラリとして利用する場合）は、ファイルスキャンは行われません。  
その場合は従来通りコードで登録する必要があります。

---

## まとめ

|  | コード登録型 | ファイルベース |
| --- | --- | --- |
| 定義場所 | TypeScript コード | フォルダー構造 |
| インストラクション | 文字列またはテンプレートリテラル | `instructions.md` |
| 自動登録 | 手動で `new Mastra({ agents })` | CLI が自動スキャン |
| 動的設定 | ◎ | △（`config.ts` の関数では可） |
| 初心者の始めやすさ | △ | ◎ |
| 大規模プロジェクト | ◎（柔軟性が高い） | ◎（構造が整理される） |

ファイルベースエージェントは「どこに何を書くか」の答えをフォルダー構造として提示することで、エージェント開発の**認知的負荷を下げる**アプローチです。  
複雑な動的登録が必要な場面ではコード登録型を、構造化された管理や素早いプロトタイピングにはファイルベースを使い分けることが推奨されます。

現時点では **beta** のため、API が安定する前にマイナーバージョンで破壊的変更が入る可能性があります。  
本番利用の際はリリースノートを注視してください。

---

**参考リンク**
