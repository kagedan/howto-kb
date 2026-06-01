---
id: "2026-05-31-mcp-launcher-phase-2patを短命トークンに置き換える-01"
title: "mcp-launcher Phase 2：PATを短命トークンに置き換える"
url: "https://zenn.dev/masuda_masuo/articles/2026-05-31-mcp-launcher-phase2"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

前回の記事では、MCPサーバーのconfigに平文で書かれていたAPIキーをOSキーストアに移した。configからシークレットは消えた。しかし問題が一つ残っていた。

<https://zenn.dev/masuda_masuo/articles/2026-05-28-mcp-launcher>

---

## 残っていた問題：PATは長期のまま

Phase 1でキーストアに保存されるのは、通常のPersonal Access Token（PAT）だ。PATは手動でrevokeするまで有効であり続ける。configに書かれなくなっただけで、漏洩した場合のリスクは変わらない。

プロンプトインジェクションのシナリオを考えると、これは無視できない。Claude Codeが外部のリポジトリを読んでいるとき、コードベースに仕込まれた悪意あるコメントがAIを誘導してトークンを外部送信させる可能性がある。トークンが長期有効である限り、漏洩のダメージは時間的に限定されない。

Phase 2のテーマは「**漏洩してもダメージが1時間で切れるトークンに置き換える**」だ。

---

## GitHub Appによる短命トークンの仕組み

GitHub Appのインストールアクセストークンは最大1時間有効だ。PATとは異なり、期限が来れば自動的に無効になる。

GitHub Appを作成すると、3つの長期クレデンシャルが手に入る。

| クレデンシャル | 用途 |
| --- | --- |
| App ID | GitHub Appの識別子 |
| 秘密鍵（RSA） | JWTの署名に使う |
| Installation ID | どのアカウント/Orgへのアクセスか |

この3つを使ってGitHub APIを叩くと、最大1時間有効な短命トークンが発行される。mcp-launcherはこの短命トークンだけをMCPサーバーに渡す。

### クレデンシャルの階層

ここが設計上の重要なポイントだ。

| クレデンシャル | 保存場所 | MCPサーバーに渡る | Claudeから見える |
| --- | --- | --- | --- |
| App ID・秘密鍵・Installation ID | OSキーストア | ❌ | ❌ |
| 短命トークン（最大1時間） | envとして子プロセスに注入 | ✅ | ⚠️ 間接的に |

App ID・秘密鍵・Installation IDはCLIで一度登録するだけで、キーストアの外に出ない。MCPサーバーのプロセスには渡されず、Claudeが読めるいかなる経路にも現れない。

短命トークンは子プロセスのenvに注入される。信頼できるMCPサーバー（公式のGitHub MCP Serverなど）はそれをGitHub APIの呼び出しにのみ使い、ツールレスポンスには含めない。Claudeが環境変数を直接読む手段はなく、観測できるのはMCPのツールレスポンスだけだ。

プロンプトインジェクション攻撃がアクセスできる最大範囲はMCPのツールレスポンスだ。OSキーストアには届かない。

| クレデンシャル | プロンプトインジェクションで到達できるか | 漏洩時の影響 | 有効期限 |
| --- | --- | --- | --- |
| 秘密鍵 | ❌ 到達不可 | 🔴 高——無期限にトークンを発行できる | なし（手動revoke） |
| 短命トークン | ⚠️ ツールレスポンス経由で到達可能性あり | 🟡 限定的——最大1時間のみ有効 | 最大1時間 |

秘密鍵がClaudeの届く経路に入ることは構造上ない。仮に侵害されるとすればOSレベルのアクセスが必要であり、それはプロンプトインジェクションとは根本的に異なる攻撃だ。それでも長期クレデンシャルとして扱い、キーストア以外には保存せず、侵害が疑われる場合はGitHub App設定からすぐにrevokeする。

---

## 当初の設計：「起動時リフレッシュで十分」

