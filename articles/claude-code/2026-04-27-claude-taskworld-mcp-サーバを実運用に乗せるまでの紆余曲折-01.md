---
id: "2026-04-27-claude-taskworld-mcp-サーバを実運用に乗せるまでの紆余曲折-01"
title: "Claude × Taskworld MCP サーバを実運用に乗せるまでの紆余曲折"
url: "https://zenn.dev/yoshiki_otagaki/articles/ae51648618931c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "zenn"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

# Taskworld MCP サーバを自作してハマったこと全記録

## はじめに

業務で Taskworld（プロジェクト管理 SaaS）を使っている組織で、Claude（claude.ai / Claude Code / Claude Desktop）から直接 Taskworld のタスク・プロジェクトを操作できるようにしたかったので、MCP（Model Context Protocol）サーバを書いて Dokploy にデプロイしました。

「数日で終わるだろう」と思っていたら、**Snapshot 設計、レート制限、リアルタイム性のトレードオフ** で何度も壁にぶつかり、結局 PR を 6 つくらい重ねてようやく実運用に耐える形になりました。

ハマったポイントを共有します。同種のシステム（GitLab MCP、Notion MCP、Linear MCP など、サードパーティ SaaS の API を MCP でラップする系）を作っている人の参考になれば。

---

## 全体構成

最終形はこうなりました:

* HTTP MCP サーバ（Streamable HTTP / SSE 両対応）を Docker でデプロイ
* ユーザーごとに Taskworld の `access_token` を保管し、Bearer 認証で MCP セッションに紐付け
* **Snapshot パターン**: 夜間に全プロジェクト/タスクリスト/タスク/メッセージ等をディスクに丸ごと書き出し、read 系のツールはほぼ全てこれを参照
* **Write overlay（軽量 WAL）**: MCP 経由の write は Taskworld API に書きつつ、in-memory のオーバーレイにも反映 → 同セッション内で即座に可視化
* **Shared RateLimiter（per-workspace）**: 複数ユーザーの呼び出しを 1 個のトークンバケットで束ねて API 制限を遵守
* **Fresh オプション**: 主要 read ツールで `fresh: true` を指定すると snapshot を迂回して API 直取得 + overlay 書き戻し

シンプルに見えますが、ここに到達するまでに以下のフェーズを経ています。

---

## 第 1 章: search\_all\_tasks の N+1 地獄

最初は素直に「全エンドポイントを MCP tool として 1:1 にラップする」スタイルで実装しました。

問題が顕在化したのは「全プロジェクトを横断してタスクを検索する」ツール。Taskworld の REST API は

1. プロジェクト一覧取得 (`project.get-all`) — 1 call
2. プロジェクトごとのタスクリスト一覧 (`tasklist.get-all`) — N call
3. タスクリストごとのタスク取得 (`tasklist.get-tasks`) — N×M call

という階層構造で、数百プロジェクト・数千タスクリストを抱えるワークスペースだと 1 回の検索で**数千 API call** が必要になります。当然、

* 30 秒〜数分のタイムアウト
* HTTP 429（レート制限超過）の連発
* Claude の MCP セッションがハング

という地獄を見て、「これは API 直叩き型では無理」と気付きました。

---

## 第 2 章: Snapshot パターンの導入

そこで方針転換: 夜間に全データを 1 回フェッチしてディスクに保存し、read はそこから返す。

```
[3:00 JST]      [全件 fetch]    →    [snapshot.json]
                                          ↓
[ユーザー read]  ←────────  [snapshot 読み出し（API call ゼロ）]
[ユーザー write] ──→ Taskworld API ──→ [overlay 反映]
```

これで `search_all_tasks` のような重い read は **API 0 call** で完了するように。

ただし当然、**「snapshot のデータは最大 24 時間古い」** というトレードオフが発生します。これが後で別の問題を生みます。

---

## 第 3 章: 「Loaded 0 users」事件

snapshot を入れた直後、本番ログにこんな行が:

ユーザーは登録されているはずなのに 0 人。当然 SnapshotStore も生成されず、3:00 JST の nightly タイマーも動かない。

最初は「Docker ボリュームが消えた？」と疑いましたが、診断ログを足してみると判明:

```
[TOKENS] Dropped 1/1 record(s) from /data/tokens.json:
  required string fields (mcpToken, twAccessToken, twSpaceId) were missing.
  Shapes: [{createdAt,mcpToken,name}]
```

過去の GraphQL ベース実装時代の旧スキーマレコードが、新しい REST 実装の正規化関数で「必須フィールド不足」として**黙ってドロップ**されていた。`name` フィールドの存在で旧式と判別できる。

