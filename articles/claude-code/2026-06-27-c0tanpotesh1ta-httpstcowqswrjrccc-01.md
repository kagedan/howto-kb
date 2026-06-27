---
id: "2026-06-27-c0tanpotesh1ta-httpstcowqswrjrccc-01"
title: "@c0tanpoTesh1ta: https://t.co/WqswrJrccC"
url: "https://x.com/c0tanpoTesh1ta/status/2070780765898702986"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "TypeScript", "x"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

https://t.co/WqswrJrccC


--- Article ---
今回は入門編なので、簡単に始められる基本部分を中心にしています。
詳細なループ設計は最後に少しだけ補いました。ご了承ください。

## Loop Engineeringって何？

簡単に言うと、Loop Engineering は 
「作業を1回のお願いで終わらせる」のではなく、
「作業・検証・修正・記録を回る仕組みとして設計する」
考え方です。

単発プロンプトでは、こうなりがちです。

「このコードを直して」

AIはそれっぽく直してくれます。
でも、本当に直ったかどうかは分かりません。

そこで、ループではこう考えます。

1. 現状を確認する
2. 直す
3. 自動チェックを走らせる
4. 失敗したら原因を読んでまた直す
5. 成功したら記録して終わる

つまり、AIに「直して」と頼むだけでなく、**どうなったら成功なのか**、**どうやって検証するのか**、**どこまで進んだかをどこに残すのか**まで決めます。

## 単発プロンプトの落とし穴例：

AIに「1ページのbriefを書いて」と頼むと、自信満々に書いてくれますが、出典リンクが偽物だったり、内容が実際のページと一致しないことがあります。
ループにすると「すべての主張に3つ以上の実在ソースがあり、リンクが開いて裏付けられる」条件で自分で検証・修正を繰り返します。

---

## 人間がループになるのをやめる

今までのやり方では、人間が毎回こう判断していました。

- 次に何をすべきか
- エラーが直ったか
- まだ続けるべきか
- どこまで終わったか
- 何を記録すべきか
でも、これらのうち一部は仕組みにできます。

たとえば lint（リント：コードの「文法ミス・書き方の揺れ・危なそうな書き方」を自動でチェックする仕組み）の修正なら、終了条件はかなり明確です。

npm run lint が成功すること
テスト修正なら、こうです。
npm test が成功すること
ビルド確認なら、こうです。
npm run build が成功すること

このように、**機械的に判定できる条件**がある作業は、ループに向いています。

---

## Claude Codeの場合：/goal と /loop の使い分け

Claude Codeを使う場合は、ループを動かすための代表的なコマンドとして、/goal と /loop があります。

名前が似ていますが、使いどころは違います。
※ 詳しくは、noteに追記してあります。

---

## ループを作る前に確認（4条件チェック）

1. 作業は週1回以上繰り返すか？
1. 自動検証（テスト/lint/build）ができるか？
1. エージェントが自分でコードを実行できる環境か？
1. 明確な終了条件はあるか？
すべて満たさない場合は普通のプロンプトで十分です。
## AGENTS.md / VISION.md / SKILL.md / STATE.md の使い分け

AI CLIエージェントに任せるときは、ファイルの役割を分けておくと扱いやすくなります。

おすすめはこの4つです。

AGENTS.md   : プロジェクト全体のルール
VISION.md   : 何を目指しているか
SKILL.md    : 特定作業の手順
STATE.md    : 現在の進行状況

## AGENTS.md

AGENTS.md は、AIエージェント向けのREADMEです。

ここには、プロジェクト全体で常に守ってほしいことを書きます。

```
# AGENTS.md

## Project overview

This is a TypeScript + React project.

## Commands

- Install: `npm install`
- Lint: `npm run lint`
- Test: `npm test`
- Build: `npm run build`

## Rules

- Prefer small, local changes.
- Do not introduce unrelated refactors.
- Do not leave `console.log`.
- Avoid `any` unless there is no safer local fix.

## Reporting

When finished, report:

- files changed
- commands run
- remaining risks
```

## VISION.md

VISION.m
