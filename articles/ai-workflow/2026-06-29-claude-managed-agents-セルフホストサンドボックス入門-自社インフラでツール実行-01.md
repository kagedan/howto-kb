---
id: "2026-06-29-claude-managed-agents-セルフホストサンドボックス入門-自社インフラでツール実行-01"
title: "Claude Managed Agents セルフホストサンドボックス入門 — 自社インフラでツール実行"
url: "https://qiita.com/kai_kou/items/6fc806ec57620d989243"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "Python", "TypeScript", "qiita"]
date_published: "2026-06-29"
date_collected: "2026-06-29"
summary_by: "auto-rss"
query: ""
---

## はじめに

Anthropic は 2026 年 5 月 19 日（Code with Claude London）、Claude Managed Agents に **セルフホストサンドボックス（self-hosted sandboxes）** を追加したことを発表しました。現在は public beta として提供されています。

この記事では、セルフホストサンドボックスとは何か、どのようなアーキテクチャで動くのか、そして実際にどう構築するのかを、公式ドキュメントをもとに解説します。

### この記事で学べること

- セルフホストサンドボックスの仕組みと、クラウド実行との違い
- environment worker（ワークキュー方式）の動作モデル
- `ant` CLI / SDK を使ったワーカーの起動手順
- 対応マネージドプロバイダ（Cloudflare / Daytona / Modal / Vercel）の特徴

### 対象読者

- Claude のエージェント機能を業務で使いたいエンジニア
- 機密データやプライベートネットワークの制約でクラウド実行が難しい方
- エージェントの実行環境を自社のコンプライアンス・監査下に置きたい方

## TL;DR

- セルフホストサンドボックスは、**エージェントループは Anthropic 側に残したまま、ツール実行だけを自社インフラに移す** 仕組み
- ファイルシステム・プロセス・ネットワーク egress は自社の管理下に置かれる
- 自社で動かす **environment worker** が、Anthropic のワークキューからセッションをクレームして実行する
- `ant` CLI / SDK（Python・TypeScript・Go）に組み込みワーカーが同梱され、Cloudflare・Daytona・Modal・Vercel のマネージドプロバイダにも対応

## クラウド実行との違い

Managed Agents は、デフォルトでは Anthropic が管理するクラウドサンドボックス内でツールやコードを実行します。セルフホストサンドボックスは、オーケストレーションを Anthropic 側に残しつつ、ツール実行を自社が管理するインフラへ移します。エージェントのコード・ファイルシステム・ネットワーク egress が自社環境から外に出ない点が特徴です。

| | クラウド環境 | セルフホストサンドボックス |
|---|---|---|
| ツールの実行場所 | Anthropic 管理のサンドボックス | 自社インフラ |
| ネットワーク到達範囲 | Anthropic の egress 制御 | 自社のネットワークポリシー |
| ファイル/GitHub リポジトリのマウント | Anthropic が管理 | 自社が管理 |
| ライフサイクル | Anthropic が管理 | 自社が管理 |

ただし注意点として、ツールの **入力と出力は引き続き Anthropic のコントロールプレーンに流れます**。Claude がモデルとして結果を見て次の行動を判断するためです。「コードが実行される場所」は自社内に閉じますが、「モデルが結果を読む」フローは Anthropic 側に残ります。

セルフホストが向いているのは、次のようなケースです。

- ネットワーク境界の外に出せないデータをエージェントが扱う必要がある
- 公開ルーティングされていない社内サービスへ到達したい
- 自社のコンプライアンス・監査統制の下でエージェントを動かしたい

## アーキテクチャ: environment worker とワークキュー

セルフホストの中核は **environment worker** です。これは自社インフラ上で動かすプロセスで、Anthropic からツール実行リクエストを受け取り、ローカルで実行します。

`self_hosted` 環境は **ワークキュー** として機能します。セッションがその環境に割り当てられると、Anthropic はセッションをワークアイテムとしてキューに積みます。ワーカーは次の流れで処理します。

