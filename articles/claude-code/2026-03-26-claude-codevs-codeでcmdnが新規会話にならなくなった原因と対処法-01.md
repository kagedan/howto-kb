---
id: "2026-03-26-claude-codevs-codeでcmdnが新規会話にならなくなった原因と対処法-01"
title: "【Claude Code】VS Codeでcmd+Nが新規会話にならなくなった原因と対処法"
url: "https://qiita.com/k_bobchin/items/4dee07aaaab49c5a8599"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

# 症状

Claude Code 拡張を VS Code のセカンダリサイドバーで使用中、`⌘N`（Cmd+N）で新規会話が開始できなくなった。

以前は `⌘N` で即座に新しいセッションが始まっていたが、拡張のアップデート後に突然動作しなくなった。

## 結論

**`claudeCode.enableNewConversationShortcut` のデフォルト値が `true` → `false` にサイレント変更されていた。**

| バージョン | デフォルト値 |
| --- | --- |
| v2.1.71 | `true` |
| v2.1.84 | `false` |

この変更は [CHANGELOG](https://github.com/anthropics/claude-code/releases) に記載されていない。

## 対処法

VS Code の `settings.json` に以下を追加する：

```
"claudeCode.enableNewConversationShortcut": true
```

Settings UI からも設定可能。`Claude Code: Enable New Conversation Shortcut` で検索すればチェックボックスが見つかる。

[![スクリーンショット 2026-03-26 17.13.03.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F183059%2Fa1c323a1-b8f2-4168-9de1-3fcb608713be.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1473264f7205befdac4d439be92d4f9d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F183059%2Fa1c323a1-b8f2-4168-9de1-3fcb608713be.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1473264f7205befdac4d439be92d4f9d)

## 調査の過程

### 1. キーバインディングの確認

まず、`⌘N` に何が割り当てられているかを確認した。

Claude Code 拡張の `package.json` には以下のキーバインディングが定義されている：

```
{
  "command": "claude-vscode.newConversation",
  "key": "cmd+n",
  "mac": "cmd+n",
  "when": "config.claudeCode.enableNewConversationShortcut && (activeWebviewPanelId == 'claudeVSCodePanel' || (claude-vscode.sideBarActive && !editorFocus && !panelFocus))"
}
```

`when` 句に `config.claudeCode.enableNewConversationShortcut` が含まれている。この設定が `false` であれば、when 句全体が `false` になり、キーバインディングは発火しない。

### 2. デフォルト値の比較

ローカルに残っていた旧バージョン（v2.1.71）と最新バージョン（v2.1.84）の `package.json` を比較した：

```
# 拡張のpackage.jsonから設定のデフォルト値を抽出
python3 << 'EOF'
import json

for ver, path in [
    ("2.1.71", "~/.vscode/extensions/anthropic.claude-code-2.1.71-darwin-arm64/package.json"),
    ("2.1.84", "~/.vscode/extensions/anthropic.claude-code-2.1.84-darwin-arm64/package.json"),
]:
    with open(path) as f:
        data = json.load(f)
    for item in data.get("contributes", {}).get("configuration", []):
        for key, val in item.get("properties", {}).items():
            if "enableNew" in key:
                print(f"v{ver}: {key} = default: {val.get('default')}")
EOF
```

```
v2.1.71: claudeCode.enableNewConversationShortcut = default: True
v2.1.84: claudeCode.enableNewConversationShortcut = default: False
```

明確にデフォルト値が変更されていた。

### 3. CHANGELOG の確認

[GitHub Releases](https://github.com/anthropics/claude-code/releases) の v2.1.72〜v2.1.84 のリリースノートを確認したが、この変更に関する記載は見つからなかった。

## なぜハマるのか

1. **デフォルト値の変更**なので、自分の `settings.json` を変更していなくても動作が変わる
2. **CHANGELOG に記載がない**ので、リリースノートを読んでも原因にたどり着けない
3. キーバインディング自体は存在するので、Keyboard Shortcuts UI で見ると `⌘N` → `claude-vscode.newConversation` が登録されているように見える
4. `when` 句の中に `config.claudeCode.enableNewConversationShortcut` が埋まっているため、設定が `false` だと気付きにくい

## 補足：Developer: Inspect Context Keys の活用

VS Code のキーバインディング問題を調査する際は、コマンドパレットから **Developer: Inspect Context Keys** を実行すると、現在のフォーカス位置で有効なコンテキストキーの値を一覧できる。`when` 句のどの条件が `true`/`false` かを確認でき、問題の切り分けに役立つ。

## 環境

* macOS (Apple Silicon)
* VS Code（1.113.0）
* Claude Code 拡張 v2.1.84
