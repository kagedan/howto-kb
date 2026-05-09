---
id: "2026-05-08-aiエージェント自律完遂率を上げるハーネス設計パターン3選-lint-as-promptreview-01"
title: "AIエージェント自律完遂率を上げるハーネス設計パターン3選 — lint as prompt・Reviewer Agent CI・構造ガード"
url: "https://zenn.dev/aerign/articles/e5b561d7f1650b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* AIエージェントがコード生成コストをほぼゼロにした結果、人間の希少資源は「実装力」から「時間・注意力・コンテキストウィンドウ」の3つに変わった（OpenAI / Ryan Lopopolo 講演, 2026-04-17）
* エージェントに `continue` と入力しなければならない状況はすべてハーネス側の設計失敗を示すシグナルである
* ハーネス設計のコアは3つのパターン：(1) 構造ガードレール、(2) lint as prompt、(3) Reviewer Agent CI統合
* 各パターンの本質は「エージェントへのジャストインタイムなコンテキスト提供」であり、ドキュメントや設定ファイルに設計意図を埋め込む作業に相当する
* 一方で、モデルの急速な進化によって不要になるほど複雑なハーネスを作ってしまう過剰設計リスク（The Bitter Lesson）も同時に存在する
* 優先実装順は `AGENTS.md 作成 → linter メッセージ改善 → Reviewer Agent 導入` の順が費用対効果が高い

---

## 対象読者と前提

**対象：**

* Claude Code・Copilot Workspace・Devin 等の AIエージェントを CI/CD や開発ワークフローに組み込んでいる、または組み込もうとしているソフトウェアエンジニア
* エージェントの自律完遂率の低さや出力品質のばらつきに課題を感じているプラットフォームエンジニア / テックリード
* 「AIに任せたのに結局自分が直す羽目になる」という経験を繰り返しているエンジニア

**前提：**

* AIエージェントがコードを自律的に生成・修正できるという前提で話を進める（GPT-5.2 相当以上のモデルが実装タスクを自律遂行できるという Ryan Lopopolo の見解に基づく）
* ESLint（Node 20+）または Ruff（Python 3.11+）の基本的な使い方を知っている
* GitHub Actions の YAML 構文を読める

**扱わないこと：**

* 特定モデルの API 利用方法や fine-tuning
* プロンプトエンジニアリングの一般論
* モデル選定・コスト最適化の詳細比較

---

## 背景

OpenAI の Ryan Lopopolo は 2026年4月17日の講演「Harness Engineering: How to Build Software When Humans Steer, Agents Execute」でこう宣言した。

> "Code is free. We have an abundance of code to solve the problems that we come across."  
> — Ryan Lopopolo, 02:15

コードを書くコストがほぼゼロに近づくとはどういうことか。エンジニアの仕事の「希少資源」が変わるということだ。講演では希少資源を次の3つに整理している（timestamp 05:12）。

1. **人間の時間** — 何を設計・判断するかに使う時間
2. **人間とモデルの注意力** — コンテキストを維持し意思決定する認知リソース
3. **モデルのコンテキストウィンドウ** — エージェントが一度に参照できる情報量

この枠組みが実装判断を変える。「どれだけ多くのコードを書けるか」ではなく、「いかに少ないコンテキストで、いかに多くのことをエージェントに正確に伝えるか」が設計の中心課題になる。

そして Lopopolo は続ける。

> "Every time I have to type continue to the agent is like a failure of the harness to provide enough context."  
> — Ryan Lopopolo, 33:31

`continue` を打つたびに、それはハーネスの設計ミスだ。エージェントが途中で止まるのは「モデルの限界」ではなく、「コンテキスト提供の仕組みが足りていない」という設計上のフィードバックである。

この視点を持つと、次の問いが生まれる。**ハーネスをどう設計すれば、エージェントは自律的に走り続けられるか。**

---

## 全体アーキテクチャ

ハーネスの構成要素を3層で捉える。各層が「節約する希少資源」と対応している。

