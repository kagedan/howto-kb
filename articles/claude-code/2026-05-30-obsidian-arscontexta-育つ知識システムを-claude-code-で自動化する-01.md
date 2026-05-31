---
id: "2026-05-30-obsidian-arscontexta-育つ知識システムを-claude-code-で自動化する-01"
title: "Obsidian × arscontexta — 育つ知識システムを Claude Code で自動化する"
url: "https://zenn.dev/miyaken0805/articles/dae6219165e858"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "cowork"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

## はじめに

僕は最近メモツールにObsidianを導入し、そこに日々の気づき、生きていて感じたことなどを保存するようにしている。

一部のことはClaudeを使って、自動で保存し、Wikilinkで自動で繋がるようにもしていて、割と快適に使っている。  
<https://zenn.dev/miyaken0805/articles/ed70d88fa81c34>

ただ日々増え続けるメモの中には、削除するものもあるし、そうするとそれとリンクさせてたメモは繋がりを失う。  
箇条書きで残したinboxとかはWikilinkもない、つまりObsidian宇宙の外側にいるメモが、小惑星みたいに増え続けている。  
これは非常に勿体無いなと思い、なんとかしたくて色々調べていたら、今回の方法に辿り着いた。

書く習慣を強化するんじゃなくて、書いた後を仕組み化する。それが今回やったこと。

Claude Codeのプラグイン `arscontexta` を導入し、Cowork のローカルScheduledで日次自動メンテを組んだ。  
結果、自分が寝ている間（実際にはPCを起動している間だが）にvault内でノードが繋がり、孤立メモが拾われ、古いノートが新しい知識でアップデートされていく状態になった。

## 背景：書いても繋がらないノートの山

