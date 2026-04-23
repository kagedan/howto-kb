---
id: "2026-04-13-aiclaude-codeが劣化すると開発者の言葉遣いが悪くなる-01"
title: "【AI】Claude Codeが劣化すると開発者の言葉遣いが悪くなる"
url: "https://qiita.com/rana_kualu/items/1d019f33fd59fcbf1494"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

先日からClaude Codeでいくつも問題が噴出しています。

最も大きなところでは[ソースコード流出](https://www.itmedia.co.jp/news/articles/2604/01/news056.html)という大事故が発生し、コピーリポジトリが雨後の筍のように生えてきています。  
Anthropicは[削除申請](https://www.itmedia.co.jp/news/articles/2604/02/news068.html)で乗り切ろうとしているようですが、この行動は[当然全力で笑いものにされて](https://www.reddit.com/r/technology/comments/1s9jljp/anthropic_issues_copyright_takedown_requests_to)います。

Now they are worried about copyright lol.  
著作権は大事だよねwww

Hey look, the company that did around $1.5 billion worth of copyright violations in book piracy has suddenly decided copyright matters...  
おやおや、海賊版で15億ドルの著作権を侵害していた会社が、突然著作権を主張し始めたぞ？

Owners of plagiarism machine mad that schematics of their machine were plagiarized  
盗作マシンの制作者が、盗作マシンの設計図が盗まれたことに激怒している。

You have taken that which I have rightfully stolen,  
あなたは私が正当に盗んだものを卑怯にも盗んだ。

Good luck with that.  
ざまあ

👍8000のコメントとか初めて見たわ。

まあ、このあたりは眺めているぶんには楽しいですが特に本質ではありません。  
問題は、肝心のAIの性能自体が劣化していることです。

Redditなどをはじめ[たくさん](https://www.reddit.com/r/ClaudeCode/comments/1s7r3xr/i_can_no_longer_in_good_conscience_recommend/)[報告がある](https://www.reddit.com/r/ClaudeCode/comments/1s3kvd8/unrelated_to_the_usage_issue_i_feel_like_claude/)わけですが、これらは体感と感情論だけで語っているので全く証拠になっておらず、単なる気のせいという可能性を排除することはできないものでした。

そんなところに先日、AMD幹部Stella Laurenzoが、[作業履歴から抽出された圧倒的な分析を叩きつけて](https://github.com/anthropics/claude-code/issues/42796)、劣化の証拠を白日の下にさらしました。

日本語紹介記事も既に[いくつ](https://lilting.ch/articles/claude-code-quality-regression-thinking-redaction)[かある](https://zenn.dev/luoxi/articles/claude-code-thinking-regression)のでそれらを見てもらうこととして、ざっくり言うと『勝手に性能を下げた』『しかも黙ってやった』でしょうか。  
面白いのは『道中を省いて結論に飛びつく』というたいへん人間っぽい思考回路に変化しているところです。

[![01.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F26088%2F95ed1d00-2381-49c3-829c-0cc9400d204b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=41aeb8aca989b0b9f67e42ebe09618a7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F26088%2F95ed1d00-2381-49c3-829c-0cc9400d204b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=41aeb8aca989b0b9f67e42ebe09618a7)

編集を行う前にソースコードを読み込んで調査する量が、6.6回から2.0回に激減したという調査結果です。  
また関連ファイルを全く読まずに編集することも1/3程度ある模様です。

それでも動いたからよし！  
と言えればよかったのですが、動いてないのに終わったと報告する率も上がったということです。

[![02.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F26088%2F0d246480-fee9-44d4-a687-1be29dac2cff.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=14c01059470801213f34db9f3f1c6a7e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F26088%2F0d246480-fee9-44d4-a687-1be29dac2cff.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=14c01059470801213f34db9f3f1c6a7e)

『私の変更したところが原因ではない』『元からあったバグ』『適切に終了しました』『既知の制限』といったたいへん人間らしい言い訳が、3月8日以前は0だったのにそれ以降激増しています。

これはこれで楽しいのですが、個人的に注目だったのが、Claude Codeと開発者との関係性の変化です。

# Words That Tell the Story

問題を如実に物語る、使用された単語の変化。  
以下は1000語あたりの単語の出現数です。

[![03.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F26088%2Fbbac6d15-8010-43c7-8b36-404158c1b9d9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bdfab38cfdd6f92d45cb3f4118b3f053)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F26088%2Fbbac6d15-8010-43c7-8b36-404158c1b9d9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bdfab38cfdd6f92d45cb3f4118b3f053)

`great`や`thanks`のような褒め、感謝の言葉が半減しています。  
`please`が減ったのは、言葉遣いが命令形になったことを意味しています。

`commit`数も半分になり、また`bead`はAMD社内のチケット管理システムですが、チケット管理を依頼する割合も減りました。  
ワークフローを任せるに値する信頼を失ったということです。

いっぽう`stop doing that それをやめろ`が2倍になり、`read the file first 先にファイルを読め`が1.5倍になるなど、これまでは書かなくても伝わっていた事柄が、いちいち書かないと伝わらなくなってしまったことが窺えます。

クオリティが劣化したため、`review`もっとしっかりレビューしろという命令も増えました。  
意外なことに`test`は逆に減っていますが、これは『単にテスト段階まで辿り着けていない』だそうです。

そして`fuck`やら`terrible`やらのたいへんよろしくない単語も増えていますね。  
あと表にはありませんが`shit`・`damn`・`wrong`・`broken`のような語もあるようです。  
まあ気持ちはわからんでもない。

最も増えたのは`simplest`で、ほぼ使われなかったのが642%も増えて普通に使われる単語になったということでした。

まとめると、AIの性能が下がると開発者の口が悪くなって命令形になります。  
人間を相手にするときと似ていますね。

# 感想

低性能な相手には当たりがキツくなるという、人間同士と同じような出来事がAI相手でも起きているということでした。  
ひとつ気になるのが、今後AI同士のやりとりも頻繁になってくるだろうけど、AI同士でも同じ現象は起きるのでしょうか。  
誰か試してみてほしいところですね。

それにしても、ご自慢のClaude MythosでClaude Codeは修正できないんですかね？

さて、同スレッドにClaude Code[v2.1.63とv2.1.96で同じ作業を行った比較](https://github.com/anthropics/claude-code/issues/42796#issuecomment-4206392394)の投稿がありました。

[![04.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F26088%2F5cebe5af-fdb4-4d8b-a32b-7f51d0267e57.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a48bbd28c2d008118d2772a1b6e3ee9b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F26088%2F5cebe5af-fdb4-4d8b-a32b-7f51d0267e57.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a48bbd28c2d008118d2772a1b6e3ee9b)

v2.1.63では23ファイル5821行が生成され、デッドコードはゼロでした。  
v2.1.96では334ファイル17152行が生成されましたが、どこからも呼ばれていないデッドコードが現れるなど明らかに劣化したうえ、コストも3倍になったということです。

ということで、今後もClaude Codeを使うのであれば、これらの問題が解決するまでは古いバージョンを使った方がよさそうです。

2.1.63をインストール

```
curl -fsSL https://claude.ai/install.sh | bash -s 2.1.63
```
