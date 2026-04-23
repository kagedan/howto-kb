---
id: "2026-03-27-mcpサーバー入門-claude-desktopと連携して5分でaiにファイル操作させる方法-01"
title: "MCPサーバー入門 — Claude Desktopと連携して5分でAIにファイル操作させる方法"
url: "https://qiita.com/NakajimaSH/items/a886675458963b96c89d"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

**動作確認環境**

* Claude Desktop：最新版（2025年3月時点）
* Node.js：v18以上（推奨 v20 LTS）
* `@modelcontextprotocol/sdk`：v1.x（2025年3月時点の最新安定版）
* OS：Windows 11 / macOS 14 Sonoma

## 1. はじめに — 「MCPって聞くけど、自分に関係ある？」

「MCP」という言葉、最近よく目にしませんか？

エンジニアのブログ、X（旧Twitter）のタイムライン、AI系のニュースサイト……でも「なんか難しそう」「サーバーって聞くと身構える」と感じて、読み飛ばしてしまっている方も多いのではないでしょうか。

この記事はそんな方に向けて書きました。

**この記事を読み終わったら：** `claude_desktop_config.json` を1箇所書き換えるだけで、AIがあなたのデスクトップのファイルを一覧してくれる体験ができます。設定は10分以内に完了します。

**この記事を読むと分かること：**

* MCPとは何か、30秒で理解できるアナロジー
* MCPを構成する3つの登場人物と通信の流れ
* MCPで何ができるのか（実用ユースケース5選）
* Claude DesktopにMCPサーバーを接続する具体的な手順
* 自作MCPサーバーへの最初の一歩

**前提知識：** プログラミングの基礎（JSONが読める、コマンドラインが使える程度）があれば十分です。「サーバー」の構築経験は不要です。

**「サーバー」という言葉に身構えないで**  
MCPサーバーは、Webサーバーのように常時起動してインターネットに公開するものではありません。CLIツールと同じように、必要なときだけローカルで起動するプログラムです。

## 2. MCPとは何か — 30秒でつかむ本質

### AIへの「手と目」を与えるプロトコル

従来のLLM（大規模言語モデル）は「テキストを入力するとテキストを返す」だけの存在でした。

```
【Before】
ユーザー → テキスト → AI → テキスト → ユーザー
                ↑
        ここで完結。外の世界に触れられない。
```

MCPを使うと、AIは外部のツールやデータソースと連携できるようになります。

```
【After】
ユーザー → テキスト → AI ←→ MCPサーバー ←→ ファイル・GitHub・DB・Slack...
                ↑
        外の世界に「手と目」が生えた！
```

### MCP = Model Context Protocol

MCPはAnthropic（Anthropicは、ClaudeというAIを開発している企業です）が2024年11月に公開したオープンな通信規格です。正式名称は **Model Context Protocol**。

「なぜ新しい規格が必要だったのか？」と思うかもしれません。MCPが登場する前は、AIと外部ツールを連携させるたびに、**ツールごとに専用のコードを書く必要がありました**。

### USB規格アナロジー

MCPの登場は、周辺機器の世界でのUSBの登場に似ています。

| 時代 | 周辺機器 | AI連携 |
| --- | --- | --- |
| 統一前 | 機器ごとに専用ケーブル | ツールごとに専用コード |
| 統一後 | USB一本で接続 | MCP一本で接続 |

MCPというUSB規格に対応さえすれば、ClaudeだろうとほかのAIだろうと、どのMCPサーバーとでも繋がれる。これがMCPの本質的な価値です。

> **このセクションのポイント：** MCPはAIに「手と目」を与えるオープンな通信規格。USB規格のように「一度対応すればどこでも繋がる」を実現する。

## 3. MCPの仕組み — 3つの登場人物

MCPには3つの登場人物がいます。

