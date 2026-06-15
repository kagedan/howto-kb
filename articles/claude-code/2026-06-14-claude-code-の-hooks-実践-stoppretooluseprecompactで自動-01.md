---
id: "2026-06-14-claude-code-の-hooks-実践-stoppretooluseprecompactで自動-01"
title: "Claude Code の hooks 実践 — Stop/PreToolUse/PreCompactで自動化と安全弁を仕込む"
url: "https://qiita.com/leven-E/items/e601c14e86b7621685ef"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Python", "qiita"]
date_published: "2026-06-14"
date_collected: "2026-06-15"
summary_by: "auto-rss"
query: ""
---

## この記事の位置づけ

Claude Code には「hooks」という仕組みがあります。Stop（応答完了後）・PreToolUse（ツール実行前）・PreCompact（コンテキスト圧縮前）などのイベントにシェルスクリプトを登録することで、**手動でやっていた繰り返し作業を自動化**し、**危険操作に安全ゲートを挟む**ことができます。

この記事は「拡張プリミティブ」シリーズの spoke 記事です。hooks の具体的な設定例と実運用での落とし穴を扱います。

- 対象: Claude Code を日常使いしていて、繰り返し手作業や危険操作をなんとかしたい方
- 動作確認: Claude Code v2.1 系 / 2026-05時点
- 設定ファイルパス: `~/.claude/settings.json` または `<プロジェクトルート>/.claude/settings.json`

---

## 1. hooksとは何か — 3行まとめ

- Claude Code のライフサイクルに **シェルスクリプトを割り込ませる仕組み**
- Stop・PreToolUse・PostToolUse・PreCompact の4イベントをサポート（2026-05時点）
- hook の exit code で「続行」「ブロック」を制御できる（非0 → ツール実行をブロック）

```
Claude が応答 → Stop hook 発火 → スクリプト実行（記憶投入・レポート生成 etc.）
Claude がツール呼び出し → PreToolUse hook 発火 → チェックOK → ツール実行
コンテキスト圧縮前 → PreCompact hook 発火 → 残課題をファイルに退避
```

hooks を使うまでは「作業完了後のふりかえり記録（walkthrough）を書いたら手動でナレッジ蓄積ツール（mnemory）に投入」「危険コマンドを実行される前に気づけず後悔」といった場面が繰り返されていました。hooks を入れてからはそれが機構として動くようになりました。

---

## 2. settings.jsonでの設定方法

### 基本構造

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/your/stop-hook.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/your/pre-bash-check.sh"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/your/pre-compact.sh"
          }
        ]
      }
    ]
  }
}
```

### イベント種別の一覧

| イベント | タイミング | 主な用途 |
|---|---|---|
| `Stop` | Claude の応答が完了した直後 | 記憶投入・レポート生成・通知 |
| `PreToolUse` | ツール（Bash/Write/Edit 等）実行の直前 | 安全チェック・確認ゲート |
| `PostToolUse` | ツール実行の直後 | ログ記録・後処理 |
| `PreCompact` | コンテキスト圧縮の直前 | 残課題保全・セーブポイント |

### matcher の指定

`matcher` に文字列を設定すると、特定のツール名にだけ hook を適用できます。

```json
"matcher": "Bash"        // Bash ツールにのみ発火
"matcher": "Write"       // Write ツールにのみ発火
"matcher": ""            // 全イベントに発火（Stopは常に空でOK）
```

### hook スクリプトの基本形

```bash
#!/usr/bin/env bash
set -euo pipefail

# --- 環境変数（著者実測: Claude Code v2.1系 2026-06時点）---
# CLAUDE_HOOK_EVENT: イベント種別 (Stop / PreToolUse / etc.)
# CLAUDE_HOOK_TOOL_INPUT: ツール入力のJSON (PreToolUse 時)
# CLAUDE_TRANSCRIPT_PATH: 現在の会話ログのパス
# ※ 変数名はバージョンで変わる可能性あり。使用前に公式ドキュメントを確認してください

# 処理...

exit 0  # 続行
# exit 1  # ブロック（PreToolUse の場合はツール実行を停止）
```

スクリプトは `chmod +x` で実行権限を付与してください。

---

## 3. 実践例1 — Stop hook: walkthrough後の記憶投入を自動化

### やりたいこと

作業完了後に書くふりかえり記録ファイル（walkthrough.md）を書いた後、「`## 記憶投入` セクションをナレッジ蓄積ツール（mnemory）に手動で登録」という手順を毎回踏んでいました。これをセッション終了時に自動実行されるスクリプト（Stop hook）で自動化します。

### 仕組み

1. Stop hook が発火する
2. 会話ログ（`CLAUDE_TRANSCRIPT_PATH`）の末尾に `## 記憶投入` セクションがあるか確認
3. あれば mnemory の API を叩いて記録
4. 投入済みフラグを置いて二重投入を防ぐ（冪等性）

### スクリプト例

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/remember.sh
set -euo pipefail