### 教訓

* **silent な fallback は最悪の挙動。** `return [];` する代わりに、捨てた件数とデータ形状をログに吐き、人間が気付ける形で。
* 旧データは別ファイル（`tokens.json.invalid.json`）に退避して手動復旧の余地を残す。

---

## 第 4 章: tasks=0 の謎

snapshot 構築は走るようになったが、完了ログを見ると:

```
[SNAPSHOT] Build completed: projects=227, tasks=0
```

プロジェクトは取れてるのにタスクが 0。`get_tasks_in_tasklist` も `search_all_tasks` も全部空配列を返す。一方で `task.get(task_id)` で個別取得すると中身が返ってくる。データ自体は存在している。

### 仮説 1: パラメータ名の不整合

他の `tasklist.*` 系エンドポイント（`tasklist.update`、`tasklist.delete`、`tasklist.add-task` 等）は全部 `list_id` を使っている。それなのに `tasklist.get-tasks` だけは `tasklist_id` を使っているのが不自然。「これか！」と思って `list_id` に統一してデプロイしたら:

```
HTTP 400 invalid_payload: "tasklist_id" is required
```

逆だった。`tasklist.get-tasks` だけは本当に `tasklist_id` が正しい。慌てて revert。

### 仮説 2: レスポンス構造の違い

レスポンスの生 JSON を 2 件分ログに吐く probe コードを仕込んで本番デプロイしたら、ビンゴ:

```
{
  "ok": true,
  "tasklist": {
    "list_id": "...",
    "title": "...",
    "tasks": [
      { "task_id": "...", "title": "..." }
    ]
  }
}
```

`data.tasks` ではなく `data.tasklist.tasks` にネストされていた。我々のコードは `data.tasks` を見ていたので毎回空配列。

クライアント側で 1 行 unwrap するだけで全部解決:

```
const data = await this.post("/tasklist.get-tasks", {...});
const tasks = Array.isArray(data?.tasklist?.tasks) ? data.tasklist.tasks : [];
return { ...data, tasks };
```

### 教訓

* **API ドキュメントだけを信じない。** エンドポイント名・パラメータ名・レスポンス形状の 3 つは、必ず生レスポンスで確認する。
* 「同じリソースの他の操作と命名規則が一貫しているはず」という勘は外れる。`tasklist.get-tasks` の `tasklist_id` のような outlier は普通にある。

---

## 第 5 章: snapshot 構築が遅すぎる問題（4 時間 → 30 分への道）

データは取れるようになった。でもビルドが終わらない。

最初の build は **約 4 時間**。「夜中に走らせるからまあ……」と諦めかけたが、ユーザーが増えたら破綻するので根本対処することに。

### ボトルネック分析

コードを精査して 3 つの絞りが重なっていることが判明:

1. `SNAPSHOT_THROTTLE_MS = 1200`: 1 call ごとに 1.2 秒 sleep。実効 50 calls/min。
2. **per-user RateLimiter**: `TaskworldClient` のコンストラクタで都度 `new RateLimiter(950, ...)`。各ユーザー独立で 950/min を「持ってる」と楽観視。
3. **`SnapshotStore.globalBuildQueue`**: 全ユーザーの build を直列化する static キュー。10 ユーザーなら 10 倍時間。

### 修正

* `SNAPSHOT_THROTTLE_MS` のデフォルトを `0` に。
* `RateLimiter` を `(apiBase, spaceId)` キーの**共有レジストリ**に変更。同じワークスペースの全 `TaskworldClient` は 1 個の `RateLimiter` を共有。
* `globalBuildQueue` を撤廃。`SnapshotStore` インスタンスごとの `buildPromise`（同一ユーザーの重複 refresh dedup）だけ残す。
* build 内部の for ループを `pMap(concurrency=8)` で並列化。

これで理論上 950 calls/min ＝ 8 分で完走するはず。デプロイ → トリガー → 結果:

```
HTTP 429: Rate Limit for this ip address has exceeded.
```

---

## 第 6 章: per-IP だった

エラーメッセージにヒント:

```
Rate Limit for this ip address has exceeded
```

レート制限は **per-IP**。Taskworld のドキュメントには「1000 calls/minute」としか書かれていないが、実際は IP 単位。1 つの Dokploy サーバから複数ユーザーが叩いても合算される。

しかも実効値は 1000/min ではなく **300〜600/min くらい**で 429 を出してくる（厳密な閾値はドキュメント化されていない）。さらに、トークンバケット容量を 950 にしていると初手で 950 calls をバーストして即死。

最終的に環境変数で:

