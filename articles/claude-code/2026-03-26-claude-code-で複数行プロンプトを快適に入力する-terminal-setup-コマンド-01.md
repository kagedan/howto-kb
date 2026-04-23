---
id: "2026-03-26-claude-code-で複数行プロンプトを快適に入力する-terminal-setup-コマンド-01"
title: "Claude Code で複数行プロンプトを快適に入力する `/terminal-setup` コマンド"
url: "https://qiita.com/tacker530i/items/72ed6ad1438f29dbe2ba"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

Claude Code を使い始めて最初に戸惑うのが「**Enter を押すと即座に送信されてしまい、複数行の指示が書けない**」という問題です。

通常のチャットツール（Slack や Discord など）では Enter が改行、Shift+Enter が送信という操作が一般的ですが、Claude Code はターミナルツールであるため、**Enter がそのまま実行**になっています。(できればShift+Enterに統一してほしい...)

この記事では、公式が用意している `/terminal-setup` コマンドを使った改行設定の方法と、環境別の対処法をまとめます。

## 動作環境

| 項目 | 内容 |
| --- | --- |
| ツール | Claude Code（最新版） |
| 対応ターミナル | VS Code、iTerm2、WezTerm、Ghostty、Kitty、Alacritty、Zed、Warp 他 |

---

## 問題：Enter を押すと即送信されてしまう

Claude Code のインタラクティブモードでは、Enter キーの動作は「**実行（送信）**」です。

複数行にわたる指示を書こうとすると、途中で意図せず送信されてしまいます。

```
> このリポジトリで以下の作業をしてください:
（← ここで Enter を押すと送信されてしまう）
```

---

## 解決策① どの環境でも使えるバックスラッシュ改行

設定不要でどの環境でも確実に動作する方法です。

行末に `\`（バックスラッシュ）を入力してから Enter を押すと、Claude Code は「まだ入力が続く」と解釈して複数行入力を受け付けます。

```
> このリポジトリで以下の作業をしてください:\
1. テストが失敗している原因を特定する\
2. 修正案を実装する\
3. 必要なテストコードを追加する
```

**注意** バックスラッシュを消し忘れると、`\` がプロンプトの一部として解釈されてしまいます。また、毎回入力が必要なため常用には向きません。

Windows 環境では `¥`（円マーク）＋ Enter でも同様に動作します。

---

## 解決策② `/terminal-setup` コマンドで自動設定（推奨）

Claude Code 内で以下のコマンドを実行するだけです。

これにより、**Shift+Enter で改行、Enter で送信**という操作が使えるようになります。設定は一度実行すれば永続的に有効になります。

### 対応ターミナル

| ターミナル | 状況 |
| --- | --- |
| **iTerm2 / WezTerm / Ghostty / Kitty** | 最初から Shift+Enter が使用可能（コマンド不要） |
| **VS Code ターミナル** | `/terminal-setup` 実行で設定される |
| **Alacritty / Zed / Warp** | `/terminal-setup` 実行で設定される |

**ポイント** iTerm2、WezTerm、Ghostty、Kitty を使用している場合、Shift+Enter はすでにネイティブに機能するため `/terminal-setup` コマンドは表示されません。

---

## 解決策③ Ctrl+J（万能な代替手段）

`/terminal-setup` が使えない環境（tmux 使用時、code-server など）でも、`Ctrl+J` を使うと確実に改行できます。

OS・ターミナル環境に依存せず安定して動作するため、環境が特殊な場合の第一候補です。

---

## 解決策④ Option+Enter（macOS 限定）

macOS 環境では、ターミナルの設定を変更することで `Option+Enter` を改行に割り当てられます。

**macOS Terminal.app の場合：**

1. 設定 → プロファイル → キーボードを開く
2. 「Option キーを Meta キーとして使用」にチェックを入れる

**iTerm2 / VS Code ターミナルの場合：**

各アプリのキーバインド設定から Option+Enter を改行シーケンスにマッピングします。

---

## 解決策⑤ code-server 環境での設定（手動）

code-server 上では `/terminal-setup` がうまく動作しないことがあります。その場合は `keybindings.json` を手動で編集します。

1. コマンドパレットを開く（`Ctrl+Shift+P` または `F1`）
2. `Open Keyboard Shortcuts (JSON)` を選択
3. 以下を追加する

```
[
  {
    "key": "shift+enter",
    "command": "workbench.action.terminal.sendSequence",
    "args": { "text": "\\\n" },
    "when": "terminalFocus && !terminalTextSelected"
  }
]
```

**仕組み** `\\\n` は「バックスラッシュ＋改行文字」を送信します。Claude Code はこの組み合わせを複数行入力として解釈します。

---

## 方法のまとめ

| 方法 | 設定 | おすすめ度 | 備考 |
| --- | --- | --- | --- |
| `\` ＋ Enter | 不要 | ★★☆ | どこでも動くが毎回入力が必要 |
| `/terminal-setup` | コマンド1行 | ★★★ | 一度設定すれば永続的に有効 |
| `Ctrl+J` | 不要 | ★★★ | tmux 等の特殊環境でも安定 |
| `Option+Enter` | ターミナル設定変更 | ★★☆ | macOS 限定 |
| `keybindings.json` 手動編集 | JSON 編集 | ★★☆ | code-server 等の代替手段 |

---

## まとめ

* Claude Code では Enter が即送信のため、複数行入力には別の操作が必要
* 最も手軽な設定は Claude Code 内で **`/terminal-setup`** を実行するだけ
* iTerm2 / WezTerm / Ghostty / Kitty は最初から **Shift+Enter** が使える
* どの環境でも確実に動く方法は `\` ＋ Enter または **Ctrl+J**
* code-server など特殊環境は `keybindings.json` の手動編集で対応

複数行プロンプトがスムーズに入力できるようになると、より詳細な指示を Claude Code に与えられるようになり、開発効率が大きく向上します。ぜひ環境に合った方法を設定してみてください。

---

## 参考