TRANSCRIPT="${CLAUDE_TRANSCRIPT_PATH:-}"
if [[ -z "$TRANSCRIPT" ]] || [[ ! -f "$TRANSCRIPT" ]]; then
  exit 0
fi

# ## 記憶投入 セクションを抽出
MEMORY_SECTION=$(awk '/^## 記憶投入/{found=1; next} found && /^## /{exit} found{print}' "$TRANSCRIPT")

if [[ -z "$MEMORY_SECTION" ]]; then
  exit 0  # セクションなし → 何もしない
fi

# 投入済みフラグ（冪等性）
FLAG_FILE="/tmp/remember_$(md5sum <<< "$MEMORY_SECTION" | cut -d' ' -f1).done"
if [[ -f "$FLAG_FILE" ]]; then
  exit 0  # 既投入 → スキップ
fi

# mnemory API 呼び出し（実際の呼び出し方はmnemory仕様に合わせる）
# ここでは curl を例示
MNEMORY_ENDPOINT="${MNEMORY_URL:-http://localhost:8765}"
echo "$MEMORY_SECTION" | curl -s -X POST "${MNEMORY_ENDPOINT}/store" \
  -H "Content-Type: text/plain" \
  --data-binary @- \
  -o /dev/null

touch "$FLAG_FILE"
echo "[remember.sh] 記憶投入完了" >&2

exit 0
```

### settings.json への登録

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "/home/your-user/.claude/hooks/remember.sh"
          }
        ]
      }
    ]
  }
}
```

**ポイント:** Stop hook はセッション中に何度も発火します（Claude が返答するたびに）。`## 記憶投入` セクションが存在しなければ即座に `exit 0` することで、無駄な処理を避けています。

---

## 4. 実践例2 — PreToolUse hook: 危険コマンドの実行前に門番チェック

### やりたいこと

`rm -rf`・`docker system prune`・`git reset --hard` のような不可逆コマンドを、確認なしに実行されるのを防ぎます。

### 仕組み

1. Bash ツールが呼ばれる直前に PreToolUse hook が発火
2. コマンド文字列に危険パターンが含まれるか検査
3. 含まれていれば exit 1 でブロック（Claude に「確認が必要」と伝える）

### スクリプト例

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/pre-bash-guard.sh
set -euo pipefail

# ツール入力のJSONからコマンドを取り出す
TOOL_INPUT="${CLAUDE_HOOK_TOOL_INPUT:-{}}"
COMMAND=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")

if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# 危険パターンリスト
DANGER_PATTERNS=(
  "rm -rf"
  "rm -fr"
  "git reset --hard"
  "git clean -fd"
  "docker system prune"
  "docker container rm"
  "docker image rm"
  "git push --force"
  "git push -f"
  "DROP TABLE"
  "TRUNCATE"
)

for PATTERN in "${DANGER_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qF "$PATTERN"; then
    echo "[pre-bash-guard] 危険パターン検出: ${PATTERN}" >&2
    echo "[pre-bash-guard] コマンド: ${COMMAND}" >&2
    echo "[pre-bash-guard] このコマンドは人間の確認が必要です。ユーザーの明示承認を得てから再実行してください。" >&2
    exit 1  # ブロック
  fi
done

exit 0  # 安全 → 続行
```

### settings.json への登録

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/home/your-user/.claude/hooks/pre-bash-guard.sh"
          }
        ]
      }
    ]
  }
}
```

**ポイント:** exit 1 で返すと Claude はツールの実行を止め、stderr に出力したメッセージを受け取ります。Claude はそのメッセージを元に「このコマンドはブロックされました」と報告するため、**ユーザーへの通知も兼ねています**。

Write/Edit ツールに対しても「このファイルへの書き込みをガードしたい」と Claude に伝えれば、同様の hook を生成させることができます。特定のファイル（`authorized_keys` など）への書き込みゲートも同じ発想で実現できます。

---

## 5. 実践例3 — PreCompact hook: コンテキスト圧縮前に残課題を退避

### やりたいこと

Claude Code はコンテキストが一定量を超えると自動的に圧縮（compaction）を行います。このとき、会話の中でやりとりしていた `- [ ]` 残課題リストも「過去のやりとり」としてまとめて要約されてしまいます。チェックリストとして機能していた箇条書きが、「〜という残課題があった」という1文の要約に溶けてしまうイメージです。PreCompact hook を使うと、圧縮が走る直前に残課題をファイルへ書き出して保全できます。

### 仕組み

1. PreCompact hook が発火（圧縮の直前）
2. 会話ログから `- [ ]` を含む行を全部抽出
3. タイムスタンプ付きでファイルに保存
4. 次のセッション開始時に Claude が読み込める場所に置く

### スクリプト例

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/pre-compact.sh
set -euo pipefail

TRANSCRIPT="${CLAUDE_TRANSCRIPT_PATH:-}"
if [[ -z "$TRANSCRIPT" ]] || [[ ! -f "$TRANSCRIPT" ]]; then
  exit 0
fi

# 残課題（未チェックのタスク）を抽出
TODOS=$(grep -n "- \[ \]" "$TRANSCRIPT" 2>/dev/null || true)

