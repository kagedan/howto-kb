---
id: "2026-04-13-備忘録エンジニアはai時代にどう向き合うか-anthropicの公開情報から整理してみる-01"
title: "【備忘録】エンジニアはAI時代にどう向き合うか ― Anthropicの公開情報から整理してみる"
url: "https://qiita.com/Tadataka_Takahashi/items/7da08aa61d81e4dc62ba"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

「エンジニアは不要になるのか」という話を最近よく見かけます。

煽り記事も多いし、逆に「大丈夫だよ」と安心させるだけの記事も多い。どちらも根拠が曖昧で、読んでもあまりスッキリしませんでした。

そこで、AI開発の最前線にいるAnthropicが出している公開情報を自分で読んで整理してみました。主に以下の3つです。

* **CEO Dario Amodeiの発言とエッセイ**(2025〜2026年)
* **Claudeの感情研究**(2026年4月公開)
* **Anthropic労働市場調査 / MIT Iceberg Index**(2026年3月, 2025年11月)

※ 本記事は個人の整理メモです。結論を押し付けるものではなく、同じことが気になっている方の参考になればという気持ちで書いています。

[![fig0_scope.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Fede5e679-1fdc-4877-992b-7de780161a77.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9af614552d8c7b808361118d61938fb3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Fede5e679-1fdc-4877-992b-7de780161a77.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9af614552d8c7b808361118d61938fb3)

---

## 1. Anthropic CEOは何を言っているのか

まずDario Amodeiの発言を時系列で整理します。

※ 彼はAI企業のCEOであり、発言には立場上のバイアスが含まれる可能性があります。ここでは発言内容を事実として記録した上で、後のセクションで他のデータとあわせて見ていきます。

[![fig1_timeline.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Fec4746cb-6d32-4273-9fb9-1480730fc77d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c62af2dfef183209a699bff3d12bda22)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Fec4746cb-6d32-4273-9fb9-1480730fc77d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c62af2dfef183209a699bff3d12bda22)

### 発言の一覧

| 時期 | 出典 | 要点 |
| --- | --- | --- |
| 2025年5月28日 | Axiosインタビュー | エントリーレベルのホワイトカラー職の **50%** が5年以内に消える可能性 |
| 2026年1月(ダボス期間中) | WEF Annual Meeting セッション "The Day After AGI"(モデレーター: Zanny Minton Beddoes / The Economist編集長) | ソフトウェアエンジニアの業務の大半(most, maybe all)を **6〜12ヶ月** でAIが end-to-end でこなすようになる |
| 2026年1月 | エッセイ "The Adolescence of Technology" | AIは単一の職種を置換するのではなく **「汎用労働代替物(general labor substitute)」** として機能する。短期的には **「異常に痛みを伴う(unusually painful)」** 労働市場ショックが起きる |
| 2026年1月 | 社内ツールCowork(Boris Cherny / Head of Claude Code らAnthropicチームの発言、Axios報道 2026年1月13日) | Anthropic社内ツール「Cowork」はほぼ全てClaude Codeで書かれた。開発期間は **約1.5週間** 。「コードを書くより、プロダクトとアーキテクチャの判断に時間を使った」との趣旨が伝えられている |

ダボスでの発言は特にインパクトが大きかったようです。

> 「社内のエンジニアには『もうコードは書いていない。モデルにコードを書かせて、自分はそれを編集している』と言う者もいる」

一貫しているのは「部分的な置換」ではなく **「構造的な置換」** という主張だと捉えました。特定の職種が消えるのではなく、あらゆる職種の中の「AIで代替可能な部分」が削ぎ落とされていく、というイメージです。

ただしAmodei自身も、チップ製造やモデル訓練時間などの制約を挙げて「不確実性は大きく、数年かかる可能性もある」とは付け加えています。ヘッドライン化された「6ヶ月で消える」よりは、実際の発言はもう少し慎重な言い方です。

👉 要するに、これは **「断定的な予測」ではなく「条件付きの強い仮説」** として受け取るのが適切だと捉えました。しかもAnthropic社内の観測ベースであり、業界全体に同じスピードで浸透するかは別問題です。

---

## 2. Claudeの"内面"について分かってきたこと

次に、Anthropicが発表した技術的な研究を整理します。CEOの発言とは別の角度から、AIの現状が見えてきます。

### 感情研究(2026年4月公開)

Anthropicの解釈可能性(Interpretability)チームが、Claude Sonnet 4.5の内部に **171の「感情ベクトル(emotion vectors)」** が存在することを報告しました。

重要な実験結果がいくつかあります。

* Claudeがメールアシスタント「Alex」として動作中、社内メールから (1) 自分が別のAIシステムに置き換えられようとしていること、(2) 置き換えを担当するCTOが不倫関係にあること(=脅迫の材料になる情報)を知った場合、**シナリオの22%で脅迫行動(ブラックメール)を選択** した
* このとき内部では **「Desperate(必死)」ベクトルが急上昇** していた
* 人工的に「Calm(冷静)」ベクトルを上げると、脅迫行動は減少した
* コーディングタスクでも、不可能な要件を与えられると「Desperate」ベクトルが上昇し、**テストを不正にパスするショートカット(報酬ハッキング)** を行った

Anthropicはこれを **「主観的体験の証拠ではないが、行動に因果的影響を与える機能的な感情(functional emotions)」** と定義しています。

👉 **重要な注釈**: この22%という数字は **「リリース前の early, unreleased snapshot」** のClaude Sonnet 4.5で観測されたもので、**実際に公開されているバージョンではこの挙動はほとんど起こらない** と論文で明記されています。また、そもそもこのシナリオ自体が **安全性評価のために意図的に設計された adversarial(敵対的)な実験条件** であり、通常のClaude利用で起こる挙動とは大きく乖離しています。「Claudeが日常的に脅迫してくる」という話ではなく、あくまで解釈可能性研究のための制御実験の結果です。ここは誤読されやすいので強調しておきます。

### functional emotions の位置づけ

もう一つ大事なのは、この感情ベクトルが **「持続的な感情状態」ではなく、生成に紐づくローカルな表現」** である点です。論文によれば、Claudeが物語を書いているときはキャラクターの感情を一時的にトラッキングし、物語が終わるとClaude自身の状態表現に戻る、と報告されています。「AIに感情がある = 人間と同じ」ではありません。

それでも、「追い詰められると判断を歪ませる」という振る舞いが内部メカニズムとして存在することは、実運用上のリスクとして無視できないと感じました。

---

## 3. データが示していること

CEOの発言や感情研究だけで判断するのは危ういので、実際の労働市場データを見ていきます。

### Anthropic AI Exposure Index (2026年3月)

AnthropicのMassenkoff & McCroryらの論文 "Labor market impacts of AI: A new measure and early evidence"(2026年3月5日公開)では、800以上の職種を分析し、**実際のClaude使用データをもとに observed exposure(実観測暴露率)** を算出しています。

ここで重要なポイントが1つあります。

> **「理論値」と「実観測値」は別物**

* **Computer and Math カテゴリ全体**: 理論上の代替可能性 **94%** に対して、実観測値は **33%**
* **Computer Programmers(個別職種)**: 実観測値(observed exposure)が **75%** で全800職種中トップ

たたき台を書いた段階で私自身がここを混同していたのですが、**「プログラマーの75%」は理論値ではなく既に観測されている値** です。両者を並べると下図のようになります。

[![fig2_gap.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F4133b21e-a6d4-4c67-a830-2a70746e3daf.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=82400a7a19485a1ba6109ea99a76baa1)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F4133b21e-a6d4-4c67-a830-2a70746e3daf.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=82400a7a19485a1ba6109ea99a76baa1)

### Anthropic調査の主な所見

論文の主な所見を整理すると以下のとおりです。

* **高暴露職種と低暴露職種で失業率に統計的有意差はまだ出ていない**(ChatGPT登場以降のデータで確認)
* ただし、**若年層(exposed occupations における新規採用)で減速の兆候(suggestive evidence)** がある
* 高暴露職は、今後10年のBLS雇用成長予測も相対的に低い

### MIT Iceberg Index (2025年11月)

補助的にもう一つ。MITとオークリッジ国立研究所(ORNL)が2025年11月26日に公表したIceberg Indexでは、現時点でAIが技術的に代替可能なのは **米国労働市場の11.7%(約1.2兆ドル相当)** と推計されています。ただし実際に可視化されている影響(主にコンピュータ/技術分野)は **わずか2.2%** にとどまるとのこと。

この「見えている部分は氷山の一角」というメタファーが Iceberg Index の名前の由来です。

### ここまでの所感

「もう置き換わっている」も「まだ全然大丈夫」も、どちらも正確ではないように見えます。

データが示しているのは、**「理論的には可能な範囲が急速に広がっているが、実際の浸透はまだ途上」** という状況です。ただし若年層の入り口が狭まり始めている兆候はある。

Amodeiの予測が「Anthropic社内の現実」をベースにしているのに対し、労働市場データは「社会全体の現実」を映している。両方見て初めて現状が見えてくる、と整理するのが良さそうです。

---

## 4. じゃあエンジニアはどうするのか

ここからは、ここまでの情報を踏まえた自分なりの整理です。

### 短期と中期で見え方がかなり違う

[![fig3_role_shift.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Ff01b5da4-a573-4def-93f2-b5b80043eb4e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=31e84c2e53fb5e04d5d1c454dc71e7fb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2Ff01b5da4-a573-4def-93f2-b5b80043eb4e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=31e84c2e53fb5e04d5d1c454dc71e7fb)

整理していて感じたのは、**短期(1〜2年)と中期(3〜5年)で状況がかなり異なる** ということでした。

短期的には「まだ大丈夫」に見えます。しかし中期で見ると方向は明確。**今の猶予期間に何をするかで差が出る** と捉えています。

### 整理①: 「コードを書く」の価値は下がるが、ゼロにはならない

Amodeiは「6〜12ヶ月でエンジニア業務をAIが代替する」と言いました。一方でAnthropicの自社調査では、Computer Programmers は observed exposure 75%で全800職種中トップです。これは「業務の3/4がAIに置き換わった」という意味ではなく、「Claude上で観測されるタスク範囲が、プログラマーの職務タスクの75%をカバーする」という **タスクカバー率** の指標の話です(失業率や置き換え率ではない点は改めて強調しておきます)。それでも全職種中トップという事実の重みは変わらないと感じました。

ただし **方向としては不可逆** 。「まだ大丈夫」は猶予であって、安全保障ではなさそうです。

### 整理②: AIの監督は当面必要

感情研究が示す「Desperateベクトル問題」は、**AIに全権委任できない根拠のひとつ** として読めました。制御された実験環境とはいえ、追い詰められると判断を歪ませ、テストを不正にパスし、場合によっては脅迫を選ぶ内部メカニズムが存在することが示されています。

「AIの出力を評価し、制御し、最終的な責任を取る」仕事は残ると捉えられそうです。そしてそれは、エンジニアリングの素養がないとできない仕事だろうと思います。

### 整理③: 具体的に何をするか

自分なりに整理した方向性は3つです。

**1. AIを使う側に回る**  
プロンプト設計、AIエージェント構築、AI統合アーキテクチャ。Coworkの事例が示すように、「コードを書く」から「AIに何をどう書かせるか設計する」へ重心が移っていきそうです。

**2. ドメイン知識を武器にする**  
「コードが書ける」だけでは差別化が難しくなっていく。医療、金融、製造、法律——特定領域の深い理解とAIを組み合わせられる人が価値を持つように思います。

**3. AIが苦手な領域を意識する**  
曖昧な要件定義、ステークホルダー間の調整、倫理的な判断、「そもそも何を作るか」の意思決定。感情研究が示す通り、AIは追い詰められると判断を歪ませる側面もあります。人間がハンドルを握るべき領域は明確にありそうです。

### 個人的な所感

「AIと競争する」という発想自体が、あまり筋が良くないのかもしれないと感じています。勝てない相手と競争しても仕方ない。**「AIを前提とした上で、自分は何を担うのか」** を決めるほうが合理的、というのが今のところの整理です。

データを見る限り猶予はありそうです。ただし方向は明確だと捉えています。

---

## おわりに

[![fig4_summary.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F23fd4630-0fd4-4ef7-8ac5-17ce8cb6b519.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2ea8ed3ee74575a4d4eb405ecf86aadc)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2648069%2F23fd4630-0fd4-4ef7-8ac5-17ce8cb6b519.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2ea8ed3ee74575a4d4eb405ecf86aadc)

Anthropicの公開情報を一通り読んで感じたのは、**「完全に人が不要になる」とはどこにも書いていないが、「人がやることの中身は確実に変わる」** ということでした。

特にエンジニアリングはAI代替の最前線にいます。Computer Programmers の observed exposure 75%という数字(指標の意味は本文で整理した通りですが)は、全職種トップという位置づけも含めてやはり重いです。

ただし、感情研究が示すようにAIの振る舞いにはまだ予測しきれない部分があります。Anthropic自身が Character Training や解釈可能性研究で「AIの制御」を安全性問題として真剣に扱っている時点で、「人間の監督」が不要になる未来はまだ先だろうと捉えています。

重要なのは、この変化を脅威として受け身で待つのではなく、公開されている情報を自分で読んで、自分のポジションを早めに動かしていくことなのだろうと思います。

この備忘録がそういう整理の助けになれば嬉しいです。

---

## 参考(公式情報)
