---
id: "2026-05-31-tiptap-claude-apiでブロックタイプを保持したまま選択範囲を置換する-01"
title: "Tiptap × Claude APIで「ブロックタイプを保持したまま」選択範囲を置換する"
url: "https://zenn.dev/haruto_miyakawa/articles/23d90a93180b6c"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "Python", "TypeScript", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

note の下書きを書いていて、こんな経験はないでしょうか。

ある段落の言い回しがしっくりこないので、AI に「ここをもう少し柔らかく直して」と頼む。返ってきた文章を貼り付ける。すると——**さっきまで H2 見出しだった行が、ただの段落になっている**。

これは、AI に「文章だけ」を渡して「文章だけ」を受け取り、それを素直に差し込んでいるから起きます。見出しなのか、引用なのか、リストの項目なのか、という**ブロックの構造情報が、AI とのやり取りの途中で消えてしまう**わけです。

私はいま「つむぐ（Tsumugu）」という、note クリエイター向けの AI 共同執筆エディタを個人開発しています。Next.js + React + TypeScript + Tiptap 3 + Claude API という構成で、テキストエディタの上で部分的に AI に相談しながら書き進められるツールです。

この記事では、その中でも一番こだわった「**選択範囲を、ブロックタイプを保ったまま AI に置換させる**」機能の実装を解説します。Tiptap（ProseMirror）を使ってリッチエディタを作っている人なら、どこかで踏む問題だと思います。

