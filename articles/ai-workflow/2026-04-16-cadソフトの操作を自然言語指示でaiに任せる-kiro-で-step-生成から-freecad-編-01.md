---
id: "2026-04-16-cadソフトの操作を自然言語指示でaiに任せる-kiro-で-step-生成から-freecad-編-01"
title: "CADソフトの操作を自然言語指示でAIに任せる — Kiro で STEP 生成から FreeCAD 編集まで"
url: "https://zenn.dev/aws_japan/articles/45fb5d3130035d"
source: "zenn"
category: "ai-workflow"
tags: ["Python", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

[前回の記事](https://zenn.dev/aws_japan/articles/0bb6554b10c6bc)では、AWS の「[Auto&Manufacturing - Kiro for Business Users](https://catalog.us-east-1.prod.workshops.aws/workshops/2b863a58-f3b0-414e-98c2-2cb095c4ac81/en-US)」ワークショップを紹介しました。AI コーディングアシスタント「Kiro」を使い、自然言語の指示だけで CFD シミュレーションや 3D モデリングを行う内容です。

前回の記事の「[応用：より複雑な産業機械の3Dモデリング](https://zenn.dev/aws_japan/articles/0bb6554b10c6bc#%E5%BF%9C%E7%94%A8%EF%BC%9A%E3%82%88%E3%82%8A%E8%A4%87%E9%9B%91%E3%81%AA%E7%94%A3%E6%A5%AD%E6%A9%9F%E6%A2%B0%E3%81%AE3d%E3%83%A2%E3%83%87%E3%83%AA%E3%83%B3%E3%82%B0)」セクションでは、6軸多関節ロボットアームの3Dモデルを自然言語の指示だけで生成しました。

このとき使ったのは Python の numpy-stl ライブラリで、三角形の頂点座標を直接計算して **STL ファイルを出力する方法です。CAD ソフトは一切使っていません**。

ワークショップでは `pip install numpy-stl` 一発で環境が整う手軽さから STL が採用されていましたが、STL は三角形メッシュの集合にすぎないため、CAD ソフトでのフィーチャーベースの編集（穴の直径変更、フィレット追加など）は実用的に困難です。**設計の初期探索やコンセプト確認には使えても、そのまま実務の CAD ワークフローには乗りません**。

![](https://static.zenn.studio/user-upload/649edc2a456b-20260416.png)  
【画像】前回生成した6軸ロボットアームのSTLモデル

今回は一歩踏み込み、このロボットアームを **STEP 形式**で出力し直すことで、**AI が生成した 3D モデルを CAD ソフトで開いて編集できることを実証します**。

![](https://static.zenn.studio/user-upload/4f80068c8f90-20260416.png)

> 注記：本ワークショップでは、Kiro CLI の基盤モデルとして Claude Opus 4.6 を使用しています。モデルのバージョンによって生成されるコードの品質や挙動が異なる場合があります。

**続編を公開しました**: 本記事で STEP 出力・FreeCAD 編集したロボットアームに対して、Kiro に FreeCAD FEM で構造解析（CAE）を実行させ、応力・変位を定量評価する記事を公開しました。設計 → CAD 編集 → 強度検証の一気通貫パイプラインが完成しています。

> 👉 [AI が設計して、AI が強度検証する — Kiro × FreeCAD FEM でロボットアーム CAE 構造解析](https://zenn.dev/aws_japan/articles/a5cd987ecb59ff)

### STL と STEP の違い

|  | STL | STEP |
| --- | --- | --- |
| データの中身 | 三角形の頂点座標の集まり | B-rep（面・エッジ・頂点の数学的定義） |
| CADソフトでの編集 | メッシュ編集は可能だが、フィーチャーベースの編集は実用的に困難 | 穴追加・フィレット・ブーリアン演算が可能 |
| 形状情報の保持 | 表面の近似形状のみ | 面・エッジのトポロジーと正確な曲面定義を保持 |
| パラメトリック設計履歴 | なし | なし（STEPもフィーチャーツリーは保持しない） |
| 用途 | 3Dプリント、可視化、解析 | CAD設計、製造データ受け渡し |

**STL をビットマップ画像（JPEG）に例えるなら、STEP は PowerPoint ファイルに近い存在です**。JPEG は見た目は分かるけれど、写っている文字や図形を個別に選んで編集することはできません。一方 PowerPoint なら、テキストボックスや図形を一つずつ選択して移動・変形・削除できます。STEP も同様に、面やエッジを選択してフィレットを追加したり穴を開けたりできます。

ただし、この例えは厳密ではありません。PowerPoint は「どの順番でオブジェクトを作ったか」という作成履歴も保持しますが、STEP にはそれがありません。STEP が保持するのは「形状そのもの」であり、「形状の作り方（設計履歴）」ではありません。SolidWorks 等で STEP を開くと「ダムソリッド（dumb solid）」として読み込まれ、フィーチャーツリーは空の状態になります。つまり、面やエッジを選んで新しい加工を加えることはできるけれど、元の設計手順を遡って「この穴の直径だけ変えたい」といった操作はできない、ということです。

---

## 今回の流れ

本記事では、以下の 3 ステップで進めます。

```
Step 1: Kiro が CadQuery のコードを生成し、STEP ファイルを出力
        （自然言語の指示 → Python スクリプト → STEP）

Step 2: Kiro が FreeCAD の Python API を使って STEP を編集
        （フィレット追加、穴追加などの CAD 操作をスクリプトで実行）

Step 3: FreeCAD の GUI で STEP を開き、人間が対話的に編集できることを確認
        （パーツ選択、フィーチャー追加など通常の CAD 操作）
```

Step 1〜2 は Kiro への自然言語指示だけで完結します。Step 3 は人間が FreeCAD を操作する作業ですが、Step 2 で Kiro がスクリプトで行った編集と同じことを GUI でもできる、という確認です。

---

## 環境構築

### 使用ツール

| ツール | バージョン | 用途 |
| --- | --- | --- |
| CadQuery | 2.7.0 | Python から STEP ファイルを生成 |
| OpenCASCADE (OCP) | 7.8.1.2 | CadQuery の内部 CAD エンジン |
| FreeCAD | 1.1.0 | STEP ファイルの読み込み・編集・可視化 |
| Python | 3.12 | スクリプト実行環境 |

### インストール手順

CadQuery は OpenCASCADE（CAD エンジン）を内蔵しているため、pip 単体ではインストールできません。conda（miniforge）経由でインストールします。以下は macOS での手順です。

```
# miniforge がなければインストール（macOS）
brew install miniforge

# CadQuery 環境を作成（Python 3.12 + CadQuery + OCP を一括インストール）
micromamba create -n cadquery python=3.12 cadquery -c conda-forge -y

# FreeCAD のインストール（macOS）
brew install --cask freecad
```

Windows の場合は、[miniforge のインストーラー](https://github.com/conda-forge/miniforge#miniforge3)をダウンロードして実行し、`micromamba create` コマンドは同じです。FreeCAD は [公式サイト](https://www.freecad.org/downloads.php) からインストーラーを入手できます。

前回のワークショップで numpy-stl が `pip install numpy-stl` の一発で入ったのに対し、CadQuery は conda 環境が必要です。これが前回のワークショップで STL を採用した理由の一つであると予想されます — 25分のワークショップでは環境構築の安定性が優先されると思われます。

---

## STEP モデルの生成

### 対象モデル：6軸多関節ロボットアーム

前回のブログで STL 版を紹介した [6 軸ロボットアーム](https://zenn.dev/aws_japan/articles/0bb6554b10c6bc#%E5%BF%9C%E7%94%A8%EF%BC%9A%E3%82%88%E3%82%8A%E8%A4%87%E9%9B%91%E3%81%AA%E7%94%A3%E6%A5%AD%E6%A9%9F%E6%A2%B0%E3%81%AE3d%E3%83%A2%E3%83%87%E3%83%AA%E3%83%B3%E3%82%B0)を、今回は CadQuery で STEP 形式として再作成します。

### Kiro へのプロンプト

まず参考として、前回の記事で STL 版ロボットアームを生成したときのプロンプト（抜粋）を示します。

```
産業用6軸多関節ロボットアームの3Dモデルを生成する generate_robot_arm.py という
Pythonスクリプトを構築してください。numpy-stl、numpy、matplotlib のみを使用してください。

■ ロボットアーム構成（ベースから先端へ）：
1. ベース（J1軸: 旋回） — 固定台座: 円筒 直径300mm 高さ50mm、旋回部: 円筒 直径250mm 高さ100mm
2. ショルダー（J2軸: 前後傾動） — 関節ハウジング: 直径200mm 高さ150mm
3. 上腕（リンク1） — 長さ500mm、断面: 150mm x 120mm
4. エルボー（J3軸: 上下傾動） — 関節ハウジング: 直径160mm 高さ120mm
5. 前腕（リンク2） — 長さ450mm、断面: 120mm x 100mm
6. 手首（J4/J5/J6軸） — 3段の円筒
7. エンドエフェクタ（ツールフランジ） — 直径63mm（ISO 9409-1準拠）、ボルト穴6個

■ 姿勢パラメータ：
- J1〜J6の関節角度を変数化し、順運動学（FK）で各リンクの位置・姿勢を計算
```

今回は、この STL 版と同じ形状仕様を STEP 形式で出力するよう Kiro に指示します。

```
前回作成した6軸ロボットアーム（demos/06_robot-arm/generate_robot_arm.py）と
同じ形状仕様で、CadQuery を使って STEP 形式で出力するスクリプトを書いてください。

- 各パーツ（ベース、旋回部、ショルダー関節、上腕、エルボー関節、前腕、手首3段、フランジ）を
  個別のソリッドとして生成
- 順運動学（FK）で関節角度に応じた位置・姿勢を計算
- CadQuery の Assembly 機能でパーツを組み立て
- STEP 形式でエクスポート
```

### 生成されたコードのポイント

Kiro が生成した CadQuery スクリプトの特徴的な部分：

```
import cadquery as cq

# CadQuery のソリッドモデリング — STL版との違い
def make_cylinder(radius, height):
    return cq.Workplane("XY").circle(radius).extrude(height)

def make_box(w, d, h):
    return cq.Workplane("XY").rect(w, d).extrude(h)

# フランジにボルト穴を開ける — STLでは実用的に困難な操作
def make_flange(radius, height, bolt_r, bolt_pcd, bolt_count):
    wp = cq.Workplane("XY").circle(radius).extrude(height)
    for k in range(bolt_count):
        angle = 2 * math.pi * k / bolt_count
        bx = (bolt_pcd / 2) * math.cos(angle)
        by = (bolt_pcd / 2) * math.sin(angle)
        wp = wp.faces(">Z").workplane().pushPoints([(bx, by)]).hole(bolt_r * 2)
    return wp
```

STL 版では三角形の頂点座標を直接計算していましたが、CadQuery 版では「円を描いて押し出す」「穴を開ける」といった **CAD 的な操作** でモデルを構築しています。CadQuery は内部で OpenCASCADE（CAD カーネル）を使ってソリッドモデルを構築するため、出力される STEP には B-rep（面・エッジの数学的定義）が保持されます。**これが後の編集可能性の源泉**です。

### 実行結果

```
STEP保存完了: robot_arm.step
パーツ数: 10
パーツ一覧: ['base', 'swivel', 'shoulder_joint', 'upper_arm',
             'elbow_joint', 'forearm', 'wrist_j4', 'wrist_j5',
             'wrist_j6', 'flange']
エンドエフェクタ先端: (28.2, 0.0, 1156.8) mm
ファイルサイズ: 108.8 KB
```

10 個の名前付きパーツを持つ STEP ファイルが生成されました。

![](https://static.zenn.studio/user-upload/7ac19148b448-20260416.png)  
【画像】STEP版ロボットアーム 4面ビュー

---

## FreeCAD での確認・編集

ここが今回の核心です。生成した STEP ファイルを FreeCAD で開き、CAD ソフトとしての操作を行います。

### FreeCAD GUI での読み込み

まず、FreeCAD の GUI で STEP ファイルを開きます。

![](https://static.zenn.studio/user-upload/4f80068c8f90-20260416.png)  
【画像】FreeCAD GUI で STEP を開いた画面

左パネルのモデルツリーに 10 パーツ（base, swivel, shoulder\_joint, upper\_arm, elbow\_joint, forearm, wrist\_j4/j5/j6, flange）が名前付きで表示されています。パーツをクリックすると個別に選択でき（画像では forearm が水色にハイライト）、右パネルには「フィレット」「面取り」などの CAD 編集ツールが並んでいます。

STL ファイルを FreeCAD で開いた場合、モデルツリーには単一のメッシュオブジェクトが表示されるだけで、パーツ単位の選択や B-rep ベースの編集ツールは使えません。**この違いが STEP の価値**です。

### FreeCAD Python API による編集操作

GUI での対話的な編集に加え、FreeCAD の Python API（FreeCADCmd）を使ったスクリプトベースの編集も可能です。**今回はブログ用の再現性を確保するため、Python API で編集操作を実行**しました。

#### 編集操作 1：フィレットの追加

上腕リンク（upper\_arm）の長辺エッジに R5mm のフィレットを追加します。

```
# FreeCAD Python API でフィレット追加
edges = shape.Edges
fillet_edges = [e for e in edges if e.Length > 400]  # 長辺を選択
filleted = shape.makeFillet(5.0, fillet_edges)
```

STL はメッシュ（三角形の集まり）なので、「このエッジにフィレットを追加」という B-rep ベースの操作は実用的に困難です。STEP は面・エッジのトポロジーを保持しているため、エッジを選択して精密にフィレットを適用できます。

#### 編集操作 2：穴の追加

ロボットアーム先端のツールフランジ（エンドエフェクタ取付面）の中心に、直径 16mm の貫通穴を追加します。元々ボルト穴が6個ある部品です。

```
# FreeCAD Python API で穴追加
center_hole = Part.makeCylinder(8, 17, ...)
new_shape = shape.cut(center_hole)  # ブーリアン演算（差）
```

```
編集前 体積: 44,214 mm³
中心穴追加完了: 直径16mm
編集後 体積: 42,532 mm³
```

体積が減少していることから、穴が正しく開いたことが確認できます。

![](https://static.zenn.studio/user-upload/cca27b6747b6-20260416.png)  
【画像】編集後 — 等角図（フィレット + 穴追加）

### 編集後のエクスポート

編集後のモデルを STEP と STL の両方でエクスポートします。

```
STEP保存: robot_arm_edited.step (102.5 KB)
STL保存:  robot_arm_edited.stl  (177.8 KB)
```

編集後も STEP 形式で保存できるため、さらに別の CAD ソフトで開いて追加編集することも可能です。ただし、STEP を経由するたびにパラメトリックな設計履歴は保持されない（前述の「ダムソリッド」問題）ため、最終的な詳細設計はネイティブ CAD 形式で行うのが一般的です。

---

## STL 版との比較

![](https://static.zenn.studio/user-upload/d25d621ba9b6-20260416.png)  
【画像】STL版 vs STEP版 比較

|  | STL版（前回） | STEP版（今回） |
| --- | --- | --- |
| ファイルサイズ | 60.6 KB | 108.8 KB |
| 三角形数 | 1,240 | 3,640（STL変換後） |
| パーツ情報 | なし（全パーツを1メッシュに結合） | 10パーツ（名前・体積・表面積付き） |
| フィレット追加 | メッシュ編集ソフトで近似的に可能だが精度に限界 | B-repベースで精密に追加 |
| 穴追加 | ブーリアン演算は可能だがメッシュ品質が劣化しやすい | ブーリアン演算で正確に追加 |
| CADソフトでの編集 | メッシュとしての編集のみ | FreeCAD でフィーチャー追加を確認済み |
| 生成ライブラリ | numpy-stl（pip一発） | CadQuery（conda必要） |

三角形数の違いは、STEP から STL に変換する際のテッセレーション（メッシュ分割）設定の違いによるものです。STEP ファイル自体には三角形は含まれず、曲面は数学的な定義（NURBS 等）で保持されています。

---

## 考察

### 設計プロセスにおける位置づけ

```
[形状探索・コンセプト検討]  →  [詳細設計]  →  [製造図面]  →  [製造]
 ↑ 前回（STL）                ↑ 今回（STEP）
 見るだけ                     CADソフトで編集の起点にできる
```

前回の STL 出力は「形状探索」フェーズまでのカバーでした。今回の STEP 出力により、AI が生成したモデルを CAD ソフトにインポートし、フィーチャーの追加やブーリアン演算といった編集の起点にできるところまで到達しました。

ただし、STEP で開けば何でも自由に編集できるわけではありません。今回実証したのは「フィレットを付ける」「穴を開ける」といった **新しい加工の追加** です。一方、「既にある穴の直径を 10mm から 12mm に変える」操作は簡単にはできません。STEP には「ここに直径 10mm の穴を開けた」という設計手順が記録されていないため、CAD ソフトから見ると「たまたまこの形をしている塊」でしかないからです。穴の直径を変えたければ、一度穴を埋めてから 12mm で開け直す、といった回りくどい手順になります。

SolidWorks のネイティブ形式（.sldprt）なら「穴あけ: 直径 10mm」というフィーチャーが設計履歴として残っているので、10 を 12 に書き換えるだけで済みます。STEP にはそれがない。これが業界で「ダムソリッド（dumb solid）」と呼ばれる理由です。

つまり、AI が生成した STEP モデルは「形状の出発点」として活用し、そこから人間が CAD ソフト上で詳細設計を進めるワークフローが現実的です。

### 既存 CAD ソフトへの組み込み

今回の手法を既存の CAD ワークフローに組み込むには、3 つのアプローチが考えられます：

1. **STEP インポート方式**（今回実証）: Kiro → CadQuery → STEP → CAD ソフトにインポート
2. **API コード生成方式**: Kiro に対象 CAD ソフトの API コードを書かせて直接実行
3. **MCP 連携方式**: CAD ソフトの MCP サーバーを構築し、Kiro から直接操作

MCP（Model Context Protocol）は AI アシスタントが外部ツールと連携するための標準プロトコルで、Kiro も対応しています。CAD ソフトの MCP サーバーが実現すれば、「フランジに直径 20mm の穴を追加して」→ 結果を確認 →「穴の位置を中心から X 方向に 10mm オフセットして」といった対話的な設計操作が可能になります。現時点で MCP 対応の CAD ソフトはほぼありませんが、FreeCAD のように Python API が充実したソフトであれば、MCP サーバーの自作は技術的に可能です。

---

## まとめ

本記事では、前回の STL 出力から一歩進み、以下を実証しました：

* **Kiro + CadQuery で STEP 形式の 3D モデルを生成**（10 パーツ、108.8KB）
* **FreeCAD で STEP を読み込み、パーツ単位での選択・編集が可能なことを GUI で確認**
* **FreeCAD Python API でフィレット追加・穴追加の編集操作を実行**
* **編集後のモデルを STEP/STL で再エクスポート**

AI が生成した 3D モデルが「見るだけ」の STL から「CAD ソフトで編集の起点にできる」STEP になることで、実際の CAD ワークフローへの接続が可能になります。生成された STEP はパラメトリック履歴を持たない「ダムソリッド」ではありますが、形状の出発点として CAD ソフトに取り込み、そこから人間が詳細設計を進めるワークフローは十分に実用的です。

続編として、この STEP モデルに Kiro で構造解析（CAE）を実行する記事を公開しました。AI が編集した形状が実際に強度・剛性の要件を満たすかまでを一気通貫で検証しています。  
👉 [AI が設計して、AI が強度検証する — Kiro × FreeCAD FEM でロボットアーム CAE 構造解析](https://zenn.dev/aws_japan/articles/a5cd987ecb59ff)
