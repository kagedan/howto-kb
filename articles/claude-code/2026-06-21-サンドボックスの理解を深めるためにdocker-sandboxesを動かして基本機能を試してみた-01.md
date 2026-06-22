---
id: "2026-06-21-サンドボックスの理解を深めるためにdocker-sandboxesを動かして基本機能を試してみた-01"
title: "サンドボックスの理解を深めるために、Docker Sandboxesを動かして基本機能を試してみた"
url: "https://zenn.dev/yotaroyotaro/articles/e4b93265692b16"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "GPT", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

今回は、個人開発用に使っている私物のMacBookで、Docker Sandboxesを試してみます。

最近、「ハーネスエンジニアリング」という言葉を聞く機会が増えてきました。  
ざっくりと、AIに毎回人間が細かく指示・承認するのではなく、AIがより自律的に動けるような実行環境や評価の仕組みを整える、という理解しています。特に、安全にAIを動かすための環境づくり、に最近は関心があります。

AIエージェントにコードを書かせたり、コマンドを実行させたりする場合、便利な一方で、ローカル環境のファイルを壊してしまうリスクや、意図しないネットワークアクセスのリスクがあります。

そこで出てくる手段のひとつが「サンドボックス」です。

今回は、そのサンドボックスの選択肢のひとつとして、Docker Sandboxesを使い、Claude Codeを動かしてみます。

Docker Sandboxesは、`claude` コマンドをそのまま実行するのではなく、`sbx run claude` のように実行することで、Claude Codeを隔離されたmicroVM上で動かせる仕組みです。Claude Codeの公式ドキュメントでも、仮想マシンでサンドボックスを作るケースで、Docker Sandboxesが紹介されています。  
<https://code.claude.com/docs/ja/sandbox-environments#virtual-machine>

実際に触ってみると、コマンドに sbx を付けるだけでmicroVMを立ち上げてくれるので、思ったより手軽でした。

# サンドボックスについて

サンドボックスと一言で言っても、どこまで隔離してくれるのかは、利用する機能やツールによってかなり違います。

たとえば、Claude Code自体にもサンドボックス機能があります。Claude Codeのサンドボックスは、OSが提供するセキュリティ機構を使って実現されており、macOSではSeatbelt、Linux / WSL2ではbubblewrapを利用しているようです。

例えば、settings.jsonに以下のような記載をすると、sandbox機能が使えます。

```
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "allowWrite": ["~/.kube", "/tmp/build"]
    }
  }
}
```

これは、ざっくり言うと、Claude Codeが実行するBashコマンドに対して、ファイルシステムやネットワークのアクセス範囲を制限するアプローチと認識をしてます。

一方で、今回利用するDocker Sandboxesは、仮想マシン（VM）で隔離しようという発想です。VMと聞くと重いイメージがありますが、Docker SandboxesではmicroVMという軽量なVMを使う仕組みになっています。

## ローカルでコーディングエージェントを動かすときの隔離レベル

ローカルでサンドボックスを作る場合、どのレベルで隔離されるのか、4つのレベルでまとめてみました。(ChatGPTと対話しながら作りました)

