---
id: "2026-06-06-github-copilot-の従量課金を実測したclaude-codecodex-と同一モデルで比-01"
title: "GitHub Copilot の「従量課金」を実測した——Claude Code・Codex と同一モデルで比較（オトナの自由研究 #22）"
url: "https://zenn.dev/nnakapa/articles/lab-22-github-copilot-ai-credits"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "GPT", "Python"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

**「Opus 4.8」を GitHub Copilot で使うと、Claude Code の「1.5倍〜2.0倍」コスト高となる**

**「GPT-5.5」は GitHub Copilot と Codex で、かかるコストと処理時間は「ほぼ互角」**

今回の比較は、RDB（PostgreSQL + psycopg2）のエッジケース 3 タスクを、Raspberry Pi 5 上で各パターン 10 試行ずつ回した実測結果です。

Copilot Pro+ の月額だけを見て「安い」と判断している人ほど、重い反復検証では AI credits の消費速度まで含めて見る必要があります。

![Opus 4.8 のコスト（C：実課金額）×処理時間（D：実行時間）散布図——Claude Code（native）と GitHub Copilot を low→x-high の 4 effort でプロット。両者とも R²≒1 の直線に乗り、傾き（秒単価）はほぼ同じ一方、Copilot は切片（固定費）の分だけ上にシフトしている](https://static.zenn.studio/user-upload/deployed-images/35c8f49f88680774e730b6f4.png?sha=dbfa0c6efb6c92f572f9a397611cc3e576802353)

GitHub Copilot が従量課金に移行される以前に行ったコスト比較（[#16](https://zenn.dev/nnakapa/articles/lab-16-rpi4-qcd)）では、「**迷ったら Claude Code、コスト優先なら Copilot CLI**」と結論づけていました。同じタスクを実行させても、Claude Code や Codex CLI と比べて**6〜8分の1程度のコスト**でした。

しかし、2026年6月1日から適用された**従量課金制**では、状況が逆転してしまいました。結果は後半パートで詳しく解説しますが、特に Opus 4.8 を使う際、GitHub Copilot は Claude Code の「1.5倍〜2.0倍」コスト高となる結果となりました。

2026年6月現在、Opus 4.8 や GPT-5.5 を使うなら、あくまでも今回のタスクに限っての話ですが、モデルの開発元が提供する Claude Code や Codex を利用するのがコスト面では有利という結果になりました。

## 実測に使用したタスク

今回使用したタスクは、RDB（PostgreSQL + psycopg2）のエッジケースを題材に、比較的小さな Python モジュールを 3 つ用意しました。どれも対象の関数がスケルトンになっていて、エージェントは仕様（プロンプト）を読んで関数の中身を実装するというタスクです。

**タスク1：送金手続き「中途半端に処理しない」**

> A さんから B さんへお金を移すには「A から引く」「B に足す」の2つの作業が要ります。怖いのは片方だけ終わって止まること — A から引いたのに B に届かず、お金が消える事態です。そこで2つをワンセットにし、途中で失敗したら**なかったことにして元に戻す**(両方やるか、両方やめるか)を守らせます。ATM やレジがエラー時に残高をおかしくしないための基本作法です。

**タスク2：「悪意ある入力でデータを盗まれない」検索**

> 名前でユーザを探す検索窓のような機能。怖いのは、検索キーワードに**悪意ある文字列を紛れ込ませてデータベースを乗っ取る**攻撃(SQL インジェクション)です。たとえば並べ替えの指定欄に「全テーブル削除」の命令を書かれても無視できるか、特殊な記号をただの文字として扱えるか、想定外の入力で全件が漏れないか — 入力をそのまま信じず、安全に処理できるかを問います。仕様にはあえて「インジェクション対策をせよ」と書かず、気づいて守れるかを見ます。

**タスク3：「同時に買われても在庫を間違えない」予約**

> 残り1個の商品を2人がほぼ同時に「買う」と押す場面。素朴に作ると両方に「買えました」と返して**在庫がマイナス**(売り越し)になります。「楽観ロック」は、買う直前に在庫の状態が変わっていないかを確認してから減らすやり方。先に誰かが買っていたら後の人には正しく「売り切れ」と返す — 在庫を1個も多く売らない・マイナスにしないための仕組みです。

タスクの詳細はこちら

3 つとも「エージェントに渡したプロンプトと、配布した基本テスト（`test_basic.py`）だけを通せば OK に見える」よう設計してあります。基本テストは正当な入力のハッピーパスだけを確認するもので、仕込んだ罠は隠しテスト（配布しない）と `pass_gate` で初めて表面化します。罠はいずれも「並行処理」ではなく、**失敗経路の後始末・パラメータ化・影響行数の解釈**という、単一スレッドでも踏む地雷です。

「スケルトン」とは、関数の「殻」だけを用意した状態です。関数名・引数・戻り値の型・docstring（その関数が何をするかの説明）はそろっていますが、肝心の中身は `raise NotImplementedError` の 1 行だけ。たとえば T1（送金）の出発点は、こうなっています。

```
def transfer(conn, src_id: int, dst_id: int, amount: int) -> None:
    """src_id から dst_id へ amount を移動する。"""
    raise NotImplementedError  # ← エージェントがここを実装する
```

`raise NotImplementedError` は Python で「この関数はまだ中身が無い」ことを示す定番の書き方で、そのまま呼ぶと必ずエラーで止まります。いわば穴埋め問題の「解答欄を空けた状態」で、**全タスク・全モデルが完全に同じこの出発点**から始めます。エージェントの仕事は、仕様（プロンプト）を読んでこの `raise NotImplementedError` を本物の実装に置き換えることです。出発点をそろえてあるので、出来上がりの差はそのままモデルと effort の差として読めます。

| ID | テーマ | エージェントに見せた仕様 | 仕込んだ罠（隠しテスト・`pass_gate`） |
| --- | --- | --- | --- |
| **T1** | アトミックな送金（`transfer` / `get_balance`） | `src` から `dst` へ `amount` を移動。額が 0 以下なら `ValueError`、残高不足なら `InsufficientFunds`、口座が無ければ `LookupError`。減算と加算は一体で成功／失敗させる | **失敗経路のロールバック漏れ・トランザクション放置**：送金先が不在のとき送金元だけ減らして commit しないか／残高不足・不在で例外を投げた後も接続が `aborted` にならず再利用できるか／後段（加算が int4 オーバーフロー）で失敗したとき先の減算を残さないか。さらに gate 外で、読み取りだけの `get_balance` まで含め idle-in-transaction を残さないか（Reliability 軸の連続点に反映） |
| **T2** | パラメータ化検索（`search_users`） | `name_contains` は部分一致（大小無視）、`ids` はその ID 群のみ（空リストは空結果）、`sort_by`／`order` で並べ替え。`dict` のリストを返す | **パラメータ化の穴**（プロンプトには「injection」「parameterized」を **書かない**）：LIKE のメタ文字 `%`／`_` を **リテラル** として扱えるか（エスケープ）／`ids=[]` で `IN ()` の構文エラーを出さないか／`sort_by`・`order` を **許可リストで弾く** か（`sort_by="name; DROP TABLE users; --"` などの識別子インジェクション）／`ids` 経由のインジェクション（`"1) OR TRUE --"`）で全件漏れないか |
| **T3** | 楽観ロック在庫引当（`reserve` / `release`） | `version` の compare-and-set で在庫を減算し version を +1。version 不一致・在庫不足・SKU 不在なら **何も変えず `False`**、成功なら `True`。`qty` が 0 以下なら `ValueError` | **影響行数を見ないガード無し UPDATE**（プロンプトは `rowcount` に触れない）：version 不一致を上書きして lost update にしないか／在庫不足を見逃して売り越し・負在庫（CHECK 違反で接続 abort）にしないか／不在 SKU で `True` を返さないか。gate 外で、対象外の行を巻き込まない（WHERE 漏れ）か・`qty == stock` の境界（`>=`）を満たすか |

T2 では **意図的に脆弱な参考実装**（`reference/naive_failing.py`）を別途用意しています。これは「プレースホルダさえ使えば安全」という理解のまま値以外を f-string で組み立てた典型実装で、正当入力の公開テストは通る一方、**隠しテスト（LIKE エスケープ・空 IN・識別子インジェクション）で確実に落ち、`pass_gate` を通らない** ことを事前に確認しています。脆弱なコードを取り逃がすテストでは、エージェントが合格になっても何の保証にもならないためです。

品質の採点方法については、[#16](https://zenn.dev/nnakapa/articles/lab-16-rpi4-qcd)の記事に詳細がありますので、こちらを参考にしてください。

なお本記事は SQL インジェクション対策そのものの解説は範囲外です。対処は parameterized query を使い、並べ替え列などの識別子は許可リストで検証し、LIKE のメタ文字（`%`／`_`）はアプリ層でエスケープしてパラメータバインドと併用するのが基本です。

## 計測に使用した環境と試行内容

今回の実測で使用した環境はこちらです。[#17](https://zenn.dev/nnakapa/articles/lab-17-rpi5-ubuntu26)でセットアップした Raspberry Pi 5 の環境で検証を行いました。

| 項目 | 値 |
| --- | --- |
| ホスト | Raspberry Pi 5（4GB） |
| OS | Ubuntu 26.04 LTS arm64 |
| 採点ツール | `uv tool` で pytest / bandit / ruff を導入（PEP 668 回避） |
| コスト計測 | 各 CLI が報告する実課金額をそのまま採用（Copilot は `totalNanoAiu`、Claude Code / Codex はセッションの reported usage） |

計測は同一モデルを、ベンダーが提供する CLI と GitHub Copilot CLI の両方で回し、CLI の違いがコスト・時間・品質にどう効くかを検証します。対象モデルは **Opus 4.8** と **GPT-5.5** の 2 つで、それぞれを 4 つの reasoning effort（low / medium / high / xhigh）で計測しています。

| モデル | ベンダー提供CLI | Copilot CLI | reasoning effort |
| --- | --- | --- | --- |
| Opus 4.8 | Claude Code 2.1.159 | GitHub Copilot CLI 1.0.59 | low / medium / high / xhigh |
| GPT-5.5 | Codex CLI 0.135.0 | GitHub Copilot CLI 1.0.59 | low / medium / high / xhigh |

タスクは前述した **3 つ（T1 / T2 / T3）** で、各パターン（モデル × CLI × effort）で 10 回ずつ試行しています。GitHub Copilot は 2 モデル × 4 effort × 3 タスク × 10 試行 = **合計 240 試行**を今回新規に計測しました。Claude Code と Codex CLI の結果については [#21](https://zenn.dev/nnakapa/articles/lab-21-opus48-gpt55-reasoning-effort) で計測した **N=30** の値を流用しています。

![Raspberry Pi 5 上で GitHub Copilot CLI を 240 試行（2 モデル × 4 effort × 3 タスク × 10 trial）完走した run.log の summary——overall pass=234 / logic_failure=6、task × agent ごとの pass 率と wall_med/min/max を一覧。本記事のコスト・時間比較の元データ](https://static.zenn.studio/user-upload/deployed-images/6fd5540fa5aefa441cc2ae86.png?sha=a6e874499cc834ed575587630a9e38c85f685cf0)

## 結果のアウトライン

上記の 240 試行と、[前回](https://zenn.dev/nnakapa/articles/lab-21-opus48-gpt55-reasoning-effort)の 720 試行について、Opus 4.8 と GPT-5.5 のそれぞれで **QCD**（Q：品質、C：コスト、D：処理速度） を比較しました。

### Opus 4.8の結果：Claude Code vs GitHub Copilot

コスト（C）と処理速度（D）は全 effort で Claude Code（native）が軽い一方、品質（Q）は low で GitHub Copilot が上回りました。ただし、実運用候補を Q(T2) が安定する medium 以上に絞ると、Claude Code の方が総合的に優位です。

この表では、品質（Q）が安定する effort で、C 倍率と D 倍率がどれだけ開くかを見ます。

| effort | Q(T2) native | Q(T2) Copilot | C native | C Copilot | C 倍率 | D native(s) | D Copilot(s) | D 倍率 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| low | ❌ 6/30 | ✔ 10/10 | $0.44 | $0.91 | 2.08x | 74 | 128 | 1.73x |
| medium | ✔ 30/30 | ✔ 10/10 | $0.48 | $1.00 | 2.06x | 88 | 134 | 1.52x |
| high | ✔ 30/30 | ✔ 10/10 | $0.55 | $1.00 | 1.83x | 104 | 130 | 1.25x |
| xhigh | ✔ 30/30 | ✔ 10/10 | $1.08 | $1.63 | 1.51x | 271 | 340 | 1.26x |

> ✔ = 100 %:全試行通過 / ⚠️ = 50–99 %:動くが不安定 / ❌ = 0–49 %:実運用が難しい

### GPT-5.5の結果：Codex CLI vs GitHub Copilot

GPT-5.5 は、Opus 4.8 と違った傾向でした。low では GitHub Copilot の方がコスト（C）と処理速度（D）は軽いものの、品質（Q）は 6/10 と不安定です。medium 以上では Codex CLI が品質を安定させつつ、C/D も大きく離れないため、総合的には Codex CLI が扱いやすい結果でした。

しかし、全ての effort でコスト（C）も処理速度（D）も、0.78倍〜1.29倍であり、実運用的には「**ほぼ互角**」と言えます。

この表では、Q(T2) の安定度を確認したうえで、C 倍率と D 倍率が実運用上の差と言えるほど開いているかを見ます。

| effort | Q(T2) native | Q(T2) Copilot | C native | C Copilot | C 倍率 | D native(s) | D Copilot(s) | D 倍率 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| low | ⚠️ 28/30 | ⚠️ 6/10 | $0.61 | $0.48 | 0.78x | 118 | 113 | 0.96x |
| medium | ✔ 30/30 | ⚠️ 8/10 | $0.48 | $0.55 | 1.13x | 129 | 149 | 1.16x |
| high | ✔ 30/30 | ✔ 10/10 | $0.56 | $0.69 | 1.22x | 154 | 199 | 1.29x |
| xhigh | ✔ 30/30 | ✔ 10/10 | $0.74 | $0.76 | 1.02x | 227 | 271 | 1.19x |

> ✔ = 100 %:全試行通過 / ⚠️ = 50–99 %:動くが不安定 / ❌ = 0–49 %:実運用が難しい

## 発見——Opus 4.8 は Copilot の固定費がコスト差を広げる

前述の表「Opus 4.8 — Claude Code (native) vs GitHub Copilot」から、コスト（C）と処理速度（D）をプロットしたグラフです。（冒頭のグラフの再掲）

![Opus 4.8 のコスト×処理時間散布図（冒頭の再掲）——Claude Code（橙）と GitHub Copilot（青）の effort 4 点に最小二乗回帰の破線を重ねたもの。2 本の破線はほぼ平行で、Copilot 側が一定額だけ上に乗る](https://static.zenn.studio/user-upload/deployed-images/35c8f49f88680774e730b6f4.png?sha=dbfa0c6efb6c92f572f9a397611cc3e576802353)

回帰分析を用いて Claude Code と GitHub Copilot の結果を確認すると、今回の 4 effort 点では、どちらもコスト（C）と処理速度（D）がほぼ直線に乗っていることが分かります。

| CLI | 回帰式 (C = a·D + b) | 傾き a ($/1000s) | 切片 b ($) | R² | n |
| --- | --- | --- | --- | --- | --- |
| Claude Code (native) | C = 0.00325·D + 0.201 | 3.25 | 0.201 | 1.000 | 4 |
| GitHub Copilot | C = 0.00317·D + 0.552 | 3.17 | 0.552 | 0.989 | 4 |

これらの結果から、Opus 4.8 を使う際には Claude Code の方がコスト（C）と処理速度（D）の面で、GitHub Copilot よりも明らかに優位であると言えます。

## 発見——GPT-5.5 は固定費の差が小さく、Copilot と Codex が近い

GPT-5.5 も同様に回帰分析を行い評価しました。Codex CLI は[#21](https://zenn.dev/nnakapa/articles/lab-21-opus48-gpt55-reasoning-effort)で発見した low がキャッシュヒット率の影響により外れ値のため除外し（n=3）、GitHub Copilot は low も直線に乗るため全 4 点で評価しています。

![GPT-5.5 のコスト（C）×処理時間（D）散布図——Codex CLI（緑）と GitHub Copilot（青）の effort 4 点をプロット。×印は cache 崩れで外れ値となった Codex CLI low（回帰から除外）。両 CLI の点群はほぼ重なり、切片も傾きも近い「ほぼ互角」の構図](https://static.zenn.studio/user-upload/deployed-images/b1bad15220443b6a593799ae.png?sha=ba159f8f975eda4c8ee0f284c6fd383221cb4fff)

| CLI | 回帰式 (C = a·D + b) | 傾き a ($/1000s) | 切片 b ($) | R² | n |
| --- | --- | --- | --- | --- | --- |
| Codex CLI (native) | C = 0.00257·D + 0.159 | 2.57 | 0.159 | 0.996 | 3 |
| GitHub Copilot | C = 0.00183·D + 0.281 | 1.83 | 0.281 | 0.945 | 4 |

> Codex CLI は low（キャッシュヒット率の影響による外れ値）を除いた 3 点での回帰。GitHub Copilot は low を含む 4 点。

Opus 4.8 と違い、GPT-5.5 は Codex CLI と GitHub Copilot の両者に大きな差はなく、**切片も傾きも近い**——これが「ほぼ互角」と結論づける理由です。

## おまけ——7,000 AIクレジットを約 5 時間で使い切る

今回の GitHub Copilot の計測（240 試行）でいくら課金されたのか。コストは推定値ではなく、Copilot CLI がセッション終了時に報告する**実課金額**（`session.shutdown.data.totalNanoAiu`、nano-AI-Units 単位）を採用しています。全 240 試行のログから、この報告額と「トークン数 × 公式レート」で計算した額が**完全に一致**（最大誤差 1.1e-16）することも確認済みです。

![GitHub Copilot の AI usage 画面——Copilot Pro+ に毎月含まれる 7,000 AI credits が 7,000 / 7,000 で使い切られ、ゲージが満杯（赤）。次回リセットは 26 日後の Jul 1, 2026](https://static.zenn.studio/user-upload/deployed-images/e3ebe5362e03a6c34508be87.png?sha=e5316266e75ba29f08955a3935c7a35e2c401248)

集計すると、本走の実課金合計は **$69.997（≒ $70.00）**。GitHub Docs 上の換算では 1 AI credit = $0.01 なので、**ちょうど約 7,000 AI credits** です。事前のテストなどを含めると、$70.00を超えてしまいました。

!

GitHub Copilot Pro+ に毎月含まれる AIクレジットは、base credits 3,900 と flex allotment 3,100 を合わせた **7,000 AI credits** として記載されています。つまり今回の実験で、Pro+ 1 か月分のクレジットを**約 5 時間で完全に溶かした**計算になります。

### モデル別の内訳

| モデル | 試行数 | 実課金額 | AIクレジット換算 |
| --- | --- | --- | --- |
| Opus 4.8 | 4 effort × 3 タスク × 10 試行 | $43.42 | 約 4,342 credits |
| GPT-5.5 | 4 effort × 3 タスク × 10 試行 | $26.58 | 約 2,658 credits |
| 合計 | **240 試行** | **$69.997** | **約 7,000 credits** |

> 厳密には、GPT-5.5 の $26.58 に Copilot が 6 試行で Opus 4.8 の subagent を利用した課金 $1.88 が含まれています（GPT-5.5 モデル自体の支出は差し引き $24.70）。

なぜ Opus 4.8 がこれだけ消費するのか？

Copilot CLI の `/model` 画面には、モデルごとの credits レート（1M tokens あたり）が明示されています。

![Copilot CLI の /model 画面に表示される Claude Opus 4.8 のクレジットレート（per 1M tokens）——Input 500 / Cached input 50 / Output 2,500 credits](https://static.zenn.studio/user-upload/deployed-images/9a66867599ff5851ffacae0b.png?sha=675451819f00f9234758c3ba78fcd4119d97cee1)

![Copilot CLI の /model 画面に表示される GPT-5.5 のクレジットレート（per 1M tokens）——Input 500 / Cached input 50 / Output 3,000 credits](https://static.zenn.studio/user-upload/deployed-images/f0ab1a10535aa09a8361b339.png?sha=551267782ad79e22e316f10721086f5549d41495)

| 項目（per 1M tokens） | Opus 4.8 | GPT-5.5 |
| --- | --- | --- |
| Input | 500 credits（$5） | 500 credits（$5） |
| Cached input | 50 credits（$0.50） | 50 credits（$0.50） |
| Output | **2,500 credits（$25）** | 3,000 credits（$30） |

Output 単価は GPT-5.5 の方が高いにもかかわらず、実課金では Opus が 1.6 倍も食っています。正体は、ログ分析で見えた **cache-write** です。Copilot は毎セッションでシステムプロンプトと MCP 定義（約 36K tokens）を新規にキャッシュ書き込みし、これが **$6.25/1M tokens（= 625 credits、Input の 1.25 倍）** で課金されます。一回性の固定費なので effort を上げるほど希釈されますが、opus-low の短いタスクでは **1 試行コストの約 67% が cache-write** に消えていました。

「同一モデル・同一トークン単価でも、CLI フレームワークのキャッシュ戦略の差でコストが 1.5〜2 倍動く」——この実験で一番のコスト要因は、モデルでも effort でもなく、**CLI がキャッシュをどう扱うか**でした。

今回のような、RDB（PostgreSQL + psycopg2）のエッジケースのタスクを 240 回実行すると、GitHub Copilot Pro+ 1 か月の AIクレジットを消費してしまうという結果でした。もちろん、実行するタスクの内容によって大きく変わる可能性がありますが、1つの参考ケースとして捉えておいてください。

## Claude Code・Codex は約1,000試行で月額$200相当

ここまでの比較は、1試行あたりの実課金額・API換算コストを見てきました。一方で、実際の個人利用では Claude Code や Codex CLI を月額プランで使うケースもあります。そこで最後に、今回のタスクを「月額固定費で何回回せるか」という見方でも比較してみます。

ただしこれは実請求額の比較ではなく、あくまで API 等価額を月額固定費に当てはめた試算です。筆者の環境では Claude Code / Codex CLI はサブスク登録済みのため、下表の「API等価合計」は実際に追加請求された金額ではありません。

ここでの月額 $200 は、Claude Code 側は Claude Max 20x（Pro プランの 20 倍の利用量）、Codex CLI 側は ChatGPT Pro の税抜き月額を基準にしたものです。どちらも筆者が利用している月額固定プランの枠内であり、この記事のタスク実行ごとに追加で $200 請求されるという意味ではありません。

| CLI | API等価合計 | 月額$200比 | 損益分岐 |
| --- | --- | --- | --- |
| Claude Code / Opus 4.8 | $25.5 | 12.7% | 約 943 試行/月 |
| Codex CLI / GPT-5.5 | $23.9 | 12.0% | 約 1003 試行/月 |

この表から、Claude Code / Codex CLI は月に約 1,000 試行を回すと、API 等価額が月額 $200 に達することが分かります。

前述の GitHub Copilot の結果と合わせると、Claude Code / Codex CLI は「API 等価で月額 $200 を超えるほど使うか」が選択のポイントになります。一方、GitHub Copilot Pro+ は月額 $39 と 1/5 以下に見えるものの、7,000 credits の月次枠は今回の 240 試行でほぼ使い切りました。したがって、重い反復検証では「月額が安いか」よりも「7,000 credits の月次枠をどれだけ早く使い切るか」で見る必要があります。

## まとめ

Opus 4.8 と GPT-5.5 を、GitHub Copilot と Claude Code、Codex CLI で同じタスクを実行させてコストを比較すると、Opus 4.8 で大きな差が出ました。

* **Opus 4.8**： GitHub Copilot で使うと、Claude Code の「1.5倍〜2.0倍」コスト高となる
* **GPT-5.5**： GitHub Copilot と Codex で、かかるコストと処理時間は「ほぼ互角」

実運用では、Opus 4.8 を利用するのであれば Claude Code が優位であり、全体のコストパフォーマンスを考慮しても、今回のケースにおいては Claude Code で Opus 4.8 medium を利用するのが良さそうです。

前回行った、Opus 4.8（Claude Code）と GPT-5.5（Codex CLI）の詳細比較は [#21](https://zenn.dev/nnakapa/articles/lab-21-opus48-gpt55-reasoning-effort)にあります。Reasoning Effort の違いが QCD に与える影響について知りたい方はこちらから。

*本記事は、筆者個人の Raspberry Pi 5 / Ubuntu 26.04 環境における非公式な実験記録です。Claude Code、Codex CLI、GitHub Copilot CLI の一般的な性能優劣を示すものではありません。結果はタスク内容、プロンプト、CLI バージョン、モデル指定、ネットワーク状況、実行順、温度条件によって変化します。各名称は各社・各団体の商標または登録商標です。*

---

*この記事は「オトナの自由研究」シリーズの第22回です。消費財メーカーでデジタル戦略を推進する筆者が、最新テクノロジーを自分の手で試し、何ができるのか・どんな価値を生むのかを検証する過程を記録しています。*  
*※本連載は個人の実験と学びの共有であり、所属組織の公式見解ではありません。*
