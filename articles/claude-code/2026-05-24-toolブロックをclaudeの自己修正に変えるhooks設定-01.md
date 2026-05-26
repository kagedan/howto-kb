---
id: "2026-05-24-toolブロックをclaudeの自己修正に変えるhooks設定-01"
title: "ToolブロックをClaudeの自己修正に変えるhooks設定"
url: "https://zenn.dev/giana12th/articles/6df4b4e7265608"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-05-24"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

コマンド実行を自動でブロックしつつ、推奨する方法に誘導するhooks設定方法。Claude Code向け。

![cdコマンドブロック](https://static.zenn.studio/user-upload/abca227e5368-20260523.png)  
*動作事例*

Claude Code の `deny` 設定でBashツールの実行をブロックしても、Claude は「なぜブロックされたか」を理解できません。`PreToolUse` フック + `exit 2` を使って、**理由を渡してその場で自己修正させる**ことができます。

## 承認プロンプト面倒すぎ問題

Claude Codeでは、ツール実行のたびに承認プロンプトが表示されます。しかし**面倒**。都度判断を求められる認知負荷は大きく、とりあえずで許可しがち。

Anthropicの調査でも、ユーザーは承認プロンプトの **93% を承認**していたと報告されています。みんなやってます。この状態を **approval fatigue（承認疲れ）** と呼び、設計問題として位置付けられています。

<https://www.anthropic.com/engineering/claude-code-auto-mode>

対策としては「毎回判断しなくていい仕組み」を作ることです。明らかに問題のあるコマンドは**機械的に判定してブロック**。判断コストを、本当に判断が必要な場面だけに集中させます。

そこで `settings.json` の `deny` 設定が役立ちます。危険なコマンド実行をブロックできます。

```
"permissions": {
  "deny": ["Bash(cd *)"]
}
```

**「いやなんでcdダメなん？？？」**

`deny`では**Claude に理由が伝わりません**。Claude 側からは「権限エラー」としか見えません。なぜブロックされたのかが分からないため、**同じミスを繰り返します。**

そこで`PreToolUse`フックを使って、Claudeに**理由を伝える**仕組みを整備しました。コマンドを自己修正させて、確認や説明の手間を省きます。

![絶対パスブロック](https://static.zenn.studio/user-upload/058163bda135-20260523.png)  
*絶対パスをブロックして相対パスへ誘導する例*

## セットアップ方法

### 環境

* Windows 11
* WinGet版のClaude Code 2.1.142
* Git Bash
* jq

Windowsに**直接**インストールしたClaude Codeでの設定です  
Powershell環境や、MacやLinuxだとコマンドが異なる可能性があります

またjqを使用しています

<https://jqlang.org/download/>

### ディレクトリ構成

ディレクトリ構成

```
~/.claude/
└─ hooks/
    ├─ bash/
    │   ├─ validate.sh     # ロジック
    │   └─ rules.jsonl     # ルール一覧
    ├─ skills/
    │   └─ add-bash-rule/
    │       └─ SKILL.md        # ルール設定スキル
    └─ settings.json       # hooks設定
```

### validate.sh

ロジック本体です  
`rules.jsonl`の内容を元に、Bashツールの実行をブロックします  
`exit 2` を使うと、実行をブロックしつつ、stderr に書いたメッセージが Claude に直接届きます

~/.claude/hooks/bash/validate.sh

```
#!/usr/bin/env bash
# PreToolUse hook: validate Bash commands against JSONL rules.
#
# Exit codes:
#   0 — allowed
#   2 — blocked; stderr is shown to Claude for self-correction

set -euo pipefail

RULES_FILE="$(dirname "$0")/rules.jsonl"

input=$(cat)
command=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

[ -z "$command" ] && exit 0
[ ! -f "$RULES_FILE" ] && exit 0

while IFS= read -r line || [ -n "$line" ]; do
  [[ -z "$line" || "$line" == \#* ]] && continue

  enabled=$(printf '%s' "$line" | jq -r '.enabled // true')
  [ "$enabled" = "false" ] && continue

  pattern=$(printf '%s' "$line" | jq -r '.pattern // empty')
  reason=$(printf '%s' "$line"  | jq -r '.reason  // empty')

  [ -z "$pattern" ] && continue

  if printf '%s' "$command" | grep -qE "$pattern"; then
    printf 'Command blocked by validate-bash hook.\nRule pattern: %s\nReason: %s\n' \
      "$pattern" "$reason" >&2
    exit 2
  fi

done < "$RULES_FILE"

exit 0
```

### rules.jsonl

1行 = 1ルールの JSONL 形式で作成します

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `pattern` | string | yes | ERE 正規表現。`grep -E` でコマンド全体に対してマッチング |
| `reason` | string | yes | Claude へのブロック理由。「なぜ禁止か」＋「どう直すか」を含める |
| `enabled` | boolean | no | 省略時は `true`。`false` で一時無効化 |

筆者環境での設定例です

~/.claude/hooks/bash/rules.jsonl

```
{"pattern": "(^|&&\\s*|;\\s*|\\|\\|\\s*)rm\\s", "reason": "`rm` は不可逆な削除のため使用禁止です。削除方法は rules/use-bash-tool.md を参照してください。", "enabled": true}
{"pattern": "(^|&&\\s*|;\\s*)cd\\s", "reason": "プロジェクトルートで起動しているため cd は不要ではありませんか？コマンドを直接実行するか、絶対パスを指定してください。例: 'cd /path && cmd' → 'cmd'", "enabled": true}
{"pattern": ">>?\\s*nul\\b", "reason": "> nul および >> nul はnulファイルが生成されます。Git Bash では '> /dev/null'を使用してください", "enabled": true}
{"pattern": "\\s[A-Z]:/[^/ ]+/", "reason": "Windowsの絶対パス指定は冗長です。カレントディレクトリがプロジェクトルートのため、相対パスを使用してください（例: `mkdir -p D:/workspace/project/subdir` → `mkdir -p subdir`）", "enabled": true}
```

内容はお好みで調整してください  
と言っても**正規表現**を自分で組むのがツラい  
ので、Claudeに全任せできるようにスキルを用意しました

### SKILL.md

`disable-model-invocation: true`のためコンテキストへのロード**0**  
使うときだけ`/add-bash-rule`で呼んでください

使用例

```
/add-bash-rule rm -rf の使用をブロックしたい
```

~/.claude/skills/add-bash-rule/SKILL.md

```
---
name: add-bash-rule
description: Add a new validation rule to the Bash PreToolUse hook. Describe what to block in natural language; Claude handles the ERE regex and reason.
disable-model-invocation: true
argument-hint: "ブロックしたいコマンドや動作を説明（例: rm -rf の使用、curl の http:// など）"
allowed-tools: Read,Write,Bash(echo *)
---

# add-bash-rule

`$ARGUMENTS` の内容をもとに `~/.claude/hooks/bash/rules.jsonl` に新しいルールを追加する。

## ステップ1: 現在のルールを確認

`~/.claude/hooks/bash/rules.jsonl` を Read して：
- 既存ルールの `pattern` を把握する
- 追加しようとするルールと重複・競合がないか確認する

## ステップ2: 正規表現を設計する

ブロック対象の説明から ERE 正規表現（`grep -E` 互換）を設計する。

考慮すべき変形：
- コマンドの先頭だけでなく `&& cmd` や `; cmd` の形も必要か
- スペースの有無（例: `>nul` と `> nul`）
- 誤検知を防ぐ単語境界（`\b`、`\s` など）

パターンを Bash で検証する（ブロックすべき例・通過すべき例の両方）：
```bash
echo 'テスト用コマンド' | grep -qE 'PATTERN' && echo MATCH || echo NO_MATCH
```

## ステップ3: reason を書く

Claude に渡されるメッセージとして、以下を1〜2文にまとめる：
- なぜ問題なのか
- 代わりに何を使うべきか（具体例付き）

日本語で書く。

## ステップ4: ルールを追加する

ファイルを Read し、末尾に新しい行を追加して Write する：
```jsonl
{"pattern": "...", "reason": "...", "enabled": true}
```

## ステップ5: 確認

追加したルールの内容とテスト結果を表示して完了を伝える。
```

### settings.json

`PreToolUse`のhooksを設定します  
ブロックするコマンドを`deny` に入れていた場合は削除してください  
hooksの検証スクリプト実行前にブロックされてしまいます

~/.claude/settings.json

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/bash/validate.sh"
          }
        ]
      }
    ]
  },
  "permissions": {
    "deny": []
  }
}
```
