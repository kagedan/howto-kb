---
id: "2026-06-10-claude-code-の-pretooluse-フックで-ai-エージェントの行動を物理的に制御す-01"
title: "Claude Code の PreToolUse フックで AI エージェントの行動を物理的に制御する"
url: "https://zenn.dev/penne_inc/articles/claude-code-pretooluse-hook-permission-control"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "OpenAI", "zenn"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

`.claude/settings.json` の `permissions.deny` だけでは、AI エージェントの暴走は止まりませんでした。

「安全文字起こし」の開発では、複数の Claude Code エージェントが並行で動いています。lead が dev や PO に worktree 隔離で作業を委任するのですが、その隔離が cwd 継承問題で 1 週間に 13 回破られた話を別の記事に書きました。インシデント側の整理はそちらに譲ります。

この記事は、その対策として実装した PreToolUse フックの中身を書きます。「設定ファイルで止められないなら、シェルスクリプトで止めればいい」という、結論にしてみれば当たり前の話です。

---

## 設定ファイルだけでは AI は止まらない

最初に試したのは `permissions.deny` の拡張でした。`.claude/settings.json` でツール呼び出しのパターンを拒否リスト化する方法です。

```
{
  "permissions": {
    "deny": [
      "Edit(/Users/.../main-repo/*)"
    ]
  }
}
```

ただこの方式には2つの限界がありました。

1. **静的なパターンマッチしか効かない**。エージェントが「同じ親リポジトリの絶対パス」を別の表現で渡してくれば素通りします
2. **cwd の状態を判定できない**。subagent が main repo に居る状態で相対パス Edit すれば、deny パターンに一切引っかかりません

「動的な状態」を見る必要があると気づいたのが、フック導入の出発点でした。

---

Claude Code には `PreToolUse` という hook 機構があります。ツール呼び出しの直前に任意のシェルスクリプトを実行できる仕組みです。

特性は次のとおりです。

* **stdin で payload を受け取る**：`tool_name` / `tool_input` / `cwd` / `session_id` などが JSON で渡る
* **exit code でツール実行を制御する**：`exit 0` = 通過、`exit 2` = ブロック
* **stderr が Claude に reasoning として渡る**：ブロック理由を書けば、エージェントが次の判断材料にできる
* **動的判定が可能**：branch 状態・git status・環境変数・他コマンドの実行結果を使って判定できる

`.claude/settings.json` への登録例：

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/worktree-isolation-guard.sh"
          }
        ]
      }
    ]
  }
}
```

`matcher` で対象ツールを絞り、`command` で実行するスクリプトを指定するだけです。

---

## worktree-isolation-guard.sh の設計

実装したフックの判定ロジックは3段階です。

### 1. lead は無条件で許可

worktree 隔離が問題になるのは subagent（lead 以外のエージェント）が main repo に書き込もうとしたときだけです。lead はそもそも main repo で作業するのが正しい役割なので、即 `exit 0`。

```
AGENT_TYPE="${CLAUDE_AGENT_TYPE:-lead}"

if [[ "$AGENT_TYPE" == "lead" || -z "$AGENT_TYPE" ]]; then
  exit 0
fi
```

### 2. subagent の worktree ルートを判定する

subagent の cwd から `git rev-parse --show-toplevel` で worktree のルートを取得します。

```
WORKTREE_ROOT="$(git -C "$CALL_CWD" rev-parse --show-toplevel 2>/dev/null || true)"
```

ここで取得できなければ「判断できないので素通し」（`exit 0`）。**「不確実なら通す」が基本ポリシー**です。厳しすぎると正常な作業まで止まり、開発が動かなくなります。

### 3. worktree ルートが main repo と一致したらブロック

これが核心です。subagent の worktree ルートが `$CLAUDE_PROJECT_DIR`（main repo）と一致するなら、それはそもそも隔離されていない危険状態。Bash/Edit/Write をまとめてブロックします。

```
if [[ "$WORKTREE_ROOT" == "$MAIN_REPO" ]]; then
  echo "BLOCK: subagent (${AGENT_TYPE}) が main repo に居ます。" >&2
  echo "対処: lead に戻り、'git worktree add' で隔離 worktree を作成してください。" >&2
  exit 2