[![Gemini_Generated_Image_alpr6walpr6walpr.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3822984%2F5c4ae238-3904-4150-bae9-049d07c7af22.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=51b0dc14fdd7fecc5cf2e0cb25f6dce8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3822984%2F5c4ae238-3904-4150-bae9-049d07c7af22.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=51b0dc14fdd7fecc5cf2e0cb25f6dce8)

### MCPクライアント

ユーザーが直接触れる側のアプリケーションです。代表例はClaude Desktopです。ユーザーの自然言語での指示を受け取り、MCPサーバーへの要求に変換します。

### MCPサーバー

特定のツールや機能を提供するプログラムです。「filesystem」「GitHub」「Slack」など、機能ごとに個別のMCPサーバーが存在します。**ローカルで起動する小さなプログラム**で、常時公開するWebサーバーとは別物です。

### トランスポート（通信方式）

クライアントとサーバー間の通信方法です。

| 方式 | 用途 |
| --- | --- |
| **stdio**（標準入出力） | ローカルで動かす場合（最も一般的） |
| **Streamable HTTP** | リモートサーバーに接続する場合（現行仕様） |

**HTTP+SSEからStreamable HTTPへ**  
以前のMCP仕様ではリモート通信に「HTTP + SSE（Server-Sent Events）」を使用していましたが、現行仕様では **Streamable HTTP** に移行しています。新規に実装する際は Streamable HTTP を採用してください。

### 通信の流れ（シーケンス）

[![Gemini_Generated_Image_a20xjha20xjha20x.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3822984%2F7ed633c1-a8c4-45b6-9a18-77b8ff11783f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9365a705751717c334138138fdaa330f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3822984%2F7ed633c1-a8c4-45b6-9a18-77b8ff11783f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9365a705751717c334138138fdaa330f)

### MCPサーバーが提供する4つの機能

| 機能 | 説明 | 例 |
| --- | --- | --- |
| **Tools**（ツール） | AIが呼び出せる関数 | ファイル読み書き、検索実行 |
| **Resources**（リソース） | AIが参照できるデータ | ファイル内容、DBレコード |
| **Prompts**（プロンプト） | 再利用可能なプロンプトテンプレート | コードレビュー用プロンプト |
| **Sampling**（サンプリング） | サーバーからAIを呼び出す機能 | 複雑な推論の委譲 |

実際のユースケースでは **Tools** と **Resources** が最もよく使われます。

> **このセクションのポイント：** MCPはクライアント・サーバー・トランスポートの3要素で成り立つ。「サーバー」はローカルで動く小さなプログラムで、難しくない。

## 4. 何ができるようになるのか — ユースケース5選

### filesystem（難易度 ★☆☆）

ローカルのファイルシステムへのアクセスを提供します。Claudeに「このフォルダ内のコードをリファクタリングして」と指示すると、実際にファイルを読み書きしてくれます。

**できること例：**

* 指定フォルダ内のファイル一覧取得
* ファイルの読み込みと内容分析
* ファイルの作成・編集・削除

### GitHub（難易度 ★★☆）

GitHubのAPIと連携します。Claudeに「このリポジトリの未解決Issueをまとめて」と頼めば、自動でAPIを叩いてまとめてくれます。

**できること例：**

* Issue・PRの一覧取得とサマリー作成
* ファイル内容の閲覧・変更
* ブランチ操作

### Slack（難易度 ★★☆）

Slackのチャンネル情報やメッセージを扱えます。「今日の#generalの重要な連絡をまとめて」といった依頼が可能になります。

**できること例：**

* メッセージの読み込みとサマリー
* チャンネル一覧の取得
* メッセージの送信

### SQLite / PostgreSQL（難易度 ★★★）

データベースに自然言語で問い合わせられます。「売上が先月より20%以上増えたユーザーを教えて」と言えば、Claudeが適切なSQLを組み立てて実行します。

**できること例：**

* 自然言語からSQLへの変換・実行
* テーブル構造の把握と可視化
* クエリ結果の分析・レポート生成

### Puppeteer（難易度 ★★★）

ブラウザを自動操作できます。「このECサイトの商品価格を毎日取得して」といったスクレイピングや操作自動化が可能です。

**できること例：**

* Webページのスクリーンショット取得
* フォーム入力・ボタンクリックの自動化
* Webスクレイピング

> **このセクションのポイント：** まずはfilesystemから始めるのが最も簡単でリスクも低い。慣れたら徐々に難易度の高いサーバーに挑戦しよう。

## 5. 実際に触ってみる — Claude DesktopにfilesystemMCPを接続するハンズオン

### 前提条件

* Claude Desktopがインストールされていること
* Node.js v18以上がインストールされていること（`node --version` で確認）

```
# Node.jsバージョン確認
node --version
# 出力例: v20.11.0

# npmも確認
npm --version
# 出力例: 10.2.4
```

### claude\_desktop\_config.json の場所

設定ファイルは以下の場所にあります。

| OS | パス |
| --- | --- |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

**ファイルが存在しない場合**  
Claude Desktopを一度起動すると自動生成されます。起動後、上記パスを確認してください。

### 設定ファイルの書き方

`claude_desktop_config.json` をテキストエディタで開き、以下のように編集します。

```
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Users/yourname/Desktop",
        "C:/Users/yourname/Documents"
      ]
    }
  }
}
```

**パスの指定について**  
`args` の3番目以降に、Claudeがアクセスを許可するフォルダのパスを指定します。セキュリティのため、最小限のフォルダのみを指定することをお勧めします。macOSの場合は `/Users/yourname/Desktop` のような形式です。

**Windowsのパス区切り文字について**  
JSON内のWindowsパスは、スラッシュ（`/`）またはバックスラッシュを2つ重ねた形（`\\`）で記述してください。バックスラッシュ1つ（`\`）はJSONのエスケープ文字として解釈されるためエラーになります。

* 正しい例：`"C:/Users/yourname/Desktop"` または `"C:\\Users\\yourname\\Desktop"`
* 誤った例：`"C:\Users\yourname\Desktop"` （バックスラッシュ1つはNG）

**セキュリティについて**  
GitHub等の外部サービスと連携するMCPサーバーを使う場合、トークンやAPIキーなどのシークレットは設定ファイルに直接書かず、環境変数で渡すようにしてください。

**設定完了後の操作：**

1. Claude Desktopを完全に終了する（タスクトレイからも終了）
2. Claude Desktopを再起動する
3. チャット画面の左下に「ツール」アイコンが表示されれば成功

### 動作確認

Claude Desktopのチャットで以下のように入力してみましょう。

**成功時の出力例：**

```
デスクトップには以下のファイル・フォルダがあります：

📁 フォルダ
- projects/
- screenshots/

📄 ファイル
- todo.txt（更新日: 2025-03-25）
- memo.md（更新日: 2025-03-27）
- report_draft.docx（更新日: 2025-03-20）
```

### トラブルシューティング TOP3

**1. ツールアイコンが表示されない**

* JSONの記述ミス（カンマの抜け、括弧の対応）がないか確認
* `npx` コマンドのパスが通っているか確認：`npx --version`
* Claude Desktopを完全終了して再起動

**2. 「ツールの実行に失敗しました」と表示される**

* 指定したフォルダパスが実際に存在するか確認
* Windowsの場合、パスの区切り文字を `/` または `\\` に統一（`\` 1つはNG）
* Node.jsのバージョンがv18以上であることを確認

**3. アクセス権限エラーが出る**

* 指定フォルダへの読み取り権限があるか確認
* Windowsの場合、管理者権限でClaude Desktopを起動してみる

> **このセクションのポイント：** 設定はJSONファイルを1つ書くだけ。トラブルの大半はJSONの記述ミスかパスの間違い。

---

ここからは発展編です。既存のMCPサーバーで物足りなくなったら、ぜひ挑戦してみてください。

発展編：TypeScriptでMCPサーバーを自作する

## 6. 自作MCPサーバーへの入口

「既存のMCPサーバーでは物足りない」「自社のAPIと連携したい」という場合は、MCPサーバーを自作できます。

Anthropicが公式SDKを提供しており、TypeScriptとPythonで使えます。

### TypeScriptによる最小構成のサンプル

**ビルドが必要です**  
TypeScriptのソースコードは、Node.jsで実行する前にJavaScriptへのコンパイル（ビルド）が必要です。以下の手順でビルド環境を整えてください。

```
# プロジェクト作成
mkdir my-mcp-server && cd my-mcp-server
npm init -y

# MCP SDK と zodをインストール（zodはスキーマ定義に必要）
npm install @modelcontextprotocol/sdk zod

# TypeScriptとNode.js型定義をインストール
npm install -D typescript @types/node
```

最小限の `tsconfig.json` を作成します。

```
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true
  },
  "include": ["src"]
}
```

```
// src/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// サーバーインスタンスを作成
const server = new McpServer({
  name: "my-first-mcp-server",
  version: "1.0.0",
});

