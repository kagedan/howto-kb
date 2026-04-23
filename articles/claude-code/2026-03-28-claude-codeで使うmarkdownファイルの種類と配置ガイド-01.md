---
id: "2026-03-28-claude-codeで使うmarkdownファイルの種類と配置ガイド-01"
title: "Claude Codeで使うMarkdownファイルの種類と配置ガイド"
url: "https://zenn.dev/hageoyaji/articles/4258167f3c54c5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

Claude Codeでは、用途の異なるMarkdownファイルを適切に配置することで、AIの振る舞いを制御できます。しかし種類が多く、正しく整理できないまま中途半端な環境を作ってしまっていました。

本記事では、どのファイルに何を書くべきか、どこに置くべきか、どのようなルートで呼び出されるかをサンプル付きで整理しました。

# ディレクトリ構成の全体像

```
my-project/
├── .claude
│   ├── CLAUDE.md                      # プロジェクト全体の方針・構成
│   ├── rules/                         # 条件付き・トピック別ルール
│   │   ├── testing.md
│   │   ├── api-security.md
│   │   └── db-access.md
│   ├── agents/                        # 専門エージェント定義
│   │   ├── be-api.md
│   │   └── be-db.md
│   └── skills/                        # 手順・観点・ナレッジ（スラッシュコマンド）
│       ├── api-design/
│       │   └── SKILL.md
│       └── testing/
│           └── SKILL.md
├── frontend/
│   ├── CLAUDE.md                      # フロントエンド固有の規約
│   ├── package.json
│   └── src/*
├── backend/
│   ├── CLAUDE.md                      # バックエンド固有の規約
│   ├── pom.xml
│   └── src
│       ├── main/*
│       └── test/                      # テストコード
```

# 使い分けの判断基準

| やりたいこと | 使うファイル |
| --- | --- |
| 常に意識させたいルール | `.claude/CLAUDE.md` |
| frontendディレクトリ固有のルール | `frontend/CLAUDE.md` |
| backendディレクトリ固有のルール | `backend/CLAUDE.md` |
| 特定ファイルだけに適用するルール | `.claude/rules/` |
| タスクを専門家に委譲したい | `.claude/agents/` |
| 必要なときだけ参照する手順・知識 | `.claude/skills/` |

# なぜこんなにファイルを分割するのか

理由はひとつ、**コンテキストウィンドウの節約**です。

Claude Codeには一度に処理できる情報量の上限（コンテキストウィンドウ）があります。CLAUDE.mdに全てのルールを詰め込むと、セッション開始時に大量のトークンを消費してしまい、肝心の作業に使える容量が減ります。さらに、指示が多すぎるとClaudeの遵守率も下がります。

ファイルを分割することで、**必要なルールだけを、必要なタイミングで読み込む**ことができます。

| 方式 | 読み込みタイミング | コンテキスト消費 |
| --- | --- | --- |
| `.claude/CLAUDE.md` に全部書く | 起動時に一括 | 常に全量を消費 |
| `backend/CLAUDE.md` に分割 | backend環境のファイルにアクセスした時だけ | 必要なときだけ消費 |
| `frontend/CLAUDE.md` に分割 | frontend環境のファイルにアクセスした時だけ | 必要なときだけ消費 |
| `.claude/rules/`（paths指定あり）に分割 | 該当ファイルを操作したときだけ | 必要なときだけ消費 |
| `.claude/agents/` に分離 | エージェント起動時に独立コンテキストで | メインの会話を消費しない |
| `.claude/skills/` に分離 | 呼び出されたときだけ | 必要なときだけ消費 |

例えば、Controller のセキュリティ規約を `CLAUDE.md` に書くと、Mapperの実装中でも常にコンテキストを占有します。`.claude/rules/api-security.md` に分離して `paths: controller/**/*.java` を指定すれば、Controllerを触るときだけ読み込まれ、それ以外のときはコンテキストに一切影響しません。

「全部1ファイルに書けば簡単」と思いがちですが、プロジェクトが大きくなるほどこの分割が効いてきます。

# 実際の処理フロー — どのmdがいつ読まれるか

