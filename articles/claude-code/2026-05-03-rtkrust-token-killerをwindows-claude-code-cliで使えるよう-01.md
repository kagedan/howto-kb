---
id: "2026-05-03-rtkrust-token-killerをwindows-claude-code-cliで使えるよう-01"
title: "RTK（Rust Token Killer）をWindows + Claude Code CLIで使えるようにする手順"
url: "https://qiita.com/tanaka_taro_JP_KYUSYU/items/0565cc59862691982770"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "LLM", "qiita"]
date_published: "2026-05-03"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## RTKとは

  **RTK（Rust Token Killer）** は、Claude Code などのAIコーディングアシスタントのトークン消費を **60〜90%削減する CLI
  プロキシ**です。コマンドの出力を自動的に圧縮・フィルタリングし、LLMに渡してくれます。

  **実績値の例:**
  - `cargo test`（262テスト成功）: 4,823トークン → **11トークン（99.8%削減）**
  - 30分間のセッション全体: 150K トークン → **45K トークン（70%削減）**

  単一のRustバイナリで依存関係ゼロ、作業フローの変更もなし（透過的に動作）という特徴があります。

  - 公式リポジトリ: https://github.com/rtk-ai/rtk


  ## 動作環境

  - Windows 10 / 11（x64）
  - Claude Code CLI インストール済み
  - Git for Windows インストール済み（Bash環境として使用）


  ## 手順

  ### 1. バイナリのダウンロード

  [GitHub Releases](https://github.com/rtk-ai/rtk/releases) から最新バージョンの Windows 用 ZIP をダウンロードします。

  ファイル名: `rtk-x86_64-pc-windows-msvc.zip`

  または PowerShell で直接ダウンロードすることもできます（バージョンは適宜最新に変えてください）:

  ```powershell
  Invoke-WebRequest -Uri "https://github.com/rtk-ai/rtk/releases/download/v0.38.0/rtk-x86_64-pc-windows-msvc.zip" -OutFile
  "$env:TEMP\rtk.zip"
  ```

  ### 2. 解凍してインストール先へ配置

  ZIP を解凍すると `rtk.exe` が取り出せます。これをPATHの通ったフォルダに配置します。

  おすすめのインストール先: `C:\Users\<ユーザー名>\.local\bin\`

  フォルダが存在しない場合は作成してください:

  ```powershell
  New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.local\bin"
  ```

  ZIPを解凍して `rtk.exe` をコピー:

  ```powershell
  Expand-Archive -Path "$env:TEMP\rtk.zip" -DestinationPath "$env:TEMP\rtk-extracted" -Force
  Copy-Item "$env:TEMP\rtk-extracted\rtk.exe" "$env:USERPROFILE\.local\bin\rtk.exe"
  ```

  ### 3. PATHへの追加

  Git Bash（Claude Code CLIが使うBash環境）のPATHに追加します。

  `C:\Users\<ユーザー名>\.bash_profile` をテキストエディタで開き、末尾に以下を追加:

  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

  ファイルが存在しない場合は新規作成してください。

:::note info
Claude Code CLI は Git for Windows の Bash を使用しているため、`.bash_profile` への追記が有効です。Windows 標準のコマンドプロンプト / PowerShell の PATH 設定（システム環境変数）とは別物です。
:::

  ### 4. 動作確認

  Git Bash を新規に開いて確認:

  ```bash
  which rtk
  # => /c/Users/<ユーザー名>/.local/bin/rtk

  rtk --version
  # => rtk 0.38.0
  ```

  `rtk` と表示されれば OK です。

:::note warn
`cargo install rtk` で別途インストールした場合、**別パッケージ（Rust Type Kit）** が入ってしまう可能性があります。`rtk --version` で `rtk
X.Y.Z` と表示されることを必ず確認してください。
:::

  ### 5. Claude Code CLI への統合

  以下のコマンドでグローバル設定を自動セットアップします:

  ```bash
  rtk init -g --auto-patch
  ```

  実行すると以下が自動的に行われます:

  - `~/.claude/settings.json` に Bash フックを追加
  - `~/.claude/RTK.md` を生成（RTKの使い方説明ファイル）
  - `~/.claude/CLAUDE.md` に `@RTK.md` の参照を追記

  ### 6. settings.json の確認

  `C:\Users\<ユーザー名>\.claude\settings.json` を開き、以下の `hooks` セクションが追加されていることを確認します:

  ```json
  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Bash",
          "hooks": [
            {
              "type": "command",
              "command": "rtk hook claude"
            }
          ]
        }
      ]
    }
  }
  ```

  このフックにより、Claude Code が Bash ツールを呼び出すたびに `rtk hook claude` が実行され、コマンドの出力が自動的に圧縮されます。

  ### 7. Claude Code CLI を再起動

  設定を反映するために Claude Code CLI を再起動します。


  ## 動作確認

  再起動後、以下のコマンドでトークン削減統計を確認できます:

  ```bash
  rtk gain
  ```

  ```bash
  rtk gain --history    # コマンド別の削減履歴
  rtk discover          # 過去の Claude Code 履歴から削減機会を分析
  ```


  ## しくみ

  RTK は Claude Code の `PreToolUse` フックを使って動作します。

  ```
  Claude Code が Bash コマンドを実行
    ↓
  PreToolUse フック: rtk hook claude が起動
    ↓
  RTK がコマンド出力をフィルタリング・圧縮
    ↓
  圧縮済みの出力のみ Claude のコンテキストに渡る
  ```

  ユーザーには圧縮前の出力が見えますが、Claude には圧縮後の出力が渡されるため、トークンを大幅に削減できます。


  ## まとめ

  | ステップ | 内容 |
  |---|---|
  | ① ダウンロード | GitHub Releases から `rtk-x86_64-pc-windows-msvc.zip` を取得 |
  | ② 配置 | `~/.local/bin/rtk.exe` に配置 |
  | ③ PATH追加 | `~/.bash_profile` に `export PATH="$HOME/.local/bin:$PATH"` を追記 |
  | ④ 統合 | `rtk init -g --auto-patch` を実行 |
  | ⑤ 再起動 | Claude Code CLI を再起動 |

  Rustプロジェクト・テスト件数が多いプロジェクト・Git操作が頻繁なプロジェクトほど効果が大きいです。ぜひ試してみてください。
