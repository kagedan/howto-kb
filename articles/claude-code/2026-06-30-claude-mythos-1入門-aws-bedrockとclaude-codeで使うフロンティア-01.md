---
id: "2026-06-30-claude-mythos-1入門-aws-bedrockとclaude-codeで使うフロンティア-01"
title: "Claude Mythos 1入門 — AWS BedrockとClaude Codeで使うフロンティアセキュリティAI"
url: "https://qiita.com/kai_kou/items/392f9353d4bb73b56ee5"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "Python", "qiita"]
date_published: "2026-06-30"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

![Claude Mythos 1とClaude Code/AWS Bedrockを結ぶ統合イメージ](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/mythos-1-claude-code-bedrock-api-guide/01-hero.png)

## はじめに

2026年4月7日にAnthropicが「gated research preview」として公開した **Claude Mythos Preview** が、いよいよ **Claude CodeとClaude Securityへの統合準備段階** に入りました。

2026年5月26日ごろ、Claude Codeの公開インターフェイスに `claude-mythos-1-preview` というモデル文字列と「Access to the Claude Mythos model in Claude Code and Claude Security」という説明文が一時的に出現し、その後削除されたことを複数のメディアが報告しました。また、AWS Bedrockではすでに `anthropic.claude-mythos-preview` として新エンドポイント経由でアクセスが可能です。

この記事では、**Mythos 1の現在のアクセス方法・技術仕様・コードサンプル**、そしてClaude Codeへの統合準備の全貌を公開情報に基づいて整理します。

### この記事で解説すること

- Claude Mythos 1（`claude-mythos-1-preview`）の概要と最新動向
- AWS Bedrock経由でのアクセス方法とPythonコードサンプル
- Claude CodeとClaude Securityへの統合準備状況
- Project Glasswingの最新統計（2026-05-22時点）
- 開発者が今準備できること

### 対象読者

- Claude APIを使っているバックエンドエンジニア・AIエンジニア
- セキュリティエンジニア・AppSecチーム
- AWS BedrockでAnthropicモデルを利用しているチーム

### 注意

Mythos 1は2026年5月時点で **gated research preview** です。一般公開APIとしての提供は開始されていません。AWSのBedrock経由でのアクセスも、申請審査が必要な **Standard tierのみ** の提供です。

---

## TL;DR

- `claude-mythos-1-preview` がClaude Code・Claude Securityに統合準備中（UIに一時出現）
- AWS Bedrock: モデルID `anthropic.claude-mythos-preview`、エンドポイントは新しい `bedrock-mantle` を使用
- コンテキスト: **1Mトークン**、最大出力: **128Kトークン**
- Reasoning: `thinking.type: "adaptive"` のみサポート
- プロンプトキャッシュ: 最小4,096トークン・最大4チェックポイント
- Project Glasswing: 1,000+のOSSプロジェクトで **23,019件の問題を検出**、6,202件がhigh/critical

---

## Claude Mythos 1とは

### 初期発表（2026年4月7日）

AnthropicはMythos Previewを「**サイバーセキュリティ・自律コーディング・長期エージェントに特化したフロンティアモデル**」として発表しました。コードの推論能力と自律性においてOpus 4.7を大幅に上回るとされ、セキュリティ分野での応用が最優先されています。

当初は約50の厳選パートナー組織のみにアクセスを限定したProject Glasswingという形で展開。これらのパートナーが最初の1か月で10,000件以上のhigh/critical脆弱性を発見したことで、Mythosの実力が広く知られるようになりました。

初期発表の詳細については [Claude Mythos Preview入門 — Project GlasswingとAIゼロデイ発見の全貌](/articles/292-claude-mythos-project-glasswing-security-guide) を参照してください。

### 2026年5月時点の新展開

Anthropicのソースコードに `claude-mythos-1-preview` という新しいモデル文字列が登場し、Claude CodeとClaude Securityへの統合が具体化しつつあります。これはgated previewから **製品組み込み** への移行を示す重要なシグナルです。

