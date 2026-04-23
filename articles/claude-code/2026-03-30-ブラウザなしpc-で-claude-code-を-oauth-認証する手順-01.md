---
id: "2026-03-30-ブラウザなしpc-で-claude-code-を-oauth-認証する手順-01"
title: "ブラウザなしPC で Claude Code を OAuth 認証する手順"
url: "https://zenn.dev/akinobukato/articles/5bd6db5d657f20"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "VSCode", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

# ブラウザなしPC で Claude Code を OAuth 認証する手順

ブラウザが使えない PC でも、スマホや別 PC を使って Claude Code の OAuth 認証を通す方法。

## 前提

* 認証したい PC にはブラウザがない（または使えない）
* スマホ or 別 PC でブラウザ操作ができる
* API キーは使えず、OAuth 認証が必要

---

## 手順

### 1. 認証を開始する

ブラウザなし PC のターミナルで以下を実行：

ログイン URL がターミナルに表示される。`c` キーを押すと URL をクリップボードにコピーできる。

もしくはvscodeでclaudeログインを試す（以下のClaude.ai Subscriptionを選ぶ）  
![](https://static.zenn.studio/user-upload/3e2fcefe1104-20260328.png)

ここに表示されるURLをコピーしておく  
![](https://static.zenn.studio/user-upload/a1a8f6a1bc33-20260331.png)

---

### 2. URL をスマホ or 別 PC に転送する

以下のいずれかの方法で URL を別デバイスに送る。

**QR コード変換（おすすめ）**

`qrencode` が入っていれば、ターミナル上に QR コードを表示してスマホのカメラで読み取れる：

```
qrencode -t ansiutf8 "コピーした URL"
```

**その他の方法**

* ローカルネットワーク経由でテキスト共有
* 手打ち（URL が短ければ）

---

### 3. 別デバイスのブラウザで URL を開いて認証する

1. スマホ or 別 PC のブラウザで URL を開く
2. Claude アカウントでログイン
3. **「Claude Code を承認しますか？」** → 許可  
   ![](https://static.zenn.studio/user-upload/7a4cf778c324-20260331.png)

---

### 4. 表示された認証コードを本体 PC に入力する

認証が完了すると、ブラウザ側に\*\*認証コード（トークン）\*\*が表示される。  
![](https://static.zenn.studio/user-upload/4b7da2529dc4-20260331.png)

そのコードをブラウザなし PC のターミナルに手打ちで入力すると認証が完了する。（以下の緑色のところに実際には入力してます）  
![](https://static.zenn.studio/user-upload/ba0715ddc371-20260331.png)

---

## 補足

* CLI と VSCode 拡張機能は認証情報を共有しているため、どちらか一方でログアウトするともう一方も使えなくなる
* ログアウト・再ログインをしても、会話履歴やメモリ（`~/.claude/`）はローカルに残るため消えない
* `ANTHROPIC_API_KEY` 環境変数が設定されていると API キー認証が優先されるので注意
