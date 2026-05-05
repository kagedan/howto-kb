---
id: "2026-05-04-予測不能にai-codingの利用が加速する-データで見る2026年4月のai-codingの動向ま-01"
title: "予測不能にAI Codingの利用が加速する ～データで見る2026年4月のAI Codingの動向まとめ～"
url: "https://qiita.com/kotauchisunsun/items/2244cfc243afb54749a6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "qiita"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

# AI Coding Agentの2026年4月の動向

AI Coding.Infoというサイトを2025年7月から運営しています。

https://ai-coding.info/ja

https://x.com/AICodingInfo
 
 これは、Claude CodeやCodex CLI、あるいはGithub Copilot、Geminiなど、AI Coding Agentに関する利用動向をGithubのリポジトリの情報から定点観測するサイトです。
AI Coding Agentの利用の判定として、以下のような条件で毎日調査を行っています。

- Githubの公開リポジトリを9,000リポジトリを毎日調査
  - プログラミング言語毎のGithub スター数のTOP 300
  - プログラミング言語は30種類から調査
- AI Coding Agent 16種類を対象
- 各種AI Coding Agentの利用するルールファイルがGithubリポジトリにある場合のみ、AI Coding Agentを利用していると判断

# 先月の動向

https://qiita.com/kotauchisunsun/items/ab78bb338500b4c71103

# AI Coding Agentの利用率は10.0%

**AI Coding Agentのリポジトリ利用率は10.0%** で、前回8.7%から1.3%増加です。**2026年の1月から1%ずつ利用率が増えている。という驚異の速度で浸透が進んでいます。**
[2025年12月時点](https://qiita.com/kotauchisunsun/items/b11a628124ad3b4bb157)では、まだ1ヵ月の利用率の増加分が0.5%だったのですが、それ以降、常に1%を超える増分で利用率が上昇しています。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/d220731f-716b-41e9-b71f-35bbe01b7562.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/92f5b2dd-0e3c-4e04-99a1-25f3907855db.png)

2026/5/1のAI Coding Agent利用率

https://ai-coding.info/ja?date=2026-05-01#adoption-rate

2026/4/1のAI Coding Agent利用率

https://ai-coding.info/ja?date=2026-04-01#adoption-rate

2026/4/1～2026/5/1までのAI Coding Agent利用率の推移

https://ai-coding.info/ja?date=2026-04-01&since=2026-04-01&until=2026-05-01#share-trend

# AI Coding Agentのプロダクト別のシェア

プロダクト別のシェアは以下のようになっています。

| 順位 | 製品名 | シェア率 |
|:---:|:------:|--------:|
|1位 | Codex CLI | 35.1% |
|2位 | Claude Code | 32.8% |
|3位 | Copilot Agent | 18.0% |
|4位 | Gemini CLI | 5.8% |
|5位 | Cursor | 5.8% |

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/4c91fab4-363d-4fa8-bab7-b6a8c9069b38.png)

全体の雰囲気としては変わっていないかな。という印象です。今月もCodexが1位、Claude Codeも2位、Copilotが3位と安定した動きをしています。
ただ、この3つに収斂、もしくは上位2つのプロダクトに収斂している感じはあり、2026年3月時点で、Cursorの利用率は11.0%、Geminiが6.6%でした。今月、GeminiとCursorは入れ替わっており、初めてGeminiが4位になりました。ただ、この話も難しく、どちらかと言うとCursorの利用率がだんだん減ってきており、Geminiが堅調である。という見方の方が正しいのかもしれません。Copilotも3位にはいますが、先月が19.0%のシェアであったことを考えると、微減、もしくは踏みとどまっている。という形でしょうか。

2026/5/1のAI Coding Agentシェア率

https://ai-coding.info/ja?date=2026-05-01&since=2026-04-01&until=2026-05-01#agent-share

2026/4/1のAI Coding Agentシェア率

https://ai-coding.info/ja?date=2026-04-01&since=2026-04-01&until=2026-05-01#agent-share

# プログラミング言語別のAI Coding Agent利用状況

　一番AI Coding Agentが利用されているプログラミング言語は「TypeScript」、2番目は「Python」、3番目は「Rust」、4番目は「Go」、5番目は「C#」です。以前まで、Pythonは2位に安定したポジションがありました。しかし、[今年の2月以降](https://qiita.com/kotauchisunsun/items/8ff87803193ff448f4eb)、それほど、GoやRustと差がなくなってきていました。そのため、今回はたまたまPythonが2位に戻ってきた。という印象があります。そのため、「Python」、「Rust」、「Go」はAI Coding Agentの利用数としては拮抗が続いている。という印象があります。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/5029a513-989e-4ffb-ab7f-f5a578a000a4.png)

2026/5/1のAI Coding Agentのプログラミング言語別ランキング

https://ai-coding.info/ja?date=2026-05-01&since=2026-04-01&until=2026-05-01#language-agent-rank

2026/4/1のAI Coding Agentのプログラミング言語別ランキング

https://ai-coding.info/ja?date=2026-05-01&since=2026-04-01&until=2026-05-01#language-agent-rank

# AI Coding Agent利用リポジトリ数の1ヵ月の推移

2026/04/01時点では1,234件だったリポジトリ数が、2026/05/01時点では1,436件となり、AI Coding Agentを利用しているリポジトリは202件増加しています。先月が、154件の増加であったことを考えると、さらに利用数が増えているということが分かると思います。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/3b531e72-70b9-4a1a-bb5d-4adbc1de9d4a.png)

2026/4/1～2026/5/1までのAI Coding Agentを利用利しているリポジトリ数の推移

