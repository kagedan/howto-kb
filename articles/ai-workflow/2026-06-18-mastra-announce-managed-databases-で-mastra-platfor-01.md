---
id: "2026-06-18-mastra-announce-managed-databases-で-mastra-platfor-01"
title: "[Mastra Announce] Managed Databases で Mastra Platform のDB構築がワンクリック化"
url: "https://zenn.dev/shiromizuj/articles/8dd16e54fe4e80"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめですが、過去記事での手順と比較することで今回の発表のどこが新しいかを分かりやすく示しているつもりです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年6月16日、Mastra は **Introducing Managed Databases for Mastra Projects** を公開しました。

今回の発表をひとことで言えば、**Mastra Platform 上で使うデータベースの「調達」と「接続文字列の受け渡し」を、外部サービスの管理画面から Mastra Platform の中へ引き戻した**アップデートです。

Mastra 自体はこれまでも LibSQL や Postgres など複数のストレージをサポートしていました。ただし本番に持っていくには、どこかの DB サービスを自分で契約し、接続情報をコピーし、環境変数を設定し、コード側でアダプタを切り替える必要がありました。今回の Managed Databases は、そのうち特に面倒だった **プロビジョニングと資格情報の注入** を Platform の標準機能として持たせた、という理解が一番しっくりきます。

---

## 今回の発表をひとことで言うと

**「Mastra のストレージを使うための外部 DB 準備を、Platform のプロジェクト設定画面から直接済ませられるようになった」** ということです。

やることはかなり単純です。

1. Mastra Platform の Project Settings を開く
2. Databases セクションで Add database を押す
3. Turso か Postgres を選び、名前とリージョンを決める
4. `ready` になるのを待つ
5. 表示された環境変数を使って `LibSQLStore` か `PostgresStore` をコードに渡す

重要なのは、ここで提供されるのが「Mastra 独自の新しいストレージ API」ではないことです。接続後に書くコードは、従来どおりの Mastra ストレージアダプタです。

```
import { PostgresStore } from '@mastra/pg';

export const storage = new PostgresStore({
  connectionString: process.env.DATABASE_URL!,
});
```

あるいは Turso / LibSQL ならこうです。

```
import { LibSQLStore } from '@mastra/libsql';

export const storage = new LibSQLStore({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});
```

つまり Mastra が追加したのは「ランタイムの抽象化」ではなく、**本番 DB を用意して接続するまでの運用導線の標準化** です。ここを取り違えると、今回の発表の価値が見えにくくなります。

---

## 背景: なぜこの発表が必要だったのか

### Mastra の弱点ではなく、本番化の弱点だった

エージェントフレームワークを触り始めた段階では、ローカルファイルやインメモリで十分に見えます。ところが Platform に載せて運用し始めると、かなり早い段階で「状態をどこに永続化するか」の問題が前面に出てきます。

この問題は Mastra に限りません。LLM アプリやエージェントを本番へ持っていくと、だいたい「モデルの選定」より先に「どの永続ストアをどう運用するか」で止まります。公式記事のトーンがあえて地味なのはそのためで、今回の発表は派手な新機能というより、**最初の本番化でつまずく確率が高い地点を埋める機能** と言えます。

### 接続文字列は小さな摩擦だが、積み上がると大きい

公式記事が挙げているのは、接続文字列はどこか、ステージング DB はあるか、どのアカウントで課金しているか、といった一見些細な運用摩擦です。ですが、これらは初学者だけの問題ではありません。

Managed Databases は、この種の面倒をゼロにはしませんが、少なくとも「Mastra Platform を触っているのに、最初の一歩で別ダッシュボードへ飛ばされる」感覚はかなり減らします。

---

## 何が追加されたのか

### 1. Platform から DB を直接プロビジョニングできる

Project Settings の Databases セクションから、Mastra 側でホストされる DB をアタッチできます。現時点では Turso と Postgres が利用可能で、MongoDB も近日対応予定です。

このとき Mastra Platform がやってくれるのは次の 3 つです。

* プロバイダ側で DB をプロビジョニングする
* 認証情報を安全に保持する
* 実行時環境変数として接続情報を自動注入する

