---
id: "2026-06-29-ai-agent-の改善した気がするをやめる改善ループを-trace-で見えるようにした-01"
title: "AI Agent の「改善した気がする」をやめる：改善ループを trace で見えるようにした"
url: "https://zenn.dev/sunyeul89/articles/0d51dea1eae162"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "LLM", "zenn"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

## はじめに

AI Agent の Skill 改善は、放っておくとすぐに「良くなった気がする」になりがちです。

プロンプトを少し直した。  
手順を少し足した。  
失敗例を反映した。

すると、なんとなく改善したように見える。でも本当に良くなったのか、どの evidence に基づいて良くなったと言っているのか、どの判断で新しい skill を採用したのかは曖昧になりやすいです。

前回の記事では、この問題に対して、小さな SkillOpt-style harness を作りました。

<https://zenn.dev/sunyeul89/articles/c8f32b161d5559>

この harness は LLM agent runner ではありません。Codex や human が外側で作った rollout records や edit proposals を受け取り、candidate skill を作り、parent skill と比較し、strict gate で採否を決めるものです。

前回は、改善ループの結果を artifact として残すところまで作りました。今回やりたかったのは、その次です。

artifact は残っている。  
でも、改善ループの流れは見えにくい。

そこで OpenTelemetry を使って、Skill 改善ループを trace として観測できるようにしました。

この記事は OpenTelemetry の入門ではありません。書くのは、次の小さな実験です。

