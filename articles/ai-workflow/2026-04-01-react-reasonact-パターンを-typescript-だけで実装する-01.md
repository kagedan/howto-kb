---
id: "2026-04-01-react-reasonact-パターンを-typescript-だけで実装する-01"
title: "ReAct (Reason+Act) パターンを TypeScript だけで実装する"
url: "https://zenn.dev/kt3k/articles/74785af8436b1e"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "TypeScript", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

この記事では AI Agent の代表的な実装パターンの1つである ReAct (Reason+Act) を TypeScript  
を使って実装してみます。

ReAct パターンは多くの場合、LangChain、Mastra  
などのフレームワーク経由で使われますが「実際に中で何が起きているのか」はブラックボックスになりがちです。

この記事では、フレームワークを一切使わずに、 TypeScript だけで ReAct  
エージェントをゼロから実装し、その仕組みを理解します。

## ReAct パターンとは

ReAct は LLM  
が「考える(Reason)」と「行動する(Act)」ステップを交互にくり返すことで、段階的に問題を解決してゆくパターンです。

より具体的には、以下のようなステップを繰り返します。

* 考える (Reason)
* 行動 (Action)
  + ツールを呼び出す（検索、DBクエリ、API呼び出しなど）
* 観察 (Observation)

この「Reason -> Action ->  
Observation」のループを繰り返し、十分な情報が揃った時点で最終的な *Answer*  
を出力します。

## サンプルエージェントの仕様

このサンプルでは npm package の選定を行うエージェントを作成してみます。

エージェントは以下の2つのツールを使えるとします

* search
* get\_info
  + パッケージの description、バージョン、ライセンスなどの詳細情報を取得する

エージェントのゴールは、与えられた要件に対して最適な npm パッケージを選定し、  
その理由とトレードオフを含めて説明することです。

(Note: なるべく LLM に get\_info  
ツールも使って欲しいので、最終レポートにおすすめパッケージのバージョン番号を含めるというルールも追加しています。)

## コード

```
// 例として OpenAI SDK を使用
import OpenAI from "openai"
const client = new OpenAI()

// コマンド引数から目標とするパッケージの要件を取得
const goal = process.argv.slice(2).join(" ")

if (!goal) {
  console.log(`Usage: node --env-file=.env main.ts <npm package description...>

  Example:
    node --env-file=.env main.ts best date time package for frontend dev
    deno --env -NE main.ts best date time package for frontend dev`)
  process.exit()
}
console.log("Package requirement:", goal)

/** LLM 呼び出し */
async function generate(input: string) {
  const res = await client.responses.create({ model: "gpt-5.4-mini", input })
  return res.output_text
}

// システムプロンプト、LLM に対して ReAct パターンのルールを説明
const SYSTEM_PROMPT = `
# General rule
You are a npm package selection agent.

Your job is to choose the best npm package for the user's requirements.
- Collect missing information using tools
- Call one tool each time
- Observe the result
- Continue until you can make a recommendation

Rules:
- Prefer actively maintained packages
- Prefer packages with healthy adoption (many downloads)
- Prefer packages with clear TypeScript support
- Mention tradeoffs, not only the winner

Output format:
Thought: ...
Act: {"tool":"toolName","arg":"string"}

Available tools:
- search: search npm registry
  - example: {"tool":"search","arg":"query string"}
  - Note: npm search only support search by main topic
    - good search arg: "date", "markdown", "http client"
    - bad search arg: "npm date time library frontend TypeScript popular maintained"
- get_info: get package info including
  - example: {"tool":"get_info","arg":"package-name"}
  - the correct version number can be only obtained by this tool

Or, when finished:
Answer: {
  "recommended": "...",
  "latestVersion": "x.y.z",
  "license": "license name",
  "alternatives": ["..."],
  "reasons": ["..."],
  "tradeoffs": ["..."]
}

# User requirements
${goal}