Phase 2の最初の設計はシンプルだった。daemonは作らない。`mcp-launcher`が呼ばれるたびに起動前にトークンの期限をチェックし、期限切れ間近であれば新しいトークンを取得してからMCPサーバーを起動する。

```
mcp-launcher github
    ↓
キーストアからEXPIRYを確認
  ├ 初回 or 期限切れ間近 → GitHub App APIで新トークン取得 → キーストアに保存
  └ まだ有効 → スキップ
    ↓
短命トークンをenvに注入してgithub-mcp-serverを起動
```

Claude DesktopはMCPサーバーをstdioプロセスとして都度起動する。起動のたびにチェックすれば十分な頻度が確保できる——そう考えていた。

---

## 動かして気づいたこと

実際に使ってみると問題が明らかになった。

**Claude DesktopはMCPサーバーを起動時に一度だけ生成し、常駐させる。**

プロセスの実態はこうだ。

```
Claude Desktop（常駐）
    ↓ 起動時に一度だけ生成
mcp-launcher（常駐・Claude Desktopに掴まれている）
    ↓
github-mcp-server（常駐）
```

mcp-launcherはClaude Desktopが掴んでいるプロセスとして常駐し続ける。「起動のたびにチェック」が走るのは**Claude Desktopを再起動したときだけ**だ。

つまりトークンの有効期限を1時間に設定した場合、1時間ごとにClaude Desktopを再起動しなければPATが更新されない。これは現実的な運用ではない。

---

## バックグラウンドリフレッシュの実装

Claude Desktopに掴まれたまま常駐しているmcp-launcherが、セッション中もトークンを監視すれば問題は解決できる。

`check_interval_seconds`を設定すると、mcp-launcherがgithub-mcp-serverのプロセスを管理しながら定期的にトークンの期限をチェックする。期限切れ間近になれば新しいトークンを取得し、子プロセスを再起動して新しいトークンを渡す。

```
{
  "github": {
    "command": "C:\\path\\to\\github-mcp-server.exe",
    "args": ["stdio"],
    "env_keys": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "mcp-launcher/github/GITHUB_PERSONAL_ACCESS_TOKEN"
    },
    "token_source": {
      "type": "github_app",
      "app_id_key": "mcp-launcher/github/APP_ID",
      "private_key_key": "mcp-launcher/github/PRIVATE_KEY",
      "installation_id_key": "mcp-launcher/github/INSTALLATION_ID",
      "target_env_key": "GITHUB_PERSONAL_ACCESS_TOKEN",
      "refresh_before_seconds": 600
    },
    "check_interval_seconds": 60
  }
}
```

`check_interval_seconds: 60`は「60秒ごとにトークン期限を確認する」設定だ。`refresh_before_seconds: 600`と組み合わせることで、期限の10分前に自動的に新しいトークンが取得される。

---

## 次の問題：処理中に子プロセスが落ちる

バックグラウンドリフレッシュを実装したところ、新たな問題が浮上した。

Claude CodeがGitHubのMCPを使ってGit操作を実行している最中に、タイミング悪くトークンリフレッシュが走ると、子プロセス（github-mcp-server）が再起動されて処理が落ちる。

単純な「タイマーで定期kill→再起動」では、進行中のリクエストを巻き込む。

---

## 状態遷移による解決

解決策は「処理が終わってから再起動する」だ。mcp-launcherはgithub-mcp-serverへのJSON-RPCをプロキシし、in-flightのリクエスト数を把握する。再起動はアイドル状態になったときだけ実行される。

```
Ready（通常動作）
    ↓ トークン期限切れ間近を検知
Draining（新規リクエストをキューに積む・進行中を待つ）
    ↓ in-flight == 0
Restarting（トークンリフレッシュ → 子プロセス再起動 → 再ハンドシェイク）
    ↓
Ready（キューに積んでいたリクエストをflush）
```

