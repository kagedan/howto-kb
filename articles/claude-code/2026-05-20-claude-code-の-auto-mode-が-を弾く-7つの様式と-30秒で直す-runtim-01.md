---
id: "2026-05-20-claude-code-の-auto-mode-が-を弾く-7つの様式と-30秒で直す-runtim-01"
title: "Claude Code の Auto Mode が $() を弾く 7つの様式と、 30秒で直す runtime の hook"
url: "https://qiita.com/yurukusa/items/05bb2544d34dcfc64ce0"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-05-20"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

# Claude Code の Auto Mode が `$()` を弾く 7つの様式と、 30秒で直す runtime の hook

Claude Code の Auto Mode で `echo "build $(date)" > VERSION` を実行しようとして、 `Command contains $() command substitution` の警告で弾かれた経験はあるか。 これは利用者の側の `settings.json` の `Bash(...)` の allow-list で解決できない、 上流の不具合 ([anthropics/claude-code#38537](https://github.com/anthropics/claude-code/issues/38537)、 49 reactions) の表面化である。

本記事は、 Auto Mode の許可の prompt の false positive の 7つの様式と、 各々の解決の経路 (`PreToolUse` の hook で構造の安全な命令を承認する) と、 即時の診断の道具を整理する。

## 問題の構造

Auto Mode の Bash の道具の呼び出しを判定する分類器は、 「危険な可能性」 の様式を遮断する。 ただし、 利用者の側で `settings.json` の `Bash(...)` で allow-list を設定しても、 分類器は allow-list の前に発火するため、 該当の命令を allow-list と比較する前に拒否する。

つまり、 `settings.json` の経路では解決できない。 `PreToolUse` の hook で、 構造の安全な命令を分類器の判定の前に承認する経路が、 利用者の側の唯一の解決の経路である。

## 7つの様式の整理

### 様式1. `$()` の命令の置換

最も明白な false positive。 `$()` の中身が読み取り専用の命令 (`date`、 `pwd`、 `git rev-parse`) で、 外側の命令が非破壊の操作でも、 分類器は `$(...)` の段で遮断する。

```bash
echo "Build at $(date)" > VERSION
mkdir -p "logs/$(date +%Y-%m-%d)"
cp file "backup-$(git rev-parse --short HEAD).txt"
```

上流の起票: [#38537](https://github.com/anthropics/claude-code/issues/38537) (49 reactions)

### 様式2. pipe の連鎖

[#30435](https://github.com/anthropics/claude-code/issues/30435) (29 reactions) で報告。 各々の命令が読み取り専用でも、 pipe の段で分類器が遮断する。

```bash
ls -la | grep '\.log$'
cat /var/log/syslog | tail -100
ps aux | grep node
```

### 様式3. compound の git の命令

[#30519](https://github.com/anthropics/claude-code/issues/30519) で報告。 `Bash(git:*)` の wildcard は単独の git の命令にのみ一致、 `&&` や `;` で連結された compound の段では allow-list の経路を素通する。

```bash
cd src && git log
git add file.txt && git commit -m 'fix'
git fetch && git rebase origin/main
```

### 様式4. heredoc

`<<` の段が redirect として読まれ、 分類器が遮断する場合がある。

```bash
cat <<'EOF'
hello
EOF
```

### 様式5. `for` と `while` の loop

loop の段の構造そのものが分類器の遮断の対象。 内側が `wc -l` 等の読み取り専用でも遮断する。

```bash
for f in *.log; do wc -l "$f"; done
while read -r line; do echo "$line"; done < input.txt
```

### 様式6. `find ... -exec`

`-exec` の段が 「道具の中の道具の呼び出し」 として権限の拡大の対象に読まれ、 分類器が遮断する。

```bash
find . -name '*.log' -exec wc -l {} \;
find /var/log -mtime -1 -type f -exec ls -la {} \;
```

### 様式7. process substitution `<(cmd)` / `>(cmd)`

`$()` の命令の置換と構造の類似で、 同じ分類器の遮断の経路に乗る。

```bash
diff <(sort a.txt) <(sort b.txt)
tee >(grep error > errors.log) >(wc -l > linecount.txt) < input.log
```

## 30秒で直す runtime の hook

`cc-safe-setup` の `auto-mode-safe-commands.sh` の `PreToolUse` の hook で、 構造の安全な命令を分類器の判定の前に承認する。

### 設置

```bash
curl -fsSL https://raw.githubusercontent.com/yurukusa/cc-safe-setup/main/examples/auto-mode-safe-commands.sh \
  -o ~/.claude/hooks/auto-mode-safe-commands.sh
chmod +x ~/.claude/hooks/auto-mode-safe-commands.sh
```

### `settings.json` の登録

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/auto-mode-safe-commands.sh"
      }]
    }]
  }
}
```

### 検査の経路

設置の後、 `echo "now: $(date)" > /tmp/timestamp.txt` 等の命令を Claude Code の作業の中で実行する。 設置の前は分類器の警告で弾かれた命令が、 設置の後は警告なしで通る状態になる。

該当しない命令 (例: `rm -rf /` 等の真に破壊の命令) は引き続き通常の prompt の経路で確認の対象。 hook は構造の安全な命令の経路だけを開く。

## 即時の診断の道具

自分の手元の命令が false positive の対象かを即時に判定する単独の頁の道具を公開した: [Auto Mode False Positive Diagnoser](https://htmlpreview.github.io/?https://gist.githubusercontent.com/yurukusa/964629cb1a1d8af717a09ef34fe19d68/raw/auto-mode-diagnoser.html)。

利用者が `Bash` の命令を貼り付けると、 7つの様式の各々の解析の結果と、 該当する場合の install の経路を即時に表示する。 外部の依存なし、 通信なし、 telemetry なし、 単独の HTML の頁。

## 何故 `Bash(*)` の経路で済まないか

`Bash(*)` の allow-list は `rm -rf /` 等の真に破壊の命令も含めて全件を承認する。 分類器の段は真に危険な命令を遮断するために存在する。 runtime の hook は 「構造の安全な命令だけを通す」 の経路で、 false positive の修正 + 真に危険な命令の確認の両方を維持する。

破壊の損失への防衛の追加が必要な場合は、 [Defense Kit](https://gist.github.com/yurukusa/c44e28ea04acdad7e7ed48c3e01dbb78) で 11件の破壊の損失の事例への対応の hook の install の経路を整理している。 `rm-safety-net`、 `ssh-key-protect`、 `git-history-rewrite-guard` 等の hook で、 false positive の修正と真に危険な命令の遮断の両方を実現可能。

## 関連の起票と参考

- 上流の分類器の false positive の親の起票: [anthropics/claude-code#38537](https://github.com/anthropics/claude-code/issues/38537) (49 reactions)
- pipe の連鎖の起票: [#30435](https://github.com/anthropics/claude-code/issues/30435) (29 reactions)
- compound の git の起票: [#30519](https://github.com/anthropics/claude-code/issues/30519)
- 英語版の長編 Gist: <https://gist.github.com/yurukusa/21a8295c0b990ce477cd6dffc5f4cafe>
- `cc-safe-setup` の repo: <https://github.com/yurukusa/cc-safe-setup>

利用者の側の許可の prompt の false positive の対応の経路は、 上流の分類器の修正の経路と並行で、 利用者の側の runtime の hook の経路で先行できる。 30秒の install と数行の `settings.json` の修正で、 7つの様式の遮断は同時に解消する。
