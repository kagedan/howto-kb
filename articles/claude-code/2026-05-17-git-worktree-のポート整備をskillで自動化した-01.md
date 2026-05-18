---
id: "2026-05-17-git-worktree-のポート整備をskillで自動化した-01"
title: "git worktree のポート整備をSkillで自動化した"
url: "https://qiita.com/yuchi1128/items/0ac7eee336506f53998c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

# はじめに

個人で以下の Web アプリを運営しています。

https://bakuwaki.jp/

関連記事

https://qiita.com/yuchi1128/items/eca2bb94dec63ecbff93

Next.js + Go + PostgreSQL のモノレポ構成です。

このアプリの開発で **git worktree** をよく使うのですが、ローカル環境でのポートの競合に悩まされていました。その問題をシェルスクリプト + Claude Code Skill で解決しました。

同じような悩みを抱えている方の助けになると幸いです。

## git worktreeとは？
`git worktree` は1つのリポジトリから複数のブランチを **別々のディレクトリにチェックアウトできる機能** です。普通の `git checkout` での切り替えと違って、各ブランチが独立したディレクトリ・独立した `node_modules`・独立した起動状態を持てます。

個人開発で次のような状況が増えてきたので使い始めました。

- 複数の機能を **並行で進めたい** (Claude Code を別セッションで並行起動するときに特に便利)
- ブランチ切り替えのたびに stash・依存再インストールをしたくない


## ぶつかった問題

`git worktree` は便利なのですが、開発でフロントエンド (npm run dev) と バックエンド・DB (Docker) を同時に起動するので、worktree を増やすと

- フロントエンド / バックエンドの **ポートが衝突**
- フロントが叩く API URL が worktree ごとに違う
- CORS の許可ドメインも増える
- 作業終了後の片付け (worktree削除・ブランチ削除・サーバー停止) も毎回手動

という問題がありました。

要するに、**worktree を作るたびに環境変数とポートの調整が地味に面倒**でした。

## 解決方法

### 設計のポイント（2つのモードに分ける）

作業内容に応じて2モードを使い分けることにしました。

**モード A : フロントエンドのみ変更**

フロントエンドだけ触る作業のときは worktree 内でDocker を立ち上げず、main のバックエンドを共有するようにしました。

```
[Worktree Frontend (3100台)]
    ↓
[Main Backend (8080)]  ← main で起動済みのものを共有
    ↓
[Main DB (5432)]
```

Docker をまったく起動しなくて済むので、worktree の立ち上げが軽くて早いです。

**モード B: バックエンド・DBも変更**

バックエンドの変更が伴う時は worktree 内で Docker も起動するようにしました。

```
[Worktree Frontend (3100台)]
    ↓
[Worktree Backend (8100台)]  ← worktree専用に Docker 起動
    ↓
[Worktree DB (5500台)]       ← worktree専用に Docker 起動
```

バックエンドのコード変更だけでなく **DBのスキーマ変更も worktree で安全に試せる** ように、Backend と DB をまとめて worktree 内に起動します。
main のデータベースに影響を与えないので、マイグレーションの検証もこちらで行えます。

### 全体構成

- **シェルスクリプト** (`setup-worktree.sh`)の作成
  - ポート割り当て
  - 環境ファイルの自動生成
- **Skills**で以下を1コマンド化
  - worktreeを作成
  - 起動（上記スクリプトでポート割り当て）
  - 片付け
  - モードA/Bの分岐も Skill 側に押し込める


### シェルスクリプト

worktree 名のハッシュからポートを決定的に割り当て、衝突したら次のスロットにずらします。
Frontend / Backend / DB の3つ分のポートを worktree ごとに用意します。

<details><summary>シェルスクリプトの内容</summary>

