---
id: "2026-04-25-cohereとaleph-alphaが200億ドル規模で統合発表claudeのmanaged-age-01"
title: "CohereとAleph Alphaが200億ドル規模で統合発表、ClaudeのManaged Agentsにメモリ機能追加など：2026-04-25 AI動向まとめ"
url: "https://qiita.com/lavellehatcherjr/items/dae8cc9987dabdb13d3b"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "qiita"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

![qiita-april25-thumbnail.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4398742/44cefc95-a9c3-41ce-aef5-607970f24518.png)
※本記事は公開情報をもとにした個人的なまとめであり、各企業の公式見解ではありません。本記事は投資助言を目的としたものではありません。

## CohereとドイツのAleph Alphaが統合し、約200億ドル規模の企業に

カナダのCohereとドイツのAleph Alphaが、2026年4月24日に統合計画を発表しました。並行して進めているシリーズEの調達クローズ後の評価額は、合計で約200億ドル規模になる見込みと報じられています。

統合後の体制では、Cohere側の株主が約9割、Aleph Alpha側の株主が約1割を保有する形が示されました。Aleph Alphaの主要出資元であるドイツのSchwarz Group（リーダーやKauflandを擁する小売コングロマリット）は、新たに6億ドルをCohereのシリーズEに拠出する方針です。

両社は、金融・ヘルスケア・防衛・エネルギー・通信といった規制業界向けに、自社環境内で運用できる「ソブリンAI」基盤を統合提供する構想を掲げています。発表の場にはドイツのデジタル担当大臣とカナダのAI担当大臣も同席し、欧州での主権的なAI整備が政策と企業戦略の双方で前面に出てきた印象です。

開発者目線では、欧州案件で「データを域内に閉じ込めたい」「特定モデルプロバイダ依存を避けたい」という要件が増えているので、選択肢が広がる方向の話として参考にしたいところです。

## Anthropic、Claude Managed Agentsに「メモリ」機能を公開ベータで提供

Anthropicは2026年4月24日、企業向けのClaude Managed Agentsにメモリ機能を追加し、公開ベータとして利用可能にしたと発表しました。エージェントが過去のセッションから学んだ内容を蓄積し、別セッションや別エージェントでも活用できる仕組みです。

特徴的なのは、メモリがファイルシステムに直接マウントされる点です。Claudeはbashやコード実行ツールでファイル操作と同じ感覚でメモリを読み書きできます。書き込みはClaudeコンソール上のセッションイベントとして記録され、APIを通じてエクスポートやロールバック、内容の編集が行えるとされています。

NetflixやRakuten、Wisedocs、Andoといった先行ユーザーの利用例も紹介されており、初回パスでのエラー削減やコスト・レイテンシの改善が示されています。

エージェント開発で「毎回コンテキストを詰め直す」運用に疲れていた人にとって、ファイル単位で監査・差し戻しできるメモリ層は素直に嬉しい設計に思えます。

## Anthropic、ClaudeにSpotifyやUberなど「パーソナル系」コネクタを追加

同じく4月23日から24日にかけて、Anthropicはコンシューマー向けのコネクタも拡充しました。SpotifyやAudible、Uber、AllTrails、TripAdvisor、Instacart、TurboTaxなど、業務用途以外のパーソナルサービスとClaudeを直接接続できるようになっています。

Spotifyとの連携では、リスニング履歴や好みに基づくプレイリスト・ポッドキャストの提案ができ、無料ユーザーと有料ユーザーの双方が利用できます。有料ユーザーは「気分」や「シーン」を自然言語で伝えてプレイリストを生成することも可能です。

Anthropicは、これらの連携枠に有料での優先表示や広告は導入しないと明言しています。ChatやAssistantが「アプリのハブ」になっていく流れは、開発者がプロダクトをどう露出させるかというSEOならぬ「AIO」の議論にも直結しそうです。

## Cognition AI、評価額250億ドルでの調達協議が報道される

Bloombergは4月23日、AIコーディングエージェント「Devin」を提供するCognition AIが、評価額250億ドル規模での新ラウンド調達協議に入っていると報じました。数億ドル以上を調達する想定とされ、現時点で条件は流動的とされています。

Cognitionは2025年9月にFounders Fund主導の4億ドル調達で評価額を約102億ドルとしたばかりで、今回の協議が成立すれば短期間でおよそ2倍以上に切り上がる計算です。エンタープライズ領域でのAIコーディングエージェント需要の高まりが背景にあると報じられています。

## Tencent・Alibaba、DeepSeekへの初の外部出資協議が伝わる

中国の大手プラットフォーマーであるTencentとAlibabaが、AIスタートアップDeepSeekへの初めての外部出資ラウンドへの参加について協議していると報じられています。Tencentは最大で約20%相当の株式取得を提案しているとされています。

DeepSeekは直前にオープンウェイトのV4プレビュー（V4-ProとV4-Flash）を公開したばかりで、外部資本の受け入れ自体が新しい動きとなります。資本構造の変化は、今後のモデル公開ポリシーや海外利用条件にも影響しうる論点として追っておきたいところです。

## ICLR 2026がリオデジャネイロで開幕

機械学習分野の主要国際会議であるICLR 2026が、4月23日から27日までブラジル・リオデジャネイロのRiocentroで開催中です。本会議は23〜25日、ワークショップが26〜27日というスケジュールです。

今回のICLRはエージェント型AIや、安全性・ガバナンス・データ管理といったテーマが目立つと各社のプレビュー記事で紹介されています。AppleやGoogle、NAVER LABS Europeなどが採択論文や発表予定を公開しています。論文の本数だけでなく「研究の重心が応用と運用にどれだけ寄っているか」を読み取りやすい場としてチェックしてみてもよさそうです。

## まとめ

- 規制業界・公共セクター向けの「ソブリンAI」を巡って、Cohere・Aleph Alphaのような大型統合が動き始めています。欧州案件では新しい選択肢として頭に入れておきたいところです。
- Anthropicはエージェント基盤に「ファイルとして扱えるメモリ」を導入し、業務側ではUberやSpotifyなどのパーソナルアプリ連携も拡張しました。エージェントが「業務タスク以外のライフ系タスク」までこなす設計が現実味を帯びています。
- AIコーディング分野の評価額は引き続き上昇基調で、Cognitionの250億ドル協議がその象徴になっています。中国側でもDeepSeekへの大手プラットフォーマー出資協議が進み、資本面での再編が広がっています。
- ICLR 2026がリオで開幕しており、エージェント・データガバナンス・安全性周りのトレンドを論文ベースで追える時期に入っています。

## 参考

- Cohere acquires, merges with Germany-based startup to create a 'transatlantic AI powerhouse' (TechCrunch)
- Cohere to acquire German AI company Aleph Alpha as it looks to expand in Europe (CNBC)
- Anthropic adds memory to Claude Managed Agents (SD Times)
- Spotify Brings Music and Podcast Recommendations to Claude (Spotify Newsroom)
- AI Coding Firm Cognition in Funding Talks at $25 Billion Value (Bloomberg)
- ICLR 2026
