---
id: "2026-07-12-claude-code-の部下に-codex-と-grok-と-agy-を雇った夜-サブエージェント-01"
title: "Claude Code の部下に codex と grok と agy を雇った夜 — サブエージェント E2E で UNCONFIRMED が 2 つ確定した"
url: "https://note.com/zephel01/n/n6da3b5152f5f"
source: "note"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "OpenAI", "Gemini"]
date_published: "2026-07-12"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

> **TL;DR**: 前話（v2.9.0・plugin 切り出し）の**直後の状態**で、外部エージェント backend が「実際に Claude Code のサブエージェントとして動くのか」を初めて実機で通しました。体制が特殊です ── テストキット（`providers.yaml` / サブエージェント定義 / `run\_e2e.sh`）は Cowork の Claude（司令塔）が書き、実行は作者が Mac のターミナルでやり、結果ログを Claude が判定する「**リモート E2E**」の往復です。Claude は Mac のバイナリを直接叩けない、という制約が出発点でした。orchestrator の main だけは Ollama（qwen3-coder:30b）、部下は claude/codex/grok/agy の 4 CLI。初回は `plugin-not-found` で serve が即死しましたが、**エラーメッセージ自体が移行手順を出す**（31 話で仕込んだ緩和策）に助けられました。本番 run `20260711-232732` は Phase A **4/4**、Phase B **3/4**（grok が exit 0 の空応答で FAIL）、Phase C（サブエージェント E2E）**3/4**（ext-codex だけ FAIL）。そして最大の収穫 ── ワイヤ上に「これはサブエージェントです」という識別子は無いのに、**frontmatter のカスタム model 名（`e2e-claude` 等）が `signals.model` に無加工で届く**ことを実測で確認しました。docs に「UNCONFIRMED」と書いて放置していた宿題が 2 つ確定し、「**モデル名をルーティングキーに使う**」設計が Claude Code × CodeRouter で公式に成立しました。grok の空応答と ext-codex の失敗は、それぞれ次話・次々話で釣り上げます。

---

## あらすじ — 32 話目です

連作のタイムスタンプ。初コミットは **2026-04-19**。本記事の検証は **2026-07-11 の 23 時すぎ〜翌未明**、初コミットから **84 日目の夜**です。前話（第 31 話・Phase 2 完結）と**同じ 84 日目の続き**、その晩のうちに始めた実機検証の記録です。

