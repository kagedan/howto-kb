---
id: "2026-05-12-claude-code-がいま何してたどう詰まったを観測したい-otel-をローカル分析-01"
title: "Claude Code が「いま何してた？どう詰まった？」を観測したい！ ── OTEL をローカル分析"
url: "https://qiita.com/wasssse/items/aa1b040caf0dc46e2562"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "Python"]
date_published: "2026-05-12"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

# 背景
ご無沙汰しております。かわせです！
最近はClaudeCode, kiro-cli, GithubCopilotCLI などなどを活用して業務/趣味で開発してます！


AI Agentによって我々の役割は大きく変わりつつあるいま、皆さんは Agent定義らのカスタマイズをどのように行っているでしょうか？

私はこれまで「よっしゃ！良い感じの定義が出来た！**これこそが俺の最強のAgent定義**(Rules/Hook/ハーネスエンジニアリングetc.. )**だ！！**」とか自分を褒めながら雰囲気で改善していました。

**...が、それって本当に「最強」で「さっきまでより良く」なっているんですかね？**

ということで今回は、 **ClaudeCodeの挙動をOTELを使って「外部サービス無し」「重たいリソース起動無し」「自分だけが見られる」「手軽に試せる」ようにして観測していきたい**と思います！！

# ざっくりまとめ

## 今回の記事でやったこと

以下の画像のような「ClaudeCodeがさっきのセッションでどう動いていて、何で詰まったのか！？」を**自然言語**で、**自分以外の誰にも見せずに分析**します！

<details><summary>（折り畳み）成果例 </summary>

▽ 自然言語で分析できる！
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3629247/fd027b61-e4b1-4eea-befe-273f41d5dab0.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3629247/cde757bf-47a4-4ffe-8881-b70d8d3c70bf.png)

▽ 分析もできればレポートも作れる！
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3629247/24b8d4d7-8934-45a1-bedc-9fa00a23c1ac.png)


</details>




## 今回構築したのは、「ローカルOTEL観測構成」です！

以下の3ステップでやりました！

1. `otelcol-contrib` をローカルでプロセス起動し、`~/.claude/otel/` に JSONL を1セッション1ファイルで追記しながら貯める
2. その JSONL を読む分析 Skill を書く
3. `claude` を実行してセッションを終えたあとに「さっきのセッション分析して」などと聞くと、**Claudeによる分析結果や、SVG 画像入りのHTMLレポート**が返ってくる

Grafana も Langfuse も不要で、WSL2 の閉域環境でも動きます！

以下、順にやっていきます。

:::note info
今回のポイントは、**「ClaudeCodeの挙動ログ（OTEL）をローカルに出力すること」です！**
これさえできれば、あとは賢いClaudeさんに分析を依頼します。

ただし、今回対象とする挙動ログ（OTEL）では、**実際に入力したプロンプトや回答そのものは記録されません**。
これを紐づけるネタは次回以降でご紹介できればと思います！
:::


:::note warn
**そもそもOTELとは！？**
素晴らしいブログが既に多数存在するので、そもそもOTEL（OpenTelemetry）とは？！はこの記事では**詳しく記載しません**。
AI Agent の文脈ではざっくり、「AI Agent の利用状況・コスト・LLM呼び出し・ツール実行を外部監視基盤へ出すための標準テレメトリ」と私は理解しています！

技術ブログ以外にも、 Claude 公式の説明などおすすめです！
https://code.claude.com/docs/ja/monitoring-usage

:::



## セットアップ（2ステップ）

まずは今回のセットアップ手順からいきます！
私の環境は WSL2 (Ubuntu 24.04) ですが、ほぼ環境に依存しない手順です。

## ① otelcol-contrib を取得

実行ディレクトリはどこでも問題ないです。
（私は普段の作業ディレクトリで、ClaudeCodeに教えてもらってそのままやりました・・）

