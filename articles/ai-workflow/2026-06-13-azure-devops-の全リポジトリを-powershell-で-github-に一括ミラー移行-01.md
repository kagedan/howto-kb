---
id: "2026-06-13-azure-devops-の全リポジトリを-powershell-で-github-に一括ミラー移行-01"
title: "Azure DevOps の全リポジトリを PowerShell で GitHub に一括ミラー移行メモ"
url: "https://qiita.com/rex0220/items/1d81d8830f5c4c25c2e0"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-06-13"
date_collected: "2026-06-14"
summary_by: "auto-rss"
query: ""
---

## はじめに

長らく Azure DevOps でソースコードを管理してきましたが、GitHub へ移行することにしました。きっかけは **生成 AI 系のツールやサービスが、軒並み GitHub を前提とした仕組みになっていた** ことです。

コーディングエージェントや各種 AI 連携ツールは、リポジトリの参照・クローン・PR 作成といった操作を GitHub の API やエコシステム前提で組んでいるものが多く、Azure DevOps のままではこの恩恵を素直に受けられない場面が増えてきました。「AI に開発を任せる」流れに乗るうえで、リポジトリの置き場所を GitHub に揃えておくのが現実的です。

そこで Azure DevOps の全リポジトリを GitHub へ移すことにしました。当初は1リポジトリずつ手作業で移行していましたが、残りをまとめて移すため、最終的に PowerShell スクリプトで一括処理する形にしました。

この記事では、その移行スクリプトと作業手順を、実際にハマったポイントも含めてまとめます。対象は **Git リポジトリの履歴(全ブランチ・全タグ)のみ**で、パイプラインや PR 履歴、Work Item の移行は扱いません。

移行案、移行手順、スクリプトは Claude に作ってもらいました。

:::note info
本記事のスクリプトは「冪等(べきとう)」に設計しています。途中で失敗しても、再実行すれば移行済み分は自動でスキップされ、未移行分だけが処理されます。
:::

## 移行方式の検討

一括移行の方式はいくつか考えられます。今回は要件と照らして比較し、3番目を採用しました。

| 方式 | 長所 | 短所 |
| --- | --- | --- |
| `gh ado2gh`(GitHub 公式の移行ツール) | PR 履歴やブランチポリシーの一部も移行可能 | GitHub Enterprise Cloud 前提の機能あり |
| エージェント型(AI に丸ごと委任) | 検証・例外処理まで自動化できる | 完全自動ではなく監督が必要 |
| **シェル/PowerShell で `git clone --mirror`** | **全履歴を確実に移行・透明・リトライ容易** | **パイプライン等は移行されない** |

今回はリポジトリの履歴だけ移ればよく、移行後の検証まで自分で握りたかったため、3番目を選びました。中核は次の3コマンドです。

```bash
git clone --mirror <ADO のリポジトリ URL>   # 全 ref を含むベアクローン
gh repo create <owner>/<name> --private     # GitHub 側にリポジトリを作成
git push --mirror <GitHub の URL>            # 全 ref をそのまま push
```

`--mirror` を使うことで、通常の `clone`/`push` では持ち越せないすべてのブランチ・タグ・参照が移行されます。

## 前提環境

Windows 上で完結させるため、PowerShell **7 以上**(`pwsh`)を使います。

:::note warn
Windows 標準の Windows PowerShell 5.1 では、`$ErrorActionPreference = "Stop"` とネイティブコマンドの標準エラー出力の組み合わせで意図しない挙動になることがあります。本スクリプトは冒頭でバージョンを確認し、5.1 では停止するようにしています。必ず `pwsh` から実行してください。
:::

必要なツールは winget でまとめて導入できます。

```powershell
winget install Git.Git GitHub.cli Microsoft.AzureCLI Microsoft.PowerShell
```

インストール後はターミナルを開き直し(PATH 反映のため)、`pwsh` を起動してから以下を実行します。

```powershell
az extension add --name azure-devops
gh auth login
```

### gh auth login のポイント

`gh auth login` では対話的に質問されます。重要なのは最後の項目です。

```text
? Where do you use GitHub? GitHub.com
? What is your preferred protocol for Git operations on this host? HTTPS
? Authenticate Git with your GitHub credentials? (Y/n)
```

