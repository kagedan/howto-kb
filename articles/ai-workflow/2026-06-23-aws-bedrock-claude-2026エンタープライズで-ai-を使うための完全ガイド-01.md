---
id: "2026-06-23-aws-bedrock-claude-2026エンタープライズで-ai-を使うための完全ガイド-01"
title: "AWS Bedrock × Claude 2026──エンタープライズで AI を使うための完全ガイド"
url: "https://note.com/fragments_jp/n/ndf670c130d94"
source: "note"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "note"]
date_published: "2026-06-23"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

Claudeを使うなら、Anthropicに直接APIキーを発行してもらうのが一番速い。そう思って始めると、エンタープライズではたぶん損する。

最初の私がそうだった。直APIで作ったPoCを社内に出した瞬間、情シスに止められた。「そのAPIキー、誰が管理してる? データはどこのリージョンに飛んでる? 監査ログは?」。3つとも答えられなかった。

AWS Bedrock経由なら、この3つに最初から答えがある。同じClaudeを、AWSのIAM・リージョン・コスト管理に乗せて使える。直APIより一手間多いように見えて、エンタープライズでは結果的に近道だった。

順に、なぜそうなるかとコードを出していく。

---

## 「直APIで十分」が通らない場面の話だ

個人開発なら直APIでいい。これははっきりしている。Bedrockの一手間は無駄だ。

でも組織で使うと、必ずこの3つを聞かれる。

* **データはどこで処理されている?** ── 直APIだと「Anthropicのサーバー」としか言えない
* **APIキーは誰が・どう管理している?** ── キー一本の漏洩が全社事故になる
* **AIのコストはどう可視化している?** ── 請求書が別建てで、他のインフラと突き合わせられない

Bedrockはこれを構造で解く。

* データは指定リージョン（ap-northeast-1）内で処理され、国外に出ない
* 認証はIAM。APIキーという概念自体が消える。既存のIAM体制にそのまま乗る
* コストはAWS Cost Explorerで他のインフラと一元管理。SOC2やISO 27001といったAWSの認証もそのまま使える

「IAMの設定が面倒そう」と思うかもしれない。でもキーを各自が.envに貼って祈る運用より、IAMロール一つで縛るほうが圧倒的に楽だ。一度やればわかる。

---

## セットアップ：IAMポリシーとモデルアクセス

まずInvoke権限を絞ったポリシーを作る。リソースをClaude系だけに限定するのがポイントだ。

```
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
    ],
    "Resource": [
      "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-*"
    ]
  }]
}
```

そのあとAWSコンソール → Amazon Bedrock → Model access からClaudeモデルをリクエストする。初回だけ。承認は数分〜数時間。2026年現在、Bedrock経由で使える主なClaudeはこれだ。

```
anthropic.claude-opus-4-8-v1:0     最高性能
anthropic.claude-sonnet-4-6-v1:0   バランス型
anthropic.claude-haiku-4-5-v1:0    高速・低コスト
```

---

## まず動かす：Anthropic SDKでBedrockを叩く

boto3で生のJSONを組み立てる方法もあるが、正直しんどい。anthropic SDKがBedrock対応のクライアントを持っているので、こっちから始めるのを勧める。

```
import anthropic

# IAMロール使用時は鍵の指定すら不要
client = anthropic.AnthropicBedrock(aws_region="ap-northeast-1")

message = client.messages.create(
    model="anthropic.claude-sonnet-4-6-v1:0",
    max_tokens=1024,
    messages=[{"role": "user", "content": "日本語で説明してください"}]
)
print(message.content[0].text)
```

直APIのコードとほぼ同じ形で書ける。違いは Anthropic() が AnthropicBedrock(aws\_region=...) になるだけ。**直APIで書いた既存コードの移植コストがほぼゼロ**なのが、Bedrockを選ぶ地味だが大きい理由だ。

boto3を使いたい場合の生の形も置いておく。Guardrailsを付けたいときなどはこちらが要る。

```
import boto3, json

bedrock = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

def call_claude(prompt: str, model_id: str = "anthropic.claude-sonnet-4-6-v1:0") -> str:
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    })
    response = bedrock.invoke_model(
        body=body, modelId=model_id,
        accept="application/json", contentType="application/json"
    )
    return json.loads(response["body"].read())["content"][0]["text"]
```

ハマりどころを先に言う。anthropic\_version は "bedrock-2023-05-31" で固定。直APIの値とは違う。ここを直APIのままにして1時間溶かした。

---

## Guardrailsで「漏らしてはいけないもの」を止める

エンタープライズで効くのがこれだ。PII（個人情報）の自動マスク、有害コンテンツのフィルタ、根拠のない回答の拒否を、モデル呼び出しに被せられる。

```
response = bedrock.invoke_model(
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }),
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    guardrailIdentifier="your-guardrail-id",
    guardrailVersion="1",
)
```

止められるもの: 有害コンテンツ / 特定トピックの拒否 / PII検出・マスキング / グラウンディング（根拠のない回答の拒否）。アプリ側でフィルタを書くより、ここに寄せたほうが監査が通りやすい。

ここまでが「なぜBedrockなのか」と、最初の一歩だ。直APIとの差、IAMでの認証、Guardrailsまで出し切った。

ここから先は本番運用の話になる。Bedrockには直APIにない固有のつまずきがある──スロットリング（ThrottlingException）、Provisioned Throughput、リージョン別の価格。これを踏まえた**本番で落ちないBedrock実装パターン**を、全コードで公開する。トークンコストの実測・自動フォールバック・マネージドRAG（Knowledge Base）の呼び出しまで、コピペで動く形で渡す。

## 有料パート：本番で使える Bedrock 実装パターン集
