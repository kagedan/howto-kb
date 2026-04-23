---
id: "2026-03-23-保存版claude-codeのグローバル設定をgithubで管理してどのpcでも一発復元する-01"
title: "【保存版】Claude Codeのグローバル設定をGitHubで管理して、どのPCでも一発復元する"
url: "https://qiita.com/LingmuSajun/items/f0756783e36fa3fc142d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

# 【保存版】Claude Codeのグローバル設定をGitHubで管理して、どのPCでも一発復元する

## はじめに

Claude Codeを使い込んでいくと、`~/.claude/` 配下にどんどん設定が溜まっていきます。

* CLAUDE.md（グローバルルール）
* settings.json（権限・MCP設定）
* commands/（カスタムスラッシュコマンド）
* skills/（カスタムスキル）
* plugins/（プラグイン設定）

これらを**PCの入れ替え・クリーンインストール・チームメンバーへの共有**のたびに手動コピーするのは面倒ですし、漏れが発生します。

本記事では、**dotfilesリポジトリ + シンボリックリンク**という定番の手法で、Claude Codeのグローバル設定をGitHub管理し、新しい環境でも **`clone` → `./install.sh` の2ステップで即復元**できる仕組みを構築します。

### この記事で得られるもの

* `~/.claude/` 配下の全ファイルについて「Git管理すべきか否か」の判定基準
* dotfilesリポジトリの具体的な構築手順
* 新しいPCでの復元手順
* セキュリティの3層防御（.gitignore / pre-commitフック / 目視確認）
* すぐに使えるカスタムスラッシュコマンドのサンプル

### 前提環境

* Claude Codeがインストール済み（macOS / Linux / WSL）
* GitとGitHubアカウントがある

> 本記事のコマンドはLinux / WSL / macOSで共通です。

---

## なぜGitHub管理すべきか？

| 課題 | 管理なし | GitHub管理あり |
| --- | --- | --- |
| PC入れ替え | 手動コピー、漏れがち | `clone` → `./install.sh` で即復元 |
| バックアップ | なし | GitHubが自動バックアップ |
| 変更履歴 | 不明 | コミット履歴で全追跡 |
| 他人への共有 | ファイル送付 | リポジトリURL共有だけ |
| 設定ミスの巻き戻し | できない | `git revert` で即復元 |

シェルの設定（`.bashrc`、`.zshrc`）をdotfilesで管理するのと全く同じ発想です。

---

## `~/.claude/` の全ファイル管理判定表

Claude Codeを使い込むと `~/.claude/` 配下に多くのファイル・ディレクトリが生成されます。すべてをGit管理する必要はありません。

### ✅ Git管理する（自分でカスタマイズした設定）

| ファイル/ディレクトリ | 説明 |
| --- | --- |
| `CLAUDE.md` | グローバルルール。**最重要**。全セッションで読み込まれる |
| `settings.json` | 権限設定（allow/deny）、MCP設定 |
| `commands/` | カスタムスラッシュコマンド（`/review`、`/commit` 等） |
| `skills/` | カスタムスキル定義 |
| `plugins/` | プラグイン設定 |

### ❌ Git管理しない（自動生成・秘密情報・一時データ）

| ファイル/ディレクトリ | 理由 |
| --- | --- |
| `.credentials.json` | ⚠️ **認証トークン。漏洩厳禁** |
| `mcp-needs-auth-cache.json` | MCP認証キャッシュ。環境固有 |
| `history.jsonl` | 会話履歴。環境固有 |
| `sessions/` | セッションデータ |
| `session-env/` | セッション環境変数 |
| `shell-snapshots/` | シェル状態のスナップショット |
| `tasks/` | タスク管理の一時データ |
| `projects/` | プロジェクト別の自動生成データ |
| `ide/` | IDE連携の一時データ |
| `file-history/` | ファイル変更履歴 |
| `downloads/` | ダウンロード一時データ |
| `cache/` | キャッシュ |
| `backups/` | 自動バックアップ |

> **判定基準**: 「自分が意図的に作成・編集したもの」は管理する。「Claude Codeが自動生成したもの」と「秘密情報」は管理しない。

---

## 構築手順

