---
id: "2026-06-22-mastra-ollama-でご当地グルメ回答aiエージェントを作るハンズオンapiキー不要完全ロー-01"
title: "Mastra × Ollama でご当地グルメ回答AIエージェントを作るハンズオン【APIキー不要・完全ローカル・無料】"
url: "https://zenn.dev/fuqda/articles/f160e323d9ed27"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "OpenAI", "Gemini", "TypeScript"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

今回はローカル環境で動かせるLLMのOllamaを使って、TypeScript製AIエージェント開発フレームワークのMastraを動かしてみます。  
AI関連のトピックに乗り遅れ気味の私のような方でも楽しめるように書きましたので、最後までお付き合いください。

## この記事の対象読者

* Macユーザーの方
* 何らかのプログラミング言語で簡単なアプリケーションを作ったことがある方
* サクッとローカルで動くLLMを試してみたい方

## Ollamaとは？🐑

※説明不要な方は飛ばしてOK🙆

アメリカ発のオープンソースツールでLlamaやMistralなどのLLMをローカル環境で簡単に実行するためのランタイム・管理ツールです。  
APIキー流出などの従量課金が不安な方でも安心して利用できるため、手軽に試して遊ぶにはもってこいですね。

<https://ollama.com/>

## Mastraとは？🤖

※説明不要な方は飛ばしてOK🙆

AIエージェントを作るのはもちろん、LLMを使ったアプリケーションを作るためのバックエンドフレームワークです。  
「天気APIを叩く」「DBを検索する」といった業務に必要なツールを定義して、それを動かす頭脳としてモデルを接続することで、特定の業務を自律的にこなすエージェントを組み立てられます。  
今日はそのMastraを使って、ツールを定義してエージェントが実際に動く体験をしていきます。

<https://mastra.ai/>

## 作るもの

「〇〇のグルメを教えて」と日本各地の地名を入力してご当地グルメを回答してくれるAIエージェントを作成します。  
なお、今回は無料・APIキー不要・完全ローカルでやっていきます 🔧