「注文一覧のAPIを追加してください」という指示を出したとき、各mdファイルがどの順番で処理されるかを示します。

```
1: Claude Code起動（ユーザーの指示より前に読み込み）
  ├─ .claude/CLAUDE.md             → 管理者として振る舞う・ワークフローを確認
  └─ .claude/rules/testing.md     → テスト規約を確認（paths指定なし＝全体適用）

ユーザー「注文一覧のAPIを追加してください」
  │
  │ 2: 管理者が命令を分析・タスク分解（CLAUDE.mdに管理者としてふるまうことを記載している）
  ├─ 設計が必要と判断 → /api-design を呼び出す
  │    └─ .claude/skills/api-design/SKILL.md → 手動または自動で読み込み・設計手順を確認
  │
  │ 3: 管理者がbe-apiエージェントに委譲
  ├─ .claude/agents/be-api.md     → エージェントのシステムプロンプトとして読み込み
  │    │  （独立したコンテキストウィンドウで動作）
  │    │
  │    │ 4: エージェントがbackend/配下のファイルを操作し始める
  │    ├─ backend/CLAUDE.md             → backend/配下の最初のファイルを読んだ瞬間に読み込み
  │    ├─ .claude/rules/api-security.md → controller/**/*.java を操作した瞬間に読み込み
  │    │
  │    └─ 「Mapper実装が必要です。be-dbへの委譲をお願いします」と管理者に報告
  │
  │ 5: 管理者がbe-dbエージェントに委譲（be-apiから直接は呼び出せないため）
  ├─ .claude/agents/be-db.md      → エージェントのシステムプロンプトとして読み込み
  │    │  （独立したコンテキストウィンドウで動作）
  │    │
  │    ├─ .claude/rules/db-access.md → mapper/**/*.java を操作した瞬間に読み込み
  │    └─ Mapper実装完了 → 管理者に結果を返す
  │
  │ 6: 管理者がレビュー・ユーザーに報告
  └─ 完了
```

**ポイント**:

* `1:` `.claude/CLAUDE.md`とpaths指定なしのrulesは**セッション開始時から常に有効**
* `2:` skillsは常時読み込みではなく、**必要なときだけ呼び出される**（コンテキスト節約）
* `3: 5:` サブエージェントは**別のサブエージェントを呼び出せない**。エージェント間の委譲は必ず管理者（メインのClaude）を介する
* `3: 5:` 各エージェントは**独立したコンテキスト**で動くため、作業内容がメインの会話を圧迫しない
* `4:` `backend/CLAUDE.md` は `backend/` 配下の**どのファイルを触っても**読み込まれる
* `4:` paths指定ありのrulesは**該当パターンのファイルを操作したそのとき**だけ読み込まれる

# 各ファイルの役割

## .claude/CLAUDE.md — 「常に読まれるルールブック」

セッション開始時に自動で読み込まれるファイルです。配置場所によって**書く内容を明確に分けるのがポイント**です。

### .claude/CLAUDE.md — 「役割・振る舞いの定義」

`.claude/CLAUDE.md` は起動時に必ず読み込まれます。ここには**Claudeにどう振る舞わせるか**を定義します。技術的なルールは書きません。

| カテゴリ | 具体的な記述内容 | 例 |
| --- | --- | --- |
| ロール定義 | Claudeがどの役割で動くかを明示する | 「あなたは管理者として振る舞い、ユーザーからの指示を受けて作業分解する」 |
| ワークフロー | 指示の流れ・作業の進め方を定義する | 「命令を受けたら①分析②タスク分解③担当への指示④レビューの順で進めよ」 |
| 出力フォーマット | 応答の形式・トーン・構造を指定する | 「報告は結論から先に述べ、問題があれば対策案を添えること」 |
| 権限・制約 | やってよいこと・禁止事項を定義する | 「担当ディレクトリ外のファイルを無断で変更するな」 |
| エージェント間の連携ルール | 複数エージェントがいる場合の通信規約 | 「フロントエンド担当はバックエンドコードに手を出してはならない」 |

