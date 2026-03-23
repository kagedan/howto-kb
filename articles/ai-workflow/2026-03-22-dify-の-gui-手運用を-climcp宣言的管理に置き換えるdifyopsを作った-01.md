---
id: "2026-03-22-dify-の-gui-手運用を-climcp宣言的管理に置き換えるdifyopsを作った-01"
title: "Dify の GUI 手運用を CLI・MCP・宣言的管理に置き換える「DifyOps」を作った"
url: "https://zenn.dev/cacc_lab/articles/178a9333e99dda"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

3つのアプリに同じプロンプト変更を反映するのに30分ほどかかった
セルフホスト版の Dify を運用していて、ある日気づきました。
GUI で1つのアプリの設定を変えて、同じ変更を残り2つにも反映して、ナレッジベースを更新して、変更前の設定をメモしておいて――全部手作業。
「作る」のは簡単なのに「運用する」のがひたすら面倒。この摩擦を解消するために、DifyOps を作りました。


 DifyOps が目指したもの
単なる「Dify を CLI で触れるようにすること」ではありません。目指したのは、Dify の運用を


再現可能にする（desired state を YAML で...
