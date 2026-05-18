---
id: "2026-05-17-adaptive-survivable-verification-system-asvs-に基づく技-01"
title: "Adaptive Survivable Verification System (ASVS) に基づく技術監査フレームワーク"
url: "https://zenn.dev/kafka2306/articles/5c3c93f798da3f"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/929064738102-20260517.png)

1. イントロダクション：AI時代のシステム監査におけるパラダイムシフト

現代のシステム環境は、AI（LLM）の統合やマイクロサービス化、複雑なサプライチェーンの依存により、本質的に「非決定論的（Non-deterministic）」な挙動を内包しています。従来の「静的な文書ベースの監査」は、特定時点のスナップショットを検証するに過ぎず、実行時に刻々と変化するシステムの現実、すなわち「ランタイム・ドリフト」を捉えきれません。

このような背景から、証拠ベースの継続的検証、すなわち Adaptive Survivable Verification System (ASVS) への移行が戦略的に不可欠となっています。

ASVSのメタ原則：壊れ続ける現実世界での検証可能性

ASVSの根底にあるのは、「壊れ続ける現実世界の中で、継続的に検証可能性を維持すること」というメタ原則です。システムは常に、依存関係の乖離（Dependency Drift）、外部APIの仕様変更、部分的障害（Partial Outage）、あるいは人間による運用ミス（Human Operational Failure）に晒されています。ASVSは、単なる一過性の正しさではなく、これらの不確実性に耐え、検証可能な状態を維持し続ける「生存性（Survivability）」を最優先事項と定義します。

組織的メリット：もっともらしい説明より、現実との継続整合

1. 信頼の客観化: 従来の「推論」や「もっともらしい説明」を排除し、暗号学的に検証可能な「客観証拠」に基づく信頼を構築します。
2. ドリフトの早期検知: 公式仕様（Official Specifications）と、刻一刻と変化する現実（Runtime Reality）の乖離を自動的に検出し、致命的な破綻を未然に防ぎます。
3. レジリエンスの証明: 部分的障害や劣化状態においても、システムが最低限の品質を維持し、回復可能であることを定量的証拠によって証明します。

この監査を成立させるための前提条件として、まず「客観証拠」の厳格な定義と核心原則を確立します。

---

2. 監査の核心原則と客観証拠の定義

NISTが引用するISO 19011:2018の定義に従い、監査とは客観証拠（Objective Evidence）を監査基準（Criteria）と照合するプロセスです。ASVSでは「No Evidence, No PASS（証拠なしにPASSを出さない）」を鉄則とし、以下の核心原則を遵守します。

ASVS核心原則

原則 システムの強靭性への寄与  
Runtime Overrides Assumptions 推論ではなく実際の実行状態（Runtime）の結果を真実として優先する。  
Reality Overrides Documentation READMEやLLMの要約は真実の源泉ではない。現実の動作をエビデンスとする。  
Official Specifications Override Local Assumptions ローカルの実装都合よりも、公式の外部仕様（RFC、API定義等）との整合を優先する。  
Observability Is Mandatory 観測不能なシステムは監査不能である。内部状態の可視化を義務付ける。  
State and Time Matter 単発の成功は信頼の証拠にならない。長期的な状態遷移、継続性、ドリフトを監査対象とする。  
Survivability Over Snapshot Correctness 「点の正しさ」より、依存関係の変化や劣化に耐えうる「継続的な生存性」を重視する。

証拠の階層構造（Evidence Hierarchy）

監査証拠は以下の階層に従って評価され、Tier 2/3のみでのPASS判定は明示的に禁止されます。

階層 証拠タイプ 具体的な技術成果物 評価  
Tier 0 直接的な実行証拠 終了コード（Exit Code）、APIレスポンス、実行コードのハッシュ値、署名検証、状態スナップショット。 最強の証拠  
Tier 1 構造的証拠 ソースコード、IaCマニフェスト、Lockfile、環境定義ファイル。 強い証拠  
Tier 2 記述的証拠 README、ドキュメント、ADR（意思決定記録）、コメント。 単独PASS不可  
Tier 3 推論的証拠 LLMによる要約、意図の解釈、人間の主観的な想定。 単独PASS不可

