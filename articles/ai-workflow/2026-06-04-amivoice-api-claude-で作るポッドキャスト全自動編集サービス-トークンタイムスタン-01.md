---
id: "2026-06-04-amivoice-api-claude-で作るポッドキャスト全自動編集サービス-トークンタイムスタン-01"
title: "AmiVoice API × Claude で作る「ポッドキャスト全自動編集サービス」— トークンタイムスタンプで文ごとにジャンプできる文字"
url: "https://zenn.dev/nobalto/articles/d4a55f9be67434"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

## はじめに

「収録したポッドキャストを編集するのが面倒すぎる」

ノイズ除去・フィラー（えーとあのー）カット・文字起こし・ボイスチェンジ・BGM挿入……これを毎回手動でやっていると、収録より編集のほうが時間がかかります。

そこで **PodVoice**（<https://www.podvoice.jp>）を作りました。

### なぜ作ったのか

日本でもポッドキャストは少しずつ広がっていますが、海外の主要サービス（Riverside.fm、Descript など）は UI が英語で、日本語話者には操作が難しかったり、料金も高めです。「日本語UIで、日本語音声に強くて、普通の人でも使いこなせる編集サービスがあったら絶対に需要がある」と思ったのが開発のきっかけです。

そこで技術選定の段階から一つのこだわりがありました。**文字起こしエンジンは日本語に強いものを使うこと**。ポッドキャスト編集の中心には文字起こしがあり、精度が低ければ編集体験が根本から崩れます。

### AmiVoice が「このサービスにとって最高のAPI」だった理由

いくつかのエンジンを比較検討した末に選んだのが **AmiVoice API** です。日本語特化の音声認識エンジンとして、固有名詞・専門用語・話し言葉のカタカナ語（「リファクタリング」「プルリクエスト」）の認識精度が明らかに優れていました。

でも精度だけではありません。AmiVoice が返す**トークンレベルのタイムスタンプ**こそが、このサービスの目指す編集体験を実現する鍵でした——文字をクリックしたらその箇所の音声に飛ぶ、という機能です。日本語音声に強く、かつ単語ごとの時刻情報まで取れるAPIは、まさに「日本語ポッドキャスト編集サービスのために作られたもの」と感じました。

ブラウザだけで複数人を個別トラック収録し、そのままノイズ除去・文字起こし・ボイスチェンジ・WAV書き出しまでできるWebサービスです。Claude MCP にも対応しているので、「えーとを消してロボット声にして書き出して」とチャットで指示するだけで全部動きます。

この記事では、サービスの核心である **AmiVoice API を使った文字起こし実装**を中心に、Claude との組み合わせ方や、ブラウザでのロスレス録音まで解説します。

---

## サービス全体像

