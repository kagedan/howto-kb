---
id: "2026-06-11-あなたのclaude-code1日いくら-fable-5従量課金化の前にjsonlログから自分で実測-01"
title: "あなたのClaude Code、1日いくら? Fable 5従量課金化の前にJSONLログから自分で実測・検算する"
url: "https://zenn.dev/yrd/articles/a03e366612cc84"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "Python"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

## 1. Fable 5初日、1日で$119

わたしはClaude Code上で常駐エージェントを2体運用しています。1体はメール・Slackのトリアージとカレンダー管理を担う秘書役、もう1体はノート整理を担うリサーチ役です。ただし、Claude Codeの用途はこの2体だけではありません。アプリ開発をはじめとする日常の業務タスクもClaude Codeで実行しており、本記事で扱うログには常駐エージェント分と業務タスク分の両方が記録されています。

実のところ、わたしはこれまでモデルの振り分けを考えたことがありませんでした。複雑な設計判断も定型のトリアージも、全部Opusでジャブジャブ回す。Maxプランの定額に収まっている限り、それで何も困らなかったからです。

2026年6月9日、Claude Fable 5がリリースされて、この前提が崩れました。Maxプランでは6月22日まで追加費用なしで使えますが、6月23日からはプラン外となり、従量クレジット課金(入力$10/出力$50 per Mtok、Opus 4.8の2倍)に切り替わります。つまり、「最高モデルを何も考えずに使い続ける」という今までのフレームは、従量課金の世界では成立しません。続けるなら、自分の使い方が月いくらになるのかを知らないと判断のしようがない。

しかしサブスクの課金画面にはトークン数が表示されません。そこで無料期間中に実測を始めたところ、初日の集計が\*\*$119.80\*\*でした。

「Fableが高い」で済ませる前に、この数字を**自分で算出し、計算し、検証する**方法を整備しました。本記事はその全ロジックとコードの公開です。同じことが、あなたの `~/.claude/projects/` でもそのままできます。

## 2. 算出ロジック — 「何を数えるか」を正しくする

データソースははっきりしています。Claude Codeは全リクエストのusage情報を `~/.claude/projects/<プロジェクト>/**/*.jsonl` に自動記録しています。1ファイルが1セッションに対応し、サブエージェントの分は `subagents/` 配下に分かれて保存されます。

### 2.1 usage行の構造(v2.1.x時点)

JSONLを読む上で押さえるポイントは3つです。

* 人間の発言行: `promptSource: typed/queued`
* cron等のハーネス注入行: `isMeta: true` + `promptSource: "system"`
* usage行: `message.usage` に input / cache\_creation(5分・1時間TTLの内訳) / cache\_read / output が記録される

### 2.2 正しく数えるための4つの処理 — 省くとどう狂うか

生のJSONLを素朴に合計すると、間違った数字が出ます。必要な処理は4つで、それぞれ省いた場合の誤り方が異なります。

| 処理 | 省いた場合の誤り |
| --- | --- |
| `(message.id, requestId)` で重複排除 | ストリーミングで同一レスポンスが複数行記録されるため過大計上。**わたしの環境の実測(3日分)で2.34倍**に膨れた(§4のコードCで自分の環境の倍率を確認できる) |
| `model == "<synthetic>"` の除外 | API実呼び出しでない行が混入する |
| UTC→ローカル日付変換 | 日次集計が9時間ズレる(JSTなら朝9時までの消費が前日に計上される) |
| `subagents/**` を含む再帰探索 | サブエージェント委譲をしていると過小計上になる |

この4つを織り込んだ最小の算出スクリプトがコードAです。トークン数を数えるだけで、コスト計算はまだしません(それは§3)。

### コードA: count\_tokens.py(算出)

