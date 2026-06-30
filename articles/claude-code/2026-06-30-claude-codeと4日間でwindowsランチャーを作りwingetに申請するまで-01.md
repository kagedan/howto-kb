---
id: "2026-06-30-claude-codeと4日間でwindowsランチャーを作りwingetに申請するまで-01"
title: "Claude Codeと4日間でWindowsランチャーを作り、WinGetに申請するまで"
url: "https://zenn.dev/hidecode365/articles/3af41c981730ff"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

ずっと Launchy というランチャーアプリを使っていた。

キーボードだけでアプリを起動できる、あのシンプルさが好きだった。  
でも最近、動作が怪しくなってきた。古いツールだから仕方ない。

Flow Launcher に乗り換えも試みたけれど、機能が多すぎて逆に疲れた。  
「もっとシンプルでいい。自分が使う機能だけあれば」

それなら作ってしまおう、と思ったのが WinLauncher の始まりです。

Tauri v2 + React + Rust という構成で、Claude Code と一緒に開発を進め、  
着手からわずか4日で WinGet（Windows の公式パッケージマネージャー）への申請まで届きました。

この記事では、WinLauncher がどんなツールか、  
そして Claude Code との開発体験がどんなものだったかを書いていきます。

![](https://static.zenn.studio/user-upload/ad98a9a061f0-20260630.png)

## WinLauncher の魅力

WinLauncher の基本はシンプルです。  
Alt+Space を押すと、画面中央にランチャーが現れる。それだけ。

でもこの「それだけ」が、思いのほか快適でした。  
マウスに手を伸ばさなくていい。タスクバーを探さなくていい。  
キーボードから手を離さずに、次の操作へ移れます。

ランチャーとしての基本機能はもちろん揃っています。  
ファイル検索、アプリ起動、Web検索。  
これだけでも十分使えます。

さらに、こんな機能も入っています。

**クリップボード履歴**  
コピーしたテキストや画像が、ランチャーの中にまとめて残っています。  
「さっきコピーしたやつ、どこいった？」が消えました。

**電卓**  
数式を入力するとその場で計算結果が出る。  
わざわざ電卓アプリを開く必要がありません。  
結果はそのままクリップボードにコピーできます。

全部ひとつの画面で完結する。  
これが自分の求めていたシンプルさでした。

![](https://static.zenn.studio/user-upload/d4c234b377b9-20260630.png)

## Claude Code との開発体験

正直に言うと、最初は半信半疑でした。  
「AIにコードを書かせる」というのは、なんとなく補助的なものだと思っていたから。

でも実際に使ってみて、印象が変わりました。

**指示するだけで動く、その速さ**  
「こういう機能を作りたい」と伝えると、数分でコードが出てくる。  
しかも、ビルドエラーが出れば自分で原因を調べて直してくれる。  
自分はほとんどコードを書いていません。

**ワークフローの核心は REQUIREMENTS.md**  
このプロジェクトでは、こういう進め方をしていました。

1. Claude.ai で要件を整理し、REQUIREMENTS.md に書き出す
2. Claude Code に「REQUIREMENTS.md を読んで実装して」と指示する
3. Claude Code が実装を進めながら、CLAUDE.md を自分で作成・更新していく

CLAUDE.md は自分が書くものではありません。  
Claude Code が設計判断や注意事項を自ら記録していくファイルです。  
次の指示を出すときも、Claude Code は CLAUDE.md を読み返して文脈を引き継いでくれます。

REQUIREMENTS.md さえ丁寧に書いておけば、あとは任せられる。  
自分の役割は、要件を言語化することだけ。

**4日間で WinGet 申請まで届いた理由**  
スピードの源泉はここにあったと思っています。  
「何を作るか」に集中できたから、「どう作るか」に時間を取られなかった。

Tauri v2 + React + Rust の知見がなくてもやれるとは思っていました。  
でも、想像以上に簡単で、想像以上に速かった。

![](https://static.zenn.studio/user-upload/f8de7b61f430-20260630.png)

## WinGet への申請

WinGet は Windows 公式のパッケージマネージャーです。  
登録されると、コマンド一つでインストールできるようになります。

```
winget install WinLauncher
```

申請は GitHub のプルリクエストで行います。  
難しそうに聞こえますが、手順は意外とシンプルでした。

**申請の流れ**

1. [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs) をフォーク
2. マニフェストファイル（yaml）を作成してプルリクエストを出す
3. 自動チェックが通ればヒューマンレビューへ
4. 承認されれば公開完了

**マニフェストファイルとは**  
アプリ名・バージョン・ダウンロードURLなどを記載した yaml ファイルです。  
`wingetcreate` というツールを使えば、対話形式で自動生成できます。

```
winget install Microsoft.WingetCreate
wingetcreate new https://（インストーラーのURL）
```

あとは生成されたファイルをプルリクエストとして提出するだけ。  
審査は数日〜数週間かかることもありますが、待つだけです。

個人開発のアプリが Windows の公式ルートに載る。  
小さいけれど、じわっと嬉しい体験でした。

![](https://static.zenn.studio/user-upload/5ed62d9b64e0-20260630.png)

## まとめ

「シンプルなランチャーが欲しい」という小さな不満から始まって、  
4日間で WinGet への申請まで届きました。  
（この記事執筆時点だと、まだWinGetでの審査中です。）

Claude Code との開発体験は、想像以上に快適でした。  
要件を言語化することに集中できれば、実装はほとんど任せられる。  
個人開発のハードルが、確実に下がっています。

WinLauncher はこれからも地道に育てていくつもりです。

使ってみた感想、気になる機能、こんなの欲しいという要望など、  
気軽にコメントしてもらえると嬉しいです。

👉 GitHub: <https://github.com/hidecode365/win-launcher>
