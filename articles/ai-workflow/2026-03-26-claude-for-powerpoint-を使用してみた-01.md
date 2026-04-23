---
id: "2026-03-26-claude-for-powerpoint-を使用してみた-01"
title: "Claude for PowerPoint を使用してみた"
url: "https://qiita.com/Pyonaya/items/cd8edcd3adb23dc00d51"
source: "qiita"
category: "ai-workflow"
tags: ["GPT", "qiita"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

どんどん進化するAI。  
もはや仕事でもプライベートでも、AIを使用しないと成り立たないくらい頼り切ってしまっている。どのAIが一番よいのか、情報は刷新されつづけ、追いつくのに苦労する日々である。

いままでChatGPTをメインで使用していたが、claudeの拡張機能がどんどん進化していて、  
・wordやpowerpointで拡張機能としてclaudeを使用できる  
・codingの際にVS code上でclaudeを拡張機能として使用できる  
らしいということがわかり、（2026-03-26現在）claudeの汎用性が非常に高く、コスパもよさそうだという風潮になってきている感じである。

いままではchatGPTに課金して文章タスクに使用、claudeはコーディングで使用するという使い分けをしていたが（ただしくはVS codeのcopilotに課金してでAI選択をsonnet(claudeのAI機能の一つ)を使用すること）、これはもう、claudeのみに絞っていいのかなとおもってきた。  
あまり、claudeを使用してこなかったので、claudeになれていないという点で不安だが、思い切って１年の有料プランに課金してみたのでいろいろと試してみようと思っている。

まず、powerpointのアドイン機能でclaudeを使用できる、Claude for PowerPointをやってみたので、備忘録として記録する

＊この機能を使用するには、pro以上が必要なので、claudeの有料プランに課金しないとできないことに注意

### Claude for PowerPointのセットアップ

下記サイトにアクセス  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F09085ece-2726-47e7-9ab6-863836c659c7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=99d4dbb70b1a57bcfe7e1f09ddb94db6)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F09085ece-2726-47e7-9ab6-863836c659c7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=99d4dbb70b1a57bcfe7e1f09ddb94db6)  
<https://support.claude.com/ja/articles/13521390-claude-for-powerpoint-%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B>

ガイドにそって、Microsoft Marketplaceに移動し、Claude by Anthropic for PowerPointを開く  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F6c4e85cd-0ca7-4cc4-b363-eac2d3b0a19f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6d5e6549a8e077b30f3c9b5573ec853e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F6c4e85cd-0ca7-4cc4-b363-eac2d3b0a19f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6d5e6549a8e077b30f3c9b5573ec853e)

Claude by Anthropic for PowerPointをセットアップできたら、パワポを開く画面になるので、開くと下記の画面がでて、

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F5f1772a5-2cf3-419c-a0e7-49fca8706a0e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2f21d07303391ea2d596d92d77d462eb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F5f1772a5-2cf3-419c-a0e7-49fca8706a0e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2f21d07303391ea2d596d92d77d462eb)

Add-inのClaude by Anthropic for PowerPointのAddを押すと、  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F2d9c6ad5-8d28-49df-b6a5-7f37be26841a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c3d5591da0c4c31834e89c6b7b3505d9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F2d9c6ad5-8d28-49df-b6a5-7f37be26841a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c3d5591da0c4c31834e89c6b7b3505d9)

右側にclaudeのプロンプトを入れるタブが出現し、claudeにログインすることで、パワポ内でclaudeの使用が可能になる！！

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2Fac056d62-34d0-4217-91ad-e7ffa96e876b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0da04fd70682eddc26295560eebb4b01)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2Fac056d62-34d0-4217-91ad-e7ffa96e876b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0da04fd70682eddc26295560eebb4b01)

### Claude for PowerPointでできること

主な機能は以下の通り

＊claude web siteより引用  
<https://support.claude.com/ja/articles/13521390-claude-for-powerpoint-%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B>

テンプレートから構築する  
既に読み込まれているクライアントまたは企業テンプレートから始めます。必要なものを説明すると、Claude はスライド マスターから正しいレイアウト、フォント、色を使用してスライドを生成します。Claude はデッキのテンプレートを読み取り、そのフォーマット ルールを尊重します。

プロンプトの例：

「市場規模セクションを作成してください—TAM、SAM、SOM をカバーする 3 つのスライドと補足ビジュアル」

