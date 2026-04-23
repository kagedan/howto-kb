---
id: "2026-04-02-claude-codeのトークン消費が突然10倍になる原因とhookで防ぐ実践的な方法-01"
title: "Claude Codeのトークン消費が突然10倍になる原因と、hookで防ぐ実践的な方法"
url: "https://qiita.com/yurukusa/items/49f1fa305522368d7e7a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-02"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

Claude Codeを使っていて、突然トークン消費が跳ね上がった経験はありませんか？

GitHub Issueには195件以上のリアクションが集まり、「5時間分のquotaが15分で消えた」「300Kトークンのスパイクが発生する」という報告が相次いでいます。

この記事では、トークン消費が爆発する主な原因と、Claude Codeのhook機能を使って**事前に検知・防止する方法**を、実際のhookコードとともに解説します。

## なぜトークン消費が突然爆発するのか

Claude Codeはプロンプトキャッシュを使って、会話履歴の再送信コストを削減しています。通常、キャッシュヒット率は89〜99%程度です。

しかし、**キャッシュが無効化されると、すべての会話履歴を毎ターン再送信する**ことになり、トークン消費が10〜20倍に膨れ上がります。

コミュニティの調査（[@jmarianski氏の分析](https://github.com/anthropics/claude-code/issues/40524)）によると、主な原因は以下の3つです。

### 原因1: セッションファイルの読み取りによるキャッシュ汚染

Claude Codeが自分自身の会話履歴ファイル（`.jsonl`）を読み取ると、CLIが内部的にbilling hashを書き換えます。これによりキャッシュのプレフィックスが変わり、**以降のすべてのターンでキャッシュが効かなくなります**。

実測値：キャッシュ読み取り率が **89% → 4.3%** に暴落し、1ターンあたりのトークン消費が約20倍になったケースが報告されています。

### 原因2: セッション再開時のキャッシュミス

`claude --resume` でセッションを再開すると、最初の1〜2ターンでキャッシュが再構築されます。この間、通常より多くのトークンを消費します。通常は2ターン目以降に回復しますが、他の原因と組み合わさると回復しないケースがあります。

### 原因3: 並列サブエージェントのキャッシュ競合

複数のサブエージェントを同時に起動すると、それぞれが個別のキャッシュエントリを作成するため、親セッションのキャッシュが押し出される可能性があります。7つのサブエージェントを同時起動したところ、一部でキャッシュミスが発生したという報告があります。

## hookで防ぐ：実践的な対策5選

Claude Codeのhook機能を使えば、これらの問題を**自動的に検知・防止**できます。

### 対策1: セッションファイル読み取りブロック（最重要）

最も効果が大きい対策です。Claudeが自分の会話履歴を読めないようにします。

```
// ~/.claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Read",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/conversation-history-guard.sh"
          }
        ]
      }
    ]
  }
}
```

```
#!/bin/bash
# conversation-history-guard.sh
# Claudeが自分の会話履歴を読むとキャッシュが壊れるのを防ぐ

INPUT=$(cat)

# Bashコマンドのチェック
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
if [ -n "$CMD" ]; then
    if printf '%s' "$CMD" | grep -qE '\.(jsonl|log)' && \
       printf '%s' "$CMD" | grep -qiE '(claude|session|billing|transcript)'; then
        cat <<'EOF'
{"decision": "block", "reason": "⚠️ セッションファイルの読み取りはキャッシュを破壊します。外部ターミナルで確認してください。"}
EOF
        exit 0
    fi
fi

# Readツールのチェック
FILE=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
if [ -n "$FILE" ]; then
    if printf '%s' "$FILE" | grep -qE '\.claude/projects/.+\.jsonl$'; then
        cat <<'EOF'
{"decision": "block", "reason": "⚠️ 会話履歴ファイルの読み取りはキャッシュを20倍悪化させます。"}
EOF
        exit 0
    fi
fi

exit 0
```

### 対策2: コンテキスト使用量モニター

コンテキストウィンドウの残量を段階的に警告します。3%まで気づかず使い切る事故を防ぎます。

```
#!/bin/bash
# context-monitor.sh — 4段階警告でコンテキスト枯渇を防止
# PostToolUse で空matcherに設定（全ツール実行後に発火）

STATE_FILE="/tmp/cc-context-state"
COUNTER_FILE="/tmp/cc-context-monitor-count"

COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

# 3回に1回チェック（オーバーヘッド軽減）
[ $((COUNT % 3)) -ne 0 ] && exit 0

# デバッグログからトークン使用量を読み取り
DEBUG_DIR="$HOME/.claude/debug"
if [ -d "$DEBUG_DIR" ]; then
    LATEST=$(find "$DEBUG_DIR" -maxdepth 1 -name '*.txt' -printf '%T@ %p\n' 2>/dev/null \
             | sort -rn | head -1 | cut -d' ' -f2)
    if [ -n "$LATEST" ]; then
        LINE=$(grep 'autocompact:' "$LATEST" 2>/dev/null | tail -1)
        if [ -n "$LINE" ]; then
            TOKENS=$(echo "$LINE" | sed 's/.*tokens=\([0-9]*\).*/\1/')
            WINDOW=$(echo "$LINE" | sed 's/.*effectiveWindow=\([0-9]*\).*/\1/')
            if [ -n "$TOKENS" ] && [ -n "$WINDOW" ] && [ "$WINDOW" -gt 0 ] 2>/dev/null; then
                PCT=$(( (WINDOW - TOKENS) * 100 / WINDOW ))
                if [ "$PCT" -le 15 ]; then
                    echo "🚨 EMERGENCY: コンテキスト残り${PCT}%。即座に/compactを実行してください" >&2
                elif [ "$PCT" -le 20 ]; then
                    echo "⛔ CRITICAL: コンテキスト残り${PCT}%。/compactを推奨します" >&2
                elif [ "$PCT" -le 25 ]; then
                    echo "⚠️ WARNING: コンテキスト残り${PCT}%。現在のタスクを完了させてください" >&2
                fi
            fi
        fi
    fi
fi

exit 0
```

### 対策3: トークン予算ガード

セッション全体のトークン消費量を推定し、設定した予算を超えたら警告・ブロックします。

```
#!/bin/bash
# token-budget-guard.sh — セッションのトークンコスト上限を設定
# PostToolUse で空matcherに設定

WARN_BUDGET="${CC_TOKEN_BUDGET:-10}"   # $10で警告
BLOCK_BUDGET="${CC_TOKEN_BLOCK:-50}"   # $50でブロック
STATE="/tmp/cc-token-budget-$$"

# ツール出力サイズからトークン数を推定
INPUT=$(cat)
OUTPUT=$(echo "$INPUT" | jq -r '.tool_result // empty' 2>/dev/null)
OUTPUT_LEN=${#OUTPUT}

# 概算: 4文字 ≈ 1トークン, Opus入力$15/M + 出力$75/M
EST_TOKENS=$((OUTPUT_LEN / 4))
PREV=$(cat "$STATE" 2>/dev/null || echo 0)
TOTAL=$((PREV + EST_TOKENS))
echo "$TOTAL" > "$STATE"

# ドル換算（概算）
COST_CENTS=$(( TOTAL * 75 / 10000 ))  # $75/M output tokens

if [ "$COST_CENTS" -ge "$((BLOCK_BUDGET * 100))" ]; then
    echo "⛔ セッション推定コスト: \$${COST_CENTS}超。上限\$${BLOCK_BUDGET}に到達。" >&2
    echo '{"decision": "block", "reason": "Token budget exceeded. Start a new session."}'
    exit 0
elif [ "$COST_CENTS" -ge "$((WARN_BUDGET * 100))" ]; then
    echo "⚠️ セッション推定コスト: 約\$${COST_CENTS}。予算\$${WARN_BUDGET}に接近中。" >&2
fi

exit 0
```

### 対策4: compaction検知アラート

自動compactionが発火したことを検知して通知します。compactionの連鎖（compact→再構築→compact）はトークン消費の大きな原因です。

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); if echo \"$INPUT\" | grep -qi compact; then echo \"⚠️ Auto-compaction検知。トークン消費が増加する可能性があります\" >&2; fi; exit 0'"
          }
        ]
      }
    ]
  }
}
```

### 対策5: compaction前のバックアップ

compactionで会話が要約されると、元の情報は失われます。事前にバックアップしておけば、何を失ったか確認できます。

```
#!/bin/bash
# pre-compact-transcript-backup.sh — compaction前に全文保存
# Notification hookで設定

