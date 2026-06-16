---
id: "2026-06-14-github-actions-で-claude-によるコードレビューを必須化する方法個人開発向け-01"
title: "GitHub Actions で Claude によるコードレビューを必須化する方法（個人開発向け）"
url: "https://qiita.com/inoue_d/items/15c801135e0a602d673d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-06-14"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

## この記事のまとめ
- PR 作成時に Claude が差分を自動レビューし、指摘を該当行のインラインコメント（解決可能スレッド）で残す。
- 未解決スレッドがある限りマージ不可（`required_review_thread_resolution`）。誤検知はスレッドを Resolve すればマージ可。
- 認証は Claude サブスク（Pro/Max）の OAuth トークン。API キー/Bedrock 不要・追加課金なし。
- レビューは PR 作成時（`opened`）のみ。push（`synchronize`）は即パスで、必須チェックの永久ブロックと再レビューのコスト・Nit ループを回避。
- 「Claude review」を必須チェック化し、レビュー完了前のすり抜けマージも防止。
- インライン投稿は公式 MCP ツール `mcp__github_inline_comment__create_inline_comment`。

> 対象範囲: 本記事は個人／小規模リポジトリ向けの構成です。チームの共有・本番自動化では、公式ガイダンスどおり Claude Platform の API キー（予測可能な従量課金）を推奨します。Agent SDK の月次クレジットは個人の実験・自動化向けに設計されています（[公式](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)）。

## 前提
- リポジトリ管理者権限
- Claude Pro/Max サブスク
- `gh` CLI

## 手順

