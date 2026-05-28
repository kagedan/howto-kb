---
id: "2026-05-27-claude-code-の-batch-で1つの指示を530個の-unit-に分解する-01"
title: "Claude Code の /batch で1つの指示を5~30個の unit に分解する"
url: "https://zenn.dev/gudezou/articles/c2a4336ed5da0b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

![サムネイル](https://static.zenn.studio/user-upload/e2bbeacf5ca1-20260527.png)

* `/batch` は1つの指示でコードベース全体の機械的な refactor を取りまとめ、5~30個の独立した unit に分解する bundled skill です。
* 計画の提示と承認のあと、unit ごとに1つのバックグラウンドの subagent が別々の git worktree 上で動き、それぞれがテストを通してプルリクエストを1本ずつ開きます。
* 前提として git リポジトリが必須で、トークン使用量は並列数の掛け算になるため、初回は小さめのスコープで挙動を見るのがよさそうです。

---

## 1つの指示で5~30個の subagent に分け、それぞれが PR を開く

`/batch` は Claude Code の bundled skill のひとつで、コードベース全体の機械的な変更を並列にまとめます。  
`/batch <instruction>` の形で1行の指示を渡すと、Claude がまずコードベースの中身を調査します。  
そのあとに、作業を5~30個の独立した unit に分解した計画を提示してくれます。  
ユーザーがその計画を承認すると、unit ごとに1つのバックグラウンドの subagent が動き出します。  
subagent はそれぞれ別々の git worktree で動くので、ファイルの編集が他の subagent と衝突しません。  
各 subagent は自分の unit を実装し、その unit のテストを走らせます。  
最後に unit ごとに1本プルリクエストを作成します。  
ここまでの一連の流れは Anthropic Docs > Commands にまとめられています。

得意な作業は限定されていて、使いどころは Anthropic Docs > Run agents in parallel にまとめられています。  
そこでは、コードベース全体に及ぶ移行や、1つの指示で説明できる機械的な refactor が向くとされています。  
docs に挙がっている例は `/batch migrate src/ from Solid to React` のような形です。  
対象範囲と移行先を1文で書き切れる指示が得意ということです。  
逆に、設計判断が unit ごとに分かれる作業や、unit 間で副作用の調整が必要な作業には向きません。  
そうした作業は、ふつうの subagent やセッション内のやり取りで進めるほうが安全そうです。

![/batch の処理の流れ](https://static.zenn.studio/user-upload/013c9c218143-20260527.png)

---

## git リポジトリ必須・worktree の分岐元・トークン使用量の掛け算

初回利用で押さえておきたい前提が3つあります。

1つ目は、`/batch` が git リポジトリを必須とする点です。  
git で管理されていないディレクトリでは `/batch` そのものが動きません。  
これは Anthropic Docs > Commands に明記されています。

2つ目は、subagent が動く worktree の分岐元の話です。  
worktree はデフォルトでリポジトリのデフォルトブランチ origin/HEAD から枝分かれします。  
そのため、ローカルで未 push のコミットや、作業中の feature ブランチの状態は subagent に引き継がれません。  
ローカルの HEAD から分岐させたいときは、設定で `worktree.baseRef` を `"head"` に切り替える方法があります。  
あわせて、`.env` のような未追跡ファイルは新しい checkout には入りません。  
subagent に渡したい場合は、プロジェクト直下の `.worktreeinclude` で明示する必要があります。  
ここまでの挙動は Anthropic Docs > Run parallel sessions with worktrees にまとめられています。

3つ目はコストの話です。  
並列で複数の subagent を走らせると、トークン使用量が並列数の掛け算で増えます。  
これは Anthropic Docs > Run agents in parallel が明示しています。  
さらに、成果物は unit ごとに1本ずつのプルリクエストとして出てきます。  
5~30本のプルリクエストをどう review してマージするかも、最初の `/batch <instruction>` を打つ前に考えておきたいところです。

![3つの前提条件のチェックリスト](https://static.zenn.studio/user-upload/3c229da59183-20260527.png)

---

## 参考文献

1. Anthropic. *Commands - Claude Code Docs*. Anthropic Documentation. <https://code.claude.com/docs/en/commands>
2. Anthropic. *Run agents in parallel*. Anthropic Documentation. <https://code.claude.com/docs/en/agents>
3. Anthropic. *Run parallel sessions with worktrees*. Anthropic Documentation. <https://code.claude.com/docs/en/worktrees>
4. Anthropic. *Extend Claude with skills*. Anthropic Documentation. <https://code.claude.com/docs/en/skills>
