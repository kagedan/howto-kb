---
id: "2026-05-21-claude-code-obsidian-で知識の記録役を雇う運用をしてみた話-01"
title: "Claude Code × Obsidian で「知識の記録役」を雇う運用をしてみた話"
url: "https://zenn.dev/kenya0126/articles/205dc56cf36ee3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "zenn"]
date_published: "2026-05-21"
date_collected: "2026-05-22"
summary_by: "auto-rss"
query: ""
---

## 想定読者

* Claude Code を日常的に使っているが、過去セッションの判断や試行錯誤が流れていくのが気になっている人
* Obsidian で開発ノートを取っているが、Claude に毎回ゼロから前提を説明し直すのが面倒な人
* 「AI とのやり取りそのもの」を資産化したい人

## アウトライン

1. なぜ memory だけでは足りないのか — 二層永続化の発想
2. 全体像 (A+B+C+D ワークフロー)
3. ステップ 1: Vault を Git 化する
4. ステップ 2: Vault に `CLAUDE.md` を置く
5. ステップ 3: Claude 側 memory を組む
6. ステップ 4: Obsidian MCP を入れる
7. ステップ 5: テンプレ補助スキル (`/save-session` 等) を作る
8. 陰としての Vault / 陽としての memory の使い分け
9. 一週間使ってみた所感とつまづいたところ
10. まとめ

### 1. なぜ memory だけでは足りないのか

Claude Code には自動 memory 機能があり、`~/.claude/projects/{path}/memory/MEMORY.md` をインデックスとして次セッションに引き継いでくれる。ユーザーの好み、過去の判断、よくあるミスなどを feedback / project / user / reference の 4 タイプで蓄積していくものだ。

ただし memory には弱点がある。

* **人間が読み返しにくい**: フラットなファイル群で、横断検索や時系列確認には向かない
* **wikilink / 図 / 添付がない**: ノートツールとしての構造化に欠ける
* **「言いっぱなしの記録」になりがち**: 自分の知識ベースとして再利用する経路がない

逆に Obsidian Vault には:

* 自分が普段の知識ベースとして使い続けている (検索・wikilink・グラフビュー)
* でも Claude は明示的に指示しないと参照してくれない
* 毎回「Vault の○○を読んで」と書くのは面倒

→ **両方の弱点を相互補完させる** のが本記事のテーマ。

---

### 2. 全体像 (A+B+C+D ワークフロー)

ルールはたった 4 つ。

| ルール | やること | 保存先 |
| --- | --- | --- |
| **A. プロジェクトハブ起点** | 開発タスク開始時に `01-Projects/{プロジェクト名}/README.md` を最初に読む | Vault |
| **B. セッション末ログ** | 区切りで `/save-session` を実行 → `Claude Sessions/{プロジェクト名}/{日付}-{概要}.md` | Vault |
| **C. ミス記録** | ユーザーに指摘されたミスを `02-Areas/Claude運用/コーディングミスログ.md` 先頭に追加 + memory にも feedback として保存 | Vault + memory |
| **D. 知識蓄積** | 読んだ Zenn / 学んだこと / 書きたい記事を `03-Resources/` `02-Areas/Zenn執筆/` に蓄積 | Vault |

A と B は「開発タスクのプロローグとエピローグ」、C は「学習ループ」、D は「副産物の整理」だ。

Vault のディレクトリ構成は以下:

```
Obsidian Vault/
├── 00-Inbox/           # 未整理ノート
├── 01-Projects/        # アクティブな開発プロジェクト ← A の起点
├── 02-Areas/           # 継続管理する領域 (Claude運用 / Zenn執筆 など)
├── 03-Resources/       # 参考資料 (Zenn記事メモ / 学習メモ)
├── 04-Archive/         # 完了済み (編集禁止)
├── Claude Sessions/    # ← B の保存先
├── Templates/          # 各種テンプレート
└── CLAUDE.md           # ← Claude への指示書
```

---

### 3. ステップ 1: Vault を Git 化する

複数台 (例: Mac と Windows) で同じ Vault を使うため、Git 管理 + プライベートリポジトリで同期させる。

```
cd "/path/to/Obsidian Vault"
git init
gh repo create your-name/obsidian-vault --private --source=. --remote=origin
```

`.gitignore` はマシン固有ファイルだけ除外する。`.obsidian/plugins/` 等はコミット対象に含め、別マシンでも同じ環境を再現できるようにする。

```
# Obsidian の作業状態 (マシン固有)
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# macOS
.DS_Store
```