最後の **「Authenticate Git with your GitHub credentials?」は必ず Y** にしてください。これは「gh が保持するトークンを git の認証情報としても使う」設定です。本スクリプトは `git push` を直接呼ぶため、ここを `n` にすると push 時に認証情報を別途用意する必要が生じ、一括処理が止まってしまいます(GitHub は HTTPS のパスワード認証を廃止しているため、`n` のままだと PAT の手動設定が別途必要になります)。

## Personal Access Token(PAT)の準備

Azure DevOps 側のアクセスには PAT が必要です。ブラウザで Azure DevOps を開き、右上の **User settings → Personal access tokens → New Token** から発行します。

設定のポイントは **スコープ** です。

| スコープ | 用途 |
| --- | --- |
| Code (Read) | リポジトリの clone |
| Project and Team (Read) | プロジェクト一覧の取得 |

:::note warn
clone に必要な `Code (Read)` だけでは不十分です。プロジェクト一覧を取得する `az devops project list` には **`Project and Team (Read)`** も必要になります。これが欠けていると、認証は通っているのに `TF400813: The user ... is not authorized to access this resource.` というエラーになります(後述)。
:::

発行したトークン文字列をその場でコピーし(画面を閉じると二度と表示されません)、環境変数に設定します。

```powershell
$env:AZURE_DEVOPS_EXT_PAT = "<コピーしたトークン文字列>"
```

:::note alert
ここに設定するのは**トークン文字列**です。フォルダのパスやトークン名ではありません。`$env:AZURE_DEVOPS_EXT_PAT = "C:\Users\xxx\tmp"` のようにパスを入れてしまうと当然ながら認証に失敗します(これは筆者がやらかしたミスです)。
PAT はパスワード同等の機密情報です。万一どこかに貼ってしまったら、同じ画面から Revoke して無効化してください。
:::

## 移行スクリプト

以下が PowerShell 版の全文です。`Migrate-AdoToGitHub.ps1` として保存します。

```powershell
<#
.SYNOPSIS
  Azure DevOps → GitHub 一括ミラー移行スクリプト(複数プロジェクト対応・強化版)
.DESCRIPTION
  - 組織内の全プロジェクトを列挙し、各プロジェクト内の全リポジトリを移行
  - GitHub に「存在し、かつ空でない」リポジトリはスキップ(冪等・再実行安全)
  - -DryRun で実行内容の確認のみ
  - 結果は migration-result.log に記録
.EXAMPLE
  .\Migrate-AdoToGitHub.ps1 -DryRun   # 振り分け確認のみ
  .\Migrate-AdoToGitHub.ps1           # 本実行
#>
[CmdletBinding()]
param(
    [switch]$DryRun
)

# ===== 設定(環境に合わせて変更)=====
$AdoOrg       = "https://dev.azure.com/yourorg"   # Azure DevOps 組織 URL
$GhOwner      = "yourorg"                          # GitHub の組織名 or ユーザー名
$GhVisibility = "--private"                        # --private / --public / --internal
# =====================================

# PowerShell 7 必須
if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Host "ERROR: PowerShell 7 以上で実行してください(現在: $($PSVersionTable.PSVersion))" -ForegroundColor Red
    Write-Host "インストール: winget install Microsoft.PowerShell  →  pwsh で起動"
    exit 1
}

$ErrorActionPreference = "Stop"
$WorkDir = Join-Path (Get-Location) "ado-migration-work"
$LogFile = Join-Path (Get-Location) "migration-result.log"
New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

# --- 前提コマンド確認 ---
foreach ($cmd in @("git", "gh", "az")) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "ERROR: $cmd が見つかりません。winget でインストールしてください。"
        exit 1
    }
}

# --- 認証確認 ---
gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: gh auth login を先に実行してください"
    exit 1
}
if ([string]::IsNullOrEmpty($env:AZURE_DEVOPS_EXT_PAT)) {
    Write-Error "ERROR: 環境変数 AZURE_DEVOPS_EXT_PAT に Azure DevOps の PAT を設定してください"
    exit 1
}

# PAT を URL に埋め込まず、ヘッダーで認証(ログ・履歴に残さない)
$basic      = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":" + $env:AZURE_DEVOPS_EXT_PAT))
$AuthHeader = "Authorization: Basic $basic"

# --- プロジェクト一覧取得 ---
Write-Log "Azure DevOps からプロジェクト一覧を取得中..."
$projectsJson = az devops project list --org $AdoOrg --query "value[].name" -o json
if ($LASTEXITCODE -ne 0) { Write-Error "プロジェクト一覧の取得に失敗しました"; exit 1 }
$projects = $projectsJson | ConvertFrom-Json
Write-Log "対象プロジェクト数: $($projects.Count)"

# --- 全プロジェクトのリポジトリを集約 ---
Write-Log "各プロジェクトのリポジトリ一覧を取得します(プロジェクト数が多いと数分かかります)"
$listSw = [System.Diagnostics.Stopwatch]::StartNew()
$repos = @()
$pIdx = 0
foreach ($project in $projects) {
    $pIdx++
    Write-Host ("  [{0}/{1}] {2} ... " -f $pIdx, $projects.Count, $project) -NoNewline -ForegroundColor DarkGray
    $repoJson = az repos list --org $AdoOrg --project $project `
        --query "[?isDisabled==``false``].{name:name, url:remoteUrl}" -o json
    if ($LASTEXITCODE -ne 0) { Write-Host ""; Write-Error "[$project] のリポジトリ一覧取得に失敗"; exit 1 }
    $list = $repoJson | ConvertFrom-Json
    foreach ($r in $list) {
        $repos += [PSCustomObject]@{ Project = $project; Name = $r.name; Url = $r.url }
    }
    Write-Host ("リポジトリ {0} 件" -f @($list).Count) -ForegroundColor DarkGray
}
$listSw.Stop()
Write-Log ("対象リポジトリ総数: {0}(一覧取得 {1:mm\:ss})" -f $repos.Count, $listSw.Elapsed)