```
# .claude/CLAUDE.md の例

## あなたの役割
あなたは「管理者」として振る舞います。
ユーザーからの命令を受け取り、作業を分解して各担当者（エージェント）に割り振ってください。

## ワークフロー
1. ユーザーの命令を受領し、内容を正確に把握する
2. フロントエンド・バックエンド・ドキュメントに作業を分解する
3. 各担当エージェントに指示を出す
4. 成果物をレビューし、合格なら報告、不合格なら差し戻す

## 出力規約
- 報告は常に結論から述べること
- 問題が発生した場合は、原因と対策案をセットで報告すること
```

### サブディレクトリの CLAUDE.md — 「技術的なルール」

`frontend/CLAUDE.md` や `backend/CLAUDE.md` は、そのディレクトリのファイルを操作したときにオンデマンドで読み込まれます。ここには**その領域固有の技術ルール**を書きます。

> **補足**: サブディレクトリの `CLAUDE.md` はプロジェクトルート直下に置くことも可能ですが、個人設定はかつての `CLAUDE.local.md` ではなく、後述の **Auto Memory** を活用してください。

| カテゴリ | 具体的な記述内容 |
| --- | --- |
| ビルド・実行コマンド | `./mvnw spring-boot:run`、`./mvnw test` など、その領域でよく使うコマンド |
| ディレクトリ構成 | 「Controllerは `controller/` に置く」「DTOは `dto/` に配置し、ドメインオブジェクトと混在させない」などファイルの置き場所 |
| コーディング規約 | チェックツールでは検出できない判断基準を書きます。「`null` を返すメソッドは作らず `Optional<T>` を使う」「例外は @ControllerAdvice で一元処理する」「ログは必ずSLF4Jを使い System.out.println は禁止」など、**なぜそうするか**の意図もセットで書くとClaudeが応用して判断できます |
| アーキテクチャ方針 | 技術選定の結果と理由を書きます。「Controller → Service → Mapper の依存方向を厳守する（テスタビリティ確保のため）」「DTOをServiceに渡さない（ドメインロジックをHTTPの関心事から分離するため）」など、**迷いが生じやすい箇所の決定事項**を記載します |

### サンプル: `backend/CLAUDE.md`（Java / Spring Boot）

```
# バックエンド 開発規約

## ビルド・実行コマンド
- 起動: `./mvnw spring-boot:run`
- テスト: `./mvnw test`
- ビルド: `./mvnw clean package`

## ディレクトリ構成
src/main/java/com/example/
├── controller/   # HTTPリクエストの受付のみ。ビジネスロジックは書かない
├── service/      # ビジネスロジック。トランザクション管理はここで行う
├── mapper/       # MyBatisのMapperインターフェース
├── domain/       # エンティティ・値オブジェクト
└── dto/          # リクエスト/レスポンスのデータクラス

## コーディング規約
- 例外はカスタム例外クラスを定義し、グローバルハンドラ（@ControllerAdvice）で一元処理する
- `null` を返すメソッドは作らない。存在しない可能性がある場合は `Optional<T>` を返す
- ロジック内でのSystem.out.printlnは禁止。必ずSLF4Jのloggerを使うこと
- Serviceクラスのメソッドはpublicのみ。privateロジックはprivateメソッドに切り出す

## アーキテクチャ方針
- レイヤードアーキテクチャを採用。Controller → Service → Mapper の依存方向を厳守する
  （理由: 依存方向を一方向に保つことでテスタビリティを確保するため）
- ControllerはDTOを受け取り、ServiceはDomainオブジェクトで処理する。DTOをServiceに渡さない
  （理由: ドメインロジックをHTTPの関心事から分離するため）
- DBのトランザクションは@Transactionalをサービス層にのみ付与する
- APIのバリデーションはBean Validation（@NotNull, @Sizeなど）をDTOに付与して行う
```

## .claude/rules/ — 「条件付きルール」

CLAUDE.mdを分割し、特定のパスパターンにだけ適用するルールを定義できます。

* `paths` 指定なし → 起動時に全体適用されます（CLAUDE.mdと同等）
* `paths` 指定あり → 該当ファイル操作時のみ適用されます（コンテキスト節約）

