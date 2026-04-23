---
id: "2026-04-08-claude-codeエージェントチーム機能でアプリ作ってみた-qiita-01"
title: "【Claude Code】エージェントチーム機能でアプリ作ってみた - Qiita"
url: "https://qiita.com/pro-tein/items/27ced96875f5d6b2d095"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

# はじめに

今回はいよいよエージェントチーム機能を実際に使ってみました。  
まだ試したことがない方の参考になれば幸いです。

まずは公式ドキュメントを一読することをおすすめします。

エージェントチーム機能とは：

# 意識すること

まずはエージェントチーム機能を使うときに意識することをまとめてみました。

## エージェントチームは初期設計がすべて

エージェントチームはAIがとことん自律して動くため、最初の設計がとてもとてもとても重要です。  
特にチームリーダーの役割にすべてかかっているといっても過言ではありません。  
失敗しにくくさせる設計のコツをまとめてみました。

良質な設計書を作成するためのコツとして、**プランモード**と`/dig`プラグインを使用するのがおすすめです。  
曖昧な状態であれば逆質問をさせて深堀りさせることで、エージェントにしっかり理解させた状態をつくることができます。

こちらから事前に用意しておきましょう。

## リーダーに作業をもたせない

リーダーにはあくまで全体管理に専念してもらうため、  
禁止事項：  
・コード実装  
・修正  
・調査  
・レビュー  
・テスト  
をスキルに明示する。

### Delegate Mode（委任モード）を使用する

Delegate Mode（委任モード）とは、メインエージェント（チームリーダー）が自律的にコード実装を行わず、オーケストレーション（タスク割り当てや調整）に専念させるための特別な設定のことです。これを設定すると、リーダーが作業の分割や結果の統合に集中できるようになるためチームの生産性が向上します。

### Push型のタスク割り当て

各メンバーエージェントが各々の好きなようにタスクを取得(Pull)してしまうと、**ファイル競合・タスク重複**といった原因になります。  
そこで、リーダーによる以下のPush型がおすすめです。  
・依存関係と影響範囲を見て先に担当者を決める  
・コンフリクト発生時は直ぐに調整する

# さっそく使ってみた

今回は、以下のようにエージェントチームを構成して、todoアプリを作ってみようと思います。  
（メンバー6,7は省略することにしました）

後半に改善点を記載しましたが、この例（プロンプトの渡し方）はあまり良くない例です。  
失敗例としてご参考ください。

[![SCR-20260401-tkim.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fa250f9c7-8c9c-49da-9393-1db615cbe488.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=63f61407e7be87891c0b3668c2f93d72)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fa250f9c7-8c9c-49da-9393-1db615cbe488.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=63f61407e7be87891c0b3668c2f93d72)

**リーダー：**  
・全体の管理（指示出し）のみを行います  
・まず最初にメンバー１に設計を依頼します  
・もしメンバー１の設計が完了したら、メンバー２にレビューを依頼します  
・全体を監視し、必要であれば適宜適切な指示を与えます  
・依存関係と影響範囲を見て担当者に指示を与えてください  
・コンフリクト発生時は直ぐに調整してください  
・進捗は`status-log-board.md`に書き出してください

**メンバー１(設計担当)：**  
・リクエストされたアプリケーションを作成するための、具体的な設計ファイルを作成します  
・プランモードと`/dig`プラグインを併用しながら、設計ファイルを作成してください  
・曖昧な場合は、ユーザーに確認してください  
・使用する言語、フレームワークやライブラリ、データベース設計などを考え、フロントエンドの実装とバックエンドの実装に分けて、それぞれ具体的な手順書を作成します  
・完成したアプリケーションのローカル環境での起動方法や、操作手順もドキュメント化します  
・設計もしくは修正が完了したら、リーダーに報告します  
・進捗は`status-log-board.md`に書き出してください

