---
id: "2026-06-09-claude-code-の-code-review-は観点を引数で選べない-effort-は深さ角度-01"
title: "Claude Code の /code-review は観点を引数で選べない ── effort は深さ、角度は固定"
url: "https://zenn.dev/gudezou/articles/514bd112d0a23d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

![サムネイル](https://static.zenn.studio/user-upload/e2af3aac29cd-20260609.png)

* `/code-review` の観点はコードの正しさ (correctness) のバグと再利用・簡素化・効率化の手直しに固定で、引数でレビュー観点は変えられない。
* effort (low から max) は拾う件数と深さを変えるダイヤルで、レビュー観点を変えるものではない。
* 観点を変えたいときは引数ではなく `CLAUDE.md` に書き、セッションコンテキストに含ませるくらいしか方法がない。

---

## /code-review が見る観点は決め打ちになっている

ローカルで動く `/code-review` は、いま手元にある差分を決まった観点でレビューします。  
見るのは、コードが正しく動くか (correctness) に関わるバグと、再利用・簡素化・効率化といった手直しの2系統です。  
前者はバグを見つける検査、後者はコードをすっきりさせる検査で、目的の違う2つがいつも一緒に走ります。

この観点は決め打ちで、引数で「セキュリティだけ」のように角度を切り替える仕組みはありません。  
渡せる引数は effort の段階と ultra、`--fix` / `--comment` / ターゲットの指定だけです。  
code.claude.com > [Commands](https://code.claude.com/docs/en/commands) に並ぶ引数の一覧にも、観点そのものを指定するものは含まれていません。

effort (推論にどれだけ手間をかけるかを決める設定) を low から max まで上げても、レビュー観点は変わりません。  
この effort は推論の深さを決める設定だと、code.claude.com > [Model configuration](https://code.claude.com/docs/en/model-config) は説明しています。  
低い effort は件数を絞って確信度を高くし、high から max は広く拾って不確実なものも含む、という深さの違いだけです。  
effort を省いたときは、そのセッションでいま使っている effort のままレビューします。

![観点は固定で effort は深さの軸だと示す図](https://static.zenn.studio/user-upload/dab381e1c576-20260609.png)

---

## 観点を変えたいなら引数ではなく CLAUDE.md に書く

決まった観点以外もレビューしてほしいときの正規ルートは、呼び出しごとの引数ではなく、セッションに常時読み込まれる `CLAUDE.md` に書くことです。  
`CLAUDE.md` は、Claude Code が毎セッション読み込むプロジェクト共通の指示です。  
ローカルの `/code-review` はこのセッションの文脈として `CLAUDE.md` を踏まえます。

Anthropic の Code Review (GitHub App) は、`CLAUDE.md` を明示的に読み込んで、新しく入った違反を指摘します。  
どちらも、プロジェクト共通の約束ごとを `CLAUDE.md` に書いておけば効いてきます。

この Code Review は、Claude をベースにした自動の PR レビューです。  
GitHub の Pull Request を解析して、指摘を該当行のインラインコメントとして投稿する仕組みです。

このサービスは `CLAUDE.md` に加えて、レビュー専用の `REVIEW.md` も読みます。  
`REVIEW.md` はレビューを行う全てのエージェントに最優先で読み込まれます。  
何をどの深刻度で指摘するかを変えられると、code.claude.com > [Code Review](https://code.claude.com/docs/en/code-review) は説明しています。

`REVIEW.md` はこの Code Review 向けの仕組みです。  
ローカルの `/code-review` コマンドには効果がありません。  
`CLAUDE.md` は両方に効く共通の指示、`REVIEW.md` は Code Review だけに効く追加の指示、と整理できます。

引数で動かせるのは、観点ではなく結果の出力先と対象です。

`--fix` はレビュー後の修正を作業ツリーに適用します。  
`--comment` は指摘を GitHub の PR にインラインコメントとして投稿します。  
対象のパスや PR の参照を渡せば、いまの差分のかわりに特定の対象をレビューできます。

さらに `ultra` を付けると、より深いレビュー (ultrareview) に切り替わります。  
ただしこれは、PR に自動でコメントするさきほどの Code Review とは別の経路です。  
動かせるのは深さ・出力先・ターゲットまでで、観点は `CLAUDE.md` で誘導する、と整理できます。

![引数のルートと CLAUDE.md / REVIEW.md のルートの対比図](https://static.zenn.studio/user-upload/b98c253549b2-20260609.png)

---

## 参考文献

1. Anthropic. *Commands - Claude Code Docs*. Anthropic Documentation. <https://code.claude.com/docs/en/commands>
2. Anthropic. *Code Review - Claude Code Docs*. Anthropic Documentation. <https://code.claude.com/docs/en/code-review>
3. Anthropic. *Model configuration - Claude Code Docs*. Anthropic Documentation. <https://code.claude.com/docs/en/model-config>
