---
id: "2026-04-13-claude-codeのdeny-rulesが50コマンドで無効化されるhookで防ぐ方法-01"
title: "Claude Codeのdeny rulesが50コマンドで無効化される——hookで防ぐ方法"
url: "https://qiita.com/yurukusa/items/f9c48bb44569bbf4492e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

Claude Codeのdeny rules（禁止ルール）に、深刻な脆弱性が見つかった。

**50個以上のサブコマンドを連結すると、すべてのdeny rulesが無効化される。**

[Adversa AI](https://adversa.ai/blog/claude-code-security-bypass-deny-rules-disabled/)の調査で判明した。内部的に50サブコマンドの上限があり、50を超えるとセキュリティチェックがスキップされて「ユーザーに確認」にフォールバックする。自律運行中（`--dangerously-skip-permissions`等）ではそのまま実行される。

## 何が起きるか

settings.jsonにこう書いてあるとする:

```
{
  "permissions": {
    "deny": ["Bash(rm *)"]
  }
}
```

`rm -rf /important-data` は単体ではブロックされる。しかし:

```
true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; true; rm -rf /important-data
```

これはブロックされない。50個の`true`（何もしないコマンド）の後に危険なコマンドを置くだけで、deny rulesを完全にバイパスできる。

## 同時期に起きた実被害

この脆弱性と同じ4月に報告された実害:

deny rulesを設定していても安全ではない。

## パッチ状況

Anthropicは[v2.1.90（4月6日リリース）](https://github.com/anthropics/claude-code/releases)でこの脆弱性を修正した。**v2.1.90以上にアップデートしていれば、deny rules自体は正常に動作する。**

ただし、deny rulesには構造的な限界がある:

* パターンマッチングに依存するため、コマンドの書き方を変えるだけで回避される可能性がある
* 新しいバイパス手法が見つかるたびにアップデートが必要

hookはdeny rulesの上位互換として、コマンドの内容を自由にスクリプトで検査できる。アップデートを待たずに自分で防御ロジックを書ける。

## hookで防ぐ

PreToolUse hookはdeny rulesとは別の仕組みで動く。サブコマンド数の制限を受けない。

```
#!/bin/bash
# subcommand-chain-guard.sh
THRESHOLD=${CC_SUBCOMMAND_LIMIT:-20}
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$CMD" ] && exit 0

SUBCOMMAND_COUNT=$(echo "$CMD" | tr ';' '\n' | tr '&' '\n' | tr '|' '\n' | grep -c '[^ ]' 2>/dev/null || echo 1)

if [ "$SUBCOMMAND_COUNT" -gt "$THRESHOLD" ]; then
    echo "BLOCKED: Command contains $SUBCOMMAND_COUNT subcommands (limit: $THRESHOLD)." >&2
    echo "  Claude Code ignores deny rules after 50 subcommands." >&2
    exit 2
fi

# 50個のtrue + 危険コマンドのパターンも検出
NOOP_COUNT=$(echo "$CMD" | grep -oE '\btrue\b|^:|;\s*:' | wc -l 2>/dev/null || echo 0)
if [ "$NOOP_COUNT" -gt 10 ]; then
    echo "BLOCKED: Suspicious no-op padding detected ($NOOP_COUNT no-ops)." >&2
    exit 2
fi

exit 0
```

settings.jsonに追加:

```
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "bash ~/.claude/hooks/subcommand-chain-guard.sh"
      }]
    }]
  }
}
```

## ワンコマンドで導入

[cc-safe-setup](https://github.com/yurukusa/cc-safe-setup)（664個以上のhook）にこのhookが含まれている:

個別にインストールする場合:

```
npx cc-safe-setup --install-example subcommand-chain-guard
```

**キャッシュ破壊でトークンが数倍消費される問題**  
deny rulesバイパスだけでなく、git statusがキャッシュを壊す構造的問題も発見されている。[Cache Breakage Fix](https://gist.github.com/yurukusa/fe6ba0a6aee14207f27ecc84419878b4)で原因と対策をまとめた。

**自分の環境が脆弱か確認する**  
[Security Checkup](https://yurukusa.github.io/cc-safe-setup/security-checkup.html)で6つの質問に答えるだけで、deny rulesバイパスを含むClaude Codeの脆弱性を診断できる（無料）。

---

**📖 トークン消費に困っているなら** → [Claude Codeのトークン消費を半分にする——800時間の運用データから見つけた実践テクニック](https://zenn.dev/yurukusa/books/token-savings-guide?utm_source=qiita-f9c48bb4&utm_medium=article&utm_campaign=token-book)（¥2,500・はじめに+第1章 無料）

---