---

3. ユニバーサル検証ワークフローとガバナンス

監査プロセスが単なるチェックリストの消化に陥ることを防ぐため、22段階のワークフローを以下のフェーズで運用します。

Universal Verification Workflow (22 Steps)

Phase 1: 発見とアサンプション抽出 (Steps 1-9)

目標：システムのドメインを特定し、検証すべき期待値を抽出する。

1. Discover: 監査対象の全体像を特定。
2. Detect domains: 検証対象となる技術領域を分類。
3. Extract runtime assumptions: 実行環境に関する想定を抽出。
4. Extract state assumptions: 期待される状態遷移の抽出。
5. Extract environment assumptions: OS、パス、権限等の環境依存性の抽出。
6. Extract expected capabilities: システムが備えるべき機能の定義。
7. Extract expected artifacts: 生成されるべき成果物の定義。
8. Extract expected quality constraints: 遅延、精度等の品質制約の抽出。
9. Extract observability requirements: 必須となる観測項目の特定。

Phase 2: 整合性検証 (Steps 10-18)

目標：直接証拠に基づき、仕様と現実の不一致を排除する。 10. Verify external specifications: 公式仕様との整合性確認。 11. Verify dependency consistency: 依存関係（API/パッケージ）の整合性確認。 12. Verify runtime consistency: 実行時挙動の一貫性確認。 13. Verify state consistency: 状態遷移の正当性確認。 14. Verify artifact validity: 成果物のパース可能性、再現性、署名検証。 15. Verify observability: ログ、メトリクス、プロバナンスの可視性確認。 16. Verify recoverability: リトライ、ロールバック、劣化モードの動作確認。 17. Verify semantic correctness: 実行結果の論理的整合性の検証。 18. Verify long-term survivability: 長期運用におけるドリフト耐性の評価。

Phase 3: 修復統制と報告 (Steps 19-22)

目標：失敗を分析し、統制された範囲で修正・報告を行う。 19. Analyze failures: 失敗の根本原因（確定/非確定/環境等）を分類。 20. Govern repairs: 修復範囲を限定し、プロバナンスを記録した上での修復。 21. Reverify: 修復後のリプレイによる再検証。 22. Produce audit report: 機械可読（JSON/YAML）な最終レポートの生成。

検証予算ガバナンス（Verification Budget Governance）

無限の検証はリソースを枯渇させ、それ自体が脆弱性となります（OWASP LLM10: Unbounded Consumption）。

* Mandatory Limits: 最大ランタイム、最大トークン予算、最大Webルックアップ数、最大再帰深度、最大修復試行回数。
* 強制停止条件: 証拠利得の減少、再帰的な依存関係の爆発、予算超過。

---

4. フェイルクローズ設計とリソース境界の強制

SaltzerとSchroederの「Failsafe Defaults」に基づき、未知の事象に対してシステムは「拒絶」を選択しなければなりません。

Fail-closed設計基準

* 既定拒否の原則: SLSA（Software Supply Chain Levels for Software Artifacts）が提唱するように、認識できない外部パラメータ（unrecognized externalParameters）が含まれる場合、検証は「FAIL」としなければなりません。
* リソース境界の強制: KubernetesのResourceQuotaのように、メモリやCPUの制限を物理的に強制します。
* 予算超過は失敗: タイムアウトやクォータ超過は、単なる「遅延」ではなく「境界違反（Failure）」として扱います。
  + Kubernetesの activeDeadlineSeconds 到達時と同様に、reason: DeadlineExceeded として即座にプロセスを停止させます。
  + Google SREの概念に基づき、過負荷時には「リクエストの早期拒絶（Request Rejection）」を主要な制御手段として用い、連鎖的崩壊を防ぎます。

---

