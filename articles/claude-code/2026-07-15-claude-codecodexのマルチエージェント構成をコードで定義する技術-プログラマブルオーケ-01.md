---
id: "2026-07-15-claude-codecodexのマルチエージェント構成をコードで定義する技術-プログラマブルオーケ-01"
title: "Claude Code・Codexのマルチエージェント構成をコードで定義する技術 ― プログラマブル・オーケストレーション入門"
url: "https://qiita.com/Koukyosyumei/items/9ff3ddef9c11a44bcb30"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "LLM", "GPT", "Python"]
date_published: "2026-07-15"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

Claude CodeやCodexのようなコーディングエージェントは、それぞれ異なる強みを持っています。しかし、複数のエージェントを単に同時起動したり、互いにメッセージを送れるようにしたりするだけでは、「誰が実装し、誰がレビューし、どの条件でやり直し、最終的にどの変更を採用するか」まで含めた開発プロセスを再現可能な形で表現することはできません。

**[h5i-orchestra](https://github.com/h5i-dev/h5i)** およびその Python ラッパーである **[h5i-python](https://github.com/h5i-dev/h5i-python)** は、Claude CodeやCodexをはじめとする、さまざまなベンダーのコーディングエージェントを組み合わせたマルチエージェントワークフローを、通常のRust・Pythonプログラムとして記述・実行するためのフレームワークです。

例えば、次のような典型的なワークフローを記述できます。

* 同じタスクをClaudeとCodexに並行して実装させ、互いにレビュー・改善したうえで、テストを通過した候補のうち差分が最小のものを採用する
* Claude FableとCodex GPT-5.6-Solに議論させながら設計を固め、その設計をもとにClaude Opusに実装させる

さらに、

* Claude Fableによる設計とCodex GPT-5.6-Solによるレビューを10回繰り返したあと、Claude Opusに実装を任せ、Fableが実装に問題があると判定した場合のみGPT-5.6-Solに修正させる

といった、ループ、条件分岐、並列実行を含む複雑なワークフローも、特別なDSLではなく自然なPythonコードとして表現できます。

各エージェントは独立したサンドボックスとGit worktree内で作業するため、元の開発環境やほかのエージェントの作業を汚染しません。また、エージェントが生成した変更をGit上の成果物として固定し、レビュー、テスト、候補の選択、最終的な適用までを一つの再現可能なワークフローとして管理できます。

以下のコード例は、シンプルな「同じタスクを Claude と Codex に同時にやらせて、お互いにレビュー・改善させ、テストコードが通ったものの中で差分が最小のものを選ぶ」を h5i-python で実装した例です。

```python
import asyncio
from h5i.orchestra import Conductor

async def main():
    task = "implement quicksort in python with unit test"

    async with Conductor(".", "fix-auth") as c:
        claude = await c.hire("claude-agent", runtime="claude")
        codex  = await c.hire("codex-agent",  runtime="codex")

        # 2エージェントが独立に並行して実装
        claude_work, codex_work = await asyncio.gather(claude.work(task), codex.work(task))

        await c.freeze()   # ラウンドを封印:これ以前に相互影響がなかったことを保証

        # お互いの成果物を相互レビュー
        await asyncio.gather(codex.review(claude_work), claude.review(codex_work))

        # テストコードが通るかどうか検証 (新しいサンドボックス内で中立的に)
        await c.verify(claude_work, ["pytest", "--quiet"])
        await c.verify(codex_work, ["pytest", "--quiet"])

        verdict = await c.judge()   # テストが通り、差分が最小のものが勝ち
        print("winner:", verdict.selected_submission)

asyncio.run(main())
```

## 基本的な使い方

h5i-python SDK の核となるのが エージェントの管理や実行を担当する `Conductor` です。

```python
Conductor(
    repo=".",                 # エージェントに触らせるgitリポジトリ("." が普通)
    run="my-run",             # 名前    
    turn_timeout=1800,        # 1ターンの最大待ち時間(秒)
    .
    .
    .
)
```

`Condurctor` は Claude Code や Codex といった AI エージェントを `hire` めそどっによって雇うことで、マルチエージェントチームを作ります。

```python
claude = await c.hire("claude-agnet", runtime="claude", model="claude-haiku-4-5")
codex  = await c.hire("codex-agent",  runtime="codex",  model="gpt-5.4-mini", effort="medium")
```

各エージェントは、様々な async/await メソッドが搭載されています。

- `await agent.work(task, ...)`: 1回の作業ターン。タスクを渡し、成果物 (artifact) の提出を待つ
- `await agent.ask(prompt, ...)`: コードではなくデータを求める。返信はJSON値でなければならない
- `await agent.review(artifact)`: 他のエージェントの成果物をレビューする
- `await agent.revise(artifact, review)`: レビューを踏まえて成果物を修正・再提出

他にも、`Conductor` が持つ様々なメソッドによって、オーケストレーションを柔軟に定義することが可能です。

- `await c.freeze()`: 各エージェントの初回提出が終了するまでは、お互いの成果物を確認できないようにして相互影響によるバイアスを防ぐ
- `await c.verify(artifact, ["pytest", "-q"], ...)`: 指定コマンドを新しいサンドボックス内で実行する。テストケースがきちんと通るかどうかなどを検査するときに用いる
- `await c.judge()`: 複数のエージェントの成果物を比べて最も良いものを決める。デフォルトのポリシーは `tests_then_smallest_diff` というテストが通る中で変更量が最小のものを選ぶが、自作のポリシーを使うことも可能
- `await c.apply(winning_artifact)`: サンドボックス内で作られた成果物を、元のブランチに適用

## 組込みパターン

h5i-python には典型的なマルチエージェントのワークフローがすでに実装されており、コピペするだけで簡単につかうことができます。

```python
# アンサンブル:全員が独立に実装→封印→相互レビュー/修正を最大rounds回→検証→評決
out = await patterns.ensemble(c, task, [claude, codex], rounds=2, verify=["pytest", "-q"])

# アリーナ:N人が独立に挑戦→中立検証+最小差分でランキング
out = await patterns.arena(c, task, [claude, codex], verify=["pytest", "-q"])

# パイプライン:役割特化のステージを順に(設計者→実装者→改善担当)
arts = await patterns.pipeline(c, [(architect, "design"), (builder, "implement")])

# map-reduce:作業リストをファンアウトして統合
out = await patterns.map_reduce(c, [(a, t1), (b, t2)], reduce=(merger, "fuse"))

# 審査員パネル:LLM審査員が封印済み候補をルーブリックで採点
out = await patterns.judge_panel(c, "smallest correct change", [judge1, judge2])
```

## コード例

例えば、ある問題について、claude と codex に議論を行わせた上で、別の claude が勝者を判定し、勝者のほうが実装・敗者はレビューを行うという構成は以下のように記述できます。

```python
async def main(task: str) -> None:
    question = question_for(task)
    async with Conductor(".", "debate-demo", launcher="resident", isolation="supervised") as c:
        pro = await c.hire("pro", runtime="claude", model="claude-haiku-4-5")
        con = await c.hire("con", runtime="codex", model="gpt-5.4-mini", effort="medium")
        moderator = await c.hire(
            "moderator", runtime="claude", model="claude-haiku-4-5"
        )

        outcome = await patterns.debate(
            c, question, [pro, con], moderator=moderator, rounds=2
        )
        for who, argument in outcome.transcript:
            print(f"[{who}] {argument[:120]}…")
        conclusion = outcome.conclusion
        assert conclusion is not None
        print(f"\nwinner: {conclusion.winner} — {conclusion.rationale}")

        winner = pro if conclusion.winner == pro.id else con
        loser = con if winner is pro else pro

        artifact, risks = await asyncio.gather(
            winner.work(
                f"You won this debate: {question}\nYour side prevailed with: "
                f"{conclusion.rationale}\nNow do the task your way: {task}"
            ),
            loser.ask(
                "You lost the debate. List the 3 biggest risks of the winning "
                'approach as a JSON array of strings, most severe first.',
                parse=lambda v: [str(x) for x in v],
            ),
        )
        await c.freeze()
        await c.note("debate risks: " + "; ".join(risks))
        print("built:", artifact.id, "| risks recorded to the event log")
```

## まとめ

h5i-orchestra / h5i-pythonを使うと、Claude CodeやCodexといった異なるコーディングエージェントを、単に並列で動かしたり会話させたりするだけでなく、誰が実装し、誰がレビューし、どの条件で修正を繰り返し、どの成果物を採用するかまで含めた開発プロセス全体を、通常のRust・Pythonコードとして記述できます。

また、各エージェントは独立したサンドボックスとGit worktree内で作業し、生成された変更はGit上の成果物として固定されます。そのため、複数のエージェントを安全に競争・協調させながら、中立的な環境でのテスト、候補の比較、最終的な適用までを、再現可能かつ監査可能なワークフローとして管理できます。

今後、コーディングエージェントの種類や能力が増えていけば、「最も強いエージェントを一つ選ぶ」のではなく、タスクごとに異なるエージェントを組み合わせ、一つの開発チームとして動かすことがより重要になるはずです。h5i-orchestra / h5i-pythonが、そのためのプログラマブルな実行基盤になればと考えています。

- https://github.com/h5i-dev/h5i
- https://github.com/h5i-dev/h5i-python
