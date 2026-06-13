---
id: "2026-06-11-bedrock-の-claude-fable-5-で-data-retention-エラーが出たら-01"
title: "Bedrock の Claude Fable 5 で data retention エラーが出たら ― CloudShell だけで解決する"
url: "https://qiita.com/shohei_yamamoto/items/eb12e595e193b100a94f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "Python", "qiita"]
date_published: "2026-06-11"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは。スタディング開発担当の山本です。
最近の悩みは、AIコードレビューの指摘をどこまで受け入れてリリースするかです。

さて、2026年6月9日にAnthropicの最上位モデル **Claude Fable 5** がAmazon Bedrockで利用可能になりました。早速GitHub ActionsのClaude Code Action（PR 自動レビュー）のモデルをBedrock上のFable 5に差し替えたところ、初手で以下のエラーに怒られました。

:::note alert
API Error: 400 data retention mode 'default' is not available for this model
:::

Opus 4.8 / Sonnet 4.6 / Haiku 4.5 は同じ設定で動いているのに、 **Fable 5 だけが 400エラーで失敗** します。弊社のケースでは、モデルアクセスの問題でも IAM の問題でもありませんでした。

結論から言うと、 **Fable 5 の利用には data retention（データ保持）設定の opt-in が必要** で、これは **AWS CloudShell 上の 3ステップ（CLI 更新 → 現状確認 → 設定変更）** で解決できます。ローカル環境の構築もPythonスクリプトも不要です。

## 対象読者

- Amazon Bedrock で既に Claude（Opus / Sonnet / Haiku）を利用している方
- Claude Fable 5に切り替えようとして上記のエラーに遭遇した方
- ローカルにAWS CLI環境を作らず、ブラウザだけで設定を済ませたい方

## 何が起きているのか

### エラーの原因

Claude Fable 5（および Claude Mythos 5）は、Anthropicの新しいMythosクラスのモデルで、trust & safety（不正利用検知）の要件として **プロンプトと出力をAnthropicと共有し、最大30日間保持すること** が利用条件になっています。

Bedrockにはアカウント単位の data retention mode という設定があり、モデルごとに「許可される mode」が定められています。

| モデル | 許可される mode |
|---|---|
| Claude Opus 4.8 など従来モデル | `default`, `provider_data_share` |
| **Claude Fable 5 / Mythos 5** | **`provider_data_share` のみ** |

data retention mode はプロジェクト → アカウント → モデル既定値の順に解決され、新規アカウントの設定値は `inherit`（未指定）です。未指定の場合はモデル既定の `default` が有効モードとして適用されますが、Fable 5 の許可リストに `default` は含まれていないため、モデルが `unavailable`（利用不可）扱いとなり、呼び出しが 400エラーでブロックされます。これが冒頭のエラーの正体です。

※ エラー文言は経路によって異なり、コンソールやAPI上では "This model is not available under data retention mode 'default'." と表示されることもあります。

### data retention mode の種類

| mode | 説明 |
|---|---|
| `default` | モデル既定の取り扱い。データはモデル提供者（Anthropic）に共有されない |
| `none` | データ保持なし（ZDR）。利用には審査が必要なモデルあり |
| `provider_data_share` | モデル提供者へのデータ共有を許可。**Fable 5 の利用に必須** |
| `inherit` | このスコープでは指定せず、より広いスコープの設定に委ねる。**新規アカウントの既定値** |

詳細は [AWS 公式ドキュメント（Data retention）](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)を参照してください。

## 解決方法: CloudShell で 3ステップ

この設定は執筆時点でマネジメントコンソールに設定画面が存在せず、**API / CLI からのみ変更できます**（[公式モデルカード](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html)に "There is no console UI for this setting at launch" と明記されています）。

opt-in は AWS CLI の `aws bedrock put-account-data-retention` コマンドで設定できます。ただしこのコマンドは **AWS CLI 2.35.1（2026年6月9日リリース）で追加されたばかり** で、手元のCLIやCloudShellのプリインストール版では未対応の場合があります。

そこで **CloudShell 上で CLI を最新化してから実行** すれば、ブラウザ上で完結可能なため、ローカル環境の構築も不要です。

### 事前準備

