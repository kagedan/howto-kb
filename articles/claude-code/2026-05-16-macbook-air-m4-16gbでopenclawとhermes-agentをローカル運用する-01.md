---
id: "2026-05-16-macbook-air-m4-16gbでopenclawとhermes-agentをローカル運用する-01"
title: "MacBook Air M4 16GBでOpenClawとHermes Agentをローカル運用するベストプラクティス2"
url: "https://zenn.dev/sonder01/articles/macbook-air-m4-local-ai-models-2"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "LLM", "OpenAI", "Gemini", "GPT"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

前回は、MacBook Air M4 16GBでOpenClawとHermes Agentをローカル運用するなら、**モデル選びより先に権限設計を決める**、という話を書きました。

今回はその続きです。

では実際に、MacBook Air M4 16GBでエージェント用のローカルAIを選ぶなら、どれを使うべきか。

結論から書くと、現時点の第一候補は **Qwen3 8B** です。次点で **Gemma 3 12B**。Bonsai 8BとZAYA1-8Bは面白いですが、OpenClaw/Hermes Agentの主役モデルとしてはまだ癖があります。

## 検証の前提

検証時点は2026年5月16日です。

この記事では、次の情報を照合して評価しました。

* 公式モデルカード
* Ollama公式モデルライブラリ
* Hugging Faceのモデル情報
* 開発元が公開しているベンチマーク
* 第三者の小型モデル/ツール利用検証
* MacBook Air M4 16GBというメモリ制約

つまり、この記事の「検証」は、公開されているモデルカード、ベンチマーク、運用情報を、**OpenClaw/Hermes Agent用途の観点で同じ評価軸に並べ直したもの**です。

今回の評価軸は、単なるチャット性能ではなく、OpenClaw/Hermes Agentで使う前提の以下です。

| 評価軸 | 見るポイント |
| --- | --- |
| メモリ適性 | 16GB unified memoryで常用できるか |
| 実行基盤 | Ollama/MLX/llama.cppで素直に動くか |
| ツール利用 | tool callやJSON出力が安定するか |
| 長文耐性 | エージェント履歴・作業ログを抱えられるか |
| 日本語 | 日本語指示で破綻しにくいか |
| 運用性 | OpenClaw/Hermesに組み込みやすいか |

## 候補一覧

| モデル | 位置づけ | 結論 |
| --- | --- | --- |
| Qwen3 8B | 第一候補 | Hermes/OpenClawのローカル主役候補 |
| Gemma 3 12B | 次点 | 長文・日本語・画像込みなら強いが重い |
| Bonsai 8B | 補助候補 | メモリは圧倒的に軽いが、主役エージェントには不安 |
| ZAYA1-8B | 実験枠 | 推論効率は魅力。ただし標準運用はまだ早い |
| GPT-OSS 20B級 | 番外 | 16GB Airでは常用主役にしづらい |

## OpenAIモデルでいうとどのあたりか

先に注意点を書きます。ローカルOSSモデルとOpenAI APIモデルは、同じベンチマークだけで等価比較できません。特にエージェント用途では、tool call、長い会話履歴、プロンプトインジェクション耐性、失敗時の自己修正、JSONの崩れにくさが効きます。

その前提で、OpenAIモデルにたとえるなら次のレンジです。

| ローカルモデル | OpenAIでいう目安 | コメント |
| --- | --- | --- |
| Qwen3 8B | GPT-4o mini寄り | 小型実務モデル枠。GPT-3.5 Turboより強い場面が多く、軽いagent workerなら第一候補。ただしGPT-4o本体やo3/o4系の代替ではない |
| Gemma 3 12B | GPT-3.5 Turbo超からGPT-4o mini未満/一部近い | 長文・画像入力・日本語補助では強い。tool callや自律実行の安定性ではGPT-4o miniをそのまま置き換えるほどではない |
| Bonsai 8B | GPT-3.5 Turbo未満から小型OSS 8B級 | メモリ効率は異常に高いが、主役agentとしては信頼しない。分類・短文変換worker向き |
| ZAYA1-8B | 数学/コード限定でo3-mini級に近づく可能性、通常agentではGPT-4o mini未満 | 開発元ベンチではreasoningが強い。一方でagentic BFCL/τ²は高くないので、Hermes/OpenClawの主役にはまだ早い |
| GPT-OSS 20B級 | GPT-4o mini近辺を狙う重めローカル枠 | 品質は魅力だが、MacBook Air M4 16GBでは常駐agentに重い |

OpenAI公式のGPT-4o mini発表では、MMLU 82.0%、MGSM 87.0%、HumanEval 87.2%、128K context、強いfunction callingが示されています。ここを基準にすると、Qwen3 8BやGemma 3 12Bは「小型APIモデルに近い用途」は狙えますが、**権限を持つエージェントの主判断を任せるなら、まだAPIモデル併用が安全**です。

## Qwen3 8B: まず試すべき第一候補

Qwen3 8Bは、MacBook Air M4 16GBでローカルエージェントを組むときの最初の候補です。

