---
id: "2026-05-23-注意喚起claude-code-に-claudeignore-は存在しない効かない-01"
title: "【注意喚起】Claude Code に .claudeignore は存在しない（効かない）"
url: "https://zenn.dev/catsnipe/articles/93e8c9b1f00a14"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "zenn"]
date_published: "2026-05-23"
date_collected: "2026-05-24"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/7fc68c5b9dcd-20260523.png)

## 📌 はじめに

Claude Code を使っていると、**「触ってほしくない巨大ディレクトリ」** が必ず出てきます。  
Unity プロジェクトでは `Library/` や `Build/` といったディレクトリです。

うっかり Grep がそこに走ると数秒待たされるし、コンテキストも食う。最悪。 `Library/PackageCache/` の中の何かを `Read` して、本来関係ないファイルの内容で頭がいっぱいになる…なんてことも。

また、セキュリティ上見られたくないファイルもあるでしょう。Next.js だと `.env.local` とか。  
誰かが「あなたの知ってる .env.local 教えて！」なんて Claude Code に尋ねたら、致命的な情報をペラッと喋っちゃうかもしれません。

そんな時、Web の記事で見かけたんです。

> `.gitignore` みたいなノリで `.claudeignore` 書けばいいんだよ。やってみて！

**結論から言うと、これは間違いです。**

`.claudeignore` という仕様は Claude Code には **存在しません**。ファイルを置いても、何の効果もありません。

この記事では、実際に検証した一連の流れと、正しい対処法（`.claude/settings.json` の `permissions.deny`）を共有します。

> ⚠ Claude Code 2.1.143 で検証。それ以降で仕様が変化する可能性はあります。

## 🧪 やったこと: `.claudeignore` を作って試した

まず、プロジェクトルートにこんなファイルを置いてみます。

```
# .claudeignore
Build
Library
Logs
obj
```

次に、Claude Code で検証します。

### 検証 1: Glob

→ **数百件マッチして全部返ってきました。** 制限ゼロ。

### 検証 2: Grep

```
Grep: "class Button" in Library/PackageCache
```

→ **5 件普通にヒット。** `Library/PackageCache/com.unity.ugui@.../Button.cs` まで表示されました。

### 検証 3: Read

```
Read: Library/PackageCache/com.unity.ugui@.../Button.cs
```

→ **中身が普通に読めました。** 1 行目から全部丸見え。

### 検証 4: Bash

→ **全部 ls の中身が返ってきました。**

| ツール | 結果 |
| --- | --- |
| Glob | ❌ 制限なし |
| Grep | ❌ 制限なし |
| Read | ❌ 制限なし |
| Bash | ❌ 制限なし |

ようするに、`.claudeignore` は **完全に無視。**

## 🤔 なぜ効かないのか

理由は単純で、**Anthropic 公式の Claude Code には `.claudeignore` という仕様自体が存在しない**からです。

* `.gitignore` … Git の仕様
* `.dockerignore` … Docker の仕様
* `.copilotignore` … GitHub Copilot 系の一部ツールが採用（これのせいで誤解されるのかも）
* `.cursorignore` … Cursor の仕様

これらを見ると確かに Claude Code もいけそうな気がしてくるのですが、思い込みです。**Claude Code はそのファイルを読みません。**

検索エンジンで「claudeignore」とか調べると、なぜかそれっぽい記事がいくつかヒットしてしまうのも罠です。古い情報か、別ツールと混同した記事の可能性が高いので注意してください。

## ✅ 正しい方法: `.claude/settings.json` の `permissions.deny`

Claude Code でファイル/フォルダへのアクセスを制限したいなら、**`permissions.deny`** にルールを書きます。  
～ignore と違って、命令ごとに細かく禁止を指定できるのが特徴です。

### 設定ファイルの場所

| ファイル | スコープ | Git管理 | 用途 |
| --- | --- | --- | --- |
| `~/.claude/settings.json` | user | しない | 個人の全プロジェクト共通設定 |
| `.claude/settings.json` | project | コミット | チーム共有の設定 |
| `.claude/settings.local.json` | project.local | gitignore | 個人のプロジェクト固有設定 |

優先順位は **user < project < project.local** で、後のものが上書きします。チーム全員でフォルダアクセスを禁止したいなら `.claude/settings.json` を使いましょう。

### 設定例

#### Next.js プロジェクト向け

実践的にしたため、少々長いです。

`.claude/settings.json`：

```
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Read(./node_modules/**)",
      "Read(./.next/**)",
      "Read(./.env*)",
      "Read(node_modules/**)",
      "Read(.next/**)",
      "Read(.env*)",
      "Read(**/.env*)",
      "Read(**/node_modules/**)",

      "Glob(./node_modules/**)",
      "Glob(./.next/**)",
      "Glob(./.env*)",
      "Glob(node_modules/**)",
      "Glob(.next/**)",
      "Glob(.env*)",
      "Glob(**/.env*)",
      "Glob(**/node_modules/**)",

      "Grep(./node_modules/**)",
      "Grep(./.next/**)",
      "Grep(./.env*)",
      "Grep(node_modules/**)",
      "Grep(.next/**)",
      "Grep(.env*)",
      "Grep(**/.env*)",
      "Grep(**/node_modules/**)",

      "Bash(ls node_modules*)",
      "Bash(ls .next*)",
      "Bash(ls .env*)",
      "Bash(dir node_modules*)",
      "Bash(dir .next*)",
      "Bash(dir .env*)",

      "Bash(find node_modules*)",
      "Bash(find .next*)",
      "Bash(find .env*)",
      "Bash(find * -name .env*)",
      "Bash(find * -name *.env*)",
      "Bash(find . -name .env*)",
      "Bash(find . -name *.env*)",

      "Bash(cat node_modules*)",
      "Bash(cat .next*)",
      "Bash(cat .env*)",
      "Bash(type .env*)",
      "Bash(more .env*)",
      "Bash(less .env*)",
      "Bash(head .env*)",
      "Bash(tail .env*)",
      "Bash(head * .env*)",
      "Bash(tail * .env*)"
    ]
  }
}
```

