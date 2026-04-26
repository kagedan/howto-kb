---
id: "2026-04-25-緊急mcpの仕様ですが20万台のaiサーバーを危険に晒している-anthropic社の衝撃回答-01"
title: "【緊急】MCPの「仕様です」が20万台のAIサーバーを危険に晒している - Anthropic社の衝撃回答"
url: "https://qiita.com/emi_ndk/items/90fc30a9970776055602"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "qiita"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

## 結論から言うと

**Anthropic社が開発したMCP（Model Context Protocol）に、任意コマンド実行（RCE）を可能にする「設計上の欠陥」が発見された。**

影響範囲は？

- 20万台以上のAIサーバー
- 1.5億回以上のダウンロード
- 7,000以上の公開サーバー
- LiteLLM、LangChain、IBM LangFlowなど主要AIフレームワーク

そしてAnthropicの回答は...

**「仕様です」**

え？

## 何が起きているのか

セキュリティ企業OX Securityが4月に公開した調査で、MCPのコアアーキテクチャに重大な脆弱性が存在することが判明した。

:::note alert
この脆弱性は「バグ」ではなく「設計上の仕様」として実装されている。つまり、パッチで修正される可能性が低い。
:::

### MCPのSTDIO問題とは

MCPはAIエージェントと外部ツールを接続するための標準プロトコル。Claude Code、Cursor、Windsurf、そして数多くのAIフレームワークで採用されている。

問題はSTDIO（標準入出力）トランスポートの実装にある。

```python
# MCPのSTDIO実装の簡略化例
# 設定からコマンドを直接実行してしまう

def start_server(config):
    command = config.get("command")  # ユーザー入力
    subprocess.Popen(command, shell=True)  # そのまま実行！
```

OX Securityの調査によると：

> MCPのSTDIOインターフェースは、設定から直接コマンド実行への道を提供する。コマンドが与えられると、STDIOサーバーの作成に成功すればハンドルを返し、異なるコマンドの場合はコマンド実行後にエラーを返す。

つまり、**どんなコマンドでも一度は実行される**。

## 攻撃ベクターは4種類

OX Securityは4つの攻撃経路を特定した：

### 1. UIインジェクション
主要AIフレームワークのUIに、認証なしで悪意あるコードを注入

### 2. ゼロクリック・プロンプトインジェクション
WindsurfやCursorなどのAI IDEに対して、ユーザーの操作なしで攻撃可能

### 3. マーケットプレイス汚染
11のMCPレジストリのうち9つに、悪意あるパッケージの配布に成功

### 4. サプライチェーン攻撃
MCPを使用する下流プロジェクト全てに影響が波及

## 実際に攻撃が成功したプラットフォーム

OX Securityは6つの本番プラットフォームでコマンド実行に成功したと報告：

| プラットフォーム | 深刻度 | 影響 |
|:---|:---|:---|
| LiteLLM | 致命的 | APIキー、データベース流出 |
| LangChain | 致命的 | 全システム乗っ取り |
| IBM LangFlow | 致命的 | エンタープライズ環境への侵入 |
| LibreChat | 高 | チャット履歴・ユーザーデータ流出 |
| WeKnora | 高 | RCE |
| Cursor | 高 | 開発環境の完全制御 |

## 関連するCVE一覧

この設計上の欠陥を起点として、複数のCVEが発行されている：

```
CVE-2026-30623 - LiteLLM コマンドインジェクション
CVE-2026-22252 - LibreChat RCE
CVE-2026-22688 - WeKnora RCE
CVE-2025-49596 - MCP Inspector
CVE-2025-54994 - @akoskm/create-mcp-server-stdio
CVE-2025-54136 - Cursor
```

## Anthropic社の衝撃的な回答

OX Securityは、プロトコルレベルでの修正をAnthropicに提案した。これが適用されれば、下流の数百万ユーザーを即座に保護できるはずだった。

Anthropicの回答：

> STDIOの実行モデルは安全なデフォルトを表しており、サニタイゼーションは開発者の責任である。

翻訳すると：

**「私たちのプロトコルは安全です。使う側が気をつけてください。」**

