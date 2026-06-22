---
id: "2026-06-21-未経験からaiエンジニアを目指すならgithubとhugging-faceをポートフォリオに変える-01"
title: "未経験からAIエンジニアを目指すなら：GitHubとHugging Faceをポートフォリオに変える"
url: "https://zenn.dev/zapabob/articles/portfolio-github-huggingface-ai-engineer"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "GPT", "Python", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

AIコーディングの時代になって、未経験からエンジニアを目指す人に必要なものは少し変わりました。

以前は、まず文法を覚える。次にチュートリアルを写す。小さなWebアプリを作る。ポートフォリオを整える。そういう順番が一般的でした。

もちろん、今でも基礎は大切です。PythonもGitもHTTPも、知らなくてよいわけではありません。

けれど、AIエージェントがコードを書けるようになった今、未経験者にとって本当に大事なのは **自分で全部のコードを手書きできること** だけではなくなっています。

むしろ、次の力が前に出てきました。

* 何を作るべきかを決める力
* AIに実装させるために、問題を小さく切る力
* 出てきたコードが正しいかを確認する力
* 動くデモとして公開する力
* READMEやモデルカードで、設計判断を説明する力
* 作ったものをGitHubやHugging Faceに残す力

私は、これからの未経験エンジニアのポートフォリオは、単なる作品集ではなく **思考と検証の履歴** になると思っています。

この記事では、GitHubとHugging Faceをどう使えば、AIコーディング時代のポートフォリオになるのかを整理します。題材として、私自身の `zapabob` / `zapabobouj` の公開プロフィールも扱います。

## コードが書ける、はもうゴールではない

最初に、少し厳しいことを言います。

AIがあるから、コードを書けなくてもエンジニアになれる。

これは半分だけ正しいです。

AIは実装を助けてくれます。小さなWebアプリ、CLIツール、データ処理、Gradioデモ、テストコード、READMEの下書き。そういうものは、以前よりずっと速く作れるようになりました。

けれど、AIが書いたコードを読めない。動作確認できない。エラーが出たときに原因を分解できない。なぜその設計にしたのか説明できない。

この状態では、エンジニアとして信頼されるのは難しいです。

AI時代の未経験者に必要なのは、コードを一文字ずつ全部書く力よりも、次のような力です。

* 課題を見つける
* 実装範囲を絞る
* AIに指示する
* 結果を検証する
* 測定する
* 公開する
* 説明する

つまり、AIに任せる部分が増えたぶん、人間側には **設計者・検証者・編集者としての力** が求められます。

その証拠を見せる場所が、GitHubとHugging Faceです。

## GitHubとHugging Faceは役割が違う

GitHubとHugging Faceは、どちらもポートフォリオに使えます。けれど、見せるものが違います。

GitHubは、開発の過程を見せる場所です。

どんなコードを書いたか。  
どういう構成にしたか。  
READMEで何を説明しているか。  
テストがあるか。  
コミットが続いているか。  
issueやPRをどう扱っているか。

GitHub公式ドキュメントでも、プロフィールREADMEは、自分について他者に伝えるためにプロフィールへ表示できる仕組みとして説明されています。ユーザー名と同じ名前の公開リポジトリを作り、ルートに `README.md` を置くことで表示されます。([GitHub Docs](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme "Managing your profile README - GitHub Docs"))

一方で、Hugging Faceは、AIとして何を公開できるかを見せる場所です。

モデル。  
データセット。  
Spacesのデモ。  
モデルカード。  
推論の使い方。  
評価結果。  
制限事項。

