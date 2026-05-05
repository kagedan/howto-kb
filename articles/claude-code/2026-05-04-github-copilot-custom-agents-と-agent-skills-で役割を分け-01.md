---
id: "2026-05-04-github-copilot-custom-agents-と-agent-skills-で役割を分け-01"
title: "GitHub Copilot: custom agents と Agent Skills で役割を分ける"
url: "https://zenn.dev/sawa_shin/articles/github-copilot-subagents-skills-guide"
source: "zenn"
category: "claude-code"
tags: ["MCP", "AI-agent", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

instructions でプロジェクト全体のルールを整えたら、次に感じるのは

「**もっと構造的に Agent に仕事を任せたい**」

ということではないでしょうか。

たとえば：

* 品質チェックに特化した agent を用意して、レビュー専門で動かしたい
* 設計とドキュメント作成で、別の視点を持った agent に切り替えたい
* agent に「こんな場面ではこの手順とスクリプトを使って」と武器を持たせたい

この記事では VS Code の Agent Mode を前提に、**custom agents** と **Agent Skills** を使って役割と武器を持たせる方法を整理します。

この記事の前提

* 2026-04 時点の GitHub Docs と VS Code Docs で確認できる範囲が土台です
* VS Code の Agent Mode を前提にしています
* prompt files、hooks、MCP は扱いません
* 公式仕様と私の運用判断は分けて書いています

## この記事で得られること

1. instructions だけでは解決しにくくなる場面
2. **custom agent** と **subagent** の関係
3. Agent Skills で **agent に武器を持たせる** 考え方
4. custom agent と skill を**セットで設計する**視点

---

## instructions だけでは足りなくなるのはどんなとき？

instructions は「プロジェクト全体のルール」や「特定ファイルのルール」として効かせる仕組みです。でも使い込んでいくと、**ルールだけでは解決しにくい場面** が出てきます。

こうなると、instructions とは別の仕組みが必要になります。

ここで登場するのが、**custom agents** と **Agent Skills** です。

![1枚のinstructionsに詰め込まず、役割ごとのagentへ分けるイメージ](https://static.zenn.studio/user-upload/deployed-images/766d6aa0546a72c8a3cdd8fb.png?sha=868b514f1e9ccd8ddddec9ae8956cf23cf163327)

---

## custom agent ってなに？

custom agent は、**特定の役割・指示・使える道具を定義した、専門家としての agent** です。

`.github/agents/` 配下に `.agent.md` ファイルを置くことで作成できます。

```
your-project/
└── .github/
    └── agents/
        ├── pm.agent.md          ← 計画・分解専門（PM）
        ├── qa-gate.agent.md     ← 品質判定専門（QA Gate）
        └── critic.agent.md      ← 批評専門（Critic）
```

たとえば、品質判定専門の custom agent はこんなイメージです：

```
---
name: qa-gate
description: 変更内容に応じて検証と専門レビューを選び、Go / No-Go を集約する品質ゲート。
tools: ["read", "search"]
---

# QA Gate

あなたは公開判定の専門家です。
- 変更された diff を読み、設計方針・テスト・規約との整合を確認する。
- Go / No-Go と、その理由・残課題を簡潔に出す。
- ファイルの編集は行わず、判定と指摘のみを行う。
```

> 📖 custom agent の YAML 設定項目については公式ドキュメントを確認してください。  
> [GitHub Docs: Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
>
> VS Code 側の使い方は、公式ドキュメントの custom agents と chat agents の説明も参考になります。  
> [VS Code Docs: Custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)  
> [VS Code Docs: Get started with chat](https://code.visualstudio.com/docs/copilot/chat/chat-ask-mode)

ポイントは：

* `tools` で使える道具を制限できる（read だけ、edit も含める、など）
* VS Code のチャットで `Agent`、`Plan`、`Ask`、`Edit` などを選ぶのと同じように、作成した custom agent を選んで、その agent として直接実行できる

VS Code のチャットには agent picker があり、組み込みの `Agent`、`Plan`、`Ask`、`Edit` に加えて、自分で作成した custom agent も選べます。

たとえば `qa-gate.agent.md` を作っておけば、最初から qa-gate を選んで判定観点で相談できます。あるいは、通常の Agent Mode で作業を進めながら、途中で `@qa-gate` を呼び出して品質判定だけ任せることもできます。前者は「その agent として直接使う」使い方、後者は「subagent として呼ぶ」使い方です。

![custom agentを直接選ぶ使い方と、作業中にsubagentとして呼び出す使い方のイメージ](https://static.zenn.studio/user-upload/deployed-images/7fbf35bdd76271fcb59caf89.png?sha=2fc4266996a2eb6bb4bb52e62c7a21f707a2b006)

---

## subagent ってなに？

custom agent を複数定義すると、ある agent から別の agent を呼び出す構成が可能になります。このとき、呼び出された側の agent を **subagent** と呼びます。

つまり：

* あなたが Agent Mode で作業を依頼する
* Agent Mode（main agent）が「この部分は品質判定に任せよう」と判断する
* `@qa-gate` という custom agent が呼び出される
* この呼び出された qa-gate が **subagent**

> 📖 [VS Code Docs: Subagents in Visual Studio Code](https://code.visualstudio.com/docs/copilot/agents/subagents)

custom agent と subagent の関係を整理すると：

| 概念 | 意味 |
| --- | --- |
| **custom agent** | 特定の役割を定義した **.agent.md ファイル** |
| **subagent** | main agent から呼び出された **実行時の立場** |

**custom agent を作っておくと、それが subagent として呼び出される**——この関係だけ押さえれば十分です。全体として、各タスクをそれぞれ得意な agent に渡せる構成が、Agent Mode を組織的に使う強みです。

---

## Agent Skills ってなに？

Agent Skills は、**agent に装備させる武器** のようなものです。

instructions は「ルール」、custom agent は「専門家」だとすると、skill は **「その専門家に持たせる道具箱」** です。

![Agent Skillsを専門agentに持たせる道具箱として表したイメージ](https://static.zenn.studio/user-upload/deployed-images/bed7ba78687959429d519b11.png?sha=9c4a642c350f09ca809fb8522776dfdfb8c7fb57)

> 📖 [GitHub Docs: About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)

skill は `.github/skills/` 配下にディレクトリを置き、その中に `SKILL.md` を作成することで定義します。**`SKILL.md` が最低限必要なファイル**で、ここに skill の `description` と指示を記述します。

```
.github/skills/
├── coding-standards/
│   └── SKILL.md              ← これだけで skill として機能する
└── official-docs-enforcer/
    ├── SKILL.md              ← メインの指示ファイル（description 必須）
    └── resources/            ← 必要に応じて参考資料を追加
```

### instructions との違い

|  | instructions | Agent Skills |
| --- | --- | --- |
| **何か** | ルール・方針 | 手順 + スクリプト + 参考資材のパッケージ |
| **いつ効く** | 常に読み込まれる | Copilot が関連ありと判断したときだけ |
| **向いている場面** | 「毎回言いたいこと」 | 「この場面で使う手順とツール一式」 |

### custom agent + skill をセットで考える

custom agent と Agent Skills は**セットで設計する**と効果的です。

前の例で出した `pm`、`critic`、`qa-gate` に合わせるなら、こんな分け方ができます。

| custom agent | 役割 | 持たせたい skill |
| --- | --- | --- |
| `pm` | 依頼を分解し、作業順序を決める | 設計メモ・タスク分解テンプレート |
| `critic` | タイトル・目的・本文のずれを疑う | 公式ドキュメント確認、主張チェックリスト |
| `qa-gate` | diff を読み、Go / No-Go を判定する | コードレビューチェックリスト、テスト観点 |

特化した agent に特化した skill を結びつけることで、「この場面ではこの手順で」を毎回指示しなくても、agent が自分でスキルを読み込んで動いてくれます。

---

## code 作業と Markdown 作業ではどう分ける？

custom agent + skill の組み合わせを、2 つのパターン例で見てみましょう。

### コード作業の場合

1. **main agent** が実装全体を持つ
2. `@pm` に依頼を分解してもらう
3. 実装を進める
4. `@qa-gate` に diff を確認してもらい Go / No-Go をもらう
5. 必要なら test / debug 系の **skill** が読み込まれる

### Markdown（ドキュメント作成）の場合

1. **main agent** がドキュメントの約束を守る
2. `@pm` に構成案を整えてもらう
3. 本文を書く
4. `@critic` にタイトルと本文の約束がずれていないかを見てもらう
5. 最後に `@qa-gate` で公開可否を判定する

---

## まとめ

ここまでを整理すると：

| 概念 | 役割 |
| --- | --- |
| **instructions** | プロジェクト全体のルール |
| **custom agent** | 特定の役割を持った専門 agent（ファイル定義） |
| **subagent** | main agent から呼び出された agent（実行時の立場） |
| **Agent Skills** | agent に装備させる武器（手順 + スクリプト + 資材のパッケージ） |

使い込んでいく中で「もっと構造化したい」と感じたら、**特化した agent に特化した skill を持たせる**ことを考えてみてください。

---

!

➡️ **次回: だれでも使える最小ハーネス設計**

custom agents も Agent Skills も、並べ方次第で効き方が変わります。第 4 回では、ここで紹介した **`pm` / `critic` / `qa-gate` の 3 役** を「mission → instructions → agents → review」の順に並べた **だれでも再現できる最小構成** を、実際のディレクトリ構成・ファイルの中身・Copilot に作らせるプロンプト例まで含めて紹介します。

👉 [第4回: GitHub Copilot 最小ハーネス設計](https://zenn.dev/sawa_shin/articles/github-copilot-minimal-harness-design)
