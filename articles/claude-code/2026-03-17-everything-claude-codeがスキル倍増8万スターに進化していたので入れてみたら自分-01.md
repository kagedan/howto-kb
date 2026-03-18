---
id: "2026-03-17-everything-claude-codeがスキル倍増8万スターに進化していたので入れてみたら自分-01"
title: "Everything Claude Codeがスキル倍増・8万スターに進化していたので入れてみたら、自分の設定が丸裸になった"
url: "https://zenn.dev/lova_man/articles/fa521ace28a12f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

本文

 結論から簡潔に

Everything Claude Code（ECC）を本番プロダクトに導入したのをきっかけに、.mcp.jsonにAPIキーが3つハードコードされていたのを発見した
MCPのタスク別切り替えで、コンテキスト消費が110,000→33,000トークンに（70%削減）
既存のCLAUDE.mdやフックとの競合なくマージできた

この記事は、ECCの機能紹介ではなく、本番運用中のプロダクトに入れて実際に何が見つかったかの記録です。ECCの概要や設計思想は、末尾の参考リンクにある先行記事が詳しいので、そちらに譲ります。


 何が見つかったか──APIキー3つ、...
