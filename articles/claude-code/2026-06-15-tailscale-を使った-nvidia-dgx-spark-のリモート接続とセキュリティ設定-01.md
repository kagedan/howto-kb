---
id: "2026-06-15-tailscale-を使った-nvidia-dgx-spark-のリモート接続とセキュリティ設定-01"
title: "Tailscale を使った NVIDIA DGX Spark のリモート接続とセキュリティ設定"
url: "https://zenn.dev/foxgem/articles/a9109490613b33"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

NVIDIA DGX Spark をリモートから使うには、接続方法と基本的なセキュリティ設定を整える必要があります。この記事では、その主な手順を説明します。初回起動の手順はマニュアルにあるため、ここでは扱いません。

重要な注意点として、DGX Spark は Ubuntu の ***ARM64*** システムです。ソフトウェアをインストールするときは、正しいアーキテクチャ (`aarch64` または `arm64`) を選んでください。

## リモート接続を有効にする

DGX Spark には SSH でリモート接続します。まず `ssh` サービスがインストールされ、起動しているか確認します。

`Active: active (running)` と表示されていれば、SSH は利用できます。以降のリモート接続は、このサービスに依存します。

## クライアントからリモート接続する

SSH が有効であれば、手元のマシンの `ssh` クライアントから直接接続できます。NVIDIA は、便利な GUI ツール `nvidia-sync` も提供しています。  
<https://build.nvidia.com/spark/connect-to-your-spark/sync>

`nvidia-sync` では、DGX Spark への接続と管理、SSH ターミナル、VS Code や Cursor でのリモート開発をまとめて扱えます。利用をおすすめします。

Windows、Linux、macOS 版が提供されています。

`nvidia-sync` で初めてデバイスを追加するときは、ユーザー名とパスワードを使います。その後、専用の SSH 鍵ペアを作り、公開鍵を DGX Spark の `~/.ssh/authorized_keys` に追加します。次回以降は、この SSH 鍵で接続します。

ユーザー名とパスワードが必要なのは、デバイスを追加するときだけです。また、`nvidia-sync` はデバイスを追加するたびに、新しいランダムな鍵を作ります。デバイスを削除してから再追加する場合は、パスワードログインが必要です。そのため、`nvidia-sync` を使うなら SSH パスワード認証は無効にしないでください。

### LAN 内で接続する

LAN 内では、`nvidia-sync` の `Devices` ページから DGX Spark を自動検出できます。IP アドレスを手入力する必要はありません。デバイスをクリックし、ユーザー名とパスワードを入力すれば接続できます。

### 別ネットワークから接続する

別のネットワークから接続する場合は、`tailscale` を有効にします: <https://tailscale.com/>

まず IPv6 には注意が必要です。家庭内ネットワークの IPv4 デバイスは、通常ルーターの NAT 配下にあります。そのため、外部から直接接続するのは簡単ではありません。しかし DGX Spark がグローバル IPv6 アドレスを持つ場合、インターネットから直接到達できる可能性があります。ルーターやホストのファイアウォールが IPv6 の受信を許可していると、SSH ポートが IPv6 インターネット全体に公開されます。

パブリック IPv6 で直接接続することは可能です。ただし、その場合はファイアウォール、動的 IPv6 アドレスや DNS、接続元制限、SSH の安全対策を自分で管理する必要があります。より安全なのは、パブリックな受信接続を止めて、Tailscale を使う方法です。Tailscale は、許可されたユーザーとデバイスだけが使える暗号化 overlay ネットワークを作ります。パブリック IPv4、ポートフォワーディング、固定 IPv6 アドレスは不要です。DGX Spark の SSH を公開インターネットに出さずに済みます。

Tailscale は WireGuard ベースの mesh VPN サービスです。デバイス検出、ID 認証、NAT 越え、エンドツーエンド暗号化を担います。重要なのは、**NVIDIA Sync の別ネットワークからの接続が、内蔵 Tailscale 統合で動いている**ことです。LAN 内では直接接続し、LAN の外では自動的に Tailscale に切り替わります。手動で接続方式を選ぶ必要はありません。

