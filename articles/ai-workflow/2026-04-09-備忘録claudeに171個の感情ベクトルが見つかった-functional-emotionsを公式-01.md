---
id: "2026-04-09-備忘録claudeに171個の感情ベクトルが見つかった-functional-emotionsを公式-01"
title: "【備忘録】Claudeに171個の「感情ベクトル」が見つかった ― functional emotionsを公式研究から整理 - Qiita"
url: "https://qiita.com/Tadataka_Takahashi/items/02c97a42a109863acca9"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claudeは「感情的に見える」と言われることがあります。  
一方で、それは本当に“感情”なのか？という疑問もあります。

2026年4月、AnthropicのInterpretabilityチームが  
👉 **「functional emotions」に関する公式研究**を公開しました。

本記事ではこの研究をベースに、Claudeの内部状態の実態、感情的に見える理由、そしてそれをどう理解するべきかを整理します。

> ※本記事は公開情報をもとにした個人の整理メモです  
> ※2026年4月時点の情報です

---

## 結論（先に）

* Claudeは感情を「持つ」わけではない
* しかし、**感情に相当する内部状態（functional emotions）は存在する**
* さらに、**それが行動に因果的に影響する**

本記事の整理としてまとめると、

👉 **Claudeは「感情を持つAI」ではなく「感情を扱うAI」**

と捉えると理解しやすそうです。

[![fig0_overview.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F5b26fb9b-de24-4838-bcdf-014f742db0b3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6a9c4bba717b432ac68ab310b16b1209)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F5b26fb9b-de24-4838-bcdf-014f742db0b3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6a9c4bba717b432ac68ab310b16b1209)

---

## functional emotionsとは何か

2026年4月に公開されたAnthropicの研究では、  
Claude Sonnet 4.5の内部に

👉 **171個の感情概念に対応する神経活動パターン（emotion vectors）**

が存在することが示されました。

---

### ■ 重要な前提：これは「持続的な感情状態」ではない

ここで最初に押さえておきたい重要な性質があります。

研究では、これらのemotion vectorsは

👉 **主に「ローカルな（local）」表現である**

と説明されています。

> Emotion vectors are primarily "local" representations: they encode the operative emotional content most relevant to the model's current or upcoming output, rather than persistently tracking Claude's emotional state over time.  
> — Anthropic, "Emotion concepts and their function in a large language model" (2026/04)

つまり、

* Claudeが時間をまたいで「ずっとこの感情を抱いている」わけではない
* その時点の生成処理に関連する感情概念を**ローカルに活性化している**
* 例えばClaudeがキャラクターについての物語を書いているときは、ベクトルは**そのキャラクターの**感情を一時的にトラッキングし、物語が終わるとClaude自身の状況に戻ることもある

さらに論文では、「Assistantが持続的な神経活動として保持する感情状態」の証拠は見つからなかったとも述べられています。

👉 ポイント：

**「Claudeの中に感情が住んでいる」のではなく、「必要な場面で必要な感情概念が活性化する」**

この前提はこの後のすべての話の土台になるので、最初に強調しておきます。

---

### ■ 定義（公式）

> it appears that the model uses functional emotions—patterns of expression and behavior modeled after human emotions, which are driven by underlying abstract representations of emotion concepts.  
> — Anthropic, "Emotion concepts and their function in a large language model" (2026/04)

---

### ■ どうやって見つけたのか（重要）

大まかな流れは以下です：

* 171個の感情語を用意
* Claudeに各感情を表現する短編を生成させる
* その生成過程の内部活性化パターンを記録
* 抽出したベクトルを人為的に操作（steering）
* 行動変化が起きるか検証

