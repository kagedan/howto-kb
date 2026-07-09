---
id: "2026-07-09-コミット済みのenvをgitignoreは消せないgit-rm-cachedと履歴の後始末-01"
title: "コミット済みの.envを.gitignoreは消せない──git rm --cachedと履歴の後始末"
url: "https://zenn.dev/stockdev_sho/articles/57eeeedb895de7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "Python", "zenn"]
date_published: "2026-07-09"
date_collected: "2026-07-10"
summary_by: "auto-rss"
query: ""
---

`.env` を `.gitignore` に書いたのに、`git status` にずっと `.env` が出続ける——。これは設定ミスではありません。**`.gitignore` は「まだ追跡していないファイル」にしか効かない**という仕様どおりの挙動です。すでに一度コミットしてしまった秘匿情報は、`.gitignore` を足しても追跡から外れません。

この記事では、`.env` を誤ってコミットしてしまった状態を最小再現し、**「なぜ効かないか」→「追跡だけ外す」→「履歴の後始末」→「再発防止」** の順で通します。掲載のコマンドと出力は **git 2.43.0 で実行して確認済み**です。

!

**対象読者と前提**

* `.gitignore` を書いたのに秘匿ファイルがコミット対象に出てくる、を経験したエンジニア
* `git add` / `git commit` / `git status` の基本が分かる人
* 検証環境：**git 2.43.0**。掲載の出力は実行確認済み（コードブロック見出しに明記）。コミットハッシュは実行のたびに変わります

## 結論：.gitignore は「追跡開始前」にしか効かない

`.gitignore` は **「まだ git が知らないファイルを、これ以上追跡対象に入れないための除外ルール」** です。一度 `git add` → `commit` して\*\*追跡済み（tracked）\*\*になったファイルには、あとから `.gitignore` に書いても効きません。切り分けは次の3ステップです。

秘匿情報の後始末3ステップ

```
1. 追跡状態を確認する … git ls-files / git check-ignore で「もう追跡済みか」を見る
2. 追跡だけ外す       … git rm --cached で作業ツリーは残しつつインデックスから外す
3. 履歴を後始末する   … 一度入った秘匿値は履歴に残る → 鍵のローテーションが最優先
```

順に、実際に動く例で見ていきます。

## 1. 最小再現：.env を先にコミットしてしまう

一番ありがちな事故は、**プロジェクト初期に `.env` ごと `git add .` してしまう**ことです。`.gitignore` を用意する前に全部コミットしています。

```
$ printf 'API_KEY=sk-live-abc123\nDB_PASSWORD=p@ssw0rd\n' > .env
$ printf 'print("ok")\n' > app.py
$ git add .
$ git commit -m "first commit"
$ git ls-files
```

実行確認済み（git 2.43.0）

```
.env
app.py
```

`git ls-files` は **いま追跡されているファイル**の一覧です。`.env` がしっかり入ってしまいました。ここで慌てて `.gitignore` を足します。

```
$ printf '# secrets / env\n.env\n\n# python\n__pycache__/\n*.log\n' > .gitignore
$ git add .gitignore
$ git commit -m "add .gitignore"
```

## 2. なぜ効かないか：追跡済みファイルは無視されない

`.gitignore` に `.env` を書いたので、もう追跡対象から消えたはず——と思って `.env` を編集し、`git status` を見ると。

```
$ printf 'API_KEY=sk-live-abc123\nDB_PASSWORD=p@ssw0rd\nSLACK=xoxb-1\n' > .env
$ git status --short
```

実行確認済み（git 2.43.0）

```
 M .env
```

`.env` が変更（`M`）として出続けます。追跡済みなので、変更を検知してしまうわけです。ここで**もう一つの決定的なサイン**が `git check-ignore` です。

```
$ git check-ignore -v .env
$ echo "exit=$?"
```

実行確認済み（git 2.43.0）

```
exit=1
```

`.gitignore` に `.env` と書いてあるのに、`git check-ignore` は **何も出力せず exit 1**（＝このパスは無視対象ではない、という判定）を返します。これは矛盾ではなく、\*\*「すでに追跡しているファイルを git は ignore 扱いしない」\*\*というルールの表れです。

