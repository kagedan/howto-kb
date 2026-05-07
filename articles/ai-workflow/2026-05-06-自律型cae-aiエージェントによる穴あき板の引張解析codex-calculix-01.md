---
id: "2026-05-06-自律型cae-aiエージェントによる穴あき板の引張解析codex-calculix-01"
title: "自律型CAE AIエージェントによる穴あき板の引張解析：Codex + CalculiX"
url: "https://zenn.dev/ms_ai/articles/a721a5a11c5602"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "GPT", "Python", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

# Codex AppでCAE解析を実行

Codexはコーディングのためのツールというイメージがあると思いますが、適切なツールと組み合わせることでCAE解析も実施できます。形状作成→材料・境界条件設定→解析実行→結果評価→レポート作成まで一連の流れをCodexで自然言語による対話だけで実施してみます。

以下の環境が構築されていることを前提とします。  
<https://zenn.dev/ms_ai/articles/f77f8d250ece77>

## 問題設定

穴あき平板の引張解析という、構造解析でのHello World的な超簡単解析をAIエージェント**Codex App**で実行してみます。  
解析手順は教えていない状態でどこまでできるか確認してみます。穴あき平板の解析方法自体は広く知られており、どの要素タイプを使うかもよく知られているのでAIが持つネイティブの知識で十分対応できると予想しています。  
一方でCAEツールの取り扱いはややマイナーな部類なので、システムトラブルを乗り越えられるかが鍵になります。

## 使用するもの

* Codex App + GPT5.5 （AIエージェント）
* CalculiX （CAEソルバー）
* Gmsh （メッシュ作成用）
* meshio （メッシュ変換用）
* build123 （ジオメトリ作成用）

## AGENTS.md

プロジェクトディレクトリの構成や実行方法を教えておかないと無駄なトライ＆エラーが多発してトークンを無駄にしてしまうため、最低限の情報を記載しておきます。

```
# AGENTS.md

## Project

This repository is a Windows-native CAE AI workspace using CalculiX.

Main purpose:
- Create, run, and review structural FEM analyses.
- Use text-based workflows: Python scripts, CalculiX `.inp/.inc`, CSV, Markdown reports.

## Environment

CalculiX:
- Target solver: CalculiX 2.23 for Windows.
- Before running CalculiX commands, initialize the environment with:

```cmd
call C:\CAEtools\CalculiX-2.23.0\etc\CalculiXWindowsEnvironment.bat
````

Run solver:

```cmd
ccx jobname
```

Do not run:

```cmd
ccx jobname.inp
```

## Available tools

Python:

* Use project venv: `.venv`
* Main packages: numpy, scipy, pandas, pyyaml, jinja2, matplotlib, gmsh, meshio, build123d, rich, typer, pytest, ruff.

CAE tools:

* CalculiX `ccx`: solver.
* CalculiX `cgx`: optional pre/post viewer.
* Gmsh Python API: mesh generation.
* meshio: mesh conversion.
* build123d: simple CAD/helper geometry generation.

## Directory layout

Use this structure for analysis cases:

```text
cases/
  case_xxx/
    analysis.md
    geometry/
    scripts/
    input/
      main.inp
      mesh.inc
      materials.inc
      sections.inc
      bcs.inc
      loads.inc
      step.inc
      output.inc
    results/
    report/
      report.md
      figures/
```

## Rules
- Create analysis.md for record analysis plan and overview.
- Keep analysis inputs reproducible and text-based.
- Prefer .inp/.inc files over hidden GUI operations.
- Put generated solver outputs under results/.
- Write reports in Markdown.
- Use reference/ only for local manuals/README files; do not modify it unless asked.
```

## プロンプト

CodexをPlanモードに設定し、以下のようなプロンプトで解析計画を作ってもらいます。

プロンプト

```
以下の穴あき板の引張解析を実施したい。 
まずは計画を作り報告すること。不明点があれば確認。 

