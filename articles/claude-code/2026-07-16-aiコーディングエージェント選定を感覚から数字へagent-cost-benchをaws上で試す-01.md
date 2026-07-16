---
id: "2026-07-16-aiコーディングエージェント選定を感覚から数字へagent-cost-benchをaws上で試す-01"
title: "AIコーディングエージェント選定を“感覚”から“数字”へ：agent-cost-benchをAWS上で試す"
url: "https://zenn.dev/nttdata_tech/articles/130bd43f48e425"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

AIコーディングエージェントの活用が広がる中で、開発現場では次のような問いが増えてきました。

* Kiro、Claude Code、GitHub Copilot、Codexなど、どのツールを選ぶべきか
* 同じツールでも、どのモデルを使うべきか
* 高性能なモデルを使うコストは、品質向上に見合っているのか
* チームや案件全体に展開したとき、費用対効果をどのように説明するのか

AIコーディングエージェントは、単純に「一番賢いモデルを使えばよい」というものではありません。

簡単な修正であれば軽量なモデルで十分な場合もあります。一方で、既存コードベースをまたぐ修正や、IaCの変更などでは、上位モデルを使ったほうが結果的に安くなる可能性もあります。

このような判断を感覚ではなく、実際のタスクに対する **成功率・コスト・実行時間** で比較するためのツールとして、AWS Samplesにて `sample-agent-cost-bench` が公開されています。

本記事では、`agent-cost-bench` をAWS上の検証環境で試しながら、AIコーディングエージェントの導入判断にどのように活用できるかを整理します。

## 2. agent-cost-benchとは

`agent-cost-bench` は、AIコーディングエージェントの品質・コスト・レイテンシを比較するためのベンチマークフレームワークです。

主に以下の2つの比較モードがあります。

| モード | 比較対象 | 使いどころ |
| --- | --- | --- |
| `model-compare` | 同じCLI上で複数モデルを比較 | Kiro CLI上で複数モデルの費用対効果を比較する |
| `cli-compare` | 同じタスクを複数CLIで比較 | Kiro、Claude Code、GitHub Copilot、Codexなどを比較する |

今回は、まず試しやすい `model-compare` を利用し、Kiro CLI上で `claude-sonnet-5` と `claude-haiku-4.5` を比較しました。

## 3. 成功タスクあたりのコストを見る理由

AIコーディングエージェントの比較では、単純な1回あたりの実行コストだけを見ると判断を誤る可能性があります。

たとえば、1回あたりのコストが安いモデルでも、失敗率が高く、再実行や人手での修正が多ければ、実際のコストは高くなります。

逆に、1回あたりのコストが高いモデルでも、成功率が高く、手戻りが少ない場合は、結果的に安くなることがあります。

そのため、以下のような指標をセットで見ることが重要です。

| 指標 | 見るポイント |
| --- | --- |
| Pass Rate | タスクを正しく完了できた割合 |
| Cost / Run | 1回実行あたりのコスト |
| Cost per Success | 成功したタスクあたりのコスト |
| Latency | 実行時間 |
| 失敗パターン | どのタスクで失敗しやすいか |

特に重要なのは、`Cost per Success` です。

AIコーディングエージェントを実務に適用する場合、単に「安いモデル」ではなく、**成功まで含めて安いモデル**を選ぶ必要があります。

## 4. AWS上での検証手順

今回は、AWS上にEC2インスタンスを作成し、AWS Systems Manager Session Managerで接続して検証しました。

構成イメージは以下です。

```
ローカルPC
  |
  | AWS Systems Manager Session Manager
  v
EC2インスタンス
  |
  +-- Kiro CLI
  +-- agent-cost-bench
  +-- Python 3.11
  +-- Docker
  |
  v
results/
  +-- JSONレポート
  +-- HTMLレポート
  +-- ログ
```

検証環境は以下です。

| 項目 | 内容 |
| --- | --- |
| 実行環境 | Amazon EC2 |
| OS | Amazon Linux 2023 |
| 接続方法 | AWS Systems Manager Session Manager |
| 比較モード | `model-compare` |
| 利用CLI | Kiro CLI |
| Python | Python 3.11 |
| Docker | 利用 |

### EC2へSession Managerで接続する

EC2コンソールから対象インスタンスを選択し、以下の順で接続します。

