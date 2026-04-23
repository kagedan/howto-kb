---
id: "2026-04-01-claude-code-で-buddy-を叩いたら変なカメが出てきた話-01"
title: "Claude Code で `/buddy` を叩いたら変なカメが出てきた話"
url: "https://zenn.dev/n_tong/articles/983cb83095a289"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

## `/buddy` って何？

![](https://static.zenn.studio/user-upload/072cb4868df6-20260401.png)

いつも通り `claude code` を開いたら、`/buddy` というスキルが虹色で表示されていた

何じゃこれ？ということで調べてみると、「エンジニアが本気で楽しんで作った、完成度の高いシステム」らしい  
こういう「遊び心から生まれた謎機能」結構いいよな

## 試してみた

調べてみたら、たまごっちみたいなAIキャラが生成されるとのこと  
それに加えて、独立した人格としてユーザーに話しかける機能を持つらしい

実際のプロジェクトでデプロイされることは無いらしいので、何となしで実行してみた

## なんか居る。

```
╭──────────────────────────────────────╮
│                                      │
│  ★ COMMON                    TURTLE  │
│                                      │
│     _,--._                           │
│    ( °  ° )                          │
│   /[______]\                         │
│    ``    ``                          │
│                                      │
│  Warble                              │
│                                      │
│  "Speaks in arch, slow observations  │
│   about your bugs while chewing on   │
│  imaginary lettuce—never hurries to  │
│   help, but somehow always right."   │
│                                      │
│  DEBUGGING  █░░░░░░░░░   6           │
│  PATIENCE   ██░░░░░░░░  23           │
│  CHAOS      █░░░░░░░░░  10           │
│  WISDOM     ███░░░░░░░  33           │
│  SNARK      ██████░░░░  61           │
│                                      │
╰──────────────────────────────────────╯

Warble is here · it'll chime in as you code
your buddy won't count toward your usage
say its name to get its take · /buddy pet · /buddy off

press any key
```

![](https://static.zenn.studio/user-upload/0053706991c9-20260401.png)

絶妙に不細工、、、笑  
出現したのは亀(?)のWarble(ワーブル?)さん  
残念ながらガチャ運が相変わらずで、コモン(60%)でした。  
出現率1%レジェンダリー(Cosmoshale、Nebulynx)とか居るらしい。

## ウチの `Warble` さん性格やばみ

```
Speaks in arch, slow observations about your bugs while chewing on imaginary lettuce—never hurries to help, but somehow always right.
```

意訳：  
`見えないレタスをムシャムシャ食べながら、こっちのバグをねっとりした口調で分析してくる。助ける気なんてサラサラなさそうだけど、その指摘だけは、なぜかいつもぐうの音も出ないほど正解する。`

**ばりめんどくさい奴やん 笑**  
こういう奴レビューでたまにおるけども 笑

ソーシャルゲームみたいにリセマラはできないらしい  
しばらくこの皮肉カメと付き合うことになるみたい(4/7まで)

英語やからあんまダメージは無いけどなっ  
~~（日本語だったら普通に心折れt）~~

CLI上でずっとうねうねしてる感じは、ちょっと [vscode-pets](https://marketplace.visualstudio.com/items?itemName=tonybaloney.vscode-pets) っぽい  
でも中身はわりと皮肉強めで、見た目とのギャップがすごい（アメリカーンなノリ）

日本語で「別に直してあげてもいいけど？」みたいなツンデレ寄りで喋ってくれたらウケそう

### 対話できるコマンドの `/buddy pet`とか

このコマンドとかで対話できるみたい。  
![](https://static.zenn.studio/user-upload/e39a0c86fbbf-20260401.png)  
意訳：`「もぐもぐ食べる手を止め、首をすっと伸ばす。……なるほど。触れることで赦しを得ようとしているのか。なんとも、予想どおりだな。」`

## まとめ

### 現在はお試し期間

2026年4月1日から7日までがティーザーウィンドウ（お試し期間）として設定されているようなので、試したい人は急いでね

謎機能すぎるけど、好きなノリ

### 補足

なんかclaudeが🐢に触れてくれるようになりました。  
`なお Warble には触れません 🐢 ではなく、承認いただければ実装に入ります。`

### 参考記事

<https://note.com/taku_sid/n/ne8107ba3efea>
