---
id: "2026-05-27-毎朝7時に自動でaiがニュースを要約してくれる仕組みをvanilla-jsclaude-apigit-01"
title: "毎朝7時に自動でAIがニュースを要約してくれる仕組みをVanilla JS×Claude API×GitHub Actionsで作った"
url: "https://zenn.dev/sg5555/articles/47f7ad62820f52"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Python", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

## はじめに

「毎朝ニュースをチェックしたいけど、大量の記事から重要なものを選ぶのが面倒」という課題を解決するために、**完全自動のパーソナルニュースダイジェスト**を作りました。

毎朝7時にGitHub Actionsが起動し、約137記事を収集→Claude APIで要約→上位10件をWebアプリに配信する仕組みです。課金は発生しますが、1日の運用コストはClaude APIで数円程度。ゼロ操作で毎朝キュレーションされたニュースが届きます。

## 完成した姿

* **朝7時に自動更新**（GitHub Actions + Claude API）
* **137記事 → 上位10件**に自動絞り込み
* 気になった記事は**ワンタップで深掘り分析**
* **Supabaseで既読状態をデバイス間同期**
* **PWA対応**でスマホのホーム画面から起動

## 技術スタック

| 役割 | 技術 |
| --- | --- |
| フロントエンド | Vanilla HTML/CSS/JS |
| AI要約 | Claude API（claude-sonnet-4-6） |
| 自動実行 | GitHub Actions（cron: 毎朝22:00 UTC） |
| 既読同期 | Supabase |
| ホスティング | Vercel（静的配信） |

なぜVanilla JSか？ フレームワークを使うほどの複雑さがなく、ビルドなしで即デプロイできる手軽さを優先しました。

## アーキテクチャ

```
GitHub Actions（毎朝22:00 UTC = 7:00 JST）
  └─ scripts/fetch_and_summarize.py
       ├─ RSSフィード137件を並列取得
       ├─ Claude APIで各記事をスコアリング
       ├─ 上位10件を選定して要約生成
       ├─ public/news.json に書き出し
       └─ git commit & push → Vercelが自動デプロイ
```

Vercelは `public/` フォルダを静的配信するだけ。サーバーは持ちません。

## 実装のポイント

### 1. GitHub ActionsからClaude APIを呼ぶ

```
# .github/workflows/fetch-news.yml
- name: Run fetch and summarize
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: python scripts/fetch_and_summarize.py
```

GitHub Secretsにキーを入れるだけ。ローカルに`.env`を置く必要もなく、キーが漏れるリスクもありません。

```
import asyncio
import aiohttp

async def fetch_all(feeds):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url) for url in feeds]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

同期処理では137件のフェッチに数分かかりますが、非同期並列化で30秒程度に短縮しました。

### 3. Claudeへの依頼はバッチでまとめる

記事1件ずつAPIを叩くとAPI呼び出し回数が多くなりコストが増えます。記事をまとめてプロンプトに渡し、一度のAPI呼び出しでスコアリングと要約を生成します。

### 4. VercelのビルドコマンドにSupabase環境変数を注入

Vercelは静的配信のみなので、クライアントからSupabaseに接続するには環境変数をJSファイルに埋め込む必要があります。`package.json`のbuildCommandで`inject-env.js`を実行し、ビルド時にHTMLへ注入しています。

```
{
  "buildCommand": "node scripts/inject-env.js"
}
```

`package.json`がないとVercelがbuildCommandを認識できない点に注意（ハマりました）。

### 5. Service Workerでオフライン対応

```
// sw.js
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
```

朝のニュースは一度読み込んだらオフラインでも読めるようにキャッシュしています。

## ハマりポイント

**① `package.json` がないとVercelのbuildCommandが無視される**

Vercelは`package.json`が存在しない場合、静的ファイルとして扱い`buildCommand`を実行しません。Supabaseの環境変数注入スクリプトが動かず、長時間原因を調査しました。解決策は空の`package.json`でもいいので置くこと。

**② GitHub ActionsからのgitコミットにはGitHub Tokenが必要**

自動生成した`news.json`をコミットしてpushするには、GitHub Actionsの`GITHUB_TOKEN`を使った認証設定が必要です。

```
- name: Commit and push
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add public/news.json
    git commit -m "Update news $(date +'%Y-%m-%d')" || echo "No changes"
    git push
```

## まとめ

GitHub Actions × Claude API という組み合わせは「定期バッチ処理にAIを組み込む」用途に非常に相性が良く、サーバーを持たずに自動化ができます。ランニングコストも月数十円程度に収まっています。

「自分が欲しいものを作る」という原則で開発しましたが、同じ仕組みでSNS要約・論文ダイジェスト・株式ニュースのスクリーニングなど、応用範囲は広いと思います。

ソースコード: <https://github.com/sg55555/news-digest>
