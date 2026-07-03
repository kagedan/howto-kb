---
id: "2026-07-03-intellij-idea-が-git-ワークツリー-に対応したので並行作業に使ってみた-01"
title: "IntelliJ IDEA が Git ワークツリー に対応したので、並行作業に使ってみた"
url: "https://zenn.dev/nattosystem_jp/articles/18a20d887b9952"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

## はじめに

IntelliJ IDEA 2026.1 で Git ワークツリー が IDE ネイティブ対応になりました。

<https://www.jetbrains.com/idea/whatsnew/2026-1/#page__content-git-worktrees>

今回は実際に使ってみた内容をまとめています。

この機能を使うことによって、ワークツリーを作成し、別のワークツリーをAIエージェントに渡しながら、メインブランチでの作業を継続するなど、同時に、中断することなく作業を行うことができます。

## Git ワークツリー（worktree）とは

ワークツリー は、**同じリポジトリから作業フォルダをもう 1 つ増やす**仕組みです。

`.git`（履歴・ブランチの本体）は共有したまま、**フォルダごとに別のブランチを展開**できます。

```
IntellijWork/
├─ Master/              ← main（メイン作業）
└─ spring-demo-agent/   ← 別ブランチ（並行作業）
```

クローンし直すのと違って、履歴を二重に持たないのでディスクにも優しい、という利点もあります。

## IntelliJ IDEA で ワークツリーを作る

1. Git ツールウィンドウ（`Alt+9`）の **ワークツリー**を選択
2. **「新規ワークツリー」** をクリック
3. 以下を指定する:
   * **元のブランチ**: 元にするブランチ
   * **新規ブランチ**: 新しいブランチ名
   * **プロジェクト名** / **場所**: worktree を作成する場所

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--CDloBPv_--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/3838a45a-5464-4794-9ee6-ea8cf60dadbd.png?_a=BACMTiAE)

「ワークツリーの作成」を押すと、どのウィンドウで開くかを確認するポップアップが開きます。

* **現在開いているウィンドウ**: 今のウィンドウが worktree に置き換わる
* **新規ウィンドウで開く**: 別ウィンドウで worktree が開く（今のプロジェクトはそのまま残る）

並行作業が目的なら **新規ウィンドウで開く** と 2 つのウィンドウ（メインと worktree）が同時に開くことができます。

## ワークツリーを切り替える・削除する

作ったあとの管理も同じGit ツールウィンドウのワークツリータブからできます。

* **切り替え**: Worktrees タブで対象の worktree を**ダブルクリック**すると、そのウィンドウに移れます。IDE の外（CLI など）で作った worktree もここに一覧表示されます。
* **削除**: 不要になったら Worktrees タブから削除。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--D4Xms93l--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/12ba0c1b-ef7c-4358-913d-cea3d58a9e31.png?_a=BACMTiAE)

## 片方で作業しながら、もう片方を走らせておく

**worktree 側で時間のかかる作業を走らせ、自分はメイン側で別の作業を続ける**という分担を試しました。

今回は worktree 側（`agent/payment-tests` ブランチ）で、AI コーディングエージェントの Junie に `spring-demo-project` のテスト追加を依頼し、走らせている間、**自分はメインのウィンドウ（`main`）に戻って別作業を続けました**。

worktree 側で何が起きていても、メイン側はまったく影響を受けません。  
実際、一連の作業のあいだ `main` は最後までクリーンなままでした。

```
$ git -C Master status -sb
## main...origin/main      # 変更ゼロ
```

エージェントの作業は `agent/payment-tests` ブランチの別フォルダに閉じています。  
もし 1 つのフォルダでこれをやっていたら、走らせている側の未完成な変更と自分の作業が混ざって落ち着かなかったはずです。  
「**片方を隔離して走らせ、片方で手を動かし続ける**」 worktree でよかったところでした。

![タイトルなし.png](https://res.cloudinary.com/zenn/image/fetch/s--wkqmEBOh--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/63b67390-a0fb-47a1-b8f1-1e31de585593.png?_a=BACMTiAE)

## 注意点

便利な一方で、worktree ならではの注意点がいくつかありました。

### 1. worktree の中に worktree を作らない

メインのプロジェクトフォルダ**の中**に worktree を作ると、IntelliJ が **multi-root プロジェクトと誤認**して連携が壊れます。  
`Projects/main/linkedWorktree` のような入れ子配置は避け、**別の親フォルダ**に作るのが安全です。

### 2. 同じブランチは 2 つの worktree で同時に開けない

`main` をメインのフォルダで開いている場合、別の worktree で同じ `main` をチェックアウトすることはできません。  
worktree 側では**別のブランチ**（新規ブランチを切るのが自然）を使います。

### 3. gitignore された `.idea` は worktree 間で共有されない

これがいちばん実用的な発見でした。新しく開いた worktree のウィンドウには、Maven ツールウィンドウが出ませんでした。メイン側には出ているのに、です。

理由は、**このプロジェクトで `.idea`（IntelliJ のプロジェクト設定）を `.gitignore` しているため**でした。git worktree が各フォルダに展開するのは「**git が追跡しているファイル**」だけなので、ignore された `.idea` は共有されず、worktree ごとに新規生成されます。「どの `pom.xml` を Maven プロジェクトとして扱うか」という情報は `.idea` の中にあり、メイン側では取り込み済みでも、新しく開いた worktree にはその情報がありません。

`pom.xml` を右クリック →「**Add as Maven Project**」で取り込み直したら、Maven ツールウィンドウが現れました。

## まとめ

IntelliJ IDEA 2026.1 の Git worktree を実際に使ってみました。

* 作成・切り替え・削除が Worktrees タブ（`Alt+9`）IDE の中で完結する。
* New Window で開けば、メインと worktree を 2 画面で同時に進められる。ブランチ切り替えの stash も、ビルドの再生成もいらない
* 片方で時間のかかる作業（今回はエージェント）を走らせ、自分はメインで作業を続けても、メインは変わらない
* 注意点は、入れ子にしない / 同じブランチは不可 / gitignore された `.idea` は共有されない

「急ぎの割り込みが来たら別フォルダで対応する」「重い処理は別ブランチに隔離して走らせておく」並行作業が、ブランチ切り替えができるようになります。

まずはWorktrees タブから 1 つ worktree を作って、いつもの作業を 2 画面でやってみることをおすすめします。

## ナットウシステムからのお知らせ

弊社は JetBrains 製品に関するご質問、ご相談等を受け付けております。弊社の[X](https://x.com/nattosystem?s=20)または[メール](mailto:sales@nattosystem.com)でご連絡ください。

## 参考資料

<https://www.jetbrains.com/idea/whatsnew/2026-1/#page__content-git-worktrees>

<https://www.jetbrains.com/ja-jp/help/idea/use-git-worktrees.html>

<https://git-scm.com/docs/git-worktree>
