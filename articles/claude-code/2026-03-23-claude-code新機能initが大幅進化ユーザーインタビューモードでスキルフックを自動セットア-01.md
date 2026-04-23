---
id: "2026-03-23-claude-code新機能initが大幅進化ユーザーインタビューモードでスキルフックを自動セットア-01"
title: "Claude Code新機能：「/init」が大幅進化！ユーザーインタビューモードでスキル・フックを自動セットアップ可能になりました"
url: "https://zenn.dev/truestar/articles/455e5b54f3368e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/59b29c37f103-20260323.png)

日本時間午前4時半頃、下記のX投稿が投下されており、非常に大きな反響がありました。AnthropicのClaude Codeツールの新機能「/init」を紹介しており、ユーザーのフィードバックに基づき、リポジトリのスキルやフック設定をインタビュー形式で自動化するものです。

<https://x.com/trq212/status/2035799806640115806>

私個人も最近、Claude Codeのベストプラクティスを読み漁りながら「理想のプロジェクト構成とはどういうものなのだろうか」を追い求めて自分なりのテンプレートを作ろうと思っていたところでしたので、これは！と早速飛び付いてみた次第です。当エントリでは実際にこの`/init`コマンドを実践してみた内容を備忘録として残しておこうと思います。

## 環境変数設定

X投稿にもあるように、この手順は予め指定の環境変数を用意し、値を設定しておく必要があります。設定する内容は以下の通り。値は下記例では`1`を指定していますが、実際は`1`または`true`いずれの場合でも有効です。

`CLAUDE_CODE_NEW_INIT=1`

設定する方法は幾つかあります。

### 1.ターミナルログイン時に都度指定

Claude Code起動時に以下の形式で設定することが可能です。

```
CLAUDE_CODE_NEW_INIT=1 claude
```

### 2. settings.jsonに値を設定

`~/.claude/settings.json`(グローバル指定の場合)、または`.claude/settings.json`(プロジェクトのルートフォルダ/プロジェクト個別指定の場合)に以下の内容を追加することでも対応可能です。

~/.claude/settings.json

```
{
  :
  :
  "env": {
    "CLAUDE_CODE_NEW_INIT": "true"
  },
  :
  :
  "language": "ja",
  "voiceEnabled": true
}
```

## /init 実行による対話での設定、構築作業実践

上記設定後、Claude Code上で`/init`を実行。ここからは実行内容をポイントごとに画面キャプチャ、コンソール出力内容と共に見ていきます。

