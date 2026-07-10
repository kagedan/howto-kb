---
id: "2026-07-10-ibataaaa08-claude-codeの利用料で誰が何にいくらが使ったかが分からなかったので前-01"
title: "@ibataaaa08: Claude Codeの利用料で「誰が・何に・いくら」が使ったかが分からなかったので、前にAIに自動で毎朝スプレッドシー"
url: "https://x.com/ibataaaa08/status/2075460108730180048"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Codeの利用料で「誰が・何に・いくら」が使ったかが分からなかったので、前にAIに自動で毎朝スプレッドシートに勝手に溜まっていくツールを作ったらめっちゃ便利なのでシェアします！

これを作成してから無駄なコスト削減できて、メンバーのAIの定着度もわかるのでお勧めです！

作るのに使ったプロンプト、スレッドに置いときますのでよかったら丸コピしてください〜！

＜実際のプロンプト＞
あなたはシニアな自動化エンジニアです。私の「AIコーディングエージェント（Claude Code）の利用コストを、誰が・何に・いくら使ったかまで全自動で記録する原価台帳」を、私の環境に構築してください。特定のツールやIDに依存しない、汎用で再現可能な実装にしてください。

※もし私が Claude Code 以外のエージェント（Cursor など）を使っている場合、本文中の「PostToolUse hook」「~/.claude 配下の履歴 JSONL」は、そのエージェントの相当機構（ツール実行後に発火するフック／トークン使用量ログの保存先）に読み替えて実装してください。まず私にどのエージェントかを確認してから進めて構いません。

■ 作るもの（3層アーキテクチャ）
1. 記録(capture)：ツール実行のたびに発火する hook が、メタデータをバックグラウンドで Webhook に POST する
2. 転送(transport)：受け口の Web アプリ（デフォルトは Google Apps Script。私が別のものを指定したらそれに合わせる）
3. 蓄積(store)：スプレッドシート2枚に追記
   - 活動台帳：誰が・いつ・何をしたか（1行 = ツール呼び出し1回）
   - トークン台帳：いくらか（1行 = 日 × セッション × モデルの集計）
   - 2枚は session_id 列で JOIN できるようにする

■ 設計原則（必ず守る）
- プライバシー：送るのはメタデータだけ。プロンプト本文・生成物の中身・個人情報・ファイル本文は絶対に送らない。artifact は「ツール名＋対象の短い要約（allowlist方式）」に留める
- 非ブロッキング＆フェイルセーフ：hook は本来の作業を1msも止めない。POSTはバックグラウンド実行、失敗しても握りつぶしてエージェントの動作を妨げない
- 秘密情報をハードコードしない：Webhook URL は環境変数（例: LEDGER_WEBHOOK_URL）から読む
- 冪等性：同じ日を二重集計しない（date × session_id × model をキーに上書き or 重複回避）
- est_cost は「推定」：公式の公開単価表 × 実測トークンで概算し、あくまで目安である旨をコード内コメントとシート説明に明記（正本は各プロバイダのコンソール）。単価は改定されるため、最新の公開単価は各プロバイダの料金ページ（例: Anthropic の Pricing ページ）で確認してから設定値に入れること。ハードコードせず、単価は1か所の設定にまとめて後から直せるようにする

■ 実装手順（この順で、確認しながら進める）
【Step 0｜環境ディスカバリ（推測で作らない）】
- 私が使っているエージェントの hook 機構を確認する（Claude Code なら settings.json の PostToolUse フック）。まずダミーの hook を仕込んで、hook が stdin で受け取る実際の JSON を1回ダンプして、利用できるフィールド（tool 名・session_id 等）を実物で確認してから本実装する
- トークン使用量のログの実体を確認する（Claude Code ならローカルのセッション履歴 JSONL。~/.claude 配下を探索）。1ファイルを開いて、usage の実際のフィールド名（input / output / cache 作成(TTL別) / cache 読出 / model）を実物で確認してから集計ロジックを書く

【Step 1｜スプレッドシート】
- 2タブを作成し、ヘッダーを固定する
  - 活動台帳: timestamp, member, initiator_type, surface, action, client_slug, artifact, duration_s, session_id
  - トークン台帳: date, member, session_id, model, requests, input_tokens, cache_write_short_tokens, cache_write_long_tok