# 要件
板の大きさ：(X,Y)=(0,0)と(300,200)を対角線とする長方形とする。
板の厚さ：1mm
穴の直径：50mm
穴の位置：板の中央
材料：ヤング率＝210000MPa,ポアソン比＝0.3
固定条件：X=0の位置X方向変位拘束。(X,Y)=(0,0)の位置を全変位固定。
荷重条件：X=300の位置にX方向に10Nを分布荷重として負荷。

# Output
- X軸方向応力の最大値
- X軸方向応力の分布図(pngファイル）
- 日本語の解析結果報告書
```

#### （補足）CodexのPlanモード

Planモードに設定するとCodex がコンテキストを収集し、強固なプランを作ってくれます。難しいプランの場合に推奨されます。  
![](https://static.zenn.studio/user-upload/c76b1fceea7c-20260506.png)

### プラン作成時のCodexからの確認事項

Codexからいくつか質問されるので回答します。

まずモデル化方法について。寸法的には2D平面応力でよさそうですが、今回は「両方比較」を選んでみました。  
![](https://static.zenn.studio/user-upload/fc5aa113b44b-20260506.png)

メッシュ方針を聞いてきたので、今回は「収束確認あり」を選んでみました。  
![](https://static.zenn.studio/user-upload/3da285d42e3c-20260506.png)

### Codexのプラン

以下のようなプランを作ってくれました。  
![](https://static.zenn.studio/user-upload/42583272eaf5-20260506.png)  
![](https://static.zenn.studio/user-upload/8d627b51de7c-20260506.png)  
![](https://static.zenn.studio/user-upload/a69738617c0f-20260506.png)  
![](https://static.zenn.studio/user-upload/759faab0b1e9-20260506.png)  
最後の.venvの扱いだけ気になりますが、ほかは特に問題なさそうなので、そのまま計画を実行してもらいます。

## 解析実行（1回目）

### Codexのアウトプット

実行すると5分ほどで終了しました。最大応力と分布図をレポートしてくれます。ざっと見たところ、無事解析できているようです。  
![](https://static.zenn.studio/user-upload/4e590cd7dd61-20260506.png)

### （補足）Python実行環境について

.venvの扱いについてCodexに確認したところ、実行に使った Python 本体だけを Codex bundled Pythonにして、モジュール検索パス sys.path に既存のプロジェクト内パッケージ置き場`~\CAEagent_calculix\.venv\Lib\site-packages`を追加して読み込ませた、ということでした。  
Codex のWindowsローカル実行では、ネイティブ Windows sandbox環境で実行されるため、このような仕組みにしたようです。ただ、これはうまくいかないこともあるので`.\.venv\Scripts\python.exe script.py`を明示的に指定したほうが無難です。今後のために`AGENTS.md`に記載しておきます。

### 結果レポート

作成されたレポートを見てみます。  
![](https://static.zenn.studio/user-upload/f709bb02d0dc-20260506.png)  
![](https://static.zenn.studio/user-upload/f8bda3a3c70b-20260506.png)  
![](https://static.zenn.studio/user-upload/8f04f4968371-20260506.png)  
特に依頼していなかったのですが、3D解析のほうは穴周辺の分布を拡大表示してくれています。  
ざっと見たところでは問題なさそうですが、解析の詳細が書かれていないので確認してみます。

## 解析結果（1回目）レビュー

今回の解析がどのようにして行われているのか確認してみます。

### 手動でレビュー

まず手動でレビューしてみます。

#### ファイル構成

inputフォルダのファイル構成は次の通り。  
![](https://static.zenn.studio/user-upload/67a63cf986fc-20260506.png)

#### メインのインプットファイル

各種`.inc`ファイルをINCLUDEしてますね。

hole\_plate\_2d\_medium/main.inc

```
*HEADING
Hole plate tension, 2d, medium
*INCLUDE, INPUT=mesh.inc
*INCLUDE, INPUT=materials.inc
*INCLUDE, INPUT=sections.inc
*INCLUDE, INPUT=step.inc
```

そして`step.inc`でさらに境界条件関連の`.inc`ファイルをINCLUDEする形です。

hole\_plate\_2d\_medium/step.inc

```
*STEP
*STATIC
*INCLUDE, INPUT=bcs.inc
*INCLUDE, INPUT=loads.inc
*INCLUDE, INPUT=output.inc
*END STEP
```

#### メッシュ

INCLUDEしている`mesh.inc`を見てみます。ここでは`CPS3`つまり3節点の二次元平面応力要素を使っていますね。これは一次要素なのでちょっと固くなりやすい傾向があるはず。  
最後にNSETを作成しています。

hole\_plate\_2d\_medium/mesh.inc

```
*NODE
1, 0, 0, 0
2, 300, 0, 0
3, 300, 200, 0
4, 0, 200, 0
（中略）
*ELEMENT, TYPE=CPS3, ELSET=EALL
1, 269, 1329, 1606
2, 1093, 1391, 1494
3, 1391, 1154, 1494
4, 1379, 1507, 1823
（中略）
*NSET, NSET=LEFT_X
1,4,107,108,109,110,111,112,113,114,115,116,117,118,119,120
121,122,123,124,125,126,127,128,129,130
*NSET, NSET=ORIGIN_FIX
1
*NSET, NSET=RIGHT_LOAD
2,3,46,47,48,49,50,51,52,53,54,55,56,57,58,59
60,61,62,63,64,65,66,67,68,69
```

<https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node46.html>

これだけだとよくわからないので、CGXで図を表示します。穴の付近だけメッシュを細かくしてますが、特に指示していないのでAIが自律的に判断・実装した結果です。  
![ole_plate_2d_medium.frd](https://static.zenn.studio/user-upload/715c2d48eb54-20260506.png)

なお、3Dのほうは`C3D4`なので4節点テトラ要素を使用していました。

hole\_plate\_3d\_medium/mesh.inc

```
（前略）
*ELEMENT, TYPE=C3D4, ELSET=EALL
1, 197, 231, 232, 700
2, 699, 665, 700, 197
3, 699, 197, 700, 231
（後略）
```

#### 境界条件

分布荷重は節点に直接力荷重として与えているようです。両端は1/2にしており妥当な設定と思われます。

hole\_plate\_2d\_medium/load.inc

```
*CLOAD
2, 1, 0.199999999999
3, 1, 0.200000000001
46, 1, 0.399999999998
47, 1, 0.399999999999
（後略）
```

変位拘束も特に問題なし。

hole\_plate\_2d\_medium/bcs.inc

```
*BOUNDARY
LEFT_X, 1, 1, 0.0
ORIGIN_FIX, 1, 2, 0.0
```

#### 解析結果

CGXでSXXをプロットしてみると、応力の出方は特に問題なさそうです。MAX応力値も材料力学で得られる値に近いです。  
![](https://static.zenn.studio/user-upload/8426d10e7923-20260506.png)

一方、MAXが1.54e-001と出ているのはレポートにあった数値0.167582とは異なります。この理由についてCodexに確認してみます。

プロンプト

```
レポートでみるとMAXのSXXは2d mediumで0.167582だが、cgxでプロットするとMAXのSXXは1.54e-1であった。なぜこのような違いが生じるのか？
```

Codexの回答は以下の通り。  
![](https://static.zenn.studio/user-upload/055a9d1b0055-20260506.png)  
![](https://static.zenn.studio/user-upload/fbf3b64d35a0-20260506.png)  
CAEツールではよくある積分点・外挿問題でした。  
CAE業務ではポスト処理ツール（CGX）で出しているほうの値を使うことが多いと思いますが、積分点の値と両方併記しておくのもよさそうです。

#### 手動でレビューのまとめ

手動でレビューしてみた結果は以下の通り。

* 解析の計画は良い。メッシュサイズを変えた検証や2D/3Dとの比較もなされている。
* 選択している要素タイプは再検討の余地あり。一次要素の三角形やテトラ要素は固くなりすぎる傾向があるため。（リファレンスにもそのように記載されている）
* 応力結果は積分点の値をそのまま出すか節点で平均した値を出すかは指示が必要。

### AI自身にレビューさせる

解析結果をAI自身にレビューさせてみます。

すると、先ほど手動でレビューして気づいた点を指摘してくれました。  
![](https://static.zenn.studio/user-upload/8b1d7f90ca92-20260506.png)  
![](https://static.zenn.studio/user-upload/725c6a8331be-20260506.png)

## 解析実行（2回目）

このレビュー結果をもとに再度解析してもらいます。

プロンプト

```
このレビュー結果をもとに再度解析して。先ほどの結果を上書きしないようにフォルダを分けること。
```

### 解析結果（2回目）

レポートを見てみると、2Dのほうは二次要素で解析してくれたことが分かります。  
積分点と節点平均解の違いについてもレポートしていますね。  
![](https://static.zenn.studio/user-upload/79f027ec4ff6-20260506.png)  
![](https://static.zenn.studio/user-upload/861f5d3853f0-20260506.png)  
![](https://static.zenn.studio/user-upload/fda261531732-20260506.png)

### 補足：境界条件（2回目）

二次要素で解析しているので、どのように分布荷重を与えているか気になって調べてみると、中間節点かどうかを判別して荷重設定を変え、等価節点荷重になるように実装していました。

```
def quadratic_line_loads(points: np.ndarray, elements: np.ndarray) -> dict[int, float]:
    tol = 1.0e-6
    loads: dict[int, float] = {}
    edges = ((0, 1, 3), (1, 2, 4), (2, 0, 5))
    for elem in elements:
        for a, b, m in edges:
            ids = [int(elem[a]) + 1, int(elem[b]) + 1, int(elem[m]) + 1]
            if all(np.isclose(points[nid - 1, 0], WIDTH, atol=tol) for nid in ids):
                length = abs(points[ids[0] - 1, 1] - points[ids[1] - 1, 1])
                loads[ids[0]] = loads.get(ids[0], 0.0) + length / 6.0
                loads[ids[1]] = loads.get(ids[1], 0.0) + length / 6.0
                loads[ids[2]] = loads.get(ids[2], 0.0) + 2.0 * length / 3.0
    if not loads:
        raise RuntimeError("No quadratic right boundary edges found")
    scale = TOTAL_LOAD / sum(loads.values())
    return {nid: force * scale for nid, force in loads.items()}
```

## まとめ

簡単な題材でしたが、自然言語による指示だけでCAE解析を行うことができました。適切な作業環境を用意してあげれば、特に工夫していない素のAIでも一通りの作業はできるようです。  
1回目の解析では少し見直しが必要なところもありましたが、AI自身にレビューさせることで問題点を見つけて改善させることができました。レポートもAIに作らせることができます。

### 学習コストが低いのが最大のメリット

CAEツールはFEM解析自体のテクニック（メッシュ粗密や要素タイプ選択など）が複雑なうえに、インプットファイルの書式もソルバーごとに異なり、リファレンスと突き合わせてみないと内容が理解しづらいです。CAEに慣れていてもツールが変わるとすぐに理解するのが難しく、学習コストが高いと感じています。

今回のようにAIエージェントを介してCAEツールを動かすことで、

* リファレンスを見なくてもAIと自然言語でやり取りするだけでCAEツールを動かせる
* 解析テクニックに詳しくなくてもAIが自動的に実装してくれる  
  といったメリットがあり、学習コストを著しく下げることができると感じています。

一方でAIの出してきたアウトプットをそのまま使うことの危険性も見えたので、少なくとも1回はAI自身にレビューさせる、最終的な結果は自分の目で確認する、といった工夫も必要だと思いました。
