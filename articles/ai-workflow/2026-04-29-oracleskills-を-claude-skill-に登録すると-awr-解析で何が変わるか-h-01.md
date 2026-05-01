---
id: "2026-04-29-oracleskills-を-claude-skill-に登録すると-awr-解析で何が変わるか-h-01"
title: "oracle/skills を Claude Skill に登録すると AWR 解析で何が変わるか — Haiku/Sonnet × Skill有無の4パターン比較"
url: "https://qiita.com/asahide/items/53cfdab083905fedeed5"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-29"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

# 1. はじめに

Oracle が GitHub に **oracle/skills** リポジトリを公開しました。

- リポジトリ: https://github.com/oracle/skills
- カバー範囲: SQL・PL/SQL 開発、パフォーマンスチューニング、セキュリティ、管理、ORDS など 100+ の実践ガイド（Oracle 19c〜26ai 対応）

これを Claude Desktop(Code) の Skill に登録すると、Oracle 関連の質問をするたびにガイドを参照しながら回答してくれるようになります。せっかく登録したので、手元にあった AWR レポートを使って「Skill の有無」と「モデルの大小」の組み合わせで何が変わるかを記録しました。

:::note warn
負荷はシンプルなテスト環境（3分間のスナップショット、実質1セッション）です。本格的な本番チューニングの検証ではなく、**Skill の有無とモデルの組み合わせで何が変わるかを記録したご参考レベル**の内容です。
:::

### 検証ゴール

| # | ゴール |
|---|---|
| 1 | Skill の有無で解析の検出項目・定量化がどう変わるか確認する |
| 2 | Haiku と Sonnet で結果の差があるか確認する |
| 3 | Skill 効果を「見落とし防止」「定量化」「評価補正」の3軸で切り出す |

### 結論（先出し）

- **Skill の有無がモデルサイズより解析品質に影響した**
- Skill なしでは Haiku・Sonnet どちらも `Execute to Parse %` を見落とした
- **Haiku + Skill** は Sonnet 単体より多くの指標を検出し、確認 SQL も多かった
- Work Area の「高い」が Skill あり版で「3 分で 30GB」と定量化された
- ハードパースの優先度評価が Skill なし：中 → Skill あり：低 に補正された

---

# 2. 検証環境

| 項目 | 内容 |
|---|---|
| DB 名 | ORCL（PDB: PDBTEST）|
| Oracle バージョン | 23.26.2.1.0（Oracle 26ai）|
| 環境 | Oracle Exadata Cloud（Autonomous Database）|
| AWR 計測期間 | 約 3 分間（Elapsed: 184 秒）|
| DB Time | 195 秒（AAS ≒ 1.06、単一セッション相当）|
| クライアント | Claude Desktop |
| モデル | Claude Haiku 4.5 / Claude Sonnet 4.6 |
| Skill | oracle-db-skills（oracle/skills リポジトリ準拠）|

---

# 3. 検証方法

## 3.1. Skill の登録

Claude Desktop の「スキル」画面から **oracle-db-skills** を追加します。Source は `https://github.com/oracle/skills` で、AWR・ASH・チューニングなどのキーワードが含まれると自動でトリガーされます。

![skill-registration.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/e90b1c49-d29a-4603-9ac9-986617dd924f.png)


## 3.2. 4 パターンの作り方

| パターン | モデル | Skill |
|---|---|---|
| Haiku-only | Claude Haiku 4.5 | OFF |
| Haiku + Skill | Claude Haiku 4.5 | ON |
| Sonnet-only | Claude Sonnet 4.6 | OFF |
| Sonnet + Skill | Claude Sonnet 4.6 | ON |

モデルは Claude Desktop の設定で切り替え、Skill は有効/無効をトグルするだけです。

## 3.3. プロンプト

4 パターンすべて同じプロンプトを使いました。

```
（AWR レポートの HTML を貼り付け）
AWRを解析して
```

特別なプロンプトエンジニアリングは一切なし。AWR の HTML をそのまま貼って「AWRを解析して」の一言のみです。

:::note warn
各パターンは別セッションで実施していますが、同一セッション内で複数回試行した場合は履歴の影響を受ける可能性があります。厳密な A/B テストではなくご参考としてご覧ください。
:::

---

# 4. 全体比較

## 4.1. 検出項目の一覧

| 観点 | Haiku-only | Haiku+Skill | Sonnet-only | Sonnet+Skill |
|---|---|---|---|---|
| 主犯 SQL 特定 | ✅ | ✅ | ✅ | ✅ |
| CPU バウンド診断 | ✅ | ✅ | ✅ | ✅ |
| TEMP 溢れ指摘 | ✅ | ✅ | ✅ | ✅ |
| AAS 計算 | ❌ | ✅ | ❌ | ✅ |
| **Execute to Parse %** | ❌ | ✅ | ❌ | ✅ |
| Work Area 定量化 | ❌ | ✅（30GB）| ❌ | ✅（30GB）|
| Soft Parse % | ❌ | ✅（98.4%）| ❌ | ✅（98.4%）|
| ハードパース評価の補正 | ❌ | ✅ | ❌ | ✅ |

主要問題（主犯 SQL / CPU バウンド / TEMP 溢れ）はどのパターンでも正確に検出されました。一方で **AAS・Execute to Parse % などの計算指標は、Skill なしでは 2 モデルとも見落としました**。

