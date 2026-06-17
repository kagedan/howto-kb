---
id: "2026-06-16-claude-designでスライドを作成する-01"
title: "Claude Designでスライドを作成する"
url: "https://zenn.dev/kameoncloud/articles/047983317aa43a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "zenn"]
date_published: "2026-06-16"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

<https://serverless.co.jp/blog/hhlo-duf9f/>  
に投稿した記事の微修正版です。

今日はClaude Design を使って、テクノロジーの解説用スライドを作成してもらいました。

#### Claude Design とは

Claude Designは、Anthropicが2026年4月にリリースした新しいビジュアル作成ツールです。デザインの専門知識がなくても、テキストで話しかけるだけで、プロトタイプ、スライド、ワンページャー、ワイヤーフレームといったビジュアル成果物を短時間で作れます。デザイナーはもちろん、プロダクトマネージャー、マーケター、創業者など、アイデアを素早く「見える形」にしたいすべての人を対象にしています。

#### どうやって使うのか

画面はシンプルな2ペイン構成です。  
![](https://static.zenn.studio/user-upload/e11b5f144343-20260616.png)

左側のチャット欄で「モバイルアプリのオンボーディング画面を4枚作って」と入力すると、右側のキャンバスにClaudeがデザインを生成します。最初の出力はあくまで出発点であり、チャットでの指示、キャンバス上の要素への直接コメント、テキストの直接編集、Claudeが自動生成するスライダーを使って細部を調整していきます。「もっとシンプルな配色にして」「ナビゲーションを上部に移動して」といった自然な言葉で反復できるのが特徴です。

#### 何が作れるのか

インタラクティブなプロトタイプ、UI・UXのワイヤーフレーム、ピッチデッキ、社内向けのダッシュボード、マーケティング用のランディングページなど、幅広いビジュアルコンテンツに対応しています。完成したデザインはCanva・PDF・PPTX・HTML形式でエクスポートでき、開発に進む準備ができたらClaude Codeへそのままハンドオフすることも可能です。

### さっそくやってみる

現時点ではClaude DesignはClaude Desktopでは利用が行えず  
<https://claude.ai/design>  
から利用が可能となっています。

このブログではAI Agent / MCP の解説用PPTを作成してみます。  
Slide deck  
タブからプロジェクト名を入力して Create をクリックします。  
![](https://static.zenn.studio/user-upload/922465ee157f-20260616.png)  
いきなりChatで指示を与えることもできますが、土台となる素材を提供することも可能です。  
![](https://static.zenn.studio/user-upload/b885a1687e06-20260616.png)  
例えば Add screenshot で以下の画像を提供してみます。  
![](https://static.zenn.studio/user-upload/bb3ef7e387cf-20260616.png)  
Send をクリックします。  
![](https://static.zenn.studio/user-upload/a1bf397cd713-20260616.png)  
スライド作成における質問が出てきますので回答していきます。  
![](https://static.zenn.studio/user-upload/a8011ee7fb98-20260616.png)  
![](https://static.zenn.studio/user-upload/16c6e55e5eb1-20260616.png)  
Continue をクリックするとスライドの作成が開始されます。  
しばらく待つとスライドが作成されます。  
右上の shareボタンをクリックするとエクスポートが可能です。  
![](https://static.zenn.studio/user-upload/7f49896e4686-20260616.png)  
例えば PPTX を指定するとさらに形式を指定できます。  
![](https://static.zenn.studio/user-upload/e50067084dda-20260616.png)  
試したところ Editable - universal fonts はだいぶデザインが崩れた状態で出力されてしまうため screenshot-bases PPTX がいいようです。ただしこの場合編集が行えなくなります。この辺りは今後の改善に期待です。

生成されたスライドに対して自然言語で修正指示を与えることも可能です。  
3ページ目の図を透明感ある形に変更 として指示を与えるとこのようになりました。  
修正前：  
![](https://static.zenn.studio/user-upload/27d9992edaf8-20260616.png)  
修正後：  
![](https://static.zenn.studio/user-upload/1f3402cc2b63-20260616.png)  
なお、このChatはデザイン作成専用ではなくClaudeと共通です。このためWebSearchを利用できるため調べ物を指示しそのままスライドにしてもらうことが可能です。

例えば 2026年4月24日のニュースを調べて1ページ目に追加して と指示を出すと1ページ目が以下の様に再生成されました！  
![](https://static.zenn.studio/user-upload/ddb6f93634e3-20260616.png)
