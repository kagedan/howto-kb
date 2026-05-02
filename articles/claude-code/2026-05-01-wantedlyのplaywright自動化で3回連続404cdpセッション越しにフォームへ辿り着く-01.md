---
id: "2026-05-01-wantedlyのplaywright自動化で3回連続404cdpセッション越しにフォームへ辿り着く-01"
title: "WantedlyのPlaywright自動化で3回連続404——CDPセッション越しにフォームへ辿り着くまでの1時間"
url: "https://zenn.dev/taito_ichinose/articles/ichinose-post-4486"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "Python", "zenn"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

⏱この記事は約 9 分で読めます

📖 目次

最終更新: 2026-04-28

スクリーンショットで状況が全部把握できた。記事を書く。

## 何が起きたか

WantedlyのプロフィールをPlaywright + CDPで自動入力しようとしたら、スクリプトが3回連続で404に飛ばされた。`/users/edit` を叩けばフォームに辿り着けると思っていたのに、「Oops… Error 404」ページが出るだけ。ログには正常終了と出ている。セッション切れか、URLが変わったか、それともサービス側の仕様変更か——原因の切り分けに1時間近く使った。

## 環境

* macOS Sequoia / MacBook Pro M5 32GB
* Python 3.12 + Playwright（CDP経由でBraveに接続）
* Claude Code でスクリプト生成・デバッグ
* Brave 起動: `launch_brave_debug.sh`（`--remote-debugging-port=9222`）
* Ollama（qwen3.5:9b）でログ要約

## 詰まったポイント

最初のエラーは単純に見えた。`page.goto("https://wantedly.com/users/edit")` → 404。「URLが古いんだろう」と思って `/users/me/edit` に変えても同じ。`/profile/edit` でも同じ。

スクリーンショットで確認したら、ページ自体はちゃんと読み込まれていた。Wantedlyのドメインに到達して、セッションも生きていて、それでも404。

URLの問題じゃなくて、「そのページはアカウントの状態的に存在しない」という判定をWantedly側がしているわけだ。

次に気づいたのが、初回ログイン後に必ずウィザードが挟まるという構造。「あなたの新しいIDを設定」という画面で、`wantedly.com/id/{ユーザー名}` 形式のURLを確定させないとプロフィール編集ページ自体が存在しない——という仕掛けだった。スクリプトはこのウィザードを完全に無視していた。

`goto` で編集ページに飛ぼうとしても、ウィザード未完了の状態だから弾かれる。当たり前なんだけど、ハードコードしたURLを叩けば直接行けるという思い込みが邪魔をしていた。

## 解決までの手順

**ステップ1: 遷移後のURLをログに残す**

`goto()` の直後に `page.url` を取る一行を入れた。これで「どこにリダイレクトされたか」が見えるようになった。

```
await page.goto("https://wantedly.com/", wait_until="domcontentloaded")
current_url = page.url
print(f"[debug] 遷移後URL: {current_url}")
```

**ステップ2: ウィザードの検出と通過ロジックを追加**

URLに `setup` が含まれるか、`h1` テキストで「IDを設定」が見えたらウィザードフローに入るようにした。

```
if "setup" in page.url o​r await page.locator("h1:has-text('IDを設定')").count() > 0:
    await handle_wizard(page)

async def handle_wizard(page):
    await page.wait_for_selector("button:has-text('次へ')", timeout=5000)
    await page.locator("button:has-text('次へ')").click()
    await page.wait_for_load_state("networkidle")
```

**ステップ3: ウィザード完了後のプロフィールURLを動的に取得**

ウィザードで設定したIDが `https://wantedly.com/id/{username}` になる。アカウントによって変わるので、完了後に `page.url` から抜き出す形にした。

```
await page.wait_for_url("**/id/**")
profile_url = page.url  # → https://wantedly.com/id/yasushi_tsuchiya_b
username = profile_url.rstrip("/").split("/")[-1]
```

