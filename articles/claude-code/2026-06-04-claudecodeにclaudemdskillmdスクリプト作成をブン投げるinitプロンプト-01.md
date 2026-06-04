---
id: "2026-06-04-claudecodeにclaudemdskillmdスクリプト作成をブン投げるinitプロンプト-01"
title: "ClaudeCodeにCLAUDE.md・SKILL.md・スクリプト作成をブン投げる「initプロンプト」"
url: "https://qiita.com/Higemal/items/2d7afa6024d2f23b6482"
source: "qiita"
category: "claude-code"
tags: ["CLAUDE-md", "Python", "qiita"]
date_published: "2026-06-04"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

ClaudeCodeの利用に向けて、やれ `CLAUDE.mdの記述作法` やら `SKILL.mdの作成方法` みたいな内容はあるのですが、特に非プログラム開発用途において **「とりあえずAI側でCLAUDE.mdやSKILL.mdの初版は作ってくれ～～～」** という気持ちから、初期準備用の指示プロンプト＝ **initプロンプト** というのを考えてみました。

:::note warn
あくまで利用は個人の責任にて行ってください。
特にトークン消費量/課金量については最適化していません。
:::


# initプロンプト
ClaudeCodeで実現したい業務内容と、その業務内容を構成するタスク＝SKILLを共有して、AI側でCLAUDE.mdやSKILL.mdを作成してもらうという寸法です。

```md:initプロンプト
以下の処理が実現できるよう、CLAUDE.mdおよびSKILL.mdを作成してください。
必要に応じてスクリプトも作成してください。

# 処理概要

# スキル一覧

# ディレクトリ構成

# 指示および出力のイメージ
```




# 例１：入力された２つの変数で計算結果を返す
空のディレクトリで`Claude`コマンドを起動したあと、すぐにinitプロンプトを投げつけてみます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/030e726f-4393-4b14-b26f-12acc177a387.png)

```md:initプロンプト
以下の処理が実現できるよう、CLAUDE.mdおよびSKILL.mdを作成してください。
必要に応じてスクリプトも作成してください。

# 処理概要
入力された２つの変数から、和と積を計算して標準出力してください。

# スキル一覧
plusスキル：入力された2つの変数を足し算する。
timesスキル：入力された2つの変数を掛け算する。
checkスキル：入力された変数の数を確認し、2つ未満の場合は「変数が足りていません」、2より多い場合は「変数が多すぎます」と出力する。


# ディレクトリ構成
current/
├── CLAUDE.md
├── script/                  # スクリプトの配置先ディレクトリ
└── .claude/
    └── skills/              # スキルの配置先ディレクトリ
        └── (skill-name)/    # 各スキル名、スキルごとに作成
             └── SKILL.md    # 各スキルのmdファイル

# 指示および出力のイメージ
計算してください　2,3
→和：5、積：6

計算してください　1
→入力が足りていません

計算してください　1,2,3
→入力が多すぎます
```


<br>

上記をClaudeに投げ、適宜Yesを押下していくと、以下のように構成をしてくれました。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/a60c6a99-ca9f-450e-b556-d154cd33535f.png)


<br>

テスト実行したところ、問題なく実行されました。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/fcede1f9-af0c-4df0-a718-e02dca5264f9.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/9f317513-1a35-4c75-b551-e75aed527633.png)


<br>

ここまでで、`CLAUDE.md`や各`SKILL.md`、スクリプトが作成されているので、あとは各mdファイルを編集することで機能修正が可能になります。


<!-- open属性なし -->
<details><summary>自動作成された CLAUDE.md および SKILL.md（一部）</summary>

```md:（自動作成）CLAUDE.md
# 計算プロジェクト

## 概要

入力された2つの変数から和と積を計算して標準出力するプロジェクトです。

## 使い方

ユーザーが「計算してください X,Y」と入力したとき、以下の手順で処理する：

1. 入力文字列からカンマ区切りの数値リストを解析する
2. `check`スキルで入力変数の個数を検証する
3. 個数が2つの場合のみ、`plus`スキルで和を、`times`スキルで積を計算する
4. 結果を「和：X、積：Y」の形式で出力する

## スキル一覧

| スキル | 説明 |
|--------|------|
| `check` | 入力変数の個数を検証する。2未満なら「変数が足りていません」、2超なら「変数が多すぎます」と出力して処理を中断する |
| `plus` | 2つの変数を足し算する |
| `times` | 2つの変数を掛け算する |

## ディレクトリ構成

\```
/
├── CLAUDE.md
├── script/
│   ├── check.py   # 入力個数チェックスクリプト
│   ├── plus.py    # 足し算スクリプト
│   └── times.py   # 掛け算スクリプト
└── .claude/
    └── skills/
        ├── check/
        │   └── SKILL.md
        ├── plus/
        │   └── SKILL.md
        └── times/
            └── SKILL.md
\```

## 入出力例

\```
計算してください 2,3   →  和：5、積：6
計算してください 1     →  変数が足りていません
計算してください 1,2,3 →  変数が多すぎます
\```

## スクリプト実行方法

\```
python script/check.py <変数の個数>
python script/plus.py <変数1> <変数2>
python script/times.py <変数1> <変数2>
\```

```

