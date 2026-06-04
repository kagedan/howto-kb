---
id: "2026-06-04-nixos-claude-codeすべての設定を生成aiに丸投げできる対話型osの構築方法-01"
title: "「NixOS × Claude Code」—すべての設定を生成AIに丸投げできる対話型OSの構築方法"
url: "https://note.com/hatake716/n/ncbfec4f62a26"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-06-04"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

## この記事を買う前に——誰に向けた記事か、正直に話します

NixOSを選んだのは、自分でも少し不思議な気がしています。

エンジニアではありません。

プログラミングが得意なわけでもない。それでも、「システム全体の状態を一枚のファイルに書いておく」というNixOSの設計に惚れてしまいました。インストールしたソフト、フォントの設定、自動起動するサービス、すべてが `configuration.nix` に書いてある。

それを `nixos-rebuild switch` するだけで反映される。この清潔さが、たまらなく好きでした。

ただ、NixOSはその清潔さと引き換えに、詰まったときの孤独さがあります。

Steamを有効にしてゲームを起動したら、日本語タイトルがすべて豆腐（□□□□）になっていました。

「日本語フォントが当たっていない」ことは分かる。でも `environment.systemPackages` にフォントを追加しても、Steamの中には届きません。NixOSのSteamは独立した環境で動いているので、別の方法で渡す必要がある——これに気づくまで、何時間もかかりました。

別の日には、Dropboxをインストールしたのにログイン後に自動起動しないことに気づきました。`systemd.user.services` として手動で定義する必要がある、ということは調べれば分かった。でも書き方が分からない。さらに、`QT\_QPA\_PLATFORM = "xcb"` という環境変数がないとシステムトレイアイコンが出ないという罠が、その先に待っていました。

RadeonのGPUで特定のソフトが動かなくなったとき、`HSA\_OVERRIDE\_GFX\_VERSION = "11.0.1"` を設定しなければならないという事実も——誰も教えてくれませんでした。たどり着いたのは、海外フォーラムの流れていきそうな一投稿でした。

こういう「知っている人には当たり前すぎて書かれていない」ことが、NixOSには多い。ガイドを書く人のほとんどが、Nix言語の仕組みを理解した上で使っている人たちだからだと思います。非エンジニアの視点で丁寧に書かれた情報が、圧倒的に少ない。

---

そのころ、Claude Codeという名前を聞きました。「ターミナルで動く自律型AI」という説明に惹かれて、使い方を調べ始めました。

出てくる記事は、ほとんどがmacOSかUbuntu向けでした。「npmでグローバルインストールすればOK」と書いてある。NixOSユーザーは分かるはずです。

それ、そのままじゃ動かない、と。nix-shellを使う方法も見つかりましたが、毎回シェルを立ち上げ直すのは、どこかNixOSらしくない使い方に感じていました。

半ば諦めかけたとき、nixpkgsのリポジトリを直接検索してみました。

`claude-code` というパッケージが、すでにありました。

他のどのソフトウェアとも変わらない方法で、`environment.systemPackages` に一行書いて、`nixos-rebuild switch` するだけ。npmも、nix-shellも、いりませんでした。

![](https://assets.st-note.com/img/1780533551-HYyKpZCqn6IJge58zBaRi4mk.png?width=1200)

NixOS✕ClaudeCodeなら、パッケージのインストールやアンインストール、設定までOSのすべてをAIに任せられる

---

**その夜から、止まっていた問題が片づき始めました。**

Steamの日本語文字化けは、Claude Codeが既存の設定ファイルを読んだ上で `steam.override` の書き方を示してくれました。Dropboxのsystemdサービス設定も、なぜ `QT\_QPA\_PLATFORM = "xcb"` が必要なのかの説明とセットで出てきました。RadeonのROCm環境変数も、なぜその値なのかまで教えてもらいました。

「自分では絶対に辿り着けなかった」と思う設定が、いくつもあります。

## この記事は、その体験をそのまま書いたものです。

---

## この記事で具体的に手に入るもの

![](https://assets.st-note.com/img/1780532699-clTeP2iIg3uVNbUmQ8XJGqCh.jpg?width=1200)

**① すぐ動く configuration.nix のコード（flake.nix・VS Code拡張も含む）**

コピーして貼り付ければそのまま動く設定を、flake.nix・configuration.nix・VS Code拡張の3レイヤーに分けて載せています。「なぜこう書くのか」の解説付きなので、自分の環境に合わせて応用できます。

**② NixOSとClaude Codeの「相性の良さ」の正体**

「設定ファイル一枚がAIの文脈になる」「失敗してもロールバックできるから怖くない」「メインPCとサブPCの環境を一行で統一できる」——これはNixOSユーザーにしか得られない固有の体験です。なぜこの組み合わせが特別なのか、構造的に解説します。

**③ NixOS の Steam・ゲーム環境を丸ごと構築する設定**

「`programs.steam.enable = true` にしたのに日本語が文字化けする」「MangoHudをゲームに表示したい」「GamemodeでCPUを最適化したい」「ProtonUp-Qtとlsfg-vkでWindowsゲームを快適にしたい」「Sunshineでゲームストリーミングサーバーを立てたい」——これらをすべて `configuration.nix` の設定として、コードと解説付きでまとめています。

**④ GPUまわり・サービス設定・ゲーム（Steam周り）の設定・チャンネル管理など7つの実ユースケース**

「Radeon ROCmの謎の環境変数（`HSA\_OVERRIDE\_GFX\_VERSION = "11.0.1"`）の意味」「Dropboxをsystemdユーザーサービスとして手動定義する方法」「AMD→Intel GPUへの設定移植の差分」「unstable/stableチャンネルを混在させる`pkgsStable`オーバーレイ」——すべて実際の `configuration.nix` の中身をベースにした実体験です。

**⑤ claude-monitor のセットアップ**

Claude Codeの使用量・コストをリアルタイムで把握できるツールです。これも `configuration.nix` 一行で入ります。

**⑥【最新版】メインPCの設定ファイル全文**

---

## この記事が向いている人・向いていない人

**向いている人**

* NixOSを使っていて、Claude Codeを試したい人
* NixOSでゲームもしたいが、Steamまわりの設定で詰まっている人
* configuration.nixのエラーをAIに直接読ませたいと思ったことがある人
* 非エンジニアだけどNixOSを使い続けている人

**向いていない人**

**NixOSを使っていて、Claude Codeを試してみたい——それだけ揃っていれば、この記事は必ず役に立ちます。**

### 設定で詰まっていた時間を、別の作業に使ってください。

  

**この投稿をいいね＆リポストしてくれた方は無料で記事を読むことができます。ついでにXのアカウントをフォローしてくれると嬉しいです。**
