---
id: "2026-06-24-mulmoclaudeで自分専用の天気アプリをvibe-craftingしてみた-01"
title: "MulmoClaudeで自分専用の天気アプリをVibe Craftingしてみた"
url: "https://zenn.dev/michiof/articles/mulmoclaude-weather-app"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "Python", "JavaScript", "zenn"]
date_published: "2026-06-24"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

```
# JMA 天気予報コレクション 再現プロンプト

このプロンプトを別の MulmoClaude ワークスペースに貼り付ければ、気象庁の公式 API から全国主要都市の天気予報を定期取得し、テレビ天気予報風カスタムビューで閲覧できる schema-driven collection `jma-weather` を構築できます。LLM を経由しない pure Python スクリプトで取得し、定期実行はスケジューラに任せます。

---

## 0. ゴール

- `data/jma-weather/items/<office>-<YYYY-MM-DD>.json` に **1 都市 1 日 1 レコード** で天気を貯める schema-driven collection を作る
- 取得は `data/jma-weather/fetch.py`（stdlib のみ・LLM 不使用）が単独で完結する
- `config/scheduler/tasks.json` に **3 時間ごと interval 1 件** のスケジューラ登録（成功時は静音、失敗時のみ PushNotification）
- `/collections/jma-weather` のカスタムビュー「天気予報」で:
  - **指定地域モード**: 選択した都市から選んで今日 / 明日の詳細 + 週間 + 気象庁概要文 + 3 時間ごとストリップ
  - **全国モード**: Geolonia 日本地図 SVG（47 都道府県）に選択した都市のテレビ風カードを各都道府県の上 / 海側オフセットで直置き（`excludeFromNational: true` のフラグを付けた都市は除外）。地図 ⇔ リスト切替

---

## 0.5 ビルド開始前に: ユーザーに都市選択を聞く

**ファイル作成を始める前に必ず `presentForm` で以下 3 問をユーザーに聞いてください**:

```
Q1 (checkbox, multiSelect, defaultValue=全 11 都市): 取得対象とする都市（候補から）
  選択肢: 札幌 / 仙台 / 新潟 / 東京 / 横浜 / 名古屋 / 大阪 / 松江 / 高松 / 福岡 / 那覇
Q2 (textarea, optional): その他取得したい都市
  プレースホルダ: "例: 旭川, 金沢, 高知 (複数なら , または改行区切り)"
  ヘルプ: "候補に無い都市を追加します。コードは JMA の参照 JSON から自動で引きます"
Q3a (radio, defaultValue=横浜): あなたの「指定地域」(view の初期表示都市)
  選択肢: Q1 + Q2 で確定した都市 + 「その他（次の欄に都市名を入力）」
Q3b (text, optional): Q3a で「その他」を選んだ場合の都市名
  プレースホルダ: "例: 旭川"
  ヘルプ: "Q3a で『その他』を選択した場合のみ使う。Q2 と同様にコードを自動取得して取得対象にも追加する"
```

### Q2 で「その他」が入力された場合の処理

各都市名について以下の順で **JMA の参照 JSON を fetch して** コードを引く。1 つでも失敗したら presentForm で「<都市名> のコードを引けませんでした。スキップしますか？ / 別の名前で再試行？」と聞き直す。

1. **office** (6 桁、府県の予報区):
   - `https://www.jma.go.jp/bosai/common/const/area.json` を fetch
   - `offices` dict の各エントリの `name` を見て、入力した都市名の都道府県と一致するものを探す（例: "金沢" → "石川県" → office=170000）
   - 県名から逆引きしづらい場合は、`class10s` から市名を含むエントリの `parent` を辿ると確実

2. **area_code** (細分区域):
   - 同じ area.json の `class10s` から「都市が属する地方」を探す（例: 旭川 → "上川・留萌地方" → 012010）
   - 県名しか分からない場合は、その県の主要 class10 を 1 つ選ぶ（例: 神奈川県東部 = 140010）

3. **temp_code** (47xxx 気象官署):
   - `https://www.jma.go.jp/bosai/forecast/data/forecast/<office>.json` を fetch
   - `[1].timeSeries[1].areas[].area` を見て、都市名と一致する `name` の `code` を取る（例: 旭川 → 47407）
   - 一致が無ければ最初の気象官署を使う

