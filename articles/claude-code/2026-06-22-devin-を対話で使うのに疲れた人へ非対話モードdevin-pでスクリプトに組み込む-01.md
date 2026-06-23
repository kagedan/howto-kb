---
id: "2026-06-22-devin-を対話で使うのに疲れた人へ非対話モードdevin-pでスクリプトに組み込む-01"
title: "`devin` を対話で使うのに疲れた人へ：非対話モード（`devin -p`）でスクリプトに組み込む"
url: "https://zenn.dev/asix/articles/255d95eb2bdbc0"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

[前回の記事](https://qiita.com/startdevin/items/7f63f167b23dc0e38241)では、Devin for Terminal（`devin` コマンド）の機能をClaude Codeと並べて紹介しました。Skills、Subagents、Hooks、`/handoff`——ターミナルに座って**対話しながら**使う前提の話が中心でした。

ただ、しばらく使っていて思ったんです。「これ、毎回ターミナルに張り付いて会話するのは、定型作業だと逆に面倒では？」と。

たとえば「全ファイルのTODOコメントを拾って整理する」「変更点だけ要約させる」みたいな作業は、対話で1往復するより、**コマンド1発で結果だけ返してほしい**。Claude Codeに `claude -p` があるように、`devin` にも非対話モードがあります。

この記事では、`devin -p` を起点に、Devin for Terminalを**スクリプトや自動化に組み込む**使い方を、公式のコマンドリファレンス準拠で整理します。前回が「対話でどう使うか」なら、今回は「対話せずにどう回すか」の話です。

## 対話モードと非対話モードはどう違うか

まず全体像です。通常の `devin` は対話TUIを起動しますが、`--print`（`-p`）を付けると、応答を出力して即終了する非対話モードになります。

公式のコマンドリファレンスでは、`--print [PROMPT]` の説明はこうなっています。

> Print response and exit (non-interactive mode). Optionally accepts an inline prompt.

使い方はシンプルで、プロンプトを直接渡すか、`--` 区切りで渡します。

```
devin -p "list all TODO comments"
devin -p -- list all TODO comments
```

私が最初に試したのはまさにこの形でした。`-p` を付けるだけで、結果がそのままターミナルに出てプロンプトに戻ってくる。シェルスクリプトの一部として呼べる、というのが対話モードとの決定的な違いです。

> **ハマりどころ：フラグを挟むときは `--` で区切る**  
> `-p` のすぐ後ろにプロンプトを書く `devin -p "..."` は動きますが、`--permission-mode` などのフラグを**間に挟む**と、プロンプトが宙に浮いて `error: unexpected argument` になります。フラグを使うときは、プロンプトの前に `--` を置いてください。
>
> ```
> # NG: フラグの後ろに素のプロンプト → unexpected argument
> devin -p --permission-mode dangerous "fix the bug"
> # OK: プロンプトの前に -- を置く
> devin -p --permission-mode dangerous -- "fix the bug"
> ```

なお、本記事のコマンドは `devin 2026.5.x` で動作確認しています。フラグ名や取りうる値はバージョンで差が出ることがあるので、手元では `devin --help` で実際の表記を確認してください。

## プロンプトをファイルで管理する：`--prompt-file`

非対話で回し始めると、すぐに「毎回プロンプトを文字列で書くのは限界がある」と感じます。長い指示や、チームで共有したい指示は、ファイルに切り出したくなります。

そのための `--prompt-file <FILE>` が用意されています。

| フラグ | 説明（公式） |
| --- | --- |
| `--print [PROMPT]` / `-p` | Print response and exit (non-interactive mode) |
| `--prompt-file <FILE>` | Load the initial prompt from a file |
| `--model <MODEL>` | Set the AI model for this session |
| `--config <PATH>` | Configuration file path |

プロンプトをファイル化しておくと、Gitで履歴管理でき、レビューもできます。私は `prompts/` ディレクトリに定型タスクのプロンプトを置いて、`devin -p --prompt-file prompts/review.md` のように呼ぶ運用に落ち着きました。

`--model` を併用してモデルを固定できるのも、スクリプトでは地味に重要です。非対話で繰り返し回すなら、「今日はどのモデルだったか」で結果がブレないよう明示しておくほうが安心です。

## 確認プロンプトで止まらないようにする：`--permission-mode`

非対話モードで一番つまずくのが、**権限の確認プロンプト**です。対話なら「実行していい？」に「はい」と答えれば進みますが、非対話で人がいないと、そこで止まってしまいます。

そこで `--permission-mode` を合わせて指定します。コマンドリファレンスで指定できる値は次の3つです。

| 値 | 位置づけ |
| --- | --- |
| `auto`（デフォルト） | 読み取り系ツールを自動承認。書き込みやシェル実行は確認が入る |
| `dangerous` | すべてのツールコールを自動承認し、確認で止めない |

> 私の環境（`devin 2026.5.x`）で `devin --help` の `--permission-mode` 欄に表示された値は `auto`（既定）と `dangerous` の2つでした。ドキュメントやバージョンによっては `normal` / `bypass` という値が案内されることもあります。手元で使える値は `devin --help` で確認してください。

非対話で**書き込みまで**完走させたいなら、すべてを自動承認する `dangerous` を選びます。逆に**読み取りだけ**のタスクなら、デフォルトの `auto` のままでも確認で止まりません（実際、TODOコメントの要約のような読むだけの処理は `auto` のまま通ります）。

ただし、ここは正直に注意を書いておきます。`dangerous` は便利な反面、**ツールコールを無条件で通す**ので、信頼できるリポジトリ・信頼できるプロンプトでのみ使うべきです。なお公式ドキュメントでは、こうした自動承認モードであっても**管理者がTeam Settingsで設定した組織レベルの deny / ask ルールは上書きされない**（管理者による制御が常に優先される）とされています。エンタープライズで使う場合、この「個人の自動化は組織ポリシーを超えられない」という保証は安心材料です。

私は最初、面白がって何でも `dangerous` で回していましたが、よく考えると「自動承認で何でも実行する」というのは、それなりに腹を括る必要のある設定です。`--respect-workspace-trust` のようなワークスペース信頼の設定も合わせて、どこまで自動化するかは慎重に決めたほうがいいと感じています（`-p` の非対話モードでは、ワークスペース信頼はデフォルトで無効＝信頼しない側に倒れる、という点も覚えておくと安全です）。

なお、`--permission-mode` とは別に `--sandbox` フラグも実在します。`devin --help` によると、exec（シェル実行）系のプロセスをOSレベルで隔離する機能で、付与すると許可された Read / Write スコープをOSレベルで強制します（macOSのseatbelt、Linuxのbwrap+seccomp）。手元の版では Research Preview 扱いだったので、自動化に組み込む前に挙動を確認しておくと安心です。

## 結果を残す・続きをやる：`--export` と `--continue` / `--resume`

非対話で回すなら、「実行した証跡を残す」「途中から再開する」がほしくなります。ここも専用フラグがあります。

| フラグ | 説明（公式） |
| --- | --- |
| `--export [PATH]` | Export conversation to a file after each turn (ATIF format) |
| `--continue` / `-c` | Resume the most recent session in the current directory |
| `--resume <SESSION_ID>` / `-r` | Resume a specific session by ID |

`--export` は、各ターンのあとに会話をファイルへ書き出します。形式は公式で「ATIF format」と明記されています。CIのアーティファクトとして残しておけば、「Devinが何をやったか」を後から追えます。

> 注意：`--export` は**バージョンによっては未提供**です。実際、私の環境（`devin 2026.5.x`）では `devin --help` に `--export` が出てきませんでした。その場合は次のように、シェルのリダイレクトで出力を保存できます。
>
> ```
> devin -p "app.py の品質を5段階で評価して" | tee logs/review.txt
> ```

`--continue` / `--resume` は、複数ステップの作業を分割して回すときに効きます。1コマンド目で調査だけさせ、結果を確認してから2コマンド目で実装に進む、という分け方ができます。

ここで一点、正直なところを書いておきます。Claude Codeにあるような**構造化JSON出力のフラグ**は、私が確認した範囲のコマンドリファレンスには見当たりませんでした。機械的にパースしたい場合は、現状 `--export`（ATIF形式）の出力を利用するのが現実的だと思います。この点は今後のアップデートで変わる可能性があるので、最新のリファレンスを確認してください。

## スクリプト・CIに組み込む

ここまでのフラグを組み合わせると、シェルから定型タスクを回せます。たとえば、変更されたファイル群に対して順番にチェックをかけるイメージです。

```
# 認証状態を確認（CI実行前提）
devin auth status

# 変更ファイルごとにプロンプトを適用
# （フラグの後ろのプロンプトは -- で区切る。ログは tee で保存）
for f in $(git diff --name-only main); do
  devin -p --permission-mode dangerous \
    -- "Review $f for obvious bugs and summarize findings" \
    | tee "logs/${f//\//_}.txt"
done
```

認証まわりは `devin auth`（`login` / `logout` / `status`）のサブコマンドで扱います。CIで回すなら、事前に認証が通っている状態を `devin auth status` で確かめてから流すのが安全です。

## Skills と Rules を CLI から管理する

非対話運用と相性がいいのが、コンテキストをコマンドで管理できるサブコマンドです。`devin skills` と `devin rules` が用意されています。

| サブコマンド | 説明（公式） |
| --- | --- |
| `devin skills` | Manage agent skills (slash commands and agent-triggered context blobs) |
| `devin rules` | Manage agent rules (always-on context blobs) |
| `devin mcp` | Connect and log in to Model Context Protocol servers |
| `devin list` | List sessions in the current directory |

Rulesは「常時オンのコンテキスト」、Skillsは「スラッシュコマンドやエージェントが文脈で呼び出すコンテキスト」という位置づけです。これらをコマンドから管理できると、リポジトリのセットアップスクリプトの中で「このプロジェクトに必要なRulesを入れる」といった初期化まで自動化できます。

## エディタ連携：`devin acp`

最後に、非対話の延長として面白いのが `devin acp` です。

> Run Devin as an Agent Client Protocol (ACP) server over stdio

ACP（Agent Client Protocol）サーバーとしてstdio経由で起動できます。対応エディタやツールからDevinを「バックエンドのエージェント」として呼び出せる、という方向性です。`-p` がワンショットのスクリプト組み込みなら、`acp` は常駐させて他ツールから叩く統合、という棲み分けになります。

## 対話と非対話、どう使い分けるか

| シナリオ | 推奨 | 理由 |
| --- | --- | --- |
| 設計を相談しながら進める | 対話（`devin`） | 試行錯誤はTUIが向く |
| 同じチェックを多数のファイルに | 非対話（`devin -p`） | シェルでループできる |
| CIに組み込みたい | 非対話＋`| tee`（または `--export`） | 証跡を残せる |
| 多段の作業を分割 | `-p` ＋ `--continue` / `-r` | 段階的に再開できる |
| 他ツールから常駐で呼ぶ | `devin acp` | ACPサーバーとして統合 |

## おわりに

前回は「`devin` は対話CLIとしてClaude Codeと遜色ない」という話でした。今回それを一段進めて、「対話**しない**使い方」を掘ってみたわけですが、`-p`・`--prompt-file`・`--permission-mode`・`--export`・`--continue` という素直なフラグだけで、スクリプトやCIに十分組み込めることが分かりました。

一方で、構造化JSON出力のように「自動化前提のツール」として見たときにまだ揃っていない部分もあります。そこは `--export`（無ければ `| tee`）で出力を残しつつ、今後のアップデートに期待したいところです。

`devin` を「座って話す相手」だと思っている人は、一度 `devin -p "..."` を打ってみてください。**会話の往復なしで結果だけ返ってくる**あの感覚は、定型作業の景色をけっこう変えてくれます。

---

## 参考リンク