```
EC2コンソール
  → インスタンス
  → 対象インスタンスを選択
  → 接続
  → Session Manager
  → 接続
```

Session Managerで接続すると、環境によっては `ssm-user` でログインします。

今回の環境では `ssm-user` で作業しました。

### 必要なパッケージをインストールする

Amazon Linux 2023では `apt-get` ではなく `dnf` を利用します。

また、環境によっては `curl` と `curl-minimal` が競合する場合があります。その場合は、`curl` をインストール対象から外して進めるとスムーズです。

```
sudo dnf clean all
sudo dnf makecache

sudo dnf install -y \
  git \
  wget \
  unzip \
  jq \
  gcc \
  gcc-c++ \
  make \
  python3.11 \
  python3.11-pip \
  python3.11-devel \
  docker
```

Dockerを起動します。

```
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```

Session Managerで接続している `ssm-user` がDockerを使えるようにします。

```
sudo usermod -aG docker ssm-user
```

グループ変更を反映するため、一度Session Managerを終了し、再接続します。

再接続後、以下を確認します。

```
whoami
id
groups
docker ps
```

`groups` に `docker` が含まれ、`docker ps` が `sudo` なしで成功すればOKです。

### Kiro CLIをインストールする

今回の検証では、Amazon Linux 2023上にKiro CLIのLinux版をインストールしました。

```
cd ~

curl --proto '=https' --tlsv1.2 -sSf \
  'https://desktop-release.q.us-east-1.amazonaws.com/latest/kirocli-x86_64-linux.zip' \
  -o 'kirocli.zip'

unzip kirocli.zip
./kirocli/install.sh
```

PATHを通します。

```
export PATH="$HOME/.local/bin:$HOME/kirocli/bin:$PATH"

echo 'export PATH="$HOME/.local/bin:$HOME/kirocli/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$HOME/kirocli/bin:$PATH"' >> ~/.profile
```

確認します。

```
command -v kiro-cli
kiro-cli --version
```

今回の環境では以下のバージョンでした。

### Kiro CLIにログインする

Session Managerのようなリモート環境では、EC2側でブラウザを直接開けないため、device flowでログインします。

```
kiro-cli login --use-device-flow
```

ログイン方法の選択画面が表示されたら、今回は `Use with Builder ID` を選択しました。

その後、URLが表示されるので、ブラウザで開いて画面の指示に従ってログインを実施します。  
ログインできたら、以下で確認します。

```
kiro-cli whoami
kiro-cli doctor
```

Session Manager上では、`kiro-cli doctor` で以下のようなターミナル統合に関するエラーが表示される場合があります。

```
Kiro CLI terminal integrations: kiro-cli-term is not running in this terminal
```

今回の検証では、`kiro-cli whoami` でログインできていることを確認できており、`agent-cost-bench` の非対話実行には影響しませんでした。

利用可能なモデルIDを確認します。

```
kiro-cli chat --list-models --format json | jq .
```

また、存在しないモデルIDを指定すると、利用可能なモデル一覧がエラーに表示されます。

```
kiro-cli chat --model invalid --no-interactive "hi"
```

今回利用したモデルは以下です。

```
claude-sonnet-5
claude-haiku-4.5
```

### agent-cost-benchをセットアップする

GitHubからリポジトリをクローンします。

```
cd ~

git clone https://github.com/aws-samples/sample-agent-cost-bench.git
cd sample-agent-cost-bench
```

Amazon Linux 2023の標準 `python3` は環境によってPython 3.9系の場合があります。`agent-cost-bench` はPython 3.10以上が必要なため、今回は `python3.11` を明示的に利用しました。

```
python3.11 -m venv .venv
source .venv/bin/activate

python --version
```

pipを更新し、`agent-cost-bench` をインストールします。

```
python -m pip install --upgrade pip
pip install -e .
```

確認します。

### 設定ファイルを作成する

まず、サンプル設定ファイルをコピーします。

```
cp config.model-compare.example.yaml config.model-compare.yaml
```

今回利用した4つのタスクは、`sample-agent-cost-bench` リポジトリに同梱されているサンプルタスクです。独自に作成したタスクではなく、`tasks/` 配下に用意されているタスクの中から、Python、FastAPI、Docker、Terraformといった異なる性質のタスクを選択しました。

