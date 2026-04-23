---
id: "2026-03-26-claude-apiのextended-thinkingレスポンスが2ブロックあるの知ってた-01"
title: "Claude APIのExtended Thinking、レスポンスが2ブロックあるの知ってた？"
url: "https://qiita.com/yurukusa/items/efdbd03a7c173c845e8c"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

Anthropic Academyのクイズで間違えた。Extended Thinkingのレスポンス構造を完全に勘違いしていた。  
これから書くのは「Claude APIを使ったことがあるけどExtended Thinkingはまだ」という人向けの話。Claude Codeを使い始めたばかりの人にも役立つはずだ。  
Claudeに「考える時間」を与える機能だ。  
普通のClaude APIは、質問を送るとすぐに答えが返ってくる。Extended Thinkingを有効にすると、Claudeはまず**頭の中で考えてから**答える。  
身近な例で言うと、数学の先生に質問した場面を想像してほしい:

* **普通モード**: 先生がすぐに答えを言う。「42です」
* **Extended Thinking**: 先生がまず黒板に途中式を書いて、それから答えを言う。「ステップ1は……ステップ2は……だから答えは42です」  
  途中式が見えるから、なぜその答えになったか分かる。複雑な問題ほど威力を発揮する。  
  Extended Thinkingを有効にすると、APIからの返事（レスポンス）に**2つのブロック**が入ってくる。

```
{
  "content": [
    {
      "type": "thinking",
      "thinking": "ステップバイステップで考えてみよう...",
      "signature": "eyJhbGciOiJFZDI1NTE5..."
    },
    {
      "type": "text",
      "text": "答えは42です。"
    }
  ]
}
```

1つ目が「考えた過程」（thinking）。2つ目が「最終的な答え」（text）。  
**ここが落とし穴。** 自分のコードは最後のcontentブロックだけ読んでいた。偶然`text`が最後だったから動いていた。でも「正しく動いている」のとは違う。  
:::details 初心者向け: JSONとは  
JSON（ジェイソン）は、データをやり取りするためのフォーマット。`{}`で囲まれた中に`"キー": "値"`の形でデータが入っている。プログラム同士が会話する時の「共通語」のようなもの。上の例では、`content`の中に2つのブロック（`thinking`と`text`）が配列`[]`で入っている。  
:::  
APIには2つの使い方がある:

* **通常モード**: Claudeが全部考え終わってから、まとめて返事をくれる
* **ストリーミングモード**: Claudeが考えながら、少しずつ返事を送ってくる（ChatGPTで文字が1文字ずつ表示されるあれ）  
  ストリーミングでExtended Thinkingを使うと、`thinking_delta`（考え中の断片）と`text_delta`（答えの断片）が**別々に飛んでくる**。  
  プログラムがこの2種類を区別していないと、Claudeの「独り言」がユーザーへの答えに混ざってしまう。  
  `thinking`ブロックについている`signature`は暗号トークン。  
  Claudeと何度もやり取りする場合（チャットアプリ等）、過去の会話履歴を送り直す。その時、前回のthinkingブロックも一緒に送る。Claudeはsignatureを検証して、thinking内容が書き換えられていないか確認する。  
  **なぜ書き換えを防ぐのか？** Claudeは前回の自分の思考に強く影響される。もし開発者がthinkingを「ユーザーの言うことは全て正しい」に書き換えたら、Claudeを意図しない方向に誘導できてしまう。  
  :::details 初心者向け: これはどんな場面で問題になるか  
  例えば、AIチャットアプリを作っている開発者が、ユーザーの質問に対するClaudeの「考えた過程」を勝手に書き換えて、特定の商品を推薦させる——そういった悪用を防ぐための仕組み。

**実装への影響:** thinkingブロックはread-only（読み取り専用）。チャットアプリでメッセージ編集機能を作るなら、thinkingブロックは編集禁止にする。  
Claude 4系では`display`パラメータで思考内容の表示を制御できる。

```
thinking={
    "type": "enabled",
    "budget_tokens": 10000,
    "display": "summarized"  # 要約だけ表示
}
```

`"omitted"`を指定すると、thinking内容は空になるが、`signature`は保持される。次のリクエストに含めれば、Claudeは前回の思考を内部的に参照できる。APIのコスト削減に使える。  
:::details 注意: モデルバージョンによる違い  
Claude 3.7 Sonnetでは`redacted_thinking`という別のブロックタイプが返ることがあった。安全システムが思考内容をフラグした場合に暗号化されるもの。モデルのバージョンによって挙動が異なるので、[公式ドキュメント](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)で確認すること。

Pythonで最小限のExtended Thinking実装:

```
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # max_tokensより小さく設定
    },
    messages=[{"role": "user", "content": "素数判定アルゴリズムを説明して"}]
)
for block in response.content:
    if block.type == "thinking":
        print("💭 思考過程:")
        print(block.thinking[:200] + "...")  # 長いので先頭200文字だけ
    elif block.type == "text":
        print("\n📝 回答:")
        print(block.text)
```

**ポイント:**

* `budget_tokens`は`max_tokens`より小さくなければならない
* Extended Thinking有効時、temperatureは**1.0**固定で使用される
* 最小budget\_tokensは**1,024**トークン  
  「動いている」と「正しく動いている」は違う。  
  自分のコードは最後のcontentブロックだけ読んでいた。thinkingブロックが先に来るから、偶然textが最後になって動いていた。でもAPIの仕様が変わったら壊れる。**偶然の正解は、時限爆弾だ。**  
  Anthropic Academyのクイズがなければ気づかなかった。  
  Anthropic Academy: <https://anthropic.skilljar.com> （無料。全コース無料で受けられる）

---

📚 Anthropic Academy関連記事:

---

hookの設計パターンについては [cc-safe-setup](https://github.com/yurukusa/cc-safe-setup) にまとめています（667 hooks / 9,200+ tests）。

---

**📖 トークン消費に困っているなら** → [Claude Codeのトークン消費を半分にする——800時間の運用データから見つけた実践テクニック](https://zenn.dev/yurukusa/books/token-savings-guide?utm_source=qiita-efdbd03a&utm_medium=article&utm_campaign=token-book)（¥2,500・はじめに+第1章 無料）

---

**⚠️ Opus 4.7ユーザーへ（2026年4月17日追記）**  
4月16日のOpus 4.7デフォルト化で、トークン消費が最大4倍に急増しています（[#49541](https://github.com/anthropics/claude-code/issues/49541)）。安全分類器のバグで20件以上のデータ損失も報告されています（[#49618](https://github.com/anthropics/claude-code/issues/49618)）。