![](https://static.zenn.studio/user-upload/a13a5250bdea-20260609.png)

## 手順1. Ollamaのセットアップ

※curlでインストールするパターンとGUI上でダウンロードするパターンがありますが、今回はcurlのパターンでやっていきます。

```
curl -fsSL https://ollama.com/install.sh | sh
```

※AIモデルのインストールには4.7GBほど容量が必要  
以下のコマンドでOllama公式のAIモデルをローカルにインストールできます。  
今回はAlibabaが公式にメンテしている `qwen2.5` を使います。

🐑 どんなモデルがあるかは公式をチェック 🐑  
↓↓↓

<https://ollama.com/search>

### なぜ qwen2.5 を使うのか 🤔

`Function Calling` (モデルに与えられた要求に対してどういった処理を呼び出すべきかJSON形式で回答できる仕組み)に対応していることやAlibabaが公式にメンテしていて、信頼性が一定あること、そして比較的軽量かつ日本語に対する精度が高く応答にクセが少ないため選びました。  
(余談ですが、 `qwen3:8b` だとエラーが発生していない正常なレスポンスでも、応答のたびに「申し訳ありません...期待通りの結果を取得できませんでした」のような謝罪から始まってしまいノイズが多い印象でした)

この時点だと `Function Calling` が特になんのこっちゃわからん。。。だと思いますが、一旦そういうもんなのねという理解で大丈夫です 🙆

※Ollamaの公式サイトで `tools` と記載があるモデルはそれに対応しています  
![](https://static.zenn.studio/user-upload/4ff4e63c08e2-20260606.png)

はじめにMeta製のAIモデルの `llama3.2` を試しましたが、とんでもないことに...  
`Function Calling` には対応しているものの、日本語への対応が弱くとんでもないハルシネーションが発生しました 😇  
(具体例は割愛しますが、コンテキストをかなり明確にしないと厳しそうでした...)

## 手順2. Mastraのプロジェクト作成

※Node.jsは入っている前提で進めます

<https://mastra.ai/docs>

pnpmでプロジェクトを作成していますが、パッケージマネージャーはお好みでどうぞ。

`pnpm create mastra プロジェクト名` 以降は以下の通り、選択して頂ければ大丈夫です。  
ちなみにプロバイダーは後ほど上書きするので、一旦OpenAIでOKです。

```
pnpm create mastra local-gourmet-agent
┌   Mastra Create 
│
◇  Select a default provider:
│  OpenAI
│
◇  Enter your OpenAI API key?
│  Skip for now
│
◇  Enable Mastra Observability? (will open auth flow)
│  No
│
◇  Configure Mastra tooling for agents?
│  Skills
│
◇  Select your agent:
│  Universal (Codex, Cursor, Gemini, GitHub, OpenCode)
│
◇  Initialize a new git repository?
│  Yes
│
◇  Project structure created
│
◇  pnpm dependencies installed
│
◇  Mastra CLI installed
│
◇  Mastra dependencies installed
│
◇  .gitignore added
│
└  Project created successfully

│
◇  Mastra initialized
│
◇  Mastra agent skills installed (in Universal)
│
◇  Git repository initialized
│
◇   ───────────────────────────────────────╮
│                                          │
│                                          │
│        Mastra initialized successfully!  │
│                                          │
│        Rename .env.example to .env       │
│        and add your OPENAI_API_KEY       │
│                                          │
│                                          │
├──────────────────────────────────────────╯
│
└  
   To start your project:

    cd local-gourmet-agent
    pnpm run dev
```

## 手順3. 依存パッケージのインストール

* `ollama-ai-provider-v2` ： Ollama専用のAIプロバイダーで設定がシンプル

※ `dotenv` は Mastraにデフォルトで含まれているのでインストール不要なようです

```
pnpm add ollama-ai-provider-v2
```

## 手順4. `.env` の設定

```
OLLAMA_BASE_URL=http://localhost:11434/api
OLLAMA_MODEL=qwen2.5:7b
```

## 手順5. 指定した地名のご当地グルメ情報をWikipediaから取得するツールを実装

`src/mastra/tools/search-gourmet-tool.ts`

```
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

export const searchGourmetTool = createTool({
  id: 'search-gourmet',
  description: '指定した地名のご当地グルメ情報をWikipediaから取得する',
  inputSchema: z.object({
    location: z.string().describe('検索する地名（例：大阪、札幌、福岡）'),
  }),
  outputSchema: z.object({
    results: z.string(),
  }),
  execute: async ({ context }) => {
    const { location } = context;

    // ① 検索ワードで記事タイトルを探す
    const searchUrl = new URL('https://ja.wikipedia.org/w/api.php');
    searchUrl.searchParams.set('action', 'search');
    searchUrl.searchParams.set('list', 'search');
    searchUrl.searchParams.set('srsearch', `${location}の料理 OR ${location}グルメ OR ${location}名物`);
    searchUrl.searchParams.set('srlimit', '3');
    searchUrl.searchParams.set('format', 'json');
    searchUrl.searchParams.set('origin', '*');

    const searchRes = await fetch(searchUrl.toString());
    const searchData = await searchRes.json();
    const hits = searchData.query?.search ?? [];

    if (hits.length === 0) {
      return { results: `${location}のグルメ情報が見つかりませんでした。` };
    }

    // ② ヒットした記事の本文冒頭（extract）を取得
    const titles = hits.map((h: any) => h.title).join('|');
    const extractUrl = new URL('https://ja.wikipedia.org/w/api.php');
    extractUrl.searchParams.set('action', 'query');
    extractUrl.searchParams.set('prop', 'extracts');
    extractUrl.searchParams.set('exintro', 'true');    // 冒頭のみ
    extractUrl.searchParams.set('explaintext', 'true'); // HTMLタグを除去
    extractUrl.searchParams.set('exsentences', '8');   // 最大8文
    extractUrl.searchParams.set('titles', titles);
    extractUrl.searchParams.set('format', 'json');
    extractUrl.searchParams.set('origin', '*');

    const extractRes = await fetch(extractUrl.toString());
    const extractData = await extractRes.json();
    const pages = Object.values(extractData.query?.pages ?? {}) as any[];

    const results = pages
      .filter((p) => p.extract)
      .map((p) => `【${p.title}】\n${p.extract.trim()}`)
      .join('\n\n');

    return { results: results || `${location}の詳細情報が取得できませんでした。` };
  },
});
```

createTool の inputSchema に Zod スキーマを渡すと、LLMが引数を自動で型付き生成します。

## 手順6. エージェント実装

`src/mastra/agents/local-gourmet-agent.ts`

```
import { Memory } from '@mastra/memory';
import { Agent } from '@mastra/core/agent';
import { createOllama } from 'ollama-ai-provider-v2';
import { searchGourmetTool } from '../tools/search-gourmet-tool';

const ollama = createOllama({
  baseURL: process.env.OLLAMA_BASE_URL ?? 'http://localhost:11434/api',
});

export const localGourmetAgent = new Agent({
  id: 'gourmet-agent',
  name: 'ご当地グルメエージェント',
  instructions: `
    あなたは日本全国のご当地グルメに詳しい食の専門家です。
    必ず日本語のみで回答してください。
    ツールの呼び出し結果に関わらず、エラーが発生したという前置きは絶対につけないでください。
    地名を受け取ったら、search-gourmetツールを1回だけ呼び出してください。
    ツールを呼び出さずに回答することは禁止です。
    代表的なご当地グルメ3〜5品を説明付きで回答してください。
  `,
  model: ollama(process.env.OLLAMA_MODEL ?? 'qwen2.5:7b'),
  tools: { searchGourmetTool },
  memory: new Memory(),
});
```

`memory: new Memory(),` という部分があることでスレッド内のやりとりを `mastra.db` に保存します。デフォルトで直近40メッセージをコンテキストに含めます。  
ちなみに一回でもチャットに入力すると `/src/mastra/public` に `mastra.db` というファイルが生成されます。

## 手順7. Mastra本体にご当地グルメ回答エージェントを登録

`src/mastra/index.ts`

```
import { Mastra } from '@mastra/core/mastra';
import { PinoLogger } from '@mastra/loggers';
import { LibSQLStore } from '@mastra/libsql';
import { localGourmetAgent } from './agents/local-gourmet-agent';

export const mastra = new Mastra({
  agents: { localGourmetAgent },
  storage: new LibSQLStore({ id: 'mastra', url: 'file:./mastra.db' }),
  logger: new PinoLogger({ name: 'Mastra', level: 'info' }),
});
```

#### 📝 完成版ディレクトリ構成

```
local-gourmet-agent/
├── src/
│ └── mastra/
│ ├── index.ts # Mastra 本体
│ ├── agents/
│ │ └── local-gourmet-agent.ts # エージェント定義
│ └── tools/
│   └── search-gourmet-tool.ts # ツール定義
├── .env
└── package.json
```

## 手順8. 動作確認

サーバーを起動して動作確認していきます。

<http://localhost:4111/agents>

![](https://static.zenn.studio/user-upload/8672a5010c0a-20260622.png)

### Playground のチャットで動作確認

✓ ブラウザで <http://localhost:4111> を開く  
✓ 左メニュー「Agents」→「ご当地グルメエージェント」をクリック  
✓ 「Select Model」横のボタン押下→「Chat Method」を Generate に変更

![](https://static.zenn.studio/user-upload/e97551f80308-20260622.png)

✓ チャット欄に「大阪のご当地グルメを教えて」など入力して送信

※その他入力例

```
「福岡のおすすめグルメを紹介して」
「北海道に旅行するのでおすすめ料理を教えて」
「沖縄名物を全部教えて」
```

`大阪の代表的な郷土料理の一つで、小麦 Flourと油 Frying Oilを使った円形のパンケーキ Pancake です。`といった感じでローカルLLMらしい微笑ましいハルシネーション（誤答）も見られますが、ツール呼び出し自体は成功していますwww

![](https://static.zenn.studio/user-upload/04d9634810a3-20260622.png)

## 終わりに

さて、いかがだったでしょうか。  
個人的にレスポンスが正しいのにAIからのテキストが失敗した前提のテキストになってしまったり、中国語と日本語が混在したりなど、試したモデルによってはうまくいかず試行錯誤しましたが、久しぶりの自由研究ができて楽しかったです。

まだここでは試せていないモデルが公式サイトには沢山記載ありましたので、興味ある方はぜひチェックして見てください。  
最後までお読みくださり、ありがとうございました 🙏  
<https://ollama.com/search>

<https://docs.ollama.com/>
