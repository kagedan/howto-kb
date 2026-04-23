---
id: "2026-03-24-claude-sonnet-46-vs-opus-46週次記事生成の速度品質を実測比較し2モデル直列-01"
title: "Claude Sonnet 4.6 vs Opus 4.6：週次記事生成の速度・品質を実測比較し、2モデル直列運用に落ち着いた話"
url: "https://qiita.com/rehab-datascience/items/84bfb4f80ea4f0f1983f"
source: "qiita"
category: "antigravity"
tags: ["Gemini", "antigravity", "qiita"]
date_published: "2026-03-24"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

[![2026-03-24_qiita.PNG](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4172153%2F10abef34-a3cb-4436-b4a7-9b80bc85db83.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5877dbb3f756b6fb32acd367e2bc02ea)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4172153%2F10abef34-a3cb-4436-b4a7-9b80bc85db83.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5877dbb3f756b6fb32acd367e2bc02ea)

## 3行まとめ

* Claude Sonnet 4.6とClaude Opus 4.6で**同一の週次記事生成タスクを実行**し、速度と品質を定量的に比較した
* 第三者モデル（Gemini）によるクロスレビューで\*\*「速度はSonnet、品質はOpus」\*\*が確認された
* 最終的に\*\*「Sonnetでドラフト→Opusで最終調整」の2モデル直列運用\*\*に落ち着いた

---

## 背景

AIエージェント（AntiGravity）に定義した `create_articles` スキルで、毎週1週間分の記事を一括生成しています。

これまでClaude Opus 4.6を主に使っていましたが、レート制限の都合でClaude Sonnet 4.6に切り替える機会があり、「実際どれくらい差があるのか」を比較することにしました。

### 実行環境

* AIエージェント: AntiGravity（Google社製）
* スキル: `create_articles`（週次記事生成バッチ）
* 入力: Obsidianの `daily_log/` フォルダ内7日分のMarkdownファイル
* 出力: note記事7本 + Qiita記事0〜2本 + Discord投稿3本 + X投稿ファイル

---

## 検証1：速度比較

同一のログデータ・同一のスキル定義で、それぞれのモデルに記事生成を実行させました。

### 計測結果

| 項目 | Claude Sonnet 4.6 | Claude Opus 4.6 |
| --- | --- | --- |
| 総所要時間 | 約15〜20分 | 約30分 |
| ユーザー入力回数 | 少ない（まとめて処理） | 多い（段階ごとに追加入力） |
| コマンド承認 | 手動クリック必要 | 手動クリック必要 |

### 差が生まれた要因

Sonnetは、タイトル一覧出力→記事本体→Discord投稿文までを**一括で連続処理**する傾向がありました。

一方Opusでは、タイトル確認→「前半をお願いします」→「後半をお願いします」と**ユーザーの追加入力を都度待つ**挙動でした。

**補足**: コマンド承認（ファイル保存等）は両モデルとも手動クリックが必要です。完全放置でのバッチ実行はどちらも不可でした。

---

## 検証2：品質比較（Geminiクロスレビュー）

### 方法

1. Sonnet版の記事群（note 7本 + Qiita + Discord）をZip化
2. Opus版の記事群（別週のもの、Qiita記事含む）をZip化
3. 両方をGeminiに渡し、「記事としてどちらが優れているか、理由とともに比較してほしい」と依頼

### レビュー結果

Geminiの判定：**記事としてはClaude Opus 4.6の方が優秀**

| 評価軸 | Claude Sonnet 4.6 | Claude Opus 4.6 |
| --- | --- | --- |
| 要約力 | ◎ | ◎ |
| 整理力 | ◎ | ◎ |
| 文体の自然さ | △（事務的・機械的） | ◎（人間味がある） |
| 感情表現 | △（少ない） | ◎（心理面の描写が自然） |
| 読者への訴えかけ | △ | ◎ |

### 考察

* Sonnetの出力は「報告文」「技術文書」に近い印象
* Opusの出力は「エッセイ」「体験記」に近い印象
* note記事のような「読ませる文章」にはOpusの方が向いている

---

## 解決策：2モデル直列運用

速度と品質のトレードオフを解消するため、以下のフローを確立しました。

### 運用フロー

```
Step 1: Claude Sonnet 4.6 でドラフトを高速生成
  ↓
Step 2: Claude Opus 4.6 で言い回し・見出し・タイトルを最終調整
  ↓
Step 3: 最終確認・保存
```

### 実装上のポイント

* Opusのレート制限を想定し、**Step 2 のプロンプトを事前に慎重に組み立てておく**
* Step 2 は「全体のトーンはそのままに、Opusらしい自然な言い回しにブラッシュアップして」という指示で統一
* レート制限に到達した場合は、**Sonnet版をそのまま採用**するフォールバック

### 結果

タイトル・小見出し・本文のニュアンスが、より自然で柔らかい形に整えられました。

---

## 再現手順

### 環境

* AIエージェント: AntiGravity
* ノート管理: Obsidian
* スキル定義: `.agent/skills/create_articles/SKILL.md`

### 手順

1. `create_articles` スキルをClaude Sonnet 4.6で実行（ドラフト生成）
2. 生成された記事をClaude Opus 4.6に渡し、言い回しのリライトを依頼
3. プロンプト例:

```
以下の記事群について、全体のトーンはそのままに、
より自然で人間味のある言い回しにブラッシュアップしてください。
特にタイトル・小見出し・感情表現に注目して修正してください。
```

1. Opus版の出力で既存ファイルを上書き保存

---

## まとめ

| 観点 | 結論 |
| --- | --- |
| 速度重視 | Claude Sonnet 4.6 単体で完結（約15〜20分） |
| 品質重視 | Claude Opus 4.6 単体で生成（約30分） |
| バランス重視 | **Sonnet→Opus直列運用**（約20〜25分 + Opus調整） |
| レート制限時 | Sonnet版をそのまま採用 |

* 「どっちが上」ではなく、**その週の状況に応じて選ぶ**運用が最も実用的
* 品質比較は**第三者モデルにクロスレビューさせる**方法が客観的で有効

**運用Tips**: Opus 4.6のレート制限は週単位でリセットされます。記事生成の本番投入は「リセット直後のタイミング」を狙うと、1回で最大限使い切れます。
