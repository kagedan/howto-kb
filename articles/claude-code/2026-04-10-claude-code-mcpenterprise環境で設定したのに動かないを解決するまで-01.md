---
id: "2026-04-10-claude-code-mcpenterprise環境で設定したのに動かないを解決するまで-01"
title: "Claude Code × MCP、Enterprise環境で設定したのに動かないを解決するまで"
url: "https://qiita.com/namic/items/391a84760012e4112baf"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

## はじめに

Claude CodeのEnterprise/Team環境でMCPサーバーを設定したにもかかわらず、エラーも出ずに無視される現象に遭遇しました。個人アカウントでは同じ設定で動作するため、Enterprise環境固有の制御が原因でした。

本記事では、この現象の原因であるClaude Codeの設定ファイル体系とEnterprise固有の組織制御の仕組みを整理し、Amazon Bedrock経由でClaude Codeを利用することで組織制御の課題を解決した方法を説明します。Enterprise/Team環境でClaude CodeのMCP連携に苦労している方や、組織管理者としてClaude Codeの制御設計を検討している方の参考になれば幸いです。

---

## Enterprise環境でMCP設定が無視される現象

Claude CodeでMCPサーバーを使うには、`.mcp.json`に設定を書くのが基本です。公式ドキュメント通りに記述し、`claude mcp list`で確認、接続テストもOKという状態でした。

しかしEnterprise環境のClaude Codeでは、設定を書いても **MCPサーバーが認識されません**。`/mcp`コマンドで一覧を見てもサーバーが表示されず、エラーメッセージも出ません。設定ファイルの構文エラーでもなく、単に無視されます。

個人プランのアカウントに切り替えると同じ設定ファイルで動作するため、Enterprise環境固有の制御によるものだとわかりました。

原因は設定ファイルの書き方やパスではなく、Claude CodeのEnterprise/Team環境に備わっている組織管理者向けの利用範囲制御の仕組みでした。MCP接続もその制御対象に含まれており、制限に該当した場合はエラーを返さず、 **設定自体がなかったかのように振る舞います**。

Enterprise/Team環境では、`.mcp.json`に正しく設定を書いてもエラーなく無視される場合があります。エラーが出ないため、設定ミスと区別しにくい点に注意してください。

この挙動を理解するには、Claude Codeの設定ファイルの構造と優先順位を把握する必要があります。

---

## 設定ファイルの全体像

Claude Codeの設定ファイルは大きく **3系統** に分かれます。

### 系統1: settings.json系（権限・挙動制御）

Claude Codeの動作権限やツール許可を制御するファイル群です。

| ファイル | スコープ | 配置場所 | Git管理 |
| --- | --- | --- | --- |
| managed-settings.json | Managed | OS固有パス or サーバー配信 | - |
| .claude/settings.local.json | Local | プロジェクト内 | .gitignore |
| .claude/settings.json | Project | プロジェクト内 | 可能 |
| ~/.claude/settings.json | User | ホームディレクトリ | - |

Managed Settingsの配置場所はOSによって異なります。

* **macOS**: `/Library/Application Support/ClaudeCode/managed-settings.json`
* **Linux**: `/etc/claude-code/managed-settings.json`

ここで重要なのが、 **Managed Settingsには2種類ある** という点です。

**Server-managed settings（サーバー配信型）**  
Anthropicのサーバー（api.anthropic.com）から認証時に自動配信される設定。Enterprise/Teamプランの組織管理者がAnthropicの管理コンソールから設定し、ユーザーがClaude Codeを起動・認証するタイミングで適用されます。ローカルにファイルとして存在しないため、ユーザーからは直接見えません。

**Endpoint-managed settings（デバイス配信型）**  
MDMやOS設定管理を通じて、上記のOSパスにファイルとして配置される設定。IT部門がデバイスレベルで管理するもので、ファイルとして実体があるため確認可能です。

この2種類の区別を知らないと、「managed settingsのファイルがローカルにないのに、なぜ制限がかかるのか」が理解できません。Server-managed settingsはファイルではなくAPI経由で配信されるため、ローカルを探しても見つからないのが正常な動作です。

