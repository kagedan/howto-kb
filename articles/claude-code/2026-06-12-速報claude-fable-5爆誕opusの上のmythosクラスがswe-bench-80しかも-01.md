---
id: "2026-06-12-速報claude-fable-5爆誕opusの上のmythosクラスがswe-bench-80しかも-01"
title: "【速報】Claude Fable 5爆誕！Opusの上のMythosクラスがSWE-Bench 80%、しかも6月22日まで無料という衝撃"
url: "https://qiita.com/emi_ndk/items/3e8e095895713bcbde8e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "GPT", "qiita"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

**「Opusが最上位」という常識が、たった1日で過去になった。**

2026年6月9日、Anthropicが **Claude Fable 5** をリリースした。これは Opus 4.8 の上に位置する、**一般提供としては史上初の「Mythosクラス」モデル**だ。

そして信じがたいことに、**6月22日までPro/Max/Team/Enterpriseユーザーは無料**で使える。つまり今この瞬間、月$20のProユーザーがAnthropic史上最強のモデルを追加料金なしで叩けるということだ。

## 結論から言うと

- **Claude Fable 5** = Anthropicが一般提供した中で**過去最強のモデル**。「Mythosクラス」（Opusの上のティア）が初めて誰でも使える形で降りてきた
- **SWE-Bench Pro 80.3%**。GPT-5.5の**58.6%**を20ポイント以上引き離し、公開されたほぼ全ベンチマークでSOTA
- 価格は **$10 / $50（100万トークンあたり入力/出力）** — Opus 4.8の約2倍
- **6月9日〜22日の期間限定で、Pro / Max / Team / Enterprise ユーザーは無料**
- 提供先：Claude API、Amazon Bedrock、そして6月11日には **Microsoft Foundry**（GitHub Copilotのエージェントも駆動）
- 同時に、さらに上位の **Claude Mythos 5** が「trusted access」ユーザー向けに導入

:::note info
**今すぐやるべきこと：6月22日までの無料ウィンドウ中に、自分のワークロードでFable 5を試す。** 期限後は$10/$50の従量課金になるので、「自分のタスクで2倍の価格に見合うか」を無料のうちに見極めるのが合理的です。
:::

## 「Mythosクラス」とは何か

Anthropicのモデルラインは長らく Haiku / Sonnet / Opus の3段だった。Fable 5はこの上に新しい段を作る。

| ティア | モデル | 位置づけ |
|--------|--------|---------|
| **Mythos** | Claude Mythos 5 | 最上位。trusted access（限定提供） |
| **Fable** | **Claude Fable 5** | **Mythosクラスを一般提供向けにしたモデル** ← NEW |
| Opus | Claude Opus 4.8 | これまでの最上位（プレミアム） |
| Sonnet | Claude Sonnet 4.6 | バランス型 |
| Haiku | Claude Haiku 4.5 | 高速・軽量 |

注目すべきは、TechCrunchが報じた文脈だ。Anthropicは、**「AIが危険になりつつある」と警告した数日後に、史上最強モデルを公開**した。一見矛盾しているが、これには仕掛けがある（後述のセーフガード参照）。

## 📊 ベンチマーク：GPT-5.5を20ポイント突き放す

公開ベンチマークの中で最も衝撃的なのがソフトウェアエンジニアリング系だ。

| ベンチマーク | Claude Fable 5 | GPT-5.5 |
|-------------|---------------|---------|
| **SWE-Bench Pro** | **80.3%** | 58.6% |

SWE-Bench Proは実際のGitHub issueを修正できるかを測る、エージェント型コーディングの実戦ベンチマーク。ここで**80%超え**は、「10個のissueのうち8個を自力で直せる」水準に達したことを意味する。

ソフトウェアエンジニアリングだけではない。Anthropicの発表では、**ナレッジワーク、ビジョン、科学研究**などほぼ全テスト領域でSOTAを主張している。

### Stripeの事例：50Mライン規模のマイグレーションを「1日」で

早期テストでStripeが報告した数字が強烈だ。

> **5,000万行のRubyコードベース**で、本来チーム全体で**2ヶ月以上**かかるコードベース全体のマイグレーションを、Fable 5は**1日**で完了した。

:::note warn
ベンチマークも事例も、現時点ではAnthropic発表ベースの数字です。第三者検証はこれから出てきます。「自分のコードベースでどうか」は、無料期間中に自分で確かめるのが一番確実です。
:::

## 💰 価格：$10/$50は高いのか

| モデル | 入力（/1M tok） | 出力（/1M tok） |
|--------|----------------|----------------|
| **Claude Fable 5** | **$10** | **$50** |
| Claude Opus 4.8 比 | 約2倍 | 約2倍 |
| GPT-5.5（標準）比 | 2倍（$5） | 約1.7倍（$30） |

単価だけ見れば「高い」。しかし先日の記事でも書いた通り、エージェント時代のコストは**単価 × 完遂までの総トークン**で決まる。

SWE-Bench Proで80% vs 58%という差は、**「一発で直る」vs「何度もリトライして直らない」の差**でもある。失敗したエージェントランのトークンは全額ドブに捨てる金だ。難タスクでは、高単価モデルの方が**総額では安くつく**ケースが普通にある。

