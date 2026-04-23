---
id: "2026-03-17-スマホの-telegram-から-claude-に話しかけられる環境を自作した-01"
title: "スマホの Telegram から Claude に話しかけられる環境を自作した"
url: "https://zenn.dev/acropapa330/articles/zenn_article_telegtam_to_claude"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

# スマホの Telegram から Claude に話しかけられる環境を自作した

## はじめに

「スマホから Claude に指示を送れたら便利じゃないか？」

そんな思いつきから始まり、気づいたら Google Drive との PPTX 連携まで実装していました。本記事では、**Telegram Bot × Claude Agent SDK** を Windows PC 上に構築した手順と、その途中で詰まったポイントを丁寧に紹介します。

プログラミング経験はあるけど Claude Agent SDK は初めて、という方を想定して書いています。

---

## 完成したシステムの概要

最終的に以下のことができる環境が完成しました。

* スマホの Telegram から Claude と自然言語で会話できる
* Google Drive にアップした PPTX の共有リンクを送ると、スピーカーノートを注入して返してくれる
* PC 起動時にバックグラウンドで自動起動する

全体の構成はシンプルです。クラウドサーバーは不要で、自宅の Windows PC が常時起動していれば動きます。

```
スマホ（Telegram アプリ）
        ↕ メッセージ送受信
Telegram Bot API サーバー
        ↕ Webhook / Polling
Windows PC（bot.py 常駐）
        ↕ Claude Agent SDK
Claude（Pro/Max サブスク）
        ↕ ファイルの受け渡し
Google Drive
```

---

## Claude Agent SDK とは

Claude Code の中核エンジンを、Python や TypeScript のコードから使えるようにした SDK です。

特徴として以下のビルトインツールが最初から使えます。

* **Read / Write / Edit** — ファイルの読み書き
* **Bash** — ターミナルコマンドの実行
* **Glob / Grep** — ファイル検索
* **WebSearch / WebFetch** — Web 検索・取得

そして最大のポイントは、**Claude Pro/Max サブスクリプション（月額 $20〜）があれば API キーなしで使える**ことです。個人で試す分には追加費用なしで動かせます。

```
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="今日の東京の天気を教えて",
    options=ClaudeAgentOptions(
        allowed_tools=["WebSearch", "WebFetch"],
    ),
):
    if hasattr(message, "result") and message.result:
        print(message.result)
```

たったこれだけで Web 検索をしながら回答してくれます。

---

## 環境構築の手順

### 1. Node.js のインストール

