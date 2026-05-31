---
id: "2026-05-30-youtube動画からzenn記事を自動生成するaiエージェントを作った-01"
title: "YouTube動画からZenn記事を自動生成するAIエージェントを作った"
url: "https://zenn.dev/pop365/articles/436114297d8879"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "GPT", "Python", "zenn"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

## はじめに

YouTubeで、こんな経験はありませんか？

* 動画が長くて見るのが大変、テキストで読みたい
* 動画の内容をブログ記事としてまとめたい

そこで今回は、**YouTubeのURLを入れるだけでZenn記事を自動生成するAIエージェント**を作りました。

## 作ったもの

YouTubeのURLを入力すると、以下を自動でやってくれるツールです。

1. 動画の字幕を自動取得
2. AIが内容を要約・構造化
3. Zenn用のMarkdown記事として出力

## 使った技術

* **Microsoft Agent Framework 1.7.0**（Microsoftの最新エージェントフレームワーク）
* **Azure AI Foundry**（AIモデルのデプロイ・実行環境）
* **Azure AI Projects SDK**（Foundryへの接続クライアント）
* **Azure AD認証 / Entra ID**（APIキー不要・セキュアな認証）
* **youtube-transcript-api**（字幕取得）
* **Python 3.13**

## Azure AI Foundryとは

Azure AI Foundryは、Microsoftが提供するAIモデルのデプロイ・管理プラットフォームです。

* GPT-4oやClaude等のモデルを一元管理できる
* Azure AD認証でセキュアに利用できる
* 企業のシステムとの連携が容易

今回はAzure AI Foundry上にデプロイしたGPT-4.1-miniを使って記事生成を行っています。

## Microsoft Agent Framework

今回一番こだわったのが、Microsoft Agent Frameworkの採用です。

`@tool`デコレータを使うことで、AIエージェントが自律的にツールを呼び出す仕組みを実装しました。

```
@tool
def get_youtube_transcript(url: str) -> str:
    """YouTubeの動画URLから字幕テキストを取得する。"""
    video_id = _extract_video_id(url)
    # 字幕を取得して返す
    ...
```

エージェントが「字幕を取得する必要がある」と判断したときに、自動でこのツールを呼び出します。

## セキュリティへの配慮

個人開発ではAPIキーを使いがちですが、今回は企業での実用を意識してAzure AD認証（Entra ID）を採用しました。

```
credential = DefaultAzureCredential()
project_client = AIProjectClient(endpoint=ENDPOINT, credential=credential)
```

`DefaultAzureCredential`は環境を自動判別します。

* ローカル開発 → `az login`の認証情報を使用
* 本番環境（Azure上） → マネージドIDを自動使用

コードを変えずに環境を切り替えられるのが大きなメリットです。

## 動作イメージ

$ python main.py <https://www.youtube.com/watch?v=xxxxx>  
[1/3] Azure AD認証でクライアントを初期化中...  
完了（Entra ID認証）  
[2/3] エージェントを実行中...  
[ツール] 字幕取得完了: ja / 8432 文字  
完了 - 2100 文字  
[3/3] ファイルを保存中...  
保存先: output/20260530\_224500\_xxxxxxxxxxx.md

## まとめ

Microsoft Agent FrameworkとAzure AI Foundryを組み合わせることで、  
実用的なAIエージェントをシンプルに実装できました。

ソースコードはGitHubで公開しています。

<https://github.com/pop365/youtube-to-zenn-agent>