:::note
これは「設計上の問題ではなく、実装者の責任」という立場。しかし、実際には多くの主要プロジェクトがこの「仕様」に引っかかっている。
:::

## なぜこれが深刻なのか

### 1. MCPは事実上の標準になりつつある

2026年3月時点で9,700万回以上のインストール。Claude Code、Cursor、Windsurf、そして多くのエンタープライズツールが採用している。

### 2. 修正の見込みがない

「仕様」である以上、Anthropicがプロトコル自体を変更しない限り、この問題は永続する。

### 3. 開発者への責任転嫁

「サニタイゼーションは開発者の責任」という回答は、セキュリティ・バイ・デフォルトの原則に反する。

## 今すぐ確認すべきこと

MCPを使用している場合、以下を確認してほしい：

### 1. バージョンの確認

```bash
# MCPサーバーのバージョンを確認
npm list @modelcontextprotocol/sdk
# または
pip show mcp
```

### 2. 設定の監査

MCPサーバーの設定ファイルで、外部から入力される可能性のある値がないか確認。

```json
// 危険な例
{
  "command": "${USER_INPUT}",  // 外部入力を直接使用
  "args": ["--config", "${CONFIG_PATH}"]
}
```

### 3. ネットワーク分離

MCPサーバーは可能な限りネットワークから分離し、必要最小限の権限で実行する。

### 4. 入力のサニタイズ

全ての外部入力を厳密にバリデーションする：

```python
import shlex
import re

def sanitize_command(user_input: str) -> str:
    # ホワイトリスト方式でコマンドを制限
    allowed_commands = ["list", "search", "read"]
    if user_input not in allowed_commands:
        raise ValueError("Invalid command")
    return user_input
```

## 他に影響を受けているもの

同時期に報告されている関連する脆弱性：

### Flowise AI - CVSS 10.0（最大深刻度）

CVE-2025-59528として、FlowiseのCustomMCPノードにRCE脆弱性が発見された。12,000〜15,000のインターネット公開インスタンスが影響を受け、DeloitteやAWSなどのFortune 500企業も使用している。

2026年4月7日から積極的な悪用が検出されている。

### LangChain - データ流出

CVE-2026-41481として、HTMLHeaderTextSplitter.split_text_from_url()メソッドにデータ流出の脆弱性。

## AIエージェント時代のセキュリティパラダイム

この問題は、AIエージェント時代における新しいセキュリティ課題を浮き彫りにしている：

1. **プロトコルレベルの脆弱性**：個々のアプリではなく、標準プロトコル自体に問題がある

2. **サプライチェーンの連鎖**：1つの脆弱性が数百万のシステムに波及

3. **「仕様」という逃げ道**：設計上の決定がセキュリティホールになっても、責任の所在が曖昧

## まとめ

- MCPのSTDIOトランスポートに設計上のRCE脆弱性が存在
- 20万台以上のサーバー、1.5億回以上のダウンロードが影響
- Anthropicは「仕様」として修正を拒否
- 開発者は自己防衛が必要

:::note
MCPを使用している全ての開発者は、今すぐ自分の実装を監査してほしい。「上流が安全」という前提は、もう成り立たない。
:::

## 参考リンク

The Mother of All AI Supply Chains: Critical, Systemic Vulnerability at the Core of Anthropic's MCP

https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/

Anthropic MCP Design Vulnerability Enables RCE, Threatening AI Supply Chain

https://thehackernews.com/2026/04/anthropic-mcp-design-vulnerability.html

MCP STDIO Command Injection: Full Vulnerability Advisory

https://www.ox.security/blog/mcp-supply-chain-advisory-rce-vulnerabilities-across-the-ai-ecosystem/

Flaw in Anthropic's MCP putting 200k servers at risk, researchers claim

https://www.theregister.com/2026/04/16/anthropic_mcp_design_flaw/

Flowise AI Agent Builder Under Active CVSS 10.0 RCE Exploitation

https://thehackernews.com/2026/04/flowise-ai-agent-builder-under-active.html

---

この記事が参考になったら、いいねとストックをお願いします！

**質問**：あなたのプロジェクトでMCPを使っていますか？セキュリティ対策はどうしていますか？コメントで教えてください。
