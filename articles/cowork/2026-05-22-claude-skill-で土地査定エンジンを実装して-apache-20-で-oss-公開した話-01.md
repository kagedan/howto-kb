---
id: "2026-05-22-claude-skill-で土地査定エンジンを実装して-apache-20-で-oss-公開した話-01"
title: "Claude Skill で土地査定エンジンを実装して Apache 2.0 で OSS 公開した話"
url: "https://qiita.com/Matsda_K/items/f1f362c189d33fc52a80"
source: "qiita"
category: "cowork"
tags: ["API", "AI-agent", "LLM", "cowork", "Python", "qiita"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

不動産鑑定士として 20 年ほど査定業務に関わってきた立場から、「価格の根拠を全部開示する AVM」を Claude Skill として実装し、Apache License 2.0 で公開した。リポジトリは [signal-yield/tochi-satei-kun](https://github.com/signal-yield/tochi-satei-kun) にある。

本記事はプロダクト紹介ではなく、Claude Skill という配布形態を採用した実装上の判断と、その過程でハマったポイント（特に LLM 経由の xlsx 生成にまつわるハルシネーション対策）を整理したものである。査定ロジックそのものはヘドニック対数線形 OLS という古典的手法を `statsmodels` で素直に書いただけで、新規性は無い。新規性があるとすれば、**回帰係数・補正率・採用事例をすべて xlsx に書き出して開示する** という設計と、それを **Claude Skill としてエンドユーザーに直接配布する** という構成にある。

本ツールの背景・思想・公開に至った経緯は note 記事（https://note.com/matsudansyaku/n/ne64248c287b6?app_launch=false）および [公式 LP](https://signal-yield.github.io/tochi-satei-kun/) を参照されたい。本記事は技術詳細に絞る。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4436261/c588c5ae-0ec3-433f-b110-c434d2c172d2.png)

## 2. なぜ Claude Skill だったのか

OSS AVM を業務担当者の手元で動かしてもらうには、配布形態の摩擦が課題になる。Web アプリにすればホスティング費とアカウント管理が要る。デスクトップアプリにすればコード署名と更新配信が要る。CLI にすれば Python 環境構築のハードルでほぼ全員が脱落する。

Claude Skill（Claude Cowork 上のプラグイン）を選んだ理由は次の 3 点に尽きる。

1. **配布が `/plugin install` の 1 行で済む。** 既に Cowork を使っている業務担当者は環境構築をゼロから始めなくてよい。
2. **対話 UI が標準で付いてくる。** 物件情報の聞き取り（面積、最寄駅、形状、接道、用途地域……）は自然言語で済ませられる。CLI で 8 個のフラグを覚えてもらう必要が無い。
3. **既存の Python 資産がそのまま使える。** Skill 本体は SKILL.md と Python スクリプトの集合なので、`pandas` / `statsmodels` / `openpyxl` をそのまま呼べる。

トレードオフとして、Cowork サンドボックスとファイル配布層に由来する制約（後述）を全部こちらで吸収する必要がある。実装の少なくない部分がこの吸収コードに割かれている。

## 3. システム全体構成

スキル起動時、Cowork 側の Claude が SKILL.md の指示に従って `python scripts/main.py` を 1 回呼ぶ。`main.py` は次の 8 段パイプラインを順に回し、最後に xlsx を吐く。

| # | 処理 | スクリプト |
|---|---|---|
| ① | MLIT 取引価格情報 CSV 読込・列名正規化 | `load_mlit.py` |
| ② | 市区町村スコープ・IQR 外れ値除外 | `scope.py` |
| ③ | 公示地価による時点修正（直近 1 年変動率） | `time_adjust.py` |
| ④ | ヘドニック回帰（対数線形 OLS）→ 係数辞書 | `hedonic.py` |
| ⑤ | 類似事例抽出（重み付き距離 top 3） | `similarity.py` |
| ⑥ | 個別格差補正の適用 | `correction.py` |
| ⑦ | 比準価格集約・価格レンジ生成 | `aggregation.py` |
| ⑧ | 3 シート xlsx 出力（業者用 / 附属資料 / 顧客用） | `xlsx_writer.py` |


入力は 2 ファイル（MLIT 取引価格情報 CSV、地価公示 GeoJSON）。出力は 1 ファイル（3 シートの xlsx）。中間で機械学習モデルを永続化することは無い。**係数は都度回帰で算定する。** 「地区と期間が変われば係数も変わる」という統計的事実そのものを白箱性の根拠として残すためで、固定係数を出荷物にはしていない。

## 4. SKILL.md の設計

Skill の振る舞いは `skills/tochi-satei-kun/SKILL.md` 1 ファイルに集約している。Cowork 側の Claude はこのファイルを読んでスキル起動を判断する。冒頭はこんな具合に書いている。

```markdown
---
name: tochi-satei-kun
description: Apache 2.0 で公開する OSS AVM（当社調べ・2026 年 5 月時点）。
  日本の土地（更地・所有権）の査定価格を MLIT 取引事例から統計的に算定する
  白箱 AVM スキル。…（中略）…トリガー語例：「土地の査定」「査定書を作って」
  「いくらで売れる」「相場感」「取引事例から」「比準価格」「公示価格と比べて」
  「AVM」「自動査定」など。
---

# 土地価格査定クン

## 起動時の絶対命令

本スキル起動時は必ず `python scripts/main.py` を実行する。
openpyxl を直接呼んで xlsx を生成することは禁止。
```

`description` フィールドには **トリガー語を機械的に列挙する** 方針を採った。「ヘドニック」「回帰」「白箱」を知らない業務担当者の語彙（「相場感」「いくらで売れる」「査定書」）でも意味マッチングで確実にフックさせるためだ。

[スクショ：SKILL.md 冒頭（`description` と「起動時の絶対命令」が見えている状態）]

「起動時の絶対命令」セクションが本記事の主題に直結する。これを書かないと Cowork 側の Claude が **自前で openpyxl を呼んで「それらしい」xlsx を生成する** ことがある。次節で扱う。

## 5. ハルシネーション対策の 4 条件

LLM 経由で xlsx を生成する設計の最大のリスクは、**Skill が起動されず、汎用 LLM が捏造 xlsx を返してしまう**ことだ。実際に開発中、ユーザーが Cowork の「利用可能スキル」リストで `tochi-satei-kun` を ON にし忘れたケースで、それらしいが係数表もヘドニック回帰サマリも無い 15 KB 程度の xlsx が返ってきた事例がある。出力結果だけ見ると「動いている」ように見えるため、検知が遅れる。

これに対して **「本物判定 4 条件」** を実装層と運用層の両方に埋め込んだ。

### 条件 1: ファイルサイズ 40 KB 以上

3 シート構成で比準表・係数表・グラフを描くと、最小構成でも 40 KB を超える。10〜20 KB は捏造の疑いが強い。

### 条件 2: シート 3 枚構成

業者用 / 附属資料（グラフ専用）/ 顧客用の 3 枚。汎用 LLM の捏造は 1 〜 2 枚で済ませる傾向がある。

### 条件 3: A1 セルの認証マーカー

業者用シート A1 セルに固定文字列 `tochi-satei-kun v1.4.2 認証出力` を書き込んでいる。`xlsx_gyosha_sheet.py` の該当箇所はこうなっている。

```python
# 認証マーカー（A1）— ハルシネーション出力との判別用
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
_set(ws, r, 1, "tochi-satei-kun v1.4.2 認証出力",
     font=Font(name="游ゴシック", size=8, italic=True, color="808080"),
     align=Alignment(horizontal="left", vertical="center"))
r += 1
```

合わせて `Workbook.properties` にも認証情報を埋める。Excel の「ファイル → 情報 → プロパティ」で確認できる。

```python
def write_xlsx(ctx: dict, output_path: Path) -> Path:
    wb = Workbook()
    wb.properties.creator = "tochi-satei-kun v1.4.2"
    wb.properties.description = (
        "土地価格査定クン (tochi-satei-kun) — Apache License 2.0 OSS AVM. "
        "https://github.com/signal-yield/tochi-satei-kun"
    )
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]
    _write_gyosha_sheet(wb, ctx)
    _write_kokyaku_sheet(wb, ctx)
    _apply_page_setup(wb, ctx.get("target", {}))
    wb.save(output_path)
    return output_path
```

### 条件 4: 業者用シートに「■ ヘドニック回帰サマリ」セクション

業者用シートの末尾に、全 12 特徴量の β / 標準誤差 / p 値と adjusted R² を出力する。汎用 LLM がこのセクションまで構造を真似て捏造することはまず無い。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4436261/8097fe3c-fd57-4dd6-aec9-836ce59a5a58.png)


この 4 条件は INSTALL.md / README.md にも掲載して、受け取った xlsx を視覚的に判別できるようにしている。**実装側の防御** だけでなく **運用側の検証** とセットで初めて成立する設計だ。

## 6. xlsx 生成の落とし穴

実装中に踏んだ罠を 4 つだけ紹介する。すべて GitHub Issues に記録してある。

### (a) ファイル名 259 文字超で Windows で開けない（Issue #14、解決済み）

Cowork サンドボックス配下に生成された xlsx はパスが長く、Windows の `MAX_PATH = 259` 制限に引っかかると Excel から開けない。`copy_to_desktop.py` という 2 KB の独立スクリプトを置き、`main.py` の直後に必ず呼ぶ運用にした。

```python
def copy_to_desktop(src_path: Path):
    home = Path.home()
    candidates = [
        home / "OneDrive" / "デスクトップ",
        home / "OneDrive" / "Desktop",
        home / "Desktop",
    ]
    for dest_dir in candidates:
        try:
            if dest_dir.exists() and dest_dir.is_dir():
                dest_path = dest_dir / src_path.name
                shutil.copy2(src_path, dest_path)
                return dest_path
        except (OSError, PermissionError):
            continue
    return None
```

3 候補を順に試すのは、日本語 Windows / 英語 Windows / OneDrive 同期の有無で実パスが変わるため。

### (b) 印刷範囲未設定で 29 ページ印刷（Issue #2、解決済み）

散布図用の隠しデータを R-W 列に置いていたため、`ws.print_area` を指定しないと印刷時に右側まで巻き込んで 29 ページになる。`ws.print_area = f"A1:N{r}"` を末尾で明示することで 4 ページに収まった。さらに後述の理由から、**関数冒頭にも `print_area = "A1:N200"` の暫定値を置いて二重化** している。

### (c) Cowork 配布層の truncate（〜17 KB）

Cowork はプラグインの Python ファイルを **約 17 KB で切る** 挙動がある。Apache ヘッダー 14 行を全 .py に追加したタイミングで `main_helpers.py` が 17 KB を超え、列幅・印刷範囲の指定が末尾で行われていたためファイル末尾と一緒に切られた。

対策は 2 つ並走している。

1. ファイル分割：`main_helpers.py` を `main_helpers_geo.py` と `main_helpers_koji.py` に分割し、本体は再エクスポート shim（1.4 KB）に圧縮。
2. 重要処理の二重化：列幅・`print_area` のような「切られると困る」設定を関数冒頭にも書く。

### (d) 顧客用シートへの専門用語混入

業者用には「β」「OLS」「R²」「ヘドニック」を平然と書く一方、顧客用には 1 文字も入ってはならない。目視レビューでは持たないので `forbidden_words.py` で機械的に弾く。

```python
FORBIDDEN_WORDS = [
    "AI", "A.I.", "モデル", "機械学習",
    "ヘドニック", "β", "ベータ",
    "回帰", "OLS", "統計",
    "予測", "推定", "アルゴリズム",
    "学習", "係数", "R²", "R2", "R^2",
    "p値", "p-value",
]

def assert_clean(text: str, context: str = ""):
    ok, detected = check_text(text)
    if not ok:
        raise ValueError(
            f"顧客用シートに禁止語が混入: {detected} "
            f"/ context={context} / text={text!r}"
        )
```

顧客用シート書き込み時に `assert_clean` を呼び、混入時は `ValueError` で実装ごと停止させる。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4436261/6a09bf15-5e39-44fb-b93f-ef51bfb441b6.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4436261/da7d4692-7b2f-4fca-931d-87af93cd8bb5.png)


