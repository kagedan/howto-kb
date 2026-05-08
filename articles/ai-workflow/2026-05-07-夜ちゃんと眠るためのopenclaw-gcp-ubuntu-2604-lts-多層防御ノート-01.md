---
id: "2026-05-07-夜ちゃんと眠るためのopenclaw-gcp-ubuntu-2604-lts-多層防御ノート-01"
title: "夜ちゃんと眠るための、OpenClaw × GCP × Ubuntu 26.04 LTS 多層防御ノート"
url: "https://zenn.dev/noah33/articles/openclaw-gcp-ubuntu-security"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

!

**📖 このノートについて**

OpenClawをGCPで動かすにあたって、セキュリティをどこから手を付ければいいか——公式ドキュメントを行ったり来たりしながら、自分なりに地図を引いてみた**個人ノート** です。

想定環境はタイトルのとおり、**GCP Compute Engine上のUbuntu 26.04 LTS に OpenClaw 2026.5.5 をセットアップした構成**。読み物として通して読むことも、必要なときに該当の章だけ拾うこともできるよう、**OpenClaw自身の設定 → OS（Ubuntu）→ VM（GCP）の順に、内側から外側へ** 積み上げていく流れで書いています。

もし同じような構成で動かしている方が、何かひとつでも持ち帰れる気づきがあれば嬉しいです。

!

**ℹ️ 読みはじめる前に、ひとつだけ**

ここに書いてあるのは、私が自分の環境で実際にやっている／気をつけていることを並べただけのものです。OpenClaw・GCP・Ubuntu の仕様は日々アップデートされていきますし、最適な対策は環境や運用要件によって変わります。**完成された手順書ではなく、ひとつの試行錯誤の記録** くらいの距離感で眺めていただけると、書いている側も気が楽でちょうどよいです。

コマンドや設定値は、最新の仕様を公式ドキュメントで確かめつつ、ご自身の環境で動作を見ながら取り入れていってもらえると安心です。

## はじめに：なぜここまで丁寧に固めるのか

OpenClawはローカルで動くAIエージェントランタイムです。コード実行・ファイル操作・外部API呼び出し・ブラウザ操作（CDP経由）と、できることが多い分、攻撃者から見ても魅力的なターゲットになります。「便利さ」と「攻撃面の広さ」は表裏一体なので、このあたりは少し慎重すぎるくらいでちょうどいいと思っています。

クラウドで動かす場合、オンプレでは出てこなかった脅威も追加されます。代表的なものを並べると、こんな感じです。

## まず押さえておきたい大前提

| 方針 | 内容 |
| --- | --- |
| 1 Gateway = 1 信頼境界 | 複数ユーザを混ぜない。別の信頼境界が必要なら**別Gatewayを立てる** |
| 専用GCPプロジェクト | OpenClaw専用プロジェクトに分離して、IAMを独立させる |
| Shielded VM | `--shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring` を全部有効化 |
| 最小権限のサービスアカウント | デフォルトのCompute Engine SAは使わず、専用SAを作る。`Editor`は避ける |
| OS Login + 2FA | `enable-oslogin=TRUE`, `enable-oslogin-2fa=TRUE` |
| External IP不要 | VMは内部IPのみ。egressはCloud NAT、管理アクセスはIAP TCP forwarding |
| VPC firewall は default-deny | デフォルトVPCを使わず、IAP経由のSSHだけ ingress allow |
| 専用Linuxユーザー | OS内では`openclaw`専用ユーザーで実行。rootで動かさない |
| Gateway は loopback バインド | `gateway.bind: "loopback"`（既定値）。LAN公開は避ける |
| Gateway 認証必須 | `gateway.auth.mode: "token"` でランダム長文字列。`OPENCLAW_GATEWAY_TOKEN`で渡す |
| 高リスクツールは deny 既定 | `tools.deny: ["group:automation","group:runtime","group:fs","sessions_spawn"]` |
| `tools.exec.security: "deny"` | 信頼が固まるまでexec実行は禁止。必要時だけ`"sandbox"`に緩和 |

「先に全部読んでから始める派」のために、最初のVM作成コマンドだけ載せておきます。本文中の各章で、ここから何を増やしていくかが見えてくるはずです。

```
# Shielded + 最小権限SA + 内部IPのみ + OS Loginの Ubuntu 26.04 LTS VM
gcloud compute instances create openclaw-vm \
  --zone=asia-northeast1-a \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2604-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --service-account=openclaw-runtime@PROJECT_ID.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform.read-only \
  --no-address \
  --metadata=enable-oslogin=TRUE,enable-oslogin-2fa=TRUE \
  --tags=openclaw,iap-ssh
```

## 第1層：OpenClaw自身の設定をきちんと固める

外側のVMハードニングよりも先に、**OpenClaw自身が用意してくれているセキュリティ機能を使い切る** ことが、いちばん効きます。Gateway・Tool権限・Sandbox・Skillsの4つに、最初から手厚いコントロールが入っているので、これを活かさない手はありません。

### 1-1. まず `openclaw security audit` を走らせる

OpenClaw 2026.5系には、設定ドリフト・露出・権限・プラグインの健全性を一気にチェックしてくれる組み込みコマンドがあります。何か特別な設定をする前に、まず現状を見せてもらうのがおすすめです。

```
# まずはこれ。現状把握
openclaw security audit

# Gateway にライブで投げてもう一段深く見る
openclaw security audit --deep

# 自動修復可能な項目（権限の絞り込み・allowlist変換・機密のリダクション）を直してくれる
openclaw security audit --fix

# CIや定期実行向け
openclaw security audit --json | tee /var/log/openclaw/audit-$(date +%F).json
```

!

**💡 週次で回しておくと、ちょっとしたドリフトも拾える**

`0 4 * * 1 openclaw openclaw security audit --deep --json > /var/log/openclaw/audit-weekly.json` を `/etc/cron.d/openclaw-audit` に置いて、結果をCloud Loggingに流す運用にしておくと、知らないうちに緩んだ設定にも気づけます。

### 1-2. Gateway のバインドと認証

`~/.openclaw/openclaw.json` のハードニング・テンプレートです。「最初から全部 deny で出発して、必要に応じて allow に昇格させていく」スタンスでまとめています。

