---
id: "2026-03-17-cloudflare-zero-trustでclaude-in-chromeが繋がらない問題の原因と-01"
title: "Cloudflare Zero TrustでClaude in Chromeが繋がらない問題の原因と解決策"
url: "https://zenn.dev/hiroe_orz17/articles/a586cf0d586ef1"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

Claude Desktop（MCP）とChromeの拡張機能「Claude in Chrome」を組み合わせて使っていたところ、Cloudflare Zero Trust（WARP）を有効にすると接続できなくなるという問題に遭遇しました。

---

## 環境

* macOS
* Claude Desktop（MCP）
* Claude in Chrome（Chrome拡張機能）
* Cloudflare Zero Trust（WARP クライアント）

---

## 最初の仮説：ローカルアドレスの問題

Claude DesktopとChrome拡張はlocalhost経由でWebSocket通信しているのでは？と考え、Cloudflare WARPのSplit TunnelにローカルIPを除外設定しようとしました。

### Split Tunnelの場所が変わっていた

まず困ったのが、Cloudflare One（Zero Trust）のダッシュボードUIが大幅にリニューアルされており、Split Tunnelの設定場所が全く見つからなかったことです。

**現行UIでのSplit Tunnelの場所：**

```
Team & Resources
  └── Devices
        └── Device profiles タブ
              └── General profiles
                    └── [プロファイル名をクリック]
                          → Edit
                            └── Split Tunnels → Manage
```

以前は左サイドバーに直接あったものが、デバイスプロファイルの中に移動していました。ダッシュボードの検索ボックスで「Split Tunnel」と検索すると「Devices」という項目がヒットするので、そこから辿るのが早いです。

### Split Tunnelに127.0.0.1を追加してみたが…

両プロファイル（Komatsuelec ProfileとDefault）に以下を追加しました：

| Type | Value | Description |
| --- | --- | --- |
| address | `127.0.0.1/8` | localhost IPv4 |
| address | `::1/128` | localhost IPv6 |

しかしWARPを有効にしても、やはりChrome拡張と接続できません。

---

## 原因調査：実際の通信経路を確認

### lsofでポートを確認

```
lsof -i -P | grep -i claude | grep LISTEN
lsof -i -P | grep LISTEN | grep -E "127|::1|0\.0\.0\.0"
```

**結果：何も出力されない。**

Claude DesktopはローカルポートでLISTENしていませんでした。これは`127.0.0.1`の除外設定が意味をなさないことを示しています。

### Claude Desktopのログを確認

```
tail -100 ~/Library/Logs/Claude/main.log | grep -i "chrome\|websocket\|ws\|connect\|error\|fail"
```

**WARP有効時のログ：**

```
[Claude in Chrome] Connecting to bridge: wss://bridge.claudeusercontent.com/chrome/917e2c98-...
[error] [Claude in Chrome] Bridge WebSocket error after 1920ms: self signed certificate in certificate chain
[Claude in Chrome] Bridge connection closed (code: 1006, duration: 0ms)
[Claude in Chrome] Bridge reconnecting in 3000ms (attempt 2)
[Claude in Chrome] Connecting to bridge: wss://bridge.claudeusercontent.com/chrome/917e2c98-...
[error] [Claude in Chrome] Bridge WebSocket error after 204ms: self signed certificate in certificate chain
```

**原因判明。**

---

## 真の原因：TLSインスペクションによる証明書エラー

Claude in Chromeは`127.0.0.1`ではなく、**`wss://bridge.claudeusercontent.com`という外部サーバー**へのWebSocket接続を使って通信していました。

Cloudflare Zero TrustのWARPはデフォルトでHTTPS（TLS）インスペクションを行います。このとき、WARPは通信に自己署名証明書を差し込みます。Claude Desktopはこの証明書を信頼できないため、接続を拒否していたのです。

```
Claude Desktop
    ↓ wss://bridge.claudeusercontent.com への接続
Cloudflare WARP（TLSインスペクション）
    ↓ 自己署名証明書を差し込む
bridge.claudeusercontent.com
    ↑ Claude Desktopが「self signed certificate」エラーで接続拒否
```

---

## 解決策

### Split TunnelにホストのDomainを追加

プロファイルのSplit Tunnel除外リストに以下を追加します：

| Type | Value |
| --- | --- |
| host | `bridge.claudeusercontent.com` |

これにより、`bridge.claudeusercontent.com`へのトラフィックはWARPのTLSインスペクションをバイパスし、直接接続されるようになります。

### 設定手順

1. `https://one.dash.cloudflare.com/` を開く
2. **Team & Resources → Devices → Device profiles**
3. 各プロファイル（Default、カスタムプロファイル両方）の **Edit → Split Tunnels → Manage**
4. Selector: **Domain**、Value: `bridge.claudeusercontent.com` を追加して **Save destination**

---

## まとめ

| 項目 | 内容 |
| --- | --- |
| 誤った仮説 | Claude in Chromeはlocalhostで通信している |
| 実際の通信先 | `wss://bridge.claudeusercontent.com`（外部サーバー） |
| 通信方式 | Native Messaging（stdio）+ WebSocket Bridge |
| 問題の原因 | Cloudflare WARPのTLSインスペクションによる自己署名証明書エラー |
| 解決策 | `bridge.claudeusercontent.com`をSplit Tunnel除外リストに追加 |

Cloudflare Zero TrustとClaude in Chromeを併用している方は、Split Tunnelへの追加すると解決するかもです。

---

## 余談：Cloudflare One UIの変更について

今回の調査でCloudflare OneのUIが大幅に変更されており、Split Tunnelの場所を探すのに時間がかかりました。設定メニューの場所がこれだけ変わると困りますね…。

現行UIのSplit Tunnel設定は **Team & Resources → Devices → Device profiles** の中に移動してました。