Draining中に届いた新規リクエストはキューに積まれ、再起動完了後に新しい子プロセスへflushされる。Claude側からは処理が一時的に待たされるだけで、失敗しない。

### 再ハンドシェイクが必要な理由

Claude Desktopが見ているstdioはmcp-launcherのプロセスのものだ。子プロセスを差し替えてもストリームは生きたままなので、Claude Desktopは再初期化しようとしない。新しいgithub-mcp-serverには`initialize`リクエストが届かず、初期化待ちのまま詰まる。

mcp-launcherはこれを回避するため、初回の`initialize`と`notifications/initialized`をキャッシュしておき、子プロセス再起動時に自分で再送する。このとき再送する`initialize`のidを通常リクエストと区別できる固定値（sentinel id）に書き換えることで、その応答だけを握りつぶしてClaude Desktop側には転送しない。

---

## 現状のスコープ

**Phase 2が対応すること：**

* ✅ 短命トークン（最大1時間）の自動発行・更新
* ✅ セッション中のバックグラウンドリフレッシュ
* ✅ 処理中の再起動を避ける状態遷移
* ✅ Claude Desktopの再起動不要

**制約：**

* GitHub App専用。AWS・Azure・GCPなど他サービスはPhase 1（静的トークン）のまま
* `check_interval_seconds`を設定しない場合は起動時リフレッシュのみ（Phase 1相当の動作）

**前提条件（Phase 1から変わらない）：**

* OSのログインセッションが侵害された場合はキーストアも読める。「configに鍵を置かない」という話であり、「侵害されたマシンを守る」という話ではない

---

## セットアップ

### 1. GitHub Appを作成する

1. <https://github.com/settings/apps/new> にアクセス
2. App name・Homepage URLを入力、Webhookは無効化
3. Permissionsで必要な権限だけ付与（例：`Contents: Read & Write`、`Issues: Read & Write`）
4. **Create GitHub App** → 画面上部の **App ID** をメモ

### 2. 秘密鍵を生成する

App設定ページの **Private keys** → **Generate a private key** で `.pem` ファイルをダウンロード。

### 3. AppをインストールしてInstallation IDを取得する

App設定ページの **Install App** → アカウントまたはOrganizationを選択 → インストール後のURLの末尾の数字がInstallation ID。

### 4. キーストアに登録する

```
mcp-launcher register github APP_ID 123456
mcp-launcher register github PRIVATE_KEY "$(cat path/to/private-key.pem)"
mcp-launcher register github INSTALLATION_ID 7654321
```

秘密鍵ファイル（.pem）はキーストア登録後に削除してよい。ファイルとして残しておく必要はない。

### 5. launcher.jsonを更新する

```
{
  "github": {
    "command": "C:\\path\\to\\github-mcp-server.exe",
    "args": ["stdio"],
    "env_keys": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "mcp-launcher/github/GITHUB_PERSONAL_ACCESS_TOKEN"
    },
    "token_source": {
      "type": "github_app",
      "app_id_key": "mcp-launcher/github/APP_ID",
      "private_key_key": "mcp-launcher/github/PRIVATE_KEY",
      "installation_id_key": "mcp-launcher/github/INSTALLATION_ID",
      "target_env_key": "GITHUB_PERSONAL_ACCESS_TOKEN",
      "refresh_before_seconds": 600
    },
    "check_interval_seconds": 60
  }
}
```

Claude Desktopのconfigは変更不要だ。

---

## まとめ

Phase 1でconfigからシークレットは消えた。Phase 2でMCPサーバーに渡るトークンを短命にした。

設計は「起動時リフレッシュで十分」から始まったが、Claude Desktopがプロセスを常駐させる実態に合わせてバックグラウンドリフレッシュを追加し、さらに処理中の再起動問題を状態遷移で解決した。動かしながら設計を更新した記録でもある。

Phase 3では、キーストアのシークレットを取り出す際にFIDO2・パスキーによる人間の承認を要求する仕組みを検討している。

---

## リンク
