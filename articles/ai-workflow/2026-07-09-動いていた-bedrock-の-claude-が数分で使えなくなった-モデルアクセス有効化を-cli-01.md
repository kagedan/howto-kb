---
id: "2026-07-09-動いていた-bedrock-の-claude-が数分で使えなくなった-モデルアクセス有効化を-cli-01"
title: "動いていた Bedrock の Claude が数分で使えなくなった — モデルアクセス有効化を CLI で完結する手順とハマりどころ"
url: "https://qiita.com/kazu_techlog/items/0a6a3f730c159007ccbc"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-07-09"
date_collected: "2026-07-10"
summary_by: "auto-rss"
query: ""
---

## TL;DR

この記事で扱うエラー:

```text
ResourceNotFoundException: Model use case details have not been submitted for this account.
```

- Amazon Bedrock の Anthropic モデルは、利用開始前に「**use case フォーム提出**」と「**モデル提供契約（アグリーメント）締結**」が必要。どちらも**コンソール不要、CLI で完結できます**。
- ワナが 2 つ。フォームの `intendedUsers` は説明文ではなく**数値文字列**（間違えると `Invalid form data`）。そして**手続き未完了でも直後の数回は呼び出しが通ってしまう**ことがあり、「動いた」と思ったら数分後に使えなくなります。
- JP cross-region inference profile（`jp.anthropic.*`）を使うと、**データを日本国内（東京⇔大阪）に閉じたまま**新しめの Claude（Sonnet 4.6 等）を使えます。
- 検証環境一式（Terraform + boto3 CLI）は GitHub で公開しています: [bedrock-lab (phase1 タグ)](https://github.com/SantaSan-1224/bedrock-lab/tree/phase1)

## 何を作ったか

個人学習用に、Bedrock を AWS のガバナンス（IAM・監査・コスト管理）に組み込んだミニマム環境を Terraform で構築しました。

![figure1_bedrock_jp_profile.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/478546/eba53870-0387-412a-8cce-7dd996f3328f.png)
*図1: 全体構成（JP inference profile 経由で東京/大阪にルーティング、invocation logging で監査）*

| 項目 | 内容 |
|---|---|
| リージョン | ap-northeast-1（東京）※ルーティング先に ap-northeast-3（大阪） |
| モデル | Claude Sonnet 4.6 / Sonnet 4.5 / Haiku 4.5（JP inference profile 経由） |
| IaC | Terraform（IAM 最小権限・invocation logging・Budgets） |
| クライアント | boto3 の Converse API（薄い CLI ラッパー） |
| 時期 | 2026年7月 |

## 前提: JP cross-region inference profile とは

Bedrock のモデル呼び出しには「モデル ID 直指定」と「inference profile 指定」の 2 方式があります。inference profile は複数リージョンへの自動振り分け（cross-region inference）の呼び出し口で、プレフィックスで振り分け先の範囲が固定されています。

| 呼び出し方式 | 振り分け先 | データの国内所在 | 新しめのモデル |
|---|---|---|---|
| モデル ID 直指定 | 東京のみ | ✅ | ❌ Sonnet 4.5 以降はほぼ非対応 |
| `apac.` プロファイル | 東京・大阪・シンガポール・シドニー等 | ❌ | ✅ |
| `global.` プロファイル | 全世界の商用リージョン | ❌ | ✅ |
| **`jp.` プロファイル** | **東京・大阪のみ** | ✅ | ✅ |

ポイントは 2 つです。

1. **新しめの Claude は東京単体のオンデマンド呼び出しに対応していない**ものが多く、inference profile 経由が実質必須です。
2. `jp.` プロファイルなら振り分け先が東京・大阪に限定され、リージョン間通信も AWS のバックボーン網内で完結します。「データを日本から出さない」要件と新しいモデルを両立できます。

利用可能な JP プロファイルは CLI で確認できます。

```bash
aws bedrock list-inference-profiles --region ap-northeast-1 \
  --query "inferenceProfileSummaries[?starts_with(inferenceProfileId, 'jp.')].inferenceProfileId"
# jp.anthropic.claude-sonnet-4-6
# jp.anthropic.claude-sonnet-4-5-20250929-v1:0
# jp.anthropic.claude-haiku-4-5-20251001-v1:0
# jp.anthropic.claude-opus-4-7 / jp.anthropic.claude-opus-4-8 (後述の注意あり)
```

なお IAM ポリシーは、プロファイル ARN だけでなく**振り分け先リージョン（東京・大阪）それぞれの foundation-model ARN も許可が必要**です（ここも地味にハマりどころ）。ポリシー例は[公開リポジトリの iam.tf](https://github.com/SantaSan-1224/bedrock-lab/blob/phase1/terraform/iam.tf) を参照してください（ワイルドカードの簡略例です。実運用では `bedrock:InferenceProfileArn` 条件キーによる絞り込みも検討を）。

ちなみに `bedrock:Converse` という IAM アクションは**存在しません**。Converse / ConverseStream API の権限は `bedrock:InvokeModel` / `bedrock:InvokeModelWithResponseStream` でカバーされます。

## 事件: 動いていた Claude が数分後に使えなくなった

環境構築後、動作確認は成功しました。Sonnet 4.6 も Haiku 4.5 も普通に応答が返ってきます。ところが**約 10 分後、同じコードが突然エラーになりました**。

```text
ResourceNotFoundException: Model use case details have not been submitted
for this account. Fill out the Anthropic use case details form before
using the model. If you have already filled out the form, try again in 15 minutes.
```

「use case フォームが未提出」と言われています。状態を確認してみると、確かに未提出でした。

```bash
aws bedrock get-use-case-for-model-access --region ap-northeast-1
# ResourceNotFoundException: You have not filled out the request form.
```

つまりこのアカウントは **Anthropic モデルの利用開始手続きが未完了のまま、数回呼び出せてしまっていた**わけです。実はこれ、[公式ドキュメント](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)に説明のある挙動でした。初回呼び出し時にサブスクリプション処理がバックグラウンドで走り、**セットアップ期間（最大15分）の間は API 呼び出しが一時的に成功することがあり**、前提条件（Anthropic の場合は use case フォーム）が欠けていると失敗に転じます。

> During this setup period (up to 15 minutes), your API calls may succeed temporarily while the subscription is being finalized.

> **教訓**: 「一度呼び出しが通った」ことは手続き完了の証明になりません。動作確認の前に、後述の `get-foundation-model-availability` で状態を確認しておくべきでした。

## 解決: モデルアクセス有効化を CLI で完結する

背景として、2025年10月のアップデートで Bedrock のモデルアクセス管理は簡素化され、多くのモデルは**デフォルトで有効・初回呼び出し時に自動サブスクライブ**されるようになりました。ただし **Anthropic モデルは初回に use case フォーム（First Time Use form）の提出が必要**です。この経緯とコンソールでの提出手順は [@minorun365 さんの記事](https://qiita.com/minorun365/items/7070a0206547cc6dc650)や [@hayao_k さんの記事](https://qiita.com/hayao_k/items/aaaf92e15a60bebd137a)に詳しいので、本記事は **CLI で完結する手順と、その過程で実際に踏んだワナ**に絞ります。

コンソールで行う手続きと同じことが、CLI の 3 ステップでできます。

### Step 1: use case フォームの提出

```bash
cat > usecase_form.json <<'EOF'
{
  "companyName": "Personal (individual)",
  "companyWebsite": "https://github.com/your-account",
  "intendedUsers": "1",
  "industryOption": "Technology",
  "otherIndustryOption": "",
  "useCases": "Personal home lab for learning AWS Bedrock governance. Low volume, non-production."
}
EOF

aws bedrock put-use-case-for-model-access --region ap-northeast-1 \
  --form-data "$(base64 -i usecase_form.json)"
```

最大のワナは **`intendedUsers` が数値文字列**であることです。最初、コンソールのフォームを想像して `"Internal employees"` のような説明文を入れたところ、`ValidationException: Invalid form data` で弾かれました。正しくは利用者区分の数値文字列で、[公式ドキュメント](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html#model-access-modify)に **`0: Internal / 1: External / 2: Internal_and_External`** と定義されています（各フィールドの文字数上限も同ページに記載）。

なお `companyWebsite` は、個人開発者なら **GitHub プロフィールやポートフォリオの URL でよい**と公式に明記されています。

なお `Invalid form data` は他のフィールドでも起きます。[AWS re:Post の報告](https://repost.aws/questions/QUTYk-tNQ0RMqoSS2TrsBWEQ/bedrock-model-access-invalid-form-data)では `companyWebsite` の URL 形式（`www.` プレフィックス）で弾かれた例もあり、**バリデーション仕様が画面にもドキュメントにも出てこない**のがこのフォームの厄介なところです。

### Step 2: モデルごとにアグリーメント締結

```bash
m=anthropic.claude-sonnet-4-6
token=$(aws bedrock list-foundation-model-agreement-offers --model-id "$m" \
  --region ap-northeast-1 --query 'offers[0].offerToken' --output text)
aws bedrock create-foundation-model-agreement --model-id "$m" \
  --offer-token "$token" --region ap-northeast-1
```

使うモデルの数だけ繰り返します（Sonnet 4.6 / Sonnet 4.5 / Haiku 4.5 など）。

### Step 3: 状態確認 → 15 分待つ

```bash
aws bedrock get-foundation-model-availability \
  --model-id anthropic.claude-sonnet-4-6 --region ap-northeast-1
```

```json
{
  "modelId": "anthropic.claude-sonnet-4-6",
  "agreementAvailability": { "status": "AVAILABLE" },
  "authorizationStatus": "AUTHORIZED",
  "entitlementAvailability": "AVAILABLE",
  "regionAvailability": "AVAILABLE"
}
```

`agreementAvailability` が `AVAILABLE` になれば締結完了です。ただし**実際に呼び出せるようになるまで 15 分程度の伝播ラグ**がありました（エラーメッセージの「try again in 15 minutes」は本当だった）。

補足として、フォームとアグリーメントは**アカウント単位**です。JP プロファイルの振り分け先である大阪について個別の手続きは不要でした（大阪側で `get-use-case-for-model-access` を実行すると、東京で出したフォームがそのまま見えます）。

## その他のハマりどころ

### IAM の description に日本語が使えない

Terraform で IAM ロールの `description` に日本語を書いたら apply が失敗しました。

```text
ValidationError: Value at 'description' failed to satisfy constraint:
Member must satisfy regular expression pattern: [\u0009\u000A\u000D\u0020-\u007E\u00A1-\u00FF]*
```

パターンの中身は、タブ・改行（`\u0009` `\u000A` `\u000D`）+ ASCII 印字可能文字（`\u0020-\u007E`）+ Latin-1 補助（`\u00A1-\u00FF`）。つまり**日本語はまるごと範囲外**です。地味ですが日本語話者には典型的な罠です。

### Opus 系は手続きを完了しても呼び出せない

Opus 4.8 は JP プロファイルが存在し、アグリーメントも普通に締結でき、`get-foundation-model-availability` は**全項目 AVAILABLE** になります。それでも invoke だけが拒否されます。

```text
AccessDeniedException: anthropic.claude-opus-4-8 is not available for this
account. ... For additional access options, contact AWS Sales
```

つまり最上位モデル群には、ステータス API に現れない追加のアクセス制御がもう一段あり、**AWS Sales への問い合わせが必要な扱いに見えます**（[AWS re:Post にも同事象の報告](https://repost.aws/questions/QUV81Zo9tgTsmfx2ZCPUR0vA/claude-opus-4-7-4-8-on-amazon-bedrock-returns-accessdeniedexception-despite-full-entitlement-and-valid-agreement)があります）。個人アカウントでは上位モデル枠を Sonnet 4.6 で運用する、と割り切りました。

## まとめ

| 学び | 内容 |
|---|---|
| 国内所在×新モデル | `jp.anthropic.*` プロファイルで両立できる（東京⇔大阪のみ） |
| モデルアクセス有効化 | CLI 3 ステップで完結（フォーム提出→締結→確認）。`intendedUsers` は区分の数値文字列（0/1/2） |
| 非同期チェックのラグ | 初回は最大15分のセットアップ中、手続き未完了でも一時的に呼び出しが通る（公式記載の挙動）。「動いた」を信用せず状態 API で確認 |
| IAM | `bedrock:Converse` は存在しない / 振り分け先リージョンの foundation-model ARN も必要 / description は日本語不可 |
| Opus 系 | 全ステータス AVAILABLE でも invoke 不可（AWS Sales への問い合わせが必要な扱い）のことがある |

Terraform 一式・boto3 チャット CLI・README は GitHub で公開しています。

https://github.com/SantaSan-1224/bedrock-lab/tree/phase1

## 参考

**AWS 公式**

- [Request access to models - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) — use case フォームと PutUseCaseForModelAccess の公式ドキュメント
- [Supported Regions and models for inference profiles - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) — cross-region inference profile の仕様
- [Introducing Amazon Bedrock cross-Region inference for Claude Sonnet 4.5 and Haiku 4.5 in Japan and Australia (AWS Blog)](https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-cross-region-inference-for-claude-sonnet-4-5-and-haiku-4-5-in-japan-and-australia/) — JP プロファイルの一次情報（東京/大阪ルーティング、AWS 網内完結）

**先行記事（use case フォームの背景・コンソール手順はこちらが詳しいです）**

- [Bedrockのモデルアクセス有効化が不要に！ でもClaudeは初回のみ別操作が必要😣 (@minorun365)](https://qiita.com/minorun365/items/7070a0206547cc6dc650)
- [Amazon Bedrock のモデルアクセス廃止に関しておさえておくとよいこと (@hayao_k)](https://qiita.com/hayao_k/items/aaaf92e15a60bebd137a)

**同事象の報告（AWS re:Post）**

- [Bedrock Model Access "Invalid Form Data"](https://repost.aws/questions/QUTYk-tNQ0RMqoSS2TrsBWEQ/bedrock-model-access-invalid-form-data)
- [Claude Opus 4.7 / 4.8 on Amazon Bedrock returns AccessDeniedException despite full entitlement and valid agreement](https://repost.aws/questions/QUV81Zo9tgTsmfx2ZCPUR0vA/claude-opus-4-7-4-8-on-amazon-bedrock-returns-accessdeniedexception-despite-full-entitlement-and-valid-agreement)
