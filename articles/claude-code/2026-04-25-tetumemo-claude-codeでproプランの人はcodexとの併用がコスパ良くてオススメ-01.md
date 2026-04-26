---
id: "2026-04-25-tetumemo-claude-codeでproプランの人はcodexとの併用がコスパ良くてオススメ-01"
title: "@tetumemo: 📝Claude CodeでProプランの人はcodexとの併用がコスパ良くてオススメ。特にGPT-5.5とGPT-Ima"
url: "https://x.com/tetumemo/status/2047974569055776851"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "GPT", "x"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-x"
---

📝Claude CodeでProプランの人はcodexとの併用がコスパ良くてオススメ。特にGPT-5.5とGPT-Image-2になって格段に用途が上がった

今日一日Claude Codeとcodexをリミットまで使いまくったから、非エンジニア目線で自分用気づきメモをシェアします！

・ClaudeのMAX100＄、200＄支払いは一般的にハードルが高い
・Claudeの20＄、ChatGPTの20＄はまだ許容範囲
・Claudeは文系、codexは理系なイメージ。特にGPT-5.5になってコーディングやタスクを”やり切る”チカラがグッとUPした。記事はClaudeに書かせるほうが良い
・codexはサブスク料金内でGPT-Image-2が使えるのが最高。Claude Codeのみでは画像生成できないから貴重
・今までClaude Code×Nano Banana 2で実施してたけど、codex×GPT-Image-2の方がクオリティ高くて良い
・Claude Code×Nano Banana はAPI料金かかるけど、codex×GPT-Image-2ならサブスク内でAPI料金不要
・Codex Appはなぜか音声入力アプリが内蔵されていて、Aqua Voice、Typelessのように使える
・Claude Codeとcodex、Skillsを共通して使える
・codexでDeep Researchして、Claudeで執筆
・codex×NotebookLMでDeep Researchして、Claudeで執筆
・Claude Codeで仕様を固めて、codexでコーディング
・codexはClaude Codeよりレート制限が緩和されている（使えるトークン量が多い）気がする

と、実際挙げればキリが無いので、近いうちに毎週発行しているニュースレターにまとめます

とにかくcodexはデスクトップアプリがメチャ優秀なので、ChatGPTに課金している人は絶対にダウンロードしたほうが良いですよ。音声入力無料で使えるしね

Codex Appなら音声入力が使えるから、Typeless、Aqua Voiceなど検討しているなら一度使ってみたほうが良い

https://t.co/00tiFSGSAi

GPT-5.5について

https://t.co/ffAMkLVWoI

📝毎週火曜日にAIに特化した実体験型ニュースレターを発行しています

無料で読めます　↓

https://t.co/ciBcp7XVmv

📝【発展編】Claude×NotebookLMにSkills5本入れたら別物になった。チート級のトークン削減ノウハウを全部シェアします

https://t.co/2j5W6wekXj


--- 引用元 @tetumemo ---
📝そう言えば、あまり知られてないけどかなり嬉しい情報

実は、codex上で画像生成できます！
ChatGPTの3,000円サブスク内でOK！API不要！

つまり、Claude Codeみたいにcodexで記事を書かせて、サムネまで作らせるワークフローが組めるってこと

裏技で、Claude Codeからcodex呼んで画像生成もできる https://t.co/LkqZn43CqX

こちらはGoogle Antigravity上でcodexの拡張機能から実行してみました https://t.co/atn311pmCQ
📝codexからGPT-Image-2でDIYの手順を作成

プロンプト
――――
以下のプロンプトで9:16の画像生成をして

# 画像生成AI向け設計書 (DIY 子供用木の椅子 インフォグラフィック)

# 1. 画像全体の定義
image_description:
  overall_prompt: |
    DIYで作る子供用のシンプルな木の椅子の作り方をステップバイステップで示す、ミニマルスタイルのインフォグラフィック。
    白い背景に、俯瞰視点で撮影された材料(カット済み木材パーツ)・道具の写真（ラベル付き）、分かりやすいアイコンと点線で繋がれた組み立て手順、最下部に完成した椅子の写真を配置する。
    DIY初心者や親子での工作にも分かりやすい、クリーンで温かみのあるデザイン。
  style:
    - 写真 (材料パーツ, 道具, 完成品 - 俯瞰視点)
    - シンプルな線画アイコン (組み立て手順)
    - ミニマルスタイル (Minimal style)
    - DIY / クラフト (Craft)
    - インフォグラフィック (Infographic)
  aspect_ratio: 縦長 (例: 9:16 or
