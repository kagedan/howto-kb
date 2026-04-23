---
id: "2026-03-22-anthropicの戦略はllmを持たないaiネイティブsaasを駆逐するのか-01"
title: "Anthropicの戦略はLLMを持たないAIネイティブSaaSを駆逐するのか？"
url: "https://note.com/taka8109/n/n5595067201a3"
source: "note"
category: "ai-workflow"
tags: ["LLM", "note"]
date_published: "2026-03-22"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

Anthropicの次の一手は、単なる高性能LLMの提供に留まりません。いま同社が進めているのは、Claudeを「AIの入口」ではなく**「仕事の実行基盤」**に変える戦略です。  
  
象徴的なのがClaude Marketplaceです。これは企業が既存のAnthropic契約枠を使ってパートナー製品を購入でき、請求もAnthropicがまとめる仕組みです。つまりAnthropicはモデル会社の立場から、**AI予算の集約先へ進もうとしている**のです。

この動きが重要なのは、個別SaaSを使い分ける世界から、**Claudeを起点に必要な機能を呼び出す世界へ重心が移る**からです。Integrationsは外部ツールとの接続を広げ、MCPはAIと外部システムをつなぐ標準として機能します。さらにAnthropicはSkillsやPluginsを用意し、企業は社内向けのプラグインマーケットプレイスまで持てます。EnterpriseではClaude、Claude Code、Cowork、connectors、SSO、SCIM、監査ログ、データ保持ポリシーまで一体で提供されており、実行・拡張・統制が同じ箱の中に入っています。

この構造の中で、**LLMを持たないAIネイティブSaaSは厳しくなります**。理由は４つあります。

* 第1に原価です: 外部LLMのAPI費用を払いながら利益を出す必要があります。
* 第2にUIです: ユーザーの主画面がClaudeになると、SaaS側は裏側の機能提供者に下がりやすくなります。
* 第3に販売です: AnthropicはPro、Max、Enterpriseで機能を束ね、既存契約枠で周辺製品まで買えるため、新興SaaSは単独で稟議を通しにくくなります。
* 第4にガバナンスです: 大企業導入で必要な管理機能をAnthropicが先回りして揃えているため、後発は機能だけでは勝ちにくいのです。

さらに見逃せないのが、Artifactsの経済性です。Claude上で作ったAIアプリは、利用者が自分のClaudeアカウントで認証し、その利用量が利用者側の契約に計上されます。**開発側がAPI利用料を持たなくてよい設計は、薄いラッパー型AI SaaSの収益モデルを直撃**します。要約、検索、下書き、軽い自動化のように、差別化が浅い領域ほど価格競争と収益圧迫にさらされやすいでしょう。(もっとわかりやすく言うと、**LLMサービスを持たない彼らは、AnthropicやOpenAIに支払うAPI料金との差額で利益を上げなければならないビジネスモデルになってしまい**、ビジネスとしてはかなり厳しいです）

ただし、すべてのAIネイティブSaaSが駆逐されるわけではありません。残るのは、**独自データ、深い業務ロジック、規制対応、強いワークフロー、システム・オブ・レコード**を持つ会社です。実際、Claude Marketplaceの初期パートナーにはGitLab、Harvey、Replit、Rogo、Snowflakeが並んでいます。Anthropicは専門SaaSを消すというより、Claudeから呼び出される専門レイヤーとして再編しようとしているように見えます。

結論として、AnthropicのNext戦略は「AI SaaSを一斉に消す」ことではありません。**価値の薄い部分から順にClaudeへ吸収し、横断UI、実行基盤、拡張基盤、調達基盤、統制基盤を押さえる**ことです。したがって、LLMを持たないAIネイティブSaaSが生き残る条件は明確です。Claudeに置き換えられにくい**深い業務価値を持つか、Claude上で選ばれる専門拡張になるかの二択**に近づいていくはずです。

**参考出典**

1. Claude Marketplace | Claude by Anthropic
2. Claude can now connect to your world | Claude
3. What is the Model Context Protocol (MCP)?
4. Agent Skills overview | Claude Platform Docs
5. Plugins in the SDK | Claude Platform Docs
6. Manage Cowork plugins for your organization | Claude Help Center
7. Build and share AI-powered apps with Claude | Claude
8. Choosing a Claude plan | Claude Help Center
9. Using Claude Code with your Pro or Max plan | Claude Help Center
10. Claude Enterprise, now available self-serve | Claude
11. Enterprise plan | Claude by Anthropic
