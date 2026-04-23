---
id: "2026-04-18-rust-でdiagram-cliという-claude-code-互換の-cli-ツールを開発して-01"
title: "Rust で「diagram-cli」という Claude Code 互換の CLI ツールを開発して OSS 化しました！"
url: "https://zenn.dev/tad1310/articles/0c57c76d767913"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

# 開発物（OSS化済み）

<https://github.com/tadasi/diagram-cli>

## 概要

アプリケーションコードを Claude Code Agent で分析し、Mermaid ベースのシステム図を生成する CLI ツールを自主開発しました！

## 実行準備

詳細は上記 GitHub の README をご確認いただければと思いますが、基本的に以下のみで実行環境が整います。

* `diagram-cli`のバイナリインストール
  + 指定コマンドでバイナリインストールをすれば、手元で Rust の実行環境を整える必要がありません。
* `Claude CLI`セットアップ
  + 内部的に`Claude CLI`を使用することを前提としているため、先に`claude`コマンドを使用できるようにする必要があります。

セットアップ詳細

## バイナリインストール

以下で`dg`コマンドが使えるようになります。

```
curl -fsSL https://raw.githubusercontent.com/tadasi/diagram-cli/main/install.sh | bash
```

## 初期設定

`dg init`を実行するか`dg`コマンドをそのまま起動すると、まず初めに以下の順で設定に関して質問されます。

### 分析対象としたいソースコードのディレクトリパスを指定

```
% dg init
=== dg: 初期設定 ===

分析対象プロジェクトディレクトリを、ルートからの相対パスで指定（変更が不要な場合は、Enter キーを押下）してください。
  例: Projects/your-project
> `Projects/tech-index`
```

上記のように、分析を行いたい対象のリポジトリ名を指定します。

### 出力したいシステム図の種類を選択

```
システム図の種類を選択（変更が不要な場合は、Enter キー押下）してください:
  1: フローチャート
  2: シーケンス図
番号を選択: 1
```

現状フローチャートかシーケンス図しか対応していないので、そのどちらかを選択します。

### 生成したシステム図の出力先ディレクトリを指定

```
- ファイルの出力先を、ルートからの相対パスで指定（変更が不要な場合は、Enter キー押下）してください。
  デフォルト: Desktop
>
```

一旦デフォルトの Desktop のままで良いので、今回はそのまま Enter を押します。

### 設定確認

```
設定を保存しました。
指定のソースコードを分析し、システム図を出力します。
設定を確認してください。

--------------現在の設定--------------
  コードの分析対象ディレクトリ : ~/Projects/tech-index
  システム図の種類           : フローチャート
  出力先                    : ~/Desktop
------------------------------------

設定を変更しますか？ (y/n): n
```

すると、上記のように確認を求められるので、変更が不要な場合は n を入力します。  
これで設定は完了です。

### 設定ファイルの配置場所

設定ファイルは、デフォルトだと以下で確認できます。

```
cat ~/.config/dg/config.json
```

## （任意）環境変数指定

例えば、以下のように Claude のモデルとバージョンを指定することもできます。  
デフォルトでは、現時点で公開されている最新の`claude-opus-4-7`が設定されるようになっています。

```
export DG_CLAUDE_MODEL='claude-sonnet-4-6'
printenv DG_CLAUDE_MODEL # 確認
```

## 実行例