**ステップ4: 編集ページへの遷移をURL直打ちからボタンクリックに変更**

`/users/edit` に直接 `goto` するのをやめて、プロフィールページを開いてから「プロフィール項目を追加・生成」ボタンを押す方式に切り替えた。これでウィザード済みかどうかに関係なく動くようになった。

```
await page.goto(profile_url)
await page.wait_for_load_state("domcontentloaded")
edit_btn = page.locator("text=プロフィール項目を追加・生成").first
await edit_btn.click()
```

**ステップ5: Reactフォームへの入力**

Coconalaのときと同じパターンが出た。`fill()` で値を入れてもReactコンポーネントに伝わらない。nativeセッター + `dispatchEvent` の組み合わせで解決。

```
await page.evaluate("""
    (args) => {
        const el = document.querySelector(args.selector);
        const setter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, 'value'
        );
        setter.set.call(el, args.value);
        el.dispatchEvent(new Event('input', { bubbles: true }));
    }
""", {"selector": "textarea[name='description']", "value": bio_text})
```

## コード／設定の抜粋

CDP接続の基本構成。Braveを `--remote-debugging-port=9222` で起動済み前提。

```
from playwright.async_api import async_playwright

async def connect_brave():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        return browser, page
```

定期実行を launchd に乗せる場合（環境パスは各自調整）:

```
ProgramArguments

    /u​sr/local/b​in/python3
    /path/to/wantedly_profile.py

EnvironmentVariables

    PATH
    /u​sr/local/bin:/u​sr/bin:/bin
```

## 試してわかったこと

Wantedlyは新規アカウントの場合、プロフィール編集ページへの直接 `goto` が機能しない。「ユーザーIDが確定していないとプロフィールURLが存在しない」という設計で、ウィザード未完了なら404が返ってくる。言われてみれば当然なんだけど、スクリプト側はその前提を完全に無視していた。

同じパターンはCoconaraでも出た。業務領域モーダルのフローがカテゴリによって「直接保存」と「次へ→追加」に分かれていて、想定外のルートに入って詰まった。サービスが「アカウントの状態に応じて画面フローを変える」設計になっていると、URLハードコードは弱い。

「現在地を確認してから次の手を決める」——`goto` 後に `page.url` を見るだけでかなり変わった。どのWebサービス自動化にも使える基本構造だと思う。

ReactアプリのnativeセッターパターンはCoconaraで実証済みで、今回もそのまま流用できた。「一度解決した詰まりは再利用できる」のが自動化ライブラリを蓄積していく理由だと改めて感じた。

## まとめ

新規Wantedlyアカウントは、プロフィール編集URLに直接 `goto` するより先にID設定ウィザードがある。

遷移後のURLを確認してウィザードを検出・通過する分岐を1つ入れるだけで動いた。

「今どこにいるか」を確認してから動くスクリプトは、アカウント状態に左右されずに壊れにくい。✨

📘 この記事のテーマをさらに深掘りした本

非エンジニアが1年で月10万円に到達した全パイプラインと失敗談

[Kindleで読む →](https://www.amazon.co.jp/dp/B0GX2ZV7DP?tag=taito2525-22)

一ノ瀬泰斗  
AI自動化エンジニア / Python個人開発者  
Claude Code × Ollama × launchd で SNS・ブログ・KDPを全自動化。実測データと失敗談を軸に、月5万円収益化のリアルな記録を発信中。

💬 **自動化の相談・小規模受託も受付中**：「launchd で毎朝 AI が動く仕組みを作りたい」「KDP の自動出版を組みたい」など、[X (@taito\_automate) の DM](https://x.com/taito_automate) からお気軽にどうぞ。

### 関連記事

## 関連記事

---

この記事はもともと私のブログで書いたものです。より詳しい実装例・失敗談はこちらで読めます。

👉 [WantedlyのPlaywright自動化で3回連続404——CDPセッション越しにフォームへ辿り着くまでの1時間](https://ichinose-taito.com/?p=4486)
