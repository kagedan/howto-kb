---
id: "2026-04-04-claude-codeの首位陥落codexがシェアno1へ-データで見る2026年3月のai-cod-01"
title: "Claude Codeの首位陥落。CodexがシェアNo.1へ。 ～データで見る2026年3月のAI Codingの動向まとめ～"
url: "https://qiita.com/kotauchisunsun/items/ab78bb338500b4c71103"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "Gemini", "qiita"]
date_published: "2026-04-04"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

# AI Coding Agentの2026年3月の動向

AI Coding.Infoというサイトを2025年7月から運営しています。

これは、Claude CodeやCodex CLI、あるいはGithub Copilot、Geminiなど、AI Coding Agentに関する利用動向をGithubのリポジトリの情報から定点観測するサイトです。  
AI Coding Agentの利用の判定として、以下のような条件で毎日調査を行っています。

* Githubの公開リポジトリを9,000リポジトリを毎日調査
  + プログラミング言語毎のGithub スター数のTOP 300
  + プログラミング言語は30種類から調査
* AI Coding Agent 16種類を対象
* 各種AI Coding Agentの利用するルールファイルがGithubリポジトリにある場合のみ、AI Coding Agentを利用していると判断

# 先月の動向

# AI Coding Agentの利用率は8.7%

**AI Coding Agentのリポジトリ利用率は8.7%** で、前回の7.3%から1.4%増加です。これはかなり速い速度で増えています。これも繰り返しになりますが、[2025年11月時点](https://qiita.com/kotauchisunsun/items/7b32a5f969a6322d66b4)で、全体の成長率はおおむね0.73%と見積もっていました。  
また、[2025年12月には2026年末に7.29～8.01%までの普及率である。という予測](https://qiita.com/kotauchisunsun/items/b11a628124ad3b4bb157)を出していました。それが、**2026年4月1日時点で8.7%になっているということは異常な成長が起こっています。**

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F275ebe55-cdcc-4f6b-ab30-340d278fe6d9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1949e17bed7e0c200dc8ee8b6a6089f7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F275ebe55-cdcc-4f6b-ab30-340d278fe6d9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1949e17bed7e0c200dc8ee8b6a6089f7)

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F3c863e5d-ae40-4e8c-afd8-819d29a067af.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6027082714882cc0520af9f7df6feca6)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F3c863e5d-ae40-4e8c-afd8-819d29a067af.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6027082714882cc0520af9f7df6feca6)

2026/4/1のAI Coding Agent利用率

2026/3/1のAI Coding Agent利用率

2026/3/1～2026/4/1までのAI Coding Agentを利用利しているリポジトリ数の推移

# AI Coding Agentのプロダクト別のシェア

プロダクト別のシェアは以下のようになっています。

| 順位 | 製品名 | シェア率 |
| --- | --- | --- |
| 1位 | Codex CLI | 34.1% |
| 2位 | Claude Code | 32.4% |
| 3位 | Copilot Agent | 19.0% |
| 4位 | Cursor | 6.3% |
| 5位 | Gemini CLI | 6.0% |

先月、

> Codex CLIの勢いが止まらない。1位のClaude Codeをシェア率で抜きそうなイメージがあります。 先月まではClaude CodeとCodexは4%の差がありましたが、今月になって0.7%の差しかありません。そのため、Codexが覇権をとるのも時間の問題。

と書きましたがまさにその通りになりました。 **Codexがシェア1位となりました。** 私は、まわりではClaudeCode派が多く、あまりCodexは見ない肌感があるので、割と違和感があります。Codexのカウント方法ですが、"AGENTS.md"のあるなしで判定しているので、もしかしたらCodexより別の要因でシェアが大きく見えている可能性は否定できません。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F92106f9c-c587-4029-892e-a1dddcf8970d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e3a05faf0cff89a455aa7feb2b2513f8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F92106f9c-c587-4029-892e-a1dddcf8970d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e3a05faf0cff89a455aa7feb2b2513f8)

2026/4/1のAI Coding Agentシェア率

2026/3/1のAI Coding Agentシェア率

# プログラミング言語別のAI Coding Agent利用状況

　一番AI Coding Agentが利用されているプログラミング言語は「TypeScript」、2番目が「Rust」、3番目が「Go」、4番目が「Python」、5番目が「C#」です。2月にはプログラミング言語のラインキングに大変動がありましたが、今月はそれほど大きくなかった。という印象です。3月にPythonが4位に転落したのは大きな衝撃がありましたが、2月までは2～4番目のRust・Go・Pythonはあまり差がありませんでした。しかし、3月になって、「Rust」が1つ頭抜けたかな。という印象があります。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F77fba80a-f513-4268-b1f7-df76bbf6c079.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5d90024335192d1640aa76916f9cdadb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F77fba80a-f513-4268-b1f7-df76bbf6c079.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5d90024335192d1640aa76916f9cdadb)

2026/4/1のAI Coding Agentのプログラミング言語別ランキング

2026/3/1のAI Coding Agentのプログラミング言語別ランキング

# AI Coding Agent利用リポジトリ数の1ヵ月の推移

