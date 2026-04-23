---
id: "2026-03-23-claude-codehooks機能でデスクトップ通知を設定してみた-01"
title: "【Claude Code】Hooks機能でデスクトップ通知を設定してみた"
url: "https://qiita.com/pro-tein/items/49e5dbec705c3497dd51"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

# はじめに

※今回はMacOS環境での例を紹介します。  
Claude Codeを使用していると、以下のようなケースで**気づいたら処理が止まっている**といったことがあると思います。  
・（ファイルの操作権限が必要であれば）ファイル操作のために必要な権限付与の許可待ち  
・（質問であれば）質問の回答待ちもしくは深堀りのための逆質問  
・（タスクを依頼していたら）タスク完了時  
こまめに処理が止まっていないかを確認するのも大変です。  
そこで、今回はClaude Codeの**Hooks**機能を使用して、上記のようなケースにデスクトップ通知させる設定方法を紹介します。

# Hooksとは

簡潔にまとめると、「Claude Codeセッション中の**特定のポイント**に、カスタム処理を差し込める仕組み」です。  
まずは、これらの公式ドキュメントを読むことをおすすめします。

たくさんの **'特定のポイント'** （＝イベントタイプ）がありますが、例として以下のような利用方法があります。

**PreToolUse**(ツールが実行された直後に発火するフック)  
・危険コマンドのブロック（`rm -rf`など）  
・機密ファイル保護（.envへのアクセスを拒否など）

**PostToolUse**(ツールが実行される直前に発火するフック)  
・コード整形（Prettierなど）  
・ログの記録

**Notification**(特定のイベント発生時に通知処理を実行するためのフック)  
・通知（入力待ち、タスク完了）

だいたいのことは実現できそうなので、いろいろ試してみるのも面白いと思います。

・Hooksは並列処理のため、同じタイミングで発火する複数処理の順序は保証されません  
・エラー時はタイムアウト60秒で処理が停止します

・Hooksコマンドは**権限付与の許可を待たずに**ユーザーのフルアクセス権限で実行されるため、注意が必要です

# デスクトップ通知の設定

（私はすべての環境に適用させたいのでホームディレクトリの）`.claude/settings.json`に以下のような記述を追加します。  
※必要に応じてプロジェクト直下の設定ファイルを使用するなどしてください。  
設定はこれだけです。  
設定が完了すると、`スクリプトエディタ`アプリから通知が届くようになります。（Macのデフォルトの仕様）

~/.claude/settings.json

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude finished responding\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

### Notification

条件フィルタ（matcher）を`"matcher": ""`とすることで、「Claudeが通知を出す**すべて**のタイミング」で発火するようにしています。  
`osascript`はmacOSのAppleScriptをCLIから実行する仕組みで、`display notification`でネイティブ通知（Notification Center）を表示させます。

(ファイル操作の権限付与の許可待ち時)

[![SCR-20260323-qgth.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F837dbf99-2346-4525-82c2-ec65d2b97ec6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=75d1e80610ef14a6267312a3d1eefc9d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F837dbf99-2346-4525-82c2-ec65d2b97ec6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=75d1e80610ef14a6267312a3d1eefc9d)

### Stop

Claude Codeが処理を終了したタイミングで発火させたい場合はNotificationではなく、**Stop**を使用します。

（回答終了時）

[![SCR-20260323-qfmn.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F6b34a864-9744-4da8-938b-b0108d81b790.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4beca3e65b37d8f3ec7f34e8b70cfbf7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F6b34a864-9744-4da8-938b-b0108d81b790.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4beca3e65b37d8f3ec7f34e8b70cfbf7)

### 通知が飛ばない場合

・claudeを再起動しないと設定が適用されない場合があります。  
・MacBookで「おやすみモード」などが有効になっていると通知が飛ばない場合があります。  
・`Macのシステム設定 >> 通知 >> スクリプトエディタ`の通知が許可されていることを確認してください

[![SCR-20260323-qjfv.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Ff9b33336-41c5-4476-85f0-e28c1d787c2a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=dd84b4b00a77477d69a20057211207da)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Ff9b33336-41c5-4476-85f0-e28c1d787c2a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=dd84b4b00a77477d69a20057211207da)

# おまけ

`スクリプトエディタ`アプリから通知が届くようになったのはいいものの、通知バナーをクリックすると毎回以下のようなウィンドウが開いてしまいます。

[![SCR-20260323-qmcp.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F4357bab4-4f15-4cba-8251-a90a152811b8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d67772045409bb07a1dacf60fc83efe4)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F4357bab4-4f15-4cba-8251-a90a152811b8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d67772045409bb07a1dacf60fc83efe4)

そこで、現在使用しているターミナルから通知が来るようにする方法を紹介します。  
※一部対応できないターミナルがあるようです。  
※今回ターミナルは**Ghostty**を使用しています。

Ghosttyに関するこちらの記事もおすすめです。

`Macのシステム設定 >> 通知 >> Ghostty`の通知が許可されていることを確認し、  
設定ファイルを以下のように修正します。

~/.claude/settings.json

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "printf '\\x1b]9;Claude finished responding\\x07' > /dev/tty"
          }
        ]
      }
    ]
  }
}
```

### Notification

権限確認のような、「絶対に見逃してはいけないイベント」は、Claudeによってhooksとは別系統で強制通知されるそうです。  
Ghosttyの通知を許可するだけで勝手に通知されるため、今回はあえて**Notification**を設定していません。

### Stop

これはClaudeの処理終了時（Stopイベント）にターミナルへ制御シーケンスを送っています。  
`printf '\x1b]9;{メッセージ}\x07'`  
これはOSC 9 (Operating System Command)というターミナル仕様です。  
・`\x1b]` → OSC開始  
・`9;` → 「通知を出せ」という命令  
・`\x07` → 終了  
GhosttyはこのOSC 9を受け取るとmacOSのネイティブ通知を出します。  
`Claude → printf → OSC 9 → Ghostty → macOS通知`

設定が適用されていれば、以下のようにGhosttyから通知がとどきます。  
また、このバナーをクリックするとちゃんとClaude Codeの対象セッション画面が開きます。  
（真ん中のタイトル行にはセッションタイトルが自動的に反映されるようです）

[![SCR-20260323-qrrw.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fb1539cfe-9cbe-40af-b133-248a67e46be7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8b4d1cc366c919a29100e7db7746a032)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fb1539cfe-9cbe-40af-b133-248a67e46be7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8b4d1cc366c919a29100e7db7746a032)

# さいごに

`terminal-notifier`を使用したパターンもあるそうなので、気になった方はぜひ調べてみてください。
