---
id: "2026-06-25-playwrightで生成ai-webuiを自動操作するときのつまづきポイント-01"
title: "Playwrightで生成AI WebUIを自動操作するときのつまづきポイント"
url: "https://qiita.com/katojishi/items/d3730f7c451046d5516f"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Gemini", "GPT", "JavaScript", "TypeScript"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

## はじめに

「Gemini・ChatGPT・Claude・Perplexityに、一つの画面からまとめて質問を投げたい」

そんな動機から、Playwright + Node.js（TypeScript）+ HTML/CSS/JS で Windows デスクトップ向けの一括調べものツールを作成しました。

**APIキー不要**で Gemini/ CHATGPT / Claude / Perplexityを同時に試せるのが最大の特徴です。
各サービスの WebUI をそのまま Playwright で操作するため、APIの料金も契約も不要。
ブラウザで使える範囲のモデルに、一つの入力フォームからまとめてアクセスできます。

しかし、本アプリはいずれの生成AIの推奨された使い方ではないので、使用する際は必ず自己責任でお願いします。

リポジトリ：https://github.com/katojishiKun/Generative-AI-Bulk-Search

この記事では、作る過程で遭遇した設計上のポイントとつまづきを中心に整理しています。
Playwright の基本的な使い方はある程度知っている人を想定しています。

---

## アーキテクチャの全体像

```
[generative.html]  ← ユーザーが操作する入力フォーム（file://で開く）
       ↕  exposeFunction / evaluate
[open-generative.ts]  ← Node.js側のメイン処理
       ↕  CDP（Chrome DevTools Protocol）
[Chrome（専用プロファイル）]
   ├── Tab1: generative.html（入力UI）
   ├── Tab2: Gemini
   ├── Tab3: ChatGPT
   ├── Tab4: Claude
   └── Tab5: Perplexity
```

ポイントは「UIとロジックの橋渡し」に `exposeFunction` と `evaluate` を使っている点です。
Playwright は通常「テスト自動化ツール」として使われますが、このプロジェクトでは**「ブラウザを操作するバックエンドランタイム」**として運用しています。

---

## 1. `exposeFunction` で HTML ↔ Node.js を繋ぐ設計

### なぜこの設計にしたか

最初に思い浮かぶのは「ローカル HTTP サーバーを立てて fetch で通信する」方式だが、今回は避けました。
理由は**ポート管理が不要・追加依存なし・`file://` で完結できる**からです。
Playwright の `exposeFunction` と `evaluate` だけで双方向通信が成立する。

### フロント → Node.js（exposeFunction）

`exposeFunction` は、Node.js 側で定義した非同期関数を、ブラウザの `window` オブジェクトに生やす機能。

```typescript
// Node.js側（open-generative.ts）
await inputPage.exposeFunction('sendToGemini', async (text: string, entryId: string) => {
  // ここはNode.jsのコンテキストで実行される
  await geminiPage.bringToFront();
  // ...テキスト入力・送信処理...
});
```

```javascript
// ブラウザ側（generative.js）
await window.sendToGemini(text, entryId);  // Node.jsの関数をそのまま呼べる
```

ブラウザから Node.js の関数が呼べる、という点が直感に反して面白い。戻り値は `Promise` で受け取れるので `await` も普通に効きます。

> **💡 `exposeFunction` の引数はシリアライズされる**
>
> 引数は JSON 形式でやり取りされます。
つまり **DOM 要素やクラスインスタンスは渡せない**。
プリミティブ値・配列・プレーンオブジェクトのみ受け渡し可能。

### Node.js → フロント（evaluate）

逆方向、つまり Node.js からブラウザの JS を呼ぶには `page.evaluate` を使用。

```typescript
// Node.js側：ブラウザのグローバル関数を呼び出す
await inputPage.evaluate(
  ({ id, a }) => { (window as any).updateGeminiResponse(id, a); },
  { id: entryId, a: answer }
);
```

```javascript
// ブラウザ側：Node.jsから呼ばれるコールバック関数として定義しておく
window.updateGeminiResponse = function(entryId, answer) {
  updateResponse('gemini', entryId, answer);
  statusEl.textContent = 'Gemini の回答を受け取りました。';
};
```

> **💡 `evaluate` の第二引数はシリアライズ経由で渡る**
>
> `evaluate` のコールバック内で Node.js 側の変数をクロージャとして参照しようとするとエラーになる。必ず第二引数（`args`）として明示的に渡すこと。
>
> ```typescript
> // NG: Node.js側の変数をクロージャで参照しようとしている
> await page.evaluate(() => { doSomething(entryId); }); // entryId is not defined
>
> // OK: 第二引数で明示的に渡す
> await page.evaluate((id) => { doSomething(id); }, entryId);
> ```

