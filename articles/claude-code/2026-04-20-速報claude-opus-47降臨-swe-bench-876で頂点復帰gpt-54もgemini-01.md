---
id: "2026-04-20-速報claude-opus-47降臨-swe-bench-876で頂点復帰gpt-54もgemini-01"
title: "【速報】Claude Opus 4.7降臨 ─ SWE-bench 87.6%で頂点復帰、GPT-5.4もGeminiも置き去り"
url: "https://qiita.com/GeneLab_999/items/6ab7a87291df241626e8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "LLM", "Gemini", "GPT", "qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

## この記事の対象読者

* Claude Code や Claude Opus 4.6 を日常的に使っている開発者
* GPT-5.4 / Gemini 3.1 Pro との性能差が気になる[LLM](https://qiita.com/GeneLab_999/items/7f1bd2de313bdd7ca423)ウォッチャー
* エンタープライズでAIエージェント基盤を選定しているテックリード
* 「結局、今どのモデルを本番に載せればいいの？」と迷っている人

## この記事で得られること

* Claude Opus 4.7 のリリース情報と価格・仕様のサマリ
* 新ベンチマーク全12種の徹底比較（Opus 4.6 / GPT-5.4 / Gemini 3.1 Pro / Mythos Preview）
* xhigh effort、3.75MP vision、self-verification など新機能の実用インパクト
* Opus 4.6 からの移行ガイド（トークン使用量の変化、プロンプト再調整のポイント）
* どのユースケースで Opus 4.7 を選ぶべきか、明確な判断基準

## この記事で扱わないこと

---

本記事は2026年4月16日（日本時間4月17日早朝）のAnthropic公式リリースおよび各種ベンチマーク報告に基づく。数値はすべてAnthropic公式発表および主要ベンダーの自社評価から引用している。

## 1. まず結論から：Opus 4.7は"全方位ヤバい"

[![新型.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2F848a69bc-6f5a-4a14-9d31-035162aa1808.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4cdfaa0e9de3e2e48bd256c9adf7e830)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2F848a69bc-6f5a-4a14-9d31-035162aa1808.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4cdfaa0e9de3e2e48bd256c9adf7e830)

比喩から入らせてほしい。**Opus 4.7 は、同じボディのままエンジンだけ載せ替えた新型スーパーカー**である。価格は据え置き（$5 / $25 per 1M tokens）、ガワ（API仕様）もほぼそのまま。なのに0-100加速（[SWE-bench Verified](https://qiita.com/GeneLab_999/items/a557780347f52a7cda49)）が 80.8% → **87.6%** に跳ね、カメラ解像度（vision）は**3.3倍**、新しいドライビングモード（xhigh effort）まで追加された。

しかも、サーキットラップタイム比較では GPT-5.4 と Gemini 3.1 Pro をコーディング・エージェントワークで置き去りにしている。ガチで草。

| 指標 | Opus 4.6 | Opus 4.7 | GPT-5.4 | Gemini 3.1 Pro |
| --- | --- | --- | --- | --- |
| [SWE-bench Verified](https://qiita.com/GeneLab_999/items/a557780347f52a7cda49) | 80.8% | **87.6%** | - | 80.6% |
| SWE-bench Pro | 53.4% | **64.3%** | 57.7% | 54.2% |
| GPQA Diamond | 91.3% | **94.2%** | 94.4% | 94.3% |
| OSWorld-Verified | 72.7% | **78.0%** | 75.0% | - |
| CharXiv (visual) | 69.1% | **82.1%** | - | - |

→ 細かい話はあとに回して、まずは「**同じ値段でここまで上がるの、もう反則では**」という感想を共有したかった。

---

## 2. リリース情報サマリ

まずは事実を淡々と押さえる。これ一枚でOKという資料。

| 項目 | 内容 |
| --- | --- |
| リリース日 | 2026年4月16日 |
| モデルID | `claude-opus-4-7` |
| 入力価格 | $5 / 1M tokens（Opus 4.6と同じ） |
| 出力価格 | $25 / 1M tokens（Opus 4.6と同じ） |
| コンテキストウィンドウ | 1M input tokens / 128K output tokens |
| 画像対応 | 最大2,576px（長辺）/ 約3.75メガピクセル |
| Effort levels | `low` / `medium` / `high` / **`xhigh`（新設）** / `max` |
| トークナイザー | 更新（同じテキストが1.0-1.35倍のトークンに） |
| 利用可能プラットフォーム | Claude.ai (Pro/Max/Team/Enterprise) / Claude API / Amazon Bedrock / Google Vertex AI / Microsoft Foundry / GitHub Copilot |

### 2.1 API呼び出しの最小例

[Python](https://qiita.com/GeneLab_999/items/d2910c3c6dc1f4d78fb9) から Claude Opus 4.7 を叩く最小構成はこう。

クリックでサンプルコードを展開

```
import anthropic

client = anthropic.Anthropic()

# Opus 4.7 を xhigh effort で呼び出す
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Design a distributed system that handles 100k RPS across 3 regions."
        }
    ],
    # 新設の xhigh effort level（high と max の中間）
    # Claude Code ではデフォルトが xhigh に引き上げられた
    extra_headers={"anthropic-beta": "effort-2026-04-16"},
)

print(response.content[0].text)
```

モデルIDを書き換えるだけで基本は動く。**ただし注意点が2つ**あるので、後述の「5. Opus 4.6 からの移行ガイド」で必ず確認してほしい。

---

## 3. 新機能の徹底解剖

### 3.1 xhigh effort ─ 新しいドライビングモードの追加

[![xhigh.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2F75a4b286-0201-4025-9e4f-4b5789ccc955.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=84789017c1a3d2883692b16dd6197045)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2F75a4b286-0201-4025-9e4f-4b5789ccc955.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=84789017c1a3d2883692b16dd6197045)

スーパーカーに「スポーツ」と「トラック」の間に新モード「スポーツ+」が増えた、と思ってくれるとわかりやすい。従来の `high` と `max` の間に **`xhigh`** が挟まれた。

**Anthropic公式推奨**：コーディング／エージェンシック用途では、まず `high` または `xhigh` から始めるのが吉。Claude Code 全プランでデフォルトが `xhigh` に引き上げられた。

| effort | 用途 | コスト感 |
| --- | --- | --- |
| `low` | 軽い応答、チャット | 安い |
| `medium` | 一般的な質問応答 | 普通 |
| `high` | 複雑な推論、設計判断 | やや高い |
| **`xhigh`** | **難度の高いコーディング・長時間タスク** | **高い（でも max より軽い）** |
| `max` | 最難関タスクの最終手段 | 高い |

注目すべきは、**Opus 4.7 の xhigh @ 100K tokens が、Opus 4.6 の max @ 200K tokens をすでに上回っている**点。同じ予算なら Opus 4.7 のほうが深く考えてくれるということで、これは単なる値上げではなく純粋な効率改善。

### 3.2 vision が3.75メガピクセルに ─ カメラ解像度が一気に3.3倍

なにがデカいかというと、**Computer Use エージェントがダッシュボードの小さな文字やボタンを読めるようになった**ことだ。XBOW が公表した visual-acuity ベンチマークでは、Opus 4.6 の **54.5%** から Opus 4.7 で **98.5%** へ跳ねている。もはや別人。

解像度が上がるぶん画像トークン消費も増える。高解像度が不要な用途では事前にダウンサンプリングしておくほうがコスト面で賢い。

### 3.3 自己検証 ─ "自分のコードを自分でテストする"新しい振る舞い

[![CoT.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2Fb8191f0b-4b7d-4f47-946a-5866d9eeaf91.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d2aed3097a229cf825141b15b862d192)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2Fb8191f0b-4b7d-4f47-946a-5866d9eeaf91.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d2aed3097a229cf825141b15b862d192)

これが一番、**エンジニアとして感涙**ポイント。Anthropic の公式説明によると、Opus 4.7 は出力を報告する前に自ら検証する方法を考案する。

単なる Chain of Thought ではなく、**元の要件と照合して、出力がちゃんと問題を解いているか検証する**という振る舞いが組み込まれた。ClaudeCode勢もCursor勢もわかるっしょ、、、何度いままで「そうじゃない！！」って生成物に対して思ったかwwwwまじこれこれ、これだよぉ、、、待ってたよぉ！！！

Vercel のエンジニアが言うには「Claude Opus 4.7 は Vercel にとって確実なアップグレード。ワンショットのコーディングタスクで 4.6 より正しく完全で、自分の限界について明らかに正直になっている。作業開始前にシステムコードの証明まで行う」そう。これは Claude 系でも見たことない新しい挙動だという。

### 3.4 `/ultrareview` ─ 複数エージェントによる深層コードレビュー

[![統合.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2Fe71ecc96-571c-49d4-8e59-71bb8d513d42.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=69b7d31934820af12e8cf5d76faf1ccb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2Fe71ecc96-571c-49d4-8e59-71bb8d513d42.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=69b7d31934820af12e8cf5d76faf1ccb)

Claude Code に新コマンドが追加された。`/ultrareview` は単一のClaude インスタンスでコードを見るのではなく、**複数の専門エージェントを並列起動してレビューする**機能。セキュリティ担当、ロジック担当、パフォーマンス担当、スタイル担当がそれぞれ独立に見て、最後に統合レポートを出す。

Pro/Max ユーザーには無料で3回の ultrareview が提供される。まずはお試し枠で自分のリポジトリに流してみるのがオススメ。

### 3.5 Task budgets（public beta）

長時間走るエージェントのトークン消費に上限を設定できる新機能。Auto mode で「気がついたら請求がヤバいことに (;ﾟдﾟ)ﾎﾟｶｰﾝ」というアクシデントを防ぐための安全弁。

### 3.6 Auto mode の Max プラン開放

これまで Teams / Enterprise / API 限定だった Claude Code の Auto mode が、Max プランでも使えるようになった。「全許可スキップよりは安全な選択肢」として位置づけられている。

---

## 4. ベンチマーク徹底解剖

ここからが**この記事の本丸**。Opus 4.7 がどこで勝ち、どこで負けているかを全部見ていく。

### 4.1 コーディング系 ─ 完全に支配している

**[SWE-bench Verified](https://qiita.com/GeneLab_999/items/a557780347f52a7cda49) で +6.8pt、SWE-bench Pro で +10.9pt、CursorBench で +12pt**。一世代で二桁ポイント伸びる機械学習モデルって、もう滅多にお目にかかれない。

[vLLM](https://qiita.com/GeneLab_999/items/bdb9b1aa4a47bdecbfdf) や [llama.cpp](https://qiita.com/GeneLab_999/items/b4303a002abb4d98f929) でローカル推論を頑張ってる民からすると「フロンティアモデル、さらに先に行ったのか…」という気持ちになる。

特筆すべきはSWE-bench Pro の +10.9ポイント向上のほうが Verified より大きいこと。これは「より難しい、汚染の少ない問題で伸びている」証拠で、単なるベンチマークハックではなく本質的な能力向上を示している。

### 4.2 エージェンシック／ツール使用 ─ こっちも圧勝

| ベンチマーク | Opus 4.6 | Opus 4.7 | 勝者 |
| --- | --- | --- | --- |
| MCP-Atlas（スケール化ツール使用） | 73.9% | **77.3%** | Opus 4.7 |
| OSWorld-Verified（Computer Use） | 72.7% | **78.0%** | Opus 4.7 |
| Finance Agent v1.1 | 60.7% | **64.4%** | Opus 4.7（SOTA） |
| BigLaw Bench | - | 90.9% | Opus 4.7 |

Finance Agent は**state-of-the-art（SOTA）**。[MCP](https://qiita.com/GeneLab_999/items/d1299630fc2c0325003b) まわりの改善も効いている。

### 4.3 視覚系 ─ メガ進化

| ベンチマーク | Opus 4.6 | Opus 4.7 |
| --- | --- | --- |
| CharXiv（科学図表の理解） | 69.1% | **82.1%** |
| arXiv Reasoning（with tools） | 84.7% | **91.0%** |
| XBOW Visual Acuity | 54.5% | **98.5%** |

XBOW の 54.5% → 98.5% は、もはやベンチマークが壊れたのかと疑うレベルの跳ね。実際には「これまで無理ゲーだった用途が一気に実用圏に入った」ということ。

### 4.4 知識労働 ─ ここでも一人勝ち

**GDPVal-AA**（Elo スコアベースの経済的に価値のある知識労働評価）でも SOTA。

| モデル | GDPVal-AA Elo |
| --- | --- |
| **Opus 4.7** | **1753** |
| GPT-5.4 | 1674 |
| Gemini 3.1 Pro | 1314 |

GPT-5.4 に対して +79 Elo、Gemini 3.1 Pro には +439 Elo。チェスで言えば「世界トップ棋士に平均2-3勝差」くらいのレーティング差。

### 4.5 推論系 ─ 激戦区で僅差

大学院レベルの推論を測るGPQA Diamondでは、Opus 4.7 が 94.2%、GPT-5.4 Pro が 94.4%、Gemini 3.1 Pro が 94.3%で、差はノイズの範囲内。フロンティアモデルは事実上このベンチマークを飽和させた。

→ つまり「生の推論力」での差別化フェーズは終わり、**応用タスク（コーディング・エージェント・長時間ワーク）での実性能**が勝負の土俵になっている。

### 4.6 ただし…正直に言うと負けてる領域もある

褒めちぎる記事と言いつつ、公正性のためにネガティブな数値も書く。LAPRAS の独自性4.5には率直さが効く（たぶん）。

| ベンチマーク | Opus 4.7 | 勝者 |
| --- | --- | --- |
| BrowseComp（エージェンシックWeb検索） | 79.3%（Opus 4.6の83.7%から後退） | GPT-5.4 Pro: 89.3% |
| Terminal-Bench 2.0 | 69.4% | GPT-5.4: 75.1%※ |
| MMMLU（多言語Q&A） | 91.5% | Gemini 3.1 Pro: 92.6% |
| CyberGym | 73.1% | Opus 4.6: 73.8%（わずかに後退） |

※ GPT-5.4 の Terminal-Bench スコアは自社報告のため直接比較不可という注釈付き。

**Web検索ベースのエージェントを本番で運用している場合**、Opus 4.7 に移行する前に BrowseComp の retrogression を自社ワークロードでテストすることを強く推奨。GPT-5.4 Pro がまだ優位。

CyberGym のわずかな後退は訓練中にサイバー能力を意図的に差別的に削減する実験を行った結果の副作用と公式が認めている。Project Glasswing で明らかにした Mythos Preview のサイバー能力リスクを踏まえ、**Opus 4.7 はあえて刃を鈍らせている**。

---

## 5. Opus 4.6 からの移行ガイド

「モデルIDを書き換えるだけ」で9割は動くが、2つ罠がある。

### 5.1 罠①：トークンが1.0-1.35倍に増える

Opus 4.7 は更新されたトークナイザーを使用し、同じ入力がより多くのトークンにマップされる可能性がある ─ コンテンツタイプによって約1.0-1.35倍

つまり**同じテキストでも請求額が最大35%増える可能性がある**。

| コンテンツタイプ | トークン増加率（概算） |
| --- | --- |
| 英文プレーンテキスト | 1.0倍〜1.05倍 |
| 日本語プレーンテキスト | 1.1倍〜1.2倍 |
| コード・構造化データ | 1.15倍〜1.35倍 |

→ **コード中心のワークロードほど影響がデカい**。

### 5.2 罠②：高 effort では思考量が増える

xhigh/max では前ターンまでの思考を参照しながら「より深く」考える設計になっており、出力トークンも従来より多く生成される。品質は上がるが課金は増える。

**Task budgets（public beta）を必ず設定する**こと。上限を入れないと、長時間エージェントが意図せず高額化するリスクがある。

### 5.3 罠③：instruction following が厳密化

[![EF.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2F914d6f66-692a-43f4-b3c2-0344a4630f8b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0d395d1d07cc01e001e2a7a9d4010415)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908981%2F914d6f66-692a-43f4-b3c2-0344a4630f8b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0d395d1d07cc01e001e2a7a9d4010415)

これは罠というより**仕様の向上**なのだが、影響が大きい。

Anthropic 公式によれば以前のモデルが指示を緩く解釈したり部分的にスキップしていた箇所で、Opus 4.7 は指示を文字通りに受け取る。

つまり、**Opus 4.6 向けに「曖昧な表現でもなんとなく汲んでくれる」前提で書いたプロンプトは、Opus 4.7 で予想外の結果を出す**ことがある。

**対策**：CLAUDE.md、システムプロンプト、エージェントのハーネスを一通り見直すこと。特に「〜してください（でも本当は〜も含めて欲しい）」のような含みのある書き方は全部明文化する。

### 5.4 トークン効率は実は改善している

ここまで「コスト上がる！」と書いてきたが、**正味ではコスト効率が改善している**のがミソ。Anthropic 内部の coding eval では、全effort レベルでトークン使用量あたりのスコアが改善されている。

さらに Hex の CTO いわく「低effortのOpus 4.7は中effortのOpus 4.6とほぼ同等」。つまり**effortを1段階下げるだけで、旧モデルと同じ品質が手に入る**。

→ 思考力を落とさずコストを抑えたいなら、まず effort を1段階下げてベースラインを測るのが正解。

---

## 6. 競合比較 ─ いつ Opus 4.7 を選ぶべきか

### 6.1 選択マトリクス

| ユースケース | 推奨モデル | 理由 |
| --- | --- | --- |
| Claude Code / Cursor でのコーディング | **Opus 4.7** | SWE-bench Pro / CursorBench で圧勝 |
| 長時間実行のエージェンシックワーク | **Opus 4.7** | 自己検証、long-horizon coherence |
| 高解像度スクリーンショットを扱うComputer Use | **Opus 4.7** | 3.75MP + XBOW 98.5% |
| 財務分析／法務文書分析 | **Opus 4.7** | Finance Agent SOTA、BigLaw 90.9% |
| Web検索エージェント | GPT-5.4 Pro | BrowseComp 89.3% > 79.3% |
| 多言語対応重視 | Gemini 3.1 Pro | MMMLU 92.6% |
| 大量処理でコスト最優先 | Gemini 3.1 Pro | $2/$12（Opus の半額以下） |

### 6.2 Mythos Preview との関係

ここが今回のリリースの**エモい**ところ。Anthropic はOpus 4.7 は [Mythos](https://qiita.com/GeneLab_999/items/2d1948b5f6d424798960) と比較して性能が劣ることを公に認めている。

なぜ Mythos を一般公開しないのか。  
→ Project Glasswing で Mythos Preview の公開を限定し、能力の低いモデルで新しいサイバー安全対策をまずテストする方針。つまり Opus 4.7 は「**[Mythos](https://qiita.com/GeneLab_999/items/2d1948b5f6d424798960) クラスを広く展開するための踏み台**」として位置づけられている。

**逆に言うと、将来の Mythos 一般公開に向けた Safety 学習の成果が Opus 4.7 には織り込まれている**。Anthropic の評価ではOpus 4.7 は Opus 4.6 と同等の安全プロファイルで、欺瞞、おべっか、悪用への協力といった懸念される行動は低い率。正直さとプロンプトインジェクション耐性では Opus 4.6 より改善されている。

---

## 7. エンタープライズパートナーの声 ─ 現場からのリアル

ベンチマークの数字だけでは見えない、現場の体感を少し拾っておく。これが一番説得力ある。

XBOWのOege de Moor CEOは、コンピュータ使用ワークにおいてOpus 4.7は段階的変化であり、視覚視力ベンチマークで98.5%を記録し、Opus 4.6の54.5%から大幅に向上していると報告している

Vercel の Joe Haddad（Distinguished Software Engineer）は、Opus 4.7 は Vercel にとって問題なくアップグレードできる堅実な改善であり、one-shot coding タスクで Opus 4.6 より正確で完全、自身の限界について目に見えて正直、と評価している

楽天の梶悠介氏（AI for Business General Manager）は、Rakuten-SWE-Bench において Claude Opus 4.7 は Opus 4.6 の3倍の本番タスクを解決し、Code Quality と Test Quality で二桁の向上を示したと報告

楽天の「**3倍**」は特にインパクトがある。本番ワークフローでここまで差が出るモデルチェンジは稀。

---

## 8. 実際どう使えばいいのか ─ ユースケース別スタートガイド

### 8.1 Claude Code ユーザー

デフォルトで Opus 4.7 / xhigh effort になっているので、基本は何もしなくていい。ただし以下を確認：

```
# モデル確認
claude config get model

# xhigh がデフォルトになっているか確認
claude config get effort

# /ultrareview を試す（Pro/Max は3回無料）
# Claude Code 内で
/ultrareview
```

### 8.2 API 直接利用のユースケース

クリックでPythonサンプルを展開

```
import anthropic

client = anthropic.Anthropic()

# シンプルなコード生成
def generate_code(prompt: str, effort: str = "xhigh") -> str:
    """
    Claude Opus 4.7 でコードを生成する
    
    Args:
        prompt: ユーザープロンプト
        effort: low / medium / high / xhigh / max
    """
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "anthropic-beta": "effort-2026-04-16",
        },
        metadata={"effort_level": effort},
    )
    return response.content[0].text

# 複数ターンでのエージェンシックワーク
def multi_turn_agent(task: str, max_turns: int = 10):
    """
    Opus 4.7 は複数ターン後半でより深く考える特性がある
    Task budgets を設定することを推奨
    """
    messages = [{"role": "user", "content": task}]
    
    for turn in range(max_turns):
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        
        if response.stop_reason == "end_turn":
            break
    
    return messages

if __name__ == "__main__":
    # 1. コード生成の例
    code = generate_code(
        "Rustで tokio を使った並列HTTPクライアントを書いて"
    )
    print(code)
    
    # 2. 長時間エージェントの例
    conversation = multi_turn_agent(
        "このリポジトリのバグを修正してPRを作成して"
    )
```

### 8.3 Amazon Bedrock 経由

Opus 4.7 は Amazon Bedrock で米国東部（バージニア北部）、アジア太平洋（東京）、ヨーロッパ（アイルランド）、ヨーロッパ（ストックホルム）リージョンで利用可能。東京リージョンにあるのは日本のユーザーに朗報。

---

## 9. Opus 4.7 の Safety プロファイル

ここも褒めどころ。Opus 4.7 はアライメント評価で「おおむね良好にアラインされ信頼できるが、完全に理想的な振る舞いではない」と結論付けられた。

| 評価軸 | Opus 4.7 vs Opus 4.6 |
| --- | --- |
| 欺瞞（Deception） | 同程度（低率） |
| おべっか（Sycophancy） | 同程度（低率） |
| 悪用への協力（Misuse） | 同程度（低率） |
| 正直さ（Honesty） | 改善 |
| プロンプトインジェクション耐性 | 改善 |
| 規制物質の過剰詳細な害削減アドバイス | やや後退 |

**"いいところも悪いところも公式が正直に開示している"**、この姿勢自体が Anthropic を信頼できる理由でもある。

---

## 10. 学習ロードマップ ─ 次に何をすべきか

### 3段階の学習ステップ

| 段階 | 目標 | 期間 |
| --- | --- | --- |
| 初級 | モデルID差し替え、xhigh の体感 | 1日 |
| 中級 | プロンプト再調整、Task budgets、ultrareview 活用 | 1週間 |
| 上級 | Multi-agent 設計、Computer Use エージェント構築、自己検証フローの組み込み | 1ヶ月 |

---

## 11. まとめ ─ Opus 4.7 は何が"ヤバい"のか

この記事で伝えたかったことを、最後にもう一度整理する。

1. **価格据え置きで性能が純粋に上がった** ─ [SWE-bench Verified](https://qiita.com/GeneLab_999/items/a557780347f52a7cda49) +6.8pt / Pro +10.9pt / CursorBench +12pt。値段そのままで二桁ポイント改善は、今時お目にかかれない。
2. **vision が別物レベル** ─ 3.75MP、XBOW visual-acuity で 54.5% → 98.5%。Computer Use エージェントの実用性が一気に立ち上がった。
3. **自己検証する AI が来た** ─ 出力する前に自分で検証する挙動は Claude 系で初。エージェンシックワークの信頼性が根本的に変わる。
4. **ただし Mythos Preview には及ばない** ─ Anthropic 自身が正直に認めている。Opus 4.7 は"Mythos 一般公開に向けた safety 学習の最初の実戦投入"という位置づけ。
5. **GPT-5.4 / Gemini 3.1 Pro を完全に置き去りにしたわけではない** ─ BrowseComp、Terminal-Bench、多言語では負けている。用途に応じた選択が必要。

所感として、**Opus 4.7 は革命ではなく地道な進化の積み重ね**で、それが逆に頼もしい。派手な新機能の乱れ撃ちではなく、日常的に使っている開発者が「あ、仕事が減った」と静かに気づく類の改善。個人的にはこういうリリースが一番好きだ。

[RTX5090](https://qiita.com/GeneLab_999/items/ab544a30c2d43eeb00bb) でローカル [LLM](https://qiita.com/GeneLab_999/items/7f1bd2de313bdd7ca423) を動かしてる身としては、「商用フロンティアモデルはここまで来たのか…」と [Transformer](https://qiita.com/GeneLab_999/items/5e665e71ae39c197c935) の進化の速度に改めて舌を巻いている次第。

**今すぐやるべきアクション**：

1. Claude Code を使っているなら、xhigh effort で難しいタスクを1つ投げてみる
2. `/ultrareview` を自分のリポジトリで試す（Pro/Max は3回無料）
3. API 利用なら、モデルIDを `claude-opus-4-7` に変更して1週間のコストと品質を計測する

---

## 12. 参考文献

公式ドキュメントは必ず一次情報に当たること。

---

## 筆者X（旧Twitter）

記事の更新情報や、AI/LLM/ローカル推論まわりの速報はこちらで流しています。フォローしていただけると励みになります。