### 系統2: MCP設定系

MCPサーバーの定義と制御に関するファイル群です。

| ファイル | スコープ | 用途 |
| --- | --- | --- |
| managed-mcp.json | Managed | 組織管理者によるMCP排他制御 |
| .mcp.json | Project | プロジェクト単位のMCP定義 |
| ~/.claude.json | User/Local | ユーザー個人のMCP定義 |

`managed-mcp.json`が配置されると、ユーザー側のMCP追加が完全にブロックされます（詳細は後述）。`.mcp.json`はプロジェクトルートに置くもので、チーム共有に適しています。`~/.claude.json`はユーザー個人のグローバルMCP設定です。

### 系統3: CLAUDE.md系（プロンプト指示）

Claude Codeへのカスタム指示を記述するファイル群です。

| ファイル | スコープ | 用途 |
| --- | --- | --- |
| ~/.claude/CLAUDE.md | グローバル | 全プロジェクト共通の指示 |
| CLAUDE.md / .claude/CLAUDE.md | プロジェクト | プロジェクト固有の指示 |
| CLAUDE.local.md | ローカル | 個人用（.gitignore対象） |

CLAUDE.md系はMCP制限とは直接関係しませんが、運用ワークフローの定義に使うため、全体像として把握しておくと便利です。

---

## 設定ファイルの優先順位

複数のスコープに矛盾する設定がある場合の優先順位は以下の通りです。

```
Managed (最優先 - 何によっても上書き不可)
  ↓
CLI引数 (セッション限定)
  ↓
Local (.claude/settings.local.json)
  ↓
Project (.claude/settings.json)
  ↓
User (~/.claude/settings.json)
```

Managedが最優先です。Enterprise環境の制御としては妥当な設計ですが、開発者の設定が反映されない原因にもなります。

パーミッション（ツール実行許可）の評価順序は以下の通りです。

**deny → ask → allow**

どこか1箇所でもdenyが設定されていれば、他のスコープでallowを書いても拒否されます。

配列型の設定（`permissions.allow`や`permissions.deny`など）は、スコープ間で **マージ（結合・重複排除）** されます。上書きではありません。例えば、UserスコープとProjectスコープの両方に`permissions.allow`がある場合、両方のエントリが結合されて適用されます。

MCP制限に関して特に重要なのが以下の2つの設定です。

**allowedMcpServers**  
この設定が存在すると、リストに含まれないMCPサーバーはエラーなくブロックされます。未定義の場合は制限なし。空配列（`[]`）の場合は完全ロックダウン。

**deniedMcpServers**  
明示的にブロックするMCPサーバーのリスト。`allowedMcpServers`より常に優先されます。つまり、allowedに含まれていてもdeniedに含まれていれば拒否。

冒頭で述べた現象の原因は、この`allowedMcpServers`でした。Server-managed settingsに許可リストが設定されていて、リスト外のMCPサーバーがエラーなく無視されていたのです。

---

## 組織管理者によるMCP制御の方法

組織管理者がMCPを制御する方法は大きく2つあります。

### Option 1: managed-mcp.json による排他的制御

managed-mcp.json の詳細

組織管理者がMDM等でデバイスに配置するファイルです。

/Library/Application Support/ClaudeCode/managed-mcp.json

