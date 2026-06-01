---
id: "2026-05-31-aws-certified-generative-ai-developer-professional-01"
title: "AWS Certified Generative AI Developer - Professional 試験で問われる「どれを選ぶか」を全タスク・全ドメインまとめた受験ノート"
url: "https://qiita.com/Tacitus/items/df0b9ba8f27dfcb0d1c0"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "LLM", "OpenAI", "qiita"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

:::note warn
初版のため内容の甘いところがあります。随時更新していきます。
:::

## 受験までの流れ

1. **Official Practice Question Set AWS Certified Generative AI Developer - Professional (AIP-C01 - 日本語)** で問題内容のイメージをつかんだ
2. 以下の試験ガイドをもとに Claude で知識をインプットした（本記事はその出力をベースに整理したもの）
   https://d1.awsstatic.com/onedam/marketing-channels/website/aws/ja_JP/certification/approved/pdfs/docs-aip/AWS-Certified-Generative-AI-Developer-Pro_Exam-Guide.pdf
3. **Udemy の AWS 認定 AWS Generative AI Developer - Professional 模擬問題集** を受講
4. **Official Pretest AWS Certified Generative AI Developer - Professional (AIP-C01 - 日本語)** を受講

**→ 合格**

わからないところは常に **Claude** に問いかけ、壁打ちを繰り返しながら理解を深めた。
「なぜこのサービスを選ぶのか」「このシナリオでは何が優先されるのか」といった問いを Claude にぶつけ、
対話の中で腑に落ちるまで掘り下げていった。

**Claude とともに歩んで、合格できた。**

---

