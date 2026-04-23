---
id: "2026-03-23-clickhouseでclaude-codeのセッションログを実現する-01"
title: "ClickHouseでClaude Codeのセッションログを実現する"
url: "https://qiita.com/skillogy/items/23b8f09f203ba3bbb834"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## Claude Codeはセッションをまたげない

Claude Codeを使い込んでいる開発者なら、一度はこう思ったことがあるはずです。

「昨日のセッションの続きから再開したいのに、コンテキストが全部消えている」

Claude Codeには`~/.claude/`配下にMarkdownベースのメモリ機能がありますが、これは手動で「覚えて」と指示する必要があり、作業の全体像を自動的に保持するものではありません。

そこで本記事では、Claude CodeのHooks機能を使ってセッションの内容をClickHouseに自動蓄積し、新しいセッション開始時に前回の作業内容を自動で注入する仕組みを構築します。

## 全体像

```
【記録フェーズ：セッション中に自動実行】
Claude Code
  ├─ UserPromptSubmit hook → ユーザーの指示を記録
  ├─ PostToolUse hook      → ファイル編集・コマンド実行を記録
  └─ Stop hook             → Claudeの応答を記録 + セッション要約を生成
        │
        ▼
  ClickHouse (claude_memory DB)

【復元フェーズ：次のセッション開始時に自動実行】
Claude Code (新セッション)
  └─ SessionStart hook
        │
        ▼
  ClickHouseから前回の要約を取得
        │
        ▼
  stdoutで出力 → Claude Codeのコンテキストに注入
```

ポイントは2つです。

1. 記録はバックグラウンドで自動実行 — 操作を一切変えなくていい
2. 復元はSessionStart hookで自動注入 — 新セッション開始時に前回の文脈が自動で渡される

## Hooksの基本

Claude CodeのHooksは、特定のイベント発生時にシェルコマンドを実行する仕組みです。MCPサーバーの開発は不要で、設定ファイルとシェルスクリプトだけで動きます。

今回使うイベント

| イベント | タイミング | stdinで受け取れるデータ |
| --- | --- | --- |
| `UserPromptSubmit` | ユーザーがプロンプト送信時 | `prompt`（入力テキスト） |
| `PostToolUse` | ツール実行完了時 | `tool_name`, `tool_input`（ツール名とパラメータ） |
| `Stop` | Claudeの応答完了時 | `session_id`, `transcript_path`（会話記録ファイル） |
| `SessionStart` | セッション開始時 | `session_id`, `cwd` |

全イベント共通で `session_id`（セッション識別子）と `cwd`（作業ディレクトリ）が渡されます。

**2つの重要な仕様**

* `SessionStart`のHookがstdoutに文字列を出力すると、その内容がClaude Codeのコンテキストに注入される。 これを使って前回のセッション情報を渡します。
* `Stop`イベントでは`transcript_path`が渡される。これはセッション全体の会話記録（JSONL形式）へのパスで、Claudeの応答テキストを含んでいます。

## ClickHouseのテーブル設計

```
CREATE DATABASE IF NOT EXISTS claude_memory;

-- セッション中のイベントを記録
CREATE TABLE claude_memory.events
(
    session_id   String,
    event_type   LowCardinality(String),
    tool_name    LowCardinality(String),
    content      String,                  -- プロンプト / ツール入力JSON / Claude応答
    project_dir  String,
    created_at   DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (project_dir, created_at, session_id)
TTL created_at + INTERVAL 90 DAY;

-- セッション終了時に生成する要約
CREATE TABLE claude_memory.session_summaries
(
    session_id   String,
    project_dir  String,
    summary      String,    -- セッションの要約テキスト
    files_touched Array(String),
    commands_run  Array(String),
    started_at   DateTime,
    ended_at     DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree(ended_at)
ORDER BY (project_dir, session_id);
```

**2テーブル構成にした理由**

* `events` — ユーザー入力・ツール実行・Claude応答の全イベントを時系列で蓄積
* `session_summaries` — セッション終了時に要約を生成して保存。次回復元時はこのテーブルだけ参照すればよく、高速に読める

**設計のポイント**