- 対象アカウントで既に Bedrock の Claude（Opus / Sonnet / Haiku など）が利用できていること
  - この場合、モデル利用規約への同意や use case フォームの提出は済んでいるため、**Fable 5 のための追加の同意手続きは不要** です。必要なのは本記事の data retention 設定だけです
  - ※Fable 5はAWS Marketplace上だと別商品のため、EULA への同意とサブスクリプション作成は初回呼び出し時に自動で行われます（`aws-marketplace:Subscribe` 権限が必要。SCP等でブロックしている組織は事前の解除が必要です）
- マネジメントコンソールに、以下のIAM権限を持つユーザー/ロールでログインしていること
  - `bedrock:GetAccountDataRetention`
  - `bedrock:PutAccountDataRetention`
- CloudShellを起動しておくこと（コンソール上部のナビゲーションバーにあるターミナルアイコンから起動できます）

![コンソール上部のナビゲーションバー右側にある CloudShell の起動アイコン](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3927485/43fa3b40-1c58-4a6e-b5cc-7977b0494cd0.png)

※ Fable 5へのアクセス自体は全AWSアカウントへ段階的に展開中です（[AWS 公式ブログ](https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/)）。retention設定後もアクセス拒否系のエラーになる場合は、展開待ちの可能性があります。

:::note warn
この設定は**アカウント全体**に適用され、設定後はFable 5の入出力がAnthropicに共有されるようになります。本番ワークロードと同居するアカウントでは、実行前に後述の「注意点」も確認してください。
:::

### Step 1. AWS CLI を最新化する

