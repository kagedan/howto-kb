---
id: "2026-04-09-github-copilotのドキュメントを全部読んだので本当に使えるカスタマイズだけ10個まとめた-01"
title: "GitHub Copilotのドキュメントを全部読んだので、本当に使えるカスタマイズだけ10個まとめた"
url: "https://zenn.dev/miruky/articles/e7d9fe07646753"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

![スクリーンショット 2026-04-09 19.22.20.png](https://res.cloudinary.com/zenn/image/fetch/s--D01SG33Q--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3637204/0fa2f6d1-d3d8-4769-b713-d275c97d92d4.png?_a=BACAGSGT)

こんばんは、mirukyです。

最近、Claude CodeなどのAIコーディングツールの記事が増えていますが、VS Code純正の **GitHub Copilot** にもドキュメントを読み込まないと気づけない強力なカスタマイズ機能が大量に追加されています。

この記事では、VS Code公式ドキュメントとGitHub公式ドキュメントを全部読んだ上で、「知らないと確実に損する」実践的なカスタマイズを10個に厳選しました。すべてファイルを1つ作るだけ、または設定を1行変えるだけで即効果が出るものばかりです。

<https://docs.github.com/ja/copilot>

<https://code.visualstudio.com/docs>

## 目次

1. /initコマンドでcopilot-instructions.mdを自動生成する
2. .instructions.mdでファイル種別ごとにルールを分ける
3. .agent.mdでカスタムエージェントを作る
4. Handoffsでエージェント間ワークフローを組む
5. .prompt.mdで繰り返しタスクをスラッシュコマンド化する
6. SKILL.mdでポータブルなスキルを作る
7. Agent Hooksでファイル編集後に自動処理を走らせる
8. MCPサーバーをサンドボックスで安全に使う
9. BYOKで好きなモデルを使う
10. モノレポ対応の隠し設定を有効にする

## ①/initコマンドで copilot-instructions.md を自動生成する

これは多少GitHub Copilotを使用していれば結構知られているものだと思います。

`.github/copilot-instructions.md` はリポジトリ全体に適用されるカスタム指示ファイルです。コーディング規約、技術スタック、アーキテクチャパターンなどをMarkdownで記述すると、Copilotがすべてのチャットリクエストで自動的に参照します。

ポイントは、 **これを手書きする必要がない** ということです。

チャットで `/init` と入力するだけで、Copilotがプロジェクト構造を解析し、最適な `copilot-instructions.md` を自動生成します。

生成されるファイルには以下のような内容が含まれます。

* プロジェクトの技術スタック宣言
* コーディングスタイルと命名規則
* 使用するライブラリとフレームワーク
* エラーハンドリングのパターン
* テストの方針

## ②.instructions.md でファイル種別ごとにルールを分ける

`copilot-instructions.md` がプロジェクト全体に適用されるのに対し、 `.instructions.md` ファイルは **特定のファイルやフォルダにだけ** ルールを適用できます。

`.github/instructions/` ディレクトリに配置し、YAMLフロントマターの `applyTo` でglob パターンを指定します。

```
---
name: 'React規約'
description: 'Reactコンポーネントのコーディング規約'
applyTo: '**/*.tsx'
---
# React コーディング規約

- 関数コンポーネントのみ使用する
- Propsの型定義にはinterfaceを使う
- useEffectの依存配列を省略しない
```

`applyTo` には複数パターンをカンマ区切りで指定できます。

```
---
applyTo: '**/*.ts,**/*.tsx'
---
```

ディレクトリ構造で整理することも可能です。

```
.github/instructions/
  frontend/
    react.instructions.md
    accessibility.instructions.md
  backend/
    api-design.instructions.md
  testing/
    unit-tests.instructions.md
```

| ファイル | 適用範囲 |
| --- | --- |
| copilot-instructions.md | プロジェクト全体（常時適用） |
| \*.instructions.md | applyToパターンに一致するファイルのみ |
| AGENTS.md | プロジェクト全体（複数AIエージェント対応） |

## ③.agent.md でカスタムエージェントを作る

`.agent.md` ファイルを作ると、Copilotに **専用のペルソナ** を持たせることができます。エージェントごとに使えるツール、モデル、指示を制限できるため、安全性と精度が大幅に向上します。

`.github/agents/` ディレクトリに配置します。

```
---
description: コードの設計レビューを行う
tools: ['search', 'web']
model: Claude Sonnet 4 (copilot)
---

あなたはシニアアーキテクトです。以下の観点でコードをレビューしてください。

- SOLID原則に違反していないか
- 責務の分離が適切か
- テスタビリティが確保されているか
- セキュリティ上の問題がないか

コードの修正は行わず、問題点の指摘と改善案の提示のみ行ってください。
```

このファイルを保存すると、チャットのエージェントドロップダウンに **自動的に表示** されます。

重要なのは `tools` プロパティです。たとえばレビュー用エージェントに `search` と `web` だけを許可すれば、コードを勝手に変更される心配がなくなります。

| プロパティ | 説明 |
| --- | --- |
| description | エージェントの説明（チャット入力欄にプレースホルダーとして表示） |
| tools | 使用可能なツールのリスト |
| model | 使用するAIモデル（省略時はモデルピッカーの選択値） |
| agents | サブエージェントとして呼び出せるエージェントのリスト |
| handoffs | 次のエージェントへの引き継ぎ設定 |
| hooks | エージェント固有のフック設定（Preview） |

## ④Handoffs でエージェント間ワークフローを組む

Handoffsは、あるエージェントの作業完了後に **次のエージェントへボタン1つで引き継ぐ** 機能です。たとえば「設計エージェント → 実装エージェント → レビューエージェント」という一連の流れを構築できます。

`.agent.md` のフロントマターに `handoffs` を追加します。

```
---
description: 実装計画を生成する
tools: ['search', 'web']
handoffs:
  - label: 実装を開始する
    agent: implementation
    prompt: 上記の計画に基づいて実装してください。
    send: false
---

あなたはプランナーです。以下の手順で実装計画を作成してください。

1. 既存コードの構造を調査する
2. 変更が必要なファイルを特定する
3. 各ファイルの変更内容を箇条書きで示す
4. テスト方針を提示する
```

チャットでこのエージェントが応答を返すと、 **「実装を開始する」ボタン** が表示されます。ボタンを押すと `implementation` エージェントに切り替わり、プロンプトが自動入力されます。

`send: true` にすると、ボタンを押した瞬間にプロンプトが自動送信されます。各ステップで人間がレビューする場合は `send: false`（デフォルト）のままにしておくのがおすすめです。

## ⑤.prompt.md で繰り返しタスクをスラッシュコマンド化する

`.prompt.md` ファイルを使うと、よく使うプロンプトを **スラッシュコマンド** として登録できます。チャットで `/` と入力するとリストに表示されます。

`.github/prompts/` ディレクトリに配置します。

```
---
description: 'PRの説明文を生成する'
agent: agent
tools: ['changes']
---

以下の変更内容を分析し、プルリクエストの説明文を日本語で作成してください。

## フォーマット
- タイトル: 変更内容を一文で要約
- 概要: 何をなぜ変更したか
- 変更点: 箇条書きで主要な変更を列挙
- テスト: テスト方針と確認事項
```

使い方はチャットに `/create-pr-description` と入力するだけです。

プロンプトファイルでは **入力変数** も使えます。

```
---
description: 'コンポーネントのスキャフォールディング'
---

${input:componentName:コンポーネント名} という名前のReactコンポーネントを作成してください。

- ${input:componentType:関数コンポーネント or クラスコンポーネント}で作成
- テストファイルも同時に作成する
```

| プロパティ | 説明 |
| --- | --- |
| description | スラッシュメニューに表示される説明 |
| agent | 実行するエージェント（ask, agent, plan, またはカスタムエージェント名） |
| tools | 使用可能なツールのリスト |
| model | 使用するAIモデル |

## ⑥SKILL.md でポータブルなスキルを作る

Agent Skillsは `.instructions.md` の上位互換のような存在です。指示だけでなく、 **スクリプト、テンプレート、サンプルコード** をまとめてパッケージ化できます。さらに、VS Code、GitHub Copilot CLI、Copilot coding agentの間で **ポータブル** に動作するオープンスタンダードです。

`.github/skills/` ディレクトリにスキルごとのフォルダを作り、 `SKILL.md` を配置します。

```
.github/skills/
  webapp-testing/
    SKILL.md
    test-template.js
    examples/
      login-test.js
```

```
---
name: webapp-testing
description: 'Webアプリケーションのテストを作成・実行する'
---

# テスト作成手順

1. [テストテンプレート](./test-template.js)を参照して新しいテストを作成する
2. テスト対象のコンポーネントをimportする
3. 正常系・異常系・境界値テストを網羅する
4. `npm test` で実行し、結果を確認する
```

スキルはチャットで `/webapp-testing` とスラッシュコマンドで呼び出せます。

| 比較項目 | Agent Skills | Custom Instructions |
| --- | --- | --- |
| 目的 | 専門的なワークフローを定義 | コーディング規約を定義 |
| ポータビリティ | VS Code、CLI、coding agentで共通 | VS CodeとGitHub.comのみ |
| 内容 | 指示、スクリプト、リソース | 指示のみ |
| 適用 | オンデマンド（必要時のみロード） | 常時適用またはglobパターン |

Copilotはスキルの `name` と `description` を読んで、タスクに関連するスキルを **自動的に判断してロード** します。参照されていないファイルはコンテキストに読み込まれないため、多数のスキルをインストールしてもコンテキストを圧迫しません。

## ⑦Agent Hooks でファイル編集後に自動処理を走らせる

Agent Hooksは、エージェントセッションの **特定のライフサイクルポイント** でシェルコマンドを自動実行する機能です。カスタム指示やプロンプトが「ガイド」であるのに対し、Hooksは **確定的な自動処理** を提供します。

`.github/hooks/` ディレクトリにJSONファイルを配置します。

**【ファイル編集後に自動フォーマット】**

```
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\""
      }
    ]
  }
}
```

**【危険なコマンドをブロック】**

```
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "./scripts/validate-tool.sh",
        "timeout": 15
      }
    ]
  }
}
```

対応しているライフサイクルイベントは8種類あります。

| イベント | タイミング | 用途 |
| --- | --- | --- |
| SessionStart | セッション開始時 | リソース初期化、プロジェクト状態の検証 |
| UserPromptSubmit | プロンプト送信時 | リクエストの監査、コンテキスト注入 |
| PreToolUse | ツール実行前 | 危険な操作のブロック、承認要求 |
| PostToolUse | ツール実行後 | フォーマッター、リンター、テストの自動実行 |
| PreCompact | コンテキスト圧縮前 | 重要なコンテキストの退避 |
| SubagentStart | サブエージェント生成時 | サブエージェントの追跡、リソース初期化 |
| SubagentStop | サブエージェント完了時 | 結果集約、クリーンアップ |
| Stop | セッション終了時 | レポート生成、クリーンアップ |

`PreToolUse` フックでは `permissionDecision` を返すことで、特定のツール呼び出しを `allow`（自動承認）、 `deny`（拒否）、 `ask`（確認要求）のいずれかに制御できます。

## ⑧MCP サーバーをサンドボックスで安全に使う

MCPサーバーは外部ツール連携を可能にしますが、 **ローカルで任意のコードを実行できる** という性質上、セキュリティリスクがあります。macOSとLinuxでは **サンドボックス機能** を使って、ファイルシステムとネットワークのアクセスを制限できます。

`.vscode/mcp.json` でサーバーごとにサンドボックス設定を行います。

```
{
  "servers": {
    "myServer": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "sandboxEnabled": true,
      "sandbox": {
        "filesystem": {
          "allowWrite": ["${workspaceFolder}"]
        },
        "network": {
          "allowedDomains": ["api.example.com"]
        }
      }
    }
  }
}
```

`sandboxEnabled: true` にすると、サーバーは隔離された環境で実行されます。明示的に許可したパスとドメインにしかアクセスできなくなります。

さらに、サンドボックスが有効な場合は **ツール呼び出しが自動承認** されます。制御された環境で動作するため、毎回確認ダイアログを出す必要がないという判断です。

## ⑨BYOK で好きなモデルを使う

BYOK（Bring Your Own Key）を使うと、組み込みモデル以外のAIモデルをCopilotのチャットで利用できます。ローカルで動作するOllamaのモデルや、OpenAI互換のAPIエンドポイントを追加できます。

設定手順は以下の通りです。

1. チャットのモデルピッカーから **Manage Models** を選択
2. **Add Models** を選択し、プロバイダーを選ぶ
3. APIキーまたはエンドポイントURLを入力
4. モデルを選択

対応しているビルトインプロバイダーの例として、OpenAI、Anthropic、Google、Azure OpenAI、Ollamaなどがあります。

また、VS Code 1.104以降では **Auto model selection** が利用できます。モデルピッカーで `Auto` を選択すると、VS Codeがモデルのパフォーマンスやレート制限の状況を自動判断し、最適なモデルを選んでくれます。現在、Claude Sonnet 4、GPT-5、GPT-5 miniなどの中から自動選択されます。

| 機能 | 説明 |
| --- | --- |
| BYOK | 自分のAPIキーで外部モデルを追加 |
| Auto | VS Codeがリアルタイムで最適なモデルを自動選択 |
| Thinking Effort | モデルピッカーからモデルごとに推論の深さを調整 |

## ⑩モノレポ対応の隠し設定を有効にする

モノレポでサブフォルダだけをVS Codeで開いている場合、デフォルトではリポジトリルートのカスタマイズファイルが **読み込まれません** 。これは多くの人が気づかずにハマるポイントです。

`settings.json` に以下の1行を追加するだけで解決します。

```
{
  "chat.useCustomizationsInParentRepositories": true
}
```

この設定を有効にすると、VS Codeはワークスペースフォルダから `.git` フォルダが見つかるまで上位ディレクトリを遡り、その間にあるすべてのカスタマイズファイルを収集します。

```
my-monorepo/              # リポジトリルート（.gitあり）
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/
│   │   └── style.instructions.md
│   ├── prompts/
│   │   └── review.prompt.md
│   └── agents/
│       └── reviewer.agent.md
├── packages/
│   └── frontend/          # ← ここだけ開いている場合
│       └── src/
```

この例では `packages/frontend/` だけを開いていても、ルートの `copilot-instructions.md`、 `style.instructions.md`、 `review.prompt.md`、 `reviewer.agent.md` がすべて検出されます。

対象となるカスタマイズの種類は以下の通りです。

* `copilot-instructions.md`（常時適用指示）
* `AGENTS.md`（常時適用指示）
* `.instructions.md`（ファイルベース指示）
* `.prompt.md`（プロンプトファイル）
* `.agent.md`（カスタムエージェント）
* `SKILL.md`（Agent Skills）
* Hooks（フック設定）

## おわりに

ここまでお読みいただきありがとうございます。

GitHub Copilotのカスタマイズ機能は、ドキュメントを読まないと存在すら知らないものが多く、設定ファイル1つで開発体験が大きく変わります。

特に `copilot-instructions.md` と `.instructions.md` の組み合わせはすぐに試せて効果も高いので、まだ設定していない方はぜひ `/init` コマンドから始めてみてください。

ではまた、お会いしましょう。

## 参考リンク

### VS Code公式ドキュメント

### GitHub公式ドキュメント

### コミュニティ
