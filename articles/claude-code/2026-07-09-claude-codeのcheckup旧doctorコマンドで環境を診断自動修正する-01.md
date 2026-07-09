---
id: "2026-07-09-claude-codeのcheckup旧doctorコマンドで環境を診断自動修正する-01"
title: "Claude Codeの/checkup(旧/doctor)コマンドで環境を診断・自動修正する"
url: "https://zenn.dev/shirochan/articles/a24092cfebefa0"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "zenn"]
date_published: "2026-07-09"
date_collected: "2026-07-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code を使っていると、「インストール直後」「アップデート後」、あるいは「なんとなく挙動がおかしい」ときに環境を確認したくなる場面があります。こうしたとき、これまでは起動画面の警告やエラーメッセージを頼りに手探りで直すことが多かったのではないでしょうか。

2026年7月8日リリースの **v2.1.205** で、この体験が変わりました。従来の `/doctor` が「診断するだけ」から **「診断して、その場で修正までできる」フルセットアップチェックアップ** に進化し、新しく `/checkup` というエイリアスが追加されました。

本記事では公式 changelog をベースに、`/checkup`（＝`/doctor`）が何をするコマンドなのかをまとめます。

## `/checkup` とは

公式 changelog（v2.1.205）の記述はシンプルです。

> `/doctor` is now a full setup checkup that can diagnose and fix issues; `/checkup` is its alias

つまり:

* **`/doctor` と `/checkup` は同じコマンド**（`/checkup` はエイリアス）
* 環境の\*\*診断（diagnose）**だけでなく、問題の**修正（fix）\*\*まで行える

`/doctor` という名前は「壊れたときに呼ぶ」印象が強かったのに対し、`/checkup`（健康診断）という名前は「定期的に流して環境を整える」という新しい使い方を意識したものと言えます。

| 項目 | 内容 |
| --- | --- |
| コマンド | `/checkup`（`/doctor` のエイリアス） |
| 導入バージョン | v2.1.205（2026年7月8日） |
| 役割 | 環境の診断 + 問題の自動修正 |

## 何を診断するのか

`/checkup` は Claude Code の環境全体を横断的にチェックします。主な対象は以下です。

* インストール状態（自動アップデートの可否など）
* 設定ファイル（settings、managed settings の不正エントリなど）
* MCP サーバーの接続・認証状態
* プラグイン／スキルの状態
* 権限（permissions）の設定

これらを実行時に実際にテストし、`/status`（現在の設定を表示するだけ）とは異なり、**能動的に失敗を検出して修正案を提示する**のが `/doctor` / `/checkup` の位置づけです。

## `/doctor` に集約された起動時警告

このコマンドが強化された背景には、「起動画面をシンプルに保ち、診断は `/doctor` に集約する」という一連の変更があります。changelog から確認できる流れは次のとおりです。

| バージョン | 変更内容（原文） |
| --- | --- |
| v2.1.153 | `claude doctor` now shows the result of your last update attempt / one-time notice when npm global install can't auto-update; `/doctor` lists the fixes |
| v2.1.162 | Removed the "claude command missing or broken" startup warnings — they now appear in `/doctor` and `/status` instead |
| v2.1.186 | 不正な `allowedMcpServers`/`deniedMcpServers` エントリは破棄され、`claude doctor` に警告が出る |
| v2.1.187 | Improved `/doctor` with consistent flat tree layout across all sections, clearer section status icons, and highlighted command names |
| v2.1.205 | `/doctor` is now a full setup checkup that can diagnose and fix issues; `/checkup` is its alias |

起動時にごちゃごちゃ警告を出すのをやめ、代わりに「気になったら `/doctor`（`/checkup`）を叩く」という導線に一本化されているのが分かります。

## UI：フラットツリー表示

v2.1.187 の改善により、診断結果はセクションごとに一貫したフラットツリー形式で表示されるようになりました。

* 全セクション共通のフラットツリーレイアウト
* セクションごとのステータスアイコン（正常／警告／エラーが一目で分かる）
* コマンド名のハイライト表示

数秒で診断レポートが出て、どこが問題かをステータスアイコンで把握できる、という体験です。

## `/checkup` が「修正」できること

公式 changelog の記述は「diagnose and fix issues」と簡潔ですが、具体的にどんな修正を行うかは、Claude Code 開発者の1人である Boris Cherny 氏（[@bcherny](https://x.com/bcherny/status/2074997570317779038)）の発表ポストで説明されています。`/checkup` が提案する修正項目は次のとおりです。

* 使われていないスキル / MCP / プラグインの整理（コンテキストの節約）
* ローカルの `CLAUDE.md` とリポジトリにコミットされた `CLAUDE.md` の重複排除
* 肥大化したルート `CLAUDE.md` を、ネストした `CLAUDE.md` やスキルへ分割
* 遅いフックの無効化
* Claude Code 本体の最新版へのアップデート
* auto モードをデフォルトで有効化
* 頻繁に拒否している読み取り専用コマンドの事前承認

このほかにもいくつかの機能が含まれています。いずれも「環境のパフォーマンスとコンテキスト効率を上げる」方向の提案で、まさに定期的な"健康診断"にふさわしい内容です。

そして重要なのが、**これらの変更を適用する前に必ず確認を求める**点です。`/checkup` が勝手に `CLAUDE.md` を書き換えたりプラグインを消したりすることはなく、何を変更するかはユーザーが確認したうえで実行されます。

## 使いどころ

* **インストール直後** — 初期セットアップが正しく完了しているか確認
* **アップデート後** — 破壊的変更や設定不整合の検出
* **挙動がおかしいとき** — MCP 接続エラーや権限設定の問題を切り分け
* **定期メンテナンス** — 使っていないプラグイン整理や `CLAUDE.md` の肥大化解消

トラブル時だけでなく、`/checkup` という名前どおり「定期的に走らせて環境を整える」使い方がおすすめです。

## まとめ

* `/checkup` は `/doctor` のエイリアスで、v2.1.205（2026年7月8日）から**診断＋修正**ができるフルセットアップチェックアップになった
* 起動時警告は `/doctor` / `/status` に集約され、UI もフラットツリー表示に改善された
* 使っていないプラグインの整理や `CLAUDE.md` の分割など、環境を軽く保つ提案も行う（変更前に必ず確認あり）

トラブルシューティングの最初の一手として、そして定期メンテナンスとして、`/checkup` を習慣にしておくと良さそうです。

## 参考