```md:（自動作成）/plus/SKILLE.md
# plusスキル

入力された2つの変数を足し算するスキルです。

## 前提

`check`スキルにより入力変数が2つであることが確認済みであること。

## 手順

1. 以下のコマンドを実行して和を計算する：
   \```
   python script/plus.py <変数1> <変数2>
   \```
2. 出力された結果を「和：X」の形式で記録する

## 実行例

\```
python script/plus.py 2 3   # → 5
\```


```

```py:plus.py
import sys

a, b = float(sys.argv[1]), float(sys.argv[2])
result = a + b
print(int(result) if result == int(result) else result)
```


</details>







# 例２：キーワードから俳句と短歌を作ってファイルに出力する
空のディレクトリで`Claude`コマンドを起動したあと、すぐにinitプロンプトを投げつけてみます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/43e49c60-ac86-460e-a417-857dedeb9ffc.png)

```md:initプロンプト
以下の処理が実現できるよう、CLAUDE.mdおよびSKILL.mdを作成してください。
必要に応じてスクリプトも作成してください。

# 処理概要
入力されたキーワードから、俳句と短歌を作成してtxtファイルに出力してください。

# スキル一覧
haikuスキル：キーワードから俳句(5/7/5)を作成するスキル
tankaスキル：キーワードから短歌(5/7/5/7/7)を作成するスキル
outputスキル：俳句または短歌をtxtファイルに出力します。俳句の場合、YYYYMMDD-hhmmss-haiku.txt、短歌の場合、YYYYMMDD-hhmmss-tanka.txtというファイル名で出力します。ファイル内容は、5/7/5の3行、または5/7/5/7/7の5行で出力してください。


# ディレクトリ構成
/
├── CLAUDE.md
├── script/                  # スクリプトの配置先ディレクトリ
├── output/                  # 出力ファイルの配置先ディレクトリ
└── .claude/
    └── skills/              # スキルの配置先ディレクトリ
        └── (skill-name)/    # 各スキル名、スキルごとに作成
             └── SKILL.md    # 各スキルのmdファイル

# 指示および出力のイメージ
「海」で俳句と短歌を作成して
→outputディレクトリに以下ファイルを出力しました。
　・YYYYMMDD-hhmmss-haiku.txt
　・YYYYMMDD-hhmmss-tanka.txt
```


<br>

上記をClaudeに投げると、以下のように構成をしてくれました。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/28c89b35-aa34-43b6-833e-843fe4e49d3c.png)


<br>

テスト実行したところ、ファイル出力も問題なくできました。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/dc91460f-12b1-4103-a455-51361e588329.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/a94fd88b-f4d6-465c-a7a6-14d00831083c.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/0701e793-ba4d-4f8a-9644-a01df0ee4e3d.png)



<br>

ここまでで、`CLAUDE.md`や各`SKILL.md`が作成されているので、あとは各mdファイルを編集することで機能修正が可能になります。




<!-- open属性なし -->
<details><summary>自動作成された CLAUDE.md および SKILL.md（一部）</summary>

```md:（自動作成）CLAUDE.md
# 俳句・短歌生成プロジェクト

## 概要

キーワードを入力すると、俳句（5/7/5）と短歌（5/7/5/7/7）を生成して `output/` ディレクトリにテキストファイルとして保存するプロジェクト。

## ディレクトリ構成

\```
/
├── CLAUDE.md                        # このファイル
├── script/                          # スクリプト配置先
│   └── save_poem.ps1                # ファイル保存スクリプト
├── output/                          # 出力ファイル配置先
│   └── YYYYMMDD-hhmmss-haiku.txt   # 俳句出力ファイル（例）
│   └── YYYYMMDD-hhmmss-tanka.txt   # 短歌出力ファイル（例）
└── .claude/
    └── skills/                      # カスタムスキル配置先
        ├── haiku/
        │   └── SKILL.md             # 俳句生成スキル
        ├── tanka/
        │   └── SKILL.md             # 短歌生成スキル
        └── output/
            └── SKILL.md             # ファイル出力スキル
\```

## スキル一覧

| スキル | 呼び出し | 説明 |
|--------|----------|------|
| haiku  | `/haiku` | キーワードから俳句（5/7/5）を生成 |
| tanka  | `/tanka` | キーワードから短歌（5/7/5/7/7）を生成 |
| output | `/output` | 俳句または短歌をtxtファイルに出力 |

## 使い方

### 俳句と短歌を両方作成してファイル出力する（典型的な使い方）

\```
「海」で俳句と短歌を作成して
\```

この指示に対して以下の処理を行う：

1. `/haiku` スキルで俳句を生成
2. `/tanka` スキルで短歌を生成
3. `/output` スキルで俳句を `YYYYMMDD-hhmmss-haiku.txt` に保存
4. `/output` スキルで短歌を `YYYYMMDD-hhmmss-tanka.txt` に保存
5. 出力ファイルのパスをユーザーに報告

### 個別に実行する場合

\```
「春」で俳句を作って          → /haiku スキルを実行
「秋」で短歌を作って          → /tanka スキルを実行
この俳句をファイルに保存して  → /output スキルを実行
\```

## 出力ファイル形式

### 俳句（haiku）
- ファイル名: `YYYYMMDD-hhmmss-haiku.txt`
- 内容: 3行（5音／7音／5音）

\```
古池や
蛙飛び込む
水の音
\```

### 短歌（tanka）
- ファイル名: `YYYYMMDD-hhmmss-tanka.txt`
- 内容: 5行（5音／7音／5音／7音／7音）

\```
海原に
波が押し寄せ
砕け散る
白き飛沫の
果てなき旅路
\```

## 注意事項

- 日本語の音数（モーラ）を正確にカウントする
- 長音（ー）、促音（っ）、撥音（ん）はそれぞれ1音として数える
- 拗音（きゃ、しゅ、ちょ など）は2文字で1音として数える
- キーワードに関連した季語や情景を盛り込み、情緒ある作品を目指す

```

