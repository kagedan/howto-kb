---
id: "2026-06-28-締め出しanthropic最強fable-5日本人は使用禁止米輸出規制でopus止まりになった全真相-01"
title: "【締め出し】Anthropic最強「Fable 5」、日本人は使用禁止。米輸出規制でOpus止まりになった全真相"
url: "https://qiita.com/emi_ndk/items/b439b91270da1b24d49c"
source: "qiita"
category: "ai-workflow"
tags: ["Gemini", "GPT", "qiita"]
date_published: "2026-06-28"
date_collected: "2026-06-29"
summary_by: "auto-rss"
query: ""
---

## 先週「今すぐ試せ」と書いた、その最強モデルが消えた

つい先日、こう書いた。「Opusの上に立つ史上最強モデル **Claude Fable 5** が来た。6月22日まで無料だから今すぐ試せ」と。

その記事、もう半分が無効になった。

なぜなら、**あなたはもうFable 5を使えない**からだ。日本に住んでいる限り。

2026年6月12日、米国政府が異例の命令を出した。Anthropic最強のモデル群を、**全外国籍ユーザーから取り上げろ**、と。日本人開発者であるあなたも、当然その「外国籍」に含まれている。

## 結論から言うと

- 6月12日、米政府がAnthropicに**輸出規制ディレクティブ**を発令。Fable 5とMythos 5を全外国籍ユーザー（米国内外を問わず、Anthropicの外国籍社員すら含む）から遮断するよう命令
- Anthropicはコンプライアンスのため、**全顧客**に対して両モデルを即時停止せざるを得なかった
- 理由は、Fable 5のセーフガードを突破してMythos 5のサイバー攻撃能力にアクセスする手法が見つかったとされること。ただし政府は技術的な詳細を示していない
- 6月27日時点で、Fable 5は一般ユーザーには**完全に停止中**。Mythos 5は米重要インフラ企業など一部にのみ部分復活
- 7月8日、AnthropicはプライバシーポリシーをID＋生体認証必須に更新予定。これが「米国民のみ復活」の仕組みになると見られる
- **日本の開発者の現実解はOpus 4.8**。当面それしかない

:::note alert
Fable 5は消えたわけではない。「米国民だけが使える」モデルへと変わりつつある。日本にいるあなたの選択肢は、当面Opus 4.8です。
:::

## 何が起きたのか：18日間のタイムライン

| 日付 | 出来事 |
|------|--------|
| 6月9日 | Fable 5一般提供開始（Mythosクラス、SWE-Bench Pro 80%超） |
| 6月12日 17:21 ET | 米政府の輸出規制ディレクティブが着弾 |
| 6月12日 | Anthropic、全顧客向けにFable 5・Mythos 5を停止 |
| 6月13日 | Al Jazeera、Fortuneなど各社が一斉報道 |
| 6月17日 | 英国向けの適用除外案が頓挫 |
| 6月27日 | Mythos 5が「Annex A」対象に限定復活。Fable 5は依然停止 |
| 7月8日 | ID＋生体認証を求める新プライバシーポリシー発効（予定） |
| 8月1日 | 6月2日大統領令の「covered frontier model」枠組み期限 |

書簡は商務省からCEOのDario Amodei宛に送られ、Anthropic自身の説明によれば**6月12日17時21分（東部時間）**に届いた。そして同社はこう述べている。

> コンプライアンスを確保するため、我々は全顧客に対してFable 5とMythos 5を突然停止せざるを得ない。

## なぜ止められたのか：「サイバー兵器」懸念

政府の言い分は、サイバー兵器化のリスクだ。

Fable 5は内部的にMythos 5を土台にしている。そしてMythos 5は、**コードベースを読んで脆弱性を見つける能力**に極めて長けている。このセーフガードをjailbreakで外す手法が見つかった、というのが停止理由とされる。

ただし、話はそう単純ではない。

- 政府の書簡は、具体的な技術的詳細を**一切示していない**
- Anthropicは「その能力は他社モデルでも広く利用可能だ」と反論
- Anthropic自身はこの一件を「誤解（a misunderstanding）」と表現している

:::note info
Anthropicは「この基準を適用すれば、全フロンティアモデル提供企業の新規モデル展開が事実上すべて止まる」と警告しています。一企業の問題ではなく、業界全体の前例になりかねない事案です。
:::

## 影響を受けるモデル・受けないモデル

| モデル | 状態 |
|--------|------|
| Claude Fable 5 | 停止（一般ユーザー利用不可） |
| Claude Mythos 5 | 一部のみ復活（Annex A対象） |
| Claude Opus 4.8 | 通常通り利用可 |
| その他のClaudeモデル | 影響なし |

