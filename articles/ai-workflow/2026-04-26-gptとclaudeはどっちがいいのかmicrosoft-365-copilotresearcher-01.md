---
id: "2026-04-26-gptとclaudeはどっちがいいのかmicrosoft-365-copilotresearcher-01"
title: "GPTとClaudeはどっちがいいのか、Microsoft 365 Copilot（Researcher）に考えてもらった"
url: "https://qiita.com/Oyu3m/items/4ce133a69433d386507d"
source: "qiita"
category: "ai-workflow"
tags: ["OpenAI", "GPT", "qiita"]
date_published: "2026-04-26"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

#  前提
この記事は**2026/4/26時点**での公開情報や動作を私なりにまとめたものとなります。
正確な情報はご自身でご確認もしくはMicrosoftへお問い合わせください。

また、本機能はFrontier(プレビュー)であるため、今後変わる可能性があります。
管理者により制御されている可能性がある点もご留意ください。


# はじめに

Microsoft 365 CopiotはResearcher（リサーチツール）という推論専用エージェントがあります。
これまでMicrosoft 365 Copilotは基本的にGPTモデルを採用していましたが、ResearcherのFrontier機能として、Claudeと並列や直列に処理させられるようになりました。

**モデル切替画面**
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4003209/45828dba-9433-454b-94c8-70a9187b7932.png)

**自動（Critique）**：GPT→Claude直列
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4003209/bc56c510-a40e-4aea-92df-3dcd56cf9bdc.png)

**Model Council**：GPT/Claude並列→合体
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4003209/da06db8d-48ff-48de-8e13-48e02e404612.png)



#  公式情報

こちらの記事に、前提条件や管理者での設定方法など書いていますので、まだご利用されていない方はこちらもご参照ください。
具体的なモデル名については非公表であるため、本記事では推測あくまで推測で、GPT-5.4、Opus 4.7という前提を置いて検証しています。

https://support.microsoft.com/ja-jp/topic/researcher-%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E3%81%A7%E3%83%A2%E3%83%87%E3%83%AB%E3%81%AE%E9%81%B8%E6%8A%9E%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B-cf182434-02b7-4d6f-af25-c50111fc6bf6


https://support.microsoft.com/ja-jp/topic/microsoft-365-copilot%E3%81%A7%E3%81%AE%E7%A0%94%E7%A9%B6%E8%80%85%E3%81%AE%E6%A6%82%E8%A6%81-e63ab760-f3de-4c47-ae87-dad601b0e9c4



#  検証概要

### 結局どれをどう使ったらいいかわからん
４つもモデルがあるけど、ユーザー目線で何をどう切り替えて使ったらいいかわからんですよねぇ。

###  Model Councilに聞いてみる

GPTとClaudeでそれぞれお互いのことどう思っているのか、そして結局モデルをどう切り替えて使ったらいいのか聞いてみました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4003209/8ef60387-c8d9-4d6b-8411-3a2b71ec18f1.png)



###  Researcher(Model Council)への指示
プロンプトが超長いので、簡単な流れとしてまとめると、

① 自分はGPT/Claudeどっちだと思う？
② 自分の得意・苦手を言う
③ 相手のモデルを観察する
④ お互いのズレを確認する
⑤ どっちにどう任せると安心か考える
⑥ Researcherでどのモデルを使い分けるか考える

という内容になります。これを３ステップほどで実行しています。

###  実際の画面

指示を出すと、このようにGPTとClaudeが二人同時に処理を開始します。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4003209/18f28803-9a13-4aac-a6d3-fb5b1f354ee9.png)

レポートが完了すると、右側でそれぞれの完全版の出力結果を見ることができます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4003209/74166b7b-c7db-4d02-8697-2a2e7f087e0c.png)

それぞれの結果を踏まえた要約がチャット画面に返されます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4003209/04475515-7b91-4e19-8305-1ad8807cf4db.png)


# 結論

GPTくんとClaudeくんの協議の結果、以下のようなまとめになりました！
（ほんとはもっとボリューム多いですが一部抜粋）

