---
id: "2026-07-15-sugurukun-ai-blenderをcodexやclaude-codeに-丸ごと操作させるbl-01"
title: "@SuguruKun_ai: BlenderをCodexやClaude Codeに 丸ごと操作させる「blender-mcp」がすごいな... htt"
url: "https://x.com/SuguruKun_ai/status/2077300443831828964"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "GPT", "Python", "x"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

BlenderをCodexやClaude Codeに
丸ごと操作させる「blender-mcp」がすごいな...
https://t.co/N8f17ZbI2W
仕組みはシンプルで、Blenderの中にソケットサーバを立てて、そこにClaudeが直接コマンドを流し込む。チャットで指示すると、AIが書いたPythonがBlenderの中で実行される
ㅤ
できることが結構広い：
① モデリング（形を作る・変形する）
② マテリアルと色の設定
③ ライティングとカメラ配置
④ Cyclesのレンダ設定〜画像出力
⑤ シーン情報の読み取りとスクショ（AIが自分で画面を確認して直す）
⑥ Poly HavenやSketchfabから素材を取ってくる
ㅤ
セットアップは3つだけ：
・brew install --cask blender
・GitHubのhttps://t.co/Xlcn0kjQnBをBlenderに入れる
・Claudeを繋いで「浮遊するMacBookを作ってレンダして」と言う
ㅤ
3Dソフトって学習コストが一番の壁だったのに、そこがまるごと飛ばせるようになってる。元動画はCursor（GPT-5.6 Sol）でやってる例で、これを見て自分でも試しました👇🧵

自分でもClaude Codeでやってみたら、本当にBlenderを一回も触らずにこれが出てきた
ㅤ
2枚目、初回セットアップの画面が出たままなのに裏でシーンが組み上がってて笑った。クリックすらしてない https://t.co/B2zXj8svPv

ただ1発では出なくて、最初はこれ。カメラがずれてて画面も見切れてる
ㅤ
「画面が隠れてる」「スクリーンをもっと大きく」って日本語で言うだけでだんだん直っていって、4回目で1枚目の絵になった。Blenderの知識ゼロのままいけたのが正直びっくり...
ㅤ
リポジトリ: https://t.co/fmaneUNyqw https://t.co/2EN8haYFEy
