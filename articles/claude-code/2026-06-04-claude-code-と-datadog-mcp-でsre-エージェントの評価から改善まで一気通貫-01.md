---
id: "2026-06-04-claude-code-と-datadog-mcp-でsre-エージェントの評価から改善まで一気通貫-01"
title: "Claude Code と Datadog MCP で、SRE エージェントの評価から改善まで一気通貫でやってみた"
url: "https://zenn.dev/layerx/articles/3febbbc24e55a3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

## はじめに

LayerX で AI Workforce の SRE をしている石田（[@ishiishi-kenken](https://x.com/ishiishi_kenken)）です。

いきなり宣伝で恐縮ですが、本記事と重なるテーマで、2026 年 6 月 10 日開催の **Datadog DASH 2026** のセッション「The AI Engineering Playbook: How to Evaluate & Iterate at Every Phase of Development」に登壇します。DASH は Datadog が年に一度開催するユーザーカンファレンスで、新機能の発表や活用事例が共有される場です。Datadog・Tapple のみなさんと、Feature Flags や LLM Observability を使って、AI を品質とコストを担保しながら速く出す方法について話す予定です。オンライン視聴もできるので、よかったらぜひご覧ください！

<https://dash.datadoghq.com/sessions/the-ai-engineering-playbook-how-to-evaluate-iterate-at-every-phase-of-development/>

さて、本題です。私たちは Datadog のアラートを起点に障害を調べてくれる SRE エージェントを社内で動かしています。エージェントを本番に出すと、必ず「応答の質をどう保ち続けるか」という壁にぶつかります。レビューやドキュメントだけでは追いきれません。

そこで Datadog LLM Observability の Evaluations と Experiments を両方使い、品質チェックを2段構えにしました。本番のトレースを常に採点して劣化に気づく層と、プロンプトを変えたときに前後を比べる層です。この2段はどちらも、Claude Code の Datadog MCP のおかげでほぼ対話だけで用意できました。今回はその記録を残しておきます。

## 背景：Evaluations だけでは「変更の良し悪し」が測れない

Datadog LLM Observability は、LLM アプリの入出力・トークン数・レイテンシ・コスト・エラーを **トレース**として可視化する機能です。1リクエストを「どのプロンプトで、どのツールを呼び、何を返したか」というスパンの連なりで追えるので、エージェントのように複数ステップを踏む処理でも、どこで何が起きたかを後から辿れます。その可視化の上に、品質を自動で採点する **Evaluations** と **Experiments** が乗っている、という構図です。

<https://docs.datadoghq.com/ja/llm_observability/>

Datadog の LLM Observability で評価に使う機能は **Evaluations** と **Experiments** の 2 つです。Evaluations は本番トレースに対して評価を走らせる仕組み、Experiments は用意したデータセットに対して走らせる仕組みで、一般的な言い方をすれば前者がオンライン評価、後者がオフライン評価にあたります（評価ロジックである evaluator 自体は両方で共通して使えます）。

|  | Evaluations（本番トレースに評価） | Experiments（データセットに評価） |
| --- | --- | --- |
| 対象 | 本番トレースを常時自動採点 | 固定データセットにバッチ実行 |
| 用途 | 劣化に気づく（異常検知） | 変更前後をスコア比較（回帰防止） |
| いつ動く | 常時 | プロンプト/モデル変更時 |

Evaluations は「最近この指標が下がってきた」に気づくレーダーとして優秀です。ただ、プロンプトを書き換えたときに「同じ入力で前より良くなったのか」を確かめるには、入力を固定して前後を並べる必要があります。ここを担うのが Experiments です。

本記事では、この 2 つを Evaluations から順に整えていった流れを紹介します。

## Claude Code の Datadog MCP がそのまま使えた

この手の評価基盤は、ふつう「トレースを眺める → 評価軸を設計する → 評価器を書く → データセットを用意する → 実験を回す」と手数が多く、腰が重い作業です。今回はそこを Claude Code の Datadog MCP（MCP = Model Context Protocol。AI から外部ツールを呼び出すための規格）に任せました。

導入は Datadog が用意している導線に乗るだけで、大きく 2 ステップ。

まず、Datadog の MCP サーバを Claude Code につなぎます。

```
claude mcp add --scope user --transport http datadog-llmo-mcp \
  'https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=llmobs,core'
```

次に、Datadog が GitHub で公開している LLM Obs 用のスキルセット（Experiment のワークフローをエージェントに教えるもの）を入れます。`datadog-labs/agent-skills` リポジトリから取得します。

<https://github.com/datadog-labs/agent-skills>

```
npx skills add datadog-labs/agent-skills/dd-llmo --full-depth -y
```

これで、トレース検索・評価器の作成更新・データセット・Experiments といった操作が、ツールとして Claude Code から使えるようになります。

あとは対話で進めます。実際は次のような依頼を重ねていくだけでした。

* 「ml\_app が ○○ のトレースを見て、品質の評価軸を提案して」 → 実トレースを読んで評価軸案を出す
* 「この評価器をオフライン（Experiments）でも回せるよう移植して」 → SDK コード化
* 「本番トレースの入力でデータセットを作って、現行プロンプトで採点して」 → データセット作成と baseline 実行
* 「プロンプトをこう変えた candidate を回して、baseline と比較して」 → A/B

実際の Claude Code 上のやり取りは、およそこんな雰囲気です。

```
› Datadog の sre-agent-dev のトレースを見て、品質の評価軸を提案して

● search_llmobs_spans(ml_app: "sre-agent-dev", span_kind: "agent")
  ⎿  40 件のトレースを取得
● インシデント調査と実装 Q&A の 2 モードが混在しています。
  両モードを採点できる評価軸を提案します:
   - request_type / goal_completion / investigation_completeness
   - report_grounded_in_evidence / no_secret_leakage …（計 15 軸）

› オンライン評価器として publish して

● create_or_update_llmobs_evaluator(goal_completion …)  ×15
  ⎿  15 評価器を publish（gpt-5.4-mini, 日本語 reasoning）

› これをオフライン(Experiments)でも回せるよう移植して

● Write(experiments/evaluators.py)
  ⎿  15 評価器を LLMJudge に移植

› 本番トレースの入力でデータセットを作って baseline を採点して

● Bash(uv run python experiments/build_dataset.py)
  ⎿  ✅ dataset 作成（11 records）
● Bash(uv run python experiments/run_experiment.py --label baseline)
  ⎿  ✅ Experiment 完了 → https://…/llm/experiments/xxxx
```

Datadog 公式も「Bootstrap your Experiment」として、ml\_app・データセット・評価器をまとめて指示するプロンプトのひな形を配っており、最初はそれを貼るところから始められます。

トレースの中身を読みながら進められるので、思っていたより設計がブレませんでした。

## まず入れたのは Evaluations（オンライン評価）

順番としては Evaluations が先でした。対象のエージェントには評価器がひとつも設定されていなかったので、まずは本番トレースを自動で採点するレーダーを置くところからのスタートです。

ここで一度つまずきました。このエージェントは「インシデント調査」と「コードの実装・How-to の質問」の 2 モードを持つのに、最初はインシデント前提の評価軸だけを作ってしまい、実装質問のトレースを軒並み誤判定してしまったのです。そこで、どちらの依頼なのかをまず見分けたうえで、両モードを公平に採点できる 15 軸に組み直しました。

判定モデル（judge）には社内の Azure OpenAI を使い、評価理由は日本語で出す構成にしています。judge の言うことを鵜呑みにするのも不安だったので、簡単な検証もしています。人手の感覚と食い違わないかを見たうえで、明らかな機密漏れや矛盾した結論をわざと混ぜ、ちゃんと弾けるかも試しました。結果は、実用には十分という手応え。コストも mini クラスなら 1 トレース十数円、月あたり数百円で回せる程度でした。

これでレーダーは常時動くようになりました。とはいえレーダーは異常を知らせてくれるだけです。プロンプトを変えて前より良くなったかを測るには、やはり Experiments が要ります。ここからが後半です。

## つぎに：変更を測る Experiments

後半は Experiments です。狙いはプロンプト変更の回帰防止。正解ラベル（ground truth）を用意するのはコストが高いので、まずは既存の本番トレースの入力を固定データセットにして、変更前後でスコアの動きを見る、という割り切ったアプローチにしました。

構成はシンプルで、以下を用意しました。

* 本番のオンライン評価器を、SDK のコードとして移植したもの
* 本番トレース由来の入力を固定したデータセット
* 各入力に対してエージェントを再実行し、出力を採点する実験スクリプト

Datadog への連携は MCP ではなく、SDK が API キーで intake に直接送信します。実行はこれだけです。

```
# データセットを作成
uv run python experiments/build_dataset.py
# 現行プロンプトで採点（baseline）
uv run python experiments/run_experiment.py --label baseline
# プロンプトを変えたら candidate を回して比較
uv run python experiments/run_experiment.py --label candidate --system-prompt-file prompts/candidate.txt
```

## 結果：眺めるだけでは気づきにくいバグが見えた

baseline を回して最初に見えたのは、エージェントが **ある種の質問を気まぐれに断っている** ことでした。似たような質問でも、あるものは丁寧に調べて答えるのに、別のものは「これは担当外です」と即答で突き返す。本番ログを眺めているときは「たまに断るな」くらいの感覚でしたが、固定データセットに通すと、はっきり再現する偏りとして数字に出てきます。

原因はプロンプトの役割定義が狭すぎたことでした。対応範囲を補う一文を足した candidate を用意し、同じデータセットで A/B したところ、不当な拒否はほぼ消え、構成・具体性・網羅性といった主要なスコアもまとめて上がりました。この規模（今回は 11 件）でも、一行の変更が複数の評価軸のスコア差として見て取れます。

## やってみて感じたこと

良かったのは、トレース調査から評価器の移植、データセット化、A/B までをほぼ対話だけで組めたことです。実データを見ながら設計できるので、評価軸が現場の肌感に合いやすいのも効きました。

もちろん LLM-as-judge は万能ではありません。たとえば「きちんと辞退した」応答を、品質系の評価器が一律に減点してしまうことがあります。辞退は間違いではなく「答えていない」だけなので、そこを切り分けるゲートが要ります。エージェントを実際に再実行する方式だと、裏側の本番データが動いた分もスコアに乗るので、差分は厳密な因果ではなく傾向として読む割り切りも必要でした。このへんは運用しながら育てていく部分だと思っています。

## まとめ

Evaluations が「劣化に気づくレーダー」なら、Experiments は「変更の良し悪しを並べて測る物差し」です。正解ラベルがなくても、既存トレースを固定データセットにするだけで、プロンプト変更の効果を多軸のスコアで追えました。

何より、この評価基盤の立ち上げが Claude Code の Datadog MCP でかなり楽になっています。ドキュメントやレビューだけで AI エージェントの品質を守るのは限界があります。評価軸をコードに落とし、変更のたびに同じデータセットで回す型をいちど作っておけば、プロンプトもモデルも安心して触れるようになるはずです。

---

LayerX では、AI エージェントの信頼性をこうした計測の面から支える仲間を募集していますので、どうぞよろしくお願いいたします。

<https://open.talentio.com/r/1/c/layerx/pages/52751>

最後まで読んでいただき、ありがとうございました。