**メンバー２（設計レビュー担当）：**  
・メンバー１の作成した設計をレビューします  
・修正すべき箇所や、手順書に不備がないかなどを、徹底的にレビューします  
・評価項目を作成し、100点満点で合格点を80点とし、採点します  
・もし合格点に満たなかった場合は、メンバー１に修正を依頼します  
・もし合格点を満たした場合は、メンバー３に設計ファイルのフロントエンド部分の実装を依頼し、メンバー４にはバックエンド部分の実装を依頼します  
・進捗は`status-log-board.md`に書き出してください

**メンバー３（フロントエンド実装担当）：**  
・設計ファイルを参考に、フロントエンドの実装を行います  
・必要があればメンバー４とapiの情報を共有します  
・実装または修正が完了したら、メンバー５にレビューを依頼します  
・進捗は`status-log-board.md`に書き出してください

**メンバー４（バックエンド実装担当）：**  
・設計ファイルを参考に、バックエンドの実装を行います  
・必要があればメンバー３とapiの情報を共有します  
・実装または修正が完了したら、メンバー５にレビューを依頼します  
・進捗は`status-log-board.md`に書き出してください

**メンバー５（コードレビュー担当）：**  
・メンバー３と４の実装したコードをレビューします  
・修正すべき箇所や、リファクタリングすべき箇所がないかなどを、徹底的にレビューします  
・評価項目を作成し、100点満点で合格点を80点とし、採点します  
・もし合格点に満たなかった場合は、メンバー３と４それぞれに修正を依頼します  
・もし両方が合格点を満たした場合は、完了をリーダーに報告します  
・進捗は`status-log-board.md`に書き出してください

**メンバー６（テスト担当）：**  
今回は省略しますが、テスト担当（jestやplaywrightを使用）がいるとより高品質なアウトプットが期待できると思います。

**メンバー７（監視担当）：**  
今回は省略しますが、監視エージェントを置くこともおすすめです。  
全体を管理しているリーダーが、**完了報告を見逃す**場合も想定されます。  
するとエージェントの指示待ちが発生してしまい、連鎖的にデッドロック現象が発生します。  
コミュニケーション抜けやメンバー停止を早期発見するためにも、常に監視するエージェントを用意することは良いアイデアだと思います。  
例）軽量モデルHaikuを使用し、カスタムスキル`/loop`で毎分`status-log-board.md`を監視させる。一定時間以上「作業中」のタスクを検出した場合リーダーに報告する。

他にも、**セキュリティ担当**や**攻撃者（レッドチーム）**、**批判的レビュワー**などを登場させると、より議論が活発になり面白くなるかもしれません。

## エージェントチームを有効にする

エージェントチームはデフォルトでは無効になっているため、有効にするため`settings.json`に以下のように設定します。

settings.json