1. キューからワークアイテムをクレーム（claim）する
2. セッションごとの実行コンテキストを生成する
3. エージェントの **スキル**（ファイルベースの再利用可能なリソース）をダウンロードする
4. ツール呼び出しを実行する
5. 結果を Anthropic に返却する

ワークアイテムのクレーム方式は 2 通りあります。

- **always-on worker**: 常時ポーリングし続ける
- **webhook-triggered handler**: `session.status_run_started` イベントで起床してポーリングを開始する

CLI（`ant`）は always-on のみ、SDK は always-on と webhook の両方に対応します。

### サンドボックスのファイルシステム

- **`/workspace`**: ツール実行とスキルダウンロードのデフォルト作業ディレクトリ。スキルは `<workdir>/skills/<name>/` に展開される
- **`/mnt/session/outputs`**: 最終成果物の書き出し先。サンドボックスモードではこのパスにホストディレクトリをマウントすると、セッション終了後に成果物を取り出せる

## 構築手順

### 前提条件

- 既存のエージェント（なければ Quickstart で作成し agent ID を控える）
- `/bin/bash` を正確にそのパスに持つ Linux ホスト
  - TypeScript SDK は追加で `unzip` / `tar` / Node.js 22 以降が必要
  - Python SDK は標準ライブラリで完結し追加バイナリ不要
- `ant` CLI または Anthropic SDK（Python / TypeScript / Go）
- 2 つのクレデンシャル: ワーカー認証用の **環境キー** と、セッション作成・統計取得用の **Claude API キー**

### ステップ 1: セルフホスト環境を作成する

Console から `Workspace > Environments > New > Self-hosted` で作成できます。API でも作成可能です。

```python
import anthropic

client = anthropic.Anthropic()

environment = client.beta.environments.create(
    name="self-hosted", config={"type": "self_hosted"}
)
print(environment.id)
```

### ステップ 2: 環境キーを生成する

Console で対象環境を開き「Generate environment key」をクリックします。キー生成は（API で環境を作った場合でも）Console 専用です。生成したキーと環境 ID をワーカーホストに設定します。

```bash
export ANTHROPIC_ENVIRONMENT_KEY="sk-ant-oat01-..."
export ANTHROPIC_ENVIRONMENT_ID="env_..."
```

### ステップ 3: ワーカーを起動する

最もシンプルなのは always-on です。`ant` CLI なら 1 コマンドで起動できます。

```bash
ant beta:worker poll --workdir "/workspace"
```

SDK を使う場合は `EnvironmentWorker` ヘルパーを使います。

```python
import asyncio
import os
from anthropic import AsyncAnthropic
from anthropic.lib.environments import EnvironmentWorker


async def main() -> None:
    environment_key = os.environ["ANTHROPIC_ENVIRONMENT_KEY"]
    environment_id = os.environ["ANTHROPIC_ENVIRONMENT_ID"]
    async with AsyncAnthropic(auth_token=environment_key) as client:
        await EnvironmentWorker(
            client,
            environment_id=environment_id,
            environment_key=environment_key,
            workdir="/workspace",
        ).run()


asyncio.run(main())
```

ワーカーは SIGTERM / SIGINT を受けると、実行中のツール呼び出しをドレインしてからクリーンに終了します。

### ステップ 4: ワーカーの接続を確認する

別シェルから（環境キーではなく）Claude API キーで統計を確認し、`workers_polling` が 1 以上であることを確認します。

```bash
ant beta:environments:work stats --environment-id "$ANTHROPIC_ENVIRONMENT_ID"
```

`workers_polling` が 0 のままなら、ワーカーがキューに到達できていません。ワーカーホストで `ANTHROPIC_ENVIRONMENT_KEY` と `ANTHROPIC_ENVIRONMENT_ID` が設定されているか確認します。

