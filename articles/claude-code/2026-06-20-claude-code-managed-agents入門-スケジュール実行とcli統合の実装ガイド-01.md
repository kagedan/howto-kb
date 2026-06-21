---
id: "2026-06-20-claude-code-managed-agents入門-スケジュール実行とcli統合の実装ガイド-01"
title: "Claude Code Managed Agents入門 — スケジュール実行とCLI統合の実装ガイド"
url: "https://qiita.com/kai_kou/items/337eb235da9b9a081836"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

## TL;DR

2026年6月、Anthropic が **Claude Code Managed Agents** をパブリックベータリリース。
スケジュール実行（cron）・CLI tools 安全統合・Vault管理の環境変数が組み込まれた
エージェント自動化基盤が登場しました。本ガイドではAPI実装～本番運用まで完全網羅します。

---

## 1. Managed Agents とは

従来の Claude API（call-and-response）では、毎回ユーザーがトリガーして
エージェントを起動する必要がありました。**Managed Agents** は以下を内包：

| 機能 | 説明 |
|-----|------|
| **Schedule-based Execution** | cron記法でスケジュール定義。24時間無人で自動実行 |
| **Secure CLI Tool Integration** | Shell commands を安全にエージェントから実行（ホワイトリスト制御） |
| **Vault-stored Environment Variables** | Secrets.json で API キー・DB パスワード等を暗号化管理 |
| **Managed Lifecycle** | エージェント実行の state 管理・failure recovery 自動化 |

**向いてる用途**:
- 日次・週次の自動レポート生成
- 定期的なデータ収集・ETL
- スケジュール定期実行の監視タスク
- CI/CD パイプラインの AI 駆動オーケストレーション

---

## 2. 実装ステップ

### 2.1 エージェント定義（AGENTS.md 形式）

Claude Code では `.claude/agents/my-agent.md` 形式で定義：

```yaml
---
name: daily-report-generator
description: |
  毎日 09:00 JST にQiita・Zenn・noteの最新トレンドを収集し、
  Slack に自動投稿するレポートジェネレーター。
schedule: "0 9 * * *"  # 毎日9:00 実行（UTC）
tools:
  - web_search
  - file_read
  - file_write
environment:
  - SLACK_WEBHOOK_URL  # vault から読み込み
  - QIITA_TOKEN
tools_timeout: 300      # 5分でタイムアウト
max_iterations: 10      # 最大ループ回数
---

## ロール

このエージェントは以下のロールを持ちます：

### リサーチャー
Web search で最新トレンド記事を検索（過去24時間のみ）

### データ分析官
収集データから「読者へのインパクト」で Top 5 を抽出

### レポーター
Markdown 形式で整理し、Slack webhook 経由で投稿
```

### 2.2 環境変数の Vault 管理

`claude-code-cloud/.secrets.json` に暗号化して保存：

```json
{
  "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/...",
  "QIITA_TOKEN": "...",
  "ZENN_API_KEY": "..."
}
```

**ポイント**: リポジトリに commit しない（`.gitignore` で除外）。
CloudSecret や GitHub Secrets 連携で、プロセスが開始時に Vault から inject。

### 2.3 CLI Tools のホワイトリスト制御

Managed Agents が実行可能な shell コマンドを明示的に許可：

```yaml
allowed_commands:
  - curl          # HTTP リクエスト
  - python3       # 処理スクリプト実行
  - npm run       # パイプライン実行
  - date          # タイムスタンプ取得
  - jq            # JSON parsing

blocked_patterns:
  - "rm -rf"
  - "sudo"
  - "ssh"
  - "/etc/passwd"
```

### 2.4 スケジュール定義（cron 形式）

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 7) (0 and 7 are Sunday)
│ │ │ │ │
│ │ │ │ │
* * * * *

例：
0 9 * * *         毎日 09:00 実行
*/30 * * * *       30分ごと実行
0 0 1 * *         毎月1日00:00 実行
0 9-17 * * 1-5    平日 9-17時 毎時 00分実行
```

---

## 3. 実装例：日次トレンドレポート

以下は実装フローの完全例：

### ステップA: Web 検索フェーズ

```python
import anthropic
from datetime import datetime, timedelta

client = anthropic.Anthropic(api_key="YOUR_KEY")

SEARCH_PROMPT = """
過去24時間のAI技術トレンドを検索してください。
以下のテーマ優先：
- Claude / Anthropic
- エージェント / LLM
- Gemini / GoogleAI
- MCP
- セキュリティ

結果をMarkdown形式で返す。
各項目は {数値: いいね数・いいね率, リンク, 概要} を含む。
"""

