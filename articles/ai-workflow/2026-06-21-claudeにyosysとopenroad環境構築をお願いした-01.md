---
id: "2026-06-21-claudeにyosysとopenroad環境構築をお願いした-01"
title: "Claudeにyosysとopenroad環境構築をお願いした"
url: "https://qiita.com/soldierboy/items/beb47801a1c81c5b4e35"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-06-21"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

# yosysとopenroad

yosysは論理合成環境，openroadは配置配線ツールとなっている．
これらの環境構築とサンプルの実行を最近はやりのClaudeにお願いしてみた．

## 1.環境構築

### 1-1.PCのスペック

今回は、WindowsノートPC上でWSLを用いてUbuntu環境を構築し，そこにインストールした．
以下は今回考慮すべき箇所のみ記載しており，Ubuntuに割り当てているCPU数は必要に応じて拡張してほしい．

- WindowsノートPCのスペック
  - 実装RAM:16.0GB
   - プロセッサ:Intel(R) Core(TM) 5 210H (2.20 GHz)
- WSL上のUbuntu
 - OS:Ubuntu24.04
 - メモリー:12GB

Ubunutuに割り当てるメモリーはデフォルトより大きくするか後述するビルドで並列数を調整しないと失敗する．
12GBにしておけば問題はないが，4～8GBとかにしているとビルドで落ちることがある．
以下に割り当てメモリー容量を増やす方法を記載．

- `C:\Users\ユーザー名\.wslconfig`を開く．
- 以下を修正
```text
[wsl2]
memory=12GB
swap=8GB
processors=4
```
- WSLで再読み込み
```sh
wsl --shutdown # 起動していない場合は不要
wsl
```

### 1-2.yosysとopenroadのインストール

以降，Ubunutuでの作業となる．

#### 1-2-1.GitHubからcloneする

```sh
git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts
```

#### 1-2-2.safe.directory設定

```sh
git config --global --add safe.directory '*'
```

#### 1-2-3.依存パッケージインストール

```sh
sudo ./etc/DependencyInstaller.sh -all 2>&1 | tee dep.log
```

#### 1-2-4.ビルド(4)

```
./build_openroad.sh --local --threads 2 2>&1 | tee build.log
```
#### 1-2-5.ビルド完了確認

```sh
ls tools/install/OpenROAD/bin/openroad
ls tools/install/yosys/bin/yosys
```

ファイルが存在していればビルド成功．
これでビルド完了し，インストールできた．

### 1-3.サンプルの実行

次にサンプルとしてフローを一通り流せるものを実行する．

```sh
cd /home/ユーザー名/OpenROAD-flow-scripts/flow
make DESIGN_CONFIG=./designs/nangate45/gcd/config.mk
```

これで一通りフローを実行できる．

## 2.各ステップの成果物

各ステップでの成果物は以下に出力される．

```sh
ls /home/ユーザー名/OpenROAD-flow-scripts/flow/results/nangate45/gcd/base/
```

### 2-1.主要ファイル

| ファイル名 | 概要 |
|--|--|
| 1_synth.v | 合成済みネットリスト |
| 2_floorplan.def | フロアプラン |
| 3_place.def | 配置後レイアウト |
| 4_cts.def |  CTS後レイアウト |
| 5_route.def | ルーティング後レイアウト |
| 6_final.gds | 最終GDSII |

### 2-2.成果物概要

| 工程 | ファイル | 概要 |
|--|--|--|
| 論理合成(Yosys) | 1_1_yosys_canonicalize.rtlil | RTL正規化後の中間表現 |
| | 1_2_yosys.v                    | 合成済みネットリスト |
| | 1_2_yosys.sdc                  | 合成後SDC |
| | 1_synth.odb                    | OpenROAD DB形式 |
| フロアプラン | 2_1_floorplan.odb | フロアプラン後 |
| | 2_2_floorplan_macro.odb        | マクロ配置後 |
| | 2_3_floorplan_tapcell.odb      | タップセル挿入後 |
| | 2_4_floorplan_pdn.odb          | PDN生成後 |
| 配置 | 3_1～3_6_place_*.odb      | 各配置ステップ後 |
| CTS  | 4_1_cts.odb               | CTS後 |
| | 4_before_rsz_lec.v             | リサイズ前ネットリスト |
| | 4_after_rsz_lec.v              | リサイズ後ネットリスト |
| ルーティング | 5_1_grt.odb       | グローバルルーティング後 |
| | 5_2_route.odb                  | 詳細ルーティング後 |
| | 5_3_fillcell.odb               | フィルセル挿入後 |
| 最終成果物 |   6_final.gds       | 最終GDSIIファイル※テープアウトに使う |
| |  6_final.def                   | 最終DEFファイル |
| |  6_final.v                     | 最終ネットリスト |
| |  6_final.spef                  | 寄生素子情報 |
| |  6_final.sdc                   | 最終SDC |