### Step 1: dotfiles リポジトリを作成

```
mkdir -p ~/dotfiles/.claude/commands
cd ~/dotfiles
git init
```

### Step 2: CLAUDE.md を作成（まだない場合）

`~/.claude/CLAUDE.md` をまだ作成していない方は、ここで新規作成します。

`~/dotfiles/.claude/` 配下に `CLAUDE.md` を作成。中身は以下のとおり:

~/dotfiles/.claude/CLAUDE.md

```
# 個人設定

## 言語設定
- 全ての応答は日本語で行う

## コーディングスタイル
- 2スペースインデント
- セミコロン省略（JS/TS）
- 変数名・関数名は英語、コメントは日本語

## コミット
- コミットメッセージは日本語
- Conventional Commits形式（feat:, fix:, docs: 等）
- mainブランチへの直接コミットは禁止
- pushする前に必ず確認を取る

## コミュニケーション
- 簡潔に要点を伝える
- 不明点があれば実装前に確認を取る
```

> 💡 内容は後からいくらでも育てられます。`#` キーやプロンプトでClaude Codeに追記させることも可能。まずはこの骨格でOKです。

すでに `~/.claude/CLAUDE.md` がある場合は、Step 3でコピーします。

### Step 3: 既存の設定ファイルを dotfiles にコピー

```
# CLAUDE.md（すでに存在する場合）
[ -f ~/.claude/CLAUDE.md ] && cp ~/.claude/CLAUDE.md ~/dotfiles/.claude/CLAUDE.md

# settings.json（権限・MCP設定）
[ -f ~/.claude/settings.json ] && cp ~/.claude/settings.json ~/dotfiles/.claude/settings.json

# commands/（カスタムスラッシュコマンド）
[ -d ~/.claude/commands ] && cp -r ~/.claude/commands/* ~/dotfiles/.claude/commands/ 2>/dev/null

# skills/（カスタムスキル）
[ -d ~/.claude/skills ] && cp -r ~/.claude/skills ~/dotfiles/.claude/skills

# plugins/（プラグイン設定）
[ -d ~/.claude/plugins ] && cp -r ~/.claude/plugins ~/dotfiles/.claude/plugins
```

**⚠️ コピー後、settings.json にAPIキーやトークンが含まれていないか必ず確認してください:**

```
cat ~/dotfiles/.claude/settings.json
```

シークレットが含まれる場合の対処法は末尾の「セキュリティ注意事項」を参照。

### Step 4: install.sh を作成

新しい環境で `./install.sh` を実行するだけで、シンボリックリンクとセキュリティフックが自動で設定されるスクリプトです。

`~/dotfiles/` 配下に `install.sh` を作成。中身は以下のとおり:

~/dotfiles/install.sh

```
#!/bin/bash
set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

mkdir -p "$CLAUDE_DIR"

create_link() {
    local src="$1"
    local dest="$2"
    local name="$(basename "$dest")"

    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
        echo "  skip: $name (already linked)"
        return
    fi

    if [ -e "$dest" ] || [ -L "$dest" ]; then
        echo "  backup: $name → ${name}.backup"
        mv "$dest" "$dest.backup"
    fi

    ln -sf "$src" "$dest"
    echo "  linked: $name"
}

echo ""
echo "=== Claude Code dotfiles setup ==="
echo ""

# --- ファイル ---
for file in CLAUDE.md settings.json; do
    if [ -f "$DOTFILES_DIR/.claude/$file" ]; then
        create_link "$DOTFILES_DIR/.claude/$file" "$CLAUDE_DIR/$file"
    fi
done

# --- ディレクトリ ---
for dir in commands skills plugins; do
    if [ -d "$DOTFILES_DIR/.claude/$dir" ]; then
        if [ -d "$CLAUDE_DIR/$dir" ] && [ ! -L "$CLAUDE_DIR/$dir" ]; then
            echo "  backup: $dir/ → ${dir}.backup/"
            mv "$CLAUDE_DIR/$dir" "$CLAUDE_DIR/${dir}.backup"
        fi
        create_link "$DOTFILES_DIR/.claude/$dir" "$CLAUDE_DIR/$dir"
    fi
done

echo ""
echo "=== Done! ==="
echo ""
echo "Current ~/.claude/ symlinks:"
ls -la "$CLAUDE_DIR" | grep -- "->"

# --- pre-commit フック（秘密情報の誤コミット防止） ---
HOOK_DIR="$DOTFILES_DIR/.git/hooks"
if [ -d "$DOTFILES_DIR/.git" ]; then
    mkdir -p "$HOOK_DIR"
    cat > "$HOOK_DIR/pre-commit" << 'HOOK'
#!/bin/bash
BLOCKED_FILES=".credentials.json mcp-needs-auth-cache.json"
for file in $BLOCKED_FILES; do
    if git diff --cached --name-only | grep -q "$file"; then
        echo "❌ ERROR: $file には秘密情報が含まれます。コミットをブロックしました。"
        exit 1
    fi
done
if git diff --cached --name-only | grep -q "settings.json"; then
    if grep -i -E "(ghp_|sk-|Bearer [A-Za-z0-9])" .claude/settings.json 2>/dev/null; then
        echo "⚠️  WARNING: settings.json にトークンらしき文字列があります。確認してください。"
        exit 1
    fi
fi
HOOK
    chmod +x "$HOOK_DIR/pre-commit"
    echo ""
    echo "Security: pre-commit hook installed (blocks credential commits)"
fi
```

