---
id: "2026-07-14-windows版-claude-desktop-内蔵-claude-code-の本当のバージョン確認-01"
title: "Windows版 Claude Desktop 内蔵 Claude Code の本当のバージョン確認方法"
url: "https://qiita.com/fallout/items/58596893f9eef9d97820"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-07-14"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

Claude Code CLI は毎日のようにバージョンが上がりますが、**Claude Desktop アプリに内蔵されている Claude Code は、PATH に入っている単体 CLI とは別管理・別更新**です。

つまり `claude --version` で分かるのは単体 CLI の版であって、Desktop が実際に動かしているエンジンのバージョンとは限りません。

Desktop が動かしている Claude Code の「本当のバージョン」を調べる方法を、備忘録として残しておきます。

**検証環境**（2026-07-15 時点）

- Windows 11
- Claude Desktop 1.20186.9.0（**Microsoft Store / MSIX 版**）
- PowerShell 7.6.3

以下は MSIX 版 Desktop が前提です（`Get-AppxPackage` を使うため）。

---

## 方法1: アプリ起動中に調べる方法

プロセスの実行パスを見るだけです。パスに含まれるディレクトリ名がそのままバージョンになっています。

```powershell
Get-Process claude | Where-Object { $_.Path -like '*claude-code*' } | Select-Object -Expand Path -Unique
```

出力:

```
C:\Users\<user>\AppData\Roaming\Claude\claude-code\2.1.209\claude.exe
                                                   ~~~~~~~ ← これがエンジンのバージョン
```

`Where-Object` で絞っているのは、`claude` という名前のプロセスが複数走りうるためです。

---

## 方法2: アプリを起動してなくとも調べる方法（常に使える）

エンジンの実体はディスク上にあるので、そこへ直接 `--version` で聞くのが確実です。

```powershell
& (Get-ChildItem "$env:LOCALAPPDATA\Packages\$((Get-AppxPackage | Where-Object Name -eq 'Claude').PackageFamilyName)\LocalCache\Roaming\Claude\claude-code\*\claude.exe" | Sort-Object LastWriteTime | Select-Object -Last 1).FullName --version
```

出力:

```
2.1.209 (Claude Code)
```

exe を起動せず、ディレクトリ名を読むだけでも同じ答えが得られます。

```powershell
(Get-ChildItem "$env:LOCALAPPDATA\Packages\$((Get-AppxPackage | Where-Object Name -eq 'Claude').PackageFamilyName)\LocalCache\Roaming\Claude\claude-code" | Sort-Object LastWriteTime | Select-Object -Last 1).Name
```

---

## なぜこんなに長いパスなのか（ハマりどころ）

方法1の出力に出てくる `%APPDATA%\Claude\claude-code\...` を見て、素直にそこへ移動しようとすると失敗します。

```powershell
Test-Path $env:APPDATA\Claude
# False
```

**パス文字列は読めるのに、そのパスは存在しない。** これは MSIX（ストアパッケージ）アプリのファイルシステム仮想化によるものです。パッケージアプリはコンテナ（サイロ）の中で動き、その中から見た `%APPDATA%\Claude\...` は、実体としては次の場所にリダイレクトされています。

```
%LOCALAPPDATA%\Packages\Claude_<発行者ハッシュ>\LocalCache\Roaming\Claude\...
```

エクスプローラーや普段のターミナル（＝コンテナの外）からは `%APPDATA%` の下に `Claude` フォルダが**そもそも存在しません**ので、上記の物理パスを使う必要があります。方法2のコマンドが長いのはこのためです。

---

## ついでに: Desktop アプリ本体のバージョン

```powershell
Get-AppxPackage | Where-Object Name -eq 'Claude' | Select-Object Name, Version
```

---

## まとめ

| 調べたいもの | コマンド |
| --- | --- |
| Desktop 内蔵エンジン（＝Code タブが動かしている Claude Code） | 方法1 / 方法2 |
| PATH の単体 CLI | `claude --version` |
| Desktop アプリ本体 | `Get-AppxPackage` |
