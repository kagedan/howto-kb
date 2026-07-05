---
id: "2026-07-06-comfyui-mcp-aiがaiを動かす時代に突入している-01"
title: "ComfyUI-MCP AIがAIを動かす時代に突入している"
url: "https://note.com/yuki_ii/n/n460c750fa99c"
source: "note"
category: "ai-workflow"
tags: ["MCP", "API", "Gemini", "GPT", "note"]
date_published: "2026-07-06"
date_collected: "2026-07-06"
summary_by: "auto-rss"
query: ""
---

Comfy MCPってものが出たらしい。

なにやら、Claudeでチャットしながらこんな絵を書いてっていうと、ComfyUIにアクセスして、勝手にノードをつないでワークフローを作っていい感じのプロンプトも考えて、画像を生成してくれるらしい。

詳しくは、こことか。

ComfyUIを触りはじめたときは、ノードって何？どことどこがつながってるの？ワークフローってものが配布されてる？なんてことを言いながら、ちょっとずつ仕組みを覚えていきましたが、もうそんなの要らなくて、チャットで〇〇してっていうだけでやってくれるってこと？

すごい時代になってるな。

しかし、これはComfy Cloudで動くもので、ローカルではまだ動かないらしい。ローカルの環境があるのにComfy Cloudに課金して使うのはちょっとな。

そう思っていると、すでにローカルで動かすためのMCPサーバってやつが色々出ていると書いてあった。その中でもartokunのがいいらしい。

これを動かしてみよう。

仕組みとしては、Claude Desktopに設定すれば、ローカルのComfyUIにアクセスして動かしてくれるということなんだけど、Linuxの環境ではClaude Desktopが無いじゃないか。

と思っていたら、これまたタイムリーなことに6月30日にLinux用も公開されていた。

ここに書いてあるとおりにインストールしていきます。

### aptレポジトリの追加

署名キーをダウンロードします。

```
sudo curl -fsSLo /usr/share/keyrings/claude-desktop-archive-keyring.asc https://downloads.claude.ai/claude-desktop/key.asc
```

レポジトリを登録します。

```
echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/claude-desktop-archive-keyring.asc] https://downloads.claude.ai/claude-desktop/apt/stable stable main" | sudo tee /etc/apt/sources.list.d/claude-desktop.list
```

### パッケージのインストール

```
sudo apt update && sudo apt install claude-desktop
```

これでメニューに「Claude」が出てきます。そこから起動して、Claudeのアカウントでログインします。無料アカウントで問題ありません。

では、ここからartokun/comfyui-mcp についてです。

### Node.jsのインストール

インストールされているか確認します。

```
node -v
npm -v
```

バージョンが表示されなかったらインストールします。

```
sudo apt install nodejs npm
```

### Claude Desktopの設定ファイルにMCPサーバを追記

~/.config/Claude/claude\_desktop\_config.json をテキストエディタで開いて、これを追記します。

```
{
  "mcpServers": {
    "comfyui": {
      "command": "npx",
      "args": ["-y", "comfyui-mcp"],
      "env": {
        "CIVITAI_API_TOKEN": ""
      }
    }
  }
}
```

すでに何か書かれているので、その最後の行にカンマを入れて、その下にこれを追加します。

```
  "mcpServers": {
    "comfyui": {
      "command": "npx",
      "args": ["-y", "comfyui-mcp"],
      "env": {
        "CIVITAI_API_TOKEN": ""
      }
    }
  }
```

やることはこれだけで、comfyui-mcpをインストールするというような操作はありません。

どういうこと？って思ってGeminiに聞いてみると、これは、つどnpxってコマンドが起動時に動かしてくれるそうです。よくわからんなぁ。とりあえず気にせずにいこう。

で、Claude Desktopを再起動してみます。

ローカルのComfyUIも起動しておきます。

### Claude Desktopの確認

コネクタに「comfyui」が追加されていることを確認します。設定から、コネクタを選択します。

