---
id: "2026-04-17-claude-codeのコスト最適化costだけで終わる話じゃないopus-47時代の完全チートシー-01"
title: "Claude Codeのコスト最適化、/costだけで終わる話じゃない。Opus 4.7時代の完全チートシート"
url: "https://qiita.com/moha0918_/items/b004c2f6070ee1c34d85"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

Opus 4.7が来てから、デフォルトのeffort levelが`xhigh`に変わりました。気づかずに使い続けると、Opus 4.6時代より明らかにトークンを食います。設定の組み合わせを棚卸ししたので、リファレンスとして残しておきます。

## まずはコスト把握の4コマンド

何もしないうちは何も最適化できません。最初に覚えるのはこの4つです。

| コマンド | 用途 | 対象ユーザー |
| --- | --- | --- |
| `/cost` | 現セッションのAPIトークン使用量と推定コスト | API課金ユーザー |
| `/stats` | 使用量パターンの確認 | Claude Max/Pro契約者 |
| `/context` | コンテキスト消費の内訳(MCP・CLAUDE.md・履歴) | 全員 |
| `/status` | 現在のモデルとeffort level | 全員 |

`/cost`の金額はローカル推定です。正確な請求はClaude Consoleの`Usage`ページで確認してください。Claude MaxやProはサブスク内で完結するので、`/stats`の方が有用です。

