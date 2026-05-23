---
id: "2026-05-22-claude-api-cache-diagnostics入門-プロンプトキャッシュミスを即座に診断す-01"
title: "Claude API Cache Diagnostics入門 — プロンプトキャッシュミスを即座に診断する"
url: "https://qiita.com/kai_kou/items/3a781c036704e984638f"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Python", "TypeScript", "qiita"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

![Cache Diagnosticsの概念図 — 2つのAPIリクエストを比較してキャッシュミス原因を特定する](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-cache-diagnostics-api-guide/01-hero.png)

## はじめに

Claude APIのプロンプトキャッシュ（Prompt Caching）は、同一プレフィックスを持つリクエストの入力トークンコストを最大90%削減できる強力な機能です。しかし、キャッシュが**サイレントにミスする**という問題が開発現場で頻繁に発生します。

プロンプトの先頭がバイト単位で一致しなければキャッシュはヒットしません。システムプロンプトにタイムスタンプを埋め込んだ、ツールの定義順を変えた、会話履歴を誤ってトリミングした——どれか一つのミスで`cache_read_input_tokens`がゼロになりますが、**何が変わったのかは分かりません**。

2026年5月にAnthropicが公開ベータとしてリリースした**Cache Diagnostics（キャッシュ診断）**はこの問題を解決します。直前のレスポンスIDを渡すだけで、APIが2つのリクエストを比較して「どこで乖離が起きたか」を教えてくれます。

### この記事で学べること

- Cache Diagnosticsの仕組みと有効化方法
- PythonおよびTypeScriptでの実装パターン
- `cache_miss_reason`の種類と具体的な対処法
- `diagnostics`と`usage`を組み合わせた読み方

### 対象読者

- Claude APIのプロンプトキャッシュを活用しているエンジニア
- キャッシュが想定どおりにヒットしない問題を抱えているエンジニア
- コスト最適化のためにキャッシュ効率を改善したい開発者

### 前提条件

- Anthropic APIキーを取得済みであること
- Python 3.9+またはTypeScript環境が構築済みであること
- `anthropic`パッケージ（最新版）がインストール済みであること

---

## TL;DR

- **ベータヘッダー** `cache-diagnosis-2026-04-07` を付与してリクエストする
- 初回ターン: `diagnostics.previous_message_id: null` でオプトイン
- 2回目以降: 前回レスポンスの `id` を `diagnostics.previous_message_id` に渡す
- レスポンスの `diagnostics.cache_miss_reason.type` でミス原因を特定できる
- Claude APIのみ対応（Amazon Bedrock・Vertex AIは非対応）

---

## Cache Diagnosticsとは

[Cache Diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics)は、プロンプトキャッシュミスの原因を診断するためのベータ機能です。

### 解決する課題

プロンプトキャッシュは**リクエストの先頭部分がバイト単位で完全一致**した場合にのみヒットします。以下の些細な変更がサイレントにキャッシュを無効化します：

- システムプロンプトへのリクエストIDや日時の埋め込み
- ツール定義のJSON順序の変動（非決定論的なシリアライズ）
- 会話履歴のトリミングや並び替え
- A/Bテストやルーターによるモデルの切り替え

従来はこれらを`usage.cache_read_input_tokens`が0になることで検知するしかなく、何が原因か特定できませんでした。

### 仕組み

![Cache Diagnosticsのフィンガープリント比較フロー](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-cache-diagnostics-api-guide/02-architecture.png)

