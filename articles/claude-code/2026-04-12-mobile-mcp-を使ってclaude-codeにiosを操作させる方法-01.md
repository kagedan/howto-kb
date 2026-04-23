---
id: "2026-04-12-mobile-mcp-を使ってclaude-codeにiosを操作させる方法-01"
title: "mobile-mcp を使ってClaude CodeにiOSを操作させる方法"
url: "https://zenn.dev/jboydev/articles/b7bfa15e3b2eeb"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## mobile-mcp とは？

一言で言うと、**AIにスマホを操作させるためのMCPサーバー**です。

通常、ClaudeなどのAIはテキストのやり取りしかできません。しかしこのMCPサーバーを使うと、AIが **iOSやAndroidのスマホ（実機・シミュレーター）を実際に操作できるようになります**。

例えばAIに対して「Safariでgoogleを開いて、AIのトレンド記事を検索して最初の記事にコメントして」と指示すると、AIが自分でアプリを開き、タップしたり文字を入力したりして、まるで人間がスマホを操作するように実行してくれます。

「**PCのブラウザ操作をAIにさせるツール（BrowserUseなど）のモバイル版**」というイメージが最も近いです。

主なユースケースは以下の3つです。

* **テスト自動化**：アプリのUI操作テストをAIに任せる
* **反復作業の自動化**：フォーム入力や定型的なアプリ操作をAIに実行させる
* **AIエージェントのモバイル拡張**：PCで動いているAIエージェントにスマホの操作も持たせる

---

## 前提条件

* **Node.js v22以上**
* **Xcode**（iOS向け、macOS必須）
* **Claude Code** または Claude Desktop などのMCP対応AIクライアント

---

## セットアップ手順（Claude Codeの場合）

### 1. MCPサーバーを登録する

ターミナルで以下のコマンドを1つ実行するだけです。ソースコードのビルドは不要です。

```
claude mcp add mobile-mcp -- npx -y @mobilenext/mobile-mcp@latest
```

### 2. iOSシミュレーターを起動する

```
# Xcodeがインストールされているか確認
xcode-select --version

# シミュレーターを起動（例：iPhone 16）
xcrun simctl boot "iPhone 16"

# シミュレーターアプリを画面に表示
open -a Simulator
```

### 3. Claude Codeで指示を出す

あとはClaude Codeのチャットで普通に日本語で指示するだけです。

```
iPhoneのシミュレーターでSafariを開いて、Googleで「東京の天気」を検索して
```

---

## セットアップ手順（Claude Desktopの場合）

### 設定ファイルの場所（Mac）

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

ターミナルで開く場合：

```
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 設定内容

以下のJSONを追加・保存します。

```
{
  "mcpServers": {
    "mobile-mcp": {
      "command": "npx",
      "args": ["-y", "@mobilenext/mobile-mcp@latest"]
    }
  }
}
```

設定後は **Claude Desktopを完全に終了して再起動**してください。チャット画面に🔨アイコンが表示されていればMCPが認識されています。

---

## 動作確認

まずデバイスが認識されているかを確認します。

問題なければスクリーンショットを撮って動作確認します。

```
iPhoneシミュレーターのスクリーンショットを撮って見せて
```

---

## AIへの上手な伝え方

### コツ：具体的に・目的ベースで書く

**悪い例**

**良い例**

```
[アプリ名] を起動して、ログイン画面でメールアドレスとパスワードを入力し、
ログインできることを確認して
```

### ユースケース別プロンプト例

**UIの確認**

```
[アプリ名]のトップ画面のスクリーンショットを撮って、ボタンやテキストに表示崩れがないか確認して
```

**機能テスト**

```
カート機能をテストして。商品を3つ追加し、合計金額が正しく表示されているか確認して
```

**エラー系のテスト**

```
ログイン画面で意図的に間違ったパスワードを入力して、エラーメッセージが適切に表示されるか確認して
```

**複数シナリオのまとめてテスト**

```
以下のシナリオを順番に全部テストして、各ステップの結果をまとめて報告して：
1. ログイン
2. 商品検索
3. カートに追加
4. ログアウト
```

---

## 参考リンク