[statusline機能](https://code.claude.com/docs/en/statusline#context-window-usage)を使えば、コンテキスト使用量を常時表示にしておけます。`/cost`を毎回打つより視認性が高いです。

## effort levelの設定でコストが化ける

Opus 4.7で導入された`xhigh`は、`high`と`max`の間に位置する新しい段階です。Opus 4.7の既定値はこの`xhigh`で、初回起動時には過去の設定すら無視して`xhigh`が適用されます。気づかないうちにトークン消費が跳ねるのはここが原因です。

### 5段階の温度感

| Level | Opus 4.7 | Opus 4.6 / Sonnet 4.6 | 想定用途 |
| --- | --- | --- | --- |
| `low` | 対応 | 対応 | 短い・スコープが狭い・低レイテンシ重視 |
| `medium` | 対応 | 対応 | コスト感度高め、知性とトレードオフ可 |
| `high` | 対応 | 対応 | 知性必要な作業の最低ライン |
| `xhigh` | 既定 | フォールバックでhigh | コーディングとエージェント作業のおすすめ |
| `max` | 対応 | 対応 | 過剰思考のリスクあり、要事前検証 |

上から下に向かって、トークン消費が跳ね上がります。`max`は明示的に「上限なし」で動くので、入れっぱなしは事故のもとです。

### 切り替えの優先順位

設定方法は複数あり、優先度が決まっています。上ほど強いです。

1. 環境変数 `CLAUDE_CODE_EFFORT_LEVEL`
2. Skill / Subagent frontmatter の `effort`
3. `--effort` フラグ(セッション起動時)
4. `/effort` コマンド (対話的スライダー)
5. settings.json の `effortLevel`
6. モデル既定値

SkillやSubagent側で `effort: medium` を仕込んでおくと、その作業中だけトークン節約できます。

```
---
name: simple-formatter
description: Format files only, no logic changes
effort: low
---
```

Opus 4.7は常に適応的推論(adaptive reasoning)で動作し、`MAX_THINKING_TOKENS`や`CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING`は効きません。Opus 4.6 / Sonnet 4.6でしか効かない設定です。

### 一度だけ深く考えさせたいとき

セッション設定を変えずに「この回だけ思考多めで」と指示する裏技があります。プロンプトに `ultrathink` を含めるだけです。effort levelには触らずにその場限りの思考強化が入ります。

## モデル選択早見表

モデルエイリアスを使い分ければ、コストが大きく変わります。

| エイリアス | 解決先(Anthropic API) | 使いどころ |
| --- | --- | --- |
| `opus` | Opus 4.7 | 複雑な設計判断、深い推論 |
| `sonnet` | Sonnet 4.6 | 日常コーディング全般 |
| `haiku` | 最新Haiku | サブエージェント、軽量タスク |
| `opusplan` | Plan時opus、実行時sonnet | 設計と実装で自動切替 |
| `opus[1m]` | Opus 4.7 + 1M context | 巨大コードベース・長セッション |
| `sonnet[1m]` | Sonnet 4.6 + 1M context | 大量コンテキスト読み込み |

`opusplan`は知らないと損する選択肢です。Plan modeでは`opus`が効き、実装フェーズに入ると自動で`sonnet`に降りるので、設計の質を落とさずに実装コストだけ抑えられます。

Max / Team / Enterprise契約なら、Opus 4.7は1M contextが既定でついてきます。Sonnetも `[1m]` サフィックスで切り替え可能ですが、200K超分はextra usage扱いになることがあるので確認しておきます。

## サブエージェント・チーム機能のコスト感

Agent teamsは便利な反面、ドキュメントには「plan mode時で標準セッションの約7倍」と明記されています。各メンバーが独立したコンテキストを持つので当然なのですが、忘れて常用すると効きます。

| 設定 | 効果 |
| --- | --- |
| サブエージェントを `haiku` 固定 | チーム調整タスクのコスト圧縮 |
| 起動プロンプトを最小化 | 各メンバーの初期コンテキスト削減 |
| 使い終わったチームを終了 | アイドル中もトークンを食うので必須 |
| Sonnetでチームメイト構成 | 能力とコストのバランスが良い |

環境変数で常用モデルを固定することもできます。

```
export CLAUDE_CODE_SUBAGENT_MODEL='haiku'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='claude-haiku-4-5-20251001'
```

## コンテキスト圧縮の小技集

以下は `/context` を見ながら必要なものから入れていけば十分です。

| 手法 | 効果の目安 |
| --- | --- |
| `/clear` をタスク切替時に毎回 | 古い履歴の継続消費を停止 |
| `/compact <重視点>` でカスタム要約 | 要約品質を作業に最適化 |
| CLAUDE.md を200行以内に | セッション開始時の固定コスト削減 |
| 詳細手順をSkillに切り出し | 必要時のみオンデマンド読込 |
| MCPサーバーよりCLI(`gh`,`aws`等)優先 | ツール定義のリスティング不要 |
| 不要MCPは `/mcp` で無効化 | 待機中のツール定義削減 |
| Code intelligence plugin導入 | grep連発からシンボル参照へ置換 |
| 冗長な作業をサブエージェント委譲 | 大量出力をメインから隔離 |

### Hooksでコンテキストを事前圧縮する

テストログを丸ごとClaudeに渡すのは典型的な無駄です。PreToolUse hookでgrepしてからClaudeに見せると、数万トークンが数百トークンに化けます。

```
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/filter-test-output.sh"
      }]
    }]
  }
}
```

スクリプト側はテストコマンドを判別してフィルタリングするだけです。

```
#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command')

if [[ "$cmd" =~ ^(npm test|pytest|go test) ]]; then
  filtered="$cmd 2>&1 | grep -A 5 -E '(FAIL|ERROR|error:)' | head -100"
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"allow\",\"updatedInput\":{\"command\":\"$filtered\"}}}"
else
  echo "{}"
fi
```

## チーム導入時のTPM目安

組織レートリミットは小さすぎても大きすぎても困ります。公式の推奨値です。

| チーム規模 | TPM/user | RPM/user |
| --- | --- | --- |
| 1-5 | 200k-300k | 5-7 |
| 5-20 | 100k-150k | 2.5-3.5 |
| 20-50 | 50k-75k | 1.25-1.75 |
| 50-100 | 25k-35k | 0.62-0.87 |
| 100-500 | 15k-20k | 0.37-0.47 |
| 500+ | 10k-15k | 0.25-0.35 |

人数が増えるほど一人あたりの上限を下げて良いのは、同時実行率が下がるからです。組織全体での合算上限なので、個人が一時的に超過しても問題ありません。

## 環境変数でのプロンプトキャッシュ制御

プロンプトキャッシュは既定で有効で、これだけでも効きます。デバッグや特殊環境で切る選択肢があるという情報です。

| 環境変数 | 用途 |
| --- | --- |
| `DISABLE_PROMPT_CACHING` | 全モデルでキャッシュ無効化(優先度最高) |
| `DISABLE_PROMPT_CACHING_OPUS` | Opusのみ無効化 |
| `DISABLE_PROMPT_CACHING_SONNET` | Sonnetのみ無効化 |
| `DISABLE_PROMPT_CACHING_HAIKU` | Haikuのみ無効化 |

通常はいじらない設定ですが、LLMゲートウェイ側でキャッシュ実装が異なる場合に必要になることがあります。

## まとめ

Opus 4.7時代のコスト最適化は、`/effort`と`/cost`の2つを習慣にできるかで決まります。`xhigh`が常に最適とは限らないので、作業の重さに応じて`high`や`medium`に降ろす判断が大事です。`/context`で内訳を見て、`/clear`と`/compact`を躊躇なく使う癖をつければ、月のトークンは目に見えて変わります。