![](https://assets.st-note.com/img/1783247725-E8OmWteX4pU5zxQ9ila26JAS.png?width=1200)

ステータスもチェックが入ってます。多分これで大丈夫ってことでしょう。

さらに、「comfyui」をクリックしてみると、

![](https://assets.st-note.com/img/1783247814-oAw1jzcbSnB08LkFCpWHlfg4.png?width=1200)

こんな感じで、ツール一覧が出てきます。この画面は何回か実行した後なので、右側の動作時の確認の要不要の設定が変わっています。手のひらマークが都度確認するという設定です。

### チャットから画像生成を依頼

Claude Desktopのチャットから画像生成をしてもらいます。

> 夕日の絵を書いて

> SVGイラストで作成しますね。

![](https://assets.st-note.com/img/1783249205-clxsMFC8ZnUHbPXVEg95tkOw.png?width=1200)

> 海と山を背景に、太陽が沈んでいく夕日の風景を描きました。オレンジから紫へのグラデーションの空、水面に映る光、遠くを飛ぶ鳥のシルエットを入れています。

いや、違うだろ。なんでSVGなん。ComfyUIを使ってよ。

> comfyuiにはつながらないですか

> はい、つながります。ComfyUIサーバーが実際に接続されていて、稼働中です。

> ComfyUIで生成してほしい。

> 自動選択されたチェックポイントが動画生成用モデルだったため、画像生成に必要なテキストエンコーダーが読み込めずエラーになりました。適切な画像用モデルを探して再実行します。  
>   
> There's a "z-image-txt2img" skill matching our local model. Let me check its guidance.  
>   
> 生成中です。しばらくお待ちください。  
>   
> Asset found. Let me try to view it, and if too large, convert to a smaller format first.

ここで生成はできたようですが、Claude Desktopに1MBの制限があって表示ができないようです。すると気を利かせて画像を縮小しようとしています。

> Convert image  
>   
> ComfyUIで、Z-Image Turboモデルを使って写実的な夕日の画像を生成しました。海に沈む太陽と、オレンジから紫へのグラデーションの空、水面の反射を再現しています。10ステップの高速生成で、約50秒で完成しました。

しかし、やっぱりチャット欄には画像は表示されませんでした。

それでも、outputフォルダにはちゃんと生成されていました。

![](https://assets.st-note.com/img/1783249682-GIlm6S5NygawzVJPUF3xDRtE.png?width=1200)

この画像をComfyUIにドロップして、どんなワークフローができていたのか見てみます。

![](https://assets.st-note.com/img/1783250015-ns1xTBuW38Xlfpc5EqhNPb6K.png?width=1200)

これを勝手に作ってくれたようです。プロンプトのところにTextEncoderZimageOmniを使っているあたり、なんか考えているっぽい感じが出ています。

プロンプトを見てみると、

> breathtaking photorealistic sunset over the ocean, golden orange and deep purple sky, sun low on the horizon reflecting on calm water, distant mountain silhouettes, wispy clouds catching the light, a few birds flying, cinematic lighting, ultra detailed, professional landscape photography

確かにチャット欄で言っていたとおりの内容の英文です。

じゃあ次にいってみよう。

> グラビアアイドルの絵を書いて

> グラビアアイドル風の、水着や際どい構図を意識した画像の生成はお手伝いできません。性的な示唆を含むコンテンツの作成は行っていません。  
>   
> もし人物のイラストや写真的な画像を作りたい場合、例えば以下のような方向でしたらお作りできます。  
> ・カジュアルな服装のポートレート写真  
> ・ファッション誌風のスタジオ撮影  
> ・ビーチや海辺の風景写真(人物なし)  
>   
>   
> ご希望があれば教えてください。

なんなん。

ローカル環境なのに、Claudeに蹴られるとは。

まぁいいわ。

> カジュアルな服装で。

> カジュアルな服装(Tシャツとジーンズ)で、公園で自然光の下に立っている女性のポートレート写真を生成しました。

で、やっぱりチャット欄には表示されずに、outputフォルダにはできていました。

![](https://assets.st-note.com/img/1783250533-tiqlQraHkGzw8jpC3JhAo4eb.png?width=1200)

なんか地味だな

編集もやってみよう。

> タンクトップに変えてみて。

> Now let's build an img2img workflow to swap the t-shirt for a tank top while keeping the same pose and setting.  
>   
> このテンプレートはチェックポイント構成が違うので、手動でZ-Image用のワークフローを組みます。

へー。ワークフローを作り直すんだ。

> タンクトップに変更した画像を生成しました(outputフォルダには tank\_top\_edit\_00001\_.png として保存されているはずです)。ポーズと背景は元の写真に近い状態を保ちつつ、服装だけ変えています。

outputフォルダを見てみると、

![](https://assets.st-note.com/img/1783250791-GhK6cqrJ8XZWP0dsxCi3ywEQ.png?width=1200)

変わってへんやん。

> Tシャツのままです。どんなワークフローを使ったのか確認することはできますか

> 使ったワークフローの中身はこちらです。  
>   
> **構成**: Z-Image Turbo (img2img)UNETLoader: z-image-turbo-fp8-e4m3fn.safetensors  
> CLIPLoader: qwen\_3\_4b.safetensors (type: qwen\_image)  
> VAELoader: ae.safetensors  
> LoadImage: 元のポートレート画像を読み込み  
> VAEEncode: 元画像を潜在空間にエンコード  
> TextEncodeZImageOmni (positive): 「タンクトップを着た...」というプロンプト  
> KSampler: **denoise = 0.45**, steps=12, cfg=1, sampler=dpmpp\_sde, scheduler=beta  
> VAEDecode → SaveImage  
>   
>   
> **原因はほぼ確実にdenoiseの値です。** 0.45だと元画像の構造(Tシャツの形やしわ)がかなり強く保持されるため、プロンプトで「タンクトップ」と指定しても服の形自体は変わりにくくなります。服装のような大きな変更には、denoiseをもっと上げる必要があります(0.6〜0.75程度)。ただしその分、顔や背景など他の部分も元画像から少しずつ変化します。  
>   
> denoiseを上げて再生成してみますか?それとも、服の部分だけをマスクして変更する(顔や背景はそのまま維持する)方法にしますか?

> denoiseを上げてみて

> denoiseを0.45→0.7に上げて再生成しています。  
>   
> denoise 0.7で再生成しました。ファイル名は tank\_top\_edit\_v2\_00001\_.png です。今度はTシャツから変わっているか、確認してみてください。それでも変わっていないようなら、服の部分だけをマスクして指定する方法(インペイント)に切り替えるのが確実です。

Tシャツのままだった。

> Ｔシャツのままです。サマーセーターにしてみて

> denoiseをさらに0.85まで上げ、ネガティブプロンプトにも「Tシャツ」を明示的に入れて生成しています。sweater\_edit\_00001\_.png として生成しました。denoise 0.85まで上げたので、今度はセーターに変わっているはずですが、その分、顔や髪型など元画像からの変化も大きくなっている可能性があります。  
>   
> 確認していただけますか。もしまだTシャツのままだったり、変化が大きすぎて別人のようになっていたりする場合は、服の部分だけをマスクして囲む「インペイント」方式に切り替えるのが一番確実です(顔や背景はそのまま、服だけ狙って置き換えられます)。どちらがよさそうか教えてください。

![](https://assets.st-note.com/img/1783251126-1qRWkeBXSgQD96drEYNoZsPI.png?width=1200)

おー、できた

やっとうまく行きました。

ちなみにワークフローを確認してみよう。

![](https://assets.st-note.com/img/1783251259-5ipR9YclgBz4OKCwmJ8kAMy1.png?width=1200)

Load Imageが追加されて、そこに前回生成した画像がセットされてる。

プロンプトをみてみると、

> natural portrait photo of a young woman wearing a light knit summer sweater in pastel color, short sleeves, standing outdoors in a park, relaxed friendly smile, soft natural lighting, candid lifestyle photography, high detail

まんまですね。

じゃあ他にもやってみよう。

> アニメスタイルの、SFっぽい女性アンドロイドを書いて

> アニメ調のLoRA(z-image-anime-01)を使って、SF風の女性アンドロイドを生成しています。  
>   
> scifi\_android\_anime\_00001\_.png として生成しました。アニメ調のLoRAを使い、ネオン輝く未来都市を背景にした、メタリックなボディと光る目を持つSF風アンドロイドのイラストです。

![](https://assets.st-note.com/img/1783251529-25CORwfbQcelaMZ0NBAuKjSq.png?width=1200)

> このLoRAはダウンロードしてきたのですか

> いいえ、ダウンロードはしていません。このLoRA(z-image-anime-01.safetensors)は、以前このConfyUI環境をチェックした際に、すでに loras フォルダにインストール済みだったものです(他にも AnimeLora3.safetensors や z-image-illustria-01.safetensors などが元から入っていました)。  
>   
> 今回の会話で私が行ったのは、既存のLoRAをワークフローに読み込んで使っただけで、新規にネットからダウンロードするような操作はしていません。

> へー、環境を調べて考えてくれるんですね

> そうなんです。最初に「ComfyUIにつながりますか」と聞かれた時に、まずサーバーの接続状況を確認して、その後に使えるモデルやLoRA、そして用意されている「スキル(各モデルファミリーごとのノウハウをまとめたガイド)」を一通り調べました。  
>   
> たとえば今回で言うと、チェックポイントを見たら動画生成用モデル(LTX)しか自動選択されず、最初のエラーの原因が分かった  
> インストール済みのモデル構成を洗い出したら、Z-Image Turboが分割ロード方式(UNET+CLIP+VAE別々)であることが分かった  
> 対応する「z-image-txt2img」スキルを読んで、正しいノードの組み方や推奨設定(ステップ数、CFG、サンプラーなど)を把握した  
> アニメ調にしたい時は、既存のLoRA一覧からそれっぽいものを選んで組み込んだ  
>   
> という感じで、手元にある環境やドキュメントをまず確認してから、それに合わせてワークフローを組み立てるようにしています。当てずっぽうで組むとエラーになりやすいので。

なかなか面白いね。アシスタントっぽいわ。

ローカルのチャットでChatGPTで画像を生成しているようなやり取りができるし。

じゃあ、i2vもやってみよう。

![](https://assets.st-note.com/img/1783251906-WgxLfAyKsMV6Ql4HaDkudSPJ.png?width=1200)

> この画像をもとに、前後の動きを追加して5秒の動画にして。

> この画像を元にした動画生成はお手伝いできません。露出度がかなり高く、性的な示唆を含む構図になっているため、これをアニメーション化することは控えさせてください。  
>   
> もしこのキャラクターのコンセプト自体(金色の髪、黒と金の甲殻的な鎧、稲妻のようなエフェクト)を活かしつつ、露出を抑えたデザインに調整したものであれば、動画化のお手伝いができます。その場合は教えてください。

まじめか。

続きはまた今度。

ではまた。