Hosted databases docs の表現を借りれば、「connection strings to copy or configure が不要」ということです。少なくとも、手で `.env` に貼り付けて同期を取り続ける工程はかなり薄まります。

### 2. Provider ごとの環境変数が固定される

ドキュメントでは、各プロバイダに対して注入される環境変数が固定されています。

この固定化は地味ですが重要です。チームでコードを共有するとき、接続設定の命名がぶれないからです。さらに 1 プロジェクトにつき provider ごとに 1 つずつアタッチできるため、たとえば Turso と Postgres を同じプロジェクトにぶら下げて、用途別に使い分ける構成も取りやすくなっています。

### 3. DB の用途が「Mastra storage」に閉じていない

公式ブログ本文は比較的シンプルで「Mastra storage」の話に寄っていますが、Hosted databases docs では用途として次の 3 つが明示されています。

* Agent memory
* Application data
* Vector search

ここは見逃しにくいポイントです。今回の機能は単なる会話履歴の保存先ではなく、**アプリケーションデータや埋め込みベクトルの格納先まで含む、Platform 管理の永続ストア基盤** として位置付けられています。

---

## プロバイダの選び方

### Turso / LibSQL は「まず動かす」ための強い標準解

ドキュメントは、エージェント中心のプロジェクトでは Turso が最もシンプルな出発点だとしています。理由は分かりやすく、SQLite 互換で軽く、エージェントメモリや会話履歴のような用途に向いているからです。さらにリージョン数が多く、エッジ寄りに置きやすいのも利点です。

Mastra を学び始めたばかりで、まずは durable memory を持つエージェントを手早く動かしたいなら、Turso が一番 friction が少ない選択肢になりそうです。

### Postgres（Neon）は構造化データや既存資産があると強い

一方で Postgres は、単に「重いから上級者向け」という話ではありません。既に PostgreSQL を使っているチームにとっては、RDB としての設計資産、SQL の知見、BI 連携、運用ノウハウをそのまま引き継げます。

また、Mastra のアプリ側で構造化データを多く扱うなら、Postgres をストアの中心に置いたほうが自然です。公式 docs でも、structured or relational workloads には Postgres を選ぶよう明確に書かれています。

### MongoDB 対応予定は、ドキュメント指向ワークロードへの布石

近日対応予定の MongoDB は、今回まだ「coming soon」の段階です。ただし docs では document storage と built-in vector search を前面に出しており、今後は「SQL では表しづらいアプリケーションデータ」向けの導線も Platform が揃えていく可能性があります。

---

## 料金面で見ると何が変わるのか

Managed Databases は便利ですが、もちろん無料で無制限という話ではありません。課金は provider ごとの使用量ベースで、Mastra の既存アカウントにまとめて請求されます。

現時点の価格表を見ると、Platform の DB 課金はかなり理解しやすく整理されています。

ここで大事なのは、「別ベンダーに課金先が散らばらない」ことです。小規模チームや個人開発では、コストそのものより **請求の所在が増えること** のほうが煩雑さになりがちです。Managed Databases は、その運用負債を減らす意味でも効きます。

また、Database タブ上で当月の使用量を可視化できるので、「使い始めたはいいが、どこでどれだけ料金が出ているか分からない」状態にもなりにくいはずです。

---

## 以前の Neon 手動構成記事と比べると、何が変わったのか

今回の発表の何が新しいのか理解するには、このような比較が分かりやすいかもしれません。以前書いたこちらの記事では、Mastra Platform に載せたアプリの DB をローカルの LibSQL から外部の Neon に切り替えました。

<https://zenn.dev/shiromizuj/articles/3ed824b8d97648>

その際には、次のような手順を私自身で踏みました。

* Neon でプロジェクトを作る
* 接続文字列をコピーする
* `DATABASE_URL` を `.env` と Platform の環境変数へ設定する
* `@mastra/pg` を追加する
* `PostgresStore` と `PgVector` へ差し替える
* 必要なら `CREATE EXTENSION vector;` を実行する
* RAG データを再 ingest する

つまり、当時の記事が扱っていたのは **アプリケーションのストレージ構成をどう変えるか** と **外部 DB をどう調達して接続するか** の両方でした。

