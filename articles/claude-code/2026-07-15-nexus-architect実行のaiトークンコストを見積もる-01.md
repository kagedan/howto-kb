---
id: "2026-07-15-nexus-architect実行のaiトークンコストを見積もる-01"
title: "「nexus-architect」実行のAIトークンコストを見積もる"
url: "https://zenn.dev/scalar_sol_blog/articles/0acf5738bfb923"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-rss"
query: ""
---

この記事では、**AIエージェントパイプラインの実行コスト(トークンコスト)を事前に見積もり、実行中に自動計測し、実測で見積もりを校正する仕組み**を Claude Code プラグインに実装した方法を解説します。

弊社で開発しているシステムアーキテクチャ設計エージェント「nexus-architect」を題材に、次の3点を紹介します。

* 価格とヒューリスティクスを単一の JSON に集約する設計
* Claude Code の hooks でトランスクリプトからトークン使用量をフェーズ別に自動記録する実装
* LOC(コード行数)ベースの事前見積もりモデルと、実測による校正ループ

「AIエージェントに大規模なタスクを任せたいが、いくらかかるのか事前に答えられない」という課題を持つ方に向けた、実装例つきのコスト管理論です。

### 対象読者

* Claude Code のプラグインやエージェントパイプラインを運用しているエンジニア
* AIエージェントの実行コストを組織として管理・予算化したい方(FinOps 的関心)
* hooks / トランスクリプト解析の具体的な実装例を探している方

---

## 背景・目的

nexus-architect は、レガシーシステムの調査 → 分析 → 評価 → 再設計 → レビュー → レポートまでを 17 フェーズのパイプラインとして自動実行する Claude Code プラグインです。対象が数十万行のレガシーコードベースになると、当然次の質問が出てきます。

> 「50万行のコードベースを解析させたら、いくらかかるのか?」

この質問に答えられないと、API 従量課金なら予算稟議が通らず、サブスクリプションなら使用量上限を食い潰すリスクを評価できません。人月見積もりと同じで、**AIエージェントの実行にも「見積もり → 実績記録 → 見積もり精度の改善」のループが必要**だと考えました。

必要なのは次の3つの機構です。

1. **見積もる**: 実行前に、コードベースの規模から費用の幅を出す
2. **計測する**: 実行中に、どのフェーズが何トークン使ったかを自動記録する
3. **校正する**: 実測が溜まったら、見積もりモデルの係数を実測比率で更新する

---

## 実装方法 / 解説

### 全体アーキテクチャ

3つのコンポーネントで構成し、**価格は必ず `model-pricing.json` を参照する**ことで、単価改定時の修正箇所を1箇所にしています。

### 1. 価格とヒューリスティクスの単一情報源

モデル単価、キャッシュ課金の倍率、見積もり用の係数を1つの JSON にまとめます。

skills/common/references/model-pricing.json(抜粋)

```
{
  "cache_multipliers": { "read": 0.1, "write_5m": 1.25, "write_1h": 2.0 },
  "families": [
    { "name": "opus",   "match": ["opus"],   "input": 5.0, "output": 25.0 },
    { "name": "sonnet", "match": ["sonnet"], "input": 3.0, "output": 15.0 },
    { "name": "haiku",  "match": ["haiku"],  "input": 1.0, "output": 5.0 }
  ],
  "estimation_heuristics": {
    "tokens_per_loc":             { "typical": 9,     "low": 8,   "high": 12 },
    "code_ingestion_ratio":       { "typical": 0.5,   "low": 0.3, "high": 0.7 },
    "effective_input_multiplier": { "typical": 8,     "low": 4,   "high": 12 },
    "output_per_phase_tokens":    { "typical": 60000 }
  }
}
```

ポイントは **キャッシュ課金を最初からモデルに組み込む**ことです。プロンプトキャッシュの読み取りは通常入力の 0.1 倍、キャッシュ書き込み(1時間 TTL)は 2.0 倍で課金されます。マルチターンのエージェント実行ではキャッシュ読み取りが課金トークンの大半を占めるため、これを無視した見積もりは大きく外れます。

