---
id: "2026-04-17-今日のclaude-code-v21112-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.112 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/6a21a6b76828fc7529af"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

v2.1.112 はホットフィックス1件のみ。Auto modeでOpus 4.7が使えなかった可用性の不具合修正です。

## 今回の注目ポイント

1. **Auto mode + Opus 4.7の可用性修正** - 4時間前リリースの v2.1.111 で入った組み合わせの不具合を即日で潰したパッチ

---

## Auto modeでOpus 4.7が引けない問題を修正

対象読者: Maxプラン契約者でAuto modeを常用しているユーザー

1つ前の v2.1.111 で、Maxサブスクライバー向けのAuto modeがOpus 4.7を使うようになりました。xhighというeffort levelも追加され、Auto mode自体も `--enable-auto-mode` フラグなしで有効に。ユーザー側は何もせずにAuto modeからOpus 4.7が回ってくるはず、という設計でした。

ただ、この新ルートに可用性の不具合が紛れていたようです。v2.1.112 はChangelog上たった1行の修正。

```
Fixed Opus 4.7 availability issues in auto mode
```

具体的な症状は明示されていません。リリース間隔を見ると v2.1.111 から約4時間後の緊急リリースで、解禁直後の不具合を即日で潰した形です。

対処はアップデートのみ。

バージョン確認。

```
claude --version
# 2.1.112
```

Auto modeの有効化手順は v2.1.111 時点でシンプルになっています。設定ファイルや起動フラグでオンにしているMaxユーザーは、アップデートを当てたあとに普段通り走らせて Opus 4.7 に届いているか確認すれば問題ありません。

## その他の変更

今回は上記の1件のみ。

## まとめ

v2.1.112 は v2.1.111 で解禁された Auto mode + Opus 4.7 の組み合わせに入った可用性不具合を即日で潰すホットフィックスです。Maxユーザーはアップデートだけ当てておけば動作に影響はありません。