4. **amedas_code** (5 桁、AMeDAS 地点):
   - `https://www.jma.go.jp/bosai/amedas/const/amedastable.json` を fetch
   - 値の `kjName` が入力都市名と一致するエントリの **キー**（5 桁）を取る

5. **order**: 候補 11 都市の order を保持し、その他都市は order=100 から連番で追加（並びは末尾に）

6. **placement (view の CITY_ORDER 用)**: 新都市は default `"center"` で OK。地図上の被りはユーザーが後で手動調整

### 回答結果

- `CITIES_CONFIG` と view の `CITY_ORDER` を **Q1 + Q2 + (Q3a=その他 のとき Q3b)** の合算で構成
- `DEFAULT_CITY_OFFICE`:
  - Q3a が候補から選ばれた → その都市の office
  - Q3a = 「その他」 → Q3b に書かれた都市のコードを自動引き、その office を採用（同時に CITIES_CONFIG にも追加）
- `excludeFromNational: true` は自動付与しない。完成後にユーザーが手動で付ける運用

### Q3a のデフォルト挙動

- Q1 に横浜が含まれている → Q3a デフォルト = 横浜
- Q1 に横浜が無い → Q3a デフォルト = Q1 + Q2 の中で最も order の若い都市（候補 11 の order 順を優先、その他は末尾）

**注意**: 自動化用のバックグラウンドワーカーから本プロンプトを実行する場合は form を出せないので、その場合は spawn 元の指示に従って「全 11 都市 + 横浜デフォルト」を直接採用してください。

## 1. 取得対象都市の候補 (最大 11)

`fetch.py` の `CITIES_CONFIG` で持つ。各都市は **2 種類のコード** が必要:

- `area_code`: 短期予報の細分区域（forecast / wdist VPFD で使用）
- `temp_code`: 週間予報の気温観測地点 (47xxx 系の気象官署コード)
- `amedas_code`: AMeDAS の point id（**temp_code とは別体系**、bosai/amedas で使用）

東京と横浜だけ偶然 temp_code = amedas_code だが、他都市は別の値なので両フィールド必須。

| order | office | name | region | area_code | temp_code | amedas_code |
|---|---|---|---|---|---|---|
| 1 | 016000 | 札幌   | 北海道   | 016010 | 47412 | 14163 |
| 2 | 040000 | 仙台   | 宮城県   | 040010 | 47590 | 34392 |
| 3 | 150000 | 新潟   | 新潟県   | 150010 | 47604 | 54232 |
| 4 | 130000 | 東京   | 東京都   | 130010 | 44132 | 44132 |
| 5 | 140000 | 横浜   | 神奈川県 | 140010 | 46106 | 46106 |
| 6 | 230000 | 名古屋 | 愛知県   | 230010 | 47636 | 51106 |
| 7 | 270000 | 大阪   | 大阪府   | 270000 | 47772 | 62078 |
| 8 | 320000 | 松江   | 島根県   | 320010 | 47741 | 68132 |
| 9 | 370000 | 高松   | 香川県   | 370000 | 47891 | 72086 |
| 10 | 400000 | 福岡  | 福岡県   | 400010 | 47807 | 82182 |
| 11 | 471000 | 那覇  | 沖縄本島 | 471010 | 47936 | 91197 |

既定の「指定地域」（DEFAULT_CITY_OFFICE）= `140000`（横浜）。`amedas_code` は `https://www.jma.go.jp/bosai/amedas/const/amedastable.json` の `kjName` 一致で引いた値。

---

## 2. ファイル構成

作成するもの:

- `data/skills/jma-weather/SKILL.md` — スキル説明（mc-manage-skills 経由でホストに登録される）
- `data/skills/jma-weather/schema.json` — コレクションのスキーマ
- `data/skills/jma-weather/views/news-weather.html` — カスタムビュー（Geolonia SVG をインライン展開した最終成果物）
- `data/skills/jma-weather/views/japan-map.svg` — Geolonia オリジナル SVG（pinned commit から取得、出典記載のため保持、boundary-line `<g>` 削除済み）
- `data/jma-weather/fetch.py` — 取得スクリプト
- `data/jma-weather/items/` — 出力ディレクトリ（空でよい）
- `config/scheduler/tasks.json` に 1 件追記

`data/jma-weather/raw/` は使わない（v1 にはあったが v2 では生 JSON を保存していない。直接 items にだけ書き出す）。

---

## 3. fetch.py の仕様