Cache Diagnosticsはリクエストごとに**軽量なフィンガープリント**をAPIサーバーに保存します。フィンガープリントにはハッシュ値とトークン数の推定値のみが含まれ、プロンプトの生テキストは一切保存されません（[Zero Data Retention対象](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics#data-retention)）。

次回リクエスト時に前回のレスポンスIDを指定すると、APIが2つのフィンガープリントを比較して最初の乖離点を報告します。

---

## 有効化方法

### ベータヘッダーの追加

すべてのリクエストに以下のベータヘッダーを付与します：

```
anthropic-beta: cache-diagnosis-2026-04-07
```

### パラメータ

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `diagnostics.previous_message_id` | `null` | 初回ターン（比較なし、フィンガープリントのみ登録） |
| `diagnostics.previous_message_id` | 前回の `id` | 2回目以降（比較を実行） |

---

## 基本的な実装

### Python

```python
import anthropic

client = anthropic.Anthropic()

SYSTEM = "あなたは大規模ドキュメントを解析するAIアシスタントです。<document>...</document>"

# Turn 1: オプトイン（比較なし、フィンガープリントのみ登録）
r1 = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system=SYSTEM,
    messages=[{"role": "user", "content": "セクション1を要約してください。"}],
    diagnostics={"previous_message_id": None},
    betas=["cache-diagnosis-2026-04-07"],
)
print(f"Turn 1 id: {r1.id}")

# Turn 2: 前回のIDを渡して比較を実行
r2 = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system=SYSTEM,
    messages=[
        {"role": "user", "content": "セクション1を要約してください。"},
        {"role": "assistant", "content": r1.content},
        {"role": "user", "content": "続いてセクション2を要約してください。"},
    ],
    diagnostics={"previous_message_id": r1.id},
    betas=["cache-diagnosis-2026-04-07"],
)

diagnostics = r2.diagnostics
if diagnostics is None:
    print("キャッシュヒット（乖離なし）")
elif diagnostics.cache_miss_reason is None:
    print("比較処理中（次のターンで確認）")
else:
    print(f"キャッシュミス原因: {diagnostics.cache_miss_reason.type}")
```

### TypeScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();
const SYSTEM = "あなたは大規模ドキュメントを解析するAIアシスタントです。<document>...</document>";

// Turn 1: オプトイン
const r1 = await client.beta.messages.create({
  model: "claude-opus-4-7",
  max_tokens: 1024,
  cache_control: { type: "ephemeral" },
  system: SYSTEM,
  messages: [{ role: "user", content: "セクション1を要約してください。" }],
  diagnostics: { previous_message_id: null },
  betas: ["cache-diagnosis-2026-04-07"],
});

// Turn 2: IDを渡して比較
const r2 = await client.beta.messages.create({
  model: "claude-opus-4-7",
  max_tokens: 1024,
  cache_control: { type: "ephemeral" },
  system: SYSTEM,
  messages: [
    { role: "user", content: "セクション1を要約してください。" },
    { role: "assistant", content: r1.content },
    { role: "user", content: "続いてセクション2を要約してください。" },
  ],
  diagnostics: { previous_message_id: r1.id },
  betas: ["cache-diagnosis-2026-04-07"],
});

if (r2.diagnostics === null) {
  console.log("キャッシュヒット（乖離なし）");
} else if (r2.diagnostics.cache_miss_reason === null) {
  console.log("比較処理中");
} else {
  console.log(`キャッシュミス原因: ${r2.diagnostics.cache_miss_reason.type}`);
}
```

---

## マルチターン会話ループへの組み込み

実際のアプリケーションでは、会話ループに組み込んで継続的にキャッシュ効率を監視します。

```python
import anthropic

client = anthropic.Anthropic()
SYSTEM = "あなたは大規模ドキュメントを解析するAIアシスタントです。<document>...</document>"

messages = []
prev_id = None  # 初回はNoneでオプトイン

user_prompts = [
    "セクション1を要約してください。",
    "続いてセクション2を。",
    "セクション3の要点を教えてください。",
]

for i, user_message in enumerate(user_prompts):
    messages.append({"role": "user", "content": user_message})

    r = client.beta.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        cache_control={"type": "ephemeral"},
        system=SYSTEM,
        messages=messages,
        diagnostics={"previous_message_id": prev_id},
        betas=["cache-diagnosis-2026-04-07"],
    )

    # キャッシュミスを検出してログ出力
    if r.diagnostics is not None and r.diagnostics.cache_miss_reason is not None:
        reason = r.diagnostics.cache_miss_reason
        print(f"[Turn {i + 1}] キャッシュミス: {reason.type}")
        if hasattr(reason, "cache_missed_input_tokens"):
            print(f"  影響トークン数(推定): {reason.cache_missed_input_tokens}")

    messages.append({"role": "assistant", "content": r.content})
    prev_id = r.id  # 次のターンに渡す
