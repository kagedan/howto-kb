---
id: "2026-03-27-claude-code-claudemd-と-memorymd-の正しい使い方-01"
title: "Claude Code: CLAUDE.md と MEMORY.md の正しい使い方"
url: "https://zenn.dev/junko_ai/articles/311b69300fde6d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## はじめに

Claude Codeは普段使いでも十分便利ですが、設定ファイルの構造を理解して整備しておくと、さらに効率が上がります。

今回、公式ドキュメントを読み直しながら自分のCLAUDE.mdを見直しました。その過程で気づいたことをまとめます。

最初からすべての構造を把握して完璧にしようとすると大変ですよね。  
時間がない方は、まずはこれだけ押さえることをおすすめします！

* CLAUDE.mdとMEMORY.mdの役割の違い
* CLAUDE.mdに書くべきこと・書かないほうがいいことの把握

---

参考とした公式URL：<https://code.claude.com/docs/en/memory>

## Claude Codeの設定ファイル一覧

| ファイル | 誰が作る | 役割 | 必須 |
| --- | --- | --- | --- |
| CLAUDE.md | 自分 | ルールブック・永続指示 | ◎ |
| MEMORY.md | Claude自動 | 学習・記憶の蓄積 | 自動 |
| rules/\*.md | 自分 | CLAUDE.mdの補足・分割 | 任意 |
| agents/\*.md | 自分 | サブエージェント定義 | 任意 |
| skills/\*.md | 自分 | 複雑タスクの手順書 | 任意 |

この記事ではCLAUDE.mdとMEMORY.mdに絞ります。

---

## CLAUDE.md

ルールブック。プロジェクトのルール・前提をClaudeに伝えるために自分で書くファイル。  
Claude Codeに毎回読まれる＝長いと精度が落ちる。**200行以内**が推奨。

### 全部起動時に読み込む？

基本はYES。ただし**サブディレクトリのCLAUDE.mdは例外**で、そのディレクトリ配下のファイルを触ったときに初めて読み込まれる（遅延読み込み）。

`/init`で自動生成もできるが、イマイチな品質になることも。  
コードを見れば分かること（言語・フレームワーク名など）まで入る可能性があるので、**要チェック＆削って使う前提で**。

### 書かないほうがいいこと

* 見ればわかること（言語・フレームワーク名だけ書く等）
* 「間違えないで」など抽象的な指示
* 頻繁に変わる情報（進捗・チェックリスト）
* 相反する指示（矛盾があると任意に選択されてしまう）

人への指示と同じで、**具体的に書くほど効く**。

良い例：<https://github.com/anthropics/claude-code-action/blob/main/CLAUDE.md>

### 日本語より英語

トークン数は英語のほうが節約できる。  
ただし**自分がレビューしやすい言語で書くのが一番**。

### 全体用とプロジェクト用で分けられる

```
~/.claude/CLAUDE.md          # 全プロジェクト共通（作業スタイルなど）
your-project/CLAUDE.md       # プロジェクト専用
your-project/src/CLAUDE.md   # サブディレクトリ専用（遅延読み込み）
```

### 長くなったときはrulesを使う

指示が長くなったら`.claude/rules/`以下にファイルを分割。

```
your-project/
├── CLAUDE.md
└── .claude/
    └── rules/
        ├── code-style.md
        ├── testing.md
        └── security.md
```

あるいは、プロジェクト内やプロジェクト内のフォルダにCLAUDE.mdを作る形もOK

**pathsで特定ファイルにだけ適用できる**

```
---
paths:
  - "src/api/**/*.ts"
---
# API開発ルール
- すべてのエンドポイントにバリデーションを入れる
- エラーは標準フォーマットで返す
```

このrulesファイルは`src/api/`配下のTypeScriptファイルを触ったときだけ読み込まれる。全体に適用したくないルール（APIだけ・フロントだけ）に使う。

### 長くなったときは@でファイルを読み込める

