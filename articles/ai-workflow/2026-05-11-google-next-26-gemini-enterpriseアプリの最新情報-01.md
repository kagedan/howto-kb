---
id: "2026-05-11-google-next-26-gemini-enterpriseアプリの最新情報-01"
title: "＜Google Next '26＞ Gemini Enterpriseアプリの最新情報"
url: "https://zenn.dev/densan_techblog/articles/decd06cb9f2b7b"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "Gemini", "zenn"]
date_published: "2026-05-11"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

# はじめに

Google Cloud Next は、Google Cloudが年1回開催する、最新技術やAI戦略を発表する大規模イベントです。今年は4/22〜24（米国時間）に、ラスベガスで開催されました。

公式サイト：[**https://www.googlecloudevents.com/next-vegas**](https://www.googlecloudevents.com/next-vegas)

今年は3日間で、939件のセッションが開催され、セッションの一部はYouTubeにアーカイブがアップロードされており、現在でも視聴することができます。

本記事では、数あるセッションの中から、Gemini Enterpriseの最新機能と、製品ロードマップについて紹介された、「[What's new with Gemini Enterprise app](https://www.googlecloudevents.com/next-vegas/session-library?session_id=3913006&name=what&)」を整理してお届けします。

※本記事内の画像および内容は、Google Cloud Nextの公式セッション動画より引用・抜粋して作成しています。

セッション動画：**<https://www.youtube.com/watch?v=Tc3IiGNmXHc&t=1s>**

# セッションの内容

## Gemini Enterpriseが企業に与えた影響

セッションの冒頭では、各企業での具体的な活用事例が紹介され、世界中のビジネス現場でGemini Enterpriseが不可欠な存在になりつつあることが強調されました。

### セッション内で発表されたGemini Entepriseの活用事例

| 企業名 | 業界 | 導入成果・ビジネスへのインパクト |
| --- | --- | --- |
| **ASCO** | 医療 | 臨床医が膨大な医療データから情報を検索し、 意思決定を行う速度が**10倍**に向上した |
| **Anaplan** | ソフトウェア | 従業員のGemini Enterprise利用率が**80%**に到達 社内で**1500以上**のノーコード/ローコードエージェントが構築された |
| **Macquarie** | 金融 | ヘルプセンターのセルフサービス解決率が\*\*40%\*\*向上 詐欺防止やパーソナライズされた提案の支援にエージェントを活用 |

## デモを通じた新機能の紹介

セッションの中盤では、銀行の「住宅ローン処理」を題材に、Gemini Enterpriseを使った実践的なデモが披露されました。

### フルコードで作成したエージェント

「最新の未処理の住宅ローン申請10件を教えてください」と依頼すると、システムが意図を汲み取り、多数のエージェントの中から適切なエージェント（Loan Supervisor）を自動で選定して処理を開始します。  
![](https://static.zenn.studio/user-upload/2b6241fed333-20260511.png)

GCPコンソール画面にて、管理者がエージェントの実行時間や、内部での具体的な動作（書類の検証やユーザーの信用チェックなど）を詳細にモニタリングできる様子が紹介されました。  
![](https://static.zenn.studio/user-upload/50d52374f2b9-20260511.png)

### ノーコードで作成したエージェント

現場の担当者がエージェントデザイナーを使い、ノーコードエージェントの業務フロー内に、先ほどのフルコードで作成したエージェント（Loan Supervisor）を組み込む手順も披露されました。  
![](https://static.zenn.studio/user-upload/54dc14278315-20260511.png)  
「毎日スケジュール実行させる（定期実行）」機能や、人間の確認が必要な場合のみ通知を送る「条件分岐」を設定する様子が紹介されました。

### Canvas・レポート機能

「Canvas」機能を使ってGemini Enterprise内で直接プレゼンスライドを作成・編集する連携機能や、処理結果をHTML形式のレポートにまとめてくれる機能ついても紹介されました。  
![](https://static.zenn.studio/user-upload/fd48da4b4aa4-20260511.png)

## 基盤アーキテクチャとガバナンス機能の強化ポイント

セッション後半では、Gemini Enterprise Agentプラットフォームを支える技術的な進化と、運用ライフサイクルについての詳細が語られました。

### アーキテクチャの刷新と長期記憶（メモリ）のサポート

エージェントの呼び出し構造をフラット化してレイテンシを約40％削減したほか、数週間にわたる長期間の自律稼働を可能にする「ユニバーサルコンテキスト（長期記憶）」のサポートが発表されました。

### 安全なスケールを支えるエンタープライズガバナンス

GCPコンソールでの詳細な可観測性（オブザーバビリティ）やエージェントのレジストリ機能に加え、SPIFFE IDでの管理や、Model Armor・機密データ保護（SDP）を組み込んだエージェントゲートウェイなど、安全性を担保する機能が解説されました。

### 運用ライフサイクルとエコシステムの拡大

構築から運用までのライフサイクル（ビルド・スケール・管理・運用）を支援する仕組みと併せて、ServiceNowやWorkday、Boxなど主要パートナーと連携した「エージェントマーケットプレイス」の大幅なアップデートが紹介されました。

# まとめ

いかがだったでしょうか。本記事では、Google Cloud Next '26で発表されたGemini Enterpriseの最新アップデートについてご紹介しました。少しでも皆様の知識のアップデートや、今後の業務の参考になれば幸いです。

個人的には、「エージェントデザイナー」のアップデートにとても期待しています。条件分岐やエージェントの組み込みによって、エンジニアでなくても日々の業務にフィットするエージェントをより手軽に作成・運用できるようになる未来が楽しみです。

今後もGemini Enterpriseの進化に注目していきたいと思います。  
最後までお読みいただき、ありがとうございました。
