---
id: "2026-07-21-aiコーディングエージェントcliを実測で比較するagent-cost-benchをaws上で試すc-01"
title: "AIコーディングエージェントCLIを実測で比較する：agent-cost-benchをAWS上で試す(cli-compare)"
url: "https://zenn.dev/nttdata_tech/articles/6f9f7b64baef6a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

前回の記事では、AWS（Amazon Web Services） Samplesで公開されている `sample-agent-cost-bench` を使い、Kiro CLI上で複数モデルを比較しました。

<https://zenn.dev/nttdata_tech/articles/130bd43f48e425>

前回利用したのは `model-compare` です。これは、同じCLI上で複数のモデルを比較し、成功率・コスト・実行時間を確認するためのモードです。

今回はその続きとして、`agent-cost-bench` のもう1つの比較モードである `cli-compare` を試します。

`cli-compare` では、同じタスクを複数のAIコーディングエージェントCLIで実行し、CLIごとの成功率・コスト・実行時間を比較できます。

今回比較したのは以下の2つです。

| CLI | 概要 |
| --- | --- |
| Kiro CLI | Kiroで利用するAIコーディングエージェントCLI |
| Claude Code | Claude CodeのCLI |

## 2. cli-compareとは

`agent-cost-bench` には、大きく2つの比較モードがあります。

| モード | 比較対象 | 使いどころ |
| --- | --- | --- |
| `model-compare` | 同じCLI上で複数モデルを比較 | Kiro CLI上で複数モデルの費用対効果を比較する |
| `cli-compare` | 同じタスクを複数CLIで比較 | Kiro、Claude Code、GitHub Copilot、Codexなどを比較する |

前回の `model-compare` は、同じKiro CLIの中で `claude-sonnet-5` と `claude-haiku-4.5` を比較しました。

一方で、今回の `cli-compare` は、同じタスクを Kiro CLI と Claude Code の両方で実行し、CLIごとの差を確認します。

ここで重要なのは、**同じモデルを指定しても、完全に同じ条件にはならない**という点です。

CLIごとに以下のような差があります。

* システムプロンプト
* ファイル編集の方法
* ツール実行の方法
* コンテキスト管理
* 実行ログの形式

そのため、`cli-compare` の結果は「モデル単体の性能差」ではなく、**CLIを含めた実行系全体の結果**として解釈する必要があります。

## 3. 今回の比較方針

今回は、以下の方針で検証しました。

| 観点 | 方針 |
| --- | --- |
| 比較対象 | Kiro CLI / Claude Code |
| タスク | 前回と同じ同梱タスクを利用 |
| モデル | Sonnet 5 / Haiku 4.5 の2パターン |
| 評価軸 | Pass Rate / Cost / Credits / Latency |
| 実行環境 | Amazon EC2（Amazon Linux 2023） |

まず、`claude-sonnet-5` を使って Kiro CLI と Claude Code を比較しました。  
その後、`claude-haiku-4.5` でも比較しました。  
ただし、Kiro CLIとClaude CodeではモデルIDの指定方法が異なりました。

Kiro CLIでは以下のように指定できました。

一方、Claude Codeで同じ `claude-haiku-4.5` を指定すると、以下のようなエラーになりました。

```
The provided model identifier is invalid.
```

そのため、Claude Code側ではAmazon BedrockのHaiku 4.5モデルIDを環境変数でpinし、`--model haiku` として実行しました。

```
export ANTHROPIC_DEFAULT_HAIKU_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'
```

このように、`cli-compare` ではCLIごとのモデル指定方法の違いにも注意が必要です。

## 4. AWS上での検証手順

前回と同じく、Amazon EC2上に検証環境を作成し、AWS Systems Manager Session Managerで接続して実行しました。

構成イメージは以下です。

