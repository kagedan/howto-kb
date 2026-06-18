---
id: "2026-06-18-k-koga555-アンソロピックがリリースした金融サービスをcodexやopenclawherme-01"
title: "@k_koga555: # アンソロピックがリリースした金融サービスをCodexや、OpenClaw・Hermesで利用する 有効活用しなきゃ"
url: "https://x.com/k_koga555/status/2067405730899186047"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "GPT"]
date_published: "2026-06-18"
date_collected: "2026-06-18"
summary_by: "auto-x"
query: "Cowork スケジュール OR Cowork スキル作成 OR Cowork 自動化"
---

# アンソロピックがリリースした金融サービスをCodexや、OpenClaw・Hermesで利用する

有効活用しなきゃね #Codex #Claude #Hermes #OpenClaw

「Anthropicは **Claude for Financial Services** という公式GitHubリポジトリを公開しています。  
対象は投資銀行、株式リサーチ、PE、ウェルスマネジメントなどの金融ワークフローです。

GitHub上の説明でも、以下のようなワークフローに対応するプラグイン／エージェントが並んでいます。

- DCFモデル
- LBOモデル
- 3-statementモデル
- Comps分析
- CIM作成
- ICメモ作成
- KYCチェック
- GL照合
- NAV tie-out」

Codex, OpenClaw・Hermesでの利用をGPT5.5に問うた(以下、md記述）

---------
# Claude for Financial Services は Codex / OpenClaw / Hermes でも使えるか

## 結論

**Codexでは「そのまま1行インストール」は基本不可です。**  
ただし、かなり実用的に移植可能です。

**OpenClaw / Hermes でも可能性は高い**ですが、こちらも **Claude用プラグインをそのまま読むのではなく、Skill / MCP / Agent設定として移植する形**になります。

---

## 1. Codexで使えるか

### 判定：可能。ただし「Claude用プラグインとして」は使えない

Anthropicの金融サービスリポジトリは、公式には **Claude Cowork / Claude Code / Claude Managed Agents API** 向けです。  
Anthropic公式は、同じエージェント・スキルを「Claude Cowork plugin」または「Claude Managed Agents API」で使えると説明しています。  
さらにAnthropicの発表では、金融向けテンプレートは **Claude Cowork と Claude Code のプラグイン**として提供されるとされています。

一方、CodexはOpenAI側のコーディングエージェントで、ローカルのコード読み書き・実行、MCPサーバー接続、スキル利用ができます。  
OpenAI公式ドキュメントでは、Codex CLIはローカルで動くコーディングエージェントで、選択ディレクトリ内のコードを読んだり変更・実行したりできると説明されています。  
また、CodexはCLIとIDE拡張の両方でMCPサーバーをサポートします。

したがって、Codexでの現実的な使い方は次です。

| 方式 | 可否 | コメント |
|---|---:|---|
| Claude CodeプラグインをCodexにそのままインストール | × | `.claude-plugin` 形式はClaude用 |
| `skills/` の中身をCodex Skillとして移植 | ○ | かなり現実的 |
| `.mcp.json` やMCPコネクタ設定をCodexのMCP設定に移植 | ○ | APIキー・契約は別途必要 |
| DCF/LBO/CompsなどのワークフローをCodexに実行させる | ○ | Python/Excel生成・テンプレート化に向く |
| Bloomberg / FactSet / PitchBook等を無料で使う | × | データ契約・APIキーが必要 |

つまり、**Claude用の金融スキルをCodex用Skillに書き換える**のが本筋です。

---

## 2. Codexで何ができるか

Codexに向いているのは、特に以下です。

- DCFモデルのPython / Excelテンプレート生成
- LBOモデルの構造作成
- 3-statementモデルの雛形作成
- Comps分析用の表・計算ロジック作成
- 決算資料PDFやCSVを読ませた分析
- ICメモ、CIM、株式調査レポートのドラフト作成
- KYCチェックリスト作成
- GL照合・NAV照合のPythonスクリプト作成
- MCP経由で外部APIや社内データへ接続

特にCodexは「コードを書く・修正する・テストする」側が強いため、**金融分析の再現可能なワークフロー化**に向いています。

たとえば、Codexに以下のようなSkillを作れます。

```text
financial-modeling/
  SKIL
