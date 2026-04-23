---
id: "2026-03-27-claude-codeでgithubのissueを自動作成pr作成自己成長させてみた-01"
title: "Claude CodeでGitHubのIssueを自動作成・PR作成・自己成長させてみた"
url: "https://zenn.dev/umamichi/articles/77db1fef83fdb7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "OpenAI", "GPT", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## 毎朝6時に、勝手に仕事が始まる

朝起きてGitHubを開くと、AIが昨晩のうちにIssueを作っている。

「なるほど、こういう機能欲しかったな」と思ったらissueをつくり、ラベルを1個貼っておくだけ。あとはAIが実装してPRを作ってくれる。

しかも毎週月曜、そのAIは自分のプロンプトを書き換えて賢くなっていく。

こんな仕組みがあったら良いかもと思い、実際に作ってみました。

## 何を作ったか

* **PdM AI**: 毎朝6時にIssueを自動提案（OpenAI gpt-4o-mini）
* **plan-first フロー**: `plan-first` ラベルを貼ると実装プランをコメント（Claude Code）
* **auto-implement フロー**: `auto-implement` ラベルを貼るとコードを書いてPRを作成（Claude Code）
* **自己改善ループ**: 毎週月曜、過去の提案採否を分析してプロンプトを自動更新

全部GitHub Actionsで動いている。インフラ管理なし。

## システム全体像

```
毎朝 JST 6:00
PdM AI（OpenAI）→ GitHub Issue 自動作成
      ↓ 人間が "plan-first" ラベルを貼る
Claude Code Action → 実装プランをIssueにコメント
      ↓ 人間が "auto-implement" ラベルを貼る
Claude Code Action → コードを書いてPR作成
      ↓
人間がレビュー → マージ

毎週月曜 JST 10:00
PdM AI → 過去提案の採否を分析 → prompt.md を自己改善 → PR作成
人間がマージするだけでPdM AIが賢くなる
```

人間の仕事は「ラベルを貼る」と「PRをレビューしてマージする」だけ。

## 各コンポーネントの解説

### PdM AI（提案役）

`scripts/pdm-agent/index.ts` がメイン処理。

やっていることはシンプルで、

1. 直近のIssue一覧・過去の提案・コミット履歴をGitHub CLIで取得
2. `prompt.md` に書かれたシステムプロンプトとコンテキストをOpenAI APIに投げる
3. 返ってきたJSONからIssueを `gh issue create` で作成

```
// scripts/pdm-agent/index.ts（抜粋）
const response = await openai.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [
    { role: "system", content: systemPrompt },
    { role: "user", content: userPrompt },
  ],
  response_format: { type: "json_object" },
  temperature: 0.9,
});
```

`temperature: 0.9` で毎回違う提案が来るようにしている。

GitHub Actionsのトリガーはcronで、UTC 21:00 = JST 6:00に起動。

```
# .github/workflows/pdm-ai-daily.yml（抜粋）
on:
  schedule:
    - cron: "0 21 * * *"
```

### plan-first フロー（設計役）

`plan-first` ラベルをIssueに付けると起動する。使っているのは `anthropics/claude-code-action@v1`。

```
# .github/workflows/plan-first.yml（抜粋）
jobs:
  plan:
    if: github.event.label.name == 'plan-first'
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: "--max-turns 15 --dangerously-skip-permissions"
          prompt: |
            あなたはこの Issue の実装プランナーです。
            アプリケーションコードの変更・実装は一切行わないでください。
            ...
```

Claudeはコードを読んで、実装ステップ・影響ファイル・リスクなどをまとめた「📋 実装プラン」をIssueにコメントする。

大きすぎる機能はここでサブIssueに分割される。`gh issue create` で子Issueを自動作成して、親Issueにリンクを貼ってくれる。

### auto-implement フロー（実装役）

`auto-implement` ラベルを貼ると、今度は実際にコードを書く。

```
# .github/workflows/auto-implement.yml（抜粋）
jobs:
  implement:
    if: github.event.label.name == 'auto-implement'
    timeout-minutes: 45
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          claude_args: "--max-turns 45 --dangerously-skip-permissions"
```