Anthropicは「適切なセーフガードが整備されれば一般公開に向けて拡大する」と述べており、Claude Code（開発者ツール）とClaude Security（エンタープライズセキュリティ製品）が最初の公式統合先になるとみられています。

---

## 現在のアクセス方法

![Claude Mythos 1への3つのアクセス経路](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/mythos-1-claude-code-bedrock-api-guide/02-access-methods.png)

2026年5月時点でのアクセス方法は3つあります。

### 1. Claude Security Public Beta（Enterprise顧客向け）

Claude EnterpriseサブスクリプションのTeamおよびMax階層の顧客向けに、Claude SecurityダッシュボードからMythosを利用したコード脆弱性スキャンが公開ベータとして提供されています。

**できること:**
- コードベースのスキャンと脆弱性トリアージ
- 修正案（パッチ）の自動生成
- 脆弱性のPoCエクスプロイトを含むバグレポートの出力

**アクセス方法:** Claude Enterprise契約後、Claude SecurityダッシュボードからRequestを申請。

### 2. AWS Bedrock（gated Standard tier）

AWS Bedrockを通じて `anthropic.claude-mythos-preview` をAPIで呼び出せます。ただし、**bedrock-runtime** ではなく新しい **bedrock-mantle** エンドポイントを使用する点に注意が必要です。

**アクセス条件:**
- AWSアカウントが必要
- Amazon Bedrockコンソールでモデルアクセスを申請（審査あり）
- 現在 us-east-1（バージニア北部）リージョンのみ対応

### 3. Claude Code（準備中）

`claude-mythos-1-preview` のトグルがClaude Code UIに一時的に出現しましたが、その後削除されています。Anthropicは段階的な商業化を進めており、**Enterpriseプロダクトでの提供を先行させてから、安全性評価と保護機能が追いついた段階で段階的に拡大** する方針です。

---

## 技術仕様

AWS Bedrockの公式モデルカードで確認できる仕様は以下の通りです。

| 項目 | 仕様 |
|------|------|
| モデルID（Bedrock） | `anthropic.claude-mythos-preview` |
| モデルID（Claude API） | `claude-mythos-1-preview` |
| コンテキストウィンドウ | 1,048,576トークン（1Mトークン） |
| 最大出力トークン | 131,072トークン（128Kトークン） |
| Reasoning | サポート（`thinking.type: "adaptive"` のみ） |
| 入力モダリティ | テキスト、画像 |
| 出力モダリティ | テキスト |
| Bedrockエンドポイント | `bedrock-mantle`（新エンドポイント） |
| 利用可能リージョン | us-east-1（N. Virginia）のみ |
| プロンプトキャッシュ | 対応（最小4,096トークン、最大4チェックポイント） |
| 知識のカットオフ | 2025年12月 |
| Bedrockサービスティア | Standard（pay-per-token）のみ |
| モデル公開日 | 2026年4月7日 |

**ポイント:**
- **bedrock-mantleエンドポイントのみ** で提供。従来の `bedrock-runtime`（InvokeModel, Converse APIなど）は不使用
- Adaptive Thinkingにより、タスクの複雑さに応じてモデルが推論の深さを自動調整
- 通常のBedrockモデルと異なり、Priority/Flex/Reserved tierは現在非対応

---

## AWS BedrockでのAPIアクセス

### 環境セットアップ

```bash
pip install -U "anthropic[bedrock]"
```

AWSアカウントのBedrockコンソールでモデルアクセスを申請した後、長期APIキーを発行します。

```bash
export AWS_BEARER_TOKEN_BEDROCK="<BedrockのAPIキー>"
```

### 基本的なメッセージ送信

