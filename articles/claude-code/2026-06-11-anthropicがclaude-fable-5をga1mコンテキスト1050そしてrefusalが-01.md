---
id: "2026-06-11-anthropicがclaude-fable-5をga1mコンテキスト1050そしてrefusalが-01"
title: "Anthropicが「Claude Fable 5」をGA——1Mコンテキスト・$10/$50、そして「refusalが正常応答」になる新API設計"
url: "https://qiita.com/okssusucha/items/ac4f5b6c32314c577061"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "LLM", "Python", "TypeScript"]
date_published: "2026-06-11"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

# Anthropicが「Claude Fable 5」をGA——1Mコンテキスト・$10/$50、そして「refusalが正常応答」になる新API設計

2026年6月9日、AnthropicがClaude Fable 5(`claude-fable-5`)とClaude Mythos 5(`claude-mythos-5`)を発表した。注目すべきは性能の数字だけではない。「最上位モデルを安全分類器付きで一般提供し、分類器に当たったリクエストは別モデルにフォールバックさせる」という、これまでのLLM APIになかった契約がMessages APIに入った点だ。本稿の事実関係はすべて以下の一次ソースから取っている。

- 発表ブログ: https://www.anthropic.com/news/claude-fable-5-mythos-5
- 製品ページ: https://www.anthropic.com/claude/fable
- モデル仕様: https://platform.claude.com/docs/en/about-claude/models/overview
- API変更点: https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5

## 何が起きたか

Anthropicは今回、同一の能力を持つ2つのモデルを同時に出した。