Hugging Face Spacesは、機械学習デモを短時間で作成・デプロイする仕組みとして説明されており、Gradio、Docker、Static HTMLなどのSDKを選べます。さらに、SpaceはGitリポジトリとしてコードを保持し、pushのたびに再ビルドされます。([Hugging Face](https://huggingface.co/docs/hub/spaces-overview "Spaces Overview · Hugging Face"))

モデルを公開する場合は、モデルカードが重要です。Hugging Face公式ドキュメントでは、モデルカードはモデルに付随するMarkdownファイルで、発見性、再現性、共有に重要だと説明されています。モデルの用途、制限、学習情報、使用データセット、評価結果を書くべきものとして扱われています。([Hugging Face](https://huggingface.co/docs/hub/model-cards "Model Cards · Hugging Face"))

つまり、こう分けると分かりやすいです。

| 場所 | 見せるもの | 採用・評価で伝わること |
| --- | --- | --- |
| GitHub | コード、README、テスト、開発履歴 | どう作る人か |
| Hugging Face | モデル、デモ、モデルカード、評価 | AIで何を公開できる人か |
| Zenn / Qiita | 実装ログ、失敗、設計判断 | 何を考えた人か |

GitHubだけでも足りません。  
Hugging Faceだけでも足りません。  
記事だけでも足りません。

この3つをつなぐと、ポートフォリオが立体的になります。

## 実例：zapabobの公開ポートフォリオを見る

ここで、私自身の公開プロフィールを例にします。

2026-06-21時点で、GitHubの `zapabob` プロフィールには、172の公開リポジトリ、253 followers、224 stars が表示されています。また、プロフィールREADMEには `AI Engineering Portfolio // zapabob` という見出しと、創薬モデル、エージェントシステム、CUDA測定実験、VR/Unity研究ツールを作るAIエンジニアであるという説明が置かれています。([GitHub](https://github.com/zapabob "zapabob (峯岸 亮) · GitHub"))

ピン留めリポジトリを見ると、分野がかなり分かれています。

`multi-target-pIC50-predictor` は、DAT、5-HT2A、CB1、CB2、opioid receptors などを対象にしたpIC50 / pKiモデリング、RDKit descriptors、ECFP4 / MACCS fingerprints、SMARTS flags、GNN、Elastic Looped Transformerなどを扱う研究用QSARプロトタイプです。READMEには再現コマンド、ベンチマーク、研究用途の制限が明記されています。([GitHub](https://github.com/zapabob/multi-target-pIC50-predictor "GitHub - zapabob/multi-target-pIC50-predictor"))

`jaxa-earth-vrchat-terrain` は、JAXA Earth APIの地球観測データをBlender、Unity、VRChat向けの3D地形へ変換するMCPサーバーです。READMEでは、MCPサーバー、Streamlit UI、自然言語IDE操作、Blender export、Unity Terrain exportなどがEvidence Cardとして整理されています。([GitHub](https://github.com/zapabob/jaxa-earth-vrchat-terrain "GitHub - zapabob/jaxa-earth-vrchat-terrain"))

`Turboquant-CUDA` は、Qwen3.5-9BのKV-cache TurboQuant測定、captured replay、hidden cosine、logit cosine、attention relative error、memory ratio、runtime plotsなどを扱う測定系リポジトリです。READMEには再現コマンドと、研究からruntimeまでの chain を可視化する意図が書かれています。([GitHub](https://github.com/zapabob/Turboquant-CUDA "GitHub - zapabob/Turboquant-CUDA"))

`hypura` は、Windows上で大きなGGUFモデルを動かすためのRust系ランタイムで、GPU、RAM、pinned host memory、NVMeをまたいでテンソルを配置する方針が説明されています。([GitHub](https://github.com/zapabob/hypura "GitHub - zapabob/hypura"))

Hugging Face側の `zapabobouj` プロフィールには、AI / ML interestsとして研究者・科学者を示す説明があり、11 models、7 Spaces、2 datasets が表示されています。2026-06-21時点でも直近にモデル更新が継続しており、`qwen3.5-elt-l3` の更新・公開が相対表示で2日前となっています。([Hugging Face](https://huggingface.co/zapabobouj "zapabobouj (Ryo Minegishi)"))

さらに `qwen3.5-elt-l3` のモデルページでは、Hugging Face safetensorsとGGUF artifactsとして公開され、強い主張を狭く限定する形で、local STEM bridge taskやloop depthに関する説明が書かれています。これは、モデル公開時に **何が言えて、何がまだ言えないか** を分けて書く例として使えます。([Hugging Face](https://huggingface.co/zapabobouj/qwen3.5-elt-l3 "zapabobouj/qwen3.5-elt-l3 · Hugging Face"))

ここで大事なのは、スター数が大きいかどうかではありません。

重要なのは、プロフィールを見た瞬間に、

* この人は何の分野に深く入っているのか
* どんな周辺分野に広げているのか
* 実装だけでなく測定しているか
* READMEで再現性を出しているか
* GitHubとHugging Faceがつながっているか

が伝わることです。

未経験者のポートフォリオでも、この構造は再現できます。

## 原則1：一分野に深く、別分野に広く

ポートフォリオで一番避けたいのは、何でもできますという見せ方です。

Webアプリもできます。  
AIもできます。  
Unityもできます。  
Rustもできます。  
データ分析もできます。

こう並べるだけでは、見る側には軸が伝わりません。

良いポートフォリオには、縦軸と横軸があります。

縦軸は、自分が最も深く掘るテーマです。たとえば、次のようなものです。

* 創薬AI
* ローカルLLM
* 画像認識
* 音声認識
* VR / Unity
* 業務自動化
* セキュリティ
* データ可視化
* バイオインフォマティクス

横軸は、そのテーマを広げるための周辺技術です。

たとえば創薬AIを縦軸にするなら、横軸は次のようになります。

* Python
* RDKit
* PyTorch
* FastAPI
* Docker
* Hugging Face
* Gradio
* 実験ログ
* モデルカード

VR / Unityを縦軸にするなら、横軸はこうです。

* C#
* Unity Editor拡張
* Blender
* Shader
* Pythonによるデータ変換
* MCP
* GitHub Actions
* READMEによる配布手順

未経験者は、最初から分野を広げすぎないほうがよいです。

まず1つ、好きなテーマを決める。  
そのテーマで小さく動くものを作る。  
次に、それを支える周辺技術を足す。

この順番が良いです。

## 原則2：作っただけではなく、測った証拠を残す

AI時代のポートフォリオで重要なのは、作りました、で終わらせないことです。

動きました。  
測りました。  
比較しました。  
失敗も記録しました。  
制限も書きました。

ここまであると、信頼されやすくなります。

たとえば、画像分類モデルなら、単にモデルを作るだけでは弱いです。

* 何枚のデータで学習したか
* train / validation / test をどう分けたか
* accuracy、F1、confusion matrix はどうだったか
* どのクラスを間違えやすいか
* デモはどこで触れるか
* どういう用途には使ってはいけないか

ここまでREADMEやモデルカードに書く。

チャットボットなら、

* どのモデルを使ったか
* どんなプロンプト設計にしたか
* 何件で試したか
* 失敗例は何か
* 応答速度はどの程度か
* 個人情報をどう扱うか

を書きます。

GitHubでは、READMEの中にEvidence欄を作るとよいです。

```
## Evidence

- Demo: Hugging Face Spaces URL
- Test: `pytest` passed
- Metrics:
  - accuracy: 0.84
  - macro F1: 0.78
- Known limitations:
  - 小規模データセットなので汎化性能は未検証
  - 医療・法律・金融判断には使わない
```

Hugging Faceでは、モデルカードに用途、制限、評価結果、使い方を書きます。

```
---
license: mit
tags:
  - text-classification
  - gradio
  - portfolio
---

# Model Card

## What this model does

このモデルは、短い日本語テキストをカテゴリ分類する実験用モデルです。

## Intended use

- 個人用メモの分類
- 学習用デモ
- ポートフォリオでの技術説明

## Not intended use

- 医療、法律、金融などの高リスク判断
- 個人情報を含む入力
- 本番環境での自動判定

## Evaluation

| metric | value |
|---|---:|
| accuracy | 0.84 |
| macro F1 | 0.78 |

## How to run

```python
from transformers import pipeline

clf = pipeline("text-classification", model="yourname/your-model")
clf("今日は請求書を整理した")
```
```

未経験者にとって、測定値はとても強い証拠になります。

完璧な精度である必要はありません。  
むしろ、低い精度でも、なぜ低いかを説明できるほうが良いです。

## 原則3：GitHubは作り方、Hugging Faceは動くものを見せる

GitHubだけにコードを置いても、採用担当者や読者がすぐ動かしてくれるとは限りません。

ローカル環境を作る。  
依存関係を入れる。  
.env を設定する。  
データを落とす。  
コマンドを実行する。

ここまでやってくれる人は少ないです。

だから、AI系ポートフォリオでは、Hugging Face Spacesのような動くデモが強くなります。

Spacesなら、ブラウザで触れるデモを置けます。Hugging Face公式ドキュメントでも、SpacesはML-powered demosを短時間で作成・デプロイする仕組みとして説明され、Public Spacesではソースコードの閲覧、アプリへのアクセス、cloneが可能です。([Hugging Face](https://huggingface.co/docs/hub/spaces-overview "Spaces Overview · Hugging Face"))

おすすめの構成はこうです。

```
GitHub repo
├── README.md
├── app.py
├── requirements.txt
├── src/
├── tests/
└── _docs/
    └── 2026-06-21_implementation-log.md

Hugging Face Space
├── app.py
├── README.md
└── requirements.txt
```

GitHub READMEには、Hugging Face Spacesへのリンクを置きます。

```
## Demo

You can try the demo here:

- Hugging Face Spaces: https://huggingface.co/spaces/yourname/project-name
```

Hugging Face側には、GitHubリポジトリへのリンクを置きます。

```
## Source code

The source code and implementation log are available on GitHub:

- https://github.com/yourname/project-name
```

この往復リンクが大切です。

GitHubで作り方を見る。  
Hugging Faceで動くものを触る。  
Zennで設計判断を読む。

この3つがつながると、ポートフォリオとしてかなり見やすくなります。

## 原則4：READMEは30秒で伝わる入口にする

採用や評価の場では、READMEがかなり重要です。

RUNTEQの2025年の記事でも、採用で評価されるGitHubのポイントとして、Contribution Graph、READMEの記述内容、開発フロー、コードの可読性、Gitのお作法、使用技術、オリジナル作品の有無が挙げられています。([RUNTEQ(ランテック)](https://runteq.jp/blog/portfolio/29737/ "【転職で差がつく】採用で評価されるGithub7つのポイントを解説"))

未経験者のREADMEでありがちな失敗は、情報が足りないことです。

これでは弱いです。

最低限、次の項目は入れたほうがよいです。

```
# Project Name

## What this solves

このプロジェクトは何の課題を解くのか。

## Demo

- Web demo:
- Hugging Face Spaces:
- Screenshot:

## Features

- 機能1
- 機能2
- 機能3

## Tech stack

- Python
- Gradio
- FastAPI
- PyTorch
- Docker

## Architecture

簡単な構成説明。

## Evidence

- 測定値
- テスト結果
- ベンチマーク
- 失敗例

## How to run

```bash
git clone ...
cd ...
pip install -r requirements.txt
python app.py
```

## AI usage

このプロジェクトでは、AIコーディングエージェントを以下の用途で使いました。

* 初期実装案の生成
* テストケースの作成
* READMEの構成案
* リファクタリング候補の抽出

最終的な設計判断、検証、READMEの責任は作者が持ちます。

## Limitations

* 小規模データでの検証
* 本番利用は未検証
* 個人情報を含む入力は想定外
```

特に `AI usage` は、これから重要になります。

AIを使ったことを隠す必要はありません。  
ただし、AIに丸投げしたように見せてはいけません。

どこをAIに任せたのか。  
どこを自分が確認したのか。  
どこに制限があるのか。

これを書ける人は、AIを道具として扱えているように見えます。

## 未経験からのロードマップ

では、未経験者がこの形のポートフォリオを作るなら、どう進めるべきでしょうか。

私は、4ステップで十分だと思います。

## Step 1：好きな課題を1つ選ぶ

最初のテーマは、流行よりも自分が続けられるものを選んだほうがよいです。

たとえば、

* 家計簿CSVを自動分類する
* VRChatイベントのログを整理する
* 好きなゲームの戦績を可視化する
* 論文PDFを要約してタグ付けする
* 英単語学習をAIで出題する
* 画像から商品カテゴリを分類する
* 音声メモを文字起こしして検索する

このくらいで十分です。

大切なのは、現実の入力と出力があることです。

入力がある。  
処理がある。  
出力がある。  
評価がある。

これがポートフォリオになります。

## Step 2：AIと一緒に最小版を作る

最初から大きなものを作らないほうがよいです。

まずは、1画面で動くもの。  
1コマンドで動くもの。  
1つのCSVで動くもの。  
1つのモデルで推論できるもの。

このくらいにします。

AIへの指示も、小さく切ります。

```
目的:
家計簿CSVを読み込み、支出カテゴリを推定するPythonアプリを作りたい。

最初のスコープ:
- CSVを読み込む
- merchant, memo, amount の3列を使う
- ルールベースでカテゴリ分類する
- Gradioで入力と結果を表示する
- READMEに実行方法を書く

まだやらないこと:
- ログイン
- データベース
- 課金
- 高度な機械学習
```

このように、やることとやらないことを分けます。

AI時代の未経験者は、実装力だけでなく **スコープを切る力** を見られます。

## Step 3：測定と実装ログを残す

作ったら、必ず記録します。

```
_docs/
└── 2026-06-21_household-classifier_codex.md
```

中身は、短くてよいです。

```
# household-classifier 実装ログ

## 目的

家計簿CSVを読み込み、支出カテゴリを自動分類する。

## 使用したAI

- Codex
- ChatGPT

## 実装したこと

- CSV reader
- ルールベース分類
- Gradio UI
- pytestによる分類テスト

## 採用した判断

最初の版では機械学習を使わず、ルールベースにした。
理由は、データ数が少ない段階ではモデル精度よりも分類ルールの可視性が重要だから。

## 検証

\`\`\`bash
pytest
python app.py
\`\`\`

## 制限

* merchant名が未知の場合は分類精度が下がる
* 個人情報を含むCSVは公開しない
```

この実装ログがあると、読者はあなたの判断を追えます。

ただ作った人ではなく、考えて作った人に見えます。

## Step 4：プロフィールREADMEを整える

最後に、GitHubプロフィールREADMEを整えます。

GitHubのプロフィールREADMEは、ユーザー名と同名の公開リポジトリに `README.md` を置くことでプロフィール上に表示されます。([GitHub Docs](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme "Managing your profile README - GitHub Docs"))

未経験者向けの最小テンプレートは、これで十分です。

```
# AI Engineering Portfolio // yourname

AIを使って、日常の課題を小さなツールとデモに落とし込むポートフォリオです。

## Selected Projects

| Project | What it does | Evidence |
|---|---|---|
| household-classifier | 家計簿CSVをカテゴリ分類 | GitHub / HF Spaces / metrics |
| paper-tagger | 論文PDFを要約してタグ付け | GitHub / demo / README |
| game-log-analyzer | ゲームログを可視化 | GitHub / screenshot |

## Engineering Focus

- AI-assisted development
- Python tools
- Gradio / Hugging Face Spaces
- Data processing
- README-driven documentation

## How I use AI

- AIに初期実装とテスト案を出させる
- 自分で仕様、検証、制限事項を書く
- 実装ログに判断の理由を残す

## Connect

- GitHub:
- Hugging Face:
- Zenn:
- X:
- LinkedIn:
```

ここで大切なのは、盛りすぎないことです。

未経験なのに、AI研究者、フルスタック、MLOps、LLMOps、Unity、Rust、CUDA、全部できますと書くと、むしろ信用されにくくなります。

今できること。  
今作っているもの。  
次に伸ばしている分野。

この3つを素直に並べるほうがよいです。

## 採用担当者は何を見るのか

採用担当者や技術面接官が、全リポジトリのコードを細かく読むことは多くありません。

最初に見るのは、おそらく次です。

* プロフィールREADME
* ピン留めリポジトリ
* READMEの分かりやすさ
* 動くデモ
* コミットの継続性
* オリジナルの課題設定
* テストや検証の有無
* AI利用の説明
* 制限事項の書き方

ここで、スター数は主役ではありません。

もちろん、スターが多いのは良いことです。けれど未経験者の採用で、スター数だけを主な評価軸にするのは現実的ではありません。

それよりも、

この人は、作ったものを他人に伝える気があるか。  
この人は、動作確認をしているか。  
この人は、失敗や制限を書けるか。  
この人は、AIの出力を自分の責任で扱えるか。

こちらのほうが大切です。

AIコーディング時代には、コードの量よりも、判断の可視化が重要になります。

## 注意：公開プロフィールは採用向けに整える

ひとつだけ、現実的な注意もあります。

Hugging FaceやGitHubは公開プロフィールです。研究用、趣味用、実験用のものが混在していると、見る人によって印象が変わります。

たとえば、Hugging Faceプロフィールに実験的なSpacesや用途が限定されるモデルが並ぶ場合、採用向けには見せたいプロジェクトをREADMEやプロフィール文で整理したほうがよいです。

公開プロフィールに何が見えるかは、本人が思っている以上に大事です。

見せたいものを上に置く。  
見せたくないものは整理する。  
用途が限定されるものには、制限事項を書く。  
研究用なら研究用と明記する。

これは、自分をよく見せるためだけではありません。

見る人に誤解させないためです。

## まとめ：ポートフォリオは思考の履歴書になる

AIコーディング時代に、未経験者がエンジニアを目指すなら、完璧な大作を1つ作るより、小さくても説明できるものを複数公開したほうがよいです。

GitHubには、作り方を残す。  
Hugging Faceには、動くデモやモデルを置く。  
Zennには、判断と失敗を書く。  
READMEには、何を作り、なぜ作り、どう検証したかを書く。

AIを使うことは、もう珍しくありません。

だからこそ、差が出るのは **AIで何を作ったか** ではなく、**AIが作ったものをどう検証し、どう説明し、どう公開したか** です。

未経験者にとって、これはむしろチャンスです。

企業経験がまだなくても、GitHubに開発の跡を残せます。  
研究室に所属していなくても、Hugging Faceにモデルやデモを公開できます。  
大きな実績がなくても、Zennで判断の履歴を書けます。

履歴書には、過去の所属が並びます。

でも、ポートフォリオには、今の手つきが残ります。

AIコーディング時代にエンジニアを目指すなら、まずは小さな課題を1つ選んで、GitHubとHugging Faceに公開する。

そこからで十分です。

そして、その小さな公開物を、次の公開物につなげていく。

それが、未経験からAIエンジニアを目指すための、いちばん現実的なポートフォリオ戦略だと思います。