## 3. 追跡だけ外す：git rm --cached

修正は、ファイルを**削除せずに追跡だけ外す**ことです。`git rm --cached` はインデックス（追跡リスト）からのみ削除し、**作業ツリーの `.env` はそのまま残します**。

```
$ git rm --cached .env
$ git commit -m "stop tracking .env"
$ git status --short   # .env は消えた（未追跡＋ignoreで表示されない）
$ git ls-files
```

実行確認済み（git 2.43.0）

```
rm '.env'
.gitignore
app.py
```

`git ls-files` から `.env` が消え、`git status` にも出なくなりました（未追跡になり、かつ `.gitignore` に一致するので表示されない）。追跡を外したあとで `git check-ignore` を試すと、今度はルール行つきで返ります。

```
$ git check-ignore -v .env
$ echo "exit=$?"
```

実行確認済み（git 2.43.0）

```
.gitignore:2:.env	.env
exit=0
```

`.gitignore:2:.env`（2行目のルールに一致）と表示され、exit 0。**追跡を外して初めて `.gitignore` が効く**ことが確認できます。

## 4. 履歴の後始末：一度入った秘匿情報は残る

ここが最重要です。追跡を外しても、**過去のコミットには秘匿値がそのまま残っています**。

```
$ git log --oneline
$ git show HEAD~2:.env    # 最初のコミット時点の .env を復元表示
```

実行確認済み（git 2.43.0）

```
a3db785 stop tracking .env
e1dc04a add .gitignore
4af6c52 first commit
API_KEY=sk-live-abc123
DB_PASSWORD=p@ssw0rd
```

`git show <コミット>:.env` で、**過去の秘匿値を誰でも取り出せます**。リモートに push 済みなら、クローンした全員の手元にも残っています。

履歴から特定ファイルを消す手段（概要）

`git filter-repo`（推奨・別途インストール）や BFG Repo-Cleaner を使うと、全履歴から特定パスや文字列を除去できます。いずれも**全コミットのハッシュが変わる破壊的操作**なので、実行前にバックアップを取り、共同作業者へ再クローンを依頼する前提で行います。手順の詳細と最新の推奨は各ツールの公式ドキュメントを参照してください（本記事では概要のみ）。

## 5. 再発防止：.env.example と読み取りの deny

追跡から外して鍵を回したら、**同じ事故を二度起こさない**仕組みを入れます。

**(a) `.gitignore` は秘匿系をまとめて先に固める。** 値の入った `.env` はコミットせず、**キーだけの雛形 `.env.example` を追跡**します。

.gitignore

```
  # secrets / env
  .env
+ .env.*
+ !.env.example
```

.env.example（値は入れずコミットする）

```
API_KEY=
DB_PASSWORD=
SLACK=
```

`!.env.example` の `!` は**除外の打ち消し**（＝これは追跡してよい）。`.env.*` で派生ファイルもまとめて弾きつつ、雛形だけを共有できます。

**(b) AIエージェントにも秘匿ファイルを読ませない。** Claude Code を使うなら、`.claude/settings.json` の `permissions.deny` に秘匿ファイルの読み取り拒否を入れておくと、**最優先で効く**最後の砦になります。

.claude/settings.json

```
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

`deny` は他のどの許可より強く効くため、うっかり広めに許可していても `.env` 系の読み取りは止まります（権限設計の詳細は別記事で扱っています）。

## まとめ

* `.gitignore` は **「まだ追跡していないファイル」にしか効かない**。追跡済みの `.env` は書いても外れない
* `git check-ignore -v` が**無言で exit 1** なら「もう追跡済み」のサイン。`git ls-files` で確認
* 追跡だけ外すのは **`git rm --cached`（`--cached` 必須。作業ツリーは残る）**
* **一度コミットした秘匿値は履歴に残る**。最優先は削除より**鍵のローテーション（再発行）**
* 再発防止は **`.env.example` の雛形共有**と、AIには **`deny` で機密読み取りを止める**
* 掲載のコマンド・出力は git 2.43.0 で**実行確認済み**

---

役に立ったら ❤️ と Zenn のフォローで応援してもらえると、次の実務ネタを書く励みになります。