```
{
  gateway: {
    mode: "local",
    bind: "loopback",                          // 0.0.0.0 や lan は避ける
    port: 18789,
    auth: {
      mode: "token",                           // トークン認証
      token: "${OPENCLAW_GATEWAY_TOKEN}"       // 環境変数で注入（リポジトリにはコミットしない）
    },
    trustedProxies: [],                        // リバースプロキシ越しに使う場合のみ列挙
    nodes: {
      allowCommands: [],                       // ノード横断コマンドはデフォルト拒否
      denyCommands: ["*"],
      browser: { mode: "off" }                 // ブラウザリモート操作は明示的にonにするまでoff
    }
  },
  session: {
    dmScope: "per-channel-peer"                // チャネル経由で複数人がDMする場合の文脈漏洩対策
  },
  tools: {
    profile: "messaging",                      // 最小プロファイルから出発
    allow: [],                                 // 必要になった時点で個別allowに昇格
    deny: [
      "group:automation",
      "group:runtime",
      "group:fs",
      "sessions_spawn",
      "sessions_send",
      "gateway",                               // 制御プレーン操作は禁止
      "cron",                                  // 永続スケジュール作成も禁止
      "elevated"
    ],
    exec: {
      security: "deny",                        // execは原則禁止（必要時だけ"sandbox"に）
      ask: "always"                            // 例外的に許可する場合も毎回確認
    }
  },
  agents: {
    defaults: {
      sandbox: {
        mode: "all",                           // 全セッションをsandbox化（"non-main"でも可）
        scope: "agent",                        // エージェント単位で隔離
        backend: "docker",
        workspaceAccess: "none",               // ワークスペースは原則見せない
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          network: "none",                     // sandboxからの外向き通信を遮断
          readOnlyRoot: true,
          user: "sandbox",
          capDrop: ["ALL"],
          pidsLimit: 256,
          memory: "1g",
          cpus: "1.0",
          tmpfs: ["/tmp:rw,noexec,nosuid,size=64m"],
          seccompProfile: "/etc/openclaw/seccomp/default.json",
          apparmorProfile: "openclaw-sandbox"
        }
      }
    }
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",                     // 未知の相手には1時間有効のペアリングコード
      groups: { "*": { "requireMention": true } }
    }
  }
}
```

トークンは設定ファイルに直接書かず、systemd経由で環境変数で渡すのが安心です。

```
sudo systemctl edit openclaw
# [Service]
# Environment=OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)
sudo systemctl restart openclaw

# 設定ファイルの権限も忘れずに
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
```

!

**💡 このテンプレで何を防いでいるのか**

**`bind: "loopback"`**

* リスク：Gatewayが`0.0.0.0`で待ち受けていると、LANやインターネットから誰でも到達できてしまう
* 対策：受け口を自分自身（loopback）だけにして、外から繋ぎたいときは安全な経路（IAP / Tailscale）を別途用意する
* 例えるなら：玄関を直接表通りに開けず、いったんマンションのオートロック（IAP）を通させる

**`auth.mode: "token"` + 環境変数注入**

* リスク：JSONファイルに平文でトークンを書くと、git commitやバックアップで思わぬ場所に流出する
* 対策：トークンは設定ファイルから切り離し、systemdの`EnvironmentFile`で別管理にする
* 例えるなら：玄関の鍵を、家の見取り図と同じノートに書き留めない

**`nodes.browser.mode: "off"`**

* リスク：ブラウザツールは「ログイン済みのGmailやGitHubに自由にアクセスできる権限」を持つ。乗っ取られたら被害がブラウザのプロファイル全体に及ぶ
* 対策：使う必要が出るまでoff、使うときも専用プロファイルに分離する
* 例えるなら：他人にPCを貸すとき、自分のChromeにログインしたまま渡さない

**`dmScope: "per-channel-peer"`**

* リスク：同じチャネルに複数人がいる場合、Aさんの文脈がBさんの返答に混ざって機密が漏れることがある
* 対策：会話の文脈を相手ごとに分離する
* 例えるなら：複数の依頼者を抱える窓口担当が、案件ごとにファイルを分けて机に並べるイメージ

**`tools.exec.security: "deny"` + `ask: "always"`**

* リスク：任意コード実行（exec）は、攻撃が最終的に狙う「ゴール」。ここが開いているとプロンプトインジェクション一発で侵害が成立する
* 対策：禁止を既定にし、本当に必要な瞬間だけ確認付きで開ける二段構え
* 例えるなら：包丁は普段は鍵付きの引き出しに入れておいて、料理するときだけ取り出す

**Sandbox `network: "none"` + `readOnlyRoot: true` + `capDrop: ["ALL"]`**

* リスク：万一sandbox内に侵入されても、外への通信・ファイル改竄・特権昇格のいずれかが残っていると被害が広がる
* 対策：その3つの経路を同時に塞ぐ
* 例えるなら：作業部屋に窓も、外線電話も、合鍵もない状態にしておく

**chmod 700 / 600**

* リスク：認証情報やセッション履歴が他のローカルユーザーから読めると、何かのタイミングで芋づる式に乗っ取られる
* 対策：所有者本人しか読めない権限に絞る
* 例えるなら：日記を本棚に置きっぱなしにせず、引き出しの自分の側にしまう

### 1-3. ツール権限：deny-by-default の気持ちで

OpenClawのツール群はグループでまとめられているので、「とりあえずグループ単位で deny」から入れるのが運用しやすいです。**`tools.exec.security: "deny"` を既定にしておいて、必要なときだけ `"sandbox"` に緩める**、くらいの慎重さでちょうどいい印象です。

| グループ | 含まれるツールの例 | 既定 | リスクと対策（例えるなら） |
| --- | --- | --- | --- |
| `group:runtime` | `exec`, `process`, `elevated` | deny | **任意コード実行の入口**。ここが開いていると、悪意あるプロンプト1発で何でもできる状態になる。例えるなら、相手にいきなり厨房の鍵を渡さない |
| `group:fs` | `write`, `edit`, `apply_patch` | deny（読み取り専用ならread単独で許可可） | **ランサムウェア化と改竄の経路**。書き込み権限がなければ、ファイルを暗号化して身代金を要求することもできない。例えるなら、図書館で本を読むのは自由だが、本に書き込むのは別の許可がいる |
| `group:network` | `web_fetch`, `web_search`, `browser` | 必要分のみallow | **プロンプトインジェクションの入口**。Webから取り込んだ文章が新しい命令としてAIに渡ってしまう。`browser`は特に「ログイン済みのGmail/GitHubを操作できる権限」と等価。例えるなら、自分のスマホをロック解除した状態で他人に渡すような怖さがある |
| `group:automation` | `gateway`, `cron`, `sessions_spawn` | deny | **永続化と自己権限拡張の経路**。侵入者が一番欲しがるのが「居続けられる仕組み」。塞いでおくと、たとえ一瞬入られても長居できない。例えるなら、空き巣が合鍵を作ったり、勝手にスペアキーを家族に配ったりするのを防ぐ |

### 1-4. 組み込みSandbox（Docker backend）

OpenClawの`sandbox.mode`は`off` / `non-main` / `all`の3段階が選べます。慣れたら早めに **`"all"` に上げてしまう** のが結果的に楽です。「いざというときは Sandbox の中で起きてくれるから、外側の被害を狭められる」という安心感がだいぶ違います。

!

**💡 なぜ `"all"` を推すか**

* リスク：`non-main`だと、自分が日常的に使うメインセッションだけホスト直で動く。よく使う場所＝攻撃が成立しやすい場所、になりがち
* 対策：全セッションを一律にコンテナの中に入れ、ホスト本体への直接アクセスをなくす
* 例えるなら：実験室で「これは普段の作業だから素手でいいや」と例外を作らず、**毎回かならず手袋を着けて作業する** ルールにする。最初は面倒に感じても、慣れたら「手袋なしの作業」のほうが落ち着かなくなります

