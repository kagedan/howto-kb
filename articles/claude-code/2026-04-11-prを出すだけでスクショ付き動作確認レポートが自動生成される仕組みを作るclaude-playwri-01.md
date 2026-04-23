---
id: "2026-04-11-prを出すだけでスクショ付き動作確認レポートが自動生成される仕組みを作るclaude-playwri-01"
title: "PRを出すだけでスクショ付き動作確認レポートが自動生成される仕組みを作る（Claude × Playwright）"
url: "https://zenn.dev/datum_studio/articles/ebefce70f39a0d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

こんにちは。データエンジニアの山口歩夢です。

以前、Claude CodeとPlaywright CLIを使ってStreamlitで作ったアプリケーションの動作確認レポートを自動作成するスキルを作りました。  
対話形式で動作確認手順をClaudeに指示すると、Playwright CLIがStreamlitアプリを動かして、指示した通りに操作して、動作確認手順をスクショ付きで出力してくれると言ったものです。どんな風にレポートが出力されるのかは、以下の記事をご確認ください。

<https://zenn.dev/datum_studio/articles/d3b8e49a3c422d>

そして、今回は**こちらをGitHub Actionsに組み込んで、PRを出した時に自動で動作確認レポートを作成できるようにしてみよう**という挑戦をしてみたので、工夫した点を色々と紹介してみようと思います。

## 完成イメージ

この機能を使うと、動作確認手順書（ここでは、`docs/operation_check.md`とします。）を書いてPRを出せばGitHub Actionsがトリガーされ、スクリーンショット付きの動作確認レポートが自動生成されます。早速完成するもののイメージを紹介していきます。

### 全体の流れ

まずは全体の流れです。  
動作確認手順書を含んだPull Requestを作成すると、GitHub Actionsが実行されるようにしました。以降は、「動作確認」「スクショ付きレポート作成」「PRへのレポートの格納先URLの返信」を自動で実施してくれます。