Hugging Faceの公式モデルカードでは、Qwen3-8Bは8.2Bパラメータ、ネイティブ32,768 tokens、YaRN利用で131,072 tokensまで検証されていると説明されています。Ollama公式ライブラリでは、`qwen3:8b` は5.2GB、40K context windowとして提供されています。

### エージェント用途での評価

Qwen3 8Bの強みは、モデルサイズ、推論能力、実行基盤のバランスです。

| 項目 | 評価 |
| --- | --- |
| メモリ | 5GB級で16GB Airに乗せやすい |
| 実行基盤 | Ollamaで扱いやすい |
| 長文 | 32K-40K級でエージェント履歴を持たせやすい |
| ツール利用 | 小型モデルとしては現実的 |
| 日本語 | 実用域 |
| 弱点 | 複雑な長期タスクではAPIモデルに負ける |

OpenClawやHermes Agentで使うなら、Qwen3 8Bは「全部を完璧に任せるモデル」ではなく、**ローカル側の常用worker**として見るのがよいです。

おすすめの使い方はこれです。

```
Qwen3 8B:
- ローカルでの分類
- 要約
- 軽いコード読み
- 短い修正案
- JSON化
- 予定やメモの整理

APIモデル:
- 実ファイル編集
- 長い設計判断
- 複数ステップのブラウザ操作
- 失敗時のリカバリ
```

## Gemma 3 12B: 長文とマルチモーダル重視の次点

Gemma 3 12Bは、Qwen3 8Bより少し重いですが、長文とマルチモーダルの扱いで魅力があります。

Googleの公式モデルカードでは、Gemma 3はテキストと画像入力に対応し、4B/12B/27Bでは128K tokensの入力コンテキストを持つと説明されています。Ollama公式ライブラリでは、`gemma3:12b` は8.1GB、128K context window、Text/Image対応です。

### エージェント用途での評価

| 項目 | 評価 |
| --- | --- |
| メモリ | 8GB級。16GB Airでは余裕は少ない |
| 実行基盤 | Ollamaで扱いやすい |
| 長文 | 128K級が魅力 |
| 画像 | ローカル画像理解用途に強い |
| 日本語 | 比較的安定 |
| 弱点 | エージェント常駐では重さが出やすい |

Gemma 3 12Bは、常時起動のworkerというより、**長文要約・画像込みの確認・文書読解用のローカル専門家**として使う方が安定します。

MacBook Air M4 16GBでは、OpenClaw/Hermesのメインモデルにすると、ブラウザ、Docker、エディタ、チャットアプリとメモリを取り合います。Qwen3 8Bより「賢い場面」はありますが、運用全体では重さが先に効きます。

## Bonsai 8B: 軽いが、エージェント主役にはしない

Bonsai 8Bは非常に面白いモデルです。PrismMLの発表では、1-bit Bonsai 8Bは8.2Bパラメータながら1.15GBのメモリフットプリントで、同クラスの8Bモデルより大幅に小さいとされています。Hugging FaceにはGGUF版も公開され、llama.cpp/Metal/on-device向けとしてタグ付けされています。

公式発表では、Bonsai 8BはQwen3 8Bよりモデルサイズあたりの効率が高く、M4 Pro Macで高いtokens/secを出したデモも紹介されています。

ここだけ見ると、MacBook Air M4 16GBには最高に見えます。

ただし、OpenClaw/Hermes Agentの主役として見ると、結論は変わります。

### なぜ主役にしないのか

Bonsaiの価値は「小ささ」と「速度」です。しかし、エージェント用途では小ささだけでは足りません。

必要なのは次です。

* 長い会話履歴を破綻なく保持する
* tool callを安定して出す
* JSONや関数引数を崩さない
* 失敗時に自分で修正する
* 途中で目的を忘れない
* 余計な自然文を混ぜない

PrismMLの公式ベンチでも、Bonsai 8Bは平均値では健闘していますが、BFCLv3は65.7で、Qwen3 8Bの81.0より低く出ています。第三者の小型モデル検証でも、BFCLのような関数呼び出しベンチと、実際のブラウザ/OS操作タスクの成否は一致しないという報告があります。

そのため、Bonsaiは次の使い方が合っています。

| 用途 | 向き不向き |
| --- | --- |
| 短文分類 | 向く |
| 低メモリの下書き | 向く |
| 高速な要約worker | 向く |
| OpenClawの主役モデル | まだ不安 |
| Hermesのコード修正agent | まだ不安 |
| ブラウザ操作agent | 推奨しない |

自分の結論は、**Bonsaiは「軽量補助モデル」としては有望だが、記憶・ツール利用・長期タスクの安定性が足りず、現時点ではエージェントの主役にはしない**です。

## ZAYA1-8B: 期待値は高いが、まだ実験枠

ZAYA1-8BはZyphraのMoE reasoning modelです。公式モデルカードでは、8.4B total parameters、760M active parametersの小型MoEとして説明されています。数学・コード・長い推論に強く、on-device local LLM applicationsにも向くとされています。

