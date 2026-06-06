---
id: "2026-06-05-初心者向けclaude-code-workflow-codex-goal-の組み合わせと知っておくべ-01"
title: "【初心者向け】Claude Code workflow × Codex /goal の組み合わせと、知っておくべきコマンド40選"
url: "https://qiita.com/TaichiEndoh/items/8811b4605880e7732cea"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "OpenAI"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

## 📖 この記事の概要（3行で）

- Claude Code の `workflow` と Codex の `/goal` を**役割分担**で組み合わせると、AI開発がかなり現実的になります
- 「Claude Code = 設計係、Codex = 実装係」という考え方が、AI開発を安定させる鍵です
- workflow 以外にも、**Claude Code 30個 + Codex 10個の便利コマンド**を、初心者でも使えるように具体例付きで紹介します

---

## はじめに ─ こんな悩みありませんか？

AI開発ツールの進化が速すぎて、ついていけない…と感じている方、多いと思います。

> 「Claude Code 入れたけど、`/help` 以外何使ったらいいか分からない」
>
> 「Codex の `/goal` 使ってみたいけど、ふわっとした指示しかできない」
>
> 「AIにコード書かせたら、関係ないファイルまで触られて困った」

私もまったく同じところから始めました。

この記事では、

1. **Claude Code workflow と Codex /goal** の役割分担と組み合わせ方
2. **それ以外の便利コマンド40選**（特に workflow と /goal 以外を厚く）
3. **初心者がハマる落とし穴と回避方法**

を、できるだけ平易に整理します。

> 🔰 **Claude Code（クロード・コード）って何？**
> Anthropic 社が出している、ターミナル（黒い画面）で動くAIコーディングアシスタント。コードを読んだり書いたり、リポジトリ全体を理解して作業してくれる。

> 🔰 **Codex（コーデックス）って何？**
> OpenAI 社が出している、AIコーディングエージェント。ChatGPT Plus/Pro/Business プランに付いてくる。CLI・VS Code・JetBrains・macOSアプリで使える。

---

## 1. ふたつの役割分担を、ざっくり理解する

これが全体の土台です。

| ツール | 得意なこと | 一言でいうと |
|---|---|---|
| **Claude Code の workflow** | 大きな課題を**分解・調査・並列処理**する | **設計係** |
| **Codex の /goal** | 明確な完成状態に向かって**実装・修正・テスト**を回す | **実装係** |

つまりこういうことです：

```
Claude Code workflow で「何をどう作るか」を整理し、
Codex /goal で「完成状態まで持っていく」
```

### 食堂のたとえで考える

イメージしやすくたとえてみます。

- **Claude Code workflow** = ベテラン料理長
  - メニュー全体を見渡して、「今日はこの順番で作ろう」と段取りを決める
  - 若手に「あなたはサラダ、あなたはスープ」と仕事を割り振る
- **Codex /goal** = 専門料理人
  - 「この料理を、この味で、この時間までに仕上げる」と決められたら、その通りに作り切る
  - 失敗したら自分で味を直して、合格ラインに達するまで続ける

両方を組み合わせると、**「考える人」と「作る人」**が分業した、現実的な開発体制になります。

---

## 2. Claude Code workflow とは何か（初心者向け解説）

`workflow` は、Claude Code に**大きな仕事を任せたいとき**に使う機能です。

普通の使い方だと、こんな感じです：

```
このコード改善して
```

これは、Claude が**一個ずつファイルを読んで、一個ずつ考えて、一個ずつ修正**します。小規模ならOK。

でも、ファイル数が多いリポジトリだと、これでは遅い。

そこで `workflow` を使うと、

```
Run a workflow to audit all API endpoints for missing authentication checks.
```

のように依頼できます。

すると Claude が、

1. タスクを**自動で分解**
2. 複数の**サブエージェント**に並列で調査を任せる
3. 結果を**統合**して返してくれる

という動きをします。

> 🔰 **サブエージェントって何？**
> Claude が裏で立ち上げる「お手伝いAI」のようなもの。本体の Claude が指示役になり、サブエージェントが手足になって動きます。