* `LowCardinality` — イベント種別やツール名はカーディナリティが低いので圧縮効率が上がる
* `ORDER BY (project_dir, ...)` — 復元時に「同じプロジェクトの直近セッション」を引くクエリが最も頻繁に実行されるため、先頭に配置
* `TTL` — 90日で自動削除。メンテナンス不要
* `ReplacingMergeTree` — 同一セッションの要約が複数回INSERTされても、最新の`ended_at`のレコードだけ残る

## なぜClickHouseか

「セッション記録ならSQLiteやPostgreSQLでもいいのでは？」という疑問は当然あります。少人数で使うだけならSQLiteでも十分です。ClickHouseが活きるのは、以下のような場合です。

* **ログが数十万件に膨らんでも集計が一瞬** — 「過去3ヶ月で最も変更が多かったファイルは？」のような横断分析
* **TTLで古いデータが自動消滅** — メンテナンス不要
* **JSON関数が充実** — `tool_input`のようなJSON文字列の中身をSQLで直接掘れる
* **ClickHouse Cloudなら運用ゼロ** — ローカルにDBを立てる必要もない

## 記録スクリプトの実装

### イベント記録（`record.sh`）

`~/.claude/hooks/record.sh` は全イベント共通の記録スクリプトです。イベント種別に応じて記録内容を切り替えます。

```
#!/bin/bash
CH_URL="${CLICKHOUSE_URL:-http://localhost:8123}"
CH_AUTH="${CLICKHOUSE_AUTH:-default:your-pass}"

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""')
EVENT_TYPE=$(echo "$INPUT" | jq -r '.hook_event_name // ""')
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')
PROJECT_DIR=$(echo "$INPUT" | jq -r '.cwd // ""')

# イベント種別に応じてcontentを抽出
case "$EVENT_TYPE" in
  UserPromptSubmit)
    CONTENT=$(echo "$INPUT" | jq -r '.prompt // ""')
    ;;
  PostToolUse)
    CONTENT=$(echo "$INPUT" | jq -c '.tool_input // {}')
    # 10KB超は切り詰め（大きなdiff等）
    [ ${#CONTENT} -gt 10240 ] && CONTENT='{"truncated": true}'
    ;;
  Stop)
    # transcriptから最後のassistant応答を取得
    TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // ""')
    if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
      CONTENT=$(tail -r "$TRANSCRIPT" \
        | jq -r 'select(.type == "assistant") | .message.content[] | select(.type == "text") | .text' \
        2>/dev/null | head -1)
      # 10KB超は切り詰め
      [ ${#CONTENT} -gt 10240 ] && CONTENT="${CONTENT:0:10240}...(truncated)"
    fi
    TOOL_NAME="assistant_response"
    ;;
  *)
    CONTENT=""
    ;;
esac

# エスケープしてINSERT（バックグラウンド実行）
escape() { echo "$1" | sed "s/'/''/g"; }

curl -sf --max-time 3 --user "$CH_AUTH" "$CH_URL" -d "
  INSERT INTO claude_memory.events
    (session_id, event_type, tool_name, content, project_dir)
  VALUES (
    '$(escape "$SESSION_ID")', '$(escape "$EVENT_TYPE")',
    '$(escape "$TOOL_NAME")', '$(escape "$CONTENT")',
    '$(escape "$PROJECT_DIR")')
" > /dev/null 2>&1 &

exit 0
```

**Claudeの応答を取得する仕組み**

`Stop`イベント時、stdinに含まれる`transcript_path`はセッション全体の会話記録ファイル（JSONL形式）を指しています。このファイルの末尾からassistantタイプのメッセージを探し、テキスト部分を抽出します。

```
// transcript.jsonlの構造（1行1JSON）
{"type": "user", ...}
{"type": "assistant", "message": {"content": [{"type": "text", "text": "Claudeの応答テキスト"}]}}
```

`tail -r`でファイルを逆順に読み、最初に見つかったassistant応答を取得します。macOSでは`tail -r`、Linuxでは`tac`を使ってください。

**実装上の注意点**

* `curl`をバックグラウンド実行（`&`）にして、Claude Codeの操作をブロックしない
* `exit 0`を必ず返す。非0を返すとClaude Code側でエラー扱いになる
* `tool_input`とClaude応答は10KBで切り詰め。大きなファイル編集のdiffや長い説明が入り得るため

### セッション要約の生成（`summarize.sh`）

`~/.claude/hooks/summarize.sh` — `Stop`イベント時に`record.sh`の後に実行され、セッションの要約を生成します。

