---
id: "2026-03-27-claude-computer-use-が来た-ai-がデスクトップを操作する時代に何が変わるのか-01"
title: "Claude Computer Use が来た — AI がデスクトップを操作する時代に何が変わるのか"
url: "https://zenn.dev/zenchaine/articles/claude-computer-use-dispatch-cowork"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## Claude Computer Use とは何か？

2026年3月24日、Anthropic は Claude に **Computer Use** 機能を正式追加しました。AI がユーザーの macOS デスクトップ上でアプリを操作し、ブラウザを動かし、ファイルを整理する——Pro / Max プラン契約者向けのリサーチプレビューとして提供されています。

## コネクタ優先アーキテクチャをどう理解すべきか？

Computer Use の最も重要な設計は、操作手段の優先順位です。

```
1. コネクタ（API 連携） → 最も高速・正確
2. ブラウザ操作         → コネクタがない場合
3. デスクトップアプリ操作 → 最終手段
```

Claude はタスクを受けると、まず Slack / Gmail / Google Drive 等のコネクタの有無を確認します。コネクタがあればそちらを使い、なければブラウザの Web 版を操作します。「Computer Use = 万能デスクトップ自動化」ではなく、**API 連携できない部分だけ画面操作にフォールバックする**設計です。

## Dispatch — スマホからデスクトップを操作するには？

Dispatch は Computer Use をリモートから指示できる機能です。スマホの Claude アプリから指示を出すと、自宅の macOS デスクトップ上で Claude が作業を実行します。

```
移動中にスマホから:
「昨日の Slack の議論をまとめて Google Docs にブリーフィングを作って」
→ 自宅の Mac で Claude が自律実行
```

## セキュリティ設計はどうなっているのか？

* **アプリ単位の許可制**: 新しいアプリへのアクセスは必ずユーザーの許可が必要です
* **ブロックリスト**: 証券取引・暗号資産アプリはデフォルトでブロックされています
* **画面の可視性**: 操作内容はリアルタイムで画面に表示されます

「デフォルトで制限し、ユーザーが明示的に許可する」というオプトイン方式です。

## Claude Code との関係は？

Computer Use は Cowork だけでなく Claude Code でも利用可能です。これにより Claude Code は「コードを書く」だけでなく、ブラウザでプレビュー確認、GUI テスト、スクリーンショット撮影といったコーディング以外のタスクも自律的に実行できるようになります。

## 現時点での制限

* macOS のみ（Windows x64 は今後対応予定）
* Pro / Max プラン限定
* PC が起動・アプリが実行中である必要があります
* ミスの可能性があるため、重要な操作は人間の確認を推奨

## まとめ

Claude Computer Use は AI エージェントの能力を「テキスト生成」から「コンピュータ操作」に拡張しました。ただしリサーチプレビュー段階であり、「Trust, but verify」の姿勢が重要です。

## 参考ソース

---

この記事で紹介した内容の詳細な解説は、[ZenChAIne の記事](https://zench-aine.io/media/claude-computer-use-dispatch-cowork)で公開しています。
