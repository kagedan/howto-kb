---
id: "2026-04-15-mastra-announce-studio-auth-デプロイ済み-studio-をチームで安全に-01"
title: "[Mastra Announce] Studio Auth — デプロイ済み Studio をチームで安全に使うための認証機能"
url: "https://zenn.dev/shiromizuj/articles/2a4f43b424e4b6"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

※やや昔のアナウンスをさかのぼって記事にしています

---

## 背景：Studio はローカルツールから「チームツール」へ

2026年3月17日 、Mastra は **Studio Auth**を発表しました。

Mastra Studio はもともと、ローカル開発環境でエージェントを試したりデバッグしたりするためのツールとして出発しました。`mastra dev` コマンドでローカル起動し、`localhost:4111` にアクセスするのが基本的な使い方です。

しかし 2026 年初頭に[Studio のデプロイ機能](https://mastra.ai/docs/deployment/studio)が整備され、状況が変わりました。`mastra studio` コマンドで単独サーバーとして起動したり、`mastra build --studio` で API サーバーと同梱デプロイしたりできるようになったのです。

**問題はセキュリティです**。URL を知っていれば誰でもアクセスできる状態で Studio を公開すると、エージェントの実行、ワークフローのトリガー、ツールの設定、可観測性データの閲覧——これらすべてが外部に露出することになります。これは Mastra のドキュメントでも明示的に警告されていたことです。

> Once Studio is connected to your Mastra server, it has full access to your agents, workflows, and tools. Be sure to secure it properly in production (e.g. behind authentication, VPN, etc.) to prevent unauthorized access.  
> — [Deploying Studio](https://mastra.ai/docs/deployment/studio)

これまではドキュメントに「認証や VPN で保護せよ」と書かれていましたが、具体的な仕組みは開発者自身で用意する必要がありました。今回の Studio Auth は、その「各自で用意せよ」だった部分をフレームワーク組み込みで解決するものです。

---

## これは新機能か？既存機能の拡充か？

この点を理解するには、**以前どうやって認証を実装していたか**を見るのが一番早いです。

### 以前の実装：`server.middleware` による手組みアプローチ

Studio のデプロイ機能が整備された後も、Mastra には Studio UI を守る専用の仕組みがありませんでした。API エンドポイントを保護したい場合は `server.middleware` に Hono の認証ミドルウェアを自前で書くことが一般的な手段でした。

Firebase を例にすると、こういった実装が必要でした：

```
// src/mastra/index.ts（以前の実装）
import admin from 'firebase-admin';
import type { Context, Next } from 'hono';

// Firebase Admin SDK を自前で初期化
const initializeFirebase = () => {
  if (admin.apps.length > 0) return;
  const projectId = process.env.FIREBASE_PROJECT_ID;
  const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;
  const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n');
  if (projectId && clientEmail && privateKey) {
    admin.initializeApp({ credential: admin.credential.cert({ projectId, clientEmail, privateKey }) });
  }
};

// 認証ミドルウェアを自前で実装
const authMiddleware = async (c: Context, next: Next) => {
  // 開発時スキップ用フラグも自前で実装する必要があった
  if (process.env.SKIP_AUTH === 'true') { await next(); return; }
  const authHeader = c.req.header('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return c.json({ error: 'Unauthorized' }, 401);
  }
  try {
    const decodedToken = await admin.auth().verifyIdToken(authHeader.substring(7));
    c.set('firebaseUser', { uid: decodedToken.uid, email: decodedToken.email });
    await next();
  } catch {
    return c.json({ error: 'Unauthorized: Invalid or expired token' }, 401);
  }
};

initializeFirebase();

export const mastra = new Mastra({
  // ...
  server: {
    middleware: [
      { handler: authMiddleware, path: '/api/*' }, // API だけを保護
    ],
  },
});
```

**この実装の限界は明確でした。**

1. **開発用トグルを自前で実装**。本来フレームワークが提供すべき「開発中は認証スキップ」の仕組みを `SKIP_AUTH=true` という環境変数で独自に実装する必要があった。
2. **コード量が多い**。Firebase Admin SDK の初期化、トークン検証、エラーハンドリング、ユーザー情報のコンテキスト設定——これら約 60 行を毎回書く必要があった。

### 今回の発表：`server.auth` によるファーストクラスな対応

今回の Studio Auth は同じ目的を達成しますが、アプローチが根本的に異なります。

```
// src/mastra/index.ts（Studio Auth 導入後）
import { MastraAuthWorkos } from "@mastra/auth-workos";

export const mastra = new Mastra({
  server: {
    auth: new MastraAuthWorkos({
      apiKey: process.env.WORKOS_API_KEY!,
      clientId: process.env.WORKOS_CLIENT_ID!,
      redirectUri: process.env.WORKOS_REDIRECT_URI!,
    }),
  },
});
```

`server.auth` に渡された設定は、API と Studio の両方に自動で適用されます。

|  | 以前（`server.middleware` 手組み） | 今回（`server.auth`） |
| --- | --- | --- |
| API エンドポイント保護 | ✅ ミドルウェアで可能 | ✅ 自動 |
| **Studio UI ログイン画面** | ❌ 効かない | ✅ 自動表示 |
| コード量 | 約 60 行（Firebase の場合） | 約 5 行 |
| 開発中のスキップ | 自前で `SKIP_AUTH=true` を実装 | フレームワークが管理 |
| RBAC（操作権限制御） | 実装不可（UI 側に手が届かない） | ✅ Enterprise 向けに提供 |

### まだ限られているプロバイダー

現時点で Studio UI との統合に対応しているのは **Simple Auth、JWT、WorkOS、Better Auth** の 4 つのみです。Firebase は `server.auth` プロバイダーとしてドキュメントに掲載があるものの、Studio UI 統合のサポートはまだ含まれていません。

### まとめ：どう位置づけるか

Changelog v1.11〜v1.13（2026年3月11〜13日）には Studio Auth の記述はなく、3月17日のアナウンスブログが初出です。ニュースリリースも「*That's why we built Studio auth*（だから Studio auth を構築した）」と**新規構築**を示す表現を使っています。

「API 認証にカスタムミドルウェアを使える」という下地は以前からありましたが、今回の発表はそれとは別物です。**Studio UI のログイン画面統合と RBAC は明確な新機能**であり、以前の手組みでは実現できなかったものが、設定数行で手に入るようになりました。

---

## ニュースリリースの内容紹介

### いつ・誰が・何を発表したか

* **発表日**: 2026年3月17日
* **著者**: Ryan Hansen（Software Engineer at Mastra）
* **発表内容**: デプロイ済み Mastra Studio に認証を設定し、チームで安全に使うための「Studio Auth」

### 発表内容の要点

1. **認証設定が API と Studio を同時に保護**: `server.auth` に auth プロバイダーを設定するだけで、API エンドポイントと Studio UI の両方がロックダウンされる
2. **サードパーティプロバイダーのサポート**: WorkOS、Better Auth、SimpleAuth に対応
3. **カスタムプロバイダー**: `MastraAuthProvider` を継承して独自プロバイダーを実装可能
4. **RBAC（ロールベースアクセス制御）**: Enterprise Edition 限定。ロールに応じて Studio 内での操作権限を細かく設定できる

---

## 具体的な掘り下げ

### 設定方法の基本

Mastra インスタンスの `server.auth` に auth プロバイダーを渡すだけで有効になります。

```
// src/mastra/index.ts
import { Mastra } from "@mastra/core";
import { MastraAuthWorkos } from "@mastra/auth-workos";

export const mastra = new Mastra({
  server: {
    auth: new MastraAuthWorkos({
      apiKey: process.env.WORKOS_API_KEY!,
      clientId: process.env.WORKOS_CLIENT_ID!,
      redirectUri: process.env.WORKOS_REDIRECT_URI!,
    }),
  },
});
```

これだけで：

* `/api/` 配下の全エンドポイントが認証必須になる
* Studio へのアクセス時にログイン画面が表示されるようになる

認証は**オプション**です。`server.auth` を設定しなければ、従来通りすべて公開のままです。

### 認証が通った後の Studio

ログイン後、チームメンバーは通常通り Studio を使えます。エージェントとのチャット、ワークフロー実行、可観測性トレースの確認など、開発時と同じ操作が可能です。

### RBAC でできること（Enterprise Edition）

認証（誰がアクセスできるか）の一段上に、**RBAC（何ができるか）** があります。

```
import { Mastra } from "@mastra/core";
import { MastraAuthWorkos } from "@mastra/auth-workos";
import { StaticRBACProvider } from "@mastra/core/auth/ee";

export const mastra = new Mastra({
  server: {
    auth: new MastraAuthWorkos({ /* ... */ }),
    rbac: new StaticRBACProvider({
      roleMapping: {
        admin:  ["*"],                                              // 全操作可
        member: ["agents:read", "workflows:*", "tools:read", "tools:execute"],
        viewer: ["agents:read", "workflows:read"],                 // 読み取りのみ
      },
    }),
  },
});
```

WorkOS のダッシュボードなどでユーザーにロールを割り当てておくと、Mastra 側でそのロールを受け取ってアクセス制御が行われます。

RBAC は開発環境ではライセンスなしで試せますが、本番利用には Enterprise ライセンスが必要です。

### 実用的な使い分けシナリオ

| シナリオ | 推奨設定 |
| --- | --- |
| チーム内開発者が全操作可能 | 認証 + admin ロールのみ |
| PM・非エンジニアにトレース閲覧だけ許可 | 認証 + viewer ロールを追加 |
| 外部コントラクターに読み取り共有 | 認証 + viewer ロール |
| ステージング環境を VPN 不要でチームに開放 | 認証のみ（RBAC なし） |

### サポートされる auth プロバイダー（Studio UI 統合）

| プロバイダー | パッケージ | 主な特徴 |
| --- | --- | --- |
| WorkOS | `@mastra/auth-workos` | エンタープライズ SSO、SCIM、RBAC |
| Better Auth | `@mastra/auth-better-auth` | セルフホスト可能なオープンソース |
| SimpleAuth | 組み込み | トークン〜ユーザーマッピング、開発・API キーに最適 |
| JWT | 組み込み | HMAC 符号付き JWT 検証 |

カスタムプロバイダーを作る場合は `MastraAuthProvider` を継承し、`authenticateToken()` と `authorizeUser()` を実装します。

---

## まとめ

Studio Auth は「API 認証は使えたが Studio は野放し」だった状態を解消し、**一つの設定で API と Studio を同時に保護**できるようにした機能です。

従来の認証フレームワーク自体は既存でしたが、**Studio UI との統合という意味では今回の発表が初**であり、デプロイ済み Studio を本番運用するうえでの重要なセキュリティ基盤が整ったといえます。

RBAC は Enterprise 向けですが、認証そのものは無償で設定できるため、Studio を公開する予定のあるプロジェクトでは早めに auth 設定を入れておくことを強くお勧めします。

---

## 参考リンク