# Steps
`

type Action =
  | { tool: "search"; arg: string }
  | { tool: "get_info"; arg: string }

type StepResult =
  | { answer: string }
  | { thought: string; act: Action }

// search ツール
async function searchTool(query: string) {
  const res = await fetch(
    "https://api.npmjs.org/search?text=" + query + "&size=100",
  )
  const { objects } = await res.json()
  return objects.map((o: any) => ({
    downloads: o.downloads.weekly,
    dependents: o.dependents,
    name: o.package.name,
  }))
}

// get_info ツール
async function getInfoTool(pkg: string) {
  const res = await fetch("https://registry.npmjs.org/" + pkg)
  const info = await res.json()
  return {
    name: info.name,
    description: info.description,
    license: info.license,
    readme: info.readme?.slice(0, 3000),
    latestVersion: info?.["dist-tags"]?.latest,
  }
}

// LLM の出力をパース
function parse(text: string): StepResult {
  const answer = text.match(/(?<=Answer:).*$/s)
  if (answer) {
    try {
      return { answer: JSON.parse(answer[0]) }
    } catch {
      throw new Error("Cannot parse LLM answer: " + text)
    }
  }
  const thought = text.match(/(?<=Thought:).*?(?=Act:)/s)
  if (!thought) {
    throw new Error("Cannot parse LLM thought: " + text)
  }
  const actText = text.match(/(?<=Act:).*$/s)
  if (!actText) {
    throw new Error("Cannot parse LLM action: " + text)
  }
  let act: Action
  try {
    act = JSON.parse(actText[0])
  } catch {
    throw new Error("Cannot parse LLM action: " + text)
  }
  return {
    thought: thought[0].trim(),
    act,
  }
}

const messages = [SYSTEM_PROMPT]

// 最大ループ数
const MAX_ATTEMPT = 10

for (let i = 0; i < MAX_ATTEMPT; i++) {
  const result = parse(await generate(messages.join("\n")))

  if ("answer" in result) {
    // 答えが出ているので終了
    console.log("Answer:", result.answer)
    break
  }
  const { thought, act } = result
  console.log("Thought:", thought)
  console.log("Act:", act)

  // コンテキストに Thought と Act を追加
  messages.push("Thought: " + thought, "Act: " + JSON.stringify(act))

  // ツール実行
  let observation: string
  switch (act.tool) {
    case "search": {
      observation = JSON.stringify(await searchTool(act.arg))
      break
    }
    case "get_info": {
      observation = JSON.stringify(await getInfoTool(act.arg))
      break
    }
    default:
      act satisfies never
      throw new Error("Unknown tool " + JSON.stringify(act))
  }

  // コンテキストにツール実行結果を追加
  console.log("Observation: ", observation!.slice(0, 100) + "...")
  messages.push("Observation: " + observation)
}
```

## 解説

### LLM 呼び出し

```
import OpenAI from "openai"
const client = new OpenAI()
/** LLM 呼び出し */
async function generate(input: string) {
  const res = await client.responses.create({ model: "gpt-5.4-mini", input })
  return res.output_text
}
```

この generate 関数で、LLM (ここでは OpenAI の gpt-5.4-mini)  
にプロンプトを投げて結果を取得しています。

なお、`new OpenAI()` の実行では暗黙的に `OPENAI_API_KEY`  
環境変数が読み込まれています。上をそのまま実行するには、ダッシュボードで作成した  
OpenAI の API キーをセットしてください。

### 目標受け取り

```
const goal = process.argv.slice(2).join(" ")
console.log("Package requirement:", goal)
```

CLI の引数から目的パッケージの要件を受け取っています。

```
node --env-file=.env main.ts best date time package for frontend
```

のように実行すると、`best date time package for frontend`  
が目標のパッケージになります。

### システムプロンプト

ReAct のコアとなるルールをプロンプトとして表しています。

