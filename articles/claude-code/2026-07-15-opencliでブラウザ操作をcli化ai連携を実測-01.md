---
id: "2026-07-15-opencliでブラウザ操作をcli化ai連携を実測-01"
title: "OpenCLIでブラウザ操作をCLI化、AI連携を実測"
url: "https://zenn.dev/mskbhd/articles/lab-125-opencliwebcliai"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "GPT", "JavaScript", "zenn"]
date_published: "2026-07-15"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんな投稿が目に留まった。

> **OpenCLI — turns any website into a CLI tool your AI agent can use through your logged-in browser.**

「どんなWebサイトもCLIツールにして、AIエージェントが操作できるようにする」—— 26Kスターを獲得した **OpenCLI**（[https://github.com/jackwener/opencli）のコンセプトだ。](https://github.com/jackwener/opencli%EF%BC%89%E3%81%AE%E3%82%B3%E3%83%B3%E3%82%BB%E3%83%97%E3%83%88%E3%81%A0%E3%80%82)

> 従来のPlaywright/Puppeteer方式は**ヘッドレスブラウザを起動**して操作する。認証情報の管理、アンチボット検出の回避、複雑なセットアップが必要になる。
>
> OpenCLIは**既にログイン済みのChromeに拡張経由で接続**し、そのセッションをCLIから操作する。認証不要、ブラウザフィンガープリントはそのまま、セットアップは最小限。

「26Kスターを4ヶ月で獲得」——本当に使えるのか？ 実際にインストールして検証した。

## インストール

```
npm install -g @jackwener/opencli
```

Node.js >= 20 が必要。v1.8.6 がインストールされた。

```
opencli v1.8.6 doctor (node v26.4.0)
[OK] Daemon: running on port 19825 (v1.8.6)
[MISSING] Extension: not connected
[FAIL] Connectivity: failed
```

daemon は自動起動したが、**Browser Bridge 拡張**が Chrome にインストールされていないとログイン必須サイトは操作できない。拡張は Chrome Web Store からインストールできるが、今回は「拡張なしでどこまで動くか」も検証する。

## ブラウザ不要で動くアダプターを試す

まずは HackerNews のアダプターを叩いてみる。

```
opencli hackernews top --limit 3
```

**結果: 一瞬で動いた。**

```
- rank: 1
  title: Inkling: Our Open-Weights Model
  score: 351
  author: vimarsh6739
  comments: 91
  url: https://thinkingmachines.ai/...

- rank: 2
  title: Stripe and Advent have made a joint offer to acquire PayPal
  score: 235
  ...

- rank: 3
  title: Duskers, the scary command line game, is getting a sequel
  score: 54
  ...
```

HackerNews アダプターの中身を見ると：

```
// clis/hackernews/top.js
import { cli, Strategy } from '@jackwener/opencli/registry';
cli({
    site: 'hackernews',
    name: 'top',
    strategy: Strategy.PUBLIC,  // 公開API直叩き
    browser: false,             // ← ブラウザ不要！
    pipeline: [
        { fetch: { url: 'https://hacker-news.firebaseio.com/v0/topstories.json' } },
        { map: { id: '${{ item }}' } },
        { fetch: { url: 'https://hacker-news.firebaseio.com/v0/item/${{ item.id }}.json' } },
        { map: { rank: '${{ index + 1 }}', title: '${{ item.title }}', ... } },
        { limit: '${{ args.limit }}' },
    ],
});
```

`browser: false` のアダプターはサーバーサイドで直接 HTTP リクエストを発行する。ブラウザ操作が不要なので、**拡張がなくても、daemon すら不要で高速に動作する**。

`--format json / yaml / csv` も対応しているため、パイプで jq に流したりスプレッドシートに入れたりできる。

```
opencli hackernews top --limit 10 -f json | jq '.[] | {title, score}'
```

## ブラウザ必須のアダプターはどうか

ログイン必須なサイト（bilibili / Reddit / X(Twitter) など）のアダプターは Browser Bridge 拡張経由で実際の Chrome を操作する。bilibili のホット動画を取得しようとした：

```
opencli bilibili hot --limit 3 -f json
```

**結果: タイムアウト。** daemon が拡張からの応答を待ってハングした。拡張なしでは全く動作しない。

bilibili アダプターの中身を見ると：

```
pipeline: [
    { navigate: 'https://www.bilibili.com' },  // ブラウザでページを開く
    { evaluate: `fetch('https://api.bilibili.com/x/web-interface/popular?ps=...')` },
    { map: { ... } },
    { limit: '${{ args.limit }}' },
]
```

`navigate` → `evaluate(fetch(...))` の流れで、**実ブラウザ内で JavaScript を実行**してデータを取得している。これによりユーザーの Cookie やログインセッションをそのまま利用できる。つまり、認証情報を一切 CLI に渡さずにログイン必須サービスを操作できるという仕組みだ。

## アーキテクチャ理解

OpenCLI のアーキテクチャを図にするとこうなる。

```
opencli <site> <command>
       │
       ▼
  アダプター定義 (YAML/JS pipeline)
       │
       ├── browser: false ──→ fetch ステップ ──→ Node.js 内蔵 fetch
       │                      (HTTP API 直接)
       │
       └── browser: true  ──→ navigate/evaluate など
                              (パイプラインステップ)
                              │
                              ▼
                         Browser Bridge 拡張
                         (WebSocket over daemon:19825)
                              │
                              ▼
                         実 Chrome ブラウザ
                         (ログイン済みセッション)
```

登録されているアダプターは **176個**（`clis/` ディレクトリ内）。内訳は：

* **40+ の PUBLIC 戦略アダプター**: ブラウザ不要、API 直叩き（HackerNews / GitHub Trending / 天気 など）
* **残りの COOKIE / INTERCEPT 戦略アダプター**: ブラウザ必須（X(Twitter) / Reddit / bilibili / Amazon など）
* **Electron アプリアダプター**: Cursor / ChatGPT App / Discord など（CDP 接続）

## アダプターの拡張性

アダプターは自分でも作れる。

```
opencli browser init weather/current
# → ~/.opencli/clis/weather/current.js が生成
```

Pipeline DSL は以下のように宣言的：

```
pipeline: [
    { fetch: { url: 'https://wttr.in/${{ args.city }}?format=j1' } },
    { map: {
        location: '${{ args.city }}',
        condition: '${{ item.current_condition[0].weatherDesc[0].value }}',
        temp_c: '${{ item.current_condition[0].temp_C }}',
    } },
]
```

さらに `opencli plugin install github:user/repo` でプラグインとして配布も可能。実際にコミュニティプラグインが数件存在している。

## AI エージェント連携

6種類の skill が用意されている：

| Skill | 用途 |
| --- | --- |
| opencli-browser | ブラウザ操作全般（navigate/click/type/extract） |
| opencli-adapter-author | 新規アダプター作成 |
| opencli-autofix | 壊れたアダプターの修復 |
| opencli-browser-sitemap | サイトマップを活用したブラウザ操作 |
| opencli-sitemap-author | サイトマップ知識の記録 |
| opencli-usage | コマンドリファレンス |

インストールは `npx skills add jackwener/opencli` 一発。Claude Code や Cursor にスキルとして追加できる。

## 所感と評価

### 良かった点

1. **npm install 一発でセットアップ完了**。daemon も自動起動。Node.js のみで動く軽量設計。
2. **ブラウザ不要アダプターは爆速**。API 直叩きで拡張なしでも使える。既に 40 サイト以上カバー。
3. **ログイン必須サイトも「拡張インストール＋daemon起動」でワンステップ**。認証情報を CLI に預ける必要がないのはセキュリティ面で大きな利点。
4. **アダプター作成が簡単**。Pipeline DSL は YAML ライクで直感的。`browser init` で雛形生成もできる。

### 気になった点

1. **拡張なしではログイン必須サイトにアクセスできない**。当たり前だが、全ての価値は Browser Bridge 拡張に依存している。
2. **CDP の直接接続が Electron アプリ限定**。既に Chrome が --remote-debugging-port=9222 で動いていても、通常の Web サイトのブラウザ操作には使えない設計。拡張経由が唯一の接続経路。
3. **拡張のインストールは Chrome 依存**。Firefox/Safari では使えない（Chrome/Edge/Chromium 系のみ）。

### 結論

> **OpenCLI は「ログイン済みブラウザセッションを CLI から操作する」というシンプルな発想を、堅牢なアーキテクチャで実装したツール。**
>
> ブラウザ不要の PUBLIC アダプターは拡張なしで即座に使える。ログイン必須サイトも拡張を入れるだけで連携可能。26K スターは伊達ではなかった。
>
> ただし、全ての価値が Chrome 拡張＋daemon のアーキテクチャに依存しているため、導入時には拡張のインストールが不可避。その一点を許容できるなら、AI エージェントにブラウザ操作を任せる強力な手段になる。

## 補足

* 本検証は Chrome 149、OpenCLI v1.8.6 で実施
* Browser Bridge 拡張のインストールはシステム設定変更になるため未実施
* AI エージェント（Claude Code/Cursor）との実連携テストはスコープ外
* ソースコード分析は npm インストール先の dist/ を参照
