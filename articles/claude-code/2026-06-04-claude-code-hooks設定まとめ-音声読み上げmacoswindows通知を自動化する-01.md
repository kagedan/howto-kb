---
id: "2026-06-04-claude-code-hooks設定まとめ-音声読み上げmacoswindows通知を自動化する-01"
title: "Claude Code hooks設定まとめ — 音声読み上げ＆macOS/Windows通知を自動化する"
url: "https://qiita.com/satoshi_061/items/b18cce9612f6f155e294"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code で長めのタスクを走らせながら別の作業をしていると、「気づいたらとっくに完了してた」「権限確認ダイアログで止まってた」という状況になりがちです。

この記事では、Claude Code の **hooks 機能** を使って、作業完了時・権限確認時に macOS / Windows のネイティブ通知と音声読み上げを自動で出す設定方法をまとめます。

---

## TL;DR

- Claude Code には `Stop`（完了時）と `PermissionRequest`（権限確認時）のフックがある
- **macOS**: `osascript` で通知、`/usr/bin/say -v Kyoko` で日本語音声読み上げ
- **Windows**: PowerShell の `SpeechSynthesizer` で音声読み上げ、`BurntToast` でトースト通知
- `async: true` を付けることで本来の処理をブロックしない
- 設定ファイルは `~/.claude/settings.json`（グローバル設定）

---

## hooks とは

Claude Code の hooks は、特定のタイミングでシェルコマンドを自動実行できる仕組みです。

主なフックの種類：

| フック名 | 発火タイミング |
|---|---|
| `Stop` | Claude が返答・作業を完了した直後 |
| `PermissionRequest` | 許可リストにないツールの実行前（権限ダイアログが出る直前） |
| `Notification` | 席を離れている時の待機通知 |

---

## macOS での設定方法

### 設定ファイルの場所

```
~/.claude/settings.json（グローバル設定）
```

### 設定内容

以下を `settings.json` の `hooks` キーに追加します。

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "osascript -e 'display notification \"作業が完了したよ\" with title \"Claude Code\"' 2>/dev/null; /usr/bin/say -v Kyoko '作業が完了したよ' 2>/dev/null",
          "async": true
        }
      ]
    }
  ],
  "PermissionRequest": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "osascript -e 'display notification \"権限確認が必要だよ\" with title \"Claude Code\"' 2>/dev/null; /usr/bin/say -v Kyoko '権限確認が必要だよ' 2>/dev/null",
          "async": true
        }
      ]
    }
  ]
}
```

### ポイント解説

- **`osascript`**：macOS ネイティブ通知を表示するコマンド
- **`/usr/bin/say -v Kyoko`**：macOS の日本語音声（Kyoko = 日本語女性ボイス）で読み上げ
- **`2>/dev/null`**：エラー出力を捨て、余計なログを残さない
- **`async: true`**：フックを非同期実行し、Claude 本来の処理をブロックしない（重要）

### 設定の反映方法

```bash
# /hooks コマンドで確認・反映
/hooks

# または Claude Code を再起動
```

---

## Windows での設定方法

Windows では `osascript` や `say` コマンドが使えないため、PowerShell で同等の機能を実現します。

### 方法①：音声読み上げのみ（追加インストール不要）

PowerShell に標準搭載の `System.Speech.Synthesis.SpeechSynthesizer` を使います。

**前提**: 日本語音声パックが Windows にインストールされていること
（設定 → 時刻と言語 → 音声認識 → 音声を管理 → 音声を追加 → 「日本語」を追加）

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "powershell -ExecutionPolicy Bypass -Command \"Add-Type -AssemblyName System.speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('作業が完了したよ')\"",
          "async": true
        }
      ]
    }
  ],
  "PermissionRequest": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "powershell -ExecutionPolicy Bypass -Command \"Add-Type -AssemblyName System.speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('権限確認が必要だよ')\"",
          "async": true
        }
      ]
    }
  ]
}
```

### 方法②：トースト通知 + 音声（BurntToast モジュール使用）

**BurntToast** を使うと、macOS の `osascript` と同様のトースト通知が出せます。

まず PowerShell を管理者権限で開き、モジュールをインストールします。

```powershell
Install-Module -Name BurntToast -Force
```

