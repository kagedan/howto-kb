---
id: "2026-05-09-claude-coworkでできること-01"
title: "Claude Coworkでできること"
url: "https://qiita.com/j4nzeri/items/d2f7ab10ae051b6283ba"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "cowork", "qiita"]
date_published: "2026-05-09"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

Claude Coworkは、Claude Desktop上で動くAIエージェント機能です。

通常のチャットのように「質問して回答をもらう」のではなく、やりたい成果物を伝えると、Claudeがローカルファイルやアプリ、コネクタを使いながら、複数ステップの作業を進めてくれます。

Anthropic公式では、Claude Codeと同じエージェント型アーキテクチャを、**コーディング以外**の知識作業に持ち込んだものとして説明されています。

## できること

### 1. ドキュメント・スライド・Excelを作れる

公式ヘルプでは、Coworkの出力例として以下が挙げられています。

- 数式入りのExcelファイル
- PowerPointプレゼンテーション
- フォーマット済みドキュメント
- 複数ソースをまとめたレポート

CSVを吐くだけではなく、VLOOKUPや条件付き書式、複数シートを含むExcelも作れるとされています。
Claude codeではPowerPointなどのファイルは扱えないので、エンジニア以外の方でも使い道が出てくるのかと思います。

### 2. 調査と要約をまとめて任せられる

Web検索、記事、論文、手元のメモなどを横断して、要約やレポートにまとめる用途に向いています。

たとえば、

```text
このフォルダ内の議事録と、関連するWeb情報をもとに、
今月のプロダクト改善テーマを3つに整理してMarkdownで出力して
```

のように依頼できます。

### 3. 定期実行できる

CoworkにはScheduled tasksがあります。

例としては、

- 毎朝Slackやメールを要約する
- 毎週レポートを作る
- 競合や業界ニュースを定期調査する
- 指定フォルダを定期的に整理する

などが想定されています。

ただし、スケジュール実行はPCが起動していて、Claude Desktopが開いている必要があります。

### 4. Projectsで文脈を持たせられる

Cowork Projectsでは、関連タスクをワークスペースとしてまとめられます。

プロジェクトごとに、

- 指示
- ファイル
- コンテキスト
- スケジュールタスク
- メモリ

を持てます。

単発タスクよりも、「毎週のレポート作成」「特定プロダクトの調査」「社内ドキュメント整理」のような継続作業に向いています。

### 5. Plugins / Skills / Connectorsで拡張できる

Coworkはプラグインにも対応しています。

プラグインは、Skills、Connectors、Sub-agentsなどをまとめたパッケージです。Google Drive、Gmail、Slack、DocuSignなどの外部サービス連携も想定されています。

エンジニア目線では、MCPやコネクタ経由で社内ツールに接続できる点が面白いところです。

### 7. Computer Useで画面操作もできる

Claudeが直接画面を見て、クリックや入力を行うComputer Useもあります。

公式ヘルプでは、以下のような例が挙げられています。

- 社内ダッシュボードを操作する
- ブラウザで作業する
- スプレッドシートに情報を入力する
- 開発中アプリをシミュレータで触ってUX上の問題を探す

ただし、これはかなり強力なので、機密情報や重要操作には注意が必要です。

## まとめ

Claude Coworkでできることを一言でいうと、

> ローカルファイル、Web、アプリ、コネクタをまたいだ面倒な知識作業を、成果物ができるところまで任せる

です。

ファイル整理、調査レポート、Excel作成、定期レポート、複数資料の要約のように、「手順が複数あって、最後にファイルがほしい」作業はCowork向きです。

Claude Codeが開発者向けのツールだとすれば、Claude Coworkは開発者以外でもAIを活用できるようにするツールと考えてよさそうです。

## 参考

- [Claude Cowork by Anthropic](https://www.anthropic.com/product/claude-cowork)
- [Coworkを始める | Claude Help Center](https://support.claude.com/ja/articles/13345190-cowork%E3%82%92%E5%A7%8B%E3%82%81%E3%82%8B)
- [Schedule recurring tasks in Claude Cowork](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)
- [Organize your tasks with projects in Claude Cowork](https://support.claude.com/en/articles/14116274-organize-your-tasks-with-projects-in-claude-cowork)
- [Let Claude use your computer in Cowork](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork)
- [Use plugins in Claude Cowork](https://support.claude.com/en/articles/13837440-use-plugins-in-claude-cowork)