### エンドポイント（4 つ）

1. **短期予報**: `https://www.jma.go.jp/bosai/forecast/data/forecast/<office>.json`（府県天気予報。1 日 1 個の天気コード + 6h 降水確率バンド + 1 日 2 点気温）
2. **概要文**: `https://www.jma.go.jp/bosai/forecast/data/overview_forecast/<office>.json`
3. **地域時系列予報 (wdist VPFD)**: `https://www.jma.go.jp/bosai/jmatile/data/wdist/VPFD/<area_code>.json`（**3 時間ごとの天気・気温・風**）
4. **AMeDAS 観測**: today レコードの「現在気温・直近降水量」用
   - 最新観測時刻: `https://www.jma.go.jp/bosai/amedas/data/latest_time.txt`
   - 地点ブロック: `https://www.jma.go.jp/bosai/amedas/data/point/<amedas_code>/<YYYYMMDD_HH>.json`
     - 3h 境界ブロック単位、10 分間隔観測 18 個を含む
     - 24h カバーに 8 ブロック取る（3h × 8）
     - precipitation10m を 10 分間隔で重複なく合計（1h=6 点 / 6h=36 点 / 24h=144 点）
     - **min/max は AMeDAS から取らない**（予報値の方が「今日これから何度になるか」が分かって実用的）

### 引数

- `--only <office>` 単一都市だけ取得（既定: CITIES_CONFIG の全都市）
- `--out-dir` 既定 `data/jma-weather/items`
- `--sleep` 都市間 sleep（既定 0.3 秒）

### 1 回の取得で書き出されるもの

各都市について短期予報 + 週間予報を取得 → 日付ごとにマージ → 1 日 1 レコード化:

- **今日** (`source: "today"`) — 短期予報の最初の日。weather/min/max/wind/wave/popsByBand + `overviewText` + **AMeDAS 観測値**（currentTemp / precip1h / precip6h / precip24h / precipAsOf）
- **明日** (`source: "tomorrow"`) — 短期予報 2 日目。時間帯別降水確率まで
- **3〜9 日後** (`source: "weekly"`) — 週間予報。`weather/min/max/pop/reliability`
- **過去日** (`source: "past"`) — 後述の demote ロジックで降格された旧 today/tomorrow

加えて wdist VPFD の取得結果を **日付ごとに分割** して、該当日のレコードの `hourly` フィールドに格納:
```json
"hourly": [
  { "time": "12:00", "datetime": "2026-06-21T12:00:00+09:00",
    "weather": "晴れ", "weatherIcon": "☀️", "temp": "25",
    "windDir": "南西", "windSpeed": 4 },
  ...
]
```
通常は今日 + 明日 (+ 明後日の途中まで) に hourly が入る。

### 重要な実装注意点

#### a. 気温の min/max は予報値 + 既存値保持ロジック

JMA は 5 時発表で今日の min/max を載せるが、17 時発表では翌日のみになる等、発表時刻で挙動が不安定。そのため `fetch_city()` は **書き出し前に既存レコードを Read し、新値が空欄なら既存値を維持** する。これで朝 5 時に取った今日の min/max が 17 時発表後も保持される。

ヘルパ:
```python
existing = json.loads(out_path.read_text()) if out_path.exists() else {}
def keep(field, new_val):
    if new_val not in (None, ""):
        return new_val
    return existing.get(field, "")
```

短期予報の temps 配列は値そのものを比較して min/max を取る（`min == max` のときは max だけ保持）。配列順が `[09:00, 00:00]` でも `[00:00, 09:00]` でも正しい結果になる。

#### b. 過去日 today/tomorrow の自動降格 (`demote_past_today_records`)

`classify_source()` は fetch 時の `today_iso` を元に source を付けるため、日付が進むと過去日のレコードに古い `today` / `tomorrow` ラベルが残る。ビューは `source === "today"` で find するので、複数の today レコードがあると **古い (空欄混じりの) 方** を拾ってしまう（日付昇順ソートのため）。

`fetch_city()` の冒頭で `demote_past_today_records(out_dir, office, today_iso, now_iso)` を呼び、過去日の `today` / `tomorrow` レコードを以下のように書き換える:
- `source` → `"past"`
- `dayLabel` → 「N 日前」「昨日」など
- weather / min / max / precip* などの値自体は **消さない** (観測値の履歴として残す)