| 層 | パターン | 節約する希少資源 |
| --- | --- | --- |
| 構造 | ファイル行数ガードレール | コンテキストウィンドウ / モデル注意力 |
| linter | lint as prompt | 人間の注意力（レビュー介入の削減） |
| CI | Reviewer Agent | 人間の時間（コードレビューの自動化） |

---

## 実装パターン 1 — 構造がプロンプトになる

リポジトリ構造そのものがエージェントへの指示として機能するという考え方がある（講演トピック「エージェントを導く技術」11:05〜より）。1ファイルが巨大だとエージェントは局所的なコンテキストしか持てず、既存のヘルパー関数を無視して同じロジックを再実装してしまう問題（局所最適化）が起きやすい。

### 1ファイル350行以下ガードレール（Python / Ruff + pytest）

**動作環境：** Python 3.11+、pytest 8+、Ruff 0.4+

```
# tests/test_file_length.py
"""
ファイル行数ガードレール
- 350行を超えるファイルを CI で検出し、分割を促す
- エージェントが生成したファイルも対象にする
"""
from pathlib import Path
import pytest

MAX_LINES = 350
EXCLUDE_DIRS = {".git", ".venv", "node_modules", "__pycache__", "dist"}
EXCLUDE_EXTS = {".txt", ".md", ".json", ".yaml", ".yml", ".lock", ".toml"}

def collect_python_files(root: Path) -> list[Path]:
    return [
        p for p in root.rglob("*.py")
        if not any(part in EXCLUDE_DIRS for part in p.parts)
    ]

@pytest.mark.parametrize("filepath", collect_python_files(Path(".")))
def test_file_length(filepath: Path) -> None:
    """1ファイルが350行を超えたらテスト失敗 — 分割のサインとして扱う"""
    lines = filepath.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= MAX_LINES, (
        f"{filepath} は {len(lines)} 行あります（上限: {MAX_LINES} 行）。\n"
        f"モジュールを分割し、共通ロジックは src/utils/ 等のヘルパーに切り出してください。\n"
        f"参照: CONTRIBUTING.md#file-size-guideline"
    )
```

失敗時のエラーメッセージに「何をすべきか」と「どこを参照すべきか」を含めることがポイントだ。エージェントはこのメッセージを読んで自律的に修正行動を取れる。

### AGENTS.md への非機能要件の明文化

> "You can just simply say do not produce slop. Don't accept slop. You won't get slop in your codebase."  
> — Ryan Lopopolo, 09:39

「slop（雑なコード）を出すな」と明示するだけでアウトプット品質が向上するという主張に基づき、AGENTS.md に非機能要件を記述する。

```
<!-- AGENTS.md（リポジトリルートに配置） -->
# エージェント向け設計ガイドライン

## 非機能要件
- 1ファイルは350行以下に収める。超える場合はモジュール分割を先に行うこと
- 既存のヘルパー関数を使用する前に `src/utils/` と `src/shared/` を必ず参照すること
- ネットワーク呼び出しにはタイムアウト（推奨: 30秒）とリトライ（最大3回）を実装すること
- 型アノテーションを省略しないこと（mypy strict モード相当）
- 「slop」（意図不明な変数名、コピペコード、未使用インポート）は出力しないこと

## 参照すべきファイル
- `src/utils/http.py` — HTTP クライアント共通実装（タイムアウト・リトライ込み）
- `src/utils/retry.py` — リトライデコレータ
- `CONTRIBUTING.md` — コードスタイルと PR ルール
```

---

## 実装パターン 2 — lint as prompt

linter のエラーメッセージに「修正手順」を含めることで、lint 出力がエージェントへのジャストインタイム・プロンプトとして機能する（講演トピック「エージェントを導く技術」11:05〜より）。エージェントは lint エラーを読んで自律的に再修正できる。

### ESLint カスタムルール（Node 20+、ESLint 9+）

**動作環境：** Node.js 20+、ESLint 9+（flat config）

