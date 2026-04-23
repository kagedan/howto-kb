---
id: "2026-04-15-discord-に赤い-cube-追加してと書くだけで-unity-ゲームが-itchio-で遊べる-01"
title: "Discord に「赤い Cube 追加して」と書くだけで Unity ゲームが itch.io で遊べるようになる仕組みを作った~Claude Code + Unity MCP + GitHub Actions で完全自動化~"
url: "https://qiita.com/kumi0708/items/679097d959d211d59a96"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

Discord のチャットに `!build シーンに赤い Cube を位置 (0, 0, 0) に追加して、シーンを保存してください` と書きます。5〜10 分後、同じ Discord のチャンネルに `🎮 ビルド完成しました!` というメッセージと itch.io の URL が来ます。URL をクリックすると、ブラウザで指示通りの Unity シーンが WebGL で動いています。

淡々と書いてしまったので画像がはいっていないのでわかりずらいですが、  
後日スクショ貼るようにします。

[時間のない方へ: 最短実装手順](#%E6%99%82%E9%96%93%E3%81%AE%E3%81%AA%E3%81%84%E6%96%B9%E3%81%B8-%E6%9C%80%E7%9F%AD%E5%AE%9F%E8%A3%85%E6%89%8B%E9%A0%86)

### 誰のための記事か

* Unity で作ったゲームを AI に触らせてみたい人
* Discord bot と AI エージェントの連携を作ってみたい人
* GitHub Actions でセルフホストランナーを使った自動ビルドを構築したい人
* 「自然言語で指示すると AI がゲームを書き換えてくれる」環境が欲しい人
* 自分がやってみたのだけど、やったことを忘れちゃうから自分の為←ここ大事

前提スキル:

* Unity の基本操作
* Python と PowerShell の読み書き
* Git の基本操作
* Discord bot を作ったことがある or 作れそう

### 完成すると何ができるか

* Discord で `!build <タスク>` と打つと、AI (Claude Code) が Unity MCP 経由で Unity Editor を直接操作する
* AI がシーンにオブジェクトを追加したり、マテリアルを作って割り当てたりする
* 変更は自動的に Git にコミット・プッシュされる
* GitHub Actions のセルフホストランナーで Unity WebGL ビルドが走る
* ビルドされた成果物が itch.io に自動デプロイされる
* Discord bot が CI の完了を検知して「完成したよ」と通知する
* PC を再起動しても全部自動で復活する (Windows サービス化)
* API が過負荷になったら自動リトライ、複数リクエストはキューで順次処理

### 使用技術

* **Unity 6000.4.1f1** (Unity 6.4) + Built-in Render Pipeline
* **Claude Code** (Anthropic の CLI エージェント)
* **Unity MCP** (`com.unity.ai.assistant` パッケージ) + relay バイナリ
* **Python 3.14** + discord.py + aiohttp
* **GitHub Actions** (セルフホストランナー)
* **butler** (itch.io 公式 CLI)
* **NSSM** (Non-Sucking Service Manager)
* **Windows 11**

## 全体アーキテクチャ

```
[Discord]
  ↓ !build <タスク>
[Discord bot (Windows サービス)]
  ↓ キューで順次処理、認証とレート制限
[run-ai-build.ps1 (PowerShell スクリプト)]
  ↓ Claude Code を呼ぶ (API 過負荷時は自動リトライ)
[Claude Code]
  ↓ Unity MCP 経由で Unity Editor を操作
[Unity Editor] (手動起動、Unity MCP Running 状態)
  ↓ シーン編集、マテリアル作成、保存
[git add/commit/push]
  ↓
[GitHub]
  ↓ workflow_dispatch トリガー
[GitHub Actions (セルフホストランナー、Windows サービス)]
  ↓ Unity で WebGL ビルド
[butler で itch.io にデプロイ]
  ↓
[itch.io で WebGL が遊べる]
  ↓
[Discord bot が GitHub API ポーリングで CI 完了を検知]
  ↓
[Discord に 🎮 完成通知]
```

ポイント:

1. **Unity Editor だけは Windows サービスにできない** (GUI アプリなので)。手動起動が必要
2. **他は全部 Windows サービス化**されているので、PC 再起動後もそのまま動く
3. **Unity は編集を「リモート」ではなく「ローカルの起動中インスタンス」に対して行う**。これが Unity MCP の仕組みの面白さ

## 環境

構築に使った環境:

* **OS**: Windows 11 (日本語環境)
* **Unity**: 6000.4.1f1 (Unity 6.4)
* **Render Pipeline**: Built-in Render Pipeline (URP ではない)
* **Unity プロジェクト場所**: `C:\Users\<user>\Documents\UnityProjects\unity-ai-lab`
* **GitHub Actions ランナー場所**: `C:\actions-runner`
* **Python**: 3.14 (venv 使用)
* **Node.js**: Claude Code が使う (最近のバージョンなら OK)
* **Git**: Git for Windows
* **Discord Bot アプリケーション**: Discord Developer Portal で作成済み
* **itch.io プロジェクト**: 作成済み (HTML kind、draft)
* **GitHub リポジトリ**: `kumi0708/unity-ai-lab` (private)

個別の手順は各 Phase で詳述します。まず Unity プロジェクトと GitHub リポジトリは作成済み、という前提で始めます。

## Phase 1: Unity MCP 接続

### 目的

Claude Code から Unity Editor を直接操作できるようにする。

### 背景: Unity MCP とは

Unity MCP は Unity Editor を外部から操作するためのプロトコル実装です。Unity 公式の `com.unity.ai.assistant` パッケージが Unity MCP のサーバーを Editor 内に立ち上げ、Claude Code がクライアントとして接続します。

ただし Claude Code と Unity Editor の直接通信はなく、間に **relay バイナリ** という中継プロセスを挟みます。構造はこう:

```
Claude Code → relay_win.exe → (TCP) → Unity Editor 内の MCP サーバー
```

### 手順

#### 1. Unity プロジェクトに `com.unity.ai.assistant` パッケージを追加

Unity Editor で **Window > Package Manager** を開きます。

左上の `+` ボタン → **Add package by name...** を選択して以下を入力:

インストール完了を待ちます。

⚠️ **注意**: このパッケージは Unity 6.4 以降でしか動きません。Unity 6.3 以前を使っている場合は動きません。

インストール後、**Edit > Project Settings > AI > Unity MCP** を開くと、MCP の状態 (Stopped / Running) を確認できます。

初回は Stopped なので、**Start** ボタンを押して Running にします。

#### 2. relay バイナリを配置

Claude Code と Unity MCP の間を中継する relay バイナリを配置します。

場所は `C:\Users\<user>\.unity\relay\relay_win.exe` です (ユーザーホーム直下の `.unity/relay/` フォルダ)。

バイナリの入手経路: このバイナリは Unity 公式のどこかから落とす必要があります。**手順は公式のドキュメントを参照してください**。2026 年 4 月時点では Unity MCP のセットアップ手順の中で入手できます。

配置したら、実行権限の問題がないか確認:

```
Test-Path C:\Users\<user>\.unity\relay\relay_win.exe
# True が返れば OK
```

#### 3. Claude Code に Unity MCP を登録

Claude Code は **MCP サーバーの一覧**を管理しています。ここに Unity MCP を追加します。

重要: PowerShell で Claude Code にコマンドを渡す時、`--` (ダッシュ 2 つ) の解釈が PowerShell と衝突する問題があります。なので cmd 経由で実行する必要があります。

管理者 PowerShell で以下を実行:

```
cmd /c 'claude mcp add unity-mcp --scope user -- "C:\Users\<user>\.unity\relay\relay_win.exe" --mcp'
```

`<user>` を自分のユーザー名に置き換えてください。

成功すると、Claude Code の MCP サーバー一覧に `unity-mcp` が追加されます。確認:

#### 4. Unity Editor で Unity MCP を Running にする

手順 1 で設定した **Edit > Project Settings > AI > Unity MCP** で **Status: Running** になっていることを再確認します。

Stopped の場合は Start ボタンを押します。

#### 5. 接続テスト

PowerShell で Claude Code を起動して、Unity MCP に接続できているか確認します:

```
claude -p --permission-mode bypassPermissions "Unity MCP を使って現在シーンに存在するゲームオブジェクトを全部リストアップしてください。"
```

期待される動作:

* Claude Code が起動
* Unity MCP 経由で Unity Editor と通信
* 現在シーンのオブジェクト一覧が返ってくる (例: `Main Camera`, `Directional Light`, `Global Volume` など)

### 詰まった話

#### `--` の問題

最初、PowerShell で直接 `claude mcp add unity-mcp --scope user -- "C:\...\relay_win.exe" --mcp` を実行したら、`--mcp` の扱いがおかしくなって registration が失敗しました。PowerShell が `--` を特別な意味に解釈してしまっているのが原因。`cmd /c '...'` で cmd 経由に切り替えたら通りました。

#### 接続できるけど `ValidTRS()` アサーションが Console に出る

Unity Console に以下のような警告が出ることがあります:

```
Assertion failed: Assertion failed on expression: 'IsValidTRS(...)'
```

これは `com.unity.ai.assistant` パッケージの内部警告で、実際のシーン編集とは無関係です。無視して OK です。

#### Unity Editor を起動していない状態で Claude Code を叩くとどうなるか

Unity MCP サーバーが動いていないので、Claude Code は「Unity に接続できない」系のエラーを返します。常に **Unity Editor を起動しておく** 必要があります。これは Phase 3-D-2 のサービス化でも解決できません (Unity Editor は GUI なので Windows サービスにできない)。

### 動作確認

以下のテストが成功すれば Phase 1 完了:

```
claude -p --permission-mode bypassPermissions "Unity MCP でシーンに Cube を位置 (0, 0, 0) に追加して、シーンを保存してください。"
```

* Unity Editor の Hierarchy に Cube が追加される
* シーンファイルが保存される
* Claude Code が完了メッセージを返す

## Phase 2: GitHub Actions による自動 WebGL ビルドと itch.io デプロイ

### 目的

git にプッシュされた Unity プロジェクトを、GitHub Actions で自動的に WebGL ビルドし、itch.io にデプロイする。

### 背景: なぜセルフホストランナーなのか

Unity のビルドを GitHub の**クラウドランナー**で実行するには、Unity ライセンスをクラウドランナーに毎回 activate する必要があり、これが面倒です。GameCI などの OSS ラッパーを使う手もありますが、Unity Personal ライセンスは商用利用の制約があるし、Unity Build Server ライセンスが別途必要です。

自宅の PC で Unity Editor が既に動いているなら、**セルフホストランナー**を立ててそこでビルドするのが一番簡単です。ライセンスは既に activate 済みなので何も追加設定はいりません。

### 手順

#### 1. GitHub でセルフホストランナーを追加

ブラウザで `https://github.com/<user>/<repo>/settings/actions/runners` を開き、**New self-hosted runner** をクリック。

* **Runner image**: Windows
* **Architecture**: x64

画面に表示される手順に従って zip をダウンロード → `C:\actions-runner\` に解凍 → `config.cmd` を実行して登録します。

⚠️ **推奨パス**: `C:\actions-runner\` を使ってください。ユーザーディレクトリ配下 (`C:\Users\<user>\actions-runner\`) だと、後で Windows サービス化した時にサービスアカウントが他ユーザーのホームディレクトリにアクセスできず permission denied になります。Windows のシステムパス配下に置くのが定石です。

config.cmd の実行:

```
cd C:\actions-runner
.\config.cmd --url https://github.com/<user>/<repo> --token <TOKEN>
```

`<TOKEN>` は GitHub の設定画面に表示される 1 時間だけ有効なトークンです。

プロンプトに従って:

* Runner group: Default (Enter)
* Runner name: 好きな名前 (デフォルトは PC 名)
* Additional labels: 空 (Enter)
* Work folder: `_work` (Enter)

この段階では **サービス化はしません**。手動起動で試します:

`√ Connected to GitHub` と `Listening for Jobs` が表示されれば OK。このウィンドウは閉じずに置いておきます (後でサービス化するのは Phase 3-D-2)。

#### 2. Unity の WebGL ビルドを CLI から実行する仕組みを作る

Unity Editor には **CLI からビルドを実行するためのインターフェース**があります。`-batchmode -executeMethod` で C# のメソッドを指定して呼び出す仕組みです。

Unity プロジェクトに `Assets/Editor/WebGLBuilder.cs` を作成します。

```
using UnityEditor;
using UnityEditor.Build.Reporting;
using System.IO;

public class WebGLBuilder
{
    public static void Build()
    {
        // ビルド対象のシーン
        string[] scenes = new[] { "Assets/Scenes/SampleScene.unity" };

        // ビルド出力先
        string outputPath = "build/WebGL";
        if (!Directory.Exists(outputPath))
            Directory.CreateDirectory(outputPath);

        // ビルド設定
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = scenes,
            locationPathName = outputPath,
            target = BuildTarget.WebGL,
            options = BuildOptions.None
        };

        // ビルド実行
        BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
        BuildSummary summary = report.summary;

        if (summary.result == BuildResult.Succeeded)
        {
            UnityEngine.Debug.Log($"Build succeeded: {summary.totalSize} bytes in {summary.totalTime}");
            EditorApplication.Exit(0);
        }
        else
        {
            UnityEngine.Debug.LogError($"Build failed: {summary.result}");
            EditorApplication.Exit(1);
        }
    }
}
```

このファイルを git にコミット。

ポイント:

* **`EditorApplication.Exit(0)` と `Exit(1)` を明示的に呼ぶ**: バッチモードで Unity を自動終了させるため
* シーンファイルのパスは自分のプロジェクトに合わせて変更
* ビルド出力先は `build/WebGL` (リポジトリ直下からの相対パス)

#### 3. `.gitignore` に Unity 関連を設定

`.gitignore` に Unity プロジェクト標準の除外設定を入れます。GitHub の github/gitignore リポジトリに公式の Unity 用テンプレートがあるので、それを使うのが確実です:

プロジェクトルートの `.gitignore` の先頭に以下を追加 (既存の .gitignore があれば統合):

```
# Unity
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]ser[Ss]ettings/