## 7. ヘドニック回帰の実装

回帰本体は `statsmodels` の OLS をそのまま呼ぶだけで、特に工夫は無い。被説明変数は時点修正後単価の自然対数、特徴量は 12 個（面積、面積²、駅徒歩分、形状指数、道路幅員、容積率、方位スコア、私道ダミー、袋地ダミー、不整形ダミー、地区平均単価、駅勢圏平均単価）。

```python
import statsmodels.api as sm

MIN_SAMPLES_FOR_REGRESSION = 15

def fit_hedonic(df: pd.DataFrame) -> dict:
    n = len(df)
    if n < MIN_SAMPLES_FOR_REGRESSION:
        return {"ok": False, "n": n, "coefficients": {},
                "skip_reason": f"件数 {n} < {MIN_SAMPLES_FOR_REGRESSION}: 回帰スキップ"}
    y = df["unit_price"].apply(math.log)
    X = sm.add_constant(_build_features(df))
    try:
        model = sm.OLS(y, X).fit()
    except Exception as e:
        return {"ok": False, "n": n, "coefficients": {},
                "skip_reason": f"OLS失敗: {e}"}
    coef = {
        name: {
            "beta": float(model.params[name]),
            "se":   float(model.bse[name]),
            "p":    float(model.pvalues[name]),
            "label": FEATURE_LABELS.get(name, name),
        }
        for name in X.columns
    }
    return {"ok": True, "n": n,
            "r2": float(model.rsquared),
            "adj_r2": float(model.rsquared_adj),
            "coefficients": coef, "skip_reason": None}
```

