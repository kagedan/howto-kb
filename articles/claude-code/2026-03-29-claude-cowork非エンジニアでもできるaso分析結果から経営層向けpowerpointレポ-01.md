---
id: "2026-03-29-claude-cowork非エンジニアでもできるaso分析結果から経営層向けpowerpointレポ-01"
title: "【Claude Cowork】非エンジニアでもできる、ASO分析結果から経営層向けPowerPointレポートを自動生成する"
url: "https://qiita.com/4q_sano/items/abfb4c094b2d6bf7ced4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "Gemini", "cowork", "qiita"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

[![Gemini_Generated_Image_h27r4ch27r4ch27r.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2F5e8c3306-cb2c-420e-ad8c-6012d723d155.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=29337361ed5367deb361e29ba5a7020a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2F5e8c3306-cb2c-420e-ad8c-6012d723d155.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=29337361ed5367deb361e29ba5a7020a)

> この記事は、AIエージェント4体が連携してASO業務を自動化する「claude-code-aso-skill」を段階的に理解していくシリーズの第3弾です。  
> 第3弾では、「claude-code-aso-skill」で生成した分析結果をClaude Coworkで読み込み、PowerPoint資料として活用する流れを整理します。
>
> 第2弾はこちら：  
> [【第2弾】AIエージェント4体が連携してASO業務を自動化する「claude-code-aso-skill」でASO分析を実践してみたら便利すぎた](https://qiita.com/4q_sano/items/91f246e790c25f30ac41)

## はじめに

[前回の記事](https://qiita.com/4q_sano/items/91f246e790c25f30ac41)で、Claude Code上で動作するASO自動化フレームワーク「[claude-code-aso-skill](https://github.com/alirezarezvani/claude-code-aso-skill)」を紹介しました。

claude-code-aso-skillを実行すると、キーワード調査やメタデータ、ローンチ計画などが `outputs` フォルダに一括生成されます。ただ、これらは個別のMarkdownファイルなので、**経営層への報告や社内共有にはそのまま使いづらい**という課題があります。

そこで活用するのが **Claude Cowork** です。Claude Coworkを使えば、outputsフォルダの成果物を読み込んで、経営層向けのPowerPointレポートをコマンドライン不要で自動生成できます。

この記事では、その手順をスクリーンショット付きで解説します。

### Claude Coworkとは

Claude CoworkはAnthropicが提供するデスクトップツールで、非開発者でもファイルやタスクの管理を自動化できるツールです。現在リサーチプレビュー版として提供されています。ターミナルやコマンドラインを使わず、GUIの操作だけでClaudeにファイルの読み書きを任せられるのが特徴です。

## 前提条件

* **Claude Cowork**がインストール済みであること（Claudeデスクトップアプリに含まれています）
* **claude-code-aso-skillの実行済みoutputsフォルダ**があること

outputsフォルダの中身は以下のような構成です。

```
outputs/[アプリ名]/
├── 00-MASTER-ACTION-PLAN.md
├── 01-research/
├── 02-metadata/
├── 03-testing/
├── 04-launch/
├── 05-optimization/
└── FINAL-REPORT.md
```

## 手順

### Step 1: Claude Coworkを開き、outputsフォルダを指定する

Claudeデスクトップアプリの上部タブから **「Cowork」** を選択します。

[![Claude Coworkタブの選択](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2F80c09618-15c7-4356-a3f6-8f1aebc89f53.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6781976a13a6de34787262ad8ed58cb0)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2F80c09618-15c7-4356-a3f6-8f1aebc89f53.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6781976a13a6de34787262ad8ed58cb0)

画面下部の「プロジェクトで作業」をクリックすると、「フォルダを選択」と「プロジェクト」の選択肢が表示されます。**「フォルダを選択」** からASO分析結果が格納されている `outputs` フォルダを指定してください。

### Step 2: ファイルアクセスを許可する

Claude Coworkがoutputsフォルダ内のファイルを読み込み・書き込みするための許可を求めるダイアログが表示されます。

[![ファイルアクセス許可ダイアログ](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2F5895bf14-b10c-4ba5-86b6-8d0cc0295d12.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2a9a9a8d66c69ee3c523165ac3489a90)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2F5895bf14-b10c-4ba5-86b6-8d0cc0295d12.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2a9a9a8d66c69ee3c523165ac3489a90)

内容を確認し、**「許可」** をクリックしてください。「常に許可」を選ぶと、以降同じフォルダへのアクセス時にダイアログが表示されなくなります。

> **補足**: ダイアログにある通り、Claudeはファイルの読み取り・編集・削除が可能で、接続するサードパーティツールとファイル内容を共有する場合があります。機密情報を含むフォルダを指定する際はご注意ください。

### Step 3: レポート作成のプロンプトを入力する

フォルダを指定したら、入力欄にレポートの要件を記述します。今回は以下のように指示しました。

```
outputsフォルダを読み込み、
経営層向けのASO戦略レポートを作成してください。
以下の構成で資料化してください：
1. エグゼクティブサマリー
2. ASOスコアと現状評価
3. 主要な課題（上位5つ）
4. キーワード戦略と競合差分
5. フェーズ別実行計画（Research〜Optimization）
6. 優先施策（インパクト×実行難易度）
7. KPIと改善サイクル
制約：
・20スライド以内
・図解ベースで簡潔に
・意思決定に使える粒度
・PowerPoint形式で出力
```

[![プロンプト入力画面](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2Fa043d6d8-2074-4cf0-b1f8-931386152a40.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ed5bbb0de419ff0646361a6dd703cf25)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2Fa043d6d8-2074-4cf0-b1f8-931386152a40.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ed5bbb0de419ff0646361a6dd703cf25)

ポイントは、**出力形式（PowerPoint）、スライド数の上限、構成、粒度**を明確に指定することです。曖昧な指示だと汎用的なレポートになりがちなので、「経営層向け」「意思決定に使える粒度」といった目的を伝えると、内容の取捨選択が適切になります。

入力が完了したら **「始めましょう →」** ボタンをクリックします。

### Step 4: レポートが自動生成される

Claude Coworkがoutputsフォルダ内の18ファイルを読み込み、内容を統合してPowerPointレポートを生成します。

[![生成完了画面](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2Fa73f22ce-c2b4-42c1-8e63-844505364f14.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=802003b45531bb80a67f5c1968599efe)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2Fa73f22ce-c2b4-42c1-8e63-844505364f14.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=802003b45531bb80a67f5c1968599efe)

今回の実行では、全19スライドのレポートが生成されました。スライド構成は以下の通りです。

| スライド | 内容 |
| --- | --- |
| 1 | タイトル |
| 2 | エグゼクティブサマリー（40KW・10競合・8ギャップ・7テスト） |
| 3 | ASOスコア現状評価（45/100、競合比較バー） |
| 4 | 主要課題TOP 5（CRITICAL〜MEDIUM） |
| 5 | キーワード戦略（4カテゴリ＋最重要KW表） |
| 6 | キーワード優先度マトリクス（検索Vol×競合度） |
| 7 | 競合差分分析（8つの機会を2×4グリッド） |
| 8 | 競合キーワード比較（6社横断テーブル） |
| 9 | メタデータBefore/After（Apple・Google） |
| 10 | 競合ポジショニングマップ |
| 11 | フェーズ別実行計画（概要） |
| 12 | Phase 0-2 詳細（Research→メタデータ→ビジュアル） |
| 13 | Phase 3-6 詳細（テスト→リリース→最適化） |
| 14 | マイルストーンカレンダー＋工数見積り |
| 15 | 優先施策マトリクス（インパクト×実行難易度） |
| 16 | KPI（短期・中期・長期目標） |
| 17 | 改善サイクル（日次〜年次のPDCA） |
| 18 | リスクと対策 |
| 19 | Next Steps |

カラーパレットはダークネイビー基調のエグゼクティブ向けデザインで、図解・チャート・マトリクスを中心に構成されています。

### Step 5: 生成されたファイルを確認する

outputsフォルダを開くと、既存のASO成果物に加えて **`ASO-Strategy-Report.pptx`** が生成されています。

[![outputsフォルダの中身](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2F82591ae3-1727-4f51-a507-af4c3d2b41b3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ac0fdfc6b1b40684abd227c9c78d04d4)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2F82591ae3-1727-4f51-a507-af4c3d2b41b3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ac0fdfc6b1b40684abd227c9c78d04d4)

[![Gemini_Generated_Image_g83sg3g83sg3g83s.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2Fe2e29f96-f44e-4149-9a20-ee287af33844.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=59fab8dc96ccde11f2c63f4dcfed6051)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F82835%2Fe2e29f96-f44e-4149-9a20-ee287af33844.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=59fab8dc96ccde11f2c63f4dcfed6051)

このPPTXファイルをMicrosoft PowerPointやGoogle スライドで開けば、すぐにプレゼンテーションとして使用できます。

## プロンプトのカスタマイズ例

同じoutputsフォルダから、目的に応じて異なるレポートを生成できます。プロンプトを変えるだけで対応可能です。

### マーケティングチーム向けの詳細レポート

```
outputsフォルダを読み込み、
マーケティングチーム向けのASO実行計画書を作成してください。
キーワードの実装手順、A/Bテスト計画、
週次のタスクスケジュールを中心に、
実務担当者がそのまま作業に取りかかれる粒度で資料化してください。
PowerPoint形式、30スライド以内。
```

### 週次進捗レポート

```
outputsフォルダを読み込み、
ASO施策の週次進捗レポートを作成してください。
今週の実施事項、KPI推移、来週のアクションアイテムの3部構成で、
10スライド以内にまとめてください。
PowerPoint形式で出力。
```

### 競合分析に絞った報告資料

```
outputsフォルダの01-research/を重点的に読み込み、
競合分析レポートを作成してください。
競合6社のポジショニングマップ、キーワード比較、
差別化機会の優先順位を中心に構成してください。
PowerPoint形式、15スライド以内。
```

## まとめ

この記事で紹介したワークフローをまとめると、以下のようになります。

**claude-code-aso-skill**（Claude Code CLI）でASO分析を実行し、outputsフォルダに成果物を生成。その成果物を**Claude Cowork**に読み込ませて、経営層向けのPowerPointレポートを自動生成する。この2つを組み合わせることで、**ASO分析からレポーティングまでの一連の流れがAIで完結**します。

特にClaude CoworkはGUI操作だけで使えるため、開発者がclaude-code-aso-skillでASO分析を回し、マーケティング担当者がClaude Coworkでレポートを作成するという**チーム分業**にも適しています。

プロンプトを変えれば同じデータから異なる切り口のレポートを何度でも作れるので、報告先や目的に応じた資料作成の手間が大幅に削減できるはずです。

## 関連記事

## 関連記事

本記事は、AIエージェント4体が連携してASO業務を自動化する「claude-code-aso-skill」を段階的に理解していくシリーズの一部です。

> **この記事が参考になったら、LGTMをお願いします！** 👍