5. AI・非決定論的システムに対する統計的検証

LLM等の確実な予測が困難なシステムに対し、一度の成功（One-off Success）を信頼の根拠とすることを厳禁します。

LLM-as-a-judgeの限界と対策

LLMを出力評価に用いる場合、以下の固有バイアスを特定し、緩和策を講じる必要があります。

* Self-enhancement bias: 特定のモデルが自身の出力傾向に高い評価を与えるバイアス。
* Position / Verbosity bias: 提示順序や回答の長さに評価が左右される現象。
* Limited reasoning ability: 複雑な論理整合性を正確に判定できない限界。

統計的検証レイヤーの運用

NabaOSの概念に基づき、直接観測（Direct Observation）と推論（Inference）を明示的に分離します。

1. 分散分析（Variance Analysis）: 同一入力に対する出力のばらつきを測定。
2. ドリフト分析（Drift Analysis）: モデルの更新やデータの経時変化による品質低下を検出。
3. ハイブリッド検証: 確率的評価を鵜呑みにせず、決定論的な検証コード（Deterministic safeguards）による形式チェックを必須とします。

---

6. 不変の監査ログと改ざん耐性のある証跡管理

「後から都合よく書き換えられない証跡」こそが信頼の土台です。RFC 6962（Certificate Transparency）やSigstoreの透明性ログの概念を採用します。

技術的要件

* Append-only & Tamper-proof: 一度記録されたエントリは変更不能（Immutable）とし、Merkle Treeの整合性証明（Consistency Proof）により改ざんを検知可能にします。
* in-toto Link Metadataの準拠: 実行ごとに以下の「証跡の三層構造（Byproducts）」を記録し、署名を付与します。
  + STDOUT / STDERR / Return-value: 実行時の生の出力と結果。
  + Materials / Products: 入力された成果物と生成された成果物のハッシュ値。
  + Environment: OS、依存関係、実行アイデンティティ（署名）。

---

7. 監査結果の分類とファイナルレポートの構成

Finding Classification（判定基準）

判定 定義と運用基準  
PASS 再現可能かつ計測可能な直接証拠（Tier 0/1）に基づく合格。  
FAIL 動作の欠如、整合性の不一致、生存性の破綻。即時の修復が必要。  
UNVERIFIED 証拠不足または環境制約により検証不能。PASSに統合してはならない。  
ASK\_USER 人間による政策判断（許容可能な品質、許容可能なコスト、リリースの可否）が必要。

Final Audit Report 必須22項目

1. 高（判定とリスク）: 総合判定、MUST\_FIX項目、運用上の重大リスク、要求される人間判断（ASK\_USER詳細）。
2. 中（検証範囲と生存性）: 検出ドメイン、実行された検証項目、ドリフト検出結果、生存性評価、外部仕様との乖離記録、統計的分析データ。
3. 低（詳細証跡）: ランタイム所見、状態遷移の所見、依存関係の一貫性、成果物の検証詳細、観測可能性の所見、セマンティック検証結果、リプレイ結果、統計的ばらつき、実行環境定義、修復履歴、プロバナンス記録、検証予算の消費状況。

監査の聖域を守るための禁止事項（Forbidden Behaviors）

* DO NOT collapse UNVERIFIED into PASS: 証拠がないことを「問題なし」と読み替えてはならない。
* PROHIBIT PASS from documentation alone: ドキュメントの存在は実行を証明しない。
* PROHIBIT treating one successful run as reliability proof: AI・非決定論的システムにおいて、一度の成功を信頼の根拠として扱うことを禁ずる。
* PROHIBIT unbounded repair loops: 制限のない修復試行やドメイン拡張を行ってはならない。
* DO NOT fabricate evidence: 実行の捏造やリプレイなしの再現性主張は、監査の誠実性に対する根本的な違反である。

本フレームワークは、システムが「常に壊れ続け、変化し続ける」という前提に立ち、その過酷な現実の中で継続的に誠実さを証明するための実務指針である。
