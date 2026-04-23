---
id: "2026-04-13-claude-code-n8n-で企画書を知るai企画者を作る-01"
title: "Claude Code + n8n で企画書を知るAI企画者を作る"
url: "https://zenn.dev/harada_ha/articles/3a50843a793634"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## 1. なぜ作ったのか？

モバイルアプリを開発していると、繰り返しつまずく瞬間がある。

> 「この機能、ポリシーってどうなってたっけ？」

フィード投稿の通報処理基準、コメント作成条件、プロフィール編集制限 — こういったものはコードに埋め込まれておらず、Confluenceの企画ドキュメントのどこかに書いてある。だから毎回ドキュメントを漁るか、企画者にSlackで聞く必要があった。

そこで作った。**「Confluenceの企画ポリシードキュメントをもとに即答するAIチャットボット」**。開発者でも企画者でも、ブラウザひとつで使えるものとして。

結果物がn8n + Claude + Confluenceをつないだ、AI企画者チャットボットだ。

---

## 2. システム構成を一目で

| 役割 | 技術 |
| --- | --- |
| チャットUI | HTML + marked.js（ローカル実行、サーバー不要） |
| ワークフローオーケストレーション | n8n |
| ポリシードキュメントソース | Confluence（REST API v1） |
| LLM | AWS Bedrock — Claude Sonnet 4.6 |

