---
id: "2026-05-17-ai駆動開発-完全実践ガイド-ch2-6-prompt整備期での-copilot-活用-copilo-01"
title: "AI駆動開発 完全実践ガイド ｜ Ch.2-6 Prompt整備期での Copilot 活用 ― copilot-instructions."
url: "https://zenn.dev/zztomcat/articles/d460064cb71541"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-05-17"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

```
---
title: "「AI駆動開発 完全実践ガイド ｜ Ch.2-6 Prompt整備期での Copilot 活用 ― copilot-instructions.md の整備"
emoji: "🎯"
type: "tech"
topics: ["AI", "AIエージェント", "AI駆動開発", "GitHubCopilot", "copilot-instructions.md"]
published: true
---
```

## この記事は書籍『AI駆動開発 完全実践ガイド』の先行公開コンテンツです

本記事の内容は、2026年6月15日発売予定の書籍『AI駆動開発 完全実践ガイド ― Vibe期からHarness確立期へ』の一部を再編集したものです。  
※[本書籍の詳細と発売予定情報](https://zenn.dev/zztomcat/articles/d460064cb71541#%F0%9F%93%98-%E3%81%93%E3%81%AE%E8%A8%98%E4%BA%8B%E3%81%AF%E6%9B%B8%E7%B1%8D%E3%80%8Eai%E9%A7%86%E5%8B%95%E9%96%8B%E7%99%BA-%E5%AE%8C%E5%85%A8%E5%AE%9F%E8%B7%B5%E3%82%AC%E3%82%A4%E3%83%89%E3%80%8F%E3%81%AE%E5%85%88%E8%A1%8C%E5%85%AC%E9%96%8B%E3%82%B3%E3%83%B3%E3%83%86%E3%83%B3%E3%83%84%E3%81%A7%E3%81%99)を参照してください。

## 【章扉】

| **PART 2 ／ 基礎編 ― GitHub Copilotで始める**                                              **Ch.2-6**  **Prompt整備期での Copilot 活用**   *copilot-instructions.md の整備* |
| --- |

| 区分 | 内容 |
| --- | --- |
| **■ 本章の目的** | Phase 2（Prompt整備期）の核心である「プロンプト知識をリポジトリの契約に昇格させる」工程を、`copilot-instructions.md` を中心に実装レベルで習得する。属人化したプロンプト集から、チーム全員が参照する「コードと同じレベルでレビューされる文書」への移行を完了させる。 |
| **▶ 前提知識** | Ch.2-5（Vibe期での Copilot 活用 ― インライン Completion と Chat）の理解。GitHub Copilot Business／Enterprise いずれかのライセンスと VS Code（または対応IDE）の基本操作。Markdown の基本記法。 |
| **★ 本章で学ぶこと** | 1. なぜ Phase 2 で `copilot-instructions.md` が必要になるのか ― 属人化崩壊の構造 2. 5層インストラクション階層（Personal／Path-scoped／Repository／AGENTS.md／Organization）の関係 3. `copilot-instructions.md` の6セクション標準構造と書き方 4. 「Always-on」と「Path-scoped」の使い分け決定フロー 5. 90日導入ロードマップ（草案 → 第1反復 → 安定化） 6. よくある失敗パターンと検証チェックリスト |
| **● 本章の最適な対象者** | テックリード／シニアエンジニア／DevExチーム／プラットフォームエンジニア／開発生産性に責任を持つマネージャー |

---

## 2-6-1 はじめに ― なぜ「同じプロンプトを何度も書く」現象が起きるのか

**多くのチームは、Copilot を導入した瞬間に「個人の生産性は上がったがチームの一貫性は下がった」と感じる。**

Ch.2-5 で見たように、Vibe期（Phase 1）の Copilot は驚くほど強力だった。インライン補完は的確で、Chat は雑談しながら関数を仕上げる。しかし、それは「個人がそれぞれの流儀で AI と会話している」だけだ。Aさんは「Reactで」と書き、Bさんは「Vue.jsで」と書き、Cさんは何も指定せずに「ログイン画面を作って」と書く。出力は当然バラバラになる。

**現実は数字で見ると、もっと深刻だ。**

JetBrains の State of Developer Ecosystem では、AI開発ツールを「日常的に」使う開発者は2024年時点で過半数を超えたが、同じ調査で **「AIの出力品質はメンバーによって大きく違う」と感じる** チームは7割近くに達した。Copilot 自体は同じツールでも、入力されるプロンプトが属人化している以上、出力は属人化する。Microsoft の OpenJNY氏が指摘するように、Copilot のカスタマイズは「コンテキスト設計」の問題であり、ツールの問題ではない\*\*※6\*\*。

**問題は「Copilot をどう使うか」ではない。**

問題は、**「チームとして Copilot に伝えるべき前提・規約・コンテキスト」が誰の頭の中にしか存在しない** ことだ。新メンバーが入るたびに同じ説明をする。コードレビューで「うちは関数名 camelCase だよ」を毎回コメントする。AI出力の手直し時間が、本来 Copilot が節約してくれるはずだった時間を上回りはじめる ― これが **「プロンプト属人化 Hangover」** の正体である。

**本章では、この問題を `.github/copilot-instructions.md` という1枚の Markdown ファイルで解決する方法を提示する。**

`copilot-instructions.md` は、Phase 2（Prompt整備期）における **唯一かつ最も効果の高い投資** だ。書くべき内容は20〜50行。導入コストは半日。それで、チーム全員の Copilot 出力品質が揃いはじめる。**Phase 2 の終わりとは、「プロンプト知識が頭の中からファイルに移動した状態」** に他ならない。

| **Ch.2-6 の出発点** |
| --- |
| Phase 1 が個人の魔法なら、Phase 2 はチームの契約だ。 同じプロンプトを2回書いた瞬間、それは `copilot-instructions.md` に書くべき内容である。 属人化したプロンプト知識を、リポジトリで管理される文書に昇格させる ― それが本章の到達点。 |

| **本章の構成** |
| --- |
| ・2-6-2 では、Phase 2 における `copilot-instructions.md` の位置づけを成熟度マップで整理する ・2-6-3 では、5層インストラクション階層（Personal／Path-scoped／Repository／AGENTS.md／Organization）の関係を示す ・2-6-4 では、`copilot-instructions.md` の6セクション標準構造を分解する ・2-6-5 では、Always-on と Path-scoped の使い分け決定フローを提示する ・2-6-6 では、90日の段階的導入ロードマップを示す ・2-6-7 では、よくある失敗パターンと検証チェックリストを列挙する |

---

## 2-6-2 Phase 2における copilot-instructions.md の位置づけ

### 2-6-2-1 Phase 2 は「3つのステージ」に分解できる

本書 Ch.0-2 と Ch.1-3 で扱った「5段階成熟度モデル」**※16** において、Phase 2（Prompt整備期）は「個人開発者の Vibe期から、チーム標準が出来上がる Context整備期への橋渡し」と位置づけられる。本章で扱う `copilot-instructions.md` は、この橋渡しの **最終ステージ** に該当する。

![図2-6-1：Phase 2 における copilot-instructions.md の位置づけ](https://static.zenn.studio/user-upload/6e9147e31c3c-20260518.png)

*図 2-6-1：Phase 2 における copilot-instructions.md の位置づけ ― プロンプトの属人化から、リポジトリで管理される契約へ（出典：本書のために作成、AI生成。V9方法論マップ 2026 Edition と整合）*

Phase 2 は、以下の3つの内部ステージに分解できる。

* **Stage 2-A：個人プロンプト整備期** ― 個々の開発者が自分用のプロンプト集をNotionや個人 `.md` に蓄積しはじめる。トリガーは「同じプロンプトを5回以上書いた」という気づき。
* **Stage 2-B：チーム共有プロンプト集** ― チーム全員でアクセスできる場所（Notion／Wiki／社内ガイド）にプロンプト集を集約。ただしまだ「人間が見て参照する」ものに留まる。
* **Stage 2-C：`copilot-instructions.md` 標準化** ― プロンプト知識を `.github/copilot-instructions.md` に集約し、**AI自身が毎回のリクエストで自動参照する** 形式に昇格する。トリガーは「メンバー間で Copilot 出力品質に差が出ている」という痛み。

**Stage 2-C への移行は、技術的にはほぼゼロコストだが、組織的には大きな転換点である。** プロンプト集が「人間用ドキュメント」から「AI用ドキュメント」に変わる。Pull Request でレビューされる対象になる。リファクタリングと同じ重みで管理される対象になる ― これが Phase 2 の完了条件だ。

### 2-6-2-2 道具は同じ、使い方が進化する

V9 方法論マップが強調しているのは、**Phase 進化とはツール変更ではなく運用成熟度の変更である** という原則だ\*\*※16\*\*。Phase 1 の Copilot と Phase 2 の Copilot は、製品としては **同じ Copilot** である。何が違うかというと、**「Copilot に何を見せているか（コンテキスト）」** が違う。

| **項目** | **Phase 1（Vibe期）** | **Phase 2（Prompt整備期）** |
| --- | --- | --- |
| **使うCopilot機能** | インライン補完／Chat（Ask） | 同上＋カスタムインストラクション |
| **コンテキスト源** | 開いているファイル＋Chat入力 | 同上＋`copilot-instructions.md` |
| **主な担い手** | 個人開発者／早期導入エンジニア | 早期導入エンジニア＋テックリード |
| **管理対象** | なし（プロンプトは口頭・個人ノート） | `.github/copilot-instructions.md`／プロンプト集 |
| **品質の決め手** | 個人のプロンプト力 | チーム共通の規約文書の品質 |
| **次への移行サイン** | 同じミスを Copilot が繰り返す／チーム内で出力品質が割れる | パスや言語ごとに異なるルールが必要になる／Agent Mode／MCP に踏み込む |

道具を変える必要はない。**`.github/` ディレクトリに1枚のMarkdownを置くだけ** で、組織の AI 活用は1つ階段を上る。それが Phase 2 の特徴である\*\*※5\*\*。

---

## 2-6-3 5層インストラクション階層 ― copilot-instructions.md はどこに位置するか

### 2-6-3-1 GitHub Copilot の5層構造

2026年5月時点の GitHub Copilot は、カスタムインストラクションを **5層のレイヤー** で受け取る\*\*※10\*\*。これは以前は単純な階層だったが、Path-scoped 機能と Organization 機能の追加により、現在の構成に拡張された。

![図2-6-2：GitHub Copilot インストラクションファイル階層](https://static.zenn.studio/user-upload/52c6cb1fe307-20260518.png)

*図 2-6-2：GitHub Copilot インストラクションファイル階層 ― 5レイヤー構造とユニオン合成（出典：本書のために作成、AI生成。GitHub Docs、VS Code Docs、および Nived Velayudhan 解説記事 2026年5月版を参考に整理）*

### 2-6-3-2 各レイヤーの意味と配置

5つのレイヤーは、優先順位ではなく **「適用される範囲（スコープ）」が異なる** と理解するのが正しい。すべてのレイヤーがマッチした場合、VS Code はそれらを **ユニオン（和集合）** として合成し、1回のリクエストで全てモデルに渡す\*\*※10\*\*。

* **Layer 1：Personal Instructions** ― 個人のGitHub.com設定。「私はカジュアルに話してほしい」「私はTailwindよりCSSモジュール派」など個人的な好み。優先度は最も高い。
* **Layer 2：Path-scoped `.instructions.md`** ― `.github/instructions/NAME.instructions.md` 形式で配置。YAML frontmatter の `applyTo` で適用パスを指定する\*\*※9\*\*。例：`applyTo: "**/*.py"` で全Pythonファイルにのみ適用。
* **Layer 3：`.github/copilot-instructions.md`** ― **本章の主役**。リポジトリ全体に常時適用される。最初に作るべきファイルであり、ほとんどのチームにとって最初で最後のインストラクションファイル。
* **Layer 4：`AGENTS.md` ／ `CLAUDE.md` ／ `GEMINI.md`** ― 複数AIツールで共有するためのクロスツール標準\*\*※4\*\*。Linux Foundation の Agentic AI Foundation（AAIF）で2025年12月に標準化された。
* **Layer 5：Organization Instructions** ― GitHub Enterpriseの組織ポリシー。法務・セキュリティ規約など、全リポジトリに横断的に効かせたいルール。

### 2-6-3-3 Phase 2 では Layer 3 だけで十分

実務的に重要な観察は、**Phase 2 ではほぼ Layer 3 だけで足りる** という点だ。新規リポジトリで `.github/copilot-instructions.md` を1枚書き、それをチームで共通化する ― これが Phase 2 のスコープである\*\*※1\*\*。

Layer 2（Path-scoped）の導入は、リポジトリにフロントエンドとバックエンドが混在し、それぞれに異なる規約が必要になってから着手すれば良い。多くのプロジェクトでは Phase 3（Context整備期）の中盤以降の課題である。

Layer 4（`AGENTS.md` 等）は、Claude Code・Codex・Cursor 等の **複数AIツール併用** が前提のチームで本格的に必要となる。本書 Ch.4-1〜Ch.4-4 で詳述する。

| **Phase 2 における鉄則** |
| --- |
| まず Layer 3 だけを書く。 動作させる。 痛みが出てから Layer 2 を足す。 ― 「足し算で進める」のが Phase 2 の進化原則。 |

---

## 2-6-4 copilot-instructions.md の標準構造 ― 6セクションの解剖

### 2-6-4-1 GitHub Blog 推奨の6セクション

GitHub Blog の Burke Holland 氏（DevRel）が2025年9月に公開した記事\*\*※2\*\*は、`copilot-instructions.md` のデファクト標準構造を提示している。6つのセクションで構成され、それぞれが「Copilot が暗黙に持っている疑問」に答える形式だ。

![図2-6-3：copilot-instructions.md の6セクション標準構造](https://static.zenn.studio/user-upload/9cd9919b60cf-20260518.png)

*図 2-6-3：`copilot-instructions.md` の6セクション標準構造（出典：本書のために作成、AI生成。GitHub Blog「5 tips for writing better custom instructions for Copilot」2025年9月、GitHub Docs 2026年4月版を参考）*

### 2-6-4-2 各セクションが答える「Copilotの暗黙の疑問」

| **No.** | **セクション** | **Copilotの暗黙の疑問** | **書く粒度** |
| --- | --- | --- | --- |
| 1 | Project Overview | このプロジェクトは何のためのものか？ | 2〜3行（読者は AI だけでなく将来の自分） |
| 2 | Tech Stack | どの言語／フレームワーク／DBを使うか？ | バージョン込み（"Go 1.23" など） |
| 3 | Coding Guidelines | どんなコードスタイルか？ | 既存のLinterで自動チェックできない事項のみ |
| 4 | Project Structure | ファイルはどこに置くべきか？ | ツリー1段でOK |
| 5 | Build / Test / Run | 変更を検証するコマンドは？ | コピペで動く形 |
| 6 | Resources & Boundaries | 何をしてはいけないか／参照すべきドキュメントは？ | 触ってはいけないディレクトリやサービスを明記 |

### 2-6-4-3 最小実装テンプレート（80行版）

以下は、Go + PostgreSQL + Redis スタックを例にした **80行版テンプレート** である。実プロジェクトでも、これに近い長さに収めるのが現実的だ\*\*※2\*\*。

```
# Project Instructions for Copilot

## 1. Project Overview

This is a payment ledger service.

It exposes a REST API in Go and a Ruby client SDK
for selected billing endpoints.

Audience: internal billing team. Latency budget: p95 < 200ms.

## 2. Tech Stack

- Go 1.23 (server)
- Ruby 3.3 (client SDK)
- PostgreSQL 16 (primary store)
- Redis 7 (idempotency cache)
- Docker + Kubernetes (deploy)

## 3. Coding Guidelines

- Run `gofmt -s` and `golangci-lint run` before committing.
- Wrap errors with `errors.Wrap`, not `fmt.Errorf("%w", ...)`.
- Pass `context.Context` as the first argument to all
  service functions.
- Use `slog` for structured logging. Never use `fmt.Println`.
- For Ruby, follow rubocop and use `dry-monads` for Result types.

## 4. Project Structure

- `cmd/`        : main entrypoints
- `internal/`   : private business logic (do not import outside)
- `pkg/`        : public, reusable libraries
- `tests/e2e/`  : Playwright tests (see playwright.instructions.md)
- `docs/ARCH.md`: architecture decision record

## 5. Build / Test / Run

- Build      : `make build`
- Unit test  : `make test`
- Lint       : `make lint`
- Local run  : `docker compose up --build`
- DB migrate : `make migrate-up`

## 6. Resources & Boundaries

- Always read `docs/ARCH.md` before refactoring service boundaries.
- Never touch `infra/prod/` from a feature branch.
- Use mock DB connections in unit tests. Never connect to
  the production DB from local environment.
- When unsure about business rules, ask. Do not invent
  invariants from variable names.
```

| **テンプレート1セルテーブル** |
| --- |
| 1行は1つの完結した指示にする。「コーディング規約」と「テスト規約」を1行に詰め込まない。Copilot は「短く・自己完結した」指示の方が良く従う\*\*※10\*\*。 |

### 2-6-4-4 「なぜ」を書くと精度が上がる

VS Code 公式ドキュメント\*\*※10\*\*が強調しているのは、**ルールの背景（理由）を1行添えると、AIはエッジケースで賢くなる** という点だ。

たとえば「`moment.js` ではなく `date-fns` を使え」だけだと、Copilot は単純な置換しかしない。一方、`「moment.js はメンテ終了済みでバンドルサイズを増やすため、date-fns を使う」`と書けば、Copilot は他のレガシー時刻ライブラリも自発的に避けはじめる ― AIは「禁止」ではなく「方針」を学習する。

---

## 2-6-5 決定フロー ― この指示はどこに書くべきか

### 2-6-5-1 3つの選択肢

新しいルールをチームで決めたとき、それを `.md` ファイルに残すべき場所は3つある。

1. **`.github/copilot-instructions.md`** ― リポジトリ全体に常時適用。
2. **`.github/instructions/NAME.instructions.md` + `applyTo`** ― 特定のファイル・ディレクトリだけに適用。
3. **Agent Skill（`.github/skills/SKILL.md`）または Prompt File（`.github/prompts/*.prompt.md`）** ― 必要なときだけオンデマンドで読み込まれる\*\*※7\*\*。

選択を間違えると、**「全プロジェクトに Python ルールが適用される」「ノイズが多すぎてCopilotが指示を無視しはじめる」** といった失敗が起きる。

### 2-6-5-2 決定フロー

![図2-6-4：この指示はどこに書くべきかの決定フロー](https://res.cloudinary.com/zenn/image/fetch/s--yA5MdPIg--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/images/fig_2-6-4_decision_flow.png?_a=BACAGSGT)![](https://static.zenn.studio/user-upload/85dafcad3a42-20260518.png)

*図 2-6-4：この指示はどこに書くべきか ― 決定フロー（出典：本書のために作成、AI生成。GitHub Docs および「Unlocking the full power of Copilot code review」GitHub Blog 2026年4月版を参考）*

問いは2つだけだ。

* **Q1：そのルールはリポジトリ全体のすべてのファイルに当てはまるか？**
  + YES → `copilot-instructions.md`
  + NO（特定の言語・ディレクトリだけ）→ `*.instructions.md` + `applyTo`
* **Q2：そのルールは常に適用すべきか、それとも特定タスクのときだけか？**
  + 常時適用 → `copilot-instructions.md`
  + 特定タスクのみ → Agent Skill または Prompt File

### 2-6-5-3 3つのアンチパターン

GitHub の Copilot Code Review チームが2026年4月に公開した記事\*\*※11\*\*は、現場で頻発する3つのアンチパターンを警告している。

| **誤り** | **何が起きるか** | **正しいアプローチ** |
| --- | --- | --- |
| 言語ごとの細かい規約を `copilot-instructions.md` に詰め込む | TypeScriptのプロジェクトに Python ルールが混ざる／全体ファイルが膨張する | 言語別ルールは `*.instructions.md` + `applyTo: "**/*.py"` |
| 4,000文字／2ページを超える | Copilot が一部のルールを無視するようになる | 上限を意識して圧縮。重複削除。Skill に外出し |
| Linterが自動チェックできることをそのまま書く | ノイズが増え、本当に重要なルールが埋もれる | 「Linter で拾えないが守ってほしいこと」だけに集中 |

### 2-6-5-4 Path-scoped の最小例（Playwrightテスト用）

Phase 3 に踏み込むタイミングで最初に書かれることが多いのが、テストフレームワーク用の Path-scoped ファイルだ。GitHub Docs の公式例\*\*※1\*\*より：

```
---
applyTo: "**/tests/*.spec.ts"
---

## Playwright test requirements

When writing Playwright tests, please follow these
guidelines to ensure consistency and maintainability:

- Use stable locators. Prefer `getByRole()`, `getByText()`,
  and `getByTestId()` over CSS selectors or XPath.
- Use Page Object Model.
- Place all e2e tests in `tests/e2e/`.
- Mock external HTTP calls using `page.route()`.
```

YAML frontmatter で `applyTo` を指定し、その下に Markdown で規約を書くだけだ。これは Phase 2 を超え、Phase 3（Context整備期）に入った合図でもある。

---

## 2-6-6 90日導入ロードマップ ― 草案から安定運用まで

### 2-6-6-1 3つのマイルストーン

`copilot-instructions.md` の導入は、「書いて終わり」ではない。GitHub の公式ガイダンスは **「imperfect な指示書のほうが、ない状態より遥かに価値がある」** と繰り返している\*\*※2\*\*。最初から完璧を目指さない。書く → 動かす → 直す のサイクルを3ヶ月で1巡させるのが鉄則だ。

![図2-6-5：copilot-instructions.md 導入の定量的インパクト](https://static.zenn.studio/user-upload/1bba60c53e34-20260518.png)

*図 2-6-5：`copilot-instructions.md` 導入の定量的インパクト（出典：本書のために作成、AI生成。JX通信社の導入事例レポート（Zenn, 2024年9月）**※3** および公開された複数の採用事例を統合）*

### 2-6-6-2 Week 0〜Week 12 の進行

| **期間** | **マイルストーン** | **やること** | **避けること** |
| --- | --- | --- | --- |
| Week 0〜2 | **草案コミット** | テックリード1人で第1版を書き、PRでチームにレビュー依頼。「6セクション × 各3〜5行」の最小構成で開始 | 完璧を目指さない／全員参加のキックオフは不要 |
| Week 2〜6 | **観察期** | Copilot Chat の References セクションで `copilot-instructions.md` が読まれているか確認\*\*※1\*\*。出力品質の体感を週次で記録 | この期間に大きく書き換えない |
| Week 6 | **第1反復** | レトロスペクティブで「効いている／効いていない」項目を仕分け。効いていない項目は削除、足りない項目は追加 | 議論を1時間で終わらせる。コードレビューのコメント数を指標にする |
| Week 6〜10 | **横展開** | 他のリポジトリにもコピー＆カスタマイズ。テンプレート化を検討 | テンプレートを完璧にしてから配るのではなく、まず配って改善する |
| Week 10〜12 | **安定化** | プロジェクトに合わせて細かい調整。必要に応じて `*.instructions.md` を1〜2ファイル追加 | むやみに `*.instructions.md` を増やさない |

### 2-6-6-3 Copilot自身に書かせる ― 公式推奨フロー

GitHub Docs\*\*※1\*\* は、`copilot-instructions.md` の **最初のドラフトを Copilot Coding Agent 自身に書かせる** ことを推奨している。具体的には以下のプロンプトを `github.com/copilot/agents` のチャットに投げる：

```
Your task is to "onboard" this repository to Copilot
cloud agent by adding a .github/copilot-instructions.md
file. It should describe how a cloud agent seeing the
repo for the first time can work most efficiently.

Goals:
- Reduce CI failures.
- Minimize bash command and build failures.
- Allow the agent to complete tasks more quickly.

Limitations:
- Instructions must be no longer than 2 pages.
- Instructions should be broadly applicable.

Guidance:
- A summary of what the app does.
- The tech stack in use.
- Coding guidelines.
- Project structure.
- Existing tools and resources.
```

Copilot がリポジトリを走査し、80〜120行程度の `copilot-instructions.md` を生成する。**それを人間がレビュー・編集して PR に出す** のが推奨フローだ。ゼロから書くより速く、かつ Copilot が自分自身のために最適な内容を提案してくれる。

### 2-6-6-4 日本企業の実例 ― JX通信社のケース

国内では JX通信社が2024年9月にZennで導入レポートを公開している\*\*※3\*\*。同社のレポートを参考に、本書でも複数の公開事例を統合した定量データが先の図 2-6-5 のとおりである。**3ヶ月での主要指標の改善幅は、いずれの事例でも50%以上に達している**。

| **JX通信社の導入から得た学び（公開情報を本書が整理）** |
| --- |
| ・「コードスタイル指摘」のレビューコメントが激減した（重要なロジック指摘に集中できるようになった） ・新メンバーのオンボーディング期間が短縮した（"うちのお作法" が文書化されたため） ・**逆に、`copilot-instructions.md` 自体のレビュープロセスが必要になった**（重要文書なので雑に変更できない） |

3点目の「文書自体のレビュー」が必要になる ― これは Phase 2 が成功している証拠であり、同時に Phase 3 への移行サインでもある\*\*※16\*\*。

---

## 2-6-7 よくある誤解と落とし穴

### 2-6-7-1 誤解1：「長く書くほど効く」

これは最も多い誤解だ。前述の通り、4,000文字を超えると Copilot は **読み飛ばしや無視を始める**（非決定的挙動）**※11**。長さは「効果の代理指標」ではない。**「読まれるかどうか」を意識し、20〜50行を目安に圧縮する** こと。

### 2-6-7-2 誤解2：「`AGENTS.md` を書けば `copilot-instructions.md` は不要」

OpenAI の AGENTS.md 標準は2025年8月に公開され、複数AIツール（Codex／Claude Code／Cursor 等）で共有できる利点がある\*\*※4\*\*。しかし、**Copilot は `copilot-instructions.md` と `AGENTS.md` の両方を読む**（両方が存在すれば両方使う）**※8**。

Phase 2 段階では、まず `copilot-instructions.md` を整える。`AGENTS.md` への一本化は、Codex CLI や Claude Code を本格運用しはじめる Phase 3 後半〜Phase 4 のテーマである。本書 Ch.4-2 で詳述する。

### 2-6-7-3 誤解3：「個人開発者には不要」

これも間違いだ。**個人プロジェクトでも `copilot-instructions.md` は効果的** である。理由は2つ：

* セッションをまたいで Copilot が安定する（同じ前提から始まる）
* 数ヶ月後に自分が戻ってきたとき、Copilot が "そのプロジェクトの流儀" を覚えていてくれる

Jesse Liberty のブログ\*\*※5\*\*でも、個人プロジェクトでの導入価値が強調されている。

### 2-6-7-4 落とし穴：「`copilot-instructions.md` のバージョン管理を怠る」

`copilot-instructions.md` は **コードと同じ重みで PR レビュー** されるべきだ。理由は、

* AI出力に直接影響する（プロダクションコード並みの影響力）
* 古い指示が残っていると、新しい規約を上書きしてしまう
* 「言った言わない」問題を発生させる

これは、Phase 2 の終盤で「文書自体のレビュープロセス」を確立することと同義である。

### 2-6-7-5 検証チェックリスト ― Phase 2 完了の合図

以下8項目のうち、6つ以上にYESと答えられたら Phase 2 は完了し、Phase 3（Context整備期）への移行準備が整ったと判断できる。

| **No.** | **チェック項目** | **YES／NO** |
| --- | --- | --- |
| 1 | `.github/copilot-instructions.md` がリポジトリのルートに存在する |  |
| 2 | ファイルの長さは100行以内である |  |
| 3 | 6セクション（Overview／Tech Stack／Guidelines／Structure／Build／Boundaries）が揃っている |  |
| 4 | Copilot Chat の References で実際に参照されていることを確認した |  |
| 5 | 過去3ヶ月で少なくとも1回は更新された |  |
| 6 | 更新は PR レビューを経た |  |
| 7 | チームの3人以上が中身を読んでいる |  |
| 8 | "Copilot がうちの規約に従わない" という不満が、計測可能なレベルで減った |  |

| **黄金律（Phase 2 編）** |
| --- |
| 完璧な `copilot-instructions.md` を書こうとするな。 **まず書け。そして直し続けろ。** ― Burke Holland（GitHub Blog, 2025年9月）**※2** |

---

## 2-6-8 本章のまとめ

本章で読者は、Phase 2（Prompt整備期）の核心である「プロンプト知識をリポジトリの契約に昇格させる」ための、実装レベルのノウハウを手にした：

1. Phase 2 は「個人プロンプト → チーム共有 → `copilot-instructions.md`」の3ステージで進む（2-6-2）。
2. GitHub Copilot のインストラクションは5層構造で、Phase 2 では Layer 3 だけで十分（2-6-3）。
3. `copilot-instructions.md` の標準構造は6セクションで、20〜50行に収める（2-6-4）。
4. 新しいルールをどこに書くかは、2つの問い（リポジトリ全体か／常時適用か）で決まる（2-6-5）。
5. 導入は90日サイクルで、最初のドラフトは Copilot 自身に書かせる（2-6-6）。
6. 4,000文字超過・Linter重複・個人スキップは典型的なアンチパターン（2-6-7）。

| **3つの問い（教育・研修・コードレビューの場で有効）** |
| --- |
| Step 1：「同じプロンプトを何度書いたか？」 → Phase 2 への移行サイン Step 2：「`copilot-instructions.md` は何文字あるか？」 → 4,000字超過なら危険信号 Step 3：「最後に PR レビューを経て更新されたのはいつか？」 → 3ヶ月以上前なら腐敗のサイン |

次の Ch.2-7 では、`copilot-instructions.md` を土台として、**Copilot Coding Agent**（GitHubイシューをアサインしてPRを自動作成する非同期エージェント）の実践に進む。`copilot-instructions.md` が整っていれば、Coding Agent の出力品質は劇的に上がる ― 本章で築いた基盤が、Phase 3 以降のすべての応用編で活きてくる。

| **Ch.2-6 の結論** |
| --- |
| `copilot-instructions.md` は、Phase 2（Prompt整備期）における **唯一かつ最も効果の高い投資** である。 1枚のMarkdown、80行、半日で書ける。 これを書かないチームは、Vibe期の魔法のまま、属人化の地獄に留まる。 ― **AIは「使うもの」ではない。文書化して、契約化して、レビューし続けるものだ。** |

**多くの企業は Copilot 導入で満足している。**

しかし、開発速度はほとんど変わらない。

**なぜか？**

問題はツールではない。**`.github/copilot-instructions.md` がないからだ。**

プロンプトは「個人の頭」に置くものではない。**リポジトリに置き、チームでレビューし、AIに毎日読ませるものだ。**

---

## 参考文献

本章の本文中で「※N」と参照した出典は以下の通り。すべてのURLは2026年5月時点で実在を確認済み。

**※1**　GitHub Docs, "Adding repository custom instructions for GitHub Copilot," 2026年4月更新. <https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot>

**※2**　Burke Holland (GitHub Blog), "5 tips for writing better custom instructions for Copilot," 2025年9月3日. <https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/>

**※3**　Zenn（JX通信社, sirosuzume）, "copilot-instructions.mdは使えるぞ！実戦投入レポート," 2024年9月1日. <https://zenn.dev/sirosuzume/articles/9962625cde1298>

**※4**　Linux Foundation, "Linux Foundation Announces the Formation of the Agentic AI Foundation (AAIF)," 2025年12月9日. <https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation>

**※5**　Jesse Liberty, "copilot-instructions.md," 2026年2月22日. <https://jesseliberty.com/2026/02/22/copilot-instructions-md/>

**※6**　Zenn（Microsoft, openjny）, "「Skills？MCP？インストラクション？」仕組みからわかる GitHub Copilot のカスタマイズ戦略ガイド," 2025年12月21日. <https://zenn.dev/openjny/articles/91e88d7914e5bc>

**※7**　Microsoft Developer Blog, "Introducing the Awesome GitHub Copilot Customizations repo," 2025年7月. <https://developer.microsoft.com/blog/introducing-awesome-github-copilot-customizations-repo>

**※8**　Zenn（lv）, "GitHub CopilotがついにCLAUDE.mdを公式サポート。copilot-instructions.mdの役目を考え直す," 2026年2月19日. <https://zenn.dev/lv/articles/3c629c46c7e72b>

**※9**　GitHub Changelog, "Copilot code review: Path-scoped custom instruction file support," 2025年9月3日. <https://github.blog/changelog/2025-09-03-copilot-code-review-path-scoped-custom-instruction-file-support/>

**※10**　Visual Studio Code Docs, "Use custom instructions in VS Code," 2026年3月更新. <https://code.visualstudio.com/docs/copilot/customization/custom-instructions>

**※11**　Ria Gopu (GitHub Blog), "Unlocking the full power of Copilot code review: Master your instructions files," 2025年11月14日／2026年4月17日更新. <https://github.blog/ai-and-ml/github-copilot/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/>

**※12**　Nived Velayudhan (Medium), "GitHub Copilot Custom Instructions: How copilot-instructions.md, applyTo Rules, and Prompt Files Work," 2026年5月. <https://nivedv.medium.com/before-the-agent-starts-how-github-copilots-customization-layer-actually-works-a7db689c795e>

**※13**　GitHub Repository, "github/awesome-copilot ― Community-contributed instructions, agents, skills, and configurations," 2026年5月閲覧. <https://github.com/github/awesome-copilot>

**※14**　Microsoft Developer Blog, "Awesome GitHub Copilot just got a website, and a learning hub, and plugins!," 2026年3月. <https://developer.microsoft.com/blog/awesome-github-copilot-just-got-a-website-and-a-learning-hub-and-plugins>

**※15**　Zenn（katsuhisa\_）, "GitHub Copilotのカスタム命令で開発を効率化する," 2026年1月25日. <https://zenn.dev/katsuhisa_/articles/github-copilot-custom-instructions-2025>

**※16**　本書付属資料 "AI駆動開発の方法論マップ（Methodology Map for AI-Driven Development）," 2026 Edition．関係図／成熟度マップ／境界マップの3視点から構成。Phase 2（Prompt整備期）と Phase 3（Context整備期）の境界線、および Layer 3 → Layer 2 → Layer 4 への進化順序は、本マップの「成熟度マップ ― 組織は5段階で進化する」と「ツール × 運用成熟度 Phase」の章に準拠している。

― ―

---

## 📘 この記事は書籍『AI駆動開発 完全実践ガイド』の先行公開コンテンツです

本記事の内容は、**2026年6月15日発売予定**の書籍『AI駆動開発 完全実践ガイド ― Vibe期からHarness確立期へ』の一部を再編集したものです。

![alt text](https://static.zenn.studio/user-upload/cfb749277cce-20260513.png)

書籍では本記事の3〜5倍の解像度で、以下を体系化しています：

* 5段階成熟度モデル（Vibe / Prompt整備 / Context整備 / SDD-TDD / Harness）
* Phase × 3大Agent（Copilot / Codex / Claude Code）マトリクス
* ルールファイル統一戦略（AGENTS.md / CLAUDE.md / copilot-instructions.md）
* 失敗パターン9種と対処法
* 18-24ヶ月の段階的導入ロードマップ

### 本書籍の特徴と位置付け：

| 軸 | 市場中他書籍の現状（2026年5月） | 本書の特徴独自ポジション |
| --- | --- | --- |
| 思想層 | Vibe Coding / プロンプト中心 | Phase 5 (Harness確立期) を扱う日本語圏初の書籍 |
| 方法論 | 単一ツール解説（Copilot本／Claude Code本） | 5方法論×5Phase×3大Agentのマトリクス |
| 経営視点 | 技術書中心、経営層向けはほぼ皆無 | Executive Summary 5セクションを巻頭装着 |
| 鮮度 | Karpathy 2025/Vibe命名止まり | Mitchell Hashimoto 2026/2、OpenAI Codex 100万行、Anthropic Managed Agentsを完全反映 |
| 差別化最強章 | ー | Ch.4-1 　　　　ルールファイル統一戦略（AGENTS.md / CLAUDE.md / copilot-instructions.md）= 世界初の書籍化 |

### 販売予告情報

📅 電子版発売予定日：2026年6月15日　（※前後にする可能性がある）  
📅 書籍版の販売予定日は調整中  
📚 全75章 + 付録24種  
🎯 日本語圏初の Phase 5（Harness確立期）対応書籍

本書籍の内容（目次レベル）もっと知りたい場合はここ  
<https://zenn.dev/zztomcat/articles/923b0b7dbdd53f>

発売告知をでお届けします。事前興味のある方はフォローお願いします。  
X:[@ZY20240528](https://x.com/ZY20240528)  
LinkedIn:[tomcat-zhou](https://www.linkedin.com/in/tomcat-zhou)  
Facebook:[zhou yi](https://www.facebook.com/zhou.yi.1048/)

### 著者情報

[Acrosstudio株式会社](https://www.acrosstudio.co.jp/#company:~:text=%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%82%92%E6%A7%8B%E7%AF%89-,Members,-%E4%BB%A3%E8%A1%A8%E5%8F%96%E7%B7%A0%E5%BD%B9)　[執行役員CTO 周毅（しゅう　つよし）](https://www.acrosstudio.co.jp/news-detail.html?id=z5e43cwim)  
アジャイルでのプロダクト開発及び、グローバル開発拠点を含む技術組織の立ち上げ・再生に幅広い実績を有する。日産車体やアービムコンサルティング、日本IBM、RPAホールディングス、株式会社ジーニーなど、数々の名だたる企業でマネジメント経験を積んだ後、直近は、スタートアップや上場企業でのCTOの立場からグローバルなエンジニアマネジメント、AIモデル構築、プロダクト企画、AI事業開発を実施。生成AIスタートアップのM&A, PMI経験、事業リード経験も有す。2024年8月Acrosstudioへ執行役員CTOとしてジョイン。