```
// eslint-rules/no-fetch-without-timeout.js
/**
 * カスタムルール: fetch() にタイムアウト設定を強制する
 * エラーメッセージに修正手順を含め、エージェントが自律修正できるようにする
 */

/** @type {import("eslint").Rule.RuleModule} */
export default {
  meta: {
    type: "problem",
    docs: {
      description: "fetch() calls must include an AbortController timeout",
    },
    schema: [],
    messages: {
      missingTimeout: [
        "fetch() にタイムアウトが設定されていません。",
        "以下のパターンで修正してください:\n",
        "  const controller = new AbortController();",
        "  const timeoutId = setTimeout(() => controller.abort(), 30_000);",
        "  try {",
        "    const res = await fetch(url, { signal: controller.signal });",
        "  } finally {",
        "    clearTimeout(timeoutId);",
        "  }",
        "\n参照: AGENTS.md#非機能要件",
      ].join("\n"),
    },
  },

  create(context) {
    return {
      CallExpression(node) {
        if (
          node.callee.type === "Identifier" &&
          node.callee.name === "fetch"
        ) {
          const args = node.arguments;
          const hasSignal =
            args.length >= 2 &&
            args[1].type === "ObjectExpression" &&
            args[1].properties.some(
              (p) =>
                p.type === "Property" &&
                p.key.type === "Identifier" &&
                p.key.name === "signal"
            );

          if (!hasSignal) {
            context.report({ node, messageId: "missingTimeout" });
          }
        }
      },
    };
  },
};
```

このルールを `eslint.config.js` に追加する。

```
// eslint.config.js
import noFetchWithoutTimeout from "./eslint-rules/no-fetch-without-timeout.js";

export default [
  {
    plugins: {
      "local-rules": { rules: { "no-fetch-without-timeout": noFetchWithoutTimeout } },
    },
    rules: {
      "local-rules/no-fetch-without-timeout": "error",
    },
  },
];
```

エラーが出たとき、エージェントはメッセージ内の修正手順をそのまま適用して再試行できる。`continue` を打つ必要がない。

---

## 実装パターン 3 — Reviewer Agent CI 統合

CI パイプラインに Reviewer Agent を組み込み、ドキュメント化した基準との照合を自動化するパターンだ（講演トピック「エージェントを導く技術」11:05〜より）。人間がコードレビューのボトルネックになる構造を解消する。

### GitHub Actions スケルトン（continue 頻度計測つき）

```
# .github/workflows/reviewer-agent.yml
# 動作環境: GitHub Actions、Python 3.11+
# 前提: ANTHROPIC_API_KEY または OPENAI_API_KEY を Secrets に設定済み

name: Reviewer Agent

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install openai PyGithub

      - name: Run Reviewer Agent
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          REPO: ${{ github.repository }}
        run: python scripts/reviewer_agent.py

      - name: Measure continue frequency (harness quality KPI)
        run: |
          # エージェントログから "continue" 発話回数を計測する最小実装
          # ログファイルは reviewer_agent.py が agent_run.log に出力する前提
          CONTINUE_COUNT=$(grep -c '^\[agent\] continue' agent_run.log 2>/dev/null || echo 0)
          echo "continue_count=${CONTINUE_COUNT}" >> "$GITHUB_STEP_SUMMARY"
          echo "## Harness Quality KPI" >> "$GITHUB_STEP_SUMMARY"
          echo "- continue 発話回数（低いほど良い）: **${CONTINUE_COUNT}**" >> "$GITHUB_STEP_SUMMARY"
          # 閾値を超えたら警告（即 fail にはしない — まずは計測から始める）
          if [ "$CONTINUE_COUNT" -gt 5 ]; then
            echo "::warning::continue 頻度が高い（${CONTINUE_COUNT}回）。AGENTS.md のコンテキスト補足を検討してください。"
          fi
```

### Reviewer Agent の本体スクリプト（最小実装）