# 一覧を保存(後から確認用)
$repos | ConvertTo-Json -Depth 3 | Set-Content -Path (Join-Path $WorkDir "repos.json") -Encoding UTF8

# --- リポジトリ名の重複チェック(別プロジェクトに同名があると GitHub 側で衝突)---
$dups = $repos | Group-Object Name | Where-Object { $_.Count -gt 1 }
if ($dups) {
    Write-Log "ERROR: 以下のリポジトリ名が複数プロジェクトで重複しています。GitHub 側で衝突するため対応方法を決めてください:"
    $dups | ForEach-Object { Write-Log ("  " + $_.Name) }
    exit 1
}

$migrated = 0
$skipped  = 0
$failed   = 0
$mainSw   = [System.Diagnostics.Stopwatch]::StartNew()
$rIdx     = 0
$total    = $repos.Count

# --- メインループ ---
foreach ($repo in $repos) {
    $rIdx++
    $project = $repo.Project
    $name    = $repo.Name
    $url     = $repo.Url
    $ghRepo  = "$GhOwner/$name"
    $ghUrl   = "https://github.com/$ghRepo.git"

    # 進捗ヘッダー(経過時間と残り時間見込み)
    $eta = ""
    if ($rIdx -gt 1) {
        $avgSec  = $mainSw.Elapsed.TotalSeconds / ($rIdx - 1)
        $remain  = [TimeSpan]::FromSeconds($avgSec * ($total - $rIdx + 1))
        $eta     = "(経過 {0:hh\:mm\:ss} / 残り見込み 約{1:hh\:mm\:ss})" -f $mainSw.Elapsed, $remain
    }
    Write-Host ("--- [{0}/{1}] {2} {3}" -f $rIdx, $total, $name, $eta) -ForegroundColor Cyan

    # 強化版チェック: GitHub に存在し、かつ空でない場合はスキップ
    $defaultBranch = gh repo view $ghRepo --json defaultBranchRef --jq ".defaultBranchRef.name" 2>$null
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($defaultBranch)) {
        Write-Log "SKIP [$rIdx/$total]: [$project] $name (GitHub に内容ありで存在)"
        $skipped++
        continue
    }

    if ($DryRun) {
        Write-Log "DRY-RUN MIGRATE [$rIdx/$total]: [$project] $name"
        $migrated++
        continue
    }

    Write-Log "MIGRATE [$rIdx/$total]: [$project] $name を移行開始"
    $mirrorDir = Join-Path $WorkDir "$name.git"

    try {
        if (Test-Path $mirrorDir) { Remove-Item -Recurse -Force $mirrorDir }

        Write-Host "    1/4 clone --mirror 中..." -ForegroundColor DarkGray
        git -c http.extraHeader=$AuthHeader clone --mirror $url $mirrorDir
        if ($LASTEXITCODE -ne 0) { throw "git clone --mirror に失敗" }

        # 空リポジトリ(push 失敗の残骸)が既にある場合は作成をスキップ
        gh repo view $ghRepo *> $null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "    2/4 GitHub リポジトリ作成中..." -ForegroundColor DarkGray
            gh repo create $ghRepo $GhVisibility
            if ($LASTEXITCODE -ne 0) { throw "gh repo create に失敗" }
        }
        else {
            Write-Host "    2/4 GitHub に空リポジトリあり(作成スキップ)" -ForegroundColor DarkGray
        }

        Write-Host "    3/4 push --mirror 中..." -ForegroundColor DarkGray
        Push-Location $mirrorDir
        try {
            git push --mirror $ghUrl
            if ($LASTEXITCODE -ne 0) { throw "git push --mirror に失敗" }
        }
        finally {
            Pop-Location
        }
        Remove-Item -Recurse -Force $mirrorDir

        # 移行後検証: 両側の HEAD コミットハッシュを突合
        Write-Host "    4/4 HEAD ハッシュ突合で検証中..." -ForegroundColor DarkGray
        $srcHead = (git -c http.extraHeader=$AuthHeader ls-remote $url HEAD | Select-Object -First 1) -split "`t" | Select-Object -First 1
        $dstHead = (git ls-remote $ghUrl HEAD | Select-Object -First 1) -split "`t" | Select-Object -First 1

        if (-not [string]::IsNullOrWhiteSpace($srcHead) -and $srcHead -eq $dstHead) {
            Write-Log "OK [$rIdx/$total]: [$project] $name 移行完了 (HEAD: $srcHead)"
            $migrated++
        }
        else {
            Write-Log "WARN [$rIdx/$total]: [$project] $name はハッシュ不一致 (src=$srcHead dst=$dstHead) 要確認"
            $failed++
        }
    }
    catch {
        Write-Log "FAILED [$rIdx/$total]: [$project] $name の移行に失敗: $($_.Exception.Message)(再実行で自動リトライされます)"
        $failed++
    }
}

