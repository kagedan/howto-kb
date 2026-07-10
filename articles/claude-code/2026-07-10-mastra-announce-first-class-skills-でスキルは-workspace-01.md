---
id: "2026-07-10-mastra-announce-first-class-skills-でスキルは-workspace-01"
title: "[Mastra Announce] First-Class Skills で「スキルは Workspace のもの」から卒業"
url: "https://zenn.dev/shiromizuj/articles/63d473e1e01440"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## 今回の発表をひとことで言うと

2026年7月7日、Mastra は **First-Class Skills** を発表しました。これまで Workspace にぶら下げるのが前提だった Skills を、**個々の Agent に直接アタッチできる**ようにしたアップデートです。

単に設定場所が増えた、という話ではありません。これまでは「スキルを使いたいなら Workspace も filesystem も、場合によっては sandbox も考える」という設計でした。今回からは、スクリプト実行やファイル参照を必要としない多くのスキルで、`createSkill()` や `skills/*.md` だけで完結するようになります。

つまり今回の本質は、**Skills を“プロジェクト全体の共有資産”としてだけでなく、“そのエージェント固有の能力”として持てるようになった**ことです。

---

## 前提: Mastra の概念を先に 1 枚で見る

今回の話は Mastra における `workspace` と `agent` の役割を先に分けておくと理解しやすくなります。厳密には単純な親子関係ではなく、**各 Agent が必要に応じて 1 つの Workspace を参照する**という関係です。Workspace は共有できるので、複数 Agent が同じ Workspace を使うこともあります。概念の置き場をざっくり図にすると次のようになります。

```
Mastra アプリケーション / プロジェクト
├── Agent
│   ├── model
│   ├── instructions
│   ├── tools
│   ├── memory
│   ├── agent-level skills // ★ ここにも定義可能になった
│   ├── subagents
│   └── workspace（必要なときに接続）
│       ├── filesystem
│       ├── sandbox
│       ├── workspace-level skills // ★ もともと、ここだけだった
│       └── search / indexing
├── Workflow
├── MCP / Browser / Observability などの周辺機能
└── Storage / Server / Studio などの実行基盤
```

この図で重要なのは 3 点です。

* `Agent` はユーザーと直接やり取りして推論する主体で、`instructions`、`tools`、`memory`、`agent-level skills` のような能力を持つ
* `Workspace` はその Agent が必要に応じて使う共有作業環境で、filesystem、sandbox、shared skills、search index などをまとめる
* Skills には、Agent 自体に直付けする `agent-level skills` と、Workspace 側で共有する `workspace-level skills` の 2 つの置き場がある

もともとの Mastra Skills は Workspace 側で見つけて使う `workspace-level skills` が中心でした。今回の First-Class Skills は、**その Skills を Agent 自体の能力としても持てるようにした**アップデートだと考えると位置づけが分かりやすいです。

---

## 背景: これまで何が課題だったのか

### Skills は便利だったが、少し大げさだった

Mastra は 2026年2月の時点で、すでに Skills を持っていました。しかも Agent Skills 仕様に準拠していて、`SKILL.md`、`references/`、`scripts/` のような構造化された知識を段階的に読ませる仕組みまで備えていました。

ただし当時の Skills は、基本的に **Workspace 配下で発見・管理する仕組み** でした。これは、複数エージェントで共有するスキルや、ファイルシステムを読むスキル、スクリプトを実行するスキルには相性が良い一方で、もっと軽い用途には少し重かったのです。

たとえば、単一エージェントに対して「レビュー時の観点」や「複数日予報のまとめ方」のような短い指示を与えたいだけでも、

* Workspace を持つべきか
* スキルをどのディレクトリに置くべきか
* filesystem や sandbox をどう考えるべきか
* それは本当に shared skill にすべきか

といった設計判断が先に立ちます。

本当は「このエージェントにはこのノウハウを持たせたい」だけなのに、実装の重心が Workspace 側に寄っていたわけです。

### エージェントの再利用単位とスキルの再利用単位がずれていた

Mastra の Agent は、用途ごとにパッケージ化したり、コード登録型とファイルベース型で分けたり、かなり細かく分解して扱えます。ところが Skills は Workspace 管理が中心だったため、エージェント単位で持ち運びたい知識と、プロジェクト全体で共有したい知識が同じ入れ物に押し込まれがちでした。

その結果、

* ライブラリとして配布したいエージェントに、スキルも一緒に同梱しにくい
* テナントやユーザーロールごとにスキルを切り替えたいときに回り道が増える
* 「このエージェントは self-contained にしたい」という設計と相性が悪い

という違和感がありました。

### Workspace が不要なケースまで Workspace 前提になっていた

Workspace Skills は今でも重要です。特に次のようなケースでは向いています。