```
# scripts/reviewer_agent.py
"""
Reviewer Agent 最小実装
- PR の diff を取得し、AGENTS.md の非機能要件との照合を LLM に依頼する
- 指摘があれば PR にコメントとして投稿する
- 動作環境: Python 3.11+、openai 1.30+、PyGithub 2.3+
"""

import os
import subprocess
import logging
from github import Github
from openai import OpenAI

logging.basicConfig(
    filename="agent_run.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

REVIEW_CRITERIA = """
以下の非機能要件を満たしているか確認してください:
1. ネットワーク呼び出しにタイムアウト（30秒以内）とリトライ（最大3回）が実装されているか
2. 新規ファイルが350行を超えていないか
3. 型アノテーションが省略されていないか
4. 既存ヘルパー関数の重複実装をしていないか（src/utils/ 等を参照しているか）

問題がなければ「LGTM」とだけ回答してください。
問題がある場合は「ISSUE: <行番号> — <具体的な修正案>」の形式で列挙してください。
"""

def get_pr_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout[:8000]  # コンテキストウィンドウ節約のため上限設定

def review_with_agent(diff: str) -> str:
    client = OpenAI()
    logging.info("Reviewer Agent 開始")

    # "continue" を打たせないようプロンプトを完結させる
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": REVIEW_CRITERIA},
            {"role": "user", "content": f"以下の diff をレビューしてください:\n\n```diff\n{diff}\n```"},
        ],
        max_tokens=1024,
    )
    result = response.choices[0].message.content or ""
    logging.info("Reviewer Agent 完了: %s", result[:100])
    return result

def post_review_comment(body: str) -> None:
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["REPO"])
    pr = repo.get_pull(int(os.environ["PR_NUMBER"]))
    if "LGTM" not in body:
        pr.create_issue_comment(f"## Reviewer Agent\n\n{body}")
        logging.info("PR コメント投稿済み")
    else:
        logging.info("LGTM — コメントなし")

if __name__ == "__main__":
    diff = get_pr_diff()
    review_result = review_with_agent(diff)
    post_review_comment(review_result)
```

### continue 頻度を計測するメトリクス（最小実装）

エージェントログから `continue` 発話をカウントして KPI とする最小スクリプト。

```
#!/usr/bin/env bash
# scripts/measure_continue_frequency.sh
# 動作環境: bash 5+、GNU grep
# 使い方: ./scripts/measure_continue_frequency.sh [ログファイルパス]
#
# ログフォーマット想定（1行1発話）:
#   [agent] continue
#   [agent] <その他の発話>
#   [human] <人間の入力>

LOG_FILE="${1:-agent_run.log}"

if [[ ! -f "$LOG_FILE" ]]; then
  echo "ログファイルが見つかりません: $LOG_FILE"
  exit 1
fi

TOTAL_TURNS=$(grep -c '^\[agent\]' "$LOG_FILE" 2>/dev/null || echo 0)
CONTINUE_COUNT=$(grep -c '^\[agent\] continue' "$LOG_FILE" 2>/dev/null || echo 0)

if [[ "$TOTAL_TURNS" -eq 0 ]]; then
  echo "エージェント発話が0件です。"
  exit 0
fi

# continue 率を計算（bash は浮動小数点非対応のため awk を使用）
CONTINUE_RATE=$(awk "BEGIN { printf \"%.1f\", ${CONTINUE_COUNT} / ${TOTAL_TURNS} * 100 }")

echo "=== Harness Quality KPI ==="
echo "総エージェント発話数  : ${TOTAL_TURNS}"
echo "continue 発話数        : ${CONTINUE_COUNT}"
echo "continue 率            : ${CONTINUE_RATE}%"
echo ""
echo "目標: continue 率 < 10%"
echo "現状: ${CONTINUE_RATE}% — $([ "${CONTINUE_COUNT}" -le $((TOTAL_TURNS / 10)) ] && echo 'OK' || echo '要改善: AGENTS.md のコンテキスト補足を検討')"
```

---

## 検証と落とし穴

### フィードバックループの全体像

### 落とし穴 1 — 過剰設計リスク（The Bitter Lesson）

Lopopolo 自身が講演で指摘している重要なリスクがある（timestamp 不明のため要約として記述）。モデルの急速な進化によって、精巧に作り込んだハーネスが数ヶ月後に不要になる可能性がある。

