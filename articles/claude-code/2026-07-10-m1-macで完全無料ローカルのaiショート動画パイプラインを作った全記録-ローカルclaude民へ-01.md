---
id: "2026-07-10-m1-macで完全無料ローカルのaiショート動画パイプラインを作った全記録-ローカルclaude民へ-01"
title: "M1 Macで完全無料・ローカルのAIショート動画パイプラインを作った全記録 — ローカルClaude民へ"
url: "https://zenn.dev/umamon/articles/df7a862c4a944e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "LLM", "Python", "zenn"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

> 課金ゼロ・外部送信ゼロ。SDXLでキーフレームを描き、LTX-2.3 (MLX) で"本物の動き"を付け、Kokoro TTSでナレーション、MusicGenでBGM、ffmpegで焼き上げる。全部このM1 Max 64GBの中で完結させた実録と、そのまま真似できる再現レシピです。
>
> 読者は **Claude Code ユーザー、ローカルでClaude/LLMを回しているApple Silicon勢**。詰まった話（失敗談）ほど価値がある、という方針でハマりどころを全部書きました。

---

## TL;DR（先に結論）

* **「静止画をズーム/パンしただけ（Ken Burns）」は動画じゃない。紙芝居です。** 本物の動きは **I2V（Image-to-Video）** でしか作れない。ここを最初に握れなかったのが最大の失敗でした。
* スタックは全部無料ローカル: **SDXL(ComfyUI) キーフレーム → LTX-2.3 (MLX) で I2V → Kokoro TTS ナレ → MusicGen BGM → ffmpeg 合成**。
* ハマりどころの本丸は **Metal GPUウォッチドッグ・クラッシュ（MLX issue #3267）**。旧パッケージは画面表示中に即死したが、新しい `dgrauet/ltx-2-mlx`(q8) は**画面ONのまま完走**する、という顛末が一番の学び。
* 環境構築で99%詰むのは **arm64 Python** と **transformersのバージョン固定** の2点。

---

## 1. きっかけ：「これはただの紙芝居です」

最初の納品は、一発で却下されました。

SDXLで綺麗な静止画を10枚作り、ffmpegの `zoompan`（Ken Burns効果、寄り/引き）でそれっぽく動かし、ナレーションと字幕を乗せて「動画です」と出した。返ってきた言葉はこうです。

> 「思ってたのと違う。これはただの紙芝居。紙芝居じゃなくて動画です。」

刺さりました。骨に刻んだ教訓はこれです。

1. **"動画（ムービー）" とは、キャラ・水・光が実際に動くこと。** 静止画のズーム/パンは動画ではない。ここを絶対に混同しない。
2. **納品物の定義を先に握る。** 「無料で早く」を優先して、相手が本当に欲しいもの（本物の動き）を犠牲にしない。安く早く出しても、違うものなら価値ゼロで作り直し。
3. **本物の動きには I2V が必須。** 静止画パイプラインは"絵コンテ/プレビュー"までしか作れない。
4. ただし **Ken Burns を捨てはしない**。ナレ尺合わせの絵コンテ確認や、動かす必要のない締めカットには有効。**でもそれを"完成"とは呼ばない。**

この一発却下が、全部の出発点でした。

