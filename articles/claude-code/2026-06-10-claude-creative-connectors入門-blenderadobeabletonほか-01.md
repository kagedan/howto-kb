---
id: "2026-06-10-claude-creative-connectors入門-blenderadobeabletonほか-01"
title: "Claude Creative Connectors入門 — Blender・Adobe・AbletonほかMCP連携9種を解説"
url: "https://qiita.com/kai_kou/items/8c16b9255c162b9650de"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "Gemini", "GPT"]
date_published: "2026-06-10"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

![Claude Creative Connectors — MCPで接続された9ツール概念図](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-creative-connectors-mcp-guide/01-hero.png)

## はじめに

2026年4月28日、Anthropicはクリエイティブツール向けの**9種のClaudeコネクター**をリリースしました。Blender、Adobe Creative Cloud、Ableton Live、Autodesk Fusion、SketchUpなど、クリエイター・エンジニアが日常的に使うアプリをClaudeと直接連携できるようになりました。

すべてのコネクターは**MCP（Model Context Protocol）** をベースに構築されており、Claudeだけでなく他のLLMからも利用可能な設計になっています。

### この記事で学べること

- Claude Creative Connectorsの全体像と9種類のコネクター詳細
- MCPアーキテクチャによる仕組みと他LLMからの利用可能性
- 各コネクターの実際の活用パターン
- セットアップ方法と開発者が押さえるべきポイント

### 対象読者

- ClaudeとクリエイティブツールをAIで連携したい開発者・クリエイター
- MCPコネクターの実装・活用に興味がある方
- Blender・Adobe・Ableton等をより効率的に扱いたい方

## TL;DR

- Anthropicが9種のCreative Connectorsを2026年4月28日にリリース
- Blender・Adobe・Ableton・Autodesk Fusion・SketchUp・Affinity・Resolume・Spliceと連携
- すべてMCPベースで構築されており、Claude以外のLLMも利用可能
- ClaudeのConnectors設定から有効化するだけで利用開始可能

## Claude Connectorsとは

Claude Connectorsは、Claudeが外部のツール・プラットフォームに直接アクセスし、データの取得・操作・ワークフローの自動化を行う仕組みです。

従来のAPIインテグレーションと異なり、コネクターは：

- **ドキュメントの参照**: 公式ドキュメントを根拠にした正確な回答を提供
- **アセットの操作**: アプリ内のファイル・レイヤー・シーン等を直接変更
- **繰り返しタスクの自動化**: バッチ処理・スクリプト生成を自然言語で指示
- **複数アプリ間のブリッジ**: ワークフローをまたいだ横断的な操作

これらをチャット画面から自然言語で指示できる点が特徴です。

![Claude Connectorsの動作フロー — ユーザー→Claude→MCP Connector→Creative Appの流れ](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-creative-connectors-mcp-guide/02-flow.png)

## 9種のCreative Connectors一覧

### 1. Blender

