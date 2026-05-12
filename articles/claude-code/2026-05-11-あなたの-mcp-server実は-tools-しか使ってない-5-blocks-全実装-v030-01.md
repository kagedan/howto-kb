---
id: "2026-05-11-あなたの-mcp-server実は-tools-しか使ってない-5-blocks-全実装-v030-01"
title: "あなたの MCP server、実は Tools しか使ってない (5 blocks 全実装 / v0.3.0)"
url: "https://zenn.dev/kanseilink/articles/linksee-memory-mcp-five-blocks-20260507"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-11"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

Anthropic と MCP working group が口を揃えて言っていることがある。

> 「公開されている MCP server の **約 99% が Tools しか実装していない**」

MCP には Tools 以外に **Resources / Prompts / Sampling / Roots / Elicitation** という 4 + 1 のブロックがある。 残り 4 + 1 を実装するとエージェント体験が一段変わる。 にもかかわらず、 ほぼ全員が Tools だけ書いて止まっている。

私が運用している [Linksee Memory](https://www.npmjs.com/package/linksee-memory) も v0.2.x までは Tools だけだった。 5月7日に **v0.3.0** を npm publish した。 全 5 blocks + Elicitation を実装し終えた。

この記事は、 **Tools しか実装していない MCP server を持っている人向け** に、 残り 4 + 1 を実装したらどうなるか、 SDK の書き方とつまづきポイントを残す。

## Linksee Memory って何?

知らない人向けに 1 段落で。

Linksee Memory は Claude Code / Cursor / OpenAI Codex / Gemini CLI の **session 跨ぎ記憶喪失** を解決する local-first MCP server。 6-layer 構造化メモリ (goal / context / emotion / implementation / caveat / learning) と、 file diff cache による 50%+ の token 節約を提供する。

各ブロックがエージェント体験を別軸で広げる。

| Block | エージェントから見た価値 |
| --- | --- |
| **Tools** | 関数呼び出し。 サーバーに「やってもらう」 |
| **Resources** | URI でアドレス指定可能なデータ。 IDE の **`@-mention` で参照可能** になる |
| **Prompts** | 再利用可能なプロンプトテンプレート。 ユーザーがコマンドパレットから呼べる |
| **Sampling** | サーバーがクライアントの LLM を呼び返す逆方向のコール。 サーバー側に LLM key を持たずに知能を借りられる |
| **Roots** | クライアントの作業ディレクトリ情報。 サーバーがコンテキストに合わせて挙動を変えられる |
| **Elicitation** (newer) | サーバーがユーザーに structured な質問をする。 破壊的操作の前に確認を取れる |

つまり Tools しか実装していない MCP server は、 サーバー側からエージェントを「呼ばれる側」 にしか位置付けていない。 5 blocks 全部を使うと、 **サーバーが能動的にエージェント体験を作りに行ける**。

## 実装: Resources

Linksee Memory は記憶 (= memories table) を URI 化した。

静的リソース:

* `memory://stats` 全体統計
* `memory://hot` 最近アクセスされたメモリ
* `memory://recent` 直近 7 日のメモリ
* `memory://caveats` 全 caveat 層 (= 「二度と忘れたくない教訓」)

リソーステンプレート (パラメータ付):

* `memory://entity/{name}` 特定のエンティティの全記憶
* `memory://layer/{layer}` 特定のレイヤーの全記憶
* `memory://memory/{id}` 単一の記憶

これで Claude Desktop / Cursor の `@-mention` UI に Linksee Memory のエンティティが表示される。 ユーザーは「`@KanseiLink`」 とタイプするだけで該当エンティティの全記憶を context に流し込める。

SDK の書き方:

```
import {
  ListResourcesRequestSchema,
  ListResourceTemplatesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: STATIC_RESOURCES, // 自分で定義した配列
}));

server.setRequestHandler(ListResourceTemplatesRequestSchema, async () => ({
  resourceTemplates: RESOURCE_TEMPLATES,
}));

server.setRequestHandler(ReadResourceRequestSchema, async (req) => {
  const { uri } = req.params;
  // uri をパースして対応する記憶を取得
  const text = lookupResource(uri);
  return { contents: [{ uri, mimeType: 'application/json', text }] };
});
```

つまづきポイント: `capabilities` 宣言を忘れると ListResourcesRequest が来ない:

```
const server = new Server(
  { name: 'linksee-memory', version: '0.3.0' },
  {
    capabilities: {
      tools: {},
      resources: { subscribe: false, listChanged: false }, // ← これを追加
      prompts: { listChanged: false },
    },
  }
);
```

## 実装: Prompts

5 つのテンプレートを用意した。

| 名前 | 用途 |
| --- | --- |
| `summarize-session` | セッション終了時にトランスクリプトを 6 層構造化メモリに変換 |
| `extract-caveats` | ポストモーテムから「二度とやらない」 教訓を抽出 |
| `weekly-consolidation` | エンティティの直近 1 週間を learning 層 1 件にまとめる |
| `recall-and-write` | 何かを書く前に必ず recall するよう強制する anti-pattern guard |
| `entity-handoff` | 新セッションへの引き継ぎドキュメント生成 |

SDK:

```
import { ListPromptsRequestSchema, GetPromptRequestSchema } from '@modelcontextprotocol/sdk/types.js';

server.setRequestHandler(ListPromptsRequestSchema, async () => ({ prompts: PROMPTS }));

server.setRequestHandler(GetPromptRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;
  return getPrompt(name, args); // 自分で実装、 messages[] を返す
});
```

`getPrompt` は引数を埋めた messages 配列を返すだけ:

```
return {
  description: `Consolidate the last week of memories for ${entityName}.`,
  messages: [
    {
      role: 'user',
      content: { type: 'text', text: `Step 1: recall(...) Step 2: ...` },
    },
  ],
};
```

ユーザーは Claude Desktop / Cursor の **コマンドパレットから直接 Prompts を呼べる**。 「`/summarize-session`」 みたいに。

## 実装: Sampling (server が client LLM を呼ぶ)

ここから先は **server-initiated request** になる。 server が `server.request(...)` でクライアントに投げる方向。

Linksee Memory では `consolidate` ツールに `use_llm: true` フラグを足した。 true のとき:

1. server が rule-based consolidation を実行 (これは元々ある)
2. 各 cluster について **client の LLM に「これを 1 段落に要約して」と依頼**
3. 返ってきたテキストで learning エントリを上書き
4. client が拒否 / 未対応なら heuristic 結果のまま fallback

```
import { CreateMessageRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const result = await server.request(
  {
    method: 'sampling/createMessage',
    params: {
      messages: [{ role: 'user', content: { type: 'text', text: prompt } }],
      maxTokens: 400,
      temperature: 0.2,
      modelPreferences: { speedPriority: 0.7, costPriority: 0.7, intelligencePriority: 0.4 },
    },
  },
  CreateMessageRequestSchema
);
```

**サーバー側に LLM の API キーが要らない**。 これが大きい。 OSS で配る MCP server に「このサーバー使うには Anthropic key 入れて」とは書きたくないが、 sampling なら **クライアントの LLM を借りる** だけなのでサーバーは無認証のまま。

## 実装: Roots (client の作業ディレクトリを読む)

`recall_file` ツールに `scope_to_roots: true` フラグを足した。 true のとき、 client から `roots/list` を取得し、 path match を root 内のファイルに絞る。

```
import { ListRootsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const roots = await server.request(
  { method: 'roots/list', params: {} },
  ListRootsRequestSchema
);
// roots = [{ uri: "file:///C:/Users/HP/linksee-memory", name: "..." }, ...]
```

つまづきポイント: client によっては `roots/list` を実装していない。 その時はエラーで返ってくるので catch して空配列にフォールバック:

```
try {
  const res = await server.request(...);
  return res.roots ?? [];
} catch {
  return []; // 未対応 client は silent skip
}
```

## 実装: Elicitation (newer primitive)

2025-11-25 spec で正式入りした新しいプリミティブ。 server が user に **structured な質問** を投げ、 client UI で回答を受ける。 Linksee Memory では `forget` ツールに `interactive: true` フラグを足した。

```
import { ElicitRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const res = await server.request(
  {
    method: 'elicitation/create',
    params: {
      message: `Forget memory #${id}? Layer: ${layer}, Importance: ${importance}`,
      requestedSchema: {
        type: 'object',
        properties: {
          confirm: { type: 'boolean', title: 'Forget this memory' },
        },
        required: ['confirm'],
      },
    },
  },
  ElicitRequestSchema
);

