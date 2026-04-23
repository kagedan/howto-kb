---
id: "2026-04-01-mastra-で作る-aiエージェント18mcpやskillsでaiコーディングを便利にする-01"
title: "Mastra で作る AIエージェント(18)MCPやSkillsでAIコーディングを便利にする"
url: "https://zenn.dev/shiromizuj/articles/3852cf542ea8c1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

[Mastra で作るAI エージェント](https://zenn.dev/shiromizuj/articles/a0a1659e9f05b6) というシリーズの第18回です。

---

今回はちょっとややこしいのですが、「Mastraを使ったAIエージェントアプリ」自体ではなく、「Mastraを使ったAIエージェントアプリ」**の開発**をいかに便利に実現するか、という話です。今どきの開発だと、GitHub Copilot や Claude Codeなどのコーディングエージェントを活用しますよね。その際に、それらの**コーディングエージェントに最新のMastra公式ドキュメントをスムーズに参照してもらう**ことが重要になります。

2026年2月4日にリリースされた Mastra 1.2 から、AIエージェントにMastraの知識を提供する方法として、既存の「Mastra Document MCP」に加えて「Mastra Skills」が利用可能になりました（[ニュースリリース](https://mastra.ai/blog/changelog-2026-02-04)）。

* **Mastra Docs MCP Server**: Model Context Protocol サーバーとして動作
* **Mastra Skills**: Agent Skills仕様に準拠した構造化知識ファイル

両者は**相互補完的**な関係であり、用途に応じて使い分けることができます。

# Mastra Document MCP

MCP（Model Context Protocol）サーバーとして動作するMastra Docs MCPは、VSCodeなどのエディタ上でAIエージェントに高度なドキュメント検索機能を提供します。設定ファイルに数行追加するだけで、「AIがMastraについて正しい情報に基づいて回答できる状態」を手軽に整えてくれる仕組みです。

「Mastraの公式ドキュメントをMCPで提供する」というこの仕組みは、2025年の3月に提供されました（[当時の公式アナウンス](https://mastra.ai/blog/introducing-mastra-mcp)）。MCPの仕様がAnthropicによって公開されたのが2024年11月で、この頃は「一大MCPブーム」の真っ最中でもありました。AIエージェントにMastra Docs MCP の定義を書いておくだけでコーディングエージェントの書くコードが非常に筋が良いものになり、「**外さなくなった**」と舌を巻いたのを覚えています。当時LLMの性能がぐっと良くなった、というのもあると思いますが、それにしてもMastra Docs MCPを入れる時と入れない時との比較として効果を実感したものです。

![](https://static.zenn.studio/user-upload/05a0692f920a-20260209.png)  
*MCPを導入すれば、VSCode上で「ツールの構成」から様々な機能を確認できる*

Mastra Docs MCPの機能は、**ローカルパッケージドキュメント**・**リモートドキュメント**・**インタラクティブコース**の3系統で構成されています。

## ローカルパッケージドキュメント：バージョン一致が強み

ローカル参照の最大の強みは、プロジェクトにインストール済みの`node_modules/@mastra/*`を情報源とする点にあります。ライブラリのAPIが変わっても古い情報を参照するリスクがなく、使用中のバージョンと完全に一致したドキュメントを返せます。TypeScript型定義の正確な参照も可能で、`getMastraExportDetails`を使えばAgentやTool、Workflowといった主要クラスの型定義と実装コードを即座に取り出せます。内部では`SOURCE_MAP.json`でエクスポート名とファイルのマッピングが管理されており、オフライン動作とキャッシュによる高速アクセスも実現しています。

| ツール | 用途 |
| --- | --- |
| `listMastraPackages` | インストール済みパッケージ一覧 |
| `getMastraExports` | パッケージのAPI一覧（Agent, Tool, Workflowなど） |
| `getMastraExportDetails` | TypeScript型定義と実装コードの取得 |
| `readMastraDocs` | トピック別ドキュメント（agents, tools, workflows, memoryなど） |
| `searchMastraDocs` | ローカルドキュメント全文検索 |

## リモートドキュメント：常に最新情報へ

ローカルには存在しない情報——最新機能の動向、バージョン間の移行手順、公式ブログの解説——については、`https://mastra.ai`にアクセスするリモート参照が担います。特にメジャーバージョンアップ前後では、`mastraMigration`で移行ガイドを確認したり、`mastraChanges`で変更履歴を追ったりする使い方が実践的です。`mastraBlog`からはブログ投稿とアナウンスも参照でき、ドキュメントだけでは把握しづらい設計意図や新機能の背景を深掘りできます。

利用できるツールは`mastraDocs`（公式ドキュメント）、`mastraBlog`（ブログ投稿とアナウンス）、`mastraExamples`（コード例とテンプレート）、`mastraChanges`（パッケージ変更履歴）、`mastraMigration`（バージョン間移行ガイド）の5種類です。

## インタラクティブコース：体系的に学ぶ

MCPサーバーにはコース機能も内蔵されています。`startMastraCourse`でコースを開始し、`getMastraCourseStatus`で進捗を確認しながら`nextMastraCourseStep`で次のステップへ進む流れです。リファレンス検索ではなく、一から体系的に学び直したい場面に向いています。

## 導入方法

`.vscode/mcp.json`に以下を追加するだけです。`npx`がサーバーを自動起動するため、別途インストールは不要です。

```
{
  "servers": {
    "mastra": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@mastra/mcp-docs-server@latest"]
    }
  }
}
```

設定後の使用例としては、ローカルパッケージの型定義確認なら`getMastraExportDetails("@mastra/core", "Agent")`、最新のマイグレーションガイド参照なら`mastraMigration("upgrade-to-v1/agent")`、インストール済みパッケージのexport一覧なら`getMastraExports("@mastra/core")`といった形でツールを呼び出せます。

# Mastra Skills

## 静的ファイルとして配置する構造化知識

Mastra Skillsは、冒頭述べたように2026年2月4日にリリースされた Mastra 1.2 から利用可能になりました（[ニュースリリース](https://mastra.ai/blog/changelog-2026-02-04)）。[Agent Skills仕様](https://agentskills.io/specification)に準拠した構造化知識ファイルです。MCPのようにサーバープロセスを起動するのではなく、プロジェクトに静的ファイルとして配置し、GitHub CopilotなどのAIエージェントがコンテキストウィンドウ内で直接読み込む形で機能します。

インストールすると、`.agents/skills/mastra/`フォルダが作られ、以下のような構成になります。

![](https://static.zenn.studio/user-upload/85a2377afc41-20260209.png)  
*インストールすると、`.agents/skills/mastra`フォルダが作られ、スキル関連資材が導入される*

中心となる`SKILL.md`には、AIエージェントへの重要な警告（「内部知識を信頼せず、常に最新ドキュメントを確認すること」）のほか、ドキュメント検索の優先順位（Embedded docs → Remote docs）、Agents vs WorkflowsやTools・Memory・RAGといったコアコンセプト、そして質問タイプ別の参照先ガイドが含まれています。`references/`フォルダにはより詳細な情報が階層的に格納されており、**プログレッシブディスクロージャー**——必要な情報を段階的に提供してコンテキストを節約する手法——によって、エージェント非依存の汎用性を確保しながら効率的な参照を実現しています。

```
.agents/skills/mastra/
├── SKILL.md                     メインスキルファイル
└── references/
    ├── embedded-docs.md         ローカル埋め込みドキュメントの検索方法
    ├── remote-docs.md           リモートドキュメント検索方法
    ├── create-mastra.md         プロジェクト作成・セットアップガイド
    ├── common-errors.md         よくあるエラーと解決策
    └── migration-guide.md       バージョン移行ワークフロー
```

## 導入方法：`npx`が担う複数の処理

```
# インストール（インタラクティブ）
npx skills add mastra-ai/skills

# インストール（自動）
npx skills add mastra-ai/skills --yes

# 新規プロジェクト作成時に含める
npm create mastra --skills mastra-ai/skills
```

一般的にAgent Skillsはスキルフォルダのコピーで導入しますが、Mastra SkillsはAgent Skills仕様の標準的なパッケージ管理を採用しているため、`npx`コマンドで導入します。

`npx skills add mastra-ai/skills`は単純なフォルダコピーではありません。実行すると、`.agents/skills/mastra/`（universal location）への実体配置と、`.agent/skills/mastra`へのシンボリックリンク作成（Antigravity用）が自動的に行われます。この標準化された配置場所により、GitHub Copilot・Codex・Gemini CLI・Claude Code・OpenCode・Ampといった、Agent Skills仕様に対応するすべてのエージェントが自動認識します。手動コピーによる配置ミスを防ぎながら、バージョン管理と依存関係の自動解決も実現しています。

インストール後は、**VSCodeを再起動**するか`Developer: Reload Window`を実行することで、GitHub Copilotが`.agents/skills/mastra/`を自動認識し、Mastraコードの作成時にSkillsの知識が活用されます。

## バージョン管理の注意点と「予防的アプローチ」

Mastra Skillsは、MCP Docs Serverとは異なり、Mastraに関するドキュメントをローカルの`.agents/skills/mastra/`フォルダに格納する仕組みです。そのため、**Mastra本体**（`@mastra/core`など）**をバージョンアップした際にSkillsを更新し忘れると、AIエージェントが古いドキュメントを参照し続ける**ことになります。Skillファイルにはメタデータとしてバージョンが記載されており（例：`version: "2.0.0"`）、本体のアップデート時には以下のコマンドで最新版を再インストールするのが確実です。

```
# 最新版を再インストール
npx skills add mastra-ai/skills --yes
```

現状、本体とSkillsとの間での**自動的な不一致検知の仕組みは明示されていません**。ただし、SKILL.mdには次の警告が記載されています。

> ⚠️ **Critical: Do not trust internal knowledge**  
> Everything you know about Mastra is likely outdated or wrong. Never rely on memory. Always verify against current documentation.

これは「不一致を検知して対処する」のではなく、「AIエージェント自身が常に最新ドキュメントを確認することで不一致を回避する」という**予防的アプローチ**の設計思想です。型エラーが発生した場合も、`references/common-errors.md`を通じて対処方法を提示する仕組みになっています。

# Mastra Docs MCP Server と Mastra Skills の類似点と相違点

両者は「AIエージェントにMastraの情報を提供する」という目的を共有しています。`node_modules/@mastra/*/dist/docs/`の参照、`https://mastra.ai`の情報へのアクセス、インストール済みバージョンへの対応、エラー対処とマイグレーション情報の提供といった機能は、どちらにも共通しています。

その一方で、設計思想は対照的です。MCP Docs Serverがサーバープロセスとして動的にドキュメントを取得する「動的な深さ」を持つのに対し、Mastra Skillsは静的ファイルによる「軽量な広さ」を志向しています。

| 項目 | Mastra Document MCP | Mastra Skills |
| --- | --- | --- |
| **プロトコル** | Model Context Protocol (MCP) | Agent Skills仕様 |
| **動作形態** | サーバープロセスとして動作 | 静的ファイルとして配置 |
| **対応エージェント** | MCP対応エージェント（主にVSCode） | Agent Skills対応エージェント（汎用） |
| **インストール** | `.vscode/mcp.json`に設定 | `npx skills add`でファイル配置 |
| **実行時** | `npx @mastra/mcp-docs-server` | ファイル読み込みのみ |
| **機能の深さ** | 高度（型定義、SOURCE\_MAP、全文検索） | シンプル（構造化ドキュメント） |
| **TypeScript型定義** | 詳細な型情報取得可能 | ❌ 型情報は含まない |
| **インタラクティブコース** | あり | ❌ なし |
| **マイグレーションツール** | 高度な検索・フィルタリング | 基本的なガイド |
| **コンテキスト効率** | ツール呼び出しによる動的取得 | プログレッシブディスクロージャー |
| **オフライン動作** | ローカルドキュメントのみ可能 | 完全オフライン |
| **セットアップ複雑さ** | JSON設定ファイル | 1コマンド |

Mastra公式ブログ（2026年2月5日）はこのように推奨しています。

> **For purely docs purposes, we recommend using Mastra Skills. If you need access to the more sophisticated migration tools that the MCP Docs Server provides, then you can use that as a fallback.（純粋にドキュメント作成の目的であれば、Mastra Skillsの使用をお勧めします。MCP Docs Serverが提供するより高度な移行ツールへのアクセスが必要な場合は、それを代替手段として使用できます。）**

つまり日常的なコーディング支援にはMastra Skillsが推奨の第一選択です。TypeScript型定義の詳細確認や`SOURCE_MAP.json`によるexport検索、埋め込みドキュメントの全文検索が必要な場面ではMCP Docs Server（ローカル）が、最新機能・変更の確認やブログ記事の参照、詳細なマイグレーションガイドにはMCP Docs Server（リモート）が、体系的な学習にはコース機能が活躍します。

# Mastraを使う場合は、両方入れるのが吉

将来的な話はともかく、少なくとも本記事執筆時点においては、Mastraを使ってAIエージェントを開発する場合は**両方入れておけば間違いない**と思います。

---

# こぼれ話：Mastraチームのドキュメント苦難史

> 以下の話は、Mastra CTO兼共同創業者のObbyさんが2026年3月に語った舞台裏の話（[動画](https://youtu.be/M4dWxs3CV-M?si=uwcZwOpQLNckqziZ)）をもとにまとめたものです。MCPやSkillsがなぜ今の形になったのか、その背景にある試行錯誤が知れる、興味深いエピソードです。

## 「人間向けドキュメントを最高にしよう」から始まった

Mastraはもともと、Gatsby.jsを作っていたチームが立ち上げたプロジェクトです。Obbyさん曰く「Gatsby時代のドキュメントは本当にひどかった」という反省から、Mastraを始めた際の最初の決意が「**人間向けドキュメントを最高にしよう**」でした。

その初期方針は実を結び、人間にとって読みやすいドキュメントサイトが完成しました。ところが時代はすでにAIエージェントが開発現場に入り込み始めた頃。`llms.txt` の流れが出てきて、チームはすべてのページを `llms.txt` 形式へ変換し、同時にまとめた `llms.txt` も1つ用意しました。

## 日本でバズって、うっかり100万トークン超え

思わぬ出来事が起きます。**なぜかMastraが日本でバズりました。**

実際に日本を訪問してユーザーと話すと「ドキュメントサイトが日本語になっていない」という声が多く寄せられ、General Translationというツールで日本語化を進めました。  
ここまではよかったのですが、**`llms.txt` の方を見直し忘れていました。**

英語と日本語を同じファイルに混在させたまま、記事が増え続けた結果、**ファイルサイズは100万トークンを超えていました。そして、それに1年間気づかなかったのです。**

## 「分割したほうがいい」と思い直す

そこで「エージェントはパス単位でドキュメントを参照するのだから、巨大な1ファイルより、各ルートにMarkdownを置いて分割するほうが効率的だ」という方針に切り替えました。  
Obbyさんいわく、「実はMintlifyならその頃すでにできていた機能でした。知らなかっただけで……」と苦笑いしていました。

## MCPドキュメントサーバーを作るも、新たな問題

そこからMastra向けのMCPドキュメントサーバーを作り始めます。発想はシンプルでした。  
**「Mastraは新しいフレームワークだから、LLMの学習データに入っていない。ならばCursorやIDEからMCPを使えるようにして、コードを書かせやすくしよう。」**

この取り組みは会社の成長にも貢献しましたが、問題も出てきました。  
**コンテキストウィンドウの制御が難しかったのです。**  
元々のドキュメントは「人間向け」として丁寧に書かれており、説明が冗長でした。さらに、日本語化したことで英語版と日本語版の両方がMCPサーバーのレスポンスに混入し、**コンテキストが二重に膨れ上がる**という最悪の状態になっていました。

## Replitとの出会いが、本質を教えてくれた

転機になったのは、**ReplitがMastraエージェントを使い始めたこと**でした。

Replit側の開発者は「Mastraそのもの」より「Replit AgentがMastraのコードを正確に書けるか」を重視していました。そのため、Mastraの公式サイトや `llms.txt` から独自にドキュメント集合を生成して使っていたのです。  
そして、こう指摘されました。

> **「あなたたちのドキュメントは各ページに日本語が混ざっていて、要約もできない。使えない。」**

この一言が、チームを大きく動かします。以来、Obbyさんは「本当のDXとは何かを初めて理解した」と振り返っています。  
「エージェントを使う開発者の体験」を考えるとき、自分たちが見せているサイトより、**エージェントが参照するドキュメントの質**こそが重要だったのです。

## node\_modules の中にドキュメントを入れる

修正を重ねる中で生まれたのが、\*\*「ドキュメントをnode\_modulesに同梱する」\*\*という発想です。

インストールしたバージョンに常に一致したドキュメントが手元にある、これが理想の状態です。実際にLLMが情報不足のとき**node\_modulesをgrepする挙動**を観察したことが、この設計を後押ししました。  
現在はMastraの各パッケージに `dist/docs/` フォルダが入っており、パッケージの `README.md` やAPIリファレンスが同梱されています。

さらに、「関連情報を辿れるように」**パンくずを埋め込み**、`source_map.json` を配布して「概念から実装ファイルへ到達できる」動線も整備しました。  
それでも見つからない場合のフォールバックとして、最後にWebサイトを参照する設計になっています。

## 人間向けドキュメントも大事にしている

Obbyさんがこの話の中で強調していたのは、\*\*「人間向けドキュメントを捨てたわけではない」\*\*という点です。

日本語ドキュメントを整理した後、日本のユーザーから「日本語版はどこに行った？」という声が上がりました。そこで、ドキュメントをChatGPTなどで開いて扱える導線を追加し、人間側でも引き続き使いやすくする工夫を加えています。

「AI向けに最適化する」と「人間に読みやすい」は、必ずしもトレードオフではない、という姿勢が伝わってくるエピソードでした。

## MCPもSkillsも、どちらも続けていく

セッション最後の質疑で「MCPサーバーやAgent Skillsは今も両方維持し続けるのか？」という質問が出ました。Obbyさんの答えは明確でした。

**「Yes」。**

ツールの進化が激しい今の時代でも、実運用では複数の手段を組み合わせて使い続ける必要がある——それがMastraチームの現在地であり、この記事で紹介してきた「両方入れよう」という結論にも繋がっています。

1年間気づかなかった100万トークン超えのファイル、日本語テキストによる二重膨張、Replitからの「使えない」という一言……。失敗と修正を繰り返しながら、MCPとSkillsというアプローチが磨かれてきた、という背景を知ると、これらのツールの設計思想がより深く理解できるのではないでしょうか。

---

[>> 次回 : (19) さまざまなデプロイ方法](https://zenn.dev/shiromizuj/articles/dd6c48328b961b)
