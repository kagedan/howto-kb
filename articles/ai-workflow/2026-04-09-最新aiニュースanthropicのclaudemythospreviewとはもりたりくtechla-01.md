---
id: "2026-04-09-最新aiニュースanthropicのclaudemythospreviewとはもりたりくtechla-01"
title: "【最新AIニュース】AnthropicのClaudeMythosPreviewとは⁉️｜もりたりく（TechLab CEO）"
url: "https://note.com/riku_techlab/n/n69d1af962dbe"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-04-09"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

こんにちは😊  
Anthropicまわりの新情報で、いまかなり注目されているのが Claude Mythos Preview です。

結論からいうと、これは ただの新モデル ではありません。  
Anthropicがかなり強力だけど、そのまま一般公開するには危険性も高い と判断した、かなり特別な研究プレビューです。しかも用途の中心は、チャットや文章生成よりも 防御目的のサイバーセキュリティ です。

今回は、Claude Mythos Previewって結局なにがすごいのか、どこまで使えるのか、なぜ一般公開されていないのかを、できるだけわかりやすく整理します ✍️

## そもそも Claude Mythos Preview って何？ 🧠

Claude Mythos Preview は、Anthropicの最新クラスのフロンティアモデルで、特に コーディング と エージェント的な作業に非常に強いモデルです。Anthropic自身は、これを Project Glasswing の一部として、防御的なサイバーセキュリティ用途向けの research preview と位置づけています。さらに公式ドキュメントでは、一般向けの通常モデルとは別枠で提供される 招待制の研究プレビュー であり、セルフサーブ申込はできないと明記されています。

つまり、イメージとしてはこうです👇

1. みんなが普通に使うClaudeの新バージョン
2. ではなく
3. かなり危険なレベルまで性能が伸びたため、限定環境で慎重に使われている特別版

という理解が近いです。

## 何がそんなにすごいの？ 🔥

Anthropicの公式発表では、Mythos Previewは 重要ソフトウェアに対して何千件もの高重大度の脆弱性を発見した とされています。しかも対象は一部のアプリだけではなく、主要なOSや主要なWebブラウザまで含まれます。Anthropicは、こうした能力の背景にあるのは サイバー専用学習というより、強いコーディング能力と推論能力そのもの だと説明しています。

ここがかなり重要です💡

従来の感覚だと  
コードが書けるAI と セキュリティが強いAI は少し別物に見えます。  
でも Mythos Preview は、複雑なソフトウェアを深く理解して変更できる力が強すぎるため、その延長線上で 脆弱性の発見 や 悪用経路の理解 まで一気に踏み込めるわけです。

## ベンチマークでもかなり強い 📈

Anthropicが公開している評価では、Mythos Previewは Opus 4.6 を多くの項目で大きく上回っています。たとえば次のような数字が出ています。

### 1.SWE-bench Pro AIが 実際のソフトウェア開発タスクをどれだけ解けるか を測るベンチマークです。

・Mythos Preview 77.8%  
・Opus 4.6 53.4%

### 2.Terminal-Bench 2.0 AIエージェントが ターミナル上でどれだけ実務的な作業をこなせるか を測るベンチマークです。

・Mythos Preview 82.0%  
・Opus 4.6 65.4%

### 3.SWE-bench Verified SWE-bench の中でも より信頼性を高めた検証版 です。

・Mythos Preview 93.9%  
・Opus 4.6 80.8%

### 4.Humanity’s Last Exam with tools AIの総合的な知力 を測る超難問ベンチマークです。

・Mythos Preview 64.7%  
・Opus 4.6 53.1%

### 5.OSWorld-Verified パソコン上のGUI操作をどれだけ正しくこなせるか を測る系統の評価です。

・Mythos Preview 79.6%  
・Opus 4.6 72.7%

特に注目なのは、単なる文章理解だけではなく

* 実務寄りのコーディング
* 端末操作を含むエージェント的タスク
* ツール利用込みの問題解決

このあたりで強さが見えていることです。  
なので、Mythos Previewは すごいチャットAI というより かなり高度な実務エージェント寄りのモデル と見たほうがしっくりきます。

## なぜ一般公開されていないの？ ⚠️

ここが最大のポイントです。

Anthropicは、Mythos Previewについて 一般公開する予定はない と明言しています。理由はシンプルで、危険な出力や悪用可能性を十分に抑え込める safeguard がまだ必要だからです。モデル概要ページでも、Mythos Previewは defensive cybersecurity workflows 向けの research preview で、招待制かつセルフサーブ申込なしとされています。

また、Anthropicのリスクレポートでは、Mythos Previewは過去モデルよりも かなり高い能力 と より自律的・エージェント的な使われ方 を前提としており、特にソフトウェアエンジニアリングとサイバーセキュリティで非常に強いので、制限回避のような行動も以前より成立しやすいと評価されています。そのうえで、現時点の総合リスク評価は very low ではあるものの、以前のモデルより高い とされています。

要するにAnthropicの姿勢はこうです👇

1. 能力はかなり高い
2. だからこそ危険な使い方も現実味がある
3. 先に防御用途で限定展開する
4. その間に安全策を強化する

かなり慎重なリリース戦略ですね。