同期は **[obsidian-git](https://github.com/Vinzent03/obsidian-git)** プラグインに任せる。私の設定は:

* `Auto pull`: 5 分間隔 + 起動時
* `Auto push`: **無効** (`autoPushInterval: 0`)
* `Pull before push`: 有効

push を自動化していないのは、コミットメッセージを書くタイミングを自分でコントロールしたかったから。`Cmd+P → Git: Commit and push` で明示的に push する。

#### ハマりポイント: ホームディレクトリが Git リポジトリになっていないか確認

私は実際にやらかしたのだが、過去にホームディレクトリで何かを `git init` していて、`~/.git` が別のリポジトリを指していた状態だった。Vault を Git 管理しようとすると、ホーム配下のすべてのファイルが「未追跡」として浮かび上がって気付くこともある。

```
ls -la ~/.git  # ← 存在したら要確認
```

身に覚えがなければ削除して構わない。

---

### 4. ステップ 2: Vault に `CLAUDE.md` を置く

`CLAUDE.md` は Claude Code が起動時に自動で読み込む指示書。ここに「Vault 内ではこう振る舞ってほしい」を集約する。

`/path/to/Obsidian Vault/CLAUDE.md`:

```
# Obsidian Vault — Claude Operation Rules

このディレクトリは Obsidian vault です。
ファイル操作は Obsidian MCP ツール経由で行ってください
(直接のファイルシステム操作ではなく)。
理由: wikilink整合性、frontmatter保護、Obsidian側のキャッシュ同期のため。

## ディレクトリ構成
- `00-Inbox/` — 未整理ノート
- `01-Projects/` — アクティブな開発プロジェクト
- `02-Areas/` — 継続管理する領域
- `03-Resources/` — 参考資料
- `04-Archive/` — 完了済み (編集禁止)
- `Claude Sessions/` — Claude との作業ログ

## 開発時のワークフロー (A+B 併用)

### A. プロジェクトハブを起点に作業する
ユーザーが開発タスクを依頼したら、まず
`01-Projects/{プロジェクト名}/README.md` を探して読む。
- 存在すれば: 課題・意思決定ログ・落とし穴を把握してから作業開始
- 存在しなければ: `Templates/Project README Template.md` から作成を提案
- 重要な意思決定は README の「意思決定ログ」に追記

### B. セッション終了時にログを残す
`/save-session` を使うか
`Claude Sessions/{プロジェクト名}/{YYYY-MM-DD}-{概要}.md` に記録。
- frontmatter必須: tags (claude, プロジェクト名), date
- 何を変えた / なぜそうした / 次にやること を必ず含める

### C. コーディングミスの記録
私 (Claude) がミスをした場合:
- `02-Areas/Claude運用/コーディングミスログ.md` 先頭に追加
- 同時に Claude 側 memory (feedback type) にも保存

### D. 知識・記事の蓄積
- 読んだ記事: `03-Resources/Zenn記事メモ/`
- 自分が書く記事: `02-Areas/Zenn執筆/drafts/`
- わからなかったこと: `03-Resources/学習メモ/` (status frontmatter で管理)

## 禁止事項
- `04-Archive/` 以下は編集禁止
- ファイル削除は必ず事前確認
- リネーム時は wikilink への影響を報告
```

ポイントは「直接 fs 操作ではなく MCP 経由で」と明示すること。Obsidian のキャッシュが食い違うのを防ぐためだ (実際には MCP が落ちている時の fallback ルールも考えておくと良い)。

---

### 5. ステップ 3: Claude 側 memory を組む

Claude Code の memory は `~/.claude/projects/{path}/memory/` 配下にファイル群として保存される。`MEMORY.md` がインデックスで、各メモは個別ファイルだ。

私は最初に 4 つだけ仕込んだ:

```
memory/
├── MEMORY.md                   # インデックス
├── user_profile.md             # type: user
├── obsidian_workflow.md        # type: feedback (運用ルール)
├── feedback_log_mistakes.md    # type: feedback (ミス記録ルール)
└── project_vault_git.md        # type: project (Vault Git 構成)
```

`MEMORY.md` の中身は一行サマリの集まり:

```
- [User profile](user_profile.md) — 〜
- [Obsidian workflow](obsidian_workflow.md) — A+B ワークフロー: 〜
- [Log my coding mistakes](feedback_log_mistakes.md) — 〜
- [Obsidian Vault Git setup](project_vault_git.md) — 〜
```

各ファイルは frontmatter + 本文。`type: feedback` のものは「ルール / Why / How to apply」の 3 段構成で書くと Claude が判断に使いやすい。例:

```
---
name: obsidian_workflow
description: How to use the Obsidian vault for development collaboration
metadata:
  type: feedback
---

開発タスク時の運用ルール。

**A. プロジェクトハブを起点にする**
- 開発タスク依頼時、まず `01-Projects/{プロジェクト名}/README.md` を読む
- なければ Templates から作成を提案
- 重要な意思決定は README の「意思決定ログ」に追記

**B. セッション終了時にログを残す**
- `/save-session` か `Claude Sessions/...` に手動保存

**Why:** コードに残らない判断理由を蓄積すると次セッションでゼロ説明が不要

**How to apply:** MCP 経由でファイル操作する (直接 fs は禁止)

関連: [[feedback_log_mistakes]]、[[project_vault_git]]
```

`[[name]]` で他 memory への wikilink も使える。

---

### 6. ステップ 4: Obsidian MCP を入れる

Vault を Claude から操作するには [obsidian-mcp](https://github.com/MarkusPfundstein/mcp-obsidian) 等の MCP サーバーを入れる。Local REST API プラグインと組み合わせて、`vault_list` / `vault_read` / `vault_write` / `vault_append` / `vault_patch` などのツールが使えるようになる。

これで Claude が `mcp__obsidian__vault_read` のように Vault 内ファイルを直接読み書きできる。CLAUDE.md と memory が組み合わさることで、Claude は:

1. プロジェクトハブを開いて現状把握
2. 作業
3. 意思決定を README に追記
4. セッション末にログ生成

を自然な流れで行える。

#### Fallback ルールも書いておく

MCP は時々落ちる。落ちた時にどうするかも CLAUDE.md か memory に書いておくと良い。私のところでは「MCP ダウン時は読み取りに限り fs フォールバック可、書き込みは MCP 復帰待ち or 明示確認」というルールにしている。

---

### 7. ステップ 5: テンプレ補助スキル (`/save-session` 等) を作る

Claude Code のスキル機能で、Vault 運用の繰り返し作業をテンプレ化する。

`~/.claude/skills/save-session.md`:

```
今回のセッション内容を要約し、Obsidian MCP の append_content ツールを使って
vault の `Claude Sessions/{プロジェクト名}/{今日の日付}-{概要}.md` に保存してください。

含める内容:
- frontmatter (tags: [claude, プロジェクト名], date: YYYY-MM-DD)
- ## 解決した課題
- ## 主要な意思決定
- ## 変更したファイル
- ## 次回への申し送り

プロジェクト名は現在の作業ディレクトリ名から推測してください。
概要は内容を端的に表す日本語の短いフレーズで。
```

これを `/save-session` として呼べる。同様に:

* `/daily` — その日のデイリーノートを開く / 作る
* `/organize-inbox` — `00-Inbox/` を見て分類提案する

スキルは「Claude に手順を毎回説明する手間」を消す。

---

### 8. 陰としての Vault / 陽としての memory の使い分け

memory と Vault は守備範囲を分ける。

| 観点 | memory | Vault |
| --- | --- | --- |
| 想定読者 | Claude (機械) | 自分 (人間) |
| ロード | 自動 (毎セッション) | 明示 (Claude が読みに行く) |
| 形式 | 短い、原則ベース | 長い、文脈・図・履歴あり |
| 例 | 「ユーザーはこの言語が好き」 | 「2026-05-20: A 案を採用した理由」 |
| 更新頻度 | 低 (ルール変更時のみ) | 高 (セッションごとに追記) |

迷ったら「**人間が後で読み返したいか?**」で判断する。Yes なら Vault、No (Claude にだけ覚えていてほしい) なら memory。

ミス記録だけは両方に書く。memory に書かないと次回 Claude が忘れる、Vault に書かないと人間が一覧できないからだ。

---

### 9. 一週間使ってみた所感

良かったこと:

* **再開コストが劇的に下がった**: 新しいセッションでも「○○プロジェクトを進めて」と言うだけで、Claude が `README.md` を読み、状況を把握し、続きから作業に入る
* **判断のやり直しが減った**: 「なぜ A 案にしたか」が README に残るので、後から「やっぱり B では?」と蒸し返しても根拠を出せる
* **副産物の Zenn ネタが溜まる**: 学習メモや「うまくいった構成」が `02-Areas/` `03-Resources/` に貯まる (本記事もそれ)

つまづいたところ:

* **MCP の不安定さ**: たまに落ちる。fallback ルールを memory に書いておくのが必須
* **Vault と memory の二重管理**: ルール変更時に両方更新が必要 (ただし C ルールのおかげで自動化されつつある)
* **「ハブを作る前に作業を始めてしまう」**: ハブ未作成のままコーディングを進めて後から作る羽目になることが何度かあった → CLAUDE.md に「最初にハブを探す」を強調して改善

---

### 10. まとめ

* Claude Code の memory だけだと「人間が読み返す」用途に弱い
* Obsidian Vault を併用し、`memory = 機械の短期記憶`, `Vault = 人間の長期記憶` と役割分担する
* ルールは A (ハブ起点) / B (セッションログ) / C (ミス記録) / D (知識蓄積) の 4 つ
* Vault は Git 管理 + obsidian-git で複数台同期
* CLAUDE.md + memory + Obsidian MCP + 補助スキルで「Claude を知識の記録役として雇う」運用が完成する

「AI とのやり取り自体を資産化したい」人にはおすすめの構成です。

---

## メモ

* 参考にした記事: [[]]
* 関連する自分の学習メモ: [[]]
* 関連プロジェクト: [[eisai-manager/README]] (この運用で実際に進めているプロジェクト)
* 公開前チェック: スクショ差し込み? / Claude Code バージョン明記? / Vault ディレクトリ図を Mermaid にしても良いかも
