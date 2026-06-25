---
id: "2026-06-23-claude-codeの使用量をmacosメニューバーで常時確認できるアプリを作った-01"
title: "Claude Codeの使用量をmacOSメニューバーで常時確認できるアプリを作った"
url: "https://zenn.dev/yotake/articles/4173a27c455976"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

Claude Codeをヘビーに使っていると、「あとどれくらい使えるんだろう」が気になります。確認するには **ブラウザもしくは Claude アプリの Usage ページを開く**必要があって、地味に面倒でした。

そこで、メニューバーに使用量を常時表示する macOS アプリ **ClaudeMeter** を作りました。

## こんな感じで使えます

メニューバーに現在のセッション消費率がパーセント表示され、クリックで詳細が開きます。

![ClaudeMeterのポップオーバー](https://res.cloudinary.com/zenn/image/fetch/s--SKaqt8xm--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://github.com/yotake/claude-meter/raw/main/assets/screenshot-ja.png?_a=BACMTiAE)

![ClaudeMeterの設定パネル](https://res.cloudinary.com/zenn/image/fetch/s--vO3zF6IC--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://github.com/yotake/claude-meter/raw/main/assets/screenshot-settings-ja.png?_a=BACMTiAE)

## できること

* **現在のセッション** — 5時間枠の利用率 + リセットまでの残り時間
* **週間リミット** — 全モデル / Sonnet それぞれの残量（リセット曜日つき）
* **Codex レート制限**（任意）— ローカルの Codex CLI ログから読み取り
* **API 支出**（任意）— Admin キーで今月の支出を表示
* **複数アカウント** — 複数のサブスク / APIキーを同時に表示

消費ペースを予測してメニューバーのパーセント表示に色がつくので、残量が少なくなったら一目でわかります。

## インストール

[Releases](https://github.com/yotake/claude-meter/releases) から `ClaudeMeter-1.1.dmg` をダウンロードして、`ClaudeMeter.app` をアプリケーションフォルダへドラッグするだけです。

## トークンの設定

Claude Code（`claude` CLI）を使っている場合、ターミナルで次を実行するとトークンがクリップボードにコピーされます。

```
security find-generic-password -s "Claude Code-credentials" -w | pbcopy
```

## 技術的な話

### Swift + SwiftUI で書いた

Swift 5.9、macOS 13+ ターゲットです。UI は SwiftUI の `MenuBarExtra` を使っていて、ポップオーバーを AppKit と組み合わせて実装しています。

### Usage API のポーリング

claude.ai の Usage ページが内部で叩いている `https://api.anthropic.com/api/oauth/usage` を 5 分間隔でポーリングしています。このエンドポイントには `user:profile` スコープの OAuth トークンが必要です。

レート制限（HTTP 429）を受けると、レスポンスの `Retry-After` ヘッダー + 60 秒のバッファで自動的にバックオフします。

### トークンの自動更新

アクセストークンの有効期限まで 5 分を切ると先回りしてリフレッシュします。また 401 が返ってきた場合もリアクティブにリフレッシュを試みます。

トークンは `~/Library/Application Support/ClaudeMeter/accounts.json`（パーミッション `0600`）に保存されます。アプリ自体は macOS Keychain にアクセスしません（ad-hoc 署名アプリが Keychain を参照するとアンチウイルスが警告を出すことがあるため）。

### Codex ログのパース

Codex CLI のレート制限表示は、外部 API を叩くのではなくローカルの `~/.codex/sessions/*.jsonl` を直接パースしています。`token_count` イベントの `rate_limits` フィールドを読み取っているので、ネットワーク通信ゼロで取得できます。

### 複数アカウント対応

サブスク複数持ちや、サブスク + Admin API キーの組み合わせを同時に表示できます。アカウントごとに独立してポーリング・トークン更新が動きます。

## おわりに

無料・オープンソースで公開しています。

役に立ったら [GitHub Sponsors](https://github.com/sponsors/yotake) での支援が励みになります（Apple Developer 年会費の補填に使います）。

フィードバックや不具合報告は GitHub Issues へどうぞ。
