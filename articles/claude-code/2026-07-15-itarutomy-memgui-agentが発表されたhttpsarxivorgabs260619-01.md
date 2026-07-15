---
id: "2026-07-15-itarutomy-memgui-agentが発表されたhttpsarxivorgabs260619-01"
title: "@itarutomy: MemGUI-Agentが発表された（https://arxiv[.]org/abs/2606.19926）。複数アプリ"
url: "https://x.com/itarutomy/status/2077417604902531088"
source: "x"
category: "claude-code"
tags: ["AI-agent", "x"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

MemGUI-Agentが発表された（https://arxiv[.]org/abs/2606.19926）。複数アプリをまたぐ長時間タスクを自律でこなすモバイルGUIエージェントの新設計。

「AP Newsのテクノロジーとビジネスセクションから3記事ずつ読み込み、Joplinノートにセクション別で要約を作成」。こういったリアルな長時間タスクで従来のエージェントは崩れる。原因はコンテキスト爆発（文脈情報の肥大化）にある。ReAct方式（推論と行動を交互に繰り返すプロンプト設計）は操作ログを受け身に積み上げ続けるため、ステップが増えるにつれて重要な情報が薄まっていく。Qwen3-VL-8Bはこのタスクで191ステップの末に失敗する。

提案するConAct（Context-as-Action）は「記憶の整理」をUIのタップ・スクロールと同列の「アクション」に格上げする。モデルが3種の情報フィールドを自ら取捨選択して管理する。圧縮済みアクション履歴（過去手順を要約して保持）、UI状態（商品名・価格・フォーム入力値などの重要な画面上の事実）、直近の操作記録（次の動作への引き継ぎ情報）。

MemGUI-8B-SFT（ConActのデータで追加学習した8Bモデル）は同タスクを140ステップで成功。MobileWorld（訓練データ外の別ベンチマーク）でも汎化を確認し、235Bの大型モデルでも改善。150ステップ時点でコンテキストを約1,500トークン削減できる。

訓練データMemGUI-3K（2,956軌跡・約6.4万ステップ）はオープンソース予定。
