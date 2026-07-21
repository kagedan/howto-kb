---
id: "2026-07-21-claude-のサブスクリプション認証で-agent-sdk-を開発する-実践-tips-01"
title: "Claude のサブスクリプション認証で Agent SDK を開発する — 実践 Tips"
url: "https://zenn.dev/mk0bayashi/articles/fe37b27687a47e"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-rss"
query: ""
---

Claude Agent SDK でエージェントを作るとき、開発中は Claude Pro / Max のサブスクリプション認証をそのまま使えます。API キーの従量課金を気にせず試行錯誤できるので、個人開発や PoC には都合が良い。ただし、いくつか知らないと詰まる点があります。中小の受託業向けに業務エージェント（ミハシラ）を作る過程で踏んだ落とし穴を、そのまま共有します。

なお、コード片は実プロダクトから引いていますが、関数名（`renderSystemPrompt` / `buildOntologyServer` / `createApprovalRequest` など）は説明用に一部簡略化しています。

## 認証: CLI ログインを継承する

Agent SDK は、`claude` CLI でログイン済みの認証情報を継承します。つまり CLI で一度ログインしておけば、SDK 側で API キーを環境変数に置かなくても `query()` が動きます。開発マシンではこれが一番手軽です。

**ただし商用提供に切り替えるときは `ANTHROPIC_API_KEY` に移行する必要があります。** サブスクリプション認証は個人利用の枠なので、複数ユーザーにサービスとして提供するなら従量課金の API キーが正しい。幸い、切り替えは環境変数だけで済むように書いておけます。設計時点で「開発=サブスク / 提供=API キー」の二段構えを想定しておくと、後で慌てません。

コスト構造がここで質的に変わる点は要注意です。サブスクで開発している間は LLM の限界費用がほぼ見えませんが、API キーに切り替えた瞬間に1ターンごとの原価が発生します。**プライシングを設計するなら、開発中のうちに1セッションあたりのトークン消費を実測しておく**べきです（result メッセージの usage から取れます）。

## 組み込みツールを全部無効にする

Agent SDK はファイル読み書きや Bash などの組み込みツールを持っていますが、業務エージェントにこれらは要りません。むしろ危険です。`tools: []` を渡して組み込みツールを全無効化し、自分のオントロジー由来のツール（MCP サーバー経由）だけを見せます。

```
for await (const message of query({
  prompt: userMessage,
  options: {
    model: "claude-opus-4-8",
    systemPrompt: PREAMBLE + renderOntologySchema(schema),
    tools: [],                                 // 組み込みツールを全無効化
    mcpServers: { ontology: ontologyServer },  // 自作ツールだけ
    canUseTool,                                // 承認ゲート（後述）
  },
})) {
  // assistant テキストをストリーム配信
}
```

エージェントに与える手を「定義済みのアクションだけ」に絞ることが、プロンプトインジェクション対策の土台になります。何を吹き込まれても、実行できる操作の集合が広がらない。

## zod は v4 が必須

MCP ツールのパラメータスキーマを zod で書く場合、**zod は v4 系を入れてください。** v3 だと SDK の依存解決で ERESOLVE が出ます（0.3.215 時点で peerDependencies に `zod: ^4.0.0` が明記されています）。ここは地味に時間を溶かすポイントで、エラーメッセージからは原因が分かりにくい。`npm ls zod` で入っているバージョンを確認し、v4 に揃えるだけで解決します。

人間の承認が必要なアクション（破壊的・影響が大きいもの）は、`canUseTool` コールバックで遮断して承認フローに回します。実行前に割り込めるので、「エージェントが起案 → 人間がボタンで決裁」という流れを SDK の外の仕組みと繋げられます。

```
const canUseTool = async (toolName, input) => {
  const action = actionFromToolName(toolName);
  // confirm ポリシーのアクションは承認へ。ただし dryRun（試算）は確定しないので通す
  if (action?.agentPolicy === "confirm" && input.dryRun !== true) {
    const req = await createApprovalRequest(action.name, input);
    return { behavior: "deny", message: `承認待ち（ID: ${req.id}）。再実行せず承認を待って。` };
  }
  return { behavior: "allow", updatedInput: input };
};
```

deny を返すとエージェントには「承認が必要」と伝わるので、あとは PREAMBLE で「承認待ちのアクションを再実行しない」と教えておけば、行儀よく待ちます。

## structured output と maxTurns の罠

列マッピングの提案のように、エージェントループではなく**1ショットで構造化 JSON が欲しい**用途では `outputFormat`（JSON Schema 強制 + 検証済みの `structured_output`）を使います。

ここで踏んだのが **`maxTurns: 1` だと足りないことがある**という点です。structured output は内部でツール呼び出し相当のやり取りを消費するらしく、`maxTurns: 1` にすると "Reached maximum number of turns" で失敗することがありました。`maxTurns: 3` くらいに上げると安定します。1ショットのつもりでも 1 では足りない、と覚えておくと良いです。

```
for await (const m of query({
  prompt,
  options: {
    model: "claude-opus-4-8",
    tools: [],
    maxTurns: 3,   // 1 だと structured output が "max turns" で落ちることがある
    outputFormat: { type: "json_schema", schema: MY_SCHEMA },
  },
})) {
  if (m.type === "result" && m.structured_output) return m.structured_output;
}
```

**なお、構造化出力を使うときも「値そのもの」を LLM に通さない設計を勧めます。** 私の場合、CSV の列マッピングは「どの列がどのプロパティか」の対応関係だけを LLM に提案させ、実際の値の変換・検証はコードで決定的に行いました。LLM が触るデータ範囲を絞ると、精度も説明可能性も上がります。

## マルチターンは resume で

会話を継続するには、`system.init` メッセージで返る `session_id` を保存し、次回 `resume` に渡します。会話履歴・コンテキスト圧縮・プロンプトキャッシュはハーネスが自動管理するので、手動の cache\_control 実装は不要です。

一点だけ運用で注意: **サーバーを再起動すると、メモリ上の session\_id が消えてエージェントの文脈がリセットされます。** デプロイのたびに会話が途切れると使い物にならないので、session\_id は永続化ストア（私は Postgres のテナントスキーマ）に置きました。復元できない古い session\_id はエラー時に捨てて新規セッションにフォールバックする、という後始末も入れておくと堅牢です。

## まとめ

* 開発はサブスク認証（CLI ログイン継承）、商用は `ANTHROPIC_API_KEY`。切り替えは環境変数で。コストは開発中に実測
* `tools: []` で組み込みを消し、自作ツールだけ見せる
* zod は v4（v3 は ERESOLVE）
* 承認は `canUseTool` で deny → 外部フローへ
* 1ショット構造化出力は `outputFormat`。`maxTurns` は 1 だと落ちることがあるので 3 に。値は LLM に通さず対応関係だけ提案させる
* マルチターンは `resume`。session\_id は永続化する

どれも一度踏めば大したことはないのですが、最初に知っていると数時間は節約できます。次回は、この土台の上で「オントロジー定義からエージェントのツールを機械的に生成する」話を書く予定です。その先には「安全装置をプロンプトではなく構造で作る」話も控えています。