ポイントは明確だ。**Opus 4.8を含む既存モデルは無傷**で動いている。失われたのは「最上位の2モデル」だけ。だからこそ、Anthropicも公式に「他のモデルへ移行してほしい」と案内している。

## 現在の状況（6月27日時点）

### Fable 5：一般ユーザーには完全停止

ディレクティブは依然として有効で、違反には**刑事・民事の罰則**が伴う。一般ユーザーが触れる手段は、今のところ存在しない。

### Mythos 5：ごく一部のみ部分復活

6月27日、Mythos 5は「Annex A」と呼ばれる限定枠で復活した。対象は次の組織だけだ。

```
- 米国の重要インフラ企業（Annex A対象）とその外国籍従業員
- Anthropicの外国籍社員
- 米政府の文民機関・国立研究所
```

これ以外がアクセスするには、**輸出ライセンスが必要**になる。一般の開発者には事実上、門が閉じている。

## 7月8日問題：日本人にとっての本丸

ここが、日本の読者にとって一番重要なところだ。

7月8日に発効するAnthropicの新プライバシーポリシーは、**政府発行ID＋生体認証**の提出を求める。これは「Fable 5を、検証済みの米国民にだけ戻す」ための仕組みと見られている。

つまり、こういう分岐になる。

- **米国民**：ID認証を通せば、Fable 5復活の可能性あり
- **日本の開発者**：対象外。当面はOpus 4.8どまり

しかも、逃げ道もほぼ塞がれている。

- 英国向けの適用除外案は6月17日に頓挫
- EU・カナダ・豪州・インド向けの除外も存在しない

**非米国ユーザーは、ディレクティブが完全撤回されない限り使えない**と考えておくのが現実的だ。

## 日本の開発者が今すぐやるべき5つのこと

### 1. Opus 4.8に切り替える

`model` 指定がFable 5になっているコードは、もう通らない。フォールバック先を明示しておく。

```diff
# Fable 5指定はエラーになる。Opus 4.8へ
- model: claude-fable-5
+ model: claude-opus-4-8
```

### 2. Fable 5前提の検証を中断する

6月22日までの無料ウィンドウで試した結果は、「本番では使えない前提」で評価し直す。ベンチマークが良かったとしても、今は動かせない。

### 3. ベンダー・モデルロックインを見直す

単一モデル前提のパイプラインは、**地政学リスク**に直撃される。今回はそれが現実になった。複数モデルを切り替えられる抽象レイヤーを挟んでおく。

### 4. 7月8日のポリシー変更を確認する

ID＋生体認証の提出を受け入れるかどうかは、各自の判断だ。発効前に内容を読んでおく。

### 5. 代替フロンティアモデルも評価する

GPT-5.5系やGemini系、さらに中国勢（ZhipuがMythos級に追随との報道もある）まで、選択肢を一つに絞らない。

## まとめ：AIに国境が引かれた日

| 項目 | 状況 |
|------|------|
| 命令日 | 2026年6月12日 17:21 ET |
| 対象 | Fable 5・Mythos 5、全外国籍ユーザー |
| 理由 | サイバー能力の悪用懸念（詳細非公開） |
| 現在のFable 5 | 一般ユーザーは停止中 |
| 日本人の選択肢 | Opus 4.8 |
| 復活の鍵 | 7月8日 ID＋生体認証（米国民向け） |

最強モデルは、もう「誰でも使える」ものではなくなった。AIに国境が引かれた瞬間だ。

日本の開発者にとっての教訓はシンプルだ。**単一モデルに依存するな。** 地政学は、あなたのCI/CDを平気で止めてくる。


この記事が役に立ったら、いいねと保存をお願いします！

あなたはFable 5に依存していましたか？コメントで教えてください。

次回は「Opus 4.8でFable 5の性能差をどこまで埋められるか」を検証予定です。

## 参考リンク

Statement on the US government directive to suspend access to Fable 5 and Mythos 5 - Anthropic

https://www.anthropic.com/news/fable-mythos-access

US orders Anthropic to disable AI models for all foreign nationals - Al Jazeera

https://www.aljazeera.com/news/2026/6/13/us-orders-anthropic-to-disable-ai-models-for-all-foreign-nationals

Anthropic disables Fable and Mythos AI models after U.S. government bars it from giving foreigners access - Fortune

https://fortune.com/2026/06/13/anthropic-disables-fable-mythos-export-controls-national-security-threat/

U.S. government gives Anthropic green light for limited re-release of Mythos 5 - NBC News

https://www.nbcnews.com/tech/tech-news/us-government-gives-anthropic-green-light-limited-re-release-mythos-5-rcna352018

Anthropic works to restore access to Claude Fable 5, Mythos 5 after US directive

https://cryptobriefing.com/anthropic-works-to-restore-access-to-claude-fable-5-mythos-5-after-us-directive/
