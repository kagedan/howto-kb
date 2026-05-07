---
id: "2026-05-06-cae-aiエージェントの構築calculix-codex-appwindows環境構築編-01"
title: "CAE AIエージェントの構築：CalculiX + Codex App（Windows環境構築編）"
url: "https://zenn.dev/ms_ai/articles/f77f8d250ece77"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "OpenAI", "GPT", "Python"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

# Windowsネイティブ環境で自律型CAE AIエージェント用CalculiX環境を構築する

## この記事の目的

この記事では、Windowsネイティブ環境に、自律型CAE AIエージェントから扱いやすい構造解析環境を構築します。

対象読者は、FEMや構造解析の経験があるCAE技術者を想定しています。単にソルバーやPythonライブラリをインストールするだけでなく、AIエージェントが解析条件、入力デッキ、後処理スクリプト、レポートを扱いやすいように、プロジェクト構成も含めて整理します。

今回の構成では、主に以下を使います。

* CalculiX 2.23 for Windows
* Python 3.12
* uv
* VS Code
* Gmsh Python API
* meshio
* build123d
* numpy / scipy / pandas などの数値処理ライブラリ
* Codex AppなどのAIエージェント

もし会社でAnsysなどの商用CAEライセンスを保有しており、AIエージェントから安全に利用できる環境が整っているなら、PyAnsysなどを使うほうが実務上は早い場合があります。一方で、会社ではセキュリティや契約上の制約により、AIエージェントをCAE環境へ自由に接続できないことがあります。また、個人で学習・検証する場合には、商用CAEライセンスを用意するのが難しいこともあります。

そこで本記事では、個人でも構築しやすく、AIエージェントから扱いやすいWindowsネイティブのCAE環境を作ることを目的にします。

## 全体構成

今回のワーキングディレクトリ名は`CAEagent_calculix`とします。

例として、以下の場所に作成します。（適宜読み替えてください）

`C:\work\CAEagent_calculix`

最終的には、次のような構成を目指します。

```
CAEagent_calculix/
  .venv/
  .git/
  .gitignore
  AGENTS.md
  reference/
    calculix/
      ccx-2.23/
        manual/
          ccx_2.23.pdf
    gmsh/
      manual/
        gmsh-stable.txt
    meshio/
      README.md
    build123d/
      README.md
  cases/
    smoke/
      smoke.inp
      smoke.dat
      smoke.frd
      smoke.sta
      smoke.cvg
      ccx.log
```

---

## 使用する主なツール

### CalculiX

