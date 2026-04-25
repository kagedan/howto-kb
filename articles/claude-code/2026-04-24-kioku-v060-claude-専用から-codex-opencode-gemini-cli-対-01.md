---
id: "2026-04-24-kioku-v060-claude-専用から-codex-opencode-gemini-cli-対-01"
title: "KIOKU v0.6.0 — Claude 専用から Codex / OpenCode / Gemini CLI 対応へ (marketpl"
url: "https://zenn.dev/megaphone_tokyo/articles/5fd0f1c793d8d7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-04-24"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/1a6f0d43e2a0-20260424.jpg)

## はじめに

Claude Code / Desktop の記憶 OSS「KIOKU」を作っています。前回の [v0.5.0 + v0.5.1 同日リリース](https://zenn.dev/megaphone_tokyo/articles/14fc62642f8d1c) は「外部の知識を取り込む (ingest) → 取り込んだ知識を session 間で持続させる (persist)」という **内側の基盤** を揃えるリリースでした。

今日 (2026-04-24) 出した **v0.6.0** は、そこから **外側に開く** release です。一番大きいのはこれ:

> **Claude 専用だった KIOKU が、Codex CLI / OpenCode / Gemini CLI でも同じ skill で動くようになりました。**  
> vault は 1 つ持てば、どの AI agent でも second brain として使えます。

これに加えて、3 つの変化と 1 つの policy 形式化も入っています:

* 🔀 **マルチエージェント対応 (本記事の主役)** — Claude / Codex CLI / OpenCode / Gemini CLI の 4 agent で vault を共有
* 📦 **Claude Code plugin marketplace** に正式登録 — ワンコマンド install
* 📊 **Obsidian Bases 9 view ダッシュボード** — 蓄積された知識の可視化 (初の UI layer)
* 🔁 **Raw Markdown の delta tracking** — 変更ない日は LLM を呼ばない (sha256 ベース)
* 🛡 **セキュリティ policy の形式化** — CVE 分類 + Safe Harbor + 90 日 Coordinated Disclosure

全部通底するのは「**1 人 dogfooding を超えて、他の人が入ってこれる口を開ける**」。今回は multi-agent 対応をじっくり書いた後に、それぞれの変化と設計で迷ったところを書きます。

<https://github.com/megaphone-tokyo/kioku>

## 1. マルチエージェント対応 — Claude 専用から 4 AI agent 対応へ

v0.6.0 で一番大きな方針転換です。KIOKU の skill 層を **Claude Code 固有の拡張から外して**、以下すべてで同じ skill が動くようにしました:

| AI agent | 状態 |
| --- | --- |
| **Claude Code** | 既存 (これまで通り) |
| **Codex CLI** (OpenAI) | ✅ 新規対応 |
| **OpenCode** (OSS) | ✅ 新規対応 |
| **Gemini CLI** (Google) | ✅ 新規対応 |

セットアップは 1 コマンドです。

```
bash scripts/setup-multi-agent.sh
# → ~/.codex/skills/kioku/
# → ~/.opencode/skills/kioku/
# → ~/.gemini/skills/kioku/
# に symlink が配置され、各 agent から KIOKU の skill / MCP tool が呼べるようになる
```

### Before / After

**Before (v0.5 まで)**:

```
[Claude Code] → KIOKU skills → MCP → Vault (second brain)

[Codex CLI / OpenCode / Gemini CLI] → ❌ (skills 届かない)
```

vault 自体は Obsidian 上の Markdown ファイル群なので、他 agent からファイルを開くこと自体はできる。でも KIOKU の「自動で蓄積する・検索する・構造化する」機能は Claude Code に結びついていた。

**After (v0.6.0)**:

```
              ┌── Claude Code ──┐
              ├── Codex CLI ────┤
[あなた] ──→ ┤                 ├──→ KIOKU skills + MCP → Vault (同じ second brain)
              ├── OpenCode ─────┤
              └── Gemini CLI ───┘
```

どの agent でも vault ファイル自体は共有される。**自動で記憶を蓄積する層 (hot cache 注入 + session log)** は v0.6 では Claude Code 専用、v0.7 で 4 agent 対応に拡張予定。

### なぜ技術的にこれが可能だったか

素直に言うと、**KIOKU を Claude 専用にしておく合理的な理由が最初から無かった** んです。

v0.5 時点で KIOKU の skill 層は `name` + `description` の frontmatter と Markdown 本文で成立していて、Claude 固有拡張 (`maxTurns` / `allowedTools` 等) はほぼ使っていませんでした。core extractor は Node stdlib + Bash、MCP サーバーは `@modelcontextprotocol/sdk` のみ依存 (stdio protocol) で、どちらも特定 agent に縛られていない。

v0.6.0 でやったのは:

1. skill frontmatter から Claude 固有の拡張を除去 (or コメント化)
2. agent 別の skill 配置先にある差異を吸収する `setup-multi-agent.sh` の追加
3. README 10 言語に multi-agent 対応の install 手順を記載

つまり、**「vendor lock-in を積極的に作っていなかった」のが、数 h の整理で cross-platform 化できた理由** です。

### 3 persona 別のメリット

**(1) AI agent lock-in を嫌う開発者**

「今は Claude を使ってるけど、半年後に他の agent に乗り換えるかもしれない」という慎重な user に対して、**記憶の資産だけは agent から独立している** と言えるようになりました。vault は Obsidian Markdown なので、KIOKU を使わなくなっても second brain として残ります。

**(2) Agent を横断して使う開発者**

特定の task (コード生成の比較、複数の視点が欲しい時) で別 agent も触る people 向け。これまでは「vault は 1 個あるけど、agent を跨ぐと skill が動かない」という摩擦がありました。v0.6 以降は **どの agent でも vault ファイル自体は共有される**。**自動で記憶を蓄積する層 (hot cache 注入 + session log)** は v0.6 では Claude Code 専用、v0.7 で 4 agent 対応に拡張予定。

**(3) Comparison / 評価で複数 agent を回す人**

Codex / Gemini / Claude を task ごとに使い分けたい研究者 / プロンプトエンジニア層。同じ vault を 4 agent で共有できる = **agent 間の性能比較のメタ context が 1 箇所に集約** される、という使い方ができます。

### 個人的な動機

私は Claude Code を main で使いつつ、特定の task (コード生成の比較、長文要約の cross-check) で Codex や Gemini も触ることがあります。

vault は 1 個あれば十分なのに、agent を跨ぐと skill が動かない、というのは自分の UX としても摩擦でした。**自分が欲しい形 (1 つの vault + どの agent でも引き継げる second brain)** を目指したら、副次的にマーケ的にも「lock-in 回避」として訴求できる形になった、という順番です。

### 設計で避けたこと

agent ごとに fork を作る pattern (agent A 用リポ + agent B 用リポ + ...) は採用しませんでした。保守 4 倍 + bug fix の同期問題 + version drift、どれを考えても非現実的です。

v0.6.0 の approach は「**1 つの skill 定義を symlink で 4 箇所に配る**」。core logic は master に 1 つだけ、agent 別の差異は setup script が吸収する。将来 5 番目、6 番目の agent が出てきても symlink 先を足すだけで対応できる設計です。

### 公式 site のデモ (v0.7 予定)

Visualizer + v0.7 Hook port 後は「4 agent が同じ vault に並列でメモを追加し、その成長を Timeline Player で追える」デモが可能になります。v0.7 release で Hook port (automatic session log + hot cache を Gemini / Codex にも対応) が揃うと、multi-agent narrative が真価を出す予定です。

## 2. Claude Code plugin marketplace に登録

これまで KIOKU のインストールは `.mcpb` ファイルを GitHub Releases からダウンロードして Claude Desktop にドラッグ & ドロップ、という独自経路でした。v0.6.0 で **Claude Code の公式 plugin 流通経路** に載せました。

```
# marketplace 登録
claude marketplace add megaphone-tokyo/kioku

# install
claude plugin install kioku@megaphone-tokyo
```

2 コマンドで終わります。`.mcpb` 配布は MCPB エコシステム向けに **並行して維持** しているので、Claude Desktop 限定ユーザーは引き続き drag & drop でも install できます。

### 意図

独自配布は「作者が用意した install 手順に user が合わせてくれる」状態で、それが可能なのは user と作者の間に十分な信頼がある時だけ。v0.6 の現在地で言うと、KIOKU を発見した user が独自 `.mcpb` workflow に付き合ってくれるとは限らない。marketplace 登録で **他の plugin と同じ install 体験** にそろえる、というのが動機でした。

## 3. Obsidian Bases 9 view ダッシュボード

v0.5 時点では、蓄積された Wiki を眺めるには Obsidian の file explorer か Graph View (Cmd+G) を手動で使うしかありませんでした。v0.6 では [Obsidian 1.9+ の Bases 機能](https://help.obsidian.md/bases) を使って **`wiki/meta/dashboard.base` という 1 ファイル** を開くと、9 つの動的 view が並ぶ dashboard になります。

| View | 目的 |
| --- | --- |
| Hot Cache | 直近の短期記憶 (v0.5.1 で導入した `wiki/hot.md`) |
| Active Projects | `status: active` の project ページ |
| Recent Activity | 全 wiki、更新順 |
| Concepts | `type: concept` のページ |
| Design Decisions | `type: decision` のページ |
| Analyses | `type: analysis` のページ |
| Patterns | 繰り返し出てくるパターン集 |
| Bugs | 記録された bug / debug memo |
| Stale Pages | 30 日以上更新なしのページ (掃除候補) |

`wiki/` 配下のファイルに frontmatter を入れておくと、Bases が自動で分類して動的 table にします。ユーザーが手で `status` を変えれば dashboard の表示も即座に更新される。

### 意図

KIOKU は今まで「裏で静かに wiki を育てる」ツールで、**可視化の UI が存在しない** のが最大の weakness でした。Graph View は Obsidian の汎用機能で KIOKU 固有のものではないし、user が「KIOKU が何を蓄積してくれたか」を体感できる瞬間が無かった。

Bases dashboard は **「KIOKU が蓄積したものが可視化される」初体験** です。ここから「もっと見たい」と思ってくれる user が出てくるかどうかは、これから観察します。

実装自体は `templates/wiki/meta/dashboard.base` の template 配置 + `setup-vault.sh` の冪等配置で、新規 user は自動で dashboard が入ります。既存 user は手動で `bash scripts/setup-vault.sh` を再実行すると dashboard.base が配置されます。

## 4. Raw Markdown の delta tracking (sha256 ベース)

これまで KIOKU の auto-ingest cron は、`raw-sources/` 配下のファイルを **毎日同じ内容で再要約** していました。user が書いた note を頻繁に手で編集している場合、**「同じ内容を何度も LLM に送る」** という浪費があった。v0.6 ではここに sha256 ベースの delta tracking を入れました。

### 仕組み

* `raw-sources/articles/my-note.md` の sha256 を `.raw-manifest.json` に記録
* auto-ingest 実行時、**前回と同じ sha256 なら LLM を呼ばずに skip**
* 内容が変わったら sha256 が変わるので、その時だけ LLM 呼び出し

sha256 の計算は Node stdlib (`crypto.createHash`) で済み、追加依存なし。

### 効果

自分で運用している範囲で測ると、`raw-sources/articles/` を 38 ファイル抱えた vault で、毎朝の auto-ingest が触る LLM 呼び出しが **3-5 回/日 → 0-1 回/日** に落ちました。API コストも、早朝の実行時間も、ほぼゼロに近づく。

### なぜ v0.6 に入れたか

v0.5 で EPUB / DOCX を追加して ingest source の種類が増えたので、今後 RSS など足していった時に「毎日走るジョブが何回 LLM を叩くか」が無視できなくなる前に **仕組みとして入れておきたかった**、というのが動機です。v0.5 までは「自分 1 人なら気にならない」レベルでしたが、外部 user が使うなら API cost の footprint は設計事項として扱うべきです。

## 5. セキュリティ policy の形式化 (Safe Harbor + 90 日 disclosure)

v0.5 までの KIOKU は「**実装としては Hardened (8 層防御 / 14 VULN 全解消 / applyMasks / child-env allowlist 等)** だけど、**policy として何も書いていない**」状態でした。v0.6 でここを埋めました。

### 追加した 4 項目

1. **CVE 分類表** — Critical / High / Medium / Low / Info それぞれに応答 SLA (対応期限) を明文化
2. **Safe Harbor 条項** — 善意のセキュリティ研究者を法的責任から保護する一文
3. **Coordinated Disclosure Timeline** — 90 日 ルール (発見 → 非公開 patch → 90 日後に公開)
4. **Out of Scope 定義** — 対象外の脆弱性クラス (social engineering / physical access / dev dependency 等) を明示

### なぜこれが必要だったか

Phase C-5 で外部 user を迎え入れる (LP β + Discord soft launch) と同時に、**「もし脆弱性を見つけたらどこに連絡すればいいのか」** が現状の README / SECURITY.md には整理されていなかった。Safe Harbor と 90-day disclosure は研究者に対する最低限の礼儀で、これが無いと責任ある発見者が萎縮する (= 脆弱性が公開先行で晒されるリスクが増える) 構造になる。

### Hardened positioning の言語化

マーケ的に言うと「Hardened LLM Wiki for Professionals」という positioning の **Hardened 部分が policy として裏付けられた** のが大きい。これまでは実装レベルでの「8 層防御 / MASK\_RULES / applyMasks」を挙げて Hardened だと主張していたが、policy が無い状態では研究者や法務部門から見ると「とりあえず名乗ってるだけ」に見えても仕方なかった。CVE 分類 + Safe Harbor + 90 日 disclosure は、**Hardened を名乗る上での最低限の policy セット** です。

## 何が入らなかったか (v0.7 以降)

* **Visualizer HTML UI** — 内部基盤は v0.6 で入れた (user には見えない形で)、v0.7 で Timeline Player (wiki の成長を animation で再生) と Diff Viewer (2 時点の wiki 比較) を出す予定
* **Hook port (v0.6 multi-agent の second phase)** — 自動 session log + hot cache 注入を Gemini / Codex にも port、Claude Code と同等の automation layer に揃える。Visualizer と並ぶ v0.7 の柱
* **LP β narrative** — 制作中
* **Discord soft launch** — release 後数日内に開く
* **SECURITY.ja.md の残 3 section 翻訳** — 現状は英語原典のみ、v0.7 までに埋める

**Visualizer が外に見えるのは v0.7** ですが、基盤は v0.6 で用意済みです。v0.7 で出てくる Timeline Player は「**Obsidian の Graph View にない、時間軸で見る Wiki**」が見せどころで、Wiki の成長を映像化する唯一のツール、という narrative の基礎になる予定です。

## テスト / Lint

* Node / Bash の全 suite green
* `npm audit` で runtime deps の 0 vulnerabilities 継続
* plugin marketplace 登録に合わせて `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` を追加、新規テスト suite で metadata 整合性を pin
* multi-agent symlink 配置の冪等性テスト (二重実行しても symlink が壊れない)
* delta tracking の sha256 テスト (変更時は再 ingest、未変更時は skip の 2 ケース)

詳細は [v0.6.0 Release Notes](https://github.com/megaphone-tokyo/kioku/releases/tag/v0.6.0) にまとまっています。

## インストール (新規 / v0.5 からの upgrade)

### 新規

```
# Method A: Claude Code plugin marketplace (推奨)
claude marketplace add megaphone-tokyo/kioku
claude plugin install kioku@megaphone-tokyo

# Method B: .mcpb (Claude Desktop 中心ユーザー)
# Releases から kioku-wiki-0.6.0.mcpb (約 9.2 MB) をダウンロードして drag & drop
```

### v0.5 からの upgrade

```
# 既存 clone で
git pull origin main
bash scripts/setup-vault.sh  # dashboard.base が冪等配置される
bash scripts/setup-multi-agent.sh  # 任意、multi-agent 配布したい場合
```

### マルチ agent で使う場合

```
bash scripts/setup-multi-agent.sh
# → ~/.codex/skills/kioku/ / ~/.opencode/skills/kioku/ / ~/.gemini/skills/kioku/
```

## v0.7 以降に向けて

v0.6 で「外に開く口」を作ったので、次は **外に開いた結果を受ける** フェーズです。

* **Visualizer UI (Timeline + Diff Viewer)** — v0.7 α で visible 化
* **Hook port** — automatic session log + hot cache 注入を Gemini / Codex にも port、v0.6 multi-agent の second phase
* **LP β 公開** — note.com ベースで narrative を整理
* **Discord soft launch** — 日本語 channel 先行、英語は後追い
* **外部 user からの feedback loop** — edge case が増える見込み、handoff/open-issues.md で triage

1 人で作って 1 人で使う dogfooding モードは v0.5 までの話で、v0.6 以降は「他の人に触ってもらって発見してもらう」サイクルに入ります。

## まとめ

* **v0.6.0**: Claude 専用ツールから、マルチエージェント対応 + 外に開くエコシステムへ
* 🔀 **マルチエージェント対応 (主役)** — Claude / Codex CLI / OpenCode / Gemini CLI の 4 AI agent で同じ vault を共有
* 📦 **Claude Code plugin marketplace 登録** — `claude marketplace add` で 2 コマンド install
* 📊 **Obsidian Bases 9 view dashboard** — 蓄積された Wiki の初の可視化 UI layer
* 🔁 **Raw Markdown delta tracking** — sha256 ベースで変更ない日は LLM skip
* 🛡 **セキュリティ policy 形式化** — CVE 分類 + Safe Harbor + 90 日 Coordinated Disclosure で Hardened を policy 裏付け
* MIT License、フィードバック歓迎です

<https://github.com/megaphone-tokyo/kioku>

## 他のプロダクト

季節の写真を集めたギャラリーサイトです。作者が撮影した四季折々の写真を眺められるだけでなく、**自分の画像と季節の写真を AI で合成する**機能もあります。

写真が好きで、AI で遊ぶのも好き、という個人的な興味から作りました。

---

**作者**: [@megaphone\_tokyo](https://x.com/megaphone_tokyo)  
コードと AI で何かつくる人 / フリーランスエンジニア 10 年目 / 東京