たとえば「リポジトリ全体の依存グラフをエージェントに渡す複雑なスクリプト」を今作っても、次世代モデルがリポジトリを自律的に探索できるようになれば価値がゼロになる。

**判断基準の目安：**

* 実装コストが 2〜3 日以内で、メンテナンスが容易なものは作る
* 複雑なエージェントオーケストレーション、カスタムコンテキストグラフ等は「モデルが今できないこと」を前提にしているので、モデル更新ごとに見直す
* まず AGENTS.md（テキストファイル）から始め、コードが必要になったら追加するという順序が安全

### 落とし穴 2 — 局所最適化（Local Context Trap）

エージェントはリポジトリ全体ではなく、目の前のファイルのコンテキストのみでコードを生成する傾向がある（講演のリスクセクションより要約）。その結果、`src/utils/http.py` に完璧なリトライ付き HTTP クライアントがあるのに、タスクファイルの直下に同等ロジックを再実装するケースが発生しやすい。

**対策：**

1. `AGENTS.md` に「既存ヘルパーを参照せよ」と明示する（パターン1で示した例）
2. カスタム linter でヘルパーを使わず `requests.get()` / `fetch()` を直接呼ぶケースを検出する
3. ディレクトリ構造を浅く保ち、`src/utils/index.ts` や `__init__.py` で公開 API を明示する

### 落とし穴 3 — linter メッセージが曖昧すぎる

エラーメッセージに「修正してください」とだけ書いてもエージェントは自律修正できない。**何をどこに書くか** を具体的に含める必要がある。

悪い例：

```
error: fetch() にタイムアウトがありません
```

良い例（パターン2で示した通り）：

```
fetch() にタイムアウトが設定されていません。
以下のパターンで修正してください:
  const controller = new AbortController();
  ...
参照: AGENTS.md#非機能要件
```

---

## まとめと次に試すこと

コードを書くコストがほぼゼロになった世界では、人間の設計リソースをどこに集中させるかが勝負になる。ハーネス設計の3パターンはその答えの一部だ。

**優先度順のアクションリスト：**

1. **今日できる：AGENTS.md を作る**

   * ファイル行数制限、参照すべきヘルパー、非機能要件（タイムアウト・リトライ・型アノテーション）を書く
   * コスト：1〜2時間。効果：翌日から全エージェントセッションに適用される
2. **今週できる：linter メッセージに修正手順を追加する**

   * 既存のカスタムルールのエラーメッセージを改善する（コードブロック例を含める）
   * 新規ルールを1〜2個追加する（ファイル行数、`fetch` タイムアウト等）
3. **来週以降：Reviewer Agent を CI に追加する**

   * 上記のスケルトンをベースにチームのチェック基準を REVIEW\_CRITERIA に反映する
   * まず「LGTM / ISSUE」の2値出力から始め、誤検知率を確認してから本格運用する
4. **継続：continue 頻度を計測してフィードバックループを回す**

   * `measure_continue_frequency.sh` を定期実行し、率が高いセッションの AGENTS.md を改善する

再利用できる設計原則は一つに集約できる。**エージェントへのコンテキストを「その場で」「正確に」届ける仕組みを、コードではなく構造・設定・メッセージとして埋め込む**。これがハーネス設計の本質だ。

---

## 出典

* Ryan Lopopolo, "Harness Engineering: How to Build Software When Humans Steer, Agents Execute", AI Engineer YouTube チャンネル, 2026-04-17  
  URL: <https://www.youtube.com/watch?v=am_oeAoUhew>
  + 02:15 — "Code is free. We have an abundance of code to solve the problems that we come across."
  + 03:19 — GPT-5.2 がソフトウェアエンジニアの仕事を完全遂行できるという登壇者の見解
  + 05:12 — "The scarce resources in this world that we see today are three things. human time, human and model attention and model context window."
  + 09:39 — "You can just simply say do not produce slop. Don't accept slop. You won't get slop in your codebase."
  + 11:05〜 — lint as prompt / Reviewer Agent CI 統合 / 構造がプロンプトになる の説明
  + 33:31 — "Every time I have to type continue to the agent is like a failure of the harness to provide enough context."
