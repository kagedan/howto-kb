---
id: "2026-04-18-二晩でclaudeと二人三脚でrsyslogの監獄から脱獄した話-01"
title: "二晩でClaudeと二人三脚でrsyslogの監獄から脱獄した話"
url: "https://zenn.dev/naoto256/articles/limpid-log-pipeline"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

※ この記事とソフトウェアは、Claude と一緒に作りました。

## あなたもきっと越えられなかった syslog の壁

既製品の syslog デーモンを「なんとなく合わない」と感じるのは、機能不足のせいではありません。運用者ごとの要件の組み合わせが独特で、どの設計思想の内側にも綺麗には収まらない。個々の処理はありふれている。それでも、組み合わさった途端に越えられない壁になる。

たとえば、こんな組み合わせを想像してみてください。

* ファイアウォール各種から syslog を TCP/UDP で受ける
* Azure Monitor Agent (AMA) に CEF ログを転送する。CEF ログには PRI が付いていないので、facility/severity を条件付きで書き換える必要がある
* FortiGate の traffic ログは量が多すぎて AMA には送らない。破棄する
* Juniper IDP の CHARGEN 検知ログは、同じ攻撃元 IP から毎秒何十件も飛んでくる。全部送ったら AMA もログストレージも崩壊する。でも全部捨てるわけにもいかない。「同じ IP からは 5 分に 1 回だけ通す」という重複排除がしたい

特別なことはしていません。syslog を運用していれば、どこかで見たことがある構成です。ただ、これをきれいに書ける設定ファイルが欲しい。ただそれだけのことが、長年かなえられていませんでした。

## 既製品の話

### rsyslog

長年付き合ってきました。動きます。止まりません。ただ、設定が読めない。

```
template(name="DynFile" type="string" string="/var/log/remote/%HOSTNAME%/%$YEAR%-%$MONTH%-%$DAY%.log")
if $fromhost-ip == '203.0.113.20' then {
    if not ($rawmsg contains 'type="traffic"') then {
        action(type="omfile" dynaFile="DynFile")
    }
}
```

このログがどこに行くか、3 秒で分かりますか。私はいつも 10 秒くらい迷います。`template` と `action` と `if` が入れ子になった設定を見るたびに、「これ、前任者から引き継いだら地獄だろうな」と思います。自分で書いた設定でさえ、半年後に読み直すと自分が何をしたかったのか分かりません。

CHARGEN の重複排除については、rsyslog 単体では無理です。ステートフルなフィルタを書く仕組みがありません。外部プロセスを挟むか、別のツールを前段に置くか。どちらにしても「設定を読めば全部わかる」世界からは遠ざかります。

ディスク永続化キューはあります。`queue.type="disk"` で一応書けます。ただ、プロセス再起動時にキューがどう復旧するのか、ドキュメントから読み取るのが難しい。運用中に「たぶん動くはず」と思いながら使うのは精神衛生上よくない。

### syslog-ng

設定の構造が rsyslog より整理されています。期待してインストールしました。

RFC 6587 の octet counting フレーミングが、自分の環境では動きませんでした。TCP syslog で長いメッセージを扱う必要があるので、ここは譲れません。追いかける時間もなかったので、撤退しました。

### fluentd

「ログを JSON ストリームとして統一的に扱う」という設計思想は美しい。期待してドキュメントを読み込みました。そして、やめました。

tag ベースのルーティングが後付けで導入された歴史があって、設定が増えるほど tag の管理が複雑になります。tag の意味論が明示されていないまま、各プラグインが独自の流儀で tag を付け替える。設定を書く側は、各プラグインのドキュメントを横断して頭の中で合流させる必要がある。

`copy` プラグインでレコードが共有参照になっていて、後段のフィルタでレコードを変更すると、分岐した先にも影響が伝播するという問題もある。これは設計の根本に近いところで、「後で気をつければ大丈夫」というタイプの話ではない。

どれも優れたソフトウェアです。長年、現場を支えてきた実績があります。ただ自分の運用要件にあった設計ではありませんでした。

## 昔なら、諦めていた

ほしいものはずっと頭にある。でも既製品では満たされない。なんなら自分で書きたい、だけど忙しすぎてそんな時間はない。