`settings.json` の設定：

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "powershell -ExecutionPolicy Bypass -Command \"Import-Module BurntToast; New-BurntToastNotification -Text 'Claude Code', '作業が完了したよ'\"",
          "async": true
        }
      ]
    }
  ],
  "PermissionRequest": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "powershell -ExecutionPolicy Bypass -Command \"Import-Module BurntToast; New-BurntToastNotification -Text 'Claude Code', '権限確認が必要だよ'\"",
          "async": true
        }
      ]
    }
  ]
}
```

### macOS / Windows の比較

| 機能 | macOS | Windows |
|---|---|---|
| 通知表示 | `osascript` | `BurntToast`（要インストール） |
| 音声読み上げ | `/usr/bin/say -v Kyoko` | `System.Speech.SpeechSynthesizer` |
| 日本語対応 | デフォルトで利用可 | 日本語音声パックの追加が必要 |

---

## 各環境での動作確認

| 環境 | 動作 |
|---|---|
| Claude Code CLI（ターミナル） | ✅ 有効 |
| Claude Code デスクトップアプリ | ✅ 有効 |
| claude.ai/code（リモート操作） | ✅ 有効 |
| Claude.ai ブラウザ版 | ❌ 不可（ローカルコマンドが実行できないため） |

CLI・デスクトップ・リモート操作のいずれでも動作するので、普段の使い方を問わず設定しておく価値があります。

なお、**ブラウザ版（claude.ai）に通知を出したい場合**は、ブラウザの通知設定から許可が必要です。

1. claude.ai をブラウザで開く
2. アドレスバー左の 🔒 アイコン → 「通知」→「許可」
   - Safari の場合：設定 → Web サイト → 通知 → claude.ai を「許可」
3. Claude.ai の設定画面で通知項目を ON にする

※ブラウザ版では音声読み上げなどのカスタム通知は設定できません。

---

## カスタマイズ（macOS）

### 音声（ボイス）を変更する

利用可能なボイスの一覧は以下のコマンドで確認できます。

```bash
say -v ?
```

日本語ボイスの例：`Kyoko`（女性）、`Otoya`（男性）

### 読み上げ速度を変更する

`-r` オプションで1分あたりの単語数（wpm）を指定します。デフォルトは約 `175` です。

```bash
say -v Kyoko -r 120 '作業が完了したよ'  # ゆっくり
say -v Kyoko -r 175 '作業が完了したよ'  # 標準
say -v Kyoko -r 250 '作業が完了したよ'  # 速め
```

`settings.json` のコマンドに組み込む場合は `-r` を追加するだけです。

```json
"command": "osascript -e 'display notification \"作業が完了したよ\" with title \"Claude Code\"' 2>/dev/null; /usr/bin/say -v Kyoko -r 120 '作業が完了したよ' 2>/dev/null"
```

### 通知音を変更する

macOS 標準サウンドを試し聴きしてお気に入りを探す：

```bash
afplay /System/Library/Sounds/Hero.aiff
```

利用できるサウンド一覧（`/System/Library/Sounds/` 内）：

```
Basso, Blow, Bottle, Frog, Funk, Glass, Hero, Morse,
Ping, Pop, Purr, Sosumi, Submarine, Tink
```

通知音を鳴らしたい場合は、`say` の代わりに `afplay` を使うか、組み合わせることも可能です。

---

## カスタマイズ（Windows）

### インストール済みの音声ボイスを確認する

```powershell
Add-Type -AssemblyName System.speech
(New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }
```

日本語ボイスの例：`Microsoft Haruka Desktop`（女性）、`Microsoft Ichiro Desktop`（男性）

### 音声ボイスを変更する

特定のボイスを指定して読み上げる場合は、以下のように `SelectVoice` を使います。

```powershell
Add-Type -AssemblyName System.speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speak.SelectVoice('Microsoft Haruka Desktop')
$speak.Speak('作業が完了したよ')
```

`settings.json` のコマンドに組み込む場合：

```json
"command": "powershell -ExecutionPolicy Bypass -Command \"Add-Type -AssemblyName System.speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SelectVoice('Microsoft Haruka Desktop'); $s.Speak('作業が完了したよ')\""
```

### 読み上げ速度を変更する

`Rate` プロパティで速度を調整できます（`-10`：最遅 〜 `10`：最速、デフォルト：`0`）。

```powershell
$speak.Rate = -2  # 少しゆっくり
```

### BurntToast の通知音を変更する

`-Sound` オプションで通知音を指定できます。

```powershell
New-BurntToastNotification -Text 'Claude Code', '作業が完了したよ' -Sound IM
```

利用できる通知音：`Default`, `IM`, `Mail`, `Reminder`, `SMS`, `Alarm`, `Alarm2` など

---

## まとめ

- Claude Code の `Stop` と `PermissionRequest` フックで、完了通知・権限確認通知を自動化できる
- **macOS**: `osascript` + `say -v Kyoko` の組み合わせで、追加インストール不要ですぐ使える
- **Windows**: `SpeechSynthesizer`（依存なし）または `BurntToast`（トースト通知付き）で同等の機能を実現できる
- `async: true` を忘れずに付けることで、Claude の処理をブロックしない安全な設定になる

Claude Code を「走らせながら別作業する」スタイルに、ぜひ取り入れてみてください。

---

## 参考

- [Claude Code 公式ドキュメント — Hooks](https://docs.anthropic.com/ja/docs/claude-code/hooks)
- [Claude Code 設定リファレンス](https://docs.anthropic.com/ja/docs/claude-code/settings)
- [BurntToast - PowerShell Gallery](https://www.powershellgallery.com/packages/BurntToast)
- [Setting up Notification Sounds in Claude Code using Hooks on Windows (Zenn)](https://zenn.dev/is0383kk/articles/5d66a34b0a89be?locale=en)
