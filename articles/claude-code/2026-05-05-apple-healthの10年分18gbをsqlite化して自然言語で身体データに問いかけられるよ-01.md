---
id: "2026-05-05-apple-healthの10年分18gbをsqlite化して自然言語で身体データに問いかけられるよ-01"
title: "Apple Healthの10年分1.8GBをSQLite化して、自然言語で身体データに問いかけられるようにした"
url: "https://zenn.dev/hideakitamai/articles/8ab4733e65e0dc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

iPhoneとApple Watchで10年分蓄積されていた健康データ（426万レコード、1.8GB）を、ローカルのSQLiteに投入し、MCPサーバー経由でClaudeから自然言語クエリできる環境を作りました。

「過去2年のVO2max月次推移を見せて」「歩行非対称性が大きかった日を特定して」のような複雑な集計が、その場で問いを変えながら深掘りできるようになります。Apple Health公式アプリの定型レポートとは違う使い勝手です。  
こちらの実装記事です↓

<https://note.com/hideakitamai/n/nb114a1a6c486>

**この記事が役に立つ人**

* Apple Watch / iPhoneの健康データを、もっと自由に分析したい人
* MCPサーバーの実装例として「自分のデータに自然言語で問い合わせる」のを試したい人
* 健康データから行動変容の効果測定をやりたい人
* 個人ローカルにデータを置いたままAIから扱う設計に興味がある人

# 結論：SQLite + FastMCP の二段構えツール設計

Apple Health XML を SQLite に投入し、FastMCP で読み取り専用ツールを公開すると、Claudeから複雑な集計クエリを投げられるようになります。データ量1.8GB・426万レコードでも実用速度（数秒以内）で応答します。

ツール設計は「`query_health` で SQL 直接実行」と「`get_daily_summary` 等の典型集計ショートカット」の二段構えにすると、LLM側が安定して使い分けてくれます。

# 動機：健康データを中長期で見たくなった

iPhoneとApple Watchで気付かないうちに10年分のデータが溜まっていました。Apple Health公式アプリの画面では当日や週次の表示は見られますが、「過去2年の月別推移」「ある日の異常値の特定」のような問いに答えるのは難しい構造です。

中長期での変動を自分で確認したくなったのが起点です。VO2maxは改善傾向にあるのか、季節によって睡眠時間はどう変わっているのか、生活習慣を変えた前後で何が動いたのか。こういう問いを、データに直接ぶつけられる環境がほしくなりました。

既存のヘルスケア系SaaSも検討しましたが、過去全データの遡及分析と、自然言語での自由な問い合わせができるサービスは見つかりません。AppleがAPIを限定公開していることもあり、サードパーティ各社も浅い分析にとどまる構造です。

ローカルにデータを取り出してSQLite + MCPで包む構成が現実的という結論になり、構築しました。

# アーキテクチャ全体像

iPhoneの「ヘルスケア」アプリからXMLをエクスポートし、Mac mini上のSQLiteに投入。FastMCPでツール公開し、Claudeから自然言語クエリを受ける構成です。

# 実装の流れ

## 1. Apple Health XMLのエクスポートと転送

iPhone「ヘルスケア」アプリ → 設定 → データを書き出す。約1.8GB（中身は `export.xml`）が出力されます。

これをMac miniに転送するところでまず詰まりました。

## 2. SCP直接転送はXMLサイズに対して不安定だった

```
# 直接送ろうとすると87MBで切断
scp export.xml user@mac-mini:~/myws/data/
```

何度試しても安定しません。XMLが「圧縮しやすいテキスト」のため、ネットワーク経路のバッファ処理で詰まっているように見えました。

gzipで圧縮すると **1.8GB → 71MB** まで減ります（XMLは圧縮効率が異常に良い）。これなら3分19秒で安定して送れました。

```
gzip -c export.xml > export.xml.gz
scp export.xml.gz user@mac-mini:~/myws/data/
gunzip ~/myws/data/export.xml.gz
```

GBクラスのテキストファイルをSCPで送る時は、最初からgzipを挟むのが安全です。

## 3. SQLiteスキーマ設計

Apple Health は60+のメトリクスがあり、メトリクス名（`HKQuantityTypeIdentifier...`）が長いです。

