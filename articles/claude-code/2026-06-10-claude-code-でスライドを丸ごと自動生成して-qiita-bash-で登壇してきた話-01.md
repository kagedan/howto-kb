---
id: "2026-06-10-claude-code-でスライドを丸ごと自動生成して-qiita-bash-で登壇してきた話-01"
title: "Claude Code でスライドを丸ごと自動生成して Qiita Bash で登壇してきた話"
url: "https://qiita.com/kai_kou/items/822970e2f03786f0692c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "OpenAI", "Gemini"]
date_published: "2026-06-10"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

<!-- 元素材: kai-kou/kinako-mocchi PR #1503 (content/owner-articles/lt-2026-04-qiita-bash/qiita_article.md) -->

## はじめに

2026-04-28（火）に Qiita 株式会社（Increments）主催の **Qiita Bash「エンジニアリングとデザインをつなぐAI活用」** で LT 登壇させてもらいました。

会場 + YouTube Live のハイブリッド開催で、申込数は会場 40 名・配信 428 名・LT 登壇 5 名の合計 473 名というテック系 LT としては嬉しい規模になりました。

LT のタイトルは

> **「エンジニアがAI活用してスライドデザインできる世界が来たよ！」**

5 分という短い時間で、**Claude Code + Gemini API + python-pptx** を組み合わせてスライドそのものを丸ごと自動生成したワークフローを共有してきました。本記事はその振り返りと、当日に話しきれなかった技術詳細のメモです。

- 登壇スライド: https://speakerdeck.com/kaikou/enziniagaaihuo-yong-sitesuraidodezaindekirushi-jie-galai-tayo
- スライド制作リポジトリ（OSS / MIT）: https://github.com/kai-kou/qiita-bash-lt-2026
- イベント概要: https://increments.connpass.com/event/387592/

> 本記事は個人活動として書いています。所属企業の業務とは無関係です。

## 背景：「PPTX なら誰でも作れる」の一歩先

PPTX の世界では、PowerPoint や Google Slides で誰でもスライドを作れるようになりました。ただ「絵心ないけどイラスト入りのスライドにしたい」「世界観を統一したい」という壁は依然として大きく、実装系エンジニアにとってはここがネックになりがちです。

> Figma 系・UI 生成系の LT は同枠で複数ありましたが、私のテーマは「**スライド制作領域 × オリジナルキャラ世界観 × エンジニア視点のワークフロー全体**」というニッチに振り切ってみました。

## ワークフロー全体像

スライド制作を 5 フェーズに分割し、各フェーズの境界で **doc-review スキル** による 7 軸並列レビューを挟む構成にしました。

```
1. 要件定義（YAML）
   ↓ doc-review（7 軸並列レビュー）
2. 原稿（Markdown）
   ↓ doc-review
3. テキスト版 PPTX（python-pptx）
   ↓ doc-review
4. 画像版 PPTX（Gemini 3.1 Flash Image / GPT-IMAGE-2 で背景・キャラ生成）
   ↓ doc-review
5. まとめ（グラレコ風 1 枚画像）
```

ポイントは **「画像版」を最初から作らない** ことです。テキスト版で構成・文章を確定させてから画像差し替えに入ることで、画像の作り直しコストが激減します。

## 使用スタック

| 領域 | ツール |
|------|--------|
| オーケストレーター | Claude Code（メインセッション + サブエージェント並列） |
| PPTX 生成 | python-pptx（ファイル名・スライド構成は MD から動的生成） |
| キャラ画像 | OpenAI GPT-IMAGE-2（一貫性を維持したいキャラの立ち絵） |
| 背景・補足画像 | Gemini 3.1 Flash Image Preview（テキスト描画と reference_image_base64 が強い） |
| レビュー | `doc-review` スキル（自作・7 軸の Sub-Agent を並列起動） |
| スライド生成 | `slides` スキル（Markdown → テキスト版 PPTX） |
| インフォグラフィック | `infographic` スキル（最終まとめスライドの 1 枚画像化） |

## 7 軸並列レビュー（doc-review）

doc-review スキルは要件定義 → 原稿 → PPTX のそれぞれの段階で、7 つの観点をサブエージェントで **並列実行** します。

- ストーリー一貫性
- 用語統一
- 過剰な専門用語のカジュアル化
- スライド枚数バランス
- グラフィカルアセット重複チェック
- 画像生成プロンプトの再現性
- ファクトチェック（数字・出典）

並列に走らせることでレビューが 1 回 30〜60 秒で終わるので、フェーズ移行のたびに走らせても全体ワークフローのオーバーヘッドにはなりません。

## 自己証明としての OSS 公開

LT 自体のスライド制作リポジトリそのものを OSS として公開しています。

- https://github.com/kai-kou/qiita-bash-lt-2026

「AI でスライド制作」というテーマを、そのスライドを生成する過程ごと公開することで自己証明する形です。`.claude/skills/` 配下のスキル群・要件定義・出力物すべてを再現できる構成にしました。

## まとめと所感

- LT 5 分は短いですが、**「絵心がなくても世界観を保ったスライドが作れる」** というメッセージは伝えられた手応えがあります
- ワークフロー設計のキモは **「画像差し替えの後置」** と **「フェーズ境界の並列レビュー」**
- doc-review・slides・infographic の各スキルは個別利用も可能なので、興味のあるかたはリポジトリを覗いてみてください
- アーカイブが Qiita Bash の YouTube に上がる予定なので、当日参加できなかったかたはそちらもどうぞ

## 個人として応援している YouTube チャンネル

最後に余談です。スライド内のキャラクターたち（ハムスターのもっちーとセキセイインコのきなこ）は、**個人的に応援している YouTube テック解説チャンネル「きなこもっちーのテック深掘り」** のキャラクターを今回のスライドにも登場させてもらいました。

- チャンネル URL: https://www.youtube.com/channel/UCZ77dCrW-xkLKGQ2PCDqiEQ

AI / LLM 中心のテック解説を週 2 本のペースで配信しているチャンネルで、今回 LT で紹介したような Claude Code 活用や Gemini API 周りの話題も扱っています。LT 配信を見て興味を持ってくれたかたがいたら、よかったら覗いてみてください。

最後まで読んでいただきありがとうございました。LT のフィードバックや感想は X（@k_aik_ou）か Qiita のコメント欄で気軽にどうぞ。
