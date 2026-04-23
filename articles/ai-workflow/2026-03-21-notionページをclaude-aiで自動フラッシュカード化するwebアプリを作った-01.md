---
id: "2026-03-21-notionページをclaude-aiで自動フラッシュカード化するwebアプリを作った-01"
title: "NotionページをClaude AIで自動フラッシュカード化するWebアプリを作った"
url: "https://qiita.com/tai0921/items/55a60a0e403a5cf8ff9e"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## はじめに

**NotionページのURLを貼るだけで、Claude AIが自動でフラッシュカード（Q&A）を生成する** Webアプリを作りました。

工夫した点は **Notion → Claude → Notion の一気通貫フロー** です。

1. **Notion API** でページ本文（ブロック）を再帰的に取得
2. **Claude Opus 4.6** に送って問題・解説・難易度付きのカードを生成
3. 生成したカードを **Notionデータベース** に自動書き込み
4. ブラウザ上でカードをめくりながら自己評価（知ってた ✅ / 復習する 🔁）

---

## システム構成

```
ブラウザ (React + Vite, :5173)
  │
  └─ POST /api/generate
        │
        ├─ Notion API
        │     └─ ページID抽出 → ブロック再帰取得 → Markdownテキスト化
        │
        ├─ Claude API (Opus 4.6)
        │     └─ テキスト → フラッシュカード JSON (5〜15問)
        │
        └─ Notion API (書き込み)
              └─ フラッシュカードDBに1件ずつページ追加
```

| 項目 | 技術 |
| --- | --- |
| フロントエンド | React 18 + Vite + TypeScript |
| バックエンド | Express + TypeScript (tsx) |
| Notion連携 | @notionhq/client |
| AI | @anthropic-ai/sdk (Claude Opus 4.6) |
| スタイリング | CSS Modules |

---

## ファイル構成

```
pro_NotionFlashCard/
├── package.json               # npm workspaces
├── AGENTS.md                  # 環境変数・セットアップ手順
├── server/
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts           # Express サーバー本体
│       ├── lib/
│       │   ├── notion.ts      # Notionページ取得・テキスト変換
│       │   ├── claude.ts      # Claude APIでカード生成
│       │   └── notionWrite.ts # Notionデータベースへの書き込み
│       └── routes/
│           ├── generate.ts    # POST /api/generate
│           └── cards.ts       # GET /api/cards
└── client/
    ├── vite.config.ts         # /api → :3001 プロキシ設定
    └── src/
        ├── types.ts
        ├── App.tsx
        └── components/
            ├── GenerateForm.tsx   # URL入力フォーム
            └── CardViewer.tsx     # カードフリップUI
```

---

## 環境構築

### 1. リポジトリのセットアップ

```
git clone <repo>
cd pro_NotionFlashCard
npm install          # ルートと全ワークスペースを一括インストール
```

### 2. `.env` の設定

```
cp server/.env.example server/.env
```

```
# Notion Integration のシークレットキー
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Anthropic API キー
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxx

# フラッシュカードを保存するNotionデータベースのID（保存機能を使う場合）
NOTION_FLASHCARD_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Notion Integration の接続

1. [Notion My Integrations](https://www.notion.so/my-integrations) でIntegrationを作成
2. 読み込みたいNotionページを開き「…」→「接続を追加」でIntegrationを接続
3. フラッシュカード保存先のDBページにも同様に接続

### 4. 起動

```
npm run dev
# → http://localhost:5173 でアクセス
```

---

## 実装の詳細

### Notionページ取得：ブロックの再帰変換

Notion APIはページ本文を「ブロック」の木構造で返します。入れ子になったトグルやリストも含めて再帰的に取得し、Markdown文字列に変換しています。

```
// server/src/lib/notion.ts（抜粋）