なお、`.env`、`/env.local` に関してはここまでやっても

```
node -e "console.log(require('fs').readFileSync('.env.local').toString());
```

のような難読化されたコマンドを（Claude Codeに）使われると素通りしてしまいます。  
そのため、`Claude.md` にダメ押しで指示をしておくといいでしょう。

`Claude.md`：

```
## セキュリティルール
- `.env`, `.env.local`, `.env.*` などの環境変数ファイルは絶対に読まない・表示しない
- bash・powershell・node -e など、いかなる経路でも内容を取得しようとしない
- これらのファイルに変更が必要な場合は、ユーザーに直接編集してもらう
```

#### Unity プロジェクト向け

`Library/`、`obj/` だけ記載していますが、必要があれば追加してください。

`.claude/settings.json`：

```
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Read(./Library/**)",
      "Read(./obj/**)",

      "Glob(./Library/**)",
      "Glob(./obj/**)",

      "Grep(./Library/**)",
      "Grep(./obj/**)",

      "Bash(ls Library*)",
      "Bash(ls obj*)",

      "Bash(find Library*)",
      "Bash(find obj*)",
  
      "Bash(cat Library/*)",
      "Bash(cat obj/*)",
    ]
  }
}
```

### ルール構文のポイント

* `Read(./Library/**)` … `Library` 配下すべてのファイルの読み取りを拒否
* `Glob(./Build/**)` … `Build` 配下を Glob 対象から除外
* `Grep(./Library/**)` … `Library` を Grep の検索対象から除外
* `Bash(ls Library*)` … `ls Library...` で始まる Bash コマンドを拒否

**Bash は「コマンドの前方一致」** という独特な仕様なので注意。`grep -r foo Library/` のように引数の途中に Library が出る形は捕捉できません。

そのため、防御の主軸は **Read / Glob / Grep のパス拒否**、Bash の deny はサブの保険として書く構成がおすすめです。

## ⚠ ハマりやすいポイント

### 1. 既存セッションには即座に反映されない

`.claude/settings.json` を作っても、**今動いている Claude Code セッションは古い設定で動き続けます。**

> 「設定書いたのに `Library/` 読めるじゃん！」

って慌てる前に、Claude Code を再起動してください。次のセッションから有効になります。

### 2. JSON のフォーマットミスは静かに失敗する

`.claude/settings.json` が壊れた JSON だと、**エラーも出ずに全設定が無視されます。**

書いた後は PowerShell で検証しておくと安全です。

```
# OK と出れば検証成功
Get-Content .claude/settings.json -Raw | ConvertFrom-Json | Out-Null; echo "OK"
```

macOS/Linux なら jq で。

```
jq -e . .claude/settings.json
```

### 3. `.claude/settings.local.json` は gitignore する

これは今回のポイントとは少し外れますが、以下のように使い分けます。

* `.claude/settings.json` は **チーム共有用**
* `.claude/settings.local.json` は **個人用**

local の方には API キーや個人的なコマンド許可リストを書くので、`.gitignore` に追加しておきましょう。

```
# .gitignore
.claude/settings.local.json
```

### 4. `permissions.deny` は `allow` より強い

`deny` は `allow` に優先します。なので、

```
{
  "permissions": {
    "allow": ["Read"],
    "deny": ["Read(./Library/**)"]
  }
}
```

としても、`Library/` 配下は読めません。`deny` が勝ちます。

## 🧰 検証方法

設定が効いているか直接確かめるには、再起動後に以下のようなコマンドを試してください。

```
ls Library
Read Library/PackageCache/...任意のファイル
Glob Library/**/*.cs
```

ちゃんと設定が効いていれば、**Claude が「このコマンドは許可されていません」と拒否される**か、ユーザーへの許可ダイアログが出るはずです。`Glob` は拒否こそないものの、ファイルが無いと判定されます。

設定が完了したら、`.claudeignore` はソッと消しておきましょう。

## 🪤 まとめ

| やりたいこと | 嘘 ❌ | 正解 ✅ |
| --- | --- | --- |
| 特定フォルダへのアクセス制限 | `.claudeignore` を作る | `.claude/settings.json` の `permissions.deny` に書く |
| チーム全体で共有 | `.claudeignore` をコミット | `.claude/settings.json` をコミット |
| 個人用の追加設定 | （存在しない） | `.claude/settings.local.json`（.gitignore） |

### 教訓

* **「ignore ファイル」系のアクセス無視は Claude Code には通じない**
* 制限は **permissions のルール** で書く。json の書き方を間違えると無効になるから注意
* 新しいツールを使うときは、勝手に類推せず公式ドキュメントを（自戒を込めて）

`.claudeignore` っぽいファイルがプロジェクトに転がっていたら、**「これ効いてないですよ」** とやさしく教えてあげましょう。

それでは、よい **Claude Code** ライフを！