* `scripts/` を実行したい
* `references/` や `assets/` をファイルとして持ちたい
* 複数エージェントで同じスキル群を共有したい
* BM25 や vector search でスキル横断検索したい

ただ、逆に言えば、そこまでの機能が不要なケースも多い。短い再利用可能な指示を与えるだけなら、Workspace はオーバーヘッドになり得ます。Mastra 自身も今回の発表で、**ファイルシステムやスクリプトが必要な場合は引き続き Workspace スコープを推奨するが、多くのスキルではよりシンプルな方法が使える**と整理しています。

---

## 何がどう変わったのか

### Agent に直接 `skills` を持たせられる

コード登録型エージェントでは、`createSkill()` で作ったスキルをそのまま `skills` 配列に渡せます。

```
import { Agent } from "@mastra/core/agent";
import { createSkill } from "@mastra/core/skills";

const forecasting = createSkill({
  name: "forecasting",
  description: "複数日の天気予報をまとめるときに使う。",
  instructions: `
複数日の天気予報を要約するときは、次の順序で整理してください。
1. 各日の最高気温と最低気温を書く
2. 降水確率を目立つように示す
3. 前日との大きな変化があれば補足する
`.trim()
});

export const weatherAgent = new Agent({
  id: "weather-agent",
  model: "openai/gpt-5.5",
  instructions: "あなたは天気アシスタントです。",
  // エージェント固有のノウハウを直接ぶら下げられる
  skills: [forecasting]
});
```

この形の良さは、エージェント定義を見れば、そのエージェントが何を知っているかがすぐ分かることです。Workspace の外に出せるので、エージェントをパッケージやライブラリとして配布するときも、能力をまとめて持ち運びやすくなります。

### ファイルベースエージェントでは `skills/*.md` を置くだけ

ファイルベースエージェントでも、考え方は同じです。`skills/` ディレクトリに Markdown ファイルを追加すれば、それがそのままスキルになります。

```
src/mastra/agents/
└── weather-agent/
    ├── config.ts
    ├── instructions.md
    └── skills/
        ├── forecasting.md
        └── temperature-units.ts
```

```
複数日の天気予報を要約するときは、次の順序で整理してください。

1. 各日の最高気温と最低気温を書く
2. 降水確率を目立つように示す
3. 日ごとの差分が大きい場合は補足する
```

ファイル名がスキル名になり、本文がそのまま指示になります。以前の「Workspace 内の skill directory をどう設計するか」ではなく、「このエージェントに何を教えたいか」を先に考えられる構造です。

### Agent-level と Workspace-level は排他的ではない

ここはかなり重要です。今回の機能は、Workspace Skills を捨てるためのものではありません。**同じ Agent に両方を併用できます。**

しかも実行時に両者はマージされ、同名なら Agent-level のほうが優先されます。つまり、

* チーム共通の標準スキルは Workspace 側
* その Agent だけの上書きや特例は Agent 側

という構成が取れます。

これは実務的です。共通ルールを全部コピーせずに、必要な差分だけ Agent 側で持てるからです。

### 動的スキルも扱える

コード登録型では、`skills` に配列だけでなく関数も渡せます。`requestContext` を見て、ユーザーのロールやテナントごとにスキルを切り替えられます。

```
import { Agent } from "@mastra/core/agent";
import { createSkill } from "@mastra/core/skills";

const developerGuide = createSkill({
  name: "developer-guide",
  description: "開発者向けの作業方針。",
  instructions: "実装時は変更理由とテスト方針も合わせて説明してください。"
});

const supportGuide = createSkill({
  name: "support-guide",
  description: "サポート担当向けの対応方針。",
  instructions: "問い合わせ対応では結論、原因、次のアクションの順に返してください。"
});

export const triageAgent = new Agent({
  id: "triage-agent",
  model: "openai/gpt-5.5",
  instructions: "あなたは問い合わせを整理する担当です。",
  // requestContext の値に応じて返すスキルを切り替える
  skills: ({ requestContext }) => {
    const role = requestContext.get("userRole");
    if (role === "developer") return [developerGuide];
    return [supportGuide];
  }
});
```

これにより、単なる「静的な知識の束」ではなく、**文脈に応じて差し替わる能力**として Skills を使えるようになります。

---

## 以前の課題に対して、今回どこまで解決したのか

### 解決したこと 1: 単一 Agent に知識を付与するまでの距離が短くなった

以前は、短い指示を再利用したいだけでも Workspace 設計に引っ張られやすかった。今回はそれが、`createSkill()` か `skills/*.md` に落ちました。つまり、**「能力を与える」操作が Agent 定義の近くまで引き寄せられた**わけです。

これは onboarding にも効きます。特にファイルベースエージェントでは、`instructions.md` と同じ感覚で `skills/forecasting.md` を置けるので、「まず何をどこに書けばよいか」が直感的になりました。

### 解決したこと 2: self-contained な Agent を作りやすくなった