最初は「メトリクスごとにテーブルを分割する」案を考えましたが、テーブル数が60+になって管理が煩雑です。**`type` 列を持つ単一テーブル**にしたら扱いやすくなりました。

```
CREATE TABLE records (
    type TEXT,
    source_name TEXT,
    unit TEXT,
    value REAL,
    start_date TEXT,
    end_date TEXT,
    creation_date TEXT
);

CREATE INDEX idx_type_date ON records(type, start_date);
```

「期間×指標」のクエリが頻発するので、`(type, start_date)` の複合インデックスを張っています。

## 4. XMLパース時はストリーム処理必須

```
import xml.etree.ElementTree as ET
import sqlite3
from pathlib import Path

DB_PATH = Path("~/myws/data/health.db").expanduser()
XML_PATH = Path("~/myws/data/export.xml").expanduser()

def import_health_xml():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            type TEXT, source_name TEXT, unit TEXT,
            value REAL, start_date TEXT, end_date TEXT,
            creation_date TEXT
        )
    """)

    # iterparseでメモリ効率よく処理
    count = 0
    for event, elem in ET.iterparse(XML_PATH, events=("end",)):
        if elem.tag == "Record":
            cursor.execute("""
                INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                elem.get("type"),
                elem.get("sourceName"),
                elem.get("unit"),
                float(elem.get("value", 0)),
                elem.get("startDate"),
                elem.get("endDate"),
                elem.get("creationDate"),
            ))
            count += 1
            if count % 10000 == 0:
                conn.commit()
            elem.clear()  # iterparseのメモリ解放はこれが要

    conn.commit()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_type_date ON records(type, start_date)")
    conn.commit()
    conn.close()
```

`ET.parse` で全部読み込もうとすると1.8GBでメモリが破綻します。`iterparse` + `elem.clear()` のパターンは GBクラスのXMLを扱うときの定番です。

最終的に **426万レコード、DB 2.5GB** になりました。

# FastMCPでツール公開

ツール設計は二段構えにします。

## ツール1: `query_health`（SQL直接実行）

複雑な集計用に、SELECT文を直接実行できるツール。

```
from fastmcp import FastMCP
import sqlite3
import os

DB_PATH = os.path.expanduser("~/myws/data/health.db")

mcp = FastMCP("health-data-hub")

@mcp.tool()
def query_health(sql: str) -> list[dict]:
    """SQLiteに対してSELECT文を直接実行する。複雑な集計用"""
    if not sql.strip().lower().startswith("select"):
        raise ValueError("SELECT only")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(row) for row in rows]
```

## ツール2: `get_daily_summary`（典型集計のショートカット）

LLMが自然に呼び出せる、典型的な日次サマリー集計のショートカット。

```
@mcp.tool()
def get_daily_summary(target_date: str) -> dict:
    """指定日の主要指標サマリーを返す"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    summary = {}
    metrics = {
        "hrv": "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
        "resting_hr": "HKQuantityTypeIdentifierRestingHeartRate",
        "steps": "HKQuantityTypeIdentifierStepCount",
        "active_energy": "HKQuantityTypeIdentifierActiveEnergyBurned",
        "vo2max": "HKQuantityTypeIdentifierVO2Max",
    }

    for key, type_name in metrics.items():
        row = conn.execute("""
            SELECT AVG(value) as v
            FROM records
            WHERE type = ? AND date(start_date) = ?
        """, (type_name, target_date)).fetchone()
        summary[key] = row["v"]

    conn.close()
    return summary

if __name__ == "__main__":
    mcp.run()  # default: stdio transport
```

`get_sleep`、`get_activity_trend` 等、用途別のショートカットツールも同様に実装します。

## なぜ二段構えにするか

LLMの挙動として、 **典型集計ツールがあるとそちらを優先的に呼びます**。「過去30日のHRV平均」は `get_daily_summary` を30回呼ぶより、`query_health` でSQL一発の方が効率的なので、複雑な問いではLLM自身が `query_health` を選びます。

逆に「今日の状況」「最近の傾向」のような曖昧な問いには、ショートカットツールが安定します。両方提供しておくと、LLMが文脈で使い分けるという結果になりました。

# Claude Codeでの登録

`stdio` transport で個人ローカル運用するなら、Claude Code の `~/.mcp.json` に登録するだけです。