## SDK ヘルパーの 3 レベル

SDK は制御レベルの異なる 3 つのヘルパーを提供します。多くのケースは `EnvironmentWorker` で済み、より細かい制御が必要なときに下位ヘルパーへ降りていく設計です。

- **`EnvironmentWorker`**: ポーリング・セットアップ・実行までを一括で扱う標準ワーカー。`.run()` は常駐し、`.handle_item()` は 1 セッションだけ処理して終了する
- **`work.poller()`**: ワークキューをポーリングし、クレームしたセッションを 1 件ずつ渡す。セッションごとにサンドボックスを起動するなど、自分で処理を決めたいときに使う
- **`client.beta.sessions.events.tool_runner()`**: 単一セッションのツール呼び出しだけを実行する。すでにワークをクレーム済みで実行レイヤだけ欲しいときに使う

## 対応マネージドプロバイダ

自社インフラで直接動かすほか、計算資源と分離をマネージドプロバイダに任せることもできます。それぞれ専用ガイドが用意されています。

| プロバイダ | 特徴 |
|-----------|------|
| **Cloudflare** | microVM ベースの分離、zero-trust シークレット注入、カスタマイズ可能な egress プロキシ |
| **Daytona** | フル構成可能なコンピュータ。長時間ステートフル、SSH/認証付きプレビュー URL、pause/restore に対応 |
| **Modal** | AI ワークロード向けクラウド。サブ秒起動、数十万の同時サンドボックスへスケール |
| **Vercel** | VM レベルのセキュリティ + VPC peering。ミリ秒起動、firewall でのクレデンシャル注入 |

## 運用時の注意点


> セルフホストサンドボックスでは **Memory 機能は現在サポートされていません**。また、Anthropic はファイルや GitHub リポジトリをセルフホストサンドボックスにマウントしません。セッション固有のファイルを渡すには、S3 パスやコミット SHA などの参照を session の `metadata` に入れ、ワーカー側でステージングします。


監視は `work.stats` で行えます。返り値の主なフィールドは次の通りです。

- `depth`: クレーム待ちのアイテム数（バックログのアラート・スケール判断に使う）
- `pending`: ワーカーがクレームして処理中のアイテム数
- `workers_polling`: 直近 30 秒間にポーリングしたワーカー数（死活監視に使う）

なお、これら監視系のエンドポイントは **環境キーではなく組織の API キー** で認証し、ワーカーホストの外から呼び出します。ワーカーホストに `ANTHROPIC_API_KEY` を置くと、組織スコープのクレデンシャルがエージェントのツール呼び出しに露出してしまうため避けてください。

## まとめ

- セルフホストサンドボックスは、エージェントループを Anthropic 側に残しつつツール実行を自社境界内に閉じる仕組み
- 中核は自社で動かす environment worker と、Anthropic 側のワークキュー
- `ant` CLI / SDK に組み込みワーカーが同梱され、always-on / webhook の両方式に対応
- Cloudflare・Daytona・Modal・Vercel のマネージドプロバイダで分離・計算を任せられる
- Memory 未対応・ファイルは metadata 経由で渡すなどの運用上の制約に注意

機密データやプライベートネットワークの制約でクラウド実行を見送っていた現場でも、Claude のエージェントを自社のコンプライアンス下で動かす道が開けました。プライベート MCP サーバーへ到達したい場合は MCP tunnels（research preview）との併用も検討できます。

## 参考リンク

- [New in Claude Managed Agents: self-hosted sandboxes and MCP tunnels（公式ブログ）](https://claude.com/blog/claude-managed-agents-updates) — 発表内容・プロバイダ概要
- [Self-hosted sandboxes（公式ドキュメント）](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) — アーキテクチャ・構築手順・SDK ヘルパー
- [Claude Managed Agents overview（公式ドキュメント）](https://platform.claude.com/docs/en/managed-agents/overview) — Managed Agents 全体像