### 2-3.各ステップの実行

変数で以下を設定しておく．

```sh
CFG=./designs/nangate45/gcd/config.mk
```

#### 2-3-1.RTL正規化

```sh
make DESIGN_CONFIG=$CFG do-yosys-canonicalize
```

#### 2-3-2.論理合成

```sh
make DESIGN_CONFIG=$CFG do-1_synth
```

#### 2-3-3.フロアプラン

```sh
make DESIGN_CONFIG=$CFG do-2_1_floorplan
```

#### 2-3-4.マクロ配置

```sh
make DESIGN_CONFIG=$CFG do-2_2_floorplan_macro
```

#### 2-3-5.タップセル挿入

```sh
make DESIGN_CONFIG=$CFG do-2_3_floorplan_tapcell
```

#### 2-3-6.PDN生成

```sh
make DESIGN_CONFIG=$CFG do-2_4_floorplan_pdn
```

#### 2-3-7.配置(IO仮配置)

```sh
make DESIGN_CONFIG=$CFG do-3_1_place_gp_skip_io
```

#### 2-3-8.IO配置

```sh
make DESIGN_CONFIG=$CFG do-3_2_place_iop
```

#### 2-3-9.グローバル配置

```sh
make DESIGN_CONFIG=$CFG do-3_3_place_gp
```

#### 2-3-10.リサイズ・バッファ挿入

```sh
make DESIGN_CONFIG=$CFG do-3_4_place_resized
```

#### 2-3-11.詳細配置

```sh
make DESIGN_CONFIG=$CFG do-3_5_place_dp
```

#### 2-3-12.タイミング修復

```sh
make DESIGN_CONFIG=$CFG do-3_6_place_repair_timing
```

#### 2-3-13.CTS

```sh
make DESIGN_CONFIG=$CFG do-4_1_cts
```

#### 2-3-14.グローバルルーティング

```sh
make DESIGN_CONFIG=$CFG do-5_1_grt
```

#### 2-3-15.詳細ルーティング

```sh
make DESIGN_CONFIG=$CFG do-5_2_route
```

#### 2-3-16.フィルセル挿入

```sh
make DESIGN_CONFIG=$CFG do-5_3_fillcell
```

#### 2-3-17.GDS生成

```sh
make DESIGN_CONFIG=$CFG do-6_1_fill
```

#### 2-3-18.report タイミングレポート

```sh
make DESIGN_CONFIG=$CFG do-6_report
```

### 2-4.ログの確認

#### 2-4-1.合成結果(セル数・面積)

```sh
cat ./reports/nangate45/gcd/base/synth_stat.txt
```

