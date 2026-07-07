---
id: "2026-07-06-claude-code-ビルトインスキルの自動起動を-claudemd-でブロックする-02"
title: "Claude Code ビルトインスキルの自動起動を CLAUDE.md でブロックする"
url: "https://zenn.dev/thegatebreaker/articles/986593532fc901"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-07-06"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

TL;DR: Claude Code が標準搭載する `deep-research`（公式分類はビルトインWorkflow）はトリガーフレーズで自動起動し、`disable-model-invocation` では止められない。`CLAUDE.md` に禁止ルールを書くことで自動起動をソフトブロックできる。完全に無効化する `settings.json` 側の設定も別途存在するが、対象を個別に選べない。

## 何が起きたか

「ディープリサーチして」と打った瞬間、`deep-research`（公式分類：ビルトインWorkflow）が起動した。マルチエージェント Workflow が走り、トークンが大量消費された。設定は何も変えていなかった。

原因はシンプルだ。**初めてそのトリガーフレーズを使ったから、初めて起動した。** ビルトインで提供される機能は常時トリガー待ち状態にある。

## 実装 — CLAUDE.md に追加したルール

対処は `CLAUDE.md` にルールセクションを一つ追加するだけだった。実際に追記した内容の全文はこちら：

```
## Deep Research Delegation Rule

ClaudeCode must **never** invoke the `deep-research` skill autonomously,
including when the user says phrases like "ディープリサーチして",
"deep research して", "詳しく調べて", or similar.

Deep research is delegated to **Perplexity** by the Human.

When a user requests deep research:

1. Do NOT invoke the `deep-research` skill.
2. Respond: 「ディープリサーチは Perplexity にご依頼ください。」
3. If the user explicitly types `/deep-research` as a slash command,
   it may be invoked — but only then.
```

実装のポイントは三つ。

* **禁止する言葉を列挙する** — 「ディープリサーチして」「deep research して」「詳しく調べて」など、実際に使いそうな表現を具体的に書く。曖昧な言い回し一つに頼らない。
* **代替案を明示する** — 「Perplexity にご依頼ください」という定型応答をそのまま指定する。AIが自己判断で言い換えないようにする。
* **明示コマンドの例外を書く** — `/deep-research` と明示的に打った場合のみ許可することを明記し、機能自体は殺さない。

`CLAUDE.md` に書いたルールは「Always-on rules」として機能し、スキルの動作より優先される。  
![](https://static.zenn.studio/user-upload/3b7dade202f7-20260706.png)

## なぜこれで効くか — スキル・Workflowの起動モデル

Claude Code の機能には、ユーザーが定義するものとプラットフォームが提供するものがある。

### カスタムスキル

プロジェクト内の `SKILL.md` で定義する。フロントマターで制御可能：

```
---
disable-model-invocation: true
---
```

このフラグを設定すると、`/skill-name` と明示的に打たない限り起動しない。  
![](https://static.zenn.studio/user-upload/8f046c72f91a-20260706.png)

### ビルトインで提供されるスキル・Workflow

Claude Code プラットフォームが提供する機能（`/code-review` のようなビルトインスキル、`deep-research` のようなビルトインWorkflow）。ユーザーが編集できる `SKILL.md` が存在しないため、`disable-model-invocation` を設定する場所がない。トリガーフレーズにマッチした発話で自動起動する。これはプラットフォームの仕様。

だからこそ、コードレベルのフラグではなく `CLAUDE.md` という宣言的なルール層で振る舞いを縛る必要があった。

## 他に注意するビルトイン機能

| 機能 | 公式分類 | 起動条件 | 対策 |
| --- | --- | --- | --- |
| `deep-research` | ビルトインWorkflow | 自然言語トリガー | CLAUDE.md 禁止ルール（個別）／`disableWorkflows`（全Workflow一括） |
| `code-review ultra` | ビルトインスキル | `/code-review ultra` 明示のみ | 低リスク・対策不要 |
| カスタムスキル | カスタム | トリガー条件 or `/cmd` | `disable-model-invocation: true` |

`code-review ultra`（`/ultrareview`）は明示コマンドが必要なため自然言語からの誤起動リスクは低い。高コストという点は `deep-research` と共通するが、勝手に発火する条件が異なる。  
![](https://static.zenn.studio/user-upload/2d4dd7d7b84e-20260706.png)

## 設計観点

AI worker の運用コストを管理するには、「意図しない自動起動」への対策が必要だ。

ビルトインで提供されるスキル・Workflowはプラットフォーム提供のため、カスタムスキルのようにコードレベルで個別に制御できない。代わりに、CLAUDE.md という宣言的なルール層で振る舞いを制約する。

> CLAUDE.md ルールは AI の判断に依存するソフトブロックだ。`--no-verify` でフックを飛ばせるように、強制的な上書き指示で無効化される可能性はゼロではない。完全に無効化したいケースでは、`settings.json` の `disableBundledSkills: true`（バンドルドスキル・Workflowを丸ごと削除）または `disableWorkflows: true`（Workflowのみ無効化）の利用を検討すること。ただしどちらも個別の機能だけを狙い撃ちすることはできず、他の便利なビルトイン機能も道連れに止まる点に注意。`permissions.deny` はツール呼び出しのブロック用であり、スキル・Workflow自体の無効化とは別の機能なので混同しないこと。

実際のプロジェクトでは、機能の存在を把握した時点で禁止ルールを書くことを推奨する。事後対応より事前宣言のほうが、トークン消費の予測可能性が上がる。

---

*この記事は実際の運用ログをもとに書いています。*

![](https://static.zenn.studio/user-upload/b59086b093f9-20260706.png)