```
{
  "mcpServers": {
    "company-approved": {
      "type": "http",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

このファイルが存在すると、ユーザーが`.mcp.json`や`~/.claude.json`で追加したMCPサーバーは **すべて無視** されます。managed-mcp.jsonに定義されたサーバーのみ利用可能になる、排他的な制御方式です。

組織が承認したMCPサーバーだけを使わせたい場合に有効ですが、開発者の自由度は大幅に制限されます。

### Option 2: allowedMcpServers / deniedMcpServers

allowedMcpServers / deniedMcpServers の詳細

Server-managed settingsまたはEndpoint-managed settingsで設定します。

```
{
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverUrl": "https://*.internal.corp/*" }
  ],
  "deniedMcpServers": [
    { "serverUrl": "https://*.untrusted.com/*" }
  ]
}
```

挙動のまとめ:

| allowedMcpServersの状態 | 結果 |
| --- | --- |
| 未定義 | 制限なし（deniedMcpServers以外はすべて許可） |
| 空配列 `[]` | 完全ロックダウン（すべてのMCP接続を拒否） |
| サーバー指定あり | リスト内のサーバーのみ許可 |

`deniedMcpServers`は常に`allowedMcpServers`より優先されます。両方に含まれるサーバーは拒否されます。

`serverName`はMCP設定で定義した名前、`serverUrl`はURLパターン（ワイルドカード対応）でマッチングします。

Option 1は「組織が指定したサーバーのみ」、Option 2は「許可/拒否リストで柔軟に制御」という違いがあります。実際のEnterprise環境では、これらが組み合わさって適用されていることもあるため、どの制御が効いているのかの切り分けが重要になります。

---

## 実運用で発生した問題と対処

設定ファイルの構造を理解した上でも、実運用ではいくつかの問題がありました。

### VS Code拡張版のMCP連携が不安定だった

Claude CodeにはCLI版とVS Code拡張版がありますが、VS Code拡張版でMCP連携を使ったところ、接続が不安定で頻繁に切断される問題が発生しました。

同じ設定・同じMCPサーバーでも、CLI版に切り替えたら安定して動作しました。環境や設定の組み合わせによる相性の問題と考えられますが、動作しない場合にツール側を変えてみるのも有効な切り分け手段です。

### 許可リストの肥大化

MCPのデバッグ中に、動作確認のために`permissions.allow`にエントリを追加していった結果、100個以上に膨れ上がり、必要なものと不要なものの区別がつかなくなりました。

デバッグ時は`CLAUDE_DEBUG=1`環境変数を設定すると詳細ログが出力されるので、原因特定に有効です。また、MCPサーバーの起動テストには`timeout`（macOSなら`gtimeout`）コマンドが便利です。

```
# MCPサーバーが正常に起動するかテスト（5秒でタイムアウト）
gtimeout 5 npx -y @example/mcp-server
```

対策として、実験的な許可設定は`.claude/settings.local.json`（Localスコープ）に分離するようにしました。このファイルは`.gitignore`対象なので、実験設定がリポジトリに混入するリスクもありません。

### .mcp.jsonの複数プロジェクト間での共有

複数のプロジェクトで同じMCP設定を使いたいケースがありました。シンボリックリンクで共有しようとしましたが、Claude Codeがシンボリックリンクを正しく解決しないケースがあり、実体コピーに切り替えました。

ただし、コピーだと設定変更時に全プロジェクトの更新が必要になります。プロジェクト横断で使うMCPサーバーは`~/.claude.json`のUserスコープに定義し、プロジェクト固有のものだけ`.mcp.json`に書く運用に落ち着きました。

### Claude DesktopとClaude Codeの挙動の違い

`.mcp.json`にMCPサーバーを定義して`disabled: false`も明示的に書いてあるのにブロックされるケースがありました。

原因は、Claude Desktop用のMCP設定としては有効だが、Claude Code側ではServer-managed settingsの`allowedMcpServers`によってブロックされている状態でした。同じマシン上でClaude DesktopとClaude Codeを併用していると、「Desktopでは動くのにCodeでは動かない」という状況が起きます。

これは、Claude DesktopとClaude Codeで **適用されるポリシー体系が異なる** ためです。同じ設定ファイルを参照していても、組織制御のレイヤーが違います。

---

## Desktop委譲ワークフロー

Bedrock移行を検討する前に、まず既存環境内での対処法として以下のワークフローを運用しました。

Managed Settingsによる制約は、組織のセキュリティポリシーとして正当なものです。制約の中で適切なワークフローを組むのが現実的なアプローチです。

Claude Desktopには **Server-managed settingsが適用されません**。Server-managed settingsはClaude Code固有の仕組みで、api.anthropic.comへの認証時に配信されるものです。Claude Desktopは別の認証経路を使うため、この制御の対象外です。

そこで、以下のワークフローを運用しています。

1. **基本はCLI版（Claude Code）で作業**
2. **MCPが必要な場面で、Code側で使えるか確認**
3. **使えない場合、Claude Desktopに委譲**
4. **Desktop側の出力をCLI側の作業に取り込む**

判断フローはCLAUDE.mdに明文化しています。

```
1. 直接利用を試みる → Code側で使えるならそのまま実行
2. Desktop委譲 → MCPでなければ品質が大きく落ちる場合のみ
3. WebSearch/WebFetchで代替 → Desktop委譲するほどでもない場合
```

Desktop依頼時は、以下のようなフォーマットでプロンプトをまとめると効率的です。

```
【Desktop依頼】
以下を Claude Desktop で実行し、出力をこのチャットに貼り付けてください。