```scripts/setup-worktree.sh
set -euo pipefail

# 実行場所の確認 (worktree のルートで実行されているか)
if [ ! -f "docker-compose.yml" ]; then
  echo "Error: docker-compose.yml が見つかりません。" >&2
  exit 1
fi

CURRENT_DIR="$(pwd)"
WORKTREE_NAME="$(basename "$CURRENT_DIR")"

# main repo の場所を特定 (worktree の git common dir の親)
GIT_COMMON_DIR="$(git rev-parse --git-common-dir 2>/dev/null || echo "")"
if [ -z "$GIT_COMMON_DIR" ]; then
  echo "Error: git リポジトリではありません。" >&2
  exit 1
fi
MAIN_REPO="$(cd "$GIT_COMMON_DIR/.." && pwd)"

if [ "$CURRENT_DIR" = "$MAIN_REPO" ]; then
  echo "Error: このスクリプトは worktree 用です。" >&2
  exit 1
fi

# worktree名のSHA1ハッシュ先頭4桁(hex)から 1〜50 のスロット番号を計算
# Frontend port: 3100〜3149, Backend port: 8100〜8149, DB port: 5500〜5549
HASH_HEX="$(printf '%s' "$WORKTREE_NAME" | shasum | cut -c1-4)"
SLOT=$(( 16#${HASH_HEX} % 50 + 1 ))

# ポート衝突を検出して自動で次のスロットへ
MAX_TRIES=50
TRIES=0
while [ $TRIES -lt $MAX_TRIES ]; do
  FRONTEND_PORT=$((3100 + SLOT - 1))
  BACKEND_PORT=$((8100 + SLOT - 1))
  DB_PORT=$((5500 + SLOT - 1))
  if ! lsof -iTCP:$FRONTEND_PORT -sTCP:LISTEN >/dev/null 2>&1 \
     && ! lsof -iTCP:$BACKEND_PORT -sTCP:LISTEN >/dev/null 2>&1 \
     && ! lsof -iTCP:$DB_PORT -sTCP:LISTEN >/dev/null 2>&1; then
    break
  fi
  SLOT=$(( SLOT % 50 + 1 ))
  TRIES=$((TRIES + 1))
done

if [ $TRIES -ge $MAX_TRIES ]; then
  echo "Error: 空きポートが見つかりません" >&2
  exit 1
fi

write_if_absent() {
  local path="$1"
  local content="$2"
  if [ -f "$path" ]; then
    echo "  skip: $path (既に存在)"
  else
    printf '%s' "$content" > "$path"
    echo "  生成: $path"
  fi
}

echo ""
echo "Worktree:      $WORKTREE_NAME"
echo "Frontend port: $FRONTEND_PORT"
echo "Backend port:  $BACKEND_PORT"
echo "DB port:       $DB_PORT"
echo ""

# 1. Compose 用の .env (worktree ルート)
#    Backend と DB は worktree 内で起動するため、Docker内部ネットワークで接続
write_if_absent "$CURRENT_DIR/.env" "\
BACKEND_PORT=$BACKEND_PORT
DB_PORT=$DB_PORT
DATABASE_URL=postgres://user:password@db:5432/hotaruika_db?sslmode=disable
"

# 2. Next.js 用の .env.local
#    デフォルトは Main backend (8080) を共有 (Mode A)
write_if_absent "$CURRENT_DIR/frontend/.env.local" "\
PORT=$FRONTEND_PORT
NEXT_PUBLIC_API_URL=http://localhost:8080
# Mode B (Worktree backend を使う) 場合は上をコメントアウトし、以下を有効化
# NEXT_PUBLIC_API_URL=http://localhost:$BACKEND_PORT
"

# 3. backend/.env を main からコピー (Mode B で worktree backend 起動時に必要)
if [ -f "$CURRENT_DIR/backend/.env" ]; then
  echo "  skip: backend/.env"
elif [ -f "$MAIN_REPO/backend/.env" ]; then
  cp "$MAIN_REPO/backend/.env" "$CURRENT_DIR/backend/.env"
  echo "  コピー: backend/.env (main から)"
fi

cat <<EOF

セットアップ完了。

  cd frontend && npm install              # 初回のみ
  PORT=$FRONTEND_PORT npm run dev

  → http://localhost:$FRONTEND_PORT
EOF
```
</details>

### Skill