ひとりで書いて 1 年。枯らすのにさらに 3 年。片手間で維持するのはまず無理。現実的にはどれかの既製品で我慢して、イライラする設定ファイルと付き合い続ける。これが選択肢でした。

最近、この前提が崩れました。

ひとりで 1 年の作業が、Claude Code と組むと二晩に圧縮される。設計の壁打ちをしながら、実装は分業できる。ログパイプラインというドメインは幸運にも、基礎となる技術が十分に枯れています。syslog プロトコル、TCP/UDP の受信、非同期キュー、正規表現、ハッシュテーブル ― すべて教科書的な素材の組み合わせ。AI と相性がいい領域です。

作ろうと思った夕方に設計を固めて、二晩明けには 1 万行を超えるコードが動いていました。

## limpid

二晩走り抜けて書き上げたもの、limpid ―「透明な、明晰な」。その名が示すとおり、設定を読めば何が起きるか分かる、それを最優先で設計しました。

中核は 3 つです。

**設定の透明性**。input / process / output を再利用可能なモジュールとして個別に定義し、pipeline でレゴのように組み立てる。設定言語は TOML/YAML ではなくログパイプラインに最適化した専用 DSL。出力文は非終端なので、1 つのパイプラインから複数の宛先に柔軟にイベントを分配できます。

**可視性**。パイプラインの各ポイントで、メトリクスが自動でカウントされる。どこで何件受けて、何件 drop して、何件書き出したか。そしてこのメトリクスは、API 経由でいつでも取得できます。専用の CLI で見ることもできるし、HTTP ブリッジを介して Prometheus で監視することもできる（このブリッジもユースケースの例として同梱しています）。「中で何が起きているか分からない」という syslog 運用の大きな不満が、ここでほぼ解決します。でもそれだけではありません。limpid はパイプラインの任意の箇所にタップを差し込めます。再起動なし、設定変更なし、本番稼働中のデーモンの処理内容を、リアルタイムにストリームできるのです。「どこでどんな変換がなされて、結局どうなってんの？」― そのストレスから解放される、今までにない経験です。

**安全性**。出力文は非同期キュー消費で、ネットワークやファイルへの I/O ボトルネックがパイプラインに伝播しない。WAL ベースのディスクキューでプロセス再起動をまたいだイベント保持。input にトークンバケット方式のレートリミット。起動前の設定ファイル検証、サンプルデータによるパイプラインの動作検証ドライラン。SIGHUP によるホットリロードは、検証失敗時に自動ロールバック。

コンセプトの解像度を上げるところから実装まで、Claude とふたり、走り抜けました。たった二晩の大脱出劇です。

|  | 内容 |
| --- | --- |
| コード量 | Rust 約 11,000 行（3 クレート） |
| Input | syslog\_udp, syslog\_tcp, syslog\_tls, tail, unix\_socket, journal |
| Output | file, http, kafka, tcp, udp, unix\_socket, stdout |
| Process | parse\_cef, parse\_json, parse\_kv, parse\_syslog, strip\_pri, regex\_replace ほか |
| 式関数 | contains, regex\_match, geoip, to\_json, table\_lookup, sha256 ほか全 15 個 |
| ユニットテスト | 99 |
| ツール | limpidctl（tap/inject/stats/list/health）、limpid-prometheus |

## アーキテクチャ

limpid の構成要素は 4 つ。**input**（受信）、**process**（変換）、**output**（送信先）── この 3 種類のモジュールを **pipeline** で配線します。モジュールは再利用可能、pipeline は配線図。

これだけ頭に入れておけば、あとは実例で見たほうが早いです。

## 実際の動き

ここからは、冒頭で書いた運用要件を limpid で組み立てていきます。TCP で CEF を受けて AMA に転送する ― この最小構成から、一つずつ要件を足していきます。

### Step 1: 受けて、転送する

inputs/tcp514.limpid

```
def input tcp514 {
    type syslog_tcp
    bind "0.0.0.0:514"
}
```

outputs/ama.limpid

```
def output ama {
    type tcp
    address "127.0.0.1:28330"
    framing non_transparent
}
```

pipelines/ama\_forward.limpid

```
def pipeline ama_forward {
    input tcp514
    output ama
}
```

