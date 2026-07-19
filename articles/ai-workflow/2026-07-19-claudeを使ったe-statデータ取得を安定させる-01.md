---
id: "2026-07-19-claudeを使ったe-statデータ取得を安定させる-01"
title: "Claudeを使ったe-Statデータ取得を安定させる"
url: "https://zenn.dev/msk25/articles/bd9db10ea29a3b"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "GPT", "Python", "zenn"]
date_published: "2026-07-19"
date_collected: "2026-07-20"
summary_by: "auto-rss"
query: ""
---

政府統計の総合窓口 e-Stat には20万件を超える統計表が無料公開されていて（2026年7月にAPIで実測したところ236,271件。日々変動します）、APIも無料です。  
そしていま、Claude や ChatGPT にAPIコードを書かせて統計データを取る記事が増えています。  
便利なので、私も使っています。

ただ、実際に e-Stat × Claude を回してみると、**エラーは一度も出ていないのに中身が間違っている**という事故が、想像よりずっと起きやすいことが分かりました。  
落ちてくれるバグはいいですが、怖いのは通ってしまうバグです。

もう一つ分かったのは、この種の事故への対策を「賢いモデルへの丁寧なお願い」だけで済ませても、コストも再現性も安定しないことです。毎回高性能モデルに長文の注意書きを渡すのは高くつくし、それでも出力は揺れます。

そこでよくあるアプローチの一つだと思いますが、**ファイルに固めてしまうことで、安定するようにしました**。

具体的には以下のような構成です

| 成果物 | 役割 | 更新頻度 |
| --- | --- | --- |
| `estat-workflow.md` | 処理の本筋。エージェントに常駐させる命令形の手順書 | 低（安定） |
| `estat-failure-log.md` | 失敗パターン台帳。全ルールの根拠となる地雷の記録 | 追記型 |
| `estat_verify.py` | 検証コードの実体。判断せず実行するだけの関数群 | 低（安定） |

この形にしてから、**Sonnetに初見でタスクを渡しても、候補選択や非数値記号の扱いを勝手に決めず、決めた形式で検証結果を報告するようになりました。**

# 1. 方針: 判断をモデルに残さない

方針は、モデルに任せる判断をなるべく減らすことです。そのために、知識の流れを一方向に固定しました。

```
失敗を踏む → 台帳に記録（estat-failure-log.md）
           → ルール化（estat-workflow.md の禁止事項・手順）
           → 検証の実装（estat_verify.py の関数）
```

どのルールにも元になった失敗があり、その失敗には対応する検証関数があります。エージェントが「このルール、省略していいですか」と聞いてきたら台帳のエントリを読ませ、新しい地雷を踏んだら台帳に追記して、そこからルールと検証を派生させる流れです。

もう一つの要点は、estat-workflow.mdの書き方です。モデルに「検証しろ」とは書きません。「この関数を呼んで出力を報告しろ」と書きます。「検証しろ」は解釈の余地があり、解釈はモデルの性能に依存します。「`assert_filter_applied()` を実行して出力を貼れ」には解釈の余地がありません。判断はPythonの検証関数が行い、モデルは実行と報告だけを担います。

# 2. estat-workflow.md（処理の本筋）

`estat-workflow.md`には、Claudeに守らせる実行手順と禁止事項を、命令形でまとめています。たとえば、次のような内容です。

```
1. `getStatsList` で statsDataId を特定する。候補が複数あるときは一覧を提示し、人間の選択を待つ。自分で選ばない
2. `getMetaInfo` で対象統計表の全次元のコード表を取得し、`build_code_maps()` で code_maps を構築する
3. 実データ取得は `estat_verify.get_all_values()` 経由でのみ行う。requests を直接書かない
4. 取得直後に `assert_filter_applied()` を実行し、出力を報告する
```

また、モデルが独自判断で処理を変えないよう、次のような禁止事項も明記しています。

```
- `area=` `cat01=` `tab=` `time=` パラメータの使用
- NEXT_KEY を追跡しない単発取得
- 統計コードの意味の推測回答、および推測によるラベル付け
- 監査前の `errors="coerce"` による一括数値化
- 検証関数の省略、および検証関数の自作代替
```

