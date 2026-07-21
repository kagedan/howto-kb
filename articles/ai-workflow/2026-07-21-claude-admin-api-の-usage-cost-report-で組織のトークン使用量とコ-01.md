---
id: "2026-07-21-claude-admin-api-の-usage-cost-report-で組織のトークン使用量とコ-01"
title: "Claude Admin API の Usage & Cost Report で組織のトークン使用量とコストを自動監視する実装 — Admin キー・集計遅延・粒度上限の3つのハマりどころ【2026】"
url: "https://qiita.com/yureki_lab/items/710bf1797f3f7355c88d"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-rss"
query: ""
---

## はじめに / 対象と前提

Claude API を使ったプロダクトや自律稼働エージェントを運用していて、「今月どれだけAPIコストがかかっているか」「どのAPIキーが浪費しているか」をコードから追跡したい人向けの記事。

前提環境:

- Python 3.13
- Claude Console で組織(Organization)の管理者権限を持っていること
- Anthropic API `anthropic-version: 2023-06-01`

通常の Claude API キー(`sk-ant-api03-...`)を使った実装は前提としない。今回使うのは別枠の **Admin API** で、認証キーの種類からして違う。

## TL;DR

- `/v1/organizations/usage_report/messages` でトークン使用量、`/v1/organizations/cost_report` でUSDコストを取得できる
- どちらも通常のAPIキーではなく **Admin API キー**(`sk-ant-admin01-...`)が必須
- 集計データはリクエスト完了から平均5分程度で反映される(それ以上遅れることもある)
- `bucket_width` の粒度ごとに取得できるバケット数の上限が違う。長期間を細かい粒度で一気に取ろうとすると詰まる
- 数十行のPythonで「昨日のコストがしきい値を超えたら知らせる」バッチが書ける

## 手順 / 動かし方

### 1. Admin API キーを発行する

Console の **Settings → Admin API Keys** から発行する。通常のAPIキーとは別物で、組織全体のUsage/Cost取得やワークスペース管理などの権限を持つ。フォーマットは `sk-ant-admin01-` から始まる。

個人アカウントでは使えず、組織(Organization)のセットアップが必須。

### 2. 直近7日間の日次使用量を取得する

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-07-14T00:00:00Z&\
ending_at=2026-07-21T00:00:00Z&\
group_by[]=model&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

`group_by[]` には `model` / `workspace_id` / `api_key_id` / `service_tier` / `context_window` / `inference_geo` などを指定できる。モデル別・ワークスペース別に切り分けて見たいときに使う。

### 3. Python で「前日コストがしきい値超えたら警告」するスクリプト

```python
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

ADMIN_KEY = os.environ["ANTHROPIC_ADMIN_KEY"]
THRESHOLD_USD = 5.00

now = datetime.now(timezone.utc)
yesterday = now - timedelta(days=1)

params = (
    f"starting_at={yesterday.strftime('%Y-%m-%dT00:00:00Z')}"
    f"&ending_at={now.strftime('%Y-%m-%dT00:00:00Z')}"
    f"&group_by[]=description"
)
url = f"https://api.anthropic.com/v1/organizations/cost_report?{params}"

req = urllib.request.Request(
    url,
    headers={
        "anthropic-version": "2023-06-01",
        "x-api-key": ADMIN_KEY,
    },
)

with urllib.request.urlopen(req) as res:
    data = json.loads(res.read())

total_cents = 0
for bucket in data["data"]:
    for result in bucket["results"]:
        # amount は最小通貨単位(セント)の文字列で返ってくる
        total_cents += int(result["amount"])

total_usd = total_cents / 100
if total_usd > THRESHOLD_USD:
    print(f"[ALERT] yesterday cost = ${total_usd:.2f} (threshold ${THRESHOLD_USD})")
else:
    print(f"[OK] yesterday cost = ${total_usd:.2f}")
```

cronやlaunchdで毎朝これを回すだけで、「一晩で気づいたら想定外に課金されていた」を検知できる。24時間稼働させているエージェントほど、この手の監視は後回しにしがちなので早めに仕込んでおくと安心。

## ハマりどころ

### 1. 通常のAPIキーだと 403 になる

Admin APIは `sk-ant-admin01-` のキーでないと `permission_error` で弾かれる。手元の `.env` に入っているのが普段の推論用キーだと気づかず、しばらく「なぜ403になるんだ」とハマった。Bedrock / Vertex 経由の利用では、このAPI自体がまだ提供されていない点も注意。

### 2. 集計反映に遅延がある

「たった今叩いたリクエストが usage report にまだ出てこない」と焦ったが、公式には平均5分程度のラグがあるとされている。リアルタイム監視には向かないので、日次バッチで「前日分」を確実に集計する設計にした方が数字がブレない。ポーリング頻度も1分1回程度が推奨されている。

### 3. `bucket_width` ごとの取得上限に当たる

粒度によって一度に取れるバケット数の上限が異なる。

| 粒度 | デフォルト上限 | 最大上限 |
|---|---|---|
| `1m` | 60 | 1,440 |
| `1h` | 24 | 168 |
| `1d` | 7 | 31 |

たとえば1ヶ月分を `1m` 粒度で一括取得しようとすると上限に当たり、`has_more: true` を見落としてデータが歯抜けになる。`next_page` を使ったページネーションを必ず実装すること。

## 背景・補足

Usage(トークン数)とCost(USD)がなぜ別エンドポイントかというと、粒度と目的が違うため。Cost側は日次(`1d`)のみでUSD建ての金額を返し、`description` でグループ化すると `model` や `inference_geo` がパースされた形で返ってくる。逆にCode Execution のコストはCostエンドポイントの `description` に "Code Execution Usage" として出るが、Usageエンドポイントには出てこない。Priority Tierの課金体系も別枠でCostエンドポイントには含まれず、Usage側で `service_tier=priority` を見る必要がある。地味に混同しやすいので、どちらのエンドポイントで何が拾えるかは最初に整理しておくと後で楽になる。

## まとめ

- Admin API の Usage/Cost Report は、通常のAPIキーとは別の Admin API キーが必要
- 集計には平均5分の遅延があるため、日次バッチ向きの設計にする
- `bucket_width` の上限を把握し、`next_page` によるページネーションを必ず実装する
- Code Execution・Priority Tierのコストはエンドポイントによって出る/出ないが分かれるので要注意
- 自律稼働させているエージェントほど「気づいたら課金が膨らんでいた」を防ぐ仕組みを早めに仕込んでおくと安心