シェルスクリプトだけだとまだ毎回 `git worktree add` → `bash scripts/setup-worktree.sh` → `npm install` → `PORT=xxxx npm run dev` を叩く必要があります。
これを [Claude Code](https://claude.com/claude-code) の **Skill** で1コマンド化しました。

<details><summary>Skillsの内容</summary>

````.claude/skills/worktree-new/SKILL.md
---
name: worktree-new
description: 新規ワークツリーを作成して開発環境を起動する。ブランチ作成、setup-worktree.sh実行、依存インストール、devサーバー起動までを自動化。Use when user wants to start work in a new worktree, create a worktree for a feature, or begin parallel development.
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
---

# Worktree New スキル

## Instructions

このスキルは新規ワークツリーを作成し、開発をすぐ始められる状態にする。

### 実行フロー

#### 1. 事前確認

main に居ること、未コミット変更がないことを確認:

```bash
git branch --show-current
git status
```

main 以外なら AskUserQuestion で確認、未コミット変更があれば中止。

#### 2. トピック名の確認

**AskUserQuestion** でユーザーに確認 (kebab-case)。
ブランチ名は `worktree-<topic>` 形式になる。

#### 3. モード選択

**AskUserQuestion** で確認:

```
[A] フロントエンドのみ (Main backend/DB を共有・推奨)
[B] バックエンド・DBも変更 (worktree専用 backend + DB を起動)
```

#### 4. ワークツリー作成

```bash
git worktree add .claude/worktrees/<topic> -b worktree-<topic> main
cd .claude/worktrees/<topic>
```

#### 5. セットアップ実行

```bash
bash scripts/setup-worktree.sh
```

出力から Frontend port / Backend port / DB port を抽出する。

#### 6. 依存パッケージのインストール (初回のみ)

```bash
cd frontend
[ -d node_modules ] || npm install
```

#### 7. (モードB のみ) .env.local 書き換え

```bash
sed -i.tmp "s|^NEXT_PUBLIC_API_URL=http://localhost:8080|NEXT_PUBLIC_API_URL=http://localhost:<backend-port>|" .env.local
rm .env.local.tmp
```

#### 8. (モードB のみ) Backend と DB を起動

```bash
docker compose up backend db
```

#### 9. Dev サーバー起動 (バックグラウンド)

```bash
PORT=<frontend-port> npm run dev
```

#### 10. 結果報告

```
✅ ワークツリー作成完了

  Path:     .claude/worktrees/<topic>
  Branch:   worktree-<topic>
  Mode:     A or B
  Frontend: http://localhost:<frontend-port>
  Backend:  Main共有 (8080) or Worktree (<backend-port>)
  DB:       Main共有 (5432) or Worktree (<db-port>)
```

### 安全規則

- main 以外のブランチでの実行は必ず確認
- 既存の同名ブランチ・worktreeとの衝突は中止
- npm install / docker / npm run dev の失敗時はそこで停止
````

</details>

Claude Code が SKILL.md の指示通りに、bash コマンドを実行したり、ユーザーにモードを聞いたり、結果をパースしたりしながら、自動でセットアップを進めてくれます。

マージ後の片付けも Skill 化しました。

<details><summary>Skillsの内容</summary>

````.claude/skills/worktree-cleanup/SKILL.md
---
name: worktree-cleanup
description: 作業完了後のワークツリー片付け。devサーバー停止、Docker停止、worktree削除、ブランチ削除までを自動化。Use when user wants to clean up after PR merge, remove a worktree, or finish work on a worktree.
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
---

# Worktree Cleanup スキル

## Instructions

このスキルはマージ後のワークツリー片付けを自動化する。

### 実行フロー

#### 1. 現在地と対象 worktree の特定

```bash
pwd
git worktree list
```

worktree 内なら対象自動判定、main なら複数候補から AskUserQuestion で選択。

#### 2. 未コミット変更チェック

```bash
git status --porcelain
```

ある場合は AskUserQuestion で破棄 or 中止を確認。

#### 3. マージ済みチェック

```bash
git branch --merged main | grep "worktree-<topic>"
```

マージされていない場合は AskUserQuestion で確認。

#### 4. 動作中の dev サーバーを停止

このセッションで起動した npm run dev を **TaskStop** で停止。

#### 5. Worktree backend / DB Docker の停止 (起動していれば)

```bash
docker ps --filter "name=<worktree-name>-" --format "{{.Names}}"
```

起動していれば worktree ルートで:

```bash
docker compose down
```

(backend と db のコンテナがまとめて停止・削除される)

#### 6. main へ移動・最新化

```bash
cd <main-repo-path>
git checkout main
git pull origin main
```

#### 7. Worktree 削除

```bash
git worktree remove .claude/worktrees/<topic>
```

#### 8. ローカルブランチ削除

```bash
git branch -d worktree-<topic>   # マージ済みなら -d
git branch -D worktree-<topic>   # 未マージで確認済みなら -D
```

#### 9. リモート追跡参照の prune

```bash
git fetch --prune
```

### 安全規則

- 未コミット変更がある場合は必ず確認
- 未マージブランチは確認なしに削除しない
- Docker停止前に該当ワークツリーのコンテナか確認 (他worktreeを誤って停止しない)
- main ブランチ自体は絶対に削除しない
````

</details>

## 効果

### worktree作成

```
$ /worktree-new
> Topic: add-terms-page
> Mode: [A] フロントのみ
... (Claude が自動で全部実行)
> ✅ http://localhost:3115 で起動しました
```

このようにスラッシュコマンド1つで完結します。
ポート番号も Claude が出力から自動抽出して `PORT=xxxx npm run dev` まで起動してくれます。
worktree 作成〜開発開始までが **約1分** に短縮されました。

### 片付け

```
$ /worktree-cleanup
... (サーバー停止・Docker停止・worktree削除・ブランチ削除・main最新化)
> ✅ 完了
```

## まとめ

ポート競合と環境変数の管理を、シェルスクリプトと Skills で複数ステップを自動化することができました。

今後もっとAIを工夫して活用していきたいです。
