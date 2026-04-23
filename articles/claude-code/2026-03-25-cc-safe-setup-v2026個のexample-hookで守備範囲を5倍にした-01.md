---
id: "2026-03-25-cc-safe-setup-v2026個のexample-hookで守備範囲を5倍にした-01"
title: "cc-safe-setup v2.0——26個のexample hookで守備範囲を5倍にした"
url: "https://qiita.com/yurukusa/items/ce9a7c0490a59b6cfc37"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

Claude Codeの安全装置、v2.0にした。

> **追記（2026-03-31）**: この記事はv2.0時点の記録です。現在は[637 example hooks / 13,955テスト](https://github.com/yurukusa/cc-safe-setup)に拡大しています。最新の導入方法は変わっていません: `npx cc-safe-setup`

## Claude Codeは便利だけど、事故も起きる

Claude Codeを使ったことがあるだろうか。ターミナルでAIと対話しながらコードを書くツールだ。

便利だ。でも、AIにターミナルの操作を許可するということは、AIがファイル全削除コマンドを実行できるということでもある。

実際に起きた事故:

* **C:\Users\全体が削除された**（[#36339](https://github.com/anthropics/claude-code/issues/36339)）。Windowsの「ジャンクション」（フォルダのショートカットのようなもの）を経由して、削除が予想外の場所にまで及んだ
* **全ソースコードが消された**（[#37331](https://github.com/anthropics/claude-code/issues/37331)）。PowerShellの`Remove-Item -Recurse -Force *`で
* **本番データベースがリセットされた**（[#34729](https://github.com/anthropics/claude-code/issues/34729)）。`prisma migrate reset`でテストのつもりが本番に

:::details 初心者向け: なぜAIがこんなことをするのか  
AIは「目的を達成するために最短経路を選ぶ」。「不要なファイルを掃除して」と頼んだら、一番確実な方法としてファイル全削除を選ぶことがある。人間なら「いやいや、それは危険すぎるだろ」と止まるが、AIには「危険」の感覚がない。  
:::

## cc-safe-setupはワンコマンドで安全装置を入れる

これだけ。10秒で8つの安全hookがインストールされる。

:::details 初心者向け: hookって何？  
「hook」は「フック」と読む。釣り針のフックと同じ語源。

Claude Codeが何かコマンドを実行しようとする時、**実行する前に**hookが割り込んで内容をチェックする。危険なコマンドだったらブロックする。空港のセキュリティチェックのようなもの。

搭乗口（コマンド実行）の前にゲート（hook）がある。武器（危険なコマンド）を持っていたら止められる。  
:::

## 8つの基本hook——何を防ぐか

| hook | 防ぐもの | 身近な例え |
| --- | --- | --- |
| **Destructive Guard** | ファイル全削除, `git reset --hard`等 | 「全部消す」ボタンにカバーを付ける |
| **Branch Guard** | mainブランチへの直接push | 本番サーバーの鍵を金庫に入れる |
| **Secret Guard** | `.env`ファイルのgit add | パスワードメモを共有フォルダに入れない |
| **Syntax Check** | 編集後の構文エラー | 手紙を出す前に読み返す |
| **Context Monitor** | コンテキスト窓の溢れ | ガソリンメーターの警告灯 |
| **Comment Stripper** | Bashコメントの誤検知 | 雑音を除去してから判定する |
| **cd+git Auto-Approver** | 安全コマンドの許可プロンプト | 「歩いていいですか？」をいちいち聞かない |
| **API Error Alert** | セッションの静かな死 | 心拍モニターのアラーム |

## 637個のexample hook——なぜこんなに増えたか

最初は8個だけだった。1ヶ月GitHub Issueを見続けて、**実際に起きた事故**からhookを作り続けた結果、637個になった。

```
# 個別にインストールできる
npx cc-safe-setup --install-example block-database-wipe

# 一覧を見る
npx cc-safe-setup --examples

# 最大安全モード（全推奨hookを一括インストール）
npx cc-safe-setup --shield
```

## カテゴリ別の代表例

### 安全ガード（データを守る）

| hook | 防ぐもの | 元になった事故 |
| --- | --- | --- |
| block-database-wipe | `DROP DATABASE`, `prisma migrate reset` | [#34729](https://github.com/anthropics/claude-code/issues/34729) 本番DB消失 |
| protect-dotfiles | `.bashrc`, `.ssh/`, `.aws/`の変更 | [#37478](https://github.com/anthropics/claude-code/issues/37478) 設定ファイル上書き |
| scope-guard | プロジェクト外のファイル操作 | [#36233](https://github.com/anthropics/claude-code/issues/36233) ファイルシステム全削除 |
| network-guard | `curl POST`でファイル送信 | [#37420](https://github.com/anthropics/claude-code/issues/37420) データ流出 |
| secret-file-read-guard | `.env`やcredentialsの読み取り | API キー流出防止 |

### 自動承認（安全なコマンドは自動で許可）

`git log`, `git status`, `ls`のような読み取り専用コマンドは、いちいち許可を求められると面倒。自動承認hookは**安全なコマンドだけ**を自動許可する。

```
npx cc-safe-setup --install-example auto-approve-git-read
```

### 品質ガード（コードの品質を守る）

| hook | やること |
| --- | --- |
| syntax-check | 編集後に構文チェックを自動実行 |
| diff-size-guard | 1回の変更が大きすぎたら警告 |
| test-deletion-guard | テストの削除をブロック |
| verify-before-done | 「完了」と言う前に検証を要求 |

## なぜIssueから作るのか

自分が想像した問題ではなく、**実際に誰かが踏んだ問題**から作る。

`.bashrc`がchezmoiで上書きされた人がいた（[#37478](https://github.com/anthropics/claude-code/issues/37478)）。翌日にprotect-dotfilesを作った。

`prisma migrate reset`でデータが消えた人がいた（[#34729](https://github.com/anthropics/claude-code/issues/34729)）。block-database-wipeにPrisma対応を追加した。

Issueが先、hookが後。641個のhookは、637個の「誰かが困った記録」から生まれた。

## 始め方

```
# ステップ1: 基本hookをインストール（10秒）
npx cc-safe-setup

# ステップ2: 安全スコアを確認
npx cc-health-check

# ステップ3: 必要に応じてexample hookを追加
npx cc-safe-setup --examples
npx cc-safe-setup --install-example <好きなhook名>
```

Claude Codeを使い始めたばかりの人も、しばらく使っている人も、まず`npx cc-safe-setup`から。事故は「自分には起きない」と思っている時に起きる。

---

📚 関連記事:

---

**📖 トークン消費に困っているなら** → [Claude Codeのトークン消費を半分にする——800時間の運用データから見つけた実践テクニック](https://zenn.dev/yurukusa/books/token-savings-guide?utm_source=qiita-ce9a7c04&utm_medium=article&utm_campaign=token-book)（¥2,500・はじめに+第1章 無料）

---

**⚠️ Opus 4.7ユーザーへ（2026年4月17日追記）**  
4月16日のOpus 4.7デフォルト化で、トークン消費が最大4倍に急増しています（[#49541](https://github.com/anthropics/claude-code/issues/49541)）。安全分類器のバグで20件以上のデータ損失も報告されています（[#49618](https://github.com/anthropics/claude-code/issues/49618)）。

---

**⚠️ CVE-2026-21852（2026年4月公開）**: プロジェクト内`.claude/settings.json`経由でAPIキー窃盗。対策: `npx cc-safe-setup`（ユーザーレベル設定で免疫）→ [詳細](https://yurukusa.github.io/cc-safe-setup/opus-47-survival-guide.html#cve-settings-exfil)