### サンプル: `.claude/rules/testing.md`（テスト規約・全体適用）

パス指定なしで、プロジェクト全体に適用されるルールです。

```
# テスト規約

- テストクラス名は対象クラス名 + `Test`（例: `UserServiceTest`）
- テストメソッド名は `メソッド名_状態_期待結果` の形式にする（例: `findById_存在しないID_空のOptionalを返す`）
- 正常系・異常系・境界値の3パターンを最低限カバーすること
- モックは @MockitoExtension を使い、テスト間の依存を排除する
- DBアクセスが必要なテストは @MybatisTest を使い、単体テストと分離する
```

### サンプル: `.claude/rules/api-security.md`（Controllerのみに適用）

パス指定で `controller/` 配下のファイルを操作したときだけ読み込まれるルールです。

```
---
paths:
  - "src/main/java/**/controller/**/*.java"
---

# Controller セキュリティ規約

- 認証が必要なエンドポイントには必ず @PreAuthorize を付与する
- リクエストボディは必ず @Valid でバリデーションを実行する
- レスポンスに内部エラーのスタックトレースを含めてはならない
- PATCHは部分更新、PUTは全体更新として使い分けること
```

### サンプル: `.claude/rules/db-access.md`（DB操作ファイルのみに適用）

```
---
paths:
  - "src/main/java/**/mapper/**/*.java"
  - "src/main/resources/mapper/**/*.xml"
---

# DB アクセス規約（MyBatis）

## ファイル構成
- Mapperインターフェースは `src/main/java/**/mapper/` に配置する
- SQLは必ずMapperXML（`src/main/resources/mapper/*.xml`）に分離する
- MapperインターフェースにSQL文字列を直接書いてはならない（@Select等のアノテーションは禁止）
  （理由: SQLが複雑になったときに管理しづらくなるため、XMLに統一する）

## Mapperインターフェース規約
- インターフェース名は対象テーブル名 + `Mapper`（例: `UserMapper`）
- メソッド名はCRUDに応じて `selectById`、`selectList`、`insert`、`update`、`delete` を基本とする
- 戻り値がゼロ件の可能性がある単件取得は `Optional<T>` を返す

## MapperXML規約
- `namespace` はMapperインターフェースの完全修飾名と一致させる
- `resultMap` は必ず定義し、カラム名とフィールド名を明示的にマッピングする
- 動的SQLは `<if>`、`<choose>`、`<foreach>` を使い、文字列結合でSQLを組み立てない
  （理由: SQLインジェクション防止のため）
- 削除は物理削除ではなく論理削除（deleted_at）を使うこと
```

## .claude/agents/ — 「専門家の定義」

特定タスクに特化したサブエージェントを定義します。各エージェントは**独立したコンテキストウィンドウ**で動作します。

* Claudeがタスク内容と `description` を照合し、適切なエージェントに自動委譲します
* `tools` でエージェントが使えるツールを制限できます
* `model` でエージェントごとに使用モデルを変えられます（`haiku`で高速・低コスト化など）

**書くもの**: エージェントの専門性、担当範囲、判断基準、出力フォーマット

### サンプル: `.claude/agents/be-api.md`（APIエンドポイント実装担当）

```
---
name: be-api
description: JavaのControllerおよびServiceクラスの実装・修正を担当するエージェント。APIエンドポイントの追加・変更・バリデーション実装の指示を受けたときに使用する。
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---
あなたはJava / Spring Bootのバックエンド実装を専門とするエージェントです。

## 担当範囲
- Controller、Service、DTOクラスの実装・修正
- Bean Validationを使ったリクエストバリデーション
- @ControllerAdvice を使った例外ハンドリング

## 実装方針
- Controllerはリクエストの受付とレスポンスの返却のみ行い、ビジネスロジックはServiceに委譲する
- DTOはControllerとServiceの境界で使用し、ServiceからMapperにはDomainオブジェクトを渡す
- nullを返すメソッドは作らない。単件取得はOptional<T>を返す
- 例外は独自例外クラスを定義し、@ControllerAdviceで一元処理する

## 完了条件
実装後に以下を確認してから報告すること：
1. コンパイルエラーがないこと（`./mvnw compile` で確認）
2. 関連するテストが通ること（`./mvnw test` で確認）
3. Mapperの実装が必要な場合は自分で実装せず、「Mapper実装が必要です。be-dbへの委譲をお願いします」と管理者に報告すること
```

### サンプル: `.claude/agents/be-db.md`（DB・Mapper実装担当）

```
---
name: be-db
description: MyBatisのMapperインターフェースとMapperXMLの実装・修正を担当するエージェント。テーブル設計・SQL実装・マイグレーションの指示を受けたときに使用する。
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---
あなたはMyBatisを使ったDB操作の実装を専門とするエージェントです。

## 担当範囲
- Mapperインターフェースの定義
- MapperXML（SQLファイル）の実装
- Flywayマイグレーションファイルの作成

## 実装方針
- SQLは必ずMapperXMLに記述する。@SelectなどアノテーションへのSQL直書きは禁止
- resultMapを必ず定義し、カラムとフィールドのマッピングを明示する
- 動的SQLは<if>/<foreach>を使い、文字列結合でSQLを組み立てない
- 削除は論理削除（deleted_atカラム）で実装する

## 完了条件
実装後に以下を確認してから報告すること：
1. XMLのnamespaceがMapperインターフェースの完全修飾名と一致していること
2. `./mvnw test` でMapperのテストが通ること
```

## .claude/skills/ — 「呼び出し型のナレッジ」

`/スラッシュコマンド` として呼び出せる手順書・観点集です。CLAUDE.mdやrulesが「常に・自動で」読み込まれるのに対し、skillsは**必要なときだけ**読み込まれます。

```
---
name: api-design
description: RESTful APIの設計手順と観点
allowed-tools: Read, Write, Edit, Bash
---
## API設計手順
1. エンドポイントのURL設計
2. リクエスト/レスポンスの型定義
3. エラーコードの設計
4. バリデーションルールの定義
```

* `/api-design` で手動呼び出し、または `description` に基づきClaudeが自動判断で読み込みます
* 常時読み込みではないため、コンテキストウィンドウを圧迫しません

**書くもの**: 実装手順、レビュー観点、設計テンプレート、ワークフロー

# 補足: Auto Memory

上記はすべて人間が書くファイルですが、Claude Codeには**Auto Memory**という自動学習機能もあります。

## 仕組み

Claudeが作業中に学んだパターン（ビルドコマンド、デバッグで得た知見、コーディングスタイルの好みなど）を自動で保存します。設定不要で動作し、手動編集も可能です。

保存先はGitリポジトリのパスから生成されます。例えば `C:\main\develop\mf\my-app` というリポジトリなら：

```
~/.claude/projects/-C-main-develop-mf-my-app/memory/
├── MEMORY.md              # インデックス（セッション開始時に読み込まれる）
├── debugging.md           # デバッグパターンの記録
└── api-conventions.md     # API設計の決定事項
```

同じGitリポジトリ内であれば、ワークツリーやサブディレクトリに関係なく同一のメモリを共有します。

## コンテキストへの影響

Auto Memoryもコンテキストウィンドウを消費します。ただし、制限があります。

| ファイル | 読み込みタイミング | 読み込み上限 |
| --- | --- | --- |
| `MEMORY.md` | **セッション開始時に自動** | 先頭200行 または 25KBのどちらか小さい方 |
| トピックファイル（`debugging.md` 等） | **必要なときにオンデマンド** | 制限なし（ただし都度消費） |

`MEMORY.md` は CLAUDE.md と同じく**毎回コンテキストを消費する**ため、Claudeは `MEMORY.md` を簡潔なインデックスに保ち、詳細はトピックファイルに分けるよう自動で管理します。

## 注意点

* Auto Memoryは**マシンローカル**です。チームメンバーや他のマシンには共有されません
* 不要な記録が増えた場合は `/memory` コマンドで確認・削除できます
* `autoMemoryEnabled: false` で無効化できます
