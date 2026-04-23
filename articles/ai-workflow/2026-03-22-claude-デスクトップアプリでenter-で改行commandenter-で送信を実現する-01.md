---
id: "2026-03-22-claude-デスクトップアプリでenter-で改行commandenter-で送信を実現する-01"
title: "Claude デスクトップアプリで「Enter で改行、Command+Enter で送信」を実現する"
url: "https://qiita.com/nate3870/items/51b196de9a07717d3952"
source: "qiita"
category: "ai-workflow"
tags: ["GPT", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## はじめに

Claude の Web 版を使っていたとき、Chrome 拡張機能「[ChatGPT Ctrl+Enter Sender](https://github.com/masachika-kamada/ChatGPT-Ctrl-Enter-Sender)」を愛用していた。Enter で改行、Ctrl+Enter で送信という操作に慣れると、もう Enter 一発送信には戻れない。

ところが Claude デスクトップアプリに移行したところ、Chrome 拡張機能は当然使えない。デスクトップアプリは Enter 単体でメッセージが送信されてしまうため、**長文を書いている途中で誤送信**してしまうことが何度かあった。

そこで、macOS のネイティブ機能だけを使って同等の動作を実現するツール **ClaudeRemap** を作成した。

---

## 作ったもの

**ClaudeRemap** — Claude デスクトップアプリ専用のキーボードリマッパー。

| キー操作 | 動作 |
| --- | --- |
| `Enter` | 改行 / IME 変換確定 |
| `Command + Enter` | メッセージ送信 |
| その他のアプリ使用中 | 全て素通り（影響なし） |

* Claude がフォアグラウンドのときのみ動作する
* Dock・メニューバーへの表示なし（完全バックグラウンド）
* 外部依存ゼロ（Swift + macOS 標準フレームワークのみ）

---

## 技術的な仕組み

### CGEventTap

macOS には **CGEventTap** という仕組みがあり、システム全体のキーイベントを横取り・変換できる。アクセシビリティ権限さえ付与されていれば、任意のキーイベントを監視・変換・破棄できる。

```
キー入力
  ↓
CGEventTap がイベントを捕捉
  ↓
Claude がアクティブか判定
  ↓
YES → Enter を Shift+Enter に変換（改行）
      Command+Enter を Enter に変換（送信）
NO  → 素通り
```

### IME 変換確定の扱い

日本語入力中の Enter（変換確定）を誤ってブロックしないよう、IME が生成したイベントかどうかを `eventSourceStateID` で判定している。ユーザーが物理キーを押したイベントは `sourceStateID = 1`（hidSystemState）になるのに対し、IME が内部的に生成するイベントは異なる値になる。

```
func isIMEEvent(_ event: CGEvent) -> Bool {
    return event.getIntegerValueField(.eventSourceStateID) != 1
}
```

### なぜ launchd ではなくログイン項目で自動起動するのか

最初は `launchd` での常駐を試みたが、launchd はGUIセッション外から起動するため、アクセシビリティ権限が正しく継承されず `CGEventTap` の作成に失敗した。macOS のログイン項目として登録することで、GUIセッション内で起動されるためアクセシビリティ権限が正常に機能する。

---

## 実装

### ソースコード（`claude_enter_remap.swift`）

```
import Cocoa
import CoreGraphics

// ─── 定数 ────────────────────────────────────────────────────────
let KEYCODE_ENTER: CGKeyCode = 36
let TARGET_APP = "Claude"

// ─── アクティブアプリ判定 ─────────────────────────────────────────
func isClaudeActive() -> Bool {
    guard let app = NSWorkspace.shared.frontmostApplication else { return false }
    return app.localizedName?.lowercased().contains(TARGET_APP.lowercased()) ?? false
}

// ─── IME生成イベント判定 ──────────────────────────────────────────
func isIMEEvent(_ event: CGEvent) -> Bool {
    return event.getIntegerValueField(.eventSourceStateID) != 1
}

// ─── イベントタップコールバック ───────────────────────────────────
func eventCallback(
    proxy: CGEventTapProxy,
    type: CGEventType,
    event: CGEvent,
    refcon: UnsafeMutableRawPointer?
) -> Unmanaged<CGEvent>? {

    guard type == .keyDown else { return Unmanaged.passRetained(event) }

    let keycode = CGKeyCode(event.getIntegerValueField(.keyboardEventKeycode))
    let flags   = event.flags
    let isCmd   = flags.contains(.maskCommand)
    let isShift = flags.contains(.maskShift)

    guard keycode == KEYCODE_ENTER else { return Unmanaged.passRetained(event) }
    guard isClaudeActive() else { return Unmanaged.passRetained(event) }
    if isIMEEvent(event) { return Unmanaged.passRetained(event) }
    if isShift && !isCmd { return Unmanaged.passRetained(event) }

    if isCmd {
        // Command+Enter → Commandフラグを除去（= 送信）
        event.flags = flags.subtracting(.maskCommand)
        return Unmanaged.passRetained(event)
    } else {
        // Enter単体 → Shift+Enter に変換（= 改行）
        event.flags = flags.union(.maskShift)
        return Unmanaged.passRetained(event)
    }
}

// ─── メイン ───────────────────────────────────────────────────────
func log(_ msg: String) {
    let fmt = DateFormatter()
    fmt.dateFormat = "yyyy-MM-dd HH:mm:ss"
    print("\(fmt.string(from: Date())) [INFO] \(msg)")
    fflush(stdout)
}

log("Claude Enter Remapper 起動中...")
log("監視対象アプリ: \(TARGET_APP)")
log("Enter → 改行 / Command+Enter → 送信 / IME確定 → 素通り (Claude アクティブ時のみ)")

let eventMask = CGEventMask(1 << CGEventType.keyDown.rawValue)

guard let tap = CGEvent.tapCreate(
    tap: .cgSessionEventTap,
    place: .headInsertEventTap,
    options: .defaultTap,
    eventsOfInterest: eventMask,
    callback: eventCallback,
    userInfo: nil
) else {
    fputs("EventTap の作成に失敗しました。\nシステム設定 → プライバシーとセキュリティ → アクセシビリティ\nにこのアプリを追加してください。\n", stderr)
    exit(1)
}

let runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, .commonModes)
CGEvent.tapEnable(tap: tap, enable: true)

log("起動完了。")

signal(SIGINT)  { _ in print("\nシャットダウン中..."); exit(0) }
signal(SIGTERM) { _ in exit(0) }

CFRunLoopRun()
```

---

## セットアップ手順

### 前提条件

Xcode Command Line Tools がインストールされていること。未インストールの場合は以下を実行する。

```
xcode-select --install

# バージョン確認
swift --version
# Apple Swift version X.X と表示されれば OK
```

### 1. プロジェクトフォルダの作成とソースファイルの配置

```
mkdir -p ~/path/to/your/project
# 上記のソースコードを claude_enter_remap.swift として保存する
```

### 2. アプリバンドルの作成

```
# バンドルディレクトリ作成
mkdir -p ~/Applications/ClaudeRemap.app/Contents/MacOS

# コンパイル
swiftc ~/path/to/your/project/claude_enter_remap.swift \
  -o ~/Applications/ClaudeRemap.app/Contents/MacOS/ClaudeRemap \
  -framework Cocoa \
  -framework CoreGraphics

# Info.plist 作成（LSUIElement=true でDock非表示）
cat > ~/Applications/ClaudeRemap.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleIdentifier</key>
  <string>com.local.claude-remap</string>
  <key>CFBundleName</key>
  <string>ClaudeRemap</string>
  <key>CFBundleExecutable</key>
  <string>ClaudeRemap</string>
  <key>LSUIElement</key>
  <true/>
</dict>
</plist>
EOF

# コード署名
codesign --force --deep --sign - ~/Applications/ClaudeRemap.app
```

### 3. アクセシビリティ権限の付与

CGEventTap の動作にはアクセシビリティ権限が必須である。

1. **システム設定 → プライバシーとセキュリティ → アクセシビリティ** を開く
2. `+` ボタンをクリックし、`Shift+Command+G` で `/Users/ユーザー名/Applications/` を入力
3. `ClaudeRemap.app` を選択して「開く」
4. トグルを **ON（オレンジ色）** にする

Homebrew 版 Python など、コード署名のないインタープリタを使った場合はこの権限付与が機能しない。Swift でネイティブバイナリとしてコンパイルすることで解決した。

### 4. ログイン項目への登録

1. **システム設定 → 一般 → ログイン項目と機能拡張** を開く
2. 「ログイン時に開く」の `+` をクリック
3. `ClaudeRemap.app` を追加する

### 5. 起動・動作確認

```
open ~/Applications/ClaudeRemap.app
```

Claude デスクトップアプリで以下を確認する。

* `Enter` → 改行される ✅
* 日本語変換中に `Enter` → 変換確定される ✅
* `Command + Enter` → メッセージ送信される ✅
* 他のアプリでは Enter の挙動が変わらない ✅

---

## 管理コマンド

```
# 起動
open ~/Applications/ClaudeRemap.app

# 停止
osascript -e 'quit app "ClaudeRemap"'

# ログをリアルタイム確認しながら起動
~/Applications/ClaudeRemap.app/Contents/MacOS/ClaudeRemap
```

---

## ハマりどころまとめ

実装中にいくつかハマった点を記録しておく。

### Homebrew Python では CGEventTap が使えない

Homebrew でインストールした Python はコード署名がないため、アクセシビリティ権限をシステムに認識させられない。最初は Python + pyobjc で実装しようとしたが、権限付与がどうしても効かず、Swift でのネイティブ実装に切り替えた。

### launchd では権限が継承されない

`launchd` の LaunchAgent として登録するとプロセスは起動するが、CGEventTap の作成に失敗し続けた。launchd はバックグラウンドのデーモン管理向けであり、GUIセッションのアクセシビリティ権限を引き継げないことが原因だった。macOS のログイン項目として登録する方式に変えることで解決した。

### IME 変換確定の Enter を誤ってブロックしない

単純に「Enter をすべてブロック→Shift+Enter に変換」としてしまうと、日本語入力の変換確定も一緒にブロックされてしまう。`eventSourceStateID` を使って IME 生成イベントを判別することで解決した。

---

## おわりに

Chrome 拡張機能が使えないデスクトップアプリでも、macOS の CGEventTap を使えば同等の体験を実現できる。今回は Claude 専用にしたが、`TARGET_APP` の値を変えるだけで他のアプリにも応用できる。

同じ悩みを持っている方の参考になれば幸いである。

---

## 参考
