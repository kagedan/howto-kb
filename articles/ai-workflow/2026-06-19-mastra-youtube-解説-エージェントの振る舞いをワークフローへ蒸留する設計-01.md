---
id: "2026-06-19-mastra-youtube-解説-エージェントの振る舞いをワークフローへ蒸留する設計-01"
title: "[Mastra YouTube 解説] エージェントの振る舞いをワークフローへ蒸留する設計"
url: "https://zenn.dev/shiromizuj/articles/2ff24d35c78cb7"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式YouTubeチャンネル](https://www.youtube.com/@mastra-ai)にアップされた動画を速報ベースでお伝えします。ただの文字起こしではなく、扱われているトピックの抽出と、トピックごとの要約をしています。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra YouTube動画 速報解説一覧](https://zenn.dev/shiromizuj/articles/8d6e4fd86631e9)

---

## 動画情報

<https://www.youtube.com/watch?v=Abw9gutRLOQ>

---

## 概要

この動画は、AI エージェントを「全部エージェントに任せる」か「全部ワークフローで固定する」かの二択で考えるのではなく、**予測可能性と agency の間にある設計領域をどう使うか**を短く整理した講演です。Mateo Torres はその中間領域を `semi-deterministic orchestration` と `constrained non-determinism` という 2 つの言葉で説明し、GUI と agentic layer を分けつつ、共有メモリで両者をつなぐ構成を紹介します。

主張の核はかなり実務的です。エージェントは探索に向いているが、そこで見つかった反復パターンは workflow に落とし込んだほうが速くて安全になる。逆に workflow だけでは、未知のデータや曖昧な判断を扱いにくい。そこで最初は agent 的に探索し、繰り返しが見えてきたら workflow として固定する。この「agent で探索し、workflow に蒸留する」という往復が、動画全体を貫くメッセージです。

短い動画ですが、Mastra Workflows と共有メモリをどう位置づけるか、そして Arcade のような action layer をどう噛ませるかがコンパクトに整理されていて、**長時間使う実務エージェントをどう安定化させるか**という観点で見るとかなり示唆があります。

---

## 要点

1. エージェント設計は「完全に決定論的な workflow」か「完全に自由な agent」かの二択ではありません
2. Mateo はその中間に、`semi-deterministic orchestration` と `constrained non-determinism` の領域があると整理します
3. `semi-deterministic orchestration` は、workflow を土台にしつつ、分岐や評価の一部だけを LLM に委ねる設計です
4. `constrained non-determinism` は、より agent 的に振る舞わせながらも、権限やデータ流出リスクを制約して危険性を抑える考え方です
5. デモ対象の YouTube admin agent では、GUI 層と agentic layer を分け、共有メモリで両者をつないでいます
6. 構造化データは workflow や cron job 側で扱い、自由テキストや探索は agent 側で扱う、という役割分担が示されます
7. いちばん重要なのは、agent を使って探索し、繰り返しが見えた作業を workflow に蒸留するという運用パターンです

---

## 詳細

### agency と predictability の間に、実務向けの設計空間がある

Mateo が最初に示した図は Agency と Predictability の2軸があります。上側の赤い点は `if-else` と制御フローで固めた完全決定論的な automation があり、反対側の赤い点は危険な権限まで含めて自由に動ける YOLO 的な agent があります。彼の主張は、そのどちらもそのままでは「役に立つが危なくない」実務エージェントに**なりにくい**、ということです。

![](https://static.zenn.studio/user-upload/49e83e9a0c8e-20260618.png)

Mateo は自身にとってのスイートスポットはその中間で、これを s`emi-deterministic orchestration` と呼んでいます。これは、workflow の骨格を残しつつ、評価や分岐のような局所的な判断だけを LLM に任せる考え方です。これなら全体の進み方は読みやすいまま、曖昧な判断だけをモデルに吸収させられます。もうひとつの緑の点 `constrained non-determinism` は、より自由度の高い agent を許しつつ、危険な権限行使や情報流出を抑える方向です。つまり、自由度をゼロにするのではなく、被害半径を制御する発想です。

この整理が useful なのは、エージェント設計を「どれだけ autonomous か」だけで評価しなくなるからです。大事なのは autonomy そのものではなく、**その仕事に必要な agency をどこまで与え、どこを固定するか**です。

---

### GUI と agentic layer を分け、共有メモリでつなぐ

ここで事例として、Mateo 自身の DevRel 業務を題材にした YouTube admin agent の紹介が入ります。YouTube チャンネル管理、スポンサー関連の確認、競合チャンネルの観察といった仕事を支えるエージェントです。もちろん本人も強調している通り、この発表での本題はアプリそのものではなく、その構成パターンです。

![](https://static.zenn.studio/user-upload/318a9842878f-20260618.png)

ここで彼は 2 つの projection layer を置きます。ひとつは GUI で、これは主にプレゼンテーション層です。もうひとつが agentic layer で、Arcade 側の action layer や MCP サーバー群を介して、実際のアクション空間へ接続します。そのうえで、Mastra Workflows を使った semi-deterministic orchestration 層が両者を束ねます。

![](https://static.zenn.studio/user-upload/e2540caa0299-20260618.png)

面白いのは、GUI と agentic layer が別物でありながら、**memory は両者に共通**だと説明している点です。画面上の見せ方と、裏側の agent 的な探索・実行は別の責務を持つ。しかし、どちらも同じ状態と文脈を共有していないと、継続性が壊れてしまう。このあたりは、Mastra が thread や memory を中心に長時間エージェントを組み立てている最近の流れともきれいにつながります。

---

### workflow は domain knowledge を閉じ込める器として強い

Mateo の説明で重要なのは、workflow を単なる古い自動化方式として扱っていないところです。彼はむしろ、workflow の強みを **domain knowledge を閉じ込められること** だと捉えています。ユーザーがやり方をすでに知っていて、その仕事が何度も繰り返されるなら、それは workflow に落とし込む価値が高い、というわけです。

![](https://static.zenn.studio/user-upload/b00bc8623e9c-20260618.png)

この視点に立つと、agent の役割も変わります。agent は常に本番実行の主役である必要はありません。最初は agent を使って探索し、どの入力を見て、どの判断をして、どういう順序で進むのが妥当かを見つける。そして「毎回同じことをしている」と気づいたら、その反復を workflow に凍結する。動画の終盤で Mateo が言う「freeze that repetition into a workflow」は、まさにこの話です。

これはかなり重要な実務原則です。最初から全部を workflow で設計しようとすると、未知の例外や暗黙知に対応できません。逆に、全部を agent の自由判断に任せると、速度・コスト・安全性・再現性のどれかで苦しくなります。**探索は agent、定着は workflow** という役割分担が、両者の強みを素直に使う方法だと分かります。

![](https://static.zenn.studio/user-upload/f3d75561b83d-20260618.png)

---

### context は agent の自律性を支えるが、その一部は workflow 側から供給できる

動画の後半で Mateo は、結局のところ鍵は context だと述べます。ここでいう context は、単に会話履歴ではありません。タスク理解、判断、継続性を支える環境知識全体です。agent が適切なタイミングで適切な行動を選べるのは、十分な context があるからです。

![](https://static.zenn.studio/user-upload/d10f914ff62a-20260618.png)

そのうえで彼は、context は必ずしも agent がその場で全部集める必要はなく、workflow 側から供給されてもよいし、多くの場合そうあるべきだと言います。構造化データは database に載せて workflow や cron job から扱うほうが効率的です。毎回 agent に構造を解釈させるのは無駄が多いからです。一方で、自由テキストや曖昧な観察は agent 側に向いています。

この整理は、最近の「コンテキストエンジニアリング」とも相性が良いです。何を memory に入れるか、何を workflow で前処理するか、何をその場で model に判断させるか。Mateo の話は短いですが、その三層をどう切り分けるかのヒントになっています。

---

### この講演が示す本質は「agent を workflow に勝たせる」のではなく「agent から workflow を育てる」こと

最後に残るメッセージはとてもシンプルです。agent と workflow を競合関係で見るのではなく、**agent を探索装置として使い、そこから workflow を育てる** という見方です。未知の仕事、新しいタスク、例外処理、データ探索は agent に寄せる。その過程で反復パターンが見えたら、workflow に落として高速化・安定化する。そしてまた新しい探索領域だけを agent に任せる。

このループが回ると、システムは少しずつ「危なくないのに役立つ」側へ寄っていきます。Mateo が言う semi-deterministic orchestration の価値は、単に LLM を workflow に混ぜることではなく、**曖昧さを吸収する場所と、固定化してよい場所を分けられること**にあります。

6 分ほどの短い講演ですが、Mastra Workflows、共有メモリ、Arcade の action layer、MCP 連携をどう一段上の設計原理でまとめるかがよく出ています。実装 API の解説よりも、何を agent の自由に任せ、何を workflow として固定するかを考えるための動画として見ると、かなり密度の高い内容です。

---

## 関連リンク
