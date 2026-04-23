---
id: "2026-04-12-mastra-announce-エージェント運用の3層構造-mastra-platform-が変える-01"
title: "[Mastra Announce] エージェント運用の3層構造 ― Mastra Platform が変えるアーキテクチャの考え方"
url: "https://zenn.dev/shiromizuj/articles/ba80b4694382b3"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。普段このシリーズでは「速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです」と書いているのですが、**今回は私の勝手解釈が多めです**。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## Mastra が 「Mastra Platform」 を発表

2026年4月9日、Mastra は **Mastra Platform** を発表しました。

このアナウンスの冒頭の段落を直訳すると以下のようになります

> 本日、エージェントを効果的に開発・実行・管理・監視するためのツール群として、**Mastra Platform** をローンチします。
>
> これらは3つの独立したプロダクトであり、それぞれが単独でもゲームチェンジャーとなる内容です。

## 発表の内容は「新しいクラウド」と「アプリの分離」

「Mastra Platform」という名前から「新しいクラウドサービスの発表」と理解しがちですが、そしてそれは間違っていないのですが、今回の発表の**力点はそこではない**と私は理解しました。中身を読み解くと、**Mastraエージェントシステムのアーキテクチャをどう組み立てるか**という設計思想の転換が核心にあります。

Mastra Platform は次の3つのプロダクトで構成され、**それぞれが独立したプロダクトだ**、と述べているところが重要です。

* **Studio**：ログ、トレース、eval、データセット、メトリクス
* **Server**：エージェントとワークフローをプロダクション API としてデプロイ
* **Memory Gateway**：フレームワーク非依存で使える永続メモリ

## タイトルは「Platform」だが、話の力点は「アプリの分離」

考えてみれば、Studio（UI） も Server（AIエージェントの実体とAPIサーバー） も Memory Gateway（Memory） もインフラの話ではありません、アプリの話です。言い換えれば、Studio も Server も Memory も、特定の実行環境に限った登場人物ではありません。ローカルでも、オンプレでも、AWS （Amazon Web Services） でも、どこで動かしても登場するプレイヤーです。

今回のアナウンスは「Platform」というクラウド基盤の話と、「Studio と Server と Memory の分離」というアプリの話が混ざっています。そして、タイトルは「Platform」ですが、話の力点は「アプリの分離」にあり、そこが分かりづらいところだと個人的には思います。

「アプリの分離」についてフォーカスするために、クラウドへのデプロイは抜きにして開発ローカルに話を限定しましょう。いままで `npm run dev` すれば、 アプリ（APIサーバー） と Studioサーバーが同時に起動しましたし、アプリにはメモリが同梱されていました。

今後も、 `npm run dev` すれば従来どおり全部まとめて起動します。わざわざ別々のプロセスを立てる必要はありません。しかし、**Studio と Server はそれぞれを個別に起動することもできるようになる**、ということです（なお、Memory はローカル/オンプレでは独立した起動コマンドはなく、`mastra dev` / `mastra start` の Mastra サーバープロセスに内包されます。Memory Gateway として独立したサービスになるのは Mastra Platform（クラウド）のみです）。

```
（旧）一体型
Mastra = API + Studio + Memory（全部内包）

（新）3層構造
Server  = 実行・APIとしての公開
Studio  = 観測・デバッグ・評価
Memory  = 状態管理（外部からも利用可能）
```

この分解によって、必要なコンポーネントだけを選んで使えるようになります。Server だけをバックエンド API として使う。Studio だけを観測ツールとして既存のエージェントに接続する。Memory Gateway だけを LangChain や OpenAI SDK のアプリに組み込む。そういった「部分利用」が設計として成立するようになりました。マイクロサービス化、と言ってもいいかもしれません。

そのうえで、それらをMastra Platformという基盤上にデプロイすることもできる、ということです。

では、Studio と Server と Memory Gateway 、それぞれをもう少し詳しく見てみましょう。

---

## Studio：コードなしで回るイテレーションサイクル

Studio 自体は以前から存在していましたが、今回「クラウド版」として正式プロダクト化されました。

