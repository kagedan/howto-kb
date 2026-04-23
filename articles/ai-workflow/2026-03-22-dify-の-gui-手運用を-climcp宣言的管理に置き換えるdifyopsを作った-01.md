---
id: "2026-03-22-dify-の-gui-手運用を-climcp宣言的管理に置き換えるdifyopsを作った-01"
title: "Dify の GUI 手運用を CLI・MCP・宣言的管理に置き換える「DifyOps」を作った"
url: "https://zenn.dev/cacc_lab/articles/178a9333e99dda"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## 3つのアプリに同じプロンプト変更を反映するのに30分ほどかかった

セルフホスト版の Dify を運用していて、ある日気づきました。

GUI で1つのアプリの設定を変えて、同じ変更を残り2つにも反映して、ナレッジベースを更新して、変更前の設定をメモしておいて――**全部手作業**。

**「作る」のは簡単なのに「運用する」のがひたすら面倒**。この摩擦を解消するために、**DifyOps** を作りました。

![DifyOps CLI デモ](https://static.zenn.studio/user-upload/deployed-images/2afbfec1b096ff61cb550a91.gif?sha=33d2d7747c1630a0f79a640bfe113d84537f72ae)

## DifyOps が目指したもの

単なる「Dify を CLI で触れるようにすること」ではありません。目指したのは、Dify の運用を

* **再現可能**にする（desired state を YAML で定義して `plan` → `apply`）
* **差分で管理**できるようにする（環境比較、アプリ比較、DSL 比較）
* **AI から安全に操作**できるようにする（MCP 38 ツール + 安全柵 3 層）
* **変更履歴を追える**ようにする（状態変更系の監査ログ + スナップショット）

ことでした。

なぜ「Ops」と名付けたのか。**単発のコマンド実行ではなく、状態管理・監査・再現・ロールバックまでを含む運用基盤**だからです。

> Product: **DifyOps** / GitHub repo: `difyops` / CLI & Python package: `dify-admin`

DifyOps はセルフホスト版 Dify v1.13+ 向けです。DSL YAML の手動編集ではなく、**MCP サーバーとしてツールを公開し、その内部で Dify Console API を操作する**アプローチです。ワークフローの「作成」ではなく「運用」にフォーカスしています。

**MCP（Model Context Protocol）** は、AI アシスタントが外部ツールを呼び出すための標準プロトコルです。DifyOps は MCP サーバーとして 38 ツールを公開しており、Claude Code や Cursor から自然言語で Dify を操作できます。

## Before / After

### Before（GUI 手運用）

* GUI で同じ設定変更を3アプリに手で反映 → **30分**
* 変更前の設定を別ファイルにメモ → **忘れる**
* ナレッジベースの更新は手動アップロード → **漏れる**
* 誰が何を変えたか → **曖昧**
* dev と prod の差分 → **見えない**

### After（DifyOps）

* CLI / MCP で同じ変更を数コマンドで再現可能
* 変更前にスナップショットを取得 → **いつでも復元**
* KB 同期を `--checksum --dry-run` で実行 → **差分だけ更新**
* 状態変更系の操作が JSONL 監査ログに自動記録 → **追跡可能**
* `env-diff` で dev / prod を比較 → **一発で見える**

## ある日の運用：FAQ Bot の設定変更

具体的な運用シナリオを通しで見てみます。

### 1. 変更前にスナップショットを取る

```
dify-admin apps snapshot --name "FAQ Bot"
# → Snapshot taken: 20260322T090000Z
```

### 2. モデルと temperature を変更

```
dify-admin apps config patch --name "FAQ Bot" \
  --set model.name=gpt-4o \
  --set model.completion_params.temperature=0.7
```

MCP 経由なら「FAQ Bot の temperature を 0.7 に、モデルを gpt-4o にして」と話しかけるだけ。

### 3. ナレッジベースを同期

```
dify-admin kb sync --name "社内マニュアル" ./docs/ \
  --recursive --checksum --dry-run
# → Upload: 2 files, Skipped: 15 (checksum match), Delete: 0

dify-admin kb sync --name "社内マニュアル" ./docs/ \
  --recursive --checksum --yes
```

### 4. prod との差分を確認

```
dify-admin env-diff \
  --source-url http://dev:5001 \
  --target-url http://prod:5001
```

### 5. 監査ログを確認

```
「さっき何を変更した？」
→ 2026-03-22T09:00:15Z  config_patch app   FAQ Bot
   2026-03-22T09:01:30Z  sync         kb    社内マニュアル
```

もし問題があれば `apps restore` で一発復元。

### CLI + Web UI 連動デモ

![CLI + Web UI 連動デモ](https://static.zenn.studio/user-upload/deployed-images/e76c35abb4bffee15b2e5907.gif?sha=09dd380dbc0de34001a043f018ab0454034cf195)

CLI でコマンドを実行すると、Dify の Web UI がリアルタイムで変化します。

## 主要機能

多くのアプリ / KB 操作では `--name "FAQ Bot"` のように名前指定が使えます。ただし、差分比較や復元など一部の操作では ID 指定が必要です。

### Config Patching

JSON の丸ごと上書きではなく、dot-notation で特定の値だけ変更。

```
dify-admin apps config patch --name "FAQ Bot" \
  --set model.completion_params.temperature=0.7
```

### Desired State（宣言的管理）

YAML で「あるべき状態」を定義して、差分プレビュー → 適用。IaC（Infrastructure as Code）のように Dify の状態をコードで管理。

```
# state.yml
apps:
  - name: "FAQ Bot"
    mode: chat
    description: "Customer FAQ"
  - name: "Analyzer"
    mode: advanced-chat

knowledge_bases:
  - name: "Company Docs"
    description: "Internal documentation"
```

```
dify-admin plan state.yml        # 差分を確認（read-only）
dify-admin apply state.yml --yes # 適用（DESTRUCTIVE）
```

### その他

* **ナレッジベース同期** — `kb sync --checksum --recursive --dry-run`
* **スナップショット / ロールバック** — `apps snapshot` / `apps restore`
* **環境差分比較** — `env-diff --source-url dev --target-url prod`
* **アプリ複製** — `apps clone --name "FAQ Bot" --clone-name "FAQ Bot v2"`
* **テンプレート作成** — `apps scaffold chat-rag --name "RAG Bot"`

38 ツールの全一覧は [GitHub リポジトリ](https://github.com/CaCC-Lab/difyops) の README をご覧ください。

## セットアップ

```
# GitHub からインストール
pip install git+https://github.com/CaCC-Lab/difyops.git

# MCP サーバーも使う場合（dify-admin[mcp] が extras）
pip install "dify-admin[mcp] @ git+https://github.com/CaCC-Lab/difyops.git"
```

環境変数を設定（または `.env` ファイルに記載）:

```
export DIFY_URL=http://localhost:5001
export DIFY_EMAIL=admin@example.com
export DIFY_PASSWORD=password
```

Claude Code の `.mcp.json`:

```
{
  "mcpServers": {
    "difyops": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/difyops", "--extra", "mcp", "dify-admin", "mcp", "serve"],
      "env": {
        "DIFY_URL": "http://localhost:5001",
        "DIFY_EMAIL": "admin@example.com",
        "DIFY_PASSWORD": "password"
      }
    }
  }
}
```

## 安全設計

AI に運用を任せるなら、安全柵が必須です。DifyOps は 3 層で守ります。

**第1層：DESTRUCTIVE マーカー** — 状態変更ツールに `DESTRUCTIVE:` を付与。AI が実行前確認を促せる。

**第2層：read-only モード** — `DIFY_ADMIN_MODE=readonly` で全 DESTRUCTIVE ツールをサーバー側ブロック。

**第3層：explain ツール** — 操作の目的・リスク・取り消し方法を事前確認。

```
「apps_delete って何するの？」
→ アプリを完全に削除します。元に戻せません。
  リスク: high
  取り消し方法: 事前に apps_snapshot でスナップショットを取ってください
```

> MCP 側の確認フローは、最終的にはクライアント実装に依存します。サーバー側で一律にブロックするのは read-only モードのみです。

## 技術スタック

* **Python 3.10+** / `httpx` + `click` + `rich` + `pyyaml`
* **MCP SDK**（FastMCP）で 38 ツールを公開
* **Dify Console API**（Cookie + CSRF 認証）
* テスト 60 本 / CI（pytest + ruff lint/format + mypy）

## 向いている人 / 向いていない人

### 向いている人

* Dify をセルフホストで複数アプリ運用している
* GUI の手作業を減らしたい
* dev / prod の差分や変更履歴を管理したい
* Claude Code / Cursor から Dify を触りたい
* ナレッジベースの更新を CI/CD に組み込みたい

### 向いていない人

* cloud.dify.ai しか使わない
* 単発で1アプリだけ触れれば十分

### 既知の制限

* **セルフホスト版 Dify v1.13+ 専用**（cloud.dify.ai 非対応）
* `advanced-chat` / `workflow` モードでは `apps_config_get` / `apps_config_set` が使えません（Dify API の制約）
* MCP 経由の確認フローはクライアント実装に依存します

## おわりに

Dify を「作る道具」としてだけでなく、「継続的に運用する対象」として扱いたいなら、GUI だけではすぐ限界が来ます。DifyOps は、その運用を CLI・MCP・宣言的管理で支えるための基盤として作りました。同じ悩みを持つ人には、かなり刺さるはずです。
