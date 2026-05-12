---
id: "2026-05-11-potatobiz1-codexとclaude-codeを併用するめちゃ便利な方法見つけたわ-このや-01"
title: "@potatobiz1: CodexとClaude Codeを併用するめちゃ便利な方法見つけたわ！ このやり方なら、同じプロジェクトをClaud"
url: "https://x.com/potatobiz1/status/2053787046381260963"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "x"]
date_published: "2026-05-11"
date_collected: "2026-05-12"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

CodexとClaude Codeを併用するめちゃ便利な方法見つけたわ！

このやり方なら、同じプロジェクトをClaude Codeと全く同じルールで編集やテストまで任せられる。公式docsにも載ってる方法。

こんなに簡単ならCodexを別ツール扱いで放置するのはさすがにもったいないな。

順に説明する↓※ブクマ推奨

【1】まず併用のメリットから。

Claude CodeとCodexを別々のAIではなく「同じ現場の作業者」として使えるのが良い点。

例えばClaude Codeで設計を詰めながら、CodexにUI修正やテスト追加を任せるなど、両者の強みを活かせる。

【2】共通ルールで動かすと、こういう分担ができる。

✅Claude Codeで設計を相談して、Codexに実装を任せる
✅Claude Codeでバグ原因を一緒に整理して、Codexに修正とテスト追加を頼む
✅Codexにコードを書かせて、Claude Codeにレビューさせる
✅Claude Codeで仕様を詰めて、CodexにREADMEや設定ファイルまで反映させる
✅Codexに複数ファイルの修正を任せて、Claude Codeで差分の妥当性を見る
✅Claude Codeで文章や要件を整えて、Codexにアプリ内の文言やUIへ反映させる
✅Codexにテストを走らせて、Claude Codeに失敗理由を説明させる
✅Claude Codeでリファクタ方針を決めて、Codexに小さい単位で作業させる
✅Codexに下書きを作らせて、Claude Codeに読みやすさや矛盾をチェックさせる
✅Claude Codeを相談役、Codexを作業役として同じプロジェクトで並走させる

【3】やり方は簡単↓

①Claude Codeで作業したいリポジトリ直下に AGENTS.mdを作成し、ここに共通のルールを書く
②CLAUDE.md 内には 「@./AGENTS.md」と一行書く。「この場所にある AGENTS.md の中身を読んでね」という意味。

これで両方が同じルールの元作業してくれる。

【4】AGENTS.mdとは?

Codexが最初に自動で読むファイルで、Claude CodeのCLAUDE.md みたいなもの。

それぞれのAIは、こういう流れでファイルを読む↓
Claude Code：CLAUDE.md→AGENTS.mdの順に読む。
Codex：最初からAGENTS.mdを読む。

これが共通のルールで動く仕組み。

【5】AGENTS.mdには何を書けばいい？

今までClaude Codeを使ってきたのなら、CLAUDE.mdの内容をAGENTS.mdにコピペでいい。

基本的にはAIに守ってほしい作業ルール・禁止事項などを書けばOK。
・プロジェクト概要
・最初に読むファイル
・触っていい範囲
・テスト方法
・外部APIや秘密情報の扱い等

【5】気をつけるべき点

同じルールを読んでも、判断や癖まで完全一致しない。CodexとClaude Codeで、確認の仕方や得意な作業は違う。

あとAGENTS.mdを雑に書くと、両方が雑に動くw 外部API、触ってはいけないフォルダなどはしっかり書いた方がいい。

このツリーをブクマして両刀使いになろう🍟！