```
#!/usr/bin/env python3
"""コードA: Claude Code のローカルログから1日のトークン消費を数える(算出のみ)。

usage: python3 count_tokens.py [YYYY-MM-DD]   # 省略時は今日(ローカル時刻)
対象: ~/.claude/projects/**/*.jsonl (読み取りのみ・何も変更しない)
"""
import json
import glob
import os
import sys
from collections import defaultdict
from datetime import datetime

target = sys.argv[1] if len(sys.argv) > 1 else datetime.now().astimezone().strftime('%Y-%m-%d')
seen = set()
totals = defaultdict(lambda: dict(input=0, cache_write=0, cache_read=0, output=0, requests=0))

for path in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True):
    with open(path, errors='ignore') as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = d.get('message') or {}
            usage, ts = msg.get('usage'), d.get('timestamp')
            if not usage or not ts:
                continue
            model = msg.get('model', '?')
            if model == '<synthetic>':  # 処理(2): API実呼び出しでない行を除外
                continue
            try:  # 処理(3): UTC→ローカル日付に変換してから日付フィルタ
                day = datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone().strftime('%Y-%m-%d')
            except ValueError:
                continue
            if day != target:
                continue
            key = (msg.get('id'), d.get('requestId'))
            if key != (None, None) and key in seen:  # 処理(1): ストリーミング重複行の排除
                continue
            seen.add(key)
            t = totals[model]
            t['input'] += usage.get('input_tokens', 0)
            t['cache_write'] += usage.get('cache_creation_input_tokens', 0)
            t['cache_read'] += usage.get('cache_read_input_tokens', 0)
            t['output'] += usage.get('output_tokens', 0)
            t['requests'] += 1

# 処理(4): glob の recursive=True が subagents/ 配下も拾っている点に注意
print(f'{target} (ローカル時刻基準)')
for model, t in sorted(totals.items()):
    print(f"{model}: input={t['input']:,} cache_write={t['cache_write']:,} "
          f"cache_read={t['cache_read']:,} output={t['output']:,} req={t['requests']}")
```

### 2.3 まず動かす

```
python3 count_tokens.py 2026-06-11   # 自分の今日の生トークン数が出る
```

わたしの環境でのFable 5初日の実行例です。

```
2026-06-10 (ローカル時刻基準)
claude-fable-5: input=28,193 cache_write=3,156,616 cache_read=47,405,670 output=179,629 req=203
claude-opus-4-8: input=21,937 cache_write=807,789 cache_read=6,083,686 output=85,733 req=91
```

この時点で気づくことがあります。input(素の入力)は3万トークン弱なのに、cache\_readが4,700万トークンある。コストの正体はここに潜んでいます(§5で解剖します)。

## 3. 計算ロジック — 「いくらか」に変換する

### 3.1 単価表と計算式

トークン数が出たら、単価を掛けます。公式単価(2026年6月時点)はトークン種別ごとに異なります。

* input: モデルごとの基本単価
* cache write: **5分TTL = 入力×1.25 / 1時間TTL = 入力×2**
* cache read: 入力×0.1
* output: モデルごとの出力単価

計算式自体は単純で、コスト = Σ(各リクエストの各トークン種別 × そのモデルの単価)です。ただし1つ重要な原則があります。**モデルが混在する期間は、必ずリクエスト行単位で計算する**こと。日やタスクで合算してから単価を掛けると、混在分の計算が狂います。わたしはクロスレビューで指摘されるまで、まさにこのバグを抱えていました。

### 3.2 ここが落とし穴: cache writeのTTLはどちらか

単価表を見て気づいた方もいると思いますが、cache writeの単価はTTLによって1.25倍と2倍の開きがあります。見積もりを1.25倍(5分TTL)で立てると過小評価になります。**わたしの実測では、Claude Codeのキャッシュ書き込みは全て1時間TTL=入力単価の2倍でした。**

これは推測する必要がありません。usage内の `cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens` に内訳がそのまま記録されているので、直接覗けば分かります。

### コードB: check\_cache\_ttl.py(計算の前提検証)

```
#!/usr/bin/env python3
"""コードB: cache write の TTL内訳(5分/1時間)を自分の環境で確認する。

書込単価は 5分TTL=入力×1.25 / 1時間TTL=入力×2 と大差があるため、
コスト見積りの前に「自分の環境はどちらか」を実測しておく。
(比率を見る目的なので重複排除は省略 — 重複は両TTLに等しく乗るため比率は保たれる)
"""
import json
import glob
import os

cw5m = cw1h = legacy = 0
for path in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True):
    with open(path, errors='ignore') as fh:
        for line in fh:
            if '"cache_creation' not in line:  # 高速化: 関係ない行を早期スキップ
                continue
            try:
                usage = (json.loads(line).get('message') or {}).get('usage') or {}
            except json.JSONDecodeError:
                continue
            cc = usage.get('cache_creation')
            if cc:
                cw5m += cc.get('ephemeral_5m_input_tokens', 0)
                cw1h += cc.get('ephemeral_1h_input_tokens', 0)
            elif usage.get('cache_creation_input_tokens'):
                legacy += usage['cache_creation_input_tokens']  # 内訳フィールドがない旧形式

print(f'5分TTL  : {cw5m:,} tokens')
print(f'1時間TTL: {cw1h:,} tokens')
print(f'内訳なし(旧形式): {legacy:,} tokens')
total = cw5m + cw1h
if total:
    print(f'→ 1時間TTL比率 {cw1h / total:.1%} (高いほど実効書込単価は入力の2倍に近づく)')
```

