---
id: "2026-06-19-claude-codeの新機能artifactsでaiに作らせたhtmlドキュメントを爆速共有-01"
title: "Claude Codeの新機能Artifactsで、AIに作らせたHTMLドキュメントを爆速共有！"
url: "https://qiita.com/popo-lus/items/3f9f1a4eb7109544637a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "qiita"]
date_published: "2026-06-19"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

![01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4445801/aa271efd-e33e-464c-b674-7f26b3d7bf5f.png)

## はじめに

対象読者: Claude Codeを使っていて、AIに作らせたドキュメントや調査結果を「もっとちゃんと見せたい・共有したい」と思っている人

この記事で言いたいことは、ざっくり3つです。

- Claude CodeにHTMLを出力させてドキュメントを作る使い方が流行っていたが、その成果物を共有することにハードルがあった
- 新機能 **Artifacts** は、Claude Code上で生成したHTMLをそのままclaude.ai上のURLに公開・共有できる公式の仕組みで、この壁を埋めてくれる
- ただし「Team/Enterpriseプラン必須」「組織の中でしか共有できない」といった前提があるので、使いどころは選ぶ

https://x.com/claudeai/status/2067671912038240487

## 背景

少し前から、Claude CodeにMarkdownではなくHTMLを出力させてドキュメントを作る使い方が広まっていました。きっかけのひとつが、Anthropic公式ブログの記事 ["the unreasonable effectiveness of HTML"](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html) です。要点をざっくり言うと、「複雑な情報を伝えたいなら、もうMarkdownよりHTMLの方がいい」という主張でした。

たしかに、仕様書も調査レポートもコードレビューも、テキストで頑張るより1枚のページにした方が伝わる場面は多いです。

ところが、ここに無視できない壁がありました。**共有**です。

Claude Codeにお願いすると、ローカルに `report.html` のようなファイルが出力されます。しかし、そのファイルはどうやって共有すればいいのでしょうか？
GitHubやSlack、Google DriveはHTMLのプレビューに対応していないため、一度ダウンロードしてブラウザで開く必要があります。かといって、静的なドキュメントの共有のために自前でWebサーバーを立てるのも大げさです。

私は、今まで生成されたHTMLを一度ブラウザで開いて、PDFとして出力してから共有するというフローを取っていました。これでも共有はできますが、HTMLのインタラクティブな要素は失われますし、共有したデータを編集することもできません。

## HTMLで出力するメリット

そもそもHTML出力の何がいいのか。ざっくり挙げるとこんな感じです。

- 表・色分け・SVGの図・レイアウトをそのまま描ける（Markdownでは表現力が低い）。
- 見出しやタブで構造化ができる。
- スライダーやトグルを仕込めば、読み手が値を動かして試せる。

人間が読むことを前提としたドキュメントやレポートは、テキストだけでなく、視覚的な要素も重要です。HTMLはその点でMarkdownより優れていて、複雑な情報をわかりやすく伝えるのに適しています。弱点は、共有の難易度だけでした。

そこに出てきたのが、今回の **Artifacts** です。Claude Codeが生成したHTML/Markdownを、そのままclaude.ai上の限定公開URL（private URL）に公開して共有できる公式機能です！

## Artifactsで何ができるのか

### Artifactとは

artifactとは、Claude Codeがセッションの成果物を claude.ai 上のライブなWebページとして限定公開URLに公開したものです。今までは「docsフォルダにドキュメントを保存して」と頼んでローカルにMarkdownやHTMLとして保存していたのが、「artifactとして保存して」と頼む形に置き換わり、生成されたHTMLがそのまま claude.ai 上のURLに公開されるイメージです。

### 作る

作り方はシンプルで、「〜なartifactを作って」と頼むか、出力がページ向きだとClaudeが自分で判断して作ります。Claudeがプロジェクト内にHTML/Markdownファイルを書いて、公開しようとします。初回はこんな確認が出るので、

![スクリーンショット 2026-06-19 6.16.06.jpg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4445801/dd5cb47a-2dde-49a2-be1e-5d24cd123c80.jpeg)

`Yes` を選べば公開され、URLが表示されてブラウザが開きます。自動でブラウザを開きたくない場合は、環境変数 `CLAUDE_CODE_ARTIFACT_AUTO_OPEN=0` を設定すると抑制できます。また、ターミナルで `Ctrl+]` を押せば、直近のartifactをいつでも開き直せます。

作成されたページは、こんな感じです。

![02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4445801/52c094d5-b398-474f-89c5-8c0fbc6f7867.png)

ページ上部には、タイトル、共有ボタンなどが並び、下部には生成された内容が表示されます。

### 共有する

![03.jpg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4445801/6a924690-aee7-4cbd-8b14-0a18b9a39140.jpeg)