`--max-turns 45` を設定しているのは大事なポイント。デフォルトだとターン数制限で途中で止まることがある。

Claudeはplan-firstで作られた「📋 実装プラン」コメントを読んでから実装を始めるので、指示の一貫性が保たれる。

### 自己改善ループ（成長役）

毎週月曜10時に `self-improve.ts` が動く。

やること：

1. 過去のIssueを全件取得
2. 「採用（COMPLETED）」「却下（NOT\_PLANNED）」「未判断（OPEN）」に分類
3. 採用率・パターンを分析してプロンプト改善案をOpenAI APIで生成
4. 変更がある場合は `prompt.md` を書き換えてPRを作成

```
// scripts/pdm-agent/self-improve.ts（抜粋）
function categorizeIssues(issues) {
  for (const issue of issues) {
    if (issue.state === "CLOSED" && issue.stateReason === "COMPLETED") {
      accepted.push(issue); // 採用
    } else if (issue.state === "CLOSED" && issue.stateReason === "NOT_PLANNED") {
      rejected.push(issue); // 却下
    } else {
      pending.push(issue); // 未判断
    }
  }
}
```

人間がPRをマージするだけで、PdM AIは「採用されやすい提案」を学習していく。

## 実際にハマったこと

### `--dangerously-skip-permissions` は何者か

名前がこわい。が、CI環境では必須のフラグ。

通常のClaude Codeは「このファイルを編集していいですか？」と対話的に確認する。GitHub Actions上では人間がいないので、この確認をスキップする必要がある。

権限管理はGitHub Actionsの `permissions` セクションでやっているので、実際にはそこまで怖くない。

```
permissions:
  id-token: write
  contents: write
  issues: write
  pull-requests: write
```

### ターン数の罠

最初 `--max-turns 10` で動かしたら、複雑な実装の途中でClaudeが止まってPRが来なかった。

`--max-turns 45` に増やしてから安定した。タイムアウトも `timeout-minutes: 45` に合わせている。

### Issueが大きすぎると失敗する

「ユーザー認証機能を追加して」みたいな大きいIssueをそのままauto-implementに投げると、Claudeが途中で迷子になる。

plan-firstで必ずサブIssueに分割してから実装するフローにしてから、失敗率が激減した。

### CLAUDE.md の重要性

リポジトリのルートに `CLAUDE.md` を置いている。アーキテクチャの説明、よく使うファイルのパス、開発時の注意点などを書いておくと、Claudeが的外れなコードを書くことが減った。

LLMへの「読み物」として整備することが、全体の品質に直結する。

## コスト感

正直、ほぼ無料に近い。

| 用途 | モデル | 月コスト（目安） |
| --- | --- | --- |
| PdM AI（毎日提案） | gpt-4o-mini | 数十円 |
| 自己改善（週次） | gpt-4o-mini | 数円 |
| plan-first / auto-implement | Claude（Anthropic API） | 実装の複雑さによる |
| GitHub Actions | — | 無料枠内 |

gpt-4o-miniは安い。PdM AIに毎日1回呼んでも月数十円程度。

Claudeの実装系は、複雑な機能を1本実装するとそれなりにトークンを消費するが、人件費と比べれば誤差の範囲だと思っている。

## まとめ

「完全自動化」ではない。ラベルを貼るのは人間だし、最終的なマージも人間がやる。

でも「何を実装するか考える→コードを書く→PRを出す」の一番工数のかかる部分かつ、これからAIに置き換えられるであろうタスクを自動化できた感覚はある。

朝起きてGitHubを開いて、「この提案おもしろい」と思ったらラベルを貼る。夜には動くPRが来ている。  
この感覚は、まるでAI社員が寝てる間に勝手に仕事をしてくれている感覚で、一度体験してみて欲しいです。

PdM AIは今も毎朝提案を作り続けていて、自分のプロンプトを書き換えながら少しずつ賢くなっています。