```

---

## レスポンス形式

`diagnostics`フィールドは4つの状態を持ちます。

| `diagnostics`の値 | 意味 |
|-------------------|------|
| フィールド自体が存在しない | ベータヘッダーが付与されていないか、`diagnostics`パラメータを渡していない |
| `null` | 初回ターン（比較なし）、または比較して乖離が検出されなかった |
| `{"cache_miss_reason": null}` | 比較処理がまだ完了していない（レスポンス生成が非常に速かった場合）。次のターンで確認する |
| `{"cache_miss_reason": {...}}` | 乖離が検出された。`type`フィールドで原因を確認する |

乖離が検出された場合のレスポンス例：

```json
{
  "id": "msg_01Xyz...",
  "diagnostics": {
    "cache_miss_reason": {
      "type": "system_changed",
      "cache_missed_input_tokens": 41850
    }
  },
  "usage": {
    "input_tokens": 42,
    "cache_read_input_tokens": 0,
    "cache_creation_input_tokens": 41850,
    "output_tokens": 210
  }
}
```

`cache_missed_input_tokens`は乖離点以降のトークン数の推定値です。実際の課金トークン数ではなく、影響の大きさを把握するための指標として使用します。

---

## キャッシュミス理由（`cache_miss_reason`）の種類と対処法

`cache_miss_reason.type`は最初の乖離点のみを報告します。原因を修正したら、その背後に隠れていた別の乖離が現れる可能性があります。

| type | 原因 | 対処法 |
|------|------|--------|
| `model_changed` | リクエスト間でモデルが異なる（A/Bテスト・ルーター等） | キャッシュを使う会話では同一モデルを固定する |
| `system_changed` | システムプロンプトにタイムスタンプやリクエストIDが埋め込まれている | システムプロンプトを定数化し、動的な値はキャッシュブレークポイント以降の最初のユーザーメッセージに移す |
| `tools_changed` | ツール定義の順序が変わった、またはスキーマのJSONが非決定論的にシリアライズされた | ツール配列を固定順序にし、JSONキーをソートして決定論的にシリアライズする |
| `messages_changed` | モデル・システム・ツールは一致しているが、メッセージ履歴が変更・削除・並び替えされた | 会話履歴を追記専用として扱い、アシスタントの応答と`tool_result`を逐語的にエコーバックする |
| `previous_message_not_found` | 指定したIDのフィンガープリントが存在しない | ベータヘッダーを毎ターン付与し、ターン間の時間を短くする |
| `unavailable` | 診断情報が取得できなかった（ターンが長すぎる、または他のパラメータが異なる） | プロンプト関連パラメータ（`tool_choice`・`thinking`等）を会話全体で固定する |

### 最も多い原因：`system_changed`への対処

```python
import time

# NG: タイムスタンプがキャッシュを毎回無効化する
system_bad = f"あなたはAIアシスタントです。リクエストID: {time.time()}"

# OK: 動的な値はキャッシュブレークポイント以降に移す
system_good = "あなたはAIアシスタントです。"