### 2. hooks によるトークン使用量の自動記録

Claude Code の hooks(`PostToolUse` / `Stop` / `SubagentStop`)で Python スクリプトを起動し、セッションのトランスクリプト(JSONL)を**インクリメンタルに**読み取って、モデル別・フェーズ別の課金トークンを台帳に積み上げます。

hooks/hooks.json(抜粋)

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|Task|Agent",
        "hooks": [
          { "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/record_token_usage.py" }
        ]
      }
    ],
    "Stop": [
      { "hooks": [
          { "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/record_token_usage.py" } ] }
    ]
  }
}
```

トランスクリプトの assistant 行には `message.usage` として入力・出力・キャッシュ読み書きのトークン数が記録されています。これをモデル別に合算します。

hooks/record\_token\_usage.py(抜粋)

```
def usage_cost(usage, fam, pricing):
    mult = pricing.get("cache_multipliers", {})
    inp, out = effective_prices(fam)
    cost = (
        usage.get("input_tokens", 0) * inp
        + usage.get("output_tokens", 0) * out
        + usage.get("cache_read_input_tokens", 0) * inp * mult.get("read", 0.1)
        + usage.get("cache_creation_5m", 0) * inp * mult.get("write_5m", 1.25)
        + usage.get("cache_creation_1h", 0) * inp * mult.get("write_1h", 2.0)
    ) / 1_000_000.0
    return cost
```

記録先の台帳は次のような構造で、フェーズ別・モデル別に課金トークンと USD が積み上がります。

work/token-usage.json(構造イメージ)

```
{
  "phases": {
    "investigate": {
      "by_model": { "sonnet": { "input_tokens": 0, "output_tokens": 0, "...": 0 } },
      "cost_usd": 0.0
    }
  },
  "totals": { "...": 0 },
  "total_cost_usd": 0.0
}
```

### 3. 見積もりスキル: 実測優先、なければ LOC ベース

見積もりスキルは次の優先順位で動きます。

1. `work/token-usage.json` にフェーズ別実測があれば、それをそのまま(または残フェーズの外挿に)使う
2. なければ、LOC から事前見積もり(a-priori)を行う

事前見積もりの計算式は次のとおりです。

```
生コードトークン   = LOC × tokens_per_loc(9)
実読み込み量       = 生コードトークン × code_ingestion_ratio(0.5)
課金換算入力(全体) = 実読み込み量 × effective_input_multiplier(8)
出力トークン       = output_per_phase_tokens(60,000) × フェーズ数
```

`code_ingestion_ratio` が 1.0 でないのは、エージェントがコードを全行読むわけではなく、構造解析ツールやサンプリングで済ませる部分があるためです。`effective_input_multiplier` は、マルチターン実行でコンテキストが繰り返し送信される分から、キャッシュ読み取り(0.1 倍課金)による割引を差し引いた「課金換算の再送倍率」です。

---

## 実際の見積もり結果

サンプルの EC モノリス(実測 1,284 LOC)に対して、コアパイプライン 17 フェーズ(opus 6 / sonnet 10 / haiku 1)を API 従量課金で実行する前提の見積もりです。

| 項目 | typical |
| --- | --- |
| 課金換算トークン | 約 107 万(入力 4.6 万 + 出力 102 万) |
| 見積もりコスト | **$18.47 ≒ ¥2,862**(1 USD = 155 JPY) |
| ヒューリスティクス掃引の帯域 | $18.3〜$18.8 |
| 実務上の帯域 | $9〜$28(出力量に ±50% の振れを仮定) |

この結果から得られた示唆が2つあります。

**(1) 小規模コードベースではコストの 99% が出力トークン**  
LOC 由来の入力コストは $0.5 未満で、コストはほぼ「フェーズ数 × レポート分量 × 出力単価」で決まります。つまり削減レバーとして最も効くのは、コードの読み方の工夫ではなく**レポート分量の抑制とモデル選定**です。実際、opus を使う 6 フェーズだけで全体の約 49% を占めました。

**(2) 固定オーバーヘッドは無視できない**  
このモデルはシステムプロンプトやスキル定義の読み込み、フェーズ間のレポート再読込といった固定分を含みません。参考値として、パイプラインではない通常の開発セッション1回で実測 $9.27(キャッシュ読み取り 452 万トークン)を記録しており、小規模ケースでは固定分が支配的になります。見積もりレポートにはこの限界を明記するようにしています。

---

## 詰まったポイント・Tips

### フェーズへの帰属が一筋縄ではいかない

当初は「実行中フェーズ(`in_progress`)にトークンを割り当てればよい」と考えていましたが、実際のスキルはフェーズ開始を宣言せず、**完了時に `completed` だけを書く**ものが多いことがわかりました。そこで帰属ロジックを3段構えにしました。

1. `in_progress` のフェーズがあればそこへ(並列実行時は結合キーで按分せず合算)
2. なければ、前回チェックポイント以降に `completed` へ**遷移した**フェーズへ、保留分ごと割り当て
3. それもなければ保留バケツに積み、ターン終了時に未帰属(`_unassigned`)へ確定

### 同一メッセージ ID の重複計上

トランスクリプトでは、1回の API 応答が**同じ `message.id` を持つ複数行**に分かれて記録され、それぞれが同一の `usage` オブジェクトを持ちます。素朴に行ごとに合算すると数倍に過大計上されます。ID で重複排除し、さらにインクリメンタル読み取りのチャンク境界をまたぐ重複に備えて、直近の ID リストを台帳側に永続化しています。

hooks/record\_token\_usage.py(抜粋)

```
seen = set(recent_ids)          # 前回までに処理した message.id
for line in text.splitlines():
    ...
    mid = msg.get("id") or obj.get("uuid")
    if not mid or mid in seen:  # 同一応答の分割行を1回だけ数える
        continue
