---
id: "2026-05-29-obsidianstudio9-httpstcocxepxsglct-01"
title: "@obsidianstudio9: https://t.co/cXEpXsglct"
url: "https://x.com/obsidianstudio9/status/2060161232360059022"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "OpenAI", "x"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/cXEpXsglct


--- Article ---
Obsidianに複数の脳を作ってる人は完全に時代遅れです。セカンドブレインを１つにして運用すると、コード生成・設計・改善の質が格段に上がります。今回は、海外で大バズしたの設計をもとに、**Claude Code・Codex・Obsidianを1つの共通ファイル領域で連携させる方法**を、ハマりどころ込みで解説します。**Claude Code と Codex、両方使っている人は必見です**

こんな悩み、ありませんか？

- Claude Code と Codex のどっち使うか、毎回迷う
- Obsidian の Vault が AI 連携で活かしきれていない
- スキルが増えすぎて把握できない
- MCP を入れすぎてコンテキストが重い
- 3ツールの設定がバラバラで二重メンテになる
これ、3ツールを「独立したツール」として扱っているから起きる現象です。

![](https://pbs.twimg.com/media/HJcprcCbcAAuNAG.jpg)

OpenAI 創設メンバーの Andrej Karpathy 氏が、自分の知識ベースを LLM Wiki として運用する設計を 2026 年 4 月に公開しました。GitHub Gist で 41,000 人以上にブクマされていて、彼はこう書いています。

*Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.*

Obsidian は IDE、LLM はプログラマー、wiki はコードベース。

この比喩を3ツール統合に応用するとこう読めます。Obsidian は「ノートを置く場所」ではなく「Claude と Codex が共有する作業環境」。Claude Code と Codex は「別々のツール」ではなく「同じ共通ファイル領域を読み書きする2人のプログラマー」。

今回はこの設計を、ステップバイステップで日本語解説します👇

## **なぜ今「共通ファイル」が必要なのか**

ここ数ヶ月、Claude Code と Codex CLI を併用する開発者が一気に増えました。

ある統計だと、Codex CLI の npm 月間ダウンロード数は 2025 年 4 月の 82,000 件から、2026 年 3 月には **14,530,000 件まで伸びて** います。

177倍。

公式統計では週間アクティブユーザーも 300 万人（年初比5倍）、月間で2億件超のリクエストを処理している。

一方で Claude Code 側も止まっていません。

JetBrains が 2026 年 4 月に発表した Developer Ecosystem Survey 2026 では、Claude Code の開発者満足度（CSAT）が **91%**、推奨度（NPS）が **+54** で業界最高水準。世界の開発者の 18%、米国・カナダだと 24% が業務で採用していて、過去 6 ヶ月で採用率が 6 倍に伸びています。

このトレンドの読み方を間違えると、二択思考に陥ります。

「Codex に乗り換えるべきか、Claude Code を継続するか」。

実はこの問いの立て方そのものが、3ツール時代の本質を見落としています。

正しい問いは「両方使う前提で、共通する設計はどこにあるか」のはず。

**3ツールを別物として扱うと何が起きるか**

Claude Code、Codex、Obsidian を「それぞれ独立したツール」として扱うと、3つの問題が同時進行で起こります。

1つ目は MCP の過剰投入によるコンテキスト消費爆発です。

ある実測ベンチマークでは、GitHub MCP 経由で開発タスクを回したケースで月額 $55.20 のコストがかかった一方、gh CLI 直叩きに置換したら **$3.20 まで下がりました**。

17倍のコスト差。

別の比較では Microsoft Graph MCP と mgc CLI でコンテキスト消費に **35倍の開き** が出ています。Playwright MCP のスナップショット1回分が 56KB（トークン換算）を食う一方、CLI ならファイルパスの参照だけで完結する。

![](https://pbs.twimg.com/media/HJcprb2bkAAOT91.jpg)

「便利だから」で MCP を入れ続けると、コンテキストウィンドウが MCP のメタデータで埋まって、肝心のコード文脈が押し出されていきます。

ある業界エンジニ
