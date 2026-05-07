---
id: "2026-05-06-axelrod-jpn-19-毎日obsidianにメモを貯めているのに-あの情報どこだっけと検索し-01"
title: "@axelrod_jpn: 🧵 1/9 毎日Obsidianにメモを貯めているのに、 「あの情報どこだっけ」と検索しまくってる人へ。 Claude"
url: "https://x.com/axelrod_jpn/status/2052044255284339102"
source: "x"
category: "claude-code"
tags: ["MCP", "API", "x"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

🧵 1/9
毎日Obsidianにメモを貯めているのに、
「あの情報どこだっけ」と検索しまくってる人へ。

Claude Desktop + MCPでObsidianと繋ぐだけで、
あなたのノート全体をAIが読んで
「第二の脳」に変わる。

設定20分。効果は永続。やり方を解説🧵 https://t.co/0OVu0n38OB

🧵 2/9
【なぜObsidian × Claudeが必要か】

普通のAI：あなたの過去のノートを知らない
Obsidian単体：検索できるが"思考"はしない

この組み合わせだと…
✅ 何千ものメモからClaudeが文脈を読む
✅ 忘れていたアイデアを自動で再接続
✅ ノート作成・整理・検索がAI自動化

「情報の収集」から「知識の活用」へ飛躍する

🧵 3/9
【STEP 1】必要なものを用意する

準備物：
□ Obsidian（無料・Desktop版）
□ Claude Desktop（Anthropic公式）
□ Claude Proプラン（推奨）

まずObsidianを起動して
Settings → Community plugins
→ 「制限モード」をOFFにする

⚠️ここをOFFにしないとプラグインが入らない

🧵 4/9
【STEP 2】ObsidianにプラグインをINSTALL

Community plugins → Browse で以下を検索・導入：

① Local REST API（作者: Adam Coddington）
　→ ClaudeがObsidianにアクセスするための窓口

② MCP Tools（作者: Jack Steam）
　→ ClaudeとObsidianを繋ぐ橋梁プラグイン

③ Templater（オプション）
　→ AIが自動でテンプレートからノート作成

3つ全部「Enable」に切り替えること

🧵 5/9
【STEP 3】MCP Toolsの設定

Obsidian Settings → MCP Tools を開く

① 「Download MCP Server」をクリック
② ダウンロード完了後、サーバーが起動
③ Status: "Running" になればOK

ローカルサーバーが立ち上がり
（通常ポート3000）
Claudeがあなたのvaultに
セキュアにアクセスできる状態になる

🧵 6/9
【STEP 4】Claude DesktopでMCPを有効化

Claude Desktop → Settings → Developer
→ Edit Config を開く

claude_desktop_config.json に追記：

{
  "mcpServers": {
    "obsidian": {
      "command": "node",
      "args": ["/path/to/mcp-server"]
    }
  }
}

※pathはMCP Toolsが自動表示してくれる
Claude Desktopを再起動すれば完了

🧵 7/9
【STEP 5】動作確認

Claude Desktopを開いて入力：

「私のObsidianのvaultに
アクセスできますか？
テストノートを1つ作成してください」

→ Claudeが自動でノートを作成したら成功！

これで
・ノートの読み込み
・新規作成
・タグ付け・整理
・vault横断検索
が全てAIで動くようになった

🧵 8/9
【これで何ができるか】

📌 朝のルーティン
「今週のノートを要約してToDoを作って」

📌 知識の再発見
「AIについての過去のメモを全部繋げて」

📌 コンテンツ制作
「このテーマに関する私のメモを
 全部まとめてnote記事の下書きを作って」

📌 情報整理
「インボックスのメモを分類・タグ付けして」

ノートが"死蔵"から"武器"に変わる

🧵 9/9
【まとめ】

Obsidian + Claude MCP =
あなただけのAI第二の脳

過去の自分の思考を
Claudeが読み込み、繋ぎ、進化させる。

メモは「書いたら終わり」じゃない。
それを活かすシステムが必要。

設定20分でナレッジワークが
根本から変わる。

今すぐ試してみてください

感想頂けたら幸いです🔁