3 ファイル、14 行。どのログがどこに行くか、一目で分かります。

起動する前に検証します。

```
$ limpid --check --config /etc/limpid/limpid.conf
Configuration OK
  1 input(s), 1 output(s), 0 process(es), 1 pipeline(s)
```

構文だけでなく、存在しないモジュールの参照も検出します。CI に組み込めば、設定ミスを本番投入前に捕まえられます。rsyslog で「設定を直した、リロードした、ログが止まった」の事故を何度繰り返してきたことか。そんな日々とはもうさよならです。

### Step 2: 不要なログをフィルタする

FortiGate の traffic ログは大量なので、AMA には送らない。

processes/filter\_fortinet\_traffic.limpid

```
def process filter_fortinet_traffic {
    if contains(raw, "Fortinet") and contains(raw, "cat=traffic:") {
        drop
    }
}
```

pipelines/ama\_forward.limpid

```
def pipeline ama_forward {
    input tcp514
    process filter_fortinet_traffic
    output ama
}
```

process を 1 つ追加、pipeline に 1 行足しただけ。`drop` はメトリクス上 `events_dropped` としてカウントされるので、「フィルタが本当に効いているか」の可視化も自動でついてきます。

本番に出す前に、サンプルデータでロジックを確認します。

```
$ limpid --test-pipeline ama_forward --config /etc/limpid/limpid.conf \
    --input '{"raw": "<134>CEF:0|Fortinet|FortiGate|7.0|traffic|cat=traffic: session"}'
=== Pipeline: ama_forward ===
[input] → raw: <134>CEF:0|Fortinet|FortiGate|7.0|traffic|cat=traffic: session
[process]  filter_fortinet_traffic → dropped
```

実際の input / output には接続せず、パイプラインのロジックだけ検証します。dev 環境を用意して再現する儀式が消えました。

### Step 3: AMA に届いていない? タップで覗く

運用を始めてしばらくすると、AMA 側で受信できていないログがあることに気づきます。何を送っているのか確認したい。

syslog 運用で一番つらい瞬間です。「ログが届いてない」という報告を受けて、何が起きているか調べなきゃいけない。rsyslog ならデバッグモードで再起動するか、`tcpdump` で掘るか。本番を再起動するのか、それとも dev 環境で再現できるのか。デバッグログは多すぎて該当行を目視で探すことになる。

limpid なら、一行です。

```
$ sudo limpidctl tap output ama
<158>CEF:0|Fortinet|FortiGate|7.0|attack|src=203.0.113.5
<155>CEF:0|Paloalto|PA-220|10.2|threat|src=198.51.100.42
  ⋮
```

本番稼働中のデーモンに、再起動なし・設定変更なしで、特定の output に流れているイベントをリアルタイムで覗けます。`--json` を付ければ全フィールド（timestamp, source, facility, severity, raw, message, fields）が JSON で取れるので、`jq` に流して絞り込みもできます。

タップしていない間のオーバーヘッドはほぼゼロ（イベントごとのアトミックなサブスクライバ数チェック程度）なので、本番に入れっぱなしで問題ない。

デバッグ用の設定を足しては試し足しては試し、、、という無限ループはもう必要ありません。

### Step 4: PRI を書き換える

タップで見た結果、原因が見えてきました。受信側は facility 16（local0）を CEF、17（local1）を Syslog として期待しているようです。ところが届いているログの PRI は送り手ごとにまちまちで、期待とは違うものが混ざっている。受け側に合わせて書き換える必要がありそうです。

processes/ama\_pri\_rewrite.limpid

```
def process ama_pri_rewrite {
    if contains(raw, "CEF:") {
        facility = 16
    } else {
        facility = 17
    }
    severity = 6
}
```

pipelines/ama\_forward.limpid

```
def pipeline ama_forward {
    input tcp514
    process filter_fortinet_traffic | ama_pri_rewrite
    output ama
}
```

process は `|` で連結できます。「フィルタしてから、PRI 書き換えて、AMA に送る」― そのまま読める。

設定を変えたらホットリロードします。

```
$ sudo systemctl reload limpid
```

