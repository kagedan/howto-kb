---
id: "2026-03-25-claude-code-claude-desktopで音声対話環境を構築するmac-01"
title: "Claude Code / Claude Desktopで音声対話環境を構築する【Mac】"
url: "https://zenn.dev/fivot/articles/0392437670c826"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

# はじめに

作業中に都度キーボードに手を戻してClaude Code や Claude Desktopにタイプするのは意外と手間がかかります。

本記事では、以下の2つを組み合わせることで、**声で話しかけ・耳で返答を聞く**という音声対話環境の構築方法を紹介します。

* **Superwhisper**：グローバルホットキーで起動できる音声入力ツール
* **MCP + say コマンド**：Claude の返答を音声で読み上げる仕組み

# 手順

## 音声入力の設定（Superwhisper）

### インストール

<https://superwhisper.com> からダウンロードしてインストールします。

無料トライアルで全機能を試すことができます。

### 基本設定

インストール後、以下の設定を行います。

**ホットキーの設定**

設定 → Hotkey から任意のキーに変更します。

**言語の設定**

設定 → Language → Japanese を選択します。

### Claude Desktop 専用モードの作成

Superwhisper には「モード」という機能があり、フォーカスしているアプリごとに異なるモデルや言語設定ができます。

## 音声出力の設定（MCP + say コマンド）

### MCP サーバーの登録

Claude Desktop は MCP（Model Context Protocol）サーバーを登録することで、外部ツールを呼び出せるようになります。macOS 標準の `say` コマンドをラップした MCP サーバーを作成し、Claude に返答を読み上げさせます。

以下のファイルを編集します。

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

内容を以下のように設定します。

```
{
  "mcpServers": {
    "say": {
      "command": "python3",
      "args": ["-c", "import sys, json, subprocess\ndef handle():\n  for line in sys.stdin:\n    line = line.strip()\n    if not line: continue\n    req = json.loads(line)\n    method = req.get('method', '')\n    if method == 'tools/call' and req['params']['name'] == 'say':\n      text = req['params']['arguments']['text']\n      subprocess.Popen(['say', '-v', 'Kyoko (Enhanced)', '[[volm 0.3]]' + text])\n      result = {'content': [{'type': 'text', 'text': 'OK'}]}\n    elif method == 'tools/list':\n      result = {'tools': [{'name': 'say', 'description': 'テキストを音声で読み上げる', 'inputSchema': {'type': 'object', 'properties': {'text': {'type': 'string'}}, 'required': ['text']}}]}\n    elif method == 'initialize':\n      result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'say', 'version': '1.0.0'}}\n    else:\n      result = {}\n    print(json.dumps({'jsonrpc': '2.0', 'id': req.get('id'), 'result': result}))\n    sys.stdout.flush()\nhandle()"]
    }
  }
}
```

### 音声の設定

使用できる日本語の声は、ターミナルで以下のコマンドから確認できます。

デフォルトでは `Kyoko` が使用されますが、`Kyoko (Enhanced)` はニューラル音声でより自然な読み上げになります。

`Kyoko (Enhanced)` のダウンロードは、システム設定 → アクセシビリティ → 読み上げコンテンツ → システムの声 → カスタマイズ から行います。

また、`[[volm 0.4]]` は音量を指定するオプションです（0.0〜1.0）。デフォルトの音量が大きい場合は調整してください。

### Custom Instructions への指示の追加

Claude Desktop の Settings → Profile → Custom Instructions に以下を追加します。

```
返答の最後に say ツールを使って、返答の要点を1〜2文で読み上げること。
読み上げる文は自然な話し言葉にすること。
```

設定後、Claude Desktop を再起動すると反映されます。

## Claude Code でも使用する場合

設定ファイルの場所が異なるだけで、内容は同じです。

`~/.claude/claude.json` に同様の MCP 設定を追加します。

読み上げの指示は `~/.claude/CLAUDE.md` に記述します。

```
## 音声読み上げ
返答の最後に say ツールを使って、返答の要点を1〜2文で読み上げること。
読み上げる文は自然な話し言葉にすること。
```

# まとめ

本記事では、Superwhisper と MCP を組み合わせた Claude Desktop の音声対話環境の構築方法を紹介しました。

音声入力により手を止めずに話しかけることができ、MCP 経由の `say` コマンドにより返答を耳で受け取ることができます。作業の流れを止めずに Claude を活用できる環境として、ぜひ試してみてください。