■ MCPツール: （利用するMCPサーバー名）
■ 目的: （何のために必要か）
■ プロンプト:
（Desktop に入力するプロンプト本文）

■ 期待する出力: （ファイル / テキスト / JSON 等）
```

ただし、Desktop委譲はツール間でコンテキストを手動で受け渡しする手間がかかり、Desktop側にはCodeほどのファイル操作能力がないという制約があります。

---

## Amazon Bedrock経由でClaude Codeを使う

Desktop委譲ワークフローの制約を解消する方法として、Claude Codeの公式ドキュメントに以下の記載があります。

> Server-managed settings require a direct connection to api.anthropic.com and are not available when using third-party model providers: Amazon Bedrock, Google Vertex AI, Microsoft Foundry...

### Bedrock経由でServer-managed settingsが適用されない理由

Claude CodeはAPIプロバイダーとしてAmazon Bedrockを選択できます。Bedrock経由で利用する場合、Claude Codeはapi.anthropic.comに接続しません。Server-managed settingsはAnthropicサーバーへの認証時に配信される仕組みなので、 **接続先がBedrockであれば配信経路自体が存在しません**。

これはAnthropic公式ドキュメントに明記された仕様です。

### セットアップ方法

Bedrock経由でClaude Codeを使うための設定は、環境変数を数個セットするだけです。

```
# Bedrock利用を有効化
export CLAUDE_CODE_USE_BEDROCK=1

# リージョン指定
export AWS_REGION=us-east-1

# モデルバージョンのピン留め（推奨）
# ※ 利用可能なモデルIDは aws bedrock list-foundation-models で確認してください
export ANTHROPIC_DEFAULT_SONNET_MODEL='us.anthropic.claude-sonnet-4-6'
```

認証はAWS SSO（IAM Identity Center）の利用を推奨します。長期間有効なアクセスキーよりもセキュリティ面で優れています。

```
# SSO認証
aws sso login --profile=my-bedrock-profile
export AWS_PROFILE=my-bedrock-profile
```

Claude Codeの`settings.json`に認証リフレッシュの設定を書いておくと、セッション切れ時に自動で再認証してくれます。

~/.claude/settings.json

```
{
  "awsAuthRefresh": "aws sso login --profile myprofile",
  "env": {
    "AWS_PROFILE": "myprofile"
  }
}
```

### 制限の回避ではなく管理体系の移行

Bedrock経由にすることで変わるのは、管理の主体です。

* **Anthropic側の組織管理（Server-managed settings）** → 適用されなくなる
* **AWS側の管理（IAM, CloudTrail, Guardrails, VPC制御）** → 新たに適用される
* **デバイス側の管理（Endpoint-managed settings / MDM）** → 引き続き有効

管理が「なくなる」のではなく、管理の主体がAnthropicのSaaSレイヤーからAWSインフラレイヤーに移行します。

### Anthropic直接利用とBedrock経由の比較

| 項目 | Anthropic直接 | Amazon Bedrock |
| --- | --- | --- |
| 認証 | Anthropic API Key / OAuth | AWS IAM / SSO |
| Server-managed settings | 適用される | **適用されない** |
| Endpoint-managed settings | 適用される | 適用される |
| MCP機能 | 制限なし | 制限なし |
| VPC内完結 | 不可 | 可能 |
| 監査ログ | Anthropic側 | CloudTrail |
| コスト管理 | Anthropicダッシュボード | AWS Budgets / CloudWatch |
| モデル可用性 | 最新モデルが最速 | 数日〜数週間遅れの場合あり |
| 料金 | トークン単価ベース | 同等（データ転送料は別途） |

Bedrock経由の場合、Anthropicの最新モデルリリースから数日〜数週間の遅れが発生する場合があります。また、トークン単価自体はほぼ同等ですが、VPC EndpointやData Transfer等のAWSインフラコストが別途かかる点は考慮が必要です。

Endpoint-managed settings（MDMやOSレベルで配置されるmanaged-settings.json）は、Bedrock経由でも引き続き適用されます。Server-managed settingsのみが対象外になる点に注意してください。

---

## Bedrockをセキュアに使う構成

Bedrock経由にした場合、Server-managed settingsが外れる代わりに、AWSのセキュリティ機能で同等以上の制御が可能です。

### 全体アーキテクチャ

```
[開発者PC: Claude Code CLI]
   |
   | aws sso login (OIDC/SAML)
   v
