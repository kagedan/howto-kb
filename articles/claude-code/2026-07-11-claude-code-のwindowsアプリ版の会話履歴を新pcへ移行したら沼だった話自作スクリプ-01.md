---
id: "2026-07-11-claude-code-のwindowsアプリ版の会話履歴を新pcへ移行したら沼だった話自作スクリプ-01"
title: "Claude Code の【Windowsアプリ版】の会話履歴を新PCへ移行したら沼だった話（自作スクリプトで抜け出すまで）"
url: "https://qiita.com/kanameShiga/items/9af4d5144dc79fcada54"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-07-11"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

:::note warn
この記事は **Claude Code の Windows デスクトップアプリ版**（`Claude` アプリ）の話です。
ターミナルの CLI 版ではありません。**ここが今回の沼の核心**でした。アプリ版は CLI とは
別の索引で履歴を管理していて、CLI 用のファイルをいくら運んでもアプリの「最近の項目」には
出てこないのです。
:::

## TL;DR

- **メインで使っているのは Windows デスクトップアプリ版**（ターミナルの CLI ではない）。ここが重要。
- プロジェクトのフォルダをコピーしても、**会話履歴は引き継がれない**。履歴は「作業フォルダの絶対パス」に紐づいて保存されるから。
- しかも履歴には**2つの層**がある。裏側の実体 `~/.claude/projects/*.jsonl` と、**アプリが実際に一覧表示に使う別の索引**。後者を作り直さないとアプリには出ない。
- 途中で **PowerShell 5.1 特有の罠**を2つ踏んだ（BOMなしUTF-8、ネイティブコマンドの stderr）。
- `CLAUDE_CONFIG_DIR` は根本策**ではない**。
- 最終的に移行スクリプトを自作して公開した → [KanameShiga-dev/claude-code-migrate](https://github.com/KanameShiga-dev/claude-code-migrate)
- **これは全部、公式にサポートされた手順ではない。自己責任です。**

:::note warn
この記事で触る `~/.claude/projects/*.jsonl` やデスクトップアプリの索引ファイルは、Claude Code の内部形式です。[公式ドキュメントにも「バージョンごとに変わり得る」と明記](https://code.claude.com/docs/en/sessions)されており、直接いじるのはサポート外です。真似する場合は自己責任で、必ずバックアップを取ってください。
:::

---

## きっかけ

個人開発のアプリを新しいPCに移すことになった。プロジェクトは Git 管理していたし、「フォルダごとコピーすれば動く」ようには作ってあった。実際、コピーして環境チェックを走らせたら必須項目は全部OKで、アプリはあっさり起動した。**ここまでは10分**だった。

問題はそのあと。「これまでの Claude Code の会話履歴も引き継ぎたい」と思った瞬間から、沼が始まった。

なお、この移行作業自体を Claude Code（に指示する形）で進めた。**Claude Code を使って Claude Code の履歴を移行する**という構図で、AI 側も途中で何度か読み違えている。そのやり取りも含めて、知見として残す。

## 環境

- Windows 11
- Windows PowerShell 5.1（← これが後で効いてくる）
- **Claude Code：Windows デスクトップアプリ版がメイン**（CLI も入ってはいるが、普段は使っていない）

ここが今回の話の前提として一番大事。「アプリ版で会話してきた履歴を、新PCのアプリ版にも
出したい」——ゴールはこれ。ところが世の中の移行情報の多くは CLI 前提で書かれていて、
**アプリ版特有の事情でことごとくハマった**。

---

## 前提：履歴はどこに保存されるのか

Claude Code の会話履歴は、ローカルのここに保存される。

```
~/.claude/projects/<作業パスの非英数字をハイフンに置換した名前>/<session-id>.jsonl
```

たとえば作業ディレクトリが `C:\work\proj` なら、フォルダ名は `C--work-proj` になる。**この「フォルダ名が作業パスから作られる」のが、移行のすべての元凶**だった。

```powershell
# 作業パスから履歴フォルダ名（slug）を作るルール
$slug = $ProjectRoot -replace '[^A-Za-z0-9]', '-'
# C:\work\proj  →  C--work-proj
```

## 沼1：フォルダをコピーしても履歴が一覧に出てこない

新PCではプロジェクトの置き場所を変えていた。すると slug が変わり、旧PCの履歴は「別プロジェクトの履歴」として切り離され、一覧に出てこない。

`~/.claude/projects/<旧slug>/` を新PCにコピーすれば……と思ったが、それだけでは**まだ出ない**。各セッションは、会話開始時の作業ディレクトリ（`cwd`）で絞り込まれるからだ。jsonl の中身にこう埋まっている。

```json
{"type":"user","cwd":"C:\\old\\path","message":{ ... }}
```

この `cwd` が新しいパスと一致しないと、履歴一覧に現れない。しかも罠がもう一段あって、**旧PCの `cwd` はプロジェクト直下とは限らなかった**。親フォルダで Claude Code を起動していると、`cwd` は親パスになる。

ヒントは履歴フォルダ名そのものにあった。フォルダ名が `C--old`（親）なのに、プロジェクトは `C:\old\proj`。「slug に proj が入っていない＝親フォルダで起動していた」と読める。AI 側は最初これを `C:\old\proj` だと決めつけて外していた。

修正は「`cwd` フィールドだけ」を書き換える。会話本文中に出てくるパス文字列は**記録として残す**ために触らない。

```powershell
# jsonl は JSON なのでバックスラッシュはエスケープ済み（C:\\old）。
# 長いパスから先に置換しないと、短いほうが前方一致で食ってしまう。
$text = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
$newEsc = $ProjectRoot.Replace('\', '\\')
foreach ($old in ($OldPath | Sort-Object Length -Descending)) {
    $oldEsc = $old.Replace('\', '\\')
    # Replace は大文字小文字を区別する（C:\old と C:\Old は別物）。
    $text = $text.Replace('"cwd":"' + $oldEsc, '"cwd":"' + $newEsc)
}
```

これで **CLI からは** `claude --resume` で旧セッションが開けるようになった。……が、繰り返すと
自分が使いたいのは**アプリ版**。ここからが本当の沼だった。

## 沼2（本丸）：cwd を直したのに、Windows アプリには出ない

試しに CLI（`claude --resume`）で見ると、履歴は出る。**でも普段使っている Windows デスクトップ
アプリの「最近の項目」には、まだ出ない。** 自分が使いたいのはアプリ版なので、これでは意味がない。
ここが今回一番はまった、本丸だった。

答えは[公式ドキュメントの冒頭](https://code.claude.com/docs/en/sessions)に書いてあった。

> The desktop app, Claude Code on the web, and the VS Code extension each maintain their own session history.

**デスクトップアプリ・Web版・VS Code拡張は、それぞれ独自のセッション履歴を持つ。** つまり CLI 用の jsonl を運んでも、アプリの一覧には反映されない。アプリは別の索引ファイルを見ている。

```
%APPDATA%\Claude\claude-code-sessions\<accountUuid>\<organizationUuid>\local_<uuid>.json
```

中身は、CLI の jsonl を指すポインタになっている。

```json
{"sessionId":"local_xxxx","cliSessionId":"<jsonlのファイル名>","cwd":"C:\\new\\path",
 "title":"セッションのタイトル","createdAt":1700000000000,"model":"claude-...", ...}
```

やっかいなことに、**旧PCと新PCでアプリのバージョンが違うと、この保存方式自体が変わっている**ことがある。今回の旧PCはこの `local_*.json` 方式ですらなく、古い形式（アプリが jsonl を直接読む方式）だった。だから旧PCの索引を運んでも新アプリは読めない。**「運ぶ」のではなく「作り直す」**しかなかった。

## 沼3：PowerShell 5.1 の罠が2つ

日本語コメント入りのスクリプトを書いていたら、2回ハマった。

### (1) BOMなしUTF-8を ANSI として読む

Windows PowerShell 5.1 は、BOMのないUTF-8ファイルを ANSI（cp932）として解釈する。日本語コメント入りの `.ps1` が、実行時に構文エラーで起動すらしない。

対策は単純で、**UTF-8 BOM付きで保存する**こと。

```powershell
$bom = New-Object System.Text.UTF8Encoding $true   # $true = BOM付き
[System.IO.File]::WriteAllText($path, $text, $bom)
```

### (2) ネイティブコマンドの stderr がエラーに化ける

`git bundle verify` は、**成功時でも** `... is okay` を stderr に書く。これを `2>&1` でリダイレクトすると、PowerShell 5.1 は各行を ErrorRecord に変換する。`$ErrorActionPreference = 'Stop'` を設定していると、**成功したのに例外で止まる**。

```powershell
# NG: 成功しても例外で止まる
git bundle verify $bundle 2>&1 | Out-Null

# OK: ネイティブ呼び出しの間だけ Continue に落とし、終了コードで判定する
$saved = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    git bundle verify $bundle | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "検証失敗" }
} finally { $ErrorActionPreference = $saved }
```

## 沼4：「CLAUDE_CONFIG_DIR で解決」は誤解だった

途中で「`CLAUDE_CONFIG_DIR` を設定すれば、そもそもパス依存が消えるのでは？」という話になった。**これは誤りだった。**

`CLAUDE_CONFIG_DIR` が変えるのは保存先の**ルート**（`~/.claude` の位置）だけ。その下は相変わらず `projects/<作業パス由来の名前>/` なので、**パス依存は消えない**。

```
$CLAUDE_CONFIG_DIR/projects/<encoded-cwd>/*.jsonl
                            ~~~~~~~~~~~~~  ← ここは作業パス依存のまま
```

これが効くのは「履歴を同期フォルダやバックアップ対象に置きたい」ケース。「別パスへ移す／別PCでフォルダ名が変わる」問題は防げない。

**再発を本当に避けたいなら、新PCでもプロジェクトを同じ絶対パスに置くのが一番確実**。そうすれば slug が一致し、そのまま認識される。今回はパスを変えたのが、そもそもの引き金だった。

## 仕上げ：デスクトップアプリの索引を合成する

沼2の結論に従い、`local_*.json` を jsonl から合成した。ポイントは、**推測でごまかす部分を最小にする**こと。

- `cliSessionId` … jsonl のファイル名そのもの
- `createdAt` / `lastActivityAt` … jsonl の最初と最後の `timestamp`
- `model` … jsonl から読める
- `title` … 最初のユーザー発言から生成（または手で指定）
- `accountUuid` / `organizationUuid` … **既存の `local_*.json` から実行時に読む**（ハードコードしない）

```powershell
# 既存の local_*.json から account/org を借りる（＝この端末で一度アプリを使っていること）
$sample = Get-ChildItem $sessRoot -Recurse -Filter 'local_*.json' | Select-Object -First 1
$indexDir = $sample.Directory.FullName

# jsonl のメタ情報から索引レコードを組み立てる
$rec = [ordered]@{
    sessionId    = 'local_' + [guid]::NewGuid()
    cliSessionId = $id
    cwd          = $ProjectRoot
    originCwd    = $ProjectRoot
    createdAt    = $createdMs
    lastActivityAt = $lastMs
    model        = $model
    title        = $title
    # ... 既存の手本ファイルに合わせて残りのフィールドを埋める
}
$json = $rec | ConvertTo-Json -Depth 5 -Compress
[System.IO.File]::WriteAllText((Join-Path $indexDir "local_$([guid]::NewGuid()).json"), $json,
    (New-Object System.Text.UTF8Encoding $false))
```

アプリを完全終了して起動し直すと、「最近の項目」に旧PCの会話が並んだ。**壊れても、作ったファイルを消せば元に戻る**（＝索引は再生成可能、会話の実体 jsonl は無傷）。

## できたもの

一連の作業をスクリプト化して公開した。

**https://github.com/KanameShiga-dev/claude-code-migrate**

| スクリプト | 実行場所 | 役割 |
|---|---|---|
| `migrate_export.ps1` | 旧PC | 履歴・設定・git bundle・照合用インベントリを zip に集める |
| `migrate_import.ps1` | 新PC | SHA256照合しつつ取り込み、`cwd` を新パスへ書き換える |
| `rebuild_app_index.ps1` | 新PC | デスクトップアプリの索引を再合成する |

設計で気をつけたこと。

- **個人情報は運ばない**：機微なフォルダは中身もファイル名も出さず「件数と合計バイト数」だけで照合。
- **壊れたコピーに上書きしない**：インポートは照合を先に行い、欠落があれば中断。
- **上書き前にバックアップ**：設定や索引は退避してから置き換え。
- **まず `-DryRun`**：書き込みなしで挙動を確認してから本実行。

## まとめ／教訓

- **フォルダをコピーしただけでは履歴は移らない。** slug が作業パスに紐づくから。
- **Windows アプリ版の履歴移行は、CLI の情報だけ見ていると必ずハマる。** アプリは CLI と別の索引を持ち、CLI 用のファイルを運んでもアプリの一覧には出ない。**アプリ版利用者は索引の作り直しが必須**。
- **公式の移行手順は無い。** あるのは `/export`（読み物として書き出す）だけで、これは会話の再開用ではない。
- **履歴は既定30日で自動削除**（`settings.json` の `cleanupPeriodDays`）。大事な会話は `/export` で保全を。
- **一番確実な予防策は、新PCでも同じ絶対パスに置くこと。**

会話の中身そのものは jsonl（ただのテキスト）に残るので、最悪アプリが読めなくてもデータは消えない。壊れるのは「一覧に出るか」「再開できるか」だけ——そう割り切れば、自己責任で試す価値はあると思う。

同じ移行で沼にはまった人の役に立てば幸いです。

:::note info
繰り返しになりますが、内部ファイルを直接いじる手法はサポート外です。アップデートで壊れる前提で、バックアップを取ってからどうぞ。
:::
