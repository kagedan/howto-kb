---
id: "2026-04-05-anthropic-academyを3コース受けてみた-体系的に学べた話-01"
title: "Anthropic Academyを3コース受けてみた 体系的に学べた話📚"
url: "https://zenn.dev/kohei486/articles/35d83dcf96a282"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## はじめに

3月にAnthropic Academyが出ましたね。存在は知っていたのですが、優先して読みたいと思っておらず読めていなかったです。今更ながら読みました。

実際に受けてみたところ、断片的に知っていただけで把握できていなかったこと、体系的に理解できました。4Dフレームワークのように知っているようで言語できていなかった概念を知ることもできました。「知ってるつもり」の状態と思っている人や、Academyってどんなもの？と思っている人に向けての参考程度の記事がかければと思います。

### Anthropic Academyとは

Anthropicが2026年3月に開設した無料の学習プラットフォーム。全15コース、メール登録のみで受講可能で、修了証も取得できます。  
コースは英語だけしかなく、もっぱら私は日本語訳して読んでいました。わかりにくいところだけ英語みたいな感じで全然読めます。  
YouTubeの動画は、日本語の自動字幕が使えます。

受講サイト: <https://anthropic.skilljar.com/>

### 全体構成

コースは3つのトラックに分かれています。

| トラック | 対象者 | レベル |
| --- | --- | --- |
| **AI Fluency** | 非エンジニア（管理者・学生・教育者） | 初級 |
| **Product Training** | 業務にClaudeを組み込みたい人 | 中級 |
| **Developer Deep-Dives** | API統合・本番運用する開発者 | 上級 |

**AI Fluency トラック（6コース）**

| コース名 | 内容 |
| --- | --- |
| Claude 101 | Claudeの基本的な使い方・プロンプティング基礎 |
| AI Fluency: Framework & Foundations | 4Dフレームワーク（委任・記述・判断・勤勉さ）でAIとの協働を学ぶ |
| AI Fluency for Students | 学生向けにカスタマイズされたAI活用 |
| AI Fluency for Educators | 教育者向けAI活用 |
| Teaching AI Fluency | AI Fluencyを他者に教えるためのコース |
| AI Fluency for Nonprofits | NPO向けAI活用 |

**Product Training トラック（3コース）**

| コース名 | 内容 |
| --- | --- |
| Introduction to Claude Cowork | Claude Coworkの使い方入門 |
| Claude with Amazon Bedrock | AWS Bedrock経由でのClaude活用 |
| Claude with Google Cloud's Vertex AI | GCP Vertex AI経由でのClaude活用 |

**Developer Deep-Dives トラック（6コース）**

| コース名 | 内容 |
| --- | --- |
| Building with the Claude API | API統合の本番パターン（ストリーミング、ツール呼び出し等） |
| Claude Code in Action | Claude Codeによる開発ワークフロー実践 |
| Introduction to Model Context Protocol | MCP基礎（外部サービス連携） |
| Model Context Protocol: Advanced Topics | MCP本番運用・トランスポート・安全性 |
| Introduction to Agent Skills | 再利用可能なスキル（マークダウン指示）の作成 |
| Introduction to Subagents | サブエージェントの活用 |

### 今回受講した3コース

今回はClaudeから進めもあり、この中から以下の3コースを受講しました:

* **Claude 101** - Claudeの基礎と活用フレームワーク
* **Introduction to Agent Skills** - スキルの設計と運用
* **Claude Code in Action** - Claude Codeの実践的な使い方

全体的な所感としては、私のようにざっくり理解で使ってしまう人は向いているが、公式のドキュメントをちゃんと読んでいる人ならやらなくてもいい、くらいな感じに思います。

ここからは実際に受けたコースがどういうものだったのか、個人的に知らなかったことなどを書いていきます。

## Claude 101 - AIの使い方、Claudeでできること

### 正直な感想

このコースはClaudeを使ってできることがざっくり学べるのがいいところです。  
初手、最新のモデル情報ではなく、Sonnet 4.5やOpus 4.5が出ている今、紹介されているモデルは一世代前のものでした。なので、最新情報を期待して受けると肩透かしを受けるかもしれません。  
ただ、今回受けた3つのコースの中で、このコースが一番学びでした。

時間にして2時間強くらいかかりました。

### 4Dフレームワーク（AI Fluency）

1番の収穫？かもしれないのはここで、AnthropicはAIをうまく使える力を「AI Fluency（AI流暢性）」として定義していて、その核となる4つの力を4Dとして整理しています。

* **Delegation（委任）** - 何をAIに任せ、何を人間がやるべきか
* **Description（説明）** - 何をどうAIに伝えるべきか
* **Discernment（見極め）** - AIが出力したものを評価する力
* **Diligence（責任）** - AIと作った成果物を外部に発信するときの注意点

うまく言語化するのが自分ではできなかったので、下記の書き方を拝借しています。  
<https://x.com/A7_data/status/2034608695083233352>

印象に残っているのは、人間に仕事の一部を依頼してやってもらうのをAIに代わってやってもらうというところで、  
人間相手だと、その人間に必要な情報を渡す、その人にどこまでやってもらうのかを意識しますが、AIだとそのあたりの認識が曖昧だと感じました。  
AIは同じチームで働く人という意識で接するというイメージかと思いました。

AIが上手く使える人は上記を意識した使い分けが上手いのかなと思いました。

### Claudeの各種機能

