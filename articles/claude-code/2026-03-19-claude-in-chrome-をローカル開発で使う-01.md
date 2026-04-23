---
id: "2026-03-19-claude-in-chrome-をローカル開発で使う-01"
title: "Claude in Chrome をローカル開発で使う"
url: "https://zenn.dev/yuyu_496/articles/c250d4037d3325"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

**記事概要**  
Claude in Chrome拡張機能とClaude Code CLIを組み合わせてコードのフィードバックループを回す方法と、localのみのアクセス制限などセキュアな設定手順をまとめています。

**対象読者**  
Claude Codeを使ってWeb開発をしていて、AI出力コードの質向上とテスト・デバッグの効率化に興味がある方を対象としています。

---

## 1. サイトアクセスをlocalのみに絞る

Claudeがアクセスできるサイトを `localhost` だけに制限します。

### 手順

1. Chromeのツールバーで拡張機能アイコンを右クリック
2. 「拡張機能を管理」→「サイトへのアクセス」
3. **「On specific sites」** を選択
4. `localhost` や `127.0.0.1` を追加

### 各オプションの違い

| オプション | 動作 |
| --- | --- |
| On click | クリックするたびに手動で許可 |
| **On specific sites** ✅ | 指定サイトのみ常時アクセス可能 |
| On all sites | すべてのサイトにアクセス可能 |

---

## 2. Permission Mode を設定する

Claudeが操作する前に確認を挟むかどうかの設定です。

### 場所

Chromeツールバーの **Claudeアイコン** をクリック → サイドパネルのチャット入力欄のドロップダウン

### 2つのモード

| モード | 動作 |
| --- | --- |
| **Ask before acting** ✅ | 操作前にプランを提示→承認後に実行 |
| Act without asking | 確認なしで即実行 |

### 承認済みサイトの確認

「Ask before acting」で許可したサイトは、Claude in Chrome settings>Permissionページで確認できます。

**手順:** 拡張機能アイコンを右クリック →「Manage Extension」→「Extension options」→「開いたページ内のYour approved sites欄」

なお、1で設定した「On specific sites」の登録サイトと、「Ask before acting」で都度許可したサイトは別々に管理されています。  
意図しないサイトが承認済みになっていないか、定期的に確認しておくと安心です。

---

## 3. Claude Code CLI と Chrome を繋げる

### セットアップ

```
# Claude Codeをインストール or 最新版に更新
# Chrome Web StoreからClaude in Chromeをインストールしておく

# Chrome連携を有効にして起動
claude --chrome
```

### 使い方イメージ

```
> localhost:3000を開き、ログインフォームに無効なデータを送信する
  エラーメッセージが正しく出るか確認して、正しくない場合は修正して
```

こんな感じで自然言語で投げると、Claudeがブラウザを操作して結果を返してくれます。

---

## 4. /chrome コマンドで管理する

Claude Code CLI内では `/chrome` コマンドで接続周りを管理できます。

| やりたいこと | 操作 |
| --- | --- |
| 接続状態の確認 | `/chrome` を実行 |
| `--chrome` を毎回省略したい | `/chrome` →「Enabled by default」 |
| 接続が切れた | `/chrome` →「Reconnect extension」 |

**Enabled by default** にすると `claude` だけで起動してもChrome連携がONになります。  
ただしコンテキスト使用量が増えるのとセキュリティ的にも明示的な方が良いのでOFF推奨です。

**Reconnect extension** は長いセッションで拡張機能のService Workerがアイドルになって接続が切れたときに使います。

---

## 5. セキュリティについて

### プロンプトインジェクションに注意

Webページに埋め込まれた悪意ある指示によって、Claudeが意図しない操作をさせられるリスクがあります。アクセス先を `localhost` に絞るのが一番シンプルな対策です。  
ただし、localhostでも外部の情報を取り込んでいる場合は、外部サイトにアクセスするのと同様のリスクが生じます。

### 推奨設定まとめ

| 設定 | 推奨値 | 理由 |
| --- | --- | --- |
| サイトアクセス | On specific sites（`localhost`のみ） | 外部への意図しないアクセスを防ぐ |
| Permission Mode | Ask before acting | 操作前に確認できる |
| Chrome連携の起動 | 必要なときだけ `--chrome` | 攻撃面を最小化・使用の明示 |

---

## 参考リンク