```
# 公式のsandbox imageビルド補助スクリプト
bash scripts/sandbox-setup.sh

# AppArmor プロファイルを登録（Ubuntu 26.04 標準）
sudo cp /opt/openclaw/security/openclaw-sandbox.apparmor /etc/apparmor.d/openclaw-sandbox
sudo apparmor_parser -r /etc/apparmor.d/openclaw-sandbox
```

> **公式ドキュメントの一節**
>
> "Sandboxing is **not a perfect security boundary**, but it materially limits filesystem and process exposure."
>
> サンドボックスは万能ではなく、あくまで「被害範囲を狭めるためのもの」と言い切ってあるのが個人的には好きなところです。だからこそ、外側のVM・GCP層がちゃんと意味を持ってきます。

!

**🚨 バインド禁止パスは尊重する**

OpenClawは以下を `agents.defaults.sandbox.docker.binds` から自動拒否してくれます。気を利かせて自前で書き換えたくなっても、ここは触らないでください：`docker.sock`, `/etc`, `/proc`, `/sys`, `/dev`, `~/.aws`, `~/.cargo`, `~/.config`, `~/.docker`, `~/.gnupg`, `~/.netrc`, `~/.npm`, `~/.ssh`

### 1-5. ファイル権限と機密ファイルの居場所

`~/.openclaw/` 配下には、認証情報・モデルAPIキー・セッション履歴など、漏れたら困るものが集まっています。最初に一通りパーミッションを締めておくと、あとが楽です。

```
chmod 700 ~/.openclaw
find ~/.openclaw -type f -name 'openclaw.json' -exec chmod 600 {} \;
find ~/.openclaw/credentials -type d -exec chmod 700 {} \;
find ~/.openclaw/credentials -type f -exec chmod 600 {} \;
find ~/.openclaw/agents -name 'auth-profiles.json' -exec chmod 600 {} \;
find ~/.openclaw/agents -name 'sessions/*.jsonl' -exec chmod 600 {} \;
```

!

**📌 特に守りたいファイル**

* `~/.openclaw/openclaw.json`（Gateway設定）
* `~/.openclaw/credentials/<channel>/...`（WhatsApp等のチャネル資格情報）
* `~/.openclaw/agents/<id>/agent/auth-profiles.json`（モデルAPIキー）
* `~/.openclaw/agents/<id>/sessions/*.jsonl`（チャット履歴）

## 第2層：Skills と ClawHub との付き合い方

OpenClawのSkillsは**ワークスペース内の信頼コード** として読み込まれます。SKILL.mdをワークスペースに置いた瞬間からロードされるため、**Skillを入れる行為は実質的にコードを実行可能にすること** です。ここは少し緊張感を持って付き合う領域だと思っています。

### 2-1. ClawHub経由なら built-in scanner が走ってくれる

ClawHubから`openclaw skills install`したとき、Gateway側で**dangerous-code scanner**（VirusTotal / ClawScan / 静的解析の組み合わせ）が動いて、`critical`判定はデフォルトでブロックされる仕組みになっています。これがあるおかげで、ある程度は安心してClawHubを使えます。

```
# 普段使うのはこの3つでだいたい足ります
openclaw skills discover                       # 検索
openclaw skills install <skill-slug>@1.2.3     # ★必ずバージョンをピン留め
openclaw skills update --all                   # 月次の更新
```

!

**💡 なぜバージョンをピン留めするのか**

* リスク：Skillはいつでも中身を差し替えられる。最新を自動で追いかけていると、ある日こっそり差し込まれた悪意あるバージョンに気づけない（実際の供給チェーン攻撃の典型パターンです）
* 対策：バージョンを固定して、更新は意識的なタイミングでまとめて。「いつ・何が変わったか」が手元のログで追える状態にする
* 例えるなら：スーパーで毎週同じお菓子を買うとき、**ロット番号を確認してから買う** ようなもの。同じ商品名でも、製造ロットが変わると中身が変わっていることがあるので、無頓着に「いつもの」で買い続けない

### 2-2. インストール前のレビュー、ひと手間

数分で終わるので、初めて入れるSkillについては、ぜひ習慣にしたい手順です。

```
# 1. ClawHubのVirusTotalレポートを確認
xdg-open https://clawhub.ai/skills/<slug>

# 2. 直接gitからcloneして読む（ClawHub経由でない場合は必須）
git clone https://github.com/<author>/<skill-name> /tmp/skill-review
less /tmp/skill-review/SKILL.md
less /tmp/skill-review/index.{js,py}

# 3. SKILL.mdのfrontmatterで宣言された権限と、実装が一致しているかチェック
grep -E '^(name|description|metadata|requires)' /tmp/skill-review/SKILL.md

# 4. zip配布の場合はVirusTotal API経由で再スキャン
curl -X POST "https://www.virustotal.com/api/v3/files" \
  -H "x-apikey: ${VT_API_KEY}" \
  -F "file=@skill.zip"
```

### 2-3. Skillの依存パッケージの供給チェーン対策

Skill自身がclean でも、その内側で npm / PyPI を呼んでいる場合、間接的に悪意あるパッケージが入ってくる可能性は残ります。ここは古典的な供給チェーン対策が効きます。

#### Takumi Guard（Flatt Security）：レジストリプロキシで自動ブロック

設定ファイルを1行変えるだけで、悪意あるパッケージをインストール前に止めてくれます。**導入コストが低くて常時ブロックが効く** ので、迷ったらこれを最初に入れる、で間違いないです。

URL: <https://flatt.tech/takumi/features/guard>

```
npm config set registry https://npm.flatt.tech
pnpm config set registry https://npm.flatt.tech
yarn config set registry https://npm.flatt.tech
pip config set global.index-url https://pypi.flatt.tech/simple/

# systemd unit からも参照されるように /etc/environment に追記しておく
echo 'PIP_INDEX_URL=https://pypi.flatt.tech/simple/' | sudo tee -a /etc/environment
echo 'NPM_CONFIG_REGISTRY=https://npm.flatt.tech'    | sudo tee -a /etc/environment
```

#### GuardDog / scfw / Trivy（補完スキャナ）

Takumi Guardが「常時ブロック」役だとすると、こちらは「気になるときに精密検査する」役です。

```
pip install guarddog scfw --break-system-packages
guarddog npm scan <package>
guarddog pypi scan <package>
scfw run pip install <package>
scfw run npm install <package>

# Trivy（Skillの配置先と依存ツリーをスキャン）
sudo apt install trivy
trivy fs --scanners vuln,secret,misconfig ~/.openclaw/agents/<id>/agent/skills
```

## 第3層：OS（Ubuntu）の足元を整える

OpenClaw自身のSandboxはDocker backendですが、その**外側にいるUbuntu OS** にも、AppArmorとsystemd sandboxを重ねておきます。「Sandboxの中の人」が万一抜け出してきても、ホスト側でもう一段引っかかる、というイメージです。