# Visual Studio
.vs/
*.csproj
*.sln
*.suo
*.user
*.userprefs

# OS
.DS_Store
Thumbs.db

# Custom (Phase 3 以降で追加される)
.ai-build.lock
.last-build-result.json
.claude/
bot/logs/
bot/.env
```

#### 4. Git LFS の設定

Unity のアセット (テクスチャ、モデル、音声、プレハブの一部) は大容量になりがちです。GitHub は 1 ファイル 100 MB の制限があるので、Git LFS で扱います。

```
cd <プロジェクトルート>
git lfs install
```

`.gitattributes` を作成:

```
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.psd filter=lfs diff=lfs merge=lfs -text
*.fbx filter=lfs diff=lfs merge=lfs -text
*.obj filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.ogg filter=lfs diff=lfs merge=lfs -text
*.unity filter=lfs diff=lfs merge=lfs -text
```

#### 5. itch.io の準備と butler のセットアップ

**itch.io のプロジェクトを作成**:

<https://itch.io/game/new> で新規プロジェクトを作成。

* **Kind of project**: HTML
* **Uploads**: 最初は空で OK (後で butler が自動アップロード)
* **Visibility**: Draft (公開しない状態)

プロジェクトの URL は `https://<user>.itch.io/<project-name>` になります。例: `https://atu708.itch.io/unity-ai-lab`。

**butler API キーを取得**:

1. <https://itch.io/user/settings/api-keys> で API キーを発行
2. キーの値をコピー (これは 1 回しか表示されません)

**GitHub リポジトリに Secret として登録**:

1. `https://github.com/<user>/<repo>/settings/secrets/actions` を開く
2. **New repository secret** をクリック
3. Name: `BUTLER_API_KEY`
4. Value: 先ほどコピーした API キー
5. **Add secret** をクリック

これで GitHub Actions から `${{ secrets.BUTLER_API_KEY }}` として参照できます。

#### 6. GitHub Actions workflow を作成

`.github/workflows/build.yml` を作成:

```
name: Build WebGL

on:
  push:
    branches:
      - main
    paths:
      - 'Assets/**'
      - 'Packages/**'
      - 'ProjectSettings/**'
      - '.github/workflows/build.yml'
  workflow_dispatch:

jobs:
  build:
    runs-on: self-hosted
    timeout-minutes: 60

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          lfs: true
          clean: false

      - name: Cleanup ephemeral files
        shell: powershell
        run: |
          Remove-Item -Recurse -Force "Packages/manifest.json.bak" -ErrorAction SilentlyContinue
          Remove-Item -Recurse -Force "unity-build.log" -ErrorAction SilentlyContinue
          Remove-Item -Recurse -Force "build/WebGL" -ErrorAction SilentlyContinue

      - name: Show environment
        shell: powershell
        run: |
          Write-Host "Working directory: $(Get-Location)"
          Write-Host "Current user: $env:USERNAME"
          Get-ChildItem | Select-Object Name, Mode

      - name: Remove ai.assistant from manifest
        shell: powershell
        run: |
          $manifestPath = "$env:GITHUB_WORKSPACE\Packages\manifest.json"
          Copy-Item $manifestPath "$manifestPath.bak"
          $json = Get-Content $manifestPath -Raw | ConvertFrom-Json
          $json.dependencies.PSObject.Properties.Remove("com.unity.ai.assistant")
          $utf8NoBom = New-Object System.Text.UTF8Encoding $false
          [System.IO.File]::WriteAllText($manifestPath, ($json | ConvertTo-Json -Depth 10), $utf8NoBom)
          Write-Host "Removed com.unity.ai.assistant from manifest.json"

      - name: Build WebGL with Unity
        shell: powershell
        run: |
          $unityExe = "C:\Program Files\Unity\Hub\Editor\6000.4.1f1\Editor\Unity.exe"
          $projectPath = $env:GITHUB_WORKSPACE
          $logPath = "$projectPath\unity-build.log"

          $args = @(
            "-batchmode",
            "-nographics",
            "-quit",
            "-projectPath", $projectPath,
            "-executeMethod", "WebGLBuilder.Build",
            "-logFile", $logPath
          )

          Write-Host "Starting Unity build..."
          $process = Start-Process -FilePath $unityExe -ArgumentList $args -PassThru -Wait -NoNewWindow
          $exitCode = $process.ExitCode
          Write-Host "Unity exit code: $exitCode"

          if (Test-Path $logPath) {
            Write-Host "=== Unity build log (last 100 lines) ==="
            Get-Content $logPath -Tail 100
          }

          if ($exitCode -ne 0) {
            Write-Error "Unity build failed with exit code $exitCode"
            exit $exitCode
          }

      - name: Restore manifest
        if: always()
        shell: powershell
        run: |
          $manifestPath = "$env:GITHUB_WORKSPACE\Packages\manifest.json"
          if (Test-Path "$manifestPath.bak") {
            Move-Item "$manifestPath.bak" $manifestPath -Force
            Write-Host "Restored manifest.json"
          }

      - name: Download butler
        shell: powershell
        run: |
          if (-not (Test-Path "C:\tools\butler\butler.exe")) {
            New-Item -ItemType Directory -Force -Path C:\tools\butler
            Invoke-WebRequest -Uri "https://broth.itch.ovh/butler/windows-amd64/LATEST/archive/default" -OutFile "C:\tools\butler\butler.zip"
            Expand-Archive -Path "C:\tools\butler\butler.zip" -DestinationPath "C:\tools\butler" -Force
            Remove-Item "C:\tools\butler\butler.zip"
          }
          & "C:\tools\butler\butler.exe" -V

      - name: Deploy to itch.io
        shell: powershell
        env:
          BUTLER_API_KEY: ${{ secrets.BUTLER_API_KEY }}
        run: |
          $butler = "C:\tools\butler\butler.exe"
          & $butler push build\WebGL <itch-user>/<itch-project>:webgl --userversion $env:GITHUB_SHA
          if ($LASTEXITCODE -ne 0) {
            Write-Error "butler push failed with exit code $LASTEXITCODE"
            exit $LASTEXITCODE
          }
```

**プレースホルダーを置き換えてください**:

* `<itch-user>/<itch-project>` → 例: `atu708/unity-ai-lab`

重要なポイントを解説します:

**`runs-on: self-hosted`**: セルフホストランナーで実行します。

**`paths` フィルタ**: Assets、Packages、ProjectSettings、workflow ファイル自体のどれかが変更された時だけ CI を起動します。bot のコードや PowerShell スクリプトの変更では CI が走らないようにしています。

**`clean: false`**: これが極めて重要です。デフォルトの `clean: true` だと checkout が実行されるたびに `_work` ディレクトリの中身を全削除してしまい、Unity の `Library/` キャッシュも消えてしまいます。そうするとビルド時間が毎回 15〜17 分になります。`clean: false` にすれば `Library/` が保持されて、2 回目以降のビルドが 5 分程度に短縮されます。

**`Cleanup ephemeral files` ステップ**: `clean: false` にしたことで残る「ビルドの残骸」を明示的に削除します。前回のマニフェストバックアップ、ビルドログ、前回の `build/WebGL` 出力など。

**`Remove ai.assistant from manifest` ステップ**: これが今回一番ハマった部分です。`com.unity.ai.assistant` パッケージは Editor 用のもので、WebGL ビルド時にコンパイルエラーを起こします (`TraceSinkConfigManager` のエラーなど)。このエラーを回避するため、**ビルド前にパッケージをマニフェストから削除し、ビルド後に復元する** 方式を取っています。

JSON の書き換えで注意: Windows の PowerShell でファイルを書き出すとき、デフォルトで UTF-8 BOM 付きになってしまいます。Unity のマニフェストは BOM 付きだと読み込めないので、`System.Text.UTF8Encoding $false` (BOM なし) を明示的に指定して書き出します。

**`if: always()` でのマニフェスト復元**: ビルドが失敗しても manifest.json を元に戻します。これがないと次回のローカル操作でマニフェストが壊れた状態になります。

**butler のダウンロード**: セルフホストランナーなので butler が入っていなければ自動でダウンロードします。`C:\tools\butler\` 配下にキャッシュすることで、2 回目以降は再ダウンロードなし。

**butler push**: `<itch-user>/<itch-project>:webgl` の `:webgl` はチャンネル名です。HTML プロジェクトなら任意の名前でいいですが、WebGL を示す慣習的な名前として `webgl` を使います。`--userversion $env:GITHUB_SHA` で commit SHA をバージョンとして記録します。

#### 7. 初回ビルドを動かす

設定ができたら、何か小さな変更 (例えば空のスクリプトを Assets/ に追加) を push して CI をトリガーします:

```
cd <プロジェクトルート>
git add .
git commit -m "Trigger initial CI build"
git push
```

GitHub の Actions タブでビルドが始まるのを確認します。初回は Library キャッシュがないので **15〜17 分** かかります。成功すれば itch.io の プロジェクトページに WebGL が自動アップロードされます。

**確認方法**: ブラウザで `https://<itch-user>.itch.io/<project-name>` を開いて **Ctrl+F5** でリロード。Unity ロゴが出て、作ったシーンが動けば成功です。

### 詰まった話

#### `com.unity.ai.assistant` のコンパイルエラー

最初に `ai.assistant` パッケージを入れた状態でビルドしようとしたら、以下のエラーで失敗しました:

```
Assets/Plugins/... TraceSinkConfigManager.cs(xx,xx): error CSxxxx: ...
```

このパッケージは Editor で動く前提のもので、WebGL ターゲットへのビルドを想定していません。GitHub Issue や discussion を調べても「ビルド時には除外すべき」という情報しかなかったので、上記のように **ビルド前にマニフェストから除外 → ビルド後に復元** 方式を採用しました。

#### `clean: true` でビルド時間が 3 倍に

最初は `actions/checkout@v4` のデフォルト設定 (`clean: true`) で作ったら、毎回のビルドが 15〜17 分。おかしいなと思ってログを見たら、Unity が `Library/` フォルダを毎回再構築していました。これは checkout の `clean: true` が `_work` の中身を全消しするからで、`clean: false` に変えたら 2 回目以降は 5〜7 分に短縮されました。

#### マニフェストの BOM 問題

PowerShell の `Set-Content` は UTF-8 で書き出すと BOM が付きます。Unity はマニフェストが BOM 付きだと `manifest.json is not a valid JSON file` と言って起動すらしません。`[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)` で BOM なしを明示する必要があります。

#### butler が失敗する

