---
id: "2026-06-20-完全版claude-code-claude-designでデザイン制作を変える全手順-01"
title: "【完全版】Claude Code / Claude Designでデザイン制作を変える全手順"
url: "https://note.com/kawaidesign/n/n1fea02814b7a"
source: "note"
category: "claude-code"
tags: ["claude-code", "MCP", "note"]
date_published: "2026-06-20"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

Claude CodeやClaude Designが出てきて、デザイン制作の境界線が一気に変わっています。

ただし、変わるのは**「デザイナーが不要になる」**という話ではありません。

変わるのは、サムネイル、バナー、SNS広告、スライド、Webサイト、アプリUI、アイコン、ロゴマークを作る時の、**考え方、作り方、検証方法、チーム分業**です。

この記事では、**Claude Code / Claude Design**をデザイン制作の実務へ落とし込みます。

読み終わると、ノンデザイナーは**「どこまで自分で作れるか」**、プロデザイナーは**「どこをAI化し、どこで価値を出すか」**が分かります。

---

見出し画像はAIで生成しました。  
プロンプトは120,000文字超えの記事に掲載中。  
毎日プロンプトは増えていきます。

---

## 目次

## 結論

![](https://assets.st-note.com/img/1781912439-8r4AOyBXShQUoPMLqKYbnJfp.png?width=1200)

Claude Code / Claude Design時代に、デザインする人が覚えるべきことは3つです。

---

1つ目は、AIに「作って」と言う力ではなく、AIに**「何を守って、どの基準で直すか」**を渡す力です。

---

2つ目は、**Claude DesignとClaude Codeを分けて使うこと**です。

Claude Designは、デザイン案、資料、プロトタイプ、マーケ素材、ブランドに沿った初稿作りに向いています。

Claude Codeは、Webサイト、アプリUI、実装、検証、量産、レビュー、自動化に向いています。

---

3つ目は、人間の役割を**「手作業」**から**「判断基準の設計」**へ移すことです。

AIは手を速くします。

ただし、目的、顧客、ブランド、文字の強さ、余白、視線誘導、情報設計、権利、実装品質までは、人間が締める必要があります。

特にデザイン領域では、次の分担が現実的です。

![](https://assets.st-note.com/img/1781912734-b6OdWjMivlYCwU4fIAuP0KqQ.png?width=1200)

一番危険なのは、Claudeに「いい感じにして」と投げることです。

一番強い使い方は、Claudeへ**「目的、読者、制約、ブランド、成功条件、失格条件、検証方法」を渡すこと**です。

## まず押さえる最新情報

![](https://assets.st-note.com/img/1781912752-hOHcK4XrpTE7098Bye2SGdwN.png?width=1200)

2026年6月20日時点で、Claude CodeとClaude Design周辺は**「チャットで相談するAI」**から**「制作物を作り、直し、実装し、接続するAI」**へ移っています。

重要な公式情報だけ先に整理します。

---

### Claude Codeは開発環境全体へ広がった

Anthropic公式docsでは、Claude Codeは**「コードベースを読み、ファイルを編集し、コマンドを実行し、開発ツールと統合するエージェント型コーディングツール**」と説明されています。

利用面もターミナルだけではありません。

公式docs上では、ターミナル、VS Code、デスクトップアプリ、Web、JetBrainsで使えることが示されています。

これはデザイナーにも関係があります。

なぜなら、WebサイトやアプリUIは、最終的に**コード、コンポーネント、CSS、レスポンシブ、動作確認へ落ちるから**です。

デザインがFigmaや画像で止まらず、実装と検証まで一気通貫になるほど、Claude Codeの価値が出ます。

Claude Code公式ページでは、コードベースの理解、複数ファイル編集、テスト、GitHub/GitLab連携、CLIツール、MCPサーバー連携が説明されています。

同じページでは、VS Code、JetBrains、Web、Slack、デスクトップなど、作業場所に合わせた利用も整理されています。

---

### Claude Designは「デザイン初稿」と「ブランド反映」のbeta

Claude Design公式ページでは、Claude Designは、デザイン、デッキ、プロトタイプなどのオンブランドなビジュアルワークをClaudeと共同制作するAnthropicのbeta製品と説明されています。

対象は、**プロトタイプ、ワイヤーフレーム、モックアップ、デザイン探索、ピッチデッキ、マーケティング素材、ドキュメント**です。

公式ページでは、GitHub、デザインファイル、ローカルコードベースからデザインシステムを読み込み、自社のコンポーネントに沿った出力を作れるとされています。

さらに、Claude DesignとClaude Codeの往復も明記されています。

Claude Codeから**`/design-sync`**でデザインシステムを取り込む、またはClaude Code上で`/design`を使う導線です。

ここが重要です。

Claude Designは「ノンデザイナーが何でも作るツール」ではありません。

**「ブランドやデザインシステムを読み込ませ、最初の方向性を出し、人間が直し、Claude Codeや外部ツールへ渡すための制作キャンバス**」です。

---

### Claude DesignはAdobe、Canva、Gamma、Lovable、Miro、Replit、Vercel、Wixへ接続する

Claude Design公式FAQでは、コードベース、Webキャプチャ、DOCX、PPTX、XLSXを取り込めることが示されています。

出力はPPTX、PDF、HTML、組織内共有リンク、Claude Codeへのハンドオフ、外部アプリ連携です。

公式ページでは、接続先としてAdobe、Base44、Canva、Gamma、Lovable、Miro、Replit、Vercel、Wixが挙げられています。

これは制作現場にかなり大きい変化です。

なぜなら、Claude内で作ったラフを、資料化、LP化、アプリ化、キャンペーン素材化へ動かしやすくなるからです。

---

### Claude Connectorsはデザイン用途も増えている

Claude公式のConnectorsページでは、MCPを通じてClaudeをツール、データベース、アプリへ接続できると説明されています。

カテゴリにはDesignがあり、Adobe for creativityのようなデザイン向けコネクタも掲載されています。

Connectorsは、デザイン制作では**「Claudeに外部ツールの文脈を持たせる仕組み」**です。

**Adobe、Canva、Figma、Miro、Notion、Google Drive、Slack**などをつなぐほど、Claudeはただの文章AIではなく、制作工程の中に入ってきます。

---

### Skillsは「自社デザインルール」をClaudeへ持たせる仕組み

Claude公式Skillsページでは、Skillsは組織の知識や個人のワークフローをパッケージ化し、一貫した結果を出すために使うものと説明されています。

会社固有のスキル例として、ブランドガイドラインや好みのフォーマットを適用する使い方も挙げられています。

デザイン制作では、Skillsはかなり重要です。

毎回**「このブランドはこういうトーンで、余白はこうで、文字量はこうで、NG表現はこう」**と説明していると、プロンプトが長くなります。

それをSkill化しておけば、Claude DesignでもClaude Codeでも、制作の前提を読み込ませやすくなります。

## Claude DesignとClaude Codeの役割

![](https://assets.st-note.com/img/1781913129-ZgucDsoKadyfVI3T0bMmkvN5.png?width=1200)

まず、**Claude DesignとClaude Codeを混ぜないことが大事**です。

名前が近いので、同じように見えます。

でも、実務での役割は違います。

---

**Claude Design**は、見た目の初稿を作る場所です。

言葉からビジュアルへ変換し、方向性を出し、デザインシステムに寄せ、資料やプロトタイプへまとめる場所です。

---

**Claude Code**は、動くものへ変える場所です。

HTML、CSS、React、Next.js、Vue、Astro、Tailwind、コンポーネント、状態、テスト、Git、CI、スクリーンショット検証まで扱う場所です。

制作物の完成度を上げるなら、この順番が強いです。

1. **Claudeで目的、読者、訴求、構成を整理する**
2. **Claude Designでラフ、ワイヤー、デッキ、素材案を作る**
3. **人間が方向性、文字、余白、ブランド、情報順序を判断する**
4. **Claude Codeで実装、検証、レスポンシブ調整を行う**
5. **Claude Codeにスクリーンショット、テスト、lint、アクセシビリティで確認させる**
6. **人間が最終判断する**

ここで重要なのは、AIが先ではなく、目的が先ということです。

Claude Designへいきなり「LP作って」と投げると、見た目は出ます。

でも、顧客、訴求、購入動機、反論、CV導線が弱ければ、ただのきれいなページです。

Claude Codeへいきなり「このデザインを実装して」と投げると、コードは出ます。

でも、デザインシステム、コンポーネントルール、ブレークポイント、画像比率、文字折り返し、状態設計がなければ、量産できない実装になります。

つまり、AIデザイン制作は**「指示力」**ではなく**「設計力」**です。

## ノンデザイナーが覚えるべきスキル

![](https://assets.st-note.com/img/1781913307-xnlJtc19gmwKBjpMRHQfykLq.png?width=1200)

ノンデザイナーは、プロデザイナーの真似をする必要はありません。  
覚えるべきことは、センスよりも判断基準です。

---

### 1. 目的を1行で書く力