### 3-1. Shielded VM（VMの外側のハードニング）

最初の`gcloud compute instances create`で指定済みですが、改めて中身を整理しておきます。**Secure Boot + vTPM + Integrity Monitoring** の3つを有効化することで、boot/kernelレベルのrootkitやブートローダ改竄を検出できます。Integrity MonitoringのアラートはCloud Loggingと**Security Command Center** に流れていきます。

!

**💡 なぜVM起動の「前」を守るのか**

* リスク：起動プロセスの根っこ（ブートローダ・カーネル）が改竄されると、その上のOSセキュリティ機能（AppArmor等）はすべて無力化されてしまう。下から崩されると上の積み木はぜんぶ倒れる
* 対策：起動の各段階で署名を検証し、初回起動時の状態を「正しい状態」として記録。以降の起動が改竄されたら検知する
* 例えるなら：**家のホームインスペクション報告書を金庫に保管しておく** ようなもの。あとから「基礎が変だな」と思ったとき、最初の状態と比べて初めて改造があったとわかる

```
# Integrity Monitoringのログを確認
gcloud logging read 'resource.type="gce_instance" AND jsonPayload.@type="type.googleapis.com/cloud_integrity.IntegrityEvent"' \
  --limit 20 --format json
```

!

**💡 機密データを扱うなら Confidential VM も視野に**

機密データを扱う構成なら、**Confidential VM** への昇格も検討する価値があります。AMD SEV / SEV-SNP / Intel TDXによる**メモリ暗号化** で、ハイパーバイザレベルの攻撃やDRAM物理攻撃にも備えられます。`--confidential-compute --machine-type=n2d-standard-2` などで作れます。

### 3-2. Ubuntu Pro：Livepatch + USG + ESM

Ubuntu 26.04 LTSは **Ubuntu Pro on GCP** として動かせます。個人利用なら無料枠で5台までLivepatchが使えるので、まずこれだけでも有効化しておくと、運用中の心理的負担がだいぶ違います。

!

**💡 なぜLivepatchが効くのか**

* リスク：カーネルに緊急のCVEが公開されたとき、再起動の調整に時間がかかる間、システムは無防備な状態で晒され続ける。「忙しい時期だから来週パッチ当てよう」と思ううちに、攻撃者のほうが先に着手する
* 対策：再起動なしで稼働中のカーネルにパッチを適用し、「公開→適用」の窓を分単位まで短くする
* 例えるなら：**営業中のままお店の床のひび割れを直せる工法**。「閉店してから直す」前提だと、危ないと分かっていても直せない時間が長く続いてしまう

```
sudo pro attach <TOKEN>

# Livepatch（再起動なしのカーネル脆弱性パッチ）
sudo pro enable livepatch
sudo canonical-livepatch status

# USG（CISベンチマーク自動適用）
sudo pro enable usg
sudo apt install -y usg
sudo usg audit cis_level1_server          # まずは監査
sudo usg fix cis_level1_server            # 内容を確認したら適用

# ESM（10年延長サポート＋追加CVEパッチ）
sudo pro enable esm-infra
sudo pro enable esm-apps
```

### 3-3. unattended-upgrades：セキュリティ更新を自動で

「気がついたら何ヶ月もパッチ当ててなかった」を防ぐ、地味だけど効く設定です。

```
sudo apt install unattended-upgrades apt-listchanges
sudo dpkg-reconfigure -plow unattended-upgrades

# /etc/apt/apt.conf.d/50unattended-upgrades の Allowed-Origins
# Unattended-Upgrade::Allowed-Origins {
#   "${distro_id}:${distro_codename}-security";
#   "${distro_id}ESMApps:${distro_codename}-apps-security";
#   "${distro_id}ESM:${distro_codename}-infra-security";
# };

sudo systemctl enable --now unattended-upgrades
```

### 3-4. AppArmor：OpenClaw専用プロファイル

UbuntuはAppArmorがデフォルトで有効です。OpenClawバイナリ用とSandbox用、2本のプロファイルを用意しておくと、宣言的にアクセス範囲を絞れて気持ちが楽になります。

!

**💡 なぜプロファイルを書くのか**

* リスク：プロセスがLinuxユーザー権限の範囲内で動く以上、「openclawユーザーが触れる場所」にはぜんぶ手が届く。本来必要のない`~/.aws`や`~/.ssh`まで読まれる可能性が残る
* 対策：「このバイナリはこのパス以外触れない」とカーネルレベルで宣言する
* 例えるなら：**社員ごとに入退室カードでアクセスできる部屋を限定する** のと同じ。本人がうっかり別フロアに迷い込もうとしても、ドアが開かない

```
sudo aa-status

# /etc/apparmor.d/usr.local.bin.openclaw
sudo tee /etc/apparmor.d/usr.local.bin.openclaw << 'EOF'
#include <tunables/global>

/usr/local/bin/openclaw {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  #include <abstractions/openssl>

  /usr/local/bin/openclaw mr,

  # OpenClawの標準ディレクトリ
  owner /home/openclaw/.openclaw/** rwk,
  /opt/openclaw/** r,
  /tmp/openclaw-*.log w,

  # Docker socket（Sandbox backendがDockerなので必要）
  /var/run/docker.sock rw,

  # 拒否（明示）
  deny /etc/shadow r,
  deny /root/** rwx,
  deny /home/*/.ssh/** rwx,
  deny /home/*/.gnupg/** rwx,
  deny /home/*/.aws/** rwx,

  network inet stream,
  network inet6 stream,
}
EOF

sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.openclaw
sudo aa-enforce /usr/local/bin/openclaw
```

### 3-5. systemd ユニット：sandbox機能をフルに使う

`/etc/systemd/system/openclaw.service` のテンプレートです。systemdの最近の隔離機能を一通り盛り込んでいます。`systemd-analyze security` のスコアは0に近いほど安全なので、運用を始めたら一度確認してみると面白いです。

```
[Unit]
Description=OpenClaw 2026.5.5 Personal AI Assistant Gateway
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple
User=openclaw
Group=openclaw
ExecStart=/usr/local/bin/openclaw serve
WorkingDirectory=/home/openclaw
Environment=PIP_INDEX_URL=https://pypi.flatt.tech/simple/
Environment=NPM_CONFIG_REGISTRY=https://npm.flatt.tech
EnvironmentFile=-/etc/openclaw/secrets.env
# /etc/openclaw/secrets.env に
#   OPENCLAW_GATEWAY_TOKEN=...
# などを置く（chmod 600 root:root）

# **=** ファイルシステム保護 **=**
ProtectSystem=strict
ProtectHome=tmpfs
BindPaths=/home/openclaw
PrivateTmp=yes
ReadWritePaths=/home/openclaw/.openclaw /var/log/openclaw

# **=** 権限昇格の禁止 **=**
NoNewPrivileges=yes

# **=** ネットワーク制限 **=**
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX

# **=** カーネル・syscall制限 **=**
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectControlGroups=yes
ProtectClock=yes
ProtectHostname=yes
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources @debug @mount @reboot @swap

# **=** Linux Capability **=**
CapabilityBoundingSet=
AmbientCapabilities=

# **=** その他のハードニング **=**
MemoryDenyWriteExecute=yes
RestrictNamespaces=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
LockPersonality=yes
PrivateDevices=yes

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw

# 隔離レベルを点数で見せてくれる便利コマンド
sudo systemd-analyze security openclaw.service
```

