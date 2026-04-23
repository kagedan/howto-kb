---
id: "2026-03-23-claude-code-cursor-wsl-完全セットアップガイドwindows-01"
title: "Claude Code × Cursor × WSL 完全セットアップガイド（Windows）"
url: "https://qiita.com/LingmuSajun/items/bdcaa74e1cbfa54515a2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

# Claude Code × Cursor × WSL 完全セットアップガイド（Windows）

> **対象**: Windows 10/11 ・ ツール未インストールの状態からスタート  
> **ゴール**: WSL + Cursor + Claude Code の本格開発環境を構築し、育てていく

---

## 全体の流れ

```
① WSL（Ubuntu）のインストール & 初期設定
② WSL内に Claude Code をインストール
③ Anthropicアカウント認証（Claude Pro / Max 必須）
④ Cursor インストール & WSL連携
⑤ プロジェクトフォルダの作り方 & claude 起動
⑥ CLAUDE.md で Claude Code を「育てる」
```

---

## ① WSL（Ubuntu）のインストール

### WSLとは？

Windows上でLinux（Ubuntu）を動かすMicrosoft公式の仕組み。  
Claude CodeはもともとLinux/macOS向けに設計されているため、  
WSL経由が最も安定してパフォーマンスも良い。

### 1-1. Windowsバージョンの確認

`Win + R` → `winver` と入力してEnter。

* Windows 10: ビルド19041以降が必要
* Windows 11: そのままOK

### 1-2. WSLのインストール

**PowerShellを「管理者として実行」する:**

* `Win + X` → 「ターミナル（管理者）」または「PowerShell（管理者）」

これ1行で以下がすべて自動実行される:

* WSL機能の有効化
* 仮想マシンプラットフォームの有効化
* Linuxカーネルのインストール
* Ubuntuのダウンロード＆展開

### 1-3. 再起動

⚠️ **再起動は必須。** スキップするとWSLが正常に動作しない。

### 1-4. Ubuntuの初期設定

再起動後、以下のいずれかでUbuntuを起動:

* 自動でUbuntuのウィンドウが開く（数分待つ）
* スタートメニューで「Ubuntu」を検索して起動
* PowerShellで `wsl` と入力

**初回起動時にユーザー名とパスワードを設定する:**

```
Enter new UNIX username: lingmu
New password: ********
Retype new password: ********
```

> ⚠️ Windowsのユーザー名/パスワードと一致させる必要はない。  
> パスワードは `sudo` コマンド（管理者権限の実行）で使うので覚えておく。

### 1-5. Ubuntuを最新状態に更新

```
sudo apt update && sudo apt upgrade -y
```

### 1-6. WSLバージョンの確認

PowerShell（Windows側）で:

```
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

VERSION が `2` であればOK（WSL2のほうが高速＆サンドボックス対応）。

もし `1` だった場合:

```
wsl --set-version Ubuntu 2
```

---

## ② WSL内に Claude Code をインストール

WSL（Ubuntu）のターミナルで作業する。  
ネイティブインストーラーを使うので **Node.js は不要**。

```
curl -fsSL https://claude.ai/install.sh | bash
```

### 確認

```
claude --version
# → バージョン番号が表示されればOK
```

---

## ③ Anthropicアカウント認証

Claude Codeは **有料プラン（Claude Pro $20/月〜 または Claude Max）** が必要。

初回実行時にブラウザ認証のURLが表示される。  
URLをコピーしてWindows側のブラウザで開き、Anthropicアカウントでログイン。  
認証コードが表示されたら、ターミナルに貼り付けてEnter。

### 💡 プランの選び方

| プラン | 月額 | おすすめ用途 |
| --- | --- | --- |
| Claude Pro | $20 | まず試したい人。学習・個人開発 |
| Claude Max 5x | $100 | 本格的にClaude Codeを使い倒したい人 |
| Claude Max 20x | $200 | ヘビーユーザー・大規模開発 |
| API（従量課金） | 使った分 | 自動化パイプライン向け |

> まずProで始めて使用量を把握 → 本格利用ならMaxへ切り替えが合理的。

---

## ④ Cursor インストール & WSL連携

### 4-1. CursorをWindows側にインストール

1. **<https://www.cursor.com>** からダウンロード＆インストール
2. VS Codeとほぼ同じ使い勝手

### 4-2. WSL拡張機能をインストール

Cursor内で `Ctrl + Shift + X`（拡張機能ビュー）を開き:

1. **「WSL」** で検索 → Microsoft製の「WSL」拡張機能をインストール
2. **「Claude Code」** で検索 → インストール

### 4-3. CursorからWSLに接続する

**方法A: コマンドパレットから（推奨）**

1. `Ctrl + Shift + P` → 「WSL: Connect to WSL」を選択
2. 左下に「WSL: Ubuntu」と表示されれば接続成功

**方法B: WSLターミナルから（こちらも便利）**

```
# WSLのUbuntuターミナルで、プロジェクトフォルダに移動して:
cursor .
```

→ CursorがWSL接続モードで自動的に開く

### 4-4. 接続確認

Cursorの左下ステータスバーに以下が表示されていればOK:

Cursor内でターミナルを開くと（``` Ctrl + `` ``` ）、  
**自動的にWSL（Ubuntu）のシェルが起動する。**

---

## ⑤ フォルダ構成 & claude の起動方法

### 🔑 核心: どこにプロジェクトを作るか？

**結論: WSLのLinuxファイルシステム内（`~/` 以下）にプロジェクトを作る。**

| 場所 | パス例 | 速度 | 推奨 |
| --- | --- | --- | --- |
| **Linux側（推奨）** | `~/Projects/my-app/` | ⚡ 高速 | ✅ |
| Windows側 | `/mnt/c/Users/.../my-app/` | 🐢 遅い | ❌ |

Windows側（`/mnt/c/`）はファイルI/Oが大幅に遅くなるため、  
**必ずLinux側に作業フォルダを置く。**

### おすすめフォルダ構成

```
# WSLのUbuntuターミナルで作成:
mkdir -p ~/Projects
```

```
~/                                  ← WSLのホームディレクトリ
├── .claude/
│   └── CLAUDE.md                   ← グローバル設定（全プロジェクト共通）
└── Projects/                       ← プロジェクト群の親フォルダ
    ├── my-webapp/                  ← Cursorでこのフォルダを開く
    │   ├── CLAUDE.md               ← プロジェクトメモリ
    │   ├── .claude/                ← Claude Code設定（自動生成）
    │   ├── src/
    │   └── ...
    ├── study-project/              ← 別プロジェクト
    │   ├── CLAUDE.md
    │   └── ...
    └── sandbox/                    ← 実験・お試し用
        ├── CLAUDE.md
        └── ...
