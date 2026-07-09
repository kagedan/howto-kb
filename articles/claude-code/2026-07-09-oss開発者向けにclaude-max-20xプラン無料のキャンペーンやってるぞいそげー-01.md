---
id: "2026-07-09-oss開発者向けにclaude-max-20xプラン無料のキャンペーンやってるぞいそげー-01"
title: "OSS開発者向けにClaude Max 20xプラン無料のキャンペーンやってるぞ、いそげー"
url: "https://zenn.dev/tai_kimura/articles/a129c0b6f0e4b8"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "Python", "zenn"]
date_published: "2026-07-09"
date_collected: "2026-07-10"
summary_by: "auto-rss"
query: ""
---

## 結論から：OSS 開発者なら Claude Max 20x が6ヶ月タダになるかもしれん

Anthropic が **「Claude for Open Source」** というプログラムをやっていて、対象の OSS 開発者に **Claude Max 20x を6ヶ月間無料** で提供している。2026年7月に対象が拡大された。

Max 20x は Claude の一番上のプランで、Claude Code をゴリゴリ回す人間にとっては普通に効く。しかも応募は**フォームを数分埋めるだけ**。落ちても失うのは数分。やらない理由がない。

というわけでこの記事は「こんなキャンペーンやってるぞ」＋「実際にこう応募したぞ」のログです。

---

## もらえるもの

* **Claude Max 20x を6ヶ月間、無料**
* 6ヶ月後は元のプラン(有料なら元のレート、無料なら無料プラン)に戻るだけ。**期限前にメール通知が来る**ので、気づかないうちに高額課金される罠は無い。

---

## 応募資格（5カテゴリのいずれか1つ）

公式ページに載っている基準はこの5つ。**どれか1つ**満たせばよい。

1. **Maintainers / Library Authors**  
   依存リポジトリ 500以上 / 依存パッケージ 100以上 / 全レジストリ合算で月間ダウンロード 20万以上
2. **Core Contributors**  
   著名財団の登録コミッター・メンテナ（CPython, Rust team, Node.js TSC, Apache PMC, CNCF, Kubernetes, Linux kernel, Django, Rails など）
3. **Active Contributors**  
   過去12ヶ月で、**自分が所有しないリポ**に 100件以上の PR をマージ
4. **Community Builders**  
   過去12ヶ月で、管理リポに **20人以上の外部コントリビュータ**からの merged PR
5. **Critical Infrastructure**  
   OpenSSF の **Criticality Score が 0.4 以上**

見ての通り、1・4・5 は「利用規模」、2 は「大御所財団所属」の指標。**個人のニッチな OSS だとハード基準はだいたい刺さらない。** 現実的に個人開発者が届きうるのは 3（自分の年間 PR 活動）くらい。

### でも諦めるな：裁量レーンがある

公式ページにはこう書いてある。

> applicants who don't fit exact criteria to apply anyway and explain their ecosystem contribution  
> （基準に完全一致しなくても、エコシステムへの貢献を説明して応募することを推奨）

つまり **「数字は満たしてないけど、こういう貢献をしている」を説明して出す正規ルート**が用意されている。ニッチ OSS 勢はここで勝負する。

---

## 実際に応募してみた（JsonUI の場合）

自分は **JsonUI**（ドキュメント: <https://jsonui.tanosys.com/> ）という OSS を8年以上・12リポで単独メンテしている。「JSON で UI を一度定義すれば iOS / Android でネイティブ描画され、Web は CLI が React を生成する」宣言的クロスプラットフォーム UI フレームワークだ。

正直、利用者は多くない。ハード基準はどれも厳しい。なので**裁量レーン**で出した。

### フォームの構成

応募フォームはこんな感じ（2026年7月時点）。

1. **Select a repository you've contributed to** — 貢献したリポを選ぶプルダウン（自分は `jsonui-cli` を選択）
2. **Tell us about the project's reach and impact**（必須） — reach / impact / エコシステムで埋めるギャップを書く
3. **How will you use the subscription for your project?**（必須） — サブスクをどう使うか
4. **Other info**（任意）

以下、実際に書いた文面（英語フォームなので英語）。丸パクリ推奨ではなく「こういう温度感で書けばいい」の参考に。

### ① reach and impact に書いたこと