!

**💡 systemd ハードニングが効く理由**

**`ProtectSystem=strict` + `ProtectHome=tmpfs`**

* リスク：マルウェアは侵入後「居場所を確保」しようとする。`/usr`や別ユーザーの`/home`にバックドアを書ければ、再起動しても残る
* 対策：プロセスから見える「書ける場所」を最小化し、書き込めるのは作業用ディレクトリだけにする
* 例えるなら：来客には応接間だけ開放し、寝室や書斎には鍵をかけておく

**`NoNewPrivileges=yes`**

* リスク：侵入後にsudoや特殊な実行ファイル（setuid）を踏み台にして権限昇格される
* 対策：「このプロセスは今より強い権限を取れない」と起動時にカーネルに宣言させる
* 例えるなら：アルバイトの社員証では、社長の権限カードと交換できないように設計する

**`CapabilityBoundingSet=`（空）+ `MemoryDenyWriteExecute=yes`**

* リスク：rootで動くプロセスはネットワーク設定変更・カーネルモジュール挿入など何でもできる。さらに、書き換え可能なメモリにコードを流し込む手法（多くのRCE攻撃の定番）が効いてしまう
* 対策：Linux Capabilityを全部剥がし、メモリも「書ける領域」と「実行できる領域」を分離する
* 例えるなら：仮にrootに昇格できても、工具箱を空っぽにしておけば何も組み立てられない、という考え方

**`SystemCallFilter=~@privileged @reboot @mount @swap`**

* リスク：マルウェアはマウント・再起動・スワップなど、普通のアプリが触らないsyscallを使って痕跡を消したり権限を奪ったりする
* 対策：そういう「普段使わないはずのsyscall」を呼んだ瞬間にプロセスを止める
* 例えるなら：レジ担当者が金庫を開けようとしたら警報が鳴る、という業務分掌の発想に近い

## 第4層：マルウェア・ルートキット・カーネルへの備え

ここからは「もし何か入ってしまったら」を前提にした検出・対処のレイヤです。地味ですが、入れておくと夜眠れる種類の対策です。

!

**💡 4つを併用する理由**

* リスク：マルウェアの形は様々（既知の検体／ルートキット／設定の穴／侵入後の痕跡消去）。1種類の対策では必ず取りこぼしが出る
* 対策：守備範囲が重ならない4つを並べて、抜けを減らす
  + ClamAV：「既知のマルウェアシグネチャ」を検出
  + rkhunter：「ルートキットの痕跡」を検出
  + Lynis：「設定の弱点」をスコア化
  + auditd：「ファイルアクセス・syscallの記録」を保全
* 例えるなら：火災対策で、**煙感知器・消火器・スプリンクラー・避難経路図** をぜんぶ用意するのと同じ発想。どれかひとつだけだと、別の種類の事故に間に合わない

### ClamAV：マルウェアスキャン

```
sudo apt install clamav clamav-daemon
sudo freshclam

# /etc/clamav/clamd.conf に追記
# OnAccessIncludePath /home/openclaw/.openclaw/agents
# OnAccessExcludeUname clamav
# OnAccessPrevention yes

sudo systemctl enable --now clamav-daemon clamav-freshclam

# 毎日深夜の定期スキャン
sudo tee /etc/cron.d/openclaw-clamscan << 'EOF'
0 3 * * * root clamscan -r /home/openclaw/.openclaw \
  --log=/var/log/clamav/openclaw-daily.log \
  --bell --move=/var/quarantine
EOF
```

### rkhunter：ルートキット検出

```
sudo apt install rkhunter
sudo rkhunter --update
sudo rkhunter --propupd                   # ★クリーンな状態のベースラインを最初に記録
sudo rkhunter --check --skip-keypress

sudo tee /etc/cron.weekly/rkhunter << 'EOF'
#!/bin/bash
rkhunter --update
rkhunter --check --skip-keypress --report-warnings-only 2>&1 \
  | mail -s "[OpenClaw GCP] rkhunter weekly report" you@example.com
EOF
sudo chmod +x /etc/cron.weekly/rkhunter
```

### Lynis：システム全体のセキュリティ監査

`Hardening index` のスコアが80以上を目指すと、目に見える指標があってモチベーションが続きます。

```
sudo apt install lynis
sudo lynis audit system
```

### auditd：Linux監査サブシステム（OpenClaw特化ルール）

```
sudo apt install auditd audispd-plugins
sudo systemctl enable --now auditd

sudo tee /etc/audit/rules.d/openclaw.rules << 'EOF'
# OpenClaw実行と機密ファイルアクセスを監査
-w /usr/local/bin/openclaw -p x -k openclaw_exec
-w /home/openclaw/.openclaw/openclaw.json -p wa -k openclaw_config
-w /home/openclaw/.openclaw/credentials -p rwa -k openclaw_credentials
-w /home/openclaw/.openclaw/agents -p wa -k openclaw_agents

# 一般機密
-w /etc/shadow -p r -k sensitive_read
-w /root/.ssh -p rwa -k sensitive_ssh

# GCEメタデータサーバアクセス（execve経由）
-a always,exit -F arch=b64 -S execve -F a0=/usr/bin/curl -k metadata_curl
EOF
sudo augenrules --load
```

## 第5層：ランタイム脅威検知（Falco + Cloud Logging）

ここまでの層が「攻撃を入れない・広げない」のための設計だとすると、この層は「もし何か起きたら、なるべく早く気づく」ためのレイヤです。GCPの強みが効いてくるところでもあります。

### 5-1. Ops Agent + Cloud Logging：ログをまとめてGCPに送る

**Ops Agent** はGCP Compute Engine用の統合エージェント（Fluent Bit + OpenTelemetry Collector）で、入れるだけでメトリクスとログをCloud LoggingとCloud Monitoringに送ってくれます。VM内に閉じたログだけ見ていると、消されたり改竄されたりして気づけないことがあるので、ここは早めに繋いでおきたいレイヤです。

```
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
sudo systemctl status google-cloud-ops-agent
```

`/etc/google-cloud-ops-agent/config.yaml` を編集してOpenClaw関連ログを取り込みます。

```
logging:
  receivers:
    openclaw:
      type: files
      include_paths:
        - /tmp/openclaw/openclaw-*.log
        - /var/log/openclaw/*.log
    openclaw_audit:
      type: files
      include_paths:
        - /var/log/openclaw/audit-*.json
    falco:
      type: files
      include_paths:
        - /var/log/falco.log
    auditd:
      type: files
      include_paths:
        - /var/log/audit/audit.log
  service:
    pipelines:
      default_pipeline:
        receivers: [openclaw, openclaw_audit, falco, auditd, syslog]
```

