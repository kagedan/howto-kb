---
id: "2026-05-01-hermes-agent-に-line-を繋いだ話-コアを触らずブリッジで解決する-01"
title: "Hermes Agent に LINE を繋いだ話 — コアを触らずブリッジで解決する"
url: "https://zenn.dev/acntechjp/articles/5e2cf37de21a49"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "OpenAI", "zenn"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/52cb460f4ab8-20260501.png)

## はじめに

[Hermes Agent](https://github.com/NousResearch/hermes-agent)（NousResearch の AI エージェントフレームワーク）と LINE Messaging API を繋ぐ**スタンドアロンブリッジ**を作りました。コードは MIT ライセンスで公開しています。

<https://github.com/hfujikawa77/hermes-line-bridge>

---

## なぜ作ったのか

情報収集・コンテンツ作成・配信を目的として、VPS上で運用していた [OpenClaw](https://github.com/openclaw/openclaw) を破棄することになり、SNSやGitHubで話題になっていた [Hermes Agent](https://github.com/NousResearch/hermes-agent) へ移行しました。  
OpenClawでは家族との連絡にLINEを使ってたので、Hermesでも使いたかったのですが、2026年5月時点では未サポート、[upstream Issue #6081](https://github.com/NousResearch/hermes-agent/issues/6081) や関連PRもありますが、進展がありません。これを受けて、自作してみました。

---

## できたもの

* LINEからのメッセージ入力と応答 (ユーザー、グループ）
* Hermes Agent CLI、Discordからのメッセージ送信
* ユーザー、グループのIDの替わりに「僕」「グループ」など別名での宛先指定可
* LINEからの画像メッセージの受信と応答

<https://youtu.be/_CDNmz9qhYg>

---

## なぜコアを触らずブリッジ案なのか

Hermes 本体を改変する方法もありますが、アップデートのたびにコンフリクトが発生するリスクと、将来の公式対応時に切り替えしにくくなることを避けるため、ブリッジ案を採用しました。

Hermes には **[OpenAI 互換の API サーバー](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/api-server.md)**（`:8642`）が内蔵されています。このエンドポイントに HTTP でリクエストを投げるブリッジを外から立てれば、本体を一切変更せずに新チャンネルを追加できます。

---

セットアップの手順は [README](https://github.com/hfujikawa77/hermes-line-bridge) に書いてあります。以下は元ネタとの差分、実装上の工夫、はまりポイントに絞った解説です。

---

## 元ネタとの差分・工夫・はまりポイント

ブリッジというアイデア自体は [Issue #6081 のコメント](https://github.com/NousResearch/hermes-agent/issues/6081#issuecomment-4231624619)（[@audachang](https://github.com/audachang)）が元ネタです。ただそのコメントは骨格だけで、動くものを作るには細部を自分で設計する必要がありました。

### (A) 画像メッセージの受信（vision 連携）

![](https://static.zenn.studio/user-upload/53778d85f678-20260501.png)

LINE で画像を送ると、bridge が LINE Content API からダウンロードして base64 エンコードし、OpenAI 互換のマルチモーダル形式で Hermes に渡します。vision 対応モデルを使えば LINE 上でそのまま画像の説明や OCR を頼めます。

bridge.py

```
content = [
    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
]
```

**ハマりポイント1：Content API のホスト名**

画像コンテンツの取得は `api.line.me` ではなく **`api-data.line.me`** が正しいホストです。公式ドキュメントには記載がありますが見落としやすく、最初は 404 が返り続けました。

bridge.py

```
LINE_DATA_API = "https://api-data.line.me/v2/bot"  # api.line.me ではない
```

**ハマりポイント2：`aiohttp.ClientSession` のスコープ**

画像のダウンロードと LINE への返信を別の `ClientSession` ブロックに分けると `RuntimeError: Session is closed` になります。ダウンロード・Hermes 呼び出し・返信を同一の `with` ブロックに収める必要があります。

bridge.py

```
async with ClientSession() as http:
    img_bytes, img_mime = await _download_image(http, mid)
    response = await _ask_hermes(http, "", sid, img_bytes)
    await _line_reply(http, rt, response)  # 同じ with の中
```

### (B) Hermes → LINE への能動送信（`POST /send`）

Webhook は LINE からの着信にしか反応しません。cron によるリマインダーや Hermes CLI からの指示で送信するために `POST /send` エンドポイントを追加しました。ローカルホスト（`127.0.0.1`）からのリクエストのみ受け付け、`API_SERVER_KEY` で認証します。

```
curl -s -X POST http://localhost:8650/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_SERVER_KEY>" \
  -d '{"to": "Uxxxxxxxxxx", "text": "おはようございます！"}'
```

Discord → Hermes → LINE のような転送チェーンも同じ方法で実現できます。

### (C) エイリアス解決（`line-aliases.tsv`）

LINE の user/group ID（`U...` / `C...`）は 33 文字あって覚えられません。`alias<TAB>id` 形式の TSV ファイルにニックネームを書いておき、シェルスクリプト（`line-send.sh`）が解決します。

line-aliases.tsv

```
僕	Uxxxx...
家族	Cxxxx...
```

Hermes の記憶に「LINE 送信には `line-send.sh <alias> <message>` を使う」と登録しておくと、CLI から自然言語で送信先を指定できます。

### (D) Reply API → Push API フォールバック

LINE の Reply Token は約 1 分で失効します。LLM の処理が間に合わなかった場合、Reply API が静かに失敗してユーザーに何も届かないため、Push API へのフォールバックを入れています。

bridge.py

```
if not await _line_reply(http, reply_token, response) and push_to:
    await _line_push(http, push_to, response)
```

### (E) セッション継続と API キー

`X-Hermes-Session-Id` ヘッダーを使い、同じ LINE ユーザー／グループの会話を跨いで文脈を保持します。

ここで注意が要ったのは、Hermes 側で `API_SERVER_KEY` を設定しないとセッション継続が動かない点です。キーなしでも 1 通目は返答しますが、2 通目から 403 が返ります。`hermes config set` では反映されなかったため、`~/.hermes/.env` に直接 `API_SERVER_KEY=<key>` を書きました。

---

## まとめ

* Hermes の OpenAI 互換 API を使えば、**本体を一切改変せず** LINE を新チャンネルとして追加できる
* ブリッジ方式なので、将来 Hermes 公式が LINE 対応したときにスムーズに切り替え可能
* 画像連携・能動送信・エイリアス解決など、元ネタにはなかった機能を独自に追加した

<https://github.com/hfujikawa77/hermes-line-bridge>
