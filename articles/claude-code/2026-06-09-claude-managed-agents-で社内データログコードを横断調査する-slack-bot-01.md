---
id: "2026-06-09-claude-managed-agents-で社内データログコードを横断調査する-slack-bot-01"
title: "Claude Managed Agents で社内データ・ログ・コードを横断調査する Slack bot を安定運用する方法"
url: "https://zenn.dev/dinii/articles/1cfac1ca8b46c3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回の記事『[Claude Managed Agentsで「まずエンジニアに聞こう」を「まずbotに聞こう」に変えた](https://zenn.dev/dinii/articles/d7be3acc43d868)』では、ダイニーが社内向け Slack bot `@ask-anything` を Claude Managed Agents で組み、社内エンジニアへの調査依頼 (= dev-help) を半減させた話を書きました。本記事はその技術編で、**Slack から Claude Managed Agents を安定運用するためのダイニーの実装パターン** を紹介します。

記事1に書いた通り、Managed Agents を使うとダイニー側で書くコードは 3 種類に収束します。

1. Slack からイベントを受ける薄い HTTP handler
2. Claude Managed Agents の session を作り、events を中継する relay
3. agent から呼ばれる custom tool の実装本体（BigQuery 実行、Cloud Logging 実行、CSV upload など）

ただし「3 種類に減った」のは結果の話で、そこに辿り着くまでに Claude Managed Agents 特有の制約・振る舞いをいくつか踏まえる必要がありました。本記事では、以下の 3 つの実装パターンと、運用コストの削り方、そして bot を継続的に改善するための開発手法を扱います。

* **Repo mount** — ダイニーの monorepo を session ごとに clone して agent に grep させる構造
* **Skills mount** — `version: "latest"` で skill を publish した瞬間に本番反映される運用
* **Session reuse** — Slack thread と Anthropic session を 1:1 で対応させる仕組み

なお Claude Managed Agents は記事執筆時点で beta で、`skills-2025-10-02` 等の beta フラグを明示的に渡す必要があります。SLA や料金体系も通常の API とは別建てになるので、採用を検討する場合は最新の公式ドキュメントを確認してください。

### 全体の流れ

詳細に入る前に、ざっくりした流れを 1 枚にしておきます。

Slack のメンションを Cloud Run（runtime パッケージ）が受け取り、Claude Managed Agents に session を作って中継します。agent が必要なら BigQuery / Cloud Logging / monorepo の grep などを Cloud Run 経由で実行し、最終回答が Slack スレッドへ返ります。

---

## 1. アーキテクチャ全体像

### 1.1 登場人物

本記事の説明は、以下の 5 つの登場人物を頭に入れておくと追いやすいです。

| 登場人物 | 役割 | 持ち物 |
| --- | --- | --- |
| **runtime パッケージ** | ダイニーが運用する Cloud Run service | Slack 署名検証 / session 管理 / GCP ADC（Application Default Credentials）/ custom tool の実装本体 |
| **agent 定義パッケージ** | ダイニーが管理する agent 定義の SSOT（Single Source of Truth） | system prompt / tool schema / skill content / MCP server URL |
| **Claude Managed Agents API** | Anthropic 側の SaaS | session のライフサイクル管理 / event stream / skill 配信 |
| **Sandbox** | session ごとに起動する隔離環境 | Python / bash / file system / `/workspace/<monorepo>` / `/workspace/skills/*` |
| **外界のツール** | BigQuery / Cloud Logging / Slack / Notion / GitHub / Sentry / channel-talk | ダイニーの credential が必要 |

Runtime と Agent 定義は「ダイニーが書く側」、Claude Managed Agents API と Sandbox は「Anthropic がホストする側」、外界のツールは「読みに行く相手」と分かれます。

### 1.2 2 パッケージに分けた理由

ダイニーが書く側は、monorepo 内の 2 パッケージに分割してあります。

