---
id: "2026-05-21-claudemd-に-pay-per-call-mcp-を組み込んだら-claude-が勝手に有料-01"
title: "CLAUDE.md に pay-per-call-mcp を組み込んだら Claude が勝手に有料 API を使い始めた話"
url: "https://qiita.com/LemonCake/items/94c7099b5466744e31fa"
source: "qiita"
category: "claude-code"
tags: ["CLAUDE-md", "MCP", "API", "qiita"]
date_published: "2026-05-21"
date_collected: "2026-05-22"
summary_by: "auto-rss"
query: ""
---

:::note
この記事で紹介する **pay-per-call-mcp** は Claude Desktop / Cursor / Windsurf に追加するだけで使えます。デモモードは認証不要・無料です。
- **npm**: https://www.npmjs.com/package/pay-per-call-mcp
- **Glama**: https://glama.ai/mcp/servers/evidai/lemon-cake
- **Discord**: https://discord.gg/JBekn3EF
:::

## この記事でわかること

- CLAUDE.md に MCP ツールの使用ルールを書くと Claude の行動が自動的に変わる仕組み
- `pay-per-call-mcp` を CLAUDE.md に組み込んで「自律的に有料 API を使う Claude」を作る方法
- Web検索・メール調査・Webスクレイピングを毎回指示せず自動実行させる設定例
- Pay Token の予算上限で「使いすぎ」を物理的に防ぐ安全設計
- 実際に動かしたときの Claude の応答の変化（Before / After）

---

## はじめに

[以前の記事](https://qiita.com/LemonCake/items/35e90a7fe50c8434e843) で CLAUDE.md を 300 行から 60 行に圧縮して精度が上がった話を書きました。

その後、さらに踏み込んで「**CLAUDE.md に外部 API の使用ルールを書いたらどうなるか**」を試しました。

結論から言うと、**Claude が何も言わなくても有料 API を自律的に叩き始め、コストも自動で記録されるようになりました**。

---

## 仕組みの概要

`pay-per-call-mcp` は Claude に「USDC ウォレット付きの API プロキシ」を提供する MCP サーバーです。

```
Claude
 ├── call_service(serper) → Google検索結果を返す（$0.005/回）
 ├── call_service(hunter) → メール調査（$0.02/回）
 ├── call_service(firecrawl) → Webページ取得（$0.005/回）
 └── check_tax(T番号) → 国税庁インボイス検証（無料）
```

これを CLAUDE.md に「いつ使うか」のルールとして書くと、Claude が判断して自動的に使うようになります。

---

## セットアップ

### 1. MCP サーバーを追加

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "pay-per-call": {
      "command": "npx",
      "args": ["-y", "pay-per-call-mcp"],
      "env": {
        "LEMON_CAKE_PAY_TOKEN": "your-pay-token-here"
      }
    }
  }
}
```

> 🎮 `LEMON_CAKE_PAY_TOKEN` を空欄にすれば **Demo Mode** で起動します。Wikipedia検索・FXレート・httpbin echo が無料で使えます。

### 2. CLAUDE.md にルールを追加

```markdown
## 外部 API 利用ルール（pay-per-call-mcp）

以下のタスクが発生した場合、必ずこのルールに従うこと。

### Web 検索
- 「調べて」「検索して」「最新情報を」という指示には
  `call_service` で serviceId=`serper` を使う
- ブラウザ操作や WebSearch ツールより優先する

### Webページ取得
- URL を読み込む場合は `call_service` で serviceId=`firecrawl` を使う
- Markdown 形式で返ってくるため後処理が不要

### メール・企業調査
- 企業名やドメインからメールアドレスを調べる場合は
  `call_service` で serviceId=`hunter` を使う

### 請求書確認
- T から始まる 14 桁の番号が出てきたら
  必ず `check_tax` で適格請求書番号を検証する

### 予算管理
- 作業開始前に `check_balance` で残高を確認する
- 残高が $1.00 を切ったら作業を止めて報告する
```

---

## Before / After

### Before（ルールなし）

```
ユーザー: 競合の料金ページを調べておいて

Claude: 申し訳ありませんが、私はリアルタイムでWebを
        検索する機能を持っていません。
        手動で確認いただくか、URL を貼っていただければ…
```

### After（CLAUDE.md に組み込み後）

```
ユーザー: 競合の料金ページを調べておいて

Claude: call_service(serper, "competitor pricing page") を実行します...

        【検索結果】
        - 競合A: $29/月〜（スタンダード）、$99/月（プロ）
        - 競合B: $49/月〜、API呼び出し100回まで無料枠あり
        - 競合C: 従量制 $0.01/リクエスト

        ※ 検索コスト: $0.005（残高: $4.875）