わたしの環境の実行例です。1時間TTLが100%でした。

```
5分TTL  : 0 tokens
1時間TTL: 31,836,962 tokens
内訳なし(旧形式): 0 tokens
→ 1時間TTL比率 100.0% (高いほど実効書込単価は入力の2倍に近づく)
```

## 4. 検証ロジック — その数字を信じてよいか

算出と計算ができても、その数字をそのまま意思決定に使ってはいけません。集計コードにはバグが入り得るし、ログ形式は予告なく変わり得ます。わたしは検算を3つ用意し、**全て通って初めて数字を使う**ことにしています。

1. **独立実装との突合** — 同じ生データを別実装(別人・別エージェント・またはccusage)で集計し、一致を確認します。わたしは2つのエージェントにそれぞれ独立に集計を実装させ、4項目(input/cache write/cache read/output)の完全一致を確認しました。
2. **切り口を変えた検算** — 「日付×モデル」集計と「タスク別」集計の総額が一致するかを確認します。分類バグがあると、合計は合っても内訳が狂います。内訳の妥当性は既知のイベント(この時間帯はトリアージが走ったはず、といった事実)と突き合わせます。
3. **処理の有無での差分確認** — 重複排除をON/OFFして差分を見ます。差が数倍あれば重複排除が正しく効いている証拠です。逆に差がゼロなら、ログ形式が変わった可能性を疑います。

検算1と3を自動化したのがコードCです。

### コードC: verify\_totals.py(検証)

```
#!/usr/bin/env python3
"""コードC: 集計値の検算 — その数字を意思決定に使ってよいか。

(1) 重複排除の有無での差分実測(排除しないと何倍に膨れるか)
(2) 切り口を変えた合計の一致確認(日別合計 = モデル別合計 = 総計)

usage: python3 verify_totals.py YYYY-MM-DD [YYYY-MM-DD]
"""
import json
import glob
import os
import sys
from collections import defaultdict
from datetime import datetime

since = sys.argv[1]
until = sys.argv[2] if len(sys.argv) > 2 else since

def usage_rows():
    """期間内の usage 行を (日付, モデル, 重複排除キー, 総トークン) で列挙する。"""
    for path in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True):
        with open(path, errors='ignore') as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = d.get('message') or {}
                u, ts = msg.get('usage'), d.get('timestamp')
                if not u or not ts or msg.get('model') == '<synthetic>':
                    continue
                try:
                    day = datetime.fromisoformat(
                        ts.replace('Z', '+00:00')).astimezone().strftime('%Y-%m-%d')
                except ValueError:
                    continue
                if since <= day <= until:
                    tokens = sum(u.get(k, 0) for k in (
                        'input_tokens', 'cache_creation_input_tokens',
                        'cache_read_input_tokens', 'output_tokens'))
                    yield day, msg.get('model', '?'), (msg.get('id'), d.get('requestId')), tokens

raw = dedup = 0
seen = set()
by_day = defaultdict(int)
by_model = defaultdict(int)
for day, model, key, tokens in usage_rows():
    raw += tokens
    if key != (None, None) and key in seen:
        continue
    seen.add(key)
    dedup += tokens
    by_day[day] += tokens
    by_model[model] += tokens

print(f'検算対象期間: {since}〜{until} (ローカル時刻)')
print(f'[検算1] 重複排除なし: {raw:>15,} tokens')
print(f'        重複排除あり: {dedup:>15,} tokens', end='')
print(f'  → 排除しないと {raw / dedup:.2f}倍に過大計上' if dedup else '')
day_sum, model_sum = sum(by_day.values()), sum(by_model.values())
ok = day_sum == model_sum == dedup
print(f'[検算2] 日別合計={day_sum:,} / モデル別合計={model_sum:,} / 総計={dedup:,}')
print(f'        → {"一致 ✓ 集計ロジックは自己整合" if ok else "不一致 ✗ 集計バグの疑い"}')
```