| パッケージ | 役割 |
| --- | --- |
| **agent 定義パッケージ** | **agent 定義側**: system prompt / custom tool schema / MCP server URL / skill content をすべて保持し、`bun run update-agent` で Anthropic に push する |
| **runtime パッケージ** | **runtime 側**: Cloud Run service。Slack イベントを受け取り、session を作成し、agent から emit された custom tool 呼び出しを実行し、結果を session に送り返す |

分割しておくと、prompt 試行錯誤と runtime の安定運用がそれぞれ独立した loop で回せます。さらに **runtime パッケージは複数の managed agent bot で共有できる** ので、新しい bot を追加するときも agent 定義パッケージだけ書けば済みます（ダイニーでは同じ runtime に別の bot も同居させています）。

### 1.3 システム全体構成

ここまでの登場人物がどう繋がっているかを描くと次のようになります。

![](https://static.zenn.studio/user-upload/40a8bc37dd7c-20260609.png)

この図から読み取りたいポイントは 3 つあります。

1. Slack からのイベントは、まず runtime パッケージが受け取ります（署名検証 → session lookup → Anthropic への中継）
2. Sandbox からアクセスできる経路は、「直接アクセスできるもの」（MCP / `github_repository` / skill ファイル）と「custom\_tool 経由で runtime が実行するもの」（BigQuery / Cloud Logging / Slack 投稿）の 2 系統に分かれています
3. agent からの events は stream で返り、runtime パッケージがそれを逐次読みつつ custom tool を実行し、結果を session に返却します

### 1.4 何がどちら側にあるか

最終的に Runtime と Agent 定義がそれぞれ何を持っているのかを 1 枚にまとめます。

| 持ち物 | Runtime 側 | Agent 定義側 |
| --- | --- | --- |
| Slack signing secret / bot token | ○ | — |
| GCP ADC / Service Account impersonation | ○ | — |
| BigQuery 実行 / Cloud Logging 実行 | ○ | — |
| Slack への CSV upload | ○ | — |
| Slack thread ↔ session\_id の Map | ○ | — |
| GitHub App installation token mint | ○ | — |
| system prompt の本文 | — | ○ |
| custom tool の schema (`input_schema`) | — | ○ |
| MCP server URL | — | ○ |
| Skill content (`SKILL.md`) | — | ○ |
| `version: "latest"` での agent / skill bind | — | ○ |

Agent 定義側は「LLM が何を見て何を考えるか」の情報源、Runtime 側は「外界に副作用を起こす実行系」、という分担です。この分担を守るかぎり、prompt engineering は agent パッケージ内で完結し、Cloud Run 起因の事故も runtime パッケージ内で完結します。

ただし運用上の地雷が一つだけ残っています。tool の `input_schema` は agent 側に書く（LLM が schema を読んで呼び出すため）一方で、tool の実装本体は runtime 側にあります。**両者は容易に drift しうる** ため、schema を変更したら必ず実装側の case 分岐も変更する、という運用ルールが必要です。現状は手動レビューで guard していますが、自動化したい領域として残っています。

---

## 2. Repo mount + Skills + Memory — Anthropic 側に資産を渡す 3 つの API

ここから Anthropic 側に渡すリソースの話に入ります。`sessions.create` の `resources` には Repo mount / Skills mount / Memory store の 3 種類を渡せ、それぞれライフサイクルと用途が異なります。  
![](https://static.zenn.studio/user-upload/52ef1e794af2-20260609.png)

「重い・あまり変わらないもの」を Repo mount、「軽い・頻繁に変わる procedural knowledge」を Skills mount、「運用中の experiential knowledge」を Memory に積む、と分けると気持ちよく運用できます。以下で順に整理します。

### 2.1 Repo mount: `github_repository` resource

agent に「いまのコードを見て答えて」と頼む場合、sandbox から直接ダイニーの monorepo を読めると話が早いです。Claude Managed Agents は `github_repository` という session resource を持っており、session 起動時に Anthropic 側で clone されます。

runtime パッケージで session を作るとき、resources は以下のように構築します。

```
const githubToken = await fetchInstallationToken();
const resources = [
  {
    type: "github_repository",
    url: DINII_SELF_ALL_REPO_URL,
    authorization_token: githubToken,
    mount_path: DINII_SELF_ALL_MOUNT_PATH,
    checkout: { type: "branch", name: DINII_SELF_ALL_BRANCH },
  },
  // ...
];
```

![](https://static.zenn.studio/user-upload/e603a1ad184f-20260609.png)

ポイントは 3 つあります。

**① GitHub App installation token を session ごとに mint する**

`fetchInstallationToken()` は GitHub App の installation token を JWT（JSON Web Token）経由で取得する関数です。token の TTL は 1 時間で、長期 PAT（Personal Access Token）を使わずに済みます。session 起動のたびに新しい token を取って `authorization_token` に渡すので、token が漏れたところで影響範囲は session 寿命に限定されます。

**② token は clone にだけ使われ、Anthropic は token をログに残さない**

Anthropic 側のドキュメント上、`authorization_token` は repo clone のために使われるだけで、agent の応答や API ログには出ません。これは公開ドキュメントを信頼している前提なので、念のため定期的に token を rotate する運用は欲しいところです（GitHub App の private key 自体を rotate するだけで、各 session が次回からは新しい token を使います）。

**③ checkout はブランチ指定可能**

`checkout: { type: "branch", name: ... }` で指定したブランチが、sandbox 内の指定 mount path（例: `/workspace/<monorepo>`）に展開されます。ダイニーは `main` を指定しています。タグや特定 commit を指定する選択肢もあり、再現性を重視する場合は commit SHA で固定する手もあります。

### 2.2 Repo mount の使われ方

sandbox 内の agent は、bash 経由で以下のように使います。

```
# 関数の定義位置を探す
rg -n "export const dispatchCustomTool" /workspace/<monorepo>

# あるテーブルがどこから INSERT されているか
rg -nC2 "INSERT INTO\s+slack_agent_hub.threads" /workspace/<monorepo>
```

agent は system prompt と skill の指示に従って、必要なら `rg` で grep、`sed` で行範囲を切り出し、要約します。read-only mount なので、agent が誤って書き換えても永続化されません。

### 2.3 Skills mount: `version: "latest"` の即時反映

Repo mount が「コードを積む」のに対して、Skills mount は「やり方マニュアルを積む」ものです。agent に「BigQuery の特定テーブルはこう叩く」「Cloud Logging はこのフィルタで引く」といった procedural knowledge を渡す仕組みです。

ask-anything では現状 20 個の skill を運用しています。

```
// agent 定義パッケージ（要旨）
const SKILLS = [
  { type: "custom", skill_id: BIGQUERY_SKILL_ID, version: "latest" },
  { type: "custom", skill_id: DEV_HELP_PRIOR_CASE_SKILL_ID, version: "latest" },
  { type: "custom", skill_id: ESCALATION_TEAM_ROUTING_SKILL_ID, version: "latest" },
  { type: "custom", skill_id: OPS_REQUEST_ESCALATION_SKILL_ID, version: "latest" },
  { type: "custom", skill_id: CLOUD_LOGGING_RULES_SKILL_ID, version: "latest" },
  { type: "custom", skill_id: POS_DEVICE_VERSION_CHECK_SKILL_ID, version: "latest" },
  // ... 他 14 個
];
```

Skills API には **2 層構造** があります。

* **skill**: 論理エンティティ（`skill_id` で識別、不変）
* **version**: その時点での content snapshot（publish するたびに増える）

agent は `{ skill_id, version: "latest" }` の形で skill を参照します。**`version: "latest"` で publish した瞬間に live agent へ反映される** ので、運用上「skill 更新 = publish」だけで本番反映が完了します。Cloud Run の再デプロイも `update-agent` も不要です。

ところで、この Skills API には **「1 つの agent に登録できる skill は 20 個まで」** という上限があります。ask-anything はいま 20 個ちょうどで、すでに上限に張り付いています。bot がカバーする領域を広げるほど「この手順も skill に切り出したい」が増えていくのに、もう枠が空いていない——という地味な悩みを抱えながら運用しています。

### 2.4 Skill upload の実装

各 skill の中身は `skills/<name>/SKILL.md` に Markdown で書きます。upload は `upload_skill.ts` の `uploadSkill` 関数が担当し、skill ファイルを `multipart/form-data` で Anthropic API に POST します。

* **初回**: `POST /v1/skills` で新しい skill を作り、返ってきた `skill_id` を `.env` に保存
* **以降**: `POST /v1/skills/{id}/versions` で同じ `skill_id` に新しい version を publish

`bun run upload-<name>-skill` 1 コマンドで version が増え、`version: "latest"` でバインドしている agent に即時反映されます。「prompt 編集 → publish → 30 秒後に動作確認」のループで procedural knowledge を磨いていけます。

### 2.5 Memory store — フィードバックから自律改善する

Repo mount と Skills mount は「人間が事前に渡す静的資産」ですが、もう一つ **agent が自分で書き込める memory store** という枠があります。`sessions.create` の `resources` に `memory_store` を `access: "read_write"` で渡すと、agent が session 内で knowledge を書き込み、次以降の session で読み出せます。

```
// runtime パッケージ（要旨）
const resources = [
  /* github_repository など */
  ...(config.MANAGED_AGENT_MEMORY_STORE_ID_ASK_ANYTHING
    ? [{
        type: "memory_store" as const,
        memory_store_id: config.MANAGED_AGENT_MEMORY_STORE_ID_ASK_ANYTHING,
        access: "read_write" as const,
      }]
    : []),
];
```

ダイニーでは ask-anything の memory を **「調査を速くする memo」** として使っています。貯めるのは汎用知識ではなく、次に同じ系統の質問が来たときに調査を加速する情報——前提条件、最初に打つべき一手、ハマった行き止まり、エスカレーション先の候補——です。読むのは調査の冒頭で一度、書くのは調査の終わりに最大 1 エントリ、と頻度を絞っています。

書き込みトリガーで一番優先度が高いのが **訂正イベント** です。これには 2 種類あって、**人間が間違いを指摘したとき**（「それ違うよ」「○○ではなく△△」）だけでなく、**agent が後のターンで自分の回答を訂正したとき**（「先ほどの回答を訂正します」）も含みます。訂正が入ったら、**間違った内容を書いていたはずのエントリを上書き**します——「訂正メモ」を別に足すのではなく、正しい内容で丸ごと置き換える。スレッドには訂正のやり取りが残るので、memory 側は最新の正解だけを持てばいい、という考え方です。

![](https://static.zenn.studio/user-upload/31fa95bbf216-20260609.png)

Skills mount が「人間が前もって書く procedural knowledge」だとすると、memory store は「agent が運用中に蓄えていく experiential knowledge」と整理できます。両者を組み合わせると、初期は skill に書いた前提で動き、運用しながら memory で精度が上がっていく形になります。

---

## 3. Session reuse — Slack thread と Anthropic session を繋ぐ運用

ここまでで「sandbox に渡すもの」「sandbox の外で実行するもの」「Anthropic 側に積むもの」が揃いました。最後に残るのが **「Slack thread と Anthropic session を繋ぎつづける運用」** です。

### 3.1 なぜ session を再利用するか

Slack の会話は thread 単位で続きます。ユーザーが追加質問を投げれば、bot は **前の質問・回答を踏まえて** 答える必要があります。素朴に毎回新しい session を作ると、

* thread のコンテキストを毎回 prompt に詰め直す必要がある（コスト・遅延が増える）
* Anthropic 側の memory store / prompt caching の恩恵を受けられない
* skill が「過去に同じ thread でやった調査」を踏まえて動けない

ので、ダイニーは **「Slack thread の `thread_ts` と Anthropic の `session_id` を 1:1 にマップする」** という運用にしています。

### 3.2 session-manager を Firestore で永続化する

最初は session-manager を runtime プロセス内の in-memory `Map<threadTs, Entry>` で持っていました。ところがこの構成には穴があります。Cloud Run のリビジョンが切り替わると、新しいコンテナは空の RAM で起動するので、**この Map がまるごと消えます**。

ここで失われるのは Anthropic 側の session そのものではなく、runtime が握っていた **`thread_ts → session_id` の対応表** です。session 自体は Anthropic 側に在って、`session_id` さえ分かれば再開できます。ただ、その対応表を失うと runtime は既存 session を参照できず、追加質問が来ても **新しい session を立て直して** しまいます。文脈はリセットされ、prompt キャッシュも効かない cold start になる——これをデプロイのたびに踏んでいました。

そこで対応表を runtime の外、**Firestore に永続化** しました。ステートレスな Cloud Run から状態を切り離して managed store に逃がすのは定石で、なかでも Firestore は同じ GCP プロジェクト内で VPC もいらず、`thread_ts` を document id にすれば O(1) で引けて書き込み量も少ないので、この小さな対応表の置き場としては一番軽い選択でした。Cloud Run と同じ project の `thread_sessions` コレクションに、Slack の `thread_ts` をそのまま document id にして 1 スレッド 1 ドキュメントで保存します（`thread_ts` の `.` は Firestore の doc id でそのまま使えるので、サニタイズなしで引けます）。

```
// session-store.ts（要旨）
type ThreadSessionDoc = {
  sessionId: string;
  createdAt: Timestamp;   // serverTimestamp() で記録
  inFlight: boolean;      // まだ回答を生成中か
  channel: string;        // 復旧時に relay を貼り直すのに必要
  // …isEscalation / triggeringUserId
};

await collection.doc(threadTs).set(doc);            // 登録（upsert）
const snap = await collection.doc(threadTs).get();  // 参照
```

`registerThreadSession` / `lookupThreadSession` / `removeThreadSession` という公開 API の名前はそのままに、中身を Firestore 越しの非同期呼び出しへ差し替えました。呼び出し側は `await` を付けるだけで、リビジョンを跨いでも session を見失わなくなります。  
![](https://static.zenn.studio/user-upload/e4177c794b2e-20260609.png)

### 3.3 TTL と起動時の復旧 sweep

Firestore に積みっぱなしだとゴミが溜まるので、2 段構えで掃除します。

* **遅延 TTL**: `lookupThreadSession` のたびに `createdAt + TTL` を過ぎていないか見て、超えていればその場で削除する
* **起動時 sweep**: インスタンス起動時に `inFlight = true` のまま残っているドキュメントを拾い、リビジョン切替やクラッシュで中断された調査を **relay を貼り直して再開** する。再開を流し終えてから、TTL 超過の古いドキュメントをまとめて消す

ドキュメントに `channel` を持たせているのはこの復旧 sweep のためです。in-memory だった頃は request handler が channel を知っていましたが、Firestore から復元するときは周辺の文脈が何も残っていないので、ドキュメント単体で relay を貼り直せるよう必要な情報を持たせています。

### 3.4 timeout した session を Cloud Tasks で retry する

session 再利用と対になるのが、**失敗した session の自動リトライ** です。これも deploy をまたいで生き残らせる必要があります。Anthropic 側で障害が起きると（例: 2026-05-13 の約 30 分の incident）、数分ぶんのリトライ budget では吸収しきれず session が timeout します。これを「5 分後 → 15 分後 → 30 分後」と間隔を空けて投げ直したいのですが、素朴に `setTimeout` で待つと **リビジョン切替で待機ごと消えます**。session 永続化と同じ穴です。

そこで auto-retry のスケジュールを **Cloud Tasks** に逃がしました。スケジュールとリトライ間隔は Cloud Tasks が持ち、リトライに必要な文脈（質問文・添付・attempt 回数）は Firestore に置いて、task の payload には Firestore のドキュメント id だけを載せます。発火時刻になると Cloud Tasks が runtime の `/ask-anything/auto-retry-fire` を叩き、handler が文脈を読み直してリトライします。

ここで一度ハマったのが認証でした。Cloud Tasks から runtime を叩くときは OIDC トークンで認証しますが、Cloud Tasks がそのトークンを発行する（= 指定した service account を名乗る）には、runtime の SA に対象 SA を **actAs する権限**（`roles/iam.serviceAccountUser`）が要ります。これが欠けていて `createTask` が `PERMISSION_DENIED` で静かに落ち、auto-retry が本番で動いていなかった、というのを後から見つけて塞ぎました。

## 4. コスト削減 — 静的プレフィックスと BigQuery の課金バイト

Managed Agents は便利な一方で、放っておくとコストが効いてきます。運用しながら効いた打ち手を 2 つ紹介します。1 つは Anthropic 側のトークンコスト、もう 1 つは BigQuery 側のクエリコストの話です。

### 4.1 静的プレフィックスを削る

Anthropic 側でまず効くのが **prompt caching** です。session のターンが進むたびに、agent は毎回ほぼ同じ「前置き」——system prompt と、使えるツール・skill の定義——を読み込みます。この前置きは prompt cache に乗るので 2 回目以降は安く読めますが、**それでも毎ターン読み直すぶんのコストがかかります**。前置きが大きいほど、会話が長引くほど、地味に積み上がっていきます。

![](https://static.zenn.studio/user-upload/c247f194c9df-20260609.png)

そこで、一番コントロールしやすい **system prompt** を削りにいきました。やったことは 2 つです。

* **圧縮**: 冗長な言い回しや重複したルールを畳んで、同じ意図を短く書く
* **skill への切り出し**: 「customer 向け返信の作法」のような毎回は要らない詳細手順を system prompt から抜き、skill の `SKILL.md` に移す。skill 本体は必要なときだけ読まれるので、常時載る前置きから外せる

これは一度やって終わりではありません。障害や失敗のたびに「次から気をつけるルール」を足したくなるので、system prompt は運用するほど自然に伸びていきます（ask-anything に限らず、LLM アプリならどこでも起きる話だと思います）。だからこそ「足したくなる圧力」と「定期的に圧縮して skill へ逃がす」のバランスを取り続けるのが、コストを抑える地味な勘所になります。

### 4.2 BigQuery の課金バイト上限

もう一方の BigQuery は、**1 クエリで課金されるバイト数に上限**をかけています。実行するジョブに BigQuery ネイティブの **`maximumBytesBilled`** を付けるだけです。

```
const [job] = await bq.createQueryJob({
  query: sql,
  maximumBytesBilled: String(config.BQ_QUERY_MAX_BYTES_BILLED), // 例: 32 GiB
  labels: BQ_JOB_LABELS_QUERY,
});
```

ポイントは、これが **実際に課金されるバイト（＝パーティションやクラスタリングで絞り込んだ後の量）** に対する上限だということです。実行前の見積もりではなく実課金ベースなので、`id` クラスタの巨大 CDC テーブルに `WHERE id = ...` で当てるような、実際には一瞬で終わるクエリを過大に見積もって弾いてしまうことがありません。そのうえ上限を超えるとジョブは **課金されずに失敗する** ので、「本物のコスト天井」かつ「超過しても無課金」の安全弁になります。上限はインライン照会で 32 GiB、CSV エクスポートで 64 GiB にしています。

上限に当たったときは「query failed」で終わらせず、「この CDC テーブルは WHERE や列削りでは上限を切れないので、curated テーブルを使うか人間にエスカレーションして」という **次の手を示すメッセージ** に翻訳して agent に返します。同じ重いクエリを延々叩き直す無駄ループを防げます。

## 5. 開発手法 — bot を継続的に良くするループ

ここまでは「bot をどう組むか」の実装パターンを見てきました。ただ、社内 bot は一度組んで終わりではなく、運用しながら回答の質とコストを直しつづける対象です。ここでは、ダイニーが実際に回している改善の手法を 2 つ紹介します。

### 5.1 回答ログを Claude Code に分析させて改善する

Claude Managed Agents の Sessions API は、セッションごとの token 使用量・実行時間・呼ばれたツールの一覧を返します。これを集計するだけで、「どのセッションが重いか」「どのツールが実際には使われていないか」が見えてきます。ダイニーでは、この生データを人間に読める形へ変換する小さなツールをいくつか用意し、本番の回答ログを Claude Code に分析させて改善点を見つけています。

たとえば、特定のセッションを丸ごと書き出すツールはこれだけです。

```
# 本番セッションのイベントを JSONL に書き出し、
# イベント種別・ツール使用回数・token 内訳のサマリを表示する
bun run dump-session <session_id>
```

書き出した JSONL を Claude Code に渡すと、「同じツールを何度も呼び直している」「重い結果を抱えたまま会話が伸びている」といった無駄をそのまま指摘してくれます。期間内の全セッションを集計するツールと組み合わせれば、改善の前後で同じ指標を取り直して、効いたかどうかを確かめられます。

凝った dashboard を作り込んだわけではありません。Sessions API が出す構造化データを土台に、「測る → Claude Code に分析させる → 直す → また測る」を回しているだけです。大事だったのは、Claude Code が読める形のデータを安く取り出せることでした。

### 5.2 評価指標を集めて改善に繋げる

回答が役に立ったかどうかは、最終的には使った人にしか分かりません。そこで、回答メッセージに付いた Slack のリアクション（👍 / 👎）をそのまま評価シグナルとして集めています。

リアクションが付くと、その event を BigQuery のテーブルに 1 行ずつ貯めます。👎 が付いたときだけはスレッドに「どこが間違っていたか教えてください」と返信を促し、返ってきた訂正は bot 自身の memory（2.5）へ反映されます。評価を集める仕組みと、間違いから学ぶ仕組みが地続きになっている形です。

![](https://static.zenn.studio/user-upload/423a8f470c20-20260609.png)

集めた生データは、週に一度のジョブが集計し直し、利用件数・スレッド数・起票数・評価率（👍 と 👎 の比率）・リードタイムといった指標にまとめます。結果は同じく週次で開発相談チャンネルへ自動投稿され、利用が広がっているか・回答の質が保てているかをチームで眺められるようにしています。

![](https://static.zenn.studio/user-upload/6da31c14966e-20260609.png)

この指標は、成果を対外的に主張するためというより、**次にどこを直すべきかを決める物差し**として使っています。評価率が落ちた週があれば回答フォーマットを見直す、特定領域のリードタイムが伸びていればその領域の skill を厚くする、といった具合です。bot を「作る」フェーズから「育てる」フェーズに移ると、こうした指標が次の一手を決めてくれます。

## 6. 利用状況を可視化する

5.1・5.2 が回答の質を上げるための計測だったのに対して、運用が続くと「そもそも bot がどれくらい使われているか」も気になってきます。ダイニーでは、bot のコメント数・参加したスレッド数・開発相談チケットの起票数・エスカレーション率を週次で集計し、直近 26 週ぶんを 1 枚のダッシュボードにまとめています。

5.2 の週次サマリが「今週はどうだったか」のスナップショットだとすると、こちらは「bot がどれだけ仕事を引き受けるようになったか」を長い目で追うための図です。利用が広がる一方で起票は減ってきている、といった全体の動きが 1 枚で見えるようにしています。

![](https://static.zenn.studio/user-upload/4ce675e3e583-20260609.png)

## 7. まとめ

Claude Managed Agents を使うと、tool use loop の retry / sandbox 管理 / skill 配信といった orchestration の重荷が API 層に消えます。自前で書くコードは Slack handler + relay + custom tool 本体 + session-manager といった、限られた部品に収束しました。

本記事で扱った実装パターン（Repo mount / Skills / Session reuse）とコスト削減、各章末の注意点を踏まえれば、Slack から Managed Agents を安定運用に乗せられます。Managed Agents の実装に取り組むときに、本記事が参考になれば幸いです。

経営インパクト側の話は記事1『Claude Managed Agentsで「まずエンジニアに聞こう」を「まずbotに聞こう」に変えた』に書いています。