---

## 2. 直列送信 × 並行回答待機 という非同期設計

### タブのフォーカス競合問題

最初、全 AI への送信を `Promise.all` で並行実行しようとしたが、すぐに問題が発生。
`bringToFront()`（タブをアクティブにする）を複数タブで同時に呼ぶと、**フォーカスが奪い合いになり入力が正しく行われなかった**。

AI サービスの入力欄はリッチテキストエディタ実装が多く、フォーカスが外れていると入力が欠落する。

解決策は「**送信は直列、回答待ちは並行**」に分けることでした。

```typescript
// ブラウザ側（generative.js）：送信は順番に（直列）
if (checkedTargets.includes('gemini'))     await window.sendToGemini(text, entryId);
if (checkedTargets.includes('chatgpt'))    await window.sendToChatGPT(text, entryId);
if (checkedTargets.includes('claude'))     await window.sendToClaude(text, entryId);
if (checkedTargets.includes('perplexity')) await window.sendToPerplexity(text, entryId);
```

```typescript
// Node.js側（open-generative.ts）：各sendTo関数の内部構造
await inputPage.exposeFunction('sendToGemini', async (text: string, entryId: string) => {
  // ① 入力・送信（awaitして直列化）
  await typeWithRetry(geminiPage, inputSelector, text, getActualText);
  await sendBtn.click();

  // ② 回答待ちはfire-and-forget（非同期で走らせてすぐreturn）
  void (async () => {
    const answer = await waitForGeminiResponse(capturedGeminiCount);
    await inputPage.evaluate(
      ({ id, a }) => { (window as any).updateGeminiResponse(id, a); },
      { id: entryId, a: answer }
    );
  })();
  // ここでreturn → ブラウザ側の次のawait（sendToChatGPT）へ進む
});
```

送信関数の中で回答待ちを `void` な fire-and-forget として投げることで、「送信は一件ずつ終わるのを待ちながら、回答はバックグラウンドで全 AI が並行して待機する」という動作になる。

> **💡 `void` 演算子での fire-and-forget**
>
> `void asyncFn()` は「Promise を意図的に捨てる」という明示的なイディオム。ESLint で `@typescript-eslint/no-floating-promises` を有効にしている場合、`await` なしの Promise を警告してくれるが、`void` を付けることで「意図的に捨てている」と宣言できる。

---

## 3. Playwright でのテキスト入力のつまづきポイント

### `keyboard.type()` ではなく `execCommand('insertText')` を使う

最初は `page.keyboard.type(text)` でテキストを入力しようとしたが、いくつか問題が起きた。

| 問題 | 詳細 |
|---|---|
| **改行が送信トリガーになる** | `\n` が Enter キーとして扱われ、複数行の質問を入力中に送信されてしまう |
| **フォーカスが外れると入力が途切れる** | タイピングシミュレーションのため、途中でフォーカスが外れると残りが欠ける |
| **クリップボードを汚す** | `clipboard-write` を使う実装だと OS のクリップボード内容が上書きされる |

解決策として `document.execCommand('insertText')` を使った。

```typescript
await page.evaluate(({ sel, txt }) => {
  const el = document.querySelector(sel) as HTMLElement;
  if (el) {
    el.focus();
    document.execCommand('insertText', false, txt);
  }
}, { sel: inputSelector, txt: text });
```

`execCommand` は WebKit/Blink 系では現役で動作し、

- **一括挿入**なのでフォーカス外れの影響を受けない
- **クリップボードを使わない**
- `\n` はテキストとして挿入され、Enter キーとは解釈されない