if [[ -z "$TODOS" ]]; then
  exit 0  # 残課題なし → 何もしない
fi

# 保存先（プロジェクトの .claude/ 以下に置くと次回セッションで参照しやすい）
SAVE_DIR="${PWD}/.claude"
mkdir -p "$SAVE_DIR"
SAVE_FILE="${SAVE_DIR}/pre-compact-todos-$(date +%Y%m%d-%H%M%S).md"

cat > "$SAVE_FILE" << EOF
# Pre-Compact 残課題保全 ($(date '+%Y-%m-%d %H:%M:%S JST'))

以下は圧縮前のコンテキストに存在した未完了タスクです。

\`\`\`
${TODOS}
\`\`\`

元ファイル: ${TRANSCRIPT}
EOF

echo "[pre-compact] 残課題を退避しました: ${SAVE_FILE}" >&2

exit 0
```

### settings.json への登録

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "/home/your-user/.claude/hooks/pre-compact.sh"
          }
        ]
      }
    ]
  }
}
```

**ポイント:** 保存先を `.claude/` 直下にしておくと、次のセッション開始時に「前回の残課題を確認する」フックや手動確認が楽になります。ファイル名にタイムスタンプを入れることで、複数回の圧縮があっても履歴として残ります。

---

## 6. 落とし穴と対策

### 落とし穴1 — 冪等性: 同一hookが複数回発火する

Stop hook は Claude が返答するたびに発火します。「ふりかえり記録が完成したら1回だけ投入したい」という場合、冪等性を考慮せずに Claude に生成させると同じ内容が繰り返し投入されます。

**対策:**

```bash
# md5 や sha256 でコンテンツのハッシュを取ってフラグファイルを置く
HASH=$(echo "$MEMORY_SECTION" | sha256sum | cut -d' ' -f1)
FLAG="/tmp/hook_done_${HASH}"
if [[ -f "$FLAG" ]]; then
  exit 0  # 処理済み → スキップ
fi
# 処理...
touch "$FLAG"
```

もしくは、投入条件を「セクションが存在し、かつ今回の応答に新規で現れた場合のみ」に絞る判定を加えます。冪等性を意識しないと、記憶投入が何十件も重複する事故になります。著者環境では一度の放置で大量の重複エントリが積み上がった経験があります。

### 落とし穴2 — hook内でClaude APIを呼ぶと無限ループになる

hook のスクリプトから Claude API を呼び出すと、そのレスポンスが再び Stop hook を発火させ、また API を呼び出す… という無限ループが発生します。

**対策:** hook スクリプト内から Claude API（`claude` CLI 含む）を呼ぶことは禁止です。記憶システム・外部サービス・シェルコマンドのみを使ってください。

### 落とし穴3 — exit codeの意味を間違える

| exit code | Stop hook の挙動 | PreToolUse hook の挙動 |
|---|---|---|
| `0` | 正常終了（何もしない） | ツール実行を続行 |
| 非0（`1` 等） | エラーログに記録される | **ツール実行をブロック** |

Stop hook で非0を返すと、Claude がエラーを受け取ってセッションが不安定になる場合があります。Stop hook では原則 `exit 0` で終了し、エラーは stderr にログとして出すだけに留めましょう。

```bash
# Bad: Stop hook で exit 1 すると意図せずエラーになる
some_command || exit 1

# Good: エラーをログに残しつつ exit 0 で終了
some_command || { echo "[hook] some_command failed, skipping" >&2; exit 0; }
```

### 落とし穴4 — スクリプトのパスは絶対パスで書く

settings.json に書くコマンドパスは `~/` 展開が効かない場合があります。必ず `/home/your-user/...` の絶対パスで書いてください。

```json
// Bad
"command": "~/.claude/hooks/remember.sh"

// Good
"command": "/home/your-user/.claude/hooks/remember.sh"
```

---

## 7. まとめ

| hook | 典型用途 | exit 0 / 非0 の意味 |
|---|---|---|
| Stop | 記憶投入・レポート生成・通知 | 非0 → エラー扱い（原則 0 で終了） |
| PreToolUse | 危険操作ゲート・確認チェック | 非0 → ツール実行ブロック |
| PreCompact | 残課題保全・セーブポイント | 非0 → 圧縮をブロック（通常 0 で終了） |

hooks を入れると「機構として動く」状態になります。ルールを人間が覚えて毎回実行するのではなく、スクリプトに書いてシステムに委ねる。これが Claude Code 運用の次のステップです。

冪等性・APIループ禁止・exit code の意味の3点を理解しておけば、あとは「やりたいことを Claude に日本語で伝える」だけです。コードは Claude が書きます。あなたはゴールを言語化すれば良い。

---

## 関連記事

- [Claude Code 拡張プリミティブ全10種 — hooks/slash commands/MCP servers を体系的に整理する](https://qiita.com/leven-E/items/0fdbfc85894e366ce3e2)（hub記事）

---

*動作確認環境: Claude Code v2.1 系 / Oracle Linux 9 aarch64 / 2026-05時点*