#### c. 90 日より古いレコードの自動削除 (`cleanup_old_records`)

`main()` の最後で `cleanup_old_records(out_dir, today_iso, keep_days=90)` が走る。ファイル名から日付を抽出し、cutoff 以前は unlink。天気予報の履歴は実用上見返さないため、ストレージ/表示速度対策で自動掃除する。

#### d. 短期予報 vs 週間予報のマージ

同じ日付があれば **短期予報が勝つ**（情報が多いため）。週間にしか無い `reliability` は温存。

#### e. JMA 天気コード → 絵文字マップ

- 100 番台 = 晴れ系 → ☀️、雨/雪混じり → 🌦️、曇り混じり → ⛅
- 200 番台 = 曇り系 → ☁️、雨混じり → 🌧️、雪混じり → 🌨️
- 300 番台 = 雨 → 🌧️
- 400 番台 = 雪 → ❄️
- コードに「雷」を含むものは ⛈️（テキスト判定）

wdist 用に別途短い `wdist_weather_icon()` も用意:
- 「晴れ」 → ☀️、「くもり」 → ☁️、「雨」 → 🌧️、「雪」 → ❄️、「雷」を含む → ⛈️、「晴れ＋くもり混じり」 → ⛅

#### f. エラー

1 都市でも成功すれば exit 0、全失敗で exit 1。AMeDAS 一部ブロック取得失敗は warn だけ出して該当フィールドは空のまま（ブロッカーにしない）。

### レコード形状（`data/jma-weather/items/<office>-<YYYY-MM-DD>.json`）

```json
{
  "id": "140000-2026-06-21",
  "office": "140000",
  "cityName": "横浜",
  "regionName": "神奈川県",
  "cityOrder": 5,
  "date": "2026-06-21",
  "weekday": "日",
  "dayLabel": "今日",
  "source": "today",
  "areaCode": "140010",
  "areaName": "神奈川県 横浜",
  "publishingOffice": "横浜地方気象台",
  "reportDatetime": "2026-06-21T05:00:00+09:00",
  "updatedAt": "2026-06-21T18:01:00+09:00",
  "weather": "...",
  "weatherCode": "201",
  "weatherIcon": "☁️",
  "min": "21",
  "max": "29",
  "pop": "30",
  "popsByBand": "06-12: 40% / ...",
  "currentTemp": "25.3",
  "precip1h": "0.0",
  "precip6h": "2.5",
  "precip24h": "12.0",
  "precipAsOf": "2026-06-21T11:50:00+09:00",
  "wind": "南の風",
  "wave": "1メートル",
  "reliability": "",
  "overviewText": "...",
  "hourly": [{ "time": "12:00", "weatherIcon": "☀️", ...}, ...],
  "summary": "横浜 今日 (日) | ☁️ ... | 21/29℃ | 降水 30%"
}
```

### 標準出力
- 成功時最終行: 既定都市（横浜）の `summary` を 1 行出力
- 失敗時: stderr にエラー

---

## 4. schema.json

⚠️ **重要**: MulmoClaude ホストは type が `string` / `number` / `enum` / `date` / `markdown` / `text` / `file` / `derived` / `table` / `toggle` のみ対応。`type: "json"` を入れると **スキーマ全体が無効化されてコレクションが一覧に出なくなる**。`hourly` のような構造化データはスキーマに宣言しないこと（レコード JSON にデータは残り、custom view の JS から `r.hourly` で読める）。