SIGHUP で再読み込み、ダウンタイムなし。rsyslog でも reload はできますが、設定にエラーがあったときの挙動を覚えているでしょうか。rsyslog は場合によっては古い設定で動き続けるか、最悪クラッシュします。

limpid は違います。ホットリロード時にも設定を検証して、失敗したら自動でロールバックします。急いで `--check` を飛ばしてリロードしても、ログ転送は止まりません。

リロード後のパイプライン、どんな形になっているか見てみます。

```
$ sudo limpidctl list
ama_forward:
  input   tcp514
  process filter_fortinet_traffic
  process ama_pri_rewrite
  output  ama
```

意図したとおりのパイプラインになっていることが分かります。各ポイントを流れているイベントを覗いて、処理できているか確認してみましょう。

```
# 入口 ― 送り手ごとにまちまちな PRI
$ sudo limpidctl tap input tcp514
<158>CEF:0|Fortinet|FortiGate|7.0|attack|src=203.0.113.5
<155>CEF:0|Paloalto|PA-220|10.2|threat|src=198.51.100.42
  ⋮

# PRI 書き換え後 ― facility / severity が揃っている
$ sudo limpidctl tap process ama_pri_rewrite
<134>CEF:0|Fortinet|FortiGate|7.0|attack|src=203.0.113.88
<134>CEF:0|Paloalto|PA-220|10.2|threat|src=198.51.100.17
  ⋮

# 出口 ― 実際に AMA へ流れているもの
$ sudo limpidctl tap output ama
<134>CEF:0|Fortinet|FortiGate|7.0|attack|src=203.0.113.200
<134>CEF:0|Paloalto|PA-220|10.2|threat|src=198.51.100.7
  ⋮
```

`<158>` / `<155>` でまちまちだった PRI が、`<134>`（facility 16 = local0、severity 6 = info）に揃って AMA に届いているのが分かります。パイプラインの処理が、コマンド一発で見える。

### Step 5: CHARGEN の嵐

Juniper IDP から CHARGEN 検知ログが大量に飛んできます。同じ攻撃元 IP から毎秒何十件。全部転送すれば AMA もストレージもパンク。全部捨てれば攻撃検知ができない。「同じ IP からは 5 分に 1 回だけ通す」。これがやりたい。

rsyslog でステートフルなフィルタを書く方法は、ありません。外部プロセスに投げるか、別のツールを前段に置くか。設定の見通しが一瞬で崩壊します。

limpid には、インメモリの key-value テーブルがあります。DSL からアクセスできて、TTL 付きで読み書きできる。これで書けます。

limpid.conf

```
table {
    chargen_seen {
        max 10000
    }
}
```

processes/filter\_chargen.limpid

```
def process filter_chargen {
    if contains(raw, "CHARGEN") {
        // 攻撃元 IP を正規表現で抽出
        fields._src = regex_extract(raw, "Attack log <([^/]+)/")

        // 既に登録されていれば重複 → drop
        if table_lookup("chargen_seen", fields._src) != null {
            drop
        }

        // 初出なら登録、300 秒（5 分）で自動消滅
        table_upsert("chargen_seen", fields._src, "1", 300)
    }
}
```

`table_upsert` の第 4 引数は TTL です。テーブル宣言側で `ttl 300` のようにデフォルト値を書いておけば、各呼び出しで省略できます。どちらも省略した場合は TTL なし ― エントリは `table_delete` で明示的に消すまで残り続けます。

pipelines/ama\_forward.limpid

```
def pipeline ama_forward {
    input tcp514
    process filter_chargen | filter_fortinet_traffic | ama_pri_rewrite
    output ama
}
```

実際に動かしたメトリクスがこれです。

```
$ sudo limpidctl stats
Pipelines:
  ama_forward                278941 received     10117 finished    268824 dropped         0 discarded

Inputs:
  tcp514                    278941 received         0 invalid         0 injected

Outputs:
  ama                         10117 received         0 injected     10117 written         0 failed         0 retries
```

27 万件受信、26 万件 drop、AMA に届いたのは 1 万件。CHARGEN の嵐と FortiGate traffic を削って、本当に必要なログだけが残りました。

