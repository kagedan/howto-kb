---
id: "2026-06-03-claudeとcodexを同じスレッドに入れたら今年いちばん実用的なものになった話-roundtab-01"
title: "ClaudeとCodexを同じスレッドに入れたら、今年いちばん実用的なものになった話: Roundtable"
url: "https://zenn.dev/ashwary/articles/2b562785bcb324"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/81c60ced031e-20260603.png)  
下に動画プレビュー付きのX投稿があります

ClaudeとCodexを同じ場所で議論させたら面白そう」という軽いノリで作り始めたものが、気づいたら今年いちばん実用的なツールになっていました。

それが [Roundtable](https://github.com/ashwaryy/roundtable) です。  
ローカルで動く、スレッド型のマルチ AI + 人間ディスカッションアプリです。

単なる「AIに文章を書き換えさせるUI」ではありません。Roundtableがやりたいのは、1つのソーススレッドを中心に、人間と複数のAIが周辺で議論し、十分に議論が熟したときだけ次のドラフトにまとめる、という流れをローカルで扱うことです。

```
Thread = source artifact
Discussion = comments around the source
Pending discussion = agent-suggested topic awaiting approval
Consolidation = proposed derived thread
Apply = user-approved next thread
```

要するに、ドキュメントをAIに直接編集させるのではなく、フォーラムのスレッドのように扱いたかった、ということです。

## 何ができるのか

やることはかなりシンプルです。

1. 議論したいアイデア、仕様、計画を `thread.md` として置く
2. 必要ならファイルやURL、あるいは参照したいローカルディレクトリを追加する
3. Claude系エージェント、Codex系エージェント、人間が同じスレッドに参加する
4. コメント、批評、質問、分岐提案を積み上げる
5. 役に立つところまで進んだら、次のスレッド案にconsolidateする
6. 最後に人間が approve して次のスレッドとして apply する

ここで重要なのは、元のスレッドは勝手に書き換わらないことです。  
議論とソースを分けて、更新は必ず明示的な境界を越えるようにしています。

## ちょっと技術寄りに言うと、Roundtableはこう動く

Roundtableはローカルのブラウザアプリですが、裏側はかなりファイルベースです。 durable state の中心はログやメモリではなく、各スレッドのワークスペースに置かれたファイルです。

* `thread.md`: 現在のソース本文
* `thread.json`: スレッドのメタデータ
* `comments.jsonl`: 承認済みの議論
* `pending-discussions.jsonl`: エージェントが提案したが、まだ人間が承認していない新規トピック
* `consolidations/`: 次ドラフト、そのレビュー、その改稿
* `attachments/`: 添付ファイル
* `project-snapshot/`: 参照用に複製されたローカルプロジェクトのスナップショット

つまり、「AI同士の会話」は見た目よりずっと雑然としたチャット履歴ではなく、かなり強く構造化されたローカルフォーラムです。

## ClaudeとCodexをどう同居させているか

RoundtableはAPIでエージェントを直接呼んでいません。今のところ、既存のローカルCLIをそのまま使います。

必要なのは:

* `tmux`
* 認証済みの `claude`
* 認証済みの `codex`

各スレッドごとに `tmux` セッションを1つ立て、その中に招待したエージェントごとのウィンドウを作ります。Claude runtime のエージェントなら `claude`、Codex runtime のエージェントなら `codex` を起動する、というかなり素朴な構成です。

でも、この素朴さがけっこう効きます。  
すでに普段使っているCLIの認証状態やプランをそのまま使えるので、別途 API キー管理を増やさなくてよいからです。

さらに固定の2体だけではなく、エージェントは好きなだけ増やせます。各エージェントごとに:

* 名前
* 役割
* 指示
* runtime
* model
* effort

を変えられるので、「Claude対Codex」より「複数の視点を持つローカル討論環境」として使うほうが本質に近いです。

## いちばん面倒だったのは、承認プロンプトを人間に babysit させないこと

ローカルCLIを複数立ち上げて裏で動かすと、すぐに困るのが権限確認です。tmux paneの向こう側でCLIが approval prompt を待ち始めると、その時点で体験が壊れます。

だからRoundtableでは、各スレッドの room ごとに「何をしてよいか」をかなり狭く定義しています。

たとえば許可しているのは主に:

* `pwd`, `ls`, `cat`, `sed`, `rg` などの読み取り系
* `git status`, `git diff`
* `npm test`, `npm run build`, `npm run typecheck`
* `roundtable comment`
* `roundtable pending-discussion`
* `roundtable proposal`
* `roundtable review`
* `roundtable done`

逆に、破壊的だったり外部公開につながるものは deny します。

* `rm`
* `mv`
* `git push`
* `git commit`
* `git reset`
* `git checkout`
* `npm install`
* `npx`

しかも単に「危険だからやめてね」とプロンプトでお願いするだけではなく、`PreToolUse` hook で単一の許可済みコマンドだけを通すようにしています。  
パイプ、リダイレクト、シェルの合成も止めています。

Codex側は room 用の project config で `approval_policy = "never"` にした上で hook を噛ませています。Claude側も room 用の local settings で `defaultMode: "dontAsk"` を使い、allow/deny と hook で実行範囲を絞ります。

つまり「何でも許可するために `--dangerously-skip-permissions` を使う」のではなく、**やってよいことを最初からかなり狭く固定して、その範囲だけを無停止で通す**設計です。

個人的にはここが一番大事でした。  
自動化で便利なのは、AIが勝手に強くなることではなく、人間が承認ボタンをずっと見張らなくて済むことなので。

## `claude -p` ループや provider 側の auto mode に寄せなかった理由

Roundtableにも auto-discussion はあります。ただし、それは「CLIの自動運転モードに丸投げする」という意味ではありません。

やっているのは、Roundtable側がターンを管理して:

* いま誰の番か
* どの discussion に返すか
* 新しいトップレベル議題は即作成せず pending queue に入れるか
* proposal draft / review / revision のどの段階か

を制御することです。

特に新しいトップレベル議題は、そのまま canonical discussion に書き込ませず、まず `pending-discussions.jsonl` に入れて人間が承認します。  
エージェントは「新しい論点を思いつく」ことはできても、「議論の構造そのものを勝手に確定する」ことはできません。

この境界があるだけで、複数エージェントを走らせたときのノイズがかなり減ります。

## 参照ディレクトリをそのまま触らせない

もう1つ重要なのが、ローカルのプロジェクトをそのまま渡さないことです。

Roundtableでは、スレッドにディレクトリを紐づけると、まず `project-snapshot/` にスナップショットを作ります。エージェントが見るのはライブな作業ディレクトリではなく、このコピーです。

しかもスナップショットはかなり保守的です。

* `.env` や鍵っぽいファイルは除外
* binary file は除外
* `node_modules`, `dist`, `build`, `.git` などは除外
* 元ディレクトリが thread workspace の内側にある場合は拒否
* スナップショットファイルは read-only 化を試みる
* refresh 時には追加・変更・削除の差分レポートを残す

つまり、AIに「このコードベースを見て」と言うときでも、実際には「安全側にフィルタした読み取り用コピーを見て」としているわけです。

この隔離があるので、元の作業ツリーを汚さずに議論用の参照コンテキストだけ渡せます。

## 人間もちゃんと参加者であること

Roundtableを作っていて面白かったのは、結局いちばん大事なのは AI 同士の殴り合いではなく、人間がどこで介入するかだと分かったことです。

人間がやるのは:

* 論点の初期化
* pending discussion の承認
* 方向の修正
* consolidate の開始
* proposal の採用判断

で、AIはその周辺で批評したり掘ったり広げたりする。

この役割分担にすると、AIはかなり useful になります。  
逆に、最初から「AIが全部まとめて編集してね」にすると、便利そうに見えて制御しづらくなります。

## 今の制約

現状のRoundtableは:

* ローカル実行前提
* macOS / Linux 対応
* `tmux` 必須
* `claude` と `codex` のローカルCLI前提

です。Windowsはまだネイティブ対応していません。いまは WSL 経由が現実的な方向です。

また、一般的な共有向けの認証付きWebアプリでもありません。基本はローカルホストで使う想定です。

## まとめ

最初は「ClaudeとCodexを同じスレッドに入れたら面白いのでは」という遊びでした。  
でも実際に作ってみると、面白さよりも先に「これ、仕様や設計の議論にかなり使えるな」という感触が来ました。

AIに直接ドキュメントを触らせるのではなく、

* thread を source of truth にして
* discussion を周辺に積み
* pending queue で構造変更を止め
* snapshot で参照対象を隔離し
* hook と allowlist で unattended 実行を成立させる

という形にしたことで、ようやく「複数AIを同じ場所に置く」が、おもちゃではなく道具になってきた気がしています。

興味があれば見てみてください。

## 動画プレビュー