```
ローカルPC
  |
  | AWS Systems Manager Session Manager
  v
EC2インスタンス
  |
  +-- Kiro CLI
  +-- Claude Code
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
| 比較モード | `cli-compare` |
| 比較CLI | Kiro CLI / Claude Code |
| Python | Python 3.11 |
| Docker | 利用 |

### 前提

前回の記事で、以下はセットアップ済みの前提です。

* Amazon Linux 2023のEC2
* Session Managerでの接続
* Docker
* Python 3.11
* Kiro CLI
* `sample-agent-cost-bench`

今回は追加で、Claude Codeをセットアップしました。

### Claude Codeをインストールする

Claude Codeをインストールします。

```
cd ~

curl -fsSL https://claude.ai/install.sh | bash

export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile

claude --version
```

### Claude CodeでAmazon Bedrockを利用する

Claude Codeを起動します。

対話画面の案内に従い、Amazon Bedrockを利用する設定を行います。今回の環境では、Claude Code on Amazon Bedrockとして設定し、利用可能なモデルをpinしました。  
設定後、通常のシェルに戻り、Claude Codeが非対話で利用できることを確認します。

```
claude -p "Say hello" \
  --output-format json \
  --model claude-sonnet-5 \
  --dangerously-skip-permissions \
  --effort high
```

JSON出力に以下のような情報が含まれていればOKです。

```
{
  "type": "result",
  "subtype": "success",
  "model": "claude-sonnet-5",
  "total_cost_usd": 0.0497
}
```

`total_cost_usd` が出力されるため、`agent-cost-bench` 側ではClaude Codeのコストをこの値から取得できます。

### Kiro CLIの状態を確認する

前回セットアップ済みですが、念のためKiro CLIのログイン状態も確認します。

```
export PATH="$HOME/.local/bin:$HOME/kirocli/bin:$PATH"

kiro-cli whoami
kiro-cli chat --model claude-sonnet-5 --no-interactive "Say hello"
```

### Sonnet 5用のcli-compare設定を作成する

`sample-agent-cost-bench` のディレクトリに移動します。

```
cd ~/sample-agent-cost-bench
source .venv/bin/activate
```

`config.cli-compare.yaml` を作成します。

```
cat > config.cli-compare.yaml <<'YAML'
comparison_label: "Kiro CLI vs Claude Code with Claude Sonnet 5"

runners:
  - name: kiro
    display_name: "Kiro CLI (claude-sonnet-5)"
    cli_path: kiro-cli
    model_id: claude-sonnet-5
    pricing:
      usd_per_credit: 0.04
    cli_base_args:
      - chat
      - --no-interactive
      - --trust-all-tools
      - "--model={model}"
      - "--effort={effort}"

  - name: claude-code
    display_name: "Claude Code (claude-sonnet-5)"
    cli_path: claude
    model_id: claude-sonnet-5
    cli_base_args:
      - "-p"
      - "{prompt}"
      - "--output-format"
      - "json"
      - "--model"
      - "{model}"
      - "--dangerously-skip-permissions"
      - "--effort"
      - "{effort}"

tasks_dir: tasks

task_ids:
  - log-analyzer-cli
  - rest-api
  - dockerize-flask
  - terraform-s3

modes:
  - vibe

concurrency: 1
timeout_minutes: 45
repeats: 3

functional_pass_threshold: 0.99

workspace_base: /home/ssm-user/agent-cost-bench-workspaces/cli-compare
output_dir: results
report_title: "agent-cost-bench cli-compare on AWS"
open_report: false
YAML
```

今回利用した4つのタスクは、`sample-agent-cost-bench` リポジトリに同梱されているサンプルタスクです。

| タスク | 内容 |
| --- | --- |
| `log-analyzer-cli` | アクセスログを解析してJSONに変換するCLIを作成するタスク |
| `rest-api` | TodoのCRUD REST APIを作成するタスク |
| `dockerize-flask` | 既存のFlaskアプリにDockerfileとdocker-composeを追加するタスク |
| `terraform-s3` | セキュアなS3バケットをTerraformで定義するタスク |

この設定では、以下の実行数になります。

### Haiku 4.5用のcli-compare設定を作成する

次に、Haiku 4.5相当のモデルでも比較します。

Kiro CLI側は `claude-haiku-4.5` を指定します。

Claude Code側は、Amazon BedrockのHaiku 4.5モデルIDを `ANTHROPIC_DEFAULT_HAIKU_MODEL` でpinし、`--model haiku` として実行します。

```
export ANTHROPIC_DEFAULT_HAIKU_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'
echo "export ANTHROPIC_DEFAULT_HAIKU_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'" >> ~/.bashrc
```

Claude Code側で `haiku` が使えることを確認します。

```
claude -p "Say hello" \
  --output-format json \
  --model haiku \
  --dangerously-skip-permissions \
  --effort high
