---
id: "2026-06-10-claude-code-の-worktree-隔離は信用するな-1週間13件のインシデントと-pre-01"
title: "Claude Code の worktree 隔離は信用するな — 1週間13件のインシデントと PreToolUse フックによる解決"
url: "https://zenn.dev/penne_inc/articles/claude-code-worktree-isolation-bug"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "OpenAI", "zenn"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

「安全文字起こし」の開発では、6体の Claude Code エージェントが同時に走っています。lead、dev、PO、webmaster、qa、claude-code-guide — それぞれが独立したタスクを並行処理しています。

同一リポジトリで複数エージェントが同時に書き込むと、コンフリクトや意図しない上書きが起きます。それを防ぐために `Agent({ isolation: "worktree" })` を使っていました。物理的に分離した git worktree 上で作業させることで、「最悪 worktree を捨てれば戻せる」という前提でエージェントに広めの権限を与えていました。

その前提が、1週間で13回崩れました。

---

## 何が起きたか

2026年6月の第1週、以下の事象が積み重なりました。

| # | 日付 | 事象 | 影響 |
| --- | --- | --- | --- |
| 1 | 6/2 | dev が worktree 内で作業中、API ファイルを親リポジトリ直接編集 | ローカル main 汚染 |
| 2 | 6/2 | dev が lead 専任の内部管理ファイルを worktree 外で編集 | governance 違反 |
| 3 | 6/3 | dev がルーティングファイルの未コミット変更を親 main に波及 | ビルド失敗 |
| 4 | 6/4 | PO が lead 側 main directory に3ファイル直書き | リカバリ成功 |
| 5 | 6/4 | dev の HANDOFF commit が別 PR ブランチに誤積み | remote 汚染なし |
| 6 | 6/5 | dev が環境変数ファイルを親リポジトリ直下に生成 | 即削除（内容は無害） |
| 7 | 6/6 | dev 委任でフロントエンドコンポーネント9ファイルを親 main に直書き | ステージング破損 |
| 8 | 6/6 | 並行 PO エージェントが lead 側ファイルに3回波及 | リカバリ成功 |
| 9 | 6/7 | dev がソースディレクトリ配下を worktree 外で書き換え | ステージング失敗 2回目 |
| 10 | 6/7 | lead（管理者）自身が PO ブランチ上に誤 commit を積んだ | revert で復旧 |
| 11 | 6/8 | dev が main branch で直接 `git commit` を実行 | ローカル main 1 commit ahead |
| 12 | 6/8 | dev の worktree 完了後、cwd が親セッションに引き継がれた | 次タスクで誤 push |
| 13 | 6/9 | dev が起動直後に親リポジトリ絶対パスを Edit に渡し API ファイル3本汚染 | PR でリカバリ |

リアルタイム倍率 13x で事故を生産していました。

---

## 典型パターン3例

### 事象 #1 — dev が gateway を汚染

最初の事象はシンプルでした。dev エージェントに「`gateway/email_msg.py` の返り値を修正して」と指示したところ、worktree 内ではなく親リポジトリの `gateway/email_msg.py` が直接書き換えられました。

`git status` を実行するまで気づかなかった。worktree 内で作業していると信じていたので。

### 事象 #7 — コンポーネント9ファイル直書き

PR #647 のコードレビューを dev に委任した際に起きました。レビューの過程で dev が修正も実施し、書き込み先がすべて親リポジトリの `frontend/app/` 配下でした。9ファイル。ステージング環境のビルドが壊れ、原因特定に30分かかりました。

この時点では「なぜ worktree 内に留まらなかったのか」が理解できていませんでした。

### 事象 #10 — lead が自分で隔離を破った

これが一番きつかった。

worktree 隔離を監視・管理する側の lead エージェントが、PO のブランチ上に誤って commit を積みました。lead はそもそも worktree 隔離で起動していません。それでも起きた。

「エージェントが隔離を守らない」という問題だと思っていたのが、「隔離の概念そのものが脆弱だった」という問題だったと気づいた瞬間でした。

---

## 根本原因の特定

### 最初の仮説：絶対パス問題（仮説 B）

調査を始めると、まず Claude Code 公式の cwd継承問題（Issue #57847）が見つかりました。