```
sudo systemctl restart google-cloud-ops-agent
```

### 5-2. Cloud Audit Logs：GCP API操作の監査

Compute Engineの操作（VM作成・SSH鍵更新・メタデータ書換など）はAdmin Activityログとして無効化不可で記録されます。Data Access Logsは別途有効化が必要です。「VMにSSHした履歴は残るのか？」が気になったときに、ここを見る習慣をつけておくと安心です。

```
gcloud logging read 'protoPayload.serviceName="compute.googleapis.com"' --limit 20 --format json
```

### 5-3. Falco：プロセス・ネットワークの異常行動検知

Ubuntu 26.04ではmodern eBPF probeで動かすのが推奨です。「カーネルに直接センサーを刺す」ような形でシステムコールを観測できます。

!

**💡 なぜ検知レイヤを置くのか**

* リスク：どれだけ予防策を積んでも、未知の脆弱性や設定ミスで突破される可能性はゼロにならない。突破された後、気づくのが数日後になると被害が桁違いに広がる
* 対策：「想定外の動き（メタデータサーバへの突然のアクセス、ホストでのシェル起動、認証情報ディレクトリへの読み取りなど）」を、起きた瞬間に通知する
* 例えるなら：**家中に動体センサーを置く** ホームセキュリティ。鍵を二重三重にかけても、それでも何か動いたら知らせてほしい、という安心感の保険

```
curl -fsSL https://falco.org/repo/falcosecurity-packages.asc \
  | sudo gpg --dearmor -o /usr/share/keyrings/falco-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] https://download.falco.org/packages/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/falcosecurity.list
sudo apt update && sudo apt install falco

# /etc/falco/falco.yaml で modern eBPF を有効化
# engine:
#   kind: modern_ebpf
```

OpenClaw向けのカスタムルールです。「これが鳴ったらほぼ間違いなくおかしい」という条件だけを集めています。

`/etc/falco/rules.d/openclaw.yaml`：

```
# **=****=****=****=****=****=****=****=****=****=****=****=**
# OpenClaw 2026.5.5 on GCP Ubuntu 26.04 LTS 用ルール
# **=****=****=****=****=****=****=****=****=****=****=****=**

- rule: OpenClaw Workspace Escape
  desc: OpenClawプロセスが想定外のパスに書き込んだ
  condition: >
    open_write and
    proc.name = "openclaw" and
    not fd.name startswith "/home/openclaw/.openclaw" and
    not fd.name startswith "/tmp/openclaw" and
    not fd.name startswith "/var/log/openclaw"
  output: >
    OpenClaw wrote outside its allowed paths
    (file=%fd.name pid=%proc.pid cmdline=%proc.cmdline)
  priority: CRITICAL
  tags: [openclaw, filesystem]

- rule: OpenClaw Spawned Shell Outside Sandbox
  desc: OpenClawがホスト上で直接シェルを起動した（sandbox bypass疑い）
  condition: >
    spawned_process and
    proc.pname = "openclaw" and
    proc.name in (shell_binaries) and
    not container.id != "host"
  output: >
    OpenClaw spawned a host shell! (shell=%proc.name parent=%proc.pname cmdline=%proc.cmdline)
  priority: CRITICAL
  tags: [openclaw, sandbox_bypass, rce]

- rule: OpenClaw Hit GCE Metadata Server
  desc: OpenClawがGCEメタデータサーバ（169.254.169.254）にアクセスした
  condition: >
    outbound and
    proc.name = "openclaw" and
    fd.sip = "169.254.169.254"
  output: >
    OpenClaw accessed GCE metadata server
    (proc=%proc.name dest=%fd.sip:%fd.sport cmdline=%proc.cmdline)
  priority: CRITICAL
  tags: [openclaw, gcp, credential_theft]

- rule: OpenClaw Touched Credential Directory
  desc: OpenClawが守るべき機密ディレクトリにアクセスした
  condition: >
    open_read and
    proc.name = "openclaw" and
    (fd.name startswith "/home/openclaw/.aws" or
     fd.name startswith "/home/openclaw/.ssh" or
     fd.name startswith "/home/openclaw/.gnupg" or
     fd.name startswith "/home/openclaw/.config/gcloud" or
     fd.name = "/etc/shadow")
  output: >
    OpenClaw accessed credential file (file=%fd.name)
  priority: CRITICAL
  tags: [openclaw, credential_theft]

- rule: OpenClaw Gateway Bound Beyond Loopback
  desc: openclaw が 0.0.0.0 や LAN address でリッスンした（loopback以外）
  condition: >
    inbound and
    proc.name = "openclaw" and
    fd.sport = 18789 and
    not fd.sip in ("127.0.0.1", "::1")
  output: >
    OpenClaw Gateway listening on non-loopback (addr=%fd.sip:%fd.sport)
  priority: CRITICAL
  tags: [openclaw, gateway, exposure]

# Macros
- macro: shell_binaries
  items: [bash, sh, zsh, fish, dash, ksh]
```

```
sudo systemctl enable --now falco-modern-bpf
sudo journalctl -u falco-modern-bpf -f

# テストでわざと違反を起こしてみる
sudo -u openclaw curl -s http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token \
  -H "Metadata-Flavor: Google"
# CRITICAL アラートが出ればOK
```

### 5-4. Wazuh（任意）：HIDSをもう一段深く

FalcoがOpenClawのプロセス監視に特化しているのに対し、**Wazuhはホスト全体を見張る** 役割を担います。Cloud Loggingで足りる構成なら省略してもいいですが、コンプライアンス要件がある場合や、自前のSIEMダッシュボードを持ちたい場合は足してみてください。

```
curl -sO https://packages.wazuh.com/4.x/wazuh-install.sh
sudo bash wazuh-install.sh -a
```

!

**📌 Wazuhで見ておきたいもの**

* **FIM**：`~/.openclaw/openclaw.json`、`~/.openclaw/credentials/`、`/usr/local/bin/openclaw`
* **ログ分析**：`/tmp/openclaw/openclaw-*.log`
* **脆弱性検知**：インストール済みパッケージのCVEチェック
* **メタデータサーバアクセス**：`169.254.169.254`へのアクセスをルール化

### 5-5. Security Command Center（組織運用時）

組織レベルでGCPを使っている場合、**Security Command Center** の Standardティアを有効化すると、Shielded VMのIntegrity Monitoring結果、誤設定（パブリックIP / 0.0.0.0/0 のSSH許可など）、Web Security Scannerの結果が一覧で眺められて便利です。

## 第6層：ネットワークまわり

VPC firewallはVMの外側、nftablesはVMの中。両方使うのが、結果的に一番強くて運用が楽な組み合わせだと思っています。

### 6-1. VPC firewall：default-deny + IAPだけ許可

!

**💡 なぜ default-deny から入るのか**

