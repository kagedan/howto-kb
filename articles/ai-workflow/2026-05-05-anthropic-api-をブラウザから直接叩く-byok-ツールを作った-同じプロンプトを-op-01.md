---
id: "2026-05-05-anthropic-api-をブラウザから直接叩く-byok-ツールを作った-同じプロンプトを-op-01"
title: "Anthropic API をブラウザから直接叩く BYOK ツールを作った — 同じプロンプトを Opus/Sonnet/Haiku に並列投げて比較する 150 行"
url: "https://qiita.com/sen-ltd/items/e90c206e299d7ae92f90"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

> 「この用途、Opus と Haiku どっちで足りる？」を実物で比較するには、3 モデル全部に同じプロンプトを投げて結果・レイテンシ・token 数を並べて見るのが早い。**ブラウザだけで完結**するし、サーバープロキシも要らない。Anthropic API は **`anthropic-dangerous-direct-browser-access: true`** ヘッダで browser direct 呼び出しを許可しているので、BYOK (ユーザーの API キーを localStorage に保持) ツールが 150 行で書ける。
>
> ブラウザから直接 Claude を叩くときの仕様、CSRF 対策ヘッダの位置づけ、parallel fetch + 部分失敗のハンドリングの話。

![prompt-lab の UI。Anthropic API key を入れた状態で「ビルドログを見つめながら CI が緑になるのを待つ俳句を書いて」というプロンプトを 3 モデル (Opus 4.7 / Sonnet 4.6 / Haiku 4.5) に並列実行した結果。各カラムに haiku の出力 + 「3,142 ms · in 21 · out 84」のような latency と token 統計が表示されている。ダークテーマ。](https://sen.ltd/portfolio/prompt-lab/assets/screenshot.png)

🤖 **Demo**: https://sen.ltd/portfolio/prompt-lab/
📦 **GitHub**: https://github.com/sen-ltd/prompt-lab

## なぜブラウザ直叩き API が「危険」と呼ばれるか

通常、Anthropic API は **ブラウザの origin** から来たリクエストを **拒否します**。理由は CSRF 対策: `<form action="https://api.anthropic.com/...">` を仕込んだ悪意あるサイトをユーザーに踏ませると、ブラウザは送信時に認証 cookie を勝手に付ける可能性がある。これが Origin チェックなしで通ると、第三者が他人の API key で勝手にリクエストを発射できてしまう。

しかし **「自分の API key を自分のブラウザで使いたい」** という BYOK 用途では browser direct で全く問題ない。Anthropic はそのために opt-in ヘッダを用意しています:

```http
POST /v1/messages HTTP/1.1
Host: api.anthropic.com
x-api-key: sk-ant-...
anthropic-version: 2023-06-01
anthropic-dangerous-direct-browser-access: true
content-type: application/json
```

「dangerous」という命名はわざとで、**「お前は危険性を理解した上で opt-in してるんだな？」** という念押し。プロダクション app で自分のキーをこのヘッダ付きで使うと dev tools 開かれた瞬間に流出するので絶対やらない。BYOK では「ユーザー本人のキー」なので問題ない。

## 150 行の API クライアント

`anthropic-dangerous-direct-browser-access: true` を加えるだけで、後は標準の Messages API:

```javascript
const ANTHROPIC_VERSION = "2023-06-01";

export function buildHeaders(apiKey) {
  return {
    "content-type": "application/json",
    "x-api-key": apiKey,
    "anthropic-version": ANTHROPIC_VERSION,
    "anthropic-dangerous-direct-browser-access": "true",
  };
}

export async function callOnce({ apiKey, model, prompt, maxTokens = 1024, fetchFn = globalThis.fetch }) {
  const body = { model, max_tokens: maxTokens, messages: [{ role: "user", content: prompt }] };
  const t0 = Date.now();
  const res = await fetchFn("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: buildHeaders(apiKey),
    body: JSON.stringify(body),
  });
  const elapsedMs = Date.now() - t0;
  if (!res.ok) {
    const detail = (await res.json().catch(() => ({}))).error?.message || "";
    throw new Error(`HTTP ${res.status}${detail ? ` — ${detail}` : ""}`);
  }
  const data = await res.json();
  const text = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("");
  return { model, text, elapsedMs, inputTokens: data.usage?.input_tokens, outputTokens: data.usage?.output_tokens };
}
```

ポイント:

- **`fetchFn` を引数で受け取る**: テストで stub fetch を渡せるよう純粋に。実行時は `globalThis.fetch` がデフォルト
- **multi-block content の text のみ抽出**: `content` は `[{type: "text", text: "..."}, {type: "tool_use", ...}]` の配列で来る (tool 呼び出し時など)。`text` block のみ filter & join
- **エラーは `HTTP <status> — <message>` 形式**: 401 (key 無効)、429 (rate limit)、500+ などをユニフォームに表現

## 並列実行 + 部分失敗の独立性

3 モデル並列は `Promise.all` で素直にできるが、**1 つのモデルだけ失敗 (rate limit など) するケース** をちゃんと扱うと UX が一段良くなる:

```javascript
export async function callParallel({ apiKey, models, prompt, onResult, fetchFn }) {
  const tasks = models.map(async (model) => {
    try {
      const value = await callOnce({ apiKey, model, prompt, fetchFn });
      if (onResult) onResult({ model, status: "ok", value });
      return { model, status: "ok", value };
    } catch (err) {
      const error = err?.message || String(err);
      if (onResult) onResult({ model, status: "error", error });
      return { model, status: "error", error };
    }
  });
  return Promise.all(tasks);
}
```

各 task の中で **try/catch** してから `Promise.all`。これで `Promise.allSettled` 相当の挙動だが:

- 各 task の終了ごとに `onResult` callback で UI を即時更新できる (allSettled は全部揃うまで待つ)
- 戻り値の shape を統一 (`{model, status, value | error}`) で UI 側の分岐が綺麗

テストで「Opus だけ 429、Sonnet/Haiku は 200」のシナリオを書くと挙動が証明できる:

```javascript
const fetchFn = async (_url, opts) => {
  const body = JSON.parse(opts.body);
  if (body.model === "claude-opus-4-7") {
    return { ok: false, status: 429, json: async () => ({ error: { message: "rate" } }) };
  }
  return { ok: true, status: 200, json: async () => ({
    content: [{ type: "text", text: "ok" }],
    usage: { input_tokens: 1, output_tokens: 1 },
  }) };
};

const results = await callParallel({ apiKey: "k", models: MODELS.map(m => m.id), prompt: "hi", fetchFn });
const byModel = Object.fromEntries(results.map(r => [r.model, r]));
assert.equal(byModel["claude-opus-4-7"].status, "error");
assert.match(byModel["claude-opus-4-7"].error, /HTTP 429/);
assert.equal(byModel["claude-sonnet-4-6"].status, "ok");
assert.equal(byModel["claude-haiku-4-5-20251001"].status, "ok");
```

## 並列性の検証

`Promise.all` がちゃんと concurrent に走ってるか、**stub fetch にわざと違う latency を仕込んで時間計測**で確認できる:

```javascript
const fetchFn = async (_url, opts) => {
  const body = JSON.parse(opts.body);
  const delays = {
    "claude-opus-4-7": 50,    // 50ms
    "claude-sonnet-4-6": 30,  // 30ms
    "claude-haiku-4-5-20251001": 10,  // 10ms
  };
  await new Promise(r => setTimeout(r, delays[body.model]));
  return { ok: true, status: 200, json: async () => ({ /* ... */ }) };
};

const t0 = Date.now();
await callParallel({ models: MODELS.map(m => m.id), prompt: "ping", fetchFn });
const elapsed = Date.now() - t0;

assert.ok(elapsed < 80, `expected parallel (~50ms), got ${elapsed}ms`);
// sequential なら 50+30+10 = 90ms。parallel なら最遅の 50ms で終わる
```

`elapsed < 80ms` で「ちゃんと並列に走ってる」が assert できる。3 モデル × Anthropic API は **同一 origin への並列接続** なので、Chrome の per-origin 6 接続上限内に余裕で収まる。

## モデル選定の観点

`prompt-lab` を作って気づくのは、**「どのモデルでも答えはまあ正しい」** ケースが意外と多いこと。差分は:

| 観点 | Opus 4.7 | Sonnet 4.6 | Haiku 4.5 |
|---|---|---|---|
| **最高難度の reasoning** | ◎ | ○ | △ |
| **ツール使用 / 長文 spec** | ◎ | ◎ | △ |
| **大量テキスト処理 (要約・分類)** | ○ | ○ | ◎ (cost / latency) |
| **コードレビュー / 提案** | ◎ | ◎ | ○ |
| **平均レイテンシ** | 3-5s | 1-2s | < 1s |
| **token 単価 (in/out)** | 高 | 中 | 低 |

「どっちで足りる」を確かめたいときは **同じプロンプト × 3 モデルの output を並べて比較** が一番速い。**「Haiku で十分なんだな」** が見えれば月数千円のコスト削減になることもザラ。これが `prompt-lab` のユースケース。

## まとめ

- `anthropic-dangerous-direct-browser-access: true` ヘッダで Anthropic API は **browser direct** 呼び出しを許可。BYOK ツール用の opt-in
- 「dangerous」命名は **本番アプリで自分のキーを browser に出すな** という警告。BYOK では問題ない
- API クライアントは ~150 行 (build request / build headers / callOnce / callParallel)
- **per-task try/catch + Promise.all** で部分失敗を独立に扱える。`onResult` callback で UI 即時更新
- stub fetch に latency を仕込めば **並列性自体をテスト可能**
- モデル選定は「同じプロンプト × 全モデル並列」が最速。`prompt-lab` はそれを 1 つの UI にまとめた

[コード全文](https://github.com/sen-ltd/prompt-lab) — `api.js` (~150 行 + 12 テスト) と `script.js` (UI)。MIT。

[ライブデモ](https://sen.ltd/portfolio/prompt-lab/) は API キーを localStorage に保存する BYOK 動作なので、自分のキーで試せます (キーはこちらのサーバーには絶対送られない)。
