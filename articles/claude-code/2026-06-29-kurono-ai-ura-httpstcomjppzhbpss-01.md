---
id: "2026-06-29-kurono-ai-ura-httpstcomjppzhbpss-01"
title: "@kurono_ai_ura: https://t.co/mjPPZHbpsS"
url: "https://x.com/kurono_ai_ura/status/2071505951052722394"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "TypeScript", "x"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/mjPPZHbpsS


--- Article ---
Claude Codeを使って、最初は感動した。「すごい、何でもできる」と思った。

でも使い続けていると、精度が落ちてくる。指示を無視される。同じミスを繰り返す。前はうまくいってたのに、最近なぜか微妙になった。

その原因、**AIの性能じゃありません。あなたの使い方が壊しています。**

AI×SNSでのマネタイズ7,000万。放置で月300万。Claude Code 約2,000時間使用。

僕がこの時間をかけて気づいた結論は1つ。**「使えば使うほどうまくなる」は完全に嘘。**

正しい使い方を知らない人は、使うほど生産性が下がっていく。

![](https://pbs.twimg.com/media/HL9pmPJaQAAiXwH.jpg)

> **AIエージェントでの稼ぎ方はこちら👇

[>> くろのの公式LIN**E](https://utage-system.com/line/open/29eSgDJcxiWv?mtid=YdgBFzRGGHTL)

今日は、2,000時間の中で僕自身も全部やらかした「やってはいけない使い方」を8つ紹介する。全部つぶせば、明日からClaude Codeの出力が別物に変わります。

# ■ CLAUDE.mdを「全部入り辞書」にしている — 200行超えた瞬間、AIはルールを無視し始める

「ルールを全部書いておけばAIが守ってくれる」。これ、完全に逆。

CLAUDE.mdは、Claude Codeが**毎回のメッセージで強制的に読み込む**ファイル。ここが巨大になるということは、**毎回の会話で使えるAIの脳の容量が減る**ということです。

## ▍ ルールが多いほど守られない。これがCLAUDE.mdのパラドックス

公式が推奨しているCLAUDE.mdのサイズは**200行以内**。

500行を超えると、重要なルールがノイズに埋もれる。1,000行を超えると、もはやClaudeはルールの半分を無視します。

僕も最初は全部書いていました。命名規則、ディレクトリ構造、テストの書き方、過去のミスの対策。気づいたら1,500行を超えていた。

**結果、何が起きたか。Claudeが一番守ってほしいルールを無視するようになりました。**

ルールを増やせば増やすほど、ルールが機能しなくなる。これがCLAUDE.mdの最大の罠です。

## ▍ 「このルールを消したらAIは間違えるか？」 — Noなら今すぐ消せ

CLAUDE.mdに書くべきものは限られています。

**書くべき情報:**

- Claudeが推測できないプロジェクト固有のBashコマンド
- 一般的でない命名規則やコードスタイル
- 「なぜこの構造になっているか」という意図（WHY）
- テスト実行方法
**書いてはいけない情報:**

- コードを読めばわかること（ディレクトリ構造の説明等）
- TypeScriptのベストプラクティス（Claudeは既に知っている）
- 長い説明やチュートリアル
- APIドキュメント（URLリンクで十分）
判断基準はシンプル。「このルールを削除したら、Claudeは間違えるか？」 Noなら削除してください。それだけで精度が上がる。

## ▍ 正解は「3層アーキテクチャ」 — 全部CLAUDE.mdに書くな

![](https://pbs.twimg.com/media/HL9pxSFbEAA6KV5.jpg)

CLAUDE.mdに全部入れるのではなく、**3つの層に分散させる。**

- **Layer 1（CLAUDE.md）**: 全セッションで常に読み込まれる。最重要ルールだけ。200行以内
- **Layer 2（.claude/rules/）**: 特定のファイルを触ったときだけ読み込まれる。パス指定で自動ロード
- **Layer 3（.claude/skills/）**: 明示的に呼び出したときだけ読み込まれる。複雑な手順書はここ
僕はこの構造に変えてから、**Claudeが指示を無視する頻度が体感で半分以下になった。** 常時ロードの情報を最小にすることで、AIの脳のリソースを実際のコード処理に回せるようになります。

> **AIエージェントでの稼ぎ方はこちら👇

[>> くろのの公式LIN**E](https://utage-system.com/line/open/29eSgDJcxiWv?mtid=YdgBFzRGGHTL)

## ■ MCPサーバーを「便利そう」で入れまくっている — 存在するだけでAIの脳を食い潰す

MCPサーバーは接続しているだ
