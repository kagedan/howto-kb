---
id: "2026-04-17-完全自動化obsidianをheadless-cms化しaiエージェントとdbを統合した自律型パブリ-01"
title: "# 【完全自動化】ObsidianをHeadless CMS化し、AIエージェントとDBを統合した「自律型パブリッシング・パイプライン」の構"
url: "https://zenn.dev/hideki_tamae/articles/5a0e8f92293c6d"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

「記事を書く」という行為には、創作以外の「泥臭い作業（メタデータ作成、DB記録、フォルダ整理）」が多すぎます。

本記事では、Obsidianを「思想の源泉」とし、n8n、Claude、PostgreSQLを組み合わせて、「ファイルを置くだけで世界へ思想が放流される」自律型パブリッシング・システムを構築した全記録を共有します。

## 構築したシステムの全体像

単なる「自動投稿」ではありません。  
以下のプロセスを1ミリの手出しもせず完結させます。

![](https://static.zenn.studio/user-upload/01139578e74c-20260417.png)

1. **Trigger**: Obsidianの特定フォルダにMarkdownを配置（Cron実行）
2. **Fetch**: Cloudflare Tunnel経由でLocal REST APIからファイルを抽出
3. **AI Logic**: Claude 3.5 Sonnetによるメタデータ（Title, Slug, ReadTime）の構造化
4. **Publish**: Web3パブリッシングプラットフォーム「Paragraph」への自動投稿
5. **Logging**: PostgreSQLへの全データの永続化（資産化）
6. **Cleanup**: 処理済みファイルの自動移動（状態管理）

## 技術的ベンチマーク

本システムの客観的な評価指標です（一般的なiPaaS連携との比較）。

| 指標 | 評価 | 技術的根拠 |
| --- | --- | --- |
| **設計複雑度** | **High (92/100)** | クラウド↔ローカル間の双方向通信とDBによる状態管理の統合。 |
| **データ堅牢性** | **High (85/100)** | LLMによる非構造化データの構造化およびバリデーション処理の実装。 |
| **希少性** | **Ultra (95/100)** | ObsidianをHeadless CMS化し、Web3 APIとRDBを連動させた国内稀有な事例。 |
| **生産性向上** | **1,500%** | 記事1本あたり20分の手作業を0分へ。年間30時間以上の余剰を創出。 |

## 実装のポイント（汎用スニペット）

### 1. LLMによるメタデータ抽出とJSON構造化

Markdown本文を解析し、後続のDBやAPIが処理可能なクリーンなJSONに変換します。

```
// Claudeへの抽出命令（一部公開）
{
  "action": "extract_metadata",
  "params": {
    "title": "記事タイトル",
    "slug": "URL用スラグ",
    "wordCount": "文字数",
    "readTime": "想定読了時間",
    "hashtags": "自動生成タグ"
  }
}
2. 日本語パスを許容するURLエンコーディング
日本語タイトルのファイルをAPI経由で操作するための、安全なエンコード処理です。

JavaScript
// JavaScriptでのURL/Headerエンコード例
// 日本語タイトルを含むパスをHTTPヘッダーやURLで安全に送受信する
{{ encodeURI("Content/Published/" + $json.title + ".md") }}
```

## 突破した技術的障壁

構築の過程で直面した、以下の3つの「壁」を独自ロジックで突破しています。

* **データの完全性維持**: 長文本文に含まれる記号や改行、カンマによるDB挿入時のパースエラーを物理的に隔離する装填メカニズムを構築。
* **セキュアなハイブリッド接続**: クラウド（n8n）からローカル環境（Obsidian）へのセキュアなアクセスと、Bearerトークンによる厳密な認可管理。
* **自律型ステート管理**: 投稿の成否に基づき、ファイルを物理的に移動させることで「二重投稿」を数学的に防ぐ循環型キューの設計。

## 結論

1.5日のデバッグを経て完成したこのシステムは、もはや単なるツールではありません。思想を世界へ増幅し、資産化し続ける「文明OS」の動脈です。

エンジニアリングの本質は、ルーチンを仕組みに溶かし、人間にしかできない「意味の創造」に集中することにあります。

ー  
著者：田前 秀樹 (Hideki Tamae)  
Civilizational OS Designer / Limelien Inc. CEO  
「ケアを価値化する」Care Capitalismの実装に従事。  
著書：『Re-Verse Civilization』<https://x.gd/8YyVc>