初回は butler の API キーが設定されていなくて `no API key` エラーで失敗しました。GitHub リポジトリの Secret に `BUTLER_API_KEY` を設定したら解決。Secret の値は発行された API キーをそのまま貼り付ければ OK。

### 動作確認

以下が成功すれば Phase 2 完了:

1. `git push` で main ブランチに Unity 関連の変更を入れると CI が起動する
2. CI のログに Unity の `Build succeeded` が出る
3. itch.io のプロジェクトページに WebGL がアップされる
4. ブラウザで WebGL が動く

初回 17 分、2 回目以降は 5〜7 分、という時間感覚を覚えておくと運用で役立ちます。

## Phase 3-A: 手動ループで AI に Unity を編集させる

### 目的

Phase 1 で Claude Code から Unity MCP 経由で Unity を操作できるようになり、Phase 2 で git push から itch.io までの自動化ができました。これを **人間の手でつないで** 1 サイクルを回します。自動化の前に「手順が全部通る」ことを確認する段階です。

### 手順

#### 1. AI に Unity を編集させる

PowerShell で:

```
cd C:\Users\<user>\Documents\UnityProjects\unity-ai-lab
claude -p --permission-mode bypassPermissions "シーンに赤い Cube を位置 (0, 0, 0) に追加して、シーンを保存してください。"
```

`-p` (非対話モード) と `--permission-mode bypassPermissions` (ツール実行の確認をスキップ) がポイント。これがないと対話的に許可を求められて止まります。

#### 2. AI の作業結果を確認

Unity Editor に戻って Hierarchy を確認。`Cube` というオブジェクトが追加されていれば成功です。

この時点では、シーンが保存されていてもマテリアルは割り当てられていないかもしれません (後の Phase 3-D で解決)。

#### 3. Git にコミットしてプッシュ

```
git add .
git commit -m "AI: Add red cube"
git push
```

#### 4. CI の完了を待つ

GitHub の Actions タブで CI を監視。完了したら itch.io でリロードして、追加したオブジェクトが見えることを確認。

### 学び

この時点では人間が 4 つの手順 (Claude 呼び出し → 確認 → git 操作 → CI 監視) を手動でやっているので、面倒です。でも「全部繋がっている」ことは確認できたので、次はこれをスクリプト化します。

## Phase 3-B: PowerShell スクリプト 1 本にまとめる

### 目的

Phase 3-A の手順を 1 つの PowerShell スクリプトに統合する。

### 設計

スクリプトは 1 つの引数 (AI へのタスク文) を受け取り、以下を自動実行:

1. **Pre-check**: ワーキングツリーが綺麗か、ビルドロックが存在しないか確認
2. **Lock ファイル作成**: 同時実行を防ぐ
3. **Claude Code 実行**: AI に Unity を編集させる
4. **Git commit & push**: 変更をリモートに反映
5. **結果を JSON ファイルに保存**: 後で bot が読める形式で記録
6. **Lock ファイル削除**: 次回の実行を許可

### スクリプト本体

`scripts/run-ai-build.ps1` を作成 (この時点ではまだリトライ機構やプロンプト補強は入れていない最小版):

この段階のスクリプトは、最終形 (Phase 3-D で完成) の前身です。最終版を Phase 3-D で示すので、ここでは **必要な機能と構造の説明** だけにします。

主な要素:

* `param([string]$Task)`: タスク文字列を受け取る
* `$ErrorActionPreference = "Stop"`: エラーで即座に停止
* `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`: 日本語の文字化け防止
* `$OutputEncoding = [System.Text.Encoding]::UTF8`: 子プロセスへの入力エンコーディング

実行は以下のように:

```
.\scripts\run-ai-build.ps1 "シーンに青い Sphere を位置 (0, 2, 0) に追加して、シーンを保存してください"
```

**完成版のコード全文は Phase 3-D-1 のセクションで示します** (リトライ、プロンプト補強、JSON 保存など全部入り)。ここでは「このスクリプトが次の Discord bot の起点になる」という構造だけ押さえてください。

### 詰まった話

#### PowerShell の文字化け

最初、スクリプト内で `claude -p ...` を呼んだ後、日本語の応答が `蜷医ｋ縺ｰ` みたいに化けていました。原因は Windows の PowerShell 5.1 のデフォルト出力エンコーディングが cp932 (Shift-JIS) で、Claude Code が UTF-8 で出力した日本語が cp932 として解釈されてしまうため。

対処は 2 行追加するだけ:

```
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
```

これをスクリプトの先頭に入れると、子プロセスの出力も UTF-8 で解釈されるようになります。保存するときは **BOM 付き UTF-8** にするのを忘れずに (メモ帳の「名前を付けて保存」で文字コードを UTF-8 BOM 付きに)。

## Phase 3-C: Discord bot から AI を起動する

### 目的

Phase 3-B の PowerShell スクリプトを Discord 経由で起動できるようにする。ユーザーは Discord で `!build <タスク>` と打つだけ。

### 設計の選択肢

Discord bot から PowerShell スクリプトを呼ぶ方法はいくつかあります:

* **A. subprocess で `powershell.exe -Command "..."`**: 一番シンプル、でも日本語を含むタスク文で破綻
* **B. subprocess で `powershell.exe -File "..."`**: ファイル経由だけど引数エスケープが難しい
* **C. subprocess で `powershell.exe -EncodedCommand "..."`**: Base64 エンコードで渡す、日本語対応

今回は **C (EncodedCommand)** を採用しました。理由は日本語のタスク文を安全に渡すため。

### スクリプトの標準出力を読む方法の選択肢

PowerShell スクリプトの結果 (成功/失敗、コミット SHA、Claude の応答など) を bot が受け取る方法:

* **A. 標準出力をパイプで読む**: `stdout=asyncio.subprocess.PIPE`
* **B. JSON ファイル経由**: スクリプトが結果を `.last-build-result.json` に書き出し、bot が読む

**最初は A で実装** しましたが、**CLIXML 問題** で破綻しました (後述の詰まり話)。最終的に **B (JSON ファイル経由)** を採用しました。

### Discord bot 本体

`bot/bot.py` を作成:

最終版 (認証、レート制限、キューイング込み) は Phase 3-D-5 で示します。ここでは Phase 3-C 段階の **最小動作版** の構造を示します。

最小版の機能:

* `!ping` で `pong` を返す (疎通確認)
* `!build <タスク>` で PowerShell スクリプトを起動
* 同時実行制御 (`asyncio.Lock`)
* 結果は `.last-build-result.json` から読む
* Claude の応答を Discord に表示

#### 必要なライブラリ

Python の仮想環境を作ってインストール:

```
cd C:\Users\<user>\Documents\UnityProjects\unity-ai-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install discord.py python-dotenv aiohttp
```

#### `.env` ファイル

`bot/.env` を作成 (これは git にコミットしない):

```
DISCORD_BOT_TOKEN=あなたのDiscordボットトークン
```