![](https://static.zenn.studio/user-upload/ad0187821065-20260621.png)  
※低レイヤーの知識は、OSの書籍をペラペラ読んだ程度の薄い知識ですので、理解間違っていたら、すみません。

Claude Codeのsettings.jsonに記載するsandboxは、「B. Claude CodeのBashサンドボックス」を想定してます。

Docker Sandboxesは、「D.仮想マシン」のパターンに該当します。仮想マシンなので、ゲストOSが存在するため、ホストOSのカーネルを利用しません。「C.コンテナ」のパターンとの違いは、ゲスト側OSに問題があったとしても、ホスト側には影響が及ばない点だと思います。VMだから絶対安全というわけではありませんが、コンテナよりも一段外側に境界があり、AIエージェントが自由にコマンドを実行するような用途では、安心感が高い選択肢になりそうです。

隔離のレベルを上げるほど安心感はありますが、手軽さとのトレードオフになりそうです。今回試すDocker Sandboxesは、手軽さにも注目して動作確認してみます。

## Docker Sandboxesについて

<https://docs.docker.com/ai/sandboxes/>

Dockerという言葉を聞くと、まずコンテナをイメージする人が多いと思います。自分も最初は、Docker Sandboxesも「AIエージェントをコンテナの中で動かす仕組み」なのかなと思っていました。ただ、Docker Sandboxesは、単純にコンテナを立ち上げる仕組みではなく、microVM上に隔離された実行環境を作る仕組みです。

AI agentを隔離されたmicroVM上で実行され、各サンドボックスが独自のDocker daemon、filesystem、networkを持っています。そのため、基本的に、サンドボックス内で完結させやすくなります。

今回は私物のMacBookを使った個人利用用途なので、無料で使えていますが、業務用途などでは、有料プランが必要になります。詳しくは、以下を確認ください。  
<https://www.docker.com/ja-jp/pricing/>

## Docker以外の選択肢(軽く調べた程度)

Dockerの代替手段の一つであるPodmanでも、同等の機能があるのか、軽く調べてみました。Podmanも、Docker Sandbox相当の機能について議論はされているようですが、現時点で、まだ使いやすい形で提供されているわけではなさそうです。  
<https://github.com/podman-container-tools/podman/discussions/28238>

サンドボックス系のリリース発表は、最近多い印象を持ってます。  
例えば、Microsoftは2026年6月2日のBuild 2026で、Microsoft eXecution Container (MXC)を発表しました。（現時点では、まだ早期プレビュー版です。）  
<https://github.com/microsoft/mxc>

他にも様々サンドボックス系のサービスあると思います。ローカルでサンドボックスを作る以外にも、クラウド上にサンドボックスを作る考え方もあります。

とりあえず、今回は、手軽に試せそうだし、Claude Codeドキュメントにも記載があったので、Docker Sandboxesを使ってみることにします。

# 使い方

前提として、今回はMacにClaude Codeがすでにインストールされている状態から始めます。  
Docker Sandboxesを使う場合は、`claude` コマンドを直接実行するのではなく、`sbx run claude` のように sbx経由で起動することになります。

まずは、Docker Sandboxesをインストールしていきましょう。

```
brew install docker/tap/sbx
```

もし、以下のエラーが出た場合

```
Error: Refusing to load cask docker/tap/sbx@nightly from untrusted tap docker/tap.
Run `brew trust --cask docker/tap/sbx@nightly` or `brew trust docker/tap` to trust it.
```

まず trust してから、installします。

インストールが完了したら、Claude Code を Docker Sandbox 内で起動させます。

初回起動時には、サンドボックスのネットワークポリシーを選択する画面が表示されます。

```
Select a default network policy for your sandboxes:

     1. Open         — All network traffic allowed, no restrictions.
  ❯  2. Balanced     — Default deny, with common dev sites allowed.
     3. Locked Down  — All network traffic blocked unless you allow it.
```

サンドボックス内から外部ネットワークへどこまでアクセスを許可するか、という設定です。

| 選択肢 | 意味 | 向いているケース |
| --- | --- | --- |
| **Open** | 外部ネットワーク全部OK | とにかく詰まらず試したい。でも安全性は低め |
| **Balanced** | 基本は拒否。ただし GitHub / npm / pip / Docker Hub / AI API など開発でよく使う通信は許可 | 普段の開発・Claude Code検証向き |
| **Locked Down** | 全部拒否。必要な通信だけ自分で許可 | かなり厳密に検証したい時向き |

今回は、普段の開発に近い形で試したかったので、Balancedを選択しました。  
選択すると、Claude Codeが起動します。

別のターミナルを開き、以下のコマンドで、サンドボックス一覧を確認できます。

```
SANDBOX                 AGENT    STATUS    PORTS   WORKSPACE
claude-basic-test       claude   running           /docker_sandbox
```

また、`sbx`だけで実行すると、起動しているsandboxとネットワークの設定を見ることができます。

![](https://static.zenn.studio/user-upload/a813c01934f6-20260621.png)

起動するところまでは確認できました。

ちなみに、Claudeに聞いてみたところ、サンドボックス側のゲストOSは、Ubuntu 26.04 LTSを使っているようでした。

サンドボックス内のClaude Codeの回答

```
  コマンド:
  uname -a
  cat /etc/os-release

  結果:
  Linux claude-clone-test 7.0.11 #1 SMP PREEMPT Thu Jun 11 16:46:26 UTC 2026 aarch64 GNU/Linux

  PRETTY_NAME="Ubuntu 26.04 LTS"
  NAME="Ubuntu"
  VERSION_ID="26.04"
  VERSION="26.04 (Resolute Raccoon)"
  VERSION_CODENAME=resolute
```

# 基本的な動作確認

ここからは、Claude CodeをDocker Sandboxes上で起動し、基本的な動作を確認していきます。今回は、以下3点を確認します。

* フォルダがどのように扱われるのか
* ネットワークアクセスがどのように制御されるのか
* サンドボックス内でDockerコンテナを起動した場合、どこで動くのか

ここからの動作確認では、Docker Sandboxesのcloneモードを使ってClaude Codeを起動します。cloneモードでは、Claude Codeを起動したホスト側のフォルダを、サンドボックス内にコピーし、読み取り専用マウントをしてくれます。そのため、ホスト（Mac）側のフォルダ内を直接編集されず、サンドボックス内に閉じることができます。

cloneを指定しない場合は、ホスト側のフォルダを直接マウントし、ホスト側のフォルダ内のデータを直接読み書きできるようです。

| モード | ホスト側のマウント | Claudeの編集先 |
| --- | --- | --- |
| Clone | 読み取り専用 | Sandbox内の専用clone |
| デフォルト | 読み書き | マウントされたホストファイルを直接扱う |

## フォルダの確認

まずは、cloneモードで起動した場合に、ホスト側のフォルダとサンドボックス内のフォルダがどのように見えるのかを確認します。今回試したフォルダの確認をまとめた図も作ってみました。

![](https://static.zenn.studio/user-upload/4ffb2364155d-20260621.png)

今回の検証では、Mac上でのフォルダ構成は、以下のようにしています。

Macのフォルダ構成

```
.../docker_sandbox/
├── README.md
├── docs/
└── sandbox-lab/                
    ├── host-control/
    │   └── sentinel.txt         
    └── claude-workspace/        # ⭐️ ここでsbx claudeを実行
        ├── .git/
        └── sample.txt
```

Mac側で`claude-workspace`フォルダに移動してから、cloneモードで、サンドボックスを起動し、claudeを起動させます。`host-control`フォルダは、機密情報が入っている想定をし、ホスト側からのみ参照でき、サンドボックス側からは、参照も編集もさせたくない想定です。

実際に以下のコマンドで起動させてみます。

```
cd sandbox-lab/claude-workspace

sbx run \
  --clone \
  --name claude-clone-test \
  claude
```

すると、サンドボックスが立ち上がります。

サンドボックス内のフォルダ構成を確認すると、以下のようになっていました。

サンドボックス内（MicroVM）のフォルダ構成

```
.../docker_sandbox/
  └── sandbox-lab/
      └── claude-workspace/            ← git clone されたコピー
          ├── .git/
          └── sample.txt               

/run/sandbox/source/                   ← ホストの読み取り専用マウント
  ├── .git/
  └── sample.txt
```

ホスト側のフォルダ構成と比較すると、`sbx run claude` を実行した `claude-workspace` フォルダが、同じパスのままサンドボックス内にコピーされていることが分かります。このコピーしたフォルダで、Claudeが編集作業をするため、ホスト側のファイルには影響がありません。

ホスト側に存在する`host-control`フォルダはコピーされていません。sbx claudeを実行したフォルダ配下のみをコピーしているようです。

サンドボックス内には、`/run/sandbox/source/` と言うフォルダが存在しました。ここは、ホスト側の`claude-workspace`を読み取り専用でマウントしています。そのため、Macで直接`sample.txt`を編集すると、変更が反映されます。ただし、サンドボックス内からは、編集できません。

サンドボックス内でClaudeに、ホストとmicroVM間のファイル共有をどう実現しているのか、聞いたところ、どうやら `virtiofs` という技術を使っているようでした。

## ネットワークの確認

次に、サンドボックス内から外部ネットワークへどのようにアクセスできるのかを確認します。ネットワークの確認も、まとめた図を載せておきます。  
![](https://static.zenn.studio/user-upload/7836a9b94439-20260621.png)

`example.com` を許可して接続確認してみます。

```
sbx policy allow network --sandbox claude-clone-test example.com
sbx exec claude-clone-test curl -I --max-time 10 https://example.com
```

HTTPレスポンスが返ってくれば、許可ルールが機能していることが分かります。

```
HTTP/1.0 200 Connection established
...
```

次に、拒否ルールを確認してきます。同じ宛先のAllowとDenyを同時登録できないようなので、Allowを削除してからDenyを追加します。

```
sbx policy rm network --sandbox claude-clone-test --resource example.com
sbx policy deny network --sandbox claude-clone-test example.com
sbx exec claude-clone-test curl -I --max-time 10 https://example.com
```

HTTPレスポンスから拒否ルールが機能しています。

```
HTTP/1.1 403 Forbidden
...
```

ちなみに、`sbx`を実行すると、`example.com`がBlockedされていることがわかります。

![](https://static.zenn.studio/user-upload/295b02ed9e80-20260621.png)

サンドボックスごとにネットワークアクセスの許可・拒否を設定できるので、便利ですね。

## コンテナの起動

最後に、サンドボックスのmicroVM内でDockerコンテナを起動できるか確認してみます。こちらも、図に動作確認内容をまとめてみました。  
![](https://static.zenn.studio/user-upload/39a48d783438-20260621.png)

サンドボックス内で、nginxのコンテナ「simple-nginx」という名前で起動させていきます。

```
sbx exec claude-clone-test \
  docker run -d \
  --name simple-nginx \
  -p 8080:80 \
  nginx:alpine
```

状態を確認してみます。

```
sbx exec claude-clone-test docker ps
```

```
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                                     NAMES
xxxxxxxxxxxx   nginx:alpine   "/docker-entrypoint.…"   43 seconds ago   Up 43 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   simple-nginx
```

起動していました。ホストのMac側では、simple-nginxは起動してません。docker psコマンドで確認できます。

```
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                                     NAMES
# simple-nginx は表示されない
```

つまり、サンドボックス内で実行した docker runは、ホスト側MacのDocker daemonではなく、microVM内のDocker daemonに対して実行されていることが分かります。

サンドボックス内から、コンテナに接続できることを確認します。

```
sbx exec claude-clone-test \
  curl -I http://localhost:8080
```

Mac側からもサンドボックス内のコンテナにアクセスを試してみますが、アクセスはできません。

```
curl -I http://localhost:8080
```

```
curl: (7) Failed to connect to localhost port 8080 after 0 ms: Couldn't connect to server
```

ただし、Macからサンドボックス内のコンテナにアクセスする手段もあります。`sbx ports`で明示的にポートを公開します。以下を実行することで、「ホスト:8080」->「サンドボックスVM:8080」->「コンテナ:80」の流れでアクセスが可能になります。

```
sbx ports claude-clone-test \
  --publish 8080:8080/tcp
```

再びcurlコマンドを実行してみると。接続できました。

```
curl -I http://localhost:8080
```

Docker Sandboxesでは、サンドボックス内でDockerコンテナを起動できる一方で、そのコンテナはホスト側MacのDocker環境とは分離されていることが分かりました。

# まとめ

今回は、Docker Sandboxesの基本的な動作確認をしてみました。

使い始める前は、VMを立ち上げた後、毎回、Claude Codeをインストールし、認証して、...と言う手間のかかるステップを踏むのかと思っていましたが、`sbx`コマンドで、claudeを起動するたびに、MicroVM内でclaudeが立ち上がってくれ、手間はかからず、予想以上に使いやすい良い印象でした。

正直なところ、自分自身もサンドボックス周りの理解はまだ薄いところがありました。ただ、小さく手を動かして、フォルダ、ネットワーク、コンテナの挙動をひとつずつ確認してみると、やはり理解が深まるなと感じました。

コーディングエージェントを使うときに、どのレベルのサンドボックスを使うべきかは、AIにどこまで自律的に動いてもらいたいかによって変わりそうです。たとえば、GitHubと連携させて、サンドボックス上でIssueを読み、バグ修正を行い、テストを実行し、PRまで作ってもらう、のような使い方をするなら、Docker SandboxesのようにmicroVMで隔離された環境はかなり相性が良さそうです。

一方で、人間が常に横で確認しながら、コーディングエージェントとペアプログラミングするような使い方であれば、必ずしもVMレベルの隔離までは必要ないケースもありそうです。

もちろん、安全性を考えると隔離レベルは高いに越したことはありません。ただし、そのぶんセットアップや運用の複雑さも増えるので、用途に応じて使い分けるのが大事そうです。

---

最後に、今回の内容とは関係ないですが、Zennの投稿前に、aiレビュー機能試してみました。スペルミスや表記揺れの指摘してくれて、とても便利でした！