fi
```

これで `isolation: "worktree"` が cwd 継承問題で失敗していても、フックが最後の砦になります。

### 補助：Edit/Write の絶対パス検査

3段階の判定をパスした subagent でも、絶対パスで main repo を直接指していればブロックします。

```
case "$FILE_PATH" in
  "$MAIN_REPO"/*|"$MAIN_REPO")
    if [[ "$FILE_PATH" != "$WORKTREE_ROOT"/* ]]; then
      echo "BLOCK: main repo の絶対パスで ${TOOL_NAME} を実行しようとしました。" >&2
      exit 2
    fi
    ;;
esac
```

---

## 実運用での誤検知ゼロ

フック導入後、1週間で起きていた13件の隔離破れはゼロになりました。同時に、誤検知（本来許可すべき操作のブロック）も0件でした。

「不確実なら通す」設計が効いていて、判断材料が足りないケースは安全側に倒して素通しします。具体的には次のような場合です。

* `jq` がインストールされていない環境
* `CLAUDE_PROJECT_DIR` が未設定
* `git rev-parse` が失敗する（git 管理外のディレクトリ）
* payload が空

「フックは完璧であろうとしない」というのが意外と大事でした。誤検知でブロックされると、エージェントは「やり直す」ではなく「タスクが失敗した」と判断して止まることが多く、生産性に直撃します。

---

## フック設計の注意点

### exit code は 0 か 2 のどちらか

PreToolUse フックでは `exit 1` を避けるのが安全です。`exit 2` だけが「Claude に reasoning として stderr が渡る」仕様で、`exit 1` だと Claude には届かない一般的なエラー扱いになります。明示的なブロックは必ず `exit 2`。

### bypass 機構を組み込む

完璧なフックは存在しないので、緊急時の bypass を最初から組み込んでおきます。

```
if [[ "${WORKTREE_GUARD_BYPASS:-0}" == "1" ]]; then
  exit 0
fi
```

`WORKTREE_GUARD_BYPASS=1` を export すれば全許可。Owner 判断が必要な場面でだけ使う想定です。「フックが間違っているときに開発が止まる」リスクをここでヘッジします。

### branch-aware の追加検査

特殊な例ですが、`.ai/coordination/HANDOFF.md` は通常 lead 専任ファイルです。一方で PR ブランチ上では subagent も触る必要がある。そこで branch 名で allow/block を切り替えています。

```
case "$FILE_PATH" in
  */.ai/coordination/HANDOFF.md)
    CUR_BRANCH="$(git -C "$WORKTREE_ROOT" branch --show-current 2>/dev/null || true)"
    case "$CUR_BRANCH" in
      dev/*|lead/*|po/*|webmaster/*) ;;  # allow
      *) exit 2 ;;
    esac
    ;;
esac
```

「ホワイトリスト」ではなく「コンテキストで判定」する方が、実運用では誤検知が減りました。

---

## エージェントの善意を信じつつ、構造で守る

エージェントに「やってはいけないこと」をプロンプトで書くのは限界があります。LLM は確率的にしか従わないし、状況によって判断を変える。それは長所でもあるけれど、ガードに使う領域では短所になる。

フックは「エージェントの判断に依存しない、確定的なガード」です。プロンプトを補完するもの、と捉えるとちょうどいい。エージェントに任せたい領域はプロンプトで、確実に守りたい領域はフックで、という分担。

エージェントが悪意で逸脱することはほぼないと思っています。でも善意で「便利だから親リポジトリの方を直接編集しちゃおう」と判断することはある。その善意を信じつつ、構造で止める。

`permissions.deny` に1行書いて済む話だと思っていたのが、結局 145 行のシェルスクリプトになりました。それでもこれ以上シンプルな解決策が見つからなかったので、しばらくこの構成で運用するつもりです。

---

[安全文字起こし](https://anzen-mojiokoshi.org)というサービスを作っています。取材や会議の音声を私たちの専用サーバーで処理し、Google や OpenAI などの外部AI企業には転送しない設計の SaaS です。プライベートな会話を外部の AI サービスに気軽に渡してよいのか？という不安から生まれたプロジェクトです。複数の Claude Code エージェントと一緒に開発しています。
