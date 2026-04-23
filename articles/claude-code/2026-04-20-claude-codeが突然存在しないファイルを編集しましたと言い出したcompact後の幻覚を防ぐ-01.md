---
id: "2026-04-20-claude-codeが突然存在しないファイルを編集しましたと言い出したcompact後の幻覚を防ぐ-01"
title: "Claude Codeが突然「存在しないファイルを編集しました」と言い出した——compact後の幻覚を防ぐhook"
url: "https://qiita.com/yurukusa/items/a4a79ee057de1e532ff3"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

3時間のセッション中に突然、Claudeが「先ほど作成したutils/helper.tsを更新しました」と言い出した。そんなファイルは作っていない。

これはcontext compaction後に発生する「幻覚」で、GitHub Issue [#46602](https://github.com/anthropics/claude-code/issues/46602) で報告された（現在はクローズ済み、ただしcompactionの仕組み上、類似の現象は依然として発生しうる）。compactionで会話履歴が要約される際に、要約が不正確になり、Claudeが「やっていないこと」を「やった」と認識してしまう現象だ。

## 何が起きるのか

context compactionは、コンテキストウィンドウが一杯になると自動で実行される。古い会話を圧縮して容量を空ける処理だ。問題は、この圧縮で情報が失われること。

具体的には:

* 「ファイルAを編集した」という記録が「ファイルA,B,Cを編集した」に要約される
* 実際には存在しないファイルへの言及が生まれる
* Claudeがその幻覚に基づいて行動し、存在しないファイルを上書きしようとする

最悪のケースでは、幻覚に基づいてCLAUDE.mdの指示を「捏造」し、ユーザーが書いていないルールに従って暴走する事例もある。

## PreCompactフックによる防御

v2.1.83で追加された`PreCompact`フックイベントを使えば、compaction直前にgitチェックポイントを作成できる。幻覚が発生しても、チェックポイントとの差分で「何が本当に変更されたか」を確認できる。

```
#!/bin/bash
# pre-compact-checkpoint.sh
git rev-parse --is-inside-work-tree &>/dev/null || exit 0
CHANGES=$(git status --porcelain 2>/dev/null | wc -l)
[ "$CHANGES" -eq 0 ] && exit 0

TIMESTAMP=$(date -u '+%Y%m%d-%H%M%S')
git add -A 2>/dev/null
git commit -m "checkpoint: pre-compact auto-save (${CHANGES} files, ${TIMESTAMP})" \
  --no-verify 2>/dev/null

echo "Pre-compact checkpoint: ${CHANGES} file(s) saved" >&2
exit 0
```

```
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/pre-compact-checkpoint.sh"
          }
        ]
      }
    ]
  }
}
```

> **Note:** `PreCompact`はmatcher不要。PreToolUseと違い、compaction発生時に常に実行される。

インストール:

```
npx cc-safe-setup --install-example pre-compact-checkpoint
```

## compaction後の確認手順

compaction後にClaudeが「〜を変更しました」と言ったら、まず確認する:

```
# チェックポイント以降の実際の変更を確認
git diff HEAD

# チェックポイントの内容を確認
git log --oneline -5
git show HEAD --stat
```

`git diff HEAD`で差分がなければ、Claudeの報告は幻覚。差分があれば本当の変更。

## CLAUDE.mdへの防御指示

CLAUDE.mdに以下を追加しておくと、compaction後のClaudeに「自分の記憶を疑え」と伝えられる:

```
# compaction後の復旧手順
context compaction後は自分の記憶を信用しないでください。
1. `git log --oneline -5` でチェックポイントを確認
2. `git diff HEAD` で実際の変更を確認
3. 記憶と差分が一致しない場合は、差分を正とする
```

## なぜ根本修正が難しいのか

compactionの要約精度を100%にするのは原理的に難しい。長い会話を短く要約する以上、情報の欠落は避けられない。

現実的な対策は:

1. **PreCompactフックでチェックポイントを作る**（この記事の方法）
2. **こまめにgit commitする**（手動でも自動でも）
3. **長すぎるセッションを避ける**（2-3時間で区切る）

---

「どのhookを入れればいいかわからない」なら → [Hook Selector](https://yurukusa.github.io/cc-safe-setup/hook-selector.html)（30秒で推薦）  
「トークンがどこで消えているか知りたい」なら → [Token Checkup](https://yurukusa.github.io/cc-safe-setup/token-checkup.html)（5問で診断）
