---
id: "2026-04-11-claude-code-skillsのドキュメントを全部読んだので本当に使える実装パターンだけ8個ま-01"
title: "Claude Code Skillsのドキュメントを全部読んだので、本当に使える実装パターンだけ8個まとめた"
url: "https://qiita.com/moha0918_/items/786b556a84052a564fb5"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

Claude Codeを使い込んでいると、チャットに同じ手順を何度もペーストしていることに気づきます。デプロイ手順、コードレビューのチェックリスト、PR作成のテンプレート。毎回書き直しているあれです。

Skillsはその繰り返しを断ち切るための仕組みですが、公式ドキュメントは機能の網羅が目的なので、「実際どう組み合わせると強いのか」という視点が薄い。

この記事では、ドキュメントを一通り読んで理解した上で、**現実のプロジェクトで即使えるパターン**だけを8個に絞って解説します。

対象読者: Claude Codeをある程度使っている方。Skillsの基本（`SKILL.md`を置くとスラッシュコマンドになる）は知っていることを前提にします。

## まず構造だけ把握する

Skillsを置ける場所は3つあります。

| 場所 | パス | 有効範囲 |
| --- | --- | --- |
| 個人 | `~/.claude/skills/<name>/SKILL.md` | 全プロジェクト |
| プロジェクト | `.claude/skills/<name>/SKILL.md` | そのプロジェクトのみ |
| 企業管理 | managed settings経由 | 組織全員 |

チームで共有したいなら `.claude/skills/` をgitにコミットする。自分だけが使うなら `~/.claude/skills/` に置く。この使い分けが基本です。

既存の `.claude/commands/` ディレクトリにあるファイルもそのまま動きます。移行は不要。

## パターン1: 手動専用のデプロイコマンド

Skillsで最初に設定すべきは、**Claudeに勝手に実行させたくないコマンド**です。

`disable-model-invocation: true` を付けると、Claudeはそのスキルを自律的に呼び出せなくなります。「コードが書き終わったから自動でデプロイしておきました」という事態を防げます。

```
# .claude/skills/deploy/SKILL.md
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
allowed-tools: Bash(npm *) Bash(git *)
---

Deploy $ARGUMENTS to production:

1. Run `npm test` — abort if any tests fail
2. Run `npm run build`
3. Confirm the build output looks correct
4. Run the deployment script: `./scripts/deploy.sh $ARGUMENTS`
5. Verify deployment by hitting the health endpoint
6. Report the deployed version and any warnings
```

`/deploy staging` や `/deploy production` のように引数で環境を指定できます。`allowed-tools` に書いたコマンドはこのスキル実行中に限り承認なしで動くので、手順の途中でいちいち確認ダイアログが出ません。

## パターン2: GitHubのIssue番号を渡すだけで修正まで完結

引数の受け渡しで、定型的な作業を大幅に短縮できます。

```
# .claude/skills/fix-issue/SKILL.md
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true
allowed-tools: Bash(gh *) Bash(git *)
---

Fix GitHub issue #$ARGUMENTS:

1. Fetch the issue: `gh issue view $ARGUMENTS`
2. Read the issue title, body, and comments carefully
3. Identify which files are likely involved
4. Implement the fix following the existing code style
5. Write or update tests to cover the change
6. Create a commit: `git commit -m "fix: resolve issue #$ARGUMENTS - <title>"`
7. Show a summary of what was changed and why
```

`/fix-issue 482` と打つだけで、IssueをGitHub CLIから取得して修正→コミットまで一気に実行します。

`gh` コマンドを `allowed-tools` に含めているので、途中でAPIコールの許可を求めてきません。

## パターン3: 背景知識だけを持たせるスキル

全てのスキルがスラッシュコマンドである必要はありません。**Claudeだけが参照する知識**として機能させることもできます。

```
# .claude/skills/our-api-conventions/SKILL.md
---
name: our-api-conventions
description: REST API design conventions for this codebase. Load when writing or reviewing API endpoints, controllers, or route handlers.
user-invocable: false
---

## API conventions for this project

### Endpoint naming
- Use kebab-case: `/user-profiles`, not `/userProfiles`
- Nest resources max 2 levels: `/users/{id}/posts`, not deeper
- Use plural nouns for collections

### Response format
Always return:
```json
{
  "data": {},
  "meta": { "timestamp": "", "version": "" },
  "errors": []
}
```

### Error codes

* 400: Validation failed (include field-level details)
* 401: Authentication required
* 403: Insufficient permissions (do not reveal resource existence)
* 422: Business rule violation

```
`user-invocable: false` を設定すると、`/our-api-conventions` というコマンドはメニューに出てきません。でもClaudeはAPIのコードを書く文脈でこの知識を自動で読み込み、プロジェクト固有のルールに従ったコードを書いてくれます。

CLAUDE.md に書いていたルールが長くなってきたら、こうやって個別のスキルに切り出すのがおすすめです。CLAUDE.md は常にコンテキストに読み込まれますが、スキルの本文は呼び出されたときだけ読み込まれるので、**コンテキストの節約にもなります**。

## パターン4: PRサマリーを動的データで生成

`!` から始まるシェルコマンドを書くと、スキルの内容がClaudeに届く前に実行されて、その出力が埋め込まれます。

```yaml
# .claude/skills/pr-summary/SKILL.md
---
name: pr-summary
description: Generate a PR summary with actual diff and comments
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context (fetched live)

Diff:
!`gh pr diff`

Open comments:
!`gh pr view --comments`

Changed files:
!`gh pr diff --name-only`

CI status:
!`gh pr checks`

## Task

Write a PR summary including:
1. What problem this PR solves (1-2 sentences)
2. Key implementation decisions and their rationale
3. Any areas reviewers should pay special attention to
4. Testing approach
```