**サーバー側設定**

DGX Spark に SSH 接続し、Tailscale が入っているかを確認します。

コマンドが存在しない場合は、公式ドキュメント <https://build.nvidia.com/spark/tailscale/instructions> を参考にインストールします。

```
# 必要なツールをインストール
sudo apt install -y curl gnupg

# Tailscale の署名鍵を追加
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg | \
  sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg > /dev/null

# Tailscale のリポジトリを追加
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list | \
  sudo tee /etc/apt/sources.list.d/tailscale.list

# Tailscale をインストール
sudo apt update && sudo apt install -y tailscale
```

インストール後、Tailscale を起動してログインします。

ターミナルの案内に従ってブラウザを開き、Tailscale アカウントにログインします。管理コンソールで DGX Spark がオンラインになっていれば、サーバー側の設定は完了です。

**クライアント側設定**

`nvidia-sync` には Tailscale クライアント機能があります。NVIDIA Sync だけを使う場合は、`tailscale` コマンドを別途インストールする必要はありません。**Settings** ページで **Tailscale** を見つけ、**Enable Tailscale** をクリックします。ブラウザで Tailscale にログインすると、管理コンソールで `nvidia-sync` の接続状態を確認できます。

有効化すると、クライアントと DGX Spark が同じ LAN にない場合、`nvidia-sync` は Tailscale トンネル経由で接続します。手動切り替えは不要です。

