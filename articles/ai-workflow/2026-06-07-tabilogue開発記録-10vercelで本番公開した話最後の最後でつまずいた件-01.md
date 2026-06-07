---
id: "2026-06-07-tabilogue開発記録-10vercelで本番公開した話最後の最後でつまずいた件-01"
title: "tabilogue開発記録 #10｜Vercelで本番公開した話〜最後の最後でつまずいた件〜"
url: "https://note.com/cazi_lab/n/n6d24799b3078"
source: "note"
category: "ai-workflow"
tags: ["API", "note"]
date_published: "2026-06-07"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

機能がある程度揃ったので、いよいよ本番公開です。Vercelというサービスを使ってデプロイします。

### Vercelとは

今まで localhost:3000 でしか見られなかったtabilogを、世界中からアクセスできるURLで公開するためのサービスです。

Next.jsを作った会社が運営していて相性が良く、GitHubと連携すれば git push するだけで自動でデプロイされる仕組みになっています。個人開発なら無料枠で十分使えます。

### 環境変数の入力で詰まった

Vercelのアカウントを作成して、GitHubと連携。tabilogueのリポジトリをインポートするところまではスムーズでした。

問題はデプロイ前に必要な**環境変数の設定**でした。

![](https://assets.st-note.com/img/1780793676-9oejUDmJxMA8QiFWBgT74ZRc.png?width=1200)

Environmentsの画面

.env.local に保存していたAPIキーなどを、Vercelのダッシュボードに1つずつ入力する必要があります。

```
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY
STRIPE_PRICE_ID
ANTHROPIC_API_KEY
...
```

最初、Keyの欄に全部まとめて貼り付けてしまいました。1つずつ別々に入力する必要があったのですが、気づかずに全変数名をKeyに入れてしまった形です。

![](https://assets.st-note.com/img/1780793225-ajk28xsqCgyVZBmiR4cLofz9.png?width=1200)

各Keyの設定　失敗例

Claudeに指摘されて修正しましたが、数が多くて結構大変でした。途中で「Import .env」ボタンを使う方法に切り替えて、.env.local ファイルをそのまま読み込む形にしたら一気に楽になりました。

![](https://assets.st-note.com/img/1780793487-h5IWrJVt28XvzkuSlA0Q3fRM.png?width=1200)

隠しファイルなのでMacのファイル選択画面で Command + Shift + . を押して表示させる必要がありましたが、それ以外はスムーズでした。

### デプロイ中にエラーが出た

環境変数を設定してDeployボタンを押したら、ビルド中にエラーが出ました。

Stripe関連のコードに型エラーがあったのが原因でした。ローカルでは動いていたのに、本番ビルドでは通らないケースです。Claudeにエラーを貼り付けて修正してもらい、再デプロイして通りました。

### コミットが「Blocked」になった

デプロイ後にコードを修正してGitHubにプッシュしたら、コミットが「Blocked」と表示されました。

「Blocked」と表示されて、アップグレードを促すようなボタンも出ていた気がしたので、有料プランが必要なのかと思いました。ただClaudeに確認したところ、原因は全く別のところにありました。

GitのコミッターメールアドレスとGitHubのプライマリメールアドレスが一致していなかったのが原因でした。※Gmailでエイリアスなど使っていると要注意です。

bash

```
git config --global user.email "あなたのGitHubプライマリメール"
```

この1行で設定を修正して、空のコミットをプッシュしたら解決しました。有料プランは不要でした。

### 本番URLでログインできた

諸々修正を終えて、本番URL ~~https://tabilog-lemon.vercel.app~~ （現在<https://tabilogue-app.vercel.app/>）にアクセスしてGoogleログインを試してみました。

問題なくログインできて、投稿フィードも表示されました。localhostでしか見られなかったtabilogueが、世界中からアクセスできる状態になりました。

### 気づいたこと

今回一番感じたのは、「デプロイは思ったより手順が多い」ということでした。環境変数の設定、ビルドエラーの修正、アカウント設定のズレと、公開するまでに想定外のことがいくつも出てきました。ただ一つずつClaudeに確認しながら進めたら、最終的には動いたので、詰まっても諦めずに確認し続けることが大事だと思いました。

### 次回

次回は、ここまでのWeb開発を振り返ります。Claudeと一緒に作ってみて感じたこと、良かったこと、まだまだだと思っていることを書きます。