2026/03/01時点でのリポジトリ数は1,008件だったのに対し、2026/04/01時点でリポジトリ数は1,234件となっています。154件の増加です。**1ヵ月で15%増加していることを考える** と、かなりハイペースで増加しています。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2Fed9b861c-8c7b-4de9-a2a5-7058c9771521.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a7ec7511b8cc4691eea5bc01ebdf2ca3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2Fed9b861c-8c7b-4de9-a2a5-7058c9771521.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a7ec7511b8cc4691eea5bc01ebdf2ca3)

2026/3/1～2026/4/1までのAI Coding Agentを利用利しているリポジトリ数の推移

# AI Coding Agent利用率が加速したきっかけは？

2025/12/01～2025/04/01までプロットを引いてみます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2Fb17a70cc-b458-4c2c-9013-012fd629882c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5cce0b15c716f91e1842db48408f6c64)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2Fb17a70cc-b458-4c2c-9013-012fd629882c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5cce0b15c716f91e1842db48408f6c64)

Go言語に関して、利用率は順当に上がっていっているように思います。一方で、RustやC++に関しては、少々恣意的ではありますが、2/12あたりを境に急増しているポイントがあるように思います。このあたりに何があったかのイベントを見てみると、

GPT-5.3-Codex-Sparkのリリースが2/12にありました。

GPT-5.4のリリースが3/5にありました。

そうすると、ある程度の説明はついて、GPT-5.3-Codex-SparkやGPT-5.4のリリースがあったために、RustやC++のAI Coding Agentの利用率が高まった。そして、「全体のAI Coding Agentの利用率が高まった」という仮説はあります。  
　この話は若干怪しい部分もあります。Rustに関しては、ClaudeCodeとCodexはかなり拮抗した状態がずっと続いています。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F451bbdbe-e52f-4d83-b6e2-ea4e0d3ae6ac.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=81be013463a8ca91be65d776013b00fd)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F451bbdbe-e52f-4d83-b6e2-ea4e0d3ae6ac.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=81be013463a8ca91be65d776013b00fd)

　一方でC++に関しては割と正しいのかな。と思っています。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F94a58f83-249a-46b4-bc3b-e69142f88715.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2627a9ac11b6f0540f215be3e8ca6319)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F139643%2F94a58f83-249a-46b4-bc3b-e69142f88715.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2627a9ac11b6f0540f215be3e8ca6319)

2025/12/01時点ではGithub Copilotが有意にありましたが、段々Claude Codeに食われていき、2026/2/20ぐらいからCodexが割合として増えていっていることが確認できます。そのため、「Codexの新モデルがC++を正確に書けるようになってきた」そのために「利用率が上がっていった」、それに伴って、全体のAI Coding Agentの利用率が高まっている。という感じがしています。  
　したがって、私の理解としては、プログラミング言語においてAI Coding Agentの利用率の高かったTypeScriptは、CodexとClaudeCodeでかなり拮抗した戦いをしている。しかし、今まで利用率の低かったC++のような言語でCodexが積極的に利用されるようになり、シェアをまくった。という考え方ができるように思います。

# 感想

　3月は異様にAI Coding Agentの利用率が加速した。1ヵ月であった。というのが私の感想でした。一方で、Claude Codeはどうなるのだろうか？と思うのが正直な感想です。ClaudeCodeとOpenAIを比べると、おそらくOpenAIの方が資金力はあり、強いモデルを作るには有利な状況にあるでしょう。Microsoftとのつながりもあり、GithubはMicrosoftの傘下にあります。そのため、Anthropicに比べて、コーディングに強いモデルを作る能力はあると推察できます。一方で、「OpenAIが力を入れるべきポイントはコーディング領域であるのか？」ということろには若干の疑問があります。どちらかというと、コーディング領域より、日常生活に溶け込むタイプのAIを作るほうが、彼らのミッションとしてはいいのではないか？とは思うことがあり、なぜここまで力を入れているのだろうか。というところに若干の疑問があります。  
　そして、もう1つ疑問があるのはGoogleです。Googleに関して、コーディング領域に対しGeminiにあまり力が入っていないように思います。しかし、これはある意味で納得する部分はあります。私の視点だと、「OpenAIは無駄にコーディング領域にAI投資をしすぎではないか？」というのに対し、「GoogleはGemini全体に投資をしているから、コーディングは一領域にすぎない。」と考えると、ここでシェアを大きくとることに意味を見出せないのかもしれません。一方で、スマホなどのビルトインで快適にAIを使えるほうに投資をしている。と考えると、そちらの方がパイは大きいので、合理的だと思います。  
　また、Github Copilotも、これほどシェアをとられて大丈夫なのか？と思う部分はあります。しかし、MicrosoftはOpenAIに投資をしていたり、Azureを通してOpenAIを使わせているので、最悪、OpenAIの買収もありうることを考えると、Microsoft陣営として、負けはない状況なのかな。と思う部分もあります。そのため、Github Copilotがシェアが低くても問題はない。という考えです。ただ、味方同士で領域を食い合っているので、無駄な戦いである。とは言えます。  
　最近、OpenClawの流れもあり、自立型のAgentも流行っていますが、Claude Codeもそういった方向に舵を取りつつある気がします。そういった部分で、また盤面が変わる気がします。今までは、そういった用途はMicrosoft Copilotなどが部分的に担ってきた部分ですが、Claude Codeが開発者だけのものではなくAgent化することで、ChatGPTのように生活に溶け込む未来もあるのかな。と思ったりします。