実装上の判断ポイントが 2 つある。

**期待符号チェックの導入。** 信頼度ラベル（高 / 中 / 中-低 / 低）を機械的に決めるため、`ln_area` `walk_min` `D_shidou` `D_fukuro` `D_fuseikei` の 5 つは「負であるべき」とハードコードし、`p < 0.10` で有意に正側に反転したものが 2 件以上ある場合だけ「構造問題あり」と判定する。非有意な符号反転はノイズ範囲とみなしてカウントしない。これがないと小サンプル地区で信頼度が過剰に下振れする。

**方位の ordinal 化。** 「南向きダミー」だと「南」と「南西」の 1 ステップ差が表現できない。北 = 0 → 南 = 4 の 0〜4 スケール（北東 / 北西 = 1、東 / 西 = 2、南東 / 南西 = 3）にして β を 1 本に集約した。標準化補正で方位差分が綺麗に積算できる。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4436261/29eba15c-ac06-40b7-b411-b3f95d6f2306.png)

## 8. Apache 2.0 での OSS 公開

v1.4.0 でライセンスを MIT から **Apache License 2.0** に切り替えた。判断理由は 3 つある。

1. **特許保護条項。** Apache 2.0 には貢献者が暗黙に特許ライセンスを付与する条項がある。AVM 分野は将来的に手法特許のリスクがゼロでないため、ここを明示しておきたかった。
2. **派生物の表示義務。** `NOTICE` ファイルによる帰属表示を派生物が引き継ぐ義務がある。OEM 配布を想定したときに、ブランドは差し替え可能でもベース実装の出自は残るようにしたかった。
3. **企業導入の法務障壁低下。** 法務レビューで Apache 2.0 のほうが明示的で扱いやすいと判定されるケースが実務上多い。

