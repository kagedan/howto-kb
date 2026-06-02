---
id: "2026-06-01-roadmwss-設計入門1-アーキテクチャ編-世代wssbsrscdc-powered-by-cl-01"
title: "ROADM/WSS 設計入門(1) アーキテクチャ編 — 世代・WSS・B&S/R&S・CDC powered by claude"
url: "https://qiita.com/dabide/items/bbfd6b36496f104f9895"
source: "qiita"
category: "construction"
tags: ["qiita"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

## 0. 対象と前提

- 対象：光伝送を学習者する人で、リンクバジェット・OSNR・OTN の基礎を理解している読者
- ゴール：ROADM を「世代」「WSS」「B&S/R&S」「CDC」の視点で説明できるようになる

---

## 1. ROADM の役割と機能

ROADM（Reconfigurable Optical Add/Drop Multiplexer）は、波長単位で「通過」「上げ下ろし」を遠隔から再構成できる光ノードです。

| 経路 | 役割 | O/E変換 | 損失の考え方 |
|---|---|---|---|
| express（スルー） | 通過波長を電気に落とさず別方路へ中継 | なし（全光） | ノード内光損失のみ。多段通過で累積 |
| add/drop（局内） | 局内トランスポンダで終端／挿入 | 終端機器側で発生 | add/drop 構造の損失（express とは別系統） |

- **degree（方路）**：1本の回線方向。2-degree が最小、3以上が MD-ROADM（Multi-Degree）。
- ROADM の内ではトランスペアレント（光で透過）で、O/E 変換はしない。変換は接続するトランスポンダ等で起こる。

### O/E と O/E/O

| 終端機器 | 信号変換 | 呼称 |
|---|---|---|
| コヒーレント受信機 → ルータ内蔵プラガブル等 | O→E のみ | O/E |
| トランスポンダ（クライアントが光IF） | O→E→O | O/E/O |
| トランスポンダ同士の再生中継 | O→E→O（同一信号の3R再生） | O/E/O |

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4177943/271ee723-4f12-4008-9a8f-9d9795da5952.png)


---

## 2. 世代進化 — 「何を自由化したか」

世代は「解いた制約」で見ていくと進化の方向性が見えます。

| 世代 | 解いた制約 | 残った制約 | 要素技術 |
|---|---|---|---|
| FOADM | （固定上げ下ろし） | 波長変更＝物理工事 | 薄膜フィルタ(TFF) |
| 第1世代(WB) | 遠隔での通過/遮断 | add/drop が色・方路に固定 | 波長ブロッカ＋スプリッタ |
| 第2世代(WSS) | 方路選択（多方路化） | add/drop が色・方路に固定 | 1×N WSS |
| 第3世代(CDC) | add/drop の色・方路・競合 | グリッド固定（50GHz等） | M×N WSS／マルチキャストスイッチ |
| 第4世代(CDC-F) | グリッド（可変帯域） | 制御複雑性・コスト | LCoS-WSS＋flexgrid |

方向性は一貫しており、「現地工事の削減」と「波長資源の利用効率」です。

---

## 3. WSS とは（LCoS と MEMS）

WSS（Wavelength Selective Switch）は、ROADM の中核となる部品です。入力 WDM を波長ごとに分離し、各波長を任意の出力ポートへ独立に振り分けます（同時に減衰量も制御してパワー等化）。

入力光を回折格子で波長を空間分離し各波長を任意ポートへ偏向する動作は同じで、**偏向素子だけが違います**。

| 観点 | LCoS-WSS | MEMS-WSS |
|---|---|---|
| 偏向素子 | 画素化した液晶位相板（1枚で全波長、ホログラムで制御） | 波長ごとの微小傾斜ミラー |
| フレキシブルグリッド | 得意（画素単位で任意帯域幅） | 不利（固定パスバンド寄り、flexgrid非対応とされる） |
| 挿入損失 | やや大（回折・偏光依存） | 小（直接反射） |
| パワー等化 | 画素制御で容易 | 可能だが粒度依存 |
| 主流 | flexgrid WSS の主流 | 旧世代・固定グリッド用途 |

- LCoS は画素の位相パターンで偏向するため、任意のパスバンド幅を設定できる（＝flexgrid 対応）。
- 線路側の WSS はすべて **1×N 型**（共通ポート1＝回線側、分岐 N＝他方路＋Add/Drop）。実機では 1×9・1×20 等がある。
- 挿入損失はポート数とともに増える傾向（例：1×25 LCoS で 5.4〜9.6 dB／C帯）。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4177943/251d2a7e-f831-4b1f-a2df-8185a7e82218.png)

---

## 4. フレキシブルグリッド（G.694.1）

LCoS が任意帯域を作れるためフレキシブルグリッドを実現できます。

| 項目 | 値 |
|---|---|
| 基準周波数 | 193.1 THz | 
| flexgrid 中心周波数粒度 | 6.25 GHz |
| flexgrid スロット幅粒度 | 12.5 GHz |
| 中心周波数の式 | **f [THz] = 193.1 + n × 0.00625**（n は整数） |

