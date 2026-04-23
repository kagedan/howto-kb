---
id: "2026-04-20-reviewmdを自己改善させる-prコメントからレビュー観点を自動で育てるgithub-actio-01"
title: "REVIEW.mdを自己改善させる — PRコメントからレビュー観点を自動で育てるGitHub Actionsワークフロー"
url: "https://qiita.com/tatematsu-k/items/3bd83df16ac4718a2cd4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "LLM", "qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

## TL;DR

PRレビューで繰り返し指摘されるパターンを、Claude（LLM）が毎週自動で分析し、レビュー観点ドキュメント（REVIEW.md）を更新するPRを作成する仕組みを構築した。レビュー品質の属人化を防ぎ、チームの知見を自動で蓄積する。

## 背景と課題

チーム開発でPRレビューをしていると、同じ指摘を何度もしていることに気づく。

* 「N+1クエリになっていませんか？」
* 「このロジック、Serviceクラスに切り出しませんか？」
* 「デプロイ時の新旧リソース共存は大丈夫ですか？」

こうした繰り返しの指摘は、レビュー観点としてドキュメント化しておけば、AIレビューツール（Devin、Claude Code等）に事前プロンプトとして渡すことでレビュー品質を安定させられる。

しかし、このドキュメントのメンテナンスが課題になる。手動で更新するのは面倒だし、更新が止まればドキュメントは陳腐化する。

**そこで、PRコメント自体からレビュー観点を抽出し、ドキュメントを自動更新する仕組みを作った。**

## 全体アーキテクチャ

```
毎週月曜 10:00 JST (cron)
        │
        ▼
┌─────────────────────────┐
│ GitHub Actions Workflow │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 1. PRコメント収集        │  GitHub GraphQL API で
│    (過去1週間分)         │  レビューコメントを取得
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 2. Claude Code Action   │  コメントを分析し
│    でREVIEW.mdを更新     │  汎用的な観点を抽出
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 3. PRを自動作成          │  人間がレビューして
│    → developへマージ     │  マージ判断
└─────────────────────────┘
```

ポイントは**最後に人間のレビューを挟む**こと。LLMが勝手にドキュメントを書き換えるのではなく、PRとして提案し、チームが確認してからマージする。

## 実装の詳細

### Step 1: PRコメントの収集

GitHub GraphQL APIを使い、直近1週間に更新されたPRからレビューコメントを収集する。

```
- name: Collect PR review comments from last week
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    INPUT_DAYS: ${{ inputs.days || '7' }}
  run: |
    DAYS="$INPUT_DAYS"
    SINCE=$(date -u -d "${DAYS} days ago" '+%Y-%m-%dT%H:%M:%SZ')
```

GraphQL APIでは `pullRequests` を `updatedAt` の降順で取得し、対象期間外のPRに到達したらページングを打ち切る。

```
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 50, states: [MERGED, OPEN],
                 orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        title
        updatedAt
        reviews(last: 50) {
          nodes {
            author { login }
            body
            createdAt
            comments(last: 50) {
              nodes {
                author { login }
                body
                createdAt
                path
              }
            }
          }
        }
        comments(last: 50) {
          nodes {
            author { login }
            body
            createdAt
          }
        }
      }
    }
  }
}
```

#### ポイント: botコメントの除外

収集したコメントから `github-actions`、`claude[bot]`、`dependabot[bot]` のコメントと `@claude` メンション（Claude Code Actionへの指示）を除外する。人間のレビュアーによる指摘だけを分析対象にするため。

```
jq --arg since "$SINCE" '
  .data.repository.pullRequests.nodes[] |
  {
    pr_number: .number,
    pr_title: .title,
    review_comments: [
      .reviews.nodes[] |
      select(.author.login != "github-actions"
         and .author.login != "claude[bot]"
         and .author.login != "dependabot[bot]") |
      # ... 期間フィルタリング
    ],
    issue_comments: [
      .comments.nodes[] |
      select(.createdAt >= $since) |
      select(.body | test("@claude") | not) |
      # ...
    ]
  } |
  select((.review_comments | length > 0) or (.issue_comments | length > 0))
' > /tmp/pr_comments.json
```

### Step 2: Claude Code Actionによる分析・更新