試験ガイド: [AWS Certified Generative AI Developer - Professional](https://docs.aws.amazon.com/ja_jp/aws-certification/latest/ai-professional-01/ai-professional-01.html)

各タスクを「**試験で問われる判断パターン**」「**読むべき公式ドキュメント（何を確認するか）**」「**迷いやすい比較ポイント**」のセットで記載。

---

## ドメイン構成（出題比率）

| ドメイン | 内容                                 | 比率    |
| -------- | ------------------------------------ | ------- |
| Domain 1 | FM統合・データ管理・コンプライアンス | **31%** |
| Domain 2 | 実装と統合                           | **26%** |
| Domain 3 | AIの安全性・セキュリティ・ガバナンス | **20%** |
| Domain 4 | 運用効率と最適化                     | **12%** |
| Domain 5 | テスト・検証・トラブルシューティング | **11%** |

> Domain 1 + 2 だけで出題の **57%** を占める。まずここに集中する。

---

## Domain 1: FM統合・データ管理・コンプライアンス（31%）

---

### Task 1.1 ｜ 要件を分析してGenAIソリューションを設計する

**試験で問われる判断パターン**

- **「ドメイン知識を持たせたい」→ RAG / Fine-tuning / プロンプトエンジニアリング / CPT のどれを選ぶか**
  - 「情報が頻繁に更新される」「引用元を提示したい」「社内ドキュメントを参照させたい」→ **RAG**（モデルは変えず、外部から都度知識を注入）
  - 「特定の文体・出力フォーマット・専門用語を一貫して再現させたい」→ **Fine-tuning**（少量のQ&Aペアでモデルの振る舞いを矯正）
  - 「ドメイン固有の膨大な非ラベルテキスト（医療文献・法律文書等）で基礎知識ごと与えたい」→ **Continued Pre-training**（大量データ・高コスト・モデル全体の再学習）
  - 「数件の例示で十分カバーできる」→ **プロンプトエンジニアリング**（Few-shot・CoTで最も低コスト）
  - **判別軸**：データ更新頻度／必要データ量／コスト／引用可否

- **「レイテンシ重視 / バッチ処理 / 安定運用」→ オンデマンド・Provisioned Throughput・Batch API のどれか**
  - 「ユーザー対話で即応必須・トラフィックが予測不能」→ **オンデマンド**（従量課金・スロットリングあり）
  - 「夜間に数万件のドキュメント要約をまとめて処理」→ **Batch API**（最大50%安・非同期・S3入出力）
  - 「高頻度かつ予測可能な常時トラフィック」→ **Provisioned Throughput**（モデルユニットを月／半年単位で予約・スロットリングなし）
  - **判別軸**：応答時間要件／トラフィックパターン／コスト

- **「コンテキストが長大なPDFを処理したい」→ どのモデルを選ぶか（コンテキスト長の観点）**
  - モデルごとに最大入力トークン数（コンテキストウィンドウ）が異なる（例：Claude系は200K前後、軽量モデルは数K〜数十K）
  - 文書全体を一度に渡したい → 長コンテキスト対応モデル（Claude Sonnet/Opus等）を選択
  - 長すぎてコストが膨らむ場合 → **RAGで分割検索**して必要箇所だけ渡す代替案を検討
  - **判別軸**：入力サイズ／コスト／要約精度

**読むべき公式ドキュメント**

| ページ                                                                                                                                                                      | 確認すべきポイント                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| [Amazon Bedrockとは](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)                                                                             | 左ナビで全機能（KB・Agents・Guardrails・Flows・Fine-tuning等）の一覧を把握                        |
| [RAG・Fine-tuning・プロンプトエンジニアリングの使い分け](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/introduction.html) | 3手法の使い分け判断基準を図で理解する                                                             |
| [マネージドRAG vs カスタムRAG の選択](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/choosing-option.html)                 | ==Bedrock KBを使う場合と、OpenSearch自作の場合の選択基準==                                        |
| [サポートされているFMモデル一覧](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)                                                                | モデルのコンテキスト長・モダリティ・Fine-tuning対応可否の比較表                                   |
| [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)                                                                 | 6本柱（運用上の優秀性・セキュリティ・信頼性・パフォーマンス効率・コスト最適化・持続可能性）の観点 |
| [Generative AI Lens（Well-Architected）](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html)                                     | GenAI固有の設計ベストプラクティス。試験ではアーキテクチャ妥当性の根拠として登場                   |

---

### Task 1.2 ｜ FMを選定して設定する

**試験で問われる判断パターン**

- **モデル選定問題：要件からFMを選ぶ**
  - 「予算が厳しい・低レイテンシ重視」→ 小型モデル（Claude Haiku / Nova Micro / Llama 8B 等）
  - 「高精度・複雑な推論が必要」→ 大型モデル（Claude Sonnet・Opus / Nova Pro 等）
  - 「画像も入力に含めたい」→ マルチモーダル対応モデル（Claude 3系・Nova 系）
  - 「日本語含む多言語処理」→ 多言語対応モデル（Claude / Cohere Command-R 等）
  - **判別軸**：コスト × レイテンシ × 精度 × コンテキスト長 × モダリティ × 言語

- **API選定問題：Converse API か InvokeModel API か**
  - 「チャット・複数ターン対話・ツールユース・モデル差し替え」→ **Converse API**（モデル横断で統一フォーマット、messages配列でメンテ容易）
  - 「特殊なモデル固有パラメータが必要」「ConverseがまだサポートしないFM」→ **InvokeModel API**（モデル個別のリクエスト形式）
  - **判別軸**：マルチターン会話の有無／ツールユース要件／モデル切替の頻度

- **スループット問題：オンデマンド か Provisioned Throughput か**
  - 「バースト的・予測不能なトラフィック」→ **オンデマンド**（従量課金）
  - 「常時高トラフィック・スロットリング回避必須・コスト予測したい」→ **Provisioned Throughput**（モデルユニットを1か月／6か月でコミット）
  - **判別軸**：トラフィックの安定性／コスト予測性／SLA要件

- **モデル差し替え柔軟性：「コード変更なしにモデルを切り替えたい」**
  - Lambda 内にモデルIDをハードコードすると、変更のたびにデプロイが必要
  - **AWS AppConfig** にモデルID・プロンプトテンプレート等を外部設定として保管 → Lambda が起動時に取得 → コードデプロイなしで切替可能
  - 段階的ロールアウト・即時ロールバックにも有効

- **可用性・耐障害性：「リージョン障害でも継続したい」**
  - **Bedrock クロスリージョン推論プロファイル**：単一リージョンで容量・モデル可用性が足りないときに別リージョンへ自動ルーティング（最も簡単な耐障害化）
  - **Step Functions サーキットブレーカー**：連続失敗時に呼び出しを遮断して大量エラーを防ぐ
  - **グレースフルデグラデーション**：高精度モデル失敗時に小型モデルへフォールバックして応答継続
  - **判別軸**：障害発生時に「機能停止」「精度低下で継続」「自動フェイルオーバー」のどれを許容するか

- **カスタムモデル運用：「ドメイン特化FT済モデルを安全にデプロイ・ロールバックしたい」**
  - **SageMaker Model Registry** でバージョン管理・承認状態管理・ステージング/本番昇格
  - CodePipeline + CodeBuild で自動デプロイ・自動テスト
  - 失敗時は Registry で旧バージョンに即ロールバック
  - **判別軸**：バージョニング要件／承認フロー／監査要件

**読むべき公式ドキュメント**

| ページ                                                                                                           | 確認すべきポイント                                                                        |
| ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [サポートされているFMモデル一覧](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)     | プロバイダー別の機能比較表。コンテキスト長・マルチモーダル対応・Fine-tuning可否           |
| [Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)                | マルチターン会話・ツールユースに統一的に対応するAPIの特徴と利点                           |
| [InvokeModel API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html)          | モデル固有のリクエスト形式が必要なケース。ConverseAPIとの使い分け                         |
| [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)              | PTの設定単位（モデルユニット）・コミット期間（1か月/6か月）と、オンデマンドとのコスト比較 |
| [Bedrock クロスリージョン推論](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) | 単一リージョンで容量・モデル可用性が限られる場合の自動ルーティング。耐障害性設計の中核    |
| [AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html)                   | 動的構成でモデルID・プロンプトテンプレート等をコードデプロイなしに切替                    |
| [SageMaker Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html)                  | カスタムモデルのバージョニング・承認状態管理・デプロイ／ロールバックのライフサイクル      |

---

### Task 1.3 ｜ FM消費のためのデータ検証・処理パイプラインを実装する

**試験で問われる判断パターン**

- **PII除去に使うサービス：Comprehend か Macie か**
  - 「FMに入力する文字列の中からリアルタイムにPIIを検出・マスクしたい」→ **Amazon Comprehend**（DetectPiiEntities API、パイプライン処理向き）
  - 「S3バケット内のファイル全体をスキャンして機密データの所在を把握したい」→ **==Amazon Macie==**（ガバナンス・監査・棚卸し向き、リアルタイム処理は不向き）
  - **判別軸**：処理対象（テキスト文字列 vs S3ファイル）／処理タイミング（推論時 vs 定期スキャン）

- **データ取り込み経路：ETL か ストリームか**
  - 「S3間で大量データを変換・結合してKB用に整形」→ **AWS Glue**（サーバーレスETL、データカタログ統合）
  - 「ログやイベントをリアルタイムで取り込みたい」→ **Amazon Kinesis**（ストリーミング）
  - 「Knowledge Base 取り込み時に独自パース処理が必要（HTML特殊形式・社内独自フォーマット等）」→ **Lambda カスタム変換**を KB データソースに登録

- **データ品質検証：「FM投入前に欠損・型崩れを自動チェックしたい」**
  - 「ETLパイプラインに統合してルールベースでチェック」→ **==AWS Glue Data Quality==**（欠損・重複・統計外れ値・カスタムルール）
  - 「データサイエンティストがGUIで探索しながらクレンジング」→ **==SageMaker Data Wrangler==**
  - 「軽量な前処理チェックをLambdaで実施し、結果を可視化」→ Lambda + CloudWatch カスタムメトリクス
  - **判別軸**：チェックの自動度・運用者スキル・処理規模

- **マルチモーダル前処理：データ種別ごとのサービス選定**
  - 「音声 → テキスト」→ **AWS Transcribe**（会議録・コールセンター録音の文字起こし）
  - 「スキャンPDF・画像 → テキスト/表/フォーム抽出」→ **Amazon Textract**
  - 「画像分類・物体検出」→ **Amazon Rekognition**
  - 「PDF/画像/動画/音声を一気通貫で抽出」→ **==Bedrock Data Automation==**（Textract・Transcribeを内部で組み合わせる新サービス、自前で組む代替）
  - 「巨大なバッチ前処理ジョブ」→ **==SageMaker Processing==**

- **FM入力フォーマット：呼び出し先ごとの形式**
  - **Bedrock InvokeModel** → モデル固有のJSON（Anthropic 形式 / Cohere 形式 等）
  - **Bedrock Converse API** → 統一の `messages` 配列（role: user/assistant）
  - **SageMaker エンドポイント** → コンテナの定義に従った構造化JSON
  - **対話アプリ** → 会話履歴を含む messages 形式が必須（履歴保持には DynamoDB を併用）

**読むべき公式ドキュメント**

| ページ                                                                                                                               | 確認すべきポイント                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| [Knowledge Base - データソースとS3設定](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html)             | 対応データソース形式（PDF・HTML・CSV・Confluence・Salesforce等）                                |
| [データ取り込みのカスタマイズ（Lambdaパーサー）](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-custom-transformation.html) | Lambda関数を使った独自パーシングロジックの統合方法                                              |
| [Bedrock Data Automation](https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html)                                             | PDF・画像・動画・音声からの情報抽出を自動化する新機能。Textract・Transcribeを個別に組む代替手段 |
| [Amazon Comprehend - PII検出](https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html)                                         | PIIエンティティ種別（氏名・メール・クレカ番号等）の検出とマスキングの仕組み                     |
| [AWS Glue - ETLパイプライン](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)                                           | S3間のデータ加工・変換パイプライン構成とデータカタログ                                          |
| [AWS Glue Data Quality](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html)                                           | データの欠損・重複・統計外れ値を自動検出するルールセット定義。KB取り込み前のゲート              |
| [SageMaker Data Wrangler](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler.html)                                        | GUIによるデータ探索・クレンジング・特徴量生成。FT用データ準備に有効                             |
| [SageMaker Processing](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html)                                          | 大規模なバッチ前処理ジョブ。マルチモーダル前処理に利用                                          |
| [AWS Transcribe](https://docs.aws.amazon.com/transcribe/latest/dg/what-is.html)                                                      | 音声→テキスト変換。会議録FMパイプラインに利用                                                   |
| [Amazon Textract](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)                                                       | スキャンPDF・画像からのテキスト・表・フォーム抽出。Data Automationが内部で利用                  |

---

### Task 1.4 ｜ ベクターストアソリューションを設計・実装する

**試験で問われる判断パターン**

- **ベクターDB選定：要件からストアを選ぶ**
  - 「とにかく早く立ち上げたい・運用負荷を最小化したい」→ **Bedrock Knowledge Base + OpenSearch Serverless**（マネージド構成、デフォルト最有力）
  - 「**BM25**（キーワードの一致頻度や文書の長さを考慮した従来型の全文検索アルゴリズム）と組み合わせた**ハイブリッド検索**（意味的な類似度で探すベクター検索と、キーワードの一致で探すBM25検索を両方同時に使う検索方式）、**シャード調整**（データを複数の小さな塊に分割して並列処理するときの、その塊の数やサイズの設定変更）、**独自スコアリング**（検索結果の並び順を決めるスコアの計算ロジックをカスタマイズすること）が必要」→ **OpenSearch（プロビジョン）**
  - 「既存の Aurora PostgreSQL にベクター検索を追加したい・トランザクションと一緒に扱いたい」→ **Aurora pgvector**
  - 「ミリ秒オーダーの超低レイテンシが必要」→ **Redis（MemoryDB / ElastiCache）**
  - 「既に Pinecone / MongoDB を使っている」→ そのまま外部マネージドを継続
  - **判別軸**：運用負荷／検索カスタマイズ要件／既存DB資産／レイテンシSLA

- **インデックスアルゴリズム選定：HNSW / IVF / Flat**
  - **HNSW**（Hierarchical Navigable Small World）：高精度・高速だがメモリ大。中〜大規模で最も一般的
  - **IVF**（Inverted File）：超大規模データ向き。クラスタ単位に分割しメモリ効率良いが精度はHNSWに劣る
  - **Flat**：全件総当たり。小規模・完全一致重視。精度100%だが遅い
  - **判別軸**：データ件数／メモリ予算／求めるRecall

- **エンべディングモデル選定**
  - 「日英など多言語混在文書を扱う」→ **Cohere Multilingual Embeddings** や **Titan Text Embeddings V2**（多言語対応）
  - 「コスト最優先・英語中心」→ Titan の小次元（256/512）モデル
  - 「ドメイン特化（医療・法律）」→ ドメイン特化埋め込み or 必要に応じてカスタム学習
  - **判別軸**：言語サポート／次元数 vs コスト／ドメイン適合性

- **メタデータ設計：「検索精度を上げるために何を付与するか」**
  - **タイムスタンプ**：「最新情報のみ」フィルタや時系列ランキングに利用（S3 LastModified + カスタム属性）
  - **著者・部署・所属**：アクセス制御（部署外には見せない等）と検索フィルタを同時に実現
  - **ドメインタグ**：「製品マニュアル」「契約書」「議事録」等で検索範囲を絞る
  - **機密度ラベル**：Guardrails や Lake Formation と連携して閲覧権限を制御
  - 付与方法：S3 オブジェクトのカスタムメタデータ（`x-amz-meta-*`）／KB のメタデータ JSON ファイル

- **大規模スケール：「数億ベクトル規模」**
  - **OpenSearch シャーディング戦略**：プライマリ／レプリカ数、シャードサイズの目安を計算（1シャード10〜50GB目安）
    - **プライマリ**：データを実際に保存する本体のシャード（塊）。プライマリ数を増やすほど並列処理が可能になる
    - **レプリカ**：プライマリのコピー（バックアップ）。障害時の冗長性確保と読み取りの負荷分散に使われる
    - **シャード数の計算式**：`総データ量 ÷ 1シャードのサイズ = プライマリ数`、`プライマリ数 × (1 + レプリカ数) = 合計シャード数`
    - 例：300GB・1シャード30GB・レプリカ1の場合 → プライマリ10、合計シャード20（本体10＋コピー10）
    - シャードが小さすぎると管理オーバーヘッド増、大きすぎると障害時の影響が大きくなるため10〜50GBが目安
  - **ドメイン特化マルチインデックス**：「製品ごと」「言語ごと」等で別インデックスに分けて検索範囲を絞る
  - **階層型インデックス**：粗い検索 → 細かい検索の2段構成で計算量を削減

- **データ鮮度：「KB側を常に最新に保ちたい」**
  - **増分更新**：S3 イベント → EventBridge → KB Ingest Job 起動（変更分のみ再エンベディング）
  - **リアルタイム変更検出**：DynamoDB Streams / DocumentDB Streams → Lambda → KB 同期
  - **定期同期パイプライン**：Step Functions でスケジュール実行（深夜バッチで全件 sync）
  - **完全再構築**：エンべディングモデルを変更した場合は必須（ベクトル空間が変わるため）
  - **判別軸**：更新頻度／許容遅延／コスト

**読むべき公式ドキュメント**

| ページ                                                                                                                                                | 確認すべきポイント                                                              |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| [Knowledge Base - ベクターストア設定](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-setup.html)                                 | OpenSearch Serverless・Aurora・RDS・Redis・Pinecone等の選択肢と設定の違い       |
| [OpenSearch - k-NNベクター検索](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html)                                        | k-NNエンジン選択（nmslib / faiss / Lucene）の違いと推奨ユースケース             |
| [OpenSearch - Serverlessベクター検索コレクション](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector-search.html) | マネージドな構成。Bedrockとの統合が最も容易                                     |
| [OpenSearch - セマンティック検索](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/semantic-search.html)                          | ニューラル検索パイプラインを使ったエンべディング＋キーワードのハイブリッド検索  |
| [Aurora PostgreSQL + pgvector](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.VectorDB.html)                           | 既存RDBにベクター検索を追加するユースケースと設定                               |
| [OpenSearch - Neural プラグイン（Bedrock統合）](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/ml-amazon-connector.html)        | OpenSearch内でBedrockエンべディングモデルを直接呼び出すパイプライン構成         |
| [OpenSearch - シャーディング戦略](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/sizing-domains.html)                           | プライマリ／レプリカ数、シャードサイズの目安。スケール時の必須知識              |
| [Knowledge Base - データソース同期](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html)                             | フル同期 vs 増分同期、自動同期スケジュール設定                                  |
| [Amazon S3 オブジェクトメタデータ](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingMetadata.html)                                          | x-amz-meta-\*カスタムメタデータでドキュメント属性をベクトル検索のフィルタに活用 |

---

### Task 1.5 ｜ FM拡張のための検索メカニズム（RAG）を設計する

> **📝 用語補足：チャンクとチャンキング**
>
> - **チャンク**：長いドキュメントを検索しやすいサイズに分割した小さなテキストの塊。RAGでは100ページのPDFをそのままLLMに渡せないため、あらかじめ小さく切っておき、質問に関連する部分だけを取り出してLLMに渡す
> - **チャンキング**：ドキュメントをチャンクに分割する処理のこと
> - ※シャード（OpenSearch側のデータ保存の分割単位）とは別物。チャンクは「何を保存するか（テキスト）」、シャードは「どこに・どう分けて保存するか（インフラ）」の概念

**試験で問われる判断パターン**

- **チャンキング戦略の選定：文書の性質から戦略を選ぶ**
  - 「ログ・CSV・コードなど均質テキスト」→ **固定サイズ**（実装シンプル、サイズ・オーバーラップを設定）
  - 「自然文の意味境界を保ちたい・PDFや論文」→ **セマンティック**（文脈の切れ目で分割、精度高）
  - 「短いチャンクで検索 → 周辺含めて回答させたい」→ **階層（親子）チャンキング**（小チャンクで検索ヒット、大チャンクをコンテキストとして渡す）
  - 「HTML・Markdown・独自タグ構造で分割したい」→ **Lambda カスタムパーサー**
  - **判別軸**：文書構造／検索精度要件／実装工数

- **検索精度が低い場合の改善手段：リランキング・ハイブリッド検索・クエリ変換**
  - 「上位k件に正解が含まれるが順位が低い」→ **リランキング**（Bedrock Rerank で再順序付け）
  - 「専門用語の完全一致もしたい」→ **ハイブリッド検索**（セマンティック + BM25 を組み合わせ、OpenSearch ニューラル検索）
  - 「ユーザーの質問が曖昧・専門用語不足」→ **クエリ変換**（後述）
  - **判別軸**：失敗パターン（順序問題 / 用語ミスマッチ / 質問曖昧）

- **コンテキスト過多で精度が落ちる**
  - 大きすぎるチャンクを渡すと「Lost in the Middle」現象で中盤の情報が無視される
  - → **親子チャンキング**：小チャンク（〜300トークン）で検索精度を稼ぎ、ヒットした親チャンク（〜1500トークン）を回答用コンテキストとして渡す
  - 代替：上位k件を絞る、Rerank で必要十分な件数のみ渡す

- **エンべディング選定：次元数 vs 精度 vs 多言語性**
  - 「日本語/多言語含む」→ **Cohere Multilingual** または **Titan Text Embeddings V2（多言語版）**
  - 「英語中心・コスト最優先」→ Titan V2 の **256次元**（最も安価）
  - 「精度最優先」→ Titan V2 の **1024次元** や OpenAI text-embedding-3-large
  - 注意：エンべディングモデルを変更した場合は **全データ再ベクトル化が必須**

- **クエリ変換：曖昧な問い合わせの精度を上げる**
  - **クエリ拡張**：同義語・関連語を Bedrock FM で生成して再検索（recall を上げる）
  - **クエリ分解**：「Aの売上とBの利益を比較」のような複合質問を複数サブクエリに分割し、それぞれ検索 → 統合
  - **クエリ書き換え（reformulation）**：会話履歴を踏まえて代名詞や省略を補完（Bedrock KB の Query Reformulation 機能）
  - 実装：Bedrock（FMでクエリ生成）／Lambda（前処理）／Step Functions（分解と並列検索のオーケストレーション）

- **アクセス手段：FMから検索をどう呼ぶか**
  - **関数呼び出し（Tool Use）**：Converse API の toolConfig にベクター検索ツールを登録、FMが必要時に呼び出す
  - **MCP クライアント**：Model Context Protocol で標準化されたツールとして接続、他エージェントでも再利用可能
  - **標準API（REST）**：API Gateway 経由で Retrieve API をラップ、外部システムからも利用
  - **判別軸**：エージェント連携の有無／標準化要件／外部公開の必要性

**読むべき公式ドキュメント**

| ページ                                                                                                                                                      | 確認すべきポイント                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [Knowledge Base - チャンキング設定](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html)                                                  | 固定サイズ・セマンティック・階層・カスタムの各戦略の設定値と特徴を比較            |
| [Knowledge Base - Rerank（リランキング）](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html)                                                 | 初回検索後にFMで再ランク付けして精度を向上させる仕組みと設定                      |
| [OpenSearch - ニューラル検索パイプライン設定](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-configure-neural-search.html) | ハイブリッド検索（セマンティック＋BM25）のパイプライン構成                        |
| [RAGのベストプラクティス](https://docs.aws.amazon.com/prescriptive-guidance/latest/writing-best-practices-rag/introduction.html)                            | チャンキング・プロンプト設計・コンテキスト管理の推奨パターン                      |
| [Amazon Titan Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)                                                 | Titan Text Embeddings V2の次元数選択（256/512/1024）とコスト・精度トレードオフ    |
| [Bedrock Knowledge Base - クエリ変換](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html)                                             | クエリ書き換え（query reformulation）・分解の設定オプション                       |
| [Model