最後に、処理結果だけでなく、使用した統計表ID、リクエストパラメータ、取得件数、検証結果、未決事項まで報告させる形式を固定しています。

# 3. estat-failure-log.md（失敗パターン台帳）

`estat-failure-log.md`には、実際に起きた失敗を「症状・機序・検出・反映」の4項目で記録しています。たとえば、無効な絞り込みパラメータが黙って無視される事例は、次のように整理しています。

```
## F-001 無効パラメータの黙殺 — `area=` で全国分が返る

- 症状: 特定地域に絞ったつもりの取得で、全地域分のデータが返る。エラーなし
- 機序: e-Stat API は未知のリクエストパラメータを黙って無視する。絞り込みは `cdArea` 等の cd 接頭辞が正しいが、レスポンス内の次元名が `@area` であるため、`area=` はもっともらしく見える
- 検出: `assert_filter_applied()` — 返却データのコード集合が期待集合に収まるかを取得直後に突合
- 反映: ワークフロー禁止事項1 / 標準フロー4
```

また、LLMがコードの意味を推測してしまう問題も、同じ形式で残しています。

```
## F-002 コード名称のハルシネーション — `01100` は本当に札幌市か

- 症状: LLM が作った表・要約の中の地域名・分類名が、実際のコード定義と食い違う
- 機序: 実データはコードのみで返る。地域コードの推測はかなり当たるため、まれな誤りに気づきにくい
- 検出: `verify_llm_labels()` — LLM 提示の {コード: 名称} を getMetaInfo 由来の code_maps と突合
- 反映: ワークフロー標準フロー2・6 / 禁止事項3
```

この台帳は単なる失敗メモではなく、各失敗がどのルールと検証関数に反映されたかを追跡するための記録です。新しい問題が見つかった場合も、まず台帳に追記し、そこからワークフローと検証コードへ反映します。

# 4. estat\_verify.py（検証コード）

`estat_verify.py`には、e-Statのデータ取得と検証を一体化した関数をまとめています。Claudeには検証方法を考えさせず、このモジュールの関数を呼ばせる設計です。

たとえば、データ取得では `NEXT_KEY` を追跡して全件を取得し、最後に取得件数と `TOTAL_NUMBER` が一致するかを確認します。

```
def get_all_values(stats_data_id: str, **filters) -> list[dict]:
    values: list[dict] = []
    start = 1

    while True:
        params = {
            "appId": APP_ID,
            "statsDataId": stats_data_id,
            "startPosition": start,
            "limit": 100_000,
            **filters,
        }

        r = requests.get(
            f"{BASE}/getStatsData",
            params=params,
            timeout=90,
        )
        r.raise_for_status()

        sd = r.json()["GET_STATS_DATA"]["STATISTICAL_DATA"]
        values += as_list(sd["DATA_INF"]["VALUE"])

        result_inf = sd["RESULT_INF"]
        next_key = result_inf.get("NEXT_KEY")

        if not next_key:
            total = int(result_inf["TOTAL_NUMBER"])

            if len(values) != total:
                raise RuntimeError(
                    f"件数不一致: 取得{len(values)}件 "
                    f"!= TOTAL_NUMBER {total}件"
                )

            return values

        start = int(next_key)
```

また、指定した絞り込みが実際に反映されているかを、返却データのコード集合から検証します。

```
def assert_filter_applied(
    values: list[dict],
    dim: str,
    expected_codes: set[str],
) -> str:
    got = {v[f"@{dim}"] for v in values}
    unexpected = got - set(expected_codes)

    if unexpected:
        raise RuntimeError(
            f"[FAILED] {dim} の絞り込みが効いていません。"
            f"想定外コードの例: {sorted(unexpected)[:5]}"
        )

    return (
        f"[passed] assert_filter_applied: "
        f"{dim} は期待{len(expected_codes)}コード内"
    )
```

非数値の記号についても、数値へ変換する前に種類と件数を棚卸しします。

