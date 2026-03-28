---
id: "2026-03-27-anthropicのハーネス設計論文を読んでclaude-codeの開発環境を全部見直した-01"
title: "Anthropicの「ハーネス設計」論文を読んで、Claude Codeの開発環境を全部見直した"
url: "https://zenn.dev/lova_man/articles/99777e473b3c2c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

本文
AIに「この実装で問題ない？」と聞くと、ほぼ毎回「はい、適切に実装されています」と返ってきます。でも実際に動かすと、本番で壊れるコードが混ざっている。Anthropicが公式ブログで、この現象の構造と解決策を実験データ付きで公開していました。

 結論

Anthropicが公式ブログで発表した「ハーネス設計」の研究で、AIは自分の成果物を甘く評価することが実験的に示された
解決策は「生成するAI」と「評価するAI」の分離。この構造はClaude Codeの設定（CLAUDE.md・スキル・エージェント・フック）で再現できる
自分の環境を見直したら、「生成」はできていたが「評...