```bash
curl -LO https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.121.0/otelcol-contrib_0.121.0_linux_amd64.tar.gz
tar xzf otelcol-contrib_0.121.0_linux_amd64.tar.gz
mkdir -p ~/work/claude/otel
mv otelcol-contrib ~/work/claude/otel/
```

## ② `~/.bashrc` に `claude()` 関数を追加

```bash
export PATH="$HOME/work/claude/otel:$PATH"

claude() {
  local name
  name="$(basename "$(pwd -P)")_$(date +%Y%m%d_%H%M%S)"
  local otel_dir="$HOME/.claude/otel"
  local otel_config="/tmp/claude-otel-config-$$.yaml"

  mkdir -p "$otel_dir"

  # 前回の Collector が残っていたら停止（保険として・・）
  local existing_pid
  existing_pid=$(lsof -t -i :14317 2>/dev/null)
  [ -n "$existing_pid" ] && kill "$existing_pid" 2>/dev/null && sleep 1

  # YAML 設定を毎回動的生成（パスがセッション毎に変わるので、静的ファイルにはしない）
  cat > "$otel_config" <<EOF
receivers:
  otlp:
    protocols:
      http:
        endpoint: 127.0.0.1:14317

exporters:
  file:
    path: ${otel_dir}/${name}.jsonl
    format: json

service:
  telemetry:
    metrics:
      level: none
  pipelines:
    traces:  { receivers: [otlp], exporters: [file] }
    metrics: { receivers: [otlp], exporters: [file] }
    logs:    { receivers: [otlp], exporters: [file] }
EOF

  otelcol-contrib --config "$otel_config" &
  local otel_pid=$!
  sleep 1

  # どの終了経路でも Collector を止めて config を消す
  trap 'kill "$otel_pid" 2>/dev/null; wait "$otel_pid" 2>/dev/null; rm -f "$otel_config"; trap - INT TERM EXIT' INT TERM EXIT

  CLAUDE_CODE_ENABLE_TELEMETRY=1 \
  CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1 \
  OTEL_METRICS_EXPORTER=otlp \
  OTEL_LOGS_EXPORTER=otlp \
  OTEL_TRACES_EXPORTER=otlp \
  OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
  OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:14317 \
  OTEL_METRIC_EXPORT_INTERVAL=10000 \
  OTEL_LOG_TOOL_DETAILS=1 \
    command claude "$@" # 環境変数をつけて、引数をそのまま渡してClaudeCodeを起動

  echo "OTEL output: ${otel_dir}/${name}.jsonl" # 終わったらすぐ確認したいことがあるのでパスを出力しておく
}
```

> **社内プロキシを使っている方へ**: プロキシが `127.0.0.1` への通信をブロックしていると Collector にデータが届きません。`NO_PROXY=127.0.0.1` を追加してください。

これで `claude` コマンドを実行するたびに、 `~/.claude/otel/` にその日の日時パスファイル名で JSONL が1本できます。

:::note warn
後ろでも少し触れていますが、今時点の設定は 「1セッションで1回実行する」扱いなので、5月中旬にClaudeCodeで発表された「agent view」を使われるような多数セッション同時並行ユーザの方には向いておりません・・・
:::


---

# 実装・設定の詳細（読み飛ばしても OK！ ）

## 今回やっつけた3つのハードル

Grafana や Langfuse に OTEL を流す方法はすでにブログ記事がいくつかあります。
が、以下の3点にどれか1つでも当てはまる方、いらっしゃいませんか・・？！

<dl>
  <dt>① :sob: ：PC環境内（や自由に使える環境内）にLangfuseやGrafanaを起動するまでの余裕が無い </dt>
  <dd>（所感）EC2などで作業しないと、ローカルでGrafanaらを全部起動することも可能！な環境ってなかなか無いですよねえ。。。</dd>
  <dt>② :spy_tone2:：AWSアカウントなど、他チームメンバから見えるところで試行錯誤したくない/できない</dt>
  <dd>（所感）AWSのCloudWatch側にOTELを連携することもできるので、AWS側でダッシュボード化/ログ分析するのも手です！が、認証情報の管理や課金されてもOKな自由にできるアカウントがあるか？という問題があったりしますよね・・・</dd>
  <dt>③ :sleeping:：GrafanaやLangfuseのリッチなUIから、グラフ読み取りを自分でしたくない！できない！</dt>
  <dd>（所感）私はGrafanaとかでカスタムダッシュボードを作るのが好きなんですが、得意では無いです:innocent:</dd>
