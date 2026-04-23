---
id: "2026-03-31-claudecodeとはどのような状態機械であるか-流出したclaudecodeのソースコードを読み-01"
title: "ClaudeCodeとは、どのような状態機械であるか? ~ 流出したClaudeCodeのソースコードを読み解いてみた ~"
url: "https://zenn.dev/jintarotanba/articles/a5018cbed152ed"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

`LLM APIをどう実行するか` という観点から Claude Code を読むと、このコードベースは「高機能なAIエージェントの魔法の塊」ではありません。  
むしろ、かなり明確に次の3層へ分解できます。

* `request compiler`  
  会話状態を、毎ターン API に送れる payload へ再コンパイルする層
* `runtime harness`  
  その payload を実際に API へ流し、ストリームを解釈し、ツール実行や権限処理を仲介する層
* `recursive state machine`  
  `assistant -> tool_use -> tool_result -> next request` を反復して会話を進める層

Claude Code の本質は、この3層の設計にあります。

## 1. 設計思想の解読

Claude Code の設計思想を一言でいえば、`会話をそのままLLMへ投げない` ことです。  
毎ターン、内部状態をいったん分解し、LLM API に最適な形へ再構成し、返ってきたストリームを再び内部状態へ還元します。中心にあるのは prompt ではなく、**状態変換ループ**です。

このコードベースを読むと、少なくとも次の思想が見えます。

* Claude Code は「prompt を1回送るアプリ」ではなく、「複数の API 呼び出しを連結するオーケストレータ」である
* transcript は真実ではなく、API 再送用に毎回 repair される中間表現である
* prompt caching は最適化ではなく、設計制約そのものである
* model output は信用されず、stream も `tool_use.input` も壊れうる I/O として扱われる
* tool use は model の自由意志ではなく、権限・hooks・classifier によって仲介される
* memory, compact, subagent は「賢さの追加」ではなく、次の API 呼び出しを準備する補助ループである