```
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

エージェントチームを使用するために必要な設定はこれだけです！  
あとはプロンプトを入力し、リクエストを送信するだけです。

今回は以下のように入力しました。上述の

> **リーダー：**  
> ・全体の管理（指示出し）のみを行います

以降をそのままコピペしてます。

[![SCR-20260402-bfdp.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F99c6772b-f363-4d45-a985-4a086970e249.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c176f47a6602f2311e60bda2d593e9e4)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F99c6772b-f363-4d45-a985-4a086970e249.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c176f47a6602f2311e60bda2d593e9e4)

LLMの解釈によっては、エージェントチームが立ち上がらない場合があります。  
その場合は「エージェントチーム機能を使用して」などと明示的に指定してください。

エージェントチームが起動しました。

[![SCR-20260402-bflp.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fe7225cc1-a069-470f-a9e2-41956e05ef36.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=19d3fe73dbcc11278b244d624483b380)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fe7225cc1-a069-470f-a9e2-41956e05ef36.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=19d3fe73dbcc11278b244d624483b380)

各エージェントが作成されていきます。

[![SCR-20260402-bvbn.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F6b0d038d-0f42-49fd-abe5-8e5e5f4e982f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c72c7e00f11639141ae9493013f6d7b9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F6b0d038d-0f42-49fd-abe5-8e5e5f4e982f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c72c7e00f11639141ae9493013f6d7b9)

チームリーダーがメンバーに指示を出します。

[![SCR-20260402-bgnz.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F86c4e8fc-0048-478c-b7b4-59203ca6a6a4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b9c5e5d30eb6c6063012fa6ab8f6a142)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F86c4e8fc-0048-478c-b7b4-59203ca6a6a4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b9c5e5d30eb6c6063012fa6ab8f6a142)

よしなに催促とかしてくれます

[![SCR-20260402-bjhd.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F88e1c23e-a4f5-46da-8434-3b2772c7259c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=727eed1eb2d7f328a83353fad81440d8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F88e1c23e-a4f5-46da-8434-3b2772c7259c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=727eed1eb2d7f328a83353fad81440d8)

メンバー１（設計担当）の様子  
`Shift + ↑`で切り替えることができます。

[![SCR-20260402-bjsl.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F8310f095-c9d7-458b-b9f9-ee23e722bcda.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d45047c2234acc5a2dd8a2ee9355a268)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F8310f095-c9d7-458b-b9f9-ee23e722bcda.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d45047c2234acc5a2dd8a2ee9355a268)

メンバー２（設計レビュー担当）の様子

[![SCR-20260402-bjzn.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F2dfc747e-22b5-4225-8585-a4ad37ecc8e2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7be3dd53b26524a9e3e3cdc9f023c63c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F2dfc747e-22b5-4225-8585-a4ad37ecc8e2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7be3dd53b26524a9e3e3cdc9f023c63c)

しばらくすると無事に完成したようです。  
進捗ログファイルです。

[![SCR-20260402-bsfj.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F1f49e13b-7280-4de5-8b7b-60a52582884c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=120abcb6d89578d6a23399d00c277dc5)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F1f49e13b-7280-4de5-8b7b-60a52582884c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=120abcb6d89578d6a23399d00c277dc5)

生成されたファイルです（最初は空のディレクトリでした）

[![SCR-20260402-bskn.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fef13f66e-ebb8-463d-96b6-5491697854dc.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ba6ca89100c759f196382f0faae5c5c9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fef13f66e-ebb8-463d-96b6-5491697854dc.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ba6ca89100c759f196382f0faae5c5c9)

ローカル環境で問題なく動作しました！（データベースも使用しているため、リロードしてもデータが消えません）

[![SCR-20260402-bspc.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fc2ec5e80-9373-455f-8def-845be7494479.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6e703c89aa5a9ef9f58cde259dcae5bf)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fc2ec5e80-9373-455f-8def-845be7494479.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6e703c89aa5a9ef9f58cde259dcae5bf)

# 今後改善したいと思ったこと

* 全メンバーの役割やルールを最初のプロンプトとして渡したのが良くなかった（コンテキスト大量消費）
* 簡単なアプリのつもりでも、全体的にトークンの消費量がものすごかったため、省エネ化を進めていきたい（メンバーの数を減らす、コンテキストエンジニアリング）
* どんなアプリを作りたいかの設計書は、エージェントチームを使う前に、プランモードと/digプラグイン、askUserQuestionなどを使用して、ファイルとして用意しておきたい
* エージェントチームの最初のプロンプトはなるべく少なくする（メンバー全員のコンテキストが圧迫される）
* 段階的開示で、それぞれの役割の指示されたファイルを参照させる（他のメンバーのコンテキストが混ざらないようにする）
* スキルを用意してコンテキスト（トークン消費）を抑える
* gitリポジトリの作成からプッシュまでもフローにする
* ギットワークツリーを導入して並列で開発させる

# おわりに

途中いろいろ省略してしまいましたが、実際に動かしてみるのが一番早いと思うので、ぜひ試してみてください！
