---
id: "2026-06-19-oikon48-claude-codeの初心者向け良い記事が出てますね-概要-claude-code-01"
title: "@oikon48: Claude Codeの初心者向け良い記事が出てますね👀 【概要】 Claude Codeの振る舞いをカスタマイズす"
url: "https://x.com/oikon48/status/2067986260803645898"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "AI-agent", "x"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Codeの初心者向け良い記事が出てますね👀

【概要】

Claude Codeの振る舞いをカスタマイズするには、7つの手段があり、

1. いつコンテキストに読み込まれるか
2. 長いセッションでどう振る舞うか
3 どれくらい指示の従いやすさを持つか

が異なるため、どの指示をどこに置くべきかの判断基準を明確にすることが重要。

【7つの方法】

- CLAUDE.md :  
ビルドコマンド・ディレクトリ構成・コーディング規約・チームのルールなどを書く場所。
ルート直下のものはセッション開始時に常に読み込まれ、コンパクション後も再読込される。一方サブディレクトリ（例 `app/api/CLAUDE.md`）に置いたものは、そのフォルダ内のファイルを触ったときだけ読み込まれる。
コストが高く全員の全セッションでトークンを消費するため、200行以内に抑え、所有者を決めてコードと同様にレビューすることが推奨されている。

- Rules: 
`.claude/rules/` に置く、特定の制約や規約を定めるファイル。スコープなしだと常時読み込まれるが、`paths` フィールドを付けると特定パス（例 `src/api/**`）のファイルを触ったときだけ読み込める。

- Skills: 
`.claude/skills/` に置く手順書で、開始時には名前と説明だけ読み込まれ、スラッシュコマンド（例 `/code-review`）や自動マッチで呼び出されたときに本体が読み込まれる。
デプロイ手順やリリースチェックリストなど、手続き的なワークフローに向く。

- Subagents: 
`.claude/agents/` に置く、独立したタスク専用の補助アシスタント。独立したコンテキストウィンドウで動作し、メインの会話には最終結果（要約とメタデータ）だけが戻る。
ログ解析や依存関係監査など、中間結果でメイン会話を散らかしたくない作業に向く。

- Hooks:
ファイル編集・ツール呼び出し・セッション開始などのライフサイクルイベントで発火する、決定論的な制御手段。
Linterの自動実行、完了時のSlack通知、特定コマンドのブロックなどに使用する。

- Output styles: 
`.claude/output-styles/` に置き、システムプロンプトに直接注入されるため指示への従い度合いが最も高い手段。
ただしデフォルトのシステムプロンプト（ソフトウェアエンジニアとしての役割など）を置き換えてしまうため、慎重に使うべき。

- Appending the system prompt: 
`--append-system-prompt` フラグで、役割を置き換えずに追加だけ行う方法。
その起動時のみ有効で、トーンや出力形式の指定に向く。指示が多いほど従い度合いが下がる「逓減」がある点に注意。

【押さえておくべき判断のコツ】

CLAUDE.mdに「毎回Xしたら必ずYせよ」と書くなら、確実に動かしたいのでHookへ。

「絶対にこれをするな」と書くなら、プロンプトの指示は長時間セッションやプロンプトインジェクションで破られうるため、決定論的に強制できるHookや権限設定（managed settings）へ。

30行の手順を書くなら、Skillsへ。

`src/api/` だけに効くルールなら、`paths` 付きの Rules へ。

個人の好みはプロジェクト共有ファイルではなく、ユーザーレベルのローカルファイルへ

---

Steering Claude Code: CLAUDE.md files, skills, hooks, rules, subagents and more
https://t.co/LqIq4A143j

Steering Claude Code: CLAUDE.md files, skills, hooks, rules, subagents and more
https://t.co/mMa07czEss
