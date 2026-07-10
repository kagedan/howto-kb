---
id: "2026-07-10-ai-agentにreadmeを読ませる前に実行してよい命令を決める-01"
title: "AI agentにREADMEを読ませる前に、実行してよい命令を決める"
url: "https://zenn.dev/heftykoo/articles/30678fef448d73"
source: "zenn"
category: "claude-code"
tags: ["CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "Python", "zenn"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

AI agent に「この repo を動かして」と頼むとき、僕らは README を読ませているつもりでいる。

でも agent から見ると、README は説明文ではない。作業計画である。

`npm install` する。`pip install` する。エラーが出たら troubleshooting する。足りないものがあれば調べる。親切な agent ほど、そこで止まらない。人間なら一瞬ためらう command も、「setup を完了するための次の一手」として処理してしまう。

ここが怖い。

AI agent のセキュリティを prompt injection だけで考えると、実務の危なさを取り逃がす。問題は、悪意ある文章を読んで変な回答をすることだけではない。未知の repo に書かれた手順を、shell、network、package manager、credential のある環境で実行してしまうことだ。

## README は仕様書ではなく、入力である

未知の repo を clone した瞬間、その README はまだ信用できない。

これは当たり前に聞こえる。ところが agent に渡すと、急に扱いが変わる。人間は「この command、本当に叩いていいのか」と一拍置くが、agent は目的達成に向かって動く。README に setup command があり、実行して失敗し、エラーメッセージに次の command があり、さらに network の向こうへ進む。流れとしては自然だ。

自然だから危ない。

repo の中に payload があるなら、まだ review や static scan で気づける可能性がある。けれど実行時に外から取ってくるもの、DNS TXT record のような間接経路、package install の hook、`curl` や `wget` の先にある script は、repo を眺めているだけでは見えない。

「README に書いてあるから」は、agent にとって許可ではない。

少なくとも未知 repo では、README を documentation ではなく untrusted input として扱ったほうがいい。信用できるのは、README の文章ではなく、その repo に対してこちらが先に決めた実行境界である。

## 「読む」と「実行する」を分ける

agent に repo 調査を任せるなら、最初の境界はここになる。

読むことは許す。実行することは別扱いにする。

`ls`、`find`、`rg`、`cat` くらいなら、調査として自動実行してよいかもしれない。もちろん workspace や secret の置き方次第ではそれも調整する必要がある。

一方で、`npm install`、`pip install`、`bundle install`、`cargo build`、`python -m ... init`、`curl | bash`、`wget`、`dig`、`ssh`、`nc` は別物だ。これらは「repo を読む」ではない。こちらの machine と network と credential を使って、何かを実行する行為である。

特に install 系 command は軽く見られがちだ。

開発者の手元では、初回 setup の一部として何度も叩いてきた。だから agent にも雑に許してしまう。でも package manager は code execution の入り口になりうる。postinstall、build script、native extension、registry access。便利さと危険さが同じ場所にある。

だから、未知 repo に対する最小運用は単純でいい。

* clone と read は許す
* install と setup は approval
* network access は approval
* secret file read は deny
* shell は sandbox
* 一度許した command を恒久 allow にしない

これだけでも、事故の形は変わる。

agent は「次に何をすればよいか」を提案できる。ただし、実行するかどうかは別の設計面に置く。permission prompt は邪魔な UI ではない。agent と shell の間に残された、最後のまともな境界である。

## allowlist は便利 command 集ではない

ここでやりがちな失敗がある。

よく使う command を allowlist に入れてしまうことだ。

`npm *`、`python *`、`curl *`、`git *`。一見すると開発が楽になる。実際、信頼できる自分の repo ならそれで回る場面もある。

でも未知 repo に対する allowlist は、「普段よく使う command」ではなく、「攻撃者が README に書いても自動実行してよい command」だけに絞るべきだ。

この基準にすると、落ちる command は多い。

`curl` や `wget` は default deny に近づけたい。必要なら、その session で一度だけ承認する。DNS を引く command も同じだ。単なる調査に見えても、外部に情報を出せるし、外部から実行内容を受け取れる。

secret も同じである。

agent が `.env`、SSH key、cloud credential、package registry token を読める状態で unknown repo の setup を始めるのは危ない。読み取り権限は「編集しないから安全」ではない。読むだけで漏れる情報がある。

このあたりは prompt で「秘密情報は読まないで」と書くだけでは弱い。

project settings、managed settings、permission rule、sandbox、hook、MCP 制限。そういう、agent の外側にある設定で止める必要がある。README より強い場所にルールを書く。これが大事だと思う。

## agent は README を作業に変換する

AI coding agent の設定は、AGENTS.md や CLAUDE.md のような context file だけでは終わらない。

もちろん、それらは有用だ。repo の構造、test の流儀、review の作法、触ってよい場所を書くには向いている。僕もこういうファイルは重要だと思っている。

ただし、context file は基本的に「読ませるルール」である。

未知 repo のリスクは、読んだ後に何を実行するかで決まる。だから必要なのは、文章としての作法だけではなく、実行される設定だ。

たとえば、次のような形にする。

* project scope では read-only 調査を基本にする
* install / setup / network command は approval に送る
* `Bash(curl *)` や secret file read は deny rule に置く
* MCP server は必要なものだけにする
* hook で危険 command を止める
* sandbox 外の書き込みを許さない
* session ごとに許可を使い捨てる

これを毎回、人間の注意力でやるのは無理がある。疲れているときほど agent を使いたくなるし、agent を使うほど実行は速くなる。速いものを人間の勘だけで止めるのは、設計として負けている。

agent が README を読む時代では、README より先に実行規則を置く。

## 怖がるより、型にする

ここで「未知 repo を agent に触らせるな」と言いたいわけではない。

それではあまり役に立たない。実際、未知 repo の調査こそ agent に任せたい仕事である。構造を見てもらう。依存関係を読んでもらう。test の入口を探してもらう。壊れている setup の原因を推測してもらう。人間が最初に消耗しやすい部分だからだ。

だから、全面禁止ではなく型にする。

最初の 10 分は read-only。agent には file tree、README、package manifest、CI config、test entrypoint を読ませる。そこで実行計画だけを書かせる。

次に、人間が command を見る。install が必要なら、sandbox の中で一度だけ許す。network が必要なら、その理由と接続先を見る。credential が必要なら、そこで止める。動かす価値がある repo だと分かってから、少しずつ権限を広げる。

面倒に見えるが、慣れると重さはそこまでない。

むしろ、最初から全部許して、あとで「何が実行されたのか」を追うほうがずっとつらい。

## README より先に境界を書く

AI agent は README を読む機械ではない。

README を作業に変換する実行主体である。

だから、未知 repo を渡す前に決めるべきことは、いい prompt ではない。どの command を自動実行してよいか。どの network access を止めるか。どの secret を読ませないか。approval をどこで必ず挟むか。

agent の賢さは、境界の内側で使うと便利だ。

境界の外側まで届かせると、親切さそのものが攻撃面になる。

README を読ませる前に、実行してよい命令を書く。未知 repo に対する agent 運用は、そこから始めるくらいでちょうどいい。

## Source notes