| タスク | 内容 |
| --- | --- |
| `log-analyzer-cli` | アクセスログを解析してJSONに変換するCLIを作成するタスク |
| `rest-api` | TodoのCRUD REST APIを作成するタスク |
| `dockerize-flask` | 既存のFlaskアプリにDockerfileとdocker-composeを追加するタスク |
| `terraform-s3` | セキュアなS3バケットをTerraformで定義するタスク |

比較モデルには、品質・安定性を重視するモデルとして `claude-sonnet-5`、軽量・低コスト寄りのモデルとして `claude-haiku-4.5` を選択しました。`auto` も利用可能でしたが、内部で利用されるモデルが変わる可能性があるため、今回は比較結果を解釈しやすいように、明示的にモデルIDを指定しています。

今回は以下の設定で実行しました。

```
cat > config.model-compare.yaml <<'YAML'
kiro_cli_path: kiro-cli

effort: high

models:
  - claude-sonnet-5
  - claude-haiku-4.5

pricing:
  usd_per_credit: 0.04

tasks_dir: tasks

task_ids:
  - log-analyzer-cli
  - rest-api
  - dockerize-flask
  - terraform-s3

modes:
  - vibe

concurrency: per_target
timeout_minutes: 30
repeats: 3

functional_pass_threshold: 0.99

workspace_base: /tmp/agent-cost-bench-model-compare
output_dir: results
report_title: "agent-cost-bench trial on AWS"
open_report: false
YAML
```

この設定では、以下の実行数になります。

`agent-cost-bench` は実際にAIコーディングエージェントを実行するため、クレジットを消費します。最初は以下のように、タスク数や繰り返し回数を絞って動作確認するのがおすすめです。

```
task_ids:
  - log-analyzer-cli
  - rest-api

repeats: 1
```

なお、今回 `pricing.usd_per_credit` には `0.04` を設定しました。これは、Kiroのadd-on creditsやoverageの単価として示されている `$0.04/credit` をもとに、クレジット消費量をUSD換算するための前提値です。

ただし、月額プランに含まれるクレジットを利用している場合、各実行ごとに必ずこの金額が追加請求されるわけではありません。`agent-cost-bench` 上のUSD表示は、モデル間の比較をしやすくするための換算値として捉えるのがよいです。

価格やクレジット体系は変更される可能性があるため、実行時点のKiro Pricingページ、Billingページ、自身の契約プランを確認したうえで設定してください。

### validateしてから実行する

実行前に、設定ファイルを検証します。

```
agent-cost-bench model-compare validate config.model-compare.yaml
```

今回の検証では、以下のように表示されました。

問題がなければ、ベンチマークを実行します。

```
agent-cost-bench model-compare run config.model-compare.yaml
```

実行が完了すると、`results/` 配下にHTML、JSON、ログが出力されます。

今回の実行では、以下のファイルが出力されました。

```
20260714_141324_a08bb5.html
20260714_141324_a08bb5.json
20260714_141324_a08bb5.log
```

## 5. 検証結果

今回の実行条件は以下です。

| 項目 | 内容 |
| --- | --- |
| 実行環境 | Amazon EC2 / Amazon Linux 2023 |
| 接続方法 | AWS Systems Manager Session Manager |
| 比較モード | `model-compare` |
| 利用CLI | Kiro CLI |
| 比較モデル | `claude-sonnet-5` / `claude-haiku-4.5` |
| タスク | `log-analyzer-cli` / `rest-api` / `dockerize-flask` / `terraform-s3` |
| 繰り返し回数 | 3回 |
| 実行数 | 4タスク × 2モデル × 3回 = 24実行 |

モデル別の結果は以下です。

| モデル | Pass Rate | Avg Cost / Run | Cost / Success | Avg Credits / Run | Avg Latency | Runs |
| --- | --- | --- | --- | --- | --- | --- |
| `claude-sonnet-5` | 100% | $0.0233 | $0.0233 | 0.582 | 26.3s | 12/12 |
| `claude-haiku-4.5` | 100% | $0.0070 | $0.0070 | 0.175 | 18.7s | 12/12 |

全体結果は以下です。

| 指標 | 結果 |
| --- | --- |
| Pass Rate | 100% |
| 成功数 | 24/24 |
| Total Cost | $0.3632 |
| Total Credits | 9.080 |
| Total Time | 669.7s |

今回の検証では、4種類のタスクを対象に、2つのモデルをそれぞれ3回ずつ実行しました。

