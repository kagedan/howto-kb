---
id: "2026-04-13-openai-gpt-realtime入門-sipmcp対応の本番音声エージェントをpythonで実-01"
title: "OpenAI gpt-realtime入門 — SIP・MCP対応の本番音声エージェントをPythonで実装する"
url: "https://zenn.dev/kai_kou/articles/191-gpt-realtime-sip-mcp-production-guide"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## はじめに

OpenAIが2026年4月、[Realtime APIをGeneral Availability（GA）に昇格させ、新モデル `gpt-realtime` を正式リリースしました](https://openai.com/index/introducing-gpt-realtime/)。

従来のプレビュー版と比べて大きな変化点が3つあります。

1. **SIP電話対応** — Twilioなどを経由して公衆電話網に直接接続できる
2. **リモートMCPサーバー対応** — ツールをURL一本で接続できる
3. **非同期関数呼び出し** — 長時間処理中も会話を途切れなく続けられる

### この記事で学べること

* `gpt-realtime` の性能改善とモデル仕様
* 新しい声「Cedar」「Marin」の設定方法
* SIP電話連携の仕組みと構成
* リモートMCPサーバーとの統合
* 非同期関数呼び出しの実装パターン
* プレビュー版からGAへの移行チェックリスト

### 対象読者

* OpenAI Realtime APIをすでに使っている開発者（移行対応）
* 音声エージェント・コールボット開発を検討しているエンジニア
* MCPサーバーを音声インターフェイスと統合したい方

### 前提環境

* Python 3.9+
* OpenAI APIキー（Realtime API アクセス権限付き）
* `openai` SDK v2.x（`pip install -U openai`）

---

## TL;DR

* `gpt-realtime` はプレビュー版から命令追従性が **48%向上**、ツール呼び出し精度が **34%向上**
* 新声 `cedar` / `marin` が最高音質 — 新規構築はこちらを推奨
* `session.update` にMCPサーバーURLを渡すだけでツール自動接続が完了
* SIPは Twilio + Realtime API の組み合わせでコールセンター向け音声エージェントを構築可能
* プレビュー版廃止は **2026-04-30** — イベント名変更に注意

---

## gpt-realtime の性能改善

[公式発表](https://openai.com/index/introducing-gpt-realtime/)によると、`gpt-realtime` は以下のベンチマークで大幅な改善を達成しています。

| ベンチマーク | 旧プレビュー版 | gpt-realtime | 改善率 |
| --- | --- | --- | --- |
| MultiChallenge audio（命令追従） | 20.6% | **30.5%** | +48% |
| ComplexFuncBench audio（ツール呼び出し） | 49.7% | **66.5%** | +34% |

MultiChallenge audioはGemini 3.1 Flash Live（thinking有効時36.1%）と同水準で、現時点で最高水準の音声AIモデルのひとつです。

### トークン仕様

[公式ドキュメント](https://developers.openai.com/api/docs/models/gpt-realtime)に記載の仕様は以下の通りです。

| 項目 | 仕様 |
| --- | --- |
| 最大入力トークン | 32,000 |
| 最大出力トークン | 4,096 |
| 音声フォーマット | PCM（Base64エンコード、20〜50msフレーム） |
| サンプルレート | 24kHz固定 |

---

## 新しい声: Cedar と Marin

GA版では2つの新しい声が追加されました。OpenAIは新規プロジェクトには `cedar` または `marin` を推奨しています。

| 声名 | 特徴 | 推奨用途 |
| --- | --- | --- |
| `cedar` | 落ち着いた中性的なトーン | ビジネス・カスタマーサポート |
| `marin` | 明るく自然なリズム | 消費者向けアプリ・アシスタント |
| `alloy`, `ash`, `coral` など | 旧来の声（引き続き利用可） | 既存アプリの継続利用 |

```
from openai import OpenAI

client = OpenAI()

# WebSocketセッション作成時に声を指定
session_config = {
    "model": "gpt-realtime-1.5",
    "voice": "marin",  # または "cedar"
    "modalities": ["audio", "text"],
}
```

---

## 機能1: リモートMCPサーバー対応

最もインパクトの大きな新機能のひとつが[リモートMCPサーバー対応](https://developers.openai.com/api/docs/guides/realtime-mcp)です。

従来は外部ツールとの連携に手動でのwireupが必要でしたが、GA版ではMCPサーバーのURLを渡すだけでツールが自動接続されます。

### 基本的な統合

```
import json
import asyncio
import websockets

async def create_mcp_session():
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-1.5"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    async with websockets.connect(url, additional_headers=headers) as ws:
        # セッション設定でMCPサーバーを登録
        session_update = {
            "type": "session.update",
            "session": {
                "voice": "marin",
                "modalities": ["audio", "text"],
                "tools": [
                    {
                        "type": "mcp",
                        "server_url": "https://mcp.example.com/api",
                        "server_label": "my-tools",
                        # セキュリティ: 許可するツールを限定
                        "allowed_tools": ["search", "get_weather"],
                        "headers": {
                            "Authorization": "Bearer MCP_TOKEN"
                        }
                    }
                ],
                "tool_choice": "auto",
            }
        }
        await ws.send(json.dumps(session_update))

        # 以降はイベントループで音声入出力を処理
        response = await ws.recv()
        print(json.loads(response))
```

### セキュリティの考慮点

MCPサーバー連携では以下の点に注意します。

* **`allowed_tools` で最小権限原則を徹底**: サーバーが提供する全ツールを自動承認させない
* **書き込み系操作は `require_approval`**: データ変更・送信などは人間承認フローを経由させる
* MCPサーバーは会話コンテキスト全体を自動受信しないため、トークン漏洩リスクは低め

---

## 機能2: SIP電話対応

[Realtime API with SIP](https://platform.openai.com/docs/guides/realtime-sip)を使うと、公衆電話網・PBXシステム・デスク電話と直接接続できます。

### アーキテクチャ概要

```
電話ユーザー
    ↓ PSTN/SIP
Twilio（SIPトランキング）
    ↓ WebSocket
OpenAI Realtime API（gpt-realtime）
    ↓ MCPサーバー / 外部API
CRMシステム・予約DB
```

### Twilio + Realtime API の構成例

Twilio Media Streamsを使って音声をWebSocketでRealtimeにブリッジします。

```
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
import threading
import websocket
import json
import base64

app = Flask(__name__)

OPENAI_API_KEY = "sk-..."
OPENAI_WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-realtime-1.5"

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    """Twilioからの着信を処理してメディアストリームへ転送"""
    response = VoiceResponse()
    connect = Connect()
    # ngrokなどで公開したWebSocketエンドポイントへ
    stream = Stream(url="wss://your-server.example.com/media-stream")
    connect.append(stream)
    response.append(connect)
    return Response(str(response), mimetype="text/xml")

def openai_ws_handler(twilio_ws):
    """TwilioのWebSocketとOpenAI Realtime APIをブリッジ"""
    openai_ws = websocket.create_connection(
        OPENAI_WS_URL,
        header=[f"Authorization: Bearer {OPENAI_API_KEY}", "OpenAI-Beta: realtime=v1"]
    )

    # セッション設定
    openai_ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "voice": "cedar",
            "instructions": "あなたは予約受付アシスタントです。丁寧な日本語で対応してください。",
            "input_audio_format": "g711_ulaw",  # Twilioの電話音声形式
            "output_audio_format": "g711_ulaw",
        }
    }))
    # 以降は双方向にオーディオパケットをリレー
```

---

## 機能3: 非同期関数呼び出し

従来の関数呼び出しでは、外部API呼び出しなどで処理が長引くと会話が止まる問題がありました。GA版の`gpt-realtime`は非同期関数呼び出しをネイティブサポートし、処理待ち中も会話を継続できます。

### 実装パターン

```
import asyncio
import json

async def handle_function_call(ws, call_id: str, function_name: str, arguments: dict):
    """非同期で関数を実行しながら会話を継続"""
    if function_name == "get_order_status":
        # 長時間かかる外部API呼び出し（例: 在庫確認）
        result = await fetch_order_from_api(arguments["order_id"])

        # 結果をRealtimeセッションに返す
        await ws.send(json.dumps({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result)
            }
        }))
        # 次の応答生成を指示
        await ws.send(json.dumps({"type": "response.create"}))

async def event_loop(ws):
    """イベントを受信してディスパッチ"""
    async for message in ws:
        event = json.loads(message)

        if event["type"] == "response.function_call_arguments.done":
            # 関数呼び出しをバックグラウンドで処理
            asyncio.create_task(
                handle_function_call(
                    ws,
                    call_id=event["call_id"],
                    function_name=event["name"],
                    arguments=json.loads(event["arguments"])
                )
            )
        elif event["type"] == "response.output_audio.delta":
            # 音声出力を処理（関数実行と並行して進む）
            process_audio(event["delta"])
```

ポイントは `asyncio.create_task` で関数実行をバックグラウンドに逃がすことです。これにより、注文状況照会のような数秒かかる処理中も「少々お待ちください」などの音声応答を並行して出力できます。

---

## 料金

料金は更新されることがあるため、[OpenAI API Pricing](https://developers.openai.com/api/docs/pricing) および [gpt-realtime モデルページ](https://developers.openai.com/api/docs/models/gpt-realtime) で最新の価格を確認してください。

公式ページによると `gpt-realtime` は**音声・テキストのモダリティ別にトークン料金が異なり**、音声トークンはテキストより高い傾向があります。

詳細なコスト管理は[Managing Costs for Realtime API](https://developers.openai.com/api/docs/guides/realtime-costs)を参照してください。

---

## プレビュー版からGA版への移行

プレビュー版のイベント名がGA版で変更されています。移行時に必ず対応が必要です。

### イベント名の変更一覧

| プレビュー版 | GA版 |
| --- | --- |
| `response.text.delta` | `response.output_text.delta` |
| `response.audio.delta` | `response.output_audio.delta` |
| `response.audio_transcript.delta` | `response.output_audio_transcript.delta` |

### モデルIDの変更

```
# 変更前（プレビュー版）
model = "gpt-4o-realtime-preview"

# 変更後（GA版）
model = "gpt-realtime-1.5"
```

### 移行チェックリスト

Azureを使用している場合は、[Azure OpenAI Realtime API移行ガイド](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/realtime-audio-preview-api-migration-guide)も合わせて参照してください。

---

## ハマりポイント

### セッション中に声を変更しようとしてしまう

`session.update` でセッション中に `voice` を変更しようとしても反映されません。**セッション作成前**または最初の音声出力前に設定する必要があります。

### MCPサーバーのタイムアウト

音声会話のリアルタイム性上、MCPツールの応答が遅いと自然な会話体験が損なわれます。MCPサーバーはレスポンス時間を**1秒以内**に抑えることを推奨します。遅い処理は非同期関数呼び出しと組み合わせてください。

### input\_audio\_format のミスマッチ

SIP/Twilio経由の場合は `g711_ulaw`、ブラウザ/マイクの場合は `pcm16` を指定します。フォーマット不一致は無音や雑音の原因になります。

```
# Twilio（電話系）
"input_audio_format": "g711_ulaw",
"output_audio_format": "g711_ulaw",

# ブラウザ/マイク（Web系）
"input_audio_format": "pcm16",
"output_audio_format": "pcm16",
```

---

## まとめ

* `gpt-realtime` はプレビュー版比で命令追従性 **+48%**、ツール呼び出し精度 **+34%** を達成
* **SIP対応** により電話コールセンターをそのまま音声AIに置き換えられる
* **MCPサーバー連携** でURLを渡すだけのゼロコードツール統合が可能
* **非同期関数呼び出し** により長い外部API処理中も会話が自然に続く
* プレビュー版は非推奨化予定 — [Deprecationsページ](https://developers.openai.com/api/docs/deprecations)で廃止日を確認し、今すぐ移行を開始することを強くお勧めします

音声AIは「インフラ」として成熟しつつあります。SIP電話とMCPの組み合わせにより、既存の業務システムをほぼそのままの形で音声エージェントに接続できる時代が来ています。

---

## 参考リンク
