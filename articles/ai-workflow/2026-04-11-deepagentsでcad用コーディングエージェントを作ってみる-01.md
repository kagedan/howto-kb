---
id: "2026-04-11-deepagentsでcad用コーディングエージェントを作ってみる-01"
title: "deepagentsでCAD用コーディングエージェントを作ってみる"
url: "https://zenn.dev/neka_nat/articles/905843984f6972"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

# はじめに

2年前くらいに図面画像から3DCADを生成するAIワークフローの記事を書いたのですが、そこからかなりAIの性能が進化し、AIエージェントが主流となった今、これをリファインしてAIコーディングエージェントを使ったCAD生成を行ってみました。

<https://zenn.dev/firstautomation/articles/dc3690eb364e48>

# CAD用コーディングエージェント

前回の記事でも触れましたが、**CADはプログラミングです。**  
以下のようにCAD上ではデータ構造がツリー形式で表されており、それぞれのノードの関係性を演算によって記述することで3Dモデルを表現しています。

![](https://static.zenn.studio/user-upload/b6efefdde560-20260412.jpg)

実際にコードを使った例を見てみます。  
以下は[Cadquery](https://github.com/cadquery/cadquery)を使ったCADプログラムの例です。

```
result = cq.Workplane("front").box(2, 3, 0.5)  # make a basic prism
result = (
    result.faces(">Z").workplane().hole(0.5)
)  # find the top-most face and make a hole
```

このコードによって以下のような3Dモデルが作られます。  
![](https://static.zenn.studio/user-upload/9026d8382455-20260412.png)

簡単に説明すると、これは最初に2x3x0.5のboxが作られ、その後、直径0.5の穴がboxに追加されるというコードになっています。

このようにCADはプログラミングであり、コーディングエージェントを使って精度の高い3DCAD生成ができるのではと考えました。

# deepagentsとは？

deepagentsは**langchain/langgraphをベースに作られた、"Agent Harness"です。**

<https://github.com/langchain-ai/deepagents>

プランニングやファイルシステム操作、プログラム実行のような基本的なツールが用意された状態でのAIエージェントを簡単に立ち上げ、実行することができます。  
また、Skillsやサブエージェントなども使用することができ、柔軟なハーネス設計が可能となっています。  
Pythonパッケージとしてアプリに組み込むことができるので、**オリジナルのClaude CodeのようなAIエージェントを簡単に構築することができます。**

# 今回作成したAIコーディングエージェントの構成

CAD用のコーディングエージェントを作るにあたって、以下のような構成のAIエージェントを作りました。

## Workspace

**Workspaceはコーディングエージェントが作業を行なうための作業用フォルダです。**  
今回のCAD用コーディングエージェントでは、以下のような作業フォルダの構造になっており、入力となるファイルやSkillsファイル、各工程での成果物および最終的なCADファイルなどが格納されます。

```
workspace
├── artifacts  # 最終的な3DCADモデルなどの成果物置き場
│   ├── build_report.json
│   ├── model.step  # 3DCADモデル、最終成果物
│   ├── model.stl
│   └── projections
│       ├── front.png
│       ├── right.png
│       ...
├── generated  # 生成された3DCADコード
│   ├── history
│   └── model.py  # 3DCADを生成するpythonコード
├── input  # 入力画像
│   └── reference.png
├── preprocessed  # 入力画像などを編集した画像
│   ├── front_ref.png
│   ...
├── review  # 生成した3DCADのレビュー結果
│   ├── compare_report.json
│   └── fix_plan.json
├── skills  # サブエージェントが使用するSkills
│   ├── builder
│   │   └── SKILL.md
│   └── verifier
│       └── SKILL.md
└── templates  # コード生成時のテンプレート
    └── model_template.py
```

## 画像編集ツール

今回のエージェントは図面画像からのCAD生成を想定していたので、**画像処理まわりのツールを用意しました。**  
特に与えられた図面に対して、3D形状を作る上で、  
**寸法線を除いた外形の情報** と  
**図面上のどの投影図がどこから見たビューか**  
を知る必要がありそうだと思い、以下のようなツールを用意しました。

* **外形抽出ツール**: 与えられた図面に対して、外形のみを抽出するように画像を編集するツール(`Nanobanana2`を使用)
* **投影図抽出ツール**: 与えられた図面と抽出したい投影図の名称(正面図、側面図など)を与えて、対象のビューを取得するツール(`gemini-3-flash-preview`を使用)

## CADコードビルダー(サブエージェント)

**指示されたオブジェクトを作るためのCADコードを生成するサブエージェントです。**  
メインのエージェントから受け取った指示を元に[Cadquery](https://github.com/cadquery/cadquery)というPython用の3DCADコードを書くパッケージを使って、3DCADモデルを生成するコードを作成します。  
作成されたコードを実行し、エラーがあれば修正、最終的に3DCADモデルを`artifact`フォルダに保存するまでの役割を担います。  
ここまでの流れをSkillsとして保持しておき、参照できるようにしています。

## 検証エージェント(サブエージェント)

生成された3DCADモデルを画像にレンダリングして、見た目的に合ってそうかを検証するサブエージェントです。  
元の図面との比較を行い、修正ポイントをJSON形式でまとめます。  
検証において、上記の画像編集ツールと画像を比較するためのツールが与えられており、これらを駆使してモデルの検証を行います。

## 最終的に作成されたAIエージェント

ここまでの要素を組み合わせて、deepagentsを使って作成したモデルは以下のようなモデルになっています。(実際のAIエージェント作成部分のみ抽出したコード)  
メインのエージェントに対して、2つのサブエージェントが登録されており、ツールとして画像編集ツールを使用することができます。  
検証エージェントにも画像編集ツールとこちらには画像比較用のツールも登録されています。

```
# 各サブエージェントを定義
subagents = [
    {
        "name": "cadquery-builder",
        "description": "Build the CadQuery model from the reference drawing, optionally using image_editor outputs and verifier guidance, then export artifacts.",
        "model": "gemini-3.1-pro-preview",
        "system_prompt": BUILDER_SYSTEM_PROMPT,
        "tools": [],
        "skills": ["skills/builder"],  # CADモデル作成用スキルを登録
    },
    {
        "name": "render-verifier",
        "description": "Compare rendered projections against reference views, optionally using image_editor to isolate reference views, then write a concrete fix plan.",
        "model": "gemini-3-flash-preview",
        "system_prompt": VERIFIER_SYSTEM_PROMPT,
        "tools": [image_editor, compare_projection_pair],  # こちらのサブエージェントにもツールを登録
        "skills": ["skills/verifier"],  # CADモデル検証用スキルを登録
    },
]

# メインエージェントを作成
agent = create_deep_agent(
    name="drawing-to-cad-supervisor-local-shell",
    model="gpt-5.4",  # メインエージェントで使用するAIモデル
    backend=backend,
    checkpointer=InMemorySaver(),
    system_prompt=SUPERVISOR_PROMPT,
    tools=[image_editor],  # 画像編集ツールを登録
    subagents=subagents,
    debug=debug,
)
```

# 生成結果

今回、生成に使用した図面は以下です。  
![](https://static.zenn.studio/user-upload/458ecc56954a-20260411.png)

3回ほどコードのリファインを行っており、最終的に以下のような3DCADモデルが生成されました。

![](https://static.zenn.studio/user-upload/e5146b4d05e4-20260411.png)

余分なRが付いていたりしますが、ほぼ形状が再現されているのではないかと思います。

エージェントが作業を行っていく中で、作られた中間生成物についても触れておきます。  
まずはNanobanana2を使って作成された外形図面です。  
かなり綺麗に外形が取れています。

![](https://static.zenn.studio/user-upload/53f317cd8e52-20260411.png)

次は抽出された投影図です。正面図が抽出された際の画像です。

![](https://static.zenn.studio/user-upload/56ece1385a2d-20260411.png)

次は実際に比較検証の際に作られた画像です。  
1回目に生成された3DCADモデルを検証した際の比較画像と最終3DCADモデルの比較画像を載せてます。

**1回めの比較画像**  
![](https://static.zenn.studio/user-upload/3f379c8411c8-20260411.png)

**最終の比較画像**  
![](https://static.zenn.studio/user-upload/1a162502006d-20260411.png)

検証を重ねることで、形状が近づいているのが分かります。  
最終のCADモデルは重ね合わせると形状的には合っているのですが、寸法的にはまだまだ正確でない部分は多そうです。

今回、使用したコードは以下になります。  
<https://github.com/neka-nat/agent3dify>

# まとめ

**deepagentsを用いて、3DCADコードを生成するコーディングエージェントを作ってみました。**  
gemini-3.1-pro-previewの素の性能が良いということはありつつ、検証を重ねながら改善していくところはエージェントになることで性能が上がっていると言えそうです。  
deepagentsを使ってAI Harnessを構築して、オリジナルのコーディングエージェントを作るのは他にもいろいろ応用がありそうで、今後も試していきたいと思います。
