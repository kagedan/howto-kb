---
id: "2026-06-20-windows-powershell-51-で-claude-code-を実運用して踏んだ落とし穴と-01"
title: "Windows + PowerShell 5.1 で Claude Code を実運用して踏んだ落とし穴と対策"
url: "https://zenn.dev/equaliainc/articles/claude-code-windows-powershell-tips"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

個人開発のサービスを Claude Code で書いていますが、開発機は Windows 11 + Windows PowerShell 5.1 です。Claude Code やこの手の AI エージェントは macOS / Linux + bash 前提のドキュメントが多く、Windows ＋ PowerShell 5.1（PowerShell 7 ではなく**OS 同梱の 5.1**）で常用すると、地味にハマる箇所がいくつもありました。この記事ではその落とし穴と、実際に効いた対策をまとめます。

## 前提

* OS: Windows 11
* シェル: Windows PowerShell 5.1（`pwsh` ではなく `powershell.exe`）
* Claude Code を日常の実装・運用フローに使用

PowerShell 7 に上げれば解決するものもありますが、「素の Windows でそのまま動かしたい」という事情で 5.1 を使い続けています。同じ環境の人の参考になればと思います。

## 1. `&&` / `||` でコマンド連結できない

bash 脳で `npm run build && git push` と書くと、PowerShell 5.1 では**パーサエラー**になります（パイプライン連結演算子は PowerShell 7 から）。

```
# NG（5.1 では構文エラー）
npm run build && git push

# OK: 直前の成功を $? で見て分岐
npm run build; if ($?) { git push }

# 失敗を無視して順に流すだけなら ;
git add .; git commit -m "wip"
```

エージェントに作業させるときも、この差は最初に明示しておくと無駄な失敗が減ります。

## 2. ネイティブ exe への `2>&1` が「誤った失敗」を生む

PowerShell 5.1 で `git` などネイティブ実行ファイルの標準エラーを `2>&1` でリダイレクトすると、stderr の各行が `NativeCommandError`（ErrorRecord）に包まれ、**終了コード 0（成功）でも `$?` が `$false` になる**ことがあります。git は進捗を stderr に出すので、これに何度も引っかかりました。

```
# 危険: 成功しても失敗扱いになりがち
git push 2>&1

# 基本は素直に実行する（stderr はそのまま表示される）
git push
```

「成功しているのにスクリプトが失敗判定する」ときは、まずこのパターンを疑うとよいです。

## 3. ファイルの文字コードが UTF-16 BOM になる

`Out-File` / `Set-Content` の既定エンコーディングは 5.1 だと \*\*UTF-16 LE（BOM 付き）\*\*です。他のツール（Node のスクリプト、Git、各種 CLI）が読む JSON や `.md` をこれで書くと、先頭の BOM や文字化けで読めなくなります。

```
# 他ツールが読むファイルは必ず utf8 を明示
"{ ""ok"": true }" | Out-File -Encoding utf8 config.json
```

状態管理用の JSON をスクリプトで書き換える運用をしているのですが、ここを `-Encoding utf8` で固定するまで、たまに JSON パースが壊れて原因究明に時間を溶かしました。

## 4. bash 由来のコマンド・記法はそのままでは動かない

`head` / `tail` / `which` / `touch` / `2>/dev/null` あたりは PowerShell には無い、もしくは意味が違います。よく使う対応表:

| やりたいこと | bash | PowerShell 5.1 |
| --- | --- | --- |
| 先頭 N 行 | `head -n 20` | `Get-Content f -TotalCount 20` |
| 末尾 N 行 | `tail -n 20` | `Get-Content f -Tail 20` |
| パス取得 | `which node` | `(Get-Command node).Source` |
| 空ファイル作成 | `touch f` | `New-Item -ItemType File f` |
| 出力破棄 | `2>/dev/null` | `2>$null` |
| 環境変数 | `FOO=x cmd` | `$env:FOO='x'; cmd` |

ヒアドキュメントの書き方も違います。`@'...'@` の閉じ `'@` は\*\*行頭（インデントなし）\*\*でないと構文エラーになります。

## 5. POSIX が必要なときだけ bash に逃がす

とはいえ全部を PowerShell でやろうとすると消耗します。`find` / `grep` を多用する処理や、bash 前提のワンライナーは、Windows でも使える bash（Git Bash 等）に明示的に逃がすのが現実的でした。

「標準は PowerShell、POSIX シェルが必要なときだけ bash」という方針をプロジェクトの指示ファイルに書いておくと、エージェントもそれに従ってくれて事故が減ります。

## まとめ

Windows + PowerShell 5.1 での Claude Code 運用は、

* `&&`/`||` は使えない → `; if ($?) { }`
* ネイティブ exe への `2>&1` は誤った失敗を生む → 素直に実行
* 他ツールが読むファイルは `-Encoding utf8` を明示
* bash 由来コマンドは対応表で読み替え、必要なときだけ bash に逃がす

この 4 点を**プロジェクトの指示ファイル（CLAUDE.md / AGENTS.md 等）に最初から書いておく**のが、結局いちばん効きました。エージェントは毎回それを読んでから動くので、同じハマりを繰り返さなくなります。

---

ちなみに、こうした「Claude Code やプロンプトの実運用ノウハウ」を売買できるマーケットを個人で作って運営しています 👉 [equaliA（イコリア）](https://equalia.jp)。同じように AI ツールを業務に組み込んでいる方は覗いてみてください。
