---
id: "2026-05-26-claude-公式-e-learning-2本を受講してわかったbedrock-で-claude-を-01"
title: "Claude 公式 e-learning 2本を受講してわかった「Bedrock で Claude を使う」ための5つの勘所"
url: "https://qiita.com/yuta_satake/items/8939f42f4585374a8543"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-05-26"
date_collected: "2026-05-27"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

AWS パートナー企業に勤め、AWS 認定資格を全冠（2023-2025 Japan All AWS Certifications Engineers）取得している筆者が、**Claude on AWS Champion Program** への参加を目指して Anthropic 公式 e-learning を 2 本受講しました。

- [Claude with Amazon Bedrock](https://anthropic.skilljar.com/claude-in-amazon-bedrock)
- [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action)

「AWS は知っているが Claude は初心者」という立場から、**AWS エンジニアが引っかかりやすいポイント**に絞ってまとめます。

## 2. そもそも Claude を Bedrock 経由で使う利点とは？

Bedrock を使わず Anthropic API を直接使えば良くね？と思う方もいるかも知れません。私も e-learning 学習前はそう思っていました。AWS パートナーとして顧客に提案する立場から整理すると、**Bedrock 経由を選ぶ理由は主に 4 つ**です。

**① AWS のセキュリティ・ガバナンス基盤がそのまま使える**
IAM によるアクセス制御、CloudTrail による API ログ、VPC エンドポイントによるプライベート通信など、企業が既に整備しているセキュリティ統制を Claude にも適用できます。

**② 入出力データが AWS 環境の外に出ない**
Bedrock 経由の推論では、プロンプトや応答は Anthropic のトレーニングに使用されません。機密情報を扱うエンタープライズ用途で重要な要件となるはずです。

**③ 既存の AWS インフラとシームレスに統合できる**
Lambda・ECS・S3・CloudWatch など、使い慣れたサービスとそのまま組み合わせられます。新しいアカウントや契約を増やさず、既存の AWS 環境に Claude を追加できます。

**④ Bedrock ネイティブのマネージドサービスが使える**
Knowledge Bases (RAG), Agents, Guardrails（コンテンツフィルタ）など、本来自前で実装が必要な機能がマネージドサービスとして提供されています。

これらの理由から、**エンタープライズ用途では Bedrock 経由が事実上の標準選択肢**と言えます。
以下では、実際に使う際の勘所をまとめます。

---

## 3. Bedrock で Calude を使うための 5 つの勘所
### 3.1. Bedrock API と Anthropic API は「別物」と心得る

まず最初にして最重要の気づきがこれです。

Claude モデルは AWS Bedrock と Anthropic API の両方で利用できますが、**SDK・ドキュメント・エンドポイントがまったく異なります。**

```python
# AWS Bedrock の場合は boto3 を使う
import boto3

client = boto3.client("bedrock-runtime", region_name="us-west-2")
response = client.converse(
    modelId="us.anthropic.claude-sonnet-4-6-20250514-v1:0",
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)
text = response["output"]["message"]["content"][0]["text"]
```

Anthropic 公式 SDK（`anthropic` パッケージ）のドキュメントを見ながら Bedrock で実装しようとすると確実にハマります。**Bedrock 専用のドキュメントを最初から参照する**ことが時間節約の近道です。

---

### 3.2. モデル ID は Inference Profile を使う

Bedrock でモデルを呼び出す際、モデルカタログに表示されている ID をそのまま使うと**リージョンによっては謎のエラーが出ることがあります。** 理由は、すべてのモデルがすべてのリージョンでホストされているわけではないためです。

```python
# ❌ 直接モデル ID（リージョンによっては失敗）
modelId = "anthropic.claude-sonnet-4-6"

# ✅ Inference Profile ID（クロスリージョンで確実にルーティング）
modelId = "global.anthropic.claude-sonnet-4-6"
```

Inference Profile ID は AWS コンソールの **「モデルカタログ」ではなく「推論プロファイル」** のメニューにあります（2026 年 5 月時点の UI）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3333253/26eea8db-65d9-42b4-aacf-62755cc84292.png)

---

### 3.3. Prompt Caching でコストを削る

同じシステムプロンプトやツールスキーマを繰り返し送るユースケースでは **Prompt Caching** が効果的です。