```log
16. Printing statistics.

=== gcd ===

        +----------------------------Count including submodules.
        |        +-------------------Area including submodules.
        |        |        +----------Local count, excluding submodules.
        |        |        |        +-Local area, excluding submodules.
        |        |        |        |
      546        -      546        - wires
      592        -      592        - wire bits
       42        -       42        - public wires
       88        -       88        - public wire bits
        8        -        8        - ports
       54        -       54        - port bits
        -        -        -        - memories
        -        -        -        - memory bits
        -        -        -        - processes
      521  663.138      521  663.138 cells
        4    4.256        4    4.256   AND2_X1
        1     1.33        1     1.33   AND2_X2
        1    1.596        1    1.596   AND4_X1
        5     5.32        5     5.32   AOI21_X1
        2    3.724        2    3.724   AOI21_X2
        1    3.458        1    3.458   AOI21_X4
        5     3.99        5     3.99   BUF_X1
        3    3.192        3    3.192   BUF_X2
        2    3.724        2    3.724   BUF_X4
        5    17.29        5    17.29   BUF_X8
        2    1.596        2    1.596   CLKBUF_X1
       35   158.27       35   158.27   DFF_X1
       72   38.304       72   38.304   INV_X1
       12    9.576       12    9.576   INV_X2
        3     3.99        3     3.99   INV_X4
      164  130.872      164  130.872   NAND2_X1
       28    37.24       28    37.24   NAND2_X2
        8   19.152        8   19.152   NAND2_X4
       19   20.216       19   20.216   NAND3_X1
        9   16.758        9   16.758   NAND3_X2
        1    3.458        1    3.458   NAND3_X4
       28    37.24       28    37.24   NAND4_X1
       28   22.344       28   22.344   NOR2_X1
       11    14.63       11    14.63   NOR2_X2
        7   16.758        7   16.758   NOR2_X4
        4     5.32        4     5.32   NOR4_X1
       38   40.432       38   40.432   OAI21_X1
        9   16.758        9   16.758   OAI21_X2
        3    3.192        3    3.192   OR2_X1
        7   11.172        7   11.172   XNOR2_X1
        2    3.192        2    3.192   XOR2_X1
        2    4.788        2    4.788   XOR2_X2

   Chip area for module '\gcd': 663.138000
     of which used for sequential elements: 158.270000 (23.87%)
```

#### 2-4-2.配線混雑レポート
```sh
cat logs/nangate45/gcd/base/5_1_grt.log | grep -i "congestion\|overflow"
```

#### 2-4-3.IRドロップ
```sh
cat logs/nangate45/gcd/base/6_report.log | grep -i "ir\|power"
```

#### 2-4-4.タイミングレポート
```sh
cat logs/nangate45/gcd/base/6_report.log
```

### 2-5.OpenROAD GUIで各ステップのレイアウトを確認

OpenROAD GUIでOBDを読み込み段階的なレイアウトを確認できる．
OBDはOpenROAD独自のデータベース形式が使用するチップ設計データベースのバイナリファイルで拡張子が`.odb`となる．OpenROAD以外では`OA/ORCAD`形式などがある．

中に含まれるデータは以下となる．
- 回路のネットリスト(セル・ネット・ピン)
- フロアプラン情報(チップサイズ・電源レール)
- セルの配置座標
- クロックツリー情報
- 配線情報(ルーティング)
- タイミング制約



### 2-5-1.OpenROAD GUIの起動

```sh
openroad -gui
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4450162/b6ee90bd-7aca-4b81-a2d4-7eca9db6bba1.png)

### 2-5-2.TclコンソールでODB(OpenDataBase)を読み込み

OpenROAD GUIが起動できたら`TCL commands`に以下コマンドを入力しEnterを押すことでODBを読み込める．
なお，1回で読み込めるOBDファイルは1つだけで次段階のOBDを読み込む．

#### 2-5-2-1.フロアプラン直後

`TCL commands`に以下コマンドを入力．
フロアプラン完了時点のスナップショット`2_4_floorplan_pdn.odb`を読み込める．

```tcl
read_db results/nangate45/gcd/base/2_4_floorplan_pdn.odb
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4450162/111e054e-7cb2-4adb-8c0d-4eec98cf8781.png)

#### 2-5-2-2.配置後

詳細配置完了時点`3_5_place_dp.odb`を読み込める．

```tcl
read_db results/nangate45/gcd/base/3_5_place_dp.odb
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4450162/2f38fafd-cfe9-4dc1-a7cb-6fd75490bf7d.png)

#### 2-5-2-3.CTS後

クロックツリー合成完了時点`4_1_cts.odb`を読み込める．

```tcl
read_db results/nangate45/gcd/base/4_1_cts.odb
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4450162/e678a2fb-0616-46ec-b547-c095b62aa963.png)

#### 2-5-2-4.ルーティング後

ルーティング完了時点`5_2_route.odb`を読み込める．

```tcl
read_db results/nangate45/gcd/base/5_2_route.odb
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4450162/c41b8126-8010-4b66-9bee-6ed2205c4813.png)