```

### 起動手順（毎日のワークフロー）

#### Step 1: WSLのターミナルからCursorを開く

```
cd ~/Projects/my-webapp
cursor .
```

#### Step 2: Cursorのターミナルで claude を起動

Cursor内で ``` Ctrl + `` ```  でターミナルを開き:

#### Step 3: 初回は `/init` で自動セットアップ

→ Claude Codeがプロジェクト構造を読み取り、`CLAUDE.md` を自動生成。

### IDE連携の確認

Cursorのターミナルで `claude` を起動すると、自動的にIDE連携が有効になる。  
ウニマーク（✱）がCursorのサイドバーに表示される。

もし連携されない場合は、Claude Code内で `/ide` と入力してCursorを選択。

---

## ⑥ CLAUDE.md で Claude Code を「育てる」

CLAUDE.mdは **Claude Codeの「プロジェクトメモリ」** 。  
一度書けば毎セッション自動で読み込まれ、いちいち説明し直す必要がなくなる。

### CLAUDE.md の3つのスコープ

| スコープ | 場所 | 用途 |
| --- | --- | --- |
| **グローバル** | `~/.claude/CLAUDE.md` | 全プロジェクト共通の個人設定 |
| **プロジェクト** | `プロジェクトルート/CLAUDE.md` | プロジェクト固有のルール（Git管理推奨） |
| **ローカル** | `プロジェクトルート/.claude/CLAUDE.md` | 個人的なローカル設定（Git管理外） |

優先順位: ローカル > プロジェクト > グローバル

### 最初に作る: グローバル設定

```
mkdir -p ~/.claude
nano ~/.claude/CLAUDE.md
```

以下を貼り付けて保存（`Ctrl + O` → Enter → `Ctrl + X`）:

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

### プロジェクト CLAUDE.md のテンプレート

新しいプロジェクトを始めたら `/init` で自動生成するのが最速。  
生成後、以下のようなプロジェクト固有情報を追記する:

```
# プロジェクト名

## 概要
- What: ○○するWebアプリ
- Why: ○○の課題を解決するため
- Who: ○○向け

## 技術スタック
- フレームワーク: Next.js 14
- 言語: TypeScript
- スタイリング: Tailwind CSS
- DB: PostgreSQL + Prisma

## コマンド
- `npm run dev` - 開発サーバー起動（localhost:3000）
- `npm run build` - ビルド
- `npm run test` - テスト実行
- `npm run lint` - Lint実行

## ディレクトリ構成
- src/app/ - ページ（App Router）
- src/components/ - UIコンポーネント
- src/lib/ - ユーティリティ
- src/types/ - 型定義

## ルール
- 新しい機能は必ずブランチを切って作業する
- mainブランチへの直接コミットは禁止
- テストを書いてから実装する（TDD）