![](https://static.zenn.studio/user-upload/f8fe4f82badf-20260323.png)

セットアップ対象のファイルを指定。

```
どのCLAUDE.mdファイルをセットアップしますか？

❯ 1. Project CLAUDE.md
     チーム共有のプロジェクト指示書（ソース管理にコミット）— アーキテクチャ、コーディング規約、共通ワークフロー。
  2. Personal CLAUDE.local.md
     このプロジェクト向けの個人設定（gitignore、非共有）— 自分の役割、サンドボックスURL、好みのテストデータ、ワークフローの癖。
  3. 両方（Project + Personal） ✔
     プロジェクト共有の指示書と個人設定の両方を作成します。
  4. Type something.
  5. Chat about this
```

![](https://static.zenn.studio/user-upload/9309b251d11e-20260323.png)

追加設定。SkillとHookも併せて作るか聞かれます。

```
スキルとフックもセットアップしますか？

❯ 1. スキル + フック両方
     オンデマンドのワークフロースキル（/skill-name で呼び出し）と、ツールイベント時に自動実行するフックの両方を設定します。
  2. スキルのみ
     繰り返しのワークフローや参照知識のためのスキルのみ設定します。
  3. フックのみ
     編集後の自動フォーマットなど、決定的なシェルコマンドフックのみ設定します。
  4. なし（CLAUDE.mdのみ）
     CLAUDE.mdファイルのみセットアップします。
  5. Type something.
  6. Chat about this
```

![](https://static.zenn.studio/user-upload/6e53755e36e7-20260323.png)

プロジェクトの目的。何のためにこのプロジェクトを作るのか聞かれます。

```
プロジェクトの目的

このプロジェクト（claude-code-init-test）は何のためのプロジェクトですか？

❯ 1. Claude Code設定・初期化の実験場
     CLAUDE.md、スキル、フックなどClaude Codeの設定をテスト・実験する場所
  2. 新規アプリ/ツール開発の足がかり
     これから実際に何かを作り始めるためのプロジェクト起点
  3. Claude Codeワークフローの学習
     Claude Codeの使い方を学習・習得するためのプレイグラウンド
  4. まだ未定
     今はまだ決まっていない
  5. Type something.
```

![](https://static.zenn.studio/user-upload/80c5a019ccba-20260323.png)

技術スタック：プロジェクトで使用予定のスタック。

```
このプロジェクトで使用予定の技術スタックは？

❯ 1. [✔] Python
  Python（uvで管理）
  2. [ ] TypeScript/JavaScript
  Node.js系
  3. [ ] Rust
  Rust言語
  4. [ ] まだ未定/汎用
  技術スタックはまだ決まっていない
  5. [ ] Type something
  6. Chat about this
```

![](https://static.zenn.studio/user-upload/58c18336e837-20260323.png)

習熟度：自身のClaude Code、及び対する習熟度。

```
Claude Codeとこのプロジェクトに対するあなたの習熟度は？

❯ 1. 上級（設定・カスタマイズを深く理解）
     Claude Codeのフック、スキル、MCPなどの高度な設定を理解している
  2. 中級（日常的に使用している）
     Claude Codeを日常的に使っており、基本的な設定は理解済み
  3. 初級（使い始めたばかり）
     Claude Codeの学習中
  4. Type something.
  5. Chat about this
```

![](https://static.zenn.studio/user-upload/39569361a714-20260323.png)

コミュニケーション：Claudeとのコミュニケーションの方法粒度に関する質問。

```
Claudeとのコミュニケーションの好みは？

  1. 簡潔・要点のみ
     簡潔な回答、詳細な説明は不要
  2. トレードオフを説明してほしい
     選択肢やトレードオフの説明が欲しい
❯ 3. 段階的に詳しく説明
     詳細な説明とステップバイステップのガイダンスが好み
  4. 実装前にプランを提示
     実装に入る前に必ずアプローチを提示してほしい
  5. Type something.
  6. Chat about this
```

![](https://static.zenn.studio/user-upload/ce2dc39f83f1-20260323.png)

以上で質疑応答完了。選択、回答内容がまとめられ、これでOKなら作成するよとなります。内容的に問題無ければ1を選択して作成を進めます。

```
 ☐ 提案確認

この提案内容でよいですか？

❯ 1. 良い—作成してください        ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
 2. フックは不要（CLAUDE.md+ス    │ 設定ファイル:                                                                                    │
   キルのみ）                     │ • CLAUDE.md（プロジェクト共有）— WHY/WHAT/HOW構造、TypeScript+Pythonスタックの出発点             │
 3. スキルは不要（CLAUDE.md+フ    │ • CLAUDE.local.md（個人設定）— 中級ユーザー、段階的説明希望                                      │
   ックのみ）                     │ • .gitignore— CLAUDE.local.mdを追加                                                              │
                                  │                                                                                                  │
                                  │ スキル:                                                                                          │
                                  │ • /verify — lint+テストを実行して変更を検証（TypeScript: tsc+eslint、Python: ruff+pytest）       │
                                  │ • /setup-env — Python(uv)+TypeScript(npm/pnpm)の初期セットアップ手順ガイド                       │
                                  │                                                                                                  │
                                  │ フック:                                                                                          │
                                  │ • フォーマットオンエディット — Python: ruff format、TS: prettier（フォーマッター設定後に有効化） │
                                  └──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

![](https://static.zenn.studio/user-upload/80f3fae140b7-20260323.png)

以下、一通りのファイル一式が作成されるまでは以下のような感じで作業が進み、適宜「これで良いか？」とClaude Codeが聞いてきます。内容を確認し、先に進めてください。(※問題なければひたすら1を押下する流れになるかと)

```
Phase 4: CLAUDE.md 作成
Phase 5: CLAUDE.local.md 作成
Phase 6: スキル作成
Phase 7: フォーマットオンエディットフックの設定
ステップ1: dedup チェック
ステップ2: コマンド構築
ファイルパスを取得し、拡張子に応じて ruff（Python）または prettier（TypeScript/JavaScript）を実行するコマンドを構築します。
ステップ3: コマンド構築とパイプテスト
ruff/prettier がまだ未インストールのため、インストール後に動作するようグレースフルなコマンドを構築します。
ステップ4: settings.json 書き込み
ステップ5: JSON構文・スキーマ検証
ステップ6: フック発火の確認（センチネル方式）  
ステップ7: ハンドオフ
フックの JSON は正しく書き込まれています。ただし .claude/ ディレクトリはこのセッション開始後に作成されたため、Claude Code を再起動するか /hooks メニューを一度開くとフックが有効になります。
Phase 7: 追加最適化チェック
GitHub CLI は導入済み。
```

作成ステップが一通り完了すると、以下のような形でまとめステップの情報が表示されます。ユーザー自身が何をすれば良いのかの案内もちゃんとされていて安心ですね。

```
Phase 8: まとめと次のステップ

  以下のファイルを作成しました:

  ┌───────────────────────────────────┬─────────────────────────────────────────────────────┐
  │             ファイル              │                        内容                         │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ CLAUDE.md                         │ WHY/WHAT/HOW 構造、TypeScript+Python スタックの指示 │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ CLAUDE.local.md                   │ 個人設定（中級ユーザー、段階的説明希望）            │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ .gitignore                        │ CLAUDE.local.md、.venv/、node_modules/ 等を除外     │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ .claude/settings.json             │ フォーマットオンエディットフック（ruff/prettier）   │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ .claude/skills/verify/SKILL.md    │ /verify スキル — lint+テスト実行                    │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ .claude/skills/setup-env/SKILL.md │ /setup-env スキル — Python/TS 環境初期化ガイド      │
  └───────────────────────────────────┴─────────────────────────────────────────────────────┘

  重要: フックを有効にするには Claude Code を再起動するか /hooks を開いてください（このセッション中に .claude/ を作成したため）。

  ---
  追加で取り組むとよいこと

  1. フォーマッター/linterをセットアップする — /setup-env を実行して ruff（Python）と prettier（TypeScript）をインストールすると、フォーマットフックが自動で動作します。
  2. テストフレームワークを追加する — pytest（Python）と Jest/Vitest（TypeScript）を設定すると /verify が全てのチェックを実行できるようになります。
  3. CLAUDE.md の WHY セクションを記入する — プロジェクトの目的が決まったら [このプロジェクトが何を解決するか] を埋めてください。
  4. スキルの品質改善 — /plugin install skill-creator@claude-plugins-official でスキルを評価・改善できます。/skill-creator verify でスキルを洗練させることができます。
  5. 公式プラグインを探索する — /plugin でスキル・エージェント・フック・MCP サーバーをバンドルしたプラグインを確認できます。必要なものを追加してセットアップを強化してください。
```

![](https://static.zenn.studio/user-upload/f877b42c8d20-20260323.png)

## 作成された成果物の内容を確認

実際にどういう内容のファイルが作成されたのか、それぞれ見ていきましょう。一式内容はこんな感じになっています。

![](https://static.zenn.studio/user-upload/d77cfef37476-20260323.png)

ここからは作成されたファイル個別の内容をそのまま掲示します。

### .claude/settings.json

.claude/settings.json

```
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "f=$(jq -r '.tool_input.file_path // empty'); [ -z \"$f\" ] && exit 0; case \"$f\" in *.py) if [ -f \".venv/bin/ruff\" ]; then .venv/bin/ruff format \"$f\"; elif command -v ruff >/dev/null 2>&1; then ruff format \"$f\"; fi ;; *.ts|*.tsx|*.js|*.jsx|*.json|*.css) if [ -f \"node_modules/.bin/prettier\" ]; then node_modules/.bin/prettier --write \"$f\"; elif npx --no-install prettier --write \"$f\" 2>/dev/null; then :; fi ;; esac 2>/dev/null || true",
            "timeout": 30,
            "statusMessage": "フォーマット中..."
          }
        ]
      }
    ]
  }
}
```

### .claude/skills/setup-env/SKILL.md

.claude/skills/setup-env/SKILL.md

```
---
name: setup-env
description: Python(uv)とTypeScript(npm/pnpm)の開発環境を初期セットアップする手順をガイドする。新しい開発環境を構築するときに使う。
---

ユーザーが要求した言語/環境に応じてセットアップ手順を案内してください。

## Python 環境セットアップ（uv）

'''bash
# 1. 仮想環境の作成
uv venv .venv

# 2. 仮想環境の有効化
source .venv/bin/activate

# 3a. パッケージのインストール（requirements.txt がある場合）
uv pip install -r requirements.txt

# 3b. pyproject.toml 管理のプロジェクトの場合
uv add <package>

# 4. 開発用ツールの追加（必要に応じて）
uv add --dev ruff pytest
'''

注意: pip installx / conda / poetry は使用禁止。uv のみを使うこと。

 ## TypeScript/JavaScript 環境セットアップ

'''bash
# 1. package.json の初期化（新規プロジェクトの場合）
npm init -y   # または pnpm init

# 2. TypeScript のセットアップ
npm install --save-dev typescript @types/node
npx tsc --init

# 3. 開発用ツール（任意）
npm install --save-dev eslint prettier

# 4. 依存関係のインストール
npm install   # または pnpm install
'''

## ruff 設定（Python）

`pyproject.toml` に以下を追加:

'''toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I"]
'''

## prettier 設定（TypeScript）

`.prettierrc` を作成:

'''json
{
  "singleQuote": true,
  "semi": true,
  "tabWidth": 2
}
'''

セットアップ完了後は `/verify` で動作確認してください。
```

### .claude/skills/verify/SKILL.md

.claude/skills/verify/SKILL.md

```
---
name: verify
description: lint・型チェック・テストを実行して変更を検証する。コードを変更した後、レビューや完了前に使う。
---

以下の手順で変更を検証してください。検出されたツールや設定に応じてステップをスキップしてよい。

## Python（存在する場合）

1. 仮想環境を確認: `.venv` があれば `source .venv/bin/activate`
2. lint: `ruff check .`
3. format チェック: `ruff format --check .`
4. テスト: `pytest` （`tests/` または `test_*.py` が存在する場合）

## TypeScript/JavaScript（存在する場合）

1. 型チェック: `npx tsc --noEmit`（`tsconfig.json` が存在する場合）
2. lint: `npm run lint`（`package.json` に `lint` スクリプトがある場合）
3. テスト: `npm test`（`package.json` に `test` スクリプトがある場合）

## 完了基準

すべてのチェックが通ったら「✓ 検証完了」と報告する。
エラーがあれば内容を段階的に説明し、修正方法を提案する。
```

### .gitignore

.gitignore

```
# Claude Code
.claude/settings.local.json
CLAUDE.local.md

# 環境変数
.env
.env.local
.env.*.local

# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.pytest_cache/
.ruff_cache/

# Node.js
node_modules/
dist/
.next/
.nuxt/

# OS
.DS_Store
Thumbs.db

# エディタ
.vscode/
.idea/
*.swp
*.swo
```

### CLAUDE.local.md

CLAUDE.local.md

```
# CLAUDE.local.md（個人設定・git管理外）

## 私の役割・習熟度

- Claude Code 中級ユーザー（日常的に使用）
- TypeScript/Python での開発経験あり

## コミュニケーション設定

- 回答は **段階的に詳しく説明**してほしい
- 選択肢やトレードオフを示す前に、まず実装アプローチを提示すること
- 実装に入る前に計画を確認すること
```

### CLAUDE.md

CLAUDE.md

```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# Project: claude-code-init-test

新規アプリ/ツール開発の起点となるプロジェクト。

---

## WHY（目的）

[このプロジェクトが何を解決するか・なぜ存在するかを記載]

---

## WHAT（構成）

### 技術スタック

- **Python**: パッケージ管理は `uv` のみ使用（pip/conda/poetry 禁止）
- **TypeScript/JavaScript**: Node.js 系（パッケージマネージャーは npm または pnpm）

### ディレクトリ構成

'''
[プロジェクト構成が決まったら記載]
'''

---

## HOW（作業方法）

### コマンド

'''bash
# Python セットアップ
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Python テスト
pytest

# Python lint/format
ruff check .
ruff format .

# TypeScript セットアップ
npm install   # または pnpm install

# TypeScript ビルド
npm run build

# TypeScript テスト
npm test

# TypeScript lint
npm run lint
'''

### ワークフロールール

- Python 作業前に必ず `.venv` を有効化してから実行する
- 実装前にアプローチを提示して確認を取る

### 注意事項（Gotchas）

- [決まったら記載]

---

## 参考ドキュメント

- アーキテクチャ: @docs/architecture.md
- 意思決定記録: @docs/decisions/
- 運用手順: @docs/runbooks/
```

## まとめ

という訳で、Claude Codeで新しく追加された`/init`コマンドの新機能(対話で情報を収集し、プロジェクトの初期雛形を構築)に関する紹介でした。プロジェクトで何をやるかがある程度見えている、技術スタックなども目星がついているという状況であればこれは実に便利な機能だなと思いました。作成される各種ファイルも「どういうことを書けば良いのか」が分かりやすく案内されていて良いですね。今後他の設定や項目に関しても充実してくれると個人的には嬉しいです。

---

## この記事を読んだ方へ

感想・フィードバックは X（[@shinyaa31](https://x.com/shinyaa31)）までお気軽にどうぞ。
