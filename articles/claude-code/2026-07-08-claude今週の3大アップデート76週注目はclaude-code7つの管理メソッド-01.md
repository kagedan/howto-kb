---
id: "2026-07-08-claude今週の3大アップデート76週注目はclaude-code7つの管理メソッド-01"
title: "Claude：今週の3大アップデート（7/6週）〜注目はClaude Code「7つの管理メソッド」"
url: "https://note.com/quick_ferret9648/n/n2e86f48bc98e"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "note"]
date_published: "2026-07-08"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

＜ニュース概要＞  
今週のClaudeは「使い方を制御する」動きが目立ちました。Claude Codeの挙動を制御する7つの方法が公式に整理され、Slackで常駐する新しいAI相棒「Claude Tag」が登場、さらにClaude Desktopが主要クラウドで本格提供へ。個人が賢く使うフェーズから、組織で安全・低コストに運用するフェーズへと軸足が移りつつあります。

1.【注目】Claude Codeを制御する「7つの管理メソッド」が公式整理

Anthropicが、Claude Code（コーディング用のAIエージェント）の挙動を指示・制御する方法を7つに整理して公開しました。CLAUDE.mdファイル、ルール（Rules）、スキル（Skills）、サブエージェント（Subagents）、フック（Hooks）、出力スタイル（Output styles）、そしてシステムプロンプトへの追記の7つです。

ポイントは「どれを使うか」で、（1）いつコンテキストに読み込まれるか、（2）長い会話でも指示が消えずに残るか、（3）トークンをどれだけ消費するか、（4）指示としての強さ（守られやすさ）——の4つが変わることです。たとえばCLAUDE.mdは会話の最初から常に読み込まれるため確実に効く反面、毎回トークンを食います。スキルやサブエージェントは「必要なときだけ」中身が読み込まれるので低コスト。フックはAIの判断に任せず、コードとして機械的に必ず実行されるため、「毎回リンターをかける」「完了時にSlackへ通知する」「危険なコマンドをブロックする」といった“絶対に守らせたいこと”に向きます。

実務的な勘所は「『毎回必ずこうして』はCLAUDE.mdに書くのではなくフックにする」「30行の手順書はCLAUDE.mdではなくスキルにする」「特定フォルダだけのルールはパス指定で範囲を絞る」の3つ。指示を書く“場所”を選ぶだけで、トークンコストが下がり、かつ指示がきちんと守られるようになります。トークン浪費が問題になり始めた今、まさに効いてくる知識です。

出典：Claude公式ブログ・2026/6/18  
https://claude.com/ja/blog/steering-claude-code-skills-hooks-rules-subagents-and-more

2. Anthropic「Claude Tag」発表——Slackに常駐するAIチームメイト

Slack上で「@Claude」とタグするだけで、チームの一員のように動くAI相棒「Claude Tag」が登場しました。個人ごとの従来のSlackアプリを置き換え、チャンネル全体で共有する“持続型”のAIとして機能します。

特徴は、チャンネルの会話を追いかけて文脈を蓄積・記憶する点。プロジェクトを毎回ゼロから説明し直す必要がなく、非同期でタスクを自律的に進めます。さらに「ambient（アンビエント）モード」では、AIの側から自発的にチャットに入り、忘れられたタスクや他部署の動きをフォローしてくれます。まずはClaude Enterprise / Teamプラン向けにベータ提供で、Opus 4.8で稼働します。

出典：マイナビニュース・2026/6/24  
https://news.mynavi.jp/techplus/article/20260624-4621417/

3. Claude Desktopの企業向け提供が加速（主要クラウド対応）

Claude Desktopが、AWS・Google Cloud・Microsoft Foundryの主要クラウドから全機能を利用できるようになりました。自社が契約するクラウド環境内で実行できるため、データを外に出さずに使える点が企業にとって大きな安心材料です。

一方で、日本国内での利用は現状Amazon Bedrock経由が実質一択という状況。クラウド選定やデータガバナンスの方針とあわせて、どの経路で導入するかを検討するフェーズに入ってきました。

出典：Claude公式ブログ  
https://claude.com/blog/the-full-claude-desktop-experience-on-aws-google-cloud-and-microsoft-foundry
