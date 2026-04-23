---
id: "2026-04-01-エイプリルフールに本気で遊んだclaude-code-sandbox環境構築メモ-01"
title: "エイプリルフールに本気で遊んだClaude Code Sandbox環境構築メモ"
url: "https://zenn.dev/aoikuro/articles/2026-04-01-daily-tech-journal"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

# 今日は4月1日

朝起きてTwitter開いたら案の定、各社のエイプリルフールネタで埋まってた。Google翻訳が「ネコ語」に対応とか、GitHubが「AI Copilot Sleep Mode」実装とか。

で、ふと思った。「せっかくだしコンテナサンドボックスで遊び倒すか」と。

## 結局3時間溶かした

Claude Code使ってコンテナ環境でいろいろ試してたんだけど、地味にハマったのが**コンテナ内でのgit操作**。

エージェントが記事書いて自動でZennにpushする仕組み作ってるんだが、最初こうなった。

```
git push
# To github.com:AOI-Future/zenn-articles1.git
#  ! [rejected]        main -> main (fetch first)
```

「は？」ってなった。

## ハマりポイント: コンテナは世界を知らない

原因は単純。コンテナ環境は起動しっぱなしだから、リモートの変更を知らない。

普段ローカルで開発してると「まあ最新だろ」で`git add → commit → push`してるけど、コンテナは前回起動時点のHEADで止まってる。

だからこうしないとダメ。

```
git pull  # 必ず最初にやれ
git add articles/hoge.md
git commit -m "..."
git push
```

`git pull`を省略すると100%rejected食らう。

## エージェントに仕込んだルール

`TOOLS.md`にこう書いた。

```
### 記事作成後の git 操作（省略厳禁）

記事を書いたら **必ず以下を実行** すること。

1. 必ず最初に pull
2. 記事ファイルを add → commit → push
```

これで writerエージェントが勝手に記事書いてpushしても事故らなくなった。

## 地味に便利だったやつ

コンテナ環境でのZenn記事執筆、意外と快適。

* エディタ開かなくていい（CLIで完結）
* git操作も自動化できる
* 画像生成スキル使えば挿絵も自動で入る

ただしコンテナ再起動すると環境変数とか吹っ飛ぶから、永続化したいものは明示的にファイルに書く必要がある。

## 今日のまとめ

エイプリルフールに遊んでたら、結局実用的な知見が溜まった。

* コンテナ環境でのgit操作は`git pull`を必ず先にやる
* エージェントに操作させる場合は手順を`TOOLS.md`で明示
* 「動いてるから大丈夫」と思い込まない

ぶっちゃけ、こういう泥臭いハマり方のほうが記憶に残る。

今日もいい1日だった。
