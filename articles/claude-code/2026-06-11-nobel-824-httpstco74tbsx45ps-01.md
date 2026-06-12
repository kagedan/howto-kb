---
id: "2026-06-11-nobel-824-httpstco74tbsx45ps-01"
title: "@nobel_824: https://t.co/74tBSX45ps"
url: "https://x.com/nobel_824/status/2064946224751599698"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "x"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/74tBSX45ps


--- Article ---
「Claude Code は入れたけど、結局チャット代わりにしか使えていない」 「便利そうなのに、毎回同じ前置きを打ち込むのが面倒で続かない」

Claude Code を仕事で触り始めた人なら、たぶん一度は通る道です。

インストールして起動するだけだと、ターミナル（黒い画面）の中で動く高機能なチャットとして半分も使えないまま終わります。

本領は、ローカルのシェルと深く同期して、ファイル操作やコマンド実行まで自分で進めるエージェント（自律的に作業するプログラム）にあります。

先に結論を言うと、最初の設定をちゃんと組むかどうかで、その後の体感がはっきり変わります。

毎回「日本語で答えて」「テストを先に流して」と打ち込む前置きが消え、変更のたびに押していた承認も減り、定型作業はコマンド一発で呼べるようになります。

僕も最初は確認に疲れて放置していたのですが、設定スコープと CLAUDE.md を整えたら、任せて検品するだけの時間がぐっと増えました。

逆にここを飛ばすと、便利なはずのツールが宝の持ち腐れになります。最初の30分の差が、その後ずっと効いてきます。

申し遅れました。tatsuki（[@nobel_824](https://x.com/nobel_824)）と申します。

中小企業向けに AI の活用サポートをしていて、Claude / Codex の業務導入を手伝いつつ、自分でも Claude Code を1日中走らせています。

この記事は CLI（コマンドで操作する入口）でガッツリ使い込む中級者向けに、初期設定と実務コマンドを、すべて2026年6月時点の[公式ドキュメント](https://code.claude.com/docs/en/settings)で裏取りしながらまとめました。

## 1. 導入直後にやるべき「3つの構造的セットアップ」

Claude Code は単なるチャットツールではありません。だからこそ、最初に土台を3つだけ整えておくと、後の運用が楽になります。

① 設定スコープを理解して散らからせない

Claude Code の設定には「Managed / User / Project / Local」という4つのスコープ（適用範囲）があります。ここを整理せずに設定を散らかすと、チーム開発で「自分の環境では動くのに他の人は動かない」が起きます。公式の[設定リファレンス](https://code.claude.com/docs/en/settings)に沿って役割を分けると、こうなります。

スコープファイル用途共有User~/.claude/settings.jsonテーマや個人の好みなど、全プロジェクト共通の項目しないProject.claude/settings.jsonテストコマンドや権限など、チームで共有する設定。Git にコミットするLocal.claude/settings.local.json自分だけのデバッグ設定・マシン固有のパス。gitignore 対象しないManagedmanaged-settings.json（システム配置）IT/DevOps が組織に展開するセキュリティ・コンプライアンス。上書き不可する（IT 配布）

同じ設定が複数のスコープにあるときの優先順位も公式に明記されていて、強い順に「Managed（最上位。コマンドライン引数も含め、何物も上書きできない）> コマンドライン引数 > Local > Project > User」です。実務では「チームの標準は Project、個人のこだわりは User、機密に触る制限は Managed」と分けておくと事故りません。

今日できる1アクション: .claude/settings.json（Project）と ~/.claude/settings.json（User）に何が書いてあるか一度開いて、個人設定が Project に紛れ込んでいないか確認する。

② シェルスナップショットでエイリアスを引き継ぐ

普段ターミナルで使っている ll や gs といったエイリアス（コマンドの短縮名）を、Claude Code の中でもそのまま使えると作業が速くなります。これは起動時に ~/.claude/shell-snapshots/ へ、いまのシェル環境（関数・エイリアス・環境変数）をスナップショットとして保存し、各コマンド実行の前に読み込み直す仕組みがあるからです。

もしエイリアスが通らないときは、Claude Code を再起動してスナップショットを作り直すか、.zshrc や .bashrcの定義が正しく読まれ
