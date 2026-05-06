---
id: "2026-05-05-google-cloud-next-26-体験記-4-2-つの-keynote-現地レポート-01"
title: "[Google Cloud Next '26 体験記 #4] 2 つの Keynote 現地レポート"
url: "https://qiita.com/koichim33/items/42bb1dff1628c0ffd3e4"
source: "qiita"
category: "construction"
tags: ["AI-agent", "qiita"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

ラスベガスで開催された Google Cloud Next '26 の体験ブログ、第 4 弾です。

これまでの記事はこちら 👇
- 第 1 弾：[[Google Cloud Next '26 体験記 #1] Agentic Hack Zone でエージェント開発を体験してきた](https://qiita.com/koichim33/items/0e2883d847fd3abd3f11)
- 第 2 弾：[[Google Cloud Next '26 体験記 #2] EXPO で体験した 3 つのユニークなブース](https://qiita.com/koichim33/items/e1d1cd8eabcb3a84c381)
- 第 3 弾：[[Google Cloud Next '26 体験記 #3] Anthropic のセッションで聞いた「ソフトウェアの先」のビジョン](https://qiita.com/koichim33/items/03748c6017fa578cec0f)

![IMG_1627のコピー.jpeg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1602803/e739e827-fa9a-4d72-b0d5-fa5b414167f3.jpeg)

今回は、Next '26 で実施された **2 つの Keynote**、

- **Opening Keynote**
- **Developer Keynote**

について、現地の会場の雰囲気を交えつつレポートしたいと思います。テックカンファレンスに参加したらやっぱり Keynote は外せませんよね。

すでにご覧になられた方も多いかもしれませんが、Keynote は YouTube でも視聴可能です。

- 🎥 **Opening Keynote**：https://www.youtube.com/watch?v=11PBno-cJ1g
- 🎥 **Developer Keynote**：https://www.youtube.com/watch?v=A01DQ8_xy7Q

---

## Keynote のポジショニング

Next の Session Types によると、Keynotes の定義は以下の通りです。

> Join Google Cloud and industry leaders as they make big announcements, showcase the latest products and customer successes, and set the stage for everything else at the event.

つまり、**大型発表・最新プロダクト・顧客事例** が一気に披露される、イベント全体の方向性を定める「土台となるセッション」という位置付けです。

## 会場：Michelob ULTRA Arena

Keynote の会場は、過去開催と同様 **マンダレイベイ内の Michelob ULTRA Arena** でした。私は今回が初めての現地参加だったのですが、**12,000 人を収容できるアリーナ** ということで、入った瞬間からそのスケール感に圧倒されました。

開演前から会場がじわじわと埋まっていき、ライティングと音響で空気が作られていく感じは、現地でしか味わえない独特の高揚感がありました。

---

## Opening Keynote

### 開演前のオープニングパフォーマンス

Opening Keynote 開始前には、**音楽と映像のパフォーマンスタイム** がありました。どうやら **生成 AI を使って作られた映像** のようで、操作者が音楽に合わせて **ハンドジェスチャーで指示を出して映像パターンを切り替えていく** という、ユニークな演出でした。

開演前のウォーミングアップから「これからエージェントの時代の話が始まるぞ」という空気が作られていました。

Opening Keynote の内容については各方面ですでに発表がされているので、ここでは簡単に概要に触れておきます。

### 全体メッセージ

業界は **ジェネレーティブ AI から「エージェント時代（Agentic Era）」へと大きくシフト** しており、自律的に推論・行動・スケールできる AI エージェントが企業全体で動き出している、という主張でした。

### 戦略的なメッセージ

Google の強みとして、

> **カスタムシリコン（Ironwood / 第 8 世代 TPU）→ フロンティアモデル（Gemini）→ クラウドプラットフォーム → エンタープライズ配信チャネル（30 億ユーザーの Workspace）**

という、**チップからアプリまでフルスタックを自社所有している** 点が強調されていました。

### 主な発表

#### 1. Gemini Enterprise Agent Platform（旧 Vertex AI）

Vertex AI を **Gemini Enterprise Agent Platform** へとリブランディング。従業員向け AI アシスタント **Agentspace** も統合し、**Gemini Enterprise** という単一プロダクトに集約。**エージェントの構築・スケール・ガバナンス・最適化を一気通貫で行えるプラットフォーム** という位置付けです。

#### 2. Gemini Enterprise アプリ

**非技術者でも自然言語でエージェントを構築・利用できる**、業務の中核となるインターフェース。

#### 3. 第 8 世代 TPU（2 チップ構成）

- **TPU 8t**（学習向け）：単一スーパーポッドで **最大 9,600 TPU までスケール**
- **TPU 8i**（推論向け）：前世代比で **費用対効果 80% 向上**、**ニアゼロのレイテンシ**

#### 4. Agentic Data Cloud

データ基盤を **全面的に再設計**。

#### 5. Agentic Defense

買収した **Wiz** の技術を統合し、**自律的な Red / Blue / Green エージェント** が機械の速度で脆弱性を検出・修正。

#### 6. Workspace Intelligence

**Gmail / Docs / Sheets / Drive / Meet / Chat** 全体にエージェントが組み込まれる。

### 個人的に印象的だった点

個人的に最も印象的だったのは、**"State-of-the-art models in Gemini Enterprise Agent Platform"** というタイトルで各種モデルが紹介されたシーンです。

ここで **Gemini 3.1 Pro / Gemini 3.1 Flash image / Lyria 3 Pro / Veo 3.1 Lite** という Google の 4 つのモデルが紹介されていたのですが、それと並んで **Anthropic Models として Claude Opus 4.7** が登場していました。
クローズドな印象を避ける配慮の意味合いもあったかもしれませんが、個人的には Opus 4.7 のモデル性能の高さを Google 側も認めていることの表れではないか、とも考えてしまう場面でした。

---

## Developer Keynote

### 開演前のパフォーマンス（再び）

Developer Keynote 開演前にも、**Opening Keynote と同様の音楽と映像のパフォーマンスタイム** がありました。同じ演出でしたが、「お、また始まるぞ」という感じでもありました。

Developer Keynote についても Google Cloud 公式ブログ等ですでに報告されていますので、ここでは簡単に概要を整理しておきます。

### Keynote 全体の構成

Developer Keynote は、**実機デモとライブコーディング中心** の開発者向けセッションでした。

全体のテーマは **「架空のラスベガスマラソンを企画・シミュレートするマルチエージェントシステム」** で、**最初のプロトタイプから本番運用までの工程を順に構築していく** という、ストーリー仕立ての非常に分かりやすい構成になっていました。

ちなみに、ラスベガスマラソン・シミュレーターは

- **Planner**
- **Evaluator**
- **Simulator**

という **3 エージェント構成** とのことでした。

### 7 つのデモ

Developer Keynote では、以下の 7 つのデモが紹介されました。

1. **Build agents with Agent Platform**
2. **Creating multi-agent systems**
3. **Enhancing agents with memory**
4. **Debugging agents at scale**
5. **Intent to infrastructure with Gemini Cloud Assist**
6. **Build and share no-code agents**
7. **Securing agents**

エージェントを「作る → 連携させる → 記憶を持たせる → デバッグする → インフラを宣言的に扱う → ノーコードで広める → セキュアに守る」という流れで一通り体験できる構成で、開発者目線でも非常に学びの多い内容でした。

### ソースコードと Codelab がフル公開

特にうれしかったのが、**全ソリューションが GitHub でソースコード公開済み**、かつ **デモは Codelab として提供** されていた点です。Keynote 中のスライドで提示された QR コードのリンク先は以下でした。

- https://developers.google.com/profile/badges/events/cloud/next/2026/codelab/build-agents-with-agent-platform/award
- https://developers.google.com/profile/badges/events/cloud/next/2026/codelab/creating-multi-agent-systems/award
- https://developers.google.com/profile/badges/events/cloud/next/2026/codelab/enhancing-agents-with-memory/award
- https://developers.google.com/profile/badges/events/cloud/next/2026/codelab/debugging-agents-at-scale/award
- https://developers.google.com/profile/badges/events/cloud/next/2026/codelab/intent-to-infrastructure-with-gemini-cloud-assist/award
- https://developers.google.com/profile/badges/events/cloud/next/2026/codelab/run-and-share-agents/award
- https://developers.google.com/profile/badges/events/cloud/next/2026/codelab/marathon-demo/award

Keynote を見て「気になったから自分でも触ってみよう」となれる動線がきちんと用意されているのは、開発者向けカンファレンスとして本当にありがたいところです。

---

## 余談：Keynote 会場での少し不思議な出来事

ところで Developer Keynote では、ちょっと不思議な出来事もありました。
私の斜め前の席には関係者らしき方が座っていたのですが、Keynote 開始前にスマホで自撮りを始めました。スマホにはとても明るいスマホ用ライトが付いていて眩しかったです。
さらに Keynote 終盤のデモ中には、今度は目の前に座っていた人が後ろを振り返って私の方をじっと見てきて、そのまま無言で去っていくということもありました。何か用でもあったのでしょうか…？
テックカンファレンスではこういうこともよくあるようですので、そっとしておこうと思います。

---

## まとめ

現地で 2 つの Keynote に参加してみて、改めて感じたのは以下のような点でした。

- **会場の規模感とライブの熱量** は、足を運んだからこそ体験できる
- Opening Keynote の **「Agentic Era」** というメッセージは、その後のセッションや EXPO 全体を貫く軸になっている
- Developer Keynote は **マラソンシミュレーターを題材にした 7 つのデモ** で、エージェント開発のフルスタックを 1 本のストーリーで体感できる構成

「Keynote は YouTube でも見られる」とはいえ、**現地ならではの体験** の価値はやっぱり大きいなと改めて実感したセッションでした。

#5 (ラスト) に続きます。