https://ai-coding.info/ja?date=2026-04-01&since=2026-04-01&until=2026-05-01#time-based-bar-chart

# 長期予測との強烈な乖離

2025年12月31日に記事を公開しました。

https://qiita.com/kotauchisunsun/items/b11a628124ad3b4bb157

この時に、2025年7月1日から2025年12月31日までのデータをフィッティングして、 **2026年のAI Coding Agentの利用率の予測** を行いました。その時は、以下のような結果でした。関数を以下のように定義し、AI Coding Agent全体の利用率に対してフィッティングを行いました。

```math
y(t) = \frac{K}{1 + Ae^{-B(t-t_0)}}
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/9b32cc3e-249e-4138-94d7-4d757b6e79b7.png)

結果は以下のようになりました。

```
K = 7.7575e-02
A = 2.8346e+00
B = 9.6907e-03
t0 = -4.4439e+00
決定係数 (R^2) = 0.9852
σ: 0.0012
```

2026年末まで予測線を引くと以下のようになりました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/3bd3f7f8-3a32-4abb-a7da-75703acba506.png)

その時には、

**2026年末のプログラミング言語全体のAI Coding Agent利用率は、7.29～8.01% と予測できます。**

と結論付けました。ですが、**今月のAI Coding Agentの利用率は10.0%でした。完全に予測を外しています。** ここから、

**2026年にAI Coding Agentの利用の構造変化が起きた。**

といえるかもしれません。
　ここは難しいのですが、大きく2つ論点があると思います。1つ目の論点は、「そもそも予測式が間違ってる」ということです。年末にはロジスティック曲線によるフィッティングを行っていました。しかし、これがそもそも間違っている可能性がある。ということは否めません。ただ決定係数が0.98あったので、"予測時点では"、それほど悪いモデルではなかったと認識しています。(また、本質的にこのような長期予測は難しいという問題はあります。)
　これは3月の記事に書きましたが、ある一時期において特定言語でAI Coding Agentの利用率が激しく上昇していました。
 
 https://qiita.com/kotauchisunsun/items/ab78bb338500b4c71103
 
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/1d6bc58c-311b-49b3-9176-23beee4474e9.png)

この3月の記事では、Codexのリリースが原因ではないか。と結論付けていました。
12月の記事に話を戻すと、この時に、複数のプログラミング言語における利用率のフィッティングも行っておりました。この時の値と現在の利用率を比較します。

|     言語   | 上限予測利用率(K)  |    利用率(5/1時点)  |
|:---------:|------------------:|------------------:|
| TypeScript|            100.0% |            46.0%  |
| Python    |           100.0%  |             23.0% |
| Rust      |          13.4%    |             27.3% |
| Go        |          12.4%    |             25.4% |
| C#        |          12.3%    |             20.2% |

　TypeScriptやPythonは極限まで行くと100%の利用率になる予想でした。しかし、Rustに関しては上限値の予測でも13.4%でした。しかし、Rustは、5/1時点でほぼ倍以上の利用率の27.3%になっています。他の言語においても、上限値の倍程度の利用率が現在の利用率として観測されています。3月の記事で、Codexのリリースの影響を受けたであろう言語は、Go, C++, Rustとしており、そのため、AIの利用率に大きな変動があった。と結論付けていました。その変動時期は2026年2月16日ごろでした。もともとの予測は2025年12月31日までのデータまでしかなかったため、このような突発的な利用率上昇は予測できなかった。とは考えられます。したがって、「当たらないのが正しい」のですが、たぶん納得はされないと思います。
　TypeScriptとPythonに関しては12月の予測が比較的当たってるかな。と思っています。

 ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/faf56267-37c1-4a00-8da9-c6341907f4db.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/139643/e09845b3-b4ab-4c9c-99f0-21c3ed5e7097.png)

　グラフを読み解いてもらえば分かると思いますが、TypeScriptでのAI Coding Agent利用率は4/18時点で37～42%ぐらい。Pythonに関しては、16%～24%ぐらいです。そう考えると、5/1時点の値は、そこまで外していない。という感触があります。これに関しても説明がついて、「そもそもTypeScriptやPythonに関してはAI Codingの利用が非常に進んでいた。」と言えます。そのため、Codexのリリースがあっても、置き換えなどは進んだかもしれませんが、大きく利用率へは影響がなかった。と言えるかもしれません。むしろ、RustやGoのように「AI Codingの利用が少なかった言語」が今年のリリースにおいてインパクトを残し、予測が外れている主要因になっている。と考えることが出来ます。

# 感想

　AI Coding Agentの利用率の動向を毎月報告していますが、昨年末に予測した内容とズレが大きくなってきたな。というのが肌感としてありました。先月の時点で全体の利用率が8%を超え始めたので、これは考えを改めないとな。そのため、改めて振り返りと原因の探求をした回でした。
　振り返りをやってみた結果として、あーあやっぱり未来予測は難しいね。という感想もありましたが、TypeScriptやPythonに関しては、思ったより精度よく予測できていたな。というのは驚きがありました。今回、フィッティングに時間が取れなかったので、再予測をしませんでしたが、AI Coding.Infoの機能の1つとして、こういった利用率の予測値を出してもいいのかな。と、少し思った次第でした。
  また、昨今の話題では、Claude MythosやGPT 5.5の発表がありました。

https://forbesjapan.com/articles/detail/95537

https://openai.com/ja-JP/index/introducing-gpt-5-5/

Mythosに関しては、あまりに賢すぎて危険なために公開が止められた。などの話もありました。今、Codexがシェア1位になった。というのが、AI Coding.Info的な見解ではありますが、こういったClaudeの動きも今後のシェアにどう影響を与えてくるのかも注目する必要がありそうです。
