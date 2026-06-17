---
id: "2026-06-16-解決claude-code-の-routineクラウド定期実行でカスタムmcpコネクタが動かない問題-01"
title: "【解決】Claude Code の routine（クラウド定期実行）でカスタムMCPコネクタが動かない問題"
url: "https://zenn.dev/sawai/articles/5a4c109e70f04b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "zenn"]
date_published: "2026-06-16"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* **症状**: claude.ai / Claude Code の **routine（クラウドのスケジュール実行）** で、自分で追加したカスタム MCP コネクタのツールが**実行セッションに注入されない**。エージェントは「ツールが1つも無い」状態で起動し、`No matching deferred tools found` になる。
* **原因**: コネクタ注入側の既知バグ（[anthropics/claude-code#43397](https://github.com/anthropics/claude-code/issues/43397) ほか）。さらに claude.ai のカスタムコネクタは **OAuth（ユーザー同意必須）専用**で、無人実行にはそもそも同意コンテキストが無い。
* **効かない対処**: OAuth 再接続 / `client_credentials` / URL埋め込みトークン / Bearer ヘッダ指定。
* **効いた解**: routine の **cloud environment の Setup script** で、壊れているアカウント連携コネクタを使わず、**静的トークンで MCP サーバーを自前登録**する。これで注入バグを迂回でき、**クラウド実行・PCオフ・routine の UI** を全部保ったまま動く。

---

## 背景

毎朝 GSC を分析して改善提案を Notion/GitHub に書き出す、という日次 SEO ルーティンを Claude Code の routine で回そうとしていた。外部 SaaS へのアクセスは自前の MCP サーバー（OAuth/PAT でクレデンシャルを隠蔽するゲートウェイ）経由。

ローカルの対話セッションでは完璧に動く。ところが **クラウドの routine に載せた瞬間に動かなくなった。**

## 症状

routine の実行ログを見ると、事前チェックで必ずこう出る:

```
必須ツール（grantry / google_gsc_* / github_*）が未検出。
接続済み: WebFetch, WebSearch, ファイル系のみ。
```

`tools/list` 相当を叩いても、自分の MCP サーバーのツールが**1つも出てこない**。一方、対話セッションでは同じコネクタが普通に使える。

つまり「設定」ではなく「**routine 実行環境にツールが注入されていない**」のが症状。

## 効かなかった対処（時短のため全部書く）

ここで数時間溶かしたので、同じ轍を踏まないように列挙する。

### ❌ コネクタの OAuth を再接続する

「トークン期限切れだろう」と Disconnect → 再接続を何度かやったが無意味。OAuth の access token(1h)/refresh token(60d) の話ではなく、**そもそも routine 実行環境がそのトークンストアに到達できていない**。

### ❌ `client_credentials`（M2M）に対応する

「無人実行なら OAuth の machine-to-machine grant が正道では」と考えたが、**claude.ai 側が `client_credentials` 非対応**。カスタムコネクタの接続は\*\*すべてユーザー同意ゲート（authorization\_code）\*\*を通る仕様。自前の認可サーバーに `client_credentials` を実装しても、claude.ai がそれを叩きに来ないので徒労。  
（参考: [Authentication for connectors — Claude Docs](https://claude.com/docs/connectors/building/authentication)）

### ❌ URL にトークンを埋め込む（旧 Zapier 方式）

「URL 自己認証で OAuth チャレンジを返さなければ繋がるのでは」というアイデア。実際 Zapier はかつてこれだったが、**Zapier 自身が OAuth に移行して廃止済み**。業界の流れにも逆行するので採用見送り。

### ❌ コネクタUIに Bearer ヘッダを指定する

claude.ai の「Add custom connector」ダイアログは **URL と OAuth Client ID/Secret しか入力欄が無い**。静的 Bearer ヘッダを差す場所が無い（既知の要望: [claude-ai-mcp#112](https://github.com/anthropics/claude-ai-mcp/issues/112)）。

## 根本原因

これは**Claude 側のバグ**で、自分の MCP サーバーをどう直しても解決しない。複数の issue が立っている:

ポイント:

1. **routine はクラウドで実行される**（PC オフでも走る）。これは仕様通り。壊れているのは「**アカウント連携した MCP コネクタのツール注入**」だけ。
2. **特定コネクタの問題ではない**。Slack / Notion / Gmail など**全コネクタで再現**報告がある。
3. #35899 いわく「**人間がメッセージを1通送ってセッションを warm すると注入される**」。＝初期化バグ。だが無人実行ではその warm を起こせない。指示書（プロンプト）でも回避不能（プロンプトが読まれる時点で、ツールが既に存在しないため）。

## 効いた解: Setup script で静的トークン MCP を自前登録する

Claude Code の routine には **cloud environment**（Anthropic 管理のサンドボックス、自前 VM 不要）を割り当てられる。その設定に **Setup script（Claude Code 起動前に走る Bash）** がある。![](https://static.zenn.studio/user-upload/e04c8fb65584-20260616.png)

ここで、**壊れているアカウント連携コネクタを使わず**、静的トークンで MCP サーバーを**その場で登録**してしまう。自前登録の MCP は、アカウント連携コネクタの注入バグの**対象外**なので、ちゃんとセッションに乗る。

### cloud environment の設定

| 項目 | 値 |
| --- | --- |
| Network access | **FULL**（MCP サーバーへの外向き通信を通すため。Trusted だと弾かれることがある） |
| Environment variables | **空**（"visible to anyone" なのでトークンを入れない） |
| Setup script | ↓ |

### Setup script

```
#!/bin/bash
set -e

# アカウント連携コネクタ（OAuth）は routine 実行に注入されないので使わない。
# 静的トークンで MCP サーバーを user スコープに自前登録する。
claude mcp add --scope user --transport http my-mcp \
  https://your-mcp.example.com/mcp \
  --header "Authorization: Bearer <STATIC_TOKEN>"

# 登録できたかをセットアップログで確認できるように
claude mcp list || true
```

> ⚠️ **トークンの扱い**: Environment variables は「環境利用者に可視」と明記されているので入れない。Setup script にインラインで書く場合も露出範囲を理解した上で、**短命トークン＋定期 rotate** で運用する。理想は CI 並みのシークレット管理だが、現状この環境にそれは無いので割り切り＋ rotate。

### 指示書（routine のプロンプト）側

* 自前登録した名前空間（例 `mcp__my-mcp__*`）のツールを使うよう明記
* 静的トークンが scope 引数を要求するゲートウェイなら、各ツール呼び出しで scope を渡すよう指示
* 事前ガードで「ツールが見えなければ理由を明記して停止」を入れておくと、注入失敗時に黙って空振りせず原因が分かる

## 結果

scheduled run（手動でなく**スケジュール起動**）のログで、自前 MCP のツールが実際に呼ばれ、GSC 取得 → 分析 → リポジトリへのログ push まで**完走**した。

これで要件を全部満たせた:

* ✅ クラウド実行（**PC オフでも走る**）
* ✅ routine の UI（Runs パネル）をそのまま使える
* ✅ MCP 認証が通る（静的トークン）
* ✅ **自前 VM 不要**（Anthropic のクラウド環境）

## 補足: 代替案

* **常時起動ホスト + cron + `claude -p`**: VPS / 常時起動 Mac / Raspberry Pi で headless 実行。確実だが VM 管理と UI を自前で用意する必要がある。
* **Claude Messages API の MCP connector**: API なら `mcp_servers` に URL + `authorization_token` を直接渡せる（UI と違い Bearer が通る）。任意のクラウド cron（GitHub Actions / Railway cron 等）から叩けば、routine 機能を使わずに同じことができる。observability は自前。

## まとめ

* routine でカスタム MCP が動かないのは**あなたの設定ミスではなく Claude 側の既知バグ**。
* OAuth をいくらいじっても直らない。**cloud environment の Setup script で静的トークン MCP を自前登録**して迂回するのが、現時点で最も筋の良い解。
* 本来は注入バグが直れば設定そのままで動くはずなので、上記 issue を購読しておくとよい。

同じところでハマっている人の時間が少しでも減れば幸い。