* リスク：「必要そうなものを開ける」発想だと、運用の途中で開けたルールを誰も覚えておらず、何ヶ月も穴が放置される
* 対策：最初に全部閉じておき、必要なものだけを明示的にallowする。許可ルール一覧 = 「いま外と繋がっている経路の全リスト」になる
* 例えるなら：**ホテルの客室ドアと同じ発想**。基本は施錠されていて、滞在中の人だけがカードキーで開けられる。「とりあえず開けておいて、怪しい人が来たら閉める」運用ではホテルは成り立たない

```
gcloud compute firewall-rules delete default-allow-ssh default-allow-rdp default-allow-icmp default-allow-internal --quiet

# IAP TCP forwarding経由のSSHのみ許可（35.235.240.0/20 はIAP送信元レンジ）
gcloud compute firewall-rules create allow-ssh-from-iap \
  --network=openclaw-vpc \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=35.235.240.0/20 \
  --target-tags=iap-ssh

# LLM API宛 egress のみ許可（IPは要確認・更新）
gcloud compute firewall-rules create allow-egress-llm \
  --network=openclaw-vpc \
  --direction=EGRESS \
  --action=ALLOW \
  --rules=tcp:443 \
  --destination-ranges=35.245.32.0/22 \
  --target-tags=openclaw

# それ以外のegressは拒否
gcloud compute firewall-rules create deny-egress-all \
  --network=openclaw-vpc \
  --direction=EGRESS \
  --action=DENY \
  --rules=all \
  --priority=65535 \
  --destination-ranges=0.0.0.0/0 \
  --target-tags=openclaw
```

### 6-2. IAP TCP forwarding：管理アクセスはこれが一番楽

External IPなしでSSH／OpenClaw Gateway UIに繋げます。VPNソフトを別途維持するより、こっちに寄せたほうが運用が単純で気持ちが楽です。

!

**💡 なぜVPNではなくIAPなのか**

* リスク：VPNサーバ自体がインターネットに公開されるため、サーバの脆弱性や鍵管理ミスで侵入経路になり得る。IPアドレス制限だけだと、誰がアクセスしたかが追えない
* 対策：Google IAMで「誰が」アクセスできるかを管理し、TCP通信を暗号化トンネルでGoogle側から流す。VMはExternal IPを持たないままでよい
* 例えるなら：**マンションのオートロック + コンシェルジュ受付**。住人リスト（IAM）に名前があり、本人確認（OAuth）が通った人だけが入居者の部屋に取り次がれる。誰がいつ訪問したかも記録される

```
# IAM ロール付与
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=user:you@example.com \
  --role=roles/iap.tunnelResourceAccessor
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=user:you@example.com \
  --role=roles/compute.osLogin

# IAP経由でSSH
gcloud compute ssh openclaw-vm --zone=asia-northeast1-a --tunnel-through-iap

# OpenClaw Gateway をローカル18789にトンネル
gcloud compute start-iap-tunnel openclaw-vm 18789 \
  --local-host-port=localhost:18789 \
  --zone=asia-northeast1-a

# 認証トークンを付けてGateway UIにアクセス
open "http://localhost:18789/?token=${OPENCLAW_GATEWAY_TOKEN}"
```

### 6-3. Cloud NAT + Private Google Access

External IPを持たないVMでもインターネット側へ出ていけるようにし、なおかつ`*.googleapis.com`への通信はインターネットを経由しない、というネットワーク構成を整えます。

```
gcloud compute routers create openclaw-router \
  --network=openclaw-vpc \
  --region=asia-northeast1

gcloud compute routers nats create openclaw-nat \
  --router=openclaw-router \
  --region=asia-northeast1 \
  --auto-allocate-nat-external-ips \
  --nat-all-subnet-ip-ranges \
  --enable-logging

gcloud compute networks subnets update openclaw-subnet \
  --region=asia-northeast1 \
  --enable-private-ip-google-access
```

### 6-4. nftables：VM内部のUID単位egress制限

VPC firewallはVMの外側、nftablesはVMの中。**ユーザー（UID）単位のアウトバウンド制限** はVPC firewallでは書けないので、ここはnftablesにお願いします。

`/etc/nftables.conf`：

```
table inet openclaw_filter {
  chain output {
    type filter hook output priority 0; policy accept;

    # openclawユーザーからの通信を制限
    skuid openclaw ip daddr 35.245.32.0/22 tcp dport 443 accept
    skuid openclaw ip daddr 169.254.169.254 reject     # GCEメタデータサーバを明示拒否
    skuid openclaw reject with icmp type net-prohibited
  }
}
```

```
sudo systemctl enable --now nftables
sudo nft -f /etc/nftables.conf
```

## 第7層：バックアップ — 最後の砦

### Persistent Disk：スナップショットスケジュール

毎日決まった時間に自動でスナップショットを取って、30日分残しておく構成です。手で取る運用は続かないので、最初にスケジュール化してしまうのがおすすめです。

!

**💡 なぜ「スケジュール」が大事なのか**

* リスク：「気づいたときに手で取る」運用は、最初の1ヶ月だけ続いて、忙しくなった瞬間に止まる。事故が起きるのは決まって取り忘れた週
* 対策：人間の意志に依存せず、毎日同じ時刻に自動で取り、古いものから自動で消す
* 例えるなら：**スマホの自動バックアップ** と同じ発想。意識して毎日PCに繋ぐより、寝ている間にWi-Fiで勝手に取られているほうが結果的に確実

```
gcloud compute resource-policies create snapshot-schedule openclaw-daily \
  --region=asia-northeast1 \
  --max-retention-days=30 \
  --start-time=04:00 \
  --daily-schedule \
  --on-source-disk-delete=apply-retention-policy \
  --storage-location=asia-northeast1

gcloud compute disks add-resource-policies openclaw-data \
  --zone=asia-northeast1-a \
  --resource-policies=openclaw-daily
```

### Cloud Storage：バージョニング + Retention Lock

ランサムウェア対策の本命がこれです。**Retention Lock** をかけると、設定した保持期間の間はオブジェクトを誰も削除できなくなります。たとえアカウントが乗っ取られても、過去のバックアップは守られます。

```
gsutil mb -l asia-northeast1 -b on gs://openclaw-backups
gsutil versioning set on gs://openclaw-backups
gsutil retention set 90d gs://openclaw-backups
gsutil retention lock gs://openclaw-backups   # ★これ以降ポリシー解除不可
```

### `~/.openclaw` の定期同期

```
# /etc/cron.d/openclaw-backup
0 2 * * * openclaw gsutil -m rsync -d -r \
  -x '.*\.log$|.*sandboxes/.*' \
  /home/openclaw/.openclaw \
  gs://openclaw-backups/openclaw-config/
```

## 全体像を図でまとめると

ここまで積み上げてきた防御層を、**外側（GCP）から内側（Skills）へ** ネストして配置した構成図です。一番内側の `Skills` が攻撃者の最終ターゲットで、そこに辿り着くまでに何枚の壁があるか、を一望できるように描いています。

攻撃者は外側の GCP 境界から入って、最深部の **Skills** に到達するまでに 7 層を順に突破する必要があります。==**どこか 1 層が破られても、内側の層が独立に効く**== ── これが Defense in Depth の構造的な強みです。