3DCGソフト[Blender](https://www.blender.org/)向けのコネクターは、**BlenderのPython APIへの自然言語インターフェース**を提供します。

**主な機能：**
- Blenderシーン全体の解析・デバッグ
- シーン内のオブジェクトへの一括変更スクリプトを自動生成
- Blenderのインターフェースに新しいツールを直接追加
- 複雑なセットアップの解説・チュートリアル

Anthropicは[Blender Development Fund](https://fund.blender.org/)にパトロンとして参加し、Python API開発を支援しています。


> BlenderのコネクターはオープンソースのMCPをベースにしているため、Claude以外のLLMでも利用できます。BlenderのオープンソースへのコミットメントとMCPの相互運用性が組み合わさった設計です。


**活用例：**
```
# Claudeへの指示例
「シーン内の全オブジェクトのマテリアルをメタリックに変更するPythonスクリプトを生成して」
「このBlenderファイルのポリゴン数が多いオブジェクトを特定して、最適化案を提示して」
```

### 2. Adobe for Creativity

Adobe Creative Cloudとの連携コネクターです。**Photoshop・Premiere・Illustrator・Firefly・Express・Lightroom・InDesign・Stock**を含む50以上のCreative Cloudツールにアクセスできます[^adobe]。

**主な機能：**
- ポートレートのレタッチ・補正
- アセット設計・素材加工
- 動画のリサイズ・最適化
- マルチアプリをまたいだワークフロー自動化

[^adobe]: [Adobe for creativity connector](https://blog.adobe.com/en/publish/2026/04/28/adobe-for-creativity-connector)（2026年4月28日）

### 3. Affinity by Canva

Affinity（Canva傘下）のデザインツール向けコネクターです。

**主な機能：**
- バッチ画像調整の自動化
- レイヤーの一括リネーム
- ファイルエクスポートの自動化
- カスタム機能の生成・アプリへの直接追加

### 4. Autodesk Fusion

3D CAD/CAMツール「Autodesk Fusion」向けコネクターです。Fusionのサブスクリプションが必要です。

**主な機能：**
- 自然言語で3Dモデルを作成・修正
- 設計コンテキストへのセキュアなアクセス
- DesignコンテキストをAIシステムから参照


> AutodeskはFusion MCP（Model Context Protocols）を提供しており、AIシステムが設計コンテキストに安全にアクセスできる仕組みになっています。


### 5. Ableton

音楽制作DAW「Ableton Live」と「Push」向けコネクターです。

**主な機能：**
- Ableton LiveとPushの公式ドキュメントを根拠にした回答
- ソフトウェアの学習・機能解説のサポート
- プロダクション作業のアシスタンス

### 6 & 7. Resolume Arena / Resolume Wire

VJ・ライブビジュアルアーティスト向けのビジュアルパフォーマンスソフト「Resolume Arena」と「Resolume Wire」向けコネクターです。

**主な機能：**
- ライブパフォーマンス中にArena・Avenue・Wireを自然言語でコントロール
- AV制作のリアルタイム操作
- 複雑なビジュアルセットアップの管理

### 8. SketchUp

3Dモデリングツール「SketchUp」向けコネクターです。

**主な機能：**
- 自然言語による記述から3Dモデルの出発点を自動生成
- 部屋・家具・敷地コンセプト等を記述するだけでSketchUpに読み込み可能な形式で出力
- さらに詳細な修正はSketchUp上で実施

**活用例：**
```
「北向きリビング20畳、南側に大きな窓があるシンプルなオープンフロアプランを作って」
```

### 9. Splice

音楽プロデューサー向けロイヤリティフリー・サンプルライブラリ「Splice」向けコネクターです。

**主な機能：**
- SpliceのロイヤリティフリーサンプルカタログをClaude内から検索
- 楽曲制作ワークフローへのサンプル探しを統合

![9種のClaude Creative Connectors — 3カテゴリ分類図（3D/CAD・Visual/Design・Music）](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-creative-connectors-mcp-guide/03-comparison.png)

## MCPアーキテクチャの全体像

Claude Creative Connectorsの技術基盤はすべて**MCP（Model Context Protocol）** です。

### MCPとは

MCPはAnthropicが提唱したオープンスタンダードで、AIモデルが外部ツール・データソースに接続するための標準プロトコルです。2024年のリリース以降、急速に普及し、ClaudeだけでなくGemini・GPT等の主要LLMがサポートするエコシステムになっています。

### Creative ConnectorsにおけるMCPの意義

Blenderのコネクターを例に取ると：

1. **開発者がMCPサーバーを実装** — Blender側がPython APIへのMCPインターフェースを提供
2. **Claudeがクライアントとして接続** — Claude ConnectorsからMCPサーバーへ接続設定
3. **自然言語 → MCP呼び出し** — ユーザーの指示をClaudeがMCPツール呼び出しに変換
4. **他LLMからも利用可能** — MCPオープン標準のため、Claude以外のLLMも同じMCPサーバーを使用可能

この設計により、Anthropicはクリエイティブツールとのエコシステムを独占するのではなく、MCPを通じてオープンな協調基盤を構築しています。

## セットアップ方法

### Claude.aiからの有効化

Claude Connectorsの有効化はClaude.aiのUIから行います。

1. [Claude.ai](https://claude.ai) にログイン
2. 設定（Settings）→ Connectors を開く
3. 利用したいコネクターを選択して「Connect」をクリック
4. 各ツールの認証・権限付与を行う
5. Claudeのチャット画面からコネクターを使用


> Creative Connectorsはすべてのプランで利用可能です。ただし一部コネクター（Autodesk Fusion等）は対象ツール側のサブスクリプションが別途必要です。詳細は[Anthropic公式のコネクター一覧ページ](https://www.anthropic.com/news/claude-for-creative-work)を参照してください。


### Claude Code経由での活用

開発者向けには、Claude Codeからコネクターを活用した自動化スクリプトの作成も可能です。

```python
# Claude APIを使ったBlenderコネクター活用例（コンセプト）
import anthropic

client = anthropic.Anthropic()

# BlenderシーンをClaudeに分析させる
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": "Blenderシーンのポリゴン数を確認して、最適化が必要なオブジェクトを教えて"
        }
    ]
)
print(message.content)
```


> 上記はAPIの概念的なサンプルです。実際のBlender MCP連携では、ローカル環境でのMCPサーバー設定が別途必要です。詳細は[Anthropic公式のClaude for Creative Work](https://www.anthropic.com/news/claude-for-creative-work)を参照してください。


## 活用シナリオ

### シナリオ1: 3Dアーティストの作業効率化

BlenderとSketchUpコネクターを組み合わせることで、コンセプト設計から3Dモデリングまでをシームレスに進められます。

```
1. SketchUp: 「倉庫を改装したロフトアパートのリビング、天井高5m」と指示
   → SketchUpで開ける3Dモデルを自動生成

2. Blender: 生成したモデルを読み込み、マテリアル設定を自然言語で調整
   → 「コンクリート壁・木目フローリング・工業系照明のマテリアルを適用して」
```

### シナリオ2: 音楽プロデューサーのワークフロー統合

AbletonとSpliceコネクターを組み合わせ、サンプル探しから制作指示まで一連の流れをClaude内で完結できます。

```
1. Splice: 「ダークなアトモスフェリックテクスチャ、BPM 140、キーAm」で検索
   → カタログから候補サンプルをリストアップ

2. Ableton: 「選んだサンプルのレイヤリングはどうすればいい？」と質問
   → 公式ドキュメントに基づいたAbleton Liveでの実装方法を回答
```

### シナリオ3: デザイナーのアセット量産

Affinity/Adobeコネクターを使った繰り返し作業の自動化です。

```
Affinity: 「100枚の商品写真に同じトーン補正とウォーターマークを一括で適用して」
Adobe: 「各写真をInstagram用1:1、Twitter用16:9、LinkedIn用4:3の3サイズで書き出して」
```

## 教育パートナーシップ

Anthropicは[ロードアイランド・スクール・オブ・デザイン（RISD）](https://www.risd.edu/)、[Ringling College of Art and Design](https://www.ringling.edu/)、[ゴールドスミス（ロンドン大学）](https://www.gold.ac.uk/)の3校と提携し、学生・教員にClaudeとコネクターへのアクセスを提供しています。

クリエイティブ教育における「コンピューテーショナルクリエイティビティ」カリキュラムへの活用を想定したパートナーシップです。

## まとめ

Claude Creative Connectorsの主要ポイントをまとめます：

| コネクター | 分野 | 主な用途 |
|-----------|------|---------|
| Blender | 3DCG | シーン解析・Pythonスクリプト生成 |
| Adobe | 映像/デザイン | 50+CCツール操作・マルチアプリ連携 |
| Affinity by Canva | デザイン | バッチ処理・ファイル操作 |
| Autodesk Fusion | 3D CAD | 3Dモデル作成・修正 |
| Ableton | 音楽制作 | 公式ドキュメント活用 |
| Resolume Arena/Wire | VJ | リアルタイムビジュアルコントロール |
| SketchUp | 建築/空間 | 自然言語→3Dモデル生成 |
| Splice | 音楽制作 | サンプル検索 |

**MCPオープン標準ベース**という設計により、特定のLLMに縛られない将来性のあるエコシステムが形成されています。エンジニアがカスタムMCPサーバーを実装すれば、このコネクターエコシステムに独自ツールを追加することも可能です。

クリエイティブ分野のAI統合はまだ初期フェーズですが、MCPという共通基盤によって今後の連携ツールが急速に増えることが期待されます。

## 参考リンク

- [Claude for Creative Work（公式発表）](https://www.anthropic.com/news/claude-for-creative-work) — Anthropic公式
- [Adobe for creativity connector（Adobeブログ）](https://blog.adobe.com/en/publish/2026/04/28/adobe-for-creativity-connector) — Adobe公式
- [Anthropic releases 9 Claude connectors for creative tools（9to5Mac）](https://9to5mac.com/2026/04/28/anthropic-releases-9-new-claude-connectors-for-creative-tools-including-blender-and-adobe/)
- [Claude Gains Integrations With Adobe, Blender, SketchUp（MacRumors）](https://www.macrumors.com/2026/04/28/claude-creative-tool-connectors/)
- [Anthropic joins Blender Development Fund](https://letsdatascience.com/news/anthropic-joins-blender-development-fund-as-corporate-patron-c53458fb)