[IAM Identity Center] ← [IdP: Entra ID / Okta]
   |
   | 一時認証情報
   v
[VPC Endpoint: bedrock-runtime] ← Private DNS有効
   |
   | AWSバックボーン
   v
[Amazon Bedrock]
   ├── Guardrails (コンテンツフィルタ)
   ├── CloudTrail (API監査)
   └── CloudWatch (利用量監視)
```

開発者のPCからAmazon Bedrockまで、各レイヤーで制御・監査を入れる構成です。

### 1. VPC Endpoint（PrivateLink）

Bedrockへのトラフィックをインターネットに出さず、AWSバックボーン内に閉じることができます。

* `bedrock-runtime`のVPC Endpointを作成
* Private DNSを有効化することで、クライアント側のコード変更は不要
* エンドポイントポリシーで`InvokeModel`系のアクションのみ許可

VPNやDirect Connect経由で開発者PCからVPCに接続している環境であれば、Bedrockへの通信が完全にプライベートネットワーク内で完結します。

### 2. IAM最小権限ポリシー

Claude Codeの公式ドキュメントで推奨されている最小権限のIAMポリシーです。

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*:*:foundation-model/*"
      ]
    }
  ]
}
```

必要なのは推論実行とプロファイル一覧取得のみ。モデルの管理操作やGuardrailの変更権限は不要です。Resourceの範囲は、実際に利用するモデルとリージョンに絞ることでさらに制限できます。

### 3. Guardrails強制適用