わたしの環境(3日分)の実行例です。

```
検算対象期間: 2026-06-09〜2026-06-11 (ローカル時刻)
[検算1] 重複排除なし:     277,051,485 tokens
        重複排除あり:     118,507,848 tokens  → 排除しないと 2.34倍に過大計上
[検算2] 日別合計=118,507,848 / モデル別合計=118,507,848 / 総計=118,507,848
        → 一致 ✓ 集計ロジックは自己整合
```

排除しないと2.34倍。「ccusageを疑え」とまでは言いませんが、自分の意思決定に使う数字は一度自分で検算しておくべき、というのがわたしの立場です。

## 5. 適用例 — $119を解剖したら犯人は「空打ちループ」だった

ここからは、§2〜4の方法論を冒頭の$119に実際に適用した結果です。

### 5.1 日次実測(1台のMac、エージェント用途中心)

| 日付 | モデル | input | cache write(1h) | cache read | output | 概算コスト |
| --- | --- | --- | --- | --- | --- | --- |
| 前日(参考) | Opus 4.8 | 5.3k | 1.43M | 7.33M | 59k | $19.46 |
| Fable初日 | **Fable 5** | 28k | 3.16M | 47.4M | 180k | **$119.80** |
| 同日 | Opus 4.8(別セッション) | 22k | 0.81M | 6.08M | 86k | $13.38 |

表の「Opus 4.8(別セッション)」は、エージェントではなく業務タスク(開発作業など)でClaude Codeを使った分です。わたしの消費は常駐エージェントと業務タスクの両輪で構成されており、$119.80はあくまでエージェント側(Fableに切り替えたセッション群)の数字です。

参考までに、Opus運用時の実測ベースライン(別マシン2台=エージェント常駐機と開発用メイン機・約1.5ヶ月分)は、**いずれも$30〜34/日**、1台あたり月$1,000規模でした。Fable初日のエージェント分はその**4倍**です。単価差(2倍)だけでは説明がつきません。倍率の残り半分はどこから来たのか。解剖します。

### 5.2 解剖 — コストは「コンテキスト長 × 起こされ方」の掛け算

前提として、LLMはステートレスです。**応答のたびに会話履歴全体を送り直します**。常駐エージェントは履歴が育ち続けるため、夜には20〜30万トークンに達していました。

プロンプトキャッシュがあるので、繰り返し分は読込0.1倍に割引されます。ただし**TTLが切れた後の再書込は入力単価の2倍**です。つまりコスト構造はこうなります。

内訳を見ると、初日は203リクエスト、cache readは47.4Mトークン。**20数万トークンの履歴を約190回読み直した**計算になります。

犯人を特定しました。30〜60分間隔で動く「自律ループ」(ユーザー不在時の見回り機能)です。**見回るたびにキャッシュの期限を跨ぎ、巨大な履歴のフル再読込が発生していた**。しかも秘書エージェントの仕事は実際にはcronと対話でしか発生しておらず、見回りはほぼ空打ちでした。

タスク別に集計した結果(3日分)がこちらです。

| タスク | コスト | 一言 |
| --- | --- | --- |
| 対話・個別タスク | $57 | 本体価値。ここは削らない |
| **ループ空打ち** | **$28** | **全くの無駄と判明 → 廃止** |
| 朝ブリーフィング | $28 | 並列ツール群が重い。改善余地 |
| Slackトリアージ | $13 | 委譲候補 |
| Gmailトリアージ | $3 | 委譲候補 |

## 6. 対策 — 運用で削る(モデルを変える前に)

解剖結果から打った対策は、モデルの変更ではなく運用の変更でした。

1. **空打ちの定期起床を廃止** — 必要な実益(深夜のログ保存等)は時刻指定のcron 1本(1日1回の冷間起動)に置き換えました。
2. **セッションを長生きさせない** — 適時新規セッションに切り替えて、履歴を短く保ちます。掛け算のもう片方を縮める対策です。
3. 教訓として: **新しい常駐運用を導入したら、初日にコストを実測して費用対効果を検証する**。計測は対象だけでなく、計測者自身の無駄も写します。