収集したコメントを [claude-code-action](https://github.com/anthropics/claude-code-action) に渡し、REVIEW.mdの更新を依頼する。

```
- name: Update REVIEW.md with Claude
  if: steps.collect-comments.outputs.has_comments == 'true'
  uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    settings: |
      {
        "permissions": {
          "allow": ["Read", "Edit", "Write", "Glob", "Grep"]
        }
      }
    prompt: |
      ## タスク: REVIEW.md のブラッシュアップ

      `.pr_comments.json` に直近1週間のPRに付けられたレビューコメントが
      保存されています。分析し、`doc/agents/REVIEW.md` のレビュー観点に
      反映すべき改善点があれば更新してください。

      ### 重要なルール:
      1. エッジケースすぎる過剰なルール追加は避ける
      2. 既存の構造・フォーマットを維持する
      3. 簡潔に（各項目は1-2行）
      4. 重複しない
      5. 変更がない場合は変更しない
```

#### プロンプト設計のポイント

LLMにレビュー観点を更新させる際、最も重要なのは**過剰なルール追加を防ぐ**こと。1つのPRでたまたま指摘された特殊なケースをルール化してしまうと、ドキュメントがノイズだらけになる。

そのため、プロンプトで以下を明示している:

* **「複数のPRで繰り返し指摘されているパターン」のみ追加する**
* **エッジケースすぎるルールは避ける**
* **変更不要なら変更しない**

### Step 3: PR作成

REVIEW.mdに変更があった場合のみ、自動でブランチを作成しPRを作る。

```
- name: Check for changes and create PR
  run: |
    CURRENT_DATE=$(date +'%Y.%m.%d')
    if [ -n "$(git status --porcelain doc/agents/REVIEW.md)" ]; then
      git checkout -b update-review-md/$CURRENT_DATE
      git add doc/agents/REVIEW.md
      git commit -m "docs: update REVIEW.md based on PR review comments"
      git push origin update-review-md/$CURRENT_DATE
      gh pr create -B develop \
        -t "docs: REVIEW.md ブラッシュアップ ($CURRENT_DATE)" \
        -b "..."
    fi
```

## REVIEW.mdの構造

更新対象のREVIEW.mdは、AIレビューツールに渡す事前プロンプトとして設計されている。

```
### 共通ルール
- レビューコメントは全て日本語で記載
- レビュー温度感の明記（【必須】【推奨】【参考】）
- 総合点数をレビュー末尾に記載

### Railsアプリケーション
- MVCの原則に沿っているか
- N+1問題の検出
- 冪等性の確認（Sidekiqジョブ等）
- ...

### reactアプリケーション
- hooks の使い方や依存性リストの抜け
- 不要な再レンダリングの防止
- ...
```

このドキュメントが毎週のPRコメント分析によって少しずつ成長していく。

## セキュリティ上の考慮

### Script Injection対策

`workflow_dispatch` の `inputs.days` をシェルスクリプト内で直接展開すると、Script Injectionのリスクがある。環境変数経由で渡すことで対策している。

```
# NG: ${{ inputs.days }} を直接 run: 内で使う
# OK: 環境変数経由
env:
  INPUT_DAYS: ${{ inputs.days || '7' }}
run: |
  DAYS="$INPUT_DAYS"
```

### 権限の最小化

Claude Code Actionに付与する権限は、ファイルの読み書きに必要な最小限に絞っている。

```
{
  "permissions": {
    "allow": ["Read", "Edit", "Write", "Glob", "Grep"]
  }
}
```

## 運用してみて

### うまくいっている点

* **レビュー観点の属人化が減った** — 特定のメンバーだけが気にしていた観点がドキュメント化され、チーム全体で共有される
* **メンテナンスコストがほぼゼロ** — 週1回自動でPRが上がってくるので、確認してマージするだけ
* **AIレビューの品質が安定した** — REVIEW.mdを事前プロンプトに含めることで、AIレビューツールの出力品質が向上

### 注意点

* **過剰なルール追加への監視は必要** — プロンプトで制御しているが、完璧ではない。PRレビュー時に人間が「これは不要では？」と判断する必要がある
* **コメントが少ない週は変更なし** — それでOK。無理にルールを追加しない設計にしている
* **GraphQL APIのレート制限** — 大規模リポジトリでは注意が必要。ページングの打ち切り条件を適切に設定する

## まとめ

レビュー観点ドキュメントの自己改善サイクルを構築した。

1. 人間がPRレビューでコメントする（通常業務）
2. GitHub Actionsが週次でコメントを収集
3. Claudeが分析し、汎用的な観点を抽出
4. PRとして提案 → 人間が確認してマージ
5. 次回以降のAIレビューに反映される

**人間の日常的なレビュー活動が、自動的にチームの知見として蓄積されていく。** メンテナンスコストをほぼゼロに保ちながら、レビュー品質を継続的に改善できる仕組みになっている。

ワークフローの全コードは記事内に掲載済みなので、自分のリポジトリに導入する際の参考にしてほしい。
