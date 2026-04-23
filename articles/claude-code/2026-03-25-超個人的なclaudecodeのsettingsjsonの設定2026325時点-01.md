---
id: "2026-03-25-超個人的なclaudecodeのsettingsjsonの設定2026325時点-01"
title: "超個人的なClaudeCodeのsettings.jsonの設定（2026/3/25時点）"
url: "https://qiita.com/TatApp/items/1f2feeb5ac2a785dcbd7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## はじめに

Claude Code を使い始めて、毎回権限の確認ダイアログが出たり、処理が終わっても気づかなかったりと、使用している上でネックだった部分があったので、グローバル設定（`~/.claude/settings.json`）を整理しました。

完全に個人の好み全開の設定ですが、誰かの参考になれば。

## 設定ファイルの場所

```
%USERPROFILE%\.claude\settings.json
```

Windows の場合は `C:\Users\<ユーザー名>\.claude\settings.json` です。

## 全体像

```
{
  "permissions": {
    "allow": [
      "Bash",
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "WebFetch",
      "WebSearch"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Read(./.env)",
      "Read(./**/*.pem)"
    ]
  },
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\<ユーザー名>\\.claude\\hooks\\notify.ps1"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\<ユーザー名>\\.claude\\hooks\\notify.ps1"
          }
        ]
      }
    ]
  },
  "language": "japanese",
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "70"
  },
  "autoUpdater": {
    "check": true
  },
  "theme": "dark"
}
```

以下、各項目の解説です。

---

## 1. 権限設定（permissions）

```
"permissions": {
  "allow": [
    "Bash", "Read", "Edit", "Write",
    "Glob", "Grep", "WebFetch", "WebSearch"
  ],
  "deny": [
    "Bash(rm -rf *)",
    "Read(./.env)",
    "Read(./**/*.pem)"
  ]
}
```

### allow

`Bash` と書くだけで **全Bashコマンドが確認なしで実行**されます。個別に `Bash(git add *)` `Bash(node *)` と書く必要はありません。

同様に `Read` `Edit` `Write` なども、ツール名だけで全許可です。

これで毎回のダイアログ地獄から解放されます。

### deny

`deny` は `allow` より**常に優先**されます。全許可しつつ、本当に危険な操作だけブロックするスタイル。

| ルール | 理由 |
| --- | --- |
| `Bash(rm -rf *)` | 再帰削除の事故防止 |
| `Read(./.env)` | APIキー等の機密情報が会話ログに残るのを防止 |
| `Read(./**/*.pem)` | 秘密鍵ファイルの読み取り防止 |

MCP ツール（Unity MCP等）を使う場合は、プロジェクトごとの `.claude/settings.local.json` で `"mcp__サーバー名"` を allow すれば、サーバー単位で一括許可できます。

---

## 2. 通知フック（hooks）

```
"hooks": {
  "Notification": [ ... ],
  "Stop": [ ... ]
}
```

| イベント | タイミング |
| --- | --- |
| `Notification` | 権限確認など、ユーザーの注意が必要な時 |
| `Stop` | Claude の応答が完了した時 |

長い処理を走らせて別の作業をしている時に、**音とバルーン通知**で完了を知らせてくれます。

### 通知スクリプト（notify.ps1）

`%USERPROFILE%\.claude\hooks\notify.ps1` に配置します。

```
Add-Type -AssemblyName System.Windows.Forms
[System.Media.SystemSounds]::Asterisk.Play()
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon = [System.Drawing.SystemIcons]::Information
$n.Visible = $true
$n.BalloonTipTitle = 'Claude Code'
$n.BalloonTipText = '処理が完了しました'
$n.BalloonTipIcon = 'Info'
$n.ShowBalloonTip(3000)
Start-Sleep -Milliseconds 3500
$n.Dispose()
```

### ハマりポイント

実際に設定する中でいくつかハマったので共有します。

**command のパスは絶対パス必須**

```
// NG: 動かない
"command": "powershell ... -File ~/.claude/hooks/notify.ps1"

// OK: 動く
"command": "powershell ... -File C:\\Users\\<ユーザー名>\\.claude\\hooks\\notify.ps1"
```

`~` は PowerShell では展開されません。必ずフルパスで指定してください。

**notify.ps1 は UTF-8 BOM 付きで保存**

PowerShell 5.1 は BOM なしの UTF-8 だと日本語が文字化けします。VS Code なら右下のエンコード表示をクリックして「UTF-8 with BOM」で保存してください。

**無効なイベント名を入れると全フックが壊れる**

```
// NG: StopFailure は存在しないイベント名
// → Notification も Stop も含めて全部動かなくなる
"hooks": {
  "Notification": [ ... ],
  "Stop": [ ... ],
  "StopFailure": [ ... ]
}
```

存在しないイベント名を1つでも入れると、hooks セクション全体がサイレントに無効化されます。エラーも出ません。これは本当にハマります。

---

## 3. 応答言語の固定（language）

これを設定しないと、英語のコードを扱っている時に英語で返答されることがあります。常に日本語で返してほしいなら設定しておくと安心。

---

## 4. コンテキスト自動圧縮（env）

```
"env": {
  "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "70"
}
```

Claude Code はコンテキストウィンドウが一杯になると自動で会話を圧縮しますが、デフォルトでは **95%** まで溜まってから実行されます。

70% に下げることで、余裕があるうちに圧縮が走るようになり、突然のコンテキスト不足を回避できます。

---

## まとめ

| 設定 | 効果 |
| --- | --- |
| `permissions.allow` | 確認ダイアログなしでスムーズに作業 |
| `permissions.deny` | 危険な操作だけブロック |
| `hooks.Stop` | 処理完了を通知で把握 |
| `hooks.Notification` | 入力待ちを通知で把握 |
| `language` | 応答を日本語に固定 |
| `autocompact 70%` | コンテキストの早め圧縮 |