![artifact と trace の役割分担](https://static.zenn.studio/user-upload/010a76538231-20260630.png)  
*artifact で結果を確認し、trace で判断の流れを確認する。*

## 背景：artifact で evidence を残す

### 何を「改善した気がする」で済ませたくなかったのか

前回作った harness の目的は、AI Agent の Skill 改善を、雰囲気ではなく evidence に寄せることでした。

この harness では、train / selection / test の役割を分けます。train split は改善案を作るため、selection split は parent / candidate を比較するため、test split は最終確認のために使います。

この分離によって、少なくとも次のような状態を避けたいと考えていました。

```
失敗例を見た
skill を直した
なんとなく良さそうなので採用した
```

代わりに、harness は artifact を残します。

```
full-loop-manifest.json
gate-decision.json
parent-selection.jsonl
candidate-selection.jsonl
aggregated-edits.json
selected-edits.json
update-report.json
```

これらを見ると、どの evidence が残り、どの candidate が作られ、どの score で採用されたのかを確認できます。ここまでは前回の記事で扱った範囲です。

### 導入前：artifact は残るが、流れは頭の中で再構成していた

artifact が残ること自体はかなり重要です。

たとえば、今回 replay した loop の `gate-decision.json` には次のような結果が残っていました。

gate-decision.json

```
{
  "decision": "accept_new_best",
  "parent_score": 0.6,
  "candidate_score": 1.0,
  "best_score": 0.6,
  "leakage_status": "clean",
  "rollout_isolation": "independent",
  "reject_reason": null
}
```

この JSON を見ると、candidate が parent より良く、contamination もなく、rollout isolation も `independent` なので、新しい best として採用されたことが分かります。

ただし、この結果に至るまでの流れを理解するには、他の artifact も読む必要があります。

```
full-loop-manifest.json
selected-edits.json
update-report.json
parent-selection.jsonl
candidate-selection.jsonl
gate-decision.json
```

証拠は残っている。でも、改善ループの流れは複数 artifact から再構成する必要がある。ここが今回の問題でした。

artifact は evidence としては十分に大事です。ただし、改善ループの execution map ではありません。

### 具体例：accept\_new\_best を理解するまで

今回の loop では、candidate skill に適用された edit は 2 件でした。

selected-edits.json

```
{
  "edits": [
    {
      "id": "E1-contract-checklist",
      "op": "add",
      "score": 0.95,
      "section": "## Rules"
    },
    {
      "id": "E2-full-contract-small-change",
      "op": "add",
      "score": 0.89,
      "section": "## Rules"
    }
  ]
}
```

`update-report.json` では、この 2 件がどちらも適用に成功していました。

update-report.json

```
{
  "applied_count": 2,
  "failed_count": 0,
  "validation_errors": []
}
```

ここまで読むと、candidate skill が「どの edit によって作られたか」は分かります。さらに selection records と gate decision を読むと、parent が 0.6、candidate が 1.0 で、`accept_new_best` として採用されたことも分かります。

ここで欲しかったのは、新しい最適化アルゴリズムではありません。次の流れをそのまま見られる execution map でした。

```
proposal -> aggregate -> select -> apply -> gate -> score -> decide
```

## 欲しかったもの：decision flow の execution map

### OpenTelemetry で何を見るのか

今回 OpenTelemetry で見たいものは、LLM の中身でも、Codex の実行 trace でも、token cost でもありません。見たいのは、harness の decision flow です。

設計した span tree は、だいたい次の形です。

```
skillopt.loop_run
 ├─ skillopt.proposal
 │   ├─ skillopt.aggregate_edits
 │   ├─ skillopt.select_edits
 │   └─ skillopt.apply_edits
 └─ skillopt.gate
     ├─ skillopt.score_parent
     ├─ skillopt.score_candidate
     └─ skillopt.decide
```

ここで重要なのは、trace が artifact を置き換えるわけではないことです。役割は分けています。

```
artifact = 何が evidence として残ったか
trace = どの順番で判断が進んだか
```

### 導入後：decision flow を trace として見られるようになった

OpenTelemetry を有効にすると、改善ループを span tree として見られるようになります。

今回確認した trace は、Jaeger では次のように見えます。

![Jaeger で見た skillopt.loop_run の waterfall](https://static.zenn.studio/user-upload/beff0fcde1d9-20260630.png)  
*`skillopt.loop_run` の中で proposal と gate が child span として見え、最後に `decide` で採否が決まる。*

特に `skillopt.decide` span を見ると、gate decision に必要な値が attribute としてまとまります。

```
parent_score = 0.6
candidate_score = 1.0
score_delta = 0.4
decision = accept_new_best
leakage_status = clean
rollout_isolation = independent
```

これにより、artifact で確認した結果と、trace で見える decision flow が同じ話をしていることを確認できます。OpenTelemetry は採否の根拠ではなく、その判断がどの順番で進んだかを見るための補助線です。

### 導入前後で何が変わったか

OpenTelemetry を入れる前後の違いは、次のように整理できます。

| 観点 | 導入前 | 導入後 |
| --- | --- | --- |
| 採否 | `gate-decision.json` で確認 | 同じく artifact で確認 |
| score | `parent-selection.jsonl` / `candidate-selection.jsonl` を読む | artifact に加えて span attribute でも追える |
| 実行順序 | 複数 artifact から頭の中で再構成 | span tree で見える |
| candidate 作成過程 | `selected-edits.json` と `update-report.json` を読む | `aggregate_edits` / `select_edits` / `apply_edits` span で流れが見える |
| 失敗箇所 | artifact と error message を探す | どの span で止まったか追いやすい |
| 説明しやすさ | JSON/JSONL を横断して説明 | waterfall と attribute で説明できる |

採否の source of truth は変えていません。trace だけを見て「改善した」と言うのではなく、artifact で結果を確認し、trace で流れを確認する。そのための導入です。

## 実装と検証

### 実装は最小限にした

実装はかなり小さくしました。

やったことは主に次の通りです。

```
OpenTelemetry packages を optional dependency にする
SKILLOPT_OTEL_ENABLED=1 のときだけ有効にする
無効時や dependency 未導入時は no-op にする
backend 固有のコードは入れない
trace だけを扱う
metrics / logs は扱わない
```

環境変数で opt-in する形です。

```
SKILLOPT_OTEL_ENABLED=1
OTEL_SERVICE_NAME=skillopt-harness
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

span attributes に載せる情報も、score、decision、edit count などの軽量な metadata に絞りました。

```
skillopt.parent_score
skillopt.candidate_score
skillopt.score_delta
skillopt.decision
skillopt.leakage_status
skillopt.rollout_isolation
skillopt.selected_edit_count
skillopt.applied_edit_count
skillopt.failed_edit_count
```

逆に、次のようなものは載せません。

```
prompt
skill body
source code
verifier stdout/stderr
secrets
raw user data
```

trace は便利ですが、何でも載せる場所ではありません。特に AI Agent 周りでは prompt や source code を雑に attribute に入れたくなりますが、今回はそこを避けました。

実装の中心は、次のファイルです。

* `skillopt_harness/telemetry.py`: no-op fallback と OpenTelemetry 初期化
* `skillopt_harness/skill_loop.py`: `loop-run` / proposal / gate / decide の span
* `otel/collector.yaml`: debug exporter 付きのローカル collector 設定
* `otel/docker-compose.yaml`: Jaeger UI 用の compose 設定

### 実際に確認したこと

今回の recorded loop を使って、telemetry disabled / enabled の両方で `loop-run` を replay しました。

telemetry disabled / enabled のどちらでも、結果は同じでした。

```
parent_score = 0.6
candidate_score = 1.0
decision = accept_new_best
leakage_status = clean
rollout_isolation = independent
```

テストと lint も通っています。

```
pytest: 32 passed
ruff: passed
```

さらに、ローカルの Jaeger で実際の trace も確認しました。確認できた span は次の通りです。

```
skillopt.loop_run
skillopt.proposal
skillopt.aggregate_edits
skillopt.select_edits
skillopt.apply_edits
skillopt.gate
skillopt.score_parent
skillopt.score_candidate
skillopt.decide
```

`skillopt.decide` span でも、上で見た score / decision / leakage status / rollout isolation が attribute として確認できました。artifact で確認した判断と、trace 上で見える decision flow が同じ話をしていた、ということです。

### 調査用 skill に落とし込んだ

trace を見られるようにしただけだと、次に同じ問題を調べるときに、また人間が見方を思い出す必要があります。そこで、この repo には `skillopt-otel-investigation` という調査用 skill も追加しました。

この skill には、今回の役割分担をそのまま入れています。

```
Trace says:
- span attribute から、どの phase で何が起きたかを見る

Artifacts confirm:
- JSON/JSONL artifact で、decision や score を確認する
```

たとえば、`skillopt.decide` span の attribute だけを見て「candidate が採用された」と断定しない。`gate-decision.json` を開いて、artifact 側でも同じ decision になっていることを確認する。そういう調査手順を skill として明文化しました。

また、`localhost:4317` は browser で開く UI ではなく、通常は OTLP gRPC receiver です。この混乱も起きやすいので、collector logs や Jaeger など、実際に trace を見る場所を確認する手順も入れています。

つまり、今回追加した OpenTelemetry は「trace が出るようになった」で終わりではありません。trace を入口にして、最後は artifact で確認する、という調査の型まで一緒に残しました。

## 分かったことと限界

### 分かったこと

今回分かったのは、OpenTelemetry を入れると Skill が改善される、という話ではありません。candidate を採用するかどうかは、これまで通り artifact と strict gate で決まります。

OpenTelemetry が良かったのは、改善ループを説明しやすくなったことです。

artifact だけだと、次のような説明になります。

```
この JSON では parent_score が 0.6 で、
この JSONL では candidate が 1.0 で、
この gate-decision では accept_new_best になっていて...
```

trace があると、次のように言えます。

```
loop_run の中で proposal が走り、
aggregate/select/apply で candidate が作られ、
gate の中で parent と candidate を score 化し、
decide で accept_new_best になった。
```

この 2 つを分けると、AI Agent の Skill 改善ループを少し扱いやすくなります。

### まだ言えないこと

今回の検証で言えるのは、次の範囲です。

```
OTel enabled / disabled で harness の判断結果が変わらないこと
recorded loop の decision flow を trace として確認できたこと
artifact と trace が同じ decision を指していたこと
```

一方で、次のことはまだ言えません。

```
OpenTelemetry によって Skill 自体が改善された
LLM provider の内部挙動まで trace できた
token cost や latency を評価できた
production dashboard として運用できる状態になった
multi-epoch optimization 全体を観測できた
```

このあたりは、今後の追加検証として扱うべきです。

## まとめ

前回は、AI Agent の Skill 改善を「改善した気がする」で終わらせないために、artifact を残す SkillOpt-style harness を作りました。

今回は、その改善ループを OpenTelemetry trace として観測できるようにしました。OpenTelemetry は新しい最適化機構ではなく、artifact で残した evidence に対して execution map を与える補助線です。

「改善した気がする」をやめるには、score や gate だけでなく、その判断がどう進んだかも見えるようにする必要がある。今回の OpenTelemetry 導入は、そのための小さな一歩でした。

## 参考
