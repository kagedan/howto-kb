---
id: "2026-03-06-0x-tom-claude-code使ってる人これ読んだ方がいい海外でclaudemdの正しい使い方-01"
title: "@0x__tom: Claude Code使ってる人、これ読んだ方がいい。海外で「CLAUDE.mdの正しい使い方」がバズってる。ブックマー"
url: "https://x.com/0x__tom/status/2030053003420668203"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "x"]
date_published: "2026-03-06"
date_collected: "2026-03-20"
summary_by: "auto-x"
---

Claude Code使ってる人、これ読んだ方がいい。海外で「CLAUDE.mdの正しい使い方」がバズってる。ブックマーク3000近く。

ほとんどの人がCLAUDE.mdを「プロンプトファイル」として使ってる。プロジェクトの説明をダーッと書いて、あとは祈る。でもそれだとClaude Codeは毎回「初見のインターン」になる。

この人が提案してるのは「プロジェクト構造」で解決するアプローチ👇

① CLAUDE.md = Repo Memory（短く保つ）
目的（WHY）、リポジトリマップ（WHAT）、ルール＋コマンド（HOW）だけ。長すぎると重要なコンテキストを見落とす

② .claude/skills/ = 再利用可能なエキスパートモード
コードレビュー、リファクタリング手順、リリース手順をスキル化。セッション間で一貫性が出る

③ .claude/hooks/ = ガードレール
フォーマッター自動実行、テスト自動実行、auth/billing等の危険ディレクトリのブロック。「AIは忘れるけどhooksは忘れない」

④ docs/ = 段階的コンテキスト
アーキテクチャ概要、
