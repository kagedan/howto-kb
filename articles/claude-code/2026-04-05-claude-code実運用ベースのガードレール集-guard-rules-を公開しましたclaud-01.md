---
id: "2026-04-05-claude-code実運用ベースのガードレール集-guard-rules-を公開しましたclaud-01"
title: "Claude Code実運用ベースのガードレール集 guard-rules を公開しました——Claude Codeで実際に起きた事故と対策"
url: "https://zenn.dev/76hata/articles/claude-code-guard-rules-accident-lessons"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## この記事で分かること

* **CLAUDE.mdだけではAIのルール逸脱を防げない** 構造的な理由
* 実際の本番運用で起きた **事故・未遂の具体例** とその根本原因
* **3層制御アーキテクチャ** （CLAUDE.md + rules + Hooks）によるガードレール設計
* 収録されたすべてのHook・ルールファイルの **役割・仕組み・設計思想**
* 事故の教訓から生まれたOSS「[claude-code\_guard-rules](https://github.com/76Hata/claude-code_guard-rules)」の使い方

---

**Xのフォロー、いいねもよろしくお願いします。相互フォロー大歓迎です！**  
[Xアカウント(Code Bond)](https://x.com/code_bond_agent)

---

<https://github.com/76Hata/claude-code_guard-rules>

---

## はじめに

「このルールは絶対に守ってください」と書いたのに、Claude Codeがそのルールを無視した——そんな経験はありませんか？

筆者はClaude Codeを使ったナレッジアシスタントシステム（KA）を約1ヶ月半本番運用してきました。その間、**CLAUDE.mdに書いたはずのルールが破られる事故** が複数回発生しました。設定ファイルのサイレント上書き、Dockerビルド後の報告漏れ、明確な指示でもなぜか「確認で止まる」問題……。

これらの事故・未遂を分析して生まれたのが、汎用ガードレール集「 **claude-code\_guard-rules** 」です。本記事では事故の実録とともに、このOSSの設計思想・各ファイルの詳細な仕組みを紹介します。「なぜその仕組みが必要なのか」を理解することで、自分のプロジェクトへの応用も容易になるはずです。

---

## 前提知識：CLAUDE.mdとHooksの違い

本題に入る前に、基本的な2つの仕組みを整理します。

| 仕組み | 役割 | 保証レベル |
| --- | --- | --- |
| **CLAUDE.md** | LLMへのガイドライン（コンテキスト注入） | **保証なし** （守られることが多いが例外あり） |
| **Hooks** | シェルスクリプトによるシステム的強制 | **高い** （AIが「忘れても」必ず発火） |

たとえ話をすると、CLAUDE.mdは「この部屋では静かにしてください」という貼り紙、Hooksは「大きな声を出すとアラームが鳴る」センサーです。前者は読んでもらえれば守られますが、後者は物理的に強制します。

さらに言えば、Hooksにはいくつかの **発火タイミング（イベント）** があり、それぞれ用途が異なります：

| イベント | 発火タイミング | 主な用途 |
| --- | --- | --- |
| `SessionStart` | セッション開始時（1回のみ） | 共通コンテキストの注入 |
| `UserPromptSubmit` | ユーザーが入力を送信するたび | プロンプト内容に応じたルール追加 |
| `PreToolUse` | ツール実行直前 | 危険な操作の事前チェック・警告 |
| `PostToolUse` | ツール実行直後 | 実行後の検証・リマインダー |
| `Stop` | Claudeの応答完了時 | 完了後のチェック・通知 |

この豊富なイベント体系こそが、Hooksを強力なガードレールたらしめる理由です。

---

## 実際に起きた事故4選

### 事故1：設定ファイルのサイレント上書き

**何が起きたか** : config.jsonの設定値を、確認なしにデフォルト値でリセットされた。  
**根本原因** : 「変更前に確認する」ルールはCLAUDE.mdに書いていたが、長いセッションの途中でルールの優先度が下がった。  
**生まれた対策** : `config-change.md`（設定ファイル変更時の必須確認ルール）

```
<!-- .claude/rules/config-change.md -->
---
description: 設定ファイル変更時は必ずユーザー確認を取る
alwaysApply: false
paths: ["**/*.json", "**/*.yaml", "**/*.toml", "**/*.env*"]
---

# 設定ファイル変更ルール
- 既存の値を上書きする前に、現在の値と変更後の値を明示してユーザーに確認する
- NEVER: 確認なしに設定値をデフォルトに戻す
```

### 事故2：Dockerビルド後の報告漏れ

**何が起きたか** : コードを修正したが、Dockerを再ビルド・再起動せずに「直りました」と報告。本番は古いコードのままだった。  
**根本原因** : タスク完了の定義が曖昧。コード修正完了≠動作確認完了だが、AIはそれを意識しなかった。  
**生まれた対策** : `commit-reminder.sh`（Stop Hookでセッション終了時に未コミット変更を検知）

### 事故3：「確認で止まる」問題

**何が起きたか** : 「〇〇を実行してください」という明確な指示なのに、「どのような作業をご依頼いただけますか？」で処理が止まり続けた。  
**根本原因** : CLAUDE.mdに「作業前に必ず確認する」と書いたルールが過剰に適用された。適用範囲の定義が曖昧だったため、すべての指示を「確認が必要」と解釈した。  
**生まれた対策** : ルールの適用範囲を「曖昧な指示・破壊的操作・不明点がある場合のみ」に限定する記述に修正。加えて`prompt-guard.sh`で文脈に応じたルール注入を実装し、「常に全ルールをコンテキストに載せる」状態を避けるようにした。

### 事故4：Bashコマンドのタイムアウト未設定

**何が起きたか** : `docker build`等の時間のかかるコマンドがデフォルトの2分でタイムアウトし、中途半端な状態で処理が止まった。  
**根本原因** : Claude CodeのBashツールはデフォルト2分のタイムアウトがあるが、その仕様を知らずに運用していた。  
**生まれた対策** : `bash-timeout.md`（コマンド種別ごとのタイムアウト設定ガイド）

---

## 3層制御アーキテクチャ

事故の分析から見えてきたのは、「1つの仕組みだけに頼ってはいけない」という教訓です。

* **L1 CLAUDE.md** : 全体的な行動指針。短く・明確に書くほど守られやすい
* **L2 rules/\*.md** : `paths:`フロントマターで条件付き適用。トークン節約と精度向上
* **L3 Hooks** : 判断をAIに委ねない。スクリプトで機械的に強制する

**重要な原則** : 「3層が同じことを言って初めて『毎回守る』が実現する」。HookだけだとAIが文脈を理解しない。CLAUDE.mdだけだと忘れる。両方が同じルールを参照することで、どちらを先に読んでも同じ結論に至る。

---

## guard-rules キットの中身

[claude-code\_guard-rules](https://github.com/76Hata/claude-code_guard-rules)には、上記の事故教訓から生まれたルール・Hookが収録されています。

### ディレクトリ構成

```
claude-rules/
├── README.md                    ← このファイル
│
├── global/                      ← 全プロジェクト共通（~/.claude/ に展開）
│   ├── CLAUDE.md                ← ~/.claude/CLAUDE.md に追記するグローバルルール
│   └── .claude/
│       └── rules/               ← ~/.claude/rules/ に展開
│           ├── bash-timeout.md      ← 長時間コマンドのタイムアウト対策
│           └── config-change.md     ← 設定ファイル変更前の確認手順（paths: フィルタ付き）
│
├── project/                     ← プロジェクト固有（PROJECT_ROOT/ に展開）
│   ├── CLAUDE.md                ← PROJECT/CLAUDE.md に追記するプロジェクトルール
│   ├── .claude/
│   │   └── rules/               ← PROJECT/.claude/rules/ に展開
│   │       ├── git-workflow.md      ← Gitflowルール詳細（prompt-guard.sh が自動注入）
│   │       └── destructive-ops.md  ← 破壊的操作の確認手順（prompt-guard.sh が自動注入）
│   └── hooks/                   ← プロジェクト固有Hookの定義例
│       ├── python-quality-gate.sh  ← Python (.py) 編集後の ruff 自動チェック
│       └── settings.json           ← プロジェクト固有設定の定義例（.claude/settings.json に置く）
│
└── hooks/                       ← グローバルHook（~/.claude/hooks/ に展開）
    ├── README.md                    ← Hooks 設置手順
    ├── settings.template.json       ← ~/.claude/settings.json のテンプレート
    ├── session-start.sh             ← SessionStart: 共通コンテキスト注入（キャッシュ有効）
    ├── prompt-guard.sh              ← UserPromptSubmit: キーワード別ルール注入
    ├── explain-risk.js              ← PreToolUse: 破壊的操作のリスク可視化（Node.js）
    └── commit-reminder.sh           ← Stop: 未コミット変更の検知・警告
```

---

## 収録Hookの詳細解説

このキットが他のガードレール集と一線を画す理由は、 **すべてのHookイベントをカバーしていること** です。各Hookの設計思想を詳しく見ていきましょう。

---

### session-start.sh — セッション開始時の共通コンテキスト注入

**イベント** : `SessionStart`（新規セッション開始時に1回だけ発火）

```
# hooks/session-start.sh の動作概要
# - プロジェクト名・日付・基本的な行動指針をセッション冒頭に注入
# - Claude Code のプロンプトキャッシュ機能と組み合わせてトークンコストを削減
```

**なぜ必要か** : Claude Codeはセッションごとに記憶がリセットされます。毎回同じ「おまじない」をCLAUDE.mdだけで賄おうとすると、CLAUDE.mdが肥大化してトークンを圧迫します。`SessionStart`フックを使えば、 **毎回確実に・効率よく** 基本コンテキストを注入できます。

**設計の妙** : Claude Codeにはプロンプトキャッシュ機能があり、冒頭の固定テキストはキャッシュされてコストが下がります。`session-start.sh`はこの仕組みを活用するため、**変化しない情報** （プロジェクト概要、不変のルール等）を冒頭に集中させる構成になっています。

---

### prompt-guard.sh — プロンプト内容を見てルールを動的注入

**イベント** : `UserPromptSubmit`（ユーザーが入力を送信するたびに発火）

**動作** :

1. ユーザーのプロンプトを受け取る
2. キーワードを検出（例: "git push", "削除", "deploy", "migrate"）
3. 該当するルールファイルをコンテキストに追加注入する

```
# prompt-guard.sh の概念的な動作
PROMPT="$CLAUDE_USER_PROMPT"

if echo "$PROMPT" | grep -qiE "git (push|merge|rebase|reset)"; then
  cat ~/.claude/rules/git-workflow.md  # Gitflowルールを注入
fi

if echo "$PROMPT" | grep -qiE "削除|drop|truncate|rm -rf"; then
  cat ~/.claude/rules/destructive-ops.md  # 破壊的操作ルールを注入
fi
```

**なぜ重要か** : これが「スマートなコンテキスト注入」の核心です。すべてのルールを常時CLAUDE.mdに書き続けると、コンテキストウィンドウが圧迫され、かえってAIの判断精度が下がります。 **必要なときだけ、必要なルールを注入する** という方式により、精度とトークン効率を両立します。

`git-workflow.md`と`destructive-ops.md`が`project/.claude/rules/`に分離されているのはこのためです。常時読み込みではなく、`prompt-guard.sh`経由でオンデマンドに注入されます。

---

### explain-risk.js — ツール実行前のリスク可視化（Node.js製）

**イベント** : `PreToolUse`（Claudeがツールを使用しようとする直前に発火）

このHookの最大の特徴は **Node.jsで書かれていること** です。シェルスクリプトでは難しいJSON操作（Claude Codeがツール実行前に渡すツール入力パラメータのパース）をNode.jsで行い、高精度なリスク判定を実現しています。

```
// explain-risk.js の概念的な動作
const toolInput = JSON.parse(process.env.TOOL_INPUT);
const toolName = process.env.TOOL_NAME;

const RISK_PATTERNS = [
  { pattern: /rm\s+-rf/i, level: 'CRITICAL', message: '再帰的削除コマンドです' },
  { pattern: /git push.*--force/i, level: 'HIGH', message: 'force pushは履歴を書き換えます' },
  { pattern: /DROP TABLE/i, level: 'CRITICAL', message: 'テーブルが完全に削除されます' },
  { pattern: />\s*[^\s]/i, level: 'MEDIUM', message: 'ファイルが上書きされます' },
];

// ツール実行前にリスクレベルを出力
// → Claudeがこの情報を「見て」から実行判断をする
```

**なぜ「可視化」が有効か** : HooksはAIの実行を強制停止する（exitコード非ゼロ）こともできますが、`explain-risk.js`は **停止ではなく可視化** を選んでいます。理由は、すべての`rm`や`git push --force`が悪いわけではないからです。リスクレベルを表示することで、AIが「この操作には注意が必要だと認識した上で実行しているか」を意識させます。本当に問題のある場合は`destructive-ops.md`のルールと組み合わせて確認ステップを踏ませる、という二段構えです。

---

### commit-reminder.sh — セッション終了時の未コミット検知

**イベント** : `Stop`（Claudeが応答を完了したタイミングで発火）

```
# commit-reminder.sh の動作概要
# git statusで未コミット変更を確認
# 変更があれば警告を出力してコミットを促す

UNCOMMITTED=$(git status --porcelain 2>/dev/null)
if [ -n "$UNCOMMITTED" ]; then
  echo "【警告】未コミットの変更があります。作業内容を保存するためにコミットを検討してください。"
  echo "$UNCOMMITTED"
fi
```

**なぜ`Stop`イベントか** : 事故2（Dockerビルド漏れ）から派生した問題意識として、「AIがタスクを完了した気になっている」状態を検知することが目的です。`PostToolUse`では個々のツール使用後にしか発火しませんが、`Stop`はClaude全体の応答完了後に発火するため、 **セッション全体の結果** をチェックするのに適しています。

---

### python-quality-gate.sh — Python編集後の自動品質チェック

**配置** : `project/hooks/`（プロジェクト固有Hook）  
**イベント** : `PostToolUse`（Write/Edit ツールでPythonファイルを編集した後）

```
# python-quality-gate.sh の動作概要
EDITED_FILE="$TOOL_RESULT_PATH"

if echo "$EDITED_FILE" | grep -q '\.py$'; then
  echo "--- Python品質チェック ---"
  ruff check "$EDITED_FILE" && echo "✅ ruffチェック通過" || echo "❌ ruffエラーあり（上記を修正してください）"
fi
```

**設計の考え方** : このHookが`project/hooks/`にある理由は、ruffの利用はPythonプロジェクトにしか意味がないためです。`hooks/`（グローバル）ではなくプロジェクト固有に置くことで、**必要なプロジェクトにだけ適用** できます。同じ発想で、JavaScriptプロジェクトなら`eslint`、Rustなら`cargo clippy`を叩くHookをプロジェクトごとに追加できます。

---

## 収録ルールファイルの詳細解説

Hookがシステム的な強制を担うのに対し、ルールファイル（`.claude/rules/*.md`）はAIへの **精密な行動指針** を担います。Claude Codeのrules形式は`alwaysApply`と`paths`フロントマターにより、 **適用条件を細かく制御** できるのが強みです。

---

### bash-timeout.md — 長時間コマンドのタイムアウト対策

**配置** : `global/.claude/rules/`（全プロジェクト共通）  
**適用** : `alwaysApply: true`

```
---
description: Bashコマンドのタイムアウト設定ガイド
alwaysApply: true
---

# Bashコマンドタイムアウト設定

Claude CodeのBashツールはデフォルト2分のタイムアウトがある。

## コマンド種別と推奨設定
- **高速コマンド** （ls, cat, grep等）: デフォルトのまま
- **中速コマンド** （テスト実行、pip install等）: timeout: 600000（10分）
- **低速コマンド** （docker build, npm install等）: run_in_background: true
```

このルールは全プロジェクトで共通して発生する問題のため、グローバルrules（`~/.claude/rules/`）に配置します。

---

### config-change.md — 設定ファイル変更前の確認手順

**配置** : `global/.claude/rules/`（全プロジェクト共通）  
**適用** : `alwaysApply: false`、`paths: ["**/*.json", "**/*.yaml", ...]`

```
---
description: 設定ファイル変更時は必ずユーザー確認を取る
alwaysApply: false
paths: ["**/*.json", "**/*.yaml", "**/*.toml", "**/*.env*"]
---

# 設定ファイル変更ルール
- 既存の値を上書きする前に、現在の値と変更後の値を明示してユーザーに確認する
- NEVER: 確認なしに設定値をデフォルトに戻す
- NEVER: コメントアウトされた設定を無断で削除する
```

**`paths:`フロントマターの威力** : このルールはJSONやYAMLを編集するときだけコンテキストに注入されます。Pythonファイルを書いているときには読み込まれません。これにより、 **関係ないタイミングでのトークン消費を防ぎつつ、必要なときに確実に適用** されます。

---

### git-workflow.md — Gitflowルール詳細

**配置** : `project/.claude/rules/`（プロジェクト固有）  
**適用** : `alwaysApply: false`（`prompt-guard.sh`が動的注入）

```
---
description: Gitブランチ戦略とコミット規約
alwaysApply: false
---

# Gitワークフロールール

## ブランチ戦略
- feature/* → develop にマージ
- develop → main へのマージはPR必須
- NEVER: mainへの直接push

## コミットメッセージ規約
- feat: / fix: / docs: / refactor: プレフィックスを使用
- 本文に変更理由を記述する

## 禁止操作
- git push --force（緊急時はチームに連絡してから）
- git reset --hard（作業中の変更がある場合）
```

このルールはプロジェクトごとにGitflowが異なるため、`project/.claude/rules/`に配置しています。`prompt-guard.sh`が「git」関連のキーワードを検出したときだけ注入するため、Gitと無関係な作業時にはコンテキストを汚染しません。

---

### destructive-ops.md — 破壊的操作の確認手順

**配置** : `project/.claude/rules/`（プロジェクト固有）  
**適用** : `alwaysApply: false`（`prompt-guard.sh`が動的注入）

```
---
description: 破壊的操作（削除・上書き・リセット）の確認手順
alwaysApply: false
---

# 破壊的操作ルール

## 対象操作
- ファイル/ディレクトリの削除
- データベースのDROP/TRUNCATE
- git reset --hard / git clean -fd

## 必須手順
1. 操作内容と影響範囲をユーザーに説明する
2. 「本当に実行しますか？」と明示的に確認を取る
3. バックアップが存在するか確認する
4. ユーザーの明示的な「はい」を得てから実行する
```

`explain-risk.js`（リスク可視化）と`destructive-ops.md`（確認手順ルール）は、セットで機能するように設計されています。前者がリスクを検知して「ここは危ない操作だ」とAIに認識させ、後者が「危ない操作のときはこう動け」という行動手順を与えます。

---

## 全コンポーネントの連携イメージ

このように、 **各コンポーネントがそれぞれの役割に集中しながら連携** することで、単一のHookやルールファイルでは実現できない多層防御が機能します。

---

## 3ステップ導入ガイド

```
# Step 1: リポジトリをクローン
git clone https://github.com/76Hata/claude-code_guard-rules.git
cd claude-code_guard-rules

# Step 2: グローバルルールとHooksを配置
mkdir -p ~/.claude/rules ~/.claude/hooks
cp -r global/.claude/rules/* ~/.claude/rules/
cp -r hooks/*.sh hooks/*.js ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh

# Step 3: settings.jsonにHooksを登録
# hooks/settings.template.json をベースに ~/.claude/settings.json を編集
```

```
// ~/.claude/settings.json（settings.template.json より）
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/session-start.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/prompt-guard.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node ~/.claude/hooks/explain-risk.js"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/commit-reminder.sh"
          }
        ]
      }
    ]
  }
}
```

プロジェクト固有のルールは `project/` 以下をプロジェクトルートにコピーしてください。

```
# プロジェクト固有ルールの配置
cp -r project/.claude PROJECT_ROOT/.claude
cp project/CLAUDE.md PROJECT_ROOT/CLAUDE.md  # 既存のCLAUDE.mdがある場合は追記
```

---

## 導入優先度

| 優先度 | ファイル | 防ぐ事故 | 種別 |
| --- | --- | --- | --- |
| ★★★ | `destructive-ops.md` | 設定上書き・ファイル削除 | ルール |
| ★★★ | `bash-timeout.md` | タイムアウト起因の中断 | ルール |
| ★★★ | `prompt-guard.sh` | ルール注入漏れ・コンテキスト汚染 | Hook |
| ★★★ | `explain-risk.js` | 破壊的操作の無自覚実行 | Hook |
| ★★☆ | `commit-reminder.sh` | ビルド漏れ・旧コードのまま動作 | Hook |
| ★★☆ | `config-change.md` | 設定値サイレント上書き | ルール |
| ★★☆ | `session-start.sh` | セッションごとのコンテキスト再構築コスト | Hook |
| ★☆☆ | `git-workflow.md` | 手順飛ばしによるGit事故 | ルール |
| ★☆☆ | `python-quality-gate.sh` | コード品質の劣化 | Hook（プロジェクト固有） |

---

## よくある落とし穴

### 「CLAUDE.mdに書いたから大丈夫」は危険

最も多いミスです。CLAUDE.mdは **コンテキストウィンドウに注入されるテキスト** に過ぎません。セッションが長くなればなるほど、初期に注入されたルールの「重み」が相対的に下がります。重要なルールはHookでも強制してください。

### Hookの過剰な使用

逆に、すべてをHookで制御しようとするのも問題です。HooksはシェルスクリプトなのでLLMの文脈を理解できません。「こういう状況では例外」という判断が必要なルールはCLAUDE.mdで書き、機械的に強制できるものだけHookにするのが原則です。`prompt-guard.sh`のようにキーワードベースで条件分岐するのがバランスの良い実装です。

### ルールの重複と矛盾

CLAUDE.mdとrules/配下で同じことを書くときは、 **必ず同じ表現にする** 。微妙に違う表現をすると、Claudeが「どちらが正しいルールか」と混乱し、予期しない解釈をすることがあります。

`explain-risk.js`はあえてブロックではなく「可視化」を選んでいます。すべての危険に見える操作を機械的にブロックすると、正当な操作もできなくなります。 **AIの判断を止めるのではなく、判断に必要な情報を与える** という設計思想を覚えておいてください。exitコード非ゼロでの強制停止は、本当に許容できないケース（例: production DBへの直接接続）だけに留めましょう。

### settings.jsonのHook登録忘れ

ファイルを配置しただけではHookは動きません。 **必ず`settings.json`に登録する** 必要があります。`settings.template.json`をそのままコピーして使うことで、この漏れを防げます。

---

## まとめ

Claude Codeの本番運用で学んだ最大の教訓は、「 **ルールを守らせるのではなく、守らざるを得ない仕組みを作る** 」です。

| 層 | 仕組み | 特性 |
| --- | --- | --- |
| L1 | CLAUDE.md | お願い（破られることがある） |
| L2 | rules/\*.md | 条件付き精密指示（トークン効率◎） |
| L3 | Hooks | 物理的な壁（忘れても必ず発動） |

本キットの特徴をまとめると：

* **全イベントカバー** : SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop すべてに対応
* **スマート注入** : `prompt-guard.sh`でキーワードベースのオンデマンドルール注入
* **リスク可視化** : Node.jsを使った`explain-risk.js`で高精度なリスク判定
* **グローバル/プロジェクト分離** : 全プロジェクト共通と固有ルールを明確に分離

guard-rulesは今後も実運用の教訓をもとにアップデートしていく予定です。GitHubスター・Issue・PRをお待ちしています。

<https://github.com/76Hata/claude-code_guard-rules>

---

**Xのフォロー、いいねもよろしくお願いします。相互フォロー大歓迎です！**  
[Xアカウント(Code Bond)](https://x.com/code_bond_agent)

---

**関連記事:**

---

### こちらもよく読まれています