```
TW_RATE_LIMIT_CAPACITY=10        # バースト 10
TW_RATE_LIMIT_PER_SECOND=5       # 持続 300/min
SNAPSHOT_BUILD_CONCURRENCY=4     # 並列 4
```

に絞り、1 ユーザーあたり約 30 分で安定。429 はほぼ消えた。

### 教訓

* **API ベンダの「N requests/minute」表記は一次情報ではない。** 実効値は実測で詰めるしかない。
* バースト容量と持続レートを別々に設定できるのが token bucket の利点だが、両方ちゃんと意識しないと初手で死ぬ。
* per-IP / per-token / per-workspace のどれかは**エラーメッセージで示唆されることが多い**。最初の 429 メッセージを丁寧に読む。

---

## 第 7 章: スケール時の現実

per-IP 制限の判明により:

| ユーザー数 | 単一サーバ運用 | ローカル（各自 PC）起動 |
| --- | --- | --- |
| 1 | 30 min/晩 | 30 min/晩 |
| 10 | 5 hour/晩 | 30 min/晩（並列・各自の IP） |
| 50 | 25 hour/晩（**破綻**） | 30 min/晩 |

つまり中央集権型は per-IP 制限が直撃する。スケールさせるなら:

* **A.** 複数サーバ IP に水平分散（共有ストレージが必要、運用複雑）
* **B.** ローカル MCP 起動（各ユーザーの PC から、各ユーザーのアカウント・IP で叩く）← MCP の本来形
* **C.** mid-day incremental refresh（API が `updated_since` 系を持っていれば可能だが、Taskworld は message 系だけ）

10 人規模なら 5 時間メンテウィンドウで運用、それ以上は B を真剣に検討、というのが現実解。

---

## 第 8 章: 「今いじったやつが見えない」問題

ここまでで日常の運用は安定。でも別の課題が:

> 「今 Taskworld の Web UI で編集したタスクが、Claude 側からは古い状態に見える」

snapshot は前夜のデータ。write overlay は MCP 経由の自分の write しか拾わない。外部変更（Web UI、他ユーザー、他 MCP セッション）は次の nightly まで反映されない。

解決策として `fresh: boolean` オプションを主要 read ツールに導入:

| ツール | `fresh=true` の意味 | コスト |
| --- | --- | --- |
| `get_task(id, fresh)` | そのタスク 1 件最新化 | 1 call |
| `get_tasks_in_tasklist(p, l, fresh)` | そのタスクリスト最新化 | 1 call |
| `list_tasklists(p, fresh)` | プロジェクト内タスクリスト一覧最新化 | 1 call |
| `list_projects(fresh)` | 全プロジェクト一覧最新化 | 1 call |

`search_all_tasks` は意図的に非対応（数千 call になるため snapshot 固定）。

`fresh` で取得したデータは **overlay に書き戻す** ので、同セッションで 1 回 `fresh` すれば以降の非 `fresh` read も最新値が返る。

これで「**速度（snapshot）**」「**鮮度（fresh）**」「**自身の write の即時可視化（overlay）**」の 3 層が揃いました。

---

## 学んだこと

1. **silent な空配列を信じない。** 落とした件数・形状のログを最初から仕込む。
2. **API ドキュメントは出発点であって正解ではない。** 生レスポンスを見るログを最初から仕込む。
3. **レート制限は per-IP/per-token/per-workspace のどれかを実測で確かめる。** バースト容量と持続レートは別物。
4. **大規模ワークスペース向けには snapshot 必須。** 直叩きはユーザー体験を破壊する。
5. **snapshot 構築は思ったより重い。** 並列化と RateLimiter の調整をフルにやっても 30 分〜1 時間が現実的なライン。夜間バッチ前提の運用設計を。
6. **「今この瞬間の状態」が必要なケースはある。** snapshot 設計でも fresh モードを残す。
7. **per-IP 制限はスケーリングの天井。** 本格的に増やすならローカル起動型 MCP に倒す方が筋が良い。

---

## おわりに

着手前は「API ラップするだけ」と思っていた MCP サーバが、**API 設計の罠 × レート制限 × 大規模データ × リアルタイム性** という典型的な複雑さを全部踏むことになりました。

でも、**Snapshot + Overlay + RateLimiter + Fresh** という最終形に到達してみると、これは Taskworld 固有じゃなく「**サードパーティ SaaS API を MCP でラップする時の汎用パターン**」だと感じます。Notion, Linear, Asana, ClickUp あたりも、同じワナに同じ順番でハマる可能性が高いはず。

もし同じ道を歩んでる人がいたら、この記事のどこかが少しでも近道になれば嬉しいです。
