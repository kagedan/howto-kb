---
id: "2026-05-29-claude-code-hooksで作る7つの安全装置-pretooluseposttooluse-01"
title: "Claude Code Hooksで作る7つの安全装置 ─ PreToolUse/PostToolUse 実装集"
url: "https://zenn.dev/kenimo49/articles/claude-code-hooks-7-safety-patterns"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

Claude CodeにCLAUDE.mdで「`rm -rf` は使うな」と書いても、エージェントは時々忘れます。私は1度、テスト用のディレクトリ削除が思いがけず親フォルダに刺さって、半日分の作業履歴を消したことがあります。あの夜以来、お願いベースのルールは信用しなくなりました。

信用すべきはハーネス側の強制力、つまり**Hooks** です。Hooksはエージェントのライフサイクルの特定タイミングでスクリプトを発火させる仕組みで、CLAUDE.mdに書いた指示の「ほぼ毎回」を、「例外なく毎回」に変える装置です。

本記事では、私が実運用で入れている7つの安全装置を、`settings.json` 設定例と発火スクリプトのセットで紹介します。

![Claude Code Hooksのライフサイクル図](https://static.zenn.studio/user-upload/deployed-images/cf99b918a895540845b560d6.png?sha=dcf4dc017c59d38d207468f482d76bd6b278a680)

## Hooksとは何か

Hooksは `.claude/settings.json` (プロジェクト共有) または `~/.claude/settings.json` (ユーザ個人) に書きます。2026年5月時点で公式が提供しているライフサイクルイベントは12種類以上あり、代表的なものはこの4つです。

| Event | 発火タイミング | 主な用途 |
| --- | --- | --- |
| `PreToolUse` | ツール呼び出しの直前 | 危険コマンドの遮断、入力書き換え |
| `PostToolUse` | ツール呼び出しの直後 | diff保存、lint、テスト発火 |
| `Stop` | セッション終了時 | コスト集計、通知、引継ぎ |
| `SubagentStop` | サブエージェント終了時 | 並列実行の整合性チェック |

このほか `Notification` / `PreCompact` / `SessionStart` / `UserPromptSubmit` などもありますが、まずはこの4種類を押さえれば本記事の安全装置は全部組めます。

Hookスクリプトの基本動作はシンプルです。stdinからJSONを受け取り、stdoutにJSONを返すか、exit code 2でブロックする。それだけです。

```
{
  "session_id": "abc123",
  "cwd": "/home/iris/repos/myproj",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/build"
  }
}
```

ブロックしたいときは `hookSpecificOutput.permissionDecision: "deny"` を返す、もしくは exit 2 でstderrに理由を書く。この2択です。

それでは7つの安全装置を順に紹介します。

冒頭の私の事故を二度と起こさないための装置です。`rm -rf` を含むBashコマンドはPreToolUseで問答無用にdenyします。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh"
          }
        ]
      }
    ]
  }
}
```

スクリプトはこうなります。

```
#!/bin/bash
# .claude/hooks/block-rm.sh
CMD=$(jq -r '.tool_input.command' < /dev/stdin)

if echo "$CMD" | grep -qE '(rm -rf|rm -fr|rm --recursive)'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "rm -rf is blocked. Use trash-cli or specify the target file explicitly."
    }
  }'
  exit 0
fi
exit 0
```

denyされたエージェントはreasonをそのまま読み、別の方法を提案してきます。`trash-put` を使えと書いておけば、そちらに切り替えてくれます。

## 安全装置2: PostToolUseで `git diff` を自動キャプチャ

エージェントが大量のEditを連続でやると、後で「どこを触ったか」が追えなくなります。PostToolUseで毎回 `git diff` をスナップショットファイルに追記すれば、セッション終了後に変更履歴を一望できます。

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/snapshot-diff.sh"
          }
        ]
      }
    ]
  }
}
```

```
#!/bin/bash
# .claude/hooks/snapshot-diff.sh
SESSION=$(jq -r '.session_id' < /dev/stdin)
SNAPSHOT_DIR="${CLAUDE_PROJECT_DIR}/.claude/snapshots"
mkdir -p "$SNAPSHOT_DIR"

cd "$CLAUDE_PROJECT_DIR" || exit 0
{
  echo "=== $(date -Iseconds) ==="
  git diff --stat HEAD 2>/dev/null || true
  echo "---"
} >> "$SNAPSHOT_DIR/${SESSION}.log"
exit 0
```

セッション後に `.claude/snapshots/abc123.log` を見れば、エージェントがどのファイルを何行触ったかが時系列で残ります。私はこれを後述のStop hookで `git diff > final.patch` と組み合わせて、ロールバック可能な状態を担保しています。

ローカル開発中のエージェントが、うっかり本番DBの接続文字列を含むコマンドを実行する事故は、想像以上に起こります。`PROD_DATABASE_URL` や `prod.cluster` のような文字列がBashコマンドに混入したら止めます。

