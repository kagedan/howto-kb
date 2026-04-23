---
id: "2026-04-17-mastra-announce-リモートサンドボックスで信頼されていないコードを安全に実行する-01"
title: "[Mastra Announce] リモートサンドボックスで信頼されていないコードを安全に実行する"
url: "https://zenn.dev/shiromizuj/articles/e05b0f22d60c10"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

※やや昔のアナウンスをさかのぼって記事にしています

---

2026年3月11日、Mastra は**リモートサンドボックス**のサポートを発表しました。エージェントコードを分離されたクラウドコンテナで安全に実行するための 3 つの新しいサンドボックスプロバイダーが利用可能になります。

---

## 背景

### アプリケーションサーバーと同じ場所でコードを実行する問題

エージェントがパッケージのインストール、信頼されていないコードの実行、または長期的なプロセスの起動を行う場合、アプリケーションサーバー上でそれを行うのは望ましくありません。CPU やメモリをワークロード間で奪い合うだけでなく、エージェントが何か破壊的なことをした場合の影響範囲が広がってしまいます。

### リモートサンドボックスによる解決

Mastra の [ワークスペース](https://mastra.ai/blog/announcing-mastra-workspaces) がリモートサンドボックスに対応しました。最初のプロバイダーとして [Daytona](https://mastra.ai/reference/workspace/daytona-sandbox)、[E2B](https://mastra.ai/reference/workspace/e2b-sandbox)、[Blaxel](https://mastra.ai/reference/workspace/blaxel-sandbox) の 3 つをリリースし、今後さらに追加予定です。

各サンドボックスには専用のファイルシステム、ネットワーク、プロセス空間があります。エージェントのワークロードが CPU やメモリを奪い合うことはなく、エージェントが何か破壊的なことをしても、その影響範囲は最小限に抑えられます。

---

## ニュースリリースの内容紹介

### 発表の概要

* **日時**: 2026年3月11日
* **著者**: Paul Scanlon（Mastra Technical Product Marketing Manager）
* **発表内容**: Mastra Workspaces のリモートサンドボックス対応。Daytona、E2B、Blaxel の 3 プロバイダーを新たにサポートし、エージェントコードを分離されたクラウドコンテナで安全に実行できるようにする。

### 発表の要点

1. **3 つの新プロバイダー追加**: Daytona、E2B、Blaxel のリモートサンドボックスをサポート
2. **既存の Workspace API と完全互換**: `sandbox` を差し替えるだけでプロバイダーを切り替え可能
3. **各プロバイダーに特徴あり**: ネットワーク制御・テンプレート・マルチランタイムなど用途に応じて選択できる
4. **コールドスタートの最適化**: スナップショットやテンプレートの事前ビルドで起動を高速化できる
5. **ローカル開発からのパス**: `LocalSandbox` でローカル開発し、本番ではリモートに切り替えるシームレスな移行が可能

---

## 具体的な掘り下げ

### ワークスペースの構造

ワークスペースには 2 つのレイヤーがあります。

* **ファイルシステム**: ファイルが置かれる場所（ローカルディスク、S3、GCS）
* **サンドボックス**: コマンドが実行される場所（ローカル、Daytona、E2B、Blaxel）

以下のようにエージェントに `workspace` プロパティとして渡します。`sandbox` を差し替えるだけでプロバイダーを切り替えられます。

```
// src/mastra/agents/agent.ts

import { Agent } from "@mastra/core/agent";
import { Workspace, LocalFilesystem, LocalSandbox } from "@mastra/core/workspace";

export const agent = new Agent({
  id: "agent",
  name: "Agent",
  model: "anthropic/claude-sonnet-4-6",
  workspace: new Workspace({
    mounts: {
      "/data": new LocalFilesystem({ basePath: "./my-data" }),
    },
    sandbox: new LocalSandbox(),
  }),
});
```

`mounts` はパスを [S3](https://mastra.ai/reference/workspace/s3-filesystem) や [GCS](https://mastra.ai/reference/workspace/gcs-filesystem) などのファイルシステムプロバイダーにマッピングし、エージェントがクラウドストレージをローカルファイルシステムと同じように扱えます。`sandbox` はコマンドが実際に実行される場所で、どのファイルシステムとも組み合わせ可能です。

エージェントにワークスペースを割り当てると、Mastra はファイルの読み書き、ディレクトリの一覧取得・検索、コマンドの実行を行うためのツールを提供します。これらのツールはどのサンドボックスが設定されていても同じように動作します。

---

### Daytona

[@mastra/daytona](https://mastra.ai/reference/workspace/daytona-sandbox) は Daytona SDK をラップし、スナップショット、ネットワーク分離、永続ボリューム、リソース設定をサポートします。

```
// src/mastra/agents/agent.ts

import { Agent } from "@mastra/core/agent";
import { Workspace } from "@mastra/core/workspace";
import { DaytonaSandbox } from "@mastra/daytona";

export const agent = new Agent({
  id: "agent",
  name: "Agent",
  model: "anthropic/claude-sonnet-4-6",
  workspace: new Workspace({
    sandbox: new DaytonaSandbox({
      apiKey: process.env.DAYTONA_API_KEY,
      target: "us",
      language: "typescript",
      snapshot: "my-snapshot-id",
    }),
  }),
});
```

#### Daytona の主な機能

| 機能 | 概要 |
| --- | --- |
| **スナップショット** | サンドボックスイメージを事前設定し、コールドスタートをほぼ瞬時に。依存関係や FUSE ツールを 1 回含めるだけで毎起動時の手間を省けます。 |
| **ネットワーク分離** | `networkBlockAll: true` で全アウトバウンドをブロック、`networkAllowList` で特定の CIDR をホワイトリスト化。外部 API 呼び出しを強制的に禁止できます。 |
| **永続ボリューム** | サンドボックス再起動を超えてデータが保持されます。`volumes` オプションで接続し、停止・再起動してもデータが残ります。 |
| **エフェメラルモード** | `ephemeral: true` で停止時にサンドボックスが即削除。一度きりのタスクに最適です。 |
| **リソース設定** | CPU、メモリ、ディスクを GiB 単位で設定できます。 |
| **再接続** | 同じ `id` をコンストラクタに渡すと既存のサンドボックスに再接続。停止中・アーカイブ済みは自動再起動、破棄済みは新規作成します。 |
| **直接 SDK アクセス** | `sandbox.instance` で Daytona のベースオブジェクトに直接アクセスできます。 |

---

### E2B

[@mastra/e2b](https://mastra.ai/reference/workspace/e2b-sandbox) は E2B SDK をラップし、テンプレートベースのサンドボックス、バックグラウンドプロセス、セルフホストデプロイメントをサポートします。

```
// src/mastra/agents/agent.ts

import { Agent } from "@mastra/core/agent";
import { Workspace } from "@mastra/core/workspace";
import { E2BSandbox } from "@mastra/e2b";

export const agent = new Agent({
  id: "agent",
  name: "Agent",
  model: "anthropic/claude-sonnet-4-6",
  workspace: new Workspace({
    sandbox: new E2BSandbox({
      apiKey: process.env.E2B_API_KEY,
      template: "my-custom-template",
      timeout: 300_000,
    }),
  }),
});
```

#### E2B の主な機能

**テンプレート**: 4 つの設定方法があります。

1. 既存の E2B テンプレートを使うためにテンプレート ID 文字列を渡す
2. `TemplateBuilder` を使ってプログラム的に定義する（`aptInstall`、`pipInstall`、`npmInstall`）
3. デフォルトテンプレートをカスタマイズする関数を渡す
4. 何も渡さず、`s3fs` と FUSE がプリインストールされたデフォルトテンプレートを使用する

テンプレートは決定論的にハッシュ化されるため、同じ設定は同じテンプレート ID を生成します。一度ビルドされると、インスタンス間で再利用されます。

**セルフホストサポート**: `domain`、`apiUrl`、`accessToken` を設定して、自社の E2B デプロイメントに向けることができます。

**バックグラウンドプロセス**: `E2BProcessManager` 経由で完全サポート。`spawn()`、`get()`、`kill()`、`sendStdin()` とストリーミング出力コールバックが使えます。`get(pid)` で外部から起動したプロセスへの再接続も可能です。

---

### Blaxel

[@mastra/blaxel](https://mastra.ai/reference/workspace/blaxel-sandbox) は Blaxel SDK をラップし、9 つの言語ランタイム、ポート公開、TTL ベースのライフサイクル管理をサポートします。

```
// src/mastra/agents/agent.ts

import { Agent } from "@mastra/core/agent";
import { Workspace } from "@mastra/core/workspace";
import { BlaxelSandbox } from "@mastra/blaxel";

export const agent = new Agent({
  id: "agent",
  name: "Agent",
  model: "anthropic/claude-sonnet-4-6",
  workspace: new Workspace({
    sandbox: new BlaxelSandbox({
      timeout: "5m",
      memory: 4096,
      runtimes: ["node", "python", "bash"],
      ports: [{ name: "api", target: 3000, protocol: "HTTP" }],
    }),
  }),
});
```

#### Blaxel の主な機能

| 機能 | 概要 |
| --- | --- |
| **9 つのランタイム** | Node、Python、Bash、Ruby、Go、Rust、Java、C++、R。デフォルトは `['node', 'python', 'bash']` ですが任意の組み合わせで設定可能。 |
| **ポート公開** | サンドボックス内でサーバーを起動し、外部からアクセス可能にします。HTTP、TCP、UDP をサポート。 |
| **TTL ベースのライフサイクル** | `'5m'` や `'1h'` などの人間が読みやすいタイムアウト文字列。TTL が切れるとサンドボックスが停止します。 |
| **アボートシグナル** | `abortSignal` で実行中のコマンドをキャンセルでき、部分的な出力は結果に保持されます。 |

> **注意**: Blaxel は stdin に非対応です。実行中プロセスへの入力送信が必要な場合は Daytona または E2B を使用してください。

---

## プロバイダーの選び方

状況次第ですが、判断の指針を整理します。

**Daytona** がおすすめな場合:

* ネットワーク分離、永続ボリューム、きめ細かいリソース制御が必要
* スナップショットにより、コールドスタートが重要な繰り返し環境に適している
* 最も多くの設定オプションと最も堅牢な再接続ロジックが必要

**E2B** がおすすめな場合:

* エフェメラルで素早く起動するサンドボックスが必要
* テンプレートシステムで一度ビルドすれば再利用したい
* 永続状態を必要としないコード実行タスク

**Blaxel** がおすすめな場合:

* 幅広いランタイムサポートが必要（Go、Rust など）
* サンドボックス内でのサーバー起動とポート公開が必要
* TTL ベースのシンプルなライフサイクル管理

3 つすべてが S3 や GCS のマウント、バックグラウンドプロセス、自動再接続をサポートしています。Mastra の `Workspace` API はすべてのプロバイダーで同一なので、**プロバイダーの切り替えは 1 行の変更**で済みます。

### コールドスタートを速くするための事前ビルド

すべてのプロバイダーが、FUSE ツールのランタイムインストールを避けるための事前ビルドをサポートしています。クラウドストレージをマウントする場合、事前ビルドは特に価値があります（`gcsfuse` のゼロからのインストールには数秒かかり、リクエストをまたいで積み重なるため）。

| プロバイダー | 事前ビルド方法 |
| --- | --- |
| **Daytona** | `s3fs` と `gcsfuse` をプリインストールしたスナップショットを作成する |
| **E2B** | `TemplateBuilder.aptInstall()` でカスタムテンプレートをビルドする |
| **Blaxel** | ツールを組み込んだカスタム Docker イメージを使用する |

---

## まとめ

エージェントはコードを実行する必要がありますが、アプリケーションサーバーと同じ場所でそれを行うのは望ましくないでしょう。Daytona、E2B、Blaxel はそれぞれ、その実行を高速に起動し自身でクリーンアップする分離コンテナに移動するための手段を提供します。

`LocalSandbox` を使ってローカルで開発してから、本番環境ではリモートプロバイダーに切り替えられます。まず 3 つのプロバイダーから始め、近日中にさらに追加予定です。

セットアップガイドとプロバイダー固有の設定については、[サンドボックスドキュメント](https://mastra.ai/docs/workspace/sandbox)をご参照ください。ファイルシステム、マウント、サンドボックスがどのように組み合わさるかの全体像については、[ワークスペース概要](https://mastra.ai/docs/workspace/overview)をご覧ください。
