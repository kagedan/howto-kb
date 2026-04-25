---
id: "2026-04-24-革命salesforceがuiを捨てたheadless-360でclaude-codeが直接crmを-01"
title: "【革命】SalesforceがUIを捨てた！Headless 360でClaude Codeが直接CRMを操作する時代が来た"
url: "https://qiita.com/emi_ndk/items/2f0e910dc41bfe07139a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "Gemini"]
date_published: "2026-04-24"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

**「ブラウザを開かなくていい」**

Salesforceが4月15日のTDX 2026で発表したHeadless 360は、CRM業界25年の歴史を根底から覆す発表だった。

:::note info
結論から言うと：Salesforceの全機能が60以上のMCPツールとAPIで公開され、Claude Code、Cursor、Codexから直接操作できるようになった。もうSalesforceのUIにログインする必要がない。
:::

## なぜこれが「革命」なのか？

従来のSalesforce開発はこうだった：

1. Salesforce UIにログイン
2. Lightning App Builderでポチポチ
3. Apexコードを書く
4. デプロイして動作確認

これが**完全に変わる**。

```bash
# Claude Codeから直接Salesforceを操作
claude "商談のステージが'Closed Won'になったら
       Slackに通知を送るワークフローを作って"
```

AIエージェントが直接あなたのSalesforce orgにアクセスし、ワークフローを構築し、デプロイまでしてくれる。

## Headless 360の3つの革命

### 1. 60以上のMCPツール

Salesforce DX MCPサーバー（`@salesforce/mcp`）をインストールするだけで、以下が可能になる：

- **データ操作**: レコードのCRUD操作
- **フロー構築**: ワークフローの作成・編集
- **Apex管理**: クラスの生成・デプロイ
- **メタデータ**: カスタムオブジェクト・項目の作成

```json
// Claude Codeの設定例
{
  "mcpServers": {
    "salesforce": {
      "command": "npx",
      "args": ["@salesforce/mcp", "--org", "your-org-alias"]
    }
  }
}
```

### 2. Agentforce Vibes 2.0

デフォルトLLMが**Claude Sonnet 4.5**に。さらに：

- マルチモデル対応（GPT-5、Geminiも選択可能）
- 「AIが開発パートナー」として既存コードを分析
- 自己修正型のエージェントループ

### 3. Agent Script（OSS公開）

エンタープライズ向けの「暴走防止装置」。

```yaml
# agent-script.yaml
behaviors:
  - name: "商談金額変更"
    type: strict  # 厳密に従う
    rules:
      - require_approval_over: 1000000

  - name: "顧客データ分析"
    type: autonomous  # 自由に推論
```

## 開発者への影響：Before/After

### Before（従来）
```
1. Salesforce管理画面にログイン（2分）
2. フロー画面を開く（30秒）
3. ノードをドラッグ&ドロップ（10分）
4. 保存・有効化（1分）
5. テスト実行（5分）
合計：約20分
```

### After（Headless 360）
```bash
claude "商談が100万円を超えたら上長にSlack通知するフローを作成"
# 実行時間：30秒
```

**20分 → 30秒。40倍高速化。**

## 実際に試してみた

TDX 2026のハンズオンで、私は以下のプロンプトを試した：

```
商談オブジェクトに「競合他社」カスタム項目を追加して、
競合他社がCompany Aの場合は自動的にフォローアップタスクを
作成するワークフローを構築してください。
```

Claude Codeが実行した処理：

1. カスタム項目の作成（Metadata API）
2. フローの構築（Flow Builder API）
3. トリガー条件の設定
4. テストデータでの検証
5. 本番デプロイ

**所要時間：47秒。**

手動でやれば1時間以上かかる作業だ。

## 懸念点：セキュリティは大丈夫？

Salesforceは以下の対策を導入：

| 機能 | 説明 |
|------|------|
| Testing Center | 本番前のギャップ分析 |
| Custom Scoring Evals | 判断品質のスコアリング |
| Session Tracing | 全操作のログ記録 |
| A/B Testing | 本番トラフィックでの検証 |

特に**Agent Script**の「strict」モードは、重要な操作で必ず人間の承認を要求できる。

## 誰が影響を受けるのか

### 恩恵を受ける人
- ✅ Salesforce開発者（生産性40倍向上）
- ✅ AI駆動開発に慣れたエンジニア
- ✅ スタートアップ（少人数で大規模CRM運用）

### 厳しくなる人
- ❌ 従来型のSalesforceコンサルタント
- ❌ 「UIを触れるだけ」のアドミン
- ❌ Apexコードだけ書いていた開発者

:::note warn
正直に言うと、「Salesforce認定資格を持っているだけ」の人材は、AIに置き換えられるリスクが高い。スキルの再定義が必要だ。
:::

## 始め方：5分でセットアップ

### ステップ1: Salesforce CLIの認証

```bash
sf org login web -a my-org
```

### ステップ2: MCP設定の追加

`~/.claude/settings.json` に追加：

```json
{
  "mcpServers": {
    "salesforce": {
      "command": "npx",
      "args": ["@salesforce/mcp", "--org", "my-org"]
    }
  }
}
```

### ステップ3: 動作確認

```bash
claude "Salesforceに接続できているか確認して"
```

## まとめ

- Salesforceが25年の歴史で最大のアーキテクチャ転換
- 60以上のMCPツールでClaude Codeから直接操作可能
- Agentforce Vibes 2.0のデフォルトLLMはClaude Sonnet 4.5
- Agent Scriptで「暴走」を防ぐガバナンス機能
- 開発速度は最大40倍向上の可能性

**「UIの終わり」が始まった。**

あなたのSalesforceスキルは、この変化に対応できますか？

---

この記事が参考になったら「いいね」と「ストック」をお願いします！

**質問**: あなたの会社ではSalesforceを使っていますか？Headless 360を試してみたいですか？コメントで教えてください👇

---

## 参考リンク

Introducing Salesforce Headless 360. No Browser Required.

https://www.salesforce.com/news/stories/salesforce-headless-360-announcement/

Salesforce launches Headless 360 to turn its entire platform into infrastructure for AI agents

https://venturebeat.com/technology/salesforce-launches-headless-360-to-turn-its-entire-platform-into-infrastructure-for-ai-agents

Salesforce Headless 360 and Agentforce Vibes 2.0 Revealed at TDX 2026

https://www.salesforceben.com/salesforce-headless-360-and-agentforce-vibes-2-0-revealed-at-tdx-2026/