// ツールを定義（AIが呼び出せる関数）
server.tool(
  "greet",                          // ツール名
  "指定した名前に挨拶する",           // 説明（AIがツール選択の参考にする）
  { name: z.string() },             // 引数のスキーマ（zodで型安全に定義）
  async ({ name }) => {             // 実際の処理
    return {
      content: [
        {
          type: "text",
          text: `こんにちは、${name}さん！MCPサーバーからお返事です。`,
        },
      ],
    };
  }
);

// stdioトランスポートで起動
// main関数でラップしてトップレベルawaitを避ける
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // stdoutはMCP通信に使用されるため、ログはstderrへ出力する
  console.error("MCPサーバーが起動しました");
}
main().catch(console.error);
```

ビルドして実行ファイルを生成します。

```
npx tsc
# dist/index.js が生成される
```

これを `claude_desktop_config.json` に追加すれば、Claudeから `greet` ツールを呼び出せます。

```
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["C:/path/to/my-mcp-server/dist/index.js"]
    }
  }
}
```

### 公式リソース

> **このセクションのポイント：** MCPサーバーの自作はSDKのおかげでシンプル。「ツール定義」「処理の実装」「トランスポート接続」の3ステップで動く。

## 7. まとめ — 今日できる3ステップアクション

この記事で学んだことをおさらいしましょう。

* **MCPとは：** AIに「手と目」を与えるオープンな通信規格（Anthropic提唱、2024年11月公開）
* **仕組み：** クライアント（Claude Desktop）↔ トランスポート ↔ サーバー（ツール提供）
* **できること：** ファイル操作・GitHub連携・Slack連携・DB操作・ブラウザ自動化など
* **始め方：** `claude_desktop_config.json` にJSON設定を1つ追加するだけ

### 今日できる3ステップアクション

**STEP 1（5分）：** `node --version` でNode.jsがv18以上であることを確認する。なければ[公式サイト](https://nodejs.org/ja)からv20 LTSをインストール。

**STEP 2（10分）：** `claude_desktop_config.json` にfilesystem MCPの設定を追加し、Claude Desktopを再起動する。

**STEP 3（5分）：** 「デスクトップのファイル一覧を教えて」とClaude Desktopに入力して、MCPサーバー経由でファイルが表示されることを確認する。

---

MCPの世界はまだ発展中で、毎週のように新しいサーバーが公開されています。まずはfilesystemで感触をつかんで、少しずつ自分のワークフローに組み込んでみてください。

「動いた！」という体験が、次のステップへの最大のモチベーションになります。
