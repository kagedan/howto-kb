---
id: "2026-05-27-mastra-announce-mastra-workspaces-発表-エージェントに実際の作業環-01"
title: "[Mastra Announce] Mastra Workspaces 発表 ― エージェントに「実際の作業環境」を与える仕組み"
url: "https://zenn.dev/shiromizuj/articles/6f3f1705de70ab"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

※やや昔のアナウンスをさかのぼって記事にしています

---

2026年2月5日、Mastra は **Workspaces** についてのアナウンスを行いました。これは 1月30日発表の、Mastra Ver1.1 で追加された機能で、AIエージェントがファイル操作・コマンド実行・コンテンツ検索・再利用可能なスキルを、制御された環境で安全に扱えるようにする仕組みです。

---

## 背景

### 「話すだけのエージェント」から「実際に動くエージェント」へ

LLM ベースのエージェントは、自然言語でタスクを理解し、計画を立て、回答を生成することが得意です。しかし従来の構成では、エージェントは「テキストを出力するだけ」にとどまりがちでした。ファイルを読み書きしたり、シェルコマンドを走らせたり、ローカルのドキュメントを検索したりするには、開発者がツールを個別に実装する必要がありました。

加えて、「どこまでエージェントに許可を与えるか」という権限管理の問題もありました。ファイル書き込みを許すと削除もできてしまう、コマンド実行を許すと危険な操作も実行できてしまう、といった問題です。システムプロンプトで「削除はしないでください」と伝えても、エージェントがその指示に従う保証はありません。

### Agent Skills 仕様との関係

