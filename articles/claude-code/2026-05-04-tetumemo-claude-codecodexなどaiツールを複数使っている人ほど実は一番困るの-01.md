---
id: "2026-05-04-tetumemo-claude-codecodexなどaiツールを複数使っている人ほど実は一番困るの-01"
title: "@tetumemo: 📝Claude Code、CodexなどAIツールを複数使っている人ほど、実は一番困るのは「使い方」ではなく「ルールの散"
url: "https://x.com/tetumemo/status/2051216440670494749"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "Gemini", "x"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-x"
---

📝Claude Code、CodexなどAIツールを複数使っている人ほど、実は一番困るのは「使い方」ではなく「ルールの散らばり」だと思う

今回じっくり整理してかなり学びがあった

Codex、Claude Code、Gemini、Antigravity
それぞれにAGENTS.md / CLAUDE.md / GEMINI.mdなどコアとなる指示書（◯◯.md）があり、能力を拡張するSkillも別々にある、気づくと管理場所がバラバラになる

でも整理の本質はシンプルだった

「原本管理」をGitHubで実現すること

今回の学びを10個でまとめます🧵

①まず分けるべきは『指示書（◯◯.md）』と『Skill』

ここを混ぜると一気に分からなくなる

・指示書
→ AI全体の基本姿勢、安全ルール、作業方針

・Skill
→ 特定作業をうまくやるための手順書

つまり

master-instructions = 憲法
master-skills = 道具箱

この分け方がかなり効いた https://t.co/BbmiLsVfME

②AGENTS.md / CLAUDE.md / GEMINI.md は完全同一にしない

最初は「全部同じにしたい」と思う

でも実際には

・CodexはAGENTS.md
・Claude CodeはCLAUDE.md
・GeminiはGEMINI.md

というように、読むファイルも違うし、得意な動きも違う

だから正解は

共通ルール + ツール別差分

完全統一ではなく、統一管理

③一番充実したものを土台にする

今回は既存のAGENTS.mdとCLAUDE.md系が一番充実していた

そこに

・Gemini独自のルール
・Google Drive側の保存場所ルール
・settings系を触らない方針

を合流した

ゼロから作るより、すでに育っているものを土台にする方が強い

運用は「発明」より「整理」が大事

④settings.json は統一しない

ここは大事

AGENTS.md / CLAUDE.md / GEMINI.md はAIへの指示書

でも settings.json や config.toml はアプリ本体の設定

・認証
・権限
・自動処理
・プラグイン
・連携先

こういう配線が入っている

指示書と同じノリで統一すると壊れる可能性がある

統一しない。場所と役割だけ管理する

⑤原本とコピーを分ける

今回の整理で一番スッキリしたのはこれ

原本:
G:\マイドライブ\AI\master-instructions

コピー:
C:\Users\tooru\.codex\AGENTS.md
C:\Users\tooru\.claude\CLAUDE.md
C:\Users\tooru\.gemini\GEMINI.md

コピーを直接いじり続けると、必ずズレる

原本を直す
生成する
反映する

この流れにするだけで、迷子になりにくい

⑥Skillも同じ思想で管理する

すでにmaster-skillsはこうなっていた

原本:
G:\マイドライブ\AI\master-skills\skills

反映先:
・Codex
・Claude Code
・Google Antigravity

ここに合わせて、master-instructionsも同じ考え方にした

ツールが増えるほど、個別最適ではなく「原本管理」が効いてくる

これはAI活用の地味だけど重要な基盤

⑦READMEはただの説明書ではなく、迷子防止マップ

今回、master-instructionsにもREADMEを作った

書いたのは

・何を管理する場所か
・どこが原本か
・どこへ反映するか
・settings系はなぜ統一しないか
・master-skillsとの関係

これがあるだけで、未来の自分が助かる

READMEは他人のためだけではなく、数週間後の自分への案内板

⑧相互リンクを持たせる

master-instructionsからmaster-skillsへ
master-skillsからmaster-instructionsへ

双方のREADMEに関係を書いた

これで

・基本方針を直すならmaster-instructions
・作業手順をSkill化するならmaster-skills

と判断できる

管理場所が2つある時は、つながりを書かないと必ず忘れる

リンクは構造の記憶

⑨manager Skillを作る

今回さらに

master-instructions-manager

を作った

これはAGENTS.md / CLAUDE.md / GE