目玉は [Agent Editor](https://mastra.ai/blog/announcing-agent-editor)（前日に別途発表された機能）との統合です。エージェントのプロンプト、ツール構成、表示条件をコードなしで変更・バージョン管理・ロールバックできます。

<https://zenn.dev/shiromizuj/articles/7ece2af5c09ce9>

それに加えて：

* **Metrics**：全実行のコスト・エラー・レイテンシをダッシュボードで把握
* **Datasets / Experiments**：収集した実行ログを使って、新しいモデルやプロンプトに対してリプレイ評価が可能
* **Logs / Traces**：モデル呼び出し・ツール実行・ワークフローステップの全履歴

これらは今まで `mastra studio` でローカル実行するものでしたが、Platform 版では URL にデプロイしてチームで共有できます。[Studio Auth](https://mastra.ai/blog/announcing-studio-auth) と RBAC でアクセス制御もできます。

もともと Studio は Playground と呼ばれていて、文字通り「開発者の遊び場」、リリース前にザッとAIエージェント部分に特化して動作確認するための開発者向けツールだったわけです。しかし、機能が充実し、むしろこれを商用利用したい、そのためには権限によるアクセス制御もしたい、みたいな話になって位置づけも変わってきたのでしょう。一言でいえば、評判が良いのでプロダクション化した、ということです。

---

## Server：エージェントが「バックエンド API」になる

多くのチームが直面していたのは、「エージェントを作ったはいいが、どうデプロイするか」という問題です。

Mastra Server はその答えです。`mastra build` で自己完結型のビルドを生成し、`mastra start` または `mastra server deploy` でデプロイします。エージェント、ワークフロー、ツールが REST エンドポイントになり、OpenAPI ドキュメントと Swagger UI も自動で付いてきます。

```
mastra build   # 自己完結型の出力を生成
mastra start   # 起動
```

セキュリティ面での設計も重要です。システムプロンプト、ツール定義、API キーはデフォルトでストリーミングレスポンスから除外されます。Studio を保護する認証システムをそのまま Server エンドポイントの保護にも適用できます。

---

## Memory Gateway：Mastra 外からも使える「記憶」

Memory Gateway は今回の3つのプロダクトの中で、最も新しい概念です。

Mastra の [Observational memory](https://mastra.ai/blog/observational-memory) は **Fortune 500 企業や元 DeepMind 研究者が本番環境で使っている**実績あるメモリ機能です。

<https://zenn.dev/shiromizuj/articles/12e4640b99bc6a>

今回はそれを **Mastra エコシステムの外** に向けて開放しました。

```
LLM の呼び出しを Memory Gateway に向けるだけで、
エージェントに永続的なメモリが付与される。
Python、TypeScript、またはあらゆるフレームワークから利用可能。
```

これは Mastra のビジネス戦略としても重要な一手です。今まで Mastra はフレームワークとして LangChain や OpenAI SDK と競合する位置に立っていました。しかし Memory Gateway によって、それらのフレームワークを使うユーザーに向けて「メモリ基盤」として Mastra を提供できるようになります。つまり部分的には**競合ではなく補完関係**に変わります。

---

## ローカル開発はどう変わるか

「アーキテクチャが3層になった」と聞くと、`npm run dev` のたびに3つのプロセスを個別に立てないといけないのか？と不安になるかもしれません。

答えはノーです。**デフォルトの開発体験はほぼ変わりません。**

`npm run dev` で Studio も Server もまとめて起動します。Memory はローカル開発ではデフォルトで内蔵モードで動きます。わざわざ外部の Memory Gateway を立てる必要はありません。

変化は「構造が分離可能になった」という点です。本番環境でスケールしたいとき、他のシステムと統合したいとき、その分離が有効になります。なお、Memory を独立したサービス（Memory Gateway）として運用できるのは Mastra Platform（クラウド）のみです。ローカル/オンプレでは、Memory は常に Mastra サーバープロセスに内包されます。

```
（ローカル/オンプレ）mastra dev / mastra start → Server に Memory が内包
（Mastra Platform）  Server と Memory Gateway を分離して運用
```

開発体験を保ちながら、本番での柔軟性を獲得する、という設計です。

---

## 念のためローカルで分離起動してみた

念のため、ダミーのmastraプロジェクトを作って、ローカルでAPIサーバーだけ / Studioだけの分離起動をしてみました。

まず、最初は `pnpm run dev` で両方のサーバーが起動することを確認します。

![](https://static.zenn.studio/user-upload/251119bcb0e0-20260410.png)  
*Studio と API の両方が起動した*

次に、`pnpm run build` でビルドしてから `pnpm run start` することで、APIサーバーだけ起動することを確認します。

![](https://static.zenn.studio/user-upload/30b498b80466-20260410.png)  
*Studio は起動せず、API だけが起動した*

最後に、`npx mastra studio` で、Studioだけが起動することを確認します。デフォルトでポート 3000 でStudio UIのみが起動し、APIサーバー（port 4111）は起動しません。

![](https://static.zenn.studio/user-upload/a4d2bbf71c54-20260410.png)  
*API は起動せず、Studio だけがポート 3000 で起動した*

注意点として、StudioはUIのみで、実際のエージェント実行にはAPIサーバー（mastra dev）が別途必要です。StudioはAPIサーバーに接続することで動作します。なので、APIサーバーを起動せずにStudioだけ起動しても、こんな感じです。

![](https://static.zenn.studio/user-upload/b2ed051a5abe-20260410.png)  
*Studioのトップページではなく、Mastraインスタンスを聞いてくる画面が表示される*

---

## 改めてPlatformの話：Mastra Cloud と何が違うのか

と、ここまで「アプリの分離」の話が今回の発表の主眼だと位置づけて、そこを中心に考察してきましたが、改めて「Mastra Platform」について調べてみます。

発表を読んで最初に浮かぶのが「Mastra Cloud との関係は？」という疑問です。Mastra Cloud はすでに存在していた、デプロイ・モニタリング・Studio をセットで提供するSaaSでした。今回の Platform はその進化版なのか、置き換えなのか。

結論から言うと、**進化というより"分解と再設計"** です。

|  | Mastra Cloud（旧） | Mastra Platform（新） |
| --- | --- | --- |
| 構造 | 一体型のSaaS | 3つの独立プロダクト |
| Studio | ダッシュボード的存在 | 独立プロダクト（クラウド / セルフホスト） |
| 実行基盤 | 裏で動く実行環境 | **Server** として明示的に切り出し |
| メモリ | フレームワーク内部の機能 | **Memory Gateway** として外販 |
| 指向 | 個人〜小規模チーム | プロダクション・チーム開発・大規模 |

Mastra Cloud と Mastra Platform の違いは、Firebase と AWS の比較に近いかもしれません。Firebase（一体型の便利なSaaS）が AWS（分解されたサービス群）になった、という変化です。

で、今までの Mastra Cloud はどうなるのか？　私自身の Mastra Cloud のダッシュボードを開いたところ、ヘッダーに次のバナーが表示されていました。

> **Mastra Cloud is being deprecated. Migrate your project to the new Project platform to avoid service interruption.**

要するに、Mastra Cloud は廃止され、Mastra Platform への移行が促されています。「進化というより"分解と再設計"」という見立ては正しかったようです。「フルマネージド版として残り続ける」のでは？と予想しましたが、それは外れました。Mastra Cloud は Mastra Platform に置き換わります。

![](https://static.zenn.studio/user-upload/53e7e8dde2eb-20260410.png)  
*Deprecated(非推奨)になってしまった、Mastra Cloud*

---

## Platform の料金

Studio と Server は同一プラン、Memory Gateway は独自プランで提供されます。どちらも Starter は無料で、ユーザー数とデプロイメント数は全ティアで無制限です。

**Studio / Server**

|  | Free | Teams | Enterprise |
| --- | --- | --- | --- |
| 価格 | 無料 | $250/チーム・月 | カスタム |
| ユーザー / デプロイ | 無制限 | 無制限 | 無制限 |
| 可観測性イベント | 10万件 | 未定 | カスタム |
| CPU 時間 | 24時間 | 250時間 | カスタム |
| データ転送量 | 10GB | 100GB | カスタム |

**Memory Gateway**

|  | Free | Teams | Enterprise |
| --- | --- | --- | --- |
| 価格 | 無料 | $250/チーム・月 | カスタム |
| メモリトークン | 10万 | 100万 | カスタム |
| 追加トークン | $10/100万 | $10/100万 | $10/100万 |
| 検索ストレージ | 250MB | 1GB | カスタム |
| 古いスレッドの保持 | 15日 | 6ヶ月 | カスタム |

---

## まとめ：「道具」から「基盤」へ

Mastra Platform を一言で表すなら、エージェントシステムが「アプリの中の機能」から「独立したアーキテクチャコンポーネント」に昇格した、という発表です。

今までの Mastra は「AIエージェントを作るための便利なフレームワーク」でした。Platform 以後の Mastra は、**エージェントを本番で運用するための基盤**を名乗っています。

Server（実行・公開）、Studio（観測・評価）、Memory（状態管理）の3層に分解することで、エンタープライズ規模のエージェント運用に必要な構成要素が揃いました。各コンポーネントを個別に使えること、どこでも動くこと、開発体験を変えないことが、この設計の強みです。

---

## 参考リンク
