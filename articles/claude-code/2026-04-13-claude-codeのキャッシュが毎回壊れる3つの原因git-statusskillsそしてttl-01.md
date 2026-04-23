---
id: "2026-04-13-claude-codeのキャッシュが毎回壊れる3つの原因git-statusskillsそしてttl-01"
title: "Claude Codeのキャッシュが毎回壊れる3つの原因——git status、skills、そしてTTLサイレント変更"
url: "https://qiita.com/yurukusa/items/e8a8af7356cacd4fb371"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

Claude Codeのプロンプトキャッシュが壊れると、トークン消費が数倍に跳ね上がる。

「昨日まで普通に使えていたのに、今日は5時間制限の16%が一瞬で消えた」——[#47108](https://github.com/anthropics/claude-code/issues/47108)の報告だ。原因はキャッシュの仕組みにある。

## プロンプトキャッシュとは

Claude Codeは毎ターン、システムプロンプト（CLAUDE.md、skills、設定情報）をAPIに送信する。キャッシュが効いていれば、前回と同じ部分は再計算されない。効いていなければ、全文が新規トークンとして課金される。

キャッシュが効いている状態では1ターンの消費が軽い。壊れると同じ操作でも消費が2〜5倍になる。

## 原因1: git statusがシステムプロンプトに含まれる

[#47107](https://github.com/anthropics/claude-code/issues/47107)で指摘された問題。Claude Codeはシステムプロンプトに現在のgit statusを含める。つまり:

* ファイルを1つ変更するとgit statusが変わる
* git statusが変わるとシステムプロンプトが変わる
* システムプロンプトが変わるとキャッシュが壊れる

**コードを書くたびにキャッシュが壊れる。**

### 回避策

環境変数で無効化できる:

```
export CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1
claude
```

ただしgit関連の指示がなくなるため、gitを多用するワークフローでは注意が必要。

## 原因2: skills + CLAUDE.mdが毎回キャッシュを再生成する

[#47098](https://github.com/anthropics/claude-code/issues/47098)の発見。新しいセッションを開始すると、skills・CLAUDE.md・設定情報（約6,500トークン）がキャッシュなしで送信される。

これは仕様上避けられない——新セッションには前回のキャッシュがない。問題は、この6,500トークンのキャッシュ作成が**セッションを開始するたびに発生する**こと。

セッションを頻繁に切り替える使い方だと、毎回6,500トークンのオーバーヘッドが積み重なる。

### 回避策

* **セッションを安易に切り替えない**。1セッション=1テーマで、テーマが完了するまで続ける
* **CLAUDE.mdを短くする**。長いCLAUDE.mdはキャッシュ再生成コストを増やす。100行→35行に凝縮するとキャッシュ効率が改善する
* **skillsを整理する**。使わないskillsは無効化する

## 原因3: Cache TTLが1時間→5分にサイレント変更された

[#46829](https://github.com/anthropics/claude-code/issues/46829)で報告された問題。2026年3月初旬、Anthropicはプロンプトキャッシュの有効期間（TTL）を1時間から5分に短縮した。**事前の告知なし**。

何が起きるか:

* 以前は1時間以内の操作ならキャッシュが効いていた
* 5分に短縮されたため、少し考えたり休憩したりするとキャッシュが切れる
* キャッシュミス → 全文再送信 → トークン消費が20-32%増加

**5分間操作しないだけでキャッシュが消える。** コードを読んで考える時間、ドキュメントを確認する時間——人間にとって普通のペースがキャッシュを壊す。

### 回避策

* **作業を中断しない**。5分以内に次の操作を行う
* **長考が必要なら新セッションを前提にする**。--resumeは使わない（[#42338](https://github.com/anthropics/claude-code/issues/42338)でキャッシュ完全無効化が報告されている）
* **hookでキャッシュ効率を監視する**（下記参照）

## hookでキャッシュ破壊を検知する

settings.jsonのhookで、キャッシュ効率の低下を自動検知できる:

```
#!/bin/bash
# cache-efficiency-monitor.sh (PostToolUse hook)
# セッション中のトークン消費を記録し、急増を警告
SESSION_LOG="/tmp/cc-token-session-$(date +%Y%m%d).log"
INPUT=$(cat)
TOKENS=$(echo "$INPUT" | jq -r '.session_tokens // empty' 2>/dev/null)
[ -z "$TOKENS" ] && exit 0

echo "$(date +%H:%M:%S) $TOKENS" >> "$SESSION_LOG"
exit 0
```

## まとめ

キャッシュ破壊の3大原因:

1. **git statusの変更**（ファイル編集のたびに発生）→ `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1`で回避
2. **セッション切り替え時の再生成**（6,500トークン/回）→ セッション頻度を減らす + CLAUDE.mdを短く
3. **Cache TTLサイレント短縮**（1h→5min、2026年3月）→ 5分以上の中断でキャッシュ消失。コスト20-32%増

**自分のキャッシュ効率を確認したい方へ**  
[Token Checkup](https://yurukusa.github.io/cc-safe-setup/token-checkup.html)で5つの質問に答えるだけでトークン消費パターンを診断できる（無料）。

---

**📖 トークン消費に困っているなら** → [Claude Codeのトークン消費を半分にする——800時間の運用データから見つけた実践テクニック](https://zenn.dev/yurukusa/books/token-savings-guide?utm_source=qiita-e8a8af73&utm_medium=article&utm_campaign=token-book)（¥2,500・はじめに+第1章 無料）

---

**関連記事**: [Claude Codeのトークン消費を減らす5つの方法——Opus 4.7対応](https://qiita.com/yurukusa/items/435810e1e8a046c99916)  
:::note info  
**📖 AIで事業を回す実体験を全記録** → [Claude Code×個人事業 800時間の全記録](https://zenn.dev/yurukusa/books/3c3c3baee85f0a19?utm_source=qiita-e8a8af7356ca&utm_medium=article&utm_campaign=book3)（¥800・第2章まで無料）  
:::

---