全体の流れはこうだ。  
![n8nワークフロー全体構成](https://static.zenn.studio/user-upload/f9d14b129d70-20260413.png)

```
[ブラウザ]
    │  POST /community-planner
    ▼
[Webhook] ──▶ [Parse_Request]
                    │  messages 分割
                    ▼
         [Fetch_Confluence_Children]
                    │  REST API v1
                    ▼
              [Merge_Docs]
                    │  HTML → plain text
                    ▼
         [LLM_Community_Planner] ◀── [Claude_Bedrock]
           (Agent Node)            (AWS Bedrock)
                    │
                    ▼
           [Format_Response]
                    │  OpenAI互換フォーマット
                    ▼
         [Respond_to_Webhook]
                    │
                    ▼
              [ブラウザ]
          マークダウンレンダリング + フォローアップ質問カード
```

---

## 3. n8nワークフロー詳細

### 3-1. Webhook Node

POST `/community-planner` エンドポイントを受け取るエントリーポイントだ。リクエストボディはOpenAI API互換フォーマットをそのまま使う。

```
{
  "model": "community-planner",
  "max_tokens": 2000,
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user", "content": "フィード投稿の通報ポリシーはどうなっていますか？" }
  ]
}
```

`responseMode: responseNode` に設定して、`Respond_to_Webhook` ノードがレスポンスを直接制御するようにした。LLMの出力を加工してから返せるので便利だ。

---

### 3-2. Parse\_Request (Code Node)

`messages` 配列を分解するノードだ。核心ロジック：

```
const body = $input.item.json.body;
const messages = body.messages || [];
const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
const userText = lastUserMsg?.content || '';

// 過去の会話履歴（最後のuserを除く）
const priorHistory = messages.filter(m => m.role !== 'system').slice(0, -1);
const contextText = priorHistory
  .map(m => `[${m.role === 'user' ? 'ユーザー' : 'アシスタント'}]: ${m.content}`)
  .join('\n\n');
```

`__init__` という特殊メッセージも処理する。ページを最初に開いたときに送るトリガーで、このときLLMが推薦質問を2つ生成してカードで表示する。

![](https://static.zenn.studio/user-upload/070e3a4d8983-20260413.png)

---

### 3-3. Fetch\_Confluence\_Children (HTTP Request Node)

Confluence REST API v1で特定の親ページの配下ドキュメントをすべて取得する。

```
GET /wiki/rest/api/content/{your-page-id}/child/page?expand=body.storage&limit=50
```

n8nに登録されたBasic Auth credentialを使うので、コードに認証情報を露出させる必要がない。

この設計の核心は**ドキュメント追加 = 自動反映**だ。配下ページに新しい企画ドキュメントを追加するだけで、次のリクエストからLLMのコンテキストに自動で入る。ワークフローを別途修正する必要がない。

---

### 3-4. Merge\_Docs (Code Node)

ConfluenceはコンテンツをHTMLで保存している。LLMに渡す前にplain textに変換する必要がある。

```
let text = rawHtml
  .replace(/<[^>]+>/g, ' ')       // HTMLタグ除去
  .replace(/&amp;/g, '&')          // エンティティデコード
  .replace(/&lt;/g, '<')
  .replace(/&gt;/g, '>')
  .replace(/&nbsp;/g, ' ')
  .trim();

// ```markdown ... ``` ラッピングがあれば除去
const mdBlockMatch = text.match(/^```(?:markdown)?\s*([\s\S]*?)\s*```$/);
if (mdBlockMatch) text = mdBlockMatch[1].trim();

docsContent += `\n\n===== ${title} =====\n${text}`;
```

複数の配下ページを `===== ドキュメントタイトル =====` 形式で区切って、ひとつの文字列に結合する。

---

LLMは**AWS BedrockのClaude Sonnet 4.6**で、n8n AgentノードにLLMとして接続した。

システムプロンプト設計がこのチャットボットの核心だ。主要な原則はこうだ。

**役割宣言**

> コミュニティサービス企画ポリシー専門家。対象は企画者とAndroid/iOS開発者。

**`__init__` モード**  
初期アクセス時に推薦質問2つをJSONのみで返す。当日のConfluenceドキュメントをもとに動的に生成される。

```
{"suggestions": [
  {"tag": "通報", "text": "フィード投稿の通報処理基準はどうなっていますか？"},
  {"tag": "コメント", "text": "コメント作成条件と制限事項を教えてください"}
]}
```

**回答構造の強制**（順序厳守）:

1. ポリシー要約 — 核心を**3文以内**、数値・条件は**ボールド**
2. 条件詳細 — 分岐が2つ以上なら必ず表
3. 参考コード位置 — 明示的に聞かれたときのみ

**フォローアップ質問の自動生成**  
毎回の回答末尾に以下のJSONブロックを付けるよう指示した。

```
{"followups": [
  "通報処理後の投稿ステータスはどう変わりますか？",
  "累積通報回数の閾値はありますか？"
]}
```

プロンプトの末尾にConfluenceから取得した全ドキュメントを差し込む。

```
===== コミュニティ企画ドキュメント =====
{{ $json.connectDocs }}
```

## 実際のレスポンス結果 — 構造化された回答 + フォローアップ質問カード

### 3-6. Format\_Response (Code Node)

LLMの出力をOpenAI互換フォーマットでラッピングする。フロントエンドが `choices[0].message.content` をそのまま読む構造なので、後でLLMを交換してもフロントエンドは触らなくていい。

```
return [{
  choices: [{
    index: 0,
    message: { role: 'assistant', content: llmOutput },
    finish_reason: 'stop'
  }],
  model: 'community-planner',
  object: 'chat.completion'
}];
```

---

## 4. フロントエンド（index.html）のUX設計

![チャットボット完成画面](https://static.zenn.studio/user-upload/11d805931131-20260413.png)  
別途サーバーなしでローカルの `file://` から実行できる。n8nのレスポンスに `Access-Control-Allow-Origin: *` ヘッダーを含めてCORSの問題を解決した。

**初期推薦質問カード**  
ページロード時に `__init__` メッセージを自動送信する。LLMがその日のConfluenceドキュメントを読んで推薦質問を2つ生成し、カードで表示する。ハードコードではなく、ドキュメントの内容によって毎回変わる。

**フォローアップ質問カード**  
回答バブルの下にクリック可能なカードが表示される。クリックするとそのまま送信される。連続した会話が自然につながる。

**レスポンス解析フロー**:

* `__init__` レスポンス → ```` ```json {"suggestions": [...]}``` ```` → 推薦カードレンダリング
* 通常の回答本文 → marked.jsマークダウンレンダリング（表、ボールドなど）
* 本文内の ```` ```json {"followups": [...]}``` ```` → フォローアップ質問カードとして分離レンダリング

---

## 5. 拡張ポイントと学んだこと

### Claude Codeエージェントとの関係

同じ役割をするClaude Codeエージェントも別途作った。エージェントはローカルのスペックドキュメントを読んで、IDE内でそのままポリシーに答える。n8nチャットボットはその**チーム共有版**だ。Confluenceドキュメントをリアルタイムでfetchして、ブラウザから誰でも使えるようにしたもの。用途によって両方を使い分けている。

### 良かった点

**ドキュメント追加 = 自動反映**  
Confluenceの配下ページを追加するだけで、ワークフローの修正なしにLLMのコンテキストに即反映される。企画者がドキュメントを更新すれば、次の質問から新しい内容で答える。

**n8nのビジュアルワークフロー**  
複雑なパイプラインをノード単位で管理できる。HTTP Requestの認証、エラーハンドリングといった繰り返し作業をコードなしで処理できるのが良い。

**OpenAI互換フォーマットの維持**  
最初はAzure OpenAIで開発し、途中でAWS Bedrockに切り替えたが、フロントエンドは一行も触らなかった。

**Claudeの指示追従性能**  
表、ボールド、フォローアップ質問JSONといった構造化出力の強制を、GPT系よりも安定してこなす。プロンプト設計しながら最も体感が大きかった部分だ。

### 惜しかった点 / 改善余地

* **毎回全ドキュメントfetch**: ドキュメント数が増えるとトークンコストとレイテンシが同時に上がる。ベクトル検索（RAG）の導入を検討中だ。
* **ローカルHTML方式**: チーム全体で使うには、簡単なWebサーバーかVercelデプロイが必要になる。

---

## 6. まとめ

n8n + Claudeを組み合わせると、企画ドキュメントを知るAIをかなり素早く作れる。

核心はLLMの交換ではなかった。**プロンプト設計 + ドキュメントパイプライン構造**がすべてだ。Claudeがどれだけ優秀でも、ドキュメントをきちんと渡さなければ的外れな答えを返す。逆に構造さえ整えれば、モデルを変えてもチャットボットの品質は維持できる。

次のステップとしてRAG導入とSlackボット連携を検討中だ。
