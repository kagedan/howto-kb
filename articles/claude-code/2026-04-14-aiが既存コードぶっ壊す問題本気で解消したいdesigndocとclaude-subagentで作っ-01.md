---
id: "2026-04-14-aiが既存コードぶっ壊す問題本気で解消したいdesigndocとclaude-subagentで作っ-01"
title: "「AIが既存コードぶっ壊す問題、本気で解消したい」——DesignDocとClaude Subagentで作った解決策"
url: "https://zenn.dev/mgdx_blog/articles/2ccfd55e2ac785"
source: "zenn"
category: "claude-code"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

「AIにコードを書かせているんだけど、ちょっと気を抜くとアーキテクチャ規約が崩れる…」「一定以上の規模感の開発になると手戻りが多い..」「既存機能がすでに豊富なので変更を加えると破壊してしまう..」そんな課題を感じたことはないでしょうか。

私たちのプロジェクトはDDD＋クリーンアーキテクチャで構成された20以上のGoマイクロサービスで動いています。既存機能が豊富に積み上がっており、新しい機能を加えるたびに既存コードへの影響を考慮しながら、各レイヤーの規約を守って実装しなければならない。通常のSpecDriven開発も軽微な修正であればよいのですが、変更範囲が大きい場合手戻りが発生することもありました。

そこで、**Design Docを渡すだけで、全フェーズの実装を自律的に完了してくれるオーケストレーター**を Claude Code（claude.ai/code）のskills機能を使って作りました。新規MSの全自動実装だけでなく、既存コードを壊さないためのガードレール機能も組み込んでいます。その開発の過程を振り返ってみます。

## 背景：なぜDesignDocドリブン実装なのか

以前からClaude Codeを使った開発を行っていましたが、課題がありました。

**課題1：コンテキスト爆発問題**  
マイクロサービス全体の実装を1つの会話で行うと、途中でAIのコンテキストが膨大になり、後半の実装品質が落ちてくる。

**課題2：規約逸脱問題**  
「SimpleClientパターンを使う」「Repositoryの命名はFind/Load/Save/Remove」といった独自規約を毎回プロンプトで伝えるのが大変で、守られないことがある。

**課題3：Design Docとのズレ問題**  
実装が進むにつれて、DesignDoc上の定義（ER図・シーケンス図..etc）と実際のコードが少しずつ乖離していく。

### DesignDocとは？

私たちのプロジェクトでは、実装前にDesign Docを作成しています。これは、\*\*「実装の詳細は記載せず、設計判断の根拠と制約を記述」\*\*します。  
つまり、API定義も全フィールドを列挙するのではなく、設計上のトレードオフに関わる部分（認証方式・ページング方針など）に絞って書きます。

**含まれないもの**: 実際のコード・詳細なスキーマ定義・非機能要件の実装詳細。

DesignDoc テンプレ例

```
## Problem Statement
なぜこの機能が必要か、解決する課題を記述。

## Goals / Non-Goals
- Goals: 実装する範囲
- Non-Goals: 今回は対象外にするもの

## Design
### ER図
（テーブル定義・リレーション, 関連する部分だけ抜粋）

### Domain Model
（Entity・ValueObject定義）

### シーケンス図
（処理フロー・イベント発行タイミング）

## API定義
エンドポイントの設計上のトレードオフに関わる部分のみ記載。
詳細なRequest/Responseスキーマは実装時に確定させる。

## Dependencies
依存する外部サービスや、相互依存するサービスについて記載

## Testing
正常系・準正常系・異常系のテストケース

## Influence range
影響範囲
```

## Orchestrator: design-doc-impl

`design-doc-impl` は、Design DocのNotion URLとMS名を受け取り、9つの特化型Subagent Skillを依存関係に基づいて順次起動するオーケストレーターです。DesignDocの内容（ER図・シーケンス図・IF定義）を解析して必要なSkillだけを自動選択し、A〜Eの5フェーズを順番に実行します。