先日個人開発を行なった [Tech Index](https://tech-index-1.onrender.com/) （[紹介記事](https://zenn.dev/tad1310/articles/ff24ba64a10b27)）をサンプルとして、実行を試してみます。

### 実行コマンド

#### `dg`コマンドだけを実行する場合

```
指定のソースコードを分析し、システム図を出力します。
設定を確認してください。

--------------現在の設定--------------
  コードの分析対象ディレクトリ : ~/Projects/tech-index
  システム図の種類             : フローチャート
  出力先                       : ~/Desktop
------------------------------------

設定を変更しますか？ (y/n): n
```

まず最初に設定確認があるので、特に変更の必要が無ければ`n`を入力。

```
分析対象の詳細を指定してください:
  API 単位の分析 → curl コマンドを入力
  包括的な分析   → 画面操作手順や機能説明を自由テキストで入力
  （行末に \ を加えると、継続行の入力が可能）
>
```

対象のソースコードに対して、`API`ベースで分析したければ`curl`コマンドを、  
画面操作手順や機能概要を元に分析したければ、自由テキストを入力する。

ここで入力された文字列が`claude`へのプロンプトとして渡されます。

#### `dg curl ~`を実行する場合

上記で`dg`コマンドを入力してから`curl`コマンドを指定するのと本質的には同じですが、  
最初から`dg`コマンドの引数として`curl`コマンドを渡すとスムーズです。

例えば postman で保管しておいたローカル API 情報を「コードスニペット」からコピーして`dg`コマンドと一緒に投げるようにすると便利です。

![](https://static.zenn.studio/user-upload/cedb2f26a3db-20260418.png)

shell

```
dg curl --location 'http://localhost:3000/tech_articles'
```

```
指定のソースコードを分析し、システム図を出力します。
設定を確認してください。

--------------現在の設定--------------
  コードの分析対象ディレクトリ : ~/Projects/tech-index
  システム図の種類             : フローチャート
  出力先                       : ~/Desktop
------------------------------------

設定を変更しますか？ (y/n): n

コード分析中……
実行が完了しました。出力内容を確認してください。
出力ファイル: /Users/your_name/Desktop/dg_tech_articles_get_20260418_191533.html
```

### 生成物

生成物は、html ファイルと mmd ファイルの 2 種類あります。  
実行が完了すると、HTML ファイルをブラウザで開いてくれます。

#### 例1.フローチャート

まぁツッコミ所も色々とありますが、概ね合ってます。  
これは自主開発のシンプルなアプリケーションなので簡単ですが、複雑な業務ロジックとなるとどうなるかは見ものですね。

また生成の精度は完全に AI Agent 依存なので、毎回全然異なる図を返してくるのもご愛嬌ですし、不要な情報も多かったりたまに間違ってたりもしますが…。

#### 例2.シーケンス図

シンプルなアプリケーションにしては複雑な図を返してきますが…。  
これもまた概ね合ってそうではあります。

なお README にも書きましたが、AI Agent 依存なため精度の保証はいたしません。  
![](https://static.zenn.studio/user-upload/d9ca318f4a53-20260418.png)

## セキュリティ上、気にしたポイント

基本的に、この CLI ツールは実行者の手元環境依存であり、  
手元のソースコードに対して、手元の`Claude Agent`で実行をかける際のラッパーとしての役割しか果たしていません。

そのため、README には以下のように実行は自己責任においてお願いしますと記載しました。  
![](https://static.zenn.studio/user-upload/21a57e546635-20260418.png)

が、以下のように最低限、プロンプトに機密情報をなるべく渡さないような配慮を加えたりはしました。

### `Curl`に渡され得る機密情報のサニタイズ

`curl`コマンドが指定された場合は、`cookie`や`x-csrf-token`その他、  
機密情報をサニタイズ（`****`に置き換え）した上でプロンプトに渡すようにしています（[参照コード](https://github.com/tadasi/diagram-cli/blob/main/src/sanitize.rs)）。

渡された`curl`コマンドは最後にシステム図の上部に説明として入れるようにしているので、  
サニタイズする前提とは言え、機密情報は渡さないようにしていただいた方が無難です。

システム図を生成する上では不要ですので。

### OSS 化する上で、GitHub 上の保護ルールはガチガチに

万が一にも自分が窺い知れない経路で問題のあるコードを仕込まれたりしないよう、  
以下の記事などを参考に GitHub 上の保護ルールはかなりガチガチにしました。

<https://zenn.dev/json_hardcoder/articles/f9b534377103a4>  
<https://docs.github.com/ja/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/managing-rulesets-for-a-repository>

特に、Code Owner である自分の許可無しには、いかなる変更も`main`には加えられないようにしています。

#### Permission の考慮

`claude`コマンド実行時に渡すフラグは[この辺り](https://github.com/tadasi/diagram-cli/blob/main/src/claude.rs#L108-L124)で指定していますが、間違っても`--dangerously-skip-permissions`といったフラグを渡さないよう気を付けました。

<https://code.claude.com/docs/en/cli-reference>

> --dangerously-skip-permissions Skip permission prompts. Equivalent to --permission-mode bypassPermissions. See permission modes for what this does and does not skip

<https://code.claude.com/docs/en/permissions#permission-modes>  
![](https://static.zenn.studio/user-upload/b78d76ecdf71-20260418.png)

<https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode>  
![](https://static.zenn.studio/user-upload/d434d2a15c62-20260418.png)

上記のように公式ページ上でも、`--dangerously-skip-permissions`は`--permission-mode bypassPermissions`の指定と同等であり、「実行するとしても Claude Code が損害を与えることができないコンテナや VM などの隔離環境だけにすべし」と繰り返し警告されています。

非隔離環境で使ってしまうと、万が一にも悪意のある指示がプロンプトに含まれていた（プロンプトインジェクションがあった）場合、人間によるチェックを介さずに、自環境において好き放題にコマンドが実行されてしまう恐れがあります。

オープンソースなどで上述のフラグが使われている場合は、基本的には使用を避けることが好ましいかと思います。皆さんも気を付けてくださいね。

自分は今回、`--allowedTools Read,Glob,Grep`フラグを指定し、不必要な書き込み権限は一切与えないようにしました。

#### クレデンシャルの読み取り権限を与えないように

上記と合わせて、`--disallowedTools`で`Read(.env)`その他クレデンシャルが含まれ得るファイルを読み取らせないようにフラグ指定しています（[参照コード](https://github.com/tadasi/diagram-cli/blob/main/src/claude.rs#L117-L124)）。

しかし、それでもまだ万全ではありません。

全ての可能性を網羅して予め読み取りを禁止させることは難しいです。  
プロンプト上でも秘匿情報を読まないようにと指示してはいますが、それを AI Agent が厳守するかどうかは分かりません。

以下のように deny ルールを設定して、絶対に読ませないように自身の責任において管理をする必要があります。  
これはこの CLI ツールに限った話ではなく、AI 全盛のこの時代、誰もが気を付けるべき事柄でもありますね…。

予め分析対象ディレクトリ内の`.claude/settings.json`に設定を追加して、秘匿が必要なファイルの Read を deny 設定しておくことを推奨します。

settings.json（設定例）

```
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

## 背景

### なぜこのツールを開発したか

複雑なロジックを読み解く際に、1から10まで自分の目で読んで、全てを図示するとなると膨大な時間がかかるため。

例え精度がそれほどだとしても、AI Agent がパッとコードを読んでパッと図示してくれれば、  
それを叩きとして改修の検討を進められるため。大きな時短となり得るだろうと考えてのことです。

### なぜ Rust を選択したか

これに関しては、大きな理由はありません。

強いて言えば、コンパイルしたバイナリデータをインストールすることで簡単に配布できるメリットがあったためというのが1つ（これは GO や他の言語でも良い訳ですが）。

あとは CLI ツールなので実行が早いにこしたことはないという理由もありますが、  
一番時間がかかるのは AI Agent によるソースコードの読み取りなので、Rust の実行が早くても今回ほぼ意味はありません。

あとは、単純に今まで使ったことが無かった Rust を使ってみたかったからという理由です。  
最近 SNS 上でも話題に登ることが多い印象でもあったので、使用感を確かめてみたかったのです。

## 学び

### Rust に関して

今回以下の記事にざっと目を通すぐらいはしましたが、後はひたすら Agent をフル活用しつつ開発を進めました。  
<https://zenn.dev/mebiusbox/books/22d4c1ed9b0003>

以下の Playground で実行を試しながら、Rust の仕様を読み解きつつリファクタしたりはしましたが、AI Agent のお陰でスムーズにキャッチアップを行えました。  
<https://play.rust-lang.org/>

正直 Rust の言語仕様についてはまだ理解が浅いなと感じてはおりますが、個人的には今回 Rust を選択して良い勉強になったなと感じております。

所有権の概念が面白かったのと、あと少し驚いたのは、ユニットテストの配置場所は実行ファイルの下の方に書くという慣例についてです（[参照コード](https://github.com/tadasi/diagram-cli/blob/main/src/mermaid.rs#L88-L133)）。  
<https://doc.rust-lang.org/book/ch11-03-test-organization.html>

> You'll put unit tests in the src directory in each file with the code that they're testing. The convention is to create a module named tests in each file to contain the test functions and to annotate the module with cfg(test).

自分は現職では Rails で開発しておりますが、改めてコンパイル言語はテストの実行速度も早いなと実感しました。  
コード修正毎のコンパイルは多少面倒ではありますが、前職 GO で開発していた時の感覚を思い出しました。慣れると、随所で開発体験の良さを感じます。

### セキュリティに関して

今回 OSS 化するに当たって、本当に問題が無いかかなり慎重に見たので、自分の中のセキュリティ意識の高まりと、知識の拡充ができたと実感しています。

### CLI ツール開発 & OSS 化に関して

自分の手で CLI ツールを形に出来て、OSS 化も出来たことは、自分にとって今後に繋がる成果となりました。

今後も AI Agent を活用しつつ、好きなツールを開発していけると思うとワクワクします。

## 終わりに

以上です！今後もセキュリティには気を付けながら楽しんで開発していこうと思います！  
読んでくださってありがとうございました！では！