## Project Glasswing って何？ 🛡️

Claude Mythos Previewは、Project Glasswing という取り組みの中心モデルです。これは、AI時代の重要ソフトウェアを守るための共同プロジェクトで、AWS、Apple、Broadcom、Cisco、CrowdStrike、Google、JPMorganChase、Linux Foundation、Microsoft、NVIDIA、Palo Alto Networks などが参加しています。Anthropicはこのプロジェクトに最大1億ドル分の利用クレジットと、オープンソースセキュリティ団体向けに400万ドルの寄付を用意しています。

この枠組みでは、参加組織が Mythos Preview を使って

* 脆弱性検出
* バイナリのブラックボックステスト
* エンドポイント保護
* ペネトレーションテスト

などを行う想定です。Anthropicは90日以内に、公開可能な範囲で学びや修正内容を報告する予定だとしています。

## APIで誰でも使えるの？ 💻

現時点では 誰でも自由にAPIから使える状態ではありません。  
公式のモデル概要ページでも、招待制でセルフサーブ申込なしとされています。

一方で、Project Glasswing参加者向けには Claude API、Amazon Bedrock、Google Cloud Vertex AI、Microsoft Foundry から利用できると案内されています。価格は参加者向けに 入力100万トークンあたり25ドル、出力100万トークンあたり125ドル です。

## コンテキスト長はどうなの？ 📚

Anthropicの価格ページでは、Claude Mythos Preview、Opus 4.6、Sonnet 4.6 は 1Mトークンのコンテキストウィンドウ を標準価格で含むと案内されています。つまり、かなり長いコードベースや大規模ドキュメントを扱う前提にも合っています。

この点も、Mythos Previewが単発チャット向けというより

* 大きなコードベースを読む
* 複数ファイルを横断する
* 長い作業履歴を踏まえて継続的に動く

といった、エージェント型ワークフロー向けの性格を強く持っていることを感じさせます。これはベンチマーク結果ともかなり整合的です。

## Mythos Previewは 次のClaude ではない 👀

ここ、誤解しやすいです。

Mythos Previewは、いわゆる みんなが使う次世代Claudeの標準モデル という見え方をしがちですが、実際にはそうではありません。  
Anthropicの公式説明を見る限り、Mythos Previewは 防御的サイバーセキュリティ用途向けの特別な研究プレビュー です。一般公開予定もなく、むしろ upcoming Claude Opus モデルで safeguard を先に試しながら整備していく方針が示されています。

なので、今の理解としては

1. 一般向け主力モデル  
   Opus、Sonnet、Haiku 系
2. 特殊かつ高リスクな研究プレビュー  
   Mythos Preview

という整理がいちばん自然です。

## 使う側としてどう見るべき？ 🤔

開発者や企業の視点では、Claude Mythos Previewから見えてくるメッセージはかなり大きいです。

### 1. AIのコーディング能力は セキュリティ能力 に直結し始めている

コード理解と修正能力が上がるほど、防御にも攻撃にも使える力になります。これは今後のモデル評価で、単なる生成品質だけでは足りなくなることを意味しています。

### 2. これからは 高性能 だけでなく 配布方法 が重要

性能が高いモデルを出すだけではなく、どこまで公開するか、誰に先に渡すか、どうガードするかが製品戦略の中心になってきています。Anthropicはこの点でかなり慎重です。

### 3. セキュリティ業界は AI前提で再設計が必要

Project Glasswingでは、脆弱性開示、ソフトウェア更新、サプライチェーンセキュリティ、パッチ自動化などの実務ルール見直しも視野に入っています。つまり影響はモデル単体ではなく、セキュリティ運用全体に及びます。

## まとめ ✨

Claude Mythos Preview をひとことで言うなら

**超高性能なコーディング系フロンティアモデルを、防御的サイバーセキュリティ向けに限定公開している特別版**

です。

ポイントを最後に整理すると👇

1. Anthropicのかなり強力な新モデル
2. コーディング、推論、エージェント実行が特に強い
3. 重要ソフトウェアの脆弱性発見で大きな成果が出ている
4. ただし危険性も高いため一般公開はしていない
5. 招待制で Project Glasswing の参加者中心に使われている
6. AI時代のセキュリティ運用そのものを変える可能性がある

Anthropicが Mythos Preview をすぐに広く配らず、まず防御側に持たせているのは、かなり象徴的です。  
これからのAIは 便利かどうか だけでなく、どの順番で、どの範囲に、どう安全に届けるか がますます重要になっていきそうです。

---

[#Claude](https://note.com/hashtag/Claude) [#ClaudeMythosPreview](https://note.com/hashtag/ClaudeMythosPreview) [#Anthropic](https://note.com/hashtag/Anthropic) [#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#セキュリティ](https://note.com/hashtag/%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3)

---

![](https://assets.st-note.com/img/1775656614-yZ1lrbAFEqH296gOkn3iauNK.png?width=1200)

---

**・ホームページ**  
AIの社会実装を通じて、誰ひとり取り残さない社会を実現する

**・お問い合わせ**AI開発・DXコンサルティングに関するご相談、採用に関するお問い合わせなど、お気軽にご連絡ください。

Xはこちらです。良かったらフォローしてね。
