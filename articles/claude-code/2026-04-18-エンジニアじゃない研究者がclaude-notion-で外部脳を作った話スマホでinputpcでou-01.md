---
id: "2026-04-18-エンジニアじゃない研究者がclaude-notion-で外部脳を作った話スマホでinputpcでou-01"
title: "エンジニアじゃない研究者がClaude × Notion で「外部脳」を作った話—スマホでINPUT・PCでOUTPUT"
url: "https://zenn.dev/kajungbang/articles/5c00f3bf7d7416"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "Python", "zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

---

## はじめに：Claude Codeの”忘却性”と日々溜まる論文や公文書

Python書いたことありません。RもSQLも書いたことありません。ただ遥か昔にSASプログラムだけは学びました（もう忘れた）。  
そんな社会科学系研究者（Marketing & Branding）は、日々刻々と変化する社会状況をキャッチアップするのに忙殺され、他の研究者の論文や著作は読もうと思っても溜まっていくばかり。どうにかこうにかAIの進化はキャッチアップをするものの、Claude Codeの”朝になる（再起動する）と今までのやりとりがすべて忘却されてしまう”問題に直面し、フラストレーションが溜まるばかり。.mdとメモリーを活用して回避すれど、次は自分自身がClaude Code外で接するさまざまな情報の共有ができてないので、壁打ちにおいて頓珍漢な回答も多いことで頭を悩ませていました。  
この”素直で地頭が非常に高いけれども、文脈（コンテキスト）を忘れ、Claude Codeリリース時の情報に固執するめちゃくちゃ頭のいいパートナー”を育て上げたい！！  
そんな時にXのタイムラインで、Andrej Karpathyさんの[CLLM Knowledge Bases](https://x.com/karpathy/status/2039805659525644595)投稿を読み、hoeemさんの[How to create your own LLM knowledge bases today (full course)](https://x.com/hooeem/status/2041196025906418094)記事を見つけました。さらにClaude Code Sudioさんの[元OpenAIの社員が実践するClaude Code×Obsidianで「AI外部脳」をゼロから作る完全ガイド](https://x.com/ClaudeCode_love/status/2042886840177557533)記事も見つけ、「これだ！！外部にナレッジ＝過去の記憶＝AI外部脳を蓄積できれば、Claude Codeが育つ」と思い、自分で作ってみようと思ったのです。

---

## 次にやったこと

「Obsidian初耳、一方でNotionは多少知っていた」そんなレベルでしたので、世の中の”Obsidian vs Notion”情報を読み漁りました。  
その結果、①複数デバイス間で使いたい　②蓄積する情報の量が今後どれぐらいになるかわからない　③初心者はNotionがよき、などの理由で、Claude＊Notionで”AI外部脳”を構築するぞ〜となったわけです。

## システムの全体像

```
スマホで論文・記事を発見（いつでもどこでも）
        ↓
Claude App → Notionに書き込む（INGEST/COMPILE）
        ↓
Pythonスクリプトでローカルに同期
        ↓
Claude Code が読んで横断参照（QUERY）
        ↓
「私の知識」で答えるAI
```

シンプルに見えますが、実はここに至るまでに紆余曲折がありました。

---

## 最初の失敗：Claude Codeに全部やらせようとした

最初の設計はとてもシンプル。「Claude CodeからNotionに直接読み書きすればいい」→ClaudeCodeくんにゴールイメージだけをお伝えして、構築をお願いしました。

**うまくいきませんでした。**

2026年4月現在、Claude CodeのNotion MCP連携にはOAuth トークンが約1時間で失効するバグがあります（[GitHub #28256](https://github.com/anthropics/claude-code/issues/28256)）。毎時間、手動で再認証が必要。これは実用に耐えられません。

ところが、最初は「制約」に見えたこの問題が、**より良い設計を生みだしたのです。**

---

## 逆転の発想：「書く」と「読む」を分ける

|  | Claude App（スマホ/デスクトップ） | Claude Code（ターミナル） |
| --- | --- | --- |
| **得意なこと** | Notion MCP安定、自然な会話、常にポケットの中 | ファイル横断参照、コーディング、100本超の文書を一気に読む |
| **苦手なこと** | ファイルシステム、スクリプト実行 | Notion MCP不安定、ターミナル必須 |
| **担当** | INGEST / COMPILE（Notionに書き込む） | QUERY（読んで合成する） |

**Claude Appはキュレーター、Claude Codeはアナリスト。**

この役割分担が決まったとき、システムが一気にクリアになりました。

---

## 今の私の使い方

### 移動中にスマホから

面白い論文を見つけたら、Claude Appに一言。

> 「この論文をNotionのKnowledge DBに追加して、Wiki化もして」

Claudeが内容を読んで評価し、Notionに構造化して保存する。PCを開く前に、知識が外部脳に格納されています。

### PCのClaude Code（ターミナル）を立ち上げると

```
python3 ~/scripts/sync_notion_kb.py
```

これだけで、スマホで溜めた知識がローカルに同期される。あとは自然に聞くだけ。

> 「質的研究のデータ飽和について、私のKBは何を言ってる？」

Claude Codeが wiki フォルダを横断参照して、**私自身が読んできた文献に基づいた**答えを返してくれます。

---

## 3層のアーキテクチャ

| レイヤー | 場所 | 役割 |
| --- | --- | --- |
| **Raw** | Notion: Raw Sources DB | 原典。AIが勝手に書き換えない |
| **Wiki** | Notion: Wiki DB | AI生成のサマリー・概念記事・統合知 |
| **Schema** | SCHEMA.md | AIの読み書きのルールを定義 |

Rawレイヤーは「触らない」が鉄則です。AIが要約・解釈するのはWikiレイヤーだけ。原典の完全性を保ちながら、知識を構造化できます。

---

## Claude.mdへのルーチン追加が地味に効く

Claude Codeの `~/.claude/CLAUDE.md` に以下を追加しました。

```
## External Brain (Notion KB)
- セッション開始時に ~/notion_kb/INDEX.md の同期タイムスタンプを確認
- 24時間以上古ければ python3 ~/scripts/sync_notion_kb.py を実行
- 研究ドメインに関する質問は ~/notion_kb/wiki/ を横断参照してから回答
```

Claude Codeが立ち上がるたびに、自動的に外部脳を確認しに行く。**AIが自分から知識を取りに来る**設計です。

---

## エンジニアでなくても作ることができる理由

PythonもRもSQLも書きません。もちろんSASも不要です。やるべきことはシンプルです。

必要な作業は：

1. Notionにデータベースを2つ作る（クリック操作のみ）
2. JSONファイルのIDを書き換える（コピペ）
3. `python3 sync_notion_kb.py` を実行する（コマンド一つ）

スクリプト本体はGitHubに置いてあります。カスタマイズしたければAIに頼めばいい。

---

## GitHubで公開中

→ **[Kajungbang/claude-notion-brain](https://github.com/Kajungbang/claude-notion-brain)**

* セットアップ手順（ステップバイステップ）
* Notionデータベーススキーマのテンプレート
* 同期スクリプト一式
* SCHEMA.md テンプレート

Issues・Pull Requests歓迎です。特に、社会科学・人文系の研究者や非エンジニアの方々からのフィードバックを待っています。

---

## おわりに

「AIによる外部脳」——このチャレンジは、まだまだ続きます。  
Claude Appの記憶力も万全ではありません。これも解消したいと思っています。（実は、解消する仕組みを作ったので、それは次回書きます）  
また、今回は選択しなかったObsidianについても、オフライン完結ならではの強みがあるので、Notionとの使い分けを模索したいところです。

2022年11月にOpen AIが公開したChatGPTを触った時、そして初期のPerplexityやGeminiを触った時は全くその価値がわからず、自分がここまでAIにハマるとは思っていませんでしたが、今や、使う目的が明確になればAIは最強のパートナーであり「外部脳」です。  
その本質は、記憶の移譲や拡張ではなく、**知識の継続的な対話**にあるかもしれません。

---

*著者：傍流社会科学系研究者 /　元実務家*  
*2026年4月 スマホのClaudeアプリから執筆*