![](https://static.zenn.studio/user-upload/9eeba35ef55d-20260408.png)  
*PRを作成すると「動作確認」「スクショ付きレポート作成」「PRへのレポートの格納先URLの返信」を実施*

### 作成される動作確認レポート

実際に作成される動作確認レポートは、GitHubのArtifactにHTML形式で格納されます。

以下のようなイメージの動作確認レポートがDLできます。手順書に記載した通りの手順で動作確認をして、動作確認時の全ての行程のスクショと、どんな操作をしたかを記録して、HTMLで出力してくれます。

![](https://static.zenn.studio/user-upload/7afe960daf94-20260408.png)  
*ブログ用に生成したイメージ画像ですが、ほぼこの見た目のレポートが生成されます*

ちなみに、GitHubのArtifactは、GitHub Actions時に作成した成果物を格納しておく機能です。生成した成果物はGitHub ActionsのジョブのページからDLすることができます。

<https://docs.github.com/ja/actions/tutorials/store-and-share-data>

<https://docs.github.com/ja/actions/how-tos/manage-workflow-runs/download-workflow-artifacts>

### PRのコメントにレポートのリンクを返信

動作確認レポートまでの動線がわかりやすくなるように、ArtifactのURLをPRのコメントに返信してくれるように実装することも可能です。このような形でArtifactのURLをPRに返信してくれます。

![](https://static.zenn.studio/user-upload/4605bc0256aa-20260408.png)

以上のように、動作確認レポートをGitHub Actionsで作成して、レポートの場所をPRにコメントしてくれる機能を作成しました。

## この機能の構成要素

まずは、この機能の構成要素について紹介します。  
この機能は主にこの3つの機能がポイントかなと考えています。

### 動作確認手順書(mdファイル)

まずは、動作確認手順書（docs/operation\_check.md）です。  
このファイルに、動作確認の方法について詳細を記載することによって、Playwright CLIがその通りにStreamlitアプリを操作してくれます。  
[冒頭に紹介した記事](https://zenn.dev/datum_studio/articles/d3b8e49a3c422d)では対話形式で、Claudeに手順を指示していましたが、今回は**PRトリガーで自動実行したかったため、手順書をファイルとしてコミットする方式を採用する必要**がありました。

手順は、`docs/operation_check.md`に確認したい操作手順を日本語で書くだけです。  
以下のようなイメージで、操作の流れを可能な限りに詳細に書きます。  
今回はシンプルなアプリケーションで検証を行っているため簡潔に書いていますが、実際には**実際にアプリを開いてどのボタンを押して、どのページに遷移して、どのボタンを押してどこに表示されるはずのデータを確認する**など事細かく書く必要があります。

```
# date_inputアプリケーション動作確認手順

## 動作確認手順
1. サイドバーのメニューを開く
2. date_inputアプリケーションを選択する
3. メインエリアにjp_date_inputとst.date_inputが横並びに表示されているかを確認
4. サイドバーにもjp_date_inputとst.date_inputが表示されているかを確認
```

こちらをスキルが読み取って、この手順通りにPlaywright CLIでアプリを操作し、動作確認の全ての行程のスクリーンショットと、実施した動作確認をすべて書き起こしてくれます。

### 動作確認手順書の通りアプリを操作するSKILL.md

続いて、**自然言語の手順書をClaude Codeが解釈してブラウザ操作に変換する部分**について紹介します。  
以下の流れをClaudeのスキル(SKILL.md)として作成しました。

1. `playwright-cli`でブラウザを開き`localhost:8501`にアクセス、Streamlitのロード完了まで待機
2. 動作確認手順書の各ステップを上から順に解釈・実行
3. 全ステップ完了後、`verification.md`に各ステップの観察メモを書き出す

本記事では作成したスキルを`cicd-browser-verify/SKILL.md`とします。このスキルをGitHub Actions上で`--system-prompt`オプションに渡して実行します。これによって、動作確認手順書に書いてある内容に沿って、ClaudeがPlaywright CLIを使用してアプリケーションの動作確認とエビデンスとしてのスクショの撮影を行い、レポートの作成まで行ってくれます。

### HTMLレポートをArtifactに保存し、PRにURLを自動返信

こちらの機能では、**作成した動作確認レポートはHTML形式で作成して、GitHubのArtifactに配置する方法**をとりました。

**本当はPRに対して、スクリーンショット付きのコメントと言う形で返信をしたかった**のですが、GitHubのコメントに画像をインライン表示するには**公開アクセス可能なURLが必要**であるということが分かりました。  
外部の画像ホスティングサービスにアップロードして、公開URLを作成して、そのURLをコメントに貼る必要がありました。この方法だと、URLを知っている人全てがアプリの中身を見れてしまうので避けたいと思いました。

そこで、**スクリーンショットをBase64エンコードしてHTMLに直接埋め込んで、GitHubのArtifactにファイルを生成する方法**を思いつきました。これであれば、外部への画像アップロードしなくて済みます。

## GitHub Actionsへの組み込み時に必要なこと

本記事のメインとなる機能の説明を前述したので、実装の流れを紹介していきます。具体的なコードは割愛します。

### 事前準備

GitHub ActionsでClaudeを使用するには、ClaudeのOAuthトークンをGitHub Secretsに設定するなど、事前準備の必要があります。Claude Codeのセットアップ自体は色々な方が解説されているので、こちらを参考にしてください。

<https://zenn.dev/mohy_nyapan/articles/133279a79c7dcd>

### ワークフローのトリガー設定

本記事のワークフローでは、`paths`を設定していて、`docs/operation_check.md`が変更されたPRのみに対して実行されます。手順書を更新したときだけ動作確認が走るので、むやみにCIが走るのを防げます。

```
on:
  pull_request:
    paths:
      - "docs/operation_check.md"
```

### 環境構築

このワークフローでは以下の環境構築するフローが必要です。  
以下をセットアップするコマンドをGitHub Actionsに組み込みます。日本語フォントをインストールしないと、**スクリーンショットの日本語が文字化けしてしまう**場合があります。

* **Pythonのセットアップ**
* **Node.jsのセットアップ**
* **playwright-cliのインストール**
* **Claude Codeのインストール**
* **日本語フォントのインストール**
* **必要に応じて外部サービスの認証情報ファイルの生成**（Streamlitアプリ上で外部サービス上にあるデータを参照したい場合など）

### Streamlitの起動

CI上でアプリを実際に動かしてブラウザからアクセスできる状態にするため、Streamlitをバックグラウンドプロセスとして起動します。`--server.headless true`でブラウザ自動起動を抑制し、`--server.port 8501`でポートを指定します。

```
pipenv run streamlit run "streamlit_main.py" \
  --server.headless true \
  --server.port 8501 &
STREAMLIT_PID=$!
```

また念の為、以下のコマンドで、Streamlitが起動するまで60秒ほど待つようにしました。ブラウザに何も写っていない画面を見たPlaywright CLIが動作確認を進めてしまうのを避けるためです。

```
timeout 60 bash -c 'until curl -sf http://localhost:8501/_stcore/health; do sleep 2; done'
```

### Claude Codeの実行

Streamlitの起動完了後、以下のコマンドでClaude Codeを実行するようにワークフローを作ります。スキルを`--system-prompt`に渡し、手順書を読んでブラウザ操作するよう指示します。

```
claude -p \
  --system-prompt "$(cat .claude/skills/cicd-browser-verify/SKILL.md)" \
  --allowedTools Read Write "Bash(playwright-cli:*)" "Bash(mkdir:*)" \
  -- \
  "docs/operation_check.mdを読んでPlaywrightで動作確認を実行してください"
```

また、GitHub Actions上で動かすため、`-p`を指定し、非対話モードで実行するように設定をしました。そして、非対話モードでは承認プロンプトが発生すると処理が停止してしまうため、`--allowedTools`を使って必要なツールをあらかじめ許可しました。これで、指定したツールの実行時に承認が不要になり、ワークフローが途中で停止せずに実行できるようになります。

ジョブ終了時にStreamlitが永遠に実行中のままになるということを防ぐため、`trap`を使って確実に停止するようにしました。

```
cleanup() {
  kill "$STREAMLIT_PID" 2>/dev/null || true
}
trap cleanup EXIT
```

さらに、このステップ全体には念のため`timeout-minutes`を30分に設定しました。たとえば Streamlitアプリ側でエラーが発生した場合に、Claude Codeが待機し続けてしまうといったことを防ぐためです。

### レポート生成とPRコメント投稿機能の組み込み

Streamlit起動・Claude Code実行の後は、Pythonスクリプトを順番に呼び出してレポートを完成させ、レポートのURLをPRにコメントで返信します。これらのスクリプトもワークフローに組み込んで、GitHub Actionsに実行してもらいます。

#### 動作確認・レポート生成ジョブ

* `generate_report.py`  
  HTML形式のレポートを作成するスクリプトです。  
  Claude Codeが出力した`verification.md`(動作確認ログ）と画像を読み込み、テキストと画像がセットで並ぶHTMLに変換します。  
  **ここはClaudeと相談しながら、レポートの出力が綺麗になるように微修正を重ねました。**
* `generate_manifest.py`  
  Run ID・commit SHAなどをjson形式で書き出すスクリプトです。  
  `post_pr_comment.py`でこのjsonを読んで、PRのコメントに投稿をして、どのジョブの動作確認なのかを分かりやすくすることが可能にしました。「[PRのコメントにレポートのリンクを返信](#pr%E3%81%AE%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88%E3%81%AB%E3%83%AC%E3%83%9D%E3%83%BC%E3%83%88%E3%81%AE%E3%83%AA%E3%83%B3%E3%82%AF%E3%82%92%E8%BF%94%E4%BF%A1)」で添付した画像にcommitのハッシュやURLをコメントで返信していますが、このハッシュやURLを生成するための準備です。

#### PRコメント投稿ジョブ

* `post_pr_comment.py`  
  `generate_manifest.py`で生成したjsonを読んで、実際にPRにコメントで投稿するスクリプトです。

以上がGitHub Actionsに組み込むうえで必要だった工夫です。

## まとめ

以上のように、動作確認手順書を用意するだけで、PR作成時にClaudeにスクリーンショット付きの動作確認レポートを自動生成してもらうことが可能になります。

レビュー依頼時に、アプリケーションの動作確認内容をレビュワーへ共有する際、スクリーンショットを撮って貼り付けながら手順を記述するのは、時間がかかる作業だったりしますが、これでClaudeが代わりにやってくれます🏋️

少しだけ宣伝なのですが、「Data Engineer Casual Talk」というYoutube Channelを解説したので、見守っていただけると幸いです。

<https://www.youtube.com/@DataEngineerCasualTalk>
