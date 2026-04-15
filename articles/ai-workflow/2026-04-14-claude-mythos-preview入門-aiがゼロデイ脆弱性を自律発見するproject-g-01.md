---
id: "2026-04-14-claude-mythos-preview入門-aiがゼロデイ脆弱性を自律発見するproject-g-01"
title: "Claude Mythos Preview入門 — AIがゼロデイ脆弱性を自律発見するProject Glasswingの仕組み"
url: "https://qiita.com/kai_kou/items/1b7e28ce3631ec2d50a7"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

<!-- IMAGE_SLOT: hero | Claude Mythos Preview と Project Glasswing のコンセプト図。Anthropicのロゴとサイバーセキュリティをテーマにしたアイキャッチ。16:9、ブルー系配色 -->

## はじめに

2026年4月7日、Anthropicは「Claude Mythos Preview」という新しいAIモデルを発表しました。これは同社史上最も強力なモデルですが、**一般公開されていません**。

理由は単純かつ衝撃的です。このモデルは主要なOSやブラウザに存在した「数千件」のゼロデイ脆弱性を数週間で自律的に発見・悪用できるほどの能力を持っており、攻撃的な用途に悪用されるリスクが高すぎると判断されたためです。

代わりにAnthropicは「**Project Glasswing**」を立ち上げました。AWS、Apple、Microsoft、Googleなど12社が参加する防衛的コンソーシアムで、Mythos Previewを攻撃者より先に脆弱性を発見するために活用します。

### この記事で学べること

- C
