---
id: "2026-07-11-claude-desktop-on-amazon-bedrock-から-salesforce-に-m-01"
title: "Claude Desktop on Amazon Bedrock から Salesforce に MCP 接続してみた"
url: "https://zenn.dev/aws_japan/articles/claude-desktop-bedrock-salesforce-mcp"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "cowork", "zenn"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは！AWS でソリューションアーキテクトをしている町田です。

今回は、Claude Desktop (Cowork) から Salesforce にアクセスするための **Salesforce Hosted MCP Server** を Windows 環境でセットアップしてみました。  
これを利用することで、**自然言語だけでSalesforceのデータ操作が完結**します。  
なお、Salesforce Hosted MCP Server は複数個あり、今回は、sobject-read(読み取り操作) と sobject-all(読み書き操作) の2つの違いを確認してみようと思います。

## Salesforce Hosted MCP Server とは

Salesforceが公式にホスト・運用しているMCPサーバーで、AIエージェント（Claude等）からSalesforceのデータや機能に直接アクセスできるエンドポイントです。  
接続は Salesforce のホストする HTTPS エンドポイント経由のため、自前のサーバーやミドルウェアは不要で、External Client App（OAuth アプリ）の登録だけで AI エージェントから接続できるのがポイントです。

## 前提条件

* Claude Desktop がインストール済みで、Amazon Bedrock 経由のサードパーティ推論が設定済み

## セットアップの全体像

セットアップは以下の 4 ステップで完了します。

今回のセットアップは Salesforce 管理者と Claude Desktop 利用者で役割が分かれます。

**Salesforce 管理者が行うこと：**

* MCP Server の有効化
* External Client App の作成
* コンシューマー鍵 を利用者に共有

**Claude Desktop 利用者が行うこと：**

* Claude Desktop でのコネクタ設定
* Salesforce へのサインイン

## 1. Salesforce 側のセットアップ

### 1.1 Salesforce Developer Edition のサインアップ

**Salesforce Hosted MCP Servers** が無料で使えるため Salesforce Developer Edition を使います。  
<https://developer.salesforce.com/free-trials> にアクセスして必要情報を入力して登録を完了させます。

「Get a Developer Edition」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/7adc5f1f527b6799f9489ee7.png?sha=6210fb4e8578d92e6de1f0d33d43690cf9a7f76e)

必要情報を入力して、「Sing me up」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/7ab923b9b6e489d0d9b07d63.png?sha=1b39d4aa7cc6e188cfe4a279fdc0bf30814d0b1a)

以下のようなメールが届くのでパスワードをリセットします。  
![](https://static.zenn.studio/user-upload/deployed-images/80c96cebf1a1e79065e1125c.png?sha=1de698a733323f4409f0a2af94d6c755e9439995)

パスワードのリセットをクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/7ae9c55840fbb23bc414c6bf.png?sha=cc744c1e2826b0c9acc87981633da283d6a44c89)

必要な情報を入力してパスワードを変更します。  
![](https://static.zenn.studio/user-upload/deployed-images/ab258cc1e5ba76707fb809e0.png?sha=b7a241a263155c9b4d2479cd5ebe4afed47bbb76)

登録完了です。  
![](https://static.zenn.studio/user-upload/deployed-images/910c437050e66342a6be8458.png?sha=a99036a7e1cf561014619cfe76d17fe9d9280f17)

「設定」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/b1c8f00d118d21fe4bb18900.png?sha=c091cf438e1c49ee6b0e73747f67c5aa8e979285)

"**MCP**"と入力し、「インテグレーション」「APIカタログ」の下にある「MCP サーバー」をクリックします。  
初回テストのために「**sobject-reads**」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/9bcb8a62770920521969f3c1.png?sha=b0fad94010dbbfacac79fb353b1b36a1e706c33c)

「有効化」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/6f90254fd206edac404014c7.png?sha=74d21ae2dc5aefeffb75f8f35a27a6f540391a8b)

