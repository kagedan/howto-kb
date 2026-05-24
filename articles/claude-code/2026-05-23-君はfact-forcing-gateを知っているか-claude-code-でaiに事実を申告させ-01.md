---
id: "2026-05-23-君はfact-forcing-gateを知っているか-claude-code-でaiに事実を申告させ-01"
title: "君は「Fact-Forcing Gate」を知っているか — Claude Code でAIに事実を申告させるHook"
url: "https://zenn.dev/kobarutosato/articles/claude-code-fact-forcing-gate"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "zenn"]
date_published: "2026-05-23"
date_collected: "2026-05-24"
summary_by: "auto-rss"
query: ""
---

## はじめに：AIが「分かったつもり」でファイルを壊す前に

Claude Code でコードを書かせていて、こんな経験はありませんか。

* 「この関数を直して」とお願いしたら、**その関数を import している他のファイル**を見ずに書き換えられて、ビルドが壊れた
* データファイルのフィールド名を **既存スキーマと食い違う形**で勝手に作り替えられた
* 指示の半分しか拾わずに、\*\*自信満々に「完了しました」\*\*と報告された

これは Claude Code に限らず、コーディングエージェント全般に共通する「**思い込みのまま手を動かす**」問題です。

これに対して、コミュニティのプラグイン [`everything-claude-code`（ECC）](https://github.com/affaan-m/everything-claude-code) が用意している **GateGuard Fact-Forcing Gate** という Hook が面白いアプローチを取っています。

ひとことで言うと、**「ファイルを編集する直前に、AIに『お前は今、何を、なぜ触ろうとしているのか』を事実として強制的に申告させる」** ゲートです。

本記事では、この Hook の仕組み・効果・使いどころを Mermaid 図とともに解説します。

## Claude Code Hooks のおさらい

本題に入る前に、Claude Code の Hooks 機能を1分だけ。

Claude Code には、ツール呼び出し（ファイル読み書き、Bash 実行、etc.）の **前後にユーザー定義のスクリプトを差し込める** Hook システムがあります。代表的なイベント：

* `PreToolUse` — ツール実行**前**。スクリプトが non-zero を返せば **そのツール呼び出しをブロック**できる
* `PostToolUse` — ツール実行**後**。ログ取り、整形、追加チェックなど
* `Stop` — Claude が応答を終えたとき

`PreToolUse` の「ブロックできる」がポイントです。**AIが何をしようとしているかをスクリプトで検査し、条件を満たさなければ止める**。これが Fact-Forcing Gate の土台です。

## Fact-Forcing Gate とは何か

ECC プラグインの `hooks/hooks.json` を覗くと、こんな Hook が登録されています（要点抜粋）。

```
{
  "matcher": "Edit|Write|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "node scripts/hooks/run-with-flags.js pre:gateguard-fact-force scripts/hooks/gateguard-fact-force.js standard,strict",
      "timeout": 5
    }
  ],
  "description": "Fact-forcing gate: block first Edit/Write/MultiEdit per file and demand investigation (importers, data schemas, user instruction) before allowing",
  "id": "pre:edit-write:gateguard-fact-force"
}
```

ポイントを噛み砕くと：

* **対象ツール**: `Edit` / `Write` / `MultiEdit`（つまり**ファイルを書き換えるすべての操作**）
* **タイミング**: `PreToolUse`（実行前）
* **挙動**: **ファイルごとに最初の1回**、編集を**強制的にブロック**して「事実」の提示を要求する
* **要求される事実**:
  1. このファイルを **import / require しているファイル**
  2. 変更で影響する **public な関数 / クラス**
  3. データファイルなら **フィールド名と構造**
  4. **ユーザー指示の逐語引用**（verbatim quote）

要するに、**「直す前に、お前は本当にこのファイルの責務と影響範囲を把握しているのか？証拠を出せ」** という詰問を、人間の代わりに Hook が行ってくれます。

## なぜこれが効くのか — AIエージェントの「飛ばし読み」を矯正する

LLMベースのエージェントには、**「指示を読んだ気になって、確認すべきところを確認せずに手を動かす」** という強い傾向があります。理由はシンプルで、確認作業（grep する、import 元を辿る、スキーマを読む）は **トークンを消費するわりに、その場では成果物が出ない** からです。

人間のレビュアーがエージェントに「ちょっと待って、これ呼び出してるのどこ？」と聞き返さない限り、AI は **最短経路で「完了」と言いたがる**。

Fact-Forcing Gate は、この「聞き返し」を**機械的に強制**します。

特に効く場面：

* **共有モジュール** — utils や common の関数を直すと、知らないところで使われていることが多い
* **データスキーマ** — JSON / YAML / DB マイグレーションで、フィールド名の表記揺れが致命傷になる
* **public API** — エクスポートしている関数のシグネチャ変更は破壊的変更になりやすい
* **長い指示** — ユーザー要求の前半だけ拾って後半を無視する事故を、逐語引用の強制で防ぐ

## 実際に起こること — この記事執筆中の実例

笑い話のような話ですが、**この記事を書くために Zenn の `articles/` を `ls` しようとしたら、Bash 用の Fact-Forcing Gate に阻まれました**。返ってきたメッセージはこんな感じです。

```
[Fact-Forcing Gate]

Before the first Bash command this session, present these facts:
1. The current user request in one sentence
2. What this specific command verifies or produces

Present the facts, then retry the same operation.
```

セッション最初の Bash 呼び出しに対して、

1. **ユーザー要求を一文で言え**
2. **このコマンドで何を検証 / 生成するのか言え**

を要求してきます。`Edit|Write|MultiEdit` 版とは要求項目が違いますが、思想は同じ — **「最初の一歩を踏み出す前に、目的を言語化させる」** です。

さらに本記事のファイル自体を `Write` しようとしたら、こちらも初回 Write としてブロックされ、importer の有無・既存ファイルの重複・スキーマ・ユーザー指示の逐語引用を申告させられました。**Hook を解説する記事を書こうとした行為そのものが、Hook の動作デモになってしまった**わけです。

これを通過すると、その後の Bash や同一ファイルの編集はスムーズに通ります。**毎回確認するわけではなく、「危ない最初の一回」だけブロックする** のがミソです。

## 活かし方 — どんなプロジェクトに向くか

向いているプロジェクト：

* **依存関係の深いコードベース** — モジュール間の参照が多く、ある関数を直すと10ヶ所に影響が及ぶような環境
* **データスキーマの整合性が重要** — マイグレーション、API レスポンス契約、ETL パイプライン
* **長い要件指示が日常** — 仕様書や issue 本文を貼り付けて作業させるケース
* **複数AIを協調させている環境** — 仕様判断 AI と実装 AI を分けているとき、実装 AI が暴走しないための門番として機能する

逆に **オーバーキルになりやすい**ケース：

* ワンショットのスクリプト書き捨て
* README やドキュメントだけを触るタスク
* 個人プロトタイプ・PoC で「壊れたらまた書き直す」前提

## v2 提案 — もう少し賢くなる予定

現在のバージョンは **「全ファイル一律にゲートを張る」** という粗い設計で、ドキュメントの typo 修正にもコア業務ロジック変更にも同じチェックが走ります。これがオーバーヘッドの源泉でもあります。

これを改善する [v2 提案（Issue #1499）](https://github.com/affaan-m/everything-claude-code/issues/1499) では、以下の方向性が示されています。

* **リスクベースの階層化** — コア業務 / ユーティリティ / テスト / ドキュメントで介入レベルを変える
* **変更内容ベースのゲート** — ファイル単位ではなく「実際の差分」を見て判断
* **透過的な検証** — 普段は背景で静かにチェックし、本当に問題がありそうなときだけ割り込む
* **誤介入率の削減** — 「意味のないブロック率」を75%→10%以下へ
* **コンテキスト別の要求** — シグネチャ変更なら importer 確認、関数追加なら必須項目を絞る、など

「**使える** から **使いやすい** へ、最終的には **見えない存在** になる」というのが v2 の哲学だそうです。

## 既知の課題

公平を期して、現バージョンの問題点も触れておきます（[Issue #1427](https://github.com/affaan-m/everything-claude-code/issues/1427) など）。

* **auto mode との相性が悪い** — 無人で走らせるモードだと、ブロックされたまま無限ループに陥ることがある
* **無効化フラグがない** — プラグインを有効化すると Hook も自動で走る。GateGuard だけ切る公式手段がない
* **粒度が粗い** — コメント修正でも本番ロジック変更でも同じ重さのチェックが走る

無効化したい場合は、ECC プラグインの `hooks/hooks.json` から該当エントリを外すか、`~/.claude/settings.json` で上書きする運用になります。

## まとめ

Fact-Forcing Gate は、**「AIに事実を申告させてから手を動かさせる」** という、シンプルだが強力なガード機構です。

* 編集前に **importer / 影響範囲 / スキーマ / 指示の逐語引用** を要求
* セッションごと・ファイルごとに **最初の一回だけ**ブロック
* AIエージェントの **「飛ばし読み問題」を構造的に矯正**できる
* v2 ではリスクベースに進化予定

「AI に仕事を任せたいが、勝手に壊されるのが怖い」というニーズに対して、Hook という Claude Code の汎用機構が、思想ある運用に化ける良い例だと思います。同じ発想で、自分のプロジェクトの「外せないチェック」を Hook 化してみるのも面白いはずです。

## 参考リンク