# --- サマリー ---
$mainSw.Stop()
Write-Log "===== 完了 ====="
Write-Log ("移行: {0} / スキップ: {1} / 失敗: {2} (全 {3} 件, 所要 {4:hh\:mm\:ss})" -f $migrated, $skipped, $failed, $repos.Count, $mainSw.Elapsed)
if ($failed -gt 0) {
    Write-Log "失敗分は本スクリプトを再実行すれば未移行分のみ処理されます"
}
exit 0
```

## スクリプトの設計ポイント

### 1. 「プロジェクト=リポジトリ」構成への対応

環境によっては、プラグインやサービスごとにプロジェクトが分かれており、各プロジェクトの中にリポジトリがある構成になります。この場合、組織直下のリポジトリ一覧を取るだけでは不十分です。本スクリプトは **全プロジェクトを列挙 → 各プロジェクトのリポジトリを集約** という二段構えにしています。

### 2. 移行済みの除外(冪等性)

手作業で先行移行したリポジトリを二重に処理しないよう、移行前に GitHub 側を確認します。判定は単なる「存在するか」ではなく、**`defaultBranchRef` の有無で「存在し、かつ空でない」** を見ています。

```powershell
$defaultBranch = gh repo view $ghRepo --json defaultBranchRef --jq ".defaultBranchRef.name" 2>$null
```

これにより、「リポジトリ作成は成功したが push 前に失敗した残骸(空リポジトリ)」を移行済みと誤判定せず、再実行時にきちんと続きを処理できます。

### 3. PAT をコマンド履歴・ログに残さない

PAT を `https://<PAT>@dev.azure.com/...` のように URL へ埋め込む方法もありますが、これだとプロセス一覧やログにトークンが露出します。本スクリプトは HTTP ヘッダー経由で渡しています。

```powershell
$basic      = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":" + $env:AZURE_DEVOPS_EXT_PAT))
$AuthHeader = "Authorization: Basic $basic"
# ...
git -c http.extraHeader=$AuthHeader clone --mirror $url $mirrorDir
```

### 4. 移行後の検証(ハッシュ突合)

push の成功だけでは「正しく移行できた」とは言い切れません。移行直後に、Azure DevOps 側と GitHub 側それぞれの `HEAD` のコミットハッシュを `git ls-remote` で取得し、一致を確認しています。一致しなければ `WARN` を出して後から追えるようにしています。

### 5. リポジトリ名の重複検出

