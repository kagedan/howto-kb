---
id: "2026-06-27-kurono-ai-ura-httpstco4a1knkdhcw-01"
title: "@kurono_ai_ura: https://t.co/4A1kNKdhcW"
url: "https://x.com/kurono_ai_ura/status/2070784842200170810"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/4A1kNKdhcW


--- Article ---
Claude Codeを使ってる人は増えた。でも9割の人は、まだ表面しか触れていません。

- 公式ドキュメントの片隅にしか載っていないコマンド
- ソースコードから見つかった環境変数
- 海外Redditで話題になったショートカット
**知ってる人だけが生産性10倍で回してる「裏側」が確実に存在します。**

AI×SNSでのマネタイズ7,000万、全自動で月300万円、Claude Code 2,000時間使い倒してきた僕が、公式が教えてくれない使い方を15個まとめて全部出します。

![](https://pbs.twimg.com/media/HLzmTCnbsAAcOVU.jpg)

> **AIエージェントでの稼ぎ方はこちら👇

[>> くろのの公式LIN**E](https://utage-system.com/line/open/29eSgDJcxiWv?mtid=YdgBFzRGGHTL)

この記事を読み終わる頃には、あなたのClaude Codeは別物になっています。

# 「Claude Code使ってる」だけじゃもう差がつかない時代

![](https://pbs.twimg.com/media/HLznWpZawAAhJQs.jpg)

2026年に入って、Xで「Claude Codeで〜した」という投稿が毎日何百と流れるようになりました。もう「使ってること」自体には何の希少性もありません。

## 9割のユーザーが基本コマンドしか使っていない事実

「/help」「/clear」くらいを知ってるだけで「使いこなしてる」と思ってる人が大半です。

**でもClaude Codeには、公式ドキュメントに載っていない機能が山ほどあります。**

 2026年3月にはnpmパッケージからソースコードが発見されて、330個以上の環境変数と32個のフィーチャーフラグが眠っていたことが判明しました。

## 差がつくのは「裏側」を知ってるかどうか

僕はClaude Codeを1,500時間以上触ってきました。AIエージェント100体以上を全自動で動かして、放置で月300万円の仕組みを回しています。

ここまで来れたのは、基本機能だけじゃなくて「裏側」を徹底的に掘ったからです。**GitHub Issues、Reddit、ソースコード、海外のブログ。** 全部漁って見つけた15個を、今日は全部出します。

> **AIエージェントでの稼ぎ方はこちら👇

[>> くろのの公式LIN**E](https://utage-system.com/line/open/29eSgDJcxiWv?mtid=YdgBFzRGGHTL)

# AIの思考深度を操る「ultrathink」と「ultracode」【①②③】

![](https://pbs.twimg.com/media/HLznb91bgAAoC-G.jpg)

Claude Codeには、AIの考える深さを自分でコントロールできる仕組みがあります。**これを知らずに使ってるのは、スポーツカーをずっとローギアで走らせてるのと同じです。**

## 「ultrathink」をプロンプトに入れるだけで思考が深くなる

プロンプトの中に「ultrathink」という単語をポンと入れるだけです。スラッシュコマンドじゃありません。ただの単語です。

これを入れると、AIが約32,000トークン分の思考を使って、回答する前にじっくり考えます。**通常の何倍も深い推論をしてから答えを出すので、設計判断やバグの根本原因特定の精度が段違いです。**

ただし、1回のターンだけに効きます。セッション全体の設定は変わりません。

## 「ultracode」はセッション全体を最強モードに切り替える

ultrathinkが「1回だけ深く考えて」なら、ultracodeは「このセッション全体を最高設定で回して」です。

**ultracodeをONにすると、effort levelがxhighに固定されて、さらにタスクを自動的にサブエージェントに分割・並列実行するワークフローモードが発動します。** 勝手に計画を立てて、勝手に分担して、勝手に完成させる。

ただしトークン消費はかなり重いです。ある人は「5時間分のトークンを18分で使い切った」と報告しています。

## /effortコマンドで思考深度を細かく調整する

日常的に使うなら「/effort」コマンドの方が便利です。**low、medium、high、xhigh、maxの5段階から選べます。**

- **low** — 簡単なファイル操作
