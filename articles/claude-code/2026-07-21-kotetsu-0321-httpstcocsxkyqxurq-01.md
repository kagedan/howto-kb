---
id: "2026-07-21-kotetsu-0321-httpstcocsxkyqxurq-01"
title: "@kotetsu_0321: https://t.co/cSXKYqxurq"
url: "https://x.com/kotetsu_0321/status/2079484098675126638"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "OpenAI", "x"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/cSXKYqxurq

公式URLはこちらから👇

📌https://t.co/r6aHhCcKd6
📍https://t.co/ZZ5FGnBhsu


--- Article ---
最近、AIエージェントを組み合わせて、一人でもチームや会社のように仕事を進める方法が広がっています。

**私もいくつか試してきましたが、その中で特に可能性を感じたのが「Hermes Agent」です。**

以前から名前は知っていたものの、正直なところ、「また新しいAIエージェントが出てきたのか」と後回しにしていました。ところが最近、改めて調べてみると、その進化の速さに驚かされました。

デスクトップアプリやWebダッシュボード、バックグラウンドで動くサブエージェント、複数のAIモデルを組み合わせるMixture of Agents、定期業務を自動化するAutomation Blueprintsなど、もはや単なるチャット型AIではありません。

さらに参考になったのが、Akshay Pachaar氏の[「Hermes Agent Masterclass」](https://x.com/akshay_pachaar/status/2054564519280804028)です。

単にAIへ役割を与えるだけでなく、それぞれに記憶やスキル、設定を持たせ、同じメンバーと継続して仕事をする。この考え方は、「一人チーム」や「一人会社」のような働き方とも相性がよさそうです。

> **本記事では、Akshay氏の記事を参考にしながら、最新のアップデートも反映し、Hermes Agentとは何か、どうインストールして仕事へ組み込むのかを、私自身の試行錯誤も交えながら解説します。**

---

# 1. Hermes Agentとは何か

Hermes Agentは、Nous Researchが開発しているオープンソースのAIエージェントです。

![](https://pbs.twimg.com/media/HNuFqDAaIAE8kaB.jpg)

ただし、「高性能なAIモデルが新しく一つ増えた」と考えると、少し分かりにくくなります。

**Hermes Agentは、特定のAIモデルそのものではありません。**

OpenAI、Anthropic、Google、OpenRouter、Nous Portal、ローカルモデルなどを利用しながら、記憶、ツール、スキル、自動化といった機能を組み合わせて仕事を進めるための基盤です。

![](https://pbs.twimg.com/media/HNuF_OqaEAA7iwL.jpg)

一般的なAIチャットでは、ユーザーが質問を送り、モデルが回答を返します。

Hermes Agentも会話はできますが、それだけではありません。

**必要に応じてターミナルを操作し、ファイルを読み、Webを検索し、ブラウザを使い、コードを実行します。複雑な仕事であれば、複数のサブエージェントへ分担させることもできます。**

具体的には次のような依頼が可能です。

> ・リポジトリを調査し、問題を修正してテストする 
・複数のニュースソースを調べ、出典付きのレポートを作る
・過去の会話から関連情報を探す 
・毎朝決まった時間にニュースを調査し、Telegramへ送る
・複雑な調査を複数のサブエージェントへ分担する 
・一度うまくいった作業手順をSkillとして保存する 
・Researcher、Writerなどを別々のエージェントとして運用する

ここまで聞くと、Claude CodeやCodexと同じ多機能なAIエージェントに見えます。

**ただ、Hermes Agentの本当の面白さは、機能の数ではありません。**

> **①仕事を通じて知ったことをMemory（自身の記憶）へ残す。
　→②うまくいった仕事の進め方をSkillとして定義する。
　　→③増えすぎたSkillsをCuratorで整理する。
　　　→④次に同じような仕事が来たとき、過去の経験を再利用する。
　　　　→また①に戻る**

これらが一つの循環としてつながっている点に、Hermes Agentの大きな特徴があります。

> **一言で表すなら、Hermes Agentは「使うほど、自分の仕事に合った形へ育っていくAIエージェント」です。**

ただし、ここで言う「育つ」という言葉には少し注意が必要です。

通常の使い方で、HermesがAIモデルの重みを自動的に再学習しているわけではありません。

**蓄積されるのは、主にユーザーの好み、プロジェクトの情報、過去の会話、仕事の手順、エージェントの設定です。**

人間そ
