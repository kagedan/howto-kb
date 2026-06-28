---
id: "2026-06-28-claude-fable-5入門-mythos級モデルをapiで使う完全ガイド-01"
title: "Claude Fable 5入門 — Mythos級モデルをAPIで使う完全ガイド"
url: "https://qiita.com/kai_kou/items/26e48f68f6840e32d9a6"
source: "qiita"
category: "ai-workflow"
tags: ["API", "GPT", "Python", "qiita"]
date_published: "2026-06-28"
date_collected: "2026-06-29"
summary_by: "auto-rss"
query: ""
---

![Claude Fable 5 をAPIから利用するイメージ](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/claude-fable-5-mythos-class-api-guide/01-hero.png)

## はじめに

2026年6月9日、Anthropicは新モデル **Claude Fable 5** を公開しました。これは、これまで限定提供にとどまっていた「Mythos級（Mythos-class）」のモデルを、一般の開発者が初めてAPIから利用できるようになったものです。

この記事では、Claude Fable 5の位置づけ・料金・ベンチマーク・APIでの使い方・安全分類器によるフォールバックの仕組みを、公式発表と公開情報をもとに整理します。

### この記事で学べること

- Claude Fable 5 と Claude Mythos 5 の違い
- Opus 4.8 と比較した料金・性能の全体像
- Python から Claude Fable 5 を呼び出す基本実装
- 安全分類器による Opus 4.8 への自動フォールバックの仕組み
- サブスクリプションでの提供条件（6月22日という期限）

### 対象読者

- Claude API を業務やプロダクトで利用している開発者
- 高難度のコーディング・知識労働タスクに最新モデルを使いたい方
- Opus 4.8 からの移行を検討している方

### 前提環境

- Python 3.10 以上
- `anthropic` Python SDK
- Claude API キー（Claude Platform で発行）

## TL;DR

- Claude Fable 5 は Mythos級モデルの **一般公開版**。model id は `claude-fable-5`。
- 料金は **$10/M（入力）・$50/M（出力）** で、Opus 4.8 のおよそ2倍。
- **SWE-Bench Pro 80.3%** と、コーディング系で次点モデルを約11ポイント引き離す。
- cyber・biology/chemistry・distillation など高リスク領域は **Opus 4.8 へ自動フォールバック** する。
- Pro / Max / Team / seat-based Enterprise プランでは **6月9日〜22日のみ無償**、6月23日以降は usage credits が必要。

## Claude Fable 5 とは

Claude Fable 5 は、Anthropic が「最も難しい知識労働とコーディング問題のための次世代の知能」と位置づけるモデルです。同時に、上位の **Claude Mythos 5** も承認済み組織向けに提供が開始されました。

両者は **同一のアーキテクチャ** を持ち、違いは「安全策（safeguards）」にあります。公式発表では、Fable はラテン語の *fabula*（寓話）に由来し、ギリシャ語の *mythos* に通じる語として説明されています。

| 項目 | Claude Fable 5 | Claude Mythos 5 |
|------|----------------|-----------------|
| 提供範囲 | 一般公開（API・サブスク） | 承認済み組織向け（15か国） |
| 安全策 | 高リスク領域は Opus 4.8 へフォールバック | 一部の安全策を承認パートナー向けに解除 |
| アーキテクチャ | 共通 | 共通 |

つまり Fable 5 は、Mythos 5 と同じ基盤性能を持ちながら、誰でも安全に使えるよう安全分類器を組み込んだ「公開版」だと理解すると整理しやすくなります。

## ベンチマークと位置づけ

公式発表によると、Fable 5 は「テストしたほぼすべてのベンチマークで最高水準（state-of-the-art）」を達成したとされています。具体的に公開されている数値として、コーディング能力を測る **SWE-Bench Pro** では **80.3%** を記録し、次点のモデルを約11ポイント引き離しています。

| ベンチマーク | Claude Fable 5 | Claude Opus 4.8 | GPT-5.5 |
|-------------|----------------|-----------------|---------|
| SWE-Bench Pro | 80.3% | 69.2% | 58.6% |

