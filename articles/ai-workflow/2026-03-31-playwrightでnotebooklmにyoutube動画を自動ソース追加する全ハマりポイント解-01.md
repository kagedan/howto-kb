---
id: "2026-03-31-playwrightでnotebooklmにyoutube動画を自動ソース追加する全ハマりポイント解-01"
title: "PlaywrightでNotebookLMにYouTube動画を自動ソース追加する【全ハマりポイント解説】"
url: "https://zenn.dev/ilumination1879/articles/17c16d55a4f4c7"
source: "zenn"
category: "ai-workflow"
tags: ["Python", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

# PlaywrightでNotebookLMにYouTube動画を自動ソース追加する

## はじめに

あるYouTuberの動画90本を、NotebookLMに古い順に連番付きでソース追加したい——そう思ったことはありませんか？

手作業でやると気が遠くなる作業です。そこでPlaywright（Pythonブラウザ自動化ライブラリ）を使って全自動化に挑戦しました。

しかし、NotebookLMはAngular製のSPAで独特のDOM構造を持ち、Googleログインはセキュリティ上の理由でPlaywrightのChromiumをブロックします。数多くのハマりポイントを乗り越えた実装記録を共有します。

---

## 完成したスクリプト構成

```
notebooklm連携/
├── step1_get_videos.py    # yt-dlpで動画一覧取得
├── step2_login.py         # Chromeでセッション保存（手動ログイン）
├── step3_add_sources.py   # NotebookLMへ自動追加・リネーム
├── videos.json            # 動画リスト
├── session.json           # Googleログインセッション
├── progress.json          # 途中再開用の進捗
└── requirements.txt
```

**実行手順:**

```
pip install -r requirements.txt
playwright install chromium

python step1_get_videos.py   # 動画一覧を取得
python step2_login.py        # 手動ログインしてセッション保存
python step3_add_sources.py  # 自動追加スタート（途中で止めても再開可）
```

---

## Step 1: yt-dlpで動画一覧を取得する

```
import yt_dlp
import json

CHANNEL_URL = 'https://www.youtube.com/@remote.kosuke/videos'

ydl_opts = {
    'extract_flat': 'in_playlist',
    'quiet': False,
    'ignoreerrors': True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(CHANNEL_URL, download=False)

entries = [e for e in info['entries'] if e is not None]

videos = []
for entry in entries:
    video_id = entry.get('id', '')
    videos.append({
        'id': video_id,
        'title': entry.get('title', ''),
        'upload_date': entry.get('upload_date', '00000000'),  # YYYYMMDD
        'url': f'https://www.youtube.com/watch?v={video_id}',
    })

# 古い順にソートして連番を付与
videos.sort(key=lambda x: x['upload_date'])
for i, v in enumerate(videos, start=1):
    v['index'] = i
    v['numbered_title'] = f"{i:02d} {v['title']}"

with open('videos.json', 'w', encoding='utf-8') as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)
```

これで `upload_date`（YYYYMMDD形式）を使った古い順のソートと、`01`, `02`, ... という連番付与ができます。

---

## ハマりポイント1: Googleログインがブロックされる

### 問題

PlaywrightのChromiumでNotebookLM（Googleアカウントが必要）にアクセスすると、Googleのログイン画面で「このブラウザはサポートされていません」「安全でない可能性があります」と弾かれます。

これはPlaywrightのChromiumが一般的なブラウザとして認識されないためです。

### 失敗したアプローチ

* `chromium.launch(channel='chrome')` → Chrome起動自体は成功するが、依然としてブロックされる
* `chromium.launch_persistent_context(user_data_dir=...)` → プロファイルがロック中でクラッシュ
* 既存Chromeプロファイルをそのまま使う → ロックファイルの競合

### 解決策: CDP接続でシステムChromeを使う

```
import subprocess
import time
from playwright.sync_api import sync_playwright

CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
TEMP_PROFILE = r'C:\Temp\chrome_notebooklm_profile'
DEBUG_PORT = 9222

# 既存のChromeプロセスを先に終了
subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
time.sleep(3)

# デバッグポート付きで専用プロファイルから起動
proc = subprocess.Popen([
    CHROME_PATH,
    f'--remote-debugging-port={DEBUG_PORT}',
    f'--user-data-dir={TEMP_PROFILE}',  # 専用の一時プロファイル
    '--no-first-run',
    '--no-default-browser-check',
    'https://notebooklm.google.com/',
])

# ポートが開くまで待機
time.sleep(5)

with sync_playwright() as p:
    # システムChromeにCDP接続
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    # ユーザーが手動でログインした後、セッションを保存
    context.storage_state(path='session.json')
```

**ポイント:**

* `subprocess.Popen` でシステムのChromeを `--remote-debugging-port=9222` 付きで起動
* `connect_over_cdp` でPlaywrightからCDPプロトコルで接続
* 接続URLは `localhost` ではなく `127.0.0.1` を使う（IPv6の解決順序の問題でlocalhostだと`::1`に解決されECONNREFUSEDになることがある）
* 専用の一時プロファイルディレクトリを使うとロック問題が起きない
* ユーザーが手動でログイン・2段階認証を完了した後、`storage_state()` でセッションを保存

この `session.json` を次のステップで使い回すことで、以降はPlaywright標準のChromiumでも認証済み状態で動かせます。

---

## ハマりポイント2: `networkidle` が永遠にタイムアウトする

### 問題

```
page.wait_for_load_state('networkidle', timeout=30000)
# → TimeoutError: Timeout 30000ms exceeded
```

### 原因

NotebookLMはAngular製SPAで、常にバックグラウンドで通信を続けています。`networkidle`（ネットワーク通信がない状態）には永遠になりません。

### 解決策

```
# NG
page.wait_for_load_state('networkidle', timeout=30000)

# OK
page.wait_for_load_state('domcontentloaded', timeout=30000)
time.sleep(3)  # Angular描画の完了を待つ
```

`domcontentloaded`（DOMの読み込み完了）で十分で、その後少しsleepしてAngularの描画を待ちます。

---

## ハマりポイント3: NotebookLMのソース追加UIフロー

UIを手動で確認してから実装することが重要です。2025年時点のフローは以下の通りです。

### 新規ノートブック作成

```
page.goto('https://notebooklm.google.com/')
page.wait_for_load_state('domcontentloaded', timeout=30000)
time.sleep(4)

btn = page.locator('button:has-text("新規作成")').first
btn.click()

page.wait_for_url('**/notebook/**', timeout=20000)
page.wait_for_load_state('domcontentloaded', timeout=30000)
time.sleep(5)
```

### ソース追加フロー

```
「+ ソースを追加」→「ウェブサイト」→ URL入力 →「挿入」
```

```
# 1. 「ソースを追加」をクリック
page.locator('button:has-text("ソースを追加")').first.click()
time.sleep(2)

# 2. 「ウェブサイト」をクリック
# ※ YouTube専用オプションはない。ウェブサイトからYouTube URLを貼るだけでOK
page.locator('button:has-text("ウェブサイト")').first.click()
time.sleep(1.5)

# 3. URLを入力
# ※ input ではなく textarea
inp = page.locator('textarea[placeholder*="リンクを貼り付ける"]').first
inp.fill(video_url)
time.sleep(1)

# 4. 「挿入」をクリック
page.locator('button:has-text("挿入")').last.click()

# ソース処理の完了を待つ（15秒未満だと次の操作がブロックされる）
time.sleep(15)
```

**注意点:**

* YouTube専用のソース追加オプションはない。「ウェブサイト」からYouTube URLを貼り付けるとYouTube動画として認識される
* URLの入力欄は `input` ではなく `textarea`
* 処理完了待ちは15秒必要（短すぎると次の追加がブロックされる）

---

## ハマりポイント4: ソースのリネーム——UIもセレクターも罠だらけ

これが最大の難所でした。

### 間違ったアプローチ1: 「...」ホバーメニューを探す

一般的なWebアプリのリネームUIを想像して `...` ボタンをホバーしようとしましたが、NotebookLMのUIは違います。

### 正しいUIフロー

```
ソース行の左端にあるYouTubeアイコン（赤いボタン）を直接クリック
→ コンテキストメニューが出る
→「ソース名を変更」をクリック
→ ダイアログが開く
→ 入力 →「保存」をクリック
```

### 間違ったアプローチ2: 標準セレクターが効かない

```
# NG - mat-list-item はDOMに存在しない
page.locator('mat-list-item').last.click()

# NG - data属性がない
page.locator('[data-source-id]').last.click()

# NG - notebook-source-list-item も効かない
page.locator('notebook-source-list-item').last.click()
```

NotebookLMのDOMはAngularのカスタムコンポーネントで構成されており、一般的なセレクターが通用しません。

### 解決策: JavaScriptの座標フィルタで探す

```
# YouTubeアイコンボタン（左端 x<60、svg/img持ち）を座標で絞り込む
# 最後に追加したソース（一番下のボタン）をクリック
clicked = page.evaluate("""
    () => {
        const btns = Array.from(document.querySelectorAll('button'))
            .filter(b => {
                const r = b.getBoundingClientRect();
                return r.left >= 0 && r.left < 60 &&
                       r.top > 150 && r.width > 5 && r.height > 5 &&
                       b.querySelector('img, svg, mat-icon');
            })
            .sort((a, b) => {
                const ra = a.getBoundingClientRect();
                const rb = b.getBoundingClientRect();
                return rb.top - ra.top;  // 下から上の順（最新が先頭）
            });

        if (btns.length === 0) return {ok: false};
        btns[0].click();
        return {ok: true, total: btns.length};
    }
""")
```

ソースパネルの左端（x < 60）にあり、svg/imgを含むボタン＝YouTubeアイコンボタンと特定。一番下（最後に追加）のものをクリックします。

### 間違ったアプローチ3: `fill()` がAngularに効かない

ダイアログが開いたら入力フィールドに新しい名前を入れる必要がありますが、`fill()` がうまく動きません。

```
# NG - Angularのchange detectionが発火しない
inp.fill('新しい名前')

# NG - mat-label はPlaywrightが認識しない
page.get_by_label('ソース名').fill('新しい名前')
```

### 解決策: `keyboard.type()` で直接入力

```
inp = page.locator('edit-source-dialog input').first
inp.wait_for(state='visible', timeout=5000)
inp.click()

# 全選択してから入力（Angularのchange detectionを正しく発火させる）
page.keyboard.press('Control+a')
page.keyboard.type(new_name)

page.get_by_role('button', name='保存').click(timeout=5000)
```

`inp.click()` でフォーカスを当ててから `Control+a` で全選択、`keyboard.type()` でキーイベントとして入力することでAngularのリアクティブフォームが正しく認識します。

**ダイアログのHTML構造**（DevToolsで確認）:

```
<edit-source-dialog>
  <form class="edit-source-dialog">
    <mat-form-field class="input-form-field">
      <input>  ← ここを操作する
    </mat-form-field>
  </form>
</edit-source-dialog>
```

セレクターは `page.locator('edit-source-dialog input').first` が正解です。

---

## ハマりポイント5: yt-dlpとNotebookLMでタイトルが違う

### 問題

yt-dlpで取得したタイトルは英語なのに、NotebookLMに追加すると日本語タイトルで表示されることがあります。

yt-dlpのタイトルでリネームすると、元の日本語タイトルが英語に変わってしまいます。

### 解決策: ダイアログの現在値を読んで連番だけ付ける

```
# NG - yt-dlpのタイトルで上書き
new_name = f"{index:02d} {video['title']}"  # 英語になってしまう

# OK - NotebookLMが表示している現在のタイトルに連番を付ける
current_title = inp.input_value()  # NotebookLMの（日本語の）タイトルを読む
new_name = f"{index:02d} {current_title}"
```

`input_value()` でダイアログに表示されている現在のタイトルを読み取り、その頭に連番を付けるだけにします。これでNotebookLMが独自に付けた日本語タイトルを保持できます。

---

## その他の実装ポイント

### 進捗の保存と途中再開

90本の動画追加には相当な時間がかかります。途中でエラーが起きても再開できるよう、`progress.json` に進捗を保存します。

```
def load_progress():
    if os.path.exists('progress.json'):
        with open('progress.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'added_indices': [], 'notebook_urls': []}

def save_progress(progress):
    with open('progress.json', 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

# 各動画処理後に保存
added_indices.add(idx)
progress['added_indices'] = list(added_indices)
save_progress(progress)
```

再実行すると `added_indices` に含まれる動画をスキップして続きから始まります。

### 1ノートブック50件上限の対処

NotebookLMは1ノートブックに追加できるソースが最大50件です。90本の動画を扱うには自動で2冊目を作成する必要があります。

```
MAX_SOURCES_PER_NOTEBOOK = 50

if sources_in_current >= MAX_SOURCES_PER_NOTEBOOK:
    # 新しいノートブックを作成して切り替え
    current_notebook_url = create_notebook(page, f"{NOTEBOOK_BASE_NAME} 2")
    sources_in_current = 0
```

---

## まとめ

| 問題 | 解決策 |
| --- | --- |
| Googleログインブロック | `subprocess`でシステムChromeを起動 → CDPで接続してセッション保存 |
| `localhost` ECONNREFUSED | `127.0.0.1` を使う（IPv6問題回避） |
| `networkidle` タイムアウト | `domcontentloaded` + sleepに変更 |
| ソース追加ボタンが見つからない | UIを手動で確認し日本語テキストのセレクターを使う |
| URLがtextarea | `textarea[placeholder*="リンクを貼り付ける"]` で対応 |
| ソースリネームのUI | `...`ホバーではなくYouTubeアイコン直接クリック |
| Angularのセレクター | 座標ベースのJavaScript評価で特定 |
| `fill()` がAngularに効かない | `click()` → `Control+a` → `keyboard.type()` |
| タイトルの言語ズレ | `input_value()` で現在値を読んで連番だけ付ける |

NotebookLMはAngular製SPAで独特の癖がありますが、DevToolsでHTML構造を確認しながら丁寧に対処すれば自動化できます。途中再開の仕組みを入れておくと長時間処理でも安心です。

---

## ソースコード

GitHubで公開しています。

<https://github.com/nykfsfs/notebooklm-automation>

ファイル構成:

* `step1_get_videos.py`: yt-dlpで動画一覧取得
* `step2_login.py`: Chromeデバッグモードでセッション保存
* `step3_add_sources.py`: NotebookLMへの自動追加・リネーム
* `requirements.txt`: 依存パッケージ

```
playwright>=1.40.0
yt-dlp>=2024.1.0
```