トークンは Discord Developer Portal (<https://discord.com/developers/applications>) でアプリを作って、Bot セクションで Reset Token して取得。

`.gitignore` に `bot/.env` を追加済みであることを確認してください。

#### Discord Bot アプリの設定

Discord Developer Portal で以下を確認:

* **Bot セクション**: **MESSAGE CONTENT INTENT** を ON にする (これがないと `!build` のテキストを読めない)
* **OAuth2 > URL Generator**: `bot` scope を選択、権限は `Send Messages`, `Read Message History`, `Read Messages/View Channels` など
* 生成された URL でサーバーに bot を招待

#### bot.py 最小版の構造

最小版は EncodedCommand で PowerShell を起動して、結果 JSON を読んで Discord に返すだけ。完成版のコードは Phase 3-D-5 で示します。

### 動作確認

bot を起動:

起動時のログ:

```
Bot logged in as <botname>#<discrim>
Connected to 1 guild(s):
  - <サーバー名>
Bot is ready.
```

Discord で:

→ `pong` が返る

```
!build シーンに青い Sphere を位置 (0, 2, 0) に追加して、シーンを保存してください
```

期待される動作:

1. bot が「🔨 ビルド開始」と応答
2. 1〜2 分後、「✅ Unity 編集完了」+ Claude の応答 + Commit SHA
3. 人間が GitHub Actions の進捗を確認
4. 5〜10 分後、itch.io で反映を確認

### 詰まった話

ここからが Phase 3-C の本番です。4 つの大きな問題にぶつかりました。

#### 詰まり 1: 文字化け (EncodedCommand が必要だった理由)

最初は subprocess で `powershell.exe -Command "& 'path\to\script.ps1' '<タスク>'"` のように実行していました。でも日本語のタスク文を渡すと、PowerShell 側で `蜀溘＞縺ｫ` のような文字化けが発生。

原因は subprocess が標準エンコーディングで引数をバイト列に変換する時、cp932 として解釈されてしまうため。日本語文字が Windows のコマンドラインを通る時の落とし穴です。

対処は **EncodedCommand** を使うこと:

```
ps_command = f"& '{SCRIPT_PATH}' '{task.replace(chr(39), chr(39)+chr(39))}'"
encoded = base64.b64encode(ps_command.encode("utf-16-le")).decode("ascii")

process = await asyncio.create_subprocess_exec(
    "powershell.exe",
    "-NoProfile",
    "-NonInteractive",
    "-ExecutionPolicy", "Bypass",
    "-OutputFormat", "Text",
    "-EncodedCommand", encoded,
    ...
)
```

ポイント:

* `encode("utf-16-le")`: PowerShell の `-EncodedCommand` は UTF-16 LE Base64 を期待している
* `.replace(chr(39), chr(39)+chr(39))`: シングルクォートのエスケープ (PowerShell では `''` で 1 つのシングルクォート)

これで日本語タスク文が安全に渡せるようになりました。

#### 詰まり 2: CLIXML 問題 (結果 JSON 経由方式の採用)

最初、スクリプトの標準出力をパイプで受け取って bot 側で JSON パースしていました:

```
process = await asyncio.create_subprocess_exec(
    ..., stdout=asyncio.subprocess.PIPE, ...
)
stdout, _ = await process.communicate()
output = stdout.decode("utf-8")
result = json.loads(output)  # ← ここで失敗
```

ところが、`json.loads` が失敗する。stdout に以下のような内容が混じっていました:

```
#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <S S="Error">...</S>
  ...
</Objs>
{"status": "success", ...}
```

これが **CLIXML 問題**です。PowerShell は `Write-Error` や `Write-Warning` を stdout ではなく stderr に出しますが、`asyncio.subprocess` + PowerShell の組み合わせで `-OutputFormat Text` を指定しないと、**エラー情報が XML でラップされて stdout に混入**します。

対処の選択肢:

* A. `-OutputFormat Text` を指定する: 効くときと効かないときがある
* B. stderr を DEVNULL にリダイレクト: エラー情報が消えるのは困る
* C. **結果を JSON ファイルに書き出して bot が読む**: stdout 問題を完全に回避

**C を採用**しました。`run-ai-build.ps1` は結果を `.last-build-result.json` に書き出して exit。bot は stdout を読まずに、ファイルから結果を読みます。

```
process = await asyncio.create_subprocess_exec(
    ...,
    stdout=asyncio.subprocess.DEVNULL,  # ← 捨てる
    stderr=asyncio.subprocess.DEVNULL,
)
await process.wait()

with open(RESULT_FILE, "r", encoding="utf-8") as f:
    result = json.load(f)
```

これで CLIXML 問題は完全に回避できました。副次的に「スクリプトの出力が bot のログを汚さない」というメリットもあります。

#### 詰まり 3: `.claude/settings.local.json` が勝手に変更される

テストを繰り返すうちに、毎回 `.claude/settings.local.json` が「modified」として git status に出てくるようになりました。これは Claude Code がセッション情報や tool 許可状態をここに保存しているため、`claude` コマンドを実行するたびに書き換えられる。

これがあると次回の Pre-check で「ワーキングツリーが汚れている」と言って止まってしまいます。

対処は `.gitignore` に追加して追跡対象から外すこと:

```
Add-Content -Path .gitignore -Value "`n# Claude Code local settings`n.claude/"
git rm --cached .claude/settings.local.json
git commit -m "Ignore .claude/ local settings"
```

`git rm --cached` は「ファイル自体は残すけど git の追跡対象から外す」コマンドです。`--cached` を忘れるとファイルも消えるので注意。

#### 詰まり 4: `.last-build-result.json` も git に入ってしまう

同じ理由で、`.last-build-result.json` も毎回スクリプトが書き換えるので git 追跡対象になっていると厄介です。これも `.gitignore` に追加:

```
# Build result file
.last-build-result.json
```

### Phase 3-C 完了の目安

以下が動けば Phase 3-C の本質的な目標達成:

* Discord で `!build <タスク>` を投げる
* bot が PowerShell スクリプトを起動
* スクリプトが Claude Code を呼んで Unity を編集
* git commit & push
* JSON ファイルに結果を保存
* bot が JSON を読んで成功/失敗を Discord に通知
* Claude の応答プレビューが **日本語で読める** (文字化けしていない)

ここまで来たら、人間がやることは **Discord で `!build` を投げる** だけ。CI 監視と itch.io 確認はまだ手動ですが、それは Phase 3-D-3 で自動化します。

## Phase 3-D: 運用堅牢化の全体像

Phase 3-C までで「Discord で `!build` を投げれば AI が Unity を編集して git push する」という基本動作ができました。Phase 3-D ではこれを実運用に耐える形にします。

Phase 3-D のサブフェーズ:

* **3-D-1**: リトライ機構 (API 過負荷への対応)
* **3-D-X**: プロンプト補強 (AI にマテリアル割り当てを強制する)
* **3-D-3**: CI 完了通知 (GitHub API ポーリング)
* **3-D-2**: サービス化 (ランナーと bot を Windows サービスに)
* **3-D-4**: 認証 / レート制限
* **3-D-5**: キューイング

番号の順番が少しずれているのは、実際の作業順番に合わせたからです (リトライ機構をやりたくて始めたら、途中でマテリアル問題が発生して中断、先にプロンプト補強で解決してからリトライに戻った、などの経緯)。

## Phase 3-D-1: リトライ機構

### 目的

Anthropic API が過負荷 (HTTP 529 `overloaded_error`) になっても、bot が自動で待ってリトライするようにする。

### 背景

実際に運用中にこのエラーに遭遇しました。Claude Code からのリクエストが Anthropic 側で捌ききれずに `overloaded_error` が返されると、`!build` が失敗してユーザーは手動で再実行するしかない状態でした。

Anthropic のステータスページを見ると、2026 年 4 月には複数回の elevated errors が発生しています。API 過負荷は「たまにある」ではなく「日常的に発生しうる」と考えた方が現実的です。

### 設計

リトライは 2 つの場所に実装できます:

* **A. `bot.py` 側でリトライ**: bot から PowerShell スクリプトを複数回呼び直す
* **B. `run-ai-build.ps1` 側でリトライ**: スクリプト内で Claude Code 呼び出しだけリトライ

**B を選びました**。理由:

* A だと git の状態管理が複雑になる。1 回目の試行で何かファイル変更されたら、2 回目の実行前に Pre-check に引っかかる
* B なら Claude Code の呼び出しだけ再試行できて、git の操作は 1 回だけ
* B なら Discord から見ると「1 回の `!build` に時間がかかっただけ」に見える

リトライ戦略:

* 最大 **3 回** まで試行
* **指数バックオフ**: 1 回目失敗後 30 秒、2 回目失敗後 60 秒
* **overloaded\_error のみリトライ**: それ以外のエラー (実際のバグなど) は即座に諦める
* 結果 JSON に `attempts` フィールドを追加して何回目で成功したかを記録

### `run-ai-build.ps1` の更新

次のセクション (Phase 3-D-X) と合わせて、`run-ai-build.ps1` の完成版を示します。

## Phase 3-D-X: プロンプト補強 (マテリアル割り当て問題の解決)

### 目的

AI が「マテリアルを作ったのにオブジェクトに割り当てない」問題を解決する。

### 問題の発見

リトライ機構のテストをしていた時、Unity Editor のシーンをよく見ると、AI が作ったオブジェクトが全部**白っぽい灰色**になっていました。

調査すると:

* ✅ オブジェクトの形状は指示通り (Cube, Sphere, Capsule)
* ✅ オブジェクトの位置も指示通り
* ✅ `Assets/Materials/` フォルダにマテリアルは作られている (少なくとも一部は)
* ❌ **オブジェクトの MeshRenderer に `Default-Material` がついたまま**
* ❌ AI の応答には「マテリアルを作成して割り当てました」と書いてある

つまり **AI が嘘をついている or ステップを省略している**。

### 原因の掘り下げ

別のテストで AI に「Unity MCP のツール仕様を教えて」と聞くと、完璧な説明が返ってきました:

* マテリアルアセット作成は `Unity_ManageAsset` ツール
* GameObject への割り当ては `Unity_ManageGameObject` ツールの `component_properties.MeshRenderer.material` プロパティ
* 「通常は 2 ステップの流れ」

つまり **AI は正しい手順を完全に理解している**のに、実際のタスク実行時にはステップ 2 (割り当て) を省略していた。これは「面倒なステップを省く傾向」で、プロンプトが弱いと発生しがち。

さらに、別のテストで「白い Cylinder を追加して」と指示した時の応答を見ると:

```
完了しました。
- 作成: 白い Cylinder を位置 (-3, 0, 0) に追加
- 保存: Assets/Scenes/SampleScene.unity に保存済み

デフォルトのシリンダーマテリアルは白色なので、そのまま白い円柱として表示されます。
```

AI が「デフォルトが白だからマテリアル作る必要ない」と **合理的に省略を判断** していたのです。論理的には正しいけど、一貫性がない (青や紫は専用マテリアル作るのに、白だけ作らない) し、後で「白を青に変えて」みたいな指示があった時にマテリアルがないと困ります。

### 対処: プロンプトにチェックリストを強制注入

CLAUDE.md に書くだけでは AI がこの判断を揺るがせるので、**`run-ai-build.ps1` でユーザーのタスク文に強制的にチェックリストを追加**します。

重要なポイント:

* **具体的なツール名と JSON 例を示す**: AI が「どのツールをどう呼ぶべきか」で迷わない
* **「省略禁止」を明示する**: 「デフォルトのままで OK と判断する省略は禁止」
* **色の RGB 対応表を提示**: 「白」を「RGB(1,1,1,1)」に変換する過程をスキップできる
* **「今までこの失敗が頻発しています」と伝える**: AI に「これは重要な注意事項」と認識させる
* **完了報告の形式を指定**: 「作成したオブジェクト名」「マテリアルの RGB 値」「MeshRenderer.material の確認結果」を必須化

### `run-ai-build.ps1` の完成版

以下が Phase 3-D-1 (リトライ) + Phase 3-D-X (プロンプト補強) を統合した完成版です:

run-ai-build.ps1 のコードながいのでまとめました。

```
#Requires -Version 5.1
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Task
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = "C:\Users\<user>\Documents\UnityProjects\unity-ai-lab"
$LockFile = Join-Path $ProjectRoot ".ai-build.lock"
$ResultFile = Join-Path $ProjectRoot ".last-build-result.json"
$GameUrl = "https://<itch-user>.itch.io/<project-name>"
$ActionsUrl = "https://github.com/<user>/<repo>/actions"

# リトライ設定
$MaxAttempts = 3
$BackoffSeconds = @(30, 60)

function Write-Section($msg) {
    Write-Host ""
    Write-Host ("=" * 70)
    Write-Host " $msg"
    Write-Host ("=" * 70)
}

function Write-Info($msg) { Write-Host "[INFO] $msg" }
function Write-Ok($msg)   { Write-Host "[OK]   $msg" }
function Write-Warn($msg) { Write-Host "[WARN] $msg" }
function Write-Err($msg)  { Write-Host "[ERR]  $msg" }

function Save-Result {
    param(
        [string]$Status,
        [string]$Message,
        [string]$CommitSha = "",
        [string]$ClaudeOutput = "",
        [int]$DurationSeconds = 0,
        [int]$Attempts = 1
    )
    $result = @{
        status = $Status
        message = $Message
        task = $Task
        commit_sha = $CommitSha
        claude_output = $ClaudeOutput
        duration_seconds = $DurationSeconds
        attempts = $Attempts
        game_url = $GameUrl
        actions_url = $ActionsUrl
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
    }
    $json = $result | ConvertTo-Json -Depth 10
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($ResultFile, $json, $utf8NoBom)
    Write-Info "Result saved to $ResultFile"
}

function Test-IsOverloadError($output) {
    if (-not $output) { return $false }
    return ($output -match "overloaded_error|529|Overloaded")
}

# Step 0: Pre-check
Write-Section "Step 0: Pre-check"

Set-Location $ProjectRoot
Write-Info "Project root: $ProjectRoot"
Write-Info "Task: $Task"

if (Test-Path $LockFile) {
    Write-Err "Another build is in progress (lock: $LockFile)"
    Save-Result -Status "error" -Message "Another build is in progress"
    exit 1
}

$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Err "Working tree has uncommitted changes:"
    git status --short
    Save-Result -Status "error" -Message "Working tree has uncommitted changes. Commit or discard them first."
    exit 1
}
Write-Ok "Working tree is clean"

$lockBody = "PID: $PID`nStart: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`nTask: $Task"
Set-Content -Path $LockFile -Value $lockBody
Write-Ok "Lock file created"