```md:（自動作成）/haiku/SKILLE.md
# haiku スキル

キーワードから俳句（5/7/5）を生成するスキル。

## 実行手順

1. ユーザーのメッセージからキーワードを抽出する
2. そのキーワードをテーマに俳句を1句作成する
3. 音数を必ず検証してから出力する

## 俳句の作り方

- **形式**: 5音 / 7音 / 5音 の3句構成
- キーワードを中心に据え、季節感・情景・感情を盛り込む
- 季語を積極的に活用する（キーワード自体が季語になる場合もある）
- 切れ字（や・かな・けり など）を効果的に使う

## 音数カウントのルール

| 種類 | 例 | 音数 |
|------|-----|------|
| 通常の仮名 | か、き、く | 各1音 |
| 長音符 | ー（コーヒー） | 1音 |
| 促音 | っ（きって） | 1音 |
| 撥音 | ん（みんな） | 1音 |
| 拗音 | きゃ、しゅ、ちょ | 2文字で1音 |

## 出力形式

作成した俳句を以下の形式で出力する：

\```
（第1句：5音）
（第2句：7音）
（第3句：5音）
\```

各句を改行で区切り、読み仮名や解説は不要。俳句本文のみを出力する。

## 音数検証

出力前に必ず各句の音数を声に出して（内部的に）数え、5/7/5 になっていることを確認する。合わない場合は作り直す。

## 例

**キーワード「海」の場合：**

\```
夏の海
波が砕けて
白泡立つ
\```

検証：
- 「なつのうみ」→ な(1)つ(2)の(3)う(4)み(5) = 5音 ✓
- 「なみがくだけて」→ な(1)み(2)が(3)く(4)だ(5)け(6)て(7) = 7音 ✓
- 「しろあわたつ」→ し(1)ろ(2)あ(3)わ(4)た(5)つ(6) = 6音 ✗ → 作り直す

## このスキルの後続処理

俳句を生成したら、ユーザーから「ファイルに保存して」と指示があった場合、または最初の指示に「作成して」「出力して」が含まれている場合は `/output` スキルを続けて実行する。

```

```ps:save_poem.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("haiku", "tanka")]
    [string]$Type,

    [Parameter(Mandatory=$true)]
    [string]$Line1,

    [Parameter(Mandatory=$true)]
    [string]$Line2,

    [Parameter(Mandatory=$true)]
    [string]$Line3,

    [Parameter(Mandatory=$false)]
    [string]$Line4,

    [Parameter(Mandatory=$false)]
    [string]$Line5
)

if ($Type -eq "tanka" -and (-not $Line4 -or -not $Line5)) {
    Write-Error "tanka requires -Line4 and -Line5"
    exit 1
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$filename = $timestamp + "-" + $Type + ".txt"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputDir = Join-Path $scriptDir "..\output"
$outputPath = Join-Path $outputDir $filename

if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$nl = [System.Environment]::NewLine
if ($Type -eq "haiku") {
    $content = $Line1 + $nl + $Line2 + $nl + $Line3
} else {
    $content = $Line1 + $nl + $Line2 + $nl + $Line3 + $nl + $Line4 + $nl + $Line5
}

[System.IO.File]::WriteAllText($outputPath, $content, [System.Text.UTF8Encoding]::new($false))

Write-Output ("output/" + $filename)

```


</details>



# 後記
どんどん生成AI自体の精度や周辺のツール/環境がアップデートされていくので、そのうち生成AIが **"全部察して責任も明確化してくれる"** ような未来も訪れるかもしれません。

ただそれまでは人間が生成AIを(および人間を)指示・管理・監督する必要があることは変わらないと思うので、「なるべく具体的な指示を」「可能な限り簡素に」するという微妙なラインを攻めるというところが個人業務効率化のコツなのでは、というのをこの記事を書いていて思いました。
