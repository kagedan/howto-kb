---
id: "2026-07-22-3chhe-1passwordのaiエージェント連携をcodexとclaude-codeの両方で実際-01"
title: "@3chhe: 1PasswordのAIエージェント連携を、CodexとClaude Codeの両方で実際に設定し、安全境界まで検証する"
url: "https://x.com/3chhe/status/2079871201997111752"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "OpenAI", "GPT", "x"]
date_published: "2026-07-22"
date_collected: "2026-07-23"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

1PasswordのAIエージェント連携を、CodexとClaude Codeの両方で実際に設定し、安全境界まで検証するコピペ用プロンプト↓

------✂︎------

CodexまたはClaude Codeから1Passwordを安全に利用できるように、公式情報の調査、現状監査、設定、検証、運用ルールの作成、テストデータの削除まで進めてください。

【目的】

・ChatGPTまたはhttps://t.co/gyLeCOOMvEのサブスクリプションOAuthを維持する
・AIモデルの回答やMCPの出力へ秘密値を表示しない
・1Password EnvironmentsのLocal MCP Serverを主経路として検証する
・秘密値だけでなく、メタデータ、子プロセスの環境変数、ローカルの.envの信頼境界も確認する
・本番Environment、実秘密値、無人実行は、私の明示承認なしに有効化しない

【安全条件】

・実際のAPIキー、パスワード、トークン、顧客情報、個人情報を、プロンプト、標準出力、ログ、成果物へ書かない
・Vault名、アカウントID、Environment ID、Environment名、変数名などの生情報を最終回答へ出さない
・テストにはプロセス内でランダム生成したダミー値だけを使い、値そのものは一度も表示しない
・Environment名と変数名には、外部へ見えても問題のない汎用名を使う
・Shell PluginでOPENAI_API_KEYやANTHROPIC_API_KEYを注入せず、サブスクリプションOAuthを維持する
・既存の設定、symlink、未コミット変更、別セッションの作業を保護し、勝手にstash、reset、rebase、全体上書きをしない
・永続許可、セキュリティ設定の変更、Environmentの作成、永久削除の直前には、対象と影響を示して私の確認を取る
・確認できない事実を推測で断定せず、公式ドキュメントの記載と実機で確認した結果を分けて記録する

【作業手順】

1. 計画

最初に、作業計画、変更予定、承認が必要になる操作、想定する成果物を提示してください。

2. 公式情報の調査

1Password Environments MCP Server、local .env files、Codex／Claude Code向けShell Plugin、OpenAIのChatGPTプランでのCodex利用、AnthropicのPro／MaxプランでのClaude Code利用、認証の優先順位を公式情報で確認してください。仕様は更新される可能性があるため、必ず現在の公式ページを参照してください。

3. 現状監査

次の項目を、秘密値を表示せずに確認してください。

・1PasswordデスクトップアプリとCLIのバージョン
・Local MCP ServerとMCPクライアント統合の有効状態
・CodexとClaude CodeのMCP登録状態
・CodexがChatGPT OAuthを利用しているか
・Claude Codeがhttps://t.co/gyLeCOOMvE OAuthを利用しているか
・OPENAI_API_KEYまたはANTHROPIC_API_KEYがOAuthより優先されていないか
・CodexとClaude Codeの子プロセスへ、キー、トークン、secret-likeな環境変数が継承されていないか

4. 方針判定

サブスクリプションOAuthを維持する前提で、Local MCP ServerとShell Pluginのどちらが適切か判断してください。APIキー認証へ切り替わる可能性がある場合は作業を止め、理由と根拠を説明してください。

5. Local MCPの設定

私の承認後、1PasswordのLocal MCP ServerとMCPクライアント統合を有効にし、CodexとClaude Codeへ1password-mcpを登録してください。設定ファイルがsymlinkの場合は実体を部分編集し、TOML／JSONの構文検証を行ってください。Always allowは選ばず、原則として1回限り、または現在のセッション中だけの承認にしてください。

6. 空のEnvironmentで接続確認

私の承認後、外部へ見えても問題のない汎用名で、開発専用Environmentを1件だけ作成してください。最初は変数を追加せず、CodexとClaude CodeからEnvironment件数だけを返すスモークテストを行ってください。ツール履歴に表示されるアカウント、Environment、変数のメタデータ範囲を確認し、生情報は成果物へ転記し