Claude Code CLI は Node.js が必要です。[nodejs.org](https://nodejs.org) から LTS 版をダウンロードします。

インストーラー実行時に **「Add to PATH」のチェックを必ずオンのまま** にしてください。これを忘れると後でコマンドが見つからないエラーになります。

```
node --version
# v24.x.x と表示されれば OK
```

### 2. Claude Code のインストールとログイン

```
npm install -g @anthropic-ai/claude-code
claude --version
# 2.x.xx (Claude Code) と表示されれば OK
```

ログインします。

```
mkdir c:\work\ClaudeAgentBot
cd c:\work\ClaudeAgentBot
claude login
```

ブラウザが開くので、claude.ai の Pro/Max アカウントで「承認」を押します。ログイン方法の選択肢が出たら **「1. Claude account with subscription」** を選びましょう。

### 3. Python のインストール

[python.org](https://www.python.org/downloads/) から最新版をダウンロードします。インストール時に **「Add python.exe to PATH」に必ずチェック** を入れてください。

```
python --version
# Python 3.x.x と表示されれば OK
```

### 4. 仮想環境とライブラリのセットアップ

```
cd c:\work\ClaudeAgentBot
python -m venv venv
venv\Scripts\activate
pip install python-telegram-bot claude-agent-sdk python-pptx
```

### 5. Telegram Bot の作成

1. Telegram で **@BotFather** を検索して開く
2. `/newbot` と送信してBot名とユーザー名を設定
3. 発行される **Bot Token** をメモ

自分の **Telegram User ID** も必要です。**@userinfobot** に `/start` と送ると数字のIDが返ってきます。

---

## bot.py の実装

### 基本構造

メッセージの処理は以下の優先順位で行います。この順番が重要で、後述のトラブルの原因にもなりました。

```
async def handle_message(update, context):
    # 1. PPTX 待ち状態ならノート処理
    if user_id in user_state:
        ...
        return

    # 2. Google Drive リンクを検出
    if "drive.google.com" in text or "docs.google.com" in text:
        ...
        return

    # 3. それ以外は Claude Agent SDK に流す
    async for message in query(prompt=text, ...):
        ...
```

### PPTX スピーカーノートの注入

`python-pptx` を使うとスライドのノートを簡単に書き換えられます。

```
from pptx import Presentation

def inject_notes(pptx_path, notes, output_path):
    prs = Presentation(str(pptx_path))
    for i, slide in enumerate(prs.slides, start=1):
        if i in notes:
            slide.notes_slide.notes_text_frame.text = notes[i]
    prs.save(str(output_path))
```

ユーザーからは以下の形式でノートテキストを受け取ります。

```
スライド1: ここで話す内容を書きます
スライド2: 次のスライドの説明
スライド3: まとめの話
```

### キャッシュの仕組み

同じ PPTX に同じノートを何度も処理しないように、MD5 ハッシュでキャッシュします。

```
pptx_hash  = hashlib.md5(open(pptx_path, "rb").read()).hexdigest()
notes_hash = hashlib.md5(notes_text.encode()).hexdigest()
cache_path = CACHE_DIR / f"{pptx_hash}_{notes_hash}.pptx"

if cache_path.exists():
    # キャッシュから返す
```

---

## Google Drive 連携

### サービスアカウントの準備

1. [Google Cloud Console](https://console.cloud.google.com) でプロジェクトを作成
2. Google Drive API を有効化
3. サービスアカウントを作成して JSON キーをダウンロード
4. `credentials.json` として `c:\work\ClaudeAgentBot\` に保存
5. Google Drive にフォルダを作成し、サービスアカウントの `client_email` と共有（編集者権限）

### ライブラリのインストール

```
pip install google-auth google-auth-httplib2 google-api-python-client
```

### Drive からのダウンロード

```
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def drive_download(file_id, dest_path):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    with open(dest_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
```

### Drive へのアップロード

処理後の PPTX は常に Google Drive にアップロードしてリンクを返す方式にしました。Telegram の 20MB 制限を気にしなくて済むためです。

```
def drive_upload(file_path, filename):
    service = get_drive_service()
    file_metadata = {"name": filename, "parents": [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(str(file_path), mimetype=PPTX_MIME)
    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id, webViewLink"
    ).execute()

    # 誰でも閲覧できるように共有設定
    service.permissions().create(
        fileId=uploaded["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return uploaded["webViewLink"]
```

---

## 詰まったポイントと解決策

### ① Telegram の 20MB 制限

PPTX（21MB）を送ったら盛大にエラーが出ました。

```
telegram.error.BadRequest: File is too big
```

Telegram Bot API は 20MB が上限で、これは仕様上変えられません。ファイル受信前にサイズチェックを入れて、超えている場合は Google Drive リンクで送るよう案内するようにしました。

```
if doc.file_size and doc.file_size > 20 * 1024 * 1024:
    await update.message.reply_text(
        "20MB を超えています。Google Drive の共有リンクを送ってください。"
    )
    return
```

### ② Google Drive ダウンロード方式の沼

これが今回最も手こずった部分です。試行錯誤の記録を残しておきます。

| 試行 | 方法 | 結果 |
| --- | --- | --- |
| 1回目 | `docs.google.com` URL の検出なし | Claude が WebFetch しようとして失敗 |
| 2回目 | URL判定追加 + `export_media` | `Export only supports Docs Editors files` |
| 3回目 | `get_media` に戻す | `Got an unexpected keyword argument mimeType` |
| 4回目 | `get_media(fileId=file_id)` のみ | ✅ 成功！ |

**ポイント：**

* `export_media` は Google Slides 形式（Google がホストしているファイル）専用
* PPTX のまま Drive にアップロードしたファイルは `get_media` を使う
* `get_media` に余計な引数を渡してはいけない

最終的にはシンプルなコードで動きました。回り道でしたが、Drive API の仕組みがよく理解できました。

### ③ `/restart` が Windows で動かない

`os.execv` は Linux 専用のシステムコールで、Windows では動作しません。

```
# NG（Linux 専用）
os.execv(sys.executable, [sys.executable] + sys.argv)

# OK（Windows 対応）
import subprocess
subprocess.Popen(
    [sys.executable, "bot.py"],
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)
os._exit(0)
```

新しいプロセスを起動してから自分を終了する方式に切り替えて解決しました。

### ④ Drive URL が Claude に流れてしまう

Google Drive のリンクを送ったら、Claude が「I'm unable to directly access that Google Slides link...」と返してきました。

原因はメッセージハンドラの処理順の問題で、Drive URL の判定より先に Claude Agent SDK に流れていたためです。

また URL の形式も落とし穴でした。Drive にアップした PPTX のリンクが `docs.google.com/presentation/...` という形式になっており、`drive.google.com` だけを見ていたため検出できていませんでした。

```
# NG
if "drive.google.com" in text:

# OK
if "drive.google.com" in text or "docs.google.com" in text:
```

---

## PC 起動時の自動起動設定

### start\_bot.vbs の作成

コマンドプロンプトが一瞬も表示されない完全バックグラウンド起動には VBScript を使います。

```
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d c:\work\ClaudeAgentBot && venv\Scripts\activate && pythonw bot.py", 0, False
```

### タスクスケジューラへの登録

1. スタートメニューで「タスクスケジューラ」を開く
2. 「タスクの作成」をクリック
3. **全般タブ**：名前を `TelegramClaudeBot` に設定
4. **トリガータブ**：「ログオン時」を選択
5. **操作タブ**：`start_bot.vbs` のパスを設定
6. **条件タブ**：「AC電源のみ」のチェックを外す

これで PC を起動してログインすれば自動で Bot が立ち上がります。

---

## 実装したコマンド一覧

| コマンド | 機能 |
| --- | --- |
| `/help` | コマンド一覧を表示 |
| `/ping` | Bot の死活確認 |
| `/status` | 現在の状態確認 |
| `/cancel` | PPTX 待ち状態をキャンセル |
| `/slides` | 受信中 PPTX のスライド一覧 |
| `/preview N` | スライド N の現在のノートを確認 |
| `/files` | ファイル一覧 |
| `/clean` | 一時ファイルを削除 |
| `/cache` | キャッシュ情報 |
| `/clearcache` | キャッシュを全削除 |
| `/log` | 直近のエラーログ |
| `/restart` | Bot を再起動 |

---

## やってみた感想

Google Drive のリンクを送ったときに「ダウンロード完了（14枚）」と返ってきた瞬間が一番うれしかったです。それまで何度もエラーと格闘していたので、あっさり動いたときの達成感は格別でした。

Claude Agent SDK は「Claude に手足を生やす」感覚で、テキスト生成だけでなく実際にファイルを操作したり Web を検索したりしてくれるのが頼もしいです。

今回は PPTX のスピーカーノート注入がメインでしたが、同じ仕組みで他のパイプラインにも応用できそうです。

---

## まとめ

| ステップ | 難易度 | 備考 |
| --- | --- | --- |
| Claude Code インストール | ★☆☆ | Node.js の PATH 設定を忘れずに |
| Telegram Bot 作成 | ★☆☆ | @BotFather で数分で完了 |
| Claude Agent SDK 連携 | ★☆☆ | コードがシンプルで驚いた |
| Google Drive 連携 | ★★★ | API の仕様理解に時間がかかった |
| Windows 自動起動 | ★★☆ | VBScript を使えばスッキリ |

Claude と一緒に実装を進めていくスタイルで、詰まっても「このエラーどういう意味？」と聞きながら進められたのがよかったです。同じことをやりたい方の参考になれば幸いです。
