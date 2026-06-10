---
id: "2026-06-09-mastra-foundations-コーディングエージェントの本体はループではなく-harness-01"
title: "[Mastra Foundations] コーディングエージェントの本体はループではなく Harness だった"
url: "https://zenn.dev/shiromizuj/articles/75f375ac273175"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で公開された [Foundations](https://mastra.ai/blog/category/foundations) カテゴリの記事を、**背景知識を補いながらより詳しく**解説します。

---

## この記事が書かれた背景

2026年前半の Mastra は、単に「エージェントフレームワーク」を作るだけでなく、エージェントを長時間・複数ターン・複数 UI で運用するための基盤を急速に整えてきました。2月には [Observational Memory](https://zenn.dev/shiromizuj/articles/12e4640b99bc6a)、4月には [Channels](https://zenn.dev/shiromizuj/articles/b09eee651a06e9)、6月には [Agent Signals](https://zenn.dev/shiromizuj/articles/e91394dd201039) が出ています。

これらは別々の機能に見えますが、実際にはひとつの問題に向いています。つまり、**エージェントを単発の LLM 呼び出しではなく、継続して動くソフトウェアとしてどう成立させるか**という問題です。

今回の Sam Bhagwat の記事は、その答えを「Harness」という言葉でまとめ直したものです。コーディングエージェントの差は、モデル単体の性能だけではなく、ループの外側で何を面倒見ているかにある。これがこの記事の核心です。

---

## 今回の記事をひとことで言うと

[Mastra Code](https://zenn.dev/shiromizuj/articles/bae2cd3e33cbe9) の優位性として語られているのは、「より賢いコーディングモデルを積んだ」という話ではありません。**会話、状態、承認、表示、再開、メモリ圧縮を支える harness をどう設計したか**が主題です。

コーディングエージェントを雑に言えば、LLM にファイル読み書きやコマンド実行のツールを渡し、その結果を見ながら次の一手を決めさせるループです。しかし、それだけでは長時間の実務に耐えません。記事はまず、単純な agent loop がどう壊れるかを3つの観点で示します。

* Context rot: ツール結果と途中経過が溜まりすぎて、重要情報の密度が落ちる
* Lossy compaction: 履歴をまとめて要約すると、細かい制約や以前の判断が抜け落ちる
* Stateless sessions: セッションをまたぐと、毎回ゼロから文脈を渡し直す必要がある

ここで重要なのは、どれも「落ちてエラーになる」タイプの失敗ではないことです。エージェントは動き続けるので、ユーザーはしばらく問題に気づけません。だからこそ、loop そのものではなく、その周囲にある運用レイヤーが必要になります。

---

## Harness とは何か

この記事で言う Harness は、エージェントループを包む運用基盤です。Mastra Code では少なくとも次の責務を持っています。

| 領域 | Harness が担当すること |
| --- | --- |
| 会話モデル | 会話を one-shot 呼び出しではなく、開いた channel として保持する |
| ストリーミング整形 | provider ごとの raw chunk を semantic event に変換する |
| UI 表示 | event 群を single display state に reducer で畳み込む |
| HITL | ツールが人間の返答や承認を待てるようにする |
| 永続化 | thread、mode、model、token 消費量、memory 設定を保存する |
| メモリ継続性 | observational memory で高信号な履歴を保つ |
| 実行ガード | ツール承認チェーンや session lock を管理する |

ばらばらに語られがちだった話ですが、全部 harness の責務として再配置されます。たとえば「CLI を閉じても再開できる」「途中でユーザーが指示を差し込める」「承認 UI が出る」「長時間セッションでも劣化しにくい」といった話は、同じ設計思想の上に乗っています。

---

## 会話を Channel として扱う意味

この記事の中でも特に重要なのが、**会話を function call ではなく channel として扱う**という説明です。

普通の LLM アプリは「メッセージを送る」「応答を受け取る」「接続終了」という HTTP 的な世界観で作れます。しかしコーディングエージェントはそれでは足りません。数分かかるタスクの途中でユーザーが横から「その修正はやめて、先にテストを見て」と言うことがありますし、今の run が終わったら次にやってほしいことを先回りで伝えたくなることもあります。

thread に対して継続購読する channel モデルにしておくと、こうした操作が自然にできます。

* 実行中のエージェントへの割り込み
* 次メッセージのキューイング
* 現在 run の中止と別タスクへの切り替え
* クラッシュや再起動後の再アタッチ

この説明は、4月の Channels 記事で語られていた「エージェントとの会話を thread として扱う」考え方を、コーディングエージェント側へ引き寄せて整理したものとも読めます。Slack や Discord のマルチチャネル世界で必要だった thread 永続化と signal の仕組みが、ローカル CLI の coding agent にも効いているわけです。

---

## Event から Display State へ落とす設計が強い

Mastra の harness は、モデルやツールから流れてくる生のストリームをそのまま UI に見せません。まず `processStreamChunk` で provider 依存の raw chunk を semantic event に変換し、次に reducer で single display state に畳み込みます。

この2段階変換の利点はかなり大きいです。

### 1. provider 差分の吸収点がひとつになる

ストリーミング API は provider ごとに少しずつ違います。フィールド名、chunk の切り方、tool call の途中表現、将来の仕様変更。これを UI やログ層が直接解釈し始めると、変更点が全体へ伝播します。

`processStreamChunk` を唯一の翻訳層にしておけば、仕様差分の局所化ができます。

### 2. UI が「現在状態」だけ見ればよくなる

UI は「いま世界がどう見えるべきか」を知りたいのであって、イベントを一つずつ再生したいわけではありません。display state に統合してしまえば、UI 側は状態を読むだけで済みます。

これは CLI でも Web UI でも効きます。さらに、250ms バッチと 500ms ceiling を置いた redraw 制御によって、描画負荷と即時性のバランスも取っています。承認要求や質問のような human-blocking イベントだけ即時 flush する判断も妥当です。

このあたりは、エージェントを「賢くする」技術というより、リアルタイムアプリケーションの UI アーキテクチャに近い話です。Mastra が coding agent をアプリケーションとして真面目に作っていることがよく分かります。

---

## ツールは単なる関数ではなく、一時停止できる手続きになる

記事の中盤で面白いのが、`ask_user` や `submit_plan` の説明です。ここではツールが Promise を返しながら人間の応答を待つ、という形で実装されています。

これは、ツールを「すぐ終わる関数呼び出し」と見なさない設計です。現実のエージェントでは、次のような操作がしばしば入ります。

* 危険なコマンド実行前に確認を取りたい
* 実装計画を見せて承認されてから build mode に移りたい
* ユーザーに不足情報を聞いてから先へ進みたい

harness が back-channel を tool context に差し込むことで、ツールは UI に prompt を出し、callback を登録し、回答待ちで停止できます。しかも harness がない環境では plain text fallback で動ける。つまり、同じ tool を CLI、GUI、headless pipeline で共通利用しやすいわけです。

ここは、単なる tool calling を超えて「エージェントアプリケーションの制御フロー」をどう記述するか、という話でもあります。

---

## Observational Memory は compaction の置き換えではなく再設計

Mastra はすでに 2 月に Observational Memory を発表していましたが、今回の記事ではそれが coding agent の文脈で再度整理されています。

ポイントは、OM を「履歴が限界に来たら最後に要約する仕組み」としてではなく、**早めに観測し、構造化し、段階的に圧縮する仕組み**として扱っていることです。

構成は3層です。

* 直近の raw messages
* observer model が書き出した observation log
* reflector model が圧縮した reflections

これにより、過去の決定が単なる曖昧な要約文の中へ埋もれず、「決定」「状態変化」として残りやすくなります。さらに、provider の prompt cache が切れやすいタイミングや provider switch の瞬間にも OM を発火させる設計は実務的です。長時間セッションを支えるために、モデルの理想論ではなく provider の現実的なふるまいに合わせているからです。

Claude Code や Codex と比較するセクションも、この OM を軸に組み立てられています。Mastra の主張は明快で、単純 compaction よりも「高信号な継続メモリ」を維持したい、ということです。

---

## 競合比較から見える Mastra の売り方

記事後半では Claude Code と OpenAI Codex との比較表が出てきます。もちろんプロダクト比較なので Mastra 寄りですが、何を勝ち筋と見ているかはよく表れています。

Mastra が押し出しているのは次の点です。

* 長時間セッションの劣化を observational memory で抑える
* thread 単位の永続化で、再起動後も mode や model を保持する
* 実行中の steering を queue / interrupt / abort のかたちで扱う
* ツール承認を ordered rule chain で細かく制御する
* provider 横断で mode ごとにモデルを選べる
* harness 自体が OSS なので、自作エージェントの土台にできる

逆に言うと、Mastra は「最強の1モデルで全部解く」方向ではなく、**エージェントを構成する周辺システムをプロダクト化する**方向で差別化しています。これはフレームワーク企業として自然なポジショニングですし、長期的にはこちらのほうが再利用価値が高いとも言えます。

---

## まとめ

この記事を読むと、コーディングエージェントの本質は LLM ループそのものではなく、その周囲にある harness 設計にあることが見えてきます。

長時間の作業でコンテキストが腐らないこと。途中で人間が口を挟めること。危険な操作に承認を挟めること。CLI を閉じても同じ thread に戻れること。複数の UI が同じ実行状態を見られること。これらは全部、モデルの賢さとは別の層で解かなければならない課題です。

Mastra はその層を Harness として切り出し、Mastra Code というプロダクトの内部実装であると同時に、他の agent にも流用可能な再利用層として説明しています。support agent でも research agent でも ops agent でも、中断可能で継続可能な agent を作るなら、同じ問題にぶつかるはずです。

コーディングエージェントを「モデルがコードを書くツール」としてではなく、「状態を持って仕事を進めるアプリケーション」として捉え直す。この記事の価値はそこにあります。

---

## 参考リンク