try {
    Write-Section "Step 1: Claude Code running Unity task (with retry)"

    # プロンプト補強: 省略防止のチェックリスト + 具体的なツール使用例
    $promptSuffix = @"

【厳守事項】このタスクを完了するには、以下の手順を必ず全て実行してください。省略は禁止です。

# 必須手順

1. オブジェクトには内容が分かる名前を必ず付ける (例: WhiteCylinder, RedCube, BlueSphere)。
   Unity のデフォルト名 (Cube, Sphere, Cylinder など) のままにしないこと。

2. 色が指定されている場合、以下の2ステップを必ず両方実行する。片方だけは禁止。

   ## ステップ A: マテリアルアセットを作成 (Unity_ManageAsset ツール)

   {
     "Action": "Create",
     "Path": "Assets/Materials/<色名>Material.mat",
     "AssetType": "Material",
     "Properties": {
       "shader": "Standard",
       "color": [R, G, B, 1]
     }
   }

   ## ステップ B: GameObject の MeshRenderer に割り当て (Unity_ManageGameObject ツール)

   {
     "action": "modify",
     "target": "<オブジェクト名>",
     "component_properties": {
       "MeshRenderer": {
         "material": "Assets/Materials/<色名>Material.mat"
       }
     }
   }

   ステップ B を省略すると、見た目は白いままになります。必ず実行してください。

3. 割り当て後、Unity_ManageGameObject の get アクションで MeshRenderer の状態を確認し、
   material が想定通りに設定されているか検証する。

4. シーンファイル (Assets/Scenes/SampleScene.unity) を必ず保存する。

5. Unity Console を確認し、エラーや警告があれば報告する。

6. 完了報告には以下を必ず含める:
   - 作成したオブジェクト名
   - 作成したマテリアルのパス
   - マテリアルの色の RGB 値
   - **MeshRenderer.material が割り当てられたことの確認結果** (重要)
   - シーン保存の確認

# 色のRGB対応表 (参考)

- 白: [1, 1, 1, 1]
- 黒: [0, 0, 0, 1]
- 赤: [1, 0, 0, 1]
- 緑: [0, 1, 0, 1]
- 青: [0, 0, 1, 1]
- 黄: [1, 1, 0, 1]
- 紫: [0.5, 0, 0.5, 1]
- オレンジ: [1, 0.5, 0, 1]
- ピンク: [1, 0.4, 0.7, 1]
- 水色: [0.5, 0.8, 1, 1]

# 重要な禁止事項

- 「デフォルトのままで OK」と判断する省略は絶対禁止
- マテリアル作成だけして割り当てないことは禁止 (今までこの失敗が頻発しています)
- 割り当て確認を省略することは禁止
"@

    $fullPrompt = $Task + $promptSuffix

    $claudeOutputStr = ""
    $claudeExit = -1
    $totalDuration = 0
    $attempt = 0
    $success = $false

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        Write-Info "Attempt $attempt of $MaxAttempts"

        $claudeStart = Get-Date
        $claudeOutput = & claude -p --permission-mode bypassPermissions $fullPrompt 2>&1
        $claudeExit = $LASTEXITCODE
        $claudeDuration = (Get-Date) - $claudeStart

        $claudeOutputStr = ($claudeOutput | Out-String).Trim()
        $totalDuration += [int]$claudeDuration.TotalSeconds

        Write-Host ""
        Write-Host "----- Claude Code output (attempt $attempt) -----"
        Write-Host $claudeOutputStr
        Write-Host "----- end -----"
        Write-Host ""

        Write-Info "Attempt $attempt duration: $([int]$claudeDuration.TotalSeconds) seconds (total: $totalDuration)"

        if ($claudeExit -eq 0) {
            Write-Ok "Claude Code succeeded on attempt $attempt"
            $success = $true
            break
        }

        if (Test-IsOverloadError $claudeOutputStr) {
            Write-Warn "Overload error detected (attempt $attempt)"
            if ($attempt -lt $MaxAttempts) {
                $waitSec = $BackoffSeconds[$attempt - 1]
                Write-Info "Waiting $waitSec seconds before retry..."
                Start-Sleep -Seconds $waitSec
                continue
            } else {
                Write-Err "All $MaxAttempts attempts failed due to API overload"
                break
            }
        } else {
            Write-Err "Non-retryable error (exit $claudeExit). Aborting."
            break
        }
    }

    if (-not $success) {
        $errMsg = if (Test-IsOverloadError $claudeOutputStr) {
            "Claude API overloaded (tried $attempt times)"
        } else {
            "Claude Code failed (exit $claudeExit)"
        }
        Save-Result -Status "error" -Message $errMsg -ClaudeOutput $claudeOutputStr -DurationSeconds $totalDuration -Attempts $attempt
        exit 1
    }

    Write-Ok "Claude Code task finished after $attempt attempt(s)"

    Write-Section "Step 2: Commit and push changes"

    $changes = git status --porcelain
    if (-not $changes) {
        Write-Warn "No file changes. AI may have done nothing."
        Save-Result -Status "no_changes" -Message "AI made no changes" -ClaudeOutput $claudeOutputStr -DurationSeconds $totalDuration -Attempts $attempt
        exit 0
    }

    Write-Info "Changed files:"
    git status --short

    git add .
    if ($LASTEXITCODE -ne 0) {
        Save-Result -Status "error" -Message "git add failed" -ClaudeOutput $claudeOutputStr -DurationSeconds $totalDuration -Attempts $attempt
        exit 1
    }

    $commitMsg = "AI: $Task"
    if ($commitMsg.Length -gt 72) {
        $commitMsg = $commitMsg.Substring(0, 69) + "..."
    }

    git commit -m $commitMsg
    if ($LASTEXITCODE -ne 0) {
        Save-Result -Status "error" -Message "git commit failed" -ClaudeOutput $claudeOutputStr -DurationSeconds $totalDuration -Attempts $attempt
        exit 1
    }

    $commitSha = (git rev-parse HEAD).Trim()
    Write-Ok "Committed: $commitMsg ($commitSha)"

    git push
    if ($LASTEXITCODE -ne 0) {
        Save-Result -Status "error" -Message "git push failed" -ClaudeOutput $claudeOutputStr -CommitSha $commitSha -DurationSeconds $totalDuration -Attempts $attempt
        exit 1
    }
    Write-Ok "git push done"

    Write-Section "Step 3: Done"
    Save-Result -Status "success" -Message "Pushed successfully. CI is building." -ClaudeOutput $claudeOutputStr -CommitSha $commitSha -DurationSeconds $totalDuration -Attempts $attempt
    Write-Host "GAME_URL=$GameUrl"
}
finally {
    if (Test-Path $LockFile) {
        Remove-Item $LockFile -Force
        Write-Info "Lock file removed"
    }
}

exit 0
```

プレースホルダー:

* `<user>`: Windows ユーザー名 (例: `kumi0`)
* `<itch-user>/<project-name>`: itch.io のプロジェクト (例: `atu708/unity-ai-lab`)
* `<user>/<repo>`: GitHub リポジトリ (例: `kumi0708/unity-ai-lab`)

これを **BOM 付き UTF-8** で保存。日本語が入っているので BOM なしだと Unicode 系の問題が起きることがあります。

### CLAUDE.md の重要性

プロンプト補強と同時に、`CLAUDE.md` もプロジェクトルートに置いておきます。これは Claude Code が自動で読む「プロジェクト指示書」です。内容例:

```
# プロジェクト指示

このプロジェクトは Unity 6.4 (6000.4.1f1) の WebGL ゲームです。

## 基本情報

- Unity バージョン: 6000.4.1f1 (Unity 6.4)
- Render Pipeline: Built-in Render Pipeline (URP ではない)
- Input Handling: Both (Input System + Legacy Input)
- 主要シーン: `Assets/Scenes/SampleScene.unity`

## マテリアル規則

- マテリアルは `Assets/Materials/` に配置
- シェーダーは必ず `Standard` を使用
- マテリアル名は `<色名または用途名>Material.mat`

## シーン編集後の必須作業

- シーンを必ず保存 (`Assets/Scenes/SampleScene.unity`)
- Unity Console でエラーや警告を確認
- MeshRenderer に指定のマテリアルが割り当てられていることを確認
```

プロンプト補強だけでは足りない「常識」を CLAUDE.md に書いておく。プロンプトは毎回の実行時注意書き、CLAUDE.md は常時参照される基本ルール、という役割分担です。

### 詰まった話

#### AI が「合理的に」省略する

上述の通り、AI は「デフォルトが白だから作らなくていい」という合理的判断で省略することがあります。これを防ぐには、**「たとえ合理的に見えても省略するな」と明示** する必要があります。

プロンプトに「省略禁止」と 1 回書くのではなく、3 回くらい違う表現で書くのが効く印象でした:

* 「省略は禁止です」
* 「たとえ『白』のようにデフォルト色に近くても省略しない」
* 「『デフォルトのままで OK』と判断する省略は絶対禁止」

しつこいくらい念押しする方が結果が安定します。

#### `renderer.material` vs `renderer.sharedMaterial` の警告

AI が Unity MCP でマテリアルを割り当てる時、Unity Console に以下のような警告が出ることがあります:

```
Instantiating material due to calling renderer.material during edit mode. 
This will leak materials into the scene. You most likely want to use renderer.sharedMaterial instead.
```

これは Edit モードで `material` プロパティを触るとマテリアルのインスタンスが作られる (=シーンに埋め込まれる) ための警告。正しくは `sharedMaterial` を使うべき。

実害はあまりないので今はスルーしていますが、気になるなら CLAUDE.md に「`sharedMaterial` を使うこと」と追記できます。

## Phase 3-D-3: CI 完了通知

### 目的

GitHub Actions のビルド完了を bot が自動検知して、Discord に「完成したよ」と通知する。

### 背景

Phase 3-C 時点では、`!build` の結果として「GitHub Actions でビルド中... (5〜10 分かかります)、完成したら itch.io を確認してください」というメッセージが bot から出るだけでした。ユーザーは自分で GitHub Actions ページを見に行くか、「そろそろかな」と予想して itch.io をリロードする必要がありました。

これを bot が自動でやれば、体験が完全に変わります。**投げて待っていれば結果が通知される** という本当の意味での自動化。

### 設計

GitHub REST API の `/repos/<owner>/<repo>/actions/runs?head_sha=<SHA>` エンドポイントで、指定の commit SHA に対応するワークフロー実行の状態を取得できます。これを定期的に叩いて、`status == "completed"` になるのを待てばいい。

* **ポーリング間隔**: 30 秒ごと
* **初期待機**: 20 秒 (commit push 直後だとまだ workflow が登録されていないため)
* **タイムアウト**: 25 分 (当初 15 分にしていたが、初回ビルド 17 分に対応できず延長)
* **認証**: GitHub Personal Access Token (PAT) を使用

Private リポジトリの場合は PAT が必須。Public なら不要ですが、レートリミット (認証なしで 60 req/hour) を考えると認証ありが安全です。

### PAT の取得

1. <https://github.com/settings/tokens?type=beta> で Fine-grained personal access tokens を作成
2. Token name: `unity-ai-lab-bot` など
3. Expiration: 好きな期間
4. Repository access: **Only select repositories** で対象リポジトリを選択
5. Repository permissions:
   * **Actions**: Read-only
   * **Contents**: Read-only
6. Generate token
7. 表示されたトークンをコピー (1 回しか表示されない)

このトークンは Discord bot の `.env` に追加します (次セクション)。

### `.env` の更新

`bot/.env` に以下を追加:

```
GITHUB_TOKEN=<さっき取得したPAT>
GITHUB_REPO=<user>/<repo>
```

### bot.py に CI 監視機能を追加

bot.py を更新して、`!build` 成功後に **別タスクで CI 監視** を開始するようにします。完成版コードは Phase 3-D-5 (最終版) で示しますが、構造は以下のような感じ:

```
import aiohttp

CI_POLL_INTERVAL_SEC = 30
CI_POLL_TIMEOUT_SEC = 1500  # 25 分
CI_INITIAL_WAIT_SEC = 20

async def fetch_workflow_run(session, commit_sha):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
    params = {"head_sha": commit_sha, "per_page": 5}
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with session.get(url, params=params, headers=headers) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        runs = data.get("workflow_runs", [])
        return runs[0] if runs else None

async def monitor_ci(ctx, commit_sha, game_url):
    short_sha = commit_sha[:7]
    elapsed = 0

    await asyncio.sleep(CI_INITIAL_WAIT_SEC)
    elapsed += CI_INITIAL_WAIT_SEC

    async with aiohttp.ClientSession() as session:
        run_url = None
        while elapsed < CI_POLL_TIMEOUT_SEC:
            run = await fetch_workflow_run(session, commit_sha)
            if run is None:
                await asyncio.sleep(CI_POLL_INTERVAL_SEC)
                elapsed += CI_POLL_INTERVAL_SEC
                continue

            run_url = run.get("html_url")
            status = run.get("status")
            conclusion = run.get("conclusion")

            if status == "completed":
                if conclusion == "success":
                    await ctx.send(
                        f"🎮 ビルド完成しました! (commit `{short_sha}`)\n"
                        f"プレイ: {game_url}\n"
                        f"ビルドログ: {run_url}"
                    )
                else:
                    await ctx.send(f"❌ CI 失敗: {conclusion} ({run_url})")
                return

            await asyncio.sleep(CI_POLL_INTERVAL_SEC)
            elapsed += CI_POLL_INTERVAL_SEC

        # タイムアウト
        await ctx.send(f"⏰ CI 監視タイムアウト (25 分経過、commit `{short_sha}`)")
```

そして `build` コマンドの成功ハンドリングで:

```
if status == "success":
    await ctx.send("✅ Unity 編集完了 ...")
    # CI 監視を別タスクで起動 (bot をブロックしない)
    if commit_sha:
        asyncio.create_task(monitor_ci(ctx, commit_sha, game_url))
```

**ポイント**: `asyncio.create_task()` で別タスクにするので、bot は CI 監視中も他のコマンドに反応できます。

### 詰まった話

#### タイムアウトが 15 分では足りなかった

最初は `CI_POLL_TIMEOUT_SEC = 900` (15 分) にしていました。平常時のビルド (Library キャッシュ有効) は 5〜7 分で終わるので余裕と思っていたのですが、セルフホストランナーをサービス化した時に `_work` フォルダを消した結果、キャッシュがなくなって初回ビルド 16 分かかり、タイムアウトに引っかかって「⏰ タイムアウトしました」メッセージが出ました。

**教訓**: タイムアウトは「平常時 + バッファ」ではなく「最悪のケース + バッファ」で設定すべき。25 分くらいにしておけば初回ビルドでも安心です。

#### Rate limit の心配は不要

30 秒に 1 回のポーリングなので、認証ありの PAT (5000 req/hour) なら余裕で収まります。複数の `!build` が並行に監視されても問題なし。

### Phase 3-D-3 完了の目安

* Discord で `!build` を投げる
* AI が編集 → git push (2 分以内)
* 5〜17 分後、bot から自動で `🎮 ビルド完成しました! (URL)` が来る
* 人間が GitHub Actions を見に行く必要がない

---

## Phase 3-D-2: サービス化 (ランナーと bot を Windows サービスに)

### 目的

PC を再起動しても、GitHub Actions ランナーと Discord bot が自動で復活するようにする。

### 背景

ここまでの状態だと、PC を再起動するたびに以下を手動で立ち上げる必要がありました:

1. Unity Editor (Unity Hub からプロジェクトを開く)
2. `./run.cmd` で actions-runner を起動 (PowerShell ウィンドウを閉じずに保持)
3. `python bot.py` で Discord bot を起動 (別の PowerShell ウィンドウ)

3 つのウィンドウが机の上でゴチャゴチャしますし、間違えて閉じたら止まります。PC を再起動するたびに 5 分かけて立ち上げるのはストレスです。

このうち **Unity Editor は GUI アプリなのでサービス化できません**。これだけは手動。でも残り 2 つはサービス化できるので、それをやります。

### Phase 3-D-2a: actions-runner のサービス化

#### 既存のランナー登録を削除

ランナーは **設定時にサービス化オプションを指定する** 必要があり、既に設定済みだと作り直しになります。

1. 現在の `./run.cmd` を Ctrl+C で停止
2. GitHub のランナー画面 (`https://github.com/<user>/<repo>/settings/actions/runners`) で、該当ランナーの `...` メニューから **Remove runner** を選択
3. 2FA の確認が出たら承認
4. 表示される削除コマンド `./config.cmd remove --token <トークン>` のトークンをコピー
5. PowerShell で実行:

