---
id: "2026-03-18-webmcpのmodel-context-tool-inspectorをclaude-codeで動く-01"
title: "WebMCPのModel Context Tool InspectorをClaude Codeで動くようにした"
url: "https://zenn.dev/abalol/articles/9526128d199b80"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Gemini", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

## TL;DR

Google の [Model Context Tool Inspector](https://github.com/beaufortfrancois/model-context-tool-inspector) は WebMCP ツールのテスト用 Chrome 拡張ですが、AI 連携が Gemini API のみでした。Claude Code のサブスクで使えるように、ローカルの Go サーバー経由で `claude -p` を呼ぶ版を作りました。

<https://github.com/tomohiro-owada/webmcp-tool-inspector-with-claude>

## WebMCP とは

AI がスクレイピングや DOM 解析なしに Web ページを操作できるようにする仕組みです。サイト側が「このフォームにはこういう入力欄があって、こういう値を受け付ける」といった情報を構造化されたツールとして公開し、AI エージェントがそれを見て正しく操作できるようにします。Chrome 146 からアーリープレビューが始まっています。

詳しくは [W3C の提案](https://nicolo-ribaudo.github.io/webmcp/) や [Chrome の解説](https://developer.chrome.com/docs/ai/webmcp) を参照してください。

## 動機

Model Context Tool Inspector には「User Prompt」欄があり、自然言語で指示すると AI がツールを選んで実行してくれます。ただし **Gemini API キーが必要**です。

Claude Code のサブスク（Max プランなど）を持っていれば `claude -p` でプロンプトを実行できるので、これを使えばいいのでは？と思い作りました。

## 構成

```
ブラウザ (WebMCP ツール登録済みページ)
    ↕
Chrome 拡張 (サイドパネル)
    ↓ 自然言語の指示
    ↓ POST http://localhost:9111/prompt
Go Bridge Server
    ↓ claude -p --model haiku "プロンプト"
Claude Code
    ↓ {"tool": "fill-form", "args": {...}}
Chrome 拡張がツール実行
    ↓
ブラウザ (フォーム自動入力)
```

Go のワンバイナリで API サーバーを立て、Chrome 拡張の Gemini SDK 部分を `fetch` に差し替えただけです。

## 使い方

### 1. Bridge サーバー起動

```
cd bridge
go build -o webmcp-claude-bridge .
./webmcp-claude-bridge -model haiku
```

### 2. Chrome 拡張インストール

1. `chrome://flags#webmcp-for-testing` を有効化
2. `chrome://extensions` → デベロッパーモード ON
3. 「パッケージ化されていない拡張機能を読み込む」→ `chrome-extension/` を選択

### 3. 実行

WebMCP ツールが登録されたページでサイドパネルを開き、自然言語で指示するだけです。

## 変更点

オリジナルからの差分はほぼ `sidebar.js` だけです。

* Gemini SDK (`GoogleGenAI`) の import を削除
* `promptAI()` を `fetch` でローカル Bridge サーバーを呼ぶように書き換え
* API キー設定ボタンを Bridge URL 入力欄に変更
* モデルはサーバー起動時の `-model` フラグで指定（デフォルト: haiku）

## まとめ

WebMCP 自体がまだアーリープレビューなので実用段階ではありませんが、ツールの検証に Gemini API キーを用意しなくても Claude Code のサブスクだけで試せるようになりました。