```
#!/bin/bash
# .claude/hooks/block-prod-db.sh
CMD=$(jq -r '.tool_input.command' < /dev/stdin)

PATTERNS='(PROD_DATABASE_URL|prod\.cluster|prod-db|amazonaws\.com:5432.*prod)'
if echo "$CMD" | grep -qE "$PATTERNS"; then
  echo "Production DB endpoint detected in command. Refusing for safety." >&2
  exit 2
fi
exit 0
```

ここではJSON出力ではなくexit 2を使っています。理由は単純で、エージェントに見せる文言がそのまま `stderr` の1行で済むからです。短いメッセージならexit 2のほうが書きやすい場面が多いです。

settings.jsonの `matcher` は `Bash` 単独で十分ですが、SQLクライアントを別ツール化している場合は `Bash|mcp__postgres__.*` のようにMCPツールも含めるとさらに堅くなります。

## 安全装置4: Stopで未コミット変更をTelegram通知

私が一番使っているのが、これです。エージェントが作業を終えたタイミングで未コミットの変更があれば、Telegramに「レビュー待ちが残ってるよ」と送ります。

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/notify-uncommitted.sh"
          }
        ]
      }
    ]
  }
}
```

```
#!/bin/bash
# .claude/hooks/notify-uncommitted.sh
cd "$CLAUDE_PROJECT_DIR" || exit 0

CHANGED=$(git status --porcelain | wc -l)
if [ "$CHANGED" -gt 0 ]; then
  PROJ=$(basename "$CLAUDE_PROJECT_DIR")
  MSG="🪝 [${PROJ}] Claude Codeが作業終了。未コミットの変更が${CHANGED}件あります。"
  curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
    -d "chat_id=${TG_CHAT_ID}" \
    -d "text=${MSG}" > /dev/null
fi
exit 0
```

これを入れる前は、長時間タスクを夜中に走らせて、朝起きたら「コードは書いてくれたが、コミットされていない」状態を発見することがありました。今は風呂上がりに通知が鳴って、その場でレビュー→コミットまで持っていけます。

## 安全装置5: PostToolUseで `shellcheck` をMUST通過させる

エージェントが生成するシェルスクリプトは、quotingが甘いことが多いです。PostToolUseで `.sh` ファイルへのEdit/Writeを検知したら、`shellcheck` を走らせて、警告が出たらエージェント側に修正を要求します。

```
#!/bin/bash
# .claude/hooks/shellcheck-must.sh
FILE=$(jq -r '.tool_input.file_path' < /dev/stdin)

case "$FILE" in
  *.sh|*.bash) ;;
  *) exit 0 ;;
esac

if ! command -v shellcheck > /dev/null; then
  exit 0
fi

OUT=$(shellcheck -f gcc "$FILE" 2>&1)
if [ -n "$OUT" ]; then
  echo "shellcheck found issues in $FILE:" >&2
  echo "$OUT" >&2
  exit 2
fi
exit 0
```

exit 2でstderrに `shellcheck` の出力をそのまま渡すと、エージェントは内容を読んで該当箇所を修正し、Edit→PostToolUseのループでクリーンな状態まで自走します。CLAUDE.mdに「shellcheckを通せ」と書くのと、Hookで強制するのは、「ほぼ毎回」と「例外なく毎回」の違いです。

エージェントが `cat .env` をしてシークレットをコンテキストに取り込むと、それがログに残ったり、外部APIへのリクエストヘッダに混入したりする可能性があります。Readツールと、`cat`/`head`/`grep` 系Bashの両方をブロックします。

```
#!/bin/bash
# .claude/hooks/block-env-read.sh
EVENT=$(jq -r '.hook_event_name' < /dev/stdin)
INPUT=$(cat)

deny() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
}

TOOL=$(echo "$INPUT" | jq -r '.tool_name')
case "$TOOL" in
  Read)
    PATH_=$(echo "$INPUT" | jq -r '.tool_input.file_path')
    if [[ "$PATH_" == *".env"* ]]; then
      deny "Reading .env files is blocked. Use env var names only."
      exit 0
    fi
    ;;
  Bash)
    CMD=$(echo "$INPUT" | jq -r '.tool_input.command')
    if echo "$CMD" | grep -qE '(cat|head|tail|less|more|grep)[^|]*\.env'; then
      deny "Shell read of .env is blocked. Reference variables by name."
      exit 0
    fi
    ;;
