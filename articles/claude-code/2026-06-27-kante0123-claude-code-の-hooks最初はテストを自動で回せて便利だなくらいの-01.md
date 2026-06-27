---
id: "2026-06-27-kante0123-claude-code-の-hooks最初はテストを自動で回せて便利だなくらいの-01"
title: "@kante0123: Claude Code の hooks、最初は「テストを自動で回せて便利だな」くらいの認識でした。それが PostToo"
url: "https://x.com/kante0123/status/2070880196077433256"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "x"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Code の hooks、最初は「テストを自動で回せて便利だな」くらいの認識でした。それが PostToolUse と Stop に自分の業務処理を挿し始めてから一気に化けます。

うちでやってるのは Stop フックに日報生成を噛ませる構成です。その日の作業を一通り終えてセッションが止まると Stop が走って、git log と変更ファイルの diff をまとめて別プロセスの Codex に投げ、日報のドラフトを Slack に流す。自分は何も叩いてません。エディタを閉じた瞬間に日報が勝手にできてます。

ハマったのは Stop フックの無限ループです ⚙️ Stop の中でまた Claude を呼ぶ書き方にしてたら、その子プロセスの Stop がまた発火して延々回り続けました。API代が一晩で跳ねて朝青ざめます。対策は単純で、フックから呼ぶのは本体じゃなく外部の軽いスクリプト(Codex CLI なり素のAPI叩き)にして、フック内からセッションを再起動しない。あと環境変数でフラグを立てて二重発火をガードしてます。

PostToolUse の方は、ファイル書き込みのたびに lint と型チェックを走らせて、落ちたら exit code 2 で Claude に差し戻す使い方が地味に効きます。Claude が自分で直しにいくので、自分がレビューに回す前段がかなり減りました。

結局 hooks って「AIに作業させる」から「AIが止まった/動いたタイミングに自分の業務フローを接続する」発想に変える装置なんだと思ってます。ここまで来ると、自分の仕事は処理を書くことじゃなくて、どのイベントに何を繋ぐかの設計だけになってきた感覚があります。