```

### 並行発火の直列化

`PostToolUse` と `SubagentStop` はほぼ同時に発火することがあります。台帳の読み書きが競合しないよう `flock` で直列化し、ロックを取れなかった発火は**黙って諦める**設計にしました。読み取りオフセットはロック下でしか進まないため、取りこぼした分は次の発火が同じバイト位置から拾います。

### プラグイン配布時の hooks 定義場所

マーケットプレイスのマニフェスト(`marketplace.json`)のプラグインエントリに `"hooks": "./hooks/hooks.json"` とファイルパスで書いたところ、Claude Code が「marketplace エントリではファイルパス形式の hooks は未サポート」というロードエラーを出しました。**hooks はプラグイン自身の `hooks/hooks.json` に置けば自動発見される**ため、マニフェスト側の指定は不要です。同じ構成を検討している方はご注意ください。

---

## まとめ

* **成果:** AIエージェントパイプラインに「見積もる(スキル)・計測する(hooks)・校正する(実測で係数更新)」のコスト管理ループを実装しました。価格と係数を単一 JSON に集約したことで、単価改定やモデル追加にも1箇所の修正で追従できます。
* **課題:** 事前見積もりの係数はまだ未校正のデフォルト値で、帯域は最大3倍程度の幅があります。実パイプラインの実行実績を数回分記録し、観測された比率(特にフェーズあたり出力量と実効入力倍率)で係数を更新していく予定です。固定オーバーヘッドのモデル化も今後の課題です。

人間のチームと同じように、AIエージェントにも「見積もり精度は実績記録の積み重ねでしか上がらない」が当てはまります。この記事が、エージェント運用のコスト管理に取り組む方の参考になれば幸いです。

---

## 参考

<https://code.claude.com/docs/ja/costs>

---

## 執筆者紹介

### 執筆者

**深津 航**  
株式会社Scalar 代表取締役CEO、Co-Founder

> 最近はAIを使った開発プロセスの改善に取り組んでいます。
