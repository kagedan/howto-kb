---
id: "2026-05-31-mastra-announce-最大の発表ついに登場-エンジニアと非エンジニアが一緒にエージェントを-01"
title: "[Mastra Announce] 最大の発表ついに登場！ エンジニアと非エンジニアが一緒にエージェントを作る Agent Builder"
url: "https://zenn.dev/shiromizuj/articles/ca906f165e7e2b"
source: "zenn"
category: "construction"
tags: ["MCP", "API", "AI-agent", "OpenAI", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースで解説します。ただの直訳ではなく、関連情報も補いながら、なるべく「何がうれしいのか」「前は何が足りなかったのか」まで分かるように整理します。速報性重視のため一部は公開情報ベースの解釈を含みますが、事実と推測は分けて書きます。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## ロードマップで「最大の発表」と予告されていたもの

2026年5月4日、MastraのCo-FounderでCPOのShane Thomasが登壇したロードマップウェビナーで、セッション最後のパートとして「最大の発表」が披露されました。そのときの模様はこちらの記事で詳しく紹介しています。

<https://zenn.dev/shiromizuj/articles/f8ed4ed72c414b>

ウェビナーのその場でShaneが語った言葉を振り返ると、発表の文脈がよく分かります。

> 「エンジニアリングチームが社内の他部署から『私たちにもエージェントを使わせてくれ』と圧力をかけられている」

OpenClawや各種AIエージェントが話題になるたびに「私たちにもあれがほしい」と言われる。でもコードは書けない。では誰が作るのか？——その問いに対する、Mastraとしての答えがこれです。

「エンジニアが王国を守りながら、他の人が遊び場で楽しめるようにする」とShaneは表現していました。

そのウェビナーから約3週間後の2026年5月28日、MastraのCEO Sam Bhagwatによる公式アナウンスとして **Mastra Agent Builder** が正式に発表されました。

---

## Agent Builder が解決する課題：「エージェントはエンジニアだけのものか？」

### 大組織での社内 AI の現実

公式アナウンスには印象的な具体例が挙げられています。Marsh McLennan は専任エンジニアリングチームで約 7 万 5000 人の社員が使う検索アプリケーションを構築し、Softbank はドキュメント自動化のために Satto Workspace を出荷しました。

これは大企業の事例ですが、同じ構造は中規模のチームでも起きています。

* マーケティングチームが「競合の動向を毎朝レポートするエージェントがほしい」と言う
* カスタマーサポートが「FAQ を参照しながら回答をドラフトするエージェントがほしい」と言う
* 経営企画が「売上データを集計して週次サマリーを書くエージェントがほしい」と言う

全部もっともな要求です。しかしエンジニアチームのリソースは有限で、すべてのリクエストに答えられるとは限りません。かといって「Difyを使ってください」と丸投げするにも、社内のデータソースや既存ツールとの連携を非エンジニアが一から設定するのは困難です。

### Mastra 自身も同じ問題を抱えていた

アナウンスの中で Sam は自チームの体験も語っています。

> 「私たちの小さなチームですら、通話録音からフィードバックをまとめるエージェント、メトリクスを自動投稿するエージェント、GitHub リリースノートのドラフトを作るエージェントによって、はるかに効率的になっています。しかし私たちは全員エンジニアです。」

これは重要な自己言及です。Mastra チーム自体が「エンジニアしかいないから何とかなっているが、これを全社展開するとなると話が変わる」という壁を認識していた。

---

## Agent Builder の全体像：コンポーザブルなエージェントスタジオ

公式アナウンスにあるシンプルな説明が核心をついています。

> 「Agent Builder をコンポーザブルなエージェントスタジオとして捉えてください：開発者がツールを書き、モデルを選び、ワークフローを構築します。非開発者のチームメンバーは Builder UI を使って、それらのプリミティブをエージェントに組み立てます。」

つまり Agent Builder は、エンジニアが作ったピース（ツール・モデル設定・ワークフロー）を使って、非エンジニアがエージェントを「組み立てる」ための場所です。

**エンジニア側がやること**

* ツール・MCP接続・インテグレーション・ワークスペース・スキルを設定する
* どのツール/モデル/ワークフローを誰に使わせるかをコードで制御する（アローリスト方式）
* RBAC で誰が何にアクセスできるかを制御する

**非エンジニア側がやること**

* 自然言語でエージェントを構築する（バイブコーディング）
* 作ったエージェントを社内の共有ライブラリに公開する
* 他のメンバーが作ったエージェントを発見・再利用する
* Slack 連携でワンクリックインストール——作ったエージェントをそのままチャンネルに投入する

このデザインのポイントは、**「エンジニアが全体を設計し、非エンジニアがその範囲内で自律する」** という役割分担が明確であることです。エンジニアはセキュリティやガバナンスの責任を負ったまま、チームメンバーが自分でエージェントを作れる環境を提供できます。

---

## 技術的な仕組み：コードで制御されたアーキテクチャ

### セットアップの基本

まず必要なパッケージをインストールします。

```
npm install @mastra/editor @mastra/libsql
```

`createBuilderAgent` は `@mastra/editor/ee`（EE = Enterprise Edition）からインポートする点に注目してください。これが後述するライセンス要件と関係しています。

```
// src/mastra/index.ts
import { Mastra } from '@mastra/core/mastra'
import { MastraEditor } from '@mastra/editor'
import { createBuilderAgent } from '@mastra/editor/ee'
import { LibSQLStore } from '@mastra/libsql'

export const mastra = new Mastra({
  storage: new LibSQLStore({ url: 'file:./mastra.db' }),
  agents: { builderAgent: createBuilderAgent() },
  editor: new MastraEditor({
    builder: {
      enabled: true,
      configuration: {
        agent: {
          memory: { observationalMemory: true },
        },
      },
    },
  }),
})
```

開発サーバーを起動すると：

Agent Builder は `http://localhost:4111/agent-builder` でアクセスできます。

### 前提条件

Agent Builder が動くには3つの要件があります。

1. **ストレージ**: `Mastra` インスタンスに `@mastra/core` のストレージアダプターが必要。エージェント、メモリ、ワークスペースの状態はすべて `Mastra.storage` を通じて永続化されます。
2. **Builder エージェント**: `createBuilderAgent()` ファクトリで作成した Builder エージェントを `Mastra.agents` に登録する必要があります。チャットベースのエディタはこれを通じて動作します。登録なしだと 404 が返ります。
3. **OPENAI\_API\_KEY**: `createBuilderAgent()` で作成される Builder エージェントは OpenAI モデルで動作するため、環境変数 `OPENAI_API_KEY` が必要です。

### ツール・エージェント・ワークフローのアローリスト

アローリスト方式が Agent Builder のセキュリティモデルの核心です。

```
editor: new MastraEditor({
  builder: {
    enabled: true,
    configuration: {
      agent: {
        tools: { allowed: ["crm-lookup-tool", "ticket-search-tool"] },
        agents: { allowed: ["account-research-agent"] },
        workflows: { allowed: ["customer-onboarding-workflow"] },
        models: { allowed: [{ provider: "openai" }, { provider: "anthropic" }] },
        memory: { observationalMemory: true }
      }
    }
  }
})
```

アローリストのセマンティクスはシンプルです。

| 設定 | 挙動 |
| --- | --- |
| `allowed` を省略 | 制限なし。全登録エントリがピッカーに表示される |
| `allowed: []` | 明示的ロックダウン。ピッカーは空になる |
| `allowed: [...ids]` | リストされた ID のみがピッカーに表示される |

これにより、「このチームには CRM ツールと Slack 連携だけ使わせる」「このロールには読み取り専用ワークフローしか見せない」といった細かい制御がコードレベルで完結します。

### MCP ツールも使える

MCP（Model Context Protocol）ツールも同じ方法で利用できます。`MCPClient.getTools()` でツールを取得して `tools` マップに展開するだけです。エンジニアが設定した MCP サーバーのツール群を、非エンジニアが Builder UI から使えるようになります。

### フィーチャートグルで UI をカスタマイズ

`builder.features.agent` で Builder UI に表示するセクションを制御できます。

```
new MastraEditor({
  builder: {
    enabled: true,
    features: {
      agent: {
        tools: true,
        agents: true,
        workflows: true,
        skills: true,
        memory: true,
        model: true,
        browser: true,
        avatarUpload: true,
        favorites: true,
      },
    },
  },
})
```

例えば `browser: false` にするとブラウザタブが非表示になります。エンジニアは「この機能は今のチームには早い」と判断したものを UI レベルから隠せます。

### エージェントのライフサイクル

Builder UI で作られたエージェントは、公開されるまで **非公開（private）** です。公開前に **ドラフト状態** に置くこともできます。公開されると Agent Builder UI の共有ライブラリに表示され、他のチームメンバーが発見・チャット・再利用できるようになります。

---

## RBAC：きめ細かいアクセス制御

### 2つのロール

Agent Builder には `admin` と `member` の2つのロールが組み込まれています。

| ロール | 権限 | 説明 |
| --- | --- | --- |
| `admin` | `*`（全アクセス） | エージェントとスキルの作成・編集・公開・削除。全 Builder サーフェスを管理。 |
| `member` | スコープされたアローリスト | Builder を開く、エージェントとスキルを閲覧、ピッカーを使う、Builder エージェントとチャット。 |

### パーミッションの文法

パーミッションパターンは `resource:action` 形式です。ワイルドカードが使えます。

* `*` — フルアクセス（全リソース、全アクション）。`admin` で使用。
* `agent-builder:*` — `agent-builder` リソースへの全アクション。
* `*:read` — 全リソースへの `read`。

`member` が Builder を普通に使うために必要な最低限のパーミッションセットはドキュメントで定義されています。

```
// WorkOS を使った RBAC の例
const rbacProvider = new MastraRBACWorkos({
  roleMapping: {
    admin: ['*'],
    member: [
      'agent-builder:*',
      'agents:read',
      'agents:execute',
      'stored-agents:*',
      'stored-skills:*',
      'stored-workspaces:*',
      'tools:read',
      'tools:execute',
      'workflows:read',
      'workflows:execute',
      'memory:read',
      'channels:read',
      'infrastructure:read',
    ],
    _default: [],
  },
})
```

`@mastra/auth-workos` パッケージで WorkOS との SSO・RBAC 統合がすぐに使えます。WorkOS 側の組織ロールを Mastra の `admin`/`member` にマッピングするだけです。`_default` は WorkOS のマッピングにないロールを持つユーザーの扱いを定義します（空配列 `[]` にするとアクセス拒否になります）。

---

## Slack 連携：作ったエージェントをそのまま Slack へ

### Channels の仕組み

Channels は、Builder で作ったエージェントを Mastra サーバーの外にいるユーザーに届ける仕組みです。現時点では Slack が唯一サポートされているチャネルです。

```
npm install @mastra/slack
```

```
import { SlackProvider } from '@mastra/slack'

export const mastra = new Mastra({
  storage,
  channels: {
    slack: new SlackProvider({
      refreshToken: process.env.SLACK_APP_CONFIG_REFRESH_TOKEN,
      baseUrl: process.env.SLACK_BASE_URL,
    }),
  },
  agents: { builderAgent: createBuilderAgent() },
  editor: new MastraEditor({
    builder: { enabled: true },
  }),
})
```

`SlackProvider` は Slack アプリの作成、OAuth、スラッシュコマンド、メッセージルーティングをすべて処理します。Builder で作ったエージェントが Slack のチャンネルに対応するかどうかは、エージェント単位でオプトインします。

### 認証トークンの管理

`SLACK_APP_CONFIG_REFRESH_TOKEN` は Slack の Your App Configuration Tokens から取得できる無期限のリフレッシュトークンです。発行されるアクセストークンは12時間ごとに自動ローテーションされ、`Mastra.storage` に自動永続化されます。`SlackProvider` を使うには `Mastra` インスタンスに永続ストレージが必要なのはこのためです。

ローカル開発では `cloudflared tunnel --url http://localhost:4111` のようなトンネルを使って、Slack のイベント送信先として公開 URL を確保します。

---

## Skill Registries：コミュニティスキルのエコシステム

Agent Builder には [skills.sh](https://skills.sh/) レジストリとの統合が組み込まれています。

```
new MastraEditor({
  builder: {
    enabled: true,
    registries: {
      skillsSh: { enabled: true },
    },
  },
})
```

これを有効にすると、Builder のライブラリタブに Browse ビューが表示され、エンドユーザーはコミュニティスキルをプレビューして自分のエージェントにインストールできます。エンジニアが1から書かなくても、コミュニティが作ったスキルをそのまま利用できる仕組みです。

---

## 重要な問い：セルフホストでもライセンスが必要なのか？

### 答え：「本番デプロイ」には必要。「ローカル試用」は不要。

ユーザーが抱くであろう最初の疑問をここで正面から扱います。公式アナウンスにはこう書かれています。

> 「Agent Builder はセルフホスティングで利用可能で、Mastra プラットフォーム上ではエンタープライズエディションライセンスの下で利用できます。Mastra Studio でローカルに試すことはできますが、**デプロイするにはライセンスキーが必要**です。」

ドキュメントの[Overview](https://mastra.ai/docs/agent-builder/overview)ページにも明記されています。

> 「注意: Agent Builder は Mastra Enterprise Edition の一部です。本番デプロイには有効な EE ライセンスが必要です。」

そして[Deploying](https://mastra.ai/docs/agent-builder/deploying)ページでは、さらに具体的に書かれています。

> 「デプロイ環境に `MASTRA_EE_LICENSE` を設定してください。`builder.enabled` が truthy の場合、有効なライセンスなしにサーバーは起動を拒否します。ライセンスキーはシークレットとして扱ってください。」

整理すると次の通りです。

| 利用形態 | ライセンス要否 |
| --- | --- |
| `npx mastra dev`（ローカル開発） | 不要。自由に試せる |
| Mastra Platform 上でのホスティング | EE ライセンス必要 |
| **セルフホスト本番デプロイ** | **EE ライセンス必要** |

セルフホストであっても「本番として動かす」なら `MASTRA_EE_LICENSE` 環境変数が必要で、それがない状態でサーバーを起動しようとすると拒否されます。「セルフホストだからフリーで使える」というわけではありません。

### これは Mastra として初めてのことか？

**Yes、これは Mastra としての初めての Enterprise Edition（EE）機能です。**

Mastra はこれまで、フレームワーク・Studio・Server・Memory Gateway・Platform のすべてが MIT ライセンスで、商用利用を含めて完全無償でした。EE ライセンスという概念が存在しなかったのです。

今回の Agent Builder は、その歴史の中で初めて「本番デプロイには有効なライセンスキーが必要」と明示された機能です。`@mastra/editor/ee` という `ee` サフィックスのついたエントリポイントからインポートする `createBuilderAgent` が、このアーキテクチャを象徴しています。

ただし、重要な点として **コアフレームワーク（`@mastra/core`）は引き続き MIT ライセンス** です。ツール・エージェント・ワークフロー・Observational Memory・RAG・ストリーミングなど、これまでの機能はすべて従来通り無償で使えます。Agent Builder という「チームで共有するプラットフォーム」の部分だけが EE 対象になっています。

### なぜ EE 化したのか（私的考察）

公式には理由が詳しく語られているわけではありませんが、機能の性質から考えると自然な流れとも言えます。

Agent Builder が解決しようとしているのは、「エンジニアリングチームが社内の非エンジニアにエージェントを使わせたい」という組織規模の問題です。RBAC、監査ログ、WorkOS SSO 統合、マルチテナント対応——これらの要件を持つのは、ほぼ確実にある程度の規模の企業です。

個人開発者や小規模スタートアップには `npx mastra dev` でローカル試用できる道が残されており、「最初の壁」は低く保たれています。本番で組織規模にスケールさせたい場合に EE ライセンスを取得するという構造は、いわゆる "Open Core" モデルに近い形です。

ライセンスの取得は [コンタクトフォーム](https://mastra.ai/contact) または [カレンダー予約](https://calendly.com/josh-mastra/agent-builder-chat?month=2026-06) から。現状はセールスとの会話を通じた個別対応になっているようです。

---

## 本番デプロイの全体像

ローカル開発から本番へ移行するとき、変わるのはコードの構造ではなく「プロバイダー」です。

**必要な6要素**

1. **EE ライセンス** — `MASTRA_EE_LICENSE` 環境変数
2. **ホスト型ストレージ** — LibSQL Cloud、PostgreSQL など複数インスタンスで共有できるストア
3. **共有ワークスペースファイルシステム** — S3、GCS、Azure など（ローカルはシングルノードのみ）
4. **クラウドサンドボックス** — E2B、Docker、Vercel など（ローカルサンドボックスは共有環境では安全でない）
5. **Auth & RBAC** — Builder UI と `/agent-builder/*` ルートを保護する
6. **チャネル向けの公開ベース URL** — Slack などがアクセスできる URL

コードで示すと次のようになります。

```
import { s3FilesystemProvider } from '@mastra/s3'
import { e2bSandboxProvider } from '@mastra/e2b'

new Mastra({
  storage: new LibSQLStore({
    url: process.env.DATABASE_URL!,
    authToken: process.env.DATABASE_AUTH_TOKEN,
  }),
  editor: new MastraEditor({
    filesystems: { [s3FilesystemProvider.id]: s3FilesystemProvider },
    sandboxes: { [e2bSandboxProvider.id]: e2bSandboxProvider },
    builder: {
      enabled: true,
      configuration: {
        agent: {
          workspace: {
            type: 'inline',
            config: {
              name: 'builder-workspace',
              filesystem: {
                provider: s3FilesystemProvider.id,
                config: {
                  bucket: process.env.S3_BUCKET!,
                  region: process.env.S3_REGION!,
                },
              },
              sandbox: {
                provider: e2bSandboxProvider.id,
                config: { apiKey: process.env.E2B_API_KEY! },
              },
            },
          },
        },
      },
    },
  }),
})
```

ドキュメントで「A local sandbox can't run commands safely in a shared environment」と警告されている通り、本番環境でクラウドサンドボックスなしで動かすことは推奨されません。

---

## Composio 統合：来週出荷予定

アナウンスの末尾には次の一文があります。

> 「このバージョンには自然言語ビルダーとガバナンスレイヤーが含まれており、来週 Composio サポートが出荷されます。」

[Composio](https://composio.dev/) は 250 以上のアプリ（GitHub、Notion、Salesforce、Jira など）との統合を提供するエージェントインテグレーションプラットフォームです。これが Agent Builder に統合されると、非エンジニアが Builder UI から Composio のインテグレーションライブラリを直接選んでエージェントに接続できるようになります。

ロードマップウェビナーでも「Composio・Arcadeなどのインテグレーションプロバイダーとの連携も計画中」と述べられていたので、予告通りの展開です。

---

## 「すべてのエージェントはただのコード」

アナウンスで強調されているもうひとつの重要な点があります。

> 「構築されたエージェントはすべて『ただのコード』なので、どこでも実行できます。」

Agent Builder の UI で作られたエージェントは、裏側では `Mastra.storage` に保存される構造化されたエージェント設定です。ベンダーロックインではなく、エクスポートして通常の Mastra エージェントとして動かすことができます。「ノーコードで作ったけど後でコードに落とし込みたい」というシナリオも想定された設計になっています。

---

## まとめ

Mastra Agent Builder は、「エージェント開発はエンジニアだけのものか？」という問いに対するひとつの答えです。エンジニアがコードで安全な枠組みを作り、非エンジニアがその中で自律的にエージェントを組み立てる——この役割分担を仕組みとして提供するのが Agent Builder の本質です。

技術的に注目すべき点をまとめます。

* **コードファーストのガバナンス**: アローリスト方式でエンジニアがコードレベルで制御範囲を定義する
* **IAM スタイルの細粒度 RBAC**: `resource:action` パターンと glob ワイルドカードで柔軟に権限を設定できる
* **コミュニティスキルエコシステム**: skills.sh レジストリとの統合でエージェントの能力を拡張できる
* **Slack チャンネル統合**: Builder で作ったエージェントをそのまま Slack に投入できる
* **「ただのコード」哲学**: UI で作ったエージェントもコードとして扱えるため、ロックインがない

そして最後に重要な事実として——**これは Mastra 初の Enterprise Edition 機能**です。ローカル開発は引き続き無償で試せますが、本番デプロイにはセルフホストであっても EE ライセンスが必要になりました。コアフレームワーク（`@mastra/core`）は MIT ライセンスを維持しており、これまでの機能は変わらず使えます。

デプロイやライセンスについての詳細は [公式ドキュメント](https://mastra.ai/docs/agent-builder/overview) か [コンタクトフォーム](https://mastra.ai/contact) で確認してください。

---

## 関連リンク
