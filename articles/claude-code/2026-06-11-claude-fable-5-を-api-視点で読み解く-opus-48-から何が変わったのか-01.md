---
id: "2026-06-11-claude-fable-5-を-api-視点で読み解く-opus-48-から何が変わったのか-01"
title: "Claude Fable 5 を API 視点で読み解く — Opus 4.8 から何が変わったのか"
url: "https://zenn.dev/aiden_ai/articles/00fd9f3839b548"
source: "zenn"
category: "claude-code"
tags: ["CLAUDE-md", "API", "TypeScript", "zenn"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026/6/9、Anthropic が **Claude Fable 5**（`claude-fable-5`）を一般提供開始しました。これまで招待制だった Mythos 系の能力を、安全装置を載せて誰でも使えるようにしたモデルで、Anthropic が「一般提供したモデルの中で最も高性能」と位置づけています。

筆者も初日から1日触ってみたのですが、正直なところ Opus 4.8 との違いを「体感」としては掴みきれませんでした。**この違和感には明確な理由があり、それは Fable 5 の設計そのものに由来します。** 本記事はその理由を起点に、API を叩く開発者の視点で「Opus 4.8 から何が変わったのか」を、破壊的変更とコードを中心に整理します。

---

## なぜ「1日触っても違いが分からない」のか

先に結論を書くと、**Fable 5 の Opus 4.8 に対する優位は「難しく・長時間・自律的なタスク」に集中していて、短くスコープの明確なタスクでは両者はかなり近い**からです。

公開ベンチマークを並べると、差が出る領域がはっきりします。

| ベンチマーク | Fable 5 | Opus 4.8 | 性質 |
| --- | --- | --- | --- |
| SWE-bench Pro | **80.3%** | 69.2% | 長時間エージェントコーディング |
| FrontierCode (Cognition) | **29.3%** | 13.4% | フロンティアコーディング |
| 社内分析ベンチ | **90%超**（史上初の大台） | 〜80% | 複雑・長時間の分析タスク |
| フロンティア物理研究 | 推論トークン約1/3で同等以上 | — | 科学研究 |

長時間エージェントコーディング（SWE-bench Pro, FrontierCode）で10〜16ポイントの差がつく一方、日常的な「短い質問・要約・単発の実装」では Opus 4.8 と体感差が出にくい。つまり、**普段の使い方を1日繰り返しても差が立ち上がってこないのは、むしろ正常な観測結果**なのです。

差を引き出す条件は後述しますが、ここでは「Fable 5 は難問に最初の一手から全力を注いだときに初めて Opus を引き離す」とだけ押さえておきます。

---

## 基本スペックと位置づけ

| 項目 | Claude Fable 5 |
| --- | --- |
| モデル ID | `claude-fable-5` |
| コンテキストウィンドウ | 1M トークン（**最大かつデフォルト**） |
| 最大出力 | 128K トークン |
| 料金 | **$10 / $50** per 1M tokens（入力 / 出力） |
| 思考 | **常時ON**（無効化不可） |
| データ保持 | **30日保持が必須**（ZDR 不可） |

Opus 4.8 が $5 / $25 なので、**料金は単純比較で2倍**。さらに後述のトークナイザ変更でトークン数自体が増えるため、コスト感はそれ以上に開きます。

なお `claude-mythos-5` という同等モデルが Project Glasswing 経由で存在しますが、能力・料金・API 挙動は Fable 5 と同一で、ID が違うだけです。一般の開発者は `claude-fable-5` を使います。

---

## 破壊的変更①：思考は常時ON、`thinking` は省略する

Opus 4.7/4.8 では `thinking` を省略すると思考なしで動きました。**Fable 5 では思考が常時オン**で、`thinking` パラメータの扱いが変わります。

* `thinking` を**省略**すれば adaptive thinking が自動適用される
* `{"type": "adaptive"}` を明示してもよい
* **`{"type": "disabled"}` は 400 エラー**（Opus 4.8 では受理されるが Fable 5 では拒否）
* `{"type": "enabled", "budget_tokens": N}` も 400（`budget_tokens` は完全廃止）

思考の「深さ」は `thinking` ではなく **`output_config.effort`** で制御します。

```
import anthropic

client = anthropic.Anthropic()

# 最小形：thinking は書かない。深さは effort で。
response = client.messages.create(
    model="claude-fable-5",
    max_tokens=16000,
    output_config={"effort": "high"},  # low | medium | high | xhigh | max
    messages=[{"role": "user", "content": "..."}],
)
```

### effort の選び方

`effort` はコスト・レイテンシ・知能のメインスイッチです。Anthropic の推奨は以下。

| effort | 用途 |
| --- | --- |
| `high` | 多くのタスクの既定 |
| `xhigh` | 最も能力が要るコーディング・エージェント用途 |
| `medium` / `low` | ルーチンワーク、インタラクティブで速さ優先 |
| `max` | 最難・レイテンシ非依存の検証用途 |

重要なのは、**Fable 5 は `low` でも前世代の `xhigh`/`max` を上回ることがある**という点。高 effort で「タスクに不要な深掘り・リファクタ」をし始めたら、effort を下げるのが正解です。

---

## 破壊的変更②：Protected thinking — 生の思考は返らない

Fable 5 は `protected_thinking` ポリシーを持ち、**生の思考連鎖（raw chain of thought）はレスポンスに一切含まれません。** ただし返ってくるのは暗号化ブロックではなく、通常の `thinking` ブロックです。

* `display: "summarized"` → 読める**要約**が返る
* `display: "omitted"`（デフォルト、Opus 4.8/4.7 と同じ）→ `thinking` フィールドは空文字
* どちらでも思考は実行され、課金も同じ。`display` は表示の有無を変えるだけ

```
# 思考の要約をユーザーに見せたい場合
response = client.messages.create(
    model="claude-fable-5",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "xhigh"},
    messages=[{"role": "user", "content": "..."}],
)

for block in response.content:
    if block.type == "thinking":
        print("[思考の要約]", block.thinking)
    elif block.type == "text":
        print(block.text)
```

### 思考ブロックの往復ルール（マルチターンで重要）

同一モデルで会話を継続するときは、**受け取った `thinking` ブロックを改変せずそのまま送り返す**必要があります。`thinking` が空文字のブロックも含めてそのまま戻します。API が弾くのは「改変されたブロック」であって「読んだだけのブロック」ではありません。

別モデル（例：Opus 4.8 にフォールバック）へ会話を渡す場合、Fable 5 の protected thinking ブロックは**プロンプトから黙って落とされます**。落ちる処理は課金前に行われるため、`usage.input_tokens` が下がるだけで、こちらでストリップする必要はありません。

---

## 破壊的変更③：新トークナイザ — 同じ内容で約30%増

Fable 5 は新しいトークナイザを採用しており、**同じ内容が Opus 系より約30%多くトークン化されます**（ワークロード次第で変動）。課金はトークン単価なので、ワークロードを変えなくても移行だけでコストが上がり得ます。さらに単価自体も2倍なので、コスト見積もりは必ず測り直してください。

`count_tokens` に `model: "claude-fable-5"` を渡すと、**新旧両方のトークナイザでの数値**が返るので、移行前に差分を測れます。

```
resp = client.messages.count_tokens(
    model="claude-fable-5",
    messages=[{"role": "user", "content": open("CLAUDE.md").read()}],
)

print(resp.input_tokens)                  # 新トークナイザ（課金対象）
print(resp.input_tokens_prior_tokenizer)  # 旧世代トークナイザでの同一リクエスト

delta = resp.input_tokens / resp.input_tokens_prior_tokenizer - 1
print(f"トークン増加率: {delta:.1%}")
```

---

## 破壊的変更④：`refusal` stop reason とフォールバック

Fable 5 は受信リクエストに安全分類器を走らせ、研究レベルの生物学・大半のサイバーセキュリティ領域を対象に**拒否**することがあります。良性の隣接タスク（セキュリティツール、ライフサイエンス）でも稀に誤検知が起こり得るため、本番コードでは必ずハンドリングが必要です。Anthropic によれば、この安全装置が発動するのは**平均してセッションの5%未満**です。

重要なのは、**拒否は HTTP 200 で返り、`stop_reason: "refusal"` になる**こと。`content[0]` を無条件で読むコードは壊れます。

```
response = client.messages.create(
    model="claude-fable-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}],
)

# content を読む前に必ず stop_reason を見る
if response.stop_reason == "refusal":
    # 出力前なら content は空（課金なし）、
    # ストリーム途中なら部分出力（課金あり・破棄する）
    cat = response.stop_details.category if response.stop_details else None
    handle_refusal(cat)  # "cyber" | "bio" | "reasoning_extraction" | None
else:
    print(response.content[0].text)
```

拒否されたリクエストを別モデルで救う方法は3つあります。優先度順に紹介します。

### 方式1：サーバーサイド `fallbacks`（推奨・1往復）

beta パラメータで代替モデルを指定すると、拒否時に API が**同一リクエストで次のモデルを実行**して返してくれます。クライアント側のロジック不要。

```
response = client.beta.messages.create(
    model="claude-fable-5",
    max_tokens=1024,
    betas=["server-side-fallback-2026-06-01"],
    fallbacks=[{"model": "claude-opus-4-8"}],  # 現状の対応先は opus-4-8
    messages=[{"role": "user", "content": "Hello, Claude"}],
)

# 切り替わったかは fallback ブロックで分かる
for block in response.content:
    if block.type == "fallback":
        print(f"{block.from_.model} が拒否 → {block.to.model} が継続")
```

ポイント:

* beta ヘッダは**ちょうど `server-side-fallback-2026-06-01`**。別の日付値だと 400
* ポリシー拒否のときだけ発火。レート制限・過負荷・サーバエラーは**フォールバックしない**
* 一度フォールバックした会話は、以後の非ストリーミングリクエストで約1時間フォールバック先に固定（sticky routing）
* Batches API では拒否、Bedrock/Vertex では非対応（その場合は方式2）

### 方式2：SDK クライアントミドルウェア（Bedrock/Vertex 向け）

サーバーサイド fallbacks が使えない環境では、SDK のミドルウェアを登録すると、ストリーミングも含めて拒否時に自動リトライしてくれます。

```
from anthropic import Anthropic, BetaFallbackState, BetaRefusalFallbackMiddleware

client = Anthropic(
    middleware=[BetaRefusalFallbackMiddleware([{"model": "claude-opus-4-8"}])]
)

# state は会話ごとに1つ作る（受理したモデルに後続ターンを固定する）
state = BetaFallbackState()
with state:
    response = client.beta.messages.create(
        model="claude-fable-5",
        max_tokens=1024,
        messages=messages,
    )
```

`BetaFallbackState` は**会話ごとに1個**。使い回すと無関係なスレッドまで固定されてしまいます。TypeScript / Go / C# も同等の API があり、各 SDK の `examples/` にフォールバックの実例があります。

### 方式3：手組みリトライ + fallback credit（生 HTTP 用）

`stop_reason` で拒否を検知し、会話をそのまま別モデル（`claude-opus-4-8` など）へ再送します。Fable 5 の protected thinking ブロックは他モデル側で黙って無視されるので、ストリップ不要。`fallback-credit-2026-06-01` ヘッダを付けると、再送時のキャッシュ書き込みコストが軽減されます。詳細は移行ガイドの refusal セクション参照。

---

## 破壊的変更⑤：30日データ保持が必須（ZDR 不可）

地味ですが運用に効く差分です。**Fable 5 はゼロデータ保持（ZDR）では利用できません。** 安全分類器の運用にプロンプト・出力の保持が必要なためです。組織のデータ保持設定が30日未満だと、**正常なペイロードでも全リクエストが `400 invalid_request_error`** になります。

```
# 移行直後に原因不明の 400 が出たら、まず組織のデータ保持設定を疑う
400 invalid_request_error
```

Opus 4.8 は ZDR 可なので、**コンプライアンス要件で ZDR が必須の組織は、そもそも Fable 5 を使えない**点に注意。これは「使い分け」ではなく「使える / 使えない」の線引きになります。

---

## アシスタント prefill は不可

Opus 4.6 以降と同じく、**最後のアシスタントターンへの prefill は 400**。JSON 等の出力形を強制したい場合は `output_config.format`（structured outputs）かシステムプロンプトの指示に置き換えます。

```
response = client.messages.create(
    model="claude-fable-5",
    max_tokens=1024,
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
                "additionalProperties": False,
            },
        }
    },
    messages=[{"role": "user", "content": "名前を抽出して"}],
)
```

---

## 「差を引き出す」ための実装パターン

冒頭の「違いを感じない」問題への答えです。Fable 5 の真価は**難問に最初の一手から全力を注いだとき**に出ます。Anthropic の移行ガイドが挙げる前提を、実装に落とすとこうなります。

### 1. 最初の1ターンでタスク全体を渡し、high〜xhigh で回す

小出しにすると性能も効率も落ちます。曖昧・過小指定のプロンプトを複数ターンで渡すのは Fable 5 では逆効果。ゴール・意図・制約を最初のターンに集約します。

```
response = client.messages.create(
    model="claude-fable-5",
    max_tokens=64000,             # 高 effort では潤沢に
    output_config={"effort": "xhigh"},
    messages=[{"role": "user", "content": FULL_TASK_SPEC}],
)
```

### 2. 1リクエストが数分〜15分走るのが正常

難タスクでは単発リクエストが何分も走ります（コンテキスト収集→構築→自己検証）。**タイムアウト・ストリーミング・進捗UIを前提に設計**し、ブロックせず非同期にチェックインする構造にします。

```
# 大きな max_tokens は必ずストリーミング（非ストリーミングは HTTP タイムアウトのリスク）
with client.messages.stream(
    model="claude-fable-5",
    max_tokens=64000,
    output_config={"effort": "xhigh"},
    messages=[{"role": "user", "content": FULL_TASK_SPEC}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()
```

### 3. 過剰なお膳立てプロンプトはむしろ品質を下げる

前世代向けの「ステップを逐一指示する」スキャフォルディングは Fable 5 では出力品質を下げます。移行時は、旧来の手取り足取りプロンプトを**外して** A/B するのが推奨。ゴールと制約だけ渡し、手順の列挙はやめる方向です。

### 4. 長時間ランの安定化に効くシステムプロンプト

移行ガイドが具体的な system プロンプト断片を推奨しています。代表的なものを意訳で挙げます（そのまま使うより、ワークロードに合わせて調整推奨）。

* **過剰計画の抑制**：「行動できる情報が揃ったら行動する。既に確定した事実の再導出や、選ばない選択肢の列挙はしない」
* **不要な後始末の禁止**：「タスクが要求していない機能追加・リファクタ・抽象化はしない。バグ修正に周辺の掃除は不要」
* **進捗主張の裏取り**：「進捗を報告する前に、各主張をこのセッションのツール結果と突き合わせる。検証できていないなら、その旨を明示する」
* **境界の明示**：「ユーザーが問題を説明・質問・思考の整理をしているだけなら、成果物は『あなたの評価』。修正は依頼されるまで適用しない」

---

## 引き継がれるもの（変わらない点）

Messages API とツール利用のパターンは Opus 系と同じです。以下は Fable 5 でもそのまま使えます。

* `output_config.effort`（`low`〜`max`）
* Task Budgets（beta `task-budgets-2026-03-13`）
* Compaction（beta `compact-2026-01-12`）
* メモリツール、context editing によるツール結果クリア
* 高解像度ビジョン（Opus 4.7+ と同様、長辺2576pxまで）

---

## 移行チェックリスト（Opus 4.8 → Fable 5）

実装を移すときの必須項目（`[必須]` は怠ると 400 等で壊れる）と推奨項目（`[調整]`）。

* `[必須]` モデル ID を `claude-fable-5` に
* `[必須]` `thinking={"type":"disabled"}` を削除（Fable 5 では 400）
* `[必須]` `thinking={"type":"enabled","budget_tokens":N}` を削除し、深さは `effort` で制御
* `[必須]` アシスタント prefill を structured outputs かシステム指示に置換
* `[必須]` 組織のデータ保持が30日以上か確認（ZDR だと全リクエスト 400）
* `[必須]` `content` を読む前に `stop_reason == "refusal"` を分岐。フォールバック戦略（方式1〜3）を1つ選ぶ
* `[調整]` トークン数・コンテキスト予算・`max_tokens`・コストを再測定（`count_tokens` は新旧両方返す）
* `[調整]` 推論をUIに出すなら `display: "summarized"` を明示
* `[調整]` 数分単位のターンを前提に、タイムアウト・ストリーミング・進捗UIを用意
* `[調整]` low/medium も含めて effort をスイープ。高 effort で不要な後始末が出たら抑制プロンプトを追加
* `[調整]` 旧モデル向けの過剰スキャフォルディングを外して A/B

---

## まとめ：いつ Fable 5 を使うか

* **Fable 5 が効くのは「難しく・長時間・自律的」なタスク** — 長時間エージェントコーディング、深い分析、フロンティア科学。最初の一手から全力（full spec + high/xhigh）で投げたときに Opus を引き離す
* **短くスコープの明確なタスクでは Opus 4.8 とほぼ互角** — しかも料金は半分、ZDR 可。日常用途は Opus 4.8 で十分
* 賢い運用は**タスクでルーティング**：難所は Fable 5、それ以外は Opus 4.8
* API レベルでは「思考常時ON / protected thinking / 新トークナイザ / refusal 分岐 / 30日保持必須」の5点が Opus 4.8 との実装上の主要差分

「1日触って違いが分からない」のは正しい観測でした。Fable 5 は、こちらが本気の難問をぶつけて初めて本気を返してくるモデルです。

---

### 参考
