---
id: "2026-05-12-potatobiz1-claude-codeでcodexを超楽に呼び出す方法をもう一個見つけた危うく-01"
title: "@potatobiz1: Claude CodeでCodexを超楽に呼び出す方法をもう一個見つけた！危うく知らずに機会損失するところだった… こ"
url: "https://x.com/potatobiz1/status/2054113112761262533"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "GPT", "x"]
date_published: "2026-05-12"
date_collected: "2026-05-13"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

Claude CodeでCodexを超楽に呼び出す方法をもう一個見つけた！危うく知らずに機会損失するところだった…

これをやれば、
✅言葉一つですぐにCodexを呼び出せる
✅チャット内でAIが互いにレビューし合い、品質アップ
✅1人のAI相談からチーム運用に変わり自動化効率UP

順に説明する↓ブクマ推奨

今回紹介するのは、AI同士をつなぐMCP（Model Context Protocol）という仕組み。

ざっくり言うと片方のAIから、もう片方のAIを直接呼べる窓口。

Claude CodeにCodexのMCPを刺すと、Claude側で作業しながら「これCodexにも聞いて」が1コマンドで通る。

つまり人力で画面切り替える必要がなくなる。

実際に試してみた↓

Claude Codeで構成案を作る→「議論して」と打つ→裏でCodexが呼ばれて反対意見と別案を返す→Claude側で統合。

ここまで全部1画面で完結する。

以前は2つのAIで答え合わせに15分かかってた作業が、今は3分。判断の質と速さが両方上がり、自動化がさらに効率的になった。

使い方の具体例↓

X投稿の構成案をClaude Codeに作らせる。

「全体の構造は最適か、わかりやすいか、内容に間違いはないか、Codexに聞いて」と一言添えるだけで、別の頭から反対意見が返ってくる。

1人で書いてた時の「これでいいかな…」の不安が消える。頼れる編集者がもう1人増えた感覚に近い。

料金について↓

ChatGPTのPlusプラン以上に月額課金してる人は、サブスクの範囲内で動くから追加料金0円で使える。

未契約の人はAPIキー方式になって、作業の規模によって従量課金が発生する。

ChatGPT Plusプランは3000円。迷う時間がもったいない人は、さっさと課金して触った方が早い。

具体的なやり方↓

Claude Codeデスクトップアプリ / CLI / VS Code拡張 、どれを使っててもやることは3つだけ。

・Codex CLI をインストール
・codex login でChatGPTアカウントログイン
・Claude Code に Codex を MCP として登録

これだけで、Claude側から「Codexに聞いて」が動くようになる。

一番楽に設定する方法↓

以下の指示をClaude Codeのチャットに貼り付けて、聞きながら進めればOK↓

───

Claude Code に Codex CLI を MCP として連携させたい。

ゴール： 「Codexに聞いて」と指示したら Codex が呼ばれる状態。

手順：
1. Codex CLI をインストール
2. codex login で ChatGPT 認証
3. claude mcp add で MCP 登録
4. /mcp で connected を確認

私の OS と環境を確認した上で、1ステップずつ案内してください。エラーが出たら一緒に解決してください。

───

最後に↓

AIはあくまで効率化の手段。一番大事なのは「どうやって自動収入を作っていくか」のマネタイズ設計。

10時間で1000円しか稼げない仕組みを、いくらAIで3時間に短縮しても微妙。どうせならほぼ稼働0で日給3万。

俺はAIでコスパ良く自動収入を作っていくので、ブクマ・フォローよろしく！🍟