```
# General rule

You are a npm package selection agent.

Your job is to choose the best npm package for the user's requirements.

- Collect missing information using tools
- Call one tool each time
- Observe the result
- Continue until you can make a recommendation
```

Agent の目的と、ReAct のループの概要を LLM  
に対して説明しています。ここの表現次第で、ツールの呼び出し方の傾向が変わります。(このあたりの表現の影響はモデルによっても変わるため、より良い結果を得るためには、モデル  
x プロンプトの組み合わせごとにチューニングが必要そうでした)

```
Rules:
- Prefer actively maintained packages
- Prefer packages with healthy adoption (many downloads)
- Prefer packages with clear TypeScript support
- Mention tradeoffs, not only the winner
```

選定の観点を説明しています。

```
Output format:
Thought: ...
Act: {"tool":"toolName","arg":"string"}

Available tools:
- search: search npm registry
  - example: {"tool":"search","arg":"query string"}
  - Note: npm search only support search by main topic
    - good search arg: "date", "markdown", "http client"
    - bad search arg: "npm date time library frontend TypeScript popular
      maintained"
- get_info: get package info including
  - example: {"tool":"get_info","arg":"package-name"}
  - the correct version number can be only obtained by this tool

Or, when finished:
Answer: {
  "recommended": "...",
  "latestVersion": "x.y.z",
  "license": "license name",
  "alternatives": ["..."], "reasons": ["..."],
  "tradeoffs": ["..."]
}
```

アウトプットのフォーマットと、ツールの定義をしています。この辺りの定義をうまく書かないと、LLM  
が思ったようなツールの使い方をしてくれず、予想した結果が得られなかったりしました  
(余談: gpt-5.4-nano だと、search  
ツールの検索語の制約が伝わらず、長すぎる検索クエリーを発行してしまい、うまく検索することが難しいようでした。)

```
# User requirements

${goal}

# Steps
```

ユーザーの入力を目標として埋め込んで、最後にここから ReAct  
のステップが始まることを示すトリガーを置いています。

```
type Action =
  | { tool: "search"; arg: string }
  | { tool: "get_info"; arg: string }

type StepResult =
  | { answer: string }
  | { thought: string; act: Action }

async function searchTool(query: string) {
  const res = await fetch(
    "https://api.npmjs.org/search?text=" + query + "&size=100",
  )
  const { objects } = await res.json()
  return objects.map((o: any) => ({
    downloads: o.downloads.weekly,
    dependents: o.dependents,
    name: o.package.name,
  }))
}

async function getInfoTool(pkg: string) {
  const res = await fetch("https://registry.npmjs.org/" + pkg)
  const info = await res.json()
  return {
    name: info.name,
    description: info.description,
    license: info.license,
    readme: info.readme?.slice(0, 3000),
    latestVersion: info?.["dist-tags"]?.latest,
  }
}
```

LLM に実行させる Tool を実装しています。npm の search API  
と、個別パッケージの取得 API を使っています。

なるべく複数ツールを使わせたいため、search API レスポンスの一部分だけを LLM  
に渡して、search ツールだけでは情報が足りないようにしています。

### LLM の出力のパース

```
function parse(text: string): StepResult {
  const answer = text.match(/(?<=Answer:).*$/s)
  if (answer) {
    try {
      return { answer: JSON.parse(answer[0]) }
    } catch {
      throw new Error("Cannot parse LLM answer: " + text)
    }
  }
  const thought = text.match(/(?<=Thought:).*?(?=Act:)/s)
  if (!thought) {
    throw new Error("Cannot parse LLM thought: " + text)
  }
  const actText = text.match(/(?<=Act:).*$/s)
  if (!actText) {
    throw new Error("Cannot parse LLM action: " + text)
  }
  let act: Action
  try {
    act = JSON.parse(actText[0])
  } catch {
    throw new Error("Cannot parse LLM action: " + text)
  }
  return {
    thought: thought[0].trim(),
    act,
  }
}
```