`discarded` が 0 なのも大事です。これは「イベントがパイプラインを通過したのにどの output にも行かなかった」件数で、ルーティングの設計ミスを検出するためにあります。0 なら、すべてのイベントが意図通りに処理された証拠です。

### Step 6: AMA が落ちたら

ここまでで転送は動いていますが、AMA が再起動したり一時的に応答しなくなったらどうなるか。デフォルトのメモリキューではイベントが失われます。rsyslog にも `queue.type="disk"` はあります。ただ、復旧時の挙動がドキュメントから読み取りにくく、不安を抱えたまま使っている人も多いと思います。

limpid では output にディスクキューを数行追加するだけです。

outputs/ama.limpid

```
def output ama {
    type tcp
    address "127.0.0.1:28330"
    framing non_transparent

    queue {
        type disk
        path "/var/lib/limpid/queues/ama"
        max_size "1GB"
    }
}
```

WAL (Write-Ahead Log) ベースで、プロセス再起動をまたいでイベントを保持します。AMA が復旧すれば、溜まったイベントが自動で流れ出ます。破損したエントリはスキップして続行するので、ディスク障害でパイプライン全体が止まることもありません。

### Step 7: 全量のログをファイルにも残す

CHARGEN dedup で AMA へのノイズは減りましたが、dedup で落としたログは **捨てた** ことになっています。攻撃の後追い分析や監査のために、生ログ自体は残しておきたい。

パイプラインを少し組み替えて、dedup の前に全量をファイルへ吐きます。

outputs/archive.limpid

```
def output archive {
    type file
    path "/var/log/limpid/archive.log"
}
```

pipelines/ama\_forward.limpid

```
def pipeline ama_forward {
    input tcp514
    process filter_fortinet_traffic | ama_pri_rewrite
    output archive              // ← ここで全量をファイルに保存
    process filter_chargen
    output ama
}
```

パイプラインの形が、そのままイベントの旅路になっています。FortiGate traffic を削り、PRI を揃え、そこまでのログを archive に残す。そこから CHARGEN dedup を通して、最終的に AMA へ送る。archive には全量、AMA には dedup 後のログ。

ここで地味に効くのが、limpid の出力文が **非終端** だという設計判断です。`output archive` を書いても、その行でパイプラインは終わらない。イベントのディープコピーが archive のキューに投入され、本流は次の `process filter_chargen` にそのまま進みます。ディープコピーなので、archive 側の都合で本流のイベントが書き換わる事故も起きません。fluentd の `copy` プラグインで起きるレコード変異の波及問題が、構造的に発生しない。

### Step 8: 取りこぼしたログを、あとから流す

ディスクキューでも守り切れない時間はあります。limpid を導入する前のアーカイブ、プロセスが落ちていた時間帯、別サーバに残っていたファイル ― これらを後からパイプラインに流し込みたい。

tap の対称機能として、`limpidctl inject` があります。

```
# ファイルをパイプラインの上流に流す（フィルタも書き換えも通常通り効く）
cat archive.log | sudo limpidctl inject input tcp514

# 加工済みのログを出力キューに直接積む（パイプラインをバイパス）
cat processed.log | sudo limpidctl inject output ama
```

`--json` を付ければ、tap が出力する形式（timestamp・source・fields 全部入り）をそのまま注入できます。tap → inject のラウンドトリップが成立する。

```
# 本番のトラフィックを捕獲
ssh prod sudo limpidctl tap input tcp514 --json > captured.jsonl

# ステージングで再生
ssh staging sudo limpidctl inject input tcp514 --json < captured.jsonl
```

本番トラフィックのステージング再生が、二行です。ログパイプラインのテストの概念が変わります。

### ついでに、レートリミット

input にはレートリミットを 1 行で付けられます。

inputs/tcp514.limpid

```
def input tcp514 {
    type syslog_tcp
    bind "0.0.0.0:514"
    rate_limit 10000    // events/sec
}
```

トークンバケット方式。バーストは 1 秒分まで許可。それ以上は捨てる。rsyslog でこれをちゃんと設定したことがある人なら、この 1 行のありがたさが分かるはずです。

## Claude との分業について

ここまで読んで、「で、Claude はどこで活躍したの」と思った方へ。

役割分担は、書き出せばこうなります。

