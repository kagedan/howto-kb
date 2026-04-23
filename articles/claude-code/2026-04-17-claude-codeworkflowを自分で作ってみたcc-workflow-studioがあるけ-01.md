---
id: "2026-04-17-claude-codeworkflowを自分で作ってみたcc-workflow-studioがあるけ-01"
title: "【Claude Code】Workflowを自分で作ってみた！CC Workflow Studioがあるけどね"
url: "https://zenn.dev/sika7/articles/778304406e60e0"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeを使っていて、こんな経験はありませんか？

* せっかくサブエージェントを作ったのに、呼び出してくれない
* Skillsを用意しても、エージェントが無視して自分でやろうとする
* 毎回同じ手順を指示するのが面倒くさい

これを解決する手段として **Workflow** があります。

Workflowとは、一連の作業フローを定義したものです。「誰が・何を・どの順番でやるか」を事前に決めておくことで、エージェントが想定通りに動いてくれるようになります。

---

## Workflowって結局なに？

Claude CodeのWorkflowは、**カスタムスラッシュコマンド用のMarkdownファイル**です。

`.claude/commands/` ディレクトリに配置したMarkdownファイルが、そのままスラッシュコマンドとして使えるようになります。

```
.claude/
└── commands/
    └── my-workflow.md  →  /my-workflow で実行できる
```

中身はMarkdownで、Claudeへの指示をステップ形式で書いておくだけです。「このSkillを使って」「このサブエージェントに渡して」「失敗したらこうして」といった内容を定義します。

---

## CC Workflow Studioというツールもある

実は、VisualエディタでWorkflowを作れる **CC Workflow Studio** というVSCode拡張機能があります。

ノードをドラッグ＆ドロップで配置して、矢印でつなぐだけでWorkflowが作れる、いわば「AIワークフローのFigma」的なツールです。GitHubで1,000以上のスターを獲得しており、活発に開発が続いています。

ただ、CC Workflow StudioはAnthropicの公式製品ではなくOSSです。最終的に生成されるのも `.claude/commands/` のMarkdownファイルです。

つまり、**Markdownを手書きすれば同じことが実現できる**わけです。

ならば試しに、**Workflowを生成するWorkflow**をClaude（このチャット）と一緒に作ってみよう！というのがこの記事の主旨です。

---

## 作ったもの

今回作成したのは、以下の2つのカスタムスラッシュコマンドです。

| コマンド | 役割 |
| --- | --- |
| `/workflow-design` | 要望を聞き取り、Mermaidで設計図を出力する |
| `/workflow-generate` | 設計図をもとにMarkdownを生成し、配置方法を案内する |

あえて2つに分割した理由は、**設計と実装を分けることで修正しやすくするため**です。設計図の段階でフローを確認・修正できるので、Markdownを生成してから「やっぱり違う」となる手戻りを減らせます。

---

## 作り方の流れ

### Step 1：やりたいことをチャットで伝える

Claudeに対して「こんなWorkflowを作りたい」と伝えます。事前にMarkdownファイルに整理しておいた場合は、ファイルパスを渡すこともできます。

```
/workflow-design ./my-idea.md
```

ファイルがなければ、口頭で伝えるだけでOKです。

### Step 2：壁打ち（要件の深掘り）

Claudeが1〜2個ずつ質問しながら要件を整理してくれます。

* どのステップをサブエージェントに任せるか
* 使いたいSkillsやMCPツールはあるか
* エラー時のリトライや条件分岐はどうするか
* Workflowの完了条件は何か

一度に全部聞いてくることはなく、会話形式で進んでいくので、要件が曖昧な状態でも整理しながら進められます。

### Step 3：Mermaidで設計図を確認する

要件が整ったら、Claudeがフロー図を生成してくれます。

図を見ながら「このステップはいらない」「条件分岐を追加したい」と修正できます。OKが出たら次のステップへ。

### Step 4：Markdownを生成する

設計図が確定したら、`/workflow-generate` を実行します。

設計図をもとに `.claude/commands/` 用のMarkdownを生成してくれます。サブエージェントが含まれる場合は、`.claude/agents/` 用の定義ファイルも一緒に生成してくれます。

### Step 5：配置して実行

生成したファイルを配置するだけで完成です。

```
mkdir -p .claude/commands
mkdir -p .claude/agents  # サブエージェントがある場合
```

あとはClaude Codeで実行するだけです。

```
/my-workflow
# 引数付きで実行する場合
/my-workflow ISSUE-001
```

---

## 実際に作った2つのコマンドの中身

### workflow-design.md（設計担当）

壁打いを通じて要件を整理し、Mermaidでフロー図を出力するコマンドです。

ポイントは以下の3点です。

* ファイルパスが渡されたらそのMarkdownを読み込む
* 質問は一度に全部せず、会話形式で1〜2個ずつ行う
* Markdownの生成はしない（設計のみ担当）

### workflow-generate.md（生成担当）

確定した設計図からMarkdownを生成し、配置方法まで案内するコマンドです。

ポイントは以下の3点です。

* 設計図が渡されなければ `/workflow-design` へ誘導する
* サブエージェントが含まれる場合は定義ファイルも生成する
* 生成したMarkdownはあくまでたたき台と明示する

---

## やってみた感想

CC Workflow Studioを使わなくても、チャットで会話しながら設計→Markdown生成まで完結できました。

特に良かった点は、**設計図（Mermaid）をレビューしてから実装（Markdown生成）に進める**という流れです。「設計図を見てから判断できる」というステップがあることで、完成してから「なんか違う」となるリスクが減りました。

一方で、CC Workflow Studioには**既存のWorkflowをビジュアルで管理・編集できる**という強みがあります。Workflowが増えてきたり、チームで共有したりする場面では、Studioのほうが便利だと感じました。

用途や好みに応じて使い分けるのが良さそうです。

---

## まとめ

* Claude CodeのWorkflowは `.claude/commands/` のMarkdownファイル
* CC Workflow Studioはそれをビジュアルで作るためのツール（OSSでAnthropicの公式ではない）
* Markdownを手書きすれば同じことが実現できる
* チャットの壁打いでも、設計→Markdown生成まで十分実現できた
* 設計（`/workflow-design`）と生成（`/workflow-generate`）を分けると修正しやすい

今回作ったコマンドのMarkdownは以下のリポジトリで公開しています。

<https://github.com/sika7/workflow-command-sample>

---

最後まで読んでいただきありがとうございました！
