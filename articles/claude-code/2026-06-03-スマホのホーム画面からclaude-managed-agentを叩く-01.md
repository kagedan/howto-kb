---
id: "2026-06-03-スマホのホーム画面からclaude-managed-agentを叩く-01"
title: "スマホのホーム画面からClaude Managed Agentを叩く"
url: "https://zenn.dev/acntechjp/articles/290e28f9574912"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/e2f616b955a8-20260602.png)  
*スマホでスケジュール管理秘書*

## はじめに：ゲートウェイの必要性

突然ゲートウェイという単語を使ってしまいすみません。背景を書きます。

もともと、登壇・イベントのスケジュールを管理するAgent Skillsを作っていてClaude Codeで運用していました。内容としては、5つのスキル、データモデル（Neon/PostgreSQL）を持つ、いわば「予定管理の秘書」です。使っていく中でふと思ったのが、スマホからもこのAgent Skillsを活用したいなということでした。スケジュールの確認や予定の追加を担うAI Agentをスマホからお願いできると素敵だなと。様々な選択肢がありますが、Claudeの**Managed Agent**を作りながら学べる機会だなと思いました。ので、Managed Agentsとして構築しています。

ただ、秘書をManaged Agentに常駐させても、肝心の **使う窓口** がないとスマホからは使えません。やりたいのはシンプルで、

> 通勤中にスマホで「6/14 14:00 苫小牧高専でオンライン登壇を追加して」と話しかけたら、予定が登録されている

という体験です。

ここで問題になるのが **秘密情報の置き場所** です。`ANTHROPIC_API_KEY` やDBの接続文字列をスマホに置くわけにはいきません。かといって、画面から直接Managed AgentsをAPI呼び出しすると鍵が露出してしまいます。

そこで、スマホとAIエージェントの間に **薄い中継サーバ（ゲートウェイ）** を1枚挟みました。本記事では、この仕組みを題材に、

* **Android（PWA） → Gateway（Vercel） → AI Agent（Anthropic）** の3層疎結合アーキテクチャ
* Managed Agentsを「呼ぶだけ」に徹する薄い中継の実装
* **env/secretを注入する仕組みが無い** という制約に、どう向き合ったか（記事の山場）
* 長時間ツール実行を **SSEストリーミング** で逐次返す設計

を、実際に踏んだ罠と設計判断の理由まで含めて解説します。