```
#!/bin/bash
CH_URL="${CLICKHOUSE_URL:-http://localhost:8123}"
CH_AUTH="${CLICKHOUSE_AUTH:-default:your-pass}"

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""')
PROJECT_DIR=$(echo "$INPUT" | jq -r '.cwd // ""')

escape() { echo "$1" | sed "s/'/''/g"; }

# セッション中に編集したファイルを収集
FILES=$(curl -sf --max-time 3 --user "$CH_AUTH" "$CH_URL" --data-binary "
  SELECT DISTINCT JSONExtractString(content, 'file_path') AS f
  FROM claude_memory.events
  WHERE session_id = '$(escape "$SESSION_ID")'
    AND tool_name IN ('Edit', 'Write')
    AND f != ''
  FORMAT TabSeparated
" 2>/dev/null | head -20)

# 実行したコマンドを収集
COMMANDS=$(curl -sf --max-time 3 --user "$CH_AUTH" "$CH_URL" --data-binary "
  SELECT DISTINCT JSONExtractString(content, 'command') AS c
  FROM claude_memory.events
  WHERE session_id = '$(escape "$SESSION_ID")'
    AND tool_name = 'Bash'
    AND c != ''
  FORMAT TabSeparated
" 2>/dev/null | head -20)

# ユーザーの指示を時系列で収集 → 要約の素材
PROMPTS=$(curl -sf --max-time 3 --user "$CH_AUTH" "$CH_URL" --data-binary "
  SELECT content
  FROM claude_memory.events
  WHERE session_id = '$(escape "$SESSION_ID")'
    AND event_type = 'UserPromptSubmit'
    AND content != ''
  ORDER BY created_at
  FORMAT TabSeparated
" 2>/dev/null | head -20)

# 配列形式に変換
to_ch_array() {
  local input="$1"
  if [ -z "$input" ]; then
    echo "[]"
    return
  fi
  echo "$input" | grep -v '^$' | sed "s/'/''/g" \
    | sed "s/^/'/" | sed "s/$/'/" \
    | paste -sd',' - | sed 's/^/[/;s/$/]/'
}
FILES_ARR=$(to_ch_array "$FILES")
CMDS_ARR=$(to_ch_array "$COMMANDS")
[ -z "$FILES_ARR" ] && FILES_ARR="[]"
[ -z "$CMDS_ARR" ] && CMDS_ARR="[]"

# 指示の先頭5件をつなげて簡易要約に
SUMMARY=$(echo "$PROMPTS" | head -5 | tr '\n' ' | ' | sed 's/ | $//')
SUMMARY=$(escape "$SUMMARY")

# セッション開始時刻を取得
STARTED=$(curl -sf --max-time 3 --user "$CH_AUTH" "$CH_URL" --data-binary "
  SELECT min(created_at)
  FROM claude_memory.events
  WHERE session_id = '$(escape "$SESSION_ID")'
  FORMAT TabSeparated
" 2>/dev/null)
[ -z "$STARTED" ] && STARTED=$(date -u +%Y-%m-%d\ %H:%M:%S)

curl -sf --max-time 3 --user "$CH_AUTH" "$CH_URL" -d "
  INSERT INTO claude_memory.session_summaries
    (session_id, project_dir, summary, files_touched, commands_run, started_at)
  VALUES (
    '$(escape "$SESSION_ID")', '$(escape "$PROJECT_DIR")',
    '$SUMMARY', $FILES_ARR, $CMDS_ARR,
    '$STARTED')
" > /dev/null 2>&1 &

exit 0
```

ここでは指示内容をそのまま連結して簡易的な要約にしています。LLM APIを呼び出して高品質な要約を生成する方法もありますが、コストとレイテンシのトレードオフがあるため、まずはシンプルに始めるのがおすすめです。

## 復元スクリプトの実装

ここが本記事の核心です。`SessionStart` hookでClickHouseから前回のセッション情報を取得し、stdoutに出力することでClaude Codeのコンテキストに注入します。

`~/.claude/hooks/restore.sh`