注意点があります。`nvidia-sync` 内蔵の Tailscale 機能は、`nvidia-sync` アプリ内でだけ有効です。システム全体の DNS は設定されません。ターミナルや VS Code などから Tailscale ドメイン (`*.ts.net`) で接続したい場合は、クライアント側に**別途 Tailscale クライアントをインストール**してください: [https://tailscale.com/download。](https://tailscale.com/download%E3%80%82)

**Tailscale アドレスで接続する**

Tailscale 管理コンソールの **Machines** ページでは、**ADDRESSES** に表示される任意のアドレスを使えます。`100.x.x.x` のプライベート IPv4、`fd7a:115c:` で始まる IPv6、または `x.x.ts.net` ドメインです。ドメイン (`*.ts.net`) を使う場合は、Tailscale クライアントが動いている必要があります。停止していると名前解決できません。

接続中は Tailscale クライアントを動かしたままにしてください。`nvidia-sync` を開いたままにし、`tailscale` を停止しないでください。切断されると、リモート接続も切れます。

**リモート共同作業**

Tailscale は共同作業にも使えます。DGX Spark を他のユーザーに共有すれば、そのユーザーも Tailscale 経由で接続できます。

Tailscale 管理コンソールの **Machines** ページで DGX Spark を選び、**Share** をクリックします。相手は自分の管理コンソールで共有された DGX Spark を見られます。その後、上記の **クライアント側設定** と同じ手順で接続できます。

## Tailscale をもう少し深く理解する

Tailscale は単なる「設定不要の WireGuard クライアント」ではありません。WireGuard は軽量なエンドツーエンド暗号化トンネルを作ります。しかし WireGuard だけでは、ユーザー認証、デバイス検出、鍵配布、NAT 越え、アクセス制御までは扱いません。Tailscale は、これらの作業を自動化します。公式の **How Tailscale works** (<https://tailscale.com/blog/how-tailscale-works>) には、全体の仕組みが説明されています。

### Tailscale の仕組み

Tailscale には、コントロールプレーンとデータプレーンがあります。

* **コントロールプレーン**は Tailscale の Coordination Server が担当します。ユーザーとデバイスを認証し、公開鍵と接続情報を交換し、アクセス制御ポリシーを配布します。接続を調整するだけで、実際のアプリケーション通信は運びません。
* **データプレーン**は、デバイス間の WireGuard トンネルです。各デバイスはローカルで秘密鍵を作ります。秘密鍵はデバイス外へ出ません。通信はエンドツーエンドで暗号化されるため、Tailscale は内容を読めません。

流れは TCP の 3 ウェイハンドシェイクに少し似ています。Coordination Server がまず双方の ID と接続情報を確認します。その後、クライアントと DGX Spark が独立したデータチャネルを作ります。ただし、これは TCP ハンドシェイクそのものではありません。Coordination Server は、その後のアプリケーション通信の経路には入りません。

2 台のデバイスが通信を始めるときは、Tailscale の協調サービスと DERP リレーサーバーで互いを見つけます。その後、NAT 越えで直接 UDP 接続を試します。多くの場合、接続後の通信はクライアントと DGX Spark の間を直接流れます。中央 VPN ゲートウェイは経由しません。

ネットワークが UDP を禁止している場合や、NAT 越えに失敗した場合、Tailscale は同じ tailnet 内の Peer Relay を試します。それも失敗すると、世界各地の DERP サーバーで中継します。この場合でも Coordination Server はアプリケーション通信を運びません。直接接続、Peer Relay、DERP のどれでも、データは WireGuard で暗号化されています。リレーサーバーは復号できません。**接続方式** (<https://tailscale.com/docs/reference/connection-types>) の主な違いは、暗号強度ではなくレイテンシとスループットです。

実際の接続経路は、次のコマンドで確認できます。

```
tailscale ping <デバイス名または Tailscale IP>
tailscale status
tailscale netcheck
```

出力の `direct` はピアツーピア直接接続、`relay` は DERP リレー、`peer-relay` は自前の Peer Relay を意味します。リモート開発が遅い場合は、まず接続が `relay` のままになっていないか確認してください。

Tailscale と従来型 VPN の主な違いは次のとおりです。

| 比較項目 | 従来型 VPN | Tailscale |
| --- | --- | --- |
| ネットワーク構成 | 通常は中央 VPN ゲートウェイでトラフィックを転送 | デバイス間のピアツーピア mesh 接続を優先 |
| ID と設定 | アカウント、パスワード、証明書、手動ネットワーク設定に依存しがち | ID プロバイダーと統合し、デバイス公開鍵とポリシーを自動配布 |
| NAT 越えと公開ポート | 公開入口、ポートフォワーディング、固定ゲートウェイが必要になりがち | NAT 越えを自動実行し、失敗時は暗号化リレーを使用 |
| アクセス制御 | サブネットや IP アドレス単位で許可しがち | ユーザー、グループ、デバイスタグ、ポート、デバイス状態で許可可能 |
| トラフィック出口 | クライアントのインターネット通信も VPN ゲートウェイ経由になりがち | デフォルトでは tailnet 内部通信だけを扱い、必要時に Exit Node を別途設定 |

つまり Tailscale は、公開 IP を隠すための従来型「プロキシ型 VPN」ではありません。ID ベースの暗号化 overlay ネットワークと考えるほうが正確です。

### NVIDIA Sync が Tailscale を使う理由

DGX Spark は通常、家庭やオフィスのネットワークに置かれます。固定パブリック IP がないことも多く、多段 NAT や通信事業者の CGNAT 配下にある場合もあります。SSH ポートをインターネットに公開するのは面倒で、ログイン入口を常に公開することにもなります。Tailscale を使えば、DGX Spark にパブリック受信ポートを開けずに、デバイス検出、動的アドレス、NAT 越え、暗号化接続を利用できます。

**NVIDIA Sync 公式ドキュメント** (<https://docs.nvidia.com/sync/latest/tailscale.html>) では、NVIDIA Sync 自体が tailnet のノードとして参加すると説明されています。そのため NVIDIA Sync だけを使う場合、クライアント側にシステムレベルの Tailscale クライアントは不要です。NVIDIA Sync は接続方式も自動で選びます。同じ LAN なら直接接続し、LAN の外では Tailscale に切り替わります。NVIDIA Sync が管理するトンネルや SSH alias を使う VS Code、Cursor の接続も一緒に切り替わります。

クライアント上での NVIDIA Sync の動きは、おおまかに次のようになります。

```
  VS Code / Cursor / NVIDIA Sync ターミナル
                  |
                  | NVIDIA Sync が管理する SSH alias / トンネルを使用
                  v
        +------------------------------------------+
        | NVIDIA Sync                              |
        |                                          |
        | デバイス検出 + SSH 鍵管理                |
        | 接続状態の確認                           |
        | 内蔵 Tailscale ノード                    |
        +------------------------------------------+
                  |
          DGX Spark に到達可能か判定
                  |
          +-------+-------+
          |               |
          v               v
   同じ LAN で到達可能    別ネットワークまたは LAN で到達不可
          |               |
          v               v
      LAN 直接接続       Tailscale 暗号化接続
          |               |
          +-------+-------+
                  |
                  v
             DGX Spark SSH

  システムレベルの Tailscale を別途インストールすると、
  他のターミナルやアプリからも 100.x.x.x アドレスや
  *.ts.net ドメインを直接使えるようになり、NVIDIA Sync に限定されません。
```

つまり NVIDIA Sync は、単に「VPN を統合した」わけではありません。Tailscale により、移動するクライアントから固定ワークステーションへ接続しやすくなります。NVIDIA が自前でアカウント認証、NAT 越え、グローバルリレー基盤を作る必要もありません。

### Tailscale がエンタープライズ級セキュリティを実現する仕組み

Tailscale のセキュリティモデルは、「VPN に入ったら全員を信頼する」というものではありません。ID、デバイス状態、最小権限ルールを組み合わせます。

```
  ユーザー ID                    デバイス ID と状態
  SSO / MFA                     デバイス承認 / タグ / Posture
      |                              |
      +--------------+---------------+
                     |
                     v
          +------------------------------------------------+
          | Tailscale コントロールプレーン                 |
          | Grants / ACL ポリシーを解釈                    |
          +------------------------------------------------+
                     |
                     | 許可された相手、公開鍵、パケットフィルターを配布
                     v
          +------------------------------------------------+
          | DGX Spark ローカルでポリシーを実行             |
          | tailscaled 受信パケットフィルター              |
          +------------------------------------------------+
                     |
             user -> tcp:22 を許可
             その他の未認可接続を拒否
                     |
                     v
               OpenSSH サービス

  Tailscale のネットワークポリシーは、通信がサービスへ到達できるかだけを決めます。
  SSH 鍵、Ubuntu 権限、UFW、システム更新は別個のセキュリティ層です。
```

1. **エンドツーエンド暗号化**: データプレーンは WireGuard を使います。秘密鍵はデバイス上に残ります。DERP リレーを経由しても、DERP は暗号文を転送するだけです。
2. **ID 認証**: ユーザーは Google、Microsoft、GitHub、Okta などでログインできます。企業は既存の SSO、MFA、アカウント停止フローを使えます。
3. **デバイス承認**: 管理者は **Device Approval** (<https://tailscale.com/docs/features/access-control/device-management/device-approval>) を有効にできます。新しいデバイスは承認されるまで tailnet を使えません。
4. **最小権限ポリシー**: Tailscale は **Grants** (<https://tailscale.com/docs/features/access-control/grants>) を推奨しています。Grants では、誰がどのデバイスのどのポートへアクセスできるかを定義します。ポリシーはコントロールプレーンから配布されますが、実行は各デバイス上で行われます。
5. **デバイス ID と状態**: タグで DGX Spark、サーバー、一般ユーザーデバイスを分けられます。Device Posture により、OS バージョン、Tailscale バージョン、MDM、EDR、XDR の状態でアクセスを制限できます。
6. **監査とログ**: すべてのプランに設定監査ログと Webhook があります。Premium と Enterprise では、ネットワークフローログとログストリーミングも利用できます。
7. **コントロールプレーンへの信頼を減らす**: 高セキュリティ環境では **Tailnet Lock** (<https://tailscale.com/docs/features/tailnet-lock>) を使えます。新しいノード鍵には、信頼済みノードの署名が必要です。Tailscale のコントロールプレーンが侵害されても、攻撃者は通信可能なノードを勝手に追加できません。Tailnet Lock は現在 Personal と Enterprise プランのみです。Device Approval とは同時に使えないため、脅威モデルに合わせて選びます。

見落としやすい点があります。ACL と Grants は「デフォルト拒否」ですが、**新規 tailnet の初期ポリシーは、すべてのデバイスが互いにアクセスできる設定**です。本当にゼロトラストと最小権限にするには、初期の allow-all ルールを削除し、明示的な許可ルールを追加します。

たとえば DGX Spark に `tag:dgx-spark` を付けたあと、特定ユーザーだけが SSH にアクセスできるようにできます。

```
{
  "tagOwners": {
    "tag:dgx-spark": ["autogroup:admin"]
  },
  "grants": [
    {
      "src": ["your-account@example.com"],
      "dst": ["tag:dgx-spark"],
      "ip": ["tcp:22"]
    }
  ]
}
```

NVIDIA Sync の **Add a Device** で auth key を使う場合は、有効期限の短い使い捨て key を使ってください。サーバー側ではタグでデバイス ID を固定するのも有効です。再利用可能な auth key をスクリプト、チャット、リポジトリに貼らないでください。その鍵を持つ人は、tailnet に新しいデバイスを追加できてしまいます。

外部協力者を tailnet 全体に招待するより、**Share** で DGX Spark を共有するほうが安全です。**デバイス共有** (<https://tailscale.com/docs/features/sharing>) は現在も beta です。相手には共有されたマシンだけが見えます。共有マシンはデフォルトで隔離され、相手の tailnet 内の他のマシンへは接続できません。共有リンクはパスワードのように扱い、単回リンクを優先してください。さらに Grants で、協力者を DGX Spark の SSH ポートだけに制限できます。

Tailscale が保護するのは、overlay ネットワークを通る通信だけです。DGX Spark 上の弱いパスワード、脆弱性、誤った権限は直してくれません。SSH が LAN やパブリックインターフェースでも待ち受けているなら、ホストファイアウォール、システム更新、SSH の堅牢化は必要です。

### Aperture で DGX Spark 上の AI 利用を保護する

Tailscale のトップページにある **Securing AI** は、beta 段階の **Aperture by Tailscale** (<https://tailscale.com/use-cases/securing-ai>) を指します。Aperture は、Claude Code、Codex、Gemini CLI などのツールとモデルサービスの間に入る AI ゲートウェイです。役割としては **OpenRouter** に近いものです。

Aperture は、モデル API Key を 1 か所で管理します。Aperture がない場合、API Key は開発者 PC、DGX Spark、CI/CD、Agent に分散しがちです。ユーザーが Aperture にアクセスするとき、上流モデルの API Key は不要です。ゲートウェイは Tailscale ID でユーザーまたはデバイスを識別し、権限を確認してから、正しいモデルプロバイダーの認証情報を付与します。

```
  開発者 / Agent
  Claude Code / Codex / Gemini CLI / カスタムアプリ
                |
                | Tailscale ネットワーク ID
                | 上流モデル API Key は持たない
                v
       +--------------------------------------------------+
       | Aperture AI Gateway                              |
       |                                                  |
       | 認証とモデル認可                                 |
       | Provider API Key を集中保存                      |
       | モデルルーティング / クォータ / ログ             |
       | Guardrails / MCP Gateway                         |
       +--------------------------------------------------+
          |          |           |
          |          |           |
          v          v           v
       OpenAI    Anthropic   DGX Spark 上の
       Gemini    Bedrock     vLLM / Ollama /
                            llama.cpp などのモデル

  クライアントは 1 つの Aperture アドレスにだけ接続します。
  ゲートウェイはリクエスト中のモデル名に基づき、
  外部プロバイダーまたは DGX Spark のプライベートモデルへ転送します。
```

ここでいう「一つの認証」は、正確には **Tailscale ネットワーク ID と Aperture の認可ポリシー**の組み合わせです。

* ユーザーは Tailscale にログインするだけです。Claude Code、Codex、Gemini CLI などは Aperture 経由でモデルにアクセスします。OpenAI、Anthropic、Google などの API Key を個別に保存する必要はありません。
* 管理者は各プロバイダーの API Key を Aperture に保存します。Tailscale のユーザー、グループ、デバイスタグで、誰がどのモデルを使えるかを制御します。
* Aperture はデフォルトでモデルアクセスを拒否します。ゲートウェイに接続できても、対応する Grant がなければモデルは使えません。
* ユーザー削除、デバイス失効、ポリシー変更後、アクセス権はすぐに反映されます。各デバイス上のモデル API Key をローテーションしたり削除したりする必要はありません。

ただし、Claude Max、ChatGPT Plus、Gemini Advanced などのサブスクリプションをまとめて使えるわけではありません。Aperture には、モデルプロバイダーの開発者プラットフォームが発行する API Key が必要です。個人向けやチーム向けサブスクリプションのログイン権限は利用できません。

#### Aperture が AI 利用をどう保護するか

Aperture は AI リクエストの入口として、次のようなセキュリティと管理機能を提供します。

1. **API Key の拡散を減らす**: 上流キーは Aperture だけに保存します。開発者 PC、DGX Spark 上の Agent 設定、スクリプト、リポジトリに置く必要はありません。
2. **ID 付き監査**: 各リクエストは Tailscale ユーザーまたはデバイス ID と紐づきます。モデル、プロバイダー、時刻、Token 数、費用を記録できます。Claude Code や Codex の複数リクエストを 1 つのセッションとしてまとめることもできます。
3. **モデルアクセス制御**: ユーザーやチームを、特定モデルだけに制限できます。ユーザー、Agent、モデル、チーム単位でリクエスト数や予算も制限できます。
4. **リクエスト Guardrails**: リクエストが外へ出る前に、pre-request hook で検査、変更、拒否できます。たとえば PII の削除、危険なツール宣言の削除、ポリシー違反 Prompt のブロックができます。
5. **MCP 入口の集約**: Aperture は複数のリモート MCP Server を 1 つの `/v1/mcp` アドレスにまとめられます。Tailscale ID に基づき、ユーザーが見つけられる MCP ツールやリソースを制御できます。
6. **プライベートモデルを公開しない**: DGX Spark 上の vLLM、Ollama、llama.cpp などの OpenAI-compatible サービスは tailnet にだけ公開すれば十分です。Aperture はそれらを self-hosted provider としてチームに提供できます。

現行バージョンの注意点です。

* Aperture は監査のため、完全なリクエストとレスポンスを保存します。ソースコードや機密情報が含まれる可能性があります。必要に応じて保持期間を設定してください。必要であれば完全キャプチャの保持期間をゼロにし、必要なログを S3 や SIEM に出力します。
* Guardrails は現在、リクエストがモデルへ送信される前にだけ実行されます。モデルの返答を後からフィルタリングする機能はありません。
* Aperture の MCP Server Proxy はまだ alpha です。現在の Grants は、ユーザーが発見できるツールを制限します。ただし公式ドキュメントでは、ツール呼び出し時にツール単位の認可チェックは再実行されないと説明されています。
* ローカルツールは、最終的に Coding Agent が動くマシン上で実行されます。Aperture はツール利用を観測し、モデルに送るツール宣言を制限できます。ただし、Claude Code や Codex のサンドボックス、承認フロー、ファイルシステム権限を置き換えるものではありません。

#### DGX Spark と組み合わせる推奨構成

DGX Spark は、リモート開発マシンとしても、プライベートモデルサーバーとしても使えます。

```
  開発者 PC
  Claude Code / Codex / Gemini CLI
          |
          | Aperture に統一接続
          v
  +------------------------------+
  | Aperture                     |
  | ID / ポリシー / ログ         |
  +------------------------------+
       |           |
       |           +=========> 外部ホストモデル
       |                       OpenAI / Anthropic / Gemini
       |
       +== Tailscale プライベートネットワーク ==> DGX Spark
                              |
                              +-- OpenAI-compatible モデルサービス
                              |   vLLM / Ollama / llama.cpp
                              |
                              +-- プライベート MCP Server
                              +-- SSH リモート開発環境

  DGX Spark のモデルサービスと MCP サービスに
  パブリックポートを開ける必要はありません。
  管理者はユーザーごとに見えるモデルやツールを変えられます。
```

DGX Spark 上のプライベートモデルサービスは、OpenAI-compatible Chat Completions API を提供する必要があります。また、Aperture から tailnet アドレスで到達できる必要があります。たとえば Aperture の provider 設定で DGX Spark を指定できます。

```
{
  "providers": {
    "dgx-spark": {
      "baseurl": "http://dgx-spark.example.ts.net:8000",
      "models": ["private-coding-model"]
    }
  }
}
```

Claude Code、Codex、Gemini CLI など、カスタム Base URL を使えるクライアントでは、API アドレスを Aperture に向けるだけです。

```
Claude Code: ANTHROPIC_BASE_URL=http://<aperture-hostname>
Codex:       base_url = "http://<aperture-hostname>/v1"
Gemini CLI:  API Base URL = http://<aperture-hostname>/v1
```

クライアントから Aperture への接続が `http://` でも、実際の通信は WireGuard で暗号化されています。クライアントに本物のモデル API Key は不要です。ツールが API Key の入力を求める場合は、プレースホルダーで構いません。Aperture はそれを無視し、管理済みの上流認証情報を付与します。

もう一つ注意点があります。Aperture は、**ネットワークリクエストを送った Tailscale ノード**で ID を判断します。開発者が自分の PC で Coding Agent を動かす場合、Aperture はそのユーザーを記録できます。しかし複数人が同じ DGX Spark に SSH し、Spark 上で Agent を動かすと、リクエストは通常 DGX Spark のデバイス所有者またはタグ ID として記録されます。個々の SSH ユーザーとしては記録されません。

そのため、ユーザー単位の監査が必要なら、各開発者のローカルマシンで Coding Agent を動かし、NVIDIA Sync/SSH で DGX Spark を操作する構成がおすすめです。別の方法として、ユーザー、CI Runner、Agent コンテナごとに独立した Tailscale または `ts-unplug` ID を割り当てます。すべての自動化に、区別できない 1 つの DGX Spark ノード ID を共有させないでください。

現時点で Aperture は beta です。beta 中は、どの Tailscale アカウントでも無料で使えます。Personal プランでは最大 6 ユーザーまで利用できます。大きなチーム向けの正式価格はまだ公開されていません。**Aperture 公式ドキュメント** (<https://tailscale.com/docs/aperture>) と今後の価格発表を確認してください。

### Tailscale の料金

以下の価格は **Tailscale 公式料金ページ** (<https://tailscale.com/pricing>) に基づきます。Tailscale は 2026 年 4 月に新しい席位制課金を導入しており、今後も価格やプラン制限が変更される可能性があります。

| プラン | 現在の価格 | 主な用途と違い |
| --- | --- | --- |
| Personal | 無料 | 非商用の個人利用のみ。最大 6 ユーザー、ユーザーデバイス無制限、50 tagged resources、3 ACL groups、ほとんどの基本機能を含む |
| Standard | 1 席あたり月 8 米ドル | チーム向け。ユーザー数無制限に加え、SCIM、より多くのロール、MDM 設定、サードパーティ製デバイス状態統合などを追加 |
| Premium | 1 席あたり月 18 米ドル | ネットワークフローログ、ログストリーミング、ジャストインタイムアクセス、高度な Tailscale SSH、リージョナルルーティング、優先サポートを追加 |
| Enterprise | 個別見積もり | カスタム容量、契約と SLA、プロフェッショナルサービス、専用サポート、請求書払いなどを追加 |

ここでいう「席位」は tailnet に参加するユーザーを指し、デバイス単位ではありません。すべてのプランで通常のユーザーデバイスは無制限です。サーバーや Exit Node などは通常 tagged resource として扱います。Personal プランには 50 個含まれ、超過分の現在価格は 1 個あたり月 1 米ドルです。短命な CI/CD Runner や Kubernetes Pod は、ephemeral resource の分プールで計算されます。

個人が自宅で DGX Spark を使う場合、通常は無料の Personal tailnet で十分です。NVIDIA Sync、ノート PC、DGX Spark がデバイス数によって個別課金されることはありません。課金が関係するのは主に、商用利用、6 ユーザー超過、大量の tagged/ephemeral resources、または SCIM、デバイス状態統合、ネットワークフローログ、ログ出力、SLA などの企業管理・コンプライアンス機能が必要な場合です。

## ネットワークセキュリティ

DGX Spark は Ubuntu マシンなので、Ubuntu の一般的なセキュリティ対策がそのまま使えます。ここでは代表的なものをいくつか挙げます。

Tailscale はリモートアクセス用の暗号化された境界を作ります。他の tailnet は、明示的に共有しない限り、このマシンを発見したり接続したりできません。ただし、新規 tailnet のデフォルトポリシーでは、同じ tailnet 内のデバイス間アクセスが許可されています。また Tailscale が保護するのは overlay ネットワークだけで、LAN やパブリック IPv6 から DGX Spark への直接アクセスを自動的に遮断するわけではありません。そのため、以下のアクセス制御とシステムレベルの堅牢化は引き続き必要です。

### SSH のデフォルトポートを変更する

`/etc/ssh/sshd_config` を編集し、`Port` フィールド前の `#` を外して、希望するポート番号に変更します。その後 SSH サービスを再起動します。

```
sudo systemctl restart ssh
```

SSH ポートを変更した場合は、ファイアウォールルール内のポート番号も同時に変更してください。

### ファイアウォールを有効にする

ファイアウォールは有効化をおすすめします。グローバルユニキャスト IPv6 アドレスは LAN の NAT では保護されません。上流ルーターとホストファイアウォールが受信を許可していれば、外部デバイスは DGX Spark に直接アクセスできます。以下のルールは参考例として、必要に応じて調整してください。

```
# LAN からのアクセスは制限しない。ここでは LAN が 192.168.1.0/24 であると仮定します。
sudo ufw allow from 192.168.1.0/24

# tailscale0 インターフェースから SSH へのアクセスを許可。SSH ポートを変更していない前提です。
sudo ufw allow in on tailscale0 to any port 22

# ufw ファイアウォールを有効化。ufw のデフォルトは、受信をすべて拒否し、送信をすべて許可です。
sudo ufw enable
```

ufw の状態を確認します。

これは最小限のファイアウォールルール例です。LAN 方向は制限せず、Tailscale 経由の SSH アクセスを許可します。Tailscale は VPN 通信用の `tailscale0` インターフェースを作成します。この設定により、LAN と外部ネットワークのどちらからでも `nvidia-sync` 経由で DGX Spark にアクセスでき、IPv6 を含むその他の外部アクセスは遮断できます。

## まとめ

この記事では、DGX Spark のリモート接続とセキュリティ設定を紹介しました。

* **リモート接続**は SSH サービスに依存します。まず `ssh` サービスが正常に動作していることを確認します。
* **LAN 接続**には `nvidia-sync` の利用をおすすめします。mDNS で LAN 内の DGX Spark を自動検出し、簡単に接続できます。
* **別ネットワークからの接続**では、パブリック IPv6 の SSH を直接公開すべきではありません。Tailscale を使い、認可済み ID だけに見える暗号化 overlay ネットワークを構築します。NVIDIA Sync のリモート接続機能は、内蔵 Tailscale 統合によって実現されています。
* **Tailscale のセキュリティ**は、新規 tailnet のデフォルト全許可ポリシーで止めてはいけません。利用シナリオに応じて Device Approval または Tailnet Lock を有効にし、Grants でユーザーと協力者を DGX Spark に必要なポートだけへ制限します。
* **Aperture AI Gateway** は、Tailscale ID を使って Claude Code、Codex、Gemini CLI などのクライアントを認証し、モデル API Key を集中管理できます。外部モデルと DGX Spark のプライベートモデルを、同じアクセス制御、監査、予算ポリシーの下に置けます。
* **Tailscale の料金**は主に、商用ユーザー席位、企業管理・コンプライアンス機能、プラン上限を超えるリソースに関係します。個人の非商用利用で DGX Spark 1 台を使う程度なら、通常は無料の Personal プランで十分です。
* **ネットワークセキュリティ**では、DGX Spark は本質的に Ubuntu マシンです。SSH のデフォルトポート変更と ufw ファイアウォール設定は、基本的な堅牢化手段です。