CLAUDE.mdが長くなったら別ファイルに書いて参照できる。  
ただし、@で指定するとスッキリするものの、CLAUDE.mdと共に読み込むので、トークンは消費する。そのためパスの方が良いケースもある。

```
# CLAUDE.md

プロジェクト概要：ECサイト（Laravel + React）

@docs/architecture.md
@docs/api-conventions.md
```

### @とパス記載の使い分け

似ているようで用途が違う。

| 書き方 | 動作 | 向いている用途 |
| --- | --- | --- |
| `@ファイルパス` | 毎回強制的に読み込む | 常に参照が必要な内容 |
| パスをテキストで記載 | 必要なときにClaudeが自分で読みに行く | 特定の作業のときだけ参照したい内容 |

**例：毎回絶対使うときは@がよい**

毎回絶対に必要な内容（例：全作業共通のコーディング規約）にだけ使う。

**例：長いし毎回使う必要がないデザインルールはパスがよい**

```
## デザインルール
会社名義の資料を作るときは必ず参照する：
- `C:/Users/jun/.claude/brand/rule.md`
```

こう書いておくと、資料作成のタスクのときだけClaudeが読みに行く。毎回読み込む`@`と違い、トークンの無駄がない。

**プロジェクト外のファイル読み込みもできる**  
なお下記のように書くと、プロジェクト外のファイルも読み込める。

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

### コメントを入れるなら

HTMLコメントが使える。Claudeには見えないが、ファイルを管理する人間には見える。

```
<!-- 最終更新：2026-03 メンテナー：Junko -->
# プロジェクトルール

## Commands
<!-- bun→npmに変更する場合はここも更新 -->
npm run dev
```

## MEMORY.md

### MEMORY.mdとは

Claude Codeが**自動で作成・更新**するファイル。自分で書くものではない。

* 保存場所：`~/.claude/projects/<プロジェクト>/memory/`
* セッション開始時に**先頭200行または25KB**のどちらか早い方を読み込む

### 構造

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # インデックス（毎回読み込まれる）
├── debugging.md       # テーマ別の詳細メモ
├── api-conventions.md # テーマ別の詳細メモ
└── ...
```

MEMORY.mdは概要のみ。詳細はtopic filesに分けてClaudeが自動で管理する。  
topic filesはセッション開始時には読み込まれず、必要なときだけ参照される。

### セッションをまたぐ記憶について

会話履歴そのものは引き継がない。  
ただしClaudeが学習したことはMEMORY.mdに書き込まれるので、次のセッションでも覚えている。

過去の会話を呼び出すには：

```
claude --continue   # 直前の会話を継続
claude --resume     # 過去の会話一覧から選んで再開
```

### /memoryコマンド

`/memory`を実行すると3つのメニューが出る。

```
1. User memory          → ~/.claude/CLAUDE.md（グローバル）
2. Project memory       → ./CLAUDE.md（プロジェクト）
3. Open auto-memory folder → MEMORY.mdが入っているフォルダ
```

CLAUDE.mdの確認・編集は`/memory`から行うのが一番手軽。

### CLAUDE.mdとMEMORY.mdの使い分け

|  | CLAUDE.md | MEMORY.md |
| --- | --- | --- |
| 誰が書く | 自分 | Claudeが自動で |
| 内容 | ルール・前提 | 学習・記憶 |
| 読み込み | 全文・毎回 | 先頭200行まで・毎回 |

なお、追加指示はメMEMORY.mdにいれられてしまう傾向あり。  
CLAUDE.mdに指示を追加したいときは、場所を明確に伝えると確実：

```
CLAUDE.mdの「Commands」セクションに npm run lint を追加して
```

### さいごに

Claude Codeを効率よく安心に使う方法、引き続き探求していきます。  
YouTube動画でもCLAUDE.mdの書き方を解説しています。  
▶　<https://youtu.be/IFmG7dMD16E>
