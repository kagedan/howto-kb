---
id: "2026-06-26-第13回hermes-agentとobsidianを連携して知識を共有する方法-01"
title: "【第13回】Hermes AgentとObsidianを連携して知識を共有する方法"
url: "https://zenn.dev/sora_biz/articles/hermes-vps-13-obsidian"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "Python"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

## 目次

第12回でHermes本体のMemory機能を入れ、USER.mdとMEMORY.mdの2枚に「私のこと」と「環境ファクト」を覚えさせた。frozen snapshotで毎セッション自動注入される設計のおかげで、新しいチャットを開くたびに自己紹介をやり直す必要はもうない。ただ、Memoryの上限は合計3,575字しかない。気になった記事の保存、論文や調べごとのメモ、過去の議事録、書きかけの下書き──こうした「長く残しておきたい情報」までUSER.mdに詰め込もうとすると、すぐに上限を食い潰す。

第13回はそこに「外付け脳」を足す。HermesにObsidian Vaultを読ませ、Memoryに収まらない長く残しておきたい情報を別カテゴリで持てるようにする。設定は`~/.hermes/.env`に1行追加するだけだ。skillはHermes本体にbundledで入っているので、新規インストールは要らない。

シリーズの全体像はこちら。

シリーズのもくじ(タップで開く)

**第I部 体を作る**

