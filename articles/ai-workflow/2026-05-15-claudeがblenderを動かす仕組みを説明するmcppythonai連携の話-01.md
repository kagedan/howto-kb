---
id: "2026-05-15-claudeがblenderを動かす仕組みを説明するmcppythonai連携の話-01"
title: "ClaudeがBlenderを動かす仕組みを説明する【MCP・Python・AI連携の話】"
url: "https://note.com/mim2026/n/nff217d1ecc12"
source: "note"
category: "ai-workflow"
tags: ["MCP", "API", "Python", "note"]
date_published: "2026-05-15"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

## 「なんでClaudeはBlenderへの指示だってわかるの？」

最初にこの疑問が浮かんだ。

日本語で「赤い球体を3つ作って」と打つだけで、ClaudeがBlenderを動かす。でもなんでClaudeは「これBlenderへの指示だ」ってわかるんだろう？

答えはMCPコネクタにある。

━━━━━━━

## MCPって何？3行で説明する

MCP（Model Context Protocol）は、AIと外部ツールをつなぐ「共通規格」のこと。

人間で例えると：  
・USB規格みたいなもの  
・どのパソコンにもUSBが刺さるように、MCPがあればどのAIにもツールを繋げられる  
・AnthropicがオープンソースとしてMCPを公開したことで、Blenderにも対応できるようになった

![](https://assets.st-note.com/img/1778737622-1YdtXHMsvqGD0JO5lWyTp4eu.png?width=1200)

MCP仕組み図解

━━━━━━━

## ClaudeがBlenderを動かすまでの流れ

実際に何が起きているかをステップで説明する。

### Step 1：コネクタをONにする

Claude DesktopにBlender MCPコネクタを追加した瞬間から、ClaudeはBlenderという「道具」を認識し始める。

### Step 2：日本語で指示を打つ

「赤い球体を3つランダムに配置して」とチャットに打つ。

### Step 3：ClaudeがPythonコードを自動生成する

ClaudeはBlender Python APIの仕様を理解しているので、その指示を実現するPythonコードをガシガシ書く。

実際に生成されたコードはこんな感じ↓

---  
import bpy  
import random

mat = bpy.data.materials.new(name="RedMaterial")  
mat.use\_nodes = True  
（以下省略）  
---

![](https://assets.st-note.com/img/1778737670-7aqfP8QXmVrCZe9yEtwGNpul.png?width=1200)

### Step 4：コードがBlenderに送られて実行される

MCPコネクタ経由でコードがBlenderに送信され、Blenderがそのまま実行する。

### Step 5：Blenderの画面が変わる

コードが実行された瞬間、Blenderの3Dビューポートにオブジェクトがヌッと現れる。

![](https://assets.st-note.com/img/1778737729-GhljksnQiaozqIg20cvB1R5U.png?width=1200)

球体生成

━━━━━━━

## 「Blenderへの指示」だとClaudeはどうやって判断する？

ここが一番気になるポイントだと思う。

答えは2つある。

### 理由①：コネクタがONだから

MCPコネクタをONにした時点で、ClaudeはBlenderが「今使える道具」だと認識している。3D系のワードが来たら自動的にBlenderへの指示と判断する仕組み。

ペンを持ってる状態で「これ書いといて」と言われたら、そのペンで書くとわかる。それと同じ。

### 理由②：コンテキストから判断する

「球体」「マテリアル」「シーン」「オブジェクト」などのワードが来たとき、Blenderコネクタが有効ならBlenderへの指示として処理する。

### 不安な場合の対処法

全く関係ない話をしながら急にBlender操作を混ぜると、たまに誤判断することがある。  
その場合は頭に「Blenderで」をつけると確実。

例：「Blenderで赤い球体を3つ作って」

━━━━━━━

## Blender Python APIって何？コード書けなくていいの？

「Python APIって聞いただけで難しそう」と思った人、安心してほしい。

Blenderはほぼ全ての操作をPythonで自動化できる設計になっている。本来はこのPythonを自分で書く必要があった。でもClaude×MCPの組み合わせだと、ClaudeがそのPythonを全部書いてくれる。

自分がやることはゼロ。日本語で話しかけるだけ。

3Dプリンタ勢にとってこれがどれだけデカいかというと、モデリングのコマンドをいちいち覚えなくていい。「このサイズのケースを作って」「このパーツをSTLで保存して」を日本語で指示するだけで動く。

━━━━━━━

## 実際にコードを見てみる

「どんなコードが生成されてるか気になる」という人向けに、実際のコードを見せてもらった。

「今実行したPythonコードを見せて」とClaudeに打つだけで表示してくれる。

![](https://assets.st-note.com/img/1778737564-XiSxcDBEypV42eaA7TWM8l3O.png?width=1200)

実際のコード

![](https://assets.st-note.com/img/1778737564-nG8TMDhs9uzcOPRLFE2VdJHo.png?width=1200)

コードの説明もしてくれた

コードを見ると、Blender Python APIの構造がそのまま使われているのがわかる。自分でゼロから書こうとすると数時間かかるようなコードが、日本語の指示から数秒で生成される。

━━━━━━━

## まとめ：仕組みがわかると使い方が広がる

整理するとこうなる。

・MCPはAIと外部ツールをつなぐ共通規格  
・BlenderコネクタをONにするとClaudeがBlenderを認識する  
・日本語指示→Claudeがコード生成→Blenderが実行、の流れで動く  
・Pythonの知識はゼロでOK  
・3Dプリンタ勢にとってモデリングのハードルがグンと下がる

仕組みを理解すると「じゃあこれもできるんじゃ？」という発想が広がる。次の記事では実際に使えるプロンプト集をまとめる。

━━━━━━━

## 次回予告

→【有料】Claude×Blenderで使える実用プロンプト10選（近日公開）  
マテリアル一括変更・三点照明・レンダリング自動化・STL出力など、すぐ使えるフレーズを厳選してまとめる。