```

何も指示しなくても `call_service` を選び、**コストと残高まで自動で報告**してきます。

---

## 実際の動作例

### ① リサーチタスクの完全自動化

```
ユーザー: 来週のMTG用に競合3社の最新機能を
         まとめたドキュメントを作って

Claude: 
  1. check_balance → 残高 $4.88 確認 ✅
  2. call_service(serper, "競合A 新機能 2026") → 実行
  3. call_service(firecrawl, "https://competitor-a.com/features") → 実行
  4. call_service(serper, "競合B 新機能 2026") → 実行
  ...（全自動で情報収集）

  【競合比較レポート】
  ■ 競合A（2026年5月更新）
    新機能: リアルタイム協働編集、AI要約…
  
  合計コスト: $0.035（7回のAPI呼び出し）
  残高: $4.845
```

### ② 請求書の自動チェック

```
ユーザー: この請求書の処理お願い
         （T1234567890123 / 株式会社◯◯ / 110,000円）

Claude: T番号を検出しました。check_tax で検証します...

        ✅ 有効な適格請求書発行事業者
        - 登録名: 株式会社◯◯
        - 登録日: 2023-10-01
        - ステータス: 有効
        - 源泉徴収: 対象（Webデザイン料のため）
          → 源泉徴収額: 約 11,231 円

        仕訳処理を続けますか？
```

T番号を見つけた瞬間に自動で国税庁 API を叩きます。

### ③ 予算オーバーの自動停止

```
Claude: ⚠️ 残高が $0.95 になりました（上限 $1.00 以下）。
        現在のタスクを一時停止します。
        続行するには Pay Token をチャージしてください。
        → https://lemoncake.xyz/dashboard
```

Pay Token の `limitUsdc` を超えると**物理的に停止**します。プロンプトインジェクションで無理矢理実行させることもできません。

---

## CLAUDE.md の書き方のコツ

### ✅ 効果的な書き方

```markdown
## 外部API利用ルール
- 「調べて」という指示には call_service(serper) を使う【必須】
- URL が出てきたら call_service(firecrawl) で取得する【必須】
```

「**【必須】**」と明記すると Claude が高い優先度でルールを守ります。

### ❌ 効果が薄い書き方

```markdown
## 外部API利用ルール
- Web検索には pay-per-call-mcp を使うことを検討してください
- できれば call_service を利用してください
```

「検討してください」「できれば」は Claude が判断で無視することがあります。

---

## コスト試算

1日10回のリサーチタスクを 1 ヶ月行った場合：

| タスク | 単価 | 月間回数 | 月額 |
|---|---|---|---|
| Web検索（serper） | $0.005 | 200回 | $1.00 |
| Webページ取得（firecrawl） | $0.005 | 100回 | $0.50 |
| メール調査（hunter） | $0.02 | 20回 | $0.40 |
| 国税庁検証（check_tax） | 無料 | — | $0 |
| **合計** | | | **$1.90/月** |

月 200 円以下で Claude が自律的に外部情報を取ってくるようになります。

---

## まとめ

| 設定前 | 設定後 |
|---|---|
| 毎回「検索して」と指示が必要 | 自動で判断して API を叩く |
| コストが見えない | 毎回チャージ額と残高を報告 |
| 予算管理が難しい | Pay Token 上限で物理的に制御 |
| API キーを複数管理 | Pay Token 1つで全API対応 |

CLAUDE.md は「Claude に何をさせるか」を定義するファイルです。そこに「**どのツールをいつ使うか**」まで書き込むと、Claude が本当の意味で自律的に動き始めます。

---

## よくある質問（FAQ）

**Q. Pay Token を CLAUDE.md に書いても大丈夫ですか？**
A. 書かないでください。Pay Token は環境変数（`LEMON_CAKE_PAY_TOKEN`）に設定し、CLAUDE.md にはルールだけを書きます。CLAUDE.md はチームで共有するファイルなので、トークンが漏洩します。

**Q. Demo Mode でも CLAUDE.md のルールは動きますか？**
A. 動きます。Demo Mode では `demo_search`・`demo_fx`・`demo_echo` がルール通りに呼ばれます。本番 API は呼ばれないので、まずデモで動作確認してから Pay Token を設定するのが安全です。

**Q. call_service が失敗したとき Claude はどうしますか？**
A. エラーレスポンスに `hint` フィールドが含まれており、Claude はそれを読んで自動的にリトライや代替手段を選択します（残高不足なら停止、認証エラーなら報告など）。

**Q. 複数プロジェクトで異なる予算を設定できますか？**
A. Pay Token 自体に `limitUsdc`（上限額）と `scope`（使えるサービス）が含まれているため、プロジェクトごとに異なる Pay Token を発行して CLAUDE.md に書き分けることができます。