> `jsonui-cli` is the single-source-of-truth toolchain at the center of **JsonUI**, an open-source ecosystem for declarative, cross-platform **native** UI — define a screen once in JSON and render it natively on iOS and Android, with a React/Next.js + Tailwind web build generated directly by jsonui-cli itself. I've maintained it as the sole author for **8+ years across 12 public repositories**: the platform renderers (SwiftJsonUI for UIKit/SwiftUI, KotlinJsonUI for Jetpack Compose), the web code generation built into this CLI, an MCP server, and a cross-platform test runner.
>
> The gap it fills: unlike React Native or Flutter, JsonUI does **not** replace each platform's native UI layer — it keeps UIKit/SwiftUI and Jetpack Compose as the real rendering targets and generates idiomatic React for the web, sharing only one declarative spec plus per-platform code generation. `jsonui-cli` is what makes that viable — one attribute definition drives codegen for all three targets with build/verify gates and schema-drift guards so the outputs never diverge.
>
> Adoption is deliberately niche rather than mass-market, so I'm applying through the ecosystem-contribution path. What I'd point to instead of download counts is the **scope and 8-year continuity**: a single maintainer keeping genuine iOS/Android/web parity, its SSoT codegen, its cross-platform test runner, and its AI/MCP tooling all in sync and actively developed.

ポイント:

* **DL数で殴れないので、殴らない。** 代わりに「8年の継続」「12リポ」「1人で全部同期して維持」という**規模と継続性**を前に出す。
* **埋めるギャップを明確に。** RN/Flutter と何が違うのか（ネイティブ層を置き換えず、宣言スペック＋コード生成だけを共有）を1文で言い切る。
* **裁量レーンで出すことを正直に書く。**「mass-market じゃない、だからこのルートで応募する」と自分から言う。

### ② How will you use に書いたこと

> Claude is already central to how I develop JsonUI, and Max 20x would let me scale that up substantially.
>
> Concretely, I use Claude Code daily to: (1) keep code generation at parity across three targets — when I add one attribute, the Swift and Kotlin renderers and the web codegen inside jsonui-cli must all stay coherent, and I use Claude to thread changes through every emitter and catch schema drift; (2) run multi-agent design reviews before landing changes — fanning out several agents to verify a plan against the actual codebase from different angles; and (3) build and test the JSON test-runner across iOS, Android, and web.
>
> I've also built **jsonui-mcp-server**, a Model Context Protocol server that exposes the spec, layout, and codegen tools to AI agents, plus a full Claude Code agent workflow around the toolchain — so JsonUI is not just built *with* Claude, it's being made **AI-native** as a framework. Max 20x's higher throughput directly enables the parallel multi-agent workflows this cross-platform work depends on, letting me keep all three targets and their tooling moving forward faster.

ポイント:

* **「なぜ Max 20x が必要か」を具体タスクで語る。** 抽象的な「開発が捗る」ではなく、(1) 3ターゲットのコード生成整合、(2) 多エージェント設計レビュー、(3) クロスプラットフォームテスト、と手を動かしている作業で書く。
* **Anthropic に刺さる角度を混ぜる。** 自分は MCP サーバー（jsonui-mcp-server）と Claude Code エージェントワークフローを自作してツールチェーンに組み込んでいる。「Claude で作る」だけでなく「AI ネイティブなフレームワークにしている」という点は、この審査ではかなり効くはず。

### ③ Other info（任意だが入れた）

> Repos: SwiftJsonUI, KotlinJsonUI, jsonui-cli (also generates the web/React build), jsonui-mcp-server, jsonui-test-runner (+ platform test-runner variants) and their docs — 12 public repositories, all under active single-maintainer development for 8+ years. jsonui-mcp-server integrates the toolchain directly with Claude via MCP, so this project is both built with Claude and building for the AI-agent workflow.

リポ一覧を並べて「12リポ・8年・単独」の**実体を数えられる形**で提示。

---

## 応募のコツ（ニッチ OSS 勢向け）

1. **ハード基準を1つでも満たすなら、それで出す。** 特にカテゴリ3（他リポへの年100 PR）は「プロジェクトの人気」ではなく「あなた個人の活動」なので、貢献者タイプの人は狙い目。
2. **満たさないなら裁量レーンで、正直に。** 見栄を張って盛るより、「ニッチだが8年こういう貢献をしている」と等身大で書く方が通りやすい（と思う）。
3. **DL数が弱いなら、規模・継続性・埋めるギャップで代替する。** 数字の勝負に乗らない。
4. **「サブスクの使い道」は具体作業で。** できれば Claude / MCP / エージェントを使っている実例を出す。
5. **急げ。** 期限は明記されていないが、この手のキャンペーンはいつ締まるか分からない。

---

## まとめ

* Anthropic が **OSS 開発者向けに Claude Max 20x を6ヶ月無料**にするキャンペーンをやっている
* ハード基準は5カテゴリ、**どれか1つ**でOK
* 満たさなくても **「エコシステム貢献を説明して応募」する裁量レーン**がある
* 応募コストは数分、ダウンサイドはほぼゼロ
* **ニッチ OSS でも、規模・継続性・ギャップ・AI活用の実体を正直に書けば勝負になる**

該当しそうな人は、とりあえず出しておこう。いそげー。
