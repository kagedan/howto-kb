---
id: "2026-04-07-claude-codeに経営会議を持ち込む-claude-c-suite-plugin-を作った話-01"
title: "Claude Codeに「経営会議」を持ち込む — claude-c-suite-plugin を作った話"
url: "https://qiita.com/kiyotaman/items/29718a0d5f6363ccb8a2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## TL;DR

* Claude Code に **CEO・CTO・CSO・CFO  
  など14人の経営層レビュー**を呼び出せるプラグインを作った
* `/claude-c-suite:ceo` を打つだけで、リポジトリを自動診断 →  
  最適な3つの専門家視点を選定 → 統合された経営判断を返す
* 「どのレビューを呼べばいいか分からない」問題を解決する単一質問ルーター `/ask` も用意
* 全コマンドが**解析のみ・変更しない**ので、どんなリポでも安全に試せる

## なぜ作ったか

Claude Codeでコードレビューを頼むと、たいてい「とりあえず良さそうな提案」が返ってきます。でも実際の開発現場では、レビューする人の**役割**で見るポイントがまったく違うはず。

* CTO は技術的負債とアーキの一貫性を見る
* CSO は OWASP Top 10 と秘匿情報の漏洩を見る
* CFO は N+1 クエリと無駄なリソース消費を見る
* CMO は SEO と Core Web Vitals を見る
* CLO は依存ライブラリのライセンス互換性を見る

これを **「役割を切り替えて呼び出せる」スラッシュコマンド集**にしたのが  
claude-c-suite-plugin です。

この記事からの派生です。  
<https://qiita.com/kiyotaman/items/4a9523badbc08af35a93>

## インストール

```
/plugin marketplace add JFK/claude-c-suite-plugin
/plugin install claude-c-suite
```

これだけ。あとは任意の Git リポジトリで:

CEO がリポを自動診断し、最も関連の深い 3 つの C-Suite  
視点を選び、優先度付きアクションリストを返してくれます。迷ったらまず /ceo  
が安全な入口です。

## 14人の経営層

| コマンド | 役割 | レビュー対象 |
| --- | --- | --- |
| /ceo | CEO（メタレイヤー） | 必要な3つの視点を選定し、横断的な経営判断を統合 |
| /ask | C-Suite ルーター | 質問を最適な単一CxOに自動振り分け |
| /cto | Chief Technology Officer | 技術負債、アーキ、リファクタ優先度 |
| /pm | Product Manager | マイルストーン整理、Issue優先度、リリース計画 |
| /cso | Chief Security Officer | 脆弱性、認証、秘匿情報、OWASP Top 10 |
| /clo | Chief Legal Officer | ライセンス互換、プライバシー、規制対応 |
| /coo | Chief Operating Officer | CI/CD、デプロイ、可観測性、インシデント対応 |
| /cfo | Chief Financial Officer | クラウドコスト、リソース効率、課金ロジック |
| /cmo | Chief Marketing Officer | SEO、Core Web Vitals、OGP、アナリティクス |
| /caio | Chief AI Officer | LLM統合、プロンプト品質、評価、ガードレール |
| /cio | Chief Information Officer | データガバナンス、スキーマ、システム連携 |
| /cdo | Chief Design Officer | デザインシステム、コンポーネント再利用 |
| /qa-lead | QA Lead | テストカバレッジ、テスト戦略の穴 |
| /dx-lead | DX Lead | API人間工学、SDK、オンボーディング体験 |

## 3つの使い方

### 1. 全体レビュー — /ceo

リポを自動スキャンし、プロジェクトのステージ（早期・成長・成熟・保守）を判定し、上位3視点を選んで横断的な経営サマリーを返します。

### 2. 単一質問 — /ask（v1.5.0 で追加）

「質問はあるけど、どの役職に投げたらいいか分からない」とき。

* /claude-c-suite:ask この SQL スキーマは正規化されてる？
* /claude-c-suite:ask 新しく入れた依存関係、リスク高い？
* /claude-c-suite:ask JWT の実装、安全？

ルーターが内部で全11ロールをスコアリング（ドメイン適合度・証拠の発見可能性・単一視点で答えられるか）し、最適な1人に振り分けます。

面白いのは、単一視点では答えられないと判断したら、ルーター自身が `/ceo` への差し戻しを推奨すること。誤った単一回答を返すより正直に「これは統合判断が必要」と言う動作にしています。

### 3. 直接呼び出し — 役職を指定

役職を覚えているなら直接:

```
/claude-c-suite:cto debt          # 技術負債だけにフォーカス
/claude-c-suite:cso auth          # 認証だけにフォーカス
/claude-c-suite:clo licenses      # ライセンスだけにフォーカス
/claude-c-suite:cfo costs         # コストだけにフォーカス
```

## 設計のキモ — Top 3 クロスリファレンス

各CxOにはTop 3 の主要コラボレーターを定義しています。たとえば:

* CTO ↔ PM, CSO, CIO
* CSO ↔ CTO, CLO, CAIO
* CAIO ↔ CTO, CSO, CFO

これでクラスタが自然に立ち上がります:

* Tech × Security × Data: CTO ↔ CSO ↔ CIO
* AI × Security × Cost: CAIO ↔ CSO ↔ CFO
* Ops × Quality × Cost: COO ↔ QA Lead ↔ CFO
* Design × Marketing × DX: CDO ↔ CMO ↔ DX Lead

CEO はこのグラフの上にいて、ユーザーの相談から「いまこの3つのレンズが効く」と判断して呼び出します。11人を全部薄く呼ぶより、正しい3人を深く呼ぶ方が強いという発想です。

## 安全設計

* Analysis only  
  どのコマンドも解析のみ。ファイルもブランチも一切変更しません。安心して試せます
* Trust boundary  
  README や Issue本文など外部由来のテキストを「データ」として扱い、そこに埋め込まれた指示を実行しないガードレールが全コマンドに入っています（プロンプトインジェクション対策）
* AI-generated advice  
  注意書き — 全コマンドの末尾に「LLM生成のアドバイスなので、セキュリティ・法務・財務系は必ず専門家確認を」というディスクレーマーを必須化
* 適合性監査  
  `python3 scripts/audit.py` が全コマンドファイルに対して140個のチェックを実行。CIで担保

## 使用例

「リリースして大丈夫？」と聞いてみる

```
/claude-c-suite:ceo Are we ready to launch?
```

CEO がリポを診断 → CSO・QA Lead・COO の3視点を選定 → 各視点で分析 → **合意点（高確信度）と対立点（CEO判断）** を整理して、Now / Next / Monitor のアクションリストを返してくれます。

「この GPL ライブラリ、使って大丈夫？」

```
/claude-c-suite:clo Can we use this GPL library in our SaaS product?
```

CLO がライセンスツリーを確認し、コピーレフト感染リスクを評価。

## 関連プラグイン

## まとめ

Claude Code のコードレビューは「誰の視点で見るか」で得られる示唆がまったく変わります。claude-c-suite-plugin は経営層13ロール +ルーター1個を切り替えて呼び出せるようにすることで、その視点切り替えを1コマンドにしました。

* 迷ったら /ceo
* 質問があるなら /ask
* 役職が分かってるなら直接呼ぶ

MIT ライセンスで公開しています。スターやフィードバック歓迎です。

🔗 <https://github.com/JFK/claude-c-suite-plugin>
