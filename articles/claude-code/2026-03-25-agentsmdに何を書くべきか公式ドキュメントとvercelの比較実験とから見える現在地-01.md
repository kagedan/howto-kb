---
id: "2026-03-25-agentsmdに何を書くべきか公式ドキュメントとvercelの比較実験とから見える現在地-01"
title: "AGENTS.mdに何を書くべきか？公式ドキュメントとVercelの比較実験とから見える現在地"
url: "https://zenn.dev/rai0/articles/15622bbd1ac823"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "OpenAI", "zenn"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

AI コーディングエージェント向けの指示ファイルとして `AGENTS.md` が広まりつつある。  
ただ、実務で悩むのは「何をどこまで書くべきか」だ。

全部まとめて大きな `AGENTS.md` を作るべきなのか。  
それとも、最低限だけ書いて詳細は `docs/` に逃がすべきなのか。

この記事では、OpenAI の公式事例、Vercel の比較実験、Claude Code の公式ドキュメントを並べて、**AGENTS.md の実務的な落としどころ**を整理する。

## 結論

先に結論を書くと、現時点では次の方針がかなり有力だ。

> **AGENTS.md は「百科事典」ではなく「地図・目次」にする。**  
> **詳細な規約・設計・手順は `docs/` や分割ファイルに置く。**

この方針は、OpenAI が自社事例でかなり明示的に述べ、Vercel が eval で裏づけ、Claude も「長くしすぎるな、分割しろ」という形でほぼ同じ方向を示している。OpenAI は `AGENTS.md` を「百科事典として扱うかわりに、目次として扱う」と書いており、短い `AGENTS.md` をマップとして使い、より深い情報源は別に置く構成を推奨している。

## OpenAIの事例：大きな AGENTS.md は失敗した

<https://openai.com/ja-JP/index/harness-engineering>