![](https://assets.st-note.com/img/1783791474-2Lz6xMirKuNdS0X8FUnyYoVw.png?width=1200)

この連作の通低音はずっと「**机上で動くはず → 実機が裏切る → 直す**」でした。今回もその型に乗ります。ただし今回は「1 つの機能を実機で裏切られる」のではなく、**12 本のテストを一度に通して、10 本が緑・2 本が裏切る**という団体戦です。裏切った 2 本 ── grok の空応答と ext-codex の失敗 ── は今回は事実だけ記録し、それぞれ次話・次々話で追い込みます。今回の主役は、裏切らなかった側で確定した設計のほうです。

---

## 制約から始まった — Claude は Mac のバイナリを叩けない

まず今回の変わった体制を書いておきます。これまでの回は「Cowork の Claude が実装し、作者がレビューして統合する」でした。今回はもう一段ねじれています。**検証対象が作者の Mac 上のバイナリ**（`coderouter serve` / `claude` CLI / codex / grok / agy）なので、司令塔である Cowork の Claude は、それを直接実行できません。クラウドのコンテナから Mac のターミナルには手が届かないからです。

そこで採ったのが「リモート E2E」です。役割はこう割れました。テストキット ── `providers.yaml`、サブエージェント定義、`run\_e2e.sh` ── は**司令塔の Claude が書く**。実行は**作者が Mac のターミナルで叩く**。出てきた結果 zip や貼り付けログを、**Claude が判定する**。書く・走らせる・読む、が三者に分かれた往復です。

Claude 側は手ぶらで待っていたわけではありません。実行の前に、クラウドのコンテナ内で実スキーマを使って `CONFIG-OK`、plugin 込みで serve を起こして `HEALTH-OK`、`e2e-grok` リクエストでルールが発火してアダプタが grok バイナリの起動を試みて「No such file or directory」で止まる ── **CLI が無い環境でも、ルーティングだけは通ることを確認できる**ところまで先回りしてありました。実機に渡す前に、配管の絵は描き終えていたわけです。

小さな躓きも 1 つ。リモートのツールからは `.claude/` 配下に直接書き込めない制約があり、`claude-agents/` を staging 置き場にして、`run\_e2e.sh` が実行時に `.claude/agents/` へ `cp` する方式に変えました。司令塔が触れない場所には、スクリプトに運ばせる ── これも制約から生まれた形です。

---

## テストキットの設計 — なぜ main だけ Ollama なのか

キットの置き場はリポジトリの `\_run/e2e-agents/` です。`providers.yaml` には 5 つの provider を並べました。orchestrator 本体の **main-ollama**（qwen3-coder:30b）と、部下の agent\_cli 4 種 ── `agent-claude`（sonnet）/ `agent-codex`（gpt-5.5）/ `agent-grok`（grok-4.5）/ `agent-antigravity`（"Gemini 3.5 Flash (Low)"）です。4 種は全部 `paid: false`、つまりサブスク OAuth で動かします。`plugins.enabled: [agents]` の二段ゲートも当然オンです。

ここで一番の設計上のキモが **main だけが Ollama である理由**です。orchestrator 本体は `Task` ツールを呼んで部下を起動しなければなりません。ツールを呼ぶには tool 対応の backend が要ります。ところが agent\_cli は capabilities が `tools: false` ── プロンプトを入れてテキストが出るだけの一問一答窓口なので、orchestrator の main には使えないのです。ここを分かっていないと「全部 agent\_cli に流せばいい」と考えがちですが、それだと司令塔がそもそも部下を呼べません。だから main には tool を扱える backend、今回は Ollama の qwen3-coder:30b を据えました（`ollama ps` 実測で 44GB・100% GPU・CONTEXT 262144）。

ルーティングは auto\_router に任せます。`model\_pattern "e2e-claude.\*"` → claude-agent、という調子で 4 本のルールを引き、`default\_rule\_profile: main` に落とします。main の sonnet も、Claude Code が裏で投げる背景リクエストも、明示ルールに当たらないものは全部 main が受ける形です。

そして今回の主題に直結するのが、サブエージェント定義 `.claude/agents/ext-{claude,codex,grok,agy}.md` の frontmatter です。ここの `model` を、`e2e-claude` のような**カスタム名**に固定しました。本文の指示は「一問一答のリレー役、ツール禁止、答えの末尾に `CODEX-OK` などのマーカーを付ける」だけです。`run\_e2e.sh` は preflight（CLI・ログイン・Ollama・ポート）から serve 起動、Phase A（ヘッダ駆動）、Phase B（`model\_pattern`）、Phase C（サブエージェント E2E）まで走らせ、`report.md` を自動生成します。

---

## 最初の罠 — plugin-not-found、そして 31 話の自分に助けられる

キットを渡して 1 回目の起動。serve は即死しました。

```
plugin-not-found
ValueError: Unknown adapter kind 'agent_cli'
```

見覚えのあるエラーです。原因は環境の食い違いでした。coderouter は `uv tool install` の隔離環境に入っているのに、plugin だけを `uv pip install` で**別の環境**に入れてしまっていた。隔離された tool 環境からは、その plugin が見えません。前話で切り出したばかりの二段ゲートに、さっそく自分で足を取られた格好です。

救われたのは、このエラーメッセージ自身が移行手順を吐いたことです。指示どおり `uv tool install --force` で plugin を `--with` 同梱し直すと、あっさり通りました。

```
uv tool install --force coderouter-cli \
  --with "coderouter-plugin-agents @ git+https://github.com/zephel01/coderouter-plugin-agents"
```

第 31 話で、in-core を消す代わりに緩和策として仕込んだのが、まさに「旧 config で起動したら移行手順つきのエラーで止める」でした。その緩和策が、切り出しの翌日、**作者自身のうっかりを 1 分で解いてくれた**わけです。消した側が、消したことの後始末で助けられる ── 小さいけれど、円環がひとつ閉じました。

---

## 本番、run 20260711-232732 — 12 本中 10 本が緑

環境が揃ったところで本番です。CodeRouter v2.9.0、coderouter-plugin-agents 0.1.0、Claude Code CLI は検証中に 2.1.206 から 2.1.207 へ上がりました。codex-cli 0.144.1 / grok 0.2.93 / agy 1.1.1、テストは既存の 8088 と別に port 8189 で立てています。

**Phase A**（`X-CodeRouter-Profile` ヘッダ駆動・OpenAI ingress）は **4/4 PASS**。`PONG-CLAUDE` / `PONG-CODEX` / `PONG-GROK` / `PONG-AGY` が全部返ってきました。ヘッダで直接プロファイルを名指しする、いちばん素直な経路です。

**Phase B**（`model\_pattern`・Anthropic ingress の `/v1/messages`）は **3/4 PASS**。`e2e-claude` は「42」（ついでに plan モードらしく「no plan is needed here」と余計な一言つき）、`e2e-codex` も `e2e-agy` も「42」。ただし `e2e-grok` だけが FAIL でした。exit 0、valid JSON、`stop\_reason` は `end\_turn`、なのに `text` が空文字。ルール `e2e:grok` は正しく発火し（`auto-router-resolved` が 1 回)、アダプタも約 4 秒で `provider-ok`。配管は全部通ったのに、中身だけが空で返ってきた ── この「**exit 0 の空の成功**」が第 34 話の主役になります。今回は「起きた」とだけ書いておきます。

