---
id: "2026-03-27-unitygithubgithubでバージョン管理に触れてみよう-01"
title: "【Unity＆GitHub】GitHubでバージョン管理に触れてみよう"
url: "https://qiita.com/kamaboko_0716/items/95cdd69e68042a135d61"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

# 【追記】

この記事を簡潔にまとめたバージョンを作ったのですが、そちらの方がわかりやすくまとまっている記事になってしまったので、GitHubを学ぶ目的であればこちらより新しく書いた記事の方を参考にした方がいいと思います。

![:arrow_down:](https://cdn.qiita.com/emoji/twemoji/unicode/2b07-fe0f.png ":arrow_down:")新しいバージョンの記事はこちら![:arrow_down:](https://cdn.qiita.com/emoji/twemoji/unicode/2b07-fe0f.png ":arrow_down:")

# はじめに

こんにちは。  
今回は、GitHub Desktopを使ったUnityの共同開発をClaudeを使って学んだので、その学んだことをまとめて、

* 共同開発でGitHubを使ってみたい
* GitHubに触れてみたい

と思う人向けに記事を書きました。  
また、今回の記事はあくまで「**初心者向け**」かつ「**触れる**」ことに重点を置いているので、

* 本格的な運用を学びたい
* GitHubについてちゃんと学びたい
* 既にGitHubを使った経験がある

という人には向いていない内容です。予めご了承ください。

また、かなりの長文になってしまいました。(教材として作成したので長いです)  
後々内容を分割して、今回のこの記事はそれらのまとめ記事として出すかもしれません。

# 今回使用した環境

* Windows 11(25H2)
* GitHub Desktop
* Git LFS(Git Large File Storage)
* Unity Hub & Unity Editor(6000.3.11f1)

# そもそも「Git」「GitHub」とは？

一応前提としてClaudeに解説してもらいました。

> *Git はソースコードの変更履歴を管理するツールです。「いつ・誰が・何を変更したか」を記録でき、過去の状態に戻したり、複数人で並行して開発したりすることができます。  
> GitHub はGitの仕組みを使ったクラウドサービスです。コードをオンラインで保存・共有でき、チームでの共同開発やオープンソースプロジェクトのホスティングに広く使われています。  
> 一言で言えば、Gitがバージョン管理の仕組み、GitHubがそれを使えるWebサービスです。*

こんな感じで、Gitを使って管理できるサービスがGitHubとなっています。

# 準備

ということで、準備から説明します。

> ## 1.GitHubに登録

まずはGitHubのアカウントを作りましょう。

特に手順は載せませんが、指示通り作れば何も問題ない（はず）です。  
（今回の記事を書く用に新規で登録してみましたが、特に問題なくできました。）

> [![スクリーンショット 2026-03-26 234026.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F73d8b930-0a40-4915-8873-1fb273e2631a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=756b645bec8b34da0a6582d663218766)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F73d8b930-0a40-4915-8873-1fb273e2631a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=756b645bec8b34da0a6582d663218766)  
> 登録が終わり、ログインするとこんな感じの画面が出てくると思います。

> ## 2.GitHub Desktopのインストール

次に、GitHub Desktopのインストールです。

[![スクリーンショット 2026-03-26 234648.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F284bc4e7-be49-42ac-901b-7c7df218e905.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5323863f5f112ae5596ea5660b5cfbc8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F284bc4e7-be49-42ac-901b-7c7df218e905.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5323863f5f112ae5596ea5660b5cfbc8)

「**Download for Windows (64bit)**」をクリックして、インストーラーを起動しましょう。  
（Macでもほとんど同じ操作で行けると思います。）

> [![スクリーンショット 2026-03-26 235125.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F7073bff3-2e1f-4927-84cc-e2370d2596d2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=dbd725f4a2ac74180dba30e62a618c85)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F7073bff3-2e1f-4927-84cc-e2370d2596d2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=dbd725f4a2ac74180dba30e62a618c85)  
> ↑インストーラー

GitHub Desktopが起動したら、GitHubのアカウントでログインしてください。  
（ブラウザの方でログインする感じになります）

ログインの後の指示がよくわからない人はこちら
> ログイン後、GitHubとGitHub Desktopを紐づけをするかの確認が出てくると思うので、緑色の許可ボタンを押して完了です。  
> 「**関連付けられたアプリを起動しますか？**」のような表示がブラウザの上側から出てきたら、「開く」か「許可」みたいなボタンを押しましょう。  
> （詳しく覚えていませんがそんな感じだった気がします。）

ここまでが必須ですが、次に入れるのはUnityのプロジェクトデータなどの、大容量のファイルを扱いたい人向けです。必要ないと思う方は、次のステップに飛ばして構いませんが、**個人的には入れておくことをお勧めします**。

> ## 3.Git LFS（Git Large File Storage）のインストール

まず、大前提としてこれは何なのかを説明します。  
GitHubは使用上、**1つで100MBを超えるファイルをアップロードすることはできません**。

そのため、大容量のファイルを扱う開発の場合は、この「**Git LFS**」というツールを使って、数GB単位のファイルもアップロードできるようにしなければならないのです。

> **100MBを超えるファイルはそのままでだとアップロードできない**
>
> **Git LFSがあれば大容量ファイルもアップロード可能**

ということでインストールしましょう。

インストールにはGitが必要なのでGitをインストールしていきます。  
**（途中でGit LFSもついでにインストールできます）**

> [![スクリーンショット 2026-04-06 201731.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F6ae54af9-7023-4e95-bb93-777b868f7f77.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=833e70d149841ae325ae3de87ff02196)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F6ae54af9-7023-4e95-bb93-777b868f7f77.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=833e70d149841ae325ae3de87ff02196)  
> Standalone Installerの「**Git for Windows/x64 Setup**」を押してインストーラーをダウンロードします。arm系CPUの場合はその下の「ARM64 Setup」をクリックしましょう。

**Mac OSの人はインストール手順がかなり異なってきます。**  
GitやGit LFSのページに書いてあるインストール手順や、ほかの方が解説してくれている記事を参考に進めてほしいです。（今回はWindowsの手順のみを載せます）

では、インストーラーを起動してインストールしましょう。

> [![スクリーンショット 2026-04-06 202159.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fe80a92ee-10a8-4690-a9cb-5252dafbee15.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=11510c58bfe89ba7c58c8d9aee99927d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fe80a92ee-10a8-4690-a9cb-5252dafbee15.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=11510c58bfe89ba7c58c8d9aee99927d)

基本的にこだわりがなければ「Next」を押していけばいいのですが、**何点か重要な点があるので確認してほしいです。**

### １．Git LFSにチェックを入れる

3つ目の画面で「Git LFS」にチェックが入っているかを確認してください。

> [![スクリーンショット 2026-04-03 222210.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F1937db8b-ea3e-4c42-a0f2-bc45df8e1505.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c111b2a49f983fb84e3e0de3b4094fee)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F1937db8b-ea3e-4c42-a0f2-bc45df8e1505.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c111b2a49f983fb84e3e0de3b4094fee)

### ２．VS Codeをデフォルトのエディタにする

これはVS Codeを使っている人はぜひしてほしい設定なのですが、デフォルトのエディタをVS Codeにした方がいいと思います。（「Vim」というのが初期値ですが癖があって後から面倒になるそうです。）

> [![スクリーンショット 2026-04-03 232036.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fe1d78101-83ae-4bee-8890-25901e983e54.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=81bdd259f613c5a2725a14c054f1e6dc)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fe1d78101-83ae-4bee-8890-25901e983e54.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=81bdd259f613c5a2725a14c054f1e6dc)  
> VS Codeをまだインストールしていない場合は「Next」が押せないと思います。  
> この設定をしたい場合はVS Codeをインストールしてからしましょう。

# 実際に触ろう！！！

ということで長かったかもですが、実際に触っていきましょう！

> ## 1.リポジトリの作成

まずは「**リポジトリの作成**」を行います。

### 「リポジトリ」とは？

> データすべてをまとめて置く場所みたいな感じです。  
> Gitの特性上、単なるファイルの保存や共有だけでなく、
>
> という情報も記録されます。それらを保存するためのものという感じですね。

GitHub DesktopとGitHubのWebページのどちらからでも作成できますが、今回は操作の説明のためGitHubのWebページ上で作成したいと思います。

ということでGitHubのページにアクセスします

> [![スクリーンショット 2026-03-26 234026.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Ff8e62bc8-7371-4bfd-914a-cceb1373ad40.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7372a0132a286f274094fa1de105bdff)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Ff8e62bc8-7371-4bfd-914a-cceb1373ad40.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7372a0132a286f274094fa1de105bdff)  
> アカウント作成時に出てきたページです。  
> そんなに大事な知識ではないですが、この画面を「**ダッシュボード**」といいます。

では、この画面の左上「**Create repository**」をクリックしましょう。  
２つ目以降は、「New」というボタンに変わりますが、手順は同じになります。

> [![スクリーンショット 2026-03-27 004602.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F24b6138d-bdce-40c1-8c7f-4d205dffd2c4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9cca0704230ef7527480a4bd6609977b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F24b6138d-bdce-40c1-8c7f-4d205dffd2c4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9cca0704230ef7527480a4bd6609977b)  
> 初回作成時はこんな感じになっていると思います。
>
> [![スクリーンショット 2026-03-27 004631.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F07c54cb2-dc3a-44a6-8d94-c18aa35fa821.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=18b5f4c2bb8ab4c9066701b642a0d8a3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F07c54cb2-dc3a-44a6-8d94-c18aa35fa821.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=18b5f4c2bb8ab4c9066701b642a0d8a3)  
> ２つ目以降はこんなかんじになります。

すると下の画像のような画面が出てくると思います。  
[![スクリーンショット 2026-03-27 005516.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fb4062627-968c-4850-b86c-e87dbd92828a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4af711c916a69d4cc99c5a429a75a78a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fb4062627-968c-4850-b86c-e87dbd92828a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4af711c916a69d4cc99c5a429a75a78a)

ここでは、上から順に

> * Repository name/Description  
>   リポジトリ名/リポジトリの説明を設定
>
> * Choose visibility  
>   アクセス範囲（「**Public(公開)**」「**Private(非公開)**」を選択
>
> * Add README  
>   説明文を追加するか（**ONを推奨します**）
>
> * Add .gitignore  
>   含めないファイルを指定する設定ファイル（**下で説明**）
>
> * Add license  
>   ライセンスの設定（**下で説明**）

の５つを主に設定します。

> [![スクリーンショット 2026-03-27 014007.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fd4490841-2f1f-4c15-bf03-217ebc893e32.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=696722563ffac1eb9107fd2b05cd43d5)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fd4490841-2f1f-4c15-bf03-217ebc893e32.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=696722563ffac1eb9107fd2b05cd43d5)  
> こんな感じで設定します（例なので各自に合った設定を行いましょう）

特に、「Add .gitignore」と「Add license」の２つについて解説します。

### .gitignoreとは

> 「**含めないファイルを指定する設定ファイル**」です。  
> GitHub側である程度のテンプレートが用意されており、自分の使う環境に合ったテンプレートを選択するだけで、不要なファイルと必要なファイルを自動で選別してくれます。

自分はUnityを使って共同制作したいので、「Unity」を選択したいと思います。

### Licenseとは

> 「**利用についてのルールとかを書いたりするもの**」です。  
> これがないと、このリポジトリを見たときに好き勝手に使っていいのかわからないっていう問題が発生するので、それを回避するために、ちゃんと著作者や利用するルールを書いたファイルを作ろうといった感じです。

何もこだわりがなければ、「**MIT License**」がおすすめです。  
これは、「**著作者を明記すれば、コードは自由に使っていいよ。でも、動作の保証は一切しないよ。**」という感じのライセンスです。（詳しくは調べてください）

すべて設定できたら、「**Create repository**」を押しましょう！

> [![スクリーンショット 2026-03-27 014030.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F655d406f-bcd3-46f5-b4b9-175c885f7b5f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=688526fd6f823005214944835b2c5b77)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F655d406f-bcd3-46f5-b4b9-175c885f7b5f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=688526fd6f823005214944835b2c5b77)  
> 完成！

> ## 2.リポジトリのクローン

これでやっとリポジトリができましたが、編集したり作業ができるわけではありません。  
そこで、「**自分の端末**」と「**GitHub**」のリポジトリを同期させる作業を行います。

> [![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F99305367-fe9a-4b8f-bc47-1d9d86534e31.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1e50c20015452e2f367f490762c9ecb8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F99305367-fe9a-4b8f-bc47-1d9d86534e31.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1e50c20015452e2f367f490762c9ecb8)  
> 図で表すとこんな感じです

まずは、「**GitHub Desktop**」を開いてください。

画像がないのですが、最初に「**Clone repository**」という表示があったと思うので、そこを押しましょう。

> [![スクリーンショット 2026-03-27 015604.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F244f49f7-9bf0-46f3-9217-c7d82cbeb8f5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b3975f5c2998a47cb8af407a22c2fbcd)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F244f49f7-9bf0-46f3-9217-c7d82cbeb8f5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b3975f5c2998a47cb8af407a22c2fbcd)  
> ２つ目以降は左上の「**Add**」から「**Clone repository**」を選択します。

そうすることで、クローンするリポジトを選ぶ画面が出てきます。  
[![スクリーンショット 2026-03-27 021233.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F06e328b8-562a-47d7-b291-96be33823759.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f73f742290ce8f0eca88d830ea206b67)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F06e328b8-562a-47d7-b291-96be33823759.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f73f742290ce8f0eca88d830ea206b67)

ここでは、

> クローンしたリポジトリを自分の端末のどこに保存するか

を設定します。

### クローンしたいリポジトリの選択

まず、ここで自分の端末にクローンしたいリポジトリを選択します。

> [![スクリーンショット 2026-03-27 015533.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F416b68d7-1cfc-4165-acae-726f3fb9ff1d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=aa5acaf1521c976636a38c405c883462)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F416b68d7-1cfc-4165-acae-726f3fb9ff1d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=aa5acaf1521c976636a38c405c883462)  
> 今回は先ほど作成したリポジトリを選択します。

### 保存場所の設定

次に、その下側にある「**Local path**」の設定で、「**自分の端末のどこにクローンしたファイルを保存するか**」を設定します。

> [![スクリーンショット 2026-03-27 021233.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fdeb2596d-4c9e-4ace-aa5d-eed8174fda5e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a473dfd06348608903b255ffb51d0510)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fdeb2596d-4c9e-4ace-aa5d-eed8174fda5e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a473dfd06348608903b255ffb51d0510)
>
> 画像は例なので、この文字をそのままコピーすると変なところに保存されます  
> 自分のわかりやすい場所へ保存しましょう

すべてできたら、「**Clone**」というボタンを押しましょう。

**これで、指定した場所にリポジトリがクローンされたと思います！**

> ## 3.Git LFSの設定（最初だけ）

この項目は、Unityを使う方、もしくはGit LFSを使う方向けの説明になります。  
**Git LFSのインストールも必須なので、忘れずにインストールしましょう。**

既に他の人がこの設定を行っていた場合（.gitattributesが既に作成されていた場合）でも、[手順２](https://qiita.com/kamaboko_0716/items/95cdd69e68042a135d61#2git-lfsgitattributes%E3%81%AE%E8%A8%AD%E5%AE%9A)の\*\*[Step1](https://qiita.com/kamaboko_0716/items/95cdd69e68042a135d61#step1%E3%83%AA%E3%83%9D%E3%82%B8%E3%83%88%E3%83%AA%E3%81%AE%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E3%81%A7cmd%E3%82%92%E8%B5%B7%E5%8B%95)～[Step2](https://qiita.com/kamaboko_0716/items/95cdd69e68042a135d61#step2git-lfs%E3%81%AE%E5%88%9D%E6%9C%9F%E5%8C%96)の操作を必ず行ってください。\*\*

ここからは、Git LFSの設定をして、GitHub DesktopがGit LFSを使ってくれるように設定していきます。

### 1.Unityのプロジェクトデータ作成

Unityを使わない場合は、[手順２](https://qiita.com/kamaboko_0716/items/95cdd69e68042a135d61#2git-lfsgitattributes%E3%81%AE%E8%A8%AD%E5%AE%9A)へ進んでください。

まず、Unityを使う人は、プロジェクトを先ほどクローンしたリポジトリに作成しましょう。  
（作成されている場合はこの手順をスキップしてください）

> [![スクリーンショット 2026-03-27 024057.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F2dc64ac6-7795-40f0-9fd4-83d33bbb019c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b88b56a9f404e9a5f65677c2da85dc35)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F2dc64ac6-7795-40f0-9fd4-83d33bbb019c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b88b56a9f404e9a5f65677c2da85dc35)  
> 「**Unity Hub**」を起動し、右上の「**新しいプロジェクト**」を押しましょう

プロジェクトの設定はお任せしますが、作成場所は必ずクローンしたリポジトリのフォルダに作りましょう。

「**保存場所**」の項目をクリックし、クローンしたリポジトリのフォルダを選択します。

> [![スクリーンショット 2026-03-27 024354.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F621db065-1e4f-42d8-843b-9cec941b6f3b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2b22f6cae7eaac20c9993d995bbe0c1b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F621db065-1e4f-42d8-843b-9cec941b6f3b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2b22f6cae7eaac20c9993d995bbe0c1b)  
> 画像では先ほど自分がクローンしてきたリポジトリのフォルダを選択しています

プロジェクトが新規作成され、Unity Editorの画面が出てきたら、いったんEditorを閉じましょう。

> [![スクリーンショット 2026-03-27 025254.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fb8ab38c4-e30b-43a3-869d-ee9d46a0313f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=35bfa5250723597f763a3ba3c4ded59f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fb8ab38c4-e30b-43a3-869d-ee9d46a0313f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=35bfa5250723597f763a3ba3c4ded59f)  
> このまま閉じましょう

その後、エクスプローラーで、「.gitignore」ファイルを、プロジェクトのあるフォルダに移し替えます。

> [![スクリーンショット 2026-03-27 032313.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Ff27deb2e-6e26-431a-948a-0c6607db5745.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=409a04eeb053a878334ecc782ede2dbf)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Ff27deb2e-6e26-431a-948a-0c6607db5745.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=409a04eeb053a878334ecc782ede2dbf)  
> これを

> [![スクリーンショット 2026-03-27 032419.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F0c0cacce-1b4f-4917-889b-b1590311c208.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8b1350e7db46b9ba7f640ff4c00714f8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F0c0cacce-1b4f-4917-889b-b1590311c208.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8b1350e7db46b9ba7f640ff4c00714f8)  
> 先ほど作ったUnityのプロジェクト内（今回で言えば１枚目の「My Project」）に移動させます。

### 2.「Git LFS（.gitattributes）」の設定

**他の人がこの手順を行ってくれていた場合でも、Step2までは必ず行わないといけません。**

次に、GitHub DesktopでGit LFSを使ってもらうための設定用ファイルを配置します。  
その設定用ファイルを「.gitattributes」っていいます。

**「あれ？さっきも似たようなものが...」**  
となった人は、記憶力がいいですね（？）

ここでの注意は、**「.gitignore」と「.gitattributes」を混在して覚えないようにすること**かなと思います。

> 「.gitattributes」  
> **Git LFSを使ってもらうファイルの設定**

です。覚えておきましょう。

ということで、説明していきます。

#### Step1.リポジトリのフォルダでcmdを起動

まずはエクスプローラーでリポジトリを保存したファイルを開きましょう。

> [![スクリーンショット 2026-03-27 034601.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F0f9a991f-3ce1-46f8-9883-18f4253c4817.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a941da17111726c1ea8b800486bc09e8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F0f9a991f-3ce1-46f8-9883-18f4253c4817.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a941da17111726c1ea8b800486bc09e8)  
> 先ほどの項目で「.gitignore」を移動させたのでこうなっています  
> （Mac OSだとここの手順は異なります。詳しくは調べてください。）

この画像の上側にある「ドキュメント」や「`（クローンしたリポジトリのフォルダ名）`」が書いてある部分（アドレスバー）をクリックし、下の画像のように「**cmd**」と入れて、Enterキーを押してみてください。

> [![スクリーンショット 2026-03-27 035654.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Ff3ab1c87-328f-4bac-9884-2f53561f51e5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ebf73fa8c1726fe727b05c0b9d764ba8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Ff3ab1c87-328f-4bac-9884-2f53561f51e5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ebf73fa8c1726fe727b05c0b9d764ba8)  
> この状態で`Enter`

すると以下のような文字が出てくる画面が出ると思います。

この時点でクローンしたリポジトリの場所が指定できてない場合、もう一度エクスプローラーから「cmd」と入力して起動させてください

例として出しますが、「TestRepository」という名前のリポジトリを「C:\Users\username\Documents\TestRepository」にクローンした場合、

> cmd
>
> ```
> C:\Users\username\Documents\TestRepository＞
> ```
>
> のような感じになっていればOKです。
>
> のように、クローンしたリポジトリのある場所が指定できていない場合は、もう一度やり直してください。

ここにコマンドを打ち込んでいきます。

#### Step2.Git LFSの初期化

と入力し、`Enter`を押して実行します。

**ここから先は、誰かがすでに１度行っている（リポジトリに「.gitattributes」が既にある）場合、Step３とStep４は設定不要です。**  
**ただし、「.gitattributes」を編集したい場合は続けてください。**

#### Step3.管理するファイル形式を指定

次に、Git LFSで管理してほしいファイル形式の設定を行います。

例えば、「MP4」と「PNG」形式のファイルを指定する場合、

cmd

```
git lfs track "*.png" "*.mp4"
```

のように入力して、実行しましょう。  
こうすることで、「MP4」と「PNG」形式のファイルを管理するように指定できました。

> 今回Unityを使っている人は、以下のコマンドをコピーしてそのまま張り付けると、ある程度の大容量ファイルに対応してくれます。「.vrm」など、他に追加したいものがある場合は、このコードに先ほどのように付け足してください。
>
> cmd
>
> ```
> git lfs track "*.png" "*.jpg" "*.psd" "*.fbx" "*.mp3" "*.wav" "*.mp4" "*.unitypackage"
> ```

#### Step4.追加＆Commit

最後に、

cmd

```
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

と入力して、実行しましょう！

最初のコマンドで、Step3で指定したファイルをGit LFSで管理してくれるようになる設定を書いた「.gitattributes」というファイルを新規作成しています。

次のコマンドはCommitという操作をしています。（詳しくは次で説明します。）

> ## 4.「Commit」と「Push」

次に、編集したデータをGitHubにアップロードして反映させていきます。

そこで登場するのが、「Commit」と「Push」です。

> [![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F3d872a8a-0147-4b73-8723-ffe555a69a06.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6dec7cbd9621da2bfdd446de0eeb5d84)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F3d872a8a-0147-4b73-8723-ffe555a69a06.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6dec7cbd9621da2bfdd446de0eeb5d84)  
> 図で表すとこうなります。

### まずはCommitから

「Commit」は、日記のようなもので、変更した記録を自分のPCに保存します。

> 基本的には、きりがいいところで「何をしたか」を簡単にまとめておきましょう。例えば、
>
> など、１つの作業を終わらせる毎に行うといい感じに管理・運用できます。

では、実際にやってみましょう。

まだリポジトリに何も変更を加えていない人は、テキストファイルなどをクローンしたリポジトリの中に作成してみましょう。

詳しいやり方はこちら
> [![スクリーンショット 2026-03-28 234321.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F6ce2a184-e18b-4cee-9eba-06e1d65dda7d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=55074e429f5806cc3fcf7889d4b5942b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F6ce2a184-e18b-4cee-9eba-06e1d65dda7d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=55074e429f5806cc3fcf7889d4b5942b)  
> クローンしたリポジトリの中で、何もないところを「右クリック」して、「新規作成」→「テキストドキュメント」を選択しましょう。
>
> [![スクリーンショット 2026-03-28 234337.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F2b82a48d-9e98-4dcb-a333-932becd237a3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0a9f523e3df1ec887e3ee053736617db)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F2b82a48d-9e98-4dcb-a333-932becd237a3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0a9f523e3df1ec887e3ee053736617db)  
> こんな感じでできたらOKです。テキストファイルを開いて何か書いてから保存してみると、変更点がわかりやすくていいと思います。

Unityのプロジェクトを作成した人は、「**GitHub Desktop**」を再度開くと、こんな感じで何か表示が変わっていると思います。

ここに出されているのが、変更のあったファイルになります。

こういう変更があった部分を「**差分**」と呼びますが、めっちゃ大事な知識ではないので軽く覚えておきましょう。

> [![スクリーンショット 2026-03-27 051635.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F44917eea-47a9-4e84-80fa-9bde27137015.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9030c15ae94d9c76ad32231a8eeea029)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F44917eea-47a9-4e84-80fa-9bde27137015.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9030c15ae94d9c76ad32231a8eeea029)  
> GitHub Desktop上で差分が表示されていると思います

そして、この画面の左下にあるところが「Commit」をする部分です。

> [![スクリーンショット 2026-03-27 052504.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F3e84a2e5-bae4-40c0-9f9e-2b924aa7bf28.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=54ed0c09643118d39589564728003534)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F3e84a2e5-bae4-40c0-9f9e-2b924aa7bf28.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=54ed0c09643118d39589564728003534)  
> 画面左下にあります

「**Summary**」には、簡単なまとめを、  
「**Description**」には、詳細な説明を残しておきましょう。

> [![スクリーンショット 2026-03-27 053809.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F0920742b-e340-48fa-840f-c03f5ba26b53.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1410275acf0b71c28d431699d0a7e138)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F0920742b-e340-48fa-840f-c03f5ba26b53.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1410275acf0b71c28d431699d0a7e138)  
> 共同開発をする際に書く形式がばらばらになるのが気になるときは、事前に書き方のルールを決めておくといいと思います。

**では、青色の「Commit」のボタンを押しましょう！**

いっぱい出ていた表示が消えていれば完了です！

### 次にPush！

次に、Commitした記録をGitHubへアップロードしましょう！  
そこで使うのが、「**Push**」です！

> **Pushとは**  
> 簡単に説明すると、編集したデータを送り込む感じの動作のことです。  
> Gitではそれなりに出てくる用語なので知っておきましょう！

さて、実際にPushしましょう！  
Commitした後、上側をよく見ると、一番右側に「**Push origin**」と出ています。

> [![スクリーンショット 2026-03-27 055038.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F8b4aedfa-25d9-47c5-86c7-1129020e35c3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2b10d9a6f88c9dd858529ff11b136f5a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F8b4aedfa-25d9-47c5-86c7-1129020e35c3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2b10d9a6f88c9dd858529ff11b136f5a)

これを押します！すると...

> [![スクリーンショット 2026-03-27 055446.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fc0565e8f-2e39-4340-ad73-2889d822d01e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6862b85e51c15824115620668b92b19b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fc0565e8f-2e39-4340-ad73-2889d822d01e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6862b85e51c15824115620668b92b19b)

「Fetch origin」に表示が切り替わりました！これで完了です！

> 「**Fetch** **origin**」はGitHubの最新情報を確認する機能です。  
> Push後はこの表示に切り替わります。

> ## 5.ブランチ

次に、ブランチという概念について説明します！

簡単に言えば、枝分けしてそれをくっつけたりできるといった機能です。  
言葉だと分かりにくい気がするので、図示しました。

> [![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F34ae5960-6054-4ba0-8365-1853254303be.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4e00b64b4885458679702ab75ffe4d02)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F34ae5960-6054-4ba0-8365-1853254303be.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4e00b64b4885458679702ab75ffe4d02)

こうするメリットは、いくつかあります。  
例えば、

* コードを編集していたらデータを壊してしまった
* ファイルを統合したらエラーが発生してしまった
* データの復元に時間がかかってしまった

というような経験はないでしょうか？

しかし、Gitの「ブランチ」を図のように活用することで、「**共有する本番環境**」と「**自分の開発環境**」を分離することができます！

そうすることで、

* 自分のデータを壊しても、本番の環境に影響が出ない
* エラーの発生を事前に確認できる（「[7.Pull Request](https://qiita.com/kamaboko_0716/items/95cdd69e68042a135d61#%E3%81%BE%E3%81%9A%E3%81%AFpull-request)」を見てください）
* すぐに復元できる

など、**安全に大人数で開発できる**というメリットがブランチの強みです。

また、あるブランチから分岐させることを「**ブランチを切る**」といい、あるブランチをもう一つのブランチに合体させることを「**マージ**」といいます。

これだけじゃわかりにくいと思うので、イメージとしては、

> **ブランチを切る**  
> 「共有するデータのブランチ」を分岐させて、「自分の作業用のブランチ」を作る。
>
> **マージ**  
> 「自分の作業用のブランチ」を「共有するデータのブランチ」へ合体する。

というような感じで操作をしていきます。

基本的には、「ブランチを切ってマージする」の繰り返しをしていく感じになっています。

なので、開発する際は必ず「共有する環境」を直接編集するのではなく、ブランチを切って、そのブランチを編集するという感じになります。編集が終わったら、それを「共有する環境」に統合します。

> ## 6.ブランチを切る

では、実際にブランチを切ってみましょう。

「GitHub Desktop」の上のバーの真ん中にある「**Current Branch**」を押しましょう。

> [![スクリーンショット 2026-03-27 055446.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fb050b094-9fe3-4608-aa76-3c239394b661.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7507870b9e07b1fdfe0352edd5c92fa7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fb050b094-9fe3-4608-aa76-3c239394b661.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7507870b9e07b1fdfe0352edd5c92fa7)  
> 今回の画像では「main」と書かれてる部分です。

クリックすると、このような感じで現在のリポジトリにあるブランチ一覧が出てきます。

> [![スクリーンショット 2026-03-27 062937.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F93f80438-75ca-4c22-96ff-b78a8e191c98.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=42716498b00020f41a67b4f9aa02e5c8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F93f80438-75ca-4c22-96ff-b78a8e191c98.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=42716498b00020f41a67b4f9aa02e5c8)

mainのみしかないので、右上の「New Branch」というボタンを押して、mainブランチを切ってみましょう！

> [![スクリーンショット 2026-03-27 063352.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fc9c67c02-52e4-4de2-b477-48606d282f8f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=91f25d60f7c4687d0cea0fa77f4dd202)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fc9c67c02-52e4-4de2-b477-48606d282f8f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=91f25d60f7c4687d0cea0fa77f4dd202)  
> ブランチの名前を入力して、「Create Branch」をクリック！

そうすると、上のバーの右上に「**Publish branch**」と出てくるので、それを押しましょう！

> [![スクリーンショット 2026-03-27 063807.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F5e198d0b-b08c-48cf-ac07-0ac0af2103d0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2454fcd4dc244a680329559cc9bd75bc)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F5e198d0b-b08c-48cf-ac07-0ac0af2103d0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2454fcd4dc244a680329559cc9bd75bc)

こうすることで、切ったブランチをGitHubにアップロードすることができました！

> ## 7.「Pull Request」と「Merge」

いよいよマージをしてみましょう。

まず、ブランチが先ほど切ったブランチになっているかを確認し、リポジトリ内のファイルを編集します。（テスト程度なら何かファイルを新規作成したりしてみてください）

編集し終わったら、保存して「**GitHub Desktop**」を開きましょう。

> [![スクリーンショット 2026-03-27 070506.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fe6f4d3f3-3c32-48eb-979e-232cd1ed8f71.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5a43395d8b03d5470bcd81a86cea8d63)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fe6f4d3f3-3c32-48eb-979e-232cd1ed8f71.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5a43395d8b03d5470bcd81a86cea8d63)

さっきまでやってきた手順通り、「Commit」→「Push」を行います。

### まずは「Pull Request」

編集が終わりPushできたら、こんどはマージをする前段階である、「**Pull Request**」を出します。これは、共同制作で必須になる機能なので、覚えた方がいい知識となっています。

まず、「**Pull**」ですが、「Push」の逆です。なので、

となります。  
一応今回の場合、「main」ブランチが、「`（mainから切ったブランチ名）`」ブランチの内容をもらうという感じになっているので、操作としては「Pull」になるわけです。（ややこしいですが「マージの正体がこれだ！」といった感じです）

次は、「**Pull Request**」です。  
簡単に説明すると、「何を変更したか」を書いて、マージしたいことを告知することです。

共同開発の際の「Pull Request」からマージの流れを先に説明すると、

> １.**「Pull Request」を出す**  
> ここで「何を変更したか」、「どんなところを見てほしいか」を書いて、チームのメンバーへ「共有する本番環境」に変更を加えたいことを周知する。
>
> ２.「**コードレビュー**」を書いてもらう  
> ほかの人が「Pull Request」に書かれている内容を元に、問題がないかを調べ、評価します。  
> この段階で何か問題があった場合は、修正を要求することもできます。
>
> ３.「**マージ**」する  
> コードレビューを行って問題がなければ、「Pull Request」で告知した通りマージをします。

という感じになります。

では、説明だけだとわかりにくいので、実際にやってみましょう！  
Pushし終わると、「GitHub Desktop」の中央に、下のような感じの表示が出ます。

> [![スクリーンショット 2026-03-27 070859.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fc21a790d-500d-432b-8ed8-258ee36f2a05.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c805251afa823392e741c6931940a50a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fc21a790d-500d-432b-8ed8-258ee36f2a05.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c805251afa823392e741c6931940a50a)

この一番上の青色の項目「**Create Pull Request**」をクリックします。

> [![スクリーンショット 2026-03-27 072353.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F9de9de7c-c0a7-4331-9ccd-7f57dc1e0b26.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=90d5cac8fe4986703ee022f9f4ee1d9f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F9de9de7c-c0a7-4331-9ccd-7f57dc1e0b26.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=90d5cac8fe4986703ee022f9f4ee1d9f)  
> GitHubのページが開いて、こんな画面が出ると思います。

ここで、「Pull Request」を出します。  
設定する項目としては、

* どのブランチにPullするか
* どんな変更を加えるかの概要

の２つがメインになっています。

**マージするブランチの設定**

> [![スクリーンショット 2026-03-27 073313.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F4270d3ff-2c9f-4bdc-b759-95f8e6f425f5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ae527eb08a73993e7d362cc823d29cb5)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F4270d3ff-2c9f-4bdc-b759-95f8e6f425f5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ae527eb08a73993e7d362cc823d29cb5)

特に難しい設定はいりません。画像にもあるとおり、ブランチを２つ選択するだけです。

矢印の方向にデータが動くので、そこだけ間違えがないかよく確認しておきましょう。

**どんな変更を加えるかの概要**  
次に、どんな変更を加えるかの概要と説明を書いていきます。  
こちらも書き方のルールを書いておくといいと思います。

> [![スクリーンショット 2026-03-27 073559.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Ffe85c3ca-7003-460e-bd30-6a202571d108.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=897c189d820bb95cafe237d34853391f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Ffe85c3ca-7003-460e-bd30-6a202571d108.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=897c189d820bb95cafe237d34853391f)  
> こんな感じで、どこが変更されたのかを説明します

**最後に、「Create Pull Request」をクリックしてみましょう。**

すると、

> [![スクリーンショット 2026-03-27 074003.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fe4fafbc8-7634-479f-be29-27fc3d32d13a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=93b895c289a4462e9f7eb8464b92b22f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2Fe4fafbc8-7634-479f-be29-27fc3d32d13a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=93b895c289a4462e9f7eb8464b92b22f)

こんな感じの画面に切り替わると思います！

これで、「Pull Request」を出せて、どんな変更を加えたいのかを周知できました！

### 次にコードレビュー

ここからコードレビューをするのですが、今回は省きます。

コードレビューのやり方が載っている記事を見つけたので、参考にしてください。

### 最後に「Merge」する

コードレビューが終わり、問題なしだという前提で進めます！  
なので、次にマージします！

先ほどの画像の真ん中にある、「**Merge pull request**」を押しましょう！

最後に、コメントを書いて、左下の「**Confirm merge**」を押しましょう！

表示が「Open」から「Merged」に変わっていればOKです！  
これでマージできました！

> [![スクリーンショット 2026-03-27 074735.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F55d90249-6b7c-461e-971b-a3cb60959e5f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3c4a3141d03e0176351d307fa9c123ea)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F55d90249-6b7c-461e-971b-a3cb60959e5f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3c4a3141d03e0176351d307fa9c123ea)

### 最後に自分の端末のmainブランチを更新

他の人がマージした際に必要な操作ですが、一人だけならあんまり気にしなくていいかもです。

最後に自分の端末のmainブランチを更新します。

「GitHub Desktop」の「branch」から、「Update from main」を押します。

> [![スクリーンショット 2026-03-27 212232.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F64635bca-3254-4598-9f51-5ad077d7a6da.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d95a15ff9ae3c1b25d28228dddf68c1d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3622551%2F64635bca-3254-4598-9f51-5ad077d7a6da.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d95a15ff9ae3c1b25d28228dddf68c1d)

次に、差分が見つかった場合はPullの表示が出てきます。  
Pullが出てきたときはPullしましょう。  
これで完了です！

# 最後に

ここまで大変だったと思いますが、こんな感じになっています。

最初にも話した通り、これは教材としてテキトーに作ったものをいいかんじにしただけなので情報量がとんでもないことになってると思います。

いつかうまいこと分割してもっと内容をすっきりさせたバージョンを出そうと思っているので、そちらもお願いします。

この記事で伝えたいのは、とにかく簡単だよねってことを伝えたいです。  
自分はGitHubをQiitaで勉強しようと思いましたが、何一つわからなくて３度くらい挫折してますw

AIの手助けってすごいなって感じられた内容になりました。

ぜひ何度もやってみて、GitHubのスキルを身に着けてみてください！

次は運用時の問題の対処についての記事になってます！  
是非こちらも参考にしてください！
