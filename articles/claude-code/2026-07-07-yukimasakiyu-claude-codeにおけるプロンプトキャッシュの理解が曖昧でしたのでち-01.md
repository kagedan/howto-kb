---
id: "2026-07-07-yukimasakiyu-claude-codeにおけるプロンプトキャッシュの理解が曖昧でしたのでち-01"
title: "@yukimasakiyu: Claude Codeにおけるプロンプトキャッシュの理解が曖昧でしたので、ちょっと調べてみました。 ※Claudeサブス"
url: "https://x.com/yukimasakiyu/status/2074490369929314478"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "x"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Codeにおけるプロンプトキャッシュの理解が曖昧でしたので、ちょっと調べてみました。
※ClaudeサブスクリプションでのClaude Codeのメインスレッドでは、プロンプトキャッシュのTTLはデフォルト1時間で、cache hitするたびにそこからさらに1時間と延長されるので、連続稼働させている分には心配なさそう(キャッシュにヒットし続けてくれるので、デフォルトシステムプロンプトやToolsの定義等の固定の設定値の読み込み時のInput Tokenの料金は0.1倍のまま維持される)でした。

【Claude CodeにおけるデフォルトTTL】
• Claude subscriptionのメイン会話: 1時間　※5分に設定することも可能
• subscriptionでusage credits課金に入った場合: 5分　※plan usage limitを超え、usage creditsを使う場合は課金対象になるため、Claude CodeはTTLを5分へ落とすと説明されています。
• Subagents: Claude subscription でも subagent は 5-minute TTL。1-hour 自動適用は main conversation。
• Anthropic API key: per-token 課金なので より安い5-minute TTL が default。ENABLE_PROMPT_CACHING_1H=1 で 1時間に設定可能。

【整理】
• /clear や /compact の後でも、システムプロンプト・Tools などの初期設定はリクエストに含まれます。
• ただし、それらに「必ずプロンプトキャッシュが効く」わけではなく、TTL 内で、かつ prefix / cache key が一致している場合に限って cache read になります。
• TTL 外・prefix 変更・モデル変更・effort 変更・Claude Code 更新・Tools 構成変更などがあると、初期設定部分も再処理され、cache creation または通常 input 扱いになります。
• なお、Fable 5 → Opus 4.8 fallback については、Claude Code docs 上「model switch」扱いなので、その時点で Opus 側は cache 作り直しです。さらに Fable 5へ戻しても、その戻した直後のターンは model switch なので、cache hit は期待しないほうが安全です。戻した後、Fable 5で連続して使えば、そこから再び Fable 側の cache が温まります。
• 1時間TTLの場合でも、キャッシュは「最初に作られてから固定で1時間」ではなく、cache hitするたびにTTLタイマーがリセットされます。したがって、長時間エージェントが継続的にClaude APIリクエストを発生させ、同じprefixにhitし続ける限り、実務上はずっと温かい状態を維持できます。
• ただし、1時間より長いTTLは、公式仕様上は選べません。Claude APIが提供するTTLは5分と1時間の2種類です。Claude Code docsも、APIにはfive-minute TTLとone-hour TTLの2つがある、と説明しています。
• API key利用で ENABLE_PROMPT_CACHING_1H=1 にすると、cache write料金は高くなります。具体的には、5分writeの1.25xから、1時間writeの2.0xになります。したがって、cache creation部分は5分TTL比で60%高いです。
• ただし、cache read料金は0.1xのままなので、5分超〜1時間以内に同じ巨大prefixを再利用するなら、総額では1時間TTLのほうが安くなることがあります。
