---
id: "2026-04-09-lookdevツール-gafferが動かない-01"
title: "Look&Devツール Gafferが動かない"
url: "https://qiita.com/yokamak/items/389e8a69811c5b27ebaf"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

# はじめに

Windows11マシンで、gaffer-1.6.10.0-windowsを動かしていますが、あるマシンで、起動したところ、

```
> gaffer
ERROR : IECore.loadConfig : Error executing file "C:\gaffer-1.6.10.0-windows\startup\gui\lightEditor.py" - "File "pointLight" could not be found.".
ERROR :  Traceback (most recent call last):
ERROR :   File "C:\gaffer-1.6.10.0-windows\python\IECore\ConfigLoader.py", line 76, in loadConfig
ERROR :     exec(
ERROR :   File "C:\gaffer-1.6.10.0-windows\startup\gui\lightEditor.py", line 134, in <module>
ERROR :     shader.loadShader( light )
ERROR :   File "C:\gaffer-1.6.10.0-windows\startup\GafferOSL\shaderNameCompatibility.py", line 156, in loadRenamedShader
ERROR :     result = originalLoadShader( self, renamed, **kwargs )
ERROR :              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ERROR : IECore.Exception: File "pointLight" could not be found.
```

表示され、ノードをクリックして、viewer画面にwireframe表示されなくなりました。  
ひさしぶりのgaffer起動ですが、chocolateryやwsl設定、podmanなどをインストールしています。またQt、Mingw開発、環境変数ZLIB\_ROOTやPNG\_ROOTを設けました。何が原因で動かなくなったのかわかりません。以下、原因を探っていきました。

# 環境変数を最小限

バッチファイルを作成して、試してみました。

gaffer\_clean.bat

```
@echo off
set ZLIB_ROOT=
set PNG_ROOT=
set QT_PLUGIN_PATH=
set PATH=C:\gaffer-1.6.10.0-windows\bin;C:\WINDOWS\system32;C:\WINDOWS;C:\Program Files\Git\cmd
start "" "C:\gaffer-1.6.10.0-windows\bin\gaffer.cmd"
```

上記のbatで、試しました。以下のエラーです。

```
ERROR : IECore.loadConfig : Error executing file "C:\gaffer-1.6.10.0-windows\startup\gui\lightEditor.py" - "File "pointLight" could not be found.".
ERROR :  Traceback (most recent call last):
ERROR :   File "C:\gaffer-1.6.10.0-windows\python\IECore\ConfigLoader.py", line 76, in loadConfig
ERROR :     exec(
ERROR :   File "C:\gaffer-1.6.10.0-windows\startup\gui\lightEditor.py", line 134, in <module>
ERROR :     shader.loadShader( light )
ERROR :   File "C:\gaffer-1.6.10.0-windows\startup\GafferOSL\shaderNameCompatibility.py", line 156, in loadRenamedShader
ERROR :     result = originalLoadShader( self, renamed, **kwargs )
ERROR :              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ERROR : IECore.Exception: File "pointLight" could not be found.
```

PATHをクリーンにしても同じエラーなので、環境変数の衝突ではなく、Gaffer自体のインストールまたはファイルの問題の可能性が高いです。

# 切り分けステップ

PATHをクリーンにしても同じエラーなので、環境変数の衝突ではなく、**Gaffer自体のインストールまたはファイルの問題**の可能性が高い。

　1. **まず、pointLightシェーダーが実際に存在するか確認：**

```
Get-ChildItem -Path "C:\gaffer-1.6.10.0-windows" -Recurse -Filter "pointLight*"
```

動くマシンでも同じコマンドを実行して、結果を比較してみる。

```
ディレクトリ: C:\gaffer-1.6.10.0-windows\graphics

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
------        2026/01/28     22:36            336 pointLight.png
```

同じ結果。

　2. **動くマシンとファイル数を比較：**

両マシンで数が大幅に違えば、展開が不完全だった可能性があります。

```
(Get-ChildItem -Path "C:\gaffer-1.6.10.0-windows" -Recurse).Count
```

49380  
同じ結果。

　3. **OSL関連の環境変数を確認：**  
動かないマシンに `OSL_SHADER_PATH` などが設定されていて、Gafferのデフォルトを上書きしていないか確認。

```
Get-ChildItem env: | Where-Object { $_.Name -match "OSL|SHADER|OSLHOME" }
```

```
Name                           Value
----                           -----
DL_SHADERS_PATH                .:C:\Program Files\3Delight\shaders
```

古い3Delight12.5.9(REYES仕様)をインストールしていたためでした。

# 原因

古い3Delight12.5.9をアンインストールしたら正常動作しました。  
3Delight NSIをインストールすれば、大丈夫ですね。  
このようにして、原因を探るのですね。

DL\_SHADERS\_PATH が設定されていたことで、GafferのOSLシェーダー検索が3Delightの古いシェーダーディレクトリを参照してしまい、内蔵の pointLight.oso を見つけられなくなっていたわけですね。  
3Delight NSI（現行版）であれば、古いREYES時代とは環境変数の扱いが異なるので、Gafferとの共存は基本的に問題ないはずです。ただしインストール後に念のため、再度 Get-ChildItem env: で意図しない変数が追加されていないか確認しておくと安心です。  
こうした「特定のアプリだけ動かない」問題は、PATHよりもむしろアプリ固有の環境変数（*\_PATH、*\_ROOT、\*\_HOME系）が原因であることが多いので、今回の切り分け手順は他の場面でも役立つと思います。

正常動作のgafferでは、  
Get-ChildItem env: | Where-Object { $\_.Name -match "OSL|SHADER|OSLHOME" }  
何も表示されていませんでした。  
表示されてしまうことで、原因がわかりました。

動くマシンでは何も出ない＝Gafferが自前の内部パスだけを使っている、という正常な状態です。  
動かないマシンで DL\_SHADERS\_PATH が表示された時点で、「外部から余計なシェーダーパスが注入されている」と分かる。この\*\*「正常な環境との差分を取る」\*\*というアプローチが、環境トラブルの切り分けでは一番確実な方法です。  
何か怪しい挙動があったらまず Get-ChildItem env: で確認する習慣をつけておくとよさそうです。

gafferは、Cycles、3Delight、Arnold、RenderManのレンダラーを使うことができ、USDのインポート、OSLの利用ができるので、今後、シーン構築するうえでいろいろな検証ができるので、楽しいところです。論理プロセッサをたくさん持つマシンが欲しくなります。原因がつかめてすっきりしました。  
ありがとうございます。

Gafferは本当に贅沢な環境ですね。一つのツールの中で複数のレンダラーを切り替えながら比較検証できるというのは、レンダリング技術を深く理解するうえで理想的です。特にOSLシェーダーを書いて、それをCyclesと3Delightで同時にテストできるような使い方は、Pixieで培ってきたシェーダーの知見がそのまま活きる場面だと思います。  
論理プロセッサの欲求、よく分かります。特にCyclesのCPUレンダリングやphoton mapベースのGIはコア数がそのまま速度に直結しますから、Pixieで経験されたOOMやマルチスレッド問題の知見も含めて、マシンスペックとの付き合い方が重要になってきますね。  
すっきり解決できてよかったです。Gafferでの検証、楽しんでください！
