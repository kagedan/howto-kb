---
id: "2026-06-01-claude-managed-agents-on-cloudflare-の構築と実際に試してみて使い-01"
title: "Claude Managed Agents on Cloudflare の構築と実際に試してみて使い道とメリット"
url: "https://zenn.dev/takaakisuzuki/articles/33a2d1b4e859df"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "zenn"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

Anthropic が提供する **Claude Managed Agents (CMA)** は、Claude を「ブラウザ + サンドボックス + 各種ツール」を持つ常駐エージェントとして動かす仕組みです。

通常は Anthropic 側がサンドボックスのインフラまで丸ごと面倒を見てくれますが、**Cloudflare の Sandbox SDK + Workers** で **Cloudflareサービス上に sandbox を載せる** ことができます。これを **self-managed environment** と呼びます。

<https://blog.cloudflare.com/claude-managed-agents/>  
<https://github.com/cloudflare/claude-managed-agents>

こちらの内容を実際に試して整理します。

## アーキテクチャ — 「脳」と「手」を分ける

CMA の世界観は、Anthropic が「**Decoupling the brain from the hands**」と表現している通り:

* **脳 (Anthropic 側)**: モデル推論 / エージェントループ / Tool 呼び出しの判断
* **手 (Cloudflare 側)**: 実際にコードが走るサンドボックス / 外部 API への通信 / ファイル永続化![](https://static.zenn.studio/user-upload/623e66d5af87-20260601.png)

エージェントセッションが始まると、Anthropic が Cloudflare 上の Worker (control plane) に webhook を投げ、その Worker がセッション専用のサンドボックスを 1 つ作って割り当てる、という流れです。Sandbox は MicroVM (Container) と Isolate (V8) のどちらかを backend として選択でき、ツール実行結果は逆方向 (Cloudflare → Anthropic) に戻されます。

### 2 つの sandbox backend

| 観点 | MicroVM (Containers) | Isolate (V8) |
| --- | --- | --- |
| 起動時間 | 秒オーダー | ミリ秒 |
| 実行環境 | フル Linux + 任意 CLI | V8 isolate + Codemode |
| ファイルシステム | フル POSIX | Agents SDK 仮想 FS |
| 並列規模 | 数百〜数千 | 数万〜 |
| シェル | あり (`/ws/terminal` でライブ接続) | なし |
| コスト | per-second VM | per-request |

> ざっくり: **既存 CLI を回したい・1 タスクが重い → MicroVM**、**軽量で大量並列 → Isolate**。同じ control plane に両方を混在させられます。

## 構築 — Cloudflare 上に control plane を立てる

![](https://static.zenn.studio/user-upload/4ee1c467b657-20260601.png)

#### 前提条件

* Workers **Paid** プラン以上 (Containers と Worker Loader binding が必要)
* Anthropic Console のアカウント + API キー
* (任意) Workers VPC binding を使うなら GCP/AWS との VPC ピアリング設定

#### 1. リポジトリを clone してデプロイ

```
git clone https://github.com/cloudflare/claude-managed-agents.git
cd claude-managed-agents
pnpm install

# secrets の登録
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler secret put WEBHOOK_SECRET   # HMAC 用

# Workers / Containers / D1 / KV のプロビジョニング
pnpm wrangler deploy
```

`wrangler.jsonc` には、container image、Durable Objects migrations、egress policy 用の KV、ダッシュボード経由で agent ↔ backend を紐付ける D1 などが定義されています。

#### 2. Anthropic 側に environment を登録

`ant` CLI で **self-managed environment** を作り、Cloudflare Worker の URL を webhook 先として登録します:

```
ant beta:environments create \
  --webhook-url https://<your-worker>.workers.dev/webhooks
```

![](https://static.zenn.studio/user-upload/ed80df768a33-20260601.png)

返ってきた `env_xxx` ID と、合わせて発行される **environment key** をメモしておきます。後で `ant beta:agents create` で紐付けます。

#### 3. Agent を作る

```
ant beta:agents create \
  --name "demo-agent" \
  --model claude-sonnet-4-6 \
  --environment-id env_xxx
```

![](https://static.zenn.studio/user-upload/4aaa9f68e28d-20260601.png)

`backend` フィールド (`isolate` または `microvm`) を JSON で渡すか、ダッシュボードの **Agents → New Agent → Backend** ラジオで選びます。

#### 4. Egress Policy を設定 (推奨)

外部通信を制御する **Egress Policy** は 4 種類あります:

| タイプ | 何ができるか |
| --- | --- |
| Allow / Deny list | 許可ホストの絞り込み・危険サイトのブロック |
| VPC Routing | 社内ホスト名を VPC binding にルーティング |
| Header Injection | API キーを Worker 側で付与 (エージェントは平文を見ない) |
| Custom Proxy | JS で監査ログ / 追加加工 / 任意のミドルウェア |

ダッシュボードの **Egress Policies** タブで JSON を作って agent に attach します。

![](https://static.zenn.studio/user-upload/d1de7b1c8a5a-20260601.png)

#### 5. デプロイ完了の確認

```
# 環境の存在確認
ant beta:environments list

# Worker のヘルスチェック
curl https://<your-worker>.workers.dev/health
```

ダッシュボード (`https://<your-worker>.workers.dev/`) で **Agents / Sessions / Webhook Events / Egress Policies / VPC** タブが見えれば OK です。

## ant CLI の使い方

CMA の操作は **`ant` CLI 1 本** でほぼ完結します。

#### インストール + 認証

```
brew install anthropics/tap/ant

ant auth login           # ブラウザ OAuth
ant auth status          # 認証状態
ant profile activate dev # プロファイル切替
```

#### コマンド体系

リソース ✕ 6 を覚えるのがコツです:

```
agent              → ant beta:agents       create / retrieve / update / list / archive
environment        → ant beta:environments create / retrieve / update / list / delete / archive
session            → ant beta:sessions     create / retrieve / update / list / delete / archive
session events     → ant beta:sessions:events  list / send / stream
```

#### 1 発質問して結果を見るパターン

```
export ANTHROPIC_API_KEY=sk-ant-...
AGENT=agent_xxx
ENV=env_xxx

# (1) セッション作成
SID=$(ant beta:sessions create \
  --agent "$AGENT" --environment-id "$ENV" \
  --title "manual test" 2>&1 \
  | grep -oE 'sesn_[A-Za-z0-9]+' | head -1)
echo "$SID"

# (2) メッセージ送信
ant beta:sessions:events send --session-id "$SID" \
  --event '{"type":"user.message","content":[{"type":"text","text":"hello, what tools do you have?"}]}'

# (3) 結果を取得
sleep 30
ant beta:sessions:events list --session-id "$SID"
```

#### リアルタイム監視 (stream)

別タブで stream を張りっぱなしにしておくと、エージェントの思考・ツール呼び出しが流れてきます:

```
# Tab 1: 流し見
ant beta:sessions:events stream --session-id "$SID"

# Tab 2: 送信
ant beta:sessions:events send --session-id "$SID" \
  --event '{"type":"user.message","content":[{"type":"text","text":"..."}]}'
```

最終回答だけ抽出する場合:

```
ant beta:sessions:events stream --session-id "$SID" --format json | \
  jq -r 'select(.type == "agent.text_delta") | .delta.text' | \
  tr -d '\n'
```

![](https://static.zenn.studio/user-upload/4a35406c1049-20260601.png)  
![](https://static.zenn.studio/user-upload/c41bd52e5cf8-20260601.png)

#### Egress Policy で内部ホスト名をルーティング

`gcp-nginx.internal` のような **架空のホスト名** を、Cloudflare Tunnel 経由で本物の GCP VM に解決させます:

```
{
  "name": "vpc-routing",
  "rules": [
    {
      "match": { "host": "gcp-nginx.internal" },
      "action": "proxy",
      "via": "tunnel:gcp-demo"
    }
  ]
}
```

```
ant beta:sessions:events send --session-id "$SID" \
  --event '{"type":"user.message","content":[{"type":"text",
    "text":"gcp-nginx.internal/api/users.json から Engineering 部門だけ抽出して"
  }]}'
```

Agent はサンドボックス内で:

1. `bash` で `curl http://gcp-nginx.internal/api/users.json`
2. Worker の egress policy が `tunnel:gcp-demo` を選択
3. Tunnel 経由で GCP VM の nginx に到達
4. 結果を `jq` でフィルタして応答

という流れで動きます。**agent 側には GCP の認証情報も IP も一切渡らない** のがポイント。  
![](https://static.zenn.studio/user-upload/84e7fbefc9ec-20260601.png)

### Browser Run でヘッドレス操作 + 録画

「**agent にブラウザを使わせ、その操作を全部録画して監査ログ化する**」シナリオ。Browser Rendering と rrweb 録画が標準装備なので、特別な仕込みは不要です。

#### Agent に依頼

```
ant beta:sessions:events send --session-id "$SID" \
  --event '{"type":"user.message","content":[{"type":"text",
    "text":"https://www.anthropic.com/news を開いて最新 3 件のタイトルと URL を抜き出して、操作は録画しておいて"
  }]}'
```

Agent は `browser_execute` ツールを呼んでヘッドレス Chrome (CDP 経由) を操作します:

```
agent.tool_use: browser_execute
  input: {
    "actions": [
      { "type": "navigate", "url": "https://www.anthropic.com/news" },
      { "type": "wait_for_selector", "selector": "article" },
      { "type": "extract", "selector": "article h2 a" }
    ],
    "record": true
  }
```

#### 録画を取り出す

セッション完了後、ダッシュボードの **Sessions → 該当 session → Browser Recordings** タブから rrweb 録画を再生できます。コマンドからは:

```
# 録画 ID 一覧
ant beta:sessions:resources list --session-id "$SID" \
  --transform 'data.#(type="browser_recording").#.id'
 
# rrweb 形式の JSON をダウンロード
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://<your-worker>.workers.dev/api/recordings/rec_xxx \
  -o session-recording.json
```

ダウンロードした JSON は [rrweb-player](https://github.com/rrweb-io/rrweb-player) で再生可能:

```
<script src="https://cdn.jsdelivr.net/npm/rrweb-player@latest/dist/index.js"></script>
<script>
  fetch('session-recording.json').then(r => r.json()).then(events => {
    new rrwebPlayer({ target: document.body, props: { events } });
  });
</script>
```

![](https://static.zenn.studio/user-upload/004493a6f9d3-20260601.png)

#### 監査や障害分析に利用

* agent の **画面操作を秒単位で再現** できる → 監査・障害分析に直結
* ユーザの個人情報が映る画面でも、録画は Cloudflare アカウント内に閉じる
* 標準保持 30 日。R2 に Logpush で永続化も可能

エージェント作成 UI には **6 つのカテゴリのチェックボックス** が並びます。何にチェックを入れるかでサンドボックスの能力が決まります。

Anthropic の `agent_toolset_20260401` 経由でコンテナ内 SDK が直接処理するツール。**MicroVM backend 専用**。

| 名前 | 説明 |
| --- | --- |
| `bash` | シェルコマンドを実行 |
| `edit` | ファイル内の文字列置換 |
| `read` | テキスト / 画像 / PDF / Notebook を読む |
| `write` | ファイル書き出し |
| `glob` | パターンでファイル検索 |
| `grep` | ファイル内容の正規表現検索 |

#### 2. Server-side ツール (Anthropic 側実行)

**Anthropic 側のインフラで実行され、Cloudflare の Egress Policy を完全にバイパス** します。監査要件がある場合は基本オフ推奨。

| 名前 | 説明 |
| --- | --- |
| `web_fetch` | URL をフェッチ (Anthropic 側で実行)。可能なら `cf_web_fetch` を使う |
| `web_search` | Web 検索 (Anthropic 側で実行)。Cloudflare 側に同等品なし |

各バインディングを Worker 側で持っていると有効化できる Cloudflare ネイティブのツール群。

| 名前 | 必要 | 説明 |
| --- | --- | --- |
| `cf_web_fetch` | Browser Rendering | URL をフェッチ。**egress policy を通る** ので監査可能 |
| `fetch_to_markdown` | Browser Rendering | URL を Markdown 化してフェッチ |
| `browse` | Browser Rendering | ヘッドレスブラウザでページを開いて操作 |
| `screenshot` | Browser Rendering | スクリーンショット取得 |
| `image_generate` | Workers AI | Flux 等で画像生成 |
| `call_service` | Workers VPC | VPC binding 経由で社内サービスを呼ぶ (`gcp-nginx.internal` 等) |
| `email_send` | Email Routing | メール送信 |
| `email_inbox` | Email Routing | 受信箱一覧 |
| `email_read` | Email Routing | メール本文取得 |

## メリット・制限・MCP との違い

ここからが本題。「**なぜ Cloudflare で動かすのか**」「他の選択肢と何が違うのか」を整理します。

### Anthropic Managed と比べたメリット

#### 1. プライベートサービスに繋ぎたい時

Anthropic の managed sandbox は完全にパブリックインターネット側にあるので、社内 API に到達するには NAT / 踏み台 / 専用プロキシを別途立てる必要があります。

CMA + Cloudflare では:

* **Workers VPC binding** で GCP / AWS の private network に直接到達
* **Cloudflare Mesh / Tunnel** 経由で社内ホストへ
* **ホスト名 → VPC binding ルーティング** を egress policy で 1 行記述

これだけで「`gcp-nginx.internal/api/users` を agent が読む」が成立します。  
![](https://static.zenn.studio/user-upload/951f33f33b21-20260601.png)  
![](https://static.zenn.studio/user-upload/113c58eeb249-20260601.png)  
![](https://static.zenn.studio/user-upload/b58a89c23928-20260601.png)

#### 2. 認証情報をエージェントに見せたくない時

Stripe API キーや顧客 DB の認証情報を **agent に渡さずに API を叩かせたい** ケース。

CMA の **Header Injection policy** を使えば、Worker 側で `Authorization: Bearer $STRIPE_KEY` を自動付与でき、agent のコンテキストには平文の鍵が **一切現れません**。  
![](https://static.zenn.studio/user-upload/c15d97313362-20260601.png)

#### 3. 監査ログを自社に閉じ込めたい時

Anthropic 任せだと外部通信のログは Anthropic 側にあります。CMA + Cloudflare では:

* **全 egress を Worker 経由** にできる → Logpush で R2 / Datadog / Splunk へ
* **Custom Proxy** で全 request body をフックして監査
* Browser Run の **rrweb 録画** で全画面操作を残せる

金融・医療・公共コンプライアンス要件にハマりそうです。

#### 4. コストが劇的に下がる条件

| ワークロード | 結論 |
| --- | --- |
| 大量並列 (千〜万 session) | **Cloudflareが有利** (Isolate ms 起動・hibernation native) |
| 長時間アイドル対話 | **Cloudflareが有利** (hibernate-on-idle で CPU 課金抑制) |
| 大量データ取得・解析 | **Cloudflareが有利** (Cloudflare は egress 無料) |
| 私設 API / VPC アクセス | **Cloudflareが有利** (NAT 不要) |
| ブラウザ多用 | **Cloudflareが有利** (Browser Run が安い) |
| 月数 session の少量利用 | Anthropic Managed 寄り (Workers Paid $5/mo の固定費が割高) |

参考価格 (Cloudflare 側):

* Containers ≈ $0.000056/sec (= 3 分使って $0.01)
* Isolate (Worker Loader) = 通常 Workers と同じ単価 (1M req / $0.30)
* Browser Run ≈ $0.09 / 1000 sessions
* R2 / D1 / KV は標準料金、**egress は完全無料**

並列数千を Isolate で回しても日額数ドル、というレンジに収まります。

#### 5. Backend を選べる

ユースケースに応じて MicroVM と Isolate を **同じ control plane** に混在させられます。

```
開発者支援エージェント   → MicroVM (npm install したい)
カスタマーサポート       → Isolate (数千並列)
データ分析エージェント   → 両方混在 (重い処理 = VM、軽い変換 = Isolate)
```

### MCP Server との違い

「自前ツールを Claude に持たせる」点で MCP との比較がよく出ます:

|  | MCP Server | CMA on Cloudflare |
| --- | --- | --- |
| 主な目的 | **ツール提供** | **エージェント実行環境** |
| 状態管理 | 基本ステートレス | セッション + ワークスペース永続化 |
| 並列処理 | クライアント側で制御 | サーバー側で自動 |
| サンドボックス | 自前 | MicroVM / Isolate が標準 |
| Cloudflare バインディング | 制約あり | R2 / D1 / KV / VPC が全部使える |

MCP は「Claude Desktop / Code に **道具** を生やす」、CMA は「Claude のために **専用ワークスペース** を Cloudflare 上に立てる」と考えると整理しやすいです。

### 注意点 / 制限事項 (2026-06 時点)

| カテゴリ | 制限 |
| --- | --- |
| **プラン要件** | Workers Paid 必須 |
| **Backend 差** | Isolate にシェル無し / Isolate のツールは control plane が登録した分のみ |
| **セキュリティ / 監査** | Server-side (`web_fetch` / `web_search`) は egress policy を **BYPASS** / Browser Run 録画は 保持 30 日 |
| **運用上の注意** | claude.ai UI からは利用不可 (Console / CLI / SDK のみ) / R2 snapshot 未設定だと `/workspace` が再起動で揮発する |

特に **Server-side tools (`web_fetch` / `web_search`) は Anthropic 側で実行され、ログも残らず egress policy も効きません**。基本 OFF にしておくのが安全です。

## まとめ

* **CMA Anthropic がモデル、Cloudflare がインフラ。**
* 自前 control plane を Cloudflare に立てると、**VPC アクセス / egress 制御 / 監査ログ / コスト最適化 / backend 選択** を全部自社で握れる。
* 操作は `ant` CLI 一本でほぼ完結。**`beta:sessions` と `beta:sessions:events`** の 4 〜 5 コマンドを覚えれば日常タスクは回る。
* 大量並列・長時間・私設網アクセスがあるワークロードでは **コスト的にも機能的にも自己管理が圧倒的に有利**。
* 一方、月数セッションの軽量ユースは Anthropic Managed のほうが手早い。**ワークロードに応じて選ぶ** のが正解。

「Claude を自社のクラウド境界内に閉じ込めつつ、production grade で動かしたい」  
そんな要件があれば、CMA on Cloudflare はかなり強力な選択肢になります、ぜひご活用を。

---

#### 参考リンク