```json
{
  "title": "気象庁 天気予報",
  "icon": "partly_cloudy_day",
  "dataPath": "data/jma-weather/items",
  "primaryKey": "id",
  "displayField": "summary",
  "calendarField": "date",
  "sortField": "cityOrder",
  "sortOrder": "asc",
  "views": [
    {
      "id": "news",
      "label": "天気予報",
      "icon": "wb_sunny",
      "file": "views/news-weather.html",
      "capabilities": ["read"]
    }
  ],
  "fields": {
    "id":               { "type": "string", "label": "ID", "primary": true, "required": true },
    "office":           { "type": "string", "label": "office code" },
    "cityName":         { "type": "string", "label": "都市" },
    "regionName":       { "type": "string", "label": "地域" },
    "cityOrder":        { "type": "number", "label": "都市並び順" },
    "date":             { "type": "date",   "label": "日付" },
    "weekday":          { "type": "string", "label": "曜日" },
    "dayLabel":         { "type": "string", "label": "区分" },
    "source":           { "type": "enum",   "label": "情報源", "values": ["today", "tomorrow", "weekly", "past"] },
    "summary":          { "type": "string", "label": "サマリ" },
    "weather":          { "type": "string", "label": "天気" },
    "weatherCode":      { "type": "string", "label": "JMA 天気コード" },
    "weatherIcon":      { "type": "string", "label": "天気アイコン" },
    "min":              { "type": "string", "label": "最低気温 (℃)" },
    "max":              { "type": "string", "label": "最高気温 (℃)" },
    "currentTemp":      { "type": "string", "label": "現在気温 (℃)", "help": "今日のみ。AMeDAS 観測値" },
    "pop":              { "type": "string", "label": "降水確率 (%)" },
    "popsByBand":       { "type": "string", "label": "時間帯別降水確率" },
    "precip1h":         { "type": "string", "label": "直近1h降水量 (mm)" },
    "precip6h":         { "type": "string", "label": "直近6h降水量 (mm)" },
    "precip24h":        { "type": "string", "label": "直近24h降水量 (mm)" },
    "precipAsOf":       { "type": "string", "label": "観測基準時刻" },
    "wind":             { "type": "string", "label": "風" },
    "wave":             { "type": "string", "label": "波" },
    "reliability":      { "type": "string", "label": "信頼度" },
    "overviewText":     { "type": "markdown", "label": "概要文" },
    "areaCode":         { "type": "string", "label": "細分区域 area code" },
    "areaName":         { "type": "string", "label": "地域名" },
    "publishingOffice": { "type": "string", "label": "発表気象台" },
    "reportDatetime":   { "type": "string", "label": "発表日時" },
    "updatedAt":        { "type": "string", "label": "取得時刻 (ISO)" }
  }
}
```

`hourly` フィールドは schema.json **に宣言しない**（type: "json" がエラーになるため）。

---

## 5. カスタムビュー `views/news-weather.html`

ダーク背景のテレビ天気予報風 UI。

### 外観・パレット

CSS 変数:
- `--bg-grad`: `linear-gradient(180deg, #0b1530 0%, #122150 60%, #1a2f70 100%)`
- `--accent`: `#ffd83d` （黄色アクセント）
- `--accent2`: `#4cb6ff` （水色）
- `--warm`: `#ff8866` （最高気温）
- `--cool`: `#4cd6ff` （最低気温）
- `--land`: `#2a4677` （陸の塗り）
- `--land-stroke`: `rgba(255, 255, 255, 0.18)` （都道府県境）
- `--land-highlight`: `#3a5da0` （対象 10 都道府県の塗り）
- `--ocean`: `rgba(8, 20, 50, 0.4)` （海）

### 構成

- 上部:
  - ブランド「天気予報」 + 「更新 MM/DD HH:MM」（最新 updatedAt）
  - 都市ドロップダウン（ユーザーが選択した N 都市）
  - 右上トグル `[指定地域] [全国]`（黄色 pill）
- **指定地域モード**:
  - hero: 今日 / 明日の大カード（巨大アイコン・最高/最低気温・降水確率・風・波・**3 時間ごとストリップ** = `hourly` 配列 + **6 時間バンド降水バー**）
  - weekly: 7 日間ストリップ（曜日 / 日付 / アイコン / 気温 / 降水）
  - overview: 気象庁概要文（markdown）
- **全国モード**:
  - インナータブ: `[今日] [明日]` の day-tabs + `[地図] [リスト]` の layout-tabs
  - 地図モード（既定）: 日本地図 SVG に 10 都市のミニカードを各都道府県の上 / 海側オフセットで直置き
  - リストモード: 10 都市横長カードグリッド
  - 全国モードでは横浜のカードを描画しない

### 日本地図 SVG

