---
id: "2026-06-11-明確な-goal-と-eval-でエージェントを動かす-code-with-claude-exten-01"
title: "明確な Goal と Eval でエージェントを動かす — Code with Claude Extended Tokyo で学んだこと"
url: "https://zenn.dev/gaogaoasia/articles/65db07864e31b8"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

![Code with Claude のステージに掲げられた「Code w/ Claude」の看板](https://static.zenn.studio/user-upload/68c2cea46eaf-20260611.jpg)

今半の弁当、マカロン、ムース、Bun の肉まん……。

![](https://static.zenn.studio/user-upload/6310ef035c50-20260611.png)

![](https://static.zenn.studio/user-upload/a201531af1ca-20260611.png)  
![](https://static.zenn.studio/user-upload/4609d3ccdbe1-20260611.png)

……と写真を並べていたら、Slack で「**食レポはええねん！**」と突っ込まれたので、この辺で本題に入ります（笑）。

6月11日、Anthropic の「[**Code with Claude: Extended Tokyo**](https://claude.com/code-with-claude/tokyo-extended)」（本編の翌日に開かれた、独立開発者・アーリーステージの創業者向けの拡張版イベント）に参加してきました。  
普段 [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) を触っている関係で、今回は登壇を聞くより **Workshop（ハンズオン）を優先**して、手を動かす作戦で臨みました。  
当日のワークショップ教材は [anthropics/cwc-workshops](https://github.com/anthropics/cwc-workshops) に公開されています。Managed Agents 周りを中心に回り、最後は Agent Battle まで参加しました（本番ランは、会場で配られた API トークンが手元に届くのが間に合わず...）。

---

## How we Claude Code — 長時間エージェントと付き合う3つの道具

午前は Boris さんのセッションで始まり、その後に参加したのがこのセッションでした。出発点はこの一文です。

> "Agents now run for hours, not minutes and do more work than ever before."

![登壇スライド「Agents now run for hours, not minutes and do more work than ever before.」](https://static.zenn.studio/user-upload/a18de625323f-20260611.jpg)

エージェントが長時間・大量の作業をこなせるようになったぶん、ミスのコストも上がっています。だからこそ、という流れで紹介されたのが「**Three tools for working with long-running agents**（長時間動くエージェントと付き合う3つの道具）」です。それを Phase 1〜3 の実装で体感する構成でした。

### ① 曖昧さを消す（Phase 1）

**結論：実装に入る前に、エージェントに先に質問させる。**

Bad/Good の対比がわかりやすかったです。

|  | プロンプト | 何が起きるか |
| --- | --- | --- |
| **Bad** | "Create a bill-splitting app for friends for me." | 仕様が曖昧なままエージェントが方向を決め、1時間後に「こんなの頼んでない」となる |
| **Good** | "I'm not sure what my target audience is — can you help me brainstorm different ways I could take this?" | コードを書く前に、エッジケース・対象ユーザー・不明点をエージェントが洗い出してくれる |

Phase 1 の `PROMPT.MD` では `AskUserQuestion` ツールを明示することで、インタビュー形式で仕様を引き出してから spec に落とす流れを作っています。「誰向けか？」「不均等な支払いは？」といった問いが次々と出てきて、頭の中の「なんとなく割り勘アプリ」が具体的な仕様書に変わっていく体験でした。

### ② 読める計画をつくる（Phase 2）

**結論：計画は Markdown ではなく HTML で作る。**

| Markdown（昨日） | HTML（今日） |
| --- | --- |
| `# Plan` `## Scope` `## Open questions` のプレーンな箇条書き | SCOPE / OPEN / FLOW などをカード形式で構造化したビジュアル |

HTML の計画はモデルの思考をより多く捉えられる、というのがポイントです。Phase 2 の `PROMPT.MD` は Phase 1 の仕様を読んで、4つのデザイン方向性をそれぞれ HTML ファイルとして生成します。コードを書く前に**複数の方向性を並べて比較できる**感覚は、1案に縛られがちな従来の開発とはかなり違いました。

### ③ 検証を最初から組み込む（Phase 3）

**結論：検証は後付けするものではなく、設計と同時に考えるもの。**

3つの原則が示されました。

1. **Build for it from the start** — 作りながら検証を考える
2. **Modularize by verifiability** — 独立に検証できる単位でコードを分ける
3. **Verify across the stack** — ユニット / 統合 / ビジュアル / 振る舞いを横断して検証する

Phase 3 は Vite + React の実装済みアプリで、「検証可能なコンポーネント設計」を6つのアイデアで具体化していました。

| # | キーワード | 概要 |
| --- | --- | --- |
| 1 | **DOM が機械可読なサーフェス** | `data-verify-*` 属性でコンポーネントの状態を外部に公開する |
| 2 | **Verifiable Unit** | fixtures（再現可能な状態）と invariants（満たすべき条件）を各コンポーネントが宣言する |
| 3 | **独立したレンダーターゲット** | `/verify/:unit/:fixture` で1ユニットだけをマウントして観察できる |
| 4 | **プラガブルな Verifier** | `schema` / `invariants` / `dom-contract` / `a11y` の4種。コンポーネントを変えずに追加できる |
| 5 | **`window.__verify`** | エージェント向け API。`manifest()` / `current()` / `runAll()` を提供 |
| 6 | **判定は1系統** | PASS / FAIL / BLOCKED / SKIP。ダッシュボード・エージェント・CI が同じコードパスを使う |

`data-verify-*` の発想が特に面白くて、React の `useState` は JS の外から読めないけれど、状態を DOM 属性として書き出してしまえば AI エージェントが `document.querySelector` で取得できる、という話です。内部実装をリファクタしても DOM 属性さえ維持すれば検証が壊れない設計になっています。

リポジトリは `phase-1-exploration`（PROMPT.MD のみ）/ `phase-2-planning`（PROMPT.MD のみ）/ `phase-3-verify`（Vite + React 実装）の3フォルダ構成です。

このセッションの締めの言葉が強く印象に残りました。

> "The work is no longer writing the code. The work is setting up the conditions in which the code gets written well."

![登壇スライド「The work is no longer writing the code. The work is setting up the conditions in which the code gets written well.」](https://static.zenn.studio/user-upload/363b441184a1-20260611.jpg)

「コードを書くこと自体より、コードがうまく書かれる条件を整えることが仕事になってきた」——理屈では分かっていたつもりでも、Phase 1〜3 の流れで手を動かしてみると、実感として腹に落ちてきます。次のセッション以降は、その「条件を整える」がさらに具体的な形で出てきます。

---

## Managed Agents を手で動かす

### Ship your first Managed Agent

「深夜2時に p99 レイテンシが10倍になりました。どうぞ」という架空の緊急シナリオでハンズオンが始まります。渡された `agent.py` には7つの `NotImplementedError` が並んでいて、これを **34行**で埋めるだけ、というシンプルな構成でした。

面白かったのは**実行場所の分離**です。

* **エージェント本体**は Anthropic のクラウドサンドボックスで動く
* **`get_metrics` などのツール**は自分のマシンで実行される
* 両者をイベントストリームが橋渡しし、エージェント側は「処理がどこで走っているか」を意識しない

これの実用的なポイントは、社内システムを外部に公開せずにエージェントから叩けることです。普通はエージェントに社内 API を叩かせようとすると VPN や認証の問題が出てきますが、このモデルだとローカルのツールがアウトバウンドでイベントストリームに繋ぎに行くだけなので、ポート公開が不要になります。

![登壇スライド「The cloud agent calls a function on your laptop」（custom tool を SSE ストリーム経由でローカルの handle_tool が処理。インバウンド通信なし）](https://static.zenn.studio/user-upload/47e7b1cbe651-20260611.jpg)

### Agents that remember

キャッチフレーズは「金魚から同僚へ」。45分のハンズオンです。

最初の数分で「エージェントが何も覚えていない」ことをわざと体感させられる設計がうまかったです。そのうえで、**[Memory Store](https://platform.claude.com/docs/en/managed-agents/memory)** の仕組みが登場します。

![登壇スライド「Three layers（Session / Memory store / Dreaming）」](https://static.zenn.studio/user-upload/570c79ee9546-20260611.jpg)

| 概念 | 内容 |
| --- | --- |
| **Memory Store** | 読み書きできる永続ストレージ。Session 作成時にアタッチする |
| **複数 Session へのアタッチ** | 同じ Store を別 Session に渡すと、会話をまたいで記憶が引き継がれる |
| **記録の仕方を指示できる** | 「何をどう記録するか」をエージェントに指定できる |
| **[Dreaming](https://platform.claude.com/docs/en/managed-agents/dreams)** | 過去の Session ログと Memory Store を入力にバッチ処理し、整理した新しい Memory Store を生成する（リサーチプレビュー） |

「記憶させる」と聞くと実装が重そうに感じますが、実態は **Store をアタッチするだけ**でした（厳密には agent toolset の有効化が要りますし、参照専用にしたい Store は記憶の汚染を避けるため read\_only が推奨されています）。Dreaming は過去ログを遡って整理できるので、後から「あの会話も記憶に入れたかった」という場面に効きそうです。Managed Agents 自体まだベータ／一部リサーチプレビューですが、今後が楽しみな機能でした。

![登壇スライド「How Dreaming works」（Input/Output memory store と Orchestrator・Subagent の構成）](https://static.zenn.studio/user-upload/2d46ffe0fbdd-20260611.jpg)

---

## evals を「先に」書く

### Evals for taste: Hill-climbing a slide-generation agent

「とにかく LLM に任せる」の前に、まず評価（evals）を用意する。今回のイベントを通して一番繰り返し出てきた発想がこれで、専用のセッションもありました。題材は**スライドを生成するエージェント**で、それを評価タスク群（eval）で採点しながら育てていく、という流れです。

最初のスライドで示された「evals が無いとどうなるか／あるとどうなるか」の対比が、まず腹落ちしました。

![evalsセッションのスライド「Why are evals important?（Without evals / With evals）」](https://static.zenn.studio/user-upload/115fd9ff0244-20260611.jpg)

上のスライドの要点を、自分なりに表へ起こすとこうなります。

|  | evals 無し | evals あり |
| --- | --- | --- |
| 状態 | 手探りで反応的なループに陥る | AI システム開発を効率化できる |
| 具体 | 問題が本番でしか見つからない／一つの不具合を直すと別の不具合が出る／本物のフィードバックとノイズを区別できない／改善も劣化も「当てずっぽうで確認」するしかない | 成功の定義を強制的に明確化できる／最適なエージェント構成を反復改善できる／新モデルを素早く採用し、性能・レイテンシ・コスト・エラー率の知見を得られる／ローンチ前に問題を可視化し、一貫した品質基準を保てる |

特に刺さったのが「**成功とはどういう状態か（what does success look like?）を、evals が強制的に言語化させる**」という点です。曖昧なまま作り始めると、後から良し悪しを判断できなくなる——これは前述の「曖昧さを消す（Phase 1）」とも地続きの話でした。

evals は、プロンプト工学のライフサイクルの一部として位置づけられていました。

> Develop eval test cases（評価タスクを作る）→ Write preliminary prompt（暫定プロンプトを書く）→ Run prompt against tasks（タスクに対して実行）→ Refine prompt（改良）→ Ship polished prompt（仕上げて出荷）

![evalsセッションのスライド「Essential part of the prompt engineering lifecycle」](https://static.zenn.studio/user-upload/c5ba2005fe92-20260611.jpg)

ここで「Run ↔ Refine」をぐるぐる回す反復そのものが evals だ、という整理です。**先にタスク（評価）を書いてからプロンプトを書く**順番がポイントで、ゴールの定義を先に固定するから、改良の良し悪しがブレずに測れる、という納得感がありました。

採点役（Grader）の3類型も実務的でした。スライドではこう示され、自分用に表へ整理しておきます。

![evalsセッションのスライド「Graders（Code-based / Model-based / Human graders）」](https://static.zenn.studio/user-upload/6d32ddf4cbf6-20260611.jpg)

| Grader | 手法 | 長所 | 短所 |
| --- | --- | --- | --- |
| **Code-based** | 文字列一致・正規表現・あいまい一致、ユニットテスト（fail-to-pass）、静的解析（lint/type）、最終状態＆ツール呼び出しチェック | 高速・安価・決定論的 | 脆く、ニュアンスに欠ける |
| **Model-based** | ルーブリック採点、ペアワイズ比較、複数審査の合議 | 柔軟・スケーラブル・ニュアンス対応 | 非決定論的・コスト・要キャリブレーション |
| **Human** | SME（専門家）レビュー、クラウドソース判定、スポットチェック抽出、A/B テスト | 柔軟・高品質・ニュアンス対応 | 遅い・高コスト |

「算術はコードに、判断は LLM に」という後述の分業の話とつながりますが、**採点も同じで、決定論的に測れるものは Code-based に寄せ、ニュアンスが要る部分だけ Model-based / Human に回す**——というコスト感覚が腑に落ちました。このあと触る Agent Battle の `--eval` も、結局はこの「先にタスクを書いて高速に回す」発想の実装版だったのだと、後から腑に落ちました。

---

## ツール / Skill / Subagent に分解する

このセッションが個人的には一番刺さりました。テーマは「**育ちすぎたエージェントを、ツール / Skill / Subagent に分解し直す**」という話です。

ハンズオンで触った題材は、毎朝 CSV 数百行の在庫データをチェックしてサプライヤーを選定するエージェントでした。最初の状態はこんな具合です。

* system prompt: **402行**
* ツール数: **12個**
* CSV 全行がまるごと context に入る
* サプライヤー選定は subagent に丸投げして散文で返答

ワークショップで示された計測値は **488秒・102回のツール呼び出し・スコア71%**。正直、なかなかきつい数字です。

セッションを通して繰り返されたメッセージがこれでした。

> "Ranking suppliers is arithmetic, not judgment. Compute it in Python — do not reason about it in prose."

LLM に「考えさせる」べきタスクと、「計算させる」べきタスクは別物だ、という話です。サプライヤーの順位付けは、価格・リードタイム・信頼性に重みをかけて足すだけの算術。それを LLM に文章で推論させていたのが無駄だった——シンプルですが、改めて言語化されると刺さりました。

ワークショップで示された改善前後の数字がこちら。

| 指標 | Before | After |
| --- | --- | --- |
| system prompt | 402行 | 15行 |
| 処理時間 | 488秒 | 約100秒 |
| ツール/スクリプト実行 | 102回（ツール呼び出し） | 3回（スクリプトに集約） |
| スコア | 71% | 92% |

持ち帰った判断軸も整理しておきます。

| 何に任せるか | 適切なタスク |
| --- | --- |
| **コード実行（Python 等）** | 計算・集計・絞り込みなどの算術処理 |
| **Skill（プロンプト）** | ポリシーや知識の参照（必要なときだけ読む） |
| **Subagent** | 独立したゴールを持つ処理だけ |

「subagent が数値を1つ返すだけなら、それは subagent じゃなくていい」という一言も印象的でした。

「これは本当に LLM が考えるべきことか？」を、まず eval のスコアで確かめてから分解していく——という流れを、普段の開発でも当たり前にしていきたいです。

---

## インドネシアの「条文」をクエリ可能にした話

### How I built a legal platform for 280 million people at the Claude Code Hackathon

ワークショップの合間に聞いた登壇のなかで、特に印象に残った話を一つ。

**[Pasal.id](https://pasal.id)**（パサル）はインドネシア語で「条文」を意味します。2億8000万人の国の法令を、誰でも無料で検索・参照できるオープンデータベースを個人がひとりで作った、というプロジェクトでした。

課題感がとにかく明快でした。登壇者によると、インドネシアには1945年から現在まで**30万件以上の法令**があり、各省庁サイトに読みにくい PDF や画像スキャンとして散在しているそうです。フォーマットだけで**21種類**。構造化されていない情報は、探せない・引けない・AI にも聞けない、というわけです。

ここで発表者がきれいに整理してくれたのが「法令を AI に聞く方法の3段階」でした。

| レベル | アプローチ | 問題 |
| --- | --- | --- |
| Bad | モデルに直接聞く | ハルシネーション、知識カットオフ |
| Better | Web 検索 | 非構造化、信頼性にばらつき |
| **Best** | **構造化 DB へのクエリ（MCP）** | ― |

「AI エージェントの時代には、あらゆる情報がクエリ可能でなければならない」という主張はシンプルですが、逆に言えば**クエリできない情報は存在しないのと同じ**、ということでもあります。

開発プロセスでの Claude の使い方も印象的でした。「コードを書かせる」ではなく「**一緒に考える**」パートナーとして使っていて、ハッカソンのルール文書を読ませてブレストし、アーキテクチャを壁打ちし、`TASKS.md` を生成し、ロゴとデザインシステムまで一緒に作ったそうです。この使い方、個人的にもっと真似したいです。

データパイプラインの設計思想も面白かったです。

1. **Scraping** — 公式 PDF をダウンロード
2. **OCR** — 画像スキャンを含む PDF をテキスト化
3. **Parsing** — テキストを法令ツリー（章・条・項・号）に変換。**LLM は使わない決定論的なパーサー**
4. **Verify** — LLM を「Auditor」として使い、パーサー出力を PDF と照合して誤りを修正

印象的だったのは「AI でパーサーを置き換えるのではなく、AI でパーサーを監査する」という設計でした。法令ツリーへの変換そのものは LLM を使わない決定論的なパーサーが担い、LLM は出力を PDF と照合する Auditor 役に回す（精度の土台はコード側）。  
さらに、読者が記事上で誤りを報告すると、エージェントが公式 PDF と照合し、安全な修正は自動適用・それ以外はレビューへ。  
そして修正は1つずつテストケースになり、使われるほどパーサーが育っていく仕組みでした。

最後のスライドに "Japan shares these same challenges" とあって、ちょっとギクッとしました（笑）。日本の法令 PDF も画像スキャンだらけで、e-Gov はあるけれどエージェントがクエリしやすい形かというと正直微妙です。インドネシアで個人がひとりでやりきったのなら、日本でもできるはず——「やってみたいな」と素直に思いました。

![登壇スライド「What software does your country not have yet?」](https://static.zenn.studio/user-upload/5231456ca896-20260611.jpg)

---

## Agent Battle

### Agent Battle: Mine the most diamonds in 45 minutes

最後は Minecraft でダイヤモンドの採掘数を競う Agent Battle（教材は [anthropics/cwc-workshops](https://github.com/anthropics/cwc-workshops) の `agent-battle`）。コードを書くのではなく、`my_agent.py` の4つのノブ（`model` / `system` / `skills` / `mcp_servers`）をどう設定するかが競技の本質でした。

![登壇スライド「Your whole agent is a dict. Four levers（system / model / skills / mcp_servers）」](https://static.zenn.studio/user-upload/3c5a82664b2e-20260611.jpg)

アーキテクチャは Ship your first Managed Agent と同じ発想で、ローカルの [Mineflayer](https://github.com/PrismarineJS/mineflayer) ボットがクラウドの Claude へアウトバウンドで繋ぎに行くため、ポート公開は不要です。

![登壇スライド「The harness」（Anthropic cloud の Claude agent と、ローカルの mineflayer ボット／vanilla MC を MCP トンネルで接続）](https://static.zenn.studio/user-upload/fd8a433af594-20260611.jpg)

ここでも効いたのが eval でした。競技の前に `--eval` で、ダイヤ採掘の典型シーンに対するエージェントの判断を採点できます。system プロンプト空のままで **7/10**。Claude はもともと Minecraft の知識を持っているので、何も書かなくても7割は当ててしまいます。残り3問（鉄ツルハシに持ち替える／掘り尽くしたら移動する／tuff は無視する）が system に書くべきヒントでした。eval は **30〜60秒**・数円以下で回せるので、仮説を安く何度も試せます。

本番ランには API トークンが必要でしたが、会場で配られたトークンが手元に届くのが間に合わず、今回は eval を詰めるところまで。本番ランは次回へ持ち越しです。

---

## まとめ

振り返ると、今回持ち帰ったのは「**明確な Goal と Eval でエージェントを動かす**」という一点に尽きます。成功の定義（Goal）を先に決め、Eval で測りながら回す——どのセッションも、突き詰めればこの話に行き着きました。

* **まず曖昧さを詰めて、ゴールを固める**（How we Claude Code）: 実装に入る前にエージェントへ質問させ、仕様を言語化してから動かす。「コードを書くより、うまく書かれる条件を整える」という発想がここに詰まっていました。
* **Eval で測りながら回す**: 「成功とはどういう状態か」を先に Eval で定義し、改良も分解も Eval のスコアで確かめてから進める。算術はコードに、判断だけ LLM に。488秒→100秒・71%→92% の差が、その効きを物語っていました。

登壇よりワークショップ中心で回ったからこそ、この一本が腹に落ちました。また次の機会にも参加したいです。
