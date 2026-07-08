---
id: "2026-07-08-クラウドaiだけでは届かない場所へopenclawで開発環境を棚卸しするpoc-01"
title: "クラウドAIだけでは届かない場所へ：OpenClawで開発環境を棚卸しするPoC"
url: "https://zenn.dev/yutakaosada/articles/b9e4129e14df27"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "GPT", "zenn"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

# はじめに

セルフホステッドAIエージェントを業務でどう使えるかを検証してみました。

最初は、OpenClawを使って「最新技術情報を集めて、Wikiにまとめて、Teamsへ通知する」仕組みを作ろうと考えましたが、公開情報を取得し、要約して、WikiやTeamsに流すだけであれば、Azure AI Foundry・Azure Functions・Logic Appsといったクラウドネイティブな構成で充分実現できます。  
わざわざセルフホステッドのAIエージェントを持ち出す理由が弱いのです。

セルフホステッドAIエージェントの価値は、クラウドAIと同じことをローカルで再現することではなく、クラウドAIだけでは直接触りにくい場所、例えば、ローカル端末、閉域の開発環境、Gitリポジトリ、CLI、CIログ、IssueやPull Requestの状態など。これらに近いところで動ける点にあります。

本記事では、この考え方をもとに、OpenClawを使ってローカル/閉域の開発環境を定期棚卸しし、Azure DevOps Wikiへレポートを作成し、Teamsへ通知するPoCを作った過程をまとめます。

