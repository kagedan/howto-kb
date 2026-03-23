---
id: "2026-03-19-redmineのネイティブoauth2でaiエージェントに安全にredmineを操作させる-01"
title: "RedmineのネイティブOAuth2でAIエージェントに安全にRedmineを操作させる"
url: "https://qiita.com/ssc-ksaitou/items/b7a4d51ed78fa6e45521"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-03-19"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

<!-- タイトル: RedmineのネイティブOAuth2でAIエージェントに安全にRedmineを操作させる -->

## TL; DR

Redmine 6.1 のネイティブ OAuth2 + ゲートウェイで client_secret を集約し、CLI ツールがトークンを隠蔽することで、API キー不要・スコープ制限付き・AI コンテキストへのトークン漏洩なしで Redmine を操作させる構成について述べた記事です。

## はじめに

チームで Redmine と Claude Code を併用していると、**チケットの内容をブラウザからコピーして AI に貼り付け、作業結果をまたコピーしてチケットに書き戻す場面によく遭遇します。** 自分もチームメンバーもこの手作業を繰り返していました。

AI にチケットを直接読み書きさせれば済む話ですが、既存の MCP サーバや CLI ツールは利用者の全操作権限を永続的に付与する Redmine API キーを要求するため、**権限が広すぎる・漏洩すると大変（全員にAPIキーを発行させたくない）** という問題があります。

そん