## 注意事項
- APIキーは.envファイルで管理（Gitにコミットしない）
```

### 育て方のコツ

#### 1. `/init` で骨格を自動生成

新規プロジェクトで最初に `/init` を実行すれば、  
Claude Codeがプロジェクト構造を読み取ってCLAUDE.mdを自動生成。

#### 2. 作業中に `#` キーで追記

セッション中に `#` を押すと、Claude CodeがCLAUDE.mdに自動で追記してくれる。

#### 3. 「CLAUDE.mdに追記しといて」で自動更新

プロンプトで「この作業手順、毎回やるからCLAUDE.mdに書いといて」と伝えれば、  
Claude Code自身が更新してくれる。勝手に育つ。

#### 4. 自動メモリ機能（v2.1.59以降）

Claude Codeは作業中に自分でメモを保存する。  
ビルドコマンド、デバッグの洞察、コードスタイルの好みなどを自動学習・蓄積。

#### 5. 60〜300行以内に保つ

公式推奨。長すぎると無視される可能性が上がる。  
肥大化したら `.claude/rules/` ディレクトリにルールファイルを分割する。

#### 6. 一般的すぎる情報は書かない

「componentsフォルダにコンポーネントを置く」のような当たり前の情報は不要。  
Claudeはすでに知っている。**プロジェクト固有の「変わった部分」** を書く。

---

## 💡 日常の使い方Tips

### よく使うコマンド

| コマンド | 説明 |
| --- | --- |
| `/init` | CLAUDE.md自動生成 |
| `/clear` | コンテキストをリセット（タスク切り替え時に） |
| `/help` | ヘルプ表示 |
| `/ide` | IDE連携の設定 |
| `/cost` | セッションのコスト確認 |
| `/doctor` | 環境ヘルスチェック |
| `/terminal-setup` | Shift+Enter改行の設定 |

### 思考レベルの指定

プロンプトにキーワードを含めると、Claudeにより深い思考を促せる:

| キーワード | 思考の深さ | 用途 |
| --- | --- | --- |
| `think` | 基本 | 通常のタスク |
| `think hard` | 深い | 設計判断 |
| `think harder` | さらに深い | 複雑なバグ |
| `ultrathink` | 最大 | アーキテクチャ設計 |

### Cursorとの使い分け

| やりたいこと | 使うツール |
| --- | --- |
| 複数ファイルの一括変更 | Claude Code |
| ターミナルコマンドの実行 | Claude Code |
| Git操作（commit, PR作成） | Claude Code |
| プロジェクト全体の分析 | Claude Code |
| ピンポイントのコード編集 | Cursor AI |
| コード補完 | Cursor AI |
| UIを見ながら微調整 | Cursor AI |

### 権限設定のコツ

Claude Codeは実行前に許可を求めてくる。

* `Yes` を選ぶと `.claude/settings.local.json` に自動追記される
* 次回から同じコマンドは確認なしで実行される
* 危険なコマンド（`git push origin main` など）は `deny` にしておくと安心

---

## ⚠️ トラブルシューティング

### 「claude: command not found」（WSL内）

```
# PATHを確認
echo $PATH
# インストールし直し
curl -fsSL https://claude.ai/install.sh | bash
source ~/.bashrc
```

### 認証が切れた（401エラー）

```
claude auth logout
claude auth login
```

### WSLが起動しない / エラーが出る

```
# PowerShell（管理者）で:
wsl --update
wsl --shutdown
wsl
```

### Cursorでウニマークが出ない

→ 拡張機能からClaude Codeをインストール。Cursor再起動。

### WSL接続時に「Could not fetch remote environment」

→ Cursor内で `Ctrl + Shift + P` → 「WSL: Connect to WSL」を再実行。

### Windowsのパスにあるファイルにアクセスしたい

```
# WSLからWindows側のファイルにアクセス:
ls /mnt/c/Users/<Windowsユーザー名>/Desktop/
# ただし速度が遅いので、作業はLinux側で行うこと
```

### WSLのメモリ使用量を制限したい

Windows側に設定ファイルを作成:

`C:\Users\<ユーザー名>\.wslconfig`:

```
[wsl2]
memory=8GB
processors=4
swap=2GB
```

設定後:

---

## 📋 セットアップ完了チェックリスト

```
[ ] WSL（Ubuntu）が起動する
[ ] WSLのバージョンが 2 である
[ ] claude --version でバージョンが表示される
[ ] claude で認証が通り、対話できる
[ ] CursorをWindows側にインストールした
[ ] CursorにWSL拡張機能をインストールした
[ ] CursorにClaude Code拡張機能をインストールした
[ ] CursorからWSLに接続できる（左下に「WSL: Ubuntu」表示）
[ ] Cursorのターミナルで claude が起動する
[ ] ~/.claude/CLAUDE.md にグローバル設定を書いた
[ ] プロジェクトフォルダで /init を実行した
```

---

## 📚 参考リンク
