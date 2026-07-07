---
id: "2026-07-07-布団の中でフルスタック開発したいclaude-code-on-the-web-vercel-supa-01"
title: "布団の中でフルスタック開発したい：Claude Code on the web × Vercel × Supabase × Doppler"
url: "https://zenn.dev/titabash/articles/1982c4e5e7739f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "Python", "zenn"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

## はじめに

最近、フルスタックアプリ開発の体験がかなり変わってきたなと感じています。

少し前まで「スマホで開発する」と言うと、GitHubのPRを見たり、軽くレビューコメントを返したりするくらいのイメージでした。

でも今は、**Claude Code on the web** でGitHub上のリポジトリを直接触り、**Vercel Preview Deployment** で確認し、**Supabase** でDB/Authを持ち、**Doppler** で環境変数を管理する、という構成がかなり現実的になってきています。

このあたりが噛み合うと、もう普通に、

> 布団の中でスマホを触りながら、フルスタックアプリの修正を入れて、Preview環境で確認する

みたいなことができます。

この記事では、**Claude Code on the web × Vercel × Supabase × Doppler** を組み合わせて、PCを開かなくてもフルスタック開発を前に進めやすくする構成について書きます。

なお、**Vercel Services** / **Vercel Container Images** はbetaで、僕自身もこれから本格的に試していく段階です。この記事は「完全運用済みの構成紹介」というより、**Claude Code on the web時代にかなり良さそうな構成の整理**です。

## 何が嬉しいのか

一番嬉しいのは、**実装から確認までのループがクラウド上で回る**ことです。

従来は、

```
Frontend: Vercel
Backend: Railway / Render / Fly.io など
DB/Auth: Supabase
Secrets: .env や各PaaSの環境変数
```

のように、環境が分かれがちでした。

もちろんこれでも動きます。

ただ、Claude Code on the webのようなクラウド上のAI開発環境を中心に置くなら、frontend、backend、Preview環境、環境変数、DB/Auth連携はできるだけ近い場所で扱える方が楽です。