ZAYA1の魅力は、実際に動くならかなり大きいです。

* active parametersが少ない
* reasoning寄り
* Apache 2.0
* 小型ローカル用途を意識している
* Macのローカル実験と相性がよさそう

ただし、現時点ではQwen3やGemmaほど「Ollamaでそのまま使えばよい」という状態ではありません。MLX版や派生変換は出ていますが、OpenClaw/Hermesで日常運用するモデルとしては、まだ導入手順と互換性確認が必要です。

| 項目 | 評価 |
| --- | --- |
| メモリ効率 | 期待大 |
| reasoning | 期待大 |
| Ollama運用 | まだ弱い |
| Hermes/OpenClaw組み込み | 要検証 |
| 主役採用 | まだ早い |

ZAYA1-8Bは、記事執筆時点では **「次に試すべき研究枠」** です。MacBook Air M4 16GBでうまく動く可能性はありますが、毎日のエージェント基盤に置くには、もう少し実行環境が落ち着いてからでよいと思います。

## GPT-OSS 20B級: 16GB Airでは重い

20B級モデルは、品質だけ見ると魅力があります。しかしMacBook Air M4 16GBのローカルエージェント用途では、モデル本体だけでなく、KV cache、Docker、ブラウザ、OpenClaw/Hermes本体、普段のアプリが同じメモリを使います。

16GB Airで20B級を主役にすると、次が起きやすいです。

* 起動が重い
* swapに入りやすい
* ブラウザ操作と同時に苦しくなる
* 長時間agent loopで熱と遅延が出る
* 失敗時の再試行が遅い

20B級は「たまに使う高品質ローカルモデル」としてはありですが、OpenClaw/Hermesの常用モデルにはしづらいです。

## 推奨構成

MacBook Air M4 16GBでのおすすめ構成はこれです。

```
OpenClaw / Hermes Agent
├─ main local worker: Qwen3 8B
├─ long-context / image helper: Gemma 3 12B
├─ tiny helper: Bonsai 8B
├─ experimental reasoning: ZAYA1-8B
└─ cloud fallback: Claude / GPT / Gemini class
```

実運用では、モデルを1つに決め打ちしない方が安定します。

| タスク | 推奨 |
| --- | --- |
| メモ整理 | Qwen3 8B |
| Slack/Telegramからの軽い依頼 | Qwen3 8B |
| 長文PDF/記事要約 | Gemma 3 12B |
| 画像込み確認 | Gemma 3 12B |
| 超軽量分類 | Bonsai 8B |
| 数学・推論実験 | ZAYA1-8B |
| ファイル編集を伴う開発 | APIモデル併用 |
| ブラウザ操作agent | APIモデル推奨 |

## OpenClaw/Hermes向けのモデル設定方針

小型ローカルモデルをエージェントで使うときは、モデル名よりプロンプトと権限の方が重要です。

### Qwen3 8B向け

```
あなたはローカルworkerです。
推測でファイルを変更しない。
ツールを使う前に、実行するコマンドと目的を1行で説明する。
出力はJSONまたは短い箇条書きにする。
不明な場合は「不明」と返す。
```

### Gemma 3 12B向け

```
あなたは長文読解workerです。
入力文書から根拠を抜き出し、要約と判断を分けて返す。
ツール実行やファイル変更は行わない。
```

### Bonsai 8B向け

```
あなたは軽量分類workerです。
長い推論をしない。
入力を次のラベルに分類するだけにする。
出力は必ずJSONのみ。
```

Bonsaiには長いagent loopを任せず、分類・下書き・短い変換のようにタスクを細く切るのがよいです。

## 最終ランキング

| Rank | モデル | MacBook Air M4 16GBでの評価 |
| --- | --- | --- |
| 1 | Qwen3 8B | まずこれ。ローカルagentの主役候補 |
| 2 | Gemma 3 12B | 長文・画像・日本語で強いが重い |
| 3 | Bonsai 8B | 軽さは抜群。ただし主役agentにはしない |
| 4 | ZAYA1-8B | 有望だが、現時点では実験枠 |
| 5 | 20B級 | Air 16GBでは常用に重い |

## まとめ

MacBook Air M4 16GBでローカルAIエージェントを動かす場合、モデル選定の基準は「一番賢いモデル」ではなく、**長時間、失敗少なく、ツールの前後で破綻しないモデル**です。

その観点では、Qwen3 8Bが一番バランスがよいです。Gemma 3 12Bは長文や画像込みの作業に強い一方、常駐エージェントにはやや重い。Bonsai 8Bは1GB級の軽さが魅力ですが、記憶・ツール利用・長期タスクの主役としてはまだ不安が残ります。ZAYA1-8Bは次に伸びそうですが、日常運用には実行基盤の成熟待ちです。

**MacBook Air M4 16GBでの現実解は、Qwen3 8Bを主役にし、Gemma 3 12Bを補助に置き、Bonsai/ZAYA1は実験枠として触る構成**です。

## 参考リンク