```

その後、Haiku 4.5用の設定ファイルを作成します。

```
cat > config.cli-compare-haiku.yaml <<'YAML'
comparison_label: "Kiro CLI vs Claude Code with Claude Haiku 4.5"

runners:
  - name: kiro
    display_name: "Kiro CLI (claude-haiku-4.5)"
    cli_path: kiro-cli
    model_id: claude-haiku-4.5
    pricing:
      usd_per_credit: 0.04
    cli_base_args:
      - chat
      - --no-interactive
      - --trust-all-tools
      - "--model={model}"
      - "--effort={effort}"

  - name: claude-code
    display_name: "Claude Code (haiku -> Bedrock Haiku 4.5)"
    cli_path: claude
    model_id: haiku
    cli_base_args:
      - "-p"
      - "{prompt}"
      - "--output-format"
      - "json"
      - "--model"
      - "{model}"
      - "--dangerously-skip-permissions"
      - "--effort"
      - "{effort}"

tasks_dir: tasks

task_ids:
  - log-analyzer-cli
  - rest-api
  - dockerize-flask
  - terraform-s3

modes:
  - vibe

concurrency: 1
timeout_minutes: 45
repeats: 3

functional_pass_threshold: 0.99

workspace_base: /home/ssm-user/agent-cost-bench-workspaces/cli-compare-haiku
output_dir: results
report_title: "agent-cost-bench cli-compare Haiku 4.5 on AWS"
open_report: false
YAML
```

### validateしてから実行する

まず設定ファイルを検証します。

```
agent-cost-bench cli-compare validate config.cli-compare.yaml
agent-cost-bench cli-compare validate config.cli-compare-haiku.yaml
```

問題がなければ実行します。

```
AGENT_COST_BENCH_VERIFY_NETWORK=bridge \
TMPDIR="$HOME/tmp/agent-cost-bench" \
agent-cost-bench cli-compare run config.cli-compare.yaml
```

Haiku 4.5側も実行します。

```
AGENT_COST_BENCH_VERIFY_NETWORK=bridge \
TMPDIR="$HOME/tmp/agent-cost-bench" \
agent-cost-bench cli-compare run config.cli-compare-haiku.yaml
```

## 5. 実行時に発生したエラーと対処

最初に4タスク × 2 CLI × 3回で実行した際、後半のタスクで以下のエラーが発生しました。

```
Could not create an isolated environment for verification — harness error, not a model failure
```

これは、モデルやCLIの生成結果の失敗ではなく、検証用の隔離環境を作成できなかったことを示しています。

確認したところ、`/tmp` がtmpfsとして割り当てられており、過去の `agent-cost-bench` ワークスペースによって100%使用されていました。

```
/tmp/agent-cost-bench-cli-compare
/tmp/agent-cost-bench-model-compare
```

そのため、以下の対応を行いました。

```
rm -rf /tmp/agent-cost-bench-cli-compare
rm -rf /tmp/agent-cost-bench-model-compare

mkdir -p ~/tmp/agent-cost-bench
mkdir -p ~/agent-cost-bench-workspaces/cli-compare