## 4.2. レポートの量と質

| パターン | 文字数（概算）| 確認 SQL 本数 |
|---|---|---|
| Haiku-only | 約 250 字 | 0 本 |
| Haiku + Skill | 約 500 字 | 3 本 |
| Sonnet-only | 約 2,000 字 | 3 本 |
| Sonnet + Skill | 約 3,500 字 | 10 本 |

Haiku-only は最小限の箇条書きでしたが、Skill を乗せると AAS や Execute to Parse % の計算を含む分析を出力しました。

---

# 5. Skill 効果① 見落とし防止 — Execute to Parse %

### 検出状況

| パターン | 検出 |
|---|---|
| Haiku-only | ❌ 未検出 |
| Sonnet-only | ❌ 未検出 |
| Haiku + Skill | ✅ 検出 |
| Sonnet + Skill | ✅ 検出 |

### 指標の内容

```
Execute to Parse % = (1 - Parses / Executes) × 100
                   = (1 - 68.8 / 97.0) × 100
                   = 29.1%  ←  目標 50% 以上
```

この指標はロードプロファイルの数値から計算できますが、「何を計算すべきか」の知識がないと見落とします。Skill の `awr-reports.md` に **目標値（> 50%）と計算式** が明記されているため、Haiku でも Sonnet でも検出できました。

**意味**: カーソルが十分に再利用されていない。コネクションプールやステートメントキャッシュの設定見直しが必要。

---

# 6. Skill 効果② 定量化 — Work Area の異常を数値で示す

### 変化の比較

| | Skill なし | Skill あり |
|---|---|---|
| SQL Work Area の記述 | 「非常に高い」（定性）| 「164.8MB/秒 × 184秒 ≒ 30GB」（定量）|

```
164.8 MB/秒 × 184 秒 ≒ 30,332 MB（約 30GB）
```

Skill の `memory-tuning.md` に Work Area 統計の読み方が記載されており、単位変換と掛け算で異常の深刻さを数値化できました。「非常に高い」という定性表現より、「3 分で 30GB」という数字の方が問題の緊急度を伝えやすくなります。

---

# 7. Skill 効果③ 評価の補正 — 過剰対応を防ぐ

同じ事実（1.1 回/秒）でも、Skill の有無で評価が変わりました。

| | Skill なし | Skill あり |
|---|---|---|
| 事実 | 1.1 回/秒 | 1.1 回/秒（同じ）|
| 評価 | 「中程度の問題」として優先度：中 | 「閾値 100/秒 を大幅に下回る → 緊急度：低」|

Skill の `awr-reports.md` に「ハードパース > 100/秒 が問題の指標」と明記されているため、相対評価が可能になりました。これは **見落としではなく、過剰な対応を防ぐ**効果です。

---

# 8. Haiku + Skill と Sonnet-only の比較

Skill の有無の差が特に分かりやすい組み合わせを並べます。

| 観点 | Haiku + Skill | Sonnet-only |
|---|---|---|
| 主要問題の特定 | ✅ | ✅ |
| Execute to Parse % | ✅ 検出 | ❌ 未検出 |
| Work Area | ✅ 30GB と定量化 | ❌「非常に高い」のみ |
| ハードパース評価 | ✅ 緊急度：低（適正）| ❌ 優先度：中（過大）|
| 確認 SQL 数 | 3 本 | 3 本 |
| レポート文字数 | 約 500 字 | 約 2,000 字 |

Sonnet-only は文字数が多く説明が丁寧ですが、計算指標の見落としと評価のズレがありました。Haiku + Skill は短い出力ながら、Skill が補う形で定量分析まで到達しています。

:::note info
今回の検証では、**モデルを Haiku → Sonnet に上げるよりも Skill を ON にする効果の方が大きい**という結果になりました。ただし負荷がシンプルなため、より複雑な AWR での傾向は別途確認が必要です。
:::

---

# 9. まとめ

| 観点 | Skill なし | Skill あり |
|---|---|---|
| Execute to Parse % 検出率 | 0/2 | 2/2 |
| Work Area の表現 | 「高い」（定性）| 「約 30GB」（定量）|
| ハードパース優先度 | 中（過大評価）| 低（適正）|
| 確認 SQL 数（Haiku）| 0 本 | 3 本 |
| 確認 SQL 数（Sonnet）| 3 本 | 10 本 |

oracle/skills は AWR 解析に限らず、SQL チューニング・PL/SQL・セキュリティなど幅広いガイドを収録しています。Claude Desktop を使っている Oracle DBA の方は、まず登録してみる価値があると思います。

API 経由で利用する場合、Haiku は Sonnet に比べて入力・出力ともに大幅に低コストです（料金は [Anthropic 公式 Pricing](https://claude.com/pricing#api) 参照）。Skill で解析品質を補えるなら、コスト面でも Haiku + Skill の組み合わせが有利になります。

より複雑な AWR（RAC 複数ノード、待機イベントが複合している環境など）での検証は今後の課題です。

---

# 参考

- [oracle/skills リポジトリ](https://github.com/oracle/skills)
- [Oracle Database 26ai ドキュメント](https://docs.oracle.com/cd/G47991_01/index.html)
- [Automatic Workload Repository（AWR）概要](https://docs.oracle.com/cd/G13837_01/sagug/awr.html)
