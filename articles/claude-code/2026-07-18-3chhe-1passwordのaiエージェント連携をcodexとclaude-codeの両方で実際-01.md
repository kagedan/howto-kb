---
id: "2026-07-18-3chhe-1passwordのaiエージェント連携をcodexとclaude-codeの両方で実際-01"
title: "@3chhe: 1PasswordのAIエージェント連携を、CodexとClaude Codeの両方で実際に設定し、安全境界まで検証して"
url: "https://x.com/3chhe/status/2078464222288359480"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "OpenAI", "GPT", "x"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

1PasswordのAIエージェント連携を、CodexとClaude Codeの両方で実際に設定し、安全境界まで検証してみた。

結論から言うと、1Password MCPは開発用途では十分に実用的だった。ただし、「AIに秘密値が表示されない」ことと、「そのまま本番で安全に使える」ことは別の話だった。

【今回確認したこと】

・ChatGPT／https://t.co/gyLeCOOMvEのサブスクリプションOAuthを維持できるか
・秘密値がモデルの回答やMCPの履歴へ返らないか
・Environment名や変数名などのメタデータはどこまで見えるか
・ローカルの.envが平文ファイルとして残らないか
・承認後、その値を読めるプロセスは本当に限定されるか
・アクセスを拒否した場合、処理が再試行せず停止するか
・検証後にダミーデータや一時ファイルを残さず片付けられるか

単に「接続できた」で終わらせず、認証経路、秘密値、メタデータ、実行時注入、拒否動作、クリーンアップまで一通り確認した。

【なぜShell PluginではなくLocal MCPを選んだのか】

1PasswordとAIツールを連携する方法は、大きく分けると、ブラウザ上のClaude連携、1Password EnvironmentsのLocal MCP Server、Codex／Claude Code向けのShell Pluginがある。

今回の前提は、CodexをChatGPTの有料プラン、Claude Codeをhttps://t.co/gyLeCOOMvEの有料プランのOAuthで使い続けること。この前提では、Shell Pluginは目的と少しずれる。

Shell Pluginは、OPENAI_API_KEYやANTHROPIC_API_KEYをCLIプロセスへ注入する方式。環境変数のAPIキーがOAuthより優先されると、サブスクリプション枠ではなく、API従量課金の認証経路へ切り替わる可能性がある。

実際、手元のClaude Codeも「OAuthで使っているつもり」だったが、調べると環境変数のAPIキーが優先されていた。そこで今回はShell Pluginを使わず、Local MCP Serverを主経路にした。Claude Codeは起動時にANTHROPIC_API_KEYを除外してhttps://t.co/gyLeCOOMvE OAuthへ戻し、Codexも子プロセスへAPIキーやトークンを継承しない設定にした。

新しい連携を追加する前に、現在どの認証方式が使われているかを確認する。これが今回、最初に押さえるべきポイントだった。

【Local MCPで実際に分かったこと】

1PasswordのLocal MCP Serverを有効にし、CodexとClaude Codeの両方へ登録した。最初は実秘密値を使わず、空の開発用Environmentを1件だけ作成し、両方のクライアントからEnvironment件数だけを返すスモークテストを実施した。

Codex、Claude Codeともに接続は成功し、最終回答にも秘密値は表示されなかった。一方で、秘密値そのものはMCPから返されなくても、アカウント、Environment、変数の名前や識別情報はツール履歴から見える場合がある。

つまり、守るべきものは秘密値だけではない。顧客名、案件名、未公開プロジェクト名をEnvironment名や変数名へ入れず、メタデータもモデルやローカル履歴から見える前提で、外部へ見えても問題のない汎用名にする必要がある。

次に、ランダム生成したconcealed属性のダミー変数で、実行時注入を検証した。結果は次のとおり。

・変数名はMCPから参照できた
・秘密値そのものはMCPから返らなかった
・ローカルの.env経由で、実行時に正しい値を利用できた
・マウント先は通常の平文ファイルではなくFIFOだった

ここまでは期待どおりだった。ただし、もう一段テストすると、重要な制約が分かった。

【いちばん重要だった制約】

1Passwordでアクセスを承認した後は、最初に起動した対象プロセスだけでなく、同じ端末上の独立した別プロセスからもFIFOを読めた。

1Passwordの公式ドキュメントにも、承認後は1Passwordをロックするかマウントを無効化するまで、プロセスを区別しない旨が記載されている。つまり、ローカルの.envは「特定プロセスだけに秘密値を渡す仕組み」ではない。

平文をディスクへ残さない点では優れているが、承認中は端末全体が信頼境界になる。この違いは大きい。

【今回決めた運用ルール】

1. Environmentは開発、検証、本