- 単位に注意：193.1 は THz、粒度 6.25 GHz は 0.00625 THz。式は THz で統一して `193.1 + n×0.00625`。
- 400G/800G 等で必要な広帯域スロットを無駄なく割り当てられるのが flexgrid の価値。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4177943/16b96d90-9ff7-413d-ae1d-067646084cd9.png)


---

## 5. ノードアーキテクチャ：B&S と R&S

### 5.1 構造の違い

- **Broadcast-and-Select (B&S)**：入力を受動スプリッタで全方路に分配 → 出力 WSS で選択。
- **Route-and-Select (R&S)**：入力 WSS で経路選択 → 出力 WSS で再選択（WSS 2段）。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4177943/3c865d95-a9ed-4899-939d-10921e1698dd.png)

### 5.2 4方路の具体構成

degree は信号が来た方向へは折り返しません（ループバックになり意味がないため）。よって入力は他方路へ express するか局内へ drop、出力は他方路からの express か局内 add。結果として入出力は他方路どうしの**フルメッシュ**になります。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4177943/b546c40b-c482-4d5a-822d-336f70db6eb4.png)


### 5.3 ポート構成

| 部品 | 場所 | ポート構成（express＋Add・Drop） | 種別 |
|---|---|---|---|
| 入力スプリッタ（B&S） | 各方路 入力側 |  1×4 | 受動 1×N （分波）|
| 入力WSS（R&S） | 各方路 入力側 |  1×4 | 能動 1×N （分波）|
| 出力WSS（両方） | 各方路 出力側 |  4×1 | 能動 N×1（合波） |

- **Add/Drop 側は別部品（M×N WSS）**。これは CDC で扱う。

### 5.4 損失の方路数依存（簡易モデル）と分岐点

B&S は分配損失が `10·log` で増加、R&S は段数固定でほぼ一定 → 計算上はある方路数で合計損失が逆転します。以下は**損失だけを見た説明用の仮定モデル**です。

**仮定モデル**

- WSS 挿入損失 = 6.0 dB/段
- スプリッタ過剰損失（材料吸収・散乱・結合不完全・製造ばらつき） = 1.0 dB（分岐比によらず一定とする）
- express の分岐は 1×(N−1)、理想分配損失 = 10·log₁₀(N−1) dB

これより、
- B&S express損失 = 10·log₁₀(N−1) + 1.0 + 6.0
- R&S express損失 = 6.0 × 2 = 12.0 dB（分岐数に依存しない）

| 方路数 N | B&S express [dB] | R&S express [dB] | 差 (B&S−R&S) |
|---|---|---|---|
| 2 | 7.0 | 12.0 | −5.0（B&S有利） |
| 3 | 10.0 | 12.0 | −2.0（B&S有利） |
| 4 | 11.8 | 12.0 | −0.2（ほぼ拮抗） |
| 5 | 13.0 | 12.0 | +1.0（R&S有利） |
| 8 | 15.5 | 12.0 | +3.5（R&S有利） |
| 16 | 18.8 | 12.0 | +6.8（R&S有利） |

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4177943/6d0829cf-cc7c-4696-91c4-6dd5dec479b5.png)

簡易モデルの交差点：10·log₁₀(N−1) = 6 − 1 = 5 → N ≈ 4.2。

**実際の交差点について**：実際には B&S は概ね 9×9（9方路）未満、R&S はそれ以上で採用される。実際の WSS 挿入損失は 5〜10 dB 程度でポート数とともに増えるため純損失の交差点も上振れし、さらに移行判断はコストやクロストークの影響も考慮される。



### 5.5 クロストークと帯域狭窄

B&S と R&S は使い分けが重要です。

| 観点 | B&S | R&S |
|---|---|---|
| 挿入損失（多方路） | 不利（分配損失が増大） | 有利（ほぼ一定） |
| クロストーク／隔離度 | 不利（遮断は出力WSS単段頼み） | 有利（WSS2段で抑圧） |
| 帯域狭窄（passband narrowing） | **有利**（WSS1段＝狭窄が少ない） | 不利（WSS2段＝狭窄が約2倍） |

- 損失・クロストークは R&S 有利、**帯域狭窄は B&S 有利**。
- 多方路・高密度では総合的に R&S が選ばれることが多いが、帯域狭窄の観点は B&S の利点として残る。
- express 損失だけで方式を決めず、クロストーク要件・帯域狭窄・コストを併せて判断する。

---

## 6. CDC（概念と M×N WSS 実装）

### 6.1 3属性とコスト

Colorless / Directionless / Contentionless は**独立した3つの属性**で、機能としては次の順で追加されます。

```
色・方路固定 → Colorless → +Directionless → +Contentionless
（着色/着方路）  (C)          (CD)             (CDC)
```

