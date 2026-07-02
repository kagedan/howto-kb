---
id: "2026-07-02-君たちはどう-fable-のか-公式ドキュメントによる-claude-fable-5-の使い方の本質-01"
title: "君たちはどう Fable のか ~ 公式ドキュメントによる Claude Fable 5 の使い方の本質"
url: "https://qiita.com/tomoki-miso/items/36e5893e4d235625de44"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "qiita"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

### 1.1 無料枠、帰ってきました

Fable 5 が帰ってきた！！

6/9にGAして、6/12に輸出規制で止まって、6/30に規制解除、7/1に復活([公式声明](https://www.anthropic.com/news/fable-mythos-access))。ジェットコースターみたいな3週間でした。

そして今度は7/1〜7/7、[週次利用枠の最大50%までFable 5が無料開放](https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access)されています。Pro/Max/Team、一部のEnterprise premium seat対象。API利用はこの無料枠に含まれません。

**Fableにコードを書かせるな。Fableには「何を書くべきか」を探させろ。**

これが結論です。以降、その理由を潰していきます。

### 1.2 この記事で扱いたい問い

一言で言えば、「なぜ実装に投げるのは筋が悪いのか」。

もう少し具体的には以下です。

- なぜ分類器の誤爆が、実装タスクで特に効いてくるのか
- 実装以外に投げるとしたら、何が候補になるのか

この問いに答えていきます。

## 2. まず実装に投げたくなる

### 2.1 素朴に考えるとこうなりそう

50%も無料で使えるなら、一番トークンを食う作業、つまり実装に投げるのが得、と考えるのが自然です。

大規模リファクタ、複数日かかる機能実装、塩漬けの技術的負債の解消。どれも「時間はかかるけど手順は決まっている」タスクに見えます。50%枠をここに突っ込みたくなる。

でも、これは半分しか合ってません。

### 2.2 しかし分類器の誤爆で崩れる

**分類器の誤爆で自走が途中で止まるリスクがある。** これが実装に投げるのを避けたい理由です。

詳しく見ていきます。

## 3. 分類器の誤爆というリスク

### 3.1 何が起きるのか

[公式ヘルプ](https://support.claude.com/en/articles/15363606-why-claude-switched-models-in-your-conversation-with-fable-5)によると、Fable 5は全リクエストに対してsafety classifierを実行しています。対象は3領域。

- 攻撃的サイバーセキュリティ技術
- 生物学系の内容
- モデル自身の思考過程の抽出

誤爆するとどうなるか。自動でOpus 4.8に切り替わり、**以降の会話はOpusに固定される**(手動で戻せます)。

### 3.2 直近のメッセージだけが見られているわけじゃない

ここが決定的です。このチェックは直近のメッセージだけじゃなく、**memory・connector経由のコンテンツ・web検索結果・ファイルまで含めて全部見る**、と公式に明記されています。

言い換えると、自分が何も書いていなくても、memoryの中身だけで誤爆しうるということ。

overnight run前提の使い方は「途中でモデルが差し替わらない」ことが大前提です。この仕組みは、その前提を静かに壊します。長時間自走させたいタスクほど、途中で止まるコストは高い。

### 3.3 探索させたいのに、探索自体が誤爆を呼ぶという皮肉

3つ目の対象、「モデルの思考過程の抽出」が地味に効いてきます。

[公式プロンプトガイド](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)は、"reasoning を出力させる/説明させる" 系の指示が `reasoning_extraction` という refusal カテゴリを誤発火させ、Opusへのフォールバックを増やすと明言しています。

この記事で後述する「探索・診断させる」使い方は、性質上「なぜそう判断したか説明して」という指示を書きたくなる場面が多いです。
素直に書くと、誤爆リスクを自分から上げることになる。reasoningの可視化が必要なら、モデルに説明させるのではなく summarized thinking blocks を読む設計にする必要があります。

推している使い方の足を、その使い方自体が引っ張る。地味に厄介な話です。

## 4. では何に使うべきか

分類器の誤爆リスクを型で整理するとこうなります。

```text
実装タスク       : 分類器領域に触れやすい & 途中で止まると被害が大きい -> Fableに投げると損しやすい
探索・診断タスク : 途中で多少止まっても被害が小さい                   -> Fableの強みと噛み合う
```

Fableの長期自走能力が本当に生きるのは、**「何を実装すべきか自体が自明じゃない」フェーズ**です。具体的には:

- 技術的負債がどこに溜まっているか、コードベース全体を横断して洗い出す
- 複数の設計選択肢(TCA vs Riverpod、Repository層の切り方など)を、実際のコード規模・依存関係を踏まえて比較させる
- 「この機能を6ヶ月運用したらどこが壊れるか」を今のアーキテクチャから逆算させる
- 受託案件で要件が曖昧なとき、クライアントに聞くべき質問リストを、コードベースや既存ドキュメントから逆引きで作らせる

念のため断っておくと、この4つは公式ソースに載っている事例ではなく、ここまでの根拠から自分が導いた提案です。実装させるんじゃなく、探索・診断・計画させるタスク。
しかも一発の指示で終わらず、モデルが自分で仮説を立てて検証を繰り返す必要がある。
まさにovernight run向きです。

## 5. 指示の設計思想も実装向きじゃない

[公式プロンプトガイド](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)は、旧モデル向けに書いたskillsやプロンプトはFable 5には過剰に規定的すぎて、むしろ出力の質を落としうると明言しています。
デフォルトの挙動の方が優れているなら、古い指示は削除を検討しろ、と。

ガイド全体の構成を見ても、instruction-followingの強さ、意図(reason)を渡すことの有効性、境界(boundary)の明示、自己検証(self-verification)の4つが繰り返し出てくる柱になっています。

これは実装タスクとは相性が悪い。実装は具体的な手順・制約が多いほど安定しますが、Fableのような自律探索が得意なモデルにそれを与えると、過剰指示がノイズになります。
逆に「方針を考えさせる」タスクは元々指示がゆるくて済むので、Fableの強みと構造的に噛み合う。

## 6. 具体的な使い方の型

1. **いきなりビルドさせない。先に clarifying question で詰めさせる。** 検証基準を先に言語化させてから着手させると、進捗の自己申告が信用できるようになります。
2. **進捗捏造を防ぐ一文を必ず入れる**([公式プロンプトガイド](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)より、社内テストでほぼ完全に捏造報告を排除できたとされるブロック):

```text
Before reporting progress, audit each claim against a tool result from this session.
Only report work you can point to evidence for; if something is not yet verified, say so explicitly.
Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that;
when something is done and verified, state it plainly without hedging.
```

3. **投げるのは「積みタスクの中で一番重いやつ」に限定する。** 週次枠の50%は有限です。トイタスクや日常のコーディングに溶かすのは機会損失。

## 7. おわりに

50%枠は「コードを書かせる」より「コードを書く前に決めるべきことを決めさせる」方に使う。これが自分の結論です。

実装は普段のワークフローに任せて、Fableには長期方針・技術的負債の棚卸し・意思決定の材料集めをやらせる。分類器の誤爆リスクという軸で見れば、実装より探索に向いていることは、わりと機械的に導けます。

この一週間の枠、実装に溶かして終わるにはもったいないと思います。