公開したばかりのartifactは、自分にしか見えません。共有するには、ページ右上の **Share** から、組織内の特定の人か全員かを選びます。共有相手には作者の名前も表示されます。

ただし、共有できるのは組織の中まで。外の人には渡せないので、社外に共有したいときはClaudeにHTMLファイルをもらって直接送る形になります。共有された相手は閲覧専用で、編集できるのは作者だけです。

なお、自分が作成したartifactは、claude.ai のギャラリー（`claude.ai/code/artifacts`）から一覧で確認・管理できます。

### 更新とバージョン管理

内容を直したくなったら、「ここを直して再公開して」と頼むだけ。Claudeが元ファイルを編集して、同じURLに公開し直してくれます。ページを開いている人の画面も、その場で書き換わります。

そして公開するたびに、その時点が1つのバージョンとして残ります。過去のバージョンにもさかのぼれますし、**Share** には「常に最新版を共有する（Always share latest version）」トグルがあり、最新版を見せ続けるか、特定のバージョンに固定するかを選べます。

![04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4445801/15282b62-b57b-42ad-9024-80dc4d0e8815.png)

なお、別のセッションから直したいときは、そのartifactのURLを渡せばOKです。逆にURLを渡さないと、更新ではなく新しいartifactが作られてしまうので、そこだけ注意してください。

### 何が作れるのか

公式はこんな使い方を挙げています。

- PRの設計意図や所見を、差分の横に色分けで並べる
- レイアウトやAPI設計、実装プランの代替案を横並びで比較する
- スライダーやトグルで、値をその場で試す
- 「Copy as prompt」的なボタンで、操作結果を指示に戻す
- 長時間タスクの進行を、チェックリストで可視化する

### 知っておくべき制約

「1枚の自己完結したページ」なので、制約もそれなりにあります。

| 制約 | 中身 |
| :--- | :--- |
| 外部リクエスト禁止 | 厳格なCSPで、外部のスクリプト・CSS・フォント・画像の読み込みや、`fetch`/XHR/WebSocketがブロックされる。CSS/JSはインライン化、画像はdata URIで埋め込まれる |
| バックエンドなし | 静的ページなので、フォーム送信の保存・閲覧者の認証・表示時のAPI呼び出しはできない |
| シングルページ | 相対リンクは解決されない。複数セクションはページ内アンカーで表現される |
| 対応ファイル | `.html` / `.htm` / `.md` のみ（Markdownは整形済みHTMLとして表示される） |
| サイズ上限 | レンダリング後で16MiB以下。失敗するときは大きな埋め込み画像が原因のことが多い |

あと、同じ内容でもターミナルにテキストで出すより、装飾されたページとして出力する方がトークンを食います（インラインのCSS/JS、特にdata URIで埋め込む画像が主な要因です）。SVGやCSSで図を描く、いらないインタラクションは省く、大きなデータは要約する、あたりで軽くできます。

### 使える条件

冒頭でも書いたとおり、Artifactsは下の条件を全部満たさないと使えません。どれか欠けると、ローカルにHTMLが書かれるだけだったり、公開できないと返ってきたりします。

| 要件 | 利用できる条件 |
| :--- | :--- |
| プラン | Team または Enterprise（Teamは既定でON、EnterpriseはAdminが有効化） |
| 認証 | `/login` でclaude.aiにサインイン（APIキー・ゲートウェイトークン・クラウドプロバイダ資格情報では不可） |
| モデルプロバイダ | Anthropic API（Amazon Bedrock / Google Vertex AI / Microsoft Foundryでは不可） |
| 組織ポリシー | CMEK・HIPAA・Zero Data Retention が無効であること |
| 利用環境 | Claude Code CLI、またはデスクトップ版 1.13576.0 以降 |

## おわりに

- HTML出力は「伝える・見せる・触らせる」のどれを取っても強いけど、弱点が共有だった
- Artifactsはそこを公式に潰す機能。生成して、private URLに公開して、組織内で共有、が1ステップで終わる
- ただしTeam/Enterprise＋claude.aiログインが必須で、共有は組織内クローズド。

これまで「Claude CodeにHTMLを吐かせると便利だけど、共有がなあ……」と感じていた人にとって、Artifactsはかなり痒いところに手が届く機能でした。betaでプランの制約もあるけれど、対象の人はぜひ一度、いつものレビューや調査レポートをartifactにしてみてください。たぶん、テキストに戻れなくなります。

ここまでお読みいただき、ありがとうございました！

### 参考リンク

- [Share session output as artifacts — Claude Docs](https://code.claude.com/docs/en/artifacts)
- [Using Claude Code: The unreasonable effectiveness of HTML — Anthropic Blog](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html)
