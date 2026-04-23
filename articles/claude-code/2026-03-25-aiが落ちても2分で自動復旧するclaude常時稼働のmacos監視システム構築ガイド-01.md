---
id: "2026-03-25-aiが落ちても2分で自動復旧するclaude常時稼働のmacos監視システム構築ガイド-01"
title: "【AIが落ちても2分で自動復旧する。Claude常時稼働のmacOS監視システム構築ガイド】"
url: "https://note.com/disa_pr/n/n06e4759d724f"
source: "note"
category: "claude-code"
tags: ["AI-agent", "note"]
date_published: "2026-03-25"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

株式会社dotgearによる実践ガイド。**Mac miniでAIエージェントを24時間365日稼働させる中で、実際の障害を経験しながら構築した監視・自動復旧システムの設計思想と全構成を公開**した。

Gateway（AIとSlackを繋ぐ常駐プロセス）のクラッシュ検知・自動復旧、SubAgentの3回リトライ、ディスク逼迫・不正ログイン検知、Mac再起動後の自動起動確認など、7つのLaunchAgentで多層防御を構成。**設計の核心は「検知だけでなく自動復旧まで実装する」「通知疲れを防ぐクールダウン」「同じ障害の再発を記録で検知する」の3原則**だ。

AIエージェントへの業務委任が進むほど、「落ちたとき誰が気づくか」という問いが重くなる。仕組みを整えて初めて、人間は委任できる。

🐮 DiSAひとこと   
ディレクションも近しい構造。人に任せるためには、任せる仕組みが先に必要になる。AIの自律運用を支える設計力こそ、これからのディレクションに求められるスキルかもしれない。

引用元：<https://note.com/dotgear/n/n91be8bdd5285>

[#AIエージェント](https://note.com/hashtag/AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88) [#Claude](https://note.com/hashtag/Claude) [#自動化](https://note.com/hashtag/%E8%87%AA%E5%8B%95%E5%8C%96) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#macOS](https://note.com/hashtag/macOS)