![design-doc-impl システムアーキテクチャ全容](https://static.zenn.studio/user-upload/deployed-images/259a3c2fb17643b2c445dcd2.png?sha=07df3c36f1b14633f7577877e3aaf2ccd2f650a0)

| Skill | Phase | 実行条件 |
| --- | --- | --- |
| `impl1-migration` | A: スキーマ/API | ER図変更時 |
| `impl2-api-definition` | A: スキーマ/API | API変更時 |
| `impl3-domain-model` | B: ドメイン | 常に実行 |
| `impl4a-infra-mysql` | C: インフラ | MySQL Repository IFあり |
| `impl4b-infra-event` | C: インフラ | Event Repository IFあり |
| `impl4c-infra-external-ms` | C: インフラ | 外部API連携あり |
| `impl4d-infra-cloud` | C: インフラ | GCS/BigQueryアクセスあり |
| `impl5-domain-logic` | D: ロジック | 常に実行 |
| `impl6-interface` | E: I/F | 常に実行 |

### 使い方

```
/design-doc-impl <Notion Design Doc URL> <マイクロサービス名>
```

### First Step： Design Docの自律的解析とPhase Planの生成

![Step 0: Design Docの自律的解析と実装計画の生成](https://static.zenn.studio/user-upload/deployed-images/30f099a2b5fa0221888bfbc5.png?sha=e80a4569ec1afdc495351441a66f1420ffba686f)

まず**Extraction & Analysis Engine**がDesign Docを解析して実装計画（Phase Plan）を生成します。

1. **Entity抽出と順序制御** - ER図からEntityを特定し、FK依存関係を解析。`order → order_item`のように参照先を先に処理する順序を自動決定。
2. **インフラ・IF種別の自動判定** - MySQL/Event(PubSub)/外部MS/Cloud(GCS/BQ)の要否と、HTTP/gRPC/CLIのインターフェース要件を特定。
3. **計画の合意** - 分析結果をユーザーに提示し、合意を得てから実行開始。

Phase Planは `.claude/tmp/{ms_path_safe}-phase-plan.md` として保存され、全Subagentがこれを参照することで実行計画を共有します。

### 段階的実行（Cascading Execution）

![段階的実行とEntity単位の依存関係解決](https://static.zenn.studio/user-upload/deployed-images/a7dab90588d665e4da2ee5a8.png?sha=eed149570409317ba5dcb69dfd2338d1ea31745e)

全フェーズを一気に生成するのではなく、A1からEまで厳格な順序で逐次実行します。Phase C/D/EではさらにEntity単位に細分化し、各Entity内でも順序を守って実装します。

各Subagent完了ごとに必ず `git add + git commit` を実行するのも重要なポイントです。巨大な変更を小さなコミット単位に分割することで、失敗時のロールバックが容易になります。

## コアコンセプト：Rules = マスター、Skills = レシピ

設計の核心はシンプルな分業です。

| 役割 | ファイル | 内容 |
| --- | --- | --- |
| **Rules（マスター）** | `.claude/rules/*.md` | 全スキルが参照する規約の源泉。何をすべきかの「知識」 |
| **Skills（レシピ）** | `.claude/skills/*/SKILL.md` | 実行手順の定義。どう実装するかの「手順書」 |

Rulesは一度整備すれば全スキルが参照するので、規約変更があっても1箇所を直すだけで全体に反映されます。Skillsはそのフェーズで何をするかの手順だけを記述し、「なぜそうするか」はRulesに委ねます。

```
.claude/rules/
├── design_principles.md    # SOLID/DRY/KISS/YAGNI
├── architecture.md         # クリーンアーキテクチャ・レイヤー実装
├── golang_coding.md        # Go命名規則・エラー処理
└── ...                     # その他規約ファイル
```

## フェーズ別スキルの整備（impl1〜impl6）

実装を6つのフェーズに分け、それぞれ専用のSkillとして整備しました。各Skillの役割は以下の通りです。

* **`impl1-migration`** — ER図からマイグレーションSQLを生成。ロック影響の少ない順にインデックス戦略を選択
* **`impl2-api-definition`** — 独自OpenAPIジェネレータでAPI定義を生成。アノテーション・バリデーションタグをRulesで規定
* **`impl3-domain-model`** — Entity・ValueObject・Repository IF・Validator IFを生成。命名規則・パターンをRulesで統制
* **`impl4a-infra-mysql`** — MySQL Repositoryを実装。独自のDB接続抽象化パターンに従い生成
* **`impl4b-infra-event`** — Fluent/PubSubを使ったEvent Repositoryを実装
* **`impl4c-infra-external-ms`** — HTTP/gRPCで外部MSと連携するRepositoryを実装
* **`impl4d-infra-cloud`** — GCS/BigQueryのRepositoryを実装
* **`impl5-domain-logic`** — Service Impl・Validator・UseCaseを実装。シーケンス図からフローを読み取りテストも生成
* **`impl6-interface`** — HTTP handler・gRPC handler・PubSub subscriber・CLI・main.go DI配線を実装

## 品質保証の仕組み

### 自己レビューStepの横展開

当初impl4cで「実装完了後に自分でレビューしてからコミット」という仕組みを試したところ、品質が大幅に上がりました。そこでこれを全フェーズに横展開しました。各Skillの最終Stepに「Design Doc要件と実装の照合」を追加し、問題があれば人間の介入なしに自律修正してコミットします。

### QA 1：Design Doc要件への完全準拠と自律レビュー

![Quality Assurance 1: Design Doc要件への完全準拠と自律レビュー](https://static.zenn.studio/user-upload/deployed-images/8b0ea58d40ed16f8d1c14df9.png?sha=0bdee040717c9b90f312b0f2fea35fafaee90996)

各Subagentによるコード生成完了後、直ちに「レビュープロセス」が起動します。生成コードがNotionのDesign Doc要件を完全に満たしているかを検証し、問題があれば自律的に修正コードを生成して `fix: Phase {X} レビュー修正` としてコミットします。

フェーズ別のレビュー観点は以下の通りです：

| 実行フェーズ | 参照するNotionセクション | チェック観点 |
| --- | --- | --- |
| Phase A1/C（DB・インフラ） | ER図セクション | カラム名・型の完全一致、FK制約の定義漏れ、SQLクエリとインデックスの整合性 |
| Phase A2/E（API・I/F） | API定義セクション | エンドポイントのパス・メソッドの一致、Request/Response構造体のフィールド網羅 |
| Phase B（ドメイン） | Domain Model・ER | Entity全フィールドの網羅、Repository/Validator IFの定義漏れ |
| Phase D（ロジック） | シーケンス図・制約条件 | UseCaseの処理フローとシーケンス図の一致、バリデーションルール、イベント発行タイミング |

### QA 2：テスト駆動のオートヒール（自己修復）機構

![Quality Assurance 2: テスト駆動のオートヒール機構](https://static.zenn.studio/user-upload/deployed-images/81b5c88e0be34ba226504bdd.png?sha=de90ee1a16b8b4038a787c6839e69da944b12e5c)

Phase C・D・Eの完了時に `make test` を自動実行します。単なるシンタックスチェック（`go build`）ではなく、本格的な結合・単体テストを実行し、失敗時は自律的に修正ループを回します。

`make test`が担保する検証深度は以下の通りです：

![make testが担保するエンタープライズ水準の検証深度](https://static.zenn.studio/user-upload/deployed-images/4039d17240a5f55bd238b09b.png?sha=90128f269e53a822f9cb93afb4c72f597f5b4330)

`go build`では検出できないDBマイグレーション起因の不整合やinfrastructure層のエラーも拾えるため、人間がレビューする前の動作保証として機能します。

## 本番環境を守る強固なセーフティ・ガードレール

自律実行の危険性を最小化するために、複数層のガードレールを実装しました。

![本番環境を守る強固なセーフティ・ガードレール](https://static.zenn.studio/user-upload/deployed-images/f21bde04634920514eeebcc2.png?sha=5fcfa26a22729765bb6b835d4ec8968a67815a73)

**ハードブロック（settings.json）**  
`terraform apply/destroy`・`kubectl apply/delete`・`make deploy`・`gcloud`コマンドはAIのプロンプト指示では実行不可にしています。

**ブランチ保護**  
`master/main/develop/release/*`ブランチではプロセスが即座に停止します。安全なfeatureブランチでのみ動作します。

**共通ライブラリ変更検出（libs/go/）**  
対象MSとは別の共通ライブラリ（`libs/go/`）への変更が必要と判断した場合、パイプラインを一時停止して人間の判断を仰ぎます。グローバルな影響を持つ変更を自律的に実施しないようにしています。

**絶対禁止操作（PROHIBITED）リスト**  
`prohibited.md`に禁止操作を明文化し、全Subagentがこれを参照します。`cd &&` のような連結コマンドや`git add -A`（意図しないファイルを含める可能性）も禁止リストに入っています。

## Subagent間のcontext引き継ぎ

最初の実装では各Subagentが独立して動いていたため、「前のPhaseでどんな設計判断をしたか」がSubagent間で共有されないという問題がありました。

解決策として **Phase Planファイル**（`.claude/tmp/{ms_path_safe}-phase-plan.md`）を導入しました。各Subagentは：

1. 実行開始時にPhase Planファイルを読む
2. 処理中の重要な設計判断をPhase Planに追記する
3. 次のSubagentがその情報を参照して実装に活かす

これにより、例えば「Phase BでOrderEntityのIDフィールドをULIDにした」という決定が、Phase CのMySQL Repository実装にもPhase DのUseCaseにも引き継がれるようになりました。

## まとめ

`design-doc-impl`は、単なるコードスニペットのジェネレーターではありません。

![結論: 要件からテストまで完結する「自律型ソフトウェア工場」](https://static.zenn.studio/user-upload/deployed-images/810545bc15851bd127ba7df2.png?sha=6fcfa95d22ad0772109e1fe0a592509e8f036632)

要件の分析・依存関係の解決・段階的実装・要件レビュー・テスト実行・自己修復という、ソフトウェア開発の全サイクルを内包したオーケストレーターです。

1マイクロサービス単位での一貫した高品質なアーキテクチャ実装を、人間の介入を最小限に抑えながら完全自動化することができます。

![AIコーディングの信頼性を担保する3つのコアパラダイム](https://static.zenn.studio/user-upload/deployed-images/3f74f9440d7969b118512f60.png?sha=c06052733d76817b26ae5b29294d3baeb1963c05)

以下に、当初の課題に照らした振り返りをまとめます。

### よかった点

* **コンテキスト爆発が解消**：Phase分割により、各Subagentは自分の担当範囲に集中できる
* **規約の一貫性**：RulesをSubagentが参照するため、人間が指示しなくても規約が守られる
* **Design Docとの乖離防止**：各フェーズでDesign Docを参照してレビューするため、ズレが発生しにくい
* **細粒度コミット**：各Subagent完了ごとのコミットで、失敗時のデバッグが容易

### 改善点・今後の課題

* **Phase Planファイルの鮮度管理**：長期間かけた実装でPhase Planが古くなる場合への対処が必要
* **エラーリカバリーの深度**：オートヒールはunit testレベルだが、E2Eテスト失敗へのリカバリーはまだ手動
* **設計変更への追従**：実装途中でDesign Docが変更された場合のハンドリングが課題
* **権限管理の粒度設計**：AIにどこまでのファイル操作・コマンド実行を許可するか、ユースケースに応じた細かい権限設計がまだ発展途上

---

DesignDocドリブンで実装を自動化するアプローチに興味を持ってくださった方、あるいは同じような課題を感じている方にとって、少しでも参考になれば幸いです。

Claude Codeのrules/skills機能は、単なるプロンプトエンジニアリングを超えた「AIエージェントの設計」という領域を開いてくれます。今後もこの仕組みをさらに発展させていきたいと思っています。

## 参考リンク

## 付録：Codex版オーケストレーター

Claude Code版（`design-doc-impl`）に加えて、Codex版（`design-doc-impl-codex`）も作りました。

|  | Claude Code版 | Codex版 |
| --- | --- | --- |
| 実行方式 | インタラクティブ | バックグラウンド実行 |
| 確認タイミング | 各フェーズ前に確認可 | 非同期で通知 |
| 向いているケース | 複雑な判断が多い新規MS | 定型的な実装の自動化 |
