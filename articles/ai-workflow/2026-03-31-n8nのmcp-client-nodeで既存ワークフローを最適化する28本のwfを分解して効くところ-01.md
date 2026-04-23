---
id: "2026-03-31-n8nのmcp-client-nodeで既存ワークフローを最適化する28本のwfを分解して効くところ-01"
title: "n8nのMCP Client Nodeで既存ワークフローを最適化する——28本のWFを分解して「効くところ」だけMCP化した話"
url: "https://qiita.com/murata-seiji/items/41c18cbca6508acbed5e"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

n8n v2.13でMCP Client Nodeが追加された。

「お、ついに来たか」と思って、うちの28本のワークフローを全部分解してみた。HTTP Requestノードが合計70個。こいつらのうち、どれをMCP Client Nodeに置き換えたら幸せになれるのか。

結論から言うと、**MCP化して意味があるのは6本だけだった**。残り22本は今のままでいい。

日本語の記事を探してみたが、MCP Client Nodeの基本的な使い方を紹介しているものはあっても、「既存WFを全部棚卸しして、どこにMCPを入れるべきか判断した」という記事は見つからなかった。だから書く。

## MCP Client Nodeとは何か

n8n v2.13.xで追加された`@n8n/n8n-nodes-langchain.mcpClientTool`のこと。（[公式ドキュメント](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/)）

ワークフローの中から、外部のMCPサーバーが持つツールを直接呼び出せる。AI Agentノードを経由する必要がない。stdioとSSEの両方に対応している。

似た機能として「MCP Server Trigger」がある。こちらはn8n自体をMCPサーバーとして公開する機能で、方向が逆だ。

| 機能 | やること |
| --- | --- |
| MCP Client Node | n8n → 外部MCPサーバーを呼ぶ |
| MCP Server Trigger | 外部 → n8nのWFをMCPツールとして呼ぶ |

今回の話はClient側。「n8nから外のMCPを叩く」方。

## 28本のWFを分解した

まず現状を把握するところから。全28本のワークフローに含まれるHTTP Requestノードを数えて、接続先ごとに分類した。

| 接続先 | ノード数 |
| --- | --- |
| Google News RSS | 28 |
| Chatwork API | 20 |
| Claude / Anthropic API | 6 |
| Google Sheets / OAuth | 4 |
| Gemini API | 2 |
| Reddit RSS | 2 |
| その他（Dify, ForexFactory, GAS等） | 8 |
| **合計** | **70** |

見えてきたのは、**Chatwork APIが20ノードで2位**、**RSS取得が28ノードで1位**という構造。

## 「MCP化して意味がある」の判断基準

全部MCPにすればいいって話じゃない。むしろ大半はやらない方がいい。

MCP化が効くのは、こういうケースだ。

**効く:**

* 認証付きAPIを複数WFで叩いている（APIキーの一元管理ができる）
* 1つのWFの中でCRUD操作を何本もやっている（ノード数が減る）
* エラーハンドリングが各WFでバラバラになっている

**効かない:**

* 単純なHTTP GETでデータを取っているだけ（RSS取得とか）
* 1WFに1回しか使わないAPI呼び出し
* n8nの純正ノードで十分回っているもの（Gmail、Calendarなど）

この基準で28本をA/B/Cに分けた。

## A群: MCP化の効果が高い——6本

### 1. Chatwork AI Bot

httpRequest 3本（メッセージ取得 + Claude API + 返信投稿）を使っている。Chatwork MCPに置き換えれば、API認証をWFごとに設定する手間がなくなる。

### 2. Chatworkコンタクト承認

一番ノードが多いWF。全25ノードのうち14本がChatwork API。コンタクト一覧取得→承認→ルーム招待→Sheets記録の一連の流れで、同じAPIキーを14回セットしている。これはさすがにMCP化したい。

### 3. Googleフォーム自動生成

Claude API + GAS + Chatworkの3種類のAPIを叩いている。全部MCPに寄せられるパターン。

### 4. 自発的つぶやき

VPS上の静的ファイルを取得するHTTP GET以外は、Claude APIとChatwork API。MCP化でスッキリする。

### 5. GAS自律修復

Gemini API + Chatwork。CW返信部分のMCP化で改善。

### 6. システムメッセージ自動削除

Chatwork APIのGETとDELETEだけ。シンプルなCRUDで、MCP化のコストが一番低い。**最初に試すならこれ**。

## B群: やらなくていい——8本

RSS取得系のWFが5本（Morning Intelligence, 生成AIトレンド, ビジネスモデル, SNSトレンド, 朝ヘッドライン）。

全部Google News RSSやReddit RSSをHTTP GETで取っているだけ。MCPを噛ませるメリットがない。`httpRequest`でURLを叩いてJSONをパースする。これ以上シンプルにはならない。

趣味の投資用の経済指標カレンダーも同様。ForexFactoryのJSON APIを1回GETするだけだ。

## C群: 条件次第——4本

Gemini MCPが安定したらQiita記事レビューWFを切り替えたい。あとJLWA問い合わせ回答案がDify経由になっているので、Claude MCPに統合する選択肢がある。

ただ、どちらも「今の構成で困っていない」ので急がない。

## 実装の順番

一気にやらない。段階を踏む。

**Phase 1: Chatwork MCP（効果最大）**

20ノードの削減が見込める。まずシステムメッセージ自動削除で試して、動いたらAI Bot→コンタクト承認と横展開する。

VPS上にChatwork MCPサーバーをstdioかSSEで常駐させる必要がある。ここの設定が一番のハードル。

**Phase 2: Claude API MCP**

6ノードの統合。モデル切替の一元管理とトークン使用量の可視化ができるようになる。

**Phase 3: Google系MCP（将来）**

n8nの純正ノードが優秀なので、よほどの理由がない限り後回し。

## やってみてわかったこと

28本を一通り見て思ったのは、**「認証の管理コスト」がMCP化の最大の動機になる**ということ。

うちの場合、Chatwork APIキーを複数のWFにコピペしている。1つ変更したら全WFを回って直さないといけない。これがMCP化で1箇所に集約できる。

逆に、RSS取得みたいな認証不要のHTTP GETは、MCPのオーバーヘッドが邪魔になるだけだった。

あと注意点として、MCP Client Nodeは`@n8n/n8n-nodes-langchain`パッケージの一部なので、LangChain系のノードが有効になっている必要がある。Community Editionでは最初から入っているが、カスタムインストールだと確認が必要。

## まとめ

| 指標 | 値 |
| --- | --- |
| 分析したWF | 28本 |
| HTTP Requestノード | 70個 |
| MCP化効果あり | 6本（A群） |
| MCP化不要 | 8本（B群） |
| 条件付き | 4本（C群） |
| Phase 1で削減見込み | 約20ノード |

全部MCP化するのは愚策。自分のWFを分解して、認証付きAPIが集中しているところだけ狙う。それがMCP Client Nodeの正しい使い方だと思う。

Phase 1のChatwork MCP常駐化が終わったら、続編を書く。
