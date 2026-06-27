---
id: "2026-06-26-claude-codeのsettingsjson階層を理解するuserprojectlocalの優先-01"
title: "Claude Codeのsettings.json階層を理解する──user/project/localの優先順位と最小設定"
url: "https://zenn.dev/stockdev_sho/articles/f1d4d737bd90cc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

Claude Code を入れた初日、`settings.json` をどこに置けばいいのか迷いませんでしたか。`~/.claude/` なのか、プロジェクトの `.claude/` なのか。チームで共有したい設定と、自分だけの設定はどう分けるのか。

この記事では、その「どこに何を書くか」を\*\*設定ファイルの階層と優先順位（precedence）\*\*から整理します。実際の `settings.json` の中身・`.claude` ディレクトリ構成・つまずきやすい落とし穴を、コピペできる形で添えます。読み終えると「この設定はどのファイルに書くべきか」を自分で判断できるようになります。

!

**対象読者と前提**

* Claude Code をインストール済みで、これから設定を整えたいエンジニア
* JSON と Git の基本がわかる
* 出力例・設定値はすべて「想定例」です。最新の仕様・キー名は公式ドキュメント（[code.claude.com/docs](https://code.claude.com/docs/en/settings)）を確認してください

## 結論：設定は「4つのスコープ」に分かれ、上ほど強い

Claude Code の設定は、置き場所によってスコープ（適用範囲）が決まります。同じキーが複数のスコープにあるときは、**優先順位の高い方が勝ちます**（ただし `permissions` だけは“マージ”される。後述）。

| スコープ | 置き場所 | 用途 | Gitに入れる？ |
| --- | --- | --- | --- |
| Managed（組織管理） | システム配下の `managed-settings.json` 等 | 会社全体の強制ポリシー | 管理者管理 |
| Local（個人・プロジェクト内） | `.claude/settings.local.json` | このプロジェクトでの自分専用 | 入れない（gitignore） |
| Project（チーム共有） | `.claude/settings.json` | チームで共有する設定 | 入れる |
| User（個人・全体） | `~/.claude/settings.json` | 全プロジェクト共通の自分の好み | 入れない |

優先順位は **高い順に** こうなります。

```
Managed（最強・上書き不可）
  → コマンドライン引数（その場限り）
    → Local（.claude/settings.local.json）
      → Project（.claude/settings.json）
        → User（~/.claude/settings.json／最も弱い）
```

最初に押さえるべきは2点だけです。

1. **「全プロジェクト共通の自分の好み」は User（`~/.claude/settings.json`）**
2. **「チームで揃えたい設定」は Project（`.claude/settings.json`）でコミット**

この2つを分けるだけで、初日の混乱はほぼ消えます。

## `.claude` ディレクトリには何が入るのか

設定ファイルは単独ではなく、`.claude/` ディレクトリの一部です。User スコープ（ホーム）と Project スコープ（リポジトリ内）で、ほぼ同じ構成が並びます。

ディレクトリ構成（想定例）

```
~/.claude/                      # User スコープ（全プロジェクト共通）
├── settings.json               # 個人の設定
├── CLAUDE.md                   # 個人のメモリ（指示）
├── agents/                     # 自作サブエージェント
└── skills/                     # 自作スキル

<リポジトリ>/.claude/           # Project スコープ（このプロジェクト）
├── settings.json               # チーム共有設定（コミットする）
├── settings.local.json         # 自分専用の上書き（gitignore）
├── CLAUDE.md                   # プロジェクトのメモリ（コミットする）
├── commands/                   # 自作スラッシュコマンド
└── agents/                     # プロジェクト用サブエージェント
```

ポイントは、**同じ名前のファイルが「ホーム」と「プロジェクト」の両方にあり、役割が違う**こと。`settings.json` は片方にしか書けないものではなく、両方に置いて重ねるものです。

## 最小の `settings.json`：まず User に置く3つ

初日に User スコープへ置くなら、欲張らず3キーで十分です。

~/.claude/settings.json

```
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "0"
  }
}
```

書いたら、設定が読めているかを確認します。JSON の構文ミスは沈黙して効かないことがあるので、**設定したら必ず検証**します。

```
$ claude doctor   # 設定ファイルの検証・診断
```

```
（想定例：設定ファイルのパスと検出結果が一覧で表示される。
  JSONの構文エラーがあればここで指摘される）
```

`$schema` を1行入れておくと、対応エディタで補完とバリデーションが効きます。タイプミスでキーが無視される事故を減らせるので、最初に入れておくのがおすすめです。

## `permissions` だけは「上書き」ではなく「マージ」される

ここが最大のハマりどころです。冒頭で「上のスコープが勝つ」と書きましたが、**`permissions` は例外**で、各スコープのルールが\*\*合算（マージ）\*\*されます。

つまり User で許可し、Project でも許可すると、両方の許可が積み上がります。`deny` も同様に積み上がるので、**どこか1スコープで拒否すれば、その拒否は効いたまま**です。

.claude/settings.json（Project・チーム共有）

```
{
  "permissions": {
    "deny": [
      "Bash(curl *)",
      "Bash(git push *)"
    ]
  }
}
```

この Project 設定をコミットしておくと、メンバー全員の環境で `curl` と `git push` が拒否されます。各自の User 設定で `curl` を `allow` に書いても、**`deny` は別スコープでも生き残る**ため、うっかり外部送信する事故を組織側で止められます。

なぜ permissions だけマージなのか（補足）

`model` や `env` のような「単一の値」は、複数スコープにあれば1つに決めるしかありません（＝優先順位で上書き）。一方 `permissions` は「ルールの集合」なので、**全スコープのルールを足し合わせた方が安全**です。User の好みを尊重しつつ、組織や チームの `deny` を確実に効かせられる——この設計のために、permissions だけは振る舞いが違います。挙動の正確な仕様は公式docsで確認してください。

## CLAUDE.md も三層：指示を「どこに書くか」

設定値だけでなく、Claude への\*\*指示（メモリ）\*\*も階層を持ちます。これが `CLAUDE.md` です。

| スコープ | 置き場所 | 書く内容 |
| --- | --- | --- |
| User | `~/.claude/CLAUDE.md` | 全プロジェクト共通の自分の流儀 |
| Project | `CLAUDE.md` または `.claude/CLAUDE.md` | チーム共有のルール（コミット） |
| Local | `.claude/CLAUDE.local.md` | このプロジェクトの自分専用メモ（gitignore） |

たとえばチーム共有の `CLAUDE.md` には、こう書きます。

CLAUDE.md（Project・コミットする）

```
# このリポジトリの約束

- パッケージ管理は uv を使う（pip 直叩きはしない）
- テストは `pytest -q` で実行する
- コミットメッセージは日本語、命令形で書く
```

「毎回同じ説明を打っている」と感じたら、それは `CLAUDE.md` に移すサインです。チーム全員に効かせたいなら Project、自分だけなら User や Local に分けます。

## 落とし穴4つ

### 落とし穴1：`settings.local.json` をコミットしてしまう

`*.local.json` と `CLAUDE.local.md` は**個人用＝gitignore 前提**です。誤ってコミットすると、自分専用の許可や実験設定がチーム全体に漏れます。`.gitignore` に明示しておきましょう。

.gitignore

```
+ .claude/settings.local.json
+ .claude/CLAUDE.local.md
```

### 落とし穴2：「効くはず」が無言で効かない

JSON の閉じ忘れやキー名のタイプミスは、エラーで止まらず**黙って無視**されることがあります。`$schema` を入れる・`claude doctor` で検証する、の2点で大半は防げます。

### 落とし穴3：反映にリセッションが要る設定がある

`permissions` / `hooks` / `env` などは編集すると即反映されますが、`model` や `outputStyle` のように**セッション再起動が必要**なものもあります。「設定したのに変わらない」ときは、いったんセッションを開き直すか、モデルは `/model` で切り替えます。

### 落とし穴4：User と Project の役割を逆に書く

「全員に効かせたい」のに User に書く、「自分だけ」のものを Project にコミットする——この取り違えが一番多いミスです。判断はシンプルに、**「他の人の環境でも効いてほしい？」が Yes なら Project、No なら User か Local**。

## まとめ

* 設定は **Managed > コマンドライン > Local > Project > User** の順で強い
* 「全プロジェクト共通の自分の好み」は **User**、「チーム共有」は **Project にコミット**
* `permissions` だけは**マージ**。どこかで `deny` すれば効き続ける（事故防止に使う）
* `*.local.json` / `CLAUDE.local.md` は **gitignore**、秘匿値は直書きしない
* 迷ったら **`claude doctor`** と **`$schema`** で「黙って効かない」を防ぐ

---

役に立ったら ❤️ と Zenn のフォローで応援してもらえると、次の設定ネタを書く励みになります。