Mastra Workspaces は、同日に発表された **Mastra Skills** と密接に関係しています。[Agent Skills 仕様](https://agentskills.io/home) に準拠した `SKILL.md` ファイルをワークスペースの `skills` 機能として組み込むことで、エージェントは「どのスキルが使えるか」を自律的に発見し、必要なときだけ読み込む（プログレッシブ・ディスクロージャー）ことができます。

Workspaces はこれを「コンテキストの注入」だけでなく、「実際の実行環境の提供」まで拡張した仕組みと言えます。

---

## ニュースリリースの内容紹介

### 発表の概要

* **日時**: 2026年2月5日
* **著者**: Paul Scanlon（Mastra Technical Product Marketing Manager）
* **発表内容**: Mastra Workspaces のリリース。ファイルシステム・サンドボックス・検索・スキルの 4 機能を組み合わせ、エージェントの実行環境を安全・細粒度に制御できる仕組み。

### 発表の要点

1. **4 つの機能コンポーネント**: Filesystem（ファイルアクセス）、Sandbox（コマンド実行）、Skills（再利用可能な指示）、Search（コンテンツ検索）
2. **細粒度の権限制御**: ツール単位で `requireApproval` や `requireReadBeforeWrite` を設定可能
3. **設定はコードで宣言**: `Workspace` クラスにオプションを渡すだけで環境を構成できる
4. **同じスキル・異なる権限**: 同一スキルセットを持ちながら権限の異なる複数エージェントを安全に構築できる
5. **Mastra Studio 対応**: Studio 上でワークスペースのファイルブラウザが使えるように

---

## 具体的な掘り下げ

### Workspace クラスの設計

`Workspace` は `@mastra/core/workspace` から import するクラスで、エージェントに渡す「実行環境の設定オブジェクト」です。エージェントの `workspace` プロパティに渡すだけで、そのエージェントが使えるツールセットが自動的に展開されます。

```
import { Workspace, LocalFilesystem, LocalSandbox } from "@mastra/core/workspace";

const diagramWorkspace = new Workspace({
  id: "diagram-workspace",
  name: "Diagram Rendering Workspace",
  filesystem: new LocalFilesystem({ basePath: "./diagram-demo" }),
  sandbox: new LocalSandbox({ workingDirectory: "./diagram-demo" }),
  skills: ["/skills"],
  bm25: true,
  autoIndexPaths: ["/docs", "/skills"]
});

const diagramAgent = new Agent({
  id: "diagram-agent",
  model: "anthropic/claude-sonnet-4",
  workspace: diagramWorkspace  // ← ここで紐づける
});
```

### 4 つの機能コンポーネント詳解

#### 1. Filesystem（ファイルシステム）

```
filesystem: new LocalFilesystem({
  basePath: "./my-dir",   // アクセスを許可するディレクトリ
  readOnly: true          // 読み込みのみ許可する場合
})
```

`basePath` 外のファイルにはアクセスできないため、エージェントが意図しないディレクトリを触れない構造になっています。

#### 2. Sandbox（コマンド実行）

```
sandbox: new LocalSandbox({
  workingDirectory: "./my-dir",  // 作業ディレクトリ
  env: { MY_VAR: "value" }       // 環境変数の注入
})
```

ローカルでシェルコマンドを実行します。後述の権限設定で承認フローをはさむことができます。

#### 3. Skills（スキル）

```
skills: ["/skills"]   // SKILL.md を含むディレクトリを指定
```

[Agent Skills 仕様](https://agentskills.io/home) に従った `SKILL.md` ファイルのパスを渡します。エージェントは起動時にスキルのメタデータを読み込み、必要なタスクが発生したときに本文や参照ドキュメントをオンデマンドで取得します。

#### 4. Search（検索）

```
bm25: true,                            // BM25 キーワード検索を有効化
autoIndexPaths: ["/docs", "/skills"]   // 起動時にインデックス化するパス
```

`bm25: true` でキーワード検索、`vector: true` でセマンティック検索（埋め込みベクトルによる類似検索）をそれぞれ有効にできます。両方同時に有効にすることも可能です。

### 権限制御の仕組み

`tools` プロパティで、`WORKSPACE_TOOLS` 定数を使ってツールごとに権限を設定できます:

```
import { WORKSPACE_TOOLS } from "@mastra/core/workspace";

const workspace = new Workspace({
  // ...
  tools: {
    [WORKSPACE_TOOLS.FILESYSTEM.WRITE_FILE]: {
      requireApproval: true,        // 実行前にユーザー承認を要求
      requireReadBeforeWrite: true, // 書き込み前に必ず読み込みを要求
    },
    [WORKSPACE_TOOLS.SANDBOX.EXECUTE_COMMAND]: {
      requireApproval: true,        // コマンド実行前に承認を要求
    },
  }
});
```

**ポイント**: この制御は「システムプロンプトに書いた指示」ではなく、「設定レイヤーでのハードな制限」です。エージェントが指示を無視したとしても、権限なしには実行できません。

### 同一スキル・異なる権限のデモ

公式デモでは、同じスキルセット（`beautiful-mermaid` と `mastra` スキル）にアクセスできる 2 つのエージェントを用意しています:

| エージェント | Filesystem | Sandbox | コマンド実行承認 |
| --- | --- | --- | --- |
| `diagramAgent` | ✅ | ✅ | 承認必要 |
| `noSandboxAgent` | ✅ | ❌ | - |

「ダイアグラムを作って SVG にしてください」と両方に依頼すると:

* `diagramAgent`: スキルを読み込み → 承認リクエスト → `render.ts` 実行 → SVG 生成
* `noSandboxAgent`: スキルを読み込み → ファイル書き込みまでは可能 → `render.ts` は実行できない

**設計上の意図**: 同一のスキル知識を持ち、異なることができるエージェントを簡潔な設定差分だけで作り分けられる。スキルと権限は独立して管理される。

### ディレクトリ構成例

```
diagram-demo/
├── docs/          # 検索インデックスに追加される追加ドキュメント
├── skills/
│   ├── beautiful-mermaid/
│   │   ├── SKILL.md              # Mermaid 記法と SVG 変換の指示
│   │   ├── references/
│   │   │   └── mermaid-syntax.md # Mermaid 構文リファレンス
│   │   └── scripts/
│   │       └── render.ts         # .mmd → .svg 変換スクリプト
│   └── mastra/
│       ├── SKILL.md              # Mastra フレームワーク知識
│       └── references/           # API リファレンスなど
└── svg/           # 生成された SVG の保存先
```

`basePath` で指定したディレクトリが「エージェントの世界」のルートになります。エージェントはこのディレクトリ外のファイルにはアクセスできません。

### Mastra Studio との統合

Studio を起動すると、ワークスペースに設定されたディレクトリ構造をブラウザで確認できるファイルブラウザが利用できます。どのスキルが有効になっているかも一緒に確認できます。

---

## 今後の展開

公式発表では次のロードマップが示されています:

| 機能 | 概要 |
| --- | --- |
| **リモートサンドボックス** | E2B などのクラウドプロバイダーで隔離された環境でコマンドを実行 |
| **クラウドファイルシステム** | S3、GCS などのクラウドストレージを `LocalFilesystem` と同様に扱える |
| **スコープ付きワークスペース** | 会話単位・ユーザー単位で独立したワークスペースを提供（マルチテナント対応） |

特に「スコープ付きワークスペース」は、Claude Desktop のようにユーザーごとにエージェントの作業領域を分離する UseCaseへの対応で、SaaS プロダクトへの組み込みを想定した機能と考えられます。

---

## まとめ

Mastra Workspaces は、AIエージェントを「テキストを生成するエンティティ」から「実際の作業を実行するエンティティ」へと進化させるための基盤です。権限はコードで宣言し、「エージェントへの信頼」ではなく「設定による制限」でセキュリティを担保するアプローチは、本番環境でエージェントを運用する際に必要な考え方と言えます。

**参考リンク**