```
#!/bin/bash
CH_URL="${CLICKHOUSE_URL:-http://localhost:8123}"
CH_AUTH="${CLICKHOUSE_AUTH:-default:your-pass}"

INPUT=$(cat)
PROJECT_DIR=$(echo "$INPUT" | jq -r '.cwd // ""')

escape() { echo "$1" | sed "s/'/''/g"; }

# 同じプロジェクトの直近3セッションの要約を取得
RESULT=$(curl -sf --max-time 3 --user "$CH_AUTH" "$CH_URL" --data-binary "
  SELECT
    session_id,
    summary,
    files_touched,
    commands_run,
    started_at,
    ended_at
  FROM claude_memory.session_summaries
  WHERE project_dir = '$(escape "$PROJECT_DIR")'
  ORDER BY ended_at DESC
  LIMIT 3
  FORMAT Vertical
" 2>/dev/null)

# 結果がなければ何も出力しない
if [ -z "$RESULT" ]; then
  exit 0
fi

# stdoutに出力 → Claude Codeのコンテキストに注入される
cat <<EOF
[前回のセッション情報]
このプロジェクトでの直近の作業履歴です。必要に応じて参照してください。

$RESULT
EOF

exit 0
```

SessionStartのHookがstdoutに出力した文字列はClaude Codeのコンテキストに注入されます。新しいセッションを開始すると、前回のセッションで何をしていたかがコンテキストに含まれた状態で会話が始まります。

## settings.jsonの設定

`~/.claude/settings.json` の `hooks` キーに以下を追加します（既存の設定はそのまま保持してください）。

```
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [{
          "type": "command",
          "command": "~/.claude/hooks/record.sh",
          "timeout": 5
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [{
          "type": "command",
          "command": "~/.claude/hooks/record.sh",
          "timeout": 5
        }]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/record.sh",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "~/.claude/hooks/summarize.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{
          "type": "command",
          "command": "~/.claude/hooks/restore.sh",
          "timeout": 5
        }]
      }
    ]
  }
}
```

**設定のポイント**

* `matcher`を空にすると全ツール・全イベントにマッチ
* `timeout`でスクリプトの最大実行時間を制限（超過すると打ち切り）
* `Stop`イベントでは`record.sh`（Claude応答の記録）→ `summarize.sh`（要約生成）の順に実行

この設定は `~/.claude/settings.json` に書くと全プロジェクトで有効になります。特定プロジェクトだけで使いたい場合は、プロジェクトの `.claude/settings.json` に配置してください。

## 何が記録されるのか

設定が完了すると、以下のすべてがClaude Codeの操作に伴って自動的にClickHouseに記録されます。

| イベント | 記録内容 | 記録先 |
| --- | --- | --- |
| `UserPromptSubmit` | ユーザーが入力したテキスト | `events` |
| `PostToolUse` | ツール名とパラメータ（Bashのコマンド、Editのファイルパス等） | `events` |
| `Stop` | Claudeの応答テキスト（transcriptファイルから取得） | `events` |
| `Stop` | セッション要約（編集ファイル・実行コマンド・指示の概要） | `session_summaries` |

ClickHouseのPlayUI（`http://localhost:8123/play`）で、蓄積されたデータをSQLで確認できます。

```
-- 直近のイベントを確認
SELECT event_type, tool_name, substring(content, 1, 100) AS preview, created_at
FROM claude_memory.events
ORDER BY created_at DESC
LIMIT 20;

-- セッション要約を確認
SELECT * FROM claude_memory.session_summaries ORDER BY ended_at DESC;
```

## コンテキストサイズへの影響

「セッション開始時に大量のデータが注入されて、コンテキストを圧迫しないか？」という懸念があるかもしれません。

restore.shが注入するデータ量

| 要素 | 上限 | サイズ目安 |
| --- | --- | --- |
| セッション数 | 3件（`LIMIT 3`固定） | — |
| summary | ユーザー指示5件の連結 | 数百バイト〜数KB |
| files\_touched | 最大20ファイルパス | 1〜2KB |
| commands\_run | 最大20コマンド | 1〜2KB |
| **合計** |  | **最大でも10〜20KB程度** |

Claude Codeのコンテキストウィンドウ（1Mトークン）に対して誤差レベルです。

一方、eventsテーブルに記録されるClaude応答（10KB上限で切り詰め）はClickHouseに保存されるだけで、コンテキストには注入されません。将来的にキーワード検索で過去の応答を引く用途に使えます。

## この方式の限界

本記事の仕組みはセッション継続性の課題を軽減しますが、万能ではありません。実用する前に知っておくべき限界があります。

