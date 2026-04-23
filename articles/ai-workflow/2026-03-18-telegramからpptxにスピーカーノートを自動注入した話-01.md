---
id: "2026-03-18-telegramからpptxにスピーカーノートを自動注入した話-01"
title: "TelegramからPPTXにスピーカーノートを自動注入した話"
url: "https://zenn.dev/acropapa330/articles/zenn_article2"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

# TelegramからPPTXにスピーカーノートを自動注入した話

## はじめに

[前回の記事](https://zenn.dev/acropapa330/articles/zenn_article_telegtam_to_claude)では、Telegram Bot と Claude Agent SDK を連携させて、スマホから Claude に話しかけられる環境を構築しました。

今回はその環境を拡張して、**Google Drive にアップロードした PowerPoint ファイルにスピーカーノートを自動注入する機能**を実装しました。

プレゼン資料を作るたびに手動でノートを書いていた作業が、Telegram から数回操作するだけで完結するようになりました。

---

## 作ったもの

```
スマホ（Telegram）
    ↓ Google Drive のリンクを送る
Bot（Windows PC）
    ↓ ファイルをダウンロード
    ↓ スピーカーノートを注入
    ↓ Google Drive にアップロード
スマホ（Telegram）
    ← 処理済みPPTXのリンクが届く
```

### 使い方

1. Google Drive に PPTX をアップロードして共有リンクをコピー
2. Telegram の Bot にリンクを送る
3. ノートテキストを送る（以下の形式）

```
スライド1: ここで話す内容を書きます
スライド2: 次のスライドの説明
スライド3: まとめの話
```

4. 処理済み PPTX の Google Drive リンクが返ってくる

---

## 実装のポイント

### python-pptx でノートを注入する

`python-pptx` を使うとスライドのスピーカーノートを簡単に書き換えられます。

```
from pptx import Presentation

def inject_notes(pptx_path, notes, output_path):
    prs = Presentation(str(pptx_path))
    for i, slide in enumerate(prs.slides, start=1):
        if i in notes:
            slide.notes_slide.notes_text_frame.text = notes[i]
    prs.save(str(output_path))
```

`notes` は `{スライド番号: テキスト}` の辞書です。

### ノートテキストのパース

ユーザーが送ってくるテキストを正規表現でパースします。

```
import re

def parse_notes_text(text):
    notes = {}
    pattern = re.compile(
        r'スライド\s*(\d+)\s*[：:]\s*(.+?)(?=スライド\s*\d+\s*[：:]|\Z)',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        notes[int(m.group(1))] = m.group(2).strip()
    return notes
```

`[：:]` で全角・半角コロンの両方に対応しています。

### Google Drive との連携

Google Cloud Console でサービスアカウントを作成し、JSON キーを取得します。

```
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

def get_drive_service():
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json", scopes=scopes
    )
    return build("drive", "v3", credentials=creds)
```

**ダウンロード**はシンプルに `get_media` を使います。

```
def drive_download(file_id, dest_path):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    with open(dest_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
```

**アップロード**後は誰でも閲覧できるように共有設定します。

```
def drive_upload(file_path, filename):
    service = get_drive_service()
    file_metadata = {"name": filename, "parents": [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(str(file_path), mimetype=PPTX_MIME)
    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id, webViewLink"
    ).execute()
    service.permissions().create(
        fileId=uploaded["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()
    return uploaded["webViewLink"]
```

### MD5 キャッシュで再処理を防ぐ

同じ PPTX に同じノートテキストを何度も処理しないよう、MD5 ハッシュでキャッシュします。

```
def get_cache_path(pptx_path, notes_text):
    pptx_hash  = hashlib.md5(open(pptx_path, "rb").read()).hexdigest()
    notes_hash = hashlib.md5(notes_text.encode()).hexdigest()
    return CACHE_DIR / f"{pptx_hash}_{notes_hash}.pptx"
```

---

## 詰まったポイント

### Telegram の 20MB 制限

Telegram Bot API はファイルの送受信に 20MB の上限があります。21MB の PPTX を送ったら `BadRequest: File is too big` エラーが出ました。

対応策として、処理後のファイルは常に Google Drive にアップロードしてリンクを返す方式にしました。サイズを気にせず使えます。

### Google Drive URL の形式

Google Drive にアップロードした PPTX のリンクが `docs.google.com/presentation/...` という形式になっていて、`drive.google.com` だけを見ていたため検出できませんでした。

```
def is_drive_url(text):
    return "drive.google.com" in text or "docs.google.com" in text
```

両方を判定するようにして解決しました。

---

## 追加したコマンド

| コマンド | 機能 |
| --- | --- |
| `/slides` | 受信中 PPTX のスライド一覧とタイトルを表示 |
| `/preview N` | スライド N の現在のノートを確認 |
| `/cancel` | PPTX 待ち状態をキャンセル |
| `/cache` | キャッシュの件数とサイズを確認 |
| `/clearcache` | キャッシュを全削除 |

---

## 必要なライブラリ

```
pip install python-pptx google-auth google-auth-httplib2 google-api-python-client
```

---

## まとめ

* `python-pptx` でスピーカーノートの注入は数行で実装できる
* Google Drive API のダウンロードは PPTX なら `get_media`、Google Slides 形式なら `export_media`
* Telegram の 20MB 制限は Google Drive 経由で回避できる
* MD5 キャッシュで同じ処理の繰り返しを防げる

次回は**自作スケジューラと Brave Search API を使って毎朝 AI テックニュースを自動配信する仕組み**を紹介します。