作成後、実行権限を付与:

```
chmod +x ~/dotfiles/install.sh
```

**ポイント:**

* 既存ファイルは `.backup` にリネームしてから上書きするので安全
* すでに正しいリンクが張られている場合はスキップ（冪等性）
* pre-commitフックが自動設定され、秘密情報の誤コミットを防止

### Step 5: .gitignore を作成

万が一、秘密情報が紛れ込んでも守れるように。

`~/dotfiles/` 配下に `.gitignore` を作成。中身は以下のとおり:

~/dotfiles/.gitignore

```
# 秘密情報（絶対にコミットしない）
.credentials.json
mcp-needs-auth-cache.json

# 一時データ・環境固有
history.jsonl
*.backup

# OS生成ファイル
.DS_Store
Thumbs.db
```

### Step 6: README.md を作成

`~/dotfiles/` 配下に `README.md` を作成。中身は以下のとおり:

~/dotfiles/README.md

```
# dotfiles

Claude Code のグローバル設定を管理するリポジトリ。

## セットアップ

git clone https://github.com/<username>/dotfiles.git ~/dotfiles
cd ~/dotfiles
chmod +x install.sh
./install.sh

## 含まれるもの

| ファイル | 説明 |
|---------|------|
| `.claude/CLAUDE.md` | グローバルルール（日本語応答、コーディングスタイル等） |
| `.claude/settings.json` | 権限設定、MCP設定 |
| `.claude/commands/` | カスタムスラッシュコマンド |
| `.claude/skills/` | カスタムスキル定義 |
| `.claude/plugins/` | プラグイン設定 |

## 更新方法

cd ~/dotfiles
git add -A
git commit -m "docs: CLAUDE.mdにテスト方針を追記"
git push

## 別のPCに反映

cd ~/dotfiles
git pull
```

### Step 7: シンボリックリンクを張る

```
cd ~/dotfiles
./install.sh
```

実行結果:

```
=== Claude Code dotfiles setup ===

  linked: CLAUDE.md
  backup: settings.json → settings.json.backup
  linked: settings.json
  backup: commands/ → commands.backup/
  linked: commands
  backup: skills/ → skills.backup/
  linked: skills
  backup: plugins/ → plugins.backup/
  linked: plugins

=== Done! ===

Security: pre-commit hook installed (blocks credential commits)
```

### Step 8: プッシュ前の安全確認 & GitHub にプッシュ

**⚠️ 初回プッシュ前に必ず以下の確認を行ってください。**

```
cd ~/dotfiles

# 確認1: credentials がステージングされていないか
git status
# → .credentials.json や mcp-needs-auth-cache.json が表示されていたら絶対にコミットしない

# 確認2: settings.json にトークンが直書きされていないか
grep -i -E "(token|secret|password|Bearer|ghp_|sk-)" ~/dotfiles/.claude/settings.json
# → 何もヒットしなければOK。ヒットしたら環境変数に置き換える（末尾の注意事項参照）
```

