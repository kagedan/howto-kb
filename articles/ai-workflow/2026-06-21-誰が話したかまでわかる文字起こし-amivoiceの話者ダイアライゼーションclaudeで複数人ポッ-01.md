---
id: "2026-06-21-誰が話したかまでわかる文字起こし-amivoiceの話者ダイアライゼーションclaudeで複数人ポッ-01"
title: "「誰が話したか」までわかる文字起こし — AmiVoiceの話者ダイアライゼーション×Claudeで複数人ポッドキャストの議事録を自動生成す"
url: "https://zenn.dev/nobalto/articles/abe8501ab1b93e"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

## はじめに

複数人で収録したポッドキャストや会議。これを文字起こしすると、こういう壁にぶつかります。

> 「文章は起こせた。でも、**どの発言が誰のものか**が分からない」

一本の文字列にダラっと全員の発言が混ざっていると、議事録にも、話者ごとの要約にも、「Aさんの発言だけ抜き出す」にも使えません。複数人コンテンツでは **「誰が話したか（who spoke when）」の情報こそが本体**です。

この記事では、**AmiVoice API の話者ダイアライゼーション**で話者を自動判別し、その結果を **Claude（生成AI）** に渡して議事録・話者別要約・発話時間の集計まで自動生成する仕組みを、実装込みで解説します。