| 属性 | 解消する制約 | できるようになること | 実装の重さ |
|---|---|---|---|
| Colorless | add/drop ポートが特定波長に固定 | 任意ポートに任意波長を割当 | 軽〜中 |
| Directionless | add/drop ポートが特定方路に固定 | 上げ下ろし波長を任意の方路へ | 中 |
| Contentionless | 同一ノードで同一波長を複数同時に上げ下ろし不可 | 同じ色を複数方路で同時に扱える | 重（最も高コスト） |

> **判断ポイント**：Contentionless はコストが高いため、波長に余裕があり競合が生じないなら CD 構成で対応する。要否は「同一波長の同時上げ下ろし頻度 × トラフィックの動的さ」で決める。

### 6.2 実装：M×N WSS / マルチキャストスイッチ

M×N WSS は「方路側 M ポート × トランスポンダ側 N ポート」の波長選択スイッチで、任意方路の任意波長を任意トランスポンダへ競合なく接続します（§5.3 の線路側 1×N とは別部品）。各属性は次のように実現されます。

- Colorless：トランスポンダの可変波長受信機が任意波長を選択
- Directionless：M×N WSS が任意の方路へ接続
- Contentionless：同一波長を別方路から複数トランスポンダへ同時ドロップ可（波長選択で競合回避）

実装は2系統：

| 観点 | マルチキャストスイッチ（MCS） | M×N WSS |
|---|---|---|
| 原理 | スプリッタで分配＋光スイッチ（波長非依存） | 波長選択スイッチ |
| 損失 | 大（ブロードキャスト）→ 増幅器が必要 | 小 |
| Contentionless | 構造で実現（損失大） | 素子で内在的に実現 |
| コスト | 従来は安価 | 高め |

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4177943/b93c81b7-60d1-4b6e-a68a-8e06cef76616.png)

---

## 7. ROADM 1方路の装置構成（EDFA / OCM / OSC）

信号流れ順の構成。次記事で予定している「設計パラメータ編」のリンクバジェットの前提になります。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4177943/252f76d4-75a6-41bc-97f3-f6f13b4044ba.png)

ポイント：

- プリアンプEDFA は受信した WDM 光を持ち上げる。**OSNR はプリアンプの NF とパワーで決まる**。ブースタEDFA は出力光パワーを確保。
- タップ＋OCM（Optical Channel Monitor）で各チャネルのパワーを監視し、WSS の チャンネル毎の減衰でパワー等化。
- OSC（光監視チャネル、ITU-T G.692 が定義）は帯域外（よく使われる例：1510nm。他に1620/1310nm 等、ベンダー依存）で**各ノードで終端・再生**。EDFA 利得帯（C帯 ~1530–1565nm）外なので、RX は増幅前に分離、TX は増幅後に合波してアンプを迂回。

---

## 8. メトロ vs 長距離

同じ ROADM でも、メトロか長距離かで最適解が変わります。

| 観点 | メトロ | 長距離 |
|---|---|---|
| 典型 degree 数 | 少〜中（2〜4） | 多（4〜8+） |
| express : add/drop 比 | add/drop 比が高い | express（通過）比が高い |
| 主な制約 | コスト・設置性 | OSNR・クロストーク・帯域狭窄 |
| 採用傾向 | B&S も許容、固定50GHz が多い | R&S＋CDC-F、flexgrid／400G・800G |

---

## 9. まとめ

- ROADM は「express / add/drop」「degree」「世代」「WSS（LCoS/MEMS）」「B&S/R&S」「CDC」で整理できる。
- B&S と R&S は両面トレードオフ：損失・クロストークは R&S 有利、帯域狭窄は B&S 有利。
- flexgrid は中心周波数 `f[THz]=193.1+n×0.00625`、スロット幅12.5GHz刻み。LCoS-WSS で実現され400G/800G を効率的に収容可能。
- 数値の扱い：グリッド等の規格値は ITU-T、dB 値（挿入損失・隔離度）はベンダー依存で実際の値を要確認。

---

## 参考文献・規格

**ITU-T 規格**
- G.694.1（DWDM 周波数グリッド、固定／flexible）: https://www.itu.int/rec/T-REC-G.694.1
- G.672（MD-ROADM の特性）: https://www.itu.int/rec/T-REC-G.672-202505-I
- G.692（OSC の定義）／G.671（光部品の伝送特性）／G.680（光ネットワーク要素の物理伝達関数）

**WSS（LCoS / MEMS）・挿入損失**
- Laser Focus World（LCoS vs MEMS）: https://www.laserfocusworld.com/fiber-optics/article/16550240/fiber-based-components-liquid-crystal-wavelength-selective-switches-challenge-mems-designs

**OSC**
- Google Patents US9544050B2（ITU-T G.692 定義、OSC は EDFA 帯域外・各ノード終端）: https://patents.google.com/patent/US9544050B2/en

**WSS / CDC の仕組み**
- ROADM関連（光スイッチ技術）：https://journal.ntt.co.jp/backnumber2/1311/files/jn201311016.pdf
- CDCを用いた光伝送ネットワーク：https://www.docomo.ne.jp/binary/pdf/corporate/technology/rd/technical_journal/bn/vol27_4/vol27_4_009jp.pdf
