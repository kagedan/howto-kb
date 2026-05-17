---
id: "2026-05-16-claude-dispatch-で生成ファイルをスマホで見るならgoogle-drive-デスクトッ-01"
title: "Claude Dispatch で生成ファイルをスマホで見るならGoogle Drive デスクトップ版を入れること(Mac)"
url: "https://zenn.dev/and_dot/articles/c8f3a2d5e1b047"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "Gemini", "GPT", "cowork"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは、アンドドット CTO の高根沢です。

直近、外出先からオフィスのMac環境にあるAIを遠隔で動かせる、Claude Cowork の **Dispatch** 機能をよく活用しています。  
ただ、この機能、スマホから「最新ニュースをまとめてスライドを作って」と指示を投げるまでは非常に快適なのですが、、実際に使っていると一つの大きな壁にぶつかります。それは **「完成した PPTX をスマホからどうやって開くか」** という問題です。

「Google Drive にアップロードして共有リンクを返して」とプロンプトで指示するのが定石に思えますが、**現状ではこの指示がほぼ通りません**。Google Drive コネクタ（MCP）が書き込み（`create_file`）に対応した現在でも、**Dispatch 内での実行とは噛み合っていない**のが実情です。

![スマホ Dispatch のチャットで、Claude が Google Drive コネクタ経由のアップロードを試みているが、利用可能なツール候補を ToolSearch で探したり、複数のコード例を出したりと回り道している様子が表示されている](https://static.zenn.studio/user-upload/deployed-images/b17b0f4f8145747e90e51c03.png?sha=efda45749370f46084f8a64edecce81e9f813670)  
*スマホ側から見たコネクタアップロード試行の様子。Claude が「使えるツールが何か」を探し回り一向に書き込みが完了しない*

現在考えられる実用的な解決策は、**Mac に Google Drive デスクトップ版を入れて、Claude にはローカルファイル書き込みとして指示する**ことかなと思います。  
この構成がうまくいくと、Dispatch で生成した成果物がスマホの Drive アプリから以下のように確認できるようになります。

![スマホの Google Drive アプリで「Claude Work」フォルダを開いた画面。「AIニュース週次レポート_2026-04-18_v2.pptx」「AIニュース週次レポート_2026-05-08.pptx」「ネクストアクション一覧_2026-04-18」など、Dispatch から書き込まれたファイルが時系列で並んでいる（一部フォルダ名はモザイク処理）](https://static.zenn.studio/user-upload/deployed-images/b4facae1c83bf184a4d9b60b.png?sha=9fa4dff93f57c49ecd42ecf73e324baf94688887)  
*Dispatch で生成した PPTX が、Drive Desktop の同期経由でそのままスマホの Drive アプリに現れる。これが Dispatch×Drive 運用の最終形*

![スマホで PPTX を開いた画面。アンドドット (and.) ロゴ入りの「AIニュース週次レポート CTO・経営層向け 最新動向インプット」表紙が表示され、アジェンダ (01 エグゼクティブサマリー〜07 経営アクション提案) と冒頭のサマリーが続けて見える](https://static.zenn.studio/user-upload/deployed-images/118f015dfc81f04593743d73.png?sha=238c31665677e11dea18578c092e9f1e917a604a)  
*Drive Desktop 経由で同期した PPTX を、外出先のスマホで開いた状態。表紙〜アジェンダがそのままプレビューでき、移動中のレビューに耐える*

本記事では、その経緯と具体的な手順についてまとめていきます！

## 前提：Dispatch の仕組み（30秒で解説）

Dispatch は、スマホ（Claude アプリ）から Mac 上の Cowork セッションに指示を送り、ローカル環境でタスクを実行させる機能です。

必要な最低条件は以下の2点のみです。

* Mac の設定 → Cowork で Dispatch トグルをオンにする
* 「このコンピュータをスリープさせない」をオンにする

QR ペアリングは廃止されており同じアカウントでサインインしていれば、トグル1つで両端末がリンクされます。  
セットアップの詳細（対応プラン、権限設定、Managed Agents との使い分けなど）については、以下の別記事にまとめていますので、ご覧ください！  
→ [Claude Cowork Dispatch のセットアップ完全ガイド──QR ペアリング廃止後の最新フロー](https://zenn.dev/and_dot/articles/e42520784892a2)

## 課題：コネクタ経由のアップロードが完走しない

実際にスマホから以下のように指示を出してみます。

> スライド作成したい。今週の最新AIニュースについて、CTO経営向けで15枚

タスク完了の通知は届きますが、スマホ上では PPTX のサムネイルが表示されるだけでファイルを開くことができません。

![Dispatchのスマホ画面で「AI news slides for CTO」タスクが完了し、PPTXファイル「AI news週次レポート_2026-...」がチャットに表示された状態](https://static.zenn.studio/user-upload/deployed-images/6fa08f11da2871cb808e3db6.png?sha=76298cc40b6faca88939783b931e8ed3ac0f049b)  
*完成通知は届くが、PPTX はチャット内のサムネイル止まり。スマホから開いてレビューすることはできない*

そこで「Google Drive にアップロードして共有リンクを返して」と追加指示を出してみますが、ここからの動作が安定しません。Google Drive コネクタには書き込み用の create\_file ツールが用意されており、承認さえすれば本来は書き込めるはずなのですが、実行失敗が頻発します。

![Google Drive コネクタの権限設定画面。読み取り専用ツール6種(download_file_content, get_file_metadata, get_file_permissions, list_recent_files, read_file_content, search_files)と書き込み/削除ツール1種(create_file)が一覧されている](https://static.zenn.studio/user-upload/deployed-images/2c123f0c67029f77300d6899.png?sha=fa18b0db3f764173f19acc185d5dcb35068d2551)  
*書き込み用に `create_file` というツールはちゃんと存在している。承認も通せる。にもかかわらず、Dispatch 越しに呼ぶと完了まで届かないことが多い*

Mac 側の挙動を確認すると、ツールを呼び出した後に利用可能なツール候補を再検索したり、別のアプローチを試したりと、Claude が迷走を始めてしまい、成果物が Drive にアップロードされません。承認自体は通っているため権限の問題というよりは、現状のコネクタ実装が Dispatch のような実行と相性が悪いというのが実態だと考えられます。

![Mac側の Claude が Google Drive へのアップロードを試行中の画面。create_file ツールの使用権限ダイアログが表示され、右パネルには ToolSearch を含む複数ステップのタスクリストが進行中](https://static.zenn.studio/user-upload/deployed-images/5c2e6b33f53d6a09594d6811.png?sha=a7bce6fce810fd6a34a32eaad67e2c00ba2e08cd)  
*Mac 側で進行中のセッション。許可は出せるものの、その後の書き込みが安定して完走せず、結局スマホには共有リンクが返ってこない*

## 解決策：Google Drive デスクトップ版でローカル経由にする

コネクタに依存せず、Mac に「Google Drive デスクトップ版」（Drive for desktop）をインストールし、Drive をローカルフォルダとしてマウントする方法であれば、Dispatch からも安定して書き込みが可能です。

### 手順

1. [Google Drive デスクトップ版](https://www.google.com/drive/download/) をインストールし、サインインする
2. Finder のサイドバーに「Google Drive」が表示されることを確認（実体パスは `~/Library/CloudStorage/GoogleDrive-{あなたのメールアドレス}/My Drive/`）
3. Dispatch で指示を出す際、コネクタ経由ではなく、**コネクタ経由ではなく上記パスへのローカルファイル書き込み**として指示する

インストール完了後、`My Drive/` 配下が通常のローカルフォルダと同様に読み書き可能になります。

!

**初回のみ macOS の権限ダイアログで「許可」が必要**

Claude が初めて `~/Library/CloudStorage/GoogleDrive-.../My Drive/` 配下にアクセスする際、macOS 側から「Claude が Google Drive のフォルダにアクセスしようとしています」というシステムダイアログが表示されます。  
**ここは必ず「許可」を選択してください**。これは Claude アプリ内の権限とは異なる OS レベルの権限であり、拒否すると以降の書き込みができなくなります。Mac の前にいる人にしか操作できないダイアログのため、**外出前に一度ダミーの指示を投げて許可を通しておく**のが安全です。

![Mac の Finder で「Google Drive > My Drive > Claude Work」フォルダを開いた画面。AIニュース週次レポート_2026-04-18_v2.pptx (439 KB)、AIニュース週次レポート_2026-05-08.pptx (1.2 MB)、ネクストアクション一覧_2026-04-18 (gdoc) などの同期済みファイルが並ぶ（フォルダ名と左サイドバーはモザイク処理）。下部パスバーに「Google Drive > My Drive > Claude Work」の階層が表示](https://static.zenn.studio/user-upload/deployed-images/f2bf1e959b603df2e3d27685.png?sha=ac7f4e2a527750be4090fe23651db67db86f5563)  
*Drive Desktop でマウントされた「Claude Work」フォルダ。Claude が生成した PPTX がそのままローカルファイルとして見え、雲アイコン付きで自動同期される*

プロンプト例:

> 本日時点の最新情報収集してスライド作成して `~/Library/CloudStorage/GoogleDrive-{自分のメアド}/My Drive/Claude Work/` に保存して。同期完了したら Drive で見られる

#### Tip: 保存先パスは Claude に探索させると確実

`~/Library/CloudStorage/GoogleDrive-{メアド}/My Drive/` というパスは長く、環境によって微妙に異なる場合があります。慣れないうちは、**いきなりフルパスを指定するのではなく、Dispatch で「Drive Desktop のマウント先を確認して」と先に調べさせ、返ってきたパスに合わせて保存先を指示する**方が、外出先で確実に対応できます。

![スマホ Dispatch のチャットで、ユーザーが「Google ドライブがローカルにマウントされているとのことだが確認はできますか？」と聞き、Claude が  ツールを実行してマウント先  を返答。続けてユーザーが「マイドライブの Claude Work フォルダに保存すること」と指示し、Claude が「 配下に保存」「完了しました🎉」と応答する流れ](https://static.zenn.studio/user-upload/deployed-images/aa5f54a2cd216991c40c544e.png?sha=71b5d37384ad4f8f0ea94224e889788693665e18)  
*マウント先を聞く → 返ってきたパスに合わせて保存先を指定 → 同期。Claude 側に「Check Drive Desktop mount」のような確認手段があるので、人間がパスを覚えていなくても進められる*

スマホからこのように指示すると、Dispatch 側ですぐにタスクが起動し、Mac 上で調査と PPTX 生成が開始されます。

![スマホ Dispatch の画面で、「AI news deck May 8 + Drive sync」というタスクが起動し、Claude が「今日(5/8)時点の最新トピック」として Claude Sonnet 4.7、ChatGPT-5、Gemini Personal Intelligence、Anthropic 58008 バリュエーション交渉、EU AI Act 第二フェーズ施行などのニュースを整理しながら作業中の様子](https://static.zenn.studio/user-upload/deployed-images/a206f96ba2dbbd050f8caf8e.png?sha=e9dc1a5fe41b264c59250517114b98d0e46f4189)  
*スマホから「Drive に保存」と指示すると、その場でタスクが立ち上がって調査 → 生成 → 書き込みが流れ始める*

この方法であれば、コネクタの `create_file` 承認ダイアログは出ません。代わりに、初回のみ Claude のローカルファイル書き込み権限ダイアログが一度だけ表示されるので、それを許可するだけで済みます。

![スマホ Dispatch の画面で、Claude が「Drive Desktop経由で Claude Work フォルダに同期で進めます」と応答した直後、 への書き込み許可を求めるダイアログが表示され、「一度だけ許可」「拒否」ボタンが並んでいる](https://static.zenn.studio/user-upload/deployed-images/7fd3aa56a37741d210cabfd2.png?sha=c465345e9fcb2776a4078ab403aa92d839e6cada)  
*スマホ側から見た書き込み許可ダイアログ。コネクタの `create_file` 承認とは別物で、Claude のローカルファイル権限なので一度許可すれば以降止まらない*

許可後は Dispatch 中の無人実行でも問題なく書き込みが行われ、Drive Desktop が自動でクラウドへ同期するため、スマホの Drive アプリからすぐに開けるようになります。

つまり、\*\*「Mac にネイティブな Drive クライアントを導入し、Claude にはローカルへの書き込みだと思わせる」 \*\*ことが、現状の最適解と言えます。

## 現状の制約事項について

* **シングルスレッド制約**: Dispatch は1スレッド固定。並列でタスクを走らせたい場合は、Claude Code の Remote Control の方が適している
* **Mac スリープ = 全停止**: 外出前に必ず電源接続を確認すること（バッテリー駆動で電池切れになるとタスクが停止してしまうため）
* **プッシュ通知はデフォルト OFF**: Mac 側の画面下部バナーから、明示的にオンにする必要がある

## まとめ

Dispatch で生成したファイルを外出先でシームレスに確認するには、**現状は Google Drive コネクタの使用を避け、Google Drive デスクトップ版とローカルファイル書き込みを組み合わせる**のが現実的です。

Google Drive MCP（コネクタ）側にも create\_file ツールが用意されていますが、Dispatch のような無人実行環境から呼び出すと動作が安定しないのが現状の課題です。今後コネクタの実行が安定し、無人実行とスムーズに連動するようになれば、こうした OS 側のクライアントに頼る必要もなくなるはずです。アップデートを待ちつつ、それまではこのローカルマウント経由の手法で乗り切っていきましょう。

## 一緒に"爆速文化"をつくる仲間を募集しています

アンドドットでは、生成AIとともにプロダクトを創り上げ、少数精鋭で大きな成果を出す組織を目指しています。AI活用を前提とした新しい開発スタイルに興味のある方、ぜひ一度カジュアルにお話しましょう。

<https://calendar.google.com/calendar/appointments/schedules/AcZssZ2betA1myxHjAccbO6w6EEDYG6SGfdlymYyx2MJBIwHamQtmzI66cm7Da7aLiC4sYSbXv-CP846>
