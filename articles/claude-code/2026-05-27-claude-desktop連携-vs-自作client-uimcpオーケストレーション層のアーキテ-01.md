---
id: "2026-05-27-claude-desktop連携-vs-自作client-uimcpオーケストレーション層のアーキテ-01"
title: "Claude Desktop連携 vs 自作Client UI：MCPオーケストレーション層のアーキテクチャと実装のトレードオフ"
url: "https://qiita.com/jjking/items/5008c6b66ec95c85e690"
source: "qiita"
category: "claude-code"
tags: ["MCP", "LLM", "Python", "qiita"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

## AIエージェント時代におけるインターフェースの選択肢

LLMの社会実装が急速に進む中、AIを単なる「ツール」ではなく、外部システムと相互作用する「エコシステム」として捉える視点が不可欠になっています。Anthropicが提唱する「Model Context Protocol（MCP）」は、LLMと外部データソースやツールをシームレスに接続するオープン規格として急速に支持を集めています。

しかし、開発現場では一つの大きな設計判断に直面します。それは、**「作成したMCPサーバーを既存のClaude Desktopに統合すべきか、それとも独自のClient UIを構築すべきか」**という問いです。

本記事では、このMCPオーケストレーション層におけるアーキテクチャの選択肢と、それぞれのトレードオフを深掘りします。

---

## MCPオーケストレーションの内部シーケンス：DiscoveryからExecutionへ

MCPの核心は、JSON-RPC 2.0をベースにしたプロトコル層にあります。ClientとServerの間でどのようなやり取りが行われているのか、その内部シーケンスを理解することが設計判断の第一歩です。

プロトコルの動作は、大きく分けて以下の2つのフェーズに分類されます。

### 1. Discovery（接続と初期化）
Clientが起動すると、指定されたServerプロセスを起動し、双方向のストリーム（標準入出力など）を確立します。その後、Clientは `initialize` リクエストを送信し、Serverは自身が提供可能な「Tools（ツール）」や「Resources（リソース）」の一覧を返します。これにより、ClientはServerの「能力」を事前に把握します。

### 2. Execution（実行）
ユーザーがメッセージを入力すると、Client（または背後のLLM）はどのツールを呼び出すべきかを判断します。Clientは `tools/call` メソッドを用いて、必要な引数とともにServerへリクエストを送信します。Serverは処理を実行し、結果をClientに返却します。

この一連の流れ（オーケストレーション層）を、既存の「Claude Desktop」に委ねるのか、それとも「自作のClient」で完全に制御するのかが、アーキテクチャの分岐点となります。

---

## 解決策の提示：2つのアプローチと実装ロードマップ

開発者が選択できるアプローチは、大きく分けて2つあります。

### アプローチA：Claude Desktop連携（Host統合型）

既存の「Claude Desktop」をホスト層として利用する場合、開発者は独自のUIを用意する必要がありません。設定ファイルを記述するだけで、強力なLLM推論と洗練されたUIを即座に利用できます。

#### 実装手順：claude_desktop_config.json の設定

Windows（`%APPDATA%/Claude/claude_desktop_config.json`）またはmacOS（`~/Library/Application Support/Claude/claude_desktop_config.json`）に、以下のようにサーバーの起動パラメーターを指定します。

```json
{
  "mcpServers": {
    "my-custom-tool": {
      "command": "node",
      "args": [
        "/path/to/my-server/index.js"
      ]
    }
  }
}
```

この設定により、Claude Desktopの起動時に自動的にMCPサーバーが立ち上がり、チャット画面からツールを直接呼び出せるようになります。

### アプローチB：自作Client UI（カスタムオーケストレーション型）

ビジネス要件によっては、機密データのローカル処理や、独自の業務システムに特化したUIが必要になります。この場合、MCP SDKを用いてクライアント層を自ら構築します。

#### 具体的な実装コード例（Python）

以下は、Python用の `mcp` SDKを使用して、MCPサーバーと対話する最小限のカスタムクライアントの実装例です。

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    # 接続するMCPサーバーの起動パラメーターを定義
    server_params = StdioServerParameters(
        command="node",
        args=["/path/to/my-server/index.js"]
    )
    
    # サーバーとの接続を確立
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 1. 初期化 (Discoveryフェーズ)
            await session.initialize()
            
            # 2. サーバーが提供するツール一覧の取得
            tools = await session.list_tools()
            print("利用可能なツール:", tools)
            
            # 3. ツールの実行 (Executionフェーズ)
            # 実際には、ここでLLMからの指示に基づいて引数を動的に決定します
            # response = await session.call_tool("tool_name", arguments={"param": "value"})

if __name__ == "__main__":
    asyncio.run(run_client())
```

このコードを実行することで、プログラムから直接MCPサーバーを制御し、結果を独自のシステムに統合することが可能になります。

---

## アーキテクチャのトレードオフ：設計判断の「Why」を解き明かす

これら2つのアプローチの選択基準は、単なる「開発スピード」ではなく、システムが目指す**「自律性のスコープ」**にあります。

### Claude Desktop連携の評価
*   **メリット**：UI開発コストが完全にゼロ。Anthropicが提供する高度なUX、コンテキスト管理、安全設計をそのまま享受できます。
*   **デメリット**：画面レイアウトのカスタマイズが不可能。また、自社の基幹システムや特定の社内ポータルにAIを埋め込みたい場合、この方法は採用できません。

### 自作Client UIの評価
*   **メリット**：UI/UXの完全なコントロール。LangChainやLlamaIndexなどの外部オーケストレーションフレームワークと容易に組み合わせられ、プロンプトインジェクションに対する独自のフィルタリング層を挿入することも可能です。
*   **デメリット**：チャットUI、対話履歴の管理、LLMへのコンテキスト注入、エラーハンドリングなど、アプリケーションとして動作させるための開発コストが大幅に増加します。

---

## 技術選定における意思決定の指針

システム設計における古典的な名著『人月の神話』でも語られているように、ソフトウェア開発においては「概念の一貫性」が最も重要です。

新規のアイデアを素早く検証したいフェーズ（PoC）においては、**Claude Desktop連携**を選択し、検証のサイクルを最速で回すべきです。

一方で、セキュリティポリシーによって外部クラウドへのデータ露出が制限されている場合や、特定の業務フローに最適化された専用ワークフロー（エージェント）を社内へ広く展開したい場合は、初期コストを支払ってでも**自作Client UI**を構築することが、中長期的なビジネス価値の最大化に繋がります。
