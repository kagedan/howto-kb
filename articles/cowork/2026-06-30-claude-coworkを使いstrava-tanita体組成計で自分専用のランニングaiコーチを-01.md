---
id: "2026-06-30-claude-coworkを使いstrava-tanita体組成計で自分専用のランニングaiコーチを-01"
title: "Claude Coworkを使い、Strava × TANITA体組成計で自分専用のランニングAIコーチを作った話"
url: "https://zenn.dev/cvl/articles/1d1baee75e7fc6"
source: "zenn"
category: "cowork"
tags: ["MCP", "prompt-engineering", "API", "LLM", "cowork", "Python"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

ランニングを続けていると、「走った記録」と「身体の変化（体重・体脂肪率）」を  
横断して見たくなります。さらに欲を言えば、そのデータを踏まえて、  
「今週はどう走ればいい？」を相談できる相手がほしくなります。  
ランニングアプリだと運動習慣を、体重管理アプリだと対組成をそれぞれ確認できますが、双方に蓄積されたデータをとっつき合わせて自分専用のトレーナーを作りたくなりました。

そこで、

* **Strava の公式 MCP** でラン記録を参照し、
* **TANITA ヘルスプラネット（HealthPlanet）の体組成データ** を自作 MCP で参照し、
* 両者を統合した **ライブダッシュボード** と **AIコーチ** を Claude（Cowork）上で動かす

という構成で、自分専用のランニングAIコーチを作成しました。本記事はその記録と、  
途中でハマったポイントのメモ。

> 本当はAppleのHealthデータを使いたかったが公式のMCPがUSのみでの展開とのことで断念。体組成 MCP の発想は [タニタの体重・体脂肪データをClaudeから呼べるようにした話](https://zenn.dev/hittskapi/articles/e215e34c04143e) を参考にさせていただきました。

## 全体構成

図が下手

```
┌─────────────────┐     ┌─────────────────────────┐
│ Strava 公式 MCP │ ──▶ │                          │
└─────────────────┘     │   Claude / Cowork       │
                        │  ┌───────────────────┐  │
┌───────────────┐       │  │ ライブダッシュボード│  │
│ HealthPlanet  │ ──▶   │  │ (HTML Artifact)   │  │
│ MCP（自作）    │       │  │  + AIコーチ     　 │  │
└───────────────┘       │  └───────────────────┘  │
       ▲                └─────────────────────────┘
       │
  TANITA BC-768 → HealthPlanet（OAuth2 API）
```

ポイントは、**体組成側は既存コネクタが無いので自作 MCP でOAuth2 APIをラップする**こと。  
ダッシュボードは Cowork の「ライブアーティファクト」として作り、開くたびに  
両 MCP から最新データを取得します。  
これならApple HealthCareのデータを引っ張ってきて自作してもよかった気もしますが、先人がブログ化していたためHealthPlanetを使います。TANITA万歳🙌

## パート1：HealthPlanet MCP サーバーを作る

### HealthPlanet API の要点

[HealthPlanet API](https://www.healthplanet.jp/apis/api.html) は OAuth2 ベース。

* 認可: `/oauth/auth` → 認可コード → `/oauth/token` でアクセストークン取得
* 体組成: `/status/innerscan`（`tag=6021` 体重kg, `tag=6022` 体脂肪率%）
* 日付範囲は **最大3ヶ月**、レート制限は **1時間60回**
* 2020年に筋肉量・骨量などのタグは提供終了。**取れるのは体重と体脂肪率だけ**

「体重と体脂肪率しか取れない」ので、ここから **BMI・除脂肪体重・基礎代謝（Harris-Benedict）**  
を計算して付加価値にする方針にしました。正直体重と体脂肪率さえ取れれば問題ないです。  
![](https://static.zenn.studio/user-upload/02234bbde958-20260630.png)  
*こんな画面。モバイルアプリだと対応していないので注意*

### FastMCP でツール化

`pip install fastmcp httpx python-dotenv` でサクッと。ツールはこの5つ。

| ツール | 説明 |
| --- | --- |
| `get_latest_body_composition` | 最新の体重・体脂肪率（＋BMI・除脂肪体重） |
| `get_body_composition(from, to)` | 指定期間の一覧（92日超は自動分割取得） |
| `get_measurements_range` | キャッシュ内データの範囲と件数 |
| `get_profile` | 生年月日・身長・性別・年齢・BMR |
| `list_available_metrics` | 取得・計算可能なメトリクス一覧 |

体重(6021)と体脂肪率(6022)は別レコードで返ってくるので、**測定日時をキーに結合**します。

```
def _merge_record(records, item):
    key = str(item.get("date", ""))
    rec = records.setdefault(key, {"datetime": _fmt_dt(key),
                                   "weight_kg": None, "body_fat_pct": None})
    value = float(item["keydata"])
    if item["tag"] == "6021":   # 体重
        rec["weight_kg"] = value
    elif item["tag"] == "6022": # 体脂肪率
        rec["body_fat_pct"] = value
```

API制限（3ヶ月・60回/時）対策として、取得済みデータは JSON でローカルキャッシュし、  
トークンは `expires_at` を見て自動リフレッシュするようにしました。

### 派生指標の計算

```
def calc_lean_mass(weight, fat):       # 除脂肪体重
    return round(weight * (1 - fat / 100), 2)

def calc_bmr_harris_benedict(w, h, age, sex):  # 基礎代謝(改訂版)
    if sex.startswith("m"):
        return round(88.362 + 13.397*w + 4.799*h - 5.677*age)
    return round(447.593 + 9.247*w + 3.098*h - 4.330*age)
```

除脂肪体重を見ると「体重が落ちたとき、それが脂肪か筋肉か」が分かります。  
減量の“質”を測る上でこれが効いてくるはず。(どれだけ正確かは分かんないですが、気分が上がってランニングモチベに繋がればOK)

## パート2：セットアップでハマったところ

実装より、**Claude Desktop への登録でハマった**。同じ轍を踏まないようにメモを残しておきます。同じことしたい人向けの参考になれば。

### ① `claude_desktop_config.json` の場所

| OS | パス |
| --- | --- |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

無ければ新規作成。Claude Desktopアプリの「設定 → 開発者 → Edit Config」からでも開けます。意外と場所わからん

### ② トップレベルの JSON オブジェクトが2つ

既存設定の末尾に MCP ブロックを貼り足したら、`{...}` が2つ並んで  
`Unexpected non-whitespace character after JSON` に。  
**1つのオブジェクトに統合**し、`mcpServers` をキーとして中に入れる。

```
{
  "coworkUserFilesPath": "...",
  "preferences": { /* ... */ },
  "mcpServers": {
    "personal-health": {
      "command": "C:/Users/<user>/.../venv/Scripts/python.exe",
      "args": ["-m", "health_mcp.server"]
    }
  }
}
```

### ③ Windowsパスは `/`（スラッシュ）が安全

JSON では `\` がエスケープ文字。`"C:\Users\..."` はエラーになるので、  
`"C:/Users/..."` と書く（Windows も Python も解釈できる）。  
`\` を使うなら `"C:\\Users\\..."` と必ず2つ重ねる。毎度ながらバックスラッシュじゃないのねと違和感。

### ④ ターミナルは開きっぱなしにしなくていい

stdio の MCP サーバーは、Claude 側が起動時にプロセスを自動起動・管理してくれます。便利です。  
手動でターミナル実行が要るのは「起動するか確認する」診断用途だけになります。  
反映されないときは **アプリを完全終了→再起動**、必要なら **新しい会話**を開くで更新されます。

## パート3：ライブダッシュボードと AIコーチ

### まず実データの形を確認する

ダッシュボードを書く前に、MCP ツールを一度叩いて**レスポンスの実際の形**を見る。  
ラッパー経由だとフィールド名や構造が API と違うことがあるので、推測で書かない。

Strava の `list_activities` は `activities[].summary` に  
`distance`(m)・`avg_speed`(m/s)・`relative_effort` などを返す。  
ペースは `1000 / avg_speed / 60` で min/km に変換。  
（心拍は各アクティビティの stream を個別取得する必要があり重いので、  
強度は Strava の `relative_effort` で代用した。）  
![](https://static.zenn.studio/user-upload/928510b3bd37-20260630.png)  
*初めてのコネクタ利用*

### Cowork アーティファクトからの呼び出し

アーティファクト内では `window.cowork.callMcpTool` で両 MCP を叩ける。  
返り値は `{content, structuredContent, isError}` の形。

```
async function call(name, args) {
  const r = await window.cowork.callMcpTool(name, args || {});
  if (r.isError) throw new Error("tool error: " + name);
  return r.structuredContent ?? JSON.parse(r.content[0].text);
}
```

これで Strava のラン記録と HealthPlanet の体組成を取得し、Chart.js で

* 週間走行距離（直近12週）
* ペース推移（ラン毎・上ほど速い）
* 体重・除脂肪体重・体脂肪率の推移
* 最近のラン一覧

を描画。さらに `window.cowork.askClaude(prompt, data)` で、  
直近データを渡して **AIコーチの所見**（調子の評価／減量の質／翌週メニュー／補給）を生成する。

### 地味にハマる：askClaude は Markdown を返す

`askClaude` の出力をそのまま `textContent` に入れたら、`##` や `|表|` が生テキストで表示された。  
アーティファクトは CSP の都合で marked.js 等を読めない（Chart.js/Grid.js/Mermaid のみ）ので、  
**見出し・箇条書き・太字・表に対応した簡易 Markdown レンダラ**を自前で実装して `innerHTML` に流した。

### デザインも素の HTML/CSS で

「React や Tailwind を使いたい」と思ったが、アーティファクトのサンドボックスでは  
外部フレームワークを読み込めない。そこで CSS を作り込み、  
アクセントカラー（Stravaオレンジ）・カードの影・KPIタイル・表のホバーなどで  
フレームワーク無しでもモダンな見た目に寄せた。  
Claude Designとか使ってみても面白そうだったが、HTMLが散らかるためまたいつか。

## 学び・所感

* **既存コネクタが無くても、OAuth2 API があれば MCP は数時間で自作できました**。  
  FastMCP のおかげで実装の大半はツール定義に集中可能。
* **詰まるのは実装よりセットアップ**（JSON設定・パス・文字コード）。  
  エラーメッセージ（position / line）を信じて素直に直すのが近道。
* **「APIで取れるもの」と「欲しいユースケース」のギャップは計算とパワーで埋める**。  
  体重と体脂肪率だけでも、除脂肪体重やBMRを足せば一気にコーチらしくなる。
* ライブアーティファクト＋`askClaude` は、**データ取得から考察までを1画面**に  
  まとめられて気持ちいい。次は目標レースの設定と、毎朝の自動ブリーフィングを足したい。

## 完成品のイメージ

体重は恥ずかしいのでぼかしてます。  
上出来！モチベ爆上がりです  
![](https://static.zenn.studio/user-upload/f4f202262e9d-20260630.png)

## 参考リンク
