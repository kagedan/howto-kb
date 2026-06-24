---
id: "2026-06-23-claude-codeとblenderでモデルを生成しようじゃないか-01"
title: "Claude codeとBlenderでモデルを生成しようじゃないか"
url: "https://qiita.com/mittsuuuu/items/c1e53e7e8f8690d6ad71"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "Gemini", "GPT", "Python"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

こんにちは

今回は表題の通り，Claude CodeとBlenderを組み合わせて3Dモデルを自動生成を試みた内容です．


# 初めに
これをやるにあたった経緯や，自分のAI事情なんかを書きます．
本編は次の章からなので，適当に飛ばしてください．

### 最近のAI事情
自分は最近，Geminiを課金して使っていました．
CodeXやそれこそClaudeもよく耳にしていましたが使用手順などを調るだけでインストールまでは至っていませんでした．

### 経緯
そんな中「3DモデルをClaude Codeで自動生成している」という話を友人から聞き，これは試してみねばと思い立ったという経緯です．

ちなみに，Claude Codeが出た当初，Gemini CLIというのがリリースされました．文字通りターミナル上で使用するGeminiで，Claude Codeなんかと使用感は同じです．
Gemini CLIが出てすぐにBlenderのモデル生成を試してみましたが，その時はとても実用に耐えれるものではありませんでした(かろうじて指示したオブジェクトと認識できるかどうか)．
それ故にモデル生成ができるレベルに進化していることに驚きを隠せません．

### Claude Codeの設定
Claude Codeには，全体に対して許可/拒否を指定する __.claude/settings.json__ と，各プロジェクト毎にルール等を決める.CLAUDE.mdがあります．
rm * やchmod -R 777といった，取り返しがつかなくなる可能性のあるコマンドはあらかじめ.claude/settings.jsonの方で実行拒否をしておきましょう．


# 手順
前置きが長くなりましたが，今回使用するのはClaude Code及びBlenderです．
- Blender 4.3
- Claude Code(Sonnet 4.6)

Blenderには，__Blender Python API__ というのがあり，Pythonスクリプトからモデル生成をすることが可能です([詳しくはこちら](http://qiita.com/youtoy/items/5e997f7b95f515832a65))．
Claude Codeでこのスクリプトを生成し，モデルにするというのが今回の流れです．


### 補足
Pythonスクリプトを生成できれば良いので，GeminiやChat GPT等のGUIでコードを生成し，モデル化することももちろん可能です．
が，今回はBlenderファイル化する所までを自動で行うという点でCLIを使用します．


# 試しに
試しに簡単なオブジェクトとして，椅子の生成を行います．
打ち込んだプロンプトは以下のものです．

``` Claude Code 
このフォルダではBlenderで3Dモデルを生成します．
そのためのPythonスクリプトを生成し，モデル化してください．
各オブジェクト毎に適当な名前のフォルダを作り，そのフォルダの中にPythonスクリプト及び
Blenderファイルは生成してください．

1人がけの椅子を作ってください．
```

実行した結果，PythonファイルとBlender，pngファイルが生成されました．
このpngファイルは，生成されたオブジェクトのレンダリングを行ったものです．基本的に必要ないかと思いますので，CLAUDE.mdでレンダリングは不要の旨を記述した方が良さそうです．

↓出力された画像
![preview.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3907649/aab0937d-4c07-46e7-95f5-d5fb51129b06.png)
__なんかバラバラになってる!?__
![preview2.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3907649/67f6199b-fccd-436d-808b-c01e2a45440e.png)
と思ったら修正されていました．

自動で何回か作り直してくれるみたい．
パーツがバラけているとか判定できるんですね．

ゲームの個人開発も，いよいよ本当に人の手がいらなくなってきていますね