message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=2000,
    system="You are a research analyst for AI trends.",
    messages=[
        {"role": "user", "content": SEARCH_PROMPT}
    ]
)

research_text = message.content[0].text
```

### ステップB: 分析・抽出フェーズ

```python
ANALYSIS_PROMPT = f"""
以下の収集結果から「読者インパクト Top 5」を抽出してください。

{research_text}

出力形式:
1. タイトル - いいね数 | 📊 伸びるテーマ度
2. ...

判定基準:
- ✅ 伸びる: ハンズオン・CLI・自動化・Security・エージェント
- ❌ 伸びない: 単なるモデル紹介・エンタープライズニュース
"""

analysis_message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1500,
    messages=[
        {"role": "user", "content": ANALYSIS_PROMPT}
    ]
)

top_5_text = analysis_message.content[0].text
```

### ステップC: Slack 投稿フェーズ

```python
import requests
import os
from datetime import datetime as dt

webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
jst_now = dt.now().isoformat()

slack_payload = {
    "text": f"🤖 AI Trends Report - {jst_now}",
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 AI Trends Report（24h）"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": top_5_text
            }
        }
    ]
}

response = requests.post(webhook_url, json=slack_payload)
print(f"Slack posted: {response.status_code}")
```

---

## 4. ベストプラクティス

### 4.1 エラーハンドリング

```python
# Managed Agent の内部エラーは自動リトライ
# ただし、timeout / tool_error の場合は以下で catch

try:
    response = client.messages.create(...)
except anthropic.APIStatusError as e:
    if e.status_code == 504:  # Gateway timeout
        print("Tool execution timeout - agent will retry next schedule")
    elif e.status_code == 403:  # Permission denied
        print("Tool not in allowed_commands - check whitelist")
    raise
```

### 4.2 State 管理

```python
# Managed Agent は execution state を自動保存
# 前回実行の context を活用できる

STATEFUL_PROMPT = """
前回実行（24時間前）の結果: {previous_result}

今回実行で新しく追加されたトレンド（重複排除）を
抽出してください。
"""
```

### 4.3 リソース制限

```yaml
agent_config:
  max_tokens_per_call: 2000      # 1call の token 上限
  max_tool_calls: 20             # 最大 tool call 数
  timeout_seconds: 300           # 5分でタイムアウト
  max_iterations: 10             # 最大 conversation loop
```

---

## 5. 監視・デバッグ

### 5.1 Execution Logs

Managed Agent の実行ログは Cloud Console から確認：

```bash
# CLI でログ確認
claude logs my-agent --since 24h

# Output:
# 2026-06-19T09:00:00Z | START
# 2026-06-19T09:00:15Z | web_search called (Query: ...)
# 2026-06-19T09:00:45Z | file_write called (Path: reports/...)
# 2026-06-19T09:01:12Z | SLACK_WEBHOOK triggered
# 2026-06-19T09:01:20Z | SUCCESS
```

### 5.2 失敗時の自動通知

```yaml
notifications:
  on_failure:
    slack: true
    email: ops@company.com
  retry_policy:
    max_attempts: 3
    backoff: exponential
```

---

## 6. 制限事項・注意

| 項目 | 制限 |
|-----|------|
| Max context window | Agent depends on model（Opus 4.8 = 1M） |
| Tool call timeout | 300秒（5分）以上の I/O はタイムアウト |
| Concurrent agents | Account 単位で上限あり（通常 10 agents） |
| Schedule frequency | 最小 1分単位。秒単位は非対応 |
| Tool whitelist | 許可コマンド以外は実行不可（セキュリティ） |

---

## 7. まとめ・次のステップ

### できるようになること

✅ Cron スケジュールで エージェント自動実行  
✅ CLI tools を安全に統合（ホワイトリスト制御）  
✅ Vault で secrets 暗号化管理  
✅ Slack / Email への自動通知  
✅ 複雑なワークフロー（search → analyze → post）の完全自動化  

### 本格導入チェックリスト

- [ ] `.claude/agents/my-agent.md` でエージェント定義
- [ ] `.secrets.json` で環境変数設定（gitignore 確認）
- [ ] 許可コマンド whitelist を最小権限で定義
- [ ] Timeout / retry policy を本番要件に合わせ設定
- [ ] 本番前に dry-run で 24時間監視
- [ ] Slack / email notification を設定
- [ ] Execution logs の monitoring dashboard を構築

---

## 参考リンク

Sources:
- [Anthropic Newsroom - June 2026](https://www.anthropic.com/news)
- [Claude Code Documentation](https://claude.ai/docs)
- [Managed Agents - Public Beta](https://www.anthropic.com/features/managed-agents)