切替に伴って全 .py に標準ヘッダー 14 行を追加し、`NOTICE` ファイルを新設した。前述の Cowork 配布層 truncate は、このヘッダー追加で踏んだ副作用でもある。

## 9. GitHub Issues 14 本の起票

v0.1 公開時点で 14 本の Issue を起票した（v1.4 系で解決済み 2 本、open 12 本）。「コミュニティで育てる OSS」のスタンスを取り、未解決の構造的論点もそのまま open で出している。

特に **査定ロジック自体への論点** は鑑定実務家・統計家のレビューを受けたいので `needs-appraiser-review` ラベルを付けた。例：

- `#4` ヘドニック係数の地域別安定性検証
- `#5` 比準格差の補正率上限・下限ロジックの妥当性議論
- `#6` サンプル数が少ない地域での係数推定の挙動

実装側の論点は `good-first-issue` / `intermediate` で粒度を分けてある。

- `#7` テストケースの整備（pytest 導入）
- `#8` README の英訳
- `#10` `xlsx_gyosha_sheet.py`（1,100 行）の分割
- `#11` 公示価格 L01 GeoJSON 自動 DL スクリプト
- `#12` macOS 版 Watcher（LaunchAgent）

`#13` には「[Roadmap] 国交省 API 版への移行検討（v2.0 想定）」を置いて、CSV → API への移行を将来課題として明示している。

## 10. まとめ

実装で意識したのは次の 3 点だ。

1. **白箱性の徹底。** 係数も補正率も採用事例もすべて xlsx に出す。隠す価値があるロジックは無い。
2. **LLM 経由配布の防御線。** 認証マーカー、ファイルサイズ、シート構成、固定セクション名の 4 条件で捏造出力を弾く。
3. **「切られる前提」の実装。** Cowork 配布層 truncate を踏まえてファイルを 17 KB 未満に分割し、重要処理は冒頭・末尾で二重化する。

査定ロジック自体は古典的で珍しさは無い。新規性があるとすれば、**「実装して、全部開示して、Apache 2.0 で GitHub に置く」**まで踏み切った点と、それを **Claude Skill として直接配布する** 構成にある。

査定ロジック・実装・運用、どの観点でも質問・指摘を歓迎する。コメント、GitHub Issue、Pull Request、どこからでも。特に `needs-appraiser-review` ラベルの議論には、鑑定実務家・統計家のレビューを切実に求めている。

### 関連リンク

- リポジトリ: [signal-yield/tochi-satei-kun](https://github.com/signal-yield/tochi-satei-kun)
- インストール手順: [INSTALL.md](https://github.com/signal-yield/tochi-satei-kun/blob/main/INSTALL.md)
- ライセンス: Apache License 2.0
- フィードバック・Issue: [GitHub Issues](https://github.com/signal-yield/tochi-satei-kun/issues)
