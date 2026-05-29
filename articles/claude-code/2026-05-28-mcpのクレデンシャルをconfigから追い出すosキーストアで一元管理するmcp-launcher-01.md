---
id: "2026-05-28-mcpのクレデンシャルをconfigから追い出すosキーストアで一元管理するmcp-launcher-01"
title: "MCPのクレデンシャルをconfigから追い出す：OSキーストアで一元管理するmcp-launcher"
url: "https://zenn.dev/masuda_masuo/articles/2026-05-28-mcp-launcher"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "zenn"]
date_published: "2026-05-28"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

前の記事では、PATをMCPサーバーのconfigのenvに書くことで「AIのコンテキストに入らない」経路を確保した。今回はその先——**configに平文で書くこと自体**の問題に対処するツールを作った。

<https://zenn.dev/masuda_masuo/articles/2026-05-24-code-sandbox-mcp>

---

## configの平文問題：前回解決しなかったこと

前の記事でPATの渡し方を整理したとき、「argsに書く（アウト）」「envに書く（ベター）」という話をした。envに書けばAIのコンテキストには入らない——これは事実だ。

ただ、envに書いたとしても解決していない問題が4つ残っていた。

**① 平文保存のリスク**  
`claude_desktop_config.json`に書いたPATは平文のままファイルシステムに存在する。誰かに読まれれば終わりだ。Gitに誤ってコミットするリスクもある。

**② 設定の分散**  
自分はClaude DesktopとTypingMindの両方でMCPを使っている。同じPATを両方のconfigに書く必要がある。PATは1つ、設定箇所は複数——これは管理ミスの温床だ。

**③ 更新コスト**  
PATには有効期限がある。更新のたびに、各ツールのconfigを手で書き換え、Claude Desktopを完全に終了して再起動する必要がある。MCPサーバーはClaude Desktop起動時にプロセスを掴む仕様のため、configを変更しても再起動なしには反映されない。ツールが増えるほどこの手間は倍増する。

**④ config編集ミスによるエントリ消失とデバッグコスト**  
Claude DesktopはJSONが壊れている（タグ閉じ忘れ等）と、該当箇所のエントリを静かに消してしまう。手でconfigを編集するたびにこのリスクがある。対策としてバックアップを作ると、そのバックアップファイルにも平文のPATが残る。消し忘れれば①の問題に戻る。

エントリが消えて原因がわからないとき、生成AIに設定ファイルを貼って確認を求めることがある。そのとき「PATをマスクしてから貼るように」と言われる。一々マスクして貼るという手間が発生するうえ、うっかりマスクし忘れるリスクもある。configにPATが書いてある限り、このデバッグコストはついて回る。

MCPが普及するほどこの問題は大きくなる。GitHub PAT、AWSのアクセスキー、各種サービスのAPIキー——MCP化が進むほど、configを手で管理するコストとリスクは積み上がっていく。

---

## 解決策の選択肢と「手頃なVault」

クレデンシャルの一元管理という課題に対して、本格的な解決策は存在する。HashiCorp Vaultのような専用ソフトウェアだ。ただ、個人開発・小規模利用に対してこれは明らかに重い。

一方、すでに手元にある選択肢がある。**OSが標準で提供しているキーストア**だ。

| OS | キーストア |
| --- | --- |
| Windows | Credential Manager（DPAPI） |
| macOS | Keychain |
| Linux | libsecret / kwallet |

これらはOSのログインセッションと連動した暗号化ストレージだ。パスワードマネージャーやSSHキーの管理にも使われている枯れた仕組みであり、追加のインフラは不要で、クロスプラットフォームで動く。

「本格的なVaultを立てるほどではないが、平文のconfigよりははるかにまし」——この用途にちょうど合う。

---

## mcp-launcherの設計

`mcp-launcher`はAIツールとMCPサーバーの間に入るラッパーだ。