本記事の ソースコードは、[GitHub](https://github.com/yutaka-art/openclaw-dev-snapshot)に登録しています。

<https://github.com/yutaka-art/openclaw-dev-snapshot>

# 作ったもの

今回作ったものは、開発チーム向けの日次棚卸しレポート生成の仕組みです。

Windows Task Schedulerで定時起動し、PowerShellでGitリポジトリやAzure DevOpsの情報を収集します。その結果をOpenClawに渡してMarkdownレポートを生成し、Azure DevOps Wikiに作成または更新します。最後にTeams Workflow Webhookで、Wikiへのリンクを通知します。

構成要素は次の通りです。

| 役割 | 採用技術 | 考え方 |
| --- | --- | --- |
| 定時起動 | Windows Task Scheduler | Cronと同等 |
| データ収集 | PowerShell + Git + Azure DevOps REST API | 取得処理はAIに任せない |
| レポート生成 | OpenClaw + Skill | 非定型な要約と示唆を任せる |
| Wiki投稿 | Azure DevOps Wiki API | 作成・更新・失敗時のログを制御する |
| Teams通知 | Teams Workflow Webhook | 通知は軽く作る |

データ取得、API呼び出し、Wiki更新、Teams通知はPowerShellで決定的に処理し、OpenClawには集めた情報を読み解き、チームが確認しやすい形に整理するところだけを任せました。

# PoCの考え方

## 検証スコープは小さくする

最初から複数リポジトリ、複数パイプライン、複数チーム、Teams双方向連携まで含めると、収拾がつかなくなります。今回はPoCなので、範囲をかなり絞りました。

* 対象リポジトリは1つ
* 対象ブランチは `main` または `develop`
* 対象期間は直近1日または直近7日
* 出力先はAzure DevOps Wikiの1ページ
* 通知先はTeamsのPoC用チャネル

収集対象は、まず次の範囲にしました。

* Git差分
* 直近コミット
* Azure DevOps Work Items
* Pull Requests
* Build / Pipeline結果
* 必要に応じたCIログや技術メモ

最終的な出力先は、次のようなWiki階層です。

```
/TechCatchup/YYYY/MM/YYYY-MM-DD
```

まずは「1 repo / 1 pipeline / 1 Wiki page / 1 Teams通知」にしています。

## OpenClawに任せること、任せないこと

今回の構成では、OpenClawを万能実行係にはしていません。AIエージェントにAPI呼び出しやファイル操作まで全部任せることもできますが、定期実行する業務寄りの仕組みでは、成功/失敗が追えること、同じ入力なら同じように動くこと、障害時に切り分けられることが重要です。

そのため、役割を明確に分けました。

| 領域 | 担当 | 理由 |
| --- | --- | --- |
| GitやAzure DevOpsからの情報取得 | PowerShell | 結果を制御しやすい |
| JSON化 | PowerShell | 入力形式を固定できる |
| Markdownレポート生成 | OpenClaw | 非定型な整理に向く |
| Wiki作成/更新 | PowerShell | ETagや再実行性を扱いやすい |
| Teams通知 | PowerShell | 失敗時の原因を追いやすい |

AIにはAIが得意なところを、スクリプトにはスクリプトが得意なところを担当させる。という考え方ですね。

## 作業フォルダを作る

作業用のフォルダは次のようにしました。

```
New-Item -ItemType Directory -Force -Path "C:\Work\openclaw-dev-snapshot" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\Work\openclaw-dev-snapshot\scripts" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\Work\openclaw-dev-snapshot\input" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\Work\openclaw-dev-snapshot\output" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\Work\openclaw-dev-snapshot\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\Work\openclaw-dev-snapshot\repos" | Out-Null
```

構成は次の通りです。

```
C:\Work\openclaw-dev-snapshot
├─ scripts
├─ input
├─ output
├─ logs
└─ repos
```

`repos` に対象リポジトリをcloneし、`input` に収集結果のJSON、`output` にAIが生成したMarkdownや通知用payload、`logs` に実行ログを残します。

# Azure DevOps側の準備

PowerShellからAzure DevOps REST APIを呼び出すため、次の情報を環境変数で渡します。

```
$env:ADO_ORG = "<organization-name>"
$env:ADO_PROJECT = "<project-name>"
$env:ADO_REPO_NAME = "<repository-name>"
$env:ADO_WIKI_ID = "<wiki-name-or-id>"
$env:ADO_PAT = "<Azure DevOps PAT>"
```

PATには、少なくとも次の権限を付けました。

| 用途 | 権限の目安 |
| --- | --- |
| Wiki作成・更新 | Wiki Read & Write |
| PR / Commit取得 | Code Read |
| Build / Pipeline取得 | Build Read |
| Work Item取得 | Work Items Read |

PoCでは環境変数を使いましたが、本番運用ではPATをそのまま置く設計は避けたいところです。Windows Credential Manager、SecretManagement、Managed Identityを使える構成など、もう一段きちんとした秘密情報管理に寄せるべきでしょう。

また、Task Schedulerから起動する場合、PowerShell上で一時的に設定した `$env:` は引き継がれません。PoCではUser環境変数として登録しました。

```
[Environment]::SetEnvironmentVariable("ADO_ORG", "<organization-name>", "User")
[Environment]::SetEnvironmentVariable("ADO_PROJECT", "<project-name>", "User")
[Environment]::SetEnvironmentVariable("ADO_REPO_NAME", "<repository-name>", "User")
[Environment]::SetEnvironmentVariable("ADO_WIKI_ID", "<wiki-name-or-id>", "User")
```

PATのような秘密値は、画面に出さずに登録します。

```
$SecurePat = Read-Host "Azure DevOps PAT を入力してください" -AsSecureString
$BSTR = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePat)

try {
  $PlainPat = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($BSTR)
  [Environment]::SetEnvironmentVariable("ADO_PAT", $PlainPat, "User")
}
finally {
  if ($BSTR -ne [IntPtr]::Zero) {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
  }
}
```

# Teams通知用のWebhookを準備する

Teams通知はOpenClawのTeams連携ではなく、Teams Workflow Webhookを使いました。

イメージは次の通りです。

```
Teams 対象チャネル
  → Workflows
  → Webhook アラートを チャネル に送信する
  → Webhook URLを取得
```

![](https://static.zenn.studio/user-upload/deployed-images/4c4091429bb2268b386683d7.png?sha=ebcf488d0f08422ba3e6e2b595b91ec3377a82e4)

取得したWebhook URLは環境変数に保存します。

```
$env:TEAMS_WEBHOOK_URL = "<Teams Workflow Webhook URL>"
```

Task Schedulerから起動する場合は、こちらもUser環境変数として登録しておきます。

```
$SecureWebhook = Read-Host "Teams Webhook URL を入力してください" -AsSecureString
$BSTR = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureWebhook)

try {
  $PlainWebhook = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($BSTR)
  [Environment]::SetEnvironmentVariable("TEAMS_WEBHOOK_URL", $PlainWebhook, "User")
}
finally {
  if ($BSTR -ne [IntPtr]::Zero) {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
  }
}
```

# OpenClawの準備

## OpenClawのモデルを選ぶ

今回の用途では、コードやCIログを読み、IssueやPRを整理し、チーム向けの示唆を出します。軽量モデルでも動くと思われますが、PoCではまず高精度寄りのモデルを選びました。

OpenClaw側で利用可能なモデルを確認します。

候補は次のように考えました。

| 優先 | モデル | 用途 |
| --- | --- | --- |
| 1 | `github-copilot/gpt-5.5` | 高精度な要約・構造化・判断 |
| 2 | `github-copilot/claude-opus-4.7` | 長文推論・ログ読解・レビュー向き |
| 3 | `github-copilot/gpt-5-mini` | 日次運用のコスト抑制向き |

設定例です。

```
openclaw models set github-copilot/gpt-5.5
openclaw gateway restart
```

動作確認します。

```
openclaw agent --agent main --session-key main --message "日本語で一言だけ返してください。モデル変更後のOpenClaw動作確認です。"
```

もし指定したモデルが使えない場合は、`openclaw models list` に表示された正確なモデルIDを使ってください。

## OpenClaw Skillでレポートの型を決める

今回、Skillの設計はかなり重要なポイントでした。

AIに「いい感じにまとめて」と投げると、日によって出力の粒度や構造が揺れます。日次レポートとして使うのであれば、読み手が毎回同じ構造で確認できる方が望ましいです。

そこで、OpenClaw Skillとしてレポートの型を定義しました。

```
$SkillDir = "$env:USERPROFILE\.openclaw\workspace\skills\dev-environment-snapshot-report"
New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
notepad "$SkillDir\SKILL.md"
```

<https://github.com/yutaka-art/openclaw-dev-snapshot/blob/main/skills/dev-environment-snapshot-report/SKILL.md>

Skillには、次のようなルールを入れています。

```
## Hard rules

- Do not invent facts.
- Use only the provided files, logs, command outputs, and fetched official sources.
- Do not expose secrets, tokens, PATs, cookies, environment variables, or credentials.
- Do not modify source code.
- Treat the repository as read-only unless explicitly instructed otherwise.
- Separate confirmed facts from AI interpretation.
- If information is missing, write `確認不可` rather than guessing.
```

出力形式も固定しました。

```
# 開発環境 定期棚卸しレポート

対象日: <YYYY-MM-DD>  
対象リポジトリ: <repo name>  
対象期間: <period>  
実行環境: OpenClaw self-hosted agent

---

## 1. サマリ
## 2. コード・リポジトリ状況
## 3. Issue / Work Item / PR状況
## 4. CI / Build状況
## 5. 技術的な気づき
## 6. チーム向け推奨アクション
## 7. 注意事項
```

Skillを更新したらGatewayを再起動します。

# PowerShellによる実装

## 1. GitとAzure DevOpsの情報を集める

まず、OpenClawへ渡す入力データを作ります。

<https://github.com/yutaka-art/openclaw-dev-snapshot/blob/main/scripts/Collect-DevSnapshot.ps1>

ここはPowerShellで決定的に処理します。AIに「いい感じにAPIを叩いて」とやらせるより、どのAPIから何を取得するかをスクリプト側で固定しておいた方が、定期実行では安心です。

取得した情報は、1つのJSONにまとめます。

```
$Snapshot = [ordered]@{
  generatedAt = (Get-Date).ToString("s")
  targetPeriod = "last 7 days"
  repository = @{
    name = $RepoName
    localPath = $RepoDir
    branch = $GitBranch
    status = $GitStatus
    recentCommits = $RecentCommits
    changedFiles = $ChangedFiles
  }
  azureDevOps = @{
    organization = $Org
    project = $Project
    pullRequests = $PullRequests.value | Select-Object pullRequestId, title, status, createdBy, creationDate, sourceRefName, targetRefName
    builds = $Builds.value | Select-Object id, buildNumber, status, result, queueTime, startTime, finishTime, sourceBranch, sourceVersion
    workItemIds = $WorkItemQuery.workItems | Select-Object -First 20
  }
} | ConvertTo-Json -Depth 20
```

Gitの情報は、ローカルリポジトリから取得します。

```
Push-Location $RepoDir

$GitBranch = git branch --show-current
$GitStatus = git status --short
$RecentCommits = git log --since="7 days ago" --pretty=format:"%h | %ad | %an | %s" --date=short
$ChangedFiles = git diff --name-only HEAD~10..HEAD 2>$null

Pop-Location
```

Azure DevOpsからは、PR、Build、Work Itemを取得します。

```
$PrUrl = "https://dev.azure.com/$Org/$Project/_apis/git/repositories/$RepoName/pullrequests?searchCriteria.status=active&api-version=7.1"
$PullRequests = Invoke-AdoGet $PrUrl

$BuildUrl = "https://dev.azure.com/$Org/$Project/_apis/build/builds?`$top=10&queryOrder=finishTimeDescending&api-version=7.1"
$Builds = Invoke-AdoGet $BuildUrl
```

Work ItemはWIQLで取得しました。

```
$WiqlUrl = "https://dev.azure.com/$Org/$Project/_apis/wit/wiql?api-version=7.1"
$WiqlBody = @{
  query = @"
SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType]
FROM WorkItems
WHERE [System.TeamProject] = '$Project'
AND [System.ChangedDate] >= @Today - 7
ORDER BY [System.ChangedDate] DESC
"@
} | ConvertTo-Json

$WorkItemQuery = Invoke-RestMethod -Method Post -Uri $WiqlUrl -Headers $Headers -Body $WiqlBody
```

ここまでで、OpenClawに渡す入力ファイルができます。

```
powershell.exe -ExecutionPolicy Bypass -File "C:\Work\openclaw-dev-snapshot\scripts\Collect-DevSnapshot.ps1"
```

## 2. OpenClawでMarkdownレポートを生成する

次に、収集したJSONをOpenClawに渡し、Markdownレポートを生成します。

<https://github.com/yutaka-art/openclaw-dev-snapshot/blob/main/scripts/Generate-Report.ps1>

```
$Prompt = @"
/skill dev-environment-snapshot-report

以下のスナップショットファイルを読み取り、開発環境の定期棚卸しレポートを日本語Markdownで作成してください。

スナップショット:
$SnapshotPath

出力先:
$ReportPath

要件:
- 事実と示唆を分けてください。
- コード、Issue / Work Item、PR、Build / CI状況を統合して整理してください。
- 認証情報、PAT、環境変数、個人情報は出力しないでください。
- 不明な点は推測せず、確認不可と記載してください。
- チームが次に取るべきアクションを優先度付きで整理してください。
- Markdownファイルとして保存してください。
"@
```

ここで、ひとつつまずいた点があります。

最初は固定の `session-key` を使っていましたが、GitHub Copilot経由のモデルで暗号化コンテキストまわりのエラーが出ることがありました。定期実行では、実行ごとに `session-key` を変える方が安定します。

```
$SessionKey = "dev-snapshot-$Date-$(Get-Date -Format 'HHmmss')"
openclaw agent --agent main --session-key $SessionKey --message $Prompt
```

実行します。

```
powershell.exe -ExecutionPolicy Bypass -File "C:\Work\openclaw-dev-snapshot\scripts\Generate-Report.ps1"
```

生成されたMarkdownは、次のように確認できます。

```
notepad "C:\Work\openclaw-dev-snapshot\output\dev-snapshot-report-$(Get-Date -Format 'yyyy-MM-dd').md"
```

## 3. Azure DevOps Wikiへ作成・更新する

レポートができたら、Azure DevOps Wikiへ投稿します。

<https://github.com/yutaka-art/openclaw-dev-snapshot/blob/main/scripts/Publish-ToAdoWiki.ps1>

単にPUTできればよいわけではなく、実装すべき点は意外と多くあります。日次実行では、次のことを考慮する必要があります。

* 親ページがなければ作る
* 当日日付ページがなければ新規作成する
* 当日日付ページがあれば更新する
* 既存ページ更新時はETagを使う
* 同じ日に再実行しても失敗しない

Azure DevOps Wikiでは、次のような階層ページを作る場合、親ページが存在している必要があります。

```
/TechCatchup/2026/07/2026-07-07
```

そのため、先に次のページを作成または確認します。

```
/TechCatchup
/TechCatchup/2026
/TechCatchup/2026/07
```

既存ページ更新では、GETでETagを取得し、PUT時に `If-Match` を付けます。

```
$HeadersForPut = @{
  Authorization = $script:BaseHeaders.Authorization
  'If-Match' = $ExistingPage.ETag
}
```

ページ本文は `content` として送ります。

```
$Body = @{
  content = $Content
} | ConvertTo-Json -Depth 10 -Compress

Invoke-RestMethod `
  -Method Put `
  -Uri $PageUrl `
  -Headers $HeadersForPut `
  -ContentType 'application/json; charset=utf-8' `
  -Body $Body `
  -TimeoutSec 120 | Out-Null
```

PowerShell 5.1で `Invoke-WebRequest` を使う場合は、次の警告にも引っかかりました。

```
Invoke-WebRequest は Web ページのコンテンツを解析します。
```

無人実行で止まると困るため、`-UseBasicParsing` を付けています。

```
Invoke-WebRequest `
  -Method Get `
  -Uri $PageUrl `
  -Headers $script:BaseHeaders `
  -UseBasicParsing `
  -TimeoutSec 60 `
  -ErrorAction Stop
```

また、Wiki URLを作るとき、PowerShellの変数展開にも注意が必要でした。

```
$WikiPageUrl = 'https://dev.azure.com/{0}/{1}/_wiki/wikis/{2}?pagePath={3}' -f $Org, $EncodedProject, $EncodedWikiId, $EncodedPath
```

最初は文字列内で `$WikiId?pagePath` のように書いてしまい、変数展開が崩れてURLが壊れました。こうした細かい落とし穴に、何度か足をすくわれました。

こんな感じでできますね。  
![](https://static.zenn.studio/user-upload/deployed-images/657bebce75fc6355e4553fc2.png?sha=c2ce79c80fbefdf4c5715bf1b73d88b50c30310b)

## 4. Teams Workflow Webhookで通知する

Teamsには、レポート本文を全部流さず、Wikiへのリンクだけ通知することにしました。通知は本文を読む場所ではなく、Wikiを読みに行くきっかけとして使うくらいがちょうどよいです。

<https://github.com/yutaka-art/openclaw-dev-snapshot/blob/main/scripts/Notify-Teams.ps1>

Power Automate側のアクションが `Post card in a chat or channel` の場合、単純なJSONでは失敗しました。

```
{
  "text": "開発環境 定期棚卸しレポートを作成しました"
}
```

この形式だと、次のようなエラーになります。

```
Property 'type' must be 'AdaptiveCard'
```

そのため、PowerShellからAdaptive Card形式でPOSTします。

```
$AdaptiveCard = [ordered]@{
  '$schema' = "http://adaptivecards.io/schemas/adaptive-card.json"
  type = "AdaptiveCard"
  version = "1.4"
  body = @(
    [ordered]@{
      type = "TextBlock"
      text = "開発環境 定期棚卸しレポートを作成しました"
      weight = "Bolder"
      size = "Large"
      wrap = $true
    },
    [ordered]@{
      type = "FactSet"
      facts = @(
        [ordered]@{ title = "対象日"; value = $Date },
        [ordered]@{ title = "Wikiページ"; value = $PagePath },
        [ordered]@{ title = "処理"; value = $Action }
      )
    }
  )
  actions = @(
    [ordered]@{
      type = "Action.OpenUrl"
      title = "Azure DevOps Wikiで開く"
      url = $WikiUrl
    }
  )
}
```

Power Automate側が `triggerBody()` をそのままカードとして使うのか、`triggerBody()?['card']` のようにラップされた値を参照するのかで、payloadの形が変わります。今回のPoCでは、まずRawなAdaptive CardをそのままPOSTする形にしました。

```
$Payload = $AdaptiveCard | ConvertTo-Json -Depth 30 -Compress

Invoke-RestMethod `
  -Method Post `
  -Uri $WebhookUrl `
  -ContentType "application/json; charset=utf-8" `
  -Body $Payload `
  -TimeoutSec 60 | Out-Null
```

こんな感じで通知されます。  
![](https://static.zenn.studio/user-upload/deployed-images/d1ab9a76adf9b7bc8734b1cb.png?sha=67a45932a7e006cd422a04b3fd176b0113b01e25)

## 5. 全体をまとめて実行する

最後に、各スクリプトを順番に呼ぶ `Run-DevSnapshot.ps1` を作ります。

<https://github.com/yutaka-art/openclaw-dev-snapshot/blob/main/Run-DevSnapshot.ps1>

処理の流れは次の4ステップです。

```
1. Collect development snapshot
2. Generate OpenClaw report
3. Publish report to Azure DevOps Wiki
4. Notify Teams
```

実行ログも残します。

```
$BaseDir = "C:\Work\openclaw-dev-snapshot"
$LogDir = Join-Path $BaseDir "logs"
$Now = Get-Date -Format "yyyyMMdd-HHmmss"
$LogPath = Join-Path $LogDir "dev-snapshot-$Now.log"

Start-Transcript -Path $LogPath -Append | Out-Null
```

各ステップは同じPowerShellプロセス内で実行しました。子プロセスをさらに `powershell.exe` で起動すると、環境変数やログの見え方が追いにくくなったためです。

```
Run-Step "Collect development snapshot" "$BaseDir\scripts\Collect-DevSnapshot.ps1"
Run-Step "Generate OpenClaw report" "$BaseDir\scripts\Generate-Report.ps1"
Run-Step "Publish to Azure DevOps Wiki" "$BaseDir\scripts\Publish-ToAdoWiki.ps1"
Run-Step "Notify Teams" "$BaseDir\scripts\Notify-Teams.ps1"
```

実行します。

```
powershell.exe -ExecutionPolicy Bypass -File "C:\Work\openclaw-dev-snapshot\Run-DevSnapshot.ps1"
```

## 6. Windows Task Schedulerで定期実行する

最後に、Windows Task Schedulerへ登録します。

```
$Action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File `"C:\Work\openclaw-dev-snapshot\Run-DevSnapshot.ps1`""

$Trigger = New-ScheduledTaskTrigger `
  -Weekly `
  -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday `
  -At 09:00

$Settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable

Register-ScheduledTask `
  -TaskName "OpenClaw Dev Environment Snapshot" `
  -Action $Action `
  -Trigger $Trigger `
  -Settings $Settings `
  -Description "OpenClawでローカル/閉域開発環境を棚卸しし、Azure DevOps Wikiへ投稿してTeams通知する" `
  -Force
```

動作確認します。

```
Start-ScheduledTask -TaskName "OpenClaw Dev Environment Snapshot"
Get-ScheduledTaskInfo -TaskName "OpenClaw Dev Environment Snapshot"
```

OpenClawやGitHub Copilotの認証がユーザーセッションに依存する場合があります。PoCでは、最初は「ユーザーがログオンしているときのみ実行する」設定の方が扱いやすいでしょう。

# 実行結果

最終的には、Task Schedulerから一連の処理を起動し、次の流れが通るところまで確認できました。

```
PowerShell
  → Git / Azure DevOps情報を収集
  → OpenClawでMarkdownレポート生成
  → Azure DevOps Wikiへ作成/更新
  → TeamsへAdaptive Card通知
```

Wikiには次のようなページが作成されます。

```
/TechCatchup/2026/07/2026-07-07
```

![](https://static.zenn.studio/user-upload/deployed-images/657bebce75fc6355e4553fc2.png?sha=c2ce79c80fbefdf4c5715bf1b73d88b50c30310b)

同じ日に再実行すると、既存ページをETag付きで更新します。

```
Wiki page already exists: /TechCatchup/2026/07/2026-07-07
Updating existing wiki page: /TechCatchup/2026/07/2026-07-07
Updated wiki page completed: /TechCatchup/2026/07/2026-07-07
```

Teamsには、Wikiへのリンク付きカードが投稿されます。

![](https://static.zenn.studio/user-upload/deployed-images/d1ab9a76adf9b7bc8734b1cb.png?sha=67a45932a7e006cd422a04b3fd176b0113b01e25)

# ハマったところ

PoCとはいえ、いくつかの点でつまずきました。

## Task Schedulerから環境変数が読めない

PowerShell上で `$env:ADO_PAT` のように設定しただけでは、そのPowerShellプロセス内でしか有効になりません。Task Schedulerから起動する場合は、User環境変数として登録する必要がありました。

## Azure DevOps Wikiの親ページが必要

`/TechCatchup/2026/07/2026-07-07` をいきなり作ろうとすると、親ページが存在しない場合に失敗します。

```
One or more ancestor pages of the page does not exist.
```

そのため、親ページを順番に作成または確認する処理を入れました。

## 既存Wiki更新にはETagが必要

同じ日に再実行すると、既存ページを更新する必要があります。Azure DevOps Wiki APIでは、既存ページ更新時にETagを使う形にしました。

## PowerShell 5.1の文字コードとInvoke-WebRequest

PowerShell 5.1では、日本語を含むps1を扱うときに文字化けや構文崩れが起きることがありました。UTF-8 BOM付きで保存すると安定しました。

また、`Invoke-WebRequest` では `-UseBasicParsing` を付けないと対話プロンプトが出る場合があります。Task Schedulerでは処理が止まってしまうため、ここは潰しておいた方がよいです。

## Teams WorkflowはAdaptive Cardを要求することがある

Teams Workflowのアクションによっては、単純な `{ "text": "..." }` ではなくAdaptive Card形式を期待します。エラーに `Property 'type' must be 'AdaptiveCard'` と出たら、payloadの形を見直す必要があります。

## OpenClawの固定session-keyでLLM request failed

固定の `session-key` を使っていたところ、GitHub Copilot経由のモデルで暗号化コンテキスト関連のエラーが出ることがありました。定期実行では、実行ごとに `session-key` を変える方が無難でした。

# 使ってみて感じたこと

今回やってみて一番大きかったのは、セルフホステッドAIエージェントの立ち位置が少し見えたことです。

OpenClawは、Azure AI FoundryやMicrosoft 365 Copilotの代替というより、クラウドAIだけでは届きにくい場所にいるエージェントとして考えるとしっくりきます。たとえば、次のような情報です。

* ローカルGitリポジトリ
* 開発端末上のファイル
* CLIでしか見ていない状態
* 閉域ネットワーク上の情報
* CIログ
* チーム内のIssueやPRの流れ

こうした情報を集め、AIが読み解き、チーム向けのレポートとして残す。これは、単なるチャットAIとは少し違う価値です。

ただし、何でもAIに任せるのは危険です。今回のPoCでは、データ取得や投稿はPowerShellで堅く作り、非定型な整理だけをOpenClawに任せました。この組み合わせは、業務に寄せるうえでかなり現実的だと感じています。

# OpenClawとHermesの比較について

実は、最初からOpenClawだけで進めたわけではなく、

同じくエージェント系の選択肢として、Hermesも触りました。Hermesは、Cronによる定期実行や、継続的にタスクを回していくエージェントとしての見せ方がしやすく、今回のような「毎日レポートを作る」用途にも一見合いそうでした。

一方で、今回やりたいことを分解すると、定期実行そのものよりも、次の要素が重要でした。

* ローカルリポジトリやAzure DevOpsから、必要な情報を安定して集める
* 収集結果を固定のJSONにする
* AIには非定型な要約と示唆出しだけを任せる
* Azure DevOps Wikiの作成/更新をETag込みで制御する
* Teams通知のpayloadをPower Automate側に合わせて調整する
* 失敗したときにPowerShellのログから追えるようにする

つまり、今回のPoCでは「AIエージェントが全部やる」よりも、**PowerShellで決定的に処理する部分と、AIに読み解かせる部分を分ける**方が大事でした。

その前提で見ると、HermesのCronや自律的な実行の強みは、今回の構成では少し薄まります。スケジュール実行はWindows Task Schedulerに寄せ、データ取得や投稿もPowerShellで握るためです。

比較すると、今回の判断はこんな感じでした。

| 観点 | OpenClaw | Hermes | 今回の判断 |
| --- | --- | --- | --- |
| 定期実行 | OpenClaw Cronもあるが、今回は使わない | Cron実行の見せ方がしやすい | Windows Task Schedulerに寄せる |
| レポート生成の型 | Skillでレポート形式を定義しやすい | タスク継続や改善の文脈が強い | 日次レポートの型をSkillで固定したい |
| PowerShell連携 | 外側からCLI実行しやすい | CLI実行できるが、今回は強みを活かしきれない | PowerShell主導にしやすいOpenClawを採用 |
| PoCの説明 | セルフホステッドAIエージェントがローカル/閉域情報を読む、という説明にしやすい | 自律実行・改善型エージェントとして面白い | 今回のテーマにはOpenClawが合う |
| 今後の発展 | Teams/Slack連携やSkill拡張に広げやすい | 継続実行・自己改善型のワークフローに広げやすい | 今回はOpenClaw、別テーマならHermesもあり |

誤解のないように書くと、Hermesが合わなかったわけではありません。

むしろ、継続的にタスクを回しながら改善していくエージェントとして見せるなら、Hermesの方が話を作りやすい場面もありそうです。

ただ、今回のテーマは「開発環境の棚卸し」です。

ローカル/閉域の情報を集め、AIで読み解き、Wikiに残し、Teamsに通知する。その一連の処理を、業務寄りに説明できる形で組みたかったので、最終的にはOpenClawを採用しました。

# まとめ

OpenClawを使って、ローカル/閉域の開発環境を棚卸しし、Azure DevOps WikiとTeamsへ通知するPoCをしました。

当初は技術ニュース要約を考えていましたが、それだけならクラウドネイティブな構成で十分であり、セルフホステッドAIエージェントを使う理由は、クラウドAIだけでは触りにくい開発環境の近くで動けることにあります。

今回の構成では、PowerShellがGitやAzure DevOpsから情報を集め、OpenClawがレポートを生成し、PowerShellがWiki投稿とTeams通知を担当します。AIにすべてを任せるのではなく、決定的に処理したいところはスクリプトで固め、非定型な整理や示唆出しだけをAIに任せる。この割り切りが、セルフホステッドAIエージェントを実務に近づけるうえで一番大事なポイントでした。

# 参考リンク

<https://docs.openclaw.ai/tools>

<https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-requests/get-pull-requests?view=azure-devops-rest-7.1>

<https://learn.microsoft.com/en-us/rest/api/azure/devops/wiki/pages/create-or-update?view=azure-devops-rest-7.1>

<https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook>

<https://docs.github.com/ja/copilot/reference/ai-models/supported-models>
