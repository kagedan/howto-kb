---
id: "2026-03-24-claude-codeを3層に分けたらgithub-issueが勝手に実装されるようになった-bee-01"
title: "Claude Codeを3層に分けたら、GitHub Issueが勝手に実装されるようになった — beeops設計の全記録"
url: "https://zenn.dev/whale_ai/articles/beeops-construction"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

GitHub Issueを立てる。しばらくすると、PRが上がっている。サブタスク分解、並列実装、コードレビュー、CI確認まで終わっている。
beeops はそれをやるnpmパッケージだ。Claude Codeのセッションをtmuxで3層に並べて、Issue単位で自律的に動かす。
npm install beeops
npx beeops init
# Claude Code で /bo を実行するだけ
この記事では設計の「なぜ」と「どう使うか」を一緒に書く。壊しながら到達した設計判断の記録と、実際の使い方をセットで理解できるようにした。

 出発点：チームで積み上げる場所がなかった
世の...