![左：静止画をズームしただけの紙芝居／右：I2Vで生成した本物の動き](https://static.zenn.studio/user-upload/04140f79f72e-20260710.gif)  
*実物で比較：左＝却下された「紙芝居」（静止画をズームしただけ）／右＝同じキーフレームからLTX-2.3(I2V)で生成した"本物の動き"。水面とゴンドラが実際に動いているのが右です。*

---

## 2. ゴール：本物の動き＝I2V を、ローカル無料で回す

やることはシンプルです。**各カットの起点になる静止画（キーフレーム）を作り、それを I2V モデルに"動かして"もらう。** キーフレームはSDXL、動かすのは LTX-2.3 の MLX 移植。全部このMacの中で回ります。

全体像はこの順番です。

![完全無料・ローカルAI動画パイプライン全体図](https://static.zenn.studio/user-upload/f2f760bf508c-20260710.png)  
*図1: パイプライン全体図。I2V（LTX-2.3）が"動画の本体"*

| 段 | 工程 | ツール | 位置づけ |
| --- | --- | --- | --- |
| A | 絵コンテ＋ナレ台本 | ローカルLLM（gemma-3-12b-it・mlx\_lm） | 設計 |
| B | キーフレーム静止画 | ComfyUI / SDXL(realcartoon-xl) | 各カットの起点画像 |
| C | ナレ音声＋実尺確定 | Kokoro TTS（or macOS `say`）＋`ffprobe` | 無料・尺確定 |
| D | **I2V＝キーフレームを"動かす"** | **LTX-2.3 MLX** | **ここが"動画"の本体。省略不可** |
| E | 合成（連結＋ナレ＋字幕＋BGM） | ffmpeg | 仕上げ |
| （プレビュー用） | Ken Burns | ffmpeg zoompan | 確認用のみ。完成ではない |

---

## 3. スタック（全部無料・全部ローカル）

* **キーフレーム**: ComfyUI + `realcartoon-xl-v4`（SDXL系）。REST API（`:8000`）を叩いてバッチ生成。
* **I2V（動画本体）**: LTX-2.3 の MLX 移植。用途に応じて2系統を使い分け（後述）。
  + 下書き＝`notapalindrome/ltx23-mlx-av-q4`（20GB・蒸留q4・速い）
  + 本番＝`dgrauet/ltx-2.3-mlx-q8`（21GB・`--two-stages-hq`＋STG・高精細）
* **テキストエンコーダ / 台本LLM**: `mlx-community/gemma-3-12b-it-4bit`（約7GB）。
* **ナレ**: Kokoro TTS（`mlx-audio`）。macOS標準の `say` でも動く。
* **BGM**: MusicGen（`transformers` 内蔵の `MusicgenForConditionalGeneration`）。
* **合成**: ffmpeg（Homebrew版・ただし後述の落とし穴あり）。

ハードは **M1 Max / 64GB** です。この「64GBの現実」がモデル選定を縛ります。

---

## 4. 環境構築でだいたい詰む（ここが本命の2点）

正直、動画生成そのものより **環境構築で99%詰みます**。踏んだ地雷は2つ。

### ① arm64 の Python を使う（Anacondaで死ぬ）

Anaconda等の Python は x86\_64（Rosetta）で走っていることがあり、その場合 `mlx` が入りません（`no matching distribution` で弾かれる）。**必ず arm64 ネイティブの Python** で venv を切ります。

```
# arm64 python でvenvを作る（Anacondaのx86_64を掴ませない）
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m venv ~/ltx-mlx
~/ltx-mlx/bin/pip install -U mlx-video-with-audio
```

新パッケージ側（`dgrauet/ltx-2-mlx`）は `uv` を使いますが、**uv も初期に x86\_64 の anaconda python を掴んでしまい mlx が入らない**ことがあるので、arm64 python を明示指定します。

```
git clone --depth 1 https://github.com/dgrauet/ltx-2-mlx.git ~/ltx-2-mlx
cd ~/ltx-2-mlx
uv sync --all-extras --python /Library/Frameworks/Python.framework/Versions/3.11/bin/python3
```

### ② transformers を `>=4.50,<5` に固定する

`pip install mlx-video-with-audio` は transformers 5.13 を引き込みますが、これが `mlx_lm` の tokenizer 登録をクラッシュさせます（`AttributeError: 'str' object has no attribute '__module__'`）。**バージョンを落として固定**すれば通ります（4.57.6 で実行時OK。pipは依存警告を出しますが挙動は通る）。

```
~/ltx-mlx/bin/pip install "transformers>=4.50,<5"   # ← これが必須の固定
```

この2つを踏み抜くと「なぜか mlx が入らない」「起動時に謎の AttributeError」で数時間溶けます。先に潰しておいてください。

---

## 5. モデル選択と「64GBの現実」

LTX-2.3 のフル精度モデルは**単一で53.5GB**あり、64GBだとロードで OOM / 激重スワップになります。**使わない。** 量子化版で回すのが定石です。

| 目的 | モデル / 設定 | 実測の速度感 |
| --- | --- | --- |
| 速さ優先・下書き | 蒸留q4（`ltx23-mlx-av-q4` / `--distilled`） | 約4分/クリップ・ピーク約14.7GB |
| 品質優先・本番 | **q8 `--two-stages-hq` ＋ STG** | **約30分/クリップ**・ピーク約21GB |
| 格闘/激しい動き | q8 HQ ＋ `--stg-scale 1.0` ＋ モーションLoRA | 30分＋α |

HQの内訳は、1024×576・97フレームで **1クリップ約30分（1774秒）**。うち Stage1 が24分（15ステップ × 約95秒）です。蒸留q4（約4分）の約7.5倍かかりますが、レンガや水面、輪郭がはっきりと高精細になります。**下書きはq4で速く回し、通ったら本番だけq8で焼く** のが現実解でした。

![LTX-2.3モデルの使い分け（q4下書き／q8本番／LoRA）](https://static.zenn.studio/user-upload/73a233579865-20260710.png)  
*図2: 64GBの現実の中でのモデル使い分け*

---

## 6. 再現レシピ（実際に回したコマンド）

### ① 台本（ローカルLLM・完全自走）

`mlx_lm` + `gemma-3-12b-it-4bit` で、カット割り＋各カットの映像プロンプト＋ナレをまとめて生成します。

```
"$PY/mlx_lm.generate" --model mlx-community/gemma-3-12b-it-4bit \
  --max-tokens 1100 --temp 0.75 --prompt "$PROMPT" \
  | sed '/^==========/d' > script.md
```

プロンプト側で「最初の3秒で強いフック」「映像プロンプトは英語で人物/場所/光/動きを具体的に」「憶測の数字・誇張・保証表現は書かない」を縛っています。

### ② キーフレーム（ComfyUI / SDXL）

ComfyUIのREST（`:8000`）へグラフをPOSTして静止画を得ます。サンプラーは `dpmpp_2m` / `karras` / steps 30 / cfg 6.5。

```
"3": {"class_type": "KSampler", "inputs": {
    "seed": seed, "steps": 30, "cfg": 6.5,
    "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0,
    ...}}
```

**キャラ一貫性が生命線**なので、主要人物の固定設計文を全プロンプトで使い回します。SDXLは人数を勝手に増やしがちなので、ネガに `three people, group` を入れて抑えるのがコツ。

![SDXLで実際に生成したキーフレーム（運河の夕景・cut01起点）](https://static.zenn.studio/user-upload/2f4cac5a33a4-20260710.jpg)  
*ComfyUI/SDXLで実際に生成したキーフレーム（cut01の起点画像）*

![SDXLキーフレーム（給仕シーン・3回リテイクしたv3）](https://static.zenn.studio/user-upload/4ccd1f6b0d33-20260710.jpg)  
*キャラ固定設計文で人物の一貫性を保ったキーフレーム（cut07・リテイク3回目のv3）*

### ③ I2V（動画本体・LTX-2.3）

**下書き＝q4**（1カット約4分）。単独実行＋`caffeinate`でスリープ抑止。

```
caffeinate -i -s ~/ltx-mlx/bin/python -m mlx_video.generate_av \
  --model-repo notapalindrome/ltx23-mlx-av-q4 \
  --text-encoder-repo mlx-community/gemma-3-12b-it-4bit \
  --image kf.png --prompt "動きの描写, cinematic film footage, natural gentle motion, warm golden light" \
  --negative-prompt "static, morphing, warping, extra fingers, flicker, jitter, low quality" \
  -W 1024 -H 576 --num-frames 65 --fps 24 --no-audio \
  --output-path cut.mp4
```

**本番＝q8 HQ**（1カット約30分・高精細）。

```
/Users/yuma/ltx-2-mlx/.venv/bin/ltx-2-mlx generate \
  --model dgrauet/ltx-2.3-mlx-q8 --two-stages-hq \
  --image keyframe.png 0 1.0 \
  --prompt "動きの描写, cinematic film, natural motion, warm golden light" \
  --frames 97 --frame-rate 24 -H 576 -W 1024 \
  --stg-scale 1.0 --cfg-scale 4.0 --seed 42 \
  --output cut.mp4
```

![LTX-2.3で実際に生成したカット（GIF変換）](https://static.zenn.studio/user-upload/a8c64c599993-20260710.gif)  
*上のパイプラインで実際に生成されたカット（記事用にGIF化＝画質/fpsは落としてあります。実物は1024×576・24fps・音声付き）*

要点メモ:

* 解像度は **64の倍数**（1024×576 推奨＝真16:9）。縦型Shortsにするなら `-H 1024 -W 576`。
* num-frames は **8n+1**（q4系は最大97）。蒸留モデルは `--steps` を無視（8+3固定）。
* `--no-audio` でモデル生成の音を外し、自前のナレを後合成する（教材用途はこれ）。
* `--image PATH FRAME STRENGTH` で **両端フレームをアンカー**でき、長い連続モーションを補間できる。

### ④ ナレ（Kokoro TTS）

```
~/ltx-mlx/bin/python -m mlx_audio.tts.generate \
  --model mlx-community/Kokoro-82M-bf16 \
  --text "英文ナレーション" --voice bm_george --lang_code b \
  --output_path seg_01.wav
# 実尺取得: ffprobe -v error -show_entries format=duration -of csv=p=0 seg_01.wav
```

`pip install "misaki[en]"` が要ります。稀に特定の文で形状エラーが出たら、文を少し整えて再試行。**Kokoroは軽くGPUウォッチドッグを踏まない**ので、画面ONでも回せます。macOS標準の `say -v Daniel -r 165` でも一応いけます（無料・確実）。

### ⑤ BGM（MusicGen）

`audiocraft` は `av` / pkg-config のビルドで詰むので使わず、**transformers 内蔵の MusicGen** が正解でした。`facebook/musicgen-small` をCPUで（20秒に約4.6分）。

```
from transformers import AutoProcessor, MusicgenForConditionalGeneration
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
prompt = "warm gentle emotional cinematic film score, soft solo piano with tender strings, slow, heartfelt, in a major key"
audio = model.generate(**inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=1024)  # ~20s
```

20秒を acrossfade でループさせて尺に合わせ、`volume=0.30` で控えめにミックスします。

### ⑥ 合成（ffmpeg）

各カットを 1080p にアップスケール（lanczos＋軽グレード）、字幕を焼き、ナレを乗せ、10本を連結して最後にBGMを `amix`。ラウドネスは `loudnorm=I=-15` で整えます。字幕は**カット単位で焼く**とナレとズレません。

---

## 7. ハマりどころ全集（開発者への本命）

ここが一番共有したいところ。全部踏んだので、あなたは避けてください。

![Metal GPUウォッチドッグ・クラッシュの仕組みと新旧対策の逆転](https://static.zenn.studio/user-upload/d5a1f0b2e5f7-20260710.png)  
*図3: クラッシュの正体と、新パッケージによる前言撤回*

症状はこれ。

```
[METAL] Command buffer execution failed: Impacting Interactivity
(kIOGPUCommandBufferCallbackErrorImpactingInteractivity)
```

**「再起動後の最初のLTX 1本だけ成功、2本目以降が即死」** という不気味な挙動でした。

真因は MLX 公式 Issue #3267 で確定していて、**ディスプレイ表示中は WindowServer が GPU で画面を合成している → MLX の重いコマンドバッファがその合成を妨げると、macOSが"操作性を守るため"にプロセスを強制終了する**、というものです。ディスプレイON = 100%再現、OFF = 100%回避。

効かなかった対策:

* `caffeinate -i -s` … システムスリープは防ぐが**画面は消えない**ので無意味
* `pmset displaysleepnow` … 外部モニタが生きていると合成が継続してダメ
* ComfyUI停止 / `/free` … そもそも無関係

**旧パッケージ（`mlx-video-with-audio` の蒸留q4）** で確実に回す答えは、①Mac再起動でGPU hang後のドライバリークをクリア → ②外部モニタ電源OFF＋ノートのlidを閉じて表示ゼロ → ③その状態でLTXバッチを回す、でした。これで全10カットをクラッシュ0で完走。

**ところが、これは新パッケージで覆りました。** `dgrauet/ltx-2-mlx`(q8 HQ) は、**画面を点けっぱなしのまま cut を生成 → 30.8分・クラッシュ0・新規クラッシュレポートも無し**で完走したのです。つまり**昼間でも、人が画面を使いながら裏でHQバッチを流せる**。無人夜間バッチに縛られなくなりました。旧環境で「画面OFF必須」と結論していたのを、実測で撤回した形です（発熱は出るので通気だけ確保）。

### ★ Homebrew ffmpeg に libass が無い → 字幕が焼けない

Homebrew の ffmpeg は libass/freetype 無しビルドで、**`subtitles` フィルタも `drawtext` フィルタも存在しません**（`ffmpeg -filters | grep subtitles` が空なら該当）。SRTを作っても焼けない。

回避策は **Pillow で透過PNGに字幕を描画し、ffmpeg の `overlay` で焼く**こと。フォントは `/System/Library/Fonts/Supplemental/Arial Bold.ttf`。縁取り（stroke）を太め・濃くして、半透明の角丸プレートを敷くと読みやすくなります。

### ★ ブーメラン（逆再生ループ）アーティファクト

LTXは1本が約2.7〜4秒（97フレーム）。ナレが長いカットを「順再生＋逆再生（boomerang）」で尺埋めすると、"動いて戻る／飲み物を飲み戻す"ような**逆再生アーティファクト**が出ます（動きの採点で最大の減点要因）。

正解は **逆再生しない**。最終フレームをクローンで保持しつつ、緩いドリフトを足します。

```
tpad=stop_mode=clone:stop_duration=X   # 最終フレームをナレ実尺までクローン保持
zoompan=z='min(1.0+0.0006*on,1.11)':d=1:fps=24   # 気づかない程度のドリフト
```

もっと長い連続モーションが要るなら、**LTXを数珠つなぎ**（クリップの最終フレーム → 次のキーフレームで生成 → 連結）にします。

### ★ 4x-UltraSharp（ESRGAN）は Apple MPS で破綻する

高解像度化に ESRGAN 系（4x-UltraSharp）を使うと、Apple の MPS で**走査線状に画が破綻**します。使わない。4Kが要るなら **ffmpeg のクリーン拡大**（`scale=3840:2160:flags=lanczos` ＋ 軽い unsharp）で十分見られます。

### ★ scratchpad（/tmp）は揮発する

作業スクリプトを `/tmp` に置くと、再起動やクリーンで消えます。**重要なスクリプトは成果物フォルダに置く。** これは地味に効く教訓でした。

### ★ LoRAは「可能」だった（前言撤回）

最初は「LoRAは Wan 専用・LTX 非対応・無理筋」と結論していました。**これは誤りでした。** `dgrauet/ltx-2-mlx generate` の `--help` で対応を確認済みです。

* `--lora PATH STRENGTH` … 通常LoRA（モーション強化・速度LoRA等）
* `--distilled-lora` / `--distilled-lora-strength` … 蒸留（高速）用LoRA
* `--stg-scale` と `--lora` は併用可（per-block適用）

つまり **「LTX + 複数LoRA」路線は本物**。ComfyUI-PyTorch（torch破壊リスク大）に手を出さなくても、**MLXのCLIだけでLoRAが差せます**。格闘級の激しい動きは「q8 `--two-stages-hq` ＋ `--stg-scale 1.0` ＋ モーション系LoRA」が本線です。

---

## 8. 品質スコアの推移（正直な実録）

![品質スコアの推移（70→85・95点ゲート未達）](https://static.zenn.studio/user-upload/80cd326e88ef-20260710.png)  
*図4: 紙芝居からの正直な道のり*

この会社では、動画は**独立採点（作った本人は採点しない・別セッションが採点）で95点ゲート**という運用にしています。実際のスコアはこう推移しました。

```
v1 紙芝居 → 却下
 → Wan(I2V) 70
 → LTX キャラ統一 76 → 77
 → 全カット実LTX 78
 → ブーメラン全廃 81
 → +Kokoro / +MusicGen / 字幕プレート / -15 LUFS で 推定85
```

**紙芝居 → 本物の動画 → 無料のまま85前後**まで来ました。まだ95には届いていません（動きの伸び・尺合わせが天井）。ここは正直に書きます。次の一手は「LTX数珠つなぎ」と「HQ＋モーションLoRA」で90を狙う段階です。**"無料ローカルで完璧"ではなく、"無料ローカルでここまで来た"** が正確なところです。

---

## 9. 再現レシピ（最短手順まとめ）

1. **arm64 python で venv**（Anacondaのx86\_64を掴ませない）→ `mlx-video-with-audio` を入れ、`transformers>=4.50,<5` に固定。
2. **台本** … `mlx_lm.generate` + `gemma-3-12b-it-4bit` でカット割り＋映像プロンプト＋ナレを生成。
3. **キーフレーム** … ComfyUI(`:8000`) + `realcartoon-xl-v4`。キャラ固定設計文を全カットで統一、ネガで人数増殖を抑制。
4. **I2V** … 下書きは **q4**（`generate_av` / 約4分）、本番は **q8 `--two-stages-hq` ＋ STG**（約30分）。解像度は64の倍数、frames は 8n+1、`--no-audio`。
5. **ナレ** … Kokoro TTS（`mlx_audio` / `misaki[en]`）。`ffprobe` で実尺を取る。
6. **BGM** … transformers 内蔵 MusicGen（`facebook/musicgen-small`・CPU）。控えめに `volume=0.30`。
7. **合成** … ffmpeg で 1080p 化＋グレード、**字幕は Pillow透過PNG → overlay**（libass無し回避）、**逆再生禁止・clone hold＋drift**、最後に BGM を `amix` ＋ `loudnorm=I=-15`。
8. **重いGPU処理は時間をずらす**（同じMacで他の作業と衝突すると両方遅く/落ちる）。長尺は `caffeinate -i`＋通気確保。

---

## 10. ローカルでClaudeを回している仲間へ

最後に、同じように**ローカルでClaude/LLMを回している開発者**へメッセージとTipsを。

**課金しなくても、Apple Silicon一台でここまで作れます。** クラウドのI2V（Kling/Runway/Veo…）は綺麗で速いけれど、外部送信＋課金が要る。手元のMacだけで完結する体験は、コストの話以上に「全部自分で握れている」という安心感が大きいです。詰まっても、原因が全部自分の環境の中にある。

つまずきポイントを回避するTipsを置いておきます。

* **環境で溶かすな。** `mlx` が入らない／起動時に謎のAttributeError、の8割は「x86\_64 python を掴んでいる」か「transformers が5.x」です。ここだけ先に潰せば、あとは楽しい工程です。
* **"動いているか"を毎回自問する。** 綺麗な静止画をズームしただけで満足しない。I2Vを通すまでが動画です。安く早く出せても、違うものなら価値ゼロ。
* **失敗ログを資産にする。** 当たったプロンプト＋seed、モデルの所要時間、踏んだ地雷を全部 `knowledge/` に残す。再現性がそのまま資産になります。私たちのスコアが77→85に上がったのは、毎回の失敗を1行ずつ記録に変えたからです。
* **重いGPUタスクは"時間をずらす"。** 同じMacで別の重処理や自分の作業と同時に走らせると、両方が遅くなるか落ちます。GPUは1個。バッチは寝る前や離席中に。
* **「無料でここまで」を誇っていい。** 完璧じゃなくていい。紙芝居から本物の動きへ、一歩ずつ。その記録を共有し合えるのが、ローカルClaude民のいいところだと思っています。

同じMacの中で、また一本作ります。あなたのパイプラインの詰まりどころも、どこかで聞かせてください。🌿

---

*（数値・所要時間はいずれもこのM1 Max 64GB環境での実測に基づき、憶測の数字・保証表現は含みません。）*