* [第1回](https://zenn.dev/sora_biz/articles/hermes-vps-01-deploy) Hermes AgentをVPSにデプロイする方法
* [第2回](https://zenn.dev/sora_biz/articles/hermes-vps-02-tailscale) Hermes Agentの接続を安全にする方法
* [第3回](https://zenn.dev/sora_biz/articles/hermes-vps-03-1password) Hermes Agentの認証情報を安全に管理する方法
* [第4回](https://zenn.dev/sora_biz/articles/hermes-vps-04-install) Hermes AgentをDockerで隔離して動かす方法
* [第5回](https://zenn.dev/sora_biz/articles/hermes-vps-05-oauth-discord) Hermes AgentにGrokとDiscordを連携させる
* [第6回](https://zenn.dev/sora_biz/articles/hermes-vps-06-systemd) Hermes Agentをsystemdで常時起動させる方法

**第II部 顔と操作席**

* [第7回](https://zenn.dev/sora_biz/articles/hermes-vps-07-desktop) Hermes Agentをデスクトップアプリで操作する方法
* [第8回](https://zenn.dev/sora_biz/articles/hermes-vps-08-dashboard) Hermes AgentをWeb Dashboardで管理する方法

**第III部 生活リズム**

* [第9回](https://zenn.dev/sora_biz/articles/hermes-vps-09-cron) Hermes Agentに毎朝のタスクを自動実行させる
* [第10回](https://zenn.dev/sora_biz/articles/hermes-vps-10-skills) Hermes Agentが使うほど賢くなるSkillsの登録方法
* [第11回](https://zenn.dev/sora_biz/articles/hermes-vps-11-web-search) Hermes Agentに最新情報を自動取得させる方法

**第IV部 記憶を分けて育てる**

* [第12回](https://zenn.dev/sora_biz/articles/hermes-vps-12-memory) Hermes AgentにMemoryで好みと前提を記憶させる
* **第13回**(本記事) Hermes AgentとObsidianを連携して知識を共有する方法

全体像は[Hermes Agent完全構築ガイド](https://zenn.dev/sora_biz/articles/hermes-vps-complete-guide)にある。

手を動かすのは、SSHで`~/.hermes/.env`に1行足してHermesを再起動するだけだ。あとはTelegramから「Vaultにメモを書いて」と頼めば、エージェントがbundled `obsidian` skillを使ってVault内に.mdファイルを作る。

## この回の到達点

第12回完了時と第13回完了後の差分を表にする。

| 項目 | 第12回完了時 | 第13回完了後 |
| --- | --- | --- |
| 記憶できる範囲 | 「私のこと」(USER.md 1,375字)+「環境ファクト」(MEMORY.md 2,200字) | +「世界のこと」(Obsidian Vault・字数無制限の知識ベース) |
| 記憶の置き場 | VPS内の`~/.hermes/memories/`のみ | +母艦のObsidian Vault(VPSとgitで同期) |
| HermesがVaultを読むか | 読まない | bundled `obsidian` skillでVault内.mdをファイル直アクセスで読み書き |
| 3エージェント共有 | VaultはClaude Code/Codexの個別管理 | 同じVaultをHermes/Claude Code/Codexの3つで共用(本格実装は第20回予定) |
| 配布対象 | USER.md/MEMORY.mdは個人所有で配布除外 | Vaultも同じく個人所有で配布除外(第37回Profile Distributionsで詳述) |

一言でまとめると「Hermesに、Memoryに収まらない長く残しておきたい情報の置き場を持たせる」回だ。

この回で出てくる用語を先に押さえておく。

| 用語 | 意味 |
| --- | --- |
| Vault(ボールト) | Obsidianが管理するノートの置き場。物理的にはMarkdownファイル(.md)が並んだフォルダ。1つのVault=1つの「外付け脳」 |
| bundled skill | Hermes本体の`.bundled_manifest`に登録されているskill。`obsidian`はその1つ。多くの場合は実体までシードされて`hermes skills list`に出るが、初期インストール時の状況によっては実体だけ未シードで`reset --restore`が必要なことがある |
| `OBSIDIAN_VAULT_PATH` | HermesがどのVaultを読むかを指定する環境変数。本回ではSKILL.md標準のフォールバック先をそのまま使うため設定不要 |
| Wikilink | Obsidianのノート間リンク記法。`[[ノート名]]`で他のノートを参照する。AIはこのリンクをたどって文脈を組み立てる |
| 5項目テンプレ | AIに読ませるノートの基本構造。Title/Summary/Source/Context/Links/Next Actionの5つの見出しで揃える |

## なぜObsidianを連携するのか

第12回で入れたMemoryには容量の上限がある。気になった記事や調べごと、長い記録をすべてUSER.mdに記憶させようとすると、すぐに1,375字を食い潰してしまう。Obsidianは「世界のこと」を貯める層として、Memoryと別カテゴリで持つ。

### Memory三層では届かない「知識」の置き場

第12回のMemoryは三層(Markdown第1層・SQLite第2層・外部provider第3層)で構成されるが、合計でも数千字の規模だ。「名前はそら」「妻と高校生の娘」のような人物カードは収まる。だが「先週調べたAWSコスト最適化の記事」「半年前に読んだ建築の論文」「自分が書いた過去のZenn記事の下書き」までMemoryに入れようとすると、たちまち容量を食い潰す。

気になった記事や調べごと、書き溜めたメモは、Memoryではなく別の層に置くのが筋だ。それがObsidian Vault=外付け脳になる。容量制限はファイルシステムの空きだけで、何万字でも入る。

### 「私のこと」と「世界のこと」を分ける

分け方をひと言で書くとこうなる。

| 層 | 覚えるもの | 例 |
| --- | --- | --- |
| Memory(USER.md/MEMORY.md) | 私のこと=毎セッション必要な前提 | 名前・年齢・家族構成・好み・主な仕事・記事の文体ルール |
| Obsidian Vault | 世界のこと=長期保存したい知識 | 気になった記事のメモ・調べごとの記録・書きかけの下書き・プロジェクトの設計メモ |

Memoryは毎セッション開始時にfrozen snapshotで自動注入される=「毎日カバンに入れて持ち歩く必需品」。Vaultはskill経由で必要なときだけ参照する=「家のクローゼットに整理してしまう大量の資料」。役割が違うから両方持つ。

## 4つの比喩で全体像を1分で

第IV部全体(第12回〜第19回相当)の境界を1分で理解するための4つの比喩を置いておく。これを頭の地図にしておくと、本回も次回以降も「あ、これは付箋の話か。書庫の話か。手順書の話か」と即座に判別できる。

| 比喩 | Hermes機能 | 役割 | 本連載の該当回 |
| --- | --- | --- | --- |
| 📝 付箋 | Memory(USER.md/MEMORY.md) | 短い前提・毎回使うもの・手元に貼っておく | 第12回 |
| 📚 書庫 | Obsidian Vault | 長いログ・調査・長期保存・棚から引き出す | **本回(第13回)** |
| 📋 手順書 | Skills | 「こう動く」のレシピ・状況に応じて取り出す | 第10回・第18回予定 |
| 🧹 棚卸し | Cron | 定期的に整える・古いものを片付ける・新しいものを足す | 第9回・第19回予定(Curator) |

第12回(付箋)→第13回(書庫)→第14回予定(過去会話の検索=書庫の検索)→第17回予定(人格=書庫を読む側の癖)、と並ぶ。本回(書庫)は付箋(第12回)の隣に置く分担の話だ。

## 第13回終了時点の構成図

HermesとObsidian Vaultがどう繋がるかを俯瞰する。第12回で書いた三層メモリ(Markdown/SQLite/外部provider)の右隣にObsidian Vaultが別カテゴリで並ぶ。

![Hermes Agentの内蔵メモリ(三層=Markdown/SQLite/外部provider)とObsidian Vault(外付け脳・母艦ローカル)が、bundled obsidian skill+ホスト側symlinkを介して役割分担する構成図](https://static.zenn.studio/user-upload/deployed-images/880f225398045f7b0fa3cc93.png?sha=ded4a258efc3671e1fc307aabbf55d4faafc4d85)

接続レイヤーは4つだが、本回の主役は上2つだけだ。

| レイヤー | 役割 | 本回での扱い |
| --- | --- | --- |
| bundled `obsidian` skill | HermesがVault内の.mdをファイル直アクセスで読み書きする手順書 | 主役 |
| `OBSIDIAN_VAULT_PATH`環境変数 | どのVaultを読むかを指定する1行設定 | 本回では使わない(SKILL.mdのフォールバック先をそのまま採用) |
| Obsidian MCPサーバー | Obsidianプラグイン経由のAPI(検索・グラフ操作) | 本回は使わない |
| git同期 | 母艦のVaultとVPS側のVaultを揃える | 基本のgit push/pullを扱う |

## 事前準備

第12回までが完了していれば、追加で入れるものはない。VPSへSSHで入って稼働を確認し、母艦のObsidian Vaultの場所を控える。

### VPSの実機バージョン確認

```
ssh -i ~/.ssh/hermes_vps_ed25519 admin@hermes-vps

hermes version                                  # v0.17.0(2026.6.19 The Reach Release)以降を確認
systemctl --user status hermes-gateway          # active (running)
```

![ターミナルでhermes versionを実行した結果。Hermes Agent v0.17.0(2026.6.19)upstream bb7ff7dc、Project /home/admin/hermes-agent、Python 3.11.15、OpenAI SDK 2.24.0、Up to date が並ぶ画面](https://static.zenn.studio/user-upload/deployed-images/06dcf6c8201f9db0e6d05997.png?sha=33a062e695b3fae79c8366c14d0f0c4d5671a458)

v0.17.0より古いバージョンが出る場合は、`hermes update`で本体を最新に上げてからやり直す。v0.17.0ではOffice読み込みのread\_file拡張など、本回のObsidian連携と相性のいい機能がいくつか追加されている。

### 母艦のObsidian Vaultの場所を控える

母艦(普段使っているノートPC)でObsidianを起動し、Vault管理画面でVaultの絶対パスを確認する。Windowsなら`C:\Users\sora\Documents\Obsidian Vault\`のような場所が一般的だ。

Obsidianを未導入なら公式サイトから入れてVaultを1つ作る。中身は空でよい。

![母艦の画面を左右に並べた様子。左はWindowsエクスプローラーでにフォルダと空の(0 KB・新規作成時の自動生成ファイル)が並ぶ画面・右はObsidianアプリでHermes-Vaultを開いた直後の画面で「無題のファイル」タブが1つ・本文は空](https://static.zenn.studio/user-upload/deployed-images/66f2c7a360873991716a239a.png?sha=0e0eba018c4fcc52a5a18658437c13a11fb0987e)

このあとの§7では「VPS側にVault実体を作り、`/home/admin/hermes-vault`からショートカットで読み書きできる形にする」手順を扱う。母艦のパスをそのまま転記するわけではない。母艦とVPSのVaultを揃えるのは§11で扱うgit同期の役目だ。

## bundled obsidian skillの確認

Hermes本体の`~/.hermes/skills/.bundled_manifest`には`obsidian`がbundled skillとして登録されている。多くの場合は`~/.hermes/skills/note-taking/obsidian/SKILL.md`に実体がシードされていて`hermes skills list`に並ぶが、初期インストール時の状況によってはmanifestに登録されているのに実体だけシードされていないことがある(v0.17.0実機で観測)。まずskillが存在することを確認し、無ければ復旧してから先に進む。

### skill一覧でobsidianを探す

出力の中に`obsidian`(`note-taking`カテゴリ)があれば配置済みで、そのまま§7に進める。

もしobsidianが出ない場合は、manifestに登録があっても実体ファイルがシードされていない状態だ。次のコマンド1発で復旧する。

```
hermes skills reset obsidian --restore --yes
```

このコマンドは`.bundled_manifest`の`obsidian`エントリを参照して、`~/.hermes/skills/note-taking/obsidian/`配下に実体ファイル一式を再コピーする。実行後にもう一度`hermes skills list`を打つとobsidian行が並ぶ。

![ターミナルでhermes skills listを実行した結果。表形式の出力にobsidian行が並んでいる画面。Categoryはnote-taking、Sourceはbuiltin、Trustはbuiltin、Statusはenabled](https://static.zenn.studio/user-upload/deployed-images/8ac68252b445a5acbe0fb91e.png?sha=2506b8df69e1443e506ba7be7ffa2c8ba933096b)

### SKILL.mdの中身を確認する

```
cat ~/.hermes/skills/note-taking/obsidian/SKILL.md
```

冒頭のYAMLフロントマター(`---`で囲まれた領域)で、必要な環境変数(`OBSIDIAN_VAULT_PATH`)、未設定時のフォールバック(`~/Documents/Obsidian Vault`)、使うツール(`search_files`/`read_file`/`write_file`/`patch`)が宣言されている。

![ターミナルでcat ~/.hermes/skills/note-taking/obsidian/SKILL.md | head -20 を実行した結果。冒頭のYAMLフロントマター(name obsidian / description Read, search, create, and edit notes in the Obsidian vault. / platforms [linux, macos, windows])の下に、Obsidian Vault見出し+概要+Vault path節(OBSIDIAN_VAULT_PATH環境変数とフォールバック~/Documents/Obsidian Vault)+file toolsの注意書きが並ぶ画面](https://static.zenn.studio/user-upload/deployed-images/60aac485b3ea5571d1dabab4.png?sha=6278af7a739f2043d11b43fda6a9ab61fc2c67da)

## Vault実体の準備

Hermes本体は標準で`~/Documents/Obsidian Vault`という場所にVaultがあると想定して動く(bundled obsidian skillに記載されたフォールバック先)。VPSのHermesはコンテナ内でこのpathを見るため、ホスト側の実体は`~/.hermes/sandboxes/docker/default/home/Documents/Obsidian Vault/`という長いpathに置く。

毎回この長いpathを打つのは大変なので、`/home/admin/hermes-vault`からショートカット(symlink)を1本張って、短いpathで読み書きできる形にする。

### 実体ディレクトリの作成

VPSにSSHで入った状態で、Hermesが書く実体ディレクトリを作る。

```
ssh -i ~/.ssh/hermes_vps_ed25519 admin@hermes-vps
mkdir -p ~/.hermes/sandboxes/docker/default/home/Documents/Obsidian\ Vault
```

末尾の`\` は「半角スペース」を含むpathを正しく扱うためのエスケープ記号(`Obsidian Vault`の間のスペース)。

### ショートカット(symlink)の作成

長いpathを毎回打たなくて済むよう、`/home/admin/hermes-vault`からショートカットを張る。

```
ln -sf ~/.hermes/sandboxes/docker/default/home/Documents/Obsidian\ Vault /home/admin/hermes-vault
ls -la /home/admin/hermes-vault
```

`ls -la`の出力で`lrwxrwxrwx ... /home/admin/hermes-vault -> /home/admin/.hermes/.../Obsidian Vault`の形が出ればOK(`l`はsymlinkの印・`->`の後に実体pathが見える)。

![ターミナルでを実行した結果。先頭がから始まるsymlinkを示す行で、矢印の後にサンドボックス配下の実体pathが表示されている。プロンプトのホスト名は黒塗りマスク済](https://static.zenn.studio/user-upload/deployed-images/fcb46eba8c9601e4da3c5815.png?sha=e8381cc9f418acc7850d68d3210854cc49dcaea3)

これで`/home/admin/hermes-vault`から書庫の中身を読み書きできる状態になった。Hermesがコンテナ内で`~/Documents/Obsidian Vault`に書いたファイルは、ホストではsymlink経由で`/home/admin/hermes-vault`にも同時に見える(物理的には同じファイル)。

## 4経路の整理

HermesとObsidianの接続経路は混乱しやすい。本回で使うのは「skill+環境変数」の2本柱だけだが、ほかの選択肢の存在を整理しておく。

### skill経由(主役)/環境変数/MCP/git同期

| 経路 | 役割 | 本回での扱い |
| --- | --- | --- |
| bundled `obsidian` skill | HermesがVault内の.mdをファイルアクセスで読み書きする | 主役。§6で確認・§9で動作確認 |
| `OBSIDIAN_VAULT_PATH`環境変数 | どのVaultを読むかを指定する | 本回では使わない(SKILL.mdのフォールバック先をそのまま採用・将来の発展回で扱う) |
| Obsidian MCPサーバー | Obsidianプラグイン経由のAPI(検索・グラフ・タグ操作) | 本回は使わない。skill主軸で十分 |
| git同期 | 母艦のVaultとVPSのVaultを揃える | §11で扱う(基本=git push/pull手動) |

![ターミナルでを実行した結果。MCP Servers見出しの下にName/Transport/Tools/Status列のテーブルが1行だけ並び、agentwikis (npx -y agentwikis-mcp/all/✓ enabled)のみ表示。Obsidian用MCPは存在しない](https://static.zenn.studio/user-upload/deployed-images/caedc93c2166a1cfff5ae6c4.png?sha=cc322f507d6c45f74d516e06797420ad7dc32841)

MCPサーバー経由のObsidian連携は、リアルタイム検索やグラフ操作が必要になったときの選択肢だ。本連載は当面skill主軸で運用する。

### memory providerにobsidianが入らない理由

第12回§12で外部memory provider 8つ(byterover/hindsight/holographic/honcho/mem0/openviking/retaindb/supermemory)を概観したが、この一覧に`obsidian`は入っていない。

```
hermes memory --help
# providers: honcho, openviking, mem0, hindsight, holographic, retaindb, byterover, supermemory
```

![ターミナルでを実行した結果。usageとサブコマンド(setup/status/off/reset)の説明文の中に「Available providers: honcho, openviking, mem0, hindsight, holographic, retaindb, byterover」と並び、Obsidianはこのprovider一覧に含まれていない](https://static.zenn.studio/user-upload/deployed-images/6e442e545bd3e450474e0752.png?sha=a4939dc419a382aa6ac8586eecea4f787deef3ab)

Obsidianはmemory providerではなく、note-taking skillとして提供されている。第12回の表現で言えば「第3層(外部provider)」ではなく「別カテゴリ(外付け脳)」だ。memoryコマンドで設定するものではない。Vault連携はbundled obsidian skill(§6)+ホスト側symlink(§7)の2本立てで行う。これが正しい経路だ。

## 動作確認──HermesにVault参照を依頼

設定が効いているかをTelegramからHermesに頼んで確認する。VPS側のVaultにファイルが実際に生成されるかを`ls`で確認するまでが本章の射程だ。

### TelegramからVault参照を依頼する

母艦からTelegramを開いて、Hermesに頼む。

```
Hermesテストノートを作って。タイトルは「Hermes動作テスト」、本文に「2026年6月24日、第13回でObsidian連携を試した」と書いて、Vaultに保存して。
```

![母艦からTelegramでHermesに依頼した直後の画面。依頼テキストの下にHermesの応答が並び、skill_view obsidian+terminalでecho +を実行した後、write_file で保存完了。最終応答に保存先パスとノート本文プレビューが含まれている](https://static.zenn.studio/user-upload/deployed-images/b66958b1ec9ad22ff1183cc8.png?sha=c063f6550d5ab4de94b39ffa85bee22c6c12f9cf)

エージェントはSKILL.mdの手順に従って、内部で`write_file`ツールを呼びVault内に.mdファイルを書き込む。Telegramには「保存しました」のような自然文で応答が返ってくる。応答の本文にVaultパスとファイル名が含まれていれば成功だ(Hermesの応答に出る`/root/hermes-vault`はコンテナ内のビュー・ホスト側ではsymlink経由で`/home/admin/hermes-vault`から同じファイルが見える)。

### 母艦とVPSのVaultで実体を確認する

VPS側でファイルが実体として作られたか確認する。

```
ls -la /home/admin/hermes-vault/
# Hermes動作テスト.md のようなファイルが増えている
cat /home/admin/hermes-vault/Hermes動作テスト.md
```

![ターミナルでを実行した結果。の下にとに続いてが並んでいる。所有者はadmin:adminで、sudoなしで読める。プロンプトのホスト名は黒塗りマスク済](https://static.zenn.studio/user-upload/deployed-images/c1642c06817d5dbb23a403ec.png?sha=a041e64996b59bf79c8780d4eaa0996c0713ff67)

母艦のObsidianとVPSのVaultを§11のgit同期でつなげば、ここで作られたノートが母艦のObsidianアプリにも現れる。Hermesが「私の代わりにノートを書く」が動いた瞬間だ。

## AIが読めるノートの書き方

Vault接続ができたら、次の問いは「で、何を書けばいいのか」になる。AIが迷わず読めるノートには共通の構造がある。実機運用で確認された設計パターンとして、5項目テンプレと「AIが迷うノート4特徴」を紹介する。

### 5項目テンプレ──Title/Summary/Source/Context/Links/Next Action

1枚のノートに次の5つの見出しを置く。これだけでHermes・Claude Code・Codexの3エージェントが再利用しやすい構造になる。

```
# Title(対象と用途が分かるもの)

## Summary
このノートは何か。3行以内。

## Source
どこから来た情報か。URL・書籍名・会話・日付など。

## Context
なぜ保存したか。自分の目的・前提・判断材料。

## Links
関連ノート・プロジェクト・人物・記事。
[[ノート名]] 形式で他のノートを参照する。

## Next Action
AIまたは自分が次に何をすればいいか。
```

![母艦のObsidianでVault「Hermes-Vault」を開き、5項目テンプレを当てたを表示している画面。Title/Summary/Source/Context/Links/Next Actionの6見出しが本文中に並び、それぞれに雛形テキスト(「対象と用途が分かるもの」「3行以内」「URL・書籍名・会話・日付など」など)が入っている。左ペインはファイルリスト、左下にVault名「Hermes-Vault」、右下は文字数カウンタ](https://static.zenn.studio/user-upload/deployed-images/7f40cca737a36a374538635d.png?sha=8c54b794690263e251fc92e07550c24b2251025f)

5項目それぞれが、AIにとって判断材料になる。SummaryでノートのID、Sourceで信頼度、Contextで目的、Linksで他文脈、Next Actionで作業指示。これらが分離して書かれていれば、AIは「事実」と「自分の解釈」と「次の作業」を取り違えない。

### AIが迷うノートの4特徴

裏返しに、次のような書き方をするとAIは判断に迷う。

| 特徴 | 何が問題か |
| --- | --- |
| タイトルがあいまい | 「AIメモ」「あとで読む」のような汎用タイトル。AIは「これは何の話?」を本文を全部読まないと判断できない |
| 出典・引用・感想が混ざっている | 「事実」「自分の解釈」「次の作業指示」が同じ段落に並ぶ。AIは「これは事実か感想か」を取り違えやすい |
| 関連リンクがない(孤立ノート) | 1枚で完結していて他のノートと繋がっていない。AIは文脈を組み立てられない |
| Next Actionが書かれていない | 「で、次に何をすればいい?」がノートに書かれていない。AIに作業を任せようとすると毎回プロンプトに足す必要がある |

### テンプレ適用前後の比較

5項目テンプレの有無で、同じ題材のノートがどう変わるかを見比べる。たとえば「Hermes Agentを調べた」という同じ題材を、雑に書いたAIメモと、5項目テンプレで整理したノートで並べてみる。

**適用前(雑なAIメモ)**

![母艦のObsidianでVault「Hermes-Vault」を開き、を表示している画面。本文は「最近Hermes調べた。よさそう。あとで読む記事=https://...」「インストール簡単」「設定ファイル多い気がする」「明日続きやる」が連なる短いメモ。タイトル「AIメモ」だけでは中身がわからず、事実(調べた)・解釈(よさそう)・作業指示(明日続きやる)が同じ段落に混ざる。左下にVault名「Hermes-Vault」、右下は46ワード・70文字のカウンタ](https://static.zenn.studio/user-upload/deployed-images/45372fee219691e096681c7b.png?sha=f7b7468bf946bda6abc89b33c96b77124543a499)

「最近Hermes調べた」「あとで読む記事」「明日続きやる」が同じ段落に並ぶ。これだけ見せられても、自分でもAIでも「これは何の調査結果なのか/次に何をすればいいのか」が判定できない。

**適用後(5項目テンプレ整理)**

同じ題材を§10-1のテンプレで書き直したのが、§10-1冒頭で示した`Hermes Agent調査.md`だ。Title/Summary/Source/Context/Links/Next Actionの6見出しに沿って書き直すと、AIが読んだとき「これは何のノートで、自分は次に何をすればいいか」が1秒で判定できるようになる。同じVault内で2つのノートを並べておくと、自分自身も「テンプレを当てる前のメモ」と「当てた後のメモ」をタブ切替で行き来できる。

## 母艦とVPSのVault同期

母艦のObsidianで書いたノートをVPSのHermesに読ませる、あるいはVPSのHermesが書いたノートを母艦のObsidianで開く。両方を同じVaultにする手段が必要だ。基本はgitで揃える。

### git双方向push/pull(基本)

母艦とVPSの両方で同じgitリポジトリをcloneし、変更があるたびに`git push`+`git pull`で同期する。GitHubでprivate repositoryを1つ作り、両方からcloneする想定だ(Vaultは個人所有の知識ベースなので必ずprivateにする)。認証はGitHubが提供する`gh` CLIに任せる(SSH鍵を別途生成して登録する手間を省ける・非エンジニアにとってブラウザでのWeb認証のほうが慣れている)。

#### GitHubにprivate repoを1つ作る(母艦のターミナル)

```
# 母艦のターミナルで(ghは第3回1Passwordセットアップ時にinstall済の想定)
gh repo create sora-bluesky/hermes-vault --private \
  --description "Shared AI long-term memory Vault (Obsidian)"
```

#### 母艦Vaultをinitial pushする

```
cd ~/Documents/Hermes-Vault/

# .gitignoreを用意して、端末固有の.obsidian/workspace.json等をexcludeする
cat > .gitignore <<'EOF'
.obsidian/*
!.obsidian/app.json
!.obsidian/appearance.json
!.obsidian/core-plugins.json
!.obsidian/community-plugins.json
!.obsidian/hotkeys.json
.trash/
.DS_Store
Thumbs.db
EOF

git init
git add .gitignore \
  .obsidian/app.json .obsidian/appearance.json .obsidian/core-plugins.json \
  "AIメモ.md" "Hermes Agent調査.md"
git commit -m "Initial Vault commit"
git branch -M main
git remote add origin https://github.com/sora-bluesky/hermes-vault.git
git push -u origin main
```

#### VPSで`gh` CLIをインストールしてGitHub認証する

VPS側にも`gh`を入れ、母艦と同じGitHubアカウントで認証する。

```
# VPS側で(sshで接続して実行・sudoパスワードを聞かれる)
(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
     | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y

# 認証(対話形式・8桁codeをコピーして、母艦のブラウザで貼り付ける)
gh auth login -h github.com -p https -w
```

#### VPSにcloneする

```
# VPS側で続けて
cd ~
git clone https://github.com/sora-bluesky/hermes-vault.git hermes-vault-repo
ls hermes-vault-repo  # 母艦と同じファイルが見える
```

#### 日常運用:push/pull

母艦で書いたら:

```
# 母艦のターミナルで
cd ~/Documents/Hermes-Vault/
git add <変更したファイル>
git commit -m "変更内容の説明"
git push origin main
```

![母艦のPowerShellでを実行した直後の画面。というcommitがpushされ、++の3行で成功している。ユーザー名はプロンプトでマスク済](https://static.zenn.studio/user-upload/deployed-images/5059b96f644a49e4a12732e3.png?sha=a400cfee8e493aad4421cfa3832746802318bc09)

VPSで取り込む:

```
# VPS側で
cd ~/hermes-vault-repo
git pull origin main
```

![VPS側のターミナルでを実行した直後の画面。+++++が表示され、母艦から送信したcommit がfast-forwardでマージされている。プロンプトのVPSホスト名は一部マスク済](https://static.zenn.studio/user-upload/deployed-images/78d0d77994a7a4b8a443802a.png?sha=0f872051f237121aa5a0f39b8f0bd19b90cbe0fa)

編集のたびに両側で`git pull`→`git push`を回す。Hermes側が書き込んだら母艦で`git pull`、母艦で書いたら`git push`してVPSで`git pull`。最初は手動でいい。第19回予定のCurator+cronで自動化する道が見えている。

### Obsidian Sync(補足)

Obsidian公式が提供する有料同期サービス(月額数ドル)を使うと、gitなしで母艦↔複数デバイス間の同期ができる。VPS側はgitで母艦と繋ぎ、母艦↔スマホ間はObsidian Syncで繋ぐ運用も可能だ。本回は基本のgit同期だけで進める。Obsidian Syncは「やりたくなったときに足せばよい」補足扱いとする。

## 3エージェントで同じVaultを読む

同じVaultをHermes・Claude Code・Codexの3つが読む設計が可能だ。本回ではHermes側の接続まで扱う。3エージェント連携の実装手順は連載後半の予定回(自宅PCを手足にする回)で本格的に扱う。

### 3エージェントが同じVaultを共用する概念

母艦のVaultを1つの共有フォルダにしておけば、Hermes(VPS・本回で接続)、Claude Code(母艦のターミナル)、Codex(母艦のターミナル)の3つが同じノート群を読み書きできる。それぞれが得意なエージェントに得意な仕事を任せる構成が見えてくる。

| エージェント | 得意領域(本連載の想定) |
| --- | --- |
| Hermes(VPS常駐) | 夜間や朝の自動処理・Telegram対話・cron運用・長期メンテ |
| Claude Code(母艦) | 記事執筆・コードレビュー・対話的なリファクタ |
| Codex(母艦) | 監査・ファクトチェック・独立視点のレビュー |

実装手順(Tailscale+OpenSSHでVPSと母艦を繋ぐ・3つのエージェントが同じVaultを読む設定など)は別回で扱う予定だ。本回ではHermes側の「Vaultを読める状態」までで止める。

## Vaultは配布対象外

Hermesには「Profile Distributions」という、自分の設定一式を他のマシンに配る仕組みがある(連載後半の予定回で扱う)。配布対象はSOUL.md/config.yaml/Skills/Cron/MCP設定など「人格と手順」だ。一方、Memoryの中身(USER.md/MEMORY.md/sessions/state.db)+Obsidian Vaultは配布対象外になる。

### user-ownedとnever-touchedの境界

| 配布される(人格と手順) | 配布されない(私の記憶と私のVault) |
| --- | --- |
| SOUL.md(文体・応答スタイル) | USER.md(私の人物カード) |
| config.yaml(設定) | MEMORY.md(私の環境ファクト) |
| Skills(手順書) | sessions(過去の会話履歴) |
| Cron(スケジュール) | state.db(セッション検索DB) |
| MCP設定 | Obsidian Vault(個人所有の外付け脳) |

配布されるのは「人格と手順」、配布されないのは「私の記憶と私のVault」。境界がきっぱり分かれている。これがあるからHermesを他のマシンに配っても、自分のプライベートな情報が一緒についていく心配がない。

配布の具体的なコマンドや運用は別回で扱う予定だ。本回は「Vaultは配布対象外」の1行を覚えておけば十分だ。これで安心してVaultを育てられる。

## まとめと第14回予告

第13回でやったこと。

* bundled `obsidian` skillがHermes本体に最初から入っていることを確認した
* VPS側にVault実体ディレクトリを作り、`/home/admin/hermes-vault`からsymlinkで読み書きできる形にした
* TelegramからHermesに「Vaultにメモを書いて」と頼み、VPS側のVaultに.mdファイルが実体として作られることを確認した
* AIが読めるノートの構造(5項目テンプレ:Title/Summary/Source/Context/Links/Next Action)を整理した
* AIが迷うノートの4特徴(あいまいタイトル/事実と感想の混在/孤立ノート/Next Action欠落)を裏返しで把握した
* 母艦とVPSのVaultをgit push/pullで同期する最小構成を作った
* 3エージェント(Hermes/Claude Code/Codex)が同じVaultを読む設計の伏線を引いた
* Vaultが配布対象外であることを境界として明示した

これで、Hermes Agentは「毎回使う前提(Memory)」と「長く残しておきたい情報(Vault)」の両方を持てる相棒に育った。Memoryの3,575字に収まらない気になった記事の保存、調べごとの記録、過去の議事録、書きかけの下書きは、これからすべてVault側に逃がせる。

第14回(予定)は**Session Search**だ。Hermesは過去のすべての会話を`~/.hermes/state.db`(SQLite+FTS5)に保存している。「先週Telegramで話した、あのAWSコスト最適化の話」を、Hermesが自分で検索して引っ張ってくる仕組みを入れる。

Memory(毎回使う前提)+Obsidian(長く残しておきたい情報)+Session Search(過去の会話)。この3つが揃うと、Hermesはようやく「忘れない相棒」と呼べる段階に入る。

---

📑 [シリーズのもくじ](https://zenn.dev/sora_biz/articles/hermes-vps-complete-guide)

## よくあるエラーと対処

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| 「Vaultが見つかりません」 | symlinkまたは実体ディレクトリが未作成 | `ls -la /home/admin/hermes-vault`でsymlinkがあるか確認・`ls -la ~/.hermes/sandboxes/docker/default/home/Documents/`でsymlink先の実体があるか確認 |
| `hermes memory setup --provider obsidian`が`not found.`になる | そのコマンドはv0.17.0実機に存在しない | VaultはMemory providerではない。bundled obsidian skill(§6)+ホスト側symlink(§7)で連携する |
| 環境変数を設定したのにHermesがVaultを読めない | Hermes本体未再起動 | `systemctl --user restart hermes-gateway`で反映 |
| Telegramで頼んでも「Vault機能がありません」と返ってくる | skillが無効化されている | `hermes skills list`で`obsidian`の有効状態を確認。無効なら有効化 |
| `hermes skills list`にobsidianが出ない | bundled manifestには登録があっても実体がシードされていない(v0.17.0初期インストールで観測) | `hermes skills reset obsidian --restore --yes`で実体を再シード |
| `git push`で「リモートに変更があります」エラー | 母艦↔VPSの片方が先に更新した | `git pull --rebase`で取り込んでから再push |
| 母艦のObsidianとVPSのVaultが食い違う | git同期し忘れ | 編集後は両側で`git pull`→`git push`を習慣化する(将来的に第19回予定のCurator+cronで自動化) |
| Vaultフォルダ内の日本語ファイル名が文字化けする | VPS側のlocale設定がja\_JP.UTF-8でない | `locale`で確認。`sudo dpkg-reconfigure locales`または`sudo locale-gen ja_JP.UTF-8` |

## 操作早見表

```
# skill確認
hermes skills list                              # bundled skill一覧
cat ~/.hermes/skills/note-taking/obsidian/SKILL.md   # SKILL.md表示

# Vaultパス設定
mkdir -p ~/.hermes/sandboxes/docker/default/home/Documents/Obsidian\ Vault   # 実体ディレクトリ作成
ln -sf ~/.hermes/sandboxes/docker/default/home/Documents/Obsidian\ Vault /home/admin/hermes-vault  # symlink張り
ls -la /home/admin/hermes-vault                 # symlinkが見えればOK
systemctl --user restart hermes-gateway         # Hermes再起動

# 動作確認
ls -la /home/admin/hermes-vault/                       # Vault内ファイル一覧
cat /home/admin/hermes-vault/<ノート名>.md             # 中身確認

# git同期(母艦・VPS両方で)
git pull origin main                            # 取り込み
git push origin main                            # 反映
```

## 補足:v0.17.0「The Reach Release」での関連機能

2026-06-19公開のv0.17.0「The Reach Release」では、本回のObsidian連携と相性のいい機能がいくつか追加されている。

* **read\_file拡張(Office対応)**:従来の.txt/.mdに加えて.docx/.xlsxも直接読めるようになった。Vault内に貯めた会議メモのdocxをHermesがそのまま要約できる(.pdfはそのままでは読めないので、テキストにしてから渡す)。
* **secure login(Dashboard)**:Dashboardにtoken必須endpointが導入された。本回では使わないが、第19回予定のCuratorでVault整理を自動化するときに関連してくる。

本回の手順はv0.17.0より前のバージョンでもskill+環境変数の2本柱で動くが、最新版に保つほどObsidian連携の活用幅が広がる。`hermes update`で本体を最新に保ち続けるのが基本だ。

## 引用元と参考