### 攻撃者の侵入経路と防御層の対応

「どの脅威が、どの層で止まるのか」を別の角度からも見ておきます。最後に立つのは ==**人間の判断**== ── ここだけは自動化できません。

## 全体像をひとつの表にまとめると

ここまでの内容を一望できる早見表です。「あれ、この層は何で守ってたっけ？」となったときに戻ってきてください。

| セキュリティ層 | 主軸 | 補強 |
| --- | --- | --- |
| **OpenClaw Gateway** | `bind: loopback` + token認証 + `tools.exec.security: deny` | Tailscale Serve / IAP（外部公開する場合） |
| **OpenClaw Tools** | `tools.profile: messaging` + `deny: [group:runtime, group:fs, group:automation]` | tool単位allowlist |
| **OpenClaw Sandbox** | `sandbox.mode: all` + Docker backend + AppArmor profile | `network: none` + `readOnlyRoot: true` + `capDrop: [ALL]` |
| **OpenClaw Skills** | ClawHub + VirusTotalスキャン + バージョンピン | `--dangerously-force-unsafe-install` 厳禁 |
| **OpenClaw 監査** | `openclaw security audit --deep --json` 週次 | Cloud Logging連携 |
| VMの外側のハードニング | **Shielded VM**（Secure Boot + vTPM + Integrity Monitoring） | Confidential VM |
| 認証・アクセス | **OS Login + 2FA** + IAM最小権限 | service account scopes 限定 |
| 管理アクセス | **IAP TCP forwarding** | Tailscale Serve |
| OS層パッチ | **Ubuntu Pro Livepatch** + **unattended-upgrades** | ESM / USG |
| プロセス隔離 | **systemd sandbox** + **AppArmor** | Firejail |
| 供給チェーン（Skill依存） | **Takumi Guard**（常時ブロック） | GuardDog + scfw + Trivy |
| マルウェア | **ClamAV** + **rkhunter** + **Lynis** + **auditd** | — |
| ランタイム検知 | **Falco（modern eBPF）** + **Cloud Logging（Ops Agent）** | Wazuh / Security Command Center |
| ネットワーク（VM外） | **VPC firewall**（default-deny ingress + egress allowlist） | Cloud NAT / Private Google Access |
| ネットワーク（VM内） | **nftables**（UID単位） | — |
| バックアップ | **Persistent Disk スナップショット** | **Cloud Storage Retention Lock** |
| 監査 | **Cloud Audit Logs**（Admin Activity 強制） | Data Access Logs（IAM auditConfigs） |

### 正直なところの評価

「言うは易く行うは難し」の世界なので、各レイヤの実効性を5段階で見積もってみました。あくまで個人の感覚値ですが、ご参考まで。

| 項目 | 強度 | 補足 |
| --- | --- | --- |
| OpenClaw自体の権限統制 | ★★★★★ | `openclaw security audit --deep` で常時ドリフト検知できる。最も効くレイヤ |
| Skill供給チェーン | ★★★★★ | ClawHub VirusTotal + Takumi Guard + GuardDog + Trivyの4層でかなり堅い |
| プロセス隔離 | ★★★★★ | OpenClaw Sandbox + AppArmor + systemd sandbox + Shielded VM の4重 |
| 管理アクセス制御 | ★★★★★ | IAP + OS Login + 2FA は VPN + 鍵管理よりも安全で運用が楽 |
| カーネルパッチ | ★★★★★ | **Livepatch** で再起動なしに緊急CVEが塞がる |
| ランタイム検知 | ★★★★★ | Falco + Cloud Logging + SCC で商用EDR水準 |
| バックアップ耐性 | ★★★★★ | Cloud Storage の **Retention Lock** によりランサムウェアからも守れる |
| プロンプトインジェクション対策 | ★★★☆☆ | OpenClawは外部コンテンツの特殊トークンを除去してくれるが、根本解決ではない。最終防衛線は人間の判断 |

## どこから手を付けるか — おすすめの順番

「全部一気にやる」のは現実的ではないので、効くものから段階的に積み上げる順番を提案します。Step 1だけでも入れておけば、まずまず夜眠れるラインに届きます。

!

**⚠️ Step 2（1週間以内）**

* **Ubuntu Pro attach** → Livepatch + USG + ESM 有効化
* **unattended-upgrades** 設定
* **Ops Agent** → Cloud Logging 連携、`/tmp/openclaw/*.log`を取り込み
* ClamAV + rkhunter + Lynis + auditd インストールと定期スキャン
* Takumi Guard / GuardDog / Trivy を Skill 依存ツリーに対して運用ルーチン化
* **OpenClaw Sandbox を `mode: "all"` に昇格**

!

**ℹ️ Step 3（1ヶ月以内）**

* **Falco（modern eBPF）** + 本ノートのOpenClawカスタムルール
* **Persistent Disk スナップショットスケジュール**
* **Cloud Storage** バックアップ + Retention Lock
* AppArmor `usr.local.bin.openclaw` プロファイル運用開始
* **`openclaw security audit --deep --json` を週次cronに登録**

!

**💡 Step 4（安定運用後）**

* nftables による UID 単位 egress 制限
* Wazuh セットアップ
* Security Command Center Standard 有効化
* Confidential VM への移行検討
* VPC Service Controls による境界設定
* ブラウザツール利用時：専用ブラウザプロファイル分離 + `gateway.nodes.browser.mode: "off"` をベースに

## おわりに

!

**📝 「便利だけど怖い」と感じる感覚は、たぶん正しい**

AIエージェントを動かすのって、ワクワクする一方で、ちょっと怖いですよね。その「怖い」という感覚は、たぶん正しい直感です。怖がりすぎず、でも油断しない、くらいのバランスで付き合うのがちょうどいいと思っています。

GCP上のUbuntu 26.04 LTS で OpenClaw 2026.5.5 を動かす場合、まず **OpenClaw自身のGateway / Tool / Sandbox / Skills 設定を `openclaw security audit` で堅め**、その上に **Shielded VM + IAP + OS Login + Ubuntu Pro Livepatch + Falco + Cloud Logging + Persistent Disk スナップショット** を重ねていけば、商用EDRに匹敵する水準を、無料〜低コストで組み上げられます。クラウドの良さは、VMの外側にも防御層を積めること。オンプレでDockerだけで頑張るより、構造的にだいぶ楽になります。

> **最終防衛線は人間の判断**
>
> ただ、どれだけ技術的な対策を積み重ねても、最後の最後の砦は\*\*「怪しいSkillを入れない」「プロンプトインジェクションに気づく」「`--dangerously-force-unsafe-install`を絶対に使わない」という、私たち自身の判断\*\* です。ツールはあくまで「気づきを早くしてくれるもの」。判断のスピードと精度を支えるパートナーとして、上手に頼っていけたらいいなと思います。

## 参考にしたドキュメント

### OpenClaw

### Google Cloud

### Ubuntu