結果として、`claude-sonnet-5` と `claude-haiku-4.5` はいずれも全タスクでPASSしました。そのため、今回のタスク群に限れば、品質面では両モデルとも十分な結果でした。

一方で、コストには明確な差が出ました。`claude-haiku-4.5` の平均実行コストは `$0.0070`、`claude-sonnet-5` は `$0.0233` であり、今回の条件では `claude-haiku-4.5` のほうが約70%低コストでした。

また、平均レイテンシも `claude-haiku-4.5` が18.7秒、`claude-sonnet-5` が26.3秒であり、今回のような比較的シンプルなタスクでは、軽量モデルでも十分に成功するケースがあることが確認できました。

ただし、これはあくまで今回選択した4タスクでの結果です。より複雑な既存コード改修、複数ファイルをまたぐリファクタリング、設計判断を伴うタスクでは、上位モデルのほうが安定する可能性があります。

そのため、実務で利用する際は、対象とする開発タスクに近いベンチマークを用意し、タスク種別ごとにモデルを使い分けることが重要だと感じました。

## 6. S3に出力したレポートの活用

Session Managerで接続している場合、EC2上のHTMLレポートをそのままブラウザで開くのは少し手間です。

そのため、今回は結果ファイルをS3にアップロードし、ローカルPCで確認する形にしました。

```
aws s3 cp results/ s3://<your-bucket>/agent-cost-bench/ --recursive --sse AES256
```

S3にアップロードした結果は、以下のように活用できます。

| 活用方法 | 内容 |
| --- | --- |
| HTMLレポートの確認 | S3からHTMLをダウンロードし、ローカルブラウザで確認する |
| 検証証跡の保存 | 実行時点のJSON、HTML、ログをまとめて保管する |
| 結果の共有 | 限定されたメンバーにS3経由で共有する |
| 再分析 | JSONを使って後から集計・比較する |
| ブログ用の素材 | サマリー表やグラフを確認し、必要な情報だけ抜粋する |

S3上のファイルを確認する場合は、以下を実行します。

```
aws s3 ls s3://<your-bucket>/agent-cost-bench/
```

HTMLレポートをローカルにダウンロードする場合は、以下です。

```
aws s3 cp s3://<your-bucket>/agent-cost-bench/20260714_141324_a08bb5.html .
```

JSONやログもあわせてダウンロードできます。

```
aws s3 cp s3://<your-bucket>/agent-cost-bench/20260714_141324_a08bb5.json .
aws s3 cp s3://<your-bucket>/agent-cost-bench/20260714_141324_a08bb5.log .
```

今回出力されたHTMLレポートでは、実行全体のサマリー、モデル別の比較、グラフ、詳細な実行結果を確認できます。

以下は、最終的に実行した24回分のHTMLレポートのサマリーです。

サマリー画面では、Total Runs、Passed、Total Credits、Total Costなどを一覧で確認できます。今回の検証では、24回の実行すべてがPASSし、Total Costは `$0.3632` でした。

また、Chartsでは、モデルごとのPass Rate、Final Score、平均クレジット消費量、平均コストを確認できます。

