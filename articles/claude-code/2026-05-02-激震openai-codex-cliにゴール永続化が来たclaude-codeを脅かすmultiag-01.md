---
id: "2026-05-02-激震openai-codex-cliにゴール永続化が来たclaude-codeを脅かすmultiag-01"
title: "【激震】OpenAI Codex CLIに「ゴール永続化」が来た！Claude Codeを脅かすMultiAgentV2の全貌"
url: "https://qiita.com/emi_ndk/items/377f89d24b6ea520e90b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "TypeScript"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

**「AIエージェントを途中で止めても、続きから再開できたら...」**

この夢、ついに叶いました。

## 結論から言うと

OpenAI Codex CLIの2026年5月アップデートで「**Persisted Goal Workflows**」が追加されました。これは：

- AIエージェントのゴールを**永続的に保存**
- 途中で中断しても**続きから再開可能**
- 複数エージェントが**同時並列で作業**

つまり、「寝てる間にコードを書かせて、朝起きたら続きをやらせる」が現実になったんです。

## なぜこれがヤバいのか

Claude Codeユーザーなら分かるはず。

長時間タスクを実行中に：
- PCがスリープした
- ネットワークが切れた
- 「ちょっと待って」と止めた

**全部やり直し。**

この苦痛から、Codex CLIユーザーは解放されました。

## Persisted Goal Workflowsの仕組み

```bash
# ゴールを設定（永続化される）
codex goal create "このリポジトリをTypeScript化して"

# 一時停止
codex goal pause

# 翌日、続きから再開
codex goal resume

# 完了したらクリア
codex goal clear
```

ゴールは**app-server APIs**を通じて永続化され、Codex CLIを閉じても消えません。

:::note info
これはローカルファイルではなく、OpenAIのサーバーに保存されます。つまり、別のマシンからでも同じゴールを再開できる可能性があります。
:::

## MultiAgentV2とは何か

今回のアップデートの目玉は「**MultiAgentV2**」です。

### 従来のMultiAgent（V1）

```
メインエージェント → サブエージェント1
                  → サブエージェント2
                  → サブエージェント3
```

問題点：
- スレッド数の制限が曖昧
- サブエージェントの深さ管理が不明確
- 設定の競合でエラー

### MultiAgentV2の改善点

1. **明示的なスレッド上限設定**
2. **待機時間コントロール**
3. **ルート/サブエージェントの明確な区別**
4. **V2専用の深さハンドリング**

```json
{
  "multiagent": {
    "version": "v2",
    "max_threads": 8,
    "wait_timeout_ms": 30000,
    "depth_limit": 3,
    "root_agent_hint": true
  }
}
```

:::note warn
競合する設定を入れると**拒否**されるようになりました。V1では黙って失敗していた問題が解消されています。
:::

## Claude Codeとの比較

| 機能 | Codex CLI | Claude Code |
|------|-----------|-------------|
| ゴール永続化 | ✅ May 2026 | ❌ なし |
| 途中再開 | ✅ pause/resume | ❌ 最初から |
| マルチエージェント | ✅ MultiAgentV2 | ✅ Subagents |
| オフライン保存 | ✅ サーバー同期 | ❌ セッション依存 |
| 価格 | 従量課金 | Max契約が必要 |

## 実際に使ってみた

### ゴールの作成

```bash
$ codex goal create "src/配下の全.jsファイルをTypeScriptに変換"

✅ Goal created: goal_abc123
📝 Subtasks identified:
   1. Analyze existing .js files (42 files found)
   2. Generate .ts files with type annotations
   3. Update imports and exports
   4. Run type check and fix errors

⏳ Estimated completion: ~45 minutes
```

### 30分後に一時停止

```bash
$ codex goal pause

⏸️ Goal paused: goal_abc123
📊 Progress: 67% (28/42 files converted)
💾 State saved to OpenAI servers

Resume anytime with: codex goal resume goal_abc123
```

### 翌朝に再開

```bash
$ codex goal resume goal_abc123

▶️ Resuming goal: goal_abc123
📊 Progress: 67% → Starting from file 29/42
🔄 Context restored from server

[Agent continues working...]
```

## 権限プロファイルの強化

もう一つの大きなアップデートが「**Permission Profiles**」です。

```bash
# サンドボックスプロファイルを選択
codex --profile sandbox-strict

# カレントディレクトリ制御
codex --cwd /path/to/safe/directory
```

ビルトインのデフォルトプロファイルが用意され、「このエージェントには読み取りだけ許可」といった細かい制御が可能になりました。

## 注意点：まだ実験的機能も

以下の機能は**experimental**ステータスです：

- `codex exec-server` サブコマンド
- リモートワークフローのegress websocket transport
- MCPのbearer-tokenフィールド（非表示化）

本番環境での利用は、安定版を待った方が無難です。

## Claude Codeユーザーはどうすべきか

正直に言います。

**今すぐ乗り換える必要はありません。**

理由：
1. Claude Codeの方がコード品質が高い（Opus 4.7のSWE-Bench）
2. MultiAgentV2はまだ発展途上
3. ゴール永続化はClaude Codeにも来る可能性が高い

ただし、**長時間タスクが多い人**は試す価値あり。

## まとめ

- OpenAI Codex CLIに「ゴール永続化」が追加された
- `pause/resume`で中断・再開が可能に
- MultiAgentV2で複数エージェントの制御が明確化
- Claude Codeへのプレッシャーになることは間違いない

AIコーディングエージェント戦争は、まだ始まったばかり。

---

**この記事が参考になったら、いいねとストックをお願いします！**

あなたはClaude Code派？Codex CLI派？コメントで教えてください👇

## 参考リンク

Codex CLI Changelog

https://developers.openai.com/codex/changelog

Codex Updates May 2026 - Releasebot

https://releasebot.io/updates/openai/codex

OpenAI Codex CLI Features

https://developers.openai.com/codex/cli/features

Building Workflows with Codex CLI & Agents SDK

https://cookbook.openai.com/examples/codex/codex_mcp_agents_sdk/building_consistent_workflows_codex_cli_agents_sdk