Agent-level Skills は Workspace に依存しません。Mastra の docs でも、self-contained な Agent、コードで定義されたスキル、ライブラリやパッケージとして配布する Agent、request context ベースでスキルを切り替えたいケースに向いていると整理されています。

これはかなり大きい変化です。Agent 自体をひとつのモジュールとして扱いたい場合、スキルまで含めて完結させられるからです。

### 解決したこと 3: 共通スキルと個別スキルの役割分担がしやすくなった

Workspace Skills を全否定せず、runtime で merge しつつ Agent 側が優先される、という設計は現実的です。共通ルールは centralize しつつ、Agent ごとの差分だけを local override できます。

これはフロントエンドでいう theme token と component override の関係に近く、shared policy と local specialization を両立しやすい構造です。

---

## それでも Workspace Skills が必要な場面

今回の発表を「Workspace Skills の置き換え」と読むのは正確ではありません。Workspace 側には、Agent-level にはない役割があります。

### `SKILL.md` を中心にしたパッケージング

Workspace Skills は Agent Skills 仕様そのものに近い形です。`SKILL.md` に frontmatter を持たせ、`references/`、`scripts/`、`assets/` を束ねる構造は、単なる短文 instruction よりも豊かな配布単位です。

仕様上も、エージェントは次の 3 段階で情報を読む前提になっています。

1. `name` と `description` だけを先に読む
2. 必要になったスキルの `SKILL.md` 本文を読む
3. さらに必要なら `references/` や `scripts/` を読む

この progressive disclosure は、スキルを大量に持つときに特に効きます。

### 検索と discovery

Workspace 側では、BM25 や vector search を有効にすると skill content が自動でインデックスされます。エージェントは `skill_search` で横断的に探せます。

Agent-level Skills でも `skill`、`skill_read`、`skill_search` は使えますが、複数ディレクトリにまたがる shared skill pool を運用したり、同名スキルのソース種別を整理したりするのは Workspace 側の仕事です。

### ファイルシステムやスクリプトを使うスキル

Mastra 自身が明言している通り、スキルがスクリプトを実行したり、ファイルシステム上の資料を読む必要があるなら、Workspace スコープは今も推奨です。今回の Agent-level Skills は、その手前にある「もっと軽いスキル」の受け皿と見るのが自然です。

---

## Agent Skills 仕様との関係

Mastra の Skills は、もともと [Agent Skills 仕様](https://agentskills.io/specification) に沿っていました。今回のアップデートも、その流れを壊していません。むしろ、仕様ベースの skills ecosystem を維持しつつ、Mastra の Agent 定義により自然に溶け込ませた、と見るべきです。

仕様の要点を雑にまとめると、

* `SKILL.md` は metadata と instructions を持つ
* `references/`、`scripts/`、`assets/` を必要時に読む
* スキルは一気に全部読むのではなく、必要になった分だけ読む

という設計です。

今回の First-Class Skills は、この思想をそのままに、Mastra の Agent API と file-based agent のファイル構造の中へ押し込んだ実装です。だから「新しい別物」ではなく、**既存の skill model を Agent 中心に再配置した**アップデートだと理解すると全体像がつかみやすいです。

---

## 実務でどう使い分けるべきか

迷ったら、まず次のように分けると整理しやすいです。

| 使い方 | 向いている置き場所 |
| --- | --- |
| 単一 Agent に固有の短いノウハウを与えたい | Agent-level Skills |
| パッケージやライブラリとして Agent ごと配布したい | Agent-level Skills |
| ユーザーやロールごとに動的に切り替えたい | Agent-level Skills |
| 複数 Agent で共有する大きめの知識ベースを持ちたい | Workspace Skills |
| `references/` や `scripts/` を含む本格的な skill package にしたい | Workspace Skills |
| 横断検索や shared discovery を重視したい | Workspace Skills |

この整理を見ると、今回のアップデートは「Workspace か Agent か」の二者択一を迫るものではなく、**軽量スキルの置き場所を増やした**と考えるのが正しいです。

---

## まとめ

First-Class Skills は、Mastra の Skills をより Agent 中心にしたアップデートです。これまで Skills は強力だった反面、Workspace 前提の構造が少し重かった。今回、Agent に直接スキルを持たせられるようになったことで、短い再利用知識をエージェント定義の近くに置けるようになりました。

特に重要なのは、Workspace Skills を捨てたのではなく、**軽量な Agent-level Skills と、重厚な Workspace Skills を役割分担できるようにした**ことです。スキルがただの shared asset ではなく、Agent の能力そのものとして扱えるようになったことで、Mastra の設計はかなり自然になりました。

言い換えると、今回の発表は「Skills が増えた」のではなく、**Skills の重心が Workspace から Agent へも移った**ということです。Mastra でエージェントをモジュールとして組み立てていく人ほど、この変化の恩恵は大きいはずです。