問題なければ、GitHubで **Privateリポジトリ** を作成してからプッシュ。

> ⚠️ **GitHubでリポジトリを作成する際、必ず「Private」を選択してください。** デフォルトがPublicになっている場合があるので注意。

```
cd ~/dotfiles
git add -A
git commit -m "feat: Claude Code dotfiles 初期設定"
git remote add origin https://github.com/<username>/dotfiles.git
git branch -M main
git push -u origin main
```

### Step 9: pre-commit フックの確認（install.sh が自動設定済み）

Step 7 で `install.sh` を実行した時点で、pre-commit フックが自動的にインストールされています。

このフックにより、万が一 `.credentials.json` 等をコミットしようとしても**自動ブロック**されます。

動作確認:

```
# わざと .credentials.json をステージングしてみる（テスト）
touch ~/dotfiles/.claude/.credentials.json
cd ~/dotfiles
git add .claude/.credentials.json
git commit -m "test"
# → ❌ ERROR: .credentials.json には秘密情報が含まれます。コミットをブロックしました。

# テスト後のクリーンアップ
git reset HEAD .claude/.credentials.json
rm ~/dotfiles/.claude/.credentials.json
```

> 💡 pre-commit フックは `.git/hooks/` 内にあるためリポジトリ自体にはコミットされません。新しいPCでも `install.sh` を実行すれば自動で再設定されます。

---

## 完成後のリポジトリ構成

```
~/dotfiles/
├── .gitignore
├── README.md
├── install.sh
└── .claude/
    ├── CLAUDE.md
    ├── settings.json
    ├── commands/
    │   └── *.md
    ├── skills/
    │   └── ...
    └── plugins/
        └── ...
```

`~/.claude/` 内のシンボリックリンク:

```
~/.claude/CLAUDE.md      → ~/dotfiles/.claude/CLAUDE.md
~/.claude/settings.json  → ~/dotfiles/.claude/settings.json
~/.claude/commands/      → ~/dotfiles/.claude/commands/
~/.claude/skills/        → ~/dotfiles/.claude/skills/
~/.claude/plugins/       → ~/dotfiles/.claude/plugins/
```

それ以外のファイル（sessions, cache, history, credentials 等）は `~/.claude/` に残り、Git管理されません。

---

## 日常の運用フロー

### 設定を変更したとき

Claude Codeが `#` キーや自動メモリでCLAUDE.mdを更新した場合も、シンボリックリンク経由で **dotfiles側のファイルが直接更新**されます。

```
cd ~/dotfiles
git diff                    # 何が変わったか確認
git add -A
git commit -m "docs: TDD方針を追記"
git push
```

### 別のPCで最新を取得

```
cd ~/dotfiles
git pull
# シンボリックリンクなので pull だけで即反映。install.sh の再実行は不要。
```

### 新しいPCをゼロからセットアップ

```
# 1. Claude Codeをインストール & 一度起動して ~/.claude/ を生成
curl -fsSL https://claude.ai/install.sh | bash
claude    # 認証して終了

# 2. dotfilesをクローン
git clone https://github.com/<username>/dotfiles.git ~/dotfiles

# 3. シンボリックリンクを張る
cd ~/dotfiles
./install.sh

# 4. 完了。前のPCと同じ環境が復元される
claude
```

**たった3コマンドで環境復元できます。**

---

## おまけ：カスタムスラッシュコマンドのサンプル

`~/dotfiles/.claude/commands/` 配下に `.md` ファイルを置くと、Claude Code内で `/コマンド名` として呼び出せます。dotfilesで管理すれば、どの環境でも同じコマンドが使えます。

### `/review` — コードレビュー

`commands/` 配下に `review.md` を作成。中身は以下のとおり:

commands/review.md

```
---
description: 現在の差分をレビューする
---
現在のブランチの差分をレビューしてください。
以下の観点でチェック:
- バグやセキュリティの問題
- 冗長なコードやデバッグコードの残留
- 命名規則の一貫性
- テストの漏れ

問題があれば具体的に指摘し、修正案を提示してください。
```

### `/commit` — コミット作成