export TMPDIR="$HOME/tmp/agent-cost-bench"
```

また、設定ファイルでは以下のように `workspace_base` を `/home/ssm-user` 配下に変更しました。

```
workspace_base: /home/ssm-user/agent-cost-bench-workspaces/cli-compare
```

さらに、安定性を優先して `concurrency: 1` にしました。

この対応後に再実行したところ、24実行すべてがPASSしました。

今回のように、`cli-compare` ではタスク数、CLI数、繰り返し回数が増えるほど、一時ファイルや検証用ワークスペースの使用量が増えます。

Session Manager経由の検証環境では、`/tmp` の容量に注意したほうがよいと感じました。

## 6. 検証結果

### Sonnet 5での比較

まず、`claude-sonnet-5` を使って Kiro CLI と Claude Code を比較しました。

| CLI | Pass Rate | Avg Cost / Run | Cost / Success | Avg Credits / Run | Avg Latency | Runs |
| --- | --- | --- | --- | --- | --- | --- |
| Kiro CLI | 100% | $0.0234 | $0.0234 | 0.586 | 25.1s | 12/12 |
| Claude Code | 100% | $0.1289 | $0.1289 | - | 22.2s | 12/12 |

全体結果は以下です。

| 指標 | 結果 |
| --- | --- |
| Pass Rate | 100% |
| 成功数 | 24/24 |
| Total Cost | $1.8275 |
| Total Credits | 7.030 |
| Total Time | 1082.2s |

今回のSonnet 5での比較では、Kiro CLIとClaude Codeのどちらも24実行すべてでPASSしました。

一方で、平均コストと平均レイテンシには差が出ました。

Kiro CLIは平均コストが `$0.0234`、平均レイテンシが25.1秒でした。Claude Codeは平均コストが `$0.1289`、平均レイテンシが22.2秒でした。

今回の条件では、Kiro CLIのほうがベンチマーク上の換算コストは低く、Claude Codeのほうが平均レイテンシは短い結果になりました。

### Haiku 4.5での比較

次に、Haiku 4.5相当のモデルでも比較しました。

| CLI | Pass Rate | Avg Cost / Run | Cost / Success | Avg Credits / Run | Avg Latency | Runs |
| --- | --- | --- | --- | --- | --- | --- |
| Kiro CLI | 100% | $0.0068 | $0.0068 | 0.170 | 17.2s | 12/12 |
| Claude Code | 100% | $0.0420 | $0.0420 | - | 19.1s | 12/12 |

全体結果は以下です。

| 指標 | 結果 |
| --- | --- |
| Pass Rate | 100% |
| 成功数 | 24/24 |
| Total Cost | $0.5854 |
| Total Credits | 2.050 |
| Total Time | 960.6s |

Haiku 4.5相当の比較でも、Kiro CLIとClaude Codeのどちらも24実行すべてでPASSしました。

平均コストは、Kiro CLIが `$0.0068`、Claude Codeが `$0.0420` でした。平均レイテンシは、Kiro CLIが17.2秒、Claude Codeが19.1秒でした。

今回の条件では、Haiku 4.5相当のモデルを使った場合、Kiro CLIのほうがベンチマーク上の換算コストと平均レイテンシの両方で低い結果になりました。

### Sonnet 5とHaiku 4.5の比較結果を並べて見る

今回の結果を並べると、以下のようになります。

| モデル | CLI | Pass Rate | Avg Cost / Run | Cost / Success | Avg Credits / Run | Avg Latency | Runs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sonnet 5 | Kiro CLI | 100% | $0.0234 | $0.0234 | 0.586 | 25.1s | 12/12 |
| Sonnet 5 | Claude Code | 100% | $0.1289 | $0.1289 | - | 22.2s | 12/12 |
| Haiku 4.5 | Kiro CLI | 100% | $0.0068 | $0.0068 | 0.170 | 17.2s | 12/12 |
| Haiku 4.5 | Claude Code | 100% | $0.0420 | $0.0420 | - | 19.1s | 12/12 |

今回の4タスクでは、どの組み合わせでもPass Rateは100%でした。

つまり、今回のタスク群に限れば、CLIやモデルの違いによる成功率の差は出ませんでした。

一方で、コストとレイテンシには差が出ています。

ただし、ここでのコスト比較には注意が必要です。Kiro CLIはクレジット消費量を `usd_per_credit: 0.04` でUSD換算しています。一方、Claude CodeはJSON出力に含まれる `total_cost_usd` を利用しています。

つまり、両者のコストは完全に同一の課金体系で正規化されたものではなく、**agent-cost-bench上で比較しやすいように表示された換算値**として捉えるのがよさそうです。

## 7. S3に出力したレポートの活用

HTMLレポートを以下に示します。

### Sonnet 5での比較

![](https://static.zenn.studio/user-upload/99e2353705ec-20260717.png)

### Haiku 4.5での比較

![](https://static.zenn.studio/user-upload/67ba5206b6b3-20260717.png)

## 8. 活用ポイント

今回の4タスクでは、Sonnet 5でもHaiku 4.5でも、Kiro CLIとClaude CodeはいずれもPass Rate 100%でした。この場合、成功率だけを見ると差はありません。一方で、コストやレイテンシを見ると差が出ています。

そのため、AIコーディングエージェントの評価では、成功率だけでなく、以下をあわせて見る必要があります。

| 指標 | 見るポイント |
| --- | --- |
| Pass Rate | タスクを正しく完了できた割合 |
| Cost / Run | 1回実行あたりのコスト |
| Cost / Success | 成功タスクあたりのコスト |
| Latency | 実行時間 |
| Detailed Results | どのタスクで失敗・成功したか |

つまり、`cli-compare` は、AIコーディングエージェントCLIを選ぶ際の判断材料になります。

| 活用ポイント | 内容 |
| --- | --- |
| 標準CLIの検討 | Kiro、Claude Code、Copilot、Codexなどの候補を比較する |
| タスクとの相性確認 | 自分たちの開発タスクでどのCLIが安定するか確認する |
| コスト説明 | 成功タスクあたりのコストを示す |
| 開発者体験の確認 | レイテンシやログの見やすさを確認する |

ただし、今回のような同梱タスクだけで判断するのではなく、実際に活用したい開発タスクに近いベンチマークを用意することが重要です。

`agent-cost-bench` は、単に「どのCLIがよいか」を決めるためだけでなく、**自分たちの開発タスクに対して、どのCLI・モデル・設定が合うかを測るための基盤**として使えると感じました。

## 9. 注意点

最後に、今回の検証で感じた注意点を整理します。

### 結果をCLIの優劣として単純化しない

今回の結果では、特定の条件でコストやレイテンシに差が出ました。

ただし、これは各CLIの総合的な優劣を示すものではありません。

タスク、モデル、CLI設定、実行環境、認証方式、リージョン、契約プランによって結果は変わります。

そのため、結果はあくまで **今回の条件における実測値** として扱う必要があります。

### 最初は小さく始める

`cli-compare` は、CLI数 × タスク数 × 繰り返し回数で実行数が増えます。

今回のように、4タスク × 2 CLI × 3回であれば24実行です。

CLIを4種類に増やすと、同じ条件でも48実行になります。

最初は以下のように小さく始めるのがおすすめです。

```
task_ids:
  - log-analyzer-cli
  - rest-api

repeats: 1
```

## 10. まとめ

本記事では、前回の `model-compare` に続き、`agent-cost-bench` の `cli-compare` をAWS上で試しました。

今回は、Kiro CLIとClaude Codeを対象に、Sonnet 5とHaiku 4.5相当のモデルで比較しました。

4タスク × 2 CLI × 3回の検証では、Sonnet 5、Haiku 4.5相当のどちらでも、Kiro CLIとClaude CodeはすべてのタスクでPASSしました。一方で、平均コストや平均レイテンシには差が出ました。

ただし、本記事の結果は、今回選択したタスク、モデル、設定、実行環境におけるものです。各ツールの総合的な良し悪しを示すものではありません。

今回の検証を通じて、`cli-compare` は以下のような用途で有用だと感じました。

* 同じタスクを複数CLIで実行して比較できる
* 成功率だけでなく、成功タスクあたりのコストを確認できる
* CLIごとのレイテンシ差を確認できる
* 導入前に、自分たちのタスクに近い形で検証できる

AIコーディングエージェントの導入では、「どのモデルを使うか」だけでなく、「どのCLIを通じて使うか」も重要です。

`agent-cost-bench` の `cli-compare` は、その判断を感覚ではなく実測値で進めるための有用なツールだと感じました。
