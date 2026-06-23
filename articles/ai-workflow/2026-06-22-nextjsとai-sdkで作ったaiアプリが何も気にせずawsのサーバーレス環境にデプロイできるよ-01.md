---
id: "2026-06-22-nextjsとai-sdkで作ったaiアプリが何も気にせずawsのサーバーレス環境にデプロイできるよ-01"
title: "Next.jsとAI SDKで作ったAIアプリが何も気にせずAWSのサーバーレス環境にデプロイできるようになったぞ～Blocks最高～"
url: "https://qiita.com/moritalous/items/05b43a518b6ee86d977c"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "GPT", "TypeScript", "qiita"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

AWSが新しいOSSのBlocksを発表しました。

Blocksって何？ってのはすでに色んな方が発信されているのでそちらをご確認ください、

[https://www.google.com/search?q=aws+blocks](https://www.google.com/search?q=aws+blocks)

---

で、私は何をしたかというと、タイトルの通りです。

Blocks登場以前は

- SPAでフロントエンドから直接Bedrockを呼ぶ（個人的あまり好きではない）
- AmplifyのAI Kitを使う選択をし、AI SDKとかの市場のいけいけエコシステムを諦める
- Next.jsをAmplifyにデプロイするが、ストリーミング（ChatGPTみたいなカタカタするやつ）を我慢する
- Next.jsで構築しFargateにデプロイ（固定費がかかる）

などの方法が取れましたが、どれもイマイチでした。

Blocksにより

- **Next.jsで構築したアプリを特別な細工なくサーバーレス（API Gateway + Lambda）にデプロイ。ストリーミングも可！**

ができるようになりました。

悲願！！

:::note
ちなみに、今回紹介するのはBlocksのHostingコンポーネントだけを扱います。それ以外にも色々コンポーネントがあるようなので、チェックしてね。
:::

以前投稿した以下のチャットアプリを、2026/6版にアップデートしつつ、手順をご紹介！

https://qiita.com/moritalous/items/744b935a765f0621c881

## 手順（おしゃれチャットができるまで）

Next.jsプロジェクトを新規作成します。

```shell
npx create-next-app@16.2.9 chat-app-with-aws-blocks
```

ウィザードでは「Yes, use recommended defaults」を選びます。

```
❯   Yes, use recommended defaults - TypeScript, ESLint, No React Compiler, Tailwind CSS, No src/ directory, App Router, AGENTS.md
    No, reuse previous settings
    No, customize settings
```

続いて、AI Elementsを追加します。

```shell
cd chat-app-with-aws-blocks
npx ai-elements@1.9.0
```

ウィザードは言われるがままに進めます。
tooltipに関する内容を、言われた通り対応します。

```
✔ You need to create a components.json file to add components. Proceed? … yes
✔ Select a component library › Radix
✔ Which preset would you like to use? › Nova
✔ Preflight checks.
✔ Verifying framework. Found Next.js.
✔ Validating Tailwind CSS. Found v4.
✔ Validating import alias.
✔ Writing components.json.
✔ Checking registry.
✔ Installing dependencies.
✔ Updating fonts.
✔ Created 74 files:

✔ Updating app/globals.css
The `tooltip` component has been added. Remember to wrap your app with the `TooltipProvider` component.

The `tooltip` component has been added. Remember to wrap your app with the `TooltipProvider` component.

```tsx title="app/layout.tsx"
import { TooltipProvider } from "@/components/ui/tooltip"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <TooltipProvider>{children}</TooltipProvider>
      </body>
    </html>
  )
}
```

そして、AI SDKを追加します。

```shell
npm install ai@ai-v6 @ai-sdk/react@ai-v6 zod
```

AI SDKのプロバイダーも追加します。

2026年6月現在、Bedrockを使うならMantleがイケてるみたいなので、その方法を採用します。
    
:::note
Opusだけじゃなくて、Haiku 4.5もMantleに対応しています。Sonnetはまだいない😭😭😭
:::

MantleでAnthropicモデルを呼び出すには、BedrockプロバイダーではなくAnthropicプロバイダーを使用します。

```shell
npm install @ai-sdk/anthropic @aws-sdk/credential-providers @aws/bedrock-token-generator
```

準備が整ったので、実装していきます。まずはAPIから。

https://github.com/moritalous/chat-app-with-aws-blocks/blob/main/app/api/chat/route.ts

Anthropicプロバイダーを使う部分はこんな感じです。baseURLをMantleエンドポイントにし、APIキーを動的に生成するようにします。

```typescript
const tokenProvider = getTokenProvider({
  credentials: fromNodeProviderChain(),
  region: region,
});