# 動的な値はユーザーメッセージの先頭に付加する
user_message_with_context = f"[リクエストID: {time.time()}]\n{actual_user_message}"
```

---

## `diagnostics`と`usage`の組み合わせ

2つのフィールドを組み合わせることで、キャッシュの状態をより正確に把握できます。

| `diagnostics` | `cache_read_input_tokens` | 解釈 |
|---------------|--------------------------|------|
| `null` | 高い | 正常動作。プレフィックスが一致してキャッシュヒット |
| `null` | 低い/0 | リクエストは一致しているが、キャッシュエントリの有効期限が切れた。ターン間の時間を短縮するか[1時間キャッシュTTL](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration)の利用を検討する |
| `*_changed`型 | 低い/0 | バグあり。`type`が示す原因を修正する |
| `*_changed`型 | 高い | まれなケース。変更が後半のプロンプトで発生したが、より前の`cache_control`ブレークポイントはヒットしている |

---

## ストリーミングとの組み合わせ

ストリーミングレスポンスでは、`diagnostics`は`message_start`イベントで返されます。

```python
import anthropic

client = anthropic.Anthropic()
SYSTEM = "あなたはAIアシスタントです。<document>...</document>"

# Turn 1（通常リクエスト）
r1 = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system=SYSTEM,
    messages=[{"role": "user", "content": "セクション1を要約してください。"}],
    diagnostics={"previous_message_id": None},
    betas=["cache-diagnosis-2026-04-07"],
)

# Turn 2（ストリーミング）
with client.beta.messages.stream(
    model="claude-opus-4-7",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system=SYSTEM,
    messages=[
        {"role": "user", "content": "セクション1を要約してください。"},
        {"role": "assistant", "content": r1.content},
        {"role": "user", "content": "続いてセクション2を。"},
    ],
    diagnostics={"previous_message_id": r1.id},
    betas=["cache-diagnosis-2026-04-07"],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    print()
    r2 = stream.get_final_message()

# diagnosticsはmessage_startで到着し、最終メッセージに引き継がれる
if r2.diagnostics and r2.diagnostics.cache_miss_reason:
    print(f"キャッシュミス原因: {r2.diagnostics.cache_miss_reason.type}")
```

---

## 制限事項

| 制限 | 内容 |
|------|------|
| ベータ機能 | フィールド名や仕様はGA前に変更される可能性あり |
| Claude APIのみ | Amazon Bedrock・Vertex AIは非対応 |
| フィンガープリントの保存期限 | 短期間のみ保存。ターン間が長すぎると`previous_message_not_found`になる |
| 同一ワークスペース | 異なる組織・ワークスペースのIDは参照できない |
| 比較ホライズン | 非常に長い会話で変更が深い位置にある場合、`unavailable`になることがある |

---

## まとめ

Claude API Cache Diagnosticsのポイントをまとめます。

- **有効化は簡単**: `anthropic-beta: cache-diagnosis-2026-04-07`ヘッダーと`diagnostics`パラメータを追加するだけ
- **最も多い原因は`system_changed`**: システムプロンプトへの動的な値の混入を防ぐ設計が重要
- **`tools_changed`は見落としがち**: ツール定義のJSON順序・シリアライズを固定する
- **`diagnostics`と`usage`の両方を確認**: 組み合わせることでキャッシュの状態を正確に把握できる
- **ゼロデータリテンション対応**: フィンガープリントにはハッシュ値のみが含まれ、プロンプトの生テキストは保存されない

プロンプトキャッシュのコスト最適化を進めている場合、Cache Diagnosticsはキャッシュ効率の定常的な監視ツールとして活用できます。ベータ期間中は仕様変更の可能性があるため、[公式リリースノート](https://platform.claude.com/docs/en/release-notes/overview)を定期的に確認することを推奨します。

## 参考リンク

- [Cache diagnostics — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics) — 公式ドキュメント
- [Prompt caching — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) — プロンプトキャッシュの基本
- [Beta headers — Claude API Docs](https://platform.claude.com/docs/en/api/beta-headers) — ベータヘッダーの一覧
- [API and data retention — Claude API Docs](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) — データ保持ポリシー