</dl>

▽ ②のご参考：AWSにも直接OTELを送れます！CloudWatchで見るのも手です！

https://docs.aws.amazon.com/ja_jp/AmazonCloudWatch/latest/monitoring/CloudWatch-OpenTelemetry-Sections.html

個人的には③は半分ネタですが本気で思ってまして、、何でもAI Agentが分析してくれるこの時代に、ダッシュボードから概要以上を人間が読み取るのは辛い！
**特にコストやコンテキストのような定量的な判断基準を設けやすい値ではなく、挙動そのものに関するログを人間の目で判断するのは大変です！**
※ ただし、[Grafana](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/integrations/integration-reference/integration-claude-code/)など多数の OTEL 可視化ツールのダッシュボードは激かっこいいです。（私は苦手ですが..）役立てられるスキルがある人に絶対おすすめなので、**これらのツールを否定する意図はまっっったくございません**。環境が建てられるならそこからクエリなりしてAIが読めばいいだけなのでメリットばかりです・・。



---

ということで、今回は OTEL を用いて、 **ClaudeCode に自然言語で「今回なんで遅かったと思う？どう直したらいいかな？じゃあそれ反映して！」とお願いできる環境を整えました。**


---

ここからちょっと、今回の設定の工夫をご紹介します。

## ポイント①：Claude Code はOTELをファイルに吐いてくれない・・・

最初に詰まったのがここでした。