この記事で引用するコードは、すべて [GitHub リポジトリ `haruto-miyakawa/tsumugu`](https://github.com/haruto-miyakawa/tsumugu) で公開しています。各コードブロックには出所のファイルパスを記載しているので、全体の文脈はリポジトリと併せて読んでもらえると分かりやすいはずです。

<https://github.com/haruto-miyakawa/tsumugu>

![](https://static.zenn.studio/user-upload/33ecc62305f2-20260531.png)

## やりたいこと

機能としてはシンプルです。

1. エディタ上で、ある段落（または見出し、引用）を選択する
2. 「ここをこう直して」と AI に指示を送る
3. AI がストリーミングで提案を返す
4. 「選択範囲を置き換える」ボタンを押すと、その範囲だけが提案で置き換わる

このとき守りたいルールが一つあります。

> **置換しても、元のブロックタイプは変わらない。**

H2 で書いた見出しに相談したら、H2 のまま返ってくる。引用（blockquote）の中の文を直したら、引用のまま直る。リストの項目を直したら、リストの項目のまま直る。

「当たり前の体験」に聞こえますが、素直に作ると、これが当たり前にならないのです。

## なぜ素直に作ると壊れるのか

Tiptap（ProseMirror）のドキュメントは、フラットなテキストではなく、ノードのツリー構造です。たとえば見出しなら `heading` ノード、段落なら `paragraph` ノード、引用なら `blockquote` の中に `paragraph` がネストしている、という具合です。

AI に渡すとき、私たちは普通そのブロックの「中身のテキスト」だけを送ります。AI は当然、テキストとして処理して、テキストとして返してきます。それをそのまま `insertContent` のような API で差し込むと、ProseMirror は「これは段落だな」とデフォルトの `paragraph` として解釈します。

結果、**見出しが段落に化ける**。「どのブロックタイプだったか」「どの範囲を置き換えるべきか」という情報を、AI に投げた瞬間に手放してしまっているのが原因です。

## 解決方針：2段構えで「範囲」と「型」を握り続ける

つむぐでは、これを2段構えで解いています。

1. **選択が変わるたびに、置き換えるべき「実効範囲」と「ブロックタイプ」を計算しておく**（エディタ本体側）
2. **AI に送信した瞬間に、その値をメッセージにスナップショットとして保存する**（AI パネル側）

ここで言う「実効範囲」がポイントです。ユーザーがドラッグした生の選択範囲（`from`/`to`）をそのまま使うのではなく、**そのブロック（ノード）の境界まで広げた範囲**を別に計算して持っておきます。

全体の流れを図にすると、こうなります。

```
段落を選択
   ↓
selectionUpdate → エディタ本体が getEffectiveReplacement() で
                  「実効置換範囲」と nodeType を計算
                  （pos.before(n) / pos.after(n) でノード境界まで拡張）
   ↓
送信時に AIパネルが、その範囲と nodeType を
         メッセージの savedRange / savedNodeType としてキャプチャ
   ↓
POST /api/editor/assist → Claude streaming
   （system プロンプトで「観察コメント → ---SUGGESTION--- → リライト文」を指定）
   ↓
クライアントが ---SUGGESTION--- で comment と suggestion に分離
   ↓
「選択範囲を置き換える」ボタン
   → insertContentAt(savedRange, buildReplacementHtml(...))
   ↓
buildReplacementHtml:
  - heading  → <h{level}>...</h{level}>
  - それ以外 → <p>...</p>   （blockquote / list の中身も <p>）
```

順に見ていきます。

## ① 選択が変わるたびに「実効範囲」を計算する

ProseMirror では、ある位置（`pos`）が、ドキュメントのツリーの中でどの深さにいるかを `depth` で表現します。`pos.node(1)` は「doc 直下のブロックノード」、つまり見出しや段落、引用そのものを指します。

さらに `pos.before(n)` / `pos.after(n)` を使うと、**depth `n` のノードのすぐ外側の位置**が取れます。これが「ノード1個まるごとを置き換えるための範囲」になります。

`selectionUpdate`（選択が変わったタイミング）で、選択範囲の `from` 位置からブロック構造を解決し、ブロックタイプごとに置換範囲を出し分けます。

components/editor/EditorShell.tsx

```
function getEffectiveReplacement(
  ed: Editor,
  from: number
): { replaceRange: SelectionRange; nodeType: NodeTypeInfo | null } {
  const pos = ed.state.doc.resolve(from);
  if (pos.depth < 1) return { replaceRange: { from, to: from }, nodeType: null };

  const d1 = pos.node(1); // doc 直下のブロック

  // 見出し → 見出しノード全体（depth 1）を置換
  if (d1.type.name === "heading") {
    return {
      replaceRange: { from: pos.before(1), to: pos.after(1) },
      nodeType: { type: "heading", attrs: d1.attrs }, // level を保持
    };
  }

  // 引用 → blockquote の「中の paragraph」だけ（depth 2）を置換
  if (d1.type.name === "blockquote" && pos.depth >= 2) {
    return {
      replaceRange: { from: pos.before(2), to: pos.after(2) },
      nodeType: { type: "paragraph", attrs: {} },
    };
  }

  // リスト → listItem の「中の paragraph」だけ（depth 3）を置換
  if (
    (d1.type.name === "bulletList" || d1.type.name === "orderedList") &&
    pos.depth >= 3
  ) {
    return {
      replaceRange: { from: pos.before(3), to: pos.after(3) },
      nodeType: { type: "paragraph", attrs: {} },
    };
  }

  // 通常の段落など → depth 1 のブロック全体を置換
  return {
    replaceRange: { from: pos.before(1), to: pos.after(1) },
    nodeType: { type: d1.type.name, attrs: d1.attrs },
  };
}
```

肝は、**引用とリストでは「外側のラッパー」ではなく「内側の paragraph」を置換範囲にしている**ことです。

* 引用なら `pos.before(2)` 〜 `pos.after(2)`、つまり blockquote の中の paragraph（depth 2）の境界
* リストなら `pos.before(3)` 〜 `pos.after(3)`、つまり listItem の中の paragraph（depth 3）の境界

この範囲に対して中身を差し替えれば、**置換されるのは内側の paragraph だけ**で、外側の `<blockquote>` や `<ul>/<ol><li>` は範囲の外なのでそのまま残ります。「内側を指しているから維持される」のではなく、「**置換範囲を内側ノードの境界に設定しているから、外側が範囲外で残る**」というのが正確なところです。

なお見出しは、置換範囲を `heading` ノード全体にしつつ、`nodeType` に `attrs`（`level` を含む）を持たせています。これで H2 は H2、H3 は H3 のまま復元できます。

## 送信時にスナップショットを取る理由

`getEffectiveReplacement` で計算した範囲と型は、選択が変わるたびに更新される「いまの値」です。これをそのまま置換ボタンで使うと困ったことになります。

ユーザーは AI の提案を待っている間にも、カーソルを動かしたり別の場所をクリックしたりします。選択が外れた瞬間に範囲は `null` になるので、「置換ボタンを押した時点の値」を見にいくと、すでに範囲が消えていてズレる、という事故が起きます。

そこで、AI に送信したその瞬間の値を、メッセージ自身に保存します。

components/editor/AiPanel.tsx

```
interface AiMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  // 送信時にキャプチャ。ボタンは常にこの値で置換する
  savedRange: SelectionRange | null;
  savedSelectedText: string;
  savedNodeType: NodeTypeInfo | null;
}
```

送信時に `savedRange` / `savedNodeType` を確定させ、置換ボタンはこのスナップショットを使います。これで「提案を待っている間にカーソルを動かしても、ちゃんと元の場所が置き換わる」状態になります。

## ② ブロックタイプに応じて置換 HTML を組み立てる

置換は Tiptap の `insertContentAt({ from, to }, html)` で、保存しておいた `savedRange` に HTML を流し込みます。

このときの `html` を作るのが `buildReplacementHtml` です。ここで重要なのは、**分岐の大半はすでに `getEffectiveReplacement` の側で済んでいる**ことです。引用やリストは、あの時点で `nodeType` が `paragraph` に解決されています。なので HTML 生成側で特別扱いが要るのは、実質**見出しだけ**です。

components/editor/EditorShell.tsx

```
function buildReplacementHtml(text: string, nodeType: NodeTypeInfo | null): string {
  if (nodeType?.type === "heading") {
    const level = (nodeType.attrs.level as number) || 2;
    // 見出しは1行。AIが改行を返してきても潰す
    return `<h${level}>${text.replace(/\n+/g, " ").trim()}</h${level}>`;
  }
  // 段落（blockquote / list の中身を含む）はすべて <p>
  return wrapParagraphs(text);
}

function wrapParagraphs(text: string): string {
  return text
    .trim()
    .split(/\n\n+/)
    .map((p) => `<p>${p.replace(/\n/g, "<br>")}</p>`)
    .join("");
}
```

見出しは `<h{level}>` を明示的に出して H2 のまま戻す。引用やリストは `<p>` を差すだけ。置換範囲が内側 paragraph の境界に設定されているので、これだけで外側ラッパーは保持されます。

「H2 に相談したら H2 で返ってくる」「引用の中を直しても引用のまま」という地味な体験は、この**範囲計算（getEffectiveReplacement）と HTML 生成（buildReplacementHtml）の役割分担**で成り立っています。

## ストリーミング応答を「コメント」と「提案」に割る

実装上の工夫として、AI の応答を「観察コメント」と「提案本文」に分けています。

応答をそのまま全部置換に使うと、前置きのコメントまで本文に混ざってしまいます。そこで、サーバー側の system プロンプトで出力フォーマットを指定しています（つむぎは「批評せず観察する」という口調ルールも、ここで縛っています）。

```
（system プロンプトの該当部分・要約）
1〜2文の短い観察コメントの後に「---SUGGESTION---」を入れ、
そのあとに対象段落だけをリライトした文章を書く。
記事の他の部分は絶対に書かない。
```

クライアントは `---SUGGESTION---` で文字列を割って、前半をコメント、後半を提案として扱います。

components/editor/AiPanel.tsx

```
const SEPARATOR = "---SUGGESTION---";

function parseSuggestion(text: string): { comment: string; suggestion: string | null } {
  const idx = text.indexOf(SEPARATOR);
  if (idx === -1) {
    // ストリーミング途中で "---S..." まで来ている場合は、その断片を隠す
    const partial = text.match(/---S(?:UGGESTION?(?:---)?)?$/);
    return {
      comment: partial ? text.slice(0, partial.index).trimEnd() : text,
      suggestion: null,
    };
  }
  return {
    comment: text.slice(0, idx).trimEnd(),
    suggestion: text.slice(idx + SEPARATOR.length).trimStart(),
  };
}
```

地味ですが効いているのが、**ストリーミング中の「区切り文字の食べかけ」を隠す処理**です。`---SUGGESTION---` が1文字ずつ流れてくる途中だと `---SUG` のような中途半端な文字列がコメント末尾に見えてしまうので、正規表現で部分一致を検出して表示から除いています。tool\_use を使うほどでもない軽い分離は、これで十分でした。

なお、サーバー側は SSE ではなく、`messages.stream()` のテキストデルタを `ReadableStream` でそのまま `text/plain` として返しています。クライアントは `res.body.getReader()` で読むだけ。一方向にテキストを流すだけならこれが一番軽いです。

## おまけ：デュアル EditorBody 問題

選択範囲の置換とは別軸ですが、Tiptap を使っていて踏んだ罠をもう一つ共有します。

レスポンシブ対応で「デスクトップ用」「モバイル用」のレイアウトを出し分けたくなり、最初は CSS で書こうとしました。

```
// これがダメだった
<div className="hidden lg:flex"><EditorBody /></div>
<div className="lg:hidden"><EditorBody isMobile /></div>
```

CSS の `hidden` で隠しているだけなので、**React は両方の DOM をマウントします**。つまり Tiptap のインスタンスが2つ同時に走る。すると `onEditorReady` のようなコールバックが後勝ちで上書きされ、カーソル位置がズレる、片方の状態がもう片方に引っ張られる、といった事故が起きます。

解決策は、CSS ではなく **JS 側でブレークポイントを判定し、一度に1インスタンスしかマウントしない**ことです。

components/editor/EditorShell.tsx

```
const LG_BREAKPOINT = "(min-width: 1024px)";
const [isDesktop, setIsDesktop] = useState<boolean | null>(null);

useEffect(() => {
  const mq = window.matchMedia(LG_BREAKPOINT);
  setIsDesktop(mq.matches);
  const fn = (e: MediaQueryListEvent) => setIsDesktop(e.matches);
  mq.addEventListener("change", fn);
  return () => mq.removeEventListener("change", fn);
}, []);

// レンダリング
if (isDesktop === null) return <Spinner />;        // 初回判定前
return isDesktop
  ? <DesktopLayout />   // OutlinePanel + EditorBody + AiPanel の3カラム
  : <MobileLayout />;   // タブで body / outline / ai を切り替え
```

ポイントが2つあります。ひとつは `isDesktop` を `boolean | null` にして、**初回判定が終わるまで（null の間）はどちらも描画せずスピナーを出す**こと。これで「サーバー想定の初期値でいったんマウント → クライアントで切り替え」という二重マウントを避けられます。もうひとつは、デスクトップとモバイルで別物のコンポーネントを作るのではなく、**同じ `EditorBody` に `isMobile` を渡す**こと。エディタの実体は1つに保ちます。

「表示・非表示は CSS でやる」という普段の習慣が、Tiptap のような**生きたインスタンスを持つコンポーネント**では裏目に出る、という教訓でした。

つむぐには「既存の note 記事を読ませて、文体を解析する」機能もあります。ここは Claude API の **tool\_use** を使っています。出力を JSON Schema で縛ることで、手作業のパースを完全になくすのが狙いです。

app/api/style/analyze/route.ts

```
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const ANALYZE_TOOL: Anthropic.Tool = {
  name: "extract_style",
  description: "Extracts writing style from the given Japanese article text",
  input_schema: {
    type: "object" as const,
    properties: {
      tone: {
        type: "object",
        properties: {
          formality:   { type: "string", enum: ["casual", "neutral", "formal"] },
          humor:       { type: "string", enum: ["none", "light", "frequent"] },
          perspective: { type: "string", enum: ["first_person", "third_person", "mixed"] },
          enthusiasm:  { type: "string", enum: ["restrained", "moderate", "high"] },
          description: { type: "string", description: "50字以内で文体の特徴を日本語で説明" },
        },
        required: ["formality", "humor", "perspective", "enthusiasm", "description"],
      },
      // structure / vocabulary / noteSpecific も同様に enum で定義…
    },
    required: ["tone", "structure", "vocabulary", "noteSpecific"],
  },
};

const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  tools: [ANALYZE_TOOL],
  tool_choice: { type: "any" }, // 必ずツールを使わせる
  messages: [{ role: "user", content: `…記事本文…\n\nextract_styleツールを使って解析結果を返してください。` }],
});

const toolUse = message.content.find((c) => c.type === "tool_use");
if (!toolUse || toolUse.type !== "tool_use") {
  // ツールが呼ばれなかった場合のフォールバック
}
const style = toolUse.input; // 型に沿った構造化データ
```

ポイントは2つです。ひとつは `tool_choice: { type: "any" }` で、**必ずいずれかのツールを使わせる**こと。これがないと、Claude がツールを使わず普通の文章で返してくる可能性が残ります。もうひとつは、enum を使って**値の集合を固定する**こと。`formality` が `casual / neutral / formal` のどれかに必ず収まるので、受け取った後の値が予測でき、UI 側の出し分けが安定します。

「正規表現で解析する」「LLM の出力を信じて JSON.parse する」といった壊れやすい処理が要らなくなる。これは tool\_use（と OpenAI の function calling）の一番おいしいところだと思います。

## まとめ

つむぐの「選択範囲をブロックタイプ保持で置換する」機能を支えているのは、

* **選択時に `pos.before(n)` / `pos.after(n)` で「実効置換範囲」を計算する**（引用・リストは内側 paragraph の境界に設定して、外側ラッパーを範囲外に残す）
* **送信時にその範囲と型をスナップショットする**（待っている間にカーソルが動いてもズレない）
* **HTML 生成は見出しだけ特別扱い**にして、あとは `<p>` を差すだけ

という、どれも派手ではない役割分担です。でも、この積み重ねが「H2 に相談したら H2 で返ってくる」という当たり前を作ります。

次回は、つむぐのもう一つの軸である「**AI を黒子にする**」というデザイン思想と、それを体現したマスコット「つむぎ」の SVG 実装について書きます。技術というより設計・UI の話です。

---

筆者：宮川陽翔（[@haruto\_miyakawa](https://zenn.dev/haruto_miyakawa)）  
情報システムを学ぶ大学2年生。Next.js / TypeScript / Python と LLM を組み合わせた個人開発が中心です。