### workflow が向いている場面

- ✅ 大規模リポジトリの調査
- ✅ 影響範囲を広く分析したい
- ✅ 複数の観点（UI・API・DB・セキュリティ）を同時にチェックしたい
- ✅ 実装方針を比較検討したい

### workflow が向かない場面

- ❌ 小さなバグ修正
- ❌ 1ファイルの編集
- ❌ 完成条件が明確な実装

---

## 3. Codex /goal とは何か（初心者向け解説）

`/goal` は Codex の機能で、**「この状態になるまで進めて」**とゴールを設定する機能です。

普通のプロンプトとの違いは、**「いつ終わるか」**が明確なところ。

| 普通の指示 | /goal を使った指示 |
|---|---|
| 「このバグ直して」 | 「ログイン失敗時にエラーメッセージが表示され、テストが全部通る状態にして」 |
| AIは1回提案して終わり | AIは合格条件を満たすまで作業を続ける |

> 🔰 **/goal を使うのに事前設定が要る場合**
> もし `/goal` がスラッシュコマンド一覧に出てこないときは、`config.toml` の `[features]` で `goals = true` を有効にする必要があります（[出典：Codex 公式ドキュメント](https://developers.openai.com/codex/app/commands)）。

```toml
[features]
goals = true
```

または CLI で：

```bash
codex features enable goals
```

### /goal の動き方

Codex は `/goal` を渡されると、こう動きます：

```
現状確認
↓
原因調査
↓
修正
↓
テスト
↓
失敗したら再修正
↓
完了条件を満たしたら終了
```

つまり、**「完了条件つきの作業指示」**になっているのが核です。

---

## 4. 2つを組み合わせる実用フロー

ここからが本記事の肝です。

```
STEP 1: Claude Code workflow で全体を調査
STEP 2: Claude Code に SPEC.md を作らせる
STEP 3: Claude Code に GOAL.md を作らせる
STEP 4: 人間が GOAL.md を確認
STEP 5: Codex /goal に GOAL.md を渡す
STEP 6: Codex が実装・テスト・修正を回す
STEP 7: 人間が差分レビュー
```

### STEP 1：Claude Code で全体調査（編集なし）

```
Run a workflow to analyze this repository and propose an implementation plan for adding a dashboard feature.

Scope:
- src/
- app/
- components/
- api/

Output:
- Current architecture summary
- Files likely to be changed
- Implementation risks
- Recommended step-by-step plan

Do not modify any files
```

**ポイント**：最後に `Do not modify any files`（ファイル編集禁止）と書く。これだけでAIの暴走が大幅に減ります。

### STEP 2：SPEC.md を作らせる

調査が終わったら、仕様書を書かせます。

```
Based on the workflow analysis, create SPEC.md.

Include:
- Feature overview
- User story
- UI requirements
- API requirements
- Data model assumptions
- Error handling
- Non-goals
- Risks
- Verification plan
```

**ポイント**：「**Non-goals（やらないこと）**」を必ず書く。AI開発では「何をしないか」のほうが大事です。

例：

```
Non-goals:
- Do not redesign the entire UI
- Do not change the authentication system
- Do not modify the database schema unless necessary
```

### STEP 3：GOAL.md を作らせる

Codex に渡す指示書です。

```markdown
# Goal
管理画面に売上ダッシュボードを追加する

# Scope
Modify only:
- app/admin/dashboard/**
- components/dashboard/**
- app/api/sales/**

# Constraints
- Do not change authentication logic
- Do not modify unrelated pages
- Do not add new UI libraries

# Done when
- Admin users can view sales summary
- Daily sales chart is displayed
- npm test passes
- npm run lint passes
- No unrelated files are modified

# Verification
Run:
- npm test
- npm run lint
- npm run build
```

### STEP 4-7：Codex に渡して、人間がレビュー

```
/goal Please implement the feature described in GOAL.md.

Follow the scope and constraints strictly.
Before finishing, run:
- npm test
- npm run lint
- npm run build

If any command fails, fix the cause and rerun the verification.
Stop when all Done when conditions are satisfied.
```

これで Codex は「**合格条件を満たすまで続ける**」モードになります。

---

# 🎯 ここから本題：workflow と /goal 以外のおすすめコマンド集

ここからが、この記事のメインです。

Claude Code と Codex には、workflow や /goal 以外にも**たくさんの便利コマンド**があります。初心者は知らないと損なものを、特に厳選しました。

---

## 🌟 Claude Code のおすすめコマンド30選

### 【セッション管理系】

#### 1. `/clear` ─ 会話履歴をぜんぶ消す

新しい話題に切り替えるときに使います。Claude Code を再起動するより速い。

**こう使う**：

```
/clear
```

**ポイント**：会話履歴は消えるが、**ファイル変更は残る**ので安全。

#### 2. `/compact` ─ 会話を圧縮する

長く会話していると、コンテキスト（AIが覚えている会話量）が満杯になります。`/compact` を使うと、過去の会話を要約して圧縮してくれます。

**こう使う**：

```
/compact
```

または、何を残すか指定できます：

```
/compact retain the error handling patterns and the database schema
```

**目安**：コンテキスト使用率が80%を超えたら使う。

#### 3. `/context` ─ いま何%使っているか確認

```
/context
```

これでコンテキスト使用率を見られます。

#### 4. `/cost` ─ いまのセッションの料金を確認

```
/cost
```

API課金で使っている場合、これで使用料金を確認できます。月末に「あれ、こんなに使ってた…」を防げます。

#### 5. `/status` ─ いまの状態を見る

```
/status
```

使っているモデル、設定、コンテキスト状態などを一覧で確認できます。

---

### 【プロジェクト設定系】

#### 6. `/init` ─ プロジェクト初期化

リポジトリの直下で `/init` を実行すると、`CLAUDE.md` という設定ファイルが自動生成されます。

```
/init
```

> 🔰 **CLAUDE.md って何？**
> Claude が**毎回のセッション開始時に必ず読む**Markdown ファイル。プロジェクトの方針・コーディング規約・注意点などを書いておくと、毎回伝える必要がなくなります。

#### 7. `/memory` ─ CLAUDE.md を編集する

```
/memory
```

これでエディタが開いて、CLAUDE.md の中身を直接編集できます。

#### 8. `# テキスト` ─ メモを素早く追加

`/memory` を開かずに、その場でメモを追加できます。

```
# Use JWT tokens for authentication
# Follow React hooks conventions
# Write tests for all API endpoints
```

これだけで CLAUDE.md に自動追記されます。

#### 9. `/agents` ─ サブエージェントを管理

```
/agents
```

「コードレビュー専用のエージェント」「テスト書き専用のエージェント」など、目的別のエージェントを作って使い分けられます。

---

### 【コードレビュー系】

#### 10. `/review` ─ コードレビュー

```
/review
```

自分の書いたコードや、変更した内容をAIにレビューしてもらえます。

**おすすめ使い方**：PR を出す前に必ず実行。レビューワーに渡す前に整える。

#### 11. `/permissions` ─ Claude にどこまで許可するか設定

```
/permissions
```

「このコマンドは確認なしで実行OK」「このファイルは触らないで」など、Claude の権限を細かく設定できます。

> ⚠️ **大規模プロジェクトでは必須**
> 何でもかんでも許可すると、思わぬファイルが書き換えられます。最初は厳しめに、慣れたら緩めるのが安全。

---

### 【ファイル参照系】

#### 12. `@パス` ─ ファイルを参照する

会話の中で、特定のファイルを指定できます。

```
@src/auth/login.ts の認証ロジックを見直してほしい
```

**Tab補完が効く**ので、長いパスでも楽。

#### 13. `! コマンド` ─ シェルコマンドを直接実行

```
!ls
!git status
!npm test
```

`!` をつけるだけで、ターミナルのコマンドを実行できます。結果が会話に取り込まれるので、AI が状況を理解しやすくなります。

---

### 【セッション操作系】

#### 14. `claude -c` ─ 前回の続きから再開

ターミナルを閉じても、前回のセッションを継続できます。

```
claude -c
```

**こんな場面で**：「昨日のインシデント調査の続きから再開したい」

#### 15. `claude --resume` ─ 過去セッションから再開

```
claude --resume
```

過去のセッション一覧から選んで再開できます。

#### 16. `Esc Esc` ─ 前のメッセージに戻る

Esc を2回押すと、過去のメッセージに戻ってフォークできます。

「あ、この一個前の判断、間違ってた」というときに便利。

#### 17. `Ctrl+R` ─ 履歴検索

過去のコマンドを検索できます。

#### 18. `Shift+Tab` ─ モード切り替え

Claude のモード（通常／思考強化）を切り替えられます。

---

### 【モデル・設定系】

#### 19. `/model` ─ モデル切り替え

```
/model
```

軽量モデル（Haiku）と高性能モデル（Sonnet, Opus）を切り替えられます。

**使い分け**：

| 場面 | おすすめモデル |
|---|---|
| 単純な作業（リネーム、フォーマット） | Haiku（速い・安い） |
| ふつうのコーディング | Sonnet |
| 複雑な設計・大規模分析 | Opus |

#### 20. `/help` ─ ヘルプ

```
/help
```

全コマンド一覧が出ます。**迷ったらこれ**。

---

### 【拡張系】

#### 21. `/skills` ─ スキルを管理

スキル（特定分野の知識セット）を読み込ませる機能です。

```
/skills
```

#### 22. `/agents` ─ サブエージェント管理

特定タスク用のエージェントを作って管理できます。

#### 23. カスタム slash command を作る

`.claude/commands/` の下に Markdown ファイルを置くと、独自のスラッシュコマンドが作れます。

例：`.claude/commands/refactor.md`

```markdown
---
description: コードをリファクタリング
---

このファイルを以下の観点でリファクタリングしてください：
- 単一責任の原則
- 命名の改善
- テスト追加
```

これで `/refactor` というコマンドが使えるようになります。

#### 24. `/mcp` ─ MCP サーバー管理

MCP（Model Context Protocol）= 外部ツールとの連携。GitHub・Slack・Atlassian などと接続できます。

```
/mcp
```

---

### 【便利テクニック】

#### 25. Plan モード（Shift+Tab で切替）

実行前に「**まず計画を立てる**」モードに切り替えられます。

「いきなり書き始めず、まずプランを示してください」と言わなくても、Plan モードに入ればAIは計画段階で止まってくれます。

#### 26. 画像を貼り付ける

スクリーンショットを撮ってそのまま貼り付けると、Claude が解析してくれます。

「このエラー画面、何が起きてる？」と画像を貼るだけでOK。

#### 27. `claude --cd <path>` ─ 別ディレクトリで起動

```
claude --cd ./frontend
```

**こんな場面で**：モノレポで特定のサブプロジェクトだけ作業したい。

#### 28. 並列でセッションを立ち上げる

複数のターミナルで Claude Code を別々に立ち上げて、別タスクを並行で進められます。

#### 29. `/feedback` ─ フィードバックを送信

```
/feedback
```

Anthropic にバグや要望を直接送れます。

#### 30. `/quit` または `/exit` ─ 終了

```
/quit
```

これで終了。

---

## 🚀 Codex のおすすめコマンド10選

### 1. `/plan` ─ プランモード

```
/plan
```

`/goal` を作る前に、まずプランを練るモード。完成条件が曖昧なときは `/plan` から始めるのがおすすめ。

**典型的な流れ**：

```
/plan → 内容を Codex と整理 → /goal でゴール確定 → 実行
```

### 2. `/model` ─ モデル切り替え

```
/model
```

GPT-5 など、使うモデルを切り替えられます。

### 3. `/review` ─ コードレビュー

```
/review
```

`git diff` や指定ブランチとの差分をレビューします。

### 4. `/diff` ─ 差分確認

```
/diff
```

何が変更されたか、コミット前に確認。

### 5. `/permissions` ─ 権限設定

```
/permissions
```

Codex がどこまで自動実行していいかの設定。

**プリセット例**：

- `read-only`：読むだけ
- `workspace-write`：ワークスペース内のみ書き込みOK
- `danger-full-access`：何でもOK（**危険**）

> ⚠️ **danger-full-access は基本使わない**
> サンドボックス（隔離環境）でのみ使う。公式ドキュメントも明確に警告しています（[出典：Codex CLI Slash Commands](https://developers.openai.com/codex/cli/slash-commands)）。

### 6. `/approve` ─ 拒否されたアクションを再試行

自動レビューに弾かれたアクションを、もう一度試したいときに使います。

```
/approve
```

### 7. `/status` ─ 状態確認

```
/status
```

スレッドID、コンテキスト使用率、レート制限の状況がわかります。

### 8. `/memories` ─ メモリ管理

```
/memories
```

Codex の長期メモリの設定。

### 9. `/skills` ─ スキル選択

```
/skills
```

特定のスキルを適用できます。

### 10. `/feedback` ─ フィードバック

```
/feedback
```

OpenAI に直接フィードバックを送れます。

---

## 🎁 さらに便利な Codex のテクニック

### `!` シェルコマンド実行

Codex でも、プロンプトの頭に `!` をつけるとシェルコマンドが実行できます。

```
!npm test
!git status
```

### Tab でコマンドをキューに入れる

Codex が作業中でも、次の作業を**先取りで指示**できます。`/review` を入力して Tab を押すと、現在のタスクが終わった直後に `/review` が実行されます。

### `/goal` の文字数制限

`/goal` の本文は**最大 4,000 文字**。それ以上長い場合は、ファイル（GOAL.md）に書いて参照させましょう（[出典：Codex CLI Slash Commands](https://developers.openai.com/codex/cli/slash-commands)）。

---

## 🚨 初心者がハマる落とし穴 5つ

### 落とし穴① いきなり編集させる

Claude Code に最初から `「コード直して」` と頼むと、思わぬ範囲に手を入れられます。

**対策**：最初は必ず `Do not modify any files` で調査だけさせる。

### 落とし穴② スコープを絞らない

「アプリ全体を改善して」のような広いスコープは危険。

**対策**：

```
Scope:
- app/admin/dashboard/**
- components/dashboard/**
のみ
```

のように、対象範囲を必ず限定する。

### 落とし穴③ 完了条件を書かない

「いい感じにして」と頼むと、AIは「いつ終わればいいか」がわからずダラダラと作業を続けます。

**対策**：必ず `Done when:` を書く。

```
Done when:
- npm test が通る
- npm run lint が通る
- npm run build が通る
- 関係ないファイルが変更されていない
```

### 落とし穴④ レビューを省く

AIに任せた結果をそのままマージするのは危険。

**対策**：必ず人間が以下を確認：
- 関係ないファイルが変更されていないか
- 認証・権限まわりを壊していないか
- DB スキーマを勝手に変えていないか
- 新しい依存パッケージを勝手に追加していないか
- テストが本当に意味のあるものになっているか

### 落とし穴⑤ `danger-full-access` を本番環境で使う

Codex の `danger-full-access` や Claude Code で全権限を渡すモードは、**サンドボックス環境でのみ**使いましょう。

**対策**：本番に近い環境では `workspace-write` 以下の権限に絞る。

---

## ✅ 最初に覚えるべきコマンド「TOP 10」

全部を一度に覚えるのは無理。まずはこの10個から始めましょう。

### Claude Code

| 優先度 | コマンド | 目的 |
|---|---|---|
| ⭐⭐⭐ | `/init` | プロジェクト初期化 |
| ⭐⭐⭐ | `/clear` | 話題切り替え |
| ⭐⭐⭐ | `/compact` | 長い会話の圧縮 |
| ⭐⭐ | `/memory` | CLAUDE.md 編集 |
| ⭐⭐ | `/review` | コードレビュー |
| ⭐⭐ | `@パス` | ファイル参照 |
| ⭐ | `/status` | 状態確認 |

### Codex

| 優先度 | コマンド | 目的 |
|---|---|---|
| ⭐⭐⭐ | `/plan` | プラン作成 |
| ⭐⭐⭐ | `/goal` | ゴール設定 |
| ⭐⭐ | `/review` | コードレビュー |

---

## 🎯 おすすめ運用シーケンス（実例）

具体的なシナリオで、コマンドの使い方を見てみます。

### シナリオ：ポートフォリオサイトに投資分析ページを追加したい

```
[1] cd ~/projects/portfolio
[2] claude
[3] /init
    → CLAUDE.md が自動生成される
[4] CLAUDE.md に方針を書く（プロジェクトの特徴・規約）
[5] /memory で確認
[6] @app/page.tsx で既存実装を読ませる
[7] workflow で全体調査
[8] SPEC.md と GOAL.md を作らせる
[9] /clear で会話をリセット
[10] Claude Code を終了して Codex を起動
[11] /plan で計画整理
[12] /goal で GOAL.md を渡す
[13] Codex が実装→テスト→修正
[14] /diff で差分確認
[15] /review でセルフレビュー
[16] 人間が最終レビュー → コミット
```

これが、私が今いちばん安定してると感じている流れです。

---

## 🎯 まとめ

Claude Code と Codex は、**役割分担**で使うと真価が発揮されます。

```
Claude Code workflow
= 大きな課題を分解・調査する設計係

Codex /goal
= 明確な完成状態に向かって実装を回す実装係
```

そして、それ以外にもたくさんの便利コマンドがあります。

特に初心者が真っ先に覚えるべきは、

- `/init` ─ プロジェクト初期化
- `/clear` ─ 話題切り替え
- `/compact` ─ 会話の圧縮
- `/memory` ─ プロジェクト方針の管理
- `/review` ─ コードレビュー
- `/plan` ─ プラン作成
- `/goal` ─ ゴール設定

この7つから始めて、慣れたら少しずつ広げていくのがおすすめです。

そして、**「AIに任せる前に、何を任せるかを整理する」**こと。これがいちばん大事です。

AI開発が苦手な人は、たいてい**任せる前の整理が雑**です。

`workflow` で整理して、`SPEC.md` と `GOAL.md` を作って、`/goal` に渡す。

このフローを身につければ、AI開発はかなり安定します。

---

## 📚 参考資料（一次情報）

### Claude Code

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code Slash Commands - 公式](https://code.claude.com/docs/en/agent-sdk/slash-commands)
- [Claude Code Slash Commands - SDK](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-slash-commands)

### Codex

- [Codex 公式ドキュメント](https://developers.openai.com/codex)
- [Codex CLI Slash Commands](https://developers.openai.com/codex/cli/slash-commands)
- [Codex IDE Slash Commands](https://developers.openai.com/codex/ide/slash-commands)
- [Codex App Commands](https://developers.openai.com/codex/app/commands)
- [Codex Changelog](https://developers.openai.com/codex/changelog)
- [Codex CLI Features](https://developers.openai.com/codex/cli/features)

---

## ⚠️ 免責

この記事は筆者の現時点での個人的見解です。

- AI開発ツールは進化が速く、コマンドや仕様は頻繁に更新されます。**必ず公式ドキュメントを参照してください**
- 業務利用する場合は、**情報セキュリティ部門・顧問弁護士**と相談したうえで導入してください
- 筆者は、この記事の内容を実際の業務で使われたことに起因するいかなる損害についても責任を負いません

---

## 著者プロフィール

**臨床工学技士 × AIエンジニア**

11年間、病院の医療機器の現場に立ち続けてきました。
いまはAIエンジニアとしても活動しながら、酪農学園大学の研究生として論文博士の取得を目指しています。
研究テーマの主軸は遺伝子医療の未来。
そのうえで、医療現場と地続きにある病院のIT・サイバーセキュリティ・医療AI導入についても、現場で起きている課題と一次情報を突き合わせながら調べ続けています。

質問・誤りの指摘・「うちのチームではこう使っている」という事例の共有、いつでも歓迎します。

X：[@endoh_taichi](https://x.com/endoh_taichi)
Qiita：[@TaichiEndoh](https://qiita.com/TaichiEndoh)
