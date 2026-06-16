---
id: "2026-06-15-claudeのprompt-cacheが効かない原因をcache-diagnosticsで特定してみ-01"
title: "Claudeのprompt cacheが効かない原因を、cache diagnosticsで特定してみた"
url: "https://zenn.dev/mochitec_tech/articles/cff58bf183c643"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Python", "zenn"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは。株式会社MOCHITECでCTOをしている上田（@ryo\_u27）です。

prompt caching を使っていると、たまに `usage.cache_read_input_tokens` がゼロに落ちます。コストとレイテンシが跳ねる。でも「なぜ効かなかったのか」は出てこない。エラーは出ず、`cache_read_input_tokens` が静かにゼロになるだけ。原因の特定は、これまで勘に頼るしかありませんでした。

2026年5月、Anthropic がこの「勘で潰す」を埋めにくる機能を出しました。**cache diagnostics**。前のリクエストのidを渡すと、APIが2つのリクエストを比較して「どこで最初に分岐したか」を教えてくれます。気になったので、最小構成で触ってみました。

### 想定読者

* Claude API で prompt caching を使っているが、`cache_read_input_tokens` がたまにゼロになる人
* 原因を勘で潰していて疲れた人
* multi-turn / エージェントで、キャッシュが効く前提のコスト設計をしている人

## prompt cacheは「1バイトでも違うと崩れる」

まず前提。prompt caching が効くのは、プロンプトの先頭が**直前のリクエストとバイト単位で完全一致**しているときだけです。

崩れる経路はだいたい決まっています。

* system prompt に現在時刻やリクエストIDを差し込む
* tool の並び順が変わる、schema のシリアライズが非決定的
* 過去メッセージを編集・切り詰める（append じゃなくする）

どれも `cache_read_input_tokens` がゼロに落ちる、という一点でしか観測できない。「何が変わったか」は分からない。ここが今まで穴でした。

## cache diagnosticsが埋めにきたギャップ

cache diagnostics は2026年5月13日公開のbeta機能です。使うには beta header を付けます。

```
anthropic-beta: cache-diagnosis-2026-04-07
```

仕組みはシンプルです。

1. beta header があると、APIはリクエストごとに軽量な**フィンガープリント**を保存する（レスポンスの `id` をキーに）
2. 次のリクエストで、その `id` を `diagnostics.previous_message_id` として渡す
3. APIが新旧のフィンガープリントを比較し、**最初の分岐点**を `diagnostics` オブジェクトで返す

フィンガープリントはハッシュとトークン数の推定値だけで、生のプロンプトは保存しない（ZDR適格）。判定しているのは「リクエストの構造が変わったか」だけです。キャッシュが実際にヒットしたかどうかは別軸なので、混ぜずに読みます。

## 実際に動かしてみる

最小構成はこれです（Python）。turn1 は比較対象がないので `previous_message_id=None` で opt-in、turn2 で turn1 の `id` を渡します。

```
import anthropic

client = anthropic.Anthropic()

SYSTEM = "You are an AI assistant analyzing a large document. <document>...</document>"

# Turn 1: previous_message_id=None で opt-in
r1 = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system=SYSTEM,
    messages=[{"role": "user", "content": "Summarize section 1."}],
    diagnostics={"previous_message_id": None},
    betas=["cache-diagnosis-2026-04-07"],
)

# Turn 2: 前のレスポンスidを渡す
r2 = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system=SYSTEM,
    messages=[
        {"role": "user", "content": "Summarize section 1."},
        {"role": "assistant", "content": r1.content},
        {"role": "user", "content": "Now summarize section 2."},
    ],
    diagnostics={"previous_message_id": r1.id},
    betas=["cache-diagnosis-2026-04-07"],
)

d = r2.diagnostics
if d is None:
    print("No divergence detected.")
elif d.cache_miss_reason is None:
    print("Comparison still pending.")
else:
    print(f"cache_miss_reason: {d.cache_miss_reason.type}")
```

実際に `claude-opus-4-8` で回すと、こうなりました（2026-06-15 実行、`system` には約6,000トークンのダミー文書を積んでいます）。

| turn | 内容 | cache\_creation | cache\_read | diagnostics |
| --- | --- | --- | --- | --- |
| turn1 | opt-in（比較対象なし） | 6,275 | 0 | `null` |
| turn2 | systemそのまま・append | 162 | 6,275 | `null` |

turn1 で6,275トークンがキャッシュに書き込まれます（`cache_creation_input_tokens`）。turn2 では同じ6,275トークンが `cache_read_input_tokens` に乗ってヒットしました。`diagnostics` はどちらも `null`、つまり「分岐なし」です。キャッシュが効いているとき、diagnostics は静かなまま。

