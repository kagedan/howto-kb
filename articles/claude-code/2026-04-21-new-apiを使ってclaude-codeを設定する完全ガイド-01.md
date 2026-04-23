---
id: "2026-04-21-new-apiを使ってclaude-codeを設定する完全ガイド-01"
title: "New APIを使ってClaude Codeを設定する完全ガイド"
url: "https://qiita.com/ai-8tb-cc/items/d4aa9c39d76868e2b062"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

> **New API**（ai.8tb.cc）はAnthropicの公式APIと完全互換のエンドポイントを提供しています。Base URLとAPI Keyを置き換えるだけで、Claude Codeですぐに使い始めることができます。

## 前提条件

* Claude Codeがインストール済み（`npm install -g @anthropic-ai/claude-code`）
* [ai.8tb.cc](https://ai.8tb.cc) でアカウントを作成し、API Keyを取得済み

---

## 方法1：環境変数（推奨）

最もシンプルな方法で、すべてのOSに対応しています。

### macOS / Linux

ターミナルで以下を実行：

```
export ANTHROPIC_BASE_URL=https://api.8tb.cc/v1
export ANTHROPIC_AUTH_TOKEN=あなたのAPIKey
```

その後、Claude Codeを起動：

**永続化する場合**（シェル設定ファイルに追加）：

```
# bashユーザー
echo 'export ANTHROPIC_BASE_URL=https://api.8tb.cc/v1' >> ~/.bashrc
echo 'export ANTHROPIC_AUTH_TOKEN=あなたのAPIKey' >> ~/.bashrc
source ~/.bashrc

# zshユーザー（macOSのデフォルト）
echo 'export ANTHROPIC_BASE_URL=https://api.8tb.cc/v1' >> ~/.zshrc
echo 'export ANTHROPIC_AUTH_TOKEN=あなたのAPIKey' >> ~/.zshrc
source ~/.zshrc
```

### Windows（PowerShell）

```
$env:ANTHROPIC_BASE_URL = "https://api.8tb.cc/v1"
$env:ANTHROPIC_AUTH_TOKEN = "あなたのAPIKey"
```

**永続化する場合**：

```
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://api.8tb.cc/v1", "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", "あなたのAPIKey", "User")
```

### Windows（CMD）

```
set ANTHROPIC_BASE_URL=https://api.8tb.cc/v1
set ANTHROPIC_AUTH_TOKEN=あなたのAPIKey
```

---

## 方法2：設定ファイル

プロジェクトルートまたは `~/.claude/` ディレクトリに `settings.json` を作成します：

```
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.8tb.cc/v1",
    "ANTHROPIC_AUTH_TOKEN": "あなたのAPIKey"
  }
}
```

**設定ファイルの優先順位**（低→高）：

1. `~/.claude/settings.json`（グローバル：全プロジェクトに適用）
2. `プロジェクトルート/.claude/settings.json`（プロジェクト単位：グローバルを上書き）
3. 環境変数（最高優先度）

---

## 方法3：起動時に一時的に指定

システム設定を変更せず、一時的に使いたい場合：

```
ANTHROPIC_BASE_URL=https://api.8tb.cc/v1 ANTHROPIC_AUTH_TOKEN=あなたのAPIKey claude
```

---

## 設定の確認

Claude Codeを起動したら、以下のコマンドで確認できます：

現在のモデル名（例：`claude-sonnet-4-5`）が表示されれば設定成功です。

実際に会話して確認することもできます：

---

## 利用可能なClaudeモデル

New APIでは以下のClaudeモデルが利用できます（`/model` コマンドで切り替え）：

| モデル名 | 説明 | 用途 |
| --- | --- | --- |
| `claude-opus-4-5` | 最高性能・高度な推論 | 複雑なコード・深い分析 |
| `claude-sonnet-4-5` | バランス型・速度と品質を両立 | 日常的な開発（デフォルト推奨） |
| `claude-haiku-4-5` | 軽量・高速・低コスト | 簡単なタスク・高頻度呼び出し |

---

## トラブルシューティング

### 「Authentication failed」または「Invalid API key」と表示される

* API Keyが正しくコピーされているか確認（余分なスペースがないか）
* `ANTHROPIC_API_KEY` ではなく **`ANTHROPIC_AUTH_TOKEN`** を使用しているか確認（Claude Codeは後者を優先して読み取ります）

### 環境変数を設定したが反映されない

* 環境変数を設定した**同じターミナルウィンドウ**でClaude Codeを起動しているか確認
* 新しいターミナルを開いた場合は `source ~/.zshrc` を再実行するか、ターミナルを再起動してください

### VS Codeで設定するには

VS CodeのClaude Code拡張機能の設定から `Anthropic: Base Url` と `Anthropic: Api Key` に入力します。またはVS Codeの統合ターミナルで環境変数を設定してから `claude` を実行する方法でも動作します。

---

## ワンコマンド設定スクリプト

macOS/Linux向けのセットアップスクリプト：

```
#!/bin/bash
echo "New APIのAPI Keyを入力してください："
read -s API_KEY

SHELL_RC="$HOME/.zshrc"
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"

echo "" >> "$SHELL_RC"
echo "# New API for Claude Code" >> "$SHELL_RC"
echo "export ANTHROPIC_BASE_URL=https://api.8tb.cc/v1" >> "$SHELL_RC"
echo "export ANTHROPIC_AUTH_TOKEN=$API_KEY" >> "$SHELL_RC"

source "$SHELL_RC"
echo "✅ 設定完了！'claude' を実行して使い始めましょう"
```

`setup-new-api.sh` として保存し、以下を実行：

```
chmod +x setup-new-api.sh
./setup-new-api.sh
```

---

## まとめ

New APIを使えば、Anthropic公式アカウントなしでもClaude Codeがすぐに使えます。設定はたった2つの環境変数だけ。

```
export ANTHROPIC_BASE_URL=https://api.8tb.cc/v1
export ANTHROPIC_AUTH_TOKEN=あなたのAPIKey
claude
```

ぜひ試してみてください 🚀

---

## 関連リンク