```python
system = [
    {
        "text": "あなたは AWS Well-Architected Framework の専門家です。"
                "ユーザーのシステム構成を 6 本柱でレビューしてください。..."
    },
    {"cachePoint": {"type": "default"}}  # ここまでをキャッシュ（5分間）
]
```

初回リクエストでキャッシュが作成（`cache_write`）され、以降は再利用（`cache_read`）されます。レスポンスの高速化とコスト削減が同時に得られます。

ElastiCache でクエリ結果をキャッシュするのと発想は同じです。AWS エンジニアには直感的に理解しやすい概念だと思います。

---

### 3.4. Hooks が便利

『Claude Code in Action』で最も印象的だったのが **Hooks** の仕組みです。

Claude がファイルを読み書きするたびにカスタムスクリプトを自動実行でき、結果を Claude 自身にフィードバックできます。

**実用例①：TypeScript 型チェック Hook**

```json
// .claude/settings.local.json
{
  "hooks": {
    "postToolUse": [{
      "matcher": "edit",
      "command": "tsc --no-emit"
    }]
  }
}
```

ファイル編集のたびに型チェックが走り、エラーがあれば Claude に自動フィードバックします。関数シグネチャ変更時の呼び出し元修正漏れが自動解消されます。
ここでは `postToolUse` を使用していますが、ツール実行前に動く `PreToolUse` もあります。

**実用例②：重複コード防止 Hook**

別の Claude インスタンスを起動して新しく書かれたコードの重複を自動チェックする Hook も実装可能です。AI が AI を監視するアーキテクチャです。

AWS CodeBuild のポストビルドアクションに近い概念ですが、**AI のワークフローにリアルタイムで介入できる**点が異なります。

---

### 3.5. CLAUDE.md でコンテキストを設計する

Claude Code の効果は **CLAUDE.md** の整備度合いに直結します。

```
$ claude
> /init   ← コードベースを自動解析して CLAUDE.md を生成
```

プロジェクトのアーキテクチャ・コーディング規約・重要ファイルへの参照が記述され、すべてのリクエストに自動でコンテキストとして含まれます。

| ファイル | スコープ | 説明 |
|---|---|---|
| `CLAUDE.md` | チーム共有（Git 管理） | initで生成され、ソース管理にコミットされ、他のエンジニアと共有される |
| `CLAUDE.local.md` | 個人用（Git 管理外） | 他のエンジニアとは共有されず、Claude の個人的な指示とカスタマイズが含まれている |
| `~/.claude/CLAUDE.md` | 全プロジェクト共通 | マシン上のすべてのプロジェクトで使用され、Claude がすべてのプロジェクトで従うべき手順が含まれている |

コンテキストが多すぎても精度が落ちるため、**「必要十分な情報を設計する」** 意識が重要です。

---

## 4. 所感

受講前後でのギャップをまとめると：

| 領域 | AWS 知識の転用 | 追加で学んだこと |
|---|---|---|
| インフラ・IAM・セキュリティ | ✅ そのまま使える | なし |
| Bedrock API | △ | Inference Profile, converse API |
| コスト最適化 | ✅ 考え方は同じ | Prompt Caching の実装 |
| RAG | △ | Knowledge Bases、Hybrid Search |
| Claude Code | ❌ 新概念 | CLAUDE.md, Hooks, MCP 連携 |

AWS の知識があれば **インフラ周りのキャッチアップは不要**で、Claude 固有の概念と Bedrock 固有の API に集中できます。

---

## 5. おわりに

次のステップとして以下に取り組みます。

1. **AWS Certified Generative AI Developer - Professional (AIP-C01) 受験**（落ちたらセルフノミネーション不可になります、、）
2. **Claude on Bedrock を使った PoC 実装**（Well-Architected Review アシスタント）

学んだ内容を実装に落とし込んだ記事も公開予定です。

---

## 参考リンク

- [Claude with Amazon Bedrock（Anthropic 公式 e-learning）](https://anthropic.skilljar.com/claude-in-amazon-bedrock)
- [Claude Code in Action（Anthropic 公式 e-learning）](https://anthropic.skilljar.com/claude-code-in-action)
- [Amazon Bedrock ドキュメント](https://docs.aws.amazon.com/bedrock/)
