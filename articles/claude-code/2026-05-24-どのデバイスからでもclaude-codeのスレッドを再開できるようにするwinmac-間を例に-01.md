---
id: "2026-05-24-どのデバイスからでもclaude-codeのスレッドを再開できるようにするwinmac-間を例に-01"
title: "どのデバイスからでもClaude Codeのスレッドを再開できるようにする（Win/Mac 間を例に)"
url: "https://zenn.dev/oqamura/articles/54d72bf9e7ca9d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

## やりたいこと

Claude Code は便利だが、MacとWindowsなど、デバイスが変わると同じスレッドから再開することはできない。これは困る。

よって、本記事ではClaude Code (CC) のセッションを、Windows と Mac のどちらからでも `--resume` (`/resume`) で再開できるようにする。

本記事は、Google Driveを使用しているが、その他のクラウドでも可能である。ただし、他のエンジニアの方々が口を揃えて仰る通り、OneDriveはいかなる環境下でもお勧めしない。

## 前提知識: CC のセッション保存先

CC はセッションデータ（JSONL + memory/）を以下に保存する。

```
~/.claude/projects/<encoded-cwd>/
```

`<encoded-cwd>` は cwd のパス区切りを `-` に置換した文字列。OS ごとに異なる。

```
Win: C--Users-username-My-Drive-[YOUR_Dir]
Mac: -Users-username-Library-CloudStorage-GoogleDrive-email-My-Drive-[YOUR_Dir]
```

`~/.claude/` はホームディレクトリ直下にあり、Google Drive の同期対象外。つまり Win で作ったセッションは Mac から見えないし、逆も同様。

## 失敗した方法: Drive 内にジャンクションを張る

最初に試したのは、Google Drive 内（`My Drive/[YOUR_Dir]/`）に NTFS ジャンクションを作り、`~/.claude/projects/<encoded-cwd>` を参照させる方法。

```
My Drive/.cc_projects  ──junction──→  ~/.claude/projects/<encoded-cwd>
```

OS レベルではジャンクション先のファイルが見える。しかし Google Drive Desktop はジャンクションポイントを `type=kOther` として扱い、`CreateFileW` で `PERMISSION_DENIED` を返して同期を拒否する。

Drive Desktop のログ:

```
GetLocalItem Checksumming ..\.cc_projects failed with
PERMISSION_DENIED: CreateFileW failed during OpenHandleForPath
```

10 秒ごとにリトライした末に `GENERIC_UPLOAD_FAILURE` で放棄。ジャンクション先の中身は走査しない。

結論: **Drive Desktop (Mirror) は NTFS ジャンクションをフォローしない。**

## 成功した方法: ジャンクションの向きを逆にする

発想を逆転させる。

* 実体を Drive 内に置く（通常ディレクトリ → Drive が普通に同期）
* `~/.claude/projects/<encoded-cwd>` からジャンクション / シンボリックリンクで参照（Drive は関知しない）

```
【実体】My Drive/[YOUR_Dir]/.cc_projects/
    ├── *.jsonl
    ├── memory/
    └── <uuid>/

【Win】~\.claude\projects\<win-encoded-cwd>\  ──junction──→  実体
【Mac】~/.claude/projects/<mac-encoded-cwd>/  ──symlink───→  実体
```

Drive が触るのは `My Drive` 内の通常ディレクトリだけ。ジャンクションは `~/.claude/` 内にあり Drive の管理外。CC は OS レベルのリンク解決で透過的に読み書きする。

## セットアップ

### 1. encoded-cwd を確認

Win:

```
ls "$env:USERPROFILE\.claude\projects\"
```

Mac（CC を一度起動して生成させる）:

```
cd ~/My\ Drive/[YOUR_Dir] && claude
# 何か送信して /exit
ls ~/.claude/projects/
```

Mac の CC は `~/My Drive`（シンボリックリンク）を実パスに解決してから encode するため、名前が長くなる。`@` `.` は `-` に置換される。

### 2. Win 側（先に実行）

CC をすべて終了してから:

```
$src = "$env:USERPROFILE\.claude\projects\<win-encoded-cwd>"
$dst = "$env:USERPROFILE\My Drive\[YOUR_Dir]\.cc_projects"

robocopy $src $dst /MIR /R:1 /W:1      # 実体を Drive 内にコピー
Rename-Item $src "${src}.bak"            # 元を退避
cmd /c mklink /J "$src" "$dst"           # ジャンクション作成
```

確認:

```
Get-Item $src | Select-Object LinkType   # → Junction
```

CC を起動して `/resume` でセッション一覧が見えれば成功。Drive Web で `.cc_projects` が表示されることも確認する。

### 3. Mac 側（Drive Web に .cc\_projects が表示されてから）

CC をすべて終了してから:

```
mac_dir="$HOME/.claude/projects/<mac-encoded-cwd>"

cp "${mac_dir}"/*.jsonl "$HOME/My Drive/[YOUR_Dir]/.cc_projects/" 2>/dev/null
mv "$mac_dir" "${mac_dir}.bak"
ln -s "$HOME/My Drive/[YOUR_Dir]/.cc_projects" "$mac_dir"
```

確認:

```
ls -la "$mac_dir"   # → ... -> .cc_projects
```

CC を起動して `/resume` で Win のセッションが見えれば成功。初回は Stream モードのダウンロードで数十秒かかる。

### 4. クリーンアップ

動作確認後、`.bak` を削除。

## 復旧

問題があればジャンクション / シンボリックリンクを消して `.bak` を戻すだけ。

Win:

```
cmd /c rmdir "$src"               # ジャンクション削除（実体は残る）
Rename-Item "${src}.bak" $src     # 退避を復元
```

Mac:

```
rm "$mac_dir"
mv "${mac_dir}.bak" "$mac_dir"
```

## 注意点

**同時アクセス禁止** — 両 OS で同じセッションを同時に `--resume` しない。JSONL の書き込みが競合すると Drive が競合コピーを生成してセッションが壊れる。

**同期待ち** — OS を切り替えた直後は Drive の同期完了を待つ。大きい JSONL は同期に数分かかる。

**CC アップデート時** — CC のバージョンアップで `~/.claude/projects/<encoded-cwd>/` が再作成され、ジャンクション / シンボリックリンクが通常ディレクトリに置き換わることがある。アップデート後にリンクが生きているか確認する。

**cwd を間違えると見えない** — CC は cwd ごとにセッションを管理する。`/resume` で "No conversations found" が出たら、起動ディレクトリが正しいか確認する。

## まとめ

* CC のセッション保存先（`~/.claude/projects/`）は Drive 管理外
* Drive 内にジャンクションを張っても Drive は reparse point を同期しない
* 逆方向（実体を Drive 内、`~/.claude/` からリンク）なら動く
* Win はジャンクション、Mac はシンボリックリンクで参照
* 実測値を含めてセットアップは 10 分程度で完了する
