---
id: "2026-05-22-claude-codeでサードパーティapiを使う設定方法base-urlとよくあるエラー-01"
title: "Claude CodeでサードパーティAPIを使う設定方法：Base URLとよくあるエラー"
url: "https://qiita.com/xujfcn/items/26e203ee2801fd347491"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "qiita"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

Claude CodeをサードパーティのAPIゲートウェイ経由で使うとき、いちばん間違いやすいのはBase URLです。

OpenAI互換SDKではよく次のようなURLを使います。

```text
https://example.com/v1
```

しかしClaude CodeはAnthropic API互換の設定になるため、`/v1` を付けないルートURLを指定するケースがあります。

Crazyrouterを例にすると：

```text
ANTHROPIC_BASE_URL=https://crazyrouter.com
ANTHROPIC_API_KEY=sk-your-key
```

ドキュメント入口：

https://docs.crazyrouter.com/en/introduction?utm_source=qiita&utm_medium=article&utm_campaign=docs_intro

Claude Code設定ページ：

https://docs.crazyrouter.com/en/integrations/claude-code?utm_source=qiita&utm_medium=article&utm_campaign=docs_intro

## 前提

- Node.js 18以上
- Claude Code CLI
- APIキー
- ターミナルで環境変数を設定できること

## macOS / Linuxでの設定

```bash
export ANTHROPIC_BASE_URL="https://crazyrouter.com"
export ANTHROPIC_API_KEY="sk-your-key"
```

中国向けルートを使う場合：

```bash
export ANTHROPIC_BASE_URL="https://cn.crazyrouter.com"
export ANTHROPIC_API_KEY="sk-your-key"
```

重要：`ANTHROPIC_BASE_URL` の末尾に `/v1` を付けません。

## 永続化する

毎回exportするのが面倒な場合は、シェル設定に追加します。

zshの場合：

```bash
echo 'export ANTHROPIC_BASE_URL="https://crazyrouter.com"' >> ~/.zshrc
echo 'export ANTHROPIC_API_KEY="sk-your-key"' >> ~/.zshrc
source ~/.zshrc
```

bashの場合：

```bash
echo 'export ANTHROPIC_BASE_URL="https://crazyrouter.com"' >> ~/.bashrc
echo 'export ANTHROPIC_API_KEY="sk-your-key"' >> ~/.bashrc
source ~/.bashrc
```

## Windows PowerShell

```powershell
setx ANTHROPIC_BASE_URL "https://crazyrouter.com"
setx ANTHROPIC_API_KEY "sk-your-key"
```

新しいPowerShellを開いて反映を確認します。

```powershell
echo $env:ANTHROPIC_BASE_URL
echo $env:ANTHROPIC_API_KEY
```

## 動作確認

プロジェクトディレクトリでClaude Codeを起動します。

```bash
cd your-project
claude
```

最初は小さな質問で確認するのがおすすめです。

```text
このリポジトリの構成を簡単に説明してください。
```

いきなり大きな編集を頼むより、まずAPI接続とモデル応答を確認します。

## よくあるエラー

### 1. 404 または endpoint not found

Base URLに `/v1` を付けている可能性があります。

NG：

```text
ANTHROPIC_BASE_URL=https://crazyrouter.com/v1
```

OK：

```text
ANTHROPIC_BASE_URL=https://crazyrouter.com
```

### 2. Unauthorized

APIキーが違う、期限切れ、または環境変数が反映されていない可能性があります。

```bash
echo $ANTHROPIC_API_KEY
```

キーをログやGitに残さないよう注意してください。

### 3. 以前の設定が残っている

複数の設定ファイルやシェルに別の環境変数が残っていると、意図しない接続先に飛ぶことがあります。

```bash
env | grep -i anthropic
```

で確認できます。

## OpenAI互換SDKとの違い

同じCrazyrouterでも、OpenAI互換SDKでは通常：

```text
https://crazyrouter.com/v1
```

Claude Codeでは：

```text
https://crazyrouter.com
```

この違いを覚えておくだけで、かなりの設定ミスを避けられます。

## まとめ

Claude CodeでサードパーティAPIを使う場合は、通常のOpenAI SDK設定をそのまま流用しないほうが安全です。

チェックポイント：

- `ANTHROPIC_BASE_URL` はルートURL
- `/v1` を付けない
- APIキーは環境変数で管理
- まず小さい質問で動作確認
- ツール別ドキュメントを読む

CrazyrouterのClaude Code設定はこちら：

https://docs.crazyrouter.com/en/integrations/claude-code?utm_source=qiita&utm_medium=article&utm_campaign=docs_intro