そこで気になっているのが、[Vercel Services](https://vercel.com/docs/services) と [Vercel Container Images](https://vercel.com/docs/functions/container-images) です。

Vercel Servicesは、1つのVercel Project内に複数のfrontend/backend serviceをdeployできる仕組みです。公式ドキュメントでは、Next.js frontendとFastAPI backendを同じrepository内でdeployし、routing、environment variables、domainを共有できると説明されています。

さらに、Vercel Container Imagesでは、`Dockerfile.vercel` または `Containerfile.vercel` を置くことで、Vercel Functions上でOCI互換のcontainer imageを実行できます。

つまり、Next.jsだけでなく、FastAPIやGoなどのbackendもVercel側に寄せられる可能性が出てきています。

## 目指したい構成

ざっくり構成はこんな感じです。

使うものを整理するとこうです。

| 領域 | 使うもの |
| --- | --- |
| AI開発環境 | Claude Code on the web |
| Repository | GitHub |
| Frontend | Next.js |
| Backend | FastAPI / Go / Node.jsなど |
| Backend実行環境 | Vercel Services / Container Images |
| DB / Auth / Storage | Supabase |
| Secret管理 | Doppler |
| Preview / Deploy | Vercel |
| 簡易E2E確認 | Playwright |

この構成のポイントは、**GitHub PRを中心に開発ループが回る**ことです。

Claude Code on the webで実装する。  
PRを作る。  
Vercel Previewが立つ。  
必要ならClaude Code on the webからPlaywrightでPreview URLを確認する。  
人間もスマホでPreviewを見る。  
問題があれば、そのままClaudeに戻す。

このループが作れると、かなり開発体験が変わります。

## Vercel Servicesでfrontend/backendを同じProjectに寄せたい

Vercel Servicesを使うと、1つのVercel Project内に複数のserviceを定義できます。

たとえば、こんなモノレポ構成です。

```
.
├── frontend/
│   └── Next.js app
└── backend/
    └── FastAPI app
```

`vercel.json` でservicesを定義し、`/api/*` はbackendへ、それ以外はfrontendへ流すようにします。

```
{
  "services": {
    "frontend": {
      "root": "frontend/"
    },
    "backend": {
      "root": "backend/",
      "entrypoint": "main:app"
    }
  },
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": {
        "service": "backend"
      }
    },
    {
      "source": "/(.*)",
      "destination": {
        "service": "frontend"
      }
    }
  ]
}
```

[Vercel Servicesの公式ドキュメント](https://vercel.com/docs/services) では、すべてのserviceは同じdeploymentを共有すると説明されています。

つまり、Preview Deploymentが立つと、そのdeploymentの中にfrontend serviceとbackend serviceをまとめて載せられる構成が取れます。

たとえば、Preview URLが以下だったとします。

```
https://my-app-git-feature-xxx.vercel.app
```

このとき、

```
/       → frontend service
/api/*  → backend service
```

のようにroutingできれば、同じPreview URLでfrontend/backend込みの動作確認ができます。

これはClaude Code on the webとの相性がかなり良いです。

Claudeに実装させる。  
PRができる。  
Vercel Previewが立つ。  
Preview URLでfrontend/backend込みで確認する。  
ダメならまたClaudeに修正させる。

このループがかなり回しやすくなります。

## Dockerfile.vercelでbackendを提供したい

さらに気になっているのが、`Dockerfile.vercel` です。

[Vercel Container Images](https://vercel.com/docs/functions/container-images) では、project rootに `Dockerfile.vercel` または `Containerfile.vercel` を置くと、Vercelが自動検出してcontainer imageとしてbuild・deployできます。

Servicesと組み合わせる場合、frontend/backendそれぞれのserviceに `Dockerfile.vercel` を置くこともできます。

```
{
  "services": {
    "frontend": {
      "root": "frontend/",
      "entrypoint": "Dockerfile.vercel"
    },
    "backend": {
      "root": "backend/",
      "entrypoint": "Dockerfile.vercel"
    }
  }
}
```

たとえばFastAPI backendなら、イメージとしてはこんな感じです。

```
FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

実際にはproject構成に合わせて調整が必要ですが、重要なのは、**backendの実行環境までrepositoryに閉じ込められる**ことです。

これがClaude Code on the webと相性が良いです。

Claudeに、

* backendの実装を直して
* `Dockerfile.vercel` も必要なら調整して
* `vercel.json` のroutingも見て
* Previewで動くようにして

と依頼しやすくなります。

ここはまだこれから試す部分ですが、かなり期待しています。

## SupabaseとVercel Previewを噛み合わせる

Supabaseは、Postgres、Auth、Storage、Edge Functions、Realtimeをまとめて扱えるので、フルスタックアプリの土台としてかなり便利です。

ここで重要なのが、SupabaseとVercelの連携です。

[Vercel MarketplaceのSupabase連携](https://vercel.com/marketplace/supabase) では、Supabase projectの環境変数をVercel projectsへ自動同期したり、Supabase Preview branchesにredirect URLを自動作成したりできます。

Preview環境でよくあるつらみとして、

```
- frontend previewは立っている
- でもbackendはstagingを見る
- DBもstaging共有
- Auth redirect URLが合わない
- 環境変数の向き先がズレる
```

みたいなものがあります。

これだと、せっかくPRごとにPreviewが立っても、結局ちゃんと検証できません。

Vercel Preview Deployment、Supabase連携、Dopplerの環境変数管理が噛み合うと、PRごとの検証環境がかなり使いやすくなるはずです。

## Dopplerがかなり重要

この構成で一番の肝はDopplerです。

特に重要なのは、**Claude Code on the webの開発環境にDoppler Service Tokenを `DOPPLER_TOKEN` として設定しておく**ことです。

ここで使うべきなのは、Personal Access Tokenではなく、基本的には **Doppler Service Token** です。

[DopplerのService Token](https://docs.doppler.com/docs/service-tokens) は、特定project / configのsecretsにアクセスするためのtokenです。個人アカウントに広く紐づくtokenを渡すのではなく、対象configにscopeを絞ったService Tokenを使うのが重要です。

たとえばDoppler側で、configをこう分けます。

そして、それぞれのconfigに対してService Tokenを発行します。

```
DOPPLER_TOKEN=dp.st.dev.xxxx
DOPPLER_TOKEN=dp.st.stg.xxxx
DOPPLER_TOKEN=dp.st.prd.xxxx
```

Claude Code on the webの開発環境には、基本的に **dev config用のService Token** を `DOPPLER_TOKEN` としてセットします。

そしてコマンド実行時に `doppler run` を使います。

```
doppler run -- npm run dev
```

backendなら、たとえばこうです。

```
doppler run -- uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Claude Code on the webに大量の `.env` を貼り付ける必要はありません。

渡すのは、対象configに絞ったService Tokenだけ。  
実際のsecretのsource of truthはDopplerに置いたまま、`doppler run` 経由で必要な環境変数を読み込む。

この形がかなり扱いやすいです。

## DopplerからVercel Previewにも注入できる

DopplerはVercel integrationも提供しています。

[DopplerのVercel連携ドキュメント](https://docs.doppler.com/docs/vercel) では、VercelのDevelopment、Preview、Productionそれぞれのenvironmentごとにintegrationを作り、Vercel project、Vercel environment、Doppler configを選んでsyncできると説明されています。

つまり、こんな対応ができます。

```
Doppler dev → Vercel Development
Doppler stg → Vercel Preview
Doppler prd → Vercel Production
```

[Vercelの環境変数ドキュメント](https://vercel.com/docs/environment-variables) によると、Preview環境変数はproduction branch以外のbranchから作られるPreview Deploymentに適用されます。また、Preview環境変数は全Preview branch向けにも、特定branch向けにも設定できます。

ただし、DopplerのVercel integrationで公式に確認できるのは、基本的には、

```
Doppler config ↔ Vercel environment
```

のsyncです。

なので、まずは以下のように考えるのが安全そうです。

```
Claude Code on the web → Doppler dev
Vercel Preview         → Doppler stg
Vercel Production      → Doppler prd
```

branchごとに細かくDoppler configを自動で切り替える構成は、別途検証したいです。

## 最終的にはPreview環境で見ればいい

大事なのは、Claude Code on the web上で完璧にすべてを完結させようとしないことです。

実装はClaude Code on the webにかなり任せる。  
でも、最終的に正しく動いているかはVercel Previewで見る。

この分担がちょうどいいと思っています。

たとえば、Claude Code on the webに、

> この画面からbackend APIを叩いて、Supabaseに保存できるようにして

と依頼します。

Claudeがfrontend、backend、必要なら `vercel.json` や `Dockerfile.vercel` まで修正します。

その後、PRを作るとVercel Preview Deploymentが立ち上がります。

そこで実際にブラウザやスマホから触ってみる。

もし画面でエラーが出たら、そのエラーメッセージやスクリーンショット、Networkタブの情報、VercelのログをClaude Code on the webに渡して、

> Previewでこのエラーが出ているので直して

と頼めばいい。

AIに全部を一発で正しく作らせる必要はありません。

人間がPreview環境で触って、違和感やエラーを見つけて、それをClaudeに戻す。  
このループをどれだけ軽く回せるかが大事です。

## Playwrightで簡単なE2E確認まで回せる

さらに、この構成だと簡単なE2E確認もClaude Code on the webに任せやすくなります。

Vercel Preview URLが立っていれば、Claude Code on the webからPlaywrightを使って実際の画面を開き、最低限の動作確認をしてもらえます。

たとえば、

> Preview URLをPlaywrightで開いて、ログイン画面が表示されるか確認して  
> 主要なボタンを押して、画面遷移が壊れていないか見て  
> エラーが出ていたらスクリーンショットを取って原因を調べて

みたいな依頼ができます。

もちろん、本格的なE2Eテストスイートを全部AIに丸投げするという話ではありません。

ただ、UIの軽い確認や、画面が真っ白になっていないか、主要な導線が壊れていないか、APIエラーが出ていないか、くらいの確認にはかなり向いています。

人間が毎回Preview URLを開いて細かく確認する前に、Claude側でざっくり画面を触ってもらう。

これができると、UIのサクッとした修正や確認はかなり進めやすくなります。

## 寝ながらでも開発ループが回る

この構成が整うと、開発できる場所がかなり自由になります。

たとえば、布団の中でスマホを触りながら、

```
1. Claude Code on the webを開く
2. 修正内容を投げる
3. Claudeがfrontend/backendを修正する
4. 必要ならDockerfile.vercelやvercel.jsonも直す
5. PRを作る
6. Vercel Previewが立つ
7. ClaudeがPlaywrightで軽く確認する
8. スマホでPreview URLを開いて確認する
9. 追加修正をまたClaudeに投げる
```

みたいなことができます。

電車の中でも同じです。

ちょっとしたUI修正、APIの軽微な修正、型エラー修正、環境変数の不足確認、Previewでの動作チェックくらいなら、PCを開く前にかなり進められます。

今までは、外出中に「あ、ここ直したいな」と思っても、

> あとでPC開いたらやろう

になりがちでした。

でもこの構成だと、その場でClaude Code on the webに投げられます。

しかも、ただコードを書くだけではなく、Preview環境で実際に確認できます。

これがかなり大きいです。

## まだ検証したいところ

Vercel Services / Container Imagesについては、まだこれからちゃんと試したいところもあります。

具体的には、このあたりです。

```
- Servicesでfrontend/backendを同じPreview Deploymentに載せたときの実際の挙動
- /api/* rewriteでbackendに流す構成の使い勝手
- Service Bindingsの開発体験
- Dockerfile.vercelでFastAPI backendを動かすときの起動体験
- Doppler → Vercel Preview syncとの相性
- Supabase Preview branchesとの組み合わせ
```

この記事では「この構成がもう完全に完成している」と言いたいわけではありません。

むしろ、

> Claude Code on the web中心の開発体験を考えると、Vercel Services / Container Images / Supabase / Dopplerの組み合わせがかなり良さそう

という話です。

## セキュリティ面で気をつけること

Claude Code on the webに環境変数を渡すときは慎重にした方がいいです。

おすすめは以下です。

```
- .envをそのまま貼らない
- production secretを普段の開発環境に渡さない
- Doppler Service Tokenを使う
- dev / stg / prdでconfigを分ける
- 必要なconfigにだけaccessできるtokenを使う
- tokenは定期的にrotateする
```

Claude Code on the webの開発環境に渡すなら、基本はdev configのService Token。

staging / productionはdeploy環境側で扱う。

この分離が大事です。

## まとめ

Claude Code on the web、Vercel Services、Vercel Container Images、Supabase、Dopplerを組み合わせると、PCを開かなくてもフルスタックアプリ開発をかなり前に進められるようになりそうです。

ポイントはこのあたりです。

```
Claude Code on the web
→ GitHub上で実装する

Vercel Services
→ frontend/backendを1つのProjectで扱う

Dockerfile.vercel
→ backend実行環境をcontainerとして定義する

Supabase
→ DB/Auth/Storageを担当する

Doppler Service Token
→ Claude Code on the webにDOPPLER_TOKENとして渡す

Doppler Vercel Integration
→ Vercel Preview / Productionにsecretsをsyncする

Playwright
→ Preview URLで簡単なE2E確認とスクショ取得を行う
```

これにより、

```
実装する
↓
PRを作る
↓
Preview環境が立つ
↓
Playwrightで軽く確認する
↓
スマホで確認する
↓
追加修正する
```

というループがかなり回しやすくなります。

「AIがコードを書いてくれる」だけではなく、**AIが書いたコードをすぐにPreview環境で確認できる**ところまでクラウド側に寄ってきているのが大きいです。

布団の中でも、電車の中でも、ちょっとした空き時間でも、フルスタックアプリ開発を前に進められる。

そのための現実的な構成として、Claude Code on the web × Vercel × Supabase × Dopplerはかなり良い選択肢になりそうです。

Vercel Services / Container Imagesはこれから実際に試していくので、検証できたらまた続きも書きたいと思います。
