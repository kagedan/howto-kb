---
id: "2026-05-28-claude-code-のパーミッション設計を理解してdo-you-want-to-proceedを-01"
title: "Claude Code のパーミッション設計を理解して「Do you want to proceed?」を減らす"
url: "https://qiita.com/satoshi_061/items/8e56cc945445e2fbee72"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "Python", "qiita"]
date_published: "2026-05-28"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

Claude Code を使っていると、コマンドを実行するたびに表示される「Do you want to proceed?」確認プロンプト。

便利な安全機構ですが、毎回止まると作業テンポが崩れます。パーミッション設定を理解して、信頼できる操作は確認なしで動かせるようにしましょう。

## なぜパーミッションが必要なのか

Claude Code はファイル編集・シェルコマンド実行・外部通信など、影響範囲の大きい操作を行えます。デフォルトでは未知の操作に対して確認プロンプトを出すことで、意図しない変更を防ぐ設計になっています。

## 設定ファイルの場所

パーミッションは JSON ファイルで管理します。

| ファイル | スコープ | 用途 |
|----------|----------|------|
| `~/.claude/settings.json` | グローバル | 全プロジェクト共通の設定 |
| `.claude/settings.json` | プロジェクト | チーム共有の設定（git 管理） |
| `.claude/settings.local.json` | プロジェクトローカル | 個人の上書き設定（gitignore 推奨） |

設定は `user → project → local` の順に読み込まれ、後から読まれたものが優先されます。

## パーミッションルールの書き方

`permissions.allow` 配列にルールを追加します。

```json
{
  "permissions": {
    "allow": [
      "Bash(gh issue list *)",
      "Bash(git *)",
      "Edit(/path/to/dir/)",
      "Write(/path/to/dir/)"
    ]
  }
}
```

### Bash コマンドのルール

```
"Bash(コマンド *)"
```

`*` はワイルドカードで、後続の引数すべてにマッチします。

| ルール | マッチする例 |
|--------|-------------|
| `"Bash(git *)"` | `git status`、`git log`、`git commit -m "..."` |
| `"Bash(gh issue list *)"` | `gh issue list --repo vitejs/vite --state open` |
| `"Bash(python3 *)"` | `python3 script.py`、`python3 -c "..."` |
| `"Bash(npm run test)"` | `npm run test`（完全一致） |

### ファイル操作のルール

```
"Edit(/path/to/dir/)"   // 指定ディレクトリ以下のファイル編集を許可
"Write(/path/to/dir/)"  // 指定ディレクトリ以下へのファイル作成を許可
"Read"                  // すべての読み取りを許可（引数なし）
```

## 実際の設定例

OSS コントリビュート用に GitHub CLI と学習ノートの編集を許可する例：

```json
{
  "permissions": {
    "allow": [
      "Bash(gh issue list *)",
      "Bash(gh issue view *)",
      "Bash(gh pr list *)",
      "Bash(gh pr view *)",
      "Bash(gh pr comment *)",
      "Bash(gh issue comment *)",
      "Bash(python3 *)",
      "Bash(grep *)",
      "Edit(/Users/yourname/notes/)",
      "Write(/Users/yourname/notes/)"
    ]
  }
}
```

## deny で危険な操作をブロックする

`deny` を使うと、`allow` よりも優先して操作を拒否できます。

```json
{
  "permissions": {
    "allow": ["Bash(git *)"],
    "deny": ["Bash(git push --force *)"]
  }
}
```

これで `git` コマンド全般は許可しつつ、`git push --force` だけは必ず確認プロンプトを出せます。

## スコープは必要最小限に

`"Bash(*)"` のように全コマンドを許可するのは危険です。`rm -rf` や意図しない副作用のあるコマンドも素通りしてしまいます。

**よい設計の指針：**

- 実際に使うコマンド・ディレクトリだけを `allow` に追加する
- 広いルールを使う場合は `deny` で危険な操作を塞ぐ
- 不明なコマンドはデフォルトの確認プロンプトに任せる

## /fewer-permission-prompts コマンドを使う

Claude Code には、過去のトランスクリプトを解析して「よく使うのに毎回確認している操作」を自動検出し、`allow` リストへの追加を提案してくれるコマンドがあります。

```
/fewer-permission-prompts
```

一から設定を書くより、まずこのコマンドで候補を出してもらうのが効率的です。

## まとめ

| 設定 | 用途 |
|------|------|
| `Bash(コマンド *)` | シェルコマンドを許可 |
| `Edit(/path/)` | ファイル編集を許可 |
| `Write(/path/)` | ファイル作成を許可 |
| `deny` | 特定の操作を明示的にブロック |

パーミッション設定を適切に整えると、確認プロンプトを減らしながら安全性も保てます。最初は狭いスコープで始めて、使いながら少しずつ広げていくのがおすすめです。
