---
id: "2026-06-23-amazon-connect-customer-で-ai-agent-を構築する際に詰まりがちなポイ-01"
title: "Amazon Connect Customer で AI Agent を構築する際に詰まりがちなポイントを整理してみた"
url: "https://zenn.dev/aws_japan/articles/2a122e21269f06"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

Amazon Connect Customer の AI Agent 機能により、様々な要件に対応したセルフサービスを実装できるようになりました。一方で、いざ手を動かしてみると「プロンプトが反映されない」「Lambda が呼ばれない」といった地味な詰まりポイントに遭遇しがちです。

本記事では、飲食店の電話予約一次対応を AI 音声ボットで自動化するシステムを構築する過程で踏んだハマりどころを整理しました。同様の構成を検討中の方の参考になれば幸いです。

## 構築した構成

飲食店の電話予約における一次対応を AI Agent で自動化する構成です。

* AI Agent が DynamoDB を参照し、予約の空き状況をリアルタイムに回答
* 予約の意思を確認した時点で人間のオペレーターにエスカレーション
* FAQ（営業時間、定休日等）にも対応

```
電話 → Amazon Connect Customer → Lex → AI Agent
  → AgentCore MCP Gateway → API Gateway → Lambda → DynamoDB
```

なお、今回のアセット生成には [AICC Builder](https://github.com/aws-samples/sample-aicc-builder-for-amazon-connect-ai-agent) を使用しました。Lambda コードや OpenAPI Spec、AI プロンプト、Contact Flow 等を会話ベースで一括生成できる OSS ツールです。生成されたアセットをデプロイし、コンソールで接続設定を行うことで構築を完了しました。

## 詰まりポイント集

ここからが本記事の主要部分です。AI Agent の構築の過程で、遭遇した問題を整理します。

### 修正した AI Agent のプロンプトが反映されていない

AI Agent のプロンプトを編集 → Publish を実行しても、古い応答が返り続けるケースがあります。原因は、Contact Flow の「顧客の入力を取得する」ブロックにおいて、AI Agent のバージョンがが固定値に設定されていたことでした。Publish のたびにバージョン番号はインクリメントされますが、Contact Flow 側は古いバージョンを参照していたままでした。

**解決策:** AI Agent のバージョンを `$LATEST` に変更する。

![](https://static.zenn.studio/user-upload/ceb2ed399b24-20260623.png)

本件は後述のモデル呼び出しログで、意図したプロンプトとは異なるものが使用されていることが観測できたことで、原因特定に至りました。

![](https://static.zenn.studio/user-upload/81f2b2744b21-20260623.png)

### プロンプトの更新が確実に反映されているか確認する

上記とは別に、Publish 成功かつバージョン番号がインクリメントされているにも関わらず、AI agent designer 画面でプロンプト本文を確認すると古い内容が表示されるケースがあります。

**解決策:** プロンプトを更新した際は、テスト前に必ず AI agent designer → 対象エージェント → プロンプトを確認してみてください。

![](https://static.zenn.studio/user-upload/cbf2f5736ec6-20260623.png)

### MCP ツールが呼ばれているのに Lambda が動かない

AI Agent がツールを呼び出しているにも関わらず Lambda の CloudWatch ログが出力されない場合、MCP Gateway が参照している接続先 URL が正しいかを確認してください。

AgentCore Gateway の Target に設定された OpenAPI Spec の `servers.url` が、実際の API Gateway エンドポイントと一致しているかがポイントです。API Gateway を再作成した場合などに URL が古いまま残り、存在しないエンドポイントへリクエストを送信し続けることがあります。

**解決策:** OpenAPI Spec 内の `servers.url` と、実際に稼働している API Gateway のエンドポイント URL が一致しているか確認します。

![](https://static.zenn.studio/user-upload/ba736dee1887-20260623.png)

### Lex が AI Assistant にアクセスできていない

```
ValidationException: Amazon Lex could not access your Q In Connect Assistant
```

**解決策:** Amazon Connect Customer コンソール → 問い合わせフロー → Amazon Lex セクション → 一度無効化 → 保存 → 再度有効化 → 保存。これによりサービスロールが再プロビジョニングされます。

![](https://static.zenn.studio/user-upload/9f47b0d86b06-20260623.png)

### ユーザーが発話した瞬間に「システムエラー」で切断される

Contact Flow の初回挨拶（Play prompt）は正常に再生されるが、ユーザーが発話した瞬間にフローが Error 分岐に落ち、切断される事象がありました。

**解決策:** 「顧客の入力を取得する」ブロック → **AIエージェントを有効にする** にチェック → 「ドメインを選択」で AI Agent 名とバージョン`$LATEST`を指定します。（先ほどと同様の対応）  
![](https://static.zenn.studio/user-upload/8f366e810486-20260623.png)

## トラブルシューティングで有効だった手法

**モデル呼び出しログ**がトラブルシューティングに有効でした。

AI Agent が実際にどのモデル・どのプロンプトを使用しているか、LLM への入力と出力を全文確認できます。上記のプロンプトのバージョン固定問題は、このログで想定外のプロンプト名が表示されていることに気づいて初めて原因特定に至りました。

2026年6月時点で Connect コンソールからは設定できず、API 経由で有効化する必要があります。

> To enable logging for Connect AI agents, you use the CloudWatch API. Complete the following steps.

<https://docs.aws.amazon.com/connect/latest/adminguide/monitor-ai-agents.html>

```
# 以下はコマンド例です
aws logs put-delivery-source \
  --name "connect-model-invocation" \
  --resource-arn "arn:aws:connect:{REGION}:{ACCOUNT}:instance/{INSTANCE_ID}" \
  --log-type "MODEL_INVOCATION_LOGS"

aws logs put-delivery-destination \
  --name "connect-model-logs-dest" \
  --output-format "json" \
  --delivery-destination-configuration \
    "destinationResourceArn=arn:aws:logs:{REGION}:{ACCOUNT}:log-group:/aws/connect/model-invocation-logs"

aws logs create-delivery \
  --delivery-source-name "connect-model-invocation" \
  --delivery-destination-arn "arn:aws:logs:{REGION}:{ACCOUNT}:delivery-destination/connect-model-logs-dest"
```

動作に問題がある場合は、このログを確認することで解決の手掛かりが得られるかもしれません。Contact Flow ログや Lambda ログと組み合わせることで、多くの問題を切り分けることが可能です。

## まとめ

同じような事象で詰まっている方の参考になれば幸いです。誤りや追加情報があればコメントで教えていただけると助かります。また今回アセット生成に使用した [AICC Builder](https://github.com/aws-samples/sample-aicc-builder-for-amazon-connect-ai-agent) は aws-samples で OSS として公開されています。興味のある方はぜひ試してみてください。
