---
id: "2026-07-07-vs-code-devcontainer-を使わなくなった私のllm-エージェント向け開発環境-01"
title: "VS Code DevContainer を使わなくなった私の、LLM エージェント向け開発環境"
url: "https://zenn.dev/kenfdev/articles/1febc0052b0d71"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "VSCode", "zenn"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

以前、「辿り着いた最高の開発環境は Remote な Dev Containers です」という記事を書きました。

<https://zenn.dev/kenfdev/articles/dba4dbd4526172>

当時は本当にそう思っていました。Mac や Windows の普段使い環境を維持しつつ、開発だけ Linux 上に寄せられる。Tailscale や Remote SSH を組み合わせれば、どこからでも同じ開発環境に入れる。

最高だと思っていたのですが。。。

今の私は、VS Code + DevContainer を全く使わなくなりました。代わりに、**コンテナを SSH できる個人用の開発マシンとして扱う** 方向に寄せています。

この記事は現時点（2026/07/07）の私の開発環境の共有と、なぜそこに至ったのかの紹介です。自己満です。「これが正解です」という話ではありません。あくまで、今の自分にはこの形が一番フィットしている、という共有です。もっとよいやり方があれば知りたいです。特に、個人の開発環境とプロジェクトごとの依存関係をどう共通化するかは、まだかなり悩んでいます。

## TL;DR

* VS Code + DevContainer は便利だったが、今は全く使わなくなった
* LLM エージェントに作業を任せる時間が増え、VS Code よりも SSH で入れる開発環境のほうが重要になった
* 今は「1 プロジェクト 1 コンテナ」ではなく、「組織が扱っているドメインごとに 1 つの開発コンテナ」という感覚で運用している
* コンテナの中には、同一組織内の複数プロジェクトや worktree を置く
* Orca という Agent Development Environment から SSH でコンテナに接続し、remote worktree と agent terminal を使っている
* secret は物理ファイルに残さず、基本的に 1Password の `op` CLI 経由で必要なときに注入する

## 今の構成と開発フロー

まず、今の自分の開発環境の全体像はこんな感じです。