GitHub のリポジトリ名前空間はオーナー直下でフラットです。一方 Azure DevOps では別プロジェクトに同名リポジトリが存在しうるため、移行を始める前に重複を検出してエラー停止させ、命名方針を先に決められるようにしています。

## 作業手順

### 1. 実行ポリシーの解除

ダウンロードしたスクリプトは、実行ポリシーによりブロックされることがあります。

```text
.\Migrate-AdoToGitHub.ps1 : ... running scripts is disabled on this system.
```

このセッション限りで解除します(システム全体には影響せず、管理者権限も不要です)。

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
Unblock-File .\Migrate-AdoToGitHub.ps1
```

`Unblock-File` は、インターネット経由で入手したファイルに付く「ブロックマーク」を外すコマンドです。

### 2. ドライランで振り分けを確認

いきなり本実行せず、まず `-DryRun` で「どれがスキップされ、どれが移行対象になるか」を確認します。**ここで、スキップされる一覧が手作業で移行済みのものと一致するかを必ず目視確認してください。**

```powershell
.\Migrate-AdoToGitHub.ps1 -DryRun
```

### 3. 本実行

問題なければ本実行します。

```powershell
.\Migrate-AdoToGitHub.ps1
```

実行中は次のような進捗が表示されます(以下は移行対象が 90 件あった場合の例です)。

```text
--- [12/90] new-plugin (経過 00:03:10 / 残り見込み 約00:22:00)
[10:31:51] MIGRATE [12/90]: [new-plugin] new-plugin を移行開始
    1/4 clone --mirror 中...
    2/4 GitHub リポジトリ作成中...
    3/4 push --mirror 中...
    4/4 HEAD ハッシュ突合で検証中...
[10:32:45] OK [12/90]: [new-plugin] new-plugin 移行完了 (HEAD: a1b2c3...)
```

### 4. 結果確認とリトライ

ログから結果行だけを抽出して確認します。

```powershell
Select-String -Path migration-result.log -Pattern "OK|WARN|FAILED|SKIP"
```

- **OK** … 移行完了。ハッシュ一致を確認済み
- **WARN** … push は成功したがハッシュ不一致。移行直後に Azure 側へ push があった場合など。要確認
- **FAILED** … 移行失敗。**スクリプトを再実行するだけで未移行分のみリトライされます**

別ターミナルからログをリアルタイム監視することもできます。

```powershell
Get-Content migration-result.log -Wait
```

### 5. 移行後の後処理(任意)

全件 OK を確認したら、Azure DevOps 側のリポジトリを無効化(Project Settings → Repositories → Disable)しておくと、誤って旧リポジトリへ push する事故を防げます。完全な削除は、GitHub 側での運用が安定してからで十分です。

## ハマったポイントまとめ

実際に詰まった箇所を整理しておきます。

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `TF400813: ... not authorized` | PAT のスコープが `Code (Read)` だけで、`Project and Team (Read)` がない | PAT を作り直してスコープを追加 |
| 認証は通るのにアクセス拒否 | 環境変数にトークンではなくパスを設定していた | トークン文字列を設定し直す |
| push 時に認証で止まる | `gh auth login` で Git 連携を `n` にした | `Y` で再ログイン |
| スクリプトが実行できない | 実行ポリシーによるブロック | `Set-ExecutionPolicy -Scope Process RemoteSigned` |
| 一覧取得中に無反応に見える | プロジェクト数が多く `az` 呼び出しが逐次実行される | 進捗表示を入れて待つ(数分) |

## おわりに

`git clone --mirror` を軸にしたシンプルな方式でも、複数プロジェクトの集約・移行済みの除外・PAT の安全な扱い・移行後の検証を組み込むことで、実用的な一括移行ツールになりました。特に、冪等性(再実行で続きから処理できる)と移行後のハッシュ突合は、件数が多い移行ほど効いてきます。

移行を終えてみると、GitHub に揃えたことで生成 AI 系ツールとの連携がスムーズになりました。リポジトリの置き場所を一本化しておくことは、AI を前提とした開発フローへ移っていくうえでの地ならしになると感じています。

同じように Azure DevOps から GitHub への移行を検討している方の参考になれば幸いです。

:::note info
本記事のスクリプトは「リポジトリの履歴のみ」を対象としています。パイプライン(`azure-pipelines.yml`)を GitHub Actions に移行したい場合や、PR 履歴まで残したい場合は、`gh ado2gh`(GitHub Enterprise Importer)の利用も検討してください。
:::