* **設計判断** ― 自分。DSL 構文、パイプラインモデル、モジュール分類、output の非同期化、`table_*` 関数の API、全部
* **実装** ― Claude Code

ただ、この「設計判断」は、最初に仕様を固めて指示を投げて終わり、という話ではありませんでした。実際の作業の大半は、**コンセプトを自分の言葉で説明し続けること** と、**実装がそこから少しずつズレていくのを検出すること** に費やされました。

検出の主な手がかりは、Claude が作業中に漏らす独り言 ― 生成途中に出力される思考の断片です。「ここは最短で書くと…」「こうすれば通るが…」といったつぶやきを眺めていると、コードが書き上がる前にだいたい違和感の正体が見えてきます。

LLM はコードを書くのは速い。でも「このコンセプトでいいのか」「今の実装は最初の思想からズレてないか」を判定してくれるわけではありません。放っておくと、動くけど一貫性のない機能の山が積み上がる。特に limpid のように「**何を自分の責務にしない**」が設計の核にあるプロダクトでは、この判定は止まらない仕事になります。

具体例を一つ。input/output のモジュールを実装しているときのことです。Claude の独り言を眺めていると、既存コードに手を入れて…… あれ、どう考えても修正すべきじゃないファイルを修正してるぞ？ いやちょっと待って、そこ、いまどういう実装にしてるの？ 問いただすと、モジュールをランタイムに `match` でハードコードしていました。`"syslog_udp"` → `SyslogUdpInput::new()` という形。モジュールを追加するたびにランタイムを触る必要がある構造です。

これはまずい。後になればなるほど地味に効いてくる。そこで、レジストリパターンにするよう軌道修正しました。

```
pub fn register_builtins(registry: &mut ModuleRegistry) {
    register_input_type::<SyslogUdpInput>(registry, "syslog_udp");
    register_input_type::<SyslogTcpInput>(registry, "syslog_tcp");
    register_input_type::<TailInput>(registry, "tail");
    // 新モジュールはここに 1 行追加するだけ
}
```

これ以降、output モジュールは既存コードの修正ほぼゼロで追加できるようになり、http / kafka / unix\_socket / stdout といったモジュールを Claude が書く際の効率と正確性が爆上がりしました。アーキテクチャの骨を先に通しておくと後半の生産性が段違いになるのは、AI に実装を任せる場合でも変わりません。

この軌道修正も、振り返れば「それちゃうやろ」という違和感を言語化して戻す作業でした。仕様を渡す指示者というより、**コンセプトの番人** と言ったほうが実態に近い気がします。AI がコードを速く出せるようになるほど、「このコードはコンセプトに忠実か」を見る目の重要性は、むしろ増していきます。

逆に、Claude が圧倒的に速かったのは:

* **ボイラープレート** ― Input/Output の各モジュールは構造が似ている。1 つ丁寧に書けば、残りは正確に量産してくれる
* **パーサ実装** ― PEG 文法と AST の変換は、人間がやると地味に時間を溶かす領域
* **テスト量産** ― エッジケースを含めたテストを大量に書いてくれる

設計は人間、実装は AI。この分業が、二晩の大脱出劇を可能としたのです。

## 終わりに

「自分の運用に合ったソフトウェアは、自分で書いて維持する」── これが現実的な選択肢になった日の話を書きました。

何年もどうにもならなかった壁が、二晩で越えられた。コンセプトの解像度を上げることに集中していれば、書き起こしは AI が引き受けてくれる。「諦めるしかない」のリストが、ひとつずつ片付いていく時代になりました。

あなたが今この瞬間に「既製品ではどうにもならない」と諦めている要件があるなら、まずそれを言語化してみてください。壁の輪郭がはっきりすれば、もう半分は越えています。

limpid 自体はまだ若いプロジェクトで、他の環境で揉まれていくのはこれから。それでも、ここで動いている事実が誰かの最初の一押しになれば嬉しいです。rsyslog の設定ファイルを前に途方に暮れた経験のある方、ログパイプラインはもっと透明であっていいと感じる方、ぜひ覗いてみてください。

<https://github.com/naoto256/limpid>

---

*limpid = 「透明な、明晰な」。ログパイプラインの設定に、その名に恥じない透明さを。*