**Claude Fable 5** は「Mythos級モデルを一般利用向けに安全化したもの(a Mythos-class model that we've made safe for general use)」と説明される、同社の最上位の一般提供モデル。6月9日からClaude API、Claude Platform on AWS、Amazon Bedrock、Vertex AI、Microsoft Foundryで一般提供(GA)が始まった。

**Claude Mythos 5** は同じモデルから一部領域の安全分類器を外したもので、Project Glasswingの承認顧客のみの限定提供。一般開発者が触れるのはFable 5のほうだ。

性能面では「テストしたほぼすべてのベンチマークでstate-of-the-art」と謳い、CognitionのFrontierCodeで「medium effortでもフロンティアモデル中最高スコア」、HebbiaのFinance Benchmarkで全モデル中最高、自社のコア分析ベンチマークで初の90%超えを挙げる。Stripeは「通常ならチームで2か月以上かかるコードベース全体のマイグレーションを1日で完了した」とコメントしている(顧客の証言であり、再現可能な測定値ではない点には留意)。

6月9日〜22日はPro/Max/Team/Enterpriseプランで追加費用なしで使え、6月23日以降は利用クレジットが必要になる。

## 技術的な詳細

仕様の要点を公式ドキュメントから拾うと:

- **コンテキストウィンドウ**: デフォルトで1Mトークン。最大出力は128kトークン
- **価格**: 入力$10/出力$50(per MTok)。Opus 4.8($5/$25)のちょうど2倍。プロンプトキャッシュで入力90%引き
- **トークナイザ**: Opus 4.7で導入された新トークナイザを使用。それ以前のモデル比で「同じテキストが約30%多いトークン数になる」と明記されており、コスト試算時は要注意
- **思考モード**: Adaptive thinkingが常時オンで、これが唯一の思考モード。`thinking: {"type": "disabled"}` は非対応。思考の深さは `effort` パラメータで制御する
- **生のCoTは返さない**: `thinking.display` のデフォルトは `"omitted"`(空の思考ブロックが返る)。`"summarized"` を指定すると要約された思考が読める。生のchain of thoughtは一切返らない

そして今回いちばん面白いのが **refusalとfallbackのAPI契約** だ。Fable 5にはサイバーセキュリティ、生物・化学、モデル蒸留の3領域に安全分類器が入っており、該当リクエストは拒否される。このとき:

- Messages APIはエラーではなく **HTTP 200の正常応答として `stop_reason: "refusal"` を返す**。どの分類器が拒否したかもレスポンスに含まれる
- `fallbacks` パラメータ(ベータ)を渡すと、拒否時にAPI側で別モデルに自動リトライしてくれる。クライアント側用にはTypeScript/Python/Go/Java/C#のSDKミドルウェアがある
- 出力生成前に拒否されたリクエストは課金されず、リトライ時は「fallback credit」がプロンプトキャッシュの載せ替えコストを払い戻す

発表ブログによれば分類器の発動は「セッションの5%未満」で、該当トラフィックはOpus 4.8が自動処理する。外部レッドチームの1,000時間超のテストで「universal jailbreakは見つからなかった」ともしている。一方でFable 5/Mythos 5は「Covered Models」に指定され、**30日間のデータ保持が必須でゼロデータ保持(ZDR)は選択不可**。ZDR前提でコンプライアンスを組んでいる組織には採用判断のブロッカーになりうる。

機能面では、effort、メモリツール、コンテキスト編集(ベータ)、compaction、task budgets(ベータ)、visionをローンチ時点でサポートする。

## 実務エンジニアへの影響

短期的に対応が必要なのは、Fable 5を組み込む場合 **refusalハンドリングが必須コードパスになる** ことだ。これまで「モデルの拒否」はテキストとして返る曖昧な事象だったが、`stop_reason` で機械可読に判定できる以上、ハンドリングしないのは設計漏れになる。リトライ・フォールバック・課金の仕様が最初からセットで文書化されているのは運用側にはありがたい。

コスト面では、Opus 4.8の2倍の単価に加えて新トークナイザで実効トークン数が約3割増えるため、見た目以上に請求額は膨らみやすい。長時間のエージェントタスクや1Mコンテキストを活かした大規模リポジトリ解析など、Opus 4.8で歯が立たなかった仕事に絞るのが現実的だろう。逆に「medium effortでもFrontierCode最高スコア」という主張が本当なら、高effortのOpus 4.8と低effortのFable 5の比較は自分のワークロードで測る価値がある。

また、生のCoTが返らない仕様は、思考ログを監査やデバッグに使っていたチームに影響する。`display: "summarized"` の要約で足りるかは移行前に確認しておきたい。

## 試し方

Claude APIキーがあればすぐ試せる。モデルIDは `claude-fable-5`。Pythonでrefusalを拾ってOpus 4.8にフォールバックする最小形はこうなる。

```python
import anthropic

client = anthropic.Anthropic()

def ask(prompt: str):
    resp = client.messages.create(
        model="claude-fable-5",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":
        # 安全分類器による拒否。出力前の拒否は課金されない
        resp = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
    return resp
```

`fallbacks` パラメータやfallback creditの詳細は前掲のAPI変更点ドキュメントにまとまっている。6月22日までは有料プランに含まれるので、Claude Code等から `/model` でFable 5を指定して挙動を見るのが一番手軽だ。

## 所感

ゲーム業界のR&Dという立場で目を引いたのは、発表ブログにさらっと書かれていた『Slay the Spire』の評価だ。永続メモリ(memory tool)を与えたときの性能向上が「Opus 4.8の3倍大きかった」とあり、プレイ経験から学習を積み上げるゲームプレイエージェントの実用度が一段上がったことを示唆する。QA自動化やバランス調整用のプレイテストエージェントを検証してきた身としては、数日単位の自律セッションを前提に設計されたモデル+メモリツールの組み合わせは、「1プレイごとに文脈がリセットされる」というこれまでの最大の壁を正面から崩しに来ていると感じる。一方で30日データ保持の強制は、未発表タイトルの素材を扱う開発現場では明確な制約だ。性能の派手さよりも「最上位モデルは分類器とフォールバック込みで出荷する」という枠組みのほうが、後年このリリースの本質だったと言われる気がしている。

(本稿の事実関係は2026年6月10日時点の公式発表・公式ドキュメントに基づく。ベンチマークの数値は自社・パートナー測定であり、第三者検証はまだ出ていない)