題材は、私が開発しているポッドキャスト編集サービス [PodVoice](https://www.podvoice.jp)（ブラウザ録音 → 文字起こし → 編集 → 書き出しを Claude に話しかけるだけでできる、完全日本語のWebサービス）です。「複数人で録る」ユースケースにこの機能がどれだけ効くか、というのが今回いちばん伝えたいところです。

---

## 話者ダイアライゼーションとは

**話者ダイアライゼーション（speaker diarization）** は、1つの音声の中で「いつ・誰が」話したかを区切る技術です。声紋の違いから話者を `speaker0` `speaker1` …と自動でラベリングします。

```
（従来の文字起こし）
本日はよろしくお願いしますこちらこそお願いしますでは始めましょう

（話者ダイアライゼーション後）
[speaker0] 本日はよろしくお願いします
[speaker1] こちらこそお願いします
[speaker0] では始めましょう
```

右側のように話者が分かれていれば、そのまま議事録の体裁になり、「speaker1 の発言だけ要約して」といった操作も一発です。

AmiVoice は日本語特化の音声認識エンジンで、この話者ダイアライゼーションに対応しています（[公式アナウンス](https://acp.amivoice.com/blog/2022-02-01/)）。

### ポッドキャストと相性が良い理由（と、過信しないための前提）

魔法の道具というわけではありません。話者分離は声の特徴で区切る技術なので、**全員が同時にかぶせて話す場面や、ごく短い相槌**ではラベルがぶれることがあります。これはAmiVoiceに限らず話者分離全般の性質です。

その上で、ポッドキャストや対談はこの技術と**かみ合いやすい**コンテンツだと考えています。理由は3つ。

1. **基本的に話者が交代で話す**。司会→ゲスト→司会…とターンが分かれるため、同時発話が主体の環境より格段に分離しやすい。
2. **日本語の話し言葉が多い**。日本語特化のエンジンなので、固有名詞・カタカナ語・口語が混じる収録でも文字起こしの土台が崩れにくい。
3. **多少のラベルのぶれは後工程で吸収できる**。後述するように、話者名は人が手で（またはAIが文脈から）付け直せるので、「だいたい合っている分離結果」を実用レベルまで持っていけます。

つまり「完璧な話者分離」を期待するのではなく、**8割方正しい分離をAIと人で仕上げる**という前提に立つと、ポッドキャスト編集にちょうど良い道具になります。

---

## なぜ「同期API」ではなく「非同期API」なのか

ここが最初のポイントです。AmiVoice には2種類の音声認識インタフェースがあります。

|  | 同期HTTP | 非同期HTTP |
| --- | --- | --- |
| エンドポイント | `acp-api.amivoice.com/v1/recognize` | `acp-api-async.amivoice.com/v1/recognitions` |
| 最大データサイズ | **16MB** | **約2.14GB** |
| 話者分離 | ✕ | **○** |
| 処理 | リクエストを投げて待つ | ジョブ投入 → ポーリングで結果取得 |

話者ダイアライゼーションは**非同期API側の機能**です。そして非同期APIは「ジョブを作る → 完了するまで結果取得をポーリングする」というジョブ型の使い方になります。

（余談ですが、以前 16MB の同期APIに 127MB のWAVを投げて `413 Payload Too Large` を食らった話は[別記事](https://www.podvoice.jp)に書きました。長尺・複数人を本気で扱うなら、最初から非同期APIを選ぶのが正解です。）

---

## 実装：ジョブ投入 → ポーリング → 話者ターンへ整形

### ① ジョブを投入する

非同期APIのジョブ作成は、`d` パラメータに `speakerDiarization=True` を足すだけです。最小・最大話者数も指定できます。

```
AMIVOICE_ASYNC_ENDPOINT = "https://acp-api-async.amivoice.com/v1/recognitions"

# d パラメータに話者分離の設定を載せる
d_param = (
    f"grammarFileNames=-a-general "
    f"speakerDiarization=True "
    f"diarizationMinSpeaker=1 "
    f"diarizationMaxSpeaker={max_speakers}"
)

with open(audio_path, "rb") as f:
    resp = await client.post(
        AMIVOICE_ASYNC_ENDPOINT,
        data={"u": AMIVOICE_API_KEY, "d": d_param},
        files={"a": ("audio.flac", f, "audio/x-flac")},  # ファイルハンドルでストリーム送信
    )
sessionid = resp.json()["sessionid"]   # ← このIDで結果をポーリングする
```

ポイントが2つ。

* **音声は 16kHz モノラルに変換して送る**。音声認識エンジンは 16kHz が標準なので精度は落ちず、アップロード量を大きく減らせます。話者分離はモノラル1チャンネルの中で声を分けるので、ダウンミックスしても問題ありません。
* **`bytes` ではなくファイルハンドルを渡す**。httpx がストリーミング送信してくれるので、長尺ファイルでもメモリのピークを抑えられます。

### ② 完了までポーリングする

ジョブには `queued → started → processing → completed`（または `error`）というステータスがあります。`completed` になるまで `sessionid` で問い合わせます。

```
header = {"Authorization": f"Bearer {AMIVOICE_API_KEY}"}

while waited < MAX_WAIT:
    await asyncio.sleep(5.0)
    waited += 5
    pr = await client.get(f"{AMIVOICE_ASYNC_ENDPOINT}/{sessionid}", headers=header)
    pj = pr.json()
    status = pj.get("status")
    if status == "completed":
        result_json = pj
        break
    if status == "error":
        raise RuntimeError(pj.get("error_message"))
    # ここで SSE のハートビートを送り、フロント／プロキシのタイムアウトを防ぐ
    yield sse({"type": "progress", "message": f"話者分離 解析中... ({status})"})
```

ポーリング中は **SSE（Server-Sent Events）でハートビート**を送り続けます。これがないと、ブラウザや Vercel/Render のプロキシが「無反応」とみなして接続を切ってしまうためです。

### ③ トークンの話者ラベルを「発話ターン」に束ねる

完了レスポンスの肝は、**トークン（単語）ごとに付く `label`** です。`segments[].results[].tokens[]` の各トークンに `"label": "speaker0"` のように話者が入っています。

```
{
  "status": "completed",
  "segments": [
    {
      "results": [
        {
          "tokens": [
            { "written": "本日", "starttime": 1200, "endtime": 1680, "label": "speaker0" },
            { "written": "は",   "starttime": 1680, "endtime": 1840, "label": "speaker0" },
            { "written": "こちらこそ", "starttime": 3200, "endtime": 3900, "label": "speaker1" }
          ]
        }
      ]
    }
  ]
}
```

このままだと単語バラバラなので、**連続する同じ話者のトークンを1つの発話ターンに結合**します。これで「[speaker0] 本日は…」という議事録向きの単位になります。

```
def _segments_to_speaker_turns(segments):
    """連続する同一話者のトークンを1つの発話ターンに結合する"""
    turns, cur = [], None
    for seg in segments:
        for res in seg.get("results", []):
            for tok in res.get("tokens", []):
                written = tok.get("written", "")
                if not written:
                    continue
                label = tok.get("label") or "speaker0"
                start = tok.get("starttime", 0) / 1000
                end   = tok.get("endtime", 0) / 1000
                if cur and cur["speaker"] == label:
                    cur["text"] += written       # 同じ話者 → 結合
                    cur["end"] = end
                else:
                    if cur:
                        turns.append(cur)
                    cur = {"speaker": label, "text": written, "start": start, "end": end}
    if cur:
        turns.append(cur)
    return turns
```

結果はこうなります。

```
[
  { "speaker": "speaker0", "text": "本日はよろしくお願いします", "start": 1.2, "end": 5.4 },
  { "speaker": "speaker1", "text": "こちらこそお願いします",     "start": 5.6, "end": 8.1 },
  { "speaker": "speaker0", "text": "では始めましょう",           "start": 8.3, "end": 10.0 }
]
```

「誰が・いつ・何を」話したかが構造化されました。**ここから先が生成AIの出番**です。

---

## 2つの入り口：GUIのワンクリックと、Claude（MCP）

この話者分離は **画面のボタンからも、AIへの指示からも**実行できるようにしました。

* **GUI**: ダッシュボードの録音ごとに「話者分離」ボタンを置き、押すと発話ターンが時刻付きで並びます。ブラウザから Render の処理サーバーへ直接 SSE 接続するので、長尺でもプロキシのタイムアウトに当たりません。
* **MCP（Claude）**: 「3人で録ったやつを議事録にして」と話しかけるだけ。Claude が裏でツールを呼びます。

同じ処理を「人が手で」も「AIが自律的に」も叩ける——この二面性が後で効いてきます。まずは生成AIとの組み合わせから。

### Claude が議事録に変える

PodVoice は Claude の **MCP（Model Context Protocol）サーバー**を提供しています。話者分離をMCPツールとして公開し、Claude が自分で呼び出して結果を読めるようにしました。

```
// MCPツール定義（抜粋）
server.tool(
  "transcribe_with_speakers",
  "話者ダイアライゼーション付きで文字起こしする（AmiVoice非同期API）。" +
  "誰がいつ話したかを speaker0/speaker1... のラベル付き発話ターンで返す。\n" +
  "用途: 複数人ポッドキャスト・会議の議事録作成、話者ごとの要約、発話時間の集計など。",
  { recording_id: z.string(), max_speakers: z.number().optional() },
  async ({ recording_id, max_speakers }) => {
    const data = await api("/api/mcp/transcribe-speakers", {
      method: "POST",
      body: JSON.stringify({ recording_id, max_speakers }),
    });
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);
```

ツールの説明文に「議事録・話者別要約・発話時間集計に使う」と書いておくと、Claude は話者ラベル付きセグメントを受け取ったあと、**追加の指示なしに**それを議事録や要約へ加工してくれます。

実際の使い心地はこんな感じです。

```
ユーザー: 昨日の収録、3人で話したやつを議事録にして

Claude: transcribe_with_speakers を実行します...
        （AmiVoiceで話者分離 → 2,800字 / 3話者 / 142ターンを取得）

        議事録:
        ■ 出席: speaker0（司会）, speaker1, speaker2
        ■ 発話時間: speaker0 12分 / speaker1 18分 / speaker2 9分
        ■ 要点:
          - speaker1: 新機能のリリース時期は来月を想定
          - speaker2: ただしテスト工数が懸念。speaker0 が追加メンバー調整を約束
        ■ ToDo:
          - [ ] speaker0: テスト要員のアサイン（〜今週中）
          ...
```

AmiVoice が出した `speaker0/1/2` というラベルを、Claude が文脈から「司会」「○○の担当」と推測して読み替えることもできます。**「声で話者を区切るAmiVoice」と「文脈を読む生成AI」は、片方だけでは届かないところを補い合う**——ここが今回いちばん効いている組み合わせです。

### 文字起こし枠を無駄にしないキャッシュ

話者分離は処理時間も認識枠も消費します。そこで結果を DB（`recordings.transcript_speakers`）にキャッシュし、同じ録音で再度呼ばれたらキャッシュを返すようにしました。議事録の作り直しや追加質問で何度 Claude に話しかけても、AmiVoice を再実行しません。

```
// 2回目以降はキャッシュを返す（文字起こし枠を消費しない）
if (rec.transcript_speakers) {
  return Response.json({ ...rec.transcript_speakers, cached: true })
}
```

### `speaker0` に名前をつける（GUIでもAIでも）

`speaker0` `speaker1` のままでは議事録として読みにくい。そこで**話者ラベルに任意の表示名を割り当てて保存**できるようにしました。データは録音ごとに `speaker_names` として持ちます。

```
{ "speaker0": "田中", "speaker1": "山田", "speaker2": "佐藤" }
```

付け方は2通り。

* **GUI**: 各話者の名前入力欄に「田中」と打てば即保存。以降、発話ターンも「田中」表示になり、ワンクリックで議事録テキストとしてコピーできます。
* **AI（MCP）**: `set_speaker_names` ツールで Claude が命名します。面白いのは、**Claude が会話の中身から話者を推測して名前を当てられる**ことです。

```
ユーザー: speaker1 が自己紹介で「山田です」って言ってたから、それで名前つけといて

Claude: set_speaker_names を実行します...
        speaker1 → 山田 として保存しました。
```

「声で誰かを区切る（AmiVoice）」と「文脈で誰かを当てる（Claude）」の役割分担が、ここでもきれいに噛み合います。

```
// 話者名を保存するMCPツール
server.tool(
  "set_speaker_names",
  "話者ラベル（speaker0/1...）に任意の表示名を割り当てる。" +
  "transcribe_with_speakers の結果から話者を特定して命名する。",
  { recording_id: z.string(), names: z.record(z.string()) },
  async ({ recording_id, names }) => {
    const data = await api(`/api/recordings/${recording_id}/speakers`, {
      method: "PATCH", body: JSON.stringify({ names }),
    });
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);
```

---

## 複数人ポッドキャストでこれが効く理由

最後に、この機能が**複数人ポッドキャスト**にとってなぜ重要かを整理します。

1. **話者別の文字起こしがそのまま「台本／議事録」になる**  
   収録後の「文字起こし→誰の発言か手で振り分け」という最も面倒な工程が消えます。
2. **話者ごとの発話時間が出せる**  
   「司会がしゃべりすぎ」「ゲストの出番が少ない」を定量的に把握でき、次回の構成改善に使えます。
3. **概要欄・タイムスタンプ・チャプターを話者単位で自動生成できる**  
   生成AIに渡せば「この話題は誰が・何分から話したか」付きのショーノートが作れます。
4. **「ゲストAの発言だけ切り出して」が一言でできる**  
   話者ラベルがあるからこそ、特定話者の抽出・要約・引用が自然言語の指示で完結します。

ソロ収録ではここまでの恩恵はありません。**複数人で録るからこそ、話者分離 × 生成AI が編集体験を一段変える**——というのが今回の主張です。

### そして、これは「切り抜き（ショート）」の土台になる

発話ターンが `{ speaker, text, start, end }` という構造で取れている、という点が次の一手につながります。これはそのまま**切り抜き動画・ショート生成の素材**です。

* 「山田さんが一番盛り上がった30秒を切り抜いて」→ 話者と時刻が分かるので区間を特定できる
* 生成AIに「バズりそうな発言トップ3を選んで」と頼めば、`start`/`end` 付きで候補が返る
* あとはその区間を切り出すだけ（音声カットはすでに実装済み）

つまり今回の「話者分離＋命名」は、**収録 → 話者つき文字起こし → AIがハイライト選定 → ショート自動生成**という流れの最初のピースです。「誰が・いつ・何を」を構造化できたからこそ、その先が一気に現実的になります。

---

## まとめ

* AmiVoice の **話者ダイアライゼーション（非同期API・`speakerDiarization=True`）** で「誰がいつ話したか」を自動判別
* トークンの `label` を**発話ターンに束ねて**構造化
* **GUIのワンクリック**でも **Claude（MCP）への一言**でも実行できる
* `speaker0` に**任意の名前を付けて保存**（GUIで手入力 / AIが文脈から命名）
* それを生成AIに渡し、議事録・話者別要約・発話時間集計を生成
* 結果はキャッシュして認識枠を節約
* 構造化された発話ターンは、次の **「ショート（切り抜き）自動生成」の土台**になる

話者分離は万能ではなく、同時発話などでラベルがぶれることもあります。それでも「話者が交代で話す」ポッドキャストとは相性が良く、**ぶれは人やAIが後工程で直せる**前提に立てば、複数人収録の後処理はかなり軽くなります。日本語の話し言葉に強いエンジンが話者分離まで持っていることが、日本語ポッドキャストにとって実用的に効く、というのが使ってみての実感です。

[PodVoice](https://www.podvoice.jp) では、Claude に「3人で録ったやつを議事録にして」と話しかけるだけで、ここまでの処理が裏で全部走ります。複数人で収録している方はぜひ試してみてください。

---

## 参考
