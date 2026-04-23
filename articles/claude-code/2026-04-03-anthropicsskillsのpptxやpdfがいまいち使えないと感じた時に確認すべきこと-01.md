---
id: "2026-04-03-anthropicsskillsのpptxやpdfがいまいち使えないと感じた時に確認すべきこと-01"
title: "Anthropics/skillsのpptxやpdfがいまいち使えないと感じた時に確認すべきこと"
url: "https://zenn.dev/megrou/articles/2dc60417ae5d67"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

## はじめに

Claude CodeなどのAIエージェントを日々の業務効率化やシステム開発に導入する中で、設計書やプレゼン資料の作成を自動化しようと `npx skills add https://github.com/anthropics/skills --skill pptx pdf` を実行したケースを想定します。

しかし、実際に生成や編集を行わせてみると、以下のような問題に直面することがあります。

* レイアウトが崩れたまま出力される
* 何度修正を指示しても、意図したデザインに到達しない
* 単にテキストを流し込んだだけの粗雑なスライドしか生成されない

このような事象は、スキルの基本性能が低いのではなく、AIがスライドを視覚的に確認するための前提ツールがローカル（ホストOS）に不足しており、機能が制限されてしまっている可能性が考えられます。

## `npx skills` だけでセットアップを終えていませんか？

ネット上の紹介記事の多くは、コマンドを一つ実行するだけでAIがPowerPointやPDFを完璧に操作できるようになるかのように書かれています。

しかし、`npx skills` コマンドが行うのは、GitHubからプロンプト（`.md`）やPythonスクリプトをダウンロードし、ローカル環境に配置することだけです。**これらのスクリプトが裏側で呼び出しているOSレベルの依存パッケージまでは自動解決してくれません。**

ここでセットアップを終えたつもりになっていると、スキルの真の力を引き出すことができず、「いまいち使えない」状態に陥ってしまいます。その理由となるのが、次に解説する「Visual QA」という仕組みです。

## スキルの要となる「Visual QA」機能

AIが `.pptx` や `.pdf` を高い精度で編集するには、XMLタグやテキストデータを操作するだけでなく、「実際に画面上でどう描画されているか」をAI自身が視覚的に確認し、自己評価と修正を繰り返すプロセス（Visual QA）が不可欠です。

Anthropicsが提供するドキュメント系スキルの内部スクリプトは、このVisual QAを機能させるために以下の動作を前提としています。

1. AIが編集した `.pptx` などのファイルを `.pdf` に変換する。
2. 変換した `.pdf` を高解像度の画像（`.jpg`など）にレンダリングする。
3. 生成された画像をVisionモデルが解析し、レイアウト崩れやデザインを修正する。

ホストOSにこの変換処理を行うための外部コマンドが存在しない場合、画像生成プロセスがエラーになるかスキップされます。結果としてAIは「盲目的に内部のXMLを編集するだけ」の状態に陥り、生成物のクオリティが著しく低下します。

## 隠れた必須依存ツール：`soffice` と `pdftoppm`

変換プロセスを正常に動作させるには、以下の2つのネイティブツールがホストOSにインストールされ、コマンドラインから直接呼び出せる（Pathが通っている）状態になっている必要があります。

* **`soffice` (LibreOffice):** ファイルをPDFにヘッドレス変換するために使用。
* **`pdftoppm` (Poppler):** PDFを画像としてレンダリングするために使用。

`npx skills` コマンドによるインストールは、プロンプト（`.md`）やPythonスクリプトをローカルに配置するだけであり、これらのOSレベルの依存パッケージまでは自動解決しません。

## 必須ツールのセットアップ

お使いのOS（Windows、macOS、Linux）の環境に合わせて、適切なパッケージマネージャーやインストーラーを用いてセットアップを行ってください。

macOSやLinux環境を使用している場合は、Homebrew（`brew install --cask libreoffice` および `brew install poppler`）やapt（`sudo apt install libreoffice poppler-utils`）などを利用して導入し、コマンドへのパスを通します。

### 例：Windows環境でのセットアップと確認

Windows環境での具体的な手順例は以下の通りです。

**1. soffice (LibreOffice) の導入**  
[LibreOffice公式サイト](https://ja.libreoffice.org/download/download/)からWindows版のインストーラーをダウンロードしてインストールします。その後、システムの環境変数「Path」に、インストール先の `program` ディレクトリ（通常は `C:\Program Files\LibreOffice\program`）を追加します。

**2. pdftoppm (Poppler) の導入**  
Windows環境では、パッケージマネージャー経由での導入が確実です。コマンドラインから以下を実行します。

* Scoopの場合: `scoop install poppler`
* Chocolateyの場合: `choco install poppler`

**3. パスの確認**  
環境変数の設定後、ターミナルを再起動し、以下のコマンドがエラーなく実行できれば準備完了です。

```
soffice --version
pdftoppm -v
```

## まとめ

AIエージェントのスキルエコシステムは強力ですが、OSのネイティブコマンドに依存するスクリプトが裏側で動いているケースは少なくありません。話題のスキルを導入しても期待した性能が出ないと感じた際は、リポジトリ内の `SKILL.md` や `scripts/` 配下のソースコードを確認し、前提となる実行環境が整っているかチェックすることが重要です。