![](https://static.zenn.studio/user-upload/f7419e74763c-20260707.png)

「こんな図を見せられても。。。」と思うでしょうけど、とにかく今の自分の開発環境の構成はこんな感じです、っていうのを先に見せておきます。で、この構成で何ができているかというと「ローカル開発」も「ローカルコンテナ開発」も、「リモート開発」も「リモートコンテナ開発」もすべて１箇所で、かつ同じような開発体験が実現できています。

ほとんど Orca という ADE のおかげといえばそうなのですが、コンテナ開発環境のマインドシフトのおかげでもあると思っています。

一元管理している様子はこんな感じ（ローカルで開発しているものもあれば、SSH経由でリモートコンテナ上で動いているものもあります）

![](https://static.zenn.studio/user-upload/4a0ba80421f7-20260707.png)

どの環境であろうが、Agentが作業を終わらせるとちゃんと通知がきます

![](https://static.zenn.studio/user-upload/a68efb65e507-20260707.png)

リモート環境からは動的にポートフォワードもできます（VSCodeと同じような感じ）

![](https://static.zenn.studio/user-upload/3d098fb04f55-20260707.png)

Orcaの機能を使ってブラウザ内の要素に直接コメントを書いてAgentに渡せます（どんな環境でもOK）

![](https://static.zenn.studio/user-upload/c5b05a9f157e-20260707.png)

コードにももちろんフィードバックをまとめてLLMに渡すこともできます（これもどんな環境でもOK）

![](https://static.zenn.studio/user-upload/27289e356b79-20260707.png)

と、あげていけばキリがないのと、どちらかというとすごいのはOrcaで、この記事の趣旨とちょっとずれてしまうのでこの辺にしておきます。とにかくリモートコンテナ開発であっても快適に開発ができているということです。

では、本題に戻りましょう。

## この記事で扱うこと

これはチーム全員に同じ開発環境を配る話ではありません。

チーム標準の環境を作るなら、リポジトリに `.devcontainer` を置いて DevContainer として管理するのは今でもよい選択肢だと思います。プロジェクト単位の再現性を持たせやすいですし、VS Code で開発する人にとっては体験も整っています。

この記事で扱うのは、それとは少し違います。

個人が LLM エージェントと一緒に作業するための開発環境を、どう持つかという話です。

特に、自分の中では次の問いが大きくなりました。

> ほしいのは、プロジェクトごとに毎回作られる開発環境なのか。それとも、LLM エージェントが安定して入れる、自分用の開発マシンなのか。

今の自分は、後者に寄っています。

## 何が変わったのか

VS Code + DevContainer は最高でした。エディタからコンテナに入り、コンテナ内のツールを使い、拡張機能も動く。人が IDE の中で作業するなら、すぐにプロジェクトの開発が開始できました。

ただ、最近は LLM エージェントに実装や調査を任せることがほとんどです。自分でコードを読むことはありますが、「自分が VS Code のようなエディタでコードを書く」ことが激減しました。

そうなると欲しいものが変わります。

* コードが快適に書けること
* 拡張機能がコンテナ内で便利に動くこと

よりも、

* agent が動作する環境があること
* 複数の agent terminal を並行して動かせること
* agent が今どういう状態なのか一目でわかりやすいこと（通知もくること）
* 必要な port を簡単に確認できること

のほうが重要になりました。

この開発スタイルだと、VS Code + DevContainer を中心に据え続けるのはだんだんきつくなると感じています。

## worktree と DevContainer のつらさ

LLM エージェントを使うようになると、git worktree を多用したくなります。

タスクごとに worktree を切って、それぞれで agent を走らせる。失敗したら捨てる。別案を並列に試すなどなど。

ただ、DevContainer と組み合わせると、worktree ごとにコンテナが増えがちです。（最近の VSCode は改善しているかもしれませんが、少なくとも私が使っていた頃はこのあたりつらみがありました）

* worktree ごとに環境が増える
* 同じ port を使うアプリが衝突する
* DB や Redis などの周辺サービスをどう共有するか考える必要がある
* 初期化や後片付けが増える
* VS Code の接続状態や初期化処理に運用が引っ張られる

これは DevContainer だけの問題ではありません。DevContainer を使わなくても、worktree を並列に増やすなら似た問題は起きます。

このあたりをどうにかできないかと以前、worktree と DevContainer を組み合わせる工夫についても書きました。

<https://zenn.dev/kenfdev/articles/222fe622d42f0d>

それで比較的快適に開発を進められたのですが、今の使い方では「worktree ごとに開発環境を増やす」より、「1 つの長生きする開発マシンの中に worktree を増やすほうがいいのでは？」と思うようになったのですよね。

## 1 プロジェクト 1 コンテナをやめる

今は、プロジェクトごとにコンテナを作るのを基本的にはやめました。

代わりに、組織が扱っているドメインごとに 1 つの開発コンテナを持つようにしています。ここでいうドメインは、DDD の用語というより顧客、契約、事業、扱う権限が同じ範囲、くらいの意味です。

同じ組織内であれば、技術スタックが多少違っても同じコンテナに入れます。逆に、顧客や契約が違う仕事は分けます。

これくらいの粒度です。

* 同じ組織・同じ仕事の範囲なら、複数プロジェクトを 1 コンテナに入れる
* 顧客や契約が違う仕事は、別コンテナにする
* 本番権限や強い secret を扱うものは、普段使いの agent 環境から分ける

技術スタックが近いかどうかだけでは決めません。むしろ、同じ shell history、同じ `gh` 認証、同じ package cache、同じ LLM agent の実行権限を共有してよいか、などで決めています。正直なところコンテナの思想に則っていないという気持ちはあります。。。が、現段階ではこれがフィットしています。

長生きするコンテナは、ただの隔離された作業ディレクトリではなく、操作履歴、キャッシュ、生成ファイルが溜まる開発マシンとして考えています。

なので、便利さのために顧客や契約の境界をまたがないようにしています。

## 開発コンテナを SSH できるマシンとして扱う

もう 1 つ大きく変えたのが、コンテナへの入り方です。

以前は、DevContainer を使うなら VS Code に任せていましたし、少し中を見るだけなら `docker exec` で十分だと思っていました。

ただ、LLM エージェント用の開発環境として考えると、SSH できることが重要になります。

自分は今、[Orca](https://www.onorca.dev/) を使っています。Orca は、Claude Code や Codex などの CLI agent を、worktree 単位で並行して動かせる総合的な IDE ならぬ ADE(Agent Development Environment) です。

Orca には SSH worktrees という機能があります。SSH target を登録すると、remote host 上に git worktree を作り、agent もその remote host 上で動かせます。エディタ、diff、browser などは手元のアプリ側に残しつつ、実行環境だけ SSH 先に寄せられる、という形です。

<https://www.onorca.dev/docs/ssh>

この機能があったので、「それならコンテナに SSH できるようにすれば、コンテナを remote host として扱えるのでは」と考えました。

イメージはこうです。

ポイントとしては、コンテナを「Orca が SSH で入る開発マシン」として扱うことです。

Orca 側では、SSH target を登録して、その target 上に worktree を作ります。agent terminal もそのコンテナ内で動きます。

port forwarding も Orca の Ports タブから扱えます。コンテナ内で dev server が立ち上がると、VS Code の Ports と同じような感覚で、検出された port をクリックして手元に forward できます。手動の `ssh -L` ではなく、GUIからダイナミックに設定ON/OFFできるのはかなりでかいです。

## SSH の設定

コンテナへの接続情報に関しては環境に合わせて SSH config を書いています。

雰囲気としてはこんな感じです。

```
Host my-dev-container
  User ubuntu
  ProxyCommand ssh -T host-machine docker exec -u root -i my-dev-container /usr/sbin/sshd -i
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no
  LogLevel ERROR
```

かなりオレオレ設定ですが、プライベートな開発コンテナで、外に公開しない前提なので割り切っています。（セキュリティポリスでツッコミがある人、ぜひコメントをよろしくお願いします）

あくまで「自分の管理下にある private な開発環境で、Orca から SSH target として扱えるようにしている」というものです。

余談ですが、最初は Orca からこの `ProxyCommand` 経由のコンテナ SSH で port forwarding がうまく動きませんでした。GitHub Issue で相談したところ、すぐに修正されました。

<https://github.com/stablyai/orca/issues/6498>

こういうアップデートの速さも、Orca を使っていて良いところだと感じています。

## secret はファイルに残さない

長生きする開発コンテナを使うなら、secret の扱いはかなり重要です。

自分の場合、credential をコンテナ内やリポジトリ内の物理ファイルに残さないようにしています。基本的には 1Password の `op` CLI を使い、必要なときに環境変数として注入します。

たとえば Tailscale の auth key や SSH authorized keys のようなものも、workspace-local な `.env` に平文で置くのではなく、1Password 参照を使います。

```
TS_AUTHKEY=op://PrivateDev/example/tailscale_auth_key
SSH_AUTHORIZED_KEYS=op://PrivateDev/example/dev_container_authorized_keys
```

起動時は `op run` を通します。

```
op run --env-file /path/to/.env.1password -- docker compose up -d
```

1Password の `op` CLI を使った開発環境の作り方は、以前動画でも少し取り上げました。興味があればこちらも見てみてください。

<https://youtu.be/FgJzWz-cYy0?si=F5j7S2NhDLcfqU23>

こうしておくと、secret の実体をファイルに残さず、必要なタイミングでだけ compose や entrypoint に渡せます。

もちろん、環境変数として渡した時点で、そのプロセスや workspace から見えるものになります。なので、何でも渡してよいわけではありません。最低限のものだけ渡すようにここは注意が必要です。

## base image とプロジェクトごとの依存

この運用で悩ましいのは、どこまでを共通化するかです。

今は、自分がよく使うツール群を入れた base image を作り、その上にプロジェクトごとの依存を足すようにしています。

base image には、たとえば次のようなものを入れます。

* shell / dotfiles
* git / gh / ripgrep / fzf などの CLI
* Codex や Claude Code などの LLM agent
* SSH 接続に必要な最低限の設定

自分の場合、private な image なので公開鍵も base image 側に入れてしまっています。これは一般にすすめたいというより、自分の private な運用では今のところ困っていない、という話です。

そしてプロジェクト固有の依存は project 側で足します。すべてを base image に入れると重くなりますし、どの project のための依存なのか分からなくなりますから。

個人的には、ここが今の時代の開発環境でかなりコアな問題だと感じています。Docker だけできれいに解くのは難しい気がしています。もっとよい設計や運用があればコメント等で教えていただきたいです。

## 個人環境をプロジェクトから分離する

この構成にしてから、個人の開発環境をプロジェクトから分離したほうがよいと感じるようになりました。

DevContainer 的な発想では、プロジェクトの中に Dockerfile や `devcontainer.json` を置きます。これはチームで開発環境を共有するにはよいです。

ただ、開発環境って思った以上に自分用にカスタマイズしたくなるものです（私だけですかね？）

よく使う CLI、shell 設定、agent 用の準備、dotfiles、1Password の使い方、Orca とのつなぎ込み。こういうものを各プロジェクトのリポジトリに入れるべきではありません。

個人のツールをチームやプロジェクトに強制することは基本的にはバッドプラクティスだと思っています（すべてが、というわけではないのですが）。

今の自分の考え方はこうです。

* チームで共有すべきものは、プロジェクト側に置く
* 自分だけが使う開発環境は、プロジェクトから分離する
* base image や workspace 定義は、自分の管理下に置く
* プロジェクトは開発コンテナ内に mount する

チームの開発環境と、個人が LLM エージェントを動かしやすい開発マシンは別物かなと最近は思っています。

ここを分けて考えるのが、ここ最近で一番大きいマインドシフトでした。

## AGW を作った理由

ここまでの構成は、手でやるなら、だいたい次のようになります。

1. base image を用意する
2. workspace ごとに compose を書く
3. host のプロジェクトディレクトリをコンテナに mount する
4. SSH で入れるようにする
5. 1Password の `op run` で必要な secret を注入する
6. Orca に SSH target として登録する

ただ、これを何度もやるのは面倒です。

特に面倒なのは、開発コンテナだけで完結しないところです。

アプリケーションが使う Postgres や Redis などのインフラは、基本的にプロジェクト側に置いてある compose を使います。自分の開発環境コンテナは別の場所で定義していますが、プロジェクト側の Docker network に join することで、開発コンテナから Postgres や Redis に接続できるようにしています。

つまり、管理したいものは 1 つの compose だけではありません。

* 自分用の開発コンテナ
* プロジェクト側の DB / Redis などのサービス
* どの Docker network に join するか
* secret を `op` 経由でどう渡すか
* Orca から SSH target として接続できるか

このあたりを毎回手で思い出すのがつらくなりました。

そこで、自分用に AGW という CLI を作りました。完全なるオレオレツールです。

AGW は Agent の Workspace を以下のように管理できるようにしたものです。

```
id: example
name: example
workspace:
  dir: workspaces/example
container:
  service: dev
  workdir: /workspace
projects:
  - name: example
    hostPath: /Users/me/path/to/project
networks:
  - project_default
lifecycle:
  beforeStart:
    - docker compose -f /Users/me/path/to/project/compose.yaml up -d postgres redis
```

実際の yaml は workspace ごとに変わりますが、考え方としては「開発コンテナを起動する前に、プロジェクト側のインフラを立ち上げる」「必要な network に開発コンテナを join する」という情報を workspace 定義に持たせています。なので毎回各プロジェクトで何を準備するべきか、というのを意識しなくてよくなります。 `agw start <workspace>` を実行することで環境が立ち上がるようにしました。

compose 側では、project の bind mount、home 用の named volume、Tailscale や SSH host key 用の volume、`SSH_AUTH_SOCK`、`TS_AUTHKEY`、`SSH_AUTHORIZED_KEYS` などを扱っています。

AGW がやっているのは、Docker の代替ではなく

* どの workspace があるか
* どの project が対象か
* どの compose service が開発コンテナなのか
* 開発コンテナをどの project network に参加させるか
* 先に起動すべき Postgres / Redis などがあるか

を整理するための薄いレイヤーです。

正直、まだまだ最初のセットアップは面倒です。でもその面倒さを LLM に委譲できる良い時代でもあります。今は AGW 用の Agent Skill を作って、LLM に初期化や診断を任せやすくしています。いったん workspace として定義できると、別の環境にも同じ考え方を持っていけます。

## 良いところ

この構成で特に良いと感じているのは、VS Code を中心にしなくてよくなったことです。（ここがメモリを食いまくって地獄だったので...）

開発環境は SSH で入れる Linux マシンとして存在していて、Orca から worktree を作り、agent を動かせます。

もう 1 つは、worktree を増やしやすいことです。

worktree ごとにコンテナを増やすのではなく、同じ開発コンテナ内に worktree を増やします。project の依存や cache も使い回しやすいです。

そして Orca の SSH worktrees と相性がよいです。remote host 上で agent を動かしつつ、手元では diff や editor や port forwarding を扱えます。体験としては VSCode + Remote SSH + Devcontainers の上位互換な気がしています。

## 割り切り

がしかし、万能ではありません。（お約束）

まず、プロジェクト単位の完全な再現性を目指す構成ではありません。チームメンバー全員に同じ環境を配るのはこのワークフローでは厳しいです。おそらく何かしら環境再現用のツール（miseなど？）を組み合わせることでさらによくなるとは思いつつ、ベストプラクティスにはまだ至っていません。

次に、コンテナを sandbox として過信しないほうがいいです。host mount、SSH agent forwarding、privileged container などを使っていると、境界はかなり弱くなります。あくまで「プロジェクトを動かすための最小限の登場人物に絞ってますよ」くらいな保証しかないです。

secret の扱いにも注意が必要です。自分は 1Password の `op` CLI でファイルに残さないようにしていますが、常にこのあたりに関しては余計な情報を入れてしまっていないか気をつけておく必要があります（これはコンテナに限った話じゃないのですが）

掃除も必要です。長生きする開発コンテナには、cache、生成ファイル、古い worktree、試行錯誤の残骸が溜まります。base imageの作り直しなどを繰り返しているとdocker imageのキャッシュなどゴミが溜まっていって気づいたらホストマシンの容量数百GB専有していたりします。。。

とまぁ気にしておかないといけないこともまだまだあります。。。

## 向いている人、向いていない人

この構成が向いているのは、次のような人だと思います。

* 個人で LLM エージェントをよく使う
* git worktree で並列に作業する
* VS Code ではなく SSH / terminal / ADE 中心で作業したい
* secret や workspace の境界を自分で管理できる

逆に、次の場合は DevContainer のままで大丈夫そうです。

* チーム全員に同じ環境を配りたい
* そもそも並列開発そんなにしないし VSCode で困っていない
* SSH や secret の運用を増やしたくない
* Remote SSH とか使ってないし、 Zed が使えるから軽量で大丈夫

## まとめ

以前は Remote Dev Containers が自分にとって一番合っていると思っていました。

今でも、開発を Linux に寄せる、ローカルを汚さない、リモートから入れる、という方向性は良かったと思っています。

ただ、LLM エージェントを前提にすると、開発環境の中心が変わった気がしています。

コンテナは自分が VS Code でコードを書く場所から、agent が安定して入れる開発マシンへシフト。

Orca から SSH で入り、コンテナ内に worktree を作り、agent を動かす。これが今の自分にはフィットしてます。

ただ、まだまだ完成形ではありません。新しい workspace が必要になったとき、憂鬱です。「ポチッとな」でいい感じにコンテナ開発環境が出来上がるようにしたいです。

というわけで同じように LLM 時代のコンテナ開発環境を考えている人がいれば、ぜひどうしているか聞いてみたいお気持ちでいっぱいです。

ここまで自己満な長文を読んでいただきありがとうございました。引き続き快適な開発環境を目指して精進しつづけたいと思っています。