const anthropic = createAnthropic({
  baseURL: `https://bedrock-mantle.${region}.api.aws/anthropic/v1`,
  apiKey: await tokenProvider(),
});
```
  

APIができたので、チャット画面を実装します。長いので、、見て！
    
https://github.com/moritalous/chat-app-with-aws-blocks/blob/main/app/page.tsx

これで完成です。`npm run dev`で確認しましょう。

![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/7fb1420b-04a1-4981-9281-ba33e301c519.png)

相変わらず、おしゃれなAI Elementsでございます。

これで、何の変哲もないNext.jsアプリができました。

## 手順（Blocksでデプロイ）

では、ここにBlocksを追加し、デプロイしましょう。

:::note warn
BlocksはまだGAではないので、いくつか対策をしながら進めます。楽しいからいいんですけどね
:::

1. Blocksを導入

```shell
npx @aws-blocks/create-blocks-app@0.1.3 .
```

「とりあえずエンター」を押すと、Abortされますので（笑）「Y」と入力して進めます。

```
🔍 Detected existing project (package.json found)

This will add AWS Blocks backend to your project:

  CREATE  aws-blocks/           (Blocks backend workspace)
  CREATE  cdk.json              (CDK configuration)
  MODIFY  package.json          (adds workspace, deps, scripts)
  MODIFY  .gitignore            (adds Blocks entries)

Proceed? (y/N) 
```
```
📦 Adding Blocks backend...

  ✓ Created aws-blocks/
  ✓ Created cdk.json
  ✓ Modified package.json
  ✓ Modified .gitignore

Installing dependencies...

added 137 packages, and audited 1203 packages in 28s

362 packages are looking for funding
  run `npm fund` for details

3 vulnerabilities (1 low, 2 moderate)

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.

✓ AWS Blocks backend added to your project!

Next steps:
  npm run sandbox         # Deploy backend to your AWS sandbox
  npm run dev:server      # Run local dev server

Import your API in frontend code:
  import { api } from 'aws-blocks'
```

Next.jsのサーバー側はLambdaにデプロイされます。このLambdaがBedrockのMantleエンドポイントを呼べるように権限を追加します。

```diff_typescript:aws-blocks/index.cdk.ts
  if (!sandboxMode) {
-   new Hosting(blocksStack, 'Hosting', {
+   const hosting = new Hosting(blocksStack, 'Hosting', {   
      root: join(__dirname, '..'),
      buildCommand: 'npm run build',
      buildOutputDir: 'dist',
      api: blocksStack
    });

+   hosting.ssrFunction?.addToRolePolicy(
+     new iam.PolicyStatement({
+       actions: ["bedrock-mantle:*"],
+       resources: ["*"],
+     }),
+   );   
  }
```


:::note warn
AI Elementsのバグ（？）なのか、このままではプロダクションビルドが通りません。

`components/ai-elements/schema-display.tsx`を以下のように修正します。

```diff
- dangerouslySetInnerHTML={{ __html: children ?? highlightedPath }}
+ dangerouslySetInnerHTML={{ __html: (children as string) ?? highlightedPath }}
```

とりあえずキャストして逃げ切りましょう。
:::


:::note warn
もう一つ修正が必要です。どうも、既存のNext.jsプロジェクトにBlocksを後から導入した際に、正しくNext.jsプロジェクトだと判定されず、問答無用でViteプロジェクト扱いになります。

`aws-blocks/scripts/server.ts`を一行修正します。

```diff_typescript
  startDevServer({
    backendPath: join(__dirname, '..', 'index.ts'),
-   frontendCommand: 'npx vite --port 3100 --strictPort',
+   frontendCommand: "npx next dev --port 3100",
    frontendPort: 3100,
  });
```

そして`aws-blocks/index.cdk.ts`も修正が必要です。

```diff_typescript:aws-blocks/index.cdk.ts
    const hosting = new Hosting(blocksStack, 'Hosting', {
      root: join(__dirname, '..'),
      buildCommand: 'npm run build',
-     buildOutputDir: 'dist',
      api: blocksStack
    });
```

困るので、PR上げてますので、いいネください！
https://github.com/aws-devtools-labs/aws-blocks/pull/65

:::

デプロイします。

```shell
npm run deploy
```

結構時間がかかります。30分ぐらい待ちましょう。

![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/dd0da300-a3e1-4e7d-8738-261a8f443c5e.png)

出ました！
Next.jsアプリ部分は全く改変してません。Blocksのなんやかんやはいじりましたが、そのうち治るでしょう。


そうだよ、これだよ。

AWSにデプロイする目的のためにアプリ側をひねるってナンセンスだよなーって思ってたんよ！

---


:::note warn
Blocksを追加したタイミングで、謎のTODOアプリの残骸も追加されます。APIやらなんやらがデプロイされいますので、消したほうが良さげです。

`aws-blocks/index.ts`をこうします。これ以外全部消してOKです。

```typescript
import { Scope } from '@aws-blocks/blocks';

new Scope('my-app');
```
:::

---

多分、Blocksの5%ぐらいしか旨味を味わってない気がしますが、満足です

GitHubにソース全部おいてますので、参考にしてください。

https://github.com/moritalous/chat-app-with-aws-blocks