Claude Code は OTEL に対応しています（[ご参考](https://code.claude.com/docs/ja/monitoring-usage)）。ただし「ローカルファイルに直接書き出す」機能は現時点で用意されておらず、OTLP プロトコルで送信するだけです・・。
つまり、**受け取る側(Collector)を自分で立てないとデータはどこにも残らない**という仕様です。

（ちなみに GitHub Copilot CLI は `COPILOT_OTEL_FILE_EXPORTER_PATH` らのうち、File出力設定のパラメータを1つ設定するだけでファイル出力できます（[ご参考](https://docs.github.com/ja/copilot/reference/copilot-cli-reference/cli-command-reference)）。...とっても便利です！）

とはいえ、逆にいえば Collector を1枚挟むということは「**後から何でも足せる**」とも言えます！Grafana に流したくなったら exporter を1行足せばいいし、Langfuse でも Jaeger でも同じです。まあ、そう思えば悪くないかな～～と考えています。

ただ、今回すぐに欲しいのは「さっきのセッションで何が起きていたか」だけなので、「ひとまずファイルに落として、そのまま Claude 自身に読ませてしまえばいいじゃん」という方針にしました！

## ポイント②：都度起動するのは必ず忘れるので、`claude()` 関数に全部仕込む

ここで一工夫入れたのが「Collector の起動と停止をどう管理するか」でした。手動で `otelcol-contrib --config ... &` して `kill` するのは絶対に忘れるので、**`claude` コマンド自体にラップしちゃって、自動的に Collector のライフサイクルを管理する**方針にしました。

`~/.bashrc` に `claude()` 関数を定義することで、以下を実現します。

- ① セッションごとにユニークな JSONL ファイル名を自動生成（`<作業ディレクトリ名>_<日時>.jsonl`）
- ② Collector の YAML 設定を `/tmp` に毎回ヒアドキュメントで生成
- ③ Collector をバックグラウンド起動
- ④ `trap` で Ctrl+C・正常終了のどちらでも Collector を確実に停止
- ⑤ Claude Code 本体を `CLAUDE_CODE_ENABLE_TELEMETRY=1` や ローカルで動いている otelcol-contrib の指定付きで起動
- ⑥ 終了後に一時 YAML を削除

### ポイント③：なぜ YAML を bashrc に直接書き込んでいるのか

今回都度生成している `otel-collector-config.yaml` を別ファイルとして置いてもいいのですが、**OTEL の JSONL の出力パスがセッションごとに変わる**ので、静的な YAML に固定値を書くのは不向きです。
そこで、今回はヒアドキュメント（`cat > config.yaml <<EOF ... EOF`）で毎回yamlを動的生成する方式にしました。シェル変数（`${otel_dir}/${name}.jsonl`）をそのまま展開できるので、セッションごとの一意なパスが自然に埋め込めます。`/tmp` に書くので環境を汚すことを気にせず作れて、終了時に `trap` で消すので片付けも気にせずでOKです。


#### 少し脱線：そもそも otelcol-contrib って何？

otelcol-contrib は、OpenTelemetry の Collector で、**テレメトリデータを受け取って、加工して、どこかに送る**ためのミドルウェアです。Apache License Version 2.0 で公開されており、Star数も5千弱と、大人気のOSSです！

https://github.com/open-telemetry/opentelemetry-collector-contrib

OTLP という共通プロトコルで受け取って、Prometheus や Jaeger、Datadog、あるいは「ただのファイル」などに出力できます。

この Collector には2種類のディストリビューションがあります。

| 種類 | 中身 |
|---|---|
| `otelcol` (コア) | 基本的な receivers/exporters だけで、超軽量です。今回は取り扱いません。 |
| **`otelcol-contrib`** | **コミュニティ製を含む全部入り**で、今回使う file exporter もここに入っています。全部入りとは言いますが軽量です。 |

今回やりたい「ファイルに書き出す」ためには **`file` exporter が必要**なので `otelcol-contrib` を使います（コア版には入っていません）。

Collector の動作は **YAML ファイル1枚で全部定義**します。「何から受け取って（receivers）」「どう加工して（processors）」「どこに出すか（exporters）」を記載します。今回の用途だと途中で加工する `processor` すら要らないので、ClaudeからOTELを受け取ってファイルに書くだけのシンプルな構成です。

▽ otelcol-contrib の定義例

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 127.0.0.1:14317   # ← OTLP/HTTP で受ける

exporters:
  file:
    path: /path/to/output.jsonl    # ← ファイルに追記

service:
  pipelines: # trace, metrics, logs を全て出力するように書きました
    traces:  { receivers: [otlp], exporters: [file] }
    metrics: { receivers: [otlp], exporters: [file] }
    logs:    { receivers: [otlp], exporters: [file] }
```

これで `127.0.0.1:14317` に OTLP を投げると JSONL で1ファイルに貯まります。
あとは Claude Code 側に「ここに投げて」と環境変数で指示すればOKです！


### ポイント④：`trap` で二重・異常終了に強くする

Claude のセッションが終わったときに Ctrl+C で雑に抜ける（私はほぼこれを常にやっちゃいます。。笑）と Collector が残ったままになって、次回起動時にポート競合でコケることが分かったので、以下のようにClaudeが起動されるたびに事前に前のプロセスを消します。

```bash
trap 'kill "$otel_pid" 2>/dev/null; wait "$otel_pid" 2>/dev/null; rm -f "$otel_config"; trap - INT TERM EXIT' INT TERM EXIT
```

「INT（Ctrl+C）・TERM・EXIT のいずれでも Collector を kill して wait して config 削除」という1行を入れることで、どう終わっても綺麗に片付くようにしています。加えて関数の先頭で `lsof -t -i :14317` して**前回の残骸を掃除**してから起動します（保険として・・）。

:::note warn
これによって、プロセスが被らないように2回目の起動では敢えてプロセスを落としているので、Claudeを別ターミナルから複数セッション同時に動かしたい場合は工夫が必要です。（既に Collector&Claude が動いている場合はポートを変える など）
:::



# 成果のもう少し細かな紹介

## 出力される JSONL の中身

今回生成される OTEL の JSONL には3種類のデータが混ざっています。

▽ OTELのJSONLに含まれる情報の概要整理

| 種類 | 中身 | 何がわかるか |
|---|---|---|
| Spans | interaction / llm_request / tool.execution / **tool.blocked_on_user** | どこで何秒使ったか |
| Logs | tool_decision, tool_result, api_error, hook_execution | 何のツールを呼んだか、エラーの有無 |
| Metrics | token.usage, cost.usage | トークン量・キャッシュ効率・コスト |

例えば、↑でいうと `tool.blocked_on_user` というスパンがわりと重要でして、**Claude Code が権限プロンプトを出して我々人類が許可を出すまでの待ち時間**が記録されています。

:::note warn
繰り返しになりますが、**OTEL単体では「具体的に送ったプロンプト」や「具体的にAIから返ってきた応答」は残りません**。
トークン数などは分かりますが、具体的なテキストを使いたい場合はセッションログから紐づけて分析しましょう！
次回こちらもネタにします（するつもりです）！
:::

---

## OTEL を分析してくれる Skill を作る（SVG 入りリッチ HTML を吐かせる）

```bash
mkdir -p ~/.claude/skills/claude-code-otel-analysis/scripts
```

`~/.claude/skills/claude-code-otel-analysis/SKILL.md` など、Skills ディレクトリに以下を置きます。

▽ Skill定義例
※ 元ソースは色々自分用に特化したことを書きすぎているので、こちらには簡略版を載せます。Claudeに「OTELを分析して！これが例ね！ほんでSkills化して！」で簡単に作ってくれました！

````markdown
---
name: claude-code-otel-analysis
description: Claude Code の OTEL JSONL を分析し、wall/token/tool の内訳を集計して
  SVG 埋め込みのリッチHTMLレポートを生成する。~/.claude/otel/ 以下に配置された JSONL を
分析したい、どこで時間を使ったか知りたい、権限待ちの有無を確認したいときに使う。
---

メインの出力は `report.html`。SVG を inline 埋め込みし、
この1ファイルをブラウザで開くだけで全グラフが見られるように作成する。

以下のコマンドで分析を実行し、分析結果をレポート出力する。

```bash
python3 ~/.claude/skills/claude-code-otel-analysis/scripts/analyze_claude_otel.py \
  --latest --out-dir /tmp/claude-otel-analysis
```

<中略>

````



<details><summary>（もしご興味を持っていただければ..）今回利用している分析&レポート出力スクリプトのソース </summary>


▽ 分析スクリプト（scripts/analyze_claude_otel.py）
※ シンプルにClaudeCodeに生成してもらったものでしかないので、OTEL出力先ディレクトリなどを変えた場合は別途ClaudeCodeに作らせたほうが良いと思います！

````plaintext
#!/usr/bin/env python3
"""
Claude Code OTEL JSONL 分析スクリプト。

OTLP JSON 形式 (resourceSpans / resourceLogs / resourceMetrics) を読み込み、
interaction ごとの wall/token/tool 内訳を集計して CSV と SVG/HTML を出力する。
"""
import argparse
import csv
import json
import math
import os
import re
from collections import defaultdict
from pathlib import Path


# ────────────────────────────────────────────────────────────
#  基本ユーティリティ
# ────────────────────────────────────────────────────────────

def _attrs(attr_list: list) -> dict:
    """OTLP の [{key, value:{Xvalue: v}}] → {key: v} に変換する。"""
    out = {}
    for a in attr_list:
        k = a.get("key", "")
        v = a.get("value", {})
        for vv in v.values():
            out[k] = vv
            break
    return out


def _nano_to_sec(nano_str) -> float:
    return int(nano_str) / 1_000_000_000


def _scrub(value: str, max_len: int = 120) -> str:
    """個人情報になりやすい値を丸める。"""
    if not value:
        return ""
    s = str(value)
    # ユーザーID(SHA256 like)は短縮
    s = re.sub(r"[0-9a-f]{40,}", "<hash>", s)
    # ファイルパスのホームディレクトリを省略
    s = s.replace(str(Path.home()), "~")
    return s[:max_len]


# ────────────────────────────────────────────────────────────
#  JSONL パーサ
# ────────────────────────────────────────────────────────────

def load_jsonl(path: Path) -> dict:
    """
    JSONL を読み込み、spans / logs / metrics の3リストに分類して返す。
    spans: list of span dict (attributes を展開済み)
    logs:  list of log record dict (attributes を展開済み)
    metrics: list of (name, datapoints) で datapoints は {attrs, value}
    """
    spans = []
    logs = []
    metrics = []

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)

            for rs in obj.get("resourceSpans", []):
                for ss in rs.get("scopeSpans", []):
                    for sp in ss.get("spans", []):
                        a = _attrs(sp.get("attributes", []))
                        start = _nano_to_sec(sp["startTimeUnixNano"])
                        end = _nano_to_sec(sp["endTimeUnixNano"])
                        spans.append({
                            "name": sp.get("name", ""),
                            "trace_id": sp.get("traceId", ""),
                            "span_id": sp.get("spanId", ""),
                            "parent_span_id": sp.get("parentSpanId", ""),
                            "start": start,
                            "end": end,
                            "wall": round(end - start, 4),
                            "attrs": a,
                        })

            for rl in obj.get("resourceLogs", []):
                for sl in rl.get("scopeLogs", []):
                    for r in sl.get("logRecords", []):
                        a = _attrs(r.get("attributes", []))
                        ts_nano = r.get("timeUnixNano", "0")
                        logs.append({
                            "body": r.get("body", {}).get("stringValue", ""),
                            "ts": _nano_to_sec(ts_nano),
                            "attrs": a,
                        })

            for rm in obj.get("resourceMetrics", []):
                for sm in rm.get("scopeMetrics", []):
                    for m in sm.get("metrics", []):
                        name = m.get("name", "")
                        dp_list = []
                        for dp_type in ("sum", "gauge", "histogram"):
                            for dp in m.get(dp_type, {}).get("dataPoints", []):
                                a = _attrs(dp.get("attributes", []))
                                val = dp.get("asDouble") or int(dp.get("asInt", 0))
                                dp_list.append({"attrs": a, "value": val})
                        metrics.append({"name": name, "datapoints": dp_list})

    return {"spans": spans, "logs": logs, "metrics": metrics}


# ────────────────────────────────────────────────────────────
#  集計ロジック
# ────────────────────────────────────────────────────────────

def _tool_name_from_logs(logs: list, span_start: float, span_end: float) -> str:
    """
    tool.execution span に対応する tool_name をログから取る。
    tool_result ログの event.timestamp が span の [start, end] に含まれるもので判定。
    """
    for log in logs:
        if log["body"] != "claude_code.tool_result":
            continue
        if span_start <= log["ts"] <= span_end + 0.05:
            return log["attrs"].get("tool_name", "unknown")
    return "unknown"


def extract_agent_calls(data: dict) -> list:
    """
    Agent(Task) tool の呼び出しを subagent 呼び出しとして抽出する。

    Claude Code 2.1.x では tool_name="Agent" として記録される。
    各要素: {subagent_type, description, prompt_snippet, start, end, wall}
    """
    calls = []
    spans = data["spans"]
    for log in data["logs"]:
        if log["body"] != "claude_code.tool_result":
            continue
        a = log["attrs"]
        # Claude Code 2.1.x: "Agent"、旧版: "Task" も念のため許容
        if a.get("tool_name") not in ("Agent", "Task"):
            continue
        subagent_type = "unknown"
        description = ""
        prompt_snippet = ""
        tool_input_raw = a.get("tool_input", "{}")
        try:
            ti = json.loads(tool_input_raw) if isinstance(tool_input_raw, str) else tool_input_raw
            subagent_type = ti.get("subagent_type", "unknown")
            description = ti.get("description", "")
            prompt_snippet = (ti.get("prompt", "") or "")[:120]
        except Exception:
            pass

        # 対応する tool.execution span を timing で探す
        match_sp = None
        for sp in spans:
            if sp["name"] != "claude_code.tool.execution":
                continue
            if sp["start"] <= log["ts"] <= sp["end"] + 0.05:
                match_sp = sp
                break
        if not match_sp:
            continue
        calls.append({
            "subagent_type": subagent_type,
            "description": description,
            "prompt_snippet": prompt_snippet,
            "start": match_sp["start"],
            "end": match_sp["end"],
            "wall": match_sp["wall"],
        })
    calls.sort(key=lambda c: c["start"])
    return calls


def aggregate(data: dict) -> dict:
    """spans / logs / metrics から分析用集計データを作成する。"""
    spans = data["spans"]
    logs = data["logs"]
    metrics = data["metrics"]

    # ── 1. interaction ごとの集計 ──
    interactions = []
    for sp in spans:
        if sp["name"] != "claude_code.interaction":
            continue
        seq = int(sp["attrs"].get("interaction.sequence", 99))
        if seq >= 2 and sp["wall"] < 1.0:
            continue  # 終了入力など短い後続ターンは除外
        interactions.append({
            "seq": seq,
            "wall": sp["wall"],
            "duration_ms": int(sp["attrs"].get("interaction.duration_ms", sp["wall"] * 1000)),
            "prompt_len": int(sp["attrs"].get("user_prompt_length", 0)),
            "start": sp["start"],
            "end": sp["end"],
        })
    interactions.sort(key=lambda x: x["seq"])

    # ── 2. tool.execution の集計 ──
    tool_calls = []
    for sp in spans:
        if sp["name"] != "claude_code.tool.execution":
            continue
        tname = _tool_name_from_logs(logs, sp["start"], sp["end"])
        tool_calls.append({
            "tool_name": tname,
            "wall": sp["wall"],
            "duration_ms": int(sp["attrs"].get("duration_ms", sp["wall"] * 1000)),
            "success": sp["attrs"].get("success", True),
            "start": sp["start"],
            "end": sp["end"],
        })

    tool_wall_by_name = defaultdict(float)
    tool_count_by_name = defaultdict(int)
    tool_fail_by_name = defaultdict(int)
    for tc in tool_calls:
        tname = tc["tool_name"]
        tool_wall_by_name[tname] += tc["wall"]
        tool_count_by_name[tname] += 1
        if not tc["success"]:
            tool_fail_by_name[tname] += 1

    # ── 3. blocked_on_user の集計 ──
    blocked_total = sum(
        sp["wall"] for sp in spans if sp["name"] == "claude_code.tool.blocked_on_user"
    )
    blocked_count = sum(
        1 for sp in spans if sp["name"] == "claude_code.tool.blocked_on_user"
    )

    # ── 4. llm_request の集計 ──
    llm_calls = [sp for sp in spans if sp["name"] == "claude_code.llm_request"]
    llm_total_wall = sum(sp["wall"] for sp in llm_calls)
    llm_count = len(llm_calls)

    # ── 5. token/cost metric の集計 ──
    token_totals = defaultdict(int)  # (model, query_source, type) -> int
    cost_totals = defaultdict(float)  # (model, query_source) -> float
    for m in metrics:
        if m["name"] == "claude_code.token.usage":
            for dp in m["datapoints"]:
                a = dp["attrs"]
                key = (a.get("model", "?"), a.get("query_source", "?"), a.get("type", "?"))
                token_totals[key] += int(dp["value"])
        if m["name"] == "claude_code.cost.usage":
            for dp in m["datapoints"]:
                a = dp["attrs"]
                key = (a.get("model", "?"), a.get("query_source", "?"))
                cost_totals[key] += float(dp["value"])

    # main/auxiliary 別合算
    def sum_tokens(query_source, token_type):
