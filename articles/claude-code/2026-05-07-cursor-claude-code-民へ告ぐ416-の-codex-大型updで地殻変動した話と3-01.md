---
id: "2026-05-07-cursor-claude-code-民へ告ぐ416-の-codex-大型updで地殻変動した話と3-01"
title: "Cursor / Claude Code 民へ告ぐ。4/16 の Codex 大型UPDで地殻変動した話と、30種類のAIに1ファイルでルール配布する .ruler 完全ガイド"
url: "https://note.com/kento_kanazawa/n/na9de053bdc32"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "OpenAI"]
date_published: "2026-05-07"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

## Cursor / Claude Code 民へ告ぐ。4/16 の Codex 大型UPDで地殻変動した話と、30種類のAIに1ファイルでルール配布する .ruler 完全ガイド

> **TL;DR**  
> - 2026年4月16日、OpenAI Codex が "Computer Use × In-app ブラウザ × Memory × スケジューリング × 90+ プラグイン" を一気に解禁し、ChatGPT 内で "ほぼ全部やる相棒" に化けた。  
> - その3日前、Anthropic Claude Opus 4.7 が GA し、1Mコンテキストが標準価格に。Claude Code 側も /skills 検索や plugin prune で運用負荷を下げてきた。  
> - 結論として **"両方使う"** が現実解。ところが両方使うと CLAUDE.md と AGENTS.md と .cursorrules が手で同期する地獄になる。  
> - そこに刺さるのが **.ruler**(intellectronica/ruler)。.ruler/ に1回書けば **30以上のAIエージェント**に自動配布される。**v0.3.40 が 2026年5月1日リリース** されたばかりの最旬ツールだ。

※イメージ画像

---

## 1. 何が起きた? — 2026年4月後半の48時間で勢力図が動いた