LLM が返してきた

```
Thought: 考え
Act: アクションのJSON
```

もしくは

という部分をパースしています。gpt-5.4 / gpt-5.4-mini  
などのモデルだと大体上のコード(単純な正規表現)でパースできるようでした。gpt-5.4-nano  
だと Thought: を2連続で出してきたり、Act:  
が無い出力をして来たり、パースできないケースが増える印象がありました  
(使うモデルによってはプロンプトとパーサーのチューニングがさらに必要かもしれません)

### メインループ

```
const messages = [SYSTEM_PROMPT]

// 最大ループ数
const MAX_ATTEMPT = 10

for (let i = 0; i < MAX_ATTEMPT; i++) {
  const result = parse(await generate(messages.join("\n")))

  if ("answer" in result) {
    console.log("Answer:", result.answer)
    break
  }
  const { thought, act } = result
  console.log("Thought:", thought)
  console.log("Act:", act)

  messages.push("Thought: " + thought, "Act: " + JSON.stringify(act))

  let observation: string
  switch (act.tool) {
    case "search": {
      observation = JSON.stringify(await searchTool(act.arg))
      break
    }
    case "get_info": {
      observation = JSON.stringify(await getInfoTool(act.arg))
      break
    }
    default:
      act satisfies never
      throw new Error("Unknown tool " + JSON.stringify(act))
  }
  console.log("Observation: ", observation!.slice(0, 100) + "...")
  messages.push("Observation: " + observation)
}
```

メインのループです。

`messages` 配列に、システムプロンプト、Thought, Act, Observation  
の繰り返しを入れながら LLM に次々プロンプトを投げて、続きを考えさせています。

(これまでの Thought / Act / Observation をすべてプロンプトに含めることで、  
疑似的に状態を持たせています)

LLM が `Answer:`  
の行を返してくるか、規定のループ回数(10)に達するとループを抜けます。

## 実行例

(モデルは `gpt-5.4-mini` を使っています)

### `lightweight date time library`

```
$ node --env-file=.env main.ts lightweight date time library
Package requirement: lightweight date time library
Thought: I’ll search for lightweight date/time libraries in npm, then inspect the leading candidates for maintenance, TypeScript support, and package health.
Act: { tool: 'search', arg: 'date time library' }
Observation:  [{"downloads":43487863,"dependents":"24204","name":"dayjs"},{"downloads":3575,"dependents":"1","name...
Thought: Day.js and date-fns are the obvious top candidates. Since the user asked for a lightweight date/time library, I’ll inspect both to compare current version, license, and TypeScript support.
Act: { tool: 'get_info', arg: 'dayjs' }
Observation:  {"name":"dayjs","description":"2KB immutable date time library alternative to Moment.js with the sam...
Answer: {
  recommended: 'dayjs',
  latestVersion: '1.11.20',
  license: 'MIT',
  alternatives: [ 'date-fns', '@js-joda/core' ],
  reasons: [
    'Very lightweight: Day.js advertises a ~2KB core and is designed as a minimal date/time library.',
    'Excellent adoption: it has very high npm downloads and a large number of dependents, suggesting healthy usage.',
    'Clear TypeScript support and modern DX are widely available in the ecosystem.',
    'Actively maintained and widely trusted as a Moment.js-style replacement.',
    'MIT licensed.'
  ],
  tradeoffs: [
    'Day.js is plugin-based, so some advanced features require extra packages/plugins.',
    'If you prefer a more functional, immutable utility style with a richer standalone function set, date-fns may be a better fit.',
    'If you need strict temporal modeling and heavier date/time correctness guarantees, @js-joda/core is more rigorous but less lightweight and less popular.'
  ]
}
```

dayjs が選定されています。`search` ツールが `date time library`  
と言うクエリーで呼ばれています。dayjs  
のバージョンとライセンス情報取得のために、`get_info` ツールが `dayjs`  
に対して呼ばれています。