Amazon Bedrock Guardrailsを使うと、推論リクエストに対してコンテンツフィルタリングを適用できます。ここで重要なのは、 **IAMポリシーのConditionキーでGuardrailの使用を必須化できる** 点です。

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*:*:foundation-model/*",
      "Condition": {
        "StringEquals": {
          "bedrock:GuardrailIdentifier": "arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123:1"
        }
      }
    }
  ]
}
```

このConditionを設定すると、指定されたGuardrailを付与せずに推論リクエストを送った場合、IAMレベルで拒否されます。ユーザーがGuardrailを迂回する方法はありません。Anthropic側のServer-managed settingsで行っていたコンテンツ制御を、AWS IAMの仕組みで実現できます。

### 4. SCP（Organization制御）

AWS Organizations配下であれば、SCP（Service Control Policy）でさらに上位の制御が可能です。

例えば、Bedrockの利用を特定リージョンに限定する場合:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "bedrock:*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["us-east-1", "us-west-2"]
        }
      }
    }
  ]
}
```

SCPはOrganization内の全アカウントに強制適用されるため、個別アカウントのIAMポリシーで上書きすることはできません。Server-managed settingsのManagedスコープと同等の強制力をAWS側で実現できます。

### 5. 監査・可視化

Bedrock経由の利用は、AWSの標準的な監査機能で記録・可視化できます。

**CloudTrail**  
BedrockのAPIコールを記録します。データイベント（InvokeModel等）の記録にはAdvanced Event Selectorsの設定が必要です。誰が、いつ、どのモデルに、どのようなリクエストを送ったかを追跡可能です。

**Model Invocation Logging**  
Bedrockの機能で、推論リクエストとレスポンスの完全な内容をS3やCloudWatch Logsに記録できます。コンプライアンス要件がある場合に有効です。

**CloudWatch Metrics**  
`InputTokens`、`OutputTokens`、`InvocationCount`などのメトリクスでリアルタイム監視が可能です。異常な利用パターンの検知やコスト管理に使えます。

### セキュリティと開発者体験の両立

| セキュリティ要件 | 実装方法 | 開発者体験への配慮 |
| --- | --- | --- |
| 通信の閉域化 | VPC Endpoint | Private DNSでコード変更不要 |
| 認証の強化 | SSO必須 | awsAuthRefreshで自動更新 |
| コンテンツ制御 | Guardrail強制 | IAM Conditionで透過的に適用 |
| 監査ログ | CloudTrail + Invocation Logging | バックグラウンドで自動収集 |

セキュリティを強化しても、開発者のワークフローはほぼ変わりません。VPC EndpointのPrivate DNS、SSOの自動リフレッシュ、IAMによるGuardrail強制適用は、いずれも開発者から見て透過的に動作します。

---

## 組織管理者向け：設計のポイント

ここまでの内容を踏まえて、組織管理者として設計する際のポイントをまとめます。

**Anthropic管理とAWS管理の使い分け**

Anthropic直接利用（Server-managed settings）は、設定の手軽さが利点です。Anthropicの管理コンソールから設定するだけで、デバイス側の作業は不要です。一方、AWS管理（Bedrock経由）は、既存のAWSセキュリティ基盤に統合できる点が強みです。VPC制御、IAM、CloudTrailなど、すでに組織で運用している仕組みをそのまま活用できます。

**最小権限の原則で始める**

最初から全機能を開放するのではなく、必要最小限の権限で始めて段階的に拡大するアプローチが安全です。Bedrock利用の場合、IAMの最小権限ポリシーから始めて、チームの要望に応じてモデルやリージョンを追加していく形が実用的です。

**小さいチームで検証してから展開する**

全社展開の前に、小さいチームで検証期間を設けることを推奨します。設定ファイルの優先順位やMCP制限の挙動は、ドキュメントだけでは把握しきれない部分があります。

**ユーザー向けの確認手順を整備する**

Claude Codeには`/status`コマンド（接続状態の確認）や`/permissions`コマンド（現在の権限設定の確認）があります。これらの使い方を社内ドキュメントに整備しておくと、問い合わせ対応の負荷が下がります。一次切り分けをユーザー自身でできるようにしておくことが重要です。

**Bedrock移行時のMCP制御の再構築**

Bedrock経由に移行するとServer-managed settingsのMCP制御が外れるため、必要に応じて **Endpoint-managed settings** （ファイルベース）やAWS IAMでMCP制御を再構築してください。Endpoint-managed settingsのmanaged-settings.jsonにallowedMcpServersを設定するか、managed-mcp.jsonで排他制御する方法が使えます。

---

## まとめ

本記事の要点は3つです。

1. **Claude Codeの設定ファイルは3系統**。中でもManaged Settingsには **Server-managed（サーバー配信）** と **Endpoint-managed（デバイス配信）** の2種類があり、この区別が重要
2. **Server-managed settingsはBedrock経由では適用されない**。これはAnthropic公式ドキュメントに明記された仕様で、API接続先がapi.anthropic.comでないため設定配信経路が存在しないことが理由
3. **Bedrock移行は管理体系の移行**。VPC Endpoint、IAM最小権限、Guardrails強制適用、CloudTrailなど、AWSのセキュリティ機能で同等以上の制御が可能

Enterprise環境でのAIツール運用は、ツールの機能だけでなく、組織制御の仕組みを理解することが必要です。設定ファイルの優先順位、Managed Settingsの2種類の違い、APIプロバイダーによる制御適用範囲の差異といった知識が、実運用で重要になります。
