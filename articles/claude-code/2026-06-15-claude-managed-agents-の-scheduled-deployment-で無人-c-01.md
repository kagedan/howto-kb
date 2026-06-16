---
id: "2026-06-15-claude-managed-agents-の-scheduled-deployment-で無人-c-01"
title: "Claude Managed Agents の scheduled deployment で無人 cron 実行"
url: "https://zenn.dev/tom1414/articles/c8fd4f32effa95"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

こんにちは、とむです。  
今回は、2026年6月10日にCode with Claude Tokyo イベントで public beta として発表された、Managed Agentsの「**scheduled deployment**」機能を使ってみました！  
私もManaged Agentsを使うのは初めてのため、その辺りもかみ砕きながら本編へ入っていきます！

## 0. Claude Managed Agentsとは

Claude Managed Agents は、Claude を**自律エージェント**として実行するためのハーネスとインフラストラクチャを提供する仕組みです。  
Claude Managed Agents は、4 つの概念を中心に構築されています。

| 概念 | 説明 |
| --- | --- |
| エージェント | モデル、システムプロンプト、ツール、MCPサーバー、およびスキル |
| 環境 | セッションが実行される場所の設定：Anthropicが管理するクラウドサンドボックス、または独自のインフラストラクチャ上のセルフホスト型サンドボックス |
| セッション | 環境内で実行中のエージェントインスタンスで、特定のタスクを実行し出力を生成するもの |
| イベント | アプリケーションとエージェントの間で交換されるメッセージ（ユーザーターン、ツール結果、ステータス更新） |

### Claude Codeとは何が違う？

これは筆者が初学時によく分からなかった部分だったため、一応まとめておきます！  
Claude Managed Agentsはクラウド上で自律的にタスクを完了するフルマネージド型サービスであることに対し、Claude Codeはリアルタイムで対話しながら作業するツールです。

適用シナリオの違いは、以下のとおりです。

| 用途 | Claude Code | Claude Managed Agents |
| --- | --- | --- |
| 単発作業・対話型開発 | 〇 | △ |
| 継続的な業務自動化 | △ | 〇 |
| インフラ管理・セキュリティ | ユーザー側で管理 | Anthropicが提供 |
| タスクの自律実行 | 人間が介在 | 完全自律 |

## 1. 導入：scheduled deployment とは

* エージェントに cron スケジュールを紐付け、**発火するたびに新しいセッションを開始してタスクを完了する**仕組み。
* ポイントは「**自前でスケジューラを構築・ホストする必要がない**」こと。
* 用途例：夜間データ同期 / 週次コンプライアンススキャン / 日次ダイジェスト。
* 採用事例で信頼性を補強（Actively AI は自作のスケジューリングインフラを置き換え、スタックを簡素化）。

## 2. 前提

* Console アカウントと API キー。
* `ant` CLI（Managed Agents CLI）。
* 全リクエストに `managed-agents-2026-04-01` の beta ヘッダーが必要（CLI / SDK は自動付与）。

## 3. 作る（agent → environment → deployment）

* deployment は既存の **agent と environment を ID 参照**する構造。
* だから順番は「agent 作成 → environment 作成 → deployment.yaml に両 ID を書く → create」。
* create のレスポンスに `status: active` と `upcoming_runs_at`（次回以降の発火予定）が返る。

## 4. 検証

* `run`（手動実行）でスケジュールを待たずに即セッション生成 → **本番投入前のテスト**に使える。
* `deployment-runs list` で各発火の成否を追跡。`--has-error` でエラーのみ抽出。
* deployment run は**セッションのライフサイクルとは独立した記録**である、という設計を強調すると技術記事として締まる。

## 5. cron / timezone / DST 挙動

* 最大粒度は**分レベル**。
* cron はリテラルな **wall-clock マッチング**。`America/New_York` の `0 20 * * *` は EST/EDT に関わらずローカル20時に発火。
* エッジケース：春の存在しない時刻（2AM 等）は発火しない／秋の重複時刻は2回発火。
* 取りこぼし・重複が許容できないなら、ローカル 1〜3AM を避けるか UTC を使う。
* `upcoming_runs_at` は UTC 表示だが、発火判定そのものは wall-clock ベース、という整理が正確。
* 負荷分散のため**最大10秒の jitter** が乗りうる（ピッタリには発火しない）。  
  （と言いつつも、恐らくその他の要因で、数分後に実行なんてことは良くある話だと思います。）

## 6. ライフサイクル管理

* **pause（可逆）**：以降のトリガーを抑制。ただし先行する run から走っているセッションは継続。pause 中でも手動 `run` は可能。
* **unpause**：次回予定回から再開。取りこぼしはバックフィルされない。
* **archive（不可逆 / terminal）**：スケジュール終了、以降変更不可。
* 自動挙動：agent がアーカイブ/削除されると deployment も自動アーカイブ。サブエージェントがアーカイブされると次回トリガーで失敗 run を記録し**自動 pause**（更新後に再開できるように）。

## 7. 注意点

* **課金**：これは Claude Platform（API）側の機能で、**Pro/Max のような月額サブスクとは別系統**。scheduled deployment 自体に追加料金は付いていないが、発火ごとにセッションが走る＝**そのトークン消費とサンドボックス実行が API 従量で課金される**。例：毎朝1回×30日 = セッション30回分の使用量。正確な単価は `claude.com/pricing#api` か Console の使用量画面で要確認。
* **ZDR / HIPAA 非対応**：Managed Agents は会話履歴・サンドボックス状態・出力をサーバー側に保持する stateful 設計のため、Zero Data Retention と HIPAA BAA の対象外。
* **public beta**：仕様は変わりうる。
* 上限：**1組織あたり最大 1,000 個**の scheduled deployment。

