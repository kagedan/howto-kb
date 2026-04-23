---
id: "2026-04-06-claude-md-improverでclaudemdの品質評価をする-01"
title: "claude-md-improverでCLAUDE.mdの品質評価をする"
url: "https://note.com/masaru_furuya/n/nf5e62c1b4c1f"
source: "note"
category: "claude-code"
tags: ["CLAUDE-md", "note"]
date_published: "2026-04-06"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## 今回解決したいこと

CLAUDE.mdは一度書いたら終わりになりがちです。「これで本当にいいのか？」を判断する軸がないため、作りっぱなしで改善されません。

チームで共有する場合はさらに問題です。共通の評価軸がないと、各メンバーが好き勝手に書き換えてしまい、品質がバラつきます。定量的な評価基準を設けて、継続的に改善できる仕組みが必要でした。

## 解決方針

Anthropic公式プラグイン「[claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management)」に含まれる **claude-md-improver** を使い、100点満点のスコアリングで品質を可視化します。評価→改善→記録のサイクルを回すことで、CLAUDE.mdを「生きたドキュメント」にすることを目指します。

## claude-md-managementプラグインについて

Anthropic公式のClaude Codeプラグインで、2つの機能を持ちます。

プラグインのインストールは  /install-plugin で簡単にできます。

## 使い方

```
/claude-md-improver
```

を実行するだけです。こちらを実行すると今cluade codeを動かしているプロジェクトに存在するCLAUDE.mdへの評価が自動で実行されます。自分の環境では5件 (グローバル1 + プロジェクトルート1 + サブプロジェクト3)への評価が行われました。

## claude-md-improverの動作の仕組み

6つの評価軸で100点満点のスコアリングを行います。

* Commands/Workflows

  + 20点
  + ビルド・テスト等のコマンドが網羅されているか
* Architecture Clarity
* Non-Obvious Patterns
* Conciseness
* Currency
* Actionability

  + 15点
  + コピペで実行できる具体的な手順になっているか

また次の5フェーズ、Discovery（CLAUDE.mdファイルの発見）→ Quality Assessment（採点）→ Report（結果表示）→ Targeted Updates（改善提案）→ Apply（承認制で適用）で動作します。

## 改善点を出して修正を行う

評価レポートで具体的な改善提案が出ます。例えば「heredocが動かないのでbody-fileを使う」といったハマりポイントの追記や、古い参照パスの更新などです。提案は一つずつ承認制で適用できるので、意図しない変更が入る心配はありません。

自分のプロジェクトのCLAUDE.mdは88点でした。そこまで優先度の高い改善点は無さそうです。

![](https://assets.st-note.com/img/1775434059-vVkPnd5qiBmLc1YTIZt6QCyX.png?width=1200)

## 修正結果をシートに記録する

評価スコアをGoogleスプレッドシートに記録しておけば、時系列でCLAUDE.mdの品質推移を追跡できます。チームなら各メンバーのCLAUDE.mdスコアを並べて比較することも可能です。

![](https://assets.st-note.com/img/1775434350-hQ1fJxU5tzEkLw8vuHXejaTs.png?width=1200)

## 今回解決できたこと・今後の改善方針

まずは手動で評価・改善ができるようにはなりましたが、改善点は沢山あります。ダッシュボード化したり、定期自動化などをやれるとより役立ちそうなので、また今後やってみたいですね。