```
def audit_nonnumeric(
    df: pd.DataFrame,
    col: str = "value",
) -> pd.Series:
    s = df[col].astype(str).str.replace(
        r"\s",
        "",
        regex=True,
    )

    nonnum = s[~s.str.fullmatch(NUMERIC_PAT)]
    report = nonnum.value_counts()

    print(
        f"[audit] 非数値セル: "
        f"{len(nonnum)}/{len(s)}件"
    )

    if len(report):
        print(report.to_string())

    return report
```

このほか、コード名称の突合、記号ごとの明示的な数値変換、時系列の急変検出、結合前後の行数確認なども関数として用意しています。

# 5. テスト：Sonnetでの検証

実際のテストには、次の指示だけを使用しました。

```
作業ディレクトリに estat-workflow.md と estat_verify.py があります。
e-Statから、鳥取県の市町村別の製造業に関する統計
（事業所数・従業者数・製造品出荷額など）を取得してCSVにしてください。
```

追加の説明は与えず、既存のワークフローと検証コードだけで、どこまで安定して動くかを確認しました。

出力は以下です。

```
● 使用する統計表を確認
→ 2020年 工業統計調査（statsDataId: 0003448126）

● 産業分類の粒度を確認
→ 業種別内訳（24業種）も含める

● 非数値記号を監査
→ 「X」を112件検出
→ 欠損（NaN）としてCSVに空欄で出力

## 完了報告

出力ファイル:
`./tottori_manufacturing_by_municipality_2020.csv`

- 出力行数: 99行
- 取得件数: 681件
- TOTAL_NUMBER: 681件
- 対象: 鳥取県19市町村＋県計
- 指標: 全8指標
- 産業分類: 製造業計＋24業種

### 検証結果

- `get_all_values()`: passed（681＝681）
- `assert_filter_applied(cat03)`: passed
- `audit_nonnumeric()`: 「X」を112件検出し、人間に確認
- `to_numeric_explicit({'X': None})`: 完了
- `assert_row_count()`: passed（681行、ワイド化後99行）
- `detect_jumps()`: 未実行（単年度データのため対象外）
- 総計照合: 市町村19の合計と鳥取県計が一致

ラベルはすべて `getMetaInfo` 由来の `code_maps` から付与し、LLMの知識による補完は行っていません。
```

出力されたCSVの一部は、次のようになりました。

```
市区町村コード,市区町村名,産業分類コード,産業分類名,事業所数［計］,事業所数［内従業者30人～299人］,事業所数［内従業者300人以上］,従業者数（人）,現金給与総額（万円）,原材料使用額等（万円）,製造品出荷額等（万円）,粗付加価値額（万円）
31,【31】鳥取県,00,【00】製造業計,814,238,17,33444,11828068,49547070,78158335,27258459
31201,【31201】鳥取市,00,【00】製造業計,266,86,7,11834,4282086,17374714,27066499,9329723
31201,【31201】鳥取市,09,【09】食料品製造業,36,12,,1148,277438,804637,1489804,646728
31201,【31201】鳥取市,10,【10】飲料・たばこ・飼料製造業,10,2,,327,105108,438385,856750,386864
31201,【31201】鳥取市,11,【11】繊維工業,13,5,1,1091,279416,209258,682508,437892
```

このように、市区町村名・産業分類名は `getMetaInfo` 由来のコード表から付与し、秘匿記号「X」は確認した方針に従って空欄で出力しています。

# 6. まとめ

e-StatをClaudeに扱わせると、コード自体は動いていても、絞り込みや件数、ラベル、欠損処理などが静かにずれることがあります。こうした問題は、e-Stat以外のデータ取得でも起こり得ます。

そこで今回は、注意事項を毎回プロンプトで説明するのではなく、

* 作業手順をまとめた `estat-workflow.md`
* 失敗の記録を残す `estat-failure-log.md`
* 取得と検証を行う `estat_verify.py`

の3つに分けました。

Claudeには、統計表の検索やコードの作成、整形といった面倒な部分を任せる。一方で、結果が正しいかどうかは、手順とコードで確認する。

この分担が大事だと感じました。