### `cross runtime web framework`

```
$ deno --env -NE main.ts cross runtime web framework
Package requirement: cross runtime web framework
Thought: I should search for cross-runtime web frameworks on npm to find actively maintained, well-adopted options with TypeScript support.
Act: { tool: "search", arg: "web framework" }
Observation:  [{"downloads":96246348,"dependents":"101499","name":"express"},{"downloads":35812002,"dependents":"2...
Thought: Hono appears to be a strong cross-runtime web framework candidate; I should inspect its package info to confirm latest version, license, and TypeScript support details before recommending.
Act: { tool: "get_info", arg: "hono" }
Observation:  {"name":"hono","description":"Web framework built on Web Standards","license":"MIT","readme":"<div a...
Answer: {
  recommended: "hono",
  latestVersion: "4.12.9",
  license: "MIT",
  alternatives: [ "fastify", "express", "@nestjs/core" ],
  reasons: [
    "Built specifically for cross-runtime use: Cloudflare Workers, Deno, Bun, Node.js, AWS Lambda, and more.",
    "Strong TypeScript support with first-class types.",
    "Very healthy adoption and active maintenance.",
    "Web-standards-based API makes portability easier across runtimes.",
    "Small and fast, with zero dependencies."
  ],
  tradeoffs: [
    "Smaller ecosystem than Express and often less enterprise-oriented than NestJS.",
    "If you want a traditional Node-only server framework with many plugins, Fastify may be a better fit.",
    "If you need the broadest legacy middleware compatibility, Express still wins, but it is not cross-runtime focused."
  ]
}
```

クロスランタイムな web framework として Hono が選ばれています。

### `best cli parser`

```
$ bun main.ts best cli parser    
Package requirement: best cli parser
Thought: I’ll identify the leading CLI parser packages first, then inspect the top candidates’ maintenance, downloads, TypeScript support, and latest versions before recommending one.
Act: {
  tool: "search",
  arg: "cli parser",
}
Observation:  [{"downloads":158440,"dependents":"7","name":"peowly"},{"downloads":8203,"dependents":"5","name":"zo...
Thought: I found several relevant CLI parser candidates; the strongest likely are yargs-parser, mri, and the broader yargs/oclif ecosystem. I’ll inspect the top likely choices for maintenance, version, license, and TypeScript support before recommending one.
Act: {
  tool: "get_info",
  arg: "yargs-parser",
}
Observation:  {"name":"yargs-parser","description":"the mighty option parser used by yargs","license":"ISC","readm...
Answer: {
  recommended: "yargs-parser",
  latestVersion: "22.0.0",
  license: "ISC",
  alternatives: [ "mri", "@oclif/core", "yargs" ],
  reasons: [ "Very high adoption and usage: it has far more downloads than most dedicated CLI parsers.",
    "Actively maintained and part of the widely used yargs ecosystem.",
    "Good modern support: ESM support is documented, and it works in Node.js, Deno, and browsers.",
    "Flexible parser features: aliases, arrays, booleans, coercion, defaults, and more.",
    "Clear, simple parser API if you want parsing without a full CLI framework."
  ],
  tradeoffs: [ "It is only the argument parser, not a full CLI framework with commands, help generation, and subcommand routing.",
    "If you want a batteries-included CLI tool, yargs or oclif may be a better fit.",
    "For very small CLIs, mri can be lighter and simpler, but it has less feature depth."
  ],
}
```

CLI パーサーとして yargs-parser が選ばれました。

## レポジトリ

以上の内容は以下のレポジトリでも公開しています。

<https://github.com/kt3k/reason-act-demo>

## まとめ

* ReAct は「Thought / Act / Observation」のループで実現できる
* フレームワークなしでもシンプルに実装可能だが、プロンプトとパーサー周りは細かいチューニングが必要