Claudeが指示を受け取った時点で、差分もコメントもCIステータスも全部埋め込み済みです。「最新のdiffを取得して」とお願いする必要がありません。

`context: fork` を付けているので、このスキルは独立したサブエージェントで動きます。メインの会話コンテキストを汚染しません。

## パターン5: モノレポのパッケージごとに異なるスキルを用意する

モノレポの場合、パッケージごとに違うルールやデプロイ手順があることが多いです。Skillsは **ネストした `.claude/skills/` ディレクトリを自動で発見**します。

```
packages/
├── frontend/
│   └── .claude/
│       └── skills/
│           └── storybook-story/
│               └── SKILL.md    # フロントエンド専用
├── api/
│   └── .claude/
│       └── skills/
│           └── openapi-endpoint/
│               └── SKILL.md    # API専用
└── .claude/
    └── skills/
        └── shared-deploy/
            └── SKILL.md        # 共通
```

`packages/frontend/` のファイルを編集しているとき、Claudeは `packages/frontend/.claude/skills/` 以下のスキルも自動で発見します。frontendとapiで全く違うコーディング規約やビルド手順があっても、それぞれのスキルが正しく適用されます。

ルートに置いた共通スキルも有効なので、「共通のデプロイ基盤 + パッケージ固有の手順」という構成が自然に作れます。

## パターン6: 特定のファイルパターンにだけ反応させる

`paths` フィールドを使うと、特定のファイルを編集しているときだけスキルを自動ロードできます。

```
# .claude/skills/migration-guide/SKILL.md
---
name: migration-guide
description: Guidelines for writing database migrations
paths: "db/migrations/**,src/migrations/**"
user-invocable: false
---

## Database migration rules

### Always required
- Include both `up` and `down` migrations
- Migrations must be backward-compatible for at least one release cycle
- Never rename columns directly — add new, migrate data, drop old

### Prohibited in production migrations
- `DROP TABLE` without a feature flag gate
- Adding NOT NULL columns without a default value
- Removing columns that active code references

### Naming convention
`YYYYMMDDHHMMSS_verb_noun_description.sql`
Example: `20240315143022_add_email_verified_to_users.sql`
```

`db/migrations/` や `src/migrations/` 以下のファイルを触っているときだけ、このスキルがClaudeのコンテキストに入ります。他の作業のときは読み込まれません。

これはかなり設計がうまいと思っていて、「マイグレーションのルールはマイグレーションを書くときだけ必要」という当たり前のことが、コンテキストの使い方に反映されています。

## パターン7: 複数引数で柔軟なコード変換

`$0`, `$1`, `$2` で引数を位置指定できます。

```
# ~/.claude/skills/migrate-component/SKILL.md
---
name: migrate-component
description: Migrate a component between frameworks or versions
disable-model-invocation: true
argument-hint: "[component-name] [from-framework] [to-framework]"
---

Migrate the `$0` component from $1 to $2.

### Requirements
- Preserve all existing functionality and props interface
- Preserve all existing tests (update syntax only, not behavior)
- Match the conventions of existing $2 components in this codebase
- Do not introduce new dependencies unless unavoidable

### Process
1. Read the current `$0` component implementation
2. Find 2-3 existing $2 components to understand the local conventions
3. Rewrite `$0` in $2 style
4. Update the corresponding test file
5. List any breaking changes in props or API
```

`/migrate-component SearchBar React Vue` を実行すると:

* `$0` → `SearchBar`
* `$1` → `React`
* `$2` → `Vue`

に展開されます。`argument-hint` を設定しておくと、`/migrate-component` と打ったときのオートコンプリートにヒントが表示されます。

## パターン8: セッションIDでログを自動仕分け

`${CLAUDE_SESSION_ID}` 変数を使うと、セッションごとにファイルを分けた記録が残せます。

```
# .claude/skills/decision-log/SKILL.md
---
name: decision-log
description: Log architectural decisions and reasoning to a session file
disable-model-invocation: true
---

Append the following to `docs/decisions/${CLAUDE_SESSION_ID}.md`:

---
Timestamp: !`date -u +"%Y-%m-%dT%H:%M:%SZ"`
---

$ARGUMENTS

---

If the file doesn't exist, create it with this header first:

    # Decision Log — Session ${CLAUDE_SESSION_ID}
```

`/decision-log "認証周りをJWTからセッションCookieに切り替える。理由: モバイルアプリが不要になったため"` のように使います。セッションIDがファイル名になるので、「あのとき何を考えていたか」が後から追跡しやすくなります。

ちなみに `${CLAUDE_SKILL_DIR}` という変数もあって、スキルのディレクトリ絶対パスが取れます。スクリプトをスキルと一緒にバンドルしているとき、カレントディレクトリに依存せず確実にスクリプトを参照するのに使えます。

```
allowed-tools: Bash(python *)
---
Run the analysis script:

    python ${CLAUDE_SKILL_DIR}/scripts/analyze.py $ARGUMENTS
```

## まとめと最初の一歩

8パターンを整理すると、Skillsの設計思想は「**誰が・いつ・何の目的で呼び出すか**」を明示することにあります。`disable-model-invocation`、`user-invocable`、`paths`の3つのフィールドを使い分けるだけで、かなりきめ細かい制御ができます。

まず試すなら、今CLAUDE.mdに書いている長い手順を1つ切り出してスキルにすることをおすすめします。CLAUDE.md が短くなる分だけ、他の指示がより確実に効くようになります。