| モデル | 主な役割・強み（Work IQでできること） | 適している業務シーン | 注意点・留意事項 |
|---|---|---|---|
| **Critiqueモデル**<br>（GPT＋Claude併用） | **AI二段階レビュー**：GPTで下書き作成 → Claudeが構成・完全性を査読<br><br>**Work IQで実現：**<br>・過去の役員向け資料（SPO / OneDrive）の文脈・用語を反映し、組織固有の表現で報告書を生成<br>・Teams会議議事録・Outlookメール履歴から意思決定の経緯を引用し、説明責任を担保<br>・重要な主張に**明確な出典（内部文書・Web）**を自動付与し、再作業を削減 | **信頼性が最重要の報告書作成：**<br>・役員向け四半期レビュー、社外提出ドキュメント、監査対応資料<br>・過去プロジェクト（Teams / SPO）の文脈を踏まえた事業計画書<br>・法務・コンプライアンス案件で引用漏れを防ぎたい分析 | ・2モデル分の処理で応答に時間（通常の約2倍）<br>・単純な問いやブレーンストーミングには過剰品質で非効率 |
| **Model Council**<br>（マルチモデル比較） | **複数AIによる並行推論**：GPTとClaudeが同時に深い推論を実行し、一致点・相違点・独自知見を要約でハイライト<br><br>**Work IQで実現：**<br>・Teams過去会議・Outlookメールスレッドから複数の意見・立場を抽出し、合意点と対立点を整理<br>・SPO / OneDrive内の複数プラン文書を横断比較し、リスク・機会の見落としを防止<br>・Plannerタスク履歴・Loop議論ログを反映し、現実的な選択肢を多角的に提示 | **複雑な意思決定・戦略判断：**<br>・新規事業検討（実現可能性・リスク評価で複数視点が必要）<br>・複数プランのレビュー（M&A評価、投資判断、組織再編）<br>・抜け漏れ防止が重要な仮説検証・合意形成プロセス | ・2レポート＋要約で情報量が多く、処理時間・コストも増加<br>・シンプルな問いには冗長で読解負荷が高い |
| **GPTモデル**<br>（OpenAI GPTシリーズ） | **迅速な情報統合と即応性**：Web検索結果の高速統合と高い即答性<br><br>**Work IQで実現：**<br>・Outlookメール・Teams会議履歴を即座に要約し、翌日の会議準備を数分で完了<br>・SPO / OneDrive内の市場調査資料とWeb最新情報を統合し、競合分析の速報を作成<br>・Plannerタスクと関連メールを横断検索し、プロジェクト進捗サマリーを自動生成<br>・**コスト効率が高く大量処理に最適** | **速度優先・日常業務：**<br>・市場・競合調査の速報作成（即日〜翌日納期）<br>・議事録の要約、メール返信ドラフト、提案書の初稿作成<br>・ブレーンストーミング、アイデア発散、仮説列挙<br>・定型業務の効率化（日報・週報作成） | ・複雑な長期推論では誤り・抜けが生じる可能性<br>・確認質問を省略して即答する傾向があり、意図ズレはユーザー側で検証・精緻化が必要 |
| **Claudeモデル**<br>（Anthropic Claudeシリーズ） | **段階的な深い推論と自己検証**：長文コンテキスト処理と構造化・矛盾検出に強み<br><br>**Work IQで実現：**<br>・SPO内の数十万文字規模の契約書・規程文書を横断分析し、リスク条項を精査<br>・Teams過去会議＋Outlookメール履歴から複雑な経緯を段階的に整理<br>・曖昧な指示に対し追加質問を行い、解釈ズレを事前防止<br>・一貫した原則に基づく安全な判断 | **高度な分析・リスク評価：**<br>・長文資料の比較・要約を含む分析レポート<br>・法務・コンプライアンス・医療など高リスク領域<br>・曖昧な課題の構造化・論点整理<br>・安全性・一貫性が重要な意思決定 | ・出力が長く詳細（簡潔さより網羅性重視）<br>・質問が曖昧だと追加確認が入りやすく時間がかかる<br>・処理コストが高め（GPT比 約1.6〜2倍） |

これは途中で絵にしてみた様子↓
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4003209/1bea8347-c68b-4536-a303-81460c40463d.png)

# 所感
「自動」でええやんと思っていましたが、それぞれ特色や使いどころが理解できてよかったです。ちなみにGPTはスピード重視と言っていますが、Model Councilで先に終わるのはClaudeの場合がほとんどです。
Model Council中の同じ指示に対するGPT/Claudeの回答の違いがわかりやすく、単純に並行して動く様子も面白いので、どんどん使って試してみてください！
