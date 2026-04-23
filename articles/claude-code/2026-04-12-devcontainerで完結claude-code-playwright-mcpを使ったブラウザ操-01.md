---
id: "2026-04-12-devcontainerで完結claude-code-playwright-mcpを使ったブラウザ操-01"
title: "DevContainerで完結！Claude Code + Playwright MCPを使ったブラウザ操作自動化の構築手順"
url: "https://zenn.dev/secondselection/articles/claude_playwright"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

**Claude Code + Playwright MCP**を使うと、自然言語でブラウザを操作し、その操作をそのままRPAスクリプトとして自動生成できます。  
イメージとしては、RPAのコードをClaude Codeに作らせるイメージです。  
Playwrightの知識がなくても、操作を見せるだけでスクリプトを作れる点が最大のメリットです。

本記事では、この環境をDevContainer内で完結させる構築手順をまとめます。  
動作確認として、NotebookLMのソース同期を自動化した例も紹介します。

## Playwright とは

Microsoftが開発したオープンソースのブラウザ自動化フレームワークです。

| 項目 | 内容 |
| --- | --- |
| 対応ブラウザ | Chromium（Chrome/Edge）、Firefox、WebKit（Safari） |
| 対応言語 | JavaScript/TypeScript、Python、Java、.NET |
| 主な用途 | E2E テスト、Web スクレイピング、業務自動化 |

**Auto-wait 機能**が最大の特徴で、操作対象の要素が準備完了になるまで自動的に待機します。  
これにより、タイミング問題による操作の不安定さを大幅に削減できます。

## Playwright MCP とは

`@playwright/mcp`として提供されるMicrosoft公式のMCPサーバーです。  
Claude CodeなどのAIエージェントがPlaywrightのブラウザ操作機能を直接呼び出せるようにします。

<https://github.com/microsoft/playwright-mcp>

## システムイメージ

ClaudeがMCPサーバーを介してクリック等のPlaywright機能を利用するイメージです。  
MCPサーバーとして提供されていることで、AIはPlaywrightのAPIを直接書くことなく、ツール名とパラメータを指定するだけでブラウザ操作ができます。

