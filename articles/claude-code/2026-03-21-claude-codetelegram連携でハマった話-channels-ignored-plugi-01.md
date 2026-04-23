---
id: "2026-03-21-claude-codetelegram連携でハマった話-channels-ignored-plugi-01"
title: "【Claude Code】Telegram連携でハマった話　--channels ignored (plugin:telegram@claude-plugins-official)   Channels are not currently available"
url: "https://qiita.com/bbapexx/items/fae995598d467b2eeb19"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## はじめに

Claude CodeのChannels機能を使ってTelegramと連携したところ、

**最初の1回だけ動作し、2回目以降の起動で動かなくなる問題に遭遇しました。**

同様の問題で詰まる人が出てきそうなので、原因と対処方法をまとめます。

---

## 発生した現象

Claude Code起動時に以下のエラーが表示されます。

```
--channels ignored (plugin:telegram@claude-plugins-official)
Channels are not currently available
```

さらに、以下のような状態になります。

* Telegram botは正常に動作している
* メッセージも受信されている
* しかしClaudeが一切応答しない

👉 **完全に無反応になる**

---

## 状況整理

| 項目 | 状態 |
| --- | --- |
| Telegram bot | 正常 |
| plugin | 読み込み成功 |
| Channels | 無効扱い |
| Claudeの応答 | なし |

---

## 最初に疑ったこと（誤り）

以下のような典型的な原因を疑いましたが、いずれも該当しませんでした。

* Botトークンの設定ミス
* Webhook設定の不備
* pluginのインストール不良

👉 **いずれも原因ではありません**

---

## 原因（結論）

以下のGitHub Issueで報告されている通り、

👉 **Claude Code側の不具合です**  
色々試しましたがダメだったので修正待つしかなさそうです。

---