## 7. モデル最適化 — タスク別の振り分け設計

運用で削った後に、ようやくモデルの話です。

Claude Codeのモデル指定はセッション単位ですが、**サブエージェント(Agent tool)にはモデルを個別指定できます**。これを使った設計はこうなります。判断・進言を伴う対話はFable/Opus(メイン)が担い、定型トリアージはSonnet/Haikuのサブエージェントに委譲する。

委譲の効果は二重です。第一に単価が1/3〜1/10になる。第二に、**サブエージェントは長大な履歴を持たないため、§5.2の掛け算の両辺が同時に縮みます**。

委譲できるかどうかを決めるのは「手順と状態のファイル外部化」です。手順書・pending状態・通知フォーマットが全てファイルにあれば、会話の記憶を持たないサブエージェントでもそのまま実行できます。委譲後の品質がメイン直営と比べてどうかは、現在検証中です。

## 8. 判断 — 6/23以降どうするか

執筆時点(6/11)では計測期間の途中ですが、判断材料は出揃いつつあります。

* Opus運用時のベースライン: $30〜34/日 ≒ 月$1,000規模(§5.1)
* Fable 5の単価はその2倍。運用をそのまま全面Fable化すれば月$2,000超
* ただし初日の$119の主因はモデル単価ではなく運用(空打ちループ)でした。§6の対策後の日次がどこまで下がるかを、残りの無料期間で実測します

月額の試算式は§3の単価をそのまま月次に展開したものです。

```
月額 ≒ (入力Mtok×単価 + cache read Mtok×0.1単価
        + cache write Mtok×2単価 + 出力Mtok×単価) × 30日
```

現時点の見立てはハイブリッドです。判断・進言を伴うメインの対話にだけ高いモデルを置き、定型トリアージは安価なサブエージェントに委譲する(§7)。Fable継続かOpus回帰かの最終判断は、対策後の実測値をこの式に入れて決めます。

判断の枠組み自体は記事の方法論と地続きです。「最高モデルが必要なタスクはどれか」をタスク別の実測で特定してから、必要な所にだけ高いモデルを置く。モデル選択を感覚ではなく、自分のログの実測値で決める。この枠組みは、そのまま自分の判断に流用できます。

## 9. まとめ — 6つの教訓

1. 常駐エージェントのコスト主変数は「コンテキスト長×起こされる頻度」。モデル単価は係数にすぎない
2. cache writeの実効単価は公称の想定より高いことがある(実測では1時間TTL=入力の2倍)。見積もりは実測で補正する
3. 空打ちの定期起床は静かに月数百ドルを溶かす。cron化・イベント駆動化で代替する
4. タスク別集計をすると「どこに高いモデルが必要か」が定量で見える。JSONLに全データは既にある
5. 手順と状態をファイルに外部化した設計は、安価なサブエージェントへの委譲をそのまま可能にする(将来のコスト弾力性)
6. 集計値は検算して初めて意思決定に使える。独立実装との突合・切り口を変えた再集計・処理有無の差分確認の3点セット(§4)

## 10. 付録 — 既知の注意点

本文のコードA/B/Cは2026-06-11に実データで動作検証済みです。課金計算まで含めた完全版が欲しい場合は、コードAの集計結果に§3.1の単価表を掛けるだけです。タスク別の内訳が欲しい場合は、usage行と同じJSONLにある `promptSource` や `isMeta`(§2.1)でリクエストを分類してから、同じ集計をすれば得られます。

* JSONLは非公開の内部フォーマットです。本記事はClaude Code v2.1.x時点の構造に基づいており、将来変わり得ます(掲載コードはフィールド欠落に耐えるよう `.get()` で防御しています)
* cache writeの集計には、「トップレベルの `cache_creation_input_tokens`」と「`cache_creation` 内訳の合計」が約0.1%ズレる行が存在します(コードAは前者、コードBは後者を読んでいます)。意思決定に影響しない誤差ですが、完全一致を期待すると気づきます
* Fable 5のサブスク提供は2026-06-22までで、6/23以降は従量クレジットに移行します。ただしAnthropicは容量確保後にサブスクへ復帰させる方針を表明しており、本記事のコスト前提は変わる可能性があります
