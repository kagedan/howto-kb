---
id: "2026-05-31-skillmd-の-linter-を自作する-公式仕様のどこを機械で検査できるか-01"
title: "SKILL.md の linter を自作する ── 公式仕様のどこを機械で検査できるか"
url: "https://zenn.dev/gudezou/articles/584336630493dc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

![サムネイル](https://static.zenn.studio/user-upload/16c7d1607659-20260531.png)

* 自作した `SKILL.md` が公式の書き方からずれても Claude Code は教えてくれないので、検査する道具 (linter) を自分で用意すると安心です
* 検査の多くは `description` の1024文字のような文字数や、`frontmatter` の型・決められた値の確認で自動で判定できます
* ERROR と WARN と INFO の深刻さで枠組みだけを機械検査し、description やシステムプロンプトの中身のレビューは別のスキルに任せるのが設計のキモです

---

## 自作 SKILL.md が公式の書き方から外れる典型パターン

`SKILL.md` の `frontmatter` には細かい決まりがあります。  
全体は公式の Skill authoring best practices ページにまとまっています。

* 必須項目
  + `name`
    - 64文字以内で、小文字と数字とハイフンだけが使えます
    - 予約語の `anthropic` と `claude` は `name` に入れられません
  + `description`
    - 1024文字以内で、三人称で「何をするか」と「いつ使うか」を書きます
    - `description` と `when_to_use` の合計が1536文字を超えると、一覧の表示で後ろが切り詰められます
* オプション項目
  + `effort` のように決められた値しか取れない欄に、別の値を書く崩れもよくあります
  + `disable-model-invocation` には true か false の真偽値だけを入れます
* その他の注意点
  + 同梱したスクリプトは固定パスではなく `${CLAUDE_SKILL_DIR}` で参照します
  + 本文に長い前置きを置いたり、不要な複数案を並べすぎたりするのも、公式が避けるようすすめる点です

![SKILL.md の frontmatter を上から検査するイメージ](https://static.zenn.studio/user-upload/7adb532098ae-20260531.png)

---

## 公式ルールを深刻さで仕分けて linter を組み立てる

この linter が調べるのは `frontmatter` という「枠組み」で、その大半は文字数・型・決められた値・正規表現で機械的に判定できます。  
公式ルールを深刻さで三つに分けると整理しやすいです。

### ERROR: 破ったら止める

* `name` と `description` があるか、文字数や `name` の文字種を満たすかは公式が必須とする項目です
* 必須を満たさないものは止める ERROR にして、その場で気づけるようにします

### WARN: 推奨なので注意

* `SKILL.md` 本体を500行以内に保つといった推奨 (Tips) は、破っても動くので注意をうながす WARN に下げます
* 固定パスではなく `${CLAUDE_SKILL_DIR}` で書くといった推奨も、この WARN に入ります

### INFO: 慣習レベルのアドバイス

* 公式違反ではなくコミュニティ内だけの慣習は、INFO の助言にとどめます
* 目次は一律に禁止せず、100行を超える参照ファイルには目次を付けることを公式がむしろ推奨しています

判定の作り方も分けて考えます。  
文字数・型・決められた値・正規表現で白黒つく部分は、誰が走らせても同じ結果になるので毎回の確認に向いています。  
この linter が受け持つのは、ここまでの機械で白黒つく検査だけにしぼります。

一方で `description` が三人称で書けているか、いつ使うかが伝わるか、システムプロンプトの中身が良いかどうかは、機械では測りきれません。  
こうした中身の良し悪しの判定は linter には持ち込まず、本文レビュー専用の別スキルに任せます。  
linter と本文レビュー専用のスキルで役割をはっきり分けておくと、それぞれが何をするのかがぶれません。

仕上げに、まとめて直す修正モードと、他の道具へ渡すための JSON 出力モードを用意すると運用に乗せやすくなります。  
完璧な linter をいきなり目指すより、一番効くルールから一つずつ足していくほうが無理がありません。

![公式ルールを ERROR・WARN・INFO に仕分けて検査する設計図](https://static.zenn.studio/user-upload/ef6443a815da-20260531.png)

---

## 参考文献

1. Anthropic. *Skill authoring best practices*. Anthropic Documentation. <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
2. Anthropic. *Extend Claude with skills*. Anthropic Documentation. <https://code.claude.com/docs/en/skills>
