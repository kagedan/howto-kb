---
id: "2026-05-05-claude-agent-skills-をやってみる-01"
title: "Claude Agent Skills をやってみる"
url: "https://zenn.dev/kameoncloud/articles/dff0de5016d828"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

<https://serverless.co.jp/blog/lx87rayrtm8v/>  
に投稿した記事の微修正版です

Anthropic は 2025年10月16日（米国時間）に「Agent Skills」を初めて公式に発表 し、同社の AI モデル Claude（クロード） が特定のタスクを実行するために必要な知識や手順をスキルとして読み込める仕組みを公開しました。これは単なるプロンプトレベルの指示ではなく、必要な指示・スクリプト・リソースを纏めたフォルダ構造として整理されたもので、AI が 再利用可能かつ状況に応じて動的に読み込める専門知識 を扱えるようにするものです。

発表当初は、Claude の新機能としてプレビュー形式で提供され、企業や開発者が Excel 操作やブランドガイドラインに沿った文書作成など、実務的なタスク処理をスキル化できる基盤 が整えられました。これにより、AI は単なる質問応答ではなく 継続性のある作業遂行能力を持つエージェント として振る舞えるようになっています。

2025年12月中旬（12月18日頃）Anthropic は Agent Skills の仕様を オープンスタンダード（公開仕様）として公開 し、特定のモデルやプラットフォームに縛られない形で利用・共有できるようにしました。これにより、AI エコシステム全体で Agent Skills の互換性が高まり、Claude 以外の AI ツールやプラットフォームとも連携できるような 開かれた基盤として進化 しています。

#### Agent Skills の動作の仕組み

Anthropic が公開している `anthropics/skills` リポジトリで提案されている Agent Skills（エージェントスキル） は、AI エージェントに「役割」や「専門性」を与えるための仕組みです。  
これは単なるプロンプト集ではなく、AI が特定のタスクを安定して実行するための知識・手順・補助リソースを一体化した再利用可能な単位として設計されており、従来自然言語でLLMに動作を指定していたシステムプロンプトを拡張し、「この作業をするときは、この考え方・この手順・この制約を守る」という知識を スキルとして事前定義 し、必要なときにエージェントへ読み込ませるという考え方を取っています。

Agent Skills は、プロンプトエンジニアリングを 属人化したノウハウ から 構造化された資産 に変えます。これまでのプロンプトは、チャット履歴に埋もれたり、人によって書き方が異なったりと、再利用性や保守性に課題がありました。

一方で Agent Skills は、フォルダ単位で管理され、Markdown 形式の `SKILL.md` にスキルの目的、前提条件、具体的な指示、使用例などが明確に記述されます。  
このファイル自体が「AI に渡す作業マニュアル」となり、エージェントは必要に応じてそれを読み込み、振る舞いを切り替えます。

つまり、「その場限りのプロンプト」ではなく、「継続的に使える業務スキル」として AI の能力を拡張できるのです。

### さっそくやってみる

#### 1. skills サンプルの入手

`anthropics/skills` GitHub レポジトリで多くの実務的なサンプルが提供されているためこちらを試していきます。

まずはZIPファイルをダウンロードします。  
![](https://static.zenn.studio/user-upload/b51538c50bc2-20260505.png)  
ZIPファイルの中身は以下で構成されています。  
![](https://static.zenn.studio/user-upload/2edb78b0206a-20260505.png)  
この中から `skill` フォルダをコピーしておきます。

#### 2. Claude Code への組み込み

Claude Code を[この手順](https://code.claude.com/docs/ja/overview#native-install-recommended)に従いローカル環境で起動できるようにしておきます。  
Windowsであれば `"C:\Users\<user name>\.claude"` の下に `skills` フォルダをコピーします。

#### 3. Claude Code で skill のテスト

では Claude Code からテストを行います。 /skill と入力して実行してみます。  
![](https://static.zenn.studio/user-upload/1e6a695ec04e-20260505.png)  
以下の様に認識されていれば一覧が表示されます。  
![](https://static.zenn.studio/user-upload/eea8584cbd08-20260505.png)  
次にPowerPointファイルを作成してみます。

```
/pptx claude code を説明する１枚のスライドを作成して
```

このように指定することで `pptx` スキルが自動で使用されます。初回実行時はPPTX生成のためにいろいろモジュールをダウンロードしたり少し試行錯誤しながらしばらく待つとPPTXが生成されます。

```
● PowerPointファイルが正常に作成されました（57KB）。

  Claude Codeを説明する1枚のスライドを作成しました。

  ファイル: C:\Users\h-kameda\workspace\claude-code.pptx
```

以下のスライドが出来ました。  
![](https://static.zenn.studio/user-upload/d5d371a03f04-20260505.png)

#### 4. pptx skill の改修

では先ほど使用した `pptx skill` を改修します。以下のプロンプトを実行してみます。

```
pptx skill を改修したい。生成されるpptxは常に青バックにしたい
```

以下の通りpptx skill の改造が完了します。

```
 pptx skillを改修しました。

  変更内容: C:\Users\h-kameda\.claude\skills\pptx\scripts\html2pptx.js

  // 変更前
  async function addBackground(slideData, targetSlide, tmpDir) {
    if (slideData.background.type === 'image' && slideData.background.path) {
      targetSlide.background = { path: imagePath };
    } else if (slideData.background.type === 'color' && slideData.background.value) {
      targetSlide.background = { color: slideData.background.value };
    }
  }

  // 変更後
  async function addBackground(slideData, targetSlide, tmpDir) {
    targetSlide.background = { color: '0066CC' };  // 常に青背景
  }

  これで、html2pptxを使って生成されるすべてのスライドが青い背景（#0066CC）になります。
```

では以下のプロンプトで再度pptxを再生成させます。

指示通りのpptxが生成されました。  
![](https://static.zenn.studio/user-upload/7e014fdc38a7-20260505.png)
