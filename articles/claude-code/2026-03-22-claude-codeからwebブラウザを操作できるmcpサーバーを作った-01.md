---
id: "2026-03-22-claude-codeからwebブラウザを操作できるmcpサーバーを作った-01"
title: "Claude CodeからWebブラウザを操作できるMCPサーバーを作った"
url: "https://qiita.com/koyama-techno/items/8ae01a58f09d4a9d8183"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## なぜ作ったか

Claude Codeを使って開発していると、**Webサイトの動作確認やスクレイピングを自然言語で指示したい**場面が増えてきました。

例えば：

* 「Yahooでtechnosphereを検索して、公式サイトのスクリーンショットを撮って」
* 「Redmineにログインしてチケット一覧を確認して」
* 「このフォームに入力してsubmitして」

既存のブラウザ自動化ツールはスクリーンショットベースのものが多く、LLMが画像を解析する必要があるため**処理が遅く、トークンも消費**します。

そこで、**DOM構造を直接JSON形式で取得**し、LLMが効率的に操作できるMCPサーバーを作りました。

## 何ができるか

### スクリーンショットなしで高速にページ状態を取得

↓ JSON形式でページの構造を返す

```
{
  "url": "https://example.com/login",
  "title": "ログイン",
  "forms": [
    {
      "action": "/auth",
      "inputs": [
        { "name": "email", "type": "email", "selector": "#email" },
        { "name": "password", "type": "password", "selector": "#password" }
      ]
    }
  ],
  "links": [...],
  "buttons": [...]
}
```

LLMはこの情報を見て「#emailに入力して、#passwordに入力して、submitボタンをクリック」と判断できます。

### 利用可能なツール一覧

| カテゴリ | ツール | 説明 |
| --- | --- | --- |
| セッション | `browser_create_session` | ブラウザセッションを作成 |
| ナビゲーション | `browser_navigate` | URLに移動 |
| DOM検査 | `browser_get_state` | ページ状態を取得 |
| DOM検査 | `browser_query` | CSSセレクタで要素を検索 |
| DOM検査 | `browser_find_text` | テキストで要素を検索 |
| アクション | `browser_click` | 要素をクリック |
| アクション | `browser_fill` | 入力欄を埋める |
| アクション | `browser_type` | テキストを入力 |
| その他 | `browser_screenshot` | スクリーンショット（必要時のみ） |

## ユースケース：Webアプリ開発のテスト

このツールの主な目的は、**Webアプリケーション開発時のテスト**です。

### 1. 開発中の動作確認

コードを書いたら、Claude Codeにそのまま動作確認を依頼できます。

```
「ログイン画面を開いて、test@example.com / password123 でログインして、
ダッシュボードが表示されるか確認して」
```

わざわざブラウザを開いて手動で確認する必要がなくなります。

### 2. フォームのバリデーションテスト

```
「会員登録フォームで以下のパターンをテストして：
- メールアドレスを空にしてsubmit → エラーが出るか
- 無効なメールアドレス（test@）を入力 → エラーが出るか
- パスワードを5文字で入力 → 8文字以上のエラーが出るか」
```

LLMが各パターンを順番に試して、結果を報告してくれます。

### 3. 複数ページにまたがる操作テスト

```
「商品一覧ページから商品Aをカートに追加して、
カートページに移動して、数量を2に変更して、
合計金額が正しく計算されているか確認して」
```

E2Eテストのシナリオを自然言語で指示できます。

### 4. レスポンシブデザインの確認

```
「ビューポートを375x667に変更して、ハンバーガーメニューが表示されるか確認して」
```

### 5. エラーハンドリングの確認

```
「存在しない商品ID（/products/99999）にアクセスして、
404ページが正しく表示されるか確認して」
```

### 6. ログイン後の画面テスト

認証が必要なページも、ログイン操作から自動で行えます。

```
「管理画面にログインして、ユーザー一覧が表示されるか確認して、
新規ユーザー作成ボタンがあるかも確認して」
```

### なぜテストに便利なのか

| 従来の方法 | LLM Browser |
| --- | --- |
| テストコードを書く | 自然言語で指示 |
| セレクタを調べる | LLMが自動で特定 |
| 手動でブラウザ確認 | コマンドラインで完結 |
| スクショを目視確認 | DOM構造で判定 |

**テストコードを書くほどではないが、手動確認は面倒**という場面で特に有効です。

## 技術スタック

* **MCP (Model Context Protocol)**: Anthropicが提唱するLLMとツールの連携プロトコル
* **Playwright**: ブラウザ自動化ライブラリ
* **TypeScript**: 型安全な実装
* **Docker**: 環境を汚さずに実行

## インストール・使い方

### 方法1: Dockerで実行（推奨）

WSLやローカル環境を汚さずに実行できます。

```
git clone https://github.com/technosphere-koyama/llm-browser.git
cd llm-browser
docker build -t llm-browser:latest .
```

`~/.claude/settings.json` に追加:

```
{
  "mcpServers": {
    "llm-browser": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "llm-browser:latest"]
    }
  }
}
```

### 方法2: 直接実行

```
git clone https://github.com/technosphere-koyama/llm-browser.git
cd llm-browser
npm install
npx playwright install chromium
npm run build
```

`~/.claude/settings.json` に追加:

```
{
  "mcpServers": {
    "llm-browser": {
      "command": "node",
      "args": ["/path/to/llm-browser/dist/index.js"]
    }
  }
}
```

## Dockerで環境を汚さない

Playwrightは依存ライブラリが多く、ローカルにインストールすると環境が汚れがちです。

このプロジェクトでは**Playwright公式Dockerイメージ**をベースにすることで、WSL環境を一切汚さずに実行できます。

```
FROM mcr.microsoft.com/playwright:v1.58.2-noble

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

CMD ["node", "dist/index.js"]
```

MCPサーバーはstdin/stdoutで通信するため、`docker run -i` で実行します。

## 実際の動作例

### Yahoo検索 → サイト訪問 → スクリーンショット

Claude Codeに「Yahooでtechnosphereを検索して、公式サイトのスクリーンショットを撮って」と指示すると：

1. `browser_create_session` でブラウザ起動
2. `browser_navigate url="https://www.yahoo.co.jp/"` でYahooに移動
3. `browser_fill selector="input[name='p']" value="technosphere"` で検索ワード入力
4. `browser_press key="Enter"` で検索実行
5. `browser_get_state` で検索結果のリンクを取得
6. `browser_click` でテクノスフィアのリンクをクリック
7. `browser_screenshot` でスクリーンショット保存

### ログインが必要なサイトの操作

```
browser_create_session
browser_navigate url="https://example.com/login"
browser_get_state  # フォーム構造を確認
browser_fill selector="#username" value="user"
browser_fill selector="#password" value="pass"
browser_click selector="button[type='submit']"
browser_get_state  # ログイン後の状態を確認
```

## アーキテクチャ

```
src/
├── index.ts           # エントリポイント
├── mcp/
│   └── server.ts      # MCPサーバー実装
├── browser/
│   ├── manager.ts     # ブラウザセッション管理
│   ├── dom-extractor.ts # DOM構造抽出
│   └── actions.ts     # ブラウザアクション
└── types/
    └── index.ts       # 型定義
```

## まとめ

* **Claude CodeからWebブラウザを自然言語で操作**できるMCPサーバーを作りました
* **スクリーンショットなしでDOM構造を取得**するため、高速かつトークン効率が良い
* **Dockerで実行**することで、環境を汚さずに利用可能

GitHub: <https://github.com/technosphere-koyama/llm-browser>

ぜひ試してみてください！

## 参考
