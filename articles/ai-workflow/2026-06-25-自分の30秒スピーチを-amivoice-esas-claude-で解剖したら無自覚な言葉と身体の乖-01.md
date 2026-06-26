---
id: "2026-06-25-自分の30秒スピーチを-amivoice-esas-claude-で解剖したら無自覚な言葉と身体の乖-01"
title: "自分の30秒スピーチを AmiVoice ESAS × Claude で解剖したら、無自覚な「言葉と身体の乖離」が出てきた"
url: "https://zenn.dev/kenimo49/articles/amivoice-esas-claude-self-speech-analysis"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "Python", "zenn"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

> Zennfes Spring 2026「音声認識AmiVoice APIと生成AIで作る音声体験」テーマへの参加記事です。実装した [speech-habit-lens](https://github.com/kenimo49/speech-habit-lens)（MIT, OSS）の自己 dogfooding 体験記として書いています。

![AmiVoice ESAS × Claude の三層解析: 音響層・テキスト層・クロス層](https://static.zenn.studio/user-upload/deployed-images/d8197bfac08dd1ab3f578e5b.png?sha=4187373dd4faa6e238ad4745608e8bafa1835442)

## なぜ自分の声を可視化したかったか

プレゼン前に自分のスピーチを録音して聞き返したことのある人は多いと思います。私もよくやります。問題は、聞き返しても **「なんかパッとしないな」止まり** で、何がパッとしないのかが言葉にならないことでした。

* 結論はちゃんと言ったはずなのに弱く聞こえる
* 「自分は流暢に話せている」自己評価とは裏腹に、聞き手から「もう少し熱量がほしい」と言われる
* 直したい癖が「ある気がする」のに特定できない

主観の聞き返しでは限界があるな、と思いつつ放置していたところに [Zennfes Spring 2026](https://zenn.dev/events/zennfes-spring-2026) の AmiVoice テーマが告知されて、ちょうど API を触る理由ができた。「自分の声を解剖するツールを作って自分にぶつけてみる」をテーマに、`speech-habit-lens` を作りました。

## 3行で何を作って何が見えたか

* 1分前後のスピーチを `.wav` で投げると、**AmiVoice ESAS（感情20パラメータの時系列）× Claude の三層解析**で「身体と言葉の連動パターン」が見える CLI + Streamlit UI
* 私自身の31秒スピーチ（1分間トークについての雑談）を投げたら、**締め句で「元気なイメージ」と言った瞬間に `stress=46`（最大値）と `energy=3`（最小値）が同時に出る**、という「言葉の内容と音響的な身体信号が真逆」の乖離が定量的に出てきた
* リポジトリは [`kenimo49/speech-habit-lens`](https://github.com/kenimo49/speech-habit-lens)（MIT）。AmiVoice API key と Anthropic API key があれば手元で動きます

---

## AmiVoice ESAS の凄み — 言語非依存の感情20パラメータ

このツールの核は AmiVoice API の **ESAS（Emotional Signature Analysis Solution）** です。イスラエルの Nemesysco 社が開発した音声分析エンジン LVA7 をベースに、ES Japan が日本向けにチューニングしたもので、AmiVoice の非同期 HTTP v1 リクエストに `sentimentAnalysis=True` を1個追加するだけで使えます。

```
curl https://acp-api-async.amivoice.com/v1/recognitions \
  -F u=$AMIVOICE_API_KEY \
  -F d='grammarFileNames=-a-general sentimentAnalysis=True' \
  -F a=@speech.wav
```

これで認識結果と一緒に、**約2秒間隔で20種類の感情・認知パラメータ**の時系列が `sentiment_analysis.segments[]` として返ってきます。

### 公式 doc の罠: display name と実フィールド名が違う

公式 doc の [Sentiment Analysis ページ](https://docs.amivoice.com/en/amivoice-api/manual/sentiment-analysis/) には 20 パラメータ全部の **display name + 値域 + 値の傾向（positive / negative / -）** が表で公開されています。一見親切なんですが、**API レスポンスに実際入ってくる JSON のフィールド名は別物**です。しかも一部、display name から推測できないものが混じっています:

| 公式 doc の display name (EN) | 実 API レスポンスのフィールド名 |
| --- | --- |
| Energy | `energy` |
| Emotional Balanced Logical | `emo_cog` |
| Brain Activity | `brain_power` |
| Aggression Anger | `aggression` |
| Atmosphere Conversation Trend | `atmosphere` |
| **Joy**(EN display) ／ **喜び**(JA display) | `content` ← 推測不能 |
| **Agitation**(EN display) ／ **動揺**(JA display) | `upset` ← 推測不能 |
| **Confusion**(EN display) ／ **困惑**(JA display) | `embarrassment` ← 推測不能 |

下3行が特に厄介で、display name から JSON フィールド名は機械的に導出できません。display name と JSON フィールド名の対応表は、**別 API** (`GET https://acp-dsrpp.amivoice.com/v1/sentiment-analysis/ja/result-parameters.json` に Bearer トークンを付けて叩く) を呼ぶと、20 件すべての `name` / `display_name` / `minimum` / `maximum` が JSON で返ってきます。本ツールでは初期実装時の実 API レスポンスから 20 フィールド名を抽出し、後日この `result-parameters.json` で完全一致を再確認しました:

```
energy, content, upset, aggression, stress, uncertainty,
excitement, concentration, emo_cog, hesitation, brain_power,
embarrassment, intensive_thinking, imagination_activity,
extreme_emotion, passionate, atmosphere, anticipation,
dissatisfaction, confidence
```

値域もパラメータごとにバラバラで、**`Energy / Stress / Concentration / Thinking / Brain Activity` などは 0-100、`Passion / Joy / Hesitation` などは 0-30、`Emotional Balanced Logical (emo_cog)` は 1-500、`Atmosphere` は -100~100** と分かれています。`emo_cog` の 1-500 を 0-100 のつもりで Claude に渡すと「異常値だ」と誤判定するので、プロンプト側に値域を明記してハルシネーション抑制しています。

![ESAS 20 パラメータの値域分類: 0-100 / 0-30 / 1-500 / -100~100 の4グループ](https://static.zenn.studio/user-upload/deployed-images/62840a70b884406caacd0368.png?sha=27d515cee1bc89f637eb3e7dd538f564c608a2bc)

### 一番おもしろいのは「言語非依存」なこと

ESAS が個人的に一番好きなところは、**認識テキストが誤認識まみれでも ESAS は鋭く出る**ことです。たとえば Stallman の英語講演を `-a-general`（日本語エンジン）で無理矢理通すと、テキストは「カタカナまみれの謎言語」になりますが、ESAS の `concentration` peak / `passionate` peak / `anticipation` の立ち上がりは、英語話者が聞いた時の印象と一致する形で出てきます。

つまり「言葉が分からなくても、声の癖は分かる」。これが他の音響分析 API と差別化される一番の利点だと感じました。日本語エンジンが英語をカタカナで誤認識しても、英語話者がドギマギしている事実だけは数値の側からきれいに漏れてきます。

## 三層解析の設計

ESAS だけだと数値の羅列で、テキストだけだと「結論が中盤に来てフィラーが多い」止まり。両方を交差させて初めて **「結論キーワードを言う瞬間に concentration が落ちる」** のような身体 × 言葉の連動が見えます。

| 層 | 入力 | 抽出する癖 |
| --- | --- | --- |
| **音響層** | ESAS 20 パラメータ時系列 | テンション推移、抑揚の偏り、出だしのエネルギー、終端の失速 |
| **テキスト層** | 認識テキスト + セグメント | フィラー、結論位置、繰り返し語、論理展開 |
| **クロス層 ⭐** | 上記2層の出力 + 元データ | 「結論手前で声量が落ちる」等の身体×言語連動 |

各層を Claude（Sonnet 4.6）に独立したプロンプトとして投げて、JSON で返してもらいます。クロス層プロンプトには「**Grounding Rule（絶対遵守）**」を入れて、**時刻 + ESAS パラメータ + テキスト引用の3点セットを根拠としない発見は禁止**しました。

```
## Grounding Rule（絶対遵守）

- すべてのパターンは **時刻 + ESAS パラメータ + テキスト引用** の3点で根拠付けすること
- 入力にない時刻・引用を捏造しない
- 改善提案は必ず1つ以上のパターンを参照すること（独立した一般論は禁止）
- 「もっと自信を持って」「ゆっくり話して」等の **データに紐付かない一般的アドバイスは禁止**
```

これを入れる前は Claude が **「全体的に落ち着いて話せている印象」みたいな"占い"を返してくる**ことがあったので、グラウンディング条件をプロンプトに明示するのは効きました。クロス層は最大3パターンに絞らせて、5個書くと薄まることも明記しています。

## 自分の31秒スピーチを投げた結果

ここからが本題。私が「1分間トーク」について自由に話す約31秒を録音して、Streamlit UI（`shl serve`）から投げました。AmiVoice で認識 + ESAS パース + Claude × 3層解析で**約3分**かかります。

### テキスト層が拾ったもの

```
{
  "fillers": [{"word": "ですね", "count": 3}],
  "conclusion_position": {
    "zone": "middle",
    "evidence_second": 9.8,
    "main_claim": "1分間トークはですね、ただの雑談ではないと思っておりまして、その人が何を考えているかとか、その人の自己紹介も兼ねてやるものだなと思っております。"
  },
  "opening_hook": "挨拶＋状況提示 — 「おはようございます。今日の天気は晴れですね。」",
  "closing_landing": "聴衆への問いかけ — 「そういう元気なイメージを出してみたんですが、いかがでしょうか？」"
}
```

ここで一発、自覚と数値がズレました。

* 自覚: 「自分は『えーと』『あの』みたいなフィラーはあまり言わない」
* データ: **「ですね」を3回、機能的フィラーとして使用**

「ですね」は終助詞でフィラーではない、という主張も成立しますが、**意味的な情報を持たず文末を埋める用途で連続使用**されているなら、機能的にはフィラーです。AmiVoice の認識テキストとセグメント情報があれば、Claude が「『ですね』の出現位置と前後の文脈から、結論的な使われ方かフィラー的な使われ方か」を判別できました。

そしてもう1つ気づいたのは、**自分は「結論先出し型」だと思っていたのに、実際の結論位置は middle (9.8s)** だったこと。前置きで状況提示してから主張に入るタイプで、自己評価とは違いました。

### 音響層が拾ったもの

* **冒頭 (0-5s)**: `intensive_thinking=57` + `concentration=53` が支配的 — 発話開始前から強い内的思考状態
* **終端 (28.5-31.5s)**: `stress=46`（全サンプル最高値）と `concentration=100` が同時に最高値 — 高緊張下での強制集中で締め
* **全域**: `energy` は16サンプル全部で max=10 / min=2、ほぼ全域で 2〜5 に固定 → 声の出力が一貫して低水準
* **全域**: `content=0` が全サンプル、`passionate=0` が14サンプル、`atmosphere / dissatisfaction / aggression` も全域0 → 感情的彩りが音声からほぼ排除

つまり開幕から終端まで「内的思考は強いがエネルギーは出ていない」状態で、終盤に向かってストレスだけが急騰しています。

### クロス層が拾った3つの指摘

```
## クロス層 ⭐

### #1 主張直前に思考が内向する
- 時刻: 4.62s
- ESAS: intensive_thinking = 36
- 引用: 「今日はですね天気の話がしたいわけじゃないんですけど、どっちかというと、」
- 意味: 核心主張への移行点で intensive_thinking が高止まりし、言葉が
  内部処理に追われている。聴衆に届く前に思考が内側に閉じている状態。

### #2 締め句でストレス最高・声量最低
- 時刻: 28.48s
- ESAS: stress = 46（最大値）, energy = 3
- 引用: 「そういう元気なイメージを出してみたんですが、いかがでしょうか？」
- 意味: 「元気なイメージ」と語る瞬間に stress=46・energy=3 が同時記録
  され、言葉の内容と身体状態が真逆に乖離している。

### #3 hesitation と「ですね」の同期
- 時刻: 6.62s
- ESAS: hesitation = 16
- 引用: 「1分間トークはですね、ただの雑談ではないと思っておりまして」
- 意味: 主張を立てる場面で hesitation=16 と「ですね」が重なり、断言を
  避ける言語習慣と音響上のためらいが連動して自信を削いでいる。
```

![クロス層が拾った3パターン: #1 主張直前に思考が内向（intensive_thinking=36 @ 4.62s）/ #2 締め句で stress 最大・energy 最小（stress=46, energy=3 @ 28.48s）/ #3 hesitation と「ですね」の同期（hesitation=16 @ 6.62s）](https://static.zenn.studio/user-upload/deployed-images/c373dd39c2e9a1ee9c54be93.png?sha=0704fad5f3d59d8715393fb776b3bb6816b8d114)

#2 が一番痛いです。私は「元気なイメージ出したい」と**口で言いながら、音響的な身体信号は真逆の状態**になっていた。これは録音を耳で聞き返しても気づけない指摘でした。「元気そうに聞こえなかったのは、本当に声の出方が元気じゃなかったから」という、当たり前のようで耳では捉えられないズレが、ESAS と引用テキストを Claude が交差させて初めて言語化されました。

![28.48s で stress=46（最大）と energy=3（最小）が同時に出るタイムライン](https://static.zenn.studio/user-upload/deployed-images/184934e9f28fd75da2c1c668.png?sha=5b6f9a1f439a3c976131da8fa6791f1709e39d4a)

### 改善提案（grounded）

```
## 改善提案

1. 主張の冒頭文（「1分間トークはただの雑談ではない」）を事前に
   一言で言い切る練習を繰り返し、移行直前の内部処理を発話前に完結
   させる。
   - 根拠: 主張直前に思考が内向する
2. 締めの「いかがでしょうか？」を発する直前に意図的に声量を上げる
   動作（例：姿勢を起こす）をルーティン化し、stress 急騰時の energy
   低下を身体で打ち消す。
   - 根拠: 締め句でストレス最高・声量最低
```

「もっと自信を持って」みたいな曖昧な助言ではなく、**「28.48s で何が起きたか」に紐付いた具体的行動**として返ってきます。Grounding Rule の効果がここで出ました。

## 数値が自覚を上回った瞬間

自分の声に対して「結論先出し型」「流暢」「元気なイメージ出せている」だと思っていた自己評価が、ESAS × Claude を交差させた瞬間に **「中盤に結論を置く前置き型」**「**ですね機能フィラー多用**」「**口では元気でも身体は真逆**」に上書きされました。

聞き返すだけでは届かない理由が、書き出してみるとシンプルでした。

* **耳で聞き返す**: そのスピーチの絶対値しか見えない（うまかった/下手だった）
* **ESAS で計測する**: パラメータの時系列が見える（どこで何が起きたか）
* **Claude でクロスする**: 「ある瞬間に何と何が同時に起きたか」が言語化される

最後の「クロス」だけが、**自覚と外部観察のあいだの解像度のギャップ**を埋めてくれます。ESAS 単体でも Claude 単体でも届かなかったゾーンで、両方を 1 つのプロンプト境界の中で交差させる必然性は、実装してみて初めて納得しました（数値で殴られないと癖は更新できないタイプの人間だった、ということでもあります）。

## ハマった3つの罠

実装中に踏んで一番時間を吸われた罠を3つだけ共有します。Zennfes 参加者で AmiVoice を Streamlit に組み込む人がもしいたら、最初に読んでおくと丸1時間助かるかもしれません。

### 罠1: Chrome の既定マイクが「無音デバイス」を掴むことがある

Streamlit を `st.audio_input` で組んで「録音できているはずなのに無音」になる現象を踏みました。原因は Chrome の入力デバイスが HDMI キャプチャカード（Display capture-UVC03）を「マイク」として認識して、それを既定にしていたこと。録音は成功して bytes は返ってくるのに、**Opus 5秒で 110 bytes（= 完全無音）** という値で判別可能。

`navigator.mediaDevices.enumerateDevices()` で `audioinput` を列挙して、AnalyserNode で RMS をリアルタイム測定するデバッグパネルを `st.components.v1.html` で組み込みました。`st.audio_input` 側からはデバイス指定できない（別 iframe で外から指定不可）ので、最終的にはユーザーに `chrome://settings/content/microphone` で既定マイクを切り替えてもらう案内をUI に出す形に落ち着きました。

### 罠2: Claude の JSON 出力に末尾の Markdown 補足が混じる

プロンプトで「**JSONのみ返してください**」と明示しても、Claude（Sonnet 4.6）が

```
```json
{ ... }
```

補足: このスピーチは前向きな印象でした...
```

みたいに、JSON の後に**補足の地の文 Markdown** を付けてくることがあります。先頭の fence（```` ```json ````）は剥がせても末尾の補足は剥がしにくいので、`json.loads()` だと `Extra data: line 15 column 1` で死にます。

解決は `json.JSONDecoder().raw_decode()` に切り替えること。これは **先頭から JSON を読んで、有効な終端位置を返し、それ以降の余分テキストを無視**します。

```
def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.lstrip("\n")
    decoder = json.JSONDecoder()
    obj, _end = decoder.raw_decode(text)
    return obj
```

`raw_decode` は本来「JSON のあとに何があるか分からないストリーミング用途」のために用意されているので、こういう「LLM が末尾に何かくっつけてくる」シナリオにきれいに刺さります。

### 罠3: Streamlit のブラウザ録音は secure context 必須

Tailscale 経由で `http://100.x.x.x:8501` に Windows から接続して開発していたところ、`navigator.mediaDevices.getUserMedia` が `undefined` で死ぬ現象を踏みました。原因は **HTTP + hostname が secure context として認められない**こと（localhost は例外）。

Chrome なら `chrome://flags/#unsafely-treat-insecure-origin-as-secure` に origin を追加して Enable + 再起動で開発時は回避できます。本番デプロイでは普通に HTTPS を当てれば終わる話ですが、開発時にこれ知らないと「マイク権限の問題か?」「コードのバグか?」を切り分けるのにかなり時間使います。

## まとめ + クーポンの案内

実装してみて、**ESAS の値そのものより、ESAS とテキストを交差させた瞬間に何が言語化されるか**の方が圧倒的に価値があると感じました（自分を解剖した結果が想定外に痛かったので、余計にそう思います）。AmiVoice の音声認識精度はテキスト面で十分強いのですが、ESAS という「もう一軸」が同じレスポンスで返ってくる構造があってこそ、生成 AI 側でクロス層が組める。Whisper + 別途感情分析モデルを併用する構成でも近いことはできますが、**同一レスポンスで完結する**シンプルさは AmiVoice の強みです。

### Zennfes 2026 春クーポン

Zennfes Spring 2026 参加者向けに、AmiVoice 側から **月10時間まで無償の Trial クーポン**が配布されています（2026年5月・6月限定）。AmiVoice マイページで以下のコードを適用すると、無料枠が月60分 → 月10時間に拡大します。

普通に使うと1解析で30〜90秒の音声を投げるので、月60分だと検証 40〜60 回くらいで枠を使い切ります。Trial クーポンで一気に **月 600 回相当** まで枠が増えるので、Streamlit UI でガチャガチャ試行錯誤するなら適用しておくと良いです（取得手順は[公式マイページ](https://acp.amivoice.com/)から）。

### OSS として公開しています

[`kenimo49/speech-habit-lens`](https://github.com/kenimo49/speech-habit-lens) (MIT) で公開しています。`pip install -e .` でインストールして、`.env` に `AMIVOICE_API_KEY` と `ANTHROPIC_API_KEY` を入れれば、`shl analyze your_speech.wav` または `shl serve` で動きます。

```
git clone https://github.com/kenimo49/speech-habit-lens
cd speech-habit-lens
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # API key を記入
shl serve             # http://localhost:8501
```

`shl serve` の「録音」タブを使う場合は **`ffmpeg` が PATH に必要**です（録音 bytes を AmiVoice 仕様 16kHz/mono/16-bit PCM WAV に変換するため）。既存 WAV のアップロード解析のみであれば不要です。

自分のスピーチを解剖する体験、地味におすすめです。**自覚と数値がズレた瞬間にだけ、自分の癖は更新される**ので。…裏を返せば、聞き返すだけで気づける人にはこのツール要りません。要る側だった、というのが私の dogfooding の結論です。

---

**この記事は Zennfes Spring 2026「音声認識AmiVoice APIと生成AIで作る音声体験」テーマに参加しています。**