turn2 にも `cache_creation_input_tokens: 162` が出ています。append した分が新しくキャッシュされたものです。

### わざとキャッシュを壊してみる

正常系だけだと面白くないので、わざと壊します。system prompt の末尾に毎回違う timestamp を差し込んで、turn3 を投げました。レスポンスの主要なフィールドはこうでした。

| 項目 | 値 |
| --- | --- |
| `cache_read_input_tokens` | 0（キャッシュ全ミス） |
| `cache_creation_input_tokens` | 6,604 |
| `diagnostics.cache_miss_reason.type` | `system_changed` |
| `cache_missed_input_tokens` | 6,610 |

キャッシュは全ミスでした（`cache_read_input_tokens` が 0）。その原因を、diagnostics は `system_changed` と名指ししています。system の末尾に timestamp を1つ足しただけです。その小さな変更を、API がそのまま当ててきました。`cache_missed_input_tokens` は 6,610 で、分岐点より後ろの prefix がまるごと無効になった規模を表します。

## cache\_miss\_reason の型を自分のログと突き合わせる

返ってくる `type` は6種類。**最初の分岐だけ**を報告するので、まずそれを直す（後ろの分岐は隠れていることがある）。

prefix はこの順で前から一致が必要です。どこか1層が変わると、その層から後ろが全部キャッシュミスになります。`*_changed` の4型は、この並びのどの層で分岐したかに対応しています。

だから `cache_miss_reason` が指す最初の分岐を、手前から直すと効きます。

| type | 意味 | 直すこと |
| --- | --- | --- |
| `model_changed` | `model` が前回と違う（router/AB/fallbackで別モデルに） | キャッシュ会話の中ではモデルを固定する |
| `system_changed` | `system` が違う（timestamp等を差し込んだ） | systemはバイト安定の定数にし、動的データはbreakpoint後の最初のuserへ |
| `tools_changed` | `tools` の追加/削除/並べ替え、schemaの非決定的シリアライズ | 毎回同じtoolを固定順で、schemaはキーソート等で決定的に |
| `messages_changed` | model/system/toolsは一致だが過去メッセージを編集/切り詰めた | 履歴はappend-onlyで、assistant content や tool\_result は逐語で返す |
| `previous_message_not_found` | 渡した `previous_message_id` のフィンガープリントが無い | beta headerを毎回付ける、連続turnを時間的に近くに保つ |
| `unavailable` | 比較が作れなかった（後述の他パラメータ差分や、比較地平の外） | prompt関連パラメータをキャッシュ会話の間は固定する |

注意点が1つ。`*_changed` 系には `cache_missed_input_tokens` という整数が付きますが、これは**トークン化前のバイト長由来の概算**で、課金の数値ではありません。「どれだけのprefixが失われたか」の規模感として読む。`usage.input_tokens` と一致しないこともある（たまに超える）。

出典: <https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics>

## diagnostics と usage を一緒に読む

`diagnostics` は「リクエストが変わったか？」、`usage.cache_read_input_tokens` は「キャッシュがヒットしたか？」。この2つを並べると、見るべき場所が決まります。

| diagnostics | cache read tokens | 解釈 |
| --- | --- | --- |
| `null` | 高い | 正常。prefixが安定してヒットしている |
| `null` | 低い/ゼロ | リクエストは一致だがエントリが消えていた → turn間隔を詰めるか1h TTL |
| `*_changed` | 低い/ゼロ | 自分のバグ。`type` が示す原因を直す |
| `*_changed` | 高い | 稀。後ろで変化したが手前のbreakpointがヒット。直す価値は低い |

なお比較中や `previous_message_not_found` / `unavailable` のときは、この表の対象外です。

「自分のバグ」と「キャッシュエントリが消えただけ」を切り分けられるのが地味に効きます。この切り分けができないと、ただ消えただけなのにプロンプトを触って余計に壊す、という遠回りになりがちです。

## ハマりどころ

触る前に知っておくと事故らない点を、docsから先に拾っておきます（自分が踏んだら追記する）。

* **初回turnは `diagnostics: null` かつ read 0 が正常**。キャッシュは「書いている」ので、ここでトラブルシュートしようとすると無駄に悩む。
* **`previous_message_not_found` はリクエストが変わった証拠ではない**。beta header無し / 別workspace / 時間が空きすぎ、で出る。「自分のせいだ」と早とちりしない。
* **`unavailable` は一致していても出る**。model/system/toolsが一致でも、次のいずれかが違うと比較不能になる。
  + `tool_choice` / `thinking` / `context_management`
  + `output_config` / `output_format`
  + 有効な `anthropic-beta` ヘッダの集合