---

# 手順書（コピペ実行用）

> 前提：`ant` CLI インストール済み、`ANTHROPIC_API_KEY` 設定済み。  
> CLI は beta ヘッダーを自動付与する。

## Step 0. API キーを環境変数に

```
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Step 1. エージェントを作成して agent.id を控える

```
ant beta:agents create \
  --name "News Digest Agent" \
  --model '{id: claude-opus-4-8}' \
  --system "あなたは日次ニュース要約アシスタントです。簡潔で正確に。" \
  --tool '{type: agent_toolset_20260401}'
```

* `agent_toolset_20260401` で bash・ファイル操作・web search などのプリビルトツール一式が有効になる。

レスポンス例：  
![](https://static.zenn.studio/user-upload/aecd28cfaefa-20260614.png)

* 返ってきた `agent.id` を控える（以降 `$AGENT_ID` として使用）。

```
export AGENT_ID="agent_xxxxxxxxxxxx"
```

## Step 2. 環境を作成して environment.id を控える

```
ant beta:environments create \
  --name "cron-env" \
  --config '{type: cloud, networking: {type: unrestricted}}'
```

レスポンス例：  
![](https://static.zenn.studio/user-upload/fe600eb96679-20260614.png)

* 返ってきた `environment.id` を控える。

```
export ENVIRONMENT_ID="env_xxxxxxxxxxxx"
```

## Step 3. deployment.yaml を書く

今回はwsl上から直接VS Codeを呼び出し、そこで以下のyamlを作成します。

```
# deployment.yaml
name: Weekday morning digest
agent: $AGENT_ID
environment_id: $ENVIRONMENT_ID
initial_events:
  - type: user.message
    content:
      - type: text
        text: 今日のニュースダイジェストを作成して。
schedule:
  type: cron
  expression: "0 9 * * 1-5"   # 平日 朝9時
  timezone: Asia/Tokyo
```

* `expression` は標準 POSIX cron（`分 時 日 月 曜日`）。
* `timezone` は IANA タイムゾーン識別子。

## Step 4. scheduled deployment を作成

ファイルから流し込む形（公式画像の形）：

```
ant beta:deployments create < deployment.yaml
```

heredoc + ID 取得まで一気にやる形（公式ドキュメントの形）：

```
DEPLOYMENT_ID=$(ant beta:deployments create <<YAML | jq -er '.id'
name: Weekday morning digest
agent: $AGENT_ID
environment_id: $ENVIRONMENT_ID
initial_events:
  - type: user.message
    content:
      - type: text
        text: 今日のニュースダイジェストを作成して。
schedule:
  type: cron
  expression: "0 9 * * 1-5"
  timezone: Asia/Tokyo
YAML
)
```

レスポンス例：  
![](https://static.zenn.studio/user-upload/c4ff1545a6fb-20260614.png)

```
export DEPLOYMENT_ID="depl_xxxxxxxxxxxx"
```

## Step 5. 手動実行でテスト（スケジュールを待たない）

```
ant beta:deployments run --deployment-id "$DEPLOYMENT_ID"
```

* 即セッションを生成し、`trigger_context.type: "manual"` の deployment run を書く。
* 本番のスケジュールに乗せる前の動作確認に。

レスポンス例：  
![](https://static.zenn.studio/user-upload/ff8f523e8f28-20260614.png)

### 出力確認

Claude Platformのコンソールから確認できます！  
![](https://static.zenn.studio/user-upload/75d4e9a29ab9-20260615.png)

## Step 6. 実行履歴を確認

```
# 全 run
ant beta:deployment-runs list --deployment-id "$DEPLOYMENT_ID"

# エラーのみ
ant beta:deployment-runs list --deployment-id "$DEPLOYMENT_ID" --has-error
```

レスポンス例：  
![](https://static.zenn.studio/user-upload/dafda7e68f5e-20260614.png)

* 失敗 run には `error.type`（例：`environment_archived_error` / `agent_archived_error` / `session_rate_limited_error`）が入る。

## Step 7. ライフサイクル操作

```
# 一時停止（可逆）：以降のトリガーを抑制。走行中セッションは継続。pause中も手動runは可。
ant beta:deployments pause --deployment-id "$DEPLOYMENT_ID"

# 再開：次回予定回から。取りこぼしのバックフィルなし。
ant beta:deployments unpause --deployment-id "$DEPLOYMENT_ID"

# アーカイブ（不可逆 / terminal）：スケジュール終了、以降変更不可。
ant beta:deployments archive --deployment-id "$DEPLOYMENT_ID"
```

## Step 8. 実施結果

実施時間も、指定したAM9:00近くに実行されていることが分かりますね！  
![](https://static.zenn.studio/user-upload/58246a4a6f4f-20260615.png)

---

## Step 9. お片付け

```
ant beta:deployments archive --deployment-id "$DEPLOYMENT_ID"
```

レスポンス例：  
![](https://static.zenn.studio/user-upload/c15e63062f59-20260615.png)

## 余談

Claude には定期実行の手段が段階的に用意されています！  
Claude Code 内で動く /loop(セッションを開いている間だけ)、PCを閉じても Anthropic のクラウドで動く /schedule(Cloud Routine)、そして本記事で扱う Managed Agents の scheduled deployment、計3段階となっています。  
手元の作業補助から本番運用まで、用途に応じて選べるのが特徴ですね！  
各手段の細かい違いは [【Claude loop 完全ガイド】税理士・経理・人事など非エンジニアが"定期確認"をノーコードで自動化する方法](https://x.com/claudecode_lab/status/2066404471891206320?s=53&t=qZ8apxpZksdCAbF_qrBcyg) の最後の方にまとまっておりますので、そちらをご確認ください！

# 参照（一次ソース）
