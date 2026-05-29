---
id: "2026-05-28-金曜日にデプロイさせないhookを含むclaude-codeのちょっと面白いhook-7選-01"
title: "金曜日にデプロイさせないhookを含む、Claude Codeの「ちょっと面白い」hook 7選"
url: "https://qiita.com/yurukusa/items/4f4137c47081ce403e98"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-05-28"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

Claude Code hookは真面目な安全装置だが、面白いやつもある。

## 1. no-deploy-friday — 金曜にデプロイさせない

```bash
#!/bin/bash
CMD=$(cat | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$CMD" ] && exit 0
DOW=$(date +%u)
if [ "$DOW" = "5" ]; then
    echo "$CMD" | grep -qiE 'deploy|firebase|vercel|netlify' && \
        echo "BLOCKED: No deploys on Friday. Come back Monday." >&2 && exit 2
fi
exit 0
```

`npx cc-safe-setup --install-example no-deploy-friday`

## 2. loop-detector — 同じコマンドを5回繰り返したら止める

Claudeは時々「テスト実行→失敗→同じテスト実行→失敗...」を永遠に繰り返す。

```bash
npx cc-safe-setup --install-example loop-detector
```

3回で警告、5回でブロック。

## 3. cost-tracker — 「今いくら使った？」を表示

```bash
npx cc-safe-setup --install-example cost-tracker
```

Opus換算で$1超えたら警告。$5超えたらアラート。

## 4. commit-quality-gate — 「update code」を許さない

```bash
npx cc-safe-setup --install-example commit-quality-gate
```

「update」「fix」「changes」だけのcommitメッセージを警告。72文字超も警告。

## 5. diff-size-guard — 50ファイル変更したら止める

```bash
npx cc-safe-setup --install-example diff-size-guard
```

10ファイルで警告、50ファイルでブロック。レビューできない量は出させない。

## 6. session-handoff — 「何やってたっけ？」を解消

```bash
npx cc-safe-setup --install-example session-handoff
```

セッション終了時にgit状態と作業内容を自動保存。次のセッションで読める。

## 7. protect-claudemd — AIに自分の設定ファイルを書き換えさせない

```bash
npx cc-safe-setup --install-example protect-claudemd
```

CLAUDE.mdやsettings.jsonへのEdit/Writeをブロック。AIが自分のルールを変えるのを防ぐ。

---

全67hookを探す: `npx cc-hook-registry search <キーワード>`

真面目な安全hookは: `npx cc-safe-setup`

---

📘 [Claude Codeを本番品質にする——700+時間の自律稼働から生まれた実践ガイド](https://zenn.dev/yurukusa/books/6076c23b1cb18b)（¥800）

**Claude Codeのセットアップ、本当に安全ですか？** `npx cc-health-check` で20項目の無料診断ができます。スコア80未満なら改善の余地あり。
