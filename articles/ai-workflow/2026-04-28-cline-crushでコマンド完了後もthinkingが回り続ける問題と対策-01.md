---
id: "2026-04-28-cline-crushでコマンド完了後もthinkingが回り続ける問題と対策-01"
title: "Cline / Crushでコマンド完了後もThinkingが回り続ける問題と対策"
url: "https://zenn.dev/magur0/articles/0a8b323b080255"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-28"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

## はじめに

Cline や Crush などの AI コーディングエージェントを使っていると、次のような症状が出ることがあります。

* ターミナル上ではコマンドが完了している
* 出力も表示されている
* しかしエージェント側では `Thinking...` や `Waiting for tool response...` が回り続ける
* 次の操作に進まない

この症状は、一見すると「LLM が考え続けている」ように見えます。

しかし実際には、**モデルが長考しているのではなく、エージェントがコマンドの完了を正しく検知できていない**ケースがあります。

## 先に結論：現時点ではClineの方が安定させやすい

自分の環境では、同じような症状は Cline でも Crush でも発生しました。

ただし、運用上は **Cline の方が安定させやすい**と感じています。

理由は、Cline には terminal 実行まわりの設定があり、特に **Terminal Execution Mode を `Background Exec` に変更する**ことで、VS Code の terminal integration 由来の問題を回避しやすいためです。

一方で Crush は CLI ベースのツールなので、Cline の `Background Exec` のような「まずここを変える」という明確な逃げ道が少なく、長時間実行コマンド、background job、対話入力などを運用で避ける必要があります。

つまり、ざっくり言うと次のような整理です。

```
Cline:
  設定で回避しやすい
  Background Exec にすると安定しやすい

Crush:
  似た問題は起きる
  ただし運用で踏まないようにする必要がある
```

もちろん Cline でも完全に問題がなくなるわけではありません。  
ただ、少なくとも「コマンド完了後も Thinking が回り続ける」問題に対しては、Cline の方が対策を取りやすいです。

## 起きていること

通常、AI コーディングエージェントは次のような流れでコマンドを実行します。

```
AI がコマンドを提案
↓
ターミナルでコマンド実行
↓
コマンドの出力を取得
↓
終了状態を検知
↓
AI が次の判断に進む
```

ところが、何らかの理由で最後の

部分に失敗すると、実際にはコマンドが終わっていても、エージェント側は

だと判断し続けます。

その結果、画面上では `Thinking...` や `Waiting for tool response...` が回り続けます。

## これはAPIやモデルの問題ではないことが多い

この症状を見ると、最初は次のように疑いがちです。

```
社内APIが遅いのでは？
OpenAI Compatibleの応答が悪いのでは？
モデルがThinkingし続けているのでは？
```

しかし、ターミナル上でコマンド自体が完了している場合は、まず疑うべきはそこではありません。

疑うべきなのは、次です。

つまり、問題はモデルや API ではなく、**エージェントとターミナルの接続部分**にある可能性が高いです。

## Clineの場合

Cline は VS Code 拡張として動作します。

そのため、Cline がターミナルコマンドを実行するとき、VS Code の terminal / shell integration の影響を受けます。

ここで完了検知や出力取得がうまくいかないと、次のような状態になります。

```
ターミナルではコマンド完了
↓
しかしCline側には完了が伝わらない
↓
ClineがThinkingのまま止まる
```

特に、次のようなコマンドで起きやすいです。

* 長時間実行されるコマンド
* `npm run dev` などの常駐コマンド
* watcher 系コマンド
* 出力が多いコマンド
* pipe を多用するコマンド
* 対話入力を求めるコマンド

## Clineの対策

Cline でまず試すべき対策は、**Terminal Execution Mode を `Background Exec` に変更すること**です。

### 設定

Cline の Settings を開き、Terminal Settings で次のようにします。

```
Terminal Execution Mode: Background Exec
```

これは、VS Code のターミナル統合に依存せず、バックグラウンド実行に寄せる設定です。

Cline で「コマンドは終わっているのに Thinking が止まらない」場合、まずここを変更するのが一番効果的です。

## VS Code統合ターミナルを使う場合の追加対策

`Background Exec` にできない場合や、VS Code の統合ターミナルを使い続けたい場合は、次も確認します。

```
Default Terminal Profile: bash
Shell integration timeout: 10秒程度
Enable aggressive terminal reuse: OFF
```

WSL を使っている場合は、次のようにします。

```
WSL側で code . してVS Codeを開く
Default Terminal Profile: WSL Bash
Shell integration timeout: 15秒程度
```

特に Remote-SSH や WSL では、shell integration の完了検知が不安定になることがあります。

## Clineに実行させない方がよいコマンド

Cline に次のようなコマンドを直接実行させるのは避けた方がよいです。

```
npm run dev
python app.py
tail -f app.log
watch -n 1 command
some_command | grep keyword | head -30
```

これらは、終了しなかったり、出力の扱いが複雑になったりするため、Cline 側が待ち続ける原因になります。

代わりに、次のようにします。