async function blockToText(block: BlockObjectResponse): Promise<string> {
  const lines: string[] = [];

  switch (block.type) {
    case 'paragraph':
      lines.push(richTextToStr(block.paragraph.rich_text));
      break;
    case 'heading_1':
      lines.push(`# ${richTextToStr(block.heading_1.rich_text)}`);
      break;
    case 'bulleted_list_item':
      lines.push(`- ${richTextToStr(block.bulleted_list_item.rich_text)}`);
      break;
    case 'code':
      lines.push(`\`\`\`${block.code.language}\n${richTextToStr(block.code.rich_text)}\n\`\`\``);
      break;
    // heading_2, heading_3, numbered_list_item, to_do, quote, callout, toggle ...
  }

  // 子ブロックを再帰的に取得（トグル・コールアウト等）
  if ('has_children' in block && block.has_children) {
    const children = await notion.blocks.children.list({ block_id: block.id });
    for (const child of children.results) {
      const childText = await blockToText(child as BlockObjectResponse);
      if (childText) lines.push(childText);
    }
  }

  return lines.filter(Boolean).join('\n');
}
```

NotionページのURLからIDを抽出する処理も必要です。URLの形式は複数あるので正規表現で対応しています。

```
export function extractPageId(urlOrId: string): string {
  // https://www.notion.so/Title-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  const urlMatch = urlOrId.match(/([a-f0-9]{32})(?:[?#]|$)/i);
  if (urlMatch) return urlMatch[1];

  // ハイフン付きUUID形式
  const uuidMatch = urlOrId.match(
    /([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i
  );
  if (uuidMatch) return uuidMatch[1].replace(/-/g, '');

  return urlOrId.replace(/-/g, '');
}
```

### Claude APIでフラッシュカード生成

取得したMarkdownテキストをClaude Opus 4.6に渡し、JSON形式でカードを生成させます。

```
// server/src/lib/claude.ts（抜粋）

export async function generateCards(
  pageTitle: string,
  content: string
): Promise<Flashcard[]> {
  const prompt = `以下のNotionページの内容を読んで、学習に役立つフラッシュカードを5〜15問生成してください。

ページタイトル: ${pageTitle}

---
${content.slice(0, 8000)}
---

以下のJSON形式で回答してください（他のテキストは不要です）:
{
  "flashcards": [
    {
      "question": "概念・用語・仕組みを問う質問（1文）",
      "answer": "簡潔な解説（2〜3文）",
      "difficulty": "基礎 or 応用 or 発展"
    }
  ]
}`;

  const response = await client.messages.create({
    model: 'claude-opus-4-6',
    max_tokens: 4096,
    messages: [{ role: 'user', content: prompt }],
  });

  const textBlock = response.content.find((b) => b.type === 'text');
  const text = textBlock?.type === 'text' ? textBlock.text : '';

  // コードブロックで包まれていても対応
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  const parsed = JSON.parse(jsonMatch![0]) as { flashcards: Flashcard[] };
  return parsed.flashcards;
}
```

プロンプトのポイント：

* **「他のテキストは不要です」** と明示することで、JSONだけを返してもらいやすくなる
* レスポンス後に正規表現でJSON部分を抽出することで、コードブロックが混入しても壊れない
* コンテンツは8,000文字に切り詰めてトークン数を制御

### Notionデータベースへの書き込み

フラッシュカードのプロパティを定義したNotionデータベースに1件ずつページを追加します。

```
// server/src/lib/notionWrite.ts（抜粋）

export async function writeCardsToNotion(
  cards: Flashcard[],
  sourceUrl: string,
  dbId: string
): Promise<string[]> {
  const createdIds: string[] = [];

  for (const card of cards) {
    const page = await notion.pages.create({
      parent: { database_id: dbId },
      properties: {
        '問題':  { title:     [{ text: { content: card.question } }] },
        '解説':  { rich_text: [{ text: { content: card.answer } }] },
        '元ページ': { url:    sourceUrl },
        '難易度':  { select:  { name: card.difficulty } },
        '生成日':  { date:    { start: new Date().toISOString().split('T')[0] } },
      },
    });
    createdIds.push(page.id);
  }

  return createdIds;
}
```

### カードフリップUI

CSS transformのrotateYでカードをめくるアニメーションを実装しています。

```
// client/src/components/CardViewer.tsx（抜粋）

<div
  className={`${styles.cardWrapper} ${flipped ? styles.flipped : ''}`}
  onClick={handleFlip}
>
  <div className={styles.cardInner}>
    <div className={styles.cardFront}>
      <p className={styles.questionText}>{card.question}</p>
      <div className={styles.flipHint}>タップして答えを見る 👆</div>
    </div>
    <div className={styles.cardBack}>
      <p className={styles.answerText}>{card.answer}</p>
    </div>
  </div>
</div>
```

```
/* CardViewer.module.css（抜粋） */

.cardWrapper {
  perspective: 1000px;
}

.cardInner {
  transform-style: preserve-3d;
  transition: transform 0.5s ease;
}

.cardWrapper.flipped .cardInner {
  transform: rotateY(180deg);
}

.cardFront,
.cardBack {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
}

.cardBack {
  transform: rotateY(180deg);
}
```

`backface-visibility: hidden` で表裏それぞれ反対面を隠すのがポイントです。

---

## フラッシュカードデータベースのプロパティ構成

Notionデータベース側のプロパティは以下の5つです。

| プロパティ名 | 型 | 内容 |
| --- | --- | --- |
| 問題 | タイトル | カードの質問文 |
| 解説 | テキスト | 2〜3文の解説 |
| 元ページ | URL | 生成元NotionページのURL |
| 難易度 | セレクト | 基礎 / 応用 / 発展 |
| 生成日 | 日付 | 生成した日付 |

DBを手動で作る場合は上記のプロパティ名・型に合わせて作成してください。`notionWrite.ts` に `createFlashcardDatabase()` 関数も用意しており、親ページIDを渡すとプログラムからDBを作成することもできます。

---

## APIエンドポイント

### POST /api/generate

フラッシュカードを生成し、オプションでNotionに保存します。

```
// リクエスト
{
  "pageUrl": "https://www.notion.so/...",
  "saveToNotion": false
}

// レスポンス
{
  "success": true,
  "pageTitle": "TypeScriptの型システム入門",
  "pageUrl": "https://www.notion.so/...",
  "cards": [
    {
      "question": "TypeScriptにおける型推論とは何ですか？",
      "answer": "型推論とは、変数宣言時に型を明示しなくても、代入された値からTypeScriptが自動的に型を推定する機能です。例えば `const x = 42` と書くと、`x` は自動的に `number` 型として扱われます。",
      "difficulty": "基礎"
    }
  ],
  "savedCount": 0
}
```

### GET /api/cards

NotionデータベースのカードをJSON形式で返します。`NOTION_FLASHCARD_DB_ID` が必要です。

---

## 使ってみた感想

* **10〜20分かかっていた手動カード作成**が30秒程度になった
* Claude Opus 4.6の質問の質が高く、ピンポイントで重要な概念を突いてくる
* 難易度の自動分類が思ったより正確で、「発展」に分類されたものは確かに難しい
* Notionブロックの再帰取得で、トグル内の内容も漏れなく取得できるのが地味に重要だった

---

## まとめ

| ステップ | 実装のポイント |
| --- | --- |
| Notionページ取得 | ブロックを再帰的に走査してMarkdownに変換 |
| カード生成 | プロンプトでJSON出力を明示、正規表現でフォールバック |
| Notion書き込み | プロパティ名・型をDB設計と完全に一致させる |
| フリップUI | CSS `perspective` + `rotateY` + `backface-visibility` |

Notionで知識を蓄積している方は、ぜひ試してみてください。

---

## 参考
