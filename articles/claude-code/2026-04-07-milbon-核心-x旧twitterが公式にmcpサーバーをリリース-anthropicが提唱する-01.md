---
id: "2026-04-07-milbon-核心-x旧twitterが公式にmcpサーバーをリリース-anthropicが提唱する-01"
title: "@milbon_: ■ 核心 X（旧Twitter）が公式にMCPサーバーをリリース。 Anthropicが提唱する「Model C"
url: "https://x.com/milbon_/status/2041378664039006276"
source: "x"
category: "claude-code"
tags: ["x"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-x"
query: ""
---

■ 核心  
X（旧Twitter）が公式にMCPサーバーをリリース。  
Anthropicが提唱する「Model Context Protocol」を使って、Claude CodeなどのAIがXのAPIを安全に直接操作できるようになった。これまで複雑だったAPI連携が、ローカルサーバー1つで劇的にシンプルに。

■ 主要機能  
・searchPostsRecent：最新投稿を検索  
・createPosts：投稿を即作成  
・getUsersMe：自分のアカウント情報取得  
・likePost / repostPost：いいね・リポスト  
（.envでツールを制限可能）

■ 利用方法  
1. X Developerでアプリ作成（API Key取得）  
2. git clone https://t.co/vPmprDhyOw → .envにキーを設定  
3. python https://t.co/Qlf6Drs5I5でサーバー起動（初回OAuth認証）  
4. 別ターミナルで claude mcp add --transport http xmcp http://127.0.0.1:8000/mcp  

→ 完了！あとはClaude Codeに「AIのバズ投稿調べて」「この内容で投稿して」と話しかけるだけ。

■ 背景  
今までのX運用は「ブラウザ開く→投稿→反応見る→分析」と全部バラバラだった。  
X公式がMCPを出したことで、Claude Codeとの相性が爆発的に向上。  
ターミナル1つでX運用が「作業」から「指示だけ」になる時代が本格的に到来した。