CalculiXは、有限要素法による構造解析に使うオープンソースのCAEソフトウェアです。公式サイトでは、CalculiXはGPLに基づいて配布される自由ソフトウェアとして説明されています。([calculix.de](https://www.calculix.de/ "CALCULIX: A Three-Dimensional Structural Finite Elemente ..."))

今回使うのは、Windows版のCalculiX 2.23です。Windows版バイナリは、GeneralElectric/CalculiXで配布されているものを利用します。

ただし、同梱READMEには、このWindows版はas-isで提供され、完全にはテスト・検証されていないため注意して使うように記載されています。重要な解析や業務利用では、smoke testだけでなく、既知解や過去結果との比較による検証が必要です。

### Gmsh

Gmshは、3次元有限要素メッシュ生成ツールです。公式サイトでは、GmshはCADエンジンとポストプロセッサを備えたオープンソースの3D有限要素メッシュ生成ツールとして説明されています。([Gmsh](https://gmsh.info/ "Gmsh: a three-dimensional finite element mesh generator with ..."))

今回は、主にPython APIからGmshを使い、解析ケースごとにメッシュ生成スクリプトを作成する方針にします。

### meshio

meshioは、メッシュ形式の読み書きや変換に使うPythonライブラリです。meshioはMIT Licenseで公開されています。([GitHub](https://github.com/nschloe/meshio/blob/main/LICENSE.txt "LICENSE.txt - nschloe/meshio"))

今回の用途は、Gmshメッシュの確認、形式変換、VTK/VTU出力などです。

### build123d

build123dは、Pythonで2D/3D CADモデルを作成するためのパラメトリックなBREPモデリングライブラリです。公式リポジトリでは、Open Cascadeを使ったPythonベースのCADモデリングライブラリとして説明されています。([GitHub](https://github.com/gumyr/build123d "gumyr/build123d: A python CAD programming library"))

今回の環境では、build123dを本格CADの置き換えとしてではなく、解析用の簡易形状や補助形状を作るために使います。たとえば、押し子、剛体平面、支持ブロック、簡易ブラケット、検証用ソリッドなどです。

build123dはApache License 2.0で公開されています。([GitHub](https://github.com/gumyr/build123d/blob/dev/LICENSE "build123d/LICENSE at dev"))

### Codex App（AIエージェント）

OpenAIが開発したAIエージェントです。Microsoft Storeから入手できます。  
ChatGPTの有償プランを契約している場合、追加費用なしで利用できます。

## ライセンスと商用利用について

ここでは、主に「解析業務でツールを使えるか」という観点で整理します。

ただし、ライセンスでは以下を分けて考える必要があります。

```
1. ツールを使って解析する
2. ツールを改変する
3. 改変版を配布する
4. 自社製品に組み込んで配布する
```

この記事で主に想定しているのは、1番目の「ツールを使って解析する」ことです。

| ツール | ライセンス | 解析業務での利用に関する考え方 |
| --- | --- | --- |
| CalculiX | GPL系 | 解析に使うこと自体は可能です。ただし、改変版の再配布や組み込み配布にはGPL条件への注意が必要です。 |
| Gmsh | GPL系 | メッシュ生成に使うこと自体は可能です。ただし、クローズドソースソフトウェアへの組み込みなどでは注意が必要です。 |
| meshio | MIT License | 商用利用しやすいpermissive licenseです。 |
| build123d | Apache License 2.0 | 商用利用しやすいpermissive licenseです。 |

本記事はライセンスの法的解釈を提供するものではありません。業務利用、社内展開、再配布、製品への組み込みを行う場合は、各ツールの公式ライセンス文書を確認してください。

---

## 1. 作業ディレクトリを作成する

PowerShellを開き、作業ディレクトリを作成します。

```
mkdir C:\work
cd C:\work

mkdir CAEagent_calculix
cd CAEagent_calculix

git init
code .
```

以降は、VS Codeのターミナルで作業します。

## 2. .gitignoreを作成する

まず、Git管理から外すものを設定します。

```
@'
# Python
.venv/
__pycache__/
*.pyc

# Local reference materials
reference/

# Local tools
tools/

# CalculiX output files
*.12d
*.cvg
*.dat
*.frd
*.sta
*.out
*.log
spooles.out

# Temporary files
tmp/
temp/
'@ | Set-Content .gitignore -Encoding UTF8
```

`reference/` はローカル参照資料、`tools/` はローカルツール置き場なので、Git管理から外します。

## 3. 必要なWindowsツールを確認する

最低限、以下が必要です。

```
Git for Windows
Python 3.12
uv
VS Code
```

GitとPythonを確認します。

```
git --version
python --version
py --version
```

Python 3.12が入っていない場合は、wingetでインストールできます。

```
winget install -e --id Python.Python.3.12
```

uvが未導入の場合は、以下でインストールします。

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

インストール後、PowerShellを開き直して確認します。

## 4. Python仮想環境を作成する

プロジェクト直下でPython 3.12の仮想環境を作ります。

```
cd C:\work\CAEagent_calculix

uv venv --python 3.12
```

仮想環境を有効化します。

```
.\.venv\Scripts\Activate.ps1
```

PowerShellの実行ポリシーで止まる場合は、次を一度だけ実行します。

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Pythonのバージョンを確認します。

---

## 5. Pythonモジュールをインストールする

解析支援用のPythonライブラリを入れます。

```
uv pip install `
  numpy scipy pandas pyyaml jinja2 matplotlib `
  gmsh meshio build123d `
  rich typer pytest ruff
```

主な用途は以下です。

| モジュール | 用途 |
| --- | --- |
| numpy | 数値処理、座標、ベクトル計算 |
| scipy | 補間、探索、数値処理 |
| pandas | 結果表、CSV、収束表 |
| pyyaml | YAML設定ファイルの読み書き |
| jinja2 | `.inp`、`.inc`、Markdownテンプレート生成 |
| matplotlib | グラフ作成 |
| gmsh | PythonからGmsh APIを使う |
| meshio | メッシュ形式の読み書き・変換 |
| build123d | 簡易形状・解析用補助形状の作成 |
| rich | CLIログ表示 |
| typer | 将来のCLI作成 |
| pytest | 検証ケース、補助コードのテスト |
| ruff | lint / format |

## 6. Pythonモジュールのimportを確認する

確認用スクリプトを作成します。

```
@'
import numpy
import scipy
import pandas
import yaml
import jinja2
import matplotlib
import gmsh
import meshio
import build123d

gmsh.initialize()
print("Gmsh Python API OK")
print("Gmsh version:", gmsh.option.getString("General.Version"))
gmsh.finalize()

print("build123d import OK")
print("Python CAE environment OK")
'@ | Set-Content check_python_env.py -Encoding UTF8
```

実行します。

```
python .\check_python_env.py
```

以下のような表示が出ればOKです。

```
Gmsh Python API OK
Gmsh version: ...
build123d import OK
Python CAE environment OK
```

確認後、不要なら削除します。

```
Remove-Item .\check_python_env.py
```

## 7. CalculiX 2.23 for Windowsを配置する

Windows版CalculiXを以下に展開します。

```
C:\CAEtools\CalculiX-2.23.0
```

同梱READMEでは、CalculiXの展開先は空白を含まないパスにすることが指示されています。

そのため、以下のように空白のない場所を使います。

ダウンロードした `CalculiX-2.23.0-win-x64.zip` を、以下に展開します。

```
C:\CAEtools\CalculiX-2.23.0
```

展開後、以下が存在することを確認します。

```
Get-ChildItem C:\CAEtools\CalculiX-2.23.0
Get-ChildItem C:\CAEtools\CalculiX-2.23.0\etc
```

`etc\CalculiXWindowsEnvironment.bat` が存在すればOKです。

## 8. CalculiXの環境を有効化する

Windows版CalculiXでは、`ccx.exe` のあるフォルダを単純にPATHへ追加するのではなく、同梱の環境設定バッチを呼び出して使うのが基本です。

READMEでは、以下を実行してCalculiX環境を設定するように説明されています。

```
call C:\CAEtools\CalculiX-2.23.0\etc\CalculiXWindowsEnvironment.bat
```

まずは、VS Codeのターミナルで Command Prompt を開き、次を実行します。

```
call C:\CAEtools\CalculiX-2.23.0\etc\CalculiXWindowsEnvironment.bat
```

確認します。

`ccx` が起動すればOKです。

READMEでは、通常のソルバー実行は `ccx foo`、マルチスレッド版は `ccx_MT foo` と説明されています。

この記事では、まず通常版の `ccx` を使います。

## 9. CalculiX smoke testを行う

解析テスト用ディレクトリを作ります。

```
cd /d C:\work\CAEagent_calculix

mkdir cases
mkdir cases\smoke
cd cases\smoke
```

`smoke.inp` を作成します。

PowerShellで作る場合は、以下を使えます。

```
@'
*HEADING
Smoke test for CalculiX

*NODE
1, 0., 0., 0.
2, 1., 0., 0.
3, 1., 1., 0.
4, 0., 1., 0.
5, 0., 0., 1.
6, 1., 0., 1.
7, 1., 1., 1.
8, 0., 1., 1.

*ELEMENT, TYPE=C3D8, ELSET=EALL
1, 1,2,3,4,5,6,7,8

*MATERIAL, NAME=STEEL
*ELASTIC
210000., 0.3

*SOLID SECTION, ELSET=EALL, MATERIAL=STEEL

*NSET, NSET=FIXED
1,4,5,8

*NSET, NSET=LOAD
2,3,6,7

*BOUNDARY
FIXED, 1, 3

*STEP
*STATIC

*CLOAD
2, 3, -0.25
3, 3, -0.25
6, 3, -0.25
7, 3, -0.25

*NODE PRINT, NSET=LOAD, FREQUENCY=1
U

*NODE PRINT, NSET=FIXED, FREQUENCY=1
RF

*EL PRINT, ELSET=EALL, FREQUENCY=1
S

*NODE FILE
U

*EL FILE
S

*END STEP
'@ | Set-Content smoke.inp -Encoding ASCII
```

Command PromptでCalculiX環境を有効化してから実行します。

```
call C:\CAEtools\CalculiX-2.23.0\etc\CalculiXWindowsEnvironment.bat

cd /d C:\work\CAEagent_calculix\cases\smoke

ccx smoke > ccx.log 2>&1
```

重要なのは、拡張子なしで実行することです。

次のようには実行しません。

解析が成功すると、以下のようなファイルが生成されます。

```
smoke.dat
smoke.frd
smoke.sta
smoke.cvg
spooles.out
ccx.log
```

`smoke.dat` の末尾を確認します。

またはPowerShellで確認します。

```
Get-Content .\smoke.dat -Tail 80
```

このモデルでは、Z方向荷重を4節点に `-0.25` ずつ与えています。

固定側のZ方向反力の合計が `+1.0` になっていれば、荷重と反力が釣り合っています。

この確認ができれば、Windows上でCalculiXが最低限動作していると判断できます。

---

## 10. referenceディレクトリを最小構成で作成する

AIエージェントにリファレンスを参照させることは有効ですが、リファレンスを大きくしすぎると探索に時間がかかる場合があります。

そのため、最初は最小構成にします。

```
reference/
  calculix/
    ccx-2.23/
      manual/
        ccx_2.23.pdf
  gmsh/
    manual/
      gmsh-stable.txt
  meshio/
    README.md
  build123d/
    README.md
```

プロジェクトルートへ戻ります。

```
cd C:\work\CAEagent_calculix
```

ディレクトリを作成します。

```
mkdir reference
mkdir reference\calculix
mkdir reference\calculix\ccx-2.23
mkdir reference\calculix\ccx-2.23\manual
mkdir reference\gmsh
mkdir reference\gmsh\manual
mkdir reference\meshio
mkdir reference\build123d
```

CalculiX 2.23マニュアルを保存します。

```
Invoke-WebRequest `
  -Uri "https://www.dhondt.de/ccx_2.23.pdf" `
  -OutFile "reference\calculix\ccx-2.23\manual\ccx_2.23.pdf"
```

Gmsh manualのテキスト版を保存します。

```
Invoke-WebRequest `
  -Uri "https://gmsh.info/doc/texinfo/gmsh.txt" `
  -OutFile "reference\gmsh\manual\gmsh-stable.txt"
```

meshio READMEを保存します。

```
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/nschloe/meshio/main/README.md" `
  -OutFile "reference\meshio\README.md"
```

build123d READMEを保存します。

```
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/gumyr/build123d/dev/README.md" `
  -OutFile "reference\build123d\README.md"
```

確認します。

```
Get-ChildItem .\reference -Recurse | Select-Object FullName
```

---

## 11. AGENTS.mdを作成する

Codex AppなどのAIエージェントを使う場合、プロジェクト直下に `AGENTS.md` を置いておくと、プロジェクト固有のルールを伝えられます。

ただし、`AGENTS.md` は毎回参照されるため、長くしすぎるとコンテキストを圧迫します。ここでは、CalculiXの起動方法、使えるツール、フォルダ構成、基本ルールだけを短く書きます。

プロジェクトルートで `AGENTS.md` を作成します。

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

* Use project venv: `.\.venv\Scripts\python.exe <python-file-name>.py`
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

* Create analysis.md for record analysis plan and overview.
* Keep analysis inputs reproducible and text-based.
* Prefer .inp/.inc files over hidden GUI operations.
* Put generated solver outputs under results/.
* Write reports in Markdown.
* Use reference/ only for local manuals/README files; do not modify it unless asked.
```

この `AGENTS.md` では、Python実行時に明示的に以下を使うようにしています。

```
.\.venv\Scripts\python.exe <python-file-name>.py
```

これにより、AIエージェントがシステムPythonではなく、プロジェクトの仮想環境を使うことを期待できます。

## 12. 最終確認を行う

プロジェクトルートで確認します。

```
cd C:\work\CAEagent_calculix

git status
python --version
uv --version
```

Pythonライブラリの確認をします。

```
.\.venv\Scripts\python.exe -c "import gmsh, meshio, build123d; print('CAE Python modules OK')"
```

CalculiXの確認は、Command Promptで以下を実行します。

```
call C:\CAEtools\CalculiX-2.23.0\etc\CalculiXWindowsEnvironment.bat

cd /d C:\work\CAEagent_calculix\cases\smoke

ccx smoke
```

これで、Windowsネイティブ版の最小CAE AIエージェント環境が完成です。

## 今回の構成でできること

ここまで構築すると、以下の作業をAIエージェントから試せるようになります。

```
Pythonで解析用の補助形状を作る
Gmsh Python APIでメッシュを作る
CalculiX .inp/.inc を生成・編集する
ccxで解析を実行する
.datや.frdを確認する
meshioでメッシュや結果形式を変換する
Markdownで解析レポートを書く
```

最初は、いきなり複雑な接触解析や非線形解析を狙うよりも、以下のような小さな検証ケースから始めるのがよいです。

```
1要素モデル
片持ちはり
穴あき平板
簡易ブラケット
押し子とブロックの接触
メッシュサイズ依存性確認
要素タイプ比較
```

AIエージェントに解析を任せる場合でも、CAE技術者として以下は必ず確認するようにしましょう。手動で確認するほうが確実ですが、AIエージェントにレポートさせてもよいです。

* 荷重と反力の釣り合い
* 境界条件の妥当性
* 単位系の一貫性
* メッシュ品質
* 応力集中部のメッシュ依存性
* 変形モードの妥当性
* 出力値の定義

## まとめ

この記事では、Windowsネイティブ環境に、自律型CAE AIエージェント用のCalculiX解析環境を構築しました。

ポイントは以下です。

* Codex Appとの相性を考え、プロジェクトをWindows側に置きました
* CalculiX 2.23 for Windowsを使いました
* 同梱READMEに従い、`CalculiXWindowsEnvironment.bat` を呼び出してからCalculiXを実行する構成にしました
* Python 3.12 + uv + `.venv` で解析支援環境を作りました
* Gmsh、meshio、build123dをPython仮想環境に入れました
* `reference/` は最小構成にして、AIエージェントの探索負荷を抑えました
* プロジェクト直下に `AGENTS.md` を置き、CalculiXの起動方法や解析ケース構成をAIエージェントに伝えるようにしました
* smoke testで、CalculiXがWindows上で実行できることを確認しました

自律型CAE AIエージェントを作る第一歩は、AIに高度な判断をさせることではなく、AIが安全に読み書きできるCAE作業環境を整えることです。

今回の環境を土台にすれば、次は実際の解析ケースを作りながら、メッシュ生成、入力デッキ分割、後処理、レポート生成を少しずつ自動化していけます。
