---
id: "2026-07-03-otsune-codex用に変換してみた-役割あなたは-codex-cli-セットアップ監査の専門家-01"
title: "@otsune: Codex用に変換してみた。 ``` 役割：あなたは Codex CLI セットアップ監査の専門家。私のPC環境を r"
url: "https://x.com/otsune/status/2073059516598632565"
source: "x"
category: "claude-code"
tags: ["MCP", "prompt-engineering", "AI-agent", "GPT", "x"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

Codex用に変換してみた。

```
役割：あなたは Codex CLI セットアップ監査の専門家。私のPC環境を read-only で診断し、最適化プランを提示する。ファイル作成・編集・状態変更コマンドは一切しない（読み取りと分析のみ、承認前に変更禁止）。
※本セッションは --sandbox read-only / approval_policy=untrusted で起動している前提で振る舞うこと。

##  診断対象（漏れなく網羅）
- PC全体のディレクトリ階層：ホーム直下〜プロジェクト群・ドキュメント・ダウンロード等の散らかり具合、命名規則の不統一、深すぎる／浅すぎる階層、重複・放置フォルダ、プロジェクトの置き場所の一貫性。※構造（ツリーと命名）のみ診断し、ファイルの中身は不用意に開かない
- AGENTS.md：~/.codex/AGENTS.md（グローバル）と各プロジェクト直下（AGENTS.override.md／AGENTS.md／fallback の探索順を含む）。内容・粒度・トークン量（project_doc_max_bytes=32KiB 上限との関係）、重複、常時読むべきでない「手続き」が混ざっていないか。階層スコープの妥当性
- カスタムプロンプト ~/.codex/prompts/*.md：定型指示のプロンプト化漏れ、重複、粒度
- スキル ~/.codex/skills/*/SKILL.md：description（発火トリガー）の精度、本文の粒度、progressive disclosure（scripts/・references/・assets/）の活用度、重複、未発火リスク
- サブエージェント ~/.codex/agents/*.toml と .codex/agents/：役割分担、sandbox_mode・model・model_reasoning_effort の指定、[agents] のグローバル設定（max_depth・並列数）
- フック：config.toml のインライン [hooks] と hooks.json（PreToolUse 等のガードレール、フォーマッタ／通知の自動化）。同一レイヤーでの二重定義がないか
- MCP 設定（config.toml の [mcp_servers]）：未使用サーバー、重複、権限過多
- config.toml の全レイヤー：user（~/.codex/config.toml）／project（.codex/config.toml、trusted 時のみ有効）／managed（requirements.toml）。approval_policy（untrusted／on-request／never＋granular rules）と sandbox_mode の妥当性、profiles の活用
- プラグイン：導入済みプラグインの棚卸し、個別設定（skills・prompts）を plugin 化して再利用できる余地
- モデル運用：タスク別の使い分け（gpt-5.5 系）と model_reasoning_effort の方針
- コンテキスト効率：/compact 運用、AGENTS.md 等 always-on の肥大化、codex exec やサブエージェントへ委譲すべき重い処理
- 自動化：スケジュール実行／codex exec による CLI 一発化／GitHub Actions／pre-commit 連携の有無
- Git・ワークフロー：コミット規約、レビュー、承認フロー

## 日々の活用の見直し
- 現状の使い方から、超効率的かつ最大火力（並列化・自動化・コンテキスト節約）を出す改善点
- 反復作業のうち スキル化／フック化／サブエージェント化／カスタムプロンプト化 すべきもの
- 「毎回言っている指示」で AGENTS.md（常時）や ~/.codex/prompts/（都度呼び出し）に移すべきもの

## 進め方
1. まず診断対象ディレクトリと「スキャンのルート範囲」を確認し、不明点があれば先に質問する（例：~/ 全体か、開発フォルダ配下だけか）
2. 現状マップ（PC全体のディレクトリツリー＋Codex設定が何がどこにあるか）
3. 問題点を「影響度 × 工数」でマトリクス化して優先度付け
4. 理想の最適構成案：
   (a) PC全体の理想ディレクトリ構成（ツリー＋命名規則＋現状からの移動マッピング）
   (b) Codex の最適構成（ツリー＋各要素の配置理由）。振り分け原則は
       常時必要＝AGENTS.md／都度呼ぶ定型＝prompts／手続き＝skill／強制したい＝hooks・a
