---
id: "2026-03-20-claude-codevps-iphoneからssh接続-01"
title: "【Claude Code】VPS / iPhoneからSSH接続"
url: "https://note.com/yellowbirdjp/n/n6be15a209397"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-03-20"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

```
4GBメモリ
仮想3コア
NVMe50GB	host02-101	Claude Code	
```

シンVPS  
Claude Codeアプリイメージを利用する

メッセージあり！  
Claude Code has switched from npm to native installer. Run claude install or see ….

```
Claude Codeは、従来のnpmパッケージ形式からネイティブインストーラー（Bunベースの単一バイナリ）へと完全に移行しました。 

現在、npm経由のインストールは**非推奨（Deprecated）**となっており、公式はネイティブ版への移行を強く推奨しています。 

移行・インストールの手順
既存のnpm版を利用している場合、ターミナルで以下のコマンドを実行するだけでネイティブ版への移行が開始されます。 

移行コマンド: claude install

設定の継承: このコマンドを実行しても、過去の会話履歴、ログイン状態、設定（~/.claude/内のデータ）はそのまま保持されます。
```

iPhoneでは下記のSSHアプリを利用  
Termius - Modern SSH Clientアプリ - App Store - Apple