`commands/` 配下に `commit.md` を作成。中身は以下のとおり:

commands/commit.md

```
---
description: ステージング済みの差分からコミットを作成
---
現在ステージングされている差分を確認し、
適切なコミットメッセージを作成してcommitしてください。

ルール:
- メッセージは日本語
- Conventional Commits形式（feat:, fix:, docs: 等）
- pushは行わない（ユーザーに確認させる）
```

### `/test` — テスト作成

`commands/` 配下に `test.md` を作成。中身は以下のとおり:

commands/test.md

```
---
description: 指定ファイルのテストを作成
---
$ARGUMENTS のテストを作成してください。

ルール:
- 既存のテストファイルのパターンに従う
- 正常系・異常系・エッジケースを網羅
- テストを実行して全てパスすることを確認
```

---

## ⚠️ セキュリティ注意事項

### 本記事の多層防御

この手順では以下の3層で秘密情報の漏洩を防いでいます。

| 層 | 対策 | 防げるリスク |
| --- | --- | --- |
| **第1層** | `.gitignore` で除外 | 通常の `git add -A` での混入 |
| **第2層** | `pre-commit` フック | `.gitignore` をすり抜けた場合のブロック |
| **第3層** | プッシュ前の目視確認 | 上記すべてが失敗した場合の最終防衛 |

> **どれか1つが失敗しても、他の層で食い止められる設計です。**

### 絶対にGitにコミットしてはいけないもの

| ファイル | 理由 |
| --- | --- |
| `.credentials.json` | Anthropicの認証トークン。漏洩するとアカウントが悪用される |
| `mcp-needs-auth-cache.json` | MCP認証のキャッシュトークン |

### プッシュ前の確認コマンド（毎回実行推奨）

```
cd ~/dotfiles

# 秘密ファイルが含まれていないか
git status | grep -E "credentials|auth-cache"

# settings.json にトークンが直書きされていないか
grep -i -E "(token|secret|password|ghp_|sk-)" .claude/settings.json
```

**何もヒットしなければ安全です。**

### settings.json にシークレットが含まれる場合

MCP設定にトークンが直書きされている場合は、環境変数に置き換えてください。

settings.json 内の該当部分を以下のように書き換え:

```
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.github.com/mcp",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  }
}
```

トークンの実体は `~/.bashrc` に記載（この行自体はdotfilesにコミットしない）:

```
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

### GitHubリポジトリは必ずPrivateで作成

* GitHubの新規リポジトリ作成時、**デフォルトが Public の場合がある**ので必ず確認
* 万が一 Public で作成してしまった場合は、即座に `Settings` → `Danger Zone` → `Change visibility` で Private に変更
* すでにプッシュ済みで認証情報が含まれていた場合は、**トークンを即座に無効化**（Anthropicダッシュボードでログアウト → 再認証）

### もし秘密情報をコミットしてしまったら

**`git rm` や新しいコミットで削除しても、Git履歴に残ります。** 以下の対処が必要です:

1. **トークンを即座に無効化する**（これが最優先）
   * Claude Code: `claude auth logout` → `claude auth login` で再認証
   * MCP: 該当サービスのダッシュボードでトークンを再生成
2. **Git履歴からも削除する**

   ```
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .claude/.credentials.json' \
     --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```
3. **GitHubのキャッシュを削除する**（GitHubサポートへ連絡が必要な場合あり）

---

## まとめ

* Claude Codeのグローバル設定は `~/.claude/` 配下に集約されており、**dotfilesリポジトリで管理可能**
* 管理対象は **CLAUDE.md / settings.json / commands / skills / plugins** の5つ。それ以外は自動生成データなので不要
* **シンボリックリンク方式**により、`git pull` だけで即反映。install.shの再実行も不要
* 新しいPCでも **clone → install.sh → claude** の3ステップで完全復元
* セキュリティは **.gitignore + pre-commitフック + 目視確認** の3層防御。秘密情報の漏洩リスクを最小化
* リポジトリは **必ずPrivate** で作成する

一度セットアップすれば、あとはClaude Codeを使い込むほど設定が育ち、それがそのままGitHubにバックアップされていきます。

---

## 参考
