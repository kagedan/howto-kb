---
id: "2026-06-24-puterjsでapiキー不要のaiチャットを作りbyokで複数aiを切り替える-01"
title: "Puter.jsでAPIキー不要のAIチャットを作り、BYOKで複数AIを切り替える"
url: "https://qiita.com/masakazuimai/items/44a4d4596e4645a1fe69"
source: "qiita"
category: "ai-workflow"
tags: ["API", "OpenAI", "Gemini", "GPT", "qiita"]
date_published: "2026-06-24"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

## 結論（3点）

- **Puter.js を `<script>` で読むだけで、APIキーなしにブラウザから GPT / Claude / Gemini 系を呼べる**（`puter.ai.chat()`）。無料の裏側は「利用料を利用者の Puter アカウントが負担する」User Pays モデル
- 精度・速度・モデルを自分で握りたいときは **BYOK（自分のAPIキー）**。Gemini / Groq / Claude を**同じ `callAI()` に包む**と切り替えが `switch` 1か所で済む
- スマホ Safari は**サインインのポップアップがブロックされて固まる**ので、最初の応答にタイムアウトを置いて別AIへ誘導する

## Puter.js でキーなしに AI を呼ぶ

```html
<script src="https://js.puter.com/v2/"></script>
<script>
  const reply = await puter.ai.chat("日本の首都はどこ？");
  console.log(reply); // -> 回答テキスト
</script>
```

ストリーミングは `{ stream: true }`、モデル指定は `{ model: "claude-sonnet-4" }`。返り値は async iterator なので `part.text` を繋ぐだけです。

```js
const res = await puter.ai.chat(messages, { stream: true });
let full = "";
for await (const part of res) full += part?.text ?? "";
```

`messages` は `[{ role, content }]` の配列。**会話履歴をそのまま渡せばマルチターン**になります。

## BYOK で複数 AI を共通化する

呼び出し口を 1 つに統一し、中で `switch` するだけにします。

```js
export async function callAI({ provider, model, messages, apiKey }) {
  switch (provider) {
    case "puter":  return callPuter({ model, messages });
    case "gemini": return callGemini({ model, messages, apiKey });
    case "groq":   return callGroq({ model, messages, apiKey });
    case "claude": return callClaude({ model, messages, apiKey });
  }
}
```

各社のクセは下表のとおり。これを各関数の中だけに閉じ込めれば、UI 側は `callAI()` だけ知っていればよくなります。

| プロバイダ | 作法 | ポイント |
|---|---|---|
| Puter | キー不要 | `puter.ai.chat()`。初回サインインが要る |
| Gemini | `contents` で送る | `role: assistant` → `model` に変換が必要 |
| Groq | OpenAI 互換 | `messages` を変換なしでそのまま投げられる |
| Claude | 専用ヘッダ | `anthropic-dangerous-direct-browser-access: true` が必要 |

OpenAI 互換の Groq は一番素直です。

```js
const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
  },
  body: JSON.stringify({ model, messages }), // そのまま
});
const text = (await res.json()).choices[0].message.content;
```

Claude をブラウザから直接叩くときは、`anthropic-dangerous-direct-browser-access: true` を付けないと CORS で弾かれます。キーが露出する形なので、**自分のキーを自分の端末で使う BYOK だから許される**用途と割り切ります。

## スマホで Puter が固まる対策

初回サインインのポップアップがブロックされると応答が来ないので、**最初のチャンクが一定時間来なければ打ち切って案内**します。

```js
let firstSeen = false;
const timeout = new Promise((_, reject) =>
  setTimeout(() => {
    if (!firstSeen) reject(new Error("別のAI（自分の無料キー）に切り替えてください"));
  }, 30000)
);
// 本体は最初のチャンクで firstSeen = true にする
return Promise.race([run(), timeout]);
```

`callAI()` で口が揃っているので、**別プロバイダへの切り替えは 1 行**で済みます。

## まとめ

- Puter.js は `<script>` + `puter.ai.chat()` で**キーなしに AI を呼べる**（User Pays モデル）
- 複数 AI は **`callAI({ provider, ... })` で口を 1 つに**し、各社のクセ（Gemini の role 変換 / Groq の OpenAI 互換 / Claude の専用ヘッダ）は中に閉じ込める
- スマホのポップアップ詰まりは**タイムアウト + 別 AI へ切り替え**で回避

`messages` の形を全プロバイダで揃えておけば、AI の追加も差し替えも `switch` を 1 行いじるだけです。

---

この実装で作った AI メモアプリ: [AIでちょっと調べながらメモ](https://codequest.work/generator/ai-shirabe-memo/?utm_source=qiita&utm_medium=article&utm_campaign=puter-js-keyless-ai-byok) — 付箋に質問を書くと AI が答える、登録不要・無料のメモアプリ。
Web制作・SEOツール開発の技術情報サイト: [CodeQuest.work](https://codequest.work/?utm_source=qiita&utm_medium=article&utm_campaign=puter-js-keyless-ai-byok)