OpenAI の「Harness Engineering」の記事では、この点がかなりはっきり書かれている。  
Codex を使って大規模開発を進めたなかで、OpenAI は **「1つの大きな AGENTS.md」** を試し、**予測可能な形で失敗した**と述べている。 ([OpenAI](https://openai.com/ja-JP/index/harness-engineering/ "ハーネスエンジニアリング：エージェントファーストの世界における Codex の活用 | OpenAI"))

記事では失敗理由として、次の4点を挙げている。

* **コンテキストは希少な資源**であり、巨大な指示ファイルがタスクやコード、関連ドキュメントを圧迫する。
* ガイダンスが多すぎると、何が重要かわからなくなり、エージェントが意図的に辿るのではなく局所的なパターンマッチに寄りやすくなる。
* 分厚いマニュアルはすぐ腐り、古い規則の墓場になる。
* 単一の巨大ファイルは、カバレッジ・鮮度・オーナーシップ・クロスリンクのような機械的チェックに向かない。

そのうえで OpenAI は、`AGENTS.md` を **百科事典ではなく「目次」として扱う**べきだ、と結論づける。リポジトリ知識は構造化された `docs/` 配下に置き、**短い `AGENTS.md`（約100行）をマップとして使う**、という運用例まで示している。

実際に OpenAI は、次のような構成例を掲載している。

```
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   ├── core-beliefs.md
│   └── ...
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   ├── new-user-onboarding.md
│   └── ...
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   ├── uv-llms.txt
│   └── ...
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

この例から読み取れるのは、`AGENTS.md` 自体を知識の本体にするのではなく、**知識の所在を示す入口にしている**ことだ。設計、計画、仕様、信頼性、セキュリティのような重い情報は `docs/` 以下に分解され、`AGENTS.md` はそれらへ辿るための地図として機能する。

## ただしOpenAIの記事だけでは「比較実験」とは言い切れない

ここは少し冷静に見たほうがいい。

OpenAI の記事は、**自社の運用知見を共有したもの**ではあるが、厳密な意味でのコントロールされた比較実験ではない。記事中には「1つの大きな AGENTS.md を試した」とあるが、どの条件を固定し、どう比較し、何回測定したかまでは公開されていない。

なので、

* **OpenAI の主張は強い実務知見**
* しかし **そのまま厳密な比較実験結果とは言い切れない**

という整理が妥当だと思う。

ここで補助線として効くのが、Vercel の eval 記事だ。

## Vercelの比較実験：圧縮インデックス入り AGENTS.md が強かった

<https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals>

Vercel は `AGENTS.md` と skills ベースの方式を比較する eval を公開している。  
ここでのポイントは、**詳細文書そのものを全部プロンプトに入れたわけではない**ことだ。

Vercel が最も良かったとしている構成は、**`AGENTS.md` に圧縮した 8KB の docs index を埋め込み、本文は `.next-docs/` ディレクトリから必要に応じて読む**方式である。これで **100% pass rate** を達成し、skills は明示的に使わせても最大 79% だったとしている。 ([Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals "AGENTS.md outperforms skills in our agent evals - Vercel"))

さらに Vercel 自身が、**エージェントは全文をコンテキストに持たなくても、どこにドキュメントがあるかを知っていればよい**と説明している。必要な情報があれば、`.next-docs/` ディレクトリから該当ファイルを読む。

これは OpenAI の「AGENTS.md は目次」という主張と、構造的にかなり近い。

* `AGENTS.md` には**圧縮された案内情報**
* 詳細は**外部のドキュメント群**
* 必要なときだけ**該当ファイルを読む**

という設計だからだ。

### ただし、Vercel の結論は少し限定付きで読むべき

Vercel の比較は有益だが、これも万能の一般法則として読むべきではない。

なぜなら Vercel が比較しているのは、**一般的な framework knowledge を扱う文脈で、skills よりも passive context が強かった**という話だからだ。つまり、

* **一般知識の導線としては、AGENTS.md のインデックスが強い**
* ただし **特定タスク専用のワークフロー**では別の仕組みが有効な余地もある

という読み方が自然だと思う。

それでもなお、この実験が強く示しているのは、**“AGENTS.md に全部を書く” のではなく “AGENTS.md に探し方を書く” のが強い**という点だ。

## Claude Codeの公式ドキュメント：同じ方向だが、言い方は少し柔らかい

<https://code.claude.com/docs/ja/memory>

Claude Code には `AGENTS.md` ではなく `CLAUDE.md` がある。  
ここで Anthropic の公式ドキュメントを見ると、かなり近い運用指針が出ている。

まず、**`CLAUDE.md` は 200 行以下を目標にし、長くなるとコンテキスト消費が増え、遵守が下がる可能性がある**ので、長くなったら `@path` インポートや `.claude/rules/` に分割するよう案内している。 ([Claude](https://code.claude.com/docs/ja/memory "Claude があなたのプロジェクトを記憶する方法 - Claude Code Docs"))

また `.claude/rules/` については、

* 指示を複数ファイルにモジュール化できる
* 特定のファイルパスにスコープできる
* 一致するファイルで作業するときだけ読み込まれる
* ノイズを減らし、コンテキストを節約できる

と説明している。

ここで重要なのは、Claude が **「CLAUDE.md は目次である」とまでは言っていない**ことだ。  
OpenAI ほど強く「百科事典にするな」と定義してはいない。

ただし実務上のメッセージはかなり近い。

* 長い1ファイルは避ける
* 必要に応じて分割する
* 常時ロードが不要な情報は別レイヤーへ逃がす
* スコープを絞ってノイズを減らす

ということだからだ。

なので、Claude は**完全な目次型とまでは言わないが、詳細を外部化・分割する方向性は同じ**であり、ただし OpenAI より少し緩い、という整理がしっくりくる。

## 3社を並べると何が見えるか

整理するとこうなる。

OpenAI は最も明示的だ。  
**大きな AGENTS.md は失敗した**とまで書き、**短い AGENTS.md を目次として使い、詳細は `docs/` 配下へ**という構成を推している。

Vercel は比較 eval で、**圧縮 docs index を埋め込んだ AGENTS.md + 外部 docs** が強かったと示した。  
詳細本文を全部入れるのでなく、**“どこにあるか” を持たせる**設計が効いたと読める。

Claude は `CLAUDE.md` を短く保ち、長くなったら `@path` や `.claude/rules/` に分割せよという方針だ。  
**目次と明言はしないが、巨大単一ファイルを避ける方向は同じ**である。

この3つを合わせると、かなり自然に次の結論になる。

> **AGENTS.md / CLAUDE.md は “全部書く場所” ではなく、  
> “最初に必ず読ませたい最小限” と “詳細の入口” を置く場所である。**
