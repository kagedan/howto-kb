---
id: "2026-06-13-claude-fable-5-はどんなコーディング特性だったのかopus-48-と統計的に比較した記-01"
title: "Claude Fable 5 はどんなコーディング特性だったのか——Opus 4.8 と統計的に比較した記録（オトナの自由研究 #26）"
url: "https://zenn.dev/nnakapa/articles/lab-26-fable5-opus48-coding-traits"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "GPT", "Python", "zenn"]
date_published: "2026-06-13"
date_collected: "2026-06-14"
summary_by: "auto-rss"
query: ""
---

## 2つの発見

**Fable 5 → クラッシュや不正入力を先回りして塞ぐ、防御的・堅牢設計重視の実装が特徴**

**Opus 4.8 → 役割分割と読みやすさを優先する、構造・可読性重視の実装が特徴**

この 2つは別々の発見ではなく、1つの結果の表と裏です。守りを固める Fable 5 と、読みやすさにこだわる Opus 4.8——同じトレードオフを両面から見ています。

![ブラインド・ペア比較 40 判定の軸別勝敗を示す対向横棒グラフ。中央から左に Fable 5 の勝ち数、右に Opus 4.8 の勝ち数が伸びる。latent_risk は 31 対 9、concurrency_durability は 34 対 6、defensive_depth は 36 対 3 で Fable 5 が圧倒し、design_readability だけは 8 対 27 で Opus 4.8 が勝つ（引分けは design_readability 5 件・defensive_depth 1 件）。3 軸対 1 軸の対構造で、防御的堅牢性の Fable 5・構造可読性の Opus 4.8 という性格差が一目でわかる](https://static.zenn.studio/user-upload/deployed-images/8cb8182ea13c779a7e7b26ef.png?sha=88df9e0c1de677a287850062b3b47a0e55b70aff)

これは「Fable 5 のほうが優れていた」という記事ではありません。機能面——テストを通せるか——での差は 10回の試行では出ませんでした。統計的に差が出たのは、点数に出ない非機能の「**性格の違い**」でした。もう試すことは出来ませんが、グラフからも読み取れるように Fable 5 と Opus 4.8 の差が明確に出ています。

## はじめに

前回（[#24](https://zenn.dev/nnakapa/articles/lab-24-fable5-opus48-qcd)）は、既存の QCD タスクで Fable 5 と Opus 4.8 を 240 試行で比較し、「品質（Q）は両者の差がなく、Fable 5 は約 2倍のコストに見返りなし」という結論になりました。ただし既存タスクは Fable 5 が解くには比較的小ぶりなタスクで難易度も易しかったので、「品質（Q）が飽和していたため Fable 5 の品質上限までは未検証」という課題を残していました。

そこで、AIコーディングエージェントが実務でよく利用される代表的な 10 領域——実装・デバッグ・堅牢性・リファクタ・性能・並行処理・耐久性・互換・セキュリティ・自己検証——を 1つのタスクに詰め込んで、コスト 2倍の Fable 5 はどこかで価値を示せるのかを検証しました。果たして Fable 5 はその価値を示せるのでしょうか。それとも、何も示せないのでしょうか。

この比べ方は以前の記事を元にしています。Opus 4.7 と GPT-5.5 を比較した [#19](https://zenn.dev/nnakapa/articles/lab-19-opus47-gpt55-code-review) です。あのときも機能スコアは飽和して差がつかず、違いは「コードレビューの仕方」という非機能に差が出ました。今回もスコアだけ見れば差は出ません。そこで [#19](https://zenn.dev/nnakapa/articles/lab-19-opus47-gpt55-code-review) と同じ道筋——**点数の外側、ソースコードの中身そのものを突き合わせる**——を試みます。

## 検証環境

今回も [#17](https://zenn.dev/nnakapa/articles/lab-17-rpi5-ubuntu26) でセットアップした Raspberry Pi 5 の環境で検証しました。

| 項目 | 値 |
| --- | --- |
| ホスト | Raspberry Pi 5 （4GB） |
| OS | Ubuntu 26.04 LTS arm64 |
| 実行 CLI | Claude Code v2.1.174 |
| モデル | claude-fable-5[1m] / claude-opus-4-8[1m] |
| effort level | high / xhigh の 2×2 |
| 試行数 | N=10 × 4 タイプ = 40 試行 |
| 計測日 | 2026-06-12 |
| LLM採点 | Codex CLI + GPT-5.5（effort=high） |

Claude Code は [#24](https://zenn.dev/nnakapa/articles/lab-24-fable5-opus48-qcd) で使用していた v2.1.170 から新しくなっていたので、最新の v2.1.174 へ更新しています。

LLM採点に Codex CLI + GPT-5.5 を使ったのは、比較対象が両方 Claude だったからです。Claude 系を使うと自己選好の混入を否定できないため、別系統のモデルで構造的に排除しました。

## 検証用に実行したタスク

タスクは 1つ。「**ファイルベースのミニ KVS（ドキュメントストア）+ CLI**」を、Python標準ライブラリのみで一気に実装させています。仕様書には 10個のチェックポイント（CP）に対応する要求を明記してあり、「仕様を曖昧さなく書き切ったタスクを一発で実装する」という、Anthropic が Fable 5 の得意領域として挙げる課題を意図的に用意しています。Fable 5 が最も力を発揮できるはずの土俵で、それでも Opus 4.8 と差がつかなければ、「2倍コストに見返りなし」という [#24](https://zenn.dev/nnakapa/articles/lab-24-fable5-opus48-qcd) の結論はいっそう強くなる——そういう設計です。

| CP | 領域 | 要求の概要 |
| --- | --- | --- |
| #1 | impl（新規実装） | put / get / delete / list と JSON ファイル永続化 |
| #2 | debug（レガシー修正） | 同梱した「壊れたクエリフィルタモジュール」のバグ修正 |
| #3 | robustness（堅牢性） | 空キー・Unicode 正規化・巨大値・不正 JSON 読込への耐性 |
| #4 | refactor（保守性） | 挙動維持の関数分割（ radon / ruff の複雑度しきい値で機械判定） |
| #5 | perf（アルゴリズム） | プレフィックス検索インデックス。10 万件で時間上限内（素朴な線形走査では落ちる設定） |
| #6 | concurrency（並行） | 8 スレッド並行 put / get で lost update ゼロ |
| #7 | durability（永続・回復） | 原子的書き込み + ジャーナル。書き込み途中の例外注入 → 再オープンで整合回復 |
| #8 | compat（互換・移行） | データフォーマット v1→v2 マイグレーション、round-trip 保証 |
| #9 | security-hygiene（防御） | path traversal 防止、`eval`/`pickle` 不使用などの防御的実装 |
| #10 | verification（自己検証） | ランダム操作列 + 不変条件（例外注入を挟んでも list == 真値集合） |

注意点は CP #1 → #10 は**難易度の階段ではない**ことです。各 CP は別領域のスキルに対応する単なるタグであり、結果は「どのレベルで落ちたか」ではなく「どの領域で勝敗が分かれたか」を比較します。

採点は CP ごとの隠しテスト、計 47件で行いました。採点器そのものの信頼性は事前の受入検証で確認しています。さらに [#24](https://zenn.dev/nnakapa/articles/lab-24-fable5-opus48-qcd) の既知タスクを両モデルで 1 試行ずつ流し、既知の結果（ゲート通過・Q 96〜100）が再現することでハーネスを較正しています。

なお、Fable 5 には特定トピック（セキュリティ・生物・化学など）で Opus 4.8 が代わりに応答するフォールバック仕様があります（公式発表でセッションの 5% 未満）。これが起きると Fable 5 と Opus 4.8 の比較が成立しないため、全 40 試行の応答モデル ID を指定モデルと突合したところ、すべて一致——フォールバックは 0件でした。

## 結果のアウトライン

### 機能面の採点は完全飽和——点数では差が出ない

まず機能の採点結果です。40 試行の全てが CP（チェックポイント）もゲートも通過していて、点数での差はありませんでした。

![Raspberry Pi 5 上で lab-26 の本走 40 run を実行中のターミナルログ。set=a1_profile_pi5、4 アーム（claude-opus-4-8 と claude-fable-5 × high/xhigh）、温度ゲートとタイムアウトの設定行に続き、trial ごとの実行結果が流れている。どの行も pass=true、cp=10/10（score=100.0）、gate=✓ で、wall 秒数だけが run ごとに異なる。機能採点が全 run で満点に飽和している様子がログからそのまま読み取れる](https://static.zenn.studio/user-upload/deployed-images/ed2c221897e70cc65f172b79.png?sha=406666c0061c9d59f4ab846b1d1dbfdf0c8c29d7)

| パターン | CP 通過 | ゲート通過 | 実行時間 | コスト |
| --- | --- | --- | --- | --- |
| Fable 5 / high | 10/10 × 10 run | 10/10 | 412 秒 | $3.03 |
| Fable 5 / xhigh | 10/10 × 10 run | 10/10 | 799 秒 | $5.62 |
| Opus 4.8 / high | 10/10 × 10 run | 10/10 | 365 秒 | $1.49 |
| Opus 4.8 / xhigh | 10/10 × 10 run | 10/10 | 625 秒 | $2.29 |

> 実行時間とコストは中央値、コストは CLI 報告値ベースの換算値です。

測定前に決めておいた 5 通りの比べ方（同 effort 同士・同コスト帯同士・effort 内比較）のどれで見ても、両モデルの CP 通過数の差はゼロ。Fisher 検定でも p=1.0 で、機能面の差は統計的にまったく検出されませんでした。[#24](https://zenn.dev/nnakapa/articles/lab-24-fable5-opus48-qcd) で見られた「品質（Q）が天井に張り付いて差が出ない」状態は、今回のように検証する領域を 10個に広げても同じように起きました。コスト中央値は high で約 2.0倍、xhigh で約 2.5倍。**機能面だけ見れば、2倍コストの見返りは今回もありません。**

### ブラインド比較——15勝1敗、4引き分け（p=0.001）

点数で差が出ないなら、ソースコードの内容を直接見て比べることにしました。そこで、同 effort・同 trial の成果物をペアにして、GPT-5.5 をジャッジとして**ブラインドでどちらが優勢かを選ぶ選択式**で比較しました。

採点（0〜100 点）ではなく、どちらが優勢かを選ぶ選択式にしたのには理由があります。[#19](https://zenn.dev/nnakapa/articles/lab-19-opus47-gpt55-code-review) で、ジャッジの人格が絶対値の点数に影響する——同一の成果物に 0 点と 85 点が付くような割れ方をする——問題を把握していました。選択式なら「どちらが良いか」だけを答えさせるので、ジャッジの癖を構造的に消すことができます。

判定の基準は次のとおりです。

* 評価の軸は 4つ: latent\_risk（潜在リスク）/ concurrency\_durability（並行・耐久）/ design\_readability（設計・可読性）/ defensive\_depth（防御の深さ）。各軸は引き分けも認め、総合判定だけはどちらか一方を必ず選ばせました
* ジャッジは先に見せた側を高く評価しがちなので、各ペアは A と B を入れ替えて 2回判定しました（2 effort × 10 trial × 2 通りの提示順 = 全 40 判定）
* 統計の単位は個々の「判定」ではなく「ペア」です。入れ替えた 2回は同じペアを見直しただけで独立した観測ではないため、検定（符号検定）は、提示順を変えても勝者が動かなかった＝結論が安定したペア（decisive ペア）だけで行いました

総合判定の結果がこちらです。

| effort | Fable 5 勝ち | Opus 4.8 勝ち | 引分け | 符号検定（decisive のみ） |
| --- | --- | --- | --- | --- |
| high | 8 | 0 | 2 | n=8、p=0.008 |
| xhigh | 7 | 1 | 2 | n=8、p=0.070 |
| **計** | **15** | **1** | 4 | **n=16、p=0.001** |

> 勝敗はペア単位（2 effort × 10 trial = 20 ペア）の集計です。検定は decisive なペアのみで n=16。提示順を入れ替えた判定単位の参考値は後述の details を参照してください。

合計で 15勝1敗、符号検定でも p=0.001。機能テスト（CP）の点数では「差なし」だったのに、ジャッジにソースコードの中身を直接比べさせると、勝敗ははっきり Fable 5 側に倒れました。**全項目クリア（CP 飽和）＝中身も互角、ではなかった**のです。

検定の詳細と位置バイアスの観察

* 符号検定は、提示順を入れ替えても勝者が変わらなかったペア（decisive ペア）だけを対象にした二項検定（両側）です。high は n=8 で p=0.008、xhigh は n=8 で p=0.070、合算 n=16 で p=0.001。xhigh だけだと 5% 水準（p<0.05）には届きませんが、勝敗の向きは high と同じ（Fable 5 寄り）です
* 参考までに、ペア単位ではなく判定 1件ずつで数えると high 18-2 / xhigh 16-4 でした。ただし入れ替えた 2 判定は独立していないので、検定には使わず参考値（記述統計）に留めています
* 先に見せた側が有利になる「位置バイアス」は実際にありました。2回の判定で勝者が割れて引き分けになった 4 ペアは、全体として先に提示した側へ流れる傾向があり（20 ペア中、両方の提示順で勝者が一致したのは 16 ペア）、A と B を入れ替える設計は欠かせませんでした。もし入れ替えず 1回だけの判定で集計していたら、先に見せた側の勝ち数が実際より水増しされていたはずです

では、ジャッジは何を見て Fable 5 を選んだのでしょうか。4つの評価軸ごとに勝敗を集計すると、**両モデルの性格がくっきり分かれます。**

| 軸 | Fable 5 | Opus 4.8 | tie |
| --- | --- | --- | --- |
| latent\_risk（潜在リスク） | **31** | 9 | 0 |
| concurrency\_durability（並行・耐久） | **34** | 6 | 0 |
| design\_readability（設計・可読性） | 8 | **27** | 5 |
| defensive\_depth（防御の深さ） | **36** | 3 | 1 |

> 合算 40 判定（判定単位）の集計です。総合判定のペア単位 n=16 とはカウントの単位が違う点に注意してください（こちらは提示順を入れ替えた 2回ぶんを別々に数えています）。

冒頭に出した「2つの発見」の根拠が、この軸別の集計です。グラフにすると分かりやすいので、冒頭のグラフを再掲します。

![ブラインド比較 40 判定の軸別勝敗を示す対向横棒グラフ（冒頭の再掲）。中央から左へ Fable 5 の勝ち数、右へ Opus 4.8 の勝ち数が伸びる。latent_risk は 31 対 9、concurrency_durability は 34 対 6、defensive_depth は 36 対 3 で Fable 5 が大きく上回り、design_readability だけ 8 対 27 で Opus 4.8 が上回る（引き分けは design_readability 5 件・defensive_depth 1 件）。3 軸対 1 軸の対構造で、防御的堅牢性に寄る Fable 5 と構造・可読性に寄る Opus 4.8 の性格差が一目でわかる](https://static.zenn.studio/user-upload/deployed-images/8cb8182ea13c779a7e7b26ef.png?sha=88df9e0c1de677a287850062b3b47a0e55b70aff)

3 軸で Fable 5、1 軸で Opus 4.8。結果がきれいに分かれます。とくに defensive\_depth（防御の深さ）は 36 対 3、concurrency\_durability（並行・耐久）は 34 対 6 と、「落ちたときに困る」領域では Fable 5 が一方的に選ばれています。それに対して Opus 4.8 が勝った唯一の軸が design\_readability（設計・可読性）の 27 対 8 です。冒頭の「防御的堅牢性の Fable 5／構造・可読性の Opus 4.8」は、この 1 枚に凝縮されています。次からは、ジャッジが各軸で何を見ていたのかを、コメントの原文で確かめていきます。

## 発見——Fable 5 は「防御的・堅牢設計を重視」

defensive\_depth（防御の深さ） は 36 対 3、concurrency\_durability（並行・耐久） は 34 対 6。ジャッジが Fable 5 を選んだ理由を読むと、毎回ほぼ同じ論点に行き着きます。閉じたあとのストアを誤って操作していないかのチェック、メタ情報ファイルを途中で壊さない原子的な書き込み、ジャーナル（変更履歴）レコードの厳格な検証、書き込みに失敗したときの巻き戻し（ロールバック）——どれも「**本来なら起きないはずの失敗**」**への備え**です。

defensive\_depth（防御の深さ） の判定理由です。

> A validates open state on every public operation, validates decoded journal records more strictly, and uses atomic temp+replace for meta writes. B defensively deep-copies values, but it accepts malformed journal records more readily and operations after close can fail with less disciplined AttributeError-style behavior through \_fp.

該当ソースコード（`kvstore.py` 抜粋・Fable 5 / high / trial1）

公開操作のたびにオープン状態を確認（`_check_open`）してから処理に入る:

```
def _check_open(self):
    if self._file is None:
        raise StoreError("store is closed")

def put(self, key: str, value: dict) -> None:
    key = _normalize_key(key)
    if not isinstance(value, dict):
        raise TypeError(f"value must be a dict, got {type(value).__name__}")
    with self._lock:
        self._check_open()
        self._append_record({"op": "put", "key": key, "value": value})
        if key not in self._data:
            bisect.insort(self._keys, key)
        self._data[key] = value
```

ジャーナル 1 行を厳格に検証し、壊れた行は `None` で弾く:

```
def _decode_record(line):
    """ジャーナル 1 行を解析。不正な行は None を返す。"""
    try:
        record = json.loads(line)
    except ValueError:
        return None
    if not isinstance(record, dict) or not isinstance(record.get("key"), str):
        return None
    op = record.get("op")
    if op == "put" and isinstance(record.get("value"), dict):
        return record
    if op == "del":
        return record
    return None
```

メタ情報は一時ファイルに書いてから `os.replace` で原子的に差し替える:

```
def _write_meta(self, version):
    meta_path = os.path.join(self._path, _META_NAME)
    tmp_path = meta_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump({"format_version": version}, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, meta_path)
```

A（Fable 5）は、外部から呼べる操作のたびにストアが開いているかを確認し、ジャーナル（変更履歴）の中身もより厳しくチェックし、メタ情報の書き込みには「一時ファイルに書いてから置き換える」壊れにくい手順を使っています。一方 B（Opus 4.8）は、値を防御的にコピーするものの、壊れたジャーナルをそのまま受け入れてしまいやすく、閉じたあとに操作すると `AttributeError`（閉じたファイルに触れて出る内部エラー）任せで落ちます——という対比です。どちらも仕様の要求（CP7・CP9）は満たしています。差がついたのは、**仕様に書かれていない失敗のしかたを、どこまで先回りして塞いだか**でした。

### 例 2: partial-write ロールバック（`high / trial8 / order fo`、A = Fable 5）

concurrency\_durability（並行・耐久） の判定理由です。

> A uses a single RLock around read-modify-write paths and low-level os.write with a tracked \_good\_size plus truncation on append failure, giving clearer recovery from partial appends. B locks public operations but uses buffered file writes without partial-write rollback, and update lets user code mutate the live stored object before the append succeeds.

該当ソースコード（`kvstore.py` 抜粋・Fable 5 / high / trial8）

`os.write` で追記し、成功したぶんだけ `_good_size` を進める。例外時は `_good_size` まで `os.ftruncate` で切り詰めて巻き戻す:

```
def _append_record(self, record: dict) -> None:
    payload = (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
    try:
        view = memoryview(payload)
        while view:
            view = view[os.write(self._fd, view):]
        if self._sync:
            os.fsync(self._fd)
    except Exception:
        self._discard_partial_write()
        raise
    self._good_size += len(payload)

def _discard_partial_write(self) -> None:
    try:
        os.ftruncate(self._fd, self._good_size)
    except OSError:
        pass
```

A（Fable 5）は、OS の低レベルな書き込み（`os.write`）を使って「どこまで正しく書けたか」を記録し、追記に失敗したら書きかけの部分を切り捨てて元の状態に巻き戻します。一方 B（Opus 4.8）は、いったんバッファ（書き込みを溜める領域）を経由する書き込みで、途中まで書けて失敗したときに元へ戻す仕組みを持ちません——という対比です。

この傾向は high・xhigh どちらの effort level でも同じ形で現れました。だとすれば、これは effort level の設定による癖ではなく、今回の条件で安定して現れた実装傾向と見るのが自然です。

## 発見——Opus 4.8 は「構造・可読性を重視」

4 軸のうち Opus 4.8 が唯一勝ち越したのが design\_readability で、27 対 8（引き分け 5）でした。ジャッジのコメントは、データの流れの追いやすさ・処理の役割分担の明確さ・状態管理のシンプルさを、一貫して評価しています。

### 例: 監査しやすいデータフロー（`high / trial5 / order of`、A = Opus 4.8）

design\_readability の判定理由です。

> A's data flow is easier to audit: writes mark a sorted index dirty and \_ensure\_sorted rebuilds from \_data, avoiding the multi-state pending\_adds/pending\_dels machinery in B. B's extra incremental index logic adds maintenance surface without much clarity benefit.

該当ソースコード（`kvstore.py` 抜粋・Opus 4.8 / high / trial5）

書き込み時はソート済み索引に「dirty（要再構築）」の印を立てるだけ。`_ensure_sorted` が必要になった時点で `_data` から作り直す:

```
def _ensure_sorted(self) -> None:
    if self._sorted_dirty:
        self._sorted = sorted(self._data)
        self._sorted_dirty = False

def put(self, key: str, value: dict) -> None:
    key = _normalize_key(key)
    _validate_value(value)
    with self._lock:
        is_new = key not in self._data
        self._append({"op": "put", "key": key, "value": value})
        self._data[key] = copy.deepcopy(value)
        if is_new:
            self._sorted_dirty = True
```

A（Opus 4.8）は「書き込みのときはインデックス（検索用の索引）に『あとで作り直す』印を付けておき、必要になった時点でまとめて作り直す」という単純な作りで、コードを追って確かめやすい。一方 B（Fable 5）は、書き込みのたびに索引を少しずつ更新する作りで、分かりやすさの見返りに乏しいわりに、直したり読んだりする手間（保守の負担）を増やしている——という指摘です。Fable 5 の作り込みが、この軸ではかえって減点につながっています。

それでも、このペアの総合（overall）判定は Fable 5 でした。ジャッジは同じ判定の中でこう書いています。

> B carries more index complexity, but its stronger append/error-recovery discipline, closed-handle checks, and journal validation are more important for this file-backed store than A's simpler readability.

「ファイルにデータを保存するストアでは、追記とエラー回復をきちんとやることのほうが、シンプルな読みやすさより大事だ」——という判断です。つまり総合での 15勝1敗は、latent\_risk（潜在リスク）と concurrency\_durability（並行・耐久）を重く見る、**今回の採点基準（ルーブリック）の重み付けが生んだ結果**です。もし可読性・保守性を最重要に置く採点基準なら、総合は逆転し得ます。だから「Fable 5 が優れている」ではなく、「この重み付けでは Fable 5 が選ばれる」と読んでください。

## 考察

### 効く範囲——耐久性・並行処理・防御的実装が必要な領域

今回の条件では、Fable 5 の約 2倍のコストが買っているのは**防御的な堅牢性**だと言えます。クラッシュからの整合回復・ジャーナル・並行アクセスのような「落ちたときに困る」コードを書かせる領域で、ジャッジ判定は defensive\_depth が 36 対 3、concurrency\_durability が 34 対 6 と、一方的に Fable 5 へ傾きました。high 同士のコスト中央値で見ると、1 run あたり約 $1.5 の上乗せ（$3.03 対 $1.49、いずれも換算値）で、この性格を買っている計算になります。

逆に、保守チームに引き継ぐコード——半年後に別の人が読んで直すコード——を重く見るなら Opus 4.8 です（design\_readability 27 対 8）。テストを通す力は今回 40/40 で互角なので、**選び分けの基準は「何を最適化したいか」だけ**に絞れます。これは仮説ですが、N=5 の途中集計から N=10 に増やしても構図が変わらなかった程度には安定した傾向です。

### 効かない範囲——この結果からは言えないこと

この結果には、はっきりした限界があります。

* **機能面の差までは分からない**: 統計的に確定したのは、点数に出ない非機能の性格差だけです。機能採点は 40/40 で満点に飽和しているので、機能については「N=10 では差を検出できなかった」までしか言えません。Fable 5 が機能面で細かい取りこぼしをしない、という意味ではありません。
* **タスクは 1 本だけ**: Python 標準ライブラリだけで作る単一ツールを、Claude Code 上で比べた結果です。別の言語・別のドメイン・長時間タスクにそのまま当てはまるとは主張しません。
* **ジャッジは GPT-5.5 の 1 種類だけ**: ここでの「中立」は、Claude 同士の自己びいきを避けたという意味です。GPT-5.5 自身に系統的な好き嫌いがない保証まではありません。Opus 系のジャッジに同じペアを判定させて一致率を測る裏取りは、まだ宿題として残っています。
* **総合（overall）の勝敗は採点基準しだい**: 15勝1敗は、潜在リスクと耐久性を重く見る重み付けで出た結果です。可読性を重く見る基準なら、逆転し得ます。

### 前回（[#24](https://zenn.dev/nnakapa/articles/lab-24-fable5-opus48-qcd)）の結論はこう更新される

[#24](https://zenn.dev/nnakapa/articles/lab-24-fable5-opus48-qcd) の「品質が飽和していて、2倍コストの見返りはない」という結論は、あくまで機能面（テストを通せるか）の話でした。今回の結果を加味すると、このように更新されます。

**2倍コストの見返りは、点数に出ない防御的堅牢性という形で、たしかに存在した。ただし可読性を少し犠牲にする、というトレードオフ付きで。**

もし採点結果の点数だけを見ていたら、この差はずっと「差なし」のままだったはずです。

## まとめ

AIコーディングエージェントが活用できる 10 の領域を 1つに詰め込んだタスクを 40 試行走らせて、Fable 5 と Opus 4.8 を比べた結果です。

* 機能テストは 40/40 で全部満点。テストを通す力は N=10 では差が出ず、違いはコストが約 2.0〜2.5倍高いことだけ
* ソースコードを直接見比べると、Fable 5 の 15勝1敗（p=0.001）。全項目クリアでも、中身は互角ではなかった
* 差の正体は、きれいに対になった性格の違い。守りに強い Fable 5、読みやすさに強い Opus 4.8

もし Fable 5 が引き続き利用できたとすると、実運用での選び分けの仮説はこうです。クラッシュからの復帰・並行処理・ジャーナルのような「落ちたら困る」コードは Fable 5 向き、保守チームに引き継ぐ「読まれる」コードは Opus 4.8 向き。ただし、どちらもテストは同じだけ通る、という前提付きです。

「2倍のコストに見返りはあるのか」という問いの出発点だった前回の QCD 比較も、同じ Fable 5 と Opus 4.8 を測った——いまや過去になった——記録です。

*本記事は、筆者個人の Raspberry Pi 5 / Ubuntu 26.04 環境における非公式な実験記録です。Claude Code 上で実行した Claude Fable 5 / Opus 4.8、およびジャッジに用いた Codex CLI + GPT-5.5 の一般的な性能優劣を示すものではありません。結果はタスク内容、プロンプト、CLI バージョン、effort level、ネットワーク状況、実行順によって変化します。各名称は各社・各団体の商標または登録商標です。*

---

*この記事は「オトナの自由研究」シリーズの第26回です。消費財メーカーでデジタル戦略を推進する筆者が、最新テクノロジーを自分の手で試し、何ができるのか・どんな価値を生むのかを検証する過程を記録しています。*  
*※本連載は個人の実験と学びの共有であり、所属組織の公式見解ではありません。*