- 取得元: `https://github.com/geolonia/japanese-prefectures` の `map-full.svg`
- **pinned commit**: `90c5b4b8260de058d3db61b3cb8bfb6f67a81f9a` （2025-10-30）
- **sha256**: `3b4b9aef5c6282675dc8f04fc1002af13c09e2feec7c1d130cb4038856c64497`
- **ライセンス**: GFDL（Wikipedia 日本地図ベース）。view 右下に「地図: Geolonia / Wikipedia (GFDL)」を表示
- 取得手順:
  1. `curl` or Python urllib で `https://raw.githubusercontent.com/geolonia/japanese-prefectures/90c5b4b8260de058d3db61b3cb8bfb6f67a81f9a/map-full.svg` を `data/skills/jma-weather/views/japan-map.svg` に保存
  2. **ダウンロード直後**に sha256 を確認 (上記の値と一致するか) → 一致しなければ pinned commit の取得が失敗している
  3. `grep -iE 'script|onclick|onload|onerror|onmouse|javascript:|foreignObject|iframe' japan-map.svg` で何も出ないことを確認
  4. **`<g class="boundary-line">` 全体を削除**: 元 SVG に沖縄 inset と本土の間に引かれた白い斜線（`<line>` 2 本）があり、那覇カードと衝突するため。沖縄の `transform="translate(52, 193)"` はそのまま保持
  5. 削除後の sha256 は元と異なるが、それで正しい (削除前 sha256 はダウンロード整合性チェック用、削除後は内容変更のため一致しない)
- view への展開: HTML に `<!--__GEOLONIA_SVG__-->` プレースホルダを置き、Python で SVG 本体（boundary-line 削除後）を置換してインライン化
- 47 都道府県を含み viewBox は 1000×1000。各 prefecture は `<g class="<prefecture-name> [region] prefecture" data-code="1..47">` 形式
- CSS は Geolonia の inline `fill="#EEEEEE"` を `.prefecture { fill: var(--land); stroke: var(--land-stroke); stroke-width: 0.6; }` で上書き
- `.prefecture.highlight` で対象 10 都道府県を `fill: var(--land-highlight)` に

### 地図コンテナの高さ

```css
.map-wrap {
  width: min(100%, 80vh);
  margin: 0 auto;
  aspect-ratio: 1 / 1;
}
```
viewport 高さの 80% を上限にし、スクロールなしで全国モードが 1 画面で収まるようにする。

### 都市カードの配置 (CITY_ORDER)

ユーザーが選んだ N 都市について、所属都道府県 class 名 (`pref`) + bbox 内の `xPct`/`yPct` (0–1) + `placement` を持つ。下記は全 11 候補の値（選択されなかった行は CITY_ORDER から除く）:

```js
const CITY_ORDER = [
  { office: "016000", name: "札幌",   pref: "hokkaido",  xPct: 0.18, yPct: 0.70, placement: "center" },
  { office: "040000", name: "仙台",   pref: "miyagi",    xPct: 0.45, yPct: 0.50, placement: "E" },
  { office: "150000", name: "新潟",   pref: "niigata",   xPct: 0.50, yPct: 0.30, placement: "N" },
  { office: "130000", name: "東京",   pref: "tokyo",     xPct: 0.45, yPct: 0.09, placement: "E" },
  { office: "140000", name: "横浜",   pref: "kanagawa",  xPct: 0.65, yPct: 0.40, placement: "center", excludeFromNational: true },
  { office: "230000", name: "名古屋", pref: "aichi",     xPct: 0.45, yPct: 0.20, placement: "S" },
  { office: "270000", name: "大阪",   pref: "osaka",     xPct: 0.55, yPct: 0.45, placement: "N" },
  { office: "320000", name: "松江",   pref: "shimane",   xPct: 0.80, yPct: 0.50, placement: "N" },
  { office: "370000", name: "高松",   pref: "kagawa",    xPct: 0.55, yPct: 0.55, placement: "S" },
  { office: "400000", name: "福岡",   pref: "fukuoka",   xPct: 0.40, yPct: 0.30, placement: "center" },
  { office: "471000", name: "那覇",   pref: "okinawa",   xPct: 0.88, yPct: 0.40, placement: "center" },
];
const NATIONAL_CITIES = CITY_ORDER.filter((c) => !c.excludeFromNational);
```

### ピン位置の計算 + placement オフセット

SVG 描画後に各都道府県 `<g>` の `getBoundingClientRect()` を取り、map-wrap に対する % で `left`/`top` を計算。さらに `placement` によって CSS の `transform` を方向別オフセット:

```css
.pin[data-place="N"]  { transform: translate(-50%, calc(-50% - 70px)); }
.pin[data-place="S"]  { transform: translate(-50%, calc(-50% + 70px)); }
.pin[data-place="E"]  { transform: translate(calc(-50% + 70px), -50%); }
.pin[data-place="W"]  { transform: translate(calc(-50% - 70px), -50%); }
.pin[data-place="NE"] { transform: translate(calc(-50% + 50px), calc(-50% - 50px)); }
.pin[data-place="NW"] { transform: translate(calc(-50% - 50px), calc(-50% - 50px)); }
.pin[data-place="SE"] { transform: translate(calc(-50% + 50px), calc(-50% + 50px)); }
.pin[data-place="SW"] { transform: translate(calc(-50% - 50px), calc(-50% + 50px)); }
/* center は通常の translate(-50%, -50%) で都道府県の上 */
```

JS:
```js
function getPinPosition(c, svgEl, wrapEl) {
  const g = svgEl.querySelector("." + c.pref);
  if (!g) return null;
  const gRect = g.getBoundingClientRect();
  const wrapRect = wrapEl.getBoundingClientRect();
  if (!gRect.width || !wrapRect.width) return null;
  const xPx = (gRect.x - wrapRect.x) + gRect.width * c.xPct;
  const yPx = (gRect.y - wrapRect.y) + gRect.height * c.yPct;
  return { xPct: (xPx / wrapRect.width) * 100, yPct: (yPx / wrapRect.height) * 100 };
}
```

`renderMap` は `requestAnimationFrame(() => requestAnimationFrame(...))` で SVG のレイアウト完了を待ってからピンを描画する。

placement の選び方の指針（被り回避）:
- 仙台: E（太平洋側へ）
- 東京: E（南東の太平洋へ。Izu 諸島側に伸ばさない）
- 名古屋: S（南の海へ）
- 大阪: N（北の北陸海へ。京都側）
- 新潟: N（日本海側へ）
- 松江: N（日本海側へ）
- 高松: S（瀬戸内海から南の海へ）
- 福岡: center（W だと地図外にはみ出すため）
- 札幌・横浜・那覇: center
- 引き出し線（カードと都道府県を繋ぐ線）は試したが視覚的に不自然だったので **付けない**

### カード（pin-card）の見た目 — 台座型

- 位置: `transform: translate(-50%, -50%)` + placement 追加オフセット（上記）
- **pin-dot は廃止**（カード自体がマーカー）
- 背景: `rgba(8, 18, 45, 0.92)`、`backdrop-filter: blur(6px)`
- 境界: `1px solid rgba(255, 216, 61, 0.45)`（黄色アクセント）
- 内部: 縦並び（都市名 / アイコン / 気温 / 降水）
- フォントサイズ:
  - base 12px、`pin-city` 13px 太字、`pin-icon` 30px、`pin-temp` 16px 太字（`.min` 13px）、`pin-pop` 11px
  - padding `7px 12px 6px`、min-width 70px、border-radius 11px
- ホバー: `transform` は変えず、border 黄色強調 + box-shadow

### 温度表示の特別ロジック

JMA が 5:00 発表で今日の `min == max` を返すケースが多い。`min === max` のときは **1 値だけ表示** (`30℃` だけ、スラッシュなし)。view 内ヘルパー:
- `renderHeroTemp(min, max)` — hero カード用
- `renderWeekTemps(min, max)` — 週間ストリップ用
- `renderPinTemp(min, max)` — 地図カード用
- `renderListTemp(min, max, pop)` — リストカード用

すべて「`!min || min === max` → 単一値、`!max` → min を単一値、else → max / min」のロジック。

### 3 時間ごとストリップ (hourly-strip)

hero カード内、降水バンドより上に配置。`r.hourly` 配列を直接描画:
```html
<div class="hourly-strip">
  <div class="h-cell">
    <div class="h-time">12:00</div>
    <div class="h-icon">☀️</div>
    <div class="h-temp">25°</div>
    <div class="h-wind">南西</div>
  </div>
  ...
</div>
```
横スクロール可能 (`overflow-x: auto`)。今日 + 明日 + 明後日朝までカバー（最大 12-13 セル）。

### 出典表示

view 右下に小さく:
```html
<div class="map-attrib">地図: <a href="https://github.com/geolonia/japanese-prefectures" target="_blank" rel="noopener">Geolonia / Wikipedia</a> (GFDL)</div>
```

### 動作上の他のポイント