### 1. OAuth トークンを Secret に登録
```bash
claude setup-token                                  # sk-ant-oat01-... が出力される（有効期間 1年）
gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo <owner>/<repo>   # マスクしたまま登録可能
```
- `claude setup-token` が出すのは有効期間 1年 の OAuth トークン（[公式: Authentication / Generate a long-lived token](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token)）。
- `ANTHROPIC_API_KEY` が環境にあるとそちらが優先されるため、サブスクで動かすなら置かない（[公式: Authentication precedence](https://code.claude.com/docs/en/authentication#authentication-precedence)）。
- 消費枠: GitHub Actions は非対話（`claude -p` / Agent SDK 相当、連携もこのクレジット対象）。2026-06-15 を境に、サブスクの Agent SDK 利用は、対話の利用上限とは別の「月次 Agent SDK クレジット」から消費される（それ以前は対話の 5時間/週次枠と共有）（[公式: Use the Claude Agent SDK with your Claude plan](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)）。
  - クレジットはプランに含まれ追加課金なし（Pro $20 / Max 5x $100 / Max 20x $200・月次相当）。受け取りはアカウントごとに一度の申請（opt-in）が必要で、以降は毎サイクル自動更新。
  - 使い切った場合: usage credits（従量）を無効なら翌サイクルまで停止するだけ（課金なし）、有効なら標準 API レートで従量課金。想定外の請求を避けるなら usage credits を OFF に。
  - チーム共有・本番自動化では、本クレジットではなく Claude Platform の API キー（予測可能な従量課金）を推奨（公式）。クレジットは個人の実験・自動化向け。

### 2. ワークフローを追加
`.github/workflows/claude-review.yml`:
```yaml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]
    branches: [main]

permissions:
  contents: read
  pull-requests: write
  issues: write

concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: false

jobs:
  review:
    name: Claude review
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      # push（synchronize）では再レビューせず即パス。これで必須チェックが新 HEAD でも緑になる。
      - name: skip review on push
        if: github.event.action != 'opened'
        run: echo "PR 作成時のみレビュー。push は即パス。"

      # アクションは可変タグでなく full commit SHA で固定する（サプライチェーン対策）。
      # コメントに元バージョンを併記しておくと更新時に分かりやすい。
      - uses: actions/checkout@9f698171ed81b15d1823a05fc7211befd50c8ae0 # v6.0.3
        if: github.event.action == 'opened'
        with:
          fetch-depth: 0

      - uses: anthropics/claude-code-action@d5726de019ec4498aa667642bc3a80fca83aa102 # v1.0.148
        if: github.event.action == 'opened'
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          classify_inline_comments: "false"
          claude_args: |
            --max-turns 30
            --allowedTools Read,Grep,Glob,Bash(git diff:*),Bash(git log:*),Bash(cat:*),mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*)
          prompt: |
            REPO: ${{ github.repository }}
            PR NUMBER: ${{ github.event.pull_request.number }}

            この PR の変更をレビューしてください。
            1. `git diff origin/main...HEAD`（失敗時は `git diff HEAD~1 HEAD`）で差分を取得。
            2. `cat REVIEW.md` `cat AGENTS.md` を読み観点を把握。REVIEW.md を最優先で厳守。
            3. 指摘は mcp__github_inline_comment__create_inline_comment（confirmed: true）で
               該当する変更行に1指摘1インラインコメントとして投稿。各コメント本文の先頭に重大度を `High:` / `Medium:` / `Low:` で付ける。
            4. 最後に一度だけ `gh pr comment` で一行サマリを投稿（指摘ゼロなら「ブロッカーなし」）。
            5. すべて日本語で書くこと。
```

設定の根拠（変更前に必読）:
- トリガは `[opened, synchronize]`、`opened` のみ本レビュー、`synchronize`（push）は即パス。
  - `opened` のみ＋必須チェックにすると、push 後に新コミットへ「Claude review」が付かず、必須が揃わずマージ不能になる。これを synchronize の即パスで回避する。
  - 必須チェックにしない場合、レビュー投稿前（CI 緑・スレッド0の状態）にマージできてしまう。
  - synchronize で毎回本レビューすると、レート枠を消費し指摘が再生成され続ける。push では再レビューしない。
- `--allowedTools` に投稿手段（`mcp__github_inline_comment__create_inline_comment` と `Bash(gh pr comment:*)`）を必ず含める。含めないとツールが権限拒否され、何も投稿されないまま成功扱いで終わる（ログに `permission_denials_count`）。
- `classify_inline_comments: "false"` で分類を挟まず即投稿。
- `concurrency.cancel-in-progress: false` で `opened` のレビューを途中で止めない。

### 3. ブランチ保護を設定
- 会話の解決を必須化: 未解決スレッドがあるとマージ不可。Rulesets なら `pull_request` ルールの `required_review_thread_resolution: true`。
- 「Claude review」を必須ステータスチェックに追加: `opened` のレビュー実行中はチェックが pending になり、レビュー完了前のマージを止める。

### 4. レビュー観点を REVIEW.md に定義
リポジトリ直下に `REVIEW.md` を置き、CLAUDE.md からリンクする（Claude は CLAUDE.md からリンクされたファイルを読む）。例:
```markdown
# レビュー方針
- 重大度は High / Medium / Low の3段階。各指摘の本文先頭に付ける。
  - High: 認可漏れ・内部情報の漏洩・本番を壊すロジック誤り・秘密情報のコミット。
  - Medium: エラー処理不足・エッジケース・テスト欠落など、すぐ壊れはしないが直すべきもの。
  - Low: スタイル・命名・軽微な改善。
- 報告しない: lint/format/型（CI が担保）・生成物。
- 出し方: 日本語・file:line で裏取り。
```

## 注意点
- 投稿手段を `--allowedTools` に入れないと権限拒否で無投稿になる。
- `opened` のみ＋必須チェックは push で永久ブロックになる → `synchronize` 即パスで回避。
- 網羅性の限界: synchronize 即パス設計のため、PR 作成後に push した変更はレビューされないままマージし得る（網羅性より必須チェックの運用性を優先）。「必須化」は「PR 作成時に必ずレビューが走る」の意味で、「全コミットが必ずレビューされる」ではない。毎 push レビューが必要なら synchronize も本レビュー対象にする（枠消費は増える）。
- claude-code-action は PR の設定ファイルを base（main）版に復元する（公式 security.md が claude-code-base-action との比較で「restore project configuration from the base ref」と明記。[出典](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)）。具体的な対象は実行ログで `.claude` / `.mcp.json` / `CLAUDE.md` / `CLAUDE.local.md` / `.husky` 等が `origin/main` から復元される（"PR head is untrusted"）と確認できる（ファイル一覧自体は公式未掲載・ログ観測）。
  - 結果として、CLAUDE.md の変更（REVIEW.md へのリンク追加を含む）は main マージ後の PR から反映される。REVIEW.md / AGENTS.md はこの復元対象外で PR の版が読まれるが、REVIEW.md は CLAUDE.md からのリンクで読ませる構成上、初回のリンク設置は main に入れる必要がある。
- サブスクトークンの消費枠は 2026-06-15 を境に変わる（以降は別枠の月次 Agent SDK クレジット。[出典](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)）。

## 参考
- [Claude Code Authentication（公式）](https://code.claude.com/docs/en/authentication) — OAuth トークン生成（`setup-token`）・認証の優先順位
- [Use the Claude Agent SDK with your Claude plan（公式サポート）](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan) — Agent SDK クレジットの対象・金額・申請・チーム/本番の API キー推奨
- [claude-code-action security（公式）](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md) — base ref からの設定復元
- [anthropics/claude-code-action（GitHub）](https://github.com/anthropics/claude-code-action)
