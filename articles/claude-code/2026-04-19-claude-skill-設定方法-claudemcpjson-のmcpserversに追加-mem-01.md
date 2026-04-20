---
id: "2026-04-19-claude-skill-設定方法-claudemcpjson-のmcpserversに追加-mem-01"
title: "@claude_skill: 設定方法 ~/.claude/.mcp.json のmcpServersに追加: memory: { com"
url: "https://x.com/claude_skill/status/2045863095789343091"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "x"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

これClaude Codeユーザーなら全員共感すると思う

新しいセッション開くたびに「このプロジェクトは○○で、××を使ってて、前回△△まで進んで...」って毎回説明し直すやつ

@ClaudeCode_love が紹介してたMemory MCPを入れると、これが消える

リプで設定方法も含めて解説👇 https://t.co/qjnsVZXhs5

何が起きてたかというと

Claude Codeはセッション終了で記憶が全部飛ぶ
CLAUDE.mdで指示は残せるけど「前回の会話で学んだこと」は消える

自分もターミナルのタブを消さないように気を使って、セッション維持に神経使ってた

Memory MCPはナレッジグラフで情報同士の関係性ごと保持するから「Aの問題をBで解決した」みたいな因果も残る

設定方法

~/.claude/.mcp.json のmcpServersに追加:
"memory": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"]
}

Claude Codeを新しいセッションで開くだけ

記憶はローカルの.jsonlファイルに蓄積
CLAUDE.md=静的ルール / Memory MCP=動的記憶
両方入れると2層構造になる

仕組み

エンティティ（プロジェクト名、ツール名等）
＋リレーション（AはBに依存、CはDで解決）
＋オブザベーション（個別の事実）
の3層ナレッジグラフ

セッション中の会話を自動キャプチャ→次セッションで関連記憶だけ注入

注意: 最初の数セッションは蓄積フェーズで効果薄い。記憶が増えすぎたらトークン消費も増えるので定期的な整理も必要

@ClaudeCode_love 毎回同じ説明するストレスから解放されるのはガチでデカい

特に長期プロジェクトやってる人、複数プロジェクト並行してる人は試す価値ある

GitHub: https://t.co/acSLBh61uM

@claude_skill をフォロー&amp;保存で最速キャッチアップ👍
