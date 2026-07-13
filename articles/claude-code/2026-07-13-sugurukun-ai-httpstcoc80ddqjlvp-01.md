---
id: "2026-07-13-sugurukun-ai-httpstcoc80ddqjlvp-01"
title: "@SuguruKun_ai: https://t.co/c80dDQJLVP"
url: "https://x.com/SuguruKun_ai/status/2076494538227757156"
source: "x"
category: "claude-code"
tags: ["API", "AI-agent", "OpenAI", "GPT", "x"]
date_published: "2026-07-13"
date_collected: "2026-07-14"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/c80dDQJLVP

再告知ですが、この謎にコスパいいAI講座、今週日曜にやるのでぜひ！

今日まで早割で申し込み可能です！
https://t.co/B3tyN8sWyG


--- Article ---
OpenAIが2026年7月9日、GPT-5.6をChatGPT、Codex、OpenAI APIへ正式投入しました。CodexではSol、Terra、Lunaの3モデルに加えて、推論の深さをLowからUltraまで選べます。

ただ、モデルが賢くなっただけでCodexを使いこなせるわけではないんですよね。

Codexは、チャット欄にコードを書かせるだけのツールではありません。リポジトリを読み、ファイルを編集し、コマンドを実行し、画面を確認し、テストし、差分をレビューし、必要ならサブエージェントに仕事を分ける「実行するエージェント」です。

この記事では、インストールからGPT-5.6の選び方、AGENTS.md、Skills、Plugins、権限、レビュー、Ultraまで、保存してそのまま手順書として使える粒度でまとめます。2026年7月12日時点の公式情報と、Codex CLI v0.144.1で実際に確認した内容だけを書きます。

![](https://pbs.twimg.com/media/HNEwU_kaEAA8Pz7.jpg)

## 1. GPT-5.6対応で何が変わったのか

まず結論から言うと、GPT-5.6対応の本質は「一番賢いモデルが増えた」ことより、仕事の種類に合わせて3つの能力帯を選べるようになったことです。

- **GPT-5.6 Sol**: 複雑で曖昧な実装、設計、調査、セキュリティ、画面の仕上げまで必要な仕事向けです。迷ったらこれでいいです。
- **GPT-5.6 Terra**: 日常の実装、調査、修正、資料作成を回す実務の主力です。Solほどの深さがいらない仕事に向いてます。
- **GPT-5.6 Luna**: 抽出、分類、整形、定型チェックなど、完成条件が明確な大量処理向けです。
公式ドキュメントでは、Codexの標準Power設定は **gpt-5.6-sol** のMediumです。複雑さに応じてSmarter側へ上げ、速度を優先するならFaster側へ下げる。Lunaを明示したい時はAdvancedから選ぶ、という設計になっています。

API側の **gpt-5.6** はSolへのエイリアスです。Solは105万トークンのコンテキスト、最大12万8,000トークンの出力に対応し、API価格は100万トークンあたり入力5ドル、キャッシュ入力0.5ドル、出力30ドルです。長いリポジトリや大量資料を一度に扱える余裕は増えましたが、コンテキストが大きいことと、雑に全部入れてよいことは別です。

![](https://pbs.twimg.com/media/HNEwViqaYAAuMOt.jpg)

![](https://pbs.twimg.com/media/HNEwWPVaAAANtnk.jpg)

自分の場合、軽いファイル整理や定型抽出はLuna、普段の実装はTerra、仕様が曖昧な新機能や公開前レビューはSol、という切り分けが一番わかりやすいと思ってます。全部を最高設定にするより、仕事に合うモデルと深さを選んだ方が速いです。

## 2. Codexは「どこで使うか」で役割が変わる

Codexには、ChatGPTデスクトップアプリのCodexモード、CLI、IDE拡張、Web、Cloudという複数の入口があります。どれが正解というより、仕事の形で選ぶのが正です。

- **デスクトップアプリ**: 複数タスクを並行で進めたい時、スクリーンショットやドキュメントを見せたい時、成果物をプレビューしながら直したい時に向いてます。
- **CLI**: リポジトリの調査、実装、テスト、レビュー、スクリプトやCIへの組み込みに向いてます。実行ログが残るので、再現性が高いです。
- **IDE拡張**: 今開いているファイルや選択範囲をそのまま文脈にしたい時に速いです。小さな修正やコード理解に向いてます。
- **Web / Cloud**: ローカルPCから離れて長いタスクを回す、GitHub上の変更をレビューする、クラウド環境へ委譲する時に向いてます。
![](https://pbs.twimg.com/media/HNEwXiDboAAzNAk.jpg)

初心者が最初に覚えるなら、デスクトップアプリとCLIの2つで十分です。デスクトップアプリで「何を作るか」を相談し、CLIで「どのリポジトリにどう実装するか」を詰める。逆に、同じ仕
