---
id: "2026-07-01-mutagenでwindowsからwslにファイル同期-01"
title: "MutagenでWindowsからWSLにファイル同期"
url: "https://zenn.dev/jsaito99/articles/c9fd2e25a27fdc"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

## 同期の動機

CLI系のAIエージェントでObsidianのファイルを読み込んで色々やらせたい。  
AI的にはVaultはWSL側に置きたいけど、Obsidianアプリ的にはWindows側に置きたい。  
解決策として、Mutagenを導入する。

## Mutagenの概要

Mutagenは、異なるファイルシステム間（WindowsとWSL、あるいはローカルとリモートサーバーなど）で、「ネイティブ速度での読み書き」と「リアルタイムの双方向同期」を両立させるツール。

## Mutagenの導入

```
# フォルダ構成例
C:\Tools\mutagen ← Pathに追加 
├─ mutagen.exe 
└─ mutagen-agents.tar.gz
```

## 同期セッションの作成

PowerShellを開き、パスを書き換えて実行。  
自分のディストリビューション（Ubuntu等）は`wsl -l -v`で確認。

```
# 例：WindowsのVaultとWSLのホーム配下を同期
mutagen sync create --name=obsidian-sync --ignore='/.git'  "C:\Users\あなたのユーザー名\Documents\ObsidianVault" "\\wsl.localhost\ディストリビューション名\home\あなたのユーザー名\vault"

# 動いている同期セッションの確認
mutagen sync list
```

指定したパスにフォルダが同期されていることが確認できる。

**.gitの除外**  
.gitフォルダも同期していたが、WSLとWindows両側からgit操作しているとコンフリクトが起きたり不具合が多かった。  
.gitは同期から外し、git操作はどちらか一方に絞るのが良さそう。

## Mutagenデーモンの開始

PCの起動後、何かしらの方法で`mutagen`デーモンを動かし始める必要がある。  
今回は.bashrcにコマンド実行を盛り込む。

```
echo 'cmd.exe /c "mutagen sync list" > /dev/null 2>&1' >> ~/.bashrc
```

これでターミナルを開いたときにはmutagenの同期も動くようになった。
