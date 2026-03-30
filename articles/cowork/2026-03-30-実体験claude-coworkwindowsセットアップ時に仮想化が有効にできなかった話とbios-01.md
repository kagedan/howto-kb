---
id: "2026-03-30-実体験claude-coworkwindowsセットアップ時に仮想化が有効にできなかった話とbios-01"
title: "【実体験】Claude Cowork（Windows）セットアップ時に仮想化が有効にできなかった話とBIOS設定での解決方法"
url: "https://qiita.com/kan2530/items/fbac7254b3375a9fe690"
source: "qiita"
category: "cowork"
tags: ["cowork", "qiita"]
date_published: "2026-03-30"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

## はじめに

Claude Coworkは2026年2月よりWindowsでも利用可能になり、試してみた方も多いのではないでしょうか。

私がセットアップを進めたところ、**仮想化が有効にならず**Coworkが起動できないという壁に当たりました。
本記事では仮想化を有効にするため実際に行った手順と方法を共有します。

---

## 環境

| 項目 | 詳細 |
|---|---|
| PC | Minisforum 790 Pro（ミニPC） |
| OS | Windows 11 |
| 対象アプリ | Claude Desktop（Cowork機能） |
| Claudeプラン | Pro / Max / Team / Enterprise いずれか（有料プラン必須） |

:::note info
**Claude Coworkとは？**
Claude Desktopアプリ内の機能で、ローカルファイルへのアクセスや複数ステップのタスクを自律実行できます。
実行には**仮想マシン（VM）環境**が使われるため、PCの仮想化機能が有効になっている必要があります。
:::