このほか、FrontierCode 評価やHebbia の金融ベンチマークでもフロンティアモデル中で最高スコアを得たと報告されています。報告では「タスクが長く複雑になるほど、Fable 5 のリードが大きくなる」とされており、短い単発クエリよりも、長時間にわたる複雑なワークフローで強みが出る設計と読み取れます。


> ベンチマークの数値はAnthropicおよび評価ベンダーの公表値です。自分のユースケースで効果を判断する際は、実際のタスクで評価（eval）を組むことが推奨されます。


## 料金体系 — Opus 4.8 との比較

![Claude Fable 5 と Opus 4.8 の料金・性能比較](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/claude-fable-5-mythos-class-api-guide/02-comparison.png)

Fable 5 の料金は、Opus 4.8 のおよそ2倍に設定されています。プロンプトキャッシュを併用すると入力コストを大きく抑えられる点は従来モデルと同様です。

| 項目 | Claude Fable 5 | Claude Opus 4.8 |
|------|----------------|-----------------|
| 入力 | $10 / 100万トークン | $5 / 100万トークン |
| 出力 | $50 / 100万トークン | $25 / 100万トークン |
| キャッシュヒット | $1 / 100万トークン | $0.50 / 100万トークン |
| コンテキスト | 100万トークン | 100万トークン |

公式発表では、Fable 5・Mythos 5 はいずれも「Claude Mythos Preview の半額未満」とされています。性能は上がりつつ、プレビュー版より単価が下がっている形です。

コスト最適化の基本は従来のClaudeモデルと変わりません。

- 繰り返し送る大きなシステムプロンプトや参照ドキュメントは **プロンプトキャッシュ** に載せる
- すべてのリクエストを Fable 5 に投げず、難易度の低いタスクは Sonnet や Opus 4.8 に振り分ける
- 出力料金が高いため、不要に長い応答を避けるよう `max_tokens` を適切に設定する

## APIで使う

Claude Fable 5 は、model id に `claude-fable-5` を指定するだけで利用できます。既存の Messages API の使い方はそのままです。

### インストール

```bash
pip install anthropic
```

### 基本的な呼び出し

```python
import anthropic

client = anthropic.Anthropic()  # 環境変数 ANTHROPIC_API_KEY を参照

message = client.messages.create(
    model="claude-fable-5",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": "次のPython関数のバグを指摘し、修正版を提示してください。\n\n"
                       "def average(nums):\n    return sum(nums) / len(nums)",
        }
    ],
)

print(message.content[0].text)
```

`model` を `claude-fable-5` にする以外は、これまでのClaude API呼び出しと同じ構造です。既存コードからの切り替えは、原則としてモデル名の差し替えだけで済みます。

### 長いコンテキストを活かす

Fable 5 は100万トークンのコンテキストウィンドウを持ちます。大規模なコードベースや長文ドキュメントをまとめて渡す場合は、繰り返し利用する部分をキャッシュに載せると効率的です。

```python
message = client.messages.create(
    model="claude-fable-5",
    max_tokens=4096,
    system=[
        {
            "type": "text",
            "text": "あなたはシニアソフトウェアエンジニアです。",
        },
        {
            "type": "text",
            "text": large_codebase_context,  # 大きな参照コンテキスト
            "cache_control": {"type": "ephemeral"},  # キャッシュ対象に指定
        },
    ],
    messages=[
        {"role": "user", "content": "このリポジトリの認証処理をレビューしてください。"}
    ],
)
```

`cache_control` を付与した部分はキャッシュされ、次回以降のリクエストで入力コストを抑えられます。

## 安全分類器とフォールバックの仕組み

![安全分類器によるフォールバックの仕組み](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/claude-fable-5-mythos-class-api-guide/03-flow.png)

Fable 5 を理解するうえで重要なのが、**安全分類器（safety classifiers）によるフォールバック** です。Fable 5 は次のような高リスク領域のリクエストを検知すると、応答を **Claude Opus 4.8 に自動的に切り替え** ます。

- **サイバーセキュリティ**: 攻撃的・侵入を目的とするタスク
- **生物・化学**: 設計上、広めに対象とされる
- **蒸留（distillation）**: モデルの抽出を狙う試み

