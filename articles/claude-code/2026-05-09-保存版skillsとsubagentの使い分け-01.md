---
id: "2026-05-09-保存版skillsとsubagentの使い分け-01"
title: "【保存版】SkillsとSubAgentの使い分け"
url: "https://note.com/kawaidesign/n/ned8763550e00"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "Gemini"]
date_published: "2026-05-09"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

Claude CodeやCodexを使うなら、  
SkillsとSubAgentを混ぜて考えない方がいいです。

結論は単純です。

Skillsは再利用する手順。

SubAgentは分担する作業者です。

> この記事は**全文無料（期間限定）**で閲覧できます。

見出し画像はAIで生成しました。  
プロンプトはこの記事に掲載中。

## まず結論

![](https://assets.st-note.com/img/1778283633-qYUXeDJ5Vn0sdGjM92fahut7.png?width=1200)

正解は、Skillで標準化し、SubAgentで分業することです。

Claude Codeの公式ドキュメントでは、**Skills**は`SKILL.md`を中心に、指示、スクリプト、テンプレートなどをまとめる仕組みとして説明されています。

Codex公式でも、Skillsは再利用可能なワークフローの authoring format として整理されています。

一方、**SubAgent**は別コンテキストで動く専門担当です。

**Claude Code公式**では、Subagentは独自のcontext window、system prompt、tool権限を持つ専門AIアシスタントとして説明されています。

**Codex公式**では、複雑で並列化しやすい作業に対して、専門agentを並列spawnして結果を集約する仕組みと説明されています。

つまり、役割はこうです。

---

## 目次

* まず結論
* Skillsは「手順の再利用」
* SubAgentは「作業の分担」
* Claude CodeとCodexで違う点
* 実務判断チェックリスト
* いちばん強い組み合わせ
* 今日から直す設定

---

**【先着100名限定】Claude Codeデザインパターン**  
〜フォルダ構造・Skills・database・コンテンツ生成フロー全公開〜

## Skillsは「手順の再利用」

Skillsは、毎回同じ説明をプロンプトに貼っている作業を外出しする仕組みです。

たとえば、note記事を書くたびに「タイトルは32字以内」「定型文を入れる」「サムネプロンプトを作る」と指示しているなら、それはSkill向きです。

X投稿、PRレビュー、Figma実装、議事録整形、リリースノート作成も同じです。

Skill化すべき条件は3つあります。

* **作業手順が毎回ほぼ同じ**
* **参照ファイルやテンプレートがある**
* **出力形式を固定したい**

逆に、1回しか使わない作業をSkill化する必要はありません。

Skillは増やすほど便利になりますが、説明文が雑だと誤発火します。

「何をするSkillか」より「いつ使うSkillか」をdescriptionに書く方が重要です。

## SubAgentは「作業の分担」

SubAgentは、main agentから作業を切り出すための別担当です。

使う場面は、ノイズが多い作業です。

コード探索、ログ解析、テスト失敗の原因調査、PRレビュー、複数ファイルの影響確認。

こうした作業をmain会話に全部流すと、重要な要件や判断が埋もれます。

Codex公式は、この問題をcontext pollutionやcontext rotとして説明しています。

探索ログ、stack trace、テスト出力でmain contextが汚れると、後半の判断が落ちます。

SubAgentはこのノイズを別スレッドへ逃がし、要約だけmainへ戻すために使います。

SubAgent向きの条件は4つあります。

* **並列化できる**
* **調査ログが多い**
* **専門観点が分かれる**
* **main agentの判断材料だけ返してほしい**

反対に、次の一手がその結果に完全依存する作業はmain agentで処理した方が速いです。

SubAgentは便利ですが、各agentがモデルとtoolを使うため、単体実行よりトークンコストが増えます。

## Claude CodeとCodexで違う点

Claude CodeとCodexは、似た言葉を使いますが挙動が違います。

---

### Claude CodeのSkills

リクエスト内容とSkill descriptionが一致するとClaudeが自律的に使います。

Slash commandのようにユーザーが明示起動するものではなく、model-invokedです。

---

### Claude CodeのSubagent

説明文と一致すれば自動委任されます。

さらに`/agents`から作成でき、project単位とuser単位で保存できます。  
subagentごとにtool、model、system promptを変えられます。

---

### CodexのSkills

明示起動と暗黙起動の両方があります。

Codexは最初にSkillの名前、description、pathだけを軽く読み、必要になった時だけ`SKILL.md`全文を読みます。  
これはcontext節約に効きます。

---

### CodexのSubAgent

明示依頼が基本です。

公式ドキュメントでは、Codexはユーザーが明示的に依頼した場合だけsubagentをspawnすると説明されています。

「spawn two agents」「delegate this work in parallel」「use one agent per point」のように依頼する必要があります。

## 実務判断チェックリスト

![](https://assets.st-note.com/img/1778285092-V940EyKpvGkWzFg5cQ1JnM7P.png?width=1200)

迷ったら、次の順番で判断します。

最初に見るべき点は5つあります。

* **常時守らせたいルールか**
* **何度も使う手順か**
* **外部システム接続が必要か**
* **並列化できる作業か**
* **実行タイミングが決まっているか**

答えはこうなります。

* **常時守らせたいルール: AGENTS.md**
* **何度も使う手順: Skills**
* **外部システム接続: MCP**
* **並列化できる作業: SubAgent**
* **実行タイミング固定: Hooks**

この分類を外すと、運用が重くなります。

たとえば、毎回守る文体ルールをSkillに入れると、Skillが発火しない場面で崩れます。

逆に、note執筆のような成果物別ワークフローをAGENTS.mdに全部入れると、常時contextを圧迫します。

## いちばん強い組み合わせ

![](https://assets.st-note.com/img/1778283782-hMf9TCIgbOUzuyXEqKSFsLaJ.png?width=1200)

最強は、Skillで仕事の型を定義し、SubAgentで実行を分ける形です。

例を出します。

PRレビューなら、`code-review` Skillにレビュー基準、出力形式、禁止事項を書きます。

そのうえでSubAgentを3つに分けます。

* **security担当**
* **test gap担当**
* **maintainability担当**

main agentは3つの結果を受け取り、重要度順にまとめます。

これなら、レビュー基準は毎回同じで、調査だけ並列化できます。

note制作でも同じです。

`writer-note` Skillで記事構成、定型文、サムネ、図解、参照リンクのルールを固定します。

必要に応じて、別agentへ一次情報調査、過去記事検索、図解案作成を分けます。

Skillは標準化。

SubAgentは分業。

この2つを分けるだけで、AIエージェント運用の迷いがかなり消えます。

## 今日から直す設定

まずやることは、既存の指示を4つに仕分けることです。

今日見るべきファイルは4種類です。

* **AGENTS.md / CLAUDE.md**
* **skills配下のSKILL.md**
* **agents配下のcustom agent設定**
* **MCP / hooks設定**

仕分け基準は単純です。

常時ルールはAGENTS.mdへ置きます。  
成果物ごとの手順はSkillへ置きます。  
専門担当の人格や権限はSubAgentへ置きます。  
外部ツール接続はMCPへ置きます。

この整理をすると、プロンプトが短くなります。  
main会話も汚れにくくなります。  
そして、AIに任せる仕事の単価が下がります。

Claude CodeやCodexを使う目的は、AIに詳しくなることではありません。  
仕事の再現性を上げ、作業時間を減らし、判断を速くすることです。

そのための最小構成はこれです。

* **AGENTS.md: 会社の憲法**
* **Skills: 業務マニュアル**
* **SubAgent: 専門担当者**
* **MCP: 外部システム接続**
* **Hooks: 自動実行装置**

ここまで分ければ、あとは増やすだけではなく削る判断ができます。

ROIが低いSkillは消す。

並列化しても速くならないSubAgentは作らない。

毎回使うルールだけ残す。

これが、開発者がClaude CodeやCodexを実務に入れる時の現実解です。

---

【先着100名限定】Claude Codeデザインパターン  
〜フォルダ構造・Skills・database・コンテンツ生成フロー全公開〜

AI、デザイン、キャリアの個別相談はこちら

法人研修の無料相談・お問い合わせこちら

最大8名のグループコンサル

noteメンバーシップに参加すると800本以上の記事が読み放題です。

書籍「AIでゼロからデザイン」好評発売中

NewsPicks「実践！仕事術」

さらば森田のAI〇〇ラボ

ベイジTV（株式会社ベイジ 公式チャンネル）

San Francisco Design Talk（btrax Brandon氏のPodcast）

---

参照リンク

[#AI](https://note.com/hashtag/AI) [#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#AIエージェント](https://note.com/hashtag/AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88) [#AI時代](https://note.com/hashtag/AI%E6%99%82%E4%BB%A3) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#AI人材](https://note.com/hashtag/AI%E4%BA%BA%E6%9D%90) [#AI研修](https://note.com/hashtag/AI%E7%A0%94%E4%BF%AE) [#AIツール](https://note.com/hashtag/AI%E3%83%84%E3%83%BC%E3%83%AB) [#Claude](https://note.com/hashtag/Claude) [#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#Codex](https://note.com/hashtag/Codex) [#Gemini](https://note.com/hashtag/Gemini)