```
timeout 30 npm run build
python -m pytest tests/test_xxx.py -q
some_command > /tmp/out.txt 2>&1
head -30 /tmp/out.txt
```

ポイントは、**短時間で終わるコマンドにすること**です。

## 開発サーバーは別ターミナルで起動する

`npm run dev` や `python app.py` のような開発サーバーは、Cline に起動させない方が安定します。

おすすめは次の運用です。

```
開発サーバー:
  自分で別ターミナルやtmuxで起動

Cline:
  ファイル編集
  ログ確認
  テスト実行
  ビルド確認
```

Cline に常駐プロセスを持たせると、終了判定が難しくなります。

## .clinerulesに書いておくとよい設定

毎回同じ問題を踏まないように、プロジェクトの `.clinerules` にルールを書いておくと便利です。

```
# Terminal execution safety

Avoid commands that can keep Cline waiting indefinitely.

- Prefer short, bounded, non-interactive commands.
- Do not run long-running foreground processes such as dev servers, watchers, or `tail -f`.
- For commands that may hang, use an explicit timeout.
- Avoid complex pipe chains when possible.
- If output may be large, redirect it to a temporary file first, then inspect the file with `head`, `tail`, or `grep`.
- Do not rely on interactive prompts. Authentication and setup should be completed outside Cline first.
```

日本語で書くなら、次でもよいです。

```
# コマンド実行ルール

Cline に長時間実行・常駐・対話入力が必要なコマンドを実行させない。

- dev server や watcher は Cline 上で起動しない
- コマンドは短時間で終了するものを優先する
- 必要に応じて timeout を付ける
- 出力が多い場合は一度ファイルに保存してから確認する
- 認証やパスワード入力は Cline の外で済ませる
```

## Crushの場合

Crush でも似た問題が起きます。

ただし、Crush は VS Code 拡張ではなく CLI ベースのツールです。

そのため、Cline のように VS Code shell integration が原因になるわけではありません。

Crush では、主に次のようなケースで止まりやすいです。

* `npm run dev` などの常駐コマンド
* background job
* `job_kill`
* 対話入力が必要な認証
* 出力が多い検索
* fork するプロセス

症状としては、次のようになります。

```
コマンドは動いたように見える
↓
しかしCrush側が Waiting for tool response... のまま戻らない
```

## Crushの対策

Crush では、Cline の `Background Exec` のような一発の設定より、運用で避けるのが重要です。

基本方針はこれです。

```
Crushには短時間・非対話・単発コマンドだけを実行させる
```

避けた方がよいコマンドは次です。

```
npm run dev
tail -f app.log
watch -n 1 command
```

代わりに、次のようなコマンドを使います。

```
npm run build
npm test
pytest -q
rg "keyword" src
```

また、GitHub 認証などは Crush の中でやらず、事前に外で済ませておきます。

## Crush用のルール例

Crush を使う場合も、ルールファイルに次を書いておくと安全です。

```
# Crush command safety

Avoid interactive commands and long-running foreground processes.

- Do not start dev servers, watch tasks, or persistent processes in the foreground.
- Prefer one-shot, bounded, non-interactive commands.
- Complete authentication outside Crush first.
- Do not rely on job_kill for persistent background jobs.
- For large searches, narrow the target directory.
```

## 実務での切り分け方

この問題が起きたら、次の順で確認します。

### 1. ターミナル上でコマンドは終わっているか

まず、普通のターミナル画面を見ます。

コマンドが完了していて、プロンプトが戻っているなら、コマンド自体は終わっています。

### 2. エージェント側だけが止まっているか

Cline や Crush の画面だけが `Thinking...` や `Waiting for tool response...` のままなら、完了検知の問題を疑います。

### 3. 同じコマンドを通常のterminalで実行する

通常の terminal で正常に終わるなら、コマンドそのものよりも agent 側の実行経路が怪しいです。

### 4. 長時間実行・対話・pipeを含んでいないか

次の要素があると詰まりやすくなります。

```
dev server
watcher
tail -f
対話入力
大量出力
複雑なpipe
background job
```

これらが含まれている場合は、コマンドを単発・短時間のものに変えます。

## まとめ

Cline や Crush で

```
コマンドは終わっているのにThinkingが回り続ける
```

場合、モデルが考え続けているとは限りません。

多くの場合、問題は次です。

```
エージェントがコマンドの完了を正しく検知できていない
```

Cline では、まず次を試します。

```
Terminal Execution Mode: Background Exec
```

さらに必要なら、次も設定します。

```
Default Terminal Profile: bash
Shell integration timeout: 10〜15秒
Enable aggressive terminal reuse: OFF
```

Crush では、次の運用が重要です。

```
長時間実行コマンドを避ける
対話入力を避ける
dev serverは別ターミナルで起動する
短時間で終わるコマンドだけを実行させる
```

自分の環境では、Cline は `Background Exec` などの設定でかなり安定させやすく、Crush はコマンド運用をかなり気をつける必要がある、という印象です。

AI エージェントを安定して使うには、モデルや API だけでなく、**ターミナル実行のさせ方**も重要です。