> **💡 `execCommand` は MDN で非推奨とされているが…**
>
> [MDN](https://developer.mozilla.org/ja/docs/Web/API/Document/execCommand) では非推奨扱いだが、Playwright（Chromium）では現在も問題なく動作する。代替案として `ClipboardItem` + `navigator.clipboard.write` + `Ctrl+V` という方法もあるが、ブラウザの権限周りが面倒なので、Playwright 用途では `execCommand` の方がシンプルで現実的。

---

## 4. 入力チェック＆リトライ設計（低スペック PC 対応）

### なぜリトライが必要になったか

低スペック PC や高負荷状態では、`execCommand` でテキストを挿入した直後に DOM への反映が遅延することがある。「入力した → すぐ送信ボタンをクリック → 実は入力欄が空だった」というケースが多数発生しました。

実装した `typeWithRetry` 関数では、入力後に**実際に DOM に反映された文字数を検証**し、期待値から外れた場合はクリアして再入力する。

```typescript
async function typeWithRetry(
  page: Page,
  inputSelector: string,
  text: string,
  getActualText: () => Promise<string>
): Promise<void> {
  const expectedLen = text.trim().length;

  for (let attempt = 1; attempt <= MAX_TYPE_RETRIES; attempt++) {
    // Ctrl+A → Backspace でクリア
    const inputEl = page.locator(inputSelector).first();
    await inputEl.click();
    await page.keyboard.press('Control+a');
    await page.keyboard.press('Backspace');
    await new Promise(r => setTimeout(r, 200)); // クリア完了待ち

    // 一括挿入
    await page.evaluate(({ sel, txt }) => {
      const el = document.querySelector(sel) as HTMLElement;
      if (el) { el.focus(); document.execCommand('insertText', false, txt); }
    }, { sel: inputSelector, txt: text });

    await new Promise(r => setTimeout(r, 1000)); // DOM反映待ち

    // 文字数を検証（85%〜115%なら合格）
    const actualLen = (await getActualText()).trim().length;
    const ratio = expectedLen > 0 ? actualLen / expectedLen : 1;
    if (ratio >= 0.85 && ratio <= 1.15) return; // OK

    if (attempt < MAX_TYPE_RETRIES) {
      await new Promise(r => setTimeout(r, RETRY_DELAY_MS));
    }
  }
  throw new Error(`${MAX_TYPE_RETRIES}回リトライしましたが、正しく入力できませんでした。`);
}
```

### 85〜115% という許容幅の根拠

100% ピッタリで判定しない理由は、改行コードの扱いの差でした。
入力元のテキストが `\r\n`（Windows 改行）を含む場合、ブラウザ側では `\n` に変換されて 1 文字分少なくなる。
改行の多い長文を投げると数十文字規模のズレが生じるため、±15% の幅を持たせることにしました。

> **💡 `innerText` vs `textContent` vs `value` — 入力欄の種類ごとに違う**
>
> 各 AI の入力欄は実装形式がバラバラで、実際のテキストを取得するプロパティも異なる。
>
> | サービス | 入力欄の実装 | 実テキスト取得 |
> |---|---|---|
> | Gemini | `contenteditable div`（Quill 系） | `textContent` |
> | ChatGPT | `<textarea>` or `contenteditable div` | `.value` or `.innerText` |
> | Claude | ProseMirror（`contenteditable div`） | `.innerText`（改行を正しく反映） |
> | Perplexity | `<textarea>` or `contenteditable div` | `.value` or `.textContent` |
>
> ProseMirror は `textContent` だと改行が消えてしまうため `innerText` が必要。`value` はネイティブの `<textarea>` や `<input>` にしか存在しない点も注意。

---

## 5. 各 AI の回答完了を検出する方法の違い

ここが最もサービスごとの差が出るポイントだ。

### Gemini：カスタム要素のカウント＋テキスト安定確認

```typescript
// 新しい model-response 要素が増えるまで待つ
while (Date.now() - start < timeoutMs) {
  const count = await geminiPage.evaluate(
    () => document.querySelectorAll('model-response').length
  );
  if (count > previousCount) break;
  await new Promise(r => setTimeout(r, 500));
}

// テキストが3回連続で変化しなければ完了とみなす
let stableCount = 0;
while (Date.now() - start < timeoutMs) {
  const currentText = await geminiPage.evaluate((prev) => {
    const responses = document.querySelectorAll('model-response');
    const last = Array.from(responses).slice(prev).at(-1);
    return last?.querySelector('message-content')?.textContent?.trim() ?? '';
  }, previousCount);

  if (currentText === lastText && currentText.length > 0) {
    stableCount++;
    if (stableCount >= 3) {
      // 安定したら innerHTML を返す（テキストではなくレンダリング済みHTMLを取得）
      return await geminiPage.evaluate((prev) => {
        const responses = document.querySelectorAll('model-response');
        const last = Array.from(responses).slice(prev).at(-1);
        return last?.querySelector('message-content')?.innerHTML ?? '';
      }, previousCount);
    }
  } else {
    stableCount = 0;
    lastText = currentText;
  }
  await new Promise(r => setTimeout(r, 1500));
}
```

Gemini は `<model-response>` というカスタム要素を使っており、これを利用できる。生成中かどうかを示す属性が安定して使えなかったため、**textContent を 1.5 秒ごとにポーリングして 3 回連続で変化しなければ完了**という安定判定方式を採用した。

### Claude：`data-is-streaming` 属性の監視

```typescript
// data-is-streaming="true" の要素がなくなるまで待つ
while (Date.now() < deadline) {
  const isStreaming = await claudePage.evaluate(() =>
    document.querySelector('[data-is-streaming="true"]') !== null
  );
  if (!isStreaming) break;
  await new Promise(r => setTimeout(r, 800));
}
```

Claude は生成中に `data-is-streaming="true"` という属性を持つ要素が DOM に存在し、生成完了と同時に値が変化する。これを使えば**「ストリーミング完了」を属性で直接検知**できるため、ポーリング間隔を短くしても安定して動く。

> **💡 Claude が最もシンプルに完了検知できる**
>
> 他のサービスはテキストの安定確認という間接的な手法が必要だが、Claude は `data-is-streaming` という明示的な属性があるため実装がクリーンになる。こういった「自動化しやすい設計」が開発者フレンドリーだと感じる部分だった。

### ChatGPT：`data-message-author-role` でカウント

```typescript
const CHATGPT_RESPONSE_SEL = '[data-message-author-role="assistant"]';
// この要素数が増えるまで待ち → textContentの安定判定

// innerHTML を返す際はmarkdown要素を優先して取得
const html = await chatgptPage.evaluate(({ sel, prev }) => {
  const responses = document.querySelectorAll(sel);
  const last = Array.from(responses).slice(prev).at(-1);
  const markdown = last?.querySelector('.markdown, .prose');
  return (markdown ?? last)?.innerHTML ?? '';
}, { sel: CHATGPT_RESPONSE_SEL, prev: previousCount });
```

ChatGPT は assistant の発言ごとにこの data 属性を持つ要素が追加される。`.markdown` や `.prose` セレクタを優先取得することで、メインの回答テキストだけを抽出できる。

> **💡 ChatGPT のレスポンス要素には複数の中身が混在する**
>
> ChatGPTのレスポンス要素には、マークダウンレンダリングされた部分（`.markdown` や `.prose`）と引用・ツール呼び出し等が混在していることがある。`.querySelector('.markdown, .prose')` で絞ることで、メインの回答テキストだけを取れる。

### Perplexity：`.prose` 要素のカウント＋安定確認

```typescript
const PERPLEXITY_RESPONSE_SEL = '.prose';
// .prose 要素が増えるまで待ち → textContentの安定判定

// 送信前に毎回新規チャット画面へ遷移する
await perplexityPage.goto(PERPLEXITY_URL, { waitUntil: 'domcontentloaded' });
```

Perplexity は毎回新規チャット画面（トップページに `goto`）してから送信している。理由は「続きのチャット」になってしまうと前回の `.prose` 要素が残りカウントがズレるため。
毎回クリーンな状態にリセットすることで、カウントベースの検知が安定する。

---

## 6. Chrome 起動の工夫：専用プロファイル＋CDP で接続

Playwright でブラウザを CDP で制御する構成にしている。`chromium.launch()` ではなく `chromium.connectOverCDP()` を使い、自前で起動した Chrome に Playwright を接続する方式だ。

### なぜ専用プロファイルが必要だったか

Chrome 127 以降で導入された **App-Bound Encryption** の影響で、通常の「User Data」ディレクトリに `--remote-debugging-port` で接続しようとすると、Cookie が暗号化されたまま読み取れず**全サービスでログアウト状態**になる。

専用プロファイルフォルダ（プロジェクト直下の `chrome-profile/`）を使うことでこの問題を回避できる。

```typescript
const USER_DATA_DIR = path.join(__dirname, 'chrome-profile');

const chromeProcess = spawn(CHROME_EXE, [
  `--user-data-dir=${USER_DATA_DIR}`,
  `--remote-debugging-port=${REMOTE_DEBUGGING_PORT}`,
  '--disable-blink-features=AutomationControlled', // 自動化検知を無効化
  '--disable-background-timer-throttling',          // バックグラウンドタブの制限解除
  '--disable-backgrounding-occluded-windows',       // 非表示ウィンドウの処理制限解除
  '--disable-renderer-backgrounding',               // バックグラウンドタブのレンダラー制限解除
  '--allow-file-access-from-files',                 // file://からJS/CSSの読み込みを許可
]);

// CDP エンドポイントが上がるまでポーリング
await waitForCDP(REMOTE_DEBUGGING_PORT);

// Playwright を CDP 経由で接続
const browser = await chromium.connectOverCDP(`http://localhost:${REMOTE_DEBUGGING_PORT}`);
```

> **💡 `--allow-file-access-from-files` は必須**
>
> `file://` で開いた HTML ページから相対パスの CSS や JS を読み込む場合、このフラグがないと「Cross-origin エラー」でスクリプトが読み込まれない。開発中に「なぜか JS が動かない」という問題の多くはこれが原因。

> **💡 `--disable-background-timer-throttling` 系フラグの意味**
>
> Chrome はバックグラウンドタブの JavaScript タイマーを意図的に間引く。このツールはバックグラウンドタブ（各 AI のタブ）で `setTimeout` による回答ポーリングを走らせているため、これを無効化しないと待機タイマーが大幅に遅延する。

### 既存セッションの再利用

ツールを二重起動した場合に備え、起動前に CDP エンドポイントが既に存在しないかチェックし、あれば新規起動せず接続する。

```typescript
async function isCDPAlreadyRunning(port: number): Promise<boolean> {
  try {
    const res = await fetch(`http://localhost:${port}/json/version`);
    return res.ok;
  } catch {
    return false;
  }
}