* **retentionが短い**。比較は連続した近いリクエスト同士で。バッチで間隔が空くと拾えない。

## まとめ

cache diagnostics は、prompt cache が効かないときの調査を「勘で潰す」から「最初の分岐点をAPIに聞く」へ変えるものでした。`diagnostics` で原因の種類を、`usage` でヒットの有無を、2軸で読むのが基本の型になりそうです。

まだbetaなので field名やsemanticsは変わりうるし、Bedrock/Vertexでは使えない。それでも、キャッシュ前提でコストを組んでいるなら、デプロイ前に `cache_miss_reason` を1回見ておくだけで景色は結構変わると思います。自分も次にキャッシュが崩れたら、まずこれを叩くようにします。

この記事の情報は2026年6月時点のスナップショットです。

## 参考

## 付録：再現スクリプト

この記事の turn1〜3 は、このスクリプト1本で回しています（SDK非依存・stdlibのみ）。`ANTHROPIC_API_KEY` を渡して実行すると、各ターンの usage と diagnostics を表示し、生JSONを `./out/` に保存します。

run-experiment.py（全文）

run-experiment.py

```
#!/usr/bin/env python3
"""cache diagnostics 検証スクリプト（SDK非依存・stdlibのみ）。

ANTHROPIC_API_KEY は環境変数か、リポジトリの .env から自動で読む。
実行: python3 run-experiment.py
"""
import json
import os
import sys
import time
import urllib.request

BETA = "cache-diagnosis-2026-04-07"
URL = "https://api.anthropic.com/v1/messages"

def load_dotenv():
    """スクリプトの場所から親方向に .env を探して環境変数へ。既存は上書きしない。"""
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (here, os.path.join(here, ".."), os.path.join(here, "..", "..")):
        path = os.path.join(cand, ".env")
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        break

load_dotenv()
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = os.environ.get("MODEL") or "claude-opus-4-8"

if not API_KEY:
    sys.exit("ANTHROPIC_API_KEY が未設定です（環境変数か .env に設定してください）。")

# キャッシュ最小トークン長を超えるよう、大きめの system prompt を作る。
PARA = (
    "This is a filler paragraph used to make the system prompt large enough to be cached. "
    "It repeats so the cacheable prefix comfortably exceeds the model minimum. "
)
DOC = PARA * 120  # 約数千トークン
SYSTEM_BASE = f"You are an AI assistant analyzing a large document. <document>{DOC}</document>"

os.makedirs(os.path.join(os.path.dirname(__file__), "out"), exist_ok=True)

def call(label, messages, system, prev_id):
    body = {
        "model": MODEL,
        "max_tokens": 256,
        "cache_control": {"type": "ephemeral"},
        "system": system,
        "messages": messages,
        "diagnostics": {"previous_message_id": prev_id},
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": BETA,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"\n### {label}: HTTP {e.code}\n{e.read().decode()}")
        return None

    with open(os.path.join(os.path.dirname(__file__), "out", f"{label}.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    usage = data.get("usage", {})
    print(f"\n### {label}")
    print("usage:", json.dumps({
        "input_tokens": usage.get("input_tokens"),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
        "output_tokens": usage.get("output_tokens"),
    }, ensure_ascii=False))
    print("diagnostics:", json.dumps(data.get("diagnostics"), ensure_ascii=False))
    return data

def assistant_text(data):
    if not data:
        return "..."
    for block in data.get("content", []):
        if block.get("type") == "text":
            return block["text"]
    return "..."

print(f"model={MODEL}  beta={BETA}")

# Turn 1: opt-in（比較対象なし → diagnostics は null。キャッシュは書き込み）
r1 = call("turn1-optin", [{"role": "user", "content": "Summarize section 1."}], SYSTEM_BASE, None)
if r1 is None:
    sys.exit("turn1 が失敗。モデル名/キー/beta の有効性を確認。")
time.sleep(1)

# Turn 2: 正常系（system 一致・append のみ → diagnostics null、cache_read が乗る）
msgs2 = [
    {"role": "user", "content": "Summarize section 1."},
    {"role": "assistant", "content": assistant_text(r1)},
    {"role": "user", "content": "Now summarize section 2."},
]
r2 = call("turn2-control", msgs2, SYSTEM_BASE, r1["id"])
time.sleep(1)

# Turn 3: わざと壊す（system に timestamp → system_changed が出る）
system_broken = SYSTEM_BASE + f"\n\nCurrent time: {time.time()}"
msgs3 = msgs2 + [
    {"role": "assistant", "content": assistant_text(r2)},
    {"role": "user", "content": "Now summarize section 3."},
]
call("turn3-break-system", msgs3, system_broken, r2["id"] if r2 else None)
```
