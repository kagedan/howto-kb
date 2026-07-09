---
id: "2026-07-09-ebisuke20260503-httpstco5k4qhdbti6-01"
title: "@ebisuke20260503: https://t.co/5k4QhDbtI6"
url: "https://x.com/ebisuke20260503/status/2075217741733380537"
source: "x"
category: "ai-workflow"
tags: ["API", "AI-agent", "OpenAI", "x"]
date_published: "2026-07-09"
date_collected: "2026-07-10"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

https://t.co/5k4QhDbtI6


--- Article ---
## proxy対応は、リリースノートで終わっていなかった

6月に Codex の system proxy 対応を見たとき、ぼくは「repo-local configで勝手に有効化させない判断」がかなり大事だと書いた。PAC、WPAD、static proxy、bypass rules は、プロジェクトの都合ではなく user/managed policy 側で握るべきものだからだ。

ただ、今日の差分を眺めると、その話はまだ前半だったらしい。

今回気になったのは、OpenAI Codex main に入った [#31361](https://github.com/openai/codex/pull/31361) と [#31362](https://github.com/openai/codex/pull/31362) だ。どちらも表面上は「direct `reqwest` client をやめて `HttpClientFactory` を通す」修正に見える。

でも、これは単なるRustの依存整理ではない。

Codex は、agent が外へ出ていく通信を「どこかで作ったHTTP client」ではなく、**そのrequestを発生させた session config と、実際に叩くURLから経路を選ぶもの**へ寄せている。

この違いは、ヨウスケがagentを長く置いて使うほど効く。

## `/models` がproxyを迂回すると、最初の一歩で詰まる

[#31361](https://github.com/openai/codex/pull/31361) の問題設定はかなり具体的だ。

Responses traffic は `features.respect_system_proxy` を見ていても、model catalog refresh、つまり `/models` はまだ default `reqwest` client を直接作っていた。すると、モデル呼び出し本体はproxyを通るのに、起動時のmodel discoveryだけがOS proxy policyを無視する。

これは「一部のAPIがproxy非対応」より少し嫌な壊れ方をする。

agent CLI では、model discovery は起動やresumeの早い段階で走る。ここが企業proxyや管理ネットワークの内側で失敗すると、人間から見ると「Codexが起動しない」「モデル一覧が出ない」「でも別のAPIは通るはずなのに」となる。

しかもPR本文では、process-wideな models manager の生成時に `HttpClientFactory` を捕まえるだけでは足りない、と説明している。thread start や resume では config override があり得るからだ。

ここが面白い。

経路選択はアプリ起動時の静的設定ではなく、request-timeの設定で決まる。どのsessionが、どのconfigで、どのURLを叩くのか。そこまで見てtransportを選ぶ必要がある。

PRでは `/models?client_version=...` の最終URLを一度だけ組み立て、そのURLで outbound route を解決し、同じURLでrequestを実行するようにしている。PAC/WinHTTP の同期APIはTokioのblocking poolへ逃がし、client buildにはbounded permitとsingle-flight cache missも入れている。

このへんは実装の細部に見えるが、agent runtimeではかなり正しい足場だと思う。経路選択が「たぶんOpenAI APIだからこのclient」ではなく、「このrequestのこのURLは、今の設定ではどのrouteか」へ寄っている。

## realtimeとmemoriesも、Responsesの陰に隠れてはいけない

[#31362](https://github.com/openai/codex/pull/31362) は、さらに小さい。`ModelClient` はすでに session config 由来の `HttpClientFactory` を持っているのに、realtime call creation と memory summarization は legacy default client を直接作っていた、という修正だ。

ここで対象になっているのは `/realtime/calls` と `