![ClaudeがMCPサーバーを介してPlaywrightを操作するシステムイメージ](https://static.zenn.studio/user-upload/deployed-images/d7ae42a53526591d67bcb562.png?sha=7dc38b09492d70861f9376c1af9e8f3ade909f50)

## 環境構成

ブラウザ(Chrome)にて動作確認しながら進めたかったため、**コンテナ内に仮想デスクトップ（Xvfb + noVNC）を立てて、ブラウザから画面を確認する**方式を採用します。  
※今回はDevContainerを利用しましたが、通常のDockerコンテナでも同じ環境は作れます。

```
WSL
└── devcontainer
    ├── Playwright MCP サーバー（npx）
    ├── 仮想デスクトップ（Xvfb + noVNC）
    └── Claude Code
         ↓ ブラウザ操作
Windows ブラウザ → localhost:6080 で画面確認
```

### 構成のメリット

* Claudeと対話形式でブラウザ操作をさせる、操作状態も確認できる
* コンテナ内で完結するため環境が汚れない
* `localhost:6080` をブラウザで開くだけで画面確認できる

## セットアップ手順

### Step 1: devcontainer.json を設定

仮想デスクトップにて確認をするため`desktop-lite`featureを追加し、ポート6080を転送します。

```
{
  "name": "Node.js with AI Tools",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:1-20-bullseye",
  "features": {
    "ghcr.io/devcontainers/features/common-utils:2": {
      "installZsh": "true",
      "configureZshAsDefaultShell": "true",
      "installCurl": "true",
      "upgradePackages": "false"
    },
    "ghcr.io/devcontainers/features/desktop-lite:1": {}
  },
  "forwardPorts": [6080],
  "postCreateCommand": "curl -fsSL https://claude.ai/install.sh | bash && npx playwright install --with-deps chromium && claude mcp add playwright npx @playwright/mcp@latest",
  "customizations": {
    "vscode": {
      "settings": {},
      "extensions": [
        "dbaeumer.vscode-eslint"
      ]
    }
  },
  "remoteUser": "node"
}
```

### Step 2: 動作確認

VSCode上でdevcontainer起動後、Claude Codeを用いて確認します。

`playwright` が `connected` で表示されれば設定完了です。

![Claude CodeでPlaywright MCPがconnected状態で表示されている様子](https://static.zenn.studio/user-upload/deployed-images/3949ebeb5ddebb4d99ede6d9.png?sha=41bb777106165992d2faaa84d002af2e5e5cc4a9)

### 活用例: NotebookLMのソース自動同期

ここからは実際にどんな操作を自動化するかを説明します。

NotebookLMはGoogleが提供するAIを活用したナレッジ管理ツールです。  
ソース(アップロードした資料)に更新があった際に手動で同期ボタンをクリックする必要があり、Notebookの数が増えるとメンテナンス負荷が増えます。

![NotebookLMのソース同期ボタン](https://static.zenn.studio/user-upload/deployed-images/e04a889b7361c4a3dca044a4.png?sha=f754f7fe1ebb20447e33da3e2951d672e1d0c261)

この同期作業をClaude Codeに指示しながら進め、最後にスクリプトとして書き出させます。

![スクリプトフロー](https://static.zenn.studio/user-upload/deployed-images/32635bc4e593e522ce0b137d.png?sha=f5790c32617a098266da12dd98730c394aab735d)

### Step 3: ブラウザで画面を開く

ブラウザで以下にアクセスします。

`http://localhost:6080`

仮想デスクトップが表示されます。Claude CodeからPlaywrightを操作すると、この画面でブラウザの動きを確認できます。接続をクリックしてください。

![noVNCの仮想デスクトップ画面（localhost:6080）](https://static.zenn.studio/user-upload/deployed-images/9de41af275fe1a3e4e6a363e.png?sha=15a614747f8768d8d1590ff5c04d976bc490b3db)

## ブラウザを操作させてみる

ここまでのセットアップが完了すると、あとはClaude Codeに自然言語で指示するだけでブラウザを操作できます。

以降プロンプトは🧑‍🦲マークを付与します。

`🧑‍🦲google.comを開いて`

![Claude CodeがPlaywrightでgoogle.comを開いた様子](https://static.zenn.studio/user-upload/deployed-images/5b94fdb54f8cbcb6ea64b2c6.png?sha=9e0dea132a1f9ab16f59392677c6aec4732528eb)

## NotebookLMの自動更新

実際にClaude Codeに指示して操作させます。

後ほどスクリプト作成用の実行手順を教えるためにスクショを取らせます。

`🧑‍🦲各操作をする度にスクショをして`

`🧑‍🦲NotebookLMを開いて`

サインインします。こちらは手動入力します。

![NotebookLMのサインイン画面](https://static.zenn.studio/user-upload/deployed-images/9960d9b9ea73e54b5c265719.png?sha=0998ec423fd9ef1298f9459b23d341e036a5a354)

サインインが完了するとNotebookLMにログインできます。  
サインイン後、ログインステータスを保存することで次回からのログインが省けますが、セキュリティにはご注意ください。

![サインイン後のNotebookLMトップ画面](https://static.zenn.studio/user-upload/deployed-images/58af953c0087ce6986618111.png?sha=5c7158ca72ba8c8e979409bfa6cc3ad787614a42)

自動更新させたいブックを開かせます。

`🧑‍🦲「The Japanese Test Document」のブックを開いて`

![「The Japanese Test Document」のNotebookを開いた画面](https://static.zenn.studio/user-upload/deployed-images/23c4eb93053a0758b810c9ce.png?sha=a8f88a1de5cb044a29f88e3d72d914f951b75796)

自動更新させたいソースを開かせます。

`🧑‍🦲ソース(テスト)をクリックして`

![ソース詳細を開いた画面](https://static.zenn.studio/user-upload/deployed-images/6b4aacfc42ef00d68a66812a.png?sha=907c0c8db34beafac53faf304a2e16623565413d)

`🧑‍🦲同期するをクリックして。`

![同期前のソース状態](https://static.zenn.studio/user-upload/deployed-images/1298977ff73689a242961d98.png?sha=b52672d053ba6612b18328e642e70ece5f013c19)  
![同期後のソース状態](https://static.zenn.studio/user-upload/deployed-images/d8826bea726269c0fe29dac7.png?sha=c08a969112f57499b7372ba6a50934eb57612076)

`🧑‍🦲ここまでの作業をPlaywrightを用いて自動化して`

すると自動更新のスクリプトが作成されますので、スクリプトを定期実行することで更新の手間が省けます。  
なお、生成されるスクリプトは正常系が中心のため、本番利用の際はエラーハンドリングを確認・追加することをおすすめします。  
実際にソースが更新されていないと同期ボタンが表示されず、エラーが発生しました。

## 生成されたスクリプト

```
const { chromium } = require('playwright');

async function syncNotebookLM() {
  console.log('ブラウザを起動中...');

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: false,
    args: ['--no-sandbox'],
  });

  const page = await browser.newPage();

  try {
    // 1. NotebookLM を開く
    console.log('NotebookLM を開いています...');
    await page.goto('https://notebooklm.google.com');

    // ログインが必要な場合は手動で待機
    if (page.url().includes('accounts.google.com')) {
      console.log('⚠️  ブラウザでGoogleアカウントにログインしてください。');
      console.log('ログイン完了後、自動的に続行します...');
      await page.waitForURL('https://notebooklm.google.com/**', { timeout: 120000 });
    }

    console.log('✅ NotebookLM を開きました');

    // 2. "The Japanese Test Document" をクリック
    console.log('"The Japanese Test Document" を開いています...');
    await page.goto('https://notebooklm.google.com/notebook/xxxx');
    await page.waitForLoadState('load');
    console.log('✅ ノートブックを開きました');

    // 3. 左側の「テスト」ソースをクリック
    console.log('「テスト」ソースを選択しています...');
    await page.getByRole('button', { name: 'テスト', exact: true }).waitFor({ timeout: 30000 });
    await page.getByRole('button', { name: 'テスト', exact: true }).click();
    await page.waitForTimeout(1000);
    console.log('✅ ソースを選択しました');

    // 4. 「クリックして Google ドライブと同期」をクリック
    console.log('Google ドライブと同期しています...');
    await page.waitForSelector('text=クリックして Google ドライブと同期', { timeout: 10000 });
    await page.click('text=クリックして Google ドライブと同期');

    // 同期完了を待機
    await page.waitForSelector('text=同期が完了しました', { timeout: 30000 });
    console.log('✅ 同期が完了しました！');

  } catch (err) {
    console.error('❌ エラーが発生しました:', err.message);
    console.log('現在のURL:', page.url());
    await page.screenshot({ path: 'debug_screenshot.png' });
    console.log('スクリーンショットを debug_screenshot.png に保存しました');
    process.exitCode = 1;
  } finally {
    await browser.close();
    console.log('ブラウザを閉じました。');
  }
}

syncNotebookLM();
```

## まとめ

Claude CodeとPlaywright MCPを利用することでNotebookLMを自動更新できることを確認しました。  
この構成の活用方法として、**まずClaudeに自然言語で操作させてRPAスクリプトを自動生成し、それを定期実行する**という流れが有効です。Playwrightの知識がなくても、操作を見せるだけでスクリプトを作れるため、非エンジニア職の方にも有効と言えるでしょう。

![同期後のソース状態](https://static.zenn.studio/user-upload/deployed-images/156cceeed9f04ad35a9d6db2.png?sha=6f33d8a1d2cc0685b43b4361a616ee887b33b4ec)