```
cd C:\actions-runner
.\config.cmd remove
# プロンプトでトークンを貼り付け
```

#### サービスとして再登録

新しい登録トークンを取得:

`https://github.com/<user>/<repo>/settings/actions/runners/new` で Windows / x64 を選択すると `--token <TOKEN>` の値が表示されます。

**管理者 PowerShell** で実行:

```
cd C:\actions-runner
.\config.cmd --url https://github.com/<user>/<repo> --token <TOKEN> --runasservice --name <PC名> --labels self-hosted,Windows,X64 --work _work
```

対話プロンプトが出た場合:

1. Runner group: Enter (Default)
2. Runner name: Enter (デフォルトの PC 名)
3. Additional labels: Enter (なし)
4. Work folder: Enter (`_work`)
5. **Run as service?**: **`Y`** と入力して Enter (ここ重要!)
6. Service account: Enter (デフォルトの `NT AUTHORITY\NETWORK SERVICE`)

成功メッセージ:

```
√ Service actions.runner.<owner>-<repo>.<PC名> successfully installed
√ Service actions.runner.<owner>-<repo>.<PC名> successfully set recovery option
√ Service actions.runner.<owner>-<repo>.<PC名> successfully started
```

#### サービスの動作確認

```
Get-Service "actions.runner.*"
```

`Running` を確認。GitHub の設定画面でもランナーが **緑 + Idle** になっていることを確認。

#### 実行ポリシーの設定

サービスアカウント (NetworkService) では、デフォルトの PowerShell 実行ポリシーがスクリプトの実行を禁じている場合があります。管理者 PowerShell で:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

`LocalMachine` スコープなので、全ユーザー (NetworkService 含む) に適用されます。

#### `_work` フォルダの所有権問題 (ハマったポイント)

サービスアカウントが NetworkService に変わった瞬間、**既存の `_work` フォルダのファイル所有者が以前のユーザーのまま**なので、git が「dubious ownership」エラーで checkout を拒否します。

```
fatal: detected dubious ownership in repository at 'C:/actions-runner/_work/...'
```

対処: 一度 `_work` を削除して、次回のジョブで NetworkService が作り直す:

```
Stop-Service "actions.runner.*"
cd C:\actions-runner
Remove-Item -Recurse -Force _work
Start-Service "actions.runner.*"
```

⚠️ これをやると Library キャッシュも消えるので、次回のビルドは初回相当の 15〜17 分かかります。その次から 5〜7 分に戻ります。

### Phase 3-D-2b: Discord bot のサービス化

#### 方針

Python スクリプトを Windows サービスにするツールはいくつかありますが、**NSSM (Non-Sucking Service Manager)** を使います。

理由:

* GUI でサービス設定ができる
* 仮想環境の Python にも対応
* ログのファイル出力・ローテーションが楽
* クラッシュ時の自動再起動機能がある
* 広く使われていて信頼できる

#### NSSM のインストール

PowerShell を新しく開き直して、PATH が反映されたか確認:

#### 現在動いている bot を停止

既に `python bot.py` が動いているなら、そのウィンドウで Ctrl+C で停止。

#### bot をサービス登録

管理者 PowerShell で:

```
nssm install UnityAILabBot
```

GUI ダイアログが開きます。タブごとに以下を設定:

**Application タブ**:

* Path: `C:\Users\<user>\Documents\UnityProjects\unity-ai-lab\.venv\Scripts\python.exe`
* Startup directory: `C:\Users\<user>\Documents\UnityProjects\unity-ai-lab\bot`
* Arguments: `bot.py`

**Details タブ**:

* Display name: `Unity AI Lab Discord Bot`
* Description: `Discord bot for Unity AI Lab automation`
* Startup type: `Automatic`

**Log on タブ**:

* Log on as: `This account` を選択
* Account: `.\<user>` (例: `.\Atu0`)
* Password: Windows ログインパスワード (Microsoft アカウントの場合はそのアカウントのパスワード、**PIN は使えない**)
* Confirm password: 同じ

**I/O タブ**:

* Output (stdout): `C:\Users\<user>\Documents\UnityProjects\unity-ai-lab\bot\logs\bot.out.log`
* Error (stderr): `C:\Users\<user>\Documents\UnityProjects\unity-ai-lab\bot\logs\bot.err.log`

**File rotation タブ**:

* Rotate files: チェック
* Rotate while service is running: チェック
* Restrict rotation to files bigger than: `1048576` (1 MB)
* Rotate every: `86400` 秒 (1 日)

**Exit actions タブ**:

* On exit: `Restart application` (デフォルト)
* Delay restart by: `5000` ミリ秒 (5 秒)

設定が全部済んだら **Install service** ボタン。

#### ログフォルダの作成

I/O タブで指定したパスのフォルダを先に作っておく必要があります:

```
New-Item -ItemType Directory -Force -Path C:\Users\<user>\Documents\UnityProjects\unity-ai-lab\bot\logs
```

`.gitignore` にも追加:

#### サービス起動

```
Start-Service UnityAILabBot
Get-Service UnityAILabBot
```

`Running` を確認。

#### 動作確認

Discord で bot のステータス (右側メンバー一覧) が **緑のドット (オンライン)** になっているか確認。`!ping` を投げて `pong` が返るか確認。

ログ確認:

```
Get-Content C:\Users\<user>\Documents\UnityProjects\unity-ai-lab\bot\logs\bot.err.log -Tail 20
```

### 詰まった話

#### Microsoft アカウントの PIN ではサービスを設定できない

Windows 11 では PIN でログインするのが普通ですが、NSSM のサービスアカウントには **本来のパスワード** が必要です。PIN しか覚えていない場合、Microsoft アカウントのパスワードを思い出す (or リセット) する必要があります。

<https://account.live.com/password/reset> でリセット可能。

#### `_work` 所有権問題 (上述)

actions-runner のサービス化でアカウントが NetworkService に変わった場合、既存の `_work` フォルダの所有者が不一致になって git が失敗する。`_work` を削除して作り直せば解決。

#### Python の print() がログに出ない問題

サービスで動いている Python スクリプトは、`print()` の出力が **バッファリング** されてログファイルに即座に反映されません。discord.py の INFO ログは stderr に出るので `bot.err.log` で見えますが、bot.py 内の `print()` 文は見えにくいです。

対処 (任意):

```
import sys
sys.stdout.reconfigure(line_buffering=True)
```

または NSSM の Environment タブで `PYTHONUNBUFFERED=1` を設定。

今回は致命的じゃないのでスルーしました。

## Phase 3-D-4: 認証 / レート制限

### 目的

`!build` を叩けるユーザーを制限し、1 日あたりの実行回数に上限を設ける。

### 背景

Discord bot をサーバーに入れているとき、**誰でも `!build` を叩けてしまう**状態は危険です:

* 嫌がらせで大量にビルドを投げられる
* Anthropic API の課金が暴走する
* 意図しないシーン変更が入る

少人数で使う分でも、**誰が実行可能か** と **1 日何回まで** の制限は入れておきたい。

### 設計

**認証**: Discord ユーザー ID のホワイトリスト方式

ロールベース (特定のロールを持つユーザーだけ許可) という選択肢もありますが、1 人 〜 数人の運用ならユーザー ID の直接指定が一番シンプル。将来ロール方式にしたくなれば拡張可能。

**レート制限**: 1 ユーザーあたり 1 日 20 回

日付が変わったらリセット。メモリ上の辞書で管理 (永続化なし)。bot 再起動で使用回数はリセットされますが、再起動はそう頻繁じゃないので問題なし。

### Discord ユーザー ID の取得

1. Discord の設定 (左下の歯車)
2. **詳細設定** → **開発者モード** を ON
3. 自分のアバター or 名前を右クリック → **ユーザーID をコピー**
4. 18〜19 桁の数字がクリップボードに入る

### `.env` の更新

`bot/.env` に追加:

```
ALLOWED_USER_IDS=<あなたのDiscordユーザーID>
DAILY_BUILD_LIMIT=20
MAX_QUEUE_SIZE=10
```

複数ユーザーを許可する場合はカンマ区切り: `ALLOWED_USER_IDS=123,456,789`

### 実装内容

bot.py に以下を追加:

* `.env` から `ALLOWED_USER_IDS` を読んで set にパース
* `build_usage = {}` 辞書でユーザーごとの使用回数を管理
* `check_and_consume_quota(user_id)` 関数で「許可するか」「今何回目か」を返す
* `!build` 実行時に認証 + レート制限チェック
* `!quota` コマンドで残り回数確認

完成版コードは次の Phase 3-D-5 の後に全文掲載します。

## Phase 3-D-5: キューイング

### 目的

複数の `!build` リクエストを順番に処理する。

### 背景

Phase 3-D-4 までの実装では、ビルド実行中に他の `!build` が投げられると `build_lock.locked()` で弾かれていました。1 人運用でも「思いついた順に投げて、自動で順番に処理」できると便利です。

### 設計

Python の `asyncio.Queue` を使います:

* bot 起動時に `build_queue = asyncio.Queue(maxsize=10)` を作成
* `build_worker()` という永久ループのワーカーを 1 つだけ起動
* ワーカーが `await queue.get()` で待機し、来たリクエストを 1 つずつ処理
* `!build` コマンドハンドラは、認証・レート制限チェックを通ったらキューに put するだけ
* キューが満杯 (10 件) になったら拒否

ポイント:

* **排他制御はキューが代替**: Python の asyncio.Queue + 単一ワーカーの組み合わせで、自然に順次処理になる
* **認証・レート制限はキューに入れる前に実施**: 不正なリクエストをキューに溜めない
* **レート制限のクォータはキューに入れた時点で消費**: もし後でキャンセルしたら返却する (refund)

### 完成版 bot.py 全文

Phase 3-D-1, 3-D-3, 3-D-4, 3-D-5 すべてを統合した最終版:

bot.py のコードながいんでまとめました