![](https://static.zenn.studio/user-upload/398308ddbf74-20260604.png)  
主な機能：

| 機能 | 技術 |
| --- | --- |
| マルチトラック収録 | AudioWorklet + WebRTC |
| **文字起こし** | **AmiVoice API**（Pro）/ Whisper tiny（Free） |
| ボイスチェンジ | librosa pitch shift |
| BGM・SE挿入 | Jamendo API + pydub |
| WAV書き出し | pydub mixdown |
| AI 指示 | Claude API（Haiku） |
| MCP サーバー | 自作 MCP + Claude Desktop |

スタック：Next.js 16（App Router）+ FastAPI + Supabase + Cloudflare R2 + Render

---

## AmiVoice API の技術的な特長

**決め手は3つ：**

### 1. 日本語ポッドキャストへの精度

Whisper（tiny〜medium）と比較したとき、AmiVoice は日本語の固有名詞・専門用語の認識が明らかに上でした。特にポッドキャストでよく出てくるカタカナ語（「リファクタリング」「プルリクエスト」など）の精度が高い。

### 2. トークンレベルのタイムスタンプ

これが最大の理由です。AmiVoice は `tokens` フィールドで**単語ごとのタイムスタンプ**を返してくれます。

```
{
  "text": "本日はよろしくお願いします。",
  "results": [
    {
      "tokens": [
        { "written": "本日", "starttime": 1200, "endtime": 1680 },
        { "written": "は",   "starttime": 1680, "endtime": 1840 },
        { "written": "よろしく", "starttime": 1840, "endtime": 2320 },
        { "written": "お願いします", "starttime": 2320, "endtime": 3100 },
        { "written": "。",   "starttime": 3100, "endtime": 3100 }
      ]
    }
  ]
}
```

これを使うと「**文字をクリックするとその箇所に音声がジャンプする**」機能が作れます。編集時に「あのーって言ったのどこだっけ？」と音声を聴き直す手間がゼロになります。

### 3. 月60分の無料枠（コンテスト期間中は10時間）

SaaS に組み込むには、ある程度の無料枠がないとプロトタイプが作れません。月60分あれば十分テストができます。

---

## 実装詳細

### アーキテクチャ

```
ブラウザ → Next.js API Route → FastAPI（Render）→ AmiVoice API
                                     ↓
                              チャンク変換処理
                                     ↓
                              Next.js → ブラウザ（SSEでリアルタイム進捗）
```

### FastAPI 側: AmiVoice API 呼び出し

```
AMIVOICE_ENDPOINT = "https://acp-api.amivoice.com/v1/recognize"
AMIVOICE_ENGINE   = "-a-general"  # 汎用日本語エンジン

async def _transcribe_amivoice(audio_bytes: bytes, filename: str = "audio.wav") -> dict:
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            AMIVOICE_ENDPOINT,
            data={"d": AMIVOICE_ENGINE, "u": AMIVOICE_API_KEY},
            files={"a": (filename, audio_bytes, "audio/wav")},
        )
        resp.raise_for_status()
        data = resp.json()

    text    = data.get("text", "").strip()
    results = data.get("results", [])
    chunks  = _tokens_to_chunks(results)   # ← ここが肝

    return {"text": text, "chunks": chunks, "engine": "amivoice"}
```

シンプルです。マルチパートで音声バイナリを送るだけ。

### トークン → 文チャンク変換が工夫ポイント

AmiVoice は長い音声を1〜数個の `results` にまとめて返す傾向があります。そのまま使うと「音声全体が1チャンク」になってしまい、文クリックジャンプが使えません。

そこで `tokens` の単語レベルタイムスタンプを使い、**句読点（。！？）で文を区切って細かいチャンクを生成**しています。

```
_SENTENCE_ENDS = frozenset("。！？…!?")

def _tokens_to_chunks(results: list) -> list:
    chunks = []
    for result in results:
        tokens = result.get("tokens") or []
        if not tokens:
            # トークン情報なし → result 単位でそのまま使う
            t = result.get("text", "").strip()
            if t:
                chunks.append({
                    "text":  t,
                    "start": result.get("starttime", 0) / 1000,
                    "end":   result.get("endtime",   0) / 1000,
                })
            continue

        # トークンを句読点で区切って文を生成
        buf = []
        for tok in tokens:
            buf.append(tok)
            written = tok.get("written", "")
            if written and written[-1] in _SENTENCE_ENDS:
                text = "".join(t.get("written", "") for t in buf).strip()
                if text:
                    chunks.append({
                        "text":  text,
                        "start": buf[0].get("starttime", 0) / 1000,  # 文の最初の単語の開始時刻
                        "end":   buf[-1].get("endtime",   0) / 1000,  # 文の最後の単語の終了時刻
                    })
                buf = []

        # 末尾の句読点なしの残り
        if buf:
            text = "".join(t.get("written", "") for t in buf).strip()
            if text:
                chunks.append({
                    "text":  text,
                    "start": buf[0].get("starttime", 0) / 1000,
                    "end":   buf[-1].get("endtime",   0) / 1000,
                })

    return chunks
```

**変換前のイメージ：**

```
result: { text: "本日はよろしくお願いします。早速ですが始めていきましょう。", starttime: 1200, endtime: 8500 }
```

**変換後：**

```
chunk[0]: { text: "本日はよろしくお願いします。", start: 1.2, end: 3.1 }
chunk[1]: { text: "早速ですが始めていきましょう。", start: 3.1, end: 8.5 }
```

文ごとに正確な開始・終了時刻が付いたチャンクが得られます。

### SSEでリアルタイム進捗を返す

AmiVoice API のレスポンスは音声の長さに応じて数秒〜数十秒かかります。その間ユーザーが「止まってる？」と思わないよう、**Server-Sent Events（SSE）でリアルタイム進捗**を返しています。

```
@router.post("/transcribe-stream")
async def transcribe_stream(request: Request, token: str = Form(...), url: str = Form(...)):
    async def generate():
        yield _sse({"type": "progress", "value": 10, "message": "音声を取得中..."})

        # AmiVoice に送信
        yield _sse({"type": "progress", "value": 30, "message": "AmiVoice に送信中..."})
        task = asyncio.create_task(_transcribe_amivoice(audio_bytes, "audio.wav"))

        # AmiVoice 処理中にハートビートを送り続ける（プロキシのタイムアウト対策）
        progress = 30
        while not task.done():
            await asyncio.sleep(5.0)
            progress = min(progress + 5, 88)
            yield _sse({"type": "progress", "value": progress, "message": "AmiVoice 解析中..."})

        result = task.result()
        yield _sse({"type": "done", "text": result["text"], "chunks": result["chunks"]})

    return StreamingResponse(generate(), media_type="text/event-stream")
```

ハートビートを5秒ごとに送ることで、Render や Vercel のプロキシが途中でコネクションを切らないようにしています。

### Next.js 側: SSEの受け取りとUI反映

```
// チャンクをリアルタイムに受け取ってプログレスバーを更新
const es = new EventSource(`...`)
// もしくは fetch + ReadableStream で SSE を受け取る
const res = await fetch('/api/transcribe-token', { method: 'POST', body: form })
const reader = res.body!.getReader()

for await (const chunk of reader) {
  const lines = new TextDecoder().decode(chunk).split('\n')
  for (const line of lines) {
    if (!line.startsWith('data:')) continue
    const event = JSON.parse(line.slice(5))
    if (event.type === 'progress') setProgress(event.value)
    if (event.type === 'done') {
      setTranscript(event.text)
      setChunks(event.chunks)  // { text, timestamp: [start, end] }[]
    }
  }
}
```

### 文クリックでタイムジャンプ

受け取ったチャンクをそのまま `<button>` に並べ、クリック時に `<audio>` の `currentTime` を変更するだけです。

```
<div className="space-y-1">
  {chunks.map((chunk, i) => (
    <button
      key={i}
      onClick={() => {
        if (audioRef.current) {
          audioRef.current.currentTime = chunk.timestamp[0]
          audioRef.current.play()
        }
      }}
      className="text-left text-sm hover:bg-indigo-50 px-2 py-1 rounded"
    >
      <span className="text-xs text-gray-400 mr-2 font-mono">
        {fmtTime(chunk.timestamp[0])}
      </span>
      {chunk.text}
    </button>
  ))}
</div>
```

![](https://static.zenn.studio/user-upload/6fb29c02dc1f-20260604.png)  
確認したいところにすぐ飛べます。「あのーって言ったのどこだっけ？」と音声を何度も聴き直す手間がなくなります。

---

## Claude との組み合わせ

文字起こしと Claude を組み合わせることで、さらに強力な機能を作れます。

### ① MCP サーバーで「話しかけるだけ」

Claude Desktop に PodVoice の MCP サーバーを登録すると、チャット画面から自然言語で操作できます。

```
ユーザー: 最新の録音を文字起こしして

Claude: 「第5回収録.wav」(43分) の文字起こしを開始します...
        [AmiVoice で解析中]
        完了しました。143文のチャンクが生成されました。
        要約：本日は○○について3名で議論しました...
```

MCP ツールの定義はシンプルです：

```
@mcp.tool()
async def transcribe_recording(recording_id: str) -> str:
    """録音を文字起こしする（AmiVoice使用）"""
    result = await call_transcribe_api(recording_id)
    # chunks を Markdown に変換して返す
    lines = [f"[{fmt_time(c['start'])}] {c['text']}" for c in result['chunks']]
    return "\n".join(lines)
```

Claude は返ってきたタイムスタンプ付きテキストをそのまま要約・分析できます。

### ② AI ボイス指示

マルチトラック収録後、「田中さんをロボット声にして、山田さんはナレーター風にして」とチャットで指示できます。Claude Haiku がトラック一覧と指示文を受け取り、どのトラックにどのボイスを適用するかを JSON で返します。

```
// POST /api/multi-track-projects/[id]/ai-voice
const message = await anthropic.messages.create({
  model: 'claude-haiku-4-5',
  max_tokens: 512,
  messages: [{
    role: 'user',
    content: `
トラック一覧:
- ID: xxx, 名前: 田中, 現在のボイチェン: none
- ID: yyy, 名前: 山田, 現在のボイチェン: none

利用可能なボイスタイプ: robot, narrator, female, anime ...

ユーザーの指示: 「田中をロボットにして山田をナレーターに」

JSON配列で返してください: [{"trackId": "...", "voiceType": "..."}]
    `
  }]
})
// → [{"trackId": "xxx", "voiceType": "robot"}, {"trackId": "yyy", "voiceType": "narrator"}]
```

文字起こし結果 → Claude による要約・分析 → ボイス指示という流れで、**テキストと音声を行き来する編集体験**が生まれます。

---

## ブラウザ録音の品質を上げる工夫

AmiVoice API がどれだけ高精度でも、入力音声が悪ければ精度は落ちます。ブラウザ録音の品質を上げるために、MediaRecorder ではなく **AudioWorklet** を採用しました。

### ブラウザ音声処理をすべてオフにする

```
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: false,  // ブラウザのECをオフ（音色を守る）
    noiseSuppression: false,  // サーバー側で処理するのでブラウザNRはオフ
    autoGainControl:  false,  // AGCによる音量ポンプを防ぐ
    sampleRate:       48000,
    channelCount:     1,
  },
})
```

`echoCancellation: true`（デフォルト）のままだと、ブラウザが独自の音声処理を行い声の音色が変わってしまいます。これをオフにするだけで劇的に音質が改善します。

### AudioWorklet で生PCM → 16-bit WAV

```
// public/audio-processor.worklet.js
class PCMProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const ch = inputs[0]?.[0]
    if (ch) this.port.postMessage(new Float32Array(ch))
    return true
  }
}
registerProcessor('pcm-processor', PCMProcessor)
```

```
// Float32 PCM → 16-bit WAV（ロスレス）
function encodeWAV(buffers: Float32Array[], sampleRate: number): Blob {
  const totalSamples = buffers.reduce((n, b) => n + b.length, 0)
  const buf = new ArrayBuffer(44 + totalSamples * 2)
  const v = new DataView(buf)
  // WAVヘッダ書き込み...（PCM, 16bit, mono）
  let pos = 44
  for (const b of buffers) {
    for (let i = 0; i < b.length; i++) {
      const s = Math.max(-1, Math.min(1, b[i]))
      v.setInt16(pos, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
      pos += 2
    }
  }
  return new Blob([buf], { type: 'audio/wav' })
}
```

エンコードされた WAV を Cloudflare R2 にプリサイン PUT URL で直接アップロード（Vercel のボディサイズ制限をバイパス）し、それを AmiVoice に送ります。

**MediaRecorder（128kbps Opus）との比較：**

* ブラウザ処理なし → 自然な声のまま
* WAV（16-bit 48kHz）→ ロスレス
* AmiVoice に最適な入力 → 認識精度が上がる

---

## 詰まったところと解決策

### 1. AmiVoice が長い音声を1チャンクにまとめてしまう

最初は `results` をそのままチャンクにしていたので、10分の音声が1つの巨大チャンクになっていました。`tokens` の句読点分割で解決。

### 2. プロキシのタイムアウト

Vercel → Render（FastAPI）→ AmiVoice という経路で、AmiVoice の処理中（30〜60秒）にVercelのプロキシが504を返してしまいました。SSEのハートビート（5秒ごとにイベントを送る）で解決。

### 3. R2 への直接アップロードの CORS

ブラウザから R2 へ直接 PUT するとき、R2 の CORS ポリシーに `AllowedMethods: ["PUT"]` を追加しないとブラウザのプリフライトが弾かれます。

```
[{
  "AllowedOrigins": ["https://www.podvoice.jp"],
  "AllowedMethods": ["PUT"],
  "AllowedHeaders": ["Content-Type"],
  "MaxAgeSeconds": 3600
}]
```

---

## まとめ

PodVoice の文字起こし実装のポイントをまとめます：

1. **AmiVoice API の `tokens` フィールドで単語レベルタイムスタンプを取得**
2. **句読点で分割して文チャンクを生成 → クリックジャンプ実現**
3. **SSE + ハートビートで長時間処理中もリアルタイム進捗を表示**
4. **AudioWorklet + WAV でブラウザ処理をバイパスして AmiVoice に最適な音声を渡す**
5. **Claude との組み合わせで文字起こし結果をそのまま AI 分析・指示に活用**

「音声 → テキスト → AI操作」の流れを一つのサービスで完結させることで、ポッドキャスト制作の体験を根本的に変えられると感じています。

ぜひ [PodVoice](https://www.podvoice.jp) を試してみてください。Proプランで AmiVoice 文字起こしが使えます（現在ベータ版につき割引中）。

---

## 参考