この設計思想は、[`QueryEngine.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/QueryEngine.ts#L175) の入口、[`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts#L241) の主ループ、[`services/api/claude.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/claude.ts#L1538) の request 構築、[`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L1989) の normalization に一貫して現れています。

言い換えると、Claude Code は `agent` というより次の関数に近いです。

```
next_state = reduce(
  current_state,
  run_harness(
    compile_request(current_state)
  )
)
```

この読み方をすると、Claude Code の全体像がかなり整理されます。

## 2. アーキテクチャ全体像の説明

### 全体の見取り図

Claude Code の主要概念は次の通りです。

* `Conversation State`  
  ユーザー入力、assistant 出力、tool result、attachment、compact boundary などを含む内部会話状態
* `Cache-safe Prefix`  
  system prompt, userContext, systemContext, tools, messages prefix など、prompt cache key を支える部分
* `Request Compiler`  
  内部状態から API payload を作る層。message normalization、system prompt 分割、tool schema 化を含む
* `Runtime Harness`  
  provider client、retry、stream parser、tool execution、permission、hooks を含む実行基盤
* `Context Manager`  
  tool result budgeting、microcompact、autocompact、tool search、memory injection などを担当する層
* `Side Loops`  
  compaction agent、memory extraction、session memory、prompt suggestion のような派生 API 呼び出し群

### 概念の関係性

この図のポイントは、Claude Code の中心が `LLM` 単体ではなく、`State -> Payload -> Runtime -> State` の循環にあることです。

### 概念的コード

Claude Code のアーキテクチャは、概念的には次のように書けます。

```
type AgentState = {
  messages: Message[]
  systemPrompt: SystemPrompt
  userContext: Record<string, string>
  systemContext: Record<string, string>
  toolUseContext: ToolUseContext
}

async function runClaudeCodeTurn(state: AgentState) {
  while (true) {
    const payload = compileRequest(state)
    const assistantMessages = await executeLLMRequest(payload, state)

    state.messages.push(...assistantMessages)

    const toolUses = collectToolUses(assistantMessages)
    if (toolUses.length === 0) {
      await runStopHooksAndBackgroundLoops(state)
      return state
    }

    const toolResults = await executeToolBatch(toolUses, state)
    state.messages.push(...toolResults)
  }
}

function compileRequest(state: AgentState) {
  let messages = normalizeMessagesForAPI(state.messages)
  messages = applyToolResultBudget(messages)
  messages = maybeSnip(messages)
  messages = maybeMicroCompact(messages)
  messages = maybeAutoCompact(messages)

  return {
    system: buildSystemPromptBlocks(
      appendSystemContext(state.systemPrompt, state.systemContext)
    ),
    messages: prependUserContext(messages, state.userContext),
    tools: toolToAPISchema(state.toolUseContext.options.tools),
    thinking: resolveThinking(state.toolUseContext),
    betas: resolveBetaHeaders(),
    cache: resolvePromptCaching(),
  }
}
```

実装としては、この疑似コードの各行がかなり分厚いです。

## 3. 主要な概念の詳細

### 3.1 Conversation State

Claude Code の source of truth は prompt ではなく `messages` です。  
ただしそれは API にそのまま送る配列ではありません。内部の `messages` には progress, system message, attachment, tombstone など UI や実行制御のための要素も混ざっています。これが、送信前に別形式へ変換されます。参照: [`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts#L203), [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L1989)

重要なのは、Claude Code が「会話表示用の状態」と「API送信用の状態」を分けていることです。

### 3.2 Cache-safe Prefix

Claude Code では、毎ターンの API 呼び出しのうち、何が cache key を壊し、何が壊さないかが明確に意識されています。  
そのため `CacheSafeParams` という名前で、system prompt, userContext, systemContext, toolUseContext, forkContextMessages が束ねられています。参照: [`utils/forkedAgent.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/forkedAgent.ts#L46)

この概念があるため、subagent ですら「独立した別人格」ではなく、「同じ prefix を共有する派生 request」として扱われます。

### 3.3 ToolUseContext

`ToolUseContext` は Claude Code の実行時コンテナです。  
model、tools、thinkingConfig、mcpClients、abortController、AppState、readFileState、messages など、API 呼び出しとツール実行に必要な runtime state が一箇所に集められています。参照: [`Tool.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/Tool.ts#L158)

これは単なるコンテキストオブジェクトではありません。Claude Code における「1ターンの実行環境」そのものです。

### 3.4 Transcript-to-Wire Compiler

Claude Code の最重要概念の1つが、内部 transcript を wire format に変換する compiler 層です。

* `normalizeMessagesForAPI()` は virtual/system/progress を取り除き、隣接 user message をマージし、tool\_reference や危険な media を整理する: [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L1989)
* `ensureToolResultPairing()` は `tool_use` と `tool_result` の整合性を修復する: [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L5133)
* `normalizeContentFromAPI()` は API から返った `tool_use.input` を JSON として復元する: [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L2651)

ここで守られている不変条件は、「次の API 呼び出しに耐える transcript であること」です。Claude Code は UI に見えている履歴を、そのまま model memory だとは考えていません。

Claude Code にとって tool は「常に全部使える能力」ではありません。  
そのターンで model に公開する tool pool が、permission mode, REPL mode, MCP 接続状態, deny rule に応じて組み直されます。参照: [`tools.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/tools.ts#L193), [`tools.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/tools.ts#L271), [`tools.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/tools.ts#L345)

つまり Claude Code では、「能力の存在」と「そのターンで model に見せること」が分かれています。

### 3.6 Side Loops

memory extraction, session memory, compaction, prompt suggestion は本体ループの外側で走る派生 loop です。  
しかし設計上は、どれも別の種類の LLM API 呼び出しにすぎません。参照: [`query/stopHooks.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query/stopHooks.ts#L65), [`services/extractMemories/extractMemories.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/extractMemories/extractMemories.ts#L415), [`services/SessionMemory/sessionMemory.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/SessionMemory/sessionMemory.ts#L315)

ここから見えてくるのは、Claude Code が「メインの会話」と「周辺機能」を本質的に区別していないことです。どちらも LLM API をどう編成するかの問題です。

## 4. ClaudeCodeの中で動くLLMは世界をどう見ているか？

Claude Code を上手に使う、あるいは Claude Code のような agent を設計するうえで重要なのは、LLM が現実世界を直接見ていないことです。  
Claude Code の中の LLM が見ているのは、OS やファイルシステムそのものではなく、Claude Code が毎ターン構成する **世界のテキスト表現** です。

したがって agent design の核心は、tool を増やすことだけではありません。  
本当に重要なのは、「model に何を見せるか」「何を見せないか」「どの channel で見せるか」「変化をどう観測させるか」です。

### 4.1 自分は何者だと思っているか

Claude Code の LLM は、まず system prompt によって「自分は対話型のソフトウェアエンジニアリング agent である」と教えられます。  
`getSimpleIntroSection()`, `getSimpleSystemSection()`, `getSimpleDoingTasksSection()`, `getActionsSection()`, `getUsingYourToolsSection()`, `getSimpleToneAndStyleSection()` が、その自己像を組み立てます。参照: [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L175), [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L186), [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L199), [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L255), [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L269), [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L430)

ここで model は、少なくとも次のように自己理解します。

* 自分は user と対話しながら作業する agent である
* 通常の出力はそのまま user に見える
* 自分には tools があるが、permission mode の制約下でしか使えない
* tool result や user message には `<system-reminder>` のような system 注釈が混ざりうる
* 会話履歴は自動圧縮されうるため、見えている履歴が世界の全履歴とは限らない

さらに `computeSimpleEnvInfo()` が、作業ディレクトリ、git repository かどうか、shell、OS、model 名、knowledge cutoff まで与えます。参照: [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L651)

つまり Claude Code の LLM は、抽象的な chat model として起動しているのではありません。  
「特定の実行環境に置かれた coding agent」として起動しています。

### 4.2 何ができると理解しているか

Claude Code の LLM は、現実に存在する全機能を知っているわけではありません。  
そのターンで公開された tool pool だけを、自分の行為可能性として理解します。

`getAllBaseTools()` が理論上の base tool 集合を定義し、`getTools()` が permission context, REPL mode, deny rule などを見て、そのターンで model に見せる tool 集合を決めます。参照: [`tools.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/tools.ts#L193), [`tools.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/tools.ts#L271)

その後 `toolToAPISchema()` が description, input schema, strict, eager input streaming などを含む API schema へ変換します。参照: [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts#L119)

ここで重要なのは、LLM にとって capability とは「実際に実装されている能力」ではなく、**このターンの request で説明された affordance** だということです。

したがって Claude Code では、

* 実装されているが公開されていない tool は、LLM にとって存在しない
* deny された tool は、呼んだあと拒否されるだけでなく、そもそも見えない場合がある
* tool description の質が、そのまま行動計画の質に影響する

という構造になります。

### 4.3 どんな状況にいると理解しているか

LLM の situational awareness も、自動では生まれません。  
Claude Code は system prompt とは別に、userContext, systemContext, attachment を注入して、model に「いまどんな状況か」を教えます。

`fetchSystemPromptParts()` は system prompt, userContext, systemContext をまとめて cache-key prefix の土台として取得します。参照: [`utils/queryContext.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/queryContext.ts#L44)

その中身は、

* `getSystemContext()` が git status snapshot や cache breaker を供給する: [`context.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/context.ts#L116)
* `getUserContext()` が `CLAUDE.md` と current date を供給する: [`context.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/context.ts#L155)
* `appendSystemContext()` が system channel へ状況を足す: [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts#L437)
* `prependUserContext()` が meta user message として状況説明を先頭に差し込む: [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts#L449)
* `getAttachmentMessages()` が memory, skill discovery, queued command などの追加観測を流し込む: [`utils/attachments.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/attachments.ts#L2937), [`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts#L1580)

という形で構成されます。

ここから分かるのは、Claude Code の LLM が理解している「いま」は、自然に知覚された現在ではなく、**runtime が編集して渡した現在像** だということです。  
しかも `getSystemContext()` と `getUserContext()` は会話単位で memoize されるので、LLM が見ている世界には「セッションを通じて安定させたい静的スナップショット」と「各ターンで追加される動的観測」が混在しています。

### 4.4 世界の変化をどう知るか

Claude Code の LLM は、自分の action の結果を直接観測しません。  
世界の変化は、tool result や synthetic message として返ってきたテキストを通じてしか知りません。

`runToolUse()` は tool call の成否を message 化して transcript へ戻します。unknown tool であれば error message を、成功なら tool result を、失敗なら failure を user role message として返します。参照: [`services/tools/toolExecution.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/tools/toolExecution.ts#L337)

permission layer も同様で、拒否されたときは `Permission to use X has been denied.` という観測結果が返されます。参照: [`utils/permissions/permissions.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/permissions/permissions.ts#L1087), [`utils/permissions/permissions.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/permissions/permissions.ts#L1179)

さらに transcript 側には `CANCEL_MESSAGE`, `REJECT_MESSAGE`, `AUTO_REJECT_MESSAGE(...)` のような synthetic outcome が定義されており、実行不能や拒否も「世界についての新しい事実」として会話へ埋め戻されます。参照: [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L210), [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L212), [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L234)

つまり Claude Code において、tool は actuator であると同時に sensor でもあります。  
LLM は「行動する主体」である前に、「runtime が返す観測文を読む主体」でもあります。

### 4.5 何を見ていないか

この視点を強くするためには、逆に LLM が何を見ていないかも押さえる必要があります。

* raw filesystem は直接見えない。Read 系 tool を通じて得た断片だけが見える
* 実行基盤の内部状態すべては見えない。runtime が transcript に戻した結果だけが見える
* 全 tool の実装は見えない。そのターンで schema 化された tool だけが見える
* 会話の全履歴は見えない。compact や normalize を経た履歴しか見えない: [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L1989)
* agent ごとの視界も同じではない。subagent は自分宛ての通知だけを drain し、main thread の prompt stream 全体を見るわけではない: [`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts#L1560)

この制約は弱点ではなく、agent 設計の本質です。  
高度な agent とは、「LLM に全部を見せるシステム」ではなく、「必要な世界だけを十分に見せるシステム」です。

### 4.6 ここから学ぶべきこと

Claude Code から学ぶべき重要な教訓は、agent quality が「モデルの地力」だけでなく、**モデルに与えた世界像の質** に大きく依存することです。

Claude Code は LLM に対して、

* 自分は何者か
* 何ができるか
* いまどんな状況か
* 直前の行動で世界がどう変わったか
* 何が禁止され、何が観測不能か

を、毎ターンかなり明示的に教えています。

だから Claude Code を上手に使うとは、単に良い指示を書くことではありません。  
`CLAUDE.md`, working directory, permission mode, tool result, attachment, memory が、LLM にどんな世界像を与えているかを意識して使うことです。

そして Claude Code のような agent を作るなら、考えるべき問いは「どんな prompt を書くか」だけでは足りません。  
本当に問うべきなのは、**LLM はこのターンでどんな世界に住んでいるのか** です。

## 5. プロンプトエンジニアリング

Claude Code の prompt engineering は、「良い文章を書く」ことではありません。  
本質は、**毎ターンどういう prompt byte 列を安定に生成するか**です。

### 5.1 system prompt は section registry として管理される

`getSystemPrompt()` は巨大な文字列を直書きしているのではなく、section を組み合わせて system prompt を作ります。参照: [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L444)

その section は `systemPromptSection(...)` と `DANGEROUS_uncachedSystemPromptSection(...)` で定義され、cacheable section と cache-breaking section が区別されています。参照: [`constants/systemPromptSections.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/systemPromptSections.ts#L16), [`constants/systemPromptSections.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/systemPromptSections.ts#L27)

これは prompt engineering を「文面」ではなく「構造」に引き上げている設計です。

### 5.2 static/dynamic boundary がある

`SYSTEM_PROMPT_DYNAMIC_BOUNDARY` で、global cache できる静的部分と、session 固有の動的部分を分けています。参照: [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L105), [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts#L560)

さらに `splitSysPromptPrefix(...)` が、この境界を使って cache scope を分割します。参照: [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts#L296), [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts#L321)

Claude Code における prompt engineering の核心はここです。  
prompt をどう書くかより、**どこまで不変 prefix を伸ばせるか**の方が重要です。

Claude Code では tool は runtime capability であると同時に、model にとっては prompt surface でもあります。  
`toolToAPISchema()` は tool の description, input schema, strict, defer\_loading, eager\_input\_streaming を含む schema を作ります。参照: [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts#L119)

つまり tool prompt は system prompt の外部にある別の prompt channel です。

### 5.4 prompt は user/system context の注入点まで含めて設計されている

`prependUserContext(...)` は userContext を `system-reminder` 付きの meta user message として会話先頭に足し、`appendSystemContext(...)` は systemContext を system prompt 末尾に足します。参照: [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts#L437), [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts#L449)

つまり Claude Code の prompt engineering は、「system prompt の本文」だけでは完結していません。どの情報をどの channel から入れるかも prompt 設計です。

## 6. コンテキストエンジニアリング

Claude Code の context engineering は、単に長い履歴を保持することではありません。  
むしろ「何を入れ、何を落とし、何を圧縮し、何を次ターンへ残すか」を毎回制御することです。

### 6.1 context の供給源

Claude Code は context を複数の供給源から集めます。

* `getUserContext()` は `CLAUDE.md` と current date を供給する: [`context.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/context.ts#L152)
* `getSystemContext()` は git status snapshot や cache breaker を供給する: [`context.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/context.ts#L113)
* `fetchSystemPromptParts()` は systemPrompt, userContext, systemContext をまとめて cache-key prefix として扱う: [`utils/queryContext.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/queryContext.ts#L30)

つまり context は「履歴」だけではなく、外部ファイルや環境スナップショットまで含む合成物です。

### 6.2 context はそのまま送られず、送信前に repair される

Claude Code は会話状態をそのまま次ターンへ送らず、必ず正規化します。  
tool pairing の修復や media の除去がその例です。参照: [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L1989), [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts#L5133)

ここでの思想は、「context は保存するものではなく、毎ターン構築するもの」です。

### 6.3 context budget は明示的に管理される

`query.ts` は API を呼ぶ前に、tool result budget, snip, microcompact, context collapse, autocompact を順に適用します。参照: [`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts#L365), [`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts#L396), [`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts#L412), [`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts#L453)

`microcompactMessages(...)` は古い tool result を時間ベースで削る軽量処理であり、参照: [`services/compact/microCompact.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/compact/microCompact.ts#L253)  
`autoCompactIfNeeded(...)` は context window を超えそうなときに summary 化を走らせる重処理です。参照: [`services/compact/autoCompact.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/compact/autoCompact.ts#L241)

Claude Code は context window を memory とは見ていません。**消費予算**として見ています。

### 6.4 context は demand loading される

tool search によって deferred tool を最初から全部見せず、必要な時だけロードします。参照: [`utils/toolSearch.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/toolSearch.ts#L154)

これは、context engineering の対象が「履歴」だけではなく、「利用可能能力の説明文」まで含むことを意味しています。

### 6.5 memory も context engineering の一部である

memory extraction と session memory は、過去の会話を要約して外部ファイルへ書き出し、後で prompt に戻す仕組みです。参照: [`services/extractMemories/extractMemories.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/extractMemories/extractMemories.ts#L372), [`services/SessionMemory/sessionMemory.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/SessionMemory/sessionMemory.ts#L318)

したがって Claude Code における memory は、model の内部記憶ではなく、**context pipeline の外部ストレージ**です。

## 7. ハーネスエンジニアリング

ここでいう harness engineering とは、「LLM API を実運用で安定して回すための実行基盤」を指します。  
Claude Code の工学的価値のかなり大きな部分は、この層にあります。

### 7.1 provider client を吸収する

`getAnthropicClient()` は first-party Anthropic, Bedrock, Foundry, Vertex を切り替え、認証・ヘッダ・proxy を吸収します。参照: [`services/api/client.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/client.ts#L88)

これは harness engineering の最初の仕事です。上位の agent loop が provider 差分を知らなくてよいようにすることです。

### 7.2 retry, fallback, cooldown を持つ

`withRetry(...)` は retry context を持ち、429/529、認証エラー、stale connection、fast mode fallback などに対処します。参照: [`services/api/withRetry.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/withRetry.ts#L170)

Claude Code は API call を「成功する前提の関数呼び出し」として扱っていません。  
失敗は例外ではなく、実行モデルの一部です。

### 7.3 raw stream を自前で再構成する

`services/api/claude.ts` は `beta.messages.create(...).withResponse()` を使い、raw streaming event を自分で解釈します。参照: [`services/api/claude.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/claude.ts#L1818)

`message_start`, `content_block_delta`, `message_delta` を自前で積み上げる理由は、streaming parser を自分で制御しないと、tool input JSON や usage, stop\_reason の扱いを安定化できないからです。参照: [`services/api/claude.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/claude.ts#L1979), [`services/api/claude.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/claude.ts#L2213)

`runToolUse()` と `checkPermissionsAndCallTool()` は、型検証、追加検証、pre-tool hooks、permission、tool call、post-tool hooks を直列につなぐ pipeline です。参照: [`services/tools/toolExecution.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/tools/toolExecution.ts#L337), [`services/tools/toolExecution.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/tools/toolExecution.ts#L599)

Claude Code では、tool use は model output の直接実行ではなく、**runtime harness を通った後の実行可能計画**です。

### 7.5 policy harness が model action を監督する

permission layer は deny/ask/allow rule と mode を見た上で、必要なら classifier LLM を呼びます。参照: [`utils/permissions/permissions.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/permissions/permissions.ts#L1158), [`utils/permissions/permissions.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/permissions/permissions.ts#L688)

ここが面白いのは、「メインモデルの出した行動案を、別の runtime が審査する」点です。Claude Code は model sovereignty を採用していません。

### 7.6 stop hooks と side loops まで含めて harness

turn が終わると `handleStopHooks(...)` が呼ばれ、prompt suggestion, memory extraction, autoDream などの side loop を fire-and-forget で走らせます。参照: [`query/stopHooks.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query/stopHooks.ts#L65)

つまり harness は、単に request を送るだけではなく、「1ターン完了後に何を起動するか」まで含む運用基盤です。

### 7.7 query loop 自体も dependency injection されている

`QueryDeps` によって `callModel`, `microcompact`, `autocompact` などが注入可能になっています。参照: [`query/deps.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query/deps.ts#L21)

これはテスト容易性の話に見えますが、本質的には harness が明示的な部品として切り出されていることを示しています。

## 8. 読むべきファイル

Claude Code を `LLM APIをどう実行するか` の観点で読むなら、読む順番はかなり重要です。  
最短ルートは「入口 -> 主ループ -> request compiler -> runtime harness -> 周辺 loop」です。

### 最初に読む6ファイル

1. [`QueryEngine.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/QueryEngine.ts)  
   入口です。system prompt, userContext, systemContext, ToolUseContext をどう作るかが分かります。
2. [`query.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query.ts)  
   本体です。Claude Code の agent loop はここです。
3. [`services/api/claude.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/claude.ts)  
   request build と streaming parse の中心です。
4. [`utils/messages.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/messages.ts)  
   transcript と API payload の差を理解するための最重要ファイルです。
5. [`services/tools/toolExecution.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/tools/toolExecution.ts)  
   tool runtime の本体です。
6. [`utils/permissions/permissions.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/permissions/permissions.ts)  
   policy runtime の本体です。

### 次に読むと全体像が閉じるファイル

7. [`constants/prompts.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/prompts.ts)  
   prompt engineering を理解するための中核です。
8. [`constants/systemPromptSections.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/constants/systemPromptSections.ts)  
   prompt cache と section memoization の思想が見えます。
9. [`utils/api.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/api.ts)  
   wire format への落とし込みが見えます。
10. [`context.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/context.ts)  
    user/system context の供給源が分かります。
11. [`utils/queryContext.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/queryContext.ts)  
    cache-key prefix をどう組み立てているかが見えます。
12. [`Tool.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/Tool.ts)  
    ToolUseContext と tool abstraction の定義です。
13. [`tools.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/tools.ts)  
    model に公開する tool pool の組み立てです。

### 周辺を深掘りするファイル

14. [`services/api/client.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/client.ts)  
    provider abstraction を追うためのファイルです。
15. [`services/api/withRetry.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/api/withRetry.ts)  
    retry/fallback/cooldown の実装です。
16. [`query/stopHooks.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/query/stopHooks.ts)  
    turn 後の side loop 起動を追うためのファイルです。
17. [`utils/forkedAgent.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/utils/forkedAgent.ts)  
    subagent をどう理解すべきかが最もよく分かります。
18. [`services/mcp/client.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/mcp/client.ts)  
    MCP を Claude Code runtime に正規化するアダプタです。
19. [`services/compact/microCompact.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/compact/microCompact.ts)  
    軽量な context 削減が分かります。
20. [`services/compact/autoCompact.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/compact/autoCompact.ts)  
    context budget と compaction 発火条件が分かります。
21. [`services/compact/compact.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/compact/compact.ts)  
    compaction 自体が別の LLM loop であることが分かります。
22. [`services/extractMemories/extractMemories.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/extractMemories/extractMemories.ts)  
    memory extraction の実装です。
23. [`services/SessionMemory/sessionMemory.ts`](https://github.com/JinTanba/claude-code-leaked/blob/main/services/SessionMemory/sessionMemory.ts)  
    session memory の実装です。

### 実際の読解順

実際には次の順番で読むのがいちばん理解しやすいです。

`QueryEngine.ts -> query.ts -> services/api/claude.ts -> utils/messages.ts -> services/tools/toolExecution.ts -> utils/permissions/permissions.ts -> constants/prompts.ts -> utils/api.ts -> context.ts -> utils/forkedAgent.ts -> services/compact/autoCompact.ts -> services/mcp/client.ts`

この順で読むと、Claude Code が「prompt を工夫した agent」ではなく、**LLM API 呼び出しを中心に据えた compiler/runtime/state machine** であることが見えてきます。

## 結論

Claude Code を `LLM APIをどう実行するか` という観点から読むと、答えはかなりはっきりしています。

Claude Code は、

* 会話状態を request へ再コンパイルし
* API 呼び出しを runtime harness で安定実行し
* 返ってきた assistant 出力を再び状態へ還元し
* tool 結果や side loop を踏まえて次の request を作る

という再帰的なシステムです。

だから Claude Code の本質は、`tool_use` そのものでも、system prompt の文面そのものでもありません。  
本質は、

* どの状態を次の API 呼び出しに持ち越すか
* その状態をどの形で wire format に落とすか
* stream と tool execution をどう現実的に扱うか

という `LLM API 実行技法` にあります。

その意味で Claude Code は、「AIAgent とは結局 LLM API 呼び出しの編成技術である」という命題を、かなり純度高く実装したコードベースです。
