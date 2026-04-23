---
id: "2026-04-15-claude-codeで自動承認を目指して-settingsjson-を調整したらまず起動しなかった-01"
title: "Claude Codeで「自動承認」を目指して settings.json を調整したら、まず起動しなかった話"
url: "https://zenn.dev/aliyell/articles/9cdc77fd1a7b24"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

Claude Code を使っていると、毎回の permission 確認が少しずつ重く感じてきます。  
そこで今回は、できるだけ自動で進めつつ、安全性は落としすぎない構成を目指して、`settings.json` をいろいろ調整してみました。

やりたかったのは単純で、**Bash コマンドを毎回手で承認しなくても進む状態**を作ることです。  
ただ、やってみると最初にぶつかったのは「起動しない」という問題でした。そこから `sandbox`、`bypassPermissions`、`claude doctor`、`deny` ルールを順番に見直していくことで、ようやく「どこを自動化し、どこを明示的に止めるべきか」が見えてきました。Claude Code の公式ドキュメントでも、sandbox は「毎回承認する」方式の代わりに、先に安全な境界を作ってその中でより自律的に動かすための仕組みとして説明されています。

私の環境

* windows wsl2
* claude code pro plan (auto-permissionとかは使えない）

## 最初に考えたのは `bypassPermissions` だった

最初は、「確認を減らすなら `permissions.defaultMode` を `bypassPermissions` にすればいいのでは」と考えました。実際、Claude Code には `bypassPermissions` というモードがあり、通常の permission プロンプトを大きく省略できます。ただしこれはかなり強いモードで、公式にも**隔離された環境で使う前提**に近い扱いで案内されています。 protected directory への書き込みなど一部はなお確認されますが、基本的には「確認を飛ばす」方向の設定です。

ここであとから分かったのは、**本当に欲しかったのは `bypassPermissions` そのものではなく、sandbox 内の Bash を自動で通す仕組みだった**ということです。Claude Code の sandbox には auto-allow mode があり、これを有効にすると sandbox 内で完結する Bash コマンドは permission mode と独立して自動承認されます。つまり、自動化の本丸は `bypassPermissions` よりも `sandbox.enabled` と `autoAllowBashIfSandboxed` のほうでした。

## 最初の設定はこんな感じだった

試した設定は次のようなものでした。

```
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["./"],
      "denyRead": ["~/"],
      "allowRead": ["."]
    },
    "network": {
      "allowedDomains": [
        "api.github.com",
        "registry.npmjs.org"
      ]
    }
  }
}
```

意図としてはかなり素直です。  
sandbox を有効にして、その中なら Bash を自動承認し、sandbox が張れないならそのまま動かさず止める。さらに sandbox 外への再実行も許さない、という安全寄りの構成です。`failIfUnavailable: true` は、sandbox が起動できないときに警告だけで続行せず、hard fail にするための設定です。`allowUnsandboxedCommands: false` は、制約で失敗したコマンドを sandbox 外で再実行する escape hatch を無効化します。

## ところが起動しなかった

設定の方向性自体は悪くなかったのですが、実際にはこれで Claude Code がうまく起動しませんでした。  
結論からいうと、原因は `bypassPermissions` ではなく、**sandbox の前提条件を満たしていなかったこと**です。

Claude Code の sandbox は macOS では Seatbelt、Linux と WSL2 では bubblewrap を使います。Linux/WSL2 では `bubblewrap` と `socat` が前提パッケージになっていて、これらが入っていないと sandbox を開始できません。そして `failIfUnavailable: true` を入れていると、その状態で警告だけ出して継続するのではなく、きちんと失敗して止まります。

## `claude doctor` を実行したら原因がはっきりした

そこで `claude doctor` を実行してみると、診断結果はかなり分かりやすいものでした。要点だけ抜き出すと、次のような状態でした。

```
Status: Missing dependencies
bubblewrap (bwrap) not installed
socat not installed
```

この時点で、「起動しない」の正体はほぼ確定です。  
sandbox を必須にしているのに、その sandbox 自体が必要な依存関係不足で立ち上がれない。だから起動時に止まっていたわけです。Claude Code の公式ドキュメントでも、Linux/WSL2 の sandbox では `bubblewrap` と `socat` が必要で、不足時は `/sandbox` や診断からインストール案内が出ると説明されています。

## まずは `bubblewrap` と `socat` を入れた

今回の環境は Ubuntu 系だったので、対応はシンプルでした。

```
sudo apt install bubblewrap socat
```

入れたあとにもう一度 `claude doctor` を流すと、今度は `Missing dependencies` ではなく `Available (with warnings)` に変わりました。少なくともこの時点で、**起動不能の主因は解消**したことになります。Claude Code の docs でも、Ubuntu/Debian ではこの 2 つを入れるのが Linux sandbox の前提として案内されています。

## ただし警告はまだ残った

依存関係を入れたあと、`claude doctor` にはこんな警告が残りました。

```
Status: Available (with warnings)
seccomp not available - unix socket access not restricted
```

これは「sandbox が使えない」という意味ではなく、**sandbox は使えるが、Unix socket まわりの制限がフルには効いていない**という意味です。Claude Code の sandbox はファイルシステムとネットワークの隔離を提供しますが、Unix socket は bypass の足がかりになりやすく、特に `docker.sock` のような強いソケットは危険です。公式ドキュメントでも、`allowUnixSockets` やソケット経由の権限拡張には強い注意が必要だとされています。

この警告が残っている状態でも、以前の「そもそも sandbox が起動しない」段階よりはかなり前進しています。ただし、**フル強度の sandbox ではない**という理解は必要です。特に Docker や強い system socket に触れる運用は避けたほうが安全です。

## もうひとつ気をつけたのは設定ファイルの置き場所

今回の構成では `denyRead: ["~/"]` と `allowRead: ["."]` も試していました。  
この組み合わせ自体は有効ですが、地味に重要なのが **`.` の解釈が settings のスコープで変わる**ことです。Project settings に置いた場合の `.` は project root を指しますが、`~/.claude/settings.json` のような User settings に置くと `.` は `~/.claude` を指します。そのため、同じ設定でも置き場所によっては「ホーム配下を deny した結果、肝心のプロジェクトを読めない」という状態になりえます。

これは今回の起動不能の直接原因ではありませんでしたが、sandbox を詰めるときにかなり見落としやすいポイントでした。

## 結局、自動承認と安全性は別々に考える必要があった

ここまで触ってみて一番大きかった学びは、**「自動承認」と「安全性」は同じ設定ではない**ということです。

`bypassPermissions` は確認を減らしますが、それ自体が安全性を上げるわけではありません。  
一方、sandbox は OS レベルで Bash とその子プロセスの挙動を狭い範囲に閉じ込めます。そして auto-allow mode が有効なら、その範囲内の Bash は permission mode と独立して自動で通ります。つまり、自動化の土台は sandbox であり、安全性の補強は deny ルールでやる、という分担が見えてきました。

## そこで `deny` をちゃんと入れることにした

Claude Code の permissions は **deny → ask → allow** の順で評価され、deny が最優先です。さらに sandbox の auto-allow mode でも **explicit deny は常に尊重される**とドキュメントに明記されています。つまり、「自動承認はさせたいが、これだけは絶対に触らせたくない」という境界を作るには deny が向いています。

今回のように `bypassPermissions` を併用するなら、deny はほぼ必須だと感じました。具体的には次の 4 系統を止めるだけでも、事故の確率はかなり下がります。

* `.env` や SSH 鍵などの秘密情報の読み取り
* `.bashrc` や `.zshrc` のような永続的に危険な設定ファイルの編集
* `curl` や `wget` のような Bash 経由の外部送信
* `docker` や `kubectl` などのインフラ系コマンド

公式 docs でも、`Read(./.env)` や `Read(./secrets/**)`、`Bash(curl *)` のような deny 例が紹介されていて、sensitive file の除外や危険な Bash 実行の抑制に使うことができます。

## 最終的にこういう構成に落ち着いた

最終的には、次のような方針がいちばんしっくりきました。

```
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(~/.ssh/**)",
      "Edit(~/.bashrc)",
      "Edit(~/.zshrc)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(ssh *)",
      "Bash(scp *)",
      "Bash(docker *)",
      "Bash(kubectl *)",
      "Bash(terraform *)"
    ]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["./"],
      "denyRead": ["~/"],
      "allowRead": ["."]
    },
    "network": {
      "allowedDomains": [
        "api.github.com",
        "registry.npmjs.org"
      ]
    }
  }
}
```

この構成の考え方はシンプルです。  
**sandbox の中で完結する Bash は自動で進める。sandbox が張れないなら止める。sandbox の外へ逃がさない。そして、秘密情報や永続的な改変、外部送信、インフラ操作だけは deny で先に潰す。** Claude Code の設定仕様上、deny は allow や ask より優先され、sandbox の自動承認中でも尊重されます。

なお、もっと安全寄りにしたいなら、`defaultMode` は `bypassPermissions` ではなく `acceptEdits` にして、sandbox の auto-allow を主役にしたほうがバランスは取りやすいです。`bypassPermissions` は便利ですが、公式にも isolated environment 向けの危険寄りモードとして案内されています。

## まとめ

今回の調整で分かったのは、Claude Code で「自動承認」を実現する近道は、単純に `bypassPermissions` を入れることではなかった、ということです。

本当に重要だったのは次の 3 つでした。

1. **sandbox をちゃんと起動できる状態にすること**  
   Linux/WSL2 なら `bubblewrap` と `socat` が必要で、`failIfUnavailable: true` を入れるなら依存不足のままでは起動しません。→**ここに引っかかった**
2. **自動承認の本体が sandbox 側にあると理解すること**  
   `autoAllowBashIfSandboxed` によって、sandbox 内の Bash は permission mode と独立して自動承認されます。
3. **危ないものだけは deny で明示的に止めること**  
   deny は最優先で、sandbox の auto-allow 中でも効きます。秘密情報、永続的な設定ファイル、外部送信、インフラ系コマンドは deny しておくと安心です。

自動化を進めようとすると、つい「全部通したい」方向に寄りがちです。  
でも実際に触ってみると、使いやすさを上げるのは auto-allow、安全性を作るのは deny と sandbox、という役割分担で考えたほうがずっと整理しやすいと感じました。
