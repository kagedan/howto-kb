---
id: "2026-04-19-claude公式のapple-health連携が米国限定なのでmcp-serverを自作して89万レ-01"
title: "Claude公式のApple Health連携が米国限定なので、MCP Serverを自作して89万レコードを分析した"
url: "https://zenn.dev/at_sushi/articles/1a628f17dda8b1"
source: "zenn"
category: "claude-code"
tags: ["MCP", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Claude公式のApple Health連携は**米国Pro/Max限定**。日本では使えない
* 自作した。89万レコードをSQLiteに格納 → Claude DesktopからMCP経由で自然言語クエリ
* 朝散歩のbefore/after: **歩数3倍、日光2.2倍、歩行非対称性-71%**
* コード公開中 → [GitHub](https://github.com/atsushikaneko/health-data-hub)

**対象読者**: Claude Desktop/MCPに興味があるエンジニア、ヘルスデータを活用したい人

## なぜ自作したか

2026年1月、Claude公式がApple Health連携を発表した。試そうとしたら**米国のPro/Maxプラン限定**。日本では使えない。

一方、自分のiPhoneには7年分のデータが眠っている。データはある。足りないのは引き出す仕組みだけ。じゃあ作ればいい。

## 3つの選択肢

Apple Healthのデータを分析する方法は、現時点で3つある。

本記事では以下の用語を使い分ける：

* **Apple純正ヘルスケアApp**: iPhoneに標準搭載されている緑十字のアプリ
* **Claude公式連携**: 2026年1月にClaude iOSアプリに追加されたApple Health連携機能（米国Pro/Max限定）
* **自作MCP**: 本記事で紹介する、Apple HealthのXMLをSQLite + MCP Server化したもの

|  | Apple純正ヘルスケアApp | Claude公式連携 | 自作MCP |
| --- | --- | --- | --- |
| 日本で使える | ✅ | ❌（米国のみ） | **✅** |
| データアクセス | 集計ビューのみ | サマリー程度 | **SQLで全量** |
| 任意期間の比較 | ❌（固定期間のみ） | △（AIに聞けば） | **✅** |
| 相関分析 | ❌ | △ | **✅** |
| 歩行非対称性等の深い指標 | 表示なし | 不明 | **SQLで取得可能** |
| プライバシー | ローカル | Anthropicサーバー経由 | **完全ローカル** |
| セットアップ | 不要 | ボタン1つ（米国なら） | git clone → 3ステップ |

Apple純正はデータを「見る」だけ。Claude公式連携は米国限定でサマリー止まり。自作MCPは**パーサー・DB・MCPツールが全部セットで公開されている**ので、clone → エクスポート → 起動の3ステップですぐ使える。

## アーキテクチャ

```
iPhone（ヘルスケアアプリ）
  ↓ XMLエクスポート
Python Parser（iterparse / 380MB+対応）
  ↓ INSERT OR IGNORE（冪等）
SQLite（health.db）
  ↓
FastMCP Server（8ツール）
  ↓
Claude Desktop（自然言語クエリ）
```

ポイントは2つ。

**1. iterparseでストリーミング処理。** Apple HealthのXMLは380MB超え。普通に読むとメモリが爆発する。

```
for event, elem in ET.iterparse(xml_path, events=("end",)):
    if elem.tag == "Record":
        # レコード処理
        elem.clear()  # メモリ解放
```

**2. 冪等なインポート。** `UNIQUE`制約 + `INSERT OR IGNORE`で何度フルインポートしても重複しない。定期的にiPhoneからエクスポートして投入すればデータが蓄積される。

### MCPツール

| ツール | 用途 |
| --- | --- |
| `query_health` | 任意のSQLを実行（一番使う） |
| `compare_periods` | 2つの期間を比較 |
| `get_health_summary` | 指定期間のサマリー |
| その他5本 | 睡眠分析、ワークアウト取得等 |

## 分析してわかったこと

Apple純正ヘルスケアAppは固定期間のビューしかない。Claude公式連携はサマリー止まり。自作MCPなら**任意の期間を指定してSQLで比較できる**。実際にやってみた。

### 朝散歩の before / after

2026年2月22日から毎朝1〜1.5時間の散歩を開始。`compare_periods`ツールで前後1ヶ月を比較した。

| 指標 | Before | After | 変化 |
| --- | --- | --- | --- |
| 平均歩数 | 7,259歩/日 | 21,147歩/日 | **2.9倍** |
| 日光暴露時間 | 23.1分/日 | 51.3分/日 | **+122%** |
| 平均就寝時刻 | 0:12 | 23:58 | 14分前倒し |
| 5時間未満睡眠 | 4日/月 | 1日/月 | -75% |
| 歩行非対称性 | 5.0% | 1.4% | **-71%** |
| 6分間歩行テスト | 453m | 497m | +10% |

\*\*歩行非対称性が5.0%→1.4%（-71%）\*\*は驚いた。毎日歩くだけで左右バランスがここまで変わる。

日光も23分→51分で2倍以上。散歩前でも23分あるのは通勤等の移動分だろうけど、意識的に外を歩くだけで倍になる。フリーランス在宅勤務だと、散歩しないと日光が本当に足りない。

### 手首温度 × 中途覚醒

`query_health`で相関を探ったら、**手首皮膚温が高い夜は中途覚醒が長い（r=+0.37）**。室温のせいか体調のせいかは、環境センサーを追加すれば切り分けられる。

## 今後の展望

このリポジトリは今後、**Apple Health以外のデータソースのパーサー・DB統合も追加していく予定**。同じDBに複数ソースを集約することで、デバイスを横断した相関分析ができるようになる。

### なぜ同じDBに入れるのか？

データソースごとに別々のMCP Serverを立てると、Claude側で「あっちのサーバーから睡眠を取って、こっちから気温を取って、結合して」と指示する必要がある。同じSQLiteに入っていれば、JOINひとつでクロス分析できる。

### 対応済み

* ✅ Apple Health（89万レコード）
* ✅ Open-Meteo API（気温/気圧/降水量）

### 第2弾で対応予定（パーサー + DB + MCPツールをセットで追加）

* AirGradient ONE（CO2/PM2.5/室温/湿度）→ 「CO2が1000ppm超えた夜の中途覚醒は？」
* Dexcom G7 CGM（血糖値）→ 「血糖スパイク後の睡眠の質は？」
* ActivityWatch（PC作業時間/アプリ使用時間）→ 「夜11時までコード書いてた日の翌日の睡眠は？」
* Omron体組成計（体重/体脂肪率）→ 運動量と体組成の変化追跡

健康データだけでなく、**行動データ**も同じDBに入れることで「何をしたら体調がどう変わるか」が見えるようになる。記事も別途書く予定。

## セットアップ

詳細な手順は[GitHubリポジトリのREADME](https://github.com/atsushikaneko/health-data-hub)を参照。ざっくり3ステップ：

1. iPhoneの「ヘルスケア」から全データをエクスポート → Macに転送
2. `python3 parser/xml_to_sqlite.py tmp/export.xml` でDBに投入
3. Claude Desktopの設定に追記して再起動

## まとめ

* Claude公式のApple Health連携は米国限定。**日本では自作が唯一の選択肢**
* Apple Health + サードパーティデバイス + アプリのデータが全部XMLに入ってる。**デバイスを増やすだけで分析対象が広がる**
* 朝散歩のbefore/afterで、Apple Watchアプリを眺めてるだけでは気づけないインサイトが得られた
* データはあなたのiPhoneに既にある。公式を待つ必要はない

リポジトリ → [GitHub](https://github.com/atsushikaneko/health-data-hub)
