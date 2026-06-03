---
id: "2026-06-02-claude-code活用claude-codeとは何か導入と初期設定-01"
title: "【Claude Code活用】Claude Codeとは何か・導入と初期設定"
url: "https://zenn.dev/pekopugu/articles/agent01-b1-claudecode-intro"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

## この記事について

「Claude Codeを使いこなす」をテーマにしたシリーズの第1回です。

AIエージェント自作プロジェクト [agent01](https://github.com/pekopagu/agent01) の開発を通じて、Claude Code をどのように活用したかを紹介します。

**シリーズ構成**

| Series | テーマ |
| --- | --- |
| A | AIエージェントを作って理解する |
| B（本シリーズ） | Claude Codeを使いこなす |
| C | AIへの指示を外部ファイルで管理する |

---

## Claude Code とは

Claude Code は、Anthropic が提供するターミナル上で動作する AI コーディングエージェントです。

「指示するとコードを書いてくれる」というツールではなく、**「一緒に開発する」パートナー**として設計されています。ファイルを読み・書き・実行しながら、自然言語の指示だけで実装を進めることができます。

今回の連載では、AIエージェント自作プロジェクト [agent01](https://github.com/pekopagu/agent01) の開発を通じて Claude Code をどのように活用したかを紹介します。

## インストールと初期設定

Node.js（18以上）が入っている環境であれば、以下のコマンドで導入できます。

```
npm install -g @anthropic-ai/claude-code
claude --version
claude  # 起動
/login  # ブラウザ認証
```

利用には **Claude Pro アカウント**が必要です。初回起動時に `/login` コマンドでブラウザ認証を行います。

### Windows 環境での注意点

Windows では PowerShell から起動します。文字化けを防ぐため、PowerShell のデフォルトエンコーディングを UTF-8 に設定しておくと安定します。

```
# PowerShell プロファイルに追加しておくと便利
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## CLAUDE.md の役割

Claude Code はプロジェクトのルートにある `CLAUDE.md` を起動時に自動で読み込みます。ここにプロジェクト固有のルールや規約を書いておくことで、セッションをまたいでも一貫した動作が得られます。

agent01 の `CLAUDE.md` では以下を定義しています。

CLAUDE.md

```
## 作業の進め方

### 必ず最初に読むファイル

作業開始時は以下の順で読むこと。

1. `PROGRESS.md` ← 現在地・申し送り事項を確認
2. `AGENT_SPEC.md` ← 仕様・設計を確認
3. 該当する実装指示書（例：`実装指示書_Step02.md`）
```

「起動したらまず PROGRESS.md を読む」というルールを CLAUDE.md に書いておくだけで、毎回口頭で伝える手間がなくなります。

## 基本的な使い方

Claude Code への指示は自然言語で行います。

* **ファイルを読む**：「`src/repl.py` を読んでください」
* **コードを書く**：「`src/tools/file_tools.py` に `read_file` 関数を追加してください」
* **コマンドを実行する**：「`python src/step01_hello.py` を実行して動作確認してください」

Claude Code は変更前に差分を提示して確認を取ります。`y` で適用、`n` でキャンセルできるため、意図しない変更が加わるリスクを抑えられます。

## 今回のプロジェクトでの役割分担

agent01 の開発では以下の役割分担で進めました。

```
Claude（claude.ai）  ← 設計・仕様策定・レビュー
Claude Code          ← コード実装・テスト・記事生成
PROGRESS.md          ← セッション間の文脈引き継ぎ
```

Claude.ai で設計した仕様を実装指示書として書き出し、それを Claude Code に渡して実装する流れです。PROGRESS.md がセッションをまたぐ「記憶」として機能しています。

## まとめ

Claude Code はターミナルで動く AI コーディングエージェントです。CLAUDE.md でプロジェクト固有のルールを設定し、PROGRESS.md でセッション間の文脈を引き継ぐことで、複数セッションにわたる開発を効率よく進められます。

## 次回

B2 では、Claude Code のファイル読み書き能力について、実際に `src/tools/file_tools.py` を生成させた体験をもとに紹介します。

## 関連シリーズ

このシリーズで作ったエージェントの実装詳細は Series A で解説しています。

**[Series A：AIエージェントを作って理解する](https://zenn.dev/pekopugu/articles/agent01-a1-concept-design)**  
→ OllamaのローカルLLMを使ったコードベース改良エージェントをゼロから作ります。

## シリーズリンク（Series B）
