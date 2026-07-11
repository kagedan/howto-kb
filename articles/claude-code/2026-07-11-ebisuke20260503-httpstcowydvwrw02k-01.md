---
id: "2026-07-11-ebisuke20260503-httpstcowydvwrw02k-01"
title: "@ebisuke20260503: https://t.co/WyDVWrw02k"
url: "https://x.com/ebisuke20260503/status/2075922868702216527"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "x"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/WyDVWrw02k


--- Article ---
Jul 7, 2026

## workflowの怖さは、賢さよりも散らばり方に出る

今日のAI coding watchでは、Claude Code v2.1.202 が一番引っかかった。

release noteには、履歴検索クラッシュ、remote control、mTLS、skill重複読み込み、/review の挙動戻しなど、実務で効く修正がかなり並んでいる。けれど今回ぼくが見るべきだと思ったのは、先頭の2つだ。

- /config に Dynamic workflow size が入り、Claudeが作るdynamic workflowの規模を small / medium / large の目安で寄せられるようになった

- workflowからspawnされたagentのtelemetryに workflow.run_id と workflow.name が入り、OpenTelemetry上で1つのworkflow runを再構成できるようになった

どちらも、単体では地味に見える。

でも、Claude Codeのdynamic workflowsは、そもそも「大きい仕事を複数agentに分けて裏で走らせる」機能だ。v2.1.154の時点で、tens to hundreds of agentsという表現が出ていた。今のdocsでも、workflowは1 agentのコンテキストに収まらない作業や、同じ処理を多くの対象へかける作業向けだと説明されている。

ここで問題になるのは、agentが何体出せるかだけではない。

あとから、あの大きな仕事が何だったのかを、どの粒度で取り戻せるか だ。

## prompt.id だけでは、大きな仕事の名前になりにくい

Claude Codeのmonitoring docsを見ると、OpenTelemetryはすでにかなり細かい。

session、cost、token、tool decision、active time、API request、tool result、MCP connection、skill activationなどが出る。traces betaでは、1つのuser promptからAPI requestやtool executionへつながるspanを見られる。BashやPowerShell subprocessには TRACEPARENT を渡し、対応した下流処理を同じtrace配下へつなげる設計もある。

この方向は前からかなり良い。

ただ、workflowでは少し足りない。

普通の対話なら、prompt.id はかなり自然な単位になる。「この一言から何が起きたか」を追えばいいからだ。

でもworkflowは、対話の中の一瞬から始まり、複数agentへ広がり、同じrun内で調査、編集、検証、要約が並ぶ。途中でskillが呼ばれたり、subagentがさらにagentを生んだりする。人間が見たい単位は、最初のpromptよりも「このworkflow run」になる。

docsでは、v2.1.202以降、workflow.run_id はworkflowに属するagentが出すAPI/tool eventsへ付く。agentがさらにspawnしたagent、たとえばskill invocationまで覆う。workflow.name も一緒に出る。ただしuser-authored nameは、詳細ログのgateを開かない限り custom に置き換わる。

ここが好きだ。

名前は便利だが、privateな作業名や社内用語を含みやすい。だから識別子は残す。名前は必要なら残す。user-authored nameはデフォルトでぼかす。

7月1日にCodexのWebSocket trace修正について書いたときは、「観測のためにraw payloadを残しすぎない」話だった。今回のClaude Codeは、反対側から同じ問題に触れている。

raw本文を増やすのではなく、再構成に必要なキーを足す。

## Dynamic workflow sizeは、capではなく「作りすぎない癖」

もう一つの Dynamic workflow size も、runtime制限ではなくadvisory guidelineだ。

docsでは、small は5 agent未満、medium は15 agent未満、large は50 agent未満を目安にClaudeへ送る。unrestricted がdefault。prompt側で別の規模が必要なら上書きされるし、run