「1 列のコンテンツ レイアウトを使用してエグゼクティブ サマリー スライドを追加してください」

既存のスライドを編集する  
スライドを選択し、Claude に変更内容を伝えます。Claude はフォーマットと周囲のコンテキストを保持しながら編集を行います。

プロンプトの例：

「このスライドのテキストを簡潔にしてください」

「四半期ごとのトレンドを示すグラフを追加してください」

「スライド 4～7 のストーリーラインを再構成してください」

デッキ全体を生成する  
空白のデッキを開き、目標を説明します。Claude は論理的な構造とプロフェッショナルなデフォルトを備えたドラフトを作成し、その後、そこから改善できます。

プロンプトの例：

「市場参入の仮説を説明する 10 スライドのデッキを作成してください」

「タイムラインと次のステップを含む内部プロジェクト更新プレゼンテーションを作成してください」

ネイティブ グラフと図を作成する  
箇条書きをプロフェッショナルなビジュアル（図、プロセス フロー、または編集可能なネイティブ PowerPoint グラフ）に変換します。Claude は静止画像ではなく、直接編集できるビジュアルを生成します。

プロンプトの例：

「これらの箇条書きをプロセス フロー図に変換してください」

「Q1～Q4 のパフォーマンスを比較する棒グラフを作成してください」

テンプレート認識  
Claude はデッキ内のスライド マスター、レイアウト、フォント、カラー スキームを読み取り、スライドを生成または編集するときにそれらを使用します。ブランドに外れた要素を導入することなく、テンプレート準拠を維持することを目指しています。

コネクタのサポート  
他のツールを接続して、デッキ内にあるもの以上のコンテキストを Claude に提供します。コネクタが有効になっている場合、Claude はコンテンツを生成または改善するときに、接続されたツールからの情報を利用できます。

ツールを接続するには、Claude サイドバーを開き、コネクタ アイコンを選択して利用可能なオプションを確認します。

カスタム コネクタはセキュリティ リスクをもたらす可能性があります。有効にする前に、リモート MCP を使用したカスタム コネクタの開始を確認して、考慮すべき事項についてのガイダンスを参照してください。

PowerPoint でスキルを使用する  
Claude 設定で有効にしたスキルは、Claude for PowerPoint アドインでも利用できます。Claude は作業中に関連するスキルを自動的に適用します。個別に呼び出す必要はありません。

サイドバーで / を入力して、利用可能なスキルを確認し、直接選択することもできます（例：/deck-check）。PowerPoint に関連しないスキルはこのリストから除外されます。

スキルの有効化と管理の詳細については、Claude でスキルを使用するを参照してください。

永続的な指示を設定する  
アドイン サイドバーの 指示フィールドを使用して、PowerPoint のすべての会話に適用される設定を行います。指示は、ブランド ガイドライン（例：「常に 1 行の箇条書きを使用する」または「ハイライトに青いアクセント カラーを使用する」）、推奨スライド構造、または Claude がワークフローについて知っておくべき繰り返しのコンテキストなどに役立ちます。

PowerPoint で設定した指示は PowerPoint にのみ適用されます。Excel で設定した指示とは別です。

コンテキストとセッション管理  
自動圧縮：より長い会話を新しい会話に自動的に圧縮して、コンテキストが不足するのを防ぎます。

上書き保護：誤ったデータ損失を避けるため、Claude は既存のデータを上書きする前に警告します。

注：Claude for PowerPoint の使用は、既存の Claude アカウントに関連付けられており、同じ使用量制限の対象となります。

試しに、既存の日本語スライドを英語スライドに変えるプロンプトをいれてみた。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F549a12aa-d64c-4695-9616-34a127cb977e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3a134364a3a112e7e685824275e37b9f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3817969%2F549a12aa-d64c-4695-9616-34a127cb977e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3a134364a3a112e7e685824275e37b9f)

結果として、元のフォーマットが崩されることなくタイトルや内容含め、良い感じに英語スライドに変換された。

ただ、パワポ内に挿入されている図の日本語を英語に変えるということはできない様。  
そこは画像のみclaudeになげて、英語にしてもらうなどの個別の対応が必要そうだった。

### まとめ

結果としてClaude for PowerPointは、パワポ上で操作ができるという点でかなりつかえようなものだとわかった。  
今後は、google Drive上で、google docやgoogle pptxでもclaudeが使えるかを試していきたい。