esac
exit 0
```

`matcher` 側は `Read|Bash` の2つを束ねます。`PATH_` という変数名は `PATH` 衝突回避のため意図的に付けています。`shellcheck` が文句を言ってきたら、それは安全装置5が仕事をしている証拠です。

## 安全装置7: Stopでトークンコスト集計をログ

最後はOPEX管理。1セッションあたりのコストを毎回ログに残しておくと、月末に「先月のClaude Code費用は何に飛んだか」を1ファイルで遡れます。

```
#!/bin/bash
# .claude/hooks/log-cost.sh
TRANSCRIPT=$(jq -r '.transcript_path' < /dev/stdin)
SESSION=$(jq -r '.session_id' < /dev/stdin)

if [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

# transcript.jsonlは1行1メッセージ。usage.input_tokens / output_tokensを合算
IN=$(jq -s '[.[] | .message.usage.input_tokens // 0] | add' "$TRANSCRIPT")
OUT=$(jq -s '[.[] | .message.usage.output_tokens // 0] | add' "$TRANSCRIPT")
CACHE=$(jq -s '[.[] | .message.usage.cache_read_input_tokens // 0] | add' "$TRANSCRIPT")

LOG="$HOME/.claude/cost.jsonl"
jq -n \
  --arg ts "$(date -Iseconds)" \
  --arg sid "$SESSION" \
  --arg proj "$(basename "$CLAUDE_PROJECT_DIR")" \
  --argjson in "$IN" --argjson out "$OUT" --argjson cache "$CACHE" \
  '{ts: $ts, session: $sid, project: $proj, input: $in, output: $out, cache: $cache}' \
  >> "$LOG"
exit 0
```

`$HOME/.claude/cost.jsonl` を週次で `jq` 集計すれば、プロジェクト別の消費トークン数が出ます。私は土曜の朝にこれを集計して、「先週どのプロジェクトに何トークン使ったか」をTelegramに通知する別cronと組み合わせています。

## 7パターンの優先順位とハマりポイント

![7安全装置のマトリクス](https://static.zenn.studio/user-upload/deployed-images/5bbeba78b69ffe19be0186f0.png?sha=9a77018c6ca7ecf5b934ad5c0e30cb2b19743a2d)

優先度HIGHは1番 (rm遮断)、3番 (本番DB)、6番 (.env保護) の3本です。これは事故ったときの被害が大きいので、Claude Codeを入れた初日に設定しておきます。残りは観測系なので、痛い目を見てから足しても遅くありません。

実装中のハマりポイントを3つだけ書いておきます。

**1つ目: stdinから読むのを忘れる**

JSONはstdinから来ます。`$1` や環境変数で取ろうとすると空文字が返ります。`jq -r '.tool_input.command' < /dev/stdin` で受けるのが定石です。

**2つ目: exit code 2の意味を勘違いする**

exit 2は「ブロックして、stderrの内容をエージェントに見せる」です。exit 1や3はノンブロッキングのエラー扱いで、ツール実行は止まりません。「止めたつもりが止まってなかった」事故の8割はここです。

**3つ目: `${CLAUDE_PROJECT_DIR}` を相対パスで書く**

settings.jsonにスクリプトパスを書くとき、`./.claude/hooks/foo.sh` のような相対パスはcwdに依存して壊れます。`${CLAUDE_PROJECT_DIR}/.claude/hooks/foo.sh` と必ず展開して書きます。

## Cursor / Codex CLI と比べて何が違うか

2026年時点で、Cursorは `beforeShellExecution` / `beforeMCPExecution` の2イベントに絞ったhookシステムを用意しています。リスクの大きいシェルとMCPだけに集中していて、設定は楽です。Codex CLIは早い段階で `hooks.json` を入れましたが、PreToolUse相当を1イベントに集約して、ツール種別をmatcher側で振り分ける設計です。

Claude Codeは12+イベントと一番広く、`Stop` `SubagentStop` `PreCompact` のようなセッション境界のフックまで持っています。安全装置1〜3はCursorでも組めますが、4と7のような「終了時に集計・通知」はClaude Codeの強みです。逆に「設定がシンプルで済む」のはCursor、と覚えておくと良いです。

## まとめ

CLAUDE.mdへの指示は「お願い」、Hooksは「強制」です。エージェントが信頼に値する仕事をするには、信頼を担保する仕掛けが先にあるべきです。

今日入れるべきHIGH優先度の3本は決まっています。`rm -rf` 遮断、本番DB検知、.env保護。これだけで夜中に走らせる長時間タスクの怖さがかなり減ります。残りの4本は、運用しながらログを見て、必要なものから足していけばOKです。

面白くいきましょう。

!

📖 **この記事の内容を体系的にまとめた本を公開しています**

2024年プロンプト、2025年コンテキスト、2026年ハーネス。3つの概念の全体像と違い、OpenAI・Anthropic・LangChain・Martin Fowlerの解釈差異、6つの構成要素、hooks/lifecycle、Self-Evolving Agentまでを体系化した一冊。

👉 **[ハーネス・エンジニアリング ─ AIを"使う"から"操る"へ](https://zenn.dev/kenimo49/books/harness-engineering-guide)**

## 参考