```
AI Tool (Claude Desktop / TypingMind / etc.)
    ↓
mcp-launcher  ← OSキーストアからトークンを取得してenvに注入
    ↓
MCP Server (github-mcp-server / aws-mcp-server / etc.)
```

MCPサーバー自体は何も変えない。環境変数でトークンを受け取るという動作はそのままで、その環境変数の供給元をconfigからキーストアに変える。

### configから秘密を消す

従来のconfigはこうだった：

```
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    }
  }
}
```

mcp-launcherを使うとこうなる：

```
{
  "mcpServers": {
    "github": {
      "command": "mcp-launcher",
      "args": ["github"]
    }
  }
}
```

トークンの実体はOSキーストアにある。configに書くのはキー名だけだ。

### launcher.json（秘密なし）

mcp-launcher自身の設定ファイルにも秘密は書かない：

```
{
  "github": {
    "command": "github-mcp-server",
    "env_keys": {
      "GITHUB_TOKEN": "mcp-launcher/github"
    }
  }
}
```

`env_keys`の値はキーストア内のエントリ名だ。トークンの実体ではない。このファイルはGitにコミットしても問題ない。

### トークンの登録

```
mcp-launcher register github GITHUB_TOKEN ghp_yourtoken
```

一度登録すれば、configに書く必要はない。Claude DesktopでもTypingMindでも、同じキーストアのエントリを参照する。

### 更新時の動作

PATを更新するときはkeystore上のエントリを書き換えるだけでよい。configファイルの編集は不要だ。

ただし、現在の実装ではmcp-launcherはプロセス起動時に一度だけキーストアを読み込んで子プロセスに環境変数として注入する設計のため、新しいトークンを反映させるにはClaude Desktopの再起動が必要になる。「configを手で書き換える手間」は省けるが、「再起動」自体は引き続き必要だ。

将来的にはトークンの自動ローテーション（Phase 2）と組み合わせることで、この制約を解消することを想定している。

---

## 現状のスコープと限界

実験で確認しているのはGitHub PATのみだ。ただ、設計上は環境変数でクレデンシャルを受け取るMCPサーバーであれば何でも対応できる。AWSのアクセスキーとシークレットアクセスキーも、理屈上は同じ方式で管理できる。

**このツールが守ること：**

* configファイルへの平文保存
* Gitへの誤コミット
* 複数ツールへのクレデンシャル分散
* PATローテーションの手間

**このツールが守らないこと：**

* OSのログインセッションを乗っ取られた攻撃者
* プロセスの環境変数を読める権限を持つマルウェア
* 悪意あるMCPサーバーによるトークン外部送信

OSキーストアはOSセッションと同じ信頼境界の中にある。セッションが侵害された時点ではmcp-launcherでも守れない。「configに鍵を置かない」という話であり、「侵害されたマシンを守る」という話ではない。

---

## 将来構想：パスキーとの連携

一元管理には当然リスクがある。キーストアが単一障害点になるという問題だ。

現在のPhase 1はキーストアへの格納と取得のみだ。次の段階として、クレデンシャルを取り出す際に**人間の承認**を要求する仕組みを考えている。

具体的にはFIDO2・パスキーとの連携だ。Windows Hello、Touch ID、Face ID、あるいはスマートフォンをFIDO2デバイスとして使うCTAP2 hybrid——これらを使い、「MCPサーバーへのクレデンシャル払い出しを人間が明示的に承認する」フローを作る構想だ。

もう一つはトークンの自動ローテーションだ。無期限PATを作ってしまう現状の運用を変え、短命トークンをGitHub App経由で自動発行・更新する仕組みも検討している。

どちらも現時点では構想段階だ。

---

## リポジトリ

<https://github.com/masuda-masuo/mcp-launcher>

インストールとセットアップの詳細はREADMEに書いた。現時点ではソースからのビルドが必要だ。

同じ課題——「MCPのconfigにクレデンシャルを書きたくない」——を持つ人の参考になれば。
