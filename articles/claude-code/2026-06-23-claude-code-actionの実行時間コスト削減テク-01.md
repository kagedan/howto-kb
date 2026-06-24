---
id: "2026-06-23-claude-code-actionの実行時間コスト削減テク-01"
title: "Claude Code Actionの実行時間・コスト削減テク"
url: "https://zenn.dev/dtanad/articles/6292c2824457a8"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Claude の code-review プラグインを単一エージェントに切り替え、実行時間を６分の１に短縮した
* 品質に大きな変化は見られなかった

---

数行の変更のPRでも、10分近く実行時間がかかっていたのでなんとか時間短縮できないかと思い、改めてgithub actionsのコードを調べてみました。

### プラグインが裏で複数のサブエージェントを動かしていた

```
- name: Run Claude Code Review
  uses: anthropics/claude-code-action@xxxxxxxxxx
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    
    # ① プラグインを読み込む
    plugin_marketplaces: 'https://github.com/anthropics/claude-code.git'
    plugins: 'code-review@claude-code-plugins'
    
    # ② 投稿ツール + gh を明示許可
    claude_args: >-
      --model opus
      --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*),Bash(gh pr list:*),Bash(gh issue view:*),Bash(gh issue list:*),Bash(gh search:*)"
    
    # ③ スラッシュコマンドで起動
    prompt: |
      /code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }} --comment
      
      レビュー観点は `.claude/code-review-guidelines.md` を規範として適用。Critical/High/Medium のみ投稿、Low は投稿しない。
```

code-review プラグインは、ゲートキーパー/CLAUDE.md収集/サマリ生成/レビュー実施/検証 の工程でコードレビューを実施しており、最低でもサブエージェントが5つ起動します。  
サブエージェントは1個ごとに「コンテキスト読み込み→推論→結果返却」のオーバーヘッドがあるので、これが積み上がると実行時間が長くなってしまいます。

### 単一エージェントに切り替える

```
claude_args: >-
  --model sonnet
  --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*),Read,Grep,Glob"
prompt: |
  このPRをレビューして。サブエージェントは使わず単一エージェントで。
  1. `gh pr diff <PR NUMBER>` で変更内容を取得する。
  2. `.claude/code-review-guidelines.md` を読み、その観点（マルチテナント分離・OWASP Top 10・正確性・効率性・保守性・命名規則）と、該当ディレクトリの CLAUDE.md / .claude/rules を規範としてレビューする。
  3. 高確度の Critical/High/Medium だけインライン投稿
  4. Low と自信ない指摘は投稿しない
```

プラグインを捨てて、サブエージェントを使わない単一エージェントのプロンプトに書き直してみました。

結果：（300行程度の差分で検証）

|  | code reviewプラグイン | 単一エージェント |
| --- | --- | --- |
| 実行時間 | 約8分 | 1分17秒 |
| コスト | $1.70 | $0.16 |

実行時間が６分の１、コストも１０分の１になりました。  
検証したPRでは、指摘の品質の差は見られませんでした。

## 最後に

小規模なプロジェクトやコストに制約があるプロジェクトの場合、単一エージェントに切り替える選択肢はありかもしれません。  
大規模なプロジェクトや他ファイルへの影響なども考慮する場合は、code-review プラグインを引き続き使うのがよさそうです。