> 筆者の見解：使い分けの原則は変わりません。大量の定型処理は安いモデル、**「失敗コストが高い難タスク」にFable 5**。全部Fable 5に流すのは、tokenmaxxing地獄の再来です。

## 🛡️ 面白いのは「セーフガード」の設計

「危険だと警告した直後に最強モデルを出す」矛盾への、Anthropicの答えがこれだ。

**一部のトピックに関するクエリは、Fable 5ではなくOpus 4.8が応答する。**

- センシティブな領域では、自動的に一段下のモデルへフォールバック
- この安全装置が発動するのは**平均でセッションの5%未満**

つまり「最強の能力は提供するが、リスクの高い領域では能力を意図的に絞る」という、**モデル単位ではなくクエリ単位の能力制御**だ。

:::note info
これはエンジニアリング的に重要な前例です。「1つのモデルを出すか出さないか」の二択ではなく、**ルーティングで危険領域だけ別モデルに逃がす**。自社でLLMアプリを作る際のセーフガード設計にもそのまま応用できる発想です。
:::

さらに上位の **Claude Mythos 5** が「trusted access」（審査されたユーザー向け限定提供）なのも同じ思想で、能力のティアとアクセス制御を分離している。

## 🚀 どこで使えるか

| 経路 | 状況 |
|------|------|
| Claude API | 提供中（model: `claude-fable-5`） |
| claude.ai / Claude Code | Pro / Max / Team / Enterprise で**6月22日まで無料** |
| Amazon Bedrock | 提供中 |
| **Microsoft Foundry** | **6月11日から提供**。GitHub Copilot / Foundry Agent Service のエージェントを駆動 |

Microsoft Foundry入りが象徴的だ。Build 2026でMicrosoftは自社製MAIモデルを7本発表したばかりだが、それでも**最強モデルはカタログに並べる**。「自社モデルで殴り合いつつ、最強の他社モデルも売る」というマルチモデル戦略は、もはやクラウド各社の標準になった。

## ⏰ 6月22日の「カラクリ」に注意

無料ウィンドウは**6月9日〜22日**。ここで先日の記事を思い出してほしい。

**6月15日から、Agent SDK / `claude -p` / GitHub Actions連携は別枠のAPIクレジット課金に移行する。**

つまりこうなる：

- **〜6月14日**：サブスクで対話もヘッドレスも使い放題＋Fable 5無料
- **6月15日〜22日**：対話型はFable 5無料継続。ただし**ヘッドレス系はクレジット消費**が始まる
- **6月23日〜**：Fable 5は$10/$50の従量。Proの$20クレジットだと**Fable 5ヘッドレスは一瞬で溶ける**

:::note warn
「無料だから」とFable 5を自動化パイプラインに組み込むと、6月23日に請求書で泣くことになります。**無料期間は「評価期間」と割り切り**、本採用は単価を織り込んで判断しましょう。
:::

## 今週やるべきことチェックリスト

1. **Claude Code / claude.ai でFable 5を有効化**して、普段のタスクを流してみる（〜6/22無料）
2. **一番難しかった過去タスク**（失敗したリファクタ、巨大マイグレーション）でOpus 4.8と比較
3. 自動化パイプラインに入れる場合は、**$10/$50前提でROI計算**してから
4. セーフガード（Opus 4.8フォールバック）が自分のユースケースで発動するか確認
5. Bedrock / Foundry 利用者は、リージョンと提供状況をチェック

## まとめ

- **Claude Fable 5**：一般提供では史上初の**Mythosクラス**。Opus 4.8の上位ティア
- **SWE-Bench Pro 80.3%**（GPT-5.5は58.6%）、ほぼ全ベンチでSOTA
- Stripeは**50M行のマイグレーションを1日**で完了と報告
- 価格 **$10/$50**、ただし**6月22日までPro/Max/Team/Enterpriseは無料**
- セーフガードは**クエリ単位でOpus 4.8にフォールバック**（発動は5%未満）という新設計
- 6月15日の課金変更と重なるため、**ヘッドレス自動化への投入は要計算**

「Opusの上」が当たり前に使える時代が、警告とセットでやってきました。あなたは無料期間中に何を試しますか？**Fable 5にやらせてみたい最難関タスク**をコメントで教えてください！

役に立ったら**いいね👍と保存📌をお願いします！** 無料期間が終わる前に、ぜひ試してみてください。

## 参考リンク

Claude Fable 5 and Claude Mythos 5 | Anthropic

https://www.anthropic.com/news/claude-fable-5-mythos-5

Anthropic brings Mythos to the masses with Claude Fable 5 | VentureBeat

https://venturebeat.com/technology/anthropic-brings-mythos-to-the-masses-with-claude-fable-5-its-most-powerful-generally-available-model-ever

Anthropic releases Claude Fable, a version of Mythos, days after warning AI is becoming too dangerous | TechCrunch

https://techcrunch.com/2026/06/09/anthropic-released-claude-fable-5-its-most-powerful-model-publicly-days-after-warning-ai-is-getting-too-dangerous/

Claude Fable 5: Benchmarks, Pricing & the June 22 Catch

https://claudefa.st/blog/models/claude-fable-5-mythos-5
