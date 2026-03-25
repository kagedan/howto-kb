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

<p name="5a8f2a46-1563-4aba-9adc-1d3834d746d6" id="5a8f2a46-1563-4aba-9adc-1d3834d746d6">株式会社dotgearによる実践ガイド。<strong>Mac miniでAIエージェントを24時間365日稼働させる中で、実際の障害を経験しながら構築した監視・自動復旧システムの設計思想と全構成を公開</strong>した。</p><p name="de2f59af-6ae9-42db-9dc0-0d428b42b102" id="de2f59af-6ae9-42db-9dc0-0d428b42b102">Gateway（AIとSlackを繋ぐ常駐プロセス）のクラッシュ検知・自動復旧、SubAgentの3回リトライ、ディスク逼迫・不正ログイン検知、Mac再起動後の自動起動確認など、7つのLaunchAgentで多層防御を構成。<strong>設計の核心は「検知だけでなく自動復旧まで実装する」「通知疲れを防ぐクールダウン」「同じ障害の再発を記録で検知する」の3原則</strong>だ。</p><br/><a h
