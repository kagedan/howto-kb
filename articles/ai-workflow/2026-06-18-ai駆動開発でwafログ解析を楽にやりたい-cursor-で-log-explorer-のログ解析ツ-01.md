---
id: "2026-06-18-ai駆動開発でwafログ解析を楽にやりたい-cursor-で-log-explorer-のログ解析ツ-01"
title: "AI駆動開発でWAFログ解析を楽にやりたい — Cursor で Log Explorer のログ解析ツールを作ってみた"
url: "https://zenn.dev/cloud_ace_jp/articles/cloud-armor-fp-automation"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

こんにちは。クラウドエース株式会社 第一開発部の阿部です。Zenn 初投稿です。

同じ第一開発部の喜村さんが公開した [Cloud Armor の誤検知をクエリで炙り出してチューニングする](https://zenn.dev/cloud_ace_jp/articles/415b2fd2bfebc5) を読んで、Log Explorer で `AND NOT` を積み重ねながら誤検知を洗い出す手法を実践しました。この手法は **見落としが起きにくく、優れた方法** だと感じています。

ただ、規模が大きいログを手作業で回し続けるのは想像以上に大変で、「前処理だけでも自分用に楽にできないか」と考えました。そこで **Cursor を相棒に、AI 駆動開発で前処理用の Web UI を作ってみた** というのが本記事です。

ツール自体は社内用途の手元ツールなので公開しませんが、**「手作業のつらみを、AI と対話しながら自分用ツールに落とし込んでいく進め方」** を共有できればと思います。記事内のスクショはすべて `example.com` のサンプルログです。

## 手作業でつらかったこと

WAF（Cloud Armor 事前構成ルール）のチューニングは、だいたい次の流れです。

1. **プレビューモード**でルールを有効化し、DENY ログを収集
2. Log Explorer でログを確認し、誤検知を炙り出す
3. 問題なければ **本番適用（enforced）**

この **2 の Log Explorer でのログ解析** を、設定変更のたびに担当していました。喜村さんの記事で紹介されている **`AND NOT` で確認済み URL を除外しながら、未確認だけを見る** やり方を約 1 週間実践しました。

```
resource.type="http_load_balancer"
jsonPayload.previewSecurityPolicy.outcome="DENY"
(httpRequest.requestUrl:"https://api.example.com/" OR ...)

AND NOT httpRequest.requestUrl="https://api.example.com/search"
AND NOT httpRequest.requestUrl="https://api.example.com/refresh"
...（20種類以上）
```

手法は正しいのに、規模が上がると手作業だけでは厳しい場面がありました。

| つらさ | 体感 |
| --- | --- |
| ログの量 | **1時間だけでも8万件超**。期間次第で **100万件規模** |
| 同じ通信の繰り返し | 同じ URL + 同じ WAF ルール ID なのに、Log Explorer 上は **別行として何度も出る** |
| 見続ける負担 | 非正規通信（攻撃・スキャン）のログが長時間続き、確認作業が長引く |
| 20000 文字上限 | `AND NOT` を積み重ねたクエリを貼り付けると **「クエリが最大文字数 20000 文字を超えています」** エラーに何度も当たる |

「確認済み URL を全部クエリに載せる」のではなく、**先にパスや攻撃種別で絞り込んでから、短いクエリで Log Explorer を開く** ほうが現実的だと感じ、その前処理を AI に手伝ってもらうことにしました。

## AI 駆動開発で前処理ツールにしてみる

### Cursor にどう伝えたか

最初から完成形を指示したわけではなく、**つらみを言語化して投げる → 出てきたものを動かす → ズレを直す** の繰り返しでした。最初のプロンプトは要件をそのまま書いた程度のものです。

> Cloud Logging からエクスポートした Cloud Armor の DENY ログ JSON を読み込んで、  
> 「同じ URL + 同じ WAF ルール ID」で重複をまとめて一覧表示するブラウザ完結の UI が欲しい。  
> 社内ログを扱うので、読み込んだデータは外部に一切送信しないこと。

ここで効いたのが **「社内ログを扱うので外部送信しない」** という制約を最初に明言したことでした。これを言わないと AI は気軽にサーバー送信前提の構成を提案してくるので、**前提・制約を先に固定する** のは AI 駆動開発で大事だと感じています。

### 段階的に育てた

一気に作らせるのではなく、機能を 1 つずつ足していきました。

1. ログ JSON の読み込み（`.json` / NDJSON / 配列 / `{ entries: [...] }` 形式に対応）
2. **URL + WAF ルール ID** での重複排除と一覧化
3. 攻撃種別・パス・自動判定でのフィルタとソート
4. 「誤検知 / 攻撃」を自分でマークする機能
5. 絞り込み条件を反映した **Log Explorer 用クエリの生成**

各ステップで AI が出したコードを動かし、サンプルログでズレを見つけて直す、という進め方です。「重複キーは URL だけでなく WAF ルール ID も含めて」「20000 文字を超えるクエリはコピーさせない」といった **ドメイン知識は人間側から足す** 必要がありました。AI は土台を一気に組んでくれる一方、運用上の細かい判断は自分で言語化して指示する、という分担が現実的でした。

## できあがったもの

ここからは、AI と対話しながら作った UI の例を、サンプルログ（`example.com`）のスクショで紹介します。

### 詳細一覧 — 重複を1行に集約

ログを読み込むと、**URL + WAF ルール ID** で重複を除いた一覧が表示されます。同じ通信が Log Explorer 上で何十行も並ぶ問題を、ここで先に解消します。

![詳細一覧（読み込み直後）](https://static.zenn.studio/user-upload/deployed-images/78dd2cf562732fa15d88d503.png?sha=89f7982baea7501702c7dbdb93d998fb5f2608bd)

上記のサンプルでは、12 行のログから **9 パターン** の通信に集約されています。各行には、WAF が検知した **攻撃種別**（プロトコル攻撃、XSS、SQLi など）と、ツールによる **自動判定**（攻撃の疑い / 要確認 / 正規通信の疑い）が表示されます。

### 攻撃種別・パスでフィルタ

パスや攻撃種別、自動判定で絞り込めます。`.env` 系だけ見たい、`.git` 系だけ見たい、といった確認が Log Explorer より手軽です。

![.env 系で絞り込み](https://static.zenn.studio/user-upload/deployed-images/17d3ebd0f60e39e5f25a6d27.png?sha=1f7786f670e423d959737c734cf3b150fa6017d3)

![.git 系で絞り込み](https://static.zenn.studio/user-upload/deployed-images/b068288ee357ca38471a9c54.png?sha=5af2a7dddc798f48bcb05a59d76b2d8dd680cd6e)

![要確認だけ表示](https://static.zenn.studio/user-upload/deployed-images/1eb6e520b5940b6f69f297de.png?sha=88ba04b6c9e0475b27b001148416543931a2cf2b)

並び順も **ヒット数順 / 攻撃種別順 / パス順** などに切り替えられます。

![攻撃種別順でソート](https://static.zenn.studio/user-upload/deployed-images/2f704b7bdf39d112e792cb0b.png?sha=81da7d408288eca632eda6030207b80c02cda409)

### 誤検知 / 攻撃をマークする

自動分類（高 / 中）はあくまで参考情報です。`/health` のような正規通信は **誤検知** にマークし、攻撃と確信できるものは **攻撃** にする、という流れで最終判断は自分で行います。

![/health を誤検知にマーク](https://static.zenn.studio/user-upload/deployed-images/c9a59d88ccfa2250903ecec1.png?sha=c040868ecfd1bd3f8299d36c0adda85dce1df0ae)

判定後の全体像は次のとおりです。未確認・誤検知・攻撃が色分けされ、上段の統計も連動します。

![判定後の一覧](https://static.zenn.studio/user-upload/deployed-images/9c60e6dabdd837773aec5a41.png?sha=8c43dd5ca94b5feed43422fd9361275581bd5f99)

### Log Explorer クエリを生成

絞り込み条件を反映したクエリを生成します。20000 文字を超える場合は **コピー不可の表示と警告** を出し、不完全なクエリが使われないようにしています。

![Log Explorer クエリ生成](https://static.zenn.studio/user-upload/deployed-images/c5c48e9d31966c1457feea03.png?sha=ae207481c66f4af095f9dc0e5a84329277d1a436)

つまり、**前処理（重複排除・グルーピング）はツールで、最終判断と本番適用は Log Explorer に戻って手作業で** という役割分担です。

## AI 駆動開発でやってみて感じたこと

### よかったこと

* **「つらい」を言語化するだけで土台ができる**。重複排除や一覧表示のような定型処理は、要件さえ伝えれば一気に組み上がる
* **試行のサイクルが速い**。「この列も足して」「ソート順を変えて」が会話のテンポで反映される
* 自分用の手元ツールなので、**自分の作業フローにぴったり合わせて削り込める**

### つまずいたこと

* 制約（外部送信なし・社内ログ）を **先に固定しないと、前提のズレた実装が出てくる**
* 「URL + ルール ID で重複判定」のような **ドメイン知識は人間が足す** 必要がある
* 生成されたコードはそのまま信用せず、**サンプルログで毎回挙動を確認** するのが結局いちばん早い

### 手動フローとの使い分け

最後に、どこを AI で作ったツールに任せ、どこを手作業で残したかの整理です。

| 作業 | 担当 |
| --- | --- |
| プレビューモード有効化 | 手動 |
| ログ JSON の取得 | 手動（`gcloud logging read` 等） |
| 重複排除・一覧・グルーピング | **AI で作ったツール** |
| 誤検知 / 攻撃の判断 | 手動 |
| `evaluatePreconfiguredWaf` での除外 | 手動（[喜村さんの記事 Step 3](https://zenn.dev/cloud_ace_jp/articles/415b2fd2bfebc5)） |
| DENY 0 件確認 → 本番適用 | 手動 |

## まとめ

* [喜村さんの記事](https://zenn.dev/cloud_ace_jp/articles/415b2fd2bfebc5) の `AND NOT` 絞り込みはそのまま活かす
* 手作業でつらかったのは **同じ通信の繰り返し** と **一覧の散らばり**、**20000 文字上限**
* その前処理を **Cursor との AI 駆動開発** で自分用ツールに落とし込んだら、探索が大幅に楽になった
* ポイントは **制約を先に固定する** ことと、**ドメイン知識は人間が足す** こと

「手作業でつらい定型処理」を見つけたら、まず AI に投げて土台を作らせてみる、という進め方の参考になれば幸いです。

## 参考リンク
