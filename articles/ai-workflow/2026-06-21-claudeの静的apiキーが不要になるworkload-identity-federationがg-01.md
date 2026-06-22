---
id: "2026-06-21-claudeの静的apiキーが不要になるworkload-identity-federationがg-01"
title: "Claudeの静的APIキーが不要になる、Workload Identity FederationがGA"
url: "https://zenn.dev/okssusucha/articles/20260621-anthropic-claude-workload-identity-federa"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

`sk-ant-...` で始まる長い文字列を、CIのシークレットや`.env`に置いたまま運用しているチームは多い。あれは一度作ると基本的に失効しない。リポジトリにうっかりコミットされても、漏れたことに誰も気づかないまま何ヶ月も有効なまま残る。LLMアプリの事故報告でいちばんよく見る原因が、この静的なAPIキーの流出だ。

その前提を崩す仕組みが、6月17日にClaude Platformで正式提供(GA)になった。Anthropicが [Workload Identity Federation(WIF)](https://claude.com/blog/workload-identity-federation) と呼ぶもので、ひとことで言えば「ワークロードがClaude APIを呼ぶときに、保管しておいた秘密鍵を使わない」やり方だ。

<https://claude.com/blog/workload-identity-federation>

## キーを保管するのをやめて、その都度発行する

WIFの発想自体は新しくない。AWSのIAMロールや、クラウド各社のWorkload Identity Federationと同じ考え方を、Claude APIの認証に持ち込んだものだ。すでにあなたのワークロードは、動いている環境から身元を証明する手段を持っている。GitHub Actionsのランナーには発行されるOIDCトークンがあり、KubernetesのPodには投影されたサービスアカウントトークンがあり、AWS・GCP・Azureの実行環境にはそれぞれメタデータ経由で取れる署名済みの身元情報がある。

WIFはこの「すでに持っている身元」を使う。ワークロードがIdP(身元プロバイダ)の署名したJWTをAnthropicに提示すると、Anthropicが事前に設定した信頼ルールと照合し、合致すれば短命のアクセストークン(`sk-ant-oat01-...`)を返す。このトークンで`/v1/messages`を呼ぶ。鍵を作って、CIに置いて、回して、漏らす、というサイクルそのものが消える。公式ドキュメントの表現を借りるとこうだ。

> There are no static secrets to mint, store in CI, rotate, or leak.

従来のAPIキーとの違いを並べるとはっきりする。

|  | 静的APIキー (`sk-ant-...`) | WIFのトークン (`sk-ant-oat01-...`) |
| --- | --- | --- |
| 有効期限 | 実質なし(手で失効させるまで) | 既定1時間、最短60秒(設定で60〜86400秒) |
| 保管場所 | CIシークレット・環境変数・`.env` | どこにも保管しない。実行時に発行 |
| ローテーション | 手作業 | SDKが期限前に自動で再取得 |
| 身元の粒度 | 鍵を共有=誰が使ったか不明 | サービスアカウント単位でID・監査ログ |

最後の行が地味だが効く。APIキーは「それ自体が資格情報」だが、サービスアカウントは「資格情報を都度発行してもらう主体」だ。どのワークロードがどのサービスアカウントとして動いたかが監査ログに残る。

## 設定の正体は3つのリソース

コンソールで設定するのは3種類のオブジェクトで、これを理解すると全体像が掴める。3つあわせて「発行者Xが署名し、クレームがYに見えるトークンは、サービスアカウントZとして振る舞ってよい」という宣言になる。

* **サービスアカウント** (`svac_...`): メールもパスワードもコンソールログインも持たない、人間ではないID。トークンが「誰として」振る舞うかの実体。
* **フェデレーション発行者** (`fdis_...`): 信頼するOIDCプロバイダの登録。JWTの`iss`クレーム(例:`https://token.actions.githubusercontent.com`)と、署名検証用の公開鍵(JWKS)の取得方法を持つ。
* **フェデレーションルール** (`fdrl_...`): 両者をつなぐ橋。「発行者XのJWTがこういうクレーム条件を満たしたら、サービスアカウントZのトークンを発行する」という対応づけと、付与するスコープ・トークン寿命を定義する。

マッチ条件は`subject_prefix`(`system:serviceaccount:prod:worker`のような前置一致)、`audience`の完全一致、クレーム値のマップ、複雑な論理を書く [CEL](https://cel.dev/) 式などを組み合わせられる。本番EKSクラスタ、ステージング、GitHub Actionsはそれぞれ別の発行者として登録するのが標準的な使い方で、チームや名前空間ごとにルールを分けて権限を絞れる。

## 実際の交換はこう動く

トークンの取得はRFC 7523の`jwt-bearer`グラントで、`POST /v1/oauth/token`に投げる。中身を見るとやっていることは単純だ。

```
# 1. IdPが発行したJWTを取得(取り方は環境ごとに異なる)
JWT=$(cat /var/run/secrets/anthropic.com/token)

# 2. JWTを短命のAnthropicアクセストークンに交換
RESPONSE=$(curl -sS https://api.anthropic.com/v1/oauth/token \
  -H "content-type: application/json" \
  --data @- <<JSON
{
  "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
  "assertion": "$JWT",
  "federation_rule_id": "fdrl_...",
  "organization_id": "00000000-0000-0000-0000-000000000000",
  "service_account_id": "svac_...",
  "workspace_id": "wrkspc_..."
}
JSON
)
ACCESS_TOKEN=$(jq -r .access_token <<<"$RESPONSE")
```

実務ではこれを手書きせず、SDKに任せる。クライアントには`api_key`を渡さず、フェデレーションの資格情報を渡すだけだ。SDKが交換と再取得のループを面倒見る。

```
from anthropic import Anthropic, WorkloadIdentityCredentials, IdentityTokenFile

client = Anthropic(
    credentials=WorkloadIdentityCredentials(
        identity_token_provider=IdentityTokenFile(
            "/var/run/secrets/anthropic.com/token"
        ),
        federation_rule_id="fdrl_...",
        organization_id="00000000-0000-0000-0000-000000000000",
        service_account_id="svac_...",
        workspace_id="wrkspc_...",
    ),
)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
```

引数なしでクライアントを作り、`ANTHROPIC_FEDERATION_RULE_ID`などの環境変数を環境ごとに注入する形が、本番向けの推奨パターンとされている。同じコンテナイメージをどこでも動かせるからだ。再取得は期限の120秒前に先行リフレッシュ、30秒前に必須リフレッシュという二段構えで、`botocore`に倣った設計になっている。発行されるトークンの寿命はルールの`token_lifetime_seconds`と「元のJWTの残り寿命の2倍」の小さいほう(下限60秒)で、Anthropic側のトークンが上流の身元より長生きしないようになっている。

私がいちばん使いどころが明確だと感じるのはGitHub Actionsだ。リポジトリのシークレットに`ANTHROPIC_API_KEY`を置く運用を、OIDCトークンの交換に置き換えれば、CIから長命の鍵が一掃される。

## 移行時の落とし穴は精度の罠

移行で一番引っかかるのは、SDKの資格情報の優先順位だ。`ANTHROPIC_API_KEY`はフェデレーションよりも優先される。つまり古い鍵が環境変数に残っていると、WIFを設定したつもりでも黙ってAPIキーのほうが使われ続ける。「移行できた気になる」事故が起きる位置がここだとドキュメントが明記しているのは良心的で、`ant auth status`でどの資格情報が選ばれているか確認できる。手順としては、フェデレーションを並行で設定→`ANTHROPIC_API_KEY`をあらゆる場所(コンテナ環境、CIシークレット、シェルのプロファイル)から外す→選ばれている資格情報が切り替わったのを確認→最後に鍵を失効、という順になる。

## これで全部解決、ではない

冷静に効果を見積もるなら、WIFが守るのはClaude APIへの認証だけだ。独立した検証として、認証基盤ベンダーのAembitが [WIFの限界を整理した記事](https://aembit.io/blog/anthropic-workload-identity-federation-what-it-gets-right-and-what-it-still-doesnt-solve/) を出している。指摘は妥当で、現実のワークロードはClaudeだけでなくデータベースや社内サービス、他社のAI APIにもアクセスする。それぞれに別の資格情報管理が必要なままで、その作業はアプリ開発者側に分散しがちだ。さらに、フェデレーションの強度は署名するIdPの強度を超えない。KubernetesのサービスアカウントやGitHub ActionsのOIDC設定を間違えれば、間違ったワークロードにも有効なトークンが出てしまう。Anthropic自身もドキュメントで「これ単体で完結するセキュリティの物語ではない(not a complete security story on its own)」と書いており、上流IdP側の条件付きアクセスや監査ログと組み合わせて多層防御にすべき、というのが両者で一致した見方だ。

それでも、LLM基盤の認証がようやくクラウドIAMの常識に追いついた、という意味でこれは歓迎すべき変化だと思う。新規にClaude APIで本番ワークロードを組むなら、最初から静的キーを発行しない設計にできる。既存システムでも、まずはCIの`ANTHROPIC_API_KEY`を消すところから始める価値は十分にある。漏れて困る秘密は、そもそも保管しないのがいちばん強い。