### 復元されるのは直近3セッションだけ

restore.shは同一プロジェクトの直近3セッションの要約を注入するだけです。「2週間前にやったあの作業の続き」や「別プロジェクトで似たことをやった作業」を引くことはできません。関連性の高い過去セッションを選択的に復元するには、キーワード検索や意味検索（ベクトル検索）の仕組みが別途必要です。

### 要約の品質は粗い

現在の`summarize.sh`はユーザーの指示を先頭5件連結しているだけです。「何をしたか」はわかりますが、「なぜそうしたか」「どんな問題に直面したか」「どう解決したか」は要約に含まれません。LLM APIを呼び出して要約を生成すれば品質は上がりますが、コストとレイテンシのトレードオフがあります。

### 機密情報がログに残る

**これが最も重要な限界です。** 本記事の設計はBashコマンド、プロンプト、Claude応答、tool\_inputを丸ごと記録します。つまり以下のようなデータが高い確率でClickHouseに入ります。

* 環境変数やコマンド引数に含まれるAPIキー・トークン
* `.env`ファイルの内容をClaude Codeが読んだ結果
* プロンプトに含まれる社内情報や個人情報
* Claude応答に含まれるパスワードや接続文字列

現状のスクリプトにはマスキング処理が入っていないため、記録されたデータの取り扱いには注意が必要です。次のセクションで対策を説明します。

## 実運用での注意点

### 機密情報の混入対策

最も手軽な対策は、record.shにフィルタを追加して危険なパターンを除外することです。

```
# record.sh に追加するフィルタの例
sanitize() {
  echo "$1" \
    | sed -E 's/(api[_-]?key|token|password|secret)[=:]["'"'"']?[^ "'"'"',}]+/\1=***REDACTED***/gi' \
    | sed -E 's/Bearer [A-Za-z0-9._-]+/Bearer ***REDACTED***/g'
}

# CONTENTを記録する前にサニタイズ
CONTENT=$(sanitize "$CONTENT")
```

ただし、正規表現ベースのマスキングには限界があります。より厳密に対応するなら

* **記録対象を絞る** — `PostToolUse`のmatcherでBashのみ除外する、あるいは`tool_input`ではなくツール名とファイルパスだけ記録する
* **ClickHouse側でアクセス制御** — 専用ユーザーを作り、読み取り権限を制限する
* **TTLを短くする** — 90日ではなく7〜30日にして、古い機密情報が長く残らないようにする

### 大きなデータの切り詰め

現在のスクリプトは10KBで切り詰めていますが、それでも大きなファイルの全文書き込み（Write）や長いコマンド出力が記録されるケースがあります。必要に応じて上限を引き下げるか、特定のツール（Write等）を記録対象から外すことを検討してください。

### DB障害時の影響

ClickHouseが停止していても、Claude Codeの動作には影響しません。各スクリプトは以下の設計になっています。

* `curl -sf` — エラーを静かに無視
* `> /dev/null 2>&1 &` — バックグラウンド実行で出力を破棄
* `exit 0` — 常に成功を返す

restore.shもClickHouseに接続できなければ空文字を返すだけなので、セッション開始がブロックされることはありません。ただし `--max-time 3` のタイムアウトまでの待ちが発生する可能性があるため、DB停止が長引く場合はhooksを一時的に無効化するのが無難です。

### 個人PC vs 共有環境

本記事の設計は個人PCでの利用を前提としています。共有環境で使う場合は追加の考慮が必要です。

| 観点 | 個人PC | 共有環境 |
| --- | --- | --- |
| データの分離 | 自分だけ | ユーザーごとにDBユーザーを分けるか、`user_id`カラムを追加 |
| 認証情報 | スクリプトに直書きでも可 | 環境変数や秘密管理ツール経由で注入 |
| ClickHouseへのアクセス | localhost | TLS + 認証必須 |
| 機密情報リスク | 自分のデータのみ | 他人の操作ログが見える危険がある |

## まとめ

Claude Codeのセッションが引き継げない問題は、HooksとClickHouseの組み合わせで対処できます。ユーザーの指示、Claudeの応答、ツールの実行がすべて自動で記録され、次のセッション開始時にコンテキストとして注入されます。

限界はありますが、「前回の作業を一から説明し直す」手間は確実に減ります。まずは導入して、自分の開発フローに合うか試してみてください。
