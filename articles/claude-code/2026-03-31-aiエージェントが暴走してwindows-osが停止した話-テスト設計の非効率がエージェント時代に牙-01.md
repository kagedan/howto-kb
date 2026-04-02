---
id: "2026-03-31-aiエージェントが暴走してwindows-osが停止した話-テスト設計の非効率がエージェント時代に牙-01"
title: "AIエージェントが暴走してWindows OSが停止した話 — テスト設計の非効率がエージェント時代に牙を剥く"
url: "https://zenn.dev/saytooy_arch/articles/09-agent-runaway-test-io"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

何が起きたか
Claude Codeのマルチエージェント体制で飲食店向けSaaSを開発中、programmerエージェントがテスト修正を60分間繰り返し、Windows OSのCPU/メモリ/ディスクが枯渇してコマンドを受け付けなくなった。

 原因: テストコードのI/O非効率パターン

 パターン1: vi.resetModules() + dynamic importの繰り返し
// 毎テストでモジュールキャッシュを全削除→ディスクから再読込
beforeEach(() =&gt; {
  vi.clearAllMocks();
  vi.resetModules();  //...