CloudShellで以下を実行します。[AWS CLI 公式のインストール手順（既存バージョンの更新）](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/getting-started-install.html)そのままです。

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
```

更新できたか確認します。 **2.35.1 以上** であればOKです。

```bash
aws --version
```

※ CLIが 2.35.1 未満のまま実行すると、`put-account-data-retention` がサブコマンドとして存在せず `Invalid choice` エラーになります。

※ CloudShellでは `$HOME` 以外に配置したファイルが **セッション終了時に削除される** ため、この更新は今のセッション限りです。今回は一度きりの設定作業なので問題ありませんが、恒久的に最新CLIを使いたい場合は[公式のCloudShell向け手順](https://docs.aws.amazon.com/cloudshell/latest/userguide/vm-specs.html)（`$HOME` 配下へのインストール）を参照してください。

### Step 2. 現在の設定を確認する

以降のコマンドの `--region ap-northeast-1` は **東京リージョンで推論する場合の例** です。別のリージョンでBedrockを利用している場合は、実際に推論を行うリージョンに読み替えてください。

```bash
aws bedrock get-account-data-retention --region ap-northeast-1
```

未設定であれば `inherit`（新規アカウントの既定値）が返ってきます。弊社の環境でも `inherit` でした。

![get-account-data-retention の実行結果。mode: inherit が返ってきている](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3927485/e47dc960-f3ab-4293-90ef-0e650f732de5.png)

`inherit` は「アカウントとしては未指定」の状態で、この場合はモデル既定の `default` が有効モードになります（これが冒頭のエラーの状態です）。`default` が返ってきた場合も同様に、そのまま Step 3 に進んでください。

### Step 3. provider_data_share に変更する

```bash
aws bedrock put-account-data-retention --mode provider_data_share --region ap-northeast-1
```

成功すると、設定後の `mode` と更新時刻 `updatedAt` がレスポンスで返ってきます。

![put-account-data-retention の実行結果。mode: provider_data_share と updatedAt が返ってきている](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3927485/576c9493-509e-4db0-b96a-2534b13282ca.png)

`"mode": "provider_data_share"` になっていれば設定完了です（再度 `get-account-data-retention` を実行しても確認できます）。

### 動作確認

Fable 5を呼び出してみます。推論時のモデルIDは `global.anthropic.claude-fable-5`（Global cross-region inference profile）です。

弊社の環境では、設定変更後に GitHub Actions の Claude Code Action（`--model global.anthropic.claude-fable-5`）を再実行したところ、 **前回 400 エラーで落ちていたジョブがそのまま成功** しました。コード変更は一切不要で、アカウント設定だけの問題だったことが分かります。

## 注意点

設定コマンド自体はワンライナーですが、影響範囲は理解しておく必要があります。

### 設定はアカウント全体に適用される

`put-account-data-retention` は **account-wide（アカウント全体）の設定** です。`--mode` 以外の引数はなく、モデル単位での指定はできません。

ただし、共有が実際に発生するかはモデルごとの要件によります。公式ドキュメントによると、Opus 4.8のような従来モデルは **`provider_data_share` 設定下でもデータは AWS の境界内に留まります**。Anthropicへの共有・30日保持が発生するのは、それを利用条件とするモデル（Fable 5 / Mythos 5）の呼び出しです。

### データの扱い

- Fable 5へのプロンプトと出力は **Anthropic に共有され、最大30日間保持** されます（[AWS 公式](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)）
- 保持の目的は trust & safety（不正利用検知）です。[Anthropic の公式ヘルプ](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)によれば、商用プロダクトの入出力は **既定ではモデルの学習に使われません** （フィードバックの送信や明示的なオプトインをした場合を除く）
- とはいえ「データが AWS の外に出ない」前提でBedrockを選定している組織では、本番アカウントに設定する前に社内のセキュリティ・コンプライアンス部門への確認をおすすめします

### その他

- 設定を元に戻すには `--mode default` で再実行します（当然ながらFable 5は再び使えなくなります）
- リージョン間で設定がどう伝播するかは公式に明記されていないため、 **実際に推論するリージョンを `--region` に指定して設定・確認** するのが確実です
- Fable 5にはセーフガード機構があり、リクエストが内蔵のsafety classifierで拒否されてOpus 4.8にフォールバックした場合、そのフォールバック呼び出しもFable 5と同じデータ取り扱い（Anthropic共有）になります（[公式ドキュメント](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)に記載）

## まとめ

| 項目 | 内容 |
|---|---|
| エラーの原因 | Fable 5はdata retention modeが `provider_data_share` でないと利用不可 |
| 解決方法 | `aws bedrock put-account-data-retention --mode provider_data_share` |
| AWS CLI | 2.35.1 以上（CloudShellのプリインストール版は要更新） |
| 設定の範囲 | アカウント全体。モデル単位の指定は不可 |
| データの扱い | Fable 5の入出力はAnthropicへ共有・最大30日保持。既定では学習には使われない |
| 元に戻す | `--mode default` で再実行（Fable 5は使えなくなる） |

新モデルが「モデルアクセスを有効化しても使えない」というのは初見だと面食らいますが、原因が分かればopt-in自体はワンライナーです。CloudShellならブラウザだけで完結するので、ぜひ Fable 5を試してみてください。

---

本記事は 2026年6月11日時点の情報に基づいています。data retentionの仕様やコンソールUIの対応状況は今後変わる可能性があるため、最新情報は公式ドキュメントを確認してください。

## 参考

- [Data retention - Amazon Bedrock（AWS 公式）](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)
- [put-account-data-retention - AWS CLI リファレンス](https://docs.aws.amazon.com/cli/latest/reference/bedrock/put-account-data-retention.html)
- [AWS CLI のインストールまたは更新（AWS 公式）](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/getting-started-install.html)
- [Anthropic Claude Fable 5 on AWS（AWS 公式ブログ）](https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/)
- [Claude Fable 5 を Amazon Bedrock で使ってみた（DevelopersIO）](https://dev.classmethod.jp/articles/claude-fable-5-bedrock/)

## KIYOラーニング株式会社について

当社のビジョンは『世界一「学びやすく、分かりやすく、続けやすい」学習手段を提供する』ことです。革新的な教育サービスを作り成長させていく事で、オンライン教育分野でナンバーワンの存在となり、世界に展開していくことを目指しています。

https://kiyo-learning.com/

### プロダクト

- [スタディング](https://studying.jp/)：「学びやすく・わかりやすく・続けやすい」オンライン資格対策講座
- [スタディングキャリア](https://career.studying.jp/)：資格取得者の仕事探しやキャリア形成を支援する転職サービス
- [AirCourse](https://aircourse.com/)：受け放題の動画研修がついたeラーニングシステム（LMS）

### KIYOラーニング株式会社では一緒に働く仲間を募集しています

https://herp.careers/v1/kiyolearning