```
"""
Discord bot for Unity AI Lab
Final version: retry, prompt reinforcement, CI notification, auth, rate limit, queue
"""

import os
import json
import asyncio
import base64
import aiohttp
import discord
from datetime import datetime, date
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

# .env から環境変数を読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "<user>/<repo>")

# 認証設定
ALLOWED_USER_IDS_STR = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS = set()
if ALLOWED_USER_IDS_STR:
    for uid in ALLOWED_USER_IDS_STR.split(","):
        uid = uid.strip()
        if uid.isdigit():
            ALLOWED_USER_IDS.add(int(uid))

DAILY_BUILD_LIMIT = int(os.getenv("DAILY_BUILD_LIMIT", "20"))
MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "10"))

if not TOKEN:
    print("ERROR: DISCORD_BOT_TOKEN not found in .env")
    exit(1)

if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN not found in .env. CI monitoring will be disabled.")

if not ALLOWED_USER_IDS:
    print("WARNING: ALLOWED_USER_IDS is empty. Bot will reject all !build commands.")

# 設定
PROJECT_ROOT = Path(r"C:\Users\<user>\Documents\UnityProjects\unity-ai-lab")
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run-ai-build.ps1"
RESULT_FILE = PROJECT_ROOT / ".last-build-result.json"

# CI ポーリング設定
CI_POLL_INTERVAL_SEC = 30
CI_POLL_TIMEOUT_SEC = 1500  # 25 分
CI_INITIAL_WAIT_SEC = 20

# レート制限管理: {user_id: (date, count)}
build_usage = {}

# ビルドキュー
build_queue: asyncio.Queue = None  # on_ready で初期化

def check_and_consume_quota(user_id: int):
    """ユーザーの 1 日あたりのビルド回数をチェックして消費"""
    today = date.today()
    last_date, count = build_usage.get(user_id, (today, 0))
    if last_date != today:
        count = 0
    if count >= DAILY_BUILD_LIMIT:
        return False, count, DAILY_BUILD_LIMIT
    build_usage[user_id] = (today, count + 1)
    return True, count + 1, DAILY_BUILD_LIMIT

def refund_quota(user_id: int):
    """ビルド実行前に何か問題があった場合、消費したクォータを返却する"""
    today = date.today()
    last_date, count = build_usage.get(user_id, (today, 0))
    if last_date == today and count > 0:
        build_usage[user_id] = (today, count - 1)

# Bot の Intents 設定
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    global build_queue
    if build_queue is None:
        build_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        bot.loop.create_task(build_worker())

    print(f"Bot logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Connected to {len(bot.guilds)} guild(s):")
    for guild in bot.guilds:
        print(f"  - {guild.name} (ID: {guild.id})")
    print(f"GitHub repo: {GITHUB_REPO}")
    print(f"GitHub token: {'set' if GITHUB_TOKEN else 'NOT SET'}")
    print(f"Allowed users: {len(ALLOWED_USER_IDS)} user(s)")
    print(f"Daily build limit: {DAILY_BUILD_LIMIT}")
    print(f"Max queue size: {MAX_QUEUE_SIZE}")
    print("Bot is ready.")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("pong")

@bot.command(name="quota")
async def quota(ctx):
    """残りビルド回数を確認"""
    user_id = ctx.author.id
    if user_id not in ALLOWED_USER_IDS:
        await ctx.send("❌ あなたはこの bot を使う権限がありません。")
        return

    today = date.today()
    last_date, count = build_usage.get(user_id, (today, 0))
    if last_date != today:
        count = 0

    remaining = DAILY_BUILD_LIMIT - count
    queue_size = build_queue.qsize() if build_queue else 0
    await ctx.send(
        f"📊 今日のビルド使用状況: {count} / {DAILY_BUILD_LIMIT} 回\n"
        f"残り: {remaining} 回\n"
        f"現在のキュー: {queue_size} 件"
    )

@bot.command(name="queue")
async def queue_status(ctx):
    """キューの状態を確認"""
    if build_queue is None:
        await ctx.send("⚠️ キューが初期化されていません")
        return
    size = build_queue.qsize()
    await ctx.send(f"📥 現在のキュー: {size} 件")

async def fetch_workflow_run(session, commit_sha):
    """指定の commit に対するワークフロー実行を取得"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
    params = {"head_sha": commit_sha, "per_page": 5}
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with session.get(url, params=params, headers=headers) as resp:
        if resp.status != 200:
            text = await resp.text()
            print(f"GitHub API error: {resp.status} {text[:200]}")
            return None
        data = await resp.json()
        runs = data.get("workflow_runs", [])
        return runs[0] if runs else None

async def monitor_ci(ctx, commit_sha, game_url):
    """CI の完了を待って Discord に通知する"""
    if not GITHUB_TOKEN:
        await ctx.send("⚠️ GITHUB_TOKEN が設定されていないため CI 監視はスキップされます")
        return

    short_sha = commit_sha[:7]
    elapsed = 0

    await asyncio.sleep(CI_INITIAL_WAIT_SEC)
    elapsed += CI_INITIAL_WAIT_SEC

    async with aiohttp.ClientSession() as session:
        run_url = None

        while elapsed < CI_POLL_TIMEOUT_SEC:
            try:
                run = await fetch_workflow_run(session, commit_sha)
            except Exception as e:
                print(f"GitHub API exception: {e}")
                run = None

            if run is None:
                await asyncio.sleep(CI_POLL_INTERVAL_SEC)
                elapsed += CI_POLL_INTERVAL_SEC
                continue

            run_url = run.get("html_url")
            status = run.get("status")
            conclusion = run.get("conclusion")

            if status == "completed":
                if conclusion == "success":
                    await ctx.send(
                        f"🎮 ビルド完成しました! (commit `{short_sha}`)\n"
                        f"プレイ: {game_url}\n"
                        f"ビルドログ: {run_url}"
                    )
                elif conclusion == "failure":
                    await ctx.send(
                        f"❌ CI ビルドが失敗しました (commit `{short_sha}`)\n"
                        f"ログ確認: {run_url}"
                    )
                elif conclusion == "cancelled":
                    await ctx.send(
                        f"⚠️ CI ビルドがキャンセルされました (commit `{short_sha}`)\n"
                        f"ログ確認: {run_url}"
                    )
                else:
                    await ctx.send(
                        f"❓ CI 完了、結果不明: {conclusion} (commit `{short_sha}`)\n"
                        f"ログ確認: {run_url}"
                    )
                return

            await asyncio.sleep(CI_POLL_INTERVAL_SEC)
            elapsed += CI_POLL_INTERVAL_SEC

        timeout_min = CI_POLL_TIMEOUT_SEC // 60
        await ctx.send(
            f"⏰ CI 監視がタイムアウトしました ({timeout_min}分経過、commit `{short_sha}`)\n"
            f"ビルドはまだ続いている可能性があります。\n"
            f"確認: {run_url if run_url else 'https://github.com/' + GITHUB_REPO + '/actions'}"
        )

async def process_build(request):
    """キューから取り出したビルドリクエストを処理する"""
    ctx = request["ctx"]
    task = request["task"]
    current = request["current"]
    limit = request["limit"]
    enqueued_at = request["enqueued_at"]

    wait_sec = int((datetime.now() - enqueued_at).total_seconds())
    wait_msg = f" (キューで {wait_sec} 秒待機)" if wait_sec >= 5 else ""

    if RESULT_FILE.exists():
        RESULT_FILE.unlink()

    remaining = limit - current
    await ctx.send(
        f"🔨 ビルド開始 (今日 {current}/{limit} 回目、残り {remaining} 回){wait_msg}\n"
        f"タスク: {task}\n"
        f"⚙️ Claude Code 実行中... (API 過負荷時は最大 3 回まで自動リトライします)"
    )

    ps_command = f"& '{SCRIPT_PATH}' '{task.replace(chr(39), chr(39)+chr(39))}'"
    encoded = base64.b64encode(ps_command.encode("utf-16-le")).decode("ascii")

    try:
        process = await asyncio.create_subprocess_exec(
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy", "Bypass",
            "-OutputFormat", "Text",
            "-EncodedCommand", encoded,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.wait()
        exit_code = process.returncode
    except Exception as e:
        await ctx.send(f"❌ スクリプト起動エラー: `{type(e).__name__}: {e}`")
        return

    if not RESULT_FILE.exists():
        await ctx.send(
            f"❌ 結果ファイルが見つかりません (exit: {exit_code})\n"
            f"スクリプトが想定外の終了をしました。"
        )
        return

    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            result = json.load(f)
    except Exception as e:
        await ctx.send(f"❌ 結果ファイル読み込みエラー: `{type(e).__name__}: {e}`")
        return

    status = result.get("status", "unknown")
    message = result.get("message", "")
    claude_output = result.get("claude_output", "")
    commit_sha = result.get("commit_sha", "")
    duration = result.get("duration_seconds", 0)
    attempts = result.get("attempts", 1)
    game_url = result.get("game_url", "")
    actions_url = result.get("actions_url", "")

    attempts_str = ""
    if attempts > 1:
        attempts_str = f" / {attempts} 回試行"

    if status == "success":
        short_sha = commit_sha[:7] if commit_sha else "unknown"
        await ctx.send(
            f"✅ Unity 編集完了 ({duration}秒{attempts_str})\n"
            f"📝 Commit: `{short_sha}`\n"
            f"🚀 GitHub Actions でビルド中... (5〜10 分かかります)\n"
            f"📊 進捗: {actions_url}"
        )
        if claude_output:
            preview = claude_output[:1500]
            await ctx.send(f"🤖 Claude の応答:\n```\n{preview}\n```")

        if commit_sha:
            asyncio.create_task(monitor_ci(ctx, commit_sha, game_url))

    elif status == "no_changes":
        await ctx.send(
            f"⚠️ AI は何も変更しませんでした ({duration}秒{attempts_str})\n"
            "プロンプトを変えてもう一度試してください。\n"
            f"```\n{claude_output[:1000]}\n```"
        )

    elif status == "error":
        await ctx.send(
            f"❌ ビルド失敗{attempts_str}\n"
            f"理由: {message}"
        )
        if claude_output:
            preview = claude_output[:1000]
            await ctx.send(f"```\n{preview}\n```")

    else:
        await ctx.send(f"❓ 不明なステータス: {status}\nメッセージ: {message}")

async def build_worker():
    """キューからビルドリクエストを取り出して順次処理するワーカー"""
    print("Build worker started.")
    while True:
        try:
            request = await build_queue.get()
        except asyncio.CancelledError:
            print("Build worker cancelled.")
            break

        try:
            await process_build(request)
        except Exception as e:
            print(f"Build worker error: {type(e).__name__}: {e}")
            try:
                await request["ctx"].send(f"❌ ワーカーで予期しないエラー: `{type(e).__name__}: {e}`")
            except:
                pass
        finally:
            build_queue.task_done()

@bot.command(name="build")
async def build(ctx, *, task: str = None):
    """AI に Unity タスクを実行させる (キュー経由)"""
    user_id = ctx.author.id
    user_name = ctx.author.name

    # 認証チェック
    if user_id not in ALLOWED_USER_IDS:
        await ctx.send(
            f"❌ あなた (`{user_name}`) はこの bot を使う権限がありません。"
        )
        print(f"[REJECTED] Unauthorized user: {user_name} (ID: {user_id})")
        return

    if not task:
        await ctx.send("❌ タスクを指定してください\n例: `!build シーンに赤い Cube を追加して`")
        return

    if build_queue.full():
        await ctx.send(
            f"⚠️ キューが満杯です ({MAX_QUEUE_SIZE} 件)。\n"
            f"先行するビルドの完了を待ってから再度お試しください。"
        )
        return

    allowed, current, limit = check_and_consume_quota(user_id)
    if not allowed:
        await ctx.send(
            f"⚠️ 今日のビルド上限 ({limit} 回) に達しました。\n"
            f"明日また使ってください。\n"
            f"`!quota` で残り回数を確認できます。"
        )
        print(f"[REJECTED] Rate limit exceeded: {user_name} ({current}/{limit})")
        return

    request = {
        "ctx": ctx,
        "task": task,
        "user_id": user_id,
        "user_name": user_name,
        "current": current,
        "limit": limit,
        "enqueued_at": datetime.now(),
    }

    try:
        build_queue.put_nowait(request)
    except asyncio.QueueFull:
        refund_quota(user_id)
        await ctx.send("⚠️ キューが満杯になりました。再度お試しください。")
        return

    position = build_queue.qsize()
    if position == 1:
        await ctx.send(
            f"📥 キューに追加しました (順番: 1 番目、すぐに処理開始します)\n"
            f"タスク: {task}"
        )
    else:
        await ctx.send(
            f"📥 キューに追加しました (順番: {position} 番目、{position - 1} 件が先行中)\n"
            f"タスク: {task}\n"
            f"前のビルドが完了次第、自動的に開始されます。"
        )

bot.run(TOKEN)
```

プレースホルダー:

* `<user>/<repo>`: GitHub リポジトリ名
* `C:\Users\<user>\...`: Windows ユーザーディレクトリのパス

### bot.py を更新した後の反映方法

サービスとして動いているので、再起動で反映:

```
Restart-Service UnityAILabBot
Get-Service UnityAILabBot  # Running を確認
```

## まとめ

### 達成したこと

* Discord で `!build <タスク>` と打つだけで、AI が Unity を編集して itch.io にデプロイされる
* CI 完了は bot が自動で Discord に通知
* PC 再起動後は全部自動で復活 (Unity Editor 以外)
* API 過負荷は自動リトライで隠蔽
* AI の省略癖はプロンプト補強で抑制
* 認証 + レート制限でセキュリティと課金暴走対策
* キューイングで複数リクエストを順次処理

### 全体の時間感覚