**Phase C**（本命のサブエージェント E2E。`claude -p` → orchestrator が `Task` → 部下 4 種を起動し、答えは「144」で判定）も **3/4 PASS**でした。

![](https://assets.st-note.com/img/1783791504-pta7uCw61mNFYVPZnvkUA9OB.png?width=1200)

ext-codex だけが落ちました。orchestrator の最終出力は「The system indicates that no agent named 'ext-codex' is reachable」という、謝罪文めいた台詞です。ただし serve のログを覗くと、話はそう単純ではありませんでした ── この一件だけで章がひとつ立つので、切り分けは丸ごと次話に預けます。ここでの結論は「Phase C は 4 本中 3 本が通り、codex だけが到達不能を訴えた」まで。合わせて 12 本中 10 本が緑、という夜でした。

---

## ワイヤに「サブエージェント」は書いていない — UNCONFIRMED が 2 つ確定

さて、今回いちばん持ち帰りたかったのはテストの合否そのものではありません。設計の答え合わせです。

CodeRouter はモデル名のパターンでルーティングします。ところが Claude Code のサブエージェントを外から見ると、困ったことに **ワイヤ上に「これはサブエージェントからのリクエストです」という識別子が無い**のです。main が投げる背景リクエストと、部下が投げるリクエストを、CodeRouter は口では区別できません。区別する手がかりがあるとすれば、リクエストに乗ってくるモデル名だけ ── そこに部下ごとの固有名が無加工で届いてくれれば、それをルーティングキーにできます。逆に届かなければ、この設計は成り立ちません。

`docs/guides/subagent-routing.md` の §7 には、まさにここが「UNCONFIRMED」として 2 つ、宿題のまま残っていました。今回の実測で、両方が確定します。

1. サブエージェント（frontmatter 由来）の model 名は、**カスタム文字列がそのまま届く**。`signals.model` に `e2e-claude` などが無加工で出現し、エイリアス検証は挟まりませんでした。
2. main の `--model sonnet` は、**`claude-sonnet-5` にフル ID 展開**されて届く。

1 番目については、書き方に注意が要ります。Claude Code の公式ドキュメント（model-config）は、カスタムな `ANTHROPIC\_BASE\_URL` の配下では「your provider or gateway defines the model names, so Claude Code passes any string through without checking it」と明記しています ── ゲートウェイの下ではモデル名を検証せず素通しする、というのが**公式仕様**です。今回確認したのは、その仕様の**帰結**です。`e2e-claude` のような範囲外のカスタム文字列が実際に frontmatter で受理され、無加工で `signals.model` まで届く、という具体挙動を実測で押さえた。仕様そのものの発見ではなく、仕様の帰結が現場でその通りに出た、という確認です。

この 2 つが揃うと、設計が閉じます。**サブエージェントには衝突しないカスタム名、main にはフル ID パターン**を割り当てれば、ワイヤに識別子が無くても、モデル名だけで両者を別プロファイルへ振り分けられる。「モデル名をルーティングキーに使う」という筋が、Claude Code × CodeRouter で公式に成立した、と言い切れる根拠が揃いました。docs の §7 は日英とも書き換え、§6.1 に実測検証結果のセクションを新設して反映済みです。UNCONFIRMED の付箋を 2 枚、実機で剥がせた夜でした。

---

## main ループはなぜ重いのか — 毎ターン 3 万トークンの前奏

最後に、今回の検証がやたら時間を食った理由を、背景として書き残しておきます（この重さは次話でも効いてきます）。

orchestrator の main は Ollama の qwen3-coder:30b です。ここに Claude Code の system prompt 一式が毎ターン乗るため、`input\_tokens` は常に **33,800〜36,500** 前後。しかも Ollama の Anthropic 互換エンドポイントは prompt caching に対応しておらず、`cache\_read\_input\_tokens` は常に 0（`cache-observed: no\_cache`）でした。毎ターン、3 万トークン超をキャッシュ無しで前から舐め直す構図です。

その結果、初回の prefill は 1 ターンあたり 3〜4 分かかります。ただし救いもあって、2 回目以降は 5〜15 秒まで縮みました（serve.log の `try-provider` → `provider-ok` の間隔の実測。サーバ側でプレフィックスの KV が再利用できていると見られます）。それでも Phase C の部下 4 本を通すと、計 30〜45 分コースです。ext-agy が 442 秒・6 turns かかったのも、この重い main を経由するからでした。

弱いローカル orchestrator に Claude Code の重い前奏を毎ターン弾かせる ── この構図が、次話でもう一段厄介な形で牙をむきます。

---

## まとめ

![](https://assets.st-note.com/img/1783791532-sIwHTfqx26QGB4PFiW9dSe1t.png?width=1200)

> **教訓**: ワイヤに「これはサブエージェントだ」という札は下がっていない。それでも frontmatter のカスタム model 名が無加工で届くなら、モデル名そのものをルーティングキーにできる。公式仕様（ゲートウェイ配下ではモデル名を検証せず素通し）の帰結を実機で 1 回踏んで確認すれば、「UNCONFIRMED」は「確定」に変わる。そして E2E の団体戦では、10 本の緑より、裏切った 2 本のほうが翌日の仕事になる ── テストが本当に価値を出すのは、通ったときではなく、落ちたときだ。

12 本中 10 本が緑で、設計の宿題を 2 つ片づけられた ── それだけなら、気持ちよく寝られる夜でした。ですが落ちた 2 本が、どちらも「ただの FAIL」では終わらせてくれませんでした。

次回・第 33 話は、その 1 本目 ── **ext-codex だけが「到達できない」と言い張った件**を追います。orchestrator は「そんなエージェントは居ない」と謝りましたが、serve のログはまったく別のことを語っていました。「エージェントに到達できない」という司令塔の申告を、どこまで信じてよいのか。ワイヤに聞きに行きます。

---

CodeRouter は MIT ライセンスの OSS です: <https://github.com/zephel01/CodeRouter>  
`pip install coderouter-cli` / `uvx coderouter-cli serve` で動きます。  
外部エージェント backend は `coderouter-plugin-agents` プラグインとして提供します（v2.9.0 で Core から切り出し済み）。使うには `pip install`（git+https）＋ `plugins.enabled: [agents]` の二段ゲートが必要です。認証はサブスク優先、子プロセスへの API キー継承はしません。
