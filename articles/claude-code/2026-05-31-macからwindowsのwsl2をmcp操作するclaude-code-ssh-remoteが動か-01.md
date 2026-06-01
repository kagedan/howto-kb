---
id: "2026-05-31-macからwindowsのwsl2をmcp操作するclaude-code-ssh-remoteが動か-01"
title: "MacからWindowsのWSL2をMCP操作する——Claude Code SSH Remoteが動かない時の別アプローチ"
url: "https://zenn.dev/keiichi_okamoto/articles/xx_260531_mac-win-mcp"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "cowork", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

Claude Code Desktopにはリモートマシンへの接続機能が組み込まれているが、macOS → Windows/WSL2の構成では[動作しないバグが報告されている](https://github.com/anthropics/claude-code/issues/43852)。この記事では、その代替として`claude_desktop_config.json`にSSHを直接書く方法を紹介する。同一PC内ではなく、**MacとWindowsが別マシンの構成**で実際に動作している。

---

[前回の記事](https://zenn.dev/keiichi_okamoto/articles/xx_01_web_on_window)でWindows WSL2にサーバー環境を構築した。その流れで、[こちらの記事](https://zenn.dev/kariya_mitsuru/articles/5ed08d1afe658b)を参考にWindowsのClaude DesktopからWSL2内のClaude CodeをMCPサーバーとして接続することもやってみた。

それに飽き足らず、今度はMacのClaude DesktopからWindowsのWSL2を操作できるようにした。

結果として、MacのCoworkから日本語で指示するだけでWSL2内のファイル操作やDockerの操作ができるようになった。Windows Appを使ってWSL2に入る機会がかなり減り、副産物としてMacのターミナルからSSHでWSL2に直接入れるようにもなった。

## やったこと

構成はシンプルだ。MacのClaude DesktopがSSH経由でWindowsのOpenSSH Serverに接続し、そのままWSL2内のClaude Codeを起動する。

![全体構成](https://static.zenn.studio/user-upload/deployed-images/b0fd48cefbb4d5b58e5b95dd.png?sha=0cd179a3e872ae9dc7b2d3c497d5f8b4a3d80d1d)

MacのCoworkから「WSLでDockerを再起動して」と指示すると、SSH越しにWSL2内のClaude Codeが動き、ファイル操作やDockerの操作を実行してくれる。

ここで一つ重要な気づきがある。この構成でWSL2内を操作する時、**Claude CodeはAIとして判断しているのではなくシェルとして動いている**。

![指揮者モデル](https://static.zenn.studio/user-upload/deployed-images/d9ff8be764d013e48d2672fb.png?sha=a6b30059398ebedae3c3e78aed71edcbd80bd5bf)

指示を分解して、結果を受け取って判断し、次の操作を決め、最終的に報告しているのはCowork側のClaudeだけだ。各MCP呼び出しで起動されるClaude Codeはコマンドを実行して結果を返すだけで、お互いを知らないし文脈も持っていない。

このモデルをAIに話したところ、「MCPを解釈するシェル（mcpsh）」という概念が出てきた。軽量なMCPサーバーがシェルとして動き、上位のAIが指揮者として判断する構成で、今回のClaude Code（mcp serve）はその先駆け的な形と言える。「こういう仕組みが成立するとしたらどうなる？」という問いかけから生まれたアイデアだが、実際にこの構成を動かしてみると、そのモデルがそのまま当てはまっていた。このモデルを理解しておくと、後述するパターンA/Bの選択や、CLAUDE.mdによる2層制御の意味が見えやすくなる。

---

## なぜSSHが必要か

Claude DesktopはSSH接続時にパスワードを入力できない。対話的なプロンプトに応答する仕組みがないためだ。

しかも既存の`id_rsa`にパスフレーズが設定されている場合も同様に詰まる。Claude Desktopがパスフレーズを入力できないため接続に失敗する。

解決策は**Claude Desktop専用のパスフレーズなし鍵を新規作成すること**だ。既存の鍵はそのまま使い続けられる。

```
# パスフレーズなしの専用鍵を作成
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_wsl -N ""
```

---

## セットアップの手順

### 1. WindowsにOpenSSH Serverを入れる

PowerShellを管理者権限で開いて状態を確認する。

```
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
```

`State: NotPresent`なら入れる。

```
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

`Automatic`にしておくことで、Windowsにログインしていない状態でもSSH接続を受け付けられる。

ファイアウォールはOpenSSH Serverのインストール時に自動で許可ルールが追加される。確認だけしておく。

```
Get-NetFirewallRule -Name *ssh*
# Enabled: True / Action: Allow になっていればOK
```

### 2. MacからSSH接続を確認する

WindowsのIPアドレスを確認して（`172.x.x.x`はWSL2の内部ネットワークなので使わない）、Macのターミナルから繋がるか試す。

```
ssh okamoto@192.168.0.47
# Windowsのパスワードを入力してWSL2に入れればOK
```

WindowsのOpenSSH Serverに接続すると、そのままWSL2（Ubuntu）に入る設定になっていた。WindowsのIPに繋いだだけでWSL2に入れる。

### 3. 鍵認証を設定する

Claude Desktop専用の鍵を作ってWSL2に登録する。

```
# 専用鍵を作成
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_wsl -N ""

# WSL2に公開鍵を登録
ssh-copy-id -i ~/.ssh/id_rsa_wsl.pub okamoto@192.168.0.47

# 鍵認証で繋がるか確認
ssh -i ~/.ssh/id_rsa_wsl okamoto@192.168.0.47 "echo 成功"
```

### 4. claude mcp serve の動作を確認する

SSH経由でClaude Codeが起動できるか確認しておく。フルパスを使うのがポイントで、SSH経由での実行はログインシェルを経由しないため`PATH`が通っていない場合がある。

```
# パスを確認
ssh okamoto@192.168.0.47 "which claude"
# /home/okamoto/.local/bin/claude

# mcp serve が起動するか確認（何も出力されず待機状態になるのが正常）
ssh -i ~/.ssh/id_rsa_wsl okamoto@192.168.0.47 "/home/okamoto/.local/bin/claude mcp serve"
# Ctrl+C で抜ける
```

### 5. MacのClaude Desktop設定ファイルを編集する

`~/Library/Application Support/Claude/claude_desktop_config.json`に`mcpServers`を追加する。

```
{
  "mcpServers": {
    "wsl_claude_code": {
      "command": "ssh",
      "args": [
        "-i", "/Users/okamoto/.ssh/id_rsa_wsl",
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        "okamoto@192.168.0.47",
        "/home/okamoto/.local/bin/claude",
        "mcp",
        "serve"
      ]
    }
  }
}
```

各オプションの意味はこうだ。`-i`で専用鍵を明示的に指定し、`StrictHostKeyChecking=no`で初回接続時のホスト確認プロンプトをスキップ、`BatchMode=yes`でパスワード入力を求めない対話なしモードにする。

`~/.ssh/config`を書いて設定をまとめたくなるが、Claude DesktopはアプリとしてSSHを呼び出すため`~/.ssh/config`を読まない場合がある。`args`にすべてのオプションを明示的に書いておく方が確実だ。

Claude Desktopを再起動して、設定画面（開発者 → ローカルMCPサーバー）で`wsl_claude_code`が`running`になっていれば完了。

---

## パターンA vs パターンB：どちらで起動するか

MCP接続にはWSL2のどのディレクトリで起動するかで2つの選択肢がある。

![パターンAとパターンBの比較](https://static.zenn.studio/user-upload/deployed-images/3121945dc5ef5445b0aeff3b.png?sha=a4de7c69b7f6dbcf4cbe370774cebef678e605bb)

**パターンA（今回の構成）** は`$HOME`で起動するシンプルな1エントリー。プロジェクトが増えても設定変更が不要で、複数プロジェクトをまたいだ作業もできる。ただし読み込まれるCLAUDE.mdは`$HOME/CLAUDE.md`のみで、プロジェクト固有のルールは反映されない。

**パターンB** はプロジェクトごとに個別MCPを登録する。

```
"wsl_webapi": {
  "args": [
    "-i", "/Users/okamoto/.ssh/id_rsa_wsl",
    "-o", "StrictHostKeyChecking=no",
    "-o", "BatchMode=yes",
    "okamoto@192.168.0.47",
    "bash", "-c",
    "cd /home/okamoto/Develop/Git/WebApiLab && /home/okamoto/.local/bin/claude mcp serve"
  ]
}
```

各プロジェクトのCLAUDE.mdが自動で読み込まれ、アクセス範囲も限定できる。プロジェクトが増えるたびに設定ファイルの編集が必要になるのが難点だ。

実験段階はパターンAで始めて、プロジェクトが増えてCLAUDE.mdを活用したくなったタイミングでパターンBに移行するのが現実的だと思っている。

曖昧な指示でどのプロジェクトに対して作業するか誤判断しないように、`$HOME/CLAUDE.md`に一行書いておくと確認を求めるようになる。

```
## MCP操作の確認
mcpでの作業と思われる場合には、どのmcpに対してリクエストするか必ず確認すること。
```

---

## 副産物：MacのターミナルからSSHで直接WSL2に入れる

MCP接続のためにOpenSSH Serverを設定した結果として、MacのターミナルからWSL2に直接SSHログインできるようになった。

```
ssh okamoto@192.168.0.47
# パスワードなしでWSL2（Ubuntu）に入れる
```

Windows App（リモートデスクトップ）経由でWSLを操作する場合と比べて、キーボードの挙動がMacのターミナルそのままで使え、日本語入力の切り替えもMac側のまま使えて、画面遅延もない。

MCP経由（Cowork）とSSH直接ログインの使い分けはこんな感じになっている。複雑なコマンドを自分で打ちたい時やインタラクティブに操作したい時はSSH、Coworkから日本語で任せたい時や Mac側の作業と組み合わせたい時はMCP経由、という感じだ。

---

## まとめ

MacのClaude DesktopからWindowsのWSL2をMCP経由で操作できるようになった。WindowsのClaude Desktopから操作する構成に続けて、そのままMac側からも繋げてしまった形だ。

セットアップで一番ハマるのは鍵認証の部分で、Claude Desktopはパスワードもパスフレーズも入力できないため、専用鍵を作って`args`に明示的に指定することが必要だった。それさえ分かってしまえばあとは設定ファイルに数行書くだけだ。

Windows Appを開く機会が減り、MacのCoworkから日本語で指示してWSL2の作業が完結するようになった。副産物のSSH直接アクセスも思った以上に便利で、リモートデスクトップを使う場面がさらに減った。

---

「10年Macに引きこもったiOSエンジニア」がWindowsを触り始めた——という話のはずだったが、結局MacからWindowsを操作できるようになってしまった。Macから一歩も出ていない。引きこもりは深化している。

---

## 環境

* **Mac**: macOS / Claude Desktop
* **Windows**: Windows 11 / OpenSSH Server
* **WSL2**: Ubuntu 24.04 LTS
* **Claude Code**: `/home/okamoto/.local/bin/claude`
* **SSH鍵**: `~/.ssh/id_rsa_wsl`（パスフレーズなし・Claude Desktop専用）
