---
id: "2026-07-08-amazon-bedrockのdata-retention-01"
title: "Amazon BedrockのData retention"
url: "https://qiita.com/tkazuaki0820/items/95aca04e627393f1926c"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

今回は、Amazon BedrockのData retentionにを解説する解説となります。

Amazon Bedrockではデフォルトでは、AWSに入力したデータはAWS内だけで処理され、AWS外には行かない。  
LLM提供ベンダにもデータはいかず、モデルの再学習にも利用されない。という仕様となっております。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3990360%2Fb94efa8b-ef49-4c0c-b711-3b6659f151fd.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=9315395805d4d790c6b8f673ff5d86c1)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3990360%2Fb94efa8b-ef49-4c0c-b711-3b6659f151fd.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=9315395805d4d790c6b8f673ff5d86c1)

Amazon BedrockのData retention設定を変更すると、LLM提供ベンダにもユーザが入力したプロンプトデータを提供する方式になります。  
Anthropic社のClaude Fableを利用するためにはこの設定が必須となる。  
ユーザが入力したデータをAnthropic社に提供することとなるので、セキュリティ要件を確認したうえで設定を有効化する＆  
設定有効化後は機密情報を入れないようにしてください。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3990360%2F1ee63010-a040-4727-aed3-67b88ad46bae.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=143a3aa9fa20797fbbab3181ea46cf1a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3990360%2F1ee63010-a040-4727-aed3-67b88ad46bae.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=143a3aa9fa20797fbbab3181ea46cf1a)

設定変更のコマンドは下記の公式サイトを参考に変更してください。  
実行する際は必ずセキュリティ要件を確認したうえで、設定を変えて問題ないことを確認してから実施してください。  
<https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html>
