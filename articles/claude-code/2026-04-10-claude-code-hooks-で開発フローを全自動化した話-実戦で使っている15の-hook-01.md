---
id: "2026-04-10-claude-code-hooks-で開発フローを全自動化した話-実戦で使っている15の-hook-01"
title: "Claude Code Hooks で開発フローを全自動化した話 ─ 実戦で使っている15の hook"
url: "https://qiita.com/kawabe0201/items/3fcf698abe60d57b211b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

Claude Code の `hooks` 機能は、Claude のツール実行の前後や特定イベントで任意のシェルコマンドを差し込める仕組みだ。ここを設計すると、型チェック忘れ・破壊的コマンドの事故・作業ログの欠損といった「人間の不注意由来の事故」がゼロになる。

この記事では、俺が `~/.claude/settings.json` に実際に仕込んでいる15個の hook を全公開する。

## hooks の基本構造

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "echo 'pre-bash'" }
        ]
      }
    ],
    "PostToolUse": [],
    "UserPromptSubmit": [],
    "Stop": []
  }
}
```

使えるイベントは主に `PreToolUse` `PostToolUse` `UserPromptSubmit` `Stop`。`matcher` でツール名を指定する。`PreToolUse` で exit code 2 を返すと実行がブロックされる。ここが防御の要。

## 15の hook を全公開

### 1. PostToolUse: TypeScript 型チェック

```
{
  "matcher": "Edit|Write",
  "hooks": [
    { "type": "command", "command": "npx tsc --noEmit 2>&1 | tail -20" }
  ]
}
```

ファイル編集のたびに `tsc --noEmit` を走らせる。型エラーの発見が編集直後に来るので修正コストが最小になる。

### 2. PostToolUse: ESLint 自動修正

```
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "npx eslint --fix \"$CLAUDE_FILE_PATHS\" 2>/dev/null" }
  ]
}
```

編集されたファイルだけを対象に `eslint --fix`。全体 lint は重いので差分だけ。

### 3. PostToolUse: Prettier 自動整形

```
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "npx prettier --write \"$CLAUDE_FILE_PATHS\" 2>/dev/null" }
  ]
}
```

`eslint --fix` の直後に prettier。順番が逆だとスタイル競合を起こす。

### 4. PreToolUse: rm -rf 防御

```
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "grep -qE 'rm\\s+-rf?\\s+(/|~|\\*)' <<< \"$CLAUDE_TOOL_INPUT\" && { echo 'BLOCKED: destructive rm'; exit 2; } || exit 0"
    }
  ]
}
```

`rm -rf /` `rm -rf ~` `rm -rf *` を含むコマンドを実行前にブロック。exit 2 で Claude 側にエラーが伝わる。一度これに救われてから絶対に外せなくなった。

### 5. PreToolUse: git push --force 防御

```
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "grep -qE 'git push.*(-f|--force)' <<< \"$CLAUDE_TOOL_INPUT\" && { echo 'BLOCKED: force push'; exit 2; } || exit 0"
    }
  ]
}
```

force push の事故は取り返しがつかない。明示的に外さない限り常時ブロック。

### 6. UserPromptSubmit: 現在時刻を注入

```
{
  "hooks": [
    { "type": "command", "command": "date '+現在時刻: %Y-%m-%d %H:%M:%S'" }
  ]
}
```

hook の標準出力は Claude の文脈に追加される。これで Claude は常に現在時刻を知っている。「最新」という単語の解釈精度が上がる。

### 7. UserPromptSubmit: git status を注入

```
{
  "hooks": [
    { "type": "command", "command": "git status --short 2>/dev/null | head -20" }
  ]
}
```

起動時に今のワーキングツリーの状態が見える。「変更点を見てくれ」と言わずに済む。

### 8. UserPromptSubmit: 現在ブランチを注入

```
{
  "hooks": [
    { "type": "command", "command": "git branch --show-current 2>/dev/null | sed 's/^/branch: /'" }
  ]
}
```

ブランチ名から文脈を推論させる。`feature/payment` ブランチなら自然と決済周りの話題を優先する。

### 9. PostToolUse: テスト自動実行

```
{
  "matcher": "Edit|Write",
  "hooks": [
    { "type": "command", "command": "npm test -- --bail --findRelatedTests \"$CLAUDE_FILE_PATHS\" 2>&1 | tail -30" }
  ]
}
```

編集ファイルに関連するテストだけ走らせる。`--bail` で最初の失敗で止める。

### 10. Stop: 作業ログ追記

```
{
  "hooks": [
    { "type": "command", "command": "echo \"[$(date '+%F %T')] session end\" >> ~/.claude/work.log" }
  ]
}
```

セッション終了ごとにログを1行追記。月末に grep して振り返る。

### 11. PreToolUse: .env 読み取り防御

```
{
  "matcher": "Read",
  "hooks": [
    { "type": "command", "command": "grep -q '\\.env' <<< \"$CLAUDE_TOOL_INPUT\" && { echo 'BLOCKED: .env read'; exit 2; } || exit 0" }
  ]
}
```

秘密情報の流出防止。明示的に「読んでいい」と言わない限りブロック。

### 12. PostToolUse: ビルド確認

```
{
  "matcher": "Edit|Write",
  "hooks": [
    { "type": "command", "command": "test -f package.json && npm run build --if-present 2>&1 | tail -10" }
  ]
}
```

大規模編集後にビルドが通るか即確認。壊れたまま次に進まない。

### 13. PreToolUse: npm install 警告

```
{
  "matcher": "Bash",
  "hooks": [
    { "type": "command", "command": "grep -qE 'npm install [^-]' <<< \"$CLAUDE_TOOL_INPUT\" && echo 'WARN: dependency change' || true" }
  ]
}
```

依存追加は必ず人間の目を入れたいので警告を出す。ブロックはしない。

### 14. PostToolUse: コミット後に差分表示

```
{
  "matcher": "Bash",
  "hooks": [
    { "type": "command", "command": "grep -q 'git commit' <<< \"$CLAUDE_TOOL_INPUT\" && git show --stat HEAD || true" }
  ]
}
```

コミット直後に変更サマリが流れるので、意図しないファイルが混ざっていないか即確認できる。

### 15. Stop: 未コミット変更の警告

```
{
  "hooks": [
    { "type": "command", "command": "git status --porcelain 2>/dev/null | head -1 | grep -q . && echo 'WARN: uncommitted changes remain' || true" }
  ]
}
```

セッション終了時に未コミットがあれば注意喚起。放置防止。

## 要点

hooks は「Claude の自由を制限するもの」ではなく「Claude が事故らない環境を作るもの」だ。型チェック・テスト・破壊的コマンド防御・文脈注入の4系統を押さえれば、日々の開発フローは劇的に安定する。まず4番 5番 11番の3つだけでも仕込んでおくと、夜もぐっすり眠れる。