> "Worktree-isolated subagents leak Edit/Write into parent checkout"

`isolation: "worktree"` で起動したエージェントが、絶対パスを含むツール引数を受け取ると、worktree のルートではなく `CLAUDE_PROJECT_DIR`（親リポジトリのルート）を基準にパスを解決してしまう、という内容です。

```
# 期待する動作
Edit({ file_path: "/absolute/path/to/file.py" })
→ <worktree>/absolute/path/to/file.py に解決

# 実際の動作（cwd継承問題）
Edit({ file_path: "/absolute/path/to/file.py" })
→ /Users/.../anzen-mojiokoshi-app/absolute/path/to/file.py（親リポジトリ）に解決
```

確かに事象 #1 や #13 は絶対パスが原因でした。でも事象 #10（lead の誤 commit）の説明にはならない。仮説 B は部分的に正しかった。

### git reflog が覆した：Bash cwd 継承（仮説 A）

事象 #10 の直後、`git reflog` を掘りました。

```
c41a9c5 HEAD@{0}: commit: chore: governance 更新 — worktree 第12編
ffccbb4 HEAD@{1}: merge pr/po-branch: Merge pull request #653 ...
```

lead のコミットが PO ブランチのコミット直後に積まれていました。タイムスタンプを見ると、lead が PO ブランチの PR マージを確認するために `git checkout` を実行した後、cwd をそのままにして次のタスクを開始していたことがわかりました。

これも Claude Code 公式の cwd継承問題でした。サブエージェント完了後、親セッションの cwd が worktree 内に残される現象です。絶対パスの問題ではなく、**カレントディレクトリの継承**が原因でした。

cwd継承問題は複合していた。絶対パス経由で破られるケースと、cwd が引き継がれて破られるケース、どちらも `isolation: "worktree"` は防げていなかった。

---

PR #679 で採用した解決策は、`isolation: "worktree"` を主防衛壁とすることをやめ、**PreToolUse フックで物理的にブロックする**というものでした。

フックの設計はシンプルです。subagent が Bash/Edit/Write を呼び出すたびに、操作対象のパスが worktree 外を指していないかチェックする。worktree 外なら `exit 2` で即ブロック。

`.claude/settings.json` への登録：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/worktree-isolation-guard.sh"
          }
        ]
      }
    ]
  }
}
```

### フックの smoke test（5/5 PASS）

| # | 状況 | 期待 | 結果 |
| --- | --- | --- | --- |
| 1 | lead が main で Edit | 通過 | exit 0 |
| 2 | dev が main で Edit（worktree 未使用） | ブロック | exit 2 |
| 3 | dev が正しい worktree 内で Edit | 通過 | exit 0 |
| 4 | dev が worktree 内から親リポジトリ絶対パスへ Edit | ブロック | exit 2 |
| 5 | dev が worktree サブディレクトリで Edit | 通過 | exit 0 |

全 5/5 PASS。

13件の大騒ぎの末、解決策が「settings.json 数行」だったのは、正直ちょっと笑えました。

---

## 学んだこと

`isolation: "worktree"` は「完全な隔離」ではなく、「デフォルトを worktree 内に向ける補助機能」でした。絶対パスを渡せば突き抜けるし、cwd が親に戻れば効かなくなる。

**エージェントの隔離は、エージェントへの指示では担保できません。**

プロンプトに「worktree 外を編集しないこと」と書いても、LLM は確率的にしか従いません。13件はその確率が現実になったものです。フックはそれを確定的に防ぐ。

エージェントが悪かったのではなく、インフラが設計上の前提を満たしていなかった。それが正直なところだと思っています。

Claude Code 公式の cwd継承問題が修正されれば、フックの一部は不要になるかもしれません。でも「フックで担保する」という考え方自体は残しておくつもりです。エージェントに期待するより、環境が守る方が確実です。

---

[安全文字起こし](https://anzen-mojiokoshi.org)というサービスを作っています。取材や会議の音声を私たちの専用サーバーで処理し、Google や OpenAI などの外部AI企業には転送しない設計の SaaS です。プライベートな会話を外部の AI サービスに気軽に渡してよいのか？という不安から生まれたプロジェクトです。複数の Claude Code エージェントと一緒に開発しています。