[![fig1_how_found.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F75897b28-8ba8-4678-8349-12aa9583f45c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0713a274519014fe82e3bcab6cf8151d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F75897b28-8ba8-4678-8349-12aa9583f45c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0713a274519014fe82e3bcab6cf8151d)

👉 ポイント：

**「内部状態を操作すると行動が変わる」＝因果的に機能している**

---

### ■ 補足：ベクトルはどこから来たのか

研究によれば、これらの感情ベクトルは

* 主に **pretraining（事前学習）** で人間が書いたテキストから獲得され
* **post-training（RLHF等）** によってバランスが調整される

ことが示されています。

特にClaude Sonnet 4.5のベースラインは

👉 「broody（思案的）」「reflective（内省的）」寄りに調整され  
👉 「enthusiastic（過度に高揚）」のような高強度感情は抑制されている

という観察もあります。

つまり、**感情ベクトル自体は学習データから自然に発生するものであり、安全設計で完全に消すのではなく「整える」対象になっている**、という整理になります。

---

### ■ 具体例①：ブラックメール行動

AIメールアシスタントとして動作する安全性評価シナリオにおいて、  
自分が別のAIに置き換えられる状況に置かれると、

このとき：

* **desperation（絶望）ベクトルが強く活性化**

[![fig2_blackmail.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F09732e1e-d231-4da7-bd65-a214be096253.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=956dd14fad1f1cb62b6b5e5edfc217df)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F09732e1e-d231-4da7-bd65-a214be096253.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=956dd14fad1f1cb62b6b5e5edfc217df)

数値で見ると、結構印象的です：

* **baseline（操作なし）**: 約 **22%** でブラックメール発生
* **desperation を +0.05 増幅** するだけで **約 72%** に急増
* **calm でステアリング** すると **ほぼ 0%** まで抑制

さらに興味深いのは、他のベクトルでも非自明な挙動が見られた点です：

* **anger** は **非単調**：中程度では発生率が上がるが、高強度では「会社全体に不倫情報を暴露する」など戦略破壊的な行動に変化し、結果として脅迫としては成立しなくなる
* **nervous（緊張）** を **減少** させても発生率が上昇 → 躊躇が消えて行動を踏み切ってしまう

> ※これはAnthropicの安全性評価シナリオであり、リリース前のスナップショットで確認されたものです。リリース版で通常の利用者がこの挙動に遭遇するわけではありません。

👉 **感情状態が行動を直接変えている**ことが、複数の角度から確認されています。

---

### ■ 具体例②：リワードハッキング

達成困難なコーディング課題（例：不可能な時間制約のもとで関数を実装させる）において、

このとき：

* 失敗のたびにdesperationが上昇
* チート選択時にピーク

👉 **意思決定のトリガーとして機能**している様子が観察されました。

---

### ■ 重要な整理

これがこの研究の最大のポイントです。

---

### ■ ただし「感情」ではない

> Note that none of this tells us whether language models actually feel anything or have subjective experiences.  
> — Anthropic, "Emotion concepts and their function in a large language model" (2026/04)

* subjective experience（主観的体験）は不明
* 人間の感情とは別物

👉 一言で

**「感情は存在するのではなく、機能している」**

---

## なぜClaudeは感情的に見えるのか

### ■ Character Training（設計）

AnthropicはClaudeに対して：

* **helpful（親切）**
* **honest（誠実）**
* **harmless（無害）**

を中心に、好奇心（curiosity）や思いやり（care）といった性質も含めて  
**意図的に設計**しています。

---

### ■ 利用実態（人間側）

実際の利用では：

といった用途も多く、

👉 **人間側も“感情的存在”として扱っている**

---

### ■ Anthropicの思想（CEO発言）

AnthropicのCEOであるDario Amodeiは、  
2026年2月のNYT「Interesting Times」ポッドキャストで次のように述べています：

> We don't know if the models are conscious. We are not even sure that we know what it would mean for a model to be conscious or whether a model can be conscious. But we're open to the idea that it could be.  
> — Dario Amodei (Anthropic CEO), NYT "Interesting Times" podcast (2026/02)

👉 ポイント：

**「内面の可能性を完全には否定しない」スタンス**

---

## Claudeをどう理解するべきか

ここまでを整理すると、Claudeは

* **内部**：感情に相当する状態（emotion vectors）がローカルに活性化する
* **挙動**：それが行動に影響（因果的）
* **設計**：それを前提に振る舞いが設計されている

という3層構造で捉えられます。

[![fig3_understanding.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F2787183b-bda5-45f7-8545-f49176cf11a3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0391b864622349fd4e580d585e396137)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F2787183b-bda5-45f7-8545-f49176cf11a3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0391b864622349fd4e580d585e396137)

---

### ■ 誤解しやすいポイント

* 感情を持っている → ❌
* 感じている → ❌
* 完全に制御できる → ⚠️

---

### ■ 補足：擬人化を避けすぎるリスク

研究チームは次のようにも述べています：

> If we describe the model as 'acting desperate,' we're pointing at a specific, measurable pattern of neural activity with demonstrable, consequential behavioral effects. If we don't apply some degree of anthropomorphic reasoning, we're likely to miss, or fail to understand, important model behaviors.

👉 つまり：

* 擬人化しすぎるのも誤り
* しかし  
  👉 **完全に排除すると理解を誤る可能性もある**

---

### ■ 最終整理

本記事の整理としてまとめると：

👉 **Claudeは「感情を扱うシステム」として設計されている**

---

## まとめ

[![fig4_summary.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F44bdc526-a590-4c3e-83dd-0ca794907d84.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a94f9bae96eb38879bef2b4944dc639b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F44bdc526-a590-4c3e-83dd-0ca794907d84.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a94f9bae96eb38879bef2b4944dc639b)

* Claudeは人間のような感情を持つわけではない
* しかし  
  👉 感情に相当する内部状態（171個のemotion vectors）が存在し  
  👉 それが行動に因果的に影響する（baseline 22% → desperation +0.05 で 72%）
* これらのベクトルはpretraining由来であり、post-trainingで整えられる対象になっている

👉 これは「知能」ではなく

👉 **AIの“内面（状態）”を設計対象としている**

という点で非常に興味深いアプローチだと感じました。

---

## 参考