| 工程 | 所要時間 |
| --- | --- |
| Discord からタスク送信 | 0 秒 |
| bot がキューに追加 | 即座 |
| AI が Unity を編集 (Unity MCP 経由) | 30〜60 秒 |
| git commit & push | 数秒 |
| CI が起動 (workflow がキューに入る) | 5〜20 秒 |
| Unity WebGL ビルド (Library キャッシュあり) | 5〜7 分 |
| Unity WebGL ビルド (Library キャッシュなし、初回) | 15〜17 分 |
| butler で itch.io にアップロード | 10〜30 秒 |
| bot が CI 完了を検知して Discord 通知 | 即座 |

平常時の合計: **約 6〜9 分** で `!build` から itch.io 反映まで完了。

### 学んだこと

**1. 文字エンコーディングは予想以上にハマる**

PowerShell の cp932 デフォルト、PowerShell の CLIXML 出力、マニフェスト JSON の BOM、Python subprocess のエンコーディング。1 日のうち何度もエンコーディング関連でハマりました。日本語を扱うなら最初から全部 UTF-8 で揃える決意が必要です。

**2. プロンプトの強度は 3 倍にしてちょうどいい**

AI に「省略するな」と 1 回書いても効きません。3 回くらい違う表現で書いて、さらに「失敗すると〇〇になる」という副作用まで説明する必要があります。これは CLAUDE.md だけでは不十分で、毎回のプロンプトに追記する形が確実です。

**3. Windows のサービス化はパスワード問題との戦い**

PIN ログインに慣れていると Microsoft アカウントの本来のパスワードを忘れがち。サービスアカウントには PIN が使えないので、本来のパスワードが必須。そもそもサービスをどのアカウントで動かすか (NetworkService / ユーザー / LocalSystem) の選択で挙動が変わります。

**4. Library キャッシュの威力**

Unity のビルドは Library キャッシュの有無で時間が 3 倍変わります。`actions/checkout@v4` の `clean: false` は必須。これを知らずに `clean: true` のままだと永遠に 17 分かかります。

**5. 失敗の殆どは設定ミスと環境差**

1 日のハマりどころの 80% は「エンコーディング」「権限」「パス」「既存ファイルの残骸」でした。ロジックのバグは意外と少なく、環境の問題が多い。サービス化とクロスユーザー運用が絡むと特に注意が必要。

### 次にやりたいこと

* **Unity Editor のスタートアップ登録**: Unity Hub のショートカットをスタートアップフォルダに置いて、ログイン時に自動起動させる
* **より高度なゲーム制作**: 単なる Cube 追加ではなく、ゲームロジックや UI まで AI に作らせる
* **CLAUDE.md の継続育成**: 失敗パターンを見つけるたびにルールを追加していく (Phase 3-E)
* **Unity MCP のツール拡張**: 今は標準の Unity MCP だけど、カスタムツールを追加して特定の操作を楽にできるかも

### 参考リンク

---

以上が、Discord に一言書くだけで Unity ゲームが itch.io に届くまでの完全な道のりです。半年後の自分でも、この記事を順番に追えば同じ環境を構築できるはずです。

お疲れ様でした。

---

## 時間のない方へ: 最短実装手順

「経緯はいいから、とりあえず動かしたい」という方向けの最短コースです。各ステップの詳細は記事本文の該当セクションへのリンクを貼っているので、必要に応じて参照してください。

### 事前準備: 全部揃える

以下を先にインストール・設定しておきます。

* **Windows 11** (この記事の前提)
* **Unity Hub + Unity 6000.4.1f1** (Unity 6.4 必須)
* **Git for Windows**
* **Python 3.14** (PATH 通す)
* **Node.js** (Claude Code 用)
* **Claude Code** (`npm install -g @anthropic-ai/claude-code` → `claude auth login`)
* **NSSM** (`winget install NSSM.NSSM`、Windows サービス化で使う)
* **GitHub アカウント + プライベートリポジトリ** (例: `kumi0708/unity-ai-lab`)
* **Discord Developer Portal で bot アプリ作成** (MESSAGE CONTENT INTENT を ON、bot をサーバーに招待)
* **itch.io アカウント + プロジェクト作成** (HTML kind、Draft でいい)
* **butler API キー** (<https://itch.io/user/settings/api-keys> で発行)
* **GitHub PAT (Fine-grained)** (Actions: Read-only、Contents: Read-only の権限)
* **自分の Discord ユーザー ID** (開発者モードを ON にして自分を右クリック → コピー)

### Step 1: Unity プロジェクトに Unity MCP を入れる

Unity Editor で **Window > Package Manager → Add package by name** で `com.unity.ai.assistant` をインストール。**Edit > Project Settings > AI > Unity MCP** で **Start** ボタンを押して Running にする。

[詳細: Phase 1: Unity MCP 接続](#phase-1-unity-mcp-%E6%8E%A5%E7%B6%9A)

### Step 2: relay バイナリを配置 + Claude Code に登録

`C:\Users\<user>\.unity\relay\relay_win.exe` を配置。管理者 PowerShell で:

```
cmd /c 'claude mcp add unity-mcp --scope user -- "C:\Users\<user>\.unity\relay\relay_win.exe" --mcp'
```

[詳細: Phase 1 の手順 3 と 4](#phase-1-unity-mcp-%E6%8E%A5%E7%B6%9A)

### Step 3: GitHub Actions セルフホストランナーをセットアップ

GitHub の `Settings > Actions > Runners > New self-hosted runner` の手順に従って `C:\actions-runner\` にランナーをインストール。**最初は手動起動 (`./run.cmd`) で OK** (サービス化は後でオプションで)。

[詳細: Phase 2 の手順 1](#phase-2-github-actions-%E3%81%AB%E3%82%88%E3%82%8B%E8%87%AA%E5%8B%95-webgl-%E3%83%93%E3%83%AB%E3%83%89%E3%81%A8-itchio-%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4)

### Step 4: Unity プロジェクトに `WebGLBuilder.cs` を追加

`Assets/Editor/WebGLBuilder.cs` を作成して、CLI からビルドできるようにする。

[詳細: Phase 2 の手順 2 (コード全文あり)](#phase-2-github-actions-%E3%81%AB%E3%82%88%E3%82%8B%E8%87%AA%E5%8B%95-webgl-%E3%83%93%E3%83%AB%E3%83%89%E3%81%A8-itchio-%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4)

### Step 5: `.gitignore` と `.gitattributes` を設定

Unity 用の標準 `.gitignore` + Git LFS の設定 + 今回必要な追加分:

```
.ai-build.lock
.last-build-result.json
.claude/
bot/logs/
bot/.env
```

[詳細: Phase 2 の手順 3 と 4](#phase-2-github-actions-%E3%81%AB%E3%82%88%E3%82%8B%E8%87%AA%E5%8B%95-webgl-%E3%83%93%E3%83%AB%E3%83%89%E3%81%A8-itchio-%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4)

### Step 6: itch.io の butler API キーを GitHub Secrets に登録

リポジトリの `Settings > Secrets and variables > Actions` で `BUTLER_API_KEY` を登録。

[詳細: Phase 2 の手順 5](#phase-2-github-actions-%E3%81%AB%E3%82%88%E3%82%8B%E8%87%AA%E5%8B%95-webgl-%E3%83%93%E3%83%AB%E3%83%89%E3%81%A8-itchio-%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4)

### Step 7: `.github/workflows/build.yml` を作成

記事本文に貼ってある build.yml の全文をそのままコピー。プレースホルダー `<itch-user>/<itch-project>` だけ自分のに置き換える。

[詳細: Phase 2 の手順 6 (build.yml 全文あり)](#phase-2-github-actions-%E3%81%AB%E3%82%88%E3%82%8B%E8%87%AA%E5%8B%95-webgl-%E3%83%93%E3%83%AB%E3%83%89%E3%81%A8-itchio-%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4)

ここまで来たら、適当な変更を `git push` して **CI が itch.io まで通ることを確認** (初回 15〜17 分、2 回目以降 5〜7 分)。

### Step 8: `scripts/run-ai-build.ps1` を作成

記事本文の Phase 3-D の **`run-ai-build.ps1` の完成版コード全文** をコピー。プレースホルダー `<user>` `<itch-user>/<project-name>` `<user>/<repo>` を自分のに置き換える。**保存は BOM 付き UTF-8** で。

[詳細: Phase 3-D-1 と 3-D-X (コード全文あり)](#phase-3-d-1-%E3%83%AA%E3%83%88%E3%83%A9%E3%82%A4%E6%A9%9F%E6%A7%8B)

### Step 9: Discord bot を作る

```
cd C:\Users\<user>\Documents\UnityProjects\unity-ai-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install discord.py python-dotenv aiohttp
```

`bot/.env` を作成 (中身は次の Step 10)。

`bot/bot.py` は記事本文の Phase 3-D-5 の **完成版コード全文** をコピー。プレースホルダー `<user>` `<user>/<repo>` を置き換える。

[詳細: Phase 3-D-5 の完成版 bot.py 全文](#phase-3-d-5-%E3%82%AD%E3%83%A5%E3%83%BC%E3%82%A4%E3%83%B3%E3%82%B0)

### Step 10: `.env` を埋める

`bot/.env`:

```
DISCORD_BOT_TOKEN=<Discord Developer Portal で発行>
GITHUB_TOKEN=<GitHub Fine-grained PAT>
GITHUB_REPO=<user>/<repo>
ALLOWED_USER_IDS=<あなたのDiscordユーザーID>
DAILY_BUILD_LIMIT=20
MAX_QUEUE_SIZE=10
```

[詳細: Phase 3-D-3 と 3-D-4 の `.env` 設定](#phase-3-d-3-ci-%E5%AE%8C%E4%BA%86%E9%80%9A%E7%9F%A5)

### Step 11: 動かしてみる

3 つのプロセスを立ち上げ:

1. **Unity Editor 起動 + Unity MCP Running 確認** (`Edit > Project Settings > AI > Unity MCP`)
2. **GitHub Actions ランナー起動**: `cd C:\actions-runner; .\run.cmd`
3. **Discord bot 起動**: `cd bot; python bot.py`

Discord で:

```
!ping       → pong が返れば bot OK
!quota      → 0/20 回 と表示されれば認証 OK
!build シーンに赤い Cube を位置 (0, 0, 0) に追加して、シーンを保存してください
```

期待される流れ:

1. bot が「📥 キューに追加 → 🔨 ビルド開始」と返事
2. 1 分前後で「✅ Unity 編集完了 + Claude の応答」
3. 5〜10 分後に bot から自動で「🎮 ビルド完成しました!」+ itch.io URL
4. URL を開くと WebGL でゲームが動く

これが動けば **最短実装は完了**です。

### オプション: PC 再起動後も自動で動くようにする (Windows サービス化)

3 つのプロセスを毎回手動で立ち上げるのが面倒な場合は、ランナーと bot を Windows サービス化します。Unity Editor は GUI なのでサービス化できません (手動起動のまま)。

[詳細: Phase 3-D-2 サービス化 (NSSM 設定込み)](#phase-3-d-2-%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E5%8C%96-%E3%83%A9%E3%83%B3%E3%83%8A%E3%83%BC%E3%81%A8-bot-%E3%82%92-windows-%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%81%AB)

### オプション: 別 PC に同じ環境を作る場合

別マシンで再構築する場合は、**Step 1〜11 を新しい PC でもう一度やる** ことになります。git clone でリポジトリは引き継げますが、以下は **手動で再設定**:

* `bot/.env` (Discord トークン、GitHub PAT、ユーザー ID)
* GitHub Actions ランナー登録 (新しい登録トークンが必要)
* NSSM のサービス登録
* Claude Code の認証
* Unity ライセンス (Unity Personal なら 2 台までログイン可能)

GitHub Secrets (`BUTLER_API_KEY`) と Discord bot アプリ、itch.io プロジェクトは PC を変えても引き継げます。

### つまずいたら

実装中にハマったら、記事本文の各 Phase の **「詰まった話」** セクションを参照してください。1 日で発生した主な詰まりポイントは以下:

### 完成までの所要時間の目安

慣れた人で **2〜3 時間**。詰まったら **半日〜1 日**。私は 1 日で全部やりました。

---

ここまで読んでいただきありがとうございました。半年後の自分が見ても、初めての方が見ても、同じ環境を再現できる記事になっていることを願っています。