公式発表によると、**95%以上のセッションではフォールバックが発生しない** とされています。つまり通常の開発・知識労働では Fable 5 本来の性能がそのまま得られ、限られた高リスク領域のみ Opus 4.8 の応答に置き換わる設計です。


> 高リスク領域のタスクでは、応答品質が Fable 5 ではなく Opus 4.8 のものになる可能性があります。セキュリティ研究などでフォールバックが頻発する場合は、その領域では挙動が変わりうる点に注意してください。


Anthropic は、1,000時間を超える内部のジェイルブレイクテストと外部レッドチームを実施し、「ユニバーサルなジェイルブレイク」は発見されなかったと報告しています。なお、報道では全ユーザーに対し30日間のトラフィック保持が課される点も指摘されており、データ保持ポリシーは事前に確認しておくとよいでしょう。

## 対応プラットフォーム

Fable 5 は、主要なクラウド経由でも利用できます。

- Claude API（platform.claude.com）
- Claude Platform on AWS
- Amazon Bedrock
- Google Cloud Vertex AI
- Microsoft Foundry

既存のクラウド基盤に Claude を組み込んでいる場合でも、モデル名を切り替えることで移行しやすい構成になっています。

## サブスクリプションでの提供 — 6月22日という期限

API だけでなく、サブスクリプションプランでも Fable 5 を利用できますが、**提供期間に注意** が必要です。

| 期間 | Pro / Max / Team / seat-based Enterprise プランでの扱い |
|------|-------------------------------|
| 2026年6月9日〜6月22日 | 追加費用なしで利用可能 |
| 2026年6月23日以降 | usage credits が必要（容量確保後に再開予定） |

つまり、サブスクリプションで無償利用できるのは公開からの約2週間に限られます。継続利用したい場合は、6月23日以降の usage credits の扱いを確認しておきましょう。

## Opus 4.8 からの移行チェックリスト

Opus 4.8 から Fable 5 への切り替えを検討する際は、以下を確認すると安全です。

- [ ] `model` を `claude-fable-5` に変更（API構造の変更は不要）
- [ ] 出力単価が2倍になるため、コスト試算を更新する
- [ ] 大きな参照コンテキストはプロンプトキャッシュに載せる
- [ ] 高リスク領域を扱う場合、フォールバックで挙動が変わる可能性を考慮する
- [ ] 自社ユースケースで eval を組み、Opus 4.8 との品質差を定量比較する
- [ ] サブスク利用の場合、6月23日以降の usage credits を確認する

## まとめ

- Claude Fable 5 は、Mythos級の性能を一般公開したモデルで、model id は `claude-fable-5`。
- SWE-Bench Pro 80.3% など、特にコーディングと長時間タスクで強みを持つ。
- 料金は Opus 4.8 の約2倍だが、プロンプトキャッシュとモデル振り分けでコストは最適化できる。
- 高リスク領域は Opus 4.8 へ自動フォールバックし、通常タスクは95%以上がフォールバックなしで動作する。
- サブスクの無償提供は6月22日まで。継続利用は usage credits を前提に計画する。

最新モデルを使うときほど、料金とフォールバックの挙動を踏まえた設計が重要になります。まずは小さなタスクで eval を組み、Opus 4.8 との差を定量的に確認してから本番に展開するのが堅実です。

## 参考リンク

- [Claude Fable 5 and Claude Mythos 5（Anthropic公式発表）](https://www.anthropic.com/news/claude-fable-5-mythos-5) — リリース日・モデルID・料金・安全策の出典
- [Anthropic Newsroom](https://www.anthropic.com/news) — 公式アナウンス一覧
- [Anthropic's Claude Fable 5 is a version of Mythos the public can access today（TechCrunch）](https://techcrunch.com/2026/06/09/anthropics-claude-fable-5-is-a-version-of-mythos-the-public-can-access-today/) — 安全策・データ保持の解説
- [Claude Fable 5: API, Benchmarks, Pricing & How to Use It（TrueFoundry）](https://www.truefoundry.com/blog/claude-fable-5-api-benchmarks-pricing-how-to-use-it) — SWE-Bench Pro・コンテキスト長・料金比較の参考