if (res.action === 'accept' && res.content?.confirm === true) {
  // 削除実行
}
```

破壊的な操作の前にユーザー確認を取れる。 まだ対応している client は少ないが、 対応している client では UX が一段上がる。 未対応 client では silent decline にして graceful degrade。

## Backward compatibility の design

v0.2.x → v0.3.0 でユーザー資産を壊さないために、 **3 つのルール** で設計した。

1. **既存 8 tools の signature は不変**。 v0.2.x で動いていたコードはそのまま動く。
2. **新機能は opt-in flag**。 `use_llm: true` / `scope_to_roots: true` / `interactive: true` を明示的に渡さない限り従来挙動。
3. **DB schema は変更しない**。 マイグレーション不要、 既存ユーザーは npm install するだけ。

これで「v0.3.0 にしたら壊れた」 案件をゼロにする。 OSS で破壊的変更を出すのは信頼の自殺なので、 **scope-lock** で defensible に。

## どこから着手すべきか

もしあなたが Tools しか実装していない MCP server を持っているなら、 着手順序の推奨はこれ。

1. **Resources 最優先**。 IDE の `@-mention` で目に見える形でユーザーに価値が届く。
2. **Prompts 次点**。 すぐ実装でき、 コマンドパレット経由で発見可能。
3. **Sampling は中盤**。 server-initiated なので少し complexity が上がる。
4. **Roots は context-aware が必要なら**。 file 系ツールがある server は意味がある。
5. **Elicitation は newer primitive**。 client 対応待ちなので最後でいい。

Linksee Memory v0.3.0 では 5/7 の 1 セッション (約 4 時間) で全部実装し、 npm publish + git tag + LP 更新まで完走した。 各 block の追加は **平均 200-300 行**、 一気に書くより 1 block ずつ smoke テストを書きながら進めるのが安全。

## まとめ

Linksee Memory v0.3.0 は MCP の 5 blocks 全実装 + Elicitation で、 公開 MCP server の **業界先行 1%** に入った。 v0.2.x からの backward compat も維持。 既存ユーザーは `npm install -g linksee-memory@latest` で透明に上がる。

エージェントメモリの **Pro tier (cross-device sync / team shared memory / web dashboard)** は 2026 夏 launch 予定。 興味があれば LP の waitlist (<https://linksee-site.vercel.app>) から登録してほしい。 早期登録者は v0.3.0 OSS の継続支援込みで $19/mo。

次回は **MCP Apps と Server-side Agent Loop** のはなし (これは未実装、 2025-11-25 spec の新プリミティブ)。 5 blocks の次の地平。
