---
id: "2026-07-08-claude-codeのリクエストログを実測systemmessagestoolsの内訳とトークン配-01"
title: "Claude Codeのリクエストログを実測——system/messages/toolsの内訳とトークン配分"
url: "https://qiita.com/eiji-noguchi/items/7678fdaca837ba6e176a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

# 目的

Claude CodeはClaudeモデル専用ではなく、Anthropic Messages API互換のエンドポイントを向き先にすることで、**ローカルLLM（Ollama等）をバックエンドにしたユーザーインターフェース**として使うこともできます。

そこで自分のOllama環境にClaude Codeを繋いで、チャットで単純に

```
1+1は？
```

と聞いてみたのですが、**やけにトークンの消費量が多い**ことに気づきました。
たった5文字しか入力していないのに、レスポンス側の`usage`を見ると`input_tokens`が2万を超えていたのです。

本記事では、実際にOllama側へ送られた**リクエストボディ（JSON）**と**レスポンス（SSEストリーム）**のログを解析し、Claude Codeが裏側で何を送っているのか、トークンの内訳を実測してみます。

# 前提

- WSL2 (Ubuntu) 環境
- Claude Code インストール済み
- モデルの向き先をOllama（[`laguna-xs-2.1:latest`](https://ollama.com/library/laguna-xs-2.1)）にリバースプロキシ経由で向けている
- プロキシ側で、Claude Codeから送られるリクエストと、Ollamaから返るレスポンス（SSE形式）のそれぞれログを正とする

# ログファイルの構造

まず、採取した2種類のファイルが何を表しているかを整理します。

| タイプ | 役割 |
| --- | --- |
| リクエスト | Claude Code → ローカルLLMへの**リクエスト**。<br>`model`・`messages`・`system`・`tools`などを含む |
| レスポンス | ローカルLLMからの**レスポンス**。Anthropic APIのストリーミングイベント形式（`message_start`→`content_block_delta`→`message_stop`）で、<br>`thinking`（思考過程）と`text`（回答本文）が細切れに入っている |


# 「1+1は？」だけで何トークン使われているか

`CLAUDE.md`には以下の1文だけを設定した状態で検証しました。

```markdown:CLAUDE.md
計算をする際は回答だけでなく、その過程も述べるように。
```

この状態で「1+1は？」と聞いたときのトークン量は以下の通りです。
なお、MCP、Skillは有効になっており、MCPサーバー（[`aws-knowledge`](https://github.com/awslabs/mcp/tree/main/src/aws-knowledge-mcp-server)）をはじめ、いくつか既に設定済みとなります。

```
❯ 1+1は？

  Thought for 3m 4s

計算の過程を述べますね。

問題: 1 + 1 = ?

計算のプロセス:
1. 最初の数である「1」を把握します
2. 次に加える数の「1」を考えます
3. 2つの「1」を合わせると、1つ目の1に1つ目の足し算としてカウントするだけで「2」になります

答え: 1 + 1 = 2
```

| input_tokens | output_tokens |
| --- | --- |
| 約29,700 | 153 |

ユーザーが入力した文字はわずか5文字ですが、**その裏で3万トークン近くが動いている**ことが確認できました。この内訳を、リクエストJSONの構造に沿って分解していきます。

# リクエストJSONの構造

トークンの内訳を見る前に、リクエストJSON自体の階層構造を確認しておきます。トップレベルは以下の10個のキーで構成されていました。

```json
{
  "model": "laguna-xs-2.1:latest",
  "messages": [...],
  "system": [...],
  "tools": [...],
  "metadata": {...},
  "max_tokens": 32000,
  "thinking": {...},
  "context_management": {...},
  "output_config": {...},
  "stream": true
}
```

| キー | 内容 | トークン影響 |
| --- | --- | --- |
| `model` | 向き先のモデル名（今回は`laguna-xs-2.1:latest`） | 小 |
| `messages` | ユーザー発言・システムリマインダー（CLAUDE.mdやエージェント/Skill一覧）・会話履歴 | 大 |
| `system` | Claude Codeのシステムプロンプト本体（ハーネスの振る舞い、環境情報など） | 大 |
| `tools` | 利用可能な全ツールのJSON Schema定義 | 大 |
| `metadata` | `user_id`（device_id・session_id等を含むJSON文字列） | 小 |
| `max_tokens` | 出力の最大トークン数（32000） | 小 |
| `thinking` | 拡張思考の設定（`{"type": "adaptive"}`） | 小 |
| `context_management` | コンテキスト管理の設定（古い思考ブロックの扱いなど） | 小 |
| `output_config` | 推論のeffortレベル（`{"effort": "xhigh"}`など） | 小 |
| `stream` | ストリーミング有無（`true`） | 小 |

このうち`metadata`・`max_tokens`・`thinking`・`context_management`・`output_config`・`stream`は、値自体は短い設定値なのでトークンへの影響はごくわずかでした。
**トークン消費の実体は`messages`・`system`・`tools`の3つに集約される**ため、以降はこの3つを掘り下げます。

## `messages` の中身

`messages`は配列で、今回のリクエストでは2件のメッセージが入っていました。

```json
"messages": [
  {
    "role": "user",
    "content": [
      { "type": "text", "text": "<system-reminder>...CLAUDE.mdの内容...</system-reminder>" },
      { "type": "text", "text": "1+1は？", "cache_control": { "type": "ephemeral" } }
    ]
  },
  {
    "role": "system",
    "content": "Available agent types for the Agent tool:\n- claude: ...\n\nThe following skills are available...\n- grill-me: ...\n"
  }
]
```

| 階層 | 内容 |
| --- | --- |
| `messages[0].role` | `"user"` |
| `messages[0].content[0].text` | `<system-reminder>`でラップされたCLAUDE.mdの内容 |
| `messages[0].content[1].text` | 実際のユーザー発言「1+1は？」（ここに`cache_control`が付く） |
| `messages[1].role` | `"system"` |
| `messages[1].content` | 文字列そのもの。**エージェント一覧＋Skill一覧がまとめて1本の長文で入っている** |

`messages[0].content[1]`が本来のユーザー入力ですが、わずか5文字です。
一方`messages[1].content`は前後にエージェント一覧やSkill一覧を含む長大な1本の文字列になっており、後述するSkillのコストはすべてここに乗っています。

:::note info
`CLAUDE.md`が膨大だとそれだけで多くのトークン量が消費されるため、注意が必要です。
:::

## `system` の中身

`system`も配列で、今回は3要素でした。

```json
"system": [
  { "type": "text", "text": "x-anthropic-billing-header: cc_version=...;" },
  { "type": "text", "text": "You are Claude Code, Anthropic's official CLI for Claude.", "cache_control": {...} },
  { "type": "text", "text": "\nYou are an interactive agent...(ハーネスの振る舞い、環境情報など)", "cache_control": {...} }
]
```

| 階層 | 内容 |
| --- | --- |
| `system[0].text` | Billing用のヘッダー情報（`cc_version`等） |
| `system[1].text` | 1行の自己紹介（"You are Claude Code..."） |
| `system[2].text` | ハーネスの振る舞い・環境情報・メモリの指示等を含む本体（3要素中最大） |

システムプロンプトとして、ハーネスの振る舞いなどを定義しており、テキスト量も一定増加しています。

## `tools` の中身

`tools`は配列で、1要素が1つのツールに対応します。

```json
"tools": [
  {
    "name": "Agent",
    "description": "Launch a new agent to handle complex, multi-step tasks...",
    "input_schema": {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "type": "object",
      "properties": {
        "description": { "description": "A short (3-5 word) description of the task", "type": "string" },
        "prompt": { "description": "The task for the agent to perform", "type": "string" },
        "subagent_type": { "description": "...", "type": "string" }
      }
    }
  },
  ...
]
```

| 階層 | 内容 |
| --- | --- |
| `tools[n].name` | ツール名（`Agent`、`Bash`、`Skill`、`mcp__aws-knowledge__...`など） |
| `tools[n].description` | ツールの使い方の説明文。<br>**ここが長いツールほどトークンを消費する**（例: `Workflow`は説明文だけで2万文字超） |
| `tools[n].input_schema` | パラメータのJSON Schema定義（`properties`配下に各パラメータの`type`・`description`が並ぶ） |

独自に導入したMCPツール（`mcp__aws-knowledge__aws___get_regional_availability`など）もこの`tools`配列に**Claude Code組み込みのツールと全く同じ形式**で並んで入ってきます。
つまりMCPサーバーを繋ぐと、そのサーバーが提供するツールの数だけ`tools[n]`の要素が増える、ということになります。。


:::note info
`tools`配列——つまりツール定義そのもの——が全体の9割近くを占めており
使わないツールは無効化することでトークン消費を抑えることができます。
:::

### 補足: MCPを有効化すると何が増えるか

続いて、`aws-knowledge`（私が追加したMCPサーバー）と`plugin:aws-core:aws-mcp`（Built-in MCP）を有効化した状態で、同じ「1+1は？」を送り、リクエストログを再取得しました。

`tools`配列を有効化前後で比較すると、以下の8個が新たに追加されていました。

| 追加されたツール | 文字数 | 推定トークン |
| --- | --- | --- |
| `WaitForMcpServers` | 881 | 210 |
| `mcp__aws-knowledge__aws___get_regional_availability` | 2,286 | 544 |
| `mcp__aws-knowledge__aws___list_regions` | 174 | 41 |
| `mcp__aws-knowledge__aws___read_documentation` | 2,468 | 588 |
| `mcp__aws-knowledge__aws___retrieve_skill` | 741 | 176 |
| `mcp__aws-knowledge__aws___search_documentation` | 1,738 | 414 |
| `mcp__ide__executeCode` | 667 | 159 |
| `mcp__ide__getDiagnostics` | 365 | 87 |
| **合計** | **9,320** | **約2,219** |

Skill有効時と合わせた最終的な`tools`配列は39個・109,895文字（約26,165トークン）となり、Skill無効時の31個・100,221文字（約23,862トークン）から、**約9,700文字（約2,300トークン）増加**しました。

# Skillは何トークンを占めているか

自分のClaude Code環境には[`grill-me`](https://github.com/mattpocock/skills)などのSkillが有効化されています。
Skillそのものはユーザーが明示的に呼び出す機能ですが、**呼び出していなくても、有効な全Skillの説明文が毎リクエストに乗ります**。
これはClaude Codeが「どのSkillを使うべきか」をターンごとに判断するため、カタログ全体を渡す必要があるためです。

ログ上では、この一覧は`messages`配列の`role: "system"`のメッセージ内に、エージェント一覧に続けて列挙されていました。

```
The following skills are available for use with the Skill tool:

- grill-me: Interview the user relentlessly about a plan or design...
- deep-research: Deep research harness — fan-out web searches...
- document-skills:xlsx: ...
- aws-core:amazon-bedrock: ...
- aws-core:aws-cdk: ...
（以下、有効な全Skillが続く）
```

自分の環境では`grill-me`以外にも、document-skills系・example-skills系・aws-core系など多数のSkillが同時に有効になっており、このセクション全体で**約8,700〜8,900文字（約2,000〜2,100トークン）** を占めていました。

:::note info
tools同様、使わないSkillは無効化することでトークン消費を抑えることができます。
:::


# 全体の内訳まとめ

`1+1は？` というリクエストだけでも、全体（`system` + `messages` + `tools`）の文字数を比較すると次のようになります（MCP, Skillはどちらも有効）。

| 状態 | 合計文字数 | 推定トークン |
| --- | --- | --- |
| MCP, Skill 有効 | 125,456 | 約29,870 |

この値は、**MCPツール定義やSkillの追加分やがそのままトークン消費として上乗せされている**状態となります。

:::note info
**Hooksの影響について（今回は未検証）**
今回は`hooks`を設定していなかったため実測はしていませんが、Skill/MCPとは少し性質が異なるので注釈だけ残しておきます。SkillやMCPは「有効化した時点で」ツールやカタログが`tools`配列・`messages`配列に常時乗り続けるのに対し、Hooksは`settings.json`に設定しておくだけならリクエストJSONの構造（`tools`配列など）には何も追加されません。トークンに乗ってくるのは、**Hookが発火して、その出力がClaudeへのコンテキストとして注入される場合のみ**です（`PreToolUse`のブロック理由、`PostToolUse`の追加コンテキスト、`UserPromptSubmit`の出力、`SessionStart`の注入内容など）。単に外部コマンドを実行するだけで応答をClaudeに返さないタイプのHook（例: Windows通知を飛ばすだけの`Stop`/`Notification`フック）であれば、トークン消費はほぼゼロのはずです。つまりHooksのコストは「常時固定のオーバーヘッド」ではなく「発火時・注入内容次第の可変コスト」という点が、Skill/MCPとの大きな違いです。
:::

# まとめ

| 影響度 | 要素 | 目安 |
| --- | --- | --- |
| 大 | `tools`配列（ツール定義全体） | 全体の約87%、2万トークン超 |
| 中 | Skillカタログ（有効な全Skillの説明文） | 約2,000トークン |
| 中 | MCPツール定義（サーバー1つ増えるごとに数百〜数千） | 約2,200トークン（aws-knowledge分のみ） |
| 小 | CLAUDE.md | 1,000トークン未満 |

※繰り返しますが、**ユーザーの使い方によってはこの数値が跳ね上がります。**

「1+1は？」のような単純な質問でも、実際に払っているコストの大半は**ユーザーの発言ではなく、Claude Codeが毎ターン送るツール定義とSkill/MCPのカタログ**でした。
ローカルLLMでコストやレイテンシを気にする場合、以下が効果的な対策になりそうです。

- 使わないSkillを無効化する（特にaws-core系のような、まとめて多数入っているカテゴリ）
- 使わないMCPサーバーは繋がない、あるいは接続数を絞る
- （Claude API本家であれば）`cache_control`によるプロンプトキャッシュを活用する。ただし今回検証したOllama向けのレスポンスには`cache_read_input_tokens`等のフィールドが存在せず、キャッシュ機構が機能している形跡はありませんでした

ローカルLLM運用ではAPIコストは気にならないかもしれませんが、**推論速度（レイテンシ）やコンテキスト長の制約には直結する**ため、この「見えないオーバーヘッド」を把握しておくことは意味があると感じました。