![](https://static.zenn.studio/user-upload/cdb485559d56-20260716.png)

今回の結果では、Pass RateとFinal Scoreはいずれのモデルも100%でした。一方で、平均クレジット消費量と平均コストは `claude-haiku-4.5` のほうが低く、同じタスクであってもモデルによってコスト差が出ることを視覚的に確認できます。

## 7. 活用ポイント

`agent-cost-bench` は、単に「どのモデルが安いか」を見るためだけのツールではありません。

AIコーディングエージェントをチームや案件で活用する際に、次のような判断材料として使えます。

| 活用ポイント | 内容 |
| --- | --- |
| ツール選定 | Kiro、Claude Code、GitHub Copilot、Codexなどの比較 |
| モデル選定 | 同じCLI内で、軽量モデル・中位モデル・上位モデルを比較 |
| タスク分類 | どのタスクでどのモデルを使うべきかを整理 |
| コスト説明 | 1回あたりではなく、成功タスクあたりのコストで説明 |
| 標準化 | 推奨CLI、推奨モデル、レビュー基準の整理 |

特に重要なのは、タスクの難易度に応じてモデルを使い分けることです。

| タスク | 方針 |
| --- | --- |
| 単純なコード生成 | 軽量モデルから試す |
| テスト作成 | 軽量〜中位モデルで十分か確認 |
| 既存コード修正 | 中位モデル以上を検討 |
| 複数ファイル変更 | 中位〜上位モデルを検討 |
| セキュリティ・IaC | 成功率を重視 |
| 本番影響が大きい変更 | コストより品質を重視 |

今回の検証では、比較的シンプルなタスクにおいて `claude-haiku-4.5` でも十分な結果が得られました。

一方で、より複雑なタスクでは、上位モデルを使ったほうが成功率や手戻り削減の観点で有利になる可能性があります。

`agent-cost-bench` を使うことで、この使い分けを実測値に基づいて検討できます。

また、今回は `model-compare` を中心に扱いましたが、次のステップとして `cli-compare` も有効です。

`cli-compare` では、同じタスクを複数のAIコーディングエージェントCLIで実行し、ツールごとの差を比較できます。

| 比較軸 | 例 |
| --- | --- |
| Kiro vs Claude Code | ターミナル型エージェントの比較 |
| Kiro vs GitHub Copilot | 既存のGitHub開発フローとの相性確認 |
| Claude Code vs Codex | 同じタスクに対するCLIごとの違い |
| 複数CLI横断 | 開発標準ツール候補の比較 |

モデル比較だけでなく、CLIごとの使い勝手や成功率、コストを比較できる点は、導入判断に役立ちます。

## 8. 注意点

`agent-cost-bench` を使う際は、いくつか注意点があります。

### 価格設定は必ず確認する

今回の設定では、以下のように `usd_per_credit` を指定しました。

```
pricing:
  usd_per_credit: 0.04
```

ただし、価格やクレジットの前提は、利用プランや時期によって変わる可能性があります。

### 顧客コードや機密情報をそのまま使わない

実リポジトリに近いタスクで評価することは有効ですが、コードやデータの取り扱いには注意が必要です。

最初は以下のような方法が安全です。

* サンプル化したコードを使う
* 機密情報を除去した検証用リポジトリを作る
* 接続情報やシークレットを含めない
* 検証用AWSアカウントを分離する
* レポートの共有範囲を制限する

### 1回の結果で判断しない

LLMは同じプロンプトでも毎回同じ結果になるとは限りません。

今回は各タスク・各モデルを3回ずつ実行しましたが、より厳密に評価する場合は、タスク数や繰り返し回数を増やし、平均値だけでなくばらつきも確認するのがよいです。

### 検証条件を記録する

後から結果を比較できるように、以下の情報は残しておくべきです。

| 記録項目 | 理由 |
| --- | --- |
| 実行日 | 価格やモデルの変更に備える |
| CLIバージョン | ツール側の挙動差分を追えるようにする |
| モデルID | 再現性を確保する |
| pricing設定 | USD換算の前提を明確にする |
| タスクID | どのタスクで測ったかを明確にする |
| repeats | 何回実行した結果かを明確にする |
| 実行ログ | 後から詳細を確認できるようにする |

## 9. まとめ

`agent-cost-bench` は、AIコーディングエージェントの選定を感覚ではなく、実測値で判断するための有用なツールです。

今回の検証では、Amazon Linux 2023のEC2インスタンスにSession Managerで接続し、Kiro CLIと `agent-cost-bench` をセットアップして、`claude-sonnet-5` と `claude-haiku-4.5` を比較しました。

4タスク × 2モデル × 3回の合計24実行では、両モデルともすべてPASSしました。一方で、`claude-haiku-4.5` のほうが平均コスト・平均レイテンシともに低く、今回のタスク群では軽量モデルでも十分な結果が得られることが確認できました。

特に、以下の点で活用価値があると感じました。

* モデル・ツール選定を成功率とコストで比較できる
* 1回あたりのコストではなく、成功タスクあたりのコストを確認できる
* タスク種別ごとのモデル使い分けを検討できる
* AIコーディングエージェントの標準化に向けた判断材料になる
* PoCから本格展開に進むための説明材料として使える

AIコーディングエージェントを導入する際に重要なのは、「どのツールが一番すごいか」ではなく、**自分たちの開発タスクに対して、どのツール・モデルが最も費用対効果よく成果を出せるか**です。

`agent-cost-bench` は、そのような判断を行うためのよいベンチマーク基盤になると感じました。