```
{
  "mcpServers": {
    "health-data-hub": {
      "command": "python3",
      "args": ["/Users/<USER>/myws/health-data-hub/mcp_server/server.py"]
    }
  }
}
```

# 動作確認の問い5つ

セットアップが完了したら、実際に問いを投げて動作確認します。以下の4問が通れば実用レベルです。

1. 「2025年10月前後のHRV、安静時心拍数、睡眠時間、入眠時刻、睡眠ステージを月別に集計して」
2. 「VO2maxの過去2年の月次推移を見せて」
3. 「歩行非対称性の過去半年の推移と、その変動が大きかった日を特定して」
4. 「過去2年の入眠時刻と睡眠時間の推移を月別で見せて、季節変動や生活パターンの変化を抽出して」
5. 「歩数とアクティブカロリーの**年別推移を10年分**見せて、ライフステージの変化と相関がある期間を特定して」

5問すべてに有意な答えが返ります。実際に1〜数秒で結果が返ってきます。

# 落とし穴：z-scoreの異常値が正常データだったケース

問3を投げて「歩行非対称性が日常0.9%なのに、ある日12.1%（z=+8.5）の異常値」が出てきました。最初は観測エラーかセンサー異常を疑いました。

調べたら、その日は地形の凹凸がある場所を歩いていた日でした。**観測エラーではなく、地形を反映した正常データ**だった、というオチです。

教訓: 異常値の日はGoogleカレンダーや行動履歴と突き合わせるのが必要。データだけ見て解釈するとミスリードします。

# SSH経由で動かない問題（Mac mini固有）

Mac miniのClaude CodeをSSH経由から呼び出すと、Keychainロックで認証エラーになります。

対処は、Mac miniを自動ログイン構成にして、LaunchAgent経由で起動すること。SSH経由ではなくLaunchAgentから起動されたプロセスは Keychain にアクセスできます。

観測ジョブのような常駐処理は必ずLaunchAgent化が必要です。

# 経営判断・運用上の整理

## 既存事例があるなら自前実装するな

GitHubで参考実装を見つけてスキーマ設計を流用したことで、構築時間が大幅に短縮されました。「Apple Health のXMLパーサとSQLiteスキーマ」のような部品は、車輪の再発明をする箇所ではありません。

## Notion DB と SQLite の二重管理を許容した

既存の日次サマリーDB（Notion）はそのまま維持し、深い分析はSQLite経由とする「役割分担」アプローチにしました。データの完全集約より、各データソースの強みを活かす運用です。Notionは人間が見やすく、SQLiteはAIが扱いやすい。

## 手動エクスポート月1回を許容

Apple Health XMLのリアルタイム同期は不可能です。月1回の手動エクスポートで運用としては十分でした。このユースケースでは「最新1日のデータ」より「過去2年の傾向」が重要だからです。

## MCP の `stdio` transport は個人ローカル運用に最適

認証不要で起動オーバーヘッドだけ。個人利用ならこれで完結します。claude.aiから呼ぶ場合は別途 `streamable-http` transportに切り替えてOAuth認証を入れる必要があり、これは別記事で扱います。

# 動いた後に見えたこと

データを自前のSQLiteに持つ意義は、**問いを変えながら深掘りできる**ことに出ます。

公式アプリやサードパーティSaaSの定型ダッシュボードでは「予め用意された指標」しか見られません。SQLite + MCP では、「あの月、何が起きていたか」「複数指標の同期変動」のような **問いの組み立て自体を変えられる** 。

副次的な気づきとして、健康時の日次変動レンジがそれなりに大きいこともわかりました。HRV単発の値で一喜一憂しても意味がない、という当たり前のことが、データを見て初めて言語化できる。

「自分のデータを自分で持つ」設計は、ヘルスケアに限らず家計、業務データ、設備管理など他のドメインにも転用できる構造です。次回はこのMCPサーバーをclaude.aiから呼べるようにする話を書きます。

# 参考リンク

---

筆者：玉井秀明（Hide Tamai）

BAIOX取締役CMO / Goaico共同代表。医療AIと中小企業向けAI導入支援の両面でAI事業に関わっています。

<https://note.com/hideakitamai/n/nb114a1a6c486>