![](https://assets.st-note.com/img/1778115808-bnY7L0rPBdCDNUVZuqIWjH84.png?width=1200)

※イメージ画像

「ChatGPT 内コーディング = ToyだろJK」と言ってた人、ちょっと座ろう。**4月16日の Codex アップデートはオモチャの域を完全に超えた**。

OpenAI が同日リリースしたのは、ざっくり以下の塊だ:

* **Computer Use 解禁** — Codex がカーソルを動かしてアプリを操作する。複数エージェント並列でも、ユーザー本人の作業を邪魔しない設計
* **In-app ブラウザ** — ブラウザに直接コメントして指示。フロントエンドのモックも、ゲーム画像も、同じワークフロー内で生成 (gpt-image-1.5 同梱)
* **Memory プレビュー** — 個人の好み、過去の修正指示、蓄積した知見を **セッションをまたいで覚える**
* **スケジューリング** — 数日 〜 数週間にわたるロングタスクを Codex 自身が予約・継続実行
* **90+ プラグイン拡充** — Atlassian Rovo / CircleCI / CodeRabbit / GitLab Issues / Microsoft Suite / Neon / Render…

加えて **Codex CLI も同時に化けた**:

* **Windows ネイティブサンドボックス**: WSL不要、PowerShell + OS ファイアウォールでプロキシのみ通すバイパス不能設計
* **GPT-5.3-Codex-Spark (research preview)**: 1000+ TPS のリアルタイム コーディングモデル。CLI / IDE 拡張 / Codex アプリ同梱、ChatGPT Pro 限定
* **GPT-5.5 / 5.5 Pro が API公開 (4/24)**: 5.4 より高知能 + トークン効率改善

そして 3日前の 4月13日に Claude Opus 4.7 が GA し、1Mコンテキストが Opus 4.6 と同額に開放されている ($5/$25 per 1M tokens)。Vision も最大 2576px / 3.75MP まで対応。Claude Code 側でも /skills 検索ボックス、claude plugin prune、Hooks 強化 (updatedToolOutput で出力書換、duration\_ms 追加)が同時に降ってきた。

**つまり 4/13 → 4/16 のたった3日で、両陣営が"アシスタント"の定義を書き換えた**。

---

## 2. Codex × Claude Code、4月以降の機能対比表

「で、どっち使えばいいの?」に対する一覧表がこちら。**両方使う前提**で見てほしい。

観点 OpenAI Codex (2026/4/16以降) Anthropic Claude Code (Opus 4.7世代) **看板モデル** GPT-5.5 / 5.5 Pro / Codex-Spark Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5 **コンテキスト** GPT-5.5 系で長文対応 **1M tokens を標準価格**で開放 **PC操作 (Computer Use)** 解禁、複数エージェント並列 別系統で提供 **画像生成** gpt-image-1.5 In-app 高解像度 **Vision 入力** (2576px) が強み **メモリ** Memory プレビュー (個人の癖を学習) Managed Agents Memory (managed-agents-2026-04-01) **スケジューリング / 長期タスク** ネイティブ対応 Hooks + Dispatch + Remote Control で組む **プラグイン** 90+ (Atlassian/CircleCI/GitLab他) Skills / MCP サーバー (拡張は MCP経由) **CLI のサンドボックス** **Windows ネイティブ** (WSL不要) macOS/Linux 中心、Windows は WSL 推奨 **CLI のスキル探索** プラグイン UI **/skills 検索ボックス** (type-to-filter) **キャッシュ** プロンプト最適化任意 **cache\_control 1個で自動末尾キャッシュ** **課金単位** API トークン換算に統一 (4/2〜) トークン単位 (新トークナイザーで最大35%増の罠) **ルールファイル** AGENTS.md + .codex/config.toml CLAUDE.md + .mcp.json **強み** "PCを動かす相棒" / 90+ サードパーティ統合 コーディング精度 / 1M context / Skills エコ **罠** プラグイン依存度↑ / Spark は Pro 限定 新トークナイザー実質コスト増

ぶっちゃけ **守備範囲が違う**。Codex は "**自律で動く**" 方向、Claude Code は "**深く考えて確実に**" 方向。だから "両方使う" が現実解になる。

---

## 3. 両方使うと地獄になる "ルールファイル散乱" 問題

![](https://assets.st-note.com/img/1778115802-qHA2S9QLzkGUtlJMDu4WgcFN.png?width=1200)

※イメージ画像

両方使うとこうなる:

* CLAUDE.md (Claude Code)
* AGENTS.md (Codex / 標準)
* .codex/config.toml (Codex CLI)
* .cursorrules または .cursor/rules/\*.mdc (Cursor)
* .clinerules (Cline)
* .windsurf/mcp\_config.json (Windsurf)
* .gemini/settings.json (Gemini CLI)
* .aider.conf.yml (Aider)
* WARP.md (Warp)
* .junie/skills/ (Junie)

**全部同じこと書いてる**。コーディング規約、テスト方針、禁止事項、プロジェクトの背景。**手でコピペしてる人、絶対1ヶ所更新忘れる**。

そして「あれ、Cursor では言うこと聞いてくれるのに Claude Code でハマる」現象が始まる。原因は古い CLAUDE.md だ。**この問題を構造で解く** のが .ruler だ。

---

## 4. .ruler 完全ガイド — .ruler/ に1回書けば 30エージェントに自動配布

### 正体

* リポジトリ: intellectronica/ruler (npm: @intellectronica/ruler)
* キャッチコピー: **"Apply the same rules to all coding agents"**
* 最新: **v0.3.40 (2026-05-01 リリース)** ← つい先週
* ライセンス: MIT、TypeScript 98.9%、Star ≈ 2.7k

呼称の由来は本体が「ドット始まりの隠しディレクトリ .ruler/」に置かれること。"dot ruler" を日本語読みして「**どっとルーラー**」だ。

### インストール (Node.js 20.19+ が必要)

```
# グローバル
npm install -g @intellectronica/ruler

# またはプロジェクト単位で
npx @intellectronica/ruler init
npx @intellectronica/ruler apply
```

### コマンドは3つだけ

コマンド 役割 ruler init .ruler/ と AGENTS.md / ruler.toml を生成 ruler apply .ruler/ の内容を全エージェントの設定ファイルに配布 ruler revert .bak バックアップから安全に巻き戻す

apply には実用フラグが揃ってる:

* --dry-run で配布前にプレビュー
* --agents claude,cursor で対象限定
* --nested で **モノレポの階層ロード** (frontend / backend に別ルール継承)
* --mcp / --no-mcp で MCP サーバー設定の同期切替
* --skills / --no-skills で Skills 伝搬切替

### .ruler/ の中身と読み込み順

優先度はかっちり決まってる:

1. リポジトリ直下の AGENTS.md
2. .ruler/AGENTS.md (新デフォルト)
3. .ruler/instructions.md (レガシー、AGENTS.md がない場合のみ)
4. .ruler/ 直下の他の .md (アルファベット順)

各ファイル先頭には自動で <!-- Source: <相対パス> --> が差し込まれ、**トレーサビリティが担保**される。

```
.ruler/
├── AGENTS.md          # メインルール
├── coding_style.md    # PEP8 / 型ヒント必須など
├── api_conventions.md
├── ruler.toml         # 設定本体
└── skills/api-design/SKILL.md
```

### 出力先マッピング — 30+ エージェント対応

エージェント 書き出し先 Claude Code CLAUDE.md + .mcp.json OpenAI Codex CLI AGENTS.md + .codex/config.toml GitHub Copilot AGENTS.md + .vscode/mcp.json Cursor AGENTS.md + .cursor/mcp.json Cline .clinerules Windsurf AGENTS.md + .windsurf/mcp\_config.json Gemini CLI AGENTS.md + .gemini/settings.json Aider AGENTS.md + .aider.conf.yml Amazon Q CLI .amazonq/rules/ruler\_q\_rules.md JetBrains AI .aiassistant/rules/AGENTS.md Warp WARP.md Kiro / Junie / Goose / Crush / Roo / Zed / Trae / Firebender 各専用パス

### ruler.toml の実例

```
default_agents = ["copilot", "claude", "aider"]

[mcp]
enabled = true
merge_strategy = "merge"

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "${PROJECT_ROOT}"]

[agents.claude]
enabled = true
output_path = "CLAUDE.md"

[agents.windsurf]
enabled = false

[gitignore]
enabled = true
```

.gitignore は # START Ruler Generated Files / # END Ruler Generated Files で囲まれた管理ブロックを **自動メンテ**してくれるので、生成ファイルを誤コミットしない設計だ。

---

## 5. 5分で導入する手順

```
# 1. プロジェクトルートで
npx @intellectronica/ruler init

# 2. .ruler/AGENTS.md を編集 (これが Single Source of Truth)
#    - コーディング規約
#    - テスト方針
#    - 禁止事項
#    - プロジェクト背景

# 3. ruler.toml で対象エージェントを絞る
#    default_agents = ["claude", "codex", "cursor"]

# 4. プレビュー
npx @intellectronica/ruler apply --dry-run

# 5. 配布
npx @intellectronica/ruler apply

# 6. (推奨) pre-commit フックで自動化
echo 'npx @intellectronica/ruler apply' >> .git/hooks/pre-commit
```

これで CLAUDE.md を編集する必要がなくなる。**.ruler/AGENTS.md だけが真実**になる。

---

## 6. AGENTS.md 標準との関係 — Ruler は "標準を運ぶ宅配便"

ここ重要。**AGENTS.md は 2026年に Linux Foundation 傘下の Agentic AI Foundation (AAIF) に寄贈され、正式なオープン標準になった**。OpenAI / Anthropic / Google / AWS / Cursor / Cloudflare などが参加し、リリース以降 60,000+ OSSプロジェクトで採用されている。

つまり構図はこう:

Best Practice は **"Use Both"**。AGENTS.md だけだと Cline や Aider など独自ファイルを要求するツールがカバーできない。逆に Ruler だけで AGENTS.md を書かないと標準準拠から外れる。両方使う。

---

## 7. 個人開発者の最適運用 (現場で踏んだ罠)

### やるべきこと

* **pre-commit か pre-push フックで ruler apply を自動化**: これを忘れると、ローカルが古い CLAUDE.md のまま動いて死ぬ
* **--nested で モノレポ対応**: frontend / backend / tests それぞれに継承付きで配布できる
* **--dry-run を本番投入前に必ず**: 何が書き換わるかプレビューしてから
* **.bak を残す revert を信頼する**: 失敗できる安心感が運用を変える

### ⚠ ハマりポイント

* **Ruler は配布専用** — ルールの作成・バージョニング・ドリフト検知・品質評価はしない ("Ruler distributes, but it does not create standards")。**作るのは人間の仕事**
* **Node.js 20.19+ が必須** — Python 専業勢には地味な参入障壁
* **各エージェント固有の高度機能までカバーしない** — 例: Cursor の glob ターゲット指定など
* **バージョン進行が速い** — v0.3.40 で subagents → agents のような破壊的リネームが入った例がある

---

## 8. 競合・代替ツール (ご参考)

![](https://assets.st-note.com/img/1778115790-KyzlGXj1scNkFw7JHMovrYtZ.png?width=1200)

※イメージ画像

* **rule-porter** — Cursor .mdc を CLAUDE.md / AGENTS.md / Copilot に**一方向変換**するゼロ依存CLI (同期管理ではない)
* **agent-style** (yzhao062) — Claude / Codex / Copilot / Cursor / Aider 向け 21 の**執筆スタイル**ルール集 (コンテンツ寄り)
* **AI-Rule-Spec / aicodingrules.org** — YAML+Markdown のハイブリッド仕様化
* **AGENTS.md 単体運用** — ツール側が直接読むので、対応ツールだけならこれで足りる

「Ruler は重い」「AGENTS.md だけで十分」というケースもある。プロジェクト規模で選べばOK。

---

## 9. まとめ — 2026年5月時点の "AI時代の .gitignore"

* **4/13 Claude Opus 4.7 GA** で Anthropic が "**長文 × 高解像度**" を取りに来た
* **4/16 Codex 大型UPD** で OpenAI が "**自律で動く相棒**" を取りに来た
* 結果として両方使うのが最適解 → **ルールファイル散乱問題が顕在化**
* そこに **.ruler v0.3.40 (2026-05-01)** がぴったりハマる

CLAUDE.md と AGENTS.md と .cursorrules を手でコピペしてる人、**2026年は卒業しよう**。.ruler/ にルールを 1回書けば、30種類のAIエージェントに自動配布される。**Single Source of Truth が AI時代の .gitignore になる**。

導入は npx @intellectronica/ruler init の1行。試して、合わなければ ruler revert で戻せる。失敗できる安心感がある。今週の TODO リストにこれを足してほしい。

---

### 参考リンク (一次ソース優先)
