---
id: "2026-07-05-ai-エージェントを安全に動かすためのサンドボックス入門-claude-codecodexの仕組みを-01"
title: "AI エージェントを安全に動かすためのサンドボックス入門: Claude Code、Codexの仕組みをきちんと理解しよう！"
url: "https://zenn.dev/koukyosyumei/articles/d6538033062ad5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "AI-agent", "OpenAI", "piping"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-rss"
query: ""
---

## はじめに: Claude Code、Codex、h5i はどこに「壁」を作っているのか

AIエージェントにリポジトリ内でシェルコマンドを実行させるとき、私たちは「人間が書いていないコード」を「人間がレビューする前に実行」していることになります。

エージェントは、間違ったディレクトリで `rm -rf` を実行するかもしれません。怪しい `curl | sh` を走らせるかもしれません。`~/.ssh` の秘密鍵を読み出そうとするかもしれません。あるいは、単純に無限ループでCPUを食いつぶすだけかもしれません。

このときサンドボックスは、「エージェントが何かを試した」と「エージェントが自分のマシンを壊した」の間に置かれる防火壁です。

![](https://static.zenn.studio/user-upload/54ff7ca3e9d3-20260705.png)

Claude Code と Codex は、どちらもAIコーディングエージェントを安全に動かすための仕組みを持っています。しかし、どこに壁を作るのか、どのくらい厚い壁にするのか、そして何を信頼するのかはかなり違います。

この記事では、まずLinuxのサンドボックスで使われる基本的なカーネル機構を整理し、そのうえで [Claude Code](https://github.com/anthropics/claude-code)、[Codex](https://github.com/openai/codex)、そして [h5i](https://github.com/h5i-dev/h5i) がそれらをどう組み合わせているのかを比較します。

---

## 1. サンドボックスを構成する基本部品

現代のLinuxサンドボックスは、単一の機能ではありません。複数のカーネル機構を組み合わせて、それぞれ別の種類の脱出経路を塞ぎます。

![](https://static.zenn.studio/user-upload/4a33a33dcc75-20260705.png)

まずは、よく出てくる部品を整理します。

### Namespaces

Namespace は、グローバルに見えるシステムリソースをプロセスごとに分離する仕組みです。

![](https://static.zenn.studio/user-upload/ab0db6951306-20260705.png)

代表的なものは次の通りです。

* `user namespace` は、UID/GID の対応関係を分離します。これにより、外側では普通のユーザーなのに、サンドボックス内では root のように振る舞うことができます。
* `pid namespace` は、プロセスID空間を分離します。サンドボックス内のプロセスからはホスト側のプロセスが見えず、シグナルも送れません。
* `net namespace` は、ネットワークインターフェース、ルーティングテーブル、ファイアウォールルールを分離します。新しいネットワーク namespace は、基本的に loopback 以外の接続を持ちません。
* `mount namespace` は、ファイルシステムのマウントテーブルを分離します。これにより、ホストとは違うディスクの見え方をプロセスに与えられます。
* `ipc` や `uts` namespace は、System V IPC やホスト名などを分離します。主役ではありませんが、サンドボックスの爆発半径を小さくするためによく使われます。

### Bubblewrap

Bubblewrap、通称 `bwrap` は、小さく監査しやすいサンドボックス用ヘルパーです。新しい namespace を作り、その中でカスタムされたファイルシステムビューを持つプロセスを起動します。

![](https://static.zenn.studio/user-upload/9538a761e6e0-20260705.png)

たとえば次のようなコマンドです。

```
bwrap --unshare-user --unshare-pid --unshare-net \
      --ro-bind / / \
      --bind /home/me/project /home/me/project \
      --proc /proc --dev /dev \
      -- mycommand
```

この場合、`mycommand` から見ると、ディスク全体は読み取り専用です。ただし、明示的に `--bind` したプロジェクトディレクトリだけは書き込み可能です。また、ホスト側のプロセスは見えず、`--unshare-net` によってネットワークも切り離されています。

Bubblewrap は Docker のようなコンテナランタイムではありません。イメージも、デーモンも、レイヤーもありません。あくまで「このコマンドを、制限された視界の中で一度だけ実行する」ための軽量な道具です。

Claude Code と Codex は、Linux 上のファイルシステム分離にこの Bubblewrap を使っています。

### seccomp / seccomp-bpf

`seccomp` は、システムコールを制限する仕組みです。

![](https://static.zenn.studio/user-upload/6eb090359ecf-20260705.png)

プロセスがファイルを開く、ソケットを作る、forkする、カーネルモジュールを読み込む、といった操作はシステムコールを通じて行われます。`seccomp-bpf` では、小さなBPFプログラムを使って、各システムコールを許可するか、エラーにするか、プロセスを殺すかを判断できます。

サンドボックスでは、namespace だけでは塞げない操作を seccomp で止めます。たとえば次のようなものです。

* `ptrace` を止めれば、デバッガの仕組みを使って兄弟プロセスに干渉する攻撃を防げます。
* `io_uring_*` を止めれば、過去にカーネル権限昇格バグの温床になりがちだったインターフェースを塞げます。
* `mount` や `umount2` を止めれば、サンドボックスが作ったマウント構成をプロセス自身が書き換えるのを防げます。
* `socket`、`connect`、`bind` などを止めれば、ネットワーク namespace を使わなくても「ネットワークなし」モードを作れます。

ただし、通常の seccomp-bpf は静的です。判断はシステムコール番号と引数に対する純粋な関数として行われます。そのため、「`github.com` への `connect()` だけ許可する」といった判断はできません。BPFプログラムの中でDNS解決をすることはできないからです。

### seccomp user-notification

`seccomp user-notification` は、より強力で少し珍しい仕組みです。

![](https://static.zenn.studio/user-upload/83e50be115b3-20260705.png)

`SECCOMP_FILTER_FLAG_NEW_LISTENER` を使うと、カーネルがその場で許可・拒否を決める代わりに、対象のシステムコールを一時停止し、ユーザー空間の監督プロセスに通知できます。

監督プロセスは、そのシステムコールを見て、DNS解決をしたり、ポリシーを参照したり、ログを残したり、人間に確認したりできます。そのうえで、カーネルに「許可する」「偽の戻り値を返す」「拒否する」といった判断を返します。つまり、静的な seccomp-bpf ではできない、文脈依存の判断が可能になります。

### Landlock

Landlock は、Linux 5.13 以降で使える比較的新しい Linux Security Module です。非特権プロセスが、自分自身と子プロセスに対してファイルシステムの allowlist を設定できます。

![](https://static.zenn.studio/user-upload/851689e77147-20260705.png)

Bubblewrap のようにマウントを作り替えるのではなく、「このパスは読める」「このパスは書ける」「それ以外は拒否」といったルールセットをプロセスに付与します。

Landlock は unprivileged-friendly で、seccomp や namespace と組み合わせて使えます。ただし、カーネルのバージョンによって対応している ABI が異なります。古い ABI ではファイルシステム制御のみ、新しい ABI ではネットワークポートの制御も加わっています。そのため、実用的なツールでは、実行中のカーネルが何をサポートしているかを起動時に確認する必要があります。

### nftables

`nftables` は、Linux の現代的なカーネル内ファイアウォールです。従来の iptables の後継にあたります。

![](https://static.zenn.studio/user-upload/fc3f567a6f75-20260705.png)

分離されたネットワーク namespace の中に nftables ルールを入れると、特定の IP:port への通信だけを許可し、それ以外をすべて落とすことができます。

これはレイヤー3/4の制御です。つまり、HTTPプロキシを無視して直接ソケットを開くプログラムでも、パケットレベルで止められます。

一方で、nftables は基本的にIPアドレスでフィルタします。そのため、`github.com` を許可したい場合は、事前に名前解決してIPアドレスを固定する必要があります。この設計は、DNS rebinding のような攻撃への対策にもなります。

### slirp4netns

分離された network namespace は、初期状態では外に出る経路を持ちません。`slirp4netns` は、root権限なしでその namespace に外部ネットワークへの経路を与えるためのユーザー空間TCP/IPスタックです。

![](https://static.zenn.studio/user-upload/fe19a010fa20-20260705.png)

rootless container がネットワークに出るときにもよく使われます。典型的には、サンドボックス内のプロセスが `10.0.2.2` のような固定アドレスにあるホスト側プロキシへ接続し、そこから外へ出ていきます。

### socat

`socat` は、TCP、UDP、UNIX socket、ファイルディスクリプタなど、さまざまなバイトストリーム同士を中継する汎用ツールです。

サンドボックスでは、ポリシーを実装するというより、ネットワーク namespace の内外をつなぐ配管として使われます。たとえば、隔離された namespace の中からホスト側のプロキシへ接続するために、UNIX socket やTCP接続を中継する用途です。

### Rootless Podman

Podman はコンテナエンジンですが、Docker と違って root デーモンを必要としません。コンテナは user namespace を使って、ユーザー権限の範囲内で実行されます。

rootless container は、ここまで出てきた機構をまとめて使う重めの選択肢です。イメージベースのルートファイルシステム、namespace による分離、cgroup によるリソース制限、capability の削除などを一つのパッケージとして提供します。

たとえば `--cap-drop=ALL` で全 capability を落とし、`--security-opt=no-new-privileges` で setuid などによる権限上昇を防ぎ、`--read-only` で rootfs を読み取り専用にし、`/tmp` を private tmpfs にする、といった構成が可能です。

### cgroups、rlimits、wall-clock kill

ここまでの仕組みは、主に「何にアクセスできるか」を制限するものです。しかし、プロセスがどれだけリソースを消費できるかは別問題です。リソース制限には、主に `rlimits` と `cgroups` があります。

![](https://static.zenn.studio/user-upload/f3752560684c-20260705.png)

さらに単純な対策として、wall-clock timeout があります。ジョブを専用のプロセスグループで起動し、一定時間を超えたらプロセスグループ全体に `SIGKILL` を送ります。これにより、子プロセスだけが孤児として残るのを防げます。

### Linux 以外の世界

macOS では、Seatbelt と呼ばれるカーネルサンドボックスがあります。`sandbox-exec` を使い、Scheme風のポリシーで「ファイル読み取りは許可、ネットワークは localhost 以外拒否」といった制御を行います。Linux における Landlock と seccomp を粗く合わせたようなものです。

Windows では、Restricted Token、Job Object、Windows Filtering Platform などを組み合わせます。プロセスの権限を削り、プロセスツリーのリソースを制限し、ネットワークをフィルタします。

---

## 2. Claude Code のサンドボックス

Claude Code の基本モデルは、許可・承認ベースの安全機構に、Linux ではオプションのカーネルサンドボックスを組み合わせるというものです。

中心にあるのは permission prompt です。デフォルトでは、Claude Code はコマンド実行前にユーザーへ確認を求めます。ユーザーは、コマンドを許可する、毎回確認する、拒否する、といったルールを与えられます。そのうえで、Linux では Bash tool に対してOSレベルのサンドボックスを有効にできます。

* Linux では、Bubblewrap、socat、seccomp を使って、コマンドごとにファイルシステムやネットワークを制限します。
* 一方で、macOS や Windows では同等のカーネルサンドボックスはありません。そこでの主な防御線は、Claude が実行前にユーザーへ確認する permission model です。つまり「カーネルが禁止する」というより、「Claude が事前に聞く」設計です。

重要なのは、サンドボックスの対象が Bash tool に限られることです。Read、Write、WebFetch、MCP server、hook などは、OSサンドボックスではなく permission layer によって管理されます。

### Claude Code のポリシーは静的設定で決まる

Claude Code のサンドボックス設定は、settings.json の sandbox block によって決まります。ここでは、Bash tool に対して、許可するコマンド、除外するコマンド、ネットワークの許可・拒否ドメイン、UNIX socket の allowlist、HTTP/SOCKS proxy のポート、ファイルシステムの allow/deny、credential の扱いなどを設定できます。

また、permissions block では、ツールごとの allow / ask / deny ルールを静的に定義します。ユーザーや管理者は、どの操作を自動許可するのか、どの操作を毎回確認するのか、どの操作を拒否するのかを設定できます。

企業環境では、MDM などで配布される managed-settings.json が上位に来ます。たとえば、管理された permission rule だけを許可する、管理された domain だけを許可する、bypass permissions mode を無効化するといった制約を、ユーザー側で上書きできない形で適用できます。

つまり、Claude Code における policy source は、ユーザーまたは管理者が書いた設定です。モデル自身ではありません。

### モデルはコマンドを提案するだけ

Claude Code では、モデルは「このコマンドを実行したい」と提案できます。しかし、そのコマンドを許可するかどうかは、静的な permission rule、ユーザーの承認、またはユーザーが書いた hook が決めます。

PreToolUse や PermissionRequest hook を使えば、ユーザーは独自の判定ロジックを書くこともできます。ただし、これも人間が書いた外部コードです。モデルが自分で生成して勝手に適用するものではありません。

さらに、hook は deny rule や managed settings を上書きできません。hook が allow を返したとしても、permissions.deny や管理者設定で拒否されている操作は許可されません。

つまり、Claude Code には「モデルが自分のサンドボックスを広げる」経路はありません。モデルはあくまで propose するだけで、dispose するのはユーザー、管理者設定、静的ルール、または人間が用意した hook です。

### ファイルシステム、ネットワーク、credential

* ファイルシステムについては、denyRead、allowRead、allowWrite のような glob リストで制御します。また、rm -rf / や rm -rf $HOME のような危険な操作は、auto approval が有効でもブロックされるようになっています。
* ネットワークについては、許可ドメイン、拒否ドメイン、HTTP/SOCKS proxy port、UNIX socket allowlist などを使って制御します。新しいホストへの初回接続時にユーザーへ確認することもでき、企業向けには管理されたドメインのみを許可する設定もあります。
* 認証情報については、sandbox.credentials: true により、サンドボックス化されたコマンドが credential file や secret env var を読めないようにできます。
* 一方で、リソース制限は限定的です。Bash には wall-clock timeout を設定できますが、サンドボックス層でメモリ、CPU、PID数を細かく制限するわけではありません。

### サンドボックスが使えない場合

注意すべき点として、サンドボックスが使えない場合の挙動があります。bwrap や socat が見つからない場合、設定によっては警告を出してそのまま実行を続ける可能性があります。過去には、依存関係が欠けているとサンドボックスが実質的に無効になりうる挙動が問題になり、その後、起動時に見える警告を出す方向で修正されています。

### まとめ

Claude Code の設計思想は、かなり明確です。信頼できるアシスタントを人間が監督し、その補助線として Linux ではOSサンドボックスを使う。主役は permission UX であり、カーネルサンドボックスは防御の追加層です。

---

## 3. Codex のサンドボックス

Codex のモデルは、より自動的で、よりOSネイティブです。基本的に、すべてのコマンドがプラットフォームごとのサンドボックス内で実行されます。Claude Code が「承認モデルを中心に、Linuxでは追加のサンドボックスを使う」設計だとすると、Codex は「コマンド実行には必ずサンドボックスを通す」設計に近いです。

* Linux では、Bubblewrap と seccomp を組み合わせます。Bubblewrap がファイルシステムと namespace の視界を作り、その後 `PR_SET_NO_NEW_PRIVS` と seccomp filter によってシステムコールを制限します。
* seccomp では、`ptrace`、`process_vm_readv/writev`、`io_uring_*` などが拒否されます。ネットワーク制限モードでは、AF\_UNIX 以外の socket family をブロックすることで、通常の外向き通信を止めます。
* macOS では、`/usr/bin/sandbox-exec` による Seatbelt を使います。パスをハードコードしているため、PATH の差し替えによる注入を避けられます。ネットワークは loopback と検出されたプロキシポートに制限されます。
* Windows では、restricted token、Job Object、Windows Filtering Platform を使います。

### Codex は sandbox policy と approval policy を分けている

Codex では、ユーザーが設定する軸が大きく二つあります。

一つ目は sandbox policy です。これは「何が許されるか」を決めます。CLI の --sandbox / -s、または config.toml の sandbox\_mode で設定します。代表的なモードは次の通りです。

* read-only はデフォルトのモードです。ディスク全体を読めますが、書き込みはできず、ネットワークも使えません。
* workspace-write は、カレントディレクトリ、/tmp、$TMPDIR などを writable にするモードです。追加の writable root は、[sandbox\_workspace\_write].writable\_roots や --add-dir で指定できます。ネットワークはデフォルトでは無効です。
* danger-full-access は、より広いアクセスを許すモードです。名前の通り、通常の安全なデフォルトとして使うものではありません。

二つ目は approval policy です。これは「誰に聞くか」を決めます。CLI の --ask-for-approval / -a、または approval\_policy で設定します。

* デフォルトは on-request です。これは、モデルが必要だと判断したときにユーザーへ承認を求められるモードです。

重要なのは、sandbox policy と approval policy が別の軸であることです。sandbox policy は許可範囲を決め、approval policy は escalation request をどう扱うかを決めます。

### モデルは escalation を request できるが、決定はできない

Codex では、モデルが per-command escalation をリクエストできます。shell tool の schema には sandbox\_permissions というフィールドがあり、use\_default、require\_escalated、with\_additional\_permissions のような値を取れます。

* use\_default は、通常の sandbox policy に従うという意味です。
* require\_escalated は、そのコマンドをサンドボックス外で実行したいというリクエストです。
* with\_additional\_permissions は、そのコマンドだけファイルシステムやネットワークの権限を広げたいというリクエストです。ただし、これはあくまでリクエストです。モデルが自分で権限を変更できるわけではありません。
* on-request モードでは、ユーザーが承認しない限り escalation は通りません。
* never モードでは、escalation request は即座に拒否されます。
* granular モードでは、ルールによって自動拒否されることもあります。場合によっては、ユーザーに確認すら行かずに拒否されます。

さらに、approval policy が on-request でない場合、handler 側が escalation request を尊重しないようになっています。つまり、「モデルが formal に escalation を要求できる」という点では Claude Code と違いますが、その要求は常に approval policy とユーザーまたはルールにゲートされています。

### ハードコードされた保護

Codex では、設定に関係なく保護される領域もあります。たとえば .git、.codex、.agents は強制的に読み取り専用になります。これは、エージェントが .git/hooks や .codex を編集して、自分自身の権限昇格経路を作ることを防ぐためです。

### ネットワーク

ネットワークについては、サンドボックス内では大きく on/off の制御になります。ホスト単位の細かい allow / deny は、session-approved / denied hosts や managed proxy を使った runtime approval flow として扱われます。つまり、静的なサンドボックス設定そのものに細かな per-host allowlist があるというより、実行時の承認フローとプロキシで制御する設計です。

### リソース制限はサンドボックス層の責務ではない

Codex のサンドボックス層には、メモリ、CPU、PID数、timeout のようなリソース制限はありません。これらは、サンドボックス自体ではなく上位レイヤーで扱う想定です。

### まとめ

Codex の設計思想は、次のようにまとめられます。すべてのコマンドを、自動的に、クロスプラットフォームで、OSネイティブのサンドボックスに入れる。モデルは必要に応じて escalation を request できるが、その可否はユーザー設定と承認ポリシーが決める。

---

## 4. [h5i](https://github.com/h5i-dev/h5i) のサンドボックス

[h5i](https://github.com/h5i-dev/h5i) は比較的新しい AI エージェント向けのサンドボックスツールで、Claude Code や Codex とは少し違う単位でサンドボックスを捉えます。

Claude Code や Codex は、基本的に「個々のコマンド」をサンドボックス化します。言い換えると、実際の作業ディレクトリをそのまま使用し、その中でコマンド単位の制約をかけます。一方、h5i は「作業環境そのもの」を分離の単位にします。

`h5i env` は、専用の Git worktree、専用ブランチ、並行する reasoning branch、policy manifest を持つ、独立した作業環境を作ります。エージェントはその中で作業し、結果は直接メインブランチには入りません。この設計は、複数のAIエージェントを並列に走らせ、結果を比較し、レビューし、最終的に採用する変更だけを選ぶための土台になります。

h5i には、必要な強度に応じた複数の分離ティアがあります。

* `process` tier では、Landlock allowlist、seccomp-bpf denylist、user/pid/net namespace、private `/proc`、rlimits、wall-clock tree-kill を組み合わせます。ネットワークを拒否する場合は network namespace を使います。
* `supervised` tier では、これに加えて seccomp-notify supervisor を使い、さらに nftables による L3/L4 egress 制御と slirp4netns を組み合わせます。DNSで解決したIP:portを固定し、それ以外への通信をパケットレベルで拒否する、より厳密な allowlist を作れます。
* `container` tier では、rootless Podman を使います。`--cap-drop=ALL`、`no-new-privileges`、読み取り専用 rootfs、private `/tmp` tmpfs、`userns keep-id` などを組み合わせた、より重いが強い分離を提供します。あわせて HTTP/HTTPS CONNECT のドメイン allowlist proxy も使えます。

h5i の特徴は、単に「サンドボックスが強い」だけではありません。いくつかの点で、Claude Code や Codex のネイティブサンドボックスとは違う方向を向いています。

### リソース制限を持つ

h5i の process tier は、`RLIMIT_AS`、`RLIMIT_NPROC`、`RLIMIT_CORE` を使って、メモリ、プロセス数、core dump などを制限できます。必要に応じてファイルサイズやCPU時間も制限できます。

さらに、`setsid` でプロセスグループを分離し、wall-clock timeout を超えたら子孫プロセスごと `SIGKILL` します。タイムアウトした実行は exit code 124 として記録され、peak RSS や CPU time などの rusage も残ります。Claude Code や Codex のサンドボックス層には、ここまでのメモリ・CPU・PID制限はありません。

### live syscall gate と packet-level egress を持つ

h5i の supervised tier では、seccomp-notify supervisor が syscall をユーザー空間で仲介します。

さらに egress は nftables によって、解決済みかつ固定済みの IP:port に対してレイヤー3/4で制御されます。つまり、プロセスが `HTTP_PROXY` を無視して直接 raw socket を開こうとしても、パケットレベルで止められます。

静的なサンドボックスでは、ネットワークは基本的に on/off になりがちです。真にドメイン単位の allowlist を packet-level で実現するには、このように DNS 解決と IP 固定、nftables、監督プロセスを組み合わせる必要があります。

container tier の L7 CONNECT proxy は、それを補完するものです。プロキシに従うツールに対しては便利ですが、最も厳密な egress 制御は supervised tier の nftables 側にあります。

### fail-closed する

h5i は、利用可能なカーネル機能を確認するだけでなく、実際に制限されたプロセスを起動して検証します。

Landlock ABI、user namespace、seccomp が存在しているように見えても、実際には confinement が効かない環境があります。たとえばCI上で AppArmor によって user namespace が制限されているケースでは、「機能は見えるが、使うと期待通りに閉じ込められない」ことがあります。

h5i は `verify_exec` によって、実際に confined exec が成立するかを確かめます。閉じ込められない場合は、警告して続行するのではなく、`env create` を失敗させます。

### 認証情報を環境ごとに分離する

Claude や Codex のようなエージェントは、`~/.claude` や `~/.codex` に状態や認証情報を持ちます。複数のエージェントを同時に走らせると、これらのファイルを読み書きして競合する可能性があります。

h5i では、各 env にプライベートなコピーを与えます。最初に実HOMEから seed し、その後はサンドボックス内で本物のパスに bind mount します。ただし、書き戻しはしません。これにより、あるエージェント環境が本物の credential file を破壊したり、別のエージェントの認証情報を読んだりするのを防げます。

さらに、runtime ごとに profile を分けます。Claude 用の環境は Claude の HOME state と Anthropic への egress だけを持ち、Codex 用の環境は Codex の HOME state と対応する egress だけを持ちます。互いの secret は見えません。

### propose / apply のレビューゲートを持つ

h5i では、エージェントの出力が自動的に実ブランチへ入ることはありません。

`env propose` は、canonicalized された `$WORK` path allowlist の内側だけから mediated commit を作ります。このとき、nested `.git`、symlink directory escape、`..`、エージェントが作った gitlink などは拒否されます。そのうえで review brief が作られ、人間または別のエージェントが `env apply` します。

つまり、あるエージェントが変更を提案し、別のエージェントが別クローンでレビューし、最終的に採用する、という cross-agent review loop がサンドボックスのライフサイクルに組み込まれています。

h5i の設計思想は、次のように言えます。信頼しきれない複数のAIエージェントを並列に走らせるための containment substrate を作る。各エージェントには branch-backed な独立環境を与え、ホストは fail-closed し、結果は必ずレビューゲートを通す。

---

## 5. どれが「一番良い」のか

![](https://static.zenn.studio/user-upload/cb2fb2cc3ea0-20260705.png)

結論から言うと、どれが一番良いかは脅威モデルによります。

Codex は、対応範囲が広いです。Linux、macOS、Windows で OS ネイティブのサンドボックスを使い、すべてのコマンドを自動的に包みます。ユーザーが細かい設定をしなくても、クロスプラットフォームにコマンドをサンドボックス化したいなら、Codex の設計は非常に強いです。これは、Linux中心の h5i にとって大きなギャップでもあります。

Claude Code は、強い permission / approval UX と、Linux における実カーネルサンドボックスを組み合わせています。「信頼できるアシスタントを人間が見守りつつ、Linux ではOSレベルの保険もかける」というモデルにはよく合っています。ただし、サンドボックスの対象が Bash tool に限られることと、環境によってはサンドボックスなしで続行しうる点には注意が必要です。

h5i は、Linux-only かつ opt-in である代わりに、防御の層が厚く、マルチエージェントを前提にした設計です。特に次の点は、Claude Code や Codex のネイティブサンドボックスとは異なります。

* メモリ、PID、CPU、wall-clock timeout などの実リソース制限を持つ。
* seccomp-notify supervisor と nftables によって、Layer 3/4 の pinned-IP egress 制御を提供する。
* 機能が存在するかだけでなく、実際に confinement が効くかを self-test し、失敗時は fail-closed する。
* rootless Podman による container tier を持つ。
* コマンド単位ではなく、branch-backed worktree を持つ「環境」そのものを分離単位にする。
* エージェントごとの認証情報分離、並列実行、比較、review brief、propose / apply のレビューゲートを持つ。

まとめると、Claude Code と Codex は、単一の比較的信頼されたエージェントに対して、コマンド実行を安全に包む仕組みを提供します。一方で h5i は、複数のあまり信頼しきれないエージェントを並列に走らせ、それぞれを独立した branch-backed box に閉じ込め、結果をレビューしてから取り込むための基盤です。

どれか一つが絶対に正しいという話ではありません。守りたいものが何か、どのOSで動かすのか、エージェントをどれくらい信頼するのか、そして単一エージェントなのかマルチエージェントなのかによって、適切な設計は変わります。

ただし、AIエージェントが本番コードに触れるようになった今、単に「Git diff をレビューする」だけでは足りません。

* どんなプロンプトで動いたのか。
* どんなコマンドを実行したのか。
* どのファイルに触れたのか。
* どこへネットワーク接続しようとしたのか。
* どんなポリシーが適用されたのか。
* そして、その変更は誰が、どの環境で、どうレビューしたのか。

AIがコードを書く時代には、最終的な diff だけでなく、その diff が生まれた実行環境と証跡そのものをレビュー対象にする必要があります。

Git は差分を記録します。しかし、これから必要になるのは、その差分を生んだエージェント実行の全体を記録し、検証し、必要なら止められる仕組みです。

--

## 参考
