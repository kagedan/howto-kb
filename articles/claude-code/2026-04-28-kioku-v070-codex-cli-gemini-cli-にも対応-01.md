---
id: "2026-04-28-kioku-v070-codex-cli-gemini-cli-にも対応-01"
title: "KIOKU v0.7.0 — Codex CLI / Gemini CLI にも対応"
url: "https://zenn.dev/megaphone_tokyo/articles/346a091cc9b8a6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-28"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/4d469a470301-20260428.jpg)

## はじめに

Claude Code / Desktop の記憶 OSS「KIOKU」を作っています。前回の [v0.6.0 リリース記事](https://zenn.dev/megaphone_tokyo/articles/5fd0f1c793d8d7) では、Claude 専用だった KIOKU を Codex CLI / OpenCode / Gemini CLI でも使えるようにした、と書きました。

ただ、あの v0.6 で **マルチエージェント対応** と打ち出した時点では、実は「**スキルが共有されただけ**」でした。Claude / Codex / Gemini のどこから vault を触ってもスキル (`/wiki-ingest` など) は呼べる。でも **自動セッションログ (= 会話していると勝手に `session-logs/` に記録されるパイプライン)** は Claude Code 専用のままで、Gemini で何時間会話しても vault に何も記録されない、という隔たりがありました。

今日 (2026-04-28) 出した **v0.7.0** で、この隔たりを埋めました。

> **v0.6 でスキルが共有された second brain、v0.7 で記憶も共有される。**

具体的には:

* 🔀 **マルチエージェントの自動セッションログ (本記事の主役)** — Gemini CLI / Codex CLI で起動した会話が自動で `session-logs/` に記録される
* 📚 **マルチエージェント MCP セットアップ手順書** — Codex / Gemini / OpenCode への導入手順を 3 エージェント分公式化 (英語 + 日本語)
* 🎬 **Visualizer α (`kioku_generate_viz` MCP tool)** — Wiki の成長を時間軸で見る、最初の HTML 出力
* ✅ **`verify-multi-agent-e2e.sh`** — 導入後の 6 ステップ対話式の動作確認スクリプト

セキュリティ実装もエージェント境界まで及ぶように手を入れました (後述)。

<https://github.com/megaphone-tokyo/kioku>

## 1. マルチエージェントの自動セッションログ — Hook の移植

### v0.6 の時点で残っていたもの

v0.6 で配布した `setup-multi-agent.sh` は、KIOKU のスキルディレクトリを各エージェントのスキル配置場所にシンボリックリンクで貼る手順でした:

```
~/.codex/skills/kioku/  → KIOKU/skills/
~/.gemini/skills/kioku/ → KIOKU/skills/
~/.opencode/skills/kioku/ → KIOKU/skills/
```

これで `/wiki-ingest` などのスキルは Codex / Gemini / OpenCode から呼べるようになりました。**でもそれだけ**。

KIOKU の本体機能の 1 つは「会話している間、勝手に `session-logs/` に Markdown が積まれていく」というものです。これは Claude Code の Hook システム (`UserPromptSubmit` / `Stop` / `PostToolUse` / `SessionEnd` イベント) を捕捉する `hooks/session-logger.mjs` という Node スクリプトで実現していました。**この Hook 機構が Claude Code 固有**で、Gemini や Codex の Hook システムに対応していなかった。

つまり v0.6 までの実態は:

```
[Claude Code]   → Hook 発火 → session-logger → session-logs/ に記録される
[Gemini CLI]    → Hook 発火しない → 何も記録されない
[Codex CLI]     → Hook 発火しない → 何も記録されない
```

スキルは呼べる、でも自動記憶は走らない、という中途半端な状態でした。マーケ narrative としても、ユーザーの期待としても、ここが詰めきれていなかった。

### v0.7 でやったこと: 591 行のモノリシックなスクリプトを core + 3 adapter に refactor

`hooks/session-logger.mjs` は v0.6 時点で 591 行あるモノリシックな Node スクリプトでした。Claude Code の Hook イベントスキーマ (`{event, prompt, tool_use, transcript_path, ...}`) を直接受け取って解析 → マスキング → frontmatter 生成 → ファイル書き込み、という処理が一本化されていた。

これを v0.7 で **core + 3 adapter** 構造にリファクタしました:

```
hooks/
├── session-logger.mjs         (core: エージェント非依存、NormalizedEvent を受けて処理)
├── adapters/
│   ├── claude.mjs             (Claude Code の Hook 入出力スキーマを正規化)
│   ├── gemini.mjs             (Gemini CLI の Hook スキーマを正規化)
│   └── codex.mjs              (Codex CLI の Hook スキーマを正規化)
└── _common.mjs                (safeMain — exit-0 契約、共通ヘルパー)
```

各アダプターがエージェント固有の Hook 入力を **NormalizedEvent** という共通型に変換し、core 側はそれだけを見る。マスキングのパイプライン (API キー / トークンの伏字化)、frontmatter 生成、`session-logs/` 配置先の決定はすべて core に集約。

### 導入

```
# Gemini CLI 用の Hook を導入
bash scripts/install-hooks-gemini.sh --apply

# Codex CLI 用も同様
bash scripts/install-hooks-codex.sh --apply

# 以降、gemini や codex を起動して会話すると
# $OBSIDIAN_VAULT/session-logs/ に Claude と同じ形式で記録される
```

`--apply` は jq による設定ファイルの冪等マージで、既存の Hook 設定を壊さずに追記する仕組みです。`--probe` で差分確認だけもできる。

### Before / After

**Before (v0.6)**:

```
[Claude Code] → 自動セッションログ ✅
[Gemini CLI]  → 自動セッションログ ❌ (スキルは呼べる)
[Codex CLI]   → 自動セッションログ ❌ (スキルは呼べる)
```

**After (v0.7)**:

```
[Claude Code] → 自動セッションログ ✅
[Gemini CLI]  → 自動セッションログ ✅
[Codex CLI]   → 自動セッションログ ✅
```

vault に対して、**どのエージェントから会話しても等しく second brain が育つ**状態になりました。

### 設計判断: 3 つの hardening

リファクタで意識したのは、エージェントの CLI が KIOKU の Hook 経路で死なないこと、マスキングがエージェント越境で抜けないこと、攻撃者がアダプターを突破しても core で止まること。3 つ書きます。

**(a) safeMain — exit-0 契約**

`_common.mjs` の `safeMain` 関数が全アダプターを wrap しています。中で何が throw しても、最後は `process.exit(0)` する。理由は **エージェントの CLI を絶対にクラッシュさせない** ため。

KIOKU の Hook が throw すれば、それを起動した Claude / Gemini / Codex 自身が Hook 失敗と扱って異常終了する可能性がある。second brain ツールが本体 CLI を巻き添えで落とすのは最悪の失敗モードなので、KIOKU 側の例外は **KIOKU 側だけで吸収する** 契約にした。

代わりにエラーは `session-logs/.kioku-errors.log` に書き込んで、ユーザーが後で気づける構造にしてあります。

**(b) マスキングのパイプラインは core に集約**

API キー / トークン / Bearer トークン / PEM 等の伏字化は `applyMasks()` という関数 1 本に集約され、core 側で必ず通ります。アダプターは NormalizedEvent を作るだけで、マスキングは通せない。**アダプターを迂回して生のシークレットが `session-logs/` に書かれる経路がない**。

これは LEARN#9 (外部スキーマ drift の grep 監査) と整合する設計で、新しいエージェント用アダプターを足してもマスキングは強制適用される。

**(c) NormalizedEvent の core 再検証**

アダプターは **信頼しない (untrusted)** という契約。アダプターが NormalizedEvent を core に渡しても、core 側で再度、型 / 範囲 / フィールドの整合性を検証する。理由は、攻撃者がエージェントのプロセスから偽造イベント (forged event) をアダプターに流し込んで、vault の任意ファイルへの書き込みを誘発する経路を塞ぐため。

「アダプターは単にスキーマ変換するだけで、最終判断は core」という構造にしておくと、新しいアダプターを足すときのセキュリティレビューの面が小さくなる。

## 2. マルチエージェント MCP セットアップ手順書 (Codex / Gemini / OpenCode)

KIOKU の MCP サーバーは v0.5 時点でエージェント非依存 (stdio + JSON-RPC) な実装で、技術的には Codex / Gemini / OpenCode のどれでも繋がるはずでした。**でも、各エージェントでどう設定すればいいかの手順書がゼロ**。ユーザーが自力で `~/.codex/config.toml` や `~/.gemini/settings.json` の MCP セクションを書く必要があった。

v0.7 で `docs/install-guide-multi-agent.md` (英語) + `.ja.md` (日本語) を新設して、3 エージェントそれぞれの:

* **設定ファイルの場所**: `~/.codex/config.toml` / `~/.gemini/settings.json` / `~/.config/opencode/opencode.json`
* **設定スニペット**: コピー & ペースト可能な JSON / TOML
* **動作確認コマンド**: `codex mcp ls`、`gemini mcp ls` 相当の手順
* **トラブルシューティング**: 既知の制約と対処

を整理しました。

### 「未検証」バナーという誠実装置

各エージェントの節の冒頭に **`Verification status: 未検証 (delegation 環境で install 不可)`** というバナーを明示掲載しています。これは「この手順書の内容が動くかどうかを KIOKU 作者が手元の委譲環境で完全には検証できなかった」を読者に正直に伝えるシグナルです。

OSS でマルチエージェント手順書を出す時、「動くと書いてあるけど環境次第で動かない」のはありがちな失敗パターンです。むしろ、**検証できなかった部分を明示する** 方が、読者の信頼につながると考えています。動作報告をもらえればバナーを取る、というスタンス。

v0.6 で内部ライブラリ (`mcp/lib/git-history.mjs` + `mcp/lib/wiki-snapshot.mjs`) は land 済でしたが、ユーザーが呼べる MCP tool は無い状態でした。v0.7 でその tool が出ます:

```
# Claude Desktop / Claude Code で
"kioku_generate_viz tool で wiki/some-page の成長 timeline を作って"
→ vault/wiki/some-page.html が生成される
```

生成される HTML は、**git history から該当ページの過去の commit を全部辿って、時系列にスナップショットを並べたビューア** です。Obsidian の Graph View が「ページ間の関係を空間的に見る」ものだとしたら、これは「**1 ページの時間軸での成長を見る**」もの。

### 実装の hardening

生成された HTML はユーザーの vault に置かれて Obsidian で開かれるので、XSS の hardening を念入りに入れました:

* スナップショット JSON は `safeJsonForScript` で `</`, U+2028, U+2029 を escape (`</script>` injection 等を遮断)
* DOM 描画は `createElement` + `textContent` のみ、`innerHTML` ゼロ
* インラインスタイルは CSS に静的に記述、ユーザーコンテンツから動的生成しない

### α であることの正直さ

**現時点では UI がラフです**。スナップショットを時系列に並べた静的な HTML で、Timeline Player (アニメーション) や Diff Viewer (2 時点の差分を色分け) は v0.8 で仕上げ予定です。

それでも v0.7 で出したのは、「時間軸で wiki を見る」という**体験への最初の触れ方**をユーザーに提供したかったから。スクリーンショット素材としても、KIOKU 固有の差別化軸 ("Obsidian の Graph View にない時間軸ビュー") の最初の visual proof としても機能します。

## 4. `verify-multi-agent-e2e.sh` — 導入後の安心動作確認スクリプト

ここまでで `install-hooks-gemini.sh` を走らせたユーザーは、「自分の Gemini で本当にセッションログが記録されるようになったか」を確認したくなります。v0.6 までは「session-logs/ にファイル出てるかなあ」と手動で `ls` する程度で、確証が薄かった。

v0.7 では 6 ステップの対話式の確認スクリプトを追加:

```
bash scripts/verify-multi-agent-e2e.sh --agent=gemini

# Step 1: gemini --version 確認
# Step 2: 認証リマインダー (login しているか)
# Step 3: install-hooks --probe で差分表示 → 確認プロンプト
# Step 4: 設定ファイルの構造確認 (jq で必須イベントキーを検証)
# Step 5: 別ターミナルで 1 セッション走らせるよう案内
# Step 6: session-logs/ の最新ファイルを inspect
#   - frontmatter の agent タグ確認 (gemini と書かれている)
#   - マスキングの spot check (テスト API キーを仕込んで *** に置換されているか確認)
#   - Codex は per-turn の git-sync を計上 (commit 数が想定通り)
```

ステップ 6 で **「マスキング spot check pass」** や **「per-turn git-sync 1 件確認」** が緑で出れば、ユーザーは dogfood する根拠を得られる。**手順書だけだと「動いてるけど不安」、確認スクリプトがあると「動いている」が一段確信に変わる**、という差です。

## セキュリティ実装の前進

v0.6 では SECURITY.md に CVE 分類 + Safe Harbor + 90 日 disclosure を入れて **ポリシーを形式化**しました。v0.7 はその実装側を、エージェント境界まで及ぶように:

* **agent-aware self-recursion guard (§43)** — `buildContext({ agent })` で Claude のみ self-recursion guard を発火させ、Gemini / Codex では guard を skip。Claude の auto-ingest が `claude -p` を spawn する経路だけ guard が必要で、Gemini / Codex には該当する再帰経路がないので guard を narrow した
* **アダプターの exit-0 契約** — 上述の `safeMain`、3 アダプターでエージェントの CLI をクラッシュさせない (DoS-by-self-fault 防止)
* **マスキングのパイプライン全エージェント適用** — 上述、`applyMasks()` の core 集約
* **NormalizedEvent の core 再検証** — 上述、アダプターを信頼しない契約

「Hardened LLM Wiki for Professionals」の Hardened 部分が、v0.6 の policy 化 → v0.7 のエージェント境界実装、と段階的に厚くなった形です。

## テスト / Lint

* Node / Bash の全 suite green
* `npm audit` で runtime deps の脆弱性 0 件継続
* 新規テスト:
  + `tests/hooks/adapters/{claude,gemini,codex}.test.mjs` (各アダプターのイベント正規化動作)
  + `tests/hooks/_common.test.mjs` (safeMain の exit-0 契約、forged event の reject)
  + `tests/mcp/tools-generate-viz.test.mjs` (HTML escape、innerHTML ゼロ、`</script>` injection block)
  + `tests/install-hooks-{gemini,codex}.test.sh` (冪等マージ、jq による既存 Hook の非破壊)

## インストール / アップグレード

### 新規

```
# 方法 A: Claude Code plugin marketplace (推奨)
claude plugin marketplace add megaphone-tokyo/kioku
claude plugin install kioku@megaphone-tokyo

# 方法 B: .mcpb (Claude Desktop 中心ユーザー)
# Releases から kioku-wiki-0.7.0.mcpb をダウンロードして drag & drop
```

### v0.6 → v0.7 のアップグレード

```
# 既存 clone で
git pull origin main
bash scripts/setup-vault.sh   # 冪等、既存ファイルは上書きしない

# Gemini でセッションログを取りたい場合
bash scripts/install-hooks-gemini.sh --apply

# Codex でセッションログを取りたい場合
bash scripts/install-hooks-codex.sh --apply

# 動作確認
bash scripts/verify-multi-agent-e2e.sh --agent=gemini
```

OpenCode の Hook 用アダプターは v0.7.0 では未提供 (MCP 手順書のみ)。需要次第で v0.7.x に乗せる予定です。

## 次に向けて

* **v0.7.1** — 主要な polish 数件 (Gemini アダプターの出力重複の解消、buildContext の realpath fallback、`agent:` frontmatter フィールド、SECURITY.ja.md 残翻訳 等)
* **v0.8 α** — Visualizer の本格 UI: Timeline Player (アニメーション) + Diff Viewer (2 時点比較を色分け)
* **OpenCode の Hook 用アダプター** — 需要次第
* **LP β + Discord soft launch** — 並行制作中

v0.6 → v0.7 でマルチエージェント narrative を「スキル共有」から「記憶共有」まで進めたので、次は **その記憶を時間軸で見る (v0.8 Visualizer)** が見せ場になる予定です。

## まとめ

* **v0.7.0**: v0.6 でスキルが共有された second brain、v0.7 で記憶も共有される
* **マルチエージェントの自動セッションログ**: `session-logger.mjs` 591 行 → core + 3 adapter (claude / gemini / codex) refactor、Gemini / Codex でも `session-logs/` に自動記録
* **マルチエージェント MCP セットアップ手順書**: 3 エージェント分のインストール / 設定 / 動作確認手順を英語 + 日本語で公式化、未検証バナー付き
* **Visualizer α**: `kioku_generate_viz` MCP tool で `wiki/<page>.html` 生成、時間軸で wiki を見る最初の体験 (UI ラフ、v0.8 で polish)
* **`verify-multi-agent-e2e.sh`**: 導入後の 6 ステップ対話式動作確認スクリプト
* **セキュリティ実装の前進**: agent-aware self-recursion guard / アダプター exit-0 契約 / マスキング全エージェント適用 / NormalizedEvent の core 再検証
* MIT License、フィードバック歓迎です

<https://github.com/megaphone-tokyo/kioku>

## 他のプロダクト

季節の写真を集めたギャラリーサイトです。作者が撮影した四季折々の写真を眺められるだけでなく、**自分の画像と季節の写真を AI で合成する**機能もあります。

写真が好きで、AI で遊ぶのも好き、という個人的な興味から作りました。

---

**作者**: [@megaphone\_tokyo](https://x.com/megaphone_tokyo)  
コードと AI で何かつくる人 / フリーランスエンジニア 10 年目 / 東京