サーバー状況が稼働中になっていることを確認できます。  
![](https://static.zenn.studio/user-upload/deployed-images/2645c9bac36234c7e718f404.png?sha=f1505089d37eb4b483db0e555c99bab75c92bf10)

後ほど、画面内のサーバーURLを Claude Desktop 側で用いるのでどこかに保存しておくか、Salesforceの画面をすぐに参照できるようにしておきましょう。

```
サーバー URL:
https://api.salesforce.com/platform/mcp/v1/platform/sobject-reads
```

### 1.2 External Client App (ECA) の作成

External Client App（ECA）は「MCP クライアント（アプリケーション）ごと」に 1 つ作成するものであり、ユーザーごとに作成するものではありません。

検索ボックスに「外部」と入力し、「外部クライアントアプリケーションマネージャー」をクリックし、「新規外部クライアントアプリケーション」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/7c181f09c92ef8c306a18805.png?sha=c62a224c9fc6f77147758d4e28294500309f6f16)

基本情報を入力します。  
外部クライアントアプリケーション名は任意の値で大丈夫です。API 参照名は自動で設定されます。  
![](https://static.zenn.studio/user-upload/deployed-images/6a6d4456c7003d60fe26a304.png?sha=3fb67a713f6efad8426d74b9922ae676939b0cf2)

OAuth を有効化します。  
以下の値を入力したり、選択します。

* コールバック URL
* OAuth 範囲
  + いつでも要求を実行 (refresh\_token, offline\_access)
  + Salesforce でホストされている MCP サーバーにアクセス (mcp\_api)  
    ![](https://static.zenn.studio/user-upload/deployed-images/18fa2707c6d9742e3e65a2ee.png?sha=0cf5374202d46bb373cf464d0f9287586d84a349)

セキュリティは以下の通りに設定します。  
![](https://static.zenn.studio/user-upload/deployed-images/048ba0aa6f7cd3ee06865200.png?sha=638a5fe12c6360cb85b0c9ec2840af754d2cef3d)

「作成」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/6dbab47b0759ae7c2f75affe.png?sha=839b7999267057646955e2c71f7292ffba576224)

作成されたので、コンシューマー鍵を入手します。その値を Claude Desktop 側のクライアントIDに設定することになります。  
![](https://static.zenn.studio/user-upload/deployed-images/8749638548cd0b56349fe137.png?sha=fa2b36f26d371c870045064474c5fd07dae4be49)

設定したメールアドレスにセキュリティコードが送られるので、確認コードに入力して、「検証」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/481bbd5021c33f0b7df6b248.png?sha=0e9e4864da744aa67c0d7bec519e26fa40fc427c)

コンシューマー鍵は Claude Desktop 側で必要になるので、コピーしておきます。  
![](https://static.zenn.studio/user-upload/deployed-images/e270b7d09a36dd2820417f7a.png?sha=3170a06be59e378c33d45ac0a44b56810f109787)

## 2. Claude Cowork 側の設定

「コネクタと拡張機能」、「+ 追加」から「空白」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/b705d96226017c0e4e007f76.png?sha=d26defc4e7d4d082f04f6bfbf031f65dca44780f)

以下の値を入力、選択します。

* 「名前」は任意の値
* 「トランスポート」は **Streamable HTTP**
* 「URL」は <https://api.salesforce.com/platform/mcp/v1/platform/sobject-reads>
* 「OAuth」は **独自クライアントを使用**
  + 「クライアントID」は **Salesforce で取得したコンシューマー鍵**
  + 「コールバックホスト」は **localhost**
  + 「コールバックポート」は **38000**  
    ![](https://static.zenn.studio/user-upload/deployed-images/4ac355430b63d7bd7931e50d.png?sha=8f5e257efc507fa120169b92dd04e6352665b3a5)  
    コールバックホストが localhost か 127.0.0.1 に指定されてしまうが、Salesforce 側では 127.0.0.1 を http:// で登録することはできないので、必ず localhost に指定すること。  
    「変更を適用」をクリックします。  
    ![](https://static.zenn.studio/user-upload/deployed-images/d71034ae32ddbaa2072d5c7a.png?sha=daf54c13f02ed192247a84fefa24b0de980c4b93)

「今すぐ再起動」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/a6209dacbac267214cc39a22.png?sha=6133bbdbf9fe2697ff7c8ca3cc6ddb79b3565584)

再起動後に「サインインしてテスト」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/473f2d467f55923de01a28ee.png?sha=09fbbcc28b274b7260276a9d4d69f814b617f8e6)

ブラウザが起動して Salesforce ログイン画面が表示されます。  
Salesforce のユーザー名とパスワードを入力してログインします。  
![](https://static.zenn.studio/user-upload/deployed-images/8e88f944d2c7c81ad74dbdb2.png?sha=4af7ff71e7609fea078685dc403ff3aa84c7abea)

Salesforce に登録されているメールアドレスに確認コードが送信されるので、そのコードを入力し「検証」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/2636f64baa12e761ca3f59d3.png?sha=cf5c3d632f5b2553b2e9d740da600700b4a271f8)

「許可」をクリックします。  
![](https://static.zenn.studio/user-upload/deployed-images/c2a3e8d3bc651451358a9601.png?sha=78e5f6a271b575e3e90a935983a3b37f11b43417)

アクセスが拒否されることがあるのですが、  
![](https://static.zenn.studio/user-upload/deployed-images/eb14ce804fdac9976c6d2490.png?sha=800ac450110e907b1bd0b430a78a2197728031e2)

再度、Claude Desktop から再テストを行ったら成功しました。  
![](https://static.zenn.studio/user-upload/deployed-images/522f8def0983b68a0b7cd707.png?sha=d7030d7131a5c8f3a0fc424d8d90874afbfbdf9c)  
![](https://static.zenn.studio/user-upload/deployed-images/c41e310ccc43d9a1fc51105c.png?sha=9097a36a86773562498937491d52b83d7d3d3cf3)

## 3. 動作確認(sobject-read)

適当なプロンプトを入力して、Salesforce に接続してみます。（ローマ字での入力でも何も問題なしです）  
![](https://static.zenn.studio/user-upload/deployed-images/33f41f9553909326a8271082.png?sha=170a0e047c5161bae0c1fd892fae49f0ccba388e)

Salesforce にはサンプルデータがインポートされているので、そのサンプルデータを使って簡単なレポートを作ってもらおうと思います。  
![](https://static.zenn.studio/user-upload/deployed-images/11b76f1c7088e56aaff54490.png?sha=b96d505e5710c5de828812a4f93b6b45bdbc26a7)

![](https://static.zenn.studio/user-upload/deployed-images/de682e11d7299b97faef73b4.png?sha=ab77bb7abcc0e657c493c890931e51b4f79f0acf)

以下が回答されました。  
![](https://static.zenn.studio/user-upload/deployed-images/69bf7ecdf520f119c468ff4b.png?sha=8379bf09f1dbd8791dcbe997c4c1b49f4b043f76)

Claude は Closed Won が18件という回答をしていますが、実際の Salesforce を確認すると Closed Won は18件であることを確認できました。  
![](https://static.zenn.studio/user-upload/deployed-images/019ea9cf177763115b67cf51.png?sha=8951b950186f0bf23654b9f9acd04757ae0ca4ab)

実際に登録してみようとしたところ、拒否されました。  
sobject-reads を使っているため想定通りの挙動です。  
![](https://static.zenn.studio/user-upload/deployed-images/93daf952ee5b94de59242d05.png?sha=b995e0ac1c2627db246121803489f5151cda2600)

## 4. 動作確認(sobject-all)

### 4.1 設定変更

Salesforce 側で **sobject-all** を有効化します。  
![](https://static.zenn.studio/user-upload/deployed-images/afdbe56ca2a8b82b3f25386c.png?sha=ec691cb5cbc48688c238b26f973b238f282c7d2d)  
![](https://static.zenn.studio/user-upload/deployed-images/f433eb40d4b869af1a41d242.png?sha=1cd887a1cb664248c05153f7c2f3c517a8741333)

```
サーバー URL: https://api.salesforce.com/platform/mcp/v1/platform/sobject-all
```

Claude Desktop 側のURLを **sobject-all** に変更します。  
![](https://static.zenn.studio/user-upload/deployed-images/decb9b6607ff01181ee2158c.png?sha=34dd16d44867e53ffb616748c885ba8dd46ec3f3)

変更を適用して再起動します。  
![](https://static.zenn.studio/user-upload/deployed-images/75bd0774ea31dc3c4c9b04a8.png?sha=2ab2a045a38d810063a4869c7ada2c966e95c734)

### 4.2 ユースケース1(商談パイプライン自動生成)

従来では担当者が商談後にSalesforceへ情報を手入力するにあたって以下の様な工程や課題が発生したと思います。

* **入力工数**: Account → Contact → Opportunity → Product の順に画面遷移しながら手動作成（15〜30分）
* **入力漏れ**: 忙しくて後回し → 情報鮮度が落ちる → 不正確なパイプライン
* **構造化の壁**: ヒアリング情報は自然言語。それをSalesforceのフィールドに分解するのは認知負荷が高い

AIエージェントを使うことにより、以下の工程を自動化することができます。

1. 既存Account/Contact検索（重複チェック）
2. 情報抽出 & フィールドマッピング
3. レコード群の一括作成
4. 確認サマリーの出力

以下のプロンプトを投げてみます。

```
以下の商談メモをSalesforceに登録してください。

【お願いしたいこと】
・登録する前に、同じ会社名や担当者がSalesforceに既にいないか確認してください
・もし既にあれば、新しく作らずそちらに紐付けてください
・予算が「〜万円」のように幅がある場合は、真ん中の金額で登録してください
・「来年度」「半年後」などは具体的な日付に直してください（日本の年度＝4月始まり）
・登録が終わったら、何を作ったか一覧で見せてください

【商談メモ】
先週金曜、XYZ物流の管理本部・本部長の高橋誠さんと初回MTG（紹介経由）。
現行は自社DC内の物理サーバーで基幹系DBを運用。保守切れが来年6月に迫っており、
クラウド移行を検討中。予算は2000万〜3000万で、
今期中（2027年3月末まで）に本番移行を完了したい意向。
まずは11月に2週間程度のPoCで性能検証をしたいとのこと。
移行対象は約3TB、夜間バッチの処理時間が現行4時間→2時間以内が目標。
高橋さんの連絡先: makoto.takahashi@xyz-logistics.co.jp
同席していた情シスの中村主任（nakamura@xyz-logistics.co.jp）が技術窓口になる予定。
競合あり（クラウドDB系マネージドサービス）。
既存SIerとの関係もあるので、提案はSIer経由でも可とのこと。
```

実際に出力された回答です。  
![](https://static.zenn.studio/user-upload/deployed-images/ef92f561bb19a4083f525d04.png?sha=ae1576cb39c861aafb10e607f82f6a7c41c3f58c)

間違った値を登録してしまったことを認めた上で修正したい旨を促してきましたね。  
なお、2500万**ドル**で登録していますが、Salesforce側で**マルチ通貨の有効化**をONにしていないので組織全体の既定通貨（現在USD）で扱われます。  
![](https://static.zenn.studio/user-upload/deployed-images/170b5cebc57fc7c4db693ac8.png?sha=8f1d9667941df5ca6c7f72a37cced77a57c9dbc3)

Salesforce を確認すると意図した通りに登録されていることを確認しました。  
![](https://static.zenn.studio/user-upload/deployed-images/f074ce55ff3dea4a16614c56.png?sha=55f8aeee87c53670f29fdd7dfaae1a6c978e9196)  
![](https://static.zenn.studio/user-upload/deployed-images/5b6dbad4d8ad30ef4284dfa0.png?sha=8c934ae7cef1fe92ca397e2c319553763234c58f)

### 4.3 ユースケース2(Task/Event自動登録)

従来では以下の様な課題が発生したと思います。

* 会議後に議事録は書くが、**Salesforceへの反映を忘れる**
* アクションアイテムは議事録に埋もれて**フォローが漏れる**
* 会議参加者とSalesforce上のContactの紐付けが面倒

AIエージェントを使うことにより、以下の工程を自動化することができます。

1. 参加者の特定 → Contact検索
2. 関連Opportunity/Accountの特定
3. アクションアイテム、日程情報などの抽出
4. Task/Eventの作成、Opportunity更新

以下のプロンプトを投げます。

```
以下の議事録を読んで、Salesforceにやるべきことと次の打ち合わせを登録してください。

【お願いしたいこと】
・「誰が何をいつまでにやるか」を読み取って、タスクとして登録してください
・自分たちがやることは「未着手」、相手待ちのものは「相手待ち」にしてください
・次の打ち合わせがあれば予定として登録してください（終了時間がなければ1時間で）
・この議事録に関係する商談があれば、進捗状況も更新してください
・新しい人が出てきてSalesforceに登録されていなければ、追加していいか聞いてください
・最後に、何を登録・更新したか一覧で見せてください

【議事録】
2026/10/8（火）14:00-15:30 定例MTG＠XYZ物流 本社5F会議室

出席者:
・XYZ物流: 高橋本部長、中村主任、山本課長（セキュリティ担当、今回初参加）
・当社: 佐々木、小林

話した内容:

1. PoC結果の報告
  - クラウドDB（PostgreSQL互換）への移行PoCを9月に実施した
  - 結果: 夜間バッチが4時間から1.5時間に短縮（目標の2時間以内をクリア）
  - 通常の処理速度も問題なし
  - 高橋本部長「想定以上の結果。社内稟議を進めたい」

2. セキュリティの確認（山本課長から）
  - PCI DSS対応が必須（決済系データがあるため）
  - クラウド事業者のコンプライアンスレポートで対応可能と説明 → 了承
  - 社内ネットワークからの閉域接続が必要 → 設計に反映する

3. 今後のスケジュール
  - 11月: 詳細設計とセキュリティレビュー
  - 12月〜1月: 本番環境の構築とデータ移行テスト
  - 2月: 並行稼働
  - 3月第1週: 本番切替

4. 見積もりについて
  - 高橋本部長から「11月中に見積もりを出してほしい」
  - SI部分はパートナーのDEFシステムズが担当する方向

やること:
- 佐々木: 詳細設計書と見積書を作成（11/15まで）
- 小林: 閉域接続の構成図を作成（10/18まで）
- 中村主任: 既存システムの構成図とバッチ一覧を共有（10/15まで）
- 山本課長: セキュリティチェックリストの提供（10/22まで）
- 次回: 10/25（金）15:00 XYZ物流にて（設計レビュー）
```

![](https://static.zenn.studio/user-upload/deployed-images/6fd4a40e711b9e89e683a41f.png?sha=6df143f0c02318fdae10eaad6dffc7e574614b93)  
![](https://static.zenn.studio/user-upload/deployed-images/c4e6db8aebf0bd1c727effd2.png?sha=5862b4b20ab5d9b03e5f52db7cd173cce673ac49)  
![](https://static.zenn.studio/user-upload/deployed-images/ff06b9fd10ab7b1cc62c6196.png?sha=390c8e33bd13a5ce2ffb684e3a6106b636d7c043)

Salesforce 側を確認すると、山本課長が登録されていることを確認できました。  
![](https://static.zenn.studio/user-upload/deployed-images/0ac3d88ae07ba4bd0909a805.png?sha=c7b98c1da1d50b33797d5870aa109117937a993e)

商談を確認すると複数のTODOを確認できます。  
![](https://static.zenn.studio/user-upload/deployed-images/ebf1588de31349a536ee5302.png?sha=e3d602012831d1804675f720a7cf2cc53f4f7304)

## ネットワーク要件

Salesforce Hosted MCP Server は **Salesforce がホストするリモート MCP サーバー**です。Claude Desktop から直接 Salesforce のエンドポイントに HTTPS で接続します。以下のアウトバウンドアクセスが必要です。

| ホスト | 目的 |
| --- | --- |
| api.salesforce.com | MCP 通信 |
| login.salesforce.com | OAuth 認証 |

## 認証・認可に関する FAQ

### Q1. 認証にはどのフローが使われる？

OAuth 2.0 Authorization Code Flow + PKCE です。  
初回接続時にブラウザが開き、Salesforce へのログインと MCP アクセスの許可を求められます。認証後はリフレッシュトークンが保存されるため、トークンが有効な間は再ログイン不要です。

### Q2.「誰にどのオブジェクト・レコードを見せるか」はどう制御する？

Salesforce の既存アクセス制御がそのまま適用されます。  
MCP Server 経由のアクセスは、OAuth で認証したログインユーザーの権限で実行されます。

* プロファイル / 権限セットで「オブジェクトの CRUD 権限」を制御
* 組織の共有ルール / ロール階層で「どのレコードが見えるか」を制御
* フィールドレベルセキュリティで「どのフィールドが見えるか」を制御

Salesforce は「ログインユーザー単位」で認可が効くため、ユーザーごとの出し分けはより直感的です。

### Q3. トークンの有効期限はどうなっている？失効した場合はどうなる？

Salesforce のアクセストークンは組織のセッションタイムアウト設定に従います。アクセストークンが失効すると、クライアントはリフレッシュトークンを使って新しいアクセストークンを自動取得します。

リフレッシュトークンについては、External Client App の OAuth Policies で以下を設定できます。

| 設定項目 | デフォルト | 推奨設定 |
| --- | --- | --- |
| Refresh Token Validity | 無期限（Revoke されるまで有効） | 30日等、組織ポリシーに合わせて設定 |
| Refresh Token Rotation | 無効 | **有効**（トークン再利用攻撃の防止） |

Refresh Token Rotation を有効にすると、リフレッシュトークン使用時に新しいトークンが発行され、古いトークンは無効化されます。万が一トークンが漏洩した場合のリスクを低減できます。

### Q4. ユーザーが退職・異動した場合、MCP 経由のアクセスはどう無効化する？

以下の方法で即座に無効化できます:

1. **Salesforce ユーザーの無効化（Deactivate）**: ユーザーアカウントを無効にすれば、そのユーザーの OAuth トークンも無効になり、MCP 経由のアクセスは即座に遮断されます。
2. **個別トークンの取り消し**: ユーザーの詳細ページから、特定アプリのトークンを個別に Revoke できます。他の Connected App への接続を維持したまま MCP だけ切断する場合に有効です。
3. **Single Logout の活用**: External Client App で Single Logout を有効にすると、Salesforce セッションの取り消しが MCP クライアントセッションの終了に連動します。
4. **Enterprise IdP 連携（大規模組織向け）**: MCP 仕様の「Enterprise-Managed Authorization」拡張により、企業の IdP（Okta, Azure AD 等）でのユーザー無効化が即座にすべての MCP クライアントへ伝播する構成も可能です。

## まとめ

Claude Desktop (Cowork) on Amazon Bedrock に Salesforce Hosted MCP Server をリモート MCP サーバーとして接続することで、会話の中から Salesforce のデータに直接アクセスできるようになりました。

* Salesforce がホスト・運用するリモート MCP のため、ローカルにサーバーを立てる必要がない
* OAuth 2.0 + PKCE で認証し、Salesforce の既存アクセス制御（プロファイル・共有ルール）がそのまま適用される
* MCP によって読み取りのみや読み書き両対応である。また、レコードの検索だけでなく作成・更新・削除もエージェントが実行可能

ユースケースで確認した通り、単に SOQL を代行するだけでなく、**営業メモや議事録のような非構造化テキストからエージェント自身がフィールドマッピングを判断し、重複チェック → レコード生成 → フォローアップ Task 登録まで一気通貫で実行してくれる**のが AI エージェント × CRM の面白さです。

## 参考リンク