今回の Managed Databases は、そのうち後半、つまり **DB の調達と資格情報の注入** を Platform 側に吸収したものです。比較すると違いはかなりはっきりしています。

| 観点 | 以前の Neon 手動構成 | 今回の Managed Databases |
| --- | --- | --- |
| DB 作成場所 | Neon の管理画面 | Mastra Platform の Project Settings |
| 接続文字列の扱い | 自分でコピーして設定 | Platform が自動注入 |
| 課金管理 | Neon 側で管理 | Mastra 側に統合 |
| コード側の adapter | `PostgresStore` / `PgVector` を自分で設定 | ここは基本的に同じ |
| RAG / ベクトル設定 | 自分で `PgVector` や pgvector を考慮 | 引き続きアプリ設計として考慮が必要 |
| 運用の自由度 | 高い | 高いが Platform の管理導線に乗る |

要するに、**コードの世界は大きく変わらないが、Platform 運用の最初の一歩がかなり軽くなった** ということです。

### それでも以前の Neon 記事がまだ有効な箇所は

今回の発表を受けて Managed Database を使った場合、以前の Neon 記事で示した手順のいくつかの個所は不要になりますが、完全に不要になるわけではありません。Mastra が自動化するのは主に次の範囲です。

* DB のプロビジョニング
* 資格情報の保持
* 環境変数の注入
* 料金表示の統合

一方で、引き続き自分で設計する必要があるのは次の部分です。

さらに docs には、現時点で Hosted databases の作成は **CLI や public API ではできず、Project Settings からのみ** と明記されています。インフラ自動化まで含めて完全にコード化したいチームにとっては、ここは今後の拡張待ちになるでしょう。

また、detach はプロバイダ側の DB 削除と環境変数削除を伴う不可逆操作です。便利になったぶん、Platform 画面上の操作がそのまま実データの削除につながる点は、運用ルールとしてきちんと押さえておく必要があります。

---

## この発表が効くのはどんな人か

### 1. Mastra Platform を初めて本番利用する人

いちばん恩恵が大きいのはここです。Platform の外に出ず、数クリックで durable storage を持てるだけで、学習コストはかなり下がります。

### 2. 個人開発や少人数チーム

ベンダーごとの管理画面、課金先、資格情報管理を増やしたくないケースではかなり相性がよいはずです。特に「まずは動かしたいが、ローカルファイル永続化のまま本番に行くのは怖い」という層には強い解です。

### 3. 既存の外部 DB 運用に強く依存していないチーム

逆に、既に Neon や別の Postgres を標準基盤として深く運用しているチームでは、Managed Databases の価値は「簡単さ」よりも「Mastra Platform との統合度」に寄ります。そこをどこまで重視するかで評価は変わります。

---

## まとめ

今回の Managed Databases 発表は、Mastra のストレージ API を変えるニュースではありません。むしろ、**Mastra Platform でエージェントを本番化するときに最初に踏む運用作業を、プラットフォームの責務として吸収し始めた** ことに意味があります。

以前の Neon 記事が「外部 DB を自前で選び、つなぎ込み、構成を直す」話だったとすると、今回の announcement はそのうち「選んでつなぐ」の部分を Platform の標準導線へ取り込んだアップデートです。だから両者は競合ではなく、きれいに補完関係にあります。

Mastra Platform をこれから使う人にとっては、まず Managed Databases で durable storage を手に入れ、そこから必要に応じて Postgres / LibSQL / ベクトルストア設計へ踏み込む、という順序がかなり自然になりました。Platform 自体が、単なるデプロイ先から「本番化の足場」へ一段進んだと言ってよさそうです。

なお、今回の対象をどう切り分けるかという点では、**主眼は memory と RAG を含むアプリケーション側の永続ストア**と理解してよさそうです。Hosted databases docs でも用途は Agent memory、Application data、Vector search と整理されています。一方で Observability は別ラインで発表されており、Mastra Platform Observability は OTel 形状のシグナルを ClickHouse 系の OLAP 基盤へ流し込む構成として説明されています。したがって、ログ・トレース・メトリクスまで今回の Managed Databases に一本化する話ではなく、**Observability は分析基盤寄りの別責務、Managed Databases はランタイムデータ寄りの別責務**と見ておくのが自然です。

---

## 参考リンク