```python
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle(aws_region="us-east-1")

message = client.messages.create(
    model="anthropic.claude-mythos-preview",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "このPythonコードの脆弱性を分析してください。\n\n```python\nimport subprocess\n\ndef run_command(user_input):\n    result = subprocess.run(f'echo {user_input}', shell=True, capture_output=True)\n    return result.stdout.decode()\n```"
        }
    ],
)

print(message.content[0].text)
```

### Adaptive Thinking（推論モード）を有効にする

![Adaptive Thinkingのフロー](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/mythos-1-claude-code-bedrock-api-guide/03-adaptive-thinking.png)

Mythos 1のReasoning機能を使う場合は `thinking.type: "adaptive"` を指定します。`extended` は現在非対応です。

```python
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle(aws_region="us-east-1")

response = client.messages.create(
    model="anthropic.claude-mythos-preview",
    max_tokens=8192,
    thinking={
        "type": "adaptive",
        "budget_tokens": 4096,
    },
    messages=[
        {
            "role": "user",
            "content": """
以下のC言語コードを解析し、セキュリティ脆弱性を特定してください。
脆弱性の種類、影響範囲、再現手順、修正案を含めて報告してください。

```c
void copy_data(char *dst, const char *src) {
    strcpy(dst, src);
}
```
"""
        }
    ],
)

for block in response.content:
    if block.type == "thinking":
        print(f"[推論プロセス]: {block.thinking[:200]}...")
    elif block.type == "text":
        print(f"[回答]: {block.text}")
```

### プロンプトキャッシュの活用

大規模コードベースを繰り返しスキャンする場合、プロンプトキャッシュを活用するとコストを削減できます。

```python
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle(aws_region="us-east-1")

# 大規模コードベースをcache_controlで固定
codebase_content = open("large_codebase.py").read()

response = client.messages.create(
    model="anthropic.claude-mythos-preview",
    max_tokens=4096,
    system=[
        {
            "type": "text",
            "text": "あなたはセキュリティ専門家です。コードの脆弱性を特定し、CVSSスコア、影響範囲、修正案を報告してください。",
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": codebase_content,
                    "cache_control": {"type": "ephemeral"},
                },
                {
                    "type": "text",
                    "text": "このコードに含まれるSQL Injectionの脆弱性をすべて特定してください。",
                },
            ],
        }
    ],
)

print(response.content[0].text)

# キャッシュ使用状況を確認
usage = response.usage
print(f"キャッシュ読み込みトークン: {usage.cache_read_input_tokens}")
print(f"キャッシュ書き込みトークン: {usage.cache_creation_input_tokens}")
```


> プロンプトキャッシュのTTL（Time-to-live）は5分または1時間を選択できます。デフォルトは5分です。1時間TTLはキャッシュ書き込みコストが高くなりますが、長時間の繰り返しスキャンに適しています。
>
> **注意**: AWS公式モデルカードはプロンプトキャッシュを `bedrock-runtime` エンドポイント向けとして記載しています。`bedrock-mantle`（`AnthropicBedrockMantle`）経由でのキャッシュ対応状況については、[公式ドキュメント](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)で最新情報をご確認ください。


---

## Project Glasswingの最新統計（2026-05-22時点）

Anthropicは2026年5月22日時点での脆弱性開示ダッシュボードを更新しました。Mythos Previewの実績は以下の通りです。

### 開示済み脆弱性（coordinated disclosure）

| 指標 | 数値 |
|------|------|
| 開示済み脆弱性数 | 1,596件 |
| 対象OSSプロジェクト数 | 281プロジェクト |
| パッチ適用済み | 97件（約6%） |

### 大規模スキャンの成果

Mythosは1,000+のOSSプロジェクトを対象とした大規模スキャンも実施しました。

| 指標 | 数値 |
|------|------|
| 検出した問題の総数 | 23,019件 |
| うちhigh/criticalレベル | 6,202件 |
| 外部セキュリティ企業による検証数 | 1,752件（6社が評価） |
| 真陽性（true positive）率 | 90.6%以上 |