if (await isCDPAlreadyRunning(REMOTE_DEBUGGING_PORT)) {
  const browser = await chromium.connectOverCDP(`http://localhost:${REMOTE_DEBUGGING_PORT}`);
  // 既存のコンテキスト・ページをそのまま再利用
}
```

---

## 7. 各 AI の CSS セレクタ選定の考え方

各 AI の UI 要素を特定するセレクタは、変更耐性の観点から「なるべく安定した属性」を選ぶようにした。

```typescript
// Gemini
const inputSelector = 'rich-textarea div[contenteditable="true"], rich-textarea div.ql-editor';
// → カスタム要素 <rich-textarea> の中の contenteditable 要素を対象に

// ChatGPT
const inputSelector = '#prompt-textarea';
// → ID が安定しているので最もシンプル

// Claude
const CLAUDE_INPUT_SEL = '[data-testid="chat-input"], .tiptap.ProseMirror, [role="textbox"]';
// → data-testid → クラス名 → role の優先順位でフォールバック

const CLAUDE_SEND_BTN_SEL = 'button[aria-label*="Send"], button[aria-label*="送信"]';
// → aria-label の部分一致で多言語対応（英語UI・日本語UIの両方に対応）

// Perplexity
const PERPLEXITY_INPUT_SEL = 'textarea[placeholder], div[contenteditable="true"]';
```

> **💡 セレクタの安定性の優先順位**
>
> `data-testid` > `id` > `aria-label` > 意味のあるクラス名 > DOM 構造依存
>
> `data-testid` はフロントエンド開発チームがテスト用に意図的につけている属性なので、デザイン変更では消えにくい。Claude がこれを持っているのが助かました。
逆に `div.sc-xxxxx` のような CSS-in-JS で生成されたクラス名はビルドごとに変わるため使わない方が良い。

---

## まとめ

| テーマ | 採用した解決策 |
|---|---|
| HTML ↔ Node.js 通信 | `exposeFunction`（フロント→Node.js）＋ `evaluate`（Node.js→フロント） |
| タブのフォーカス競合 | 送信は直列、回答待ちは fire-and-forget で並行 |
| テキスト入力 | `execCommand('insertText')` で一括挿入 |
| 入力漏れ対策 | 文字数検証＋リトライ（±15% 許容） |
| 回答完了検知 | サービスごとに最適な手法（属性監視 or textContent 安定確認） |
| Cookie の保持 | 専用プロファイル＋CDP で接続 |

Playwright は「テスト自動化ツール」としての文脈で語られることが多いが、`exposeFunction` や `evaluate` を組み合わせることで「ブラウザと Node.js が協調するデスクトップアプリ基盤」としても機能する。Electron ほど重くなく、Web アプリをそのまま活用できるのが強みです。

API キーなしで複数の生成 AI を同時に試したい、あるいは同様のブラウザ操作ツールを作りたい人の参考になれば。


## ⚠️ 免責事項（重要）

本ツールをご利用いただく前に、必ず以下の免責事項をお読みください。

1. **自己責任での利用**
   * 本ツールは個人開発のオープンソースソフトウェアです。本ツールの利用により生じた直接的・間接的な損害（アカウントの利用制限・BAN、PCの不具合、データの紛失など）について、開発者は**一切の責任を負いません**。すべて自己責任でのご利用をお願いいたします。
2. **自動化スクリプトによるリスク**
   * 本ツールは自動操作ライブラリ（Playwright）を用いてWebブラウザを操作します。各AIサービスの利用規約では自動操作が制限されている場合があり、頻繁なリクエストや使用状況によっては**アカウントが制限されるリスク**がゼロではありません。
3. **規約・仕様変更への追従**
   * 各生成AIサービスのUI（デザイン）や仕様の変更により、ツールが正常に動作しなくなる可能性があります。