4Dフレームワークも良かったのですが、他収穫があったのはClaudeのプロダクト群の紹介パートです。なんとなく存在は知っていたものもあったのですが、ちゃんと調べていなかった機能が多かったので、学びが多かったです

* **[Cowork](https://claude.com/product/cowork)** - 契約書、財務報告書、会議議事録などの業務ファイルを渡して精査させるNotebookLM的な機能。スケジュールされたタスクの実行もできて、アプリを開いたら自動実行されるらしい
* **[Projects](https://claude.ai/projects)** - 独自のメモリ、チャット履歴、ナレッジベース、カスタマイズされた手順書を備えた独立ワークスペース。繰り返し使う参考資料を置いておける。小さい会社やNPO法人でも、これがあれば一人で事業を回せそうな気がした
* **[エンタープライズ検索](https://support.claude.com/ja/articles/12489464-%E3%82%A8%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%97%E3%83%A9%E3%82%A4%E3%82%BA%E3%82%B5%E3%83%BC%E3%83%81%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B)** - 通常のWeb検索とは異なり、接続したツール（Slack、Gmail、Google Drive、Jira等）を横断して**組織内の情報**を統合検索できる機能。「私が外出している間に昨日何が起こったのか」「プラットフォームプロジェクトの現在の阻害要因は何か」のような質問に、社内の複数ソースをまたいで回答してくれる。チームやエンタープライズ組織向けの機能
* **[Research Mode](https://support.claude.com/en/articles/11088861-using-research-on-claude)** - 5分〜45分かけて体系的に調査してくれるモード。Deep Research的な機能はGeminiなどで使っていたのですが、こっちは知らなかった
* **[Claude for Excel](https://claude.com/claude-for-excel)** - Excel上でClaudeが使えるアドイン。私はExcel使っておらずですが、私は存在すら知らなかったので共有

Claude Codeばかり使っていて、Claudeのプロダクト群のキャッチアップが全然できていなかったと感じました。  
普段の業務でも使えるものが多そうで、特にCoworkやProjectsは、Claude Codeとは別の文脈で導入を検討する価値がありそうに感じました。

### 所感

プロンプトの書き方（具体的に書く、背景をちゃんと書く等）は公式ドキュメントにも書かれている内容で、どこかで見たものではありました。ただ、枝葉のテクニックではなく、AIツールが発展しても変わりにくい本質的な部分を体系的に学べるのは価値があると感じます。

2026年後半にはAWSのバッジのようにClaudeの認定試験も始まるらしいので、その準備にもなりそうに思います。

## Introduction to Agent Skills - スキル設計の勘所

### 正直な感想

全く知らないということはなかったのですが、断片的に知っていたことや過去に調べたが覚えていないことが体系的に学べました。  
私にとっては101ほど学びはなかったのですが、1時間もかからず見終わるので、気になっていたら読むのいいと思います。

### スキルの優先順位

複数の場所にスキルがある場合、どれが優先されるかが明確に定義されています。

1. エンタープライズ（管理対象設定、最優先）
2. 個人（`~/.claude/skills`）
3. プロジェクト（`.claude/skills`）
4. プラグイン（最低優先度）

衝突を避けるため、「レビュー」ではなく「フロントエンドレビュー」のように具体的な名前をつけることが推奨されています。

### SKILL.mdの設計原則

* `name` と `description` が必須。`allowed-tools` と `model` はオプション
* descriptionが最も重要 - Claudeがスキルのマッチングに使う。スキルが発動しない場合、原因はほぼ間違いなくdescription
* **SKILL.mdは500行以内に収める**。詳細は `references/` や `scripts/` に分ける（段階的情報開示）
* スクリプトはコンテキストにコンテンツをロードせずに実行され、出力のみがトークンを消費する

### CLAUDE.md / Skills / Hooks / Subagents / MCPの使い分け

これは何回も見ているのですが、ぱっと説明できるかというと怪しいのでメモ

* **CLAUDE.md** - すべての会話で読み込まれる。常時稼働のプロジェクト標準
* **Skills** - リクエストに合致した時だけ読み込まれる。タスク固有の専門知識
* **Hooks** - イベント駆動型（ファイル保存時、ツール呼び出し時など）
* **Subagents** - 分離された実行コンテキスト。委任された作業用
* **MCP** - 外部ツールとの統合

## Claude Code in Action - ClaudeCodeの使い方

### 正直な感想

3コースの中では知らないことが一番少なかったです。知らないことがないかの確認はできました。

### メモ

* **CLAUDE.md** はプロジェクト用の永続的なシステムプロンプト。すべてのリクエストに含まれる
* **escape → /rewind** の使い方。Claudeが間違った方向に進んだ時、過去の会話履歴に戻ってやり直す。余計な情報をコンテキストに残さない
* **Hooksの種類**: PreToolUse, PostToolUse, Notification, Stop, SubagentStop, UserPromptSubmit, SessionStart, SessionEnd, PreCompact
* **Claude Code SDK** でプログラムからClaude Codeを実行できる（Gitフック、CI/CDでの品質チェック等）

## まとめ

3コースを受けてみて感じたところは、**「知ってるつもり」と「体系的に理解している」の差は思った以上に大きい**ということでした。

特にClaude 101の4Dフレームワークは、日々のAI活用を振り返るよいフレームワークになったと思います。各機能は、今後の使いたいなと思うきっかけになりました。

全コース無料でできるのがいいところと、私のようにざっくり理解で使ってしまう人にはこういう体系的に学べるものが向いていると思います。もしやるなら、Claude 101がおすすめです。

**受講サイト**: <https://anthropic.skilljar.com/>