> 23,000件以上の問題が報告されたにもかかわらず、パッチが当たっているのはまだ97件（約0.4%）のみです。OSSコミュニティのメンテナーへの連絡と修正の対応が課題として指摘されています。


注目の発見例として、OpenBSDで27年間存在し続けた脆弱性がMythosによって発見されています（[参照](https://cryptobriefing.com/anthropic-mythos-open-source-vulnerabilities/)）。

---

## 開発者が今準備できること

Mythos 1がClaude Codeに統合されるまでの間、以下の準備を進めておくことを公式情報に基づいて推奨します。

### 1. Claude Securityの早期アクセスを申請する

Claude EnterpriseのTeam/Max階層のユーザーは、[Claude Security](https://claude.ai/security)からPublic Betaへの参加申請が可能です（2026-05-28時点）。

### 2. AWS Bedrockのモデルアクセスを申請する

AWSアカウントがあれば、Amazon Bedrockコンソールから `anthropic.claude-mythos-preview` へのアクセス申請ができます。審査には数日かかる場合があります。

```bash
# AWS CLIでモデルアクセス状況を確認
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query "modelSummaries[?modelId=='anthropic.claude-mythos-preview']" \
  --output json
```

### 3. bedrock-mantleエンドポイントへの移行準備

従来の `bedrock-runtime` ベースのコードをそのままMythosに適用することはできません。`AnthropicBedrockMantle` クライアントを使用するコードに書き換える必要があります。

```python
# 旧来のBedrockクライアント（Mythos非対応）
# from anthropic import AnthropicBedrock
# client = AnthropicBedrock()

# Mythos対応の新クライアント
from anthropic import AnthropicBedrockMantle
client = AnthropicBedrockMantle(aws_region="us-east-1")
```

### 4. Adaptive Thinkingのパラメータチューニングを理解する

Mythosは `thinking.type: "adaptive"` のみサポートしており、`extended` は使えません。`budget_tokens` でモデルが推論に使えるトークン量を制御できます。コスト管理の観点から、タスクの複雑さに応じて適切な予算を設定することが重要です。

---

## まとめ

| 項目 | 内容 |
|------|------|
| 最新動向 | `claude-mythos-1-preview` がClaude Code UIに一時出現（2026-05-26） |
| 現在のアクセス方法 | Claude Security Beta（Enterprise）、AWS Bedrock（申請制） |
| 近日公開 | Claude CodeとClaude Securityへの正式統合 |
| 技術仕様 | 1Mコンテキスト、128K出力、Adaptive Thinking |
| 成果 | 23,019件の問題を1,000+ OSSプロジェクトで検出 |

Claude Mythos 1は「gated research preview」から「製品組み込み」へと着実に移行しています。特にClaude Codeへの統合は、AIコーディングエージェントとセキュリティスキャンの境界を取り払う可能性があります。

公開情報では「適切なセーフガードが整備されれば段階的に拡大する」とAnthropicは述べており、エンタープライズ製品での実績積み上げ後に一般開発者向けの提供が拡大するとみられます。

---

## 参考リンク

- [Anthropic: Claude Mythos Preview](https://red.anthropic.com/2026/mythos-preview/)
- [Anthropic: Project Glasswing Initial Update](https://www.anthropic.com/research/glasswing-initial-update)
- [AWS Bedrock: Claude Mythos Preview model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-preview.html)
- [Testing Catalog: Anthropic prepares Mythos 1 for Claude Code and Claude Security](https://www.testingcatalog.com/anthropic-prepares-mythos-1-for-claude-code-and-claude-security/)
- [Help Net Security: Anthropic Glasswing Update (2026-05-26)](https://www.helpnetsecurity.com/2026/05/26/anthropic-project-glasswing-update/)
- [CryptoBriefing: Anthropic Mythos 23,000 OSS Vulnerabilities](https://cryptobriefing.com/anthropic-mythos-23000-oss-vulnerabilities/)
