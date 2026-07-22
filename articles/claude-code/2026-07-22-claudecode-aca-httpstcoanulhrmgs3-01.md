---
id: "2026-07-22-claudecode-aca-httpstcoanulhrmgs3-01"
title: "@ClaudeCode_aca: https://t.co/anULHrmGS3"
url: "https://x.com/ClaudeCode_aca/status/2079900404062752863"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "x"]
date_published: "2026-07-22"
date_collected: "2026-07-23"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/anULHrmGS3


--- Article ---
Claude Codeアカデミアです。

2,000時間以上Claude Codeを使い込んだガチ勢が集まって運営しています。

営業しなくても「教えてほしい」と依頼が絶えません。

![](https://pbs.twimg.com/media/HN1Jh8LaoAAqtx5.jpg)

Claude Codeを極めたい方は、フォロー (@ClaudeCode_aca )しておいてください。

[無料公式LINEはこちら](https://utage-system.com/line/open/wcoIZQB0rwv3?mtid=1U5McDifKcjO)

CLAUDE.mdにルールを書いた。なのに無視される。何回書いても抜けるんですよ。

CLAUDE.mdは「お願い」です。 だから忘れる。これが現実です。

**100%守らせたいなら、Hooks（自動で動くスクリプト）を使ってください。**

僕らが2,000時間かけて見つけた「本当に使える5パターン」を全部出します。 コピペだけで、作業が勝手に回り出します。

# ■ CLAUDE.mdに書いたルールが"無視"される——Hooksなら100%強制できる

![](https://pbs.twimg.com/media/HN1JjM0awAENQ3T.jpg)

2,000時間使い込んだ僕らが断言します。 **CLAUDE.mdだけじゃ足りません。**

便利なのは間違いない。 でも「従ってくれる」と「100%実行される」は全然違います。

## ▍ 「Prettierを使え」と書いても忘れられる現実

僕もCLAUDE.mdにこう書いてました。

> ファイルを編集したら、必ずPrettierでフォーマットしてください。

最初の数回は守ってくれます。 でもタスクが複雑になると——忘れます。

これ、CLAUDE.mdの構造的な限界なんです。

- セッション開始時に1回読み込まれるだけ
- ツール実行のたびにチェックされない
- 会話が長くなると優先順位が下がる
**「忘れる」のは仕様です。** 仕様だから、仕組みで対処するしかない。

## ▍ Hooksは"お願い"じゃなく"強制"——実行保証率100%

Hooksは特定のイベントにスクリプトを自動実行させる仕組みです。 **僕はこの違いが全てだと思ってます。**

```
CLAUDE.md → 「こうしてね」（お願い）→ 忘れることがある
Hooks     → 「こうする」 （強制）  → 100%実行される
```

> 「AIの判断に委ねる」のがCLAUDE.md。「仕組みで強制する」のがHooks。

この違いを知るだけで、使い方が一段変わります。

> 👉 Claude Codeを極めたい方は、@ClaudeCode_aca をフォロー！ 👉 [無料公式LINEはこちら](https://utage-system.com/line/open/wcoIZQB0rwv3?mtid=1U5McDifKcjO)

# ■ 3分でわかるHooksの全体像——27イベント×5タイプを一気に整理する

![](https://pbs.twimg.com/media/HN1JkKEacAAR-kW.jpg)

Hooksには27個のイベントがあります。 「多すぎない？」と思いますよね。

**僕らは27個を全部試しました。** その上で、"本当に使える5つ"に絞りました。 全部覚える必要はありません。

## ▍ 押さえるのは3グループだけ——セッション・ターン・ツール

27個は3グループに分かれます。

- **セッション系（3個）**: 起動・終了時に動く
- **ターン系（6個）**: メッセージのやり取りごとに動く
- **ツール系（6個）**: ファイル編集やコマンド実行の前後に動く
- 残り12個は上級者向け。最初は無視してOK
**僕のおすすめは「ツール系」から入ること。** 今回の5パターンのうち4つがツール系です。

## ▍ settings.jsonに書くだけ——プログラミング不要

設定はsettings.json（設定ファイル）に書くだけ。 僕が最初に覚えた場所はこれです。

- .claude/settings.json — チーム共有用
- .claude/settings.local.json — 自分だけの設定用
**コピペで終わります。** 難しいことは何もありません。

> 👉 Claude Codeを極めたい方は、@ClaudeCode_aca をフォロー！ 👉 [無料公式LINEはこちら
