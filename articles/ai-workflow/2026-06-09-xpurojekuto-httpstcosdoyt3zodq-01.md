---
id: "2026-06-09-xpurojekuto-httpstcosdoyt3zodq-01"
title: "@xpurojekuto: https://t.co/SDOyt3ZOdq"
url: "https://x.com/xpurojekuto/status/2064368978793992569"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "x"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

https://t.co/SDOyt3ZOdq


--- Article ---
Codexを使っていて、こんな状態になっていませんか？

毎回フルアクセスで雑に走らせて、たまにヒヤッとしている。 TUIに話しかけるだけで終わり、自動化には一切組み込めていない。 同じ前提を毎回タイプし直していて、AGENTS.mdを書いていない。 会話が長くなると、途中から精度がスーッと落ちていく。

Goal modeやAppshotsみたいな派手な機能は、みんな話題にします。

でも、実際に周りと差がつくのは、そこではありません。「同じCodexを、どう設計して使うか」という地味な使い方のほうです。そして、その多くはとっくにCLIに入っているのに、9割の人が使いこなせていません。

本記事では、実際に差がつく使い方だけを、一次情報をもとに8つ整理します。

それでは行きましょう。

## 1. AGENTS.md ── 毎回の指示を、一度書けば効く資産に変える

最初は、いちばん効くのにいちばん軽視されている AGENTS.md です。

プロジェクト直下に置く AGENTS.md は、ビルドコマンド、テスト設定、コーディング規約、守ってほしいルールを書いておくファイルです。Codexはタスク完了前に、ここに書かれたテストを実行するよう学習しています。

毎回「テストはこう走らせて」「この規約に従って」と打ち直している人と、一度書いて全工程に効かせている人。同じCodexでも、積み上がる差は日に日に開いていきます。

しかも AGENTS.md はCodexだけでなく、Cursorなど他のツールでも読まれる共通仕様です。一度書けば、ツールをまたいで効きます。

「毎回の口頭指示」が「一度書けば効く資産」に変わる。ここが出発点です。

## 2. 権限プロファイル ── --full-auto は、もう卒業していい

次に、安全性と速度のバランスを握る権限プロファイルです。

かつての --full-auto は非推奨になりました。今は --profile と --sandbox を組み合わせて権限を細かく制御します(v0.133で管理可能な正式機能に格上げ)。config.toml に用途別のプロファイルをいくつでも宣言でき、--profile dev のように明示して切り替えます。

codex --profile dev "implement the new endpoint"

「全自動か手動か」の2択だと、つい全権限を雑に渡してしまいます。プロファイルを使えば、「速いが危険」と「安全だが遅い」の間を、自分で設計できます。長時間タスクを任せる人ほど、ここを詰めるべきです。

## 3. サンドボックスモード ── 事故の被害範囲を、先に絞る

権限とセットで効くのが、サンドボックスの使い分けです。

実務では、おおむね二つの形に落ち着きます。開発やCIでは workspace-write、本番で動かす自動エージェントには read-only。危険な全アクセスは、使い捨てコンテナの中の特定バッチだけに限定する。

codex exec --sandbox workspace-write "run tests and fix failures"

特定のディレクトリにだけ書き込ませたいときは、全アクセスに手を伸ばす前に --add-dir で範囲を絞ります。AIはファイルを消すことも、危ないパッケージを入れることもあります。だからこそ、被害の範囲を先に小さくしておく。これが本番でCodexを回す人の発想です。

## 4. codex exec ── Codexを「対話相手」から「部品」に変える

ここから一段、自動化寄りの話です。

codex exec(エイリアスは codex e)は、Codexを非対話で実行するコマンドです。TUIを開かず、標準入力からプロンプトを渡し、結果を標準出力やファイルに流せます。

codex exec "write a CHANGELOG entry for the commits since v2.4.0 and append it to CHANGELOG.md"
codex exec -o docs/api.md "generate API documentation from the source code"

これをシェルスクリプトと組み合わせると、changelog更新、issueの仕分け、PR前のチェックを丸ごと自動化できます。codex exec を使えるようになると、Codexは「話しかける相手」から「パイプラインに組み込む部品」に変わります。

## 5. MCP連携 ── 単体
