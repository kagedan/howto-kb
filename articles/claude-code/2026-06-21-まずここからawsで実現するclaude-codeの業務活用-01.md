---
id: "2026-06-21-まずここからawsで実現するclaude-codeの業務活用-01"
title: "まずここから——AWSで実現するClaude Codeの業務活用"
url: "https://zenn.dev/akring/articles/5ae1fe7d1be4e5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "LLM", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

## 業務でのAI活用、何から始めるか

業務でAIを活かしたいけど、こんな壁を感じていないでしょうか。

* チャットで質問する使い方しか知らない。プログラムから組み込むのは難しそうだ
* 組織のセキュリティ審査を通る気がしない。データが外に出るのが怖い
* 動かせたとしても、改善するたびにコードを触らないといけないのは運用が重い
* AIが何をしたか追えない。監査で説明できる気がしない
* 導入コストや契約がよくわからない。AI利用は高額になりやすいと聞いている

この記事の「実は」はそれぞれその壁を取っ払う話です。筆者は **Claude Code CLIをCI/CDパイプラインに組み込み、デプロイ後のレポートを自動生成する** デモ（[Hephaestus](https://github.com/mahitotsu/hephaestus)）を作成しました。まず動くものを見てください。

## Hephaestusの概要

構成はシンプルです。GitHubにpushすると、CDK Pipelinesが起動し、CloudFormationデプロイが完了した後、CodeBuildがClaude Code CLIを呼び出します。Claude Codeは自律的にAWS APIを叩き、デプロイレポートをMarkdownで生成します。S3に保存され、Lambda Function URL経由でブラウザから確認できます。

![](https://static.zenn.studio/user-upload/974e4b392a97-20260620.png)  
*Hephaestusの概念図*

セットアップは3ステップで完了します。

```
git clone https://github.com/mahitotsu/hephaestus.git
cd hephaestus
npm ci
# cdk.json に connectionId を設定後
npx cdk bootstrap
npx cdk deploy HephaestusPipelineStack
```

[CDK Pipelines](https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/cdk-pipeline.html) の性質上、初回のみ `cdk deploy` が必要です。以降は main ブランチへの push だけでパイプラインが自動実行されます。

## なぜスクリプトではなくClaude Codeなのか

「同じことをシェルスクリプトで書けばいいのでは」と思うかもしれません。このユースケースをスクリプトで実装しようとすると、いくつかの壁にぶつかります。

* 何をするにもまずAWSのどのAPIを使えばいいか調べるところから始まります。コードを書いて、動かして、直して、という試行錯誤に思った以上に時間がかかります
* デプロイの内容によって「何に注目してレポートに書くべきか」が変わります。あらかじめ全パターンを想定してスクリプトに書いておくことはできません
* 収集した情報を人間が読みやすい要約やレポートとして整形できるのはLLMならではです。スクリプトには真似できません

Claude Code CLIはエージェントループを内包しています。プロンプトで「何をするか」を指示するだけで、Claude Codeが次に何をすべきか判断しながら実行します。改善したければプロンプトを変えるだけで、ループの実装には触れません。

## 実は①：追加契約不要、AWSアカウントだけで使える

上で述べたエージェントループは、Claude Code CLIというツールに内包されています。使うのに特別なことは何もありません。`npm install -g @anthropic-ai/claude-code` でインストールし、環境変数 `CLAUDE_CODE_USE_BEDROCK=1` を設定すればBedrockに向きます。あとは `claude -p "やってほしいこと"` とプロンプトを渡して実行するだけです。Hephaestusでは実際にこう呼び出しています。

```
claude -p "$TASK" \
  --model "$ANTHROPIC_MODEL" \
  --append-system-prompt-file /tmp/system_prompt.txt \
  --dangerously-skip-permissions \
  --max-turns 30 \
  --no-session-persistence
```

全体のコードは[こちら](https://github.com/mahitotsu/hephaestus/blob/main/scripts/build.sh)で確認できます。Anthropicとの直接契約は不要で、AWSアカウントさえあれば今日から始められます。詳細は[公式ドキュメント](https://code.claude.com/docs/ja/amazon-bedrock)を参照してください。

## 実は②：AWSでいつも使ってる統制がそのまま効く

「データが外に出るのが怖い、セキュリティ審査を通る気がしない」。その不安に構造で答えます。Claude Code CLIはBedrock経由で動作するため、通信経路やログ保存先を自社のAWSアカウント内で統制できます。その上で、Hephaestusはさらに2層のガードレールを仕込んでいます。

**推論が国内に閉じています。** JP Geographic Cross-Region Inference Profileを使用しています。これにより推論リクエストは日本国内（東京リージョン、大阪リージョン）にのみルーティングされ、意図せず海外リージョンで推論が走ることはありません。

**モデルが権限レベルで固定されています。** IAMポリシーで東京リージョン・大阪リージョンのHaiku 4.5 Foundation Model ARNだけを許可しています。jpプロファイル以外のモデルを呼び出そうとしても権限エラーで弾かれるため、設定ミスや悪意ある変更でモデルが差し替わることを防げます。

```
new iam.PolicyStatement({
  sid: 'BedrockInvokeHaikuOnly',
  actions: ['bedrock:InvokeModel', 'bedrock:InvokeModelWithResponseStream'],
  resources: [
    // jp.* クロスリージョン推論プロファイル（東京リージョン・大阪リージョン）
    `arn:aws:bedrock:ap-northeast-1:<account>:inference-profile/jp.anthropic.claude-haiku-4-5-20251001-v1:0`,
    // 実際に推論が走る Foundation Model ARN（東京リージョン・大阪リージョン）
    `arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0`,
    `arn:aws:bedrock:ap-northeast-3::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0`,
  ],
}),
```

これ以外のモデルARNは含まれていません。

## 実は③：プロンプトはコードから分離、コードを触らずに改善できる

「動かせたとしても、改善するたびにコードを触らないといけない」。その心配は要りません。プロンプトはAmazon Bedrock Prompt Managementでバージョン管理されています。CodeBuildの`pre_build`フェーズで最新版を取得する構成なので、プロンプトを変更するだけでレポートの内容や形式を更新できます。コードのデプロイは不要です。

改善の手順はこうです。AWSマネジメントコンソールでBedrock Prompt Managementを開き、Web画面上のフォームでプロンプトを編集して保存ボタンを押すだけ。次のパイプライン実行から新しいプロンプトが反映されます。コードエディタもターミナルも要りません。

プログラミングスキルのない担当者でも自分で改善できますし、エンジニアがプロンプトだけ渡して依頼することもできます。エージェントループの実装は自前で持たず、改善の入口をコードの外に出したことで、関われる人が増えます。

地味ですが、もう一つメリットがあります。プロンプトはBedrock上のリソースなので、IAMで取得権限を制御できます。`bedrock:GetPrompt`を許可した役割だけがプロンプトを取得できる構成にすれば、意図しない人やシステムにプロンプトを利用させないガバナンスも効かせられます。

参考までに、パイプラインがビルド開始時にプロンプトを取得する部分のコードを示します。

```
const [sys, task] = await Promise.all([
  client.send(new GetPromptCommand({ promptIdentifier: process.env.SYSTEM_PROMPT_ARN })),
  client.send(new GetPromptCommand({ promptIdentifier: process.env.TASK_PROMPT_ARN })),
]);
writeFileSync('/tmp/system_prompt.txt', sys.variants[0].templateConfiguration.text.text);
writeFileSync('/tmp/task_prompt.txt',   task.variants[0].templateConfiguration.text.text);
```

プロンプトのARNは環境変数で管理されており、スクリプト本体には一切埋め込まれていません。

## 実は④：全実行ログと詳細トレースが残る、監査にも耐えられる

「AIが何をしたか追えない」。Bedrockを使う構成ならその心配は要りません。Bedrock Model Invocation LoggingをオンにするとCloudWatchに全実行ログが記録されます。記録されるのはCodeBuildの実行ログだけではありません。Claude Codeがどのプロンプトを送り、モデルが何を返したか、Claude Codeがモデルを呼び出すたびの詳細なトレースまで残ります。消費トークン数やレイテンシも合わせて記録されるため、実行の全体像をあとから追えます。

しかもGitHubコミットからS3レポートまで、CodeBuildのビルドIDがBedrockログの`identity.arn`に埋め込まれます。10回のLLM呼び出しが全件ビルド単位で帰属できる「実行系譜」が自動的に形成されるわけです。CloudTrailとBedrockログを照合すれば、LLMの報告が事実と合致しているかまで独立した証拠源で検証できます。

実際に[サンプルのデプロイレポート](https://github.com/mahitotsu/hephaestus/blob/main/samples/report-example.md)生成時のBedrockログを分析した[後検証レポート](https://github.com/mahitotsu/hephaestus/blob/main/samples/bedrock-trace-example.md)を公開しています。この後検証レポート自体も、Claude Code（Opusモデル）が生成しました。「分析してほしい」と依頼しただけで、CloudWatchログやBedrockメトリクス、CloudTrailを自律的に収集・照合して分析しています。

この仕組みが機能した例を挙げます。後検証レポートでは、Claude Codeが「チェンジセットが存在しなかった」と報告しましたが、CloudTrailのタイムラインと照合すると事実と異なっていたことが判明しました。

| 時刻 (UTC) | 操作 | 状態 |
| --- | --- | --- |
| 15:59:24Z | `CreateChangeSet` | 作成完了 |
| 15:59:57Z | `ExecuteChangeSet` | 実行開始 |
| 16:00:16Z | スタック更新完了 | `EXECUTE_COMPLETE` で残存 |
| 16:01:06Z | LLMが `ListChangeSets` 呼び出し | ← この時点でチェンジセットは存在していた |

Claude Codeの説明が事実と異なっていても、CloudTrailという独立した証拠源で事後検証できます。最終レポートの内容は正確でしたが、何を根拠にその結論に至ったかまで追えるのがこの構成の強みです。

## 実は⑤：Haikuで十分、しかもコストが読める

「AI利用は高額になりやすい」という不安はよく聞きます。しかしこのデモでは、出力するレポートのテンプレートを明確に定義し、安価なモデル（Haiku 4.5）でも十分な品質が保てるようにしました。さらにプロンプトキャッシュも有効にしてトークン消費量を減らしています。

実際のサンプルレポートを見てください。変更サマリー、タイムライン、IAM変更の有無、リスク評価、確認チェックリストまで出力されています。[こちら](https://github.com/mahitotsu/hephaestus/blob/main/samples/report-example.md)から確認できます。

こうした工夫の効果も、Bedrock Model Invocation Loggingで確認できます。Claude Codeがモデルを呼び出すたびのトークン消費が記録されるため、新規入力トークンだけでなく、プロンプトキャッシュの書き込み・読み取りの内訳まで把握できます。実際のコストをリアルタイムで監視することもできます。

サンプルのデプロイレポート生成時の実測値はこうなっています。

```
呼び出し  新規入力   cache読み取り  cache書き込み
#1        2,650       0              0
#2            9       0             25,018
#3            4      20,491          4,709
#4            9      25,018          6,595
#5            3      25,200          6,818
#6            3      32,018            614
#7            2      32,632         21,348
#8            —      53,980              —
#9            —      55,504              —
#10           —      56,676              —
```

会話が進むにつれてキャッシュが積み上がり、後半の呼び出しでは新規入力トークンがほぼゼロに圧縮されています。このキャッシュ利用状況が可視化されることで、コスト構造を理解した上での改善策も立てやすくなります。このレポート生成1回あたりのコストは実測で約$0.16でした。稟議を通すときに数字で説明できます。

## 実行・観測・改善、サイクルはすでに揃っている

このデモを動かした瞬間から、実行→記録→AI観測→改善提案というサイクルを回せる基盤がすでに揃っています。手軽に始められますが、始めただけで終わりません。

AIが何をしているか詳細に追えるからこそ、「このパターンは毎回同じだ」という判断ができます。AIによる試行錯誤の末にパターンが見えてきたら、その部分をスクリプト化して固めていく、という段階的なアプローチも取れます。「AIで始めてスクリプトに育てる」という使い方です。

後検証レポートが示すように、同じClaude Codeを使えばパイプラインの観測記録を分析し、問題点を特定し、改善案を提示するところまで自動化できます。さらに進めれば、プロンプトの自動修正やパイプライン設定の自動更新も視野に入ります。「実行するエージェント」と「観測・改善するエージェント」を組み合わせることで、自律的に改善し続けるインフラ運用の入口に立てます。

## このサイクルを、次のユースケースへ

Hephaestusが示したのはデプロイレポートの自動生成という一例に過ぎません。しかし、ここで構築した基盤はそのまま次のユースケースに持ち込めます。AWSの統制機構、多くの人がプロンプトを改善できる仕組み、全実行ログの可観測性、コストの予測可能性。これらが全て揃った状態で、次のエージェントを動かせます。

* 障害発生時のCloudWatchログ収集と初期分析
* コスト異常検知後のリソース調査レポート
* セキュリティアラートのトリアージ

どのユースケースでも、プロンプトを書き換えるだけで同じ基盤の上に新しいエージェントが動き始めます。ガバナンスも、可観測性も、コストの透明性も、全て引き継がれます。

まずはデプロイレポート生成から始めてみてください。実行、観測、改善のサイクルは、すでに揃っています。