INPUT=$(cat)
if echo "$INPUT" | grep -qi "compact"; then
    BACKUP_DIR="$HOME/.claude/backups"
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)

    # 直近のセッションファイルをバックアップ
    LATEST=$(find "$HOME/.claude/projects" -name "*.jsonl" -newer /tmp/cc-last-compact 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        cp "$LATEST" "$BACKUP_DIR/pre-compact-${TIMESTAMP}.jsonl"
        echo "📦 Compaction前バックアップ: $BACKUP_DIR/pre-compact-${TIMESTAMP}.jsonl" >&2
    fi
    touch /tmp/cc-last-compact
fi

exit 0
```

## 環境設定での追加対策

hookに加えて、環境変数でもトークン消費を抑制できます。

```
// ~/.claude/settings.json
{
  "env": {
    "ENABLE_TOOL_SEARCH": "false"
  }
}
```

`ENABLE_TOOL_SEARCH=false`は、動的なツール検索を無効化します。ツール定義の変更がキャッシュ無効化の一因になるケースが報告されており（[#34629](https://github.com/anthropics/claude-code/issues/34629)）、これを無効にすることでキャッシュの安定性が向上する可能性があります。

## 効果の実測

700時間以上のClaude Code運用で、これらのhookを導入した前後の変化：

| 指標 | 導入前 | 導入後 |
| --- | --- | --- |
| キャッシュ無効化によるセッション喪失 | 月2-3回 | 月0回 |
| コンテキスト枯渇による作業喪失 | 月1-2回 | 月0回（15%で警告が出る） |
| 予期しない高額セッション | 発生あり | 予算ガードで事前検知 |

## まとめ

トークン消費の爆発は、主にプロンプトキャッシュの無効化が原因です。hookで防げる範囲と、プラットフォーム側の問題を正直に分けると：

**hookで防げるもの：**

* セッションファイル読み取りによるキャッシュ汚染 → conversation-history-guard
* コンテキスト枯渇の見逃し → context-monitor
* 予算超過の検知 → token-budget-guard

**hookでは防げないもの（プラットフォーム側の問題）：**

* セッション再開時のキャッシュ再構築コスト
* 並列リクエストのキャッシュ競合
* サーバー側のキャッシュ管理

hookは万能ではありませんが、「防げる事故を確実に防ぐ」ことで、不必要なトークン消費を大幅に減らせます。

すべてのhookは[cc-safe-setup](https://github.com/yurukusa/cc-safe-setup)で公開しています（698 hooks収録、MIT License）。

---

*この記事で紹介した対策をさらに深掘りしたガイドは、[Claude Codeを本番品質にする実践ガイド](https://zenn.dev/yurukusa/books/6076c23b1cb18b)（Zenn Book, ¥800）で体系的に解説しています。800時間の自律稼働で実際にトークン消費とどう戦ったかの全記録は、[AIに仕事を任せてみた——非エンジニアが800時間で学んだ全記録](https://zenn.dev/yurukusa/books/3c3c3baee85f0a19)（¥800・第2章まで無料）にまとめています。*

「自分のCLAUDE.mdがトークンをどれくらい消費しているか」を無料で診断 → [CLAUDE.md Analyzer](https://yurukusa.github.io/cc-safe-setup/claudemd-analyzer.html)  
キャッシュバグを含むトークン消費問題の全体像と対策 → [Token Book](https://yurukusa.github.io/cc-safe-setup/token-book.html)（¥2,500・第1章まで無料）。[#46829](https://github.com/anthropics/claude-code/issues/46829)で判明したキャッシュTTLサイレント変更（1h→5min、コスト20-32%増）への対策も収録

> 🚀 **[cc-safe-setupがProduct Huntに登場](https://www.producthunt.com/posts/cc-safe-setup)** — Claude Codeの安全hookを一発でインストール。701 hooks / 56セクションのSurvival Guide / 無料ツール7個。upvoteで応援お願いします！

> **Opus 4.7で問題が起きていませんか？** [Safety Scanner](https://yurukusa.github.io/cc-safe-setup/opus47-scanner.html)でsettings.jsonの脆弱性を無料チェック。[Survival Guide](https://yurukusa.github.io/cc-safe-setup/opus-47-survival-guide.html)で全対策を確認。

**設定が正しいか不安な方へ**  
[無料で診断](https://yurukusa.github.io/cc-safe-setup/safety-audit.html): `npx cc-health-check` で安全スコアを即座に確認できます。プロによる詳細レビュー（$50〜）も受付中。

「どのhookを入れればいいかわからない」なら → [Hook Selector](https://yurukusa.github.io/cc-safe-setup/hook-selector.html)（5つの質問で最適なhookセットを推薦）  
「CLAUDE.mdのトークンコストが気になる」なら → [Token Checkup](https://yurukusa.github.io/cc-safe-setup/token-checkup.html)（トークン消費パターンを診断）

---

## 追記（2026-04-17）: 8つ目 — Opus 4.7新トークナイザー

4月16日にOpus 4.7がデフォルトモデルになった。APIの単価は据え置きだが、**新しいトークナイザーが同じテキストで最大35%多いトークンを生成する**（[Finout.io分析](https://www.finout.io/blog/claude-opus-4.7-pricing-the-real-cost-story-behind-the-unchanged-price-tag)）。コード・構造化データ・非英語テキストで特に顕著。

コーディングエージェントの試算: **$10/day → $13.50/day（+35%）**。

さらに深刻なのは、auto modeの安全分類器がOpus 4.6にハードコードされていた問題（[#49618](https://github.com/anthropics/claude-code/issues/49618)）。3日間で20件以上のデータ損失が報告されている。

対策はPreToolUseフックの導入。モデルバージョンに依存しない安全装置になる。

---

---

**📖 トークン消費に困っているなら** → [Claude Codeのトークン消費を半分にする——800時間の運用データから見つけた実践テクニック](https://zenn.dev/yurukusa/books/token-savings-guide?utm_source=qiita-49f1fa30&utm_medium=article&utm_campaign=token-book)（¥2,500・第1章無料）| [Ko-fi $17](https://ko-fi.com/s/fd44ef09a7)

> **📖 [非エンジニアがClaude Codeで事業を回した全記録（¥800）](https://zenn.dev/yurukusa/books/cc-ai-business-diary?utm_source=qiita-batch&utm_medium=cta&utm_campaign=book3)** — $800のAIコストで¥6,000を稼ぐまでの失敗と改善。第2章まで無料

---

**関連記事**: [Claude Codeのトークン消費を減らす5つの方法——Opus 4.7対応](https://qiita.com/yurukusa/items/435810e1e8a046c99916)

---

**⚠️ CVE-2026-21852（2026年4月公開）**: プロジェクト内`.claude/settings.json`経由でAPIキー窃盗。対策: `npx cc-safe-setup`（ユーザーレベル設定で免疫）→ [詳細](https://yurukusa.github.io/cc-safe-setup/opus-47-survival-guide.html#cve-settings-exfil)