- データ取得: `window.__MC_VIEW.dataUrl` から Bearer token で全レコード GET、クライアント側で都市・日付フィルタ
- 都市ドロップダウンは `CITY_ORDER`（選択した N 都市）、地図 / リストは `NATIONAL_CITIES`（excludeFromNational が付いた都市を除いた M 都市）
- カードクリックで指定地域モードに遷移し、その都市の詳細を表示
- 全国地図モードはウィンドウリサイズ時に `renderMap` を再実行

---

## 6. スケジューラ登録 — interval 1 件

`config/scheduler/tasks.json` に 1 件だけ追加。

```json
{
  "id": "jma-weather-fetch",
  "name": "JMA weather fetch (every 3h, silent)",
  "description": "3 時間ごとに気象庁の天気予報を取得し、data/jma-weather/items/<office>-<date>.json を最新化する。成功時は静音、失敗時のみ PushNotification。",
  "schedule": { "type": "interval", "intervalMs": 10800000 },
  "missedRunPolicy": "skip",
  "enabled": true,
  "roleId": "general",
  "prompt": "気象庁の天気予報を取得します。確認は不要。すぐに以下を実行してください。\n\n1. Bash で `python3 data/jma-weather/fetch.py` を実行する。\n2. 成功時 (exit 0): 何も出力しない。チャット返信なし、通知なし。\n3. 失敗時 (exit != 0): PushNotification で title=「JMA 天気予報 取得失敗」、body=stderr の最後の 200 文字程度。チャットにもエラー内容を返す。\n\n他の処理はしない。要約や解説は不要。",
  "createdAt": "<ISO now>",
  "updatedAt": "<ISO now>"
}
```

`intervalMs: 10800000` = 3 時間。サーバー起動時刻基準で発火するので時刻アンカーはないが、JMA は 5:00 / 11:00 / 17:00 JST に発表するので 3 時間ごとで十分追従できる。

---

## 7. SKILL.md

`data/skills/jma-weather/SKILL.md` には YAML frontmatter（`name: jma-weather` + 簡潔な description）と、上記の仕組みを要約した本文を書く。description はユーザーが「今日の天気」「全国の天気」「週間予報」「気象庁から取り込んで」などと言ったときに発火するキーワードを含める。

---

## 8. 完成後の検証

1. `python3 data/jma-weather/fetch.py` を実行
2. exit 0、stdout 最終行に「横浜 今日 (X) | <icon> <weather> | min/max℃ | 降水 N%」が出る
3. `data/jma-weather/items/` に **N 都市 × 7〜9 ファイル**（N = ユーザー選択数。全 11 選択なら 77〜99）
4. 今日の横浜レコードに `currentTemp` / `precip1h` / `precip6h` / `precip24h` / `precipAsOf` が入っている
5. 今日の横浜レコードに `hourly` 配列（時刻 / 天気 / 気温 / 風向）が入っている
6. `/collections/jma-weather` を開き:
   - 標準テーブル / カレンダー表示が出る
   - カスタムビュー「天気予報」が一覧から選べる
   - ビューを開くと指定地域モード（横浜）の hero 2 枚 + 3h ストリップ + 6h 降水バー + 週間 7 列 + 概要が出る
   - 「全国」→「地図」で 10 都市カードが日本地図の上 / 海側オフセットで並ぶ
   - 「全国」→「リスト」で 10 都市の横長カードが並ぶ
   - 10 都道府県（北海道・宮城・新潟・東京・愛知・大阪・島根・香川・福岡・沖縄）が highlight 色で塗られている
   - 沖縄インセットと本土の間に白い境界線が無い
   - 右下に「地図: Geolonia / Wikipedia (GFDL)」と出ている

---

## 補足: ユニットテストのススメ

JMA fixture を Python に直書きして parser をオフラインで検証するテストを `/tmp/test_jma_fetch.py` などに置くと、ネットワーク不要で回せて再現の信頼性が上がる。テストすべき項目:

- 気温の `[09:00, 00:00]` 逆順 + 同値重複ケースで `min == max` が正しく出る
- 短期予報 + 週間予報のマージで日付重複時に短期が勝つ
- 全 11 都市が `CITIES_CONFIG` に含まれる
- `--only <office>` で単一都市だけ取得できる
- `demote_past_today_records` が過去日 today を `past` に書き換える
- `cleanup_old_records` が 90 日より古いファイルだけ削除する
- 既存値保持ロジック: 既存に min=22 / max=28 がある状態で新値 min=空 / max=空 が来たら 22/28 が残る
```
