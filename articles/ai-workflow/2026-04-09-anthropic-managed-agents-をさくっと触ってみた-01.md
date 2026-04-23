---
id: "2026-04-09-anthropic-managed-agents-をさくっと触ってみた-01"
title: "Anthropic Managed Agents をさくっと触ってみた"
url: "https://zenn.dev/sprix_it/articles/3211f5068cec29"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## きっかけ

Anthropic 公式エンジニアリングブログに [**Scaling Managed Agents: Decoupling the brain from the hands**](https://www.anthropic.com/engineering/managed-agents) という記事が出ているのを見て興味を持ちました。「頭脳（モデル）」「手（サンドボックス）」「記録（セッションログ）」を分離する、というアーキテクチャの説明が面白かったので、本当にそういう作りになっているか自分の手元で叩いて確かめてみよう、というのがこの記事の出発点です。

## これは何の話？

Anthropic が 2026 年 4 月に **Managed Agents**（`/v1/agents`, `/v1/sessions`）というベータ機能を出しました。

ざっくり言うと、**「AI エージェントを動かすためのコンテナと実行ループを Anthropic 側で持ってくれるサービス」** です。

これまで「Claude にツールを使わせる長時間タスク」を作るには、自分のサーバ上で次のようなものを全部用意する必要がありました。

* ツール実行用の bash / ファイル操作環境（コンテナ）
* ツール呼び出しと結果送信を回すループ
* 途中で落ちたときの再開・ログ管理
* セッション状態の永続化

Managed Agents はこの土台一式を Anthropic 側に肩代わりしてもらい、こちら側は「エージェント定義（モデル、systemプロンプト、使えるツール）」と「ユーザーメッセージ」を渡すだけにする、というものです。

立ち位置のイメージ:

| 選択肢 | 実行場所 | あなたが書くもの |
| --- | --- | --- |
| Messages API + tool use | 自前 | プロンプト + ツール定義 + ループ + コンテナ管理 |
| Claude Agent SDK（ローカル版） | 自前 | エージェント定義だけ（ループ不要・Claude Code を library として呼ぶ形） |
| **Managed Agents（今回）** | **Anthropic クラウド** | **エージェント定義だけ** |
| Claude Code | Anthropic クラウド | （コードを書かない／使うだけ） |

`pip install claude-agent-sdk` で導入できる **Claude Agent SDK** は同時期に出た「Claude Code を自分のプログラムから呼び出せるライブラリ版」です。実行環境は自前（自分のサーバや CI）ですが、tool use ループは SDK が回してくれます。Managed Agents との違いは「コンテナを誰が管理するか」で、ローカル版が自分のインフラで完結するのに対し、Managed Agents はサンドボックスごと Anthropic 側で持つ点が決定的に異なります。

## メリット

* **コンテナ管理がいらない**: bash 実行環境・ファイルマウント・タイムアウト処理を自前で書かなくていい
* **観測機能が組み込み**: 応答開始時間・モデル使用トークン・ツール呼び出しがすべてイベントログとして取れる
* **エージェント定義がバージョン管理される**: system プロンプトを更新しても動いている処理が壊れない、リグレッションしたら旧バージョンに戻せる
* **長時間タスクの再開がフレームワーク前提**: 接続が切れても履歴 API でロスレスに復元できる
* **公式 SDK で書ける**: Python / TypeScript / Go など主要言語にバインディングあり

## デメリット・注意点

* **パブリックベータ**: コア機能はベータヘッダー `managed-agents-2026-04-01` を付ければ全 API アカウントで使える（申し込み不要）が、ヘッダー名が日付付きであることからもわかる通り仕様変更の可能性はある
* **一部機能は research preview で申し込み制**: 「outcomes（出力評価）」「multiagent（マルチエージェント協調）」「memory（永続記憶）」の 3 つは [request access](https://claude.com/form/claude-managed-agents) からアクセスを申請する必要がある
* **ランタイム時間で課金**: モデル使用料に加えて **0.08 USD/時間** のサンドボックス稼働料金が乗る。ただし課金対象は **active runtime のみ**で、ユーザー入力やツール結果待ちのアイドル時間・rescheduling・terminated は含まれない（ミリ秒単位で計測）
* **ツール課金が別途乗ることがある**: 特に Web 検索を使うエージェントは標準の Web Search 料金 **10 USD / 1,000 検索** が追加でかかる。検索ヘビーなユースケースでは無視できないコストになる
* **クラウド版 Managed Agents だけ第三者プロバイダ非対応**: Managed Agents は Bedrock / Vertex AI / Azure 経由では提供されず、Anthropic の API を直接叩く必要がある（同時期に出た Claude Agent SDK ローカル版は環境変数で 3 プロバイダすべてに切り替え可能なので、ここを混同しないこと）
* **API の作法に独特な落とし穴がいくつかある**: エージェントは必ず先に作成して ID を再利用する、stream を開いてからメッセージを送る、など。知らずに書くと地雷を踏む
* **Claude Code ほどのお膳立てはない**: 結局はエージェント設計（プロンプト、ツール構成、終了判定）を自前で行う必要がある

## サクッと検証してみた

公式ドキュメントの主張を裏取りするために、最小コードを 4 本書きました（`01_setup.py` は環境とエージェントを 1 度だけ作るセットアップ専用なので、観点表からは除外しています）。

| # | 検証項目 | 確認したいこと |
| --- | --- | --- |
| 02 | 最小 Hello World | 1 ターン送って応答開始時間（TTFT）を計測 |
| 03 | 接続切断からの再開 | 強制切断 → 履歴 fetch → 再開がロスレスにできるか |
| 04 | サンドボックスの中身 | bash で OS / リソース / 外部到達性を観察 |
| 05 | 認証情報を外に出さないツール | カスタムツールで credentials をホスト側に残せるか |

検証結果サマリ:

| 確認項目 | 結果 |
| --- | --- |
| 応答開始までの時間（TTFT） | クライアント側 **5,636 ms** / そのうちサーバ側モデル推論は **2,289 ms**。残りの ~3.3 秒はセッション起動・コンテナ準備込みのオーバーヘッド |
| 1 リクエストの使用量 | input 3 / output 5 / cache\_creation 5,194 / cache\_read 0。**input が極端に少ないのは Prompt Caching の集計仕様**で、`input_tokens` は「キャッシュにヒットも書き込みもしなかった残り」だけを指す。Managed Agents の harness が注入する内部 system プロンプト + ツール定義一式（5,194 トークン分）が初回リクエストでキャッシュに書き込まれた格好 |
| サンドボックスの環境 | **gVisor (`runsc`) 上の Ubuntu 24.04.4 LTS**、16 vCPU、21 GiB RAM、30 GB ディスク。Python 3 / Node 22 / git プリインストール、HTTPS egress 有効 |
| 接続切断からの再開 | `events.list()` で停止中に発生した 2 件（`agent.thinking` / `agent.tool_use`）を復元 → 再ストリームで残り 5 件取得 → 計 10 イベントを欠落なく処理できた |
| カスタムツール round-trip | `agent.custom_tool_use` を host 側で受信し、ホストの関数で結果を生成して `user.custom_tool_result` で返却 → エージェントが結果を踏まえた最終応答を生成。**サンドボックスには credentials を一切渡していない** |

> 💡 **公式ドキュメント記載との差分**: cloud-containers ドキュメントには「Memory: Up to 8 GB / Disk space: Up to 10 GB」とありますが、今回の実測では 21 GiB / 30 GB が割り当てられていました。"up to" 表記が現状の上限ではなく **保証下限** に近い表記である可能性があります。本番設計では公式値で見積もる方が安全です。

### 検証コード（折りたたみ）

興味のある人向けに、実際に書いたスクリプトを置いておきます。`ANTHROPIC_API_KEY` を設定して `01_setup.py` を 1 回実行 → 以降は順番に動かす想定です。

requirements.txt

```
anthropic>=0.50.0
python-dotenv>=1.0.0
```

01\_setup.py — Environment と Agent を作って ID を保存

```
"""
セットアップスクリプト（一度だけ実行）

Environment と Agent を作成して、ID を .env に追記する。
ベータヘッダー `managed-agents-2026-04-01` は SDK が自動で付与する。
"""
from __future__ import annotations

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

ENV_FILE = Path(__file__).parent / ".env"

def append_env(key: str, value: str) -> None:
    lines: list[str] = []
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line and not line.startswith(f"{key}="):
                lines.append(line)
    lines.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(lines) + "\n")

def main() -> None:
    client = anthropic.Anthropic()

    env = client.beta.environments.create(
        name="first-look-env",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    append_env("MANAGED_AGENTS_ENV_ID", env.id)

    # ⚠️ 重要: model/system/tools は session ではなく agent に置く
    # 一度作ったら ID を保存して再利用する
    agent = client.beta.agents.create(
        name="first-look-agent",
        model="claude-opus-4-6",
        system=(
            "You are a verification agent for testing Managed Agents. "
            "Be concise. When asked to inspect the environment, use bash."
        ),
        tools=[
            {
                "type": "agent_toolset_20260401",
                "default_config": {"enabled": True},
            },
        ],
    )
    append_env("MANAGED_AGENTS_AGENT_ID", agent.id)
    append_env("MANAGED_AGENTS_AGENT_VERSION", str(agent.version))

if __name__ == "__main__":
    main()
```

02\_hello\_ttft.py — TTFT とサーバ側推論時間の計測

```
"""
Hello World + TTFT 計測

  - クライアント側 TTFT: send 直後 → 最初の `agent.message` テキストデルタまで
  - サーバ側モデル推論時間: span.model_request_start → span.model_request_end
  - トークン使用量: span.model_request_end.model_usage

⚠️ stream-first ordering: 必ず stream を先に開いてから send する
"""
from __future__ import annotations

import os
import time
from datetime import datetime

import anthropic
from dotenv import load_dotenv

load_dotenv()

AGENT_ID = os.environ["MANAGED_AGENTS_AGENT_ID"]
AGENT_VERSION = int(os.environ["MANAGED_AGENTS_AGENT_VERSION"])
ENV_ID = os.environ["MANAGED_AGENTS_ENV_ID"]

def main() -> None:
    client = anthropic.Anthropic()

    session = client.beta.sessions.create(
        agent={"type": "agent", "id": AGENT_ID, "version": AGENT_VERSION},
        environment_id=ENV_ID,
        title="ttft-probe",
    )

    user_text = "Reply with exactly: 'pong'. No preamble."

    t_send: float | None = None
    t_first_text_local: float | None = None
    model_request_start_dt: datetime | None = None
    model_request_end_dt: datetime | None = None
    model_usage = None
    final_text_parts: list[str] = []

    # ⚠️ 実 SDK のメソッドは sessions.events.stream(...) （ドキュメントに sessions.stream と書いてある箇所があるが間違い）
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        t_send = time.monotonic()
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": user_text}],
                }
            ],
        )

        for event in stream:
            etype = getattr(event, "type", None)

            if etype == "span.model_request_start":
                model_request_start_dt = event.processed_at  # datetime.datetime
            elif etype == "span.model_request_end":
                model_request_end_dt = event.processed_at
                model_usage = getattr(event, "model_usage", None)

            elif etype == "agent.message":
                if t_first_text_local is None:
                    t_first_text_local = time.monotonic()
                for block in event.content:
                    if block.type == "text":
                        final_text_parts.append(block.text)

            elif etype == "session.status_idle":
                stop_reason = getattr(event, "stop_reason", None)
                if stop_reason and getattr(stop_reason, "type", None) == "requires_action":
                    continue  # tool 待ちなのでループ続行
                break
            elif etype == "session.status_terminated":
                break

    print(f"agent text: {''.join(final_text_parts).strip()!r}")
    if t_send is not None and t_first_text_local is not None:
        print(f"client TTFT: {(t_first_text_local - t_send) * 1000:.0f} ms")
    if model_request_start_dt and model_request_end_dt:
        infer_ms = (model_request_end_dt - model_request_start_dt).total_seconds() * 1000
        print(f"server inference: {infer_ms:.0f} ms")
    if model_usage:
        print(f"usage: {model_usage.model_dump()}")

if __name__ == "__main__":
    main()
```

03\_resume.py — SSE 切断 → 履歴 fetch → 再開

```
"""
セッション再開デモ（lossless reconnect パターン）

  1. セッション開始 → メッセージ送信 → 数イベント受信したら意図的に stream を閉じる
  2. その間にもエージェントは動き続けている（処理は止まらない）
  3. events.list() で履歴を取得し、ID 集合を埋める
  4. もう一度 stream を開いて、欠落イベントが履歴経由で復元できることを確認
"""
from __future__ import annotations

import os
import time

import anthropic
from dotenv import load_dotenv

load_dotenv()

AGENT_ID = os.environ["MANAGED_AGENTS_AGENT_ID"]
AGENT_VERSION = int(os.environ["MANAGED_AGENTS_AGENT_VERSION"])
ENV_ID = os.environ["MANAGED_AGENTS_ENV_ID"]

def main() -> None:
    client = anthropic.Anthropic()

    session = client.beta.sessions.create(
        agent={"type": "agent", "id": AGENT_ID, "version": AGENT_VERSION},
        environment_id=ENV_ID,
        title="resume-probe",
    )

    seen_event_ids: set[str] = set()

    # ステップ1: kickoff を送って数イベントだけ受け取って強制切断
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Run `uname -a && ls -la /workspace && echo done`. "
                                "Then summarize what you saw in 2 lines."
                            ),
                        }
                    ],
                }
            ],
        )
        received = 0
        for event in stream:
            seen_event_ids.add(event.id)
            received += 1
            if received >= 3:
                break  # 接続切断シミュレーション

    time.sleep(2)  # サーバ側は処理を続けている

    # ステップ2: 履歴 fetch で欠落分を取り戻す
    history = client.beta.sessions.events.list(session_id=session.id)
    for ev in history.data:
        if ev.id not in seen_event_ids:
            seen_event_ids.add(ev.id)

    # ステップ3: 改めて stream を開いて完了まで読む（dedupe 込み）
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        for event in stream:
            if event.id not in seen_event_ids:
                seen_event_ids.add(event.id)

            if event.type == "session.status_terminated":
                break
            if event.type == "session.status_idle":
                stop_reason = getattr(event, "stop_reason", None)
                if stop_reason and getattr(stop_reason, "type", None) == "requires_action":
                    continue
                break

    print(f"取り扱った計イベント数: {len(seen_event_ids)}")

if __name__ == "__main__":
    main()
```

04\_sandbox\_probe.py — bash でコンテナの中身を観察

```
"""
サンドボックス観察スクリプト

エージェントに bash で OS / CPU / ネットワーク到達性を集めさせる。
bash 実行は agent.tool_use イベントとして記録される。
"""
from __future__ import annotations

import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

AGENT_ID = os.environ["MANAGED_AGENTS_AGENT_ID"]
AGENT_VERSION = int(os.environ["MANAGED_AGENTS_AGENT_VERSION"])
ENV_ID = os.environ["MANAGED_AGENTS_ENV_ID"]

PROBE_PROMPT = """\
Run these commands one by one and report the output verbatim:
1. `uname -a`
2. `cat /etc/os-release | head -5`
3. `nproc && free -h | head -2`
4. `df -h / | tail -1`
5. `which python3 node git || true`
6. `curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com 2>&1 || echo "no curl"`

After all commands finish, give a 3-line summary in JSON:
{"os": "...", "cpu_mem": "...", "egress": "..."}
"""

def main() -> None:
    client = anthropic.Anthropic()

    session = client.beta.sessions.create(
        agent={"type": "agent", "id": AGENT_ID, "version": AGENT_VERSION},
        environment_id=ENV_ID,
        title="sandbox-probe",
    )

    tool_calls: list[dict] = []
    text_chunks: list[str] = []

    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": PROBE_PROMPT}]}],
        )

        for event in stream:
            if event.type == "agent.tool_use":
                tool_calls.append(
                    {"name": event.name, "input": getattr(event, "input", None)}
                )
            elif event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        text_chunks.append(block.text)
            elif event.type == "session.status_idle":
                stop_reason = getattr(event, "stop_reason", None)
                if stop_reason and getattr(stop_reason, "type", None) == "requires_action":
                    continue
                break
            elif event.type == "session.status_terminated":
                break

    for i, call in enumerate(tool_calls, 1):
        print(f"{i}. {call['name']}: {json.dumps(call['input'], ensure_ascii=False)[:140]}")
    print("\n=== summary ===")
    print("".join(text_chunks).strip())

if __name__ == "__main__":
    main()
```

05\_custom\_tool.py — credentials をホスト側に残すパターン

```
"""
カスタムツール round-trip デモ

サンドボックスに credentials を渡したくない場合、custom tool として宣言しておけば
「呼び出しはエージェント、実行はホスト側」の形にできる。
"""
from __future__ import annotations

import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

ENV_ID = os.environ["MANAGED_AGENTS_ENV_ID"]

def fake_get_weather(location: str) -> str:
    """ホスト側で実行されるツール。実際は外部 API を叩いてもよい。
    credentials はここに置けばサンドボックスに漏れない"""
    return json.dumps({"location": location, "temp_c": 18, "condition": "sunny"})

def main() -> None:
    client = anthropic.Anthropic()

    agent = client.beta.agents.create(
        name="custom-tool-probe",
        model="claude-opus-4-6",
        system="When asked about weather, call get_weather. Do not invent values.",
        tools=[
            {
                "type": "custom",
                "name": "get_weather",
                "description": "Fetch current weather for a given location.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name, e.g. Tokyo"}
                    },
                    "required": ["location"],
                },
            }
        ],
    )

    session = client.beta.sessions.create(
        agent={"type": "agent", "id": agent.id, "version": agent.version},
        environment_id=ENV_ID,
        title="custom-tool-probe",
    )

    final_text: list[str] = []

    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": "What's the weather in Tokyo?"}],
                }
            ],
        )

        for event in stream:
            if event.type == "agent.custom_tool_use":
                tool_use_id = event.id  # ⚠️ sevt_... 形式。toolu_ ではない
                # ⚠️ event.name (NOT event.tool_name)
                if event.name == "get_weather":
                    result = fake_get_weather(**event.input)
                else:
                    result = f"Unknown tool: {event.name}"

                client.beta.sessions.events.send(
                    session_id=session.id,
                    events=[
                        {
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": tool_use_id,
                            "content": [{"type": "text", "text": result}],
                        }
                    ],
                )

            elif event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        final_text.append(block.text)

            elif event.type == "session.status_idle":
                stop_reason = getattr(event, "stop_reason", None)
                if stop_reason and getattr(stop_reason, "type", None) == "requires_action":
                    continue
                break
            elif event.type == "session.status_terminated":
                break

    print("".join(final_text).strip())

if __name__ == "__main__":
    main()
```

## どんな人に向いてる？

* **向いてる**: 自分のサービスに「ファイルを編集してコミットまでするエージェント」「データを集計してレポートを書くエージェント」のような長時間タスクを組み込みたい人
* **向いてない**: 単発のチャット応答や分類タスクを作りたい人（普通の Messages API で十分）
* **判断保留**: 既に自前で tool use ループを運用している人。コスト試算と乗り換えコストの見極めが必要

## 所感

実際に最小コードを書いて 5 本走らせてみての印象は「Anthropic が **エージェントの土台を自分のところで持つ覚悟を決めた**」という感じです。Messages API は API 設計上「リクエスト / レスポンス」のスタイルから抜け出せていなかったのに対し、Managed Agents は最初から「セッション + イベントストリーム」モデルになっており、長時間タスクを真面目に組む前提の API になっています。

アイドル時間が課金対象外になったのも実用上大きく、「ユーザーの次の入力を待っている間ずっと従量課金」というよくあるサンドボックスサービスの落とし穴を避けてあります。これは Claude Code 系の対話的ユースケースを意識した設計だと思います。

サンドボックスの中身が **gVisor 上の Ubuntu 24.04 + 16 vCPU + 21 GiB RAM** だったのは正直驚きでした。「そこそこの開発機相当のリソースを 1 セッションあたりで貰える」と思っていいレベルで、ファイル編集・テスト実行・ビルドのような重めの作業も気にせず投げられそうです。

切断 → 再接続のロスレス再開も、`events.list()` + dedupe の手動パターンが想定通りに動きました。SSE がリプレイなしという制約を **クライアント実装の責務として明示** しているのは、隠蔽してしまうより誠実な API 設計だと思います。

一方で「常時稼働する小さなエージェントを大量に立てる」用途には向かず、当面は **「有意味な単発タスクを腰を据えて回す」** ユースケース寄りに見えます。Claude Code を自社サービスに埋め込みたいけど **コンテナを自前で管理したくない**、というニーズへの答えとして読むと自然です。

### ハマりどころ実例（執筆時点の SDK 0.92.0）

* 公式ドキュメント側で `client.beta.sessions.stream(...)` と書かれている箇所があるが、実 SDK のメソッドは `client.beta.sessions.events.stream(...)`。書き写したコードがそのままだと `AttributeError`
* `agent.custom_tool_use` イベントの「呼ばれたツール名」フィールドは `event.tool_name` ではなく `event.name`
* `processed_at` は ISO 文字列ではなく `datetime.datetime` 型。直接引き算してよい

ベータ仕様の動きが速いので、「ドキュメントと実 SDK のどちらを正にするか」を意識して書く必要があります（**実 SDK が正**）。

## 参考リンク