僕のObsidianの中には、自己分析・読書メモ・アイデア・Feliz.lab（僕の個人開発ブランド）の構想——色々入っている。  
<https://feliz-lab.com/?zenn>  
Claude Desktopで作ったものは、[上記の記事の方法](https://zenn.dev/miyaken0805/articles/ed70d88fa81c34)でリンクさせていたが、そうでないものはそれぞれが孤立している。  
ちょっとした気づきとかもClaudeに頼んでObsidianにすればとも思ったが、そういう時は大抵スマホからメモするものだ。  
ただObsidian MCPはあくまでローカルPCでしか動かないので、スマホのClaudeからではObsidianに接続できないのだ。

* 1週間前の気づきと、今日の気づきが繋がらない
* いらないメモだから削除したいけど、リンクの繋がりを汚してしまうから安易に消せない。
* せっかく書いた内容が、書いた瞬間しか効力を持たない

なので「ちゃんと繋がる仕組み」が欲しかった。

## arscontexta とは何か

arscontexta は、Claude Codeのプラグインとして提供される**個人ナレッジ管理のメソドロジー＋ツールセット**だ。

<https://github.com/agenticnotetaking/arscontexta>  
<https://www.arscontexta.org/>

ざっくり言うとこういうもの。

| 概要 | 詳細 |
| --- | --- |
| **思想** | Discovery-first — 書いたノートは「発見できる」必要がある |
| **コア概念** | キャプチャ → 振り返り → つなげる → 確かめる の4フェーズパイプライン |
| **提供されるもの** | スキル群（`/surface`, `/find-patterns`, `/revisit`, `/validate`, `/graph` など）+ テンプレ + 運用ルール |
| **やってくれる事** | 雑なメモを構造化、Wikilinkの自動付与、孤立ノートの検出、スキーマ検証、古いノートの再活性化 |

要するに「**ノートを書いた瞬間に、それが既存のグラフに自動で組み込まれる仕組み**」をClaude Code上に作るためのフレームワーク。

### スキル例

```
/surface         # inboxの素材から洞察を抽出
/find-patterns   # メモ間のつながりを発見
/check-resonance # 品質ゲートを実行
/validate        # スキーマ違反・壊れたWikilink検出
/graph orphans   # 孤立ノートを検出
/revisit         # 古いノートを新しい知識で更新
/next            # 今やるべきメンテを推奨
/rethink         # 蓄積したフリクションを構造的にレビュー
```

## 何が嬉しいか

導入してすぐに体感したメリット。

### 書いたら勝手に繋がる

新しいメモを `📥inbox/` に投げ込むだけ。`/surface` を走らせると、AIが既存ノートとの関連を発見してWikilinkを自動で貼ってくれる。  
これまで「これ、前にも似たこと書いた気がする…」を毎回検索する手間がこれだけで消える。

### 「書きっぱなし」が物理的に発生しない

`/validate` でスキーマ違反・リンク切れを検出、`/graph orphans` でどこにも繋がっていないノートを検出。これを**毎日自動で実行**するので、ノートが孤島化することがない。

## 実際にObsidianに導入した方法

### Step 1: Claude Code に arscontexta プラグインを入れる

Claude Codeのプラグインとして `arscontexta` をインストール。

```
/plugin marketplace add agenticnotetaking/arscontexta
/plugin install arscontexta@agenticnotetaking
```

### Step 2: `/setup` でセットアップ

Claude Codeをvaultディレクトリで開いて：

これだけで対話形式のセットアップが始まる。粒度、組織化方針、リンクルール、ナビゲーション階層、パーソナリティ、プラットフォーム——これらを質問されながら導出してくれる。

自分の場合の主な選択：

* **粒度**: moderate（1ジャーナル1ノート、1アイデア1ノート）
* **組織**: flat + ドメインフォルダ（既存の inbox/journal/ideas を継続）
* **リンク**: explicit+implicit（関連ノートは必ずWikilinkで繋ぐ）
* **ナビゲーション**: 3-tier（index → テーマmap → 個別ノート）
* **パーソナリティ**: warm + casual + emotionally-attentive（ジャーナル中心のvaultなので）

### Step 3: vault ルートに `CLAUDE.md` が生成される

これがシステム全体の理念・運用ルール・スキーマ定義を持つ「**Claude Code 用の唯一の情報源**」になる。Claude Codeが毎セッション最初に必ず読みにくる。

## Obsidian用に工夫したところ

ここからが個人的なカスタマイズの話。

### Feliz.lab だけサブフォルダで深く構造化

個人開発ブランドのFeliz.labは扱う領域が広いので、サブフォルダで切った。

```
🌼felizlab/
  apps/    # 各アプリの設計・アイデア
  sns/     # SNS運用・投稿企画
  note/    # Note記事の原稿
  dev/     # 技術・開発メモ
  brand/   # ブランディング・マーケティング
```

スキーマで `category` にenumを持たせて、自動仕分けが効くようにした。

### Claude Desktop と Claude Code の住み分け

今までの用途である、Claude Desktopからのメモ用に作ってた[Obsidian-Claude.md](https://zenn.dev/miyaken0805/articles/ed70d88fa81c34#obsidian-claude.md-%E3%81%AE%E5%BD%B9%E5%89%B2)は、`claude-desktop.md`と名前を変えて残し、Claude Code用は `CLAUDE.md` で完結させている。

両方が同じvaultを触っても矛盾しない設計にしてある。

### qmd でセマンティック検索を有効化した

arscontexta はデフォルトだとキーワード一致（BM25）でノートを探す。  
でも「ジャーナリング」と「日記」、「習慣」と「ルーティン」みたいに**同じ意味でも違う言葉を使っているケース**でつながりを見つけられない。

それを解決するのが `qmd`。意味ベクトルで検索できるようになる。

```
npm install -g @tobilu/qmd
```

インストール後、vaultディレクトリで：

```
qmd init
qmd collection add . --name "my-memos" --mask "**/*.md"
qmd update && qmd embed
```

これで `/find-patterns` の精度がぐっと上がる。「毎日の習慣」と「デイリールーティン」が別語彙でも同じクラスターに入るようになる。

### 日次メンテ用プロンプトを自作

`ops/daily-maintenance-prompt.md` を作って、毎日やるべきメンテ手順を1ファイルにまとめた。

ops/daily-maintenance-prompt.md

```
1. CLAUDE.md, ops/tasks.md, ops/reminders.md を読む
2. 📥inbox/ に何かあれば /ralph でバッチ処理
3. /validate でスキーマ・リンク健全性チェック
4. /graph orphans で孤立ノート発見＋接続
5. /revisit で古いノートを1〜3件アップデート
6. 結果を ops/sessions/ にログ出力
```

このプロンプトを次の運用フェーズで自動化する。

## 運用方法：Cowork でローカル日次自動化

「人間が毎日メンテを走らせる」前提だと結局続かないので、**完全自動化**したかった。

選択肢は2つあった。

|  | Claude Code Routines（クラウド） | Cowork Scheduled（ローカル） |
| --- | --- | --- |
| PC不要 | ✅ | ❌ |
| ローカルファイル直アクセス | ❌（GitHub経由） | ✅ |
| arscontexta スキル使用 | ❌ | ✅ |
| 設定の複雑さ | やや複雑 | シンプル |

Obsidian vaultはローカルファイルなので、**Cowork ローカル一択**だった。  
そうしないと、ローカルにしか保存されてない上記のスキルを回すことができないためだ。

### Cowork での設定手順

1. **Coworkで New Project** → 「Use existing folder」でvaultルートを指定
2. プロジェクト名を `arscontexta-daily` に
3. プロジェクト画面右の **Scheduled** セクションで「＋」
4. プロンプトに以下を貼る：

```
ops/daily-maintenance-prompt.md の内容に従って、Obsidian vault の日次メンテナンスを実行してください。

実行前に必ず CLAUDE.md を読んで知識システムの理念とパイプラインを理解してから着手してください。

完了したら ops/sessions/ に YYYY-MM-DD-daily-maintenance.md という名前で実行結果のサマリーを残してください。
```

5. **頻度**: daily、**時刻**: 普段確実にMacを開いている時間（10:00）
6. 初回は **Run now** で動作確認

## 今後

### 短期で考えていること

* **Note / Instagram 投稿ネタの自動抽出**：Journal、idea、knowledgeから「投稿候補」をピックアップする独自スキル

### 中長期

* **「気づき → 投稿 → 反応」までの循環を可視化**：書いた気づきが、どの投稿に繋がり、どんな反応を生んだかをvault内で追跡
* **Feliz.labプロダクトとナレッジを接続**：プロダクトのユーザーフィードバックも同じグラフに乗せて、アイデア → 実装 → 反響をひとつのループに

## まとめ

Obsidianは素晴らしいツールだ。でも、**「ノートを書く」と「ノートが育つ」は別問題**だと痛感していた。

arscontexta + Claude Code + Cowork で、その間にあった「人間の意志に依存する部分」を仕組みに置き換えることができた。

毎朝、vaultがメンテされ、孤立ノートが繋がり、古いノートが新しい知識でアップデートされていく。  
中々に気持ちのいい体験ができる仕組みはできたので、あとは日々メモを増やし続けてそれをアイデアとして、新しいアプリの開発やSNS投稿などのアウトプット活動に継続的に繋げていくだけだ。（それが一番難しいのだけど。。）

> 「努力してると言い切れるなら、今日の自分は失敗しても大丈夫」

Timeleszの松島聡さんがこんなことを言っていた。  
この仕組み作り、自分の中の「書きっぱなし、忘却の罪悪感」をだいぶ消してくれた。

「書くけど育たない」課題を持っている人に、ヒントになれば嬉しい。
