---
id: "2026-05-05-kiro-cli-の過去セッションを全文検索再開する-kiro-cli-history-01"
title: "Kiro CLI の過去セッションを全文検索・再開する kiro-cli-history"
url: "https://zenn.dev/nemutaizo/articles/61a6134b6e1a05"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

## サマリ

* Kiro CLI は会話を自動保存し `--resume` / `--resume-picker` で再開できるが、**スコープがディレクトリ単位** / **本文検索ができない**（公式 Limitation）
* [`prabhugr/kiro-cli-history`](https://github.com/prabhugr/kiro-cli-history) を入れると、**全ディレクトリ横断の全文 fuzzy 検索 + プレビュー + ワンキー再開** ができる
* Claude Code の `/resume` + `raine/claude-history` と同じ体験を Kiro CLI で再現する補完ツール
* 読み取り専用でセッションデータを壊さない。macOS のみ、依存は Python 3.9+ と `textual` のみ

## はじめに — この Kiro との会話、どこでしたっけ？

複数のリポジトリを行き来しながら Kiro CLI を使っていると、ふとした拍子にこういう場面に遭遇する。

> 「先週くらい、Lambda のコールドスタート削減について Kiro と Provisioned Concurrency と SnapStart のトレードオフを整理したはず。あのときのやり取りを引っ張ってきたい」

ところが、その会話をしたディレクトリを覚えていない。Kiro CLI のセッション一覧は **カレントディレクトリに閉じている** ので、ディレクトリを順に掘っていく羽目になる。おまけにタイトルは UUID か自動生成で、本文を見ないと中身が分からない。

Claude Code を使っている人なら、`/resume` と [`raine/claude-history`](https://github.com/raine/claude-history) の組み合わせでこの問題を既に解決しているはず。同じ体験を Kiro CLI でも欲しい、というのが本記事の出発点である。

答えは既に存在する。[`prabhugr/kiro-cli-history`](https://github.com/prabhugr/kiro-cli-history) がそれを埋めてくれる。

## 1. kiro-cli-history でできること

[`prabhugr/kiro-cli-history`](https://github.com/prabhugr/kiro-cli-history) は、Kiro CLI の全セッションをディレクトリ横断で fuzzy 検索できる TUI ツール。README でも Claude Code 向けの `raine/claude-history` に着想を得たと明記されている。

具体的にできることは以下。

* **全ディレクトリ横断の検索**: カレントディレクトリに縛られない
* **全文 fuzzy 検索**: タイトルだけでなく、ユーザーと Kiro が交わした全メッセージ本文が対象
* **Markdown プレビュー**: 会話全体を読み込んでから再開を判断できる
* **ワンキー再開**: `Ctrl+R` でそのまま Kiro CLI に引き継ぐ
* **クリップボードコピー**: `Ctrl+Y` で会話丸ごとコピー
* **3 ストレージ対応**: v1/v2 SQLite と v3 JSONL をすべて読む（後述）

![](https://static.zenn.studio/user-upload/d462f5a6d764-20260505.gif)

*Demo GIF: [prabhugr/kiro-cli-history](https://github.com/prabhugr/kiro-cli-history) より引用（MIT License）*

Kiro CLI 本体の `--resume-picker` との役割分担はこうなる。

|  | `--resume-picker`（本体） | `kiro-cli-history` |
| --- | --- | --- |
| スコープ | 現在のディレクトリ | **全ディレクトリ横断** |
| 検索対象 | タイトル | **会話の全メッセージ本文** |
| プレビュー | タイトル + メッセージ数 | **Markdown レンダリング付き会話全体** |
| 再開 | そのまま再開 | `Ctrl+R` で Kiro CLI に引き継ぐ |
| 書き込み | する（再開後の会話追記） | **読み取り専用**（再開は Kiro CLI 本体に委譲） |

**補完関係** であって、置き換えるものではない。本体の `--resume-picker` は今のディレクトリで続きをやるときに、`kiro-cli-history` は「どこにあるか分からない過去セッションを探す」ときに使う。

## 2. インストール

macOS 前提。リポジトリを clone して `install.sh` を叩くだけ。

```
git clone https://github.com/prabhugr/kiro-cli-history.git
cd kiro-cli-history
bash install.sh
```

依存は [`textual`](https://github.com/Textualize/textual)（Python 製の TUI フレームワーク）のみで、`install.sh` が自動インストールする。

### PEP 668 エラーに遭遇したら（macOS + Homebrew Python）

`install.sh` は内部で `pip3 install textual` を叩く。macOS に Homebrew の Python を入れている環境だと、[PEP 668](https://peps.python.org/pep-0668/) の保護でこれが失敗する。

```
error: externally-managed-environment

× This environment is externally managed
```

最もクリーンな回避策は **venv に閉じ込める** 方式。手動でインストール手順を組み替える。

```
# 1. 中断したインストールをクリーンアップ
rm -rf ~/.local/share/kiro-cli-history
rm -f ~/.local/bin/kiro-cli-history

# 2. venv を作って textual を入れる
mkdir -p ~/.local/share/kiro-cli-history
python3 -m venv ~/.local/share/kiro-cli-history/venv
~/.local/share/kiro-cli-history/venv/bin/pip install --quiet textual

# 3. kiro_history.py を配置（cloneしたリポジトリのディレクトリで実行）
cp kiro_history.py ~/.local/share/kiro-cli-history/kiro_history.py

# 4. venv の Python を使うラッパーを自作
mkdir -p ~/.local/bin
cat > ~/.local/bin/kiro-cli-history << 'EOF'
#!/usr/bin/env bash
exec "$HOME/.local/share/kiro-cli-history/venv/bin/python3" \
  "$HOME/.local/share/kiro-cli-history/kiro_history.py" "$@"
EOF
chmod +x ~/.local/bin/kiro-cli-history

# 5. PATH 確認（入ってなければ .zshrc に追記）
[[ ":$PATH:" == *":$HOME/.local/bin:"* ]] || \
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

これで **システム Python を一切触らず**、`textual` は専用 venv に隔離される。アンインストールも `rm -rf ~/.local/share/kiro-cli-history ~/.local/bin/kiro-cli-history` だけで綺麗に消える。

`--break-system-packages --user` フラグで突破する方法もあるが、後始末が面倒なので上記の venv 方式を推奨する。

### 起動

どのディレクトリから起動しても、全セッションが見える。

## 3. 実際の使い方

### ケース 1: 全文検索で埋もれたセッションを掘り起こす

冒頭の例そのまま。「先週、Lambda のコールドスタートについて Kiro と整理したはず」を思い出したいが、ディレクトリを覚えていない状況。

* `kiro-cli-history` を起動
* `/` を押して検索バーに `コールドスタート` と入力
* 本文中に該当語を含むセッションが一覧でヒット
* プレビューペインで会話の抜粋を確認、目的のセッションを特定
* `Ctrl+R` でそのまま Kiro CLI に引き継いで続きを依頼

タイトルを覚えていなくても、**会話の中で使った単語が 1 つ思い出せれば辿れる**。体感的にはこれが一番大きい。

### ケース 2: 別プロジェクトで整理した方針を新プロジェクトに引き継ぐ

複数の CDK プロジェクトを行き来していると、**同じ課題に 2 回目以降ぶつかる** ことがある。

たとえば以前の S3 通知 Lambda プロジェクトで、Secrets Manager の取得キャッシュ戦略（Lambda 内でモジュールスコープにキャッシュ、TTL は 10 分、エラー時は指数バックオフ）を Kiro と詰めた経験があったとする。新しい Lambda プロジェクトで同じ論点に直面したとき、ゼロから議論し直すのは時間の無駄になる。

* `kiro-cli-history` で `Secrets Manager キャッシュ` を検索
* 過去の会話を発見、プレビューで方針を再確認
* `Ctrl+Y` で会話全体をクリップボードにコピー
* 新プロジェクトの Kiro CLI セッションに貼り付けて「**この方針を踏襲して今回も実装して**」とプロンプト化

実質 **自分専用のナレッジベース** が Kiro CLI のセッション履歴から立ち上がる感覚に近い。

### ケース 3: 会話ログをそのままドキュメント化の叩き台にする

Kiro との試行錯誤のログは、後から見ると、それ自体がドキュメントの素材になる。

* 社内 Wiki / Obsidian のノート化
* ブログ記事（まさにこの記事もそう）の下書き
* 議事メモ / トラブルシュート記録

`Ctrl+Y` でセッション全体をコピーできるので、貼り付け先に流し込むだけ。Markdown として読める形式で出力されるので、見出しやコードブロックの再整形は最小限で済む。

個人的には **ブログ下書きへの叩き台としての使い方が一番ハマっている**。Kiro に雑に相談して、論点整理ができた時点でコピー、Zenn の下書きに貼ってリライトする、という流れ。

### キーバインド

| キー | 動作 |
| --- | --- |
| `/` or `Ctrl+F` | 検索バーにフォーカス |
| `j` / `k` / 矢印 | セッション移動 |
| `Ctrl+R` | ハイライト中のセッションを Kiro CLI で再開 |
| `Ctrl+Y` | 会話をクリップボードにコピー |
| `Esc` | 検索クリア / 終了 |
| `Ctrl+C` | 終了 |

プレビューペインのテキスト選択は **Option (Alt) + ドラッグ** で OK（ターミナルのマウス挙動を避けるため）。

## 4. Kiro CLI 本体のセッション管理と、埋める穴

ここから先は、Kiro CLI 本体のセッション管理機能を押さえたい人向け。本ツールがなぜ必要なのかを、公式機能の整理とともに見ていく。

### 4.1 本体の機能

Kiro CLI は **全ての会話ターンを自動的にローカル DB に保存** する（公式ドキュメント [Session Management](https://kiro.dev/docs/cli/chat/session-management/)）。

* **保存頻度**: 会話のターンごとに都度保存
* **スコープ**: ディレクトリごと（プロジェクトごとに独立）
* **保存先**: `~/.kiro/` 配下の SQLite データベース
* **セッション ID**: UUID（例: `f2946a26-3735-4b08-8d05-c928010302d5`）

コマンドラインから操作できるフラグ:

```
kiro-cli chat --resume              # 最後のセッションを再開
kiro-cli chat --resume-picker       # インタラクティブに選んで再開
kiro-cli chat --list-sessions       # セッション一覧
kiro-cli chat --delete-session <ID> # セッション削除
```

チャット起動中は `/chat` サブコマンド:

```
/chat new                   # 新規会話（現在のセッションは自動保存）
/chat resume                # インタラクティブに再開
/chat save <path>           # ファイルに保存
/chat load <path>           # ファイルから読み込み
/chat save-via-script <sh>  # スクリプト経由で保存（stdin で JSON を受ける）
/chat load-via-script <sh>  # スクリプト経由で読み込み（stdout に JSON を出す）
```

`save-via-script` / `load-via-script` は面白い機構で、公式ドキュメントには **Git Notes に会話を保存する例** が載っている。コミットハッシュに紐付けて会話履歴をリポジトリで管理する、というユースケースはチーム運用と相性が良さそう。

### 4.2 公式が認める限界

公式ドキュメントの **Limitations セクション** に以下が書かれている。

> * Sessions stored per-directory
> * Auto-save to database only (not files)
> * Session IDs are UUIDs (not human-readable)
> * No cloud sync (use scripts for custom storage)
> * **No session search by content**

最後の「**No session search by content**」が本記事の動機そのもの。ディレクトリを横断した本文検索は **標準機能に存在しないことが公式に明記されている**。`--resume-picker` はカレントディレクトリ内のセッションを UUID とタイトルで見せるだけで、fuzzy 検索でも全文検索でもない。

`kiro-cli-history` はこの穴をピンポイントで埋めるツールと位置付けられる。

## 5. 仕組み — なぜ 3 つのストレージ形式を読むのか

Kiro CLI のセッション永続化は、バージョンによって実装が変遷している。

| 形式 | 保存場所 | 使用モード |
| --- | --- | --- |
| v3（JSONL） | `~/.kiro/sessions/cli/*.json` + `*.jsonl` | `kiro-cli --classic` |
| v2（SQLite） | `~/Library/Application Support/kiro-cli/data.sqlite3` | 新 TUI モード（`kiro-cli`） |
| v1（SQLite） | 同じ DB の `conversations` テーブル | レガシー |

`kiro-cli-history` は **この 3 形式すべてを読んで統一ビューに出す**。単純な grep では辿れない理由がここにある。

一覧表示される情報:

* **Title**: 最初のメッセージ or 自動生成タイトル
* **Directory**: セッションが開始されたディレクトリ
* **Date**: 最終アクティビティ（例: "7 Apr 2026"）
* **Message count**: 往復メッセージ数
* **Duration**: 会話の継続時間

### 読み取り専用設計

強調されているのは **ツール側は一切書き込まない** という設計。

* `~/.kiro/sessions/cli/`（JSONL）は読むだけ
* `~/Library/Application Support/kiro-cli/data.sqlite3` は **SQLite を read-only モードで open**

`Ctrl+R` での再開も、`kiro-cli-history` が書き込むわけではなく、**Kiro CLI 本体を起動するランチャー** として振る舞う。以降の会話追記は Kiro CLI 本体の責務になる。セッションデータを壊す経路が構造的にない。

## 6. 注意点

* **macOS のみ**（クリップボードに `pbcopy`、パスも macOS 固有の `~/Library/Application Support/`）
* Linux / Windows は未対応、Community PR 歓迎とのこと
* バージョンは **v0.1.0**（2026/04/06 リリース）、Star もまだ少ない
* 本家 Kiro CLI 側で `--resume-picker` が全ディレクトリ横断 / 本文検索に拡張されれば、本ツールの役割は変わる可能性がある
* 前述の通り **書き込みはしない** ので、試して合わなくてもデータは壊れない

## まとめ

* Kiro CLI 本体のセッション管理は、**自動保存・ディレクトリ単位の再開・カスタムスクリプト連携** までは揃っている
* 一方で **全ディレクトリ横断の本文検索は公式 Limitation として明記** されていて、複数プロジェクトを行き来する使い方だと痛い
* `kiro-cli-history` はこの穴を埋める補完ツールで、**Claude Code の `/resume` + `raine/claude-history` 体験を Kiro CLI にもたらす**
* 読み取り専用・macOS のみ・v0.1.0 と気軽に入れられる規模なので、同じ悩みを抱えていれば試す価値は高い

本家側で同種機能が出てくれば嬉しいし、それまでは `kiro-cli-history` で回す、くらいの位置付けで日常的に使っている。

## 参考リンク