この記事で紹介するソースコードは全てGitHubに公開しています。ぜひご覧ください。  
[GitHub PWAとゲートウェイ](https://github.com/Masa1984a/schedule-gateway)  
[GitHub スケジュール管理Skills](https://github.com/Masa1984a/my-event-schedule-management)

### この記事で得られること

* Claude Managed Agents（Agent / Environment / Session / Events）の実ユースケース理解
* 「窓口・中継・頭脳」を独立進化させる3層疎結合の設計思想
* Managed Agentsへのシークレット注入問題と、その回避策（bootstrap）・トレードオフ
* 長時間実行を支えるSSEストリーミングの実装パターン（stream-first / idle-gate）
* PWAをホーム画面アプリ化する最小構成

### 前提知識

* Next.js（App Router）の基礎
* TypeScript / Node.jsの基礎
* 「AIエージェント」の概念（LLMが自律的にツールを選択・実行すること）

---

## 1. 全体アーキテクチャ：3層を疎結合にする

### 1-1. 全体像

全体像は下記となります。  
![](https://static.zenn.studio/user-upload/4804d3667c85-20260603.png)

より詳細に見ていきましょう。まずは登場人物を見ていきます。

スマホからの発話が、どこを通って行くのかイメージできたらと。

```
[Androidスマホ]
   │  HTTPS（自分専用トークン GATEWAY_TOKEN（自前で生成） で認証）
   ▼
[schedule-gateway @ Vercel Pro] 
   ├─ PWA（チャットUI）
   └─ API（ゲートウェイ）
        │  x-api-key = ANTHROPIC_API_KEY（Vercel env に保持）
        │  beta: managed-agents-2026-04-01
        ▼
[Claude Managed Agents API @ Anthropic]    ← 呼ぶだけ
   └─ Session（agent + 5スキル）→ サンドボックス（bash/file/code）
        │  skills → scripts/neon_client.sh（Neon HTTP /sql）
        ▼
[Neon インスタンス A（スケジュール管理）]  speaking_events / travel_routes

[Gateway] ──直接SQL──> [Neon インスタンス B（セッション管理）] gateway_sessions
```

ポイントは、**頭脳（Managed Agent）はすでに別リポで構築済み** で、このプロジェクトはそれを **IDで参照して「呼ぶだけ」** だということです。モデルもプロンプトもスキルも、ゲートウェイは一切持ちません。

### 1-2. 責任分解（4ゾーン）

各レイヤーの責務と「どの秘密を持つか」を表にすると、設計の意図が一目で分かります。

| ゾーン | コンポーネント | 責任 | 保持する秘密 |
| --- | --- | --- | --- |
| クライアント | Android PWA | 窓口/表示のみ | `GATEWAY_TOKEN`（localStorage） |
| ゲートウェイ@Vercel | API + lib | 認証・セッション仲介・SSE中継 | **全秘密**（Vercel env） |
| Managed Agent@Anthropic | Agent/Env/Session/Skills | 頭脳の定義 + ツール実行サンドボックス | （実行時に `~/.neonrc`） |
| データ層@Neon | スケジュール管理DB(A) / セッション管理DB(B) | ドメインデータ / セッション管理 | — |

### 1-3. なぜ疎結合にするのか？

各ゾーンは **契約（HTTP / SSE / Events API / 接続文字列）だけ** で結ばれ、お互いの内部実装を知りません。この分離が効いてくる場面は具体的です。

* **フロントを差し替えても** Gatewayは不変。LINE BotやAndroidの自動化アプリ（Tasker等）を窓口に追加しても、同じ `/api/chat` を叩くだけ。
* **Agentのプロンプト/スキルを更新しても** GatewayはID参照のまま不変。頭脳の進化が窓口に波及しない。
* **Gatewayを別言語/別基盤に置き換えても** Agent・DBは不変。

「窓口」「中継」「頭脳」をそれぞれ独立して進化させられる ― これが3層疎結合の狙いです。

---

## 2. 技術スタック

| 区分 | 採用 | バージョン |
| --- | --- | --- |
| フレームワーク | Next.js（App Router） | 16.2.6 |
| 言語 | TypeScript | 5.7 系 |
| UI | React | 19.2.6 |
| Managed Agents SDK | `@anthropic-ai/sdk` | 0.100.1 |
| DB クライアント | `@neondatabase/serverless` | 1.1.0 |
| ランタイム | Node.js（Vercel） | 20+ |
| ホスティング | Vercel Pro | — |
| DB | Neon (PostgreSQL) ×2 | — |

実装上、最初に押さえておくべき点が2つあります。

* Managed Agentsのbetaヘッダ `managed-agents-2026-04-01` は **SDKが自動付与** します（明示不要）。
* APIルートはNodeランタイムで動かし（`export const runtime = "nodejs"`）、ツール実行の待ち時間を確保するため `export const maxDuration = 300` を指定します。

### リポジトリ構成

PWA・API・libが1つのNext.jsプロジェクトに同居する、シンプルな構成です。

```
schedule-gateway/
├─ app/
│  ├─ layout.tsx                # メタ/viewport/PWA メタ
│  ├─ page.tsx                  # チャットUI（"use client"）: トークン保存 + SSE逐次表示 + SW登録
│  ├─ manifest.ts               # /manifest.webmanifest を生成
│  └─ api/
│     ├─ chat/route.ts          # メイン: 認証→セッション→stream-first→SSE中継
│     └─ health/route.ts        # 死活確認
├─ lib/
│  ├─ auth.ts                   # Bearer 検証（timingSafeEqual / fail-closed）
│  ├─ anthropic.ts              # Managed Agents クライアント + bootstrap
│  └─ session.ts                # gateway_sessions に user_key↔session_id を保存・再利用
├─ public/
│  └─ sw.js                     # 最小 Service Worker（API は素通し / network-first）
└─ scripts/
   └─ reset-session.mjs         # セッション管理の user_key 行を削除し新規 bootstrap をやり直す保守用
```

---

## 3. ゲートウェイ詳細設計

ここからゲートウェイ本体の実装に入ります。役割は **認証・セッション仲介・SSE中継** の3つだけ。徹底して「薄い中継」に徹します。

### 3-1. 認証 ― fail-closed なBearer検証

すべてのAPIは `Authorization: Bearer <GATEWAY_TOKEN>` を必須にします。ここで地味に大事なのが2点です。

1. **タイミングセーフな比較**：トークンの一致判定に `timingSafeEqual` を使い、文字列比較の所要時間からトークンを推測される攻撃を防ぐ。
2. **fail-closed**：`GATEWAY_TOKEN` が未設定なら **常に拒否** する。設定漏れが「誰でも通る」状態にならないようにする。

```
import { timingSafeEqual } from "node:crypto";

export function isAuthorized(req: Request): boolean {
  const expected = process.env.GATEWAY_TOKEN;
  if (!expected) return false;                       // fail-closed
  const header = req.headers.get("authorization") ?? "";
  if (!header.startsWith("Bearer ")) return false;
  const token = header.slice(7).trim();
  const a = Buffer.from(token), b = Buffer.from(expected);
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}
```

不一致・欠落はすべて401を返します。

### 3-2. Managed Agentsクライアント ― 「ID参照」で呼ぶだけ

`lib/anthropic.ts` がManaged Agents APIとの窓口です。責務は、セッション作成 / ステータス取得 / メッセージ送信 / ストリーム購読 / bootstrap。

注目してほしいのは `createSession()` です。モデルもプロンプトもツールも **渡しません**。既存のAgentとEnvironmentを **ID参照** で新規セッション化するだけです。

```
// 既存 Agent / Environment を ID で参照してセッションを起こす
client.beta.sessions.create({
  agent: AGENT_ID,
  environment_id: ENVIRONMENT_ID,
  title: "schedule-gateway session",
});
```

頭脳の定義（モデル・プロンプト・スキル）はすべてAnthropic側に固定されているので、ゲートウェイは「どのAgentを使うか」をIDで指すだけ。これが疎結合の実装上の核心です。

主なメソッドは以下の通りです。

| メソッド | 役割 |
| --- | --- |
| `createSession()` | Agent + Environment をID参照で新規セッション化 |
| `sendMessage(sessionId, text)` | `events.send` で `user.message` を1件送信 |
| `getSessionStatus(sessionId)` | `sessions.retrieve` の `status` を取得 |
| `streamSession(sessionId)` | `events.stream()` を `AsyncIterable` で返す薄いラッパ |
| `bootstrapSession(sessionId)` | セッション開始直後にDB接続情報を注入（§5で詳述） |

### 3-3. セッション管理 ― 文脈を継続させる仕組み

Managed Agentsのサンドボックスはセッション毎に独立し、揮発します。つまり毎回新しいセッションを作ると、**会話の文脈が引き継がれず、毎回DB接続情報の再注入（bootstrap）のレイテンシも乗ります**。

そこで、`user_key`（個人運用なら `'me'` 固定）と `session_id` を紐づける小さなセッション管理テーブルをNeon上に置き、生きているセッションを再利用します。

```
CREATE TABLE IF NOT EXISTS gateway_sessions (
  user_key     text PRIMARY KEY,
  session_id   text NOT NULL,
  created_at   timestamptz NOT NULL DEFAULT now(),
  last_used_at timestamptz NOT NULL DEFAULT now()
);
```

セッション取得のアルゴリズムはこうです。

```
getOrCreateSession(userKey):
1. ensureTable()                          # 初回のみ CREATE TABLE IF NOT EXISTS
2. gateway_sessions を user_key で検索
3. 既存あり:
     sessions.retrieve(session_id) で status 確認
       status ∈ {running, idle} → 再利用し last_used_at を更新して返す
       それ以外（terminated / 取得失敗）→ 4 へ
4. 新規作成:
     sessionId = createSession()
     bootstrapSession(sessionId)          # ~/.neonrc 注入 + idle まで読み捨て
     gateway_sessions に UPSERT
     返す
```

`running` と `idle` は再利用、`terminated` は作り直し。再利用できると **同一 `session_id` を使い回すので文脈が継続** し、bootstrapも省けるため応答が一気に速くなります（実測で初回76秒 → 2回目以降5秒。詳細は§7）。

### 3-4. メインAPI ― 認証からSSE中継まで

`app/api/chat/route.ts` が処理の本体です。冒頭でランタイムと最大実行時間を宣言します。

```
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;   // ツール実行で数十秒かかるため
```

リクエストは `{ "message": string }` のみ。既定は **SSEストリーム** で逐次返し、`?mode=sync` を付けるとidleまで待って最終テキストをJSONで返す同期モードになります（後者はTasker等の自動化から叩くときに便利）。

処理順を擬似コードで示します。

```
1. isAuthorized() → 401 なら即返す
2. body.message を取得・検証（空は 400、不正 JSON も 400）
3. getOrCreateSession('me') → sessionId
4. stream の場合:
     send("session", {session_id})
     events = await streamSession(sessionId)   ← stream-first（先にストリームを開く）
     await sendMessage(sessionId, message)      ← その後で発話を送る
     for await (ev of events):
       agent.message  → text ブロックごとに send("message", {text})
       agent.tool_use → send("tool", {name})
       session.status_idle:
         stop_reason.type === "requires_action" → continue（まだ続く）
         else → send("done", {reason}); close
       session.status_terminated → send("done", {reason:"terminated"}); close
     catch → send("error", {message}); close
```

Gatewayがクライアントへ流すSSEの「契約」は次の通りです。Agentの内部イベントを、クライアントが扱いやすい最小限のイベントに翻訳しています。

| Agent イベント | クライアントへのSSE |
| --- | --- |
| セッション確定 | `event: session` `{session_id}` |
| `agent.message`(text) | `event: message` `{text}` |
| `agent.tool_use` | `event: tool` `{name}` |
| `session.status_idle`(end\_turn 等) | `event: done` `{reason}` |
| `session.status_terminated` | `event: done` `{reason:"terminated"}` |
| 例外 | `event: error` `{message}` |

---

## 4. ストリーミング設計の3つの勘所

ここはManaged Agentsを実際に中継してみて初めて分かった、ハマりやすいポイントです。

### 4-1. stream-first：ストリームを先に開く

直感的には「メッセージを送ってから応答ストリームを開く」と書きたくなりますが、それだと **初期イベントを取りこぼします**。正解は逆順で、

```
const events = await streamSession(sessionId);   // ① 先にストリームを開く
await sendMessage(sessionId, message);           // ② その後で発話を送る
for await (const ev of events) { /* ... */ }
```

「受け口を開けてから喋りかける」と覚えると間違えません。

### 4-2. idle-gate：`idle` 単独で終了しない

`session.status_idle` が来たら会話終了、とつい判定したくなりますが、これは罠です。Agentがツール実行を挟むと、その合間にも `idle` が現れます。終了判定は `stop_reason.type` を見て行います。

* `requires_action` → まだ続く。**continue**
* `end_turn` / `retries_exhausted` → 終了
* `session.status_terminated` → 終了

### 4-3. `agent.message` はトークンdeltaではなく完結テキストブロック

OpenAIのストリーミングに慣れていると「1トークンずつ来る」と思いがちですが、Managed Agentsの `agent.message` は **完結したテキストブロック単位** で届きます。なので中継側は「delta を連結」ではなく「イベント毎に追記表示」でOKです。

加えて、ツール実行は数十秒かかることがあるため、関数のウォール時間として `maxDuration=300`（Vercel Pro）を確保しておくのが重要でした。

---

## 5. 記事の山場：シークレット注入問題と回避策

ここが今回いちばん悩んだ、そして共有する価値があると思った設計判断です。

### 5-1. 課題：Managed Agentsにenv/secretを渡すフィールドが無い

スキルはDBにアクセスするため `DATABASE_URL`（Neonの接続文字列）を必要とします。ところが現状、**Agent定義にもEnvironment定義にも、任意の環境変数・シークレットをサンドボックスへ渡すフィールドが存在しません**。

* Agentの受付フィールド：`name / model / system / tools / mcp_servers / skills / multiagent / description / metadata`
* Environment(cloud) config：`type / packages / networking`
* `vault_ids` は **MCPのOAuth/bearer専用** で、bash用の汎用env varではなく、コンテナのシェルには露出しない

つまり「スキルが必要とする接続文字列を、正規の経路でサンドボックスへ渡す方法が無い」。これが出発点でした。

### 5-2. 採用した回避策：bootstrap

そこで採ったのが **bootstrap** です。新規セッション作成の直後、Gatewayが「最初の `user.message`」として、Agentにbashを実行させ `~/.neonrc` に接続文字列を書かせる、という方式です。

```
umask 077 \
  && printf "export DATABASE_URL='%s'\n" '<DATABASE_URLの実値>' > "$HOME/.neonrc" \
  && echo "neonrc written"
```

各スキルの `SKILL.md` 冒頭では、この `~/.neonrc` を読み込んでからDBクライアントを使います。

```
set -a && . "$HOME/.neonrc" && set +a   # bootstrap で書かれた DATABASE_URL を読込
source scripts/neon_client.sh
```

#### 実際に踏んだ罠

ここはコピペで動かないポイントが詰まっていました。

* **`$HOME` はサンドボックス側（Linux, `$HOME=/root`）で展開させる**。ローカルで展開してしまわないよう注意。
* **接続文字列の `&` は必ずシングルクオートで括る**。Neonの接続文字列は `...&sslmode=require` のように `&` を含みます。クオートしないと `source` 時にbashが `&` をバックグラウンド演算子と解釈し、**URLが途中で切れます**。
* Gatewayはbootstrapの応答ターン（`neonrc written`）を **`session.status_idle` まで読み捨て**、以降のユーザー発話のストリームをクリーンに保つ。
* サンドボックスはセッション毎に揮発するので、`~/.neonrc` は **新規セッションごとに再注入** が必要。

### 5-3. トレードオフ：明記すべきリスク

回避策である以上、リスクは正直に記録しておきます。

* `DATABASE_URL` が **セッションのイベントログ（Anthropicサーバ側に保存）に平文で残る**。`events.list()` やcompaction summaryからも読める。
* 露出する軸は「**`ANTHROPIC_API_KEY` にアクセスできる人**」。正面玄関の `GATEWAY_TOKEN` はこの軸には効かない（後述§6）。
* **個人用途では許容範囲。共有/本番では非推奨。**

### 5-4. 本番向けの「あるべき姿」

理想に近い順に、本番でやるべき追加設計を挙げておきます。

1. **DBアクセスのMCP化 + Vault（最有力）**：`neon_client.sh` の各操作をMCPツール化し、接続情報はVaultに集約してAgentの `mcp_servers` から参照する。サンドボックスは接続文字列を一切見ず、bashでのSQL組立も不要になり堅牢。**「Agent側に秘密を置く」の正しい実装形** です。
2. **カスタムツールでホスト側実行**：custom toolを宣言し、`agent.custom_tool_use` をGateway側が自分の資格情報で実行して結果を返す。コンテナは鍵を見ない（ただしGatewayがスケジュール管理DBに触れるため分離は崩れる）。
3. **Vault + egress-proxy**：送信時にプロキシで資格情報を注入し、サンドボックスには見せない。

> **結論**：Managed Agentsにenv/secret注入機能が追加されればbootstrapは不要になります。現状は個人用途として許容できる回避策であり、本番では「MCP化 + Vault」を追加設計するのが筋、というのが今回の設計判断です。

---

## 6. セキュリティモデルを「二軸」で理解する

このプロジェクトのセキュリティは、混同しがちな2つの軸を分けて考えると整理できます。

| 軸 | 何を守る/晒す | 関連する鍵 |
| --- | --- | --- |
| 正面玄関 | 誰が `/api/chat` を叩けるか | `GATEWAY_TOKEN` |
| ログ経由のDB到達 | スケジュール管理DB接続文字列がイベントログに残る | `ANTHROPIC_API_KEY` |

`GATEWAY_TOKEN`（64桁hex推奨）は正面の不正利用を防ぎますが、`ANTHROPIC_API_KEY` の漏洩は **別軸** であり、そこからイベントログ経由でDB接続文字列に到達しうる。両者は独立しています。

したがって実質の要は、**`ANTHROPIC_API_KEY` をスケジュール管理DBと同等に厳重管理すること** です。

実装済みの担保は以下の通りです。

* 秘密は **Vercel Environment Variablesのみ**。クライアント・git・ビルド成果物に非露出（`NEXT_PUBLIC_` 接頭辞なし＝サーバ専用）。
* `.gitignore` で `.env*.local` を除外。コミット前に `git check-ignore` / `git ls-files` で実機検証済み。
* 全経路HTTPS（Vercel標準）。
* 認証は `timingSafeEqual` + fail-closed。

低コストの追加ハードニングとしては、スケジュール管理DB用に **最小権限のNeonロール** を切っておく（接続文字列が漏れても被害を限定）のが効果的です。

---

## 7. データ層：2つのNeonインスタンスを分離する

地味ですが重要な設計判断が、Neonを **2つのインスタンスに物理分離** したことです。

|  | スケジュール管理DB（A） | セッション管理DB（B） |
| --- | --- | --- |
| env 変数 | `DATABASE_URL` | `SESSION_DATABASE_URL` |
| 中身 | speaking\_events / travel\_routes / 関数 | gateway\_sessions |
| アクセス主体 | **Agentのスキル**（サンドボックス内、`~/.neonrc` 経由） | **Gateway** が直接SQL |
| Gateway は SQL する? | ❌ しない（資格情報は預かるが操作しない） | ✅ する（唯一の直接SQL） |

当初は1本（`DATABASE_URL`）で兼用していましたが、**関心の分離**（ドメインデータ vs 運用状態）とバックアップ/権限設計のために分けました。

この分離で1つ学びがありました。DB分離前は、bootstrapが **セッション管理側のDB** を注入してしまっていたため、スキルがスケジュール管理テーブルを見つけられず、`gateway_sessions` と `neon_auth.*` しか検出できなかったのです。`DATABASE_URL` をスケジュール管理DBに修正し、セッション管理の `me` 行を削除して新規bootstrapさせたところ、無事38件のスケジュール取得に成功しました。

ここから得られる勘所はシンプルです ―― **「bootstrapが指すDBが、そのままスキルの参照先になる」**。

---

## 8. フロントエンド：PWAでホーム画面アプリ化

フロントは `app/page.tsx`（クライアントコンポーネント）1枚が主役です。

* `GATEWAY_TOKEN` を `localStorage` に保存。未設定ならログイン画面を出す。
* `fetch('/api/chat')` のレスポンスボディを `ReadableStream` として読み、SSEフレーム（`event:` / `data:`）を手動パースして逐次表示。
* Service Worker（`/sw.js`）を登録。

`app/manifest.ts` で `display: standalone`、アイコン192/512、テーマカラーを定義すると、Chromeの「ホーム画面に追加」が成立し、ネイティブアプリのように起動できます。

Service Workerは最小構成です。**API・非GETリクエストは常にネットワーク（キャッシュしない）**、それ以外はnetwork-first。チャットの応答を誤ってキャッシュしないことが肝心です。

---

## 9. 代表シーケンスで動きを追う

### 9-1. 初回リクエスト（新規セッション + bootstrap）

```
Android → POST /api/chat {message}
Gateway:
  auth OK
  getOrCreateSession('me'): セッション管理に無し
    createSession() → sesn_xxx
    bootstrapSession():
      events.send(user.message="...~/.neonrc に書け...")   # DATABASE_URL を注入
      events.stream() を idle まで読み捨て                  # 「neonrc written」を消費
    UPSERT gateway_sessions(me, sesn_xxx)
  events.stream() ← stream-first
  events.send(user.message=ユーザー発話)
  SSE 中継（session / message / tool / done）
```

初回はbootstrap分のレイテンシが乗ります（**実測 約65〜76秒**）。

### 9-2. 2回目以降（再利用）

```
getOrCreateSession('me'): 既存 sesn_xxx, retrieve → idle/running → 再利用
events.stream() → events.send → SSE 中継
```

bootstrapが無いので **実測 約5秒**、しかも前ターンの文脈を保持。セッション管理によるセッション再利用の効果がはっきり出ます。

### 9-3. Gatewayは発話を「加工しない」

たとえば「直近2週間のスケジュールを出力してください。」という入力に対し、Gatewayは **何も足さずに** これを送るだけです。

```
POST /v1/sessions/{id}/events
{ "events": [ { "type": "user.message",
  "content": [ { "type": "text", "text": "直近2週間のスケジュールを出力してください。" } ] } ] }
```

system プロンプトもスキルもモデルも、そして **日付** すら含めません。「直近2週間」の解決はAgent側（サンドボックスで `date` を叩く）が行います。Gatewayは基準日すら付けない、徹底した「素通し設計」です。返りは `agent.tool_use`（date / neon\_client.sh）→ `agent.message`（整形済みテーブル）→ `session.status_idle(end_turn)` と流れます。

---

## 10. デプロイと実機導入

### 10-1. Vercel

VercelのAdd New → Project → Import でGitHubリポをImportすれば、プロジェクト作成と同期設定が同時に済みます。Import画面の **Environment Variables** に以下6つを登録してからDeployします。

| 変数 | 用途 | 出所 |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | Managed Agents 呼び出し | Anthropic Console |
| `AGENT_ID` | 使用 Agent | agent-ids.json |
| `ENVIRONMENT_ID` | 使用 Environment | agent-ids.json |
| `DATABASE_URL` | スケジュール管理DB（bootstrap 注入） | Neon インスタンス A |
| `SESSION_DATABASE_URL` | セッション管理 | Neon インスタンス B |
| `GATEWAY_TOKEN` | 自分専用の認証トークン | 自分で生成（長いランダム） |

本コードはenvを **実行時のみ** 読むため、env無しでもビルドは成功します（失敗するのは実リクエスト時のみ）。env変更後は **Redeployが必要** な点に注意。以降は `git push` で自動デプロイされます。

### 10-2. スマホ導入

1. Chromeで本番URLを開く → `GATEWAY_TOKEN` を入力（localStorageに保存）
2. メニュー →「ホーム画面に追加」→ アプリのように起動
3. 自然文で発話（例「6/14 14:00 旭川高専でオンライン登壇を追加して」）

---

## 11. 検証結果（実測エビデンス）

ローカルと本番で確認した結果です。

| 項目 | 結果 |
| --- | --- |
| `GET /api/health` | `{"ok":true,...}`（本番でも確認） |
| 未認証 / 不正トークン `POST /api/chat` | **401**（ローカル・本番） |
| 初回 sync チャット（新規セッション + bootstrap） | 約65〜76秒で完走、`~/.neonrc` 書込 → スキル発火 → Neon接続 |
| スケジュール参照（DB分離後） | **38件** 取得・整形（speaking\_events / travel\_routes） |
| セッション再利用 | 同一 session\_id、**76s → 5s**、前ターンの文脈を保持 |
| SSE ストリーム | `event: session / message / done` を確認 |
| Android 実機 | ホーム画面追加 → 動作確認 OK |

---

## 12. 既知の落とし穴・学びまとめ

最後に、この設計で踏んだ・押さえておきたいポイントを一覧にしておきます。

* **betaヘッダは別物**：Managed Agents = `managed-agents-2026-04-01` / Skills API = `skills-2025-10-02`。前者はSDKが自動付与。取り違え注意。
* **`events.stream()` は `APIPromise` を返す** → `await` してから `for await`。
* **`idle` 単独でbreakしない**（`requires_action` は継続）。
* **bootstrapの `$HOME` と `&` クォート**（§5-2）。
* **サンドボックスは揮発** → `~/.neonrc` は新規セッション毎に再注入。
* **2つのDBの取り違え**：bootstrap注入先＝スキルの参照先。Gatewayのセッション管理は別インスタンス。

---

## おわりに

今回作った `schedule-gateway` は、コードの量こそ多くありませんが、**「窓口・中継・頭脳」を疎結合に分け、Managed Agentsを薄く中継する** という設計の練習台として、得るものが多いプロジェクトでした。

特に印象的だったのは、**シークレット注入という「正規の経路」が無い** という制約に対し、bootstrapという回避策とそのトレードオフ（イベントログ残留）を引き受け、「本番ではMCP化 + Vault」という出口まで含めて設計判断を記録できたことです。新しいプラットフォームを使うときは、こうした「足りないピース」とどう折り合うかが、そのまま設計の質になると改めて感じました。

今後は、

* **本番ハードニング**：DBアクセスのMCP化 + Vault
* **窓口の追加**：同じ `/api/chat` を叩くLINE Bot / Tasker（`?mode=sync` が有用）
* **マルチユーザー化**：`GATEWAY_TOKEN` → `user_key` の導出でセッション管理を分離

あたりを拡張していく予定です。Managed Agentsの実ユースケースを探している方の参考になれば嬉しいです。最後までお読みいただき、ありがとうございました。
