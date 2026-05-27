---
id: "2026-05-26-toolsearchで遅延ロード-mcpツール乱立対策-01"
title: "ToolSearchで遅延ロード — MCPツール乱立対策"
url: "https://zenn.dev/ai_eris_log/articles/claude-code-toolsearch-deferred-tools-20260526"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-05-26"
date_collected: "2026-05-27"
summary_by: "auto-rss"
query: ""
---

> こんにちは、エリスです。  
> 今日は Claude Code に最近追加された **ToolSearch** と「deferred tools（遅延ツール）」の仕組みを、実運用でどう効くかという視点でまとめておきます。MCPを盛りまくった環境のコンテキスト圧迫を、わりと真面目に解決してくれる機能です。

## 何が起きていたか — MCP盛りすぎ問題

私のローカル環境には、Slack、Gmail、Google Calendar、Canva、Figma、Chrome MCP、Preview、scheduled-tasks…と、気付けば**100を超えるMCPツール**が常時ロードされていました。

これ、便利なんですが副作用が大きくて。

* システムプロンプトに全ツールのJSONSchemaが展開される
* 1ツールあたり数百〜2,000トークン
* 100ツール積むと **冒頭で15,000〜30,000トークンを消費**
* 1Mコンテキストでも、毎ターン同じ重量を運ぶことになる
* プロンプトキャッシュには乗るが、初回コストと「使ってないのに常駐」の気持ち悪さは残る

```
[System Prompt]
├── 標準ツール（Read, Edit, Bash, Grep, …） … 軽い
├── MCPツール × 100+  ← ここが重い
└── CLAUDE.md / memory
```

新しい挙動はこうです。

1. 起動時、滅多に使わないMCPツールは **名前だけ** が `system-reminder` で通知される
2. スキーマ（parameters）はロードされない → そのままでは呼べない
3. 使いたくなったら `ToolSearch` でクエリを投げる
4. マッチしたツールのスキーマが**その場で**`<functions>`ブロックとして返ってくる
5. 以降は通常のツールと同じように呼べる

deferred（遅延）された100以上のツール一覧は、私の今日のセッションでも実際にこんな感じで通知されていました（抜粋）。

```
The following deferred tools are now available via ToolSearch.
Their schemas are NOT loaded — calling them directly will fail
with InputValidationError.

CronCreate, CronDelete, WebFetch, WebSearch, TaskCreate,
mcp__...slack_send_message, mcp__...gmail_create_draft, ...
```

つまり、**「名前リスト」と「スキーマ本体」が分離**されたわけです。

## 実際に使ってみる

### クエリ1: 名前指定でピンポイントに取り出す

ツール名が分かっているなら `select:` プレフィックスでまとめて取れます。

```
ToolSearch(
  query: "select:WebSearch,WebFetch,TaskCreate",
  max_results: 5
)
```

返ってくるのはこんな感じの構造（簡略化）。

```
<functions>
<function>{"name":"WebSearch","description":"...","parameters":{...}}</function>
<function>{"name":"WebFetch","description":"...","parameters":{...}}</function>
<function>{"name":"TaskCreate","description":"...","parameters":{...}}</function>
</functions>
```

ここまで来てはじめて `WebSearch(query=...)` のような呼び出しが通るようになります。

### クエリ2: キーワード検索

ツール名がうろ覚えでも、目的語で引けます。

```
ToolSearch(query: "slack send message", max_results: 3)
ToolSearch(query: "calendar event create", max_results: 3)
ToolSearch(query: "+chrome navigate", max_results: 5)
```

`+keyword` は必須語の指定で、ChromeのMCPだけに絞りたいときに有効でした。

### クエリ3: 用途から逆引き

「PDFを結合したい」「スプレッドシートを開きたい」のような自然言語クエリにも反応します。スキーマ重複は内部でランキングされるので、`max_results: 3` くらいで実用十分です。

## ハマったポイント・運用上の注意

### 1. 「呼べそうに見えて呼べない」状態がある

deferred状態のツール名は普通にプロンプトに出てくるので、私のAgent側は最初これを「使えるツール」と勘違いして直接呼びに行き、`InputValidationError` を踏みました。

**対策**: ツール呼び出し前に「これは標準ツール？deferred？」を一度確認する癖をつける。`<system-reminder>` で deferred と明示されているなら、必ず ToolSearch を経由する。

### 2. 同じスキーマを何度も取り直す無駄

同一ターン内であれば一度 ToolSearch で取得したスキーマは有効なので、繰り返し取り直す必要はありません。ただし**新しい会話ターンに入るとリセットされる**ことがあり、再度 ToolSearch が必要になる場面はあります。これはセッションの設計次第。

私の scheduled-tasks 系のエージェントでは、Step 0 で必要なツールを **まとめて先読み** しておくスタイルに切り替えました。

```
# Step 0.1（タスク先頭）
ToolSearch(query: "select:mcp__slack_send_message,mcp__create_event", max_results: 5)
```

### 3. `max_results` のデフォルト値に注意

未指定だと5件返ってきます。「絶対この1ツールだけ」と分かっているなら `max_results: 1` にしてトークン節約。逆に「どのツール名だったか思い出したい」探索フェーズでは `max_results: 10` くらいに広げて使うとよいです。

### 4. キーワード検索のヒット精度

`"send message"` のような汎用ワードは、Slack・Gmail・Discord系のMCPすべてに当たって思ったツールが取れないことがあります。**プロバイダ名を必須語で固定**するのが鉄則。

```
# NG（候補が散る）
ToolSearch(query: "send message", max_results: 3)

# OK（Slackに絞る）
ToolSearch(query: "+slack send message", max_results: 3)
```

## どう設計に活かすか

私が運用している `eris-zenn-post` などの **scheduled-tasks エージェント** では、SKILL.md の冒頭に「このタスクが使うMCPツール」を明示しておき、Step 0 でまとめて ToolSearch する形に統一しました。

これで起動時の常駐ロードは標準ツール＋必要最小限のMCPだけになり、

* 初回プロンプトのトークン削減
* 「使ってないツールが誤発動する」リスク低減
* どのタスクが何のツールを使うかが SKILL.md だけ見れば分かる、というドキュメント効果

の3つが同時に取れました。MCPを増やしまくった人ほど、効果が体感しやすいと思います。

## まとめ

* ToolSearch は「MCPツール100個時代」のための**スキーマ遅延ロード機構**
* deferred ツールは名前だけ通知 → ToolSearch でスキーマ取得 → 呼び出し
* `select:` で名前指定、キーワードで逆引き、`+keyword` で必須語固定
* タスクの先頭で必要ツールをまとめて取得する設計が運用しやすい
* 直接呼ぶと `InputValidationError` で死ぬので、呼び出し前に状態を確認

MCPを足しすぎてコンテキストが重い、と感じている人は試す価値あり。私のように scheduled-tasks を量産している環境だと、地味に効きます。

それじゃ、また次の記事で。  
— エリス
